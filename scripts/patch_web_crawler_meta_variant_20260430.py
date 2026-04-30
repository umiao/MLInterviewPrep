"""Patch interview-web-crawler with the Meta adversarial-scale variant (T-P0-264).

Adds 4 deltas distilled from the Meta AI-Native onsite (2026-05-01) source
material that are NOT covered by the baseline `interview-web-crawler` SD:

1. architecture            -- "## 去中心化 10K-节点变体" appendix (ring topology,
                              push-mode handoff, V=200 virtual nodes, batch RPC,
                              gossip Bloom 摘要)
2. tradeoffs               -- 2 new rows in 关键设计决策 table
                              (Push vs Pull; Leader-Follower vs Leaderless DHT
                               with adversarial-security argument)
3. defense                 -- Q6 (exactly-once via Paxos consumer-group, multi-leader
                              vs Paxos = consensus-before-action)
                              + Q7 (10K-机不需要 Bloom: 100MB/机 set fits in RAM;
                                    Bloom仅用于跨机预过滤节省带宽)
4. production_constraints  -- 1 new SPOF row: clockwise-next-2 peer-backup model,
                              backups track-only-no-fetch, replaces ZK in
                              leaderless variant

Idempotent: each delta is bracketed by a unique sentinel pair and the script
replaces the bracketed body in-place. Re-running yields byte-identical column
content (no DB write).

Embedded content is the source-of-truth (script is self-contained; the staging
.md files at `docs/staging/generated/system_designs/` are gitignored drafts).
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"

SLUG = "interview-web-crawler"
SENTINEL_BEGIN = "<!-- META-VARIANT BEGIN -->"
SENTINEL_END = "<!-- META-VARIANT END -->"


# ---------------------------------------------------------------------------
# Delta 1: architecture -- 去中心化 10K-节点变体
# ---------------------------------------------------------------------------
ARCHITECTURE_VARIANT = r"""## 去中心化 10K-节点变体 (Adversarial Scale: 10K-Machine Leaderless Variant)

**适用场景**: 当机群规模膨胀到 **10,000 台节点** (相比基准 35-63 台
扩大 200x), 中央 URL Frontier 服务和 ZooKeeper 协调层都会成为
**单点瓶颈 (Bottleneck)** 与**安全暴露面 (Attack Surface)**. Meta 风格的
对抗规模面试题会引入这一变体. 关键变化: 没有"主节点"概念, 每台机器
对等 (peer), 通过**分布式哈希表 (Distributed Hash Table, DHT)** 自组织.

### 拓扑结构 (Ring Topology)

- 10,000 台机器按 ID 排列在一个**逻辑环 (Logical Ring)** 上, 类似
  **Chord / Kademlia DHT**. 每台机器只需要知道环上**前/后 K 个邻居**
  (典型 K=20) 的地址, 不需要全局节点列表
- **无中央 Frontier**: URL 队列分布存放在每台机器本地, 总队列 =
  10K 台机器各自的子队列之和. 不存在"丢失主队列"的故障模式
- **无 ZooKeeper**: 节点发现通过环上邻居的 **gossip 协议**, 心跳由
  下一跳邻居互相检测 (而非中心化的 ZK session)

### URL 分发: 推模式 (Push-mode URL Handoff)

不再是 Worker 主动 pull, 而是**发现者主动推 (Push)**:

1. 节点 A 解析页面 P 后得到链接 URL `u`, 计算 `hash(domain(u))`
2. 用一致性哈希环定位 `u` 应归属的目标节点 N (顺时针最近)
3. 节点 A 直接把 `u` 推送给 N (单跳 RPC) -- N 入本地队列
4. 如果 N 不可达 (心跳丢失), A 回退到顺时针下一跳 N+1

**为什么 Push 而非 Pull**: 在无中央 Frontier 的拓扑下, "Pull" 需要
节点主动询问"谁有我的 URL", 退化为全员 broadcast 或维护中心目录,
违背去中心化初衷. Push 则把路由决策本地化为单次哈希计算.

### 虚拟节点 (Virtual Nodes for Load Balancing)

- 每台物理机映射 **V=200 个虚拟节点**到环上, 减少 hash 倾斜
- 热点域名 (e.g. wikipedia.org) 单一物理机的吞吐限制由"该机的所有
  虚拟节点之和"决定 -- 远超单机带宽
- 节点上下线只影响 `1/N` (N=10K, 即 0.01%) 的 URL 重路由

### 批量节点间通信 (Batch Inter-node Communication)

10K 节点两两通信成本是 O(N^2). 关键优化:

