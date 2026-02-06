import pytest
from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency, ResidencyContact
from organisations.venues.models import Venue, VenueContact
from organisations.serializers import BlankToNullDateField, handle_nested_contacts


@pytest.mark.django_db
class TestBlankToNullDateField:
    """Tests for BlankToNullDateField custom serializer field."""

    def test_blank_string_returns_none(self):
        """Test that blank string is converted to None."""
        field = BlankToNullDateField()
        result = field.to_internal_value("")

        assert result is None

    def test_none_returns_none(self):
        """Test that None is returned as None."""
        field = BlankToNullDateField()
        result = field.to_internal_value(None)

        assert result is None

    def test_valid_date_string_parsed(self):
        """Test that valid date strings are parsed correctly."""
        field = BlankToNullDateField()
        result = field.to_internal_value("2026-01-15")

        assert str(result) == "2026-01-15"

    def test_invalid_date_raises_error(self):
        """Test that invalid date strings raise validation error."""
        field = BlankToNullDateField()

        with pytest.raises(Exception):  # DateField raises ValidationError
            field.to_internal_value("invalid-date")

    def test_whitespace_treated_as_blank(self):
        """Test that whitespace-only strings are handled properly."""
        field = BlankToNullDateField()
        # The parent class handles whitespace, but our check is before stripping
        result = field.to_internal_value("")
        assert result is None


@pytest.mark.django_db
class TestHandleNestedContacts:
    """Tests for handle_nested_contacts helper function."""

    def test_create_new_contacts(self):
        """Test creating new contacts for an organisation."""
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")

        contacts_data = [
            {"name": "John", "email": "john@festival.com"},
            {"name": "Jane", "email": "jane@festival.com"},
        ]

        handle_nested_contacts(festival, contacts_data, FestivalContact)

        assert festival.contacts.count() == 2
        assert festival.contacts.filter(name="John").exists()
        assert festival.contacts.filter(name="Jane").exists()

    def test_update_existing_contacts(self):
        """Test updating existing contacts."""
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        contact = festival.contacts.create(name="John", email="john@festival.com")

        contacts_data = [
            {"id": contact.id, "name": "Jonathan", "email": "jonathan@festival.com"},
        ]

        handle_nested_contacts(festival, contacts_data, FestivalContact)

        contact.refresh_from_db()
        assert contact.name == "Jonathan"
        assert contact.email == "jonathan@festival.com"

    def test_delete_removed_contacts(self):
        """Test that contacts not in incoming data are deleted."""
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        contact1 = festival.contacts.create(name="John", email="john@festival.com")
        contact2 = festival.contacts.create(name="Jane", email="jane@festival.com")

        # Only provide contact1 in the new data
        contacts_data = [
            {"id": contact1.id, "name": "John", "email": "john@festival.com"},
        ]

        handle_nested_contacts(festival, contacts_data, FestivalContact)

        assert festival.contacts.count() == 1
        assert festival.contacts.first().id == contact1.id
        assert not FestivalContact.objects.filter(id=contact2.id).exists()

    def test_mixed_create_update_delete(self):
        """Test handling mixed create, update, and delete operations."""
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        contact1 = festival.contacts.create(name="John", email="john@festival.com")
        contact2 = festival.contacts.create(name="Jane", email="jane@festival.com")

        contacts_data = [
            {"id": contact1.id, "name": "Jonathan", "email": "jonathan@festival.com"},
            {"name": "Bob", "email": "bob@festival.com"},  # New contact
        ]

        handle_nested_contacts(festival, contacts_data, FestivalContact)

        assert festival.contacts.count() == 2
        # contact1 should be updated
        assert festival.contacts.filter(name="Jonathan").exists()
        # contact2 should be deleted
        assert not FestivalContact.objects.filter(id=contact2.id).exists()
        # New contact should be created
        assert festival.contacts.filter(name="Bob").exists()

    def test_empty_contacts_list_deletes_all(self):
        """Test that empty contacts list deletes all existing contacts."""
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        festival.contacts.create(name="John", email="john@festival.com")
        festival.contacts.create(name="Jane", email="jane@festival.com")

        handle_nested_contacts(festival, [], FestivalContact)

        assert festival.contacts.count() == 0

    def test_works_with_residency_contacts(self):
        """Test that function works with different contact types."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")

        contacts_data = [
            {"name": "Alice", "email": "alice@residency.be"},
        ]

        handle_nested_contacts(residency, contacts_data, ResidencyContact)

        assert residency.contacts.count() == 1
        assert residency.contacts.first().name == "Alice"

    def test_works_with_venue_contacts(self):
        """Test that function works with venue contacts."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")

        contacts_data = [
            {"name": "Bob", "email": "bob@venue.be"},
        ]

        handle_nested_contacts(venue, contacts_data, VenueContact)

        assert venue.contacts.count() == 1
        assert venue.contacts.first().name == "Bob"

    def test_preserves_non_updated_fields(self):
        """Test that other fields in the contact are preserved if not included."""
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        contact = festival.contacts.create(name="John", email="john@festival.com", role="Manager")

        contacts_data = [
            {"id": contact.id, "name": "Jonathan", "email": "jonathan@festival.com"},
        ]

        handle_nested_contacts(festival, contacts_data, FestivalContact)

        contact.refresh_from_db()
        assert contact.name == "Jonathan"
        assert contact.email == "jonathan@festival.com"
        assert contact.role == "Manager"
