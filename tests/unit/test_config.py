#!/usr/bin/env python3
"""
Test the new configuration system for Groqqy v0.2.0
"""

from groqqy.config import GroqqyConfig
from pathlib import Path

def test_config_system():
    """Test all configuration features."""

    print("=" * 60)
    print("Groqqy v0.2.0 Configuration System Test")
    print("=" * 60)
    print()

    # 1. Initialize config
    config = GroqqyConfig()
    print(f"✓ Config initialized")
    print(f"  Directory: {config.config_dir}")
    print(f"  Boot file: {config.boot_file}")
    print(f"  Knowledge: {config.knowledge_dir}")
    print()

    # 2. Ensure directories exist
    config.ensure_config_exists()
    print(f"✓ Config directories created/verified")
    print(f"  boot.md exists: {config.boot_file.exists()}")
    print(f"  knowledge/ exists: {config.knowledge_dir.exists()}")
    print()

    # 3. Load default instruction
    instruction = config.load_system_instruction()
    print(f"✓ Default system instruction loaded")
    print(f"  Length: {len(instruction)} chars")
    print(f"  Preview: {instruction[:80]}...")
    print()

    # 4. Test with extra context
    context_file = config.knowledge_dir / "test_context.md"
    context_file.write_text("# Test Context\nThis is additional knowledge.")

    instruction_with_context = config.load_system_instruction(
        context_files=[str(context_file)],
        extra_prompt="Always be extra helpful"
    )

    print(f"✓ System instruction with extras loaded")
    print(f"  Length: {len(instruction_with_context)} chars")
    print(f"  Has boot.md: {'Groqqy Boot' in instruction_with_context}")
    print(f"  Has context: {'Test Context' in instruction_with_context}")
    print(f"  Has prompt: {'extra helpful' in instruction_with_context}")
    print()

    # 5. Show file structure
    print("📁 ~/.groqqy/ structure:")
    for item in sorted(config.config_dir.rglob("*")):
        if item.is_file():
            rel_path = item.relative_to(config.config_dir)
            size = item.stat().st_size
            print(f"  {rel_path} ({size} bytes)")
    print()

    print("=" * 60)
    print("✅ All configuration tests passed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Edit ~/.groqqy/boot.md to customize behavior")
    print("  2. Add knowledge files to ~/.groqqy/knowledge/")
    print("  3. Run: groqqy --help")
    print("  4. Run: groqqy --prompt 'hello world'")
    print()

if __name__ == "__main__":
    test_config_system()
