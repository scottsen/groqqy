# Groqqy Architecture

**v0.3.0 - Clean, Composable, Extensible**

## Design Philosophy

Groqqy follows these core principles:

1. **Clarity over cleverness** - Readable code beats smart code
2. **Composability first** - Small, focused, reusable components
3. **Single responsibility** - One job per component
4. **Separation of concerns** - Clear boundaries between layers
5. **Teaching-friendly** - Structure visible, easy to understand

All design choices prioritize **understandability** and **extensibility**.

---

## Architecture Overview

### Layer Diagram

```
┌──────────────────────────────────────────────────────┐
│                 Layer 1: Public API                  │
│                      (Bot)                           │
│  Simple facade: chat(), reset()                      │
│  Hides complexity, provides clean interface          │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│                 Layer 2: Agent                       │
│          (Agentic Loop Orchestrator)                 │
│  THINK → ACT → OBSERVE loop                          │
│  Coordinates: Provider, Tools, Components            │
└────────────────────┬─────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┬─────────────┐
      │              │              │             │
      ▼              ▼              ▼             ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Conversa-│   │   Tool   │   │   Cost   │   │ Provider │
│tion Mgr  │   │ Executor │   │ Tracker  │   │  (LLM)   │
│          │   │          │   │          │   │          │
│ Message  │   │ Execute  │   │ Track    │   │ Chat     │
│ history  │   │ tools    │   │ costs    │   │ API      │
└──────────┘   └────┬─────┘   └──────────┘   └──────────┘
                    │
                    ▼
              ┌──────────┐
              │   Tool   │
              │ Registry │
              │          │
              │ Dynamic  │
              │ tools    │
              └──────────┘
```

### Component Responsibilities

| Component | Responsibility | Lines | Dependencies |
|-----------|---------------|-------|--------------|
| **Bot** | Simple API facade | 140 | Agent |
| **Agent** | Agentic loop orchestration | 175 | All components |
| **ConversationManager** | Message history | 92 | None |
| **ToolExecutor** | Tool execution | 102 | ToolRegistry |
| **CostTracker** | Cost accumulation | 72 | None |
| **Provider** | LLM interface | 35 | None (abstract) |
| **ToolRegistry** | Tool management | 199 | None |

**Key insight:** Each component is <200 lines and has ZERO or ONE dependency.

---

## Layer 1: Public API (Bot)

**File:** `bot.py` (140 lines)

### Purpose

Provide a simple, user-friendly interface that hides all complexity.

### Design

**Facade pattern** - Bot delegates everything to Agent:

```python
class Groqqy:
    def __init__(self, model, tools, system_instruction, max_iterations):
        # Create provider
        self.provider = GroqProvider(model, system_instruction)

        # Create or convert tools
        self.tools = tools or create_default_registry()

        # Create agent (does the real work)
        self.agent = Agent(self.provider, self.tools, max_iterations)

    def chat(self, user_message: str) -> tuple[str, float]:
        """Simple chat interface."""
        result = self.agent.run(user_message)
        return result.response, result.total_cost

    def reset(self):
        """Reset conversation."""
        self.agent.reset()
```

### Why This Design?

**Before (v0.2.0):** 277-line monolithic class mixing conversation, tools, LLM, cost tracking

**After (v0.3.0):** 140-line facade that composes components

**Benefits:**
- Simple API for users (unchanged from v0.2.0)
- All complexity moved to Agent
- Easy to understand entry point
- Backwards compatible

### API Contract

```python
# User facing
bot = Groqqy()                           # Create bot
response, cost = bot.chat("message")     # Chat
bot.reset()                              # Reset

# Advanced (new in v0.3.0)
bot = Groqqy(
    model="llama-3.3-70b",               # Custom model
    tools=custom_registry,               # Custom tools
    max_iterations=20,                   # More reasoning steps
    system_instruction="..."             # Custom behavior
)
```

---

## Layer 2: Agent (Agentic Loop)

**File:** `agent.py` (175 lines)

### Purpose

Implement the **ReAct pattern** (Yao et al., 2022): Thought → Action → Observation loop.

### Core Algorithm

