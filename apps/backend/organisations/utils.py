from typing import Dict, Any, List, Optional
from organisations.models import Organisation
from profiles.models import Profile
from performances.models import Performance
import json
import re


def generate_enrich_prompt(
    organisation: Organisation, search_results: Optional[str]
) -> str:
    """Generate enrichment prompt for any organisation type."""
    sr = search_results or "No search results provided."

    def nv(x: Any) -> str:
        return "" if x is None else str(x)

    # Format contacts for the prompt
    contacts_list = []
    for contact in organisation.contacts.all():
        contact_str = f"{contact.email}"
        if contact.name:
            contact_str = f"{contact.name} ({contact.email})"
        if contact.role:
            contact_str += f" - {contact.role}"
        contacts_list.append(contact_str)
    contacts_display = "; ".join(contacts_list) if contacts_list else "No contacts"

    prompt = f"""
    You are enriching organisation data for a cultural booking app.

    TASK
    - Read the current record and the web search snippets.
    - If the web snippets provide better or newer information for a field, **you must update it**.
    - If a field is missing in the snippets, keep the existing value.
    - Translate non-English data to English.
    - Normalize dates to ISO 8601 as strings: "YYYY-MM-DD".

    SOURCES & CONFLICTS
    - Prefer official organisation website > reputable cultural listings > news > blogs.
    - If sources conflict, pick the **most recent official source**.

    OUTPUT FORMAT
    - Return **only** a single JSON object, no prose.
    - Valid JSON. No comments. No trailing commas.
    - Exactly these keys (strings):
      country, town, website_url, description,
      contacts, sources, updated_fields
    - contacts should be an array of objects with: email (required), name (optional), role (optional).
        Provide at least one contact with an email.

    CURRENT RECORD
    country: {nv(organisation.country)}
    town: {nv(organisation.town)}
    website_url: {nv(organisation.website_url)}
    description: {nv(organisation.description)}
    contacts: {contacts_display}
    comments: {nv(organisation.comments)}

    WEB SEARCH SNIPPETS (include URLs if you have them)
    {sr}

    REQUIRED JSON SHAPE (example, syntactically correct — values are illustrative):
    {{
      "country": "Belgium",
      "town": "Brussels",
      "website_url": "https://example.be",
      "description": "A cultural organisation.",
      "contacts": [
        {{"email": "info@example.be"}},
        {{"email": "programming@example.be", "name": "John Smith", "role": "Programming Manager"}},
      ],
      "comments": "this is a comment."
    }}
    """
    return prompt


def extract_fields_from_llm(llm_response: str) -> Dict[str, Any]:
    """Extract fields from LLM JSON response."""
    json_str: str = re.sub(r"```json\s*|\s*```", "", llm_response).strip()
    try:
        response_data: Dict[str, Any] = json.loads(json_str)
        return response_data
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the JSON response: {e}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def clean_organisation_data(organisation: Organisation) -> None:
    """Clean and normalize organisation data."""

    def clean_nan(value: str) -> str:
        return "" if str(value).strip().lower() == "nan" else str(value).strip()

    if organisation.name:
        organisation.name = organisation.name.title()

    if organisation.town:
        organisation.town = clean_nan(organisation.town.title())

    if organisation.country:
        organisation.country = clean_nan(organisation.country.title())

    if organisation.comments:
        organisation.comments = clean_nan(organisation.comments.strip().lower())

    if organisation.website_url:
        url: str = organisation.website_url.strip()
        if not url.startswith("http"):
            url = "https://" + url
        organisation.website_url = url.lower()

    if organisation.description:
        desc: str = organisation.description.strip()
        if not desc.endswith("."):
            desc += "."
        organisation.description = desc


