"""T-P1-456: Matrix Factorization -> Two-Tower bridge.

Expands framework_node id=108 (Collaborative Filtering) description with:
(1) MF evolution narrative: Bias-only -> Funk-SVD (PMF) -> Biased-MF
(2) Explicit SGD vs ALS training trade-off (online-friendly vs
    closed-form/parallelizable/offline)
(3) The conceptual bridge: MF is the ancestor of Two-Tower -- same
    user_emb . item_emb dot product, but with learned towers instead of
    fixed ID-lookup embeddings.

Also upserts a standalone docs/mf_to_two_tower_bridge.md and a Google
company_document that references the existing Two-Tower Retrieval Deep
Dive (doc id=64). We do NOT re-derive InfoNCE / sampled-softmax here --
that is deferred to doc 64.

Pyramid: mid (~1500 words). Complexity: S.

Idempotent: re-runs UPDATE the framework_node description, the markdown
file, and upsert the company_document by (company_id, title).

Usage::

    python scripts/seed_mf_to_two_tower_bridge_20260416.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"
DOC_MD_PATH = ROOT / "docs" / "mf_to_two_tower_bridge.md"

GOOGLE_COMPANY_ID = 3  # matches doc 64's company_id
DOC_TITLE = "MF to Two-Tower Bridge (Funk-SVD -> Biased-MF -> Dual Encoders)"

NODE_ID = 108  # pillar4.recommender_systems.collaborative_filtering


# ==========================================================================
# Framework node description (replaces existing node 108 description)
# ==========================================================================

NODE_DESCRIPTION = """# Collaborative Filtering

## Overview

**Collaborative Filtering（协同过滤）** 是推荐系统的核心方法，广泛应用于各大科技公司（Netflix、Spotify、Amazon等）。其核心思想是：通过大量用户的集体行为模式来预测单个用户的偏好。协同过滤不需要了解物品本身的内容特征，而是利用"相似用户喜欢相似物品"这一基本假设。

资深MLE必须掌握**Memory-Based（基于记忆）** 和 **Model-Based（基于模型）** 两大类协同过滤方法，理解它们的可扩展性权衡，以及驱动混合方法发展的**Cold-Start Problem（冷启动问题）**。同时必须理解 **MF（矩阵分解）-> Two-Tower（双塔）** 的演化脉络——Two-Tower 本质上是 MF 的自然延伸，把固定 ID 查表换成了学习的编码器塔。

## Core Concepts

### User-Item Interaction Matrix

给定 $$m$$ 个用户和 $$n$$ 个物品，定义交互矩阵 $$R \\in \\mathbb{R}^{m \\times n}$$，其中 $$r_{ui}$$ 表示用户 $$u$$ 对物品 $$i$$ 的评分（或隐式信号）。在实际场景中，$$R$$ 极度稀疏（通常填充率 $$< 1\\%$$），这是协同过滤面临的根本挑战。

### Memory-Based CF

**User-Based（基于用户的协同过滤）**：找到与目标用户 $$u$$ 相似的用户集合，聚合他们的评分作为预测：

$$
\\hat{r}_{ui} = \\bar{r}_u + \\frac{\\sum_{v \\in \\mathcal{N}(u)} \\text{sim}(u, v)(r_{vi} - \\bar{r}_v)}{\\sum_{v \\in \\mathcal{N}(u)} |\\text{sim}(u, v)|}
$$

其中 $$\\bar{r}_u$$ 是用户 $$u$$ 的平均评分，$$\\mathcal{N}(u)$$ 是与用户 $$u$$ 最相似的邻居集合。公式通过减去均值来消除用户评分尺度的差异。

**Item-Based（基于物品的协同过滤）**：找到与物品 $$i$$ 相似的物品集合，聚合用户对这些相似物品的评分。实践中 Item-Based 通常比 User-Based 更稳定（物品相似度随时间变化慢），Amazon 的推荐系统就是基于 Item-Based CF 构建。

**Cosine Similarity（余弦相似度）** 是最常用的相似度度量：

$$
\\text{sim}(u, v) = \\frac{\\mathbf{r}_u \\cdot \\mathbf{r}_v}{\\|\\mathbf{r}_u\\| \\|\\mathbf{r}_v\\|}
$$

### Model-Based CF: MF 演化三步走（Bias-only -> Funk-SVD -> Biased-MF）

理解 MF 最好的方式是看它从简单基线如何一步步长出来的。

**Step 1. Bias-only baseline（只有偏置）**：用全局平均 + 用户偏置 + 物品偏置预测评分，没有任何潜在因子：

