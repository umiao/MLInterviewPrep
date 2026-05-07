"""Seed Google R2 Coding problem: Necklace 均分 (D/R 两人公平切分).

User-provided content (Discord 2026-05-07 msg 1501779766720594093,
message.txt attachment). Custom problem: split a string s of 'D' and 'R'
(with #D = #R) into <= 2 contiguous segments so two parties (甲, 乙) each
end up with equal counts of D and R.

Core insight: it's the k=2 special case of the Hobby-Rice / Necklace
Splitting theorem -- a <=2-cut solution ALWAYS exists. The middle segment
of a 2-cut split must have length n/2 and contain #D/2 D's and #R/2 R's,
so the problem reduces to:

    find a length-(n/2) substring with prefix sum f(j) = f(j - n/2),
    where f(k) = (# of D in s[:k]) - (# of R in s[:k]).

Existence proof via discrete IVT + parity: g(k) = f(k) - f(k - m) starts
at f(m), ends at -f(m), step in {-2, 0, +2}, and is always even (since m
is even -> f(m) is even). A function that is always even and goes from
+f(m) to -f(m) in steps of magnitude <= 2 cannot skip 0.

Algorithm: O(n) prefix sum + O(n) sweep (or O(1) space with on-the-fly
window D-R count maintenance).

Per CLAUDE.md `Idempotent seed pattern per row type`: title is canonical
key for custom problems. Per Invariant 3, this seed is the sole sanctioned
write path.

The R2 Coding Index (doc 92) is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this commit
to add a new entry under the existing `### Prefix Sum / Hash` section
(joining Gold Chain 平分 and 等值端点最大子数组和).

Run: python scripts/seed_google_r2_necklace_split_dr_20260507.py
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

TITLE = "Necklace 均分 (D/R 两人公平切分)"

DESCRIPTION = """\
给定一个由 `'D'` 和 `'R'` 两种字符组成的字符串 `s`, 满足 `#D = #R`。要求将 `s` 切成若干**连续段**, 把这些段分配给甲、乙两人, 使得:

- 甲拿到的所有段里, D 的总数等于 R 的总数
- 乙拿到的所有段里, D 的总数等于 R 的总数

求出一组合法切法。

> **核心结论**: 必然存在一种**最多切 2 刀**的合法切法。问题的算法和证明都围绕这一结论展开。

来源: Google R2 Coding 2026-05 用户 Discord 2026-05-07 提供。
"""

NOTES = """\
## Necklace 均分问题: D / R 字符串两人公平切分

### 题目描述

给定一个由 `'D'` 和 `'R'` 两种字符组成的字符串 `s`, 满足 `#D = #R`。要求将 `s` 切成若干**连续段**, 把这些段分配给甲、乙两人, 使得每人手里 D 数 = R 数。求一组合法切法。

> **核心结论**: 必然存在一种**最多切 2 刀**的合法切法。

### 前置约束

为了让两人各得 `#D/2` 个 D 和 `#R/2` 个 R, `#D` 和 `#R` 都必须是偶数。

记 $n = |s|$, 则 $n$ 是 4 的倍数。令 $m := n/2$, 那么 $m$ 也是偶数。**这一奇偶性条件是后面证明的关键**, 请记住。

---

### 思路展开

#### 为什么是 "最多 2 刀", 而不是 "切成碎片"

这一限制不是题目额外强加的, 而是一个**定理**: 在 `#D = #R` (皆为偶数) 的前提下, **总存在**一种 $\\le 2$ 刀的均分方案。这是 **Necklace Splitting Theorem** 在两种颜色、两个分配方的特例。

如果反过来去切很多刀 (极端地一字一段), 均分本身仍然成立, 但分配过程退化为一个 subset-sum 类问题, 复杂度反而更高。固定 "2 刀" 这个结构, 反而把问题压成了 $O(n)$ 的滑动窗口。

#### 2 刀的结构 ↔ 长度 n/2 的子串

切 2 刀得到 3 段: 左段 + 中段 + 右段。把**中段**给甲、两端给乙 (或反过来)。

为使均分成立:

- 中段必须含 `#D/2` 个 D 和 `#R/2` 个 R
- 由于 D 和 R 加起来就是段长, 中段长度必为 $n/2 = m$

问题因此化归为:

> 在 `s` 中找一个长度为 $m$ 的子串, 使其恰好含 `#D/2` 个 D。

这是经典的固定窗口滑动窗口, $O(n)$ 一次扫描即可。

#### 等价的前缀和写法

定义前缀和

$$f(k) = D(k) - R(k) \\quad \\text{(前缀里 D 比 R 多多少)}$$

则子串 `[i, j)` 内 D 与 R 数目相等 $\\Longleftrightarrow f(j) = f(i)$。

本题中 $j - i = m$ 是固定的, 所以**不需要 hashmap** -- 直接对每个 $j \\in [m, n]$ 比较 $f(j)$ 与 $f(j - m)$ 即可。

---

### 算法实现

```python
def split_necklace(s: str) -> tuple[int, int]:
    \"\"\"返回两刀位置 (i, j), 使得 s[i:j] 给一人、s[:i] + s[j:] 给另一人。\"\"\"
    n = len(s)
    assert n % 4 == 0, "需要 #D = #R 且都是偶数"
    m = n // 2

    # 构造前缀和 f(k) = D(k) - R(k)
    prefix = [0] * (n + 1)
    for k, c in enumerate(s):
        prefix[k + 1] = prefix[k] + (1 if c == 'D' else -1)

    # 固定窗口扫: 找 j 使 prefix[j] == prefix[j - m]
    for j in range(m, n + 1):
        if prefix[j] == prefix[j - m]:
            return (j - m, j)
    raise RuntimeError("不可达: 定理保证一定存在")
```

