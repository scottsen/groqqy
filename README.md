# Groqqy 🤖

**Clean, composable micro agentic bot powered by Groq**

Ultra-fast, ultra-cheap, and truly agentic. Groqqy is a multi-step reasoning agent that can read files, run commands, search content, and chain tool calls to complete complex tasks.

## Why Groqqy?

- ⚡ **Fast**: 460+ tokens/sec (11x faster than standard inference)
- 💰 **Cheap**: $0.00002-$0.00006 per interaction (300x cheaper than GPT-4)
- 🧠 **Agentic**: Multi-step reasoning loop (THINK → ACT → OBSERVE)
- 🛠️ **Tool-capable**: Execute local tools with automatic chaining
- 🧩 **Composable**: Mix and match components (Agent, Tools, Memory, etc.)
- 📚 **Teaching-friendly**: Clean, readable code perfect for learning agentic AI

## What's New in v0.3.0

**Major Architecture Refactor** - Transformed from single-turn assistant to true micro agentic bot:

- ✅ **Agentic Loop**: Multi-step reasoning (think/act/observe pattern)
- ✅ **Tool Registry**: Dynamic tool registration - add custom tools without code edits
- ✅ **Composable Components**: ConversationManager, ToolExecutor, CostTracker
- ✅ **49% Smaller**: Bot.py reduced from 277 → 140 lines
- ✅ **Extensible**: All components <200 lines, easy to customize

See [CHANGELOG.md](CHANGELOG.md) for full details.

## Installation

```bash
cd ~/src/projects/groqqy
pip install -e .
```

## Quick Start

### Interactive Chat

```bash
python -m groqqy.cli
```

Or use the convenience script:

```bash
./groqqy
```

### Programmatic Use

**Basic usage** (same API as before):

```python
from groqqy import Groqqy

bot = Groqqy()

# Simple conversation
response, cost = bot.chat("Hello! What can you do?")
print(response)
print(f"Cost: ${cost:.6f}")

# Use tools (agent will chain them as needed)
response, cost = bot.chat("Find all .py files and count the lines in each")
print(response)  # Agent will: search → read each file → count → report

# Reset conversation
bot.reset()
```

**Advanced usage** (new in v0.3.0):

```python
from groqqy import Groqqy, ToolRegistry

# Create custom tool registry
registry = ToolRegistry()

def analyze_sentiment(text: str) -> str:
    """Analyze sentiment of text."""
    # Your implementation
    return "Positive sentiment detected"

registry.register_function(analyze_sentiment)

# Create bot with custom tools and settings
bot = Groqqy(
    model="llama-3.3-70b-versatile",
    tools=registry,
    max_iterations=20,  # Allow more complex reasoning
    system_instruction="You are a helpful code analyst"
)

response, cost = bot.chat("Analyze the sentiment of README.md")
```

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────┐
│           Bot (Simple API)              │
│  chat() ──► Agent.run()                 │
│  reset() ──► Agent.reset()              │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────▼──────────┐
        │       Agent        │
        │  (Agentic Loop)    │
        │  THINK→ACT→OBSERVE │
        └─────────┬──────────┘
                  │
      ┌───────────┼───────────┬──────────────┐
      │           │           │              │
      ▼           ▼           ▼              ▼
┌──────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│Conversat-│ │  Tool  │ │   Cost   │ │ Provider │
│ion Mgr   │ │Executor│ │ Tracker  │ │  (LLM)   │
└──────────┘ └────┬───┘ └──────────┘ └──────────┘
                  │
                  ▼
            ┌──────────────┐
            │ToolRegistry  │
            │ (extensible) │
            └──────────────┘
```

### Agentic Loop (THINK → ACT → OBSERVE)

The heart of Groqqy is the multi-step reasoning loop in `agent.py`:

```
User: "Find Python files and count their lines"
    │
    ▼
┌───────────────┐
│  THINK (LLM)  │ ──► "I need to search for .py files first"
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  ACT (Tool)   │ ──► execute: search_files("*.py")
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  OBSERVE      │ ──► "Found: app.py, test.py, main.py"
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  THINK (LLM)  │ ──► "Now I need to read each file and count lines"
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  ACT (Tools)  │ ──► execute: read_file("app.py"), read_file("test.py"), ...
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  OBSERVE      │ ──► "app.py: 150 lines, test.py: 89 lines, ..."
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  THINK (LLM)  │ ──► "I have all the data, I'll summarize"
└───────┬───────┘
        │
        ▼
