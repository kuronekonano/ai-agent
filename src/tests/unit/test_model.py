"""
Unit tests for AI model functionality.
"""

from unittest.mock import Mock, patch

import pytest

from ai_agent.model import AIClient, OpenAIClient, create_client


class TestAIClient:
    """Test AIClient abstract base class."""

    def test_ai_client_abstract(self):
        """Test that AIClient is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            AIClient()


class TestOpenAIClient:
    """Test OpenAIClient functionality."""

    @patch("ai_agent.model.openai.OpenAI")
    def test_openai_client_initialization(self, mock_openai):
        """Test OpenAI client initialization."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        client = OpenAIClient(
            api_key="test_key", 
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )

        assert client.model == "gpt-4"
        assert client.default_params["temperature"] == 0.7
        assert client.default_params["max_tokens"] == 2000
        mock_openai.assert_called_once_with(api_key="test_key")

    @patch("ai_agent.model.openai.OpenAI")
    def test_openai_client_chat(self, mock_openai):
        """Test OpenAI client chat completion."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Create a proper Mock with integer values for token usage
        usage_mock = Mock()
        usage_mock.prompt_tokens = 10
        usage_mock.completion_tokens = 5
        usage_mock.total_tokens = 15
        
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response"))],
            usage=usage_mock
        )

        client = OpenAIClient(api_key="test_key", model="gpt-4")
        result = client.chat([{"role": "user", "content": "Hello"}])

        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()

    @patch("ai_agent.model.openai.OpenAI")
    def test_openai_client_complete(self, mock_openai):
        """Test OpenAI client text completion."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Create a proper Mock with integer values for token usage
        usage_mock = Mock()
        usage_mock.prompt_tokens = 20
        usage_mock.completion_tokens = 10
        usage_mock.total_tokens = 30
        
        mock_client.completions.create.return_value = Mock(
            choices=[Mock(text="Test completion")],
            usage=usage_mock
        )

        client = OpenAIClient(api_key="test_key", model="gpt-4")
        result = client.complete("Test prompt")

        assert result == "Test completion"
        mock_client.completions.create.assert_called_once()

    @patch("ai_agent.model.openai.OpenAI")
    def test_openai_client_performance_stats(self, mock_openai):
        """Test OpenAI client performance statistics."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test_key", model="gpt-4")
        
        # Initially should be empty
        stats = client.get_performance_stats()
        assert stats["total_api_calls"] == 0
        assert stats["total_token_usage"]["total_tokens"] == 0

        # After a call, should record stats
        # Create a proper Mock with integer values for token usage
        usage_mock = Mock()
        usage_mock.prompt_tokens = 100
        usage_mock.completion_tokens = 50
        usage_mock.total_tokens = 150
        
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response"))],
            usage=usage_mock
        )
        
        client.chat([{"role": "user", "content": "Hello"}])
        
        stats = client.get_performance_stats()
        assert stats["total_api_calls"] == 1
        assert stats["total_token_usage"]["total_tokens"] == 150

    @patch("ai_agent.model.openai.OpenAI")
    def test_openai_client_reset_stats(self, mock_openai):
        """Test resetting performance statistics."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Create a proper Mock with integer values for token usage
        usage_mock = Mock()
        usage_mock.prompt_tokens = 100
        usage_mock.completion_tokens = 50
        usage_mock.total_tokens = 150
        
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response"))],
            usage=usage_mock
        )

        client = OpenAIClient(api_key="test_key", model="gpt-4")
        client.chat([{"role": "user", "content": "Hello"}])
        
        # Verify stats recorded
        stats_before = client.get_performance_stats()
        assert stats_before["total_api_calls"] == 1
        
        # Reset
        client.reset_performance_stats()
        
        # Verify stats cleared
        stats_after = client.get_performance_stats()
        assert stats_after["total_api_calls"] == 0
        assert stats_after["total_token_usage"]["total_tokens"] == 0


class TestCreateClient:
    """Test create_client factory function."""

    def test_create_client_openai(self):
        """Test create_client for OpenAI provider."""
        config = {
            "provider": "openai",
            "api_key": "test_key", 
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }

        with patch("ai_agent.model.OpenAIClient") as mock_client:
            create_client(config)
            mock_client.assert_called_once_with(
                api_key="test_key",
                model="gpt-4",
                temperature=0.7,
                max_tokens=2000,
                base_url=None
            )

    def test_create_client_default_provider(self):
        """Test create_client with default provider (OpenAI)."""
        config = {
            "api_key": "test_key",
            "model": "gpt-4"
        }

        with patch("ai_agent.model.OpenAIClient") as mock_client:
            create_client(config)
            mock_client.assert_called_once()

    def test_create_client_unsupported_provider(self):
        """Test create_client with unsupported provider."""
        config = {
            "provider": "unsupported",
            "api_key": "test_key"
        }

        with pytest.raises(ValueError, match="Unsupported AI provider"):
            create_client(config)