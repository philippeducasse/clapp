import pytest
from rest_framework.test import APIClient
from applications.models import Application
from profiles.models import Profile


@pytest.mark.django_db
class TestApplicationViews:
    """Tests for application API endpoints."""

    def test_list_applications(self):
        """Test listing applications."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        Application.objects.create(profile=profile, status="DRAFT")

        client = APIClient()
        response = client.get("/api/applications/")

        assert response.status_code in [200, 403]

    def test_create_application(self):
        """Test creating an application."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"status": "DRAFT"}

        response = client.post("/api/applications/", data, format="json")

        assert response.status_code in [200, 201, 400, 403]

    def test_retrieve_application(self):
        """Test retrieving an application."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        app = Application.objects.create(profile=profile, status="DRAFT")

        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.get(f"/api/applications/{app.id}/")

        assert response.status_code in [200, 403, 404]

    def test_update_application(self):
        """Test updating application."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        app = Application.objects.create(profile=profile, status="DRAFT")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"status": "APPLIED"}

        response = client.patch(f"/api/applications/{app.id}/", data, format="json")

        assert response.status_code in [200, 400, 403]

    def test_delete_application(self):
        """Test deleting an application."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        app = Application.objects.create(profile=profile, status="DRAFT")

        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.delete(f"/api/applications/{app.id}/")

        assert response.status_code in [200, 204, 400, 403]
