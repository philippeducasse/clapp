from unittest.mock import MagicMock, patch

import pytest
from rest_framework.exceptions import Throttled

from services.mistral_service import MistralClient


@pytest.mark.django_db
class TestMistralClientInit:
    """Tests for MistralClient initialization."""

    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_init_creates_client_with_api_key(self, mock_mistral_class):
        """Test that client is created with API key from environment."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_client.beta.agents.create.return_value = MagicMock(id="agent123")

        client = MistralClient()

        mock_mistral_class.assert_called_once_with(api_key="test_key")
        assert client.client == mock_client
        assert client.model == "mistral-small"

    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_init_creates_search_agent(self, mock_mistral_class):
        """Test that search agent is created on initialization."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_agent = MagicMock(id="agent123")
        mock_client.beta.agents.create.return_value = mock_agent

        client = MistralClient()

        mock_client.beta.agents.create.assert_called_once()
        call_kwargs = mock_client.beta.agents.create.call_args[1]
        assert call_kwargs["name"] == "Websearch Agent"
        assert call_kwargs["model"] == "mistral-medium-2508"
        assert client.search_agent.id == "agent123"


@pytest.mark.django_db
class TestMistralClientChat:
    """Tests for MistralClient.chat method."""

    @patch("services.mistral_service.increment_llm_call_counter")
    @patch("services.mistral_service.check_llm_rate_limit")
    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_chat_successful_response(self, mock_mistral_class, mock_rate_limit, mock_increment):
        """Test successful chat call with rate limit check."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_client.beta.agents.create.return_value = MagicMock(id="agent123")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello, World!"))]
        mock_client.chat.complete.return_value = mock_response

        mock_rate_limit.return_value = (True, 50)
        mock_increment.return_value = 1

        client = MistralClient()
        result = client.chat("What is AI?", "test_tenant")

        assert result == "Hello, World!"
        mock_rate_limit.assert_called_once_with("test_tenant")
        mock_increment.assert_called_once_with("test_tenant")

    @patch("services.mistral_service.check_llm_rate_limit")
    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_chat_rate_limit_exceeded(self, mock_mistral_class, mock_rate_limit):
        """Test that Throttled exception is raised when rate limit is exceeded."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_client.beta.agents.create.return_value = MagicMock(id="agent123")

        mock_rate_limit.return_value = (False, 0)

        client = MistralClient()

        with pytest.raises(Throttled):
            client.chat("What is AI?", "test_tenant")

    @patch("services.mistral_service.increment_llm_call_counter")
    @patch("services.mistral_service.check_llm_rate_limit")
    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_chat_handles_api_exception(self, mock_mistral_class, mock_rate_limit, mock_increment):
        """Test that API exceptions are caught and returned as strings."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_client.beta.agents.create.return_value = MagicMock(id="agent123")

        mock_rate_limit.return_value = (True, 50)
        mock_client.chat.complete.side_effect = Exception("API Error")

        client = MistralClient()
        result = client.chat("What is AI?", "test_tenant")

        assert "API Error" in result

    @patch("services.mistral_service.increment_llm_call_counter")
    @patch("services.mistral_service.check_llm_rate_limit")
    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_chat_sends_correct_message_format(
        self, mock_mistral_class, mock_rate_limit, mock_increment
    ):
        """Test that chat sends message in correct format."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_client.beta.agents.create.return_value = MagicMock(id="agent123")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.complete.return_value = mock_response

        mock_rate_limit.return_value = (True, 50)
        mock_increment.return_value = 1

        client = MistralClient()
        client.chat("Custom prompt", "test_tenant")

        mock_client.chat.complete.assert_called_once()
        call_kwargs = mock_client.chat.complete.call_args[1]
        assert call_kwargs["model"] == "mistral-small"
        assert call_kwargs["messages"][0]["role"] == "user"
        assert call_kwargs["messages"][0]["content"] == "Custom prompt"


@pytest.mark.django_db
class TestMistralClientSearch:
    """Tests for MistralClient.search method."""

    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_search_returns_conversation_response(self, mock_mistral_class):
        """Test that search method returns ConversationResponse."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_agent = MagicMock(id="agent123")
        mock_client.beta.agents.create.return_value = mock_agent

        mock_response = MagicMock()
        mock_client.beta.conversations.start.return_value = mock_response

        client = MistralClient()
        result = client.search("Search query")

        assert result == mock_response

    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_search_calls_agent_with_query(self, mock_mistral_class):
        """Test that search calls the agent with the correct query."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_agent = MagicMock(id="agent_test_123")
        mock_client.beta.agents.create.return_value = mock_agent
        mock_response = MagicMock()
        mock_client.beta.conversations.start.return_value = mock_response

        client = MistralClient()
        client.search("Find circus festivals in France")

        mock_client.beta.conversations.start.assert_called_once_with(
            agent_id="agent_test_123", inputs="Find circus festivals in France"
        )

    @patch.dict(
        "os.environ", {"MISTRAL_API_KEY": "test_key", "MISTRAL_DEFAULT_MODEL": "mistral-small"}
    )
    @patch("services.mistral_service.Mistral")
    def test_search_uses_initialized_agent(self, mock_mistral_class):
        """Test that search uses the agent created during initialization."""
        mock_client = MagicMock()
        mock_mistral_class.return_value = mock_client
        mock_agent = MagicMock(id="agent_xyz")
        mock_client.beta.agents.create.return_value = mock_agent
        mock_response = MagicMock()
        mock_client.beta.conversations.start.return_value = mock_response

        client = MistralClient()
        # Verify that the agent is stored
        assert client.search_agent.id == "agent_xyz"

        client.search("test")
        # Verify that search uses the stored agent
        call_kwargs = mock_client.beta.conversations.start.call_args[1]
        assert call_kwargs["agent_id"] == "agent_xyz"
