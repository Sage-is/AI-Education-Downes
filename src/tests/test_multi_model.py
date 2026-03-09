"""Tests for multi-model / role-based LLM configuration."""

import os
import pytest
from unittest.mock import patch

from downes.model import _is_localhost, get_llm_config


# ---------------------------------------------------------------------------
# _is_localhost
# ---------------------------------------------------------------------------


class TestIsLocalhost:
    def test_localhost(self):
        assert _is_localhost("http://localhost:3456/v1") is True

    def test_127_0_0_1(self):
        assert _is_localhost("http://127.0.0.1:8080/v1") is True

    def test_ipv6_loopback(self):
        assert _is_localhost("http://[::1]:3456/v1") is True

    def test_remote_url(self):
        assert _is_localhost("https://openrouter.ai/api/v1") is False

    def test_none(self):
        assert _is_localhost(None) is False

    def test_empty(self):
        assert _is_localhost("") is False


# ---------------------------------------------------------------------------
# get_llm_config — no role (base config, backward-compatible)
# ---------------------------------------------------------------------------


class TestGetLlmConfigNoRole:
    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-base",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_MODEL": "z-ai/glm-5",
            "LLM_TEMPERATURE": "0.8",
            # Role vars present but should be ignored
            "LLM_PLANNING_MODEL": "claude-sonnet-4",
            "LLM_PLANNING_BASE_URL": "http://localhost:3456/v1",
        },
        clear=True,
    )
    def test_base_config_ignores_role_vars(self):
        config = get_llm_config()
        assert config["api_key"] == "sk-base"
        assert config["model"] == "z-ai/glm-5"
        assert config["temperature"] == 0.8
        assert config["base_url"] == "https://openrouter.ai/api/v1"

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "sk-test", "LLM_MODEL": "gpt-4.1"},
        clear=True,
    )
    def test_no_base_url(self):
        config = get_llm_config()
        assert "base_url" not in config
        assert config["api_key"] == "sk-test"

    @patch.dict(
        os.environ,
        {"OPENAI_BASE_URL": "http://localhost:11434/v1"},
        clear=True,
    )
    def test_localhost_auto_key(self):
        config = get_llm_config()
        assert config["api_key"] == "not-needed-for-local"


# ---------------------------------------------------------------------------
# get_llm_config — with role
# ---------------------------------------------------------------------------


class TestGetLlmConfigWithRole:
    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-base",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_MODEL": "z-ai/glm-5",
            "LLM_TEMPERATURE": "0.8",
            "LLM_PLANNING_MODEL": "claude-sonnet-4",
            "LLM_PLANNING_BASE_URL": "http://localhost:3456/v1",
            "LLM_PLANNING_API_KEY": "my-key",
            "LLM_PLANNING_TEMPERATURE": "0",
        },
        clear=True,
    )
    def test_full_override(self):
        config = get_llm_config(role="planning")
        assert config["model"] == "claude-sonnet-4"
        assert config["base_url"] == "http://localhost:3456/v1"
        assert config["api_key"] == "my-key"
        assert config["temperature"] == 0.0

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-base",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_MODEL": "z-ai/glm-5",
            "LLM_ACTION_MODEL": "x-ai/grok-4.1-fast",
        },
        clear=True,
    )
    def test_model_only_override(self):
        config = get_llm_config(role="action")
        assert config["model"] == "x-ai/grok-4.1-fast"
        # Inherits base URL and key
        assert config["base_url"] == "https://openrouter.ai/api/v1"
        assert config["api_key"] == "sk-base"

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-base",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_MODEL": "z-ai/glm-5",
            "LLM_ANSWER_MODEL": "claude-sonnet-4",
            "LLM_ANSWER_BASE_URL": "http://localhost:3456/v1",
            # No LLM_ANSWER_API_KEY — should auto-detect localhost
        },
        clear=True,
    )
    def test_localhost_auto_key_for_role(self):
        config = get_llm_config(role="answer")
        assert config["model"] == "claude-sonnet-4"
        assert config["base_url"] == "http://localhost:3456/v1"
        assert config["api_key"] == "not-needed-for-local"

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-base",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_MODEL": "z-ai/glm-5",
            "LLM_ANSWER_BASE_URL": "https://api.example.com/v1",
            # No LLM_ANSWER_API_KEY — should inherit base key
        },
        clear=True,
    )
    def test_remote_role_url_inherits_base_key(self):
        config = get_llm_config(role="answer")
        assert config["base_url"] == "https://api.example.com/v1"
        assert config["api_key"] == "sk-base"

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-base",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "LLM_MODEL": "z-ai/glm-5",
            "LLM_TEMPERATURE": "0.8",
        },
        clear=True,
    )
    def test_no_overrides_returns_base(self):
        config = get_llm_config(role="action")
        assert config["model"] == "z-ai/glm-5"
        assert config["base_url"] == "https://openrouter.ai/api/v1"
        assert config["api_key"] == "sk-base"
        assert config["temperature"] == 0.8

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-base",
            "LLM_MODEL": "z-ai/glm-5",
            "LLM_PLANNING_TEMPERATURE": "0.2",
        },
        clear=True,
    )
    def test_temperature_override_only(self):
        config = get_llm_config(role="planning")
        assert config["temperature"] == 0.2
        assert config["model"] == "z-ai/glm-5"
        assert config["api_key"] == "sk-base"
