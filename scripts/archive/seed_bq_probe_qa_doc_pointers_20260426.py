"""Seed probe_qa.md doc pointers into behavioral_examples.tech_terms (T-P2-584).

Adds a "Probe Q&A doc" entry to the tech_terms dict for each of the 5 golden
stories that now have probe_qa.md prep notes (EX-01, EX-15, EX-16, EX-17,
EX-30). The pointer is a relative repo path string; the /behavioral/examples
drawer renders tech_terms entries as a definition list, so the path becomes
discoverable in the UI today and the future Phase D redesign (T-P1-583) can
promote it to a clickable deeplink.

Why tech_terms (vs analogy or a new column):
  - analogy is semantic prose ("Simple Analogy" panel in the drawer); a file
    path there reads as content noise.
  - A new column would require model + Pydantic + frontend type changes for a
    pointer that the drawer already renders elsewhere.
  - tech_terms is JSON, accepts arbitrary key/value pairs, already iterates in
    ExampleDrawerContent.tsx. A "Probe Q&A doc" key is discoverable today,
    consumable by Phase D wiring.

Idempotent:
  - For each example, parse tech_terms (None -> {}), add/update the pointer
    key, JSON-equality compare. SKIP when unchanged.

DB-backup-guarded:
  - Copies the engine-bound SQLite file to <db>.bak.<timestamp>_pre_probe_qa_doc
    before any write. --no-backup to skip.

Usage:
    python scripts/seed_bq_probe_qa_doc_pointers_20260426.py [--no-backup]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.backend.database import SessionLocal, get_engine, init_db  # noqa: E402
from src.backend.models.behavioral import BehavioralExample  # noqa: E402

POINTER_KEY = "Probe Q&A doc"

POINTERS: list[tuple[str, str]] = [
    ("EX-01", "docs/behavioral_prep_notes/EX-01_probe_qa.md"),
    ("EX-15", "docs/behavioral_prep_notes/EX-15_probe_qa.md"),
    ("EX-16", "docs/behavioral_prep_notes/EX-16_probe_qa.md"),
    ("EX-17", "docs/behavioral_prep_notes/EX-17_probe_qa.md"),
    ("EX-30", "docs/behavioral_prep_notes/EX-30_probe_qa.md"),
]


def _backup_db(db_path: Path) -> Path | None:
    """Copy SQLite DB file to <db>.bak.<timestamp>_pre_probe_qa_doc."""
    if not db_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_probe_qa_doc")
    shutil.copy2(db_path, backup)
    return backup


def _resolve_db_file() -> Path | None:
    """Return the SQLite DB file path bound to the engine, or None."""
    engine = get_engine()
    url = engine.url
    if url.drivername != "sqlite":
        return None
    if url.database in (None, "", ":memory:"):
        return None
    return Path(url.database).resolve()


def _parse_tech_terms(raw: str | None) -> dict[str, str]:
    """Parse the tech_terms TEXT column into a dict (None -> {})."""
    if raw is None or raw == "":
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError(f"tech_terms is not a JSON object: {raw!r}")
    return parsed


def _serialize_tech_terms(d: dict[str, str]) -> str:
    """Serialize tech_terms dict back to JSON text (compact, deterministic)."""
    return json.dumps(d, ensure_ascii=False)


def _upsert_pointer(example: BehavioralExample, doc_path: str) -> bool:
    """Add/update the POINTER_KEY entry in tech_terms.

    Returns True if a write happened, False if SKIP.
    """
    current = _parse_tech_terms(example.tech_terms)
    desired = dict(current)
    desired[POINTER_KEY] = doc_path
    if current == desired:
        return False
    example.tech_terms = _serialize_tech_terms(desired)
    return True


def seed() -> dict:
    """Apply pointer upserts. Returns counter dict for audit."""
    engine = get_engine()
    init_db(engine)

    db = SessionLocal()
    try:
        counters = {"updated": 0, "skipped": 0}
        for ex_id, doc_path in POINTERS:
            example = (
                db.query(BehavioralExample)
                .filter(BehavioralExample.example_id == ex_id)
                .first()
            )
            if example is None:
                raise RuntimeError(f"BehavioralExample {ex_id!r} missing.")

            doc_full = REPO_ROOT / doc_path
            if not doc_full.exists():
                raise RuntimeError(
                    f"Probe Q&A doc not found: {doc_full}. "
                    "Create the .md before seeding the pointer."
                )

            if _upsert_pointer(example, doc_path):
                print(f"[DONE] tech_terms pointer set on {ex_id} -> {doc_path}")
                counters["updated"] += 1
            else:
                print(f"[SKIP] tech_terms pointer unchanged on {ex_id}")
                counters["skipped"] += 1

        db.commit()

        audit_ok = 0
        for ex_id, doc_path in POINTERS:
            example = (
                db.query(BehavioralExample)
                .filter(BehavioralExample.example_id == ex_id)
                .first()
            )
            tt = _parse_tech_terms(example.tech_terms)
            if tt.get(POINTER_KEY) == doc_path:
                audit_ok += 1
        counters["audit_ok"] = audit_ok
        return counters
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip pre-seed DB-file backup",
    )
    args = parser.parse_args(argv)

    if not args.no_backup:
        db_file = _resolve_db_file()
        if db_file is not None:
            bkp = _backup_db(db_file)
            if bkp is not None:
                print(f"[BACKUP] {bkp.name}")
        else:
            print("[BACKUP] skipped -- non-file DB URL")

    report = seed()

    print()
    print("=" * 60)
    print("Probe Q&A doc pointer seed report (T-P2-584)")
    print("=" * 60)
    print(f"pointers updated this run : {report['updated']}")
    print(f"pointers skipped (no diff): {report['skipped']}")
    print(f"Audit: pointer == target  : {report['audit_ok']}/{len(POINTERS)}")

    if report["audit_ok"] == len(POINTERS):
        print("[OK] All probe_qa.md pointers at target state.")
        return 0
    print("[FAIL] Audit failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
