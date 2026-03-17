"""Seed Pillar 1 (Coding & Algorithms) framework node descriptions.

Usage:
    python scripts/seed_pillar1_content.py

Populates the `description` field for all 20 Pillar 1 leaf nodes
in the framework_nodes table. Idempotent -- overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, get_engine  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Content for each leaf topic, keyed by path
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {}

# ===== DATA STRUCTURES =====

CONTENT["pillar1.data_structures.array_string"] = r"""# Array / String

## Overview
Arrays and strings are the most frequently tested data structures in coding interviews. Nearly every problem involves them directly or as the underlying representation. Mastering in-place manipulation, two-pointer techniques, and sliding windows is essential for senior MLE interviews where optimal time/space complexity is expected.

## Core Concepts

### Array Fundamentals
Arrays provide $O(1)$ random access and $O(n)$ insertion/deletion (worst case). In Python, `list` is a dynamic array with amortized $O(1)$ append.

**Key properties**:
- Contiguous memory layout enables cache-friendly traversal
- Sorting transforms many problems from $O(n^2)$ to $O(n \log n)$
- Prefix sums enable $O(1)$ range queries after $O(n)$ preprocessing:

$$
\text{prefix}[i] = \sum_{j=0}^{i} a[j], \quad \text{sum}(l, r) = \text{prefix}[r] - \text{prefix}[l-1]
$$

### String Specifics
Python strings are immutable -- concatenation in a loop is $O(n^2)$. Use `"".join(parts)` for $O(n)$ construction. Key operations:
- **Substring search**: KMP achieves $O(n + m)$; Python's `in` uses a variant of Boyer-Moore
- **Character frequency**: `collections.Counter` for $O(n)$ frequency maps
- **Encoding**: ASCII (128 chars) vs Unicode -- affects hash table sizing

### Two-Pointer Technique
Reduces $O(n^2)$ brute force to $O(n)$ for sorted arrays or specific patterns:

$$
\text{Invariant: } l < r \text{ and search space shrinks each step}
$$

**Variants**: opposite ends (sorted pair sum), same direction (fast/slow for cycles), read/write (in-place removal).

### Sliding Window
Maintains a window $[l, r]$ over a contiguous subarray. Two flavors:
- **Fixed-size**: advance both pointers together
- **Variable-size**: expand $r$, shrink $l$ when constraint violated

## Implementation

```python
def max_subarray_sum_k(arr: list[int], k: int) -> int:
    # Maximum sum of subarray of size k -- fixed sliding window.
    window_sum = sum(arr[:k])
    best = window_sum
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        best = max(best, window_sum)
    return best

def length_of_longest_substring(s: str) -> int:
    # Longest substring without repeating chars -- variable window.
    seen: dict[str, int] = {}
    left = ans = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1
        seen[ch] = right
        ans = max(ans, right - left + 1)
    return ans
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Two pointers (opposite) | Sorted array, pair/triplet sum | Sort first if not sorted; skip duplicates for unique results |
| Sliding window (variable) | Longest/shortest subarray with constraint | Track constraint in hash map or counter; shrink from left |
| Prefix sum | Range sum queries, subarray sum = k | Use hash map of prefix sums for $O(n)$ subarray sum = k |
| In-place manipulation | Remove/move elements without extra space | Read/write pointer pattern; overwrite from end for shifts |
| Sorting + scan | Merge intervals, meeting rooms | Sort by start; greedily merge or count overlaps |

### Common Interview Questions
- [ ] Two Sum / Three Sum with optimal complexity
- [ ] Longest substring without repeating characters
- [ ] Merge intervals
- [ ] Product of array except self (without division)
- [ ] Trapping rain water (two-pointer or stack approach)
- [ ] Minimum window substring

## Comparisons

| Aspect | Brute Force | Two Pointer | Sliding Window | Prefix Sum |
|--------|------------|-------------|----------------|------------|
| Time | $O(n^2)$ | $O(n)$ | $O(n)$ | $O(n)$ preprocess, $O(1)$ query |
| Space | $O(1)$ | $O(1)$ | $O(k)$ for window state | $O(n)$ |
| Requires sorted | No | Often yes | No | No |
| Best for | Small $n$ | Pair problems | Contiguous subarray | Range queries |

## Common Pitfalls
- **Off-by-one in sliding window**: forgetting to initialize the window before the main loop, or miscounting window size
- **Not handling duplicates in two-pointer**: Three Sum requires skipping duplicate values to avoid duplicate triplets in the result
- **String immutability**: building strings with `+=` in a loop is $O(n^2)$; always collect in a list and join
- **Prefix sum indexing**: the prefix array is typically length $n+1$ with `prefix[0] = 0`; off-by-one here causes wrong range sums
- **Modifying array while iterating**: use a separate write pointer or build a new array instead

## Key Takeaways
- [ ] Two pointers on sorted arrays reduce $O(n^2)$ to $O(n)$ -- always consider sorting first
- [ ] Sliding window is the canonical approach for contiguous subarray/substring problems
- [ ] Prefix sums turn range queries into $O(1)$ lookups -- combine with hash maps for subarray sum = k
- [ ] In-place string/array manipulation requires careful index management -- practice the read/write pointer pattern
- [ ] For MLE: array operations map directly to tensor manipulations in NumPy/PyTorch
"""

CONTENT["pillar1.data_structures.hashmap_hashset"] = r"""# HashMap / HashSet

## Overview
Hash-based data structures provide amortized $O(1)$ lookup, insertion, and deletion. They are the single most important tool for optimizing brute-force solutions in interviews. Nearly every problem that asks "can you do better than $O(n^2)$?" has a hash map solution. For MLEs, understanding hashing is critical for feature hashing, bloom filters in data pipelines, and caching in serving systems.

## Core Concepts

### Hash Function and Collision Resolution
A hash function maps keys to bucket indices: $h(k) \to [0, m)$ where $m$ is the table size.

**Collision resolution strategies**:
- **Chaining**: each bucket holds a linked list. Load factor $\alpha = n/m$; expected chain length = $\alpha$
- **Open addressing**: probe sequence (linear, quadratic, double hashing). Degrades past $\alpha > 0.7$

$$
\text{Expected lookups (chaining)} = 1 + \alpha/2 \quad \text{(successful)}, \quad 1 + \alpha \quad \text{(unsuccessful)}
$$

### Python dict Internals
Python uses open addressing with compact dict (CPython 3.6+). Key facts:
- Maintains insertion order (guaranteed since 3.7)
- Resize at $\alpha = 2/3$; doubles table size
- Keys must be hashable (immutable): `str`, `int`, `tuple` are hashable; `list`, `dict` are not

### Common Hash Map Patterns
- **Frequency counting**: `Counter` or `defaultdict(int)`
- **Index mapping**: store last-seen index for "subarray sum" problems
- **Grouping**: `defaultdict(list)` to group anagrams, duplicates, etc.
- **Two-pass vs one-pass**: Two Sum can be solved in one pass by checking map before inserting

## Implementation

```python
from collections import defaultdict

def two_sum(nums: list[int], target: int) -> list[int]:
    # Classic one-pass hash map solution. O(n) time, O(n) space.
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

def group_anagrams(strs: list[str]) -> list[list[str]]:
    # Group strings by sorted character key. O(n * k log k).
    groups: dict[str, list[str]] = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Complement lookup | Two Sum variants, pair problems | Check map before inserting for one-pass |
| Frequency map | Anagrams, permutation checks, top-k | `Counter` comparison is $O(k)$ where $k$ = unique chars |
| Prefix sum + map | Subarray sum equals k | Store prefix sum frequencies; answer = `map[curr - k]` |
| Index tracking | First/last occurrence, sliding window | Map value to index for $O(1)$ position lookup |
| Seen set | Cycle detection, duplicate check | HashSet for $O(1)$ membership testing |

### Common Interview Questions
- [ ] Two Sum (one-pass hash map)
- [ ] Group Anagrams
- [ ] Subarray Sum Equals K (prefix sum + hash map)
- [ ] Longest Consecutive Sequence ($O(n)$ using set)
- [ ] LRU Cache (hash map + doubly linked list)
- [ ] Design a hash map from scratch

## Comparisons

| Aspect | HashMap | TreeMap (SortedDict) | Array (direct addr) |
|--------|---------|---------------------|-------------------|
| Lookup | $O(1)$ amortized | $O(\log n)$ | $O(1)$ |
| Ordered | No (insertion order) | Yes (key order) | By index |
| Space | $O(n)$ | $O(n)$ | $O(\max\_key)$ |
| Use case | General lookup | Range queries, min/max key | Small fixed key range |

## Common Pitfalls
- **Unhashable keys**: lists and dicts cannot be dict keys; convert lists to tuples first
- **Default value mutation**: `dict.fromkeys(keys, [])` shares ONE list object; use `defaultdict(list)` instead
- **Hash collision performance**: worst case is $O(n)$ per lookup with many collisions; Python rehashes automatically but adversarial inputs can degrade performance
- **Forgetting to check existence**: `dict[key]` raises `KeyError`; use `dict.get(key, default)` or check with `in` first
- **Mutable default in Counter**: `Counter` handles missing keys gracefully (returns 0), but `dict` does not

## MLE-Specific Applications
- **Feature hashing (hashing trick)**: maps arbitrary feature names to a fixed-size vector without maintaining a vocabulary. Used in Vowpal Wabbit and large-scale linear models: $\phi(x)_i = \sum_{j: h(j)=i} x_j$
- **Bloom filters**: probabilistic set membership with no false negatives. Used in data pipelines to deduplicate records or check if a URL has been crawled
- **Caching (memoization)**: hash maps power LRU caches in model serving to avoid redundant inference on repeated inputs
- **Embedding lookup tables**: `nn.Embedding` in PyTorch is essentially a hash map from integer IDs to dense vectors

## Key Takeaways
- [ ] Hash maps turn $O(n^2)$ nested loops into $O(n)$ single passes -- always consider them first
- [ ] Prefix sum + hash map is the canonical pattern for "subarray sum = k" problems
- [ ] Know the difference between `dict`, `defaultdict`, `Counter`, and `OrderedDict`
- [ ] For MLE: feature hashing (hashing trick) maps arbitrary features to fixed-size vectors without a vocabulary
- [ ] LRU Cache (dict + doubly linked list) is a top interview design question
"""

CONTENT["pillar1.data_structures.stack_queue"] = r"""# Stack / Queue

## Overview
Stacks (LIFO) and queues (FIFO) are fundamental for managing ordering and processing sequences. Stacks power expression evaluation, parenthesis matching, and monotonic stack problems. Queues enable BFS, level-order traversal, and rate limiting. Deques (double-ended queues) combine both and appear in sliding window maximum problems. These are high-frequency interview topics with well-defined patterns.

## Core Concepts

### Stack (LIFO)
Last-In-First-Out. Operations: `push`, `pop`, `peek` -- all $O(1)$. Python: use `list` (append/pop from end).

**Monotonic stack**: maintains elements in sorted order. Key insight -- when a new element breaks monotonicity, pop and process elements:

$$
\text{For each element, it is pushed once and popped at most once} \implies O(n) \text{ total}
$$

### Queue (FIFO)
First-In-First-Out. Operations: `enqueue`, `dequeue` -- $O(1)$ with linked list or deque. Python: use `collections.deque` (never `list.pop(0)` which is $O(n)$).

### Deque (Double-Ended Queue)
Supports $O(1)$ append/pop from both ends. Critical for sliding window maximum.

### Monotonic Stack Pattern
The monotonic stack maintains a decreasing (or increasing) sequence. Used for "next greater element", "largest rectangle in histogram", and temperature problems.

## Implementation

