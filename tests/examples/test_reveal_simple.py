#!/usr/bin/env python3
"""
Simple test: Groqqy learns and uses reveal
"""

import os
from groqqy import Groqqy, ToolRegistry
from groqqy.tools import run_command

if not os.environ.get('GROQ_API_KEY'):
    print("❌ GROQ_API_KEY not set")
    exit(1)

SEED = """You are Groqqy, a helpful assistant.

You have access to `reveal` - a semantic code exploration tool.

**When to use**: BEFORE reading code files, use reveal to see structure first (10-150x token reduction).

**Learn more**: Run `reveal --agent-help` to see the full agent guide.

**Basic pattern**:
```bash
reveal file.py              # See structure (50 tokens vs 7,500)
reveal file.py func_name    # Extract specific function
```

**Rule**: Never read full code files without checking structure with reveal first.
"""

print("=" * 70)
print("Groqqy Learning reveal-cli")
print("=" * 70)
print()

registry = ToolRegistry()
registry.register_function(run_command)

bot = Groqqy(
    model="llama-3.3-70b-versatile",  # Better at tool calls
    tools=registry,
    system_instruction=SEED
)

# Single comprehensive test
print("TEST: Complete reveal discovery and usage")
print("-" * 70)
response, cost = bot.chat("""
I want you to demonstrate your knowledge of reveal:

1. First, check reveal --agent-help to learn about it
2. Then show me the structure of groqqy/bot.py using reveal
3. Finally, explain what you learned

Be concise in your responses.
""")

print(f"Groqqy: {response}")
print()
print(f"Cost: ${cost:.6f}")
print(f"Total cost: ${bot.total_cost:.6f}")
print()

# Export
output_dir = os.environ.get('OUTPUT_DIR', '/output')
os.makedirs(output_dir, exist_ok=True)

md_path = os.path.join(output_dir, "reveal_learning_simple.md")
html_path = os.path.join(output_dir, "reveal_learning_simple.html")

bot.save_conversation(md_path)
bot.save_conversation(html_path)

print(f"✅ Saved to {md_path}")
print(f"✅ Saved to {html_path}")
print()
print("Review the HTML to see:")
print("  - reveal --agent-help execution")
print("  - reveal groqqy/bot.py execution")
print("  - Groqqy's learning and explanation")