┌───────────────────────────────┐
│  Response: "Found 3 Python   │
│  files with a total of 289    │
│  lines: app.py (150), ..."    │
└───────────────────────────────┘
```

This pattern follows the **ReAct** framework (Yao et al., 2022) and enables true agentic behavior.

### File Structure

```
groqqy/
├── __init__.py              # Package exports
├── bot.py (140 lines)       # Simple facade over Agent
├── agent.py (175 lines)     # Agentic loop (THINK/ACT/OBSERVE)
├── tool.py (199 lines)      # Tool registry system
├── tools.py (77 lines)      # Built-in tools (read, search, run)
├── cli.py (141 lines)       # Interactive CLI
├── config.py (116 lines)    # Configuration system (~/.groqqy/)
├── log.py (117 lines)       # Logging (loguru + JSONL)
├── provider.py (35 lines)   # Provider interface
├── utils.py (73 lines)      # Tool schema builder
│
├── components/              # Composable components
│   ├── conversation.py      # Message history manager
│   ├── executor.py          # Tool execution with error handling
│   └── tracker.py           # Cost tracking
│
└── providers/               # LLM providers
    └── groq.py              # Groq provider implementation
```

**Key Design Principles:**
- All files <200 lines
- Single responsibility per component
- Easy to understand and modify
- Production-ready patterns

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed component descriptions.

## Built-in Tools

Groqqy comes with 4 essential tools:

1. **read_file(file_path: str)** - Read file contents
2. **run_command(command: str)** - Execute shell commands (secure)
3. **search_files(pattern: str, path: str)** - Find files by pattern
4. **search_content(query: str, path: str)** - Search text in files

All tools use `shlex.quote()` for security (prevents shell injection).

## Custom Tools

### Simple Approach (Pass Functions)

```python
from groqqy import Groqqy

def get_weather(city: str) -> str:
    """Get weather for a city."""
    # Your implementation
    return f"Weather in {city}: Sunny, 72°F"

def calculate_tip(bill: float, percent: float = 15.0) -> str:
    """Calculate tip amount."""
    tip = bill * (percent / 100)
    return f"Tip: ${tip:.2f}, Total: ${bill + tip:.2f}"

# Just pass functions - auto-registration!
bot = Groqqy(tools=[get_weather, calculate_tip])
response, cost = bot.chat("What's the weather in SF?")
```

### Advanced Approach (Tool Registry)

```python
from groqqy import Groqqy, ToolRegistry

# Create registry
registry = ToolRegistry()

# Define tools
def analyze_code(file_path: str) -> str:
    """Analyze Python code for issues."""
    # Your implementation
    return "Analysis: 3 issues found..."

def run_tests(test_pattern: str) -> str:
    """Run tests matching pattern."""
    # Your implementation
    return "Tests passed: 15/15"

# Register with custom descriptions
registry.register_function(analyze_code, "Static analysis tool")
registry.register_function(run_tests, "Test runner")

# Inspect registry
print(f"Available tools: {registry.list_names()}")
print(f"Total tools: {len(registry)}")

# Use in bot
bot = Groqqy(tools=registry)
```

**Tool Requirements:**
- Type annotations for all parameters
- Docstring (used as tool description for LLM)
- Return type: `str` (LLM sees the output)
- Handle errors gracefully (return error message, don't raise)

See `examples/custom_tools.py` for complete examples.

## Configuration

Groqqy supports persistent configuration via `~/.groqqy/`:

```bash
~/.groqqy/
├── boot.md              # System instructions (loaded on startup)
└── knowledge/           # Additional context files
    ├── domain_info.md
    └── api_docs.txt
```

**CLI options:**

```bash
# Interactive mode (loads boot.md)
groqqy

# Single-shot mode
groqqy --prompt "What's 15 * 23?"

# With context files
groqqy --context docs.md --context api.txt -p "Explain the API"

# Skip boot.md
groqqy --no-boot

