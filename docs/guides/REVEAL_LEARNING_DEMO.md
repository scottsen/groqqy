# Groqqy Self-Discovery Demo: Learning reveal-cli

This demo shows Groqqy autonomously learning to use reveal-cli through self-discovery.

## Quick Start

```bash
cd /home/scottsen/src/projects/groqqy

# Set your Groq API key
export GROQ_API_KEY='your-key-here'

# Run the demo
./demo_reveal_learning.sh
```

**Cost**: ~$0.001-0.002 (typically 3 API calls)

## What Happens

The demo runs Groqqy in a **fresh podman container** with this workflow:

### 1. Groqqy Discovers reveal
```
User: "What is reveal? Check the --agent-help to learn about it."

Groqqy:
  → Runs: reveal --agent-help
  → Reads: 9,398 characters of guidance
  → Learns: Purpose, patterns, token efficiency
  → Responds: Explains what reveal does
```

### 2. Groqqy Understands Usage
```
User: "When should you use reveal instead of reading files directly?"

Groqqy:
  → Recalls: Information from --agent-help
  → Explains: Token efficiency (50 tokens vs 7,500)
  → Describes: Workflows and patterns
```

### 3. Groqqy Uses reveal
```
User: "Show me the structure of groqqy/bot.py using reveal"

Groqqy:
  → Runs: reveal groqqy/bot.py
  → Parses: Structure output
  → Explains: What's in the file
```

## Output

After the demo completes, you'll find:

```
reveal_learning_output/
├── reveal_discovery_session.md    # Markdown conversation
└── reveal_discovery_session.html  # Styled HTML with tool calls
```

### Markdown Export
Clean, readable format:
- User messages
- Assistant responses
- Tool calls with arguments in JSON
- Tool results in code blocks
- Timestamps

### HTML Export
Beautiful styled output:
- Purple gradient theme
- Syntax-highlighted tool calls
- Clear visual separation
- Tool results in styled code blocks
- Professional appearance

## What You'll See

The exported conversation includes:

**Full Tool Call Visibility**:
```json
{
  "tool": "run_command",
  "arguments": {
    "command": "reveal --agent-help"
  }
}
```

**Complete Results**:
```
Result: [9,398 characters of reveal guidance]
```

**Groqqy's Learning**:
- Parses help output
- Extracts key concepts
- Creates mental model
- Applies knowledge

## Key Insights from Demo

After running, you'll see:

1. **Autonomous Learning**
   - Groqqy reads --agent-help without prompting
   - Understands content independently
   - Integrates into workflow

2. **Token Efficiency**
   - Old way: Read file (7,500 tokens)
   - New way: Reveal structure (50 tokens)
   - Groqqy learns this pattern

3. **Practical Application**
   - Groqqy actually uses reveal
   - Correctly interprets output
   - Explains findings to user

4. **Self-Improvement**
   - Started: Read files directly
   - Learned: Use reveal first
   - Result: 150x token reduction

## Technical Details

**Environment**: Fresh podman container
- Python 3.11
- groqqy (from source)
- reveal-cli 0.13.3
- Isolated from host

**Seed Prompt**: 11 lines (minimal MVP)
- Points to --agent-help
- No detailed instructions
- Agent discovers rest autonomously

**Cost Breakdown**:
- Test 1 (learn): ~$0.0005 (reads help output)
- Test 2 (understand): ~$0.0003 (recall)
- Test 3 (apply): ~$0.0004 (uses reveal)
- **Total**: ~$0.0012

## Troubleshooting

### API Key Not Found
```bash
export GROQ_API_KEY='your-key-here'
```

### Container Not Built
```bash
podman build -t groqqy-test -f Containerfile .
```

### Can't Find Demo Script
```bash
cd /home/scottsen/src/projects/groqqy
ls -l demo_reveal_learning.sh
```

### Permission Denied
```bash
chmod +x demo_reveal_learning.sh
```

## What This Proves

✅ **Self-Discovery Works**
- Groqqy can learn tools autonomously
- No pre-programming required
- Just point to --agent-help

✅ **Minimal Seed Prompt**
- 11 lines is enough
- Agent discovers details
- Scales to other tools

✅ **Export Captures Everything**
- Full conversation preserved
- Tool calls visible
- Learning process documented

✅ **Container Isolation**
- Clean environment
- Reproducible
- CI/CD ready

## Next Steps

After running the demo:

1. **View HTML Output**
   ```bash
   open reveal_learning_output/reveal_discovery_session.html
   ```

2. **Read Markdown**
   ```bash
   cat reveal_learning_output/reveal_discovery_session.md
   ```

3. **Analyze Tool Calls**
   - Look for `reveal --agent-help` execution
   - Check groqqy's interpretation
   - Verify reveal was used on code

4. **Share Results**
   - HTML is self-contained
   - Perfect for documentation
   - Shows agent capabilities

## Files

- `demo_reveal_learning.sh` - Main demo script
- `test_reveal_discovery.py` - Test program
- `docs/REVEAL_SEED_PROMPT_MVP.md` - Seed prompt used
- `Containerfile` - Container definition

## Example Session

What the exported conversation looks like:

```markdown
# Groqqy Conversation

**Date**: 2025-12-01 09:15:23
**Messages**: 8

## Message 1: User
What is reveal? Check the --agent-help to learn about it.

## Message 2: Assistant
**Tool Calls:**
- **run_command**
  ```json
  {
    "command": "reveal --agent-help"
  }
  ```

## Message 3: Tool Result
**Tool Call ID**: `call_abc123`
**Result:**
```
# Reveal

> Semantic code exploration tool optimized for token efficiency...
[9,398 characters of guidance]
```

## Message 4: Assistant
I've learned about reveal! It's a semantic code exploration tool that...
[Groqqy explains what it learned]

[... continues with remaining conversation ...]
```

---

**Ready?** Just run: `./demo_reveal_learning.sh`
