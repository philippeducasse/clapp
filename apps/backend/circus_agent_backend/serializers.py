from rest_framework import serializers
from applications.models import Application
from festivals.models import Festival
from typing import Type


class BlankToNullDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)


class FestivalSerializer(serializers.ModelSerializer):
    start_date = BlankToNullDateField(required=False, allow_null=True)
    end_date = BlankToNullDateField(required=False, allow_null=True)

    class Meta:
        model: Type[Festival] = Festival
        fields: str = "__all__"
        read_only_fields = ("id",)


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Application] = Application
        fields: str = "__all__"
