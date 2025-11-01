from rest_framework import serializers
from applications.models import Application
from typing import Type, Optional, Dict, Any
from performances.serializers import PerformanceSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    organisation_type = serializers.SerializerMethodField(read_only=True)
    organisation = serializers.SerializerMethodField(read_only=True)
    performances = PerformanceSerializer(many=True, read_only=True)

    # For writes
    content_type_id = serializers.IntegerField(write_only=True, required=False)
    object_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model: Type[Application] = Application
        fields: str = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

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
