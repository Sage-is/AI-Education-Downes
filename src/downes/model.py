import os
import time
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List, Optional
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage
from openai import APIConnectionError

from downes.prompts import DEFAULT_SYSTEM_PROMPT


def _is_localhost(url: Optional[str]) -> bool:
    """Check if a URL points to a local server."""
    if not url:
        return False
    return any(host in url for host in ("localhost", "127.0.0.1", "[::1]"))


def get_llm_config(role: Optional[str] = None):
    """
    Get LLM configuration from environment variables.
    Supports OpenAI and OpenAI-compatible APIs (OpenRouter, Ollama, llama.cpp, etc.)

    When ``role`` is provided (e.g. "planning", "action", "answer"), the
    function checks for role-specific overrides before falling back to the
    base config:

        LLM_{ROLE}_MODEL, LLM_{ROLE}_BASE_URL, LLM_{ROLE}_API_KEY,
        LLM_{ROLE}_TEMPERATURE

    Precedence: role override > base env var > default value.

    Environment variables:
    - OPENAI_API_KEY: API key (required for most providers, can be 'not-needed' for local)
    - OPENAI_API_BASE or OPENAI_BASE_URL: Custom base URL for OpenAI-compatible APIs
    - LLM_MODEL: Model name (default: gpt-4.1)
    - LLM_TEMPERATURE: Temperature (default: 0)

    Examples:
    - OpenAI: Just set OPENAI_API_KEY
    - OpenRouter: Set OPENAI_API_KEY and OPENAI_BASE_URL=https://openrouter.ai/api/v1
    - Ollama: Set OPENAI_BASE_URL=http://localhost:11434/v1 and LLM_MODEL=llama2
    - llama.cpp: Set OPENAI_BASE_URL=http://localhost:8080/v1
    """
    # --- Base config (same as before) ---
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")

    if _is_localhost(base_url):
        api_key = os.getenv("OPENAI_API_KEY", "not-needed-for-local")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Get your key from https://platform.openai.com/api-keys or "
                "configure a local LLM provider (Ollama, llama.cpp) by setting OPENAI_BASE_URL"
            )

    config = {
        "api_key": api_key,
        "model": os.getenv("LLM_MODEL", "gpt-4.1"),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0")),
    }

    if base_url:
        config["base_url"] = base_url

    # --- Role-specific overrides ---
    if role:
        prefix = f"LLM_{role.upper()}_"

        role_model = os.getenv(f"{prefix}MODEL")
        if role_model:
            config["model"] = role_model

        role_temp = os.getenv(f"{prefix}TEMPERATURE")
        if role_temp:
            config["temperature"] = float(role_temp)

        role_url = os.getenv(f"{prefix}BASE_URL")
        if role_url:
            config["base_url"] = role_url

            # If the role URL is localhost and no explicit role key, auto-set
            role_key = os.getenv(f"{prefix}API_KEY")
            if role_key:
                config["api_key"] = role_key
            elif _is_localhost(role_url):
                config["api_key"] = "not-needed-for-local"
            # else: inherit the base api_key (already in config)
        else:
            # No role URL override — still allow role-level key override
            role_key = os.getenv(f"{prefix}API_KEY")
            if role_key:
                config["api_key"] = role_key

    return config


def call_llm(
    prompt: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    tools: Optional[List[BaseTool]] = None,
    verbose: bool = False,
    role: Optional[str] = None,
) -> AIMessage:
    """
    Call the LLM with the given prompt.

    Supports OpenAI and any OpenAI-compatible API (OpenRouter, Ollama, llama.cpp, etc.)
    Configure via environment variables - see get_llm_config() for details.

    Args:
        prompt: The user prompt
        model: Model name (overrides LLM_MODEL env var and role config)
        system_prompt: System prompt (default: DEFAULT_SYSTEM_PROMPT)
        tools: List of tools to bind to the LLM
        role: LLM role ("planning", "action", "answer") for per-role config

    Returns:
        AIMessage with the response (text content or tool calls)
    """
    final_system_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
    # Escape braces in system prompt to avoid ChatPromptTemplate variable parsing
    # for literal JSON examples or instructional text.
    sp_escaped = final_system_prompt.replace("{", "{{").replace("}", "}}")

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", sp_escaped), ("user", "{prompt}")]
    )

    # Get LLM configuration (role-aware)
    config = get_llm_config(role=role)
    # Explicit model param takes highest precedence
    if model:
        config["model"] = model

    # Initialize the LLM with configuration
    llm = ChatOpenAI(**config)

    # Bind tools if provided
    runnable = llm.bind_tools(tools) if tools else llm

    chain = prompt_template | runnable

    # Retry logic for transient connection errors
    for attempt in range(3):
        try:
            if verbose:
                start_time = time.time()
                role_tag = f" {role}" if role else ""
                print(f"\n[LLM{role_tag}] Calling {config['model']}...")

            response = chain.invoke({"prompt": prompt})

            if verbose:
                elapsed = time.time() - start_time
                print(f"[LLM] Response received in {elapsed:.2f}s")
                if hasattr(response, "response_metadata"):
                    metadata = response.response_metadata
                    if "token_usage" in metadata:
                        usage = metadata["token_usage"]
                        print(
                            f"[LLM] Tokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                            f"Completion: {usage.get('completion_tokens', 'N/A')}, "
                            f"Total: {usage.get('total_tokens', 'N/A')}"
                        )

            return response
        except APIConnectionError as e:
            if attempt == 2:  # Last attempt
                raise
            if verbose:
                print(f"[LLM] Connection error (attempt {attempt + 1}/3), retrying...")
            time.sleep(0.5 * (2**attempt))  # 0.5s, 1s backoff
