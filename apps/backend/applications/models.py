from django.db import models

from festivals.models import Festival
from typing import List, Tuple


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

    festival = models.ForeignKey(Festival, on_delete=models.CASCADE)
    application_date = models.DateField(blank=True, null=True)
    application_method = models.CharField(
        max_length=50,
        choices=APPLICATION_TYPE,
        default="EMAIL",
        blank=True,
        null=True,
    )
    email_subject = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=2000, blank=True, null=True)
    attachments_sent = models.JSONField(blank=True, null=True)
    attachments_received = models.JSONField(blank=True, null=True)
    answer_received = models.BooleanField(default=False)
    answer_date = models.DateField(blank=True, null=True)
    application_status = models.CharField(
        max_length=50, choices=APPLICATION_STATUS, default="NOT_APPLIED"
    )
    follow_up_date = models.DateField(blank=True, null=True)
    response_details = models.TextField(blank=True, null=True)
    performance_details = models.TextField(blank=True, null=True)
    contract_received = models.BooleanField(default=False, blank=True, null=True)
    contract_signed = models.BooleanField(default=False, blank=True, null=True)
    payment_received = models.BooleanField(default=False, blank=True, null=True)
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