```python
def run(self, prompt: str) -> AgentResult:
    """
    THINK → ACT → OBSERVE loop until task complete.
    """
    self.conversation.add_user(prompt)
    iteration = 0

    while iteration < self.max_iterations:
        iteration += 1

        # THINK: What should I do next?
        response = self._call_llm()

        # Track cost
        cost = self.provider.get_cost(response.usage)
        self.tracker.add(cost, {"iteration": iteration})

        # ACT: Execute tools if LLM requested them
        if response.tool_calls:
            # Execute all tools
            for tool_call in response.tool_calls:
                # OBSERVE: Get tool result
                result = self.executor.execute(tool_call)

                # Add to conversation (LLM sees this next iteration)
                self.conversation.add_tool_result(tool_call['id'], result)

            # Continue loop - LLM will process results
            continue

        # No tool calls = agent is done
        self.conversation.add_assistant(response.text)

        return AgentResult(
            response=response.text,
            iterations=iteration,
            total_cost=self.tracker.get_total(),
            tool_calls_made=tool_calls_made,
            conversation=self.conversation.get_history()
        )

    # Max iterations reached
    return AgentResult(response="[Max iterations reached]", ...)
```

### Key Features

**1. Multi-Step Reasoning**
Agent can chain tools: "search files" → "read each" → "analyze" → "summarize"

**2. Safety Guard**
`max_iterations` prevents infinite loops (default: 10)

**3. Cost Tracking**
Every LLM call tracked with metadata (iteration number)

**4. Error Handling**
Tools return strings (errors included), LLM sees and can retry

**5. Observability**
Structured logging at each step (think, act, observe)

### Why This Design?

**Separation of concerns:**
- Agent orchestrates the loop
- Components handle specific tasks (conversation, tools, cost)
- Provider abstracts LLM API

**Composability:**
- Can swap any component
- Can extend Agent with subclasses
- Can customize behavior without editing Agent

---

## Layer 3: Components

### ConversationManager

**File:** `components/conversation.py` (92 lines)

**Purpose:** Manage message history in OpenAI format

**Interface:**
```python
manager = ConversationManager()

# Add messages
manager.add_user("Hello")
manager.add_assistant("Hi there!")
manager.add_tool_calls(text, tool_calls)
manager.add_tool_result(call_id, result)

# Retrieve
history = manager.get_history()  # List[Dict]

# Utilities
len(manager)        # Message count
manager.reset()     # Clear history
```

**Why separated:**
- Conversation format may change (Anthropic, Gemini formats differ)
- Easy to swap with database-backed version
- Testable in isolation

**Design:** Pure data structure - no side effects, just append to list.

---

### ToolExecutor

**File:** `components/executor.py` (102 lines)

**Purpose:** Execute tool calls with error handling

**Interface:**
```python
executor = ToolExecutor(registry)

# Execute single tool
result = executor.execute(tool_call)  # Returns string (success or error)

# Execute multiple
results = executor.execute_all(tool_calls)  # Returns List[Tuple[id, result]]
```

**Error Handling Philosophy:**

**Don't raise exceptions** - Return error messages as strings:

```python
def execute(self, tool_call):
    try:
        tool = registry.get(name)
        args = json.loads(tool_call['function']['arguments'])
        result = tool.execute(**args)
        return result
    except Exception as e:
        return f"Error executing {name}: {str(e)}"
```

**Why:** Agent (LLM) sees errors as observations, can retry or adjust strategy.

**Logging:**
```python
self.log.info("Executing tool", name=name, args=args)
self.log.error("Tool failed", name=name, error=str(e))
```

---

### CostTracker

**File:** `components/tracker.py` (72 lines)

**Purpose:** Accumulate API costs with metadata

**Interface:**
```python
tracker = CostTracker()

# Add costs
tracker.add(0.000042, metadata={"iteration": 1, "model": "llama-3.1"})
tracker.add(0.000038, metadata={"iteration": 2})

# Retrieve
total = tracker.get_total()             # Float
entries = tracker.get_entries()         # List with metadata
tracker.reset()                         # Clear
```

**Why separated:**
- Production systems need detailed cost tracking
- Can extend with budgets, alerts, quotas
- Metadata enables cost analysis (by iteration, model, etc.)

