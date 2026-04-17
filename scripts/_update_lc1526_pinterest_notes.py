"""One-shot: add Pinterest tag + Chinese notes for LC 1526 (Min Increments on Subarrays).

T-P1-393 deliverable.
"""
import json
import sqlite3

DB_PATH = "data/mle_prep.db"

NOTES = r"""## LC 1526 - Minimum Number of Increments on Subarrays to Form a Target Array (差分贪心 / 上升沿计数)

> Pinterest must-do list (2025-11 cutoff). See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾
给定长度为 n 的非负数组 `target`。从全 0 数组出发，每次操作选一个**子数组** `[l..r]`，把其中**每个元素 +1**。问至少多少次操作才能得到 `target`。`1 <= n <= 1e5`，`1 <= target[i] <= 1e5`。

与 LC 3229 的区别：本题只允许 **+1**，且起点固定为全 0；LC 3229 允许 +1/-1 且起点任意。

### 核心思路：上升沿计数 (O(n) 一遍扫)

把 `target` 想成一条山峦折线，从左向右看：每个"**上升沿**"都对应一次**新开启**的区间加操作；下降或持平可以**复用**之前尚未结束的操作。

> **关键公式**：`ans = target[0] + sum(max(0, target[i] - target[i-1]) for i >= 1)`
>
> 等价地：把 `target[-1]` 视作 0（段外），则 `ans = sum(max(0, t[i] - t[i-1]))`。

```python
def minNumberOperations(target: list[int]) -> int:
    ans = target[0]
    for i in range(1, len(target)):
        if target[i] > target[i - 1]:
            ans += target[i] - target[i - 1]
    return ans
```

**时间 O(n)，空间 O(1)**。

### 为什么这样算是对的（正确性论证）

**差分视角**：令 `d[i] = target[i] - target[i-1]`（`d[0] = target[0]`，即前面补 0）。一次区间 `[l..r] +1` 操作在 `d` 中贡献 `d[l] += 1, d[r+1] -= 1`——也就是说，**每次操作恰好制造一个 +1 的上升和一个 -1 的下降**。

为了把全 0 变成 `target`，正差 `d[i] > 0` 的总量必须 = `sum(max(0, d[i]))`。每次操作只能提供 1 个 +1 的上升，所以**操作次数下界 = sum(max(0, d[i]))**。

**可达性**：从右向左处理每个"正上升沿"，总能找一个区间把上升沿对应的那部分抬起来（贪心构造），因此下界可达。最终：

`ans = sum(max(0, d[i])) = target[0] + sum(max(0, target[i] - target[i-1]))`。

### 示例追踪

`target = [1, 2, 3, 2, 1]`：
- 初始 `ans = 1`（第一位的上升沿）
- i=1: 2-1=1 > 0, ans += 1 -> 2
- i=2: 3-2=1 > 0, ans += 1 -> 3
- i=3: 2-3=-1, 跳过
- i=4: 1-2=-1, 跳过
- **Total = 3**（对应三次操作：[0..4]+1, [1..3]+1, [2..2]+1）

`target = [3, 1, 1, 2]`：
- ans = 3
- i=1: 1-3=-2, 跳过
- i=2: 1-1=0, 跳过
- i=3: 2-1=1, ans += 1 -> 4
- **Total = 4**（操作：[0..3]+1, [0..0]+1, [0..0]+1, [3..3]+1）

### 相关题 / 套路迁移

| 题号 | 题意 | 关键连接 |
|------|------|----------|
| **LC 3229** Min Operations to Make Array Equal to Target | 允许 ±1、起点任意 | 本题的超集：`ans = LC1526(max(d,0)) + LC1526(max(-d,0))` |
| **LC 370** Range Addition | 多次区间加，求最终数组 | 差分正向用法 |
| **LC 1109** Corporate Flight Bookings | 多个区间加 | 差分 + 前缀和 |
| **LC 798** Smallest Rotation | 差分 + 扫描线 | 区间贡献法 |
| **LC 2772** Apply Operations to Make All Equal to Zero | 区间减法、判可行 | 差分贪心消除 |
| **LC 1564** Put Boxes Into Warehouse I | 贪心区间分配 | Pinterest 同批次"区间贪心" |

### 套路识别：什么时候想到"差分贪心 / 上升沿计数"？

1. 操作是"**区间同步 +c**"且**目标数组给定**，问**最少操作数**。
2. 起点是全 0（或可归一化到全 0）。
3. 关键思考步骤：
   - 写差分 `d[i] = t[i] - t[i-1]`；
   - 每次区间操作恰好提供 1 个 +1 上升，所以答案 = 正差之和；
   - 化简为 `t[0] + sum(max(0, t[i]-t[i-1]))`。

### 陷阱与边界

1. **第一位别漏**：`ans` 初始化为 `target[0]`，相当于在数组前面补 0。新手常写成 `ans = 0` 然后从 i=1 扫，结果少算 `target[0]`。
2. **单调递减**：`target = [5, 3, 1]`，答案是 5（只需 [0..2]+1 做 3 次、[0..1]+1 做 2 次）。代码：5 + 0 + 0 = 5，正确。
3. **单调递增**：`target = [1, 2, 3]`，答案是 3（等于 `target[-1]`）。代码：1 + 1 + 1 = 3，正确。
4. **平原**：`target = [4, 4, 4]`，答案是 4。代码：4 + 0 + 0 = 4，正确。
5. **山峰再起**：`target = [3, 1, 4]`，答案 = 3 + 0 + 3 = 6（两个独立峰顶）。
6. **全 0**：题目约束 `target[i] >= 1`，不会出现；但如果出现 `target = [0,...]`，答案是 0。

### 复杂度总结

| 方法 | 时间 | 空间 |
|------|------|------|
| 差分/上升沿（单次扫描） | O(n) | O(1) |

### 45 秒口播脚本（面试开头）

> "每次操作就是把差分数组上某个位置 +1、某个位置 -1。要把全 0 变成 `target`，正差总量 = 最少操作数。正差之和可以化简成 `target[0] + sum(max(0, target[i] - target[i-1]))`，也就是'每个上升沿都新开一次操作'。单调递减段复用之前的区间、单调递增段需要新开。O(n) 一遍扫完。这题是 LC 3229 的'单边版'，3229 答案等于 `LC1526(max(d,0)) + LC1526(max(-d,0))`。"
"""


def main() -> None:
    """Tag LC 1526 with Pinterest and update notes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, company_tags FROM problems WHERE leetcode_id = 1526")
    row = c.fetchone()
    if not row:
        print("[ERR] LC 1526 not found")
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
    print(f"[OK] LC 1526 (id={pid}) updated. Pinterest tag added: {changed_tag}. Tags: {tags}. Notes len: {len(NOTES)}")
    conn.close()


if __name__ == "__main__":
    main()
