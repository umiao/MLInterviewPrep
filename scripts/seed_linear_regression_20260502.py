"""Seed: Linear Regression handwritten numpy notes for problems.id=1102.

Fills `problems.notes` for the Meta AI-Native Coding Linear Regression row.
This is the SINGLE source of truth for the deduped study-note content
(题面 + 推导 + numpy 实现对照 + LinearRegression 类 + closed-form vs GD
对比 + sanity test + follow-up Q&A). The `description` column is now a
short framing blurb only (see content_meta_anc_linear_regression.py); all
implementation/derivation/follow-up content lives here.

History:
- T-P0-688 [MLI-D1] (2026-05-02): initial seed of handwritten implementation.
- T-P1-719 [MLI-CONTENT] (2026-05-03): golden rewrite per user reference --
  removed duplicated 题面/推导/follow-ups (which previously appeared in BOTH
  description and notes), added lstsq row to numpy comparison table (matches
  the actual code which already used lstsq -- the original table only
  listed inv/solve/pinv, a hidden cheat-sheet vs code inconsistency).

Conventions:
- Code uses np.linalg.lstsq (SVD on X, kappa(X) not kappa(X)^2). Never inv.
- Ridge follow-up uses np.linalg.solve (LU on X^TX + lambda*I). Never inv.
- Chinese narration + English terms; no emoji.

Idempotency:
- Sentinel <!-- META_AI_NATIVE_LR_20260502 --> at the top of the body.
- UPDATE skipped if existing notes byte-equal to canonical payload.
- NO new problems row: this script only writes to problems.id=1102.
  Aborts with a clear error if id=1102 is missing (precondition established
  by content_meta_anc_linear_regression.py).
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PROBLEM_ID = 1102
SENTINEL = "<!-- META_AI_NATIVE_LR_20260502 -->"

NOTES = SENTINEL + r"""

## Linear Regression -- Closed-form (lstsq) + Full-Batch GD

### 1. 题面

给 $X \in \mathbb{R}^{n \times d}$ 和 $y \in \mathbb{R}^{n}$, 求
$w \in \mathbb{R}^{d}$ 最小化
$\text{MSE}(w) = \frac{1}{n}\|Xw - y\|^2$. 手推 closed-form + numpy
实现, 禁用 sklearn.

### 2. 推导

丢掉常数 $1/n$, 最小化 $L(w) = \|Xw - y\|^2$:

- 展开: $L(w) = w^T X^T X w - 2 y^T X w + y^T y$
- 求导: $\nabla_w L = 2 X^T X w - 2 X^T y = 2 X^T (Xw - y)$
- 令梯度为零: $X^T X w = X^T y \implies \boxed{w = (X^T X)^{-1} X^T y}$

### 3. Dimension argument

$\nabla_w L \in \mathbb{R}^d$, 残差 $Xw - y \in \mathbb{R}^n$; 前面乘
$X^T \in \mathbb{R}^{d \times n}$ 是为了把残差从 $n$ 维空间投回 $w$
所在的 $d$ 维空间——维度对齐, 不是 chain rule 的魔法.

### 4. numpy 实现对照

| 写法 | 算法 | 何时用 | 何时翻车 |
|------|------|--------|----------|
| `inv(X.T @ X) @ X.T @ y` | 显式求逆 | 永远别用 | $\kappa(X^T X) = \kappa(X)^2$, 误差放大一阶 |
| `solve(X.T @ X, X.T @ y)` | LU | $X$ 满秩, $d$ 小 | $X^T X$ 奇异 -> `LinAlgError` |
| `lstsq(X, y, rcond=None)` | SVD on $X$ | **默认推荐** | 比 `solve` 慢 ~2x |
| `pinv(X) @ y` | SVD 伪逆 | 奇异 / $n < d$ | 同 `lstsq` 但多一步构造伪逆 |

**金句**: `solve` 走 LU 仍构造 $X^T X$, 中等稳; `lstsq` / `pinv` 直接对
$X$ SVD, 不构造 $X^T X$, $\kappa$ 不平方, 最稳.