```python
from collections import deque

def next_greater_element(nums: list[int]) -> list[int]:
    # For each element, find next greater element. O(n).
    result = [-1] * len(nums)
    stack: list[int] = []  # indices, values are decreasing
    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            result[stack.pop()] = num
        stack.append(i)
    return result

def sliding_window_max(nums: list[int], k: int) -> list[int]:
    # Maximum in each window of size k. O(n) using deque.
    dq: deque[int] = deque()  # indices, values are decreasing
    result = []
    for i, num in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Parenthesis matching | Valid parentheses, expression parsing | Push opening; pop and match on closing |
| Monotonic decreasing stack | Next greater element, daily temperatures | Pop when current > top; remaining in stack have no NGE |
| Monotonic increasing stack | Largest rectangle in histogram | Pop when current < top; width = distance between boundaries |
| Min stack | Get minimum in $O(1)$ | Store (value, current_min) pairs, or auxiliary min stack |
| Queue via two stacks | Implement queue | Amortized $O(1)$: push to in-stack, lazy transfer to out-stack |
| Sliding window max | Maximum in fixed window | Deque of indices; maintain decreasing values |

### Common Interview Questions
- [ ] Valid Parentheses (stack)
- [ ] Daily Temperatures (monotonic stack)
- [ ] Largest Rectangle in Histogram (monotonic stack)
- [ ] Min Stack ($O(1)$ getMin)
- [ ] Sliding Window Maximum (deque)
- [ ] Implement Queue using Stacks
- [ ] Evaluate Reverse Polish Notation

## Comparisons

| Aspect | Stack (list) | Queue (deque) | Deque | Priority Queue (heapq) |
|--------|-------------|--------------|-------|----------------------|
| Order | LIFO | FIFO | Both ends | By priority |
| Push | $O(1)$ | $O(1)$ | $O(1)$ both ends | $O(\log n)$ |
| Pop | $O(1)$ | $O(1)$ | $O(1)$ both ends | $O(\log n)$ |
| Peek min/max | $O(n)$ or $O(1)$ with aux | $O(n)$ | $O(1)$ front/back | $O(1)$ min |
| Use case | Parsing, backtracking | BFS, scheduling | Sliding window | Dijkstra, top-k |

## Common Pitfalls
- **Using list as queue**: `list.pop(0)` is $O(n)$ because it shifts all elements; always use `collections.deque`
- **Monotonic stack direction**: for "next greater element" use decreasing stack; for "next smaller" use increasing stack -- mixing these up is a common error
- **Forgetting to handle empty stack**: always check `stack` before calling `stack[-1]` or `stack.pop()`
- **Largest rectangle**: the sentinel trick (appending 0 to the array) simplifies the code by forcing all remaining elements off the stack

## Advanced Patterns
- **Calculator problems**: use two stacks (operands + operators) or convert to RPN first. Handle operator precedence by comparing with stack top before pushing
- **Stack-based tree traversal**: iterative inorder/preorder/postorder all use explicit stacks. Morris traversal achieves $O(1)$ space by temporarily modifying tree pointers
- **Circular queue**: implement with a fixed-size array and `front`/`rear` pointers with modular arithmetic: `rear = (rear + 1) % capacity`

## Key Takeaways
- [ ] Monotonic stack solves "next greater/smaller" in $O(n)$ -- each element pushed and popped at most once
- [ ] Always use `deque` for queues in Python -- `list.pop(0)` is $O(n)$
- [ ] Sliding window maximum with deque is a classic pattern: maintain decreasing deque of indices
- [ ] Min stack: pair each element with the running minimum for $O(1)$ getMin
- [ ] For MLE: queues appear in BFS for graph-based models, data loading pipelines, and request buffering
"""

CONTENT["pillar1.data_structures.linked_list"] = r"""# Linked List

## Overview
Linked lists test pointer manipulation skills and in-place algorithm design. While rarely used directly in ML systems (arrays dominate for cache performance), linked list problems are interview staples that assess careful handling of edge cases, pointer reassignment, and cycle detection. The fast/slow pointer technique is particularly important.

## Core Concepts

### Singly vs Doubly Linked List
- **Singly**: each node has `val` and `next`. Traversal is $O(n)$, prepend is $O(1)$
- **Doubly**: each node has `val`, `next`, and `prev`. Enables $O(1)$ deletion given a node reference

### Sentinel (Dummy) Node
A dummy head node simplifies edge cases (empty list, head deletion):
```
dummy -> 1 -> 2 -> 3 -> None
```
Return `dummy.next` as the actual head. This eliminates special-case code for head operations.

### Fast/Slow Pointer (Floyd's Algorithm)
Two pointers moving at different speeds:
- **Cycle detection**: slow moves 1 step, fast moves 2 steps. They meet iff cycle exists
- **Finding middle**: when fast reaches end, slow is at middle
- **Cycle start**: after meeting, move one pointer to head; advance both by 1 until they meet again

$$
\text{Meeting point: } d_{\text{head to cycle start}} = d_{\text{meeting point to cycle start}}
$$

## Implementation

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None):
        self.val = val
        self.next = nxt

def reverse_list(head: ListNode | None) -> ListNode | None:
    # Reverse a linked list iteratively. O(n) time, O(1) space.
    prev, curr = None, head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev

def has_cycle(head: ListNode | None) -> bool:
    # Floyd's cycle detection. O(n) time, O(1) space.
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

def merge_two_sorted(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    # Merge two sorted lists. O(n+m) time, O(1) space.
    dummy = curr = ListNode()
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next, l1 = l1, l1.next
        else:
            curr.next, l2 = l2, l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Dummy head | Any list modification | Eliminates head-deletion edge cases |
| Fast/slow pointer | Cycle detection, find middle | $O(1)$ space alternative to hash set |
| Reverse in groups | Reverse every k nodes | Track group boundaries; reconnect after each reversal |
| Merge sorted lists | Merge k sorted lists | Use heap for k-way merge in $O(n \log k)$ |
| Two-pointer with gap | Remove nth from end | Advance first pointer n steps, then move both |

### Common Interview Questions
- [ ] Reverse a linked list (iterative and recursive)
- [ ] Detect cycle and find cycle start (Floyd's algorithm)
- [ ] Merge two sorted linked lists
- [ ] Remove nth node from end (two-pointer with gap)
- [ ] LRU Cache (doubly linked list + hash map)
- [ ] Reverse nodes in k-group
- [ ] Copy list with random pointer

## Comparisons

| Aspect | Singly Linked | Doubly Linked | Array |
|--------|--------------|--------------|-------|
| Access by index | $O(n)$ | $O(n)$ | $O(1)$ |
| Insert at head | $O(1)$ | $O(1)$ | $O(n)$ |
| Delete given node | $O(n)$ (need prev) | $O(1)$ | $O(n)$ |
| Memory overhead | 1 pointer/node | 2 pointers/node | None |
| Cache performance | Poor | Poor | Excellent |

## Common Pitfalls
- **Losing the next pointer**: when reversing, always save `next` BEFORE reassigning `curr.next`
- **Not using dummy node**: head-deletion requires special handling without a dummy; always use `dummy = ListNode(0); dummy.next = head`
- **Infinite loops in cycle problems**: if you forget to advance a pointer or break incorrectly, the code runs forever
- **Off-by-one in "remove nth from end"**: start the first pointer $n+1$ steps ahead (or use dummy node) to land on the node BEFORE the target

## Advanced Patterns
- **Sort a linked list**: merge sort is optimal -- find middle with fast/slow, recursively sort halves, merge. $O(n \log n)$ time, $O(\log n)$ stack space
- **Flatten a multilevel linked list**: use DFS (stack) or recursion; treat child pointers as branches
- **Skip list**: probabilistic alternative to balanced BSTs with $O(\log n)$ expected search. Used in Redis sorted sets and LevelDB. Multiple levels of linked lists with random promotion
- **XOR linked list**: stores `prev XOR next` in a single pointer field, halving memory. Rarely practical but tests understanding of pointer arithmetic

## Key Takeaways
- [ ] Always use a dummy/sentinel node to simplify edge cases in list manipulation
- [ ] Floyd's fast/slow pointer: cycle detection, middle finding, and cycle start in $O(1)$ space
- [ ] Draw diagrams before coding -- pointer reassignment order matters
- [ ] Common bug: losing reference to `next` before reassigning pointers
- [ ] For MLE: LRU Cache (doubly linked list + hash map) is the most practical linked list application
"""

CONTENT["pillar1.data_structures.tree_bst"] = r"""# Tree / BST

## Overview
Trees are fundamental to both algorithm interviews and ML systems (decision trees, hierarchical clustering, syntax trees for NLP). Binary search trees provide $O(\log n)$ operations when balanced. Tree traversals, recursive thinking, and BST properties are tested extensively. Senior candidates should be comfortable with both recursive and iterative approaches.

## Core Concepts

### Tree Traversals
For a binary tree with root $r$, left subtree $L$, right subtree $R$:

| Traversal | Order | Use Case |
|-----------|-------|----------|
| Inorder | $L \to r \to R$ | BST gives sorted order |
| Preorder | $r \to L \to R$ | Serialize tree, copy tree |
| Postorder | $L \to R \to r$ | Delete tree, evaluate expressions |
| Level-order | BFS by depth | Level-wise processing |

### Binary Search Tree (BST) Property
For every node $n$: all values in left subtree $< n.val <$ all values in right subtree.

**Operations on balanced BST**: search, insert, delete all $O(\log n)$. Worst case (skewed): $O(n)$.

### Tree Height and Balance
- **Height**: longest root-to-leaf path. Balanced tree: $h = O(\log n)$
- **AVL**: $|h(L) - h(R)| \le 1$ for every node
- **Red-Black**: guarantees $h \le 2 \log_2(n+1)$

### Lowest Common Ancestor (LCA)
For nodes $p$ and $q$, LCA is the deepest node that is an ancestor of both:
- **BST**: compare values; if both less, go left; both greater, go right; otherwise current is LCA
- **General tree**: recursive -- if current is $p$ or $q$, return it; check both subtrees

## Implementation

```python
class TreeNode:
    def __init__(self, val: int = 0, left: "TreeNode | None" = None,
                 right: "TreeNode | None" = None):
        self.val = val
        self.left = left
        self.right = right

def inorder_iterative(root: TreeNode | None) -> list[int]:
    # Inorder traversal without recursion. O(n) time, O(h) space.
    result, stack = [], []
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right
    return result

def max_depth(root: TreeNode | None) -> int:
    # Maximum depth of binary tree. O(n).
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def is_valid_bst(root: TreeNode | None,
                 lo: float = float("-inf"),
                 hi: float = float("inf")) -> bool:
    # Validate BST using range propagation. O(n).
    if not root:
        return True
    if root.val <= lo or root.val >= hi:
        return False
    return (is_valid_bst(root.left, lo, root.val)
            and is_valid_bst(root.right, root.val, hi))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Recursive DFS | Most tree problems | Base case = None/leaf; combine left + right results |
| Iterative with stack | Inorder/preorder without recursion | Simulate call stack explicitly |
| Level-order BFS | Level-wise operations | Queue-based; process one level per outer loop iteration |
| BST property | Search, validate, LCA in BST | Inorder gives sorted; prune search space by value comparison |
| Path problems | Root-to-leaf sum, max path sum | Track running sum/path; backtrack at leaves |

### Common Interview Questions
- [ ] Maximum depth / diameter of binary tree
- [ ] Validate BST
- [ ] Lowest common ancestor (BST and general)
- [ ] Binary tree level order traversal
- [ ] Serialize and deserialize binary tree
- [ ] Construct tree from inorder + preorder
- [ ] Binary tree maximum path sum

## Common Pitfalls
- **BST validation**: comparing only with parent is wrong. The constraint is that ALL values in the left subtree must be less than the node, not just the immediate child. Pass min/max bounds recursively
- **Confusing tree diameter with depth**: diameter is the longest path between any two nodes (may not pass through root). Compute as `max(left_depth + right_depth)` at each node
- **Forgetting base case**: `if not root: return ...` must be the first line of every recursive tree function
- **Modifying tree during traversal**: if the problem asks to modify the tree, consider whether you need a post-order traversal to process children before parents

