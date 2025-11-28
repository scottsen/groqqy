#!/usr/bin/env python3
"""
Groqqy CLI - Interactive chat interface
"""

import sys
from .bot import Groqqy


def main():
    """Run interactive chat loop."""
    print("🤖 Groqqy - Your helpful assistant (powered by Groq)")
    print("Type 'quit' or 'exit' to end conversation")
    print("Type 'reset' to clear conversation history")
    print("=" * 60)
    print()

    bot = Groqqy()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\n👋 Goodbye! Total cost: ${bot.total_cost:.6f}")
                break

            if user_input.lower() == 'reset':
                bot.reset()
                print("🔄 Conversation reset\n")
                continue

            # Get response
            response, cost = bot.chat(user_input)

            # Display response
            print(f"\nGroqqy: {response}")
            print(f"💰 Cost: ${cost:.6f} | Total: ${bot.total_cost:.6f}")
            print()

        except KeyboardInterrupt:
            print(f"\n\n👋 Interrupted. Total cost: ${bot.total_cost:.6f}")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
