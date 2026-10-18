"""research_org: one missing lead → one candidate (PENDING or UNRESOLVED), or nothing.

resolve_website → visit_site → extract_org → verify

- resolve_website: no URL? Search "{name} {town} {year}" and let the LLM pick the official site
  from the results, by number. A site clapp already has (same domain) ends the research.
- visit_site: fetch the site, then navigate("contact / application") for up to 2 more pages.
- extract_org: structured candidate from those pages (date and application-type rules copied
  from the backend's enrich prompts).
- verify: keep only emails and URLs that appear in pages fetched for this lead. A candidate needs
  a name and either a website that could be read or a verified email; otherwise it's UNRESOLVED.

Run once per lead through `Send`; the leads are researched in parallel. Only `candidates` goes
back to the main graph.
"""

import operator
from datetime import date
from typing import Annotated, Any, TypedDict
from urllib.parse import urlsplit, urlunsplit

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from discovery.backend_client import CandidateContact, CandidateIn, Evidence
from discovery.graph.deps import Deps, guarded
from discovery.graph.leads import merge_evidence
from discovery.graph.navigate import navigate
from discovery.graph.state import Lead, add_hop
from discovery.llm import BudgetExceeded
from discovery.prompts import APPLICATION_TYPES, ORG_TYPES, SUBTYPES, clip
from discovery.prompts import extract_org as extract_org_prompt
from discovery.prompts import pick_website as pick_website_prompt
from discovery.prompts.extract_org import OrgExtraction
from discovery.prompts.pick_website import WebsiteChoice
from discovery.tools.domains import registrable_domain
from discovery.tools.fetch import FetchError, Page
from discovery.tools.search import SearchError, SearchHit
from discovery.tools.verify import (
    SeenContent,
    extract_emails,
    is_blocklisted,
    normalize_email,
    url_key,
    verified_url,
    verified_website,
)

MAX_SEARCH_HITS = 8
MAX_FALLBACK_EMAILS = 3


class ResearchState(TypedDict, total=False):
    goal: str
    lead: Lead
    website_url: str
    resolve_hits: list[SearchHit]
    resolve_hop: Evidence | None
    pages: list[tuple[str, Page]]  # (kind, page): org_site first, then contact / application
    site_problem: str  # why the site couldn't be read, for UNRESOLVED candidates
    extraction: OrgExtraction | None
    already_known: bool
    out_of_budget: bool
    candidates: Annotated[list[CandidateIn], operator.add]


class ResearchOutput(TypedDict, total=False):
    candidates: Annotated[list[CandidateIn], operator.add]