## Advanced Patterns
- **Morris traversal**: $O(1)$ space inorder traversal by temporarily threading the tree. Right pointer of inorder predecessor points to current node. Restore tree structure after visiting
- **Serialization**: preorder with null markers uniquely identifies a tree. BFS level-order also works. For BST specifically, preorder alone suffices (no null markers needed) since BST property constrains structure
- **Segment tree**: a balanced binary tree for range queries (sum, min, max) with $O(\log n)$ update and query. Used in competitive programming and database indexing
- **Binary indexed tree (Fenwick tree)**: supports prefix sum queries and point updates in $O(\log n)$. More space-efficient than segment trees for cumulative frequency tables

## Key Takeaways
- [ ] Master both recursive and iterative traversals -- interviewers may ask for either
- [ ] BST validation: pass min/max bounds down, not just compare with parent
- [ ] Tree problems are naturally recursive: identify base case, recursive relation, and how to combine results
- [ ] Level-order traversal pattern: `for _ in range(len(queue))` to process one level at a time
- [ ] For MLE: decision tree splitting maps directly to BST-like structures; tree-based models (XGBoost) are interview staples
"""

CONTENT["pillar1.data_structures.heap_priority_queue"] = r"""# Heap / Priority Queue

## Overview
Heaps provide $O(\log n)$ insertion and $O(1)$ access to the min (or max) element, making them essential for top-k problems, stream processing, and graph algorithms (Dijkstra, Prim). Python's `heapq` is a min-heap. Understanding heap operations, the heapify trick, and when to use heaps vs. sorting is critical for interview performance.

## Core Concepts

### Binary Heap Properties
A complete binary tree stored as an array where:
- **Min-heap**: parent $\le$ children. Root = minimum element
- **Max-heap**: parent $\ge$ children. Root = maximum element

For node at index $i$ (0-indexed):
$$
\text{parent}(i) = \lfloor (i-1)/2 \rfloor, \quad \text{left}(i) = 2i+1, \quad \text{right}(i) = 2i+2
$$

### Time Complexities

| Operation | Time |
|-----------|------|
| Insert (push) | $O(\log n)$ |
| Extract min/max (pop) | $O(\log n)$ |
| Peek min/max | $O(1)$ |
| Heapify (build heap) | $O(n)$ -- NOT $O(n \log n)$ |
| Find k-th largest | $O(n + k \log n)$ with heapify + k pops |

### Heapify Analysis
Building a heap from an unsorted array is $O(n)$, not $O(n \log n)$:

$$
\sum_{h=0}^{\lfloor \log n \rfloor} \frac{n}{2^{h+1}} \cdot O(h) = O(n)
$$

### Python heapq Patterns
`heapq` is a min-heap only. For max-heap, negate values. For custom ordering, use tuples: `(priority, tiebreaker, item)`.

## Implementation

```python
import heapq

def top_k_frequent(nums: list[int], k: int) -> list[int]:
    # Find k most frequent elements. O(n + m log k) where m = unique.
    from collections import Counter
    freq = Counter(nums)
    # Min-heap of size k: smallest frequency gets evicted
    return heapq.nlargest(k, freq.keys(), key=freq.get)

def merge_k_sorted_lists(lists: list[list[int]]) -> list[int]:
    # Merge k sorted lists. O(n log k) where n = total elements.
    result: list[int] = []
    heap: list[tuple[int, int, int]] = []  # (value, list_idx, elem_idx)
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    while heap:
        val, li, ei = heapq.heappop(heap)
        result.append(val)
        if ei + 1 < len(lists[li]):
            heapq.heappush(heap, (lists[li][ei + 1], li, ei + 1))
    return result

def find_median_stream():
    # Running median using two heaps.
    lo: list[int] = []  # max-heap (negated) for lower half
    hi: list[int] = []  # min-heap for upper half
    def add(num: int) -> float:
        heapq.heappush(lo, -num)
        heapq.heappush(hi, -heapq.heappop(lo))
        if len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        if len(lo) > len(hi):
            return -lo[0]
        return (-lo[0] + hi[0]) / 2
    return add
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Top-k elements | Find k largest/smallest/most frequent | Min-heap of size k; evict smallest |
| K-way merge | Merge k sorted streams | Heap of size k; push next from popped stream |
| Two heaps (median) | Running median, balanced partition | Max-heap for lower half, min-heap for upper half |
| Lazy deletion | Dijkstra with updates | Push duplicates; skip stale entries on pop |
| Heap + hash map | Design Twitter, event scheduler | Heap for ordering, map for metadata |

### Common Interview Questions
- [ ] Top K Frequent Elements
- [ ] Merge K Sorted Lists
- [ ] Find Median from Data Stream (two heaps)
- [ ] Kth Largest Element in a Stream
- [ ] Task Scheduler (greedy + heap)
- [ ] Reorganize String (max-heap greedy)

## Comparisons

| Aspect | Heap | Sorted Array | BST (balanced) |
|--------|------|-------------|----------------|
| Insert | $O(\log n)$ | $O(n)$ | $O(\log n)$ |
| Find min | $O(1)$ | $O(1)$ | $O(\log n)$ |
| Delete min | $O(\log n)$ | $O(1)$ amortized | $O(\log n)$ |
| Find k-th | $O(k \log n)$ | $O(1)$ | $O(\log n)$ |
| Best for | Streaming top-k | Static sorted data | Dynamic ordered set |

## Common Pitfalls
- **Forgetting tuple ordering for tiebreaking**: when pushing `(priority, item)` to heapq, items must be comparable. Use `(priority, tiebreaker_counter, item)` to avoid comparison errors on non-comparable items
- **Confusing heapify with repeated push**: `heapq.heapify(list)` is $O(n)$; pushing $n$ elements one by one is $O(n \log n)$. Always heapify when you have all elements upfront
- **Two-heap rebalancing**: after every insert, ensure $|\text{len(lo)} - \text{len(hi)}| \le 1$. The order of operations (push to one heap, then rebalance) matters
- **Using heap for sorted output**: repeatedly popping gives sorted order but destroys the heap. For sorted iteration without modification, copy first

## Advanced Patterns
- **Indexed priority queue**: supports decrease-key in $O(\log n)$ by maintaining a position map. Essential for Dijkstra with proper decrease-key (though lazy deletion is simpler in interviews)
- **Interval scheduling with heap**: process events by start time; heap tracks end times of active intervals. Heap size at any point = number of concurrent intervals
- **External sorting**: when data exceeds memory, divide into sorted chunks, then k-way merge using a heap. This is how `sort` works on large files and how distributed systems merge sorted partitions

## Key Takeaways
- [ ] Heapify is $O(n)$ not $O(n \log n)$ -- use `heapq.heapify` when you have all elements upfront
- [ ] For max-heap in Python, negate values: `heappush(h, -val)`, result = `-heappop(h)`
- [ ] Two-heap pattern for median: max-heap (lower half) + min-heap (upper half), rebalance after each insert
- [ ] K-way merge with heap is $O(n \log k)$ -- much better than $O(nk)$ naive merge for large $k$
- [ ] For MLE: heaps power beam search in sequence models, priority-based data sampling, and Dijkstra in graph neural networks
"""

CONTENT["pillar1.data_structures.trie"] = r"""# Trie

## Overview
A trie (prefix tree) is a tree-like data structure for efficient string prefix operations. It provides $O(L)$ search/insert where $L$ is the word length, independent of the number of stored words. Tries are essential for autocomplete systems, spell checkers, and IP routing -- all relevant to ML-powered search and NLP applications. They also appear in interview problems involving prefix matching and word search.

## Core Concepts

### Trie Structure
Each node represents a character. A path from root to a node represents a prefix. A boolean flag marks word endings.

**Space complexity**: $O(\Sigma \cdot N \cdot L)$ where $\Sigma$ = alphabet size, $N$ = number of words, $L$ = average length. In practice, prefix sharing reduces this significantly.

### Operations Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Insert word | $O(L)$ | $O(L)$ new nodes worst case |
| Search word | $O(L)$ | $O(1)$ |
| Prefix search | $O(P)$ for prefix of length $P$ | $O(1)$ |
| Autocomplete (all words with prefix) | $O(P + K)$ where $K$ = results | Depends on results |

### Trie vs Hash Set for Strings
- **Trie advantages**: prefix queries, lexicographic ordering, no hash collisions
- **Hash set advantages**: simpler implementation, faster for exact lookups (constant factor), less memory for short strings with no shared prefixes

### Compressed Trie (Radix Tree)
Merges nodes with single children, reducing space. Used in Linux kernel routing tables and some databases.

## Implementation

```python
class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False

class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, prefix: str) -> "TrieNode | None":
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Basic trie | Prefix matching, autocomplete | Dict-based children for flexible alphabet |
| Trie + DFS | Word search in grid, word break | Combine trie traversal with grid/string DFS |
| Trie + backtracking | Word search II (find all words in grid) | Build trie from word list; DFS from each cell |
| Bitwise trie | Maximum XOR pair | Store binary representations; greedily pick opposite bits |
| Trie with count | Prefix frequency, IP routing | Store count at each node for prefix statistics |

### Common Interview Questions
- [ ] Implement Trie (insert, search, startsWith)
- [ ] Word Search II (trie + grid DFS)
- [ ] Design Search Autocomplete System
- [ ] Replace Words (prefix replacement using trie)
- [ ] Maximum XOR of Two Numbers (bitwise trie)
- [ ] Word Break (can be solved with trie + DP)

## Comparisons

| Aspect | Trie | HashMap | Sorted Array + Binary Search |
|--------|------|---------|------------------------------|
| Exact lookup | $O(L)$ | $O(L)$ average | $O(L \log n)$ |
| Prefix query | $O(P)$ | $O(n \cdot L)$ scan | $O(L \log n)$ |
| Space | $O(\Sigma \cdot N \cdot L)$ | $O(N \cdot L)$ | $O(N \cdot L)$ |
| Ordered iteration | Yes (lexicographic) | No | Yes |
| Best for | Prefix-heavy workloads | Exact lookups | Static dictionary |

## Common Pitfalls
- **Memory explosion with array-based children**: using `[None] * 26` at every node wastes memory for sparse tries. Dict-based children are more practical
- **Forgetting `is_end` flag**: without it, searching for "app" in a trie containing "apple" incorrectly returns True
- **Trie deletion**: rarely asked but tricky -- must check if a node has other children before removing it. Use reference counting or lazy deletion

## Key Takeaways
- [ ] Trie gives $O(L)$ prefix queries -- hash maps cannot match this for "all words starting with X"
- [ ] Use dict-based children (not array of 26) for flexibility and space efficiency with sparse alphabets
- [ ] Word Search II is the canonical trie + backtracking problem -- build trie from word list, DFS on grid
- [ ] Bitwise trie for maximum XOR is an advanced but important pattern
- [ ] For MLE: tries power tokenizer vocabulary lookup (BPE), autocomplete ranking, and prefix-based feature matching
"""

CONTENT["pillar1.data_structures.union_find"] = r"""# Union-Find

## Overview
Union-Find (Disjoint Set Union / DSU) efficiently tracks connected components and supports near-$O(1)$ union and find operations with path compression and union by rank. It is the optimal data structure for dynamic connectivity problems, Kruskal's MST algorithm, and detecting cycles in undirected graphs. For MLEs, it appears in clustering, image segmentation, and entity resolution problems.

## Core Concepts

### Core Operations
- **Find(x)**: returns the root representative of $x$'s component
- **Union(x, y)**: merges the components containing $x$ and $y$
- **Connected(x, y)**: checks if $x$ and $y$ are in the same component

### Optimizations
Without optimizations, trees can degenerate to linked lists ($O(n)$ find). Two key optimizations:

**Path compression**: during Find, point every node directly to root:
$$
\text{Find}(x): \text{parent}[x] = \text{Find}(\text{parent}[x])
$$

**Union by rank** (or size): attach smaller tree under larger tree's root.

With both optimizations, amortized cost per operation is $O(\alpha(n))$ where $\alpha$ is the inverse Ackermann function -- effectively constant ($\alpha(n) \le 4$ for any practical $n$).

