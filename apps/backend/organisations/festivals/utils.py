from typing import Any, Optional

from organisations.festivals.models import Festival


def generate_enrich_prompt(festival: Festival, search_results: Optional[str]) -> str:
    festival_types = Festival.FESTIVAL_TYPES
    application_types = Festival.APPLICATION_TYPE

    sr = search_results or "No search results provided."

    # Small helpers to avoid 'None' textual noise in the prompt
    def nv(x: Any) -> str:
        return "" if x is None else str(x)

    fest_types_str = ", ".join([value for (value, _) in festival_types])
    app_types_str = ", ".join([value for (value, _) in application_types])

    # Format contacts for the prompt
    contacts_list = []
    for contact in festival.contacts.all():
        contact_str = f"{contact.email}"
        if contact.name:
            contact_str = f"{contact.name} ({contact.email})"
        if contact.role:
            contact_str += f" - {contact.role}"
        contacts_list.append(contact_str)
    contacts_display = "; ".join(contacts_list) if contacts_list else "No contacts"

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
      festival_type, description,
      application_date_start, application_date_end, application_type,
      contacts, sources, updated_fields
    - contacts should be an array of objects with: email (required), name (optional), role (optional). 
        Provide at least one contact with an email.

    CURRENT RECORD
    country: {nv(festival.country)}
    town: {nv(festival.town)}
    approximate_date: {nv(festival.approximate_date)}
    estimated_start_date: {nv(festival.estimated_start_date)}
    start_date: {nv(festival.start_date)}
    end_date: {nv(festival.end_date)}
    website_url: {nv(festival.website_url)}
    festival_type: {nv(festival.festival_type)}
    description: {nv(festival.description)}
    contacts: {contacts_display}
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

    ESTIMATED START DATE (for sorting):
    - If exact start_date is known, set estimated_start_date to the same value
    - If only approximate_date is available, convert to a date:
    * "early <Month>" → use day 5 of that month
    * "mid <Month>" → use day 15 of that month
    * "late <Month>" → use day 25 of that month
    * "late June–early July" → use June 25
    - Format: YYYY-MM-DD (e.g., 2025-08-15)
    - Leave blank only if no date information exists at all

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
      "application_date_start": "2026-05-01",
      "application_date_end": "2026-06-15",
      "application_type": "FORM",
      "contacts": [
        {{"email": "info@examplefest.be"}},
        {{"email": "programming@examplefest.be", "name": "John Smith", "role": "Programming Manager"}},
      ],
      "comments": "this is a comment."
    }}
    """
    return prompt
