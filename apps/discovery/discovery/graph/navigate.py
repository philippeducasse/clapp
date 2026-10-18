"""navigate(goal): follow the links of one site towards a goal (calendar, contact, application).

1. Keyword ranking first (`tools/links.rank_links`): for each goal, the best link whose anchor
   text (or several words of its URL) matches a keyword is a clear match, followed without asking
   the LLM.
2. No clear match for any goal: the LLM picks link **numbers** from the top 20, or none. It never
   writes a URL.
3. At most `max_pages` links, and never more than MAX_HOPS_PER_SITE links per site in the run.
"""

from collections.abc import Sequence

from discovery.graph.deps import Deps
from discovery.prompts import pick_link
from discovery.prompts.pick_link import LinkChoice
from discovery.tools.fetch import FetchError, Page
from discovery.tools.links import TEXT_WEIGHT, Goal, Link, extract_links, rank_links

CLEAR_SCORE = TEXT_WEIGHT  # the anchor text matches, or at least two words of the URL do
LLM_CHOICES = 20


async def navigate(
    deps: Deps, page: Page, goals: Sequence[Goal], max_pages: int, step: str = "navigate"
) -> list[tuple[Goal, Page]]:
    """Pages reached from `page` for `goals`, as (goal, page), in the order followed.

    Raises BudgetExceeded (pages or LLM calls); fetch errors are reported and skipped.
    """
    allowed = min(max_pages, deps.hops_left(page.final_url))
    if allowed <= 0:
        return []
    links = [
        link for link in extract_links(page.html, page.final_url) if not deps.fetched(link.url)
    ]
    if not links:
        return []

    chosen = clear_matches(links, goals, allowed)
    if not chosen:
        chosen = await llm_choice(deps, page, links, goals, allowed)

    reached: list[tuple[Goal, Page]] = []
    for goal, link in chosen:
        if not deps.take_hop(page.final_url):
            break
        try:
            target = await deps.fetch(link.url)
        except FetchError as exc:
            await deps.error(step, f"{link.url}: {exc.reason}")
            continue
        if target.is_empty:
            await deps.progress(step, f"Empty content, skipped: {link.url}")
            continue
        reached.append((goal, target))
    return reached


def clear_matches(
    links: list[Link], goals: Sequence[Goal], allowed: int
) -> list[tuple[Goal, Link]]:
    """The best clearly matching link for each goal (different links), in goal order."""
    chosen: list[tuple[Goal, Link]] = []
    taken: set[str] = set()
    for goal in goals:
        for link in rank_links(links, [goal]):
            if link.score < CLEAR_SCORE:
                break
            if link.url not in taken:
                chosen.append((goal, link))
                taken.add(link.url)
                break
    return chosen[:allowed]


async def llm_choice(
    deps: Deps, page: Page, links: list[Link], goals: Sequence[Goal], allowed: int
) -> list[tuple[Goal, Link]]:
    top = rank_links(links, list(goals))[:LLM_CHOICES]
    answer = await deps.ask(
        "pick_link", LinkChoice, pick_link.messages(list(goals), page.final_url, top, allowed)
    )
    chosen: list[tuple[Goal, Link]] = []
    for number in answer.numbers:
        if not 1 <= number <= len(top):
            continue  # not a number from the list: ignored
        link = top[number - 1]
        if any(link.url == other.url for _, other in chosen):
            continue
        chosen.append((best_goal(link, goals), link))
        if len(chosen) >= allowed:
            break
    return chosen


def best_goal(link: Link, goals: Sequence[Goal]) -> Goal:
    """The goal whose keywords match `link` best (the first goal on a tie)."""
    scores = [(rank_links([link], [goal])[0].score, -index) for index, goal in enumerate(goals)]
    return goals[-max(scores)[1]]
