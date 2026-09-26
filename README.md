# Term-AI: Autonomous Terminal Assistant 🤖⚡

Term-AI is a lightweight, cross-platform command-line assistant built with Python and powered by the Gemini API. It translates plain-English natural language requests into precise terminal commands, provides situational awareness of your host environment, and enforces strict human-in-the-loop safety checks before executing anything on your machine.

---

## ✨ Key Features

- **Situational Awareness**: Automatically captures your OS version, active shell, current working directory, and a snapshot of local files to provide relevant context to the model.
- **Structured JSON Enforcement**: Uses Gemini's native JSON mode to guarantee predictable parsing of commands, explanations, and risk flags.
- **Rich Terminal UI**: Utilizes the `rich` library to render sleek, color-coded proposal panels (Green for safe actions, Red for destructive warnings) and structured tables.
- **Human-in-the-Loop Safety**: Enforces user confirmation (`Confirm.ask` defaulting to `False`) to mitigate risks associated with `shell=True` execution.
- **Autonomous Resilience**: Built-in retry-with-backoff logic to handle transient server-side `503 Service Unavailable` API errors gracefully.
- **Audit Trail & History**: Automatically logs every executed command locally into a `command_history.jsonl` audit file, viewable via the `--history` flag.

---

## 🛠️ Tech Stack

- **Language**: Python 3.12+
- **API Client**: `requests` (communicating with `gemini-3.8-flash`)
- **Terminal UI**: `rich`
- **Execution & System Context**: Built-in `subprocess`, `platform`, and `os` libraries.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/algozeb/term-ai.git](https://github.com/algozeb/term-ai.git)
   cd term-ai