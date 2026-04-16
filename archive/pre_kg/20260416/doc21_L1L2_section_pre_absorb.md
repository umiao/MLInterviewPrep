<!--
Archived pre-consolidation snapshot of the L1/L2 Regularization section
from company_documents.id=21 ("[合集] 概率统计 + 数学推导"), lines 1078-1183
at commit 7330441 (2026-04-16, pre-KG-P2-02). Material was absorbed into
framework_node 195 as part of the Regularization canonical_hub consolidation.
The 合集 doc 21 itself was NOT deleted per user policy (per-concept review only);
only this subsection was the unique source prior to consolidation.
-->

## 9. L1/L2 Regularization与Bias

### 题目描述

为什么L1/L2 regularization不是unbiased estimator？

### 最佳解答

**核心结论: L1/L2 regularization引入bias，但降低variance，是经典的bias-variance tradeoff。**

**无正则化的OLS (Ordinary Least Squares，最小二乘法)**:

$$\hat{\beta}_{\text{OLS}} = (X^TX)^{-1}X^Ty$$

OLS是unbiased: $E[\hat{\beta}_{\text{OLS}}] = \beta_{\text{true}}$

**L2 Regularization (Ridge)**:

$$\hat{\beta}_{\text{Ridge}} = (X^TX + \lambda I)^{-1}X^Ty$$

$$E[\hat{\beta}_{\text{Ridge}}] = (X^TX + \lambda I)^{-1}X^TX \cdot \beta_{\text{true}} \neq \beta_{\text{true}}$$

Ridge estimator **系统性地将系数向零收缩（shrink toward zero）**，所以是biased的。

**L1 Regularization (Lasso)**:

$$\hat{\beta}_{\text{Lasso}} = \arg\min_\beta \|y - X\beta\|_2^2 + \lambda\|\beta\|_1$$

Lasso不仅shrink，还进行feature selection（将某些系数精确压到0）。也是biased的。

**为什么要引入bias？**

$$\text{MSE} = \text{Bias}^2 + \text{Variance}$$

- OLS: 无bias，但可能有很高的variance（特别是feature多、数据少时）
- Ridge/Lasso: 引入少量bias，大幅降低variance
- 总MSE可能降低 -- 这是正则化的价值所在

**James-Stein现象**: 当维度 $p \geq 3$ 时，biased shrinkage estimator的MSE严格小于OLS。

### Python代码

```python
import numpy as np
from typing import Tuple

def ridge_regression(
    X: np.ndarray, y: np.ndarray, lam: float
) -> np.ndarray:
    """Ridge regression closed-form solution."""
    n_features = X.shape[1]
    return np.linalg.solve(
        X.T @ X + lam * np.eye(n_features), X.T @ y
    )


def demo_ridge_bias() -> None:
    """Demonstrate bias-variance tradeoff with Ridge."""
    rng = np.random.default_rng(42)
    n, p = 50, 10
    beta_true = rng.standard_normal(p)
    X = rng.standard_normal((n, p))
    y = X @ beta_true + rng.normal(0, 0.5, n)

    print(f"True beta norm: {np.linalg.norm(beta_true):.3f}")
    for lam in [0, 0.1, 1.0, 10.0, 100.0]:
        beta_hat = ridge_regression(X, y, lam)
        bias = np.linalg.norm(beta_hat - beta_true)
        print(f"lambda={lam:6.1f}: ||beta_hat||={np.linalg.norm(beta_hat):.3f}, "
              f"bias(||beta_hat - beta_true||)={bias:.3f}")


def lasso_coordinate_descent(
    X: np.ndarray, y: np.ndarray, lam: float,
    max_iter: int = 1000, tol: float = 1e-6,
) -> np.ndarray:
    """Simple coordinate descent for Lasso."""
    n, p = X.shape
    beta = np.zeros(p)
    for _ in range(max_iter):
        beta_old = beta.copy()
        for j in range(p):
            residual = y - X @ beta + X[:, j] * beta[j]
            rho = X[:, j] @ residual / n
            beta[j] = np.sign(rho) * max(abs(rho) - lam / n, 0)
        if np.max(np.abs(beta - beta_old)) < tol:
            break
    return beta


demo_ridge_bias()
```

### 常见Follow-up

1. **Elastic Net是什么？** 结合L1和L2: $\lambda_1\|\beta\|_1 + \lambda_2\|\beta\|_2^2$。当特征之间有相关性时，Lasso只保留一个，Elastic Net保留一组。
2. **为什么L1产生sparsity但L2不会？** 几何解释：L1的约束区域（菱形）有尖角，等高线更容易在坐标轴上与之相切，使系数恰好为0。
3. **Bayesian解释？** L2 = Gaussian prior on weights; L1 = Laplace prior on weights。Laplace分布在0处的密度峰值更高，鼓励稀疏。

### 面试要点

- 核心: 正则化通过向零收缩引入bias，换取更低的variance
- 能写出Ridge的闭式解并推导bias
- 提及bias-variance tradeoff
- L1的额外特性: sparsity / feature selection
- James-Stein estimator是高级加分项
