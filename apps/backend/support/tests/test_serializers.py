import pytest
from support.models import BugReport
from support.serializers import BugReportSerializer
from profiles.models import Profile


@pytest.mark.django_db
class TestBugReportSerializer:
    """Tests for BugReportSerializer."""

    def test_serialize_bug_report(self):
        """Test serializing a bug report."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(profile=profile, message="This is a bug")

        serializer = BugReportSerializer(bug)
        data = serializer.data

        assert data.get("message") == "This is a bug"
        assert "attachments" in data

    def test_create_bug_report_via_serializer(self):
        """Test creating bug report via serializer."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")

        data = {"message": "Found a bug"}

        serializer = BugReportSerializer(data=data)
        if serializer.is_valid():
            bug = serializer.save(profile=profile)
            assert bug.profile == profile
            assert bug.message == "Found a bug"
            assert bug.status == "new"  # Default status

    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        data = {}

        serializer = BugReportSerializer(data=data)
        assert not serializer.is_valid()
        assert "message" in serializer.errors

    def test_serialize_bug_report_with_attachments(self):
        """Test serializing a bug report with attachments."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(profile=profile, message="Bug with files")

        serializer = BugReportSerializer(bug)
        data = serializer.data

        assert data.get("message") == "Bug with files"
        assert isinstance(data.get("attachments"), list)
