"""Tests for profiles/signals.py seed_user_organisations signal."""
import pytest

from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency, ResidencyContact
from organisations.venues.models import Venue, VenueContact
from profiles.models import Profile


@pytest.mark.django_db
class TestSeedUserOrganisations:
    """Tests for the seed_user_organisations signal."""

    def _create_seeds(self):
        """Create seed organisations (user=NULL)."""
        Festival.objects.create(
            name="Seed Festival",
            town="Paris",
            country="France",
            user=None,
        )
        Venue.objects.create(
            name="Seed Venue",
            town="London",
            country="UK",
            user=None,
        )
        Residency.objects.create(
            name="Seed Residency",
            town="Berlin",
            country="Germany",
            user=None,
        )

    def test_seed_festivals_cloned_on_user_creation(self):
        self._create_seeds()
        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        user_festivals = Festival.objects.filter(user=profile, is_seed_clone=True)
        assert user_festivals.count() == 1
        assert user_festivals.first().name == "Seed Festival"

    def test_seed_venues_cloned_on_user_creation(self):
        self._create_seeds()
        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        user_venues = Venue.objects.filter(user=profile, is_seed_clone=True)
        assert user_venues.count() == 1
        assert user_venues.first().name == "Seed Venue"

    def test_seed_residencies_cloned_on_user_creation(self):
        self._create_seeds()
        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        user_residencies = Residency.objects.filter(user=profile, is_seed_clone=True)
        assert user_residencies.count() == 1
        assert user_residencies.first().name == "Seed Residency"

    def test_seed_festival_contacts_cloned(self):
        self._create_seeds()
        seed_festival = Festival.objects.get(user__isnull=True)
        FestivalContact.objects.create(
            festival=seed_festival,
            email="contact@seed.com",
            name="Seed Contact",
            user=None,
        )

        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        user_festival = Festival.objects.filter(user=profile, name="Seed Festival").first()
        assert user_festival is not None
        contacts = FestivalContact.objects.filter(festival=user_festival)
        assert contacts.count() == 1
        assert contacts.first().email == "contact@seed.com"

    def test_seed_venue_contacts_cloned(self):
        self._create_seeds()
        seed_venue = Venue.objects.get(user__isnull=True)
        VenueContact.objects.create(
            venue=seed_venue,
            email="venue@seed.com",
            name="Venue Contact",
            user=None,
        )

        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        user_venue = Venue.objects.filter(user=profile, name="Seed Venue").first()
        contacts = VenueContact.objects.filter(venue=user_venue)
        assert contacts.count() == 1
        assert contacts.first().email == "venue@seed.com"

    def test_seed_residency_contacts_cloned(self):
        self._create_seeds()
        seed_residency = Residency.objects.get(user__isnull=True)
        ResidencyContact.objects.create(
            residency=seed_residency,
            email="res@seed.com",
            name="Res Contact",
            user=None,
        )

        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        user_residency = Residency.objects.filter(user=profile, name="Seed Residency").first()
        contacts = ResidencyContact.objects.filter(residency=user_residency)
        assert contacts.count() == 1
        assert contacts.first().email == "res@seed.com"

    def test_no_seeds_means_no_clones(self):
        """When there are no seed orgs, no clones should be created."""
        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        assert Festival.objects.filter(user=profile).count() == 0
        assert Venue.objects.filter(user=profile).count() == 0
        assert Residency.objects.filter(user=profile).count() == 0

    def test_signal_not_triggered_on_update(self):
        """Signal should not seed organisations on profile update."""
        self._create_seeds()
        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        # Count after creation
        initial_festival_count = Festival.objects.filter(user=profile).count()

        # Update profile - should not clone again
        profile.first_name = "Updated"
        profile.save()

        assert Festival.objects.filter(user=profile).count() == initial_festival_count

    def test_multiple_seeds_all_cloned(self):
        """Multiple seed organisations should all be cloned."""
        for i in range(3):
            Festival.objects.create(
                name=f"Seed Festival {i}",
                town="Paris",
                country="France",
                user=None,
            )

        profile = Profile.objects.create_user(email="new@example.com", password="pass")

        user_festivals = Festival.objects.filter(user=profile, is_seed_clone=True)
        assert user_festivals.count() == 3

    def test_raw_signal_skipped(self):
        """Signal with raw=True should not clone organisations."""
        from django.db.models.signals import post_save
        from profiles.signals import seed_user_organisations

        # Simulate raw signal call
        profile = Profile.objects.create_user(email="raw@example.com", password="pass")

        # Manually trigger signal with raw=True
        post_save.send(
            sender=Profile,
            instance=profile,
            created=True,
            raw=True,
        )

        # No extra orgs should be created
        assert Festival.objects.filter(user=profile).count() == 0
