"""Seed Google R2 Coding problem: LC 276 Paint Fence + 环形 follow-up.

User-provided content (Discord 2026-05-07 msg 1501806250248376431,
attachment ~7KB). The post is already polished: linear-version derivation
(3D DP -> 2D same/diff -> 1D recurrence + closed form), retrospective on
two failed 容斥 attempts, then a circular-fence follow-up with the
'enumerate-first-two-positions + linear-DP + check-both-wrap-triples'
template, and a 思维顺序 closing lesson ("don't reach for 容斥 first --
let DP carry, optimize later").

Critical content preserved:

  - The "two wrap triples" gotcha for the circular variant -- it is
    `(p_{n-1}, p_n, p_1)` AND `(p_n, p_1, p_2)`, NOT just one. User's
    failed 容斥 attempt got `48` for k=3,n=4 when the truth is `54`.
  - The general template for ring/cycle DP: fix the coupled prefix as
    enumeration parameters, run linear DP on the rest, check coupling
    constraints at the end. Reusable for LC 213 House Robber II,
    necklace-coloring problems, etc.

LC 276 row does not exist in problems (not in bulk LC import). This seed
INSERTs (or UPDATEs on re-run) by canonical key leetcode_id=276. Sets
family='dp' pattern='constraint-counting-dp' to flag the problem class
for future siblings (LC 198/213/790/...). company_tags=['Google'],
notes ~5.5KB preserving user's full exposition + house-style footer
(易错点, 一句话总结).

Per `feedback_pinterest_two_tier_notes`: per-problem note in
`problems.notes`, ProblemDrawer renders via `db://<id>`. Doc 92 R2 Coding
Index is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this commit
to add a NEW `### DP / Counting` section at end-of-list (before the
maintenance footer) -- DP/Counting did not previously exist in the index.

Idempotent. leetcode_id=276 is the canonical key. First run on missing row:
1 INSERT. Re-run on identical state: 0 writes.

Run: python scripts/seed_google_r2_lc276_paint_fence_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 276
TITLE = "Paint Fence"
URL = "https://leetcode.com/problems/paint-fence/"
SOURCE_LABEL = "Google R2 2026-05"

COMPANY_TAGS = ["Google"]

NOTES = """\
## LC 276. Paint Fence

### 题目

`n` 个柱子排成一行, `k` 种颜色, **任意三个连续柱子不能全同色** (注意不是相邻不能同色!), 问总方案数。

**Follow-up**: 如果柱子排成**一个环** (首尾相邻), 怎么做?

---

### Part 1: 线性版本的推导

#### 起点: 三维 DP (能跑, 但冗余)

最直接的状态:

```
dp[i][c][s] = 长度 i、末位颜色 c、s 表示是否和前一位同色 (0/1)
```

转移:

```
dp[i][c][0] = Σ_{c' ≠ c} ( dp[i-1][c'][0] + dp[i-1][c'][1] )
dp[i][c][1] = dp[i-1][c][0]                    # 前一位也是 c, 但前前位不是 c
```

复杂度 `O(n·k²)`。**正确, 但 c 这一维其实是冗余的**。

#### 关键观察: 颜色对称性

所有颜色地位平等, 所以 `dp[i][c][s]` 对每个 `c` 取值都一样。

直接把颜色维度扔掉, 定义:

```
same(i) = 长度 i、末两位同色 的总方案数
diff(i) = 长度 i、末两位异色 的总方案数
```

转移变得极清爽:

```
same(i) = diff(i-1)                       # 要末两位同色, 则上一步末两位必须不同
diff(i) = (k-1) · ( same(i-1) + diff(i-1) )    # 末位有 k-1 种异色可选
```

`base`: `same(1) = 0`, `diff(1) = k` (把单个柱子记到 diff 里方便统一), 答案 `same(n) + diff(n)`。

#### 等价闭式

进一步合并, 记 `a(n)` 为长度 `n` 末位为某固定颜色的方案数 (由对称性, `a(n) = (same(n) + diff(n)) / k`):

```
a(n) = (k-1) · ( a(n-1) + a(n-2) )
a(1) = 1,  a(2) = k
答案 = k · a(n)
```

