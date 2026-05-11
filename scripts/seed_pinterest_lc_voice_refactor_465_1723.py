"""Seed Pinterest LC notes voice + density refactor (T-P1-777, 2026-05-11).

Pilot scope (per 2026-05-06 17:00 [planning v2] entry + self-decided Q1'/Q2' on 2026-05-11):
- LC 465 (problems.id=214): expand 3 WHY-style comment blocks in Approach A bitmask DP
  code; DROP the orphan "对原始写法的 code review" section (5 PEP-8 nits referencing
  user's original code that is no longer pasted in the notes).
- LC 1723 (problems.id=1067): rename `nxt` -> `dp_next` (6 occurrences in code + 1 in
  "关键点" section); expand 6 WHY-style comment blocks in Approach B 状压 DP code
  (tot[] precompute, dp[mask] semantic, dp_next intro, transition, empty-worker branch,
  return).

NOT in scope this pilot (deferred):
- LC 282 / LC 1244 sibling refactor (will batch after voice confirmed OK).
- Variable renames in LC 465 (subset_sum / dp already clear, no rename).
- Section-level structure changes (识别模板 / 面试节奏 / 对偶讨论 etc. all KEPT).

Idempotent via per-problem sentinels at the very top of `problems.notes`. Re-running
detects the sentinel and skips the UPDATE. Targeted string-replace asserts each OLD
block is present before replacing (loud failure on drift, never silent miss).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LC465_PID = 214
LC465_SENTINEL = "<!-- PINTEREST_LC465_VOICE_REFACTOR_20260511 -->"
LC1723_PID = 1067
LC1723_SENTINEL = "<!-- PINTEREST_LC1723_VOICE_REFACTOR_20260511 -->"

# ============================================================================
# LC 465 (id=214) edits
# ============================================================================

# --- Block 1: subset_sum precompute (expand WHY of lowbit recurrence) ---
LC465_OLD_BLOCK_1 = """        # Precompute subset sums
        subset_sum = [0] * (1 << n)
        for mask in range(1, 1 << n):
            low = mask & -mask
            idx = low.bit_length() - 1
            subset_sum[mask] = subset_sum[mask ^ low] + balances[idx]"""

LC465_NEW_BLOCK_1 = """        # subset_sum[mask] = mask 选出的人 balance 之和.
        # 用 lowbit 递推: 当前 mask 比 "去掉最低位 lowbit" 的前驱只多一个人,
        # 所以每格 O(1) 填, 总共 O(2^n); 不用每个 mask 都现算 O(n) 累加.
        subset_sum = [0] * (1 << n)
        for mask in range(1, 1 << n):
            low = mask & -mask              # 最低 set bit (隔离成单点)
            idx = low.bit_length() - 1      # 该 bit 对应第几个人
            subset_sum[mask] = subset_sum[mask ^ low] + balances[idx]"""

# --- Block 2: dp[mask] semantic + answer formula WHY ---
LC465_OLD_BLOCK_2 = """        # dp[mask] = max # of zero-sum partitions of `mask`; -1 if unreachable
        dp = [-1] * (1 << n)
        dp[0] = 0"""

LC465_NEW_BLOCK_2 = """        # dp[mask] = 把 mask 中的人切成最多多少个不相交 zero-sum 子集; -1 = 切不出来.
        # 答案 = n - dp[(1<<n) - 1]. 为什么是 n - K: 大小 k 的 zero-sum 组内部 k-1 次转账就能结清,
        # 划成 K 组总次数 = Σ(k_i - 1) = n - K, 所以"最少转账" 等价于 "最多分组".
        dp = [-1] * (1 << n)
        dp[0] = 0                           # 空集本身 = 0 组, 合法基底"""

# --- Block 3: submask transition semantic + WHY for zero-sum sub guard ---
LC465_OLD_BLOCK_3 = """        for mask in range(1, 1 << n):
            if subset_sum[mask] != 0:
                continue
            sub = mask
            while sub > 0:
                if subset_sum[sub] == 0 and dp[mask ^ sub] >= 0:
                    dp[mask] = max(dp[mask], 1 + dp[mask ^ sub])
                sub = (sub - 1) & mask"""

