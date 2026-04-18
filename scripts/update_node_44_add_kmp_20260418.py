"""Seed: T-P1-508 -- Expand KMP section in Array/String node (n44).

Part B of KG-CONTENT-01. Replaces the one-line KMP bullet inside
n44's "String Specifics" section with a dedicated KMP subsection
(core insight + next-array definition + compact Python template +
complexity + deeplink to the new Quick Index KMP family group).

Safety:
  1. Takes a timestamped .bak snapshot of mle_prep.db before touching
     the row.
  2. Inserts the old description into
     framework_nodes_description_history so the edit is recoverable.
  3. Idempotent: if the DB row already matches the new description
     (same content hash), exits fast without re-archiving or re-writing.
  4. Post-update structural guard: verifies the description still
     starts with "# Array / String".
"""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 44
TITLE_GUARD = "# Array / String"

OLD_BULLET_MARKER = (
    "- **Substring Search** (\u5b50\u4e32\u641c\u7d22)\uff1a**Knuth-Morris-Pratt** (KMP) "
    "\u7b97\u6cd5\u8fbe\u5230 $$O(n + m)$$\uff1bPython \u7684 `in` \u8fd0\u7b97\u7b26"
    "\u4f7f\u7528 Boyer-Moore \u7684\u53d8\u4f53"
)

NEW_KMP_SUBSECTION = """### KMP Substring Search

**Knuth-Morris-Pratt** (KMP, 克努斯-莫里斯-普拉特算法) 是子串匹配的经典线性算法。直觉：暴力解法每次失配都把文本指针回退重来，丢掉了"前缀已经匹配"这段免费情报；KMP 通过预处理 `next` 数组复用这段信息——失配时文本指针 `i` 从不回退，只让模式指针 `j` 跳到 `next[j-1]` 继续比对。

**`next` 数组定义**：`next[i]` = 模式串 `P[0..i]` 的最长相等**真前后缀** (proper prefix/suffix，不能等于自身) 长度。例如 `P = "abab"` 对应 `next = [0, 0, 1, 2]`——`"abab"` 的真前后缀为 `"ab"`，长度为 2。

```python
def kmp(text: str, pattern: str) -> int:
    # Build next-array (longest proper prefix == suffix for each prefix of pattern).
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    nxt = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = nxt[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        nxt[i] = j
    # Main scan: text pointer i never retreats.
    j = 0
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = nxt[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            return i - m + 1
    return -1
```

注意 `next` 构建阶段就是模式串在自身上的 KMP 扫描——与主匹配共享同一套"双指针 + 失配回退 + 匹配前进"骨架。复杂度 $O(n + m)$ 时间、$O(m)$ 空间（`next` 数组）；Python 内置 `str.find` / `in` 运算符使用 **Boyer-Moore** (BM, 博耶-摩尔算法) 的变体。

→ 练习题见 [KMP 家族](/quick-index?section=lc)（String Matching (KMP family) 分组）。

"""


def build_new_description(old: str) -> str:
    """Return the new description with the one-line KMP bullet removed and
    the KMP subsection inserted right before the '### Two-Pointer Technique'
    heading.
    """
    if OLD_BULLET_MARKER not in old:
        raise RuntimeError(
            "Cannot locate old Substring Search bullet to replace. "
            "The node description may have been edited externally."
        )
    # 1) Remove the old bullet line (and its trailing newline).
    without_bullet = old.replace(OLD_BULLET_MARKER + "\n", "", 1)
    # 2) Insert new subsection just before "### Two-Pointer Technique".
    anchor = "### Two-Pointer Technique"
    if anchor not in without_bullet:
        raise RuntimeError(
            f"Cannot locate anchor heading {anchor!r} for subsection insert."
        )
    return without_bullet.replace(anchor, NEW_KMP_SUBSECTION + anchor, 1)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def backup_db() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(DB_PATH, dst)
    print(f"[INFO] DB backup -> {dst.name}")
    return dst


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            return 1
        old_desc = row[0]
        # Idempotency: if the old bullet is already gone AND the new
        # subsection anchor is already present, the update was applied.
        already_applied = (
            OLD_BULLET_MARKER not in old_desc
            and "### KMP Substring Search" in old_desc
        )
        if already_applied:
            print("[SKIP] Node 44 already updated with expanded KMP subsection.")
            print(f"[PASS] Current length = {len(old_desc.encode('utf-8'))} bytes")
            return 0

        new_desc = build_new_description(old_desc)
        if new_desc == old_desc:
            print("[SKIP] No change needed.")
            return 0

        print(
            f"[INFO] Byte length: {len(old_desc.encode('utf-8'))} "
            f"-> {len(new_desc.encode('utf-8'))}"
        )
        print(f"[INFO] Old hash: {sha256(old_desc)[:12]}")
        print(f"[INFO] New hash: {sha256(new_desc)[:12]}")

        backup_db()

        # Archive old description first.
        conn.execute(
            "INSERT INTO framework_nodes_description_history(node_id, description) "
            "VALUES (?, ?)",
            (NODE_ID, old_desc),
        )
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (new_desc, NODE_ID),
        )
        conn.commit()

        # Verify.
        check = conn.execute(
            "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()[0]
        if not check.startswith(TITLE_GUARD):
            print(f"[FAIL] Post-update structural guard failed: "
                  f"description does not start with {TITLE_GUARD!r}")
            return 1
        if "### KMP Substring Search" not in check:
            print("[FAIL] New KMP subsection missing after update")
            return 1
        if OLD_BULLET_MARKER in check:
            print("[FAIL] Old bullet still present after update")
            return 1
        print(f"[PASS] Node {NODE_ID} updated; length now "
              f"{len(check.encode('utf-8'))} bytes")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
