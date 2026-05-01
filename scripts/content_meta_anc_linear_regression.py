"""[META-ANC-5] Linear Regression drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the hand-derived
Linear Regression Meta AI-Native Coding question. Distills the closed-form
normal-equation derivation (with the dimension-alignment insight that explains
why X^T appears, not X), the three numpy implementations (inv / solve / pinv),
the O(nd^2 + d^3) complexity, and the high-frequency follow-up cluster
(Ridge / Lasso / collinearity / Batch-vs-SGD / unsorted-sparse) into one
description.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='normal_equation_lstsq'). The pattern column is the STABLE SLUG --
never rewritten. The title may evolve. A sentinel HTML comment
<!-- ANC_SLUG: meta_anc_linear_regression --> is embedded at the top of the
description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup, asserted == 31).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 4 second half, lines 267-286).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402
from src.backend.models.company_tags import ProblemCompanyTag  # noqa: E402
from src.backend.models.problem import Problem  # noqa: E402

SLUG = "meta_anc_linear_regression"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "normal_equation_lstsq"
TITLE = "Meta AI-Native Coding - Linear Regression (closed-form X^TX + Ridge/Lasso/SGD follow-ups)"
DIFFICULTY = "medium"
CATEGORY = "ml_coding"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "X^TX",
    "normal equation",
    "Ridge",
    "Lasso",
    "pinv",
    "closed-form",
]

DESCRIPTION = SENTINEL + r"""

# Linear Regression -- Meta AI-Native Coding (closed-form $X^TX$ + Ridge / Lasso / SGD follow-ups)

> **题型**: 给点集，最小化 MSE，**手推**最小二乘 normal equation 闭式解 (closed-form solution) 并实现。
> **场景**: Meta AI-Native Coding MLE / 实习向；这道题考的不是会不会调 sklearn，而是**能不能自己推导 + 讲清楚每个 numpy API 背后是什么数值算法**。
> **AI 协同**: 忘公式时让 AI 推导导数 + 给 closed-form 实现没问题；但"$X^T$ 是为了维度对齐"这种**洞察必须自己讲**——这是这题的 senior signal。

---

## 1. 题面 (一句话)

给定数据矩阵 $X \in \mathbb{R}^{n \times d}$ 和目标向量 $y \in \mathbb{R}^{n}$ ($n$ 个样本、$d$ 个特征)，找到权重向量 $w \in \mathbb{R}^{d}$ 使均方误差 $\text{MSE}(w) = \frac{1}{n} \|Xw - y\|^2$ 最小。**手推**闭式解 + 用 numpy 实现，**不准调 sklearn**。

---

## 2. 推导 (3 行干完)

最小化 $L(w) = \|Xw - y\|^2$ (常数 $\frac{1}{n}$ 不影响 argmin，先丢了):

1. **展开**: $L(w) = (Xw - y)^T(Xw - y) = w^T X^T X w - 2 y^T X w + y^T y$
2. **求导**: $\nabla_w L = 2 X^T X w - 2 X^T y = 2 X^T (Xw - y)$
3. **令梯度为零**: $X^T X w = X^T y \implies \boxed{w = (X^T X)^{-1} X^T y}$

这就是 **normal equation** (最小二乘正规方程) 的 closed-form 解。

---

## 3. 关键 dimension argument (这一句是 senior signal)

考官最爱追问: "为什么求导出来前面是 $X^T$ 而不是 $X$？"

**标准答案**:

- $\nabla_w L \in \mathbb{R}^{d \times 1}$ (梯度跟 $w$ 同 shape)
- $Xw - y \in \mathbb{R}^{n \times 1}$
- 要把 $n \times 1$ 的残差 "转回" $d \times 1$ 的梯度空间，前面**必须**乘 $X^T \in \mathbb{R}^{d \times n}$
- $X^T (Xw - y) \in \mathbb{R}^{d \times n} \cdot \mathbb{R}^{n \times 1} = \mathbb{R}^{d \times 1}$ -- 维度对齐

**金句**: "**$X^T$ 不是来自 chain rule 的某个魔法步骤，而是为了维度对齐**——梯度必须落回 $w$ 所在的 $d$ 维空间。" 讲到这一句，考官就知道你不是在背公式。

---

## 4. 三种 numpy 实现对照表 (考官想听的就是这个对比)

