# Linear Regression (Closed-form lstsq + Full-Batch GD)

> **TL;DR** -- 一题两实现, closed-form 一发解出 vs GD 迭代逼近, 互验.
> **结论公式**: $$\hat\beta = (X^TX)^{-1}X^Ty$$, 但**永不显式求逆** -- 用 `np.linalg.lstsq` (SVD).
> **数值核心**: $$\kappa(X^TX) = \kappa(X)^2$$, 显式 inv 把误差放大一个量级.
> **GD 收敛要求**: $$\eta < 2/\lambda_{\max}(X^TX/n)$$, 必须先 standardize features.
> **复杂度**: closed-form $$O(nd^2 + d^3)$$, GD $$O(T \cdot nd)$$. $$d$$ 大时 GD 胜.

---

## 实现

### 0. Class skeleton

```python
import numpy as np
from typing import Literal, Optional

class LinearRegression:
    def __init__(self, method: Literal["closed_form", "gd"] = "closed_form",
                 fit_intercept: bool = True,
                 learning_rate: float = 1e-2,
                 max_iterations: int = 1000,
                 convergence_threshold: float = 1e-6):
        self.method = method
        self.fit_intercept = fit_intercept
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.coef_: Optional[np.ndarray] = None          # (d,)
        self.intercept_: float = 0.0                      # scalar
        self.training_loss_history: list[float] = []      # GD trace
```

### 1. Bias augmentation

把 intercept 折叠成 $$w_0$$, design matrix 多一列 1; closed-form 与 GD 共用矩阵代数. 加正则时 bias 通常不该被惩罚 -- 在 $$\lambda I$$ 的 $$(0,0)$$ 位置置 0.

```python
@staticmethod
def _augment_with_bias(X):
    # X: (n, d)
    n = X.shape[0]
    ones = np.ones((n, 1))                       # (n, 1)
    return np.hstack([ones, X])                   # (n, d+1)
```

### 2. Closed-form fit -- via `lstsq`, NOT `inv`

`lstsq` 内部走 SVD, 直接对 $$X$$ 分解, 不构造 $$X^TX$$, 误差只受 $$\kappa(X)$$ 影响. 教科书的 `inv(X.T @ X) @ X.T @ y` 把 condition number 平方, 工业代码永不写.

```python
def _fit_closed_form(self, X_design, y):
    # X_design: (n, d+1), y: (n,)
    w_full, *_ = np.linalg.lstsq(X_design, y, rcond=None)  # (d+1,)
    return w_full
```

### 3. GD fit -- full-batch

梯度 $$\nabla L = \frac{2}{n} X^T(Xw - y)$$. 收敛判据 $$|L_{t-1} - L_t| < \text{tol}$$ 等价于权重几乎不再变.

```python
def _fit_gd(self, X_design, y):
    # X_design: (n, d+1), y: (n,)
    n, d_aug = X_design.shape
    w = np.zeros(d_aug)                                   # (d+1,)
    previous_loss = float("inf")
    self.training_loss_history = []

    for _ in range(self.max_iterations):                  # Criterion 1: max iter
        pred = X_design @ w                               # (n,)
        residual = pred - y                               # (n,)
        gradient = (2.0 / n) * (X_design.T @ residual)    # (d+1,)
        w = w - self.learning_rate * gradient             # (d+1,)

        current_loss = float(np.mean(residual ** 2))
        self.training_loss_history.append(current_loss)

        # Criterion 2: loss change below tol
        if abs(previous_loss - current_loss) < self.convergence_threshold:
            break
        previous_loss = current_loss
    return w
```

### 4. fit / predict

```python
def fit(self, X, y):
    X_design = self._augment_with_bias(X) if self.fit_intercept else X
    if self.method == "closed_form":
        w_full = self._fit_closed_form(X_design, y)
    elif self.method == "gd":
        w_full = self._fit_gd(X_design, y)
    else:
        raise ValueError(f"Unknown method: {self.method}")

    if self.fit_intercept:
        self.coef_, self.intercept_ = w_full[1:], float(w_full[0])
    else:
        self.coef_, self.intercept_ = w_full, 0.0
    return self

def predict(self, X):
    return X @ self.coef_ + self.intercept_
```

