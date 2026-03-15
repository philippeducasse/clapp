"""Tests for organisations/venues/admin.py."""
from unittest.mock import MagicMock

import pytest

from organisations.venues.admin import SoftDeleteFilter, VenueAdmin
from organisations.venues.models import Venue
from profiles.models import Profile


@pytest.mark.django_db
class TestVenueSoftDeleteFilter:
    def test_lookups(self):
        request = MagicMock()
        model_admin = MagicMock()
        filter_obj = SoftDeleteFilter(request, {}, Venue, model_admin)
        lookups = filter_obj.lookups(request, model_admin)
        assert ("active", "Active only") in lookups
        assert ("deleted", "Deleted only") in lookups

    def test_queryset_active(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        v_active = Venue.objects.create(name="Active", town="London", country="UK", user=profile)
        v_deleted = Venue.objects.create(name="Deleted", town="London", country="UK", user=profile)
        v_deleted.delete()

        request = MagicMock()
        filter_obj = SoftDeleteFilter(request, {"deleted": "active"}, Venue, MagicMock())
        qs = Venue.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 1
        assert result.first().id == v_active.id

    def test_queryset_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Venue.objects.create(name="Active", town="London", country="UK", user=profile)
        v_deleted = Venue.objects.create(name="Deleted", town="London", country="UK", user=profile)
        v_deleted.delete()

        request = MagicMock()
        filter_obj = SoftDeleteFilter(request, {"deleted": "deleted"}, Venue, MagicMock())
        qs = Venue.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 1

    def test_queryset_no_filter(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Venue.objects.create(name="Active", town="London", country="UK", user=profile)
        v = Venue.objects.create(name="Deleted", town="London", country="UK", user=profile)
        v.delete()

        request = MagicMock()
        filter_obj = SoftDeleteFilter(request, {}, Venue, MagicMock())
        qs = Venue.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 2


@pytest.mark.django_db
class TestVenueAdmin:
    def _get_admin(self):
        return VenueAdmin(Venue, MagicMock())

    def test_deleted_status_active(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        venue = Venue.objects.create(name="Active", town="London", country="UK", user=profile)

        admin = self._get_admin()
        html = admin.deleted_status(venue)
        assert "Active" in str(html)

    def test_deleted_status_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        venue = Venue.objects.create(name="Deleted", town="London", country="UK", user=profile)
        venue.delete()
        venue.refresh_from_db()

        admin = self._get_admin()
        html = admin.deleted_status(venue)
        assert "Deleted" in str(html)

    def test_restore_venues_action(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        v1 = Venue.objects.create(name="V1", town="London", country="UK", user=profile)
        v1.delete()

        admin = self._get_admin()
        request = MagicMock()
        queryset = Venue.objects.with_deleted().filter(user=profile)
        admin.restore_venues(request, queryset)
        request.message_user.assert_called_once()

    def test_hard_delete_venues_action(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Venue.objects.create(name="V1", town="London", country="UK", user=profile)

        admin = self._get_admin()
        request = MagicMock()
        queryset = Venue.objects.with_deleted().filter(user=profile)
        admin.hard_delete_venues(request, queryset)

        request.message_user.assert_called_once()
        assert Venue.objects.with_deleted().filter(user=profile).count() == 0

    def test_get_queryset_includes_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        v = Venue.objects.create(name="Test", town="London", country="UK", user=profile)
        v.delete()

        admin = self._get_admin()
        request = MagicMock()
        request.user = profile
        qs = admin.get_queryset(request)
        assert qs.filter(id=v.id).count() == 1
