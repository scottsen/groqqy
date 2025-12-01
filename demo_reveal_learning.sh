#!/bin/bash
# Demo: Groqqy learns to use reveal in a fresh container

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     Groqqy Self-Discovery Demo: Learning reveal-cli             ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo

# Check for API key
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY not set"
    echo "   Set it with: export GROQ_API_KEY='your-key'"
    exit 1
fi

# Configuration
IMAGE_NAME="groqqy-test"
OUTPUT_DIR="./reveal_learning_output"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if image exists, build if not
if ! podman image exists "$IMAGE_NAME"; then
    echo "Building container image..."
    podman build -t "$IMAGE_NAME" -f Containerfile .
    echo "✅ Build complete"
    echo
fi

# Run the learning demo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting Groqqy Learning Session"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Groqqy will:"
echo "  1. Learn about reveal from --agent-help"
echo "  2. Understand when to use it"
echo "  3. Use reveal on actual code"
echo "  4. Export the learning session"
echo

podman run --rm \
    --name groqqy-reveal-demo \
    -v "$(pwd)/$OUTPUT_DIR:/output:z" \
    -e GROQ_API_KEY="$GROQ_API_KEY" \
    -e OUTPUT_DIR="/output" \
    "$IMAGE_NAME" \
    python test_reveal_simple.py

EXIT_CODE=$?

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Demo completed successfully!"
    echo

    if [ -f "$OUTPUT_DIR/reveal_learning_simple.md" ]; then
        echo "📄 Markdown export:"
        echo "   $OUTPUT_DIR/reveal_learning_simple.md"
        echo "   Size: $(wc -c < "$OUTPUT_DIR/reveal_learning_simple.md") bytes"
        echo
    fi

    if [ -f "$OUTPUT_DIR/reveal_learning_simple.html" ]; then
        echo "🎨 HTML export:"
        echo "   $OUTPUT_DIR/reveal_learning_simple.html"
        echo "   Size: $(wc -c < "$OUTPUT_DIR/reveal_learning_simple.html") bytes"
        echo
        echo "View it:"
        echo "   open $OUTPUT_DIR/reveal_learning_simple.html"
        echo
    fi

    echo "This conversation shows:"
    echo "  ✓ Groqqy running 'reveal --agent-help'"
    echo "  ✓ Groqqy learning from the output"
    echo "  ✓ Groqqy using reveal on actual code"
    echo "  ✓ Full tool calls and results preserved"
else
    echo "⚠️  Demo failed (exit code: $EXIT_CODE)"
    echo "Check the output above for details"
fi

echo
exit $EXIT_CODE
