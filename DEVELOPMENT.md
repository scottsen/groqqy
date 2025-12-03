# Groqqy Development Guide

**How to extend and customize the Groqqy kernel**

## Table of Contents

1. [Quick Start](#quick-start)
2. [Adding Custom Tools](#adding-custom-tools)
3. [Creating Bot Variants](#creating-bot-variants)
4. [Advanced Patterns](#advanced-patterns)
5. [Testing](#testing)
6. [Best Practices](#best-practices)

---

## Quick Start

### Development Setup

```bash
cd ~/src/projects/groqqy

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run examples
python examples/basic_chat.py
```

### Project Structure

```
groqqy/
├── groqqy/              # Core package
│   ├── bot.py          # Main bot (178 lines, 19 functions)
│   ├── tools.py        # Built-in tools
│   ├── cli.py          # Interactive interface
│   └── __init__.py     # Exports
├── examples/            # Usage examples
├── tests/               # Test suite
├── ARCHITECTURE.md      # Design document
└── DEVELOPMENT.md       # This file
```

### Using reveal

Explore the codebase structure:

```bash
reveal groqqy/              # Package overview
reveal groqqy/bot.py        # See all functions (3-7 lines each)
reveal groqqy/bot.py chat   # See specific function
```

---

## Adding Custom Tools

### Simple Tool

```python
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your implementation
    return f"Weather in {city}: Sunny, 72°F"

from groqqy import Groqqy
bot = Groqqy(tools=[get_weather])
```

**Requirements**:
1. ✅ Type annotations on parameters
2. ✅ Docstring (LLM sees this)
3. ✅ Return string

### Tool with Multiple Parameters

```python
def calculate_distance(lat1: float, lon1: float,
                      lat2: float, lon2: float) -> str:
    """Calculate distance between two coordinates in miles."""
    # Haversine formula
    from math import radians, cos, sin, asin, sqrt

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    miles = 3956 * c

    return f"Distance: {miles:.2f} miles"

bot = Groqqy(tools=[calculate_distance])
response, cost = bot.chat("How far is SF (37.77, -122.41) from LA (34.05, -118.24)?")
```

### Tool with Optional Parameters

```python
def search_web(query: str, num_results: int = 5) -> str:
    """Search the web and return results."""
    # Implementation
    return f"Found {num_results} results for: {query}"
```

**Note**: Optional parameters have defaults. LLM may omit them.

### Tool with Error Handling

```python
def read_database(user_id: int) -> str:
    """Fetch user data from database."""
    try:
        # Database call
        data = db.get_user(user_id)
        return f"User: {data['name']}, Email: {data['email']}"
    except Exception as e:
        # Return error as string (LLM sees it)
        return f"Database error: {str(e)}"
```

**Pattern**: Always return string, never raise exceptions. Let LLM handle errors.

---

## Creating Bot Variants

### Specialized Bot

```python
# code_reviewer_bot.py

from groqqy import Groqqy
import subprocess

def run_linter(file_path: str) -> str:
    """Run linter on a file and return issues."""
    result = subprocess.run(['pylint', file_path],
                          capture_output=True, text=True)
    return result.stdout

def get_git_diff() -> str:
    """Get current git diff."""
    result = subprocess.run(['git', 'diff'],
                          capture_output=True, text=True)
    return result.stdout

class CodeReviewer(Groqqy):
    """Bot specialized for code review."""

    def __init__(self):
        super().__init__(
            model="llama-3.3-70b-versatile",  # Better for code
            tools=[run_linter, get_git_diff]
        )

    def _system_instruction(self) -> str:
        return """You are a code reviewer. Analyze code for:
        - Bugs and errors
        - Performance issues
        - Security vulnerabilities
        - Code style violations
        Provide constructive feedback."""

# Usage
reviewer = CodeReviewer()
response, cost = reviewer.chat("Review the current changes")
```

### Multi-Tool Bot

```python
# research_bot.py

from groqqy import Groqqy
from groqqy.tools import read_file, search_files, search_content

def fetch_url(url: str) -> str:
    """Fetch and return webpage content."""
    import requests
    response = requests.get(url)
    return response.text[:5000]  # Truncate

def query_database(sql: str) -> str:
    """Execute SQL query and return results."""
    # Your DB logic
    return "Results..."

class ResearchBot(Groqqy):
    """Bot with access to files, web, and database."""

    def __init__(self):
        tools = [
            # File tools
            read_file, search_files, search_content,
            # Web tools
            fetch_url,
            # Data tools
            query_database
        ]
        super().__init__(
            model="llama-3.1-8b-instant",
            tools=tools
        )
```

### Cost-Optimized Bot

```python
class BudgetBot(Groqqy):
    """Bot with cost limits."""

    def __init__(self, max_cost=0.10):
        super().__init__()
        self.max_cost = max_cost

    def chat(self, user_message: str) -> tuple[str, float]:
        if self.total_cost >= self.max_cost:
            return f"Budget exceeded (${self.total_cost:.6f})", 0.0

        response, cost = super().chat(user_message)

        if self.total_cost > self.max_cost:
            return "Budget limit reached mid-conversation", cost

        return response, cost
```

---

## Advanced Patterns

### Streaming Responses

```python
class StreamingGroqqy(Groqqy):
    """Bot with streaming support."""

    def stream_chat(self, user_message: str):
        """Stream response chunks."""
        self._add_user_message(user_message)

        # Assuming provider supports streaming
        for chunk in self.provider.stream(
            messages=self.conversation,
            tools=self.tools
        ):
            yield chunk.text

        # Handle tool calls if needed
        # ... (similar to _get_response_with_tools)
```

### Conversation Pruning

```python
class PrunedGroqqy(Groqqy):
    """Bot that limits conversation history."""

    def __init__(self, max_messages=20):
        super().__init__()
        self.max_messages = max_messages

    def _add_user_message(self, message: str):
        super()._add_user_message(message)
        self._prune_if_needed()

    def _prune_if_needed(self):
        """Keep only recent messages."""
        if len(self.conversation) > self.max_messages:
            # Keep system + last N messages
            self.conversation = self.conversation[-self.max_messages:]
```

### Tool Middleware

```python
class LoggedGroqqy(Groqqy):
    """Bot that logs all tool executions."""

    def _call_tool(self, tool, args):
        print(f"🔧 Executing: {tool.__name__}({args})")
        result = super()._call_tool(tool, args)
        print(f"✅ Result: {result[:100]}...")
        return result
```

### Parallel Tool Execution

```python
from concurrent.futures import ThreadPoolExecutor

class ParallelGroqqy(Groqqy):
    """Execute multiple tools in parallel."""

    def _execute_all_tools(self, tool_calls):
        """Execute tools concurrently."""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self._execute_single_tool, tc)
                for tc in tool_calls
            ]

            for tc, future in zip(tool_calls, futures):
                result = future.result()
                self._add_tool_result(tc['id'], result)
```

### Retry Logic

```python
class RobustGroqqy(Groqqy):
    """Bot with automatic retries."""

    def _call_llm(self):
        """Call LLM with exponential backoff."""
        import time

        for attempt in range(3):
            try:
                return super()._call_llm()
            except Exception as e:
                if attempt == 2:
                    raise
                wait = 2 ** attempt
                print(f"Retry in {wait}s...")
                time.sleep(wait)
```

---

## Testing

### Unit Tests

```python
# tests/test_conversation.py

import pytest
from groqqy import Groqqy

def test_add_user_message():
    bot = Groqqy()
    bot._add_user_message("hello")

    assert len(bot.conversation) == 1
    assert bot.conversation[0]["role"] == "user"
    assert bot.conversation[0]["content"] == "hello"

def test_reset():
    bot = Groqqy()
    bot.conversation = [{"role": "user", "content": "test"}]
    bot.total_cost = 0.5

    bot.reset()

    assert len(bot.conversation) == 0
    assert bot.total_cost == 0.0
```

### Tool Tests

```python
# tests/test_tools.py

from groqqy.tools import read_file
import tempfile

def test_read_file():
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        path = f.name

    result = read_file(path)
    assert result == "test content"
```

### Integration Tests

```python
# tests/test_integration.py

from groqqy import Groqqy

def mock_tool(param: str) -> str:
    """Mock tool for testing."""
    return f"Result: {param}"

def test_chat_with_mock_tool():
    bot = Groqqy(tools=[mock_tool])

    # This would call real LLM - consider mocking provider
    # For now, test structure
    assert bot.tools[0] == mock_tool
```

---

## Best Practices

### 1. Keep Functions Small

✅ **Good** (3-7 lines):
```python
def _find_tool(self, name: str) -> Callable:
    """Find tool by name."""
    return next((t for t in self.tools if t.__name__ == name), None)
```

❌ **Bad** (70 lines):
```python
def chat(self, message):
    # 70 lines of mixed concerns
    # ... add message
    # ... call LLM
    # ... execute tools
    # ... handle errors
    # ... format response
```

### 2. Single Responsibility

Each function does ONE thing:
- `_add_user_message`: Append to list
- `_call_llm`: Make API call
- `_execute_single_tool`: Run one tool

Not multiple things.

### 3. Pure Functions Where Possible

```python
# Pure - no side effects
def _find_tool(self, name: str) -> Callable:
    return next((t for t in self.tools if t.__name__ == name), None)

# Impure - modifies state (unavoidable for conversation)
def _add_user_message(self, message: str):
    self.conversation.append(...)
```

Prefer pure. When impure is needed, isolate it.

### 4. Type Annotations

```python
# Good
def chat(self, user_message: str) -> tuple[str, float]:
    ...

# Bad
def chat(self, user_message):
    ...
```

Helps IDEs, agents, and future developers.

### 5. Clear Naming

```python
# Good
def _execute_tools_and_retry(self, response: Response) -> Response:
    ...

# Bad
def _process(self, r):
    ...
```

Name says what it does.

### 6. Error Handling in Tools

Tools return strings (never raise):
```python
def risky_operation(param: str) -> str:
    try:
        result = dangerous_call(param)
        return f"Success: {result}"
    except Exception as e:
        return f"Error: {e}"
```

Let LLM see and handle errors.

### 7. Docstrings for Tools

```python
def my_tool(param: str) -> str:
    """
    What this tool does - LLM sees this!

    Be specific: "Search database for user by email"
    Not vague: "Search"
    """
    ...
```

LLM decides when to use based on docstring.

### 8. Use reveal

Before committing, check structure:
```bash
reveal groqqy/bot.py
```

All functions 3-7 lines? ✅
Clear separation? ✅
Single responsibility evident? ✅

---

## Common Patterns

### Adding a New Layer

Want to add caching? Create new section:

```python
# ========================================================================
# Caching Layer
# ========================================================================

def _check_cache(self, message: str) -> Optional[str]:
    """Check if response is cached."""
    return self.cache.get(message)

def _save_to_cache(self, message: str, response: str):
    """Save response to cache."""
    self.cache[message] = response
```

Then hook into `chat()`:
```python
def chat(self, user_message: str) -> tuple[str, float]:
    cached = self._check_cache(user_message)
    if cached:
        return cached, 0.0

    # ... existing flow

    self._save_to_cache(user_message, response.text)
    return response.text, response.cost
```

### Custom Response Format

Override `_call_llm()`:
```python
def _call_llm(self) -> Response:
    """Call LLM and parse custom format."""
    response = self.provider.chat(
        messages=self.conversation,
        tools=self.tools,
        response_format={"type": "json_object"}
    )

    # Parse JSON response
    data = json.loads(response.text)
    text = data.get("answer", "")

    cost = self.provider.get_cost(response.usage)
    return Response(text=text, cost=cost, tool_calls=response.tool_calls)
```

---

## Resources

- **Architecture**: See `ARCHITECTURE.md` for design details
- **Examples**: See `examples/` for usage patterns
- **Groq API Docs**: https://console.groq.com/docs
- **Tool Calling Guide**: https://console.groq.com/docs/tool-use

---

**Remember**: The goal is clean, composable code that's easy to understand, modify, and extend. Every function should be obvious. If it's not, break it down further.
