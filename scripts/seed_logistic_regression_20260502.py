"""Seed: T-P0-689 [MLI-D2] -- Logistic Regression handwritten numpy in ml_coding.

Adds a new `problems` row mirroring the K-Means(1064) and KNN(1106) notes
style:
- title='Logistic Regression (Sigmoid + Stable BCE + GD)'
- category='ml_coding', difficulty='medium'
- notes contain: 题目描述 / 核心代码 (sigmoid, stable BCE FORMULA in code,
  gradient = X^T (sigma(Xw) - y) / n, full-batch GD, softmax extension) /
  关键要点 (numerical stability with the explicit |z| trick, class
  imbalance, L1/L2) / 面试追问 (Newton/IRLS, SGD, calibration, Platt) /
  复杂度.
- framework_node_id=211 ('Logistic Regression Loss').

Style anchors (per task spec):
1. T-P0-283 / T-P0-688 output (problems.id=1102 Linear Regression notes) --
   match section structure and prose style exactly.
2. problems.id=1064 K-Means -- canonical SECTION baseline (题目描述 /
   核心代码 / 关键要点 / 面试追问 / 复杂度).
3. problems.id=1106 KNN seed (T-P0-687) -- direct UPSERT template (canonical
   key = title + source).

Technical content highlights (per task spec):
- Forward: z = X w; p = sigma(z) = 1 / (1 + exp(-z)).
- Loss: BCE = -1/n * sum [y log p + (1 - y) log (1 - p)].
- Gradient: nabla_w = 1/n * X^T (sigma(X w) - y).
- **Stable BCE per-sample formula** (the EXPLICIT form, not just the words
  "log-sum-exp"): L_i = max(z_i, 0) - z_i * y_i + log(1 + exp(-|z_i|)).
  Implemented in code, with the |z| trick documented.
- Multi-class softmax extension: p_k = exp(z_k) / sum_j exp(z_j);
  cross-entropy gradient nabla_W = 1/n * X^T (P - Y).
- Regularization: L1 (subgradient sign(w) zeroed at the bias), L2 (2 lam w
  added to gradient, also zeroed at the bias).

Idempotency:
- Sentinel <!-- LOGISTIC_REGRESSION_20260502 --> at the top of the notes body.
- Canonical key for upsert: (title, source).
- INSERT skipped if a row with the same title+source already exists.
- UPDATE skipped if existing description+notes+framework_node_id match the
  canonical payload byte-for-byte. Otherwise the row is rewritten in place.
- Second run with no upstream change = 0 writes (verified manually after
  first run).
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Logistic Regression (Sigmoid + Stable BCE + GD)"
SOURCE = "ml-coding-handwritten-2026-05-02"
DIFFICULTY = "medium"
PATTERN = "ML Implementation"
CATEGORY = "ml_coding"
TAGS = '["ml-fundamentals", "logistic-regression", "implementation"]'
COMPANY_TAGS = '["Meta", "Uber", "DoorDash", "Pinterest"]'
PRIORITY = 1
FRAMEWORK_NODE_ID = 211  # ml-fundamentals/classical_ml/logistic-regression-loss

SENTINEL = "<!-- LOGISTIC_REGRESSION_20260502 -->"

DESCRIPTION = (
    "**Logistic Regression (Sigmoid + Stable BCE + GD)**: 从零实现二分类 "
    "Logistic Regression -- forward pass (sigmoid), 数值稳定的 BCE 损失 "
    "(显式 |z| 技巧, 不是仅口头说 'log-sum-exp'), 解析梯度 "
    "nabla_w = 1/n * X^T (sigma(Xw) - y), 以及 full-batch gradient descent "
    "训练循环. 同时给出 softmax / cross-entropy 的多分类扩展 "
    "(W shape (d, K), 梯度 1/n * X^T (P - Y)) 与 L1/L2 正则化在梯度上的修正.\n\n"
    "核心讨论点: (1) 为什么 LR 必须用 stable BCE -- 大 |z| 时 1+exp(-z) 上溢, "
    "log(1+exp(-z)) 下溢, 用 max(z,0) - z*y + log(1+exp(-|z|)) 一次性解决; "
    "(2) sigmoid 的导数 sigma'(z) = sigma(z)(1-sigma(z)), 二阶 Hessian = "
    "1/n * X^T diag(p (1-p)) X 严格半正定 -- LR 是凸优化, GD 必收敛到全局最优; "
    "(3) 类别不平衡: pos_weight 在 BCE 里的位置, focal loss 替代; "
    "(4) Newton / IRLS 与 GD 的关系, 何时换 quasi-Newton (L-BFGS); "
    "(5) calibration: Platt scaling vs isotonic regression; "
    "(6) L2 正则化对应 MAP + Gaussian prior, L1 对应 Laplace prior 与稀疏解; "
    "(7) 与 Linear Regression 的对比: 同样的 design matrix, 不同的 link function "
    "和 loss, 但梯度形式 1/n * X^T (prediction - y) 完全一致 (GLM 框架)."
)

NOTES = SENTINEL + r"""

