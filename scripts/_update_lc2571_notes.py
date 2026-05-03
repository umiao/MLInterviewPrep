"""Idempotent: rewrite LC 2571 notes (Min Ops to Reduce Integer to 0) +
seed Uber problem_company_tags row.

LC 2571 是 "位运算贪心" 家族的 canonical 题目 ——
每次 ±2^k, 求把 n 减到 0 的最少操作数.

Run: python scripts/_update_lc2571_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 2571
PATTERN = "bit_greedy"
FAMILY = "bit_manipulation"
UBER_COMPANY_ID = 5
SENTINEL = "<!-- LC2571_NOTES_V3 -->"

NOTES = """<!-- LC2571_NOTES_V3 -->
## 题目定位
LC 2571 Minimum Operations to Reduce an Integer to 0 —— **位运算贪心**家族的
经典小题。给正整数 $n$，每次操作可加或减**任意** $2^k$（$k \\ge 0$），求把
$n$ 变成 0 的最少操作数。

**关键洞察**：每次操作精确翻转一个 bit（或者通过进位链翻转多个）。把问题
重述成 "用最少个 $\\pm 2^k$ 项写出 $n$" —— 这是一个 **二进制贪心** 题。

## 思路
观察二进制表示，把 $n$ 的 1-bit 按"连续 1 段（run）"分组：
- **长度 = 1 的 run**（孤立的 1）：直接 `-2^k` 抹掉，**1 步**。
- **长度 ≥ 2 的 run**（连续多个 1）：`+2^k`（最低 1 的位置）会触发**进位链**，
  把整段 1 一次性变成更高位的单个 1，**1 步消段** + **1 步抹高位 1** = **2 步**。

所以最优策略是从低位到高位扫，看末两位：
- 末位是 0 → 右移（不算操作）
- 末两位是 `01` → 减 1（消掉孤立 1），$\\text{ans} += 1$
- 末两位是 `11` → 加 1（推进进位链），$\\text{ans} += 1$

## 核心代码
```python
class Solution:
    def minOperations(self, n: int) -> int:
        ans = 0
        while n:
            # 把所有 trailing zeros 一次性甩掉, 直接定位到下一个 1
            while n % 2 == 0:
                n >>= 1
            # 末两位 == 11: 这是一个长度 >= 2 的 run, 加 1 触发进位
            if n & 3 == 3:
                n += 1
            else:
                # 末两位 == 01: 孤立的 1, 直接减
                n -= 1
            ans += 1
        return ans
```

### 走查（n = 39 = 0b100111）
| 步 | n (二进制) | 末两位 | 操作 | ans |
| --- | --- | --- | --- | --- |
| 0 | `100111` | `11` | `+1` → `101000` | 1 |
| 1 | `101` (skip 3 zeros) | `01` | `-1` → `100` | 2 |
| 2 | `1` (skip 2 zeros) | `01` | `-1` → `0` | 3 |

验证：$39 = 32 + 8 - 1$，正好 3 个 $\\pm 2^k$ 项。✓

## 关键技巧
- **`while n % 2 == 0: n >>= 1` 跳零**：trailing zeros 完全不耗操作（可任意
  右移到 1）。先跳到下一个 1 再判断末两位，省掉每次 `if n & 1` 的检查。
- **`n & 3 == 3` 看末两位是否同为 1**：等价于 `(n & 1) and (n & 2)`，但更紧凑。
- **`+1` 利用进位链一次消段**：一段 $L$ 个连续 1 加 1 后变成 $0\\ldots0\\,1$（$L$ 个零
  + 1 个 1 在更高位）—— C++/Java 里这就是 ALU 的硬件级行为，相当于"借
  CPU 的进位路径帮我们消 1"。
- **算法天然处理"加 1 后连成新 run"的情况**：如 `1011 + 1 = 1100`，新 run
  在更高位，下一轮 `n & 3 == 0` 会先跳零再处理。**不需要前瞻**。

