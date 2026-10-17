import pytest

from discovery.backend_client import BackendClient, KnownEntry
from discovery.tools.domains import domain_of, host_matches, registrable_domain, same_site
from discovery.tools.known import KnownIndex, normalize_name


def entry(name, country="", domain="", town="", org_type="FESTIVAL", source="SEED") -> KnownEntry:
    return KnownEntry(
        name=name, country=country, town=town, domain=domain, org_type=org_type, source=source
    )


@pytest.fixture
def index() -> KnownIndex:
    return KnownIndex(
        [
            entry("Chalon dans la Rue", "France", "chalondanslarue.com"),
            entry("Festival des Rues", "Belgium", "festival-des-rues.be"),
            entry("Straßenfest Bergheim", "Germany", "facebook.com"),  # site is a Facebook page
            entry("Mimos", "", ""),
            entry("La Strada", "Austria", "lastrada.at", source="CANDIDATE"),
        ]
    )


# --- domains -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.Fest.org/a?b=1", "fest.org"),
        ("fest.org", "fest.org"),
        ("http://en.fest.org", "en.fest.org"),
        ("", ""),
        ("https://[bad", ""),
    ],
)
def test_domain_of(url, expected):
    assert domain_of(url) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://en.festival.co.uk/x", "festival.co.uk"),
        ("https://www.fest.org", "fest.org"),
        ("https://foo.wixsite.com/fest", "foo.wixsite.com"),  # private suffix: its own site
        ("http://127.0.0.1:8000/", "127.0.0.1"),
        ("localhost", "localhost"),
    ],
)
def test_registrable_domain(url, expected):
    assert registrable_domain(url) == expected


def test_same_site_and_host_matches():
    assert same_site("https://en.fest.org/a", "https://www.fest.org/")
    assert not same_site("https://foo.wixsite.com/", "https://bar.wixsite.com/")
    assert host_matches("m.facebook.com", {"facebook.com"})
    assert not host_matches("notfacebook.com", {"facebook.com"})


# --- known index ---------------------------------------------------------------------------


def test_normalize_name():
    assert normalize_name("Chalon dans la Rue 2026 !") == "chalon dans la rue"
    assert normalize_name("Straßenfest  Bergheim") == "strassenfest bergheim"
    assert normalize_name("Fête de l'Été") == "fete de l ete"
    assert normalize_name("Københavns Gadeteater_Festival") == "københavns gadeteater festival"


def test_match_by_domain(index):
    match = index.match("Something else", "", "https://www.chalondanslarue.com/programme")
    assert match is not None
    assert match.reason == "domain"
    assert match.entry.name == "Chalon dans la Rue"


def test_match_by_registrable_domain(index):
    match = index.match("", "", "https://en.festival-des-rues.be/")
    assert match is not None and match.reason == "registrable_domain"


def test_match_by_fuzzy_name_in_the_same_country(index):
    match = index.match("Chalon dans la rue", "france", "https://new-site.fr/")
    assert match is not None and match.reason == "name"

    close = index.match("Festival des Rue", "Belgium")
    assert close is not None and close.entry.name == "Festival des Rues"
    assert close.score >= 90

    assert index.match("Festival des Rues", "France") is None  # other country
    assert index.match("Festival des Arts de la Rue", "Belgium") is None  # different name


def test_name_without_country_needs_an_exact_match(index):
    assert index.match("Chalon dans la Rue 2026", "") is not None
    assert index.match("Chalon dans la Ru", "") is None
    assert index.match("MIMOS", "France") is not None  # entry has no country


def test_blocklisted_domains_are_never_matched(index):
    assert index.match("Other fest", "Germany", "https://www.facebook.com/otherfest") is None
    assert index.match("Straßenfest Bergheim", "Germany", "https://www.facebook.com/x") is not None


def test_add_entries_found_during_the_run(index):
    assert not index.is_known("Fête de la Jongle", "Belgium")
    index.add(entry("Fête de la Jongle", "Belgium", source="CANDIDATE"))
    assert index.is_known("Fete de la jongle", "belgium")
    assert len(index) == 6


def test_empty_lead_matches_nothing(index):
    assert index.match("", "", "") is None


async def test_load_from_the_backend(settings, backend):
    client = BackendClient(settings)
    index = await KnownIndex.load(client)
    await client.aclose()
    assert len(index) == 0
