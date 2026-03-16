"""Anthropic API wrapper for LLM interactions with async support and dual backends."""
import json
import logging

from anthropic import Anthropic

from src.backend.config import get_settings
from src.backend.services.sdk_adapter import SDK_AVAILABLE, run_query

logger = logging.getLogger(__name__)


class LLMService:
    """Wrapper around Anthropic Claude API with async support and dual backends."""

    _max_tokens_warning_logged = False

    def __init__(self, api_key: str | None = None, model: str | None = None, backend: str | None = None):
        """Initialize LLM service.

        Args:
            api_key: Anthropic API key. Defaults to settings.
            model: Model name. Defaults to settings.
            backend: Backend to use ('auto', 'sdk', 'anthropic'). Defaults to settings.
        """
        settings = get_settings()
        self.model = model or settings.LLM_MODEL
        self.backend = backend or settings.LLM_BACKEND

        # Determine actual backend
        if self.backend == "auto":
            self.actual_backend = "sdk" if SDK_AVAILABLE else "anthropic"
        else:
            self.actual_backend = self.backend

        # Initialize anthropic client if needed
        if self.actual_backend == "anthropic":
            self.client = Anthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        else:
            self.client = None

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        response_format: str = "text",
        max_tokens: int = 1024,
    ) -> dict | str:
        """Send messages to Claude (async).

        Args:
            system_prompt: System instruction.
            messages: List of {role, content} message dicts.
            response_format: 'text' or 'json'.
            max_tokens: Maximum response tokens (ignored in SDK mode with warning).

        Returns:
            Parsed JSON dict if response_format='json', else raw text string.
            On error, returns {"error": "..."} dict.
        """
        if self.actual_backend == "sdk":
            return await self._chat_sdk(system_prompt, messages, response_format, max_tokens)
        else:
            return await self._chat_anthropic(system_prompt, messages, response_format, max_tokens)

    async def _chat_sdk(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        response_format: str,
        max_tokens: int,
    ) -> dict | str:
        """Chat using Claude Agent SDK backend."""
        # Log max_tokens warning once
        if max_tokens != 1024 and not LLMService._max_tokens_warning_logged:
            logger.warning("max_tokens parameter is ignored when using SDK backend")
            LLMService._max_tokens_warning_logged = True

        try:
            # Combine all messages into a single prompt
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    prompt_parts.append(content)
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")

            prompt = "\n\n".join(prompt_parts)

            # Run query
            text = await run_query(prompt, system_prompt, self.model)

            # Parse response
            if response_format == "json":
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"error": "LLM returned invalid JSON", "raw": text}
            return text
        except Exception as e:
            return {"error": f"LLM API error: {e!s}"}

    async def _chat_anthropic(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        response_format: str,
        max_tokens: int,
    ) -> dict | str:
        """Chat using Anthropic API backend."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
            )
            if not response.content:
                return {"error": "LLM returned empty response"}
            text = response.content[0].text
            if response_format == "json":
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"error": "LLM returned invalid JSON", "raw": text}
            return text
        except Exception as e:
            return {"error": f"LLM API error: {e!s}"}
