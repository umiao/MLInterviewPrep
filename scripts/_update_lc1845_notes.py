"""Idempotent: mark LC 1845 complete and attach Chinese solution notes.

LC 1845 Seat Reservation Manager -- stateful_ds_design 家族里最干净的
min-heap 设计题: "最小可用 id" 是 heap 的经典应用场景, 同时也是很多
真实调度系统的 canonical 模型 (port 分配, slot 分配, id pool).

Run: python scripts/_update_lc1845_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 1845
PATTERN = "min-heap"
SENTINEL = "<!-- LC1845_NOTES -->"

NOTES = """<!-- LC1845_NOTES -->
## 题目定位
**stateful_ds_design 家族最干净的 heap 设计题**。`SeatManager(n)` 管理
编号 $1..n$ 的 $n$ 个座位, 需要支持两个 $O(\\log n)$ 操作:
- `reserve()` 返回**当前最小**的未预订座位编号, 并将其标记为已预订。
- `unreserve(seatNumber)` 将该座位重新标记为可用。

题目本身算法不深, 但是**很多真实调度系统的 canonical 模型**: port 分配,
连接池 slot 分配, 可复用 id 池, 甚至内存块 free list 都是同一结构。
面试里常作为 warm-up, 追问点往往是"若要拿最大 id 怎么办"或"若
`unreserve` 不保证未重复怎么办"。

## 核心洞察
语义只有一句 -- **"返回最小可用 id"** -- 直接对应 **min-heap**: 堆顶
恒是最小元素, `heappop` $O(\\log n)$, `heappush` $O(\\log n)$。
只要想清楚这一条, 实现是照着语义翻译。

## 两种初始化策略
### (a) 朴素: 一次性把 1..n 全塞进堆 (推荐面试首答)
```python
import heapq

class SeatManager:
    def __init__(self, n: int):
        self.available = list(range(1, n + 1))
        heapq.heapify(self.available)  # O(n), 不是 O(n log n)

    def reserve(self) -> int:
        return heapq.heappop(self.available)

    def unreserve(self, seatNumber: int) -> None:
        heapq.heappush(self.available, seatNumber)
```
**优点**: 代码极短, 语义一眼可读, 面试最省事。
**缺点**: $O(n)$ 内存 + $O(n)$ 初始化时间, 即便调用方只 reserve 几次
也要先实例化整个堆。

### (b) 懒加载: 维护 `next_seat` 计数器 + 归还堆
```python
import heapq

class SeatManager:
    def __init__(self, n: int):
        self.returned = []   # min-heap of returned seat numbers
        self.next_seat = 1   # 尚未分配过的最小编号
        self.n = n

    def reserve(self) -> int:
        if self.returned:
            return heapq.heappop(self.returned)
        seat = self.next_seat
        self.next_seat += 1
        return seat

    def unreserve(self, seatNumber: int) -> None:
        heapq.heappush(self.returned, seatNumber)
```
**优点**: $O(1)$ 初始化, 空间 $O(R)$ where $R$ 是已归还数量, 在
$R \\ll n$ 时远优于 (a)。适合"大 $n$, 稀疏使用"的场景 (比如 $n=10^9$
但一共只 reserve 几万次)。
**缺点**: 多几行状态, 不变式要说清"returned 里存的都严格小于 next_seat"。

### 策略对比
| 维度 | (a) heapify | (b) next_seat + heap |
| --- | --- | --- |
| 初始化时间 | $O(n)$ | $O(1)$ |
| 初始化空间 | $O(n)$ | $O(1)$ |
| reserve 时间 | $O(\\log n)$ | $O(\\log R)$, $R \\le$ 当前可用归还数 |
| unreserve 时间 | $O(\\log n)$ | $O(\\log R)$ |
| 总空间上界 | $O(n)$ | $O(\\min(R, n))$ |
| 面试推荐 | ✓ 首答 | 追问"大 $n$" 时切换 |

**面试话术**: 首答 (a), 然后补一句 "if $n$ 可能很大或调用次数稀疏, 可以
用 next_seat + 归还堆, 把空间降到 $O(R)$"。展示"能按约束换方案"的判断。

## heapify 为什么是 $O(n)$ 而非 $O(n \\log n)$
朴素想法: "$n$ 次 heappush, 每次 $O(\\log n)$, 总 $O(n \\log n)$"。
但 `heapify` 用的是 **sift-down 自底向上**: 从最后一个内部节点
(下标 $\\lfloor n/2 \\rfloor - 1$) 倒序往回, 每个节点沿子树下沉到合法位置。

