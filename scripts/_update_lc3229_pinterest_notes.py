"""One-shot: add Pinterest tag + Chinese notes for LC 3229 (Min Operations to Make Array Equal to Target).

T-P1-392 deliverable.
"""
import json
import sqlite3

DB_PATH = "data/mle_prep.db"

NOTES = r"""## LC 3229 - Min Operations to Make Array Equal to Target (差分贪心)

> Pinterest must-do list (2025-11 cutoff). See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾
给定两个长度为 n 的数组 `nums` 与 `target`。每次操作可以选一个**子数组** `nums[l..r]`，对里面所有元素**同时 +1 或 -1**。返回把 `nums` 变成 `target` 所需的**最少操作数**。`1 <= n <= 1e5`，数值范围可能含负数。

与 LC 1526 的区别：1526 只允许 +1（起点 0 -> target），3229 允许 +1 和 -1 **且起点是任意 `nums`**。

### 核心思路：差分 + 正负分家计数

令 `d[i] = target[i] - nums[i]`（即"每个位置还差多少"）。每次区间 +1/-1 对 `d` 的效果是"把 `d` 某个子数组整体减 1 或加 1"。目标是让 `d` 全部变成 0。

关键观察：**连续一段同号的 `d`** 可以作为一个"整块"被一次次区间操作消掉，但**不同号**的段必须分开处理（正的用 -1 操作、负的用 +1 操作，互不共享）。进一步地，在同号段内部，相邻位置差的**绝对值**决定了额外需要多少次独立操作。

### 方法：分段扫描 + 相邻差累加

```python
def minimumOperations(nums: list[int], target: list[int]) -> int:
    n = len(nums)
    d = [target[i] - nums[i] for i in range(n)]
    ans = 0
    prev = 0  # 上一位的 d（段外视作 0）
    for x in d:
        if x >= 0 and prev >= 0:
            # 同为非负：只需补上升部分
            ans += max(0, x - prev)
        elif x <= 0 and prev <= 0:
            # 同为非正：只需补下降部分（绝对值视角）
            ans += max(0, prev - x)
        else:
            # 跨 0：整段新开，直接加 |x|
            ans += abs(x)
        prev = x
    return ans
```

**时间 O(n)，空间 O(1)**（不用显式存 `d`，边算边用）。

### 为什么这样算是对的（正确性论证）

把 `d` 画成折线。每次 +1/-1 区间操作相当于把某个区间 **整体平移 1**。要把折线压到 0：
- 同号相邻段：像 LC 1526 那样"叠积木"，只有**上升沿**（相对于前一位）需要新增操作，下降/持平可以复用。
- **跨 0**：正值段与负值段必须用**方向相反**的操作，天然不共享，所以负段第一位要从 0 起算，贡献 `|x|`。

**等价视角**：用 `p[i] = max(d[i], 0)` 与 `q[i] = max(-d[i], 0)`，答案 = `LC1526(p) + LC1526(q)`，其中 LC 1526 的答案 = `p[0] + sum(max(0, p[i]-p[i-1]) for i>=1)`。上面那段代码是把两者合并到一次扫描里。

### 示例追踪

`nums = [3, 5, 1, 2]`, `target = [4, 6, 2, 4]`, `d = [1, 1, 1, 2]`：
- i=0: `prev=0, x=1`，同号非负，ans += max(0, 1-0) = 1
- i=1: `prev=1, x=1`，ans += 0
- i=2: `prev=1, x=1`，ans += 0
- i=3: `prev=1, x=2`，ans += max(0, 2-1) = 1
- **Total = 2**（用两次区间 +1 操作：[0..3] +1, [3..3] +1）

`nums = [1, 3, 2]`, `target = [2, 1, 4]`, `d = [1, -2, 2]`：
- i=0: prev=0, x=1，ans += 1
- i=1: prev=1, x=-2，跨 0，ans += |-2| = 2
- i=2: prev=-2, x=2，跨 0，ans += 2
- **Total = 5**

### 相关题 / 套路迁移

| 题号 | 题意 | 关键连接 |
|------|------|----------|
| **LC 1526** Min Increments on Subarrays | 只允许 +1，起点全 0 | 本题的"半边"：`ans = target[0] + sum(max(0, target[i]-target[i-1]))` |
| **LC 370** Range Addition | 多次区间加，求最终数组 | 差分数组正向：`d[l]+=v, d[r+1]-=v` |
| **LC 798** Smallest Rotation | 差分 + 扫描线 | 区间操作 -> 差分思维的通用套路 |
| **LC 1109** Corporate Flight Bookings | 多个 [l,r] 区间加 | 差分 + 前缀和 |
| **LC 2772** Apply Operations to Make All Equal to Zero | 区间减法、判可行 | 差分 + 贪心消除 |

### 套路识别：什么时候想到"差分贪心"？

1. 题面有"**区间同步 ±1**"或"**区间加某值**"，且问**最少操作数**。
2. 目标是"让数组等于某值 / 全部为 0"。
3. 关键思考步骤：
   - 定义 `d[i] = target[i] - nums[i]`；
   - 相邻差 `d[i] - d[i-1]` 的符号与大小决定**这一位是否需要新增操作**；
   - 同号段内部只计**上升沿**，异号段之间**全部计入**。

### 陷阱与边界

1. **起点边界**：`prev = 0`（段外视作 0），相当于在数组前面补一个 0；否则第一位的贡献会漏掉。
2. **全相等情况**：`nums == target`，所有 `d=0`，答案 0。代码里 `max(0, 0-0)=0`，正确。
3. **单调递减段（同号）**：比如 `d = [3, 2, 1]`，应为 3 次（[0..2]+1 做 3 次）。代码：1=3, i=1: max(0,2-3)=0, i=2: 0 => 3，正确。
4. **锯齿同号**：`d = [1, 3, 2, 4]`，ans = 1 + 2 + 0 + 2 = 5。正确（每次"抬高"都是新操作）。
5. **跨 0 不能合并**：`d = [2, -1]` 不是 2 次而是 3 次——正段用 -1 操作、负段用 +1 操作，方向不同，不能复用。
6. **溢出**：数值可能是负数或大数，用 Python `int` 无忧；C++ 要注意 `long long`。

### 复杂度总结

| 方法 | 时间 | 空间 |
|------|------|------|
| 差分贪心（单次扫描） | O(n) | O(1) |

### 45 秒口播脚本（面试开头）

> "定义 `d = target - nums`，把折线压到 0。同号连续段像 LC 1526 那样叠积木，只有**上升沿**是新增操作；**跨 0 的段**必须分开处理——正的要 -1 操作、负的要 +1 操作，天然不共享，整段直接按绝对值计入。边扫边累加 `max(0, x-prev)`（同非负）/ `max(0, prev-x)`（同非正）/ `|x|`（异号），O(n) 一遍完事。本质上是 `LC1526(max(d,0)) + LC1526(max(-d,0))` 的合并扫描。"
"""


def main() -> None:
    """Tag LC 3229 with Pinterest and update notes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, company_tags FROM problems WHERE leetcode_id = 3229")
    row = c.fetchone()
    if not row:
        print("[ERR] LC 3229 not found")
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
    print(f"[OK] LC 3229 (id={pid}) updated. Pinterest tag added: {changed_tag}. Tags: {tags}. Notes len: {len(NOTES)}")
    conn.close()


if __name__ == "__main__":
    main()
