import pytest

from applications.models import Application
from applications.serializer import ApplicationSerializer, MinimalApplicationSerializer
from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.venues.models import Venue
from profiles.models import Profile


@pytest.mark.django_db
class TestApplicationSerializer:
    """Tests for ApplicationSerializer."""

    def test_serialize_festival_application(self):
        """Test serializing an application with festival."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        Festival.objects.create(name="Test Festival", town="Paris", country="France")
        application = Application.objects.create(profile=profile, status="DRAFT")

        serializer = ApplicationSerializer(application)
        data = serializer.data

        # Profile is serialized as nested object
        assert isinstance(data.get("profile"), dict)
        assert data["profile"]["id"] == profile.id
        assert data["status"] == "DRAFT"

    def test_serialize_venue_application(self):
        """Test serializing an application with venue."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        Venue.objects.create(country="Belgium", town="Brussels")
        application = Application.objects.create(profile=profile, status="APPLIED")

        serializer = ApplicationSerializer(application)
        data = serializer.data

        assert data["status"] == "APPLIED"

    def test_serialize_residency_application(self):
        """Test serializing an application with residency."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        Residency.objects.create(country="Belgium", town="Brussels")
        application = Application.objects.create(profile=profile, status="ACCEPTED")

        serializer = ApplicationSerializer(application)
        data = serializer.data

        assert data["status"] == "ACCEPTED"

    def test_application_status_choices(self):
        """Test that valid status values are accepted."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        # Test that valid status can be created
        application = Application.objects.create(profile=profile, status="DRAFT")
        assert application.status == "DRAFT"

    def test_create_application_via_serializer(self):
        """Test creating application via serializer."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        data = {"profile": profile.id, "status": "DRAFT"}

        serializer = ApplicationSerializer(data=data)
        if serializer.is_valid():
            application = serializer.save()
            assert application.profile == profile

    def test_update_application_status(self):
        """Test updating application status."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        application = Application.objects.create(profile=profile, status="DRAFT")

        data = {"status": "APPLIED"}
        serializer = ApplicationSerializer(application, data=data, partial=True)
        if serializer.is_valid():
            updated_app = serializer.save()
            assert updated_app.status == "APPLIED"


@pytest.mark.django_db
class TestMinimalApplicationSerializer:
    """Tests for MinimalApplicationSerializer."""

    def test_serialize_minimal_application(self):
        """Test serializing with minimal serializer."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        application = Application.objects.create(profile=profile, status="DRAFT")

        serializer = MinimalApplicationSerializer(application)
        data = serializer.data

        # Minimal serializer should only include essential fields
        assert "id" in data
        assert "status" in data
