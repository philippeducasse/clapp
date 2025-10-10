import pytest
from organisations.venues.models import Venue


@pytest.mark.django_db
class TestVenueModel:
    """Basic tests for the Venue model"""

    def test_venue_creation(self):
        """Test creating a venue with required fields"""
        venue = Venue.objects.create(
            venue_name="Test Theatre", country="UK", town="London"
        )

        assert venue.id is not None
        assert venue.venue_name == "Test Theatre"
        assert venue.country == "UK"
        assert venue.town == "London"
        assert venue.venue_type == "UNKNOWN"  # default value
        assert venue.contacted is False  # default value

    def test_venue_string_representation(self):
        """Test the __str__ method"""
        venue = Venue.objects.create(venue_name="Grand Opera House")

        assert str(venue) == "Grand Opera House"

    def test_venue_with_all_fields(self):
        """Test creating a venue with all fields"""
        venue = Venue.objects.create(
            venue_name="Complete Venue",
            description="A beautiful performance space",
            country="Spain",
            town="Barcelona",
            website_url="https://example.com",
            contact_email="venue@example.com",
            contact_person="John Smith",
            venue_type="THEATRE",
            contacted=True,
            comments="Very interested",
        )

        assert venue.description == "A beautiful performance space"
        assert venue.website_url == "https://example.com"
        assert venue.contact_email == "venue@example.com"
        assert venue.contact_person == "John Smith"
        assert venue.venue_type == "THEATRE"
        assert venue.contacted is True
        assert venue.comments == "Very interested"

    def test_venue_optional_fields_null(self):
        """Test that optional fields can be null"""
        venue = Venue.objects.create(venue_name="Minimal Venue")

        assert venue.description is None
        assert venue.country is None
        assert venue.website_url is None
        assert venue.contact_email is None
        assert venue.contact_person is None

    def test_venue_type_choices(self):
        """Test valid venue type choices"""
        types = [
            "THEATRE",
            "OPERA_HOUSE",
            "CONCERT_HALL",
            "CIRCUS_TENT",
            "OUTDOOR_STAGE",
            "OTHER",
        ]

        for venue_type in types:
            venue = Venue.objects.create(
                venue_name=f"Venue {venue_type}", venue_type=venue_type
            )
            assert venue.venue_type == venue_type

    def test_venue_email_validation(self):
        """Test that contact_email field validates email format"""
        venue = Venue.objects.create(
            venue_name="Email Test", contact_email="venue@test.com"
        )
        assert venue.contact_email == "venue@test.com"

    def test_venue_url_validation(self):
        """Test that website_url field validates URL format"""
        venue = Venue.objects.create(
            venue_name="URL Test", website_url="https://venue-url.com"
        )
        assert venue.website_url == "https://venue-url.com"

    def test_venue_contacted_flag(self):
        """Test the contacted boolean field"""
        venue = Venue.objects.create(venue_name="Contact Test", contacted=True)
        assert venue.contacted is True

        venue.contacted = False
        venue.save()
        venue.refresh_from_db()
        assert venue.contacted is False
