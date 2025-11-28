# Groqqy Architecture

**Clean, composable tool-calling bot kernel**

## Design Principles

This codebase follows the [TIA Python Development Guide](../../tia/docs/guides/TIA_PYTHON_DEVELOPMENT_GUIDE.md) principles:

1. **Clarity over cleverness** - Readable beats smart
2. **Composability first** - Small, pure, reusable functions
3. **Single responsibility** - One job per function (3-7 lines ideal)
4. **Separation of concerns** - Clear boundaries between layers
5. **Agent-friendly** - Structure visible via `reveal`

## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                    Public API                        │
│  chat() - Orchestrate full interaction               │
│  reset() - Clear conversation                        │
└────────────┬────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌──────────┐
│  LLM    │◄─────┤  Conv    │
│  Layer  │      │  Mgmt    │
└────┬────┘      └──────────┘
     │
     ▼
┌─────────────┐
│  Tool       │
│  Execution  │
└─────────────┘
```

## Core Components

### 1. Public API (2 functions)

**Purpose**: User-facing interface

```python
chat(user_message: str) -> tuple[str, float]
  ├─ Orchestrates: conversation → LLM → tools → response
  └─ Returns: (response_text, cost)

reset()
  └─ Clears: conversation history + cost tracking
```

**Design**: Simple, obvious interface. All complexity hidden.

---

### 2. Conversation Management (4 functions)

**Purpose**: Maintain message history in OpenAI format

```python
_add_user_message(message)           # 3 lines
_add_assistant_message(message)      # 3 lines
_add_assistant_with_tool_calls(...)  # 7 lines
_add_tool_result(id, result)         # 7 lines
```

**Responsibility**: Pure data transformation - append to list

**Why separated**: Conversation format may change (e.g., Anthropic format). Isolated here = easy swap.

---

### 3. LLM Interaction (3 functions)

**Purpose**: Call LLM, handle tool-calling loop

```python
_get_response_with_tools()           # 6 lines
  ├─ Calls LLM
  ├─ Checks for tool calls
  └─ Executes tools if needed

_call_llm()                          # 5 lines
  └─ Single LLM API call + cost calculation

_execute_tools_and_retry()           # 6 lines
  ├─ Add tool calls to conversation
  ├─ Execute all tools
  └─ Retry LLM for final answer
```

**Flow**:
```
User message
    ↓
Call LLM
    ↓
Tool calls? ──No──→ Return response
    ↓ Yes
Execute tools
    ↓
Call LLM again
    ↓
Return final response
```

**Design**: Clean separation of concerns. Each function does ONE thing.

---

### 4. Tool Execution (5 functions)

**Purpose**: Execute function calls from LLM

```python
_execute_all_tools(tool_calls)       # 5 lines
  └─ Loop: execute each → add result

_execute_single_tool(tool_call)      # 6 lines
  ├─ Parse: name + args
  ├─ Find tool
  └─ Execute or return error

_find_tool(name)                     # 3 lines
  └─ Lookup tool by name

_call_tool(tool, args)               # 6 lines
  └─ Execute with error handling

_tool_not_found(name)                # 3 lines
  └─ Error message
```

**Error handling**: All errors return strings (not exceptions). LLM sees errors and can retry/adjust.

**Design**: Pure functions - no side effects except conversation updates.

---

### 5. Cost Tracking (1 function)

**Purpose**: Track total spend

```python
_track_cost(cost)                    # 3 lines
  └─ Add to running total
```

**Why separate**: Future expansion (budgets, rate limiting, per-tool costs).

---

### 6. Setup Helpers (3 functions)

**Purpose**: Configuration and initialization

```python
_create_provider(model)              # 6 lines
_system_instruction()                # 5 lines
_default_tools()                     # 3 lines
```

**Why separate**: Easy to customize per bot instance.

---

## Data Flow

```
User: "Read README.md"
    ↓
