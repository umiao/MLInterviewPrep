"""Meta test: three emoji regex definitions must stay byte-identical.

The emoji scanner regex lives in three places that MUST stay in sync:
- scripts/check_emoji.py (CI standalone scan)
- scripts/check_emoji_files.py (pre-commit staged-files scan)
- .claude/hooks/lint_check.py (Claude stop hook scan)

If any two diverge, users see checks that pass in one path and fail in another.
This test locks them by compiling each module and comparing _EMOJI_RE.pattern bytes.
"""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, f"could not load spec for {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_three_emoji_regex_patterns_byte_equal():
    ce = _load_module("_emoji_ce", REPO_ROOT / "scripts" / "check_emoji.py")
    cef = _load_module("_emoji_cef", REPO_ROOT / "scripts" / "check_emoji_files.py")

    # lint_check.py imports hook_utils from its own directory; add it to path.
    hooks_dir = REPO_ROOT / ".claude" / "hooks"
    sys.path.insert(0, str(hooks_dir))
    try:
        lc = _load_module("_emoji_lc", hooks_dir / "lint_check.py")
    finally:
        sys.path.remove(str(hooks_dir))

    a, b, c = ce._EMOJI_RE.pattern, cef._EMOJI_RE.pattern, lc._EMOJI_RE.pattern
    assert a == b, f"scripts/check_emoji.py regex drifted from check_emoji_files.py\n  a={a!r}\n  b={b!r}"
    assert b == c, f"scripts/check_emoji_files.py regex drifted from lint_check.py\n  b={b!r}\n  c={c!r}"
