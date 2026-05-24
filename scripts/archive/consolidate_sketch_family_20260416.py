"""T-P0-452: Consolidate sketch family (CMS/HLL/Space-Saving) around the
3-axis canonical framework.

Rewrites framework_node 196 (pillar1.streaming_topk) into the CANONICAL
3-axis lens: hash source x counter/register structure x aggregation operator.
Primitives become specific axis combinations; production pattern (cold filter
+ two-layer bucketing + epoch reset) is added as system-design section.

Surgically compacts CMS/HLL mentions in:
- framework_node 197 (pillar1.scaling_resource_model)
- framework_node 103 (pillar3.building_blocks.realtime_features)
- company_document 58 (Pinterest Sketch/Streaming 1-Pager)

Each of the 3 satellite artifacts keeps its own non-sketch content intact
but reduces CMS/HLL math/formulas to a 1-2 line pointer to node 196.

Idempotent: safe to re-run. Surgical updates detect whether the old pattern
still exists before replacing.

Usage::

    python scripts/consolidate_sketch_family_20260416.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"

NODE_196_PATH = "pillar1.streaming_topk"
NODE_197_PATH = "pillar1.scaling_resource_model"
NODE_103_PATH = "pillar3.building_blocks.realtime_features"
DOC_58_ID = 58
NODE_196_TITLE = (
    "Streaming Top-K & Sketches: 3-Axis Canonical Framework "
    "(Hash x Counter x Operator)"
)
DOC_58_TITLE = "Pinterest Sketch/Streaming Theory 1-Pager"


# ==========================================================================
# Node 196: CANONICAL 3-axis sketch framework (full rewrite)
# ==========================================================================

def build_node_196_content() -> str:
    b = StudyNoteBuilder()
    b.set_title(
        "Streaming Top-K & Sketches: 3-Axis Canonical Framework "
        "(Hash x Counter x Operator)"
    )

    b.add_prerequisites([
        "堆 / 优先队列：最小堆 O(log K) 插入删除",
        "哈希表：摊销 O(1) 计数查找；universal / pairwise independent hashing",
        "概率论：期望、方差、Markov / Chebyshev / Chernoff 不等式直观",
        "数据流模型 (streaming)：单次扫描、亚线性内存、不可回溯",
        "对数/位操作：前导零计数 (leading-zero count)、几何分布直觉",
    ])

    b.add_term(
        "CMS", "Count-Min Sketch",
        "d 行 w 列哈希计数阵 + 行 min 查询；3-轴组合 = 流标签哈希 / 标量计数器 / 每到达累加",
    )
    b.add_term(
        "CMM", "Count-Mean-Min",
        "CMS 的偏差修正变体：减去同桶噪声期望，行间取 median（非 min）",
    )
    b.add_term(
        "HLL", "HyperLogLog",
        (
            "双重身份：在 DB/工程社区严格指 Flajolet 2007 基数估计器实例 "
            "(bitmap register + idempotent max)；在 network-measurement 社区泛指"
            "基于哈希+m-桶+位寄存器的家族（包含 PCSA、LogLog、HLL++ 等）"
        ),
    )
    b.add_term(
        "SS", "Space-Saving",
        "Misra-Gries 改进版：O(K) 槽位 + 替换最小槽规则；确定性过估上界 N/K",
    )
    b.add_term(
        "MG", "Misra-Gries",
        "经典 K-counter：命中++ / 空槽占用 / 槽满时全体 -= 1",
    )
    b.add_term(
        "PCSA", "Probabilistic Counting (Flajolet-Martin)",
        "基数估计先驱：bitmap 寄存器 + 位占用分析；HLL 可视为其谐波均值改进",
    )
    b.add_term(
        "PPK", "Partition-by-Key",
        "分布式聚合标准套路：按 hash(key) 分片 -> 各机本地 top-K -> K-way merge",
    )

    # ------------------------------------------------------------------
    b.add_section("1. Problem Framing & Clarify-First", [
        (
            "面试里 **Top-K / heavy-hitter / cardinality** 三类问题的精确解与近似解"
            "来自**同一族底层结构**，只是按不同维度组合。先 clarify 三件事："
        ),
        (
            "- **数据规模**：N 可装入内存？单机 / 多机？有界批 / 无界流？\n"
            "- **问题类型**：要精确频次 / heavy-hitter / cardinality / 随机样本？\n"
            "- **精度与预算**：(epsilon, delta) 近似可接受？目标内存上限？\n"
            "- **分布**：Zipf 重尾（hot-key 压力）还是均匀？\n"
            "- **窗口语义**：全局 / 滑动窗口 / 时间衰减？\n"
            "- **可否多遍**：真流只能一次；批处理可两遍（第一遍统计，第二遍选取）"
        ),
        (
            "澄清完成后，本节剩余内容围绕**一个核心视角**：把所有 sketch 看作"
            "**(hash 来源) x (计数/寄存器结构) x (聚合算子)** 三轴的具体组合。"
            "教材把 CMS/HLL/SS 当作孤立算法讲是**教学简化**；工程面试真正需要的"
            "是从 3 轴里按问题约束**挑组合**。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("2. Precise Baseline: Heap + Hash-Map", [
        (
            "**N 能进内存**：两遍扫描。第一遍 hashmap 统计全体频次，"
            "第二遍用大小 K 的最小堆做 top-K 选拔。所有近似方案都要"
            "**先能说清精确解为何不行**，再上近似。"
        ),
        FormulaBlock(
            explanation="堆法时间复杂度：",
            latex=r"T(N, U, K) = O(N) + O(U \log K)",
        ),
        (
            "**失败模式**：U（distinct key）亿级时 hashmap 装不下；"
            "或 key 是长字符串，指针+冲突链让实际内存 2-5 倍膨胀。此时必须转向"
            "近似方案，本节剩下内容即 systematically 推导近似族。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("3. Terminology Grounding: HLL Family vs Flajolet Instance", [
        (
            "**务必在开口前声明**：\"**HLL**\" 在两个社区意义不同，混用会让回答"
            "听起来不严谨。"
        ),
        (
            "- **DB / 工程社区（Redis、Spark、BigQuery）**：HLL 严格指 Flajolet 2007"
            " 的 **cardinality 估计器实例**——哈希每个元素、用前 p 位选 m=2^p 个桶、"
            "每桶存前导零最大值、谐波均值组合输出。这是一种**特定实例**。\n"
            "- **Network-measurement / SIGCOMM 社区**：HLL 常作**家族名**"
            "泛指\"哈希 + m-桶 + 位寄存器 + 某种聚合\"这一整类结构，"
            "涵盖 PCSA、LogLog、HLL、HLL++、位占用变体等。\n"
            "- **跨社区交流时**必须先点明是说 family 还是 instance，否则对方可能"
            "误以为你把 bitmap register 的频次估计当成\"HLL 也能做频次\"（它不能，"
            "因为 Flajolet instance 只含 max 聚合算子——见第 5/7 节）。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("4. Three Canonical Axes (The Core Frame)", [
        (
            "把所有 sketch 沿三根正交轴拆开，**每个轴独立选择**，组合决定能解什么："
        ),
        (
            "**Axis 1 — Hash 来源（hash source）**：哈希取自何处？\n"
            "  - **Flow label**（canonical）：哈希 = h(key)；同一 key 的所有事件"
            "走同一桶。适合**按 key 聚合**（frequency, cardinality）。\n"
            "  - **Per-arrival Bernoulli**：每条事件独立以概率 p 通过；用于对重流"
            "降采样或做**frequency sketch 的相对误差改善**（第 6 节 Bernoulli-freq）。\n"
            "  - **其它维度**：时间戳、payload 特征——用于 sliding window 或"
            "跨特征联合估计。"
        ),
        (
            "**Axis 2 — 计数 / 寄存器结构（counter / register structure）**：桶里存什么？\n"
            "  - **Scalar counter**（整数）：最朴素，CMS、Space-Saving 使用；"
            "每次事件做加法。\n"
            "  - **Log counter (Morris)**：存 log_b(count) 而非 count，用随机近似加法"
            "`P(增) = b^(-stored)`；用 5-bit 存到 2^30 级别。**精度 vs 空间**权衡。\n"
            "  - **Bitmap register**：桶存比特向量/比特位，聚合通过**位模式**"
            "（最长 run、位占用率、最大前导零长度）读信息。信息密度高于单标量。"
            "HLL、PCSA、位占用估计器皆属此类。"
        ),
        (
            "**Axis 3 — 聚合算子（aggregation operator）**：如何合并同桶事件？\n"
            "  - **Idempotent max**（幂等最大化）：重复同一事件不改变状态；"
            "自然去重。**推论**：用 max 聚合的结构**只能回答 cardinality 类问题**"
            "（因为对 duplicate event 无响应）。HLL Flajolet instance 走这条。\n"
            "  - **Accumulative sum / set-bit**（累积/置位）：每条事件都影响状态；"
            "重复事件会增加计数或点亮位。用它才能回答 **frequency** 类问题。"
            "CMS、Morris、Space-Saving 走这条。"
        ),
        (
            "**关键洞察**：hash 来源 x 聚合算子 一起决定\"这个 sketch 回答什么问题\"："
        ),
        (
            "- flow-label hash + max = cardinality（HLL instance、PCSA）\n"
            "- flow-label hash + sum = frequency（CMS）\n"
            "- flow-label hash + MG-replace = heavy-hitter set（Space-Saving）\n"
            "- per-arrival Bernoulli + sum = robust frequency under heavy load"
            "（第 6 节）\n"
            "- flow-label hash + bitmap occupancy = cardinality + 可选 frequency"
            "（位占用估计器）"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("5. Primitives as Axis Combinations", [
        (
            "**5.1 Count-Min Sketch (CMS)** = flow-label hash + scalar counter + "
            "per-arrival sum。d 行独立哈希，w 列桶；update 对每行 ++；"
            "query 取 d 行 min（只过估不欠估，因为哈希碰撞只会叠加别人的计数）。"
        ),
        FormulaBlock(
            explanation="CMS 参数与加性误差保证（以概率 >= 1 - delta 成立）：",
            latex=(
                r"w = \lceil e / \varepsilon \rceil,\ "
                r"d = \lceil \ln(1/\delta) \rceil,\ "
                r"\Pr\bigl[\hat{f}(x) \le f(x) + \varepsilon \|F\|_1\bigr] \ge 1-\delta"
            ),
        ),
        (
            "**5.2 HLL Flajolet instance** = flow-label hash + bitmap register + "
            "idempotent max。前 p 位选 m=2^p 桶，剩余比特数前导零长度取 max。"
            "重复事件因 max 幂等而不重复贡献，所以**只能回 cardinality**。"
        ),
        FormulaBlock(
            explanation="HLL 基数估计（alpha_m 为偏差修正常数，m=16384 时 alpha≈0.7213）：",
            latex=(
                r"\hat{n} = \alpha_m \cdot m^2 \cdot "
                r"\left(\sum_{j=1}^{m} 2^{-R_j}\right)^{-1}"
            ),
        ),
        (
            "**5.3 Space-Saving (Metwally 2005)** = flow-label hash + K 个"
            "(key, count) 槽 + 替换最小槽规则。新 key 来且槽满：**踢出 min 槽，"
            "新 key 继承其 count 并 +1**。对被跟踪 key 给出确定性过估上界：\n"
            "f(x) <= f_hat(x) <= f(x) + N/K。Zipf 重尾下**实测常比 CMS 又准又省**"
            "（大 key 的噪声被小 key 的稀疏性稀释）。"
        ),
        (
            "**5.4 Morris counter** = flow-label hash + log counter + 随机加法"
            "`P(增) = b^(-stored)`。用 8 bit 存可估到 10^6 级；查询做 b^stored - 1。"
            "**用处**：内存极度受限时的频次近似；经常作为 CMS 每桶的替代降存储。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("6. Refinements: CMM, Bernoulli-Freq, Bitmap-Register General", [
        (
            "**6.1 Count-Mean-Min (CMM) > plain CMS for light flows**：CMS 的 row min "
            "在**轻流**（small f(x)，频次远小于平均 ||F||_1 / w）上相对误差爆炸："
            "min 里混了大量无关重流的碰撞。CMM 思路：**先减掉同桶的平均噪声期望**，"
            "再跨行取 median（不是 min）。"
        ),
        FormulaBlock(
            explanation="每行先做 unbiased 估计（减同桶噪声期望 (N-bucket)/(w-1)）：",
            latex=(
                r"\hat{f}_i(x) = \frac{w \cdot \text{table}[i][h_i(x)] - N}{w - 1}"
            ),
        ),
        (
            "再跨 d 行取 **median**（对外点稳健）。CMM 的相对误差在 light flow 上"
            "可比 CMS 低 10-100 倍；工程上常作为 CMS 的默认升级。**代价**：需要"
            "同时跟踪 N（总事件数），查询复杂度升到 O(d log d)（排序求中位数）。"
        ),
        (
            "**6.2 Bernoulli frequency sketch**（per-arrival 抽样 + 桶内累积）："
            "每条事件独立以概率 p 通过 Bernoulli 门，存活者进入一个大 bucket。"
            "查询 x 的估计频次 = bucket_count(x) / p。"
        ),
        FormulaBlock(
            explanation="Bernoulli frequency sketch 的标准差（v 为桶大小，p 为采样率）：",
            latex=r"\sigma(\hat{f}(x)) \approx \frac{\sqrt{f(x)}}{p}",
        ),
        (
            "**互补性**：CMS 误差是 eps·||F||_1（**加性**、由重流主导），"
            "Bernoulli-freq 误差是 sqrt(f(x))/p（**乘性、只依赖自身流量**）。"
            "重流下 Bernoulli 相对误差下降，CMS 相对误差上升；轻流下反之。"
            "生产系统常把两者**分层叠加**：Bernoulli 打重流、CMS 或 Space-Saving "
            "捕 heavy-hitter 名单（见第 10 节）。"
        ),
        (
            "**6.3 Bitmap-register generalization**（超越 HLL max）：若桶不是标量而是"
            "**bit vector**，可以读出比 max 更多的统计信息：\n"
            "  - 位占用率 (bit occupancy)：bucket 中被点亮的位占比 -> 既可估 cardinality"
            "也可估 frequency（位接近饱和时转为 log(1 / (1 - ratio)) 的无偏估计）。\n"
            "  - 最长连续 run / 前导零长度：即 HLL 的特例，max 聚合算子。\n"
            "  - **饱和处理**：bit vector 会被打满导致估计塌陷；用大 m（更多桶）"
            "+ 饱和感知估计器（见饱和位不计入分母）。\n"
            "  - 信息理论上，bitmap register 比单标量 counter 可用比特更多，"
            "相同空间下精度上限更高；代价是聚合算子比 max 复杂。"
            "\"走回 PCSA 路线\" 的说法指的就是这里。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("7. Unified \"Test Once\" View", [
        (
            "把 3 轴继续抽象，所有 sketch 都做**同一件事**：对哈希触发的事件"
            "\"测试一次\"，按语义决定响应方式。"
        ),
        (
            "- **Cardinality / distinct-count**：对每一个 **flow label** 触发一次"
            "测试——最大化聚合（max）保证同 label 的重复事件**不重复贡献**"
            "（idempotent）。回答\"见过多少种\"。\n"
            "- **Frequency / heavy-hitter**：对每一次 **arrival** 触发一次测试——"
            "累积聚合（sum / set-bit / MG-replace）让每次出现都**累加贡献**。"
            "回答\"每种出现多少次\"。"
        ),
        (
            "**含义**：底层结构（哈希 + 桶 + 寄存器）可以完全共享；**切换聚合触发"
            "时机**（per-label-once vs per-arrival）就切换问题类型。这解释了为什么"
            "生产系统往往一套桶阵列**同时服务 cardinality 和 frequency 两类查询**"
            "（HLL + CMS 共享桶、轮询 update 路径）。"
        ),
        (
            "**面试用途**：当面试官问\"能不能让一个 sketch 同时估 cardinality 和 "
            "frequency\"——标准答案就是沿着这一视角拆：共享桶、分叉聚合算子；"
            "具体实现有 HLL+CMS 共存、bitmap-register + 位占用双轨。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_comparison_table(
        headers=[
            "场景", "Hash 来源", "Counter/Register", "聚合算子", "推荐 primitive", "内存",
        ],
        rows=[
            ["distinct count 全局", "flow label", "bitmap register", "idempotent max",
             "HLL (Flajolet)", "O(m) ~ 12KB"],
            ["全局 frequency 近似", "flow label", "scalar counter", "per-arrival sum",
             "CMS (+ CMM 升级)", "O((1/eps) log(1/delta))"],
            ["heavy-hitter 确定性", "flow label", "K 个 (key, count) 槽", "MG-replace",
             "Space-Saving", "O(K)"],
            ["轻流 frequency 精准", "flow label", "scalar counter", "unbiased-mean + median",
             "CMM", "同 CMS"],
            ["重流稳健 frequency", "per-arrival Bernoulli", "scalar counter", "sum",
             "Bernoulli-freq sketch", "O(|bucket|/p)"],
            ["cardinality + frequency", "flow label", "bitmap register", "max + 位占用",
             "位占用估计器", "O(m) 但信息密度高"],
            ["滑动窗口 top-K", "flow label + time bucket", "counter + tumbling", "sum + 过期",
             "Exponential Histogram + SS", "O(K * log W)"],
            ["分布式无界流", "flow label (pre-shuffle)", "任选", "任选",
             "PPK + K-way merge", "单机 O(本地草图)"],
        ],
        title="Axis-Combination Cheat Sheet",
    )

    # ------------------------------------------------------------------
    b.add_section("8. Distributed Top-K: PPK + K-Way Merge", [
        (
            "**PPK (partition-by-key) 套路**：P 台机，事件按 hash(key(x)) mod P 发往"
            "对应机；每机本地维护 top-K（任选第 5 节 primitive）；最终 coordinator "
            "K-way merge。正确性关键：**同一 key 所有事件落同一机**，所以本机 top-K "
            "的 union 覆盖全局 top-K（K_local >= K 时）。"
        ),
        (
            "**错误套路（面试陷阱）**：按 round-robin 分发事件 -> 同一 key 被切到多机 "
            "-> 本地 top-K 是碎片 -> 直接 merge 把同 key 碎片当不同 key 算，错。必须 "
            "shuffle-by-key 重聚合（等价于 MapReduce word-count 的 reduce 阶段）。"
        ),
        (
            "**Key-skew 缓解**：salting（hot key 加 rand % s 后缀 + 两阶段）/ "
            "heavy-hitter fast path（Space-Saving 识别 hot 后独立路径）/ "
            "tree aggregation（多层 reducer 指数下降）/ skew-aware partitioner "
            "（Spark AQE）。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("9. System Design: Production Composition Pattern", [
        (
            "生产环境（Pinterest trending pins、网络流量 heavy-hitter、DDoS 检测）"
            "**从不只用单一 sketch**——都是**分层+双轴桶+epoch 重置**的组合。"
            "这是\"教材教 primitive、工程教 composition\"的核心分野。"
        ),
        (
            "**9.1 Layered architecture（冷过滤 + 主 sketch）**：\n"
            "  - **冷过滤层**（admission filter）：吃 Zipf 长尾的 one-hit-wonder。"
            "典型实现 = **1/8 采样 + k-position-full-pass**：以 1/8 概率让事件进入，"
            "或事件的 key hash 前 k 位全 0 才进入（相当于 2^k 采样但精准可重复）。"
            "长尾 key 因低采样率大概率被挡住，不污染主 sketch。\n"
            "  - **主 sketch 层**：只看通过冷过滤的\"可能重要\"流量，哈希碰撞压力"
            "从 ||F||_1 降到约 ||F||_1 / (2^k)，相当于用同等空间换 2^k 倍有效 eps。"
        ),
        (
            "**9.2 Two-layer bucketing**（双层正交桶）：\n"
            "  - **外层**：flow -> m 个 registers（3-轴里的 flow-label hash + m 桶）。"
            "作用：跨 flow 碰撞抑制。\n"
            "  - **内层**：per-arrival -> 单个 register 内的 bit 位置"
            "（3-轴里的 per-arrival hash + bitmap register）。"
            "作用：同一 flow 内的 arrival 分布到不同 bit，bit 占用率即频次代理。\n"
            "  - **好处**：两层正交 -> 两种噪声源（跨流碰撞 / 同流采样误差）可**独立调优**。"
            "常见比例：外层 m=4096，内层每寄存器 64 bit，总空间 32KB 级。"
        ),
        (
            "**9.3 Epoch reset + warm-up**（亚秒级重置 + 上代预热）：\n"
            "  - **Epoch**：每 N 秒（典型 100ms-5s）整体重置，防止陈旧重流压制新热点。\n"
            "  - **Warm-up**：新 epoch 启动时**上一代的 heavy-hitter list 预加载到"
            "冷过滤器的允许列表**，避免真冷启动的前 N 毫秒漏掉已知热点。\n"
            "  - **隐含假设**：heavy-hitter 有**时间局部性**（上一秒的热 key 下一秒仍热）——"
            "对网络流量、搜索 trending、feed 曝光都成立；对离散突发事件（新闻快讯）"
            "不成立，需要更短 epoch 或跳过 warm-up。"
        ),
        (
            "**9.4 把 3 轴落到代码**：具体系统选型 = \n"
            "  冷过滤 = flow-label hash + Bloom filter（counter=单 bit，operator=OR）；\n"
            "  主层 = CMS 或 Space-Saving（第 5 节 primitive）；\n"
            "  top-K 输出 = size-K 最小堆（按 CMS/SS 估计频次排）；\n"
            "  跨机汇聚 = PPK + K-way merge。"
            "**每一层都是一个 3-轴组合**，合起来是\"组合图\"。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("10. Common Pitfalls", [
        (
            "- **用 HLL 做 top-K**：Flajolet instance 的 max 聚合幂等，不保留 per-key 计数。**错**。\n"
            "- **跨社区混用 HLL 术语**：DB 社区的 HLL = 实例；SIGCOMM 的 HLL = 家族。"
            "首次使用必须标明，否则答案听起来不严谨。\n"
            "- **round-robin 分片后本地 top-K 合并**：同 key 被切，结果错。必须 PPK。\n"
            "- **CMS 查稀有项**：轻流被 ||F||_1 噪声淹没；**改用 CMM** 或走 Bernoulli-freq 路径。\n"
            "- **滑动窗口套全局 top-K 算法**：需要 expiry 机制（tumbling / decay counter / exp histogram）。\n"
            "- **低估 CMS 内存常数**：w = e / eps 在 eps=1e-6 时就是 2.7M 桶 * d 行 * 4B = 百 MB 级；"
            "重尾下 Space-Saving 往往更省。\n"
            "- **忘记饱和**：bitmap register 打满后估计塌陷；用大 m + 饱和感知估计器。\n"
            "- **把 primitive 当完整方案**：生产级 heavy-hitter 必须叠\"冷过滤 + 主 sketch + "
            "epoch 重置\"三件套；单给一个 CMS 的答案是本科级。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_interview_qa(
        "面试官问：1MB 内存、1e9 事件流、估 top-100 视频，怎么做？",
        (
            "**先澄清**：精确还是近似？分布先验？若允许 (eps=1e-4, delta=1e-3)："
            "用 **CMS** (w=e/eps≈2.7e4, d=ln(1/delta)=7，约 750KB) + size-100 最小堆。"
            "若分布重尾，直接 **Space-Saving O(K)** 几 KB 即可给出确定性上界。"
            "**若轻流相对误差也要精准**，用 **CMM**（同 CMS 空间，误差更低）。"
            "**关键坑**：HLL 不能用——它是 cardinality 估计器（max 聚合幂等），不保留 per-key 计数。"
            "**加分**：说明生产系统会叠 \"1/8 冷过滤 + 主 sketch + 1s epoch 重置 + 上代 warm-up\"。"
        ),
    )
    b.add_interview_qa(
        "CMS 和 Space-Saving 都过估不欠估，差别在哪？什么时候选哪个？",
        (
            "**3-轴拆解**：CMS = 流标签哈希 + d 行 w 列标量计数 + 每到达 sum；"
            "Space-Saving = 流标签哈希 + K 槽 + MG-replace。"
            "**CMS** 空间 O((1/eps) log(1/delta))，加性误差 eps·N 概率保证，对任意分布成立；"
            "**Space-Saving** 空间 O(K)，确定性 N/K 上界，重尾下实测更紧（大 key 噪声被小 key 稀疏性稀释）。"
            "工程判据：只要 top-K 本身 + 重尾分布 -> Space-Saving；要对任意 key 查频次 -> CMS。"
            "**轻流相对误差爆炸**是 CMS 的弱点（CMM 可救，median + 噪声期望修正）。"
        ),
    )
    b.add_interview_qa(
        "为什么 HLL 能做 cardinality 但做不了 frequency？三轴视角解释。",
        (
            "**Axis 3 决定**：HLL Flajolet instance 的聚合算子是 **idempotent max**——"
            "同 flow 重复事件不改变状态（max 幂等），所以回答的是\"这个 flow 出现过吗\""
            "的 yes/no 累积，也就是\"见过多少种 flow\" (cardinality)。"
            "frequency 需要的聚合算子是 **accumulative sum/set-bit**——重复事件必须累加。"
            "**解法**：若想一个结构同时解 cardinality 和 frequency，保留 flow-label hash + "
            "bitmap register（Axis 1/2 不变），分叉 Axis 3：max 路径给 cardinality，位占用率路径给 frequency。"
            "这是位占用估计器和 PCSA 家族的核心。"
        ),
    )
    b.add_interview_qa(
        "生产级 heavy-hitter 系统为什么要冷过滤 + 两层桶 + epoch 重置？",
        (
            "**冷过滤**：Zipf 长尾里 80% 流量来自 0.1% 的 key；剩下的 20% 是几千万个 one-hit-wonder。"
            "让所有事件都进主 sketch，哈希碰撞压力由 ||F||_1 驱动，eps 预算被长尾消耗掉。"
            "1/8 采样 + k-position-full-pass 把长尾挡在门外，主 sketch 只看\"有潜力的\"流量——"
            "相当于用同等空间换 2^k 倍有效 eps。"
            "**两层桶**（外层跨流 + 内层 per-arrival bit）把\"跨流碰撞\"和\"同流采样误差\""
            "拆成两个可独立调优的噪声源，比单层更省空间。"
            "**Epoch 重置 + 上代 warm-up**：防陈旧重流压制新热点（非平稳流必需）；warm-up 解决"
            "冷启动前 N ms 漏热点问题，依赖 heavy-hitter 时间局部性假设。"
        ),
    )

    # ------------------------------------------------------------------
    b.add_checklist("Self-Check (面试前必过)", [
        "能口述 3 轴：hash 来源 / counter 结构 / 聚合算子，并举 4 个 primitive 的 3 轴坐标",
        "能在首次提 HLL 时主动区分 family vs Flajolet instance",
        "能默写 CMS 的 w=e/eps, d=ln(1/delta) 及加性误差 eps·||F||_1 (1-delta)",
        "能解释 CMM 如何用减噪期望 + median 改进 CMS 轻流误差",
        "能推导为什么 idempotent max => 只解 cardinality，accumulative sum => 解 frequency",
        "能解释 bitmap register 比 scalar counter 的信息密度优势及饱和处理",
        "能画出生产 heavy-hitter pipeline：冷过滤 + 主 sketch + top-K heap + epoch 重置",
        "能解释 PPK 为何对、round-robin 为何错；能举 3 种 skew 缓解",
        "能把 Bernoulli-freq 的 sqrt(f)/p 和 CMS 的 eps·N 说清楚为何互补",
        "能用 3-轴视角回答\"一个 sketch 同时解 cardinality + frequency 怎么做\"",
    ])

    # ------------------------------------------------------------------
    b.add_section("11. Canonical Closing", [
        (
            "**Textbook teaches primitives; production teaches composition.** "
            "3-轴透镜（hash 来源 / counter 结构 / 聚合算子）+ 分层系统设计"
            "（冷过滤 / 双轴桶 / epoch 重置）是把教材 sketch 翻译成工程方案的核心 frame。"
            "面试回答顺序：**先 3 轴 clarify 问题 -> 选 primitive 组合 -> 叠生产分层 -> 给代价估算**。"
        ),
    ])

    return b.build()


# ==========================================================================
# Node 197: surgical compaction of CMS/HLL references
# ==========================================================================

NODE_197_OLD_KEY_TERMS = (
    "- **CMS** (Count-Min Sketch): 概率频次草图，参考 streaming_topk 节点\n"
    "- **HLL** (HyperLogLog): 概率基数估计，O(log log N) 位估 distinct count"
)
NODE_197_NEW_KEY_TERMS = (
    "- **CMS** (Count-Min Sketch): 概率频次草图（canonical 3-轴定义、误差公式、"
    "生产分层均见 `pillar1.streaming_topk`，本节不重复）\n"
    "- **HLL** (HyperLogLog): 双重身份——DB/工程社区的 Flajolet 2007 cardinality 估计器实例 / "
    "network-measurement 社区的家族名（canonical 见 `pillar1.streaming_topk`）"
)

NODE_197_OLD_SKETCH_BULLET = (
    "- **概率草图**：`CMS` 做频次，`HLL` 做基数，`Bloom filter` 做存在性，  "
    "全部 O(1)/O(log log N) 内存但带 (epsilon, delta) 误差。"
)
NODE_197_NEW_SKETCH_BULLET = (
    "- **概率草图**：`CMS` 做频次，`HLL` 做基数，`Bloom filter` 做存在性——"
    "canonical 3-轴分析与组合模式见 `pillar1.streaming_topk`；"
    "此处仅按内存量级召回 (O(1)/O(log log N)，(epsilon, delta) 误差)。"
)


def patch_node_197_description(description: str) -> tuple[str, bool]:
    """Apply surgical replacements to node 197's description.

    Returns (new_description, changed_flag).
    """
    changed = False
    new_desc = description
    if NODE_197_OLD_KEY_TERMS in new_desc:
        new_desc = new_desc.replace(NODE_197_OLD_KEY_TERMS, NODE_197_NEW_KEY_TERMS)
        changed = True
    if NODE_197_OLD_SKETCH_BULLET in new_desc:
        new_desc = new_desc.replace(
            NODE_197_OLD_SKETCH_BULLET, NODE_197_NEW_SKETCH_BULLET
        )
        changed = True
    return new_desc, changed


# ==========================================================================
# Node 103: surgical compaction of CMS/HLL references
# ==========================================================================

NODE_103_OLD_TABLE_ROW = (
    "| **High Cardinality Keys\uff08\u9ad8\u57fa\u6570\u952e\uff09** | "
    "\u8fd1\u4f3c\u6570\u636e\u7ed3\u6784\uff1a"
    "**HyperLogLog (HLL\uff0c\u8d85\u5bf9\u6570\u8ba1\u6570)** \u7528\u4e8e"
    "\u552f\u4e00\u8ba1\u6570, **Count-Min Sketch (CMS\uff0c\u8ba1\u6570\u6700\u5c0f\u8349\u56fe)**"
    " \u7528\u4e8e\u9891\u7387\u4f30\u8ba1 |"
)
NODE_103_NEW_TABLE_ROW = (
    "| **High Cardinality Keys（高基数键）** | "
    "近似数据结构（canonical 细节见 `pillar1.streaming_topk`）："
    "**HLL** 做唯一计数（cardinality）、**CMS** 做频次、**Space-Saving** 做 heavy-hitter |"
)

NODE_103_OLD_PARA = (
    "**HyperLogLog** 用 $O(\\log \\log n)$ 空间估计唯一元素数量，误差约 2%。"
    "**Count-Min Sketch** 用固定空间估计元素频率，仅会高估不会低估。"
)
NODE_103_NEW_PARA = (
    "**HyperLogLog (HLL)** 估计唯一元素数量 (cardinality)，"
    "**Count-Min Sketch (CMS)** 估计元素频率（只过估不欠估）。"
    "两者的 3-轴定位（hash 来源 / 寄存器结构 / 聚合算子）、误差公式、"
    "HLL family-vs-Flajolet-instance 术语消歧、"
    "以及生产分层组合（冷过滤 + 主 sketch + epoch 重置）"
    "统一放在 `pillar1.streaming_topk` canonical 节点，此处不重复。"
)


def patch_node_103_description(description: str) -> tuple[str, bool]:
    """Apply surgical replacements to node 103's description."""
    changed = False
    new_desc = description
    if NODE_103_OLD_TABLE_ROW in new_desc:
        new_desc = new_desc.replace(NODE_103_OLD_TABLE_ROW, NODE_103_NEW_TABLE_ROW)
        changed = True
    if NODE_103_OLD_PARA in new_desc:
        new_desc = new_desc.replace(NODE_103_OLD_PARA, NODE_103_NEW_PARA)
        changed = True
    return new_desc, changed