### When to Use Union-Find vs BFS/DFS
- **Union-Find**: dynamic connectivity (edges added over time), counting components, cycle detection
- **BFS/DFS**: path finding, shortest path, traversal order matters

## Implementation

```python
class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # already connected
        # union by rank
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Connected components count | Number of islands, friend circles | Initialize $n$ components; each successful union decrements count |
| Kruskal's MST | Minimum spanning tree | Sort edges by weight; union endpoints; skip if already connected |
| Cycle detection | Undirected graph cycle | If find(u) == find(v) before union, adding edge (u,v) creates cycle |
| Dynamic connectivity | Edges added over time | Union-Find handles online edge additions; BFS/DFS needs rebuild |
| Weighted Union-Find | Equations, relative relationships | Store weight on edges; adjust during path compression |

### Common Interview Questions
- [ ] Number of Connected Components (union-find or DFS)
- [ ] Redundant Connection (find the edge that creates a cycle)
- [ ] Accounts Merge (group accounts by common emails)
- [ ] Number of Islands (union adjacent land cells)
- [ ] Evaluate Division (weighted union-find for equation chains)
- [ ] Smallest String With Swaps (union swap positions, sort within components)

## Comparisons

| Aspect | Union-Find | BFS/DFS | Adjacency Matrix |
|--------|-----------|---------|-----------------|
| Dynamic edge addition | $O(\alpha(n))$ per op | $O(V+E)$ rebuild | $O(1)$ add, $O(V)$ query |
| Connected query | $O(\alpha(n))$ | $O(V+E)$ | $O(V)$ |
| Path finding | Not supported | Yes | Yes |
| Space | $O(V)$ | $O(V+E)$ | $O(V^2)$ |
| Best for | Connectivity only | Traversal, paths | Dense graphs |

## Common Pitfalls
- **Forgetting path compression**: without it, find degrades to $O(n)$ on skewed trees. Always add `parent[x] = find(parent[x])` in the recursive version, or use iterative path halving
- **Union without rank/size**: without rank-based union, the tree can become a linked list. Always attach the smaller tree under the larger one
- **Off-by-one in node indexing**: ensure node indices match your parent array size. For 1-indexed problems, allocate `parent` of size $n+1$
- **Not returning whether union succeeded**: the `union` function should return `True` if a merge happened (different components) or `False` if already connected. This is needed for cycle detection and counting

## Key Takeaways
- [ ] Always implement both path compression AND union by rank -- together they give $O(\alpha(n))$ amortized
- [ ] Track component count: initialize to $n$, decrement on each successful union
- [ ] Union-Find cannot find paths between nodes -- it only answers connectivity queries
- [ ] For cycle detection in undirected graphs, union-find is cleaner than DFS with visited tracking
- [ ] For MLE: union-find powers entity resolution (merging duplicate records), connected component analysis in graphs, and hierarchical clustering linkage
"""

# ===== ALGORITHM PARADIGMS =====

CONTENT["pillar1.algorithm_paradigms.binary_search"] = r"""# Binary Search

## Overview
Binary search achieves $O(\log n)$ search on sorted/monotonic data. Beyond simple array search, the real interview power comes from "binary search on answer" -- searching over a solution space when the feasibility function is monotonic. This technique converts optimization problems into decision problems and is a favorite at senior MLE interviews for its elegance and broad applicability.

## Core Concepts

### Standard Binary Search
Search for target in sorted array. Three key decisions:
1. **Inclusive bounds**: `lo, hi = 0, len(arr) - 1` with `while lo <= hi`
2. **Exclusive right**: `lo, hi = 0, len(arr)` with `while lo < hi`
3. **Midpoint**: `mid = lo + (hi - lo) // 2` (avoids overflow)

### Boundary Finding (bisect)
Find the insertion point for a value:
- **bisect_left**: first position where `arr[pos] >= target` (leftmost boundary)
- **bisect_right**: first position where `arr[pos] > target` (rightmost boundary + 1)

$$
\text{bisect\_left}(a, x) = \min\{i : a[i] \ge x\}
$$

### Binary Search on Answer
When optimizing a value $v$ and you can check "is $v$ feasible?" in polynomial time, and feasibility is monotonic (all values $\ge v^*$ are feasible, or all $\le v^*$), binary search on the answer space:

$$
\text{If } f(v) \text{ is monotonic, search } [lo, hi] \text{ for the boundary where } f \text{ flips}
$$

**Examples**: minimum capacity to ship packages in D days, split array largest sum, Koko eating bananas.

## Implementation

```python
from bisect import bisect_left

def binary_search(arr: list[int], target: int) -> int:
    # Standard binary search. Returns index or -1.
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def min_capacity_to_ship(weights: list[int], days: int) -> int:
    # Binary search on answer: min ship capacity for D days.
    def can_ship(cap: int) -> bool:
        d, cur = 1, 0
        for w in weights:
            if cur + w > cap:
                d += 1
                cur = 0
            cur += w
        return d <= days

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can_ship(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Standard search | Sorted array lookup | Use `bisect_left`/`bisect_right` in Python for clean code |
| First/last occurrence | Duplicates in sorted array | bisect_left for first, bisect_right - 1 for last |
| Search on answer | Minimize maximum / maximize minimum | Define `is_feasible(mid)`; search over answer range |
| Search in rotated array | Rotated sorted array | One half is always sorted; determine which half target is in |
| Search in 2D matrix | Row-sorted or fully sorted matrix | Treat as 1D array: `row = mid // cols, col = mid % cols` |

### Common Interview Questions
- [ ] Binary Search (standard + edge cases)
- [ ] Search in Rotated Sorted Array
- [ ] Find First and Last Position of Element
- [ ] Koko Eating Bananas (binary search on answer)
- [ ] Split Array Largest Sum (binary search on answer)
- [ ] Median of Two Sorted Arrays ($O(\log \min(m,n))$)

## Comparisons

| Aspect | Linear Search | Binary Search | Interpolation Search |
|--------|--------------|---------------|---------------------|
| Time | $O(n)$ | $O(\log n)$ | $O(\log \log n)$ average (uniform) |
| Requirement | None | Sorted/monotonic | Uniformly distributed |
| Implementation | Trivial | Moderate | Complex |
| Off-by-one risk | None | High | High |

## Common Pitfalls
- **Off-by-one errors**: the most frequent bug. Use `lo < hi` with `hi = mid` when searching for a boundary (leftmost valid). Use `lo <= hi` with `lo = mid + 1, hi = mid - 1` for exact search
- **Infinite loops**: if `lo = mid` when `lo + 1 == hi`, the loop never terminates. Use `mid = lo + (hi - lo + 1) // 2` (round up) when `lo = mid` is in the update
- **Wrong monotonicity direction**: "binary search on answer" requires the feasibility function to be monotonic. Verify: if $f(x)$ is True, is $f(x+1)$ also True? If not, binary search does not apply
- **Not handling empty input**: check `len(arr) == 0` before starting binary search

## Key Takeaways
- [ ] Binary search on answer is the most powerful variant: "minimize the maximum" or "maximize the minimum" signals this pattern
- [ ] Use `lo < hi` with `hi = mid` (not `mid - 1`) for finding boundaries to avoid off-by-one errors
- [ ] Python's `bisect_left`/`bisect_right` handle boundary finding cleanly -- prefer them over manual implementation
- [ ] For rotated array: always determine which half is sorted first
- [ ] For MLE: binary search appears in hyperparameter tuning (bisecting learning rate), threshold optimization (ROC curve), and quantile computation
"""

CONTENT["pillar1.algorithm_paradigms.bfs_dfs"] = r"""# BFS / DFS

## Overview
Breadth-First Search (BFS) and Depth-First Search (DFS) are the two fundamental graph/tree traversal strategies. BFS finds shortest paths in unweighted graphs and processes nodes level-by-level. DFS explores deeply and powers topological sort, cycle detection, and connected components. Every graph problem reduces to one of these two traversals with problem-specific processing.

## Core Concepts

### BFS (Breadth-First Search)
Uses a queue. Explores all neighbors at distance $d$ before distance $d+1$.

**Properties**:
- Guarantees shortest path in unweighted graphs
- Time: $O(V + E)$, Space: $O(V)$ for the queue
- Level-order traversal of trees is BFS

### DFS (Depth-First Search)
Uses a stack (or recursion). Explores as deep as possible before backtracking.

**Properties**:
- Does NOT guarantee shortest path
- Time: $O(V + E)$, Space: $O(V)$ for recursion stack
- Three states for cycle detection: unvisited, in-progress, completed

### Multi-Source BFS
Start BFS from multiple sources simultaneously. All sources are enqueued at distance 0. Used for "distance from nearest X" problems (e.g., 01 Matrix, Rotting Oranges).

### Topological Sort (DFS-based)
For a DAG, produces a linear ordering where every edge $(u, v)$ has $u$ before $v$:
- DFS post-order, then reverse
- Or: detect cycle if a node is revisited while in-progress

$$
\text{Topological order exists} \iff \text{graph is a DAG (no cycles)}
$$

## Implementation

```python
from collections import deque

def bfs_shortest_path(graph: dict[int, list[int]], start: int,
                      end: int) -> int:
    # Shortest path in unweighted graph. Returns distance or -1.
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist
        for nei in graph[node]:
            if nei not in visited:
                visited.add(nei)
                queue.append((nei, dist + 1))
    return -1

def topological_sort(graph: dict[int, list[int]], n: int) -> list[int]:
    # Kahn's algorithm (BFS-based). Returns [] if cycle exists.
    in_degree = [0] * n
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order: list[int] = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    return order if len(order) == n else []
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| BFS shortest path | Unweighted graph distance | BFS guarantees minimum hops; add to visited when enqueuing (not dequeuing) |
| Multi-source BFS | Distance from nearest source | Enqueue all sources at once; process layer by layer |
| DFS + backtracking | Path enumeration, permutations | Mark visited on enter, unmark on exit |
| Topological sort | Task scheduling, course prerequisites | Kahn's (BFS + in-degree) or DFS post-order reverse |
| DFS cycle detection | Directed graph cycle | Three colors: white (unvisited), gray (in-progress), black (done) |
| Grid BFS/DFS | Islands, shortest path in grid | 4-directional neighbors; mark visited to avoid revisiting |

### Common Interview Questions
- [ ] Number of Islands (DFS/BFS on grid)
- [ ] Rotting Oranges (multi-source BFS)
- [ ] Course Schedule I/II (topological sort, cycle detection)
- [ ] Word Ladder (BFS for shortest transformation)
- [ ] Clone Graph (BFS/DFS with hash map)
- [ ] Pacific Atlantic Water Flow (DFS from borders)

## Comparisons

| Aspect | BFS | DFS |
|--------|-----|-----|
| Data structure | Queue | Stack / recursion |
| Shortest path (unweighted) | Yes | No |
| Space (tree) | $O(w)$ width | $O(h)$ height |
| Space (graph) | $O(V)$ | $O(V)$ |
| Cycle detection (directed) | Via in-degree (Kahn's) | Via 3-color marking |
| Best for | Shortest path, level-order | Topological sort, path existence, backtracking |

## Key Takeaways
- [ ] BFS = shortest path in unweighted graphs; DFS = explore all paths / topological ordering
- [ ] Add to visited when ENQUEUING in BFS, not when dequeuing -- avoids duplicate processing
- [ ] Multi-source BFS: enqueue all sources at distance 0 to find "nearest source" distances
- [ ] Topological sort: Kahn's algorithm (BFS) is often cleaner than DFS-based in interviews
- [ ] For MLE: BFS/DFS power graph neural network message passing, dependency resolution in ML pipelines, and knowledge graph traversal
"""

CONTENT["pillar1.algorithm_paradigms.dynamic_programming"] = r"""# Dynamic Programming

## Overview
Dynamic programming (DP) solves problems with overlapping subproblems and optimal substructure by caching subproblem results. It is arguably the most important algorithm paradigm for coding interviews -- and one of the hardest. The key skill is identifying the state, transition, and base case. For MLEs, DP appears in sequence alignment (NLP), Viterbi decoding (HMMs), and edit distance computation.

## Core Concepts

### DP Framework
Every DP problem has three components:
1. **State**: what information defines a subproblem? (e.g., `dp[i]` = best answer using first $i$ elements)
2. **Transition**: how does the answer to a subproblem relate to smaller subproblems?
3. **Base case**: what are the trivially solvable subproblems?

$$
dp[i] = f(dp[i-1], dp[i-2], \ldots) \quad \text{(recurrence relation)}
$$

### Top-Down (Memoization) vs Bottom-Up (Tabulation)
- **Top-down**: recursive with `@lru_cache`; easier to write, harder to optimize space
- **Bottom-up**: iterative, fill table from base case; enables space optimization

### Common DP Categories

| Category | State | Example |
|----------|-------|---------|
| 1D (linear) | `dp[i]` | Climbing stairs, house robber |
| 2D (grid/sequence) | `dp[i][j]` | Edit distance, LCS, unique paths |
| Knapsack | `dp[i][w]` | 0/1 knapsack, coin change, subset sum |
| Interval | `dp[i][j]` = answer for subarray $[i, j]$ | Matrix chain, burst balloons |
| Bitmask | `dp[mask]` | TSP, assignment problem |
| State machine | `dp[i][state]` | Buy/sell stock with cooldown |

### Space Optimization
When `dp[i]` depends only on `dp[i-1]` (or a fixed number of previous rows), reduce space from $O(n^2)$ to $O(n)$ or $O(1)$ by keeping only the needed rows.

## Implementation

```python
from functools import lru_cache

