from unittest.mock import MagicMock, patch

import pytest
from rest_framework.exceptions import Throttled

from services.gemini_service import GeminiClient


@pytest.mark.django_db
class TestGeminiClientInit:
    """Tests for GeminiClient initialization."""

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_init_loads_env(self, mock_load_dotenv, mock_genai_client):
        """Test that __init__ loads .env file."""
        mock_client = MagicMock()
        mock_genai_client.return_value = mock_client

        GeminiClient()

        mock_load_dotenv.assert_called_once_with(".env")

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_init_creates_client(self, mock_load_dotenv, mock_genai_client):
        """Test that Client is created during initialization."""
        mock_client = MagicMock()
        mock_genai_client.return_value = mock_client

        client = GeminiClient()

        mock_genai_client.assert_called_once()
        assert client.client == mock_client

    @patch.dict("os.environ", {}, clear=True)
    @patch("services.gemini_service.load_dotenv")
    def test_init_raises_error_without_api_key(self, mock_load_dotenv):
        """Test that RuntimeError is raised if GEMINI_API_KEY is missing."""
        with pytest.raises(RuntimeError, match="Missing GEMINI_API_KEY"):
            GeminiClient()

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_init_creates_grounding_tool(
        self, mock_load_dotenv, mock_genai_client, mock_google_search, mock_tool, mock_config
    ):
        """Test that grounding tool is created on initialization."""
        mock_client = MagicMock()
        mock_genai_client.return_value = mock_client
        mock_google_search_inst = MagicMock()
        mock_google_search.return_value = mock_google_search_inst
        mock_tool_inst = MagicMock()
        mock_tool.return_value = mock_tool_inst
        mock_config_inst = MagicMock()
        mock_config.return_value = mock_config_inst

        client = GeminiClient()

        mock_google_search.assert_called_once()
        mock_tool.assert_called_once()
        assert client.grounding_tool == mock_tool_inst

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_init_creates_generation_config(
        self, mock_load_dotenv, mock_genai_client, mock_google_search, mock_tool, mock_config
    ):
        """Test that GenerateContentConfig is created with grounding tool."""
        mock_client = MagicMock()
        mock_genai_client.return_value = mock_client
        mock_google_search.return_value = MagicMock()
        mock_tool_inst = MagicMock()
        mock_tool.return_value = mock_tool_inst
        mock_config_inst = MagicMock()
        mock_config.return_value = mock_config_inst

        client = GeminiClient()

        mock_config.assert_called_once_with(tools=[mock_tool_inst])
        assert client.config == mock_config_inst


