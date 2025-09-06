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
from .trajectory import Trajectory, TrajectoryStep


class Visualizer:
    """Visualization module for AI agent trajectories and results."""

    def __init__(self):
        self.console = Console()
        self.analyzer = Analyzer()

    def show_trajectory(self, trajectory: Trajectory, detailed: bool = False):
        """Display the execution trajectory in a visual format."""
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
        analysis = self.analyzer.analyze_trajectory(trajectory)

        self.console.print(Panel.fit("📊 Performance Analysis", style="bold green"))

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

    def show_final_result(self, trajectory: Trajectory):
        """Display the final result in a visually appealing format."""
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
        with Progress() as progress:
            task = progress.add_task("[cyan]Executing...", total=total_steps)
            progress.update(
                task, completed=current_step, description=f"[cyan]{current_action}"
            )

    def create_timeline(self, trajectory: Trajectory):
        """Create a visual timeline of the execution."""
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
        if format == "text":
            return self._export_text_visualization(trajectory)
        elif format == "html":
            return self._export_html_visualization(trajectory)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_text_visualization(self, trajectory: Trajectory) -> str:
        """Export visualization as plain text."""
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

    def _export_html_visualization(self, trajectory: Trajectory) -> str:
        """Export visualization as HTML (basic implementation)."""
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
        return f"""
<div class="step">
    <h3>Step {step.step_number}: {step.action}</h3>
    <p><strong>Thought:</strong> {step.thought}</p>
    <p><strong>Result:</strong> {step.result}</p>
    <p><em>Timestamp: {step.timestamp}</em></p>
</div>
"""
