import pytest
from profiles.models import Profile
from profiles.serializers import ProfileSerializer


@pytest.mark.django_db
class TestProfileSerializer:
    """Tests for ProfileSerializer."""

    def test_serialize_profile(self):
        """Test serializing a profile."""
        profile = Profile.objects.create_user(
            email="test@example.com", password="testpass123", first_name="John", last_name="Doe"
        )

        serializer = ProfileSerializer(profile)
        data = serializer.data

        assert data["email"] == "test@example.com"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    def test_create_profile_via_serializer(self):
        """Test creating profile via serializer."""
        data = {
            "email": "new@example.com",
            "password": "newpass123",
            "first_name": "Jane",
            "last_name": "Smith",
        }

        serializer = ProfileSerializer(data=data)
        assert serializer.is_valid()
        profile = serializer.save()

        assert profile.email == "new@example.com"
        assert profile.first_name == "Jane"

    def test_serializer_excludes_password_from_data(self):
        """Test that password is not included in serialized data."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        serializer = ProfileSerializer(profile)
        data = serializer.data

        assert "password" not in data

    def test_update_profile_via_serializer(self):
        """Test updating profile via serializer."""
        profile = Profile.objects.create_user(
            email="test@example.com", password="testpass123", first_name="John"
        )

        data = {"first_name": "Jonathan", "last_name": "Doe"}
        serializer = ProfileSerializer(profile, data=data, partial=True)
        assert serializer.is_valid()
        updated_profile = serializer.save()

        assert updated_profile.first_name == "Jonathan"
        assert updated_profile.email == "test@example.com"

    def test_required_email_field(self):
        """Test that email is a required field."""
        data = {"first_name": "John", "last_name": "Doe"}

        serializer = ProfileSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_invalid_email_format_rejected(self):
        """Test that invalid email formats are rejected."""
        data = {"email": "not-an-email", "password": "testpass123"}

        serializer = ProfileSerializer(data=data)
        assert not serializer.is_valid()
