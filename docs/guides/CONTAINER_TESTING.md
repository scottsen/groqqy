# Container Testing Guide

Test Groqqy's new features in an isolated podman container.

## Quick Start

### Run Automated Tests
```bash
./container_test.sh
```

This will:
1. Build the container image
2. Run all tests (export + reveal integration)
3. Save output to `test_output_container/`

**Expected output:**
```
✅ PASS: Conversation Export
✅ PASS: reveal-cli Integration
✅ PASS: Bot Export Integration

🎉 All tests passed!
```

### Interactive Testing
```bash
./container_interactive.sh
```

Inside the container, try:
```bash
# Test export
python test_container.py

# Test reveal
reveal groqqy/bot.py
reveal --agent-help

# Test examples
python examples/reveal_mvp_demo.py
python test_export.py

# Run groqqy CLI (requires GROQ_API_KEY)
groqqy
```

## What Gets Tested

### Test 1: Conversation Export
- ✅ Markdown export
- ✅ HTML export with styling
- ✅ File saving
- ✅ Tool call preservation

### Test 2: reveal-cli Integration
- ✅ reveal installation
- ✅ reveal --help
- ✅ reveal --agent-help (self-discovery)
- ✅ reveal on actual code

### Test 3: Bot Integration
- ✅ Export methods exist
- ✅ Correct signatures
- ✅ API compatibility

## Manual Testing

### Build Only
```bash
podman build -t groqqy-test -f Containerfile .
```

### Run Specific Test
```bash
podman run --rm groqqy-test python test_container.py
```

### With API Key (for full groqqy testing)
```bash
podman run --rm \
    -e GROQ_API_KEY="your-key-here" \
    groqqy-test \
    python examples/reveal_mvp_demo.py
```

### Mount Output Directory
```bash
mkdir -p ./test_output_container
podman run --rm \
    -v $(pwd)/test_output_container:/test_output:z \
    groqqy-test \
    python test_container.py
```

## Output Files

After running `./container_test.sh`, check:

```bash
ls -lh test_output_container/

# View markdown
cat test_output_container/test_conversation.md

# View HTML (open in browser)
open test_output_container/test_conversation.html
```

## Troubleshooting

### Container build fails
```bash
# Check podman is installed
podman --version

# Clean old images
podman rmi groqqy-test
```

### Tests fail
```bash
# Check logs
podman logs groqqy-test-run

# Run interactively to debug
./container_interactive.sh
```

### reveal not found
```bash
# Verify it's in the container
podman run --rm groqqy-test which reveal
podman run --rm groqqy-test reveal --version
```

## CI/CD Integration

This setup works great for CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Test in container
  run: |
    podman build -t groqqy-test -f Containerfile .
    podman run --rm groqqy-test python test_container.py
```

## Clean Up

```bash
# Remove test image
podman rmi groqqy-test

# Remove test outputs
rm -rf test_output_container/
```

## What This Tests

✅ **Export Feature**:
- ConversationExporter works
- Markdown format correct
- HTML format correct with CSS
- Tool calls preserved
- File I/O works

✅ **Self-Discovery**:
- reveal-cli installs correctly
- --agent-help output available
- Integration with groqqy possible
- Code exploration works

✅ **Isolation**:
- No dependency on host system
- Reproducible environment
- Clean testing
- Easy CI/CD integration

---

**Quick Commands:**

```bash
# Full test suite
./container_test.sh

# Interactive exploration
./container_interactive.sh

# View results
cat test_output_container/test_conversation.md
open test_output_container/test_conversation.html
```
