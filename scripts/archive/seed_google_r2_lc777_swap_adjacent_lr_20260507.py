"""Seed Google R2 Coding problem: LC 777 Swap Adjacent in LR String.

User-provided solution (Discord 2026-05-07 msg 1501803587943010336). User
flagged the problem as `智力题` -- the trick is recognizing the directional
invariant: L can only move LEFT (via `LX -> XL`), R can only move RIGHT
(via `XR -> RX`); and since the only swap involves an X, L/R chars cannot
pass each other -- their relative order is invariant.

User's algorithm:

  1. Filter X out from both start and result, keeping (idx, char) pairs.
  2. Char sequences must be identical (same length, same chars at each
     position) -- enforces the L/R-relative-order invariant.
  3. For each i: if char is 'R', start idx must be <= target idx (R only
     moves right); if char is 'L', start idx must be >= target idx (L
     only moves left).

Same problem family as LC 2337 'Move Pieces to Obtain a String' (already
indexed under `### String / Two Pointers` of doc 92): identical move
semantics with '_' substituting for 'X'.

LC 777 row does not exist in problems (not in bulk LC import). This seed
INSERTs (or, on re-run, UPDATEs) the row by canonical key leetcode_id=777.
Sets family='two-pointers' pattern='two-pointers' to match LC 2337's metadata
in the same section, company_tags=['Google'], notes ~3.5KB preserving the
user's compact solution + invariant proof + 易错 checklist.

Per `feedback_pinterest_two_tier_notes`: per-problem note in `problems.notes`,
ProblemDrawer renders via `db://<id>`. The R2 Coding Index doc 92 is updated
separately by re-running `scripts/seed_google_r2_coding_index_20260502.py`,
extended in this commit to add an LC 777 entry above LC 2337 in the existing
`### String / Two Pointers` section (LC number order).

Idempotent. leetcode_id=777 is the canonical key. First run on missing row:
1 INSERT. Re-run on identical state: 0 writes. Per Invariant 3 (CLAUDE.md),
this seed is the sole sanctioned write path for this row.

Run: python scripts/seed_google_r2_lc777_swap_adjacent_lr_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 777
TITLE = "Swap Adjacent in LR String"
URL = "https://leetcode.com/problems/swap-adjacent-in-lr-string/"
SOURCE_LABEL = "Google R2 2026-05"

COMPANY_TAGS = ["Google"]

NOTES = """\
## LC 777. Swap Adjacent in LR String

### 题意速览

字符串只含 `L`/`R`/`X` 三种字符。允许两种相邻交换:

- `LX -> XL`: 一个 L 和它**左侧**的 X 交换 (L 左移一格);
- `XR -> RX`: 一个 R 和它**右侧**的 X 交换 (R 右移一格)。

判断能否从 `start` 经过若干次此类操作变成 `result`。

### 核心洞察 -- 这是道智力题

两条**结构性不变量**, 看穿了就直接写, 看不穿会陷入 BFS/搜索:

1. **L/R 的相对顺序不变**。所有合法 swap 都涉及 X, 永远不会让一个 L 越过另一个 L/R, 也不会让一个 R 越过另一个 L/R。所以**把 X 滤掉之后, L/R 序列必须完全相同 (长度 + 每位字符)**。
2. **L 只能左移, R 只能右移**。`LX -> XL` 让 L 索引 -1, `XR -> RX` 让 R 索引 +1。所以**对应 L 的起始索引 ≥ 目标索引**, **对应 R 的起始索引 ≤ 目标索引**。

两条不变量同时满足 ⇔ 可达 (必要性显然; 充分性可通过构造把每个 L 从左到右逐个推到位 / 每个 R 从右到左逐个推到位证明)。

### 代码 -- 用户原版

```python
class Solution:
    def canTransform(self, start: str, result: str) -> bool:
        # it can also be taken as: allow L to cross X from right,
        # R to cross X from left.

        n = len(start)
        fromSeq = []
        for i, c in enumerate(start):
            if c != 'X':
                fromSeq.append((i, c))
        toSeq = []
        for i, c in enumerate(result):
            if c != 'X':
                toSeq.append((i, c))

        if len(fromSeq) != len(toSeq):
            return False

        for i in range(len(fromSeq)):
            if fromSeq[i][1] != toSeq[i][1]:
                return False
            if fromSeq[i][1] == 'R' and fromSeq[i][0] > toSeq[i][0]:
                return False
            if fromSeq[i][1] == 'L' and fromSeq[i][0] < toSeq[i][0]:
                return False
        return True
```

