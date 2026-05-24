"""Append LC 426 + LC 1293 to the Pinterest card_index doc (id=66, 2026-05-06).

Companion to `seed_pinterest_lc_426_1293_20260506.py`, which added the two
problems to the LC index doc (id=47) but NOT to the card_index that powers
the default view at `/companies/29/prep` (no `?tab=...`).

Targets:
  - LC 1293 (problems.id=451) -> card #4 "图论/欧拉/BFS / Graph / Eulerian / BFS"
    (perfect fit: BFS with state = (x, y, k_remaining))
  - LC 426 (problems.id=332) -> card #5 "回溯/DFS / Backtracking / DFS"
    (tree DFS in-order; card already includes LC 1110 tree DFS, so the
    semantics already cover this; lightly broaden summary_zh to make
    "tree DFS" first-class without renaming)

Idempotent: re-running checks `problems.id` membership in each card before
appending. Card summaries are only updated if not already updated.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows (cp1252 default chokes on CJK in summaries)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
CARD_INDEX_DOC_ID = 66

LC1293_PROBLEM_ID = 451
LC1293_ONE_LINER = "BFS 状态 = (x, y, k_remaining) 求最短步数"
TARGET_CARD_BFS_NAME_EN = "Graph / Eulerian / BFS"

LC426_PROBLEM_ID = 332
LC426_ONE_LINER = "BST 中序 + prev 滚动重接 circular DLL"
TARGET_CARD_DFS_NAME_EN = "Backtracking / DFS"

# Lightly broaden the DFS card summary to acknowledge tree DFS / linked-list relink
# as first-class members alongside backtracking.
DFS_CARD_OLD_SUMMARY = "核心：运算符枚举、树剪枝、工人-工时状压/回溯"
DFS_CARD_NEW_SUMMARY = "核心：运算符枚举、树 DFS 状态上下传、in-order 重接、工人-工时状压/回溯"


def append_problem_to_card(
    payload: dict, *, card_name_en: str, problem_id: int,
    leetcode_id: int | None, title: str, one_liner: str,
) -> bool:
    """Idempotently append (problem_id) to the named card. Returns True if changed."""
    for card in payload["cards"]:
        if card.get("name_en") != card_name_en:
            continue
        if any(p.get("id") == problem_id for p in card["problems"]):
            print(f"  [SKIP] card '{card_name_en}' already contains problems.id={problem_id}")
            return False
        card["problems"].append({
            "id": problem_id,
            "leetcode_id": leetcode_id,
            "title": title,
            "one_liner": one_liner,
        })
        print(f"  [APPEND] problems.id={problem_id} (LC {leetcode_id}) -> card '{card_name_en}'")
        return True
    raise SystemExit(f"[FAIL] card name_en='{card_name_en}' not found")


def update_dfs_summary(payload: dict) -> bool:
    """Broaden the DFS card summary; returns True if changed."""
    for card in payload["cards"]:
        if card.get("name_en") == TARGET_CARD_DFS_NAME_EN:
            cur = card.get("summary_zh", "")
            if cur == DFS_CARD_NEW_SUMMARY:
                print("  [SKIP] DFS card summary already broadened")
                return False
            if cur != DFS_CARD_OLD_SUMMARY:
                print(
                    f"  [WARN] DFS card summary unexpected ({cur!r}); not overwriting"
                )
                return False
            card["summary_zh"] = DFS_CARD_NEW_SUMMARY
            print("  [UPDATE] DFS card summary broadened (tree DFS / in-order)")
            return True
    raise SystemExit("[FAIL] DFS card not found")


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?",
            (CARD_INDEX_DOC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"[FAIL] company_documents.id={CARD_INDEX_DOC_ID} missing")
        payload = json.loads(row[0])

        # Pull canonical (leetcode_id, title) for the two problems
        meta = {}
        for pid in (LC1293_PROBLEM_ID, LC426_PROBLEM_ID):
            r = conn.execute(
                "SELECT leetcode_id, title FROM problems WHERE id = ?", (pid,)
            ).fetchone()
            if r is None:
                raise SystemExit(f"[FAIL] problems.id={pid} not found")
            meta[pid] = r

        changed = False
        print("=== card append ===")
        changed |= append_problem_to_card(
            payload, card_name_en=TARGET_CARD_BFS_NAME_EN,
            problem_id=LC1293_PROBLEM_ID,
            leetcode_id=meta[LC1293_PROBLEM_ID][0],
            title=meta[LC1293_PROBLEM_ID][1],
            one_liner=LC1293_ONE_LINER,
        )
        changed |= append_problem_to_card(
            payload, card_name_en=TARGET_CARD_DFS_NAME_EN,
            problem_id=LC426_PROBLEM_ID,
            leetcode_id=meta[LC426_PROBLEM_ID][0],
            title=meta[LC426_PROBLEM_ID][1],
            one_liner=LC426_ONE_LINER,
        )
        print("\n=== summary tweak ===")
        changed |= update_dfs_summary(payload)

        if not changed:
            print("\n[NOOP] all targets already in place")
            return

        new_content = json.dumps(payload, ensure_ascii=False, indent=2)
        conn.execute(
            "UPDATE company_documents SET content = ?, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            (new_content, CARD_INDEX_DOC_ID),
        )
        conn.commit()

        print("\n=== verify ===")
        for card in payload["cards"]:
            if card.get("name_en") in (TARGET_CARD_BFS_NAME_EN, TARGET_CARD_DFS_NAME_EN):
                print(
                    f"  '{card['name_en']}' now has {len(card['problems'])} problems "
                    f"(summary: {card['summary_zh'][:60]}...)"
                )
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    main()