## Logistic Regression (Sigmoid + Stable BCE + GD)

### 题目描述

给定 $X \in \mathbb{R}^{n \times d}$ 和 $y \in \{0, 1\}^{n}$, 二分类 Logistic
Regression 的目标是学到 $w \in \mathbb{R}^{d}$, 使得 $p_i = \sigma(x_i^T w)$
拟合 $P(y_i = 1 \mid x_i)$. 要求**手写**:

1. **Sigmoid forward**: $\sigma(z) = 1 / (1 + e^{-z})$.
2. **数值稳定的 BCE loss** (per-sample 形式, 必须给**显式公式**, 不是只说
   "用 log-sum-exp"):
   $$L_i = \max(z_i, 0) - z_i y_i + \log(1 + e^{-|z_i|})$$
   该写法对任意 $|z|$ 都不会上溢/下溢 (理由见关键要点 1).
3. **解析梯度**: $\nabla_w L = \frac{1}{n} X^T (\sigma(X w) - y)$.
4. **Full-batch GD**: $w \leftarrow w - \eta \cdot \nabla_w L$ 迭代到收敛.
5. **多分类扩展 (softmax + cross-entropy)**:
   $p_k = e^{z_k} / \sum_j e^{z_j}$, 梯度
   $\nabla_W L = \frac{1}{n} X^T (P - Y)$, 其中 $Y$ 是 one-hot.

随后回答 follow-up: Newton / IRLS, SGD, calibration (Platt scaling),
class imbalance, L1/L2.

### 核心代码

