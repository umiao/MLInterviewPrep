# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot: add Pinterest tag + expanded Chinese notes for LC 84 (Largest Rectangle in Histogram).

T-P1-390 deliverable.
"""
import json
import sqlite3

DB_PATH = "data/mle_prep.db"

NOTES = r"""## LC 84 - Largest Rectangle in Histogram (单调栈 / 分治)

> Pinterest must-do list (2025-11 cutoff). See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾
给定 `heights: list[int]`，每根柱子宽度为 1，求直方图中所能围出的最大矩形面积。

### 核心思路：为每根柱子找"左右第一个更矮的下标"

对任意以高度 `h = heights[i]` 的柱子作为矩形的**高**，其最大宽度由：
- 左边第一个严格小于 `h` 的下标 `L`
- 右边第一个严格小于 `h` 的下标 `R`

决定，面积 = `h * (R - L - 1)`。对每根柱子都做一次这种计算，取最大值即可。单调递增栈一次遍历就能同时得到 L 与 R。

### 方法一：单调栈 O(n) 标准解

```python
def largestRectangleArea(heights: list[int]) -> int:
    stack: list[int] = [-1]   # 哨兵，避免栈空判断
    max_area = 0
    for i, h in enumerate(heights):
        while stack[-1] != -1 and heights[stack[-1]] >= h:
            top = stack.pop()
            height = heights[top]
            width = i - stack[-1] - 1   # 右界 i, 左界 stack[-1]
            max_area = max(max_area, height * width)
        stack.append(i)
    # 清栈：虚拟右界 = len(heights)
    n = len(heights)
    while stack[-1] != -1:
        top = stack.pop()
        height = heights[top]
        width = n - stack[-1] - 1
        max_area = max(max_area, height * width)
    return max_area
```

**关键点**：
- 栈内维持**下标的高度严格递增**；遇到更矮的 `h` 就把栈顶弹出并结算。
- 被弹出的柱子，其右界就是当前 `i`（第一个更矮），左界就是**新的栈顶**（栈内前一个仍然更矮或哨兵）。
- 哨兵 `-1` 让 `width = i - (-1) - 1 = i`，省掉空栈分支。
- 每个下标最多入栈/出栈一次，总时间 O(n)。

**一种等价写法**（在末尾追加 `0` 触发清栈，代码更短）：

```python
def largestRectangleArea(heights):
    heights.append(0)
    stack, max_area = [], 0
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] >= h:
            top = stack.pop()
            left = stack[-1] if stack else -1
            max_area = max(max_area, heights[top] * (i - left - 1))
        stack.append(i)
    heights.pop()  # 不污染输入
    return max_area
```

### 方法二：分治 O(n log n) 平均 / O(n^2) 最坏

思路：最大矩形要么
1. 以整个区间中**最矮柱子**为高，宽度 = 整个区间长度；要么
2. 完全落在最矮柱子的左半段；要么
3. 完全落在最矮柱子的右半段。

```python
def largestRectangleArea(heights: list[int]) -> int:
    def solve(lo: int, hi: int) -> int:
        if lo > hi:
            return 0
        # 找区间最小下标
        m = lo
        for k in range(lo, hi + 1):
            if heights[k] < heights[m]:
                m = k
        area_here = heights[m] * (hi - lo + 1)
        return max(area_here, solve(lo, m - 1), solve(m + 1, hi))
    return solve(0, len(heights) - 1)
```

- 平均 O(n log n)；**最坏** O(n^2)（全升序或全降序，分裂极不平衡）。
- 可以用稀疏表 / 线段树把"区间最小值下标"查询降到 O(1)/O(log n)，稳定 O(n log n)，但面试通常不做。
- **面试定位**：作为"我还知道另一种思路"的备选；单调栈才是最优解。

### 方法三：左右最近更小（两次单调栈，教学友好）

显式地预计算 `left[i]`、`right[i]`，再一次遍历求答案。逻辑上与方法一等价，但分开写更好调试：

```python
def largestRectangleArea(heights):
    n = len(heights)
    left = [-1] * n   # left[i]: 左边第一个严格更小的下标，没有为 -1
    right = [n] * n   # right[i]: 右边第一个严格更小的下标，没有为 n
    stack = []
    for i in range(n):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack.clear()
    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        right[i] = stack[-1] if stack else n
        stack.append(i)
    return max((heights[i] * (right[i] - left[i] - 1) for i in range(n)), default=0)
```

