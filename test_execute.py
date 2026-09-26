import os
import subprocess
from rich.console import Console
from test_context import get_context
from test_generate import generate_command
from test_render import render_and_confirm

console = Console()

def execute_command(command_str):
    """Executes the approved shell command with a 20-second timeout and output capture."""
    console.print(f"[dim]Executing: {command_str}[/dim]\n")
    
    try:
        # Run subprocess with shell=True, capturing text output, with a 20s timeout
        result = subprocess.run(
            command_str,
            shell=True,
            capture_output=True,
            text=True,
            timeout=20
        )
        
        # Print Standard Output if present
        if result.stdout:
            console.print("[bold green]Output:[/bold green]")
            console.print(result.stdout.strip())
            
        # Print Standard Error if present
        if result.stderr:
            console.print("[bold red]Errors/Warnings:[/bold red]")
            console.print(result.stderr.strip())
            
        console.print(f"\n[dim]Process exited with code: {result.returncode}[/dim]")
        
    except subprocess.TimeoutExpired:
        console.print("[bold red]Error: Command execution timed out after 20 seconds.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Execution failed:[/bold red] {e}")

if __name__ == "__main__":
    ctx = get_context()
    
    # Test prompt that generates safe terminal output
    prompt = "show all files in this directory"
    console.print(f"User Request: [yellow]{prompt}[/yellow]")
    
    # Step 3: Generate
    result = generate_command(prompt, ctx)
    if result:
        # Step 4: Render & Confirm
        approved = render_and_confirm(result)
        if approved:
            # Step 5: Execute
            execute_command(result["command"])
        else:
            console.print("[yellow]Execution cancelled by user.[/yellow]")