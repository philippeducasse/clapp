from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from festivals.models import Festival
from circus_agent_backend.serializers import FestivalSerializer
import os
from .helpers import (
    generate_enrich_prompt,
    generate_application_mail_prompt,
    extract_fields_from_llm,
    clean_festival_data,
)
from services.mistral_service import call_mistral_api
from dotenv import load_dotenv
from django.http import HttpRequest
from typing import Dict, Any
from django.core.mail import EmailMessage


# Provides CRUD operations for Festival
class FestivalViewSet(viewsets.ModelViewSet):
    queryset = Festival.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = FestivalSerializer

    # Adds an endpoint to default queryset. Detail means it affects only one entity
    @action(detail=True, methods=["post"])
    def enrich(self, request: HttpRequest, pk: int = None) -> Response:
        # Retrieves the Festival instance corresponding to the given pk (primary key) from the URL.
        festival: Festival = self.get_object()
        prompt: str = generate_enrich_prompt(festival)
        load_dotenv(".env")
        model: str = os.getenv("MISTRAL_DEFAULT_MODEL")
        llm_response: str = call_mistral_api(model, prompt)

        updated_fields: Dict[str, Any] = extract_fields_from_llm(llm_response)
        for field, value in updated_fields.items():
            setattr(festival, field, value)

        clean_festival_data(festival)

        return Response(FestivalSerializer(festival).data)

    @action(detail=True, methods=["post"])
    def send_custom_email(self, request: HttpRequest, pk: int) -> Response:
        try:
            festival = Festival.objects.get(pk=pk)
        except Festival.DoesNotExist:
            return Response({"error": "Festival not found"}, status=404)

        festival_name: str = festival.festival_name

        # Email content
        subject: str = f"Philippe Ducasse Application for {festival_name}"
        load_dotenv(".env")
        model: str = os.getenv("MISTRAL_DEFAULT_MODEL")
        prompt: str = generate_application_mail_prompt(festival)
        message: str = call_mistral_api(model, prompt)

        # Create and send the email
        email: EmailMessage = EmailMessage(
            subject,
            message,
            "ducassephi@hotmail.fr",  # From email
            ["info@philippeducasse.com"]
            # [application.festival.contact_email],  # To email
        )

        try:
            email.send()
            return Response({"message": "Email sent successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)