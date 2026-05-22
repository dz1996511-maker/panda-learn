"""Tests for the LLM provider factory."""

import pytest
from app.llm.factory import list_providers, get_provider
from app.llm.base import BaseLLMProvider


def test_list_providers():
    providers = list_providers()
    assert "claude" in providers
    assert "openai" in providers


def test_get_provider_invalid():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("nonexistent", "fake-key")


def test_get_claude_provider():
    provider = get_provider("claude", "test-key")
    assert isinstance(provider, BaseLLMProvider)
    assert provider.provider_name == "claude"


def test_get_openai_provider():
    provider = get_provider("openai", "test-key")
    assert isinstance(provider, BaseLLMProvider)
    assert provider.provider_name == "openai"
