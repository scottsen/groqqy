"""
Groqqy - Simple general-purpose AI assistant powered by Groq

Fast, cheap, and helpful.
"""

__version__ = "0.1.0"

from .bot import Groqqy
from .tools import read_file, run_command, search_files, search_content

__all__ = [
    "Groqqy",
    "read_file",
    "run_command",
    "search_files",
    "search_content",
]