$$
\\hat{r}_{ui} = \\mu + b_u + b_i
$$

$$\\mu$$ 是全局平均评分，$$b_u$$ 捕捉 "这个用户普遍打高分 / 低分"，$$b_i$$ 捕捉 "这个物品普遍被喜欢 / 被讨厌"。Netflix Prize 起手这套基线就能 RMSE ~0.97，比 user/item avg 强 ~3%。

**Step 2. Funk-SVD / PMF（纯内积潜在因子）**：Simon Funk 在 Netflix Prize 期间提出，Salakhutdinov & Mnih 用概率视角重新包装成 PMF。核心是 $$R \\approx P Q^T$$：

$$
\\hat{r}_{ui} = \\mathbf{p}_u^T \\mathbf{q}_i
$$

$$P \\in \\mathbb{R}^{m \\times k}$$ 是用户嵌入矩阵，$$Q \\in \\mathbb{R}^{n \\times k}$$ 是物品嵌入矩阵，$$k \\in [50, 200]$$。**PMF 视角**：把 $$\\mathbf{p}_u, \\mathbf{q}_i$$ 看作零均值高斯先验，$$r_{ui}$$ 在 $$\\mathbf{p}_u^T \\mathbf{q}_i$$ 附近高斯噪声，$$\\ell_2$$ 正则 = MAP。

**Step 3. Biased-MF（两者合体，行业主力）**：加回偏置项，同时保留潜在因子内积。这是 Koren 2009 综述的标准形式，实际用于 Netflix / Spotify 生产系统：

$$
\\hat{r}_{ui} = \\mu + b_u + b_i + \\mathbf{p}_u^T \\mathbf{q}_i
$$

**训练目标函数**：

$$
\\min_{P, Q, b} \\sum_{(u,i) \\in \\Omega} \\left(r_{ui} - \\hat{r}_{ui}\\right)^2 + \\lambda\\left(\\|\\mathbf{p}_u\\|^2 + \\|\\mathbf{q}_i\\|^2 + b_u^2 + b_i^2\\right)
$$

**为什么要分三步**：(a) 教学上清晰——每一步只添加一种建模能力；(b) 工程上偏置项吸收了 "尺度效应"（scale effect），让 $$\\mathbf{p}_u, \\mathbf{q}_i$$ 专注学 "口味差异"（taste dimension），训练更稳；(c) 面试上能讲清楚演化顺序是区分背过公式 vs 真正理解的关键信号。

### SGD vs ALS 训练差异（面试高频对比）

Biased-MF 有两种主流训练方式，它们的选择不是口味问题，而是对应不同的生产场景。

**SGD（随机梯度下降）** 更新规则（以 $$\\mathbf{p}_u$$ 为例）：

$$
\\mathbf{p}_u \\leftarrow \\mathbf{p}_u + \\eta (e_{ui} \\mathbf{q}_i - \\lambda \\mathbf{p}_u)
$$

其中 $$e_{ui} = r_{ui} - \\hat{r}_{ui}$$ 是预测误差。**特性**：mini-batch 级别更新，有噪声但**在线友好**——新评分一来就能增量更新一条样本，不需要重扫整个矩阵；实现简单；对学习率 $$\\eta$$ 敏感。适合**流式 / 近实时**场景。

**ALS（交替最小二乘）** 闭式解，固定 $$Q$$ 解 $$\\mathbf{p}_u$$：

$$
\\mathbf{p}_u = (Q_{\\Omega_u}^T Q_{\\Omega_u} + \\lambda I)^{-1} Q_{\\Omega_u}^T \\mathbf{r}_u
$$

**特性**：每一个 user / item block 内部独立可并行（Spark MLlib 的 ALS 实现就是这么干的），无学习率超参，收敛更确定；但每步要反解 $$k \\times k$$ 线性系统，只适合**批量 / 离线**重训练。Netflix Prize 冠军队伍、Spotify 每日离线训练都用 ALS。

**速查对比**：

| 维度 | SGD | ALS |
|---|---|---|
| 更新粒度 | mini-batch / 单样本 | user / item block 级闭式 |
| 并行性 | 难并行（样本间有冲突） | 天然并行（block 独立） |
| 在线增量 | **支持**（新评分即时更新） | 不支持（需全量重训） |
| 超参 | 学习率 $$\\eta$$ 敏感 | 无 $$\\eta$$（但 $$\\lambda$$ 仍需调） |
| 收敛速度 | 噪声大、需多 epoch | 每步精确、epoch 数少 |
| 适用场景 | 流式 / 低延迟再训 | 离线批量 / 超大矩阵分布式 |

