"""Seed: T-P0-688 [MLI-D1] -- Linear Regression handwritten numpy in ml_coding.

Fills the existing `problems` row id=1102 ('Meta AI-Native Coding - Linear
Regression ...') by UPSERTing its `notes` field. The row already has a rich
description (the Meta AI-Native cheat-sheet drawer); the notes column has
been NULL up to now and is the surface that /problems/1102 renders as the
"handwritten implementation" companion to the description.

Style anchor (TWO sources, both reflected here):
1. problems.id=1064 K-Means -- SECTION STRUCTURE
   (题目描述 / 核心代码 / 关键要点 / 面试追问 / 复杂度).
2. company_documents.id=90 cheat-sheet row 5 -- COLUMN HINTS
   ($w = (X^T X)^{-1} X^T y$, np.linalg.lstsq 不显式求逆,
   $O(n d^2 + d^3)$, Ridge/Lasso/SGD).

Technical content (per task spec):
- Code MUST NOT use np.linalg.inv. We use np.linalg.lstsq(X, y, rcond=None)
  for the primary closed-form path, and np.linalg.solve for the Ridge path
  where lstsq does not directly apply to the regularized normal equations.
  Comment block explains WHY: ill-conditioned X^T X amplifies error;
  lstsq uses SVD/QR internally and is numerically stable. The cheat-sheet
  itself prescribes this -- the code must not contradict its own index.
- TWO code paths: closed-form (lstsq) and iterative (full-batch GD).
- Follow-ups: Ridge via solve (NOT inv), Lasso ISTA / coordinate descent,
  SGD variant.

Idempotency:
- Sentinel <!-- META_AI_NATIVE_LR_20260502 --> at the top of the notes body.
- UPDATE skipped if existing notes are byte-equal to the canonical payload.
  Second run with no upstream change = 0 writes.
- NO new problems row -- this script only ever writes to problems.id=1102.
  If id=1102 is missing, we abort with a clear error (it is a precondition
  established by an earlier seed; we never re-create it here).
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PROBLEM_ID = 1102
SENTINEL = "<!-- META_AI_NATIVE_LR_20260502 -->"

NOTES = SENTINEL + r"""

## Linear Regression (closed-form lstsq + Full-Batch GD)

### 题目描述

给定 $X \in \mathbb{R}^{n \times d}$ 和 $y \in \mathbb{R}^{n}$, 最小化
$L(w) = \|Xw - y\|^2$, 求 $w \in \mathbb{R}^{d}$. 要求**手写**两条路径:
1. **Closed-form (normal equation)**: $w = (X^T X)^{-1} X^T y$.
   实现时**不准用 `np.linalg.inv`**, 用 `np.linalg.lstsq` (SVD/QR 内部
   分解, 数值最稳) 或 `np.linalg.solve` (LU 分解解 $Ax = b$).
2. **Full-batch gradient descent**: $w \leftarrow w - \eta \cdot \frac{2}{n}
   X^T (Xw - y)$, 用 GD 把 $w$ 迭代到收敛, 可与 closed-form 比对验证.

随后回答 follow-up: Ridge / Lasso / SGD 三个变体怎么改.

### 核心代码