- **不做全网广播**: 任何状态同步只在环上最近 K 个邻居之间传播
- **批量推送 URL**: 节点 A 缓冲发往同一目标 N 的 URL, 累积到 256 条
  或 100ms 后一次性发送, 摊销 RPC 开销
- **gossip Bloom Filter 摘要**: 每台机器周期性向邻居广播 URL-seen
  集合的 Bloom 摘要 (10MB 级别), 用于跨机预过滤 -- **但不用于本地
  去重** (本地 set 已经够小, 见 `production_constraints` 节)

### 路径示意 (Data Flow in Leaderless Variant)

```
节点 A: fetch(P) -> parse -> 提取链接 [u1, u2, u3, ...]
       |
       +-- u1 -> hash(domain) -> 环路定位 -> 节点 N7 (push)
       +-- u2 -> hash(domain) -> 环路定位 -> 节点 N42 (push)
       +-- u3 -> hash(domain) -> 环路定位 -> 节点 A 自己 (本地入队)
       |
       v
   邻居心跳 (gossip 给 A 的前后 20 邻居, 1Hz)
       |
       v
   Bloom 摘要广播 (1/min, 给 K 邻居用于跨机预过滤)
```
"""


# ---------------------------------------------------------------------------
# Delta 2: tradeoffs -- 2 new rows
# ---------------------------------------------------------------------------
TRADEOFFS_VARIANT = (
    "| **URL 分发模式 (Adversarial 10K 变体)** | **Push** (发现者主动推到目标节点) "
    "| **Pull** (Worker 周期向 Frontier 服务请求) "
    "| **Push (在 leaderless 拓扑下)**。Pull 需要全网共享的 Frontier 视图, "
    "退化为 broadcast 或中心目录, 违背去中心化初衷; "
    "Push 把路由决策化为单次 hash + 单跳 RPC, 同时支持本地 batch (256 条/100ms) "
    "摊销开销。在传统 leader-follower 拓扑下 Pull 仍然合理, 这一行只适用于 "
    "10K-节点变体 |\n"
    "| **拓扑选择 (Adversarial 10K 变体)** | **Leader-Follower** (中央 Frontier "
    "+ ZK 协调) | **Leaderless DHT** (Chord/Kademlia 风格环) "
    "| **Leaderless DHT (在对抗规模下)**。"
    "**Adversarial security argument**: 10K 节点中任意一台被攻陷, 在 "
    "leader-follower 架构下若刚好是 leader 则全网工作中断 "
    "(single attack = full outage); 而在 leaderless 拓扑下 "
    "leader exposure = follower exposure, 所有节点对等, "
    "攻陷一台仅影响 `1/N` 的 URL 路由, 由邻居 K (~20) 自动接管。"
    "代价: 一致性弱化为 eventual + gossip, 不适合需要强一致性 ordering 的场景 |"
)


# ---------------------------------------------------------------------------
# Delta 3: defense -- Q6 + Q7
# ---------------------------------------------------------------------------
DEFENSE_VARIANT = r"""### Q6: 在 10K-节点 leaderless 变体下, 如何保证 exactly-once 抓取? (Adversarial Scale)

**承认局限**: 单 leader 拓扑可以靠 leader 加锁实现 exactly-once,
但 10K 台对等机器没有中央协调者; 节点交接、网络分区、消息重传
都会引入重复抓取. 朴素方案 (全局分布式锁) 在 30 万 URL/秒的
吞吐量下会成为瓶颈.

**缓解策略**:

1. **将 10K 机器拆分为数千个 consumer group**: 按 `hash(url) mod G`
   (G ~= 3000) 把 URL 路由到对应 group. 每个 group 仅含 3-5 台机器
   (10K / 3K), 对一个 URL 的"是否已抓取"状态做仲裁. 仲裁范围从全网
   缩小到本 group 的 3-5 台 -- 共识成本下降 200x
2. **每 group 跑 Paxos 提交协议 (Paxos commit)**: 任一组员收到 URL
   后发起 Paxos 提案 "我即将抓取 url=X". 收到 majority (3/5) ACK 后
   才真正发起 HTTP 请求. ACK 隐含承诺: 这一轮内其他组员不会重复抓取.
   抓取完成后再跑一次 Paxos 提交结果 (status=done). 任何 timeout 都
   走 Paxos 回滚, 让 URL 回到队列等下一轮
