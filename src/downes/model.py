import os
import time
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Type, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage
from openai import APIConnectionError

from downes.prompts import DEFAULT_SYSTEM_PROMPT


def get_llm_config():
    """
    Get LLM configuration from environment variables.
    Supports OpenAI and OpenAI-compatible APIs (OpenRouter, Ollama, llama.cpp, etc.)

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
    # Check for custom base URL first (local/alternative providers)
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")

    # For local providers, API key is optional
    if base_url and "localhost" in base_url:
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

    return config


def call_llm(
    prompt: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    tools: Optional[List[BaseTool]] = None,
) -> AIMessage:
    """
    Call the LLM with the given prompt.

    Supports OpenAI and any OpenAI-compatible API (OpenRouter, Ollama, llama.cpp, etc.)
    Configure via environment variables - see get_llm_config() for details.

    Args:
        prompt: The user prompt
        model: Model name (overrides LLM_MODEL env var)
        system_prompt: System prompt (default: DEFAULT_SYSTEM_PROMPT)
        output_schema: Pydantic model for structured output
        tools: List of tools to bind to the LLM

    Returns:
        AIMessage with the response
    """
    final_system_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", final_system_prompt), ("user", "{prompt}")]
    )

    # Get LLM configuration
    config = get_llm_config()
    if model:
        config["model"] = model

    # Initialize the LLM with configuration
    llm = ChatOpenAI(**config)

    # Add structured output or tools to the LLM.
    runnable = llm
    if output_schema:
        runnable = llm.with_structured_output(output_schema, method="function_calling")
    elif tools:
        runnable = llm.bind_tools(tools)

    chain = prompt_template | runnable

    # Retry logic for transient connection errors
    for attempt in range(3):
        try:
            return chain.invoke({"prompt": prompt})
        except APIConnectionError as e:
            if attempt == 2:  # Last attempt
                raise
            time.sleep(0.5 * (2**attempt))  # 0.5s, 1s backoff
