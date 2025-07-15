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

        # festival.save()

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
        Your task is to verify and complete the information about the festival below.

        Always perform a web search to retrieve the most accurate and current information, 
        even if a field is already partially filled or looks complete. Assume nothing — verify everything.
        For all date-related fields, ensure the result is relevant for {current_year} or later.

        Here is the current known information:

        country: {festival.country}
        town (could be a city): {festival.town}
        approximate_date (give as "early July", "end of August", etc.): {festival.approximate_date}
        start_date: {festival.start_date}
        end_date: {festival.end_date}
        website_url: {festival.website_url}
        festival_type: {festival.festival_type}
        description: {festival.description}
        contact_person: {festival.contact_person}
        contact_email: {festival.contact_email}
        application_date_start: {festival.application_date_start}
        application_date_end: {festival.application_date_end}
        application_type: {festival.application_type}

        Your task:
        - Perform a web search to confirm or fill in the fields listed below.
        - Return a JSON object containing **only these fields** (even if already filled):  
          {missing}
        - Use accurate and up-to-date data.
        - Output valid JSON and nothing else.
        """

        return base

    def call_mistral_api(self, prompt: str):
        load_dotenv(".env")
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set.")
        model = "mistral-medium-2505"
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
