"""Seed framework node: pillar1.streaming_topk.

Creates the leaf ``pillar1.streaming_topk`` directly under pillar1 and
populates its ``description`` via StudyNoteBuilder.

Usage::

    python scripts/seed_streaming_topk.py

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
NODE_PATH = "pillar1.streaming_topk"
NODE_TITLE = "Streaming Top-K: Precise, Probabilistic, and Distributed"


def build_content() -> str:
    b = StudyNoteBuilder()
    b.set_title("Streaming Top-K Deep Dive: Precise vs Probabilistic vs Distributed")

    b.add_prerequisites([
        "堆 / 优先队列：最小堆的 O(log K) 插入与删除",
        "哈希表：摊销 O(1) 计数与查找",
        "概率论基础：期望、方差、Chernoff / Markov 不等式直观",
        "Hash 函数：pairwise independent / universal hashing 的意义",
        "数据流模型（streaming model）：单次扫描、亚线性内存、不可回溯",
    ])

    b.add_term("CMS", "Count-Min Sketch",
               "用 d 行 w 列的哈希计数阵近似频次，保证过估不欠估")
    b.add_term("HLL", "HyperLogLog",
               "基数（distinct count）估计器，与 top-K 相邻但不直接解 top-K")
    b.add_term("SS", "Space-Saving",
               "Misra-Gries 家族的 O(K) 内存重项估计器，保证误差界")
    b.add_term("MG", "Misra-Gries",
               "经典 K-counter 算法；每来一项或命中计数++，或空槽占用，或全体 -1")
    b.add_term("PPK", "Partition-by-Key",
               "分布式 top-K 的标准套路：按 key 哈希分片 -> 各分片本地 top-K -> K-way merge")

    # --------------------------------------------------------------
    b.add_section("1. Problem Framing & Clarify-First", [
        (
            "**Top-K** 的精确定义取决于上下文：(1) 批处理下给定数组找频次前 K 大；"
            "(2) 流式（streaming）下每秒上亿事件、内存受限、只能单次扫描；"
            "(3) 分布式多机共同观测同一个流。三种定义对应**完全不同**的算法族，"
            "面试时必须先澄清以下维度："
        ),
        (
            "- **数据规模**：N 可装入内存？单机 vs 多机？流式 vs 有界？\n"
            "- **精度要求**：必须精确（exact）还是允许 (epsilon, delta) 近似？\n"
            "- **项空间**：key 基数 U 有多大？U 是否远大于 K？\n"
            "- **分布形态**：重尾（power-law，少量 key 占据大部分质量）还是均匀？\n"
            "- **可否多遍**：真正的流只能一遍；批处理可以两遍\n"
            "- **窗口语义**：全局 top-K / 滑动窗口 / 时间衰减？"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("2. Precise Baseline: Heap + Hash-Map", [
        (
            "**N 能进内存**：两遍扫描。第一遍 hashmap 统计全体频次，"
            "第二遍用大小固定为 K 的**最小堆**（min-heap）做 top-K 选拔。"
            "总复杂度 O(N + U log K)，空间 O(U)。"
        ),
        FormulaBlock(
            explanation="堆法的时间复杂度上界：",
            latex=r"T(N, U, K) = O(N) + O(U \log K)",
        ),
        (
            "**实现要点**：堆中存 (count, key) 二元组；新键或已在堆中时更新；"
            "若新键频次 > 堆顶则弹出堆顶、插入新键；否则丢弃。"
            "需要 tie-breaking 规则（按字典序或 ID）以保证确定性。"
        ),
        (
            "**失败模式**：U 过大（亿级 key）导致 hashmap 装不下内存；"
            "此时要么分片计数，要么放弃精确，转向概率方案。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("3. Count-Min Sketch (CMS)", [
        (
            "**CMS** 用 d 个相互独立的哈希函数 h_1,...,h_d 和 d 行、每行 w 列的计数数组 C[1..d][1..w] 做近似频次估计。"
            "每来一项 x：所有行同时 C[i][h_i(x)] += 1；查询 x 的频次估计 = min over i of C[i][h_i(x)]。"
            "min 操作保证**仅过估不欠估**（no under-estimate），因为哈希碰撞只会把别人的计数叠到自己头上。"
        ),
        FormulaBlock(
            explanation="CMS 参数与误差保证（epsilon, delta）：",
            latex=r"w = \lceil e / \varepsilon \rceil,\quad d = \lceil \ln(1/\delta) \rceil",
        ),
        FormulaBlock(
            explanation="误差界（以概率 >= 1 - delta 成立）：",
            latex=r"\Pr\bigl[\hat{f}(x) \le f(x) + \varepsilon \cdot \|F\|_1\bigr] \ge 1 - \delta",
        ),
        (
            "其中 \\|F\\|_1 = 流中总事件数 N。这是**加性误差**：若 N=1e9、取 epsilon=1e-4，"
            "则每个频次估计的误差上界约为 1e5。**重项（heavy hitters）**频次远大于误差时几乎可视为精确；"
            "稀有项会被误差淹没，但我们本就不关心它们。"
        ),
        (
            "**与 top-K 的组合**：CMS 提供频次查询；再配合一个**大小 K 的最小堆**缓存当前 top-K 候选。"
            "每来一项先更新 CMS，然后用 CMS 查询其估计频次，若 > 堆顶则入堆。空间 O(w d + K) 完全脱离 U。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("4. HyperLogLog (HLL): Cardinality, Not Top-K", [
        (
            "**HLL** 解决的是**distinct count**（基数）：流里一共见过多少个不同的 key，**而不是谁是 top-K**。"
            "之所以放到这里，是因为在面试中很容易被误选：当面试官问“用 1MB 内存估计 1e9 流的 top 100”时，"
            "HLL 无法直接回答——它不保留 per-key 计数。"
        ),
        FormulaBlock(
            explanation="HLL 核心思想：用哈希值前导 0 的最大长度估计基数（m 个桶，取各桶最大前导 0 并做谐波平均）：",
            latex=r"\hat{n} = \alpha_m \cdot m^2 \cdot \left(\sum_{j=1}^{m} 2^{-R_j}\right)^{-1}",
        ),
        (
            "**典型用途**：DAU/MAU 唯一用户数、unique-query 数。**与 top-K 的关系**："
            "HLL 可以回答“总共有多少 distinct key”，配合 CMS 或 Space-Saving 才能回答“哪些 key 是 top-K”。"
            "**面试 trap**：若面试官只要 cardinality，用 HLL 即可（1MB 内存做 1e9 流 < 1% 误差）；若要 top-K，**别用 HLL**。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("5. Space-Saving / Misra-Gries (Lossy Counting Family)", [
        (
            "**Misra-Gries**：维护 K 个 (key, count) 槽位。来一项 x："
            "若 x 已在槽中 -> count++；否则若有空槽 -> 占用，count=1；否则**所有槽 count 同步 -= 1**，空了就释放。"
            "**保证**：真实频次 > N/(K+1) 的 key 一定在最终槽中（可能被低估），常用于“频次占比 > 1/(K+1) 的重项”场景。"
        ),
        (
            "**Space-Saving (Metwally 2005)**：Misra-Gries 的改进版。槽满且新 key 来时，**替换最小 count 槽的 key** 并把它的 count 继承下来 + 1。"
            "估计频次的误差 <= 最小 count，保证**过估不欠估**（与 CMS 同向）。"
        ),
        FormulaBlock(
            explanation="Space-Saving 误差界：对每个被跟踪的 key x，",
            latex=r"f(x) \le \hat{f}(x) \le f(x) + \min_{\text{slot}} \text{count} \le f(x) + N/K",
        ),
        (
            "**对比 CMS**：Space-Saving 内存 O(K)（与跟踪项数成正比、与 epsilon 无关），"
            "给出**确定性**上界；CMS 内存 O(1/epsilon · log(1/delta))，给出概率保证。"
            "在 power-law 分布（少量大 key + 巨量小 key）下 Space-Saving 通常**实测更准且更省**。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("6. Decision Table: Memory x Accuracy x Stationarity", [])
    b.add_comparison_table(
        headers=["场景", "内存", "精度", "分布要求", "推荐算法"],
        rows=[
            ["N, U 均装内存", "O(U)", "精确", "任意", "Hashmap + K-heap"],
            ["N 大 U 大, 要精确", "不可行", "-", "-", "不可能（下界证明）"],
            ["N 大 U 大, (eps, delta) 近似", "O((1/eps) log(1/delta))", "加性 eps·N", "任意", "**CMS + K-heap**"],
            ["重尾 + 要重项", "O(K)", "确定性上界", "频次占比>1/K", "**Space-Saving**"],
            ["只要 distinct count", "O(m log log n)", "~1%", "任意", "**HyperLogLog**"],
            ["滑动窗口 top-K", "O(W) 或 O(K·分块)", "近似", "有时间戳", "Exponential Histogram + SS"],
            ["均匀抽样代表", "O(k)", "无偏抽样", "任意", "Reservoir Sampling"],
            ["分布式无界流", "O(K·P)", "近似", "任意", "**Partition-by-Key + K-way merge**"],
        ],
        title="Memory vs Accuracy vs Distribution -> Algorithm Choice",
    )

    # --------------------------------------------------------------
    b.add_section("7. Reservoir Sampling (Window-Uniform Reference)", [
        (
            "**Reservoir sampling (Vitter's Algorithm R)**：在**未知长度**的流上维持**大小 k 的均匀随机样本**。"
            "来第 i 项（i > k）时以概率 k/i 替换蓄水池中随机一项，否则丢弃。结束后蓄水池即为 size-k 均匀样本。"
        ),
        FormulaBlock(
            explanation="每项出现在最终样本中的概率：",
            latex=r"\Pr[\text{item } i \in \text{reservoir}] = \frac{k}{N}",
        ),
        (
            "**与 top-K 的关系**：Reservoir 不保证抽到的就是 top-K，而是**均匀代表**——"
            "用于“我需要随机 k 条日志”而**非**“我需要最频繁 k 条”。但它是流式算法家族的重要对照组，"
            "面试时常被问“top-K 和 reservoir 有何区别”。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("8. Distributed Top-K: Partition-by-Key + K-Way Merge", [
        (
            "**标准套路（PPK）**：P 台机器，把每条事件 x 按 hash(key(x)) mod P 发往对应机器。"
            "每台机器在本地维护**精确或近似** top-K（第 2、3、5 节任一算法）。"
            "最终 coordinator 收集 P 个 top-K 列表，做 **K-way merge**（最小堆 / 多路归并）挑出全局 top-K。"
        ),
        FormulaBlock(
            explanation="单机本地处理 + 归并总复杂度（各机 N/P 条）：",
            latex=r"T_{\text{local}} = O(N/P) + O(K \log K),\quad T_{\text{merge}} = O(P K \log P)",
        ),
        (
            "**关键正确性条件**：因为 partition-by-key 保证同一 key 的全部事件落在同一机器，"
            "**本地 top-K 中最大的 K 项一定覆盖全局 top-K 的超集**（当 K_local >= K 时），归并后不会漏。"
        ),
        (
            "**错误套路**：若按**轮询 / round-robin** 分发事件，则同一 key 会被切到多台机器上，"
            "本地 top-K 不能直接合并——需要 shuffle 阶段重新按 key 聚合（等价于 MapReduce word-count）。"
            "这是**常见错误答案**，面试时要显式否定它。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("9. Key-Skew Mitigation", [
        (
            "真实流往往严重偏斜：极少数 key 占 50%+ 流量（Zipf / power-law）。"
            "partition-by-key 会把这些 hot key 全压到某一台机器，出现 **straggler**。常见对策："
        ),
        (
            "- **Salting**：对 hot key 加随机后缀 (key, rand % s) 先做局部聚合，再第二阶段合并掉 salt。\n"
            "- **Two-stage aggregation**：第一阶段 combiner 在 map 端预聚合，shuffle 数据量降 10-100 倍。\n"
            "- **Heavy-hitter fast path**：先用 Space-Saving 在线识别 top-N hot keys，对它们走独立处理链路，"
            "  其余走标准 PPK。类似 Apache Flink 的 rebalance + keyBy。\n"
            "- **Sticky partitioning + power-of-two choices**：每个 key 在 2 个候选机器间选负载较轻者，"
            "  降低单点热化（仅对无状态聚合适用）。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("10. Worked Example: Log-file Top-K Videos", [
        (
            "**题面**（连接 T-P1-206 coding 题）：日志流每行 (video_id, event)，估计**观看数**最多的前 100 部视频。"
            "单机 10GB 日志、1e8 条记录；U（distinct video_id）约 1e7。"
        ),
        (
            "**单机精确解**：hashmap<video_id, count> 装得下（约 10M 条 * (8+8) ≈ 160MB），"
            "扫一遍填表，再用 size-100 min-heap 选 top-100。O(N) + O(U log 100)。"
        ),
        (
            "**多机精确解**：按 hash(video_id) mod P 分片；每机本地精确 top-100 + K-way merge。"
            "注意**本地必须 K_local >= 全局 K**（通常取 2K~5K）以防边界情况下精确度丢失——"
            "但若只需每机 top-K 且所有机器都看完整流（非 partition），则必须取 K_local = K 并合并时重加。"
        ),
        (
            "**概率解**：CMS (eps=1e-4, delta=1e-3) 约 w=27184, d=7 -> ~750KB 内存（与 U=1e7 解耦）；"
            "配合 size-100 heap 即得 top-K。适合 U 未知或远超预算的场景。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("11. Common Pitfalls", [
        (
            "- **用 HLL 做 top-K**：HLL 只算 distinct 总数，不保存 per-key 计数。**错误**。\n"
            "- **round-robin 分片后直接本地 top-K 合并**：同一 key 在多机上被切，合并结果错。\n"
            "- **CMS 用于稀有项频次查询**：稀有项会被噪声淹没；CMS 只对重项准确。\n"
            "- **忽略 tie-breaking**：频次相等时排序依赖 hash 顺序会产生不确定性；必须指定 (count desc, key asc)。\n"
            "- **滑动窗口直接用全局 top-K 算法**：需要时间衰减或分块窗口，不能简单套 CMS。\n"
            "- **低估内存常数**：CMS 的 w=e/eps 看似省，但若 eps=1e-6 则 w≈2.7M * d 行 * 4B = 百 MB 级；"
            "  Space-Saving 在重尾分布下通常实测更省。"
        ),
    ])

    # --------------------------------------------------------------
    b.add_section("12. Interview Q&A", [])
    b.add_interview_qa(
        "面试官给 1MB 内存、要估计 1e9 事件流的 top 100 视频，怎么做？",
        (
            "**先澄清**：要精确还是近似？有无分布先验？"
            "假定允许 (epsilon=1e-4, delta=1e-3) 近似：用 **CMS** (w≈2.7e4, d=7 约 750KB) 做频次估计，"
            "加一个大小 100 的最小堆缓存 top-K 候选。每来一项：CMS 更新 + 查询 + 可能入堆。"
            "若分布重尾，**Space-Saving** 用 O(K)=几 KB 即可给出确定性上界，更省也更准。"
            "**强调**：HLL 不能用——它只算 distinct 总数。"
        ),
    )
    b.add_interview_qa(
        "CMS 和 Space-Saving 都保证过估不欠估，具体差别在哪？",
        (
            "**CMS**：空间 O((1/epsilon) log(1/delta))，误差是**加性 epsilon·N** 的概率保证，"
            "对任意分布都成立。**Space-Saving**：空间 O(K)（只跟踪 K 个 key），"
            "误差 <= N/K 的**确定性上界**，特别在**重尾分布**下几乎精确（大 key 的噪声被小 key 的稀疏性稀释）。"
            "工程上：若只关心 top-K 本身，优先 Space-Saving；若需要对任意 key 都能查询频次，用 CMS。"
        ),
    )
    b.add_interview_qa(
        "分布式 top-K 为什么 partition-by-key 是对的，round-robin 为什么错？",
        (
            "**Partition-by-key** 保证“同一 key 的所有事件落在同一机器”——于是本地精确计数后，"
            "每机的本地 top-K 合集一定**覆盖**全局 top-K（K_local >= K 时），K-way merge 即正确。"
            "**Round-robin** 把同一 key 切到多机上，本地计数都是局部片段，"
            "直接合并会把同一 key 的不同片段当作独立 key 对待——必须额外 shuffle-by-key 重聚合（等价于 MapReduce word-count 的 reduce 阶段），"
            "否则结果错。**关键判据**：聚合算子是否**按 key 有状态**——有状态就必须按 key 分片。"
        ),
    )

    # --------------------------------------------------------------
    b.add_checklist("Self-Check (面试前必过)", [
        "能默写 CMS 的 w、d 参数公式以及 (epsilon, delta) 误差界",
        "能解释为何 CMS 只过估不欠估（碰撞叠加 + min 操作）",
        "能区分 HLL（cardinality）与 top-K 算法，并指出面试 trap",
        "能写出 Space-Saving 的槽替换规则与 N/K 误差界",
        "能解释 partition-by-key 为何正确、round-robin 为何错",
        "能给出至少 2 种 key-skew 缓解方案（salting / combiner / hot-key fast path）",
        "能说出 reservoir sampling 与 top-K 的目标差异",
        "给 1MB/1e9 流/top-100 能现场估算 CMS 参数并说明可行性",
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
             0.95, "P0", "not_started", 0.0),
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
