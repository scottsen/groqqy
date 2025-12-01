#!/usr/bin/env python3
"""
Example: Export Groqqy conversations to markdown and HTML

Shows three ways to export conversations:
1. Programmatic export (for scripts/automation)
2. Interactive export (during chat session)
3. Auto-export on exit (CLI flag)
"""

from groqqy.bot import Groqqy


def example_programmatic_export():
    """Example: Export conversation programmatically."""
    print("=" * 60)
    print("Example 1: Programmatic Export")
    print("=" * 60)

    # Create bot
    bot = Groqqy(model="llama-3.1-8b-instant")

    # Have a conversation
    bot.chat("What is 2 + 2?")
    bot.chat("What about 10 * 5?")

    # Export to markdown
    markdown = bot.export_markdown()
    print("\nMarkdown export (first 200 chars):")
    print(markdown[:200] + "...\n")

    # Export to HTML
    html = bot.export_html()
    print(f"HTML export size: {len(html)} characters\n")

    # Save to files
    bot.save_conversation("example_conversation.md", format="markdown")
    bot.save_conversation("example_conversation.html", format="html")

    print("✅ Saved to example_conversation.md and example_conversation.html")
    print()


def example_interactive_usage():
    """Example: How to use export in interactive mode."""
    print("=" * 60)
    print("Example 2: Interactive Export")
    print("=" * 60)
    print("""
When running groqqy interactively:

    $ groqqy

During the chat, type:

    export markdown my_conversation.md
    export html my_conversation.html

This saves your conversation to the specified file.
    """)


def example_cli_flag():
    """Example: Using --export CLI flag."""
    print("=" * 60)
    print("Example 3: Auto-Export on Exit")
    print("=" * 60)
    print("""
Use the --export flag to automatically save on exit:

    # Auto-detects markdown format from .md extension
    $ groqqy --export conversation.md

    # Auto-detects HTML format from .html extension
    $ groqqy --export conversation.html

    # With single prompt (non-interactive)
    $ groqqy --prompt "Explain quantum computing" --export output.html

The conversation is automatically saved when you quit.
    """)


if __name__ == "__main__":
    example_programmatic_export()
    example_interactive_usage()
    example_cli_flag()

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Open example_conversation.html in your browser to see styled output
2. Try: groqqy --export test.md
3. During chat, type: export html my_chat.html
    """)
