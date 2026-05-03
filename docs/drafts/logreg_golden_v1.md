# Logistic Regression (Sigmoid + Stable BCE + GD)

> **TL;DR** -- 二分类 GLM, $$p = \sigma(Xw)$$, MLE 等价最小化 BCE; 全程在 logits 上算, 永不 `log(0)`.
> **灵魂 = 数值稳定性**: stable BCE $$L = \max(z,0) - zy + \log(1 + e^{-|z|})$$ (= `np.logaddexp(0, z) - z*y` = `F.binary_cross_entropy_with_logits`).
> **核心三步**: (1) 前向 $$z = Xw, p = \sigma(z)$$; (2) 梯度 $$\nabla L = \frac{1}{n} X^T(p - y)$$; (3) GD 到 $$|\Delta L| < \text{tol}$$ 或 max iter.
> **凸保证**: Hessian $$\frac{1}{n} X^T \mathrm{diag}(p(1-p)) X \succeq 0$$, GD 必收敛全局最优; **无闭式解** (sigmoid 把似然变非二次).
> **复杂度**: GD 单步 $$O(nd)$$, 总 $$O(Tnd)$$; Newton/IRLS 单步 $$O(nd^2 + d^3)$$; 推理 $$O(d)$$.

---

## 实现

### 0. Class skeleton

```python
import numpy as np
from typing import Optional

class LogisticRegression:
    def __init__(self, learning_rate: float = 1e-1,
                 max_iterations: int = 1000,
                 convergence_threshold: float = 1e-6,
                 l2_lambda: float = 0.0,
                 fit_intercept: bool = True):
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.l2_lambda = l2_lambda
        self.fit_intercept = fit_intercept
        self.coef_: Optional[np.ndarray] = None         # (d,)
        self.intercept_: float = 0.0                     # scalar
        self.training_loss_history: list[float] = []     # per-iter BCE
```

### 1. Bias augmentation

把 intercept 折成 $$w_0$$, design matrix 多一列 1; 梯度 / 更新代码与无 bias 共用一份, 仅在 L2 时把 `w_reg[0] = 0` 排除掉 (bias 不该被惩罚).

```python
@staticmethod
def _augment_with_bias(X):
    # X: (n, d)
    n = X.shape[0]
    ones = np.ones((n, 1))                            # (n, 1)
    return np.hstack([ones, X])                       # (n, d+1)
```

### 2. Sigmoid -- branched to avoid overflow

朴素 `1 / (1 + exp(-z))` 在 $$z$$ 大负时 $$e^{-z}$$ 上溢. 按符号分支保证 `exp` argument 始终 $$\leq 0$$, 落在 $$(0, 1]$$ 安全区.

```python
@staticmethod
def _sigmoid(z):
    # z: (n,)
    out = np.empty_like(z, dtype=float)              # (n,)
    pos = z >= 0                                      # (n,) bool
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    exp_z = np.exp(z[~pos])                          # exp arg <= 0
    out[~pos] = exp_z / (1.0 + exp_z)
    return out                                        # (n,)
```

### 3. Numerical stability -- 这道题的灵魂

**这是规范唯一允许内嵌数学推导的 section** -- LR 的工业含金量 80% 落在这一行公式上.

**朴素 BCE 的两路爆炸**: $$L = -[y \log p + (1-y) \log(1-p)]$$ 中, $$z \to +\infty$$ 时 $$p \to 1$$, $$1-p$$ 触底 `0.0`, $$\log(1-p) = -\infty$$ 整个 loss 变 NaN; $$z \to -\infty$$ 同理 $$\log p$$ 爆. Clip $$p$$ 到 $$[\varepsilon, 1-\varepsilon]$$ 是把错误藏起来 -- 大 $$|z|$$ 时梯度仍偏离 sigma 真梯度, 训练不收敛.

**正确做法: 全程在 logits $$z$$ 上算**. 先把 BCE 改写到 $$z$$ 上:

$$L_i = z_i - z_i y_i + \log(1 + e^{-z_i})$$

但 $$z < 0$$ 时 $$e^{-z}$$ 仍上溢 ($$e^{800}$$ 即 `inf`). 用恒等式 $$\log(1 + e^{-z}) = -z + \log(1 + e^{z})$$ 换边再合并两支:

