import json
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from .analyzer import Analyzer
from .logger import get_logger
from .performance import PerformanceTracker
from .trajectory import Trajectory, TrajectoryStep

logger = get_logger(__name__)


class Visualizer:
    """Visualization module for AI agent trajectories and results."""

    """AI代理轨迹和结果的可视化模块"""

    def __init__(self):
        self.console = Console()  # 控制台输出
        self.analyzer = Analyzer()  # 分析器

    def show_trajectory(self, trajectory: Trajectory, detailed: bool = False):
        """Display the execution trajectory in a visual format."""
        """以可视化格式显示执行轨迹"""
        self.console.print(Panel.fit("🤖 Execution Trajectory", style="bold blue"))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Step", style="dim", width=6)
        table.add_column("Action", width=15)
        table.add_column("Result Preview", width=50)

        for step in trajectory.steps:
            result_preview = (
                step.result[:47] + "..." if len(step.result) > 50 else step.result
            )
            table.add_row(str(step.step_number), step.action, result_preview)

        self.console.print(table)

        if detailed:
            self._show_detailed_trajectory(trajectory)

    def _show_detailed_trajectory(self, trajectory: Trajectory):
        """Show detailed view of each step."""
        """显示每个步骤的详细视图"""
        self.console.print("\n" + "=" * 60)
        self.console.print("📋 Detailed Step Analysis")
        self.console.print("=" * 60)

        for step in trajectory.steps:
            self.console.print(f"\n[bold]Step {step.step_number}: {step.action}[/bold]")
            self.console.print(f"[dim]Timestamp: {step.timestamp}[/dim]")

            self.console.print("\n💭 Thought:")
            self.console.print(Markdown(step.thought))

            if step.action_input:
                self.console.print("\n⚙️ Action Input:")
                self.console.print(
                    Syntax(json.dumps(step.action_input, indent=2), "json")
                )

            self.console.print("\n👀 Observation:")
            self.console.print(Markdown(step.observation))

            self.console.print("\n✅ Result:")
            self.console.print(Markdown(step.result))

            self.console.print("-" * 40)

    def show_analysis(self, trajectory: Trajectory):
        """Display analysis of the trajectory."""
        """显示轨迹的分析结果"""
        logger.info("Showing trajectory analysis")
        analysis = self.analyzer.analyze_trajectory(trajectory)

        self.console.print(Panel.fit("Performance Analysis", style="bold green"))

        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value")

        stats_table.add_row("Task", analysis["basic_metrics"]["task"])
        stats_table.add_row(
            "Success", "✅ Yes" if analysis["basic_metrics"]["success"] else "❌ No"
        )
        stats_table.add_row(
            "Total Steps", str(analysis["basic_metrics"]["total_steps"])
        )
        stats_table.add_row(
            "Duration", f"{analysis['basic_metrics']['duration_seconds']:.2f} seconds"
        )
        stats_table.add_row(
            "Avg Step Time",
            f"{analysis['efficiency_metrics']['average_step_time_seconds']:.2f}s",
        )

        self.console.print(stats_table)

        self.console.print("\n🛠️ Tool Usage:")
        tool_table = Table(show_header=True, header_style="bold yellow")
        tool_table.add_column("Tool")
        tool_table.add_column("Uses")
        tool_table.add_column("Success Rate")

        for tool, count in analysis["tool_usage"]["tool_usage_count"].items():
            success_rate = (
                analysis["tool_usage"]["tool_success_rates"].get(tool, 0) * 100
            )
            tool_table.add_row(tool, str(count), f"{success_rate:.1f}%")

        self.console.print(tool_table)
        logger.debug("Analysis visualization completed")

    def show_final_result(self, trajectory: Trajectory):
        """Display the final result in a visually appealing format."""
        """以视觉上吸引人的格式显示最终结果"""
        if not trajectory.final_result:
            self.console.print("[red]No final result available[/red]")
            return

        self.console.print(Panel.fit("🎯 Final Result", style="bold green"))

        if trajectory.success:
            self.console.print(
                "✅ [bold green]Task Completed Successfully![/bold green]"
            )
        else:
            self.console.print("❌ [bold red]Task Failed[/bold red]")

        self.console.print("\n" + "=" * 60)
        self.console.print(Markdown(trajectory.final_result))
        self.console.print("=" * 60)

        self.console.print(
            f"\n[dim]Generated in {trajectory.total_steps} steps over {trajectory.duration_seconds:.2f} seconds[/dim]"
        )

    def show_progress(self, current_step: int, total_steps: int, current_action: str):
        """Show real-time progress during execution."""
        """在执行过程中显示实时进度"""
        with Progress() as progress:
            task = progress.add_task("[cyan]Executing...", total=total_steps)
            progress.update(
                task, completed=current_step, description=f"[cyan]{current_action}"
            )

    def create_timeline(self, trajectory: Trajectory):
        """Create a visual timeline of the execution."""
        """创建执行的可视化时间线"""
        tree = Tree("📅 Execution Timeline", guide_style="bold blue")

        for step in trajectory.steps:
            step_branch = tree.add(f"Step {step.step_number}: {step.action}")
            step_branch.add(
                f"💭 {step.thought[:50]}..."
                if len(step.thought) > 50
                else f"💭 {step.thought}"
            )
            step_branch.add(
                f"✅ {step.result[:50]}..."
                if len(step.result) > 50
                else f"✅ {step.result}"
            )

        self.console.print(tree)

    def export_visualization(self, trajectory: Trajectory, format: str = "text"):
        """Export visualization to different formats."""
        """将可视化导出为不同格式"""
        if format == "text":
            return self._export_text_visualization(trajectory)
        elif format == "html":
            return self._export_html_visualization(trajectory)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_text_visualization(self, trajectory: Trajectory) -> str:
        """Export visualization as plain text."""
        """将可视化导出为纯文本"""
        output = []
        output.append("=" * 60)
        output.append("AI Agent Execution Report")
        output.append("=" * 60)
        output.append(f"Task: {trajectory.task}")
        output.append(f"Success: {trajectory.success}")
        output.append(f"Steps: {trajectory.total_steps}")
        output.append(f"Duration: {trajectory.duration_seconds:.2f} seconds")
        output.append("")

        output.append("Execution Steps:")
        output.append("-" * 40)
        for step in trajectory.steps:
            output.append(f"Step {step.step_number}: {step.action}")
            output.append(f"  Thought: {step.thought}")
            output.append(f"  Result: {step.result}")
            output.append("")

        output.append("Final Result:")
        output.append("-" * 40)
        output.append(trajectory.final_result or "No result")

        return "\n".join(output)

    def show_performance(self, performance_stats: Dict[str, Any]):
        """Display performance statistics in a visual format."""
        """以可视化格式显示性能统计信息"""
        if not performance_stats:
            self.console.print("[red]No performance data available[/red]")
            return

        self.console.print(Panel.fit("Performance Dashboard", style="bold green"))

        # Cost Summary
        cost_table = Table(show_header=True, header_style="bold yellow")
        cost_table.add_column("Metric")
        cost_table.add_column("Value", justify="right")

        cost_table.add_row(
            "Total Cost", f"${performance_stats['cost_summary']['total_cost']:.4f}"
        )
        cost_table.add_row(
            "Input Cost", f"${performance_stats['cost_summary']['input_cost']:.4f}"
        )
        cost_table.add_row(
            "Output Cost", f"${performance_stats['cost_summary']['output_cost']:.4f}"
        )

        self.console.print(cost_table)

        # Token Usage
        token_table = Table(show_header=True, header_style="bold blue")
        token_table.add_column("Token Type")
        token_table.add_column("Count", justify="right")

        token_table.add_row(
            "Total Tokens",
            f"{performance_stats['total_token_usage']['total_tokens']:,}",
        )
        token_table.add_row(
            "Prompt Tokens",
            f"{performance_stats['total_token_usage']['prompt_tokens']:,}",
        )
        token_table.add_row(
            "Completion Tokens",
            f"{performance_stats['total_token_usage']['completion_tokens']:,}",
        )

        self.console.print(token_table)

        # API Call Statistics
        api_table = Table(show_header=True, header_style="bold magenta")
        api_table.add_column("Statistic")
        api_table.add_column("Value", justify="right")

        api_table.add_row("Total API Calls", str(performance_stats["total_api_calls"]))
        api_table.add_row(
            "Successful Calls", str(performance_stats["successful_calls"])
        )
        api_table.add_row("Failed Calls", str(performance_stats["failed_calls"]))
        api_table.add_row("Success Rate", f"{performance_stats['success_rate']:.1%}")
        api_table.add_row(
            "Avg Duration", f"{performance_stats['average_duration_ms']:.2f}ms"
        )

        self.console.print(api_table)

        # Provider Breakdown
        if performance_stats["provider_statistics"]:
            self.console.print("\n🏢 Provider Breakdown:")
            provider_table = Table(show_header=True, header_style="bold cyan")
            provider_table.add_column("Provider/Model")
            provider_table.add_column("Calls", justify="right")
            provider_table.add_column("Tokens", justify="right")
            provider_table.add_column("Duration", justify="right")

            for provider_model, stats in performance_stats[
                "provider_statistics"
            ].items():
                provider_table.add_row(
                    provider_model,
                    str(stats["calls"]),
                    f"{stats['total_tokens']:,}",
                    f"{stats['duration_ms']:.0f}ms",
                )

            self.console.print(provider_table)

        logger.debug("Performance visualization completed")

    def show_cost_breakdown(self, performance_stats: Dict[str, Any]):
        """Display detailed cost breakdown."""
        """显示详细的成本分解"""
        if not performance_stats:
            self.console.print("[red]No performance data available[/red]")
            return

        self.console.print(Panel.fit("Detailed Cost Breakdown", style="bold yellow"))

        # Calculate costs per provider
        cost_tracker = PerformanceTracker()
        provider_costs = []

        for provider_model, stats in performance_stats["provider_statistics"].items():
            provider, model = provider_model.split("/")
            cost = cost_tracker.calculate_cost(
                provider,
                model,
                PerformanceTracker.TokenUsage(
                    prompt_tokens=stats["prompt_tokens"],
                    completion_tokens=stats["completion_tokens"],
                    total_tokens=stats["total_tokens"],
                ),
            )
            provider_costs.append(
                {
                    "provider_model": provider_model,
                    "cost": cost.total_cost,
                    "calls": stats["calls"],
                    "tokens": stats["total_tokens"],
                }
            )

        # Sort by cost descending
        provider_costs.sort(key=lambda x: x["cost"], reverse=True)

        cost_table = Table(show_header=True, header_style="bold green")
        cost_table.add_column("Provider/Model")
        cost_table.add_column("Cost", justify="right")
        cost_table.add_column("Calls", justify="right")
        cost_table.add_column("Tokens", justify="right")
        cost_table.add_column("Cost/Call", justify="right")

        for item in provider_costs:
            cost_per_call = item["cost"] / item["calls"] if item["calls"] > 0 else 0
            cost_table.add_row(
                item["provider_model"],
                f"${item['cost']:.4f}",
                str(item["calls"]),
                f"{item['tokens']:,}",
                f"${cost_per_call:.6f}",
            )

        self.console.print(cost_table)

        # Efficiency metrics
        total_tokens = performance_stats["total_token_usage"]["total_tokens"]
        total_cost = performance_stats["cost_summary"]["total_cost"]
        total_calls = performance_stats["total_api_calls"]

        efficiency_table = Table(show_header=True, header_style="bold blue")
        efficiency_table.add_column("Efficiency Metric")
        efficiency_table.add_column("Value", justify="right")

        efficiency_table.add_row(
            "Cost per Token",
            f"${total_cost / total_tokens:.8f}" if total_tokens > 0 else "N/A",
        )
        efficiency_table.add_row(
            "Tokens per Call",
            f"{total_tokens / total_calls:.1f}" if total_calls > 0 else "N/A",
        )
        efficiency_table.add_row(
            "Cost per Call",
            f"${total_cost / total_calls:.6f}" if total_calls > 0 else "N/A",
        )

        self.console.print(efficiency_table)

    def _export_html_visualization(self, trajectory: Trajectory) -> str:
        """Export visualization as HTML (basic implementation)."""
        """将可视化导出为HTML（基本实现）"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Execution Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .step {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Agent Execution Report</h1>
        <p><strong>Task:</strong> {trajectory.task}</p>
        <p><strong>Status:</strong> <span class="{'success' if trajectory.success else 'failure'}">
            {'Success' if trajectory.success else 'Failure'}
        </span></p>
        <p><strong>Steps:</strong> {trajectory.total_steps}</p>
        <p><strong>Duration:</strong> {trajectory.duration_seconds:.2f} seconds</p>
    </div>
    
    <h2>Execution Steps</h2>
    {"\n".join(self._format_step_html(step) for step in trajectory.steps)}
    
    <h2>Final Result</h2>
    <div class="step">
        <pre>{trajectory.final_result or 'No result'}</pre>
    </div>
</body>
</html>
"""
        return html

    def _format_step_html(self, step: TrajectoryStep) -> str:
        """Format a single step for HTML export."""
        """为HTML导出格式化单个步骤"""
        return f"""
<div class="step">
    <h3>Step {step.step_number}: {step.action}</h3>
    <p><strong>Thought:</strong> {step.thought}</p>
    <p><strong>Result:</strong> {step.result}</p>
    <p><em>Timestamp: {step.timestamp}</em></p>
</div>
"""
