"""Tests for changing an organisation's type (organisations/conversion.py + the convert action)."""

from datetime import date, timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from applications.models import Application, InboundEmail
from organisations.conversion import ConversionError, convert_organisation
from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency, ResidencyContact
from organisations.venues.models import Venue, VenueContact
from profiles.models import Profile, Reminder


@pytest.fixture
def user(db):
    return Profile.objects.create_user(email="convert@example.com", password="pass")


@pytest.fixture
def client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def festival(user):
    festival = Festival.objects.create(
        name="Fest",
        description="A street festival",
        country="France",
        town="Lyon",
        website_url="https://fest.fr",
        comments="Nice people",
        tag="STAR",
        festival_type="CIRCUS",
        start_date=date(2027, 6, 1),
        end_date=date(2027, 6, 3),
        approximate_date="June",
        application_date_start="January",
        application_date_end="March",
        application_type="FORM",
        user=user,
    )
    FestivalContact.objects.create(
        festival=festival, name="Ann", email="ann@fest.fr", role="Director", user=user
    )
    gone = FestivalContact.objects.create(festival=festival, name="Gone", user=user)
    gone.delete()  # soft-deleted contacts are not carried over
    return festival


def _ct(model):
    return ContentType.objects.get_for_model(model)


@pytest.mark.django_db
class TestConvertOrganisation:
    def test_festival_to_venue_copies_shared_fields_and_drops_specific_ones(self, festival, user):
        venue = convert_organisation(festival, "VENUE")

        assert isinstance(venue, Venue)
        assert venue.name == "Fest"
        assert venue.description == "A street festival"
        assert (venue.country, venue.town) == ("France", "Lyon")
        assert venue.website_url == "https://fest.fr"
        assert venue.comments == "Nice people"
        assert venue.tag == "STAR"
        assert venue.user == user
        assert venue.is_seed_clone is False
        assert venue.venue_type == "UNKNOWN"
        assert venue.contacted is False

    def test_festival_to_residency_keeps_dates(self, festival):
        residency = convert_organisation(festival, "residency")

        assert isinstance(residency, Residency)
        assert residency.start_date == date(2027, 6, 1)
        assert residency.end_date == date(2027, 6, 3)
        assert residency.approximate_date == "June"
        assert residency.application_date_start == "January"
        assert residency.application_date_end == "March"
        assert residency.application_type == "FORM"

    def test_choice_unsupported_by_target_resets_to_default(self, user):
        residency = Residency.objects.create(name="Res", application_type="OPEN_CALL", user=user)

        festival = convert_organisation(residency, "FESTIVAL")

        assert festival.application_type == "UNKNOWN"
        assert festival.festival_type == "STREET"

    def test_keeps_seed_clone_flag(self, user):
        clone = Venue.objects.create(name="Clone", user=user, is_seed_clone=True)

        assert convert_organisation(clone, "FESTIVAL").is_seed_clone is True

    def test_copies_live_contacts_only(self, festival, user):
        venue = convert_organisation(festival, "VENUE")

        contacts = list(VenueContact.objects.with_deleted().filter(venue=venue))
        assert [(c.name, c.email, c.role, c.user) for c in contacts] == [
            ("Ann", "ann@fest.fr", "Director", user)
        ]

    def test_hard_deletes_the_original_and_its_contacts(self, festival):
        festival_id = festival.id

        convert_organisation(festival, "VENUE")

        assert not Festival.objects.with_deleted().filter(id=festival_id).exists()
        assert not FestivalContact.objects.with_deleted().filter(festival_id=festival_id).exists()

    def test_moves_applications_including_soft_deleted(self, festival, user):
        live = Application.objects.create(organisation=festival, profile=user)
        deleted = Application.objects.create(organisation=festival, profile=user)
        deleted.deleted_at = timezone.now()
        deleted.save()

        venue = convert_organisation(festival, "VENUE")

        for app in (live, deleted):
            app = Application.objects.with_deleted().get(id=app.id)
            assert (app.content_type, app.object_id) == (_ct(Venue), venue.id)
            assert app.organisation == venue

    def test_moves_reminders_and_inbound_emails(self, festival, user):
        reminder = Reminder.objects.create(
            organisation=festival,
            profile=user,
            message="Apply!",
            remind_at=timezone.now() + timedelta(days=1),
        )
        email = InboundEmail.objects.create(
            profile=user,
            organisation=festival,
            message_id="<1@fest.fr>",
            from_address="ann@fest.fr",
        )

        residency = convert_organisation(festival, "RESIDENCY")

        reminder.refresh_from_db()
        email.refresh_from_db()
        assert reminder.organisation == residency
        assert email.organisation == residency

    def test_does_not_touch_other_organisations_references(self, festival, user):
        other = Festival.objects.create(name="Other", user=user)
        app = Application.objects.create(organisation=other, profile=user)

        convert_organisation(festival, "VENUE")

        app.refresh_from_db()
        assert app.organisation == other

    def test_venue_to_festival_then_back(self, user):
        venue = Venue.objects.create(name="Hall", venue_type="THEATRE", contacted=True, user=user)
        VenueContact.objects.create(venue=venue, name="Bob", user=user)

        festival = convert_organisation(venue, "FESTIVAL")
        assert festival.contacts.count() == 1

        back = convert_organisation(festival, "VENUE")
        assert back.name == "Hall"
        assert back.contacts.get().name == "Bob"
        # Type-specific values don't survive a round trip through another type
        assert back.venue_type == "UNKNOWN"
        assert back.contacted is False

    @pytest.mark.parametrize("target_type", ["", "THEATRE", "festivals"])
    def test_rejects_invalid_type(self, festival, target_type):
        with pytest.raises(ConversionError, match="Invalid organisation type"):
            convert_organisation(festival, target_type)

    def test_rejects_same_type(self, festival):
        with pytest.raises(ConversionError, match="already a festival"):
            convert_organisation(festival, "FESTIVAL")

    def test_rejects_deleted_organisation(self, festival):
        festival.delete()

        with pytest.raises(ConversionError, match="Deleted"):
            convert_organisation(festival, "VENUE")

        assert not Venue.objects.exists()

    def test_failure_rolls_back(self, festival, monkeypatch):
        """Nothing is created or deleted if a step fails part-way."""
        festival_id = festival.id

        def boom(*args, **kwargs):
            raise RuntimeError("boom")

        monkeypatch.setattr(Festival, "hard_delete", boom)
        with pytest.raises(RuntimeError):
            convert_organisation(festival, "VENUE")

        assert Festival.objects.filter(id=festival_id).exists()
        assert not Venue.objects.exists()
        assert not VenueContact.objects.exists()