**直觉**: 长度 `n` 末位为 `c`, 按倒数第二位是不是 `c` 分类:

- 倒数第二位 ≠ `c` → 接 `c`: `(k-1) · a(n-1)`
- 倒数第二位 = `c` → 倒数第三位必须 ≠ `c`, 再接 `cc`: `(k-1) · a(n-2)`

加起来就是上式。**这是线性版的"金标准"推导** -- 按末尾连续性切分, 每种情况自然合法, 无需容斥。

#### 我们走过的弯路 (教训)

1. **试图用容斥** `A(n,c) = T(n-1) − T(n-3)`: 扣多了。要扣的是"末尾两个 `c`"这种坏延伸, 按颜色应是 `A(n-3, ≠c)` 而不是总数 `T(n-3)`。
2. **三维 DP 写错 base case** (`idx == 2: return k`) 和**让 `idx-3` 跑到负数没出口**: 递归飞掉变成 TLE。

**根因都一样: 不肯枚举状态空间, 想走代数捷径。**

---

### Part 2: 环形 Follow-up

#### 新约束

把柱子摆成环后, wrap-around 多出两个三元组必须不全同色:

```
(p_{n-1}, p_n, p_1)
(p_n,    p_1, p_2)
```

注意**有两个**, 不是一个。这是第一个容易踩的坑。

#### 一个失败的思路 (教训)

直觉: 先用线性公式算 `k·a(n)`, 再扣掉环上不合法的。

误导性的尝试: 「末两位同色的方案数是 `k·(k-1)·a(n-2)`, 这些会让 `p_1 = p_n` 的填法失效, 所以答案 = `k·a(n) − k·(k-1)·a(n-2)`」。

为什么错? 验证 `k=3, n=4`:

- 线性总数 `66`
- 公式给 `66 − 18 = 48`
- 真实答案 `54`

两个错误:

- "末两位同色" ≠ "wrap 三连"。wrap 三连要求 `p_{n-1} = p_n = p_1`, 是一个**更小**的子集。
- 漏了第二个 wrap 约束 `(p_n, p_1, p_2)`。

容斥**能**做对, 但要算 `|A|, |B|, |A∩B|`, 每个都是带多重约束的子计数, 路径多、易错 -- **心智负担高**。

#### 降低心智负担的通用套路: 固定耦合部分, 剩下交给 DP

环形 = 首尾耦合的线性。处理首尾耦合的通用思路:

> **把"参与 wrap 约束的前缀"作为枚举参数固定, 剩下用线性 DP 跑, 结尾再检查 wrap 是否被违反。**

这里 wrap 约束涉及 `p_1, p_2, p_{n-1}, p_n` 四个位置。"前缀"那侧只有 `p_1, p_2` -- 把它俩固定就行。

#### 算法骨架

```
for p1 in colors:
    for p2 in colors:
        线性 DP, 状态 (prev, curr), 从 (p1, p2) 出发跑到长度 n
        遍历末态 (p_{n-1}, p_n):
            如果 (p_{n-1}, p_n, p1) 不全同 且 (p_n, p1, p2) 不全同:
                累加 dp[n][p_{n-1}][p_n]
```

转移规则同线性 DP: 状态 `(a, b)` 转到 `(b, c)`, 要求不出现 `a = b = c`。

```python
class Solution:
    def numWaysCircular(self, n: int, k: int) -> int:
        if n == 1: return k
        if n == 2: return k * k

        total = 0
        for p1 in range(k):
            for p2 in range(k):
                # dp[a][b] = 当前长度下 (倒数第二位=a, 末位=b) 的方案数
                dp = [[0] * k for _ in range(k)]
                dp[p1][p2] = 1

                for _ in range(n - 2):           # 已经放了 p1, p2, 再走 n-2 步
                    nxt = [[0] * k for _ in range(k)]
                    for a in range(k):
                        for b in range(k):
                            if not dp[a][b]: continue
                            for c in range(k):
                                if a == b == c: continue   # 线性三连
                                nxt[b][c] += dp[a][b]
                    dp = nxt

                # 末态检查 wrap
                for pn_1 in range(k):
                    for pn in range(k):
                        if pn_1 == pn == p1: continue       # 三元组 (n-1, n, 1)
                        if pn == p1 == p2: continue         # 三元组 (n, 1, 2)
                        total += dp[pn_1][pn]

        return total
```