**Design:** Simple accumulator with optional metadata.

---

## Layer 4: Tool System

### ToolRegistry

**File:** `tool.py` (199 lines)

**Purpose:** Dynamic tool registration and discovery

**Interface:**
```python
registry = ToolRegistry()

# Register
registry.register(tool)                              # Tool object
registry.register_function(func, description)        # From function

# Retrieve
tool = registry.get("read_file")                     # Get by name
tools = registry.list_all()                          # All tools
names = registry.list_names()                        # Just names
schemas = registry.to_schemas()                      # OpenAI format

# Utilities
len(registry)                    # Count
"read_file" in registry          # Check existence
```

**Tool Class:**
```python
@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    parameters: Dict  # JSON schema

    @classmethod
    def from_function(cls, func, description=None):
        """Auto-create tool from function introspection."""
        schema = build_tool_schema(func)  # Inspect type hints
        return cls(
            name=func.__name__,
            description=description or func.__doc__,
            function=func,
            parameters=schema['function']['parameters']
        )

    def execute(self, **kwargs):
        """Call the underlying function."""
        return self.function(**kwargs)
```

**Decorator for convenience:**
```python
@tool("Analyze code for issues")
def analyze_code(file_path: str) -> str:
    # Implementation
    pass

# Later:
registry.register_function(analyze_code)
```

**Why This Design?**

**Extensibility without editing code:**
- Add tools dynamically
- No hardcoded imports
- Plugin-like architecture

**Auto-schema generation:**
- Introspect type hints
- Extract docstrings
- Generate OpenAI tool schemas

**Discoverability:**
- List all available tools
- Inspect tool metadata
- Generate documentation

---

## Layer 5: Provider Interface

**File:** `provider.py` (35 lines)

**Purpose:** Abstract LLM provider interface

**Interface:**
```python
class Provider(ABC):
    @abstractmethod
    def chat(self, messages, tools=None):
        """Send messages, get response."""
        pass

    @abstractmethod
    def get_cost(self, usage):
        """Calculate cost from usage."""
        pass
```

**Implementation:** `providers/groq.py` (121 lines)

```python
class GroqProvider(Provider):
    def __init__(self, model, system_instruction):
        self.client = Groq(api_key=...)
        self.model = model
        self.system_instruction = system_instruction

    def chat(self, messages, tools=None):
        # Add system instruction
        messages = [{"role": "system", "content": system_instruction}] + messages

        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools
        )

        return ChatResponse(text, tool_calls, usage)

    def get_cost(self, usage):
        # Calculate based on Groq pricing
        return (usage.prompt_tokens * rate_in) + (usage.completion_tokens * rate_out)
```

**Why abstraction?**

**Swappable LLM providers:**
- Groq → Anthropic → OpenAI
- Change one file, everything else works
- Test with mock provider

**Cost calculation encapsulated:**
- Each provider knows its pricing
- Agent doesn't care about pricing details

---

## Design Patterns Used

### 1. Facade Pattern (Bot)

**Intent:** Provide simple interface to complex subsystem

**Implementation:** Bot.chat() → Agent.run() → Components

**Benefit:** Users see simple API, complexity hidden

---

### 2. Strategy Pattern (Provider)

**Intent:** Define family of algorithms, make them interchangeable

**Implementation:** Provider interface, Groq/Anthropic/OpenAI implementations

**Benefit:** Swap LLM providers without changing Agent

---

### 3. Registry Pattern (ToolRegistry)

**Intent:** Central repository for objects, dynamic discovery

**Implementation:** Tools registered by name, retrieved dynamically

**Benefit:** Add tools at runtime, no code edits needed

---

### 4. Composition over Inheritance (Agent)

**Intent:** Assemble behavior from parts, not inheritance hierarchy

**Implementation:** Agent composes ConversationManager + ToolExecutor + CostTracker

**Benefit:** Mix and match components, easy to customize

---

### 5. Decorator Pattern (@tool)

**Intent:** Attach metadata to functions declaratively

**Implementation:** `@tool("description")` marks functions for registration

**Benefit:** Clean syntax, metadata co-located with function

---

## Data Flow

