"""
Tools that Groqqy can use
"""

import subprocess
from pathlib import Path


def read_file(file_path: str) -> str:
    """Read and return contents of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def run_command(command: str) -> str:
    """Execute a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors: {result.stderr}"
        return output
    except Exception as e:
        return f"Error running command: {e}"


def search_files(pattern: str, path: str = ".") -> str:
    """Find files matching a pattern."""
    try:
        result = subprocess.run(
            f"find {path} -name '{pattern}' -type f 2>/dev/null | head -20",
            shell=True,
            capture_output=True,
            text=True
        )
        files = result.stdout.strip()
        return files if files else "No files found"
    except Exception as e:
        return f"Error searching files: {e}"


def search_content(query: str, path: str = ".") -> str:
    """Search for text in files."""
    try:
        result = subprocess.run(
            f"grep -r '{query}' {path} 2>/dev/null | head -20",
            shell=True,
            capture_output=True,
            text=True
        )
        matches = result.stdout.strip()
        return matches if matches else "No matches found"
    except Exception as e:
        return f"Error searching content: {e}"
