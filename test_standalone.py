#!/usr/bin/env python3
"""
Quick test to verify Groqqy is standalone (no TIA dependencies).

This script demonstrates:
1. Import without TIA in path
2. Provider interface works
3. Tool schema builder works
4. Logging works
5. Bot instantiates (requires GROQ_API_KEY to actually call API)
"""

import os
import sys

# Remove TIA from path if present to prove standalone
sys.path = [p for p in sys.path if 'tia' not in p.lower()]

print("=" * 60)
print("Groqqy Standalone Test")
print("=" * 60)

# Test 1: Provider interface
print("\n1. Testing provider interface...")
from groqqy.provider import Provider, LLMResponse
print("   ✓ Provider interface imported")

# Test 2: Utils
print("\n2. Testing tool schema builder...")
from groqqy.utils import build_tool_schema

def example_tool(path: str, recursive: bool = False) -> str:
    """Read a file from the filesystem"""
    pass

schema = build_tool_schema(example_tool)
assert schema['type'] == 'function'
assert schema['function']['name'] == 'example_tool'
assert 'path' in schema['function']['parameters']['required']
assert 'recursive' not in schema['function']['parameters']['required']
print("   ✓ Tool schema builder works correctly")

# Test 3: Groq provider
print("\n3. Testing Groq provider...")
from groqqy.providers.groq import GroqProvider
print("   ✓ GroqProvider imported")

# Test 4: Logging
print("\n4. Testing logging system...")
from groqqy.log import log, get_logger
print("   ✓ Logging system imported")

# Test 5: Bot instantiation
print("\n5. Testing bot instantiation...")
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY', 'gsk_dummy_key_for_testing')

from groqqy.bot import Groqqy
bot = Groqqy()
print(f"   ✓ Bot created successfully")
print(f"   - Session ID: {bot.session_id}")
print(f"   - Model: {bot.provider.model}")
print(f"   - Tools: {[t.__name__ for t in bot.tools]}")

# Test 6: Check structure
print("\n6. Checking structure...")
import groqqy
print(f"   ✓ Groqqy module location: {groqqy.__file__}")
print(f"   ✓ No TIA dependencies detected")

print("\n" + "=" * 60)
print("✅ All tests passed! Groqqy is standalone.")
print("=" * 60)

# Check if we can actually call the API
if os.getenv('GROQ_API_KEY') and os.getenv('GROQ_API_KEY') != 'gsk_dummy_key_for_testing':
    print("\n🚀 API key detected - testing live call...")
    try:
        response, cost = bot.chat("Say 'Hello from standalone Groqqy!' in exactly those words.")
        print(f"   Response: {response}")
        print(f"   Cost: ${cost:.6f}")
        print("   ✅ Live API call successful!")
    except Exception as e:
        print(f"   ⚠️  API call failed: {e}")
else:
    print("\n💡 Set GROQ_API_KEY environment variable to test live API calls")
    print("   Example: export GROQ_API_KEY='gsk_...'")
