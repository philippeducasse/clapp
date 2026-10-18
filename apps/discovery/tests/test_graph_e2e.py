"""End to end: the whole graph on a small fake web, through the Runner.

Artist site → calendar listing 4 festivals, 2 of them already known → festival sites → contact
and application pages.
"""

import re
from datetime import date

import pytest

from discovery.backend_client import BackendClient
from discovery.graph.build import make_discovery_graph
from discovery.runner import Runner
from discovery.tools.fetch import Fetcher
from discovery.tools.search import SearchHit
from tests.graph_fakes import FakeSearch, LLMLog, link_number, scripted_models

ARTIST = "https://lesjongleurs.fr"
FDR = "https://www.festival-des-rues.be"
SFB = "https://strassenfest-bergheim.de"

KNOWN = [
    {
        "name": "Chalon dans la Rue",
        "country": "France",
        "town": "Chalon-sur-Saône",
        "domain": "chalondanslarue.com",
        "org_type": "FESTIVAL",
        "source": "SEED",
    },
    {
        "name": "Fête de la Jongle",
        "country": "Belgium",
        "town": "Tournai",
        "domain": "",
        "org_type": "FESTIVAL",
        "source": "CANDIDATE",
    },
]

SFB_SEARCH = [
    SearchHit(url="https://www.facebook.com/strassenfest", title="Straßenfest | Facebook"),
    SearchHit(url=f"{SFB}/", title="Straßenfest Bergheim", snippet="Straßentheater im August"),
    SearchHit(url="https://www.ksta.de/bergheim-strassenfest", title="News"),
]


def page_url(prompt: str) -> str:
    match = re.search(r'<page url="([^"]+)"', prompt)
    return match.group(1) if match else ""


def scenario(purpose: str, prompt: str):
    """The LLM's answers for the fake web."""
    if purpose == "classify":
        if page_url(prompt).startswith(ARTIST):
            return {"kind": "ARTIST_SITE", "lists_events": False, "reason": "juggling company"}
        return {"kind": "IRRELEVANT"}
    if purpose == "extract_leads":
        return {
            "leads": [
                {
                    "name": "Festival des Rues",
                    "org_type": "FESTIVAL",
                    "town": "Namur",
                    "country": "Belgium",
                    "dates": "12-14 juin 2026",
                    "link_number": link_number(prompt, f"{FDR}/"),
                },
                {
                    "name": "Chalon dans la Rue",
                    "org_type": "FESTIVAL",
                    "town": "Chalon-sur-Saône",
                    "country": "France",
                    "link_number": link_number(prompt, "https://chalondanslarue.com/"),
                },
                {
                    "name": "Fête de la Jongle",
                    "org_type": "FESTIVAL",
                    "town": "Tournai",
                    "country": "Belgium",
                },
                {
                    "name": "Straßenfest Bergheim",
                    "org_type": "FESTIVAL",
                    "town": "Bergheim",
                    "country": "Germany",
                    "dates": "8-10 août 2026",
                    "link_number": link_number(prompt, "https://www.facebook.com/strassenfest"),
                },
            ]
        }
    if purpose == "pick_website":
        return {"number": link_number(prompt, f"{SFB}/"), "reason": "official site"}
    if purpose == "extract_org" and "Found as: Festival des Rues" in prompt:
        return {
            "name": "Festival des Rues de Namur",
            "org_type": "FESTIVAL",
            "country": "Belgium",
            "town": "Namur",
            "description": "Three days of street theatre, circus and music in Namur.",
            "subtype": "STREET",
            "application_type": "FORM",
            "application_url": "https://forms.gle/fdr2027",
            "start_date": "2027-06-11",
            "end_date": "2027-06-13",
            "approximate_date": "mid June",
            "estimated_start_date": "2027-06-11",
            "application_date_end": "2027-01-31",
            "contacts": [
                {"email": "programmation@festival-des-rues.be", "role": "Programming"},
                {"email": "director@festival-des-rues.be", "name": "Invented"},
            ],
            "relevance_reason": "Street festival where Les Jongleurs played in 2026.",
        }
    if purpose == "extract_org" and "Found as: Straßenfest Bergheim" in prompt:
        return {
            "name": "Straßenfest Bergheim",
            "org_type": "FESTIVAL",
            "country": "Germany",
            "town": "Bergheim",
            "subtype": "street festival",  # not a valid choice: dropped
            "application_type": "EMAIL",
            "start_date": "2027-08-07",
            "end_date": "2027-08-09",
            "contacts": [
                {
                    "email": "info@strassenfest-bergheim.de",
                    "name": "Anna Schmidt",
                    "role": "Artistic director",
                }
            ],
        }
    raise AssertionError(f"unexpected LLM call: {purpose}")


