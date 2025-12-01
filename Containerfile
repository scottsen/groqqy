# Containerfile for Groqqy Testing
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy groqqy code
COPY . /app/

# Install groqqy and dependencies
RUN pip install --no-cache-dir -e .

# Install reveal-cli for self-discovery tests
RUN pip install --no-cache-dir reveal-cli

# Create test directory
RUN mkdir -p /test_output

# Set environment variable for test output
ENV TEST_OUTPUT_DIR=/test_output

# Default command: run tests
CMD ["python", "-m", "pytest", "-v"]
