"""
Metrics analyzer for agent evaluation framework.
"""

import statistics
from datetime import datetime
from typing import Any, Dict, List


class Analyzer:
    """Analyzer for aggregating metrics from execution records."""

    def __init__(self):
        pass

    def analyze_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a list of execution records and return aggregated metrics."""
        if not records:
            return self._empty_analysis()

        # Extract metrics
        scores = []
        latencies = []
        token_usages = []
        status_counts = {"success": 0, "error": 0}

        successful_records = []

        for record in records:
            status = record.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            if status == "success":
                successful_records.append(record)

                # Extract score
                scoring = record.get("scoring", {})
                score = scoring.get("score", 0.0)
                if isinstance(score, (int, float)):
                    scores.append(score)

                # Extract latency
                response = record.get("response", {})
                latency = response.get("latency_ms", 0)
                if isinstance(latency, (int, float)):
                    latencies.append(latency)

                # Extract token usage
                usage = response.get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                if isinstance(total_tokens, (int, float)):
                    token_usages.append(total_tokens)

        # Calculate statistics
        score_stats = self._calculate_stats(scores)
        latency_stats = self._calculate_stats(latencies)
        token_stats = self._calculate_stats(token_usages)

        # Calculate accuracy
        total_cases = len(records)
        successful_cases = len(successful_records)
        accuracy = score_stats["mean"] if scores else 0.0

        # Get top failing cases
        failing_cases = self._get_failing_cases(records)

        return {
            "summary": {
                "total_cases": total_cases,
                "successful_cases": successful_cases,
                "failed_cases": total_cases - successful_cases,
                "success_rate": (
                    successful_cases / total_cases if total_cases > 0 else 0.0
                ),
                "accuracy": accuracy,
                "status_distribution": status_counts,
            },
            "score_statistics": score_stats,
            "latency_statistics": {"unit": "milliseconds", **latency_stats},
            "token_statistics": {"unit": "tokens", **token_stats},
            "top_failing_cases": failing_cases[:5],  # Top 5 failing cases
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _calculate_stats(self, values: List[float]) -> Dict[str, Any]:
        """Calculate statistical measures for a list of values."""
        if not values:
            return {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
            }

        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
        }

    def _get_failing_cases(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get cases with lowest scores."""
        failing_cases = []

        for record in records:
            if record.get("status") == "success":
                scoring = record.get("scoring", {})
                score = scoring.get("score", 1.0)  # Default to 1.0 if missing

                failing_cases.append(
                    {
                        "test_case_id": record.get("test_case_id", "unknown"),
                        "score": score,
                        "expected": scoring.get("expected", ""),
                        "actual": scoring.get("actual", ""),
                        "reason": scoring.get("reason", ""),
                    }
                )

        # Sort by score (ascending - worst first)
        failing_cases.sort(key=lambda x: x["score"])
        return failing_cases

    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            "summary": {
                "total_cases": 0,
                "successful_cases": 0,
                "failed_cases": 0,
                "success_rate": 0.0,
                "accuracy": 0.0,
                "status_distribution": {},
            },
            "score_statistics": {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
            },
            "latency_statistics": {
                "unit": "milliseconds",
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
            },
            "token_statistics": {
                "unit": "tokens",
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
            },
            "top_failing_cases": [],
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def generate_report(
        self, analysis: Dict[str, Any], format: str = "markdown"
    ) -> str:
        """Generate human-readable report from analysis."""
        if format == "markdown":
            return self._generate_markdown_report(analysis)
        elif format == "json":
            import json

            return json.dumps(analysis, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Generate markdown format report."""
        summary = analysis["summary"]
        score_stats = analysis["score_statistics"]
        latency_stats = analysis["latency_statistics"]
        token_stats = analysis["token_statistics"]

        report = [
            "# Agent Evaluation Report",
            "",
            f"**Analysis Time**: {analysis['analysis_timestamp']}",
            "",
            "## Summary",
            "",
            f"- **Total Cases**: {summary['total_cases']}",
            f"- **Successful Cases**: {summary['successful_cases']}",
            f"- **Failed Cases**: {summary['failed_cases']}",
            f"- **Success Rate**: {summary['success_rate']:.1%}",
            f"- **Accuracy**: {summary['accuracy']:.1%}",
            "",
            "## Performance Statistics",
            "",
            "### Scores",
            f"- Mean: {score_stats['mean']:.3f}",
            f"- Median: {score_stats['median']:.3f}",
            f"- Std Dev: {score_stats['std_dev']:.3f}",
            f"- Range: {score_stats['min']:.3f} - {score_stats['max']:.3f}",
            "",
            "### Latency (ms)",
            f"- Mean: {latency_stats['mean']:.1f}",
            f"- Median: {latency_stats['median']:.1f}",
            f"- Std Dev: {latency_stats['std_dev']:.1f}",
            f"- Range: {latency_stats['min']:.1f} - {latency_stats['max']:.1f}",
            "",
            "### Token Usage",
            f"- Mean: {token_stats['mean']:.1f}",
            f"- Median: {token_stats['median']:.1f}",
            f"- Std Dev: {token_stats['std_dev']:.1f}",
            f"- Range: {token_stats['min']:.1f} - {token_stats['max']:.1f}",
            "",
        ]

        # Add failing cases section if any
        failing_cases = analysis.get("top_failing_cases", [])
        if failing_cases:
            report.extend(
                [
                    "## Top Failing Cases",
                    "",
                    "| Case ID | Score | Expected | Actual | Reason |",
                    "|---------|-------|----------|--------|--------|",
                ]
            )

            for case in failing_cases:
                report.append(
                    f"| {case['test_case_id']} | {case['score']:.3f} | "
                    f"{self._truncate_text(case['expected'])} | "
                    f"{self._truncate_text(case['actual'])} | "
                    f"{self._truncate_text(case['reason'])} |"
                )

            report.append("")

        return "\n".join(report)

    def _truncate_text(self, text: str, max_length: int = 30) -> str:
        """Truncate text for display in tables."""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
