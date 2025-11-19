from typing import Optional, Type

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from applications.models import Application
from organisations.festivals.models import Festival
from organisations.festivals.serializer import FestivalSerializer
from organisations.residencies.models import Residency
from organisations.residencies.serializer import ResidencySerializer
from organisations.venues.models import Venue
from organisations.venues.serializer import VenueSerializer
from performances.serializers import PerformanceSerializer
from profiles.serializers import ProfileSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    # Read: returns organization type as string, Write: accepts organization type as string
    organisation_type = serializers.CharField(required=False, write_only=True)
    # Read: returns nested organization object, Write: accepts organization ID
    organisation = serializers.IntegerField(source="object_id", required=False)

    performances = PerformanceSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True)
    profile_id = serializers.IntegerField(write_only=True, required=True)

    performance_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        source="performances",
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "created_at",
            "updated_at",
            "organisation_type",
            "organisation",
            "profile_id",
            "profile",
            "performance_ids",
            "performances",
            "application_date",
            "application_method",
            "email_subject",
            "email_recipients",
            "message",
            "attachments_sent",
            "application_status",
            "comments",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_organisation_type_display(self, object):
        if object.content_type:
            return object.content_type.model.upper()
        return None

    def to_representation(self, instance):
        """Convert model instance to dict - customize organisation fields"""
        data = super().to_representation(instance)

        if instance.content_type:
            data["organisation_type"] = instance.content_type.model.upper()
        else:
            data["organisation_type"] = None

        # Replace organisation ID with nested object
        if instance.organisation:
            if isinstance(instance.organisation, Festival):
                data["organisation"] = FestivalSerializer(instance.organisation).data
            elif isinstance(instance.organisation, Venue):
                data["organisation"] = VenueSerializer(instance.organisation).data
            elif isinstance(instance.organisation, Residency):
                data["organisation"] = ResidencySerializer(instance.organisation).data

        return data

    def create(self, validated_data):
        organisation_type = validated_data.pop("organisation_type", None)
        organisation_id = validated_data.pop("object_id", None)

        if organisation_type and organisation_id:
            try:
                content_type = ContentType.objects.get(model=organisation_type.lower())
            except ContentType.DoesNotExist:
                raise ValidationError(
                    {
                        "organisation_type": f"Invalid organisation type: {organisation_type}"
                    }
                )

            validated_data["content_type"] = content_type
            validated_data["object_id"] = organisation_id

        return super().create(validated_data)

    def update(self, instance, validated_data):
        organisation_type = validated_data.pop("organisation_type", None)
        organisation_id = validated_data.pop("object_id", None)

        if organisation_type:
            try:
                content_type = ContentType.objects.get(model=organisation_type.lower())
                validated_data["content_type"] = content_type
            except ContentType.DoesNotExist:
                raise ValidationError(
                    {
                        "organisation_type": f"Invalid organisation type: {organisation_type}"
                    }
                )

        if organisation_id is not None:
            validated_data["object_id"] = organisation_id

        return super().update(instance, validated_data)


class MinimalApplicationSerializer(serializers.ModelSerializer):
    """Minimal application serializer WITHOUT nested organisation - for use in FestivalSerializer"""

    organisation_type = serializers.SerializerMethodField(read_only=True)
    organisation_id = serializers.IntegerField(source="object_id", read_only=True)

    class Meta:
        model: Type[Application] = Application
        fields: str = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_organisation_type(self, obj: Application) -> Optional[str]:
        """Return the type of organisation (festival, venue, residency)"""
        if obj.content_type:
            return obj.content_type.model
        return None
