# Self-Discovery Boot Snippet
# Add this to ~/.groqqy/boot.md to enable self-discovery

---

## Self-Discovery Protocol

You can learn new tools autonomously using this 5-step pattern:

### 1. INSTALL
```bash
pip install <tool-name>
```

### 2. DISCOVER
```bash
<tool> --help              # Basic usage
<tool> --agent-help        # Agent guide (if available)
<tool> --agent-help-full   # Full guide (if available)
```

### 3. LEARN
Parse help output and understand:
- What it does (purpose)
- When to use it (triggers)
- How to use it (commands)
- Where it fits (integration)

### 4. INTEGRATE
Create decision rules:
- When to use this vs alternatives
- How to combine with existing tools
- Token efficiency impact
- Workflow changes

### 5. DOCUMENT
Generate summary:
- Tool overview
- Key capabilities
- Integration rules
- Example workflows

---

## reveal-cli: Pre-Loaded Knowledge

**Purpose**: Semantic code exploration (10-150x token reduction)

**Core Pattern**: Explore → Navigate → Focus
```bash
reveal file.py              # Structure (50 tokens)
reveal file.py --outline    # Hierarchy (100 tokens)
reveal file.py func_name    # Extract (70 tokens)
```

**Integration Rules**:
- BEFORE reading code → Use reveal first (see structure)
- AFTER finding files → Use reveal to navigate
- FOR large files (>300 lines) → Use --head/--tail/--range
- WHEN reviewing code → Use --check for quality
- WITH search results → Reveal before reading

**Common Commands**:
```bash
reveal src/                     # Directory tree
reveal file.py                  # Show structure + metrics
reveal file.py --outline        # Hierarchical view (classes → methods)
reveal file.py function_name    # Extract specific element
reveal file.py --check          # Code quality checks
reveal file.py --head 10        # First 10 functions
reveal file.py --tail 5         # Last 5 functions
```

**Pipeline Integration**:
```bash
git diff --name-only | reveal --stdin
find src/ -name "*.py" | reveal --stdin --check
```

**Token Efficiency**:
- Old: Read 500-line file = 7,500 tokens
- New: Reveal structure (50) + extract (70) = 120 tokens
- **Result: 62x reduction**

**Decision Tree**:
```
Need to understand code?
├─ Unknown file → reveal file.py (structure first!)
├─ Need function → reveal file.py func (extract it)
├─ Multiple files → find/git | reveal --stdin
├─ Quality check → reveal file.py --check
├─ Large file → reveal --head N (progressive)
└─ Full content needed → Read tool (AFTER structure)
```

**Key Rule**: NEVER read full code files without checking structure with reveal first!

---

## Self-Discovery Triggers

Automatically enter self-discovery mode when user says:
- "learn about X"
- "install and learn X"
- "update yourself with X"
- "can you use X?" (if unknown)

**Process**:
1. Actually install (don't simulate!)
2. Actually read help (don't imagine!)
3. Parse real output
4. Create real integration rules
5. Generate real documentation

---

## reveal-cli Workflow Examples

### Exploring Unknown Code
```bash
# User: "What's in auth.py?"
reveal auth.py                    # See structure
reveal auth.py authenticate       # Extract specific function
```

### Code Review
```bash
# User: "Review the changes"
git diff --name-only | reveal --stdin --check
reveal modified_file.py --check --select B,S    # Bugs & Security
```

### Large File Navigation
```bash
# User: "What's at the end of utils.py?"
reveal utils.py --tail 5          # Last 5 functions (bugs often here!)
```

### Finding Complexity
```bash
# User: "Find complex code"
reveal src/app.py --check --select C    # Complexity checks
```

---

## Token Optimization Strategy

**Old Approach** (inefficient):
```
1. Read entire file (7,500 tokens)
2. Extract what's needed
3. Answer question
```

**New Approach** (optimized):
```
1. Reveal structure (50 tokens)
2. Identify target
3. Extract specific code (70 tokens)
4. Answer question

SAVINGS: 98.4% token reduction!
```

**Impact on Context Window**:
- Old: 10 files = 75,000 tokens (context overflow!)
- New: 10 files = 1,200 tokens (comfortable)
- **Can handle 62x more files in same context**

---

## Integration with Tools

### With run_command
```python
# Explore before reading
run_command("reveal src/auth.py")
# Parse structure, identify target
run_command("reveal src/auth.py authenticate")
# Now read only what's needed
```

### With search_files
```python
# Find files
run_command("find src/ -name '*.py'")
# Explore each efficiently
run_command("find src/ -name '*.py' | reveal --stdin")
```

### With git commands
```python
# What changed?
run_command("git diff --name-only")
# Quick structure review
run_command("git diff --name-only | reveal --stdin --outline")
```

---

## Success Metrics

✅ Can explain reveal purpose in one sentence
✅ Can list 5 key use cases
✅ Can show command examples
✅ Can explain token efficiency impact
✅ Can integrate into existing workflows
✅ **Uses reveal BEFORE reading files**

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Unknown file | `reveal file.py` |
| Hierarchy | `reveal file.py --outline` |
| Extract | `reveal file.py name` |
| Quality | `reveal file.py --check` |
| Directory | `reveal src/` |
| Large file | `reveal file.py --head 10` |
| Pipeline | `cmd \| reveal --stdin` |

---

**Remember**: Structure first, then extract. Never read blindly!
