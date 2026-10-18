import asyncio

import httpx
import pytest

from discovery.app import create_app
from discovery.runner import stub_graph
from tests.conftest import TOKEN


@pytest.fixture
async def make_client(settings):
    """Builds the app with a given graph, runs its lifespan and returns (client, runner)."""
    stack = []

    async def _make(**kwargs):
        app = create_app(settings, **kwargs)
        lifespan = app.router.lifespan_context(app)
        await lifespan.__aenter__()
        stack.append(lifespan)
        client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://svc")
        return client, app.state.runner

    yield _make
    for lifespan in stack:
        await lifespan.__aexit__(None, None, None)


AUTH = {"Authorization": f"Bearer {TOKEN}"}


async def test_health(make_client, backend):
    client, _ = await make_client()
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "active_run": None}


@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Bearer wrong"}, {"Authorization": "Basic abc"}],
)
async def test_start_run_rejects_missing_or_wrong_token(make_client, backend, headers):
    client, _ = await make_client()
    response = await client.post(
        "/runs", json={"run_id": 1, "starting_point": "x"}, headers=headers
    )
    assert response.status_code in (401, 403)
    assert backend.updates == []


async def test_start_run_refused_when_no_token_configured(settings, make_client, backend):
    settings.discovery_service_token = ""
    client, _ = await make_client()
    response = await client.post(
        "/runs", json={"run_id": 1, "starting_point": "x"}, headers={"Authorization": "Bearer "}
    )
    assert response.status_code in (401, 403)


async def test_start_run_validates_body(make_client, backend):
    client, _ = await make_client()
    response = await client.post("/runs", json={"run_id": 1, "starting_point": ""}, headers=AUTH)
    assert response.status_code == 422


async def test_start_run_returns_202_and_runs_stub_graph(make_client, backend):
    client, runner = await make_client(graph=stub_graph)
    response = await client.post(
        "/runs", json={"run_id": 7, "starting_point": "https://some-juggler.com"}, headers=AUTH
    )
    assert response.status_code == 202
    assert response.json() == {"run_id": 7}

    await runner.wait()
    assert backend.statuses == ["RUNNING", "DONE"]
    assert len(backend.candidates) == 1
    assert backend.candidates[0]["name"] == "Stub festival (run 7)"


async def test_second_run_while_active_gets_409(make_client, backend):
    release = asyncio.Event()

    async def slow_graph(ctx):
        await release.wait()

    client, runner = await make_client(graph=slow_graph)
    first = await client.post("/runs", json={"run_id": 1, "starting_point": "a"}, headers=AUTH)
    assert first.status_code == 202
    assert (await client.get("/health")).json()["active_run"] == 1

    second = await client.post("/runs", json={"run_id": 2, "starting_point": "b"}, headers=AUTH)
    assert second.status_code == 409
    assert second.json()["run_id"] == 1

    release.set()
    await runner.wait()
    third = await client.post("/runs", json={"run_id": 3, "starting_point": "c"}, headers=AUTH)
    assert third.status_code == 202
    await runner.wait()


async def test_shutdown_reports_active_run_as_failed(settings, backend):
    async def endless_graph(ctx):
        await asyncio.Event().wait()

    app = create_app(settings, graph=endless_graph)
    async with app.router.lifespan_context(app):
        client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://svc")
        await client.post("/runs", json={"run_id": 1, "starting_point": "a"}, headers=AUTH)
        await asyncio.sleep(0.01)

    assert backend.statuses == ["RUNNING", "FAILED"]
    assert "shutting down" in backend.updates[-1]["progress"][0]["message"]


async def test_graph_selection(settings, backend):
    from discovery.graph.build import discovery_graph

    for use_stub, expected in ((False, discovery_graph), (True, stub_graph)):
        app = create_app(settings.model_copy(update={"use_stub_graph": use_stub}))
        async with app.router.lifespan_context(app):
            assert app.state.runner.graph is expected
