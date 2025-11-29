"""
Groq Provider - External API integration
Impure: makes network calls, handles I/O
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional

from ..provider import Provider, LLMResponse
from ..utils import build_tool_schema


class GroqProvider(Provider):
    """
    Groq API implementation - handles I/O boundary.

    Impure operations isolated here:
    - Network calls (requests.post)
    - Environment variables (os.getenv)
    - API key management
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    # Model costs (per 1M tokens)
    COSTS = {
        "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
        "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        "llama-4-scout": {"input": 0.11, "output": 0.34},
    }

    def __init__(self, model: str = "llama-3.1-8b-instant", system_instruction: str = None):
        """Initialize with model and optional system instruction."""
        self.model = model
        self.api_key = self._get_api_key()
        self.system_message = self._create_system_message(system_instruction)

    def chat(self, messages: List[Dict], tools: List = None) -> LLMResponse:
        """Call Groq API - impure I/O operation."""
        payload = self._build_payload(messages, tools)
        response = self._call_api(payload)
        return self._parse_response(response)

    def get_cost(self, usage: Dict) -> float:
        """Calculate cost - pure calculation."""
        if not usage or self.model not in self.COSTS:
            return 0.0

        costs = self.COSTS[self.model]
        input_cost = self._calculate_token_cost(usage.get("prompt_tokens", 0), costs["input"])
        output_cost = self._calculate_token_cost(usage.get("completion_tokens", 0), costs["output"])
        return input_cost + output_cost

    # ========================================================================
    # Private Helpers (3-7 lines each)
    # ========================================================================

    def _get_api_key(self) -> str:
        """Get API key from environment - impure."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable required")
        return api_key

    def _create_system_message(self, instruction: Optional[str]) -> Optional[Dict]:
        """Create system message if instruction provided."""
        if not instruction:
            return None
        return {"role": "system", "content": instruction}

    def _build_payload(self, messages: List[Dict], tools: List) -> Dict:
        """Build API request payload."""
        full_messages = self._add_system_message(messages)
        payload = {"model": self.model, "messages": full_messages}

        if tools:
            payload["tools"] = self._format_tools(tools)

        return payload

    def _add_system_message(self, messages: List[Dict]) -> List[Dict]:
        """Prepend system message if exists."""
        if self.system_message:
            return [self.system_message] + messages
        return messages

    def _format_tools(self, tools: List) -> List[Dict]:
        """Convert tool functions to OpenAI schema."""
        return [build_tool_schema(tool) for tool in tools]

    def _call_api(self, payload: Dict) -> Dict:
        """Make HTTP request to Groq - impure I/O."""
        response = requests.post(
            self.API_URL,
            headers=self._build_headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _parse_response(self, data: Dict) -> LLMResponse:
        """Parse API response into domain object."""
        message = data["choices"][0]["message"]
        return LLMResponse(
            text=message.get("content", ""),
            tool_calls=message.get("tool_calls"),
            usage=data.get("usage"),
        )

    def _calculate_token_cost(self, tokens: int, cost_per_million: float) -> float:
        """Calculate cost for token count - pure calculation."""
        return (tokens / 1_000_000) * cost_per_million
