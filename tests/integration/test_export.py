#!/usr/bin/env python3
"""
Test conversation export functionality
"""

from groqqy.components.conversation import ConversationManager
from groqqy.components.exporter import ConversationExporter

def test_export():
    """Test markdown and HTML export with sample conversation."""

    # Create a sample conversation
    conv = ConversationManager()

    # Add some messages
    conv.add_user("What's the weather like?")
    conv.add_tool_calls(
        "Let me check the weather for you.",
        [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "San Francisco", "units": "celsius"}'
                }
            }
        ]
    )
    conv.add_tool_result("call_123", "Temperature: 18°C, Conditions: Partly cloudy")
    conv.add_assistant("The weather in San Francisco is currently 18°C and partly cloudy.")

    conv.add_user("Can you help me write a Python function?")
    conv.add_assistant("Of course! What kind of function do you need?")

    # Create exporter
    exporter = ConversationExporter(conv.get_history())

    # Test markdown export
    print("=" * 60)
    print("MARKDOWN EXPORT TEST")
    print("=" * 60)
    markdown = exporter.to_markdown()
    print(markdown[:500])  # Print first 500 chars
    print("\n... (truncated)\n")

    # Save markdown
    with open('/tmp/test_conversation.md', 'w') as f:
        f.write(markdown)
    print("✅ Markdown saved to /tmp/test_conversation.md")

    # Test HTML export
    print("\n" + "=" * 60)
    print("HTML EXPORT TEST")
    print("=" * 60)
    html = exporter.to_html()
    print(html[:500])  # Print first 500 chars
    print("\n... (truncated)\n")

    # Save HTML
    with open('/tmp/test_conversation.html', 'w') as f:
        f.write(html)
    print("✅ HTML saved to /tmp/test_conversation.html")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"Messages in conversation: {len(conv)}")
    print(f"Markdown size: {len(markdown)} chars")
    print(f"HTML size: {len(html)} chars")
    print("\nOpen /tmp/test_conversation.html in a browser to see the styled output!")

if __name__ == "__main__":
    test_export()
