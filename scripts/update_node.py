#!/usr/bin/env python
"""Update a single framework_node description by reading from a text file."""
import os
import sqlite3
import sys


def main():
    if len(sys.argv) < 3:
        print("Usage: python update_node.py <node_id> <content_file>")
        sys.exit(1)

    node_id = int(sys.argv[1])
    content_file = sys.argv[2]

    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mle_prep.db')

    with open(content_file, encoding='utf-8') as f:
        content = f.read()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('UPDATE framework_nodes SET description=? WHERE id=?', (content, node_id))
    conn.commit()

    cur.execute('SELECT LENGTH(description) FROM framework_nodes WHERE id=?', (node_id,))
    size = cur.fetchone()[0]

    # Check for Chinese characters
    chinese_count = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')

    print(f"Node {node_id}: {size} chars, {chinese_count} Chinese chars")
    if size < 6000:
        print(f"WARNING: Size {size} < 6000 target!")
    if chinese_count < 50:
        print(f"WARNING: Only {chinese_count} Chinese chars!")

    conn.close()

if __name__ == '__main__':
    main()