```python
import numpy as np
from typing import Literal, Optional


class LogisticRegression:
    # Logistic Regression (binary) with stable BCE + full-batch GD.
    #
    # Design choices (探讨于 "关键要点"):
    #   - Stable BCE: per-sample L_i = max(z, 0) - z*y + log(1 + exp(-|z|)).
    #     The "|z| trick" is the entire point -- naively computing
    #     log(1 + exp(-z)) overflows when z is large negative, and computing
    #     log(p) directly underflows when p ~= 0 or 1.
    #   - Gradient = (1/n) X^T (sigma(Xw) - y) -- same shape as Linear
    #     Regression's gradient, but with sigma applied to z (GLM family).
    #   - L2 regularization: gradient gets +2*lam*w (zero at the bias).
    #   - Bias-as-w[0] augmentation: same trick as Linear Regression.

    def __init__(
        self,
        learning_rate: float = 1e-1,
        max_iterations: int = 1000,
        convergence_threshold: float = 1e-6,
        l2_lambda: float = 0.0,
        fit_intercept: bool = True,
    ):
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.l2_lambda = l2_lambda
        self.fit_intercept = fit_intercept

        # Populated after fit():
        self.coef_: Optional[np.ndarray] = None         # shape (d,)
        self.intercept_: float = 0.0                     # scalar
        self.training_loss_history: list[float] = []     # per-iter BCE

    # ---- Helpers ----

    @staticmethod
    def _augment_with_bias(X: np.ndarray) -> np.ndarray:
        # Prepend a column of 1s so the bias term is folded into w[0].
        # Shape: (n, d) -> (n, d + 1). Identical trick to Linear Regression.
        n = X.shape[0]
        return np.hstack([np.ones((n, 1)), X])

    def _split_weights(self, w_full: np.ndarray) -> tuple[np.ndarray, float]:
        # (d+1,) -> (coef shape (d,), intercept scalar).
        return w_full[1:], float(w_full[0])

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        # Numerically stable sigmoid: split positive / negative branches.
        # For z >= 0:    sigma(z) = 1 / (1 + exp(-z))
        # For z <  0:    sigma(z) = exp(z) / (1 + exp(z))
        # Naive 1/(1+exp(-z)) overflows when z is very negative
        # (exp(-z) -> +inf). The branched form keeps every exp() argument
        # in (-inf, 0], where exp() is safely in [0, 1].
        out = np.empty_like(z, dtype=float)
        positive_mask = z >= 0
        # Positive branch: directly safe (exp(-z) in (0, 1]).
        out[positive_mask] = 1.0 / (1.0 + np.exp(-z[positive_mask]))
        # Negative branch: rewrite to avoid exp of large positive.
        exp_z_neg = np.exp(z[~positive_mask])
        out[~positive_mask] = exp_z_neg / (1.0 + exp_z_neg)
        return out

    @staticmethod
    def _stable_bce_loss(z: np.ndarray, y: np.ndarray) -> float:
        # The EXPLICIT stable BCE formula (per task spec -- give it in code,
        # not just words):
        #     L_i = max(z_i, 0) - z_i * y_i + log(1 + exp(-|z_i|))
        # Mean over samples returns the BCE for the batch.
        #
        # Derivation:
        #   BCE = -[y * log(sigma(z)) + (1 - y) * log(1 - sigma(z))]
        #       = -[y * log(1/(1+exp(-z))) + (1-y) * log(exp(-z)/(1+exp(-z)))]
        #       = -[y*(-log(1+exp(-z))) + (1-y)*(-z - log(1+exp(-z)))]
        #       = z - z*y + log(1 + exp(-z))                    -- (*)
        # For z >= 0,  log(1 + exp(-z)) is safe (exp arg in (-inf, 0]).
        # For z <  0,  log(1 + exp(-z)) overflows -- rewrite (*) using:
        #     log(1 + exp(-z)) = -z + log(1 + exp(z))
        # Combining both branches gives:
        #     L_i = max(z, 0) - z*y + log(1 + exp(-|z|))
        # The |z| inside exp() always makes the argument <= 0, so exp()
        # is in (0, 1] -- no overflow. log(1 + small) is in [log 1, log 2]
        # -- no underflow. This works for every finite z.
        return float(np.mean(
            np.maximum(z, 0.0) - z * y + np.log1p(np.exp(-np.abs(z)))
        ))

    # ---- Training loop (full-batch GD) ----

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticRegression":
        X_design = self._augment_with_bias(X) if self.fit_intercept else X
        n, d_aug = X_design.shape
        w = np.zeros(d_aug)
        previous_loss = float("inf")
        self.training_loss_history = []

        for _ in range(self.max_iterations):
            # Forward: logits z = X w, probabilities p = sigma(z).
            z = X_design @ w                                          # (n,)
            p = self._sigmoid(z)                                       # (n,)

            # Gradient: (1/n) X^T (p - y). For L2: + 2 lam * w_reg,
            # where w_reg masks out the bias (don't penalize intercept).
            gradient = (X_design.T @ (p - y)) / n                      # (d_aug,)
            if self.l2_lambda > 0.0:
                w_reg = w.copy()
                if self.fit_intercept:
                    w_reg[0] = 0.0
                gradient = gradient + 2.0 * self.l2_lambda * w_reg

            w = w - self.learning_rate * gradient

            # Track the stable BCE on the same batch for the loss curve.
            current_loss = self._stable_bce_loss(z, y)
            self.training_loss_history.append(current_loss)

            # Convergence: |L_{t-1} - L_t| < tol means the update is
            # numerically negligible. Could equivalently gate on
            # ||gradient||_2 < tol; both flag the same fixed point.
            if abs(previous_loss - current_loss) < self.convergence_threshold:
                break
            previous_loss = current_loss

        if self.fit_intercept:
            self.coef_, self.intercept_ = self._split_weights(w)
        else:
            self.coef_, self.intercept_ = w, 0.0
        return self

    # ---- Prediction ----

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # Returns P(y=1 | x). Use predict() for hard labels.
        z = X @ self.coef_ + self.intercept_
        return self._sigmoid(z)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        # Hard label using a probability threshold (default 0.5).
        # Tuning this threshold is the single most effective response to
        # class imbalance / asymmetric mis-classification cost -- see
        # 关键要点 #3.
        return (self.predict_proba(X) >= threshold).astype(int)


# ---- Multi-class extension: softmax cross-entropy ----

class SoftmaxRegression:
    # Softmax (multinomial logistic) regression with full-batch GD.
    # Same gradient pattern as binary case but with one-hot Y and W of
    # shape (d, K). The 1/n * X^T (P - Y) form generalizes directly.

    def __init__(self, n_classes: int, learning_rate: float = 1e-1,
                 max_iterations: int = 1000):
        self.n_classes = n_classes
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.W: Optional[np.ndarray] = None     # shape (d, K)

    @staticmethod
    def _softmax(Z: np.ndarray) -> np.ndarray:
        # Numerically stable softmax: subtract row-wise max BEFORE exp().
        # Without the shift, exp(z) overflows when any z is large; after
        # the shift, max(z) becomes 0 so exp(0) = 1 is the largest term --
        # bounded for any input. Same numerical idea as the |z| trick in
        # stable BCE, applied to a vector of logits.
        Z_shifted = Z - np.max(Z, axis=1, keepdims=True)
        exp_Z = np.exp(Z_shifted)
        return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)

    @staticmethod
    def _one_hot(y: np.ndarray, n_classes: int) -> np.ndarray:
        # (n,) -> (n, K) one-hot.
        Y = np.zeros((y.shape[0], n_classes))
        Y[np.arange(y.shape[0]), y] = 1
        return Y

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SoftmaxRegression":
        n, d = X.shape
        Y = self._one_hot(y, self.n_classes)                # (n, K)
        self.W = np.zeros((d, self.n_classes))              # (d, K)
        for _ in range(self.max_iterations):
            P = self._softmax(X @ self.W)                    # (n, K)
            # Gradient: (1/n) X^T (P - Y), shape (d, K).
            # Identical structure to binary case -- just stacked across
            # K columns. This is why softmax is "just multi-class LR".
            gradient = (X.T @ (P - Y)) / n
            self.W = self.W - self.learning_rate * gradient
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.argmax(X @ self.W, axis=1)
```

