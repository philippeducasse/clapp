import re

from dotenv import load_dotenv
from mistralai import Mistral
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from festivals.models import Festival
from .serializers import FestivalSerializer
import os
import json
from datetime import datetime

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
        promt = self.generate_prompt_from_festival(festival)
        llm_resonse = self.call_mistral_api(promt)

        updated_fields= self.extract_fields_from_llm(llm_resonse)
        for field, value in updated_fields.items():
            setattr(festival, field, value)

        self.clean_festival_data(festival)

        festival.save()

        return Response(FestivalSerializer(festival).data)

    def generate_prompt_from_festival(self, festival : Festival):
        current_year = datetime.now().year
        fields = [
            f.name
            for f in Festival._meta.get_fields()
            if f.concrete and not f.many_to_many
        ]

        missing = [field for field in fields if not getattr(festival, field)]

        print("Missing fields:", missing)

        base = f"""
            You are an assistant enriching festival data for a cultural booking app.
        
            Here is the current known information (some fields are missing). Additional info is provided for necessary 
            fields. For date fields, provide dates for or after {current_year}
        
            {festival.country=}
            {festival.town=} Could also be a city
            {festival.approximate_date=} give the approximate date, for example "end of August", or "Summer". Be as
            specific as possible 
            {festival.start_date=}
            {festival.end_date=}
            {festival.website_url=}
            {festival.festival_type=}
            {festival.description=}
            {festival.contact_person=}
            {festival.contact_email=}
            {festival.application_date_end=}
            {festival.application_date_start=}
            {festival.application_type=}
            
        
        
            Please provide the missing fields only, as a JSON object with keys from:
            {missing}
        
            Search the web if necessary.
            Return only valid JSON.
            """

        return base

    def call_mistral_api(self, prompt: str):
        load_dotenv(".env")
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set.")
        model = "mistral-small-2503"
        client = Mistral(api_key=api_key)

        try:
            # Call the Mistral API to get a chat response
            chat_response = client.chat.complete(
                model=model, messages=[{"role": "user", "content": prompt}]
            )

            # Extract and return the content of the response
            return chat_response.choices[0].message.content

        except Exception as e:
            # Handle any errors that occur during the API call
            print(f"An error occurred: {e}")
            return {"error": str(e)}

    def extract_fields_from_llm(self, llm_response):
        # Use regular expression to remove Markdown code block formatting
        json_str = re.sub(r"```json\s*|\s*```", "", llm_response).strip()
        print("CLEANED: ", json_str)

        try:
            # Parse the JSON response from the Mistral API
            response_data = json.loads(json_str)

            # Extract the fields from the response
            updated_fields = {}

            # Check each field that might be returned by the API
            if 'festival_name' in response_data:
                updated_fields['festival_name'] = response_data['festival_name']
            if 'town' in response_data:
                updated_fields['town'] = response_data['town']
            if 'country' in response_data:
                updated_fields['country'] = response_data['country']
            if 'approximate_date' in response_data:
                updated_fields['approximate_date'] = response_data['approximate_date']
            if 'start_date' in response_data:
                updated_fields['start_date'] = response_data['start_date']
            if 'end_date' in response_data:
                updated_fields['end_date'] = response_data['end_date']
            if 'website_url' in response_data:
                updated_fields['website_url'] = response_data['website_url']
            if 'type' in response_data:
                updated_fields['type'] = response_data['type']
            if 'description' in response_data:
                updated_fields['description'] = response_data['description']
            if 'contact_person' in response_data:
                updated_fields['contact_person'] = response_data['contact_person']
            if 'contact_email' in response_data:
                updated_fields['contact_email'] = response_data['contact_email']

            print("Updated fields:", updated_fields)
            return updated_fields

        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            print(f"An error occurred while parsing the JSON response: {e}")
            return {}

        except Exception as e:
            # Handle any other errors
            print(f"An error occurred: {e}")
            return {}

    def clean_festival_data(self, festival: Festival):
        # Capitalize name
        if festival.festival_name:
            festival.festival_name = festival.festival_name.title()

        if festival.town:
            festival.town = festival.town.title()

        if festival.country:
            festival.country = festival.country.title()

        if festival.contact_person:
            festival.contact_person = festival.contact_person.title()

        if festival.contact_email:
            festival.contact_email = festival.contact_email.strip().lower()

        if festival.website_url:
            url = festival.website_url.strip()
            if not url.startswith("http"):
                url = "https://" + url
            festival.website_url = url.lower()

        if festival.description:
            desc = festival.description.strip()
            if not desc.endswith("."):
                desc += "."
            festival.description = desc

        # Optionally normalize dates here (if needed)
