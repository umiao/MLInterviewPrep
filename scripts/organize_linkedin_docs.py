"""T-P0-250: Organize LinkedIn prep notes into company_documents.

1. Clean up document titles (remove Chinese, make descriptive)
2. Update prep_notes with document index header (like Uber)
3. Add solution notes for key LinkedIn problems that lack them
"""
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_PATH = "data/mle_prep.db"

# --- 1. Document title updates ---
TITLE_UPDATES = {
    22: "LinkedIn System Design Interview Prep Notes (1point3acres)",
    23: "LinkedIn BQ + Product Sense Interview Prep Notes (1point3acres)",
    24: "LinkedIn ML Fundamentals + Coding Interview Prep Notes (1point3acres)",
    26: "LinkedIn Interview Questions Index (All Topics)",
    27: "ML Fundamentals From-Scratch Complete Guide (8 Topics Merged)",
}

# --- 2. New prep_notes with document index ---
NEW_PREP_NOTES = """\
# LinkedIn AI Engineer Prep Documents Index

All detailed prep documents are available in the Documents tab:

- **1point3acres Interviews** -- Forum interview experiences and data points
- **Phone Screen Scheduling** -- Interview logistics and scheduling info
- **Probability/Statistics Prep** -- Probability, statistics, and A/B testing prep (1point3acres)
- **System Design Prep** -- ML system design interview notes (1point3acres)
- **BQ + Product Sense Prep** -- Behavioral questions and product sense (1point3acres)
- **ML Fundamentals + Coding Prep** -- ML theory, coding problems (1point3acres)
- **All-in-One Prep** -- Comprehensive LinkedIn MLE prep guide
- **Interview Questions Index** -- All 47 interview questions organized by category
- **ML Fundamentals From-Scratch** -- 8-topic ML guide (KNN, Linear/Logistic Reg, Trees, etc.)

---

# LinkedIn AI Engineer -- Phone Screen Prep

## >>> Collected Interview Problems: 2025-11-02 ~ 2026-03-26 <<<

> **April 2, 2026 1:00 PM PDT | SWE Phone Screen 1 | AI Engineer | Zoom**

---

## Pre-Interview Checklist

- [ ] Review LinkedIn JD, highlight key requirement keywords
- [ ] Review LinkedIn Engineering Blog -- focus on feed ranking, recommendation systems, knowledge graph
- [ ] Practice 3 LC mediums: graph/tree, hash map, topological sort
- [ ] Review ML system design: feed ranking pipeline, job recommendation, metrics/A/B testing
- [ ] Prepare 2-3 behavioral stories (STAR format)
- [ ] Prepare reverse questions for interviewer (team structure, ML infra, current challenges)
- [ ] Set up quiet environment + Zoom tested + resume and JD open

## Coding Prep

- [ ] Topological sort (LC 207, 210, 269)
- [ ] Hash map design (LC 146 LRU Cache, LC 380 Insert Delete GetRandom)
- [ ] Tree traversal (LC 236 LCA, LC 314 Vertical Order, LC 124 Max Path Sum)
- [ ] Graph problems (LC 200 Number of Islands, LC 127 Word Ladder)
- [ ] SQL (LC 176 Second Highest Salary, LC 181 Employees Earning More)

## ML System Design Prep

- [ ] Feed ranking system (features, model architecture, serving, metrics)
- [ ] Job recommendation system (collaborative filtering, content-based, hybrid)
- [ ] A/B testing framework (metrics selection, sample size, novelty effects)
- [ ] Feature store and real-time inference pipeline

## Key Info

Phone screen format: 45-60 min, typically 1-2 rounds.
Heavy on coding (LC medium, data structures, graph/tree, SQL),
ML system design (feed ranking, job recommendations, metrics, A/B testing),
and product/metrics questions (feature evaluation, metric debugging).
Behavioral questions appear but are lighter weight.
Common topics: topological sort, hash map design, tree traversal,
recommendation systems, ranking models, experimentation frameworks.
"""