| 写法 | 数值算法 | 何时用 | 何时翻车 |
|------|----------|--------|----------|
| `np.linalg.inv(X.T @ X) @ X.T @ y` | **教科书显式求逆** | 教学演示 | $X^TX$ 病态 / 奇异时 condition number 爆炸；**慢且数值不稳**，生产禁用 |
| `np.linalg.solve(X.T @ X, X.T @ y)` | **LU 分解解方程** $Ax = b$ | **推荐**: $X$ 满秩、$d$ 不太大 | $X^TX$ 奇异时直接报 `LinAlgError` |
| `np.linalg.pinv(X) @ y` | **SVD 伪逆** (Moore-Penrose) | $X$ 共线 / 奇异 / $n < d$ 都能跑 | 比 `solve` 慢 $2 \times$，但**最稳** |

**面试金句**: "**显式 `inv` 永远不要用**——不是慢的问题，是数值稳定性的问题。`solve` 用 LU 分解避免显式求逆；`pinv` 用 SVD 处理奇异。**$X^TX$ 病态时只有 `pinv` 能活下来**。"

### Toy 代码 (60 秒可写完)

```python
import numpy as np

# X: (n, d), y: (n,)
def fit_normal_equation(X, y):
    # 推荐写法: LU 分解, 比 inv 快且稳
    return np.linalg.solve(X.T @ X, X.T @ y)

def fit_pinv(X, y):
    # 最稳写法: SVD, 处理奇异 X^TX
    return np.linalg.pinv(X) @ y

def fit_textbook_BAD(X, y):
    # 教科书写法, 生产禁用
    return np.linalg.inv(X.T @ X) @ X.T @ y
```

**别忘了**: 加 bias / intercept 项要在 $X$ 前面拼一列 1: `X_aug = np.hstack([np.ones((n, 1)), X])`。

---

## 5. 复杂度 (一行说清楚)

$$\text{Cost} = O(\underbrace{nd^2}_{X^T X \text{ 矩阵乘}} + \underbrace{d^3}_{\text{LU / SVD 分解}})$$

- $n \gg d$: 主导项是 $nd^2$ -- normal equation 没问题
- $d$ 大 (几千+): $d^3$ 爆炸 -- 改用 **GD / SGD** (复杂度 $O(\text{iter} \cdot nd)$)
- $d \gg n$ (典型: 文本特征、基因数据): $X^TX$ 必奇异 -- 强制走 `pinv` 或加 L2 (Ridge)

**判定口诀**: $d < 1000$ -> closed-form (一发解决); $d > 10000$ -> SGD; 中间靠经验和硬件。

---

## 6. 高频 follow-up Q & A

### Q1: 加 L2 正则 (Ridge) 的闭式解？

$$w_{\text{Ridge}} = (X^T X + \lambda I)^{-1} X^T y$$

**关键洞察**: $\lambda I$ 把 $X^TX$ 的所有特征值抬高 $\lambda$，所以 $(X^TX + \lambda I)$ **永远可逆**——这是 Ridge 的"附加福利"。共线 / $d > n$ 全都能跑。**这就是为什么 Ridge 默认更稳**。

### Q2: 为什么 L1 (Lasso) 没有 closed-form 解？

$|w_j|$ 在 $w_j = 0$ 处**不可导** (左导数 -1, 右导数 +1, 有跳变 / 次梯度)，整体 $L(w) = \|Xw - y\|^2 + \lambda \|w\|_1$ 不能一次性解析解出。

**但是**逐元素 (elementwise) 固定其他维度，单个 $w_j$ 的子问题**可以**解析求解，得到 **soft-thresholding** 算子:

$$w_j \leftarrow \text{sign}(z_j) \cdot \max(|z_j| - \lambda, 0)$$

这就是 **coordinate descent** / **ISTA** 算法的基础——每次更新一个坐标，整体迭代收敛。

**金句**: "**Lasso 没有整体 closed-form, 但有 coordinate-wise closed-form**。"

### Q3: 特征共线 (collinearity) 怎么办？

共线意味着 $X$ 的列**线性相关** -> $X^TX$ **离奇异更近一步** (condition number 爆炸) -> `inv` 数值不稳。处理方案:

