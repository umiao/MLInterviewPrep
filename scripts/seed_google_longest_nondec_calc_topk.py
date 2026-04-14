"""Seed Google coding prep for T-P1-207:

1. New custom problem: Longest Non-decreasing Subarray (+ 2 follow-ups:
   allow one replacement; one-shot replace-all-X-with-Y).
2. Append Google addendum to LC 347 (Top-K Frequent): heap O(N log K) vs
   bucket-sort O(N), tie-break notes, distributed cross-ref.
3. Fill LC 224 (Basic Calculator) notes: stack with sign-flip, recursion
   for parens, shunting-yard alternative, relation to LC 227 / 772.

Idempotent: re-running updates in place, does not duplicate content.
Chinese prose per feedback_lc_notes_chinese; code + complexity English.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SOURCE_BADGE = "Google 2026-04-17 prep"


def merge_json_tag(existing: str | None, tag: str) -> str:
    tags = json.loads(existing) if existing else []
    if tag not in tags:
        tags.append(tag)
    return json.dumps(tags, ensure_ascii=False)


def merge_source(existing: str | None, new: str) -> str:
    if not existing:
        return new
    parts = [s.strip() for s in existing.split(",") if s.strip()]
    if new not in parts:
        parts.append(new)
    return ", ".join(parts)


def append_notes(existing: str | None, addendum: str, marker: str) -> str:
    if existing and marker in existing:
        # Replace the marked section with the new version for idempotent updates.
        idx = existing.index(marker)
        # trim back to preceding separator if present
        head = existing[:idx].rstrip()
        if head.endswith("---"):
            head = head[:-3].rstrip()
        if not head:
            return addendum
        return head + "\n\n---\n\n" + addendum
    if not existing:
        return addendum
    return existing.rstrip() + "\n\n---\n\n" + addendum


# ---------------------------------------------------------------------------
# (1) Longest Non-decreasing Subarray — new custom problem
# ---------------------------------------------------------------------------

LND_TITLE = "Longest Non-decreasing Subarray"
LND_DESC = """Given an integer array `a`, find the length of the longest
contiguous subarray that is non-decreasing (a[i] <= a[i+1]).

Example: a = [1, 3, 2, 2, 5, 6, 4] -> answer = 4 (subarray [2,2,5,6]).

Follow-up A ("allow one replacement"): you may change the value of **at
most one** element in the array to any integer. Return the longest
non-decreasing subarray achievable after the single replacement.

Follow-up B ("one-shot replace all X with Y"): you are given two integers
X, Y and must replace **every** occurrence of X in the array with Y
(a single batch operation, not per-index choice). Return the longest
non-decreasing subarray after this replacement, computed in
O(n log n) or better using run grouping + boundary recompute, without
re-scanning the array in O(n) for every possible (X, Y) query.

Interview context: Google 2026-04-17 coding. Classic O(N) baseline plus
two DP / segment-style follow-ups that test whether the candidate can
generalize the linear scan to (a) local-edit DP and (b) batch-update
reconstruction."""

LND_NOTES = """## Longest Non-decreasing Subarray (Google 2026-04-17)

### Baseline: O(N) 扫描
维护 `cur` 表示以当前位置结尾的最长非递减段长度：
- 若 `a[i] >= a[i-1]`：`cur += 1`
- 否则：`cur = 1`
- 答案 = `max(cur)`。

```python
def longest_nondec(a: list[int]) -> int:
    if not a:
        return 0
    best = cur = 1
    for i in range(1, len(a)):
        cur = cur + 1 if a[i] >= a[i-1] else 1
        best = max(best, cur)
    return best
```

- Time: $O(N)$, Space: $O(1)$.
- 对比"最长上升子序列" (LIS, LC 300)：LIS 要求**严格**递增且**非连续**，
  需 $O(N \\log N)$ patience sort。本题是**连续**非递减，简单扫描即可。

### Follow-up A: 允许一次替换
**问题**：可把至多一个元素改成任意整数，求最长非递减连续段。

#### 关键观察
替换的最优策略永远是：把某个"破坏单调性的位置"改成使左右两侧可拼接的值。
设位置 $i$ 是下降点 (`a[i] < a[i-1]`)，则：
- 改 `a[i-1]` 为一个 $\\le a[i]$ 且 $\\ge a[i-2]$ 的值，前提是
  $a[i-2] \\le a[i]$ — 此时左段 $[L, i-1]$ 与右段 $[i, R]$ 拼接。
