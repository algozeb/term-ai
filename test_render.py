import os
import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from test_context import get_context
from test_generate import generate_command

console = Console()

def render_and_confirm(result):
    """Renders the command proposal in a Rich Panel and prompts for confirmation."""
    if not result:
        console.print("[red]No command result available to render.[/red]")
        return False

    is_destructive = result.get("destructive", False)
    
    # Dynamic styling: Red for destructive, Green for safe
    border_style = "bold red" if is_destructive else "bold green"
    title = "[bold red]⚠️ DESTRUCTIVE ACTION WARNING[/bold red]" if is_destructive else "[bold green]Proposed Action (Safe)[/bold green]"
    
    # Build the content block inside the panel
    panel_content = (
        f"[bold white]Command:[/bold white] {result['command']}\n\n"
        f"[dim]Summary:[/dim] {result['summary']}\n"
        f"[dim]Notes:[/dim] {result.get('notes', 'None')}"
    )
    
    # Render the Panel
    console.print(Panel(panel_content, title=title, border_style=border_style, expand=False))
    
    # Optional: Display a small Table for structured metadata breakdown
    meta_table = Table(show_header=False, box=None, padding=(0, 2))
    meta_table.add_row("[cyan]Risk Level:[/cyan]", "[red]High (Destructive)[/red]" if is_destructive else "[green]Low (Safe)[/green]")
    console.print(meta_table)
    console.print()

    # Secure confirmation prompt using Rich
    return Confirm.ask("Do you want to execute this command?", default=False)

if __name__ == "__main__":
    ctx = get_context()
    
    # Test with a safe prompt first
    prompt = "show all files in this directory"
    console.print(f"User Request: [yellow]{prompt}[/yellow]")
    
    result = generate_command(prompt, ctx)
    if result:
        approved = render_and_confirm(result)
        if approved:
            console.print("[green]Command approved! (Execution logic coming in Step 5)[/green]")
        else:
            console.print("[yellow]Command cancelled by user.[/yellow]")