$$\boxed{L_i = \max(z_i, 0) - z_i y_i + \log(1 + e^{-|z_i|})}$$

- $$\max(z, 0)$$ 提出 "$$z$$ 大正时主导项" (本质是 ReLU on logits), 把 $$z$$ 大正时 $$z \cdot 1$$ 这一项显式吃掉.
- $$\log(1 + e^{-|z|})$$ 永远在 $$[0, \log 2] = [0, 0.693]$$, 既不上溢也不下溢.
- 等价写法: `np.logaddexp(0, z) - z * y`. 这是 PyTorch `F.binary_cross_entropy_with_logits` / TF `sigmoid_cross_entropy_with_logits` 的实现核心.

**Softmax 同源 trick**: 减 $$\max_j z_j$$ 再 exp, 把指数 argument 拉回 $$\leq 0$$. 所有"在 logits 空间算"的 loss (BCE-with-logits / cross-entropy-from-logits) 共享同一思想.

### 4. Stable BCE loss

照抄推出来的公式, mean over batch.

```python
@staticmethod
def _stable_bce_loss(z, y):
    # z: (n,) logits, y: (n,) in {0, 1}
    pos_part = np.maximum(z, 0.0)                     # (n,)  ReLU on logits
    log_part = np.log1p(np.exp(-np.abs(z)))           # (n,)  in [0, log 2], no overflow
    per_sample = pos_part - z * y + log_part          # (n,)
    return float(per_sample.mean())                   # scalar
```

### 5. fit -- full-batch GD with optional L2

梯度 $$\nabla_w L = \frac{1}{n} X^T (\sigma(Xw) - y)$$ 与 Linear Regression 同构 (GLM 框架: $$X^T$$ 乘"预测残差"). L2 在梯度上加 $$2\lambda w_{\text{reg}}$$, $$w_{\text{reg}}[0] = 0$$ 排除 bias. 收敛判据 $$|L_{t-1} - L_t| < \text{tol}$$ 等价于权重不再实质更新.

```python
def fit(self, X, y):
    # X: (n, d), y: (n,) in {0, 1}
    X_design = self._augment_with_bias(X) if self.fit_intercept else X
    n, d_aug = X_design.shape
    w = np.zeros(d_aug)                                    # (d_aug,)
    previous_loss = float("inf")
    self.training_loss_history = []

    for _ in range(self.max_iterations):                   # Criterion 1: max iter
        z = X_design @ w                                   # (n,)
        p = self._sigmoid(z)                               # (n,)
        error = p - y                                      # (n,)  prediction residual
        gradient = (X_design.T @ error) / n                # (d_aug,)
        if self.l2_lambda > 0.0:
            w_reg = w.copy()                               # (d_aug,)
            if self.fit_intercept:
                w_reg[0] = 0.0                              # don't penalize bias
            gradient = gradient + 2.0 * self.l2_lambda * w_reg
        w = w - self.learning_rate * gradient              # (d_aug,)

        current_loss = self._stable_bce_loss(z, y)
        self.training_loss_history.append(current_loss)
        # Criterion 2: loss change below tol
        if abs(previous_loss - current_loss) < self.convergence_threshold:
            break
        previous_loss = current_loss

    if self.fit_intercept:
        self.coef_, self.intercept_ = w[1:], float(w[0])
    else:
        self.coef_, self.intercept_ = w, 0.0
    return self
```

### 6. predict / predict_proba

`predict_proba` 给概率, `predict` 用阈值 (默认 0.5) 切硬标签. **调阈值**是应对 class imbalance 的第一招 (不动模型即可).

```python
def predict_proba(self, X):
    # X: (m, d)
    z = X @ self.coef_ + self.intercept_              # (m,)
    return self._sigmoid(z)                            # (m,)

def predict(self, X, threshold: float = 0.5):
    return (self.predict_proba(X) >= threshold).astype(int)   # (m,)
```

---

## 面试追问 (Cheat Sheet)

> **Q: 为什么 LR 没有闭式解?**

- Sigmoid 让对数似然变成关于 $$w$$ 的非二次函数, 一阶条件 $$X^T(\sigma(Xw) - y) = 0$$ 不能 algebraic 解出 $$w$$.
- LR 仍是凸 (Hessian PSD), GD / Newton / L-BFGS 都全局收敛 -- 没闭式不代表难解.
- 对比: Linear Regression 损失二次, 一阶条件线性, 所以有 $$\hat w = (X^TX)^{-1} X^Ty$$.

