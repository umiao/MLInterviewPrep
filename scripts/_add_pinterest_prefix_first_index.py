"""Add Pinterest Prefix-Match First-Word-Index custom problem to mle_prep.db.

Source: Pinterest coding round 2025-11 (non-LC, recurring).
Given a (sorted) word list and a list of prefixes, return for each prefix the
index of the first word in the list that starts with it (or -1 if none).
Two canonical solutions: (1) Trie with `min_index` annotated at every node,
(2) binary search on the sorted list using `bisect_left(prefix)` and a match
check. Both are covered in the notes with Python and Chinese explanations.

Idempotent: if a row with this title already exists, updates notes only.

Task: T-P1-399
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Prefix-Match First-Word-Index (sorted dictionary)"
SOURCE = "pinterest_interview,custom"
COMPANY_TAGS = json.dumps(["Pinterest"])
TAGS = json.dumps(["Trie", "Binary Search", "String", "Prefix"])
PATTERN = "Trie(min_index) OR bisect_left on sorted list"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
PRIORITY = 2  # P1

DESCRIPTION = """\
[Pinterest coding 2025-11] Given a list of words (often provided pre-sorted)
and a list of query prefixes, return for each prefix the index of the FIRST
word in the list that starts with the prefix, or -1 if no word does.

Example:
  words    = ['a', 'apple', 'appz', 'b']
  prefixes = ['ap']
  output   = [1]        # 'apple' is the first word starting with 'ap'

Canonical follow-ups:
  (a) Many prefixes, one fixed word list -- pre-process once, O(|prefix|)
      per query (Trie).
  (b) Words not sorted -- sort + remember original indices, OR Trie.
  (c) Return ALL matching indices, not just first -- store list at Trie node.
"""

SOLUTION_TAG = "[Pinterest Prefix-First-Index Canonical Solution]"

NOTES = SOLUTION_TAG + r"""

## Problem (Pinterest 2025-11)

Inputs: `words: list[str]` (often sorted lexicographically), `prefixes: list[str]`.
Output: for each prefix, the smallest index `i` such that `words[i].startswith(prefix)`,
or `-1` if none.

## Two Clean Solutions

### Solution 1 -- Trie with `min_index` at every node (recommended)

Insert every word into a Trie. At each node along the insertion path, record
`min_index = min(min_index, word_index)`. To query a prefix, walk the Trie
char by char; the final node's `min_index` is the answer (or -1 if the walk
falls off).

Works regardless of whether the input is sorted. O(total chars) pre-process,
O(|prefix|) per query.

```python
class TrieNode:
    __slots__ = ("children", "min_index")
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.min_index: int = -1

class PrefixIndex:
    def __init__(self, words: list[str]) -> None:
        self.root = TrieNode()
        for i, w in enumerate(words):
            node = self.root
            for ch in w:
                nxt = node.children.get(ch)
                if nxt is None:
                    nxt = TrieNode()
                    node.children[ch] = nxt
                node = nxt
                if node.min_index == -1 or i < node.min_index:
                    node.min_index = i

    def first_index(self, prefix: str) -> int:
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return -1
        return node.min_index

def solve(words: list[str], prefixes: list[str]) -> list[int]:
    idx = PrefixIndex(words)
    return [idx.first_index(p) for p in prefixes]
```

### Solution 2 -- Binary search (only if words are sorted)

If `words` is lexicographically sorted, then all words starting with `prefix`
form a contiguous range. The leftmost candidate is `bisect_left(words, prefix)`.
Verify that `words[i].startswith(prefix)`; otherwise return -1.

```python
from bisect import bisect_left

def solve_sorted(words: list[str], prefixes: list[str]) -> list[int]:
    out = []
    for p in prefixes:
        i = bisect_left(words, p)
        out.append(i if i < len(words) and words[i].startswith(p) else -1)
    return out
```

**Why `bisect_left(words, prefix)` works**: any word starting with `prefix` is
`>= prefix` lexicographically, AND any word `< prefix` cannot start with it.
So the first position where `words[i] >= prefix` is the first candidate.
If that candidate does not start with `prefix`, then no word does (the next
word is even larger and still cannot start with `prefix`... wait, careful:
`prefix='ap'`, `words=['a','az','b']` -- bisect_left returns index of 'az'
which is >= 'ap' but does not start with 'ap'. Verify step catches this.)

## Complexity

| Approach | Build | Query | Space | Requires sorted? |
|----------|-------|-------|-------|------------------|
| Trie     | O(sum \|w\|) | O(\|prefix\|) | O(sum \|w\|) | No |
| Bisect   | O(1) extra (sort if needed: O(N log N)) | O(\|prefix\| + log N) | O(1) | Yes |

Interview tip: lead with the Trie solution (general, robust). Mention bisect
as a "if the list is already sorted, here's an O(log N) per query alternative
with no preprocessing."