def longest_common_subsequence(s1: str, s2: str) -> int:
    # LCS via bottom-up DP. O(mn) time, O(n) space.
    m, n = len(s1), len(s2)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[n]

def coin_change(coins: list[int], amount: int) -> int:
    # Minimum coins to make amount. O(amount * len(coins)).
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != float("inf") else -1
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 1D DP | Sequence with local choices | Often reducible to $O(1)$ space (Fibonacci pattern) |
| 2D grid | Unique paths, min path sum | Fill row by row; can optimize to 1D if only prev row needed |
| Knapsack (0/1) | Subset selection with capacity | Inner loop backwards for 1D space optimization |
| Unbounded knapsack | Coin change, unlimited items | Inner loop forwards (items reusable) |
| LCS / edit distance | String comparison | Classic 2D DP; space optimizable to $O(\min(m,n))$ |
| State machine | Stock trading with states | Define states explicitly (holding, not holding, cooldown) |

### Common Interview Questions
- [ ] Climbing Stairs / House Robber (1D DP)
- [ ] Longest Common Subsequence
- [ ] Edit Distance (Levenshtein)
- [ ] Coin Change (minimum coins)
- [ ] 0/1 Knapsack / Partition Equal Subset Sum
- [ ] Best Time to Buy and Sell Stock (with cooldown/fee)
- [ ] Longest Increasing Subsequence ($O(n \log n)$ with binary search)
- [ ] Word Break

## Common Pitfalls
- **Wrong state definition**: if you cannot write a clear recurrence, the state is wrong. Add dimensions (e.g., add "with/without last element" as a state)
- **Not initializing base cases**: `dp[0] = ...` must be set before the loop. Missing base cases cause silent wrong answers
- **Forgetting space optimization direction**: for 0/1 knapsack in 1D, iterate capacity from HIGH to LOW; for unbounded knapsack, iterate LOW to HIGH. Reversing this gives wrong results
- **Confusing subsequence vs subarray**: subsequence = not necessarily contiguous (DP on indices); subarray = contiguous (sliding window or prefix sum often suffices)

## Key Takeaways
- [ ] Start by defining the state precisely -- a vague state definition leads to wrong transitions
- [ ] Top-down is faster to write; bottom-up enables space optimization -- know both
- [ ] 0/1 knapsack: iterate capacity backwards in 1D; unbounded: iterate forwards
- [ ] Edit distance is the canonical 2D DP and appears directly in NLP (spell correction, sequence alignment)
- [ ] For MLE: DP underpins Viterbi decoding (HMMs), CTC loss (speech recognition), beam search pruning, and sequence alignment in bioinformatics
"""

CONTENT["pillar1.algorithm_paradigms.greedy"] = r"""# Greedy

## Overview
Greedy algorithms make locally optimal choices at each step, hoping to reach a global optimum. They work when the problem has the greedy choice property (a locally optimal choice leads to a globally optimal solution) and optimal substructure. Greedy is faster than DP when applicable, but proving correctness is the hard part. For MLEs, greedy algorithms appear in feature selection, scheduling, and compression (Huffman coding).

## Core Concepts

### When Greedy Works
A greedy algorithm is correct when:
1. **Greedy choice property**: a globally optimal solution can be constructed by making locally optimal choices
2. **Optimal substructure**: an optimal solution contains optimal solutions to subproblems

**Proof techniques**:
- **Exchange argument**: show that swapping any element in the optimal solution with the greedy choice does not worsen the result
- **Stays-ahead**: show the greedy solution is at least as good as any other solution at every step

### Greedy vs Dynamic Programming
Greedy makes one choice per step without reconsidering. DP explores all choices and picks the best. If a greedy approach exists, it is always more efficient than DP.

$$
\text{Greedy} \subseteq \text{DP-solvable problems}
$$

### Common Greedy Strategies
- **Sort then greedily pick**: intervals, jobs, tasks
- **Priority queue (heap)**: always process the most urgent/valuable next
- **Two pointers**: assign resources greedily from both ends

## Implementation

```python
def min_meeting_rooms(intervals: list[list[int]]) -> int:
    # Minimum meeting rooms needed. O(n log n).
    import heapq
    intervals.sort(key=lambda x: x[0])
    heap: list[int] = []  # end times of active meetings
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heappop(heap)  # reuse room
        heapq.heappush(heap, end)
    return len(heap)

def max_non_overlapping_intervals(intervals: list[list[int]]) -> int:
    # Maximum non-overlapping intervals. O(n log n).
    intervals.sort(key=lambda x: x[1])  # sort by end time
    count = 0
    prev_end = float("-inf")
    for start, end in intervals:
        if start >= prev_end:
            count += 1
            prev_end = end
    return count

def assign_cookies(children: list[int], cookies: list[int]) -> int:
    # Assign smallest sufficient cookie to each child. O(n log n).
    children.sort()
    cookies.sort()
    child = cookie = 0
    while child < len(children) and cookie < len(cookies):
        if cookies[cookie] >= children[child]:
            child += 1
        cookie += 1
    return child
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Sort by end time | Interval scheduling (max non-overlap) | Earliest end time = most room for future intervals |
| Sort by start time + heap | Minimum resources (meeting rooms) | Heap tracks end times; reuse room if earliest end <= start |
| Sort by ratio | Fractional knapsack, job scheduling | Value-to-weight ratio maximizes total value |
| Huffman coding | Optimal prefix codes | Merge two smallest frequencies; builds optimal tree bottom-up |
| Jump game | Can reach end? / minimum jumps | Track farthest reachable position greedily |

### Common Interview Questions
- [ ] Non-overlapping Intervals (sort by end time)
- [ ] Meeting Rooms II (min rooms, heap-based)
- [ ] Task Scheduler (greedy + idle slots)
- [ ] Jump Game I and II
- [ ] Gas Station (circular greedy)
- [ ] Candy Distribution (two-pass greedy)
- [ ] Reorganize String (greedy + max-heap)

## Comparisons

| Aspect | Greedy | Dynamic Programming | Brute Force |
|--------|--------|-------------------|-------------|
| Time | Typically $O(n \log n)$ | $O(n^2)$ or $O(nW)$ | Exponential |
| Correctness | Must prove | Always correct | Always correct |
| Approach | One choice per step | All choices explored | All combinations |
| Space | Usually $O(1)$ | $O(n)$ to $O(n^2)$ | Varies |
| When to use | Greedy choice property holds | Overlapping subproblems | Small input |

## Key Takeaways
- [ ] Sorting is almost always the first step in greedy interval/scheduling problems
- [ ] Sort by end time for "maximum non-overlapping" and by start time + heap for "minimum resources"
- [ ] If a greedy approach seems to work, verify with the exchange argument before coding
- [ ] If greedy fails on a counterexample, switch to DP -- many problems look greedy but are not
- [ ] For MLE: greedy powers forward feature selection, Huffman coding in compression, and greedy decoding in language models
"""

CONTENT["pillar1.algorithm_paradigms.backtracking"] = r"""# Backtracking

## Overview
Backtracking systematically explores all candidate solutions by incrementally building choices and abandoning ("pruning") branches that cannot lead to valid solutions. It is the go-to approach for combinatorial problems: permutations, combinations, subsets, N-Queens, and constraint satisfaction. For MLEs, backtracking underlies beam search variants, constraint-based feature selection, and hyperparameter grid search.

## Core Concepts

### Backtracking Framework
Every backtracking problem follows this template:
1. **Choose**: make a decision (add element to current path)
2. **Explore**: recurse with the choice made
3. **Unchoose**: undo the decision (backtrack)

$$
\text{Prune: if current state violates constraints, return early (do not recurse)}
$$

### Time Complexity
Backtracking explores a decision tree. Without pruning:
- Permutations of $n$ elements: $O(n!)$
- Subsets of $n$ elements: $O(2^n)$
- Combinations of $k$ from $n$: $O(\binom{n}{k})$

Pruning reduces the constant factor but not the worst-case complexity.

### Pruning Strategies
- **Constraint check**: skip choices that violate constraints immediately
- **Sorting + skip duplicates**: sort input, skip `if i > start and nums[i] == nums[i-1]`
- **Bound estimation**: if remaining elements cannot improve best solution, prune (branch and bound)

## Implementation

```python
def subsets(nums: list[int]) -> list[list[int]]:
    # Generate all subsets. O(2^n).
    result: list[list[int]] = []
    def backtrack(start: int, path: list[int]) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return result

def permutations(nums: list[int]) -> list[list[int]]:
    # Generate all permutations. O(n!).
    result: list[list[int]] = []
    def backtrack(path: list[int], used: set[int]) -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if i in used:
                continue
            used.add(i)
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used.discard(i)
    backtrack([], set())
    return result

def solve_n_queens(n: int) -> int:
    # Count N-Queens solutions. Prune by column and diagonals.
    count = 0
    cols: set[int] = set()
    diag1: set[int] = set()  # row - col
    diag2: set[int] = set()  # row + col
    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if col in cols or row - col in diag1 or row + col in diag2:
                continue
            cols.add(col); diag1.add(row - col); diag2.add(row + col)
            backtrack(row + 1)
            cols.discard(col); diag1.discard(row - col); diag2.discard(row + col)
    backtrack(0)
    return count
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Subsets | Generate all subsets | Start index controls inclusion; choose to include or skip each element |
| Permutations | All orderings | Use `used` set or swap-based approach |
| Combinations | Choose $k$ from $n$ | Like subsets but stop when path length = $k$ |
| Constraint satisfaction | N-Queens, Sudoku | Track constraints in sets for $O(1)$ validity check |
| Word search / path | Find word in grid | DFS + backtracking with visited marking |
| Palindrome partitioning | Partition string into palindromes | Choose each valid palindrome prefix, recurse on remainder |

### Common Interview Questions
- [ ] Subsets / Subsets II (with duplicates)
- [ ] Permutations / Permutations II (with duplicates)
- [ ] Combination Sum (unlimited use) / Combination Sum II (each once)
- [ ] N-Queens
- [ ] Word Search (grid path finding)
- [ ] Palindrome Partitioning
- [ ] Generate Parentheses

## Comparisons

| Aspect | Backtracking | BFS/DFS | Dynamic Programming |
|--------|-------------|---------|-------------------|
| Goal | All valid solutions | Traversal/shortest path | Optimal value |
| Pruning | Yes (key advantage) | Limited | N/A (all states computed) |
| Space | $O(n)$ recursion depth | $O(V)$ | $O(\text{state space})$ |
| When to use | Enumerate combinations | Graph traversal | Optimization with overlapping subproblems |