1. **加 L2 -> Ridge**: $\lambda I$ 让 $X^TX$ 永远可逆 (见 Q1)
2. **走 SVD -> pinv**: Moore-Penrose 伪逆能处理奇异
3. **删冗余特征**: 用 VIF (variance inflation factor) 识别共线列直接砍
4. **降维 -> PCA**: 把 $X$ 投到不相关的主成分上再 fit

工业界默认: **直接 Ridge** (一行代码), 实在不行再上 PCA。

### Q4: Batch GD vs Mini-batch vs SGD 三者对比

| 算法 | 每步样本数 | 梯度方差 | 探索性 | GPU 友好 | 何时用 |
|------|------------|----------|--------|----------|--------|
| **Batch GD** | 全部 $n$ | **无偏 + 小** | 低 (易陷局部极小 / 鞍点) | 差 (一次喂不下) | 凸问题 + 数据小 |
| **SGD** | 1 | **无偏 + 大** | **高** (噪声反而帮忙跳出鞍点) | 差 (没并行性) | 在线学习 / 流式数据 |
| **Mini-batch** | 32 / 64 / ... | 折中 | 折中 | **优** (一次填满 SIMD/GPU) | **事实标准** |

**金句**: "**SGD 的方差不是 bug 是 feature**——噪声带来探索性，能跳出 batch GD 卡住的鞍点；Mini-batch 是噪声 + 并行的折中点，所以是工业默认。"

### Q5: 稀疏向量没排序怎么算 $w^T x$？

丢一边进哈希表 `{idx: val}`，遍历另一边查表，期望 $O(\text{nnz}_1 + \text{nnz}_2)$。这是 **hash join** 模式。如果两边都有序就用**双指针** (cache 友好、零额外内存) -- 这是 LeetCode 1570 的标准答案。**详见姊妹题 Sparse Matrix Ops**。

### Q6: 解释 $w$ 每个分量的意义？

$w_j$ = "**控制其他特征不变时, $x_j$ 增加 1 单位预期 $y$ 变化多少**" (ceteris paribus 解释)。**前提**: 特征不共线 (否则 $w_j$ 不唯一 / 不稳定)。

---

## 7. AI 协同分工对照表

| 让 AI 做 | 自己做更快 / 更靠谱 |
|----------|---------------------|
| 推导 $\nabla_w \|Xw - y\|^2 = 2X^T(Xw-y)$ | "**$X^T$ 是为了维度对齐**"这一句 senior insight |
| 给三种 numpy 实现 (`inv` / `solve` / `pinv`) 模板 | 三种之间的**数值稳定性 trade-off** (考官想听对比, 不是代码) |
| 列 Ridge 公式 $(X^TX + \lambda I)^{-1} X^T y$ | "$\lambda I$ **让所有特征值抬高 $\lambda$, 所以永远可逆**" |
| 写 soft-thresholding 算子模板 | "**Lasso 没有整体 closed-form, 但有 coordinate-wise closed-form**"判断 |
| 实现 batch / mini-batch / SGD 三种训练循环 | "**SGD 的方差不是 bug 是 feature**" 这句金句 |

**底线**: AI 帮你打代码 + 列公式，**洞察 (维度对齐 / 数值稳定 / 噪声 = 探索性) 必须自己讲**。这是 senior signal vs junior signal 的分水岭。

---

## 8. 三句金句 (面试时放慢节奏说)

1. **维度对齐金句**: "**$X^T$ 不是魔法步骤, 是为了让梯度落回 $w$ 所在的 $d$ 维空间**——这是 chain rule 的几何含义。"
2. **数值稳定金句**: "**显式 `inv` 永远不要用**——`solve` 走 LU, `pinv` 走 SVD; $X^TX$ 病态时只有 `pinv` 能活下来。"
3. **正则化金句**: "**Ridge 永远可逆是因为 $\lambda I$ 把所有特征值抬高 $\lambda$**; Lasso 没有整体 closed-form, 但有 coordinate-wise closed-form (soft-thresholding)。"

讲这三句 = 你在 reasoning, 不在 recite。

---

## 9. 一图流总结

