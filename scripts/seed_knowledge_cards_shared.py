"""Seed shared knowledge cards (T-P1-185, phase 1).

Seeds canonical cross-company cards identified by the T-P0-184 audit
(docs/staging/analysis/company_prep_overlap.md §2 Tier=SHARED). Each card carries
provenance back to the line range that contributed most of the canonical
prose. Overlays capture company-specific angles (product framing, interview
format) without duplicating the shared kernel.

This phase seeds two exemplar cards that together prove the full pattern:

  1. overfitting-l1-l2 (topic 5, audit's strongest dedup target -- 4 locations,
     ~12 KB prose overlap between LinkedIn ml_coding/prob + Uber knn_ml).
  2. bias-variance-tradeoff (topic 4, Uber-canonical, LinkedIn did not
     cover; Adobe aside dropped).

Remaining 12 SHARED topics (classification metrics, logistic regression,
LRU cache, feed ranking, etc.) are scheduled as follow-up tasks under
knowledge-card-seed-phase-2.

Canonical prose: Chinese by default per feedback_lc_notes_chinese; algorithm
names, formula symbols, and complexity notation stay English.

Usage:
    python scripts/seed_knowledge_cards_shared.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

COMPANY_IDS = {
    "LinkedIn": 1,
    "Uber": 5,
    "Adobe": 23,
    "Pinterest": 29,
}


CARDS = [
    {
        "slug": "overfitting-l1-l2",
        "title": "过拟合与 L1/L2 正则化",
        "tags": ["regularization", "ml-theory", "generalization"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 193,
        "source_line_end": 262,
        "canonical_body": r"""## 过拟合的定义与诊断

过拟合指模型在训练集上表现显著优于测试集，本质是**模型容量相对于有效样本量过大**，导致拟合了数据中的噪声。经典诊断：训练误差持续下降而验证误差在某一 epoch 后上升（U 型曲线），或者交叉验证各折得分方差大。

## L2 正则化（Ridge / weight decay）

在经验风险上叠加权重的 L2 范数惩罚：

$$
\mathcal{L}_{\text{L2}}(w) = \mathcal{L}_{\text{emp}}(w) + \lambda \lVert w \rVert_2^2
$$

- **几何视角**：在权重空间约束解落入以原点为中心的球内，从 MAP 视角等价于对 $w$ 施加均值为 0、方差为 $1/(2\lambda)$ 的高斯先验。
- **优化视角**：梯度为 $\nabla \mathcal{L}_{\text{emp}} + 2\lambda w$，每步都把权重往原点"拉"一点，故又称 weight decay。
- **效果**：权重整体变小但**不稀疏**；对共线特征会把系数"平摊"。
- **超参**：$\lambda$ 用验证集调，典型 log-scale 搜索 $10^{-4} \sim 10^{1}$。

## L1 正则化（Lasso）

$$
\mathcal{L}_{\text{L1}}(w) = \mathcal{L}_{\text{emp}}(w) + \lambda \lVert w \rVert_1
$$

- **几何视角**：约束区域是以原点为中心的 L1 球（高维菱形），顶点落在坐标轴上，最优解容易命中顶点 $\Rightarrow$ **稀疏解**。等价于 Laplace 先验。
- **优化视角**：次梯度在 0 处不连续，常用坐标下降（coordinate descent）或 proximal 方法（soft-thresholding）求解。
- **效果**：自动做特征选择；对相关性强的特征集合倾向于挑出其中一个，其余置 0。

## L1 vs L2 对比

| 维度 | L1 | L2 |
|---|---|---|
| 解的稀疏性 | 稀疏（特征选择） | 稠密（系数整体缩小） |
| 先验 | Laplace | Gaussian |
| 可微性 | 0 处不可微 | 处处可微 |
| 相关特征 | 挑一个 | 系数平摊 |
| 闭式解 | 一般无 | 线性回归下有闭式（$(X^\top X + \lambda I)^{-1} X^\top y$） |
| 抗噪 | 对异常特征更鲁棒 | 对异常样本更敏感 |

## Elastic Net

同时叠加 L1 与 L2：

$$
\mathcal{L}_{\text{EN}}(w) = \mathcal{L}_{\text{emp}}(w) + \lambda_1 \lVert w \rVert_1 + \lambda_2 \lVert w \rVert_2^2
$$

在**高维且特征高度相关**场景（如基因数据、广告特征）常比纯 L1 更稳定：L2 项缓解 L1 的"挑一个"特性，鼓励同组相关特征一起被选中或剔除。

## 其他抑制过拟合的手段

- 数据层：增加训练样本、数据增强、清洗标签噪声。
- 模型层：降低容量（更少层 / 更少参数 / 更浅树）、early stopping、dropout、bagging。
- 训练层：交叉验证选择超参、batch norm 的正则效应。

## 面试追问

