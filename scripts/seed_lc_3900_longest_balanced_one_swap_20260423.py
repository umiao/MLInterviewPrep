"""Seed LC 3900 "Longest Balanced Substring After One Swap" (Google tag).

User wrote the original O(N * K) version (prefix-sum + bucket of positions +
linear scan inside each bucket). This seed preserves the overall approach --
prefix sum with +1/-1 encoding, hash-map keyed by prefix value listing
positions in increasing order -- and replaces the inner linear scan with a
HAND-WRITTEN binary search (lower_bound on the position list), giving
O(N log N) in the pathological cases where one bucket accumulates many
positions (e.g. alternating patterns).

Idempotent: upserts on leetcode_id=3900. Re-running updates notes in place.
Chinese prose per feedback_lc_notes_chinese; code + complexity English.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from _lc_import_helpers import warn_if_missing_family  # noqa: E402

LEETCODE_ID = 3900
TITLE = "Longest Balanced Substring After One Swap"
URL = "https://leetcode.com/problems/longest-balanced-substring-after-one-swap/"
DIFFICULTY = "medium"
FAMILY_SLUG = "prefix_sum_balance"
SOURCE = "Google 2026-04-23 prep"
CATEGORY = "algorithm"
PATTERN = "prefix-sum + bucket + binary-search"
TAGS = ["string", "prefix-sum", "hash-map", "binary-search"]
COMPANY_TAGS = ["Google"]

DESCRIPTION = """Given a binary string `s` (only '0' and '1'), return the
length of the longest substring that can be made BALANCED (equal number of
'0's and '1's) after performing AT MOST ONE SWAP on `s`.

A "swap" picks two indices i, j in `s` (anywhere in the whole string, not
restricted to the substring) and exchanges `s[i]` and `s[j]`.

Key observation: for a window [l, r), let diff = #1 - #0 inside the window.
- diff == 0: already balanced, no swap needed.
- |diff| == 2: one swap between the window and its complement can flip the
  count. Example: diff == +2 -> swap a '1' inside with a '0' outside;
  feasibility requires at least one '0' to exist outside the window,
  i.e. window_length <= 2 * total_zeros. Symmetric for diff == -2.
- |diff| >= 4: a single swap only moves count by 2, not enough.

Example: s = "11010" -> longest balanced substring after swap = 4
(swap positions 1 and 4: "10011" has balanced substring "1001").