LC465_NEW_BLOCK_3 = """        for mask in range(1, 1 << n):
            if subset_sum[mask] != 0:
                continue                    # mask 自己不 balance, 就不可能拆成全 zero-sum 子集的并
            sub = mask
            while sub > 0:                  # (sub-1) & mask: 标准子集枚举模板, 总枚举 O(3^n)
                # 把 sub 当作"一组 zero-sum 子集"切出去, 剩下 mask^sub 递归.
                # 为什么只考虑 subset_sum[sub]==0 的 sub: 否则 mask^sub 必然也不 balance
                # (0 - 非零 != 0), 一定切不成, 提前过滤掉无效转移.
                if subset_sum[sub] == 0 and dp[mask ^ sub] >= 0:
                    dp[mask] = max(dp[mask], 1 + dp[mask ^ sub])
                sub = (sub - 1) & mask"""

# --- Section to DROP: orphan "对原始写法的 code review" ---
LC465_OLD_REVIEW_SECTION = """**对原始写法的 code review**：
- `self.ans = float('inf')` —— 未使用，删掉。
- 用 `float('-inf')` 表示不可达 —— 换成 `-1` 配合 `>= 0` 判断更清晰（逻辑等价，少一点 magic）。
- 缺 `n == 0` 保护（虽然空 balances 会返回 `n - dp[0] = 0`，能 work，但显式更稳）。
- `balanceList` → `balances`（PEP8）。
- 算法本身正确而干净。`i & -i` 取最低位 + `bit_length() - 1` 取下标是 idiomatic 的位运算写法。

"""

# ============================================================================
# LC 1723 (id=1067) edits
# ============================================================================

# Single big string-replace covering: tot block + dp/dp_next intro + transition +
# empty-worker branch + return; all in one block to keep replace atomicity.
LC1723_OLD_CODE_BLOCK = """def minimumTimeRequired(jobs: list[int], k: int) -> int:
    n = len(jobs)
    full = 1 << n
    tot = [0] * full
    for mask in range(1, full):
        low = mask & -mask
        tot[mask] = tot[mask ^ low] + jobs[low.bit_length() - 1]

    dp = tot[:]  # k=1 时就是自己
    for _ in range(1, k):
        nxt = [float('inf')] * full
        for mask in range(full):
            sub = mask
            while sub > 0:
                nxt[mask] = min(nxt[mask], max(dp[mask ^ sub], tot[sub]))
                sub = (sub - 1) & mask
            nxt[mask] = min(nxt[mask], dp[mask])  # 允许这个工人空跑
        dp = nxt
    return dp[full - 1]"""

LC1723_NEW_CODE_BLOCK = """def minimumTimeRequired(jobs: list[int], k: int) -> int:
    n = len(jobs)
    full = 1 << n

    # tot[mask] = mask 选中的工作时长之和.
    # 用 lowbit 递推 O(1) 填一格, 总共 O(2^n); 不用每个 mask 现算 O(n) 累加.
    tot = [0] * full
    for mask in range(1, full):
        low = mask & -mask
        tot[mask] = tot[mask ^ low] + jobs[low.bit_length() - 1]

    # dp[mask] (当前层 w 个工人) = 前 w 个工人处理完 mask 这些工作时的最小 makespan.
    # 起点 w=1: 唯一的工人必须扛 mask 全部 → dp[mask] = tot[mask].
    dp = tot[:]
    for _ in range(1, k):
        # dp_next[mask] = w+1 个工人处理 mask 时的最小 makespan;
        # 新工人接走 sub, 前 w 个工人在 mask^sub 上做.
        dp_next = [float('inf')] * full
        for mask in range(full):
            sub = mask
            while sub > 0:                       # (sub-1) & mask: 子集枚举模板, 总 O(3^n)
                # 转移: makespan = max(前 w 工人在 mask^sub 上的最大负载, 新工人负载 tot[sub]).
                # min over sub 选最优分配.
                dp_next[mask] = min(dp_next[mask], max(dp[mask ^ sub], tot[sub]))
                sub = (sub - 1) & mask
            # while 循环不覆盖 sub=∅. 显式补一个"新工人空跑"分支:
            # 为什么必须: k > "mask 上的有效非空分组数" 时一定有工人空跑, 没这行 dp_next[mask]
            # 会留在 inf, 最终答案错算成 inf.
            dp_next[mask] = min(dp_next[mask], dp[mask])
        dp = dp_next
    # k 个工人覆盖 "全 1 mask" (全部 n 个工作) 的最小 makespan.
    return dp[full - 1]"""

