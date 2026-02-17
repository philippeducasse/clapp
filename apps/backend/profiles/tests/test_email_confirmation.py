"""
Tests for the email confirmation flow:
  - send_registration_confirmation_email task (profiles/tasks.py)
  - confirm_email view action (profiles/views.py)

Key design decisions:
  - APP_URL and APP_EMAIL are only defined in prod settings, so every test
    that exercises those code paths uses @override_settings to inject them.
  - The signal skips task dispatch in non-prod environments (ENVIRONMENT != "prod"),
    so task tests call the task function directly rather than relying on the signal.
  - The model field `confirmation_token` is CharField(blank=True) without null=True.
    Django will coerce None -> "" when persisting to SQLite, so we assert the
    cleared token is falsy rather than asserting it equals None.
  - The confirm_email view redirects using settings.APP_URL (not FRONTEND_URL).
"""

import pytest
from django.core import mail
from django.test import override_settings
from rest_framework.test import APIClient

from profiles.models import Profile
from profiles.tasks import send_registration_confirmation_email

# ---------------------------------------------------------------------------
# Shared settings override applied to every test in this module.
# ---------------------------------------------------------------------------
CONFIRMATION_SETTINGS = {
    "APP_URL": "https://test.clapp.example.com",
    "APP_EMAIL": "noreply@test.clapp.example.com",
}


# ===========================================================================
# Task tests: send_registration_confirmation_email
# ===========================================================================


@pytest.mark.django_db
class TestSendRegistrationConfirmationEmailTask:
    """Covers the send_registration_confirmation_email Celery task."""

    @pytest.fixture
    def profile(self):
        """A bare profile with no confirmation token set."""
        return Profile.objects.create_user(
            email="artist@example.com",
            password="securepassword123",
        )

    # ------------------------------------------------------------------
    # Token generation and persistence
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_token_is_generated_and_saved_to_user(self, profile):
        """
        Calling the task must populate confirmation_token on the profile
        and persist it to the database.
        """
        assert not profile.confirmation_token  # starts empty

        send_registration_confirmation_email(profile.id)

        profile.refresh_from_db()
        assert profile.confirmation_token
        assert len(profile.confirmation_token) > 0

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_token_is_url_safe(self, profile):
        """
        The generated token must contain only URL-safe characters so it
        can be embedded in a query parameter without percent-encoding.
        """
        send_registration_confirmation_email(profile.id)

        profile.refresh_from_db()
        token = profile.confirmation_token
        # secrets.token_urlsafe produces base64url alphabet: A-Z a-z 0-9 - _
        assert all(
            c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=" for c in token
        )

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_each_call_generates_a_unique_token(self, profile):
        """
        Two consecutive calls must produce different tokens so that old
        confirmation links cannot be reused unintentionally.
        """
        send_registration_confirmation_email(profile.id)
        profile.refresh_from_db()
        first_token = profile.confirmation_token

        send_registration_confirmation_email(profile.id)
        profile.refresh_from_db()
        second_token = profile.confirmation_token

        assert first_token != second_token

    # ------------------------------------------------------------------
    # Email dispatch
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_exactly_one_email_is_sent(self, profile):
        """Task must send exactly one email per invocation."""
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        assert len(mail.outbox) == 1

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_email_is_sent_to_the_correct_recipient(self, profile):
        """The confirmation email must be addressed to the profile's email."""
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        assert mail.outbox[0].to == [profile.email]

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_email_subject_is_correct(self, profile):
        """The email subject must match the expected string."""
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        assert mail.outbox[0].subject == "Welcome to Clapp! Please confirm your email"

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_email_from_address_uses_app_email_setting(self, profile):
        """The from address must be the APP_EMAIL setting, not a hardcoded value."""
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        assert mail.outbox[0].from_email == CONFIRMATION_SETTINGS["APP_EMAIL"]

    # ------------------------------------------------------------------
    # Email body content
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_email_body_contains_users_email(self, profile):
        """The greeting in the email body must contain the user's email address."""
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        assert profile.email in mail.outbox[0].body

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_email_body_contains_confirmation_link(self, profile):
        """
        The body must include the full confirmation URL built from APP_URL
        and the generated token.
        """
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        profile.refresh_from_db()
        expected_url_prefix = (
            f"{CONFIRMATION_SETTINGS['APP_URL']}/api/profiles/confirm-email?token="
            f"{profile.confirmation_token}"
        )
        assert expected_url_prefix in mail.outbox[0].body

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_confirmation_url_uses_app_url_setting(self, profile):
        """
        The confirmation URL must be built from APP_URL so that changing the
        setting changes the link without modifying the task.
        """
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        assert CONFIRMATION_SETTINGS["APP_URL"] in mail.outbox[0].body

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_email_body_contains_clapp_branding(self, profile):
        """Brand elements (welcome text and team signature) must appear in the body."""
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        body = mail.outbox[0].body
        assert "Welcome to Clapp" in body
        assert "Clapp Team" in body

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_email_body_contains_confirm_your_email_anchor_text(self, profile):
        """The call-to-action anchor text must be present in the HTML body."""
        mail.outbox.clear()

        send_registration_confirmation_email(profile.id)

        assert "Confirm Your Email" in mail.outbox[0].body