## Edge Cases

1. Empty prefix -> should return index 0 (every word starts with empty string).
   Trie returns `root.min_index` = 0 (root is updated for each word). Bisect
   returns 0 since `bisect_left(words, '')` == 0.
2. Prefix longer than every word -> Trie walk falls off -> -1. Bisect: the
   candidate word will not start with prefix (it's a proper prefix of prefix),
   so return -1.
3. Duplicates in `words` -> Trie already takes min, bisect_left picks the
   earliest occurrence.
4. Unsorted input but the interviewer claims "sorted" -- ALWAYS validate the
   assumption verbally. If unsorted, only the Trie works.

## Chinese Notes (中文解析)

**题意**: 给定词表 (通常已按字典序排好) 和查询前缀列表, 对每个前缀返回词表里
第一个以该前缀开头的单词下标, 没有返回 -1。

**关键观察**: 两种都是标准套路, 面试时最好两种都能说。
- 如果输入**没有保证有序**: 必须用 Trie。在 Trie 每个节点维护 `min_index`
  (经过该节点的所有单词的最小下标), 查询时走到前缀末尾读取即可。
- 如果输入**保证有序**: `bisect_left` 二分找到第一个 `>= prefix` 的位置, 再验证
  它是否真的以 prefix 开头 (因为 `bisect_left` 只保证字典序, 不保证前缀关系)。

**Trie min_index 的正确更新时机**: 插入单词时, 对路径上每个节点都要更新
`min_index = min(min_index, 当前词下标)`, 不能只在单词终止节点更新。否则查询
"ap" 时走到 'p' 节点, 读到的会是该节点独有的单词下标, 漏掉更深层的单词。

**为什么 bisect_left 的验证不可省**:
  words=['a','az','b'], prefix='ap'
  bisect_left -> 1 (位置 'az'), 但 'az' 并不以 'ap' 开头, 应返回 -1。

**空前缀陷阱**: 空串是任何字符串的前缀, 应返回 0。两种写法都自然处理:
Trie 的 root.min_index 累积了所有单词的最小下标 (=0); bisect_left(words, '') 也
返回 0。

**追问**:
- 返回**所有**匹配单词下标? Trie 节点改存 list 或用子树遍历; bisect_left +
  bisect_right 截取区间。
- 流式加入新单词? Trie 直接再插入并更新 min_index; bisect 要维护有序结构
  (SortedList 或平衡树)。
- 查询非常多 (10^6)? Trie 的 O(|prefix|) 单次查询比 bisect 的 O(log N + |prefix|)
  常数更好; 同时 Trie 对缓存更友好 (字符匹配按深度而非二分跳跃)。

## Self-Test (smoke)

```python
words = ['a', 'apple', 'appz', 'b']
assert solve(words, ['ap']) == [1]
assert solve(words, ['b']) == [3]
assert solve(words, ['c']) == [-1]
assert solve(words, ['']) == [0]
assert solve(words, ['app']) == [1]
assert solve(words, ['appz']) == [2]

# Unsorted: Trie still works.
words2 = ['banana', 'apple', 'appz', 'ant']
assert solve(words2, ['ap']) == [1]   # 'apple' at index 1
assert solve(words2, ['an']) == [3]   # 'ant' at index 3

# Sorted bisect parity.
assert solve_sorted(sorted(words), ['ap']) == [1]
```
"""


def upsert() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT id, notes FROM problems WHERE title = ? AND leetcode_id IS NULL",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now(UTC).isoformat()

    if row is None:
        cur.execute("SELECT MAX(id) FROM problems")
        next_id = (cur.fetchone()[0] or 0) + 1
        cur.execute(
            """
            INSERT INTO problems (
                id, leetcode_id, title, url, difficulty, tags, pattern,
                category, source, company_tags, priority, is_completed,
                comfort_level, created_at, description, notes
            ) VALUES (?, NULL, ?, NULL, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
            """,
            (
                next_id,
                TITLE,
                DIFFICULTY,
                TAGS,
                PATTERN,
                CATEGORY,
                SOURCE,
                COMPANY_TAGS,
                PRIORITY,
                now,
                DESCRIPTION,
                NOTES,
            ),
        )
        print(f"[INSERT] id={next_id} title={TITLE!r}")
    else:
        pid, existing_notes = row
        if existing_notes and SOLUTION_TAG in existing_notes:
            print(f"[SKIP] id={pid} already has canonical solution")
        else:
            merged = (existing_notes + "\n\n---\n\n" + NOTES) if existing_notes else NOTES
            cur.execute(
                "UPDATE problems SET notes = ?, description = ? WHERE id = ?",
                (merged, DESCRIPTION, pid),
            )
            print(f"[UPDATE] id={pid} notes appended")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    upsert()
