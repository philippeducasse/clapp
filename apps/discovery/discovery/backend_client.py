"""Typed calls to the backend's /internal/discovery/* endpoints (service token auth)."""

from datetime import date, datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from discovery.config import Settings

RunStatus = Literal["RUNNING", "DONE", "FAILED", "CANCELLED"]
OrgType = Literal["FESTIVAL", "RESIDENCY", "VENUE"]


class BackendError(Exception):
    """The backend couldn't be reached or rejected a request."""


# --- Payloads (mirror discovery/serializers.py in the backend) ----------------------------


class ProgressLine(BaseModel):
    step: str
    message: str
    at: datetime | None = None


class Evidence(BaseModel):
    """One hop of `found_via`, or one page in `sources`."""

    url: str
    kind: str = ""
    title: str = ""
    snippet: str = ""


class CandidateContact(BaseModel):
    name: str = ""
    email: str = ""
    role: str = ""


class CandidateIn(BaseModel):
    org_type: OrgType
    name: str
    state: Literal["PENDING", "UNRESOLVED"] = "PENDING"
    description: str = ""
    country: str = ""
    town: str = ""
    website_url: str = ""
    subtype: str = ""
    application_type: str = ""
    application_url: str = ""
    start_date: date | None = None
    end_date: date | None = None
    estimated_start_date: date | None = None
    approximate_date: str = ""
    application_date_start: str = ""
    application_date_end: str = ""
    contacts: list[CandidateContact] = Field(default_factory=list)
    found_via: list[Evidence] = Field(default_factory=list)
    sources: list[Evidence] = Field(default_factory=list)
    relevance_reason: str = ""


class SourceIn(BaseModel):
    url: str
    kind: Literal["ARTIST_SITE", "AGGREGATOR"]
    title: str = ""
    calendar_url: str = ""
    leads_found: int = 0


class KnownEntry(BaseModel):
    name: str
    country: str = ""
    town: str = ""
    domain: str = ""
    org_type: OrgType
    source: Literal["SEED", "SUPERUSER", "CANDIDATE"]


class RunUpdateResult(BaseModel):
    status: str
    cancel_requested: bool


class CandidatesResult(BaseModel):
    created: int
    already_known: int


# --- Client --------------------------------------------------------------------------------


class BackendClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self._client = httpx.AsyncClient(
            base_url=f"{settings.backend_url.rstrip('/')}/internal/discovery/",
            headers={"Authorization": f"Bearer {settings.discovery_service_token}"},
            timeout=settings.backend_timeout_seconds,
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def update_run(
        self,
        run_id: int,
        *,
        status: RunStatus | None = None,
        progress: list[ProgressLine] | None = None,
        counters: dict[str, int] | None = None,
        plan: dict[str, Any] | None = None,
        errors: list[str] | None = None,
        error: str | None = None,
    ) -> RunUpdateResult:
        """Report progress (also the heartbeat). The answer says whether a cancel was requested."""
        body: dict[str, Any] = {}
        if status is not None:
            body["status"] = status
        if progress:
            body["progress"] = [
                line.model_dump(mode="json", exclude_none=True) for line in progress
            ]
        if counters is not None:
            body["counters"] = counters
        if plan is not None:
            body["plan"] = plan
        if errors:
            body["errors"] = errors
        if error is not None:
            body["error"] = error[:2000]
        data = await self._request("PATCH", f"runs/{run_id}/", json=body)
        return RunUpdateResult.model_validate(data)

    async def known_index(self) -> list[KnownEntry]:
        data = await self._request("GET", "known-index/")
        return [KnownEntry.model_validate(row) for row in data]

    async def post_candidates(self, run_id: int, candidates: list[CandidateIn]) -> CandidatesResult:
        body = {"candidates": [c.model_dump(mode="json", exclude_none=True) for c in candidates]}
        data = await self._request("POST", f"runs/{run_id}/candidates/", json=body)
        return CandidatesResult.model_validate(data)

    async def upsert_sources(self, sources: list[SourceIn]) -> int:
        body = {"sources": [s.model_dump(mode="json") for s in sources]}
        data = await self._request("POST", "sources/", json=body)
        return int(data["saved"])

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = await self._client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise BackendError(f"{method} {path}: backend unreachable ({exc!r})") from exc
        if response.status_code >= 400:
            raise BackendError(
                f"{method} {path}: backend answered {response.status_code}: {response.text[:300]}"
            )
        return response.json()
