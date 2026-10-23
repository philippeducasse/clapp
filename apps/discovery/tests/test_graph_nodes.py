"""Graph nodes one at a time, with scripted LLM answers and saved HTML pages."""

from datetime import date

import pytest

from discovery.backend_client import CandidateContact, CandidateIn, Evidence, KnownEntry
from discovery.graph.deps import guarded
from discovery.graph.leads import (
    MAX_CONTACTS,
    best_contacts,
    country_ok,
    dedupe_candidates,
    merge_lead,
    same_org,
)
from discovery.graph.navigate import navigate
from discovery.graph.nodes.check_known import check_known, fan_out
from discovery.graph.nodes.explore import (
    add_org_lead,
    after_classify,
    after_visit,
    classify_page,
    extract_leads,
    interpret_start,
    search,
    split_starting_point,
    visit_page,
)
from discovery.graph.nodes.finish import dedupe_candidates as dedupe_node
from discovery.graph.research_org import build_candidate, resolve_website
from discovery.graph.state import Lead, PageTask, add_hop
from discovery.prompts.classify import PageClassification
from discovery.prompts.extract_org import ContactOut, OrgExtraction
from discovery.runner import RunCancelled
from discovery.tools.known import KnownIndex
from discovery.tools.search import SearchError, SearchHit
from tests.graph_fakes import FakeSearch, LLMLog, link_number, runtime

ARTIST = "https://lesjongleurs.fr"
FDR = "https://www.festival-des-rues.be"


def lead(name="Festival des Rues", **fields) -> Lead:
    return Lead(name=name, org_type=fields.pop("org_type", "FESTIVAL"), **fields)


# --- interpret_start ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "urls", "request_text"),
    [
        ("https://some-juggler.com", ["https://some-juggler.com"], ""),
        ("see www.juggler.be/dates.", ["https://www.juggler.be/dates"], ""),
        (
            "street theatre festivals in Belgium with open calls for 2027",
            [],
            "street theatre festivals in Belgium with open calls for 2027",
        ),
        (
            "check the tour dates on https://some-juggler.com and find festivals we don't have",
            ["https://some-juggler.com"],
            "check the tour dates on and find festivals we don't have",
        ),
        ("https://a.org https://b.org https://a.org", ["https://a.org", "https://b.org"], ""),
    ],
)
def test_split_starting_point(text, urls, request_text):
    assert split_starting_point(text) == (urls, request_text)


async def test_interpret_url_only_needs_no_llm(make_deps, web_backend):
    deps = await make_deps()
    result = await interpret_start({"starting_point": f"{ARTIST}/"}, runtime(deps))

    assert result["org_types"] == ["FESTIVAL"]
    assert result["queries"] == []
    assert [task.url for task in result["queue"]] == [f"{ARTIST}/"]
    assert result["queue"][0].found_via[0].kind == "start"
    assert web_backend.plan["urls"] == [f"{ARTIST}/"]


async def test_interpret_request_asks_the_llm(make_deps, web_backend):
    llm = LLMLog(
        lambda purpose, prompt: {
            "goal": "Belgian street festivals",
            "org_types": ["FESTIVAL", "VENUE"],
            "countries": ["Belgium", " "],
            "queries": [f"query {n}" for n in range(9)],
        }
    )
    deps = await make_deps(llm)
    result = await interpret_start(
        {"starting_point": "street theatre festivals in Belgium"}, runtime(deps)
    )

    assert llm.purposes() == ["interpret"]
    assert "Today is 2026-10-18" in llm.calls[0][1]
    assert result["goal"] == "Belgian street festivals"
    assert result["org_types"] == ["FESTIVAL", "VENUE"]
    assert result["countries"] == ["Belgium"]
    assert result["queries"] == [f"query {n}" for n in range(5)]  # at most 5
    assert result["queue"] == []
    assert web_backend.plan["queries"] == result["queries"]


