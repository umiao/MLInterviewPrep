"""DeepSeek API credentials loader for MLInterviewPrep (T-P1-581 / BQ-DEPTH QA).

Mirrors the security-reviewed paradigm of pensieve's
``experiments/deepseek_spike/deepseek_creds.py`` (the proven pattern), adapted
for use as a shared MLI helper. DeepSeek is an OpenAI-compatible API; this loader
hands the OpenAI SDK a key/base_url/model triple without ever touching the
environment.

  1. Handwritten KEY=VALUE parser. No ``python-dotenv``. No ``os.environ``. Ever.
  2. Path is resolved relative to *this file* (not cwd). ``.env.deepseek`` MUST
     live next to this module (``scripts/lib/.env.deepseek``) -- never in the
     user's home, never committed.
  3. ``load()`` raises FileNotFoundError if ``.env.deepseek`` is absent. This is
     the "key not present during autorun" mitigation: an autonomous session never
     carries the key on disk (only ``.env.deepseek.example`` is committed), so
     load() crashes loudly with a pointer to the DeepSeek console -- no silent
     no-op, no fallback to environment variables, no fallback to ~/.
  4. ``DeepSeekCreds.__repr__`` masks the key completely. The raw key only ever
     exists as a transient field on a single instance returned by load(); it never
     enters globals, env, logs, or repr output. Use ``.key_display`` for logging.
  5. Strict schema: exactly the 3 expected keys, 0 extras tolerated. An attacker
     dropping a fourth key into ``.env.deepseek`` gets a ValueError, not silent pickup.

Threat model (same 3 layers as the CalDAV / pensieve spike):
  - accidental leak:    DEFENDED (this module's whole purpose).
  - adversarial inner:  NOT DEFENDED (hooks + secret_guard + the FileNotFoundError
                        autorun default are the other layers, not this file).
  - compromised runtime: NOT DEFENDED (physical disk control of .env.deepseek is
                        the contract).

NOTE: DeepSeek's base_url has NO ``/v1`` suffix, DeepSeek has NO vision support,
and the DeepSeek API is deprecated 2026-07-24 -- migrate to a successor model or
use-and-discard before then.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# --- Locked schema (edits require human review) ------------------------------

REQUIRED_KEYS: frozenset[str] = frozenset(
    {"DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"}
)

# DeepSeek (OpenAI-compatible) keys start with "sk-" followed by url-safe chars.
_KEY_SHAPE = re.compile(r"^sk-[A-Za-z0-9_-]{8,}$")
# Reject the unfilled template value so a forgotten edit fails loud.
_PLACEHOLDER = "sk-your-deepseek-key-here"

_ENV_PATH: Path = Path(__file__).resolve().parent / ".env.deepseek"
_ENV_TEMPLATE_PATH: Path = Path(__file__).resolve().parent / ".env.deepseek.example"


# --- Public API --------------------------------------------------------------


@dataclass(frozen=True)
class DeepSeekCreds:
    """Loaded DeepSeek credentials. ``key`` is masked in repr; access via ``.key``.

    Direct ``.key`` access is a code smell outside the HTTP transport layer --
    grep for it in code review.
    """

    key: str
    base_url: str
    model: str

    @property
    def key_display(self) -> str:
        """Fingerprint for logging: prefix + masked body (never the full key)."""
        return _mask_key(self.key)

    def __repr__(self) -> str:
        return (
            f"DeepSeekCreds(key={self.key_display!r}, "
            f"base_url={self.base_url!r}, model={self.model!r})"
        )


class DeepSeekCredsError(Exception):
    """DeepSeek credentials are missing or malformed."""


def load() -> DeepSeekCreds:
    """Load and validate DeepSeek credentials from ``.env.deepseek``.

    Returns:
        DeepSeekCreds: validated key/base_url/model triple.

    Raises:
        FileNotFoundError: if ``.env.deepseek`` is not on disk -- the autorun-safe
            default (autonomous sessions never carry the key).
        DeepSeekCredsError: if the file exists but is malformed (missing/extra key,
            unfilled placeholder, bad key shape, non-https base_url, empty model).
    """
    if not _ENV_PATH.exists():
        raise FileNotFoundError(
            f"DeepSeek credentials not found at {_ENV_PATH}.\n"
            "This is expected during autonomous runs. To run the DeepSeek paths:\n"
            "  1. Get an API key at https://platform.deepseek.com/api_keys\n"
            f"  2. Copy {_ENV_TEMPLATE_PATH.name} to .env.deepseek in this directory and fill it in.\n"
            "  3. Re-run from a supervised session (NOT autonomous_run.sh)."
        )
    raw = _parse_env_file(_ENV_PATH)
    _validate_keys(raw)
    key = raw["DEEPSEEK_API_KEY"].strip()
    base_url = raw["DEEPSEEK_BASE_URL"].strip()
    model = raw["DEEPSEEK_MODEL"].strip()
    _validate_values(key, base_url, model)
    return DeepSeekCreds(key=key, base_url=base_url, model=model)


# --- Internals ---------------------------------------------------------------


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a KEY=VALUE file. Skips blank lines and ``#`` comments. Strips matched
    outer quotes. No shell expansion, no command substitution, no multi-line values.
    """
    out: dict[str, str] = {}
    for lineno, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise DeepSeekCredsError(
                f"{path.name}:{lineno}: expected KEY=VALUE, got {raw_line!r}"
            )
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (len(value) >= 2) and (
            (value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")
        ):
            value = value[1:-1]
        if key in out:
            raise DeepSeekCredsError(f"{path.name}:{lineno}: duplicate key {key!r}")
        out[key] = value
    return out


def _validate_keys(raw: dict[str, str]) -> None:
    """Reject any key set that is not exactly the locked 3-key schema."""
    seen = frozenset(raw.keys())
    missing = REQUIRED_KEYS - seen
    extra = seen - REQUIRED_KEYS
    if missing:
        raise DeepSeekCredsError(
            f"{_ENV_PATH.name} missing required keys: {sorted(missing)}"
        )
    if extra:
        raise DeepSeekCredsError(
            f"{_ENV_PATH.name} contains unexpected keys: {sorted(extra)}. "
            "The DeepSeek creds schema is locked; unknown keys are rejected."
        )


def _validate_values(key: str, base_url: str, model: str) -> None:
    """Validate the shape of each credential value (loud failure on drift)."""
    if key == _PLACEHOLDER:
        raise DeepSeekCredsError(
            "DEEPSEEK_API_KEY is still the template placeholder -- paste your real "
            "key from https://platform.deepseek.com/api_keys."
        )
    if not _KEY_SHAPE.match(key):
        raise DeepSeekCredsError(
            "DEEPSEEK_API_KEY must look like a DeepSeek key ('sk-' + >=8 url-safe chars)."
        )
    if not base_url.startswith("https://"):
        raise DeepSeekCredsError(
            f"DEEPSEEK_BASE_URL must be an https URL (got {base_url!r})."
        )
    if not model:
        raise DeepSeekCredsError(
            "DEEPSEEK_MODEL must be a non-empty model id (e.g. 'deepseek-chat')."
        )


def _mask_key(key: str) -> str:
    """Mask an API key so at most the ``sk-`` prefix shows (never the secret body)."""
    if not key.startswith("sk-"):
        return "****"
    return "sk-****"
