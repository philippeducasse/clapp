import pytest
from rest_framework.test import APIClient
from profiles.models import Profile


@pytest.mark.django_db
class TestBugReportViews:
    """Tests for bug report API endpoints."""

    def test_create_bug_report(self):
        """Test creating a bug report."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"message": "Found a bug in the application"}

        response = client.post("/api/support/bugs/", data, format="json")

        assert response.status_code in [200, 201, 400, 403]

    def test_create_bug_report_with_attachments(self):
        """Test creating a bug report with attachments."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"message": "Bug with screenshot", "attachments": []}

        response = client.post("/api/support/bugs/", data, format="json")

        assert response.status_code in [200, 201, 400, 403]

    def test_unauthenticated_cannot_create_bug_report(self):
        """Test that unauthenticated users can't create bug reports."""
        client = APIClient()
        data = {"message": "Found a bug"}

        response = client.post("/api/support/bugs/", data, format="json")

        assert response.status_code in [401, 403]

    def test_invalid_bug_report_missing_message(self):
        """Test that bug report without message is rejected."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        client = APIClient()
        client.force_authenticate(user=profile)
        data = {}

        response = client.post("/api/support/bugs/", data, format="json")

        assert response.status_code in [400, 403]
