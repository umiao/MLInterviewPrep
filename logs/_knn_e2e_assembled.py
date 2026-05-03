"""Assembled real-execution harness for T-P0-709 KNN second pass.

Extracts all python code blocks from problems.id=1106 notes, indents
the method blocks 4 spaces to nest under the class, then exec the full
assembled module. Mirrors logs/_logreg_e2e_assembled.py / _kmeans_e2e_assembled.py.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
PROBLEM_ID = 1106


def main() -> int:
    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    notes = conn.execute(
        "SELECT notes FROM problems WHERE id = ?", (PROBLEM_ID,)
    ).fetchone()[0]
    conn.close()

    blocks = re.findall(r"```python\n(.*?)\n```", notes, re.DOTALL)
    if not blocks:
        print("[FAIL] no python blocks found")
        return 1

    # Block 0: imports + class skeleton (with __init__).
    # Blocks 1..N-2: methods (need 4-space indent to nest under class).
    # Block N-1: the End-to-end test (already module-level).
    skeleton = blocks[0]
    method_blocks = blocks[1:-1]
    e2e = blocks[-1]

    indented_methods = []
    for blk in method_blocks:
        indented = "\n".join("    " + line if line.strip() else line for line in blk.splitlines())
        indented_methods.append(indented)

    assembled = skeleton + "\n\n" + "\n\n".join(indented_methods) + "\n\n" + e2e
    print("=== Assembled module ===")
    print(assembled)
    print("=== End assembled ===")
    print()
    print("=== Execution ===")
    exec(compile(assembled, "<knn_e2e>", "exec"), {})
    print("=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