> **Q: Softmax 多分类怎么扩展?**

- $$p_k = e^{z_k} / \sum_j e^{z_j}$$, 损失 $$L = -\frac{1}{n}\sum_i \sum_k y_{ik} \log p_{ik}$$ ($$Y$$ one-hot).
- 梯度 $$\nabla_W L = \frac{1}{n} X^T (P - Y)$$ -- 与二分类**完全同构**, $$W$$ 升到 $$(d, K)$$.
- Stable softmax: 减 $$\max_j z_j$$ 再 exp (与 stable BCE 的 $$|z|$$ 同源).

> **Q: Newton / IRLS 与 GD 的关系?**

- Newton: $$w \leftarrow w - H^{-1} \nabla L$$, $$H = \frac{1}{n} X^T \mathrm{diag}(p(1-p)) X$$, 二阶收敛 (误差平方下降).
- IRLS = Newton 在 LR 上的具体形式, 每步解加权 least squares $$X^T W X \cdot \Delta w = X^T (y - p)$$.
- 代价 $$O(nd^2 + d^3)$$; $$d \geq 10^4$$ 时退到 GD; **L-BFGS** 是常见折中 (sklearn 默认 solver).

> **Q: 类别不平衡怎么办?**

- **调阈值** (训练不变, predict 时把 0.5 降到 ROC 上 recall/precision 平衡处) -- 单这一步解决大多数实际问题.
- **class weight / pos_weight**: BCE 给正样本乘 $$\beta$$ = neg/pos 比例.
- **Focal loss** $$-(1-p_t)^\gamma \log p_t$$ 对易分样本降权, $$\gamma=2$$ (RetinaNet 标配).

> **Q: L1 vs L2 正则的几何含义?**

- **L2 (Ridge)**: $$+\lambda \|w\|_2^2$$, 梯度 $$+2\lambda w$$; Gaussian prior $$\Rightarrow$$ 各 $$w_j$$ shrinkage 但**不为 0**.
- **L1 (Lasso)**: $$+\lambda \|w\|_1$$, 次梯度 $$\lambda \mathrm{sign}(w)$$; Laplace prior $$\Rightarrow$$ **稀疏解** (一些 $$w_j$$ 严格为 0, 自带特征选择).
- 几何: L2 等高线是圆 (各方向 shrink), L1 是菱形 (顶点在轴上 $$\Rightarrow$$ 解落在轴上 = 稀疏).

> **Q: Calibration -- 输出 $$p$$ 是真概率吗?**

- LR 在 BCE 训练下**理论上 calibrated**, 但 class imbalance / 强正则可能偏离.
- 检查: **reliability diagram** (predict_proba 分箱, 看实际频率 vs 预测均值, 完美应贴对角线).
- **Platt scaling**: 验证集再训一个 1D LR $$P_{\text{cal}} = \sigma(a z + b)$$. **Isotonic** 更灵活但需 >1000 验证样本.

> **Q: SGD vs full-batch GD?**

- Full-batch: 梯度无偏方差 0, 但 $$n$$ 大单步装不下.
- SGD / mini-batch (32-256): 方差大但 GPU SIMD 友好, 噪声有助跳出鞍点 (LR 凸不重要, NN 关键).
- LR 凸, 三者最终都收敛同一全局最优, 只差路径.

> **Q: 学习率上界与标准化?**

- 收敛要求 $$\eta < 2 / \lambda_{\max}(X^T \mathrm{diag}(p(1-p)) X / n)$$.
- 实战: 先 zero-mean unit-variance standardize, $$\lambda_{\max}$$ 落在 $$O(1)$$, $$\eta = 0.1$$ 即稳, 不收敛再砍半.

---

## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 200, 4
X = np.random.randn(N, D)
y = (X @ np.random.randn(D) > 0).astype(int)
lr = LogisticRegression().fit(X, y)
preds = lr.predict(X)
probs = lr.predict_proba(X)
assert preds.shape == (N,)
assert probs.shape == (N,)
print(f"Train accuracy = {(preds == y).mean():.3f}")
```
