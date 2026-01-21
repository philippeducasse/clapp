from typing import Any, Optional

from organisations.festivals.models import Festival
from organisations.services import _build_enrich_prompt, _format_contacts_for_prompt


def generate_enrich_prompt(festival: Festival, search_results: Optional[str]) -> str:
    """Generate festival-specific enrichment prompt."""
    festival_types = Festival.FESTIVAL_TYPES
    application_types = Festival.APPLICATION_TYPE

    def nv(x: Any) -> str:
        return "" if x is None else str(x)

    fest_types_str = ", ".join([value for (value, _) in festival_types])
    app_types_str = ", ".join([value for (value, _) in application_types])

    contacts_display = _format_contacts_for_prompt(festival)

    current_record_fields = f"""country: {nv(festival.country)}
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
comments: {nv(festival.comments)}"""

    output_keys = """country, town, approximate_date, start_date, end_date, website_url,
festival_type, description,
application_date_start, application_date_end, application_type,
contacts, sources, updated_fields"""

    type_field_section = f"""
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
    festival_type (choose one: from {fest_types_str})
    application_type (choose one: {app_types_str})

    Decision order (apply the first rule that matches; do not skip ahead):
    1) FORM — there is an application portal or form (any language; may be Google Form, Typeform, Jotform; or an obvious
     "apply/inscription/anmeldung/postuler/solicitar" button or dedicated application page).
    2) INVITATION_ONLY — the event is curated/by invitation only (any language).
    3) EMAIL — the page asks to send proposals/submissions by email OR mentions applying via email.
    4) FALLBACK to EMAIL — if none of the above are present BUT a contact email is present on the page or the current
     record has a non-empty contact_email, classify as EMAIL.
    5) OTHER - if the application method is specifically mentioned and is neither FORM, INVITATION_ONLY, nor EMAIL.
     Add details about the application process in the comments field.
    6) UNKNOWN — only if there is no form, no invitation-only statement, and **no** email available at all.

    Notes:
    - Treat hints as concepts, not exact strings (any language).
    - festival_type: look for domain terms: street festival, circus, music, theatre, dance, film, circus.
    """

    required_json_example = """{{
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
    }}"""

    return _build_enrich_prompt(
        festival,
        search_results,
        "festival",
        current_record_fields,
        output_keys,
        type_field_section,
        required_json_example,
    )
