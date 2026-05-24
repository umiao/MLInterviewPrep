"""Regression tests for scripts/lint_script_lifecycle.py (T-P2-353 follow-up).

The T-P2-353 migration was bitten by static-only reference detection: an
``importlib.import_module("x")`` in a test was invisible to a grep for
``import x`` / ``from x import``, so a still-used script was archived and only
a pytest *collection error* caught it. These tests lock in the gap-closer:

  * a retire-time live-reference scan that sees static AND dynamic imports,
  * the PINNED outcome that protects a referenced (or explicitly pinned)
    script from auto-retirement even when its SAFE_DELETE_AFTER has expired,
  * an unreferenced expired script still surfacing as CLEANUP_CANDIDATE.
"""
from __future__ import annotations

import datetime as _dt
import importlib.util
import sys
from pathlib import Path

import pytest

_LINT = Path(__file__).resolve().parents[1] / "scripts" / "lint_script_lifecycle.py"


def _load_lint():
    spec = importlib.util.spec_from_file_location("lint_script_lifecycle", _LINT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # @dataclass introspection needs this registered
    spec.loader.exec_module(mod)
    return mod


lint = _load_lint()


def _make_repo(tmp_path: Path) -> Path:
    (tmp_path / "scripts" / "seed").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    return tmp_path


EXPIRED = "# SAFE_DELETE_AFTER: 2020-01-01\n"
TODAY = _dt.date(2026, 5, 24)


def _outcomes(tmp_path: Path) -> dict[str, str]:
    findings = lint.classify(
        tmp_path / "scripts", repo=tmp_path, today=TODAY, ref_scan=True,
    )
    return {Path(f.path).name: f.outcome for f in findings}


def test_dynamic_import_pins_an_expired_script(tmp_path):
    """importlib.import_module('x') must protect x from retirement."""
    repo = _make_repo(tmp_path)
    (repo / "scripts" / "seed" / "dyn_used.py").write_text(
        EXPIRED + "x = 1\n", encoding="utf-8")
    (repo / "tests" / "test_uses_it.py").write_text(
        "import importlib\n"
        "m = importlib.import_module('dyn_used')\n",
        encoding="utf-8",
    )
    out = _outcomes(repo)
    assert out["dyn_used.py"] == lint.PINNED, (
        "dynamic import_module reference should pin, not retire")


def test_static_import_pins_an_expired_script(tmp_path):
    repo = _make_repo(tmp_path)
    (repo / "scripts" / "seed" / "stat_used.py").write_text(
        EXPIRED + "y = 2\n", encoding="utf-8")
    (repo / "scripts" / "seed" / "caller.py").write_text(
        "from stat_used import y\n", encoding="utf-8")
    out = _outcomes(repo)
    assert out["stat_used.py"] == lint.PINNED


def test_unreferenced_expired_script_is_cleanup_candidate(tmp_path):
    """The whole point still works: a truly-dead expired script is flagged."""
    repo = _make_repo(tmp_path)
    (repo / "scripts" / "seed" / "dead.py").write_text(
        EXPIRED + "z = 3\n", encoding="utf-8")
    out = _outcomes(repo)
    assert out["dead.py"] == lint.CLEANUP_CANDIDATE


def test_pinned_by_marker_protects_even_unreferenced(tmp_path):
    repo = _make_repo(tmp_path)
    (repo / "scripts" / "seed" / "ticketed.py").write_text(
        EXPIRED + "# PINNED_BY: T-P1-876\nq = 4\n", encoding="utf-8")
    out = _outcomes(repo)
    assert out["ticketed.py"] == lint.PINNED


def test_pinned_is_not_a_strict_finding(tmp_path):
    """--strict must not trip on a pinned (in-use) script."""
    repo = _make_repo(tmp_path)
    (repo / "scripts" / "seed" / "ticketed.py").write_text(
        EXPIRED + "# PINNED_BY: T-1\nq = 4\n", encoding="utf-8")
    findings = lint.classify(repo / "scripts", repo=repo, today=TODAY)
    assert not any(f.is_finding for f in findings)


def test_markdown_mention_does_not_pin(tmp_path):
    """A prose mention in a .md is not a dependency and must not pin."""
    repo = _make_repo(tmp_path)
    (repo / "scripts" / "seed" / "dead.py").write_text(
        EXPIRED + "z = 3\n", encoding="utf-8")
    (repo / "PROGRESS.md").write_text(
        "Ran scripts/seed/dead.py on 2026-01-01 -- see dead.py output.\n",
        encoding="utf-8",
    )
    out = _outcomes(repo)
    assert out["dead.py"] == lint.CLEANUP_CANDIDATE, (
        "markdown prose must not keep a dead script alive")


def test_archived_referrer_does_not_pin(tmp_path):
    """A reference from declared-dead code (archive/) is not a live dep."""
    repo = _make_repo(tmp_path)
    (repo / "scripts" / "archive").mkdir()
    (repo / "scripts" / "seed" / "dead.py").write_text(
        EXPIRED + "z = 3\n", encoding="utf-8")
    (repo / "scripts" / "archive" / "old.py").write_text(
        "import dead\n", encoding="utf-8")
    out = _outcomes(repo)
    assert out["dead.py"] == lint.CLEANUP_CANDIDATE


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
