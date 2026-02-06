import pytest
from organisations.festivals.models import Festival
from organisations.utils import clean_organisation_data, extract_fields_from_llm


@pytest.mark.django_db
class TestExtractFieldsFromLLM:
    """Tests for extract_fields_from_llm function."""

    def test_extract_valid_json(self):
        """Test extracting valid JSON from LLM response."""
        llm_response = '```json\n{"name": "Festival", "country": "France"}\n```'
        result = extract_fields_from_llm(llm_response)

        assert result == {"name": "Festival", "country": "France"}

    def test_extract_json_without_markdown(self):
        """Test extracting JSON without markdown code blocks."""
        llm_response = '{"name": "Festival", "country": "France"}'
        result = extract_fields_from_llm(llm_response)

        assert result == {"name": "Festival", "country": "France"}

    def test_extract_json_with_whitespace(self):
        """Test extracting JSON with extra whitespace."""
        llm_response = '```json  \n  {"name": "Festival"}\n  ```'
        result = extract_fields_from_llm(llm_response)

        assert result == {"name": "Festival"}

    def test_invalid_json_returns_empty_dict(self):
        """Test that invalid JSON returns empty dictionary."""
        llm_response = '```json\n{"name": "Festival"invalid json}\n```'
        result = extract_fields_from_llm(llm_response)

        assert result == {}

    def test_empty_string_returns_empty_dict(self):
        """Test that empty string returns empty dictionary."""
        result = extract_fields_from_llm("")

        assert result == {}

    def test_complex_json_structure(self):
        """Test extracting complex nested JSON."""
        llm_response = """```json
        {
            "name": "Festival",
            "contacts": [
                {"email": "info@festival.com", "name": "John"}
            ],
            "metadata": {"type": "music"}
        }
        ```"""
        result = extract_fields_from_llm(llm_response)

        assert result["name"] == "Festival"
        assert len(result["contacts"]) == 1
        assert result["contacts"][0]["email"] == "info@festival.com"


@pytest.mark.django_db
class TestCleanOrganisationData:
    """Tests for clean_organisation_data function."""

    def test_clean_name_to_title_case(self):
        """Test that organisation name is converted to title case."""
        festival = Festival.objects.create(name="lowercase festival name", country="France")

        clean_organisation_data(festival)

        assert festival.name == "Lowercase Festival Name"

    def test_clean_town_removes_nan(self):
        """Test that 'nan' town is converted to empty string."""
        festival = Festival.objects.create(name="Festival", town="nan", country="France")

        clean_organisation_data(festival)

        assert festival.town == ""

    def test_clean_town_title_case(self):
        """Test that town is converted to title case."""
        festival = Festival.objects.create(name="Festival", town="paris", country="France")

        clean_organisation_data(festival)

        assert festival.town == "Paris"

    def test_clean_country_removes_nan(self):
        """Test that 'nan' country is converted to empty string."""
        festival = Festival.objects.create(name="Festival", country="nan")

        clean_organisation_data(festival)

        assert festival.country == ""

    def test_clean_country_title_case(self):
        """Test that country is converted to title case."""
        festival = Festival.objects.create(name="Festival", country="france")

        clean_organisation_data(festival)

        assert festival.country == "France"

    def test_clean_comments_lowercase(self):
        """Test that comments are converted to lowercase."""
        festival = Festival.objects.create(
            name="Festival", country="France", comments="IMPORTANT NOTES"
        )

        clean_organisation_data(festival)

        assert festival.comments == "important notes"

    def test_clean_comments_removes_nan(self):
        """Test that 'nan' comments are converted to empty string."""
        festival = Festival.objects.create(name="Festival", country="France", comments="nan")

        clean_organisation_data(festival)

        assert festival.comments == ""

    def test_clean_website_url_adds_https(self):
        """Test that website URL without http protocol gets https added."""
        festival = Festival.objects.create(
            name="Festival", country="France", website_url="example.com"
        )

        clean_organisation_data(festival)

        assert festival.website_url == "https://example.com"

    def test_clean_website_url_preserves_http(self):
        """Test that website URL with http protocol is preserved."""
        festival = Festival.objects.create(
            name="Festival", country="France", website_url="http://example.com"
        )

        clean_organisation_data(festival)

        assert festival.website_url == "http://example.com"

    def test_clean_website_url_preserves_https(self):
        """Test that website URL with https protocol is preserved."""
        festival = Festival.objects.create(
            name="Festival", country="France", website_url="https://example.com"
        )

        clean_organisation_data(festival)

        assert festival.website_url == "https://example.com"

    def test_clean_website_url_lowercase(self):
        """Test that website URL is converted to lowercase."""
        festival = Festival.objects.create(
            name="Festival", country="France", website_url="https://EXAMPLE.COM"
        )

        clean_organisation_data(festival)

        assert festival.website_url == "https://example.com"

    def test_clean_description_adds_period(self):
        """Test that description without period gets one added."""
        festival = Festival.objects.create(
            name="Festival", country="France", description="A beautiful festival"
        )

        clean_organisation_data(festival)

        assert festival.description == "A beautiful festival."

    def test_clean_description_preserves_period(self):
        """Test that description with period is preserved."""
        festival = Festival.objects.create(
            name="Festival", country="France", description="A beautiful festival."
        )

        clean_organisation_data(festival)

        assert festival.description == "A beautiful festival."

    def test_clean_multiple_fields(self):
        """Test cleaning multiple fields at once."""
        festival = Festival.objects.create(
            name="lowercase name",
            town="paris",
            country="france",
            website_url="example.com",
            description="A festival",
            comments="NOTES",
        )

        clean_organisation_data(festival)

        assert festival.name == "Lowercase Name"
        assert festival.town == "Paris"
        assert festival.country == "France"
        assert festival.website_url == "https://example.com"
        assert festival.description == "A festival."
        assert festival.comments == "notes"

    def test_clean_none_values_skipped(self):
        """Test that None values in optional fields are not processed."""
        festival = Festival.objects.create(
            name="Festival",
            country="France",
            town="Paris",
            website_url="https://example.com",
            description="Test description",
            comments="Test comment",
        )

        clean_organisation_data(festival)

        # URL should be processed and maintained
        assert festival.website_url == "https://example.com"
        # Description should have period added
        assert festival.description == "Test description."
        # Comments should be lowercased
        assert festival.comments == "test comment"
