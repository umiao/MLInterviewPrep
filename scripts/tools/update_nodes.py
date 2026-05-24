#!/usr/bin/env python3
# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Update framework_nodes with expanded Chinese translations."""
import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mle_prep.db')

def update_node(node_id, content):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (content, node_id))
    conn.commit()
    cur.execute('SELECT LENGTH(description) FROM framework_nodes WHERE id = ?', (node_id,))
    length = cur.fetchone()[0]
    conn.close()
    return length

def get_node(node_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT description FROM framework_nodes WHERE id = ?', (node_id,))
    result = cur.fetchone()[0]
    conn.close()
    return result

if __name__ == '__main__':
    action = sys.argv[1]
    node_id = int(sys.argv[2])

    if action == 'get':
        print(get_node(node_id))
    elif action == 'update':
        content_file = sys.argv[3]
        with open(content_file, encoding='utf-8') as f:
            content = f.read()
        length = update_node(node_id, content)
        print(f'Node {node_id} updated: {length} chars')
    elif action == 'length':
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT LENGTH(description) FROM framework_nodes WHERE id = ?', (node_id,))
        print(cur.fetchone()[0])
        conn.close()
