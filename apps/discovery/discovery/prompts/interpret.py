"""interpret_start: turn a plain-words request into a goal, organisation types and search queries."""

from pydantic import Field

from discovery.prompts import LLMOutput, ABOUT_CLAPP, Message, OrgType


class Interpretation(LLMOutput):
    goal: str = Field(description="One sentence: what the research should find.")
    org_types: list[OrgType] = Field(
        default_factory=list,
        description="Kinds of organisations wanted. Empty means festivals only.",
    )
    countries: list[str] = Field(
        default_factory=list,
        description="Countries the organisations must be in, as English names. Empty: anywhere.",
    )
    queries: list[str] = Field(
        default_factory=list,
        description="Web search queries that would find relevant pages (at most 5).",
    )


SYSTEM = f"""You plan web research for clapp. {ABOUT_CLAPP}

A superuser typed a request. Work out:
- goal: one sentence describing what to find.
- org_types: FESTIVAL, RESIDENCY and/or VENUE. Use only the kinds the request asks for; when it
  doesn't say, use FESTIVAL.
- countries: only if the request limits the region (English names, e.g. "Belgium", "Germany").
- queries: up to {{max_queries}} web search queries, in the most useful languages for the
  region (e.g. French and Dutch for Belgium), that would find official sites or lists of such
  organisations. Mention the year when the request is about upcoming editions or open calls.
  If the request only asks to look at the given pages (e.g. "check the tour dates on <link>"),
  return no queries.

Today is {{today}}."""


def messages(request: str, urls: list[str], max_queries: int, today: str) -> list[Message]:
    pages = "\n".join(f"- {url}" for url in urls) or "(none)"
    return [
        ("system", SYSTEM.format(max_queries=max_queries, today=today)),
        ("human", f"Request: {request}\n\nPages given with the request:\n{pages}"),
    ]
