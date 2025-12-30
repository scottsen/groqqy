"""
ConversationManager - Manages conversation history

Single responsibility: Message list management
"""

from typing import List, Dict, Any

from ..log import get_logger


class ConversationManager:
    """
    Manages conversation message history with context overflow prevention.

    Provides simple, clear API for adding different message types.
    Automatically prunes old messages when approaching context limits.
    """

    def __init__(self, max_context_tokens: int = 100000):
        """
        Initialize with empty conversation.

        Args:
            max_context_tokens: Maximum tokens before pruning (default: 100K, safe for 128K models)
        """
        self._messages: List[Dict[str, Any]] = []
        self.max_context_tokens = max_context_tokens
        self.log = get_logger("conversation")

    def estimate_tokens(self) -> int:
        """
        Rough token estimate for all messages.

        Uses ~4 chars per token as conservative estimate.
        Better safe than sorry when preventing context overflow.

        Returns:
            Estimated token count
        """
        total_chars = 0
        for msg in self._messages:
            # Count content
            content = msg.get('content', '')
            if content:
                total_chars += len(str(content))

            # Count tool calls (if present)
            tool_calls = msg.get('tool_calls', [])
            if tool_calls:
                total_chars += len(str(tool_calls))

        return total_chars // 4

    def prune_if_needed(self):
        """
        Prune old messages if approaching context limit.

        Keeps system message (first message, if it exists) plus last N messages.
        Triggers at 80% of max_context_tokens to leave safety margin.
        """
        tokens = self.estimate_tokens()

        # Prune at 80% threshold
        if tokens > self.max_context_tokens * 0.8:
            messages_count = len(self._messages)

            # Keep first message (system prompt) + last 10 messages
            if messages_count > 11:
                # Check if first message looks like a system message
                if self._messages and self._messages[0].get('role') in ['system', 'user']:
                    system_msg = self._messages[0]
                    recent = self._messages[-10:]
                    self._messages = [system_msg] + recent

                    self.log.warning("Conversation pruned due to context limit",
                                   previous_count=messages_count,
                                   kept_count=len(self._messages),
                                   estimated_tokens=tokens,
                                   max_tokens=self.max_context_tokens)
                else:
                    # No system message, just keep last 10
                    self._messages = self._messages[-10:]

                    self.log.warning("Conversation pruned due to context limit (no system msg)",
                                   previous_count=messages_count,
                                   kept_count=len(self._messages),
                                   estimated_tokens=tokens,
                                   max_tokens=self.max_context_tokens)

    def add_user(self, message: str):
        """
        Add user message.

        Args:
            message: User's text message
        """
        self._messages.append({
            "role": "user",
            "content": message
        })
        self.prune_if_needed()

    def add_assistant(self, message: str):
        """
        Add assistant message.

        Args:
            message: Assistant's text response
        """
        self._messages.append({
            "role": "assistant",
            "content": message
        })
        self.prune_if_needed()

    def add_tool_calls(self, text: str, tool_calls: List[Dict]):
        """
        Add assistant message with tool calls.

        Args:
            text: Optional text from assistant
            tool_calls: List of tool call objects
        """
        self._messages.append({
            "role": "assistant",
            "content": text or "",
            "tool_calls": tool_calls
        })
        self.prune_if_needed()

    def add_tool_result(self, tool_call_id: str, result: str):
        """
        Add tool execution result.

        Args:
            tool_call_id: ID of the tool call
            result: String result from tool execution
        """
        self._messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        })
        self.prune_if_needed()

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get full conversation history.

        Returns:
            List of message dictionaries
        """
        return self._messages

    def reset(self):
        """Clear all messages."""
        self._messages = []

    def __len__(self) -> int:
        """Return number of messages."""
        return len(self._messages)

    def __repr__(self) -> str:
        """String representation."""
        return f"ConversationManager({len(self._messages)} messages)"