## Key Takeaways
- [ ] Master the choose-explore-unchoose template -- it applies to nearly all combinatorial problems
- [ ] Handle duplicates: sort the array, skip `nums[i] == nums[i-1]` when `i > start`
- [ ] N-Queens: track columns and both diagonals in sets for $O(1)$ constraint checking
- [ ] Backtracking explores exponential spaces -- pruning is the difference between TLE and AC
- [ ] For MLE: backtracking powers constraint-based search in AutoML, beam search with pruning in NLP, and combinatorial optimization in feature selection
"""

CONTENT["pillar1.algorithm_paradigms.graph_algorithms"] = r"""# Graph Algorithms

## Overview
Graphs model relationships and networks -- from social networks to ML computation graphs. Beyond BFS/DFS (covered separately), key graph algorithms include shortest path (Dijkstra, Bellman-Ford), minimum spanning tree (Kruskal, Prim), and strongly connected components. For MLEs, graphs are central to knowledge graphs, GNNs, dependency resolution in ML pipelines, and network analysis.

## Core Concepts

### Graph Representations

| Representation | Space | Edge lookup | Best for |
|---------------|-------|------------|---------|
| Adjacency list | $O(V + E)$ | $O(\text{degree})$ | Sparse graphs (most real-world) |
| Adjacency matrix | $O(V^2)$ | $O(1)$ | Dense graphs, matrix operations |
| Edge list | $O(E)$ | $O(E)$ | Kruskal's, simple iteration |

### Dijkstra's Algorithm
Shortest path from source to all vertices in a weighted graph with non-negative weights:

$$
\text{dist}[v] = \min_{(u,v) \in E}(\text{dist}[u] + w(u,v))
$$

Time: $O((V + E) \log V)$ with min-heap. Does NOT work with negative weights.

### Bellman-Ford Algorithm
Handles negative weights. Relaxes all edges $V - 1$ times:

$$
\text{For each edge } (u, v, w): \quad \text{dist}[v] = \min(\text{dist}[v], \text{dist}[u] + w)
$$

Time: $O(VE)$. Detects negative cycles (if relaxation improves after $V-1$ iterations).

### Minimum Spanning Tree
Connects all vertices with minimum total edge weight:
- **Kruskal's**: sort edges, greedily add if no cycle (union-find). $O(E \log E)$
- **Prim's**: grow tree from a vertex, always add cheapest edge to a new vertex (heap). $O((V+E) \log V)$

## Implementation

```python
import heapq
from collections import defaultdict

def dijkstra(graph: dict[int, list[tuple[int, int]]],
             start: int) -> dict[int, int]:
    # Shortest paths from start. graph[u] = [(v, weight), ...].
    dist: dict[int, int] = {start: 0}
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue  # stale entry (lazy deletion)
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist

def kruskal_mst(n: int, edges: list[tuple[int, int, int]]) -> int:
    # MST weight using Kruskal's. edges = [(u, v, w), ...].
    edges.sort(key=lambda e: e[2])
    parent = list(range(n))
    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    total = count = 0
    for u, v, w in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            count += 1
            if count == n - 1:
                break
    return total
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Dijkstra | Shortest path, non-negative weights | Lazy deletion: skip if popped distance > recorded distance |
| Bellman-Ford | Negative weights, cheapest flight with k stops | Relax all edges $V-1$ times; copy dist array for k-stop variant |
| Kruskal + Union-Find | MST, minimum cost to connect | Sort edges + union-find; stop at $V-1$ edges |
| Topological sort + DP | Shortest/longest path in DAG | Process in topo order; relax edges |
| Floyd-Warshall | All-pairs shortest path | $O(V^3)$; useful for small graphs |
| Bipartite check | Graph coloring, matching | BFS/DFS with 2-coloring |

### Common Interview Questions
- [ ] Network Delay Time (Dijkstra)
- [ ] Cheapest Flights Within K Stops (Bellman-Ford variant)
- [ ] Minimum Spanning Tree (Kruskal or Prim)
- [ ] Course Schedule (topological sort -- see BFS/DFS topic)
- [ ] Is Graph Bipartite?
- [ ] Minimum Cost to Connect All Points

## Comparisons

| Algorithm | Time | Negative weights | Use case |
|-----------|------|-----------------|----------|
| Dijkstra | $O((V+E) \log V)$ | No | Single-source, non-negative |
| Bellman-Ford | $O(VE)$ | Yes | Single-source, negative weights |
| Floyd-Warshall | $O(V^3)$ | Yes (no neg cycles) | All-pairs |
| Kruskal | $O(E \log E)$ | N/A | MST |
| Prim | $O((V+E) \log V)$ | N/A | MST (dense graphs) |

## Key Takeaways
- [ ] Dijkstra with lazy deletion (skip stale heap entries) is the cleanest interview implementation
- [ ] Kruskal's = sort edges + union-find; Prim's = grow from vertex + heap. Both give MST
- [ ] Bellman-Ford: for "cheapest with at most K stops," copy distance array between rounds
- [ ] Always clarify: directed/undirected, weighted/unweighted, negative weights possible?
- [ ] For MLE: graph algorithms power GNN message passing (BFS-like), computation graph optimization (topo sort), and network flow in recommendation systems
"""

CONTENT["pillar1.algorithm_paradigms.divide_and_conquer"] = r"""# Divide & Conquer

## Overview
Divide and conquer splits a problem into independent subproblems, solves each recursively, and combines results. Classic examples include merge sort, quicksort, and binary search (covered separately). For interviews, the key is recognizing when a problem has independent subproblems that can be combined efficiently. For MLEs, D&C appears in parallel training (data parallelism), MapReduce, and recursive feature elimination.

## Core Concepts

### D&C Framework
1. **Divide**: split problem into smaller subproblems
2. **Conquer**: solve subproblems recursively (base case for small inputs)
3. **Combine**: merge subproblem solutions into the final answer

### Master Theorem
For recurrences of the form $T(n) = aT(n/b) + O(n^d)$:

$$
T(n) = \begin{cases}
O(n^d) & \text{if } d > \log_b a \\
O(n^d \log n) & \text{if } d = \log_b a \\
O(n^{\log_b a}) & \text{if } d < \log_b a
\end{cases}
$$

**Examples**:
- Merge sort: $T(n) = 2T(n/2) + O(n) \Rightarrow O(n \log n)$ (case 2: $a=2, b=2, d=1$)
- Binary search: $T(n) = T(n/2) + O(1) \Rightarrow O(\log n)$ (case 1: $a=1, b=2, d=0$)
- Strassen: $T(n) = 7T(n/2) + O(n^2) \Rightarrow O(n^{\log_2 7}) \approx O(n^{2.81})$ (case 3)

### Merge Sort: The Canonical D&C Example
Divide array in half, sort each half, merge in $O(n)$. Always $O(n \log n)$, stable, but $O(n)$ extra space.

### Quick Select
Find the $k$-th smallest element in $O(n)$ expected time using randomized partition:
- Partition around a random pivot
- Recurse only on the half containing the target index

$$
T(n) = T(n/2) + O(n) \Rightarrow O(n) \text{ expected}
$$

## Implementation

```python
def merge_sort(arr: list[int]) -> list[int]:
    # Merge sort. O(n log n) time, O(n) space.
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)

def _merge(a: list[int], b: list[int]) -> list[int]:
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result

def quick_select(nums: list[int], k: int) -> int:
    # Find k-th smallest (0-indexed). O(n) expected.
    import random
    if len(nums) == 1:
        return nums[0]
    pivot = random.choice(nums)
    lo = [x for x in nums if x < pivot]
    eq = [x for x in nums if x == pivot]
    hi = [x for x in nums if x > pivot]
    if k < len(lo):
        return quick_select(lo, k)
    elif k < len(lo) + len(eq):
        return pivot
    else:
        return quick_select(hi, k - len(lo) - len(eq))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Merge sort variants | Count inversions, sort linked list | Counting during merge step captures cross-partition relationships |
| Quick select | Kth largest/smallest | $O(n)$ average; randomize pivot to avoid worst case |
| Divide array in half | Closest pair of points, max subarray | Combine step is the crux -- often $O(n)$ or $O(n \log n)$ |
| Recursive matrix ops | Matrix multiplication (Strassen) | Reduce 8 multiplications to 7 for $O(n^{2.81})$ |
| Tree recursion as D&C | Most tree problems | Left/right subtrees are independent subproblems |