### 关键要点

**1. 为什么必须用 stable BCE -- 显式 |z| 技巧 (NOT just "log-sum-exp")**

朴素写法 `-(y * np.log(p) + (1 - y) * np.log(1 - p))` 在两个方向都会爆:

- 当 $z \to +\infty$, $p = \sigma(z) \to 1$, $1 - p$ 触底为 `0.0`,
  $\log(1 - p) = -\infty$, 整个 loss 变 `nan`.
- 当 $z \to -\infty$, $p \to 0$, 同理 $\log p = -\infty$ 也炸.
- 你也不能"先 clip $p$ 到 $[\varepsilon, 1-\varepsilon]$"了事 -- 那只是把
  数值错误藏起来, 大 $|z|$ 时梯度仍然会偏离 sigma 的真梯度, 训练不收敛.

正确做法是把 BCE 重写到 **logits $z$ 上**, 永远不显式做 $\log(\sigma(z))$:

$$L_i = z_i - z_i y_i + \log(1 + e^{-z_i})$$

对 $z < 0$ 这一项里 $e^{-z}$ 仍然会上溢 ($e^{30} \approx 10^{13}$,
$e^{800}$ 就 `inf` 了). 用恒等式 $\log(1 + e^{-z}) = -z + \log(1 + e^{z})$
换一边再合并, 得到无论 $z$ 正负都安全的形式:

$$\boxed{L_i = \max(z_i, 0) - z_i y_i + \log(1 + e^{-|z_i|})}$$

- $\max(z, 0)$ 把 "$z$ 大正时主导项" 显式提出来 (本质是 ReLU on logits).
- $\log(1 + e^{-|z|})$ 永远在 $[\log 1, \log 2] = [0, 0.693]$ 区间, 既不
  上溢也不下溢.

**面试金句**: "**`max(z, 0) - z*y + log(1 + exp(-|z|))`. 这一行就是 stable
BCE, 它在 logits 上算, 永远不会触碰 $\log(0)$, 是 PyTorch
`F.binary_cross_entropy_with_logits` 的实现核心**".

**2. Sigmoid 的导数与 LR 是凸问题**

$\sigma'(z) = \sigma(z)(1 - \sigma(z))$. 因此梯度的链式:

$$\nabla_w L = \frac{1}{n} X^T (\sigma(X w) - y)$$

