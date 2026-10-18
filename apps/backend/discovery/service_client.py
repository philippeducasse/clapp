"""Calls from the backend to the discovery service (apps/discovery)."""

import httpx
from django.conf import settings

from discovery.models import DiscoveryRun


class DiscoveryServiceError(Exception):
    pass


def start_run(run: DiscoveryRun) -> None:
    """Ask the service to start exploring. Returns once the service has accepted the run."""
    if not settings.DISCOVERY_SERVICE_TOKEN:
        raise DiscoveryServiceError("DISCOVERY_SERVICE_TOKEN is not set on the backend.")
    try:
        response = httpx.post(
            f"{settings.DISCOVERY_SERVICE_URL.rstrip('/')}/runs",
            json={"run_id": run.pk, "starting_point": run.starting_point},
            headers={"Authorization": f"Bearer {settings.DISCOVERY_SERVICE_TOKEN}"},
            timeout=5,
        )
    except httpx.HTTPError as exc:
        raise DiscoveryServiceError(f"Discovery service unreachable: {exc}") from exc

    if response.status_code >= 400:
        raise DiscoveryServiceError(
            f"Discovery service refused the run ({response.status_code}): {response.text[:200]}"
        )
