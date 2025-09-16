from django.shortcuts import render

from rest_framework import viewsets
from performances.models import Performance
from circus_agent_backend.serializers import PerformanceSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = PerformanceSerializer
