# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot: write LC 410 solution notes in Chinese."""
import sqlite3

NOTES = r'''## LC 410 - Split Array Largest Sum (Binary Search on Answer)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 核心重述 (THE Key Insight)

把非负数组切成 `k` 段 (连续)，最小化各段 sum 的最大值。核心洞察：

1. **把"最优化"问题转成"可行性"问题**：固定阈值 `cap`，问"能否把数组切成 ≤ k 段，且每段和 ≤ cap？" —— 这是一个可以 O(n) 贪心判定的 feasibility check。
2. **单调性**：若 `cap` 可行，`cap + 1` 也一定可行（更宽松）。→ 可行集合是右闭区间 `[ans, +∞)`。
3. 所以可以在答案域 `[max(nums), sum(nums)]` 上二分，找最小的可行 cap。

- 下界 = `max(nums)`：至少要装得下最大的单个元素（否则该元素自己就超 cap）。
- 上界 = `sum(nums)`：全部塞一段，一定可行。

### Approach A: Binary Search on Answer (推荐，O(n log S))

```python
class Solution:
    def splitArray(self, nums: list[int], k: int) -> int:
        def feasible(cap: int) -> bool:
            # 贪心：每段尽量塞，装不下就开新段
            segs, cur = 1, 0
            for x in nums:
                if cur + x > cap:
                    segs += 1
                    cur = x
                    if segs > k:
                        return False
                else:
                    cur += x
            return True

        lo, hi = max(nums), sum(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if feasible(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
```

**复杂度**：时间 O(n · log(sum - max))；空间 O(1)。n = 1000、sum ≤ 1e9，约 30 轮二分 × 1000 次遍历 = 3e4 次操作，极快。

**为何贪心 feasibility 正确**：给定 cap，任意合法切法都能被"从左到右尽量塞"策略不劣地模仿 —— 贪心在每个位置做的决定（能装就装）不会让后续更难完成。严格证明：交换论证 (exchange argument)。

### Approach B: DP on (i, k) (O(n^2 k)，理论完整但 n=1000 下偏慢)

`dp[i][j]` = 把 `nums[:i]` 切成 `j` 段的最小最大段和。

- 转移：`dp[i][j] = min over split p in [j-1..i-1] of max(dp[p][j-1], sum(nums[p:i]))`
- 初值：`dp[i][1] = prefix[i]`
- 答案：`dp[n][k]`

```python
def splitArrayDP(self, nums, k):
    n = len(nums)
    prefix = [0] * (n + 1)
    for i, x in enumerate(nums):
        prefix[i + 1] = prefix[i] + x
    INF = float('inf')
    dp = [[INF] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            for p in range(j - 1, i):
                dp[i][j] = min(dp[i][j], max(dp[p][j - 1], prefix[i] - prefix[p]))
    return dp[n][k]
```

**复杂度**：O(n^2 k)，n=1000、k=50 → 5e7，Python 会吃紧；C++ 没问题。面试首选仍是二分 —— 代码更短、常数更小、边界更好讲。

### Code Review 要点 (常见失误)

- **下界写成 0** 或者 `max(nums)` 漏写：如果 `cap < max(nums)`，feasible 会死循环（cur 永远 > cap），所以 `lo = max(nums)` 既是正确性需求也是终止性需求。
- **贪心里 `segs > k` 提前返回**：省去剩余遍历；记得是 `>`，不是 `>=`。
- **溢出**：Python 无需担心；C++/Java 用 `long long` 保存 cap 和 cur。
- **nums 为空 / k=1 / k=n**：`k=1` 返回 `sum(nums)`；`k=n` 返回 `max(nums)`；都被二分区间自然覆盖。
- **相同 signature 的 off-by-one**：`while lo < hi` + `hi = mid` / `lo = mid + 1` 是经典"找最小可行"模板，不要写成 `<=` 或 `hi = mid - 1`。

### 识别模板 (When to Use Binary-Search-on-Answer)

触发词组合：

1. "最小化最大值" / "最大化最小值" (minimax / maximin)。
2. 答案定义域有明显的上下界，且答案具有**单调可行性**（小的可行则大的可行，或反之）。
3. 可以设计一个 O(n) 或 O(n log n) 的 feasibility check。

见到这三点就默认尝试二分答案。

### 相关题目 (Pattern Family)

| 题目 | 最小化/最大化 | feasibility check |
|------|---------------|-------------------|
| LC 410 Split Array Largest Sum | 最小化最大段和 | 贪心切段，段数 ≤ k |
| LC 1011 Capacity To Ship Packages | 最小化运载能力 | 贪心装船，天数 ≤ D |
| LC 1760 Minimum Limit of Balls in a Bag | 最小化最大袋球数 | `sum(ceil(a/cap) - 1) ≤ maxOps` |
| LC 875 Koko Eating Bananas | 最小化吃速 | `sum(ceil(pile/k)) ≤ h` |
| LC 1482 Min Days to Make m Bouquets | 最小化天数 | 连续 open 花数贪心 |

这些是**同一个骨架**：答案域二分 + 单遍 feasibility。能独立写出 410 就解锁了这一整族。

### Complexity Summary

| Approach | Time | Space |
|----------|------|-------|
| Binary Search on Answer | O(n log S), S = sum - max | O(1) |
| DP on (i, k) | O(n^2 k) | O(nk) |
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 410", (NOTES,))
conn.commit()
print(f"[OK] LC 410 notes updated ({len(NOTES)} chars)")
conn.close()
