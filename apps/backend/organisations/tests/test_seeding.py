"""Tests for organisations/seeding.py and the propagate_seed task."""

import pytest

from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency, ResidencyContact
from organisations.seeding import (
    clone_seeds_for_profiles,
    has_matching_organisation,
    propagate_seed_to_profiles,
)
from organisations.tasks import propagate_seed
from organisations.venues.models import Venue, VenueContact
from profiles.models import Profile


def make_user(email: str, **extra) -> Profile:
    return Profile.objects.create_user(email=email, password="pass", **extra)


@pytest.fixture
def seed_festival(db):
    festival = Festival.objects.create(
        name="Seed Fest",
        country="France",
        town="Paris",
        website_url="https://www.seedfest.org/en",
        festival_type="STREET",
        application_type="EMAIL",
        approximate_date="early July",
        user=None,
    )
    FestivalContact.objects.create(festival=festival, name="Ana", email="ana@seedfest.org")
    FestivalContact.objects.create(festival=festival, name="Ben", email="ben@seedfest.org")
    return festival


@pytest.mark.django_db
class TestCloneSeedsForProfiles:
    def test_copies_fields_and_contacts_to_each_profile(self, seed_festival):
        users = [make_user("a@example.com"), make_user("b@example.com")]
        # Signup already cloned the seed; start from a clean slate for this test.
        Festival.objects.filter(user__in=users).delete()

        created = clone_seeds_for_profiles(Festival, [seed_festival], users)

        assert created == 2
        for user in users:
            clone = Festival.objects.get(user=user)
            assert clone.is_seed_clone is True
            assert clone.pk != seed_festival.pk
            for field in ("name", "country", "town", "website_url", "festival_type"):
                assert getattr(clone, field) == getattr(seed_festival, field)
            assert clone.approximate_date == "early July"
            assert sorted(clone.contacts.values_list("email", flat=True)) == [
                "ana@seedfest.org",
                "ben@seedfest.org",
            ]
            assert set(clone.contacts.values_list("user_id", flat=True)) == {user.id}

    def test_contacts_mapped_by_id_not_name(self, db):
        """Two seeds with the same name must each keep their own contacts."""
        first = Festival.objects.create(name="Twin", country="France", user=None)
        second = Festival.objects.create(name="Twin", country="Spain", user=None)
        FestivalContact.objects.create(festival=first, email="first@twin.org")
        FestivalContact.objects.create(festival=second, email="second@twin.org")

        user = make_user("a@example.com")

        clones = {f.country: f for f in Festival.objects.filter(user=user)}
        assert list(clones["France"].contacts.values_list("email", flat=True)) == ["first@twin.org"]
        assert list(clones["Spain"].contacts.values_list("email", flat=True)) == ["second@twin.org"]

    def test_soft_deleted_contacts_are_not_copied(self, seed_festival):
        seed_festival.contacts.get(name="Ben").delete()

        user = make_user("a@example.com")

        clone = Festival.objects.get(user=user)
        assert list(clone.contacts.values_list("name", flat=True)) == ["Ana"]

    def test_venue_and_residency_specific_fields(self, db):
        venue = Venue.objects.create(name="Hall", venue_type="THEATRE", contacted=True, user=None)
        VenueContact.objects.create(venue=venue, email="v@hall.org")
        residency = Residency.objects.create(name="Res", application_type="OPEN_CALL", user=None)
        ResidencyContact.objects.create(residency=residency, email="r@res.org")

        user = make_user("a@example.com")

        venue_clone = Venue.objects.get(user=user)
        assert (venue_clone.venue_type, venue_clone.contacted) == ("THEATRE", True)
        assert venue_clone.contacts.get().email == "v@hall.org"
        residency_clone = Residency.objects.get(user=user)
        assert residency_clone.application_type == "OPEN_CALL"
        assert residency_clone.contacts.get().email == "r@res.org"

    @pytest.mark.parametrize("seeds, profiles", [([], ["user"]), (["seed"], [])])
    def test_empty_inputs_create_nothing(self, seed_festival, seeds, profiles):
        user = make_user("a@example.com")
        count_before = Festival.objects.count()

        created = clone_seeds_for_profiles(
            Festival,
            [seed_festival for _ in seeds],
            [user for _ in profiles],
        )

        assert created == 0
        assert Festival.objects.count() == count_before


