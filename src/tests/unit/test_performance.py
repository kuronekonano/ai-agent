"""
Unit tests for performance tracking functionality.
"""

import pytest

from ai_agent.performance import PerformanceTracker


def test_performance_tracker_initialization():
    """Test that PerformanceTracker initializes correctly."""
    tracker = PerformanceTracker()

    stats = tracker.get_statistics()
    assert stats["total_api_calls"] == 0
    assert stats["total_token_usage"]["total_tokens"] == 0
    assert stats["cost_summary"]["total_cost"] == 0.0


def test_record_api_call():
    """Test recording API calls and token usage."""
    tracker = PerformanceTracker()

    # Record API call
    record = tracker.record_api_call(
        provider="openai",
        model="gpt-4",
        endpoint="chat/completions",
        prompt_tokens=100,
        completion_tokens=50,
        duration_ms=500,
    )

    assert record.provider == "openai"
    assert record.model == "gpt-4"
    assert record.token_usage.total_tokens == 150

    stats = tracker.get_statistics()
    assert stats["total_api_calls"] == 1
    assert stats["total_token_usage"]["total_tokens"] == 150


def test_multiple_api_calls():
    """Test recording multiple API calls with different providers."""
    tracker = PerformanceTracker()

    # Record calls from different providers
    tracker.record_api_call(
        provider="openai",
        model="gpt-4",
        endpoint="chat/completions",
        prompt_tokens=100,
        completion_tokens=50,
        duration_ms=500,
    )

    tracker.record_api_call(
        provider="anthropic",
        model="claude-3-sonnet-20240229",
        endpoint="messages",
        prompt_tokens=200,
        completion_tokens=100,
        duration_ms=800,
    )

    stats = tracker.get_statistics()
    assert stats["total_api_calls"] == 2
    assert stats["total_token_usage"]["total_tokens"] == 450
    assert "openai/gpt-4" in stats["provider_statistics"]
    assert "anthropic/claude-3-sonnet-20240229" in stats["provider_statistics"]


def test_cost_calculation():
    """Test cost calculation functionality."""
    tracker = PerformanceTracker()

    tracker.record_api_call(
        provider="openai",
        model="gpt-4",
        endpoint="chat/completions",
        prompt_tokens=1000,  # 1K tokens
        completion_tokens=500,  # 0.5K tokens
        duration_ms=500,
    )

    stats = tracker.get_statistics()
    # gpt-4 pricing: input $0.03/1K, output $0.06/1K
    # Expected: (1 * 0.03) + (0.5 * 0.06) = 0.03 + 0.03 = 0.06
    assert abs(stats["cost_summary"]["total_cost"] - 0.06) < 0.001


def test_reset_functionality():
    """Test that reset clears all performance data."""
    tracker = PerformanceTracker()

    # Add some data
    tracker.record_api_call(
        provider="openai",
        model="gpt-4",
        endpoint="chat/completions",
        prompt_tokens=100,
        completion_tokens=50,
        duration_ms=500,
    )

    # Verify data exists
    stats_before = tracker.get_statistics()
    assert stats_before["total_api_calls"] == 1

    # Reset
    tracker.reset()

    # Verify data is cleared
    stats_after = tracker.get_statistics()
    assert stats_after["total_api_calls"] == 0
    assert stats_after["total_token_usage"]["total_tokens"] == 0


def test_unknown_model_pricing():
    """Test cost calculation for unknown models."""
    tracker = PerformanceTracker()

    tracker.record_api_call(
        provider="unknown",
        model="unknown-model",
        endpoint="test",
        prompt_tokens=100,
        completion_tokens=50,
        duration_ms=500,
    )

    stats = tracker.get_statistics()
    # Unknown models should have zero cost
    assert stats["cost_summary"]["total_cost"] == 0.0
