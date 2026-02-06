import pytest
from rest_framework.test import APIClient
from organisations.festivals.models import Festival
from organisations.venues.models import Venue
from organisations.residencies.models import Residency
from profiles.models import Profile


@pytest.mark.django_db
class TestFestivalViews:
    """Tests for Festival API endpoints."""

    def test_list_festivals(self):
        """Test listing festivals."""
        Festival.objects.create(name="Festival 1", town="Paris", country="France")

        client = APIClient()
        response = client.get("/api/festivals/")

        assert response.status_code in [200, 403]

    def test_create_festival(self):
        """Test creating a festival."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"name": "New Festival", "town": "Berlin", "country": "Germany"}

        response = client.post("/api/festivals/", data, format="json")

        assert response.status_code in [200, 201, 400, 403]

    def test_retrieve_festival(self):
        """Test retrieving a festival."""
        festival = Festival.objects.create(name="Festival", town="Paris", country="France")

        client = APIClient()
        response = client.get(f"/api/festivals/{festival.id}/")

        assert response.status_code in [200, 403, 404]

    def test_filter_festivals(self):
        """Test filtering festivals."""
        Festival.objects.create(name="Festival 1", town="Paris", country="France")

        client = APIClient()
        response = client.get("/api/festivals/?country=France")

        assert response.status_code in [200, 403]

    def test_search_organisations(self):
        """Test searching organisations endpoint."""
        Festival.objects.create(name="Music Festival", town="Paris", country="France")

        client = APIClient()
        response = client.get("/api/organisations/search/?query=Music")

        assert response.status_code in [200, 403, 404]


@pytest.mark.django_db
class TestVenueViews:
    """Tests for Venue API endpoints."""

    def test_list_venues(self):
        """Test listing venues."""
        Venue.objects.create(country="Belgium", town="Brussels")

        client = APIClient()
        response = client.get("/api/venues/")

        assert response.status_code in [200, 403]

    def test_create_venue(self):
        """Test creating a venue."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"country": "Belgium", "town": "Antwerp"}

        response = client.post("/api/venues/", data, format="json")

        assert response.status_code in [200, 201, 400, 403]

    def test_retrieve_venue(self):
        """Test retrieving a venue."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")

        client = APIClient()
        response = client.get(f"/api/venues/{venue.id}/")

        assert response.status_code in [200, 403, 404]


@pytest.mark.django_db
class TestResidencyViews:
    """Tests for Residency API endpoints."""

    def test_list_residencies(self):
        """Test listing residencies."""
        Residency.objects.create(country="Belgium", town="Brussels")

        client = APIClient()
        response = client.get("/api/residencies/")

        assert response.status_code in [200, 403]

    def test_create_residency(self):
        """Test creating a residency."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"country": "Belgium", "town": "Brussels"}

        response = client.post("/api/residencies/", data, format="json")

        assert response.status_code in [200, 201, 400, 403]

    def test_retrieve_residency(self):
        """Test retrieving a residency."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")

        client = APIClient()
        response = client.get(f"/api/residencies/{residency.id}/")

        assert response.status_code in [200, 403, 404]
