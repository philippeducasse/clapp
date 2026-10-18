"""Exploring: from the starting point to a list of leads.

interpret_start → load_known → search → visit_page ⇄ classify_page → (find_calendar →)
extract_leads / add_org_lead → visit_page … until no pages are left or the exploring share of the
budget is used up.
"""

import re
from typing import Any
from urllib.parse import urlsplit

from langgraph.runtime import Runtime

from discovery.backend_client import Evidence, SourceIn
from discovery.graph.deps import Deps, guarded
from discovery.graph.leads import country_ok, merge_lead
from discovery.graph.navigate import navigate
from discovery.graph.state import DiscoveryState, Lead, PageTask, add_hop
from discovery.llm import BudgetExceeded
from discovery.prompts import ORG_TYPES, extract_leads as extract_leads_prompt
from discovery.prompts import interpret as interpret_prompt
from discovery.prompts import classify as classify_prompt
from discovery.prompts.classify import PageClassification
from discovery.prompts.extract_leads import LeadList
from discovery.prompts.interpret import Interpretation
from discovery.tools.domains import host_matches, same_site
from discovery.tools.fetch import FetchError
from discovery.tools.known import KnownIndex
from discovery.tools.links import extract_links
from discovery.tools.search import SearchError
from discovery.tools.verify import is_blocklisted, url_key

URL_GOAL = (
    "Find the festivals listed on these pages (for example an artist's tour dates) that clapp "
    "doesn't have yet."
)
MAX_START_QUERIES = 5
HITS_PER_QUERY = 5
MAX_LISTING_LINKS = 150

_URL_IN_TEXT = re.compile(r"(?:https?://|www\.)[^\s<>\"'()\[\]]+", re.IGNORECASE)
_WORD = re.compile(r"\w+")

# Search results on these hosts aren't visited: they need a login or JavaScript, or their
# robots.txt shuts crawlers out, so they'd only use up the page budget.
UNVISITABLE_HOSTS = frozenset({
    "facebook.com", "fb.com", "fb.me", "instagram.com", "twitter.com", "x.com", "tiktok.com",
    "youtube.com", "youtu.be", "vimeo.com", "linkedin.com", "pinterest.com", "threads.net",
    "linktr.ee", "drive.google.com", "docs.google.com", "dropbox.com",
})  # fmt: skip


def split_starting_point(text: str) -> tuple[list[str], str]:
    """(URLs, request in plain words). The request is "" when only a few words are left once
    the URLs are taken out ("see https://x.org")."""
    urls: list[str] = []
    for match in _URL_IN_TEXT.finditer(text or ""):
        url = match.group(0).rstrip(".,;:!?")
        if url.lower().startswith("www."):
            url = f"https://{url}"
        if url not in urls:
            urls.append(url)
    rest = " ".join(_URL_IN_TEXT.sub(" ", text or "").split())
    if len(_WORD.findall(rest)) < 3:
        rest = ""
    return urls, rest