- 或者改 `a[i]` 为一个 $\\ge a[i-1]$ 且 $\\le a[i+1]$ 的值，前提是
  $a[i-1] \\le a[i+1]$。

#### 双状态 DP
$\\text{dp}[i][0]$ = 以 $i$ 结尾、**未使用**替换的最长非递减段。
$\\text{dp}[i][1]$ = 以 $i$ 结尾、**已使用**替换的最长非递减段。

转移：
$$dp[i][0] = \\begin{cases} dp[i-1][0] + 1 & a[i] \\ge a[i-1] \\\\ 1 & \\text{otherwise} \\end{cases}$$
$$dp[i][1] = \\max\\begin{cases}
dp[i-1][1] + 1 & a[i] \\ge a[i-1] \\\\
dp[i-1][0] + 1 & \\text{改 } a[i-1] \\text{ 使衔接成立，即 } a[i] \\ge a[i-2] \\\\
dp[i-1][0] + 1 & \\text{改 } a[i] \\text{ 为任意 } \\ge a[i-1]
\\end{cases}$$

实际上"改 $a[i]$"这一路总成立（因为 $a[i]$ 可被改成 $a[i-1]$），所以简化：
- `dp[i][0] = dp[i-1][0] + 1 if a[i] >= a[i-1] else 1`
- `dp[i][1] = max(dp[i-1][1] + 1 if a[i] >= a[i-1] else 1, dp[i-1][0] + 1)`

```python
def longest_nondec_one_replace(a: list[int]) -> int:
    n = len(a)
    if n <= 2:
        return n
    dp0 = dp1 = 1
    best = 1
    for i in range(1, n):
        new0 = dp0 + 1 if a[i] >= a[i-1] else 1
        # choice 1: extend an already-replaced run
        ext_repl = dp1 + 1 if a[i] >= a[i-1] else 1
        # choice 2: use replacement now — replace a[i] or a[i-1]
        use_now = dp0 + 1
        new1 = max(ext_repl, use_now)
        dp0, dp1 = new0, new1
        best = max(best, dp1)
    return best
```

- Time: $O(N)$, Space: $O(1)$（滚动）。
- **陷阱**：容易漏掉 `dp1 = max(dp1, dp0 + 1)` 这一路（即"现在使用"的
  选择），导致仅能扩展已替换段，错解。

### Follow-up B: 一次性 replace-all(X -> Y), O(n log n)
**问题**：给定 $(X, Y)$，将数组中**所有** $X$ 位置同时替换为 $Y$，
求替换后的最长非递减连续段。要求**比 O(n) 重扫更优**（因为可能有多组
query，每组 $O(\\log n)$）。

#### 结构分解：run grouping
把原数组切成极大非递减段（runs）。替换操作只会影响**包含 X 或其邻居**
的段边界，其它段完全不变。

1. **预处理**：求所有极大非递减 runs，记为 $R_1, R_2, \\ldots, R_m$，
   每个 $R_j$ 是左闭右闭区间 $[l_j, r_j]$。维护**当前**所有 run 长度的
   multiset（例如 `SortedList` 或 max-heap，本解用 multiset 因为需要
   动态增删）。
2. **建索引**：按值 $v$ 把所有出现位置索引起来 `pos_of[v] = [i1, i2, ...]`。
   查询 $(X, Y)$ 时，只需访问 `pos_of[X]` 以及这些位置所在 run 的邻居。

#### Query 处理
对每个 `pos_of[X]` 中的位置 $i$，以及 $i-1, i+1$（可能跨 run 影响），
**局部重算** run 边界：
- 若把 $a[i]$ 临时改为 $Y$，检查 `a[i-1] ?<= Y` 和 `Y ?<= a[i+1]`，
  决定 $i$ 与左右 run 是否合并/切断。
- 从 multiset 中**删除旧的受影响 run 长度**，**插入合并后的新 run 长度**。
- 查询答案 = multiset 最大值。
- 查询完后**回滚**（undo stack）以处理下一个 $(X, Y)$ query。

#### 复杂度
- 预处理 runs: $O(n)$。
- 每个 query 涉及的位置数 = $|\\text{pos\\_of}[X]|$。总操作数 $\\le$
  $2n$（每位置至多碰 1 次），但若 $X$ 出现 $k$ 次，单 query 就是
  $O(k \\log n)$（multiset 操作）。
