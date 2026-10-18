"""`Deps`: the run's tools and run-wide bookkeeping, shared by every node.

Passed to the graph as the LangGraph runtime context (`graph.ainvoke(..., context=deps)`); nodes
read it with `runtime.context`. Nothing in here goes into the graph state.
"""

import functools
import logging
from collections import Counter
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol

from langchain_core.runnables import Runnable
from pydantic import BaseModel

from discovery.backend_client import BackendError
from discovery.config import Settings
from discovery.llm import BudgetExceeded, Purpose, RunBudget, get_structured_model
from discovery.prompts import Message
from discovery.runner import RunCancelled, RunContext
from discovery.tools.domains import registrable_domain
from discovery.tools.fetch import Fetcher, FetchError, Page, clean_url
from discovery.tools.known import KnownIndex
from discovery.tools.search import SearchProvider
from discovery.tools.verify import url_key

logger = logging.getLogger(__name__)


class ModelFactory(Protocol):
    """Returns a runnable that answers with an instance of `schema` (a structured-output model).

    Every call must go through a chat model that has `budget` as a callback, so it is counted.
    """

    def __call__(
        self, purpose: Purpose, schema: type[BaseModel], budget: RunBudget
    ) -> Runnable[Any, Any]: ...


def mistral_models(settings: Settings) -> ModelFactory:
    def factory(purpose: Purpose, schema: type[BaseModel], budget: RunBudget) -> Runnable:
        return get_structured_model(purpose, schema, settings, budget)

    return factory


class NoAnswer(Exception):
    """The model didn't return the structured output."""


@dataclass
class Deps:
    ctx: RunContext
    budget: RunBudget
    fetcher: Fetcher
    search: SearchProvider
    models: ModelFactory
    today: date
    known: KnownIndex = field(default_factory=KnownIndex)
    # Pages fetched during the run, by url_key (requested and final URL): a page is fetched,
    # and counted against the budget, once per run.
    pages: dict[str, Page] = field(default_factory=dict)
    failed: dict[str, FetchError] = field(default_factory=dict)
    visited: set[str] = field(default_factory=set)  # pages explored (classified)
    hops: Counter[str] = field(default_factory=Counter)  # links followed, per registrable domain
    budget_reached: set[str] = field(default_factory=set)

    @property
    def settings(self) -> Settings:
        return self.ctx.settings

    # --- reporting ---------------------------------------------------------------------------

    async def progress(self, step: str, message: str) -> None:
        await self.ctx.progress(step, message)

    async def error(self, step: str, message: str) -> None:
        await self.ctx.report_error(step, message)

    def out_of_budget(self, exc: BudgetExceeded) -> None:
        self.budget_reached.add(exc.kind)
        self.ctx.add_note(f"budget reached: {exc.kind}")

    # --- budget shares -----------------------------------------------------------------------

    def can_explore(self) -> bool:
        """Exploring stops once it has used its share of the page or LLM-call budget, so
        researching the leads still has something left."""
        share = self.settings.explore_share
        limits, counters = self.budget.limits, self.budget.counters
        return all(
            counters[kind] < max(1, int(limits[kind] * share)) for kind in ("pages", "llm_calls")
        ) and not ({"pages", "llm_calls"} & self.budget_reached)

    def hops_left(self, url: str) -> int:
        return max(0, self.budget.max_hops_per_site - self.hops[registrable_domain(url)])

    def take_hop(self, url: str) -> bool:
        if self.hops_left(url) <= 0:
            return False
        self.hops[registrable_domain(url)] += 1
        return True

    # --- tools -------------------------------------------------------------------------------

    def fetched(self, url: str) -> bool:
        key = url_key(url)
        return key in self.pages or key in self.failed

    async def fetch(self, url: str) -> Page:
        """`Fetcher.fetch`, at most once per URL per run (failures are remembered too)."""
        url = clean_url(url)
        key = url_key(url)
        if key in self.pages:
            return self.pages[key]
        if key in self.failed:
            raise self.failed[key]
        try:
            page = await self.fetcher.fetch(url, self.budget)
        except FetchError as exc:
            self.failed[key] = exc
            raise
        self.pages[key] = page
        self.pages.setdefault(url_key(page.final_url), page)
        return page

    async def ask[T: BaseModel](
        self, purpose: Purpose, schema: type[T], messages: list[Message]
    ) -> T:
        """One structured LLM call. Raises BudgetExceeded past the LLM-call limit."""
        model = self.models(purpose, schema, self.budget)
        answer = await model.ainvoke(messages)
        if not isinstance(answer, schema):
            raise NoAnswer(f"{purpose}: no structured answer")
        return answer


Node = Callable[..., Awaitable[dict[str, Any]]]


def guarded(step: str, fallback: dict[str, Any] | None = None) -> Callable[[Node], Node]:
    """Catch a node's own errors so one broken site doesn't stop the run.

    - BudgetExceeded is recorded (the run ends with "budget reached") and the node returns
      `fallback`.
    - Any other error is reported as a run error and the node returns `fallback`.
    - RunCancelled and BackendError go through: the run stops (CANCELLED / FAILED).
    """

    def decorator(node: Node) -> Node:
        @functools.wraps(node)
        async def wrapper(state: Any, runtime: Any) -> dict[str, Any]:
            deps: Deps = runtime.context
            try:
                return await node(state, runtime)
            except (RunCancelled, BackendError):
                raise
            except BudgetExceeded as exc:
                deps.out_of_budget(exc)
                await deps.progress(step, str(exc))
            except Exception as exc:
                logger.exception("Run %s: %s failed", deps.ctx.run_id, step)
                await deps.error(step, f"{type(exc).__name__}: {exc}")
            return dict(fallback or {})

        return wrapper

    return decorator
