"""Seed Google coding prep: LC 692 Top-K Frequent Words + distributed variant,
and a new custom problem 'Sum of Good Subarrays (max-min <= 1)'.

Task: T-P1-206.
- Append Chinese solution notes to problem 393 (LC 692) with Google distributed
  follow-up (partition by key, local top-K heap, K-way merge, skew mitigation).
- Add Google company tag + 'Google 2026-04-17 prep' source badge.
- Insert new custom non-LC problem 'Sum of Good Subarrays (max-min <= 1)' with
  sliding window + 2 monotonic deques (min + max), contribution counting.
Idempotent: re-running does not duplicate tags or append notes twice.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SOURCE_BADGE = "Google 2026-04-17 prep"


def merge_json_tag(existing: str | None, tag: str) -> str:
    tags = json.loads(existing) if existing else []
    if tag not in tags:
        tags.append(tag)
    return json.dumps(tags, ensure_ascii=False)


def merge_source(existing: str | None, new: str) -> str:
    if not existing:
        return new
    parts = [s.strip() for s in existing.split(",") if s.strip()]
    if new not in parts:
        parts.append(new)
    return ", ".join(parts)


def append_notes(existing: str | None, addendum: str, marker: str) -> str:
    if existing and marker in existing:
        return existing
    if not existing:
        return addendum
    return existing.rstrip() + "\n\n---\n\n" + addendum


LC692_ADDENDUM = """## [Google 2026-04-17] Follow-up: 分布式 Top-K 频繁词

### 问题升级
原题：内存里一个词表，返回频次最高的 K 个词（同频按字典序）。
Google 变体：**大规模视频日志**（TB 级），单机放不下；求全局 Top-K `video_id`。

### 分布式方案：Map-Shuffle-Reduce 变体

#### 阶段 1：分片 (Map)
日志按行 shard 到 $M$ 台 worker。每台 worker 本地统计 `Counter[video_id]`。
- 若单 worker 的 keyspace 仍超内存，使用 **外排序 + 分块 Counter**（或 LSM
  树结构，如 leveldb）。
- 关键不变式：每个 `video_id` 只会出现在一个 shard 上吗？**不**。同一
  `video_id` 会散布在所有 worker（除非 shard key = video_id）。

#### 阶段 2：Shuffle
按 `hash(video_id) % R` 把局部 Counter 发送到 $R$ 个 reducer，使得**同一
`video_id` 的所有局部计数汇聚到同一 reducer**。这是正确性关键。

#### 阶段 3：Reduce (本地 Top-K)
每个 reducer:
1. 合并收到的局部 Counter -> 全局该 shard 的完整计数。
2. 本地维护一个 **size-K min-heap**，遍历所有 (count, word) 对：
   - 若 heap 未满，直接 push。
   - 若当前项 > heap top，pop + push。
   - tie-break: 相同 count 时 word 字典序**更大**的先被淘汰（对应 LC 692
     同频按字典序升序输出，所以堆比较器要反向）。
3. 输出本 reducer 的 Top-K，共 $R \\cdot K$ 条。

#### 阶段 4：最终合并 (Coordinator)
coordinator 收到 $R \\cdot K$ 条，再做一次 K-way merge（或直接一个 size-K
min-heap），得到全局 Top-K。

### 本地 Top-K 堆代码
```python
import heapq
from collections import Counter

def topk_frequent_words(words, k):
    cnt = Counter(words)
    # min-heap by (count, reverse_word) so that on tie, larger word is
    # popped out. Use a wrapper to flip word order.
    class Key:
        __slots__ = ('c', 'w')
        def __init__(self, c, w): self.c = c; self.w = w
        def __lt__(self, other):
            if self.c != other.c: return self.c < other.c
            return self.w > other.w  # reverse: larger word is "smaller"
    heap = []
    for w, c in cnt.items():
        heapq.heappush(heap, Key(c, w))
        if len(heap) > k:
            heapq.heappop(heap)
    out = []
    while heap:
        x = heapq.heappop(heap); out.append(x.w)
    return out[::-1]  # heap pops smallest first; reverse for desc
```
- Time: $O(N \\log K)$, Space: $O(U + K)$ 其中 $U$ 是 unique words 数。
- 对比 `sorted(cnt.items(), ...)[:k]`: 后者 $O(U \\log U)$，若 $K \\ll U$
  不如堆；若 $K \\approx U$ 或 $U$ 不大，排序更简单。
- 还有 **bucket sort** 版本 $O(N)$：按频次建桶，从高频桶向下取 K 个。

### 关键难点：数据倾斜 (key skew)
**症状**：某个超热 `video_id`（如爆款短视频）占 20% 流量，哈希到同一
reducer，该 reducer 成为瓶颈 (stragglers)。