### 5. 复杂度

Closed-form $O(n d^2 + d^3)$ ($d \lesssim 10^3$); GD $O(T \cdot n d)$
($d \gtrsim 10^4$ 或 $d \gg n$).

### 6. 实现

公开 API 上一律把 bias 当 **独立参数** $b$ (跟 NN 训练循环同构);
闭式解内部因为 lstsq 一次解一个线性系统, 临时把 1 列拼进 $X$ 解出
$[b, w_1, \dots, w_d]$ 再拆回——这只是 LR 闭式解的数学技巧, 不是
"bias 就该这么处理" 的通用范式. GD 路径完全不用这个技巧.

```python
import numpy as np
from typing import Literal, Optional


class LinearRegression:
    def __init__(
        self,
        method: Literal["closed_form", "gd"] = "closed_form",
        fit_intercept: bool = True,
        learning_rate: float = 1e-2,
        max_iterations: int = 1000,
        convergence_threshold: float = 1e-6,
    ):
        self.method = method
        self.fit_intercept = fit_intercept
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.coef_: Optional[np.ndarray] = None       # (d,)
        self.intercept_: float = 0.0                  # scalar
        self.training_loss_history: list[float] = []

    def _fit_closed_form(self, X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
        # LR-only trick: 临时拼一列 1 让 lstsq 一次解出 [b, w_1, ..., w_d].
        # NN 里永远不这么干 (bias 是独立参数, 见 _fit_gd).
        n, d = X.shape
        if self.fit_intercept:
            ones = np.ones((n, 1))                     # (n, 1)
            X_aug = np.hstack([ones, X])               # (n, d+1)
            theta, *_ = np.linalg.lstsq(X_aug, y, rcond=None)  # (d+1,)
            return theta[1:], float(theta[0])
        theta, *_ = np.linalg.lstsq(X, y, rcond=None)  # (d,)
        return theta, 0.0

    def _fit_gd(self, X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
        # NN-style: w 和 b 是两个独立参数, 各算各的梯度, 各自 update.
        # 这才是 deep learning 通用范式; LR 只是它的一个 1-layer 特例.
        n, d = X.shape
        w = np.zeros(d)                                # (d,)
        b = 0.0 if self.fit_intercept else 0.0
        prev_loss = float("inf")
        self.training_loss_history = []
        for _ in range(self.max_iterations):
            pred = X @ w + b                           # (n,)
            residual = pred - y                        # (n,)
            grad_w = (2.0 / n) * (X.T @ residual)      # (d,)
            w -= self.learning_rate * grad_w
            if self.fit_intercept:
                grad_b = (2.0 / n) * float(residual.sum())  # scalar
                b -= self.learning_rate * grad_b
            cur_loss = float(np.mean(residual ** 2))
            self.training_loss_history.append(cur_loss)
            if abs(prev_loss - cur_loss) < self.convergence_threshold:
                break
            prev_loss = cur_loss
        return w, b

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRegression":
        if self.method == "closed_form":
            self.coef_, self.intercept_ = self._fit_closed_form(X, y)
        elif self.method == "gd":
            self.coef_, self.intercept_ = self._fit_gd(X, y)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.coef_ + self.intercept_
```

**Takeaway**: `_fit_gd` 里 `w` 和 `b` 是两个独立参数——这是 NN 训练循环
的通用模式 (一层 affine + bias). `_fit_closed_form` 里那个拼一列 1 的
augment-bias 技巧是 LR 闭式解专属, 因为 lstsq 一次只能解一个 $Ax = b$
线性系统; 一旦走 GD, 就不需要也不应该用这个 trick.

#### Closed-form vs Full-batch GD