def org_root(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/"


# --- nodes ----------------------------------------------------------------------------------


async def interpret_start(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    """URL(s) → pages to visit; plain words → LLM {goal, org_types, countries, queries}; both →
    both, and the request text becomes the goal."""
    deps = runtime.context
    urls, request = split_starting_point(state["starting_point"])
    goal, org_types, countries, queries = URL_GOAL, ["FESTIVAL"], [], []

    if request:
        max_queries = max(1, min(MAX_START_QUERIES, deps.settings.max_searches // 2))
        try:
            answer = await deps.ask(
                "interpret",
                Interpretation,
                interpret_prompt.messages(request, urls, max_queries, deps.today.isoformat()),
            )
        except BudgetExceeded:
            raise
        except Exception as exc:
            await deps.error("interpret_start", f"Could not interpret the request: {exc}")
            answer = Interpretation(goal=request, org_types=list(ORG_TYPES))
            if not urls:
                answer.queries = [request]
        goal = request if urls else (answer.goal.strip() or request)
        org_types = [t for t in ORG_TYPES if t in answer.org_types] or ["FESTIVAL"]
        countries = [c.strip() for c in answer.countries if c.strip()]
        queries = [q.strip() for q in answer.queries if q.strip()][:max_queries]
        if not urls and not queries:
            queries = [request]

    queue = [
        PageTask(url=url, found_via=[Evidence(kind="start", url=url, title="Starting point")])
        for url in urls
    ]
    plan = {
        "urls": urls,
        "goal": goal,
        "org_types": org_types,
        "countries": countries,
        "queries": queries,
    }
    await deps.ctx.set_plan(plan)
    where = f" in {', '.join(countries)}" if countries else ""
    await deps.progress(
        "interpret_start",
        f"Goal: {goal} Looking for {', '.join(t.lower() for t in org_types)}{where}; "
        f"{len(urls)} page(s) to visit, {len(queries)} search(es).",
    )
    return {
        "goal": goal,
        "org_types": org_types,
        "countries": countries,
        "queries": queries,
        "queue": queue,
        "leads": [],
        "sources": [],
        "listings": [],
    }


async def load_known(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    deps.known = await KnownIndex.load(deps.ctx.backend)
    await deps.progress("load_known", f"{len(deps.known)} organisations already known.")
    return {}


@guarded("search")
async def search(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    queue = list(state.get("queue") or [])
    queued = {url_key(task.url) for task in queue}
    for query in state.get("queries") or []:
        try:
            hits = await deps.search.search(query, deps.budget)
        except SearchError as exc:
            await deps.error("search", str(exc))
            continue
        except BudgetExceeded as exc:
            deps.out_of_budget(exc)
            await deps.progress("search", str(exc))
            break
        added = 0
        for hit in hits:
            if added >= HITS_PER_QUERY:
                break
            if host_matches(urlsplit(hit.url).hostname or "", UNVISITABLE_HOSTS):
                continue
            if url_key(hit.url) in queued:
                continue
            queued.add(url_key(hit.url))
            queue.append(
                PageTask(
                    url=hit.url,
                    found_via=[
                        Evidence(
                            kind="search",
                            url=hit.url,
                            title=hit.title[:300],
                            snippet=f'Search: "{query}"',
                        )
                    ],
                )
            )
            added += 1
        await deps.progress("search", f'"{query}": {len(hits)} result(s), {added} to visit.')
    return {"queue": queue}


async def visit_page(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    """Take the next page from the queue and fetch it. Pages that fail are reported and skipped.
    Leaves `page` empty when exploring is over."""
    deps = runtime.context
    queue = list(state.get("queue") or [])
    done: dict[str, Any] = {"queue": [], "current": None, "page": None, "classification": None}
    while queue:
        if not deps.can_explore():
            await deps.progress(
                "visit_page",
                f"Exploring budget used; {len(queue)} page(s) left unvisited.",
            )
            return done
        task = queue.pop(0)
        key = url_key(task.url)
        if key in deps.visited:
            continue
        deps.visited.add(key)
        try:
            page = await deps.fetch(task.url)
        except FetchError as exc:
            await deps.error("visit_page", f"{task.url}: {exc.reason} {exc.detail}".strip())
            continue
        except BudgetExceeded as exc:
            deps.out_of_budget(exc)
            await deps.progress("visit_page", str(exc))
            return done
        if page.is_empty:
            await deps.progress("visit_page", f"Empty content, skipped: {task.url}")
            continue
        deps.visited.add(url_key(page.final_url))
        await deps.progress("visit_page", f"Visiting {page.final_url}")
        return {"queue": queue, "current": task, "page": page, "classification": None}
    return done


def after_visit(state: DiscoveryState) -> str:
    return "classify_page" if state.get("page") is not None else "check_known"


@guarded("classify_page", fallback={"classification": None})
async def classify_page(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    page = state["page"]
    assert page is not None
    links = extract_links(page.html, page.final_url)[:40]
    result = await deps.ask(
        "classify",
        PageClassification,
        classify_prompt.messages(
            state["goal"], page.final_url, page.title, page.text, [link.text for link in links]
        ),
    )
    org_types = state.get("org_types") or ["FESTIVAL"]
    if result.kind == "ORG_SITE" and (
        not result.org_name.strip() or (result.org_type and result.org_type not in org_types)
    ):
        result = result.model_copy(
            update={"kind": "IRRELEVANT", "reason": f"not a {'/'.join(org_types).lower()} site"}
        )
    await deps.progress(
        "classify_page",
        f"{page.final_url}: {result.kind}{f' ({result.reason})' if result.reason else ''}",
    )
    listings = [("listing", page)] if result.kind == "AGGREGATOR" else []
    return {"classification": result, "listings": listings}


def after_classify(state: DiscoveryState) -> str:
    result = state.get("classification")
    if result is None:
        return "visit_page"
    return {
        "ARTIST_SITE": "find_calendar",
        "AGGREGATOR": "extract_leads",
        "ORG_SITE": "add_org_lead",
    }.get(result.kind, "visit_page")


@guarded("find_calendar", fallback={"listings": []})
async def find_calendar(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    page, result = state["page"], state["classification"]
    assert page is not None and result is not None
    if result.lists_events:
        return {"listings": [("calendar", page)]}
    reached = await navigate(deps, page, ["calendar"], 1, step="find_calendar")
    if not reached:
        await deps.progress("find_calendar", f"No calendar page found on {page.final_url}")
        return {"listings": []}
    await deps.progress("find_calendar", f"Calendar: {reached[0][1].final_url}")
    return {"listings": [("calendar", calendar) for _, calendar in reached]}


@guarded("extract_leads", fallback={"listings": []})
async def extract_leads(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    page, task, result = state["page"], state["current"], state["classification"]
    assert page is not None and task is not None and result is not None
    org_types = state.get("org_types") or ["FESTIVAL"]
    countries = state.get("countries") or []
    leads = [lead.model_copy() for lead in state.get("leads") or []]
    sources = list(state.get("sources") or [])
    is_artist = result.kind == "ARTIST_SITE"
    path = add_hop(
        task.found_via, "artist_site" if is_artist else "aggregator", page.final_url, page.title
    )

    for kind, listing in state.get("listings") or []:
        try:
            links = extract_links(listing.html, listing.final_url, same_site_only=False)
            links = links[:MAX_LISTING_LINKS]
            answer = await deps.ask(
                "extract_leads",
                LeadList,
                extract_leads_prompt.messages(
                    state["goal"], org_types, countries, kind, listing.final_url,
                    listing.title, listing.text, links,
                ),
            )  # fmt: skip
        except BudgetExceeded as exc:
            deps.out_of_budget(exc)
            await deps.progress("extract_leads", str(exc))
            break
        except Exception as exc:
            await deps.error("extract_leads", f"{listing.final_url}: {type(exc).__name__}: {exc}")
            continue

        lead_path = add_hop(path, "calendar", listing.final_url, listing.title)
        found: list[str] = []
        dropped = 0
        for out in answer.leads:
            name = " ".join(out.name.split())[:200]
            if not name or out.org_type not in org_types or not country_ok(out.country, countries):
                dropped += 1
                continue
            website = ""
            if out.link_number is not None and 1 <= out.link_number <= len(links):
                url = links[out.link_number - 1].url
                if not is_blocklisted(url) and not same_site(url, listing.final_url):
                    website = url
            lead = Lead(
                name=name,
                org_type=out.org_type,
                town=out.town.strip()[:100],
                country=out.country.strip()[:100],
                dates=out.dates.strip()[:100],
                website_url=website,
                listing_url=listing.final_url,
                found_via=lead_path,
            )
            merge_lead(leads, lead)
            found.append(name)

        if found:
            sources.append(
                SourceIn(
                    url=page.final_url,
                    kind="ARTIST_SITE" if is_artist else "AGGREGATOR",
                    title=page.title[:300],
                    calendar_url=listing.final_url if kind == "calendar" else "",
                    leads_found=len(found),
                )
            )
        deps.ctx.counters["leads"] = len(leads)
        skipped = f" ({dropped} left out: not what the goal asks for)" if dropped else ""
        await deps.progress(
            "extract_leads",
            f"{len(found)} lead(s) on {listing.final_url}{skipped}: {', '.join(found)[:600]}",
        )
    return {"leads": leads, "sources": sources, "listings": []}


@guarded("add_org_lead")
async def add_org_lead(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    """An organisation's own site found while exploring: it becomes a lead with its URL."""
    deps = runtime.context
    page, task, result = state["page"], state["current"], state["classification"]
    assert page is not None and task is not None and result is not None
    org_types = state.get("org_types") or ["FESTIVAL"]
    if not country_ok(result.country, state.get("countries") or []):
        await deps.progress("add_org_lead", f"{result.org_name}: not in the countries asked for.")
        return {}
    leads = [lead.model_copy() for lead in state.get("leads") or []]
    lead = Lead(
        name=" ".join(result.org_name.split())[:200],
        org_type=result.org_type or org_types[0],
        town=result.town.strip()[:100],
        country=result.country.strip()[:100],
        website_url="" if is_blocklisted(page.final_url) else org_root(page.final_url),
        listing_url=page.final_url,
        found_via=add_hop(task.found_via, "org_site", page.final_url, page.title),
    )
    added = merge_lead(leads, lead)
    deps.ctx.counters["leads"] = len(leads)
    await deps.progress("add_org_lead", f"Lead: {lead.name}{'' if added else ' (already listed)'}")
    return {"leads": leads}
