"""
Integration test for performance tracking within a single agent run.
"""

import os
from unittest.mock import patch

import pytest

from ai_agent import ReActEngine


@pytest.mark.integration
def test_single_run_performance_with_mock():
    """Test performance tracking with mocked AI client."""
    # Use environment variables or defaults
    config = {
        "openai": {
            "api_key": os.environ.get("OPENAI_API_KEY", "test-api-key"),
            "model": os.environ.get("OPENAI_MODEL"),  # None for default
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "agent": {
            "max_iterations": 3,
            "timeout_seconds": 30,
        },
        "tools": {
            "enable_calculator": True,
            "enable_file_operations": False,
            "enable_web_search": False,
        },
        "logging": {
            "level": "ERROR",
            "console_output": False,
        },
    }

    # Mock the AI client to avoid real API calls
    with patch("ai_agent.agent.create_client") as mock_create:
        mock_client = mock_create.return_value
        mock_client.chat.return_value = "Test response"

        # Mock should return 0 for initial stats, then updated stats after calls
        # Use a simple counter approach
        mock_client._call_counter = 0

        def mock_get_performance_stats():
            if mock_client._call_counter == 0:
                mock_client._call_counter += 1
                return {"total_api_calls": 0, "total_token_usage": {"total_tokens": 0}}
            else:
                return {
                    "total_api_calls": 2,
                    "total_token_usage": {"total_tokens": 353},
                }

        mock_client.get_performance_stats.side_effect = mock_get_performance_stats

        agent = ReActEngine(config=config)

        # Check initial stats
        initial_stats = agent.get_performance_stats()
        assert initial_stats["total_api_calls"] == 0

        # Run a simple task
        agent.run("Say hello")

        # Verify performance stats were recorded
        post_task_stats = agent.get_performance_stats()
        assert post_task_stats["total_api_calls"] > 0
        assert post_task_stats["total_token_usage"]["total_tokens"] > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="No API keys provided for live testing",
)
def test_single_run_performance_live():
    """Test performance tracking with real API calls (requires API keys)."""
    config = {
        "openai": {
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "model": os.environ.get("OPENAI_MODEL"),
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "agent": {
            "max_iterations": 3,
            "timeout_seconds": 30,
        },
        "tools": {
            "enable_calculator": True,
            "enable_file_operations": False,
            "enable_web_search": False,
        },
        "logging": {
            "level": "INFO",
            "console_output": True,
        },
    }

    agent = ReActEngine(config=config)

    # Check initial stats
    initial_stats = agent.get_performance_stats()
    assert initial_stats["total_api_calls"] == 0

    # Run a simple task
    agent.run("Say hello")

    # Verify performance stats were recorded
    post_task_stats = agent.get_performance_stats()
    assert post_task_stats["total_api_calls"] > 0
    assert isinstance(post_task_stats["total_token_usage"]["total_tokens"], int)
