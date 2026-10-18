"""extract_leads: list the organisations named on a calendar or listing page."""

from pydantic import Field

from discovery.prompts import (
    LLMOutput,
    ABOUT_CLAPP,
    UNTRUSTED_CONTENT,
    Message,
    OrgType,
    clip,
    page_block,
)
from discovery.tools.links import Link


class LeadOut(LLMOutput):
    name: str = Field(description="Name of the festival, residency or venue, as on the page.")
    org_type: OrgType
    town: str = ""
    country: str = Field(default="", description="English country name.")
    dates: str = Field(default="", description="Dates as written on the page, if any.")
    link_number: int | None = Field(
        default=None,
        description="Number of the link (from the numbered list) pointing to this organisation, "
        "if there is one.",
    )


class LeadList(LLMOutput):
    leads: list[LeadOut] = Field(default_factory=list)


SYSTEM = f"""You read web pages for clapp's research. {ABOUT_CLAPP}

The page is {{page_kind}}. List every organisation on it that the goal asks for
({{org_types}}){{countries}}. For each one give:
- name: the organisation's name, without the year or edition number.
- org_type: FESTIVAL, RESIDENCY or VENUE.
- town and country (English country name), when the page says or the name makes it obvious.
- dates: as written on the page.
- link_number: the number of the link to the organisation, from the numbered list, when there is
  one. Never invent a link.

Leave out private events, schools, companies, shops, the artist's own events, and anything the
goal isn't about. List each organisation once, even if it appears on several dates.

{UNTRUSTED_CONTENT}"""

PAGE_KINDS = {
    "calendar": "an artist's calendar (tour dates): the organisations are the places it played",
    "listing": "a list of organisations or events",
}


def messages(
    goal: str,
    org_types: list[str],
    countries: list[str],
    page_kind: str,
    url: str,
    title: str,
    text: str,
    links: list[Link],
) -> list[Message]:
    where = f", in {', '.join(countries)}" if countries else ""
    numbered = "\n".join(
        f"{n}. {clip(link.text, 80) or '(no text)'} — {link.url}"
        for n, link in enumerate(links, start=1)
    )
    system = SYSTEM.format(
        page_kind=PAGE_KINDS.get(page_kind, PAGE_KINDS["listing"]),
        org_types=", ".join(org_types),
        countries=where,
    )
    return [
        ("system", system),
        (
            "human",
            f"Goal: {goal}\n\n{page_block(url, title, text, 15000)}\n\n"
            f"Numbered links on the page:\n<page>\n{numbered or '(none)'}\n</page>",
        ),
    ]
