"""Seed framework node: pillar1.scaling_resource_model.

L4 coding extension: when input size is 10GB / 1TB / 1PB, the "correct" solution
shifts from algorithmic cleverness to a resource-model conversation: memory,
CPU, IO, network, disk locality, skew. This note provides a clarify-first
checklist and the standard upgrade ladder from single-machine to distributed.

Idempotent: re-running updates in place.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"

PILLAR_PATH = "pillar1"
NODE_PATH = "pillar1.scaling_resource_model"
NODE_TITLE = "Scaling & Resource Model: Large-Input Coding Framework (L4 Extension)"


def build_content() -> str:
    b = StudyNoteBuilder()
    b.set_title("Scaling & Resource Model: Large-Input Coding Framework")

    b.add_prerequisites([
        "基础数据结构与算法：排序、堆、哈希、归并",
        "内存层级直觉：L1/L2/L3 cache、RAM、SSD、HDD、网络带宽的数量级差异",
        "流式算法入门：单次扫描、亚线性内存（参考 pillar1.streaming_topk）",
        "MapReduce / Spark 的 map-shuffle-reduce 心智模型",
        "大 O 之外的常数：CPU 指令 ~1ns、SSD 随机 IO ~100us、网络 RTT ~1ms",
    ])

    b.add_term("EMS", "External Merge Sort",
               "外部归并排序：内存放不下时分块排序到磁盘，再 K-way 归并")
    b.add_term("CMS", "Count-Min Sketch",
               "概率频次草图，参考 streaming_topk 节点")
    b.add_term("HLL", "HyperLogLog",
               "概率基数估计，O(log log N) 位估 distinct count")
    b.add_term("PPK", "Partition-by-Key",
               "分布式按 key 哈希分片：同一 key 落同一机，本地有状态聚合后再合并")
    b.add_term("MR", "MapReduce",
               "map（本地变换）→ shuffle（按 key 重分区）→ reduce（有状态聚合）")
    b.add_term("IO", "Input/Output",
               "磁盘/网络读写，顺序 IO 比随机 IO 快 100-1000 倍")

    # --------------------------------------------------------------
    b.add_section("1. Why This Framework Matters (L4 Coding Extension)", [
        (
            "Google L4 及以上面试常在一道中等 LeetCode 题后追问："
            "“如果输入是 10GB / 1TB / 1PB 呢？”此时**直接套原算法会失败**："
            "(1) 内存装不下哈希表；(2) 单机 CPU 扫一遍要几小时；"
            "(3) 磁盘随机 IO 成为瓶颈；(4) 网络带宽 vs 计算成本权衡变化。"
            "这道题**不再考算法本身**，而是考**资源建模**与**工程判断**。"
        ),
        (
            "本节建立一套可复用的回答模板：**澄清输入规模 -> 识别瓶颈 -> 选择升级路径 "
            "-> 给出可度量的代价估算**。目标是在 5 分钟内把“10GB 怎么办”这类问题"
            "系统性地讲清楚，而不是临时拼凑。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("2. Clarify-First Checklist (开口前必问的 10 件事)", [
        (
            "当题面出现 “large input / 10GB / 1TB / 1PB / unbounded stream” 时，"
            "**先别急着写代码**，按以下清单逐项澄清。每一项的答案都会**质的改变**解法类别："
        ),
        (
            "- **规模量级**：10GB（单机内存）/ 1TB（单机 SSD）/ 1PB（必须分布式）？\n"
            "- **批 vs 流**：一次性文件 / append-only 日志 / 无界实时流？\n"
            "- **可否多遍**：文件可以扫 2-3 次？流只能一次？\n"
            "- **键空间 U**：distinct key 数量——能否进内存？U 是否远大于结果规模 K？\n"
            "- **分布形态**：均匀 / Zipf 重尾（热 key）/ 长尾（稀疏）？\n"
            "- **精度要求**：必须精确，还是 (epsilon, delta) 近似可接受？\n"
            "- **延迟约束**：离线 T+1 批？在线 ms 级查询？\n"
            "- **机器数**：单机 vs 100 台 vs 弹性？网络带宽 1G / 10G / 100G？\n"
            "- **存储格式**：CSV / Parquet / 列式？压缩率？是否已按 key 排序/分区？\n"
            "- **失败语义**：at-most-once / at-least-once / exactly-once？checkpointing？"
        ),
        (
            "**面试信号**：若面试官回答“10GB，单机，CPU/内存你自己假设”，"
            "那是在引导你进入“单机磁盘外排序 / streaming”领域；若回答“1PB，有集群”，"
            "则是在引导你讨论 MapReduce / Spark 套路。**听清暗示**再作答。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("3. Bottleneck Analysis: Memory vs CPU vs IO", [
        (
            "放大输入时**不同资源以不同速度饱和**。先判断哪一维先撞墙，"
            "再针对性升级；否则容易把“内存问题”误当“CPU 问题”去优化，走歪。"
        ),
        FormulaBlock(
            explanation="三种资源的典型单机上限（2024 年通用服务器）：",
            latex=(
                r"\text{RAM} \approx 256\text{GB},\quad "
                r"\text{SSD seq read} \approx 3\text{GB/s},\quad "
                r"\text{CPU} \approx 10^{10}\ \text{simple ops/s}"
            ),
        ),
        (
            "- **Memory-bound**：若算法需要 O(U) 哈希表而 U·32B > RAM（例如 1e10 key * 32B = 320GB）→ "
            "换**流式近似**（CMS/HLL）或**分块外部排序 + 归并**。\n"
            "- **CPU-bound**：若 per-item 做的是 O(log N) 比较 + 少量哈希，1e10 条记录 * 100ns ≈ 17 分钟 → "
            "尚可单机；若是 O(N) 或 O(N²) 子过程则必须降复杂度或并行。\n"
            "- **IO-bound**：10GB 文件顺序读只需 3-5 秒，但若**随机 IO**（4KB 随机读约 100us）"
            "则 10GB / 4KB = 2.5e6 次 * 100us = 250 秒——慢 50 倍。设计要保证**顺序扫描**。"
        ),
        (
            "**判定口诀**：先估 **working set**（最大中间状态）vs 可用内存；"
            "再估 **total ops** vs CPU 预算；最后估 **bytes moved** vs IO 带宽。"
            "哪一项最先超，哪一项就是瓶颈。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("4. Single-Machine Upgrades (量级 1: 10GB-1TB)", [
        (
            "在“单机但装不下内存”区间，以下是**按认知顺序**的标准升级路径。"
            "每一步都是“算法层改造”而非“加机器”："
        ),
        (
            "- **流式 / 单次扫描**：把内存算法改写成 online 版本——"
            "把 `for x in arr: update(state)` 改成一次过，`state` 保持 O(1) 或 O(K) 大小。"
            "例：最大/最小、平均、方差（Welford 在线算法）、top-K（size-K 堆）。\n"
            "- **Reservoir sampling**：未知长度流上维持大小 k 均匀样本；"
            "  用于离线近似统计或训练集抽样。\n"
            "- **概率草图**：`CMS` 做频次，`HLL` 做基数，`Bloom filter` 做存在性，"
            "  全部 O(1)/O(log log N) 内存但带 (epsilon, delta) 误差。\n"
            "- **External merge sort (EMS)**：文件分 M 块（每块能进内存），分别排序写回磁盘，"
            "  再 K-way 归并（K 路最小堆）。复杂度 O(N log N)，IO 为 O(N/B) 顺序读写。\n"
            "- **mmap / 顺序 IO**：让 OS page cache 做工作，避免 read()/seek() 循环；\n"
            "- **列式/压缩**：Parquet/Arrow 只扫需要的列，压缩后 IO 再降 5-10 倍。"
        ),
        FormulaBlock(
            explanation="外部归并排序的 IO 成本（M 块、B 块大小、P passes）：",
            latex=r"\text{IO} = 2 \cdot \frac{N}{B} \cdot P,\quad P = \lceil \log_{M/B}(N/M) \rceil",
        ),
        (
            "**关键判据**：顺序 IO 成本 >= 网络传输成本 × 2 时，**仍值得单机做**，"
            "不要盲目上集群——集群的 shuffle 阶段开销常常反而更大。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("5. Distributed (量级 2: 1TB-1PB)", [
        (
            "单机 SSD 和内存都顶不住时进入分布式。**标准套路**："
            "MapReduce / Spark 的 **map -> shuffle -> reduce** 三段式，"
            "关键是理解每一段的代价来源："
        ),
        (
            "- **Map**：本地 per-partition 变换（filter/parse/local aggregate），并行度 = 分区数，"
            "  几乎无跨机通信；瓶颈是磁盘读取和 per-record CPU。\n"
            "- **Shuffle**：按 key 哈希重分区——跨机网络传输，**最昂贵的一步**。"
            "  shuffle 数据量 ≈ map 输出总字节数，消耗网络带宽和 NIC 中断。\n"
            "- **Reduce**：同 key 数据汇总到一台机器，做有状态聚合（sum/topK/join）。"
            "  并行度 = reducer 数，瓶颈常是单 reducer 的 key skew。"
        ),
        FormulaBlock(
            explanation="分布式时间下界（M mappers, R reducers, 网络带宽 BW）：",
            latex=r"T \ge \max\bigl(\frac{N}{M \cdot \text{disk}},\ \frac{|\text{shuffle}|}{BW},\ \frac{N_{\max}}{R \cdot \text{CPU}}\bigr)",
        ),
        (
            "**减少 shuffle 的三板斧**：\n"
            "- **Combiner / map-side aggregation**：在 map 端先做局部 reduce，"
            "  shuffle 数据量降 10-100 倍（前提：聚合算子**可结合可交换**，如 sum/max/count）。\n"
            "- **Broadcast join**：小表 (<100MB) 广播到所有 mapper，避免大表 shuffle。\n"
            "- **Pre-partitioned storage**：数据持久化时就按 join key 分区/排序（如 Hive buckets），"
            "  join 时跳过 shuffle——**空间换时间**。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("6. Key Skew: The Silent Killer", [
        (
            "分布式方案**最常见的失败模式**不是正确性，而是**某个 reducer 卡住不动**——"
            "真实数据 Zipf 分布：极少数 hot key 占 50%+ 流量。单 reducer 处理 500GB 数据耗尽内存或 CPU。"
        ),
        (
            "- **Salting (two-stage aggregation)**：对 hot key 加随机后缀 `(key, rand % s)`，"
            "  第一阶段按 salted key 聚合（负载分散到 s 个 reducer），第二阶段去 salt 再合并。"
            "  适用于 sum/count/avg 等可结合算子。\n"
            "- **Heavy-hitter fast path**：先用 CMS/Space-Saving 在线识别 top-N hot keys，"
            "  对它们走独立 pipeline（broadcast 或专用 reducer），其余走标准 PPK。\n"
            "- **Skew-aware partitioning**：自适应 partitioner 读取 sample 统计，"
            "  把 hot key 分摊到多个 partition 或单独处理（Spark AQE）。\n"
            "- **分阶段 reduce**：tree aggregation，多层 reducer，每层汇聚前一层结果，"
            "  单点数据量指数下降。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("7. Worked Example 1: Bucket-Sort Scaled to Distributed", [
        (
            "**题面**：给定 1PB 整数文件（范围 [0, 1e9]），全局排序输出。"
        ),
        (
            "**单机不行**：1PB / 3GB/s ≈ 百小时；内存装不下 1e9 整数桶；需要分布式。"
        ),
        (
            "**方案（Terasort 范式）**：\n"
            "1. **Sampling pass**：从输入随机采样 1e5 个 key，排序得到 R-1 个 **splitter**，"
            "   定义 R 个值区间（保证各区间数据量近似均衡——**解决 skew**）。\n"
            "2. **Map phase**：每个 mapper 读一份数据，按 splitter 分到 R 个桶，写本地文件。\n"
            "3. **Shuffle**：按桶号把数据传给对应 reducer（每 reducer 拿一个区间）。\n"
            "4. **Reduce phase**：每 reducer 本地做**外部归并排序**（EMS），写出有序区间。\n"
            "5. **输出**：R 个有序区间首尾拼接即为全局有序。"
        ),
        FormulaBlock(
            explanation="Terasort 复杂度（N=1PB, R=1000, 机器 M 台）：",
            latex=r"T = O(N / M / \text{disk}) + O(|\text{shuffle}| / BW) + O((N/R) \log (N/R))",
        ),
        (
            "**关键技巧**：sampling + splitter 保证区间均衡，避免**最慢 reducer 拖累全局**。"
            "这是分布式排序的标准答案，Hadoop Terasort 1TB/min 基准就是这个套路。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("8. Worked Example 2: Meeting Rooms on Huge Interval Stream", [
        (
            "**题面**：给 1e10 条会议区间 (start, end)，求同时发生的最大会议数（interval overlap maximum）。"
            "原题（LC 253）单机解：扫描事件点 + 堆 O(N log N)。放大后怎么办？"
        ),
        (
            "**瓶颈**：排序 1e10 个事件点需 ~1TB 中间数据，单机不行。"
            "**分布式解：时间窗口分区 + 局部聚合 + 边界修正**："
        ),
        (
            "1. **Partition by time window**：把时间轴切成 P 个不重叠窗口 [t_0, t_1), [t_1, t_2), ...\n"
            "2. **Local phase**：每 partition 独立扫描落在本窗口的事件点，"
            "   统计该窗口内最大并发数 `max_i`，同时记录**窗口开始时已进行中的会议数** `open_i`"
            "   （即 start < t_i 且 end >= t_i 的区间）。\n"
            "3. **Boundary correction**：跨窗口的区间需要**广播**到所有受影响窗口，"
            "   或通过前缀和累加 `open` 计数。\n"
            "4. **Global max**：`max(max_i + delta_i)`，其中 `delta_i` 是从第 1 个窗口到第 i 个窗口"
            "   的跨界会议累积。"
        ),
        (
            "**陷阱**：若直接按 start 时间 hash 分片，则同一时间点的事件会散到多机——"
            "无法在单机上精确算并发数。**必须按时间窗口范围分片**（range partition），"
            "确保每窗口内部可独立算，再合并边界。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("9. Decision Table: Input Size -> Approach", [])
    b.add_comparison_table(
        headers=["规模", "瓶颈主因", "推荐路径", "关键技术"],
        rows=[
            ["< 1GB", "无", "内存朴素算法", "标准数据结构"],
            ["1-10GB", "内存", "流式 / 采样 / 草图", "CMS, HLL, Reservoir, Welford"],
            ["10-100GB", "内存 + IO", "External merge sort / mmap", "EMS, Parquet, 列式"],
            ["100GB-1TB", "单机 IO", "单机 + 专用硬件 / 开始考虑分布式", "NVMe SSD, 并行读"],
            ["1-100TB", "单机硬件上限", "MapReduce / Spark", "PPK, combiner, broadcast join"],
            ["100TB-1PB", "shuffle + skew", "Spark AQE / salting / tree agg", "salting, skew-aware"],
            ["> 1PB", "网络 + 协调", "专用系统 (BigQuery, Snowflake)", "列式 + 压缩 + 预聚合"],
        ],
        title="Input Size -> Approach Selection",
    )

    # --------------------------------------------------------------
    b.add_section("10. Common Pitfalls", [
        (
            "- **不澄清规模就写代码**：面试官问“大输入”时直接写 LeetCode 解法 = 没听懂题。\n"
            "- **把“加机器”当万能解**：shuffle 成本常常比单机外排序更贵；先问“能不能单机外排”。\n"
            "- **忽略 key skew**：均匀分布假设在真实数据几乎不成立；必须显式提 salting / 热点识别。\n"
            "- **round-robin 分片后做有状态聚合**：同 key 被切，结果错。必须 PPK。\n"
            "- **盲目乐观估算**：面试官会问“10GB 你要多久”；不能答“很快”，"
            "  要会估 `10GB / 3GB/s ≈ 3s`（纯顺序读）或 `1e9 * 100ns = 100s`（per-item 处理）。\n"
            "- **忘记 precision 降级**：能答“精确太贵，CMS (eps=1e-4) 只用 1MB”是加分项。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("11. Interview Q&A", [])
    b.add_interview_qa(
        "10GB 日志文件找 top-100 视频观看数，单机怎么做？",
        (
            "**先估瓶颈**：假设 U=1e7 distinct video_id，hashmap<id, count> 约 320MB——单机装得下。"
            "**精确解**：顺序扫一遍填 hashmap（O(N) IO-bound，约 3-5s 顺序读），"
            "再用 size-100 min-heap 选 top-100（O(U log 100)）。"
            "**若 U 未知可能超内存**：用 CMS (eps=1e-4, delta=1e-3 约 750KB) + size-100 heap。"
            "**失败模式**：若 key 是长字符串使 hashmap 内存炸，需先 hash→int。"
        ),
    )
    b.add_interview_qa(
        "放大到 1PB 日志、分布式集群，方案怎么变？",
        (
            "**按 video_id PPK 分片** -> 每 reducer 本地 top-100 + 精确计数 -> "
            "coordinator K-way merge 拿全局 top-100。**Skew 处理**：热 video（Zipf 头）"
            "可能压垮单 reducer，用 Space-Saving 先识别 top-N hot，对它们走独立路径；"
            "其余 salting 或 tree aggregation。**Combiner** 在 map 端先局部聚合，"
            "shuffle 数据量降 10-100 倍。"
        ),
    )
    b.add_interview_qa(
        "如果题目变成“1PB 整数全局排序”怎么办？",
        (
            "**Terasort 范式**：(1) sampling pass 抽 1e5 key 确定 R-1 个 splitter，"
            "保证 R 个区间数据量均衡（**对抗 skew**）；(2) mapper 按 splitter 分桶；"
            "(3) shuffle 到对应 reducer；(4) 每 reducer 本地外部归并排序；"
            "(5) 输出拼接即全序。**瓶颈在 shuffle 阶段**，靠 splitter 均衡和网络预算控制。"
        ),
    )
    b.add_interview_qa(
        "什么时候“不要上分布式”？",
        (
            "三个信号：**(1)** 数据量 < 1TB 且可顺序扫描——单机 NVMe + EMS 比集群 shuffle 快且便宜；"
            "**(2)** 算法有严重数据依赖（无法 partition，如全局图算法小规模）；"
            "**(3)** 延迟敏感的在线查询——分布式 RPC 抖动常常比单机慢。"
            "**判据**：`单机 IO 成本 < 2 × 网络传输成本` 时选单机。"
        ),
    )

    # --------------------------------------------------------------
    b.add_checklist("Self-Check (面试前必过)", [
        "能背出 10 项 clarify-first 清单，遇到大输入题先全部澄清",
        "能区分 memory / CPU / IO 瓶颈，给出量化估算（RAM 256GB, SSD 3GB/s, CPU 1e10 ops/s）",
        "能推导单机 EMS 的 IO 成本 O(N/B · log_M/B(N/M))",
        "能写出 MapReduce 三段式及各段瓶颈（map IO / shuffle 网络 / reduce skew）",
        "能列举至少 3 种 key-skew 缓解（salting / heavy-hitter fast path / tree aggregation）",
        "能解释 Terasort 的 sampling splitter 为何能对抗 skew",
        "能解释“时间窗口分区”解法处理区间并发类问题的边界修正",
        "能判断何时**不应**上分布式（数据 <1TB + 顺序可扫 + 网络>2×单机 IO）",
    ])

    return b.build()


def upsert_leaf(conn: sqlite3.Connection, content: str) -> int:
    pillar = conn.execute(
        "SELECT id, depth FROM framework_nodes WHERE path = ?", (PILLAR_PATH,)
    ).fetchone()
    if not pillar:
        print(f"[FAIL] Pillar path {PILLAR_PATH} not found")
        sys.exit(1)
    pillar_id, pillar_depth = pillar

    existing = conn.execute(
        "SELECT id FROM framework_nodes WHERE path = ?", (NODE_PATH,)
    ).fetchone()
    if existing:
        node_id = existing[0]
        conn.execute(
            "UPDATE framework_nodes SET description = ?, title = ? WHERE id = ?",
            (content, NODE_TITLE, node_id),
        )
        action = "UPDATED"
    else:
        cur = conn.execute(
            """
            INSERT INTO framework_nodes
                (parent_id, path, depth, title, description, importance, priority, status, progress_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (pillar_id, NODE_PATH, pillar_depth + 1, NODE_TITLE, content,
             0.90, "P0", "not_started", 0.0),
        )
        node_id = cur.lastrowid
        action = "INSERTED"
    length = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()[0]
    print(f"[{action}] leaf id={node_id} path={NODE_PATH} length={length} chars")
    return node_id


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)
    content = build_content()
    warnings = StudyNoteBuilder.validate(content)
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")
    conn = sqlite3.connect(str(DB_PATH))
    try:
        upsert_leaf(conn, content)
        conn.commit()
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    main()
