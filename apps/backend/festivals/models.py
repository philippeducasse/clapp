from django.db import models


class Festival(models.Model):
    FESTIVAL_TYPES = [
        ("STREET", "Street"),
        ("PUPPET", "Puppet"),
        ("JUGGLING_CONVENTION", "Juggling convention"),
        ("CIRCUS", "Circus"),
        ("MUSIC", "Music"),
        ("THEATRE", "Theatre"),
        ("DANCE", "Dance"),
        ("OTHER", "Other"),
    ]

    APPLICATION_TYPE = [
        ("EMAIL", "Email"),
        ("FORM", "Form"),
        ("OTHER", "Other"),
        ("UNKNOWN", "Unknown"),
    ]

    festival_name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    festival_type = models.CharField(
        max_length=50, choices=FESTIVAL_TYPES, default="STREET"
    )
    website_url = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.CharField(max_length=200, blank=True, null=True)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    approximate_date = models.CharField(max_length=100, blank=True, null=True)
    application_date_start = models.CharField(max_length=100, blank=True, null=True)
    application_date_end = models.CharField(max_length=100, blank=True, null=True)
    application_type = models.CharField(
        max_length=50, choices=APPLICATION_TYPE, default="UNKNOWN"
    )
    applied = models.BooleanField(default=False)
    comments = models.CharField(max_length=500, blank=True, null=True)