async def test_interpret_both_uses_the_request_as_goal(make_deps):
    deps = await make_deps(
        lambda purpose, prompt: {"goal": "something else", "org_types": [], "queries": []}
    )
    text = f"check the tour dates on {ARTIST} and find festivals we don't have"
    result = await interpret_start({"starting_point": text}, runtime(deps))

    assert result["goal"] == "check the tour dates on and find festivals we don't have"
    assert result["org_types"] == ["FESTIVAL"]
    assert result["queries"] == []
    assert [task.url for task in result["queue"]] == [ARTIST]


async def test_interpret_falls_back_when_the_llm_fails(make_deps, web_backend):
    def broken(purpose, prompt):
        raise ValueError("model down")

    deps = await make_deps(broken)
    result = await interpret_start({"starting_point": "circus residencies in Spain"}, runtime(deps))

    assert result["goal"] == "circus residencies in Spain"
    assert result["queries"] == ["circus residencies in Spain"]
    assert result["org_types"] == ["FESTIVAL", "RESIDENCY", "VENUE"]
    assert any("Could not interpret" in error for error in web_backend.errors)


# --- search and visit_page ----------------------------------------------------------------


async def test_search_queues_results_but_not_social_networks(make_deps, web_backend):
    fake = FakeSearch(
        {
            "belgium": [
                SearchHit(url="https://www.facebook.com/x", title="FB"),
                SearchHit(url=f"{FDR}/", title="FdR"),
                SearchHit(url=f"{FDR}/#top", title="FdR again"),
            ]
        }
    )
    deps = await make_deps(search=fake)
    result = await search({"queries": ["festivals belgium"], "queue": []}, runtime(deps))

    [task] = result["queue"]
    assert task.url == f"{FDR}/"
    assert task.found_via == [
        Evidence(kind="search", url=f"{FDR}/", title="FdR", snippet='Search: "festivals belgium"')
    ]
    assert deps.ctx.counters["searches"] == 1


async def test_search_errors_and_budget_dont_stop_the_run(make_deps, web_backend):
    class Failing(FakeSearch):
        async def search(self, query, budget=None):
            budget.spend("searches")
            raise SearchError("API down")

    deps = await make_deps(search=Failing(), max_searches=1)
    result = await search({"queries": ["a", "b", "c"], "queue": []}, runtime(deps))

    assert result["queue"] == []
    assert any("API down" in error for error in web_backend.errors)
    assert deps.budget_reached == {"searches"}


async def test_visit_page_skips_failures_and_empty_pages(make_deps, web, web_backend):
    web.html(f"{ARTIST}/js", "<html><body><div id=root></div></body></html>")
    web.page(f"{ARTIST}/", "artist_home.html")
    web.finish()
    deps = await make_deps()
    queue = [
        PageTask(url="https://nowhere.example.org/"),  # 404
        PageTask(url=f"{ARTIST}/js"),  # empty content
        PageTask(url=f"{ARTIST}/"),
        PageTask(url=f"{ARTIST}/agenda/"),
    ]
    result = await visit_page({"queue": queue}, runtime(deps))

    assert result["page"].final_url == f"{ARTIST}/"
    assert [task.url for task in result["queue"]] == [f"{ARTIST}/agenda/"]
    assert after_visit(result) == "classify_page"
    assert any("nowhere.example.org" in error for error in web_backend.errors)

    # The same page isn't explored twice.
    again = await visit_page({"queue": [PageTask(url=f"{ARTIST}/")]}, runtime(deps))
    assert again["page"] is None
    assert after_visit(again) == "check_known"


async def test_visit_page_stops_at_the_exploring_share_of_the_budget(make_deps, web):
    web.page(f"{ARTIST}/", "artist_home.html")
    web.page(f"{ARTIST}/agenda/", "artist_agenda.html")
    web.finish()
    deps = await make_deps(max_pages=2)  # exploring may use 1
    first = await visit_page(
        {"queue": [PageTask(url=f"{ARTIST}/"), PageTask(url=f"{ARTIST}/agenda/")]}, runtime(deps)
    )
    assert first["page"] is not None
    second = await visit_page({"queue": first["queue"]}, runtime(deps))
    assert second["page"] is None
    assert deps.ctx.counters["pages"] == 1


# --- classify_page --------------------------------------------------------------------------


