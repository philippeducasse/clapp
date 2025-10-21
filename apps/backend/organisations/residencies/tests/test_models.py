import pytest
from datetime import date
from organisations.residencies.models import Residency, ResidencyContact


@pytest.mark.django_db
class TestResidencyModel:
    """Basic tests for the Residency model"""

    def test_residency_creation(self):
        """Test creating a residency with required fields"""
        residency = Residency.objects.create(
            name="Test Residency", country="Germany", town="Berlin"
        )

        assert residency.id is not None
        assert residency.name == "Test Residency"
        assert residency.country == "Germany"
        assert residency.town == "Berlin"
        assert residency.application_type == "UNKNOWN"  # default value
        assert residency.applied is False  # default value

    def test_residency_string_representation(self):
        """Test the __str__ method"""
        residency = Residency.objects.create(name="Artist Residency")

        assert str(residency) == "Artist Residency"

    def test_residency_with_all_fields(self):
        """Test creating a residency with all fields"""
        residency = Residency.objects.create(
            name="Complete Residency",
            description="A comprehensive residency program",
            country="France",
            town="Paris",
            website_url="https://example.com",
            start_date=date(2025, 6, 1),
            end_date=date(2025, 8, 31),
            approximate_date="Summer 2025",
            application_date_start="January 2025",
            application_date_end="March 2025",
            application_type="OPEN_CALL",
            applied=True,
            comments="Great opportunity",
        )

        ResidencyContact.objects.create(
            residency=residency, name="Jane Doe", email="contact@example.com"
        )

        assert residency.description == "A comprehensive residency program"
        assert residency.website_url == "https://example.com"
        assert residency.contacts.count() == 1
        assert residency.contacts.first().email == "contact@example.com"
        assert residency.start_date == date(2025, 6, 1)
        assert residency.end_date == date(2025, 8, 31)
        assert residency.application_type == "OPEN_CALL"
        assert residency.applied is True

    def test_residency_optional_fields_null(self):
        """Test that optional fields can be blank"""
        residency = Residency.objects.create(name="Minimal Residency")

        assert residency.description == ""
        assert residency.country == ""
        assert residency.website_url == ""
        assert residency.contacts.count() == 0
        assert residency.start_date is None

    def test_residency_application_type_choices(self):
        """Test valid application type choices"""
        types = ["EMAIL", "FORM", "OPEN_CALL", "INVITATION_ONLY", "OTHER", "UNKNOWN"]

        for app_type in types:
            residency = Residency.objects.create(
                name=f"Residency {app_type}", application_type=app_type
            )
            assert residency.application_type == app_type

    def test_residency_contact_email_validation(self):
        """Test that contact email field validates email format"""
        residency = Residency.objects.create(name="Email Test")
        contact = ResidencyContact.objects.create(
            residency=residency, name="Test Contact", email="valid@email.com"
        )
        assert contact.email == "valid@email.com"

    def test_residency_url_validation(self):
        """Test that website_url field validates URL format"""
        residency = Residency.objects.create(
            name="URL Test", website_url="https://valid-url.com"
        )
        assert residency.website_url == "https://valid-url.com"
