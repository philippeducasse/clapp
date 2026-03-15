"""Tests for profiles/oauth_smtp_backend.py."""
import base64
from unittest.mock import MagicMock, patch, call

import pytest

from profiles.oauth_smtp_backend import XOAuth2EmailBackend


class TestXOAuth2EmailBackend:
    def test_init_with_access_token(self):
        backend = XOAuth2EmailBackend(
            host="smtp.gmail.com",
            port=587,
            username="user@gmail.com",
            use_tls=True,
            access_token="my-access-token",
        )
        assert backend.access_token == "my-access-token"

    def test_init_default_access_token(self):
        backend = XOAuth2EmailBackend(
            host="smtp.gmail.com",
            port=587,
            username="user@gmail.com",
            use_tls=True,
        )
        assert backend.access_token == ""

    def test_open_returns_false_if_already_connected(self):
        backend = XOAuth2EmailBackend(
            host="smtp.gmail.com",
            port=587,
            username="user@gmail.com",
            use_tls=True,
            access_token="token",
        )
        backend.connection = MagicMock()  # Already has connection

        result = backend.open()
        assert result is False

    def test_open_creates_xoauth2_connection(self):
        backend = XOAuth2EmailBackend(
            host="smtp.gmail.com",
            port=587,
            username="user@gmail.com",
            use_tls=True,
            access_token="my-token",
        )

        mock_connection = MagicMock()

        with patch("smtplib.SMTP", return_value=mock_connection):
            result = backend.open()

        assert result is True
        assert backend.connection is mock_connection
        mock_connection.ehlo.assert_called()
        mock_connection.starttls.assert_called_once()

        # Verify XOAUTH2 auth string
        expected_auth_str = "user=user@gmail.com\x01auth=Bearer my-token\x01\x01"
        expected_auth_b64 = base64.b64encode(expected_auth_str.encode()).decode()
        mock_connection.docmd.assert_called_once_with("AUTH", f"XOAUTH2 {expected_auth_b64}")

    def test_open_without_tls(self):
        backend = XOAuth2EmailBackend(
            host="smtp.gmail.com",
            port=587,
            username="user@gmail.com",
            use_tls=False,
            access_token="my-token",
        )

        mock_connection = MagicMock()

        with patch("smtplib.SMTP", return_value=mock_connection):
            result = backend.open()

        assert result is True
        mock_connection.starttls.assert_not_called()