# ==========================================================================
# Doc 58: Pinterest-specific composition 1-pager atop canonical node 196
# ==========================================================================

def build_doc_58_content() -> str:
    b = StudyNoteBuilder()
    b.set_title("Pinterest Sketch/Streaming Composition 1-Pager (Atop Canonical)")

    b.add_prerequisites([
        "canonical 3-轴框架：`pillar1.streaming_topk`（必读；primitive 数学推导"
        "与 HLL family/instance 消歧全在那里，本文档不重复）",
        "Pinterest 系统语境：trending pins、广告 abuse detection、"
        "unique-user cardinality、feed 曝光流量的时间局部性",
    ])

    b.add_term(
        "Composition",
        "Axis-Combination Atop Primitives",
        "本 1-pager 的定位：选哪些 3-轴组合解 Pinterest 具体问题，而非重述 primitive 本身",
    )

    # ------------------------------------------------------------------
    b.add_section("1. How to Use This Doc", [
        (
            "本文档**不**教 **CMS** / **HLL** / Space-Saving 的数学——"
            "那些 canonical 内容（w/d 公式、误差界、HLL 谐波均值、"
            "bitmap register 位占用、Bernoulli-freq 相对误差、CMM 中位数修正、"
            "冷过滤 + 两层桶 + epoch 重置的生产组合）**全部**统一放在 "
            "`pillar1.streaming_topk` 规范节点。"
        ),
        (
            "这里只回答一件事：**Pinterest 的几个典型场景应选哪些 3-轴组合**，"
            "以及 trade-off 的语境。面试时先把 canonical 3-轴拉出来 clarify，"
            "再套到下面每个场景的具体 composition。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("2. Scenario A: Trending Pins (Heavy-Hitter @ Scale)", [
        (
            "**问题**：每秒千万级 pin 曝光/点击，实时输出 top-100 trending pins；"
            "重尾分布（Zipf，头部 0.1% pin 吃 80% 流量）；滑动窗口语义（5 min 或 1 h）。"
        ),
        (
            "**推荐 composition**（细节 primitive 见 canonical）：\n"
            "  - **冷过滤层**：flow-label hash + Bloom filter (OR 聚合)，挡 long-tail one-hit pin；\n"
            "  - **主频次层**：**CMS**（或 **CMM** 升级版，若 mid-tier pin 的相对误差被诟病）"
            "+ size-100 最小堆缓存当前 top-K 候选；\n"
            "  - **heavy-hitter 精度补**：**Space-Saving** O(K=~1000) 并行跑，"
            "对超重 pin 给确定性上界（CMS 估计的上界验证）；\n"
            "  - **时间衰减**：epoch 1s 重置 + 上代 heavy-hitter list warm-up 冷过滤。"
            "依赖 trending pin 的**时间局部性**（上一秒热门下一秒仍热）。"
        ),
        (
            "**分布式**：按 `hash(pin_id)` PPK 分片（**不是** round-robin——同 pin 必须落同机，"
            "否则本地计数是碎片）；各分片本地跑上述组合，coordinator K-way merge 合 top-K。"
            "Skew 缓解用 salting（hot pin 加 rand % 16 后缀，两阶段聚合）。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("3. Scenario B: Unique Users Per Campaign (Cardinality)", [
        (
            "**问题**：广告 campaign 报表\"有多少 unique user 看过\"，数十亿次曝光、"
            "百万级 user_id 维度；离线 `COUNT(DISTINCT)` 太慢且内存炸。"
        ),
        (
            "**推荐 composition**：**HLL 的 Flajolet 2007 instance**（flow-label hash + "
            "bitmap register + idempotent max，m=2^14=16384 个桶约 12KB 内存、~1% 相对误差）；"
            "每 campaign 一份 HLL，可 merge 跨分片、跨时间窗（**mergeable** 是 HLL 的关键优势）。"
        ),
        (
            "**术语注意**：对内部工程会议说 HLL 默认理解为 Flajolet instance；"
            "但若涉及网络测量/SIGCOMM 语境（DDoS 检测、flow counting）"
            "务必**区分 HLL family vs instance**——instance 只解 cardinality（max 幂等）。"
            "想在同一桶阵列里加 frequency 维度，得换 bitmap register 位占用估计器（见 canonical 6.3）。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("4. Scenario C: Abuse Detection (Combined Cardinality + Frequency)", [
        (
            "**问题**：检测\"某 user/IP 在 1 min 内对多少不同 pin 做过 action\"（distinct count）"
            "**同时**需要\"总 action 数\"（frequency）。单一 primitive 不够。"
        ),
        (
            "**推荐 composition**：双路并行桶阵列，**共享 flow-label hash + bitmap register**"
            "（canonical 7. Test-Once 视角）——\n"
            "  - Axis 3 分叉 A：**idempotent max** 路径 -> cardinality（unique pin 数）；\n"
            "  - Axis 3 分叉 B：**位占用累积** 路径 -> frequency 代理（total actions）。\n"
            "同一桶数组 two-layer bucketing，用上代 heavy-hitter warm-up 防 cold-start 误报。"
        ),
        (
            "**替代方案（若桶共享难实现）**：HLL + CMS 独立跑两份，内存翻倍但实现直接。"
            "Pinterest 工程实践倾向后者（简单、可调试、成本不敏感），"
            "面试答前者加分（体现 3-轴视角）。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("5. Scenario D: Offline A/B Event Sampling (Reservoir)", [
        (
            "**问题**：广告曝光的离线分析抽样——海量事件流上维护公平 user-ad "
            "interaction 样本，**事先不知道总流量**。"
        ),
        (
            "**推荐 primitive**：**Reservoir sampling (Vitter's R)**，canonical 里的"
            "非-sketch 对照组——`O(k)` 空间，每元素 `O(1)` 摊还，"
            "每条事件出现在最终样本中的概率 = k/N。加权变体（曝光权重）"
            "用 `key = random^(1/weight)` + 保留 top-k key。"
        ),
        (
            "**与 sketch 的关系**：reservoir 不保证抽到 heavy-hitter，而是**均匀代表**。"
            "Pinterest 广告团队常 reservoir + Space-Saving 并行——前者做代表性样本，"
            "后者做热点名单，两种信息互补。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("6. Interview Bridge: How to Answer", [
        (
            "**推荐模板**（3 分钟内讲完）："
        ),
        (
            "1. **Clarify** Pinterest 场景的 3 轴 signal：要 cardinality / frequency / heavy-hitter？"
            "重尾还是均匀？实时还是离线？滑窗还是全局？\n"
            "2. **Pick primitive 组合**（上面 Scenario A-D 对号入座，canonical 里的 3-轴定位）；\n"
            "3. **加生产分层**：冷过滤 + 主 sketch + top-K heap + epoch 重置 + 上代 warm-up；\n"
            "4. **分布式**：PPK + K-way merge；hot pin 用 salting 或 heavy-hitter fast path；\n"
            "5. **Cost 估算**：给 RAM 数量级（CMS 1MB / HLL 12KB / Space-Saving 几 KB）。"
        ),
        (
            "**面试信号**：追问\"精确 top-K\" -> Space-Saving 确定性 O(K)（但难跨机 merge，"
            "要显式说）；追问\"突发流量\" -> 滑动窗口 CMS + decay；"
            "追问\"精度评估\" -> 子集跑 ground truth + precision@K / recall@K。"
            "主动说\"HLL family vs Flajolet instance\"区分 = 加分信号。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_checklist("Pinterest-Specific Self-Check", [
        "能 3 秒把 trending pin / unique-user / abuse 三场景映射到具体 3-轴组合",
        "能在 trending pin 方案里显式提 cold filter + epoch + warm-up 三件套",
        "能区分 PPK 和 round-robin 的分布式 top-K，能给 salting 的两阶段流程",
        "能主动说 HLL 的 family-vs-instance 术语消歧（面试加分）",
        "能从 3-轴分叉角度解释 cardinality + frequency 共桶方案（Scenario C）",
        "能把 reservoir sampling 和 heavy-hitter sketch 的用途分开（不混用）",
    ])

    return b.build()


# ==========================================================================
# DB upsert helpers
# ==========================================================================

def upsert_framework_node_description(
    conn: sqlite3.Connection, path: str, title: str, content: str
) -> tuple[int, str, int]:
    """Upsert description (full rewrite) for an existing framework_node by path.

    Returns (node_id, action, new_length).
    """
    row = conn.execute(
        "SELECT id FROM framework_nodes WHERE path = ?", (path,)
    ).fetchone()
    if not row:
        print(f"[FAIL] framework_node path={path} not found")
        sys.exit(1)
    node_id = row[0]
    conn.execute(
        "UPDATE framework_nodes SET description = ?, title = ? WHERE id = ?",
        (content, title, node_id),
    )
    new_len = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()[0]
    return node_id, "UPDATED", new_len


def patch_framework_node(
    conn: sqlite3.Connection,
    path: str,
    patcher,  # callable: description -> (new_desc, changed)
) -> tuple[int, str, int]:
    """Apply surgical patch to an existing framework_node's description."""
    row = conn.execute(
        "SELECT id, description FROM framework_nodes WHERE path = ?", (path,)
    ).fetchone()
    if not row:
        print(f"[FAIL] framework_node path={path} not found")
        sys.exit(1)
    node_id, desc = row
    new_desc, changed = patcher(desc)
    if not changed:
        new_len = len(desc or "")
        return node_id, "UNCHANGED", new_len
    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?",
        (new_desc, node_id),
    )
    new_len = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()[0]
    return node_id, "PATCHED", new_len


def upsert_company_document_by_id(
    conn: sqlite3.Connection, doc_id: int, title: str, content: str
) -> tuple[int, str, int]:
    """Upsert content (full rewrite) for an existing company_document by id."""
    row = conn.execute(
        "SELECT id FROM company_documents WHERE id = ?", (doc_id,)
    ).fetchone()
    if not row:
        print(f"[FAIL] company_document id={doc_id} not found")
        sys.exit(1)
    conn.execute(
        "UPDATE company_documents SET content = ?, title = ? WHERE id = ?",
        (content, title, doc_id),
    )
    new_len = conn.execute(
        "SELECT length(content) FROM company_documents WHERE id = ?", (doc_id,)
    ).fetchone()[0]
    return doc_id, "UPDATED", new_len


# ==========================================================================
# Main
# ==========================================================================

def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    # Build content & validate before touching DB
    node_196_content = build_node_196_content()
    doc_58_content = build_doc_58_content()

    for tag, content in (("node_196", node_196_content), ("doc_58", doc_58_content)):
        warns = StudyNoteBuilder.validate(content)
        for w in warns:
            print(f"[WARN {tag}] {w}")
        length = len(content)
        print(f"[BUILT] {tag} length={length} chars")

    if not (10000 <= len(node_196_content) <= 14000):
        print(
            f"[WARN] node_196 length={len(node_196_content)} outside target "
            "[10000, 14000]"
        )
    if not (4000 <= len(doc_58_content) <= 6000):
        print(
            f"[WARN] doc_58 length={len(doc_58_content)} outside target "
            "[4000, 6000]"
        )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        nid, action, nlen = upsert_framework_node_description(
            conn, NODE_196_PATH, NODE_196_TITLE, node_196_content
        )
        print(f"[{action}] framework_node id={nid} path={NODE_196_PATH} length={nlen}")

        nid, action, nlen = patch_framework_node(
            conn, NODE_197_PATH, patch_node_197_description
        )
        print(f"[{action}] framework_node id={nid} path={NODE_197_PATH} length={nlen}")

        nid, action, nlen = patch_framework_node(
            conn, NODE_103_PATH, patch_node_103_description
        )
        print(f"[{action}] framework_node id={nid} path={NODE_103_PATH} length={nlen}")

        did, action, dlen = upsert_company_document_by_id(
            conn, DOC_58_ID, DOC_58_TITLE, doc_58_content
        )
        print(f"[{action}] company_document id={did} title='{DOC_58_TITLE}' length={dlen}")

        conn.commit()
    finally:
        conn.close()

    print("[DONE] sketch family consolidation complete")


if __name__ == "__main__":
    main()
