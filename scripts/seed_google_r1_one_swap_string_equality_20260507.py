"""Seed Google R1 custom problem: 字符串至多一次交换判等.

User-described problem (Discord 2026-05-07 msg 1501812416131108915):
"R1: 给两个字符串, 询问能否通过最多一次交换 str1 的两个字母使他变为 str2;
直接枚举每个字母, 将不同的字母 index 加入到 diff 中, 如果 len(diff)=0
返回 true, 如果 len(diff)=2 并且恰好两个字母对应相等可以返回 True,
其他情况 False."

This is the **at-most-one-swap** variant of LC 859 'Buddy Strings'. Subtle
distinction: LC 859 is "exactly one swap" so str1 == str2 case requires
str1 to have a duplicate letter; the user's variant says "at most one"
so str1 == str2 is unconditionally True.

Custom problem -- no leetcode_id (canonical key is title per CLAUDE.md
'Idempotent seed pattern per row type'). Title: "字符串至多一次交换判等"
(matches sibling Chinese-flavored custom titles like "Necklace 均分",
"门禁通行模拟", etc).

Solution preserved + house-style additions:

  - Linear scan collecting diff indices; check len == 0 (zero-swap) or
    len == 2 with crossed match `str1[i] == str2[j] AND str1[j] == str2[i]`.
  - Bonus O(1)-space short-circuit version (early-return after seeing
    third diff).
  - Edge case + LC 859 differential note + 5-item 易错 checklist.

Per `feedback_pinterest_two_tier_notes`: per-problem note in
`problems.notes`, ProblemDrawer renders via `db://<id>`. Doc 92 R2 Coding
Index extended to add this entry under existing `### String / Two Pointers`
section (joins LC 777 + LC 2337 -- all three are linear-scan string
comparisons). Doc 92 header is "R2 Coding only" but its exclusion list
specifically excludes "R1 ML fundamentals", NOT "R1 coding" -- this R1
coding problem is in scope.

Idempotent. Title is the canonical key. First run on missing row:
1 INSERT. Re-run on identical state: 0 writes.

Run: python scripts/seed_google_r1_one_swap_string_equality_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "字符串至多一次交换判等"
SOURCE_LABEL = "Google R1 2026-05"
COMPANY_TAGS = ["Google"]

NOTES = """\
## 字符串至多一次交换判等

### 题意

给两个长度相等的字符串 `str1`, `str2`, 问能否通过**至多一次**交换 `str1` 中两个位置 (任意两位, 不必相邻) 的字母, 让 `str1` 等于 `str2`。

### 思路 -- 一遍扫收集 diff

- 一次遍历, 把所有 `str1[i] != str2[i]` 的下标 `i` 收到 `diff` 列表里。
- `len(diff) == 0` -> 已经相等, 不交换也行 (题目说**至多**一次), 返回 True。
- `len(diff) == 2` -> 设两个不同位置为 `(i, j)`, 一次合法交换能修复 ⇔ `str1[i] == str2[j]` AND `str1[j] == str2[i]` (交换 str1 的 i, j 两位后正好填上对方位置)。
- 其他情况 (`len == 1` 或 `>= 3`) -> 一次交换最多消两个 diff, 不够或没法消, 返回 False。

### 代码 -- 用户原版

```python
class Solution:
    def canTransformByOneSwap(self, str1: str, str2: str) -> bool:
        if len(str1) != len(str2):
            return False
        diff = [i for i in range(len(str1)) if str1[i] != str2[i]]
        if len(diff) == 0:
            return True
        if len(diff) == 2:
            i, j = diff
            return str1[i] == str2[j] and str1[j] == str2[i]
        return False
```

### O(1) 空间 -- 短路优化版

如果 diff 数发现已经 >= 3 立即返回, 不需要存整个列表:

```python
class Solution:
    def canTransformByOneSwap(self, str1: str, str2: str) -> bool:
        if len(str1) != len(str2):
            return False
        i = j = -1
        for k, (a, b) in enumerate(zip(str1, str2)):
            if a == b:
                continue
            if i == -1:
                i = k
            elif j == -1:
                j = k
            else:
                return False                 # 第 3 个 diff, 直接 False
        if i == -1:
            return True                      # 0 个 diff
        if j == -1:
            return False                     # 1 个 diff (奇数 diff 一次交换无法消)
        return str1[i] == str2[j] and str1[j] == str2[i]
```

### 复杂度

- 时间 $O(n)$ -- 一遍扫
- 空间 $O(n)$ (原版存 diff list) 或 $O(1)$ (短路版只记两个 idx)

