import logging
from typing import Type

from rest_framework import serializers

from clapp_backend.utils import NormalizedURLField
from performances.models import Dossier, Performance

logger = logging.getLogger(__name__)


class DossierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dossier
        fields = ["id", "file", "uploaded_at", "name"]
        read_only_fields = ["id", "uploaded_at", "name"]


class PerformanceSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateField(allow_null=True, required=False)
    genres = serializers.ListField(
        child=serializers.CharField(allow_blank=True), required=False, allow_empty=True
    )
    dossiers = DossierSerializer(many=True, read_only=True)
    dossier_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False, allow_empty=True
    )
    trailer = NormalizedURLField(required=False, allow_blank=True, max_length=100)
    dossier_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False, allow_empty=True
    )

    class Meta:
        model: Type[Performance] = Performance
        fields: str = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        dossier_files = validated_data.pop("dossier_files", [])
        performance = Performance.objects.create(**validated_data)

        for dossier_file in dossier_files:
            Dossier.objects.create(performance=performance, file=dossier_file)
            logger.info("Dossier created successfully")

        return performance

    def update(self, instance, validated_data):
        dossier_files = validated_data.pop("dossier_files", [])
        dossier_ids = validated_data.pop("dossier_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If dossier_ids is provided, delete dossiers not in the list
        if dossier_ids is not None:
            instance.dossiers.exclude(id__in=dossier_ids).delete()

        for dossier_file in dossier_files:
            Dossier.objects.create(performance=instance, file=dossier_file)

        return instance
