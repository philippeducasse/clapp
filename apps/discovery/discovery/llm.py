"""Chat models and the per-run budget.

- `get_chat_model(purpose, settings, budget)` returns a ChatMistralAI: a small model for classifying
  pages and picking links, a larger one for extraction. Callers wrap it with
  `.with_structured_output(Schema)`; `get_structured_model` does both.
- `RunBudget` holds the per-run limits (LLM calls, pages, searches, leads) and the counters
  reported to the backend. It is also a LangChain callback: every chat model call made with it
  counts as one LLM call, and the call past the limit raises `BudgetExceeded` before it is sent.
"""

import os
from collections.abc import MutableMapping
from typing import Any, Literal

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel

from discovery.config import Settings

Purpose = Literal[
    "interpret", "classify", "pick_link", "pick_website", "extract_leads", "extract_org"
]
BudgetKind = Literal["llm_calls", "pages", "searches", "leads"]

# Cheap, frequent decisions use the small model; reading a page into structured data uses the
# larger one.
SMALL_PURPOSES: frozenset[str] = frozenset({"classify", "pick_link", "pick_website"})


class BudgetExceeded(Exception):
    """A per-run limit was reached. The graph stops exploring and saves what it has."""

    def __init__(self, kind: str, limit: int):
        super().__init__(f"Budget reached: {kind} (limit {limit}).")
        self.kind = kind
        self.limit = limit


class RunBudget(BaseCallbackHandler):
    """Per-run limits and counters. Pass it as a callback to chat models to count LLM calls.

    `counters` can be shared with `RunContext.counters` so progress updates show the spend.
    """

    # LangChain swallows callback exceptions unless raise_error is set; run_inline keeps the
    # check synchronous (no thread pool) so the call is refused before the request goes out.
    raise_error = True
    run_inline = True

    def __init__(self, settings: Settings, counters: MutableMapping[str, int] | None = None):
        self.limits: dict[str, int] = {
            "llm_calls": settings.max_llm_calls,
            "pages": settings.max_pages,
            "searches": settings.max_searches,
            "leads": settings.max_leads,
        }
        self.max_hops_per_site = settings.max_hops_per_site
        self.counters: MutableMapping[str, int] = counters if counters is not None else {}
        for kind in self.limits:
            self.counters.setdefault(kind, 0)

    def spend(self, kind: BudgetKind, amount: int = 1) -> None:
        """Count `amount` of `kind`, or raise BudgetExceeded (without counting) if over the limit."""
        limit = self.limits[kind]
        if self.counters[kind] + amount > limit:
            raise BudgetExceeded(kind, limit)
        self.counters[kind] += amount

    def remaining(self, kind: BudgetKind) -> int:
        return max(0, self.limits[kind] - self.counters[kind])

    def exhausted(self, kind: BudgetKind) -> bool:
        return self.remaining(kind) == 0

    # --- LangChain callback hooks ---------------------------------------------------------

    def on_chat_model_start(self, serialized: Any, messages: Any, **kwargs: Any) -> None:
        self.spend("llm_calls")

    def on_llm_start(self, serialized: Any, prompts: Any, **kwargs: Any) -> None:
        self.spend("llm_calls")


def get_chat_model(
    purpose: Purpose, settings: Settings, budget: RunBudget | None = None
) -> BaseChatModel:
    model = (
        settings.mistral_small_model if purpose in SMALL_PURPOSES else settings.mistral_large_model
    )
    return ChatMistralAI(
        model_name=model,
        api_key=settings.mistral_api_key or None,
        temperature=0,
        timeout=int(settings.llm_timeout_seconds),
        max_retries=2,
        callbacks=[budget] if budget is not None else None,
        tags=[f"discovery:{purpose}"],
    )


def get_structured_model[T: BaseModel](
    purpose: Purpose,
    schema: type[T],
    settings: Settings,
    budget: RunBudget | None = None,
) -> Runnable[Any, T]:
    """`get_chat_model(...).with_structured_output(schema)`: invoking it returns a `schema`."""
    return get_chat_model(purpose, settings, budget).with_structured_output(schema)  # type: ignore[return-value]


def configure_tracing(settings: Settings) -> None:
    """Turn on LangSmith tracing when LANGSMITH_TRACING is set (LangChain reads os.environ)."""
    if not settings.langsmith_tracing:
        return
    os.environ["LANGSMITH_TRACING"] = "true"
    if settings.langsmith_api_key:
        os.environ.setdefault("LANGSMITH_API_KEY", settings.langsmith_api_key)
    os.environ.setdefault("LANGSMITH_PROJECT", settings.langsmith_project)
