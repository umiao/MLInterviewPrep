# Support Vector Machines (SVM)

## Overview

SVMs find the maximum-margin hyperplane separating classes by solving a convex optimization problem. While less common in production than tree ensembles, SVMs are an interview staple: they test understanding of constrained optimization, Lagrangian duality, kernel methods, and the bias-variance tradeoff. Key for small-data regimes, high-dimensional sparse data, and text classification.

## Core Concepts

### Maximum-Margin Hyperplane

A hyperplane is defined by normal vector $w$ and intercept $b$: $w^Tx + b = 0$. For linearly separable data, we seek the hyperplane that maximizes the geometric margin -- the distance between the closest points of each class.

The distance from point $x_i$ to the hyperplane is $\frac{|w^Tx_i + b|}{\|w\|}$. For support vectors on the margin boundary, we normalize so that $y_i(w^Tx_i + b) = 1$, giving margin width $\frac{2}{\|w\|}$.

**Primal optimization (hard margin):**

$$
\min_{w,b} \frac{1}{2}\|w\|^2 \quad \text{s.t.} \quad y_i(w^Tx_i + b) \geq 1, \; \forall i
$$

The $\frac{1}{2}$ factor simplifies the derivative. Maximizing $\frac{2}{\|w\|}$ is equivalent to minimizing $\frac{1}{2}\|w\|^2$.

### Support Vectors

Support vectors are the training points where $y_i(w^Tx_i + b) = 1$ (lying exactly on the margin boundary). Only these points have $\alpha_i > 0$ in the dual. Key properties:

- Removing any non-support-vector point does not change the decision boundary
- The number of support vectors determines prediction complexity
- Sparsity of support vectors = efficiency at inference time

### Lagrange Duality and KKT Conditions

To solve the constrained primal problem, construct the Lagrangian:

$$
L(w, b, \alpha) = \frac{1}{2}\|w\|^2 + \sum_{i=1}^{n} \alpha_i [1 - y_i(w^Tx_i + b)], \quad \alpha_i \geq 0
$$

**Why go dual?** Two advantages: (1) simpler constraints -- optimize only $\alpha$; (2) enables the kernel trick since data appears only as dot products.

Setting partial derivatives to zero:

$$
\frac{\partial L}{\partial w} = 0 \Rightarrow w = \sum_{i=1}^{n} \alpha_i y_i x_i
$$

$$
\frac{\partial L}{\partial b} = 0 \Rightarrow \sum_{i=1}^{n} \alpha_i y_i = 0
$$

Substituting back yields the **dual problem**:

$$
\max_{\alpha} \sum_{i=1}^{n} \alpha_i - \frac{1}{2}\sum_{i=1}^{n}\sum_{j=1}^{n} \alpha_i \alpha_j y_i y_j (x_i \cdot x_j) \quad \text{s.t.} \quad \alpha_i \geq 0, \; \sum_{i=1}^{n} \alpha_i y_i = 0
$$

**KKT complementary slackness condition:**

$$
\alpha_i [y_i(w^Tx_i + b) - 1] = 0, \quad \forall i
$$

This means either $\alpha_i = 0$ (point is not a support vector) or $y_i(w^Tx_i + b) = 1$ (point is on the margin). Strong duality holds because the primal is a convex QP.

### SMO Algorithm

Sequential Minimal Optimization solves the dual by updating two $\alpha$ parameters at a time. Why two? The constraint $\sum \alpha_i y_i = 0$ means changing a single $\alpha_i$ would violate the constraint. With two parameters $\alpha_i, \alpha_j$:

$$
\alpha_i y_i + \alpha_j y_j = c, \quad c = -\sum_{k \neq i,j} \alpha_k y_k
$$

Substitute to eliminate $\alpha_j$, solve the univariate quadratic for $\alpha_i$, clip to box constraints $[0, C]$, then recover $\alpha_j$. Iterate until convergence.