- 跨 query 总复杂度 $O((n + \\sum_q k_q) \\log n)$。若 $\\sum k_q = O(n)$
  则整体 $O(n \\log n)$，达标。

#### 为什么 O(n) 重扫不够用？
多 query 场景下 $O(n \\cdot q)$ 会退化。面试官若强调"O(n log n)"，暗
示的正是 offline batch + run multiset 维护。这也和 LC 2050 Parallel
Courses III / LC 2158 Amount of New Area Painted 一类"区间合并 +
multiset max"是同族思路。

```python
# Skeleton — production code would encapsulate the multiset / undo stack.
from sortedcontainers import SortedList

def preprocess_runs(a):
    runs = []  # list of [l, r]
    n = len(a); l = 0
    for r in range(1, n + 1):
        if r == n or a[r] < a[r-1]:
            runs.append([l, r-1]); l = r
    return runs

def query_replace_all(a, runs, run_lens: SortedList, X, Y):
    # For brevity: if X not in index, return current max.
    # Otherwise, for each occurrence of X: merge/split neighboring runs
    # and update run_lens multiset. Return max, then roll back.
    pass  # full implementation ~80 LoC; see interview discussion.
```

### 错误思路对比

| 思路 | 复杂度 | 错在哪 |
|------|--------|--------|
| follow-up A 仅 dp1 = dp1+1 or reset | $O(N)$ | 漏"现在使用替换"分支，低估答案 |
| follow-up B 每 query 都 O(n) 重扫 | $O(nq)$ | 面试官要 O(n log n)，退化 |
| follow-up B 用线段树维护区间单调性 | $O(n \\log n)$ | 可行但编码复杂；multiset+run 更简洁 |
| 误用 LIS 思路 ($O(n \\log n)$ patience) | — | LIS 不要求连续，解的是不同问题 |

### 面试应答 checklist
1. 澄清：**连续**还是**子序列**？**非递减**还是**严格递增**？有没有负数？
2. 给 O(N) 基线 + 代码。
3. Follow-up A：双状态 DP 明确"两种使用时机"(扩展已替换 / 现在才用)。
4. Follow-up B：提 run 分解 + multiset + 局部合并；指出和 LC 2050 族同构。
5. 被问"如果允许 K 次替换"：推广到 $O(N \\cdot K)$ DP，同滑窗"最多 K 次
   翻转 0/1" (LC 1004 Max Consecutive Ones III) 思路。
"""


# ---------------------------------------------------------------------------
# (2) LC 347 Top-K Frequent — append Google addendum
# ---------------------------------------------------------------------------

LC347_MARKER = "## [Google 2026-04-17] LC 347 Top-K Frequent Elements"
LC347_ADDENDUM = """## [Google 2026-04-17] LC 347 Top-K Frequent Elements

### 题意
给整数数组 `nums` 和整数 `k`，返回出现频次最高的 $k$ 个元素。

### 解法一：size-K min-heap — O(N log K)
```python
import heapq
from collections import Counter

def topk_frequent(nums: list[int], k: int) -> list[int]:
    cnt = Counter(nums)
    # 保留 size-K min-heap: 堆顶是当前 top-K 里频次最低的元素
    heap: list[tuple[int, int]] = []  # (freq, num)
    for num, freq in cnt.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return [num for _, num in heap]
```

- Time: $O(N + U \\log K)$，$U$ 是 unique 元素数，$U \\le N$。
- Space: $O(U + K)$。
- **适用场景**：$K \\ll U$ 时最优；流式也友好（元素逐个来，堆维护 top-K）。

### 解法二：bucket sort — O(N)
观察：频次的取值范围是 $[1, N]$，可按频次分桶。

```python
from collections import Counter

def topk_frequent_bucket(nums: list[int], k: int) -> list[int]:
    cnt = Counter(nums)
    n = len(nums)
    buckets: list[list[int]] = [[] for _ in range(n + 1)]
    for num, freq in cnt.items():
        buckets[freq].append(num)
    out: list[int] = []
    for freq in range(n, 0, -1):
        for num in buckets[freq]:
            out.append(num)
            if len(out) == k:
                return out
    return out
```

