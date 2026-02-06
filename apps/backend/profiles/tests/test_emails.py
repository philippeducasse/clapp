import pytest
from unittest.mock import patch, MagicMock
from profiles.emails import get_user_email_connection
from profiles.models import Profile


@pytest.mark.django_db
class TestEmailFunctions:
    """Tests for email utility functions."""

    def test_get_user_email_connection_with_known_host(self):
        """Test getting email connection with a known email host."""
        profile = Profile.objects.create_user(
            email="test@example.com",
            password="testpass123",
            email_host="GMAIL",
            email_host_user="user@gmail.com",
            email_host_password="password",
            email_port=587,
            email_use_tls=True,
        )

        with patch("profiles.emails.get_connection") as mock_get_connection:
            mock_get_connection.return_value = MagicMock()
            connection = get_user_email_connection(profile)

            mock_get_connection.assert_called_once()
            # Verify get_connection was called with correct GMAIL SMTP host
            call_args = mock_get_connection.call_args
            assert call_args[1]["host"] == "smtp.gmail.com"
            assert connection is not None

    def test_get_user_email_connection_with_other_host(self):
        """Test getting email connection with OTHER email host."""
        profile = Profile.objects.create_user(
            email="test@example.com",
            password="testpass123",
            email_host="OTHER",
            other_email_host="smtp.custom.com",
            email_host_user="user@custom.com",
            email_host_password="password",
            email_port=587,
            email_use_tls=True,
        )

        with patch("profiles.emails.get_connection") as mock_get_connection:
            mock_get_connection.return_value = MagicMock()
            connection = get_user_email_connection(profile)

            # Verify get_connection was called with custom host
            call_args = mock_get_connection.call_args
            assert call_args[1]["host"] == "smtp.custom.com"
            assert connection is not None

    def test_get_user_email_connection_with_unknown_host_fallback(self):
        """Test that unknown email host uses the email_host value as fallback."""
        profile = Profile.objects.create_user(
            email="test@example.com",
            password="testpass123",
            email_host="CUSTOM_HOST",
            email_host_user="user@example.com",
            email_host_password="password",
            email_port=587,
            email_use_tls=True,
        )

        with patch("profiles.emails.get_connection") as mock_get_connection:
            mock_get_connection.return_value = MagicMock()
            connection = get_user_email_connection(profile)

            # Unknown hosts fall back to the email_host value itself
            call_args = mock_get_connection.call_args
            assert call_args[1]["host"] == "CUSTOM_HOST"
            assert connection is not None

    def test_get_user_email_connection_no_email_host_user(self):
        """Test error when no email_host_user is provided."""
        profile = Profile.objects.create_user(
            email="test@example.com",
            password="testpass123",
            email_host="GMAIL",
            email_host_user="",
            email_host_password="password",
            email_port=587,
            email_use_tls=True,
        )

        with pytest.raises(Exception, match="No email host user found"):
            get_user_email_connection(profile)

    def test_get_user_email_connection_with_custom_other_host_no_smtp(self):
        """Test error when OTHER host selected but no other_email_host provided."""
        profile = Profile.objects.create_user(
            email="test@example.com",
            password="testpass123",
            email_host="OTHER",
            other_email_host="",
            email_host_user="user@custom.com",
            email_host_password="password",
            email_port=587,
            email_use_tls=True,
        )

        with pytest.raises(Exception, match="No smtp host found"):
            get_user_email_connection(profile)

    def test_get_user_email_connection_with_empty_email_host(self):
        """Test error when email_host is empty and OTHER not selected."""
        profile = Profile.objects.create_user(
            email="test@example.com",
            password="testpass123",
            email_host="",
            email_host_user="user@example.com",
            email_host_password="password",
            email_port=587,
            email_use_tls=True,
        )

        with pytest.raises(Exception, match="No smtp host found"):
            get_user_email_connection(profile)