### Soft Margin (C Parameter)

When data is not perfectly linearly separable, introduce slack variables $\xi_i \geq 0$:

$$
\min_{w,b,\xi} \frac{1}{2}\|w\|^2 + C\sum_{i=1}^{n} \xi_i \quad \text{s.t.} \quad y_i(w^Tx_i + b) \geq 1 - \xi_i, \; \xi_i \geq 0
$$

$C$ controls the bias-variance tradeoff:

| $C$ value | Behavior | Margin | Misclassifications |
|-----------|----------|--------|--------------------|
| $C \to \infty$ | Hard margin (strict) | Narrow | Zero (if separable) |
| Large $C$ | Low bias, high variance | Narrow | Few allowed |
| Small $C$ | High bias, low variance | Wide | More tolerated |

Note: $C = \frac{1}{\lambda}$ where $\lambda$ is the regularization coefficient. The soft-margin SVM is equivalent to minimizing hinge loss with L2 regularization: $\sum_i \max(0, 1 - y_i f(x_i)) + \lambda\|w\|^2$.

### Kernel Trick

The kernel function computes dot products in a high-dimensional feature space without explicit mapping:

$$
K(x_i, x_j) = \phi(x_i)^T \phi(x_j)
$$

This works because the dual form and prediction function only involve dot products $x_i \cdot x_j$, which we replace with $K(x_i, x_j)$.

