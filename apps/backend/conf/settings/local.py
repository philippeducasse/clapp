import os
from pathlib import Path

from .base import *  # noqa

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = True
ENVIRONMENT = "local"

# Disable secure cookie requirements for local HTTP development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# Database - defaults to SQLite for local development
DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")
if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "data" / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.getenv("DB_NAME", "cab"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

# Cache
CACHE_BACKEND = os.getenv("CACHE_BACKEND", "django.core.cache.backends.locmem.LocMemCache")
CACHE_LOCATION = os.getenv("CACHE_LOCATION", "unique-snowflake")

CACHES = {
    "default": {
        "BACKEND": CACHE_BACKEND,
        "LOCATION": CACHE_LOCATION,
        "KEY_PREFIX": "cab",
    }
}

if CACHE_BACKEND == "django_redis.cache.RedisCache":
    CACHES["default"]["OPTIONS"] = {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
    }

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery Configuration
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_TIMEZONE = "UTC"
