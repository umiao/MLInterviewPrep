"""Smoke test for ``scripts/_lc_import_helpers.warn_if_missing_family``.

Verifies:
  1. Missing/blank family -> warn + TSV row appended (return True).
  2. Present family -> no warn, no TSV row (return False).
  3. Log file uses tab-separated fields in the documented order.

Usage:
    python scripts/_smoke_lc_import_helpers.py
"""
from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stderr
from pathlib import Path

_HELPER_PATH = Path(__file__).resolve().parent / "_lc_import_helpers.py"
_spec = importlib.util.spec_from_file_location("_lc_import_helpers", _HELPER_PATH)
assert _spec is not None and _spec.loader is not None
_lc_import_helpers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lc_import_helpers)
warn_if_missing_family = _lc_import_helpers.warn_if_missing_family


def main() -> None:
    """Run smoke cases against a temporary quarantine file."""
    project_root = Path(__file__).resolve().parent.parent
    tmp_log = project_root / "logs" / "_smoke_lc_family_quarantine.tsv"
    if tmp_log.exists():
        tmp_log.unlink()

    original_path = _lc_import_helpers.QUARANTINE_PATH
    _lc_import_helpers.QUARANTINE_PATH = tmp_log
    try:
        # Case 1: missing family (None) -> flagged.
        buf1 = io.StringIO()
        with redirect_stderr(buf1):
            flagged = warn_if_missing_family(
                lc_id=9999,
                title="Smoke Missing",
                family=None,
                source_script="_smoke_lc_import_helpers.py",
            )
        assert flagged is True, "expected flag=True for family=None"
        assert "[WARN] LC 9999" in buf1.getvalue(), "missing stderr WARN"

        # Case 2: blank family ("   ") -> flagged.
        buf2 = io.StringIO()
        with redirect_stderr(buf2):
            flagged_blank = warn_if_missing_family(
                lc_id=9998,
                title="Smoke Blank",
                family="   ",
                source_script="_smoke_lc_import_helpers.py",
            )
        assert flagged_blank is True, "expected flag=True for blank family"

        # Case 3: present family -> not flagged, stderr silent.
        buf3 = io.StringIO()
        with redirect_stderr(buf3):
            flagged_ok = warn_if_missing_family(
                lc_id=9997,
                title="Smoke With Family",
                family="stateful_ds_design",
                source_script="_smoke_lc_import_helpers.py",
            )
        assert flagged_ok is False, "expected flag=False when family set"
        assert buf3.getvalue() == "", "stderr should be silent when family set"

        # Verify TSV file contents (2 rows appended, 4 columns each).
        lines = tmp_log.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2, f"expected 2 TSV rows, got {len(lines)}"
        for line in lines:
            cols = line.split("\t")
            assert len(cols) == 4, f"expected 4 TSV cols, got {len(cols)}: {line!r}"
        ids = {line.split("\t")[1] for line in lines}
        assert ids == {"9999", "9998"}, f"unexpected lc_ids in log: {ids}"
        # Present-family case must NOT be in the log.
        assert "9997" not in tmp_log.read_text(encoding="utf-8")

        print("[PASS] _lc_import_helpers smoke checks passed.")
        print(f"  quarantine rows appended: {len(lines)}")
    finally:
        _lc_import_helpers.QUARANTINE_PATH = original_path
        if tmp_log.exists():
            tmp_log.unlink()


if __name__ == "__main__":
    main()
