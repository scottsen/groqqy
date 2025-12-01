#!/usr/bin/env python3
"""
Minimal demo: Groqqy learns reveal from --agent-help
"""

from groqqy import Groqqy, ToolRegistry
from groqqy.tools import run_command

# Minimal seed prompt - just enough to trigger self-discovery
SEED_PROMPT = """You are Groqqy, a helpful assistant.

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


def main():
    print("Minimal Self-Discovery Demo")
    print("=" * 60)

    # Create bot with minimal seed
    registry = ToolRegistry()
    registry.register_function(run_command)

    bot = Groqqy(
        model="llama-3.1-8b-instant",
        tools=registry,
        system_instruction=SEED_PROMPT
    )

    # Test: Agent should use reveal --agent-help to learn
    print("\n1. Asking about reveal...")
    response, _ = bot.chat("What's reveal and how do I use it? Check the --agent-help.")
    print(f"Groqqy: {response[:200]}...")

    # Test: Agent should now use reveal
    print("\n2. Asking to explore code...")
    response, _ = bot.chat("Show me the structure of groqqy/bot.py using reveal")
    print(f"Groqqy: {response[:200]}...")

    print(f"\n✅ Total cost: ${bot.total_cost:.6f}")

    # Export
    bot.save_conversation("reveal_learning.html")
    print("✅ Saved to reveal_learning.html")


if __name__ == "__main__":
    main()