# Custom model
groqqy --model llama-3.3-70b-versatile
```

**Programmatic configuration:**

```python
bot = Groqqy(
    model="llama-3.1-8b-instant",
    tools=my_tools,
    max_iterations=20,
    system_instruction="You are a code analyst specialized in Python"
)
```

## Cost Examples

Real costs from actual usage:

- Simple conversation: $0.000022
- Search files: $0.000028
- Run command: $0.000032
- Read file: $0.000058
- **Multi-step task** (3 tool calls): ~$0.000120

**1,000 interactions: ~$0.03-$0.12** (vs $10-$100 with other providers)

## Models

Groqqy supports all Groq models:

```python
# Fast and cheap (default)
bot = Groqqy(model="llama-3.1-8b-instant")

# Fastest (460+ tok/sec)
bot = Groqqy(model="llama-4-scout")

# Best quality
bot = Groqqy(model="llama-3.3-70b-versatile")

# Mixture of experts
bot = Groqqy(model="mixtral-8x7b-32768")
```

## Advanced Usage

### Component Composition

For advanced users who want to customize behavior:

```python
from groqqy import Agent, ToolRegistry, ConversationManager, ToolExecutor, CostTracker
from groqqy.providers import GroqProvider

# Create custom components
provider = GroqProvider(model="llama-3.3-70b-versatile")
registry = ToolRegistry()
registry.register_function(my_custom_tool)

# Compose custom agent
agent = Agent(
    provider=provider,
    tools=registry,
    max_iterations=50  # More complex reasoning
)

# Run directly
result = agent.run("Complex multi-step task")
print(result.response)
print(f"Iterations: {result.iterations}")
print(f"Tool calls: {result.tool_calls_made}")
print(f"Cost: ${result.total_cost:.6f}")
```

### Custom Components

Extend components with custom behavior:

```python
from groqqy.components import ToolExecutor

class CachingExecutor(ToolExecutor):
    """Tool executor with result caching."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}

    def execute(self, tool_call):
        # Create cache key
        key = (tool_call['function']['name'],
               tool_call['function']['arguments'])

        # Check cache
        if key in self.cache:
            return self.cache[key]

        # Execute and cache
        result = super().execute(tool_call)
        self.cache[key] = result
        return result

# Use in agent
from groqqy import Agent
agent = Agent(provider, tools, executor=CachingExecutor(tools))
```

## Examples

See `examples/` directory:

- **basic_chat.py** - Simple conversation
- **custom_tools.py** - Adding custom tools
- **tool_usage.py** - Tool calling patterns

## Teaching & Learning

Groqqy is designed as a **teaching kernel for agentic AI**. The codebase is:

- **Readable**: All files <200 lines, clear intent
- **Well-structured**: Clean separation of concerns
- **Pedagogical**: Comments explain THINK/ACT/OBSERVE pattern
- **Production-ready**: Real patterns (logging, cost tracking, safety)

**For educators and learners**, see:
- [TEACHING_GUIDE.md](TEACHING_GUIDE.md) - How to use Groqqy to learn/teach agentic AI
- [ARCHITECTURE.md](ARCHITECTURE.md) - Deep dive into component design
- [AGENTIC_ARCHITECTURE_PROPOSAL.md](AGENTIC_ARCHITECTURE_PROPOSAL.md) - Design philosophy

**Key concepts demonstrated:**
- ReAct pattern (Thought → Action → Observation)
- Tool calling and execution
- Multi-step reasoning
- Dynamic tool registration
- Composable architecture
- Production safety (max iterations, error handling, cost tracking)

## Requirements

- Python 3.8+
- Groq API key (set `GROQ_API_KEY` env var)
- Dependencies: `requests`, `loguru` (auto-installed via pip)

## License

MIT

## Related

- [Groq API Docs](https://console.groq.com/docs)
- [ReAct Paper](https://arxiv.org/abs/2210.03629) (Yao et al., 2022)
- [LangChain](https://python.langchain.com/) - Production agentic framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Graph-based agents

## Version History

- **v0.3.0** (2025-11-28) - Agentic architecture refactor (multi-step reasoning)
- **v0.2.0** (2025-11-28) - Configuration system + security fixes
- **v0.1.0** (2025-11-27) - Initial standalone release

---

**Built with ❤️ using Groq's blazing-fast LPU inference**

**Perfect for:** Learning agentic AI, rapid prototyping, cost-conscious automation, teaching AI agents
