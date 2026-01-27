"""Generic utility functions for the circus agent backend."""

from rest_framework import serializers


def normalize_url(url: str) -> str:
    """
    Normalize a URL by adding https:// if no protocol is present.

    Args:
        url: The URL to normalize

    Returns:
        The normalized URL with protocol, or empty string if input is empty
    """
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


class NormalizedURLField(serializers.URLField):
    """URLField that automatically adds https:// if no protocol is present."""

    def to_internal_value(self, data):
        if data:
            data = normalize_url(data)
        return super().to_internal_value(data)
