"""nanoClaw: A minimal AI agent for educational purposes."""

import os
import logging
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from anthropic.types import ContentBlock

from config import Config
from engine import ClaudeEngine
from tools import ToolBox, get_tools_schema
from memory import MemoryManager, get_memory_schema

# Load environment variables
load_dotenv()

# Initialize console for rich output
console = Console()


def setup_logging(config: Config) -> None:
    """
    Configure logging for the application.

    Set log_level to DEBUG in config.py to see:
    - Detailed execution flow
    - Raw LLM responses and content blocks
    - Token usage statistics
    - Memory operations
    """
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def print_block(block: ContentBlock) -> None:
    """
    Print a content block from Claude with rich formatting.

    Args:
        block: Content block from Claude's response (thinking, tool_use, or text)
    """
    if block.type == "thinking":
        console.print(f"\n[dim cyan]💭 THOUGHT:[/dim cyan] [dim]{block.thinking}[/dim]")
    elif block.type == "tool_use":
        console.print(f"\n[yellow]🔧 ACTION:[/yellow] [bold]{block.name}[/bold]({block.input})")
    elif block.type == "text":
        console.print(f"\n[green]🤖 CLAUDE:[/green] {block.text}")


def create_tool_result_message(tool_use_id: str, result: str) -> dict[str, Any]:
    """
    Create a properly formatted tool result message.

    Args:
        tool_use_id: ID of the tool use block
        result: Result of the tool execution

    Returns:
        Message dict in Anthropic format
    """
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": result
            }
        ]
    }


def execute_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    tools: ToolBox,
    memory: MemoryManager
) -> str:
    """
    Execute a tool and return its result.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool
        tools: ToolBox instance
        memory: MemoryManager instance

    Returns:
        Result of tool execution as a string
    """
    if tool_name == "execute_bash":
        return tools.execute_bash(tool_input["command"])
    elif tool_name == "save_to_memory":
        return memory.save_to_memory(tool_input["info"])
    else:
        return f"Error: Unknown tool '{tool_name}'"


def process_assistant_response(response: Any) -> tuple[list[dict[str, Any]], ContentBlock | None]:
    """
    Process Claude's response and extract content blocks.

    Args:
        response: Response from Claude API

    Returns:
        Tuple of (assistant_content list, tool_use_block if present)
    """
    assistant_content = []
    tool_use_block = None

    for block in response.content:
        print_block(block)

        if block.type == "thinking":
            assistant_content.append({
                "type": "thinking",
                "thinking": block.thinking,
                "signature": block.signature
            })
        elif block.type == "tool_use":
            tool_use_block = block
            assistant_content.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input
            })
        elif block.type == "text":
            assistant_content.append({"type": "text", "text": block.text})

    return assistant_content, tool_use_block


def initialize_conversation(memory: MemoryManager) -> list[dict[str, Any]]:
    """
    Initialize conversation with memory context.

    Args:
        memory: MemoryManager instance

    Returns:
        Initial messages list with memory context
    """
    mem_context = memory.get_context_string()
    init_message = (
        f"System Initialization: {mem_context}\n"
        "Please acknowledge what you remember and wait for my command."
    )

    return [{"role": "user", "content": init_message}]


def main_loop() -> None:
    """Main conversation loop for nanoClaw."""
    # Initialize configuration
    config = Config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # Initialize components
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not found in environment[/red]")
        return

    engine = ClaudeEngine(api_key=api_key, config=config)
    tools = ToolBox(config=config)
    memory = MemoryManager(config=config)

    # Combine tool schemas
    all_tools = get_tools_schema() + [get_memory_schema()]

    # Initialize conversation with memory
    messages = initialize_conversation(memory)

    # Display welcome message
    console.print(Panel.fit(
        "[bold cyan]nanoClaw[/bold cyan]\n"
        "A minimal AI agent with tools and memory\n\n"
        f"Type your message and press Enter.\n"
        f"Type '[red]{config.exit_commands[0]}[/red]' or press [red]Ctrl+C[/red] to quit.",
        border_style="cyan"
    ))

    # Main interaction loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting. Goodbye![/yellow]")
            break

        if user_input.strip().lower() in config.exit_commands:
            console.print("[yellow]Exiting. Goodbye![/yellow]")
            break

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        # Agentic loop: think → act → observe → repeat
        while True:
            response = engine.get_response(messages, all_tools)

            # Process response
            assistant_content, tool_use_block = process_assistant_response(response)

            # Save assistant's response to history
            messages.append({"role": "assistant", "content": assistant_content})

            # Handle tool execution
            if tool_use_block:
                result = execute_tool(
                    tool_use_block.name,
                    tool_use_block.input,
                    tools,
                    memory
                )

                console.print(f"[magenta]📊 RESULT:[/magenta] {result}")

                # Feed result back to Claude
                messages.append(create_tool_result_message(tool_use_block.id, result))
                continue  # Continue agentic loop

            # No more tools needed - exit inner loop
            break


if __name__ == "__main__":
    main_loop()
