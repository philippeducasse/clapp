"""Domain helpers shared by the tools."""

from functools import lru_cache
from urllib.parse import urlsplit

import tldextract

# Offline: use the public suffix list bundled with tldextract instead of downloading it.
# Private suffixes are on, so "foo.wixsite.com" and "bar.wixsite.com" are different sites.
_extract = tldextract.TLDExtract(
    suffix_list_urls=(), cache_dir=None, include_psl_private_domains=True
)


def domain_of(url: str) -> str:
    """Lowercase host without "www.", e.g. "https://www.x.org/a" -> "x.org".

    Same result as the backend's `normalize_domain` (subdomains are kept).
    """
    url = (url or "").strip().lower()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    try:
        host = urlsplit(url).hostname or ""
    except ValueError:
        return ""
    return host.removeprefix("www.")


@lru_cache(maxsize=4096)
def registrable_domain(url_or_host: str) -> str:
    """The domain a site registered, e.g. "https://en.festival.co.uk/x" -> "festival.co.uk".

    Falls back to the host for IPs and hosts without a known suffix.
    """
    host = domain_of(url_or_host)
    if not host:
        return ""
    parts = _extract(host)
    return parts.top_domain_under_public_suffix or host


def same_site(a: str, b: str) -> bool:
    """True when both URLs/hosts share a registrable domain."""
    ra, rb = registrable_domain(a), registrable_domain(b)
    return bool(ra) and ra == rb


def host_matches(host: str, domains: frozenset[str] | set[str]) -> bool:
    """True when `host` is one of `domains` or a subdomain of one."""
    host = host.lower().removeprefix("www.")
    while host:
        if host in domains:
            return True
        if "." not in host:
            return False
        host = host.split(".", 1)[1]
    return False
