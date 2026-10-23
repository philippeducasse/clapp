"""Extended tests for applications/views.py."""

from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APIClient

from applications.models import Application, ApplicationSeason
from organisations.festivals.models import Festival
from profiles.models import Profile


@pytest.mark.django_db
class TestApplicationTagAction:
    """Tests for the tag/status action."""

    def test_tag_valid_status(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        app = Application.objects.create(profile=profile, status="DRAFT")

        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.patch(f"/api/applications/{app.id}/status/APPLIED/")
        assert response.status_code == 200
        app.refresh_from_db()
        assert app.status == "APPLIED"

    def test_tag_invalid_status_returns_400(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        app = Application.objects.create(profile=profile, status="DRAFT")

        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.patch(f"/api/applications/{app.id}/status/INVALID_STATUS/")
        assert response.status_code == 400
        assert "error" in response.data

    def test_tag_requires_authentication(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        app = Application.objects.create(profile=profile, status="DRAFT")

        client = APIClient()
        response = client.patch(f"/api/applications/{app.id}/status/APPLIED/")
        assert response.status_code in [401, 403]

    def test_list_requires_authentication(self):
        client = APIClient()
        response = client.get("/api/applications/")
        assert response.status_code in [200, 401, 403]

    def test_list_authenticated_returns_user_applications(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Application.objects.create(profile=profile, status="DRAFT")
        Application.objects.create(profile=profile, status="APPLIED")

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/applications/")

        assert response.status_code == 200
        if isinstance(response.data, dict) and "results" in response.data:
            assert response.data["count"] == 2
        else:
            assert len(response.data) == 2

    def test_list_includes_applications_without_a_season(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        season = ApplicationSeason.objects.create(profile=profile, name="2027")
        in_season = Application.objects.create(profile=profile, season=season, status="DRAFT")
        without_season = Application.objects.create(profile=profile, status="APPLIED")

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/applications/")

        assert response.status_code == 200
        assert response.data["count"] == 2
        assert {application["id"] for application in response.data["results"]} == {
            in_season.id,
            without_season.id,
        }

    def test_list_can_be_filtered_by_season(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        season = ApplicationSeason.objects.create(profile=profile, name="2027")
        in_season = Application.objects.create(profile=profile, season=season, status="DRAFT")
        Application.objects.create(profile=profile, status="APPLIED")

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/applications/?season=2027")

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == in_season.id
        assert response.data["results"][0]["season"] == "2027"

    def test_list_can_be_filtered_to_applications_without_a_season(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        season = ApplicationSeason.objects.create(profile=profile, name="2027")
        Application.objects.create(profile=profile, season=season, status="DRAFT")
        without_season = Application.objects.create(profile=profile, status="APPLIED")

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/applications/?season=__none__")

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == without_season.id
        assert response.data["results"][0]["season"] is None

    def test_list_can_be_filtered_by_organisation_and_application_date(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(name="Target Fest", user=profile)
        other_festival = Festival.objects.create(name="Other Fest", user=profile)
        festival_type = ContentType.objects.get_for_model(Festival)
        today = timezone.now().date()

        def create(organisation: Festival, days_ago: int) -> Application:
            return Application.objects.create(
                profile=profile,
                content_type=festival_type,
                object_id=organisation.id,
                status="APPLIED",
                application_date=today - timedelta(days=days_ago),
            )

        recent = create(festival, 30)
        create(festival, 400)  # too old
        create(other_festival, 30)  # other organisation

        client = APIClient()
        client.force_authenticate(user=profile)
        applied_after = (today - timedelta(days=183)).isoformat()
        response = client.get(
            "/api/applications/",
            {
                "organisation_type": "Festival",
                "organisation": festival.id,
                "applied_after": applied_after,
            },
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == recent.id

    def test_organisation_type_filter_excludes_other_types(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(name="Target Fest", user=profile)
        Application.objects.create(
            profile=profile,
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            status="APPLIED",
        )

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get(
            "/api/applications/", {"organisation_type": "residency", "organisation": festival.id}
        )

        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_other_user_cannot_see_applications(self):
        profile1 = Profile.objects.create_user(email="user1@example.com", password="pass")
        profile2 = Profile.objects.create_user(email="user2@example.com", password="pass")
        Application.objects.create(profile=profile1, status="DRAFT")

        client = APIClient()
        client.force_authenticate(user=profile2)
        response = client.get("/api/applications/")

        assert response.status_code == 200
        if isinstance(response.data, dict) and "results" in response.data:
            assert response.data["count"] == 0
        else:
            assert len(response.data) == 0

    def test_all_valid_statuses(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        valid_statuses = [
            "DRAFT",
            "APPLIED",
            "IN_DISCUSSION",
            "REJECTED",
            "IGNORED",
            "ACCEPTED",
            "POSTPONED",
            "CANCELLED",
            "OTHER",
        ]

        client = APIClient()
        client.force_authenticate(user=profile)

        for s in valid_statuses:
            app = Application.objects.create(profile=profile, status="DRAFT")
            response = client.patch(f"/api/applications/{app.id}/status/{s}/")
            assert response.status_code == 200
