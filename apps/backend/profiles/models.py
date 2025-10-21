from django.db import models
from typing import Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField


class ProfileManager(BaseUserManager["Profile"]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "Profile":
        if not email:
            raise ValueError("Users must provide an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "Profile":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Profile(AbstractUser):
    username = None  # remove username field
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    artist_name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    personal_website = models.URLField(blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=255, blank=True)
    instagram_profile = models.URLField(blank=True)
    facebook_profile = models.URLField(blank=True)
    tiktok_profile = models.URLField(blank=True)
    youtube_profile = models.URLField(blank=True)
    phone = PhoneNumberField(blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = ProfileManager()

    def __str__(self) -> str:
        return self.email
