from unittest.mock import Mock, patch

import pytest

from src.ai_agent.model import AIClient, AnthropicClient, OpenAIClient, create_client


class TestAIClient:

    def test_ai_client_abstract(self):
        """Test that AIClient is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            AIClient()

    @patch("src.ai_agent.model.openai.OpenAI")
    def test_openai_client_initialization(self, mock_openai):
        """Test OpenAI client initialization."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test_key", model="gpt-4")

        assert client.model == "gpt-4"
        mock_openai.assert_called_once_with(api_key="test_key")

    @patch("src.ai_agent.model.anthropic.Anthropic")
    def test_anthropic_client_initialization(self, mock_anthropic):
        """Test Anthropic client initialization."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        client = AnthropicClient(api_key="test_key", model="claude-3-sonnet")

        assert client.model == "claude-3-sonnet"
        mock_anthropic.assert_called_once_with(api_key="test_key")

    def test_create_client_openai(self):
        """Test create_client factory function for OpenAI."""
        config = {"provider": "openai", "api_key": "test_key", "model": "gpt-4"}

        with patch("src.ai_agent.model.OpenAIClient") as mock_client:
            create_client(config)
            mock_client.assert_called_once_with(
                api_key="test_key", model="gpt-4", temperature=0.7, max_tokens=2000
            )

    def test_create_client_anthropic(self):
        """Test create_client factory function for Anthropic."""
        config = {
            "provider": "anthropic",
            "api_key": "test_key",
            "model": "claude-3-sonnet",
        }

        with patch("src.ai_agent.model.AnthropicClient") as mock_client:
            create_client(config)
            mock_client.assert_called_once_with(
                api_key="test_key",
                model="claude-3-sonnet",
                temperature=0.7,
                max_tokens=2000,
            )

    def test_create_client_invalid_provider(self):
        """Test create_client with invalid provider."""
        config = {"provider": "invalid", "api_key": "test_key"}

        with pytest.raises(ValueError, match="Unsupported AI provider: invalid"):
            create_client(config)
