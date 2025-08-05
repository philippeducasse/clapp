from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from applications.models import Application
from circus_agent_backend.serializers import ApplicationSerializer
from django.core.mail import EmailMessage
from django.http import HttpRequest


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = ApplicationSerializer