def serve(web, backend, broken_festival_site: bool = False) -> None:
    backend.known = KNOWN
    web.page(f"{ARTIST}/", "artist_home.html")
    web.page(f"{ARTIST}/agenda/", "artist_agenda.html")
    if broken_festival_site:
        web.broken(r"https://www\.festival-des-rues\.be/.*")
    else:
        web.page(f"{FDR}/", "fdr_home.html")
        web.page(f"{FDR}/contact/", "fdr_contact.html")
        web.page(f"{FDR}/appel-a-candidatures/", "fdr_appel.html")
    web.page(f"{SFB}/", "sfb_home.html")
    web.page(f"{SFB}/kontakt/", "sfb_kontakt.html")
    web.finish()


@pytest.fixture
def fake_web(web, web_backend):
    serve(web, web_backend)
    return web


async def run(settings, starting_point, responder=scenario, search=None, **overrides):
    settings = settings.model_copy(update=overrides)
    llm = LLMLog(responder)
    search = search or FakeSearch({"Straßenfest Bergheim": SFB_SEARCH})
    graph = make_discovery_graph(
        fetcher_factory=Fetcher,
        search=search,
        models=scripted_models(llm),
        today=date(2026, 10, 18),
    )
    client = BackendClient(settings)
    runner = Runner(client, settings, graph)
    runner.start(42, starting_point)
    await runner.wait()
    await client.aclose()
    return llm, search


def by_name(candidates: list[dict]) -> dict[str, dict]:
    return {candidate["name"]: candidate for candidate in candidates}


async def test_artist_calendar_to_two_candidates(graph_settings, fake_web, web_backend):
    llm, search = await run(graph_settings, f"{ARTIST}/")
    backend = web_backend

    assert backend.statuses == ["RUNNING", "DONE"]
    assert backend.errors == []
    assert backend.plan == {
        "urls": [f"{ARTIST}/"],
        "goal": backend.plan["goal"],
        "org_types": ["FESTIVAL"],
        "countries": [],
        "queries": [],
    }

    # The 2 known festivals are skipped; the 2 missing ones become candidates.
    assert len(backend.candidates) == 2
    candidates = by_name(backend.candidates)
    assert set(candidates) == {"Festival des Rues de Namur", "Straßenfest Bergheim"}

    fdr = candidates["Festival des Rues de Namur"]
    assert fdr["state"] == "PENDING"
    assert fdr["website_url"] == f"{FDR}/"
    # Verified emails only: the invented one is dropped, the obfuscated one is kept.
    assert fdr["contacts"] == [
        {"name": "", "email": "programmation@festival-des-rues.be", "role": "Programming"}
    ]
    assert fdr["application_url"] == "https://forms.gle/fdr2027"
    assert fdr["application_type"] == "FORM"
    assert fdr["subtype"] == "STREET"
    assert fdr["start_date"] == "2027-06-11"
    assert fdr["estimated_start_date"] == "2027-06-11"
    assert [(hop["kind"], hop["url"]) for hop in fdr["found_via"]] == [
        ("artist_site", f"{ARTIST}/"),
        ("calendar", f"{ARTIST}/agenda/"),
        ("festival_site", f"{FDR}/"),
        ("contact", f"{FDR}/contact/"),
        ("application", f"{FDR}/appel-a-candidatures/"),
    ]
    assert {source["url"] for source in fdr["sources"]} == {
        f"{ARTIST}/agenda/",
        f"{FDR}/",
        f"{FDR}/contact/",
        f"{FDR}/appel-a-candidatures/",
    }

    sfb = candidates["Straßenfest Bergheim"]
    assert sfb["state"] == "PENDING"
    assert sfb["website_url"] == f"{SFB}/"  # found by search: the calendar only had Facebook
    assert sfb["contacts"] == [
        {
            "name": "Anna Schmidt",
            "email": "info@strassenfest-bergheim.de",
            "role": "Artistic director",
        }
    ]
    assert sfb["subtype"] == ""
    assert sfb["estimated_start_date"] == "2027-08-07"  # no estimate given: the start date
    assert [(hop["kind"], hop["url"]) for hop in sfb["found_via"]] == [
        ("artist_site", f"{ARTIST}/"),
        ("calendar", f"{ARTIST}/agenda/"),
        ("festival_site", f"{SFB}/"),
        ("contact", f"{SFB}/kontakt/"),
    ]
    assert 'Search: "Straßenfest Bergheim Bergheim 2026"' in sfb["found_via"][2]["snippet"]
    assert search.queries == ["Straßenfest Bergheim Bergheim 2026"]

    # The artist site is recorded as a source of leads.
    assert backend.sources == [
        {
            "url": f"{ARTIST}/",
            "kind": "ARTIST_SITE",
            "title": "Compagnie Les Jongleurs — Cirque de rue",
            "calendar_url": f"{ARTIST}/agenda/",
            "leads_found": 4,
        }
    ]
    # Keyword ranking found every link: the LLM never had to pick one.
    assert sorted(llm.purposes()) == sorted(
        ["classify", "extract_leads", "pick_website", "extract_org", "extract_org"]
    )
    counters = backend.updates[-1]["counters"]
    assert counters["leads"] == 4
    assert counters["leads_missing"] == 2
    assert counters["candidates"] == 2
    assert counters["llm_calls"] == 5
    assert counters["searches"] == 1
    assert counters["pages"] == 7
    assert "check_known" in backend.steps
    assert any("2 already in clapp" in message for message in backend.messages)