- Time: $O(N)$ (计数 + 桶分配 + 从高频向低频取 K)。
- Space: $O(N)$。
- **适用场景**：$K$ 接近 $U$ 或 worst-case 严格 $O(N)$ 要求。

### 解法对比

| 方法 | Time | Space | 适用 |
|------|------|-------|------|
| `sorted(cnt.items())[:k]` | $O(U \\log U)$ | $O(U)$ | 最简；$U$ 小时 OK |
| Min-heap size K | $O(N + U \\log K)$ | $O(U + K)$ | $K \\ll U$，流式 |
| Bucket sort | $O(N)$ | $O(N)$ | 最优 worst-case |
| QuickSelect on (freq, num) | 期望 $O(N)$ | $O(U)$ | 无需输出顺序 |

### Tie-break 细节（对比 LC 692 Top-K Frequent Words）
- LC 347 输出**无顺序要求**（任意顺序）。
- LC 692 要求"同频按字典序升序"，堆比较器需**按 word 反向**（见 LC 692
  addendum）。

### 分布式 / 大数据扩展
见 LC 692 Top-K Frequent Words 的 addendum：Map-Shuffle-Reduce、salting
热键、Count-Min Sketch 近似 Top-K。LC 347 的分布式版本只需把 word
替换为 int，其余完全一致。

### QuickSelect 备选
若只需"找到 top-K"不要求排序，partition on frequency:
- 期望 $O(N)$，worst-case $O(N^2)$ (可用 median-of-medians 保证)。
- 实战不如 bucket sort 干净；面试可提但优先写 bucket。
"""


# ---------------------------------------------------------------------------
# (3) LC 224 Basic Calculator — fill notes
# ---------------------------------------------------------------------------

LC224_NOTES = """## LC 224 Basic Calculator (Google 2026-04-17)

### 题意
实现基本计算器：字符串含非负整数、`+`、`-`、`(`、`)`、空格。无 `*`、
`/`。返回求值结果。例 `"(1+(4+5+2)-3)+(6+8)"` → `23`。

### 解法一：单栈 + 符号翻转 — O(N) / O(N)
核心技巧：用栈保存**遇到左括号时的外层累积符号** (`sign_stack`)，
以便展开括号时正确继承。

```python
def calculate(s: str) -> int:
    # Stack stores the sign-multiplier active before each open parenthesis.
    sign_stack: list[int] = [1]
    sign = 1           # current sign, +1 or -1
    result = 0
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isdigit():
            num = 0
            while i < n and s[i].isdigit():
                num = num * 10 + int(s[i]); i += 1
            result += sign * num
            continue
        elif c == '+':
            sign = sign_stack[-1]
        elif c == '-':
            sign = -sign_stack[-1]
        elif c == '(':
            # The sign just computed applies to the whole parenthesized group.
            sign_stack.append(sign)
        elif c == ')':
            sign_stack.pop()
        # else: whitespace, skip
        i += 1
    return result
```

- Time: $O(N)$，Space: $O(D)$，$D$ 是括号嵌套深度。
- **不变式**：`sign_stack[-1]` 永远是"当前括号内，外层继承到的符号"。
  看到 `+` / `-`，真实符号 = 外层符号 × 局部符号。

### 解法二：递归下降 — O(N) / O(D)
遇到 `(` 递归调用，遇到 `)` 返回；主循环维护 `num, sign, result`。

```python
def calculate_rec(s: str) -> int:
    s_iter = iter(s)

    def helper() -> int:
        num = 0; sign = 1; result = 0
        while True:
            try:
                c = next(s_iter)
            except StopIteration:
                break
            if c.isdigit():
                num = num * 10 + int(c)
            elif c == '+':
                result += sign * num; num = 0; sign = 1
            elif c == '-':
                result += sign * num; num = 0; sign = -1
            elif c == '(':
                num = helper()
            elif c == ')':
                break
            # else whitespace
        return result + sign * num

    return helper()
```

- 更易读；风险：深度栈溢出（Python 默认 recursion limit 1000）。
- 面试可两种都写；若嵌套极深，优先迭代版。

