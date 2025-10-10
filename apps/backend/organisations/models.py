from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    website_url = models.URLField(max_length=200, blank=True, null=True)
    comments = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class OrganisationContact(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=200)
    role = models.CharField(max_length=100, blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.name} - {self.email}"
