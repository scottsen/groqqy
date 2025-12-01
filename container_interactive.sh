#!/bin/bash
# Interactive groqqy shell in container

set -e

IMAGE_NAME="groqqy-test"

echo "Starting interactive Groqqy container..."
echo "You'll have access to:"
echo "  - groqqy CLI"
echo "  - reveal-cli"
echo "  - Python with all dependencies"
echo

# Build if needed
if ! podman image exists "$IMAGE_NAME"; then
    echo "Building image first..."
    podman build -t "$IMAGE_NAME" -f Containerfile .
fi

# Run interactive shell
podman run --rm -it \
    --name groqqy-interactive \
    -v "$(pwd):/app:z" \
    -e GROQ_API_KEY="${GROQ_API_KEY}" \
    "$IMAGE_NAME" \
    /bin/bash

echo "Container exited."
