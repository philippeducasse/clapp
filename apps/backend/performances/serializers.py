from typing import Type

from rest_framework import serializers

from performances.models import Dossier, Performance
from circus_agent_backend.utils import NormalizedURLField


class DossierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dossier
        fields = ["id", "file", "uploaded_at", "name"]
        read_only_fields = ["id", "uploaded_at", "name"]


class PerformanceSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateField(allow_null=True, required=False)
    genres = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    dossiers = DossierSerializer(many=True, read_only=True)
    dossier_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False, allow_empty=True
    )
    trailer = NormalizedURLField(required=False, allow_blank=True, max_length=100)

    class Meta:
        model: Type[Performance] = Performance
        fields: str = "__all__"
        read_only_fields = ("id",)
        extra_kwargs = {"dossier_files": {"write_only": True}}

    def create(self, validated_data):
        dossier_files = validated_data.pop("dossier_files", [])
        performance = Performance.objects.create(**validated_data)

        for dossier_file in dossier_files:
            Dossier.objects.create(performance=performance, file=dossier_file)

        return performance

    def update(self, instance, validated_data):
        dossier_files = validated_data.pop("dossier_files", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for dossier_file in dossier_files:
            Dossier.objects.create(performance=instance, file=dossier_file)

        return instance