Constraints (typical for LC contest problems of this size):
- 1 <= len(s) <= 10^5
- s consists only of '0' and '1'."""


USER_SOLUTION = r"""```python
# User's original O(N * K) solution (preserved for reference; K = max bucket depth).
from collections import defaultdict

class Solution:
    def longestBalanced(self, s: str) -> int:
        # makes me think of parenthesis matching?
        # 滑动窗口 + 允许差一个的可行性验证
        n = len(s)
        prefixSum = [0] * (n + 1)
        prefixDict = defaultdict(list)
        prefixDict[0].append(0)
        ans = 0
        totalZeros, totalOnes = 0, 0

        for i in range(n):
            diff = 1 if s[i] == '1' else -1
            if s[i] == '1':
                totalOnes += 1
            else:
                totalZeros += 1
            prefixSum[i + 1] = prefixSum[i] + diff
            prefixDict[prefixSum[i + 1]].append(i + 1)

        for i in range(1, n):
            targetKey = prefixSum[i + 1]

            if targetKey in prefixDict:
                for leftIdx in prefixDict[targetKey]:
                    if leftIdx < i + 1:
                        ans = max(ans, i + 1 - leftIdx)
                        break
                    else:
                        break

            if targetKey - 2 in prefixDict:
                for leftIdx in prefixDict[targetKey - 2]:
                    if leftIdx < i + 1:
                        if (i + 1 - leftIdx) <= 2 * totalZeros:
                            ans = max(ans, i + 1 - leftIdx)
                            break
                    else:
                        break

            if targetKey + 2 in prefixDict:
                for leftIdx in prefixDict[targetKey + 2]:
                    if leftIdx < i + 1:
                        if (i + 1 - leftIdx) <= 2 * totalOnes:
                            ans = max(ans, i + 1 - leftIdx)
                            break
                    else:
                        break
        return ans
```
"""


OPTIMIZED_SOLUTION = r"""```python
# Optimized: O(N log N) worst case. Preserves the prefix-sum + bucket idea,
# but the inner scan is replaced with a hand-written lower_bound binary
# search over the (monotonically increasing) position list of each bucket.
class Solution:
    def longestBalanced(self, s: str) -> int:
        n = len(s)
        # prefix[i] = (#1 in s[:i]) - (#0 in s[:i]); +1 for '1', -1 for '0'.
        prefix = [0] * (n + 1)
        # bucket[v] = sorted list of indices p in [0, n] where prefix[p] == v.
        bucket: dict[int, list[int]] = {0: [0]}
        for i, ch in enumerate(s):
            prefix[i + 1] = prefix[i] + (1 if ch == '1' else -1)
            bucket.setdefault(prefix[i + 1], []).append(i + 1)

        total_ones = sum(1 for ch in s if ch == '1')
        total_zeros = n - total_ones

        def lower_bound(arr: list[int], target: int) -> int:
            # Smallest k in [0, len(arr)] with arr[k] >= target. Hand-rolled bisect_left.
            lo, hi = 0, len(arr)
            while lo < hi:
                mid = (lo + hi) >> 1
                if arr[mid] < target:
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        ans = 0
        # For each right boundary r (1..n), look up the leftmost feasible l.
        # Case A (already balanced): prefix[l] == prefix[r], smallest such l gives max length.
        # Case B (diff == +2): prefix[l] == prefix[r] - 2, feasibility r - l <= 2 * total_zeros.
        # Case C (diff == -2): prefix[l] == prefix[r] + 2, feasibility r - l <= 2 * total_ones.
        for r in range(1, n + 1):
            p = prefix[r]

            # Case A: bucket[p][0] is always the smallest index with prefix == p.
            same = bucket[p]
            if same[0] < r:
                ans = max(ans, r - same[0])

            # Cases B & C: binary-search the smallest l >= r - cap (feasibility floor).
            for delta, cap in ((-2, 2 * total_zeros), (2, 2 * total_ones)):
                arr = bucket.get(p + delta)
                if not arr:
                    continue
                l_min = r - cap  # feasibility: r - l <= cap
                k = lower_bound(arr, l_min)
                if k < len(arr) and arr[k] < r:
                    ans = max(ans, r - arr[k])
        return ans
```
"""


NOTES = """## LC 3900 一次交换后的最长平衡子串 (Google 2026-04-23)

### 题意
给定 **binary string** (只含 `'0'`/`'1'`) `s`，允许对 `s` 做**最多一次 swap**
(任选两个下标 `i, j` 交换 `s[i]` 与 `s[j]`，位置不限于子串内)，求操作后
**最长的平衡子串**长度 — "balanced" 指子串中 `'0'` 与 `'1'` 数量相等。

### 核心观察：prefix sum with ±1 encoding
令 `prefix[i]` 为前缀 `s[:i]` 中 (`#1` − `#0`)，每遇 `'1'` 加 `+1`，每遇
`'0'` 减 `-1` (就是**括号匹配**的经典技巧)。子串 `s[l..r)` 的 diff =
$\\text{prefix}[r] - \\text{prefix}[l]$。

按 diff 分三种 case (其余 $|{\\rm diff}| \\ge 4$ 单次 swap 力不从心，直接丢)：