chat("Read README.md")
    ├─ _add_user_message("Read README.md")
    │   └─ conversation = [{"role": "user", "content": "..."}]
    │
    ├─ _get_response_with_tools()
    │   ├─ _call_llm()
    │   │   └─ Returns: Response(tool_calls=[{read_file, args}])
    │   │
    │   └─ _execute_tools_and_retry(response)
    │       ├─ _add_assistant_with_tool_calls(...)
    │       ├─ _execute_all_tools([...])
    │       │   └─ _execute_single_tool(...)
    │       │       ├─ _find_tool("read_file")
    │       │       ├─ _call_tool(read_file, {"file_path": "README.md"})
    │       │       │   └─ Returns: "# Groqqy..."
    │       │       └─ _add_tool_result(id, result)
    │       │
    │       └─ _call_llm()  # Get final answer
    │           └─ Returns: Response("The README explains...")
    │
    ├─ _add_assistant_message("The README explains...")
    ├─ _track_cost(0.000058)
    └─ Return: ("The README explains...", 0.000058)
```

## Extension Points

### Adding New Tools

```python
def my_tool(param: str) -> str:
    """Tool description for LLM."""
    return f"Result: {param}"

bot = Groqqy(tools=[my_tool, read_file])
```

**Requirements**:
- Type annotations on parameters
- Docstring (becomes tool description)
- Return string

### Custom Provider

Replace `GroqProvider` in `_create_provider()`:

```python
def _create_provider(self, model: str):
    return MyProvider(model=model, system=self._system_instruction())
```

### Custom Conversation Format

Override conversation management functions:

```python
def _add_user_message(self, message: str):
    # Anthropic format example
    self.conversation.append({
        "role": "user",
        "content": [{"type": "text", "text": message}]
    })
```

### Middleware / Hooks

Add between layers:

```python
def _get_response_with_tools(self) -> Response:
    response = self._call_llm()
    response = self._apply_middleware(response)  # ← Hook
    if response.tool_calls:
        response = self._execute_tools_and_retry(response)
    return response
```

## Testing Strategy

### Unit Tests (per function)

```python
def test_add_user_message():
    bot = Groqqy()
    bot._add_user_message("hello")
    assert bot.conversation[-1] == {"role": "user", "content": "hello"}
```

### Integration Tests (layer boundaries)

```python
def test_tool_execution():
    bot = Groqqy(tools=[mock_tool])
    result = bot._execute_single_tool(mock_tool_call)
    assert result == "expected output"
```

### End-to-End Tests (full flow)

```python
def test_chat_with_tools():
    bot = Groqqy()
    response, cost = bot.chat("Read file.txt")
    assert "contents" in response
    assert cost > 0
```

## Why This Architecture?

### Composability
Each function is a building block. Swap, replace, extend.

### Visibility
`reveal bot.py` shows clean structure:
- 19 functions, all 3-7 lines
- Clear section headers
- Single responsibility evident

### Extensibility
Want streaming? Add `_stream_response()`.
Want caching? Add `_check_cache()` before `_call_llm()`.
Want parallel tools? Modify `_execute_all_tools()`.

### Maintainability
Bug in tool execution? Look in "Tool Execution" section.
Need to change LLM format? "LLM Interaction" section.
Clean boundaries = easy debugging.

### Agent-Friendly
AI agents can navigate this:
1. `reveal bot.py` → See structure
2. `reveal bot.py chat` → See orchestration
3. `reveal bot.py _execute_tools_and_retry` → See implementation

No 70-line functions to wade through.

## Performance

**Token Efficiency**: Each function small = only load what's needed for changes.

**Execution**: No performance overhead - Python function calls are cheap.

**Memory**: Conversation grows linearly. Add truncation in `_add_*` functions if needed.

## Future Enhancements

Possible additions (all isolated to specific sections):

- **Streaming**: Add `_stream_response()` in LLM Interaction
- **Caching**: Add `_check_cache()` before LLM calls
- **Retry logic**: Wrap `_call_llm()` with backoff
- **Rate limiting**: Add to `_call_llm()`
- **Parallel tools**: Modify `_execute_all_tools()` with asyncio
- **Tool middleware**: Hook in `_call_tool()`
- **Conversation pruning**: Add to `_add_*` functions
- **Multi-turn limits**: Add counter in `chat()`
- **Cost budgets**: Expand `_track_cost()`
- **Telemetry**: Add logging in each section

Each enhancement = modify 1-2 functions. No ripple effects.

---

**This is how you build a kernel**: Simple, clean, composable. Ready to grow.
