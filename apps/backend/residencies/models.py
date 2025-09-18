from django.db import models
from typing import List, Tuple


class Residency(models.Model):
    APPLICATION_TYPE: List[Tuple[str, str]] = [
        ("EMAIL", "Email"),
        ("FORM", "Form"),
        ("OPEN_CALL", "Open call"),
        ("INVITATION_ONLY", "Invitation only"),
        ("OTHER", "Other"),
        ("UNKNOWN", "Unknown"),
    ]

    residency_name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    website_url = models.URLField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(max_length=200, blank=True, null=True)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    approximate_date = models.CharField(max_length=100, blank=True, null=True)
    application_date_start = models.CharField(max_length=100, blank=True, null=True)
    application_date_end = models.CharField(max_length=100, blank=True, null=True)
    application_type = models.CharField(
        max_length=50,
        choices=APPLICATION_TYPE,
        default="UNKNOWN",
        blank=True,
        null=True,
    )
    applied = models.BooleanField(default=False)
    comments = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.residency_name