### O(1) 额外空间的双指针写法

不需要建两个 list, 用双指针同时扫两串, 各自跳过 X, 配对比较即可:

```python
class Solution:
    def canTransform(self, start: str, result: str) -> bool:
        if len(start) != len(result):
            return False
        n = len(start)
        i = j = 0
        while i < n or j < n:
            while i < n and start[i] == 'X':  i += 1
            while j < n and result[j] == 'X': j += 1
            if i == n and j == n:
                return True
            if i == n or j == n:
                return False                         # 一个走完另一个还有非 X
            if start[i] != result[j]:
                return False                         # 相对顺序对不上
            if start[i] == 'L' and i < j:
                return False                         # L 不能右移
            if start[i] == 'R' and i > j:
                return False                         # R 不能左移
            i += 1
            j += 1
        return True
```

两种写法等价, 双指针版省掉两次 list 构造, 适合压缩空间。

### 复杂度

- 时间 $O(n)$ -- 一遍扫 (双指针写法每个位置最多被各端推进一次)
- 空间 $O(n)$ (滤 X 写法) 或 $O(1)$ (双指针写法)

### 充分性 -- 为什么两条不变量就够了

构造性证明: 假设两不变量都满足, 按目标位置**从左到右**贪心推:

- 若当前目标是 R: 在 start 中找下一个 R (它的 idx ≤ 目标 idx, 由不变量), 一路 `XR -> RX` 把它推到目标位。途中遇到的只有 X (相对顺序不变, 所以在它前面再没有别的 L/R)。
- 若当前目标是 L: 同理但反向, 从**右往左**推 L。

任何时候这两类推动都不会冲突 (L 推时只越 X, R 推时也只越 X, 推完一个 R 后该 R 不再动)。所以两不变量 ⇒ 可达。

### 易错点

- 别忘了**长度检查**: 双指针写法没有 `len(start) != len(result)` 的早退就会在指针越界时崩 (虽然题目通常保证长度相同, 守好边界更稳)。
- **相对顺序检查不等于字符多重集相等**: `LR` 和 `RL` 在多重集意义上相同但相对顺序不同, 必须按位置配对而非计数对比。
- **方向方向方向**: 容易把 L/R 的允许方向写反。口诀: **L 想着 Left (只能往左), R 想着 Right (只能往右)**, 所以 `start_idx ≥ target_idx` 是 L, `start_idx ≤ target_idx` 是 R。
- 注意 `LX -> XL` 让**L 左移**而不是 X 左移。从 X 视角看 X 在右移, 但解题逻辑以 L/R 为主体描述更自然。
- 若一边的非 X 走完了另一边还有非 X, 必须 False (双指针写法的 `i == n or j == n` 早退分支别漏)。

### 一句话总结

L/R 字符串的合法变换两条不变量: **(1) 滤 X 后字符序列必须完全相同 -- L/R 相对顺序锁死; (2) L 起始 idx ≥ 目标 idx, R 起始 idx ≤ 目标 idx -- 方向单向**。两条同时满足 ⇔ 可达, $O(n)$ 一遍扫搞定。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": LEETCODE_ID,
    "title": TITLE,
    "url": URL,
    "difficulty": "medium",
    "tags": ["string", "two-pointers", "simulation", "invariant"],
    "pattern": "two-pointers",
    "family": "two-pointers",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "notes": NOTES,
}


def _select_existing_by_lc(
    conn: sqlite3.Connection, leetcode_id: int
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching leetcode_id, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, notes "
        "FROM problems WHERE leetcode_id = ?",
        (leetcode_id,),
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
    """INSERT-or-UPDATE the problem row by leetcode_id. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing_by_lc(conn, spec["leetcode_id"])

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
        "title", "url", "difficulty", "tags", "pattern", "family",
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
    """Insert-or-update LC 777. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc777_swap_adjacent_lr")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(f"[{action}] problem id={pid} leetcode_id={LEETCODE_ID} title={TITLE!r}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
