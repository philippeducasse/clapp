from django.db import models
from festivals.models import Festival
from typing import List, Tuple


class Application(models.Model):
    APPLICATION_TYPE: List[Tuple[str, str]] = [
        ("EMAIL", "Email"),
        ("FORM", "Form"),
        ("OTHER", "Other"),
        ("UNKNOWN", "Unknown"),
    ]

    APPLICATION_STATUS: List[Tuple[str, str]] = [
        ("NOT_APPLIED", "Not applied"),
        ("APPLIED", "Applied"),
        ("IN_DISCUSSION", "In discussion"),
        ("REJECTED", "Rejected"),
        ("IGNORED", "Ignored"),
        ("ACCEPTED", "Accepted"),
        ("POSTPONED", "Postponed"),
        ("Cancelled", "Cancelled"),
        ("OTHER", "Other"),
    ]

    festival: models.ForeignKey = models.ForeignKey(Festival, on_delete=models.CASCADE)
    application_type: models.CharField = models.CharField(
        max_length=50, choices=APPLICATION_TYPE, default="UNKNOWN"
    )
    application_date: models.DateField = models.DateField(blank=True, null=True)
    answer_received: models.BooleanField = models.BooleanField(default=False)
    answer_date: models.DateField = models.DateField(blank=True, null=True)
    application_status: models.CharField = models.CharField(
        max_length=50, choices=APPLICATION_STATUS, default="NOT_APPLIED"
    )
    comments: models.CharField = models.CharField(max_length=500, blank=True, null=True)
