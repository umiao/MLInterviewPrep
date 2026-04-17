"""Scan for orphan single-dollar signs in doc content."""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path


def check_dollar_pairs(content: str) -> int:
    p = re.sub(r"\$\$.*?\$\$", "", content, flags=re.DOTALL)
    p = re.sub(r"\$[^\$\n]+\$", "", p)
    return p.count("$")


def main() -> int:
    db = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
    ids = [int(x) for x in sys.argv[1:]] or [55, 56, 60, 61]
    conn = sqlite3.connect(str(db))
    try:
        for did in ids:
            row = conn.execute(
                "SELECT content FROM company_documents WHERE id = ?", (did,)
            ).fetchone()
            if row is None:
                print(f"[MISSING] doc {did}")
                continue
            orphans = check_dollar_pairs(row[0])
            status = "[PASS]" if orphans == 0 else "[FAIL]"
            print(f"{status} doc {did}: orphan $ count = {orphans}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
