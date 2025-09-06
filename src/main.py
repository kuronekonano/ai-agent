import typer
from rich.console import Console
from rich.panel import Panel

from ai_agent import ReActEngine, load_config

app = typer.Typer()
console = Console()


@app.command()
def run(task: str = typer.Argument(..., help="The task for the AI agent to execute")):
    """Run the AI agent with a specific task."""
    console.print(Panel.fit("🤖 AI Agent Framework", title="Welcome"))

    config = load_config()
    agent = ReActEngine(config=config)

    console.print(f"[bold]Task:[/bold] {task}")
    console.print("[yellow]Starting execution...[/yellow]")

    try:
        result = agent.run(task)
        console.print(Panel.fit(result, title="Result"))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show the version of the AI agent framework."""
    console.print("[bold]AI Agent Framework v0.1.0[/bold]")


@app.command()
def config():
    """Show the current configuration."""
    config = load_config()
    console.print(Panel.fit(str(config), title="Configuration"))


def main():
    """Main entry point for the AI Agent CLI."""
    app()


if __name__ == "__main__":
    main()
