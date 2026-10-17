from discovery.tools.links import Link, extract_links, rank_links
from tests.conftest import fixture_text

HOME = "https://www.lesjongleurs.fr/"


def urls(links: list[Link]) -> list[str]:
    return [link.url for link in links]


def test_extract_links_keeps_same_site_pages_only():
    links = extract_links(fixture_text("artist_home.html"), HOME)

    assert urls(links) == [
        "https://www.lesjongleurs.fr/spectacles/",
        "https://www.lesjongleurs.fr/agenda/",
        "https://www.lesjongleurs.fr/la-compagnie/",
        "https://www.lesjongleurs.fr/contact/",
        "https://en.lesjongleurs.fr/tour-dates/",  # subdomain of the same site
    ]


def test_extract_links_merges_duplicates_and_keeps_the_longest_text():
    links = {link.url: link.text for link in extract_links(fixture_text("artist_home.html"), HOME)}
    # "/agenda/" appears as "Agenda" and as an image link with alt="Voir les dates".
    assert links["https://www.lesjongleurs.fr/agenda/"] == "Voir les dates"


def test_extract_links_can_return_external_links():
    links = extract_links(
        fixture_text("calendar.html"), "https://lesjongleurs.fr/agenda/", same_site_only=False
    )
    assert "https://www.festival-des-rues.be/" in urls(links)
    assert "https://chalondanslarue.com/" in urls(links)
    by_url = {link.url: link.text for link in links}
    assert by_url["https://chalondanslarue.com/"] == "Chalon dans la Rue"


def test_extract_links_resolves_base_href_and_handles_bad_html():
    html = '<html><head><base href="https://site.org/fr/"></head><body><a href="agenda">Agenda</a></body></html>'
    assert urls(extract_links(html, "https://site.org/")) == ["https://site.org/fr/agenda"]
    assert extract_links("", "https://site.org/") == []
    assert extract_links("   ", "https://site.org/") == []


def test_extract_links_uses_title_or_aria_label_when_there_is_no_text():
    html = '<a href="/contact" aria-label="Nous contacter"></a><a href="/x" title="Tournée"></a>'
    links = extract_links(html, "https://site.org/")
    assert [(link.url, link.text) for link in links] == [
        ("https://site.org/contact", "Nous contacter"),
        ("https://site.org/x", "Tournée"),
    ]


def test_rank_links_for_the_calendar():
    links = extract_links(fixture_text("artist_home.html"), HOME)
    ranked = rank_links(links, ["calendar"])

    assert ranked[0].url in {
        "https://www.lesjongleurs.fr/agenda/",
        "https://en.lesjongleurs.fr/tour-dates/",
    }
    assert {ranked[0].url, ranked[1].url} == {
        "https://www.lesjongleurs.fr/agenda/",
        "https://en.lesjongleurs.fr/tour-dates/",
    }
    assert ranked[-1].score == 0


def test_rank_links_for_contact_and_application():
    links = [
        Link(url="https://fest.be/programme/", text="Programme"),
        Link(url="https://fest.be/infos-pratiques/", text="Infos pratiques"),
        Link(url="https://fest.be/contact/", text="Contact"),
        Link(url="https://fest.be/pros/appel-a-candidatures/", text="Appel à candidatures 2027"),
    ]
    ranked = rank_links(links, ["contact", "application"])
    assert urls(ranked[:2]) == [
        "https://fest.be/pros/appel-a-candidatures/",
        "https://fest.be/contact/",
    ]
    assert ranked[2].score == 0 and ranked[3].score == 0


def test_rank_links_in_several_languages():
    cases = [
        (Link(url="https://a.de/x", text="Tourtermine"), "calendar"),
        (Link(url="https://a.de/termine", text="Live"), "calendar"),
        (Link(url="https://a.nl/x", text="Speellijst"), "calendar"),
        (Link(url="https://a.fr/x", text="Calendrier de tournée"), "calendar"),
        (Link(url="https://a.es/x", text="Fechas"), "calendar"),
        (Link(url="https://a.de/bewerbung", text="Mitmachen"), "application"),
        (Link(url="https://a.org/x", text="Open call 2027"), "application"),
        (Link(url="https://a.de/impressum", text="Impressum"), "contact"),
    ]
    for link, goal in cases:
        assert rank_links([link], [goal])[0].score > 0, (link, goal)


def test_rank_links_matches_whole_words_only():
    links = [
        Link(url="https://a.de/datenschutz", text="Datenschutz"),
        Link(url="https://a.fr/update", text="Mise à jour"),
        Link(url="https://a.fr/tourisme", text="Tourisme"),
    ]
    assert all(link.score == 0 for link in rank_links(links, ["calendar"]))


def test_rank_links_prefers_shallow_pages_and_anchor_text():
    links = [
        Link(url="https://a.fr/agenda/2019/show-x/", text="Show X"),
        Link(url="https://a.fr/agenda/", text="Agenda"),
    ]
    assert rank_links(links, ["calendar"])[0].url == "https://a.fr/agenda/"


def test_rank_links_with_extra_keywords():
    links = [Link(url="https://a.fr/x", text="Les rendez-vous")]
    assert rank_links(links, ["calendar"])[0].score == 0
    assert rank_links(links, ["calendar"], extra_keywords=["Rendez-vous"])[0].score > 0
