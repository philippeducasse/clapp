from django.db import models
from typing import List, Tuple
from organisations.models import Organisation, OrganisationContact


class Venue(Organisation):
    VENUE_TYPE: List[Tuple[str, str]] = [
        ("THEATRE", "Theatre"),
        ("OPERA_HOUSE", "Opera house"),
        ("CONCERT_HALL", "Concert hall"),
        ("DANCE_STUDIO", "Dance studio"),
        ("MUSIC_VENUE", "Music venue"),
        ("CIRCUS_TENT", "Circus tent"),
        ("PERFORMANCE_SPACE", "Performance space"),
        ("ART_GALLERY", "Art gallery"),
        ("OUTDOOR_STAGE", "Outdoor stage"),
        ("PUPPET_THEATRE", "Puppet theatre"),
        ("CIRCUS_SPACE", "Circus space"),
        ("OTHER", "Other"),
        ("UNKNOWN", "Unknown"),
    ]

    venue_type = models.CharField(
        max_length=50,
        choices=VENUE_TYPE,
        default="UNKNOWN",
        blank=True,
    )
    contacted = models.BooleanField(default=False)

    class Meta:
        db_table = "venues_venue"


class VenueContact(OrganisationContact):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="contacts")

    class Meta:
        db_table = "venues_venuecontact"