1. **为什么 L1 产生稀疏解而 L2 不会？** 从 L1/L2 约束区域与损失等高线切点的几何位置解释（L1 顶点在坐标轴上）。
2. **weight decay 和 L2 是否完全等价？** 在 SGD 下等价；在 Adam 下 $L_2$ 正则与 weight decay **不等价**，因此 AdamW 将 weight decay 单独处理。
3. **$\lambda$ 过大的症状？** 欠拟合：训练误差与验证误差同时抬高，权重趋近 0，模型退化。
""",
    },
    {
        "slug": "bias-variance-tradeoff",
        "title": "偏差-方差分解 (Bias-Variance Tradeoff)",
        "tags": ["ml-theory", "generalization", "model-selection"],
        "source_company": "Uber",
        "source_file": "docs/uber_bps_knn_ml_fundamentals.md",
        "source_line_start": 405,
        "source_line_end": 448,
        "canonical_body": r"""## 分解公式

对于平方损失，期望泛化误差可分解为：

$$
\mathbb{E}_{D, x}\bigl[(y - \hat{f}_D(x))^2\bigr] = \underbrace{\bigl(\mathbb{E}_D[\hat{f}_D(x)] - f(x)\bigr)^2}_{\text{Bias}^2} + \underbrace{\mathbb{E}_D\bigl[(\hat{f}_D(x) - \mathbb{E}_D[\hat{f}_D(x)])^2\bigr]}_{\text{Variance}} + \underbrace{\sigma^2}_{\text{Irreducible}}
$$

其中 $f(x)$ 是真实条件期望，$\hat{f}_D$ 是在数据集 $D$ 上训练出的模型，$\sigma^2$ 是标签噪声的方差。

## 三项含义

- **Bias**：模型在所有可能训练集上的平均预测与真值的差距，反映**模型族的表达能力**。线性模型拟合非线性数据时 bias 高。
- **Variance**：模型预测随训练集不同而波动的程度，反映**模型对训练数据的敏感度**。高容量模型（深树、KNN 小 k）variance 高。
- **Irreducible**：与模型无关的观测噪声下界。

## 与模型复杂度的关系

- 复杂度 $\uparrow$：bias $\downarrow$、variance $\uparrow$。
- 复杂度 $\downarrow$：bias $\uparrow$、variance $\downarrow$。
- 泛化误差曲线呈 U 型，存在最优复杂度点。

## 常见模型的定位

| 模型 | 典型 bias | 典型 variance | 调参旋钮 |
|---|---|---|---|
| Linear / Logistic | 高 | 低 | 特征工程、多项式展开 |
| KNN (小 k) | 低 | 高 | 增大 k、加权 |
| KNN (大 k) | 高 | 低 | 减小 k |
| Decision Tree (深) | 低 | 高 | 限深度、min_samples_leaf |
| Random Forest | 中 | 低（bagging 降 variance） | 树数、max_features |
| Gradient Boosting | 低 | 中（有过拟合风险） | shrinkage、early stop |
| Deep NN | 低 | 高 | dropout、weight decay、数据增强 |

## 经验建议

- **诊断**：训练误差低、验证误差高 $\Rightarrow$ variance 主导，增加正则 / 数据量；训练误差本身高 $\Rightarrow$ bias 主导，扩容量或改特征。
- **bagging** 对 variance 友好（Random Forest），**boosting** 更多是降 bias（但要控 variance）。
- 现代深度学习在参数量远超样本的"过参数化"区常观察到 **double descent** 曲线，在传统 U 型之外再下降一次——但面试以经典分解为准答。

## 面试追问

1. **为什么 bagging 能降 variance？** 独立模型平均的方差为 $\sigma^2 / n$（相关性 $\rho$ 存在时为 $\rho \sigma^2 + (1-\rho)\sigma^2/n$），因此要求基学习器尽量去相关。
2. **能否同时降低 bias 和 variance？** 增加数据、提高特征质量可以在不提升复杂度的情况下双降；正则化则是以微量 bias 换 variance。
3. **0-1 损失下 bias-variance 是否可加？** 不是精确可加分解，需用 Domingos 2000 的定义，面试中可以这样澄清。
""",
    },
]


OVERLAYS = [
    # overfitting-l1-l2 overlays
    {
        "card_slug": "overfitting-l1-l2",
        "company_name": "LinkedIn",
        "angle": "interview-format",
        "overlay_body": r"""LinkedIn 的 ML coding 环节对该题考法特点：
- 常要求手写 $\partial \lVert w \rVert_2^2 / \partial w$ 与 L1 的次梯度，强调 soft-thresholding 的推导。
- 若面试官给 logistic regression 场景，会追问"L2 正则下 MAP 与 ridge 的对应"——参考 prob:969 的"linear ↔ logistic 等价"题。
- Coding 可能让你在 Python 中为 SGD 手动加 L2 衰减一行代码（`w -= lr * (grad + 2*lam*w)`）。""",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 193,
        "source_line_end": 262,
    },
    {
        "card_slug": "overfitting-l1-l2",
        "company_name": "Uber",
        "angle": "product",
        "overlay_body": r"""Uber 的 KNN / 产品建模语境下：