### Implicit Feedback + BPR

隐式反馈（点击/浏览/购买）用 **Weighted ALS**（每对交互加置信度权重 $$c_{ui} = 1 + \\alpha r_{ui}$$）或 **BPR（Bayesian Personalized Ranking）** 成对排序损失：

$$
\\mathcal{L}_{\\text{BPR}} = -\\sum_{(u,i,j)} \\ln \\sigma(\\hat{r}_{ui} - \\hat{r}_{uj}) + \\lambda \\|\\Theta\\|^2
$$

BPR 直接优化 "用户偏好正样本 $$i$$ 胜过负样本 $$j$$"，更匹配 Top-N 推荐场景。

## 从 MF 到 Two-Tower：桥梁与演化

**关键洞察**：Biased-MF 的打分函数 $$\\hat{r}_{ui} = \\mathbf{p}_u^T \\mathbf{q}_i + \\text{biases}$$ 和现代 **Two-Tower（双塔 / Dual Encoder）** 检索的打分函数 **本质相同**——都是用户 embedding 和物品 embedding 的点积。区别不在打分，而在 embedding 的来源：

- **MF**：$$\\mathbf{p}_u = P[u]$$，$$\\mathbf{q}_i = Q[i]$$——**固定 ID 查表**，每个用户 / 物品 ID 独占一个可学参数向量。
- **Two-Tower**：$$\\mathbf{p}_u = f_\\theta(\\mathbf{x}_u)$$，$$\\mathbf{q}_i = g_\\phi(\\mathbf{x}_i)$$——**学习到的编码器塔** 从特征生成 embedding。

**为什么这个演化很重要**：(a) **冷启动天然缓解**——Two-Tower 用特征做输入，新用户 / 新物品照样能拿到 embedding，MF 的 ID 查表对新 ID 完全失效；(b) **可融合侧信息**——地理、时间、设备、图像、文本都能塞进塔；(c) **推理成本不变**——物品塔可离线预计算写入 ANN 索引，线上用户塔一次 forward + 点积 + ANN，和 MF 相同的 $$O(k)$$ 打分 + $$O(\\log n)$$ 检索。

Two-Tower 相对于 MF 额外引入的训练细节（**in-batch negative sampling**、**InfoNCE / sampled-softmax loss**、**popularity bias correction**）见 company_documents doc 64《Two-Tower Retrieval Deep Dive》。简而言之：**MF 的损失在观测对上做回归**，**Two-Tower 的损失在 (positive, many negatives) 上做对比学习**——后者因为负采样的选择空间而更能学到区分度高的 embedding。

## Implementation

