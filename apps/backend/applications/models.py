from typing import List, Tuple

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from organisations.models import OrganisationContact
from performances.models import Performance
from profiles.models import Profile


class Application(models.Model):
    APPLICATION_TYPE: List[Tuple[str, str]] = [
        ("EMAIL", "Email"),
        ("FORM", "Form"),
        ("INVITATION", "Invitation"),
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
    # what type of model is this?
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    # which specific instance of the model?
    object_id = models.PositiveIntegerField(null=True, blank=True)
    # combine both
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
    email_recipients = models.JSONField(blank=True)
    message = models.CharField(max_length=10000, blank=True)
    attachments_sent = models.JSONField(blank=True, null=True)
    application_status = models.CharField(
        max_length=50, choices=APPLICATION_STATUS, default="NOT_APPLIED"
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        org_name = self.organisation.name if self.organisation else "No organisation"
        return f"{self.id}:{org_name} {self.application_year}"

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
