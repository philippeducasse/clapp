"""navigate: pick links by number when keyword ranking finds no clear match."""

from pydantic import BaseModel, Field

from discovery.prompts import UNTRUSTED_CONTENT, Message
from discovery.tools.links import Goal, Link

GOAL_DESCRIPTIONS: dict[Goal, str] = {
    "calendar": "the page listing the artist's performance dates (tour dates, calendar, agenda, "
    "past or upcoming shows)",
    "contact": "the organisation's contact, team or imprint page (where email addresses are)",
    "application": "the page explaining how artists apply (open call, application form, "
    "submissions, programming)",
}


class LinkChoice(BaseModel):
    numbers: list[int] = Field(
        default_factory=list,
        description="Numbers of the links to follow, best first. Empty if none fits.",
    )
    reason: str = ""


SYSTEM = f"""You help a crawler move around one website. You get a numbered list of links found on
a page and what the crawler is looking for. Answer with the numbers of the links most likely to
lead there, best first, at most {{max_links}}. Answer with an empty list if no link fits.
Only use numbers from the list.

{UNTRUSTED_CONTENT}"""


def messages(goals: list[Goal], page_url: str, links: list[Link], max_links: int) -> list[Message]:
    looking_for = "; or ".join(GOAL_DESCRIPTIONS[goal] for goal in goals)
    numbered = "\n".join(
        f"{n}. {link.text or '(no text)'} — {link.url}" for n, link in enumerate(links, start=1)
    )
    return [
        ("system", SYSTEM.format(max_links=max_links)),
        (
            "human",
            f"Looking for: {looking_for}\nPage: {page_url}\n\n<page>\n{numbered}\n</page>",
        ),
    ]
