"""Graph state: what flows between nodes.

Only plain data lives in the state. The run's tools and run-wide bookkeeping (fetcher, budget,
known index, pages fetched so far) live in `Deps`, passed to every node as the LangGraph runtime
context.
"""

import operator
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field

from discovery.backend_client import CandidateIn, Evidence, SourceIn
from discovery.prompts import OrgType
from discovery.prompts.classify import PageClassification
from discovery.tools.fetch import Page
from discovery.tools.verify import url_key


class PageTask(BaseModel):
    """A page to visit while exploring, with the path that led to it."""

    url: str
    found_via: list[Evidence] = Field(default_factory=list)


class Lead(BaseModel):
    """An organisation named somewhere (a calendar, a listing, its own site), not yet researched."""

    name: str
    org_type: OrgType
    town: str = ""
    country: str = ""
    dates: str = ""
    website_url: str = ""  # only a link found on a fetched page, never blocklisted
    listing_url: str = ""  # the page the lead was found on
    found_via: list[Evidence] = Field(default_factory=list)


class DiscoveryState(TypedDict, total=False):
    starting_point: str
    # interpret_start
    goal: str
    org_types: list[str]
    countries: list[str]
    queries: list[str]
    # exploring
    queue: list[PageTask]
    current: PageTask | None
    page: Page | None
    classification: PageClassification | None
    listings: list[tuple[str, Page]]  # (kind, page) to extract leads from: calendar | listing
    leads: list[Lead]
    sources: list[SourceIn]
    # research
    missing: list[Lead]
    candidates: Annotated[list[CandidateIn], operator.add]  # one per research_org
    final_candidates: list[CandidateIn]  # after dedupe_candidates


def add_hop(path: list[Evidence], kind: str, url: str, title: str = "") -> list[Evidence]:
    """`path` + one hop. A hop to the same page as the last one replaces its kind and title
    (e.g. "start" → "artist_site") instead of repeating the page."""
    hop = Evidence(kind=kind, url=url, title=title[:300])
    if path and url_key(path[-1].url) == url_key(url):
        last = path[-1]
        merged = last.model_copy(update={"kind": kind, "title": title[:300] or last.title})
        return [*path[:-1], merged]
    return [*path, hop]
