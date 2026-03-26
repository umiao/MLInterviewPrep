# Regularization

## Overview

Regularization is a family of techniques that constrain model complexity to prevent overfitting -- the phenomenon where a model memorizes training noise instead of learning generalizable patterns. Understanding L1 vs L2 regularization, their gradient behavior, and when to apply each is a staple of MLE interviews. This topic bridges optimization theory and practical model tuning.

## Core Concepts

### Overfitting: Causes and Solutions

Overfitting occurs when the model fits the training distribution too closely, capturing noise as if it were signal.

**Six primary causes:**
1. **Insufficient training data** -- not enough examples to learn the true distribution
2. **Distribution mismatch** -- training data violates the i.i.d. assumption relative to test/production data
3. **Noisy training data** -- label errors or irrelevant features
4. **Excessive training iterations** -- the model keeps memorizing after learning the signal
5. **Poor feature engineering** -- features lack generalization ability
6. **Information leakage** -- overly complex model treats training as a lookup table

**Solution toolkit:**
- Feature selection (manual, model-based via PCA/SVD, or random as in Random Forest)
- Regularization (L1, L2, Elastic Net)
- Dropout (randomly zeroing activations during training)
- Early stopping (halt training when validation loss increases)
- Ensemble methods (Random Forest, bagging to reduce variance)
- Controlling model complexity (tree depth, number of parameters)

### L1 Regularization (LASSO)

Adds the sum of absolute parameter values to the loss function:

$$
J_{\text{L1}}(\theta) = J(\theta) + \lambda \sum_{j=1}^{p} |\theta_j|
$$

**Gradient behavior:**

$$
\frac{\partial L_1(\theta_j)}{\partial \theta_j} = \text{sgn}(\theta_j) = \begin{cases} +1 & \theta_j > 0 \\ -1 & \theta_j < 0 \end{cases}
$$

The gradient magnitude is **constant** (always 1 or -1, independent of $\theta_j$). This means every parameter moves toward zero at a fixed rate per step, regardless of its current value. Small parameters reach exactly zero and are eliminated.

**Key properties:**
- Produces **sparse** models (some weights become exactly zero)
- Acts as automatic **feature selection**
- May have **multiple optimal solutions** (non-differentiable at $\theta_j = 0$)
- LASSO = Least Absolute Shrinkage and Selection Operator

### L2 Regularization (Ridge)

Adds the sum of squared parameter values to the loss function:

$$
J_{\text{L2}}(\theta) = J(\theta) + \lambda \sum_{j=1}^{p} \theta_j^2
$$

**Gradient behavior:**

$$
\frac{\partial L_2(\theta_j)}{\partial \theta_j} = 2\theta_j
$$

The gradient is **proportional to the parameter value**. As $\theta_j$ approaches zero, the gradient vanishes -- the parameter shrinks but never reaches exactly zero.

**Key properties:**
- Shrinks all weights toward zero but **never zeros them out**
- Produces **dense** models (all features retained with small weights)
- **Unique optimum** guaranteed (strictly convex penalty)
- Computationally simpler (differentiable everywhere)

### Elastic Net

Combines L1 and L2 penalties:

$$
J_{\text{EN}}(\theta) = J(\theta) + \lambda_1 \sum |\theta_j| + \lambda_2 \sum \theta_j^2
$$

Useful when features are correlated -- L1 alone arbitrarily selects one from a group of correlated features, while Elastic Net encourages grouping.

### Regularization Strength

The hyperparameter $\lambda$ (or equivalently $\frac{1}{C}$ in sklearn) controls the bias-variance tradeoff:

- **Large $\lambda$**: strong penalty, simpler model, higher bias, lower variance
- **Small $\lambda$**: weak penalty, complex model, lower bias, higher variance
- **$\lambda = 0$**: no regularization, equivalent to ordinary least squares

### Dimensionality Reduction as Regularization

**PCA (Principal Component Analysis):** Finds the eigenvectors of the covariance matrix, keeps the top-$k$ eigenvectors corresponding to the largest eigenvalues. Reduces feature space while retaining maximum variance. Can also be computed via SVD.