```python
import numpy as np
from typing import Literal, Optional


class LinearRegression:
    # Closed-form (lstsq) + Full-batch GD reference implementation.
    #
    # Why no np.linalg.inv:
    #   The textbook formula w = (X^T X)^{-1} X^T y is ALWAYS implemented
    #   without forming the inverse explicitly. (X^T X) often has a large
    #   condition number kappa(X^T X) = kappa(X)^2 -- forming the inverse
    #   amplifies floating-point error by kappa^2. lstsq uses SVD (or QR
    #   under rcond=None) and applies the pseudo-inverse stably; solve
    #   uses LU on the system A w = b without ever forming A^{-1}.
    #   Cost is essentially the same; numerical stability is dramatically
    #   better. The cheat-sheet for problem 1102 prescribes lstsq; the
    #   implementation MUST NOT contradict its own index.

    def __init__(
        self,
        method: Literal["closed_form", "gd"] = "closed_form",
        fit_intercept: bool = True,
        # GD-only hyperparameters (ignored for closed-form):
        learning_rate: float = 1e-2,
        max_iterations: int = 1000,
        convergence_threshold: float = 1e-6,
    ):
        self.method = method
        self.fit_intercept = fit_intercept
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold

        # Populated after fit():
        self.coef_: Optional[np.ndarray] = None         # shape (d,)
        self.intercept_: float = 0.0                     # scalar
        self.training_loss_history: list[float] = []     # GD trace

    # ---- Helpers ----

    @staticmethod
    def _augment_with_bias(X: np.ndarray) -> np.ndarray:
        # Prepend a column of 1s so the bias term is folded into w[0].
        # Shape: (n, d) -> (n, d + 1).
        n = X.shape[0]
        return np.hstack([np.ones((n, 1)), X])

    def _split_weights(self, w_full: np.ndarray) -> tuple[np.ndarray, float]:
        # Split a (d+1,) weight vector back into (coef shape (d,), intercept).
        return w_full[1:], float(w_full[0])

    @staticmethod
    def _mse(X: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
        # Mean squared error, used as both loss and convergence criterion.
        residual = X @ w - y
        return float(np.mean(residual ** 2))

    # ---- Path 1: closed-form via lstsq (NOT inv) ----

    def _fit_closed_form(self, X_design: np.ndarray, y: np.ndarray) -> np.ndarray:
        # Solve min ||X_design @ w - y||^2 directly. lstsq returns
        # (solution, residuals, rank, singular_values); we only need the
        # solution. rcond=None silences a future-warning and uses the
        # machine-epsilon-scaled cutoff (the recommended default).
        #
        # Equivalent LU path (also acceptable; pick ONE):
        #     A = X_design.T @ X_design     # (d+1, d+1)
        #     b = X_design.T @ y            # (d+1,)
        #     return np.linalg.solve(A, b)
        # solve avoids forming A^{-1} but DOES form A = X^T X, so it
        # squares the condition number; lstsq operates on X_design directly
        # and is the strictly more stable choice when n > d.
        w_full, *_ = np.linalg.lstsq(X_design, y, rcond=None)
        return w_full

    # ---- Path 2: full-batch gradient descent ----

    def _fit_gd(self, X_design: np.ndarray, y: np.ndarray) -> np.ndarray:
        # Gradient of (1/n) ||Xw - y||^2 is (2/n) X^T (Xw - y).
        # Full-batch: every step uses the entire dataset -> deterministic,
        # smooth descent, but O(n*d) per step. For LR with convex L,
        # constant learning rate gives linear convergence when eta is
        # below 2 / lambda_max(X^T X / n).
        n, d_aug = X_design.shape
        w = np.zeros(d_aug)
        previous_loss = float("inf")
        self.training_loss_history = []

        for _ in range(self.max_iterations):
            residual = X_design @ w - y                          # (n,)
            gradient = (2.0 / n) * (X_design.T @ residual)        # (d_aug,)
            w = w - self.learning_rate * gradient

            current_loss = self._mse(X_design, y, w)
            self.training_loss_history.append(current_loss)

            # Convergence: |L_{t-1} - L_t| < tol means the update is
            # numerically negligible. (Could also gate on ||grad||_2.)
            if abs(previous_loss - current_loss) < self.convergence_threshold:
                break
            previous_loss = current_loss

        return w

    # ---- Public API ----

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRegression":
        X_design = self._augment_with_bias(X) if self.fit_intercept else X

        if self.method == "closed_form":
            w_full = self._fit_closed_form(X_design, y)
        elif self.method == "gd":
            w_full = self._fit_gd(X_design, y)
        else:
            raise ValueError(f"Unknown method: {self.method}")

        if self.fit_intercept:
            self.coef_, self.intercept_ = self._split_weights(w_full)
        else:
            self.coef_, self.intercept_ = w_full, 0.0
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.coef_ + self.intercept_
```

