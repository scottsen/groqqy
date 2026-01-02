"""
Agent - Agentic loop implementation

Implements: Think → Act → Observe pattern
Enables multi-step reasoning and tool chaining
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .provider import Provider
from .tool import ToolRegistry
from .components import ConversationManager, ToolExecutor, CostTracker
from .log import get_logger
from .strategy import ToolExecutionStrategy, detect_strategy


@dataclass
class AgentResult:
    """
    Result from agent execution.

    Contains final response plus metadata about the execution.
    """
    response: str
    iterations: int
    total_cost: float
    tool_calls_made: int
    conversation: List[Dict[str, Any]]


class Agent:
    """
    Agentic loop: Think → Act → Observe → Repeat.

    The agent can:
    - Make multiple LLM calls
    - Use tools multiple times
    - Chain tool calls together
    - Reason over tool results

    This enables true agentic behavior beyond simple single-turn chat.
    """

    def __init__(
        self,
        provider: Provider,
        tools: ToolRegistry,
        max_iterations: int = 10,
        logger=None,
        strategy: Optional[ToolExecutionStrategy] = None,
        debug_dir: Optional[str] = None
    ):
        """
        Initialize agent.

        Args:
            provider: LLM provider (e.g., GroqProvider)
            tools: ToolRegistry with available tools
            max_iterations: Maximum agent loop iterations (prevents infinite loops)
            logger: Optional logger
            strategy: Tool execution strategy (auto-detected if not provided)
            debug_dir: Optional directory for saving failure state dumps
        """
        self.provider = provider
        self.tools = tools
        self.max_iterations = max_iterations
        self.log = logger or get_logger("agent")
        self.debug_dir = debug_dir

        # Auto-detect strategy based on tool types (or use default if no tools)
        if tools is not None:
            self.strategy = strategy or detect_strategy(tools.to_schemas())
        else:
            # No tools - strategy won't be used, but we need a valid object
            from .strategy import LocalToolStrategy
            self.strategy = LocalToolStrategy()

        self.log.debug(f"Agent initialized with {self.strategy.describe()}")

        # Components (composable!)
        self.conversation = ConversationManager()
        self.executor = ToolExecutor(tools, logger) if tools is not None else None
        self.tracker = CostTracker()

        # Loop detection (prevent infinite repeated tool calls)
        self.tool_call_history = []

    def run(self, prompt: str) -> AgentResult:
        """
        Run the agent loop until task is complete.

        Flow:
        1. Add user prompt to conversation
        2. Loop:
           a. THINK: Get LLM response
           b. ACT: Execute any tool calls
           c. OBSERVE: Add results to conversation
           d. Repeat until LLM returns without tool calls
        3. Return final response

        Args:
            prompt: User's input message

        Returns:
            AgentResult with response and execution metadata
        """
        self.conversation.add_user(prompt)
        iteration = 0
        tool_calls_made = 0

        self.log.debug("Agent run started",
                      prompt_length=len(prompt),
                      max_iterations=self.max_iterations)

        while iteration < self.max_iterations:
            iteration += 1
            self.log.debug(f"Agent iteration {iteration}/{self.max_iterations}")

            # THINK: What should I do next?
            response = self._call_llm()

            # Log LLM response for debugging (helps understand agent reasoning)
            has_tool_calls = hasattr(response, 'tool_calls') and response.tool_calls is not None
            num_tool_calls = len(response.tool_calls) if has_tool_calls else 0
            response_preview = response.text[:500] if response.text else ""

            self.log.debug("LLM response received",
                          iteration=iteration,
                          response_length=len(response.text) if response.text else 0,
                          response_preview=response_preview,
                          has_tool_calls=has_tool_calls,
                          num_tool_calls=num_tool_calls)

            # Track cost
            cost = self.provider.get_cost(response.usage)
            self.tracker.add(cost, {"iteration": iteration})

            # ACT: Let strategy decide how to handle response
            tools_schemas = self.tools.to_schemas() if self.tools is not None else []
            execution_result = self.strategy.handle_response(
                response,
                tools_schemas
            )

            if execution_result.needs_continuation:
                # Strategy says we need to execute tools locally
                num_tools = len(execution_result.tool_calls)
                tool_calls_made += num_tools

                # Show what tools are about to be executed
                tool_summaries = []
                for tc in execution_result.tool_calls:
                    name = tc['function']['name']
                    args = tc['function']['arguments']
                    # Parse args to show command if it's run_command
                    try:
                        import json
                        args_dict = json.loads(args) if isinstance(args, str) else args
                        if name == "run_command" and "command" in args_dict:
                            tool_summaries.append(f"{name}('{args_dict['command']}')")
                        else:
                            tool_summaries.append(name)
                    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
                        tool_summaries.append(name)

                self.log.info(f"Executing {num_tools} tool(s)",
                             iteration=iteration,
                             tools=tool_summaries)

                # Check for infinite loops (repeated identical tool calls)
                if self._detect_loop(execution_result.tool_calls):
                    self.log.warning("Loop detected - agent repeating identical tool calls",
                                   iteration=iteration,
                                   tools=tool_summaries)

                    # Dump full conversation state for debugging
                    dump_path = self._dump_failure_state(
                        failure_type="loop_detected",
                        iteration=iteration,
                        tool_calls=execution_result.tool_calls,
                        response_text=response.text
                    )

                    # Add warning to conversation
                    warning_msg = (
                        "[Loop detected: Agent is repeating the same tool calls. "
                        "Task may not be possible with available tools. Stopping.]"
                    )
                    if dump_path:
                        warning_msg += f"\n[Debug state saved to: {dump_path}]"

                    self.conversation.add_assistant(warning_msg)

                    return AgentResult(
                        response="[Loop detected - agent stuck in repeated tool calls]",
                        iterations=iteration,
                        total_cost=self.tracker.get_total(),
                        tool_calls_made=tool_calls_made,
                        conversation=self.conversation.get_history()
                    )

                # Add tool calls to conversation
                self.conversation.add_tool_calls(
                    response.text, execution_result.tool_calls
                )

                # Execute all tools
                for tool_call in execution_result.tool_calls:
                    # OBSERVE: Get tool result
                    result = self.executor.execute(tool_call)

                    # Add result to conversation (LLM will see this next iteration)
                    self.conversation.add_tool_result(tool_call['id'], result)

                # Continue loop - LLM will process tool results
                continue

            # Strategy says we're done (no local execution needed)
            self.conversation.add_assistant(response.text)

            # DEBUG: Log what we're returning
            final_response = execution_result.content or response.text
            exec_content = (
                execution_result.content[:100]
                if execution_result.content else None
            )
            resp_text = response.text[:100] if response.text else None
            final_resp = final_response[:100] if final_response else None
            self.log.info("Agent run completed",
                         iterations=iteration,
                         tool_calls_made=tool_calls_made,
                         total_cost=self.tracker.get_total(),
                         execution_result_content=exec_content,
                         response_text=resp_text,
                         final_response=final_resp)

            return AgentResult(
                response=final_response,
                iterations=iteration,
                total_cost=self.tracker.get_total(),
                tool_calls_made=tool_calls_made,
                conversation=self.conversation.get_history()
            )

        # Max iterations reached - return partial result
        self.log.warning(f"Max iterations ({self.max_iterations}) reached",
                        tool_calls_made=tool_calls_made)

        # Dump full conversation state for debugging
        self._dump_failure_state(
            failure_type="max_iterations",
            iteration=iteration,
            response_text=None  # No response available at this point
        )

        return AgentResult(
            response="[Agent reached max iterations - task may be incomplete]",
            iterations=iteration,
            total_cost=self.tracker.get_total(),
            tool_calls_made=tool_calls_made,
            conversation=self.conversation.get_history()
        )

    def _call_llm(self):
        """
        Call LLM with current conversation and available tools.

        Returns:
            LLMResponse from provider
        """
        # Pass None for tools if no tool registry
        tools_schemas = self.tools.to_schemas() if self.tools is not None else None
        return self.provider.chat(
            messages=self.conversation.get_history(),
            tools=tools_schemas
        )

    def _detect_loop(self, tool_calls: List[Dict]) -> bool:
        """
        Detect if agent is stuck in a loop (repeated identical tool calls).

        Checks if the last 3 tool call sets are identical, indicating the agent
        is repeating the same failed actions without making progress.

        Args:
            tool_calls: Current set of tool calls to check

        Returns:
            True if loop detected, False otherwise
        """
        import json

        # Build signature for this set of tool calls
        signature = []
        for tc in tool_calls:
            name = tc['function']['name']
            args = tc['function']['arguments']
            # Normalize args to string for comparison
            args_str = args if isinstance(args, str) else json.dumps(args, sort_keys=True)
            signature.append(f"{name}({args_str})")

        # Sort for consistent comparison (order doesn't matter for loop detection)
        signature_str = "||".join(sorted(signature))

        # Check last 3 iterations for identical calls
        if len(self.tool_call_history) >= 2:
            recent = self.tool_call_history[-2:]  # Last 2 signatures
            if all(s == signature_str for s in recent):
                # Same call 3 times in a row (2 previous + this one) = loop
                return True

        # Add to history (keep last 5 for efficiency)
        self.tool_call_history.append(signature_str)
        if len(self.tool_call_history) > 5:
            self.tool_call_history.pop(0)

        return False

    def _dump_failure_state(self, failure_type: str, iteration: int,
                            tool_calls: Optional[List[Dict]] = None,
                            response_text: Optional[str] = None) -> Optional[str]:
        """
        Dump complete conversation state when a failure occurs.

        This creates a JSON file with full context for debugging, including:
        - Conversation history
        - Tool call history (for loop detection)
        - Last LLM response
        - Last tool calls and results

        Args:
            failure_type: Type of failure ("loop_detected", "max_iterations", etc.)
            iteration: Current iteration number
            tool_calls: Tool calls that triggered the failure (if applicable)
            response_text: Last LLM response text (if available)

        Returns:
            Path to dump file if created, None otherwise
        """
        if not self.debug_dir:
            return None

        try:
            import json
            from pathlib import Path
            from datetime import datetime

            debug_path = Path(self.debug_dir)
            debug_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dump_file = debug_path / f"failure_{failure_type}_{timestamp}.json"

            # Build tool call signatures for loop analysis
            tool_signatures = []
            if tool_calls:
                for tc in tool_calls:
                    name = tc['function']['name']
                    args = tc['function']['arguments']
                    args_str = args if isinstance(args, str) else json.dumps(args, sort_keys=True)
                    tool_signatures.append(f"{name}({args_str})")

            dump_data = {
                "failure_type": failure_type,
                "timestamp": timestamp,
                "iteration": iteration,
                "max_iterations": self.max_iterations,
                "conversation_history": self.conversation.get_history(),
                "tool_call_history": self.tool_call_history,
                "current_tool_calls": tool_signatures,
                "last_response_text": response_text,
                "total_cost": self.tracker.get_total(),
                "tool_calls_made": sum(1 for msg in self.conversation.get_history()
                                      if msg.get('role') == 'assistant' and msg.get('tool_calls'))
            }

            with open(dump_file, 'w') as f:
                json.dump(dump_data, f, indent=2)

            self.log.info("Failure state dumped",
                         failure_type=failure_type,
                         dump_file=str(dump_file),
                         conversation_messages=len(self.conversation.get_history()))

            return str(dump_file)

        except Exception as e:
            self.log.error("Failed to dump failure state",
                          error=str(e),
                          error_type=type(e).__name__)
            return None

    def reset(self):
        """Reset agent state (conversation, costs)."""
        self.conversation.reset()
        self.tracker.reset()
        self.tool_call_history = []  # Reset loop detection
        self.log.debug("Agent reset")
