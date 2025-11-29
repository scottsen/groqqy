#!/usr/bin/env python3
"""
Groqqy CLI - Interactive chat interface with configuration support
"""

import sys
import argparse
from .bot import Groqqy
from .config import GroqqyConfig


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Groqqy - Fast AI assistant powered by Groq",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  groqqy                                    # Interactive mode with boot.md
  groqqy --prompt "explain quantum computing"  # Single prompt
  groqqy --context docs/project.md --prompt "summarize"  # With context
  groqqy -c notes.txt -c spec.md            # Multiple context files

Configuration:
  Config directory: ~/.groqqy/
  Boot instructions: ~/.groqqy/boot.md (auto-created on first run)
  Knowledge files: ~/.groqqy/knowledge/
        """
    )

    parser.add_argument(
        '--model', '-m',
        default='llama-3.1-8b-instant',
        help='Model to use (default: llama-3.1-8b-instant)'
    )

    parser.add_argument(
        '--context', '-c',
        action='append',
        metavar='FILE',
        help='Load additional context file(s) - can be used multiple times'
    )

    parser.add_argument(
        '--prompt', '-p',
        metavar='TEXT',
        help='Single prompt to execute (non-interactive mode)'
    )

    parser.add_argument(
        '--no-boot',
        action='store_true',
        help='Skip loading ~/.groqqy/boot.md'
    )

    return parser.parse_args()


def run_interactive(bot: Groqqy):
    """Run interactive chat loop."""
    print("🤖 Groqqy - Your helpful assistant (powered by Groq)")
    print("Type 'quit' or 'exit' to end conversation")
    print("Type 'reset' to clear conversation history")
    print("=" * 60)
    print()

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


def run_single_prompt(bot: Groqqy, prompt: str):
    """Execute a single prompt and exit."""
    try:
        response, cost = bot.chat(prompt)
        print(response)
        print(f"\n💰 Cost: ${cost:.6f}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_args()

    # Initialize configuration
    config = GroqqyConfig()
    config.ensure_config_exists()

    # Load system instruction
    if args.no_boot:
        system_instruction = None
    else:
        system_instruction = config.load_system_instruction(
            context_files=args.context,
            extra_prompt=None  # Don't include --prompt in system instruction
        )

    # Create bot
    bot = Groqqy(
        model=args.model,
        system_instruction=system_instruction
    )

    # Run in appropriate mode
    if args.prompt:
        run_single_prompt(bot, args.prompt)
    else:
        run_interactive(bot)


if __name__ == "__main__":
    main()
