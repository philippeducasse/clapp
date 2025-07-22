from festivals.models import Festival
import json
from datetime import datetime
import re
import math


def generate_prompt_from_festival(festival: Festival):
    current_year = datetime.now().year
    fields = [
        f.name for f in Festival._meta.get_fields() if f.concrete and not f.many_to_many
    ]

    for field in fields:
        value = getattr(festival, field)

        # Check if the value is NaN or a string representation of NaN
        if isinstance(value, float) and math.isnan(value):
            setattr(festival, field, None)
        elif isinstance(value, str) and value.lower() == "nan":
            setattr(festival, field, None)

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


def extract_fields_from_llm(llm_response):
    # Use regular expression to remove Markdown code block formatting
    json_str = re.sub(r"```json\s*|\s*```", "", llm_response).strip()
    print("CLEANED: ", json_str)

    try:
        # Parse the JSON response from the Mistral API
        response_data = json.loads(json_str)

        # Extract the fields from the response
        updated_fields = {}

        def convert_date(date_str):
            try:
                date_obj = datetime.strptime(date_str, "%B %d, %Y")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                return None

        # Check each field that might be returned by the API
        if "festival_name" in response_data:
            updated_fields["festival_name"] = response_data["festival_name"]
        if "town" in response_data:
            updated_fields["town"] = response_data["town"]
        if "country" in response_data:
            updated_fields["country"] = response_data["country"]
        if "approximate_date" in response_data:
            updated_fields["approximate_date"] = response_data["approximate_date"]
        if "start_date" in response_data:
            converted_date = convert_date(response_data["start_date"])
            if converted_date:
                updated_fields["start_date"] = converted_date
        if "end_date" in response_data:
            converted_date = convert_date(response_data["end_date"])
            if converted_date:
                updated_fields["end_date"] = converted_date
        if "website_url" in response_data:
            updated_fields["website_url"] = response_data["website_url"]
        if "type" in response_data:
            updated_fields["type"] = response_data["type"]
        if "description" in response_data:
            updated_fields["description"] = response_data["description"]
        if "contact_person" in response_data:
            updated_fields["contact_person"] = response_data["contact_person"]
        if "contact_email" in response_data:
            updated_fields["contact_email"] = response_data["contact_email"]

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


def clean_festival_data(festival: Festival):
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
