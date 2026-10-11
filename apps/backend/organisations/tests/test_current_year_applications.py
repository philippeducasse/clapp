from datetime import date

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APIClient

from applications.models import Application
from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.views import get_current_application_year_range
from profiles.models import Profile


class TestGetCurrentApplicationYearRange:
    @pytest.mark.parametrize(
        "today, expected",
        [
            (date(2026, 8, 31), (date(2025, 9, 1), date(2026, 8, 31))),
            (date(2026, 9, 1), (date(2026, 9, 1), date(2027, 8, 31))),
            (date(2026, 10, 11), (date(2026, 9, 1), date(2027, 8, 31))),
            (date(2027, 1, 1), (date(2026, 9, 1), date(2027, 8, 31))),
        ],
    )
    def test_boundaries(self, today, expected):
        assert get_current_application_year_range(today) == expected

    def test_defaults_to_today(self, monkeypatch):
        monkeypatch.setattr(timezone, "localdate", lambda: date(2026, 10, 11))
        assert get_current_application_year_range() == (date(2026, 9, 1), date(2027, 8, 31))


def _results(response):
    data = response.data
    return data.get("results", data) if isinstance(data, dict) else data


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model, url",
    [(Festival, "/api/festivals/"), (Residency, "/api/residencies/")],
)
class TestCurrentSeasonApplicationInList:
    @pytest.fixture
    def user(self):
        return Profile.objects.create_user(email="season@example.com", password="testpass")

    @pytest.fixture
    def api_client(self, user, monkeypatch):
        monkeypatch.setattr(timezone, "localdate", lambda: date(2026, 10, 11))
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def _apply(self, org, user, application_date, **kwargs):
        return Application.objects.create(
            content_type=ContentType.objects.get_for_model(type(org)),
            object_id=org.id,
            profile=user,
            application_date=application_date,
            **kwargs,
        )

    def test_returns_latest_application_of_current_season(self, model, url, api_client, user):
        org = model.objects.create(name="Org", user=user)
        self._apply(org, user, date(2025, 10, 1))  # previous season
        self._apply(org, user, date(2026, 9, 15))
        latest = self._apply(org, user, date(2026, 10, 1))

        row = next(r for r in _results(api_client.get(url)) if r["id"] == org.id)

        assert row["has_application_this_year"] is True
        assert row["current_year_application"]["id"] == latest.id

    def test_previous_season_only_is_not_current(self, model, url, api_client, user):
        org = model.objects.create(name="Org", user=user)
        self._apply(org, user, date(2026, 8, 31))

        row = next(r for r in _results(api_client.get(url)) if r["id"] == org.id)

        assert row["has_application_this_year"] is False
        assert not row["current_year_application"].get("id")

    def test_ignores_deleted_and_other_users_applications(self, model, url, api_client, user):
        org = model.objects.create(name="Org", user=user)
        other = Profile.objects.create_user(email="other@example.com", password="testpass")
        self._apply(org, other, date(2026, 10, 1))
        self._apply(org, user, date(2026, 10, 2)).delete()

        row = next(r for r in _results(api_client.get(url)) if r["id"] == org.id)

        assert row["has_application_this_year"] is False
        assert not row["current_year_application"].get("id")
