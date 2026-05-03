"""Rewrite Pinterest Sketch/Streaming 1-pager (doc 58) with Chinese prose.

Per user preference (2026-04-15): prose should be Chinese by default; code,
algorithm names (Count-Min Sketch / CMS / HyperLogLog / etc), complexity
notation, and LaTeX stay English.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

COMPANY_ID = 29
DOC_TITLE = "Pinterest Sketch/Streaming Theory 1-Pager"


def build_note() -> StudyNoteBuilder:
    b = StudyNoteBuilder()

    b.set_title("Sketch & Streaming Algorithms -- Pinterest 备考")

    b.add_prerequisites([
        "哈希函数与碰撞分析",
        "基于堆的 top-K（LC 703 / 973 / 378）",
        "概率基础（期望、方差、Markov / Chebyshev 不等式）",
    ])

    b.add_term("CMS", "Count-Min Sketch",
               "多哈希函数的亚线性频次估计结构")
    b.add_term("HLL", "HyperLogLog",
               "基于前导零统计的基数（distinct count）估计")
    b.add_term("SS", "Space-Saving (Misra-Gries 变体)",
               "用 O(1/e) 个计数器做确定性重击者检测")

    b.add_section("1. Count-Min Sketch (CMS)", [
        "**是什么**：在流式数据上做点查频次估计的概率数据结构。",
        "**结构**：`d` 个独立哈希函数，每个哈希映射到一行 `w` 个计数器（整体是 `d x w` 的矩阵）。"
        "`update(item, count)` 对每一行 `i` 执行 `table[i][h_i(item)] += count`。",
        "**查询**：取所有 `d` 行中的最小值：",
        FormulaBlock(
            latex=r"\hat{f}(x) = \min_{i=1}^{d} \; \text{table}[i][h_i(x)]",
            explanation="频次估计（只会高估，不会低估）：",
        ),
        "**误差界**：取 `w = ceil(e/epsilon)`、`d = ceil(ln(1/delta))` 时：",
        FormulaBlock(
            latex=r"\hat{f}(x) \leq f(x) + \varepsilon \|a\|_1 \quad "
                  r"\text{with probability} \geq 1-\delta",
        ),
        "**为什么只会高估**：哈希碰撞只会把别人的计数加到自己头上，不会减去。"
        "跨 `d` 行取 min 就是为了把碰撞的影响压到最小。",
        "**典型用法**：实时流的 top-K 重击者检测。Pinterest trending pins 场景下——"
        "CMS 追踪 pin 曝光频次，配合一个大小为 K 的 min-heap 维护当前 top-K；"
        "每来一条事件就更新 CMS，若估计值 > heap 的最小值就替换。",
        "**空间**：`O(w * d) = O((1/epsilon) * ln(1/delta))`——关于流长度是亚线性的。",
    ])

    b.add_section("2. Space-Saving / Misra-Gries", [
        "**是什么**：在最多 `k-1` 个计数器下确定性地找出所有频次 > `n/k` 的元素。"
        "Space-Saving（Metwally 2005）是对 Misra-Gries 替换策略的改良。",
        "**Misra-Gries 算法**：\n"
        "1. 维护最多 `k-1` 个 `(item, count)` 对。\n"
        "2. 新元素到来时：若已被追踪，count += 1；否则若还有空槽，加入 (item, 1)；"
        "否则将**所有**计数器同时 -1，为 0 的清除。",
        "**Space-Saving 的改动**：不再「全体 -1」，而是驱逐当前 count 最小的元素，"
        "用新元素顶替，并把新 count 置为「被驱逐 count + 1」。这样给出的频次估计比 Misra-Gries 更紧。",
        "**保证**：任何真实频次 > `n/k` 的元素一定会出现在最终集合里。"
        "可能有 false positive（多带一些「凑数的」），但重击者不会漏（no false negatives）。",
        "**空间**：`O(1/epsilon)` 个计数器——同样误差下比 CMS 省空间，因为省掉了 `d` 行冗余。",
        "**CMS vs Space-Saving**：\n"
        "- CMS：实现简单，可并行（合并 = 元素级相加），但空间更大。\n"
        "- Space-Saving：估计更紧、空间更省，但跨分片合并比较麻烦。",
    ])

    b.add_section("3. Reservoir Sampling (LC 382 / 398)", [
        "**是什么**：在未知长度 `N` 的流上，用 `O(k)` 内存均匀随机采样 `k` 个元素。",
        "**Vitter's R 算法**：\n"
        "1. 先用流的前 `k` 个元素填满 reservoir。\n"
        "2. 对第 `i` 个元素（`i > k`）：生成 `j = random(1, i)`；若 `j <= k`，"
        "用新元素替换 `reservoir[j]`。",
        "**证明直觉**：归纳可证每个元素最终留在 reservoir 中的概率都恰为 `k/N`。",
        "**加权变体（LC 528 / Algorithm A-ES）**：用 `key = random^(1/weight)`，保留 top-k key。"
        "权重越大的元素存活概率指数级更高。",
        "**Pinterest 场景**：广告曝光的离线分析抽样——在事先不知道总量的海量事件流上，"
        "维护一个公平的用户-广告交互样本。",
        "**复杂度**：`O(k)` 空间，每元素 `O(1)`（摊还）。",
    ])

    b.add_section("4. HyperLogLog (HLL)", [
        "**是什么**：用 `O(m) = O(1/epsilon^2)` 个寄存器估计流中不同元素的个数（cardinality）。",
        "**机制**：\n"
        "1. 把每个元素哈希成均匀的比特串。\n"
        "2. 用前 `p` 位选出 `m = 2^p` 个寄存器中的一个。\n"
        "3. 统计剩余比特串的前导零个数，每个寄存器只保留当前见过的最大值。",
        FormulaBlock(
            latex=r"\hat{n} = \alpha_m \cdot m^2 \cdot \left(\sum_{j=1}^{m} 2^{-M[j]}\right)^{-1}",
            explanation="寄存器间的调和平均估计：",
        ),
        "**精度**：标准误 ~ `1.04 / sqrt(m)`。取 `2^14 = 16384` 个寄存器（约 12 KB）时，"
        "相对误差约 0.81%。",
        "**不属于 top-K 但常被一起考**：考察流式算法的面试官常把 HLL 和 CMS 放一起问。"
        "关键区别：HLL 估计 cardinality（有多少种？），CMS 估计 frequency（每种出现多少次？）。",
        "**Pinterest 场景**：统计看过某个 campaign 的唯一用户数——"
        "在数十亿事件上跑 exact `COUNT(DISTINCT user_id)` 代价很高；HLL 用 12 KB 就能做到 ~1% 误差。",
    ])

    b.add_comparison_table(
        headers=["Algorithm", "Answers", "Space", "Mergeable?", "Error Type"],
        rows=[
            ["CMS", "Point frequency", "O(1/e * ln(1/d))", "Yes (add)", "Overestimate"],
            ["Space-Saving", "Heavy hitters (freq > n/k)", "O(1/e)", "Hard", "Over+Under"],
            ["Reservoir", "Uniform sample of k", "O(k)", "No", "Sampling variance"],
            ["HLL", "Distinct count", "O(1/e^2)", "Yes (max)", "Relative ~1%"],
        ],
        title="Streaming Algorithms Comparison",
    )

    b.add_section("Interview Bridge: Pinterest 实时 Top-K Trending Pins", [
        "**题面**：\"How would you find trending pins in real time at Pinterest scale?\"",
        "**回答骨架**：\n"
        "1. 朴素：全局大小为 K 的 min-heap 追踪精确计数——不 scale，"
        "因为精确维护每个 pin 的计数需要 `O(N)` 空间（`N` 是 pin 词表大小）。\n"
        "2. 更好：**CMS + min-heap**。CMS 在亚线性空间下估计频次；"
        "大小为 K 的 min-heap 按估计频次维护当前 top-K。"
        "每来一条事件，更新 CMS，把估计值与堆顶最小值比较，更大就替换。\n"
        "3. 分布式：按 `hash(pin_id)` 分片，每个分片本地跑 CMS + heap，"
        "周期性合并各分片的 top-K 列表（CMS 是元素级可加的，天然可合并）。\n"
        "4. 衰减：对计数应用指数时间衰减（每个窗口 tick 把所有计数器乘以衰减因子），"
        "捕捉「近期热度」而非「历史累计」。",
        "**追问钩子**：\n"
        "- \"需要精确 top-K 怎么办？\"——Space-Saving 对重击者有确定性保证，但难分布式。\n"
        "- \"怎么处理突发流量？\"——滑动窗口 CMS 或衰减计数。\n"
        "- \"怎么评估精度？\"——在子集上跑 ground truth，用 precision@K / recall@K "
        "对比近似 top-K 和精确 top-K。",
    ])

    return b


def main() -> None:
    builder = build_note()
    content = builder.build()

    doc_path = Path(__file__).resolve().parent.parent / "docs" / "pinterest_sketch_streaming_1pager.md"
    doc_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {doc_path.name} ({len(content)} chars)")

    db_path = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cur = conn.execute(
        "UPDATE company_documents SET content = ? WHERE company_id = ? AND title = ?",
        (content, COMPANY_ID, DOC_TITLE),
    )
    conn.commit()
    print(f"[UPDATE] company_documents rows={cur.rowcount} new_len={len(content)}")
    conn.close()


if __name__ == "__main__":
    main()