# ===========================================================================
# View tests: confirm_email action
# ===========================================================================


@pytest.mark.django_db
class TestConfirmEmailView:
    """
    Covers GET /api/profiles/confirm-email/?token=<token>

    The view is an AllowAny action on ProfileViewSet; no authentication needed.
    On success it redirects to APP_URL/email-confirmation?status=success.
    On failure it redirects to APP_URL/email-confirmation?status=error&message=invalid_token.
    """

    CONFIRM_EMAIL_URL = "/api/profiles/confirm-email/"

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def unconfirmed_profile(self):
        """Profile with a preset confirmation token, not yet confirmed."""
        profile = Profile.objects.create_user(
            email="unconfirmed@example.com",
            password="securepassword123",
        )
        profile.confirmation_token = "valid-token-abc123"
        profile.confirmed_account = False
        profile.save()
        return profile

    # ------------------------------------------------------------------
    # Happy path: valid token
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_valid_token_returns_redirect(self, client, unconfirmed_profile):
        """A well-formed request with a valid token must return a redirect (302)."""
        response = client.get(
            self.CONFIRM_EMAIL_URL,
            {"token": unconfirmed_profile.confirmation_token},
        )

        assert response.status_code == 302

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_valid_token_redirects_to_success_url(self, client, unconfirmed_profile):
        """The redirect location must point to the success URL."""
        expected_url = f"{CONFIRMATION_SETTINGS['APP_URL']}/email-confirmation?status=success"

        response = client.get(
            self.CONFIRM_EMAIL_URL,
            {"token": unconfirmed_profile.confirmation_token},
        )

        assert response["Location"] == expected_url

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_valid_token_sets_confirmed_account_to_true(self, client, unconfirmed_profile):
        """After a successful confirmation the profile's confirmed_account flag must be True."""
        client.get(
            self.CONFIRM_EMAIL_URL,
            {"token": unconfirmed_profile.confirmation_token},
        )

        unconfirmed_profile.refresh_from_db()
        assert unconfirmed_profile.confirmed_account is True

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_valid_token_clears_confirmation_token(self, client, unconfirmed_profile):
        """
        After confirmation the token must be cleared so it cannot be reused.
        The model field is CharField(blank=True) without null=True, so the
        view sets it to None but the DB coerces that to an empty string.
        We therefore assert it is falsy rather than asserting it is None.
        """
        client.get(
            self.CONFIRM_EMAIL_URL,
            {"token": unconfirmed_profile.confirmation_token},
        )

        unconfirmed_profile.refresh_from_db()
        assert not unconfirmed_profile.confirmation_token

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_valid_token_is_consumed_and_cannot_be_reused(self, client, unconfirmed_profile):
        """
        Using a token the second time must return an error redirect because
        the token has been cleared from the profile after first use.
        """
        token = unconfirmed_profile.confirmation_token
        expected_error_url = (
            f"{CONFIRMATION_SETTINGS['APP_URL']}"
            "/email-confirmation?status=error&message=invalid_token"
        )

        # First use — should succeed
        client.get(self.CONFIRM_EMAIL_URL, {"token": token})

        # Second use — token is now gone, should error
        response = client.get(self.CONFIRM_EMAIL_URL, {"token": token})

        assert response["Location"] == expected_error_url

    # ------------------------------------------------------------------
    # Error path: missing token
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_missing_token_returns_redirect(self, client):
        """A request with no token parameter must still return a redirect, not a 4xx."""
        response = client.get(self.CONFIRM_EMAIL_URL)

        assert response.status_code == 302

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_missing_token_redirects_to_error_url(self, client):
        """A request with no token must redirect to the invalid-token error URL."""
        expected_url = (
            f"{CONFIRMATION_SETTINGS['APP_URL']}"
            "/email-confirmation?status=error&message=invalid_token"
        )

        response = client.get(self.CONFIRM_EMAIL_URL)

        assert response["Location"] == expected_url

    # ------------------------------------------------------------------
    # Error path: invalid / unknown token
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_invalid_token_returns_redirect(self, client):
        """A request with an unrecognised token must return a redirect."""
        response = client.get(self.CONFIRM_EMAIL_URL, {"token": "does-not-exist"})

        assert response.status_code == 302

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_invalid_token_redirects_to_error_url(self, client):
        """A request with an unrecognised token must redirect to the error URL."""
        expected_url = (
            f"{CONFIRMATION_SETTINGS['APP_URL']}"
            "/email-confirmation?status=error&message=invalid_token"
        )

        response = client.get(self.CONFIRM_EMAIL_URL, {"token": "totally-wrong-token"})

        assert response["Location"] == expected_url

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_invalid_token_does_not_alter_any_profile(self, client, unconfirmed_profile):
        """
        Supplying a bad token must not change the state of any profile in
        the database.
        """
        client.get(self.CONFIRM_EMAIL_URL, {"token": "bad-token"})

        unconfirmed_profile.refresh_from_db()
        assert unconfirmed_profile.confirmed_account is False
        assert unconfirmed_profile.confirmation_token == "valid-token-abc123"

    # ------------------------------------------------------------------
    # Edge case: already-confirmed profile
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_already_confirmed_profile_with_valid_token_succeeds(self, client):
        """
        If a profile was already confirmed but still holds a token
        (e.g. a second link click before the token was cleared), the view
        should still complete the confirmation flow and redirect to success.
        This tests the view's behaviour, not a business-level guard.
        """
        profile = Profile.objects.create_user(
            email="already@example.com",
            password="securepassword123",
        )
        profile.confirmation_token = "already-confirmed-token"
        profile.confirmed_account = True  # already confirmed
        profile.save()

        response = client.get(
            self.CONFIRM_EMAIL_URL,
            {"token": "already-confirmed-token"},
        )

        expected_url = f"{CONFIRMATION_SETTINGS['APP_URL']}/email-confirmation?status=success"
        assert response["Location"] == expected_url

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_confirmed_account_remains_true_after_second_confirmation(self, client):
        """Re-confirming an already-confirmed account must leave the flag as True."""
        profile = Profile.objects.create_user(
            email="double@example.com",
            password="securepassword123",
        )
        profile.confirmation_token = "double-click-token"
        profile.confirmed_account = True
        profile.save()

        client.get(self.CONFIRM_EMAIL_URL, {"token": "double-click-token"})

        profile.refresh_from_db()
        assert profile.confirmed_account is True

    # ------------------------------------------------------------------
    # No authentication required
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_endpoint_is_publicly_accessible_without_authentication(self, unconfirmed_profile):
        """
        The confirm_email action declares AllowAny, so an unauthenticated
        client must be able to use it.
        """
        unauthenticated_client = APIClient()  # no force_authenticate

        response = unauthenticated_client.get(
            self.CONFIRM_EMAIL_URL,
            {"token": unconfirmed_profile.confirmation_token},
        )

        # Either a success or error redirect — not a 401/403
        assert response.status_code == 302
        assert response["Location"] != ""

    # ------------------------------------------------------------------
    # Success URL uses APP_URL setting
    # ------------------------------------------------------------------

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_success_redirect_uses_app_url_setting(self, client, unconfirmed_profile):
        """
        The success redirect must be built from APP_URL so that the setting
        alone controls where users land after confirming.
        """
        response = client.get(
            self.CONFIRM_EMAIL_URL,
            {"token": unconfirmed_profile.confirmation_token},
        )

        assert CONFIRMATION_SETTINGS["APP_URL"] in response["Location"]

    @override_settings(**CONFIRMATION_SETTINGS)
    def test_error_redirect_uses_app_url_setting(self, client):
        """
        The error redirect must also be built from APP_URL, not a hardcoded
        value.
        """
        response = client.get(self.CONFIRM_EMAIL_URL, {"token": "nonexistent"})

        assert CONFIRMATION_SETTINGS["APP_URL"] in response["Location"]
