"""Tool implementations for bash command execution."""

import subprocess
import logging
from typing import Any

from config import Config

logger = logging.getLogger(__name__)


class BashExecutionError(Exception):
    """Raised when bash command execution fails."""
    pass


class ToolBox:
    """Container for all available tools."""

    def __init__(self, config: Config) -> None:
        """
        Initialize the toolbox.

        Args:
            config: Application configuration
        """
        self.config = config
        logger.info("ToolBox initialized")

    def execute_bash(self, command: str) -> str:
        """
        Execute a bash command and return the output.

        Designed for standard commands like ls, grep, cat, etc.
        Supports pipes and redirects via shell=True.

        Args:
            command: The bash command to execute

        Returns:
            Combined stdout and stderr output, or success message if empty

        Raises:
            BashExecutionError: If command times out or fails unexpectedly
        """
        logger.info(f"Executing bash command: {command}")

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.bash_timeout
            )

            # Combine output so AI sees full context
            result = process.stdout + process.stderr
            output = result.strip() if result.strip() else "Success (no output)."

            logger.debug(f"Command completed with output length: {len(output)}")
            return output

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {self.config.bash_timeout} seconds"
            logger.error(error_msg)
            return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            logger.error(error_msg)
            return f"System Error: {str(e)}"


def get_tools_schema() -> list[dict[str, Any]]:
    """
    Get the tool schema definitions for Claude.

    Returns:
        List of tool definitions in Anthropic format
    """
    return [
        {
            "name": "execute_bash",
            "description": (
                "Execute a bash command to interact with the system. "
                "Use this to list files (ls), search text (grep), read files (cat), "
                "check system status, or run any standard shell command."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The complete bash command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    ]
