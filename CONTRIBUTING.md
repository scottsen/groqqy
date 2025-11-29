# Contributing to Groqqy

Thanks for your interest in contributing to Groqqy! This document provides guidelines and instructions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Submitting Changes](#submitting-changes)
- [Releasing](#releasing)

## Code of Conduct

Be respectful, inclusive, and constructive. We're here to build great software together.

## Getting Started

### Prerequisites

- Python 3.8+
- Access to Groq API (get free key at https://console.groq.com)
- TIA system (for GroqProvider) or willing to adapt to standalone

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/groqqy.git
cd groqqy

# Install in development mode
pip install -e .

# Run examples to verify
python examples/basic_chat.py
```

## Development Workflow

### 1. Explore the Architecture

**Start here:**
```bash
# See the clean structure
reveal groqqy/bot.py

# Read the docs
cat ARCHITECTURE.md
cat DEVELOPMENT.md
```

**Key principle**: Every function should be 3-7 lines. If it's longer, break it down.

### 2. Making Changes

**Follow the pattern:**

```python
# ✅ Good - Single responsibility, 3-7 lines
def _add_user_message(self, message: str):
    """Add user message to conversation."""
    self.conversation.append({"role": "user", "content": message})

# ❌ Bad - Multiple responsibilities, too long
def process_message(self, message):
    # 50 lines of mixed concerns
    ...
```

**Sections:**
- Public API
- Conversation Management
- LLM Interaction
- Tool Execution
- Cost Tracking
- Setup Helpers

Add new functions to the appropriate section.

### 3. Adding Features

**Example: Adding streaming support**

1. Read `DEVELOPMENT.md` - streaming pattern is documented
2. Add new section:
   ```python
   # ========================================================================
   # Streaming Support
   # ========================================================================
   ```
3. Keep functions 3-7 lines
4. Update `ARCHITECTURE.md` with new data flow
5. Add example to `examples/`
6. Add tests

### 4. Testing

```bash
# Run tests
python -m pytest tests/

# Add new tests
# tests/test_your_feature.py
```

**Test structure:**
- Unit tests: Test individual functions
- Integration tests: Test layer boundaries
- End-to-end: Test full workflows

## Code Standards

### Python Style

- Follow PEP 8
- Use type annotations
- Write docstrings (especially for tools - LLM sees these!)
- Keep functions 3-7 lines
- Single responsibility per function

### Function Guidelines

```python
def function_name(self, param: str) -> str:
    """
    Clear description of what this does.

    Args:
        param: What this parameter is

    Returns:
        What gets returned
    """
    # Implementation (3-7 lines)
    pass
```

### Tool Guidelines

```python
def my_tool(param: str) -> str:
    """
    Tool description - be specific!
    LLM uses this to decide when to call.
    """
    try:
        # Implementation
        return "Success result"
    except Exception as e:
        # Return errors as strings
        return f"Error: {e}"
```

**Requirements:**
- Type annotations on all parameters
- Clear docstring (LLM-facing)
- Always return string (never raise)
- Handle errors gracefully

### Documentation

Update these when adding features:
- `README.md` - User-facing docs
- `ARCHITECTURE.md` - Design decisions, data flow
- `DEVELOPMENT.md` - Extension patterns, examples
- `CHANGELOG.md` - Track changes
- Code comments - Explain "why", not "what"

## Submitting Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow code standards above
- Keep commits atomic
- Write clear commit messages

### 3. Test

```bash
# Run all tests
python -m pytest tests/

# Check structure
reveal groqqy/bot.py

# Verify examples work
python examples/basic_chat.py
python examples/tool_usage.py
python examples/custom_tools.py
```

### 4. Document

- Update `CHANGELOG.md` under `[Unreleased]`
- Update relevant docs if needed
- Add code comments for complex logic

### 5. Submit Pull Request

**Good PR:**
- Clear title: "Add streaming support" not "Update bot.py"
- Description explains:
  - What changed
  - Why it changed
  - How to test it
- Links to related issues
- Small, focused changes

**PR Template:**

```markdown
## What Changed
Brief description of the feature/fix

## Why
Why was this needed?

## How to Test
1. Run `python examples/your_example.py`
2. Verify X happens
3. Check that Y works

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] All tests pass
- [ ] Code follows style guide (3-7 lines per function)
```

## Project Goals

**Groqqy aims to be:**
1. **Exemplary** - Clean code others can learn from
2. **Composable** - Easy to extend and customize
3. **Agent-friendly** - Structure visible via `reveal`
4. **Production-ready** - Real error handling, cost tracking
5. **Educational** - Well-documented patterns

**Not aiming to be:**
- A framework with every feature
- The fastest implementation
- The most clever code

**We value:**
- Clarity over cleverness
- Simplicity over features
- Readability over brevity
- Composition over inheritance

## Questions?

- Read `ARCHITECTURE.md` first
- Check `DEVELOPMENT.md` for patterns
- Look at `examples/` for usage
- Open an issue for discussion

## Recognition

Contributors will be added to:
- `CONTRIBUTORS.md`
- Release notes
- Project documentation

## Releasing

**Releases are fully automated** via GitHub Actions using PyPI Trusted Publishing.

### Quick Release

```bash
# Bump version in groqqy/__init__.py and setup.py
# Update CHANGELOG.md with changes

# Commit changes
git add groqqy/__init__.py setup.py CHANGELOG.md
git commit -m "chore: bump version to X.Y.Z"
git push origin main

# Create release (triggers auto-publish to PyPI)
gh release create vX.Y.Z \
  --title "vX.Y.Z - Description" \
  --notes "See CHANGELOG.md for details"

# Done! Package publishes to PyPI automatically
```

### How It Works

1. **Create GitHub Release** → Triggers workflow
2. **GitHub Actions** → Builds package
3. **PyPI Trusted Publishing** → Publishes (no tokens!)
4. **Users can install** → `pip install groqqy`

**Workflow:** `.github/workflows/publish.yml`

**Security:** Uses PyPI Trusted Publishing (OIDC) - no API tokens needed!

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `2.0.1`)
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes

**Examples:**
- `2.0.0` → `2.0.1` - Bug fix
- `2.0.1` → `2.1.0` - New feature (e.g., new tool type)
- `2.1.0` → `3.0.0` - Breaking API change

### Pre-Release Checklist

- [ ] Tests pass: `python -m pytest tests/`
- [ ] Examples work: `python examples/*.py`
- [ ] Version bumped in `groqqy/__init__.py` and `setup.py`
- [ ] CHANGELOG.md updated with changes
- [ ] Documentation reflects new features

### Troubleshooting

**See:** `.github/workflows/README.md` for detailed setup and troubleshooting.

**Common issues:**
- Trusted publishing not configured → See workflow README
- Build fails → Check GitHub Actions logs: `gh run list --limit 5`

Thank you for contributing! 🚀
