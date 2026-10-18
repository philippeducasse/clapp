import json
from pathlib import Path

import pytest
import respx

from discovery.config import Settings

BACKEND = "http://backend.test"
INTERNAL = f"{BACKEND}/internal/discovery"
TOKEN = "test-token"
FIXTURES = Path(__file__).parent / "fixtures"


def fixture_bytes(name: str) -> bytes:
    """A saved page from tests/fixtures, as served over HTTP."""
    return (FIXTURES / name).read_bytes()


def fixture_text(name: str) -> str:
    return fixture_bytes(name).decode("utf-8")


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, backend_url=BACKEND, discovery_service_token=TOKEN)


class FakeBackend:
    """Records what the service sends to /internal/discovery/* and answers like the backend."""

    def __init__(self, router: respx.MockRouter):
        self.updates: list[dict] = []
        self.candidates: list[dict] = []
        self.sources: list[dict] = []
        self.known: list[dict] = []  # rows returned by GET known-index/
        self.cancel_after_updates: int | None = None  # answer cancel_requested=True from then on
        self.reject_batches = False  # answer 400 to POST candidates with more than one candidate
        self.status = "QUEUED"

        router.patch(url__regex=rf"{INTERNAL}/runs/\d+/$").mock(side_effect=self._update)
        router.post(url__regex=rf"{INTERNAL}/runs/\d+/candidates/$").mock(
            side_effect=self._candidates
        )
        router.get(f"{INTERNAL}/known-index/").mock(
            side_effect=lambda request: respx.MockResponse(200, json=self.known)
        )
        router.post(f"{INTERNAL}/sources/").mock(side_effect=self._sources)

    def _update(self, request):
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        body = json.loads(request.content)
        self.updates.append(body)
        if "status" in body:
            self.status = body["status"]
        cancel = (
            self.cancel_after_updates is not None and len(self.updates) >= self.cancel_after_updates
        )
        return respx.MockResponse(200, json={"status": self.status, "cancel_requested": cancel})

    def _candidates(self, request):
        body = json.loads(request.content)
        if self.reject_batches and len(body["candidates"]) > 1:
            return respx.MockResponse(400, json={"candidates": ["invalid"]})
        self.candidates.extend(body["candidates"])
        return respx.MockResponse(
            201, json={"created": len(body["candidates"]), "already_known": 0}
        )

    def _sources(self, request):
        body = json.loads(request.content)
        self.sources.extend(body["sources"])
        return respx.MockResponse(200, json={"saved": len(body["sources"])})

    @property
    def errors(self) -> list[str]:
        return [error for u in self.updates for error in u.get("errors", [])]

    @property
    def messages(self) -> list[str]:
        return [line["message"] for u in self.updates for line in u.get("progress", [])]

    @property
    def plan(self) -> dict | None:
        return next((u["plan"] for u in self.updates if "plan" in u), None)

    @property
    def statuses(self) -> list[str]:
        return [u["status"] for u in self.updates if "status" in u]

    @property
    def steps(self) -> list[str]:
        return [line["step"] for u in self.updates for line in u.get("progress", [])]


@pytest.fixture
def backend():
    with respx.mock(assert_all_called=False) as router:
        yield FakeBackend(router)


# --- graph tests: one respx router for the backend and the fake web -------------------------
# Use `web_backend` + `web` (not `backend`, which opens its own router).


@pytest.fixture
def graph_settings(tmp_path) -> Settings:
    return Settings(
        _env_file=None,
        backend_url=BACKEND,
        discovery_service_token=TOKEN,
        cache_dir=str(tmp_path / "cache"),
        per_domain_interval_seconds=0,
    )


@pytest.fixture
def router():
    with respx.mock(assert_all_called=False) as mock_router:
        yield mock_router


@pytest.fixture
def web_backend(router) -> FakeBackend:
    return FakeBackend(router)


@pytest.fixture
def web(router, web_backend):
    """The fake web. Its routes come after the backend's; call `web.finish()` when set up."""
    from tests.graph_fakes import FakeWeb

    return FakeWeb(router)


@pytest.fixture
async def make_deps(graph_settings, web_backend):
    """Build a `Deps` for calling nodes directly: real Fetcher and BackendClient (both served
    by respx), scripted LLM answers, a fake search."""
    from datetime import date

    from discovery.backend_client import BackendClient
    from discovery.graph.deps import Deps
    from discovery.llm import RunBudget
    from discovery.runner import RunContext
    from discovery.tools.fetch import Fetcher
    from tests.graph_fakes import FakeSearch, scripted_models

    closers = []

    def unexpected(purpose, prompt):
        raise AssertionError(f"unexpected LLM call: {purpose}")

    async def _make(responder=unexpected, search=None, **overrides) -> Deps:
        settings = graph_settings.model_copy(update=overrides)
        client = BackendClient(settings)
        fetcher = Fetcher(settings)
        closers.extend([client, fetcher])
        ctx = RunContext(1, "test", client, settings)
        return Deps(
            ctx=ctx,
            budget=RunBudget(settings, ctx.counters),
            fetcher=fetcher,
            search=search or FakeSearch(),
            models=scripted_models(responder),
            today=date(2026, 10, 18),
        )

    yield _make
    for closer in closers:
        await closer.aclose()
