# nanoClaw

A tiny **OpenClaw** for educational purposes. A minimal AI agent that actually *does* things—runs shell commands, remembers across sessions—so you can see how the pieces fit together.

## What it does

- **Chat with Claude** in a colorful CLI with configurable model (defaults to Haiku)
- **Execute bash commands** when the model decides it needs to (e.g. `ls`, `grep`, `cat`)
- **Persistent memory** stored in `MEMORY.md`—the agent remembers facts across sessions
- **Extended Thinking** so you can see the model's reasoning before actions
- **Rich console output** with colors, emojis, and formatted display

## Quick start

```bash
# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate   # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Add your Anthropic API key to a .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run
python main.py
```

Type your message, press Enter. Type `exit` or Ctrl+C to quit.

## Project structure

| File        | Purpose                                      |
|-------------|----------------------------------------------|
| `main.py`   | Main loop: chat, tool execution, message history |
| `engine.py` | Claude API wrapper with Extended Thinking        |
| `tools.py`  | `execute_bash` tool schema and implementation    |
| `memory.py` | `save_to_memory` tool and markdown persistence   |
| `config.py` | Centralized configuration (model, timeouts, etc.) |
| `MEMORY.md` | Stored memories in human-readable markdown     |
| `requirements.txt` | Python dependencies (anthropic, rich, dotenv) |

## How it works

1. Configuration is loaded from `config.py` (model, timeouts, etc.)
2. On startup, the agent loads memories from `MEMORY.md` into the first message
3. You send a message; Claude may think, use tools, or reply
4. If it calls `execute_bash`, the command runs and the output is fed back
5. If it calls `save_to_memory`, the fact is appended to `MEMORY.md`
6. The loop continues until Claude responds with text and no tool use

## Configuration

Edit `config.py` to customize:
- **Model**: Change from Haiku to Sonnet or Opus
- **Token limits**: Adjust `max_tokens` and `thinking_budget`
- **Timeouts**: Set bash command timeout
- **Memory file**: Change storage location
- **Exit commands**: Customize quit commands

## Related

- [OpenClaw](https://github.com/openclaw/openclaw) — full-featured autonomous agent (multi-platform, browser automation, skills, etc.)
- nanoClaw is a stripped-down version to learn the core loop: LLM + tools + memory.
