from rest_framework import viewsets
from applications.models import Application
from applications.serializer import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
