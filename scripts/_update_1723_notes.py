"""One-shot: write LC 1723 solution notes in Chinese."""
import sqlite3

NOTES = r'''## LC 1723 - Find Minimum Time to Finish All Jobs (二分 + 回溯 / 状压 DP)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 核心重述 (THE Key Insight)

有 `n` 个工作（时长 `jobs[i]`）和 `k` 个工人。每个工作必须整块分给某个工人，工人总时间 = 分到的所有工作时长之和。要**最小化所有工人中的最大工作时间**（最大工作时间即 makespan）。约束：`1 <= k <= n <= 12`，`jobs[i] <= 1e7`。

**核心洞察**：
- **`n ≤ 12`** 是强信号：`O(n·2^n·k)` 的状压 DP 或指数级回溯都能过。
- 最优 makespan 一定 `∈ [max(jobs), sum(jobs)]`。→ **二分答案 + 可行性回溯**是面试里最容易讲清的解。
- 工人是**同质的（interchangeable）**：分配时"第一个空工人"的选择互换等价，需要剪枝避免对称重复枚举。

### Approach A: 二分答案 + 回溯可行性 (推荐面试首选)

二分最大工时 `limit`。判定：能否把 `n` 个工作分给 `k` 个工人，每个工人负载 `≤ limit`。回溯每次尝试把当前工作塞给某个现有工人（若其 `load + job ≤ limit`）。

```python
def minimumTimeRequired(jobs: list[int], k: int) -> int:
    jobs.sort(reverse=True)  # 关键剪枝 1：大工作先放，快速失败
    n = len(jobs)

    def can(limit: int) -> bool:
        loads = [0] * k

        def dfs(i: int) -> bool:
            if i == n:
                return True
            seen = set()  # 关键剪枝 2：同一层同负载的工人只试一次
            for w in range(k):
                if loads[w] in seen:
                    continue
                if loads[w] + jobs[i] > limit:
                    continue
                seen.add(loads[w])
                loads[w] += jobs[i]
                if dfs(i + 1):
                    return True
                loads[w] -= jobs[i]
                # 关键剪枝 3：如果当前工人放完这一个工作后撤回失败，
                # 且撤回后 loads[w] == 0（即这是他的第一单），
                # 说明后面让别的空工人来接也一样会失败 -> 剪掉整层
                if loads[w] == 0:
                    break
            return False

        return dfs(0)

    lo, hi = max(jobs), sum(jobs)
    while lo < hi:
        mid = (lo + hi) // 2
        if can(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**复杂度**：二分 O(log(sum-max))，每次可行性最坏 O(k^n)，但三条剪枝（降序 + seen 去重 + 空工人 break）实测极快。`n=12, k=12` 大约 ms 级。

**三条剪枝为什么重要**：
1. **`jobs.sort(reverse=True)`**：大工作先放，如果放不下能立刻回溯；小工作先放会等整棵子树走完才发现失败。
2. **`seen` 去重**：同一递归层里，如果两个工人当前负载相同，把 `jobs[i]` 放给谁完全等价，只试一次。这是对"工人可互换"对称性的直接剪枝。
3. **"空工人 break"**：若 `loads[w]` 从 0 变 `jobs[i]` 后 `dfs(i+1)` 返回失败，说明"把 `jobs[i]` 作为某个工人第一单"这条路整体失败，换别的空工人来也一样 → 直接 `break` 退出当前层循环。

### Approach B: 状压 DP (Subset Sum on Bitmask)

令 `sub[mask]` = 位掩码 `mask` 指定的工作集合的总耗时。`dp[i][mask]` = 用前 `i` 个工人覆盖 `mask` 所有工作时，最小的 makespan。转移：
- 枚举 `mask` 的**子集** `sub`（分给第 `i` 个工人的工作集合）。
- `dp[i][mask] = min over sub of max(dp[i-1][mask ^ sub], sum[sub])`。

```python
def minimumTimeRequired(jobs: list[int], k: int) -> int:
    n = len(jobs)
    full = 1 << n
    tot = [0] * full
    for mask in range(1, full):
        low = mask & -mask
        tot[mask] = tot[mask ^ low] + jobs[low.bit_length() - 1]

    dp = tot[:]  # k=1 时就是自己
    for _ in range(1, k):
        nxt = [float('inf')] * full
        for mask in range(full):
            sub = mask
            while sub > 0:
                nxt[mask] = min(nxt[mask], max(dp[mask ^ sub], tot[sub]))
                sub = (sub - 1) & mask
            nxt[mask] = min(nxt[mask], dp[mask])  # 允许这个工人空跑
        dp = nxt
    return dp[full - 1]
```

**复杂度**：子集枚举 `Σ_{mask} 2^popcount(mask) = 3^n`，总共 `O(k · 3^n)`，`n=12, k=12` 约 `12·531441 ≈ 6.4M` 操作，稳过。

**关键点**：
- `tot[mask]` 预处理用 lowbit 递推：`tot[mask] = tot[mask ^ lowbit] + jobs[lowbit_index]`。
- **枚举子集的标准写法**：`sub = mask; while sub > 0: ... ; sub = (sub - 1) & mask`。这枚举 `mask` 所有非空子集，复杂度 `2^popcount(mask)`。
- 允许某个工人空跑（`nxt[mask] = min(nxt[mask], dp[mask])`），否则 `k > 有效分组数`时会漏解。

### Approach C: 简单回溯（不二分，直接搜最优）

直接维护 `loads[]`，每次把当前工作尝试分给每个工人，记全局最小 `max(loads)`。带上同样的剪枝。代码最短，但无二分的上界指导，剪枝稍差。可以作为 warm-up 说 "先写 brute 再优化"。

### Code Review 要点 (常见失误)

- **`jobs` 必须降序排**：升序排同样正确，但剪枝效率差一个数量级。
- **`seen` 要在每一层新建**，不是全局的。它只针对"同一层、同负载工人等价"去重。
- **二分上界 `sum(jobs)`, 下界 `max(jobs)`**：下界不能是 0（任何单个工作必须由某工人独扛），否则可行性判定会错判。
- **状压 DP 枚举子集**：`sub = (sub - 1) & mask` 的 `-1` 会把最低位翻掉然后 `& mask` 截回合法位，这是 O(3^n) 子集枚举的黄金模板，要能默写。
- **空工人对称性**：如果不加 "第一单失败就 break" 的剪枝，纯回溯 `n=12, k=12` 会 TLE。
- **二分判定内不要修改 `jobs`**：`loads` 要每次重置，别在判定之间残留。
- **工人同质对称剪枝写错**：有人写 `if loads[w] == loads[w-1] and loads[w-1] == 0: continue`，只覆盖了空工人的情况，漏掉"两个工人都非空但恰好相等"的场景。正确写法是 `seen` 集合。

### 识别模板 (When to Use This Pattern)

- **`n ≤ 12~20` + "分组 / 划分 / 分配"**：优先考虑状压 DP 或带剪枝回溯。
- **"最小化最大值"或"最大化最小值"**：二分答案 + 可行性判定是首选框架。
- **同族题目**：
  - LC 698 Partition to K Equal Sum Subsets（k 个**相等**子集，本题退化版）
  - LC 473 Matchsticks to Square（k=4 的 LC 698）
  - LC 410 Split Array Largest Sum（顺序分割，不是任意分配，单调前缀 + 二分）
  - LC 2305 Fair Distribution of Cookies（完全同构）
  - LC 1986 Minimum Number of Work Sessions（状压 DP 分组）

### 面试叙述模板 (Talking Points)

1. "看到 `n ≤ 12`，直接想到状压或回溯；看到'最小化最大值'就再叠一个二分答案。"
2. "我的首选是**二分答案 + 回溯可行性**：二分 makespan 上限 `limit`，判定能否把工作分给 k 个工人且每人 `≤ limit`。"
3. "三条剪枝：(1) `jobs` 降序，大工作先失败；(2) 同一层 `seen` 去重工人对称；(3) 空工人尝试失败就 `break`，剪掉整棵等价子树。"
4. "二分下界 `max(jobs)`（任何单工作必须放进某人）、上界 `sum(jobs)`（一个人扛全部）。"
5. "如果面试官想要更确定性的复杂度，可以改状压 DP：`dp[i][mask]` = 前 i 个工人覆盖 mask，转移枚举 mask 的子集当作第 i 个工人的任务集合，`O(k·3^n)`。"
6. "区别 LC 410：那题工作**顺序不可打乱**，所以是前缀分割 + 二分；本题工作可任意分配，所以要回溯或状压。"

### 为什么不用贪心 / LPT

- **LPT（Longest Processing Time first，把最大 job 分给当前最轻的工人）** 是 4/3 近似，非精确解。本题要**最优解**，只能搜索或 DP。
- 但 LPT 可以作为**二分初始上界的一个更紧的估计**，提前缩小搜索空间。面试时可以提一嘴作为"工业实践中当 n 很大怎么办"。

### Complexity Summary

| Approach | Time | Space | 适用 n |
|----------|------|-------|--------|
| 二分 + 回溯 + 剪枝 (A) | 最坏 O(log S · k^n)，实测 ms 级 | O(k + n) | n ≤ 12 稳过，n ≤ 20 靠剪枝 |
| 状压 DP (B) | O(k · 3^n) | O(2^n) | n ≤ 15 稳过 |
| 朴素回溯 (C) | O(k^n) | O(n) | n ≤ 10 |

LC 1723 官解两条都展示，面试首选 A（更能讲清剪枝的思考过程），有时间再补 B 作为"确定性复杂度的替代方案"。
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 1723", (NOTES,))
conn.commit()
cur = conn.execute("SELECT length(notes) FROM problems WHERE leetcode_id = 1723")
print(f"[OK] LC 1723 notes updated ({cur.fetchone()[0]} chars)")
conn.close()
