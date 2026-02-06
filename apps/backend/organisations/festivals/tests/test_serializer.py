import pytest
from organisations.festivals.models import Festival
from organisations.festivals.serializer import FestivalSerializer


@pytest.mark.django_db
class TestFestivalSerializer:
    """Tests for FestivalSerializer."""

    def test_serialize_festival(self):
        """Test serializing a festival."""
        festival = Festival.objects.create(
            name="Test Festival", town="Paris", country="France", description="A great festival"
        )

        serializer = FestivalSerializer(festival)
        data = serializer.data

        assert data["name"] == "Test Festival"
        assert data["town"] == "Paris"
        assert data["country"] == "France"

    def test_create_festival_via_serializer(self):
        """Test creating festival via serializer."""
        data = {
            "name": "New Festival",
            "town": "Berlin",
            "country": "Germany",
            "description": "A new festival",
        }

        serializer = FestivalSerializer(data=data)
        assert serializer.is_valid()
        festival = serializer.save()

        assert festival.name == "New Festival"
        assert festival.town == "Berlin"

    def test_update_festival_via_serializer(self):
        """Test updating festival via serializer."""
        festival = Festival.objects.create(name="Old Name", town="Paris", country="France")

        data = {"name": "Updated Name"}
        serializer = FestivalSerializer(festival, data=data, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()

        assert updated.name == "Updated Name"
        assert updated.town == "Paris"

    def test_nested_contacts_serialization(self):
        """Test that contacts are properly serialized."""
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        festival.contacts.create(email="info@festival.com", name="Info")

        serializer = FestivalSerializer(festival)
        data = serializer.data

        assert "contacts" in data
        assert len(data["contacts"]) == 1
        assert data["contacts"][0]["email"] == "info@festival.com"

    def test_festival_type_field(self):
        """Test festival_type field validation."""
        data = {
            "name": "Street Festival",
            "town": "Madrid",
            "country": "Spain",
            "festival_type": "STREET",
        }

        serializer = FestivalSerializer(data=data)
        assert serializer.is_valid()
        festival = serializer.save()

        assert festival.festival_type == "STREET"