### Typical Request Flow

```
1. User calls bot.chat("Find Python files")

2. Bot → Agent.run()

3. Agent → ConversationManager.add_user()

4. Agent loop iteration 1:
   a. Agent → Provider.chat() → LLM
   b. LLM response: tool_calls=[{search_files, "*.py"}]
   c. Agent → ToolExecutor.execute(tool_call)
   d. ToolExecutor → ToolRegistry.get("search_files")
   e. ToolRegistry → Tool.execute(pattern="*.py")
   f. Tool → tools.search_files() → "app.py\ntest.py"
   g. Agent → ConversationManager.add_tool_result()
   h. Agent → CostTracker.add(cost=0.000028)

5. Agent loop iteration 2:
   a. Agent → Provider.chat() with tool results
   b. LLM response: "I found 2 Python files..."
   c. No tool calls → done

6. Agent → AgentResult(response, iterations=2, cost=0.000056)

7. Bot returns: ("I found 2 Python files...", 0.000056)
```

---

## File Organization

```
groqqy/
├── __init__.py              # Public exports (Groqqy, ToolRegistry, Agent, etc.)
│
├── bot.py                   # Layer 1: Public API
├── agent.py                 # Layer 2: Agentic loop
│
├── components/              # Layer 3: Composable components
│   ├── __init__.py
│   ├── conversation.py      # Message history
│   ├── executor.py          # Tool execution
│   └── tracker.py           # Cost tracking
│
├── tool.py                  # Layer 4: Tool system
├── tools.py                 # Built-in tools (read_file, etc.)
│
├── provider.py              # Layer 5: Provider interface
├── providers/
│   ├── __init__.py
│   └── groq.py              # Groq implementation
│
├── utils.py                 # Utilities (schema builder)
├── log.py                   # Logging setup
├── config.py                # Configuration (~/.groqqy/)
└── cli.py                   # Interactive CLI
```

**Dependency graph:**
```
bot.py → agent.py → {components/, provider.py, tool.py}
agent.py → No circular dependencies
components/ → No dependencies (pure data structures)
tool.py → utils.py (for schema generation)
tools.py → None (just functions)
```

**Clean architecture:** Dependencies flow in one direction, no cycles.

---

## Extension Points

### 1. Custom Components

Replace any component with custom version:

```python
class DatabaseConversationManager(ConversationManager):
    """Store conversation in database instead of memory."""

    def __init__(self, db_connection):
        self.db = db_connection

    def add_user(self, message):
        self.db.insert({"role": "user", "content": message})

    def get_history(self):
        return self.db.query("SELECT * FROM messages")

# Use it
agent = Agent(provider, tools)
agent.conversation = DatabaseConversationManager(db)
```

### 2. Custom Tools

Add domain-specific tools:

```python
def analyze_contracts(pdf_path: str) -> str:
    """Analyze legal contracts for key terms."""
    # Your implementation
    return "Analysis results..."

registry = ToolRegistry()
registry.register_function(analyze_contracts)
bot = Groqqy(tools=registry)
```

### 3. Custom Provider

Support other LLMs:

```python
class AnthropicProvider(Provider):
    def chat(self, messages, tools=None):
        # Call Anthropic API
        response = anthropic.messages.create(...)
        return ChatResponse(...)

    def get_cost(self, usage):
        # Anthropic pricing
        return usage.input_tokens * 0.003 / 1000

agent = Agent(AnthropicProvider(), tools, max_iterations=10)
```

### 4. Agent Subclasses

Add new capabilities:

```python
class PlanningAgent(Agent):
    """Agent with explicit planning phase before acting."""

    def run(self, prompt):
        # 1. Planning phase
        plan = self._create_plan(prompt)

        # 2. Execution phase
        for step in plan:
            result = super().run(step)

        return result

    def _create_plan(self, prompt):
        # LLM call to create plan
        pass
```

---

## Code Quality Metrics

### File Sizes (Lines of Code)

| File | LOC | Status |
|------|-----|--------|
| bot.py | 140 | ✅ Small |
| agent.py | 175 | ✅ Small |
| tool.py | 199 | ✅ Manageable |
| conversation.py | 92 | ✅ Very small |
| executor.py | 102 | ✅ Small |
| tracker.py | 72 | ✅ Very small |
| groq.py | 121 | ✅ Small |

