from datetime import datetime
from typing import Any, Dict

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.html import strip_tags
from festivals.models import Festival
from circus_agent_backend.serializers import FestivalSerializer
from applications.models import Application
from services.gemini_service import GeminiClient
from .helpers import (
    generate_application_mail_prompt,
    extract_fields_from_llm,
    clean_festival_data,
    generate_enrich_prompt,
)
from services.mistral_service import MistralClient
from django.http import HttpRequest


# Provides CRUD operations for Festival
class FestivalViewSet(viewsets.ModelViewSet):
    queryset = Festival.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = FestivalSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mistral_client = MistralClient()
        self.gemini_client = GeminiClient()

    # Adds an endpoint to default queryset. Detail means it affects only one entity
    @action(detail=True, methods=["post"])
    def enrich(self, request: HttpRequest, pk: int = None) -> Response:
        # Retrieves the Festival instance corresponding to the given pk (primary key) from the URL.
        festival: Festival = self.get_object()

        query = f"{festival.website_url} {festival.festival_name} {festival.country} {datetime.now().year}"

        # search_results: ConversationResponse = self.mistral_client.search(query=query)
        # parsed_results: str = extract_search_results(search_results)
        # prompt: str = generate_enrich_prompt(festival, parsed_results)

        search_results = self.gemini_client.search(query=query)
        prompt: str = generate_enrich_prompt(festival, search_results)

        llm_response: str = self.mistral_client.chat(prompt=prompt)

        updated_fields: Dict[str, Any] = extract_fields_from_llm(llm_response)
        for field, value in updated_fields.items():
            setattr(festival, field, value)

        clean_festival_data(festival)

        return Response(FestivalSerializer(festival).data)

    @action(detail=True, methods=["post"])
    def apply(self, request: HttpRequest, pk: int) -> Response:

        try:
            festival = Festival.objects.get(pk=pk)
        except Festival.DoesNotExist:
            return Response({"error": "Festival not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = request.data.get("message")
            subject = request.data.get("email_subject")
            attachments = request.FILES.getlist("attachments_sent")


            if not message or not subject:
                return Response({"error": "Message and/or subject not found"}, status=status.HTTP_400_BAD_REQUEST)
            
             # Calculate the application year
            current_date = timezone.now().date()
            application_year = current_date.year
            if current_date.month >= 9:
                application_year += 1

            # Check if an application already exists for the festival and year
            existing_application = Application.objects.filter(
                festival=festival,
                application_date__year=application_year
            ).first()
            
            if existing_application:
                return Response(
                    {
                        "message": "Application already exists for this festival and year",
                        "application_id": existing_application.id,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            application = Application.objects.create(
                festival=festival,
                application_date=timezone.now().date(),
                application_status="DRAFT",
                message=message,
                email_subject=subject,
            )
 
            if attachments:
                application.attachments_sent = [file.name for file in attachments]
                application.save()


            try:
                text_content = strip_tags(application.message)  # plain text fallback
                html_content = application.message  # Tiptap HTML

                email = EmailMultiAlternatives(subject, text_content, "ducassephi@hotmail.fr", ["info@philippeducasse.com"])
                email.attach_alternative(html_content, "text/html")

                for file in attachments:
                    email.attach(file.name, file.read(), file.content_type)

                email.send(fail_silently=False)
                application.application_status = (
                    "APPLIED"
                )
                application.save()
                return Response(
                    {"message": "Application sent successfully"}, status=200
                )
            except Exception as e:
                return Response(
                    {"error": f"Email failed to send: {str(e)}"}, status=500
                )

        except Exception as e:
            return Response(
                {
                    "error": "Failed to process application",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_email(self, request: HttpRequest, pk: int) -> Response:
        try:
            festival = Festival.objects.get(pk=pk)
        except Festival.DoesNotExist:
            return Response({"error": "Festival not found"}, status=status.HTTP_404_NOT_FOUND)

        festival_name: str = festival.festival_name

        # Email content
        prompt: str = generate_application_mail_prompt(festival)
        message: str = self.mistral_client.chat(prompt=prompt)

        return Response({"message": message}, status=status.HTTP_200_OK)


