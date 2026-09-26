import os
import json
import sys
import time
import platform
import subprocess
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

console = Console()
HISTORY_FILE = "command_history.jsonl"

def get_context():
    """Gathers OS, shell, cwd, and a safe short directory listing."""
    try:
        items = os.listdir(os.getcwd())
        dir_listing = ", ".join(items[:10])
        if len(items) > 10:
            dir_listing += " (and more...)"
    except Exception as e:
        dir_listing = f"Error reading directory: {e}"

    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "shell": os.environ.get("SHELL", os.environ.get("ComSpec", "unknown")),
        "cwd": os.getcwd(),
        "directory_listing": dir_listing
    }

def generate_command(user_prompt, context):
    """Sends prompt + context to Gemini with 503 retry logic and returns parsed JSON."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("[red]Error: GEMINI_API_KEY environment variable is missing.[/red]")
        return None

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key.strip()}
    
    system_instruction = f"""
    You are an autonomous CLI assistant.
    Target System: {context['os']} ({context['os_release']})
    Shell: {context['shell']}
    Directory: {context['cwd']}
    Local Files Snapshot: {context['directory_listing']}

    Convert the user request into a terminal command matching this exact JSON schema:
    {{
      "command": "the exact shell command to run",
      "summary": "a brief 1-sentence explanation",
      "destructive": true or false,
      "notes": "any relevant caveats or empty string"
    }}
    """

    payload = {
        "contents": [{"parts": [{"text": f"{system_instruction}\nUser Request: {user_prompt}"}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    for attempt in range(1, 4):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 503:
                console.print(f"[yellow]Server busy (503). Retrying attempt {attempt}/3...[/yellow]")
                time.sleep(3)
                continue
            response.raise_for_status()
            
            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)
        except Exception as e:
            console.print(f"[red]Generation error: {e}[/red]")
            break
    return None

def log_history(prompt, command, status):
    """Appends executed command details to a local JSONL log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "command": command,
        "status": status
    }
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def display_history():
    """Reads the JSONL history log and renders it in a Rich table."""
    if not os.path.exists(HISTORY_FILE):
        console.print("[yellow]No command history found yet.[/yellow]")
        return

    table = Table(title="Term-AI Execution History", border_style="cyan")
    table.add_column("Timestamp", style="dim", width=20)
    table.add_column("User Prompt", style="yellow", width=30)
    table.add_column("Command", style="green", width=30)
    table.add_column("Status", style="bold", width=12)

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    status_style = "green" if entry["status"] == "success" else "red"
                    table.add_row(
                        entry["timestamp"][:19].replace("T", " "),
                        entry["prompt"],
                        entry["command"],
                        f"[{status_style}]{entry['status']}[/{status_style}]"
                    )
                except json.JSONDecodeError:
                    continue

    console.print(table)

def main():
    # Handle CLI flags like --history
    if len(sys.argv) > 1 and sys.argv[1] == "--history":
        display_history()
        return

    console.print(Panel("[bold cyan]Term-AI: Autonomous Terminal Assistant[/bold cyan]", border_style="cyan"))
    user_prompt = console.input("[bold yellow]What do you want to do? [/bold yellow]")
    
    if not user_prompt.strip():
        return

    with console.status("[bold green]Analyzing request and context...[/bold green]"):
        ctx = get_context()
        result = generate_command(user_prompt, ctx)

    if not result:
        return

    is_destructive = result.get("destructive", False)
    border_style = "bold red" if is_destructive else "bold green"
    title = "[bold red]⚠️ DESTRUCTIVE ACTION WARNING[/bold red]" if is_destructive else "[bold green]Proposed Action[/bold green]"
    
    panel_content = (
        f"[bold white]Command:[/bold white] {result['command']}\n\n"
        f"[dim]Summary:[/dim] {result['summary']}\n"
        f"[dim]Notes:[/dim] {result.get('notes', 'None')}"
    )
    console.print(Panel(panel_content, title=title, border_style=border_style, expand=False))

    if Confirm.ask("Do you want to execute this command?", default=False):
        console.print(f"[dim]Running: {result['command']}[/dim]\n")
        try:
            res = subprocess.run(result["command"], shell=True, capture_output=True, text=True, timeout=20)
            if res.stdout:
                console.print(res.stdout.strip())
            if res.stderr:
                console.print(f"[red]{res.stderr.strip()}[/red]")
            
            log_history(user_prompt, result["command"], "success" if res.returncode == 0 else "error")
        except Exception as e:
            console.print(f"[red]Execution failed: {e}[/red]")
            log_history(user_prompt, result["command"], "failed")
    else:
        console.print("[yellow]Execution cancelled.[/yellow]")
        log_history(user_prompt, result["command"], "cancelled")

if __name__ == "__main__":
    main()