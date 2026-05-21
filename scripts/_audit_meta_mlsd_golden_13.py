"""Closing-gate audit (T-P0-907): assert all 13 meta-* golden system_designs
rows pass the verbal_outline structural contract.

Per-row checks:
  - [DOMINANT] count == 1
  - [floating-twist] count in [3, 5]
  - [best-anchor] count == 1
  - [worst-anchor] count == 1
  - SD<id>_VERBAL_V1 sentinel present
  - len(verbal_outline) in [3000, 5000]

Aggregate:
  - exactly 13 rows in scope (slug LIKE 'meta-%-golden')

Exit codes:
  0  all 13 conformant
  1  one or more rows fail any gate
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
    cur.execute(
        "SELECT id, slug, display_order, verbal_outline "
        "FROM system_designs WHERE slug LIKE 'meta-%-golden' "
        "ORDER BY display_order, id"
    )
    rows = cur.fetchall()
    print(f"=== meta-* golden audit ({len(rows)} rows) ===")
    print(f"{'id':>4} {'slug':35} {'vo_len':>6} {'DOM':>3} {'FLT':>3} "
          f"{'BEST':>4} {'WRST':>4} sentinel")
    ok = 0
    fails: list[str] = []
    for r in rows:
        vo = r["verbal_outline"] or ""
        dom = len(re.findall(r"\[DOMINANT\]", vo))
        flt = len(re.findall(r"\[floating-twist\]", vo))
        best = len(re.findall(r"\[best-anchor\]", vo))
        wrst = len(re.findall(r"\[worst-anchor\]", vo))
        sent_m = re.search(r"SD\d+_VERBAL_V1", vo)
        sent_s = sent_m.group(0) if sent_m else "MISSING"
        vo_len = len(vo)
        row_fails: list[str] = []
        if dom != 1:
            row_fails.append(f"DOMINANT={dom} (want 1)")
        if not (3 <= flt <= 5):
            row_fails.append(f"floating-twist={flt} (want 3-5)")
        if best != 1:
            row_fails.append(f"best-anchor={best} (want 1)")
        if wrst != 1:
            row_fails.append(f"worst-anchor={wrst} (want 1)")
        if not sent_m:
            row_fails.append("missing SD<id>_VERBAL_V1 sentinel")
        if not (3000 <= vo_len <= 5000):
            row_fails.append(f"vo_len={vo_len} (want 3000-5000)")
        status = "[OK]" if not row_fails else "[FAIL]"
        print(f"{r['id']:>4} {r['slug']:35} {vo_len:>6} {dom:>3} {flt:>3} "
              f"{best:>4} {wrst:>4} {sent_s:14} {status}")
        if row_fails:
            for f in row_fails:
                print(f"      - {f}")
                fails.append(f"{r['slug']}: {f}")
        else:
            ok += 1
    print(f"\nResult: {ok}/{len(rows)} conformant; {len(fails)} failures")
    if len(rows) != 13:
        print(f"[FAIL] expected 13 meta-*-golden rows, found {len(rows)}")
        return 1
    if fails:
        return 1
    print("[OK] all 13 meta-* golden rows conformant.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
