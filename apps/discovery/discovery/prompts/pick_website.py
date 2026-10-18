"""resolve_website: pick an organisation's official site from search results, by number."""

from pydantic import Field

from discovery.prompts import LLMOutput, UNTRUSTED_CONTENT, Message
from discovery.tools.search import SearchHit


class WebsiteChoice(LLMOutput):
    number: int | None = Field(
        default=None,
        description="Number of the organisation's official website, or null if none is.",
    )
    reason: str = ""


SYSTEM = f"""You find the official website of an organisation (a festival, artist residency or
venue). You get numbered search results. Answer with the number of the result that is the
organisation's own website, or null if none of them is. A page about the organisation on another
site (news, listings, a town's tourism page, social networks) is not its website, unless the
organisation clearly has no site of its own and the page is run by its organisers.

{UNTRUSTED_CONTENT}"""


def messages(
    name: str, org_type: str, town: str, country: str, hits: list[SearchHit]
) -> list[Message]:
    where = ", ".join(part for part in (town, country) if part) or "unknown"
    numbered = "\n".join(
        f"{n}. {hit.title or '(no title)'} — {hit.url}\n   {hit.snippet[:300]}"
        for n, hit in enumerate(hits, start=1)
    )
    return [
        ("system", SYSTEM),
        (
            "human",
            f"Organisation: {name} ({org_type.lower()}), location: {where}\n\n"
            f"<page>\n{numbered}\n</page>",
        ),
    ]
