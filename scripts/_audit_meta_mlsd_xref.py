"""Closing-gate xref audit (T-P0-907): assert every sd:// reference in cd96
and cd94 resolves to a system_designs.slug, and every cd:// reference resolves
to a company_documents.id.

Exit codes:
  0  all references resolve
  1  one or more references unresolved
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    sd_slugs = {r["slug"] for r in cur.execute(
        "SELECT slug FROM system_designs").fetchall()}
    cd_ids = {r["id"] for r in cur.execute(
        "SELECT id FROM company_documents").fetchall()}

    target_doc_ids = [94, 96]
    all_pass = True
    for doc_id in target_doc_ids:
        row = cur.execute(
            "SELECT id, title, content FROM company_documents WHERE id = ?",
            (doc_id,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] cd://{doc_id} not found")
            all_pass = False
            continue
        content = row["content"] or ""
        sd_refs = re.findall(r"sd://([A-Za-z0-9_\-]+)", content)
        cd_refs = re.findall(r"cd://(\d+)", content)
        sd_unique = sorted(set(sd_refs))
        cd_unique = sorted(set(int(x) for x in cd_refs))
        print(f"\n=== cd://{doc_id} {row['title']!r} ===")
        print(f"  sd:// refs (unique): {len(sd_unique)}")
        sd_bad = [s for s in sd_unique if s not in sd_slugs]
        cd_bad = [c for c in cd_unique if c not in cd_ids]
        for s in sd_unique:
            mark = "[OK]" if s in sd_slugs else "[FAIL]"
            print(f"    {mark} sd://{s}")
        print(f"  cd:// refs (unique): {len(cd_unique)}")
        for c in cd_unique:
            mark = "[OK]" if c in cd_ids else "[FAIL]"
            print(f"    {mark} cd://{c}")
        if sd_bad:
            print(f"  [FAIL] {len(sd_bad)} unresolved sd:// slug(s): {sd_bad}")
            all_pass = False
        if cd_bad:
            print(f"  [FAIL] {len(cd_bad)} unresolved cd:// id(s): {cd_bad}")
            all_pass = False
    print()
    if all_pass:
        print("[OK] all cd94/cd96 sd:// + cd:// references resolve.")
        return 0
    print("[FAIL] one or more unresolved references")
    return 1


if __name__ == "__main__":
    sys.exit(main())
