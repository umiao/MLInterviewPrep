"""Seed: T-P1-790 -- LC 1673 'Find the Most Competitive Subsequence' notes.

Discord drop 2026-05-07 (msg 1501821359590867046): user-provided 单调栈 + 删除预算
solution to be attached to problems.id=804 (leetcode_id=1673), and listed in the
Google R2 Coding Index (doc id=92, 'Stack / 单调栈' section). This script handles
the per-problem notes UPSERT; the index entry is appended in
`scripts/seed_google_r2_coding_index_20260502.py` (re-run after this).

Sets:
  - notes (Chinese-prose 5-section format matching seed_lc_399 / seed_lc_778
    convention: 思路 / 解法 / 关键不变量 / 易错点 / 同族)
  - family = 'stack', pattern = 'monotonic-stack'
    (consistent with LC 1128 'Fountain Flood' which is the closest entry in
     the same Stack / 单调栈 index group)
  - framework_node_id = 46 ('Stack / Queue' under pillar1.data_structures)
  - is_completed = 1
  - last_attempted_at = now()

Backs up DB before mutating. Idempotent via SHA-256 hash of NOTES payload.
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

LEETCODE_ID = 1673
EXPECTED_DB_ID = 804
FAMILY_SLUG = "stack"
PATTERN_SLUG = "monotonic-stack"
FRAMEWORK_NODE_ID = 46  # pillar1.data_structures.stack_queue

NOTES = """## Find the Most Competitive Subsequence (LC 1673)

### 思路: 单调栈 + 删除预算

要从 nums 中选长度为 k 的子序列, 使其字典序最小。等价于: 从 nums 中**删除 n - k 个元素**, 让剩下的序列字典序最小。

贪心: 从左往右扫, 如果当前元素 nums[i] 比已选序列的末尾更小, 那把末尾换成 nums[i] 一定更优 (前缀变小)。但替换会消耗一次"删除额度", 所以维护一个计数器 `toDel = n - k` 作为预算。这是 LC 402 "Remove K Digits" 同款套路, 把"取 k 个最小子序列"和"删 (n-k) 个数字"对偶起来即可。

### 解法: 单调栈 (递增) 一遍扫

```python
class Solution:
    def mostCompetitive(self, nums: List[int], k: int) -> List[int]:
        toDel = len(nums) - k
        stack = []
        for num in nums:
            while stack and stack[-1] > num and toDel > 0:
                stack.pop()
                toDel -= 1
            stack.append(num)
        return stack[:k]
```

- 时间: O(n) -- 每个元素至多入栈/出栈一次, 摊还 O(1)
- 空间: O(k) -- 栈最终长度 = k

### 关键不变量

1. **`toDel` 是"还可以丢弃几个元素"的预算**。pop 一次消耗 1; 预算耗尽后, 后续元素只能无条件 `append`。
2. **栈始终单调不降地接近"最优前缀"**。pop 的条件三件套: 栈非空 + 栈顶 `>` num + 还有预算。三者缺一不可 (尤其预算耗尽要立刻停止 pop, 否则会把栈底删空)。
3. **末尾切片 `stack[:k]`** 处理"预算没花完"的情况: 数组本身偏递增时, while 几乎不触发, 最终栈长度 > k, 切前 k 个即得字典序最小子序列。

### 易错点

- **pop 条件用 `>` 还是 `>=`**? 用严格 `>`。等值不 pop -- 等值替换不会让前缀更小, 反而浪费预算。
- **`toDel == 0` 后必须无条件 append**, 不能跳过当前元素 -- 跳过等于额外删除, 预算已用尽。
- **结尾切片不可省**。即使 toDel 用完, 栈长度也可能 > k (例如 nums 严格递增, while 永不触发, 全部 append, 栈长度 = n)。
- **空数组 / k == n**: 切片自动覆盖, 不需要特判。
- **k == 0**: 返回 `[]`; while pop 会把整栈扫光, 切 [:0] 也对。

### 同族 (单调栈 + 删除预算)

- **LC 402 Remove K Digits**: 给字符串数字, 删 k 个使剩下数字最小。**完全同模板**, 只是预算从 `n - k` 换成 `k`, 字典序比较同样递增栈。
- **LC 316 Remove Duplicate Letters / LC 1081 Smallest Subsequence of Distinct Characters**: 单调栈 + 字符必须保留至少一次 (后续计数), 比 LC 1673 多一层"保留约束"。
- **LC 84 Largest Rectangle in Histogram / LC 739 Daily Temperatures**: 同是单调栈一族, 但目标是"找两侧最近大/小元素", 不涉及预算。
- **LC 321 Create Maximum Number**: 把 LC 1673 拓展到两数组合并, 枚举从两边各取 i / k-i, 然后 merge -- 字典序最大版本。

### Follow-up

- **要求字典序最大子序列**? while 条件改 `stack[-1] < num`, 其余不变 (递减栈).
- **流式输入 / 在线版**? 预算 toDel 已知 (n 已知) 时方法不变; n 未知则退化成 sliding-window quantile 类问题, 单调栈不再适用。
- **k 很大、值域很小**? 仍然 O(n), 单调栈与值域无关 -- 与 selection / heap 路线区分清楚。
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
