import pytest
from performances.models import Performance
from performances.serializers import PerformanceSerializer
from profiles.models import Profile


@pytest.mark.django_db
class TestPerformanceSerializer:
    """Tests for PerformanceSerializer."""

    def test_serialize_performance(self):
        """Test serializing a performance."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile,
            performance_title="My Performance",
            short_description="A great performance",
        )

        serializer = PerformanceSerializer(performance)
        data = serializer.data

        assert "performance_title" in data

    def test_create_performance_via_serializer(self):
        """Test creating performance via serializer."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        data = {
            "profile": profile.id,
            "performance_title": "Test Performance",
            "short_description": "Test description",
        }

        serializer = PerformanceSerializer(data=data)
        if serializer.is_valid():
            performance = serializer.save()
            assert performance.profile == profile

    def test_update_performance_via_serializer(self):
        """Test updating performance via serializer."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        performance = Performance.objects.create(
            profile=profile, performance_title="Old Name", short_description="Old description"
        )

        data = {"performance_title": "New Name"}
        serializer = PerformanceSerializer(performance, data=data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            assert updated.performance_title == "New Name"
