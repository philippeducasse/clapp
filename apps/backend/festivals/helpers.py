from typing import Dict, Any, List, Optional
from festivals.models import Festival
from profiles.models import Profile
from performances.models import Performance
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


def generate_application_mail_prompt(
    festival: Festival, profile: Profile, performances: List[Performance]
) -> str:
    # Determine language for email - default to English if country not specified
    language = "English" if not festival.country else f"language of {festival.country}"
    print("PERFORMANCE IN HELPER: ", performances)
    performance_objects = [Performance(**perf_data) for perf_data in performances]
    # Determine salutation based on contact person
    contact_name = festival.contact_person.strip() if festival.contact_person else None
    if contact_name and contact_name.lower() != "nan":
        salutation = f"Use a standard salutation in {language} and include the name '{contact_name}'."
    else:
        salutation = f"Use a standard salutation in {language} addressed to the {festival.festival_name} organizers."

    # Build artist identity section
    artist_identity = (
        f"{profile.first_name} {profile.last_name}".strip()
        or profile.artist_name
        or "the artist"
    )
    company_info = (
        f" representing {profile.company_name}" if profile.company_name else ""
    )

    # Build performances section with details
    # if len(performances) == 1:
    performance = performance_objects[0]
    performance_intro = f'your show "{performance.performance_title}"'
    performances_details = f"""
Performance Details:
- Title: {performance.performance_title}
- Type: {performance.get_performance_type_display() if performance.performance_type else "Not specified"}
- Genres: {", ".join([dict(Performance.GENRES).get(g, g) for g in performance.genres]) if performance.genres else "Not specified"}
- Duration: {performance.length if performance.length else "Not specified"}
- Short Description: {performance.short_description if performance.short_description else "Not available"}
"""
    #     else:
    #         performance_intro = "your performances"
    #         performances_list = []
    #         for perf in performances:
    #             perf_details = f"""
    #   * "{perf.performance_title}"
    #     - Type: {perf.get_performance_type_display() if perf.performance_type else "Not specified"}
    #     - Genres: {", ".join([dict(Performance.GENRES).get(g, g) for g in perf.genres]) if perf.genres else "Not specified"}
    #     - Duration: {perf.length if perf.length else "Not specified"}
    #     - Description: {perf.short_description if perf.short_description else "Not available"}
    # """
    # performances_list.append(perf_details)
    # performances_details = "\nPerformances Details:" + "".join(performances_list)

    # Build contact information
    contact_info = []
    if profile.email:
        contact_info.append(f"Email: {profile.email}")
    if profile.personal_website:
        contact_info.append(f"Website: {profile.personal_website}")
    contact_section = (
        "\n- ".join(contact_info)
        if contact_info
        else "Email: [your email]\nPhone: [your phone]"
    )

    # Build social media section (optional to mention if relevant)
    social_links = []
    if profile.instagram_profile:
        social_links.append(f"Instagram: {profile.instagram_profile}")
    if profile.facebook_profile:
        social_links.append(f"Facebook: {profile.facebook_profile}")
    if profile.youtube_profile:
        social_links.append(f"YouTube: {profile.youtube_profile}")
    social_section = "\n- ".join(social_links) if social_links else ""

    # The full prompt with instructions to return only the email content
    prompt = f"""
You are {artist_identity}{company_info}, a performer seeking to apply to various festivals with {performance_intro}.

Generate ONLY the plain text email content (no additional messages) in {language}. 
IMPORTANT: Use the STANDARD written form of the language, NOT regional dialects or colloquial variations.
Do not include a subject line.

Artist Profile:
- Name: {artist_identity}
{f"- Company: {profile.company_name}" if profile.company_name else ""}
{f"- Location: {profile.location}" if profile.location else ""}
{f"- Nationality: {profile.nationality}" if profile.nationality else ""}
{f"- Website: {profile.personal_website}" if profile.personal_website else ""}

{performances_details}

Festival Details:
- Festival Name: {festival.festival_name}
- Festival Type: {festival.festival_type}
- Description: {festival.description}
- Contact Person: {contact_name}
- Contact Email: {festival.contact_email}

Email Requirements:
- Salutation: {salutation}
- Introduction: Briefly introduce yourself as {artist_identity} and mention your background/experience (1-2 sentences). 
  This should come immediately after the salutation and before discussing the performances.
- Body: Explain why {performance_intro} {"is" if len(performances) == 1 else "are"} a great fit for this festival, using the festival description as your main reference.
  Mention unique aspects of the performance(s) and how {"it aligns" if len(performances) == 1 else "they align"} with the festival's theme and audience.
  Use the performance details provided above to create a compelling pitch. Keep the body concise (max 500 characters).
- Closing: Express enthusiasm and provide contact information using HTML anchor tags for clickable links:
  Email: {profile.email}
  {f"Website: <a href='{profile.personal_website}'>{profile.personal_website}</a>" if profile.personal_website else ""}
  {f"Instagram: <a href='{profile.instagram_profile}'>{profile.instagram_profile}</a>" if profile.instagram_profile else ""}
  {f"Facebook: <a href='{profile.facebook_profile}'>{profile.facebook_profile}</a>" if profile.facebook_profile else ""}
  {f"YouTube: <a href='{profile.youtube_profile}'>{profile.youtube_profile}</a>" if profile.youtube_profile else ""}

Response Format Instructions:
Return ONLY the email HTML content with <br> tags for line breaks and <a> tags for links. 
Do not add any preamble message, notes, or formatting indicators. 
The response should begin immediately with the salutation.

Email Structure:
1. Salutation (e.g., "Dear [Name],")
2. Brief self-introduction (1-2 sentences about who you are)
3. Main pitch about the performance(s) and festival fit
4. Closing with enthusiasm
5. Contact information with clickable links
6. Sign-off (e.g., "Best regards," or equivalent in the target language)
"""
    return prompt.strip()