async def page_state(deps, web, url, fixture):
    web.page(url, fixture)
    web.finish()
    page = await deps.fetch(url)
    return {
        "goal": "festivals",
        "org_types": ["FESTIVAL"],
        "page": page,
        "current": PageTask(url=url, found_via=[Evidence(kind="start", url=url)]),
    }


@pytest.mark.parametrize(
    ("answer", "route", "listings"),
    [
        ({"kind": "ARTIST_SITE"}, "find_calendar", 0),
        ({"kind": "AGGREGATOR"}, "extract_leads", 1),
        ({"kind": "ORG_SITE", "org_name": "Fest", "org_type": "FESTIVAL"}, "add_org_lead", 0),
        ({"kind": "ORG_SITE", "org_name": "Hall", "org_type": "VENUE"}, "visit_page", 0),
        ({"kind": "ORG_SITE", "org_name": " "}, "visit_page", 0),
        ({"kind": "IRRELEVANT"}, "visit_page", 0),
    ],
)
async def test_classify_routes(make_deps, web, answer, route, listings):
    deps = await make_deps(lambda purpose, prompt: answer)
    state = await page_state(deps, web, f"{ARTIST}/", "artist_home.html")
    result = await classify_page(state, runtime(deps))
    assert after_classify(result) == route
    assert len(result["listings"]) == listings


async def test_classify_error_skips_the_page(make_deps, web, web_backend):
    deps = await make_deps(lambda purpose, prompt: "not json")
    state = await page_state(deps, web, f"{ARTIST}/", "artist_home.html")
    result = await classify_page(state, runtime(deps))
    assert result == {"classification": None}
    assert after_classify(result) == "visit_page"
    assert web_backend.errors


# --- navigate -------------------------------------------------------------------------------


async def test_navigate_follows_a_clear_keyword_match_without_the_llm(make_deps, web):
    web.page(f"{ARTIST}/agenda/", "artist_agenda.html")
    deps = await make_deps()  # any LLM call fails the test
    state = await page_state(deps, web, f"{ARTIST}/", "artist_home.html")
    reached = await navigate(deps, state["page"], ["calendar"], 1)
    assert [(goal, page.final_url) for goal, page in reached] == [("calendar", f"{ARTIST}/agenda/")]


NO_KEYWORDS = """<html><head><title>Les Jongleurs</title></head><body>
<a href="/a/">Les spectacles</a> <a href="/b/">Où nous voir</a> <a href="/c/">Photos</a>
<p>Compagnie de jonglage de rue, en tournée partout en Europe depuis 2009 avec trois spectacles.</p>
</body></html>"""


async def test_navigate_asks_the_llm_for_numbers_when_nothing_matches(make_deps, web):
    web.html(f"{ARTIST}/", NO_KEYWORDS)
    web.page(f"{ARTIST}/b/", "artist_agenda.html")
    web.finish()
    llm = LLMLog(lambda purpose, prompt: {"numbers": [99, link_number(prompt, f"{ARTIST}/b/"), 1]})
    deps = await make_deps(llm)
    page = await deps.fetch(f"{ARTIST}/")
    reached = await navigate(deps, page, ["calendar"], 1)

    assert llm.purposes() == ["pick_link"]
    assert "Où nous voir" in llm.calls[0][1]
    # 99 isn't in the list and is ignored; only one page is allowed.
    assert [page.final_url for _, page in reached] == [f"{ARTIST}/b/"]


async def test_navigate_stops_when_the_llm_says_stop(make_deps, web):
    web.html(f"{ARTIST}/", NO_KEYWORDS)
    web.finish()
    deps = await make_deps(lambda purpose, prompt: {"numbers": []})
    page = await deps.fetch(f"{ARTIST}/")
    assert await navigate(deps, page, ["calendar"], 1) == []


async def test_navigate_respects_hops_per_site(make_deps, web):
    web.page(f"{FDR}/contact/", "fdr_contact.html")
    web.page(f"{FDR}/appel-a-candidatures/", "fdr_appel.html")
    deps = await make_deps(max_hops_per_site=1)
    state = await page_state(deps, web, f"{FDR}/", "fdr_home.html")
    reached = await navigate(deps, state["page"], ["contact", "application"], 2)
    assert [goal for goal, _ in reached] == ["contact"]
    assert await navigate(deps, state["page"], ["application"], 2) == []


