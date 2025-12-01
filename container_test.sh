#!/bin/bash
# Build and test Groqqy in podman container

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           Groqqy Container Test Suite                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo

# Configuration
IMAGE_NAME="groqqy-test"
CONTAINER_NAME="groqqy-test-run"
OUTPUT_DIR="./test_output_container"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Step 1: Build
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Building container image..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
podman build -t "$IMAGE_NAME" -f Containerfile .
echo "✅ Build complete"
echo

# Step 2: Run tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Running tests in container..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
podman run --rm \
    --name "$CONTAINER_NAME" \
    -v "$(pwd)/$OUTPUT_DIR:/test_output:z" \
    "$IMAGE_NAME" \
    python test_container.py

EXIT_CODE=$?

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Test outputs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$OUTPUT_DIR/test_conversation.md" ]; then
    echo "✅ Markdown export created: $OUTPUT_DIR/test_conversation.md"
    echo "   Size: $(wc -c < "$OUTPUT_DIR/test_conversation.md") bytes"
else
    echo "❌ Markdown export not found"
fi

if [ -f "$OUTPUT_DIR/test_conversation.html" ]; then
    echo "✅ HTML export created: $OUTPUT_DIR/test_conversation.html"
    echo "   Size: $(wc -c < "$OUTPUT_DIR/test_conversation.html") bytes"
else
    echo "❌ HTML export not found"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed!"
    echo
    echo "Output files in: $OUTPUT_DIR/"
    echo "View HTML: open $OUTPUT_DIR/test_conversation.html"
else
    echo "⚠️  Some tests failed (exit code: $EXIT_CODE)"
    echo "Check the output above for details"
fi

echo
exit $EXIT_CODE