### Common Interview Questions
- [ ] Merge Sort (implementation + stability analysis)
- [ ] Kth Largest Element (quick select)
- [ ] Count of Smaller Numbers After Self (merge sort + count inversions)
- [ ] Maximum Subarray (D&C approach, compare with Kadane's)
- [ ] Sort List (merge sort on linked list -- $O(1)$ extra space)
- [ ] Median of Two Sorted Arrays ($O(\log \min(m,n))$ D&C)

## Comparisons

| Aspect | Merge Sort | Quick Sort | Quick Select |
|--------|-----------|------------|-------------|
| Time (avg) | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ |
| Time (worst) | $O(n \log n)$ | $O(n^2)$ | $O(n^2)$ |
| Space | $O(n)$ | $O(\log n)$ stack | $O(n)$ |
| Stable | Yes | No (standard) | N/A |
| In-place | No | Yes | Depends |

## Key Takeaways
- [ ] Know the Master Theorem to quickly analyze D&C recurrence complexity
- [ ] Merge sort is the go-to stable $O(n \log n)$ sort; the merge step is reusable for counting problems
- [ ] Quick select gives $O(n)$ expected k-th element -- always randomize the pivot
- [ ] The "combine" step is usually the hardest part of D&C -- focus your analysis there
- [ ] For MLE: D&C underpins data-parallel training (split batch across GPUs, average gradients), MapReduce for distributed feature engineering, and recursive partitioning in decision trees
"""

# ===== MLE-SPECIFIC CODING =====

CONTENT["pillar1.mle_coding.matrix_tensor_ops"] = r"""# Matrix / Tensor Operations

## Overview
Matrix and tensor operations are the computational backbone of machine learning. Every forward pass, backpropagation step, and data transformation involves matrix multiplications, reshapes, and element-wise operations. MLE interviews frequently test NumPy/PyTorch fluency, broadcasting rules, and the ability to vectorize loops. Understanding these operations at a low level is essential for optimizing ML systems.

## Core Concepts

### Matrix Multiplication
For matrices $A \in \mathbb{R}^{m \times k}$ and $B \in \mathbb{R}^{k \times n}$:

$$
C = AB, \quad C_{ij} = \sum_{l=1}^{k} A_{il} B_{lj}
$$

Complexity: $O(mkn)$. In practice, BLAS libraries (MKL, cuBLAS) achieve near-peak FLOPS through cache-optimized tiling.

### Broadcasting Rules (NumPy/PyTorch)
When operating on arrays of different shapes, dimensions are compared from the trailing end:
1. Dimensions are compatible if they are equal or one of them is 1
2. Missing dimensions are treated as size 1 (prepended)
3. Size-1 dimensions are stretched to match the other

$$
(3, 4, 1) \odot (1, 4, 5) \to (3, 4, 5)
$$

### Key Tensor Operations

| Operation | NumPy | PyTorch | Notes |
|-----------|-------|---------|-------|
| Matrix multiply | `A @ B` or `np.matmul` | `torch.matmul` | Handles batched dims |
| Element-wise | `A * B` | `A * B` | Broadcasting applies |
| Transpose | `A.T` or `np.swapaxes` | `A.T` or `.permute` | `.T` for 2D only |
| Reshape | `A.reshape(m, n)` | `A.view(m, n)` | `view` requires contiguous memory |
| Reduce | `np.sum(A, axis=0)` | `A.sum(dim=0)` | Keepdim for broadcasting |

### Einsum Notation
Einstein summation provides a concise, general interface for tensor contractions:

```
np.einsum('ij,jk->ik', A, B)  # matrix multiply
np.einsum('bij,bjk->bik', A, B)  # batched matmul
np.einsum('ij->j', A)  # column sum
np.einsum('ii->', A)  # trace
```

## Implementation

```python
import numpy as np

def softmax(x: np.ndarray) -> np.ndarray:
    # Numerically stable softmax along last axis.
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)

def batch_cosine_similarity(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    # Cosine similarity between rows of A and B. O(n*d).
    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
    B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
    return A_norm @ B_norm.T  # (n, m) similarity matrix

def attention_scores(Q: np.ndarray, K: np.ndarray,
                     V: np.ndarray) -> np.ndarray:
    # Scaled dot-product attention. Q,K,V shape: (seq, d_k).
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)  # (seq, seq)
    weights = softmax(scores)
    return weights @ V  # (seq, d_v)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Vectorized distance | Pairwise distances, similarity | Use broadcasting: $(A - B)^2$ with shape manipulation |
| Numerical stability | Softmax, log-sum-exp | Subtract max before exp to prevent overflow |
| Batched operations | Process multiple samples | Add batch dimension; use `einsum` or batch matmul |
| Reshape for broadcast | Feature-target interaction | Reshape to align dimensions, then element-wise multiply |
| In-place operations | Memory efficiency | Use `out=` parameter or in-place operators where possible |

### Common Interview Questions
- [ ] Implement softmax (numerically stable)
- [ ] Implement attention mechanism (scaled dot-product)
- [ ] Compute pairwise Euclidean distances without loops
- [ ] Implement batch normalization (forward pass)
- [ ] Vectorize a nested loop computation using broadcasting
- [ ] Explain and use einsum for a given tensor contraction

## Comparisons

| Aspect | For loops | Vectorized (NumPy) | GPU (PyTorch) |
|--------|----------|-------------------|---------------|
| Speed (1M elements) | Seconds | Milliseconds | Microseconds |
| Memory control | Fine-grained | Intermediate copies | GPU memory limits |
| Debugging | Easy | Moderate (shape errors) | Hard (async) |
| Best for | Prototyping | CPU production | Training/inference |

## Key Takeaways
- [ ] Always vectorize: replace Python loops with NumPy/PyTorch operations for 100-1000x speedup
- [ ] Broadcasting rules: align from trailing dimension; size-1 stretches to match
- [ ] Numerical stability: subtract max before exp (softmax), use log-sum-exp instead of log(sum(exp))
- [ ] Einsum is the universal tool for tensor contractions -- learn the notation
- [ ] For interviews: be ready to implement softmax, attention, cosine similarity, and batch norm from scratch using only NumPy
"""

CONTENT["pillar1.mle_coding.implement_ml_algorithms"] = r"""# Implement ML Algorithms from Scratch

## Overview
Implementing ML algorithms from scratch is a core MLE interview skill that tests understanding beyond API calls. Interviewers want to see that you understand the math, can translate it to code, handle edge cases, and reason about convergence. Common targets: linear regression, logistic regression, k-means, KNN, decision tree, and gradient descent. Focus on clean, correct implementations over optimization.

## Core Concepts

### Gradient Descent
The foundation of most ML optimization. Update rule:

$$
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
$$

**Variants**:
- **Batch GD**: use all samples per update. Stable but slow for large datasets
- **SGD**: one sample per update. Noisy but fast
- **Mini-batch**: compromise. Standard in practice (batch size 32-256)

### K-Means Clustering
Iterative algorithm:
1. Initialize $k$ centroids (random or k-means++)
2. Assign each point to nearest centroid: $c_i = \arg\min_j \|x_i - \mu_j\|^2$
3. Update centroids: $\mu_j = \frac{1}{|C_j|}\sum_{x \in C_j} x$
4. Repeat until convergence

$$
\text{Objective: } J = \sum_{j=1}^{k} \sum_{x \in C_j} \|x - \mu_j\|^2
$$

### Decision Tree (CART)
For each node, find the best split:

$$
\text{Best split} = \arg\min_{f, t} \left[ \frac{|L|}{|N|} G(L) + \frac{|R|}{|N|} G(R) \right]
$$

where $G$ is Gini impurity or entropy, $f$ is the feature, $t$ is the threshold.

### K-Nearest Neighbors
Classification: majority vote of $k$ nearest neighbors. Regression: average.
Distance metric matters: Euclidean ($L_2$), Manhattan ($L_1$), or cosine.

## Implementation

```python
import numpy as np

class KMeans:
    def __init__(self, k: int, max_iters: int = 100) -> None:
        self.k = k
        self.max_iters = max_iters

    def fit(self, X: np.ndarray) -> "KMeans":
        idx = np.random.choice(len(X), self.k, replace=False)
        self.centroids = X[idx]
        for _ in range(self.max_iters):
            dists = np.linalg.norm(
                X[:, None] - self.centroids[None, :], axis=2
            )  # (n, k)
            labels = np.argmin(dists, axis=1)
            new_centroids = np.array([
                X[labels == j].mean(axis=0) if np.any(labels == j)
                else self.centroids[j]
                for j in range(self.k)
            ])
            if np.allclose(new_centroids, self.centroids):
                break
            self.centroids = new_centroids
        self.labels_ = labels
        return self

class LogisticRegressionScratch:
    def fit(self, X: np.ndarray, y: np.ndarray,
            lr: float = 0.01, epochs: int = 1000) -> "LogisticRegressionScratch":
        n, d = X.shape
        self.w = np.zeros(d)
        self.b = 0.0
        for _ in range(epochs):
            z = X @ self.w + self.b
            pred = 1 / (1 + np.exp(-z))
            self.w -= lr * (X.T @ (pred - y)) / n
            self.b -= lr * np.mean(pred - y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-(X @ self.w + self.b)))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Gradient descent loop | Any differentiable loss | Compute gradient analytically; vectorize over samples |
| Distance matrix | KNN, k-means | Broadcasting: `X[:, None] - centroids[None, :]` for all pairwise |
| Recursive splitting | Decision tree | Recurse on left/right subsets; track depth for stopping |
| Convergence check | Iterative algorithms | Check parameter change or loss change < epsilon |
| Numerical stability | Sigmoid, softmax | Clip inputs or use log-space computation |

### Common Interview Questions
- [ ] Implement linear regression with gradient descent
- [ ] Implement logistic regression from scratch
- [ ] Implement k-means clustering
- [ ] Implement KNN classifier
- [ ] Implement a simple decision tree (Gini or entropy splitting)
- [ ] Implement gradient descent with momentum

## Comparisons

| Algorithm | Training Time | Prediction Time | Handles Nonlinearity |
|-----------|-------------|----------------|---------------------|
| Linear Regression | $O(nd)$ per epoch | $O(d)$ | No |
| Logistic Regression | $O(nd)$ per epoch | $O(d)$ | No (linear boundary) |
| KNN | None (lazy) | $O(nd)$ | Yes |
| K-Means | $O(nkd)$ per iter | $O(kd)$ | No (spherical clusters) |
| Decision Tree | $O(n d \log n)$ | $O(\text{depth})$ | Yes |

## Key Takeaways
- [ ] Know the loss function AND its gradient for each algorithm -- interviewers will ask you to derive it
- [ ] Vectorize everything: avoid Python for-loops over samples; use matrix operations
- [ ] Handle edge cases: empty clusters in k-means, perfect separation in logistic regression, single-class leaves in trees
- [ ] K-means++ initialization matters in practice -- mention it even if you implement random init
- [ ] For MLE interviews: be ready to extend basic implementations (add regularization, mini-batching, early stopping)
"""

CONTENT["pillar1.mle_coding.data_processing_pipeline"] = r"""# Data Processing Pipeline

## Overview
Data processing is where MLEs spend the majority of their time. Interview questions test your ability to write clean, efficient data transformations using pandas, SQL, or pure Python. Key skills include handling missing values, feature engineering, join operations, and writing scalable pipelines. These problems are more practical than algorithmic and directly assess day-to-day MLE competence.

## Core Concepts

### Data Cleaning Patterns
- **Missing values**: detect with `isna()`, handle with imputation (mean, median, mode, forward-fill) or removal
- **Duplicates**: `drop_duplicates(subset=[...], keep='first')`
- **Type coercion**: ensure numeric columns are numeric, datetime parsing
- **Outlier handling**: clip to percentiles, z-score filtering, IQR method

### Feature Engineering

| Technique | When to Use | Implementation |
|-----------|------------|----------------|
| One-hot encoding | Low-cardinality categorical | `pd.get_dummies()` or `sklearn.OneHotEncoder` |
| Target encoding | High-cardinality categorical | Mean of target per category (with smoothing) |
| Binning | Continuous to categorical | `pd.cut()` or `pd.qcut()` for equal-frequency |
| Log transform | Right-skewed features | `np.log1p()` (handles zeros) |
| Interaction features | Feature combinations | `f1 * f2`, polynomial features |
| Time features | Datetime columns | Extract hour, day_of_week, is_weekend, time_since_event |

### Aggregation and Window Functions
GroupBy + aggregation is the core of feature engineering from transactional data:

$$
\text{user\_avg\_spend} = \frac{1}{|T_u|} \sum_{t \in T_u} \text{amount}_t
$$

Window functions (rolling, expanding) for time-series features.

### Efficient Processing
- **Chunked reading**: `pd.read_csv(..., chunksize=10000)` for large files
- **Vectorized operations**: avoid `iterrows()`; use vectorized pandas/numpy
- **Memory optimization**: downcast dtypes (`int64` -> `int32`), categorical type for strings

## Implementation