| Case | diff | 需求 | 可行性 |
|------|------|------|--------|
| A | $0$ | 本身已平衡，无需 swap | 永远成立 |
| B | $+2$ | 窗内多一对 `1`，需把窗内一 `1` 与窗外一 `0` 换 | $L \\le 2 \\cdot {\\rm total\\_zeros}$ |
| C | $-2$ | 窗内多一对 `0`，需把窗内一 `0` 与窗外一 `1` 换 | $L \\le 2 \\cdot {\\rm total\\_ones}$ |

**B 的可行性推导**：窗长 $L$，$\\#1_{\\rm in}=(L+2)/2$，$\\#0_{\\rm in}=(L-2)/2$。
外部至少有一个 `0`：$\\text{total\\_zeros} - (L-2)/2 \\ge 1$，整理得
$L \\le 2 \\cdot \\text{total\\_zeros}$。C 对称。

### 原始思路：bucket + 线性扫描
按 prefix 值分 bucket，每个 bucket 里存所有出现过该 prefix 值的位置 (按
位置**天然升序**，因为我们是从左到右扫着塞进去的)。对每个右端点 `r`
(prefix 值为 $p$)：
- Case A：查 `bucket[p]`，取**最小**位置即可获得最长窗口。
- Case B/C：查 `bucket[p ∓ 2]`，从前往后扫 (位置升序即长度降序)，第一个
  满足可行性的位置给出最长可行窗口。

原始代码在 B/C 分支里**线性遍历** bucket。worst case (例如 `"0101...01"`
这类 prefix 值反复震荡在少量值之间) 单个 bucket 可能有 $O(N)$ 个位置，
整体退化到 $O(N^2)$。

### 优化：hand-written binary search (lower_bound)
保留 bucket 骨架不变，把 B/C 的"找第一个满足 `l >= r - cap` 的位置"
换成**手写二分**。每次查询 $O(\\log K)$，$K$ 是 bucket 深度，整体
**$O(N \\log N)$** worst case、$O(N)$ 期望。

Case A 仍然只需 `bucket[p][0]` — bucket 已排序，最小即首个，无需二分。
(这点很容易手滑多写一次二分，其实一次 `[0]` 取值就完了。)

