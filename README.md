# Groqqy 🤖

**Simple general-purpose AI assistant powered by Groq**

Ultra-fast, ultra-cheap, and helpful. Groqqy is a conversational bot that can read files, run commands, search content, and more.

## Why Groqqy?

- ⚡ **Fast**: 460+ tokens/sec (11x faster than standard inference)
- 💰 **Cheap**: $0.00002-$0.00006 per interaction (300x cheaper than GPT-4)
- 🛠️ **Tool-capable**: Execute local tools (file ops, shell commands, search)
- 🗣️ **Conversational**: Maintains context across interactions

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

```python
from groqqy import Groqqy

bot = Groqqy()

# Simple conversation
response, cost = bot.chat("Hello! What can you do?")
print(response)
print(f"Cost: ${cost:.6f}")

# Use tools
response, cost = bot.chat("Find all .py files in the current directory")
print(response)

# Reset conversation
bot.reset()
```

## Built-in Tools

Groqqy comes with 4 essential tools:

1. **read_file(file_path)** - Read file contents
2. **run_command(command)** - Execute shell commands
3. **search_files(pattern, path=".")** - Find files by pattern
4. **search_content(query, path=".")** - Search text in files

## Custom Tools

Add your own tools by passing functions to Groqqy:

```python
def get_weather(city: str) -> str:
    """Get weather for a city."""
    # Your implementation
    return f"Weather in {city}: Sunny, 72°F"

bot = Groqqy(tools=[get_weather, read_file])
response, cost = bot.chat("What's the weather in SF?")
```

Tools must:
- Have type annotations for parameters
- Have a docstring (used as tool description)
- Return a string

## Cost Examples

Real costs from actual usage:

- Simple conversation: $0.000022
- Search files: $0.000028
- Run command: $0.000032
- Read file: $0.000058

**1,000 interactions: ~$0.03-$0.06** (vs $10-$100 with other providers)

## Models

Groqqy supports all Groq models:

```python
# Fast and cheap (default)
bot = Groqqy(model="llama-3.1-8b-instant")

# Fastest (460+ tok/sec)
bot = Groqqy(model="llama-4-scout")

# Best quality
bot = Groqqy(model="llama-3.3-70b-versatile")
```

## Requirements

- Python 3.8+
- Access to TIA's lib (for GroqProvider)
- Groq API key (set in TIA secrets or `GROQ_API_KEY` env var)

## Examples

See `examples/` directory for:
- Basic conversation
- Tool usage
- Custom tools
- Batch processing

## Architecture

```
groqqy/
├── __init__.py      # Package exports
├── bot.py           # Core Groqqy class
├── tools.py         # Built-in tools
└── cli.py           # Interactive CLI
```

## License

MIT

## Related

- [Groq API Docs](https://console.groq.com/docs)
- [TIA Groq Integration Guide](../../tia/docs/guides/GROQ_AGENTIC_POWERHOUSE_GUIDE.md)
- [GroqProvider Source](../../tia/lib/gemma/providers/groq_provider.py)

---

**Built with ❤️ using Groq's blazing-fast LPU inference**
