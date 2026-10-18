"""check_known: drop the leads clapp already has, then fan out one research_org per missing lead."""

from typing import Any

from langgraph.runtime import Runtime
from langgraph.types import Send

from discovery.graph.deps import Deps
from discovery.graph.state import DiscoveryState, Lead


async def check_known(state: DiscoveryState, runtime: Runtime[Deps]) -> dict[str, Any]:
    deps = runtime.context
    leads = state.get("leads") or []
    missing: list[Lead] = []
    known: list[str] = []
    for lead in leads:
        match = deps.known.match(lead.name, lead.country, lead.website_url)
        if match is None:
            missing.append(lead)
        else:
            known.append(
                lead.name if match.entry.name == lead.name else f"{lead.name} = {match.entry.name}"
            )

    counters = deps.ctx.counters
    counters["leads"] = len(leads)
    counters["leads_missing"] = len(missing)
    limit = deps.settings.max_leads
    to_research, left_out = missing[:limit], missing[limit:]

    known_text = f" ({', '.join(known)[:400]})" if known else ""
    await deps.progress(
        "check_known",
        f"{len(leads)} lead(s): {len(known)} already in clapp{known_text}, {len(missing)} missing.",
    )
    if left_out:
        deps.ctx.add_note(f"{len(left_out)} lead(s) not researched (limit {limit})")
        await deps.progress(
            "check_known",
            f"Lead limit ({limit}) reached; not researched: "
            f"{', '.join(lead.name for lead in left_out)[:600]}",
        )
    return {"missing": to_research}


def fan_out(state: DiscoveryState) -> list[Send] | str:
    """One research_org per missing lead, run in parallel (up to RESEARCH_CONCURRENCY)."""
    missing = state.get("missing") or []
    if not missing:
        return "dedupe_candidates"
    return [Send("research_org", {"lead": lead, "goal": state["goal"]}) for lead in missing]
