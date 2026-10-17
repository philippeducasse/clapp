import json

import pytest
import respx

from discovery.config import Settings

BACKEND = "http://backend.test"
INTERNAL = f"{BACKEND}/internal/discovery"
TOKEN = "test-token"


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, backend_url=BACKEND, discovery_service_token=TOKEN)


class FakeBackend:
    """Records what the service sends to /internal/discovery/* and answers like the backend."""

    def __init__(self, router: respx.MockRouter):
        self.updates: list[dict] = []
        self.candidates: list[dict] = []
        self.cancel_after_updates: int | None = None  # answer cancel_requested=True from then on
        self.status = "QUEUED"

        router.patch(url__regex=rf"{INTERNAL}/runs/\d+/$").mock(side_effect=self._update)
        router.post(url__regex=rf"{INTERNAL}/runs/\d+/candidates/$").mock(
            side_effect=self._candidates
        )
        router.get(f"{INTERNAL}/known-index/").respond(json=[])

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
        self.candidates.extend(body["candidates"])
        return respx.MockResponse(
            201, json={"created": len(body["candidates"]), "already_known": 0}
        )

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
