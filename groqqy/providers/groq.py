"""Groq Provider - LLM API integration"""

import os
import re
import json
import requests
from typing import List, Dict, Any, Optional

from ..provider import Provider, LLMResponse


class GroqProvider(Provider):
    """Groq API implementation with cost tracking."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    COSTS = {
        "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
        "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        "llama-4-scout": {"input": 0.11, "output": 0.34},
    }

    def __init__(self, model: str = "llama-3.1-8b-instant",
                 system_instruction: str = None,
                 temperature: float = 0.5,
                 top_p: float = 0.65,
                 lenient_tool_parsing: bool = True):
        self.model = model
        self.api_key = self._get_api_key()
        self.system_message = self._create_system_message(system_instruction)
        self.temperature = temperature
        self.top_p = top_p
        self.lenient_tool_parsing = lenient_tool_parsing
        self.lenient_parse_count = 0  # Track recovery successes

    def chat(self, messages: List[Dict], tools: List = None) -> LLMResponse:
        payload = self._build_payload(messages, tools)
        response = self._call_api(payload)
        return self._parse_response(response)

    def get_cost(self, usage: Dict) -> float:
        if not usage or self.model not in self.COSTS:
            return 0.0

        costs = self.COSTS[self.model]
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        input_cost = self._calculate_token_cost(prompt_tokens, costs["input"])
        output_cost = self._calculate_token_cost(
            completion_tokens, costs["output"]
        )
        return input_cost + output_cost

    def _get_api_key(self) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable required")
        return api_key

    def _create_system_message(self, instruction: Optional[str]) -> Optional[Dict]:
        if not instruction:
            return None
        return {"role": "system", "content": instruction}

    def _build_payload(self, messages: List[Dict], tools: List) -> Dict:
        full_messages = self._add_system_message(messages)
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": self.temperature,
            "top_p": self.top_p
        }

        if tools:
            payload["tools"] = tools

        return payload

    def _add_system_message(self, messages: List[Dict]) -> List[Dict]:
        if self.system_message:
            return [self.system_message] + messages
        return messages

    def _attempt_lenient_tool_parse(self, failed_generation: str, tools: List[Dict]) -> Optional[List[Dict]]:
        """
        Attempt to extract tool calls from malformed model output.

        Handles common malformations:
        - XML wrappers: <function=name>{...}</function>
        - Missing '>' after name: <function=name{...}></function>
        - Multiple tool calls in one output

        Args:
            failed_generation: Raw model output that failed Groq validation
            tools: List of available tools (for validation)

        Returns:
            List of tool_call dicts in OpenAI format if successful, None otherwise
        """
        if not failed_generation or not tools:
            return None

        # Build set of valid tool names for validation
        valid_names = {t['function']['name'] for t in tools}

        tool_calls = []

        # Simple string splitting - no regex!
        # Find all <function=...> patterns by splitting on '<function='
        parts = failed_generation.split('<function=')

        for i, part in enumerate(parts[1:], 1):  # Skip first part (before any function tags)
            try:
                # Find the closing tag
                end_idx = part.find('</function>')
                if end_idx == -1:
                    continue

                content = part[:end_idx]

                # Extract function name and JSON
                # The model generates various malformed formats:
                # - Correct: "name>{json}"
                # - Wrong: "name{json}" (missing '>' after name)
                # - Wrong: "name{json}>" ('>' after json instead of after name)

                # Find where JSON starts (always starts with '{')
                brace_idx = content.find('{')
                if brace_idx == -1:
                    continue

                # Everything before '{' is the function name (possibly with '>')
                func_name = content[:brace_idx].strip().rstrip('>')

                # Everything from '{' onwards is JSON (possibly with trailing '>')
                json_str = content[brace_idx:].strip().rstrip('>')

                # Validate function name
                if func_name not in valid_names:
                    continue

                # Validate JSON - let json.loads do the heavy lifting
                try:
                    json.loads(json_str)  # Validate it's valid JSON
                except json.JSONDecodeError:
                    continue

                # Build OpenAI-format tool call
                tool_calls.append({
                    "id": f"call_lenient_{i}_{hash(json_str) & 0xFFFFFF:06x}",
                    "type": "function",
                    "function": {
                        "name": func_name,
                        "arguments": json_str  # Keep as string per OpenAI spec
                    }
                })

            except Exception:
                # Skip this part if anything goes wrong
                continue

        return tool_calls if tool_calls else None

    def _call_api(self, payload: Dict) -> Dict:
        response = requests.post(
            self.API_URL,
            headers=self._build_headers(),
            json=payload,
        )

        if not response.ok:
            error_data = response.json() if response.text else {}

            # Enhanced error handling for tool_use_failed (400 errors)
            if response.status_code == 400:
                error_obj = error_data.get("error", {})
                error_message = error_obj.get("message", "Unknown error")

                # Check for tool use failures
                is_tool_failure = (
                    "tool_use_failed" in error_message.lower() or
                    error_obj.get("failed_generation")
                )

                if is_tool_failure and self.lenient_tool_parsing:
                    failed_gen = error_obj.get("failed_generation", "")
                    tools = payload.get("tools", [])

                    # Attempt lenient parsing
                    if failed_gen and tools:
                        recovered_calls = self._attempt_lenient_tool_parse(failed_gen, tools)

                        if recovered_calls:
                            # SUCCESS: Recovery worked!
                            self.lenient_parse_count += 1

                            # Return synthetic successful response in OpenAI format
                            return {
                                "choices": [{
                                    "index": 0,
                                    "message": {
                                        "role": "assistant",
                                        "content": None,
                                        "tool_calls": recovered_calls
                                    },
                                    "finish_reason": "tool_calls"
                                }],
                                "usage": {
                                    "prompt_tokens": 0,  # Unknown - Groq didn't return usage
                                    "completion_tokens": 0,
                                    "total_tokens": 0
                                },
                                "model": self.model,
                                "_lenient_parse": True,  # Flag for tracking/debugging
                                "_original_error": failed_gen  # Keep for debugging
                            }

                # Lenient parsing disabled or failed - raise error
                if is_tool_failure:
                    failed_gen = error_obj.get("failed_generation", "Not provided")

                    # Build helpful error message
                    hint_msg = (
                        "Some models (especially 8b) may wrap JSON in XML tags.\n"
                        "      Use natural language prompts instead of explicit commands:\n"
                        "      ✅ 'I need to understand the code structure'\n"
                        "      ❌ 'Use the reveal_structure tool on /path'"
                    )

                    if self.lenient_tool_parsing:
                        hint_msg += "\n      Lenient parsing attempted but failed."
                    else:
                        hint_msg += "\n      Lenient parsing is disabled. Enable with lenient_tool_parsing=True"

                    raise RuntimeError(
                        f"Groq API error (400): tool_use_failed\n"
                        f"Model '{self.model}' generated malformed tool call format.\n"
                        f"Generated: {failed_gen}\n"
                        f"Hint: {hint_msg}"
                    )

            # Generic error fallback
            raise RuntimeError(f"Groq API error ({response.status_code}): {error_data}")

        return response.json()

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _parse_response(self, data: Dict) -> LLMResponse:
        message = data["choices"][0]["message"]
        return LLMResponse(
            text=message.get("content", ""),
            tool_calls=message.get("tool_calls"),
            usage=data.get("usage"),
        )

    def _calculate_token_cost(self, tokens: int, cost_per_million: float) -> float:
        return (tokens / 1_000_000) * cost_per_million
