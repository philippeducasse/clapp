from django.db import models
from typing import List, Tuple


class Performance(models.Model):
    PERFORMANCE_TYPES: List[Tuple[str, str]] = [
        ("STREET", "Street show"),
        ("INDOOR_STAGE", "Indoor stage"),
        ("OUTDOOR", "Outdoor"),
        ("INSTALLATION", "Installation"),
        ("WALK_ACT", "Walk act"),
        ("FIRE_SHOW", "Fire show"),
    ]

    performance_name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=1000, blank=True, null=True)
    trailer = models.URLField(max_length=100, blank=True, null=True)
    length = models.DurationField(blank=True, null=True)
    long_description = models.TextField(max_length=10000, blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    # TODO only for dev, in production should switch to some bucket storage
    dossier = models.FileField(upload_to="pdfs/", blank=True, null=True)
    performance_type = models.CharField(
        max_length=50, choices=PERFORMANCE_TYPES, null=True, blank=True
    )

    def __str__(self):
        return self.performance_name
