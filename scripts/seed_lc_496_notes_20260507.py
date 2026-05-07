"""Seed: T-P1-793 -- LC 496 'Next Greater Element I' 简略 notes.

Discord drop 2026-05-07 (msg 1501827921680138421): user provided the
canonical monotonic-stack solution and asked for a 简略 (concise) note
attached to problems.id=299 (leetcode_id=496) and listed in the
Google R2 Coding Index Stack / 单调栈 section.

Per user 简略 directive: keep notes short -- single solution, three
key points (precompute on nums2 / stack pop on >, push always /
linear lookup), 易错 in two lines, no follow-up expansion.

Sets:
  - notes (Chinese-prose 简略 format, ~1.2KB)
  - family = 'stack', pattern = 'monotonic-stack'
    (consistent with LC 1128 'Fountain Flood' and LC 1673)
  - framework_node_id = 46 ('Stack / Queue')
  - is_completed = 1
  - last_attempted_at = now()

Backs up DB before mutating. Idempotent via SHA-256 hash of NOTES.
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

LEETCODE_ID = 496
EXPECTED_DB_ID = 299
FAMILY_SLUG = "stack"
PATTERN_SLUG = "monotonic-stack"
FRAMEWORK_NODE_ID = 46  # pillar1.data_structures.stack_queue

NOTES = """## Next Greater Element I (LC 496)

### 思路 (简略)

`nums1` 是 `nums2` 的子集, 求 `nums1` 中每个元素在 `nums2` 中右侧第一个比它大的值。**单调递减栈一遍预处理 nums2**, 用 hash 表把每个值映射到它的"下一个更大", 然后查表即可。

### 解法

```python
class Solution:
    def nextGreaterElement(self, nums1: List[int], nums2: List[int]) -> List[int]:
        n = len(nums1)
        ans = [-1] * n

        stack = []
        val2NextLarger = defaultdict(int)

        for i, v in enumerate(nums2):
            while stack and v > stack[-1]:
                val2NextLarger[stack[-1]] = v
                stack.pop()
            stack.append(v)

        for i in range(n):
            if nums1[i] in val2NextLarger:
                ans[i] = val2NextLarger[nums1[i]]

        return ans
```

- 时间 $O(n + m)$ -- n = len(nums2), m = len(nums1); 每个 nums2 元素至多一次入栈 / 出栈
- 空间 $O(n)$ -- 栈 + hash 表

### 关键点

1. **单调递减栈**: 栈底 -> 栈顶 严格递减; 一旦遇到更大值, 把所有 `<` 的栈顶元素出栈并赋值它们的 nextLarger.
2. **题目保证 nums2 元素互异**, 所以可以直接拿值当 hash 键 -- 不互异要改成下标键。
3. **没有 nextLarger 的元素不进 hash 表**, 所以 nums1 查不到 -> 默认 `-1` (ans 初始化已处理)。

### 易错

- pop 条件用严格 `>` 不是 `>=` -- 等值不 pop (题目保证互异其实无所谓, 但模板要稳)。
- nums1 查表用 `in` 判断是否存在, 别直接 `val2NextLarger[nums1[i]]` -- defaultdict 会插入 0 污染。
- **变体 LC 503 是循环数组**, 把 nums 串两遍 (i % n) 跑同款单调栈; **变体 LC 739 Daily Temperatures** 是同模板但栈存下标。
"""


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

    new_notes_hash = sha256(NOTES)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, leetcode_id, title, is_completed, family, pattern, "
            "framework_node_id, notes "
            "FROM problems WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] No row for leetcode_id={LEETCODE_ID}")
            return 1

        pid, lc, title, is_completed, family, pattern, fwn_id, old_notes = row
        if pid != EXPECTED_DB_ID:
            print(f"[WARN] LC {lc} db id={pid} (expected {EXPECTED_DB_ID}); "
                  f"continuing with actual id")

        old_hash = sha256(old_notes) if old_notes else None
        already_complete = (
            is_completed == 1
            and family == FAMILY_SLUG
            and pattern == PATTERN_SLUG
            and fwn_id == FRAMEWORK_NODE_ID
            and old_hash == new_notes_hash
        )
        if already_complete:
            print(f"[SKIP] LC {lc} (id={pid}) already in target state")
            print(f"[PASS] is_completed={is_completed} family={family!r} "
                  f"pattern={pattern!r} framework_node_id={fwn_id} "
                  f"notes_hash={new_notes_hash[:12]}")
            return 0

        print(f"[INFO] Pre: is_completed={is_completed} family={family!r} "
              f"pattern={pattern!r} framework_node_id={fwn_id} "
              f"notes_len={len(old_notes) if old_notes else 0}")
        print(f"[INFO] New: is_completed=1 family={FAMILY_SLUG!r} "
              f"pattern={PATTERN_SLUG!r} framework_node_id={FRAMEWORK_NODE_ID} "
              f"notes_len={len(NOTES)} hash={new_notes_hash[:12]}")

        backup_db()

        conn.execute(
            "UPDATE problems SET is_completed = 1, family = ?, pattern = ?, "
            "framework_node_id = ?, notes = ?, "
            "last_attempted_at = ? "
            "WHERE id = ?",
            (
                FAMILY_SLUG,
                PATTERN_SLUG,
                FRAMEWORK_NODE_ID,
                NOTES,
                datetime.now().isoformat(timespec="seconds"),
                pid,
            ),
        )
        conn.commit()

        check = conn.execute(
            "SELECT is_completed, family, pattern, framework_node_id, notes "
            "FROM problems WHERE id = ?",
            (pid,),
        ).fetchone()
        post_hash = sha256(check[4])
        if (
            check[0] != 1
            or check[1] != FAMILY_SLUG
            or check[2] != PATTERN_SLUG
            or check[3] != FRAMEWORK_NODE_ID
            or post_hash != new_notes_hash
        ):
            print("[FAIL] Post-update mismatch:")
            print(f"  is_completed={check[0]} (want 1)")
            print(f"  family={check[1]!r} (want {FAMILY_SLUG!r})")
            print(f"  pattern={check[2]!r} (want {PATTERN_SLUG!r})")
            print(f"  framework_node_id={check[3]} (want {FRAMEWORK_NODE_ID})")
            print(f"  notes_hash={post_hash[:12]} (want {new_notes_hash[:12]})")
            return 1

        print(f"[DONE] LC {lc} (id={pid}) updated")
        print(f"[PASS] is_completed=1 family={FAMILY_SLUG!r} "
              f"pattern={PATTERN_SLUG!r} framework_node_id={FRAMEWORK_NODE_ID} "
              f"notes_len={len(check[4])} hash={post_hash[:12]}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
