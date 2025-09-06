#!/usr/bin/env python3
"""
Demo script for the AI Agent Framework.
This script demonstrates basic functionality without requiring Jupyter.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from src.ai_agent import ReActEngine, load_config, Visualizer
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Run the demo."""
    console.print(Panel.fit("🤖 AI Agent Framework - Demo", style="bold blue"))
    
    try:
        # Load configuration
        console.print("[yellow]Loading configuration...[/yellow]")
        config = load_config()
        console.print("[green]Configuration loaded successfully![/green]")
        
        # Initialize agent
        console.print("[yellow]Initializing AI agent...[/yellow]")
        agent = ReActEngine(config)
        console.print(f"[green]Agent initialized with tools: {agent.tool_registry.get_available_tools()}[/green]")
        
        # Define demo tasks
        demo_tasks = [
            "Calculate the sum of the first 5 prime numbers",
            "Find the square root of 169 and save it to a file called result.txt",
            "Create a file with the multiplication table for 7"
        ]
        
        for i, task in enumerate(demo_tasks, 1):
            console.print(f"\n[bold]Task {i}:[/bold] {task}")
            console.print("[yellow]Executing...[/yellow]")
            
            # Execute task
            result = agent.run(task)
            
            # Get trajectory
            trajectory = agent.get_trajectory()
            
            # Show results
            visualizer = Visualizer()
            visualizer.show_trajectory(trajectory)
            
            console.print(f"[green]Result:[/green] {result}")
            console.print(f"[dim]Completed in {trajectory.total_steps} steps, {trajectory.duration_seconds:.2f} seconds[/dim]")
            
            # Reset agent for next task
            agent.reset()
        
        console.print("\n" + "="*60)
        console.print("[bold green]✅ All demo tasks completed successfully![/bold green]")
        console.print("="*60)
        
        console.print("\nTo explore further:")
        console.print("1. Run the Jupyter notebook: jupyter notebook notebooks/demo_analysis.ipynb")
        console.print("2. Use the CLI: python -m ai_agent run 'Your task here'")
        console.print("3. Check the tests: python -m pytest tests/")
        
    except Exception as e:
        console.print(f"[red]Error during demo: {e}[/red]")
        console.print("\nMake sure you:")
        console.print("1. Have set up your API keys in config/config.yaml")
        console.print("2. Installed all dependencies: pip install -e .")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())