复杂度 `O(n · k^4)`, `k` 很小时完全可接受。

#### 为什么这么做心智负担低

| 维度 | 容斥写法 | 枚举头两位 + DP |
|------|----------|------------------|
| 要算几个互相不独立的子计数 | 3+ 个 (A、B、A∩B…) | 0 个 |
| 容易漏 wrap 约束吗 | 容易 (前面就漏了一个) | 不会, 循环里挨个 if |
| 颜色对称性能否偷懒 | 能但要小心 | 写完再优化也行 |
| 改约束 (比如禁止四连) 容易吗 | 整个推导推倒重来 | 改 if 条件即可 |

**核心思想**: **当你不确定容斥写得对不对, 就让 DP 来兜底。** 容斥适合证明性、闭式型解, DP 适合在面试时稳定写对。

#### 优化 (可选)

利用颜色对称性, 把外层枚举从 `k²` 压成 `O(1)`: 所有 `(p_1, p_2)` 按"是否同色"分两类, 每类 DP 一次再乘上情况数。这就把复杂度压到 `O(n · k²)`。但**面试中先写朴素版, 时间有富余再优化**。

---

### 收尾: 思维顺序的总结

LC 276 这种"约束型 DP"题, 被加了 follow-up 后特别容易翻车。可以遵循这套**思维顺序**:

1. **线性版**: 先把"按末尾结构切分"的状态写清楚 (这里是 same/diff 或末位颜色 + 是否连色)。颜色维度通常可以靠对称性消掉。
2. **环形 / 加约束版**: 第一反应**不要**改公式。先想 wrap 涉及哪几个位置, 把那部分固定为枚举参数, 剩下交给同款线性 DP。
3. **写完正确版后**: 再看能不能用对称性 / 容斥优化。优化是锦上添花, 不是必需。

每次踩坑都是因为反着来 -- 先想代数捷径, 再撞墙后回头补 DP。把顺序倒过来, 能省掉很多心智负担。

### 易错点

- **环形版的 wrap 约束有两个**: `(p_{n-1}, p_n, p_1)` AND `(p_n, p_1, p_2)`, 不是一个。漏掉第二个会把答案算偏 (k=3,n=4 应得 54 不是 48)。
- **"末两位同色" ≠ "wrap 三连"**: 容斥试图用前者扣后者, 子集大小不匹配, 直接错。
- **同 sentence 三连只看连续三位**: 注意题目说的是"任意三个连续", 所以 `aab` 合法 (没有三连), `aaa` 不合法。容易和"任意相邻不同色"混淆。
- **base case 别错位**: `same(1) = 0` (单柱子谈不上"末两位"), `diff(1) = k`; 闭式版 `a(1) = 1, a(2) = k`。混了会算错小 n。
- **环形 DP 别忘 n=1, n=2 早退**: `n=1` 时无 wrap 约束 (一个柱子怎么转也没有三连) 答案 `k`; `n=2` 时也无三连约束答案 `k*k`。
- **$O(n·k^4)$ 是 worst case**, 字面看着大但 `k` 通常 ≤ 10 完全可跑。`k` 很大要用对称性优化压回 `O(n·k^2)`。

### 一句话总结

线性版用 `same/diff` 二维 DP (或闭式 `a(n) = (k-1)(a(n-1)+a(n-2))`) 一遍扫; **环形版别试容斥**, 枚举头两位 `(p_1, p_2)` 锁住耦合, 剩下用同款线性 DP 跑, 末态查两个 wrap 三连即可。复杂度 `O(n·k^4)`, k 小完全够用。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": LEETCODE_ID,
    "title": TITLE,
    "url": URL,
    "difficulty": "medium",
    "tags": ["dp", "counting", "recurrence", "ring-dp", "constraint"],
    "pattern": "constraint-counting-dp",
    "family": "dp",
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
    """Insert-or-update LC 276. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc276_paint_fence")
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
