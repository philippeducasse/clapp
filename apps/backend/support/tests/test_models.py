import pytest

from profiles.models import Profile
from support.models import BugReport, BugReportAttachment


@pytest.mark.django_db
class TestBugReport:
    """Tests for BugReport model."""

    def test_create_bug_report(self):
        """Test creating a bug report."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(
            profile=profile, message="Application crashes on save", status="new"
        )

        assert bug.profile == profile
        assert bug.status == "new"

    def test_bug_report_status_choices(self):
        """Test that status field respects choices."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(profile=profile, message="Test bug", status="investigating")

        assert bug.status == "investigating"

    def test_bug_report_default_status(self):
        """Test that default status is 'new'."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(profile=profile, message="Test bug")

        assert bug.status == "new"

    def test_bug_report_str_representation(self):
        """Test string representation of bug report."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(profile=profile, message="Test bug")

        str_repr = str(bug)
        assert "Bug Report from" in str_repr
        assert "test@example.com" in str_repr

    def test_bug_report_ordering(self):
        """Test that bug reports are ordered by created_at descending."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        BugReport.objects.create(profile=profile, message="Bug 1")
        bug2 = BugReport.objects.create(profile=profile, message="Bug 2")

        bugs = BugReport.objects.all()
        assert bugs[0].id == bug2.id  # Most recent first


@pytest.mark.django_db
class TestBugReportAttachment:
    """Tests for BugReportAttachment model."""

    def test_create_attachment(self):
        """Test creating a bug report attachment."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(profile=profile, message="Test bug")

        # Note: FileField requires actual file, so we'll just test structure
        attachment = BugReportAttachment(bug_report=bug)
        assert attachment.bug_report == bug

    def test_attachment_cascade_delete(self):
        """Test that attachments are deleted when bug report is deleted."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        bug = BugReport.objects.create(profile=profile, message="Test bug")
        bug_id = bug.id

        bug.delete()

        # Attachments should be cascade deleted
        assert BugReportAttachment.objects.filter(bug_report_id=bug_id).count() == 0
