from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.core import signing
from rest_framework.test import APIClient

from profiles.models import Profile


@pytest.mark.django_db
class TestOAuthDisconnect:
    def setup_method(self):
        self.profile = Profile.objects.create_user(email="test@example.com", password="pass123")
        self.profile.google_oauth_refresh_token = "refresh_token"
        self.profile.google_oauth_access_token = "access_token"
        self.profile.google_oauth_token_expiry = datetime.now(tz=timezone.utc)
        self.profile.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile)

    def test_clears_all_oauth_tokens_and_host(self):
        self.profile.email_host = "GMAIL"
        self.profile.email_host_user = "test@gmail.com"
        self.profile.save()

        response = self.client.post("/api/profiles/oauth/disconnect/")

        assert response.status_code == 200
        self.profile.refresh_from_db()
        assert self.profile.google_oauth_refresh_token == ""
        assert self.profile.google_oauth_access_token == ""
        assert self.profile.google_oauth_token_expiry is None
        assert self.profile.outlook_oauth_refresh_token == ""
        assert self.profile.outlook_oauth_access_token == ""
        assert self.profile.outlook_oauth_token_expiry is None
        assert self.profile.email_host == ""
        assert self.profile.email_host_user == ""

    def test_unauthenticated_rejected(self):
        response = APIClient().post("/api/profiles/oauth/disconnect/")

        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestGmailConnect:
    def setup_method(self):
        self.profile = Profile.objects.create_user(email="test@example.com", password="pass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile)

    @patch("profiles.oauth_views.Flow")
    def test_returns_auth_url(self, mock_flow_class):
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = ("https://accounts.google.com/auth?foo=bar", "state")
        mock_flow_class.from_client_config.return_value = mock_flow

        response = self.client.get("/api/profiles/oauth/gmail/connect/")

        assert response.status_code == 200
        assert "auth_url" in response.data
        assert response.data["auth_url"] == "https://accounts.google.com/auth?foo=bar"

    @patch("profiles.oauth_views.Flow")
    def test_unauthenticated_rejected(self, mock_flow_class):
        unauthenticated_client = APIClient()

        response = unauthenticated_client.get("/api/profiles/oauth/gmail/connect/")

        assert response.status_code in [401, 403]

    @patch("profiles.oauth_views.Flow")
    def test_flow_configured_with_gmail_scopes(self, mock_flow_class):
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = ("https://auth_url", "_")
        mock_flow_class.from_client_config.return_value = mock_flow

        self.client.get("/api/profiles/oauth/gmail/connect/")

        call_kwargs = mock_flow_class.from_client_config.call_args
        assert call_kwargs[1]["scopes"] == ["https://mail.google.com/"]


@pytest.mark.django_db
class TestGmailCallback:
    def setup_method(self):
        self.profile = Profile.objects.create_user(email="test@example.com", password="pass123")
        self.client = APIClient()
        self.state = signing.dumps({"uid": self.profile.pk})

    @patch("profiles.oauth_views.Flow")
    def test_saves_tokens_and_redirects_on_success(self, mock_flow_class):
        mock_creds = MagicMock()
        mock_creds.refresh_token = "refresh_token_123"
        mock_creds.token = "access_token_123"
        mock_creds.expiry = datetime.now() + timedelta(hours=1)
        mock_flow = MagicMock()
        mock_flow.credentials = mock_creds
        mock_flow_class.from_client_config.return_value = mock_flow

        response = self.client.get(
            "/api/profiles/oauth/gmail/callback/",
            {"state": self.state, "code": "auth_code_123"},
        )

        assert response.status_code == 302
        assert "status=success" in response["Location"]
        assert "gmail" in response["Location"]

        self.profile.refresh_from_db()
        assert self.profile.google_oauth_refresh_token == "refresh_token_123"
        assert self.profile.google_oauth_access_token == "access_token_123"
        assert self.profile.email_host == "GMAIL"
        assert self.profile.email_host_user == self.profile.email

    @patch("profiles.oauth_views.Flow")
    def test_clears_outlook_tokens_on_connect(self, mock_flow_class):
        self.profile.outlook_oauth_refresh_token = "old_outlook_refresh"
        self.profile.outlook_oauth_access_token = "old_outlook_access"
        self.profile.outlook_oauth_token_expiry = datetime.now(tz=timezone.utc)
        self.profile.save()

        mock_creds = MagicMock()
        mock_creds.refresh_token = "new_gmail_refresh"
        mock_creds.token = "new_gmail_access"
        mock_creds.expiry = datetime.now() + timedelta(hours=1)
        mock_flow = MagicMock()
        mock_flow.credentials = mock_creds
        mock_flow_class.from_client_config.return_value = mock_flow

        self.client.get(
            "/api/profiles/oauth/gmail/callback/",
            {"state": self.state, "code": "auth_code_123"},
        )

        self.profile.refresh_from_db()
        assert self.profile.outlook_oauth_refresh_token == ""
        assert self.profile.outlook_oauth_access_token == ""
        assert self.profile.outlook_oauth_token_expiry is None

    @patch("profiles.oauth_views.Flow")
    def test_redirects_on_invalid_state(self, mock_flow_class):
        response = self.client.get(
            "/api/profiles/oauth/gmail/callback/",
            {"state": "invalid_state", "code": "auth_code_123"},
        )

        assert response.status_code == 302
        assert "status=error" in response["Location"]
        assert "gmail" in response["Location"]

    @patch("profiles.oauth_views.Flow")
    def test_redirects_on_token_exchange_failure(self, mock_flow_class):
        mock_flow = MagicMock()
        mock_flow.fetch_token.side_effect = Exception("Token exchange failed")
        mock_flow_class.from_client_config.return_value = mock_flow

        response = self.client.get(
            "/api/profiles/oauth/gmail/callback/",
            {"state": self.state, "code": "bad_code"},
        )

        assert response.status_code == 302
        assert "status=error" in response["Location"]

    @patch("profiles.oauth_views.Flow")
    def test_redirects_when_user_not_found(self, mock_flow_class):
        state = signing.dumps({"uid": 99999})

        response = self.client.get(
            "/api/profiles/oauth/gmail/callback/",
            {"state": state, "code": "auth_code_123"},
        )

        assert response.status_code == 302
        assert "status=error" in response["Location"]


@pytest.mark.django_db
class TestOutlookConnect:
    def setup_method(self):
        self.profile = Profile.objects.create_user(email="test@example.com", password="pass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile)

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_returns_auth_url(self, mock_msal_class):
        mock_app = MagicMock()
        mock_app.get_authorization_request_url.return_value = "https://login.microsoftonline.com/auth?foo=bar"
        mock_msal_class.return_value = mock_app

        response = self.client.get("/api/profiles/oauth/outlook/connect/")

        assert response.status_code == 200
        assert "auth_url" in response.data
        assert response.data["auth_url"] == "https://login.microsoftonline.com/auth?foo=bar"

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_unauthenticated_rejected(self, mock_msal_class):
        unauthenticated_client = APIClient()

        response = unauthenticated_client.get("/api/profiles/oauth/outlook/connect/")

        assert response.status_code in [401, 403]

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_flow_configured_with_outlook_scopes(self, mock_msal_class):
        mock_app = MagicMock()
        mock_app.get_authorization_request_url.return_value = "https://auth_url"
        mock_msal_class.return_value = mock_app

        self.client.get("/api/profiles/oauth/outlook/connect/")

        call_kwargs = mock_app.get_authorization_request_url.call_args
        assert call_kwargs[1]["scopes"] == ["https://outlook.office.com/SMTP.Send"]


@pytest.mark.django_db
class TestOutlookCallback:
    def setup_method(self):
        self.profile = Profile.objects.create_user(email="test@example.com", password="pass123")
        self.client = APIClient()
        self.state = signing.dumps({"uid": self.profile.pk})

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_saves_tokens_and_redirects_on_success(self, mock_msal_class):
        mock_app = MagicMock()
        mock_app.acquire_token_by_authorization_code.return_value = {
            "access_token": "access_token_456",
            "refresh_token": "refresh_token_456",
            "expires_in": 3600,
        }
        mock_msal_class.return_value = mock_app

        response = self.client.get(
            "/api/profiles/oauth/outlook/callback/",
            {"state": self.state, "code": "auth_code_456"},
        )

        assert response.status_code == 302
        assert "status=success" in response["Location"]
        assert "outlook" in response["Location"]

        self.profile.refresh_from_db()
        assert self.profile.outlook_oauth_refresh_token == "refresh_token_456"
        assert self.profile.outlook_oauth_access_token == "access_token_456"
        assert self.profile.email_host == "OUTLOOK"
        assert self.profile.email_host_user == self.profile.email

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_clears_gmail_tokens_on_connect(self, mock_msal_class):
        self.profile.google_oauth_refresh_token = "old_gmail_refresh"
        self.profile.google_oauth_access_token = "old_gmail_access"
        self.profile.google_oauth_token_expiry = datetime.now(tz=timezone.utc)
        self.profile.save()

        mock_app = MagicMock()
        mock_app.acquire_token_by_authorization_code.return_value = {
            "access_token": "new_outlook_access",
            "refresh_token": "new_outlook_refresh",
            "expires_in": 3600,
        }
        mock_msal_class.return_value = mock_app

        self.client.get(
            "/api/profiles/oauth/outlook/callback/",
            {"state": self.state, "code": "auth_code_456"},
        )

        self.profile.refresh_from_db()
        assert self.profile.google_oauth_refresh_token == ""
        assert self.profile.google_oauth_access_token == ""
        assert self.profile.google_oauth_token_expiry is None

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_redirects_on_invalid_state(self, mock_msal_class):
        response = self.client.get(
            "/api/profiles/oauth/outlook/callback/",
            {"state": "invalid_state", "code": "auth_code_456"},
        )

        assert response.status_code == 302
        assert "status=error" in response["Location"]
        assert "outlook" in response["Location"]

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_redirects_on_api_error(self, mock_msal_class):
        mock_app = MagicMock()
        mock_app.acquire_token_by_authorization_code.return_value = {
            "error": "invalid_grant",
            "error_description": "The code has expired.",
        }
        mock_msal_class.return_value = mock_app

        response = self.client.get(
            "/api/profiles/oauth/outlook/callback/",
            {"state": self.state, "code": "bad_code"},
        )

        assert response.status_code == 302
        assert "status=error" in response["Location"]

    @patch("profiles.oauth_views.msal.ConfidentialClientApplication")
    def test_redirects_when_user_not_found(self, mock_msal_class):
        state = signing.dumps({"uid": 99999})

        response = self.client.get(
            "/api/profiles/oauth/outlook/callback/",
            {"state": state, "code": "auth_code_456"},
        )

        assert response.status_code == 302
        assert "status=error" in response["Location"]