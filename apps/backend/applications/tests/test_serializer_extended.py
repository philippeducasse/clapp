"""Extended tests for applications/serializer.py."""
import pytest
from django.contrib.contenttypes.models import ContentType

from applications.models import Application
from applications.serializer import ApplicationSerializer
from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.venues.models import Venue
from profiles.models import Profile


@pytest.mark.django_db
class TestApplicationSerializerToRepresentation:
    """Tests for to_representation and get_organisation_type_display."""

    def test_to_representation_with_festival(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        app = Application.objects.create(
            profile=profile,
            organisation=festival,
            status="DRAFT",
        )

        serializer = ApplicationSerializer(app)
        data = serializer.data

        assert data["organisation_type"] == "FESTIVAL"
        assert isinstance(data["organisation"], dict)
        assert data["organisation"]["name"] == "Test Fest"

    def test_to_representation_with_venue(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        venue = Venue.objects.create(name="Test Venue", town="London", country="UK", user=profile)
        app = Application.objects.create(
            profile=profile,
            organisation=venue,
            status="DRAFT",
        )

        serializer = ApplicationSerializer(app)
        data = serializer.data

        assert data["organisation_type"] == "VENUE"
        assert isinstance(data["organisation"], dict)

    def test_to_representation_with_residency(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        residency = Residency.objects.create(
            name="Test Residency", town="Berlin", country="Germany", user=profile
        )
        app = Application.objects.create(
            profile=profile,
            organisation=residency,
            status="DRAFT",
        )

        serializer = ApplicationSerializer(app)
        data = serializer.data

        assert data["organisation_type"] == "RESIDENCY"
        assert isinstance(data["organisation"], dict)

    def test_to_representation_no_organisation(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        app = Application.objects.create(profile=profile, status="DRAFT")

        serializer = ApplicationSerializer(app)
        data = serializer.data

        assert data["organisation_type"] is None

    def test_get_organisation_type_display_with_content_type(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        app = Application.objects.create(
            profile=profile,
            organisation=festival,
            status="DRAFT",
        )

        serializer = ApplicationSerializer(app)
        result = serializer.get_organisation_type_display(app)
        assert result == "FESTIVAL"

    def test_get_organisation_type_display_no_content_type(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        app = Application.objects.create(profile=profile, status="DRAFT")

        serializer = ApplicationSerializer(app)
        result = serializer.get_organisation_type_display(app)
        assert result is None


@pytest.mark.django_db
class TestApplicationSerializerCreate:
    """Tests for ApplicationSerializer.create()."""

    def test_create_with_festival_organisation(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )

        data = {
            "profile_id": profile.id,
            "status": "DRAFT",
            "organisation_type": "festival",
            "organisation": festival.id,
        }
        serializer = ApplicationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        app = serializer.save()

        assert app.content_type is not None
        assert app.object_id == festival.id

    def test_create_with_invalid_organisation_type(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")

        data = {
            "profile_id": profile.id,
            "status": "DRAFT",
            "organisation_type": "invalidtype",
            "organisation": 1,
        }
        serializer = ApplicationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        with pytest.raises(Exception):
            serializer.save()

    def test_create_without_organisation(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")

        data = {
            "profile_id": profile.id,
            "status": "DRAFT",
        }
        serializer = ApplicationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        app = serializer.save()
        assert app.content_type is None


@pytest.mark.django_db
class TestApplicationSerializerUpdate:
    """Tests for ApplicationSerializer.update()."""

    def test_update_with_new_organisation_type(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        app = Application.objects.create(profile=profile, status="DRAFT")

        data = {
            "organisation_type": "festival",
            "organisation": festival.id,
        }
        serializer = ApplicationSerializer(app, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()

        assert updated.content_type is not None
        assert updated.object_id == festival.id

    def test_update_with_invalid_organisation_type(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        app = Application.objects.create(profile=profile, status="DRAFT")

        data = {"organisation_type": "nonexistent"}
        serializer = ApplicationSerializer(app, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        with pytest.raises(Exception):
            serializer.save()

    def test_update_with_organisation_id_only(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        # Create an app already linked to festival (to have content_type set)
        app = Application.objects.create(
            profile=profile,
            organisation=festival,
            status="DRAFT",
        )

        venue = Venue.objects.create(
            name="New Venue", town="London", country="UK", user=profile
        )
        data = {"organisation": venue.id}
        serializer = ApplicationSerializer(app, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.object_id == venue.id
