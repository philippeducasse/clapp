from typing import Dict, Any, Optional
from festivals.models import Festival
import json
import re
from mistralai import ConversationResponse, TextChunk


def generate_enrich_prompt(festival: Festival, search_results: Optional[str]) -> str:

    festival_types = Festival.FESTIVAL_TYPES
    application_types = Festival.APPLICATION_TYPE

    sr = search_results or "No search results provided."

    # Small helpers to avoid 'None' textual noise in the prompt
    def nv(x):
        return "" if x is None else str(x)

    fest_types_str = ", ".join([value for (value, _) in festival_types])
    app_types_str = ", ".join([value for (value, _) in application_types])

    prompt = f"""
    You are enriching festival data for a cultural booking app.

    TASK
    - Read the current record and the web search snippets.
    - If the web snippets provide better or newer information for a field, **you must update it**.
    - If a field is missing in the snippets, keep the existing value.
    - Translate non-English data to English.
    - Normalize dates to ISO 8601 as strings: "YYYY-MM-DD".
    - If a single text gives a **date range** (e.g., "12–15 July 2026"), set:
      - start_date = first day in ISO
      - end_date   = last day in ISO
      - also update approximate_date (e.g., "mid July" or "late June–early July" if it spans months)
    - If only month/year is known, leave start_date/end_date empty strings and set a clear approximate_date.
    - Choose festival_type from: {fest_types_str}
    - Choose application_type from: {app_types_str}

    SOURCES & CONFLICTS
    - Prefer official festival website > reputable cultural listings > news > blogs.
    - If sources conflict, pick the **most recent official source**.

    OUTPUT FORMAT
    - Return **only** a single JSON object, no prose.
    - Valid JSON. No comments. No trailing commas.
    - Exactly these keys (strings):
      country, town, approximate_date, start_date, end_date, website_url,
      festival_type, description, contact_person, contact_email,
      application_date_start, application_date_end, application_type,
      sources, updated_fields

    CURRENT RECORD
    country: {nv(festival.country)}
    town: {nv(festival.town)}
    approximate_date: {nv(festival.approximate_date)}
    start_date: {nv(festival.start_date)}
    end_date: {nv(festival.end_date)}
    website_url: {nv(festival.website_url)}
    festival_type: {nv(festival.festival_type)}
    description: {nv(festival.description)}
    contact_person: {nv(festival.contact_person)}
    contact_email: {nv(festival.contact_email)}
    application_date_start: {nv(festival.application_date_start)}
    application_date_end: {nv(festival.application_date_end)}
    application_type: {nv(festival.application_type)}
    comments: {nv(festival.comments)}

    WEB SEARCH SNIPPETS (include URLs if you have them)
    {sr}

    APPROXIMATE DATE RULES
    - Day 1–10 → "early <Month>"
    - Day 11–20 → "mid <Month>"
    - Day 21–31 → "late <Month>"
    - If the range spans two months, combine, e.g., "late June–early July".

    RECOGNITION HINTS
    festival_type (choose one: from {fest_types_str} )
    application_type  (choose one: EMAIL, FORM, INVITATION_ONLY, UNKNOWN, OTHER)

    Decision order (apply the first rule that matches; do not skip ahead):
    1) FORM — there is an application portal or form (any language; may be Google Form, Typeform, Jotform; or an obvious
     “apply/inscription/anmeldung/postuler/solicitar” button or dedicated application page).
    2) INVITATION_ONLY — the event is curated/by invitation only (any language).
    3) EMAIL — the page asks to send proposals/submissions by email OR mentions applying via email.
    4) FALLBACK to EMAIL — if none of the above are present BUT a contact email is present on the page or the current
     record has a non-empty contact_email, classify as EMAIL.
    5) OTHER - if the application method is specifically mentioned and is neither FORM, INVITATION_ONLY, nor EMAIL. 
     Add details about the application process in the comments field.
    6) UNKNOWN — only if there is no form, no invitation-only statement, and **no** email available at all.

    Notes:
    - Treat hints as concepts, not exact strings (any language).
    - festival_type:
      - look for domain terms: street festival, circus, music, theatre, dance, film, circus.

    REQUIRED JSON SHAPE (example, syntactically correct — values are illustrative):
    {{
      "country": "Belgium",
      "town": "Brussels",
      "approximate_date": "mid October",
      "start_date": "2026-10-15",
      "end_date": "2026-10-20",
      "website_url": "https://examplefest.be",
      "festival_type": "STREET",
      "description": "Annual festival showcasing contemporary circus arts.",
      "contact_person": "Jane Doe",
      "contact_email": "info@examplefest.be",
      "application_date_start": "2026-05-01",
      "application_date_end": "2026-06-15",
      "application_type": "FORM",
      "comments": "this is a comment."
    }}
    """
    return prompt


def extract_search_results(search_results: ConversationResponse):
    content = next(
        (o for o in search_results.outputs if o.type == "message.output"), None
    )
    # print("content", content)

    chunks = getattr(content, "content", [])

    parsed_text = " ".join(
        chunk.text for chunk in chunks if isinstance(chunk, TextChunk)
    )

    return parsed_text


def extract_fields_from_llm(llm_response: str) -> Dict[str, Any]:
    json_str: str = re.sub(r"```json\s*|\s*```", "", llm_response).strip()
    try:
        # Parse the JSON response from the Mistral API
        response_data: Dict[str, Any] = json.loads(json_str)
        return response_data

    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the JSON response: {e}")
        return {}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def clean_festival_data(festival: Festival) -> None:
    # Capitalize name
    def clean_nan(value: str) -> str:
        return "" if str(value).strip().lower() == "nan" else str(value).strip()


    if festival.festival_name:
        festival.festival_name = festival.festival_name.title()

    if festival.town:
        festival.town = clean_nan(festival.town.title())

    if festival.country:
        festival.country = clean_nan(festival.country.title())

    if festival.contact_person:
        festival.contact_person = clean_nan(festival.contact_person.title())

    if festival.contact_email:
        festival.contact_email = clean_nan(festival.contact_email.strip().lower())

    if festival.comments:
        festival.comments = clean_nan(festival.comments.strip().lower())

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




def generate_application_mail_prompt(festival: Festival) -> str:
    # Determine the appropriate salutation based on the contact person's name
    contact_name = festival.contact_person.strip() if festival.contact_person else None
    if contact_name and contact_name.lower() != "nan":
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
