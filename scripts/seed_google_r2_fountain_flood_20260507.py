"""Seed Google R2 custom problem: Fountain Flood.

User-provided 题解 (Discord 2026-05-07 msg 1501814166435139644, attachment
~4KB). Custom Google R2 problem (no LC equivalent in our DB) where each
fountain in an ascending-index list floods strict-less-than cells
outward until blocked by a >= height; final result is a 64-bit chunked
bitmask of flooded indices.

Algorithm preserved verbatim:

  1. Monotonic decreasing stack (LC 84 'Largest Rectangle in Histogram'
     family) for L[i] / R[i] = nearest indices on each side with
     `heights[j] >= heights[i]`. Pop condition is STRICT `<` --
     `heights[stack[-1]] < heights[i]` -- so equal-height neighbors do
     NOT bound each other (else two equal-height fountains would
     over-cover).
  2. Each fountain f corresponds to closed range `[L[f]+1, R[f]-1]`.
  3. Since `fountains` is given ascending and sentinel-bounded ranges
     thus mostly ascending, run an interval-merge pass to dedupe
     overlap.
  4. Bitmask paint per 64-bit chunk: in-chunk partial uses
     `((1 << len) - 1) << offset`; whole chunk uses `~0ULL`. Total
     paint cost O(n/64).

Time: O(n + k); space: O(n) for L/R + chunked output.

Custom problem -- no leetcode_id, canonical key=title='Fountain Flood'.
family=stack, pattern=monotonic-stack, source='Google R2 2026-05',
company_tags=[Google], notes ~3.7KB preserving user's full exposition
+ house-style 易错 + 一句话总结.

Per `feedback_pinterest_two_tier_notes`: per-problem note in
`problems.notes`, ProblemDrawer renders via `db://<id>`. Doc 92 R2 Coding
Index extended to add a NEW `### Stack / 单调栈` section between
`### Sliding Window` and `### Sweep Line / 离散化 / 线段树` -- a
forward-compatible position for future LC 84/85/496/503 entries.

Idempotent. Title is the canonical key. First run on missing row:
1 INSERT. Re-run on identical state: 0 writes.

Run: python scripts/seed_google_r2_fountain_flood_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Fountain Flood"
SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS = ["Google"]

NOTES = """\
## Fountain Flood

### 题面

给定:

- `heights: int[n]` -- 一排格子的高度
- `fountains: int[k]` -- 一个**升序**的下标列表, 每个下标处放着一个喷泉

规则: 每个喷泉会向左右两侧蔓延, **淹没所有高度严格小于** `heights[fountain]` 的格子; 遇到高度 `>= heights[fountain]` 的格子就被挡住, 无法越过。

返回: 长度为 `n` 的 0/1 bitmask, 第 `i` 位表示下标 `i` 是否被淹。要求用 64-bit chunk 的位压缩形式输出。

---

### 分析

对每个喷泉 `f`, 被它淹没的范围是开区间 `(L[f], R[f])`, 其中:

- `L[f]` = 左侧最近的 `heights[j] >= heights[f]` 的下标 (不存在则为 `-1`)
- `R[f]` = 右侧最近的 `heights[j] >= heights[f]` 的下标 (不存在则为 `n`)

这是 LC 84 (Largest Rectangle in Histogram) 那一族的经典子问题: **两侧最近 ≥ 当前值的位置**。一遍单调递减栈可以在 $O(n)$ 内同时算出所有下标的 `L`、`R`。

**关键细节**: 题面是"严格小于才淹", 所以单调栈的弹出条件是 `heights[top] < heights[i]` (**严格**), 等高时不弹。这样 `R[t]` 才正好停在第一个 `>=` 的位置, 等高的两个喷泉之间不会互相穿透。

**优化**: 直接对每个喷泉调用 bitmask 染色是 $O(nk/64)$, 最坏情况退化 (所有 range 几乎覆盖全数组)。注意到 `fountains` 已经升序, 对应的 ranges 也大致升序, 可以先做一遍 **interval merge**, 再对合并后的不重叠区间染色, 染色总量降到 $O(n/64)$。

