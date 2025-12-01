# Quick Start: New Groqqy Features

## 1. Conversation Export

**Save your conversations to markdown or HTML!**

### Programmatic
```python
from groqqy import Groqqy

bot = Groqqy()
bot.chat("Hello!")
bot.chat("What can you do?")

# Export
markdown = bot.export_markdown()
html = bot.export_html()

# Save to file
bot.save_conversation("chat.md")       # markdown
bot.save_conversation("chat.html")     # HTML with styling
```

### Interactive
```bash
$ groqqy

You: Hello!
Groqqy: Hi there!

You: export markdown my_chat.md
✅ Conversation exported to my_chat.md

You: export html styled_chat.html
✅ Conversation exported to styled_chat.html
```

### CLI Flag
```bash
# Auto-save on exit (format auto-detected from extension)
groqqy --export conversation.md
groqqy --export conversation.html

# With single prompt
groqqy --prompt "Explain quantum computing" --export output.html
```

**Features:**
- 📝 Clean markdown with code blocks for tool calls
- 🎨 Styled HTML with purple gradient theme
- 🔧 Shows all tool calls + results
- 📅 Includes timestamp and message count

---

## 2. reveal-cli Integration (Self-Discovery)

**Teach Groqqy to explore code efficiently (10-150x token reduction)!**

### Setup (One-Time)

Add this to `~/.groqqy/boot.md`:

```markdown
## reveal-cli

You have access to `reveal` - a semantic code exploration tool.

**When to use**: BEFORE reading code files, use reveal to see structure first (10-150x token reduction).

**Learn more**: Run `reveal --agent-help` to see the full agent guide.

**Basic pattern**:
```bash
reveal file.py              # See structure (50 tokens vs 7,500)
reveal file.py func_name    # Extract specific function
```

**Rule**: Never read full code files without checking structure with reveal first.
```

### Usage

```bash
$ groqqy

You: What's in bot.py?
Groqqy: [runs: reveal bot.py]
        I see 3 main classes and 8 functions...

You: Show me the Groqqy class
Groqqy: [runs: reveal bot.py Groqqy]
        Here's the Groqqy class definition...
```

**Token Impact:**
- Old way: Read full file = 7,500 tokens
- New way: Reveal structure = 50 tokens
- **150x reduction!**

---

## Quick Test

### Test Export
```bash
cd /home/scottsen/src/projects/groqqy
python test_export.py
open /tmp/test_conversation.html
```

### Test Self-Discovery
```bash
cd /home/scottsen/src/projects/groqqy
python examples/reveal_mvp_demo.py
open reveal_learning.html
```

---

## Documentation

- **Export Details**: `GROQQY_CONVERSATION_EXPORT_SUMMARY.md` (in session)
- **Self-Discovery MVP**: `docs/REVEAL_SEED_PROMPT_MVP.md`
- **Full Session Summary**: `sessions/bionic-edge-1201/SESSION_SUMMARY.md`

---

## Examples

All examples in `/home/scottsen/src/projects/groqqy/examples/`:
- `export_conversation.py` - Export usage patterns
- `reveal_mvp_demo.py` - Self-discovery demo (MVP)

---

That's it! Two powerful features in minimal code. 🚀
