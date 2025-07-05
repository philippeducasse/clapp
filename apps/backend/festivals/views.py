from rest_framework import viewsets
from festivals.models import Festival
from .serializers import FestivalSerializer


# Provides CRUD operations for Festival
class FestivalViewSet(viewsets.ModelViewSet):
    queryset = Festival.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = FestivalSerializer
