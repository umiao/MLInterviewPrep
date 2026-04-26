"""Seed: T-P1-616 -- Rewrite LC#4 (id=89) notes with sentinel + 4-fact mental model.

Replaces problems.notes for id=89 (leetcode_id=4, "Median of Two Sorted Arrays")
with the user-approved sentinel-based half-open partition implementation and a
4-fact mental-model framing in the "thinking" section.

Idempotent: SHA-256 hash of NEW_NOTES is compared against the existing row;
a second run prints [SKIP] and exits 0 when the row already matches.

DB backup: copies data/mle_prep.db to data/mle_prep.db.bak_pre_lc4_notes_rewrite
before mutating, but only the first time (skips backup when [SKIP]).
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
BACKUP_PATH = DB_PATH.with_name("mle_prep.db.bak_pre_lc4_notes_rewrite")

LEETCODE_ID = 4
EXPECTED_DB_ID = 89

NEW_NOTES = """## Median of Two Sorted Arrays

### 思路
便于记忆的心智模型 -- 记住这 4 件事就行,其他都是推导出来的:

1. **谁短二分谁** -- 保证 `i in [0, n1]`,`j` 是被动算出来的,这样 `j` 不会越界,二分空间也最小,$O(\\log \\min(m, n))$ 来自这一步。
2. **`half = (total + 1) // 2`** -- `+1` 让奇数情况下左半多 1 个元素,中位数就是 `max(left)`,奇偶分支只在最后返回时分一次。
3. **正确性条件**: `left1 <= right2 AND left2 <= right1`(交叉比较)-- 命中即左半整体 <= 右半,切分线就是答案。
4. **失败时的方向**: 违反哪个条件就反向调整 `i`:
   - `left1 > right2` -> nums1 给左边太多了 -> `i` 减小(`iEnd = i`)
   - `left2 > right1` -> nums1 给左边太少了 -> `i` 增大(`iBeg = i + 1`)

底层算法是 **partition binary search**: 在较短数组上二分切分点 $i$,用 sentinel ($\\pm \\infty$) 取代 4 种边界分支,命中正确性条件就直接返回。

### 我的题解
```python
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        n1, n2 = len(nums1), len(nums2)
        if n1 > n2:
            n1, n2 = n2, n1
            nums1, nums2 = nums2, nums1

        # once we determine the split point in nums1, nums2 is determined
        totalLen = n1 + n2
        # we want to find ideal split like:  nums1[:i] and nums2[:j]

        iBeg, iEnd = 0, n1 + 1  # it is legal to iterate to [:n1]

        while iBeg < iEnd:
            i = iBeg + (iEnd - iBeg) // 2
            j = (totalLen + 1) // 2 - i

            iLeftFirstElement = nums1[i - 1] if i >= 1 else float('-inf')
            iRightFirstElement = nums1[i] if i < n1 else float('inf')
            jLeftFirstElement = nums2[j - 1] if j >= 1 else float('-inf')
            jRightFirstElement = nums2[j] if j < n2 else float('inf')

            if iLeftFirstElement > jRightFirstElement:
                iEnd = i
            elif iRightFirstElement < jLeftFirstElement:
                iBeg = i + 1
            else:
                if totalLen % 2 == 1:
                    return max(iLeftFirstElement, jLeftFirstElement)
                else:
                    ret = max(iLeftFirstElement, jLeftFirstElement) + min(iRightFirstElement, jRightFirstElement)
                    ret = ret / 2
                    return ret

        return
```

### 注意要点
1. **Sentinel `±inf` 取代 4 种边界分支**: 旧版用 `if i == 0 / j == 0 / i == n1 / j == n2` 4 路计算 `leftMax / rightMin`,最容易写错且分支多;新版直接写 `nums1[i - 1] if i >= 1 else float('-inf')`,让边界自动满足交叉条件 (`-inf <= 任何值 <= +inf`),代码瘦身一半。
2. **Half-open `while iBeg < iEnd` 避免 ±1 off-by-one**: 闭区间 `while iMin <= iMax` 加上 `iMax = i - 1 / iMin = i + 1` 容易写出无限循环或漏掉端点;半开区间 `[iBeg, iEnd)` 配合 `iEnd = i / iBeg = i + 1` 是 Python 切片语义的自然延伸,循环必然收敛到 `iBeg == iEnd`。
3. **Cross-check 条件直接对应失败方向**: `iLeftFirstElement > jRightFirstElement` 与 `iRightFirstElement < jLeftFirstElement` 是对称的两个失败分支,命中任一就反向调 `i`,不需要额外判断哪边过大,`if / elif / else` 三段结构非常对仗。
4. **`iEnd = n1 + 1` 而非 `n1`**: 因为 `iBeg, iEnd` 是半开区间,而 `i = n1`(nums1 全部进左半)是合法切分点,所以上界写到 `n1 + 1` 才能覆盖。
5. **`(totalLen + 1) // 2 - i` 一行算 `j`**: `+1` 让奇数总长时左半多 1,中位数就是 `max(iLeftFirstElement, jLeftFirstElement)`;偶数总长时左右两半等大,取 `(max(left) + min(right)) / 2`。

### 复杂度
- 时间: $O(\\log(\\min(m, n)))$ -- 在较短数组上二分
- 空间: $O(1)$
"""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def backup_db() -> Path:
    if BACKUP_PATH.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated = BACKUP_PATH.with_name(BACKUP_PATH.name + f".{stamp}")
        shutil.move(str(BACKUP_PATH), str(rotated))
        print(f"[INFO] Existing backup rotated -> {rotated.name}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"[INFO] DB backup -> {BACKUP_PATH.name}")
    return BACKUP_PATH


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    new_hash = sha256(NEW_NOTES)
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, leetcode_id, title, notes FROM problems "
            "WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] No row for leetcode_id={LEETCODE_ID}")
            return 1

        pid, lc, title, old_notes = row
        if pid != EXPECTED_DB_ID:
            print(f"[WARN] LC {lc} db id={pid} (expected {EXPECTED_DB_ID}); "
                  f"continuing with actual id")

        old_hash = sha256(old_notes) if old_notes else None
        if old_hash == new_hash:
            print(f"[SKIP] LC {lc} (id={pid}) notes already match target hash "
                  f"({new_hash[:12]})")
            print(f"[PASS] notes_len={len(old_notes)}")
            return 0

        print(f"[INFO] Pre: notes_len={len(old_notes) if old_notes else 0} "
              f"hash={(old_hash or '----')[:12]}")
        print(f"[INFO] New: notes_len={len(NEW_NOTES)} hash={new_hash[:12]}")

        backup_db()

        conn.execute(
            "UPDATE problems SET notes = ?, last_attempted_at = ? WHERE id = ?",
            (
                NEW_NOTES,
                datetime.now().isoformat(timespec="seconds"),
                pid,
            ),
        )
        conn.commit()

        check = conn.execute(
            "SELECT notes FROM problems WHERE id = ?",
            (pid,),
        ).fetchone()
        post_hash = sha256(check[0])
        if post_hash != new_hash:
            print(f"[FAIL] Post-update hash mismatch: "
                  f"{post_hash[:12]} != {new_hash[:12]}")
            return 1

        print(f"[DONE] LC {lc} (id={pid}) notes updated, "
              f"len={len(check[0])} hash={post_hash[:12]}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
