# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot: add Chinese notes for LC 85 (Maximal Rectangle) and mark completed.

T-P0-434 deliverable.
"""
import sqlite3

DB_PATH = "data/mle_prep.db"

NOTES = r"""## LC 85 - Maximal Rectangle (单调栈 + 逐行 Histogram)

> Hard. 核心: 把 0/1 矩阵逐行转化为 LC 84 直方图问题, 每行跑一次单调栈.

### 题目回顾
给定 `m x n` 二进制矩阵 `matrix` (值为 '0' 或 '1'), 找到只包含 '1' 的最大矩形, 返回其面积.

### 转化直觉: 为什么能变成 LC 84?

把矩阵想象成一栋楼俯视图. 对每一行 `i`, 计算每列 `j` 从第 `i` 行往上连续 '1' 的高度:

```
heights[j] = heights[j] + 1   if matrix[i][j] == '1'
           = 0                 otherwise
```

例如矩阵:
```
1 0 1 0 0
1 0 1 1 1
1 1 1 1 1
1 0 0 1 0
```
逐行 heights:
```
row 0: [1, 0, 1, 0, 0]  -> LC84 -> 1
row 1: [2, 0, 2, 1, 1]  -> LC84 -> 3
row 2: [3, 1, 3, 2, 2]  -> LC84 -> 6  <-- 答案
row 3: [4, 0, 0, 3, 0]  -> LC84 -> 4
```

每行的 heights 就是一个直方图, 直接套 LC 84 单调栈求最大矩形面积.

### 方法一: 单调栈 (最优解)

```python
def maximalRectangle(matrix: list[list[str]]) -> int:
    if not matrix or not matrix[0]:
        return 0
    n = len(matrix[0])
    heights = [0] * n
    max_area = 0
    for row in matrix:
        # 更新 heights
        for j in range(n):
            heights[j] = heights[j] + 1 if row[j] == '1' else 0
        # LC 84: 单调栈求直方图最大矩形
        max_area = max(max_area, _largest_rect(heights))
    return max_area


def _largest_rect(heights: list[int]) -> int:
    # LC 84 单调递增栈, 哨兵版
    stack = [-1]  # 左哨兵
    max_area = 0
    for i, h in enumerate(heights):
        while stack[-1] != -1 and heights[stack[-1]] >= h:
            top = stack.pop()
            width = i - stack[-1] - 1
            max_area = max(max_area, heights[top] * width)
        stack.append(i)
    # 清栈: 右界 = len(heights)
    n = len(heights)
    while stack[-1] != -1:
        top = stack.pop()
        width = n - stack[-1] - 1
        max_area = max(max_area, heights[top] * width)
    return max_area
```

**复杂度**: 时间 O(m * n), 空间 O(n). 外层遍历 m 行, 每行单调栈 O(n).

### 边界哨兵技巧

- 栈初始化 `[-1]` 作为左哨兵, 使得 `width = i - stack[-1] - 1` 在栈快空时仍然正确 (不用特判).
- 循环结束后栈内剩余元素右界为 `n` (虚拟右哨兵), 必须清栈, 否则漏掉全升序的最大值.
- 另一种等价写法: `heights.append(0)` 强制触发清栈, 免去循环后清栈代码.

### 为什么 O(mn) 而不是更慢?

- 外层 m 行循环: O(m)
- 内层更新 heights: O(n)
- 内层单调栈 LC 84: 每个元素最多入栈出栈各一次 = O(n)
- 总计: m * (n + n) = O(mn), 没有隐藏的平方

### 方法二: DP 三数组 (left / right / height)

```python
def maximalRectangle(matrix: list[list[str]]) -> int:
    if not matrix or not matrix[0]:
        return 0
    n = len(matrix[0])
    height = [0] * n
    left = [0] * n       # left[j]: 以 (i,j) 为右下角, 高度为 height[j] 时最左列
    right = [n] * n      # right[j]: 最右列的下一个位置
    max_area = 0
    for row in matrix:
        # 更新 height
        for j in range(n):
            height[j] = height[j] + 1 if row[j] == '1' else 0
        # 更新 left: 从左扫, cur_left 记录当前行连续 '1' 的起始列
        cur_left = 0
        for j in range(n):
            if row[j] == '1':
                left[j] = max(left[j], cur_left)
            else:
                left[j] = 0
                cur_left = j + 1
        # 更新 right: 从右扫, cur_right 记录当前行连续 '1' 的终止列+1
        cur_right = n
        for j in range(n - 1, -1, -1):
            if row[j] == '1':
                right[j] = min(right[j], cur_right)
            else:
                right[j] = n
                cur_right = j
        # 计算面积
        for j in range(n):
            max_area = max(max_area, height[j] * (right[j] - left[j]))
    return max_area
```

**DP 核心思想**: 对每个位置 (i, j), 维护:
- `height[j]`: 从 (i, j) 往上连续 '1' 的高度
- `left[j]`: 以 height[j] 为高度时, 矩形能向左扩展到的最左列
- `right[j]`: 能向右扩展到的最右列的下一个位置

面积 = `height[j] * (right[j] - left[j])`.

### 单调栈 vs DP 对比

| 维度 | 单调栈 | DP 三数组 |
|------|--------|-----------|
| 时间 | O(mn) | O(mn) |
| 空间 | O(n) heights + O(n) stack | O(n) * 3 数组 |
| 思路 | 逐行转 LC 84, 套模板 | 直接维护每列的左右边界 |
| 代码量 | 更短 (复用 LC 84) | 更长但无需理解单调栈 |
| 面试推荐 | 首选 (尤其已做 LC 84) | 备选 / 追问"不用栈怎么做" |

### 45 秒口播脚本

> "LC 85 的关键洞察: 把 0/1 矩阵逐行转化为直方图. 对每一行, 维护每列从该行往上连续 1 的高度, 这就变成 LC 84 的最大矩形直方图问题. 每行用单调递增栈 O(n) 求解, 总共 m 行, 时间 O(mn), 空间 O(n). 另外有 DP 三数组做法, left/right/height 逐行更新, 也是 O(mn) 但不需要栈."
"""


def main() -> None:
    """Update LC 85 notes and mark as completed."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM problems WHERE leetcode_id = 85")
    row = c.fetchone()
    if not row:
        print("[ERR] LC 85 not found in DB")
        conn.close()
        return
    pid = row[0]
    c.execute(
        "UPDATE problems SET notes = ?, is_completed = 1 WHERE id = ?",
        (NOTES, pid),
    )
    conn.commit()
    c.execute(
        "SELECT id, leetcode_id, title, is_completed, length(notes) FROM problems WHERE id = ?",
        (pid,),
    )
    verify = c.fetchone()
    print(
        f"[OK] LC 85 (id={verify[0]}) updated. "
        f"is_completed={verify[3]}, notes_len={verify[4]}"
    )
    conn.close()


if __name__ == "__main__":
    main()
