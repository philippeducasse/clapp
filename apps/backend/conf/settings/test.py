"""Test settings that override production settings for pytest"""

from .base import *  # noqa
import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Override database to use in-memory SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/test_db.sqlite3",
        "ATOMIC_REQUESTS": False,
    }
}

# Use Django's in-memory email backend for integration tests
# This allows testing real email sending without mocking
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Celery Configuration for tests - run tasks synchronously (eager mode)
# This allows testing Celery tasks without needing Redis or a worker
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

os.environ["GEMINI_API_KEY"] = "dummy_key_for_testing"
os.environ["MISTRAL_API_KEY"] = "dummy_key_for_testing"

# Never use tenant partitioning in tests
ENVIRONMENT = "test"
SECRET_KEY = "test-secret-key-not-for-production"
