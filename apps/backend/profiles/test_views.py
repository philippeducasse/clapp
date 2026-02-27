"""
Tests for password reset endpoints:
  - forgot_password endpoint (profiles/views.py)
  - reset_password endpoint (profiles/views.py)
  - send_forgot_password_email task (profiles/tasks.py)
"""

import pytest
from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from profiles.models import Profile
from profiles.tasks import send_forgot_password_email


RESET_PASSWORD_SETTINGS = {
    "APP_URL": "https://test.clapp.example.com",
    "EMAIL_HOST_USER": "noreply@test.clapp.example.com",
}


@pytest.mark.django_db
class TestForgotPasswordEndpoint:
    """Tests for the forgot_password endpoint (POST /api/profiles/forgot-password/)"""

    FORGOT_PASSWORD_URL = "/api/profiles/forgot-password/"

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_forgot_password_with_valid_email(self, client):
        """Test forgot_password endpoint accepts valid email and triggers task"""
        Profile.objects.create_user(email="user@example.com", password="oldpassword123")
        response = client.post(self.FORGOT_PASSWORD_URL, {"email": "user@example.com"})

        assert response.status_code == status.HTTP_200_OK

    def test_forgot_password_with_nonexistent_email(self, client):
        """Test forgot_password endpoint accepts nonexistent email (doesn't reveal if exists)"""
        response = client.post(self.FORGOT_PASSWORD_URL, {"email": "nonexistent@example.com"})

        # Should still return 200 for security (doesn't reveal if email exists)
        assert response.status_code == status.HTTP_200_OK

    def test_forgot_password_without_email(self, client):
        """Test forgot_password endpoint rejects request without email"""
        response = client.post(self.FORGOT_PASSWORD_URL, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "email required"

    def test_forgot_password_with_empty_email(self, client):
        """Test forgot_password endpoint rejects empty email"""
        response = client.post(self.FORGOT_PASSWORD_URL, {"email": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "email required"

    def test_forgot_password_is_publicly_accessible(self, client):
        """Test endpoint allows unauthenticated access"""
        # APIClient() without force_authenticate is unauthenticated
        response = client.post(self.FORGOT_PASSWORD_URL, {"email": "test@example.com"})

        # Should return 200, not 401/403
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSendForgotPasswordEmailTask:
    """Tests for the send_forgot_password_email Celery task"""

    @pytest.fixture
    def user_without_token(self):
        """Create a user without a reset token"""
        return Profile.objects.create_user(
            email="reset@example.com",
            password="password123",
            first_name="Reset",
        )

    @override_settings(**RESET_PASSWORD_SETTINGS)
    def test_token_is_generated_and_saved(self, user_without_token):
        """Task must generate and save a reset_token to the user"""
        assert not user_without_token.reset_token

        send_forgot_password_email(user_without_token.email)

        user_without_token.refresh_from_db()
        assert user_without_token.reset_token
        assert len(user_without_token.reset_token) > 0

    @override_settings(**RESET_PASSWORD_SETTINGS)
    def test_email_is_sent(self, user_without_token):
        """Task must send exactly one email"""
        mail.outbox.clear()

        send_forgot_password_email(user_without_token.email)

        assert len(mail.outbox) == 1

    @override_settings(**RESET_PASSWORD_SETTINGS)
    def test_email_sent_to_correct_recipient(self, user_without_token):
        """Email must be sent to the user's email address"""
        mail.outbox.clear()

        send_forgot_password_email(user_without_token.email)

        assert mail.outbox[0].to == [user_without_token.email]

    @override_settings(**RESET_PASSWORD_SETTINGS)
    def test_email_subject_is_correct(self, user_without_token):
        """Email subject must match expected text"""
        mail.outbox.clear()

        send_forgot_password_email(user_without_token.email)

        assert mail.outbox[0].subject == "Reset your password"

    @override_settings(**RESET_PASSWORD_SETTINGS)
    def test_email_contains_reset_link(self, user_without_token):
        """Email body must contain the reset URL"""
        mail.outbox.clear()

        send_forgot_password_email(user_without_token.email)

        user_without_token.refresh_from_db()
        expected_url = (
            f"{RESET_PASSWORD_SETTINGS['APP_URL']}/reset-password?"
            f"token={user_without_token.reset_token}"
        )
        assert expected_url in mail.outbox[0].body


@pytest.mark.django_db
class TestResetPasswordEndpoint:
    """Tests for the reset_password endpoint (POST /api/profiles/reset-password/)"""

    RESET_PASSWORD_URL = "/api/profiles/reset-password/"

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def user_with_token(self):
        """Create a user with a reset token"""
        user = Profile.objects.create_user(
            email="reset@example.com",
            password="oldpassword123",
            first_name="Reset",
        )
        user.reset_token = "valid-reset-token-abc123"
        user.save()
        return user

    def test_reset_password_with_valid_token(self, client, user_with_token):
        """Test successful password reset with valid token"""
        response = client.post(
            self.RESET_PASSWORD_URL,
            {
                "token": "valid-reset-token-abc123",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password reset successfully"

    def test_password_is_actually_changed(self, client, user_with_token):
        """Test that password was changed after reset"""
        old_password = "oldpassword123"
        new_password = "newpassword456"

        # Verify old password works before reset
        assert user_with_token.check_password(old_password)

        client.post(
            self.RESET_PASSWORD_URL,
            {
                "token": "valid-reset-token-abc123",
                "new_password": new_password,
            },
        )

        user_with_token.refresh_from_db()
        assert user_with_token.check_password(new_password)
        assert not user_with_token.check_password(old_password)

    def test_reset_token_is_cleared_after_reset(self, client, user_with_token):
        """Test that reset_token is cleared after successful reset"""
        assert user_with_token.reset_token == "valid-reset-token-abc123"

        client.post(
            self.RESET_PASSWORD_URL,
            {
                "token": "valid-reset-token-abc123",
                "new_password": "newpassword456",
            },
        )

        user_with_token.refresh_from_db()
        assert not user_with_token.reset_token

    def test_reset_token_cannot_be_reused(self, client, user_with_token):
        """Test that a reset token can only be used once"""
        token = user_with_token.reset_token

        # First use succeeds
        response1 = client.post(
            self.RESET_PASSWORD_URL,
            {"token": token, "new_password": "newpass1"},
        )
        assert response1.status_code == status.HTTP_200_OK

        # Second use fails because token was cleared
        response2 = client.post(
            self.RESET_PASSWORD_URL,
            {"token": token, "new_password": "newpass2"},
        )
        assert response2.status_code == status.HTTP_404_NOT_FOUND
        assert response2.data["error"] == "User not found"

    def test_reset_password_with_invalid_token(self, client):
        """Test reset_password rejects invalid token"""
        response = client.post(
            self.RESET_PASSWORD_URL,
            {
                "token": "invalid-token-does-not-exist",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"] == "User not found"

    def test_reset_password_without_token(self, client):
        """Test reset_password rejects request without token"""
        response = client.post(
            self.RESET_PASSWORD_URL,
            {"new_password": "newpassword456"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "token and new_password required"

    def test_reset_password_without_new_password(self, client):
        """Test reset_password rejects request without new_password"""
        response = client.post(
            self.RESET_PASSWORD_URL,
            {"token": "some-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "token and new_password required"

    def test_reset_password_with_empty_token(self, client):
        """Test reset_password rejects empty token"""
        response = client.post(
            self.RESET_PASSWORD_URL,
            {
                "token": "",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "token and new_password required"

    def test_reset_password_with_empty_password(self, client):
        """Test reset_password rejects empty new_password"""
        response = client.post(
            self.RESET_PASSWORD_URL,
            {
                "token": "valid-token",
                "new_password": "",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "token and new_password required"

    def test_reset_password_is_publicly_accessible(self, client):
        """Test endpoint allows unauthenticated access"""
        response = client.post(
            self.RESET_PASSWORD_URL,
            {"token": "any-token", "new_password": "any-password"},
        )

        # Should return 404 or 400, not 401/403
        assert response.status_code in [400, 404]

    def test_reset_password_invalid_token_does_not_affect_other_users(self, client):
        """Test that failed reset attempts don't affect other profiles"""
        user = Profile.objects.create_user(
            email="other@example.com",
            password="password123",
        )
        original_password = "password123"

        response = client.post(
            self.RESET_PASSWORD_URL,
            {"token": "wrong-token", "new_password": "newpass"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        user.refresh_from_db()
        assert user.check_password(original_password)