- 形式上和 Linear Regression 的 $\frac{1}{n} X^T (Xw - y)$ **完全同构** --
  这就是 GLM (generalized linear model) 框架的核心: 不同 link function +
  不同 loss, 但梯度都是 "$X^T$ 乘以 (prediction - target) / n".
- Hessian: $\nabla^2_w L = \frac{1}{n} X^T \mathrm{diag}(p(1-p)) X$, 严格
  半正定 (PSD), 所以 LR 损失是**凸函数**, GD 必收敛到全局最优.
- $p(1-p) \in (0, 0.25]$, $\sigma'$ 在 $z = 0$ 取最大. 当 $|z|$ 很大时
  $p(1-p) \to 0$, 梯度变得很小 -- "**置信样本不再贡献梯度**"是一个常被
  忽略的直觉 (类似饱和神经元).

**3. 类别不平衡 (class imbalance)**

正负样本比 1:99 时, 朴素 LR 会把大多数 $p$ 预测成接近 0 的小数, 决策阈值
0.5 永远被超不过 -- **AUC 可能很高, 但 recall=0**. 处理方式按优先级:

- **调阈值**: 训练不变, predict 时把阈值从 0.5 降到 (验证集 ROC 上) 让
  recall/precision 平衡的位置. 单这一步就能解决大多数实际问题, 不需动模型.
- **Class weights / pos_weight**: BCE 改成
  $L = -\frac{1}{n} \sum [\beta y \log p + (1 - y) \log(1 - p)]$,
  $\beta$ = neg/pos 比例, 等价于"每个正样本算 $\beta$ 次".
- **Resampling**: 上采样少数类 (SMOTE) 或下采样多数类. 简单粗暴, 但下采样
  会丢信息, 上采样会过拟合复制点; 一般在数据极度不平衡 (1:1000+) 才考虑.
- **Focal loss**: $-(1 - p_t)^\gamma \log p_t$ 对易分样本降权, 强化难样本.
  $\gamma = 2$ 是常用值, 来自 RetinaNet.

**4. L2 / L1 正则化在梯度上的修正**

- **L2 (Ridge)**: 损失加 $\lambda \|w\|_2^2$, 梯度加 $2 \lambda w$.
  对应贝叶斯 MAP + Gaussian prior $w \sim \mathcal{N}(0, 1/(2\lambda))$.
- **L1 (Lasso)**: 损失加 $\lambda \|w\|_1$, **次梯度** $\lambda \mathrm{sign}(w)$
  ($w = 0$ 处取 0). 对应 Laplace prior, 给出**稀疏解** (一些 $w_j$ 严格为 0).
- **bias 不该被惩罚**: 数学上 $\lambda \|w\|^2$ 写完整应改成
  $\lambda \mathrm{diag}([0, 1, \dots, 1]) \cdot w$, 实现里
  `w_reg = w.copy(); w_reg[0] = 0.0`.

**5. 训练稳定性: 标准化 + 学习率上界**

- **特征标准化 (zero-mean unit-variance) 是前置必修**, 不然不同尺度的
  特征会让 $\nabla_w L$ 的每个分量量级悬殊, GD 折返跳跃. 这与 Linear
  Regression 同源.
- 收敛要求 $\eta < 2 / \lambda_{\max}(X^T \mathrm{diag}(p(1-p)) X / n)$.
  实战不动这个公式, 直接用 `lr=0.1` (标准化后) 起步, 不收敛再砍半.

### 面试追问

- **Q1: Newton's method / IRLS 与 GD 的关系是什么?**
  Newton step: $w \leftarrow w - H^{-1} \nabla L$, 其中
  $H = \frac{1}{n} X^T \mathrm{diag}(p(1-p)) X$. 因为 LR 是凸 + Hessian
  解析可得, Newton 二阶收敛 (每一步误差平方下降), 比 GD 的线性收敛快得多.
  IRLS (Iteratively Reweighted Least Squares) 是 Newton 在 LR 上的具体
  形式 -- 把每一步重写成一个加权 least-squares: 用 $W = \mathrm{diag}(p(1-p))$
  解 $X^T W X \cdot \Delta w = X^T (y - p)$.
  - 代价: 每步要解 $d \times d$ 的线性系统, 复杂度 $O(d^3)$. 当 $d$ 大
    ($\ge 10^4$) 时不可承受 -- 此时退到 GD/SGD/L-BFGS.
  - **L-BFGS** 是常见折中: quasi-Newton, 用历史梯度近似 Hessian, 只需
    $O(d)$ 内存 (sklearn `LogisticRegression(solver='lbfgs')` 默认).