### 关键要点

**1. 为什么必须用 `lstsq` / `solve` 而不是 `inv`**

教科书公式 $w = (X^T X)^{-1} X^T y$ 的字面实现是
`np.linalg.inv(X.T @ X) @ X.T @ y` -- 这条路径在工业代码里**永远不写**, 原因是
**数值稳定性**, 不是性能:

- $X^T X$ 的 condition number 是 $X$ 的 condition number 的**平方**:
  $\kappa(X^T X) = \kappa(X)^2$. 显式求逆把浮点误差放大 $\kappa^2$ 倍.
- `lstsq` 内部走 SVD (或 QR, 取决于 numpy 版本与 `rcond`), 直接对 $X$
  做分解, 不构造 $X^T X$, 误差只受 $\kappa(X)$ 影响 -- 量级少一倍.
- `solve(X.T @ X, X.T @ y)` 走 LU 分解, 不显式求逆, 但仍构造了 $X^T X$,
  数值稳定性介于 `inv` 和 `lstsq` 之间. **$n > d$ 时首选 `lstsq`**.
- 速度上 `inv`/`solve`/`lstsq` 同量级 ($O(d^3)$), 没有"快慢"理由选 `inv`.

**面试金句**: "**$\kappa(X^T X) = \kappa(X)^2$, 所以显式求逆把误差放大一个量级.
`lstsq` 直接 SVD $X$ 是数值最稳的写法, cheat-sheet 写的就是它**".

**2. Closed-form 与 GD 互为 ground truth**

写两条路径不是为了"两选一", 而是**互验**:
- closed-form 一发解出 (单次 SVD), 是 reference solution.
- GD 迭代 100\~1000 步逼近, 应当**收敛到与 closed-form 数值上相近**的 $w$
  (`np.allclose(w_gd, w_closed_form, atol=1e-3)`). 不一致就是 GD 的
  learning rate / 收敛阈值 / 迭代步数没设好.
- 工程意义: $d$ 很小 (千以下) 时直接 closed-form; $d$ 很大 ($\ge 10^4$) 时
  $X^T X$ 的 $d^3$ 不可接受, 必须 GD/SGD.

**3. Bias 项的拼接技巧**

把 intercept 写成 $w_0$ 而不是单独存一个 scalar, 数学上等价于
$X_{\text{design}} = [\mathbf{1}_n \mid X]$, 维度从 $(n, d) \to (n, d+1)$.
- 好处: closed-form 与 GD 共用同一套矩阵代数, 不需要在每个 path 里
  单独维护 intercept.
- 坏处: 加正则化时, **bias 通常不应被惩罚** (Ridge / Lasso 默认 not
  penalize intercept). 这时 design matrix 那一列 1 在正则项里要
  跳过 -- 实现细节: $\lambda I$ 改成 $\lambda \cdot \text{diag}([0, 1,
  \dots, 1])$.

**4. GD 的 learning rate 上界**

收敛要求 $\eta < 2 / \lambda_{\max}(X^T X / n)$, 否则发散.
- 实战: 先做 feature standardization (zero-mean unit-variance), 这一步会
  让 $\lambda_{\max}$ 落在 $O(1)$ 量级, 然后 $\eta = 10^{-2}$ 之类的
  典型值就稳了.
- 没标准化时直接上小 $\eta$ ($10^{-6}$) 是 hack, 表面上能跑但会非常慢.
  做 standardization 是**前置必修**, 不是 nice-to-have.

**5. 收敛判据**

实现里用 $|L_{t-1} - L_t| < \text{tol}$, 还有几种等价写法:
- $\|\nabla L\|_2 < \text{tol}$ -- 直接看梯度是否归零, 更"原教旨".
- $\|w_t - w_{t-1}\|_2 < \text{tol}$ -- 看权重是否还在变.
- 三者在凸目标 + 学习率合理时同向, 实战常报告其中一个即可.

### 面试追问

