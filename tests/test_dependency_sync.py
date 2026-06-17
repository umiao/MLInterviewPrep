"""Regression guard for the dependency source-of-truth invariant (T-P2-878).

CLAUDE.md mandates that ``pyproject.toml`` (canonical) and ``requirements.txt``
list the same pinned dependencies. The two files are maintained by hand, so
drift is invisible until ``pip install -e .[dev]`` and ``pip install -r
requirements.txt`` diverge.

T-P2-878 was filed as a false positive: the 2026-05-14 audit scanned only
``[project].dependencies`` and missed the dev tools that already lived in the
``[project.optional-dependencies].dev`` extra (added back in T-P0-1). These
tests assert the *whole* pyproject surface (runtime + dev + scraper) so the
audit's blind spot cannot recur.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_pyproject_specs() -> set[str]:
    """Return every pinned spec across pyproject runtime + optional extras."""
    with (_PROJECT_ROOT / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    specs: set[str] = set(data["project"]["dependencies"])
    for extra in data["project"].get("optional-dependencies", {}).values():
        specs.update(extra)
    return specs


def _load_requirements_specs() -> set[str]:
    """Return every non-comment, non-blank pin from requirements.txt."""
    specs: set[str] = set()
    text = (_PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            specs.add(stripped)
    return specs


def test_requirements_is_subset_of_pyproject() -> None:
    """Every requirements.txt pin must appear somewhere in pyproject.toml."""
    req = _load_requirements_specs()
    pyproject = _load_pyproject_specs()
    missing = req - pyproject
    assert not missing, (
        f"requirements.txt pins absent from pyproject.toml: {sorted(missing)}. "
        "pyproject.toml is canonical -- add them there too (CLAUDE.md "
        "dependency source-of-truth rule)."
    )


def test_dev_tools_present_in_pyproject_dev_extra() -> None:
    """The 4 dev tools (T-P2-878) live in the [project.optional-dependencies].dev extra."""
    with (_PROJECT_ROOT / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    dev_extra = set(data["project"]["optional-dependencies"]["dev"])
    expected = {
        "ruff==0.15.4",
        "pytest==7.4.4",
        "pytest-asyncio==0.23.3",
        "pyyaml==6.0",
    }
    missing = expected - dev_extra
    assert not missing, f"dev extra missing tools: {sorted(missing)}"