# --- extract_leads and add_org_lead ---------------------------------------------------------


async def test_extract_leads_maps_link_numbers_and_filters(make_deps, web, web_backend):
    def answer(purpose, prompt):
        return {
            "leads": [
                {
                    "name": "Festival des Rues  2026",
                    "org_type": "FESTIVAL",
                    "country": "Belgium",
                    "link_number": link_number(prompt, f"{FDR}/"),
                },
                {  # same festival again: merged
                    "name": "Festival des Rues 2026",
                    "org_type": "FESTIVAL",
                    "town": "Namur",
                    "country": "Belgium",
                },
                {
                    "name": "Straßenfest Bergheim",
                    "org_type": "FESTIVAL",
                    "country": "Germany",
                    "link_number": link_number(prompt, "https://www.facebook.com/strassenfest"),
                },
                {"name": "Chalon", "org_type": "FESTIVAL", "country": "France", "link_number": 999},
                {"name": "Some theatre", "org_type": "VENUE", "country": "Belgium"},
                {"name": "Own link", "org_type": "FESTIVAL", "link_number": 1},
            ]
        }

    deps = await make_deps(answer)
    state = await page_state(deps, web, f"{ARTIST}/agenda/", "artist_agenda.html")
    state |= {
        "countries": ["Belgium", "Germany", "France"],
        "classification": PageClassification(kind="ARTIST_SITE"),
        "listings": [("calendar", state["page"])],
        "leads": [],
        "sources": [],
    }
    result = await extract_leads(state, runtime(deps))

    leads = {lead.name: lead for lead in result["leads"]}
    assert set(leads) == {"Festival des Rues 2026", "Straßenfest Bergheim", "Chalon", "Own link"}
    assert leads["Festival des Rues 2026"].website_url == f"{FDR}/"
    assert leads["Festival des Rues 2026"].town == "Namur"  # filled in from the duplicate
    assert leads["Straßenfest Bergheim"].website_url == ""  # Facebook isn't a website
    assert leads["Chalon"].website_url == ""  # number not in the list
    assert leads["Own link"].website_url == ""  # a link to the artist's own site
    assert [hop.kind for hop in leads["Chalon"].found_via] == ["calendar"]
    assert result["listings"] == []
    [source] = result["sources"]
    assert source.kind == "ARTIST_SITE"
    assert source.calendar_url == f"{ARTIST}/agenda/"
    assert source.leads_found == 5  # found on the page, before merging
    assert deps.ctx.counters["leads"] == 4


async def test_extract_leads_country_filter(make_deps, web):
    deps = await make_deps(
        lambda purpose, prompt: {
            "leads": [
                {"name": "A", "org_type": "FESTIVAL", "country": "France"},
                {"name": "B", "org_type": "FESTIVAL", "country": "belgium"},
                {"name": "C", "org_type": "FESTIVAL"},
            ]
        }
    )
    state = await page_state(deps, web, f"{ARTIST}/agenda/", "artist_agenda.html")
    state |= {
        "countries": ["Belgium"],
        "classification": PageClassification(kind="AGGREGATOR"),
        "listings": [("listing", state["page"])],
    }
    result = await extract_leads(state, runtime(deps))
    assert [lead.name for lead in result["leads"]] == ["B", "C"]
    assert result["sources"][0].kind == "AGGREGATOR"
    assert result["sources"][0].calendar_url == ""


async def test_add_org_lead_uses_the_site_root(make_deps, web):
    deps = await make_deps()
    state = await page_state(deps, web, f"{FDR}/", "fdr_home.html")
    state["page"] = state["page"].model_copy(update={"final_url": f"{FDR}/fr/2026/"})
    state["classification"] = PageClassification(
        kind="ORG_SITE", org_name="Festival des Rues", org_type="FESTIVAL", country="Belgium"
    )
    result = await add_org_lead(state, runtime(deps))
    [new] = result["leads"]
    assert new.website_url == f"{FDR}/"
    assert [hop.kind for hop in new.found_via] == ["start", "org_site"]