async def test_broken_site_gives_an_unresolved_candidate(graph_settings, web, web_backend):
    serve(web, web_backend, broken_festival_site=True)
    await run(graph_settings, f"{ARTIST}/")

    assert web_backend.statuses == ["RUNNING", "DONE"]
    candidates = by_name(web_backend.candidates)
    assert len(candidates) == 2
    fdr = candidates["Festival des Rues"]  # nothing extracted: the calendar's name is kept
    assert fdr["state"] == "UNRESOLVED"
    assert fdr["website_url"] == f"{FDR}/"  # the calendar's link, kept for the reviewer
    assert fdr["contacts"] == []
    assert fdr["relevance_reason"].startswith("Could not research: website unreachable")
    assert candidates["Straßenfest Bergheim"]["state"] == "PENDING"
    assert any("festival-des-rues.be" in error for error in web_backend.errors)


async def test_budget_reached_saves_what_was_found(graph_settings, fake_web, web_backend):
    await run(graph_settings, f"{ARTIST}/", max_pages=5)

    assert web_backend.statuses == ["RUNNING", "DONE"]
    final = web_backend.updates[-1]
    assert final["counters"]["pages"] <= 5
    assert "budget reached: pages" in final["progress"][0]["message"]
    # Whatever was researched before the budget ran out is saved.
    assert 1 <= len(web_backend.candidates) <= 2


async def test_llm_budget_reached_while_exploring(graph_settings, fake_web, web_backend):
    await run(graph_settings, f"{ARTIST}/", max_llm_calls=1)

    assert web_backend.statuses == ["RUNNING", "DONE"]
    assert web_backend.candidates == []
    assert "budget reached: llm_calls" in web_backend.updates[-1]["progress"][0]["message"]


async def test_cancel_stops_the_run(graph_settings, fake_web, web_backend):
    web_backend.cancel_after_updates = 6
    await run(graph_settings, f"{ARTIST}/")

    assert web_backend.statuses == ["RUNNING", "CANCELLED"]
    assert web_backend.candidates == []


async def test_plain_words_request_searches_and_researches(graph_settings, fake_web, web_backend):
    web_backend.known = []

    def responder(purpose, prompt):
        if purpose == "interpret":
            return {
                "goal": "Street theatre festivals in Belgium with open calls for 2027.",
                "org_types": ["FESTIVAL"],
                "countries": ["Belgium"],
                "queries": ["festival théâtre de rue Belgique 2027"],
            }
        if purpose == "classify":
            return {
                "kind": "ORG_SITE",
                "org_name": "Festival des Rues",
                "org_type": "FESTIVAL",
                "country": "Belgium",
                "town": "Namur",
            }
        return scenario(purpose, prompt)

    search = FakeSearch(
        {
            "Belgique": [
                SearchHit(url="https://www.facebook.com/events/1", title="Facebook event"),
                SearchHit(url=f"{FDR}/", title="Festival des Rues — Namur"),
            ]
        }
    )
    llm, _ = await run(
        graph_settings,
        "street theatre festivals in Belgium with open calls for 2027",
        responder=responder,
        search=search,
    )

    assert web_backend.statuses == ["RUNNING", "DONE"]
    assert web_backend.plan["countries"] == ["Belgium"]
    assert search.queries == ["festival théâtre de rue Belgique 2027"]
    [candidate] = web_backend.candidates
    assert candidate["name"] == "Festival des Rues de Namur"
    assert candidate["state"] == "PENDING"
    assert [hop["kind"] for hop in candidate["found_via"]] == [
        "festival_site",
        "contact",
        "application",
    ]
    assert candidate["found_via"][0]["snippet"] == 'Search: "festival théâtre de rue Belgique 2027"'
    assert llm.purposes().count("classify") == 1  # Facebook isn't visited
    assert web_backend.sources == []  # an organisation's own site isn't a lead source


async def test_batch_rejected_by_backend_is_saved_one_by_one(graph_settings, fake_web, web_backend):
    web_backend.reject_batches = True
    await run(graph_settings, f"{ARTIST}/")

    assert web_backend.statuses == ["RUNNING", "DONE"]
    assert len(web_backend.candidates) == 2
    assert web_backend.updates[-1]["counters"]["candidates"] == 2
