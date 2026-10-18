"""classify_page: what kind of page is this, judged against the goal?"""

from typing import Literal

from pydantic import BaseModel, Field

from discovery.prompts import ABOUT_CLAPP, UNTRUSTED_CONTENT, Message, OrgType, page_block

PageKind = Literal["ARTIST_SITE", "ORG_SITE", "AGGREGATOR", "IRRELEVANT"]


class PageClassification(BaseModel):
    kind: PageKind
    lists_events: bool = Field(
        default=False,
        description="True if this page itself lists performance dates, festivals or venues.",
    )
    org_name: str = Field(default="", description="ORG_SITE only: the organisation's name.")
    org_type: OrgType | None = Field(default=None, description="ORG_SITE only.")
    country: str = Field(default="", description="ORG_SITE only: English country name.")
    town: str = Field(default="", description="ORG_SITE only.")
    reason: str = Field(default="", description="A few words explaining the choice.")


SYSTEM = f"""You sort web pages for clapp's research. {ABOUT_CLAPP}

Classify the page, judged against the research goal:
- ARTIST_SITE: the site of a performer or company (juggler, circus or street theatre company,
  musician…) that tours. Its calendar or tour dates show where it performed.
- ORG_SITE: the official site of one festival, artist residency or venue of a kind the goal
  asks for. Give its name, type, country (English) and town.
- AGGREGATOR: a page listing several festivals, residencies or venues (a directory, a network's
  members, an article listing festivals, an agenda of events).
- IRRELEVANT: anything else, or a site the goal isn't about.

Set lists_events when this page itself lists dates, festivals or venues.

{UNTRUSTED_CONTENT}"""


def messages(goal: str, url: str, title: str, text: str, link_texts: list[str]) -> list[Message]:
    links = ", ".join(t for t in link_texts if t) or "(none)"
    return [
        ("system", SYSTEM),
        (
            "human",
            f"Goal: {goal}\n\nLinks on the page: {links}\n\n{page_block(url, title, text, 4000)}",
        ),
    ]
