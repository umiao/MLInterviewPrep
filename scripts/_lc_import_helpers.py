"""Helper for LC import scripts to flag rows inserted without a family.

Prevents the rot of `problems.family=NULL` from growing silently. Each LC
import call site should invoke ``warn_if_missing_family`` immediately before
or after the INSERT: missing/blank family produces a stderr WARN and appends
a row to ``logs/lc_family_quarantine.tsv``. Non-blocking -- the insert itself
is not aborted.

Quarantine file format (tab-separated, append-only):
    timestamp\tlc_id\ttitle\tsource_script
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUARANTINE_PATH = PROJECT_ROOT / "logs" / "lc_family_quarantine.tsv"


def warn_if_missing_family(
    lc_id: int | str | None,
    title: str | None,
    family: str | None,
    source_script: str,
) -> bool:
    """Warn and quarantine-log when an LC row is being inserted without a family.

    Args:
        lc_id: LeetCode problem id (int or numeric string). ``None`` is accepted
            but logged as the literal string ``"None"``.
        title: Problem title; logged for human triage.
        family: The family value about to be persisted. Treated as missing when
            ``None`` or an empty/whitespace-only string.
        source_script: Short label identifying the caller (e.g. module name).
            Used to attribute quarantine rows back to their origin script.

    Returns:
        ``True`` when the row was flagged (missing family), ``False`` otherwise.

    Side effects:
        On a missing family: prints ``[WARN] LC {id} inserted without family;
        logged to quarantine.`` to stderr and appends one TSV row to
        ``logs/lc_family_quarantine.tsv`` (creating the parent ``logs/``
        directory if needed). Never raises -- always non-blocking.
    """
    if family is not None and str(family).strip():
        return False

    lc_str = str(lc_id) if lc_id is not None else "None"
    title_str = (title or "").replace("\t", " ").replace("\n", " ")
    source_str = source_script.replace("\t", " ")
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        QUARANTINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(QUARANTINE_PATH, "a", encoding="utf-8") as fh:
            fh.write(f"{ts}\t{lc_str}\t{title_str}\t{source_str}\n")
    except OSError as exc:
        print(
            f"[WARN] LC {lc_str} inserted without family; quarantine log "
            f"write failed: {exc}",
            file=sys.stderr,
        )
        return True

    print(
        f"[WARN] LC {lc_str} inserted without family; logged to quarantine.",
        file=sys.stderr,
    )
    return True
