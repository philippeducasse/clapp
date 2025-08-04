from typing import Dict, Any, Optional
from festivals.models import Festival
import json
from datetime import datetime
import re
import math
from mistralai import ConversationResponse, TextChunk

def generate_enrich_prompt(festival: Festival, search_results: Optional[str]) -> str:
    current_year: int = datetime.now().year
    fields: list[str] = [
        f.name for f in Festival._meta.get_fields() if f.concrete and not f.many_to_many
    ]

    for field in fields:
        value: Any = getattr(festival, field)

        # Check if the value is NaN or a string representation of NaN
        if isinstance(value, float) and math.isnan(value):
            setattr(festival, field, None)
        elif isinstance(value, str) and value.lower() == "nan":
            setattr(festival, field, None)

    missing: list[str] = [field for field in fields if not getattr(festival, field)]

    prompt: str = f"""
      You are an assistant enriching festival data for a cultural booking app.
      Your task is to verify and complete the information about the festival below.

      You have retrieved this information through a web search: {search_results}.  

      Here is the current known information:

      country: {festival.country}
      town (could be a city): {festival.town}
      approximate_date (give as "early July", "end of August", etc.): {festival.approximate_date}
      start_date: {festival.start_date}
      end_date: {festival.end_date}
      website_url: {festival.website_url}
      festival_type: {festival.festival_type}
      description : {festival.description}
      contact_person: {festival.contact_person}
      contact_email: {festival.contact_email}
      application_date_start: {festival.application_date_start}
      application_date_end: {festival.application_date_end}
      application_type: {festival.application_type}

      Your task:
      - Use the provided web search to complete missing fields or update old fields with new information.
      - If the search result are in a different language, translate the data into English.
      - Return a JSON object containing **only these fields** (even if already filled):
        {missing}
      - Use accurate and up-to-date data.
      - Output valid JSON and nothing else.
      
      Example Output:
        {{
          "country": "Belgium",
          "town": "Brussels",
          "start_date": "2023-10-15",
          "description": "An annual festival celebrating contemporary arts."
        }}
      """

    return prompt

def extract_search_results(search_results: ConversationResponse ):
    content = next((o for o in search_results.outputs if o.type == "message.output"), None)

    print("content", content)

    chunks = getattr(content, "content", [])

    parsed_text = " ".join(chunk.text for chunk in chunks if isinstance(chunk, TextChunk))

    return parsed_text

def extract_fields_from_llm(llm_response: str) -> Dict[str, Any]:
    # Use regular expression to remove Markdown code block formatting
    json_str: str = re.sub(r"```json\s*|\s*```", "", llm_response).strip()

    try:
        # Parse the JSON response from the Mistral API
        response_data: Dict[str, Any] = json.loads(json_str)

        # Extract the fields from the response
        updated_fields: Dict[str, Any] = {}

        def convert_date(date_str: str) -> Optional[str]:
            try:
                date_obj: datetime = datetime.strptime(date_str, "%B %d, %Y")
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
            converted_date: Optional[str] = convert_date(response_data["start_date"])
            if converted_date:
                updated_fields["start_date"] = converted_date
        if "end_date" in response_data:
            converted_date: Optional[str] = convert_date(response_data["end_date"])
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

def clean_festival_data(festival: Festival) -> None:
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
        url: str = festival.website_url.strip()
        if not url.startswith("http"):
            url = "https://" + url
        festival.website_url = url.lower()

    if festival.description:
        desc: str = festival.description.strip()
        if not desc.endswith("."):
            desc += "."
        festival.description = desc

    # Optionally normalize dates here (if needed)

def generate_application_mail_prompt(festival: Festival) -> str:
    # Determine the appropriate salutation based on the contact person's name
    contact_name = festival.contact_person.strip() if festival.contact_person else None
    if contact_name and contact_name.lower() != 'nan':
        salutation = f"Use a standard salutation in the language of {festival.country} and include the name '{contact_name}'."
    else:
        salutation = f"Use a standard salutation in the language of {festival.country} addressed to the {festival.festival_name} organizers."

    prompt = f"""
You are Philippe Ducasse, a renowned performer seeking to apply to various festivals with your show "Ah Bah Bravo!".
Your task is to generate a personalized and professional email in plain text format to apply for participation in the festival.
The entire email should be written in the language of {festival.country}. Do not include a subject.

Festival Details:
- Festival Type: {festival.festival_type}
- Description: {festival.description}
- Contact Person: {contact_name}
- Contact Email: {festival.contact_email}

Email Requirements:
- Salutation: {salutation}
- Body: Explain why "Ah Bah Bravo!" is a great fit for their festival. Mention the unique aspects of your show and how it aligns with the festival's theme and audience. Ensure the text is engaging and professional. Keep the body concise, max 500 characters.
- Closing: Express enthusiasm for the opportunity to perform and provide your contact information for further discussion.
Ensure the email is formatted as plain text without any markdown or bullet points.
"""
    return prompt