- **Q2: SGD vs full-batch GD?**
  - full-batch: 每步用全部 $n$ 个样本, 梯度无偏 + 方差为 0, 但单步
    $O(n d)$, $n$ 极大时单步装不下.
  - **SGD**: 每步 1 个样本 (或 mini-batch 32/64), 梯度无偏但方差大.
    噪声让训练有概率跳出鞍点 / 平坦区, 在高维非凸问题里反而泛化更好.
    LR 是凸, SGD 与 GD 都收敛到同一全局最优.
  - mini-batch 是工业默认, 配合 SIMD/GPU 一次填满, 噪声仍存在.

- **Q3: Calibration -- LR 输出的 $p$ 是真概率吗? Platt scaling 怎么做?**
  LR 输出在交叉熵下**理论上是 calibrated**, 但实战常因为正则化 / 类别
  不平衡 / decision threshold 调整而偏离. 检查方式: **reliability diagram**
  (把 predict_proba 分箱, 看每箱平均预测 vs 实际频率, 完美 calibration
  应贴对角线).
  - **Platt scaling**: 在验证集上额外训一个 **1D logistic regression**:
    $P_{\text{cal}}(y=1) = \sigma(a \cdot s + b)$, 其中 $s$ 是模型的 raw
    logit / score, $a, b$ 由 BCE 在验证集上拟合. 等价于"把模型输出再
    pass 一个 sigmoid 校准". SVM 这类不输出概率的模型最常用.
  - **Isotonic regression**: 非参数, 拟合一个单调映射, 比 Platt 更灵活
    但需要更多验证数据 (>1000), 否则过拟合.
  - **Temperature scaling**: 神经网络专用, 把 logits 除以一个标量 $T$
    再过 softmax, 只学一个参数, 不会改变 argmax (predicted label 不变).

- **Q4: LR vs Naive Bayes, LR vs SVM?**
  - **LR vs Naive Bayes**: 同一个 $P(y \mid x)$ 拟合目标. NB 走 generative
    路径 ($P(x \mid y) P(y)$, 假设特征条件独立), LR 走 discriminative
    路径 (直接学 $P(y \mid x)$). 数据少时 NB 占优 (强先验抵御过拟合),
    数据多时 LR 通常更准 (没有独立性假设).
  - **LR vs SVM**: 都是线性分类器, 都凸优化. 区别在 loss -- LR 是 logistic
    loss (smooth, 永远有梯度), SVM 是 hinge loss (margin > 1 时梯度 0,
    "已分对的点不再驱动训练"). LR 给概率, SVM 给 margin. 高维稀疏
    (text classification) 时 SVM 历史上更受欢迎, 现在 LR + L1 也常用.

- **Q5: 多分类 -- One-vs-Rest 还是 Softmax (multinomial)?**
  - **OvR**: 训 $K$ 个独立的二分类 LR, 每个把第 $k$ 类当正类. 预测时取
    $\arg\max$. 简单, 易并行, 但 $K$ 个分类器互相不一致, $\sum p_k \ne 1$.
  - **Softmax / multinomial**: 单一模型, $W$ shape $(d, K)$, 直接拟合
    $p_k = \mathrm{softmax}(z)$, $\sum p_k = 1$ 自然成立. 损失是
    cross-entropy $-\frac{1}{n} \sum_i \sum_k y_{ik} \log p_{ik}$.
  - sklearn 默认用 multinomial (`multi_class='auto'` 在 solver 支持时
    选 multinomial). 类别多 + 数据足 -> multinomial; 类别极多
    ($K \ge 10^4$, 比如词表) -> hierarchical softmax / sampled softmax.

### 复杂度

- **训练 (full-batch GD)**: 单步 $O(n d)$ (一次 $X w$, 一次 $X^T (p - y)$).
  $T$ 步迭代 -> $O(T n d)$. 凸问题在合理 $\eta$ 下 $T$ 通常 $10^2 \sim 10^3$.
- **训练 (Newton / IRLS)**: 单步 $O(n d^2 + d^3)$ -- $n d^2$ 来自
  $X^T W X$, $d^3$ 来自解线性系统. $d \le 10^3$ 时一两步就收敛, 总 cost
  仍可能比 GD 低.