3. **multi-leader 与 Paxos 的差异**: 传统 multi-leader (e.g. mysql
   master-master) 通过冲突解决规则 (LWW / vector clock) 容忍不一致;
   而 Paxos 在抓取前**先达成共识**, 任何组员都可以发起提案 (any
   member can initiate commit), 不需要预先选 leader. 这与中央调度
   "由 leader 一人决策"的模式根本不同, 也与 multi-leader "事后合并"
   不同 -- Paxos 是 **事前协调 (consensus before action)**
4. **代价与权衡**: 每 URL 需 2 轮 Paxos (抓取前 + 抓取后), 每轮
   3 RTT. 在每组 3-5 台、同机房 RTT < 1ms 的部署下, 一个 URL 的
   协调开销约 **10ms** -- 远小于 HTTP 抓取本身的 200-500ms.
   exactly-once 的额外成本被实际抓取主导, 整体吞吐损失 < 5%
5. **退化保证**: 即使 Paxos 失败 (例如 group 内 2/5 节点同时宕机
   导致无 majority), 系统降级为 at-least-once -- URL 仍会被抓取
   一次, 只是可能多次. 由于 content_hash 主键去重, 多次抓取仍是
   幂等的, 不会污染 Content Store

### Q7: 为什么 10K-机场景反而不需要 Bloom Filter? (Counter-intuitive)

**直觉错误**: 既然 URL 总数从 10 亿涨到 100 亿, 那 Bloom Filter
肯定要更大 -- 这是单机视角下的推断, 在 10K 机场景下完全失效.

**真实数学**:

每台机器实际只负责 `1/10000` 的 URL 集合. 算一下每机的本地 set 大小:

$$
\text{URL per machine} = \frac{10 \times 10^9}{10{,}000} = 10^6 \text{ URLs/机}
$$

每条 URL 用 SHA-256 hash 存储 (32 字节) + 元数据 (~70 字节) ≈ 100 字节:

$$
\text{Set size per machine} = 10^6 \times 100 \text{ B} = 10^8 \text{ B} = 100 \text{ MB/机}
$$

**结论**: 100 MB 完全装得下机器内存 (现代服务器 64-256 GB RAM), 用
**HashSet / RocksDB** 直接做精确去重即可, 0 误判率. Bloom Filter
节省的内存 (相对完整 set) 在 100MB 级别上是无意义的优化.

**那 Bloom 在哪里仍有用**:

1. **跨机预过滤 (cross-machine pre-filter)**: 节点 A 推送 URL 给
   节点 N 之前, 先用 N 广播过来的 Bloom 摘要 (~10MB) 本地预查 --
   如果 Bloom 说 "N 已经见过", A 直接丢弃, 省去一次跨机 RPC. 主要
   动机是 **节省出站带宽**, 不是节省内存
2. **跨数据中心同步**: 各 region 之间定期交换 Bloom 摘要做全局
   去重 (传输 100MB 跨洋成本 vs 传输 10MB 摘要), 这里 Bloom 体现
   压缩优势

