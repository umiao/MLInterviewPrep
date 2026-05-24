"""Strip `__slots__` optimizations from problem notes per user feedback 2026-04-15.

User preference: plain dict-backed classes are good enough for interview solutions;
`__slots__` adds visual noise without teaching value on a white-board.

Approach: regex-remove the `__slots__ = (...)` line (and the trailing blank line
when it was the first line of the class body). Idempotent.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# Match a line that is only whitespace + __slots__ = ... (tuple, list, or set literal),
# optionally followed by a trailing blank line.
SLOTS_RE = re.compile(
    r"^[ \t]*__slots__\s*=\s*[\(\[\{].*?[\)\]\}]\s*\n(?:[ \t]*\n)?",
    re.MULTILINE,
)

def strip_slots(text: str) -> str:
    return SLOTS_RE.sub("", text)

def main():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT id, title, notes FROM problems WHERE notes LIKE '%__slots__%'"
    ).fetchall()
    for pid, title, notes in rows:
        new = strip_slots(notes)
        if new == notes:
            print(f"[skip] {pid} {title}: no match changed")
            continue
        n_removed = notes.count("__slots__") - new.count("__slots__")
        conn.execute(
            "UPDATE problems SET notes = ? WHERE id = ?", (new, pid)
        )
        print(f"[ok]   {pid} {title}: removed {n_removed} __slots__ line(s), {len(notes)} -> {len(new)} B")
    conn.commit()
    # sanity
    remaining = conn.execute("SELECT id, title FROM problems WHERE notes LIKE '%__slots__%'").fetchall()
    if remaining:
        print("WARN: still present in:", remaining)
    else:
        print("all clear")
    conn.close()

if __name__ == "__main__":
    main()