```python
def lower_bound(arr: list[int], target: int) -> int:
    # Smallest k in [0, len(arr)] with arr[k] >= target.
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) >> 1
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

### 原始代码 (保留参考)
""" + USER_SOLUTION + """
### 优化版
""" + OPTIMIZED_SOLUTION + """
### 复杂度
- 原始：Time $O(N \\cdot K)$，worst case $O(N^2)$；Space $O(N)$ (bucket + prefix)。
- 优化：Time $O(N \\log N)$；Space $O(N)$。
- 进一步可把 Case A 合并进循环、用 **first-occurrence-only dict** (只存每个
  prefix 值首次出现位置) 把 Case A 的 space 降到**单 dict 值**，但 B/C 仍
  需完整 bucket，所以整体 $O(N)$ space 不变。

### 易错点
- **Case A 别误写成二分**：`bucket[p][0]` 直接就是最小，二分只在 B/C 需要。
- **可行性 floor `r - cap`**：`cap = 2 * total_zeros` 这里 `total_zeros` 是
  **整串**的 0 的个数，不是窗口外部的 (外部 = 总 − 窗内，推导已把 "外部
  ≥ 1" 转成整串 $L \\le 2 \\cdot {\\rm total\\_zeros}$)。
- **L 必然是偶数**：因为 diff = $\\pm 2$ 时 $\\#1 + \\#0 = L$ 而 $\\#1 - \\#0$
  也是偶数 ($\\pm 2$)，所以两者同奇偶 $\\Rightarrow L$ 偶。$L/2$ 永远是整数，
  放心整除。
- **swap 是"最多一次"**：Case A (diff=0) 不需要做 swap 也可以算；代码里
  直接把 A 的结果并入最大值，不要额外条件。
- **swap 的两端不能都在窗内**：否则窗内 counts 不变，无效。但推导可行性
  时已默认"一端在内、一端在外"，无需再额外判断 — 只要可行性不等式满足，
  就一定能找到这样的配对 (鸽笼)。

### 相关题目
- **LC 525 Contiguous Array**：最长 0/1 数量相等的连续子数组 — 本题去掉
  "一次 swap" 的 0-swap 版本，就是 Case A 的纯粹形式。同一个 prefix-sum +
  first-occurrence-dict 骨架。
- **LC 560 Subarray Sum Equals K**：prefix-sum + hash-map 统计**数量**(而
  非最长长度) 的同族套路。
- **LC 1963 Minimum Number of Swaps to Make the String Balanced**：同样
  "swap 使平衡"，但针对括号串且要**全串平衡**，做法是 greedy 计 unmatched
  `]` 对，完全不同范式。
- **LC 1658 Minimum Operations to Reduce X to Zero** / **LC 1695 Maximum
  Erasure Value**：prefix-sum + 滑动窗口族，本题 bucket + binary-search
  是它们的变体。

### 面试应答 checklist
1. **澄清**：`'0'`/`'1'` 之外的字符？"swap" 是否仅限子串内 (否则 diff=0
   only) 还是全串任意 (本题)？"at most one" 还是 "exactly one"？
2. 先说 $O(N)$ prefix-sum 思路 + 把 diff 分三 case 的结构。
3. 写 bucket 骨架 + 可行性推导 (外部至少有一个反向字符 $\\Rightarrow$
   $L \\le 2 \\cdot {\\rm total\\_zeros/ones}$)。
4. 指出 bucket 线性扫描的退化 case，引入 **lower_bound 手写二分**把 worst
   case 降到 $O(N \\log N)$。面试官喜欢看到对 worst case 的主动识别。
5. 列举**易错点** (Case A 别二分；$L$ 偶；swap 端点约束已被鸽笼吸收)。
6. 把题目类比到 **LC 525** 基础版 + **LC 560** 计数版，展示 pattern 家族。
"""


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    now = datetime.now().isoformat(timespec="seconds")
    tags_json = json.dumps(TAGS, ensure_ascii=False)
    company_json = json.dumps(COMPANY_TAGS, ensure_ascii=False)

    warn_if_missing_family(LEETCODE_ID, TITLE, FAMILY_SLUG, Path(__file__).stem)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        existing = conn.execute(
            "SELECT id, title, notes FROM problems WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        ).fetchone()
        if existing:
            pid, old_title, old_notes = existing
            conn.execute(
                """
                UPDATE problems SET
                    title = ?,
                    url = ?,
                    difficulty = ?,
                    tags = ?,
                    pattern = ?,
                    category = ?,
                    source = ?,
                    company_tags = ?,
                    priority = 1,
                    is_completed = 1,
                    description = ?,
                    notes = ?,
                    family = ?
                WHERE id = ?
                """,
                (
                    TITLE, URL, DIFFICULTY, tags_json, PATTERN, CATEGORY,
                    SOURCE, company_json, DESCRIPTION, NOTES, FAMILY_SLUG, pid,
                ),
            )
            action = "UPDATE"
        else:
            conn.execute(
                """
                INSERT INTO problems (
                    leetcode_id, title, url, difficulty, tags, pattern, category,
                    source, company_tags, priority, is_completed, description,
                    notes, family, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?, ?, ?)
                """,
                (
                    LEETCODE_ID, TITLE, URL, DIFFICULTY, tags_json, PATTERN,
                    CATEGORY, SOURCE, company_json, DESCRIPTION, NOTES,
                    FAMILY_SLUG, now,
                ),
            )
            action = "INSERT"
        conn.commit()

        row = conn.execute(
            "SELECT id, leetcode_id, title, difficulty, length(description), "
            "length(notes), company_tags, family FROM problems WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        ).fetchone()
        print(f"[{action}] LC {row[1]} id={row[0]} title={row[2]!r} "
              f"difficulty={row[3]!r} |desc|={row[4]} |notes|={row[5]} "
              f"companies={row[6]} family={row[7]!r}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
