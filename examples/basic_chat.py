#!/usr/bin/env python3
"""
Basic chat example
"""

from groqqy import Groqqy

def main():
    print("Basic Groqqy Chat Example")
    print("=" * 60)
    print()

    bot = Groqqy()

    # Simple conversation
    print("1. Simple greeting")
    response, cost = bot.chat("Hello! What can you help me with?")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    # Math question
    print("2. Math question")
    response, cost = bot.chat("What's 15 * 23?")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    # Follow-up
    print("3. Follow-up question")
    response, cost = bot.chat("What about divided by 5?")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    print("=" * 60)
    print(f"Total cost: ${bot.total_cost:.6f}")

if __name__ == "__main__":
    main()
