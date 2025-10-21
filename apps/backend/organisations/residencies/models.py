from django.db import models
from typing import List, Tuple
from organisations.models import Organisation, OrganisationContact


class Residency(Organisation):
    APPLICATION_TYPE: List[Tuple[str, str]] = [
        ("EMAIL", "Email"),
        ("FORM", "Form"),
        ("OPEN_CALL", "Open call"),
        ("INVITATION_ONLY", "Invitation only"),
        ("OTHER", "Other"),
        ("UNKNOWN", "Unknown"),
    ]

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    approximate_date = models.CharField(max_length=100, blank=True)
    application_date_start = models.CharField(max_length=100, blank=True)
    application_date_end = models.CharField(max_length=100, blank=True)
    application_type = models.CharField(
        max_length=50,
        choices=APPLICATION_TYPE,
        default="UNKNOWN",
        blank=True,
    )
    applied = models.BooleanField(default=False)

    class Meta:
        db_table = "residencies_residency"


class ResidencyContact(OrganisationContact):
    residency = models.ForeignKey(
        Residency, on_delete=models.CASCADE, related_name="contacts"
    )

    class Meta:
        db_table = "residencies_residencycontact"
