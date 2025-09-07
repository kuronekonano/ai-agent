"""
Evaluation scorers for agent evaluation framework.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict


class Scorer(ABC):
    """Abstract base class for evaluation scorers."""

    @abstractmethod
    def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Score the agent response.

        Args:
            data: Dictionary containing 'expected', 'actual', and 'response'

        Returns:
            Dictionary with scoring metrics
        """
        pass


class ExactMatchScorer(Scorer):
    """Exact match scorer for precise string comparison."""

    def __init__(self):
        pass

    def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Score based on exact string match."""
        expected = data.get("expected")
        actual = data.get("actual")

        if expected is None or actual is None:
            return {
                "exact_match": False,
                "score": 0.0,
                "reason": "Missing expected or actual value",
            }

        is_match = str(expected).strip().lower() == str(actual).strip().lower()

        return {
            "exact_match": is_match,
            "score": 1.0 if is_match else 0.0,
            "expected": expected,
            "actual": actual,
            "reason": "Exact match" if is_match else "No exact match",
        }


class NormalizedMatchScorer(Scorer):
    """Normalized match scorer that ignores case, whitespace, and punctuation."""

    def __init__(self):
        pass

    def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Score based on normalized string comparison."""
        expected = data.get("expected")
        actual = data.get("actual")

        if expected is None or actual is None:
            return {
                "normalized_match": False,
                "score": 0.0,
                "reason": "Missing expected or actual value",
            }

        # Normalize strings
        normalized_expected = self._normalize_text(expected)
        normalized_actual = self._normalize_text(actual)

        is_match = normalized_expected == normalized_actual

        return {
            "normalized_match": is_match,
            "score": 1.0 if is_match else 0.0,
            "expected": expected,
            "actual": actual,
            "normalized_expected": normalized_expected,
            "normalized_actual": normalized_actual,
            "reason": "Normalized match" if is_match else "No normalized match",
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing punctuation, extra spaces, and lowercasing."""
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = re.sub(r"[^\w\s]", " ", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()


class BinaryScorer(Scorer):
    """Binary scorer that returns 1.0 if actual contains expected, else 0.0."""

    def __init__(self):
        pass

    def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Score based on substring containment."""
        expected = data.get("expected")
        actual = data.get("actual")

        if expected is None or actual is None:
            return {
                "contains_match": False,
                "score": 0.0,
                "reason": "Missing expected or actual value",
            }

        contains_match = str(expected).lower() in str(actual).lower()

        return {
            "contains_match": contains_match,
            "score": 1.0 if contains_match else 0.0,
            "expected": expected,
            "actual": actual,
            "reason": (
                "Contains expected" if contains_match else "Does not contain expected"
            ),
        }


def create_scorer(scorer_type: str = "exact") -> Scorer:
    """Factory function to create scorer instance."""
    if scorer_type == "exact":
        return ExactMatchScorer()
    elif scorer_type == "normalized":
        return NormalizedMatchScorer()
    elif scorer_type == "binary":
        return BinaryScorer()
    else:
        raise ValueError(f"Unknown scorer type: {scorer_type}")
