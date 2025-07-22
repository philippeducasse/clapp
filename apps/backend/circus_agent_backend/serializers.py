from rest_framework import serializers

from applications.models import Application
from festivals.models import Festival


class FestivalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Festival
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
