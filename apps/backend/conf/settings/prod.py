import os
from .base import *  # noqa

# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DEBUG = False

# Production database configuration - all from environment variables
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "cab"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Production cache from environment
CACHE_BACKEND = os.getenv("CACHE_BACKEND", "django_redis.cache.RedisCache")
CACHE_LOCATION = os.getenv("CACHE_LOCATION", "redis://127.0.0.1:6379/0")

CACHES = {
    "default": {
        "BACKEND": CACHE_BACKEND,
        "LOCATION": CACHE_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Production security settings
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() == "true"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True").lower() == "true"