---

## Closed-form vs Full-Batch GD

|              | Closed-form (`lstsq`)        | Full-Batch GD                     |
| ------------ | ---------------------------- | --------------------------------- |
| 选择方式     | SVD 一次出解                  | 梯度迭代 $$T$$ 步                 |
| 失败模式     | $$d^3$$ 爆炸                 | $$\eta$$ 大则发散                 |
| 实践默认值   | $$d \le 10^3$$               | $$d \ge 10^4$$                    |
| 数值稳定性   | SVD 直接分解 $$X$$, 最稳      | 依赖 standardize + 调参           |
| 复杂度       | $$O(nd^2 + d^3)$$            | $$O(T \cdot nd)$$                 |

**一句话**: closed-form 是 reference solution (单次 SVD), GD 是 $$d$$ 太大时的 fallback; 两者在凸目标下应数值收敛到同一 $$w$$, GD 不一致 = learning rate / iterations 配错.

---

## 面试追问 (Cheat Sheet)

> **Q: 为什么不用 `np.linalg.inv`?**

- $$\kappa(X^TX) = \kappa(X)^2$$ -- 显式求逆把浮点误差放大一个量级.
- `lstsq` 走 SVD, 直接分解 $$X$$, 不构造 $$X^TX$$, 数值最稳.
- `solve(X.T @ X, X.T @ y)` 走 LU, 不显式求逆但仍构造 $$X^TX$$, 中等稳.

> **Q: Ridge 怎么改?**

- 正规方程改成 $$(X^TX + \lambda I)\, w = X^Ty$$, 用 `solve` 解 (仍不显式求逆).
- $$\lambda I$$ 把所有特征值抬高 $$\lambda$$, 矩阵**永远可逆** -- 即使 $$d > n$$ 或 $$X$$ 共线.
- 实现: `reg = lam * np.eye(d_aug); reg[0, 0] = 0` (不惩罚 intercept).

> **Q: Lasso 为什么没 closed-form?**

- L1 项 $$\|w\|_1$$ 在 $$w_j = 0$$ 不可导 -- 整体 $$L$$ 没解析极值.
- **逐元素**有闭式 (coordinate descent): soft-thresholding $$w_j \leftarrow \text{sign}(z_j) \cdot \max(|z_j| - \lambda, 0)$$.
- 这是 ISTA / coordinate descent 的更新规则.

> **Q: 共线性怎么办?**

- $$X$$ 列线性相关 $$\Rightarrow X^TX$$ 奇异 $$\Rightarrow \kappa \to \infty$$.
- 优先级: Ridge (一行 $$\lambda I$$) > `pinv` (Moore-Penrose) > 删冗余列 (VIF) > PCA 降维.

> **Q: $$d \gg n$$ (文本 / 基因组) 怎么办?**

- $$X^TX$$ 必奇异, $$w$$ 不唯一 $$\Rightarrow$$ 必须正则化.
- Lasso 工业首选: 顺带做特征选择, 稀疏 $$w$$.

> **Q: SGD 与 full-batch GD 的差别?**

- full-batch: 梯度无偏, 方差小, 内存吃紧.
- SGD / mini-batch (32~256): 方差大但能跳出鞍点, GPU SIMD 友好.
- LR 是凸问题, 三者最终都收敛到同一全局最优, 只差路径.

> **Q: GD learning rate 上界?**

- $$\eta < 2 / \lambda_{\max}(X^TX / n)$$ 才收敛, 否则发散.
- 实战: 先 zero-mean unit-variance standardize, $$\lambda_{\max}$$ 落在 $$O(1)$$, $$\eta = 10^{-2}$$ 即稳.

---

## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 200, 5
X = np.random.randn(N, D)
true_w = np.random.randn(D)
y = X @ true_w + 0.01 * np.random.randn(N)
lr = LinearRegression().fit(X, y)
preds = lr.predict(X)
assert preds.shape == (N,)
print(f"MSE = {np.mean((preds - y) ** 2):.4f}")
```
