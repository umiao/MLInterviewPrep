"""Seed Google R2 Coding problem: 循环密码锁 Combination 计数.

User-provided content (Discord 2026-05-05). 3-dial circular combination lock,
each dial has N digits (0..N-1). Two passwords `user` and `bypass`. A
combination $(c_1, c_2, c_3)$ is valid iff *every* position is within
circular distance 2 of `user`'s position OR *every* position is within
circular distance 2 of `bypass`'s position. Count valid combinations.

Solution: inclusion-exclusion. $|A \\cup B| = |A| + |B| - |A \\cap B|$ where
each per-position window is an explicit set; the small wrap-around cases
($5 \\le N \\le 9$) where two windows can intersect on both sides of the
ring make the closed-form `5 - d` wrong, so the implementation uses
`set & set` uniformly to avoid edge-case logic.

Per `feedback_pinterest_two_tier_notes`, the per-problem note lives in
`problems.notes` (rendered by ProblemDrawer when opening `db://<id>`).
The R2 Coding Index doc (id=92) is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py` (extended in the same
commit to add a Math / Combinatorics / 容斥 section that references this
problem by title).

Idempotent. Title is canonical key. First clean run: 1 INSERT. Re-run on
identical content: 0 writes. Per Invariant 3 (CLAUDE.md), this seed is
the sole sanctioned write path for this row.

Run: python scripts/seed_google_r2_combination_lock_count_20260505.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS = ["Google"]

TITLE = "循环密码锁 Combination 计数"

DESCRIPTION = """\
3 位转盘锁，每位是一个有 $N$ 个数字（0 ~ $N-1$）的循环转盘。给定两个 3 位密码 `user` 和 `bypass`。一个 combination $(c_1, c_2, c_3)$ 合法当且仅当：

$$\\big(\\forall i:\\ |c_i - u_i|_N \\le 2\\big)\\ \\lor\\ \\big(\\forall i:\\ |c_i - b_i|_N \\le 2\\big)$$

其中 $|x - y|_N = \\min(|x-y|, N - |x-y|)$ 是循环距离。问合法 combination 的数量。

来源: Google R2 Coding 2026-05 题面（用户 Discord 2026-05-05 提供）。
"""

NOTES = """\
## 循环密码锁 Combination 计数

### 关键观察：整体 OR，不是逐位 OR

「三位同时通过 user 或 三位同时通过 bypass」，**不能拆成每一位独立的 OR**。否则会把诸如「第 1 位接近 user，第 2 位接近 bypass」这种两个密码都不通过的组合算进去。

### 容斥

记 $A$ = 通过 user 的 combination 集合，$B$ = 通过 bypass 的集合。则

$$|A \\cup B| = |A| + |B| - |A \\cap B|$$

每位独立，所以

$$|A| = \\prod_i |W(u_i)|,\\quad |B| = \\prod_i |W(b_i)|,\\quad |A \\cap B| = \\prod_i |W(u_i) \\cap W(b_i)|$$

其中 $W(x) = \\{(x + k) \\bmod N : k \\in \\{-2,-1,0,1,2\\}\\}$ 是该位的合法窗口。

- $N \\ge 5$：$|W(x)| = 5$，$|A| = |B| = 125$
- $N \\le 4$：窗口覆盖整圆，$|W(x)| = N$，$A = B$，答案就是 $N^3$

### 单位 overlap

设循环距离 $d_i = |u_i - b_i|_N$：

- $d_i \\ge 5$：两窗口不相交，$\\text{overlap}_i = 0$，从而 $|A \\cap B| = 0$
- $d_i \\le 4$ 且 $N \\ge 10$：闭式 $\\text{overlap}_i = 5 - d_i$
- $5 \\le N \\le 9$：两侧可能同时 wrap-around 而双重相交。例如 $N=8$，$u_i=0$、$b_i=4$ 时，$W(u_i) = \\{6,7,0,1,2\\}$，$W(b_i) = \\{2,3,4,5,6\\}$，交集是 $\\{2, 6\\}$，size = 2，闭式给的 $5 - 4 = 1$ 是错的

实现上**直接用集合交集**，统一处理所有 $N$，省掉 edge case 的脑力开销。

### 代码

```python
def count_combinations(N, user, bypass):
    def window(x):
        return {(x + k) % N for k in range(-2, 3)}

    A = B = I = 1
    for u, b in zip(user, bypass):
        Wu, Wb = window(u), window(b)
        A *= len(Wu)
        B *= len(Wb)
        I *= len(Wu & Wb)

    return A + B - I
```

### 复杂度

- 时间 $O(1)$：每位常数大小（最多 5 个元素）的集合，只有 3 位
- 空间 $O(1)$：同理

### 测试

| $N$ | user | bypass | 答案 | 注释 |
|---|---|---|---|---|
| 10 | (0,0,0) | (5,5,5) | 250 | 每位距离 5，完全不交 |
| 10 | (0,0,0) | (0,0,0) | 125 | 完全相同 |
| 10 | (0,0,0) | (1,1,1) | 250 − 4³ = 186 | 每位重叠 4 |
| 8 | (0,0,0) | (4,4,4) | 250 − 2³ = 242 | 双侧 wrap，闭式会算错 |
| 4 | 任意 | 任意 | 64 | 窗口全覆盖，$N^3$ |

### 一句话总结

容斥 + 每位独立算交集大小：$\\text{ans} = |A| + |B| - \\prod_i |W(u_i) \\cap W(b_i)|$。
"""


PROBLEM_SPEC: dict = {
    "title": TITLE,
    "leetcode_id": None,
    "url": None,
    "difficulty": "medium",
    "tags": ["math", "combinatorics", "inclusion-exclusion"],
    "pattern": "inclusion-exclusion",
    "family": "math",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "description": DESCRIPTION,
    "notes": NOTES,
}


def _select_existing(
    conn: sqlite3.Connection, title: str
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching title, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, "
        "       description, notes "
        "FROM problems WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
    ]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _normalize(spec: dict) -> dict:
    """Normalize spec into the comparable storage form (lists -> JSON strings)."""
    out = dict(spec)
    out["tags"] = json.dumps(spec["tags"], ensure_ascii=False)
    out["company_tags"] = json.dumps(spec["company_tags"], ensure_ascii=False)
    return out


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by title. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing(conn, spec["title"])

    if existing is None:
        cur = conn.execute(
            "INSERT INTO problems "
            "(leetcode_id, title, url, difficulty, tags, pattern, family, "
            " category, source, company_tags, is_completed, "
            " description, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "        CURRENT_TIMESTAMP)",
            (
                norm["leetcode_id"], spec["title"], norm["url"],
                norm["difficulty"], norm["tags"], norm["pattern"],
                norm["family"], norm["category"], norm["source"],
                norm["company_tags"], norm["is_completed"],
                norm["description"], norm["notes"],
            ),
        )
        return int(cur.lastrowid), "INSERTED"

    pid, current = existing
    fields_to_check = [
        "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
    ]
    drift = {
        f: norm[f] for f in fields_to_check if current.get(f) != norm[f]
    }
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
    """Insert-or-update the combination-lock counting problem. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_combo_lock_count")
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