**面试答题模式**: "Bloom Filter is bandwidth-saving here, not
memory-saving" -- 把工具与场景解耦, 是 Staff 候选人的核心信号.
"""


# ---------------------------------------------------------------------------
# Delta 4: production_constraints -- 1 new SPOF row
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS_VARIANT = (
    "| **协调层 (10K-Leaderless 变体)** | ZooKeeper 不存在 -- 无中心 SPOF "
    "| **顺时针下两邻居 peer-backup 模型**: 每台机器把 URL-seen 集合异步复制到"
    "环上顺时针下一台 + 下下一台 (clockwise-next-2). "
    "备份节点**只追踪状态, 不主动 fetch**, 避免重复抓取浪费带宽. "
    "主节点心跳丢失 (>30s), 下一邻居自动接管该机的 URL 路由槽位, "
    "用本地副本恢复; 若 2 个连续邻居同时挂掉的概率 ~ `(1/N)^2 = 10^-8`, "
    "可视为可忽略, 因此 next-2 备份足够. "
    "这一模型在 leaderless 拓扑下完整替代 ZooKeeper, 消除最后一处中心化协调依赖 |"
)


# ---------------------------------------------------------------------------
# UPSERT logic
# ---------------------------------------------------------------------------
def render_block(body: str) -> str:
    """Wrap a delta body in the META-VARIANT sentinel pair."""
    return f"{SENTINEL_BEGIN}\n{body}\n{SENTINEL_END}"


def upsert_block(content: str, body: str, anchor_pattern: str, mode: str) -> str:
    """Insert-or-replace the sentinel-bracketed block in `content`.

    If sentinel pair already present, replace its body. Otherwise locate
    the first match of `anchor_pattern` and insert relative to it.
    `mode` = "before" inserts the new block immediately before the anchor;
    `mode` = "after" inserts immediately after the anchor's match end.
    `mode` = "append" appends the block at end-of-content (used when the
    anchor is the trailing newline).
    """
    new_block = render_block(body) + "\n"

    sentinel_re = re.compile(
        re.escape(SENTINEL_BEGIN) + r".*?" + re.escape(SENTINEL_END) + r"\n?",
        re.DOTALL,
    )
    if sentinel_re.search(content):
        return sentinel_re.sub(new_block, content, count=1)

    if mode == "append":
        sep = "" if content.endswith("\n") else "\n"
        return content + sep + new_block

    m = re.search(anchor_pattern, content, flags=re.DOTALL)
    if not m:
        raise SystemExit(
            f"[ERROR] anchor pattern {anchor_pattern!r} not found"
        )
    if mode == "before":
        return content[: m.start()] + new_block + "\n" + content[m.start():]
    if mode == "after":
        return content[: m.end()] + "\n" + new_block + content[m.end():]
    raise SystemExit(f"[ERROR] unknown mode {mode!r}")


def patch_architecture(orig: str) -> str:
    """Append a leaderless-variant H2 section after existing 数据分区策略 block."""
    return upsert_block(
        orig,
        body=ARCHITECTURE_VARIANT.rstrip("\n"),
        anchor_pattern=r"$",  # ignored when sentinel re-found OR mode=append
        mode="append",
    )


def patch_tradeoffs(orig: str) -> str:
    """Insert 2 new rows after the existing decision table's last row.

    Anchor: the 'Frontier 持久化' row (last existing table row); insert AFTER
    that row's terminating newline.
    """
    anchor = r"\| \*\*Frontier 持久化\*\*[^\n]*\|[^\n]*\|[^\n]*\|[^\n]*\|"
    return upsert_block(
        orig,
        body=TRADEOFFS_VARIANT,
        anchor_pattern=anchor,
        mode="after",
    )


def patch_defense(orig: str) -> str:
    """Append Q6 + Q7 after the existing Q5 (Bloom Filter 误判) section.

    Easiest anchor: append at end (Q5 is last in baseline content).
    """
    return upsert_block(
        orig,
        body=DEFENSE_VARIANT.rstrip("\n"),
        anchor_pattern=r"$",
        mode="append",
    )


def patch_production_constraints(orig: str) -> str:
    """Insert new SPOF row after the existing '协调服务 (ZooKeeper)' row."""
    anchor = r"\| \*\*协调服务 \(ZooKeeper\)\*\*[^\n]*\|[^\n]*\|[^\n]*\|"
    return upsert_block(
        orig,
        body=PRODUCTION_CONSTRAINTS_VARIANT,
        anchor_pattern=anchor,
        mode="after",
    )


COLUMN_PATCHERS = {
    "architecture": patch_architecture,
    "tradeoffs": patch_tradeoffs,
    "defense": patch_defense,
    "production_constraints": patch_production_constraints,
}


def main() -> int:
    """UPSERT the 4 META-VARIANT deltas; report char-count deltas."""
    if not DB_PATH.exists():
        raise SystemExit(f"[ERROR] DB not found: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM system_designs WHERE slug = ?",
        (SLUG,),
    )
    row = cursor.fetchone()
    if row is None:
        raise SystemExit(
            f"[ERROR] system_designs row not found for slug={SLUG!r}. "
            "Run scripts/content_interview_web_crawler.py first."
        )
    record_id = row[0]

    any_change = False
    for column, patcher in COLUMN_PATCHERS.items():
        cursor.execute(
            f"SELECT {column} FROM system_designs WHERE id = ?",  # noqa: S608
            (record_id,),
        )
        old_body = cursor.fetchone()[0] or ""
        new_body = patcher(old_body)

        if old_body == new_body:
            print(
                f"[NOOP]   {column}: unchanged ({len(new_body)} chars) "
                "-- idempotent"
            )
            continue

        cursor.execute(
            f"UPDATE system_designs SET {column} = ? WHERE id = ?",  # noqa: S608
            (new_body, record_id),
        )
        delta = len(new_body) - len(old_body)
        sign = "+" if delta >= 0 else ""
        print(
            f"[UPDATE] {column}: {len(old_body)} -> {len(new_body)} chars "
            f"({sign}{delta})"
        )
        any_change = True

    if any_change:
        conn.commit()
        print("[DONE]   committed")
    else:
        print("[DONE]   no changes -- all 4 columns already at META-VARIANT state")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
