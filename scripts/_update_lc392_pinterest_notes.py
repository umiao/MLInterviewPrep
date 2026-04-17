"""One-shot: add Pinterest tag + Chinese notes for LC 392 (Is Subsequence).

T-P1-391 deliverable.
"""
import json
import sqlite3

DB_PATH = "data/mle_prep.db"

NOTES = r"""## LC 392 - Is Subsequence (双指针 / 多查询预处理)

> Pinterest must-do list (2025-11 cutoff). See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾
给定字符串 `s` 与 `t`，判断 `s` 是否为 `t` 的子序列（保持相对顺序，允许中间跳过任意字符）。`len(s) <= 100`, `len(t) <= 10^4`。

**Follow-up**：若有**海量查询** `s_1, s_2, ..., s_k`（k 可达 10^9）都要判断是否为同一个 `t` 的子序列，如何做？

### 方法一：双指针 O(n + m) 标准解

```python
def isSubsequence(s: str, t: str) -> bool:
    i, j = 0, 0
    n, m = len(s), len(t)
    while i < n and j < m:
        if s[i] == t[j]:
            i += 1
        j += 1
    return i == n
```

**关键点**：
- `i` 指向 `s` 当前要匹配的字符，`j` 在 `t` 上从左到右扫描。
- 每次 `t[j]` 与 `s[i]` 相等就把 `i` 前进一位；无论是否相等 `j` 都前进。
- 结束条件：`i == n` 说明 `s` 全部匹配完；否则 `j` 先走到头，不是子序列。
- 时间 O(n + m)，空间 O(1)。

**为什么贪心一定最优**：遇到相同字符时立刻匹配不会错过更优方案。假设存在更优匹配把某个 `s[i]` 对应到更靠后的 `t[j']`，那么把它提前到当前 `j` 只会让后续可选范围更大，不可能变差。这是**贪心匹配成立**的标准论证。

### 方法二：预处理字符位置 + 二分（多查询 follow-up）

若 `t` 固定、有 k 个 `s` 查询，每次都 O(m) 扫一遍 `t` 总共 O(k*m) 不可行。**预处理 `t` 中每个字符的下标列表**，查询时对每个 `s[i]` 做二分：

```python
from bisect import bisect_left
from collections import defaultdict

class SubsequenceChecker:
    def __init__(self, t: str):
        self.pos: dict[str, list[int]] = defaultdict(list)
        for j, ch in enumerate(t):
            self.pos[ch].append(j)

    def is_subseq(self, s: str) -> bool:
        prev = -1  # 上一次在 t 里匹配到的下标
        for ch in s:
            lst = self.pos.get(ch)
            if not lst:
                return False
            # 在 lst 中找第一个 > prev 的下标
            k = bisect_left(lst, prev + 1)
            if k == len(lst):
                return False
            prev = lst[k]
        return True
```

- **预处理**：O(m)，空间 O(m)（每个 `t[j]` 放进 `pos[t[j]]` 一次）。
- **单次查询**：O(n log m)，其中 n = `len(s)`。
- 对 k 次查询总成本：O(m + k * n log m)。

**技巧**：`lst` 本来就是升序（按 `j` 顺序插入），所以能直接二分；无需额外排序。

### 方法三：DP 预处理 `next[j][c]` —— `t` 上"下一个字符 c"的位置

比方法二的常数更小、查询 O(n)，但空间 O(m * 26)：

```python
def preprocess(t: str) -> list[list[int]]:
    m = len(t)
    nxt = [[m] * 26 for _ in range(m + 1)]  # nxt[j][c] = j 及之后第一个 c 的下标
    for j in range(m - 1, -1, -1):
        for c in range(26):
            nxt[j][c] = nxt[j + 1][c]
        nxt[j][ord(t[j]) - ord('a')] = j
    return nxt

def is_subseq(s: str, nxt: list[list[int]]) -> bool:
    j = 0
    m = len(nxt) - 1
    for ch in s:
        j = nxt[j][ord(ch) - ord('a')]
        if j == m:
            return False
        j += 1
    return True
```

- **预处理**：O(m * 26) 时间 / 空间。
- **单次查询**：严格 O(n)。
- 总成本：O(m * 26 + k * n)。字符集固定且 k 很大（e.g. k >> log m）时优于方法二。

### 方法选择对照表

| 场景 | 最佳方法 | 总复杂度 |
|------|---------|----------|
| 单次查询 | 方法一（双指针） | O(n + m) |
| k 次查询、k 中等、字符集大 | 方法二（二分） | O(m + k * n log m) |
| k 次查询、k 很大、字符集小（26/ASCII） | 方法三（next DP） | O(m * 26 + k * n) |

### 相关题 / 套路迁移

| 题号 | 题意 | 关键连接 |
|------|------|----------|
| **LC 1055** Shortest Way to Form String | 用 `source` 的子序列最少拼几次才能拼出 `target` | 每轮跑一次 LC 392 的贪心，或用方法三的 `next` 数组 O(\|source\|*26 + \|target\|) |
| **LC 524** Longest Word by Deleting | 字典中能由 s 删字母得到的最长词 | 每个候选词跑一次 LC 392 |
| **LC 792** Number of Matching Subsequences | 一个 `s`，一堆 word 查询是否为子序列 | **方法二/三正是标准解**；或按首字母桶化（bucket by next char） |
| **LC 115** Distinct Subsequences | 子序列**计数** | DP：`dp[i][j] = dp[i-1][j-1] * (s[i]==t[j]) + dp[i-1][j]` |
| **LC 1143** LCS | 最长公共子序列 | 子序列家族的 DP 起点，O(nm) |

### 套路识别：什么时候想到双指针贪心？

1. 问题是"**保序匹配**"：把 `s` 嵌进 `t`、两个有序数组求交、双数组归并等。
2. 单向扫描 + "相等前进一步" 的结构。
3. 若题目加一句"**多查询 / 离线处理 / t 固定**"，立刻切换到方法二（二分）或方法三（next-DP）。

### 陷阱与边界

1. **空 `s`**：任何字符串的子序列都包含空串，返回 `True`。方法一因 `i == n == 0` 初始即满足，天然正确。
2. **空 `t` 且 `s` 非空**：`j` 立即越界，`i < n`，返回 `False`。正确。
3. **大小写/Unicode**：方法三的 26 桶只对小写字母；题面保证 `s, t` 都是英文小写。如果题面放开，改用方法二的 `dict`。
4. **方法二二分的 off-by-one**：找的是 `> prev` 的第一个，写 `bisect_left(lst, prev + 1)` 或 `bisect_right(lst, prev)` 都对；混用写成 `bisect_left(lst, prev)` 会**把 prev 本身也算进来**（重复匹配同一个字符位置），错。
5. **方法三的初始化**：`nxt[m][*] = m` 是"哨兵/越界"，表示再也找不到；查询里用 `j == m` 判失败。

### 复杂度总结

| 方法 | 预处理 | 单查询 | 空间 |
|------|--------|--------|------|
| 双指针 | — | O(n + m) | O(1) |
| 位置表 + 二分 | O(m) | O(n log m) | O(m) |
| next-DP | O(m * 26) | O(n) | O(m * 26) |

### 45 秒口播脚本（面试开头）

> "单次判断直接双指针：`i` 扫 `s`，`j` 扫 `t`，相等就把 `i` 前进。`i` 走到末尾就是子序列。贪心成立是因为早匹配只会让后面可选范围更大。Follow-up 如果是海量查询同一个 `t`，我会预处理：字符集小用 `next[j][c]` 表 O(n) 查询，字符集大用每个字符的下标列表 + 二分 O(n log m)。时间从朴素 O(k*m) 降到 O(k*n) 或 O(k*n log m)。"
"""


def main() -> None:
    """Tag LC 392 with Pinterest and update notes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, company_tags FROM problems WHERE leetcode_id = 392")
    row = c.fetchone()
    if not row:
        print("[ERR] LC 392 not found")
        return
    pid, existing = row
    tags = json.loads(existing) if existing else []
    changed_tag = False
    if "Pinterest" not in tags:
        tags.append("Pinterest")
        changed_tag = True
    c.execute(
        "UPDATE problems SET company_tags = ?, notes = ? WHERE id = ?",
        (json.dumps(tags, ensure_ascii=False), NOTES, pid),
    )
    conn.commit()
    print(f"[OK] LC 392 (id={pid}) updated. Pinterest tag added: {changed_tag}. Notes len: {len(NOTES)}")
    conn.close()


if __name__ == "__main__":
    main()