## 正确性 / 直觉证明
**贪心局部最优 = 全局最优** 的 exchange argument：
- 若最优解某一步在 long run 末位**减 1**而非加 1，则消掉一个 1 后剩下 $L-1$
  个连续 1，需要至少再 $\\lceil (L-1)/2 \\rceil$ 步处理（每对 1 至少 1 步）。
  代价 $\\ge L - 1$。
- 加 1 方案：进位 1 步合并整段 + 后续 1 步抹高位 = $2$ 步（若高位无干扰）。
- 当 $L \\ge 2$ 时 $2 \\le L - 1 + 1 = L$，加 1 永不亏。
- 当 $L = 1$ 时加 1 反而新建一个 run，所以孤立 1 必须减。

**等价 lower bound**：每次操作翻转一个 bit（含进位链合并），所以 $\\text{ans}$
$\\ge$ 「能把 $n$ 写成 $\\sum \\pm 2^{k_i}$ 的最短表示长度」。这正是 **NAF
(Non-Adjacent Form)** 的 popcount，也是上述贪心达到的值。

## 易错点
1. **`n & 3` 写成 `n & 1`**：会退化成"逐个 bit 减 1"，对 `0b111` 要 3 步而
   非 2 步——丢掉了进位合并这一关键优化。
2. **没跳 trailing zeros 直接判**：写成 `if n & 1: ... else: n >>= 1` 也对，
   但每个 0-bit 多走一次循环；`while n % 2 == 0: n >>= 1` 一次跳完更紧凑。
3. **`n == 1` 边界**：`n & 3 == 1`（不是 3），走 `else` 分支减 1 → `n = 0`，
   ans += 1。返回 1。✓ 不要漏判这个 case。
4. **整型溢出（Java/C++）**：$n \\le 10^9$ 时 `+1` 可能让 $n$ 变成 $2^{30}$
   级别，`int32` 没问题；但若题目改成 $n \\le 2^{31}-1$，加 1 会溢出到负数。
   Python 自动大整数无忧，C++/Java 用 `long`/`int64`。
5. **以为可以"减更高位的 2^k 一次到底"**：每次只能 ±**一个** $2^k$，不能减
   "和最接近 $n$ 的 2 的幂"那种自由组合（题面易看错）。
6. **以为答案 = popcount(n)**：错。`popcount(7) = 3` 但答案是 2（$7 = 8 - 1$）。
   答案 = NAF 长度 ≤ popcount，长 run 越多差距越大。

## 复杂度
- 时间：$O(\\log n)$。每轮处理一个 1-bit（或一段 run），bit 总数是
  $\\lceil \\log_2 n \\rceil + 1$。
- 空间：$O(1)$。

## Follow-up: 等价的紧凑公式 / DP
### (a) 一行公式（基于 NAF）
观察：每次"段"决策可以从 `n` 与 `3n` 的关系读出来——`3n = n + 2n`，加 `2n`
（即 `n << 1`）会在每个 1-run 处触发一次进位入、一次进位出。这两个事件
反映在 `n ^ 3n` 的 bit pattern 上正好对应 NAF 的非零位置。

```python
def minOperations(self, n: int) -> int:
    return bin((n ^ (3 * n)) >> 1).count('1')
```
**直觉**：`n ^ 3n` 高低位各产生一对边界 bit，**右移 1 位再 popcount** 恰好
等于 NAF 非零位数 = 答案。亲自验证过 $n \\in \\{1, 7, 15, 39, 54, 100, 1023,
12345, 2^{31}-1\\}$，与贪心结果完全一致。本式是经典 bit-trick，面试可作
"知道就秒答"的彩蛋——但**不要替代主解法**，进位推导讲不清楚会失分。

### (b) DP 视角（更通用）
`dp[i]` = 处理前 $i$ 位的最小操作。状态转移看 `bit[i]`：
- $0$：`dp[i] = dp[i-1]`
- $1$：`dp[i] = min(dp[i-1] + 1, dp[i+run_len] + 1)`（减孤立 1 vs 加进位合并段）

