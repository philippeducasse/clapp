import logging
from typing import Any, List, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from phonenumber_field.modelfields import PhoneNumberField

from clapp_backend.utils import normalize_url

logger = logging.getLogger(__name__)


class SoftDeleteQuerySet(QuerySet):
    """QuerySet that filters out soft-deleted objects by default"""

    def delete(self) -> tuple[int, dict[str, int]]:
        """Override delete to perform soft delete"""
        from django.utils import timezone

        return self.update(deleted_at=timezone.now())

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Actually delete the objects from database"""
        return super().delete()

    def alive(self) -> "SoftDeleteQuerySet":
        """Return only non-deleted objects"""
        return self.filter(deleted_at__isnull=True)

    def deleted(self) -> "SoftDeleteQuerySet":
        """Return only deleted objects"""
        return self.filter(deleted_at__isnull=False)

    def with_deleted(self) -> "SoftDeleteQuerySet":
        """Return all objects including deleted ones"""
        return self


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Manager that returns non-deleted objects by default

    Uses from_queryset() to make queryset methods (alive, deleted, with_deleted)
    available on the manager while preserving RelatedManager filters.
    """

    def get_queryset(self) -> SoftDeleteQuerySet:
        """Apply default alive filter to all queries"""
        return super().get_queryset().alive()

    def with_deleted(self) -> SoftDeleteQuerySet:
        """Return all objects including deleted, bypassing default alive filter"""
        # Use super().get_queryset() to get base queryset without alive filter
        # This preserves RelatedManager filters while including deleted objects
        return super().get_queryset()

    def deleted(self) -> SoftDeleteQuerySet:
        """Return only deleted objects, bypassing default alive filter"""
        # Use super().get_queryset() to get base queryset without alive filter
        return super().get_queryset().deleted()


class Organisation(models.Model):
    TAGS: List[Tuple[str, str]] = [
        ("STAR", "Star"),
        ("WARNING", "Warning"),
        ("INACTIVE", "Inactive"),
        ("WATCH", "Watch"),
        ("OTHER", "Other"),
    ]
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True)
    country = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    website_url = models.URLField(max_length=200, blank=True)
    comments = models.TextField(max_length=500, blank=True)
    tag = models.CharField(max_length=20, choices=TAGS, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    user = models.ForeignKey(
        "profiles.Profile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        # create a unique related name for each type of organisation
        # -> festivals_festival_set
        related_name="%(app_label)s_%(class)s_set",
    )

    is_seed_clone = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True
        ordering = ["name"]

    def clean(self) -> None:
        super().clean()
        if self.website_url:
            self.website_url = normalize_url(self.website_url)

    def __str__(self) -> str:
        return self.name

    def delete(self, using: Any = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Soft delete the organisation and cascade to contacts (but preserve applications)"""
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save()
        logger.info(f"Soft deleting {self.name}")
        self._soft_delete_contacts()

        return (1, {self._meta.label: 1})

    def hard_delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Actually delete from database"""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """Restore a soft-deleted organisation"""
        self.deleted_at = None
        self.save()

        self._restore_contacts()

        # Applications are not restored because they were never soft-deleted
        # See delete() method above

    def _soft_delete_contacts(self) -> None:
        """Cascade soft delete to contacts"""
        from django.utils import timezone

        # Get the contact model from the reverse relation
        contact_model = self.contacts.model
        # Get the field name that points to this organisation
        field_name = self.contacts.field.name  # e.g. 'festival', 'venue', 'residency'
        # Use the model's manager directly with explicit filter
        contact_model.objects.with_deleted().filter(
            **{field_name: self, "deleted_at__isnull": True}
        ).update(deleted_at=timezone.now())

    def _restore_contacts(self) -> None:
        """Restore contacts"""
        # Get the contact model from the reverse relation
        contact_model = self.contacts.model
        # Get the field name that points to this organisation
        field_name = self.contacts.field.name  # e.g. 'festival', 'venue', 'residency'
        # Use the model's manager directly with explicit filter
        contact_model.objects.with_deleted().filter(
            **{field_name: self, "deleted_at__isnull": False}
        ).update(deleted_at=None)

    def _soft_delete_applications(self) -> None:
        """Cascade soft delete to applications"""
        from django.utils import timezone

        from applications.models import Application

        content_type = ContentType.objects.get_for_model(self.__class__)
        Application.objects.with_deleted().filter(
            content_type=content_type, object_id=self.pk
        ).update(deleted_at=timezone.now())

    def _restore_applications(self) -> None:
        """Restore applications when organisation is restored"""

        from applications.models import Application

        content_type = ContentType.objects.get_for_model(self.__class__)
        Application.objects.with_deleted().filter(
            content_type=content_type, object_id=self.pk, deleted_at__isnull=False
        ).update(deleted_at=None)


class OrganisationContact(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    role = models.CharField(max_length=100, blank=True)
    phone = PhoneNumberField(blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    user = models.ForeignKey(
        "profiles.Profile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_set",
    )
    is_seed_clone = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.name} - {self.email}"

    def delete(self, using: Any = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Soft delete the contact"""
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save()
        return (1, {self._meta.label: 1})

    def hard_delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Actually delete from database"""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """Restore a soft-deleted contact"""
        self.deleted_at = None
        self.save()
