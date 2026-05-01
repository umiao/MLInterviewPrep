"""Copy embedded cheatsheet content from other sections into cheat_sheet column.

Background: 4 SDs were authored before the cheat_sheet column existed
(T-P1-641 added it). Their cheatsheet content lives inside dataflow or
verbal_outline. Frontend TOC has a 'cheat_sheet' link that currently shows
empty placeholder for these — misleading.

Strategy: COPY (not move) the embedded section into cheat_sheet column.
The existing inline content stays in place to preserve narrative flow of
verbal_outline / dataflow. Idempotent — re-running overwrites cheat_sheet
with the latest extracted content.

Targets:
  id=8  ml-system-design-patterns           dataflow:技术决策速查表
  id=23 interview-price-drop-tracker        verbal_outline:容量速记卡
  id=32 pinterest-pin-ranking               verbal_outline:45-Minute Timing Cheat Sheet
  id=35 pinterest-catalog-bulk-update       verbal_outline:45-min 时间分配 cheat sheet
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

EXTRACTIONS = [
    {
        "slug": "ml-system-design-patterns",
        "source_col": "dataflow",
        "pattern": r"(技术决策速查表[\s\S]+?)(?=\n## |\Z)",
    },
    {
        "slug": "interview-price-drop-tracker",
        "source_col": "verbal_outline",
        "pattern": r"(容量速记卡[\s\S]+?)(?=\n## |\Z)",
    },
    {
        "slug": "pinterest-pin-ranking",
        "source_col": "verbal_outline",
        "pattern": r"(45-Minute Timing Cheat Sheet[\s\S]+?)(?=\n## |\Z)",
    },
    {
        "slug": "pinterest-catalog-bulk-update",
        "source_col": "verbal_outline",
        "pattern": r"(45-min 时间分配 cheat sheet[\s\S]+?)(?=\n## |\Z)",
    },
]

PROVENANCE_HEADER = (
    "<!-- extracted_from={col} on 2026-05-01 by extract_embedded_cheatsheets_20260501.py -->\n\n"
)


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        for spec in EXTRACTIONS:
            slug = spec["slug"]
            col = spec["source_col"]
            pat = spec["pattern"]

            row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
            if row is None:
                print(f"[ERROR] missing slug: {slug}")
                continue

            source = getattr(row, col) or ""
            m = re.search(pat, source)
            if not m:
                print(f"[ERROR] pattern not found in {slug}.{col}")
                continue

            extracted = m.group(1).strip()
            new_value = PROVENANCE_HEADER.format(col=col) + extracted + "\n"

            old = row.cheat_sheet or ""
            action = "NOOP" if old == new_value else ("INSERT" if not old else "UPDATE")
            row.cheat_sheet = new_value

            print(f"[{action}] {slug}: cheat_sheet = {len(new_value)} chars (from {col})")

        db.commit()
        print("[DONE] embedded cheatsheets extracted into cheat_sheet column.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
