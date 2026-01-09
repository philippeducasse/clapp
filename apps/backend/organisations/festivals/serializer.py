from typing import Any, List, Type

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from organisations.festivals.models import Festival, FestivalContact
from organisations.serializers import (
    BlankToNullDateField,
    BaseContactSerializer,
    handle_nested_contacts,
)
from circus_agent_backend.utils import NormalizedURLField


class FestivalContactSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = FestivalContact


class FestivalSerializer(WritableNestedModelSerializer):
    contacts = FestivalContactSerializer(many=True, required=False)
    website_url = NormalizedURLField(required=False, allow_blank=True)

    start_date = BlankToNullDateField(required=False, allow_null=True)
    end_date = BlankToNullDateField(required=False, allow_null=True)

    has_application_this_year = serializers.BooleanField(read_only=True, required=False)
    latest_application_status = serializers.CharField(
        read_only=True, allow_null=True, required=False
    )
    latest_application_date = serializers.DateField(read_only=True, allow_null=True, required=False)
    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)

    # will look for this name + get
    current_year_application = serializers.SerializerMethodField()

    class Meta:
        model: Type[Festival] = Festival
        fields: List[str] = [
            "id",
            "name",
            "description",
            "country",
            "town",
            "festival_type",
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
        ]

    def update(self, instance: Festival, validated_data: Festival) -> dict[str, Any]:
        contacts_data = validated_data.pop("contacts", None)

        # Update festival fields
        instance = super().update(instance, validated_data)

        if contacts_data is not None:
            handle_nested_contacts(instance, contacts_data, FestivalContact)

        return instance

    def get_current_year_application(self, obj: Festival) -> dict[str, Any]:
        from applications.serializer import MinimalApplicationSerializer

        applications = getattr(obj, "_prefetched_current_year_apps", [])
        application = applications[0] if applications else None

        return MinimalApplicationSerializer(application, context=self.context).data
