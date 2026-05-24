"""Broad tuple-assignment sweep across all problem notes (user request 2026-04-15).

Scans every ```python ... ``` code block in `problems.notes` for consecutive
same-indent simple assignments (`lhs = rhs`) and merges them into tuple-assign
form when safe.

Safety rules (conservative — skip if any fails):
  1. Both lines match `^<indent>(\\w[\\w.]*) = (.+)$` (simple name / attribute LHS).
  2. Same indent.
  3. The RHS of line 2 contains no identifier from LHS of line 1 (independence).
  4. LHS 1 and LHS 2 are different (avoid self-overwrites).
  5. Neither line ends with a trailing comment (preserve annotations).
  6. Neither RHS contains `walrus :=` or trailing backslash.

Runs multiple passes until no more merges — lets 3-way paired inits collapse too.
Prints a report per problem. Idempotent.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

ASSIGN_RE = re.compile(r"^(?P<indent>[ \t]+)(?P<lhs>\w[\w.]*)\s*=\s*(?P<rhs>.+?)\s*$")
IDENT_RE = re.compile(r"\b(\w[\w.]*)\b")

def can_merge(line_a: str, line_b: str) -> tuple[str, str, str, str, str] | None:
    ma = ASSIGN_RE.match(line_a)
    mb = ASSIGN_RE.match(line_b)
    if not ma or not mb:
        return None
    if ma.group("indent") != mb.group("indent"):
        return None
    lhs_a, rhs_a = ma.group("lhs"), ma.group("rhs")
    lhs_b, rhs_b = mb.group("lhs"), mb.group("rhs")
    # skip if LHS equal
    if lhs_a == lhs_b:
        return None
    # skip trailing comments
    if "#" in rhs_a or "#" in rhs_b:
        return None
    # skip walrus / continuation
    if ":=" in rhs_a or ":=" in rhs_b or rhs_a.endswith("\\") or rhs_b.endswith("\\"):
        return None
    # independence: LHS-a identifier must not appear in RHS-b
    # handle attribute chains — use the root name
    root_a = lhs_a.split(".")[0]
    if root_a in IDENT_RE.findall(rhs_b):
        return None
    return (ma.group("indent"), lhs_a, rhs_a, lhs_b, rhs_b)

def transform_block(block: str) -> tuple[str, int]:
    lines = block.split("\n")
    changed_total = 0
    pass_n = 0
    while True:
        new_lines = []
        i = 0
        changed = 0
        while i < len(lines):
            if i + 1 < len(lines):
                merge = can_merge(lines[i], lines[i + 1])
                if merge:
                    indent, la, ra, lb, rb = merge
                    new_lines.append(f"{indent}{la}, {lb} = {ra}, {rb}")
                    i += 2
                    changed += 1
                    continue
            new_lines.append(lines[i])
            i += 1
        lines = new_lines
        changed_total += changed
        pass_n += 1
        if changed == 0 or pass_n > 10:
            break
    return "\n".join(lines), changed_total

CODE_BLOCK_RE = re.compile(r"(```python\n)(.*?)(```)", re.DOTALL)

def transform_notes(notes: str) -> tuple[str, int]:
    total_merges = 0
    def sub(m):
        nonlocal total_merges
        new_body, n = transform_block(m.group(2))
        total_merges += n
        return m.group(1) + new_body + m.group(3)
    return CODE_BLOCK_RE.sub(sub, notes), total_merges

def main():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT id, title, notes FROM problems WHERE notes LIKE '%```python%'"
    ).fetchall()
    total = 0
    touched = 0
    for pid, title, notes in rows:
        new, n = transform_notes(notes)
        if n:
            conn.execute("UPDATE problems SET notes = ? WHERE id = ?", (new, pid))
            print(f"[ok]  {pid:4d} {title}: +{n} merges, {len(notes)} -> {len(new)} B")
            total += n
            touched += 1
    conn.commit()
    print(f"\nTOTAL: {total} merges across {touched} problems")
    conn.close()

if __name__ == "__main__":
    main()
