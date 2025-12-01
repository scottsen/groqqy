# Groqqy Examples

Hands-on examples demonstrating Groqqy's capabilities. All examples are self-contained and ready to run.

## Quick Start

```bash
# Navigate to examples directory
cd examples/

# Run any example
python basic_chat.py
python custom_tools.py
python export_conversation.py
```

**Requirements:** Set `GROQ_API_KEY` environment variable before running.

---

## Examples by Category

### 🎯 Getting Started

#### **basic_chat.py**
Simple conversation showing the basics of Groqqy.

**What you'll learn:**
- Creating a Groqqy bot
- Sending chat messages
- Getting responses and costs
- Resetting conversations

**Run:**
```bash
python basic_chat.py
```

---

### 🛠️ Tool Usage

#### **tool_usage.py**
Demonstrates built-in tools and agentic behavior.

**What you'll learn:**
- Using `read_file`, `search_files`, `search_content`, `run_command`
- Multi-step reasoning (agent chains tools automatically)
- Tool execution with error handling

**Run:**
```bash
python tool_usage.py
```

#### **custom_tools.py**
Creating and registering custom tools.

**What you'll learn:**
- Defining custom tools with `@tool` decorator
- Using `ToolRegistry` for advanced scenarios
- Passing functions directly to Groqqy
- Tool requirements (type hints, docstrings)

**Run:**
```bash
python custom_tools.py
```

---

### 📝 Conversation Export

#### **export_conversation.py**
Export conversations to markdown and HTML.

**What you'll learn:**
- Exporting to markdown format
- Exporting to styled HTML
- Saving to files with `save_conversation()`
- What gets included in exports (tool calls, results, etc.)

**Run:**
```bash
python export_conversation.py
# Outputs: example_chat.md and example_chat.html
```

**Output:**
- Clean markdown perfect for documentation
- Styled HTML with embedded CSS (purple gradient theme)
- Full tool call visibility (arguments + results)

---

### 🌐 Platform Tools & Web Search

#### **example_web_search.py**
Using Groq's platform tools for web access.

**What you'll learn:**
- Registering platform tools (`browser_search`)
- Compatible models for platform tools
- Hybrid strategy (mixing local + platform tools)
- Getting current information from the web

**Run:**
```bash
python example_web_search.py
```

**Note:** Requires compatible model (llama-3.3-70b-versatile or openai/gpt-oss-20b)

---

### 🎓 Self-Discovery & Advanced Patterns

#### **self_discovery_demo.py**
Autonomous tool learning via seed prompts.

**What you'll learn:**
- Self-discovery pattern (agent learns tools autonomously)
- Minimal seed prompts
- Tool discovery at runtime
- Meta-learning capabilities

**Run:**
```bash
python self_discovery_demo.py
```

**Concept:** Give agent a tiny seed prompt pointing to documentation, and it learns the tool autonomously by reading the docs itself.

#### **reveal_mvp_demo.py**
Integration with reveal-cli for code exploration.

**What you'll learn:**
- Self-discovery with real tools (reveal-cli)
- 11-line seed prompt enabling autonomous learning
- Token-efficient code exploration (10-150x reduction)
- Tool learning workflow

**Requirements:** `pip install reveal-cli`

**Run:**
```bash
python reveal_mvp_demo.py
```

---

## Example Output Samples

### Basic Chat
```
Creating a basic Groqqy bot...
Bot: Hello! I can help with various tasks...
Cost: $0.000022
```

### Custom Tools
```
Weather in San Francisco: Sunny, 72°F
Tip: $13.13, Total: $100.63
Agent automatically selected the right tools!
```

### Export Conversation
```
✅ Exported to example_chat.md (markdown)
✅ Exported to example_chat.html (html)

Open example_chat.html in your browser to see styled output!
```

---

## Best Practices

### Tool Definitions

**Good tool:**
```python
def get_weather(city: str, units: str = "fahrenheit") -> str:
    """Get current weather for a city.

    Args:
        city: City name (e.g., "San Francisco")
        units: Temperature units ("fahrenheit" or "celsius")

    Returns:
        Weather description with temperature
    """
    # Implementation
    return f"Weather in {city}: Sunny, 72°{units[0].upper()}"
```

