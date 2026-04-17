"""Compute CJK-ratio on prose-only content (strips LaTeX/code/tables/headings)."""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path


def prose_only(content: str) -> str:
    p = re.sub(r"\$\$.*?\$\$", "", content, flags=re.DOTALL)
    p = re.sub(r"\$[^\$\n]*?\$", "", p)
    p = re.sub(r"```.*?```", "", p, flags=re.DOTALL)
    p = re.sub(r"`[^`]*`", "", p)
    p = re.sub(r"^\|.*$", "", p, flags=re.MULTILINE)
    p = re.sub(r"^#+\s.*$", "", p, flags=re.MULTILINE)
    p = re.sub(r"<!--.*?-->", "", p, flags=re.DOTALL)
    return p


def cjk_ratio(text: str) -> tuple[float, int, int]:
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    latin = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total = cjk + latin
    return (cjk / total if total else 0.0, cjk, latin)


def main() -> int:
    db_path = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
    ids = [int(x) for x in sys.argv[1:]] or [55, 56, 60, 61]
    conn = sqlite3.connect(str(db_path))
    try:
        for did in ids:
            row = conn.execute(
                "SELECT title, content FROM company_documents WHERE id = ?", (did,)
            ).fetchone()
            if row is None:
                print(f"[MISSING] doc {did}")
                continue
            title, content = row
            prose = prose_only(content)
            ratio, cjk, latin = cjk_ratio(prose)
            status = "[PASS]" if ratio >= 0.60 else "[FAIL]"
            print(
                f"{status} doc {did}: prose_cjk={ratio:.1%} cjk={cjk} latin={latin} "
                f"({title})"
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