|  | Closed-form (lstsq) | Full-batch GD |
|---|---|---|
| 求解 | SVD 一次出解 | 梯度迭代 $T$ 步 |
| 默认场景 | $d \le 10^3$ | $d \ge 10^4$ 或 $d \gg n$ |
| 失败模式 | $d^3$ 爆炸 | $\eta$ 大则发散 |
| Bias 怎么处理 | 拼一列 1, 折进 $w$ 一起解 (LR 专属技巧) | 独立参数 $b$, 独立 grad / update (NN 通用范式) |
| 复杂度 | $O(n d^2 + d^3)$ | $O(T \cdot n d)$ |
| LR 上界 | -- | $\eta < 2/\lambda_{\max}(X^T X / n)$; 先 standardize |

凸目标两者收敛到同一 $(w, b)$, 不一致 -> LR / iters 配错.

#### Sanity test

```python
np.random.seed(0)
N, D = 200, 5
X = np.random.randn(N, D)
true_w = np.random.randn(D)
y = X @ true_w + 0.01 * np.random.randn(N)
preds = LinearRegression().fit(X, y).predict(X)
print(f"MSE = {np.mean((preds - y) ** 2):.4f}")
```

### 7. Follow-up Q&A

**Q1. Ridge closed-form?**
$w = (X^T X + \lambda I)^{-1} X^T y$. $\lambda I$ 把所有特征值抬高
$\lambda$ -> 永远可逆, 即便 $d > n$ 或 $X$ 共线. 实现:
`solve(X.T @ X + lam * I, X.T @ y)`, 且 `I[0, 0] = 0` (不惩罚 intercept).

**Q2. Lasso 为什么没 closed-form?**
$\|w\|_1$ 在 $w_j = 0$ 不可导 (次梯度有跳变), 整体无解析极值. 但坐标
下降有逐元素闭式 -- soft-thresholding:
$w_j \leftarrow \text{sign}(z_j) \cdot \max(|z_j| - \lambda, 0)$.
这是 ISTA / coordinate descent 的基础.

**Q3. 共线 / $d \gg n$ 怎么办?**
$X^T X$ 奇异, $\kappa \to \infty$. 优先级: Ridge (一行 $\lambda I$) >
`lstsq` / `pinv` > VIF 删冗余 > PCA. $d \gg n$ (文本 / 基因) 必须正则化;
想要稀疏 $w$ + 特征选择则用 Lasso.

**Q4. Batch / Mini-batch / SGD?**
凸问题三者收敛到同一最优. Batch: 方差小, 内存吃紧; SGD: 方差大但
能跳鞍点; Mini-batch (32-256): 噪声 + GPU SIMD 折中, 工业默认.

**Q5. $w_j$ 的物理意义?**
其他特征不变时, $x_j$ 加 1 单位 -> $y$ 期望变化 $w_j$
(ceteris paribus). 前提: 特征不共线 (否则 $w_j$ 不唯一).

**Q6. 稀疏 $w^T x$ 怎么算?**
两边都有序 -> 双指针 $O(\text{nnz}_1 + \text{nnz}_2)$, cache 友好;
任一边无序 -> 哈希表查表 (hash join).
"""


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT id, title, notes FROM problems WHERE id = ?",
            (PROBLEM_ID,),
        ).fetchone()

        if row is None:
            print(
                f"[FAIL] problems.id={PROBLEM_ID} does not exist. "
                "This seed only fills the existing Linear Regression row "
                "and never creates one. Re-run "
                "scripts/content_meta_anc_linear_regression.py first."
            )
            return 1

        pid, title, old_notes = row
        old_notes = old_notes or ""

        if old_notes == NOTES:
            print(
                f"[SKIP] problems.id={pid} '{title[:60]}...' notes byte-equal "
                f"({len(old_notes)} chars). No write."
            )
            return 0

        conn.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (NOTES, pid),
        )
        conn.commit()
        was_null = "NULL" if not old_notes else f"{len(old_notes)} chars"
        print(
            f"[UPDATE] problems.id={pid} '{title[:60]}...' "
            f"notes {was_null} -> {len(NOTES)} chars (sentinel: {SENTINEL})"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
