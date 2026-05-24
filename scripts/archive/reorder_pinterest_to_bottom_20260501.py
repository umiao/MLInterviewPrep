"""Move Pinterest SD modules to display_order 200-206 (bottom of list).

Pinterest 7 modules currently sit at display_order 100-106, interleaving with
the interview-* modules in the SystemDesignList grid. The user wants them in
their own section at the bottom.

Mapping (idempotent UPSERT-style — sets exact target, safe to re-run):
  pinterest-ad-ctr            100 -> 200
  pinterest-embeddings        101 -> 201
  pinterest-chatbot-pins      102 -> 202
  pinterest-pin-ranking       103 -> 203
  pinterest-pins-search       104 -> 204
  pinterest-notification-reco 105 -> 205
  pinterest-catalog-bulk-update 106 -> 206
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

REORDER = {
    "pinterest-ad-ctr": 200,
    "pinterest-embeddings": 201,
    "pinterest-chatbot-pins": 202,
    "pinterest-pin-ranking": 203,
    "pinterest-pins-search": 204,
    "pinterest-notification-reco": 205,
    "pinterest-catalog-bulk-update": 206,
}


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        changed = 0
        for slug, target in REORDER.items():
            row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
            if row is None:
                print(f"[WARN] missing slug: {slug}")
                continue
            if row.display_order == target:
                print(f"[NOOP] {slug}: already at {target}")
                continue
            print(f"[UPDATE] {slug}: {row.display_order} -> {target}")
            row.display_order = target
            changed += 1
        db.commit()
        print(f"[DONE] reordered {changed} pinterest modules.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