**Target:** All files <200 lines ✅ Achieved

**Average:** 129 lines per file

### Complexity

**Cyclomatic complexity:** Low (mostly linear flows with one loop)

**Deepest nesting:** 4 levels (agent loop with error handling)

**Function sizes:** 3-20 lines average (small, focused)

### Dependencies

**External:** groq, loguru, click (3 total)

**Internal:** Clean one-way dependency graph, no cycles

### Test Coverage

**Architecture tests:** 6/6 passing
- Imports work
- Tool registry works
- Components work independently
- Bot creation works
- Code structure validated

**Config tests:** All passing

---

## Teaching Value

### Why This Architecture Is Good for Learning

**1. Readable:**
- Average function: 8 lines
- Clear variable names
- Explicit comments on pattern (THINK/ACT/OBSERVE)

**2. Structured:**
- Layers clearly separated
- Single responsibility evident
- Data flow is linear

**3. Extensible:**
- Extension points obvious
- Can modify one component without breaking others
- Patterns are clear (facade, strategy, composition)

**4. Production-ready:**
- Real logging (not print statements)
- Cost tracking (real economic concern)
- Error handling (graceful degradation)
- Safety guards (max_iterations)

### Recommended Learning Path

1. **Start:** `bot.py` - See the simple API
2. **Then:** `agent.py:run()` - Understand the agentic loop
3. **Next:** `tool.py` - See dynamic registration pattern
4. **Then:** `components/` - See single-responsibility components
5. **Finally:** Extend it - Add your own tool/component

**Time to understand:** 1-2 hours for basics, 1 day for deep dive

---

## Comparison to Other Frameworks

### vs. LangChain

| Aspect | Groqqy | LangChain |
|--------|--------|-----------|
| Core LOC | ~1200 | ~50,000+ |
| Abstraction layers | 3 | 8+ |
| Files to understand agents | 2 | 10+ |
| Customization | Subclass components | Complex callback system |
| Learning curve | 1-2 hours | 1-2 weeks |

**Groqqy advantage:** Simplicity, teaching-friendly

**LangChain advantage:** Feature-rich, ecosystem

---

### vs. AutoGPT

| Aspect | Groqqy | AutoGPT |
|--------|--------|---------|
| Agentic loop clarity | Explicit (88 lines) | Scattered across files |
| Tool system | Registry (dynamic) | Hardcoded + plugins |
| Extensibility | Very easy | Moderate |
| Production patterns | Yes | Yes |

**Groqqy advantage:** Clear structure, easy to modify

**AutoGPT advantage:** More features (memory, planning)

---

## Future Extensions (Potential)

### 1. Memory Component

```python
class MemoryManager:
    def store(self, key, value):
        """Persist across conversations."""
        pass

    def recall(self, query):
        """Retrieve relevant memories."""
        pass
```

### 2. Planning Module

```python
class Planner:
    def create_plan(self, goal):
        """Break goal into steps."""
        return ["step1", "step2", ...]
```

### 3. Multi-Agent System

```python
class AgentTeam:
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    def collaborate(self, task):
        """Agents work together."""
        pass
```

### 4. Streaming Responses

```python
def chat_stream(self, message):
    """Yield response tokens as they arrive."""
    for chunk in agent.run_stream(message):
        yield chunk
```

All achievable because of clean component architecture.

---

## Summary

**Groqqy v0.3.0 architecture achieves:**
- ✅ Clarity (small, focused files)
- ✅ Composability (mix and match components)
- ✅ Extensibility (easy to add features)
- ✅ Teaching value (clear patterns, real-world practices)
- ✅ Production readiness (logging, cost tracking, safety)

**Design philosophy: Simple parts → Complex behavior**

---

**For more details:**
- [README.md](README.md) - User guide
- [TEACHING_GUIDE.md](TEACHING_GUIDE.md) - Learning resources
- [AGENTIC_ARCHITECTURE_PROPOSAL.md](AGENTIC_ARCHITECTURE_PROPOSAL.md) - Design rationale
