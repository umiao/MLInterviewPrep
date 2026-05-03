"""Fix over-eager merges from seed_tuple_assign_broad_20260415.py.

The broad sweep had two transformer bugs:
  - Independence check used `\\b(\\w[\\w.]*)\\b` so attribute chains returned as one token.
    `la='curNode'` failed to detect `curNode.count` in RHS2.
  - RHS `=` was allowed through, so it merged into a line whose RHS was itself a chained
    assignment, producing `a, b = x, y = z` which is invalid.

This seed reverts the known-broken merges to their pre-sweep form (or a clean split).
Real bugs (hand-verified; classic idioms like `root.left, root.right = invertTree(...)` and
`nxt, curr.next = curr.next, prev` are correct tuple-assigns and left alone).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# (pid, buggy, fixed)
FIXES = [
    # 24: was `curr.next = node; curr = curr.next` — line 2 needed NEW curr.next (= node).
    (24,
     "        curr.next, curr = node, curr.next\n",
     "        curr.next = node\n        curr = curr.next\n"),
    # 29: chain+tuple
    (29,
     "        self.found_p, result = self.found_q = False, self._dfs(root, p, q)\n",
     "        self.found_p = self.found_q = False\n        result = self._dfs(root, p, q)\n"),
    # 56: chain+tuple
    (56,
     "    result, max_prod = nums[0], min_prod = 1\n",
     "    result = nums[0]\n    max_prod = min_prod = 1\n"),
    # 93: chain+tuple (LRU sentinel init)
    (93,
     "        self.sentinel.next, self.capacity = self.sentinel.prev = self.sentinel, capacity\n",
     "        self.sentinel.next = self.sentinel.prev = self.sentinel\n        self.capacity = capacity\n"),
    # 182: chain+tuple (sentinel init)
    (182,
     "        self.sentinel, self.sentinel.prev = Node(0), self.sentinel.next = self.sentinel\n",
     "        self.sentinel = Node(0)\n        self.sentinel.prev = self.sentinel.next = self.sentinel\n"),
    # 182: two curNode RHS old-value bugs
    (182,
     "            curNode, newCnt = self.hashTable[key], curNode.count + 1\n",
     "            curNode = self.hashTable[key]\n            newCnt = curNode.count + 1\n"),
    (182,
     "            curNode, newCnt = self.hashTable[key], curNode.count - 1\n",
     "            curNode = self.hashTable[key]\n            newCnt = curNode.count - 1\n"),
    # 214: low used on RHS2 as attribute base (old value bug)
    (214,
     "            low, idx = mask & -mask, low.bit_length() - 1\n",
     "            low = mask & -mask\n            idx = low.bit_length() - 1\n"),
    # 237: self.cur meant to mirror NEW self.root
    (237,
     "        self.root, self.cur = TrieNode(), self.root\n",
     "        self.root = TrieNode()\n        self.cur = self.root\n"),
    # 1081: semicolon-bracketed deque() pair got mangled
    (1081,
     "    mx_dq, L = deque(); mn_dq = deque(), 0\n",
     "    mx_dq = deque(); mn_dq = deque()\n    L = 0\n"),
    # 1082: chain+tuple
    (1082,
     "    dp0, best = dp1 = 1, 1\n",
     "    dp0 = dp1 = 1\n    best = 1\n"),
    # 45: `reverse=True` false-positive from my scanner — LEAVE (it's valid). No fix needed.
    # 48, 75, 105, 113, 1073, 1074: all false-positives (contain `==`, `>=`, or kwarg `=`). No fix needed.
]

def main():
    conn = sqlite3.connect(DB)
    applied = 0
    for pid, buggy, fixed in FIXES:
        row = conn.execute("SELECT notes FROM problems WHERE id = ?", (pid,)).fetchone()
        if not row:
            print(f"[miss] {pid}: no row")
            continue
        notes = row[0]
        if buggy not in notes:
            print(f"[skip] {pid}: pattern not present (already fixed?)  {buggy.strip()!r}")
            continue
        new = notes.replace(buggy, fixed, 1)
        conn.execute("UPDATE problems SET notes = ? WHERE id = ?", (new, pid))
        applied += 1
        print(f"[ok]   {pid}: fixed ({len(notes)} -> {len(new)} B)")
    conn.commit()
    conn.close()
    print(f"\nApplied {applied} fixes.")

if __name__ == "__main__":
    main()
