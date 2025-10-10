from rest_framework import serializers
from applications.models import Application
from typing import Type

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Application] = Application
        fields: str = "__all__"
        read_only_fields = ("id",)