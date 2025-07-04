from django.db import models

class Festival(models.Model):

    FESTIVAL_TYPES = [
        ('STREET', 'Street'),
        ('PUPPET', 'Puppet'),
        ('JUGGLING_CONVENTION', 'Juggling convention'),
        ('CIRCUS', 'Circus'),
        ('MUSIC', 'Music'),
        ('THEATRE', 'Theatre'),
        ('DANCE', 'Dance'),
        ('OTHER', 'Other'),
    ]

    festival_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    festival_type = models.CharField(max_length=50, choices=FESTIVAL_TYPES, default="STREET")
    website_url = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.CharField(max_length=200, blank=True, null=True)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    date_text = models.CharField(max_length=100, blank=True, null= True)
    applied = models.BooleanField(default=False)
    comments = models.CharField(max_length=500, blank=True, null=True)