**缓解策略**：
1. **两级聚合 (Combiner)**：Map 端先做局部 Counter，减少 shuffle 流量。
   Hadoop MapReduce 的 `Combiner` / Spark 的 `reduceByKey`。
2. **Salting 热键**：对疑似热 key 追加随机后缀 `video_id#salt`，分散到
   多个 reducer；最后 coordinator 再聚合去 salt。
3. **Sketch 近似**：Count-Min Sketch / Space-Saving 算法给出近似 Top-K，
   换 $O(1/\\epsilon)$ 空间换精度；流式场景标配。
4. **Two-phase exact**: 第一轮用 Count-Min 找**候选集** (heavy hitters 的
   过采样)，第二轮对候选集做精确聚合。保证精确且抗倾斜。

### 为什么不用全局排序？
全局排序需要 $O(N \\log N)$ shuffle + 比较，对 TB 级数据是灾难。Top-K
只需局部 Top-K + 小规模最终合并，网络传输量从 $N$ 降到 $R \\cdot K$。

### 一致性 / 时间窗口
真实系统 Top-K 通常限定时间窗口（"过去 24 小时"），需要：
- 分片按 `(user_hash, time_bucket)` 二维切分。
- Watermark + lateness 处理（Flink 语义）。
- Sliding window 可用 **指数衰减计数**（每个 bucket 乘以 $e^{-\\lambda \\Delta t}$）。

### 面试应答 checklist
1. 澄清：数据量？K 多大？内存 / 磁盘 / 网络约束？是否流式？是否允许近似？
2. 单机基线：`Counter` + heap $O(N\\log K)$。
3. 分布式：Map-Shuffle-Reduce 三段式，shuffle key = video_id。
4. 主动提数据倾斜和 salting / Count-Min Sketch。
5. 若面试官说"流式"，切到 Space-Saving / Heavy-Hitter 算法族。
"""


NEW_PROBLEM_TITLE = "Sum of Good Subarrays (max-min <= 1)"
NEW_PROBLEM_DESC = """Given an array of integers `a`, a subarray is "good" if
`max(subarray) - min(subarray) <= 1`. Return the **sum** of all elements across
all good subarrays (i.e., sum over every good subarray of its element-sum).

Example: `a = [3, 5, 6, 7, 6]`.
- Good subarrays (max-min <= 1):
  [3], [5], [6], [7], [6], [5,6], [6,7], [7,6], [6,7,6].
- Their element sums: 3 + 5 + 6 + 7 + 6 + 11 + 13 + 13 + 19 = 83.

Follow-ups:
1. Count of good subarrays (without sum).
2. Max-min <= K for arbitrary K.
3. Streaming: answer the sum as elements arrive.

Interview context: Google 2026-04-17 coding — user was stumped on O(N)
formulation. This note gives the sliding-window + two-monotonic-deques
(min & max) approach with contribution counting."""

NEW_PROBLEM_NOTES = """## Sum of Good Subarrays (Google 2026-04-17)

### 用户原始思路校验
用户猜测："两个单调队列维护窗口 max 和 min，若 `max - min > 1` 就收缩
左端点。" **方向完全正确**，缺的是**如何把"右端点贡献"累加成总和**。

### O(N) 算法：滑窗 + 双单调队列 + 贡献法

#### 核心观察
固定右端点 $r$，设最左可行左端点为 $L(r)$（即 $[L(r), r]$ 窗口内 max-min
$\\le 1$，且 $L(r)-1$ 不满足）。则以 $r$ 结尾的所有 good subarray 是
$[L(r), r], [L(r)+1, r], \\ldots, [r, r]$，共 $r - L(r) + 1$ 个。

#### 两个贡献维度
- **计数** (follow-up 1): $\\text{count} = \\sum_{r} (r - L(r) + 1)$。
- **元素和** (原题): 每个位置 $i$ 被多少个 good subarray 覆盖？设
  $i$ 被 $c_i$ 个 good subarray 覆盖，则答案 $= \\sum_i a_i \\cdot c_i$。

$c_i$ 的计算 = (左端点 $\\le i$ 的选择数) × (右端点 $\\ge i$ 的选择数)，
**但**必须限定该 subarray 整体 good，所以直接按右端点扫描更稳：

$$\\text{ans} = \\sum_{r=0}^{n-1} \\sum_{l=L(r)}^{r} \\left( \\sum_{i=l}^{r} a_i \\right).$$

展开：以 $r$ 为右端点的贡献
$$S(r) = \\sum_{l=L(r)}^{r} \\text{prefixSum}(l..r) = \\sum_{l=L(r)}^{r} (P_{r+1} - P_l)$$
$$= (r - L(r) + 1) \\cdot P_{r+1} - \\sum_{l=L(r)}^{r} P_l.$$