@pytest.mark.django_db
class TestHasMatchingOrganisation:
    @pytest.mark.parametrize(
        "name, country, website, expected",
        [
            ("seed fest", "FRANCE", "", True),  # name + country, case-insensitive
            ("Seed Fest", "Spain", "", False),  # same name, other country
            ("Other", "Spain", "http://seedfest.org", True),  # same domain, www/scheme ignored
            ("Other", "Spain", "https://sub.seedfest.org", False),  # subdomain differs
            ("Other", "Spain", "https://notseedfest.org", False),  # substring but not same domain
            ("Other", "Spain", "", False),
        ],
    )
    def test_matching(self, seed_festival, name, country, website, expected):
        user = make_user("a@example.com")
        Festival.objects.filter(user=user).delete()
        Festival.objects.create(user=user, name=name, country=country, website_url=website)

        assert has_matching_organisation(Festival, user, seed_festival) is expected

    def test_seed_without_website_only_matches_on_name(self, db):
        seed = Festival.objects.create(name="No Site", country="Italy", user=None)
        user = make_user("a@example.com")
        Festival.objects.filter(user=user).delete()
        Festival.objects.create(user=user, name="Different", country="Italy", website_url="")

        assert has_matching_organisation(Festival, user, seed) is False


@pytest.mark.django_db
class TestPropagateSeed:
    def _new_seed(self, **fields):
        """A seed created after the users signed up (so they don't have it yet)."""
        defaults = {"name": "New Fest", "country": "Belgium", "website_url": "https://newfest.be"}
        seed = Festival.objects.create(user=None, **{**defaults, **fields})
        FestivalContact.objects.create(festival=seed, email="hello@newfest.be")
        return seed

    def test_copies_to_existing_non_staff_users_only(self, db):
        user_a = make_user("a@example.com")
        user_b = make_user("b@example.com")
        staff = make_user("staff@example.com", is_staff=True)
        admin = Profile.objects.create_superuser(email="admin@example.com", password="pass")
        seed = self._new_seed()

        created = propagate_seed(Festival._meta.label, seed.id)

        assert created == 2
        for user in (user_a, user_b):
            clone = Festival.objects.get(user=user, name="New Fest")
            assert clone.is_seed_clone is True
            assert clone.contacts.get().email == "hello@newfest.be"
        assert not Festival.objects.filter(user__in=[staff, admin], name="New Fest").exists()

    def test_skips_users_who_already_have_it(self, db):
        has_it = make_user("has@example.com")
        Festival.objects.create(user=has_it, name="My entry", website_url="http://www.newfest.be/")
        lacks_it = make_user("lacks@example.com")
        seed = self._new_seed()

        created = propagate_seed(Festival._meta.label, seed.id)

        assert created == 1
        assert Festival.objects.filter(user=has_it).count() == 1
        assert Festival.objects.filter(user=lacks_it, name="New Fest").exists()

    def test_running_twice_creates_nothing_new(self, db):
        make_user("a@example.com")
        seed = self._new_seed()

        assert propagate_seed(Festival._meta.label, seed.id) == 1
        assert propagate_seed(Festival._meta.label, seed.id) == 0
        assert Festival.objects.filter(name="New Fest").count() == 2  # seed + one copy

    def test_works_for_venues_and_residencies(self, db):
        user = make_user("a@example.com")
        venue = Venue.objects.create(user=None, name="New Hall", country="Italy")
        residency = Residency.objects.create(user=None, name="New Res", country="Spain")

        assert propagate_seed(Venue._meta.label, venue.id) == 1
        assert propagate_seed(Residency._meta.label, residency.id) == 1
        assert Venue.objects.filter(user=user, name="New Hall").exists()
        assert Residency.objects.filter(user=user, name="New Res").exists()

    def test_missing_or_deleted_seed_is_a_no_op(self, db):
        make_user("a@example.com")
        seed = self._new_seed()
        seed.delete()  # soft delete

        assert propagate_seed(Festival._meta.label, seed.id) == 0
        assert propagate_seed(Festival._meta.label, 999_999) == 0

    def test_non_seed_is_ignored_by_task(self, db):
        owner = make_user("owner@example.com")
        make_user("other@example.com")
        own_festival = Festival.objects.create(user=owner, name="Private")

        assert propagate_seed(Festival._meta.label, own_festival.id) == 0
        assert Festival.objects.filter(name="Private").count() == 1

    def test_helper_rejects_non_seed(self, db):
        owner = make_user("owner@example.com")
        own_festival = Festival.objects.create(user=owner, name="Private")

        with pytest.raises(ValueError):
            propagate_seed_to_profiles(own_festival, [owner])