# --- check_known ----------------------------------------------------------------------------


async def test_check_known_skips_known_leads_and_caps_the_rest(make_deps, web_backend):
    deps = await make_deps(max_leads=2)
    deps.known = KnownIndex(
        [
            KnownEntry(name="Chalon dans la rue", country="France", org_type="FESTIVAL",
                       source="SEED", domain="chalondanslarue.com"),
        ]
    )  # fmt: skip
    leads = [
        lead("Chalon", website_url="https://www.chalondanslarue.com/2026"),
        lead("Chalon dans la Rue", country="France"),
        lead("A"),
        lead("B"),
        lead("C"),
    ]
    result = await check_known({"leads": leads, "goal": "g"}, runtime(deps))

    assert [lead.name for lead in result["missing"]] == ["A", "B"]
    assert deps.ctx.counters["leads_missing"] == 3
    assert deps.ctx.notes == ["1 lead(s) not researched (limit 2)"]
    sends = fan_out({"missing": result["missing"], "goal": "g"})
    assert [send.node for send in sends] == ["research_org", "research_org"]
    assert sends[0].arg == {"lead": result["missing"][0], "goal": "g"}
    assert fan_out({"missing": []}) == "dedupe_candidates"


# --- research_org ---------------------------------------------------------------------------


async def test_resolve_website_picks_a_search_result_by_number(make_deps):
    hits = [
        SearchHit(url="https://www.facebook.com/fest", title="FB"),
        SearchHit(url="https://news.example.org/fest", title="News"),
        SearchHit(url="https://fest.example.org/#home", title="Fest"),
    ]
    llm = LLMLog(lambda purpose, prompt: {"number": link_number(prompt, hits[2].url)})
    deps = await make_deps(llm, search=FakeSearch({"Fest": hits}))
    result = await resolve_website({"lead": lead("Fest", town="Namur")}, runtime(deps))
    assert deps.search.queries == ["Fest Namur 2026"]
    assert "facebook" not in llm.calls[0][1]
    assert result["website_url"] == "https://fest.example.org/"
    assert result["resolve_hop"].kind == "search"


async def test_resolve_website_stops_when_the_site_is_already_known(make_deps):
    hits = [SearchHit(url="https://www.chalondanslarue.com/", title="Chalon")]
    deps = await make_deps(lambda p, m: {"number": 1}, search=FakeSearch({"": hits}))
    deps.known = KnownIndex(
        [KnownEntry(name="Chalon dans la rue", org_type="FESTIVAL", source="SEED",
                    domain="chalondanslarue.com")]
    )  # fmt: skip
    result = await resolve_website({"lead": lead("Chalon Rue Festival")}, runtime(deps))
    assert result == {"already_known": True}


@pytest.mark.parametrize("number", [None, 7])
async def test_resolve_website_no_pick_means_unresolved(make_deps, number):
    hits = [SearchHit(url="https://news.example.org/fest", title="News")]
    deps = await make_deps(lambda p, m: {"number": number}, search=FakeSearch({"": hits}))
    result = await resolve_website({"lead": lead("Fest")}, runtime(deps))
    assert "website_url" not in result
    assert result["site_problem"] == "no official website in the search results"


async def fdr_pages(deps, web):
    web.page(f"{FDR}/", "fdr_home.html")
    web.page(f"{FDR}/contact/", "fdr_contact.html")
    web.page(f"{ARTIST}/agenda/", "artist_agenda.html")
    web.finish()
    await deps.fetch(f"{ARTIST}/agenda/")
    return [
        ("festival_site", await deps.fetch(f"{FDR}/")),
        ("contact", await deps.fetch(f"{FDR}/contact/")),
    ]


