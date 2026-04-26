"""Tests for scripts/check_emoji.py CLI argument handling (T-P2-607).

Covers the four CLI branches added by F-2:
- single-file-dirty: passing a file with emoji -> exit 1, file path in stdout
- single-file-clean: passing a clean file -> exit 0
- bare invocation: zero args still walks the repo (CI compatibility)
- nonexistent-path: prints [WARN] but does not crash
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_emoji.py"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def test_single_file_dirty_exits_one(tmp_path: Path) -> None:
    """File containing a real emoji must trigger rc=1 and print the path."""
    dirty = tmp_path / "bad.py"
    dirty.write_text("marker = '\U0001f600'\n", encoding="utf-8")

    proc = _run(str(dirty))

    assert proc.returncode == 1, (
        f"expected rc=1 for dirty file, got {proc.returncode}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "bad.py" in proc.stdout, (
        f"expected file path in stdout report, got:\n{proc.stdout}"
    )
    assert "Traceback" not in proc.stderr, f"unexpected crash:\n{proc.stderr}"


def test_single_file_clean_exits_zero(tmp_path: Path) -> None:
    """File with no emoji must trigger rc=0 ([OK] path)."""
    clean = tmp_path / "good.py"
    clean.write_text("marker = 'plain ascii'\n", encoding="utf-8")

    proc = _run(str(clean))

    assert proc.returncode == 0, (
        f"expected rc=0 for clean file, got {proc.returncode}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "[OK]" in proc.stdout, f"expected [OK] message in stdout, got:\n{proc.stdout}"


def test_directory_argument_scoped_to_subtree(tmp_path: Path) -> None:
    """A directory arg restricts the scan; sibling tree pollution must not leak in."""
    sub = tmp_path / "scan_me"
    sub.mkdir()
    (sub / "ok.py").write_text("ascii_only = 1\n", encoding="utf-8")

    sibling = tmp_path / "untouched"
    sibling.mkdir()
    (sibling / "bad.py").write_text("emoji = '\U0001f600'\n", encoding="utf-8")

    proc = _run(str(sub))

    assert proc.returncode == 0, (
        f"sibling tree leaked into scan; rc={proc.returncode}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )


def test_nonexistent_path_warns_not_crashes(tmp_path: Path) -> None:
    """Bad path must print [WARN] and exit 0 (no targets means no hits)."""
    proc = _run(str(tmp_path / "does_not_exist"))

    assert proc.returncode == 0, (
        f"unknown path should not fail scan; rc={proc.returncode}\n"
        f"stderr:\n{proc.stderr}"
    )
    assert "[WARN]" in proc.stderr, f"expected [WARN] in stderr, got:\n{proc.stderr}"
    assert "Traceback" not in proc.stderr, f"unexpected crash:\n{proc.stderr}"