- **Q1: Ridge regression 怎么改?**
  正规方程改成 $(X^T X + \lambda I) w = X^T y$. **仍然不准用 `inv`** ——
  改用 `solve`:
  ```python
  d_aug = X_design.shape[1]
  reg = lam * np.eye(d_aug)
  reg[0, 0] = 0.0   # 默认不惩罚 intercept
  w = np.linalg.solve(X_design.T @ X_design + reg, X_design.T @ y)
  ```
  关键洞察: $\lambda I$ 把 $X^T X$ 的所有特征值抬高 $\lambda$,
  $(X^T X + \lambda I)$ **永远可逆**, 即使 $X$ 共线 / $d > n$ 也不奇异.
  这就是 Ridge 默认更稳的原因.

- **Q2: Lasso 为什么没 closed-form?**
  L1 项 $\|w\|_1$ 在 $w_j = 0$ 处不可导 (左导 -1, 右导 +1, 跳变 / 次梯度).
  整体 $L(w) = \|Xw - y\|^2 + \lambda \|w\|_1$ 不能一次性解析解.
  **但是**逐元素 (coordinate descent) 子问题可以: 固定其它维度,
  $w_j$ 的最优解是 **soft-thresholding**:
  $$w_j \leftarrow \text{sign}(z_j) \cdot \max(|z_j| - \lambda, 0)$$
  其中 $z_j$ 是 partial residual 投影到第 $j$ 列的内积.
  这是 **ISTA** (Iterative Soft-Thresholding Algorithm) /
  **coordinate descent** 的更新规则; 整体迭代收敛.

  金句: "**Lasso 没有整体 closed-form, 但有 coordinate-wise closed-form**".

- **Q3: SGD 与 full-batch GD 的差别?**
  - full-batch: 每步用全部 $n$ 个样本, 梯度无偏 + 方差小, 内存吃紧
    ($n$ 很大时单步装不下).
  - **SGD**: 每步用 1 个样本 (或 mini-batch 的 32 / 64), 梯度无偏但
    方差大. **方差不是 bug 是 feature** -- 噪声让梯度有概率跳出鞍点 /
    弱局部极小, 实战中泛化也常常更好.
  - mini-batch 是事实工业默认: 兼顾 SIMD/GPU 并行 (一次填满) 与
    噪声探索 (32\~256 个样本远小于 $n$).
  - LR 是凸问题, 三者最终都收敛到同一全局最优, 差别只在收敛路径与速度.

- **Q4: 共线 (collinearity) 怎么办?**
  $X$ 的列线性相关 -> $X^T X$ 离奇异更近 -> $\kappa(X^T X) \to \infty$.
  方案 (优先级):
  1. 走 Ridge (一行加 $\lambda I$, 默认稳).
  2. 走 `pinv` (Moore-Penrose 伪逆, SVD 处理奇异).
  3. 删冗余列: VIF (variance inflation factor) 找共线列直接砍.
  4. 上 PCA 降维到不相关的主成分上再拟合.

- **Q5: $d \gg n$ (e.g. 文本 / 基因组) 怎么办?**
  $X^T X$ 必奇异, $w$ 不唯一. 必须正则化 (Ridge / Lasso) 或 走 `pinv`
  (取最小范数解). 工业默认: Lasso, 因为它顺带做特征选择 (稀疏 $w$).

### 复杂度

- **Closed-form (lstsq)**: $O(n d^2 + d^3)$ -- $X^T X$ 的矩阵乘是 $n d^2$,
  SVD/LU 分解是 $d^3$. $n \gg d$ 时 $n d^2$ 主导; $d$ 大 (千以上) 时
  $d^3$ 爆炸, 改 GD/SGD.
- **Full-batch GD**: $O(\text{iter} \cdot n d)$ per pass over data;
  收敛到 $\epsilon$ 误差需要 $O(\log(1/\epsilon))$ 步 (强凸, 凸时是 $O(1/\epsilon)$).
- **空间**: closed-form $O(d^2)$ for $X^T X$; GD $O(d)$ for $w$ + $O(nd)$
  for $X$. GD 在 $d$ 极大时空间也更省.
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
