from rest_framework import serializers

from discovery.accept import EDITABLE_FIELDS
from discovery.models import DiscoveryCandidate, DiscoveryRun, DiscoverySource

# --- Frontend-facing (superusers) ---------------------------------------------------------


class DiscoveryRunSerializer(serializers.ModelSerializer):
    created_by = serializers.EmailField(source="created_by.email", read_only=True, default=None)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = DiscoveryRun
        fields = [
            "id",
            "starting_point",
            "status",
            "is_active",
            "cancel_requested",
            "plan",
            "progress",
            "counters",
            "errors",
            "error",
            "created_by",
            "created_at",
            "started_at",
            "finished_at",
            "last_heartbeat_at",
        ]
        read_only_fields = fields


class RunCreateSerializer(serializers.Serializer):
    starting_point = serializers.CharField(max_length=2000, trim_whitespace=True)


class DiscoveryCandidateSerializer(serializers.ModelSerializer):
    created_seed = serializers.SerializerMethodField()

    class Meta:
        model = DiscoveryCandidate
        exclude = ["seed_content_type", "seed_object_id"]
        read_only_fields = [f.name for f in DiscoveryCandidate._meta.fields]

    def get_created_seed(self, obj: DiscoveryCandidate) -> dict | None:
        if not obj.seed_object_id or not obj.seed_content_type_id:
            return None
        return {"org_type": obj.org_type, "id": obj.seed_object_id}


class AcceptSerializer(serializers.ModelSerializer):
    """Optional corrections made by the reviewer before accepting."""

    class Meta:
        model = DiscoveryCandidate
        fields = list(EDITABLE_FIELDS)
        extra_kwargs = {field: {"required": False} for field in EDITABLE_FIELDS}


class DismissSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(
        choices=DiscoveryCandidate.DismissReason.choices,
        default=DiscoveryCandidate.DismissReason.OTHER,
    )


# --- Internal (discovery service) ---------------------------------------------------------


class ProgressLineSerializer(serializers.Serializer):
    at = serializers.DateTimeField(required=False)
    step = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=1000)


class RunUpdateSerializer(serializers.Serializer):
    """Partial update from the service. `progress` and `errors` are appended, the rest replaced."""

    status = serializers.ChoiceField(
        choices=[
            DiscoveryRun.Status.RUNNING,
            DiscoveryRun.Status.DONE,
            DiscoveryRun.Status.FAILED,
            DiscoveryRun.Status.CANCELLED,
        ],
        required=False,
    )
    plan = serializers.DictField(required=False)
    counters = serializers.DictField(child=serializers.IntegerField(min_value=0), required=False)
    progress = ProgressLineSerializer(many=True, required=False)
    errors = serializers.ListField(child=serializers.CharField(max_length=1000), required=False)
    error = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class CandidateContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    role = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")


class EvidenceSerializer(serializers.Serializer):
    kind = serializers.CharField(max_length=30, required=False, allow_blank=True)
    url = serializers.URLField(max_length=1000)
    title = serializers.CharField(max_length=300, required=False, allow_blank=True)
    snippet = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class CandidateInSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(
        choices=[DiscoveryCandidate.State.PENDING, DiscoveryCandidate.State.UNRESOLVED],
        default=DiscoveryCandidate.State.PENDING,
    )
    contacts = CandidateContactSerializer(many=True, required=False)
    found_via = EvidenceSerializer(many=True, required=False)
    sources = EvidenceSerializer(many=True, required=False)

    class Meta:
        model = DiscoveryCandidate
        fields = [
            "org_type",
            "state",
            "name",
            "description",
            "country",
            "town",
            "website_url",
            "subtype",
            "application_type",
            "application_url",
            "start_date",
            "end_date",
            "estimated_start_date",
            "approximate_date",
            "application_date_start",
            "application_date_end",
            "contacts",
            "found_via",
            "sources",
            "relevance_reason",
        ]


class SourceInSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=500)
    kind = serializers.ChoiceField(choices=DiscoverySource.Kind.choices)
    title = serializers.CharField(max_length=300, required=False, allow_blank=True, default="")
    calendar_url = serializers.URLField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    leads_found = serializers.IntegerField(min_value=0, required=False, default=0)
