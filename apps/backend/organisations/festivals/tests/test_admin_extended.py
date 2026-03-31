"""Tests for organisations/festivals/admin.py."""

from unittest.mock import MagicMock

import pytest

from organisations.festivals.admin import FestivalAdmin, SoftDeleteFilter
from organisations.festivals.models import Festival
from profiles.models import Profile


@pytest.mark.django_db
class TestSoftDeleteFilter:
    def test_lookups(self):
        request = MagicMock()
        model_admin = MagicMock()
        filter_obj = SoftDeleteFilter(request, {}, Festival, model_admin)
        lookups = filter_obj.lookups(request, model_admin)
        assert ("active", "Active only") in lookups
        assert ("deleted", "Deleted only") in lookups

    def test_queryset_active(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        f_active = Festival.objects.create(name="Active", town="Paris", country="FR", user=profile)
        f_deleted = Festival.objects.create(
            name="Deleted", town="Paris", country="FR", user=profile
        )
        f_deleted.delete()

        request = MagicMock()
        request.GET = {"deleted": "active"}
        filter_obj = SoftDeleteFilter(request, {"deleted": "active"}, Festival, MagicMock())
        qs = Festival.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 1
        assert result.first().id == f_active.id

    def test_queryset_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Festival.objects.create(name="Active", town="Paris", country="FR", user=profile)
        f_deleted = Festival.objects.create(
            name="Deleted", town="Paris", country="FR", user=profile
        )
        f_deleted.delete()

        request = MagicMock()
        request.GET = {"deleted": "deleted"}
        filter_obj = SoftDeleteFilter(request, {"deleted": "deleted"}, Festival, MagicMock())
        qs = Festival.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 1
        assert result.first().id == f_deleted.id

    def test_queryset_no_filter(self):
        """When no filter value, returns all."""
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Festival.objects.create(name="Active", town="Paris", country="FR", user=profile)
        f_deleted = Festival.objects.create(
            name="Deleted", town="Paris", country="FR", user=profile
        )
        f_deleted.delete()

        request = MagicMock()
        filter_obj = SoftDeleteFilter(request, {}, Festival, MagicMock())
        qs = Festival.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 2


@pytest.mark.django_db
class TestFestivalAdmin:
    def _get_admin(self):
        return FestivalAdmin(Festival, MagicMock())

    def test_deleted_status_active(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(name="Active", town="Paris", country="FR", user=profile)

        admin = self._get_admin()
        html = admin.deleted_status(festival)
        assert "Active" in str(html)

    def test_deleted_status_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(name="Deleted", town="Paris", country="FR", user=profile)
        festival.delete()
        festival.refresh_from_db()

        admin = self._get_admin()
        html = admin.deleted_status(festival)
        assert "Deleted" in str(html)

    def test_restore_festivals_action(self):
        from unittest.mock import patch

        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        f1 = Festival.objects.create(name="F1", town="Paris", country="FR", user=profile)
        f2 = Festival.objects.create(name="F2", town="Paris", country="FR", user=profile)
        f1.delete()
        f2.delete()

        admin = self._get_admin()
        request = MagicMock()
        queryset = Festival.objects.with_deleted().filter(user=profile)

        with patch.object(admin, "message_user") as mock_message:
            admin.restore_festivals(request, queryset)
            mock_message.assert_called_once()
            call_args = str(mock_message.call_args)
            assert "2" in call_args

    def test_hard_delete_festivals_action(self):
        from unittest.mock import patch

        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Festival.objects.create(name="F1", town="Paris", country="FR", user=profile)
        Festival.objects.create(name="F2", town="Paris", country="FR", user=profile)

        admin = self._get_admin()
        request = MagicMock()
        queryset = Festival.objects.with_deleted().filter(user=profile)

        with patch.object(admin, "message_user") as mock_message:
            admin.hard_delete_festivals(request, queryset)
            mock_message.assert_called_once()
        assert Festival.objects.with_deleted().filter(user=profile).count() == 0

    def test_get_queryset_includes_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        f = Festival.objects.create(name="Test", town="Paris", country="FR", user=profile)
        f.delete()

        admin = self._get_admin()
        request = MagicMock()
        request.user = profile
        qs = admin.get_queryset(request)
        assert qs.filter(id=f.id).count() == 1
