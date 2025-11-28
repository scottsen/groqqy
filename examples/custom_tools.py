#!/usr/bin/env python3
"""
Custom tools example
"""

from groqqy import Groqqy
import random

# Define custom tools
def roll_dice(sides: int = 6) -> str:
    """Roll a dice with specified number of sides."""
    result = random.randint(1, sides)
    return f"Rolled a {result} on a {sides}-sided dice"

def flip_coin() -> str:
    """Flip a coin and return heads or tails."""
    result = random.choice(["Heads", "Tails"])
    return f"Coin flip result: {result}"

def calculate_tip(bill_amount: float, tip_percent: float = 15.0) -> str:
    """Calculate tip amount for a bill."""
    tip = bill_amount * (tip_percent / 100)
    total = bill_amount + tip
    return f"Bill: ${bill_amount:.2f}, Tip ({tip_percent}%): ${tip:.2f}, Total: ${total:.2f}"

def main():
    print("Groqqy Custom Tools Example")
    print("=" * 60)
    print()

    # Create bot with custom tools
    bot = Groqqy(tools=[roll_dice, flip_coin, calculate_tip])

    # Use custom tools
    print("1. Roll a dice")
    response, cost = bot.chat("Roll a 20-sided dice for me")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    print("2. Flip a coin")
    response, cost = bot.chat("Flip a coin")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    print("3. Calculate tip")
    response, cost = bot.chat("Calculate 20% tip on a $85 bill")
    print(f"Response: {response}")
    print(f"Cost: ${cost:.6f}\n")

    print("=" * 60)
    print(f"Total cost: ${bot.total_cost:.6f}")

if __name__ == "__main__":
    main()
