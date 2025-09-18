from django.db import models
from typing import List, Tuple


class Venue(models.Model):
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

    venue_name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    website_url = models.URLField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(max_length=200, blank=True, null=True)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    venue_type = models.CharField(
        max_length=50,
        choices=VENUE_TYPE,
        default="UNKNOWN",
        blank=True,
        null=True,
    )
    contacted = models.BooleanField(default=False)
    comments = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.venue_name
