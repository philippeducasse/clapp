import pytest
from performances.models import Performance, Dossier
from profiles.models import Profile
from django.core.files.base import ContentFile


@pytest.mark.django_db
class TestPerformanceDeleteSignal:
    """Tests for performance deletion signals."""

    def test_dossier_deleted_when_performance_deleted(self):
        """Test that dossiers are cascade deleted when performance is deleted."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile,
            performance_title="Test Performance",
            short_description="A test performance",
        )

        # Create a dossier
        dossier = Dossier.objects.create(
            performance=performance, file=ContentFile(b"pdf content", name="test.pdf")
        )
        dossier_id = dossier.id

        # Delete the performance
        performance.delete()

        # Verify dossier was cascade deleted
        assert not Dossier.objects.filter(id=dossier_id).exists()

    def test_performance_deletion_without_dossiers(self):
        """Test that performance deletion works even without dossiers."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile,
            performance_title="Test Performance",
            short_description="A test performance",
        )
        performance_id = performance.id

        # Delete should not raise error even without dossiers
        performance.delete()

        # Verify performance was deleted
        assert not Performance.objects.filter(id=performance_id).exists()

    def test_multiple_dossiers_cascade_deleted(self):
        """Test that all dossiers are cascade deleted for a performance."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile,
            performance_title="Test Performance",
            short_description="A test performance",
        )

        # Create multiple dossiers
        dossier1 = Dossier.objects.create(
            performance=performance, file=ContentFile(b"pdf content 1", name="test1.pdf")
        )
        dossier2 = Dossier.objects.create(
            performance=performance, file=ContentFile(b"pdf content 2", name="test2.pdf")
        )
        dossier1_id = dossier1.id
        dossier2_id = dossier2.id

        # Delete the performance
        performance.delete()

        # Verify both dossiers were cascade deleted
        assert not Dossier.objects.filter(id=dossier1_id).exists()
        assert not Dossier.objects.filter(id=dossier2_id).exists()

    def test_performance_deletion_does_not_raise_error(self):
        """Test that performance deletion doesn't raise errors."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile,
            performance_title="Test Performance",
            short_description="A test performance",
        )

        # Should not raise any errors
        try:
            performance.delete()
            deleted = True
        except Exception:
            deleted = False

        assert deleted is True
