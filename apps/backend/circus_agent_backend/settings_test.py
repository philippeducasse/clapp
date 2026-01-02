"""Test settings that override production settings for pytest"""

from .settings import *  # noqa
import os

# Override database to use in-memory SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    }
}


os.environ["GEMINI_API_KEY"] = "dummy_key_for_testing"
os.environ["MISTRAL_API_KEY"] = "dummy_key_for_testing"
