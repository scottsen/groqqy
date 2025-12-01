# Groqqy Agentic Architecture Proposal

**Current Status:** v0.2.0 - Functional but monolithic
**Proposal:** Refactor for true micro agentic capabilities

---

## 🎯 Core Problem

Groqqy v0.2.0 is a **single-turn assistant**, not a true **agentic bot**.

**Current flow:**
```
User → LLM → [Tools?] → Response → Done
```

**Agentic flow should be:**
```
User → Agent Loop:
  1. Think (plan next action)
  2. Act (use tool or respond)
  3. Observe (process result)
  4. Repeat until done
→ Final Response
```

---

## 🏗️ Proposed Architecture

### **Layer 1: Tool System** (Extensible, composable)

```python
# groqqy/tool.py
from dataclasses import dataclass
from typing import Callable, Dict, Any
import inspect

@dataclass
class Tool:
    """A tool that agents can use."""
    name: str
    description: str
    function: Callable
    parameters: Dict  # JSON schema

    @classmethod
    def from_function(cls, func: Callable, description: str = None):
        """Auto-create tool from function with introspection."""
        from .utils import build_tool_schema
        schema = build_tool_schema(func)
        return cls(
            name=func.__name__,
            description=description or func.__doc__ or "",
            function=func,
            parameters=schema['function']['parameters']
        )


class ToolRegistry:
    """Manages available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool."""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Get tool by name."""
        return self.tools.get(name)

    def list_all(self) -> list[Tool]:
        """List all tools."""
        return list(self.tools.values())

    def as_schemas(self) -> list[Dict]:
        """Convert to OpenAI tool schemas."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
            }
            for t in self.tools.values()
        ]


# Decorator for easy tool creation
def tool(description: str = None):
    """Decorator to register a function as a tool."""
    def decorator(func):
        # Store metadata on function for later registration
        func._tool_description = description
        return func
    return decorator


# Usage example:
@tool(description="Read contents of a file")
def read_file(file_path: str) -> str:
    """Read and return contents of a file."""
    with open(file_path, 'r') as f:
        return f.read()

# Auto-register
registry = ToolRegistry()
registry.register(Tool.from_function(read_file, "Read a file"))
```

**Benefits:**
- ✅ Dynamic tool registration
- ✅ Metadata attached to tools
- ✅ Easy to add custom tools
- ✅ Schema auto-generation

---

### **Layer 2: Composable Components** (Separation of concerns)

```python
# groqqy/components/conversation.py
class ConversationManager:
    """Manages conversation history."""

    def __init__(self):
        self.messages = []

    def add_user(self, message: str):
        self.messages.append({"role": "user", "content": message})

    def add_assistant(self, message: str):
        self.messages.append({"role": "assistant", "content": message})

    def add_tool_calls(self, text: str, tool_calls: list):
        self.messages.append({
            "role": "assistant",
            "content": text or "",
            "tool_calls": tool_calls
        })

    def add_tool_result(self, tool_call_id: str, result: str):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        })

    def get_history(self) -> list:
        return self.messages

    def reset(self):
        self.messages = []


# groqqy/components/executor.py
class ToolExecutor:
    """Executes tools from registry."""

    def __init__(self, registry: ToolRegistry, logger=None):
        self.registry = registry
        self.log = logger or get_logger("executor")

    def execute(self, tool_call: Dict) -> str:
        """Execute a single tool call."""
        name = tool_call['function']['name']
        args = json.loads(tool_call['function']['arguments'])

        tool = self.registry.get(name)
        if not tool:
            return f"Error: Tool {name} not found"

        try:
            self.log.debug(f"Executing {name}", args=args)
            result = tool.function(**args)
            self.log.info(f"Tool {name} succeeded",
                         result_length=len(str(result)))
            return str(result)
        except Exception as e:
            self.log.error(f"Tool {name} failed", error=str(e))
            return f"Error executing {name}: {e}"

    def execute_all(self, tool_calls: list) -> list[tuple[str, str]]:
        """Execute multiple tool calls, return (id, result) pairs."""
        return [
            (tc['id'], self.execute(tc))
            for tc in tool_calls
        ]


# groqqy/components/tracker.py
class CostTracker:
    """Tracks API costs."""

    def __init__(self):
        self.total = 0.0
        self.calls = []

    def add(self, cost: float, metadata: dict = None):
        self.total += cost
        self.calls.append({
            "cost": cost,
            "timestamp": time.time(),
            **(metadata or {})
        })

    def get_total(self) -> float:
        return self.total

    def reset(self):
        self.total = 0.0
        self.calls = []
```

