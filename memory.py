"""Persistent memory management for cross-session context."""

import os
import logging
from typing import Any

from config import Config

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent storage of facts across sessions using Markdown."""

    def __init__(self, config: Config) -> None:
        """
        Initialize the memory manager.

        Creates memory file if it doesn't exist.

        Args:
            config: Application configuration
        """
        self.filepath = config.memory_file
        self._ensure_memory_file()
        logger.info(f"MemoryManager initialized with file: {self.filepath}")

    def _ensure_memory_file(self) -> None:
        """Create memory file with initial structure if it doesn't exist."""
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                f.write("# Agent Memory\n\n")
            logger.debug(f"Created new memory file: {self.filepath}")

    def load_memory(self) -> list[str]:
        """
        Load all memories from disk.

        Returns:
            List of memory strings (without markdown bullet points)
        """
        with open(self.filepath, "r") as f:
            content = f.read()

        # Extract bullet points (lines starting with "- ")
        memories = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("- "):
                memories.append(stripped[2:])  # Remove "- " prefix

        return memories

    def save_to_memory(self, info: str) -> str:
        """
        Save a piece of information to persistent memory.

        Prevents duplicate entries.

        Args:
            info: The information to remember

        Returns:
            Confirmation message
        """
        memories = self.load_memory()

        # Prevent exact duplicates
        if info in memories:
            logger.debug(f"Duplicate memory rejected: {info}")
            return "I already remember that."

        # Append new memory as bullet point
        with open(self.filepath, "a") as f:
            f.write(f"- {info}\n")

        logger.info(f"Saved to memory: {info}")
        return f"Information remembered: {info}"

    def get_context_string(self) -> str:
        """
        Get formatted memory context for injection into conversation.

        Returns:
            Formatted string with all memories, or empty string if no memories
        """
        memories = self.load_memory()

        if not memories:
            return ""

        memories_text = "\n".join([f"- {item}" for item in memories])
        context = f"\n<memory>\nThings you must remember:\n{memories_text}\n</memory>"

        logger.debug(f"Loaded {len(memories)} memories into context")
        return context


def get_memory_schema() -> dict[str, Any]:
    """
    Get the memory tool schema definition for Claude.

    Returns:
        Tool definition in Anthropic format
    """
    return {
        "name": "save_to_memory",
        "description": (
            "Save important information to persistent memory. "
            "Use this to remember user preferences, facts about their environment, "
            "or anything else that should be recalled in future sessions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "info": {
                    "type": "string",
                    "description": "The information to remember permanently"
                }
            },
            "required": ["info"]
        }
    }
