#!/usr/bin/env python3
"""
Tool usage example
"""

from groqqy import Groqqy

def main():
    print("Groqqy Tool Usage Example")
    print("=" * 60)
    print()

    bot = Groqqy()

    # Search files
    print("1. Search for Python files")
    response, cost = bot.chat("Find all .py files in the current directory")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    # Run command
    print("2. Run a command")
    response, cost = bot.chat("Show me the current directory path")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    # Read file
    print("3. Read README")
    response, cost = bot.chat("Read the README.md file and summarize it")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    print("=" * 60)
    print(f"Total cost: ${bot.total_cost:.6f}")

if __name__ == "__main__":
    main()
