from django.db import models
from typing import List, Tuple
from organisations.models import Organisation, OrganisationContact


class Festival(Organisation):
    FESTIVAL_TYPES: List[Tuple[str, str]] = [
        ("STREET", "Street"),
        ("PUPPET", "Puppet"),
        ("JUGGLING_CONVENTION", "Juggling convention"),
        ("CIRCUS", "Circus"),
        ("MUSIC", "Music"),
        ("THEATRE", "Theatre"),
        ("DANCE", "Dance"),
        ("OTHER", "Other"),
    ]

    APPLICATION_TYPE: List[Tuple[str, str]] = [
        ("EMAIL", "Email"),
        ("FORM", "Form"),
        ("INVITATION_ONLY", "Invitation only"),
        ("OTHER", "Other"),
        ("UNKNOWN", "Unknown"),
    ]

    festival_type = models.CharField(
        max_length=50, choices=FESTIVAL_TYPES, default="STREET", blank=True
    )

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
    estimated_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Best estimate of start date for sorting. Use start_date if known, otherwise estimate from approximate_date",
    )

    class Meta:
        db_table = "festivals_festival"


class FestivalContact(OrganisationContact):
    festival = models.ForeignKey(
        Festival, on_delete=models.CASCADE, related_name="contacts"
    )

    class Meta:
        db_table = "festivals_festivalcontact"
