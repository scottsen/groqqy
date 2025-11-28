"""
Groqqy - Core bot implementation

Clean, composable architecture following functional composition principles.
Each function has a single responsibility and is 3-7 lines.
"""

import json
import sys
from pathlib import Path
from typing import List, Callable, Dict, Any
from dataclasses import dataclass

# Add TIA lib to path if available
tia_lib = Path(__file__).parent.parent.parent.parent / "tia"
if tia_lib.exists():
    sys.path.insert(0, str(tia_lib))

from lib.gemma.providers.groq_provider import GroqProvider
from .tools import read_file, run_command, search_files, search_content


@dataclass
class Response:
    """Response from LLM with cost tracking."""
    text: str
    cost: float
    tool_calls: List[Dict[str, Any]] = None


class Groqqy:
    """
    Simple general-purpose helper bot powered by Groq.

    Architecture:
        - Conversation management (add messages, track history)
        - LLM interaction (get responses)
        - Tool execution (execute and handle results)
        - Cost tracking (per-message and total)
    """

    def __init__(self, model: str = "llama-3.1-8b-instant", tools: List[Callable] = None):
        """Initialize Groqqy with model and tools."""
        self.provider = self._create_provider(model)
        self.tools = tools or self._default_tools()
        self.conversation = []
        self.total_cost = 0.0

    # ========================================================================
    # Public API
    # ========================================================================

    def chat(self, user_message: str) -> tuple[str, float]:
        """Send message and get response (orchestrates full interaction)."""
        self._add_user_message(user_message)
        response = self._get_response_with_tools()
        self._add_assistant_message(response.text)
        self._track_cost(response.cost)
        return response.text, response.cost

    def reset(self):
        """Reset conversation history and cost."""
        self.conversation = []
        self.total_cost = 0.0

    # ========================================================================
    # Conversation Management
    # ========================================================================

    def _add_user_message(self, message: str):
        """Add user message to conversation."""
        self.conversation.append({"role": "user", "content": message})

    def _add_assistant_message(self, message: str):
        """Add assistant message to conversation."""
        self.conversation.append({"role": "assistant", "content": message})

    def _add_assistant_with_tool_calls(self, text: str, tool_calls: List[Dict]):
        """Add assistant message that includes tool calls."""
        self.conversation.append({
            "role": "assistant",
            "content": text or "",
            "tool_calls": tool_calls
        })

    def _add_tool_result(self, tool_call_id: str, result: str):
        """Add tool execution result to conversation."""
        self.conversation.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        })

    # ========================================================================
    # LLM Interaction
    # ========================================================================

    def _get_response_with_tools(self) -> Response:
        """Get response, executing tools if needed."""
        response = self._call_llm()
        if response.tool_calls:
            response = self._execute_tools_and_retry(response)
        return response

    def _call_llm(self) -> Response:
        """Call LLM and return standardized response."""
        response = self.provider.chat(messages=self.conversation, tools=self.tools)
        cost = self.provider.get_cost(response.usage)
        return Response(text=response.text, cost=cost, tool_calls=response.tool_calls)

    def _execute_tools_and_retry(self, response: Response) -> Response:
        """Execute tool calls and get final response."""
        self._add_assistant_with_tool_calls(response.text, response.tool_calls)
        self._execute_all_tools(response.tool_calls)
        followup = self._call_llm()
        return Response(text=followup.text, cost=response.cost + followup.cost)

    # ========================================================================
    # Tool Execution
    # ========================================================================

    def _execute_all_tools(self, tool_calls: List[Dict]):
        """Execute all tool calls and add results to conversation."""
        for tool_call in tool_calls:
            result = self._execute_single_tool(tool_call)
            self._add_tool_result(tool_call['id'], result)

    def _execute_single_tool(self, tool_call: Dict) -> str:
        """Execute a single tool call and return result."""
        func_name = tool_call['function']['name']
        args = json.loads(tool_call['function']['arguments'])
        tool = self._find_tool(func_name)
        return self._call_tool(tool, args) if tool else self._tool_not_found(func_name)

    def _find_tool(self, name: str) -> Callable:
        """Find tool by name."""
        return next((t for t in self.tools if t.__name__ == name), None)

    def _call_tool(self, tool: Callable, args: Dict) -> str:
        """Call tool with args and return result."""
        try:
            return tool(**args)
        except Exception as e:
            return f"Error executing {tool.__name__}: {e}"

    def _tool_not_found(self, name: str) -> str:
        """Return error message for missing tool."""
        return f"Error: Tool {name} not found"

    # ========================================================================
    # Cost Tracking
    # ========================================================================

    def _track_cost(self, cost: float):
        """Add cost to total."""
        self.total_cost += cost

    # ========================================================================
    # Setup Helpers
    # ========================================================================

    def _create_provider(self, model: str) -> GroqProvider:
        """Create and configure LLM provider."""
        return GroqProvider(
            model=model,
            system_instruction=self._system_instruction()
        )

    def _system_instruction(self) -> str:
        """Return system instruction for the bot."""
        return """You are Groqqy, a helpful assistant.
You have access to tools for reading files, running commands, and searching.
Keep responses concise and friendly. Use tools when needed to help the user."""

    def _default_tools(self) -> List[Callable]:
        """Return default tool set."""
        return [read_file, run_command, search_files, search_content]