时间 $O(n)$, 空间 $O(n)$ (可优化到 $O(1)$, 只需在线维护当前窗口的 $D - R$ 净差)。

---

### 正确性证明 (Necklace Splitting Theorem 的初等版本)

需要证明: 长度为 $m$ 的滑动窗口中**必然**存在某个位置 $j$, 使 $f(j) = f(j - m)$。

#### 辅助函数

定义

$$g(k) = f(k) - f(k - m), \\quad k \\in [m, n]$$

目标: 证明 $\\exists k$, $g(k) = 0$。

**边界值**:

$$g(m) = f(m) - f(0) = f(m)$$
$$g(n) = f(n) - f(m) = -f(m) \\quad \\text{(因为 } f(n) = 0\\text{)}$$

所以 $g(m)$ 与 $g(n)$ 互为相反数。

**步长**:

$$g(k+1) - g(k) = [f(k+1) - f(k)] - [f(k+1-m) - f(k-m)] = (\\pm 1) - (\\pm 1) \\in \\{-2, 0, +2\\}$$

$g$ 每一步要么不变, 要么跳 $\\pm 2$。

#### 奇偶性

$$f(m) = D(m) - R(m) = 2 \\cdot D(m) - m$$

因为 $m$ 是偶数, 所以 $f(m)$ 是偶数。结合 $g$ 每步只跳 0 或 $\\pm 2$, **$g$ 在整个 $[m, n]$ 上始终是偶数**。

> 这一步正是 `#D, #R` 必须都是偶数的几何意义所在: 让 $m$ 偶 $\\to$ $f(m)$ 偶 $\\to$ $g$ 偶, 使得 $0$ 恰好位于 $g$ 必经的格点上。

#### 离散介值定理 (discrete IVT)

- **若** $f(m) = 0$: 直接 $g(m) = 0$, 取 $k = m$ 即可 (中段就是后半串)。
- **若** $f(m) \\ne 0$: $g(m)$ 与 $g(n)$ 异号。不妨设 $f(m) > 0$ (负的对称)。

  令 $k_0$ 为 $[m, n]$ 中最大的使 $g(k_0) > 0$ 的下标。由极大性, $g(k_0 + 1) \\le 0$。

  又 $g(k_0 + 1) \\in \\{g(k_0) - 2, g(k_0), g(k_0) + 2\\}$, 前两个 (后两个 $g(k_0+1) \\ge g(k_0) > 0$) 与极大性矛盾, 于是

  $$g(k_0 + 1) = g(k_0) - 2 \\le 0$$

  而 $g(k_0)$ 是正偶数, 必有 $g(k_0) = 2$, 从而 $g(k_0 + 1) = 0$。取 $k = k_0 + 1$ 即证。$\\blacksquare$

#### 直觉

$g$ 从 $+f(m)$ 走到 $-f(m)$, 每步只能跳 $\\{-2, 0, +2\\}$, 并且**始终是偶数**。从正偶数走到负偶数而步长不超过 2 -- 不可能跳过 $0$。

---

### 复杂度

- 时间 $O(n)$
- 空间 $O(1)$ (在线维护窗口内的 $D - R$ 净差即可, 不必显式构造 prefix 数组)

---

### 拓展观察

这道题是 **Hobby-Rice / Necklace Splitting Theorem** 在「2 种颜色 + 2 个分配方」情形下的初等版本。一般形态是: $k$ 种颜色、2 个分配方, 最多 $k$ 刀就够。本题给出的 "**离散 IVT + 奇偶性**" 是 $k = 2$ 时一种相当干净的存在性证明。

如果题目变成**环形项链** (首尾相接), 切 2 刀得到 2 段, 分析框架仍然类似 -- 把环展开成线, 再用滑窗 / 前缀和处理; 唯一的差别是中段不再被强制为 $n/2$, 需要稍作调整。

---

### 易错点 / Checklist

- [ ] 别忘验证 $n \\% 4 == 0$ 这个前置条件 ($\\#D, \\#R$ 都偶 $\\Rightarrow n$ 是 4 倍数)
- [ ] 中段长度**必须**精确为 $n/2$, 不要写成 $\\le n/2$ 的可变窗口
- [ ] 用 prefix-sum 等式 $f(j) = f(j-m)$ 判, 不必 hashmap (固定窗口距离决定)
- [ ] 边界: $j$ 取值范围 $[m, n]$ 闭区间, 即 prefix 数组下标 $[m, n]$
- [ ] 报告答案时讲清楚 "**(i, j) 是切刀位置**", 中段是 `s[i:j]` (左闭右开), 不是切点周围

### 一句话总结

D/R 均分 = **2 刀必存在**(Necklace Splitting Theorem 特例) + **化归为长度 $n/2$ 的固定滑窗找 $f(j) = f(j-m)$** + 存在性靠**离散 IVT + 奇偶性**证 (g 始终偶, 从 $+f(m)$ 到 $-f(m)$ 步长 $\\le 2$ 必经 0)。$O(n)$ 时间, $O(1)$ 空间。
"""


PROBLEM_SPEC: dict = {
    "title": TITLE,
    "leetcode_id": None,
    "url": None,
    "difficulty": "medium",
    "tags": [
        "prefix-sum", "string", "fixed-window", "discrete-ivt",
        "necklace-splitting", "hobby-rice", "parity",
    ],
    "pattern": "prefix-sum",
    "family": "prefix-sum",
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
    """Insert-or-update the necklace-splitting problem. Return 0 on success."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")          # CJK TITLE -> avoid cp1252 stdout crash
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_necklace_split_dr")
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
