from typing import Any, List, Type

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from clapp_backend.utils import NormalizedURLField
from organisations.residencies.models import Residency, ResidencyContact
from organisations.serializers import (
    BaseContactSerializer,
    BlankToNullDateField,
    OrganisationSerializerMixin,
    handle_nested_contacts,
)


class ResidencyContactSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = ResidencyContact


class ResidencySerializer(OrganisationSerializerMixin, WritableNestedModelSerializer):
    contacts = ResidencyContactSerializer(many=True, required=False)
    website_url = NormalizedURLField(required=False, allow_blank=True)

    start_date = BlankToNullDateField(required=False, allow_null=True)
    end_date = BlankToNullDateField(required=False, allow_null=True)

    has_application_this_year = serializers.BooleanField(read_only=True, required=False)
    latest_application_status = serializers.CharField(
        read_only=True, allow_null=True, required=False
    )
    latest_application_date = serializers.DateField(read_only=True, allow_null=True, required=False)
    current_year_application = serializers.SerializerMethodField()

    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)

    class Meta:
        model: Type[Residency] = Residency
        fields: List[str] = [
            "id",
            "name",
            "description",
            "country",
            "town",
            "website_url",
            "tag",
            "start_date",
            "end_date",
            "approximate_date",
            "application_date_start",
            "application_date_end",
            "application_type",
            "comments",
            "contacts",
            "deleted_at",
            # Annotated fields
            "has_application_this_year",
            "latest_application_status",
            "latest_application_date",
            # Nested applications
            "current_year_application",
            # User-created flag (for admin differentiation)
            "is_user_created",
            "added_by",
        ]
        read_only_fields = ("id", "deleted_at")

    def update(self, instance: Residency, validated_data: Residency) -> dict[str, Any]:
        contacts_data = validated_data.pop("contacts", None)

        # Update residency fields
        instance = super().update(instance, validated_data)

        if contacts_data is not None:
            handle_nested_contacts(instance, contacts_data, ResidencyContact, user=instance.user)

        return instance

    def get_current_year_application(self, obj: Residency) -> dict[str, Any]:
        from applications.serializer import MinimalApplicationSerializer

        applications = getattr(obj, "_prefetched_current_year_apps", [])
        application = applications[0] if applications else None

        return MinimalApplicationSerializer(application, context=self.context).data