- KNN 无显式参数不谈 L1/L2，但会问"距离度量的尺度正则"——特征缩放即隐式正则。
- 对 CTR / 定价模型会问："在有大量稀疏 cross feature 时选 L1 还是 Elastic Net？" 答：Elastic Net，原因是相关特征组应一起选/弃。
- 追问常与 bias-variance 串联：`λ ↑ → variance ↓ / bias ↑`。""",
        "source_file": "docs/uber_bps_knn_ml_fundamentals.md",
        "source_line_start": 449,
        "source_line_end": 498,
    },
    # bias-variance overlays
    {
        "card_slug": "bias-variance-tradeoff",
        "company_name": "Uber",
        "angle": "interview-format",
        "overlay_body": r"""Uber 的 ML fundamentals 轮高频问法：
- 要求口头说出分解公式的三项以及 KNN 中 $k$ 对应的 bias/variance 走向。
- 常与 cross-validation（knn_ml:475）串联："如何用 CV 找到 bias-variance sweet spot？"
- 会把它接到 ranking / CTR 场景："线上 AUC 抖动大是 variance 问题吗？" 答：多半是样本量 + 特征稳定性，不一定是模型 variance。""",
        "source_file": "docs/uber_bps_knn_ml_fundamentals.md",
        "source_line_start": 405,
        "source_line_end": 474,
    },
]


def seed(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Ensure tables exist (idempotent with migrate_add_knowledge_cards.py).
    ok = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_cards'"
    ).fetchone()
    if not ok:
        raise RuntimeError(
            "knowledge_cards table missing. Run migrate_add_knowledge_cards.py first."
        )

    upserted_cards = 0
    for card in CARDS:
        existing = cur.execute(
            "SELECT id FROM knowledge_cards WHERE slug=?", (card["slug"],)
        ).fetchone()
        if existing:
            cur.execute(
                """UPDATE knowledge_cards
                   SET title=?, canonical_body=?, tags=?, source_company=?,
                       source_file=?, source_line_start=?, source_line_end=?,
                       updated_at=CURRENT_TIMESTAMP
                   WHERE slug=?""",
                (
                    card["title"],
                    card["canonical_body"],
                    json.dumps(card["tags"], ensure_ascii=False),
                    card["source_company"],
                    card["source_file"],
                    card["source_line_start"],
                    card["source_line_end"],
                    card["slug"],
                ),
            )
            print(f"[UPDATE] {card['slug']}")
        else:
            cur.execute(
                """INSERT INTO knowledge_cards
                   (slug, title, canonical_body, tags, source_company,
                    source_file, source_line_start, source_line_end)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    card["slug"],
                    card["title"],
                    card["canonical_body"],
                    json.dumps(card["tags"], ensure_ascii=False),
                    card["source_company"],
                    card["source_file"],
                    card["source_line_start"],
                    card["source_line_end"],
                ),
            )
            print(f"[INSERT] {card['slug']}")
        upserted_cards += 1

    upserted_overlays = 0
    for ov in OVERLAYS:
        card_id = cur.execute(
            "SELECT id FROM knowledge_cards WHERE slug=?", (ov["card_slug"],)
        ).fetchone()[0]
        company_id = COMPANY_IDS[ov["company_name"]]
        existing = cur.execute(
            """SELECT id FROM company_card_overlays
               WHERE card_id=? AND company_id=? AND angle=?""",
            (card_id, company_id, ov["angle"]),
        ).fetchone()
        if existing:
            cur.execute(
                """UPDATE company_card_overlays
                   SET overlay_body=?, source_file=?, source_line_start=?,
                       source_line_end=?
                   WHERE id=?""",
                (
                    ov["overlay_body"],
                    ov["source_file"],
                    ov["source_line_start"],
                    ov["source_line_end"],
                    existing[0],
                ),
            )
            print(f"[UPDATE overlay] {ov['card_slug']} / {ov['company_name']} / {ov['angle']}")
        else:
            cur.execute(
                """INSERT INTO company_card_overlays
                   (card_id, company_id, angle, overlay_body,
                    source_file, source_line_start, source_line_end)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    card_id,
                    company_id,
                    ov["angle"],
                    ov["overlay_body"],
                    ov["source_file"],
                    ov["source_line_start"],
                    ov["source_line_end"],
                ),
            )
            print(f"[INSERT overlay] {ov['card_slug']} / {ov['company_name']} / {ov['angle']}")
        upserted_overlays += 1

    conn.commit()

    total_cards = cur.execute("SELECT COUNT(*) FROM knowledge_cards").fetchone()[0]
    total_overlays = cur.execute("SELECT COUNT(*) FROM company_card_overlays").fetchone()[0]
    print(
        f"\n[SUMMARY] upserted {upserted_cards} cards / {upserted_overlays} overlays"
    )
    print(f"[VERIFY] table totals: cards={total_cards}, overlays={total_overlays}")
    conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DB)
    print(f"Seeding knowledge cards: {db_path}")
    seed(db_path)
