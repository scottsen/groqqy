"""
Example: Using browser_search (Groq platform tool)

This example shows how to use Groq's browser_search tool which executes
server-side and provides web search capabilities.

Key differences from local tools:
- Tool executes on Groq's servers (not locally)
- Results appear directly in the response
- No local function needed
- Must use compatible model (openai/gpt-oss-20b)
"""

from groqqy import Groqqy
from groqqy.tool import ToolRegistry


def main():
    """Demonstrate browser_search usage."""

    # Create registry and add platform tool
    registry = ToolRegistry()
    registry.register_platform_tool("browser_search")

    print("=== Example 1: Pure Web Search ===")
    print("Using browser_search to find current information")
    print()

    # Initialize Groqqy with browser_search compatible model
    bot = Groqqy(
        model="openai/gpt-oss-20b",  # Compatible with browser_search
        tools=registry
    )

    # Ask a question that requires web search
    response, cost = bot.chat(
        "What are the latest developments in AI this week? "
        "Give me a brief summary of the most important news."
    )

    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}")
    print()

    print("=== Example 2: Hybrid (Web Search + Local Tools) ===")
    print("Mixing browser_search with local file tools")
    print()

    # Add local tools to the same registry
    from groqqy.tools import read_file, search_files
    registry.register_function(read_file)
    registry.register_function(search_files)

    # Create new bot with hybrid tools
    bot_hybrid = Groqqy(
        model="openai/gpt-oss-20b",
        tools=registry
    )

    # This could use web search OR local tools as needed
    response2, cost2 = bot_hybrid.chat(
        "What Python files exist in the current directory?"
    )

    print(f"Response: {response2}")
    print(f"Cost: ${cost2:.6f}")
    print()

    print("=== Summary ===")
    print(f"Total cost: ${cost + cost2:.6f}")
    print(f"Strategy used: {bot._agent.strategy.describe()}")


if __name__ == "__main__":
    main()