**喷泉自己算不算淹**: 按字面规则 `heights[f]` 不严格小于自己, 但通常约定喷泉本身是湿的。下面实现把喷泉自己的下标也包含在 range 里 -- 若题面要求相反, 把 `f` 单独排除即可。

---

### 算法

1. **单调栈**求出所有下标的 `L[i]`、`R[i]`, $O(n)$
2. 对每个 fountain `f`, 得到闭区间 `[L[f]+1, R[f]-1]`, $O(k)$
3. **合并**这些区间 (已按起点有序), $O(k)$
4. **位压缩染色**: 对每个合并区间 `[s, e]`, 按 64-bit chunk 切分; chunk 内不对齐的部分用 `((1 << len) - 1) << offset`, 整个 chunk 直接置 `~0ULL`, $O(n/64)$

---

### 参考实现 (Python)

```python
def fountain_flood(heights: list[int], fountains: list[int]) -> list[int]:
    n = len(heights)

    # 1) 单调栈: L[i], R[i] = 两侧最近 >= heights[i] 的下标
    L = [-1] * n
    R = [n] * n
    stack = []
    for i in range(n):
        while stack and heights[stack[-1]] < heights[i]:  # 严格 <
            R[stack.pop()] = i
        L[i] = stack[-1] if stack else -1
        stack.append(i)

    # 2) 收集每个 fountain 的闭区间
    ranges = [(L[f] + 1, R[f] - 1) for f in fountains]

    # 3) 合并区间 (fountains 升序 => ranges 起点升序)
    merged = []
    for s, e in ranges:
        if merged and s <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    # 4) 64-bit chunk 位压缩染色
    W = 64
    chunks = [0] * ((n + W - 1) // W)
    FULL = (1 << W) - 1
    for s, e in merged:
        i = s
        while i <= e:
            ci, off = divmod(i, W)
            end = min((ci + 1) * W - 1, e)
            length = end - i + 1
            chunks[ci] |= ((1 << length) - 1) << off
            i = end + 1
    return chunks
```

---

### 复杂度

- 时间 $O(n + k)$ (位压缩部分 $O(n/64)$, 可视为常数级别快)
- 空间 $O(n)$, 主要是 `L`、`R` 与输出 bitmask

### 易错点

- **弹栈是严格 `<`, 等高不弹**: 否则等高喷泉会互相覆盖, 同高度的两个喷泉本应被对方挡住, 但若 `<=` 弹栈, R/L 会越过对面喷泉, 范围算大。
- **Sentinel `L=-1`, `R=n`**: 处理两端无更高元素的情况, 算开区间 `(L, R)` 时直接展开为 `[0..R-1]` / `[L+1..n-1]`, 不需要特判。
- **喷泉本身是否计入淹没**: 字面规则不计 (因为 `heights[f]` 不严格小于自己), 实现里把 `f` 包含进 `[L+1, R-1]` 是工程默认, 面试时**先问清楚**。
- **`fountains` 不保证升序的情况**: merge 前先按起点排序, 否则 merge 漏配。
- **bitmask chunk 边界**: in-chunk partial 染色用 `((1 << len) - 1) << off`; 不要把 `len == 64` 的整 chunk 写成 `((1 << 64) - 1) << 0`, 在 Python 里没事但在 C/C++ 是 UB (`<< 64` 未定义)。整 chunk 直接置 `~0ULL` 或在 Python 里 `FULL = (1 << 64) - 1`。
- **染色总量上界**: 合并后区间不重不交, 总长度 ≤ n, 所以染色 $O(n/64)$, 不会被退化的 fountain 数量拖垮。

### 一句话总结

Fountain Flood = LC 84 单调栈 + 区间合并 + 64-bit chunk 位压缩染色, **弹栈严格 `<` 是关键** (等高不互穿); 整体 $O(n + k)$ + $O(n/64)$ 染色。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": None,
    "title": TITLE,
    "url": None,
    "difficulty": "medium",
    "tags": ["stack", "monotonic-stack", "interval-merge", "bitmask"],
    "pattern": "monotonic-stack",
    "family": "stack",
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
    """Insert-or-update Fountain Flood. Return 0 on success."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")          # belt-and-suspenders
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_fountain_flood")
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