**Prerequisite (Mercer's theorem):** $K$ must be a positive semi-definite function (the Gram matrix $K_{ij} = K(x_i, x_j)$ must be PSD).

| Kernel | Formula | Parameters | Best for |
|--------|---------|------------|----------|
| Linear | $K(x,z) = x^Tz$ | None | High-dim sparse data (text, genomics) |
| Polynomial | $K(x,z) = (x^Tz + c)^d$ | Degree $d$, offset $c$ | Explicit feature interactions |
| RBF (Gaussian) | $K(x,z) = \exp\left(-\frac{\|x-z\|^2}{2\sigma^2}\right)$ | $\gamma = \frac{1}{2\sigma^2}$ | General nonlinear; default choice |
| Sigmoid | $K(x,z) = \tanh(\kappa \, x^Tz + c)$ | $\kappa > 0, c < 0$ | Neural network analogy (rarely used) |

**RBF kernel intuition:** Maps to infinite-dimensional space. Small $\gamma$ = wide Gaussian = smooth boundary; large $\gamma$ = tight Gaussian = complex boundary (overfitting risk).

### Recovering the Decision Boundary

After solving for $\alpha$:

1. **Weight vector:** $w = \sum_{i=1}^{n} \alpha_i y_i x_i$ (only support vectors contribute)
2. **Bias:** Pick any support vector $x_s$ with $0 < \alpha_s < C$: $b = y_s - w^Tx_s$. For numerical stability, average over all such support vectors: $b = \frac{1}{|S|}\sum_{s \in S}(y_s - w^Tx_s)$
3. **Classify:** $f(x) = \text{sign}(w^Tx + b) = \text{sign}\left(\sum_{i \in SV} \alpha_i y_i K(x_i, x) + b\right)$

## Implementation

```python
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

# Always scale features -- SVMs are distance-based
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel="rbf", C=1.0, gamma="scale", probability=True))
])

# Hyperparameter search on log scale
param_grid = {
    "svm__C": [0.01, 0.1, 1, 10, 100],
    "svm__gamma": [0.001, 0.01, 0.1, 1, "scale"],
    "svm__kernel": ["rbf", "linear"]
}
grid = GridSearchCV(pipe, param_grid, cv=5, scoring="f1")
grid.fit(X_train, y_train)

# Inspect support vectors
best_svm = grid.best_estimator_.named_steps["svm"]
print(f"Support vectors: {best_svm.n_support_}")  # per class
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Kernel selection | Nonlinear boundaries needed | RBF is default; linear for high-dim sparse (text). Try linear first -- if underfitting, move to RBF |
| $C$ and $\gamma$ tuning | Overfitting or underfitting | Grid search on log scale: $C \in [10^{-2}, 10^{3}]$, $\gamma \in [10^{-3}, 10^{1}]$ |
| SVM vs logistic regression | "Which classifier?" | SVM maximizes margin (focuses on hard examples); LR models calibrated probabilities |
| Hinge loss connection | Loss function questions | SVM loss = $\max(0, 1 - y \cdot f(x))$; compare: LR uses log-loss, perceptron uses $\max(0, -y \cdot f(x))$ |
| Kernel trick explanation | "Explain intuitively" | Data appears only as dot products in dual; replace dot product with kernel to implicitly work in high-dim space |
| Scalability concerns | Large dataset scenarios | $O(n^2)$ to $O(n^3)$ training; not suitable for millions of samples. Use SGD with hinge loss instead |

### Common Interview Questions

- [ ] Explain the kernel trick intuitively -- why can we avoid computing in high-dimensional space?
- [ ] What are support vectors and why do only they determine the decision boundary?
- [ ] How does the C parameter control the bias-variance tradeoff?
- [ ] When would you use SVM vs logistic regression?
- [ ] RBF vs linear kernel: when to use which?
- [ ] Why does SMO update two parameters at a time instead of one?
- [ ] Can SVM do multi-class classification? How? (OvR or OvO)

## Comparisons

### SVM vs Other Linear Classifiers

| Aspect | SVM (Linear) | SVM (RBF) | Logistic Regression | Perceptron |
|--------|-------------|-----------|-------------------|------------|
| Decision boundary | Linear | Nonlinear | Linear | Linear |
| Loss function | Hinge | Hinge | Log-loss | Zero-one (step) |
| Probabilistic output | Via Platt scaling | Via Platt scaling | Native | No |
| Scalability | Good: $O(nd)$ | Poor: $O(n^2 d)$ | Good: $O(nd)$ | Good: $O(nd)$ |
| Sparse data (text) | Excellent | Fair | Good | Fair |
| Interpretability | Moderate (weights) | Low | High (log-odds) | Low |

### Kernel Selection Guide

| Scenario | Recommended Kernel | Reason |
|----------|--------------------|--------|
| $n_{features} >> n_{samples}$ (text, genomics) | Linear | Already high-dim; RBF overfits |
| $n_{samples} >> n_{features}$ | RBF | Need nonlinear capacity |
| Known polynomial interactions | Polynomial | Explicit degree control |
| Small dataset, unknown structure | RBF (with CV) | Most flexible default |
| Need fast training at scale | Linear (or skip SVM) | $O(nd)$ vs $O(n^2d)$ |

## Key Takeaways

- [ ] SVMs maximize the geometric margin -- understand both the primal ($\min \frac{1}{2}\|w\|^2$) and dual (maximize $\sum \alpha_i - \frac{1}{2}\sum \alpha_i \alpha_j y_i y_j K(x_i, x_j)$) formulations
- [ ] Kernel trick: $K(x,z) = \phi(x)^T\phi(z)$ avoids explicit high-dim mapping; works because dual only uses dot products
- [ ] KKT complementary slackness: $\alpha_i > 0$ only for support vectors (on or inside margin)
- [ ] SMO updates 2 parameters at a time to maintain $\sum \alpha_i y_i = 0$ constraint
- [ ] $C$ is inverse regularization: large $C$ = strict (narrow margin), small $C$ = tolerant (wide margin)
- [ ] Always scale features before training SVMs (distance-based method)
- [ ] Complexity is $O(n^2)$ to $O(n^3)$ -- use SGDClassifier(loss="hinge") for large-scale linear SVM
- [ ] Hinge loss $\max(0, 1 - yf(x))$ connects SVM to the broader loss function family