# --- 3. Solution notes for key problems ---
PROBLEM_NOTES: dict[int, str] = {
    # LC 210 - Course Schedule II
    210: """\
## Course Schedule II

### Approach
**Topological Sort (BFS - Kahn's Algorithm)**: Build adjacency list and in-degree array. \
Start BFS from nodes with in-degree 0. Each time we process a node, add it to result and \
decrement in-degree of its neighbors. If neighbor's in-degree becomes 0, add to queue.

### Key Insight
- If result length != numCourses, there's a cycle (return [])
- This is the BFS version of topological sort; DFS version uses post-order + reverse

### Solution
```python
from collections import deque

def findOrder(numCourses: int, prerequisites: list[list[int]]) -> list[int]:
    adj = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    for course, prereq in prerequisites:
        adj[prereq].append(course)
        indegree[course] += 1

    queue = deque([i for i in range(numCourses) if indegree[i] == 0])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == numCourses else []
```
- Time: O(V + E), Space: O(V + E)
""",

    # LC 380 - Insert Delete GetRandom O(1)
    380: """\
## Insert Delete GetRandom O(1)

### Approach
Use **HashMap + ArrayList** together. HashMap maps val -> index in list. \
ArrayList stores values for O(1) random access.

### Key Trick for O(1) Delete
Swap the element to delete with the last element, then pop from end. \
Update the swapped element's index in the HashMap.

### Solution
```python
import random

class RandomizedSet:
    def __init__(self):
        self.val_to_idx = {}
        self.vals = []

    def insert(self, val: int) -> bool:
        if val in self.val_to_idx:
            return False
        self.val_to_idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.val_to_idx:
            return False
        idx = self.val_to_idx[val]
        last = self.vals[-1]
        self.vals[idx] = last
        self.val_to_idx[last] = idx
        self.vals.pop()
        del self.val_to_idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```
- All operations O(1) average
""",

    # LC 236 - Lowest Common Ancestor
    236: """\
## Lowest Common Ancestor of a Binary Tree

### Approach
**Recursive DFS**: At each node, recursively search left and right subtrees for p and q. \
If both sides return non-null, current node is the LCA. If only one side returns non-null, \
propagate that result up.

### Key Insight
- Base cases: node is None, node is p, or node is q
- If left and right both found something, current node is LCA
- Otherwise, return whichever side found something

### Solution
```python
def lowestCommonAncestor(root, p, q):
    if not root or root == p or root == q:
        return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    if left and right:
        return root
    return left or right
```
- Time: O(N), Space: O(H) where H = tree height
""",

    # LC 314 - Binary Tree Vertical Order Traversal
    314: """\
## Binary Tree Vertical Order Traversal

### Approach
**BFS with column index**: Root is column 0, left child is col-1, right child is col+1. \
Use BFS (not DFS) to ensure top-to-bottom order within each column. Store results in \
a dict mapping column -> list of values.

### Key Insight
- BFS guarantees correct top-to-bottom ordering within columns
- DFS would require sorting by row within each column
- Track min/max column to iterate in order at the end

### Solution
```python
from collections import deque, defaultdict

def verticalOrder(root):
    if not root:
        return []
    cols = defaultdict(list)
    queue = deque([(root, 0)])
    min_col = max_col = 0
    while queue:
        node, col = queue.popleft()
        cols[col].append(node.val)
        min_col = min(min_col, col)
        max_col = max(max_col, col)
        if node.left:
            queue.append((node.left, col - 1))
        if node.right:
            queue.append((node.right, col + 1))
    return [cols[c] for c in range(min_col, max_col + 1)]
```
- Time: O(N), Space: O(N)
""",

    # LC 127 - Word Ladder
    127: """\
## Word Ladder

### Approach
**BFS** from beginWord to endWord. At each step, try changing each character position \
to every letter a-z. If the new word is in wordList, add to next level.

### Optimization
Use **wildcard pattern** approach: preprocess words into pattern -> [words] map. \
E.g., "hot" -> ["*ot", "h*t", "ho*"]. This avoids O(26 * L) per word.

### Solution
```python
from collections import deque

def ladderLength(beginWord: str, endWord: str, wordList: list[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0
    queue = deque([(beginWord, 1)])
    visited = {beginWord}
    while queue:
        word, steps = queue.popleft()
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word == endWord:
                    return steps + 1
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, steps + 1))
    return 0
```
- Time: O(M^2 * N) where M = word length, N = wordList size
- Space: O(M * N)
""",

    # LC 176 - Second Highest Salary
    176: """\
## Second Highest Salary

### Approach
Use **IFNULL + subquery with LIMIT/OFFSET** to handle the case where there's no second highest.

### Key Insight
- Must return NULL if no second highest exists (not empty result set)
- IFNULL/COALESCE wraps the subquery to convert empty result to NULL
- Use DISTINCT to handle duplicate salaries

### Solution
```sql
SELECT IFNULL(
    (SELECT DISTINCT salary
     FROM Employee
     ORDER BY salary DESC
     LIMIT 1 OFFSET 1),
    NULL
) AS SecondHighestSalary;
```

### Alternative (DENSE_RANK)
```sql
SELECT MAX(salary) AS SecondHighestSalary
FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rk
    FROM Employee
) ranked
WHERE rk = 2;
```
""",

    # LC 181 - Employees Earning More Than Their Managers
    181: """\
## Employees Earning More Than Their Managers

### Approach
**Self-join**: Join Employee table with itself where e1.managerId = e2.id, \
then filter where employee salary > manager salary.

### Solution
```sql
SELECT e1.name AS Employee
FROM Employee e1
JOIN Employee e2 ON e1.managerId = e2.id
WHERE e1.salary > e2.salary;
```

### Alternative (Subquery)
```sql
SELECT name AS Employee
FROM Employee e1
WHERE salary > (
    SELECT salary FROM Employee WHERE id = e1.managerId
);
```
""",

    # LC 366 - Find Leaves of Binary Tree
    366: """\
## Find Leaves of Binary Tree

### Approach
**DFS with height calculation**: The "leaf level" of a node equals its height in the tree. \
Leaves have height 0, their parents have height 1, etc. Group nodes by height.

### Key Insight
- height(node) = 1 + max(height(left), height(right))
- Leaves: height 0. This naturally groups nodes into removal rounds.
- No need to actually remove nodes -- just compute heights.

### Solution
```python
def findLeaves(root):
    result = []
    def height(node):
        if not node:
            return -1
        h = 1 + max(height(node.left), height(node.right))
        if h >= len(result):
            result.append([])
        result[h].append(node.val)
        return h
    height(root)
    return result
```
- Time: O(N), Space: O(N)
""",

    # LC 311 - Sparse Matrix Multiplication
    311: """\
## Sparse Matrix Multiplication

### Approach
**Skip zeros** during multiplication. For sparse matrices, most elements are 0. \
Only multiply and accumulate when both elements are non-zero.

### Key Insight
- Standard matrix mult: C[i][j] += A[i][k] * B[k][j]
- For sparse: iterate A row by row, skip A[i][k]==0, then skip B[k][j]==0
- This avoids unnecessary multiplications

### Solution
```python
def multiply(mat1: list[list[int]], mat2: list[list[int]]) -> list[list[int]]:
    m, k, n = len(mat1), len(mat1[0]), len(mat2[0])
    result = [[0] * n for _ in range(m)]
    for i in range(m):
        for p in range(k):
            if mat1[i][p] == 0:
                continue
            for j in range(n):
                if mat2[p][j] == 0:
                    continue
                result[i][j] += mat1[i][p] * mat2[p][j]
    return result
```
- Time: O(m * k * n) worst case, much better for sparse matrices
""",

    # LC 362 - Design Hit Counter
    362: """\
## Design Hit Counter

### Approach
**Circular buffer** of size 300 (5 minutes). Each slot stores (timestamp, count). \
On hit/getHits, check if the slot's timestamp matches current window.

### Alternative: Queue
Use a deque, append timestamps on hit, pop expired ones on getHits.

### Solution (Circular Buffer - O(1) hit, O(s) getHits where s=300)
```python
class HitCounter:
    def __init__(self):
        self.times = [0] * 300
        self.hits = [0] * 300

    def hit(self, timestamp: int) -> None:
        idx = timestamp % 300
        if self.times[idx] != timestamp:
            self.times[idx] = timestamp
            self.hits[idx] = 1
        else:
            self.hits[idx] += 1

    def getHits(self, timestamp: int) -> int:
        total = 0
        for i in range(300):
            if timestamp - self.times[i] < 300:
                total += self.hits[i]
        return total
```
- Thread-safe version: use atomic operations or locks per bucket
""",

    # LC 394 - Decode String
    394: """\
## Decode String

### Approach
**Stack-based**: Use two stacks (or one stack with tuples): one for counts, one for strings. \
When we see '[', push current string and count. When we see ']', pop and concatenate.

### Key Insight
- Build current number and current string as we scan
- On '[': push (current_string, current_num), reset both
- On ']': pop (prev_string, num), current = prev_string + num * current

### Solution
```python
def decodeString(s: str) -> str:
    stack = []
    curr_str = ""
    curr_num = 0
    for c in s:
        if c.isdigit():
            curr_num = curr_num * 10 + int(c)
        elif c == '[':
            stack.append((curr_str, curr_num))
            curr_str = ""
            curr_num = 0
        elif c == ']':
            prev_str, num = stack.pop()
            curr_str = prev_str + num * curr_str
        else:
            curr_str += c
    return curr_str
```
- Time: O(max_k * n), Space: O(n)
""",

    # LC 1249 - Minimum Remove to Make Valid Parentheses
    1249: """\
## Minimum Remove to Make Valid Parentheses

### Approach
**Two-pass or Stack**: Track indices of unmatched parentheses, then remove them.

### Stack Approach
1. Scan left to right: push '(' indices to stack, pop on matching ')'
2. Remaining stack indices = unmatched '('
3. Also track unmatched ')' indices during scan
4. Build result string skipping all unmatched indices

### Solution
```python
def minRemoveToMakeValid(s: str) -> str:
    indices_to_remove = set()
    stack = []
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)
        elif c == ')':
            if stack:
                stack.pop()
            else:
                indices_to_remove.add(i)
    indices_to_remove.update(stack)
    return ''.join(c for i, c in enumerate(s) if i not in indices_to_remove)
```
- Time: O(N), Space: O(N)
""",

    # LC 528 - Random Pick with Weight
    528: """\
## Random Pick with Weight

### Approach
**Prefix sum + Binary search**: Build prefix sum array of weights. \
Generate random number in [1, total_weight], binary search for the index.

### Key Insight
- Prefix sum creates ranges proportional to weights
- Binary search finds which range the random number falls in
- Use bisect_left for correct boundary handling

### Solution
```python
import random
import bisect

class Solution:
    def __init__(self, w: list[int]):
        self.prefix = []
        total = 0
        for weight in w:
            total += weight
            self.prefix.append(total)
        self.total = total

    def pickIndex(self) -> int:
        target = random.randint(1, self.total)
        return bisect.bisect_left(self.prefix, target)
```
- Init: O(N), Pick: O(log N)
""",

    # LC 348 - Design Tic-Tac-Toe
    348: """\
## Design Tic-Tac-Toe

### Approach
**O(1) move**: Track row sums, col sums, diagonal sum, anti-diagonal sum. \
Player 1 adds +1, player 2 adds -1. A player wins when any sum reaches +n or -n.

### Key Insight
- Don't store the board -- just track sums
- Row[i] += delta, Col[j] += delta
- If i==j: diag += delta. If i+j==n-1: anti_diag += delta
- Check if any sum == n or -n after each move

### Solution
```python
class TicTacToe:
    def __init__(self, n: int):
        self.n = n
        self.rows = [0] * n
        self.cols = [0] * n
        self.diag = 0
        self.anti_diag = 0

    def move(self, row: int, col: int, player: int) -> int:
        delta = 1 if player == 1 else -1
        self.rows[row] += delta
        self.cols[col] += delta
        if row == col:
            self.diag += delta
        if row + col == self.n - 1:
            self.anti_diag += delta
        if abs(self.rows[row]) == self.n or abs(self.cols[col]) == self.n \\
           or abs(self.diag) == self.n or abs(self.anti_diag) == self.n:
            return player
        return 0
```
- Time: O(1) per move, Space: O(N)
""",

    # LC 227 - Basic Calculator II
    227: """\
## Basic Calculator II

### Approach
**Stack with operator precedence**: Process * and / immediately, defer + and -. \
Track the previous operator and current number. When we encounter a new operator \
or end of string, process the previous operator.

### Key Insight
- +/- : push number (with sign) to stack
- * / : pop top of stack, compute with current num, push result
- Final answer = sum of stack

### Solution
```python
def calculate(s: str) -> int:
    stack = []
    num = 0
    op = '+'
    for i, c in enumerate(s):
        if c.isdigit():
            num = num * 10 + int(c)
        if c in '+-*/' or i == len(s) - 1:
            if op == '+':
                stack.append(num)
            elif op == '-':
                stack.append(-num)
            elif op == '*':
                stack.append(stack.pop() * num)
            elif op == '/':
                stack.append(int(stack.pop() / num))
            op = c
            num = 0
    return sum(stack)
```
- Time: O(N), Space: O(N)
""",

    # LC 588 - Design In-Memory File System
    588: """\
## Design In-Memory File System

### Approach
**Trie-based**: Each node represents a directory or file. Use a dict of children. \
Files store their content as a string.

### Key Operations
- `ls(path)`: List directory contents (sorted) or return filename if path is a file
- `mkdir(path)`: Create all directories along path
- `addContentToFile(path, content)`: Create/append to file
- `readContentFromFile(path)`: Return file content

### Solution
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.content = ""
        self.is_file = False

class FileSystem:
    def __init__(self):
        self.root = TrieNode()

    def _traverse(self, path: str) -> TrieNode:
        node = self.root
        if path == "/":
            return node
        for part in path.split("/")[1:]:
            if part not in node.children:
                node.children[part] = TrieNode()
            node = node.children[part]
        return node

    def ls(self, path: str) -> list[str]:
        node = self._traverse(path)
        if node.is_file:
            return [path.split("/")[-1]]
        return sorted(node.children.keys())

    def mkdir(self, path: str) -> None:
        self._traverse(path)

    def addContentToFile(self, filePath: str, content: str) -> None:
        node = self._traverse(filePath)
        node.is_file = True
        node.content += content

    def readContentFromFile(self, filePath: str) -> str:
        return self._traverse(filePath).content
```
- Time: O(L) for traverse (L = path depth), O(K log K) for ls (K = children)
""",
}