### 关键点

- **"至多一次" vs "恰好一次"**: LC 859 "Buddy Strings" 是恰好一次, 那种情况下 `str1 == str2` 还要求 str1 有重复字母才能 swap 同字母而不变。本题"至多一次"允许零次, str1 == str2 直接 True。**面试时务必先问清楚是 at-most 还是 exactly。**
- **diff 必须是偶数**: 一次交换让恰好两个位置发生变化, 所以合法 diff 数只有 0 或 2; 1 / 3 / 5 / ... 都不可能 (奇数 diff 一次交换永远消不完)。
- **交叉匹配**: `len == 2` 时检查 `str1[i] == str2[j] AND str1[j] == str2[i]`, 不是 `str1[i] == str1[j]` (那是问 str1 两位置同字母, 跟可达性无关)。

### 易错点

- 长度不等直接 False (题目可能保证, 守好边界更稳)。
- 漏了 `len(diff) == 0` 早退 -> 后续访问 `diff[0], diff[1]` 越界。
- 把交叉匹配写成 `str1[i] == str2[i]` (那永远 False, 因为 i 是 diff 位置) -- 必须用 j 的字符。
- 误把 diff 长度限制写成 `<=2` -> 漏判 `len == 1` 这种奇数情况。
- 多字符集 (如 utf-8 多字节) 时 `zip(str1, str2)` 仍然按 codepoint 配对, Python 没问题; 移植到 C/C++ 注意按 char 还是 byte 比较。

### 一句话总结

`O(n)` 一遍扫收集 diff 下标: `len == 0` -> True (至多一次允许零次); `len == 2` 且交叉匹配 (`s1[i]==s2[j] and s1[j]==s2[i]`) -> True; 其他 -> False。区分 LC 859 "恰好一次" 的语义微差。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": None,
    "title": TITLE,
    "url": None,
    "difficulty": "easy",
    "tags": ["string", "linear-scan", "diff-compare", "easy"],
    "pattern": "diff-scan",
    "family": "string",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "notes": NOTES,
}


def _select_existing_by_title(
    conn: sqlite3.Connection, title: str
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching title, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, notes "
        "FROM problems WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "title", "url", "difficulty", "tags", "pattern",
        "family", "category", "source", "company_tags", "is_completed", "notes",
    ]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _normalize(spec: dict) -> dict:
    """Normalize spec into the comparable storage form (lists -> JSON strings)."""
    out = dict(spec)
    out["tags"] = json.dumps(spec["tags"], ensure_ascii=False)
    out["company_tags"] = json.dumps(spec["company_tags"], ensure_ascii=False)
    return out


def _merge_company_tags(current_json: str | None, target_list: list[str]) -> str:
    """Union target into existing JSON-encoded company_tags list, preserving order."""
    cur = json.loads(current_json) if current_json else []
    for tag in target_list:
        if tag not in cur:
            cur.append(tag)
    return json.dumps(cur, ensure_ascii=False)


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by title (custom problem). Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing_by_title(conn, spec["title"])

    if existing is None:
        cur = conn.execute(
            "INSERT INTO problems "
            "(leetcode_id, title, url, difficulty, tags, pattern, family, "
            " category, source, company_tags, is_completed, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "        CURRENT_TIMESTAMP)",
            (
                norm["leetcode_id"], spec["title"], norm["url"],
                norm["difficulty"], norm["tags"], norm["pattern"],
                norm["family"], norm["category"], norm["source"],
                norm["company_tags"], norm["is_completed"], norm["notes"],
            ),
        )
        return int(cur.lastrowid), "INSERTED"

    pid, current = existing
    merged_company_tags = _merge_company_tags(
        current.get("company_tags"), spec["company_tags"]
    )
    fields_to_check = [
        "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "is_completed", "notes",
    ]
    drift = {
        f: norm[f] for f in fields_to_check if current.get(f) != norm[f]
    }
    if current.get("company_tags") != merged_company_tags:
        drift["company_tags"] = merged_company_tags

    if not drift:
        return pid, "UNCHANGED"

    set_clauses = ", ".join(f"{f} = ?" for f in drift)
    values = list(drift.values())
    values.append(pid)
    conn.execute(
        f"UPDATE problems SET {set_clauses} WHERE id = ?",
        values,
    )
    return pid, "UPDATED"


def main() -> int:
    """Insert-or-update the custom problem. Return 0 on success."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")          # Title contains CJK
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(
        f".db.bak.{ts}_pre_one_swap_string_equality"
    )
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(f"[{action}] problem id={pid} title={TITLE!r}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