async def test_build_candidate_keeps_only_verified_facts(make_deps, web):
    deps = await make_deps()
    pages = await fdr_pages(deps, web)
    extraction = OrgExtraction(
        name="Festival des Rues de Namur",
        org_type="FESTIVAL",
        subtype="street festival",
        application_type="form",
        application_url="https://invented.example.org/apply",
        start_date="11/06/2027",
        estimated_start_date="2027-06-15",
        contacts=[
            ContactOut(email="Programmation@Festival-des-Rues.be", role="Programming"),
            ContactOut(email="boss@festival-des-rues.be"),
        ],
    )
    the_lead = lead(
        "Festival des Rues",
        website_url=f"{FDR}/",
        listing_url=f"{ARTIST}/agenda/",
        found_via=[Evidence(kind="calendar", url=f"{ARTIST}/agenda/", title="Agenda")],
        dates="12-14 juin 2026",
    )
    candidate = build_candidate(
        {"lead": the_lead, "website_url": f"{FDR}/", "pages": pages, "extraction": extraction},
        deps.pages,
    )
    assert candidate.state == "PENDING"
    assert candidate.name == "Festival des Rues de Namur"
    assert [c.email for c in candidate.contacts] == ["programmation@festival-des-rues.be"]
    assert candidate.application_url == ""  # not on the pages
    assert candidate.subtype == ""  # not a valid festival_type
    assert candidate.application_type == "FORM"
    assert candidate.start_date is None  # not ISO
    assert candidate.estimated_start_date == date(2027, 6, 15)
    assert [hop.kind for hop in candidate.found_via] == ["calendar", "festival_site", "contact"]
    assert [source.kind for source in candidate.sources] == ["listing", "festival_site", "contact"]


async def test_build_candidate_falls_back_to_emails_of_the_sites_domain(make_deps, web):
    deps = await make_deps()
    pages = await fdr_pages(deps, web)
    candidate = build_candidate(
        {"lead": lead(listing_url=f"{ARTIST}/agenda/"), "website_url": f"{FDR}/", "pages": pages},
        deps.pages,
    )
    # No extraction (e.g. LLM budget reached): emails on the site's own domain are used,
    # programming before press.
    assert [c.email for c in candidate.contacts] == [
        "programmation@festival-des-rues.be",
        "presse@festival-des-rues.be",
    ]
    assert candidate.state == "PENDING"
    assert candidate.relevance_reason == ""


async def test_build_candidate_unresolved_without_a_readable_site(make_deps):
    deps = await make_deps()
    candidate = build_candidate(
        {
            "lead": lead(
                "Fête de la Jongle",
                dates="20 juillet",
                found_via=[Evidence(kind="calendar", url=f"{ARTIST}/agenda/", title="Agenda")],
            ),
            "site_problem": "no website found by web search",
        },
        deps.pages,
    )
    assert candidate.state == "UNRESOLVED"
    assert candidate.website_url == ""
    assert candidate.relevance_reason == (
        "Could not research: no website found by web search. On the calendar Agenda (20 juillet)."
    )


async def test_build_candidate_never_uses_an_unseen_website(make_deps):
    deps = await make_deps()
    candidate = build_candidate(
        {"lead": lead(), "website_url": "https://invented.example.org/"}, deps.pages
    )
    assert candidate.website_url == ""
    assert candidate.state == "UNRESOLVED"


# --- dedupe ---------------------------------------------------------------------------------


def candidate(name, state="PENDING", **fields) -> CandidateIn:
    return CandidateIn(org_type="FESTIVAL", name=name, state=state, **fields)


def test_dedupe_keeps_the_best_and_merges_sources_and_contacts():
    a = candidate(
        "Festival des Rues",
        state="UNRESOLVED",
        country="Belgium",
        sources=[Evidence(url="https://a.org/1")],
        contacts=[CandidateContact(email="a@fdr.be")],
    )
    b = candidate(
        "Festival des rues!",
        country="Belgium",
        website_url=f"{FDR}/",
        sources=[Evidence(url="https://a.org/1"), Evidence(url="https://a.org/2")],
    )
    c = candidate("Other", website_url="https://other.org/")
    d = candidate("Other festival", website_url="https://www.other.org/x")

    [first, second] = dedupe_candidates([a, b, c, d])
    assert first.name == "Festival des rues!" and first.state == "PENDING"
    assert [s.url for s in first.sources] == ["https://a.org/1", "https://a.org/2"]
    assert [c.email for c in first.contacts] == ["a@fdr.be"]
    assert second.name == "Other"


