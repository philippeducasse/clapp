from typing import List, Optional

from mistralai import ConversationResponse, TextChunk

from organisations.models import Organisation
from performances.models import Performance
from profiles.models import Profile


def _format_contacts_for_prompt(organisation: Organisation) -> str:
    """Format organisation contacts for display in prompt."""
    contacts_list = []
    for contact in organisation.contacts.all():
        contact_str = f"{contact.email}"
        if contact.name:
            contact_str = f"{contact.name} ({contact.email})"
        if contact.role:
            contact_str += f" - {contact.role}"
        contacts_list.append(contact_str)
    return "; ".join(contacts_list) if contacts_list else "No contacts"


def _build_enrich_prompt(
    organisation: Organisation,
    search_results: Optional[str],
    org_type_display: str,
    current_record_fields: str,
    output_keys: str,
    type_field_section: str,
    required_json_example: str,
) -> str:
    """
    Build enrichment prompt with shared structure and type-specific content.

    Args:
        organisation: The organisation to enrich
        search_results: Web search snippets
        org_type_display: Display name (e.g., "festival", "venue", "residency")
        current_record_fields: The CURRENT RECORD section content
        output_keys: The exact output keys required
        type_field_section: Type-specific recognition hints section (can be empty)
        required_json_example: Example JSON output for this type
    """
    sr = search_results or "No search results provided."

    prompt = f"""
    You are enriching {org_type_display} data for a cultural booking app.

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
      {output_keys}
    - contacts should be an array of objects with: email (required), name (optional), role (optional).
      **IMPORTANT: Only include contacts if you find actual email addresses in the search results.
      If no email addresses are found, return an empty array []. Do NOT invent or guess email addresses.**

    CURRENT RECORD
    {current_record_fields}

    WEB SEARCH SNIPPETS (include URLs if you have them)
    {sr}
{type_field_section}
    REQUIRED JSON SHAPE (example, syntactically correct — values are illustrative):
    {required_json_example}
    """
    return prompt


