"""Fakes for testing the graph: a scripted chat model, a search provider and a small web.

- `ScriptedChatModel` is a LangChain chat model whose answer comes from a Python function of
  (purpose, prompt text). It goes through LangChain's callback system, so `RunBudget` counts its
  calls and stops it at the limit like a real model.
- `FakeSearch` answers queries from a dict.
- `FakeWeb` serves pages from tests/fixtures/web with respx; anything else gets a 404.
"""

import json
import re
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

import httpx
import respx
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel

from discovery.graph.deps import ModelFactory
from discovery.llm import RunBudget
from discovery.tools.search import SearchHit
from tests.conftest import FIXTURES

Responder = Callable[[str, str], Any]


class ScriptedChatModel(BaseChatModel):
    purpose: str
    responder: Any

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        prompt = "\n".join(str(message.content) for message in messages)
        answer = self.responder(self.purpose, prompt)
        content = answer if isinstance(answer, str) else json.dumps(answer)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])


class LLMLog:
    """Wraps a responder and records every call as (purpose, prompt)."""

    def __init__(self, responder: Responder):
        self.responder = responder
        self.calls: list[tuple[str, str]] = []

    def __call__(self, purpose: str, prompt: str) -> Any:
        self.calls.append((purpose, prompt))
        return self.responder(purpose, prompt)

    def purposes(self) -> list[str]:
        return [purpose for purpose, _ in self.calls]


def scripted_models(responder: Responder) -> ModelFactory:
    def factory(purpose: str, schema: type[BaseModel], budget: RunBudget):
        model = ScriptedChatModel(purpose=purpose, responder=responder, callbacks=[budget])
        return model | RunnableLambda(lambda message: schema.model_validate_json(message.content))

    return factory  # type: ignore[return-value]


def link_number(prompt: str, url: str) -> int | None:
    """The number given to `url` in a numbered link list ("3. text — url")."""
    for match in re.finditer(r"^(\d+)\. .*? — (\S+)$", prompt, re.MULTILINE):
        if match.group(2) == url:
            return int(match.group(1))
    return None


class FakeSearch:
    def __init__(self, results: dict[str, list[SearchHit]] | None = None):
        self.results = results or {}
        self.queries: list[str] = []

    async def search(self, query: str, budget: RunBudget | None = None) -> list[SearchHit]:
        if budget is not None:
            budget.spend("searches")
        self.queries.append(query)
        for key, hits in self.results.items():
            if key.lower() in query.lower():
                return hits
        return []


HTML = {"content-type": "text/html; charset=utf-8"}


class FakeWeb:
    """Pages served by respx on `router`. Call `finish()` after the last route: it adds the
    catch-all 404 (robots.txt included, which allows everything)."""

    def __init__(self, router: respx.MockRouter):
        self.router = router

    def page(self, url: str, fixture: str) -> None:
        body = (FIXTURES / "web" / fixture).read_bytes()
        self.router.get(url).respond(200, content=body, headers=HTML)

    def html(self, url: str, html: str) -> None:
        self.router.get(url).respond(200, content=html.encode(), headers=HTML)

    def broken(self, url_regex: str) -> None:
        self.router.get(url__regex=url_regex).mock(side_effect=httpx.ConnectError("refused"))

    def finish(self) -> None:
        self.router.route().respond(404, text="not found")


def runtime(deps) -> SimpleNamespace:
    """What LangGraph passes to a node as `runtime`, for calling nodes directly."""
    return SimpleNamespace(context=deps)
