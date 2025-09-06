import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .trajectory import Trajectory, TrajectoryStep


class Analyzer:
    """Analyzes agent trajectories to extract insights and metrics."""

    def __init__(self):
        pass

    def analyze_trajectory(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Comprehensive analysis of a trajectory."""
        if not trajectory:
            return {}

        return {
            "basic_metrics": self._get_basic_metrics(trajectory),
            "step_analysis": self._analyze_steps(trajectory.steps),
            "tool_usage": self._analyze_tool_usage(trajectory.steps),
            "efficiency_metrics": self._calculate_efficiency_metrics(trajectory),
            "success_analysis": self._analyze_success(trajectory),
        }

    def _get_basic_metrics(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Get basic metrics from the trajectory."""
        return {
            "task": trajectory.task,
            "total_steps": trajectory.total_steps,
            "duration_seconds": trajectory.duration_seconds,
            "success": trajectory.success,
            "start_time": trajectory.start_time,
            "end_time": trajectory.end_time,
        }

    def _analyze_steps(self, steps: List[TrajectoryStep]) -> Dict[str, Any]:
        """Analyze the steps in the trajectory."""
        if not steps:
            return {}

        step_types = {}
        thought_lengths = []
        result_lengths = []

        for step in steps:
            step_types[step.action] = step_types.get(step.action, 0) + 1
            thought_lengths.append(len(step.thought.split()))
            result_lengths.append(len(step.result.split()))

        return {
            "step_type_distribution": step_types,
            "avg_thought_length": (
                sum(thought_lengths) / len(thought_lengths) if thought_lengths else 0
            ),
            "avg_result_length": (
                sum(result_lengths) / len(result_lengths) if result_lengths else 0
            ),
            "max_thought_length": max(thought_lengths) if thought_lengths else 0,
            "max_result_length": max(result_lengths) if result_lengths else 0,
        }

    def _analyze_tool_usage(self, steps: List[TrajectoryStep]) -> Dict[str, Any]:
        """Analyze tool usage patterns."""
        tool_usage = {}
        tool_success = {}

        for step in steps:
            if step.action != "final_answer":
                tool_usage[step.action] = tool_usage.get(step.action, 0) + 1

                if "Error" not in step.result:
                    tool_success[step.action] = tool_success.get(step.action, 0) + 1

        tool_success_rates = {}
        for tool, total_usage in tool_usage.items():
            successful_uses = tool_success.get(tool, 0)
            tool_success_rates[tool] = (
                successful_uses / total_usage if total_usage > 0 else 0
            )

        return {
            "tool_usage_count": tool_usage,
            "tool_success_rates": tool_success_rates,
            "most_used_tool": (
                max(tool_usage.items(), key=lambda x: x[1])[0] if tool_usage else None
            ),
        }

    def _calculate_efficiency_metrics(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Calculate efficiency metrics."""
        if not trajectory.duration_seconds or trajectory.total_steps == 0:
            return {}

        avg_step_time = trajectory.duration_seconds / trajectory.total_steps
        steps_per_minute = 60 / avg_step_time if avg_step_time > 0 else 0

        return {
            "average_step_time_seconds": avg_step_time,
            "steps_per_minute": steps_per_minute,
            "total_duration_minutes": trajectory.duration_seconds / 60,
        }

    def _analyze_success(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Analyze success factors."""
        return {
            "success": trajectory.success,
            "final_result_length": (
                len(trajectory.final_result.split()) if trajectory.final_result else 0
            ),
            "result_quality": (
                self._assess_result_quality(trajectory.final_result)
                if trajectory.final_result
                else "unknown"
            ),
        }

    def _assess_result_quality(self, result: str) -> str:
        """Simple heuristic for assessing result quality."""
        word_count = len(result.split())

        if word_count < 10:
            return "brief"
        elif word_count < 50:
            return "moderate"
        elif word_count < 200:
            return "detailed"
        else:
            return "comprehensive"

    def compare_trajectories(self, trajectories: List[Trajectory]) -> Dict[str, Any]:
        """Compare multiple trajectories."""
        if not trajectories:
            return {}

        analyses = [self.analyze_trajectory(traj) for traj in trajectories]

        return {
            "count": len(trajectories),
            "success_rate": sum(1 for traj in trajectories if traj.success)
            / len(trajectories),
            "avg_steps": sum(traj.total_steps for traj in trajectories)
            / len(trajectories),
            "avg_duration": sum(
                traj.duration_seconds for traj in trajectories if traj.duration_seconds
            )
            / len(trajectories),
            "individual_analyses": analyses,
        }

    def generate_report(self, trajectory: Trajectory, format: str = "text") -> str:
        """Generate a human-readable analysis report."""
        analysis = self.analyze_trajectory(trajectory)

        if format == "json":
            return json.dumps(analysis, indent=2, ensure_ascii=False)

        report = []
        report.append("=" * 50)
        report.append("AI AGENT TRAJECTORY ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Task: {analysis['basic_metrics']['task']}")
        report.append(f"Success: {analysis['basic_metrics']['success']}")
        report.append(f"Total Steps: {analysis['basic_metrics']['total_steps']}")
        report.append(
            f"Duration: {analysis['basic_metrics']['duration_seconds']:.2f} seconds"
        )
        report.append("")

        report.append("Step Analysis:")
        report.append(
            f"  Average thought length: {analysis['step_analysis']['avg_thought_length']:.1f} words"
        )
        report.append(
            f"  Average result length: {analysis['step_analysis']['avg_result_length']:.1f} words"
        )
        report.append("  Step type distribution:")
        for action, count in analysis["step_analysis"][
            "step_type_distribution"
        ].items():
            report.append(f"    {action}: {count}")
        report.append("")

        report.append("Tool Usage:")
        for tool, count in analysis["tool_usage"]["tool_usage_count"].items():
            success_rate = (
                analysis["tool_usage"]["tool_success_rates"].get(tool, 0) * 100
            )
            report.append(f"  {tool}: {count} uses ({success_rate:.1f}% success)")
        report.append("")

        report.append("Efficiency Metrics:")
        report.append(
            f"  Average step time: {analysis['efficiency_metrics']['average_step_time_seconds']:.2f} seconds"
        )
        report.append(
            f"  Steps per minute: {analysis['efficiency_metrics']['steps_per_minute']:.1f}"
        )
        report.append("")

        report.append("=" * 50)

        return "\n".join(report)

    def export_analysis(
        self, trajectory: Trajectory, filepath: str, format: str = "json"
    ):
        """Export analysis to a file."""
        analysis = self.analyze_trajectory(trajectory)

        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
        elif format == "text":
            report = self.generate_report(trajectory, "text")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
