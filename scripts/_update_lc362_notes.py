"""Idempotent: replace thin LC 362 notes with full A/B comparison + follow-ups.

LC 362 Design Hit Counter -- stateful_ds_design 家族里"滑动时间窗计数"
的 canonical 问题, 同时是面试里考察 "circular buffer 替代无界 queue"
思路的最小例子。

Run: python scripts/_update_lc362_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 362
PATTERN = "circular-buffer"
SENTINEL = "<!-- LC362_NOTES_V2 -->"

NOTES = """<!-- LC362_NOTES_V2 -->
## 题目定位
**stateful_ds_design 家族 "滑动时间窗计数" canonical 问题**。`HitCounter`
需支持:
- `hit(timestamp)`: 在 timestamp 秒收到一次点击 (题目保证 timestamp 单调
  非递减)。
- `getHits(timestamp)`: 返回 $[timestamp - 299, timestamp]$ 这 300 秒
  (5 分钟滑动窗口) 内的点击总数。

**真实系统对应物**: rate limiter (每分钟 QPS 上限), 监控窗口 (过去 5 分钟
错误数), trending feed 的热度衰减。面试里的价值是小题目但能展开 "queue
vs circular buffer" 与 "单机 vs 分布式 sliding window" 两轴追问。

## 两种解法对比
| 维度 | (A) 时间戳 deque | (B) 长度 300 环形桶 |
| --- | --- | --- |
| `hit` 时间 | $O(1)$ 摊还 (append) | $O(1)$ 最坏 |
| `getHits` 时间 | $O(k)$, $k$=过期元素数, 最坏 $O(N)$ | $O(300) = O(1)$ |
| 内存 | $O(N)$, $N$=当前窗口内点击数 | $O(300) = O(1)$ |
| QPS 爆发容忍 | 差 (一次突发把内存拉爆) | 好 (内存恒定) |
| 任意窗口大小 | 支持 (只改过期阈值) | 支持但要改 bucket 数 |
| 实现难度 | 5 行 | 10 行, 取模有坑 |
| 生产系统首选 | ✗ | ✓ |

**面试话术**: 首答 (A) 证明自己会基本思路, 再补 (B) 展示"内存常数 + 最坏
$O(1)$"的优化, 最后用 "所以 Prometheus / Redis cell-based rate limiter
都是 (B) 的变种" 收尾。

## 解法 A: 时间戳 deque (直觉解)
```python
from collections import deque

class HitCounter:
    def __init__(self) -> None:
        self.q: deque[int] = deque()

    def hit(self, timestamp: int) -> None:
        self.q.append(timestamp)

    def getHits(self, timestamp: int) -> int:
        # 从队首弹出所有早于窗口的时间戳
        while self.q and self.q[0] <= timestamp - 300:
            self.q.popleft()
        return len(self.q)
```
**走查**: `hit` 只是 $O(1)$ 追加。`getHits` 懒清理: 只在查询时把队首过期的
弹掉, 剩下长度就是答案。**摊还意义**: 每个时间戳最多被 push 一次, pop 一次,
总代价 $O(\\text{total hits})$, 平均每次操作 $O(1)$。

**致命缺点**: 最坏情况 `getHits` 是 $O(N)$ --- 考虑 $10^6$ 次 `hit(1)`
然后一次 `getHits(301)`, 要一口气弹 $10^6$ 个元素。**不能在线保证 p99
延迟**, 所以生产系统不用这个方案。

## 解法 B: 长度 300 环形桶 (生产首选)
```python
class HitCounter:
    def __init__(self) -> None:
        self.times = [0] * 300   # 每个桶记录 "上次写入的秒"
        self.counts = [0] * 300  # 对应那一秒的点击数

    def hit(self, timestamp: int) -> None:
        idx = timestamp % 300
        if self.times[idx] != timestamp:
            # 这个桶上次被占用的秒已经过期, 重置
            self.times[idx] = timestamp
            self.counts[idx] = 1
        else:
            # 同一秒多次 hit, 累加
            self.counts[idx] += 1

    def getHits(self, timestamp: int) -> int:
        total = 0
        for i in range(300):
            # 只累加 "仍在窗口内" 的桶
            if timestamp - self.times[i] < 300:
                total += self.counts[i]
        return total
```

### 为什么 bucket 数恰好 = 300
题目把窗口钉死 5 分钟 = 300 秒。**每秒对应一个桶, 桶的下标 = 秒 mod 300**。
这样任意 $timestamp$ 映射唯一桶; 下次同一 $idx$ 被访问时必然隔了至少 300
秒, **天然过期, 用 "times[idx] != timestamp" 一行判断就能 lazy reset**,
不需要显式清理。这是 circular buffer 在时间窗问题里最优雅的落点。

### 为什么 $O(300)$ 算 $O(1)$
$300$ 是题目给定的常数 window 大小, 与输入规模 $N$ 无关。即便题目
改成任意 `window_sec`, 只要是**编译期常数**, `getHits` 仍是 $O(1)$;
若 `window_sec` 是运行期参数, 则是 $O(\\text{window\\_sec})$。面试要点:
**不要在白板上把 300 当做动态 $n$**, 明确说这是"题目常数"。

