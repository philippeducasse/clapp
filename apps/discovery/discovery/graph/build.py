"""Builds the discovery graph and runs it for one run.

START
 → interpret_start → load_known → search
 → visit_page ⇄ classify_page → find_calendar → extract_leads ─┐
                              → extract_leads ──────────────────┤ (back to visit_page)
                              → add_org_lead ───────────────────┘
 → check_known → Send(research_org, lead) × missing leads, in parallel
 → dedupe_candidates → save
END
"""

import logging
from collections.abc import Callable
from datetime import date

from langgraph.graph import END, START, StateGraph

from discovery.config import Settings
from discovery.graph.deps import Deps, ModelFactory, mistral_models
from discovery.graph.nodes.check_known import check_known, fan_out
from discovery.graph.nodes.explore import (
    add_org_lead,
    after_classify,
    after_visit,
    classify_page,
    extract_leads,
    find_calendar,
    interpret_start,
    load_known,
    search,
    visit_page,
)
from discovery.graph.nodes.finish import dedupe_candidates, save
from discovery.graph.research_org import build_research_graph
from discovery.graph.state import DiscoveryState
from discovery.llm import RunBudget
from discovery.runner import Graph, RunContext
from discovery.tools.fetch import Fetcher
from discovery.tools.search import MistralSearch, SearchProvider

logger = logging.getLogger(__name__)

# Steps per explored page: visit_page, classify_page, find_calendar, extract_leads.
STEPS_PER_PAGE = 5
EXTRA_STEPS = 30


def build_graph():
    graph = StateGraph(DiscoveryState, Deps)
    graph.add_node("interpret_start", interpret_start)
    graph.add_node("load_known", load_known)
    graph.add_node("search", search)
    graph.add_node("visit_page", visit_page)
    graph.add_node("classify_page", classify_page)
    graph.add_node("find_calendar", find_calendar)
    graph.add_node("extract_leads", extract_leads)
    graph.add_node("add_org_lead", add_org_lead)
    graph.add_node("check_known", check_known)
    graph.add_node("research_org", build_research_graph())
    graph.add_node("dedupe_candidates", dedupe_candidates)
    graph.add_node("save", save)

    graph.add_edge(START, "interpret_start")
    graph.add_edge("interpret_start", "load_known")
    graph.add_edge("load_known", "search")
    graph.add_edge("search", "visit_page")
    graph.add_conditional_edges("visit_page", after_visit, ["classify_page", "check_known"])
    graph.add_conditional_edges(
        "classify_page",
        after_classify,
        ["find_calendar", "extract_leads", "add_org_lead", "visit_page"],
    )
    graph.add_edge("find_calendar", "extract_leads")
    graph.add_edge("extract_leads", "visit_page")
    graph.add_edge("add_org_lead", "visit_page")
    graph.add_conditional_edges("check_known", fan_out, ["research_org", "dedupe_candidates"])
    graph.add_edge("research_org", "dedupe_candidates")
    graph.add_edge("dedupe_candidates", "save")
    graph.add_edge("save", END)
    return graph.compile(name="discovery")


GRAPH = build_graph()


def recursion_limit(settings: Settings) -> int:
    """Safety net against loops: explored pages can't exceed the page budget."""
    return settings.max_pages * STEPS_PER_PAGE + EXTRA_STEPS


async def run_discovery(
    ctx: RunContext,
    *,
    fetcher: Fetcher | None = None,
    search: SearchProvider | None = None,
    models: ModelFactory | None = None,
    today: date | None = None,
) -> None:
    """Run the graph for `ctx`. Tools default to the real ones (Mistral, the web)."""
    settings = ctx.settings
    owns_fetcher = fetcher is None
    deps = Deps(
        ctx=ctx,
        budget=RunBudget(settings, ctx.counters),
        fetcher=fetcher or Fetcher(settings),
        search=search or MistralSearch(settings),
        models=models or mistral_models(settings),
        today=today or date.today(),
    )
    try:
        await GRAPH.ainvoke(
            {"starting_point": ctx.starting_point},
            context=deps,
            config={
                "recursion_limit": recursion_limit(settings),
                "max_concurrency": settings.research_concurrency,
            },
        )
    finally:
        if owns_fetcher:
            await deps.fetcher.aclose()


def make_discovery_graph(
    fetcher_factory: Callable[[Settings], Fetcher] | None = None,
    search: SearchProvider | None = None,
    models: ModelFactory | None = None,
    today: date | None = None,
) -> Graph:
    """A `Graph` for the Runner. Tests pass fakes; the app uses the defaults."""

    async def graph(ctx: RunContext) -> None:
        fetcher = fetcher_factory(ctx.settings) if fetcher_factory else None
        try:
            await run_discovery(ctx, fetcher=fetcher, search=search, models=models, today=today)
        finally:
            if fetcher is not None:
                await fetcher.aclose()

    return graph


discovery_graph: Graph = make_discovery_graph()
