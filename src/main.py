import typer
from rich.console import Console
from rich.panel import Panel

from ai_agent import ReActEngine, Visualizer, load_config, setup_logging

app = typer.Typer()
console = Console(force_terminal=True)


@app.command()
def run(task: str = typer.Argument(..., help="The task for the AI agent to execute")):
    """Run the AI agent with a specific task."""
    """使用特定任务运行AI代理"""
    console.print(Panel.fit("AI Agent Framework", title="Welcome"))

    config = load_config()

    # Setup logging
    setup_logging(config.get("logging", {}))

    agent = ReActEngine(config=config)

    console.print(f"[bold]Task:[/bold] {task}")
    console.print("[yellow]Starting execution...[/yellow]")

    try:
        result = agent.run(task)
        console.print(Panel.fit(result, title="Result"))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        # Ensure database connections are closed
        try:
            agent.close()
        except Exception as e:
            console.print(
                f"[yellow]Warning: Failed to close database connections: {e}[/yellow]"
            )


@app.command()
def version():
    """Show the version of the AI agent framework."""
    """显示AI代理框架的版本"""
    console.print("[bold]AI Agent Framework v0.1.0[/bold]")


@app.command()
def config():
    """Show the current configuration."""
    """显示当前配置"""
    config = load_config()
    console.print(Panel.fit(str(config), title="Configuration"))


@app.command()
def stats():
    """Show performance statistics from the last execution."""
    """显示上次执行的性能统计信息"""
    config = load_config()

    # Setup logging
    setup_logging(config.get("logging", {}))

    # Initialize database to load persisted stats
    db_path = config.get("database", {}).get("path", "data/ai_agent_metrics.json")
    from ai_agent.database import init_database

    db = init_database(db_path)

    try:
        # Get latest performance stats from database
        performance_stats = db.get_latest_performance_stats()
        if performance_stats:
            visualizer = Visualizer()
            visualizer.show_performance(performance_stats)

            console.print("\n" + "=" * 50)
            console.print("Detailed Cost Breakdown")
            console.print("=" * 50)
            visualizer.show_cost_breakdown(performance_stats)
        else:
            console.print(
                "[yellow]No performance data available in database. Run a task first.[/yellow]"
            )
    except Exception as e:
        console.print(
            f"[red]Error retrieving performance stats from database: {e}[/red]"
        )


@app.command()
def reset_stats():
    """Reset performance statistics."""
    """重置性能统计信息"""
    config = load_config()

    # Setup logging
    setup_logging(config.get("logging", {}))

    agent = ReActEngine(config=config)
    agent.reset_performance_stats()
    console.print("[green]Performance statistics reset successfully[/green]")


def main():
    """Main entry point for the AI Agent CLI."""
    """AI Agent CLI的主入口点"""
    app()


if __name__ == "__main__":
    main()
