from rest_framework import serializers
from applications.models import Application
from typing import Type, Optional, Dict, Any
from performances.serializers import PerformanceSerializer
from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    # read fields: returns nested objects
    organisation_type = serializers.SerializerMethodField(read_only=True)
    organisation = serializers.SerializerMethodField(read_only=True)
    performances = PerformanceSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True, required=False)

    # write fields - accepts Ids; not nested objects.
    profile_id = serializers.IntegerField(write_only=True, required=True)

    # accepts organisation type as string (eg "festival", "venue", "residency")
    content_type = serializers.CharField(write_only=True, required=False)
    # references the specific instance of the organisation
    object_id = serializers.IntegerField(write_only=True, required=False)

    performance_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        source="performances",
    )

    class Meta:
        model: Type[Application] = Application
        fields = [
            "id",
            "created_at",
            "updated_at",
            "organisation_type",
            "organisation",
            "content_type",
            "object_id",
            "profile_id",
            "profile",
            "performance_ids",
            "performances",
            "application_date",
            "application_method",
            "email_subject",
            "message",
            "attachments_sent",
            "attachments_received",
            "answer_received",
            "answer_date",
            "application_status",
            "follow_up_date",
            "response_details",
            "performance_details",
            "contract_received",
            "contract_signed",
            "payment_received",
            "payment_amount",
            "comments",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        content_type_str = validated_data.pop("content_type", None)
        object_id = validated_data.pop("object_id", None)

        application = super().create(validated_data)

        if content_type_str and object_id:
            # Look up the ContentType based on the model name
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get(model=content_type_str.lower())
            application.content_type = content_type
            application.object_id = object_id
            application.save()

        return application

    def update(self, instance, validated_data):
        content_type_str = validated_data.pop("content_type", None)
        object_id = validated_data.pop("object_id", None)

        instance = super().update(instance, validated_data)

        if content_type_str is not None:
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get(model=content_type_str.lower())
            instance.content_type = content_type
        if object_id is not None:
            instance.object_id = object_id

        if content_type_str is not None or object_id is not None:
            instance.save()

        return instance

    def get_organisation_type(self, obj: Application) -> Optional[str]:
        """Return the type of organisation (festival, venue, residency)"""
        if obj.content_type:
            return obj.content_type.model.capitalize()
        return None

    def get_organisation(self, obj: Application) -> Optional[Dict[str, Any]]:
        """Return the full nested organisation object"""
        if not obj.organisation:
            return None

        if not obj.content_type:
            return None

        from organisations.festivals.serializer import FestivalSerializer
        from organisations.venues.serializer import VenueSerializer
        from organisations.residencies.serializer import ResidencySerializer

        serializer_map = {
            "festival": FestivalSerializer,
            "venue": VenueSerializer,
            "residency": ResidencySerializer,
        }

        model_name = obj.content_type.model
        serializer_class = serializer_map.get(model_name)

        if serializer_class:
            return serializer_class(obj.organisation).data  # type: ignore[attr-defined]

        return None


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