def main() -> None:
    """Execute all LinkedIn document organization updates."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Update document titles
    print("=== Updating document titles ===")
    for doc_id, new_title in TITLE_UPDATES.items():
        cur.execute("UPDATE company_documents SET title=? WHERE id=?", (new_title, doc_id))
        print(f"  doc#{doc_id}: -> {new_title}")
    print(f"  Updated {len(TITLE_UPDATES)} titles")

    # 2. Update prep_notes with document index
    print("\n=== Updating LinkedIn prep_notes ===")
    cur.execute("SELECT length(prep_notes) FROM companies WHERE id=1")
    old_len = cur.fetchone()[0]
    cur.execute("UPDATE companies SET prep_notes=? WHERE id=1", (NEW_PREP_NOTES,))
    cur.execute("SELECT length(prep_notes) FROM companies WHERE id=1")
    new_len = cur.fetchone()[0]
    print(f"  prep_notes: {old_len} -> {new_len} chars")

    # 3. Add solution notes for key problems
    print("\n=== Adding solution notes for key problems ===")
    added = 0
    for lc_id, notes in PROBLEM_NOTES.items():
        cur.execute(
            "SELECT id, title, length(notes) FROM problems WHERE leetcode_id=?",
            (lc_id,),
        )
        row = cur.fetchone()
        if not row:
            print(f"  LC{lc_id}: NOT IN DB, skipping")
            continue
        prob_id, title, existing_len = row
        if existing_len and existing_len > 0:
            print(f"  LC{lc_id}: {title} -- already has {existing_len} chars, skipping")
            continue
        cur.execute("UPDATE problems SET notes=? WHERE id=?", (notes, prob_id))
        print(f"  LC{lc_id}: {title} -- added {len(notes)} chars")
        added += 1
    print(f"  Added notes for {added} problems")

    conn.commit()

    # 4. Verify
    print("\n=== Verification ===")

    # Check all LinkedIn docs
    cur.execute(
        "SELECT id, title, source_type, length(content) FROM company_documents WHERE company_id=1 ORDER BY id"
    )
    docs = cur.fetchall()
    print(f"\nLinkedIn documents ({len(docs)}):")
    for d in docs:
        print(f"  doc#{d[0]}: {d[1]} ({d[2]}, {d[3]} chars)")

    # Check prep_notes has document index
    cur.execute("SELECT prep_notes FROM companies WHERE id=1")
    pn = cur.fetchone()[0]
    has_index = "Documents Index" in pn
    print(f"\nprep_notes has document index: {has_index}")
    print(f"prep_notes length: {len(pn)} chars")

    # Check key problems now have notes
    key_lcs = list(PROBLEM_NOTES.keys())
    cur.execute(
        f"SELECT leetcode_id, title, length(notes) FROM problems WHERE leetcode_id IN ({','.join('?' * len(key_lcs))})",
        key_lcs,
    )
    rows = cur.fetchall()
    all_have_notes = all(r[2] and r[2] > 0 for r in rows)
    print(f"\nAll {len(rows)} key problems now have notes: {all_have_notes}")
    for r in sorted(rows, key=lambda x: x[0]):
        status = "OK" if r[2] and r[2] > 0 else "MISSING"
        print(f"  LC{r[0]}: {r[1]} -- {r[2] or 0} chars [{status}]")

    # Total stats
    cur.execute(
        "SELECT COUNT(*) FROM problems WHERE (company_tags LIKE '%linkedin%' OR company_tags LIKE '%LinkedIn%') AND notes IS NOT NULL AND length(notes) > 0"
    )
    total_with_notes = cur.fetchone()[0]
    print(f"\nTotal LinkedIn problems with notes: {total_with_notes}")

    conn.close()
    print("\n[DONE]")


if __name__ == "__main__":
    main()
