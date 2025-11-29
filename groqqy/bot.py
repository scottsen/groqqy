"""
Groqqy - Micro agentic bot (facade over Agent)

Clean API over composable components:
- Agent: Agentic loop (think/act/observe)
- Provider: LLM backend
- ToolRegistry: Available tools
"""

import uuid
from typing import Optional, List, Dict, Any

from .providers.groq import GroqProvider
from .agent import Agent
from .tool import ToolRegistry, create_default_registry
from .log import get_logger


class Groqqy:
    """
    Simple micro agentic bot powered by Groq.

    Features:
    - Multi-step reasoning (agent loop)
    - Tool chaining
    - Extensible tool registry
    - Clean, composable architecture

    This is a thin facade - all heavy lifting done by Agent.
    """

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        tools: Optional[ToolRegistry] = None,
        system_instruction: Optional[str] = None,
        max_iterations: int = 10
    ):
        """
        Initialize Groqqy.

        Args:
            model: Groq model name
            tools: ToolRegistry (uses defaults if not provided)
            system_instruction: Custom system prompt (uses default if not provided)
            max_iterations: Maximum agent loop iterations
        """
        # Session tracking
        self.session_id = str(uuid.uuid4())[:8]
        self.log = get_logger("groqqy").bind(
            session_id=self.session_id,
            model=model
        )

        # Provider (LLM backend)
        self.provider = GroqProvider(
            model=model,
            system_instruction=system_instruction or self._default_instruction()
        )

        # Tool registry
        self.tools = tools or create_default_registry()

        # Agent (does the heavy lifting)
        self.agent = Agent(
            provider=self.provider,
            tools=self.tools,
            max_iterations=max_iterations,
            logger=self.log
        )

        self.log.info("Groqqy initialized",
                     tool_count=len(self.tools),
                     tools=self.tools.list_names(),
                     max_iterations=max_iterations,
                     has_custom_instruction=bool(system_instruction))

    def chat(self, user_message: str) -> tuple[str, float]:
        """
        Send message and get response.

        Runs the full agent loop:
        - Can use tools multiple times
        - Can chain tool calls
        - Multi-step reasoning

        Args:
            user_message: User's input

        Returns:
            (response_text, cost) tuple
        """
        self.log.debug("Chat started",
                      message_length=len(user_message),
                      message_preview=user_message[:100])

        result = self.agent.run(user_message)

        self.log.info("Chat completed",
                     iterations=result.iterations,
                     tool_calls=result.tool_calls_made,
                     cost=result.total_cost,
                     total_cost=self.total_cost)

        return result.response, result.total_cost

    def reset(self):
        """Reset conversation history and cost tracking."""
        prev_turns = len(self.agent.conversation)
        prev_cost = self.agent.tracker.get_total()

        self.agent.reset()

        self.log.info("Conversation reset",
                     previous_turns=prev_turns,
                     previous_cost=prev_cost)

    # ========================================================================
    # Properties (for backwards compatibility)
    # ========================================================================

    @property
    def total_cost(self) -> float:
        """Get total accumulated cost."""
        return self.agent.tracker.get_total()

    @property
    def conversation(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.agent.conversation.get_history()

    # ========================================================================
    # Helpers
    # ========================================================================

    def _default_instruction(self) -> str:
        """Return default system instruction."""
        return """You are Groqqy, a helpful assistant.
You have access to tools for reading files, running commands, and searching.
Keep responses concise and friendly. Use tools when needed to help the user."""
