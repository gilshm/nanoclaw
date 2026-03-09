"""Claude API engine with Extended Thinking support."""

from typing import Any
import logging

from anthropic import Anthropic
from anthropic.types import Message

from config import Config

logger = logging.getLogger(__name__)


class ClaudeEngine:
    """Wrapper for Claude API with Extended Thinking enabled."""

    def __init__(self, api_key: str, config: Config) -> None:
        """
        Initialize the Claude engine.

        Args:
            api_key: Anthropic API key
            config: Application configuration
        """
        self.client = Anthropic(api_key=api_key)
        self.config = config
        logger.info(f"Initialized ClaudeEngine with model: {config.model}")

    def get_response(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]]
    ) -> Message:
        """
        Send messages to Claude and get a response with Extended Thinking.

        Args:
            messages: Conversation history in Anthropic format
            tools: Available tools for Claude to use

        Returns:
            Message response from Claude with thinking, tool use, and/or text
        """
        logger.debug(f"Sending {len(messages)} messages to Claude")

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            thinking={
                "type": "enabled",
                "budget_tokens": self.config.thinking_budget
            },
            tools=tools,
            messages=messages
        )

        logger.debug(f"Received response with {len(response.content)} content blocks")
        return response
