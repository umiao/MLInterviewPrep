"""Seed: T-P1-794 -- LC 312 'Burst Balloons' interval-DP notes.

Discord drop 2026-05-07 (msg 1501832530905661570): user-provided 区间 DP
classic. The key insight is **enumerate which balloon bursts LAST in the
interval** (not first), so left/right subintervals decouple cleanly.

Sets:
  - notes (Chinese-prose interval-DP format, ~2KB)
  - family = 'dp', pattern = 'interval-dp'
    (was pattern='dp' -- specializing to 'interval-dp' aligns with the
     index section name 'DP / Interval')
  - framework_node_id = 54 ('Dynamic Programming')
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

LEETCODE_ID = 312
EXPECTED_DB_ID = 124
FAMILY_SLUG = "dp"
PATTERN_SLUG = "interval-dp"
FRAMEWORK_NODE_ID = 54  # pillar1.algorithm_paradigms.dynamic_programming

NOTES = """## Burst Balloons (LC 312)

### 核心思路: **倒着想**

正向枚举"先戳哪个"会让左右子问题互相耦合 -- 戳掉 i 之后, i-1 和 i+1 变相邻, 问题没法拆。

**反过来枚举区间里"最后被戳"的气球 k**。当 k 是最后一个时, 区间内其他气球都已经爆了, k 此刻的左右邻居就是区间**外**最近的存活气球。这样以 k 为分界, 左右两个子区间天然独立, 可以递归求解。

### 状态与转移

- 首尾 padding 两个 1, 把所有边界 case 统一掉
- `dfs(L, R)`: 戳爆闭区间 `[L, R]` 内所有气球的最大收益
- 枚举 k ∈ [L, R] 作为**最后**戳爆的气球, k 的左右邻居是 `nums[L-1]` 和 `nums[R+1]` (区间外的存活者):

$$
dfs(L, R) = \\max_{k \\in [L, R]} \\big( dfs(L, k-1) + dfs(k+1, R) + nums[L-1] \\cdot nums[k] \\cdot nums[R+1] \\big)
$$

- Base case: `L > R` 时区间为空, 返回 0
- 答案: `dfs(1, n-2)` (去掉两端虚拟的 1)

### 复杂度

- 时间 $O(n^3)$: $O(n^2)$ 个状态, 每个状态 $O(n)$ 转移
- 空间 $O(n^2)$: 记忆化

### 代码

```python
class Solution:
    def maxCoins(self, nums: List[int]) -> int:
        # 首尾各加一个 1, 统一边界处理
        nums = [1] + nums + [1]
        n = len(nums)
        memo = {}

        def dfs(L, R):
            # 空区间无气球可戳
            if L > R:
                return 0
            if (L, R) in memo:
                return memo[(L, R)]

            ret = 0
            # 枚举 k 作为 [L, R] 中最后一个被戳爆的气球
            # 此时 k 的左右邻居是区间外的 nums[L-1] 和 nums[R+1]
            for k in range(L, R + 1):
                cur = dfs(L, k - 1) + dfs(k + 1, R) + nums[L - 1] * nums[k] * nums[R + 1]
                ret = max(ret, cur)

            memo[(L, R)] = ret
            return ret

        return dfs(1, n - 2)
```

### 易错点

写区间 DP 时一定要分清: 你定义的 L、R 是**待戳的两端**还是**幸存的边界**。

- **闭区间 `[L, R]`** (本题写法): L、R 是要戳的, 所以邻居要取**区间外** `nums[L-1]` 和 `nums[R+1]`
- **开区间 `(L, R)`**: L、R 是幸存的边界, 邻居直接取 `nums[L]` 和 `nums[R]`

两种写法都对, 但下标差一格, 搞混就会得到错误答案。

### 同族 (Interval DP)

- **LC 1547 Minimum Cost to Cut a Stick**: 同款"最后一刀"反向枚举, cost = 当前区间长度 + 左右子区间。
- **LC 1000 Minimum Cost to Merge Stones**: 区间 DP + k 路合并约束 (`(n-1) % (k-1) == 0`)。
- **LC 516 Longest Palindromic Subsequence**: 经典区间 DP 但是正向 (两端字符相等 / 不相等的二选一), 不需要"最后一步"反向技巧。
- **LC 1130 Minimum Cost Tree From Leaf Values**: 区间 DP / 单调栈双解。
- **LC 87 Scramble String**: 区间 DP 对 (i, j, len) 三维状态。

### 一句话总结

Burst Balloons = **区间 DP + "最后戳爆"反向枚举** (正向耦合反向解耦) + 首尾 padding 1 统一边界。$O(n^3)$。**核心套路**: 正向想不通的区间问题, 试试反向枚举"最后一步"。
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
