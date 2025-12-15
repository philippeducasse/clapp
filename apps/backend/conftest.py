import pytest
import os
from django.conf import settings


# Set dummy API keys before any imports
os.environ["GEMINI_API_KEY"] = "dummy_key_for_testing"
os.environ["MISTRAL_API_KEY"] = "dummy_key_for_testing"


@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    }