```
问题: min ||Xw - y||^2
        |
        v
推导: grad = 2 X^T (Xw - y) = 0
        |
        v ($X^T$ 是为了维度对齐, $\nabla_w L \in R^d$)
解: w = (X^T X)^{-1} X^T y  <-- normal equation closed-form
        |
        +-- 实现: solve (LU 推荐) / pinv (SVD 最稳) / inv (教科书慎用)
        +-- 复杂度: O(nd^2 + d^3); d 大 -> SGD
        |
        v
follow-up:
  Ridge -> (X^TX + lambda I)^{-1} X^T y, 永远可逆
  Lasso -> 整体没 closed-form, 但坐标下降有 soft-thresholding
  Collinearity -> Ridge / pinv / VIF 删特征 / PCA
  GD vs SGD vs Mini-batch -> 噪声 = 探索性, mini-batch 兼顾 GPU
  稀疏未排序 -> hash join O(nnz1 + nnz2)
```

**记住**: 这道题的差异化签名是 (1) 维度对齐的洞察 (不是背公式), (2) 三种 numpy 实现的数值稳定性对比 (不是只会写一个), (3) Ridge / Lasso 的可逆性 / 可导性差异 (不是只会念名字)。三件事都讲到位 = senior signal。
"""


def _normalize(text: str) -> str:
    """Semantic normalization for NOOP comparison.

    Strip per-line trailing whitespace, force LF line endings, collapse
    3+ blank lines down to 2. Forbids accidental [UPDATED] reports caused
    by trailing-whitespace drift or platform line-ending differences.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _assert_required_keywords(description: str) -> None:
    """Abort if any REQUIRED-KEYWORD is missing from the description."""
    for kw in REQUIRED_KEYWORDS:
        if kw not in description:
            raise RuntimeError(
                f"[META-ANC-5] missing keyword {kw!r} -- regenerate"
            )


def _assert_no_emoji(description: str) -> None:
    """Project rule: no emoji characters in content."""
    for ch in description:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1FAFF
            or 0x1F000 <= cp <= 0x1F2FF
            or 0x2600 <= cp <= 0x27BF
        ):
            raise RuntimeError(
                f"[META-ANC-5] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_linear_regression() -> int:
    """Insert or update the Linear Regression drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-5] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-5] expected Meta company_id=31, got {company_id}"
            )
        print(f"[OK] target company: id={company_id} name='Meta'")

        existing = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .first()
        )

        normalized_new = _normalize(DESCRIPTION)

        if existing is None:
            problem = Problem(
                title=TITLE,
                description=DESCRIPTION,
                difficulty=DIFFICULTY,
                pattern=PATTERN,
                category=CATEGORY,
                source=SOURCE,
                description_source=DESCRIPTION_SOURCE,
                is_completed=False,
                comfort_level=0,
            )
            db.add(problem)
            db.flush()
            pid = int(problem.id)
            print(
                f"[INSERT] problems id={pid} title={TITLE!r} "
                f"len={len(DESCRIPTION)}"
            )
        else:
            pid = int(existing.id)
            normalized_old = _normalize(existing.description or "")
            if normalized_old == normalized_new:
                print(
                    f"[NOOP] problems id={pid} description "
                    f"semantically identical (len={len(DESCRIPTION)})"
                )
            else:
                old_len = len(existing.description or "")
                existing.description = DESCRIPTION
                existing.title = TITLE
                existing.difficulty = DIFFICULTY
                existing.category = CATEGORY
                existing.description_source = DESCRIPTION_SOURCE
                print(
                    f"[UPDATED] problems id={pid} old_len={old_len} "
                    f"new_len={len(DESCRIPTION)} "
                    f"delta={len(DESCRIPTION) - old_len:+d}"
                )

        existing_tag = (
            db.query(ProblemCompanyTag)
            .filter(
                ProblemCompanyTag.problem_id == pid,
                ProblemCompanyTag.company_id == company_id,
            )
            .first()
        )
        if existing_tag is None:
            tag = ProblemCompanyTag(
                problem_id=pid,
                company_id=company_id,
                relevance="core",
                source="manual",
                notes="Meta AI-Native Coding 2026-05-01 inventory",
            )
            db.add(tag)
            print(
                f"[INSERT] problem_company_tags problem_id={pid} "
                f"company_id={company_id} relevance=core"
            )
        else:
            print(
                f"[NOOP] problem_company_tags problem_id={pid} "
                f"company_id={company_id} already present"
            )

        db.commit()

        final = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .one()
        )
        print(
            f"[VERIFY] problems id={final.id} pattern={final.pattern!r} "
            f"source={final.source!r} desc_len="
            f"{len(final.description or '')}"
        )
        return int(final.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upsert_meta_anc_linear_regression()
