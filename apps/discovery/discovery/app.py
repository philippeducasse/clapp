"""HTTP entry point of the discovery service.

Only two endpoints:
- POST /runs    called by the backend (discovery/service_client.py) to start a run.
- GET  /health  called by Docker's healthcheck.

Everything else goes the other way: the service calls the backend's /internal/discovery/*
endpoints (see backend_client.py) to report progress and save candidates.

FastAPI in a nutshell, for reading this file:
- `@app.get(path)` / `@app.post(path)` register a function as the handler for that URL.
- Handler parameters are filled in by FastAPI from their type annotations:
    * a pydantic model (`body: RunRequest`) is parsed and validated from the JSON body;
      invalid input gets an automatic 422 response, the handler never runs.
    * `Request` gives the raw request (and through it, `request.app`).
    * `Annotated[X, Depends(func)]` calls `func` first and passes its return value in
      ("dependency injection"). Dependencies can raise HTTPException to stop the request.
- The handler's return annotation (or `response_model`) describes the response; FastAPI
  serialises the returned pydantic model to JSON.
- Handlers are `async def`: they run on the event loop, which is what lets the runner
  start a background asyncio task from inside a request.
- Interactive docs are generated at /docs while running locally.
"""

import hmac
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from discovery.backend_client import BackendClient
from discovery.config import Settings, get_settings
from discovery.runner import Graph, Runner, RunnerBusy, stub_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


# --- Request / response bodies -------------------------------------------------------------
# Pydantic models: FastAPI validates incoming JSON against them and uses them to build the
# OpenAPI schema shown at /docs.


class RunRequest(BaseModel):
    """Body of POST /runs, sent by the backend."""

    run_id: int  # DiscoveryRun.pk in the backend
    starting_point: str = Field(min_length=1, max_length=2000)


class RunAccepted(BaseModel):
    """202: the run was accepted and is now exploring in the background."""

    run_id: int


class RunConflict(BaseModel):
    """409: another run is still active; `run_id` is that other run."""

    error: str
    run_id: int


class Health(BaseModel):
    status: str
    active_run: int | None  # id of the run in progress, if any


# Reads the `Authorization: Bearer <token>` header. With auto_error=False it returns None
# when the header is missing instead of answering 403 itself, so require_token below can
# answer 401 consistently.
bearer = HTTPBearer(auto_error=False)


def create_app(
    settings: Settings | None = None,
    graph: Graph = stub_graph,
    backend_transport: httpx.AsyncBaseTransport | None = None,
) -> FastAPI:
    """Build the FastAPI application.

    A factory (rather than a module-level app only) so tests can pass their own settings,
    a fake graph, or a mocked HTTP transport for calls to the backend.
    """
    settings = settings or get_settings()

    # Lifespan: code before `yield` runs once when the server starts, code after `yield`
    # runs once when it shuts down. It's FastAPI's replacement for the old
    # @app.on_event("startup") / ("shutdown") hooks.
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        # One HTTP client to the backend and one runner for the whole process.
        # `app.state` is a free-form place to keep such shared objects.
        backend = BackendClient(settings, transport=backend_transport)
        app.state.runner = Runner(backend, settings, graph)
        yield  # the server handles requests while we're paused here
        # Shutdown: stop the active run (it's reported as FAILED) and close the client.
        await app.state.runner.shutdown()
        await backend.aclose()

    app = FastAPI(title="clapp discovery", lifespan=lifespan)

    # --- Dependencies ----------------------------------------------------------------------
    # Small functions FastAPI runs before a handler. Declared inside create_app so they can
    # use `settings` from the enclosing scope.

    def require_token(
        # FastAPI calls `bearer` first and passes its result here.
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    ) -> None:
        """Reject the request with 401 unless it carries the shared service token.

        If no token is configured, every request is rejected (fail closed).
        `hmac.compare_digest` compares in constant time, so the token can't be guessed by
        timing the responses.
        """
        expected = settings.discovery_service_token
        if (
            credentials is None
            or not expected
            or not hmac.compare_digest(credentials.credentials.encode(), expected.encode())
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid discovery service token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_runner(request: Request) -> Runner:
        """The Runner created in `lifespan`. `app.state` is untyped; this gives it a type."""
        runner: Runner = request.app.state.runner
        return runner

    # --- Endpoints -------------------------------------------------------------------------

    @app.get("/health")
    async def health(runner: Annotated[Runner, Depends(get_runner)]) -> Health:
        """Liveness check for Docker. No token needed: the service isn't exposed publicly."""
        return Health(status="ok", active_run=runner.active_run_id)

    @app.post(
        "/runs",
        status_code=status.HTTP_202_ACCEPTED,  # default status for a successful response
        # `dependencies=[...]` runs require_token before the handler without passing its
        # (None) result in; it only matters if it raises.
        dependencies=[Depends(require_token)],
        # Documents the extra response in /docs; it doesn't change behaviour.
        responses={status.HTTP_409_CONFLICT: {"model": RunConflict}},
    )
    async def start_run(
        body: RunRequest,  # parsed and validated from the JSON body (422 if invalid)
        runner: Annotated[Runner, Depends(get_runner)],
        response: Response,  # lets the handler change the status code
    ) -> RunAccepted | RunConflict:
        """Accept the run and explore in the background. 409 if another run is active.

        Returns immediately: `runner.start` only schedules an asyncio task. The run reports
        its progress to the backend by itself.
        """
        try:
            runner.start(body.run_id, body.starting_point)
        except RunnerBusy as exc:
            response.status_code = status.HTTP_409_CONFLICT
            return RunConflict(error=str(exc), run_id=exc.run_id)
        return RunAccepted(run_id=body.run_id)

    return app


# The app uvicorn / `fastapi dev` serve: `uvicorn discovery.app:app --port 8001`.
app = create_app()
