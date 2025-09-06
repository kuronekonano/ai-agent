import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .logger import get_logger
from .performance import PerformanceTracker
from .trajectory import Trajectory, TrajectoryStep

logger = get_logger(__name__)


class Analyzer:
    """Analyzes agent trajectories to extract insights and metrics."""

    """分析代理轨迹以提取洞察和指标"""

    def __init__(self):
        pass

    def analyze_trajectory(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Comprehensive analysis of a trajectory."""
        """对轨迹进行全面分析"""
        if not trajectory:
            logger.warning("Empty trajectory provided for analysis")
            return {}

        logger.info(f"Analyzing trajectory for task: {trajectory.task}")
        analysis = {
            "basic_metrics": self._get_basic_metrics(trajectory),
            "step_analysis": self._analyze_steps(trajectory.steps),
            "tool_usage": self._analyze_tool_usage(trajectory.steps),
            "efficiency_metrics": self._calculate_efficiency_metrics(trajectory),
            "success_analysis": self._analyze_success(trajectory),
        }

        logger.debug(f"Trajectory analysis completed, steps: {trajectory.total_steps}")
        return analysis

    def _get_basic_metrics(self, trajectory: Trajectory) -> Dict[str, Any]:
        """Get basic metrics from the trajectory."""
        """从轨迹中获取基本指标"""
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
        """分析轨迹中的步骤"""
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
        """分析工具使用模式"""
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
        """计算效率指标"""
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
        """分析成功因素"""
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
        """评估结果质量的简单启发式方法"""
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
        """比较多个轨迹"""
        if not trajectories:
            logger.warning("No trajectories provided for comparison")
            return {}

        logger.info(f"Comparing {len(trajectories)} trajectories")
        analyses = [self.analyze_trajectory(traj) for traj in trajectories]

        result = {
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

        logger.debug(
            f"Trajectory comparison completed, success rate: {result['success_rate']:.2f}"
        )
        return result

    def analyze_performance(self, performance_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance statistics including token usage and costs."""
        """分析性能统计信息，包括Token使用情况和成本"""
        if not performance_stats:
            logger.warning("Empty performance stats provided for analysis")
            return {}

        logger.info("Analyzing performance statistics")

        # Calculate efficiency metrics
        total_tokens = performance_stats["total_token_usage"]["total_tokens"]
        total_cost = performance_stats["cost_summary"]["total_cost"]
        total_calls = performance_stats["total_api_calls"]

        efficiency_metrics = {
            "cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0,
            "tokens_per_call": total_tokens / total_calls if total_calls > 0 else 0,
            "cost_per_call": total_cost / total_calls if total_calls > 0 else 0,
            "avg_call_duration_ms": performance_stats["average_duration_ms"],
        }

        # Identify most expensive calls
        expensive_calls = []
        for provider_model, stats in performance_stats["provider_statistics"].items():
            cost = PerformanceTracker().calculate_cost(
                provider_model.split("/")[0],
                provider_model.split("/")[1],
                TokenUsage(
                    prompt_tokens=stats["prompt_tokens"],
                    completion_tokens=stats["completion_tokens"],
                    total_tokens=stats["total_tokens"],
                ),
            )
            expensive_calls.append(
                {
                    "provider_model": provider_model,
                    "cost": cost.total_cost,
                    "calls": stats["calls"],
                    "tokens": stats["total_tokens"],
                }
            )

        # Sort by cost descending
        expensive_calls.sort(key=lambda x: x["cost"], reverse=True)

        analysis = {
            "efficiency_metrics": efficiency_metrics,
            "cost_breakdown": {
                "total_cost": total_cost,
                "input_cost": performance_stats["cost_summary"]["input_cost"],
                "output_cost": performance_stats["cost_summary"]["output_cost"],
                "currency": performance_stats["cost_summary"]["currency"],
            },
            "token_usage": performance_stats["total_token_usage"],
            "api_call_stats": {
                "total_calls": total_calls,
                "success_rate": performance_stats["success_rate"],
                "avg_duration_ms": performance_stats["average_duration_ms"],
            },
            "most_expensive_calls": expensive_calls[:5],  # Top 5 most expensive
            "provider_breakdown": performance_stats["provider_statistics"],
        }

        logger.debug(f"Performance analysis completed, total cost: ${total_cost:.4f}")
        return analysis

    def generate_performance_report(self, performance_stats: Dict[str, Any]) -> str:
        """Generate a human-readable performance report."""
        """生成人类可读的性能报告"""
        analysis = self.analyze_performance(performance_stats)

        report = []
        report.append("=" * 60)
        report.append("AI AGENT PERFORMANCE REPORT")
        report.append("=" * 60)

        # Cost Summary
        report.append("💰 Cost Summary:")
        report.append(f"  Total Cost: ${analysis['cost_breakdown']['total_cost']:.4f}")
        report.append(f"  Input Cost: ${analysis['cost_breakdown']['input_cost']:.4f}")
        report.append(
            f"  Output Cost: ${analysis['cost_breakdown']['output_cost']:.4f}"
        )
        report.append("")

        # Token Usage
        report.append("🔢 Token Usage:")
        report.append(f"  Total Tokens: {analysis['token_usage']['total_tokens']:,}")
        report.append(f"  Prompt Tokens: {analysis['token_usage']['prompt_tokens']:,}")
        report.append(
            f"  Completion Tokens: {analysis['token_usage']['completion_tokens']:,}"
        )
        report.append("")

        # API Call Statistics
        report.append("📞 API Call Statistics:")
        report.append(f"  Total Calls: {analysis['api_call_stats']['total_calls']}")
        report.append(
            f"  Success Rate: {analysis['api_call_stats']['success_rate']:.1%}"
        )
        report.append(
            f"  Avg Call Duration: {analysis['api_call_stats']['avg_duration_ms']:.2f}ms"
        )
        report.append("")

        # Efficiency Metrics
        report.append("⚡ Efficiency Metrics:")
        report.append(
            f"  Cost per Token: ${analysis['efficiency_metrics']['cost_per_token']:.8f}"
        )
        report.append(
            f"  Tokens per Call: {analysis['efficiency_metrics']['tokens_per_call']:.1f}"
        )
        report.append(
            f"  Cost per Call: ${analysis['efficiency_metrics']['cost_per_call']:.6f}"
        )
        report.append("")

        # Most Expensive Calls
        if analysis["most_expensive_calls"]:
            report.append("💸 Most Expensive Calls:")
            for i, call in enumerate(analysis["most_expensive_calls"], 1):
                report.append(
                    f"  {i}. {call['provider_model']}: "
                    f"${call['cost']:.4f} ({call['calls']} calls, {call['tokens']:,} tokens)"
                )

        report.append("=" * 60)

        return "\n".join(report)

    def generate_report(self, trajectory: Trajectory, format: str = "text") -> str:
        """Generate a human-readable analysis report."""
        """生成人类可读的分析报告"""
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
        """将分析导出到文件"""
        logger.info(f"Exporting analysis to {filepath} in {format} format")
        analysis = self.analyze_trajectory(trajectory)

        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.debug("Analysis exported as JSON")
        elif format == "text":
            report = self.generate_report(trajectory, "text")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)
            logger.debug("Analysis exported as text")
        else:
            logger.error(f"Unsupported format: {format}")
            raise ValueError(f"Unsupported format: {format}")