def generate_application_mail_prompt(
    organisation: Organisation, profile: Profile, performances: List[Performance]
) -> str:
    """Generate email application prompt for any organisation type."""
    # Determine language for email - default to English if country not specified
    COUNTRY_LANGUAGES = {
        "france": "French",
        "italy": "Italian",
        "germany": "German",
        "spain": "Spanish",
        "austria": "German",
        "switzerland": "German",
    }

    SUPPORTED_LANGUAGES = {"English", "French", "Italian", "German", "Spanish"}

    if organisation.country:
        detected_language = COUNTRY_LANGUAGES.get(
            organisation.country.lower(), "English"
        )
        language = (
            detected_language if detected_language in SUPPORTED_LANGUAGES else "English"
        )
    else:
        language = "English"

    # Determine salutation based on primary contact person
    primary_contact = organisation.contacts.first()
    contact_name = None
    contact_emails = []

    if primary_contact:
        if primary_contact.name and primary_contact.name.strip().lower() != "nan":
            contact_name = primary_contact.name.strip()
        contact_emails = [c.email for c in organisation.contacts.all()]

    if contact_name:
        salutation = f"Use a standard salutation in {language} and include the name '{contact_name}'."
    else:
        salutation = f"Use a standard salutation using gender neutral language in {language} addressed to the {organisation.name} organizers."

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
    if len(performances) == 1:
        performance = performances[0]
        performance_intro = f'your show "{performance.performance_title}"'
        performances_details = f"""
            Performance Details:
            - Title: {performance.performance_title}
            - Trailer: {performance.trailer if performance.trailer else "Not available"}
            - Type: {
            performance.get_performance_type_display()
            if performance.performance_type
            else "Not specified"
        }
            - Genres: {
            ", ".join([dict(Performance.GENRES).get(g, g) for g in performance.genres])
            if performance.genres
            else "Not specified"
        }
            - Duration: {performance.length if performance.length else "Not specified"}
            - Description: {
            performance.long_description
            if performance.long_description
            else "Not available"
        }
            - Dossier: {
            performance.dossiers.first()
            if performance.dossiers.exists()
            else "Not available"
        }
            """

        trailer_instruction = f'If the trailer is available ({performance.trailer}), add a link to it following this format: Here you can see the <a href="{performance.trailer}">trailer</a>, making sure the link is well separated from any other text and is clearly visible.'
        dossier_instruction = f"If a dossier is available ({performance.dossiers.first() if performance.dossiers.exists() else 'none'}), say that the dossier is attached and that all further information and photos are there."

    else:
        performance_intro = "your performances"
        performances_list = []
        trailers = []
        has_dossiers = False

        for perf in performances:
            perf_details = f"""
                * "{perf.performance_title}"
                    - Type: {
                perf.get_performance_type_display()
                if perf.performance_type
                else "Not specified"
            }
                    - Genres: {
                ", ".join([dict(Performance.GENRES).get(g, g) for g in perf.genres])
                if perf.genres
                else "Not specified"
            }
                    - Duration: {perf.length if perf.length else "Not specified"}
                    - Description: {
                perf.long_description if perf.long_description else "Not available"
            }
                    - Trailer: {perf.trailer if perf.trailer else "Not available"}
                    - Dossier: {
                perf.dossiers.first() if perf.dossiers.exists() else "Not available"
            }
                """
            performances_list.append(perf_details)

            if perf.trailer:
                trailers.append(
                    f'<a href="{perf.trailer}">{perf.performance_title} trailer</a>'
                )
            if perf.dossiers.exists():
                has_dossiers = True

        performances_details = "\nPerformances Details:" + "".join(performances_list)

        if trailers:
            trailer_instruction = f"Add links to the available trailers: {', '.join(trailers)}, making sure the links are well separated from any other text and clearly visible."
        else:
            trailer_instruction = "No trailers are available to link."

        if has_dossiers:
            dossier_instruction = "Say that the dossiers are attached and that all further information and photos are there."
        else:
            dossier_instruction = "No dossiers to mention."

    # Build contact information
    contact_lines = []
    if profile.email:
        contact_lines.append(f"<a href='mailto:{profile.email}'>{profile.email}</a>")
    if profile.personal_website:
        contact_lines.append(
            f"<a href='{profile.personal_website}'>{profile.personal_website}</a>"
        )

    # Build social media line
    social_links = []
    if profile.instagram_profile:
        social_links.append(f"<a href='{profile.instagram_profile}'>Instagram</a>")
    if profile.facebook_profile:
        social_links.append(f"<a href='{profile.facebook_profile}'>Facebook</a>")
    if profile.youtube_profile:
        social_links.append(f"<a href='{profile.youtube_profile}'>YouTube</a>")

    social_line = " & ".join(social_links) if social_links else ""

    # Format signature
    signature = f"{artist_identity}<br><br>"
    if profile.company_name:
        signature += f"{profile.company_name}<br>"
    if profile.phone:
        signature += f"{profile.phone}<br>"
    signature += "<br>".join(contact_lines)
    if social_line:
        signature += f"<br>{social_line}"

    # The full prompt
    prompt = f"""
        You are {artist_identity}{company_info}, a performer seeking to apply to various organisations with {performance_intro}.

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

        Organisation Details:
        - Name: {organisation.name}
        - Description: {organisation.description}
        - Contact Person: {contact_name if contact_name else "Not specified"}
        - Contact Emails: {", ".join(contact_emails) if contact_emails else "Not specified"}

        Email Requirements:
        - Salutation: {salutation}
        - Introduction: Briefly introduce yourself as {artist_identity} and mention your background/experience (1-2 sentences).
        This should come immediately after the salutation and before discussing the performances.
        - Body: Make the text very playful and informal. Explain why {performance_intro} {"is" if len(performances) == 1 else "are"} a great fit for this organisation, using the organisation description as your main reference.
        Mention unique aspects of the performance(s) and how {"it aligns" if len(performances) == 1 else "they align"} with the organisation's theme and audience.
        Use the performance details provided above to create a compelling pitch. Keep the body concise (max 500 characters).

        Example body:
            "Ah Bah Bravo! is a magical mix of world-class juggling — from butt and nose hooping to spinning a flaming staff with my feet while in a handstand!
            it's a show full of imagination, laughter, and wonder, perfectly suited to the lively and diverse spirit of your organisation.
            Audiences are invited to dream, share, and rediscover the carefree joy of being a child again".
        - Closing: {trailer_instruction} {dossier_instruction}
        Express enthusiasm in awaiting the response and openness to answer any questions or provide more information. Provide contact information using this format: {signature}

        Response Format Instructions:
        Return ONLY the email HTML content.
        CRITICAL: Use <br><br> tags for paragraph breaks (empty lines between sections).
        Use <a> tags for links.
        Do NOT use newlines, \\n characters, or any other line break methods.
        Do NOT use asterisks (*) for emphasis (*like this*).
        Do not add any preamble message, notes, or formatting indicators.
        The response should begin immediately with the salutation.

        Email Structure (separate each section with <br><br>):
        1. Salutation (e.g., "Dear [Name],")
        2. Brief self-introduction (1-2 sentences about who you are)
        3. Main pitch about the performance(s) and organisation fit
        4. Closing with enthusiasm
        5. Sign-off (e.g., "Best regards," or equivalent in the target language)
        6. {signature}

        EXAMPLE OUTPUT FORMAT:

        Dear Team,<br><br>I am Philippe Ducasse, a circus artist based in Berlin with a passion for blending juggling, mime, and clowning into vibrant, family-friendly performances.<br><br>"Ah Bah Bravo!" is a whirlwind of acrobatic butt hullahooping, flaming staff juggling (while handstanding!), and playful storytelling. It's a joyful celebration of childhood wonder, inviting audiences to laugh, dream, and embrace the magic of the moment.<br><br>Here you can see the <a href="https://example.com/trailer">trailer</a><br><br>The dossier is attached with full details, photos, and technical requirements. I'd love to bring this show and can't wait to hear your thoughts—feel free to reach out for any questions!<br><br>Best regards,<br><br>Philippe Ducasse<br>+4915203723753<br>info@philippeducasse.com<br>https://www.philippeducasse.com<br>Instagram & Facebook

        """
    return prompt.strip()
