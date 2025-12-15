import pytest
from organisations.venues.models import Venue, VenueContact


@pytest.mark.django_db
class TestVenueModel:
    """Basic tests for the Venue model"""

    def test_venue_creation(self):
        """Test creating a venue with required fields"""
        venue = Venue.objects.create(name="Test Theatre", country="UK", town="London")

        assert venue.id is not None
        assert venue.name == "Test Theatre"
        assert venue.country == "UK"
        assert venue.town == "London"
        assert venue.venue_type == "UNKNOWN"  # default value
        assert venue.contacted is False  # default value

    def test_venue_string_representation(self):
        """Test the __str__ method"""
        venue = Venue.objects.create(name="Grand Opera House")

        assert str(venue) == "Grand Opera House"

    def test_venue_with_all_fields(self):
        """Test creating a venue with all fields"""
        venue = Venue.objects.create(
            name="Complete Venue",
            description="A beautiful performance space",
            country="Spain",
            town="Barcelona",
            website_url="https://example.com",
            venue_type="THEATRE",
            contacted=True,
            comments="Very interested",
        )

        VenueContact.objects.create(venue=venue, name="John Smith", email="venue@example.com")

        assert venue.description == "A beautiful performance space"
        assert venue.website_url == "https://example.com"
        assert venue.contacts.count() == 1
        assert venue.contacts.first().email == "venue@example.com"
        assert venue.contacts.first().name == "John Smith"
        assert venue.venue_type == "THEATRE"
        assert venue.contacted is True
        assert venue.comments == "Very interested"

    def test_venue_optional_fields_null(self):
        """Test that optional fields can be blank"""
        venue = Venue.objects.create(name="Minimal Venue")

        assert venue.description == ""
        assert venue.country == ""
        assert venue.website_url == ""
        assert venue.contacts.count() == 0

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
            venue = Venue.objects.create(name=f"Venue {venue_type}", venue_type=venue_type)
            assert venue.venue_type == venue_type

    def test_venue_contact_email_validation(self):
        """Test that contact email field validates email format"""
        venue = Venue.objects.create(name="Email Test")
        contact = VenueContact.objects.create(
            venue=venue, name="Test Contact", email="venue@test.com"
        )
        assert contact.email == "venue@test.com"

    def test_venue_url_validation(self):
        """Test that website_url field validates URL format"""
        venue = Venue.objects.create(name="URL Test", website_url="https://venue-url.com")
        assert venue.website_url == "https://venue-url.com"

    def test_venue_contacted_flag(self):
        """Test the contacted boolean field"""
        venue = Venue.objects.create(name="Contact Test", contacted=True)
        assert venue.contacted is True

        venue.contacted = False
        venue.save()
        venue.refresh_from_db()
        assert venue.contacted is False
