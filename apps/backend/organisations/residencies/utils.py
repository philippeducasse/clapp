from typing import Any, Optional

from organisations.residencies.models import Residency
from organisations.services import _build_enrich_prompt, _format_contacts_for_prompt


def generate_enrich_prompt(residency: Residency, search_results: Optional[str]) -> str:
    """Generate residency-specific enrichment prompt."""
    application_types = Residency.APPLICATION_TYPE

    def nv(x: Any) -> str:
        return "" if x is None else str(x)

    app_types_str = ", ".join([value for (value, _) in application_types])

    contacts_display = _format_contacts_for_prompt(residency)

    current_record_fields = f"""country: {nv(residency.country)}
town: {nv(residency.town)}
approximate_date: {nv(residency.approximate_date)}
start_date: {nv(residency.start_date)}
end_date: {nv(residency.end_date)}
website_url: {nv(residency.website_url)}
description: {nv(residency.description)}
contacts: {contacts_display}
application_date_start: {nv(residency.application_date_start)}
application_date_end: {nv(residency.application_date_end)}
application_type: {nv(residency.application_type)}
comments: {nv(residency.comments)}"""

    output_keys = """country, town, approximate_date, start_date, end_date, website_url,
description,
application_date_start, application_date_end, application_type,
contacts, sources, updated_fields"""

    type_field_section = f"""
    DATE RULES
    - If a single text gives a **date range** (e.g., "12–15 July 2026"), set:
      - start_date = first day in ISO (YYYY-MM-DD)
      - end_date   = last day in ISO (YYYY-MM-DD)
      - also update approximate_date (e.g., "mid July" or "late June–early July" if it spans months)
    - Day 1–10 → "early <Month>"
    - Day 11–20 → "mid <Month>"
    - Day 21–31 → "late <Month>"
    - If only month/year is known, leave start_date/end_date empty strings and set a clear approximate_date.

    RECOGNITION HINTS
    application_type (choose one: {app_types_str})

    Decision order (apply the first rule that matches):
    1) FORM — there is an application portal or form (any language; may be Google Form, Typeform, Jotform; or an obvious
     "apply/inscription/anmeldung/postuler/solicitar" button or dedicated application page).
    2) INVITATION_ONLY — the residency is by invitation only (any language).
    3) EMAIL — the page asks to send proposals/applications by email OR mentions applying via email.
    4) FALLBACK to EMAIL — if none of the above are present BUT a contact email is present on the page or the current
     record has a non-empty contact email, classify as EMAIL.
    5) OPEN_CALL — if explicitly labeled as an open call for applications.
    6) OTHER - if the application method is specifically mentioned and is neither FORM, INVITATION_ONLY, EMAIL, nor OPEN_CALL.
     Add details about the application process in the comments field.
    7) UNKNOWN — only if there is no form, no invitation-only statement, and **no** email available at all.

    Notes:
    - Treat hints as concepts, not exact strings (any language).
    """

    required_json_example = """{{
      "country": "Belgium",
      "town": "Brussels",
      "approximate_date": "mid September",
      "start_date": "2026-09-15",
      "end_date": "2026-10-15",
      "website_url": "https://example-residency.be",
      "description": "A selective artist residency program for emerging performers.",
      "application_date_start": "2026-04-01",
      "application_date_end": "2026-06-30",
      "application_type": "FORM",
      "contacts": [
        {{"email": "info@example-residency.be"}},
        {{"email": "coordinator@example-residency.be", "name": "Alice Johnson", "role": "Residency Coordinator"}},
      ],
      "comments": "this is a comment."
    }}"""

    return _build_enrich_prompt(
        residency,
        search_results,
        "residency",
        current_record_fields,
        output_keys,
        type_field_section,
        required_json_example,
    )