**Benefits:**
- ✅ Each component has ONE job
- ✅ Can swap implementations
- ✅ Testable in isolation
- ✅ Composable

---

### **Layer 3: Agent Loop** (The "agentic" part)

```python
# groqqy/agent.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentResult:
    """Result from agent execution."""
    response: str
    iterations: int
    total_cost: float
    tool_calls: list
    conversation: list


class Agent:
    """
    Agentic loop: think → act → observe → repeat.

    This is the core of agentic behavior:
    - Can use tools multiple times
    - Can chain tool calls
    - Has max iterations to prevent infinite loops
    """

    def __init__(
        self,
        provider: Provider,
        tools: ToolRegistry,
        max_iterations: int = 10,
        logger=None
    ):
        self.provider = provider
        self.tools = tools
        self.max_iterations = max_iterations
        self.log = logger or get_logger("agent")

        # Components
        self.conversation = ConversationManager()
        self.executor = ToolExecutor(tools, logger)
        self.tracker = CostTracker()

    def run(self, prompt: str) -> AgentResult:
        """
        Run the agent loop until task is complete or max iterations reached.
        """
        self.conversation.add_user(prompt)
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            self.log.debug(f"Agent iteration {iteration}/{self.max_iterations}")

            # THINK: Get LLM response
            response = self.provider.chat(
                messages=self.conversation.get_history(),
                tools=self.tools.as_schemas()
            )

            cost = self.provider.get_cost(response.usage)
            self.tracker.add(cost, {"iteration": iteration})

            # ACT: Execute tools if needed
            if response.tool_calls:
                self.log.info(f"Executing {len(response.tool_calls)} tools")

                # Add tool calls to conversation
                self.conversation.add_tool_calls(response.text, response.tool_calls)

                # Execute tools
                for tool_call in response.tool_calls:
                    result = self.executor.execute(tool_call)

                    # OBSERVE: Add result to conversation
                    self.conversation.add_tool_result(tool_call['id'], result)

                # Continue loop (LLM will process results)
                continue

            # No tool calls - agent is done
            self.conversation.add_assistant(response.text)

            return AgentResult(
                response=response.text,
                iterations=iteration,
                total_cost=self.tracker.get_total(),
                tool_calls=[],  # Could track all tool calls
                conversation=self.conversation.get_history()
            )

        # Max iterations reached
        self.log.warning(f"Max iterations ({self.max_iterations}) reached")
        return AgentResult(
            response="[Max iterations reached]",
            iterations=iteration,
            total_cost=self.tracker.get_total(),
            tool_calls=[],
            conversation=self.conversation.get_history()
        )
```

**Benefits:**
- ✅ Multi-step reasoning
- ✅ Can chain tool calls
- ✅ Prevents infinite loops
- ✅ True agentic behavior

---

### **Layer 4: Simplified Bot** (Just a facade)

