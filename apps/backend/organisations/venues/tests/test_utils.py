import pytest
from organisations.venues.models import Venue
from organisations.venues.utils import generate_enrich_prompt


@pytest.mark.django_db
class TestGenerateEnrichPromptVenue:
    """Tests for venue-specific enrichment prompt generation."""

    def test_generates_valid_prompt(self):
        """Test that prompt is generated as a string."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(venue, None)

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_prompt_includes_current_values(self):
        """Test that prompt includes current venue values."""
        venue = Venue.objects.create(
            country="Belgium", town="Brussels", website_url="https://venue.be"
        )

        prompt = generate_enrich_prompt(venue, None)

        assert "Belgium" in prompt
        assert "Brussels" in prompt
        assert "https://venue.be" in prompt

    def test_prompt_includes_search_results(self):
        """Test that prompt includes search results when provided."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")
        search_results = "Found venue information online..."

        prompt = generate_enrich_prompt(venue, search_results)

        assert search_results in prompt

    def test_prompt_handles_none_search_results(self):
        """Test that prompt handles None search results gracefully."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(venue, None)

        assert "No search results provided" in prompt

    def test_prompt_includes_venue_type_section(self):
        """Test that prompt includes venue type recognition hints."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(venue, None)

        # Check for venue type hints
        assert "RECOGNITION HINTS" in prompt
        assert "venue_type" in prompt

    def test_prompt_with_venue_type_choices(self):
        """Test that prompt includes available venue type choices."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(venue, None)

        # Check for some common venue types in the prompt
        assert "CONCERT_HALL" in prompt or "concert" in prompt.lower()

    def test_prompt_with_contacts(self):
        """Test that prompt includes venue contacts."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")
        venue.contacts.create(email="info@venue.be", name="Info")

        prompt = generate_enrich_prompt(venue, None)

        assert "info@venue.be" in prompt
        assert "Info" in prompt

    def test_prompt_with_multiple_contacts(self):
        """Test that prompt formats multiple contacts correctly."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")
        venue.contacts.create(email="info@venue.be", name="Info")
        venue.contacts.create(
            email="programming@venue.be", name="Programming Director", role="Programming"
        )

        prompt = generate_enrich_prompt(venue, None)

        assert "info@venue.be" in prompt
        assert "programming@venue.be" in prompt
        assert "Programming Director" in prompt
        assert "Programming" in prompt

    def test_prompt_includes_json_example(self):
        """Test that prompt includes example JSON output."""
        venue = Venue.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(venue, None)

        # Check for JSON structure in example
        assert '"country"' in prompt
        assert '"contacts"' in prompt
        assert '"venue_type"' in prompt

    def test_prompt_with_all_fields_populated(self):
        """Test prompt with all fields filled in."""
        venue = Venue.objects.create(
            country="Belgium",
            town="Brussels",
            website_url="https://venue.be",
            venue_type="CONCERT_HALL",
            description="A modern concert hall hosting international and local performances.",
            comments="Excellent acoustics",
        )

        prompt = generate_enrich_prompt(venue, None)

        assert "Belgium" in prompt
        assert "Brussels" in prompt
        assert "https://venue.be" in prompt
        assert "modern concert hall" in prompt
