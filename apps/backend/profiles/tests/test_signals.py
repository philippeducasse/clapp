from unittest.mock import patch

import pytest
from django.core import mail
from django.test import override_settings

from profiles.models import Profile


@pytest.mark.django_db(transaction=True)
class TestSendConfirmationEmailSignal:
    """
    Tests for the send_confirmation_email signal.

    Note: The signal only fires in 'prod' environment by design.
    These tests use @override_settings(ENVIRONMENT="prod") and mock
    the Celery task to test signal behavior without actually sending emails.
    """

    @override_settings(ENVIRONMENT="prod", CELERY_TASK_ALWAYS_EAGER=True)
    def test_signal_called_when_profile_created(self):
        """Test that the signal handler is called when a new profile is created."""
        with patch("profiles.tasks.send_registration_confirmation_email.delay") as mock_task:
            profile = Profile.objects.create_user(
                email="test@example.com", password="testpassword123"
            )

            # Verify the Celery task was called with the profile ID
            mock_task.assert_called_once_with(profile.email)

    @override_settings(ENVIRONMENT="prod", CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_mail_not_called_on_update(self):
        """Test that the signal is not called when profile is updated."""
        with patch("profiles.tasks.send_registration_confirmation_email.delay") as mock_task:
            profile = Profile.objects.create_user(
                email="test@example.com", password="testpassword123"
            )
            # After creation, reset the mock
            mock_task.reset_mock()

            # Update existing profile
            profile.first_name = "John"
            profile.save()

            # Signal should not have been called again
            mock_task.assert_not_called()

    @override_settings(
        ENVIRONMENT="prod",
        CELERY_TASK_ALWAYS_EAGER=True,
        APP_URL="http://test.example.com",
        APP_EMAIL="noreply@test.example.com",
    )
    def test_email_sent_to_correct_recipient(self):
        """Test that confirmation emails are sent to the correct recipients."""
        mail.outbox.clear()

        Profile.objects.create_user(email="user1@example.com", password="testpassword123")
        Profile.objects.create_user(email="user2@example.com", password="testpassword123")

        # In eager mode, the task runs synchronously and sends emails
        assert len(mail.outbox) == 2

        # Verify recipients
        assert mail.outbox[0].to == ["user1@example.com"]
        assert mail.outbox[1].to == ["user2@example.com"]

    @override_settings(ENVIRONMENT="prod", CELERY_TASK_ALWAYS_EAGER=True)
    def test_signal_only_on_creation(self):
        """Test that signal is only triggered on new profile creation."""
        with patch("profiles.tasks.send_registration_confirmation_email.delay") as mock_task:
            # Create a profile - signal should fire
            profile = Profile.objects.create_user(
                email="test@example.com", password="testpassword123"
            )
            initial_count = mock_task.call_count
            assert initial_count == 1

            # Update existing profile - signal should not fire again
            profile.first_name = "Updated"
            profile.save()

            # Count should remain the same
            assert mock_task.call_count == initial_count

    @override_settings(ENVIRONMENT="prod", CELERY_TASK_ALWAYS_EAGER=True)
    def test_signal_passes_correct_db_alias(self):
        """Test that signal passes the profile ID correctly to the task."""
        with patch("profiles.tasks.send_registration_confirmation_email.delay") as mock_task:
            created_profile = Profile.objects.create_user(
                email="test@example.com", password="testpassword123"
            )

            # Verify signal was called with the correct profile ID
            mock_task.assert_called_once_with(created_profile.email)

    @override_settings(ENVIRONMENT="prod", CELERY_TASK_ALWAYS_EAGER=True)
    def test_multiple_profile_creation_triggers_multiple_signals(self):
        """Test that creating multiple profiles triggers multiple signals."""
        with patch("profiles.tasks.send_registration_confirmation_email.delay") as mock_task:
            for i in range(3):
                Profile.objects.create_user(
                    email=f"user{i}@example.com", password="testpassword123"
                )

            assert mock_task.call_count == 3