**Trade-off:** PCA reduces overfitting by lowering dimensionality but sacrifices interpretability -- the principal components are linear combinations of original features.

### Dropout and Early Stopping

**Dropout:** Randomly zeroes a fraction of neuron activations during each training step. At test time, all neurons are active but scaled. Prevents co-adaptation of features. Equivalent to training an ensemble of thinned networks.

**Early stopping:** Monitor validation loss during training; stop when it begins to increase. Implicitly regularizes by limiting the effective number of optimization steps.

## Implementation

```python
from sklearn.linear_model import Lasso, Ridge, ElasticNet
from sklearn.model_selection import cross_val_score
import numpy as np

# L1 (LASSO) -- feature selection via sparsity
lasso = Lasso(alpha=0.1)  # alpha = lambda
lasso.fit(X_train, y_train)
selected = np.where(lasso.coef_ != 0)[0]  # non-zero features

# L2 (Ridge) -- shrinkage without elimination
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)

# Elastic Net -- combined L1 + L2
enet = ElasticNet(alpha=0.1, l1_ratio=0.5)  # l1_ratio: mix
enet.fit(X_train, y_train)

# Tune lambda via cross-validation
from sklearn.linear_model import LassoCV
lasso_cv = LassoCV(cv=5, alphas=np.logspace(-4, 1, 50))
lasso_cv.fit(X_train, y_train)
best_alpha = lasso_cv.alpha_
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| L1 for feature selection | High-dimensional data, many irrelevant features | Constant gradient drives weights to exact zero |
| L2 for multicollinearity | Correlated features, need stable coefficients | Distributes weight across correlated features |
| Elastic Net | Correlated features + want sparsity | Groups correlated features, then selects groups |
| Early stopping | Neural networks, iterative models | Cheapest regularization -- no hyperparameter to tune beyond patience |
| Dropout | Deep networks prone to co-adaptation | Equivalent to ensemble of $2^n$ thinned networks |

### Common Interview Questions

- [ ] What is overfitting and how do you prevent it?
- [ ] L1 vs L2: when would you use which?
- [ ] Why does L1 produce sparse solutions? (gradient argument)
- [ ] How does regularization strength affect bias-variance?
- [ ] What happens if you apply too much regularization?
- [ ] How does dropout work? Why is it effective?
- [ ] What is the geometric interpretation of L1 vs L2? (diamond vs circle constraint region)

## Comparisons

| Aspect | L1 (LASSO) | L2 (Ridge) | Elastic Net |
|--------|-----------|-----------|-------------|
| Penalty | $\sum |\theta_j|$ | $\sum \theta_j^2$ | $\lambda_1 \sum |\theta_j| + \lambda_2 \sum \theta_j^2$ |
| Gradient at $\theta_j$ | $\pm 1$ (constant) | $2\theta_j$ (proportional) | Both |
| Sparsity | Yes (exact zeros) | No (shrinks, never zeros) | Partial |
| Feature selection | Built-in | No | Built-in |
| Uniqueness | May have multiple optima | Unique optimum | Unique (if $\lambda_2 > 0$) |
| Correlated features | Arbitrarily picks one | Shares weight | Groups then selects |
| Sklearn class | `Lasso(alpha=)` | `Ridge(alpha=)` | `ElasticNet(alpha=, l1_ratio=)` |

## Key Takeaways

- [ ] Overfitting has 6 distinct causes -- match the solution to the cause
- [ ] L1 gradient is constant ($\pm 1$), which is why it drives weights to exactly zero (sparsity)
- [ ] L2 gradient is proportional ($2\theta_j$), which is why weights shrink toward but never reach zero
- [ ] $\lambda$ controls the bias-variance tradeoff: higher = simpler model = more bias
- [ ] Use L1 when you suspect many irrelevant features; use L2 when features are correlated
- [ ] Elastic Net combines both: useful for correlated features where you still want sparsity
- [ ] Dropout is conceptually an ensemble method; early stopping is the cheapest regularizer
- [ ] PCA/SVD reduce dimensionality (a form of regularization) at the cost of interpretability
