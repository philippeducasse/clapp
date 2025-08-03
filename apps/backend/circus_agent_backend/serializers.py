from rest_framework import serializers
from applications.models import Application
from festivals.models import Festival
from typing import Type


class FestivalSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Festival] = Festival
        fields: str = "__all__"

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Application] = Application
        fields: str = "__all__"