维护 **前缀和的前缀和** $Q_k = \\sum_{l=0}^{k-1} P_l$，则
$\\sum_{l=L(r)}^{r} P_l = Q_{r+1} - Q_{L(r)}$。这样 $S(r)$ 可 $O(1)$ 算出。

#### 双单调队列维护窗口 max / min
- `mx_dq`: 单调递减双端队列，队首是窗口最大值索引。
- `mn_dq`: 单调递增双端队列，队首是窗口最小值索引。
- 每次右端点 $r$ 加入：从两队列尾部弹出违反单调性的元素。
- 收缩左端点 $l$ 直到 `a[mx_dq[0]] - a[mn_dq[0]] <= 1`；弹出超出 $l$ 的
  队首索引。

```python
from collections import deque

def sum_good_subarrays(a):
    n = len(a)
    # prefix sums
    P = [0] * (n + 1)
    for i, x in enumerate(a):
        P[i+1] = P[i] + x
    Q = [0] * (n + 2)
    for k in range(1, n + 2):
        Q[k] = Q[k-1] + P[k-1]  # Q[k] = sum_{l=0..k-1} P[l]

    mx_dq = deque(); mn_dq = deque()
    L = 0
    ans = 0
    for r in range(n):
        while mx_dq and a[mx_dq[-1]] <= a[r]: mx_dq.pop()
        mx_dq.append(r)
        while mn_dq and a[mn_dq[-1]] >= a[r]: mn_dq.pop()
        mn_dq.append(r)
        # shrink L until window is good
        while a[mx_dq[0]] - a[mn_dq[0]] > 1:
            L += 1
            if mx_dq[0] < L: mx_dq.popleft()
            if mn_dq[0] < L: mn_dq.popleft()
        # contribution: S(r) = (r - L + 1) * P[r+1] - (Q[r+1] - Q[L])
        width = r - L + 1
        ans += width * P[r+1] - (Q[r+1] - Q[L])
    return ans
```

- Time: $O(N)$（每个索引至多入队/出队一次，左指针至多右移 $N$ 次）。
- Space: $O(N)$（前缀和 + 双端队列）。

### Worked Example: `a = [3, 5, 6, 7, 6]`

| r | a[r] | window max,min | L | good subarrays ending at r | element sums | cumulative |
|---|------|----------------|---|----------------------------|--------------|------------|
| 0 | 3 | (3,3) | 0 | [3] | 3 | 3 |
| 1 | 5 | (5,5) | 1 | [5] | 5 | 8 |
| 2 | 6 | (6,5) | 1 | [5,6],[6] | 11+6=17 | 25 |
| 3 | 7 | (7,6) | 2 | [6,7],[7] | 13+7=20 | 45 |
| 4 | 6 | (7,6) | 2 | [6,7,6],[7,6],[6] | 19+13+6=38 | 83 |

答案 = **83**, 与题目示例一致。

### 算法正确性要点
- **单调队列不变式**：队首始终是当前窗口 $[L, r]$ 内的 max/min 索引。
- **窗口收缩单调性**：$L$ 只右移，保证 $O(N)$。若 $L$ 可左移（不可能，
  因为 max-min 随窗口扩大只会非减），则退化 $O(N^2)$。
- **贡献式** $S(r)$ 推导：线性加权前缀和是经典 trick，常用于"所有子区
  间 sum 之和" / "所有子区间 max 之和" (后者还要结合"左右首个更大元素"
  的单调栈)。

### 错误思路对比

| 思路 | 复杂度 | 错在哪 |
|------|--------|--------|
| 暴力枚举所有 $O(N^2)$ 子区间，每次 $O(N)$ 求 max/min | $O(N^3)$ | 超时 |
| 暴力枚举 + 增量维护 max/min | $O(N^2)$ | 仍超时；但易写，可做大纲检查 |
| 仅用 1 个单调队列 | — | 只能维护 max 或 min，无法判断 max-min |
| 不用贡献法，直接累加每个子区间的 sum | $O(\\text{count})$ | 子区间数最多 $O(N^2)$，退化 |

### Follow-up 1: 计数版（max-min <= 1 的好子区间个数）
把贡献式里 $S(r)$ 换成 $(r - L + 1)$，无需前缀和：
```python
ans = 0; L = 0; mx_dq, mn_dq = deque(), deque()
for r in range(n):
    # ... (same deque maintenance) ...
    ans += r - L + 1
```

### Follow-up 2: max-min <= K
算法完全不变，把 `while a[mx_dq[0]] - a[mn_dq[0]] > 1` 换成 `> K`。
适用于任意阈值。

### Follow-up 3: 流式 (online)
- 元素逐个到达，查询当前累积答案。
- 两个 deque 维护"滑动窗口内"的 max/min 本来就是流式友好的。
- 前缀和 $P, Q$ 可增量维护。
- 难点：若窗口长度固定为 $W$ 而非 $[L, r]$，则左端点到期也要从 deque 弹，
  这是经典 LC 239 滑动窗口最大值的变体。

