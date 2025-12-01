#!/usr/bin/env python3
"""
Container test script for new Groqqy features

Tests:
1. Conversation export (markdown and HTML)
2. Self-discovery with reveal-cli
"""

import os
import sys
from groqqy.components.conversation import ConversationManager
from groqqy.components.exporter import ConversationExporter


def test_export():
    """Test 1: Conversation export to markdown and HTML."""
    print("=" * 70)
    print("TEST 1: Conversation Export")
    print("=" * 70)

    # Create sample conversation
    conv = ConversationManager()
    conv.add_user("What's the weather?")
    conv.add_tool_calls(
        "Let me check that for you.",
        [{
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "San Francisco"}'
            }
        }]
    )
    conv.add_tool_result("call_123", "Temperature: 18°C, Sunny")
    conv.add_assistant("It's 18°C and sunny in San Francisco!")

    # Test exporter
    exporter = ConversationExporter(conv.get_history())

    # Test markdown
    markdown = exporter.to_markdown()
    assert len(markdown) > 0
    assert "Groqqy Conversation" in markdown
    assert "get_weather" in markdown
    print("✅ Markdown export works")

    # Test HTML
    html = exporter.to_html()
    assert len(html) > 0
    assert "<!DOCTYPE html>" in html
    assert "Groqqy Conversation" in html
    print("✅ HTML export works")

    # Save to files
    output_dir = os.environ.get('TEST_OUTPUT_DIR', '/test_output')
    md_path = os.path.join(output_dir, 'test_conversation.md')
    html_path = os.path.join(output_dir, 'test_conversation.html')

    with open(md_path, 'w') as f:
        f.write(markdown)
    print(f"✅ Saved markdown to {md_path}")

    with open(html_path, 'w') as f:
        f.write(html)
    print(f"✅ Saved HTML to {html_path}")

    print(f"\n📊 Stats:")
    print(f"   Messages: {len(conv)}")
    print(f"   Markdown: {len(markdown)} chars")
    print(f"   HTML: {len(html)} chars")

    return True


def test_reveal_integration():
    """Test 2: reveal-cli integration."""
    print("\n" + "=" * 70)
    print("TEST 2: reveal-cli Integration")
    print("=" * 70)

    import subprocess

    # Check reveal is installed
    try:
        result = subprocess.run(
            ['reveal', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✅ reveal-cli installed: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ reveal-cli not found: {e}")
        return False

    # Test basic reveal command
    try:
        result = subprocess.run(
            ['reveal', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert 'Reveal: Explore code semantically' in result.stdout
        print("✅ reveal --help works")
    except Exception as e:
        print(f"❌ reveal --help failed: {e}")
        return False

    # Test --agent-help (the key feature for self-discovery)
    try:
        result = subprocess.run(
            ['reveal', '--agent-help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert 'Semantic code exploration' in result.stdout
        assert 'Quick Start' in result.stdout
        print("✅ reveal --agent-help works")
        print(f"   Output: {len(result.stdout)} chars")
    except Exception as e:
        print(f"❌ reveal --agent-help failed: {e}")
        return False

    # Test reveal on groqqy's own code
    try:
        result = subprocess.run(
            ['reveal', 'groqqy/bot.py'],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert 'Groqqy' in result.stdout or 'class' in result.stdout
        print("✅ reveal groqqy/bot.py works")
        print(f"   Output: {len(result.stdout)} chars")
    except Exception as e:
        print(f"❌ reveal groqqy/bot.py failed: {e}")
        return False

    return True


def test_bot_export_integration():
    """Test 3: Bot-level export integration."""
    print("\n" + "=" * 70)
    print("TEST 3: Bot Export Integration")
    print("=" * 70)

    # Note: This requires GROQ_API_KEY, so we'll test the API only
    from groqqy.bot import Groqqy
    from groqqy.components.conversation import ConversationManager

    # Mock a conversation (without actual API call)
    conv = ConversationManager()
    conv.add_user("Test message")
    conv.add_assistant("Test response")

    # Test that Bot has export methods
    try:
        from groqqy.bot import Groqqy
        import inspect

        assert hasattr(Groqqy, 'export_markdown')
        assert hasattr(Groqqy, 'export_html')
        assert hasattr(Groqqy, 'save_conversation')
        print("✅ Bot has export methods")

        # Check method signatures
        sig = inspect.signature(Groqqy.export_markdown)
        assert 'self' in str(sig)
        print("✅ export_markdown signature correct")

        sig = inspect.signature(Groqqy.export_html)
        assert 'include_css' in str(sig)
        print("✅ export_html signature correct")

        sig = inspect.signature(Groqqy.save_conversation)
        assert 'filepath' in str(sig)
        assert 'format' in str(sig)
        print("✅ save_conversation signature correct")

    except Exception as e:
        print(f"❌ Bot export integration failed: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "GROQQY CONTAINER TESTS" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝\n")

    results = []

    # Test 1: Export
    try:
        results.append(("Conversation Export", test_export()))
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        results.append(("Conversation Export", False))

    # Test 2: reveal integration
    try:
        results.append(("reveal-cli Integration", test_reveal_integration()))
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        results.append(("reveal-cli Integration", False))

    # Test 3: Bot integration
    try:
        results.append(("Bot Export Integration", test_bot_export_integration()))
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        results.append(("Bot Export Integration", False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
