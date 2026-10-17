"""Runs one discovery graph at a time as a background asyncio task and reports to the backend."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from discovery.backend_client import (
    BackendClient,
    BackendError,
    CandidateIn,
    Evidence,
    ProgressLine,
    RunStatus,
)
from discovery.config import Settings

logger = logging.getLogger(__name__)

COUNTER_NAMES = ("searches", "pages", "llm_calls", "leads", "leads_missing", "candidates")


class RunCancelled(Exception):
    """The backend asked us to stop (cancel requested, or the run was already closed)."""


class RunnerBusy(Exception):
    def __init__(self, run_id: int):
        super().__init__(f"Run {run_id} is already in progress.")
        self.run_id = run_id


class RunContext:
    """What a graph gets to work with: the run, the backend, the limits and the counters."""

    def __init__(
        self, run_id: int, starting_point: str, backend: BackendClient, settings: Settings
    ):
        self.run_id = run_id
        self.starting_point = starting_point
        self.backend = backend
        self.settings = settings
        self.counters: dict[str, int] = dict.fromkeys(COUNTER_NAMES, 0)

    async def progress(self, step: str, message: str) -> None:
        """Post a progress line (also the heartbeat). Raises RunCancelled if we should stop."""
        result = await self.backend.update_run(
            self.run_id,
            progress=[ProgressLine(step=step, message=message)],
            counters=self.counters,
        )
        if result.cancel_requested:
            raise RunCancelled()


Graph = Callable[[RunContext], Awaitable[None]]


async def stub_graph(ctx: RunContext) -> None:
    """Placeholder until the real graph exists (step 5): proves backend ↔ service ↔ frontend."""
    await ctx.progress("interpret_start", f"Starting point: {ctx.starting_point[:200]}")
    await ctx.progress("stub", "Stub graph: nothing is explored yet, posting one fake candidate.")

    candidate = CandidateIn(
        org_type="FESTIVAL",
        name=f"Stub festival (run {ctx.run_id})",
        country="Belgium",
        town="Nowhere",
        website_url=f"https://example.org/stub-festival-{ctx.run_id}",
        description="Fake candidate created by the discovery stub graph. Dismiss it.",
        relevance_reason="Test candidate: checks that the service can save candidates.",
        found_via=[Evidence(kind="stub", url="https://example.org/", title="Stub graph")],
        sources=[Evidence(kind="stub", url="https://example.org/", title="Stub graph")],
    )
    result = await ctx.backend.post_candidates(ctx.run_id, [candidate])
    ctx.counters["candidates"] += result.created
    await ctx.progress(
        "save",
        f"Saved {result.created} candidate(s), {result.already_known} already known.",
    )


class Runner:
    """Holds the single active run. A second start while one is active raises RunnerBusy (409)."""

    def __init__(self, backend: BackendClient, settings: Settings, graph: Graph = stub_graph):
        self.backend = backend
        self.settings = settings
        self.graph = graph
        self._task: asyncio.Task[None] | None = None
        self._run_id: int | None = None

    @property
    def active_run_id(self) -> int | None:
        if self._task is None or self._task.done():
            return None
        return self._run_id

    def start(self, run_id: int, starting_point: str) -> None:
        active = self.active_run_id
        if active is not None:
            raise RunnerBusy(active)
        ctx = RunContext(run_id, starting_point, self.backend, self.settings)
        self._run_id = run_id
        self._task = asyncio.create_task(self._run(ctx), name=f"discovery-run-{run_id}")

    async def wait(self) -> None:
        """Wait for the active run to finish (used by tests)."""
        if self._task is not None:
            await asyncio.shield(self._task)

    async def shutdown(self) -> None:
        """Stop the active run, if any. It is reported as FAILED."""
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self, ctx: RunContext) -> None:
        logger.info("Run %s started: %r", ctx.run_id, ctx.starting_point[:200])
        try:
            started = await self.backend.update_run(
                ctx.run_id,
                status="RUNNING",
                progress=[
                    ProgressLine(step="start", message="Discovery service picked up the run.")
                ],
                counters=ctx.counters,
            )
            if started.cancel_requested:
                raise RunCancelled()
            await self.graph(ctx)
        except RunCancelled:
            await self._finish(ctx, "CANCELLED", "Run cancelled.")
        except asyncio.CancelledError:
            await self._finish(ctx, "FAILED", "Run stopped: discovery service shutting down.")
            raise
        except Exception as exc:
            logger.exception("Run %s failed", ctx.run_id)
            await self._finish(ctx, "FAILED", f"Run failed: {exc}", error=str(exc) or repr(exc))
        else:
            await self._finish(ctx, "DONE", "Run finished.")

    async def _finish(
        self, ctx: RunContext, status: RunStatus, message: str, error: str | None = None
    ) -> None:
        """Best effort: if the backend can't be told, its heartbeat timeout marks the run FAILED."""
        logger.info("Run %s: %s", ctx.run_id, status)
        try:
            await self.backend.update_run(
                ctx.run_id,
                status=status,
                progress=[ProgressLine(step="finish", message=message)],
                counters=ctx.counters,
                error=error,
            )
        except BackendError:
            logger.exception("Run %s: could not report %s to the backend", ctx.run_id, status)
