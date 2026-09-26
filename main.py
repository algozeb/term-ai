import os
import platform
import subprocess
import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

def get_system_context():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "shell": os.environ.get("SHELL", "cmd/powershell"),
        "cwd": os.getcwd()
    }

def get_command_from_gemini(user_prompt):
    raw_key = os.environ.get("GEMINI_API_KEY")
    if not raw_key:
        console.print("[red]Error: GEMINI_API_KEY not found in environment variables.[/red]")
        return None
        
    # Purge any hidden newlines, carriage returns, or spaces trapped in the middle of the string
    api_key = raw_key.replace("\n", "").replace("\r", "").replace(" ", "").strip()

    # The current active model endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    ctx = get_system_context()
    
    system_instruction = f"""
    You are an autonomous CLI assistant.
    Target System: {ctx['os']} ({ctx['os_version']})
    Shell: {ctx['shell']}
    Directory: {ctx['cwd']}

    Convert user request into a terminal command.
    Return ONLY a raw JSON object matching this schema without markdown block formatting:
    {{
      "command": "the exact shell command",
      "explanation": "brief 1-sentence explanation",
      "is_destructive": true/false
    }}
    """

    payload = {
        "contents": [{"parts": [{"text": f"{system_instruction}\nUser Request: {user_prompt}"}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        text_response = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_response)
    except Exception as e:
        console.print(f"[red]API Error:[/red] {e}")
        return None

def main():
    console.print("[bold cyan]Autonomous Terminal Assistant Initialized[/bold cyan]")
    user_input = console.input("[bold yellow]What do you want to do? [/bold yellow]")
    
    if not user_input.strip():
        return

    with console.status("[bold green]Generating command...[/bold green]"):
        result = get_command_from_gemini(user_input)

    if not result:
        return

    border_style = "bold red" if result.get("is_destructive") else "bold green"
    warning = "\n[bold red]WARNING: This command may modify or delete files![/bold red]" if result.get("is_destructive") else ""
    
    panel_content = f"[bold white]Command:[/bold white] {result['command']}\n\n[dim]{result['explanation']}[/dim]{warning}"
    console.print(Panel(panel_content, title="Proposed Action", border_style=border_style))

    if Confirm.ask("Execute this command?"):
        try:
            output = subprocess.run(result["command"], shell=True, capture_output=True, text=True)
            if output.stdout:
                console.print(f"[dim]{output.stdout}[/dim]")
            if output.stderr:
                console.print(f"[red]{output.stderr}[/red]")
        except Exception as e:
            console.print(f"[red]Execution failed:[/red] {e}")
    else:
        console.print("[yellow]Execution cancelled.[/yellow]")

if __name__ == "__main__":
    main()