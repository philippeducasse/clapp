
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from festivals.models import Festival
from .serializers import FestivalSerializer
import os
from .helpers import generate_prompt_from_festival, extract_fields_from_llm, clean_festival_data
from services.mistral_service import call_mistral_api
from dotenv import load_dotenv

# Provides CRUD operations for Festival
class FestivalViewSet(viewsets.ModelViewSet):
    queryset = Festival.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = FestivalSerializer

    # Adds an endpoint to default queryset. Detail means it affects only one entity
    @action(detail= True, methods=["post"])
    def enrich(self,request, pk=None):
        # Retrieves the Festival instance corresponding to the given pk (primary key) from the URL.
        festival = self.get_object()
        prompt = generate_prompt_from_festival(festival)
        load_dotenv(".env")
        model = os.getenv('MISTRAL_DEFAULT_MODEL')
        print("ARGS:", prompt, model)
        llm_response = call_mistral_api(model, prompt)

        updated_fields= extract_fields_from_llm(llm_response)
        for field, value in updated_fields.items():
            setattr(festival, field, value)

        clean_festival_data(festival)

        return Response(FestivalSerializer(festival).data)
