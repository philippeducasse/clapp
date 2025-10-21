from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from typing import List, Tuple
from profiles.models import Profile
from performances.models import Performance


class Application(models.Model):
    APPLICATION_TYPE: List[Tuple[str, str]] = [
        ("EMAIL", "Email"),
        ("FORM", "Form"),
        ("INVITATION_ONLY", "Invitation only"),
        ("OTHER", "Other"),
        ("UNKNOWN", "Unknown"),
    ]
    APPLICATION_STATUS: List[Tuple[str, str]] = [
        ("DRAFT", "Draft"),
        ("APPLIED", "Applied"),
        ("IN_DISCUSSION", "In discussion"),
        ("REJECTED", "Rejected"),
        ("IGNORED", "Ignored"),
        ("ACCEPTED", "Accepted"),
        ("POSTPONED", "Postponed"),
        ("CANCELLED", "Cancelled"),
        ("OTHER", "Other"),
    ]

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    organisation = GenericForeignKey("content_type", "object_id")
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="applications"
    )
    performances = models.ManyToManyField(
        Performance, related_name="applications", blank=True
    )
    application_date = models.DateField(blank=True, null=True)
    application_method = models.CharField(
        max_length=50,
        choices=APPLICATION_TYPE,
        default="EMAIL",
        blank=True,
    )
    email_subject = models.CharField(max_length=100, blank=True)
    message = models.CharField(max_length=2000, blank=True)
    attachments_sent = models.JSONField(blank=True, null=True)
    attachments_received = models.JSONField(blank=True, null=True)
    answer_received = models.BooleanField(default=False)
    answer_date = models.DateField(blank=True, null=True)
    application_status = models.CharField(
        max_length=50, choices=APPLICATION_STATUS, default="NOT_APPLIED"
    )
    follow_up_date = models.DateField(blank=True, null=True)
    response_details = models.TextField(blank=True)
    performance_details = models.TextField(blank=True)
    contract_received = models.BooleanField(default=False, blank=True, null=True)
    contract_signed = models.BooleanField(default=False, blank=True, null=True)
    payment_received = models.BooleanField(default=False, blank=True, null=True)
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.organisation.name} {self.application_year}"

    @property
    def application_year(self) -> int | None:
        """Derive the festival year based on the application date."""
        if not self.application_date:
            return None

        month = self.application_date.month
        year = self.application_date.year

        if 9 <= month <= 12:
            return year + 1
        else:
            return year
