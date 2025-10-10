import pytest
from datetime import date, timedelta
from performances.models import Performance, Dossier
from profiles.models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ValidationError
from django.core.files.storage import default_storage


@pytest.mark.django_db
class TestPerformanceModel:
    """Basic tests for the Performance model"""

    @pytest.fixture
    def profile(self):
        return Profile.objects.create_user(
            email="performer@example.com",
            password="testpass123"
        )

    def test_performance_creation(self, profile):
        """Test creating a performance with required fields"""
        performance = Performance.objects.create(
            performance_title="Amazing Show",
            profile=profile
        )

        assert performance.id is not None
        assert performance.performance_title == "Amazing Show"
        assert performance.profile == profile

    def test_performance_string_representation(self, profile):
        """Test the __str__ method"""
        performance = Performance.objects.create(
            performance_title="My Performance",
            profile=profile
        )

        assert str(performance) == "My Performance"

    def test_performance_with_all_fields(self, profile):
        """Test creating a performance with all fields"""
        performance = Performance.objects.create(
            performance_title="Complete Show",
            profile=profile,
            short_description="A short description",
            trailer="https://youtube.com/watch?v=test",
            length=timedelta(minutes=45),
            long_description="A very long description",
            creation_date=date(2024, 1, 1),
            performance_type="STREET"
        )

        assert performance.short_description == "A short description"
        assert performance.trailer == "https://youtube.com/watch?v=test"
        assert performance.length == timedelta(minutes=45)
        assert performance.performance_type == "STREET"

    def test_performance_type_choices(self, profile):
        """Test valid performance type choices"""
        types = ["STREET", "INDOOR_STAGE", "OUTDOOR", "INSTALLATION", "WALK_ACT", "FIRE_SHOW"]

        for perf_type in types:
            performance = Performance.objects.create(
                performance_title=f"Show {perf_type}",
                profile=profile,
                performance_type=perf_type
            )
            assert performance.performance_type == perf_type

    def test_performance_optional_fields_null(self, profile):
        """Test that optional fields can be null"""
        performance = Performance.objects.create(
            performance_title="Minimal Show",
            profile=profile
        )

        assert performance.short_description is None
        assert performance.trailer is None
        assert performance.length is None
        assert performance.creation_date is None

    def test_performance_genres_multiselect(self, profile):
        """Test multi-select genres field"""
        performance = Performance.objects.create(
            performance_title="Multi-Genre Show",
            profile=profile,
            genres=["CIRCUS", "JUGGLING", "COMEDY"]
        )

        assert "CIRCUS" in performance.genres
        assert "JUGGLING" in performance.genres
        assert "COMEDY" in performance.genres


@pytest.mark.django_db
class TestDossierModel:
    """Basic tests for the Dossier model"""

    @pytest.fixture
    def profile(self):
        return Profile.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    @pytest.fixture
    def performance(self, profile):
        return Performance.objects.create(
            performance_title="Test Performance",
            profile=profile
        )

    def test_dossier_creation(self, performance):
        """Test creating a dossier"""
        pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        dossier = Dossier.objects.create(
            performance=performance,
            file=pdf_file
        )

        try:
            assert dossier.id is not None
            assert dossier.performance == performance
            assert dossier.uploaded_at is not None
        finally:
            # Clean up the uploaded file
            if dossier.file:
                default_storage.delete(dossier.file.name)

    def test_dossier_ordering(self, performance):
        """Test that dossiers are ordered by uploaded_at descending"""
        pdf1 = SimpleUploadedFile("test1.pdf", b"content1", content_type="application/pdf")
        pdf2 = SimpleUploadedFile("test2.pdf", b"content2", content_type="application/pdf")

        dossier1 = Dossier.objects.create(performance=performance, file=pdf1)
        dossier2 = Dossier.objects.create(performance=performance, file=pdf2)

        try:
            dossiers = Dossier.objects.all()
            assert dossiers[0] == dossier2  # Most recent first
            assert dossiers[1] == dossier1
        finally:
            # Clean up the uploaded files
            if dossier1.file:
                default_storage.delete(dossier1.file.name)
            if dossier2.file:
                default_storage.delete(dossier2.file.name)
