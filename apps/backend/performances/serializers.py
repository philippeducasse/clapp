from typing import Type

from rest_framework import serializers

from performances.models import Dossier, Performance


class DossierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dossier
        fields = ["id", "file", "uploaded_at", "name"]
        read_only_fields = ["id", "uploaded_at", "name"]


class PerformanceSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateField(allow_null=True, required=False)
    genres = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    dossiers = DossierSerializer(many=True, read_only=True)

    class Meta:
        model: Type[Performance] = Performance
        fields: str = "__all__"
        read_only_fields = ("id",)
