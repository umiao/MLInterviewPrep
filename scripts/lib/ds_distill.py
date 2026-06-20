"""Shared DeepSeek distillation client for the CHEATSHEET tasks (T-P1-644..648).

Thin, dependency-light wrapper over the DeepSeek chat-completions endpoint
(OpenAI-compatible) used to distill long study material into one-pager cheat
sheets. Credentials come from ``scripts/lib/deepseek_creds.py`` (handwritten
KEY=VALUE loader; key never enters env/globals/logs).

Design notes (learned from pensieve's deepseek_spike probes):
  - ``deepseek-v4-pro`` is a REASONING model: the completion budget is split
    between hidden ``reasoning_tokens`` and the visible ``content``. A too-small
    ``max_tokens`` returns EMPTY ``content`` (reasoning ate the whole budget).
    ``complete()`` therefore escalates ``max_tokens`` (doubling, capped) and
    retries up to ``max_attempts`` when content comes back empty.
  - Read ``choices[0].message.content`` (NOT ``reasoning_content``).
  - Transport is stdlib ``urllib`` -- no openai SDK / httpx dependency.
  - ``temperature=0.0`` for deterministic distillation.

Autorun-safe: ``deepseek_creds.load()`` raises FileNotFoundError when
``.env.deepseek`` is absent (autonomous sessions never carry the key), so this
helper is a no-op outside a supervised session with the key on disk.

Usage::

    from scripts.lib import ds_distill
    res = ds_distill.complete(system="You are ...", user="<source markdown>")
    print(res.text)            # the distilled cheat sheet
    print(res.usage)           # token accounting
"""
from __future__ import annotations

import json
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# deepseek_creds lives next to this module; import it whether this file is run as
# a script (sys.path has scripts/lib) or imported as scripts.lib.ds_distill.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import deepseek_creds  # noqa: E402

# Reasoning-model token budgeting. Start generous; double on empty content.
_DEFAULT_MAX_TOKENS = 8192
_MAX_TOKENS_CAP = 16384
_DEFAULT_MAX_ATTEMPTS = 3
_DEFAULT_TIMEOUT_S = 600


@dataclass(frozen=True)
class DistillResult:
    """Result of a single distillation call."""

    text: str
    usage: dict
    finish_reason: str | None
    attempts: int
    max_tokens_used: int


def _post(
    creds: deepseek_creds.DeepSeekCreds,
    system: str,
    user: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
    timeout_s: int,
) -> dict:
    """Single chat-completions POST. Returns the parsed JSON response."""
    body: dict[str, object] = {
        "model": creds.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        creds.base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {creds.key}",
            "Content-Type": "application/json",
            "Connection": "close",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def complete(
    system: str,
    user: str,
    *,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    json_mode: bool = False,
    max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
    timeout_s: int = _DEFAULT_TIMEOUT_S,
    creds: deepseek_creds.DeepSeekCreds | None = None,
    verbose: bool = False,
) -> DistillResult:
    """Call DeepSeek chat-completions, escalating max_tokens on empty content.

    Args:
        system: System prompt.
        user: User content (e.g. the source markdown to distill).
        max_tokens: Initial completion budget. Doubled (capped at 16384) on each
            empty-content retry.
        temperature: Sampling temperature (0.0 = deterministic).
        json_mode: If True, request ``response_format={"type":"json_object"}``.
        max_attempts: Max attempts before raising on persistent empty content.
        timeout_s: Per-request socket timeout.
        creds: Pre-loaded credentials; if None, ``deepseek_creds.load()`` is called.
        verbose: If True, print per-attempt diagnostics to stderr.

    Returns:
        DistillResult with the non-empty ``text``, token ``usage``, and metadata.

    Raises:
        FileNotFoundError: if creds are absent (autorun-safe default).
        RuntimeError: if content is still empty after ``max_attempts``.
    """
    if creds is None:
        creds = deepseek_creds.load()

    tokens = max_tokens
    for attempt in range(1, max_attempts + 1):
        payload = _post(
            creds, system, user, tokens, temperature, json_mode, timeout_s
        )
        choice = payload["choices"][0]
        text = (choice["message"].get("content") or "").strip()
        usage = payload.get("usage") or {}
        if verbose:
            print(
                f"[ds_distill attempt {attempt}] max_tokens={tokens} "
                f"finish={choice.get('finish_reason')} content_len={len(text)} "
                f"prompt_tok={usage.get('prompt_tokens')} "
                f"completion_tok={usage.get('completion_tokens')}",
                file=sys.stderr,
            )
        if text:
            return DistillResult(
                text=text,
                usage=usage,
                finish_reason=choice.get("finish_reason"),
                attempts=attempt,
                max_tokens_used=tokens,
            )
        tokens = min(tokens * 2, _MAX_TOKENS_CAP)

    raise RuntimeError(
        f"DeepSeek returned empty content after {max_attempts} attempts "
        f"(reasoning ate the budget; last max_tokens={tokens})."
    )


if __name__ == "__main__":
    # Connectivity smoke: cheapest possible call. Prints masked creds + reply.
    _creds = deepseek_creds.load()
    print(f"creds: {_creds!r}")
    _res = complete(
        system="Reply with exactly the word PONG.",
        user="ping",
        max_tokens=4096,
        verbose=True,
    )
    print(f"reply: {_res.text!r}  attempts={_res.attempts}  usage={_res.usage}")
