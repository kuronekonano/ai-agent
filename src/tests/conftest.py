"""
Pytest configuration and fixtures for AI Agent tests.
"""

import os
from unittest.mock import Mock, patch

import pytest

from ai_agent import ReActEngine
from ai_agent.performance import PerformanceTracker


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    return {
        "openai": {
            "api_key": os.environ.get("AIAGENT_AUTH_TOKEN", "test-api-key"),
            "model": os.environ.get(
                "OPENAI_MODEL", "deepseek-chat"
            ),  # None for default
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "agent": {
            "max_iterations": 3,  # Reduced for testing
            "timeout_seconds": 30,
            "enable_memory": False,
            "enable_reflection": False,
        },
        "tools": {
            "enable_file_operations": False,
            "enable_web_search": False,
            "enable_calculator": True,
            "enable_code_execution": False,
        },
        "logging": {
            "level": "ERROR",  # Reduce log noise during tests
            "file": None,
            "console_output": False,
        },
    }


@pytest.fixture
def performance_tracker():
    """Provide a fresh PerformanceTracker instance."""
    return PerformanceTracker()


@pytest.fixture
def mock_ai_client():
    """Mock AI client to avoid real API calls during tests."""
    mock_client = Mock()
    mock_client.chat.return_value = "Test response"
    mock_client.get_performance_stats.return_value = {
        "total_api_calls": 0,
        "total_token_usage": {"total_tokens": 0},
    }
    return mock_client


@pytest.fixture
def react_engine(mock_config, mock_ai_client):
    """Provide a ReActEngine instance with mocked AI client."""
    with patch("ai_agent.agent.create_client", return_value=mock_ai_client):
        engine = ReActEngine(config=mock_config)
        return engine


@pytest.fixture(autouse=True)
def cleanup_env_vars():
    """Clean up environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
