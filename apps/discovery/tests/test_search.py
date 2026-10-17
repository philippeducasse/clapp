from types import SimpleNamespace

import pytest
from mistralai.client.models import ConversationResponse

from discovery.config import Settings
from discovery.llm import BudgetExceeded, RunBudget
from discovery.tools.search import (
    MistralSearch,
    SearchError,
    SearchHit,
    SearchProvider,
    hits_from_response,
)

ENTRY = {
    "object": "entry",
    "id": "e1",
    "created_at": "2026-01-01T00:00:00Z",
    "completed_at": "2026-01-01T00:00:01Z",
}


def conversation(content, *, with_tool_entry: bool = True) -> ConversationResponse:
    """A response as the Mistral API returns it, parsed by the real SDK model."""
    outputs = []
    if with_tool_entry:
        outputs.append({**ENTRY, "type": "tool.execution", "name": "web_search", "arguments": "{}"})
    outputs.append(
        {**ENTRY, "type": "message.output", "role": "assistant", "model": "m", "content": content}
    )
    return ConversationResponse.model_validate(
        {
            "object": "conversation.response",
            "conversation_id": "conv_1",
            "outputs": outputs,
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
    )


def ref(url: str, title: str = "", description: str | None = None) -> dict:
    chunk = {"type": "tool_reference", "tool": "web_search", "title": title, "url": url}
    if description is not None:
        chunk["description"] = description
    return chunk


class FakeConversations:
    def __init__(self, response=None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[dict] = []

    async def start_async(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


def fake_client(conversations: FakeConversations):
    return SimpleNamespace(beta=SimpleNamespace(conversations=conversations))


@pytest.fixture
def settings():
    return Settings(_env_file=None, mistral_api_key="k", mistral_search_model="search-m")


def test_hits_keep_the_citation_urls_titles_and_snippets():
    response = conversation(
        [
            {"type": "text", "text": "Two festivals:"},
            ref("https://festa.be/", "Festival A", "Street theatre in Namur"),
            {"type": "text", "text": " and "},
            ref("https://festb.fr/programme", "Festival B"),
        ]
    )
    assert hits_from_response(response) == [
        SearchHit(url="https://festa.be/", title="Festival A", snippet="Street theatre in Namur"),
        SearchHit(url="https://festb.fr/programme", title="Festival B", snippet=""),
    ]


def test_hits_are_deduplicated_and_only_http():
    response = conversation(
        [
            ref("https://festa.be/", "A"),
            ref("https://festa.be", "A again"),
            ref("https://festa.be/#dates", "A anchor"),
            ref("ftp://files.example/x", "ftp"),
        ]
    )
    assert [hit.url for hit in hits_from_response(response)] == ["https://festa.be/"]


def test_urls_in_the_text_are_used_only_without_citations():
    no_citations = conversation("See https://festa.be/ and (https://festb.fr/x).")
    assert [h.url for h in hits_from_response(no_citations)] == [
        "https://festa.be/",
        "https://festb.fr/x",
    ]

    with_citations = conversation(
        [{"type": "text", "text": "See https://other.org/"}, ref("https://festa.be/", "A")]
    )
    assert [h.url for h in hits_from_response(with_citations)] == ["https://festa.be/"]


def test_empty_response_gives_no_hits():
    assert hits_from_response(conversation([], with_tool_entry=False)) == []
    assert hits_from_response(SimpleNamespace(outputs=None)) == []


async def test_search_calls_mistral_with_web_search_and_counts_a_search(settings):
    conversations = FakeConversations(conversation([ref("https://festa.be/", "A")]))
    search = MistralSearch(settings, client=fake_client(conversations))
    budget = RunBudget(settings)

    hits = await search.search("street festivals Belgium 2027", budget)

    assert [h.url for h in hits] == ["https://festa.be/"]
    assert budget.counters["searches"] == 1
    call = conversations.calls[0]
    assert call["model"] == "search-m"
    assert call["inputs"] == "street festivals Belgium 2027"
    assert call["tools"] == [{"type": "web_search"}]
    assert call["store"] is False


async def test_search_refuses_when_the_budget_is_spent(settings):
    conversations = FakeConversations(conversation([]))
    search = MistralSearch(settings, client=fake_client(conversations))
    budget = RunBudget(Settings(_env_file=None, max_searches=0))

    with pytest.raises(BudgetExceeded):
        await search.search("q", budget)
    assert conversations.calls == []


async def test_search_errors_are_wrapped(settings):
    search = MistralSearch(
        settings, client=fake_client(FakeConversations(error=RuntimeError("boom")))
    )
    with pytest.raises(SearchError, match="boom"):
        await search.search("q")


def test_mistral_search_is_a_search_provider(settings):
    provider: SearchProvider = MistralSearch(settings)
    assert callable(provider.search)