```python
import pandas as pd
import numpy as np

def build_user_features(transactions: pd.DataFrame) -> pd.DataFrame:
    # Aggregate transaction features per user.
    features = transactions.groupby("user_id").agg(
        total_spend=("amount", "sum"),
        avg_spend=("amount", "mean"),
        num_transactions=("amount", "count"),
        days_since_last=("date", lambda x: (pd.Timestamp.now() - x.max()).days),
        unique_merchants=("merchant_id", "nunique"),
    ).reset_index()
    return features

def handle_missing(df: pd.DataFrame,
                   numeric_strategy: str = "median") -> pd.DataFrame:
    # Impute missing values. Numeric: median/mean. Categorical: mode.
    df = df.copy()
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].isna().any():
            fill_val = df[col].median() if numeric_strategy == "median" else df[col].mean()
            df[col] = df[col].fillna(fill_val)
    for col in df.select_dtypes(include=["object", "category"]).columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode()[0])
    return df

def create_time_features(df: pd.DataFrame,
                         date_col: str) -> pd.DataFrame:
    # Extract temporal features from a datetime column.
    df = df.copy()
    dt = pd.to_datetime(df[date_col])
    df["hour"] = dt.dt.hour
    df["day_of_week"] = dt.dt.dayofweek
    df["is_weekend"] = (dt.dt.dayofweek >= 5).astype(int)
    df["month"] = dt.dt.month
    return df
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| GroupBy + agg | User/item-level features | Define named aggregations for clarity |
| Window functions | Rolling averages, cumulative sums | `df.rolling(7).mean()` for 7-day moving average |
| Merge/Join | Combine tables | Know left, inner, outer joins; watch for key duplication |
| Pivot / melt | Reshape data | Pivot: long to wide; melt: wide to long |
| Apply + vectorize | Custom transformations | Prefer vectorized ops; `apply` is a last resort |

### Common Interview Questions
- [ ] Clean a messy dataset (missing values, duplicates, type errors)
- [ ] Build aggregated features from transaction logs
- [ ] Implement a feature engineering pipeline for a recommendation system
- [ ] Write SQL to compute user retention metrics
- [ ] Handle class imbalance in a dataset (SMOTE, undersampling, class weights)
- [ ] Design a data validation pipeline (schema checks, distribution drift)

## Comparisons

| Aspect | Pandas | SQL | PySpark |
|--------|--------|-----|---------|
| Scale | Single machine (<10GB) | Database-dependent | Distributed (TB+) |
| Syntax | Python API | Declarative | DataFrame API (similar to pandas) |
| Joins | `merge()` | `JOIN` | `join()` or SQL |
| Window functions | `rolling`, `expanding` | `OVER (PARTITION BY ... ORDER BY ...)` | Same as SQL |
| Best for | EDA, prototyping | Production queries | Large-scale ETL |

## Key Takeaways
- [ ] Never use `iterrows()` -- vectorize with pandas/numpy operations for 100x+ speedup
- [ ] GroupBy + agg is the most important pandas pattern for feature engineering
- [ ] Always handle missing values explicitly -- document your imputation strategy
- [ ] Log-transform skewed features and standardize before modeling
- [ ] For MLE interviews: be fluent in both pandas and SQL; expect to write both in the same interview
"""

CONTENT["pillar1.mle_coding.sampling_algorithms"] = r"""# Sampling Algorithms

## Overview
Sampling algorithms are essential for MLEs working with large datasets, probabilistic models, and Monte Carlo methods. Interview questions test reservoir sampling (stream processing), weighted sampling, MCMC basics, and the ability to generate samples from complex distributions. These skills directly apply to training data sampling, A/B test analysis, and generative modeling.

## Core Concepts

### Reservoir Sampling
Sample $k$ items uniformly at random from a stream of unknown length $n$:

For the $i$-th element (1-indexed), include it with probability $k/i$. If included, replace a random element in the reservoir.

$$
P(\text{item } i \text{ in final sample}) = \frac{k}{n} \quad \forall i \in [1, n]
$$

**Proof**: by induction. Item $i$ is selected with probability $k/i$ and survives all subsequent steps with probability $\prod_{j=i+1}^{n} (1 - \frac{1}{j} \cdot \frac{k}{k}) = \frac{i}{n}$. Combined: $\frac{k}{i} \cdot \frac{i}{n} = \frac{k}{n}$.

### Weighted Random Sampling
Sample from a discrete distribution with weights $w_1, \ldots, w_n$:
- **CDF method**: build cumulative distribution, binary search for random uniform
- **Alias method**: $O(n)$ preprocessing, $O(1)$ per sample

$$
P(\text{select } i) = \frac{w_i}{\sum_j w_j}
$$

### Rejection Sampling
To sample from target distribution $p(x)$ using proposal $q(x)$ where $Mq(x) \ge p(x)$:
1. Sample $x \sim q(x)$
2. Accept with probability $\frac{p(x)}{Mq(x)}$; otherwise reject and repeat

Efficiency: $1/M$ acceptance rate. Choosing tight $M$ is critical.

### Importance Sampling
Estimate $E_{p}[f(x)]$ using samples from a different distribution $q(x)$:

$$
E_{p}[f(x)] = E_{q}\left[\frac{p(x)}{q(x)} f(x)\right] \approx \frac{1}{n}\sum_{i=1}^{n} \frac{p(x_i)}{q(x_i)} f(x_i)
$$

Used in off-policy RL evaluation, rare event estimation, and particle filters.

## Implementation

```python
import random
import bisect
import numpy as np

def reservoir_sample(stream, k: int) -> list:
    # Reservoir sampling: k items from stream of unknown length.
    reservoir = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir

def weighted_random_choice(values: list, weights: list[float]) -> object:
    # Weighted sampling using CDF + binary search. O(log n) per sample.
    cumulative = []
    total = 0.0
    for w in weights:
        total += w
        cumulative.append(total)
    r = random.uniform(0, total)
    return values[bisect.bisect_left(cumulative, r)]

def rejection_sample_circle(n: int) -> list[tuple[float, float]]:
    # Sample n points uniformly inside unit circle via rejection.
    points = []
    while len(points) < n:
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        if x * x + y * y <= 1:
            points.append((x, y))
    return points
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Reservoir sampling | Stream of unknown length | Include $i$-th item with probability $k/i$; replace random slot |
| CDF + binary search | Weighted sampling, few samples | Build prefix sum of weights; `bisect_left` for $O(\log n)$ |
| Alias method | Weighted sampling, many samples | $O(n)$ setup, $O(1)$ per sample; optimal for repeated sampling |
| Rejection sampling | Complex distributions | Accept/reject with ratio $p(x)/(Mq(x))$; efficiency = $1/M$ |
| Fisher-Yates shuffle | Random permutation | Swap each position with a random later position; $O(n)$ |

### Common Interview Questions
- [ ] Implement reservoir sampling and prove uniformity
- [ ] Random number in weighted distribution (CDF approach)
- [ ] Shuffle an array uniformly (Fisher-Yates)
- [ ] Sample from a circle uniformly (rejection sampling)
- [ ] Implement random pick with weight (LC 528)
- [ ] Explain importance sampling and when it fails (high variance)

## Comparisons

| Method | Preprocessing | Per-sample | Memory | Use case |
|--------|--------------|-----------|--------|----------|
| CDF + bisect | $O(n)$ | $O(\log n)$ | $O(n)$ | General weighted sampling |
| Alias method | $O(n)$ | $O(1)$ | $O(n)$ | Many samples from fixed distribution |
| Rejection | None | $O(1/\text{acceptance})$ | $O(1)$ | Continuous distributions |
| Reservoir | None (streaming) | $O(1)$ per item | $O(k)$ | Stream processing |
| MCMC | Burn-in period | $O(1)$ | $O(1)$ | High-dimensional distributions |

## Key Takeaways
- [ ] Reservoir sampling is the go-to for streaming uniform sampling -- know the proof of uniformity
- [ ] Weighted sampling: CDF + binary search for simplicity; alias method for performance
- [ ] Rejection sampling: easy to implement but inefficient if proposal poorly matches target
- [ ] Fisher-Yates shuffle: swap `arr[i]` with `arr[randint(i, n-1)]` for each $i$ -- produces uniform permutations
- [ ] For MLE: sampling algorithms power mini-batch SGD (uniform), negative sampling (Word2Vec), Thompson sampling (bandits), and MCMC (Bayesian inference)
"""

CONTENT["pillar1.mle_coding.neural_network_components"] = r"""# Implement Neural Network Components

## Overview
Implementing neural network components from scratch demonstrates deep understanding of how deep learning frameworks work under the hood. MLE interviews frequently ask candidates to implement forward and backward passes for common layers (linear, softmax, batch norm, attention) using only NumPy. This tests both mathematical understanding and coding ability -- the combination that distinguishes senior MLEs.

## Core Concepts

### Forward and Backward Pass
Every layer implements:
- **Forward**: $y = f(x; \theta)$ -- compute output from input
- **Backward**: given $\frac{\partial L}{\partial y}$, compute $\frac{\partial L}{\partial x}$ (for chain rule) and $\frac{\partial L}{\partial \theta}$ (for parameter update)

$$
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial x} \quad \text{(chain rule)}
$$

### Linear Layer
Forward: $y = xW + b$ where $x \in \mathbb{R}^{n \times d_{in}}$, $W \in \mathbb{R}^{d_{in} \times d_{out}}$

Backward:
$$
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} W^T, \quad
\frac{\partial L}{\partial W} = x^T \frac{\partial L}{\partial y}, \quad
\frac{\partial L}{\partial b} = \sum_i \frac{\partial L}{\partial y_i}
$$

### Batch Normalization
Normalize activations: $\hat{x} = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}}$, then scale and shift: $y = \gamma \hat{x} + \beta$

During training: use batch statistics. During inference: use running averages.

### Cross-Entropy Loss
For softmax output $\hat{y}$ and one-hot target $y$:

$$
L = -\sum_i y_i \log \hat{y}_i, \quad \frac{\partial L}{\partial z_i} = \hat{y}_i - y_i \quad \text{(combined softmax + CE gradient)}
$$

### Attention Mechanism
Scaled dot-product attention:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V
$$

## Implementation

```python
import numpy as np

class Linear:
    def __init__(self, d_in: int, d_out: int) -> None:
        self.W = np.random.randn(d_in, d_out) * np.sqrt(2.0 / d_in)
        self.b = np.zeros(d_out)

    def forward(self, x: np.ndarray) -> np.ndarray:
        self.x = x  # cache for backward
        return x @ self.W + self.b

    def backward(self, grad_y: np.ndarray) -> np.ndarray:
        self.grad_W = self.x.T @ grad_y
        self.grad_b = grad_y.sum(axis=0)
        return grad_y @ self.W.T

def relu_forward(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)

def relu_backward(x: np.ndarray, grad_y: np.ndarray) -> np.ndarray:
    return grad_y * (x > 0)

def softmax_cross_entropy(logits: np.ndarray,
                          labels: np.ndarray) -> tuple[float, np.ndarray]:
    # Combined softmax + cross-entropy. labels: one-hot (n, C).
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp_scores = np.exp(shifted)
    probs = exp_scores / exp_scores.sum(axis=1, keepdims=True)
    n = logits.shape[0]
    loss = -np.sum(labels * np.log(probs + 1e-12)) / n
    grad = (probs - labels) / n
    return loss, grad
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Forward + backward | Any layer implementation | Cache inputs in forward for use in backward |
| Numerical gradient check | Verify backward pass | $\frac{f(x+h) - f(x-h)}{2h}$ should match analytic gradient |
| Combined softmax + CE | Classification loss | Gradient simplifies to $\hat{y} - y$ when combined |
| He initialization | ReLU networks | $W \sim \mathcal{N}(0, 2/d_{in})$ prevents vanishing/exploding gradients |
| Batch norm forward/backward | Normalize activations | Track running mean/var for inference mode |

### Common Interview Questions
- [ ] Implement a linear layer (forward + backward)
- [ ] Implement softmax + cross-entropy loss (combined gradient)
- [ ] Implement batch normalization (forward pass, training vs inference)
- [ ] Implement dropout (training vs inference behavior)
- [ ] Implement scaled dot-product attention
- [ ] Implement a simple 2-layer MLP with training loop
- [ ] Derive and implement the backward pass for a convolutional layer

## Comparisons

| Component | Forward Complexity | Backward Complexity | Key Pitfall |
|-----------|-------------------|-------------------|-------------|
| Linear | $O(n \cdot d_{in} \cdot d_{out})$ | Same as forward | Forgetting to cache input |
| ReLU | $O(n \cdot d)$ | $O(n \cdot d)$ | Gradient is 0 for $x \le 0$ (dying ReLU) |
| Softmax | $O(n \cdot C)$ | $O(n \cdot C)$ | Numerical overflow without max subtraction |
| Batch Norm | $O(n \cdot d)$ | $O(n \cdot d)$ | Different behavior train vs eval |
| Attention | $O(n^2 \cdot d)$ | $O(n^2 \cdot d)$ | Missing $\sqrt{d_k}$ scaling |

## Key Takeaways
- [ ] Always cache forward pass inputs/intermediates for backward pass computation
- [ ] Combined softmax + cross-entropy gradient is $\hat{y} - y$ -- much simpler than computing separately
- [ ] Numerical gradient checking ($\frac{f(x+h)-f(x-h)}{2h}$) is essential for verifying implementations
- [ ] He initialization ($\sqrt{2/d_{in}}$) for ReLU, Xavier ($\sqrt{1/d_{in}}$) for tanh/sigmoid
- [ ] For MLE interviews: being able to implement forward + backward for any standard layer from scratch is a strong differentiator at the senior level
"""

# ---------------------------------------------------------------------------
# Main: Write content to database
# ---------------------------------------------------------------------------

def main() -> None:
    # Populate framework_nodes with Pillar 1 content.
    engine = get_engine()
    SessionLocal.configure(bind=engine)

    with SessionLocal() as db:
        updated = 0
        missing = []

        for path, content in CONTENT.items():
            node = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if node is None:
                missing.append(path)
                continue

            node.description = content.strip()
            updated += 1

        db.commit()

    print(f"Updated {updated} framework nodes.")
    if missing:
        print(f"WARNING: {len(missing)} paths not found: {missing}")
    print("Done.")


if __name__ == "__main__":
    main()