### 面试应答 checklist
1. 澄清：max-min 的阈值是 1 还是 K？要 count 还是 sum？数组大小？
2. 先给暴力 $O(N^2)$ 基线，说明滑窗单调性。
3. 升级到 $O(N)$：双单调队列维护 max/min + 左指针收缩。
4. 针对 "sum" 而非 "count"：引入前缀和贡献法 + 二阶前缀和 $Q$。
5. Worked example 走一遍 `[3,5,6,7,6]` = 83。
6. 主动提 follow-up: 任意 K、流式、滑动窗口定长变体。
"""


def upsert_lc_addendum(cur: sqlite3.Cursor, problem_id: int, marker: str, addendum: str) -> None:
    cur.execute("SELECT notes, tags, company_tags, source FROM problems WHERE id=?", (problem_id,))
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"problem id {problem_id} not found")
    notes, tags_json, company_json, source = row
    new_notes = append_notes(notes, addendum, marker)
    new_company = merge_json_tag(company_json, "Google")
    new_source = merge_source(source, SOURCE_BADGE)
    cur.execute(
        "UPDATE problems SET notes=?, company_tags=?, source=? WHERE id=?",
        (new_notes, new_company, new_source, problem_id),
    )


def upsert_new_problem(cur: sqlite3.Cursor) -> int:
    cur.execute(
        "SELECT id FROM problems WHERE leetcode_id IS NULL AND title=?",
        (NEW_PROBLEM_TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    tags_json = json.dumps(
        ["sliding-window", "monotonic-deque", "prefix-sum", "contribution"],
        ensure_ascii=False,
    )
    company_json = json.dumps(["Google"], ensure_ascii=False)
    if row is not None:
        pid = row[0]
        cur.execute(
            "UPDATE problems SET description=?, notes=?, tags=?, pattern=?, category=?, "
            "company_tags=?, source=?, difficulty=?, priority=? WHERE id=?",
            (
                NEW_PROBLEM_DESC,
                NEW_PROBLEM_NOTES,
                tags_json,
                "sliding-window",
                "algorithm",
                company_json,
                SOURCE_BADGE,
                "medium",
                1,
                pid,
            ),
        )
        return pid
    cur.execute(
        "INSERT INTO problems (leetcode_id, title, description, notes, tags, pattern, category, "
        "company_tags, source, difficulty, priority, is_completed, created_at) "
        "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (
            NEW_PROBLEM_TITLE,
            NEW_PROBLEM_DESC,
            NEW_PROBLEM_NOTES,
            tags_json,
            "sliding-window",
            "algorithm",
            company_json,
            SOURCE_BADGE,
            "medium",
            1,
            now,
        ),
    )
    return cur.lastrowid


def verify_example() -> None:
    """Sanity-check the algorithm on [3,5,6,7,6] == 83."""
    from collections import deque

    def sum_good(a: list[int]) -> int:
        n = len(a)
        P = [0] * (n + 1)
        for i, x in enumerate(a):
            P[i+1] = P[i] + x
        Q = [0] * (n + 2)
        for k in range(1, n + 2):
            Q[k] = Q[k-1] + P[k-1]
        mx_dq: deque[int] = deque(); mn_dq: deque[int] = deque()
        L = 0; ans = 0
        for r in range(n):
            while mx_dq and a[mx_dq[-1]] <= a[r]: mx_dq.pop()
            mx_dq.append(r)
            while mn_dq and a[mn_dq[-1]] >= a[r]: mn_dq.pop()
            mn_dq.append(r)
            while a[mx_dq[0]] - a[mn_dq[0]] > 1:
                L += 1
                if mx_dq[0] < L: mx_dq.popleft()
                if mn_dq[0] < L: mn_dq.popleft()
            width = r - L + 1
            ans += width * P[r+1] - (Q[r+1] - Q[L])
        return ans

    got = sum_good([3, 5, 6, 7, 6])
    assert got == 83, f"worked example failed: expected 83, got {got}"
    print(f"algorithm self-check: [3,5,6,7,6] -> {got} [OK]")


def main() -> None:
    verify_example()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    upsert_lc_addendum(
        cur,
        393,
        "[Google 2026-04-17] Follow-up: 分布式 Top-K 频繁词",
        LC692_ADDENDUM,
    )
    new_id = upsert_new_problem(cur)
    conn.commit()
    cur.execute("SELECT id, length(notes) FROM problems WHERE id IN (393, ?)", (new_id,))
    for r in cur.fetchall():
        print(f"problem id={r[0]} notes_len={r[1]}")
    print(f"new/updated sum-good-subarrays problem id={new_id}")
    conn.close()


if __name__ == "__main__":
    main()
