"""Tests for clapp_backend/utils.py."""
import pytest

from clapp_backend.utils import NormalizedURLField, normalize_url


class TestNormalizeUrl:
    def test_empty_string_returns_empty(self):
        assert normalize_url("") == ""

    def test_adds_https_when_no_protocol(self):
        assert normalize_url("example.com") == "https://example.com"

    def test_preserves_https(self):
        assert normalize_url("https://example.com") == "https://example.com"

    def test_preserves_http(self):
        assert normalize_url("http://example.com") == "http://example.com"

    def test_strips_whitespace(self):
        assert normalize_url("  example.com  ") == "https://example.com"

    def test_none_not_passed_but_empty(self):
        # normalize_url is only called with strings
        result = normalize_url("")
        assert result == ""


class TestNormalizedURLField:
    def test_adds_https_to_url_without_protocol(self):
        field = NormalizedURLField(required=False)
        result = field.to_internal_value("example.com")
        assert result == "https://example.com"

    def test_preserves_valid_https_url(self):
        field = NormalizedURLField(required=False)
        result = field.to_internal_value("https://example.com")
        assert result == "https://example.com"

    def test_empty_string_passes_through(self):
        field = NormalizedURLField(required=False, allow_blank=True)
        # Empty string returns empty (no normalization applied)
        result = field.to_internal_value("")
        # DRF URLField with allow_blank=True accepts empty string
        assert result == ""
