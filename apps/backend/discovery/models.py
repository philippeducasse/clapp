"""Discovery: superuser-only exploration that proposes new organisations for review.

The exploring itself happens in the separate `apps/discovery` service. This app only stores
runs, candidates and sources, and turns accepted candidates into shared seed organisations.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class DiscoveryRun(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED"
        RUNNING = "RUNNING"
        DONE = "DONE"
        FAILED = "FAILED"
        CANCELLED = "CANCELLED"

    ACTIVE_STATUSES = (Status.QUEUED, Status.RUNNING)
    FINISHED_STATUSES = (Status.DONE, Status.FAILED, Status.CANCELLED)
    # A run that hasn't reported anything for this long is treated as dead (e.g. service restart).
    STALE_AFTER = timedelta(minutes=10)
    MAX_PROGRESS_LINES = 500

    starting_point = models.TextField(max_length=2000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    cancel_requested = models.BooleanField(default=False)
    # How the service interpreted the starting point (goal, queries, start URLs…).
    plan = models.JSONField(default=dict, blank=True)
    # [{"at": iso datetime, "step": str, "message": str}], shown live on the Discover page.
    progress = models.JSONField(default=list, blank=True)
    # {"searches", "pages", "llm_calls", "leads", "leads_missing", "candidates"}
    counters = models.JSONField(default=dict, blank=True)
    errors = models.JSONField(default=list, blank=True)
    error = models.TextField(blank=True)  # why the whole run failed, if it did

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Run {self.pk} ({self.status}): {self.starting_point[:60]}"

    @property
    def is_active(self) -> bool:
        return self.status in self.ACTIVE_STATUSES

    def finish(self, status: str, error: str = "") -> None:
        self.status = status
        self.finished_at = timezone.now()
        if error:
            self.error = error
        self.save(update_fields=["status", "finished_at", "error"])

    def expire_if_stale(self) -> bool:
        """Mark an active run FAILED if the service stopped reporting. Returns True if it expired."""
        if not self.is_active:
            return False
        last_seen = self.last_heartbeat_at or self.created_at
        if timezone.now() - last_seen < self.STALE_AFTER:
            return False
        self.finish(self.Status.FAILED, "No progress from the discovery service for 10 minutes.")
        return True

    @classmethod
    def expire_stale_runs(cls) -> None:
        for run in cls.objects.filter(status__in=cls.ACTIVE_STATUSES):
            run.expire_if_stale()


class DiscoveryCandidate(models.Model):
    class OrgType(models.TextChoices):
        FESTIVAL = "FESTIVAL"
        RESIDENCY = "RESIDENCY"
        VENUE = "VENUE"

    class State(models.TextChoices):
        PENDING = "PENDING"
        ACCEPTED = "ACCEPTED"
        DISMISSED = "DISMISSED"
        ALREADY_KNOWN = "ALREADY_KNOWN"  # clapp already had it; kept for the record, hidden
        UNRESOLVED = "UNRESOLVED"  # lead whose official website couldn't be found

    class DismissReason(models.TextChoices):
        NOT_RELEVANT = "NOT_RELEVANT"
        WRONG_REGION = "WRONG_REGION"
        DEFUNCT = "DEFUNCT"
        DUPLICATE = "DUPLICATE"
        OTHER = "OTHER"

    run = models.ForeignKey(
        DiscoveryRun, on_delete=models.SET_NULL, null=True, blank=True, related_name="candidates"
    )
    org_type = models.CharField(max_length=20, choices=OrgType.choices)
    state = models.CharField(max_length=20, choices=State.choices, default=State.PENDING)
    dismiss_reason = models.CharField(max_length=20, choices=DismissReason.choices, blank=True)

    # Organisation facts, in the same formats as Festival / Residency / Venue.
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True)
    country = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    website_url = models.URLField(max_length=200, blank=True)
    domain = models.CharField(max_length=200, blank=True, db_index=True)
    # festival_type for festivals, venue_type for venues; unused for residencies.
    subtype = models.CharField(max_length=50, blank=True)
    application_type = models.CharField(max_length=50, blank=True)
    application_url = models.URLField(max_length=500, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_start_date = models.DateField(null=True, blank=True)
    approximate_date = models.CharField(max_length=100, blank=True)
    application_date_start = models.CharField(max_length=100, blank=True)
    application_date_end = models.CharField(max_length=100, blank=True)
    # [{"name", "email", "role"}]; emails were verified against fetched page text.
    contacts = models.JSONField(default=list, blank=True)

    # Evidence. found_via: the path that led here, e.g. search → artist site → calendar → site.
    # [{"kind": "SEARCH"|"ARTIST_SITE"|"AGGREGATOR"|"ORG_SITE", "url", "title"}]
    found_via = models.JSONField(default=list, blank=True)
    # Pages the facts came from: [{"url", "title", "snippet"}]
    sources = models.JSONField(default=list, blank=True)
    # Why the service thinks it fits. Superuser-only: never copied into the seed.
    relevance_reason = models.TextField(blank=True)

    # The seed organisation created when this candidate was accepted.
    seed_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    seed_object_id = models.PositiveBigIntegerField(null=True, blank=True)
    created_seed = GenericForeignKey("seed_content_type", "seed_object_id")

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.org_type}, {self.state})"


class DiscoverySource(models.Model):
    """An artist or aggregator site that produced leads, so later runs can go back to it."""

    class Kind(models.TextChoices):
        ARTIST_SITE = "ARTIST_SITE"
        AGGREGATOR = "AGGREGATOR"

    url = models.URLField(max_length=500, unique=True)
    domain = models.CharField(max_length=200, db_index=True)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    title = models.CharField(max_length=300, blank=True)
    calendar_url = models.URLField(max_length=500, blank=True)
    last_visited_at = models.DateTimeField(null=True, blank=True)
    leads_found = models.PositiveIntegerField(default=0)
    candidates_accepted = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-candidates_accepted", "-leads_found"]

    def __str__(self) -> str:
        return f"{self.domain} ({self.kind})"