```python
# groqqy/bot.py (simplified)
class Groqqy:
    """
    Micro agentic bot - now just a clean facade over Agent.
    """

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        tools: ToolRegistry = None,
        system_instruction: str = None,
        max_iterations: int = 10
    ):
        self.session_id = str(uuid.uuid4())[:8]

        # Provider
        self.provider = GroqProvider(
            model=model,
            system_instruction=system_instruction or self._default_instruction()
        )

        # Tool registry
        self.tools = tools or self._default_tools()

        # Agent (does the heavy lifting)
        self.agent = Agent(
            provider=self.provider,
            tools=self.tools,
            max_iterations=max_iterations
        )

    def chat(self, user_message: str) -> tuple[str, float]:
        """Send message and get response."""
        result = self.agent.run(user_message)
        return result.response, result.total_cost

    def reset(self):
        """Reset conversation."""
        self.agent.conversation.reset()
        self.agent.tracker.reset()

    @property
    def total_cost(self) -> float:
        return self.agent.tracker.get_total()

    @property
    def conversation(self) -> list:
        return self.agent.conversation.get_history()

    def _default_instruction(self) -> str:
        return "You are Groqqy, a helpful assistant..."

    def _default_tools(self) -> ToolRegistry:
        """Create default tool registry."""
        registry = ToolRegistry()

        # Register default tools
        from .tools import read_file, run_command, search_files, search_content

        registry.register(Tool.from_function(
            read_file,
            "Read contents of a file"
        ))
        registry.register(Tool.from_function(
            run_command,
            "Execute a shell command (use carefully!)"
        ))
        registry.register(Tool.from_function(
            search_files,
            "Find files matching a pattern"
        ))
        registry.register(Tool.from_function(
            search_content,
            "Search for text in files"
        ))

        return registry
```

**Benefits:**
- ✅ Bot.py shrinks from 277 → ~80 lines
- ✅ Just a facade over Agent
- ✅ Backwards compatible API
- ✅ Cleaner, more focused

---

## 📊 Architecture Comparison

### **Current v0.2.0 (Monolithic)**

```
┌─────────────────────────────────────┐
│          Groqqy (277 lines)         │
│  - Conversation management          │
│  - LLM calls                        │
│  - Tool execution                   │
│  - Cost tracking                    │
│  - Provider creation                │
└─────────────────────────────────────┘
        ↓
    [Tools] (4 plain functions)
        ↓
    [Provider] (interface)
```

**Issues:**
- ❌ Everything in one class
- ❌ Tools hardcoded
- ❌ No multi-step agent loop
- ❌ Hard to extend

### **Proposed (Composable)**

```
┌─────────────────────┐
│   Groqqy (facade)   │  ← 80 lines, clean API
└──────────┬──────────┘
           ↓
    ┌──────────────┐
    │    Agent     │  ← Agentic loop (think/act/observe)
    └──────┬───────┘
           ↓
    ┌──────────────────────────────┐
    │       Components             │
    │  - ConversationManager       │
    │  - ToolExecutor              │
    │  - CostTracker               │
    └──────────────────────────────┘
           ↓
    ┌──────────────┐
    │ ToolRegistry │  ← Dynamic, extensible
    └──────┬───────┘
           ↓
    [Tool objects] (metadata + function)
           ↓
    [Provider] (swappable)
```

**Benefits:**
- ✅ Separation of concerns
- ✅ Each component <100 lines
- ✅ Composable
- ✅ Multi-step reasoning
- ✅ Easy to extend

---

## 🎯 Use Case Examples

### **Current v0.2.0 (Limited)**

```python
bot = Groqqy()
response, cost = bot.chat("Read config.yaml and run tests")

# What happens:
# 1. LLM responds
# 2. If tools called: execute once
# 3. Return final response
# ❌ Can't chain: "read file, then based on content, run different commands"
```

### **Proposed (Agentic)**

```python
bot = Groqqy(max_iterations=10)
response, cost = bot.chat("Read config.yaml and run the test command specified in it")

# What happens:
# Iteration 1:
#   - Think: "I need to read config.yaml first"
#   - Act: read_file("config.yaml")
#   - Observe: content = "test_cmd: pytest tests/"
#
# Iteration 2:
#   - Think: "Now I know the command, let me run it"
#   - Act: run_command("pytest tests/")
#   - Observe: result = "All tests passed"
#
# Iteration 3:
#   - Think: "I have all info, respond to user"
#   - Act: return response
#   - Done!

# ✅ Multi-step reasoning!
# ✅ Chained tool calls!
# ✅ True agentic behavior!
```

