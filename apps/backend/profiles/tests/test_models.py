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
        assert profile.personal_website == "https://janesmith.com"
        assert profile.location == "Paris, France"
        assert profile.nationality == "French"

    def test_profile_optional_fields_null(self):
        """Test that optional fields can be blank or null"""
        profile = Profile.objects.create_user(email="minimal@example.com", password="testpass123")

        assert profile.company_name == ""
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

    def test_email_host_password_encryption(self):
        """Test that email_host_password field encrypts data"""
        plaintext_password = "MySecurePassword123!"
        profile = Profile.objects.create_user(
            email="encrypted@example.com",
            password="testpass123",
            email_host_password=plaintext_password,
        )

        # Retrieve the profile and verify the password is decrypted correctly
        retrieved_profile = Profile.objects.get(id=profile.id)
        assert retrieved_profile.email_host_password == plaintext_password

    def test_email_host_password_is_stored_encrypted(self):
        """Test that email_host_password is actually encrypted in the database"""
        plaintext_password = "MySecurePassword123!"
        profile = Profile.objects.create_user(
            email="encrypted2@example.com",
            password="testpass123",
            email_host_password=plaintext_password,
        )

        # Get the raw database value to verify it's encrypted
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT email_host_password FROM profiles_profile WHERE id = %s",
                [profile.id],
            )
            row = cursor.fetchone()
            stored_value = row[0]

        # The stored value should not be the plaintext password
        assert stored_value != plaintext_password
        # But when retrieved through Django, it should be decrypted
        retrieved_profile = Profile.objects.get(id=profile.id)
        assert retrieved_profile.email_host_password == plaintext_password

    def test_email_host_password_blank_value(self):
        """Test that email_host_password can be blank"""
        profile = Profile.objects.create_user(
            email="nopwd@example.com",
            password="testpass123",
            email_host_password="",
        )

        retrieved_profile = Profile.objects.get(id=profile.id)
        assert retrieved_profile.email_host_password == ""

    def test_email_host_password_special_characters(self):
        """Test that email_host_password handles special characters"""
        special_password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
        profile = Profile.objects.create_user(
            email="special@example.com",
            password="testpass123",
            email_host_password=special_password,
        )

        retrieved_profile = Profile.objects.get(id=profile.id)
        assert retrieved_profile.email_host_password == special_password

    def test_email_host_password_unicode_characters(self):
        """Test that email_host_password handles unicode characters"""
        unicode_password = "Pässwörd™🔐日本語"
        profile = Profile.objects.create_user(
            email="unicode@example.com",
            password="testpass123",
            email_host_password=unicode_password,
        )

        retrieved_profile = Profile.objects.get(id=profile.id)
        assert retrieved_profile.email_host_password == unicode_password

    def test_email_host_password_max_length(self):
        """Test that email_host_password respects max_length"""
        # Create a password at the max length (255 characters)
        long_password = "a" * 255
        profile = Profile.objects.create_user(
            email="longpwd@example.com",
            password="testpass123",
            email_host_password=long_password,
        )

        retrieved_profile = Profile.objects.get(id=profile.id)
        assert retrieved_profile.email_host_password == long_password
        assert len(retrieved_profile.email_host_password) == 255

    def test_email_host_password_multiple_profiles_isolated(self):
        """Test that encrypted passwords are isolated between profiles"""
        pwd1 = "FirstProfilePassword123"
        pwd2 = "SecondProfilePassword456"

        profile1 = Profile.objects.create_user(
            email="profile1@example.com",
            password="testpass123",
            email_host_password=pwd1,
        )
        profile2 = Profile.objects.create_user(
            email="profile2@example.com",
            password="testpass123",
            email_host_password=pwd2,
        )

        # Verify each profile has its own password
        retrieved1 = Profile.objects.get(id=profile1.id)
        retrieved2 = Profile.objects.get(id=profile2.id)

        assert retrieved1.email_host_password == pwd1
        assert retrieved2.email_host_password == pwd2
        assert retrieved1.email_host_password != retrieved2.email_host_password

    def test_email_host_password_update(self):
        """Test that email_host_password can be updated"""
        initial_password = "InitialPassword123"
        updated_password = "UpdatedPassword456"

        profile = Profile.objects.create_user(
            email="update@example.com",
            password="testpass123",
            email_host_password=initial_password,
        )

        # Update the password
        profile.email_host_password = updated_password
        profile.save()

        # Verify the update
        retrieved_profile = Profile.objects.get(id=profile.id)
        assert retrieved_profile.email_host_password == updated_password
        assert retrieved_profile.email_host_password != initial_password
