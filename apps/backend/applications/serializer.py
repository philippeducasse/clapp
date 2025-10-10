from rest_framework import serializers
from applications.models import Application
from typing import Type


class ApplicationSerializer(serializers.ModelSerializer):
    organisation_type = serializers.SerializerMethodField()
    organisation_id = serializers.IntegerField(source="object_id", read_only=True)
    organisation_name = serializers.SerializerMethodField()

    class Meta:
        model: Type[Application] = Application
        fields: str = "__all__"
        read_only_fields = ("id",)