### **Custom Tools (Proposed)**

```python
# Define custom tool
@tool(description="Query database")
def query_db(sql: str) -> str:
    return db.execute(sql).fetchall()

# Register it
registry = ToolRegistry()
registry.register(Tool.from_function(query_db))

# Add to bot
bot = Groqqy(tools=registry)

# Now bot can use it!
response, cost = bot.chat("How many users do we have?")
# Agent will: Think → query_db("SELECT COUNT(*) FROM users") → Respond
```

---

## 🚀 Migration Path

### **Phase 1: Add Tool Registry (backwards compatible)**

1. Create `groqqy/tool.py` with Tool class and ToolRegistry
2. Keep existing tools.py as-is
3. Bot can use either:
   - Old: `tools=[read_file, run_command]` (list of functions)
   - New: `tools=ToolRegistry()` (registry object)

### **Phase 2: Add Components (optional)**

1. Create `groqqy/components/` directory
2. Extract conversation, executor, tracker
3. Bot uses them internally
4. Public API unchanged

### **Phase 3: Add Agent Loop (opt-in)**

1. Create `groqqy/agent.py`
2. Add `Groqqy(agentic=True)` flag
3. When agentic=True, use Agent loop
4. When agentic=False, use current single-turn
5. Backwards compatible!

### **Phase 4: Make Agent Default**

1. Switch default to agentic=True
2. Deprecate single-turn mode
3. Eventually remove old code

---

## 📈 Impact Assessment

### **Code Size**

| Module | Current | Proposed | Change |
|--------|---------|----------|--------|
| bot.py | 277 lines | 80 lines | -197 ⬇️ |
| tool.py | N/A | 120 lines | +120 ⬆️ |
| agent.py | N/A | 150 lines | +150 ⬆️ |
| components/* | N/A | 200 lines | +200 ⬆️ |
| **Total** | 277 | 550 | +273 |

**Net increase:** 273 lines, BUT:
- ✅ Each file <150 lines
- ✅ Clear separation
- ✅ Easy to understand
- ✅ Easy to extend

### **Capabilities**

| Feature | Current | Proposed |
|---------|---------|----------|
| Single-turn chat | ✅ | ✅ |
| Tool calling | ✅ | ✅ |
| Multi-step reasoning | ❌ | ✅ |
| Tool chaining | ❌ | ✅ |
| Dynamic tools | ❌ | ✅ |
| Tool metadata | ❌ | ✅ |
| Composable | ❌ | ✅ |
| Extensible | ⚠️ Limited | ✅ |

### **Complexity**

| Aspect | Current | Proposed |
|--------|---------|----------|
| Understanding | Medium | Easy |
| Extending | Hard | Easy |
| Testing | Medium | Easy |
| Maintenance | Hard | Easy |

---

## 🎓 Recommendation

**For a true "micro agentic bot":**

✅ **Adopt the proposed architecture**

**Why:**
1. **Agentic behavior** - Multi-step reasoning is essential for real agents
2. **Extensibility** - Tool registry enables plugin ecosystem
3. **Clarity** - Smaller, focused modules easier to understand
4. **Composability** - Mix and match components
5. **Future-proof** - Easy to add: memory, planning, reflection, etc.

**Migration:**
- Start with Phase 1 (Tool Registry) - backwards compatible
- Gradually adopt other pieces
- v0.3.0 could be "Agentic Release"

**Alternative (keep current):**
- If goal is just "simple LLM wrapper with tools" → current is fine
- But if goal is "micro agentic bot" → needs refactor

---

## 📚 References

**Similar architectures:**
- LangChain's Agent framework
- AutoGPT's agent loop
- ReAct pattern (Reason + Act)
- OpenAI's Agent SDK

**TIA parallels:**
- TIA has semantic search, Beth, task system (specialized tools)
- TIA boot sequence (agentic startup)
- TIA's pure/impure separation (similar to Component pattern)

---

**Next step:** Want me to implement Phase 1 (Tool Registry) as a backwards-compatible addition to v0.2.0?
