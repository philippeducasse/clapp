from unittest.mock import patch

import pytest
from django.core import mail

from profiles.models import Profile


@pytest.mark.django_db
class TestSendConfirmationEmailSignal:
    """Tests for the send_confirmation_email signal."""

    def test_signal_called_when_profile_created(self):
        """Test that the signal handler is called when a new profile is created."""
        with patch("profiles.signals.send_mail") as mock_send_mail:
            Profile.objects.create_user(email="test@example.com", password="testpassword123")

            mock_send_mail.assert_called_once_with(
                "Welcome! Please confirm your email",
                "CONFIRMATION URL GOES HERE",
                "info@philippeducasse.com",
                ["test@example.com"],
                fail_silently=False,
            )

    def test_send_mail_not_called_on_update(self):
        """Test that send_mail is not called when profile is updated."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpassword123")

        with patch("profiles.signals.send_mail") as mock_send_mail:
            profile.first_name = "John"
            profile.save()

            mock_send_mail.assert_not_called()

    def test_email_sent_to_correct_recipient(self):
        Profile.objects.create_user(email="user1@example.com", password="testpassword123")
        Profile.objects.create_user(email="user2@example.com", password="testpassword123")

        assert len(mail.outbox) == 2

        assert mail.outbox[0].to == ["user1@example.com"]
        assert mail.outbox[1].to == ["user2@example.com"]
