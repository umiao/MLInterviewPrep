"""One-shot: translate LC 465 solution notes to Chinese."""
import sqlite3

NOTES = r'''## LC 465 - Optimal Account Balancing (Bitmask DP on Zero-Sum Partitions)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/pinterest_recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 核心重述 (THE Key Insight)

这道题**不是**贪心式的 "settle debts" 问题。关键在于重新表述：

1. 对每个人计算 net balance；把 net = 0 的人直接丢弃（与结果无关）。
2. 设 `n = 非零 balance 的人数`。对任意一个 zero-sum 的集合，总能在 `n-1` 步内结清（链式转账）。
3. **核心洞察**：任意一个大小为 `k` 的 zero-sum 子集都能在 `k-1` 次转账内内部结清。如果能把 `n` 个人划分成 `K` 个互不相交的 zero-sum 子集，总转账次数 = `n - K`。
4. 因此：**最小化转账次数 = 最大化 K** = 覆盖所有非零 balance 的互不相交 zero-sum 子集的最大个数。

**答案 = n - max(K)**。

### Approach A: Bitmask DP (你的写法，小 n 下最优)

题目约束 `n <= 12`，bitmask DP 可行。

- `subset_sum[mask]` = `mask` 中 set bit 对应 balance 之和。用 low-bit 技巧 O(2^n) 预处理。
- `dp[mask]` = 把 `mask` 划分成 zero-sum 子集的最大个数；`dp[0] = 0`，不可达时 `dp[mask] = -1`。
- 转移：枚举 `mask` 的 submask `sub`，若 `subset_sum[sub] == 0` 且 `dp[mask ^ sub]` 可达，则 `dp[mask] = max(dp[mask], 1 + dp[mask ^ sub])`。
- 答案：`n - dp[(1<<n) - 1]`。

**复杂度**：submask 枚举是 O(3^n)，因为每个元素属于 {sub 内, mask\sub 内, mask 外} 三种状态之一。n=12 大约 530K 次操作，足够快。

### 标准代码 (Polished Code)

```python
from collections import defaultdict

class Solution:
    def minTransfers(self, transactions: list[list[int]]) -> int:
        net = defaultdict(int)
        for src, dst, val in transactions:
            net[src] += val
            net[dst] -= val
        balances = [v for v in net.values() if v != 0]
        n = len(balances)
        if n == 0:
            return 0

        # Precompute subset sums
        subset_sum = [0] * (1 << n)
        for mask in range(1, 1 << n):
            low = mask & -mask
            idx = low.bit_length() - 1
            subset_sum[mask] = subset_sum[mask ^ low] + balances[idx]

        # dp[mask] = max # of zero-sum partitions of `mask`; -1 if unreachable
        dp = [-1] * (1 << n)
        dp[0] = 0
        for mask in range(1, 1 << n):
            if subset_sum[mask] != 0:
                continue
            sub = mask
            while sub > 0:
                if subset_sum[sub] == 0 and dp[mask ^ sub] >= 0:
                    dp[mask] = max(dp[mask], 1 + dp[mask ^ sub])
                sub = (sub - 1) & mask

        return n - dp[(1 << n) - 1]
```

**对原始写法的 code review**：
- `self.ans = float('inf')` —— 未使用，删掉。
- 用 `float('-inf')` 表示不可达 —— 换成 `-1` 配合 `>= 0` 判断更清晰（逻辑等价，少一点 magic）。
- 缺 `n == 0` 保护（虽然空 balances 会返回 `n - dp[0] = 0`，能 work，但显式更稳）。
- `balanceList` → `balances`（PEP8）。
- 算法本身正确而干净。`i & -i` 取最低位 + `bit_length() - 1` 取下标是 idiomatic 的位运算写法。

### Approach B: Naive Backtracking DFS (更朴素的写法，也是正确性证明的入口)

```python
def minTransfers(self, transactions):
    net = defaultdict(int)
    for s, d, v in transactions:
        net[s] += v; net[d] -= v
    balances = [v for v in net.values() if v != 0]

    def dfs(i: int) -> int:
        while i < len(balances) and balances[i] == 0:
            i += 1
        if i == len(balances):
            return 0
        best = float('inf')
        for j in range(i + 1, len(balances)):
            # Only transfer to opposite sign -- same sign cannot zero out i in one move
            if balances[j] * balances[i] < 0:
                balances[j] += balances[i]   # full transfer from i to j
                best = min(best, 1 + dfs(i + 1))
                balances[j] -= balances[i]   # undo
        return best

    return dfs(0)
```

**Time**: 最坏 O(n!)，实际剪枝很强；n<=12 完全够用。

### 正确性问题 (Correctness Question)

> "遍历两个符号相反的人，把第一个从第二个结清。正确性不直观 —— 是否需要证明被跳过的元素要么使子和非零（配对失败），要么子和为零（无须考虑）？"

**简短回答**：是，有两个非 trivial 的事实需要证，但它们可以归到同一个 lemma 下。

**Lemma (Full-Transfer Optimality)**：存在**某个**最优解，使得每一次转账都让至少一个端点的 balance 归零。换言之，可以把搜索空间限制为 "i 把自己全部余额转给 j" 的那种转账。

**证明思路**：假设某最优方案包含一次 partial transfer A -> B 且金额 `x < |balance(A)|`。那 A 之后仍非零，必然还会参与后续的转账。通过 swap argument 重排/合并这些转账，可以让其中至少一次完全结清某个端点，同时不增加总次数。对 partial transfer 的个数归纳即可。

**为什么只看相反符号？**
- i 的 balance 为 b_i != 0。要在 one transaction 内归零 i，counterparty j 必须符号相反（把 |b_i| 从 i 转给 j，或反向）。
- 如果 j 与 i 同号，这次转账要么让 i 仍非零（partial 或方向错），由 lemma 可以避开。

**为什么 j > i 而不是 j < i？**
- 循环不变式：进入 `dfs(i)` 时，所有 `< i` 的下标已经归零（要么本来就是 0，要么在前面的分支里被结清）。
- 所以非零候选只能在 `>= i` 的下标上。我们选 i 本身（当前最小的非零下标）作为 "giver"，j > i 作为 "receiver"。

**"被跳过元素" 的顾虑**：
- 其实没有哪个元素被真正 "跳过"。每个非零元素最终都必须被归零。
- 如果在 `dfs(i+1)` 时某个更后的下标 k 仍非零，递归会继续处理 k。
- "谁和谁配对" 的不同顺序对应 DFS 的不同分支。我们枚举所有 j > i 且符号相反的候选，等于枚举了 "i 的第一个配对对象" 的所有可能。

**与 Approach A 的对偶**：DFS 其实隐式地在枚举 partition。Approach A 把它显式化成 `dp[mask]` —— 两者是同一个组合结构（把非零 balance 划分成 zero-sum 子集）的两个视角。

### Traps & Gotchas

1. **不要把 zero-balance 的人包含进来**：会稀释集合大小，2^n 爆炸。
2. **transactions 自环**：`src == dst` 且 val != 0 —— 对 net 贡献为 0，没影响，但入口做一下 sanity check 更稳。
3. **n 可能很小 (=0, =1)**：n=0 → 0 次转账；n=1 不可能（所有 balance 之和为 0，不可能只剩一个非零）。防御性写法：`n == 0` 时返回 0。
4. **Bitmask DP 的 n<=20 上限**：2^20 = 1M 状态，3^20 = 3.5B 转移 —— 太慢。本题 n<=12 安全。

### 面试模式识别 (Pattern Recognition)

看到 "minimize transactions"、"settle debts"、"split bills" + "人数很少"（约束暗示 n <= 12~20）的组合，立刻想到 **Bitmask DP on zero-sum partitions**。

通用套路："最小化/最大化 K 个满足性质 P 的部分" + 小 n → 枚举满足 P 的 mask，在 submask 上做 partition DP。

相关题目：LC 698 (Partition to K Equal Sum Subsets)、LC 473 (Matchsticks to Square) —— 同一个 "zero-sum / equal-sum submask partition" 骨架。

### Complexity Summary

| Approach | Time | Space |
|----------|------|-------|
| Backtracking DFS | O(n!) 最坏，剪枝强 | O(n) recursion |
| Bitmask DP | O(3^n) | O(2^n) |
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 465", (NOTES,))
conn.commit()
print(f"[OK] LC 465 notes updated ({len(NOTES)} chars)")
conn.close()
