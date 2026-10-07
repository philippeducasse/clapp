from typing import Dict, Any
from organisations.models import Organisation
import json
import re
from urllib.parse import urlparse


def extract_fields_from_llm(llm_response: str) -> Dict[str, Any]:
    """Extract fields from LLM JSON response."""
    json_str: str = re.sub(r"```json\s*|\s*```", "", llm_response).strip()
    try:
        response_data = json.loads(json_str)
        return response_data if isinstance(response_data, dict) else {}
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the JSON response: {e}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def clean_organisation_data(organisation: Organisation) -> None:
    """Clean and normalize organisation data."""

    def clean_nan(value: str) -> str:
        return "" if str(value).strip().lower() == "nan" else str(value).strip()

    if organisation.name:
        organisation.name = organisation.name.title()

    if organisation.town:
        organisation.town = clean_nan(organisation.town.title())

    if organisation.country:
        organisation.country = clean_nan(organisation.country.title())

    if organisation.comments:
        organisation.comments = clean_nan(organisation.comments.strip().lower())

    if organisation.website_url:
        url: str = organisation.website_url.strip()
        if not url.startswith("http"):
            url = "https://" + url
        organisation.website_url = url.lower()

    if organisation.description:
        desc: str = organisation.description.strip()
        if not desc.endswith("."):
            desc += "."
        organisation.description = desc


def normalize_domain(url: str) -> str:
    """Return the lowercase host of a URL without "www.", e.g. "https://www.x.org/a" -> "x.org"."""
    url = (url or "").strip().lower()
    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    host = urlparse(url).hostname or ""
    return host.removeprefix("www.")
