"""Extended tests for performances/serializers.py."""
import pytest
from django.core.files.base import ContentFile

from performances.models import Dossier, Performance
from performances.serializers import PerformanceSerializer
from profiles.models import Profile


@pytest.mark.django_db
class TestPerformanceSerializerWithDossiers:
    def test_create_with_dossier_files(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")

        dossier_file = ContentFile(b"pdf content", name="test.pdf")

        data = {
            "profile": profile.id,
            "performance_title": "Show With Dossier",
            "short_description": "desc",
            "dossier_files": [dossier_file],
        }

        serializer = PerformanceSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        performance = serializer.save()

        assert performance.dossiers.count() == 1

    def test_update_with_dossier_ids_empty_string(self):
        """dossier_ids=[''] should be converted to [] and all dossiers deleted."""
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        performance = Performance.objects.create(
            profile=profile, performance_title="Show", short_description="desc"
        )
        Dossier.objects.create(
            performance=performance, file=ContentFile(b"pdf", name="test.pdf")
        )

        data = {
            "performance_title": "Updated Show",
            "dossier_ids": [""],
        }
        serializer = PerformanceSerializer(performance, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()

        assert updated.dossiers.count() == 0

    def test_update_with_dossier_ids_keeps_specified(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        performance = Performance.objects.create(
            profile=profile, performance_title="Show", short_description="desc"
        )
        d1 = Dossier.objects.create(
            performance=performance, file=ContentFile(b"pdf1", name="d1.pdf")
        )
        d2 = Dossier.objects.create(
            performance=performance, file=ContentFile(b"pdf2", name="d2.pdf")
        )

        data = {
            "performance_title": "Updated Show",
            "dossier_ids": [d1.id],  # Keep only d1
        }
        serializer = PerformanceSerializer(performance, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()

        assert updated.dossiers.filter(id=d1.id).count() == 1
        assert updated.dossiers.filter(id=d2.id).count() == 0

    def test_update_adds_new_dossier_files(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        performance = Performance.objects.create(
            profile=profile, performance_title="Show", short_description="desc"
        )
        new_file = ContentFile(b"new pdf", name="new.pdf")

        data = {
            "performance_title": "Updated Show",
            "dossier_files": [new_file],
        }
        serializer = PerformanceSerializer(performance, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()

        assert updated.dossiers.count() == 1

    def test_update_with_no_dossier_ids_keeps_all(self):
        """When dossier_ids is None, no dossiers should be deleted."""
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        performance = Performance.objects.create(
            profile=profile, performance_title="Show", short_description="desc"
        )
        Dossier.objects.create(
            performance=performance, file=ContentFile(b"pdf", name="test.pdf")
        )

        data = {"performance_title": "Updated Show"}
        serializer = PerformanceSerializer(performance, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()

        assert updated.dossiers.count() == 1
