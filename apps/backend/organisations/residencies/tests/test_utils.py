import pytest
from organisations.residencies.models import Residency
from organisations.residencies.utils import generate_enrich_prompt


@pytest.mark.django_db
class TestGenerateEnrichPromptResidency:
    """Tests for residency-specific enrichment prompt generation."""

    def test_generates_valid_prompt(self):
        """Test that prompt is generated as a string."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(residency, None)

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_prompt_includes_current_values(self):
        """Test that prompt includes current organisation values."""
        residency = Residency.objects.create(
            country="Belgium", town="Brussels", website_url="https://residency.be"
        )

        prompt = generate_enrich_prompt(residency, None)

        assert "Belgium" in prompt
        assert "Brussels" in prompt
        assert "https://residency.be" in prompt

    def test_prompt_includes_search_results(self):
        """Test that prompt includes search results when provided."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")
        search_results = "Found residency on website..."

        prompt = generate_enrich_prompt(residency, search_results)

        assert search_results in prompt

    def test_prompt_handles_none_search_results(self):
        """Test that prompt handles None search results gracefully."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(residency, None)

        # Should not raise error and should contain default text
        assert "No search results provided" in prompt

    def test_prompt_includes_date_rules(self):
        """Test that prompt includes date rules for residencies."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(residency, None)

        # Check for date-related content
        assert "DATE RULES" in prompt
        assert "YYYY-MM-DD" in prompt

    def test_prompt_includes_application_type_section(self):
        """Test that prompt includes application type recognition hints."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(residency, None)

        # Check for application type hints
        assert "application_type" in prompt
        assert "FORM" in prompt
        assert "EMAIL" in prompt

    def test_prompt_with_contacts(self):
        """Test that prompt includes organisation contacts."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")
        residency.contacts.create(email="info@residency.be", name="Info")

        prompt = generate_enrich_prompt(residency, None)

        assert "info@residency.be" in prompt
        assert "Info" in prompt

    def test_prompt_with_multiple_contacts(self):
        """Test that prompt formats multiple contacts correctly."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")
        residency.contacts.create(email="info@residency.be", name="Info")
        residency.contacts.create(
            email="coord@residency.be", name="Coordinator", role="Programming"
        )

        prompt = generate_enrich_prompt(residency, None)

        assert "info@residency.be" in prompt
        assert "coord@residency.be" in prompt
        assert "Coordinator" in prompt
        assert "Programming" in prompt

    def test_prompt_includes_json_example(self):
        """Test that prompt includes example JSON output."""
        residency = Residency.objects.create(country="Belgium", town="Brussels")

        prompt = generate_enrich_prompt(residency, None)

        # Check for JSON structure in example
        assert '"country"' in prompt
        assert '"contacts"' in prompt
        assert '"application_type"' in prompt
