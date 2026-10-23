"""extract_org: read an organisation's own pages into a structured candidate.

The date and application-type rules are copied from the backend's enrichment prompts
(`organisations/festivals/utils.py`, `residencies/utils.py`, `venues/utils.py`), so candidates
come out in the same formats as `enrich()` produces. Keep them in sync.
"""

from pydantic import Field

from discovery.prompts import (
    ABOUT_CLAPP,
    FESTIVAL_APPLICATION_TYPES,
    FESTIVAL_TYPES,
    RESIDENCY_APPLICATION_TYPES,
    UNTRUSTED_CONTENT,
    VENUE_TYPES,
    LLMOutput,
    Message,
    OrgType,
    page_block,
)


class ContactOut(LLMOutput):
    email: str = Field(description="An email address copied verbatim from the pages. Never guess.")
    name: str = ""
    role: str = ""


class OrgExtraction(LLMOutput):
    name: str = Field(description="Official name, without the year or edition number.")
    org_type: OrgType
    country: str = Field(default="", description="English country name.")
    town: str = ""
    description: str = Field(default="", description="Two or three sentences, in English.")
    subtype: str = Field(default="", description="festival_type or venue_type, from the list.")
    application_type: str = ""
    application_url: str = Field(
        default="", description="URL of the application form or open call, copied from the pages."
    )
    start_date: str = Field(default="", description="YYYY-MM-DD, next or latest edition.")
    end_date: str = Field(default="", description="YYYY-MM-DD.")
    estimated_start_date: str = Field(default="", description="YYYY-MM-DD, festivals only.")
    approximate_date: str = Field(default="", description='e.g. "mid July".')
    application_date_start: str = ""
    application_date_end: str = ""
    contacts: list[ContactOut] = Field(
        default_factory=list, description="At most 3, most useful for applying first."
    )
    relevance_reason: str = Field(
        default="", description="One sentence: why this organisation fits the goal."
    )


SYSTEM = f"""You turn an organisation's web pages into a record for clapp. {ABOUT_CLAPP}

TASK
- Read the pages of the organisation below and fill in the record.
- Translate non-English data to English (description, roles). Keep names as they are.
- Normalize dates to ISO 8601 strings: "YYYY-MM-DD". Use the next edition if dates for it are
  published, otherwise the latest one. Leave a field empty when the pages don't say.
- Use the hints from the page where the organisation was found when the pages agree or are
  silent, but prefer the organisation's own pages.

CONTACTS
- Only include contacts whose email address appears in the pages. If there is none, return an
  empty list. Do NOT invent or guess email addresses.
- Return at most 3 contacts, most useful first, even if the pages list many more people.
  Prefer, in this order: programming / booking / artistic direction / applications or open
  call; then a general address (info@, contact@). Skip press, ticketing, shop, jobs, volunteers,
  accounting, technical staff and webmaster unless there is nothing else.
- application_url must be a URL that appears in the pages.

{{type_rules}}

{UNTRUSTED_CONTENT}"""

FESTIVAL_RULES = f"""APPROXIMATE DATE RULES
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
- Leave blank only if no date information exists at all

RECOGNITION HINTS
subtype is the festival_type (choose one: {", ".join(FESTIVAL_TYPES)})
application_type (choose one: {", ".join(FESTIVAL_APPLICATION_TYPES)})

Decision order (apply the first rule that matches; do not skip ahead):
1) FORM — there is an application portal or form (any language; may be Google Form, Typeform,
   Jotform; or an obvious "apply/inscription/anmeldung/postuler/solicitar" button or dedicated
   application page).
2) INVITATION_ONLY — the event is curated/by invitation only (any language).
3) EMAIL — the page asks to send proposals/submissions by email OR mentions applying via email.
4) FALLBACK to EMAIL — if none of the above are present BUT a contact email is present on the
   pages, classify as EMAIL.
5) OTHER - if the application method is specifically mentioned and is neither FORM,
   INVITATION_ONLY, nor EMAIL.
6) UNKNOWN — only if there is no form, no invitation-only statement, and **no** email available
   at all.

Notes:
- Treat hints as concepts, not exact strings (any language).
- festival_type: look for domain terms: street festival, circus, music, theatre, dance, puppet,
  juggling convention."""

RESIDENCY_RULES = f"""DATE RULES
- If a single text gives a **date range** (e.g., "12–15 July 2026"), set:
  - start_date = first day in ISO (YYYY-MM-DD)
  - end_date   = last day in ISO (YYYY-MM-DD)
  - also set approximate_date (e.g., "mid July" or "late June–early July" if it spans months)
- Day 1–10 → "early <Month>"
- Day 11–20 → "mid <Month>"
- Day 21–31 → "late <Month>"
- If only month/year is known, leave start_date/end_date empty and set a clear approximate_date.
- application_date_start / application_date_end: when the call for applications opens and
  closes (YYYY-MM-DD when known).
- Leave subtype and estimated_start_date empty.

RECOGNITION HINTS
application_type (choose one: {", ".join(RESIDENCY_APPLICATION_TYPES)})

Decision order (apply the first rule that matches):
1) FORM — there is an application portal or form (any language; may be Google Form, Typeform,
   Jotform; or an obvious "apply/inscription/anmeldung/postuler/solicitar" button or dedicated
   application page).
2) INVITATION_ONLY — the residency is by invitation only (any language).
3) EMAIL — the page asks to send proposals/applications by email OR mentions applying via email.
4) FALLBACK to EMAIL — if none of the above are present BUT a contact email is present on the
   pages, classify as EMAIL.
5) OPEN_CALL — if explicitly labeled as an open call for applications.
6) OTHER - if the application method is specifically mentioned and is neither FORM,
   INVITATION_ONLY, EMAIL, nor OPEN_CALL.
7) UNKNOWN — only if there is no form, no invitation-only statement, and **no** email available
   at all.

Notes:
- Treat hints as concepts, not exact strings (any language)."""

VENUE_RULES = f"""RECOGNITION HINTS
subtype is the venue_type (choose one from: {", ".join(VENUE_TYPES)})
- Look for domain terms: theatre, opera house, concert hall, dance studio, music venue,
  circus tent, performance space, art gallery, outdoor stage, puppet theatre, circus space.
- If type is not clear, use "UNKNOWN".
- Leave all date fields and application_type empty."""

TYPE_RULES: dict[str, str] = {
    "FESTIVAL": FESTIVAL_RULES,
    "RESIDENCY": RESIDENCY_RULES,
    "VENUE": VENUE_RULES,
}


def messages(
    goal: str,
    org_type: str,
    lead_hints: str,
    pages: list[tuple[str, str, str, str]],
    today: str,
) -> list[Message]:
    """`pages`: (kind, url, title, text) of the organisation's pages, home page first."""
    per_page = max(2000, 18000 // max(1, len(pages)))
    blocks = "\n\n".join(
        page_block(url, title, text, per_page, label=kind) for kind, url, title, text in pages
    )
    return [
        ("system", SYSTEM.format(type_rules=TYPE_RULES[org_type])),
        (
            "human",
            f"Goal: {goal}\nToday: {today}\nExpected type: {org_type}\n"
            f"Found as: {lead_hints}\n\n{blocks}",
        ),
    ]
