import pytest

from profiles.models import Profile


@pytest.mark.django_db
class TestProfileModel:
    """Basic tests for the Profile model"""

    def test_profile_creation_with_manager(self):
        """Test creating a profile using the custom manager"""
        profile = Profile.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

        assert profile.id is not None
        assert profile.email == "test@example.com"
        assert profile.first_name == "John"
        assert profile.last_name == "Doe"
        assert profile.check_password("testpass123") is True

    def test_profile_string_representation(self):
        """Test the __str__ method returns email"""
        profile = Profile.objects.create_user(email="artist@example.com", password="testpass123")

        assert str(profile) == "artist@example.com"

    def test_profile_email_is_unique(self):
        """Test that email must be unique"""
        Profile.objects.create_user(email="unique@example.com", password="testpass123")

        with pytest.raises(Exception):  # Will raise IntegrityError
            Profile.objects.create_user(email="unique@example.com", password="anotherpass")

    def test_profile_username_field_is_email(self):
        """Test that USERNAME_FIELD is email"""
        assert Profile.USERNAME_FIELD == "email"

    def test_profile_with_all_fields(self):
        """Test creating a profile with all optional fields"""
        profile = Profile.objects.create_user(
            email="complete@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
            company_name="Amazing Jane",
            personal_website="https://janesmith.com",
            location="Paris, France",
            nationality="French",
            instagram_profile="https://instagram.com/jane",
            facebook_profile="https://facebook.com/jane",
            tiktok_profile="https://tiktok.com/@jane",
            youtube_profile="https://youtube.com/@jane",
            phone="+33123456789",
        )

        assert profile.company_name == "Amazing Jane"
        assert profile.company_name == "Smith Productions"
        assert profile.personal_website == "https://janesmith.com"
        assert profile.age == 30
        assert profile.location == "Paris, France"
        assert profile.nationality == "French"

    def test_profile_optional_fields_null(self):
        """Test that optional fields can be blank or null"""
        profile = Profile.objects.create_user(email="minimal@example.com", password="testpass123")

        # CharField fields with blank=True default to empty string
        assert profile.company_name == ""
        assert profile.company_name == ""
        assert profile.age is None
        assert profile.location == ""

    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = Profile.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.email == "admin@example.com"

    def test_profile_password_hashing(self):
        """Test that passwords are hashed"""
        profile = Profile.objects.create_user(email="secure@example.com", password="mypassword")

        # Password should be hashed, not stored in plain text
        assert profile.password != "mypassword"
        assert profile.check_password("mypassword") is True
        assert profile.check_password("wrongpassword") is False

    def test_profile_manager_requires_email(self):
        """Test that ProfileManager requires an email"""
        with pytest.raises(ValueError, match="Users must provide an email address"):
            Profile.objects.create_user(email="", password="testpass123")
