"""Seed script: Adobe Final Round prep page -- Statistics + RAG (Q1-Q50).

Source: docs/adobe_final_prep_source_2026-05-21.md (user-provided 2026-05-21).
Pattern: mirrors scripts/seed_adobe_day1_chinese.py (StudyNoteBuilder + FormulaBlock).

Covers:
- Part 1 Statistics (Q1-Q33, 11 subsections)
- Part 2 RAG full-stack (Q34-Q50, 7 subsections)
- Interview tips coda

Idempotent: delete by sentinel/title before insert.
Sentinel: <!-- ADOBE_FINAL_STATS_RAG_V1_20260521 -->
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

_BUILDER_PATH = Path(__file__).resolve().parent / "study_note_builder.py"
_spec = importlib.util.spec_from_file_location("study_note_builder", _BUILDER_PATH)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["study_note_builder"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
StudyNoteBuilder = _mod.StudyNoteBuilder
FormulaBlock = _mod.FormulaBlock

COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Final Round Prep: Statistics + RAG (Q1-Q50)"
SENTINEL = "<!-- ADOBE_FINAL_STATS_RAG_V1_20260521 -->"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def build_note() -> StudyNoteBuilder:
    b = StudyNoteBuilder()
    b.set_title("Adobe Final Round Prep: Statistics + RAG (Q1-Q50)")

    b.add_prerequisites([
        "概率论基础: 高斯/伯努利/二项/泊松分布, 期望与方差, 条件概率",
        "线性代数: 矩阵乘法、求逆、特征分解",
        "回归基础: 线性回归 OLS 闭式解、损失函数",
        "ML 工程基础: 评估指标 (Precision/Recall/AUC), 训练-验证-测试集划分",
        "向量检索基础概念: embedding, cosine similarity, ANN (Approximate Nearest Neighbor)",
    ])

    # ---- Terms (Part 1: Statistics) ----
    b.add_term("SE", "Standard Error", "统计量本身的标准差 (e.g. SE of mean = s/sqrt(n))")
    b.add_term("SD", "Standard Deviation", "单个观测值的离散程度")
    b.add_term("CI", "Confidence Interval", "置信区间, 描述均值/比例的不确定性")
    b.add_term("PI", "Prediction Interval", "预测区间, 描述单个新观测的不确定性 (比 CI 宽)")
    b.add_term("CLT", "Central Limit Theorem", "中心极限定理, 样本均值近似正态")
    b.add_term("PDF", "Probability Density Function", "概率密度函数")
    b.add_term("MDE", "Minimum Detectable Effect", "可检出的最小效应量")
    b.add_term("FWER", "Family-Wise Error Rate", "至少一个 false positive 的概率")
    b.add_term("FDR", "False Discovery Rate", "误拒占所有拒绝中的比例")
    b.add_term("BH", "Benjamini-Hochberg", "控制 FDR 的多重比较修正方法")
    b.add_term("CUPED", "Controlled-experiment Using Pre-Experiment Data",
               "用实验前协变量抵消基线差异, 减小方差")
    b.add_term("OLS", "Ordinary Least Squares", "普通最小二乘法")
    b.add_term("VIF", "Variance Inflation Factor", "方差膨胀因子, 检测多重共线性")
    b.add_term("IRLS", "Iteratively Reweighted Least Squares",
               "迭代重加权最小二乘, 求解 logistic regression MLE 的标准算法")
    b.add_term("MLE", "Maximum Likelihood Estimation", "极大似然估计")
    b.add_term("MSE", "Mean Squared Error", "均方误差")
    b.add_term("AUC", "Area Under the Curve", "曲线下面积, 默认指 ROC-AUC")
    b.add_term("ROC", "Receiver Operating Characteristic", "TPR-FPR 曲线")
    b.add_term("PR-AUC", "Precision-Recall AUC", "Precision-Recall 曲线下面积, 对正类比例敏感")
    b.add_term("TPR", "True Positive Rate", "真正例率 = TP/(TP+FN), 等于 Recall")
    b.add_term("FPR", "False Positive Rate", "假正例率 = FP/(FP+TN)")
    b.add_term("MCAR", "Missing Completely at Random", "缺失与任何变量无关")
    b.add_term("MAR", "Missing at Random", "缺失依赖观测到的其他变量")
    b.add_term("MNAR", "Missing Not at Random", "缺失依赖未观测到的值本身")
    b.add_term("MICE", "Multiple Imputation by Chained Equations",
               "链式方程多重填补, 反映缺失值不确定性")
    b.add_term("EM", "Expectation-Maximization",
               "期望最大化算法, 含缺失/隐变量的参数估计")
    b.add_term("DiD", "Difference-in-Differences",
               "双重差分, 政策/特性 rollout 前后对比的因果推断方法")
    b.add_term("RDD", "Regression Discontinuity Design",
               "断点回归, 利用阈值附近的伪随机分配做因果推断")
    b.add_term("IV", "Instrumental Variable", "工具变量, Z 影响 T 但不直接影响 Y")
    b.add_term("PSM", "Propensity Score Matching", "倾向得分匹配, 观察数据因果推断")
    b.add_term("ANCOVA", "Analysis of Covariance", "协方差分析, 回归调整的标准形式")
    b.add_term("EM-algo", "Expectation-Maximization Algorithm",
               "E-step 填补隐变量条件期望, M-step 更新参数, 迭代求 MLE")

    # ---- Terms (Part 2: RAG) ----
    b.add_term("RAG", "Retrieval-Augmented Generation",
               "检索增强生成, LLM 接外部知识库回答的范式")
    b.add_term("MTEB", "Massive Text Embedding Benchmark",
               "embedding 模型公开评测榜单")
    b.add_term("HNSW", "Hierarchical Navigable Small World",
               "多层图近邻索引, 当前最常用的 ANN 算法")
    b.add_term("IVF", "Inverted File Index",
               "倒排文件索引, 先聚类再搜对应簇")
    b.add_term("PQ", "Product Quantization",
               "乘积量化, 将向量分块独立量化以压缩内存")
    b.add_term("ANN", "Approximate Nearest Neighbor",
               "近似最近邻搜索, 用精度换速度")
    b.add_term("BM25", "Best Matching 25",
               "经典稀疏检索算法, 基于词频与文档长度的 TF-IDF 改进版")
    b.add_term("HyDE", "Hypothetical Document Embeddings",
               "让 LLM 写假设答案再 embed 检索, 提升长尾/抽象 query 召回")
    b.add_term("MRR", "Mean Reciprocal Rank",
               "平均倒数排名, 衡量首个相关结果的位置")
    b.add_term("NDCG", "Normalized Discounted Cumulative Gain",
               "归一化折扣累积增益, 分级相关性下的排序质量度量")
    b.add_term("RAGAS", "Retrieval-Augmented Generation Assessment",
               "RAG 端到端评估框架, 含 faithfulness/answer relevance 等指标")
    b.add_term("NLI", "Natural Language Inference",
               "自然语言推理, 判断蕴含/中立/矛盾, 用于 hallucination 检测")
    b.add_term("PII", "Personally Identifiable Information", "个人身份信息")
    b.add_term("ACL", "Access Control List", "访问控制列表, 检索层的权限过滤依据")
    b.add_term("AST", "Abstract Syntax Tree",
               "抽象语法树, 代码分块按函数/类切的依据")
    b.add_term("ColBERT", "Contextualized Late Interaction over BERT",
               "late-interaction 检索模型, 每 token 独立 embed + MaxSim 交互")

    # ============================================================
    # PART 1: STATISTICS
    # ============================================================

    b.add_section("Part 1 · 1. 描述性统计 (Descriptive Statistics)", [
        "**Q1. 样本均值、方差、标准差公式?**",
        "- 样本均值: $\\bar{x} = \\frac{1}{n}\\sum_{i=1}^{n} x_i$",
        "- 样本方差 (无偏): $s^2 = \\frac{1}{n-1}\\sum_{i=1}^{n}(x_i - \\bar{x})^2$",
        "- 样本标准差: $s = \\sqrt{s^2}$",
        "**为什么 n-1 (Bessel's correction)?** 用 $\\bar{x}$ 估计 $\\mu$ 时占用了一个自由度, "
        "分母用 $n$ 会低估总体方差。除以 $n-1$ 让估计量无偏。",

        "**Q2. 标准误 (SE) 和标准差 (SD) 的区别?**",
        "- SD 描述**单个观测值**的离散程度",
        "- SE 描述**统计量本身**的不确定性",
        "- 均值的标准误: $SE_{\\bar{x}} = \\frac{s}{\\sqrt{n}}$ (样本量 $n$ 越大, $\\bar{x}$ 越精确)",

        "**Q3. 95% 置信区间什么意思? 最常见的误解?**",
        "- 公式 (均值, 大样本): $\\bar{x} \\pm z_{\\alpha/2} \\cdot \\frac{s}{\\sqrt{n}}$, "
        "其中 $z_{0.025} = 1.96$",
        "- 小样本 ($n < 30$ 且 $\\sigma$ 未知) 用 t 分布: "
        "$\\bar{x} \\pm t_{\\alpha/2, n-1} \\cdot \\frac{s}{\\sqrt{n}}$",
        "- 比例的 Wald CI: $\\hat{p} \\pm z_{\\alpha/2}\\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}}$",
        "- 极端比例 ($p$ 接近 0 或 1) 用 **Wilson 区间** 更稳",
        "**误解**: \"真实参数有 95% 概率落在这个区间里\" [WRONG]",
        "**正确**: 在重复实验意义下, 构造的 CI 中有 95% 会包含真实参数。"
        "**真实参数是固定的, 区间才是随机的**。",
    ])

    b.add_section("Part 1 · 2. 概率分布 (Probability Distributions)", [
        "**Q4. 二项分布 (Binomial) 关键公式?**",
        FormulaBlock(
            latex=r"P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}",
            explanation="二项分布 PMF: n 次独立 Bernoulli 实验中恰好 k 次成功的概率",
        ),
        "- $E[X] = np$",
        "- $Var[X] = np(1-p)$",
        "- 当 $np \\geq 5$ 且 $n(1-p) \\geq 5$, 可用正态近似 $N(np, np(1-p))$",

        "**Q5. 正态分布 PDF 和重要性质?**",
        FormulaBlock(
            latex=r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)",
            explanation="正态分布概率密度函数",
        ),
        "- 68/95/99.7 法则 (1σ / 2σ / 3σ 覆盖比例)",
        "- 线性组合仍正态: $aX + bY \\sim N(a\\mu_X + b\\mu_Y, a^2\\sigma_X^2 + b^2\\sigma_Y^2)$ "
        "(X, Y 独立)",

        "**Q6. 中心极限定理 (CLT) 是什么?**",
        "任意分布 (方差有限) 的样本均值, 当 $n$ 足够大时, 分布近似为:",
        FormulaBlock(
            latex=r"\bar{X} \sim N\!\left(\mu,\, \frac{\sigma^2}{n}\right)",
            explanation="CLT 渐近正态结论: 大样本下样本均值的分布",
        ),
        "经验阈值 $n \\geq 30$。极偏分布需要更大 $n$。"
        "这是 A/B test 用 z-test 的理论基础。",

        "**Q7. 常见分布速查?**",

        "| 分布 | 场景 | 期望 |",
        "|---|---|---|",
        "| Bernoulli($p$) | 单次二元事件 | $p$ |",
        "| Binomial($n,p$) | $n$ 次独立 Bernoulli | $np$ |",
        "| Poisson($\\lambda$) | 稀有事件计数 | $\\lambda$ |",
        "| Exponential($\\lambda$) | 事件间隔时间 | $1/\\lambda$ |",
        "| Beta($\\alpha, \\beta$) | 比例的先验 (Bayesian) | $\\alpha/(\\alpha+\\beta)$ |",
        "| Geometric($p$) | 直到首次成功的尝试数 | $1/p$ |",
    ])

    b.add_section("Part 1 · 3. 假设检验 (Hypothesis Testing)", [
        "**Q8. p-value 严格定义?**",
        FormulaBlock(
            latex=r"p = P(\text{observe data as extreme or more} \mid H_0\text{ true})",
            explanation="p-value 的严格定义: 在零假设为真时, 观察到当前或更极端数据的概率",
        ),
        "**绝不等于** $P(H_0 \\mid \\text{data})$。",

        "**Q9. p-value 五大常见误解?**",
        "1. **p < 0.05 != 效果重要** -- 统计显著与实际显著不同。"
        "$n$ 极大时几乎任何差异都显著",
        "2. **p >= 0.05 != $H_0$ 为真** -- \"absence of evidence is not evidence of absence\"",
        "3. **p-value 不告诉你效果大小** -- 必须配合 effect size 和 CI",
        "4. **多次测试不调整** -> $\\alpha$ 膨胀",
        "5. **p-hacking**: 反复看数据、改变停止规则会让 p 失效",

        "**Q10. Type I / Type II / Power 的定义?**",

        "|  | $H_0$ 真 | $H_1$ 真 |",
        "|---|---|---|",
        "| 拒绝 $H_0$ | Type I 错误 ($\\alpha$) | 正确 (Power) |",
        "| 不拒绝 $H_0$ | 正确 | Type II 错误 ($\\beta$) |",

        "- $\\alpha$ = Type I 错误率 (常取 0.05)",
        "- $\\beta$ = Type II 错误率",
        "- **Power = $1 - \\beta$** = 在 $H_1$ 真时成功检出的概率 (常要求 0.8)",
        "**影响 Power 的因素**: 样本量 ↑、effect size ↑、方差 ↓、$\\alpha$ ↑ -> Power ↑",

        "**Q11. A/B test 样本量公式 (两比例)?**",
        FormulaBlock(
            latex=r"n = \frac{(z_{\alpha/2} + z_\beta)^2 \cdot [p_1(1-p_1) + p_2(1-p_2)]}{(p_1 - p_2)^2}",
            explanation="每组样本量 (标准近似), 双尾两比例检验",
        ),
        "**数值例子**: baseline CTR = 5%, MDE (绝对) = 0.5%, $\\alpha=0.05$ (双尾), power=0.8",
        "- $z_{0.025} = 1.96$, $z_{0.20} = 0.84$",
        "- 分子: $(1.96+0.84)^2 \\cdot (0.05 \\cdot 0.95 + 0.055 \\cdot 0.945) "
        "= 7.84 \\cdot 0.0995 \\approx 0.780$",
        "- 分母: $(0.005)^2 = 2.5 \\times 10^{-5}$",
        "- $n \\approx 31{,}200$ 每组",
        "**两均值版本**: $n = \\dfrac{2(z_{\\alpha/2}+z_\\beta)^2 \\sigma^2}{\\delta^2}$ 每组",

        "**Q12. 单尾 vs 双尾?**",
        "- 双尾: 你只关心\"有没有差异\" -> 默认选这个",
        "- 单尾: 你**事先**有方向假设 (且对反方向不感兴趣) -> 临界值变小, 更易显著",
        "- 业务上**几乎都用双尾**, 因为反方向的结果你不可能忽略",

        "**Q13. t-test vs z-test 怎么选?**",
        "- z-test: $\\sigma$ 已知, 或 $n$ 大 (一般 $\\geq 30$)",
        "- t-test: $\\sigma$ 未知, 小样本",
        "- 实务中 A/B test 几乎都是大样本, 两者几乎等价",

        "**Q14. 多重比较问题?**",
        "做 $m$ 个独立检验, 假设全部 $H_0$ 真, 至少一个 false positive 的概率:",
        FormulaBlock(
            latex=r"P(\text{at least 1 FP}) = 1 - (1-\alpha)^m \xrightarrow{m=20,\,\alpha=0.05} 0.64",
            explanation="20 次独立检验在 alpha=0.05 下至少一次假阳的概率高达 64%",
        ),
        "**修正方法**:",

        "| 方法 | 思路 | 特点 |",
        "|---|---|---|",
        "| Bonferroni | $\\alpha_{adj} = \\alpha/m$ | 保守, 控制 FWER |",
        "| Holm-Bonferroni | 排序后逐步 | 比 Bonferroni 强 |",
        "| Benjamini-Hochberg (BH) | 控制 FDR (错误发现比例期望) | 大规模检验首选 |",

        "**FWER vs FDR**: FWER 控制\"任何一个误拒\"的概率; "
        "FDR 控制\"误拒占所有拒绝中的比例\"。基因组学、广告 metric 海量比较时用 FDR。",
    ])

    b.add_section("Part 1 · 4. 方差缩减 (Variance Reduction)", [
        "**Q15. CUPED 原理?**",
        "**目的**: 用实验前数据 (pre-period covariate) 抵消用户基线差异, "
        "减小指标方差, 从而用更小样本量获得同等 power。",
        "**公式**:",
        FormulaBlock(
            latex=r"Y^{\text{cuped}} = Y - \theta(X - E[X])",
            explanation="CUPED 调整后的指标: 减去与 pre-period covariate 相关的部分",
        ),
        "最优 $\\theta = \\dfrac{\\text{Cov}(Y, X)}{\\text{Var}(X)}$ "
        "(其实就是 $Y$ 对 $X$ 的回归斜率)",
        "**方差缩减比例**:",
        FormulaBlock(
            latex=r"\text{Var}(Y^{\text{cuped}}) = \text{Var}(Y)(1 - \rho^2)",
            explanation="方差缩减率: rho 是 Y 与 X 的相关系数",
        ),
        "其中 $\\rho$ 是 $Y$ 和 $X$ 的相关系数。"
        "如果用户实验前后行为相关性 $\\rho=0.7$, 方差降 51%, 等价于约 2 倍样本量。",
        "**关键约束**: $X$ 必须**与处理变量独立** (用 pre-period 数据保证)。"
        "否则会引入偏差。",

        "**Q16. 其他方差缩减手段?**",
        "- **分层抽样 (Stratification)**: 按用户类型分层后取均值",
        "- **回归调整 (Regression adjustment)**: ANCOVA, CUPED 的更一般形式",
        "- **配对实验 (Paired design)**: 同一用户 before/after",
    ])

    b.add_section("Part 1 · 5. 回归分析 (Regression Analysis)", [
        "**Q17. OLS 公式和假设?**",
        "模型: $y = X\\beta + \\epsilon$, $\\epsilon \\sim N(0, \\sigma^2 I)$",
        "闭式解:",
        FormulaBlock(
            latex=r"\hat{\beta} = (X^T X)^{-1} X^T y",
            explanation="OLS 闭式解 (normal equation)",
        ),
        "**Gauss-Markov 假设 (LINE)**:",
        "- **L**inearity: $y$ 与 $X$ 的关系是线性的",
        "- **I**ndependence: $\\epsilon_i$ 独立",
        "- **N**ormality of residuals (只为做推断, 不为估计)",
        "- **E**qual variance (homoscedasticity)",
        "- 加: 无完美多重共线性 ($X^T X$ 可逆)",

        "**Q18. 怎么解释回归系数?**",
        "$\\beta_j$: **其他变量不变**时, $x_j$ 每增加 1 单位, "
        "$y$ 平均增加 $\\beta_j$ 单位。",
        "是**条件**关系而非边际关系, **不是因果**。",
        "**标准化系数** (z-score 化输入): 可跨变量比较\"哪个特征影响更大\"。",

        "**Q19. R^2 公式和陷阱?**",
        FormulaBlock(
            latex=r"R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}",
            explanation="R^2 = 1 - 残差平方和 / 总平方和",
        ),
        FormulaBlock(
            latex=r"\bar{R}^2 = 1 - \frac{(1-R^2)(n-1)}{n - p - 1}",
            explanation="Adjusted R^2: 对特征数 p 做惩罚, 避免无脑加特征",
        ),
        "**陷阱**:",
        "- $R^2$ 高 != 模型好 (可能过拟合)",
        "- $R^2$ 低 != 模型差 (噪声数据本就上限低)",
        "- 加任何特征 $R^2$ 都不会下降 -> 必须看 adjusted $R^2$ 或 hold-out",

        "**Q20. Logistic regression?**",
        FormulaBlock(
            latex=r"P(y=1 \mid x) = \sigma(x^T\beta) = \frac{1}{1 + e^{-x^T\beta}}",
            explanation="Logistic 回归: sigmoid(线性组合) = 类别 1 的概率",
        ),
        "Log-odds 形式 (最容易解释):",
        FormulaBlock(
            latex=r"\log\frac{p}{1-p} = x^T\beta",
            explanation="logit 函数将 (0,1) 上的概率映射到整个实数轴",
        ),
        "**系数解释**: $x_j$ 增加 1 -> log-odds 增加 $\\beta_j$ -> "
        "**odds 乘以 $e^{\\beta_j}$**",
        "损失 (cross-entropy / log-loss):",
        FormulaBlock(
            latex=r"\mathcal{L} = -\frac{1}{n}\sum_i \big[y_i \log \hat{p}_i + (1-y_i)\log(1-\hat{p}_i)\big]",
            explanation="交叉熵损失, 等价于 MLE 的负对数似然",
        ),
        "无闭式解, 用 IRLS 或梯度下降求 MLE。",

        "**Q21. 多重共线性 (Multicollinearity)?**",
        "- 检测: $\\text{VIF}_j = 1/(1 - R_j^2)$, VIF > 10 通常视为严重",
        "- 后果: 系数不稳、SE 膨胀 (但预测仍可能 OK)",
        "- 处理: 删除冗余特征、PCA、Ridge 回归",
    ])

    b.add_section("Part 1 · 6. CI vs PI (置信区间 vs 预测区间)", [
        "**Q22. 区别?**",

        "| | 描述对象 | 公式 (回归预测点 $x_0$) |",
        "|---|---|---|",
        "| CI | **均值**的不确定性 | $\\hat{y}_0 \\pm t \\cdot \\sigma\\sqrt{\\frac{1}{n} + \\frac{(x_0-\\bar{x})^2}{S_{xx}}}$ |",
        "| PI | **单个新观测**的不确定性 | $\\hat{y}_0 \\pm t \\cdot \\sigma\\sqrt{1 + \\frac{1}{n} + \\frac{(x_0-\\bar{x})^2}{S_{xx}}}$ |",

        "PI 比 CI 多了\"$+1$\"项 (个体随机误差), 所以**总是更宽**。",
    ])

    b.add_section("Part 1 · 7. Bias-Variance Tradeoff", [
        "**Q23. 分解公式?**",
        FormulaBlock(
            latex=r"E\!\left[(\hat{f}(x) - y)^2\right] = \underbrace{(E[\hat{f}(x)] - f(x))^2}_{\text{bias}^2} + \underbrace{\text{Var}(\hat{f}(x))}_{\text{variance}} + \underbrace{\sigma^2}_{\text{irreducible}}",
            explanation="期望平方误差 = 偏差平方 + 方差 + 不可约误差",
        ),
        "- High bias = underfit (模型太简单)",
        "- High variance = overfit (模型太复杂、数据不够)",
        "- L1/L2 正则化、bagging 降 variance; boosting 降 bias",
    ])

    b.add_section("Part 1 · 8. 不平衡分类: AUC vs PR-AUC", [
        "**Q24. 为什么不平衡数据要看 PR-AUC?**",
        "- **ROC-AUC**: TPR vs FPR; 与类别比例**无关**",
        "- **PR-AUC**: Precision vs Recall; **对正类比例敏感**",
        "**反直觉例子**: 1% 正例, 模型 TPR=0.9, FPR=0.05 -> 看似不错。但:",
        "- TP = $0.9 \\times 100 = 90$",
        "- FP = $0.05 \\times 9900 = 495$",
        "- Precision = $90 / (90+495) = $ **15%**",
        "ROC 看起来漂亮 (AUC 可能 0.95+), 实际预测 100 个正例只对 15 个。"
        "**当你关心正类预测的可信度时, 用 PR-AUC**。",
        "**经验规则**: 极不平衡 (如 < 5% 正例)、欺诈检测、点击预测 -> PR-AUC 主导。",
    ])

    b.add_section("Part 1 · 9. 缺失值处理 (Missing Data)", [
        "**Q25. 缺失机制三类?**",
        "- **MCAR** (Missing Completely at Random): 缺失与任何变量无关 -> 删除安全",
        "- **MAR** (Missing at Random): 缺失依赖**观测到的**其他变量 -> 可建模填补",
        "- **MNAR** (Missing Not at Random): 缺失依赖**未观测的值本身** "
        "-> 最棘手 (如高收入者不报收入)",

        "**Q26. 常用方法及陷阱?**",

        "| 方法 | 优点 | 陷阱 |",
        "|---|---|---|",
        "| 删除 (listwise) | 简单 | 损失数据, 仅 MCAR 无偏 |",
        "| 均值/中位数填补 | 简单 | 低估方差、削弱相关性 |",
        "| 回归填补 | 利用相关 | 低估方差 (确定性预测) |",
        "| Multiple Imputation (MICE) | 反映不确定性 | 实现复杂 |",
        "| 加 missing indicator | 保留\"缺失\"信息 | 共线性风险 |",
        "| Tree-based 原生处理 | XGBoost/LightGBM 直接支持 | 无 |",

        "**Q27. EM 算法在缺失值上怎么用?**",
        "E-step: 用当前参数估计填补缺失值 (条件期望); "
        "M-step: 用填补后的完整数据更新参数。迭代直到收敛。",
    ])

    b.add_section("Part 1 · 10. 没实验也能做因果推断 (Causal Inference)", [
        "**Q28. 主要方法对比?**",

        "| 方法 | 核心假设 | 适用 |",
        "|---|---|---|",
        "| **DiD** (Difference-in-Differences) | 平行趋势 (parallel trends) | 政策/特性 rollout 前后对比 |",
        "| **RDD** (Regression Discontinuity) | 阈值附近其他变量连续 | 有 cutoff 的场景 (e.g. 资格分数线) |",
        "| **IV** (Instrumental Variable) | $Z$ 影响 $T$ 但不直接影响 $Y$ | 有外生变量时 |",
        "| **PSM** (Propensity Score Matching) | 可观测变量上无未观测混淆 | 观察数据对比 |",
        "| **Synthetic Control** | 加权 control 单元 -> 反事实 | 单一处理单元 (e.g. 一个城市) |",
        "| **Doubly Robust** | 结合 outcome 模型 + propensity | 任一模型正确就一致 |",

        "**Q29. 混淆变量 (Confounder) 是什么?**",
        "同时影响处理 $T$ 和结果 $Y$ 的变量。"
        "不控制就会让相关性 != 因果。",
        "> 例: \"冰淇淋销量\"和\"溺水\"高度相关 -> 共同混淆是\"夏季\"。",

        "**Q30. Simpson 悖论 (Simpson's Paradox)?**",
        "聚合数据上的相关方向, 可能在分组数据上**整体反转**。",
        "> UC Berkeley 男女录取经典案例: 聚合看男生录取率高, "
        "按系分组看女生录取率高 (女生更多申请竞争激烈的系)。",
    ])

    b.add_section("Part 1 · 11. 概率应用题 (高频)", [
        "**Q31. Bayes 定理 (贝叶斯)**",
        FormulaBlock(
            latex=r"P(A \mid B) = \frac{P(B \mid A)\, P(A)}{P(B)}",
            explanation="贝叶斯公式: 后验 = 似然 x 先验 / 证据",
        ),
        "**经典疾病检测题**: 患病率 1%, 检测敏感度 99% (TPR), 特异度 95% ($1 - \\text{FPR}$)。"
        "检测阳性, 实际患病的概率?",
        FormulaBlock(
            latex=r"P(D \mid +) = \frac{P(+ \mid D)\, P(D)}{P(+ \mid D)\, P(D) + P(+ \mid \neg D)\, P(\neg D)}",
            explanation="贝叶斯公式展开 (全概率公式做分母)",
        ),
        FormulaBlock(
            latex=r"= \frac{0.99 \times 0.01}{0.99 \times 0.01 + 0.05 \times 0.99} = \frac{0.0099}{0.0594} \approx 16.7\%",
            explanation="代入数值: 真阳 0.0099, 总阳性 0.0594, 后验仅约 16.7%",
        ),
        "**直觉**: 真实患者 99 个 vs 误检的 495 个, 后者远多于前者 -> **base rate fallacy**。",

        "**Q32. 蓄水池抽样 (Reservoir Sampling)?**",
        "从流式数据中均匀采样 $k$ 个, 不知道总长。"
        "第 $i$ 个元素 ($i > k$) 以 $k/i$ 概率替换池中随机一个。"
        "每个元素最终被选中的概率为 $k/n$。",

        "**Q33. 生日问题**",
        "23 人中至少两人同生日的概率 > 50%。",
        FormulaBlock(
            latex=r"P(\text{at least 2 share}) = 1 - \frac{365! / (365-n)!}{365^n}",
            explanation="生日悖论: 反向计算 (1 - 全部不同的概率)",
        ),
        "直觉: 配对数 $\\binom{23}{2} = 253$, 比看起来多得多。",
    ])

    # ============================================================
    # PART 2: RAG FULL-STACK
    # ============================================================

    b.add_section("Part 2 · 1. Chunking 策略", [
        "**Q34. 主流切块方式?**",

        "| 策略 | 描述 | 适用 |",
        "|---|---|---|",
        "| Fixed-size | 固定 token 数 (512) + overlap (10-20%) | 通用 baseline |",
        "| Sentence-aware | 不在句中切 | 短问答 |",
        "| Recursive | 按段落 -> 句 -> 词层级回退 | LangChain 默认 |",
        "| Semantic chunking | 用 embedding 相似度找断点 | 主题切换明显的文档 |",
        "| Document structure | 按 heading (markdown/HTML) | 技术文档、wiki |",
        "| Hierarchical (parent-child) | 检索小块、返回大块上下文 | 长文档 QA |",
        "| Code-aware | 用 AST 按函数/类切 | 代码库 |",
        "| Table-aware | 整张表/按行切 + 表头保留 | 财报、技术规格 |",

        "**Q35. Chunk size 怎么选?**",
        "- 太小: 单块语义不完整, retrieve 时召回散乱",
        "- 太大: embedding 被噪声稀释, 精度下降; 上下文窗口浪费",
        "- 经验起点: **256-512 token, 50-100 overlap**",
        "- **必须**通过 retrieval recall/MRR 在 golden set 上调优, 不能拍脑袋",

        "**Q36. 怎么衡量 chunking 效果?**",
        "构建 (query, gold chunk_id) 数据集, 对比不同 chunking 策略下 Recall@k、MRR、NDCG。"
        "同时**端到端**看 answer correctness, 因为 retrieval 好不代表生成好。",
    ])

    b.add_section("Part 2 · 2. Embedding 模型选型", [
        "**Q37. 选 embedding 看什么?**",
        "- **任务类型**: asymmetric (query 短/doc 长) vs symmetric "
        "-- 选对应训练的模型 (如 BGE 有专门 query prefix)",
        "- **领域**: 通用 / 代码 (CodeBERT, text-embedding) / 多语言 (BGE-M3, multilingual-e5) "
        "/ 医疗 (BioBERT)",
        "- **维度 vs 性能**: 768 / 1024 / 3072; Matryoshka 嵌入可截断",
        "- **context length**: 短文 512 vs 长文 8k (jina, voyage-large)",
        "- **MTEB 榜单**: 但**不要直接信榜单分数**, 必须在自己数据上验证",
        "- **成本**: 自部署开源 (bge, e5, gte) vs API (OpenAI, Cohere, Voyage)",

        "**Q38. 怎么验证 embedding 在你的数据上好不好?**",
        "1. 人工标注 200-500 条 (query, relevant_doc) 对",
        "2. 用 LLM 合成数据补充 (对每篇文档生成假设性问题)",
        "3. 算 Recall@10, MRR, NDCG@10",
        "4. 对比 2-3 个候选 embedding 在同一索引上的表现",
        "5. 不要只看 cosine 平均值, 要看排序质量",

        "**Q39. 常用模型一览 (2024-2025)**",

        "| 模型 | 维度 | 特点 |",
        "|---|---|---|",
        "| OpenAI text-embedding-3-large | 3072 (可裁) | 通用强, 闭源 |",
        "| Voyage-3 | 1024 | 检索质量顶尖 |",
        "| Cohere embed-v3 | 1024 | 多语言, 便宜 |",
        "| BGE-M3 | 1024 | 开源、多语、long doc |",
        "| E5-mistral-7b-instruct | 4096 | 大但贵 |",
        "| Nomic embed | 768 | 开源轻量 |",
    ])

    b.add_section("Part 2 · 3. 向量数据库 (Vector DB)", [
        "**Q40. 主流向量库对比?**",

        "| 库 | 优点 | 缺点 |",
        "|---|---|---|",
        "| **pgvector** | 同库 SQL filter, ACID, 运维简单 | 大规模慢 (>10M) |",
        "| **Pinecone** | Fully managed, 快 | 贵, vendor lock-in |",
        "| **Weaviate** | Hybrid search 原生, 模块化 | 资源占用大 |",
        "| **Qdrant** | Rust, 强大 filtering | 生态较新 |",
        "| **Milvus** | 超大规模 (10B+) | 复杂运维 |",
        "| **FAISS** | 库不是服务, 极快 | 无持久化/分布式 |",

        "**选型决策树**:",
        "- < 1M 向量 + 已有 Postgres -> **pgvector**",
        "- 不想运维 -> **Pinecone**",
        "- 需要复杂 metadata filtering -> **Qdrant / Weaviate**",
        "- 需要 hybrid (BM25 + dense) -> **Weaviate / Elasticsearch + vectors**",
        "- 单机 prototype -> **FAISS / Chroma**",

        "**Q41. 索引类型?**",

        "| 索引 | 原理 | 内存 | 速度 |",
        "|---|---|---|---|",
        "| Flat (brute force) | 全量计算 | 高 | 慢但 100% recall |",
        "| HNSW | 多层图, 贪心搜索 | 高 | 最常用, 快 |",
        "| IVF | 先聚类再搜对应簇 | 中 | 快, 略损 recall |",
        "| IVF + PQ (Product Quantization) | 聚类+量化压缩 | 低 | 大规模首选 |",

        "**关键参数 (HNSW)**: `M` (连接数, 越大召回越好但内存大), "
        "`ef_construction` (建索引质量), `ef_search` (查询时召回 vs 速度 trade-off)。",
    ])

    b.add_section("Part 2 · 4. Re-ranker (重排)", [
        "**Q42. 为什么要重排?**",
        "- Bi-encoder (embedding 模型) 独立编码 query 和 doc, 速度快但语义匹配粗",
        "- Cross-encoder 把 query 和 doc **拼起来一起进 Transformer**, 语义对齐更细, 但 N 倍慢",
        "- **两阶段**: bi-encoder 召回 top-100, cross-encoder 重排 top-10",

        "**Q43. 常用 re-ranker?**",
        "- **Cohere Rerank v3**: API, 强大稳定",
        "- **bge-reranker-large / v2-m3**: 开源",
        "- **jina-reranker-v2**: 多语言",
        "- **LLM-as-reranker**: 用 GPT-4o/Claude 给候选打分 (成本高, 质量上限高)",

        "**Q44. ColBERT 和 cross-encoder 区别?**",
        "ColBERT 是 **late-interaction**: 每个 token 单独 embed, 查询时用 MaxSim 算交互。"
        "介于 bi-encoder (快但粗) 和 cross-encoder (精但慢) 之间。",
    ])

    b.add_section("Part 2 · 5. Query Rewriting / Transformation", [
        "**Q45. 常用技术?**",
        "- **HyDE** (Hypothetical Document Embeddings): 让 LLM 写一个**假设性答案**, "
        "对这个假答案做 embedding 检索。对长尾、抽象 query 提升明显",
        "- **Multi-query**: 让 LLM 生成 3-5 个改写, 取检索结果并集 -> 提升 recall",
        "- **Query decomposition**: 复杂问题拆成子问题分别检索 (如多跳问答)",
        "- **Step-back prompting**: 先抽象出上位概念再检索 "
        "(\"这个 API 怎么用\" -> \"API 文档结构\")",
        "- **历史改写**: 多轮对话中把指代消解掉 "
        "(\"它有什么参数\" -> \"X 函数有什么参数\")",
    ])

    b.add_section("Part 2 · 6. Guardrails (护栏)", [
        "**Q46. RAG 系统四层护栏?**",
        "**1. 输入层**:",
        "   - Prompt injection 检测 (Llama Guard, Lakera, NeMo Guardrails)",
        "   - PII 检测/脱敏 (Presidio)",
        "   - 主题分类 (拒绝 off-topic)",
        "**2. 检索层**:",
        "   - Metadata 过滤 (user role / ACL)",
        "   - 检索结果数量上限",
        "   - 拒绝低置信检索 (top score 阈值)",
        "**3. 生成层**:",
        "   - System prompt 强约束 (\"only answer based on provided context\")",
        "   - Citation enforcement (强制引用 chunk_id)",
        "   - Faithfulness check (生成内容是否真的来自 retrieved doc)",
        "**4. 输出层**:",
        "   - Toxicity / 不当内容 (Perspective API)",
        "   - PII 泄漏检查",
        "   - Hallucination 检测 (NLI 模型验证 claim ⊂ context)",

        "**Q47. Prompt injection 怎么防?**",
        "- 用 system prompt 和 user input **严格分离**",
        "- 检测明显 injection 模式 (\"ignore previous instructions\")",
        "- 用 LLM-as-judge 检测意图",
        "- 文档内容也可能含 injection (**indirect prompt injection**) "
        "-> 必须 sanitize 检索结果",
    ])

    b.add_section("Part 2 · 7. RAG Evaluation", [
        "**Q48. Retrieval 怎么评?**",
        "构建 golden set: `(query, relevant_chunk_ids)`",
        "- **Recall@k**: 召回到的相关 chunk 占全部相关 chunk 的比例",
        "- **Precision@k**: top-k 中相关 chunk 的比例",
        "- **MRR (Mean Reciprocal Rank)**:",
        FormulaBlock(
            latex=r"\text{MRR} = \frac{1}{|Q|}\sum_{q \in Q} \frac{1}{\text{rank of first relevant}}",
            explanation="平均倒数排名: 首个相关结果的位置越靠前, MRR 越高",
        ),
        "- **NDCG@k**: 有分级相关性时用 (很相关 = 3, 相关 = 1, 不相关 = 0)",

        "**Q49. End-to-end 怎么评? (RAGAS 框架)**",
        "- **Faithfulness**: 生成的每个 claim 是否能在 retrieved context 中找到支持",
        "- **Answer Relevance**: 答案是否回答了 query",
        "- **Context Precision**: top-k 中真正用上的比例",
        "- **Context Recall**: 回答 ground truth 所需的信息有多少在 context 里",
        "- **Answer Correctness**: 与参考答案对比 (语义+事实)",

        "**Q50. 怎么构建 golden dataset?**",
        "- **冷启动**: 用 GPT-4o/Claude 对每篇 doc 生成 3-5 个问题 + 答案 -> 人工筛选",
        "- **生产数据**: 收集线上 query, 让标注员标 relevant chunks",
        "- **持续迭代**: 把 bad case (用户点踩、低 confidence) 加入 eval set",
    ])

    b.add_section("面试小贴士 (Interview Tips)", [
        "**统计题被问到时常见陷阱**:",
        "- 公式说出来 + **直觉解释** + 一个**反例或边界 case**, 三件套别忘",
        "- 不要装懂 -- 不会就说\"我不确定, 但我会这样推导...\"",
        "- A/B test 题永远先问 metric, baseline, MDE, $\\alpha/\\beta$ 五要素",

        "**RAG 题被问到时**:",
        "- 永远先问业务场景 (短问答 vs 长文档总结 vs 代码搜索完全不同方案)",
        "- 给具体的**调参经验** (chunk size 我从 256 试到 1024) 会比说\"看情况\"显得专业得多",
        "- 谈到 evaluation 是大加分项 -- 多数候选人只会说 \"用 LLM 评\"",
    ])

    b.add_checklist("Self-Check Questions", [
        "写出样本方差公式并解释 n-1 (Bessel's correction) 的原因",
        "区分 SE 和 SD; 写出均值标准误 SE = s/sqrt(n)",
        "解释 95% CI 的正确含义 + 最常见误解 (区间是随机的, 不是参数)",
        "写出 A/B test 两比例样本量公式 + 用 baseline=5%, MDE=0.5% 跑一遍 (~31200/组)",
        "解释 Power = 1-beta 及影响 Power 的 4 个因素 (样本量/effect/方差/alpha)",
        "Bonferroni vs Holm-Bonferroni vs BH; 何时选 FDR 而非 FWER",
        "CUPED 公式 + 解释 rho=0.7 时方差降 51% 的来源",
        "Logistic regression 系数的 odds-ratio 解释; 损失为何用 cross-entropy",
        "VIF 公式 + 阈值 (>10 严重); 多重共线性 3 种处理方式",
        "CI vs PI 公式差异 (PI 多 +1 项); 为什么 PI 总是更宽",
        "Bias-variance 分解公式 + L1/L2/bagging/boosting 各自的作用",
        "1% 正例 + TPR=0.9, FPR=0.05 算 precision (~15%); 解释为何用 PR-AUC",
        "MCAR / MAR / MNAR 三类缺失机制 + 各自合适的处理方式",
        "DiD / RDD / IV / PSM / Synthetic Control 各自的核心假设",
        "Simpson 悖论 + UC Berkeley 录取经典案例",
        "贝叶斯疾病检测题: 患病率 1%, 敏感度 99%, 特异度 95% -> 阳性后患病约 16.7%",
        "8 种 chunking 策略 + 经验起点 256-512 token + 50-100 overlap",
        "选 embedding 看的 6 个维度 (任务/领域/维度/长度/MTEB/成本)",
        "向量库选型决策树 (pgvector / Pinecone / Qdrant / Weaviate / FAISS)",
        "HNSW 的 M / ef_construction / ef_search 参数含义",
        "Bi-encoder vs Cross-encoder vs ColBERT 三种 retrieval 范式区别",
        "HyDE / Multi-query / Decomposition / Step-back 四种 query rewriting",
        "RAG 四层护栏 (输入/检索/生成/输出); indirect prompt injection 怎么防",
        "Recall@k / Precision@k / MRR / NDCG 公式 + 何时用 NDCG",
        "RAGAS 五指标 (Faithfulness / Answer Relevance / Context Precision/Recall / Answer Correctness)",
    ])

    return b


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    builder = build_note()
    content_body = builder.build()
    # Prepend sentinel as first line for idempotent UPSERT detection.
    content = f"{SENTINEL}\n{content_body}"

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        # Idempotent: delete any existing row matching either the title or
        # sentinel. The sentinel is the canonical id; title catches stale rows
        # from earlier draft runs that may not have included it.
        existing = conn.execute(
            "SELECT id FROM company_documents "
            "WHERE company_id = ? AND (title = ? OR content LIKE ?)",
            (COMPANY_ID, DOC_TITLE, f"{SENTINEL}%"),
        ).fetchall()
        for row in existing:
            conn.execute("DELETE FROM company_documents WHERE id = ?", (row[0],))
            print(f"[CLEAN] Deleted prior row id={row[0]}")

        conn.execute(
            "INSERT INTO company_documents "
            "(company_id, title, content, source_type) VALUES (?, ?, ?, ?)",
            (COMPANY_ID, DOC_TITLE, content, "manual"),
        )
        conn.commit()

        doc = conn.execute(
            "SELECT id, length(content) FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        ).fetchone()
        print(
            f"[DONE] Inserted document id={doc[0]}, "
            f"title='{DOC_TITLE}', content_length={doc[1]} chars"
        )

        warnings = StudyNoteBuilder.validate(content)
        if warnings:
            for w in warnings:
                print(f"[WARN] {w}")
        else:
            print("[DONE] 0 validation warnings")

        section_count = content.count("\n## ")
        term_count = len(builder._terms)
        formula_count = content.count("$$")
        print(
            f"[INFO] {section_count} sections, {term_count} terms, "
            f"{formula_count // 2} display formulas, {len(content)} chars, "
            f"sentinel='{SENTINEL}'"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
