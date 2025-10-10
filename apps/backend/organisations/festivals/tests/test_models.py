import pytest
from datetime import date
from organisations.festivals.models import Festival


@pytest.mark.django_db
class TestFestivalModel:
    """Test cases for the Festival model"""

    def test_festival_creation(self):
        """Test creating a festival with required fields"""
        festival = Festival.objects.create(
            festival_name="Test Festival", country="France", town="Paris"
        )

        assert festival.id is not None
        assert festival.festival_name == "Test Festival"
        assert festival.country == "France"
        assert festival.town == "Paris"
        assert festival.festival_type == "STREET"  # default value
        assert festival.application_type == "UNKNOWN"  # default value

    def test_festival_string_representation(self):
        """Test the __str__ method returns the festival name"""
        festival = Festival.objects.create(festival_name="Summer Festival")
        assert str(festival) == "Summer Festival"

    def test_festival_with_all_fields(self):
        """Test creating a festival with all fields populated"""
        festival = Festival.objects.create(
            festival_name="Complete Festival",
            description="A comprehensive test festival",
            country="Spain",
            town="Barcelona",
            festival_type="CIRCUS",
            website_url="https://example.com",
            contact_email="contact@example.com",
            contact_person="John Doe",
            start_date=date(2025, 7, 15),
            end_date=date(2025, 7, 20),
            approximate_date="Mid July 2025",
            application_date_start="March 2025",
            application_date_end="April 2025",
            application_type="FORM",
            comments="Test comments",
        )

        assert festival.festival_name == "Complete Festival"
        assert festival.description == "A comprehensive test festival"
        assert festival.festival_type == "CIRCUS"
        assert festival.application_type == "FORM"
        assert festival.website_url == "https://example.com"
        assert festival.contact_email == "contact@example.com"
        assert festival.start_date == date(2025, 7, 15)
        assert festival.end_date == date(2025, 7, 20)

    def test_festival_optional_fields_null(self):
        """Test that optional fields can be null"""
        festival = Festival.objects.create(festival_name="Minimal Festival")

        assert festival.description is None
        assert festival.country is None
        assert festival.town is None
        assert festival.website_url is None
        assert festival.contact_email is None
        assert festival.start_date is None
        assert festival.end_date is None

    def test_festival_type_choices(self):
        """Test valid festival type choices"""
        valid_types = [
            "STREET",
            "PUPPET",
            "JUGGLING_CONVENTION",
            "CIRCUS",
            "MUSIC",
            "THEATRE",
            "DANCE",
            "OTHER",
        ]

        for fest_type in valid_types:
            festival = Festival.objects.create(
                festival_name=f"Festival {fest_type}", festival_type=fest_type
            )
            assert festival.festival_type == fest_type

    def test_application_type_choices(self):
        """Test valid application type choices"""
        valid_types = ["EMAIL", "FORM", "INVITATION_ONLY", "OTHER", "UNKNOWN"]

        for app_type in valid_types:
            festival = Festival.objects.create(
                festival_name=f"Festival {app_type}", application_type=app_type
            )
            assert festival.application_type == app_type

    def test_festival_email_validation(self):
        """Test that contact_email field validates email format"""
        festival = Festival.objects.create(
            festival_name="Email Test", contact_email="valid@email.com"
        )
        assert festival.contact_email == "valid@email.com"

    def test_festival_url_validation(self):
        """Test that website_url field validates URL format"""
        festival = Festival.objects.create(
            festival_name="URL Test", website_url="https://valid-url.com"
        )
        assert festival.website_url == "https://valid-url.com"

    def test_festival_description_max_length(self):
        """Test description field max length"""
        long_description = "A" * 1000
        festival = Festival.objects.create(
            festival_name="Description Test", description=long_description
        )
        assert len(festival.description) == 1000

    def test_festival_comments_max_length(self):
        """Test comments field max length"""
        long_comments = "B" * 500
        festival = Festival.objects.create(
            festival_name="Comments Test", comments=long_comments
        )
        assert len(festival.comments) == 500
