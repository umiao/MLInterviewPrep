"""Seed framework node: pillar2.regularization.bias_variance_geometric.

Creates the subtree ``pillar2.regularization`` (if absent) plus the leaf
``pillar2.regularization.bias_variance_geometric`` and populates the leaf's
``description`` via StudyNoteBuilder.

Usage::

    python scripts/seed_bias_variance_geometric.py

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

PILLAR_PATH = "pillar2"
SUBTREE_PATH = "pillar2.regularization"
SUBTREE_TITLE = "Regularization"
NODE_PATH = "pillar2.regularization.bias_variance_geometric"
NODE_TITLE = "Bias-Variance & L1/L2 Geometric View"


def build_content() -> str:
    b = StudyNoteBuilder()
    b.set_title("Bias-Variance Decomposition & L1/L2 Regularization (Geometric View)")

    b.add_prerequisites([
        "线性代数基础：范数、凸集、等高线（level set）",
        "概率论：期望、方差、条件期望",
        "线性回归 / logistic regression 的损失函数形式",
        "梯度下降与约束优化（拉格朗日乘子）",
    ])

    b.add_term("MSE", "Mean Squared Error",
               "均方误差，回归问题最常用的损失度量")
    b.add_term("OLS", "Ordinary Least Squares",
               "普通最小二乘，线性回归的无正则基线解法")
    b.add_term("MAP", "Maximum A Posteriori",
               "最大后验估计；L2 对应 Gaussian prior，L1 对应 Laplace prior")
    b.add_term("KKT", "Karush-Kuhn-Tucker",
               "带约束凸优化的一阶最优性条件，是约束形式与拉格朗日形式等价的桥梁")

    # ------------------------------------------------------------------
    b.add_section("1. Overview: Why Regularize", [
        (
            "在有限样本下，**模型容量（capacity）**越高越容易过拟合。"
            "**MSE** 的期望误差可以被代数分解为三项：bias^2、variance、irreducible noise。"
            "正则化（regularization）通过压缩参数空间降低 variance，以可控的 bias 增加换取更低的总期望误差。"
            "这与 **MAP** 视角等价——对参数施加先验，L2 对应 Gaussian prior，L1 对应 Laplace prior。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("2. Bias-Variance Decomposition", [
        (
            "设真实数据生成过程为 y = f(x) + epsilon，其中 epsilon 为零均值、方差 sigma^2 的不可约噪声。"
            "在训练集 D 上得到的预测函数为 hat_f_D(x)。在固定点 x 处的期望平方误差（对 D 与 epsilon 取期望）为："
        ),
        FormulaBlock(
            explanation="经典分解式：",
            latex=r"\mathbb{E}_{D,\epsilon}\bigl[(y - \hat f_D(x))^2\bigr] = \underbrace{\bigl(\mathbb{E}_D[\hat f_D(x)] - f(x)\bigr)^2}_{\text{Bias}^2} + \underbrace{\mathbb{E}_D\bigl[(\hat f_D(x) - \mathbb{E}_D[\hat f_D(x)])^2\bigr]}_{\text{Variance}} + \underbrace{\sigma^2}_{\text{Noise}}",
        ),
        (
            "三项含义：**Bias** 衡量模型平均预测与真实函数的系统偏差（under-fitting 信号）；"
            "**Variance** 衡量模型在不同训练集上的抖动（over-fitting 信号）；"
            "**Noise** 为数据本身的随机性，任何模型都无法消除，它决定了期望误差的下界。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("3. Learning-Curve Diagnosis", [
        (
            "Learning curve 把训练误差与验证误差画在同一张图上（横轴为样本量或训练轮数）。"
            "通过**曲线形态**可以快速判断模型处于 high-bias 还是 high-variance 状态，"
            "并据此选择正确的干预手段（加特征 vs 加正则）。"
        ),
    ])
    b.add_comparison_table(
        headers=["Regime", "Train loss", "Val loss", "Gap", "Root cause", "Fix"],
        rows=[
            ["High bias (under-fit)", "高且平台", "高且平台", "小",
             "模型容量不足 / 特征不足", "加深模型；加特征；减小正则 lambda"],
            ["High variance (over-fit)", "很低", "高", "大",
             "参数过多 / 样本太少 / lambda 太小", "加 L1/L2；加 dropout；增样本；early stop"],
            ["Sweet spot", "适中", "适中", "小", "容量与正则匹配", "保持；监控分布漂移"],
            ["Irreducible", "接近噪声下界", "接近噪声下界", "小",
             "已触及 sigma^2", "换更好的标签 / 特征"],
        ],
        title="Learning-curve pattern -> action",
    )

    # ------------------------------------------------------------------
    b.add_section("4. Mitigation Map: Bias vs Variance Levers", [])
    b.add_comparison_table(
        headers=["Lever", "Effect on Bias", "Effect on Variance", "Typical use"],
        rows=[
            ["增大模型容量（深度/宽度）", "降低", "升高", "欠拟合"],
            ["增加 L2 系数 lambda", "升高（轻微）", "降低", "高方差主因时"],
            ["L1 系数 lambda", "升高", "降低（通过稀疏化）", "高维+需特征选择"],
            ["Dropout / data augmentation", "几乎不变", "降低", "DNN 过拟合"],
            ["增加训练样本", "不变", "降低", "通用，但成本高"],
            ["Bagging（Random Forest）", "略升", "显著降低", "高方差基学习器"],
            ["Boosting（GBDT）", "显著降低", "略升", "高偏差基学习器"],
            ["Early stopping", "升高（轻微）", "降低", "梯度训练标配"],
        ],
        title="Levers and their bias-variance direction",
    )

    # ------------------------------------------------------------------
    b.add_section("5. L1 vs L2: Loss Surfaces & Constraint Regions (Clarified)", [
        (
            "L1 / L2 正则有两种等价写法——**penalty form** 与 **constraint form**。"
            "澄清这一点能避免将“几何切点图”误读为“优化过程图”。"
        ),
        FormulaBlock(
            explanation="Penalty form（无约束，含惩罚项）：",
            latex=r"(\mathrm{P1}):\quad \min_{w}\; \mathrm{MSE}(w) + \lambda\,\|w\|",
        ),
        FormulaBlock(
            explanation="Constraint form（有界约束域）：",
            latex=r"(\mathrm{P2}):\quad \min_{w}\; \mathrm{MSE}(w)\quad \text{s.t.}\quad \|w\| \le t",
        ),
        (
            "**静态几何对象（并非迭代轨迹）**：在 w 空间："
        ),
        (
            "- **椭圆等高线**：MSE(w) 的 level set，是一族**同心椭圆**，中心为无约束 MSE 最小点 $\\hat w$（即 OLS 解）。"
        ),
        (
            "- **约束区域**：L1 下是以原点为中心的**菱形（$\\ell_1$ ball）**；L2 下是**圆 / 球（$\\ell_2$ ball）**。"
        ),
        (
            "- **最优解 w\\***：从椭圆中心 $\\hat w$ 出发不断**放大等高线**，"
            "**首次触碰约束区域**的那个点就是 w\\*。这是**位置关系**，"
            "与优化算法、初始点、步长都无关——换句话说，这张图描述的是**最优解在哪里**，不是**解是怎么走到的**。"
        ),
        (
            "**为什么 L1 偏顶点（稀疏性几何直觉）**：菱形的**顶点凸出**（锥形尖角），"
            "椭圆从大多数方向逼近时会**先碰到顶点**；而顶点恰好落在**坐标轴上**，"
            "对应某个分量 $w_i = 0$——这就是 L1 产生**稀疏解**的几何原因。"
            "维度升高时，$\\ell_1$ 单位球的顶点数以 $O(2^p)$ 增长，稀疏性倾向**更强**。"
        ),
        (
            "**为什么 L2 不稀疏**：圆 / 球表面**处处光滑**，"
            "椭圆与圆的切点可以出现在圆周上**任意位置**，几乎不会精确落在坐标轴——"
            "因此 L2 只把参数**整体压小**，却**不压到零**。"
        ),
        (
            "**常见误读纠正**：这张“椭圆 + 菱形/圆”图**不是**梯度下降的轨迹图，"
            "也不反映 $\\lambda$ 或初始点的影响；它仅描述**最优解位置**。"
            "penalty form 里调大 $\\lambda$ ⇔ constraint form 里缩小 $t$（约束区收紧），"
            "两者通过下一节的 KKT 一一对应。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("5.5 Primal-Dual Equivalence via KKT", [
        (
            "上一节给了**几何直觉**，本节给**严格推导**：penalty form (P1) 与 constraint form (P2) "
            "通过 **Lagrangian** 和 **KKT 条件**一一对应。"
            "以 L1 为例（L2 推导同构，只把 $\\|w\\|_1$ 换成 $\\|w\\|_2^2$）。"
        ),
        (
            "**方向 1：(P2) ⇒ (P1)**。写 (P2) 的 Lagrangian，其中 $\\lambda \\ge 0$ 为对偶变量："
        ),
        FormulaBlock(
            explanation="Lagrangian：",
            latex=r"\mathcal{L}(w,\lambda) = \mathrm{MSE}(w) + \lambda\bigl(\|w\| - t\bigr)",
        ),
        FormulaBlock(
            explanation="对偶函数（对 w 内层求极小）：",
            latex=r"g(\lambda) = \min_{w}\;\mathcal{L}(w,\lambda) = \underbrace{\min_{w}\bigl[\mathrm{MSE}(w) + \lambda\|w\|\bigr]}_{\text{正是 (P1)}} \;-\;\lambda t",
        ),
        (
            "中括号内的子问题**恰好就是 (P1)**；因此在固定 $\\lambda$ 下，两问题有**相同的内层最优 w**。"
            "由 **Slater 条件**（只要 $t > 0$，取 $w = 0$ 严格满足 $\\|w\\| < t$），强对偶成立，KKT 条件既必要又充分："
        ),
        FormulaBlock(
            explanation="KKT 四条件：",
            latex=r"\begin{aligned} &\text{Stationarity:}\quad 0 \in \partial_w \mathrm{MSE}(w^*) + \lambda^*\,\partial\|w^*\|\\ &\text{Primal feasibility:}\quad \|w^*\| \le t\\ &\text{Dual feasibility:}\quad \lambda^* \ge 0\\ &\text{Complementary slackness:}\quad \lambda^*\bigl(\|w^*\| - t\bigr) = 0 \end{aligned}",
        ),
        (
            "**方向 2：(P1) ⇒ (P2)**。给定某个 $\\lambda \\ge 0$，令 $w^*(\\lambda)$ 为 (P1) 最优解；"
            "取 $t = \\|w^*(\\lambda)\\|$。反证：若存在某 $\\tilde w$ 使 $\\mathrm{MSE}(\\tilde w) < \\mathrm{MSE}(w^*)$ 且 $\\|\\tilde w\\| \\le t$，"
            "则 $\\mathrm{MSE}(\\tilde w) + \\lambda\\|\\tilde w\\| < \\mathrm{MSE}(w^*) + \\lambda\\|w^*\\|$，"
            "与 $w^*$ 是 (P1) 最优矛盾。故 $w^*$ 也是 (P2) 对该 $t$ 的最优解。"
        ),
        (
            "**互补松弛的两种几何情形**："
        ),
        (
            "- **情形 (i)**：$\\lambda^* = 0$。约束不起作用，$w^* = \\hat w$ 已经在约束区内——"
            "等价于 penalty form 里 $\\lambda$ 过小、正则失效。"
        ),
        (
            "- **情形 (ii)**：$\\|w^*\\| = t$。最优解**贴边界**；L1 下典型就是顶点，L2 下是圆周上某点。"
            "这就是几何图里“首次触碰”场景的严格对应。"
        ),
        (
            "**一句话总结**：$\\lambda$（penalty 强度）与 $t$（约束半径）通过 KKT **一一对应**；"
            "几何图呈现的是 KKT 最优性条件的**可视化**，而非优化过程。"
            "L2 推导结构完全相同，只需把次梯度 $\\partial\\|w\\|_1$ 换为光滑梯度 $\\nabla\\|w\\|_2^2 = 2w$。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("6. Closed-Form Ridge vs Soft-Thresholding Lasso", [
        FormulaBlock(
            explanation="Ridge 闭式解（正规方程加正则项）：",
            latex=r"\hat\beta_{\text{ridge}} = (X^\top X + \lambda I)^{-1} X^\top y",
        ),
        (
            "加上 lambda I 之后，即便 X^T X 奇异（多重共线，multicollinearity）也可解——"
            "这正是 L2 缓解**共线性**的代数原因。特征值较小的方向被 lambda 抬升，使得估计不再发散。"
        ),
        FormulaBlock(
            explanation="正交设计下 Lasso 有逐坐标闭式解（soft-thresholding operator）：",
            latex=r"\hat\beta_j^{\text{lasso}} = \operatorname{sign}\!\left(\hat\beta_j^{\text{OLS}}\right)\cdot\max\!\left(|\hat\beta_j^{\text{OLS}}| - \lambda,\;0\right)",
        ),
        (
            "当 |hat_beta_OLS_j| <= lambda，坐标被“削平”为 0——这就是 **L1 做特征选择（feature selection）**的算法实现。"
            "Ridge 对应的逐坐标操作是 hat_beta_j = hat_beta_OLS_j / (1 + lambda)，**按比例缩小**，永不为 0。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("7. Elastic Net: Bridging L1 and L2", [
        FormulaBlock(
            explanation="Elastic Net 同时包含两种惩罚：",
            latex=r"\min_{\beta}\;\frac{1}{2n}\|y - X\beta\|_2^2 + \lambda\!\left[\alpha\|\beta\|_1 + \tfrac{1-\alpha}{2}\|\beta\|_2^2\right]",
        ),
        (
            "alpha=1 退化为 Lasso，alpha=0 退化为 Ridge。其约束区域是**菱形与圆的凸组合**——"
            "仍保留坐标轴上的“轻微尖角”得到稀疏性，同时圆弧部分让**高度相关特征被一起保留**。"
            "Lasso 面对一组高度相关特征（correlated features）时常**任选一个**；Elastic Net 倾向**同时保留**它们，"
            "在基因组学、点击预测等 p >> n 且特征成组的场景下更稳。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("8. Interview Q&A", [])
    b.add_interview_qa(
        "为什么 L1 会产生稀疏解，而 L2 不会？",
        (
            "几何解释：OLS 损失等高线为椭圆，L1 约束区域是菱形，**尖角在坐标轴上**，"
            "椭圆与菱形相切时大概率落在顶点，对应部分 beta_i = 0。"
            "代数解释：L1 在 0 处的次梯度为区间 [-1, 1]，数据梯度只要落入 [-lambda, lambda] 即被 KKT 允许取 beta_i=0，"
            "形成**软阈值（soft-thresholding）**；而 L2 的梯度在 0 处连续且等于 0，没有这种吸附机制。"
            "因此 L1 是天然的**特征选择器（feature selector）**，适合 p >> n 的稀疏真模型场景。"
        ),
    )
    b.add_interview_qa(
        "为什么多重共线性（multicollinearity）情况下 L2 比 L1 更稳？",
        (
            "共线特征让 X^T X 病态（接近奇异），OLS 估计方差爆炸。"
            "L2 把矩阵改为 X^T X + lambda I，**小特征值被抬升**，条件数下降，估计方差有界。"
            "L1 虽然也能缩小方差，但它会在一组高度相关的特征中**任选一个保留、其它置零**，"
            "选择哪一个对数据小扰动敏感；而 L2 会把权重**均匀分摊**给整组特征，预测更稳定。"
            "若既要稀疏又要稳，用 **Elastic Net**（alpha 约 0.5）可兼得。"
        ),
    )
    b.add_interview_qa(
        "什么场景下 L1 和 L2 都不够？",
        (
            "几个典型场景：(1) 真模型**非线性**，稀疏线性先验不匹配——应换 GBDT 或 DNN + dropout；"
            "(2) 特征具有**群组结构**（grouped features，如 one-hot 的一整个类别变量），"
            "标量 L1 会破坏组内一致性，应用 **Group Lasso**；"
            "(3) 参数具有**时序或空间光滑性**（如系数随时间演化），应用 **Fused Lasso** / total-variation 惩罚；"
            "(4) 样本分布**严重不平衡**时，正则化抑制少数类信号——应同时调整 class weight 或使用 focal loss；"
            "(5) 数据维度巨大且**大部分噪声特征**，Lasso 在相关噪声下会误选——可改用 **SCAD / MCP** 非凸正则降低 bias。"
        ),
    )

    # ------------------------------------------------------------------
    b.add_checklist("Self-Check (面试前必过)", [
        "能默写 bias-variance 分解公式并口述每一项含义",
        "能用 learning curve 形态区分 high-bias 与 high-variance 并给出对应干预",
        "能画出 L1 菱形 / L2 圆形约束区 + 椭圆等高线，并解释切点为何落在坐标轴",
        "能写出 ridge 闭式解并说明 lambda I 如何缓解多重共线性",
        "能写出 lasso 正交设计下的 soft-thresholding 公式",
        "能说明 Elastic Net 在相关特征组上的优势",
        "能列出至少一个 L1/L2 都不足的场景（如 Group Lasso / Fused Lasso）",
    ])

    return b.build()


def upsert_subtree(conn: sqlite3.Connection) -> tuple[int, int]:
    """Ensure pillar2.regularization exists; return (pillar2_id, subtree_id)."""
    pillar = conn.execute(
        "SELECT id, depth FROM framework_nodes WHERE path = ?", (PILLAR_PATH,)
    ).fetchone()
    if not pillar:
        print(f"[FAIL] Pillar path {PILLAR_PATH} not found")
        sys.exit(1)
    pillar_id, pillar_depth = pillar

    existing = conn.execute(
        "SELECT id FROM framework_nodes WHERE path = ?", (SUBTREE_PATH,)
    ).fetchone()
    if existing:
        subtree_id = existing[0]
        action = "EXISTS"
    else:
        cur = conn.execute(
            """
            INSERT INTO framework_nodes
                (parent_id, path, depth, title, description, importance, priority, status, progress_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (pillar_id, SUBTREE_PATH, pillar_depth + 1, SUBTREE_TITLE, None,
             0.9, "P0", "not_started", 0.0),
        )
        subtree_id = cur.lastrowid
        action = "INSERTED"
    print(f"[{action}] subtree id={subtree_id} path={SUBTREE_PATH}")
    return subtree_id, pillar_depth + 1


def upsert_leaf(conn: sqlite3.Connection, parent_id: int, parent_depth: int, content: str) -> int:
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
        subtree_id, subtree_depth = upsert_subtree(conn)
        upsert_leaf(conn, subtree_id, subtree_depth, content)
        conn.commit()
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    main()
