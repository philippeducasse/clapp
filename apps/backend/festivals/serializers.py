from rest_framework import serializers
from festivals.models import Festival
class FestivalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Festival
        fields = '__all__'