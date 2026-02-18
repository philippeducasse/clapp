"""Test settings that override production settings for pytest"""

import os

from .base import *  # noqa

os.environ["SECRET_KEY"] = "test-secret-key-for-ci"
os.environ["ENVIRONMENT"] = "test"
os.environ["EMAIL_BACKEND"] = "django.core.mail.backends.locmem.EmailBackend"
os.environ["APP_EMAIL"] = "test@test.com"
os.environ["MISTRAL_API_KEY"] = "dummy_key_for_testing"


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Override database to use in-memory SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/test_db.sqlite3",  # /tmp is a writable folder
        "ATOMIC_REQUESTS": False,
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Celery Configuration for tests - run tasks synchronously (eager mode)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
ENVIRONMENT = "test"
SECRET_KEY = "test-secret-key-for-ci"

# Email and URL settings for testing
APP_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3020"
APP_EMAIL = "info@test.example.com"