### Shunting-yard / 两栈法（通用运算符求值）
若扩展到有 `*`, `/`（LC 227 / 772），单栈翻转法不够。Dijkstra 的
**shunting-yard** 算法用运算符栈 + 输出队列，把中缀转逆波兰 (RPN)，
再求值 RPN：
- 数字 → 输出。
- 运算符 → 弹出栈中优先级 $\\ge$ 当前的到输出，然后把当前入栈。
- `(` → 入栈；`)` → 弹到遇 `(`。
- 结束把栈剩余弹入输出。
- 求值 RPN：数字压栈，遇运算符弹两个算。

**简化版：直接两栈求值**（operand stack + operator stack），更少步骤。

### LC 224 / 227 / 772 关系

| 题号 | 含 `+ -` | 含 `* /` | 含括号 | 主流解法 |
|------|----------|----------|--------|----------|
| 224 | ✓ | ✗ | ✓ | 单栈 sign_stack 或递归 |
| 227 | ✓ | ✓ | ✗ | 单栈：`*/` 直接改栈顶，`+-` 带符号入栈 |
| 772 | ✓ | ✓ | ✓ | 递归 + 227 的栈法；或 shunting-yard |
| 770 | — | — | — | 多项式计算器，表达式树更合适 |

### LC 227 骨架（对照参考）
```python
def calculate_ii(s: str) -> int:
    stack: list[int] = []
    num, op = 0, '+'
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isdigit():
            num = num * 10 + int(c)
        if (not c.isdigit() and c != ' ') or i == n - 1:
            if op == '+': stack.append(num)
            elif op == '-': stack.append(-num)
            elif op == '*': stack.append(stack.pop() * num)
            elif op == '/': stack.append(int(stack.pop() / num))
            op, num = c, 0
        i += 1
    return sum(stack)
```

注意 `int(a / b)` 而非 `a // b`：Python 的 `//` 对负数向下取整
(`-3 // 2 == -2`)，而题目要求**向 0 截断** (`-3 / 2 == -1`)。

### 错误思路对比

| 思路 | 问题 |
|------|------|
| `eval(s)` | 面试禁用；也规避了考点 |
| 直接数字栈无符号栈 | 遇到 `-(...)` 展开时符号错 |
| 单栈法直接扩展到 `*/` | 优先级失败，需 shunting-yard 或两栈 |
| `//` 替代 `int(a/b)` | LC 227 负数向下取整错 (-3/2) |

