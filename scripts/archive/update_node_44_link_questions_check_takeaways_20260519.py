"""Seed: n44 (Array/String) -- link Common Interview Questions to the LC
problem bank + mark all Key Takeaways as checked.

Source: Discord 2026-05-19 (msg 1506186139403423754). User asked to (1)
replace the plain "Common Interview Questions" checklist with direct links
into the existing LC problem bank (a bare checklist "可能也不科学"), and
(2) check all "Key Takeaways". The strikethrough->checkmark restyle is a
separate FRONTEND change (src/frontend/.../MarkdownPreview.tsx) -- this seed
only owns the framework_nodes.description content.

All 6 questions resolve to problems already present in `problems`
(verified by leetcode_id): Two Sum=lc1, 3Sum=lc15, Longest Substring=lc3,
Merge Intervals=lc56, Product of Array Except Self=lc238, Trapping Rain
Water=lc42, Minimum Window Substring=lc76. Links use the `lc://<leetcode_id>`
drawer scheme (frontend resolver `/^lc:\\/\\/(\\d+)$/` -> /problems/by-lc/N
-> ProblemDrawer). No `#anchor` suffix (the lc:// regex disallows it).

Safety (mirrors scripts/update_node_44_add_kmp_20260418.py):
  1. Timestamped .bak snapshot of mle_prep.db before the write.
  2. Old description archived into framework_nodes_description_history.
  3. Idempotent: per-block apply -- if a block's OLD text is gone and its
     NEW text is present, that block is treated as already-applied; a
     second run is a clean [SKIP] with no re-archive / no re-write.
  4. Post-update structural guard: description still starts with
     "# Array / String".

Run: python scripts/update_node_44_link_questions_check_takeaways_20260519.py
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

OLD_QUESTIONS = """### Common Interview Questions

- [ ] Two Sum / Three Sum 最优复杂度解法
- [ ] 无重复字符的最长子串
- [ ] 合并区间
- [ ] 除自身以外数组的乘积（不使用除法）
- [ ] 接雨水（双指针或栈方法）
- [ ] 最小覆盖子串"""

NEW_QUESTIONS = """### Common Interview Questions

以下题目均已链接到题库中实际存在的题目，点击题名即可打开题目抽屉（ProblemDrawer）：

- [Two Sum](lc://1)（LC 1 · easy） / [3Sum](lc://15)（LC 15 · medium）——最优复杂度的配对 / 三元组求和
- [Longest Substring Without Repeating Characters](lc://3)（LC 3 · medium）——无重复字符的最长子串（可变滑动窗口）
- [Merge Intervals](lc://56)（LC 56 · medium）——合并区间（按起点排序 + 扫描合并）
- [Product of Array Except Self](lc://238)（LC 238 · medium）——除自身以外数组的乘积（前缀积 / 后缀积，不用除法）
- [Trapping Rain Water](lc://42)（LC 42 · hard）——接雨水（相向双指针 / 单调栈）
- [Minimum Window Substring](lc://76)（LC 76 · hard）——最小覆盖子串（可变滑动窗口 + 计数器）"""

OLD_TAKEAWAYS = """## Key Takeaways

- [x] 有序数组上的双指针可将 $$O(n^2)$$ 降到 $$O(n)$$——总是优先考虑排序
- [ ] 滑动窗口是连续子数组/子串问题的标准方法
- [ ] 前缀和将区间查询转化为 $$O(1)$$ 查找——结合哈希表解决子数组和等于 k 的问题
- [ ] 原地字符串/数组操作需要仔细管理索引——练习读写指针模式
- [ ] MLE 相关：数组操作直接对应 NumPy/PyTorch 中的张量操作"""

NEW_TAKEAWAYS = """## Key Takeaways

- [x] 有序数组上的双指针可将 $$O(n^2)$$ 降到 $$O(n)$$——总是优先考虑排序
- [x] 滑动窗口是连续子数组/子串问题的标准方法
- [x] 前缀和将区间查询转化为 $$O(1)$$ 查找——结合哈希表解决子数组和等于 k 的问题
- [x] 原地字符串/数组操作需要仔细管理索引——练习读写指针模式
- [x] MLE 相关：数组操作直接对应 NumPy/PyTorch 中的张量操作"""

BLOCKS = [
    ("Common Interview Questions", OLD_QUESTIONS, NEW_QUESTIONS),
    ("Key Takeaways", OLD_TAKEAWAYS, NEW_TAKEAWAYS),
]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def backup_db() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(DB_PATH, dst)
    print(f"[INFO] DB backup -> {dst.name}")
    return dst


def apply_blocks(desc: str) -> tuple[str, int]:
    """Apply each (old -> new) block exactly once. Returns (new_desc,
    n_changed). Per-block idempotency: if old is absent but new is present,
    that block is already applied. If neither is present, the content has
    drifted -> raise."""
    changed = 0
    for label, old, new in BLOCKS:
        if old in desc:
            desc = desc.replace(old, new, 1)
            changed += 1
            print(f"[INFO] Block applied: {label}")
        elif new in desc:
            print(f"[SKIP] Block already applied: {label}")
        else:
            raise RuntimeError(
                f"Cannot locate the {label!r} block (neither OLD nor NEW "
                f"text present). Node 44 description drifted -- aborting."
            )
    return desc, changed


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

        new_desc, n_changed = apply_blocks(old_desc)
        if n_changed == 0 or new_desc == old_desc:
            print("[SKIP] Node 44 already linked + all takeaways checked. "
                  f"Length = {len(old_desc.encode('utf-8'))} bytes")
            return 0

        print(
            f"[INFO] Byte length: {len(old_desc.encode('utf-8'))} "
            f"-> {len(new_desc.encode('utf-8'))}"
        )
        print(f"[INFO] Old hash: {sha256(old_desc)[:12]}")
        print(f"[INFO] New hash: {sha256(new_desc)[:12]}")

        backup_db()

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

        check = conn.execute(
            "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()[0]
        if not check.startswith(TITLE_GUARD):
            print(f"[FAIL] Structural guard failed: not starting with "
                  f"{TITLE_GUARD!r}")
            return 1
        for lc in ("lc://1", "lc://15", "lc://3", "lc://56",
                   "lc://238", "lc://42", "lc://76"):
            if f"({lc})" not in check:
                print(f"[FAIL] Expected link ({lc}) missing after update")
                return 1
        if OLD_QUESTIONS in check or OLD_TAKEAWAYS in check:
            print("[FAIL] An OLD block still present after update")
            return 1
        # Every Key Takeaway must be checked: no "- [ ] " after the
        # Key Takeaways heading.
        kt = check.split("## Key Takeaways", 1)[1]
        if "- [ ] " in kt:
            print("[FAIL] Some Key Takeaway is still unchecked")
            return 1
        print(f"[PASS] Node {NODE_ID} updated; length now "
              f"{len(check.encode('utf-8'))} bytes; blocks changed={n_changed}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
