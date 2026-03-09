"""Configuration management for nanoclaw."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class Config:
    """Application configuration."""

    # Model settings
    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 4000
    thinking_budget: int = 2000

    # Tool settings
    bash_timeout: int = 15

    # Memory settings
    memory_file: str = "MEMORY.md"

    # UI settings
    exit_commands: tuple[str, ...] = ("exit", "quit")

    # Logging
    # Set to "DEBUG" to see raw LLM responses, detailed execution flow, and token usage
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
