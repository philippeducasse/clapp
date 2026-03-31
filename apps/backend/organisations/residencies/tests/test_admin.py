"""Tests for organisations/residencies/admin.py."""

from unittest.mock import MagicMock

import pytest

from organisations.residencies.admin import ResidencyAdmin, SoftDeleteFilter
from organisations.residencies.models import Residency
from profiles.models import Profile


@pytest.mark.django_db
class TestResidencySoftDeleteFilter:
    def test_lookups(self):
        request = MagicMock()
        model_admin = MagicMock()
        filter_obj = SoftDeleteFilter(request, {}, Residency, model_admin)
        lookups = filter_obj.lookups(request, model_admin)
        assert ("active", "Active only") in lookups
        assert ("deleted", "Deleted only") in lookups

    def test_queryset_active(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        r_active = Residency.objects.create(
            name="Active", town="Berlin", country="DE", user=profile
        )
        r_deleted = Residency.objects.create(
            name="Deleted", town="Berlin", country="DE", user=profile
        )
        r_deleted.delete()

        request = MagicMock()
        request.GET = {"deleted": "active"}
        filter_obj = SoftDeleteFilter(request, {"deleted": "active"}, Residency, MagicMock())
        qs = Residency.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 1
        assert result.first().id == r_active.id

    def test_queryset_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Residency.objects.create(name="Active", town="Berlin", country="DE", user=profile)
        r_deleted = Residency.objects.create(
            name="Deleted", town="Berlin", country="DE", user=profile
        )
        r_deleted.delete()

        request = MagicMock()
        request.GET = {"deleted": "deleted"}
        filter_obj = SoftDeleteFilter(request, {"deleted": "deleted"}, Residency, MagicMock())
        qs = Residency.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 1

    def test_queryset_no_filter(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Residency.objects.create(name="Active", town="Berlin", country="DE", user=profile)
        r = Residency.objects.create(name="Deleted", town="Berlin", country="DE", user=profile)
        r.delete()

        request = MagicMock()
        filter_obj = SoftDeleteFilter(request, {}, Residency, MagicMock())
        qs = Residency.objects.with_deleted().filter(user=profile)
        result = filter_obj.queryset(request, qs)
        assert result.count() == 2


@pytest.mark.django_db
class TestResidencyAdmin:
    def _get_admin(self):
        return ResidencyAdmin(Residency, MagicMock())

    def test_deleted_status_active(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        residency = Residency.objects.create(
            name="Active", town="Berlin", country="DE", user=profile
        )

        admin = self._get_admin()
        html = admin.deleted_status(residency)
        assert "Active" in str(html)

    def test_deleted_status_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        residency = Residency.objects.create(
            name="Deleted", town="Berlin", country="DE", user=profile
        )
        residency.delete()
        residency.refresh_from_db()

        admin = self._get_admin()
        html = admin.deleted_status(residency)
        assert "Deleted" in str(html)

    def test_restore_residencies_action(self):
        from unittest.mock import patch

        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        r1 = Residency.objects.create(name="R1", town="Berlin", country="DE", user=profile)
        r1.delete()

        admin = self._get_admin()
        request = MagicMock()
        queryset = Residency.objects.with_deleted().filter(user=profile)

        with patch.object(admin, "message_user") as mock_message:
            admin.restore_residencies(request, queryset)
            mock_message.assert_called_once()

    def test_hard_delete_residencies_action(self):
        from unittest.mock import patch

        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Residency.objects.create(name="R1", town="Berlin", country="DE", user=profile)

        admin = self._get_admin()
        request = MagicMock()
        queryset = Residency.objects.with_deleted().filter(user=profile)

        with patch.object(admin, "message_user") as mock_message:
            admin.hard_delete_residencies(request, queryset)
            mock_message.assert_called_once()
            assert Residency.objects.with_deleted().filter(user=profile).count() == 0

    def test_get_queryset_includes_deleted(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        r = Residency.objects.create(name="Test", town="Berlin", country="DE", user=profile)
        r.delete()

        admin = self._get_admin()
        request = MagicMock()
        request.user = profile
        qs = admin.get_queryset(request)
        assert qs.filter(id=r.id).count() == 1
