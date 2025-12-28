from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from typing import List, Tuple
from circus_agent_backend.utils import normalize_url


class Organisation(models.Model):
    TAGS: List[Tuple[str, str]] = [
        ("STAR", "Star"),
        ("WARNING", "Warning"),
        ("INACTIVE", "Inactive"),
        ("WATCH", "Watch"),
        ("OTHER", "Other"),
    ]
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True)
    country = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    website_url = models.URLField(max_length=200, blank=True)
    comments = models.TextField(max_length=500, blank=True)
    tag = models.CharField(max_length=20, choices=TAGS, blank=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def clean(self) -> None:
        super().clean()
        if self.website_url:
            self.website_url = normalize_url(self.website_url)

    def __str__(self) -> str:
        return self.name


class OrganisationContact(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    role = models.CharField(max_length=100, blank=True)
    phone = PhoneNumberField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.name} - {self.email}"