**几何级数求和**: 高度为 $h$ 的节点数约为 $n / 2^{h+1}$, sift-down 代价
是 $O(h)$。所以总代价
$$\\sum_{h=0}^{\\log n} \\frac{n}{2^{h+1}} \\cdot h = n \\cdot \\sum_{h=0}^{\\infty} \\frac{h}{2^{h+1}} = n \\cdot 1 = O(n).$$
关键是 "**大多数节点在下层, 但下层 sift-down 成本低**" 的反比结构, 让
总和收敛成常数 $\\times n$。

面试追问时, 不一定要背级数, 说 "自底向上 sift-down, 底层节点多但下沉
距离短, 上层节点距离长但数量少, 总和几何级数收敛到 $O(n)$" 已经够用。

## 复杂度总结
- `reserve`: $O(\\log n)$ (heappop)
- `unreserve`: $O(\\log n)$ (heappush)
- `__init__`:
  - 方案 (a): $O(n)$ 时间 + $O(n)$ 空间
  - 方案 (b): $O(1)$ 时间 + $O(1)$ 空间
- 在线调用 $Q$ 次: (a) 时空 $O(n + Q \\log n)$; (b) 时空 $O(Q \\log Q)$。

## 易错点
1. **不要用 `sorted list + pop(0)`**。`sorted(...)` 每次重排 $O(n \\log n)$,
   或者 `SortedList.pop(0)` 虽 $O(\\log n)$ 但常数比 heap 大 2-3 倍; 而且
   Python 内置 `list.pop(0)` 是 $O(n)$ 陷阱。
2. **不要用 `set + min(s)`**。`min` 扫整个集合是 $O(n)$, reserve 每次
   $O(n)$ 直接 TLE。`set` 的 $O(1)$ 查询和 $O(\\log n)$ 最小值是两回事。
3. **不要用 `sorted list + bisect`**。`bisect.insort` 虽然 lookup $O(\\log n)$
   但插入还是 $O(n)$ (底层 `list.insert` 要右移元素), 大 $n$ 依然 TLE。
4. **heapify 和 "逐个 heappush" 是不同操作**。`heapify([1..n])` 是 $O(n)$;
   `for i in 1..n: heappush(h, i)` 是 $O(n \\log n)$。初始化时应用前者。
5. **重复 unreserve 同一个座位**: 题目保证调用合法 (不会 unreserve 未
   被 reserve 的), 所以不需要去重。工程推广时要加个 set 做 guard。
6. **方案 (b) 里 `returned` 堆不要和 `next_seat` 有交集**: 任何 `push` 进
   `returned` 的值必然之前被 `pop` 过, 严格小于当前 `next_seat`。

## Follow-up 追问指针
- **"求最大可用 id"**: 改 max-heap。Python 无原生 max-heap, 用 **取负数
  trick**: `heappush(heap, -seat)`, `pop` 时 `-heappop(heap)`。
- **"同时需要最小和最大"**: 用 `SortedList` 支持 $O(\\log n)$ 取最小/最大;
  或者一双 heap + 惰性删除 (两个堆共享状态, 每次操作后清理堆顶无效项)。
- **"支持 $n$ 超大 (如 $10^{18}$)"**: 只能用方案 (b), 因为连 $O(n)$ 内存
  都放不下。
- **"`unreserve` 不保证合法, 要去重"**: 加一个 `Set[int]` 存"当前空闲"
  的, heap push 前检查 `if seat not in available_set`。代价: 额外 $O(n)$
  空间 + 每次操作多一次 set 查询。
- **"要求持久化 (restart 保留状态)"**: 每次 reserve/unreserve 写 WAL
  (write-ahead log), restart 时 replay 重建堆。工业里 port allocator
  常用的套路。
- **"并发安全"**: 朴素加锁 $O(1)$ 额外开销但吞吐变串行; 高并发下用
  lock-free skip list (ConcurrentSkipListMap in JVM) 或 sharded heap
  (每 shard 一把锁, reserve 时抢最少的 shard)。

## 一句话 pitch（面试 45 秒）
> `reserve` 就是"取最小可用 id", 直接对应 min-heap: 构造时
> `heapq.heapify(list(range(1, n+1)))` $O(n)$ 建堆, `reserve` 是
> `heappop` $O(\\log n)$, `unreserve` 是 `heappush` $O(\\log n)$。
> 如果 $n$ 很大或调用稀疏, 可以改成"next_seat 计数器 + 归还堆"的
> 懒加载版本, 把初始化降到 $O(1)$, 空间降到 $O(R)$。核心观察是
> heapify 自底向上 sift-down 其实是 $O(n)$, 不是朴素分析的 $O(n \\log n)$,
> 这是 min-heap 在"id 池"类问题里常数表现好的原因。
"""


def main() -> None:
    """Attach notes and mark LC 1845 as completed; idempotent via sentinel."""
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
