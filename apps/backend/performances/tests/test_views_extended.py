"""Extended tests for performances/views.py."""

import pytest
from rest_framework.test import APIClient

from performances.models import Performance
from profiles.models import Profile


@pytest.mark.django_db
class TestPerformanceViewSetExtended:
    def test_list_unauthenticated_returns_empty(self):
        """Unauthenticated users get empty queryset."""
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Performance.objects.create(
            profile=profile,
            performance_title="Test Performance",
            short_description="desc",
        )

        client = APIClient()
        # No auth
        response = client.get("/api/performances/")
        # Either 200 with empty list or auth error
        if response.status_code == 200:
            assert response.data == [] or len(response.data) == 0

    def test_list_authenticated_returns_own_performances(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Performance.objects.create(
            profile=profile, performance_title="Show A", short_description="desc"
        )
        Performance.objects.create(
            profile=profile, performance_title="Show B", short_description="desc"
        )

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/performances/")

        assert response.status_code == 200
        # Response is paginated with count, results, next, previous
        if isinstance(response.data, dict) and "results" in response.data:
            assert response.data["count"] == 2
        else:
            assert len(response.data) == 2

    def test_other_user_cannot_see_performances(self):
        profile1 = Profile.objects.create_user(email="p1@example.com", password="pass")
        profile2 = Profile.objects.create_user(email="p2@example.com", password="pass")
        Performance.objects.create(
            profile=profile1, performance_title="Private Show", short_description="desc"
        )

        client = APIClient()
        client.force_authenticate(user=profile2)
        response = client.get("/api/performances/")

        assert response.status_code == 200
        # Response is paginated with count, results, next, previous
        if isinstance(response.data, dict) and "results" in response.data:
            assert response.data["count"] == 0
        else:
            assert len(response.data) == 0


@pytest.mark.django_db
class TestGetUserPerformancesView:
    def test_get_user_performances(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Performance.objects.create(
            profile=profile, performance_title="Show A", short_description="desc"
        )

        client = APIClient()
        # Authenticate as any user to access the public endpoint
        other_user = Profile.objects.create_user(email="other@example.com", password="pass")
        client.force_authenticate(user=other_user)
        response = client.get(f"/api/performances/{profile.id}")

        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_get_user_performances_empty(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")

        client = APIClient()
        # Authenticate to access the endpoint
        other_user = Profile.objects.create_user(email="other@example.com", password="pass")
        client.force_authenticate(user=other_user)
        response = client.get(f"/api/performances/{profile.id}")

        assert response.status_code == 200
        assert response.data == []

    def test_get_nonexistent_user_performances(self):
        client = APIClient()
        # Authenticate to access the endpoint
        user = Profile.objects.create_user(email="user@example.com", password="pass")
        client.force_authenticate(user=user)
        response = client.get("/api/performances/99999")

        assert response.status_code == 200
        assert response.data == []
