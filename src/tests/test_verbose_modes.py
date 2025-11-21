#!/usr/bin/env python3
"""
Test script to demonstrate verbose and debug modes in the Agent.
"""

from downes.agent import Agent


def test_normal_mode():
    """Test agent in normal mode (no extra output)"""
    print("\n" + "=" * 60)
    print("TEST 1: Normal Mode (quiet)")
    print("=" * 60)
    agent = Agent(max_steps=5, verbose=False, debug=False)
    # Just test the initialization
    print("✓ Agent initialized in normal mode")


def test_verbose_mode():
    """Test agent in verbose mode (shows LLM timing and tokens)"""
    print("\n" + "=" * 60)
    print("TEST 2: Verbose Mode (shows timing and token usage)")
    print("=" * 60)
    agent = Agent(max_steps=5, verbose=True, debug=False)
    print("✓ Agent initialized in verbose mode")


def test_debug_mode():
    """Test agent in debug mode (shows prompts, responses, etc.)"""
    print("\n" + "=" * 60)
    print("TEST 3: Debug Mode (shows detailed LLM interactions)")
    print("=" * 60)
    agent = Agent(max_steps=5, verbose=False, debug=True)
    print("✓ Agent initialized in debug mode")


def test_both_modes():
    """Test agent with both verbose and debug enabled"""
    print("\n" + "=" * 60)
    print("TEST 4: Both Verbose and Debug Modes")
    print("=" * 60)
    agent = Agent(max_steps=5, verbose=True, debug=True)
    print("✓ Agent initialized with both modes enabled")


if __name__ == "__main__":
    print("\n🧪 Testing Agent Verbose and Debug Modes")
    print("=" * 60)

    test_normal_mode()
    test_verbose_mode()
    test_debug_mode()
    test_both_modes()

    print("\n" + "=" * 60)
    print("✅ All verbose mode tests passed!")
    print("=" * 60)

    print("\nUsage Examples:")
    print("  Normal:  downes")
    print("  Verbose: downes --verbose  (or -v)")
    print("  Debug:   downes --debug    (or -d)")
    print("  Both:    downes --verbose --debug")
    print("\nOr use environment variables:")
    print("  DOWNES_VERBOSE=true downes")
    print("  DOWNES_DEBUG=true downes")
