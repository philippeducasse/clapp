from rest_framework import serializers
from performances.models import Performance


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Performance] = Performance
        fields: str = "__all__"
        read_only_fields = ("id",)
