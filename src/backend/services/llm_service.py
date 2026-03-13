"""Anthropic API wrapper for LLM interactions."""
import json

from anthropic import Anthropic

from src.backend.config import get_settings


class LLMService:
    """Wrapper around Anthropic Claude API."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize LLM service.

        Args:
            api_key: Anthropic API key. Defaults to settings.
            model: Model name. Defaults to settings.
        """
        settings = get_settings()
        self.client = Anthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.model = model or settings.LLM_MODEL

    def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        response_format: str = "text",
        max_tokens: int = 1024,
    ) -> dict | str:
        """Send messages to Claude.

        Args:
            system_prompt: System instruction.
            messages: List of {role, content} message dicts.
            response_format: 'text' or 'json'.
            max_tokens: Maximum response tokens.

        Returns:
            Parsed JSON dict if response_format='json', else raw text string.
            On error, returns {"error": "..."} dict.
        """
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
                return json.loads(text)
            return text
        except json.JSONDecodeError:
            return {"error": "LLM returned invalid JSON", "raw": text}
        except Exception as e:
            return {"error": f"LLM API error: {e!s}"}
