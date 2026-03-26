"""Expand Blind75 problem notes - batch 1 (14 problems).

Updates notes for LC 1, 3, 11, 15, 19, 20, 21, 33, 39, 48, 49, 53, 54, 55
with structured sections: 思路, 关键技巧, 核心代码, 注意点, 复杂度.
"""

import sqlite3
import sys

DB_PATH = "data/mle_prep.db"

EXPANDED_NOTES: dict[int, str] = {
    1: """## Two Sum

### 思路
使用哈希表(dictionary)存储已遍历的值及其下标。对于每个元素，检查 target - nums[i] 是否已在哈希表中。

### 关键技巧
- 一次遍历即可完成，不需要先构建完整哈希表再查找
- 哈希表存储 {值: 下标}，查找 complement = target - nums[i]

### 核心代码
```python
def twoSum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

### 注意点
- 题目保证恰好有一个解，不需要处理无解情况
- 同一个元素不能使用两次，所以先检查再插入
- 返回的是下标，不是值

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(n) - 哈希表存储""",

    3: """## Longest Substring Without Repeating Characters

### 思路
滑动窗口法。维护一个窗口 [left, right]，用 set 或 dict 记录窗口内字符。右指针扩展时若遇到重复字符，左指针收缩直到消除重复。

### 关键技巧
- 用 dict 记录字符最后出现的位置，可以直接跳转 left 指针，避免逐步收缩
- left = max(left, last_seen[char] + 1) 保证 left 只增不减

### 核心代码
```python
def lengthOfLongestSubstring(s: str) -> int:
    last_seen = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

### 注意点
- last_seen[char] >= left 的检查很关键，防止 left 回退
- 空字符串应返回 0
- 字符集可能包含任意 ASCII/Unicode 字符

### 复杂度
- 时间: O(n) - 每个字符最多被访问两次
- 空间: O(min(n, m)) - m 为字符集大小""",

    11: """## Container With Most Water

### 思路
双指针法（贪心）。左右指针从两端向中间收缩，每次移动较短的那根线。因为宽度在缩小，只有增加高度才可能找到更大面积。

### 关键技巧
- 短板效应：面积由较短的线决定，移动较长的线只会让宽度减小而高度不变或更低
- 所以每次移动较短的那一侧，才有可能找到更优解

### 核心代码
```python
def maxArea(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        h = min(height[left], height[right])
        max_water = max(max_water, h * (right - left))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water
```

### 注意点
- 两根线相等时移动哪一侧都可以（不影响正确性）
- 不要混淆此题和 Trapping Rain Water（接雨水用的是不同思路）

### 复杂度
- 时间: O(n) - 双指针一次遍历
- 空间: O(1)""",

    15: """## 3Sum

### 思路
排序 + 双指针。先排序数组，固定第一个数 nums[i]，然后在 i+1 到 n-1 范围内用双指针找两数之和等于 -nums[i]。

### 关键技巧
- 排序后可以跳过重复元素，避免重复三元组
- 固定 i 后，left = i+1, right = n-1，和 Two Sum II 相同
- 三个层次的去重：i 层去重、left 层去重、right 层去重

### 核心代码
```python
def threeSum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # skip duplicate i
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1  # skip duplicate left
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1  # skip duplicate right
                left += 1
                right -= 1
    return result
```

### 注意点
- 去重逻辑必须在找到答案后执行，不能在找答案前跳过
- nums[i] > 0 时可以提前终止（排序后后面都是正数，三数之和不可能为0）
- 注意边界：left < right 的检查在跳过重复时也需要

### 复杂度
- 时间: O(n^2) - 排序 O(n log n) + 双层循环 O(n^2)
- 空间: O(1) 不算输出（排序可能 O(log n)）""",

    19: """## Remove Nth Node From End of List

### 思路
快慢指针法。快指针先走 n 步，然后快慢指针同时移动，当快指针到达末尾时慢指针正好在倒数第 n+1 个节点。

### 关键技巧
- 添加 dummy sentinel 节点，统一处理删除头节点的情况
- 快指针先走 n+1 步（或 n 步后从 dummy 开始），这样慢指针停在要删除节点的前一个

### 核心代码
```python
def removeNthFromEnd(head: ListNode, n: int) -> ListNode:
    dummy = ListNode(0, head)
    fast = slow = dummy
    # fast 先走 n+1 步
    for _ in range(n + 1):
        fast = fast.next
    # 同时走到末尾
    while fast:
        fast = fast.next
        slow = slow.next
    # 删除 slow.next
    slow.next = slow.next.next
    return dummy.next
```

### 注意点
- 不用 dummy 的话，删除头节点需要特判
- n 保证有效（1 <= n <= 链表长度），不需要额外检查
- 一次遍历即可完成（follow-up 要求）

### 复杂度
- 时间: O(L) - L 为链表长度，一次遍历
- 空间: O(1)""",

    20: """## Valid Parentheses

### 思路
栈的基本应用。遇到左括号入栈，遇到右括号检查栈顶是否匹配。

### 关键技巧
- 用 dict 映射右括号到对应的左括号，简化匹配逻辑
- 最后检查栈是否为空（处理多余左括号的情况）

### 核心代码
```python
def isValid(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            if not stack or stack[-1] != mapping[char]:
                return False
            stack.pop()
        else:
            stack.append(char)
    return len(stack) == 0
```

### 注意点
- 空字符串返回 True
- 右括号在栈空时出现 -> 直接返回 False
- 只有 (){}[] 六种字符，不需要处理其他字符

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(n) - 最坏情况全是左括号""",

    21: """## Merge Two Sorted Lists

### 思路
归并排序的 merge 步骤。用 dummy 节点简化头部处理，逐个比较两个链表的当前节点，较小的接到结果链表后面。

### 关键技巧
- dummy 节点避免处理头部的特殊情况
- 循环结束后，将未遍历完的链表直接接到末尾（不需要逐个复制）

### 核心代码
```python
def mergeTwoLists(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0)
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 if l1 else l2
    return dummy.next
```

### 注意点
- l1.val <= l2.val 中的等号保证稳定性
- 递归解法也可以但会使用 O(n) 栈空间
- 两个链表中有一个为空的情况自然处理

### 复杂度
- 时间: O(n + m) - n, m 为两个链表长度
- 空间: O(1) - 迭代法只用常数空间""",

    33: """## Search in Rotated Sorted Array

### 思路
二分查找。关键观察：旋转后的数组，mid 将数组分为两半，其中一半一定是有序的。判断 target 是否在有序的那一半中，据此决定搜索方向。

### 关键技巧
- 判断哪一半有序：nums[left] <= nums[mid] 说明左半有序，否则右半有序
- target 在有序半边的范围内则缩小到该半边，否则搜索另一半

### 核心代码
```python
def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        # 左半有序
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # 右半有序
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

### 注意点
- nums[left] <= nums[mid] 的等号处理 left == mid 的情况（只剩两个元素时）
- 题目保证无重复元素（有重复的是 LC 81，需要额外处理）
- 范围判断时注意开闭区间：nums[left] <= target < nums[mid]

### 复杂度
- 时间: O(log n) - 标准二分
- 空间: O(1)""",

    39: """## Combination Sum

### 思路
回溯法(DFS)。每次选择一个候选数加入当前组合，如果当前和等于 target 则记录答案，大于则剪枝回退。允许重复使用同一个数。

### 关键技巧
- 排序 candidates，每次只考虑 >= 当前 candidate 的数（避免重复组合）
- 传入 start 索引，保证组合中的数字顺序非递减
- 剪枝：当 remain < 0 时提前返回

### 核心代码
```python
def combinationSum(candidates: list[int], target: int) -> list[list[int]]:
    candidates.sort()
    result = []

    def backtrack(start: int, remain: int, path: list[int]) -> None:
        if remain == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remain:
                break  # pruning: sorted, so all subsequent are larger
            path.append(candidates[i])
            backtrack(i, remain - candidates[i], path)  # i not i+1: reuse allowed
            path.pop()

    backtrack(0, target, [])
    return result
```

### 注意点
- 传 i 而不是 i+1（允许重复使用），区别于 Combination Sum II（LC 40）
- result.append(path[:]) 必须是副本，不能直接 append(path)
- 排序后的剪枝 break 很重要，否则会超时

### 复杂度
- 时间: O(n^(T/M)) - T 为 target，M 为最小候选数
- 空间: O(T/M) - 递归深度""",

    48: """## Rotate Image

### 思路
原地旋转矩阵90度（顺时针）。先转置矩阵（沿主对角线翻转），再左右翻转每一行。

### 关键技巧
- 顺时针90度 = 转置 + 水平翻转
- 逆时针90度 = 转置 + 垂直翻转
- 180度 = 水平翻转 + 垂直翻转
- 本质是二面体群 D4 的操作组合

### 核心代码
```python
def rotate(matrix: list[list[int]]) -> None:
    n = len(matrix)
    # Step 1: transpose
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    # Step 2: reverse each row
    for row in matrix:
        row.reverse()
```

### 注意点
- 转置时 j 从 i+1 开始，避免交换两次（等于没交换）
- 题目要求原地修改，不能创建新矩阵
- 也可以用逐圈旋转法（四个位置一组轮换），但代码更复杂

### 复杂度
- 时间: O(n^2) - 遍历所有元素
- 空间: O(1) - 原地操作""",

    49: """## Group Anagrams

### 思路
将每个字符串排序后作为 key，相同 key 的字符串归为一组。

### 关键技巧
- sorted(str) 返回字符列表，需要 tuple() 或 ''.join() 转为可哈希 key
- 也可以用字符频率 tuple 作为 key（26个字母的计数），避免排序

### 核心代码
```python
from collections import defaultdict

def groupAnagrams(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())
```

### 注意点
- 空字符串 "" 排序后是 ()，可以正常作为 key
- 所有输入都是小写字母（题目约束）
- 输出顺序不重要

### 复杂度
- 时间: O(n * k log k) - n 为字符串数量，k 为最长字符串长度
- 空间: O(n * k) - 存储所有字符串""",

    53: """## Maximum Subarray

### 思路
Kadane 算法（贪心/动态规划）。维护当前子数组的最大和 current_sum，如果加上当前元素后比当前元素本身还小，就从当前元素重新开始。

### 关键技巧
- current_sum = max(nums[i], current_sum + nums[i])：要么延续之前的子数组，要么从当前开始新的
- 等价于：如果 current_sum < 0，就丢弃之前的，从当前元素重新开始

### 核心代码
```python
def maxSubArray(nums: list[int]) -> int:
    current_sum = max_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum
```

### 注意点
- 初始值用 nums[0]，不能用 0（全负数数组会出错）
- 子数组不能为空（至少包含一个元素）
- 分治法也可解，时间 O(n log n)，但 Kadane 更优

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1)""",

    54: """## Spiral Matrix

### 思路
逐层剥离法。定义四个边界 top, bottom, left, right，按 右->下->左->上 的顺序遍历当前最外层，每遍历完一个方向就收缩对应边界。

### 关键技巧
- 每次遍历一个方向后，检查边界是否越界（提前终止）
- 收缩顺序：遍历完上行后 top++，遍历完右列后 right--，以此类推

### 核心代码
```python
def spiralOrder(matrix: list[list[int]]) -> list[int]:
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for col in range(left, right + 1):  # right
            result.append(matrix[top][col])
        top += 1
        for row in range(top, bottom + 1):  # down
            result.append(matrix[row][right])
        right -= 1
        if top <= bottom:
            for col in range(right, left - 1, -1):  # left
                result.append(matrix[bottom][col])
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):  # up
                result.append(matrix[row][left])
            left += 1
    return result
```

### 注意点
- 向左和向上遍历前需要检查边界（防止单行或单列时重复遍历）
- 非方阵也需要处理（m != n）
- 空矩阵边界情况

### 复杂度
- 时间: O(m * n) - 每个元素恰好访问一次
- 空间: O(1) 不算输出""",

    55: """## Jump Game

### 思路
贪心法。维护当前能到达的最远位置 max_reach。从左到右遍历，每个位置更新 max_reach = max(max_reach, i + nums[i])。如果某位置 i > max_reach，说明到不了。

### 关键技巧
- 关键是维护 max_reach 而不是模拟跳跃过程
- 如果 max_reach >= n-1，直接返回 True
- 遍历时只需检查 i <= max_reach（当前位置可达）

### 核心代码
```python
def canJump(nums: list[int]) -> bool:
    max_reach = 0
    for i in range(len(nums)):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + nums[i])
        if max_reach >= len(nums) - 1:
            return True
    return True
```

### 注意点
- 提前终止：max_reach >= n-1 时可以立即返回 True
- nums[i] = 0 并不意味着失败，只要之前的 max_reach 已经超过 i 即可
- 只有一个元素时直接返回 True

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1)""",
}


def main() -> None:
    """Update problem notes in the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updated = 0
    for leetcode_id, new_notes in EXPANDED_NOTES.items():
        # Get existing notes
        cur.execute(
            "SELECT id, notes FROM problems WHERE leetcode_id = ?",
            (leetcode_id,),
        )
        row = cur.fetchone()
        if not row:
            print(f"WARNING: LC {leetcode_id} not found in DB", file=sys.stderr)
            continue

        problem_id, old_notes = row

        # Merge: prepend old notes as "original notes" section, then expanded
        if old_notes and old_notes.strip():
            merged = f"**Original notes**: {old_notes.strip()}\n\n{new_notes.strip()}"
        else:
            merged = new_notes.strip()

        cur.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (merged, problem_id),
        )
        updated += 1
        print(f"Updated LC {leetcode_id} (id={problem_id})")

    conn.commit()
    conn.close()
    print(f"\nDone: {updated}/{len(EXPANDED_NOTES)} problems updated.")


if __name__ == "__main__":
    main()
