import os
from anthropic import Anthropic


class ClaudeEngine:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"

    def get_response(self, messages, tools, thinking_budget=2000):
        """
        Sends messages to Claude with Extended Thinking enabled.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget
            },
            tools=tools,
            messages=messages
        )
        
        return response