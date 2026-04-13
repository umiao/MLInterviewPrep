"""Seed framework node: pillar7 -> Probability & Statistics -> A/B Test Sample Size.

Creates (or updates) the leaf node `pillar7.probability_statistics.ab_test_sample_size`
and populates its `description` via StudyNoteBuilder.

Usage:
    python scripts/seed_ab_test_sample_size.py

Idempotent: re-running updates the existing node's description in place.
Per CLAUDE.md: StudyNoteBuilder is the source of truth; no raw f-string content.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"
NODE_PATH = "pillar7.probability_statistics.ab_test_sample_size"
NODE_TITLE = "A/B Test Sample Size"
PARENT_PATH = "pillar7.probability_statistics"


def build_content() -> str:
    b = StudyNoteBuilder()
    b.set_title("A/B Test Sample Size Analysis")

    b.add_prerequisites([
        "基础概率与分布：伯努利、正态、二项",
        "假设检验：z-test、t-test、显著性水平 alpha、功效 1-beta",
        "中心极限定理（CLT）与标准误差（SE）的推导",
        "参数估计基础：点估计、置信区间",
    ])

    b.add_term("MDE", "Minimum Detectable Effect",
               "最小可检出效应，实验设计阶段愿意以给定功效检出的最小真实差异")
    b.add_term("SRM", "Sample Ratio Mismatch",
               "实际分流比例与预期显著不一致，常暗示埋点、分流或过滤逻辑存在缺陷")
    b.add_term("CUPED", "Controlled-experiment Using Pre-Experiment Data",
               "利用实验前协变量回归降低指标方差，等价减少所需样本量")
    b.add_term("mSPRT", "mixture Sequential Probability Ratio Test",
               "始终有效（always-valid）的序贯检验，允许反复偷看而不破坏 Type I 误差控制")
    b.add_term("BH", "Benjamini-Hochberg",
               "控制错误发现率（FDR）的多重检验校正方法，比 Bonferroni 更有功效")

    # ------------------------------------------------------------------
    b.add_section("1. Overview and Why Sample-Size Matters", [
        (
            "样本量（sample size）是实验设计的核心参数，它直接决定了实验能以多大的概率检出真实效应。"
            "样本量不足会导致实验**欠功效（underpowered）**，真正有效的改动被误判为无效；"
            "样本量过大则浪费流量并推迟决策，在用户增长受限的产品中机会成本极高。"
            "正确的做法：在实验启动**之前**基于基线率 p1、MDE、alpha、power 计算出所需的每组样本量 n，"
            "并据此估计实验周期（n 除以每日可用流量），再与产品节奏和业务窗口对齐。"
        ),
        (
            "A/B 测试中最常见的两种场景："
        ),
        (
            "1. **比例型指标（proportion metric）**：转化率、点击率、留存率——服从伯努利分布，使用 two-proportion z-test。"
        ),
        (
            "2. **连续型指标（continuous metric）**：人均 GMV、停留时长、session per user——近似正态，使用双样本 t-test / Welch's t-test。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("2. Derivation: Two-Proportion z-test Sample Size", [
        (
            "设 control 组和 treatment 组的真实转化率分别为 p1、p2，两组样本量均为 n。"
            "在原假设 H0: p1 = p2 下，样本差 hat_p2 - hat_p1 近似服从均值 0、方差 "
            "`2 p_bar (1 - p_bar) / n` 的正态分布；"
            "在备择假设 H1: p2 - p1 = delta 下，均值为 delta、方差为 `p1(1-p1)/n + p2(1-p2)/n`。"
            "同时要求 Type I 误差 alpha（双侧则用 z_{alpha/2}）与 Type II 误差 beta（功效 1 - beta，单侧 z_{beta}）。"
        ),
        FormulaBlock(
            explanation="由功效方程 P(reject H0 | H1) = 1 - beta 推导，忽略两组方差差异的主项后得到经典闭式解：",
            latex=r"n = \frac{\left(z_{\alpha/2} + z_{\beta}\right)^2 \,\left[p_1(1-p_1) + p_2(1-p_2)\right]}{(p_2 - p_1)^2}",
        ),
        FormulaBlock(
            explanation="更严格的池化方差版本（pooled variance，更接近实际 z-test 拒绝域）：",
            latex=r"n = \frac{\left(z_{\alpha/2}\sqrt{2\bar{p}(1-\bar{p})} + z_{\beta}\sqrt{p_1(1-p_1)+p_2(1-p_2)}\right)^2}{(p_2 - p_1)^2}",
        ),
        (
            "其中 `p_bar = (p1 + p2) / 2`。单侧检验把 `z_{alpha/2}` 替换为 `z_{alpha}`。"
            "注意 MDE 的两种表达方式："
        ),
        (
            "- **绝对 MDE**：delta_abs = p2 - p1（例如 0.02 -> 0.022，delta_abs = 0.002）。"
        ),
        (
            "- **相对 MDE**：delta_rel = (p2 - p1) / p1（例如 10% lift -> p2 = 1.1 * p1）。"
            "工业界常用相对 MDE 因其与产品语言一致，但公式里必须代入绝对差。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("3. Continuous Metrics (t-test analog)", [
        (
            "对连续型指标，记两组方差均为 sigma^2（等方差假设），MDE 为 delta："
        ),
        FormulaBlock(
            explanation="所需每组样本量：",
            latex=r"n = \frac{2\,\sigma^2\,(z_{\alpha/2} + z_{\beta})^2}{\delta^2}",
        ),
        (
            "当 sigma 未知时，使用样本标准差 s 和 t 分布的临界值；但 n 较大时 t 近似 z，上式足够精确。"
            "方差来源一般为**实验前历史数据**或**pilot 小流量实验**。如果指标是重尾（heavy-tailed，如收入），"
            "应先对数变换、winsorize，或改用排序检验（Mann-Whitney U），否则 n 会被少数极值主导。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("4. Worked Examples", [
        "**案例 A：转化率提升检测。**",
        (
            "基线转化率 p1 = 2%，目标相对提升 10%（即 p2 = 2.2%，delta_abs = 0.002），"
            "alpha = 0.05 双侧（z_{alpha/2} = 1.96），power = 0.80（z_{beta} = 0.84）。"
        ),
        FormulaBlock(
            explanation="代入闭式公式：",
            latex=r"n = \frac{(1.96 + 0.84)^2 \cdot [0.02 \cdot 0.98 + 0.022 \cdot 0.978]}{(0.002)^2} \approx \frac{7.84 \cdot 0.04112}{4\times 10^{-6}} \approx 80{,}596",
        ),
        (
            "即每组约需 8.1 万用户，两组合计约 16.1 万。若每日可分配实验流量 2 万/组，实验需运行约 4 天；"
            "但实际上建议覆盖**至少一个完整业务周期（7 天）**以消除周内效应（day-of-week bias）。"
        ),
        "**案例 B：人均收入（连续指标）。**",
        (
            "基线人均 revenue = 5.0 美元，sigma = 12.0 美元（重尾，已 winsorize 在 99 分位），"
            "希望检出 delta = 0.2 美元（4% 相对提升），alpha = 0.05 双侧，power = 0.80。"
        ),
        FormulaBlock(
            explanation="代入连续指标公式：",
            latex=r"n = \frac{2 \cdot 12^2 \cdot (1.96 + 0.84)^2}{0.2^2} = \frac{288 \cdot 7.84}{0.04} \approx 56{,}448",
        ),
        (
            "每组约 5.6 万用户。注意连续指标对方差极其敏感：若 sigma 从 12 降到 8（CUPED 通常可降 30-50%），"
            "n 会下降至约 25,100，近乎减半。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("5. Sensitivity Table: n vs MDE", [
        "下表展示 p1 = 2%、alpha = 0.05 双侧、power = 0.80 下，每组样本量随相对 MDE 的变化。",
    ])
    b.add_comparison_table(
        headers=["Relative MDE", "p2", "delta_abs", "n per arm (approx)"],
        rows=[
            ["1%",  "2.02%", "0.0002", "~7,900,000"],
            ["2%",  "2.04%", "0.0004", "~1,980,000"],
            ["5%",  "2.10%", "0.0010", "~318,000"],
            ["10%", "2.20%", "0.0020", "~80,600"],
            ["20%", "2.40%", "0.0040", "~20,600"],
            ["50%", "3.00%", "0.0100", "~3,400"],
        ],
        title="Sample size vs MDE (baseline p1=2%, alpha=0.05 two-sided, power=0.80)",
    )
    b.add_section("Sensitivity Takeaway", [
        (
            "样本量按 `1 / delta^2` 增长——**MDE 减半则 n 翻四倍**。"
            "这解释了为什么成熟产品越难做显著性实验：基线指标已经很高，剩余提升空间小，"
            "单实验 n 动辄需要数百万甚至上千万曝光。此时的对策通常是："
            "(1) 改用 CUPED 等方差缩减；(2) 合并层内多个指标使用 MANOVA；"
            "(3) 放弃 per-experiment 显著性、改用 **holdout + long-term incrementality**。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("6. Practical Gotchas", [
        "**（1）多重检验（multiple testing）。**",
        (
            "同一实验监控 k 个指标 / k 个细分人群，每个 p-value 独立判定会把 family-wise Type I 误差"
            "放大到约 1 - (1 - alpha)^k。常见对策："
        ),
        (
            "- **Bonferroni**：alpha_each = alpha / k，保守但简单；"
            "- **BH (Benjamini-Hochberg)**：控制 FDR（错误发现率），功效更高，"
            "在指标数 k >= 5 时显著优于 Bonferroni；"
            "- **主指标（OEC, Overall Evaluation Criterion）**：事先声明唯一主指标，辅以 guardrail，"
            "工业界最常用做法。"
        ),
        "**（2）Sample Ratio Mismatch（SRM）。**",
        (
            "若分流设计 50/50 但实测 49.4/50.6，对 100 万样本做卡方检验 p < 0.001——这几乎必定是 bug。"
            "常见原因：bot 过滤不对称、埋点丢失、redirect 在某一 variant 失败、登录态差异。"
            "**SRM 检测应在看任何业务指标之前完成**，否则结论不可信。"
        ),
        "**（3）Novelty & Primacy effects。**",
        (
            "新 UI 在上线初期可能因为新鲜感引发点击率上升（novelty），也可能因不熟悉引发下降（primacy）。"
            "两者都会在 1-2 周后衰减。若实验窗口太短，样本量公式算出的 n 够，但**结论不稳定**。"
            "对策：至少跑满一个业务周期，并画**滚动 7 日指标曲线**观察是否收敛。"
        ),
        "**（4）Peeking / 序贯检验。**",
        (
            "每天看一次 p-value 并在首次 <0.05 时停止——这是典型的 p-hacking，Type I 实际上远高于名义 alpha。"
            "**修复方案**：使用 **always-valid 方法**，如 **mSPRT** 或 **Group Sequential boundaries (Pocock / O'Brien-Fleming)**。"
            "Optimizely、VWO 等商用平台默认使用 mSPRT，允许随时偷看而无需 Bonferroni 校正。"
        ),
        "**（5）方差缩减：CUPED。**",
        (
            "CUPED 用实验前协变量 X（通常是同一用户的 pre-period 指标）回归 Y，用残差 Y - theta*X 做检验。"
            "减少的方差比例等于 `rho^2`（pre 与 post 的相关系数平方），典型可降 30-70%。"
            "对应所需 n 按 `1 - rho^2` 比例缩小，几乎是免费的 power 提升。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("7. Decision Table: Scenario -> Recommended Approach", [])
    b.add_comparison_table(
        headers=["Scenario", "Metric type", "Suggested method", "n-reduction lever"],
        rows=[
            ["Homepage CTR lift",      "Proportion", "two-proportion z-test", "CUPED on user-level pre CTR"],
            ["Revenue per user",       "Continuous (heavy tail)", "Welch t-test on winsorized value", "CUPED + log transform"],
            ["Multi-metric launch",    "Mixed",      "OEC + guardrail, BH on secondary", "Pre-register primary"],
            ["Small surface, rare event", "Proportion (p1<0.1%)", "Exact / Fisher; or aggregate across surfaces", "Extend duration; pool arms"],
            ["Long-term retention",    "Proportion (D30)", "Quasi-experiment + holdout", "Back-to-back experiments"],
            ["Need rapid iteration",   "Any",       "Sequential testing (mSPRT)", "Allow peeking safely"],
        ],
        title="Choose method by scenario",
    )

    # ------------------------------------------------------------------
    b.add_section("8. Interview Q&A", [])
    b.add_interview_qa(
        "为什么样本量公式里是 (z_{alpha/2} + z_{beta})^2，而不是 (z_{alpha/2} - z_{beta})^2？",
        (
            "功效方程要求在 H1 下拒绝 H0 的概率为 1 - beta。在 H1 下观测统计量的均值向右移动了 delta，"
            "要让它仍以概率 1-beta 越过临界值 z_{alpha/2}，需要 delta / SE >= z_{alpha/2} + z_{beta}。"
            "两个 z 值相加是因为一个度量 Type I 的临界位置，另一个度量 Type II 的尾部位置，"
            "它们指向**相同方向**的距离而不是相消。"
        ),
    )
    b.add_interview_qa(
        "如果我把 alpha 从 0.05 改到 0.01，n 大致变多少？",
        (
            "z_{0.025} = 1.96，z_{0.005} = 2.576。n 正比于 (z_{alpha/2}+z_{beta})^2："
            "(2.576+0.84)^2 / (1.96+0.84)^2 约等于 11.67/7.84 约等于 1.49，即 n 增加约 49%。"
            "这是降低 Type I 误差的边际成本；如果同时要求 power=0.9，还需再乘额外系数。"
        ),
    )
    b.add_interview_qa(
        "我的产品每天只有 5000 活跃用户，想检出 1% 相对提升，可行吗？",
        (
            "用 sensitivity table 估算：baseline 2%、相对 MDE 1% 大约需要 790 万/组——"
            "在 5000 DAU 下要跑 3000 天，显然不可行。实践上应该：(1) 放宽 MDE 到 10-20%，即只关注较大效应；"
            "(2) 用 CUPED / 分层随机化降方差；(3) 用 **switchback 设计** 或 **interrupted time series** "
            "换取 within-subject 对比；(4) 多个相关小实验合并汇报 **meta-analysis**。"
            "关键是**提前告诉 stakeholder 不可能检出小效应**，避免浪费资源。"
        ),
    )
    b.add_interview_qa(
        "什么时候用单侧检验，什么时候用双侧？",
        (
            "双侧是默认：保护自己不要把**负向改动**误认为无效（例如新 UI 提案意外导致转化率下降）。"
            "单侧只有在**事先有强先验，且反向效应完全不影响决策**时才合理——例如纯加法功能，反向效应极不可能。"
            "在学术严谨场景，单侧几乎总被质疑，因为它等价于偷偷把 alpha 从 0.05 放宽到 0.1。"
            "工业界 best practice：坚持双侧，即使公式里因此 z_{alpha/2} 比 z_{alpha} 大。"
        ),
    )
    b.add_interview_qa(
        "CUPED 为什么能减少所需 n？它会改变 Type I 误差吗？",
        (
            "CUPED 利用 pre-experiment 协变量 X 的回归残差作为新指标：Y_cuped = Y - theta (X - E[X])，"
            "其中 theta = Cov(X,Y)/Var(X)。因为随机化保证 E[X | treatment] = E[X | control]，"
            "减去 theta*X 不会改变处理效应的期望，但**方差按 1-rho^2 缩小**（rho 是 X 与 Y 的相关系数）。"
            "因此 n 按 1-rho^2 比例下降，Type I 误差**不变**。"
            "典型 rho=0.5 时 n 下降 25%，rho=0.7 时下降 51%。代价仅是实现上的一次 OLS。"
        ),
    )

    # ------------------------------------------------------------------
    b.add_checklist("Self-Check (面试前必过)", [
        "能在白板上默写 two-proportion 样本量公式并说明每一项含义",
        "能区分绝对 MDE 与相对 MDE，并把相对 MDE 正确转成公式里的 delta_abs",
        "能解释 alpha、beta、power、MDE 四者的 trade-off，并画图示意",
        "能说出 SRM 的定义、检测方法（卡方）以及为什么要在看业务指标前检测",
        "能列出至少 3 种方差缩减手段及其适用场景（CUPED、分层、trimming）",
        "能说明为什么 peeking 破坏 alpha，以及 mSPRT / Group Sequential 如何修复",
        "能在 30 秒内估出 p1=5%、相对 MDE=5%、alpha=0.05、power=0.8 时每组约 62k 样本",
    ])

    return b.build()


def upsert_node(conn: sqlite3.Connection, content: str) -> tuple[int, int]:
    parent = conn.execute(
        "SELECT id, depth FROM framework_nodes WHERE path = ?", (PARENT_PATH,)
    ).fetchone()
    if not parent:
        print(f"[FAIL] Parent path {PARENT_PATH} not found")
        sys.exit(1)
    parent_id, parent_depth = parent

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
            (parent_id, NODE_PATH, parent_depth + 1, NODE_TITLE, content,
             0.9, "P1", "not_started", 0.0),
        )
        node_id = cur.lastrowid
        action = "INSERTED"
    conn.commit()
    length = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()[0]
    print(f"[{action}] node_id={node_id} path={NODE_PATH} length={length} chars")
    return node_id, length


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
        upsert_node(conn, content)
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    main()
