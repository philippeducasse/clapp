from typing import Any, Optional

from organisations.venues.models import Venue
from organisations.services import _build_enrich_prompt, _format_contacts_for_prompt


def generate_enrich_prompt(venue: Venue, search_results: Optional[str]) -> str:
    """Generate venue-specific enrichment prompt."""
    venue_types = Venue.VENUE_TYPE

    def nv(x: Any) -> str:
        return "" if x is None else str(x)

    venue_types_str = ", ".join([value for (value, _) in venue_types])

    contacts_display = _format_contacts_for_prompt(venue)

    current_record_fields = f"""country: {nv(venue.country)}
town: {nv(venue.town)}
website_url: {nv(venue.website_url)}
venue_type: {nv(venue.venue_type)}
description: {nv(venue.description)}
contacts: {contacts_display}
comments: {nv(venue.comments)}"""

    output_keys = """country, town, website_url, venue_type, description,
contacts, sources, updated_fields"""

    type_field_section = f"""
    RECOGNITION HINTS
    venue_type (choose one from: {venue_types_str})
    - Look for domain terms: theatre, opera house, concert hall, dance studio, music venue,
      circus tent, performance space, art gallery, outdoor stage, puppet theatre, circus space.
    - If type is not clear, use "UNKNOWN".
    """

    required_json_example = """{{
      "country": "Belgium",
      "town": "Brussels",
      "website_url": "https://example-venue.be",
      "venue_type": "CONCERT_HALL",
      "description": "A modern concert hall hosting international and local performances.",
      "contacts": [
        {{"email": "info@example-venue.be"}},
        {{"email": "programming@example-venue.be", "name": "Jane Smith", "role": "Programming Director"}},
      ],
      "comments": "this is a comment."
    }}"""

    return _build_enrich_prompt(
        venue,
        search_results,
        "venue",
        current_record_fields,
        output_keys,
        type_field_section,
        required_json_example,
    )
