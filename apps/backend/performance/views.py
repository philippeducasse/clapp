from django.shortcuts import render

from rest_framework import viewsets
from performance.models import Performance
from circus_agent_backend.serializers import PerformanceSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = PerformanceSerializer