@pytest.mark.django_db
class TestGeminiClientSearch:
    """Tests for GeminiClient.search method."""

    @patch("services.gemini_service.increment_llm_call_counter")
    @patch("services.gemini_service.check_llm_rate_limit")
    @patch("services.gemini_service.client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_search_successful_response(
        self,
        mock_load_dotenv,
        mock_genai_client,
        mock_google_search,
        mock_tool,
        mock_config,
        mock_module_client,
        mock_rate_limit,
        mock_increment,
    ):
        """Test successful search call with rate limit check."""
        mock_client = MagicMock()
        mock_genai_client.return_value = mock_client
        mock_google_search.return_value = MagicMock()
        mock_tool.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.text = "Search results about festivals"
        mock_module_client.models.generate_content.return_value = mock_response

        mock_rate_limit.return_value = (True, 50)
        mock_increment.return_value = 1

        client = GeminiClient()
        result = client.search("Find festivals in Paris", "test_tenant")

        assert result == "Search results about festivals"
        mock_rate_limit.assert_called_once_with("test_tenant")
        mock_increment.assert_called_once_with("test_tenant")

    @patch("services.gemini_service.check_llm_rate_limit")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_search_rate_limit_exceeded(
        self,
        mock_load_dotenv,
        mock_genai_client,
        mock_google_search,
        mock_tool,
        mock_config,
        mock_rate_limit,
    ):
        """Test that Throttled exception is raised when rate limit is exceeded."""
        mock_genai_client.return_value = MagicMock()
        mock_google_search.return_value = MagicMock()
        mock_tool.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        mock_rate_limit.return_value = (False, 0)

        client = GeminiClient()

        with pytest.raises(Throttled):
            client.search("Find festivals", "test_tenant")

    @patch("services.gemini_service.increment_llm_call_counter")
    @patch("services.gemini_service.check_llm_rate_limit")
    @patch("services.gemini_service.client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_search_handles_api_exception(
        self,
        mock_load_dotenv,
        mock_genai_client,
        mock_google_search,
        mock_tool,
        mock_config,
        mock_module_client,
        mock_rate_limit,
        mock_increment,
    ):
        """Test that API exceptions are caught and returned as error messages."""
        mock_genai_client.return_value = MagicMock()
        mock_google_search.return_value = MagicMock()
        mock_tool.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        mock_rate_limit.return_value = (True, 50)
        mock_module_client.models.generate_content.side_effect = Exception("API Error occurred")

        client = GeminiClient()
        result = client.search("Find festivals", "test_tenant")

        assert "[Gemini chat error]" in result
        assert "API Error occurred" in result

    @patch("services.gemini_service.increment_llm_call_counter")
    @patch("services.gemini_service.check_llm_rate_limit")
    @patch("services.gemini_service.client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_search_sends_correct_parameters(
        self,
        mock_load_dotenv,
        mock_genai_client,
        mock_google_search,
        mock_tool,
        mock_config,
        mock_module_client,
        mock_rate_limit,
        mock_increment,
    ):
        """Test that search sends correct parameters to generate_content."""
        mock_genai_client.return_value = MagicMock()
        mock_google_search.return_value = MagicMock()
        mock_tool_inst = MagicMock()
        mock_tool.return_value = mock_tool_inst
        mock_config_inst = MagicMock()
        mock_config.return_value = mock_config_inst

        mock_response = MagicMock()
        mock_response.text = "Results"
        mock_module_client.models.generate_content.return_value = mock_response

        mock_rate_limit.return_value = (True, 50)
        mock_increment.return_value = 1

        client = GeminiClient()
        client.search("Search for street performers", "test_tenant")

        mock_module_client.models.generate_content.assert_called_once()
        call_kwargs = mock_module_client.models.generate_content.call_args[1]
        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert call_kwargs["contents"] == "Search for street performers"
        assert call_kwargs["config"] == mock_config_inst

    @patch("services.gemini_service.increment_llm_call_counter")
    @patch("services.gemini_service.check_llm_rate_limit")
    @patch("services.gemini_service.client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_search_uses_text_attribute_if_available(
        self,
        mock_load_dotenv,
        mock_genai_client,
        mock_google_search,
        mock_tool,
        mock_config,
        mock_module_client,
        mock_rate_limit,
        mock_increment,
    ):
        """Test that search returns .text attribute if available."""
        mock_genai_client.return_value = MagicMock()
        mock_google_search.return_value = MagicMock()
        mock_tool.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.text = "Text from response"
        mock_module_client.models.generate_content.return_value = mock_response

        mock_rate_limit.return_value = (True, 50)
        mock_increment.return_value = 1

        client = GeminiClient()
        result = client.search("test query", "test_tenant")

        assert result == "Text from response"

    @patch("services.gemini_service.increment_llm_call_counter")
    @patch("services.gemini_service.check_llm_rate_limit")
    @patch("services.gemini_service.client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_api_key"})
    @patch("services.gemini_service.types.GenerateContentConfig")
    @patch("services.gemini_service.types.Tool")
    @patch("services.gemini_service.types.GoogleSearch")
    @patch("services.gemini_service.genai.Client")
    @patch("services.gemini_service.load_dotenv")
    def test_search_uses_str_conversion_if_text_unavailable(
        self,
        mock_load_dotenv,
        mock_genai_client,
        mock_google_search,
        mock_tool,
        mock_config,
        mock_module_client,
        mock_rate_limit,
        mock_increment,
    ):
        """Test that search converts to string if .text attribute is missing."""
        mock_genai_client.return_value = MagicMock()
        mock_google_search.return_value = MagicMock()
        mock_tool.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        # Create a mock response without .text attribute
        mock_response = MagicMock()
        # Delete the .text attribute to simulate it not being present
        del mock_response.text
        mock_response.__str__.return_value = "String conversion result"
        mock_module_client.models.generate_content.return_value = mock_response

        mock_rate_limit.return_value = (True, 50)
        mock_increment.return_value = 1

        client = GeminiClient()
        result = client.search("test query", "test_tenant")

        assert result == "String conversion result"
