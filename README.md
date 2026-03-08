# nanoclaw

A tiny **OpenClaw** for educational purposes. A minimal AI agent that actually *does* things—runs shell commands, remembers across sessions—so you can see how the pieces fit together.

## What it does

- **Chat with Claude** (Haiku) in a simple CLI loop
- **Execute bash commands** when the model decides it needs to (e.g. `ls`, `grep`, `cat`)
- **Persistent memory** stored in `memory.json`—the agent remembers facts across sessions
- **Extended Thinking** so you can see the model’s reasoning before actions

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
| `engine.py` | Claude API wrapper (Haiku + Extended Thinking)   |
| `tools.py`  | `execute_bash` tool schema and implementation    |
| `memory.py` | `save_to_memory` tool and JSON persistence       |
| `memory.json` | Stored memories (created on first use)        |
| `requirements.txt` | Python dependencies                          |

## How it works

1. On startup, the agent loads memories from `memory.json` into the first message.
2. You send a message; Claude may think, use tools, or reply.
3. If it calls `execute_bash`, the command runs and the output is fed back.
4. If it calls `save_to_memory`, the fact is appended to `memory.json`.
5. The loop continues until Claude responds with text and no tool use.

## Related

- [OpenClaw](https://github.com/openclaw/openclaw) — full-featured autonomous agent (multi-platform, browser automation, skills, etc.)
- nanoclaw is a stripped-down version to learn the core loop: LLM + tools + memory.
