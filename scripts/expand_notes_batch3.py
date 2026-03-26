"""Expand Blind75 problem notes - batch 3 (14 problems).

Updates notes for LC 124, 125, 128, 133, 139, 141, 143, 152, 153, 190, 191, 198, 200, 206
with structured sections: 思路, 关键技巧, 核心代码, 注意点, 复杂度.
"""

import sqlite3
import sys

DB_PATH = "data/mle_prep.db"

EXPANDED_NOTES: dict[int, str] = {
    124: """## Binary Tree Maximum Path Sum

### 思路
任意路径可以经过任意节点。对于每个节点，计算"经过该节点的最大路径和"：node.val + 左子树最大贡献 + 右子树最大贡献。全局维护最大值。每个节点向上返回的贡献只能选一条分支（左或右）。

### 关键技巧
- 节点贡献 = node.val + max(左贡献, 右贡献)，负贡献取 0（不选该分支）
- 经过该节点的路径和 = node.val + 左贡献 + 右贡献（这里可以同时选两条分支）
- 向上返回时只能选一条分支（路径不能分叉）

### 核心代码
```python
def maxPathSum(root: TreeNode) -> int:
    ans = [float('-inf')]

    def dfs(node: TreeNode) -> int:
        if not node:
            return 0
        left = max(dfs(node.left), 0)
        right = max(dfs(node.right), 0)
        ans[0] = max(ans[0], node.val + left + right)
        return node.val + max(left, right)

    dfs(root)
    return ans[0]
```

### 注意点
- 节点值可以为负数，所以初始 ans 用 -inf
- max(贡献, 0) 处理负贡献：不选比选更好
- 更新全局最大值时用两条分支，返回时只用一条
- 路径至少包含一个节点

### 复杂度
- 时间: O(n) - 每个节点访问一次
- 空间: O(h) - 递归栈深度""",

    125: """## Valid Palindrome

### 思路
双指针法。左右两个指针向中间移动，跳过非字母数字字符，忽略大小写比较。

### 关键技巧
- 用 isalnum() 判断是否是字母或数字
- 用 lower() 统一大小写
- 空字符串被认为是回文

### 核心代码
```python
def isPalindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

### 注意点
- 跳过非字母数字字符时要检查 left < right，防止越界
- 不要忘记 lower()，"A" 和 "a" 应该相等
- 简洁写法：先过滤再判断 filtered == filtered[::-1]，但空间 O(n)

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1) - 双指针原地操作""",

    128: """## Longest Consecutive Sequence

### 思路
将所有数字放入 HashSet。对于每个数字 x，如果 x-1 不在集合中，说明 x 是一个连续序列的起点。从 x 开始向上数（x+1, x+2, ...），记录长度。

### 关键技巧
- 只从序列起点开始计数（x-1 不在集合中），避免重复计算
- 这个判断是 O(n) 复杂度的关键：每个元素只会被作为起点检查一次
- 不需要排序

### 核心代码
```python
def longestConsecutive(nums: list[int]) -> int:
    num_set = set(nums)
    longest = 0
    for num in num_set:
        if num - 1 not in num_set:  # 是序列起点
            length = 1
            while num + length in num_set:
                length += 1
            longest = max(longest, length)
    return longest
```

### 注意点
- 遍历 num_set 而非 nums，避免重复元素导致多次处理
- 空数组返回 0
- 不需要排序，题目要求 O(n) 时间复杂度

### 复杂度
- 时间: O(n) - 每个元素最多被访问两次（一次在外层循环，一次在 while 中）
- 空间: O(n) - HashSet""",

    133: """## Clone Graph

### 思路
BFS 或 DFS。用 HashMap 记录已克隆的节点（原节点 -> 克隆节点），避免重复克隆和处理环。遍历时如果邻居已克隆就直接引用，否则创建新节点。

### 关键技巧
- HashMap 既是 visited 标记又是原节点到克隆节点的映射
- DFS 递归写法更简洁
- 处理 None 输入和单节点无邻居的情况

### 核心代码
```python
def cloneGraph(node: Node) -> Node:
    if not node:
        return None
    cloned = {}

    def dfs(n: Node) -> Node:
        if n in cloned:
            return cloned[n]
        clone = Node(n.val)
        cloned[n] = clone
        for neighbor in n.neighbors:
            clone.neighbors.append(dfs(neighbor))
        return clone

    return dfs(node)
```

### 注意点
- 必须在递归邻居之前就将 clone 放入 cloned，否则环会导致无限递归
- BFS 写法：用队列遍历，遇到未克隆的邻居才入队
- 图可能有自环（节点的邻居包含自己）

### 复杂度
- 时间: O(V + E) - 每个节点和边各处理一次
- 空间: O(V) - HashMap + 递归栈""",

    139: """## Word Break

### 思路
动态规划。dp[i] 表示 s[0:i] 是否可以被词典中的单词拆分。对于每个位置 i，检查所有可能的分割点 j：如果 dp[j] 为 True 且 s[j:i] 在词典中，则 dp[i] = True。

### 关键技巧
- 将 wordDict 转换为 set，O(1) 查找
- dp[0] = True（空字符串可以被拆分）
- 内层循环可以从 i-maxWordLen 开始，减少不必要的检查

### 核心代码
```python
def wordBreak(s: str, wordDict: list[str]) -> bool:
    word_set = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[n]
```

### 注意点
- break 优化：找到一个有效分割就可以停止内层循环
- s[j:i] 切片是 O(k)，可以用 Trie 优化到 O(1)
- 词典中的单词可以被多次使用

### 复杂度
- 时间: O(n^2 * k) - n 为字符串长度，k 为平均单词长度（切片开销）
- 空间: O(n) - dp 数组""",

    141: """## Linked List Cycle

### 思路
快慢指针（Floyd 判圈法）。慢指针每次走一步，快指针每次走两步。如果有环，快指针最终会追上慢指针；如果无环，快指针会先到达 None。

### 关键技巧
- 快指针速度是慢指针的两倍，所以在环中每轮距离缩小 1
- 不需要 HashSet，O(1) 空间
- 环的入口检测（LC 142）：相遇后将一个指针放回 head，两个都每次走一步，再次相遇就是入口

### 核心代码
```python
def hasCycle(head: ListNode) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

### 注意点
- 检查 fast and fast.next 防止空指针（无环时 fast 先到末尾）
- 用 is 而非 == 比较节点引用（比较的是同一个对象，不是值）
- 空链表和单节点无环的情况自然处理

### 复杂度
- 时间: O(n) - 最多绕环一圈
- 空间: O(1) - 只用两个指针""",

    143: """## Reorder List

### 思路
三步走：(1) 找到链表中点（快慢指针）；(2) 反转后半部分；(3) 交替合并前半和反转后的后半部分。

### 关键技巧
- 中点偏左：当节点数为偶数时，slow 停在前半部分的最后一个节点
- 反转后半部分用迭代法（prev/curr）
- 合并时交替插入：取一个前半的，取一个后半的

### 核心代码
```python
def reorderList(head: ListNode) -> None:
    if not head or not head.next:
        return
    # 1. 找中点
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    # 2. 反转后半部分
    prev, curr = None, slow.next
    slow.next = None  # 断开前后两半
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    # 3. 交替合并
    first, second = head, prev
    while second:
        tmp1, tmp2 = first.next, second.next
        first.next = second
        second.next = tmp1
        first, second = tmp1, tmp2
```

### 注意点
- 断开前后两半（slow.next = None）很重要，否则会形成环
- fast.next and fast.next.next：偶数长度时 slow 在左中点
- 合并时 second 可能比 first 短一个节点，用 while second 控制

### 复杂度
- 时间: O(n) - 三次遍历
- 空间: O(1) - 原地操作""",

    152: """## Maximum Product Subarray

### 思路
动态规划。维护当前位置结束的最大乘积 max_prod 和最小乘积 min_prod（因为负数乘以最小值可能变成最大值）。每个位置有三种选择：当前元素自己、当前元素 * 前最大、当前元素 * 前最小。

### 关键技巧
- 负数会让最大变最小、最小变最大，所以必须同时维护 max 和 min
- 每步更新：new_max = max(num, max_prod*num, min_prod*num)
- 同理 new_min = min(num, max_prod*num, min_prod*num)

### 核心代码
```python
def maxProduct(nums: list[int]) -> int:
    result = nums[0]
    max_prod = min_prod = 1
    for num in nums:
        candidates = (num, max_prod * num, min_prod * num)
        max_prod = max(candidates)
        min_prod = min(candidates)
        result = max(result, max_prod)
    return result
```

### 注意点
- 初始化 max_prod = min_prod = 1（乘法单位元），result = nums[0]
- 0 会重置乘积，但 max(num, ...) 自然处理了这种情况
- 不能像最大子数组和那样只维护 max，必须同时维护 min
- 另一种写法：遇到负数时交换 max_prod 和 min_prod

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1) - 只用常数变量""",

    153: """## Find Minimum in Rotated Sorted Array

### 思路
二分搜索。比较 mid 和 right 的值：如果 nums[mid] > nums[right]，最小值在右半部分；否则在左半部分（含 mid）。

### 关键技巧
- 和 right 比较（不是和 left 比较），因为我们找的是最小值
- nums[mid] > nums[right] 说明旋转点在 mid 右侧
- nums[mid] <= nums[right] 说明 mid 到 right 是有序的，最小值在左侧（含 mid）

### 核心代码
```python
def findMin(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]
```

### 注意点
- right = mid（不是 mid-1），因为 mid 本身可能是最小值
- left = mid + 1，因为 nums[mid] > nums[right]，mid 肯定不是最小值
- 没有重复元素（有重复的是 LC 154，需要额外处理 nums[mid] == nums[right]）
- 循环条件是 left < right（不是 <=），退出时 left == right

### 复杂度
- 时间: O(log n) - 二分搜索
- 空间: O(1)""",

    190: """## Reverse Bits

### 思路
逐位处理。取出 n 的最低位，放到结果的对应高位位置。重复 32 次。

### 关键技巧
- 取最低位：n & 1
- 放到高位：result = (result << 1) | (n & 1)
- 右移 n：n >>= 1
- 也可以用位交换（分治法），类似归并排序的思想

### 核心代码
```python
def reverseBits(n: int) -> int:
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
```

### 注意点
- 固定循环 32 次（32 位无符号整数）
- Python 整数无溢出问题，但其他语言需要用无符号右移（>>>）
- Follow-up: 如果多次调用，可以用缓存（按字节反转，查表）

### 复杂度
- 时间: O(1) - 固定 32 次循环
- 空间: O(1)""",

    191: """## Number of 1 Bits

### 思路
逐位检查，或者用 n & (n-1) 技巧每次消除最低位的 1。

### 关键技巧
- n & (n-1) 将 n 最低位的 1 变为 0（Brian Kernighan 算法）
- 循环次数等于 1 的个数，比逐位检查更优
- Python: bin(n).count('1') 最简洁但面试需要写位运算

### 核心代码
```python
def hammingWeight(n: int) -> int:
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
```

### 注意点
- n & (n-1) 原理：n-1 会将最低位的 1 及其右侧所有位取反
- 逐位法：while n: count += n & 1; n >>= 1
- Python 中负数用补码表示，但 LeetCode 保证输入为无符号整数

### 复杂度
- 时间: O(k) - k 为 1 的个数（最坏 O(32) = O(1)）
- 空间: O(1)""",

    198: """## House Robber

### 思路
动态规划。dp[i] 表示到第 i 家为止能偷到的最大金额。每家有两个选择：偷（dp[i-2] + nums[i]）或不偷（dp[i-1]）。

### 关键技巧
- 状态转移：dp[i] = max(dp[i-1], dp[i-2] + nums[i])
- 空间优化：只需要前两个状态 prev1 和 prev2
- 不能偷相邻的两家（约束条件）

### 核心代码
```python
def rob(nums: list[int]) -> int:
    prev2, prev1 = 0, 0
    for num in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + num)
    return prev1
```

### 注意点
- 初始化 prev2 = prev1 = 0（没有房子时偷 0）
- 元组交换保证同时更新，不会用到已更新的值
- House Robber II (LC 213)：环形排列，分两次计算（去掉首或去掉尾）
- 只有一家时直接返回 nums[0]

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1) - 只用两个变量""",

    200: """## Number of Islands

### 思路
遍历网格，遇到 '1' 就岛屿计数 +1，然后用 BFS/DFS 将整个连通的陆地标记为 '0'（已访问）。

### 关键技巧
- 原地修改：将访问过的 '1' 改为 '0'，不需要额外的 visited 数组
- DFS 递归更简洁，BFS 用队列实现
- 四个方向：上下左右

### 核心代码
```python
def numIslands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])
    count = 0

    def dfs(i: int, j: int) -> None:
        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != '1':
            return
        grid[i][j] = '0'
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)

    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                count += 1
                dfs(i, j)
    return count
```

### 注意点
- 网格中是字符 '1' 和 '0'，不是整数
- 原地修改会破坏输入，如果不允许则用 visited 集合
- Union-Find 也可以解决，适合动态添加的场景
- 大网格用 BFS 避免递归栈溢出

### 复杂度
- 时间: O(m * n) - 每个格子最多访问一次
- 空间: O(m * n) - 最坏情况递归栈深度（全是陆地）""",

    206: """## Reverse Linked List

### 思路
迭代法：用三个指针 prev、curr、next，逐个翻转指针方向。每步将 curr.next 指向 prev，然后三个指针同时前移。

### 关键技巧
- prev 初始为 None（反转后尾节点的 next）
- 先保存 curr.next（否则翻转后丢失后续节点）
- 递归法：先递归到尾部，回溯时翻转指针

### 核心代码
```python
def reverseList(head: ListNode) -> ListNode:
    prev, curr = None, head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev
```

### 注意点
- 返回 prev（不是 curr，因为 curr 是 None）
- 空链表和单节点链表无需特殊处理
- 递归写法：reverseList(head.next)，然后 head.next.next = head; head.next = None
- 这是链表类题目的基础操作，很多题都用到（如 reorder list、回文链表）

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1) - 迭代法；递归法 O(n)""",
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