@pytest.mark.django_db
class TestConvertAction:
    def test_converts_and_returns_new_id_and_type(self, client, festival):
        response = client.post(
            f"/api/festivals/{festival.id}/convert/", {"target_type": "VENUE"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        venue = Venue.objects.get(id=response.data["id"])
        assert response.data["organisation_type"] == "VENUE"
        assert venue.name == "Fest"

        detail = client.get(f"/api/venues/{venue.id}/")
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data["contacts"][0]["name"] == "Ann"

    def test_works_from_every_type(self, client, user):
        residency = Residency.objects.create(name="Res", user=user)
        ResidencyContact.objects.create(residency=residency, name="Cy", user=user)

        response = client.post(
            f"/api/residencies/{residency.id}/convert/", {"target_type": "FESTIVAL"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["organisation_type"] == "FESTIVAL"
        assert not Residency.objects.filter(id=residency.id).exists()

    def test_invalid_type_returns_400(self, client, festival):
        response = client.post(
            f"/api/festivals/{festival.id}/convert/", {"target_type": "NOPE"}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid organisation type" in response.data["error"]
        assert Festival.objects.filter(id=festival.id).exists()

    def test_missing_type_returns_400(self, client, festival):
        response = client.post(f"/api/festivals/{festival.id}/convert/", {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_same_type_returns_400(self, client, festival):
        response = client.post(
            f"/api/festivals/{festival.id}/convert/", {"target_type": "FESTIVAL"}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_other_users_organisation_is_not_found(self, client):
        other = Profile.objects.create_user(email="other@example.com", password="pass")
        festival = Festival.objects.create(name="Not mine", user=other)

        response = client.post(
            f"/api/festivals/{festival.id}/convert/", {"target_type": "VENUE"}, format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Festival.objects.filter(id=festival.id).exists()

    def test_staff_cannot_convert_shared_seed(self):
        staff = Profile.objects.create_user(email="staff@example.com", password="pass")
        staff.is_staff = True
        staff.save()
        seed = Festival.objects.create(name="Seed", user=None)
        api_client = APIClient()
        api_client.force_authenticate(user=staff)

        response = api_client.post(
            f"/api/festivals/{seed.id}/convert/", {"target_type": "VENUE"}, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Festival.objects.filter(id=seed.id).exists()

    def test_requires_authentication(self, festival):
        response = APIClient().post(
            f"/api/festivals/{festival.id}/convert/", {"target_type": "VENUE"}, format="json"
        )

        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        assert Festival.objects.filter(id=festival.id).exists()
