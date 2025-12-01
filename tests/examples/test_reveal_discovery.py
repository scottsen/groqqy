#!/usr/bin/env python3
"""
Quick test: Can Groqqy discover and use reveal?

Tests:
1. Groqqy reads reveal --agent-help
2. Groqqy understands when to use reveal
3. Groqqy actually uses reveal on code
"""

import os
from groqqy import Groqqy, ToolRegistry
from groqqy.tools import run_command

# Check for API key
if not os.environ.get('GROQ_API_KEY'):
    print("❌ GROQ_API_KEY not set")
    print("   Set it with: export GROQ_API_KEY='your-key'")
    exit(1)

# Minimal seed prompt
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
print("TEST: Can Groqqy Discover and Use reveal?")
print("=" * 70)
print()

# Create bot
registry = ToolRegistry()
registry.register_function(run_command)

bot = Groqqy(
    model="llama-3.1-8b-instant",
    tools=registry,
    system_instruction=SEED
)

# Test 1: Can groqqy learn about reveal?
print("TEST 1: Learning about reveal")
print("-" * 70)
response, cost = bot.chat("What is reveal? Check the --agent-help to learn about it.")
print(f"Groqqy: {response[:300]}...")
print(f"Cost: ${cost:.6f}")
print()

# Test 2: Does groqqy understand when to use it?
print("TEST 2: Understanding when to use reveal")
print("-" * 70)
response, cost = bot.chat("When should you use reveal instead of reading files directly?")
print(f"Groqqy: {response[:300]}...")
print(f"Cost: ${cost:.6f}")
print()

# Test 3: Can groqqy actually use reveal?
print("TEST 3: Using reveal on actual code")
print("-" * 70)
response, cost = bot.chat("Show me the structure of groqqy/bot.py using reveal")
print(f"Groqqy: {response[:500]}...")
print(f"Cost: ${cost:.6f}")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total cost: ${bot.total_cost:.6f}")
print(f"Messages: {len(bot.conversation)}")
print()

# Export the session
output_dir = os.environ.get('OUTPUT_DIR', '/output')
os.makedirs(output_dir, exist_ok=True)

md_path = os.path.join(output_dir, "reveal_discovery_session.md")
html_path = os.path.join(output_dir, "reveal_discovery_session.html")

bot.save_conversation(md_path)
bot.save_conversation(html_path)
print(f"✅ Session saved to {md_path}")
print(f"✅ Session saved to {html_path}")
print()
print("Review the exported files to see if groqqy:")
print("  1. Ran 'reveal --agent-help'")
print("  2. Learned from the output")
print("  3. Used reveal on actual code")
