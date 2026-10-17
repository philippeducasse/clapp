import os

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from discovery.config import Settings
from discovery.llm import (
    BudgetExceeded,
    RunBudget,
    configure_tracing,
    get_chat_model,
)


def make_settings(**overrides) -> Settings:
    return Settings(_env_file=None, mistral_api_key="test-key", **overrides)


def fake_model(budget: RunBudget, replies: int = 5) -> GenericFakeChatModel:
    return GenericFakeChatModel(
        messages=iter([AIMessage(f"reply {i}") for i in range(replies)]), callbacks=[budget]
    )


def test_budget_defaults_match_the_plan():
    budget = RunBudget(Settings(_env_file=None))
    assert budget.limits == {"llm_calls": 80, "pages": 60, "searches": 15, "leads": 25}
    assert budget.max_hops_per_site == 3


def test_spend_counts_until_the_limit_then_raises_without_counting():
    budget = RunBudget(make_settings(max_pages=2))
    budget.spend("pages")
    budget.spend("pages")
    assert budget.exhausted("pages")
    with pytest.raises(BudgetExceeded) as exc:
        budget.spend("pages")
    assert exc.value.kind == "pages"
    assert exc.value.limit == 2
    assert budget.counters["pages"] == 2


def test_budget_shares_the_run_counters():
    counters = {"searches": 0, "pages": 0, "llm_calls": 0, "leads": 0, "candidates": 0}
    budget = RunBudget(make_settings(), counters)
    budget.spend("searches")
    assert counters["searches"] == 1
    assert budget.remaining("searches") == 14


async def test_callback_counts_llm_calls_and_stops_at_the_limit():
    budget = RunBudget(make_settings(max_llm_calls=2))
    model = fake_model(budget)

    await model.ainvoke("one")
    model.invoke("two")
    assert budget.counters["llm_calls"] == 2

    with pytest.raises(BudgetExceeded):
        await model.ainvoke("three")
    assert budget.counters["llm_calls"] == 2


def test_get_chat_model_uses_the_small_model_for_quick_decisions():
    settings = make_settings(mistral_small_model="small-m", mistral_large_model="large-m")
    budget = RunBudget(settings)

    for purpose in ("classify", "pick_link", "pick_website"):
        assert get_chat_model(purpose, settings).model == "small-m"
    for purpose in ("interpret", "extract_leads", "extract_org"):
        assert get_chat_model(purpose, settings).model == "large-m"

    model = get_chat_model("extract_org", settings, budget)
    assert model.temperature == 0
    assert model.callbacks == [budget]


def test_configure_tracing_only_when_enabled(monkeypatch):
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)

    configure_tracing(make_settings())
    assert "LANGSMITH_TRACING" not in os.environ

    configure_tracing(make_settings(langsmith_tracing=True, langsmith_project="p"))
    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGSMITH_PROJECT"] == "p"
