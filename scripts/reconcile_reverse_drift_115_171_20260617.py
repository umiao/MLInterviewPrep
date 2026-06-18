"""Reconcile the reverse-drift on nodes 115 / 171 (T-P1-923).

Source: T-P1-918 triage (``logs/review/T-P1-918_reverse_drift_triage_
20260617.md``) + the T-P0-914 root-cause note. Both leaf nodes carry
``status='review', progress_pct=100`` with **0 checkboxes checked** and
all-NULL timestamps -- an untraceable pre-Invariant-3 direct DB write,
NOT earned mastery. The user (2026-06-17, per the 918 journey) confirmed
neither topic is actually mastered, so the trustworthy state is the
0-checked reality: ``progress_pct=0, status='not_started'``.

Scope (pinned, by canonical key = ``path``)::

    pillar4.nlp_llm_applications.text_classification   (node 115, 0/16)
    pillar7.probability_statistics.bayesian_inference  (node 171, 0/7)

Signature guard (non-destructive idempotency)
---------------------------------------------
A target is reset **only if it still exhibits the reverse-drift
signature** -- ``count_checkboxes(description).checked == 0`` AND
(``progress_pct > 0`` OR ``status != 'not_started'``). If the user later
genuinely studies the topic and checks boxes via the app (so
``checked > 0``), this script SKIPS it -- it will never clobber legitimately
earned progress. After a successful reset the signature no longer matches,
so a re-run is a no-op (Invariant-3 idempotency).

This deliberately does NOT touch node 69 (self-resolved to mastered 1/1)
or any parent/derived-pct node -- they are out of scope per the 918
false-positive note and are not in this script's pinned path list.

Modes
-----
* ``--apply`` (DEFAULT): timestamped ``mle_prep.db`` ``.bak`` -> commit ->
  append a structured JSONL audit record. Apply is the default because
  the human gate already happened (the 918 per-node user verdict); this
  is the sanctioned execution of that decision.
* ``--dry-run``: compute the would-change diff in an uncommitted
  transaction, roll back (zero DB writes), print the diff. Preview only.

Run (apply -- the T-P1-923 deliverable)::

    python scripts/reconcile_reverse_drift_115_171_20260617.py

Run (preview)::

    python scripts/reconcile_reverse_drift_115_171_20260617.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib.framework_progress import count_checkboxes  # noqa: E402

from src.backend.config import get_settings  # noqa: E402
from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402

# Canonical key = path (Invariant 3); node ids are shown for reference only.
TARGET_PATHS: tuple[str, ...] = (
    "pillar4.nlp_llm_applications.text_classification",  # node 115
    "pillar7.probability_statistics.bayesian_inference",  # node 171
)

AUDIT_PATH = PROJECT_ROOT / "logs" / "reconcile_reverse_drift_audit.jsonl"


@dataclass(frozen=True)
class ResetDelta:
    """One node that would change, with before/after."""

    node_id: int
    path: str
    before_status: str
    before_pct: float
    after_status: str
    after_pct: float
    checked: int
    total: int


def resolve_db_path() -> Path:
    """Resolve the live SQLite file from ``settings.DATABASE_URL`` (for .bak)."""
    url = get_settings().DATABASE_URL
    prefix = "sqlite:///"
    if url.startswith(prefix):
        raw = url[len(prefix):]
        p = Path(raw)
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()
    return (PROJECT_ROOT / "data" / "mle_prep.db").resolve()


def compute_resets(db) -> list[ResetDelta]:
    """Apply the signature-guarded reset in-session; return the deltas.

    Mutates matching nodes in the caller's (uncommitted) transaction. The
    caller owns commit (apply) vs rollback (dry-run).

    Args:
        db: An active, uncommitted SQLAlchemy session.

    Returns:
        One :class:`ResetDelta` per node actually changed (skips already-
        clean nodes and any node with checked > 0).
    """
    deltas: list[ResetDelta] = []
    for path in TARGET_PATHS:
        node = (
            db.query(FrameworkNode)
            .filter(FrameworkNode.path == path)
            .one_or_none()
        )
        if node is None:
            print(f"[WARN] target path not found, skipping: {path}")
            continue
        checked, total = count_checkboxes(node.description)
        pct = float(node.progress_pct or 0.0)
        # Non-destructive guard: only reset the reverse-drift signature.
        if checked > 0:
            print(
                f"[SKIP] {node.id} {path}: {checked}/{total} boxes checked "
                f"-- legit progress, NOT clobbered"
            )
            continue
        if pct == 0.0 and node.status == "not_started":
            print(f"[SKIP] {node.id} {path}: already pct=0/not_started (no-op)")
            continue
        delta = ResetDelta(
            node_id=node.id,
            path=path,
            before_status=node.status,
            before_pct=pct,
            after_status="not_started",
            after_pct=0.0,
            checked=checked,
            total=total,
        )
        node.status = "not_started"
        node.progress_pct = 0.0
        # Timestamps already NULL (never earned); leave as-is.
        deltas.append(delta)
    return deltas


def append_audit_record(deltas: list[ResetDelta], applied_at: datetime,
                        backup: Path) -> None:
    """Append one structured JSONL audit record (apply only)."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": applied_at.isoformat(),
        "tool": "reconcile_reverse_drift_115_171_20260617.py",
        "task": "T-P1-923",
        "backup": str(backup),
        "deltas": [
            {
                "node_id": d.node_id,
                "path": d.path,
                "before": {"status": d.before_status, "progress_pct": d.before_pct},
                "after": {"status": d.after_status, "progress_pct": d.after_pct},
                "boxes": f"{d.checked}/{d.total}",
            }
            for d in deltas
        ],
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def backup_db(db_path: Path) -> Path:
    """Copy the live DB to a timestamped ``.bak`` (apply only)."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = db_path.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(db_path, dst)
    return dst


def _print_summary(deltas: list[ResetDelta], mode: str) -> None:
    """Print a one-screen console summary of the diff."""
    print(f"[INFO] mode={mode} targets={len(TARGET_PATHS)} changed={len(deltas)}")
    for d in deltas:
        print(
            f"[DIFF] {d.node_id} {d.path} "
            f"status {d.before_status}->{d.after_status} "
            f"pct {d.before_pct}->{d.after_pct} (boxes {d.checked}/{d.total})"
        )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    ``--apply`` (default) backs up the DB, commits the signature-guarded
    reset, and appends a JSONL audit record. ``--dry-run`` computes the
    diff in an uncommitted transaction and rolls back (zero DB writes).

    Args:
        argv: Optional argv override (for tests). Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code (0 success, 1 failure).
    """
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile reverse-drift on nodes 115/171 to pct=0/not_started "
            "(signature-guarded, idempotent). Apply is the default."
        )
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true",
                       help="(default) .bak -> commit -> audit log")
    group.add_argument("--dry-run", action="store_true",
                       help="compute + print the diff; ZERO DB writes")
    args = parser.parse_args(argv)
    apply = not args.dry_run  # apply is the default
    mode = "apply" if apply else "dry-run"

    init_db()
    db = SessionLocal()
    try:
        deltas = compute_resets(db)
        now = datetime.now()
        if apply and deltas:
            db_path = resolve_db_path()
            if not db_path.exists():
                db.rollback()
                print(f"[FAIL] DB not found for backup: {db_path}")
                return 1
            backup = backup_db(db_path)
            print(f"[INFO] DB backup -> {backup.name}")
            db.commit()
            append_audit_record(deltas, now, backup)
            print(f"[INFO] audit appended -> {AUDIT_PATH.name}")
        else:
            db.rollback()  # dry-run, or apply with nothing to change
        _print_summary(deltas, mode)
        print(f"[PASS] {mode} complete")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