> **一次栈 vs 两次栈**：一次栈更精简；两次栈在"多个问题都要用到左/右最近更小"时更易复用。

### 相关题 / 套路迁移

| 题号 | 题意 | 关键连接 |
|------|------|----------|
| **LC 85** Maximal Rectangle | 0/1 矩阵中最大全 1 矩形 | 逐行累加 `heights[j]`（全 1 列的高度），每行调用 LC 84 的单调栈，O(m*n) |
| **LC 42** Trapping Rain Water | 每个下标能接的雨水 | 同是"左右最近更高/更矮"模型；单调栈也能做，双指针更常见 |
| **LC 11** Container With Most Water | 两柱之间能装的最大水 | 对撞双指针 O(n)，每次移动较矮一侧；与 84/42 同属"直方图/水"家族但解法不同 |
| **LC 496/503/739** Next Greater Element 系列 | 直接考察单调栈模板 | 把 LC 84 的"下一个更小"改为"下一个更大"，模板完全一致 |
| **LC 907** Sum of Subarray Minimums | 所有子数组最小值之和 | 经典"每个元素作为最小值贡献区间多少子数组" = 左右最近更小下标 |

### 套路识别：什么时候想到单调栈？

遇到以下信号，立刻把单调栈当候选：
1. 需要对每个下标快速得到**左/右第一个比它大/小**的位置（"Next Greater / Smaller"）。
2. 问题形式是"以每个元素为最小/最大值，它能扩张的最大区间/对答案的贡献是多少"。
3. 数组配合"维持一个单调不变量"的描述（如某区间最值、滑动窗口最值 -- 后者是单调队列的变体）。

**比较：单调栈 vs 双指针 vs 分治**
- 单调栈：需要"每个元素的贡献区间" -> LC 84/85/907。
- 对撞双指针：两端决定答案、答案是两端的函数 -> LC 11。
- 分治：答案可按"极值分裂" -> LC 84 备选、最大子数组等。

### 陷阱与边界

1. **严格 vs 非严格比较**：弹出条件写 `>=` 可以避免重复结算等高柱子（最终答案不变，因为最后一个等高柱子仍会正确结算）。如果写 `>`，等高柱子之间也会入栈，面积仍对，但栈更深。
2. **清栈别忘了**：循环结束后栈里剩下的柱子都延伸到数组末尾（右界 = n）。忘了清栈会漏掉最大矩形（比如 `[2,1,5,6,2,3]` 正好考这一点，答案 10 来自 `[5,6]` 两根）。
3. **空数组**：直接返回 0。
4. **全等高**：一次入栈不触发弹出，全靠清栈阶段结算，结果 = `h * n`，正确。
5. **大小可能到 10^5**：递归版分治在最坏情况会栈溢出，Python 默认 `sys.setrecursionlimit(1000)`；面试优先写单调栈迭代版。

### 复杂度总结

| 方法 | 时间 | 空间 |
|------|------|------|
| 单调栈（一次/两次） | O(n) | O(n) |
| 分治（朴素找最小） | 平均 O(n log n) / 最坏 O(n^2) | O(log n) 递归栈 |
| 分治 + 稀疏表 | O(n log n) | O(n log n) |

### 45 秒口播脚本（面试开头）

> "这题我用单调递增栈。对每根柱子，我要知道左右第一个比它矮的位置 -- 这样以它为高的矩形宽度就确定了。栈里保存下标，保持栈内高度单调递增；遇到更矮的当前柱子就弹出栈顶结算面积，左界是新栈顶，右界是当前下标。加一个 -1 哨兵避免空栈判断，最后还要清栈，时间 O(n)。分治 O(n log n) 也能做但常数大，不推荐作为首选。"
"""


def main() -> None:
    """Tag LC 84 with Pinterest and update notes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, company_tags FROM problems WHERE leetcode_id = 84")
    row = c.fetchone()
    if not row:
        print("[ERR] LC 84 not found")
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
    print(f"[OK] LC 84 (id={pid}) updated. Pinterest tag added: {changed_tag}. Notes len: {len(NOTES)}")
    conn.close()


if __name__ == "__main__":
    main()