写出来就是上面贪心的展开，无渐近优势但**对面试官解释更友好**：DP 是"我
真的想清楚了局部最优为何全局最优"的证明形式。

## 题目家族（位运算 / Bit Manipulation）
- **LC 191** Number of 1 Bits：popcount，本题 lower-bound baseline。
- **LC 461** Hamming Distance：`bin(x ^ y).count('1')`，本题"位差"思想的最简版。
- **LC 868** Binary Gap：扫描连续 1 之间的最长 0 段，相同的"按 run 分析"
  二进制串思路。
- **LC 397** Integer Replacement：极相似——$n$ 偶数 `n /= 2`，奇数选 $n \\pm 1$，
  其中 $n & 3 == 3$ 时 `+1`、否则 `-1`。**几乎同代码**，只是 LC 397 还多
  了 $n=3$ 的特判（该减不该加）。LC 2571 的 ±$2^k$ 等价于"奇数位也可以一步
  跳到任意 2 的幂"，所以连 $n=3$ 都不用特判。
- **LC 1611** Minimum One Bit Operations to Make Integers Zero：进阶版，
  操作受限（只能动最低位 + 紧邻最低 1 的下一位），答案是 Gray code。

## Uber 视角
位运算 puzzle 是 Uber **Coding 1 / Coding 2** 偏好的"小而精"题型——
- 题面短、逻辑紧、容错率低，30 分钟里能让面试官观察到完整的 think-aloud
  过程：识别"看二进制按 run 分组" → 推导 long-run 用加法 / short-run 用
  减法 → 用 `n & 3` 干净写出末两位检测 → 复杂度 $O(\\log n)$。
- 与系统侧偏好对位：Uber 后端常做 ride-id / hash bit-packing，position
  encoding，rate-limiter token bucket 之类，问"为什么这里能省一位"是真问题
  不是脑筋急转弯。
- 面试时**从二进制走查（$n=39$ 的表）开始**，再写代码，避免上来就 `n & 3`
  让面试官 follow 不上推导。

## 一句话 pitch (面试 30 秒)
> 二进制按 run 分析：长度 1 的 run 减一步抹掉，长度 ≥ 2 的 run 加 1 触发
> 进位、整段一步合并成更高位单个 1（再被下一轮处理）。每轮看末两位 `n & 3`：
> `01` 减 1，`11` 加 1，`*0` 右移跳零。$O(\\log n)$。
"""


def main() -> None:
    """Rewrite LC 2571 notes + insert Uber tag; idempotent."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, fam, pat = row

        notes_changed = not (existing_notes and SENTINEL in existing_notes)
        if notes_changed:
            fields: dict[str, str | int] = {
                "notes": NOTES,
                "is_completed": 1,
            }
            if not pat:
                fields["pattern"] = PATTERN
            if not fam:
                fields["family"] = FAMILY
            sets = ", ".join(f"{k} = ?" for k in fields)
            conn.execute(
                f"UPDATE problems SET {sets} WHERE id = ?",
                (*fields.values(), pid),
            )
            print(
                f"[UPDATED] LC {LC_ID} id={pid} "
                f"notes_len={len(NOTES)} fields={list(fields)}"
            )
        else:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} notes (sentinel present)")

        # Uber relational tag
        existing_tag = conn.execute(
            "SELECT id FROM problem_company_tags "
            "WHERE problem_id = ? AND company_id = ?",
            (pid, UBER_COMPANY_ID),
        ).fetchone()
        if existing_tag:
            print(f"[UNCHANGED] Uber tag exists row_id={existing_tag[0]}")
        else:
            cur = conn.execute(
                "INSERT INTO problem_company_tags "
                "(problem_id, company_id, relevance, source) "
                "VALUES (?, ?, 'likely', 'manual')",
                (pid, UBER_COMPANY_ID),
            )
            print(f"[INSERTED] Uber tag row_id={cur.lastrowid}")

        conn.commit()


if __name__ == "__main__":
    main()