**Why it's good:**
- Clear type hints (required)
- Descriptive docstring (LLM uses this)
- Default values for optional params
- Returns string (LLM can read it)

### Error Handling

**Good error handling:**
```python
def read_config(file_path: str) -> str:
    """Read configuration file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Config file not found: {file_path}"
    except PermissionError:
        return f"Error: Permission denied: {file_path}"
```

**Why:** Return error messages instead of raising exceptions—agent can see errors and adapt.

### Cost Tracking

```python
bot = Groqqy()

# Track costs per interaction
response1, cost1 = bot.chat("First query")
response2, cost2 = bot.chat("Second query")

# Get total cost
total = bot.total_cost()
print(f"Total session cost: ${total:.6f}")
```

---

## Common Patterns

### Multi-Step Reasoning

```python
bot = Groqqy()

# Agent will automatically chain tools:
response, cost = bot.chat(
    "Find all Python files in src/, read them, "
    "count the total lines, and tell me the average"
)

# Behind the scenes:
# 1. search_files("*.py", "src/")
# 2. read_file("src/file1.py")
# 3. read_file("src/file2.py")
# 4. [counts lines]
# 5. [calculates average]
# 6. Returns summary
```

### Progressive Tasks

```python
bot = Groqqy()

# Start simple
bot.chat("What files are in the current directory?")

# Build on previous context
bot.chat("Read the README file")

# Continue building
bot.chat("Summarize the installation steps")

# Export the whole conversation
bot.save_conversation("project_exploration.md")
```

### Tool Composition

```python
from groqqy import Groqqy, ToolRegistry

# Mix built-in and custom tools
registry = ToolRegistry()
registry.register_function(analyze_code)
registry.register_function(run_tests)
# Built-in tools (read_file, etc.) are included by default

bot = Groqqy(tools=registry)

# Agent can use all tools
response, cost = bot.chat(
    "Analyze main.py for issues, fix them, then run tests"
)
```

---

## Troubleshooting

### "No module named 'groqqy'"

Install groqqy first:
```bash
pip install -e .  # From groqqy root directory
```

### "GROQ_API_KEY not found"

Set your API key:
```bash
export GROQ_API_KEY="your-key-here"
```

Or add to `~/.bashrc` / `~/.zshrc` for persistence.

### "Model does not support tool calling"

Use a compatible model:
```python
bot = Groqqy(model="llama-3.3-70b-versatile")  # Best
bot = Groqqy(model="llama-3.1-8b-instant")     # Fast
```

### Platform tools not working

Platform tools require specific models:
```python
# For browser_search:
bot = Groqqy(model="llama-3.3-70b-versatile")  # Recommended
# or
bot = Groqqy(model="openai/gpt-oss-20b")
```

---

## Contributing Examples

Have a cool example? Add it!

**Guidelines:**
1. Self-contained (single file)
2. Clear docstring explaining what it demonstrates
3. Error handling (fail gracefully)
4. Comments for complex logic
5. Update this README with description

**Example template:**
```python
"""
Groqqy Example: [Feature Name]

Demonstrates: [What this shows]
Requires: [Special dependencies if any]

Run: python example_name.py
"""

from groqqy import Groqqy

def main():
    # Your example code
    bot = Groqqy()
    response, cost = bot.chat("Example query")
    print(response)
    print(f"Cost: ${cost:.6f}")

if __name__ == "__main__":
    main()
```

---

## Next Steps

After exploring examples:

1. **Read the docs:**
   - [docs/USER_GUIDE.md](../docs/USER_GUIDE.md) - Comprehensive guide
   - [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - How it works
   - [docs/TEACHING_GUIDE.md](../docs/TEACHING_GUIDE.md) - Learning path

2. **Build something:**
   - Start with `basic_chat.py` as a template
   - Add your own tools
   - Create a specialized agent

3. **Share:**
   - Export conversations to document your agent's behavior
   - Contribute examples back to the project
   - Share on GitHub Discussions

---

**Happy building! 🤖**