## 复杂度
- `hit`: $O(1)$ (两种解法一致的最坏情况)
- `getHits`:
  - (A) 摊还 $O(1)$, 最坏 $O(N)$, p99 不可控
  - (B) 最坏 $O(300) = O(1)$, p99 稳定
- 空间:
  - (A) $O(N)$, $N$ 为当前窗口活跃点击数, 会随 QPS 线性涨
  - (B) $O(300) = O(1)$

## 易错点
1. **(A) 里用 `list` 而不是 `deque`**: `list.pop(0)` 是 $O(N)$, 会把摊还
   $O(1)$ 拖成 $O(N^2)$。必须 `collections.deque`。
2. **(B) 里把 `times[idx] != timestamp` 写成 `<`**: 正确判定是"桶记录的
   秒是否恰为当前秒"。若写 `<`, 同一秒的第二次 `hit` 会被当成过期而覆盖。
3. **(B) 的 `getHits` 判据用 `< 300` 不是 `<= 300`**: 窗口是过去 300 秒
   含端点, 即 $timestamp - times[i] \\in [0, 299]$。写成 `<= 300` 会多
   算一秒。
4. **题目保证 `hit` 的 timestamp 单调非递减**, 别写成 "timestamp 可能
   回跳"。回跳场景要做更强的版本号管理, 属于追问范围。
5. **(A) 里不要在 `hit` 就清理过期**, 因为没收到查询就没必要; 只在
   `getHits` 清理, 才能把清理代价摊还到查询里。

## Follow-up 追问指针
- **并发 hit 安全 (多线程调用 `hit`)**: (B) 的 `if/else` 不是原子的, 两
  线程在同一秒可能都走到"重置"分支。解: 每个桶加一把细粒度锁; 或者 `count`
  用 `atomic int64` + CAS ("if times[idx] == timestamp: inc; else:
  CAS-reset"); 或者 sharded --- 按 $\\text{thread\\_id}$ 哈希分到多个
  HitCounter, 查询时求和。
- **任意窗口大小 `window_sec`**: 把 300 替换成 `window_sec`。`hit` 仍
  $O(1)$, `getHits` 变 $O(\\text{window\\_sec})$。内存 $O(\\text{window\\_sec})$;
  若 window 大到 $10^6$ 秒, 需要改回 (A) 的 deque 或分层桶
  (分钟级 + 秒级两层)。
- **超高 QPS (单秒 $>2^{31}$ 次 hit)**: `counts[idx]` 用 `int64` 或
  Python 原生 `int` (自动大数) 即可; C/Java 要显式 atomic int64, 否则
  溢出会让计数回绕。
- **分布式 (跨机 rate limit)**:
  - **Redis `ZSET` + `ZREMRANGEBYSCORE`**: 每次 hit `ZADD key ts ts`,
    查询时先 `ZREMRANGEBYSCORE key 0 (ts-300)` 再 `ZCARD key`。精确
    但 key 体积正比于 QPS。
  - **Redis cell-based**: 把 5 分钟切 5 个 1 分钟桶, 每桶一个 key,
    `INCR` + TTL 300; 查询时 `MGET` 5 个桶求和。近似但 key 大小 $O(1)$,
    是 Cloudflare / GitHub 线上用法。
- **持久化 (restart 不丢统计)**: (B) 的两个数组每秒批量 flush 到磁盘,
  重启时 replay; 实际上生产里多用 Redis / Prometheus 的本地 WAL, 很少
  自己实现。

## 一句话 pitch (面试 45 秒)
> 两解法: (A) deque 存每次 hit 的时间戳, `getHits` 时从队首弹所有
> $\\le timestamp - 300$ 的, 剩下长度就是答案, 摊还 $O(1)$ 但最坏 $O(N)$,
> 内存随 QPS 线性。(B) 长度 300 的环形桶, `hit` 时 `idx = timestamp % 300`,
> 若桶记录的秒就是当前秒则累加否则重置; `getHits` 扫所有 300 个桶累加
> 仍在窗口内的, $O(1)$ 时间, $O(1)$ 空间。(B) 的核心 trick 是"桶的下标
> 等于秒 mod 桶数", 下次访问同 idx 必然过期, 天然 lazy reset。生产系统
> (Cloudflare rate limiter, Prometheus rate()) 都是 (B) 的变种。
"""


def main() -> None:
    """Replace thin notes and mark LC 362 as completed; idempotent via sentinel."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, _fam, pat = row

        if existing_notes and SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} (sentinel present)")
            return

        fields: dict[str, str | int] = {
            "notes": NOTES,
            "is_completed": 1,
        }
        if not pat:
            fields["pattern"] = PATTERN

        sets = ", ".join(f"{k} = ?" for k in fields)
        conn.execute(
            f"UPDATE problems SET {sets} WHERE id = ?",
            (*fields.values(), pid),
        )
        conn.commit()
        print(
            f"[UPDATED] LC {LC_ID} id={pid} "
            f"notes_len={len(NOTES)} fields={list(fields)}"
        )


if __name__ == "__main__":
    main()