def generate_application_mail_prompt(
    organisation: Organisation,
    profile: Profile,
    performances: List[Performance],
    language: str,
    length: int,
) -> str:
    """Generate email application prompt for any organisation type."""
    primary_contact = organisation.contacts.first()
    contact_name = None
    contact_emails = []
    if primary_contact:
        if primary_contact.name and primary_contact.name.strip().lower() != "nan":
            contact_name = primary_contact.name.strip()
        contact_emails = [c.email for c in organisation.contacts.all()]

    if contact_name:
        salutation = (
            f"Use a standard salutation in {language} and include the name '{contact_name}'."
        )
    else:
        salutation = f"Use a standard salutation using gender neutral language in {language} addressed to the {organisation.name} organizers."

    length_guidelines = {
        1: {
            "description": "VERY SHORT",
            "max_words": 50,
            "paragraphs": "2-3 short paragraphs",
            "detail": "Keep it extremely brief and to the point.",
        },
        2: {
            "description": "SHORT",
            "max_words": 100,
            "paragraphs": "3-4 paragraphs",
            "detail": "Be concise and focus only on key points.",
        },
        3: {
            "description": "MEDIUM",
            "max_words": 150,
            "paragraphs": "4-5 paragraphs",
            "detail": "Provide moderate detail about the performance.",
        },
        4: {
            "description": "LONG",
            "max_words": 200,
            "paragraphs": "5-6 paragraphs",
            "detail": "Include more details and descriptions.",
        },
        5: {
            "description": "VERY LONG",
            "max_words": 300,
            "paragraphs": "6-7 paragraphs",
            "detail": "Provide comprehensive details and context.",
        },
    }
    length_config = length_guidelines.get(length, length_guidelines[3])
    max_words = length_config["max_words"]

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
            performance.long_description if performance.long_description else "Not available"
        }
            - Dossier: {
            performance.dossiers.first() if performance.dossiers.exists() else "Not available"
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
                perf.get_performance_type_display() if perf.performance_type else "Not specified"
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
                trailers.append(f'<a href="{perf.trailer}">{perf.performance_title} trailer</a>')
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

    contact_lines = []
    if profile.email:
        contact_lines.append(f"<a href='mailto:{profile.email}'>{profile.email}</a>")
    if profile.personal_website:
        contact_lines.append(f"<a href='{profile.personal_website}'>{profile.personal_website}</a>")

    social_links = []
    if profile.instagram_profile:
        social_links.append(f"<a href='{profile.instagram_profile}'>Instagram</a>")
    if profile.facebook_profile:
        social_links.append(f"<a href='{profile.facebook_profile}'>Facebook</a>")
    if profile.youtube_profile:
        social_links.append(f"<a href='{profile.youtube_profile}'>YouTube</a>")
    social_line = " & ".join(social_links) if social_links else ""

    signature = "<br><br>"
    if profile.company_name:
        signature += f"{profile.company_name}<br>"
    if profile.phone:
        signature += f"{profile.phone}<br>"
    signature += "<br>".join(contact_lines)
    if social_line:
        signature += f"<br>{social_line}"

    prompt = f"""
        ⚠️ CRITICAL OUTPUT FORMAT - READ THIS FIRST ⚠️
        Return ONLY the email HTML content - NO explanations, NO preamble.
        REQUIRED: Use ONLY <br><br> tags for ALL paragraph breaks.
        REQUIRED: Use ONLY <a> tags for links. Example: <a href="url">text</a>
        FORBIDDEN: Do NOT use \\n, newline characters, or line breaks of any kind.
        FORBIDDEN: Do NOT use asterisks (* or **) for emphasis.
        Start immediately with the salutation. No preamble.

        ⚠️ CRITICAL LENGTH REQUIREMENT - READ THIS SECOND ⚠️
        MAXIMUM WORDS: {max_words}
        TARGET LENGTH: {length_config["description"]} ({length_config["paragraphs"]})
        INSTRUCTION: {length_config["detail"]}

        DO NOT EXCEED {max_words} WORDS. Count your words carefully. If you go over, the email will be rejected.

        You are {profile.company_name}, a performer seeking to apply to various organisations with {performance_intro}.

        Generate ONLY the plain text email content (no additional messages) in {language}.
        IMPORTANT: Use the STANDARD written form of the language, NOT regional dialects or colloquial variations.
        Do not include a subject line.

        ⚠️ LENGTH REMINDER: Your response must be {length_config["description"]} - MAXIMUM {max_words} WORDS TOTAL
        {length_config["detail"]}
        
        Artist Profile:
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
        - Introduction: BRIEFLY introduce yourself. Keep it SHORT - just 1-2 sentences. Say that you would like to propose {performance_intro} for the next edition.
        - Body: Make the text playful and informal but CONCISE. Explain why {performance_intro} {"is" if len(performances) == 1 else "are"} a great fit for this organisation.
        Focus on ONE or TWO key points that align with the organisation's description. Do NOT go into exhaustive detail about the performance.
        Remember: You must stay within {max_words} words TOTAL for the ENTIRE email.
    
        - Closing: {trailer_instruction} {dossier_instruction}
        Express enthusiasm in awaiting the response and openness to answer any questions or provide more information. Provide contact information using this format: {signature}


        Email Structure (separate each section with <br><br>):
        1. Salutation (e.g., "Dear [Name],")
        2. Brief self-introduction (1-2 sentences about who you are)
        3. Main pitch about the performance(s) and organisation fit
        4. Closing with enthusiasm
        5. Sign-off (e.g., "Best regards," or equivalent in the target language)
        6. {signature}

        🚨 FINAL REMINDER BEFORE YOU START WRITING 🚨
        MAXIMUM WORDS: {max_words}
        COUNT YOUR WORDS AS YOU WRITE. STOP IMMEDIATELY WHEN YOU REACH {max_words} WORDS.
        Be selective with details. Prioritize impact over completeness.
        {length_config["detail"]}

        EXAMPLE OUTPUT FORMAT:

        {performances[0].email_prompt if len(performances) == 1 else "<br><br>".join([f"For {p.performance_title}:<br><br>" + p.email_prompt for p in performances if hasattr(p, "email_prompt") and p.email_prompt])}
        """
    return prompt.strip()


def format_email(message: str):
    return message.replace("\n", "<br>").replace("*", "").replace("—", ",").replace("–", ",")


def extract_search_results(search_results: ConversationResponse):
    content = next((o for o in search_results.outputs if o.type == "message.output"), None)
    # print("content", content)

    chunks = getattr(content, "content", [])

    parsed_text = " ".join(chunk.text for chunk in chunks if isinstance(chunk, TextChunk))

    return parsed_text
