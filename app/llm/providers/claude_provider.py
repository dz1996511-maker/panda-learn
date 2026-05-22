from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, LLMConfig, LLMRole


class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str, default_model: str | None = None):
        super().__init__(api_key, default_model)
        self._client = AsyncAnthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "claude"

    async def chat(self, messages: list[LLMMessage], config: LLMConfig | None = None) -> LLMResponse:
        cfg = config or LLMConfig()
        model = cfg.model or self.default_model or "claude-sonnet-4-20250514"

        system = cfg.system_prompt
        anthropic_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
            if m.role != LLMRole.SYSTEM
        ]
        if not system:
            system_msgs = [m.content for m in messages if m.role == LLMRole.SYSTEM]
            if system_msgs:
                system = system_msgs[-1]

        resp = await self._client.messages.create(
            model=model,
            system=system,
            messages=anthropic_messages,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

        content = "".join(block.text for block in resp.content if block.type == "text")

        return LLMResponse(
            content=content,
            model=resp.model,
            usage_input_tokens=resp.usage.input_tokens,
            usage_output_tokens=resp.usage.output_tokens,
            finish_reason=resp.stop_reason,
        )

    async def chat_stream(self, messages: list[LLMMessage], config: LLMConfig | None = None) -> AsyncIterator[str]:
        cfg = config or LLMConfig()
        model = cfg.model or self.default_model or "claude-sonnet-4-20250514"

        system = cfg.system_prompt
        anthropic_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
            if m.role != LLMRole.SYSTEM
        ]
        if not system:
            system_msgs = [m.content for m in messages if m.role == LLMRole.SYSTEM]
            if system_msgs:
                system = system_msgs[-1]

        async with self._client.messages.stream(
            model=model,
            system=system,
            messages=anthropic_messages,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Anthropic does not offer a public embedding API;
        # fall back to a simple warning.  Users who need embeddings
        # with the Claude provider should configure a separate
        # provider or use the OpenAI provider for embedding.
        raise NotImplementedError(
            "Claude provider does not support embeddings. "
            "Use OpenAI provider or configure a local embedding model."
        )