- **预测**: $O(d)$ per sample (一次点积 + 一次 sigmoid).
- **空间**: $O(d)$ for $w$, $O(n d)$ for $X$. 与 KNN 的 $O(n d)$ 训练空间
  形成鲜明对比 -- LR 训完丢掉 $X$, 只留 $w$, 这是它在工业上长盛不衰的
  根本原因.

### 多分类: softmax + cross-entropy 一并给出

二分类 LR 的所有结论自然推广:
- **Softmax**: $p_k = e^{z_k} / \sum_j e^{z_j}$, **stable trick** = 减去
  $\max_j z_j$ 再 exp (与 stable BCE 的 $|z|$ 技巧同一思想).
- **Cross-entropy loss**: $L = -\frac{1}{n} \sum_i \sum_k y_{ik} \log p_{ik}$,
  其中 $Y$ 是 one-hot.
- **梯度**: $\nabla_W L = \frac{1}{n} X^T (P - Y)$, 形式与二分类完全
  一致 -- 这是 softmax + cross-entropy 设计的优雅之处, 把 "softmax 求导
  乘 cross-entropy 求导" 的复杂链式规则消化掉, 留下最简形式.
- **二分类是 softmax 的 $K = 2$ 特例** (在 $w_0 = 0$ 的约束下), 数学上完全
  等价, 实现上分开写是为了 BCE 比 cross-entropy + one-hot 略省一点
  (单个 logit vs 两个 logits).
"""


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        # Verify framework_node 211 exists (precondition).
        node_row = conn.execute(
            "SELECT id, title FROM framework_nodes WHERE id = ?",
            (FRAMEWORK_NODE_ID,),
        ).fetchone()
        if node_row is None:
            print(
                f"[FAIL] framework_nodes.id={FRAMEWORK_NODE_ID} "
                "('Logistic Regression Loss') does not exist. "
                "This seed expects the node to be present."
            )
            return 1

        row = conn.execute(
            "SELECT id, description, notes, framework_node_id "
            "FROM problems WHERE title = ? AND source = ?",
            (TITLE, SOURCE),
        ).fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        if row is None:
            cur = conn.execute(
                "INSERT INTO problems "
                "(title, description, notes, difficulty, pattern, "
                "category, tags, source, company_tags, priority, "
                "framework_node_id, "
                "is_completed, comfort_level, description_source, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "0, 0, 'manual', ?)",
                (
                    TITLE,
                    DESCRIPTION,
                    NOTES,
                    DIFFICULTY,
                    PATTERN,
                    CATEGORY,
                    TAGS,
                    SOURCE,
                    COMPANY_TAGS,
                    PRIORITY,
                    FRAMEWORK_NODE_ID,
                    now,
                ),
            )
            new_id = int(cur.lastrowid or 0)
            conn.commit()
            print(
                f"[INSERT] '{TITLE}' id={new_id} "
                f"description={len(DESCRIPTION)} notes={len(NOTES)} chars "
                f"framework_node_id={FRAMEWORK_NODE_ID}"
            )
            return 0

        pid, old_desc, old_notes, old_node_id = row
        old_desc = old_desc or ""
        old_notes = old_notes or ""

        if (
            old_desc == DESCRIPTION
            and old_notes == NOTES
            and old_node_id == FRAMEWORK_NODE_ID
        ):
            print(
                f"[SKIP] id={pid} '{TITLE}' description+notes byte-equal "
                f"(desc={len(old_desc)} notes={len(old_notes)} "
                f"node={old_node_id})"
            )
            return 0

        conn.execute(
            "UPDATE problems "
            "SET description = ?, notes = ?, difficulty = ?, pattern = ?, "
            "    category = ?, tags = ?, company_tags = ?, priority = ?, "
            "    framework_node_id = ? "
            "WHERE id = ?",
            (
                DESCRIPTION,
                NOTES,
                DIFFICULTY,
                PATTERN,
                CATEGORY,
                TAGS,
                COMPANY_TAGS,
                PRIORITY,
                FRAMEWORK_NODE_ID,
                pid,
            ),
        )
        conn.commit()
        print(
            f"[UPDATE] id={pid} '{TITLE}' "
            f"desc {len(old_desc)} -> {len(DESCRIPTION)}, "
            f"notes {len(old_notes)} -> {len(NOTES)} chars, "
            f"node {old_node_id} -> {FRAMEWORK_NODE_ID}"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
