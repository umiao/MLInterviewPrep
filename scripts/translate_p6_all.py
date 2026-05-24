#!/usr/bin/env python3
"""Translate and expand nodes 149-164 (Pillar 6 Deep Learning & LLM) to Chinese.

Reads .txt files from node_translations/ directory and updates the database.
"""

import io
import os
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mle_prep.db')
TRANS_DIR = os.path.join(os.path.dirname(__file__), 'node_translations')


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for node_id in range(149, 165):
        filepath = os.path.join(TRANS_DIR, f'node_{node_id}.txt')
        if not os.path.exists(filepath):
            print(f"Node {node_id}: SKIP (file not found)")
            continue

        with open(filepath, encoding='utf-8') as f:
            desc = f.read().strip()

        cursor.execute("UPDATE framework_nodes SET description = ? WHERE id = ?", (desc, node_id))

        # Verify
        length = len(desc)
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in desc)

        in_code = False
        has_math_in_code = False
        for line in desc.split('\n'):
            if line.strip().startswith('```'):
                in_code = not in_code
            elif in_code and '$$' in line:
                has_math_in_code = True

        status = "OK" if (length >= 5500 and has_chinese and not has_math_in_code) else "WARN"
        if length < 5500:
            status += f" (too short: {length})"
        print(f"Node {node_id}: len={length}, chinese={has_chinese}, math_in_code={has_math_in_code} -> {status}")

    conn.commit()
    conn.close()
    print("\nAll nodes updated successfully.")


if __name__ == "__main__":
    main()
