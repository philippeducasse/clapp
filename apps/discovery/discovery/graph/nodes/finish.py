"""dedupe_candidates and save: the end of the run."""

from typing import Any

from langgraph.runtime import Runtime

from discovery.backend_client import BackendError, CandidateIn, CandidatesResult
from discovery.graph.deps import Deps
from discovery.graph.leads import dedupe_candidates as dedupe
from discovery.graph.state import DiscoveryState


async def dedupe_candidates(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    """One candidate per organisation, and none that clapp turns out to have under the name or
    website found during research."""
    deps = runtime.context
    candidates = state.get("candidates") or []
    unique = dedupe(candidates)
    kept: list[CandidateIn] = []
    known: list[str] = []
    for candidate in unique:
        if deps.known.match(candidate.name, candidate.country, candidate.website_url):
            known.append(candidate.name)
        else:
            kept.append(candidate)
    merged = len(candidates) - len(unique)
    if merged or known:
        names = f" ({', '.join(known)})" if known else ""
        await deps.progress(
            "dedupe_candidates",
            f"{merged} duplicate(s) merged; {len(known)} already in clapp{names}.",
        )
    return {"final_candidates": kept}


async def save(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    """POST the candidates and sources to the backend. A batch the backend refuses is retried
    one candidate at a time, so one bad record doesn't lose the others."""
    deps = runtime.context
    ctx = deps.ctx
    candidates: list[CandidateIn] = state.get("final_candidates") or []

    created = already_known = 0
    if candidates:
        try:
            result = await ctx.backend.post_candidates(ctx.run_id, candidates)
            created, already_known = result.created, result.already_known
        except BackendError as exc:
            await deps.error("save", f"Saving all candidates at once failed: {exc}")
            for candidate in candidates:
                single = await _post_one(deps, candidate)
                created += single.created
                already_known += single.already_known
    ctx.counters["candidates"] = created

    sources = state.get("sources") or []
    if sources:
        try:
            await ctx.backend.upsert_sources(sources)
        except BackendError as exc:
            await deps.error("save", f"Saving sources failed: {exc}")

    pending = sum(c.state == "PENDING" for c in candidates)
    unresolved = sum(c.state == "UNRESOLVED" for c in candidates)
    await deps.progress(
        "save",
        f"Saved {created} candidate(s) ({pending} to review, {unresolved} unresolved), "
        f"{already_known} already known.",
    )
    return {}


async def _post_one(deps: Deps, candidate: CandidateIn) -> CandidatesResult:
    try:
        return await deps.ctx.backend.post_candidates(deps.ctx.run_id, [candidate])
    except BackendError as exc:
        await deps.error("save", f"{candidate.name}: {exc}")
        return CandidatesResult(created=0, already_known=0)