### 面试应答 checklist
1. 澄清：表达式可能含空格？负数？会不会出现 `-(1+2)` 这种**一元负号**？
2. 先给单栈 sign_stack 解法（最经典）。
3. 提 shunting-yard 作为"若扩展到 *,/ 如何统一"。
4. 讲清 LC 227 的 `int(a/b)` 向 0 截断陷阱。
5. 提到 LC 770 Basic Calculator IV（多项式+变量）只能走表达式树。
"""


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def upsert_problem_notes(cur: sqlite3.Cursor, lc_id: int, new_notes: str, marker: str) -> int:
    cur.execute(
        "SELECT id, notes, company_tags, source FROM problems WHERE leetcode_id=?",
        (lc_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"LC {lc_id} not found in problems table")
    pid, notes, company_json, source = row
    merged_notes = append_notes(notes, new_notes, marker)
    new_company = merge_json_tag(company_json, "Google")
    new_source = merge_source(source, SOURCE_BADGE)
    cur.execute(
        "UPDATE problems SET notes=?, company_tags=?, source=? WHERE id=?",
        (merged_notes, new_company, new_source, pid),
    )
    return pid


def upsert_lnd_problem(cur: sqlite3.Cursor) -> int:
    cur.execute(
        "SELECT id FROM problems WHERE leetcode_id IS NULL AND title=?",
        (LND_TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    tags_json = json.dumps(
        ["array", "scan", "dp", "run-grouping", "multiset"],
        ensure_ascii=False,
    )
    company_json = json.dumps(["Google"], ensure_ascii=False)
    if row is not None:
        pid = row[0]
        cur.execute(
            "UPDATE problems SET description=?, notes=?, tags=?, pattern=?, category=?, "
            "company_tags=?, source=?, difficulty=?, priority=? WHERE id=?",
            (
                LND_DESC, LND_NOTES, tags_json, "scan-dp", "algorithm",
                company_json, SOURCE_BADGE, "medium", 1, pid,
            ),
        )
        return pid
    cur.execute(
        "INSERT INTO problems (leetcode_id, title, description, notes, tags, pattern, category, "
        "company_tags, source, difficulty, priority, is_completed, created_at) "
        "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (
            LND_TITLE, LND_DESC, LND_NOTES, tags_json, "scan-dp", "algorithm",
            company_json, SOURCE_BADGE, "medium", 1, now,
        ),
    )
    return cur.lastrowid


def verify_examples() -> None:
    """Sanity-check each algorithm against hand-computed cases."""
    # baseline
    def longest_nondec(a):
        if not a: return 0
        best = cur = 1
        for i in range(1, len(a)):
            cur = cur + 1 if a[i] >= a[i-1] else 1
            best = max(best, cur)
        return best
    assert longest_nondec([1,3,2,2,5,6,4]) == 4
    assert longest_nondec([]) == 0
    assert longest_nondec([5]) == 1
    assert longest_nondec([1,1,1]) == 3

    # follow-up A
    def longest_nondec_one_replace(a):
        n = len(a)
        if n <= 2: return n
        dp0 = dp1 = 1; best = 1
        for i in range(1, n):
            new0 = dp0 + 1 if a[i] >= a[i-1] else 1
            ext_repl = dp1 + 1 if a[i] >= a[i-1] else 1
            use_now = dp0 + 1
            new1 = max(ext_repl, use_now)
            dp0, dp1 = new0, new1
            best = max(best, dp1)
        return best
    # [1,3,2,4]: change 3->2 or 2->3 -> full length 4
    assert longest_nondec_one_replace([1,3,2,4]) == 4
    # [1,5,3,4]: change 5 -> any value in [1,3] -> fully non-decreasing, length 4
    assert longest_nondec_one_replace([1,5,3,4]) == 4
    # [1,5,3,2,6]: one replace can only rescue length-3 runs locally
    assert longest_nondec_one_replace([1,5,3,2,6]) == 3

    # LC 347 min-heap
    import heapq
    from collections import Counter
    def topk_heap(nums, k):
        cnt = Counter(nums); heap = []
        for num, f in cnt.items():
            heapq.heappush(heap, (f, num))
            if len(heap) > k: heapq.heappop(heap)
        return sorted(num for _, num in heap)
    assert topk_heap([1,1,1,2,2,3], 2) == [1,2]

    # LC 347 bucket
    def topk_bucket(nums, k):
        cnt = Counter(nums); n = len(nums)
        buckets = [[] for _ in range(n + 1)]
        for num, f in cnt.items(): buckets[f].append(num)
        out = []
        for f in range(n, 0, -1):
            for num in buckets[f]:
                out.append(num)
                if len(out) == k: return sorted(out)
        return sorted(out)
    assert topk_bucket([1,1,1,2,2,3], 2) == [1,2]

    # LC 224 stack
    def calculate(s):
        sign_stack = [1]; sign = 1; result = 0
        i, n = 0, len(s)
        while i < n:
            c = s[i]
            if c.isdigit():
                num = 0
                while i < n and s[i].isdigit():
                    num = num * 10 + int(s[i]); i += 1
                result += sign * num
                continue
            elif c == '+': sign = sign_stack[-1]
            elif c == '-': sign = -sign_stack[-1]
            elif c == '(': sign_stack.append(sign)
            elif c == ')': sign_stack.pop()
            i += 1
        return result
    assert calculate("(1+(4+5+2)-3)+(6+8)") == 23
    assert calculate("1-(2+3)") == -4
    assert calculate("2-1 + 2 ") == 3
    print("algorithm self-checks: all passed [OK]")


def main() -> None:
    verify_examples()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    lnd_id = upsert_lnd_problem(cur)
    lc347_id = upsert_problem_notes(cur, 347, LC347_ADDENDUM, LC347_MARKER)
    # LC 224 has no notes yet, so just set notes directly (marker-free initial seed).
    lc224_id = upsert_problem_notes(cur, 224, LC224_NOTES, "## LC 224 Basic Calculator (Google 2026-04-17)")
    conn.commit()
    cur.execute(
        "SELECT id, COALESCE(leetcode_id, 0), title, length(notes) FROM problems WHERE id IN (?,?,?)",
        (lnd_id, lc347_id, lc224_id),
    )
    for r in cur.fetchall():
        print(f"problem id={r[0]} lc={r[1]} title={r[2]!r} notes_len={r[3]}")
    conn.close()


if __name__ == "__main__":
    main()
