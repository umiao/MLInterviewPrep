"""Apply tuple-assignment style to paired initializers across recently-touched problem notes.

Scope: 1071-1076 Pinterest custom problems (1564/1580 had no candidates). User prefers
this Pythonic style on paired field/variable initializations.

Each replacement is an exact string-match rewrite; the seed is idempotent (running twice
is a no-op because the old strings won't match after the first run).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PATCHES = {
    # 1071 Lighthouse
    1071: [
        ("    visited = set()\n    q = deque([start])\n",
         "    visited, q = set(), deque([start])\n"),
    ],
    # 1072 Prefix-Index — TrieNode.__init__
    1072: [
        ("        self.children = {}\n        self.min_index = -1\n",
         "        self.children, self.min_index = {}, -1\n"),
    ],
    # 1073 round() — two paired inits inside the carry branch
    1073: [
        ("    if round_up:\n        j = len(digits) - 1\n        carry = 1\n",
         "    if round_up:\n        j, carry = len(digits) - 1, 1\n"),
    ],
    # 1075 Grant Access — PermissionSystem.__init__ + has_access BFS init
    1075: [
        (
            "    def __init__(self):\n"
            "        self.children = defaultdict(set)\n"
            "        self.parents  = defaultdict(set)\n"
            "        self.grants   = defaultdict(set)\n",
            "    def __init__(self):\n"
            "        self.children = defaultdict(set)\n"
            "        self.parents  = defaultdict(set)\n"
            "        self.grants   = defaultdict(set)\n",
        ),  # keep alignment; skip this one (alignment preserved intentionally)
        ("        seen = {node}\n        q = deque([node])\n",
         "        seen, q = {node}, deque([node])\n"),
    ],
    # 1076 Pin Conn — ConnectivityService.__init__
    1076: [
        (
            "    def __init__(self):\n"
            "        self.parent = {}\n"
            "        self.rank   = {}\n"
            "        self.size   = {}\n"
            "        self._components = 0\n",
            "    def __init__(self):\n"
            "        self.parent, self.rank, self.size = {}, {}, {}\n"
            "        self._components = 0\n",
        ),
    ],
}

def main():
    conn = sqlite3.connect(DB)
    for pid, patches in PATCHES.items():
        row = conn.execute("SELECT notes FROM problems WHERE id = ?", (pid,)).fetchone()
        if not row:
            print(f"[miss] problem {pid}: not found")
            continue
        notes = row[0]
        before = notes
        for old, new in patches:
            if old == new:
                continue  # intentional skip (alignment preserved)
            if old in notes:
                notes = notes.replace(old, new, 1)
            else:
                print(f"[warn] {pid}: pattern not found (may be already patched): {old[:60]!r}")
        if notes != before:
            conn.execute("UPDATE problems SET notes = ? WHERE id = ?", (notes, pid))
            print(f"[ok]   {pid}: {len(before)} -> {len(notes)} B")
        else:
            print(f"[noop] {pid}: nothing changed")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
