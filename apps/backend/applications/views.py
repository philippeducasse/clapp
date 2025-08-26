from rest_framework import viewsets
from applications.models import Application
from circus_agent_backend.serializers import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = ApplicationSerializer
