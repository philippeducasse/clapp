import os

os.environ["GEMINI_API_KEY"] = "dummy_key_for_testing"
os.environ["MISTRAL_API_KEY"] = "dummy_key_for_testing"


# This runs before Django is configured
def pytest_configure(config):
    from django.conf import settings

    # Override the database to use in-memory SQLite for tests
    if hasattr(settings, "DATABASES"):
        settings.DATABASES["default"] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "ATOMIC_REQUESTS": False,
        }