# Also update the "关键点" prose: it references `nxt[mask]` which must rename.
LC1723_OLD_KEYPOINT = "允许某个工人空跑（`nxt[mask] = min(nxt[mask], dp[mask])`），否则 `k > 有效分组数`时会漏解。"
LC1723_NEW_KEYPOINT = "允许某个工人空跑（`dp_next[mask] = min(dp_next[mask], dp[mask])`），否则 `k > 有效分组数`时会漏解。"


# ============================================================================
# Driver
# ============================================================================

def apply_lc465(notes: str) -> str:
    """Returns refactored LC 465 notes. Asserts each anchor is present."""
    for label, old in [
        ("BLOCK_1 (subset_sum)", LC465_OLD_BLOCK_1),
        ("BLOCK_2 (dp semantic)", LC465_OLD_BLOCK_2),
        ("BLOCK_3 (submask transition)", LC465_OLD_BLOCK_3),
        ("REVIEW_SECTION (orphan)", LC465_OLD_REVIEW_SECTION),
    ]:
        if old not in notes:
            raise SystemExit(f"[FAIL] LC 465 anchor missing: {label}")

    new = notes
    new = new.replace(LC465_OLD_BLOCK_1, LC465_NEW_BLOCK_1, 1)
    new = new.replace(LC465_OLD_BLOCK_2, LC465_NEW_BLOCK_2, 1)
    new = new.replace(LC465_OLD_BLOCK_3, LC465_NEW_BLOCK_3, 1)
    new = new.replace(LC465_OLD_REVIEW_SECTION, "", 1)
    return LC465_SENTINEL + "\n" + new


def apply_lc1723(notes: str) -> str:
    """Returns refactored LC 1723 notes. Asserts each anchor is present."""
    for label, old in [
        ("CODE_BLOCK (Approach B 状压 DP)", LC1723_OLD_CODE_BLOCK),
        ("KEYPOINT (nxt -> dp_next prose)", LC1723_OLD_KEYPOINT),
    ]:
        if old not in notes:
            raise SystemExit(f"[FAIL] LC 1723 anchor missing: {label}")

    new = notes
    new = new.replace(LC1723_OLD_CODE_BLOCK, LC1723_NEW_CODE_BLOCK, 1)
    new = new.replace(LC1723_OLD_KEYPOINT, LC1723_NEW_KEYPOINT, 1)
    return LC1723_SENTINEL + "\n" + new


def upsert_one(
    conn: sqlite3.Connection,
    *,
    pid: int,
    sentinel: str,
    transform,
    label: str,
) -> None:
    row = conn.execute("SELECT notes FROM problems WHERE id = ?", (pid,)).fetchone()
    if row is None:
        raise SystemExit(f"[FAIL] problems.id={pid} not found")
    existing = row[0] or ""
    if sentinel in existing:
        print(f"  {label} (id={pid}): [SKIP] sentinel already present, no-op")
        return
    new_notes = transform(existing)
    conn.execute("UPDATE problems SET notes = ? WHERE id = ?", (new_notes, pid))
    print(f"  {label} (id={pid}): [WRITE] {len(existing)} -> {len(new_notes)} chars")


def seed() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"[FAIL] DB not found at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("BEGIN")
        print("=== problems.notes voice refactor ===")
        upsert_one(
            conn, pid=LC465_PID, sentinel=LC465_SENTINEL,
            transform=apply_lc465, label="LC 465 Optimal Account Balancing",
        )
        upsert_one(
            conn, pid=LC1723_PID, sentinel=LC1723_SENTINEL,
            transform=apply_lc1723, label="LC 1723 Find Min Time to Finish All Jobs",
        )
        conn.execute("COMMIT")

        print("\n=== verify ===")
        for pid in (LC465_PID, LC1723_PID):
            r = conn.execute(
                "SELECT id, leetcode_id, title, length(notes) FROM problems WHERE id = ?",
                (pid,),
            ).fetchone()
            print(f"  {r}")
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    seed()
