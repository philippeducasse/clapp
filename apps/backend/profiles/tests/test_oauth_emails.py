"""Tests for OAuth email connections in profiles/emails.py."""
from unittest.mock import MagicMock, patch
from datetime import timedelta

import pytest
from django.utils import timezone

from profiles.emails import _gmail_oauth_connection, _outlook_oauth_connection, get_user_email_connection
from profiles.models import Profile


@pytest.mark.django_db
class TestGmailOAuthConnection:
    def test_gmail_oauth_used_when_refresh_token_present(self):
        profile = Profile.objects.create_user(
            email="test@gmail.com",
            password="pass",
            email_host="GMAIL",
            email_host_user="user@gmail.com",
            google_oauth_refresh_token="refresh-token",
            google_oauth_access_token="access-token",
        )

        mock_backend = MagicMock()
        with patch("profiles.emails._gmail_oauth_connection", return_value=mock_backend) as mock_fn:
            connection = get_user_email_connection(profile)
            mock_fn.assert_called_once_with(profile)
        assert connection is mock_backend

    def test_outlook_oauth_used_when_refresh_token_present(self):
        profile = Profile.objects.create_user(
            email="test@outlook.com",
            password="pass",
            email_host="OUTLOOK",
            email_host_user="user@outlook.com",
            outlook_oauth_refresh_token="refresh-token",
            outlook_oauth_access_token="access-token",
        )

        mock_backend = MagicMock()
        with patch("profiles.emails._outlook_oauth_connection", return_value=mock_backend) as mock_fn:
            connection = get_user_email_connection(profile)
            mock_fn.assert_called_once_with(profile)
        assert connection is mock_backend

    def test_gmail_oauth_connection_valid_creds(self):
        profile = Profile.objects.create_user(
            email="test@gmail.com",
            password="pass",
            email_host="GMAIL",
            email_host_user="user@gmail.com",
            google_oauth_refresh_token="refresh-token",
            google_oauth_access_token="valid-access-token",
        )

        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.token = "valid-access-token"

        with patch("profiles.emails.Credentials", return_value=mock_creds), \
             patch("profiles.emails.XOAuth2EmailBackend") as mock_backend_cls:
            mock_backend_cls.return_value = MagicMock()
            connection = _gmail_oauth_connection(profile)

        mock_creds.refresh.assert_not_called()
        assert connection is not None

    def test_gmail_oauth_connection_refreshes_expired_creds(self):
        profile = Profile.objects.create_user(
            email="test@gmail.com",
            password="pass",
            email_host="GMAIL",
            email_host_user="user@gmail.com",
            google_oauth_refresh_token="refresh-token",
            google_oauth_access_token="expired-token",
        )

        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.token = "new-access-token"
        mock_creds.expiry = timezone.now() + timedelta(hours=1)

        with patch("profiles.emails.Credentials", return_value=mock_creds), \
             patch("profiles.emails.Request") as mock_request, \
             patch("profiles.emails.XOAuth2EmailBackend") as mock_backend_cls:
            mock_backend_cls.return_value = MagicMock()
            connection = _gmail_oauth_connection(profile)

        mock_creds.refresh.assert_called_once()
        profile.refresh_from_db()
        assert profile.google_oauth_access_token == "new-access-token"

    def test_outlook_oauth_no_refresh_needed(self):
        future_expiry = timezone.now() + timedelta(hours=1)
        profile = Profile.objects.create_user(
            email="test@outlook.com",
            password="pass",
            email_host="OUTLOOK",
            email_host_user="user@outlook.com",
            outlook_oauth_refresh_token="refresh-token",
            outlook_oauth_access_token="valid-token",
            outlook_oauth_token_expiry=future_expiry,
        )

        mock_app = MagicMock()
        with patch("profiles.emails.msal.ConfidentialClientApplication", return_value=mock_app), \
             patch("profiles.emails.XOAuth2EmailBackend") as mock_backend_cls:
            mock_backend_cls.return_value = MagicMock()
            connection = _outlook_oauth_connection(profile)

        # Token not expired, should not refresh
        mock_app.acquire_token_by_refresh_token.assert_not_called()

    def test_outlook_oauth_refreshes_expired_token(self):
        past_expiry = timezone.now() - timedelta(hours=1)
        profile = Profile.objects.create_user(
            email="test@outlook.com",
            password="pass",
            email_host="OUTLOOK",
            email_host_user="user@outlook.com",
            outlook_oauth_refresh_token="refresh-token",
            outlook_oauth_access_token="expired-token",
            outlook_oauth_token_expiry=past_expiry,
        )

        mock_app = MagicMock()
        mock_app.acquire_token_by_refresh_token.return_value = {
            "access_token": "new-token",
            "expires_in": 3600,
        }

        with patch("profiles.emails.msal.ConfidentialClientApplication", return_value=mock_app), \
             patch("profiles.emails.XOAuth2EmailBackend") as mock_backend_cls:
            mock_backend_cls.return_value = MagicMock()
            connection = _outlook_oauth_connection(profile)

        mock_app.acquire_token_by_refresh_token.assert_called_once()
        profile.refresh_from_db()
        assert profile.outlook_oauth_access_token == "new-token"
