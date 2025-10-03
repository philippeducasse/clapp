from django.db import models
from typing import List, Tuple

from django.forms import ValidationError
from profiles.models import Profile
from multiselectfield import MultiSelectField


class Performance(models.Model):
    PERFORMANCE_TYPES: List[Tuple[str, str]] = [
        ("STREET", "Street show"),
        ("INDOOR_STAGE", "Indoor stage"),
        ("OUTDOOR", "Outdoor"),
        ("INSTALLATION", "Installation"),
        ("WALK_ACT", "Walk act"),
        ("FIRE_SHOW", "Fire show"),
    ]
    GENRES: list[tuple[str, str]] = [
        ("CIRCUS", "Circus"),
        ("JUGGLING", "Juggling"),
        ("COMEDY", "Comedy"),
        ("CLOWN", "Clown"),
        ("MIME", "Mime"),
        ("STANDUP", "Stand up"),
        ("PUPPETRY", "Puppetry"),
        ("WALK_ACT", "Walk Act"),
        ("FIRE_SHOW", "Fire Show"),
        ("MUSIC", "Live Music"),
        ("DANCE", "Dance / Physical Theatre"),
        ("THEATRE", "Theatre / Drama"),
        ("MAGIC", "Magic / Illusion"),
        ("INSTALLATION", "Installation / Interactive Art"),
        ("KIDS", "Kids / Family Show"),
        ("MULTIMEDIA", "Multimedia / Projection"),
    ]

    profile = models.ForeignKey(
        Profile,
        related_name="performances",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    performance_title = models.CharField(max_length=200)
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
    genres = MultiSelectField(choices=GENRES, blank=True)

    def __str__(self):
        return self.performance_title


class Dossier(models.Model):
    # Foreign key to link back to your main model
    performance = models.ForeignKey(
        Performance,
        related_name="dossiers",  # Access via yourmodel.dossiers.all()
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to="dossiers/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Optional: add validation to ensure only PDFs
    def clean(self):
        if self.file and not self.file.name.endswith(".pdf"):
            raise ValidationError("Only PDF files are allowed.")

    class Meta:
        ordering = ["-uploaded_at"]