```python
import numpy as np

def biased_mf_sgd_step(
    R_obs: list[tuple[int, int, float]],
    P: np.ndarray, Q: np.ndarray,
    bu: np.ndarray, bi: np.ndarray, mu: float,
    lr: float, lam: float,
) -> None:
    # Biased-MF SGD 一次 epoch 过一遍观测
    for u, i, r in R_obs:
        pred = mu + bu[u] + bi[i] + P[u] @ Q[i]
        e = r - pred
        # 更新潜在因子 + 偏置
        P_u_old = P[u].copy()
        P[u] += lr * (e * Q[i] - lam * P[u])
        Q[i] += lr * (e * P_u_old - lam * Q[i])
        bu[u] += lr * (e - lam * bu[u])
        bi[i] += lr * (e - lam * bi[i])

def als_user_step(
    R: np.ndarray, Q: np.ndarray, lam: float,
) -> np.ndarray:
    # ALS 一步：固定 Q 求 P，每个用户独立闭式解（可并行）
    k = Q.shape[1]
    P_new = np.zeros((R.shape[0], k))
    for u in range(R.shape[0]):
        rated = R[u] > 0
        Q_u = Q[rated]
        A = Q_u.T @ Q_u + lam * np.eye(k)
        b = Q_u.T @ R[u, rated]
        P_new[u] = np.linalg.solve(A, b)
    return P_new
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---|---|---|
| Bias-only baseline | 任何 MF 起手式 | 先跑 $$\\mu + b_u + b_i$$ 拿到参考线 RMSE |
| Funk-SVD / PMF | 评分数据 + 需要潜在因子 | MAP 正则 = $$\\ell_2$$；PMF 是概率视角包装 |
| Biased-MF | 行业主力评分预测 | 偏置吸收尺度，潜在因子学口味 |
| Weighted ALS / BPR | 隐式反馈（点击 / 购买） | 置信度加权 or 成对排序损失 |
| SGD vs ALS | 在线流式 vs 离线批量 | 流式选 SGD，批量分布式选 ALS |
| MF -> Two-Tower | 需要侧信息 / 冷启动缓解 | 固定 ID 查表 -> 学习塔，打分函数不变 |

### Common Interview Questions
- [ ] 从 bias-only 到 biased-MF 三步演化，每步加了什么建模能力？
- [ ] 推导 biased-MF 中 $$\\mathbf{p}_u$$ 的 ALS 闭式更新。
- [ ] SGD vs ALS 在生产中怎么选？给一个偏 SGD / 偏 ALS 的场景各举一例。
- [ ] 为什么说 Two-Tower 是 "学习的 MF"？它相对于 MF 多解决了什么问题？
- [ ] 显式评分和隐式反馈下，训练目标分别怎么设？

## Key Takeaways
- **MF 演化三步**：bias-only -> Funk-SVD / PMF -> Biased-MF，一步步加能力
- **SGD 在线友好、ALS 批量并行**，不是口味问题，是场景问题
- **Two-Tower = 学习版 MF**：打分函数 $$\\mathbf{u} \\cdot \\mathbf{v}$$ 不变，embedding 从 ID 查表换成编码器塔
- **Cold-Start 缓解** 是 Two-Tower 相对 MF 的核心工程收益
- **BPR / InfoNCE / Sampled-softmax** 是 Two-Tower 专属训练细节，参见 doc《Two-Tower Retrieval Deep Dive》
"""


# ==========================================================================
# docs/mf_to_two_tower_bridge.md content
# ==========================================================================

def build_bridge_doc() -> str:
    b = StudyNoteBuilder()
    b.set_title("MF to Two-Tower Bridge -- From Funk-SVD to Dual Encoders")

    b.add_prerequisites([
        "协同过滤基础：user-item 矩阵 + Memory-Based vs Model-Based",
        "线性代数：矩阵分解 / 内积 / 最小二乘闭式解",
        "基础优化：SGD 梯度更新直觉",
        "Two-Tower 架构（后续细节见 Google 公司文档 `Two-Tower Retrieval Deep Dive`）",
    ])

    b.add_term("Funk-SVD", "Simon Funk's SVD-style MF",
        "Netflix Prize 期间 Simon Funk 的做法：用 SGD 训练低秩 $P Q^T$ 分解")
    b.add_term("PMF", "Probabilistic Matrix Factorization",
        "Salakhutdinov & Mnih 2008，把 Funk-SVD 用高斯先验 + 高斯噪声重新包装成 MAP 推断")
    b.add_term("Biased-MF", "Biased Matrix Factorization",
        "Koren 2009 的标准形式：$\\mu + b_u + b_i + p_u^T q_i$，行业主力")
    b.add_term("ALS", "Alternating Least Squares",
        "交替固定一个矩阵求另一个；每个 user/item block 独立闭式，天然并行")
    b.add_term("SGD", "Stochastic Gradient Descent",
        "随机梯度下降；对 MF 而言，单样本更新 -> 在线友好")
    b.add_term("Two-Tower", "Two-Tower / Dual Encoder Retrieval",
        "用户塔 + 物品塔分别编码，打分是点积；本质上是 MF 把 ID 查表换成学习的编码器")

    # ----------------------------------------------------------------------
    b.add_section("1. MF 演化三步：从偏置基线到 Biased-MF", [
        (
            "理解 MF 最干净的办法是按历史顺序看它一步步长出来，每步只加一种建模能力。"
            "这也是面试高频考点——能讲清楚演化顺序 = 真正理解模型结构，"
            "背公式 = 只会 step 3。"
        ),
        (
            "**Step 1. Bias-only baseline（偏置基线）**\n\n"
            "用全局平均 $\\mu$ + 用户偏置 $b_u$ + 物品偏置 $b_i$ 预测评分。"
            "没有潜在因子，完全学不到 \"口味\" 维度。"
        ),
        FormulaBlock(
            latex=r"\hat{r}_{ui} = \mu + b_u + b_i",
            explanation=(
                "**什么被捕捉了**：$b_u$ 吸收 \"这个用户普遍打高分 / 低分\" 的尺度效应，"
                "$b_i$ 吸收 \"这个物品普遍被喜欢 / 不被喜欢\" 的热度效应。"
                "Netflix Prize 起手就用这套基线，RMSE 约 0.97，比 user-avg 强 3%。"
            ),
        ),
        (
            "**Step 2. Funk-SVD / PMF（纯内积潜在因子）**\n\n"
            "Simon Funk 在 Netflix Prize 期间提出 $R \\approx P Q^T$ 的低秩分解，"
            "Salakhutdinov & Mnih 2008 用概率视角重新包装成 PMF："
            "$\\mathbf{p}_u, \\mathbf{q}_i$ 是零均值高斯先验，$r_{ui}$ 在 $\\mathbf{p}_u^T \\mathbf{q}_i$ 附近高斯噪声，"
            "$\\ell_2$ 正则 = MAP 估计。**PMF 的价值** 是让 \"为什么加 $\\ell_2$\" 变成有贝叶斯解释。"
        ),
        FormulaBlock(
            latex=r"\hat{r}_{ui} = \mathbf{p}_u^T \mathbf{q}_i,\quad \mathbf{p}_u, \mathbf{q}_i \in \mathbb{R}^k",
            explanation=(
                "**潜在因子登场**：每个用户 / 物品映射到 $k$ 维潜在空间（实战 $k \\in [50, 200]$）。"
                "内积捕捉 \"用户 $u$ 在各口味维度上的偏好\" 与 \"物品 $i$ 在各维度上的属性\" 的对齐度。"
            ),
        ),
        (
            "**Step 3. Biased-MF（两者合体，行业主力）**\n\n"
            "Koren 2009 的标准形式：偏置 + 潜在因子内积合体。Netflix / Spotify / Amazon "
            "生产系统基本都是这个形式。"
        ),
        FormulaBlock(
            latex=r"\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^T \mathbf{q}_i",
            explanation=(
                "**训练目标**（加 $\\ell_2$ 正则）：$\\min \\sum_{(u,i) \\in \\Omega} "
                "(r_{ui} - \\hat{r}_{ui})^2 + \\lambda (\\|\\mathbf{p}_u\\|^2 + \\|\\mathbf{q}_i\\|^2 + b_u^2 + b_i^2)$。"
                "**为什么比 Funk-SVD 好**：偏置项吸收尺度效应后，$\\mathbf{p}_u, \\mathbf{q}_i$ "
                "专注学口味差异，维度利用率更高，收敛更稳。"
            ),
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_section("2. Training: SGD vs ALS 的工程差异", [
        (
            "Biased-MF 的两种主流训练方式不是口味问题，而是对应不同场景。"
            "能答对 \"给我一个场景选 SGD / 选 ALS\" 是 Senior MLE 面试高频问。"
        ),
        (
            "**SGD（随机梯度下降）**：对每个观测 $(u, i, r)$ 做一次梯度更新。"
        ),
        FormulaBlock(
            latex=(
                r"\mathbf{p}_u \leftarrow \mathbf{p}_u + \eta \left(e_{ui} \mathbf{q}_i "
                r"- \lambda \mathbf{p}_u\right),\quad e_{ui} = r_{ui} - \hat{r}_{ui}"
            ),
            explanation=(
                "**特性**：mini-batch 级别噪声大但**在线友好**——新评分到达可立刻增量更新，"
                "不需要重扫矩阵；实现简单；对学习率 $\\eta$ 敏感。"
                "**适用**：流式 / 近实时再训、评分分布缓慢漂移、每天只有 delta 数据的场景。"
            ),
        ),
        (
            "**ALS（交替最小二乘）**：交替固定 $Q$ 求 $P$（反之亦然）。每个用户 / 物品"
            "向量有闭式解——这是 ALS 的根本优势。"
        ),
        FormulaBlock(
            latex=(
                r"\mathbf{p}_u = \left(Q_{\Omega_u}^T Q_{\Omega_u} + \lambda I\right)^{-1}"
                r" Q_{\Omega_u}^T \mathbf{r}_u"
            ),
            explanation=(
                "**特性**：每一步精确闭式解，无学习率超参；user 间 / item 间独立可并行"
                "（Spark MLlib ALS 就是把每个 user 发到一个 executor）；但每步要反解 "
                "$k \\times k$ 线性系统（$O(k^3)$），只适合离线批量。"
                "**适用**：离线全量重训、超大矩阵分布式、Netflix Prize / Spotify Daily Job 场景。"
            ),
        ),
        (
            "**面试速答模板**：\n"
            "- 场景 A：\"每 5 分钟更新一次 embedding，用户新点击立刻反馈\" -> **SGD**（在线流式）\n"
            "- 场景 B：\"每晚离线全量重训，矩阵 1 亿 user x 1 亿 item\" -> **ALS**（并行批量）\n"
            "- 场景 C：\"小公司单机训练，代码越简单越好\" -> **SGD**（PyTorch 一把梭）\n"
            "- 场景 D：\"Spark 集群上跑，已经有 100 executors\" -> **ALS**（天然并行）"
        ),
    ])

    b.add_comparison_table(
        headers=["维度", "SGD", "ALS"],
        rows=[
            ["更新粒度", "mini-batch / 单样本", "user / item block 闭式"],
            ["并行性", "难（样本冲突）", "**天然并行**（block 独立）"],
            ["在线增量", "**支持**（新评分即时）", "不支持（需全量重训）"],
            ["超参", "$\\eta$ 敏感", "无 $\\eta$（$\\lambda$ 仍需调）"],
            ["每步成本", "$O(k)$ 梯度", "$O(k^3)$ 闭式反解"],
            ["收敛 epoch", "多（噪声大）", "少（精确）"],
            ["典型部署", "流式 / 近实时", "Spark / 离线批量"],
        ],
        title="2.1 SGD vs ALS 对照表",
    )

    # ----------------------------------------------------------------------
    b.add_section("3. MF 到 Two-Tower 的桥梁", [
        (
            "**核心洞察**：Biased-MF 和现代 Two-Tower 检索的打分函数 **在形式上完全相同**——"
            "都是用户 embedding 和物品 embedding 的点积。区别不在打分，"
            "而在 embedding 的来源。"
        ),
        FormulaBlock(
            latex=(
                r"\text{MF: } \mathbf{p}_u = P[u],\ \mathbf{q}_i = Q[i] "
                r"\quad\text{vs}\quad "
                r"\text{Two-Tower: } \mathbf{p}_u = f_\theta(\mathbf{x}_u),\ "
                r"\mathbf{q}_i = g_\phi(\mathbf{x}_i)"
            ),
            explanation=(
                "**MF**：固定 ID 查表，每个 user_id / item_id 独占一个参数向量。"
                "**Two-Tower**：学习到的编码器塔从特征 $\\mathbf{x}_u, \\mathbf{x}_i$ 生成 embedding，"
                "可以是 MLP、BERT、视觉塔、或任何神经网络。"
            ),
        ),
        (
            "**Two-Tower 解决了 MF 的三个根本问题**：\n\n"
            "1. **冷启动**：MF 的 ID 查表对新 user / 新 item 完全失效"
            "（新 ID 没有学过的向量）。Two-Tower 用特征做输入，"
            "新 user 有 demographic / 上下文，新 item 有图像 / 文本，立即能拿到 embedding。\n"
            "2. **侧信息融合**：MF 只能用 user_id / item_id；Two-Tower 能把地理、"
            "时间、设备、文本、图像统统塞进塔，让 embedding 学到更多维度的对齐。\n"
            "3. **跨域泛化**：同一个物品塔可以被多个任务共享"
            "（主 feed / 搜索 / 相关推荐），MF 每个任务得单独训一套 embedding。"
        ),
        (
            "**推理成本没变**：物品塔离线预计算物品 embedding 写入 **ANN 索引**"
            "（HNSW / FAISS / ScaNN），线上只需一次用户塔 forward + 点积 + ANN top-K，"
            "和 MF 的 $O(k)$ 打分 + $O(\\log n)$ 检索**完全相同**。"
            "这是 Two-Tower 能在生产系统大规模部署的工程基础。"
        ),
        (
            "**Two-Tower 额外引入的训练细节**（不在本文展开，参见 Google 公司文档 "
            "`Two-Tower Retrieval Deep Dive`，doc id=64）：\n\n"
            "- **In-batch negative sampling**：同 batch 其他物品作为负样本\n"
            "- **InfoNCE / sampled-softmax loss**：对比学习损失函数\n"
            "- **Popularity bias correction**：`log Q` 修正防止热门物品主导\n"
            "- **Temperature scaling**：softmax 温度控制 embedding 分布\n\n"
            "这些细节的直觉一致：MF 的损失在观测对上做回归（匹配观测到的评分数值），"
            "Two-Tower 的损失在 (positive, many negatives) 上做对比学习"
            "（匹配 \"正样本应该比负样本分高\"），"
            "后者因为负采样空间而学到更有区分度的 embedding。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_comparison_table(
        headers=["维度", "MF (Biased-MF)", "Two-Tower"],
        rows=[
            ["Embedding 来源", "ID 查表（$P[u], Q[i]$）", "**学习的编码器**（$f_\\theta(x_u), g_\\phi(x_i)$）"],
            ["打分函数", "$\\mathbf{p}_u^T \\mathbf{q}_i + \\text{biases}$", "$f_\\theta(x_u)^T g_\\phi(x_i)$（同构）"],
            ["冷启动", "**失败**（新 ID 无向量）", "**可用**（特征直接进塔）"],
            ["侧信息", "不支持", "**原生支持**"],
            ["训练损失", "回归 / BPR 成对", "InfoNCE / sampled-softmax 对比"],
            ["推理（检索）", "ANN on $Q$", "ANN on $g_\\phi(X)$（同构）"],
            ["参数量", "$O((m+n)k)$", "$O(|\\theta| + |\\phi|)$（塔参数）"],
            ["典型规模", "Netflix 500M 评分", "YouTube / Google Search 十亿级"],
        ],
        title="4. MF vs Two-Tower 对照",
    )

    # ----------------------------------------------------------------------
    b.add_interview_qa(
        "能讲一下 bias-only -> Funk-SVD -> Biased-MF 的演化吗？",
        (
            "**三步递进**：\n"
            "  1. **Bias-only**：$\\hat{r}_{ui} = \\mu + b_u + b_i$。"
            "只捕捉 \"用户打分偏高 / 偏低\" 和 \"物品普遍被喜欢 / 不被喜欢\"，"
            "Netflix Prize 起手 RMSE ~0.97。\n"
            "  2. **Funk-SVD / PMF**：$\\hat{r}_{ui} = \\mathbf{p}_u^T \\mathbf{q}_i$。"
            "引入潜在因子向量，学口味维度的对齐；PMF 是概率版本，"
            "$\\ell_2$ 正则 = 高斯先验下的 MAP。\n"
            "  3. **Biased-MF**：$\\hat{r}_{ui} = \\mu + b_u + b_i + \\mathbf{p}_u^T \\mathbf{q}_i$。"
            "偏置吸收尺度效应，潜在因子专注学口味差异，Koren 2009 生产标准。\n\n"
            "**加分**：主动提 PMF 的贝叶斯视角（为什么加 $\\ell_2$）；"
            "提 Biased-MF 为什么比 Funk-SVD 稳定（维度利用率更高）。"
        ),
    )
    b.add_interview_qa(
        "为什么说 Two-Tower 是 \"学习的 MF\"？",
        (
            "**打分函数相同，embedding 来源不同**：\n"
            "  - MF：$\\mathbf{p}_u = P[u]$（固定 ID 查表）\n"
            "  - Two-Tower：$\\mathbf{p}_u = f_\\theta(\\mathbf{x}_u)$（从特征学出来）\n\n"
            "两者打分都是 $\\mathbf{p}_u^T \\mathbf{q}_i$，推理都是点积 + ANN 索引。"
            "Two-Tower 多解决了三个问题：**冷启动**（特征而非 ID）、"
            "**侧信息融合**（塔能吃任何特征）、**跨域泛化**（塔可跨任务共享）。"
            "训练细节不同（InfoNCE / sampled-softmax vs 回归损失）"
            "但这是 loss 的事，架构上 Two-Tower 就是 MF 的自然延伸。\n\n"
            "**加分**：提推理成本完全相同（都是 ANN top-K + 点积），"
            "这是 Two-Tower 能大规模生产部署的工程基础。"
        ),
    )
    b.add_interview_qa(
        "生产环境 SGD vs ALS 怎么选？",
        (
            "**分场景决策**：\n"
            "  - **要在线增量更新**（用户刚点击的 embedding 5 分钟后生效）-> **SGD**。"
            "ALS 需要全量重训，做不到。\n"
            "  - **离线批量 Spark / 分布式集群**（每晚重训，矩阵 1 亿 x 1 亿）-> **ALS**。"
            "Spark MLlib ALS 天然把每个 user 发到 executor，并行度极高。\n"
            "  - **单机训练 / 代码简单性优先** -> **SGD**（PyTorch 三行搞定）。\n"
            "  - **隐式反馈 + 全量** -> **Weighted ALS**（加置信度 $c_{ui}$），"
            "Hu-Koren-Volinsky 2008 经典。\n\n"
            "**加分**：主动提 ALS 每步 $O(k^3)$ 成本，$k=200$ 时会有明显开销；"
            "提 SGD 对学习率敏感，ALS 无 $\\eta$ 超参这个工程优势；"
            "提真实系统通常 offline ALS 训 embedding 初值 + online SGD 做增量更新"
            "的混合策略。"
        ),
    )

    # ----------------------------------------------------------------------
    b.add_checklist("MF -> Two-Tower Self-Check", [
        "能默写 bias-only / Funk-SVD / Biased-MF 三个公式，解释每步加了什么",
        "能解释 PMF 的概率视角：$\\ell_2$ 正则 = 高斯先验下的 MAP",
        "能默写 SGD 更新公式和 ALS 闭式解，并说清楚各自为什么快 / 慢",
        "能对比 SGD vs ALS 至少 5 个维度（更新粒度 / 并行 / 在线 / 超参 / 每步成本）",
        "能举 2 个偏 SGD 的场景和 2 个偏 ALS 的场景",
        "能解释 \"Two-Tower 是学习的 MF\" 的核心：打分函数相同，embedding 来源不同",
        "能讲 Two-Tower 相对 MF 解决的 3 个问题（冷启动 / 侧信息 / 跨域泛化）",
        "能解释为什么 Two-Tower 推理成本和 MF 相同（ANN + 点积）",
        "能说出 Two-Tower 专属训练细节（InfoNCE / sampled-softmax），"
        "并承认这部分在 Two-Tower 深度 drill 文档里展开",
    ])

    return b.build()


# ==========================================================================
# DB helpers
# ==========================================================================

def update_framework_node(conn: sqlite3.Connection) -> tuple[int, int]:
    """UPDATE description of node 108 in place. Returns (node_id, new_len)."""
    row = conn.execute(
        "SELECT id FROM framework_nodes WHERE id = ?", (NODE_ID,)
    ).fetchone()
    if not row:
        raise RuntimeError(f"framework_node id={NODE_ID} not found")
    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?",
        (NODE_DESCRIPTION, NODE_ID),
    )
    new_len = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (NODE_ID,)
    ).fetchone()[0]
    return NODE_ID, new_len


def upsert_company_document(
    conn: sqlite3.Connection,
    company_id: int,
    title: str,
    content: str,
    doc_kind: str = "prep_note",
    source_type: str = "manual",
) -> tuple[int, str, int]:
    """Insert or update company_document by (company_id, title)."""
    row = conn.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (company_id, title),
    ).fetchone()
    if row:
        doc_id = row[0]
        conn.execute(
            "UPDATE company_documents SET content = ?, doc_kind = ?, "
            "source_type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (content, doc_kind, source_type, doc_id),
        )
        action = "UPDATED"
    else:
        cur = conn.execute(
            "INSERT INTO company_documents "
            "(company_id, title, content, source_type, doc_kind) "
            "VALUES (?, ?, ?, ?, ?)",
            (company_id, title, content, source_type, doc_kind),
        )
        doc_id = cur.lastrowid
        action = "INSERTED"
    new_len = conn.execute(
        "SELECT length(content) FROM company_documents WHERE id = ?", (doc_id,)
    ).fetchone()[0]
    return doc_id, action, new_len


# ==========================================================================
# Main
# ==========================================================================

def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    desc_bytes = len(NODE_DESCRIPTION.encode("utf-8"))
    desc_chars = len(NODE_DESCRIPTION)
    print(
        f"[BUILT] node 108 description: {desc_chars} chars / {desc_bytes} bytes"
    )
    if desc_bytes < 4500:
        print(f"[FAIL] node description {desc_bytes} bytes < 4500 byte target")
        sys.exit(1)

    content = build_bridge_doc()
    warns = StudyNoteBuilder.validate(content)
    for w in warns:
        print(f"[WARN] {w}")
    doc_chars = len(content)
    doc_bytes = len(content.encode("utf-8"))
    # rough EN-equivalent word count; target ~1500 words (=> ~9000-12000 chars mixed zh/en)
    word_estimate_en = doc_chars // 6
    print(
        f"[BUILT] bridge doc: {doc_chars} chars / {doc_bytes} bytes "
        f"/ ~{word_estimate_en} EN-equivalent words"
    )
    if doc_chars > 13000:
        print(f"[WARN] doc {doc_chars} chars may exceed 1500 word AC")

    DOC_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_MD_PATH.write_text(content, encoding="utf-8")
    print(f"[WROTE] {DOC_MD_PATH.relative_to(ROOT)} ({doc_bytes} bytes)")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        nid, nlen = update_framework_node(conn)
        print(f"[UPDATED] framework_node id={nid} desc_len={nlen}")

        did, daction, dlen = upsert_company_document(
            conn, GOOGLE_COMPANY_ID, DOC_TITLE, content
        )
        print(
            f"[{daction}] company_document id={did} "
            f"title='{DOC_TITLE}' content_len={dlen}"
        )

        conn.commit()
    finally:
        conn.close()

    print("[DONE] MF -> Two-Tower bridge seed complete")


if __name__ == "__main__":
    main()
