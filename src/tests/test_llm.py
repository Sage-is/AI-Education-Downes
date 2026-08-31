"""
Test script to verify LLM configuration.

Tests your LLM setup (OpenAI, OpenRouter, Ollama, llama.cpp, etc.)
Run this before using the agent to ensure everything is configured correctly.
"""

import os

import pytest
from dotenv import load_dotenv
from downes.model import call_llm, get_llm_config

# Load environment variables
load_dotenv()


@pytest.mark.live
def test_llm_config():
    """Display current LLM configuration."""
    print("=" * 60)
    print("Current LLM Configuration")
    print("=" * 60)

    config = get_llm_config()

    print(f"Model: {config['model']}")
    print(f"Temperature: {config['temperature']}")

    if "base_url" in config:
        print(f"Base URL: {config['base_url']}")
        print("Provider: Custom (OpenAI-compatible API)")

        # Identify provider based on URL
        url = config["base_url"].lower()
        if "openrouter" in url:
            print("  → Detected: OpenRouter")
        elif "localhost:11434" in url or "ollama" in url:
            print("  → Detected: Ollama (Local)")
        elif "localhost:8080" in url or "llama.cpp" in url:
            print("  → Detected: llama.cpp (Local)")
        elif "lmstudio" in url or "localhost:1234" in url:
            print("  → Detected: LM Studio (Local)")
        elif "sage.is" in url:
            print("  → Detected: Sage.is")
        elif "together" in url:
            print("  → Detected: Together.ai")
        elif "anyscale" in url:
            print("  → Detected: Anyscale")
    else:
        print("Base URL: Default (api.openai.com)")
        print("Provider: OpenAI")

    # Check API key
    api_key = config["api_key"]
    if api_key and api_key != "not-needed-for-local":
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"API Key: {masked_key}")
    else:
        print("API Key: Not required (local provider)")

    print()


@pytest.mark.live
def test_llm_connectivity():
    """Test LLM connectivity with a simple query."""
    print("=" * 60)
    print("Testing LLM Connectivity")
    print("=" * 60)

    try:
        print("Sending test query to LLM...")
        response = call_llm(
            prompt="What is 2 + 2? Respond with just the number.",
            system_prompt="You are a helpful assistant. Be concise.",
        )

        print("✓ LLM is responding!")
        print(f"Response: {response.content}")
        print()

        return True
    except Exception as e:
        print(f"✗ LLM connection failed!")
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting tips:")

        config = get_llm_config()
        if "base_url" in config:
            url = config["base_url"]
            print(f"1. Check if your LLM server is running at: {url}")
            if "localhost" in url:
                print("2. For local servers (Ollama, llama.cpp, LM Studio):")
                print("   - Verify the server is started")
                print("   - Check the port number matches")
                print("   - Try: curl {url}/models")
        else:
            print("1. Check your OPENAI_API_KEY is correct")
            print("2. Verify you have API credits/quota remaining")
            print("3. Check your internet connection")

        return False


@pytest.mark.live
def test_structured_output():
    """Test structured output (function calling)."""
    print("=" * 60)
    print("Testing Structured Output (Function Calling)")
    print("=" * 60)

    from pydantic import BaseModel, Field

    class SimpleResponse(BaseModel):
        answer: int = Field(description="The numerical answer")
        reasoning: str = Field(description="Brief explanation")

    try:
        print("Testing structured output with Pydantic schema...")
        response = call_llm(
            prompt="Calculate 15 + 27. Explain your reasoning.",
            system_prompt="You are a math assistant.",
            output_schema=SimpleResponse,
        )

        print("✓ Structured output works!")
        print(f"Answer: {response.answer}")
        print(f"Reasoning: {response.reasoning}")
        print()

        return True
    except Exception as e:
        print(f"✗ Structured output failed!")
        print(f"Error: {str(e)}")
        print()
        print("Note: Some local models may not support function calling.")
        print("The agent will still work but may have reduced accuracy.")
        print()

        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LLM Configuration Test Suite")
    print("=" * 60)
    print()

    # Test 1: Show configuration
    test_llm_config()

    # Test 2: Test connectivity
    connectivity_ok = test_llm_connectivity()

    if not connectivity_ok:
        print("=" * 60)
        print("❌ LLM connectivity test failed!")
        print("=" * 60)
        print()
        print("Please fix the configuration issues above before running the agent.")
        return

    # Test 3: Test structured output
    structured_ok = test_structured_output()

    # Final summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✓ Configuration loaded")
    print(f"✓ LLM connectivity: {'PASSED' if connectivity_ok else 'FAILED'}")
    print(
        f"{'✓' if structured_ok else '⚠'} Structured output: {'PASSED' if structured_ok else 'LIMITED'}"
    )

    if connectivity_ok:
        if structured_ok:
            print()
            print("🎉 All tests passed! Your LLM is ready to use.")
            print("   Run: uv run downes-agent")
        else:
            print()
            print("⚠️  Basic connectivity works but structured output is limited.")
            print("   The agent will still work but may be less accurate.")
            print("   Consider using a model that supports function calling.")
    print("=" * 60)


if __name__ == "__main__":
    main()
