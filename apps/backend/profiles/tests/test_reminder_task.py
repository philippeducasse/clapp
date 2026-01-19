import pytest
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.utils import timezone

from organisations.festivals.models import Festival
from profiles.models import Profile, Reminder
from profiles.tasks import check_and_set_reminders


@pytest.mark.django_db
class TestReminderTask:
    """Test the check_and_set_reminders Celery task."""

    @pytest.fixture
    def profile(self):
        """Create a test profile."""
        return Profile.objects.create_user(email="user@example.com", password="testpass123")

    @pytest.fixture
    def festival(self):
        """Create a test festival."""
        return Festival.objects.create(name="Test Festival", website_url="https://example.com")

    def test_task_sends_single_due_reminder(self, profile, festival):
        """Test that a single due reminder is sent."""
        mail.outbox.clear()  # Clear confirmation email

        reminder = Reminder.objects.create(
            profile=profile,
            message="Don't forget the festival!",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=1),
            is_sent=False,
        )

        result = check_and_set_reminders()

        # Should send 1 email
        assert result == 1
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [profile.email]

        # Reminder should be marked as sent
        reminder.refresh_from_db()
        assert reminder.is_sent is True

    def test_task_sends_multiple_due_reminders(self, profile, festival):
        """Test that multiple due reminders are sent."""
        mail.outbox.clear()  # Clear confirmation email

        reminders = [
            Reminder.objects.create(
                profile=profile,
                message=f"Reminder {i + 1}",
                content_type=ContentType.objects.get_for_model(Festival),
                object_id=festival.id,
                remind_at=timezone.now() - timezone.timedelta(hours=i),
                is_sent=False,
            )
            for i in range(1, 4)
        ]

        result = check_and_set_reminders()

        # Should send 3 emails
        assert result == 3
        assert len(mail.outbox) == 3

        # All reminders should be marked as sent
        for reminder in reminders:
            reminder.refresh_from_db()
            assert reminder.is_sent is True

    def test_task_ignores_future_reminders(self, profile, festival):
        """Test that future reminders are not sent."""
        mail.outbox.clear()  # Clear confirmation email

        Reminder.objects.create(
            profile=profile,
            message="Future reminder",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() + timezone.timedelta(hours=1),
            is_sent=False,
        )

        result = check_and_set_reminders()

        # Should not send any emails
        assert result == 0
        assert len(mail.outbox) == 0

    def test_task_ignores_already_sent_reminders(self, profile, festival):
        """Test that already sent reminders are not resent."""
        mail.outbox.clear()  # Clear confirmation email

        Reminder.objects.create(
            profile=profile,
            message="Already sent",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=1),
            is_sent=True,  # Already marked as sent
        )

        result = check_and_set_reminders()

        # Should not send any emails
        assert result == 0
        assert len(mail.outbox) == 0

    def test_task_only_sends_due_reminders(self, profile, festival):
        """Test that only due reminders are sent, not future ones."""
        mail.outbox.clear()  # Clear confirmation email

        # Create a mix of due, future, and already sent reminders
        Reminder.objects.create(
            profile=profile,
            message="Due reminder",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=1),
            is_sent=False,
        )

        Reminder.objects.create(
            profile=profile,
            message="Future reminder",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() + timezone.timedelta(hours=1),
            is_sent=False,
        )

        Reminder.objects.create(
            profile=profile,
            message="Already sent",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=2),
            is_sent=True,
        )

        result = check_and_set_reminders()

        # Should only send 1 email (the due one)
        assert result == 1
        assert len(mail.outbox) == 1
        assert "Due reminder" in mail.outbox[0].body

    def test_email_contains_correct_information(self, profile, festival):
        """Test that the email contains the correct information."""
        mail.outbox.clear()  # Clear confirmation email

        Reminder.objects.create(
            profile=profile,
            message="Custom reminder message",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=1),
            is_sent=False,
        )

        check_and_set_reminders()

        email = mail.outbox[0]
        assert email.to == [profile.email]
        assert "Custom reminder message" in email.body
        assert festival.name in email.body
        assert festival.website_url in email.body
        assert "Circus Agent" in email.body  # Signature

    def test_task_with_multiple_profiles(self, festival):
        """Test that reminders are sent to correct profiles."""
        profile1 = Profile.objects.create_user(email="user1@example.com", password="pass123")
        profile2 = Profile.objects.create_user(email="user2@example.com", password="pass123")

        mail.outbox.clear()  # Clear confirmation emails

        Reminder.objects.create(
            profile=profile1,
            message="Reminder for user 1",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=1),
            is_sent=False,
        )

        Reminder.objects.create(
            profile=profile2,
            message="Reminder for user 2",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=1),
            is_sent=False,
        )

        result = check_and_set_reminders()

        assert result == 2
        assert len(mail.outbox) == 2

        emails_by_recipient = {email.to[0]: email for email in mail.outbox}
        assert profile1.email in emails_by_recipient
        assert profile2.email in emails_by_recipient
        assert "Reminder for user 1" in emails_by_recipient[profile1.email].body
        assert "Reminder for user 2" in emails_by_recipient[profile2.email].body

    def test_reminder_exactly_at_due_time(self, profile, festival):
        """Test that reminders exactly at the due time are sent."""
        mail.outbox.clear()  # Clear confirmation email

        now = timezone.now()
        Reminder.objects.create(
            profile=profile,
            message="Right on time",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=now,  # Exactly now
            is_sent=False,
        )

        result = check_and_set_reminders()

        assert result == 1
        assert len(mail.outbox) == 1

    def test_task_returns_zero_when_no_reminders(self):
        """Test that task returns 0 when there are no reminders to send."""
        result = check_and_set_reminders()

        assert result == 0
        assert len(mail.outbox) == 0

    def test_task_idempotent_on_second_run(self, profile, festival):
        """Test that running the task twice doesn't send duplicates."""
        mail.outbox.clear()  # Clear confirmation email

        Reminder.objects.create(
            profile=profile,
            message="Test reminder",
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            remind_at=timezone.now() - timezone.timedelta(hours=1),
            is_sent=False,
        )

        # First run
        result1 = check_and_set_reminders()
        assert result1 == 1
        assert len(mail.outbox) == 1

        # Second run
        result2 = check_and_set_reminders()
        assert result2 == 0
        assert len(mail.outbox) == 1  # Still just 1 email
