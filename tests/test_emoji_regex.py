"""Regression tests for emoji regex -- ensures no BMP false positives."""
import sys
from pathlib import Path

# Import the regex from both modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".claude" / "hooks"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def test_star_not_matched() -> None:
    """U+2605 BLACK STAR must not match (was a false positive with BMP ranges)."""
    from check_emoji_files import _EMOJI_RE
    assert not _EMOJI_RE.search("\u2605"), "U+2605 BLACK STAR should not match"


def test_checkmark_not_matched() -> None:
    """U+2713 CHECK MARK must not match."""
    from check_emoji_files import _EMOJI_RE
    assert not _EMOJI_RE.search("\u2713"), "U+2713 CHECK MARK should not match"


def test_arrow_not_matched() -> None:
    """U+2794 HEAVY WIDE-HEADED RIGHTWARDS ARROW must not match."""
    from check_emoji_files import _EMOJI_RE
    assert not _EMOJI_RE.search("\u2794"), "U+2794 arrow should not match"


def test_real_emoji_matched() -> None:
    """U+1F600 GRINNING FACE must match."""
    from check_emoji_files import _EMOJI_RE
    assert _EMOJI_RE.search("\U0001f600"), "U+1F600 emoji should match"


def test_zwj_matched() -> None:
    """U+200D ZERO WIDTH JOINER must match (emoji sequence component)."""
    from check_emoji_files import _EMOJI_RE
    assert _EMOJI_RE.search("\u200d"), "ZWJ should match"


def test_vs16_matched() -> None:
    """U+FE0F VARIATION SELECTOR-16 must match (emoji presentation selector)."""
    from check_emoji_files import _EMOJI_RE
    assert _EMOJI_RE.search("\ufe0f"), "VS16 should match"


def test_rocket_matched() -> None:
    """U+1F680 ROCKET must match."""
    from check_emoji_files import _EMOJI_RE
    assert _EMOJI_RE.search("\U0001f680"), "U+1F680 ROCKET should match"