def test_dedupe_keeps_at_most_three_contacts_across_duplicates():
    def with_contacts(*emails):
        return candidate(
            "Fest",
            website_url="https://fest.be/",
            contacts=[CandidateContact(email=e) for e in emails],
        )

    [merged] = dedupe_candidates(
        [
            with_contacts("presse@fest.be", "info@fest.be", "anna@fest.be"),
            with_contacts("info@fest.be", "programmation@fest.be", "tickets@fest.be"),
        ]
    )
    assert [c.email for c in merged.contacts] == [
        "programmation@fest.be",
        "info@fest.be",
        "anna@fest.be",
    ]


def test_best_contacts_ranks_dedupes_and_caps():
    contacts = [
        CandidateContact(email="press@f.be", role="Press officer"),
        CandidateContact(email="jan@f.be", role="Comptabilité"),
        CandidateContact(email="info@f.be"),
        CandidateContact(email="info@f.be"),
        CandidateContact(email="marie@f.be", role="Programmatrice"),
        CandidateContact(email="booking@f.be"),
        CandidateContact(email="tom@f.be", role="Artistic director"),
    ]
    assert [c.email for c in best_contacts(contacts)] == [
        "marie@f.be",
        "booking@f.be",
        "tom@f.be",
    ]
    assert [c.email for c in best_contacts(contacts[:4])] == [
        "info@f.be",
        "press@f.be",
        "jan@f.be",
    ]
    assert len(best_contacts(contacts)) == MAX_CONTACTS


def test_same_org_rules():
    assert same_org("Fest", "", "https://www.fest.be/a", "Other", "", "https://fest.be/")
    assert not same_org("Fest", "", "https://facebook.com/a", "Other", "", "https://facebook.com/b")
    assert same_org("Chalon dans la Rue 2026", "France", "", "chalon dans la rue", "", "")
    assert not same_org("Chalon dans la Rue", "France", "", "Chalon dans la Rue", "Belgium", "")
    assert same_org(
        "Festival des Rues Namur", "Belgium", "", "Festival des Rue Namur", "belgium", ""
    )
    assert country_ok("", ["Belgium"]) and not country_ok("France", ["Belgium"])


def test_merge_lead_fills_blanks():
    leads = [lead("Fest", country="Belgium")]
    assert not merge_lead(leads, lead("Fest", country="Belgium", website_url="https://f.be/"))
    assert leads[0].website_url == "https://f.be/"
    assert merge_lead(leads, lead("Other"))


def test_add_hop_merges_the_same_page():
    path = [Evidence(kind="search", url="https://f.be/", title="", snippet='Search: "x"')]
    path = add_hop(path, "org_site", "https://f.be", "Fest")
    assert path == [
        Evidence(kind="org_site", url="https://f.be/", title="Fest", snippet='Search: "x"')
    ]
    assert len(add_hop(path, "contact", "https://f.be/contact", "Contact")) == 2


async def test_dedupe_node_drops_candidates_clapp_already_has(make_deps):
    deps = await make_deps()
    deps.known = KnownIndex(
        [KnownEntry(name="Fest de Namur", country="Belgium", org_type="FESTIVAL", source="SEED")]
    )
    result = await dedupe_node(
        {"candidates": [candidate("Fest de Namur", country="Belgium"), candidate("New")]},
        runtime(deps),
    )
    assert [c.name for c in result["final_candidates"]] == ["New"]


# --- guarded --------------------------------------------------------------------------------


async def test_guarded_reports_errors_and_lets_cancel_through(make_deps, web_backend):
    deps = await make_deps()

    @guarded("boom", fallback={"x": 1})
    async def broken(state, runtime):
        raise KeyError("missing")

    assert await broken({}, runtime(deps)) == {"x": 1}
    assert web_backend.errors == ["boom: KeyError: 'missing'"]

    @guarded("cancelled")
    async def cancelled(state, runtime):
        raise RunCancelled()

    with pytest.raises(RunCancelled):
        await cancelled({}, runtime(deps))
