# reveal-cli Seed Prompt (MVP)

Add this to `~/.groqqy/boot.md`:

```markdown
## reveal-cli

You have access to `reveal` - a semantic code exploration tool.

**When to use**: BEFORE reading any code file, use reveal to see structure first (10-150x token reduction).

**Learn more**: Run `reveal --agent-help` to see the full agent guide.

**Basic pattern**:
```bash
reveal file.py              # See structure (50 tokens vs 7,500)
reveal file.py func_name    # Extract specific function
```

**Rule**: Never read full code files without checking structure with reveal first.
```

That's it! The agent will:
1. See `reveal --agent-help` in the prompt
2. Run it when it needs to understand reveal
3. Get the full guide from the --agent-help output
4. Learn autonomously from there

The --agent-help output already contains everything needed!
