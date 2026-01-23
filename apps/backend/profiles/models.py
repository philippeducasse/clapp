from typing import Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField

from circus_agent_backend.utils import normalize_url
from profiles.constants import LANGUAGES

EMAIL_HOST_MAPPING = {
    "GMAIL": "smtp.gmail.com",
    "OUTLOOK": "smtp.office365.com",
    "YAHOO": "smtp.mail.yahoo.com",
    "ICLOUD": "smtp.mail.me.com",
    "PROTONMAIL": "smtp.protonmail.ch",
    "ZOHO": "smtp.zoho.com",
    "AOL": "smtp.aol.com",
    "FASTMAIL": "smtp.fastmail.com",
    "GMX": "smtp.gmx.com",
    "WEB.DE": "smtp.web.de",
    "ORANGE": "smtp.orange.fr",
    "FREE": "smtp.free.fr",
    "LIBERO": "smtp.libero.it",
    "MAIL.RU": "smtp.mail.ru",
    "VIRGILIO": "smtp.virgilio.it",
    "T-ONLINE": "securesmtp.t-online.de",
}


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
    company_name = models.CharField(max_length=255, blank=True)
    personal_website = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=255, blank=True)
    instagram_profile = models.URLField(blank=True)
    facebook_profile = models.URLField(blank=True)
    tiktok_profile = models.URLField(blank=True)
    youtube_profile = models.URLField(blank=True)
    phone = PhoneNumberField(blank=True, null=True)
    spoken_languages = MultiSelectField(choices=LANGUAGES, blank=True, max_length=200)
    email_host = models.CharField(max_length=255, blank=True)
    other_email_host = models.CharField(max_length=255, blank=True)
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_password = models.CharField(max_length=255, blank=True)
    email_host_user = models.CharField(max_length=255, blank=True)
    date_format = models.CharField(max_length=50, blank=True, null=True)
    table_size = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = ProfileManager()

    def clean(self) -> None:
        super().clean()
        url_fields = [
            "personal_website",
            "instagram_profile",
            "facebook_profile",
            "tiktok_profile",
            "youtube_profile",
        ]
        for field_name in url_fields:
            url = getattr(self, field_name, "")
            if url:
                setattr(self, field_name, normalize_url(url))

    def __str__(self) -> str:
        return self.email


class EmailTemplate(models.Model):
    name = models.CharField(max_length=255, blank=True)
    content = models.TextField(max_length=10000, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="email_templates")


class Reminder(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    organisation = GenericForeignKey("content_type", "object_id")

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reminders")
    message = models.TextField()
    remind_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["remind_at"]

    def __str__(self):
        return f"Reminder for {self.organisation} at {self.remind_at}"
