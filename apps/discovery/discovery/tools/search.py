"""Web search that keeps the result URLs.

`MistralSearch` asks a Mistral model with the built-in `web_search` tool (the same approach as the
backend's `MistralClient.search()`), but unlike the backend it keeps the citation URLs: each
`tool_reference` chunk in the answer becomes a `SearchHit`.

Search sits behind the `SearchProvider` protocol so Brave or Tavily can be added later.
"""

import logging
import re
from typing import Any, Protocol

from mistralai.client import Mistral
from pydantic import BaseModel

from discovery.config import Settings
from discovery.llm import RunBudget

logger = logging.getLogger(__name__)

SEARCH_INSTRUCTIONS = (
    "You search the web with `web_search` for a team that books circus and street theatre "
    "shows. Run the search, then list the most relevant pages you found, one per line, with a "
    "short note on what each page is. Prefer official websites of festivals, residencies and "
    "venues. Always cite the pages you used."
)

_URL_IN_TEXT = re.compile(r"https?://[^\s<>\"')\]]+")


class SearchHit(BaseModel):
    url: str
    title: str = ""
    snippet: str = ""


class SearchError(Exception):
    """The search provider failed (network, API error). The caller decides whether to go on."""


class SearchProvider(Protocol):
    async def search(self, query: str, budget: RunBudget | None = None) -> list[SearchHit]: ...


class MistralSearch:
    def __init__(self, settings: Settings, client: Mistral | None = None):
        self.settings = settings
        self.client = client or Mistral(
            api_key=settings.mistral_api_key,
            timeout_ms=int(settings.llm_timeout_seconds * 1000),
        )

    async def search(self, query: str, budget: RunBudget | None = None) -> list[SearchHit]:
        """Search the web for `query`. Counts one search against `budget` before calling out."""
        if budget is not None:
            budget.spend("searches")
        try:
            response = await self.client.beta.conversations.start_async(
                model=self.settings.mistral_search_model,
                inputs=query,
                instructions=SEARCH_INSTRUCTIONS,
                tools=[{"type": "web_search"}],
                completion_args={"temperature": 0.2},
                store=False,
            )
        except Exception as exc:  # the SDK raises several unrelated error types
            raise SearchError(f"Search failed for {query!r}: {exc}") from exc
        hits = hits_from_response(response)
        logger.info("Search %r: %d hit(s)", query, len(hits))
        return hits


def hits_from_response(response: Any) -> list[SearchHit]:
    """Collect the cited pages from a conversation response, in order, without duplicates.

    Citations (`tool_reference` chunks) come first. Bare URLs in the answer text are only used
    when the answer has no citations at all.
    """
    cited: list[SearchHit] = []
    text_parts: list[str] = []
    for entry in getattr(response, "outputs", None) or []:
        if getattr(entry, "type", None) != "message.output":
            continue
        content = getattr(entry, "content", None)
        if isinstance(content, str):
            text_parts.append(content)
            continue
        for chunk in content or []:
            kind = getattr(chunk, "type", None)
            if kind == "tool_reference" and getattr(chunk, "url", None):
                cited.append(
                    SearchHit(
                        url=chunk.url,
                        title=getattr(chunk, "title", "") or "",
                        snippet=getattr(chunk, "description", "") or "",
                    )
                )
            elif kind == "text":
                text_parts.append(getattr(chunk, "text", "") or "")

    if not cited:
        cited = [
            SearchHit(url=url.rstrip(".,;:")) for url in _URL_IN_TEXT.findall(" ".join(text_parts))
        ]
    return _dedupe(cited)


def _dedupe(hits: list[SearchHit]) -> list[SearchHit]:
    seen: set[str] = set()
    unique: list[SearchHit] = []
    for hit in hits:
        if not hit.url.startswith(("http://", "https://")):
            continue
        key = hit.url.split("#", 1)[0].rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(hit)
    return unique