@guarded("resolve_website", fallback={"site_problem": "error while looking for the website"})
async def resolve_website(state: ResearchState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    lead = state["lead"]
    await deps.progress("resolve_website", f"Researching {lead.name}")
    if lead.website_url:
        return {"website_url": lead.website_url}

    query = " ".join(part for part in (lead.name, lead.town, str(deps.today.year)) if part)
    try:
        hits = await deps.search.search(query, deps.budget)
    except SearchError as exc:
        await deps.error("resolve_website", f"{lead.name}: {exc}")
        return {"site_problem": "web search failed"}
    except BudgetExceeded as exc:
        deps.out_of_budget(exc)
        return {"out_of_budget": True}
    hits = [hit for hit in hits if not is_blocklisted(hit.url)][:MAX_SEARCH_HITS]
    if not hits:
        await deps.progress("resolve_website", f"{lead.name}: no website found.")
        return {"site_problem": "no website found by web search"}

    try:
        choice = await deps.ask(
            "pick_website",
            WebsiteChoice,
            pick_website_prompt.messages(lead.name, lead.org_type, lead.town, lead.country, hits),
        )
    except BudgetExceeded as exc:
        deps.out_of_budget(exc)
        return {"out_of_budget": True}
    if choice.number is None or not 1 <= choice.number <= len(hits):
        await deps.progress("resolve_website", f"{lead.name}: no official website in the results.")
        return {"resolve_hits": hits, "site_problem": "no official website in the search results"}

    hit = hits[choice.number - 1]
    website = urlunsplit(urlsplit(hit.url)._replace(fragment=""))
    if (match := deps.known.match("", "", website)) is not None:
        await deps.progress(
            "resolve_website",
            f"{lead.name}: already in clapp as {match.entry.name} (same website).",
        )
        return {"already_known": True}
    await deps.progress("resolve_website", f"{lead.name}: website {website}")
    return {
        "website_url": website,
        "resolve_hits": hits,
        "resolve_hop": Evidence(
            kind="search", url=hit.url, title=hit.title[:300], snippet=f'Search: "{query}"'
        ),
    }


def after_resolve(state: ResearchState) -> str:
    return END if state.get("already_known") else "visit_site"


@guarded("visit_site", fallback={"site_problem": "error while reading the website"})
async def visit_site(state: ResearchState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    lead, website = state["lead"], state.get("website_url") or ""
    if not website or state.get("out_of_budget"):
        return {"pages": []}
    try:
        home = await deps.fetch(website)
    except FetchError as exc:
        await deps.error("visit_site", f"{lead.name}: {website}: {exc.reason} {exc.detail}".strip())
        return {"pages": [], "site_problem": f"website unreachable ({exc.reason})"}
    except BudgetExceeded as exc:
        deps.out_of_budget(exc)
        return {"pages": [], "out_of_budget": True}
    if home.is_empty:
        await deps.progress("visit_site", f"{lead.name}: empty content on {website}")
        return {"pages": [], "site_problem": "no readable content (JavaScript-only site?)"}

    pages: list[tuple[str, Page]] = [(f"{lead.org_type.lower()}_site", home)]
    try:
        reached = await navigate(deps, home, ["contact", "application"], 2, step="visit_site")
    except BudgetExceeded as exc:
        deps.out_of_budget(exc)
        reached = []
    pages.extend(reached)
    await deps.progress(
        "visit_site",
        f"{lead.name}: read {', '.join(page.final_url for _, page in pages)}",
    )
    return {"pages": pages}


@guarded("extract_org", fallback={"extraction": None})
async def extract_org(state: ResearchState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    lead, pages = state["lead"], state.get("pages") or []
    if not pages:
        return {"extraction": None}
    extraction = await deps.ask(
        "extract_org",
        OrgExtraction,
        extract_org_prompt.messages(
            state.get("goal", ""),
            lead.org_type,
            describe_lead(lead),
            [(kind, page.final_url, page.title, page.text) for kind, page in pages],
            deps.today.isoformat(),
        ),
    )
    return {"extraction": extraction}


@guarded("verify")
async def verify(state: ResearchState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    lead = state["lead"]
    if state.get("out_of_budget") and not state.get("pages"):
        await deps.progress("verify", f"{lead.name}: not researched (budget reached).")
        return {}
    candidate = build_candidate(state, deps.pages)
    if candidate.state == "PENDING":
        emails = ", ".join(c.email for c in candidate.contacts) or "no email"
        message = f"{candidate.name}: candidate ({emails})."
    else:
        message = (
            f"{candidate.name}: unresolved ({state.get('site_problem') or 'not enough facts'})."
        )
    await deps.progress("verify", message)
    return {"candidates": [candidate]}


# --- building the candidate ------------------------------------------------------------------


def describe_lead(lead: Lead) -> str:
    parts = [lead.name]
    where = ", ".join(part for part in (lead.town, lead.country) if part)
    if where:
        parts.append(where)
    if lead.dates:
        parts.append(f"dates: {lead.dates}")
    origin = next((hop for hop in reversed(lead.found_via) if hop.title), None)
    if origin:
        parts.append(f"listed on {origin.title} ({origin.url})")
    return "; ".join(parts)


def default_reason(lead: Lead) -> str:
    origin = next((hop for hop in reversed(lead.found_via) if hop.kind != "start"), None)
    if origin is None and lead.found_via:
        origin = lead.found_via[-1]
    if origin is None:
        return ""
    dates = f" ({lead.dates})" if lead.dates else ""
    label = origin.title or origin.url
    if origin.kind == "calendar":
        return f"On the calendar {label}{dates}."
    if origin.kind == "search":
        return f"Found by web search: {label}."
    return f"Listed on {label}{dates}."


def build_candidate(state: ResearchState, run_pages: dict[str, Page]) -> CandidateIn:
    lead = state["lead"]
    pages = state.get("pages") or []
    extraction = state.get("extraction")
    hits = state.get("resolve_hits") or []

    # Emails and application URLs must appear on this organisation's own pages.
    own = SeenContent()
    for _, page in pages:
        own.add_page(page.url, page.html, page.text, page.final_url)
    # The website may also come from a link on the listing page or a search result.
    linked = SeenContent()
    listing = run_pages.get(url_key(lead.listing_url))
    if listing is not None:
        linked.add_page(listing.url, listing.html, listing.text, listing.final_url)
    linked.add_urls(hit.url for hit in hits)
    for _, page in pages:
        linked.add_page(page.url, page.html, page.text, page.final_url)
    website = short_url(verified_website(state.get("website_url") or "", linked), 200)

    org_type = lead.org_type
    if extraction is not None and extraction.org_type in ORG_TYPES:
        org_type = extraction.org_type
    contacts = verified_contacts(extraction, own, pages, website)

    application_url = ""
    if extraction is not None:
        application_url = verified_url(extraction.application_url, own)
    if not application_url:
        application_url = next(
            (page.final_url for kind, page in pages if kind == "application"), ""
        )
    if len(application_url) > 500:
        application_url = ""

    name = clip_line((extraction.name if extraction else "") or lead.name, 200)
    readable_site = bool(website and pages)
    state_value = "PENDING" if name and (readable_site or contacts) else "UNRESOLVED"

    reason = (extraction.relevance_reason.strip() if extraction else "") or default_reason(lead)
    if state_value == "UNRESOLVED":
        problem = state.get("site_problem") or "not enough facts found"
        reason = f"Could not research: {problem}. {reason}".strip()

    found_via = list(lead.found_via)
    if (hop := state.get("resolve_hop")) is not None:
        found_via = merge_evidence(found_via, [hop])
    for kind, page in pages:
        found_via = add_hop(found_via, kind, page.final_url, page.title)

    sources: list[Evidence] = []
    if listing is not None:
        sources.append(evidence("listing", listing))
    sources.extend(evidence(kind, page) for kind, page in pages)

    fields: dict[str, Any] = {}
    if extraction is not None:
        fields = extracted_fields(extraction, org_type)

    return CandidateIn(
        org_type=org_type,
        name=name,
        state=state_value,
        description=clip_line(extraction.description if extraction else "", 1000),
        country=clip_line((extraction.country if extraction else "") or lead.country, 100),
        town=clip_line((extraction.town if extraction else "") or lead.town, 100),
        website_url=website,
        application_url=application_url,
        contacts=contacts,
        found_via=[e for e in found_via if len(e.url) <= 1000],
        sources=merge_evidence([e for e in sources if len(e.url) <= 1000]),
        relevance_reason=reason,
        **fields,
    )


def verified_contacts(
    extraction: OrgExtraction | None, own: SeenContent, pages: list[tuple[str, Page]], website: str
) -> list[CandidateContact]:
    """The extracted contacts whose email is on the organisation's pages. If there are none, the
    emails on those pages that belong to the organisation's own domain."""
    contacts: list[CandidateContact] = []
    emails: set[str] = set()
    for contact in extraction.contacts if extraction else []:
        email = normalize_email(contact.email)
        if email and email not in emails and own.has_email(email):
            emails.add(email)
            contacts.append(
                CandidateContact(
                    email=email,
                    name=clip_line(contact.name, 200),
                    role=clip_line(contact.role, 100),
                )
            )
    if contacts or not website:
        return contacts
    site = registrable_domain(website)
    for _, page in pages:
        for email in sorted(extract_emails(page.html) | extract_emails(page.text)):
            if email not in emails and registrable_domain(email.rpartition("@")[2]) == site:
                emails.add(email)
                contacts.append(CandidateContact(email=email))
            if len(contacts) >= MAX_FALLBACK_EMAILS:
                return contacts
    return contacts


def extracted_fields(extraction: OrgExtraction, org_type: str) -> dict[str, Any]:
    subtype = extraction.subtype.strip().upper()
    application_type = extraction.application_type.strip().upper()
    fields: dict[str, Any] = {
        "subtype": subtype if subtype in SUBTYPES[org_type] else "",
        "application_type": (
            application_type if application_type in APPLICATION_TYPES[org_type] else ""
        ),
    }
    if org_type == "VENUE":
        return fields
    start = iso_date(extraction.start_date)
    fields.update(
        start_date=start,
        end_date=iso_date(extraction.end_date),
        approximate_date=clip_line(extraction.approximate_date, 100),
        application_date_start=clip_line(extraction.application_date_start, 100),
        application_date_end=clip_line(extraction.application_date_end, 100),
    )
    if org_type == "FESTIVAL":
        fields["estimated_start_date"] = iso_date(extraction.estimated_start_date) or start
    return fields


def iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat((value or "").strip()[:10])
    except ValueError:
        return None


def clip_line(value: str, limit: int) -> str:
    return " ".join((value or "").split())[:limit]


def short_url(url: str, limit: int) -> str:
    """`url`, or its site root when it's too long for the field."""
    if len(url) <= limit:
        return url
    parts = urlsplit(url)
    root = f"{parts.scheme}://{parts.netloc}/"
    return root if len(root) <= limit else ""


def evidence(kind: str, page: Page) -> Evidence:
    return Evidence(
        kind=kind[:30],
        url=page.final_url,
        title=page.title[:300],
        snippet=clip(page.text, 300),
    )


def build_research_graph():
    graph = StateGraph(ResearchState, Deps, output_schema=ResearchOutput)
    graph.add_node("resolve_website", resolve_website)
    graph.add_node("visit_site", visit_site)
    graph.add_node("extract_org", extract_org)
    graph.add_node("verify", verify)
    graph.add_edge(START, "resolve_website")
    graph.add_conditional_edges("resolve_website", after_resolve, ["visit_site", END])
    graph.add_edge("visit_site", "extract_org")
    graph.add_edge("extract_org", "verify")
    graph.add_edge("verify", END)
    return graph.compile(name="research_org")
