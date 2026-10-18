import asyncio

import httpx
import pytest
import respx

from discovery.backend_client import BackendClient, BackendError, SourceIn
from discovery.runner import RunCancelled, RunContext, Runner, RunnerBusy


@pytest.fixture
async def client(settings):
    backend_client = BackendClient(settings)
    yield backend_client
    await backend_client.aclose()


async def test_stub_graph_posts_progress_and_one_candidate(client, settings, backend):
    runner = Runner(client, settings)
    runner.start(3, "street theatre festivals in Belgium")
    await runner.wait()

    assert backend.statuses == ["RUNNING", "DONE"]
    assert backend.steps == ["start", "interpret_start", "stub", "save", "finish"]
    assert backend.updates[-1]["counters"]["candidates"] == 1
    [candidate] = backend.candidates
    assert candidate["org_type"] == "FESTIVAL"
    assert candidate["found_via"][0]["url"] == "https://example.org/"
    assert "start_date" not in candidate  # None values are not sent


async def test_cancel_requested_stops_the_run(client, settings, backend):
    backend.cancel_after_updates = 2  # the first progress line from the graph answers "cancel"
    runner = Runner(client, settings)
    runner.start(3, "x")
    await runner.wait()

    assert backend.statuses == ["RUNNING", "CANCELLED"]
    assert backend.candidates == []


async def test_cancel_before_start(client, settings, backend):
    backend.cancel_after_updates = 1
    called = False

    async def graph(ctx):
        nonlocal called
        called = True

    runner = Runner(client, settings, graph)
    runner.start(3, "x")
    await runner.wait()
    assert not called
    assert backend.statuses == ["RUNNING", "CANCELLED"]


async def test_graph_error_marks_run_failed(client, settings, backend):
    async def broken(ctx):
        await ctx.progress("visit_page", "Visiting")
        raise ValueError("boom")

    runner = Runner(client, settings, broken)
    runner.start(3, "x")
    await runner.wait()

    assert backend.statuses == ["RUNNING", "FAILED"]
    assert backend.updates[-1]["error"] == "boom"
    assert runner.active_run_id is None


async def test_runner_is_busy_while_a_run_is_active(client, settings, backend):
    release = asyncio.Event()

    async def graph(ctx):
        await release.wait()

    runner = Runner(client, settings, graph)
    runner.start(1, "a")
    with pytest.raises(RunnerBusy):
        runner.start(2, "b")
    release.set()
    await runner.wait()
    runner.start(2, "b")
    await runner.wait()


async def test_backend_unreachable_on_finish_does_not_crash(settings):
    with respx.mock() as router:
        router.patch(url__regex=r".*").mock(side_effect=httpx.ConnectError("down"))
        backend_client = BackendClient(settings)
        runner = Runner(backend_client, settings)
        runner.start(1, "a")
        await runner.wait()  # no exception: the backend's heartbeat timeout will catch it
        await backend_client.aclose()


async def test_context_progress_raises_when_cancelled(client, settings, backend):
    backend.cancel_after_updates = 1
    ctx = RunContext(1, "a", client, settings)
    with pytest.raises(RunCancelled):
        await ctx.progress("x", "y")


async def test_backend_error_status_raises(settings):
    with respx.mock() as router:
        router.get(url__regex=r".*known-index/$").respond(401, json={"detail": "nope"})
        backend_client = BackendClient(settings)
        with pytest.raises(BackendError, match="401"):
            await backend_client.known_index()
        await backend_client.aclose()


async def test_known_index_and_sources(settings):
    with respx.mock() as router:
        router.get(url__regex=r".*known-index/$").respond(
            json=[
                {
                    "name": "Chalon dans la rue",
                    "country": "France",
                    "town": "Chalon",
                    "domain": "chalondanslarue.com",
                    "org_type": "FESTIVAL",
                    "source": "SEED",
                }
            ]
        )
        sources = router.post(url__regex=r".*sources/$").respond(json={"saved": 1})
        backend_client = BackendClient(settings)
        [entry] = await backend_client.known_index()
        assert entry.domain == "chalondanslarue.com"

        saved = await backend_client.upsert_sources(
            [SourceIn(url="https://some-juggler.com", kind="ARTIST_SITE", leads_found=4)]
        )
        assert saved == 1
        assert sources.calls.last.request.headers["Authorization"] == "Bearer test-token"
        await backend_client.aclose()


async def test_errors_plan_and_notes_are_reported(client, settings, backend):
    async def graph(ctx):
        await ctx.set_plan({"goal": "g"})
        await ctx.report_error("visit_page", "https://x.org: robots")
        ctx.add_note("budget reached: pages")
        ctx.add_note("budget reached: pages")

    runner = Runner(client, settings, graph)
    runner.start(3, "x")
    await runner.wait()

    assert backend.plan == {"goal": "g"}
    assert backend.errors == ["visit_page: https://x.org: robots"]
    assert backend.updates[-1]["status"] == "DONE"
    assert backend.messages[-1] == "Run finished (budget reached: pages)."
