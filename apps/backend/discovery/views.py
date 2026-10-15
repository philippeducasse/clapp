import logging

from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from discovery import service_client
from discovery.accept import CannotAccept, accept_candidate
from discovery.known import KnownMatcher, known_index
from discovery.models import DiscoveryCandidate, DiscoveryRun, DiscoverySource
from discovery.permissions import IsDiscoveryService, IsSuperuser, ServiceTokenAuthentication
from discovery.serializers import (
    AcceptSerializer,
    CandidateInSerializer,
    DiscoveryCandidateSerializer,
    DiscoveryRunSerializer,
    DismissSerializer,
    RunCreateSerializer,
    RunUpdateSerializer,
    SourceInSerializer,
)
from organisations.utils import normalize_domain

logger = logging.getLogger(__name__)

# --- Frontend-facing API: /api/discovery/ (superusers only) -------------------------------


class DiscoveryRunViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = DiscoveryRunSerializer
    permission_classes = [IsSuperuser]
    queryset = DiscoveryRun.objects.select_related("created_by")

    def list(self, request: Request, *args, **kwargs) -> Response:
        DiscoveryRun.expire_stale_runs()
        return super().list(request, *args, **kwargs)

    def get_object(self) -> DiscoveryRun:
        run = super().get_object()
        run.expire_if_stale()
        return run

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Start a run from the starting point. Only one run can be active at a time (409)."""
        input_serializer = RunCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        DiscoveryRun.expire_stale_runs()
        with transaction.atomic():
            active = (
                DiscoveryRun.objects.select_for_update()
                .filter(status__in=DiscoveryRun.ACTIVE_STATUSES)
                .first()
            )
            if active is not None:
                return Response(
                    {"error": "A discovery run is already in progress.", "run_id": active.pk},
                    status=status.HTTP_409_CONFLICT,
                )
            run = DiscoveryRun.objects.create(
                starting_point=input_serializer.validated_data["starting_point"],
                created_by=request.user,
            )

        # Outside the transaction: the service calls back into the API and must see the run.
        try:
            service_client.start_run(run)
        except service_client.DiscoveryServiceError as exc:
            logger.warning(f"Discovery run {run.pk} could not start: {exc}")
            run.finish(DiscoveryRun.Status.FAILED, str(exc))

        return Response(self.get_serializer(run).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, pk: int) -> Response:
        """Ask the service to stop. It stops at its next progress update."""
        run = self.get_object()
        if not run.is_active:
            raise ValidationError({"error": "This run has already finished."})
        run.cancel_requested = True
        run.save(update_fields=["cancel_requested"])
        return Response(self.get_serializer(run).data)


class DiscoveryCandidateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DiscoveryCandidateSerializer
    permission_classes = [IsSuperuser]
    queryset = DiscoveryCandidate.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state", "run", "org_type"]

    @action(detail=True, methods=["post"])
    def accept(self, request: Request, pk: int) -> Response:
        """Create a shared seed from the candidate (with optional corrections) and copy it to all users."""
        candidate = self.get_object()
        overrides = AcceptSerializer(data=request.data, partial=True)
        overrides.is_valid(raise_exception=True)
        try:
            candidate = accept_candidate(candidate.pk, overrides.validated_data)
        except CannotAccept as exc:
            raise ValidationError({"error": str(exc)}) from exc
        return Response(self.get_serializer(candidate).data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request: Request, pk: int) -> Response:
        candidate = self.get_object()
        if candidate.state not in (
            DiscoveryCandidate.State.PENDING,
            DiscoveryCandidate.State.UNRESOLVED,
        ):
            raise ValidationError(
                {"error": f"A {candidate.state.lower()} candidate can't be dismissed."}
            )
        reason = DismissSerializer(data=request.data)
        reason.is_valid(raise_exception=True)

        candidate.state = DiscoveryCandidate.State.DISMISSED
        candidate.dismiss_reason = reason.validated_data["reason"]
        candidate.reviewed_at = timezone.now()
        candidate.save()
        return Response(self.get_serializer(candidate).data)

    @action(detail=True, methods=["post"])
    def restore(self, request: Request, pk: int) -> Response:
        """Put a dismissed candidate back to review."""
        candidate = self.get_object()
        if candidate.state != DiscoveryCandidate.State.DISMISSED:
            raise ValidationError({"error": "Only dismissed candidates can be restored."})

        candidate.state = (
            DiscoveryCandidate.State.PENDING
            if candidate.website_url
            else DiscoveryCandidate.State.UNRESOLVED
        )
        candidate.dismiss_reason = ""
        candidate.reviewed_at = None
        candidate.save()
        return Response(self.get_serializer(candidate).data)


# --- Internal API: /internal/discovery/ (discovery service only) --------------------------

SERVICE_AUTH = [ServiceTokenAuthentication]
SERVICE_ONLY = [IsDiscoveryService]
MAX_ERRORS = 200


@api_view(["PATCH"])
@authentication_classes(SERVICE_AUTH)
@permission_classes(SERVICE_ONLY)
def update_run(request: Request, pk: int) -> Response:
    """Progress report from the service. Doubles as heartbeat; answers whether to cancel."""
    update = RunUpdateSerializer(data=request.data)
    update.is_valid(raise_exception=True)
    data = update.validated_data

    with transaction.atomic():
        run = DiscoveryRun.objects.select_for_update().filter(pk=pk).first()
        if run is None:
            return Response({"error": "Run not found."}, status=status.HTTP_404_NOT_FOUND)

        # A finished run (e.g. expired as stale) is never reopened; tell the service to stop.
        if not run.is_active:
            return Response({"status": run.status, "cancel_requested": True})

        now = timezone.now()
        run.last_heartbeat_at = now
        if "plan" in data:
            run.plan = data["plan"]
        if "counters" in data:
            run.counters = data["counters"]
        if data.get("progress"):
            lines = [
                {
                    "at": (line.get("at") or now).isoformat(),
                    "step": line["step"],
                    "message": line["message"],
                }
                for line in data["progress"]
            ]
            run.progress = (run.progress + lines)[-DiscoveryRun.MAX_PROGRESS_LINES :]
        if data.get("errors"):
            run.errors = (run.errors + data["errors"])[-MAX_ERRORS:]
        if "error" in data:
            run.error = data["error"]

        new_status = data.get("status")
        if new_status == DiscoveryRun.Status.RUNNING and run.started_at is None:
            run.started_at = now
        if new_status:
            run.status = new_status
        if new_status in DiscoveryRun.FINISHED_STATUSES:
            run.finished_at = now
        run.save()

    return Response({"status": run.status, "cancel_requested": run.cancel_requested})


@api_view(["GET"])
@authentication_classes(SERVICE_AUTH)
@permission_classes(SERVICE_ONLY)
def get_known_index(request: Request) -> Response:
    """Everything the service should treat as already in clapp."""
    return Response(known_index())


@api_view(["POST"])
@authentication_classes(SERVICE_AUTH)
@permission_classes(SERVICE_ONLY)
def create_candidates(request: Request, pk: int) -> Response:
    """Save candidates found by a run. Exact matches with known organisations become ALREADY_KNOWN.

    Body: {"candidates": [...]}.
    """
    run = DiscoveryRun.objects.filter(pk=pk).first()
    if run is None:
        return Response({"error": "Run not found."}, status=status.HTTP_404_NOT_FOUND)

    incoming = CandidateInSerializer(data=request.data.get("candidates", []), many=True)
    incoming.is_valid(raise_exception=True)

    matcher = KnownMatcher(known_index())
    to_create = []
    for data in incoming.validated_data:
        candidate = DiscoveryCandidate(run=run, **data)
        candidate.domain = normalize_domain(candidate.website_url)
        if matcher.matches(candidate.name, candidate.country, candidate.domain):
            candidate.state = DiscoveryCandidate.State.ALREADY_KNOWN
        # Also catches duplicates within the same batch.
        matcher.add(candidate.name, candidate.country, candidate.domain)
        to_create.append(candidate)

    DiscoveryCandidate.objects.bulk_create(to_create)
    already_known = sum(c.state == DiscoveryCandidate.State.ALREADY_KNOWN for c in to_create)
    return Response(
        {"created": len(to_create) - already_known, "already_known": already_known},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@authentication_classes(SERVICE_AUTH)
@permission_classes(SERVICE_ONLY)
def upsert_sources(request: Request) -> Response:
    """Record artist/aggregator sites visited. Body: {"sources": [...]}; leads_found is added."""
    incoming = SourceInSerializer(data=request.data.get("sources", []), many=True)
    incoming.is_valid(raise_exception=True)

    now = timezone.now()
    for data in incoming.validated_data:
        source, _ = DiscoverySource.objects.get_or_create(
            url=data["url"],
            defaults={"domain": normalize_domain(data["url"]), "kind": data["kind"]},
        )
        source.kind = data["kind"]
        source.title = data["title"] or source.title
        source.calendar_url = data["calendar_url"] or source.calendar_url
        source.leads_found += data["leads_found"]
        source.last_visited_at = now
        source.save()

    return Response({"saved": len(incoming.validated_data)})
