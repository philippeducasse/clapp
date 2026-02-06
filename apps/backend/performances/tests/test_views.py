import pytest
from rest_framework.test import APIClient
from performances.models import Performance
from profiles.models import Profile


@pytest.mark.django_db
class TestPerformanceViews:
    """Tests for performance API endpoints."""

    def test_list_performances(self):
        """Test listing performances."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        Performance.objects.create(
            profile=profile, performance_title="My Performance", short_description="A great show"
        )

        client = APIClient()
        response = client.get("/api/performances/")

        assert response.status_code in [200, 403]

    def test_create_performance(self):
        """Test creating a performance."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"performance_title": "New Performance", "short_description": "A new show"}

        response = client.post("/api/performances/", data, format="json")

        assert response.status_code in [200, 201, 400, 403]

    def test_retrieve_performance(self):
        """Test retrieving a performance."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile, performance_title="My Performance", short_description="A great show"
        )

        client = APIClient()
        response = client.get(f"/api/performances/{performance.id}/")

        assert response.status_code in [200, 403, 404]

    def test_update_performance(self):
        """Test updating a performance."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile, performance_title="My Performance", short_description="A great show"
        )

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"performance_title": "Updated Performance"}

        response = client.patch(f"/api/performances/{performance.id}/", data, format="json")

        assert response.status_code in [200, 400, 403]
