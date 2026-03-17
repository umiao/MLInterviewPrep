"""Seed Pillar 2 (ML Fundamentals) framework node descriptions.

Usage:
    python scripts/seed_pillar2_content.py

Populates the `description` field for all 25 Pillar 2 leaf nodes
in the framework_nodes table. Idempotent -- overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, get_engine  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Content for each leaf topic, keyed by path
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {}

# ===== SUPERVISED LEARNING =====

CONTENT["pillar2.supervised_learning.linear_models"] = r"""# Linear Models

## Overview
Linear models are the foundation of supervised learning. They predict outputs as a linear combination of input features, offering interpretability and strong baselines. Every MLE should master them -- they appear in system design (serving latency), feature importance discussions, and as baselines.

## Core Concepts

### Linear Regression
Minimizes the sum of squared residuals:

$$
\hat{y} = X\beta, \quad \beta^* = \arg\min_\beta \|y - X\beta\|_2^2 = (X^TX)^{-1}X^Ty
$$

Closed-form solution exists when $X^TX$ is invertible. Complexity: $O(nd^2 + d^3)$ for $n$ samples and $d$ features.

**Key assumptions**: linearity, independence, homoscedasticity, normality of residuals.

### Logistic Regression
For binary classification, models $P(y=1|x)$ using the sigmoid function:

$$
P(y=1|x) = \sigma(w^Tx + b) = \frac{1}{1 + e^{-(w^Tx + b)}}
$$

Loss function (binary cross-entropy):

$$
\mathcal{L} = -\frac{1}{n}\sum_{i=1}^{n}[y_i \log \hat{y}_i + (1-y_i)\log(1-\hat{y}_i)]
$$

No closed-form solution -- optimized via gradient descent or Newton's method.

### Generalized Linear Models (GLMs)
Extend linear models through a link function $g$:

$$
g(E[y|x]) = w^Tx + b
$$

| Distribution | Link Function | Use Case |
|-------------|---------------|----------|
| Gaussian | Identity | Regression |
| Bernoulli | Logit | Binary classification |
| Poisson | Log | Count data |
| Gamma | Inverse | Positive continuous |

## Implementation

```python
import numpy as np

class LinearRegression:
    def fit(self, X, y):
        X_b = np.c_[np.ones(len(X)), X]  # add bias
        self.theta = np.linalg.pinv(X_b.T @ X_b) @ X_b.T @ y
        return self

    def predict(self, X):
        X_b = np.c_[np.ones(len(X)), X]
        return X_b @ self.theta

class LogisticRegression:
    def fit(self, X, y, lr=0.01, epochs=1000):
        self.w = np.zeros(X.shape[1])
        self.b = 0.0
        for _ in range(epochs):
            z = X @ self.w + self.b
            pred = 1 / (1 + np.exp(-z))
            grad_w = X.T @ (pred - y) / len(y)
            grad_b = np.mean(pred - y)
            self.w -= lr * grad_w
            self.b -= lr * grad_b
        return self
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Feature importance via coefficients | "How do you interpret the model?" | Standardize features first; coefficient magnitude = importance |
| Multicollinearity diagnosis | Features are correlated | VIF > 5 is a red flag; use regularization or PCA |
| Baseline model | Any ML system design | Start with logistic regression, then justify complexity |
| Online learning | Streaming data | SGD-based logistic regression updates incrementally |

### Common Interview Questions
- [ ] Why is logistic regression called "regression" if it does classification?
- [ ] When does the closed-form solution for linear regression fail?
- [ ] How do you handle multicollinearity?
- [ ] Compare logistic regression vs. naive Bayes for text classification.
- [ ] What happens when classes are perfectly separable in logistic regression?

## Comparisons

| Aspect | Linear Regression | Logistic Regression | Ridge | Lasso |
|--------|------------------|-------------------|-------|-------|
| Task | Regression | Classification | Regression | Regression |
| Loss | MSE | Cross-entropy | MSE + L2 | MSE + L1 |
| Solution | Closed-form | Iterative | Closed-form | Iterative |
| Feature selection | No | No | No | Yes (sparse) |

## Key Takeaways

- [ ] Linear regression: know the normal equation and when it breaks (singular $X^TX$, $n < d$)
- [ ] Logistic regression: understand the probabilistic interpretation and decision boundary
- [ ] Always standardize features before comparing coefficients
- [ ] Linear models are the go-to baseline in any ML system design interview
- [ ] GLMs extend the framework -- know Poisson regression for count data
"""

CONTENT["pillar2.supervised_learning.tree_models"] = r"""# Tree-Based Models

## Overview
Decision trees and their ensemble variants (Random Forest, Gradient Boosted Trees) dominate tabular data in industry. XGBoost/LightGBM are the workhorses at companies like LinkedIn, DoorDash, and Airbnb. Understanding the splitting criteria, ensemble methods, and hyperparameter tuning is essential.

## Core Concepts

### Decision Tree Splitting Criteria

**Gini Impurity** (used by CART):

$$
G(t) = 1 - \sum_{k=1}^{K} p_k^2
$$

**Entropy / Information Gain** (used by ID3/C4.5):

$$
H(t) = -\sum_{k=1}^{K} p_k \log_2 p_k, \quad IG = H(\text{parent}) - \sum_j \frac{n_j}{n} H(\text{child}_j)
$$

**Regression**: variance reduction (MSE split).

### Random Forest
Bagging + feature subsampling. Each tree trained on a bootstrap sample with $\sqrt{d}$ random features (classification) or $d/3$ (regression).

**Variance reduction**: for $B$ trees with pairwise correlation $\rho$ and individual variance $\sigma^2$:

$$
\text{Var}(\bar{f}) = \rho\sigma^2 + \frac{1-\rho}{B}\sigma^2
$$

Key insight: reducing $\rho$ (via feature subsampling) matters more than increasing $B$.

### Gradient Boosted Trees (GBT)
Sequential ensemble where each tree fits the negative gradient of the loss:

$$
f_m(x) = f_{m-1}(x) + \eta \cdot h_m(x), \quad h_m = \arg\min_h \sum_i L(y_i, f_{m-1}(x_i) + h(x_i))
$$

**XGBoost objective** (with regularization):

$$
\mathcal{L} = \sum_i L(y_i, \hat{y}_i) + \sum_t \left[\gamma T_t + \frac{1}{2}\lambda \|w_t\|^2\right]
$$

where $T_t$ = number of leaves in tree $t$, $w_t$ = leaf weights.

### LightGBM Optimizations
- **Gradient-based One-Side Sampling (GOSS)**: keep large-gradient instances, subsample small-gradient
- **Exclusive Feature Bundling (EFB)**: bundle mutually exclusive sparse features
- **Leaf-wise growth**: deeper trees with fewer leaves vs. level-wise

## Implementation

```python
# XGBoost typical setup for ranking/classification
import xgboost as xgb

params = {
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 5,
    "reg_lambda": 1.0,
    "reg_alpha": 0.1,
}
dtrain = xgb.DMatrix(X_train, label=y_train)
model = xgb.train(params, dtrain, num_boost_round=500,
                   evals=[(dval, "val")], early_stopping_rounds=50)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Feature importance | "Which features matter?" | Use SHAP values, not built-in importance (biased toward high-cardinality) |
| Handling categoricals | High-cardinality categoricals | LightGBM native categorical; XGBoost needs encoding |
| Missing value handling | Sparse/missing data | XGBoost learns optimal missing direction at each split |
| Monotonic constraints | Business logic constraints | `monotone_constraints` parameter in XGB/LGB |

### Common Interview Questions
- [ ] How does XGBoost handle missing values?
- [ ] Why is Random Forest less prone to overfitting than a single deep tree?
- [ ] Compare bagging vs. boosting: when would you prefer each?
- [ ] How do you tune GBT hyperparameters systematically?
- [ ] Explain the bias-variance tradeoff in tree ensembles.

## Comparisons

| Aspect | Decision Tree | Random Forest | XGBoost | LightGBM |
|--------|--------------|---------------|---------|----------|
| Bias | High | Medium | Low | Low |
| Variance | High | Low | Low | Low |
| Speed | Fast | Medium | Medium | Fast |
| Missing values | Some | No | Yes | Yes |
| Interpretability | High | Low | Low | Low |

## Key Takeaways

- [ ] Know Gini vs. entropy: Gini is default in sklearn, nearly identical in practice
- [ ] Random Forest: understand why $\sqrt{d}$ feature subsampling reduces correlation
- [ ] XGBoost: know the regularized objective and second-order Taylor approximation
- [ ] LightGBM: leaf-wise growth + GOSS + EFB make it faster for large datasets
- [ ] SHAP > built-in feature importance for reliable interpretation
"""

CONTENT["pillar2.supervised_learning.svm"] = r"""# Support Vector Machines (SVM)

## Overview
SVMs find the maximum-margin hyperplane separating classes. While less common in production than tree ensembles, SVMs are important for interviews: they test understanding of optimization, kernel methods, and the bias-variance tradeoff. Key for small-data regimes and text classification.

## Core Concepts

### Hard-Margin SVM
For linearly separable data, find the hyperplane $w^Tx + b = 0$ maximizing the margin $\frac{2}{\|w\|}$:

$$
\min_{w,b} \frac{1}{2}\|w\|^2 \quad \text{s.t.} \quad y_i(w^Tx_i + b) \geq 1 \;\forall i
$$

### Soft-Margin SVM
Allows misclassification via slack variables $\xi_i \geq 0$:

$$
\min_{w,b,\xi} \frac{1}{2}\|w\|^2 + C\sum_i \xi_i \quad \text{s.t.} \quad y_i(w^Tx_i + b) \geq 1 - \xi_i
$$

$C$ controls the bias-variance tradeoff: large $C$ = low bias, high variance.

### Dual Formulation and Kernels
The dual problem introduces Lagrange multipliers $\alpha_i$:

$$
\max_\alpha \sum_i \alpha_i - \frac{1}{2}\sum_{i,j} \alpha_i \alpha_j y_i y_j K(x_i, x_j) \quad \text{s.t.} \quad 0 \leq \alpha_i \leq C, \; \sum_i \alpha_i y_i = 0
$$

**Kernel trick**: compute dot products in high-dimensional space without explicit mapping.

| Kernel | Formula | Use Case |
|--------|---------|----------|
| Linear | $K(x,z) = x^Tz$ | High-dim sparse data (text) |
| RBF | $K(x,z) = \exp(-\gamma\|x-z\|^2)$ | General nonlinear |
| Polynomial | $K(x,z) = (x^Tz + c)^d$ | Feature interactions |

### Support Vectors
Only data points with $\alpha_i > 0$ (on or inside the margin) affect the decision boundary. Sparsity = efficiency at prediction time.

## Implementation

```python
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ("scaler", StandardScaler()),  # SVMs are scale-sensitive
    ("svm", SVC(kernel="rbf", C=1.0, gamma="scale", probability=True))
])
pipe.fit(X_train, y_train)
# Support vectors: pipe.named_steps["svm"].support_vectors_
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Kernel selection | Nonlinear boundaries | RBF is default; linear for high-dim sparse (text) |
| $C$ and $\gamma$ tuning | Overfitting/underfitting | Grid search on log scale: $C \in [10^{-2}, 10^{3}]$ |
| SVM vs. logistic regression | "Which classifier to use?" | SVM focuses on margin (hard examples); LR models probabilities |
| Hinge loss connection | Loss function questions | SVM loss = hinge: $\max(0, 1 - y \cdot f(x))$ |

### Common Interview Questions
- [ ] Explain the kernel trick and why it works.
- [ ] What are support vectors and why are they important?
- [ ] How does $C$ affect the decision boundary?
- [ ] When would you choose SVM over logistic regression?
- [ ] Can SVM do multi-class classification? How?

## Comparisons

| Aspect | SVM (Linear) | SVM (RBF) | Logistic Regression |
|--------|-------------|-----------|-------------------|
| Decision boundary | Linear | Nonlinear | Linear |
| Probabilistic | Via Platt scaling | Via Platt scaling | Native |
| Scalability | Good ($O(nd)$) | Poor ($O(n^2d)$) | Good |
| Sparse data | Excellent | Fair | Good |

## Key Takeaways

- [ ] SVMs maximize margin -- understand the geometric and optimization views
- [ ] Kernel trick: $K(x,z) = \phi(x)^T\phi(z)$ avoids explicit high-dim mapping
- [ ] Support vectors determine the boundary; other points are irrelevant
- [ ] Always scale features before training SVMs
- [ ] Hinge loss is the SVM loss; compare with logistic (log-loss) and perceptron (0-1)
"""

CONTENT["pillar2.supervised_learning.bias_variance_tradeoff"] = r"""# Bias-Variance Tradeoff

## Overview
The bias-variance tradeoff is a fundamental concept explaining model generalization. It decomposes prediction error into irreducible noise, bias (underfitting), and variance (overfitting). This framework guides every model selection and regularization decision.

## Core Concepts

### Decomposition
For a model $\hat{f}$ trained on dataset $D$, the expected prediction error at point $x$ is:

$$
E_D[(y - \hat{f}(x))^2] = \text{Bias}[\hat{f}(x)]^2 + \text{Var}_D[\hat{f}(x)] + \sigma^2
$$

where:
- **Bias** $= E_D[\hat{f}(x)] - f(x)$: systematic error from wrong assumptions
- **Variance** $= E_D[(\hat{f}(x) - E_D[\hat{f}(x)])^2]$: sensitivity to training data
- $\sigma^2$: irreducible noise (Bayes error)

### Model Complexity Spectrum

| Complexity | Bias | Variance | Example |
|-----------|------|----------|---------|
| Low | High | Low | Linear regression, Naive Bayes |
| Medium | Medium | Medium | Small neural net, shallow tree ensemble |
| High | Low | High | Deep tree, k-NN with $k=1$, unpruned neural net |

### Regularization as Bias-Variance Control
Regularization adds bias to reduce variance:

$$
\mathcal{L}_{\text{reg}} = \mathcal{L}_{\text{data}} + \lambda \cdot R(w)
$$

- **L2 (Ridge)**: $R(w) = \|w\|_2^2$ -- shrinks all coefficients, keeps all features
- **L1 (Lasso)**: $R(w) = \|w\|_1$ -- drives coefficients to zero, feature selection
- **ElasticNet**: $R(w) = \alpha\|w\|_1 + (1-\alpha)\|w\|_2^2$ -- compromise

### Double Descent
Modern deep learning challenges the classical U-shaped curve. In the interpolation regime ($d \gg n$), test error can decrease again after the interpolation threshold:

1. Classical regime: more parameters increases variance
2. Interpolation threshold: peak test error
3. Over-parameterized regime: implicit regularization via SGD reduces effective complexity

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Diagnosing under/overfitting | "Model performs poorly" | High training error = underfitting; large train-val gap = overfitting |
| Ensemble motivation | "Why use Random Forest?" | Bagging reduces variance; boosting reduces bias |
| Regularization selection | "Ridge vs. Lasso?" | Lasso for feature selection; Ridge when all features matter |
| Learning curves | "How to improve?" | More data helps high variance; model capacity helps high bias |

### Common Interview Questions
- [ ] Derive the bias-variance decomposition for MSE.
- [ ] How do bagging and boosting address bias and variance differently?
- [ ] Why does $k$-NN with $k=1$ have zero training error but high variance?
- [ ] Explain the double descent phenomenon.
- [ ] How does dropout act as regularization in neural networks?

## Key Takeaways

- [ ] Bias = underfitting, Variance = overfitting; total error is their sum + noise
- [ ] Increasing model complexity: bias decreases, variance increases (classically)
- [ ] Regularization injects bias to control variance -- $\lambda$ is the knob
- [ ] Bagging (Random Forest) reduces variance; Boosting (XGBoost) reduces bias
- [ ] Modern deep learning: double descent means more parameters can help beyond the interpolation threshold
"""

CONTENT["pillar2.supervised_learning.loss_functions"] = r"""# Loss Functions

## Overview
Loss functions quantify the discrepancy between predictions and targets. Choosing the right loss is critical -- it defines what your model optimizes for. Interview questions probe understanding of why specific losses are used, their gradients, and robustness properties.

## Core Concepts

### Regression Losses

**Mean Squared Error (MSE / L2 Loss)**:

$$
\mathcal{L}_{\text{MSE}} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2
$$

Gradient: $\nabla = -2(y - \hat{y})$. Sensitive to outliers (squared penalty).

**Mean Absolute Error (MAE / L1 Loss)**:

$$
\mathcal{L}_{\text{MAE}} = \frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|
$$

Robust to outliers. Non-differentiable at zero.

**Huber Loss** (best of both):

$$
L_\delta(r) = \begin{cases} \frac{1}{2}r^2 & \text{if } |r| \leq \delta \\ \delta(|r| - \frac{1}{2}\delta) & \text{otherwise} \end{cases}
$$

### Classification Losses

**Binary Cross-Entropy (Log Loss)**:

$$
\mathcal{L}_{\text{BCE}} = -\frac{1}{n}\sum_{i}[y_i\log(\hat{p}_i) + (1-y_i)\log(1-\hat{p}_i)]
$$

**Hinge Loss** (SVM):

$$
\mathcal{L}_{\text{hinge}} = \frac{1}{n}\sum_i \max(0, 1 - y_i \cdot f(x_i)), \quad y_i \in \{-1, +1\}
$$

**Focal Loss** (class imbalance):

$$
\mathcal{L}_{\text{focal}} = -\alpha_t(1 - p_t)^\gamma \log(p_t)
$$

Down-weights easy examples when $\gamma > 0$; $\gamma = 2$ is common.

### Ranking Losses

**Pairwise (BPR)**:

$$
\mathcal{L}_{\text{BPR}} = -\sum_{(i,j)} \log \sigma(f(x_i) - f(x_j))
$$

where item $i$ is preferred over item $j$.

**Listwise (ListNet)**: uses cross-entropy over top-1 probability distributions.

## Implementation

```python
import numpy as np

def huber_loss(y_true, y_pred, delta=1.0):
    r = y_true - y_pred
    return np.where(np.abs(r) <= delta,
                    0.5 * r**2,
                    delta * (np.abs(r) - 0.5 * delta))

def focal_loss(y_true, y_pred, gamma=2.0, alpha=0.25):
    p_t = np.where(y_true == 1, y_pred, 1 - y_pred)
    alpha_t = np.where(y_true == 1, alpha, 1 - alpha)
    return -alpha_t * (1 - p_t)**gamma * np.log(p_t + 1e-8)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| MSE vs. MAE | Outlier sensitivity | MSE: penalizes large errors quadratically; MAE: linear penalty |
| Cross-entropy motivation | "Why not MSE for classification?" | MSE has vanishing gradients near 0/1 for sigmoid outputs |
| Focal loss | Severe class imbalance | Reduces loss for well-classified examples |
| Custom loss for business | "Revenue optimization" | Define loss aligned with business metric (e.g., asymmetric cost) |

### Common Interview Questions
- [ ] Why use cross-entropy instead of MSE for classification?
- [ ] Derive the gradient of binary cross-entropy.
- [ ] When would you use Huber loss over MSE?
- [ ] How does focal loss address class imbalance?
- [ ] Design a custom loss for a problem where false negatives cost 10x false positives.

## Comparisons

| Loss | Task | Outlier Robust | Differentiable | Probabilistic |
|------|------|---------------|----------------|---------------|
| MSE | Regression | No | Yes | Yes (Gaussian) |
| MAE | Regression | Yes | No (at 0) | Yes (Laplace) |
| Huber | Regression | Yes | Yes | Approx |
| Cross-entropy | Classification | N/A | Yes | Yes |
| Hinge | Classification | N/A | No (at 1) | No |
| Focal | Classification | N/A | Yes | No |

## Key Takeaways

- [ ] Each loss implies a probabilistic assumption: MSE = Gaussian noise, MAE = Laplace
- [ ] Cross-entropy is the standard for classification -- it provides proper probability calibration
- [ ] Huber loss: quadratic near zero, linear far away -- use when outliers exist but gradients matter
- [ ] Focal loss: $\gamma$ controls down-weighting of easy examples; critical for detection tasks
- [ ] For interviews, know gradients of MSE, cross-entropy, and hinge loss
"""

CONTENT["pillar2.supervised_learning.regularization"] = r"""# Regularization

## Overview
Regularization prevents overfitting by constraining model complexity. It is one of the most fundamental tools in ML -- every production model uses some form of regularization. Interviews test understanding of L1 vs. L2, dropout, early stopping, and their theoretical connections.

## Core Concepts

### L2 Regularization (Ridge / Weight Decay)

$$
\mathcal{L}_{\text{ridge}} = \mathcal{L}_{\text{data}} + \lambda \sum_j w_j^2
$$

Effect: shrinks all weights toward zero proportionally. In linear regression:

$$
\beta_{\text{ridge}} = (X^TX + \lambda I)^{-1}X^Ty
$$

Adds $\lambda$ to diagonal of $X^TX$, making it always invertible.

### L1 Regularization (Lasso)

$$
\mathcal{L}_{\text{lasso}} = \mathcal{L}_{\text{data}} + \lambda \sum_j |w_j|
$$

Effect: drives small weights exactly to zero (sparsity/feature selection). The L1 ball has corners on axes, promoting sparse solutions.

### Elastic Net

$$
\mathcal{L}_{\text{elastic}} = \mathcal{L}_{\text{data}} + \lambda_1 \sum_j |w_j| + \lambda_2 \sum_j w_j^2
$$

Combines L1 sparsity with L2 stability. Handles correlated features better than pure Lasso.

### Dropout
During training, randomly zero out each neuron with probability $p$:

$$
\tilde{h}_i = \begin{cases} 0 & \text{with prob } p \\ \frac{h_i}{1-p} & \text{with prob } 1-p \end{cases}
$$

Equivalent to training an ensemble of $2^n$ sub-networks. At inference, use all neurons (already scaled).

### Early Stopping
Stop training when validation loss stops improving. Equivalent to L2 regularization in linear models (number of gradient steps acts as inverse of $\lambda$).

### Other Techniques

| Technique | Mechanism | Common In |
|-----------|-----------|-----------|
| Data augmentation | Increase effective training set | Vision, NLP |
| Batch normalization | Reduces internal covariate shift | Deep learning |
| Label smoothing | Soften one-hot targets: $(1-\epsilon)y + \epsilon/K$ | Classification |
| Weight tying | Share parameters across layers | Transformers, autoencoders |
| Mixup | Interpolate training examples | Vision |

## Implementation

```python
import torch.nn as nn

# PyTorch: L2 via weight_decay in optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)

# Dropout layer
model = nn.Sequential(
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(p=0.3),  # 30% dropout
    nn.Linear(128, 10),
)

# Label smoothing
loss_fn = nn.CrossEntropyLoss(label_smoothing=0.1)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| L1 vs. L2 geometry | "Why does L1 produce sparsity?" | L1 ball corners lie on axes; gradient pushes weights to exactly zero |
| Dropout as ensemble | "Explain dropout theoretically" | Each forward pass samples a sub-network; inference averages all |
| Early stopping = L2 | "Connection between techniques?" | Number of SGD steps is inversely related to regularization strength |
| Regularization in production | System design | Weight decay + dropout + early stopping are standard in deep learning |

### Common Interview Questions
- [ ] Why does L1 regularization produce sparse solutions but L2 does not?
- [ ] What is the Bayesian interpretation of L2 regularization?
- [ ] How does dropout differ between training and inference?
- [ ] Is batch normalization a form of regularization? Why?
- [ ] How would you choose between L1, L2, and Elastic Net?

## Key Takeaways

- [ ] L2 (Ridge): Gaussian prior on weights, shrinks all weights, always invertible
- [ ] L1 (Lasso): Laplace prior, produces sparsity, use for feature selection
- [ ] Dropout: ensemble of sub-networks; scale by $1/(1-p)$ during training (inverted dropout)
- [ ] Early stopping: cheapest regularization -- always use it
- [ ] In practice, combine multiple regularizers: weight decay + dropout + early stopping
"""

CONTENT["pillar2.supervised_learning.evaluation_metrics"] = r"""# Evaluation Metrics

## Overview
Choosing the right evaluation metric is as important as choosing the model. Metrics should align with business objectives. Interviews frequently ask about metric tradeoffs, threshold selection, and metrics for imbalanced datasets.

## Core Concepts

### Classification Metrics

**Confusion Matrix**:

|  | Predicted + | Predicted - |
|--|------------|------------|
| Actual + | TP | FN |
| Actual - | FP | TN |

**Core metrics**:

$$
\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}
$$

$$
\text{F1} = \frac{2 \cdot P \cdot R}{P + R} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN}
$$

$$
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
$$

**AUC-ROC**: Area under the curve of TPR vs. FPR across all thresholds. Threshold-independent. Interpretation: probability that a random positive ranks higher than a random negative.

**AUC-PR**: Area under Precision-Recall curve. Better than AUC-ROC for imbalanced datasets.

**Log Loss**: measures calibration quality:

$$
\text{LogLoss} = -\frac{1}{n}\sum_i [y_i \log p_i + (1-y_i)\log(1-p_i)]
$$

### Regression Metrics

$$
\text{MSE} = \frac{1}{n}\sum(y_i - \hat{y}_i)^2, \quad \text{RMSE} = \sqrt{\text{MSE}}
$$

$$
\text{MAE} = \frac{1}{n}\sum|y_i - \hat{y}_i|, \quad R^2 = 1 - \frac{\sum(y_i-\hat{y}_i)^2}{\sum(y_i-\bar{y})^2}
$$

**MAPE**: $\frac{1}{n}\sum\frac{|y_i - \hat{y}_i|}{|y_i|}$ -- interpretable as percentage but undefined when $y_i = 0$.

### Ranking Metrics

$$
\text{NDCG@k} = \frac{DCG@k}{IDCG@k}, \quad DCG@k = \sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)}
$$

$$
\text{MRR} = \frac{1}{|Q|}\sum_{q=1}^{|Q|}\frac{1}{\text{rank}_q}
$$

| Metric | Use Case |
|--------|----------|
| NDCG | Search ranking, recommendations |
| MRR | First relevant result matters |
| MAP | Multiple relevant results per query |
| Hit Rate@k | Recommendation top-k accuracy |

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Precision vs. Recall tradeoff | Imbalanced classification | Spam: optimize precision; disease: optimize recall |
| AUC-ROC vs. AUC-PR | Severe imbalance | AUC-ROC can be misleadingly high with many TNs |
| Offline vs. online metrics | System design | Offline: AUC, NDCG. Online: CTR, conversion, revenue |
| Threshold selection | "How to set the threshold?" | Business cost matrix: minimize expected cost |

### Common Interview Questions
- [ ] Why is accuracy misleading for imbalanced datasets?
- [ ] Explain AUC-ROC intuitively. What does AUC = 0.5 mean?
- [ ] When would you use F2-score instead of F1?
- [ ] How do offline and online metrics differ? Give an example where they disagree.
- [ ] How would you choose a classification threshold in production?

## Key Takeaways

- [ ] Always pick metrics aligned with business objectives, not just model quality
- [ ] Imbalanced data: use AUC-PR, F1, or weighted metrics instead of accuracy
- [ ] Ranking: NDCG is position-aware and handles graded relevance
- [ ] Calibration matters when probabilities are used downstream (e.g., bidding systems)
- [ ] Online metrics (CTR, revenue) are the ground truth; offline metrics are proxies
"""

# ===== UNSUPERVISED LEARNING =====

CONTENT["pillar2.unsupervised_learning.clustering"] = r"""# Clustering

## Overview
Clustering groups similar data points without labels. Critical for customer segmentation, anomaly detection, and feature engineering in MLE interviews. Key: understanding algorithm assumptions, scalability, and evaluation without ground truth.

## Core Concepts

### K-Means
Minimizes within-cluster sum of squares (WCSS):

$$
\arg\min_{\mu_1,...,\mu_K} \sum_{k=1}^{K}\sum_{x_i \in C_k} \|x_i - \mu_k\|^2
$$

**Algorithm**: (1) Initialize centroids, (2) Assign points to nearest centroid, (3) Update centroids as cluster means, (4) Repeat until convergence.

Complexity: $O(nKdT)$ for $n$ points, $K$ clusters, $d$ dimensions, $T$ iterations.

**K-Means++**: Smart initialization -- first centroid random, subsequent centroids sampled proportional to $D(x)^2$ (distance to nearest existing centroid). Provably $O(\log K)$-competitive with optimal.

### DBSCAN
Density-based: groups points in high-density regions, marks sparse points as noise.

Parameters: $\epsilon$ (neighborhood radius), $\text{minPts}$ (minimum neighbors for core point).

| Point Type | Definition |
|-----------|-----------|
| Core | $\geq \text{minPts}$ neighbors within $\epsilon$ |
| Border | Within $\epsilon$ of a core point but not core itself |
| Noise | Neither core nor border |

Advantages: discovers arbitrary shapes, handles noise, no need to specify $K$.

### Hierarchical Clustering
- **Agglomerative** (bottom-up): start with $n$ clusters, merge closest pairs
- **Divisive** (top-down): start with 1 cluster, recursively split

Linkage criteria: single (min), complete (max), average, Ward (min variance).

### Gaussian Mixture Models (GMM)
Probabilistic clustering: each cluster is a Gaussian $\mathcal{N}(\mu_k, \Sigma_k)$:

$$
p(x) = \sum_{k=1}^{K} \pi_k \mathcal{N}(x|\mu_k, \Sigma_k)
$$

Fitted via EM algorithm. Soft assignments (probabilities vs. hard cluster labels).

## Implementation

```python
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

# K-Means with elbow method
inertias = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, init="k-means++", n_init=10)
    km.fit(X)
    inertias.append(km.inertia_)

# DBSCAN
db = DBSCAN(eps=0.5, min_samples=5)
labels = db.fit_predict(X)
n_noise = (labels == -1).sum()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Choosing $K$ | "How many clusters?" | Elbow method (inertia), silhouette score, domain knowledge |
| K-Means limitations | Non-spherical clusters | Use DBSCAN or GMM for irregular shapes |
| Scalability | Large datasets | Mini-batch K-Means for $n > 100K$; DBSCAN is $O(n^2)$ without spatial index |
| Evaluation without labels | No ground truth | Silhouette score, Davies-Bouldin index, domain-specific validation |

### Common Interview Questions
- [ ] When does K-Means fail? Give examples.
- [ ] How does DBSCAN handle noise and varying density?
- [ ] Compare K-Means vs. GMM: when would you choose each?
- [ ] How do you evaluate clustering quality without labels?
- [ ] Design a customer segmentation pipeline for an e-commerce company.

## Key Takeaways

- [ ] K-Means: fast, simple, assumes spherical clusters of similar size
- [ ] DBSCAN: no need to specify $K$, finds arbitrary shapes, handles noise
- [ ] GMM: soft assignments, flexible cluster shapes via covariance matrices
- [ ] Always scale features before clustering
- [ ] Silhouette score is the go-to internal validation metric
"""

CONTENT["pillar2.unsupervised_learning.dimensionality_reduction"] = r"""# Dimensionality Reduction

## Overview
Dimensionality reduction projects high-dimensional data to a lower-dimensional space while preserving important structure. Essential for visualization, feature engineering, and combating the curse of dimensionality. PCA is the most interview-tested technique.

## Core Concepts

### PCA (Principal Component Analysis)
Finds orthogonal directions of maximum variance. Given centered data $X \in \mathbb{R}^{n \times d}$:

$$
X = U\Sigma V^T \quad \text{(SVD)}
$$

Principal components: columns of $V$. Projected data: $Z = XV_k$ (keep top $k$ components).

**Variance explained** by $k$ components:

$$
\text{Explained Variance Ratio} = \frac{\sum_{i=1}^{k} \sigma_i^2}{\sum_{i=1}^{d} \sigma_i^2}
$$

Choose $k$ to retain 95% variance (common heuristic).

### Kernel PCA
For nonlinear structure, apply PCA in kernel-induced feature space:

$$
K_{ij} = \phi(x_i)^T\phi(x_j)
$$

Center the kernel matrix, then eigendecompose. Common kernels: RBF, polynomial.

### t-SNE
Non-linear technique for 2D/3D visualization. Preserves local structure via:

$$
p_{j|i} = \frac{\exp(-\|x_i-x_j\|^2/2\sigma_i^2)}{\sum_{k\neq i}\exp(-\|x_i-x_k\|^2/2\sigma_i^2)}
$$

$$
q_{ij} = \frac{(1+\|y_i-y_j\|^2)^{-1}}{\sum_{k\neq l}(1+\|y_k-y_l\|^2)^{-1}}
$$

Minimizes KL divergence $KL(P\|Q)$ via gradient descent. **Perplexity** controls effective neighborhood size.

### UMAP
Faster alternative to t-SNE with better global structure preservation. Based on topological data analysis. Scales to millions of points.

| Method | Linear | Preserves | Speed | Use Case |
|--------|--------|-----------|-------|----------|
| PCA | Yes | Global variance | Fast | Feature reduction, preprocessing |
| t-SNE | No | Local structure | Slow | 2D visualization |
| UMAP | No | Local + global | Fast | Visualization, clustering |

## Implementation

```python
from sklearn.decomposition import PCA
import numpy as np

# PCA with variance threshold
pca = PCA(n_components=0.95)  # keep 95% variance
X_reduced = pca.fit_transform(X)
print(f"Reduced: {X.shape[1]} -> {X_reduced.shape[1]} dims")
print(f"Components: {pca.n_components_}")

# Incremental PCA for large datasets
from sklearn.decomposition import IncrementalPCA
ipca = IncrementalPCA(n_components=50, batch_size=1000)
for batch in np.array_split(X, 100):
    ipca.partial_fit(batch)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| PCA for feature engineering | High-dim features | Reduce multicollinearity before linear models |
| t-SNE pitfalls | Visualization | Cluster sizes/distances in t-SNE are meaningless; only topology matters |
| PCA vs. autoencoders | Nonlinear reduction | Linear PCA = single-layer autoencoder with linear activation |
| Curse of dimensionality | "Why reduce dimensions?" | Distance metrics become meaningless in high dims |

### Common Interview Questions
- [ ] Derive PCA from the maximum variance perspective.
- [ ] What is the relationship between PCA and SVD?
- [ ] Why can't you use t-SNE for new test points?
- [ ] When would you prefer PCA over an autoencoder?
- [ ] How do you choose the number of PCA components?

## Key Takeaways

- [ ] PCA: eigendecomposition of covariance matrix (or SVD of data matrix)
- [ ] Always center (and usually scale) data before PCA
- [ ] t-SNE: only for visualization; cluster sizes and distances are not meaningful
- [ ] UMAP: faster than t-SNE, better global structure, works for larger datasets
- [ ] Rule of thumb: PCA for preprocessing, t-SNE/UMAP for visualization
"""

CONTENT["pillar2.unsupervised_learning.anomaly_detection"] = r"""# Anomaly Detection

## Overview
Anomaly detection identifies data points that deviate significantly from normal patterns. Critical for fraud detection, system monitoring, and data quality. Interviews test understanding of statistical vs. ML approaches and the challenge of evaluating without labels.

## Core Concepts

### Statistical Methods

**Z-score**: flag points where $|z| > 3$:

$$
z = \frac{x - \mu}{\sigma}
$$

Assumes Gaussian distribution. For multivariate data, use Mahalanobis distance:

$$
D_M(x) = \sqrt{(x-\mu)^T \Sigma^{-1} (x-\mu)}
$$

### Isolation Forest
Key insight: anomalies are easier to isolate (fewer random splits needed).

- Build random trees with random feature + random split value
- Anomaly score based on average path length $E[h(x)]$:

$$
s(x, n) = 2^{-E[h(x)]/c(n)}
$$

where $c(n) = 2H(n-1) - 2(n-1)/n$ (average path length in a BST). Score near 1 = anomaly.

### One-Class SVM
Learn a decision boundary around normal data in kernel space:

$$
\min_{w,\xi,\rho} \frac{1}{2}\|w\|^2 + \frac{1}{\nu n}\sum_i \xi_i - \rho \quad \text{s.t.} \quad w^T\phi(x_i) \geq \rho - \xi_i
$$

$\nu$ controls the fraction of outliers (upper bound on anomaly ratio).

### Autoencoder-Based
Train autoencoder on normal data. Anomalies have high reconstruction error:

$$
\text{anomaly\_score}(x) = \|x - \text{decode}(\text{encode}(x))\|^2
$$

Threshold on reconstruction error. Works well for high-dimensional data (images, sequences).

## Implementation

```python
from sklearn.ensemble import IsolationForest

# Isolation Forest
iso = IsolationForest(
    n_estimators=200,
    contamination=0.01,  # expected anomaly fraction
    random_state=42
)
iso.fit(X_train)  # train on normal data
scores = iso.decision_function(X_test)  # lower = more anomalous
predictions = iso.predict(X_test)  # -1 = anomaly, 1 = normal
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Choosing method | Tabular vs. sequential vs. image | Isolation Forest for tabular; autoencoders for high-dim |
| Evaluation challenge | No labels | Use synthetic anomalies, domain expert review, or business metrics |
| Feature engineering | Time-series anomalies | Compute rolling stats, then apply point anomaly detection |
| Threshold selection | Production deployment | Use business cost to set threshold; alert fatigue vs. missed detections |

### Common Interview Questions
- [ ] Why does Isolation Forest work well for anomaly detection?
- [ ] How would you detect anomalies in a time series of server metrics?
- [ ] Compare Isolation Forest vs. One-Class SVM.
- [ ] How do you evaluate an anomaly detector without labeled anomalies?
- [ ] Design a fraud detection system for a payment platform.

## Key Takeaways

- [ ] Isolation Forest: fast, scalable, assumption-free -- default choice for tabular data
- [ ] Statistical methods (Z-score, Mahalanobis): simple, interpretable, require distribution assumptions
- [ ] Autoencoders: best for high-dimensional data where reconstruction error indicates anomaly
- [ ] Evaluation is the hardest part -- use precision@k, business metrics, or expert review
- [ ] In production: combine multiple detectors and use human-in-the-loop for threshold tuning
"""

# ===== OPTIMIZATION =====

CONTENT["pillar2.optimization.gradient_descent"] = r"""# Gradient Descent Family

## Overview
Gradient descent and its variants are the backbone of ML optimization. Every neural network, logistic regression, and many tree methods use gradient-based optimization. Interviews test understanding of convergence properties, momentum, and adaptive methods.

## Core Concepts

### Vanilla Gradient Descent

$$
w_{t+1} = w_t - \eta \nabla \mathcal{L}(w_t)
$$

| Variant | Batch Size | Pros | Cons |
|---------|-----------|------|------|
| Batch GD | Full dataset | Stable gradients | Slow, memory-heavy |
| Stochastic GD (SGD) | 1 sample | Fast updates, escapes local minima | Noisy |
| Mini-batch GD | $B$ samples | Best tradeoff | Requires tuning $B$ |

### Momentum

$$
v_t = \beta v_{t-1} + \nabla \mathcal{L}(w_t), \quad w_{t+1} = w_t - \eta v_t
$$

Accelerates convergence along consistent gradient directions. Typical $\beta = 0.9$.

**Nesterov Momentum**: look-ahead gradient:

$$
v_t = \beta v_{t-1} + \nabla \mathcal{L}(w_t - \eta \beta v_{t-1}), \quad w_{t+1} = w_t - \eta v_t
$$

### Adaptive Methods

**AdaGrad**: per-parameter learning rate based on historical gradients:

$$
w_{t+1,j} = w_{t,j} - \frac{\eta}{\sqrt{G_{t,jj} + \epsilon}} \nabla_j \mathcal{L}
$$

where $G_t = \sum_{\tau=1}^{t} g_\tau g_\tau^T$. Problem: learning rate monotonically decreases.

**RMSProp**: exponential moving average of squared gradients:

$$
v_t = \gamma v_{t-1} + (1-\gamma)g_t^2, \quad w_{t+1} = w_t - \frac{\eta}{\sqrt{v_t + \epsilon}}g_t
$$

**Adam** (Adaptive Moment Estimation):

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t \quad \text{(1st moment)}
$$

$$
v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2 \quad \text{(2nd moment)}
$$

$$
\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t} \quad \text{(bias correction)}
$$

$$
w_{t+1} = w_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon}\hat{m}_t
$$

Defaults: $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$.

**AdamW**: decoupled weight decay (correct L2 regularization for Adam):

$$
w_{t+1} = (1 - \lambda)w_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon}\hat{m}_t
$$

## Implementation

```python
import torch

# AdamW with linear warmup + cosine decay
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| SGD vs. Adam | "Which optimizer?" | Adam converges faster; SGD generalizes better with proper tuning |
| AdamW for transformers | LLM training | Standard choice; decoupled weight decay is critical |
| Batch size effects | "How does batch size affect training?" | Larger batch = less noise, may need larger LR (linear scaling rule) |
| Gradient clipping | Exploding gradients | Clip by norm: $g \leftarrow g \cdot \min(1, \frac{\theta}{\|g\|})$ |

### Common Interview Questions
- [ ] Explain Adam step by step. What do $m_t$ and $v_t$ represent?
- [ ] Why does AdamW fix the weight decay problem in Adam?
- [ ] When would you prefer SGD with momentum over Adam?
- [ ] What causes exploding/vanishing gradients and how do you fix them?
- [ ] Derive the gradient descent update from the Taylor expansion perspective.

## Key Takeaways

- [ ] SGD + momentum: best generalization but requires careful LR tuning
- [ ] Adam/AdamW: fast convergence, less sensitive to LR, standard for transformers
- [ ] Bias correction in Adam prevents early updates from being too small
- [ ] Gradient clipping: essential for RNNs and large-scale training
- [ ] Linear scaling rule: when doubling batch size, double the learning rate
"""

CONTENT["pillar2.optimization.learning_rate"] = r"""# Learning Rate Scheduling

## Overview
The learning rate is the single most important hyperparameter. Too high: divergence. Too low: slow convergence or getting stuck. Scheduling strategies systematically adjust the learning rate during training for better convergence and generalization.

## Core Concepts

### Warmup
Start with a small LR and linearly increase to the target:

$$
\eta_t = \eta_{\max} \cdot \frac{t}{T_{\text{warmup}}}
$$

Why: stabilizes training in the initial phase when gradients are large and unreliable (especially with Adam's small denominators early on).

### Common Schedules

**Step Decay**: reduce by factor $\gamma$ every $k$ epochs:

$$
\eta_t = \eta_0 \cdot \gamma^{\lfloor t/k \rfloor}
$$

**Cosine Annealing**:

$$
\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\frac{t\pi}{T}\right)
$$

Smooth decay to near-zero. Standard for vision and LLM training.

**Cosine with Warm Restarts** (SGDR):

$$
\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\frac{T_{\text{cur}}}{T_i}\pi\right)
$$

Periodically reset LR to escape local minima.

**One-Cycle Policy**: warmup to max LR, then cosine decay. Often finds good solutions faster.

**Inverse Square Root** (Transformer default):

$$
\eta_t = d_{\text{model}}^{-0.5} \cdot \min(t^{-0.5}, t \cdot T_{\text{warmup}}^{-1.5})
$$

### Learning Rate Finder
Gradually increase LR from very small to very large, plot loss vs. LR. Choose LR where loss is steepest (just before divergence). Popularized by fast.ai.

## Implementation

```python
import torch.optim as optim

# Warmup + Cosine decay
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=10, T_mult=2, eta_min=1e-6
)

# One-Cycle
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=1e-3, total_steps=num_epochs * steps_per_epoch
)

# Linear warmup + cosine (manual)
def lr_lambda(step):
    if step < warmup_steps:
        return step / warmup_steps
    progress = (step - warmup_steps) / (total_steps - warmup_steps)
    return 0.5 * (1 + math.cos(math.pi * progress))
scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Warmup necessity | Transformers, large batch | Prevents early divergence from large initial gradients |
| Cosine vs. step decay | "Which schedule?" | Cosine is smoother, avoids sudden jumps; step is simpler |
| LR-batch size coupling | Scaling training | Linear scaling: $\eta \propto B$ (up to a point) |
| Cyclical LR | Escaping local minima | Periodic LR increases help explore loss landscape |

### Common Interview Questions
- [ ] Why is warmup important for Transformer training?
- [ ] Compare cosine annealing vs. step decay. When is each better?
- [ ] How do you use a learning rate finder?
- [ ] What is the relationship between batch size and learning rate?
- [ ] Explain the one-cycle policy and why it works.

## Key Takeaways

- [ ] Warmup + cosine decay is the modern default for most deep learning
- [ ] Learning rate finder: quick way to find the right ballpark
- [ ] One-cycle policy: fast convergence for supervised tasks
- [ ] Inverse square root: standard for original Transformer training
- [ ] When scaling batch size, scale LR proportionally (linear scaling rule)
"""

CONTENT["pillar2.optimization.convergence"] = r"""# Convergence & Loss Landscape

## Overview
Understanding convergence guarantees and loss landscape geometry helps diagnose training issues and select optimization strategies. Interviews probe knowledge of convexity, saddle points, and why deep learning works despite non-convex objectives.

## Core Concepts

### Convexity

A function $f$ is convex if:

$$
f(\alpha x + (1-\alpha)y) \leq \alpha f(x) + (1-\alpha)f(y), \quad \forall \alpha \in [0,1]
$$

**Strongly convex** (with parameter $\mu > 0$): $f(y) \geq f(x) + \nabla f(x)^T(y-x) + \frac{\mu}{2}\|y-x\|^2$

Convergence rates for gradient descent:

| Condition | Rate | Steps to $\epsilon$-optimal |
|-----------|------|---------------------------|
| Convex, $L$-smooth | $O(1/T)$ | $O(L/\epsilon)$ |
| Strongly convex ($\mu$-SC) | $O(e^{-\mu T/L})$ | $O(\frac{L}{\mu}\log\frac{1}{\epsilon})$ |
| Non-convex, $L$-smooth | $O(1/\sqrt{T})$ to stationary point | $O(L/\epsilon^2)$ |

The condition number $\kappa = L/\mu$ determines how elongated the loss landscape is.

### Saddle Points
In high dimensions, saddle points are far more common than local minima. At a critical point, the Hessian has both positive and negative eigenvalues.

**Why SGD escapes saddle points**: gradient noise provides perturbation. Saddle points are unstable equilibria for noisy gradient methods.

### Loss Landscape of Deep Networks
- **Mode connectivity**: different minima are connected by paths of nearly constant loss
- **Flat vs. sharp minima**: flat minima generalize better (SAM optimizer targets this)
- **Lottery ticket hypothesis**: sparse sub-networks can match dense network performance

### Gradient Pathologies

| Issue | Symptom | Fix |
|-------|---------|-----|
| Vanishing gradients | Early layers don't learn | Skip connections, better activation (ReLU), normalization |
| Exploding gradients | Loss goes to NaN | Gradient clipping, initialization (He/Xavier) |
| Loss plateaus | Loss stagnates | Learning rate warmup restart, different optimizer |

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Convexity check | "Is this problem convex?" | Linear/logistic regression: convex. Neural nets: non-convex |
| Saddle points vs. local minima | "Why does deep learning work?" | High-dim: saddle points dominate; SGD escapes them |
| Initialization matters | Training from scratch | Xavier/He init prevents vanishing/exploding at start |
| Batch norm + skip connections | Deep network training | Enable training of very deep networks by improving gradient flow |

### Common Interview Questions
- [ ] Is the loss function of logistic regression convex? Prove it.
- [ ] Why are saddle points more problematic than local minima in high dimensions?
- [ ] What is the role of the condition number in optimization convergence?
- [ ] How do skip connections help with vanishing gradients?
- [ ] What does it mean for a minimum to be "flat" and why does it matter?

## Key Takeaways

- [ ] Convex problems: guaranteed global optimum. Deep learning is non-convex but works in practice
- [ ] Condition number $\kappa = L/\mu$: high $\kappa$ means slow convergence; preconditioning helps
- [ ] Saddle points, not local minima, are the main challenge in high dimensions
- [ ] SGD noise helps escape saddle points and find flat minima (better generalization)
- [ ] Skip connections + batch norm + proper initialization = trainable deep networks
"""

CONTENT["pillar2.optimization.training_tricks"] = r"""# Training Tricks

## Overview
Practical training tricks bridge the gap between theory and working models. These techniques are essential knowledge for MLE interviews -- they show you can actually train models, not just derive equations.

## Core Concepts

### Weight Initialization

**Xavier (Glorot)** for sigmoid/tanh:

$$
W \sim \mathcal{N}\left(0, \frac{2}{n_{\text{in}} + n_{\text{out}}}\right) \quad \text{or} \quad W \sim U\left[-\sqrt{\frac{6}{n_{\text{in}}+n_{\text{out}}}}, \sqrt{\frac{6}{n_{\text{in}}+n_{\text{out}}}}\right]
$$

**He (Kaiming)** for ReLU:

$$
W \sim \mathcal{N}\left(0, \frac{2}{n_{\text{in}}}\right)
$$

Maintains variance of activations across layers, preventing vanishing/exploding signals.

### Batch Normalization

Normalize activations per mini-batch:

$$
\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \quad y_i = \gamma \hat{x}_i + \beta
$$

At inference: use running mean/variance (exponential moving average from training).

**Benefits**: faster convergence, higher learning rates, slight regularization.

**Layer Normalization**: normalize across features (not batch). Used in Transformers since batch statistics are unstable for variable-length sequences.

### Gradient Clipping

**By norm**:

$$
g \leftarrow g \cdot \min\left(1, \frac{\theta}{\|g\|}\right)
$$

**By value**: $g_i \leftarrow \text{clip}(g_i, -\theta, \theta)$

Essential for RNNs and Transformer training. Typical max norm: 1.0.

### Mixed Precision Training
Use FP16 for forward/backward pass, FP32 for weight updates:

1. Forward pass in FP16
2. Loss scaling: multiply loss by scale factor to prevent FP16 underflow
3. Backward pass in FP16
4. Unscale gradients, update FP32 master weights

Speedup: 2-3x on modern GPUs. Standard in LLM training.

### Other Tricks

| Trick | What It Does | When to Use |
|-------|-------------|-------------|
| Label smoothing | Replace one-hot with $(1-\epsilon, \epsilon/(K-1))$ | Prevents overconfident predictions |
| Exponential Moving Average (EMA) | Average weights over training | Smoother model for evaluation |
| Stochastic Weight Averaging (SWA) | Average weights from cyclic LR | Better generalization |
| Gradient accumulation | Simulate larger batch size | GPU memory limited |
| Learning rate warmup | Gradually increase LR | Large batch / Transformer training |

## Implementation

```python
import torch
from torch.cuda.amp import autocast, GradScaler

# Mixed precision training
scaler = GradScaler()
for batch in dataloader:
    optimizer.zero_grad()
    with autocast():
        output = model(batch)
        loss = criterion(output, targets)
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    scaler.step(optimizer)
    scaler.update()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| BatchNorm vs. LayerNorm | Architecture choice | BN for CNNs (batch stats); LN for Transformers (sequence stats) |
| Initialization strategy | "How do you initialize?" | He for ReLU; Xavier for sigmoid/tanh; pretrained when available |
| Training instability diagnosis | "Loss is NaN" | Check: LR too high, no grad clipping, bad init, data issues |
| Gradient accumulation | Limited GPU memory | Accumulate gradients over $k$ steps, then update |

### Common Interview Questions
- [ ] Why is He initialization better than Xavier for ReLU networks?
- [ ] Explain batch normalization: training vs. inference behavior.
- [ ] How does mixed precision training work? Why use loss scaling?
- [ ] Compare BatchNorm vs. LayerNorm. When do you use each?
- [ ] How would you train a model that doesn't fit in GPU memory?

## Key Takeaways

- [ ] Weight initialization: match to activation function (He for ReLU, Xavier for tanh)
- [ ] Batch Norm: normalizes per mini-batch; Layer Norm: normalizes per sample (for Transformers)
- [ ] Gradient clipping by norm: essential for stable training of deep networks
- [ ] Mixed precision: 2-3x speedup, standard practice for large models
- [ ] Gradient accumulation: effectively increases batch size without more memory
"""

# ===== FEATURE ENGINEERING =====

CONTENT["pillar2.feature_engineering.numerical"] = r"""# Numerical Features

## Overview
Proper handling of numerical features is foundational for ML pipelines. Scaling, transformation, and interaction features significantly impact model performance. Tree models are invariant to monotonic transforms, but linear models and neural nets require careful preprocessing.

## Core Concepts

### Scaling Methods

| Method | Formula | When to Use |
|--------|---------|-------------|
| StandardScaler | $z = \frac{x - \mu}{\sigma}$ | Gaussian-like features; most common |
| MinMaxScaler | $z = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$ | Bounded features; neural nets |
| RobustScaler | $z = \frac{x - \text{median}}{\text{IQR}}$ | Outlier-heavy data |
| MaxAbsScaler | $z = \frac{x}{|x_{\max}|}$ | Sparse data (preserves zeros) |

### Transformations

**Log transform**: $x' = \log(x + 1)$ -- handles right-skewed distributions (income, counts).

**Box-Cox**: $x' = \frac{x^\lambda - 1}{\lambda}$ (requires $x > 0$). Finds optimal $\lambda$ to normalize.

**Yeo-Johnson**: generalizes Box-Cox to handle negative values.

**Quantile transform**: maps to uniform or normal distribution. Non-parametric but destroys relationships between features.

### Binning / Discretization
Convert continuous to categorical:
- **Equal-width**: fixed bin boundaries
- **Equal-frequency (quantile)**: equal number of samples per bin
- **Domain-driven**: age groups, income brackets

Useful for: capturing nonlinear effects in linear models, reducing noise.

### Interaction Features

$$
x_{\text{new}} = x_i \cdot x_j, \quad x_{\text{ratio}} = \frac{x_i}{x_j + \epsilon}
$$

Polynomial features: `PolynomialFeatures(degree=2, interaction_only=True)` for pairwise interactions without self-products.

## Implementation

```python
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer([
    ("standard", StandardScaler(), ["age", "salary"]),
    ("power", PowerTransformer(method="yeo-johnson"), ["income"]),
    ("passthrough", "passthrough", ["tree_features"]),
])
X_processed = preprocessor.fit_transform(X_train)
# IMPORTANT: fit on train, transform on train+test
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Scaling for model type | "Do I need to scale?" | Required for SVM, kNN, linear, NN. Not needed for trees |
| Data leakage via scaling | "How to preprocess?" | Fit scaler on train only; transform test with train stats |
| Log transform for skew | Heavily right-skewed | $\log(x+1)$ is simple and effective |
| Feature crosses | Linear models | Manual interactions compensate for linearity assumption |

### Common Interview Questions
- [ ] Why does scaling matter for gradient-based optimization?
- [ ] How do you handle features with very different scales?
- [ ] When would you use quantile binning vs. equal-width binning?
- [ ] How do you prevent data leakage in feature preprocessing?
- [ ] Design a feature pipeline for a price prediction model.

## Key Takeaways

- [ ] Always fit transformers on training data only (prevent data leakage)
- [ ] StandardScaler is the default; use RobustScaler when outliers are present
- [ ] Log transform for right-skewed data; Box-Cox/Yeo-Johnson for general normalization
- [ ] Tree models don't need scaling but benefit from well-constructed features
- [ ] Interaction features can dramatically improve linear model performance
"""

CONTENT["pillar2.feature_engineering.categorical"] = r"""# Categorical Features

## Overview
Categorical feature encoding is critical for ML pipelines. The choice of encoding affects model performance, training speed, and memory usage. High-cardinality categoricals (user IDs, zip codes) require special treatment.

## Core Concepts

### Encoding Methods

| Method | Output Dim | Preserves Ordinality | Handles High Cardinality |
|--------|-----------|---------------------|------------------------|
| One-Hot | $K$ | No | No ($K$ can be huge) |
| Label/Ordinal | 1 | If ordered | Yes |
| Target Encoding | 1 | No | Yes |
| Binary Encoding | $\lceil\log_2 K\rceil$ | No | Yes |
| Hash Encoding | $H$ (fixed) | No | Yes |
| Embedding | $d$ (learned) | No | Yes |

### One-Hot Encoding
Creates $K$ binary columns. Standard for low-cardinality features ($K < 50$).

**Trap**: in linear models, $K$ dummy variables are collinear. Drop one column or use regularization.

### Target Encoding
Replace category with mean of target variable:

$$
x_{\text{encoded}} = \frac{n_k \cdot \bar{y}_k + m \cdot \bar{y}_{\text{global}}}{n_k + m}
$$

where $m$ is a smoothing parameter (prevents overfitting for rare categories).

**Risk**: data leakage if applied naively. Must use cross-validation encoding (fit on fold-out data).

### Embedding (Learned)
Map categories to dense vectors $\mathbb{R}^d$ via a lookup table trained end-to-end with the model.

$$
\text{embed}(c) = W[c, :] \in \mathbb{R}^d
$$

Rule of thumb for $d$: $\min(50, \lceil K/2 \rceil)$ or $\lceil K^{0.25} \rceil$.

### Hash Encoding (Feature Hashing)
Map categories to fixed-size vector via hash function:

$$
\text{index} = \text{hash}(x) \mod H
$$

Collisions are a feature: reduces dimensionality at cost of some information loss. Standard in ad-click prediction (huge feature spaces).

## Implementation

```python
import category_encoders as ce
from sklearn.preprocessing import OneHotEncoder

# Target encoding with smoothing (leakage-safe)
encoder = ce.TargetEncoder(cols=["city"], smoothing=10)
X_train["city_enc"] = encoder.fit_transform(
    X_train["city"], y_train
)
X_test["city_enc"] = encoder.transform(X_test["city"])

# LightGBM native categoricals (no encoding needed)
import lightgbm as lgb
lgb_data = lgb.Dataset(X, label=y,
                        categorical_feature=["city", "browser"])
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| High cardinality | User ID, product ID | Embeddings or hash encoding; never one-hot |
| Tree vs. linear models | Encoding choice | Trees: ordinal encoding works; linear: one-hot or target encoding |
| Target encoding leakage | "How to encode safely?" | Always use cross-validation encoding or fold-out strategy |
| Embedding transfer | Pre-trained features | Reuse embeddings across models (e.g., user embeddings) |

### Common Interview Questions
- [ ] When does one-hot encoding fail? What are alternatives?
- [ ] Explain target encoding and its leakage risk.
- [ ] How do you handle unseen categories at inference time?
- [ ] Compare label encoding vs. one-hot for tree models.
- [ ] How would you encode a feature with 1M unique values?

## Key Takeaways

- [ ] One-hot: standard for low cardinality; creates sparse high-dim features
- [ ] Target encoding: powerful for high cardinality, but leakage risk -- use CV encoding
- [ ] Embeddings: best for deep learning and very high cardinality; learned end-to-end
- [ ] LightGBM handles categoricals natively (optimal split finding)
- [ ] Hash encoding: fixed memory, handles unlimited cardinality with controlled collision
"""

CONTENT["pillar2.feature_engineering.text"] = r"""# Text Features

## Overview
Text feature engineering transforms unstructured text into numerical representations for ML models. The landscape spans from classical bag-of-words to modern transformer embeddings. Understanding the tradeoffs is essential for NLP system design interviews.

## Core Concepts

### Bag-of-Words and TF-IDF

**Bag-of-Words (BoW)**: count vector of word occurrences. Ignores order.

**TF-IDF** (Term Frequency-Inverse Document Frequency):

$$
\text{TF-IDF}(t,d) = \text{TF}(t,d) \times \text{IDF}(t) = \frac{f_{t,d}}{\sum_t f_{t,d}} \times \log\frac{N}{|\{d: t \in d\}|}
$$

- **TF**: how important is the word in this document
- **IDF**: how rare is the word across all documents

Variants: sublinear TF ($1 + \log \text{TF}$), smooth IDF ($\log\frac{N+1}{df+1} + 1$).

### N-grams
Capture local word order:
- Unigrams: individual words
- Bigrams: word pairs ("machine learning")
- Character n-grams: subword patterns ("##ing", "pre##")

Character n-grams handle misspellings and OOV words.

### Word Embeddings

**Word2Vec** (Mikolov et al.):
- **CBOW**: predict center word from context
- **Skip-gram**: predict context from center word

$$
P(w_o|w_i) = \frac{\exp(v_{w_o}'^T v_{w_i})}{\sum_{w=1}^{V}\exp(v_w'^T v_{w_i})}
$$

**GloVe**: factorizes co-occurrence matrix. $\log X_{ij} = w_i^T \tilde{w}_j + b_i + \tilde{b}_j$

**FastText**: extends Word2Vec with subword (character n-gram) embeddings. Handles OOV words.

### Sentence/Document Embeddings

| Method | Quality | Speed | Use Case |
|--------|---------|-------|----------|
| Average word vectors | Fair | Fast | Quick baseline |
| TF-IDF weighted average | Better | Fast | Improved baseline |
| Sentence-BERT | High | Medium | Semantic similarity |
| OpenAI embeddings | Very high | API call | Production retrieval |

## Implementation

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# TF-IDF with n-grams
tfidf = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=5,
    max_df=0.95,
)
X = tfidf.fit_transform(documents)

# Sentence embeddings via sentence-transformers
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(documents, batch_size=32)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| TF-IDF vs. embeddings | "How to represent text?" | TF-IDF: interpretable, fast. Embeddings: capture semantics |
| Dimensionality reduction | Large vocabulary | Hash vectorizer, truncated SVD on TF-IDF |
| Feature engineering for NLP | Text classification | Combine TF-IDF features with handcrafted (length, entity counts) |
| Embedding fine-tuning | Domain-specific | Fine-tune sentence-BERT on domain data for retrieval |

### Common Interview Questions
- [ ] Explain TF-IDF and why IDF matters.
- [ ] Compare Word2Vec CBOW vs. Skip-gram.
- [ ] How do you handle out-of-vocabulary words?
- [ ] When would you use TF-IDF over transformer embeddings?
- [ ] Design a text similarity system for duplicate detection.

## Key Takeaways

- [ ] TF-IDF: strong baseline for classification; fast, interpretable, no training needed
- [ ] Word2Vec/GloVe: dense word-level embeddings; capture semantic relationships
- [ ] FastText: handles OOV via subword embeddings
- [ ] Sentence-BERT: current go-to for semantic similarity and retrieval
- [ ] In practice: start with TF-IDF + logistic regression, upgrade to embeddings if needed
"""

CONTENT["pillar2.feature_engineering.temporal"] = r"""# Temporal Features

## Overview
Time-based feature engineering extracts patterns from timestamps and time series data. Critical for forecasting, recommendation systems, and fraud detection. The key challenge is encoding cyclical patterns and capturing temporal dependencies without data leakage.

## Core Concepts

### Timestamp Decomposition

| Feature | Example | Captures |
|---------|---------|----------|
| Hour of day | 0-23 | Daily patterns (peak hours) |
| Day of week | 0-6 | Weekly patterns (weekday/weekend) |
| Month | 1-12 | Seasonal patterns |
| Is holiday | 0/1 | Holiday effects |
| Time since event | Minutes | Recency (last purchase, last login) |
| Day of year | 1-366 | Annual cycles |

### Cyclical Encoding
Encode cyclical features (hour, day of week) using sine/cosine:

$$
x_{\sin} = \sin\left(\frac{2\pi \cdot t}{T}\right), \quad x_{\cos} = \cos\left(\frac{2\pi \cdot t}{T}\right)
$$

where $T$ is the period (24 for hours, 7 for days). This ensures hour 23 and hour 0 are adjacent.

### Lag Features
For time series, create lagged values:

$$
x_{t-1}, x_{t-2}, \ldots, x_{t-k}
$$

**Rolling statistics**: mean, std, min, max over a window:

$$
\text{rolling\_mean}_{w}(t) = \frac{1}{w}\sum_{i=0}^{w-1} x_{t-i}
$$

**Exponential Moving Average (EMA)**:

$$
\text{EMA}_t = \alpha \cdot x_t + (1-\alpha) \cdot \text{EMA}_{t-1}
$$

### Trend and Seasonality
- **Trend**: long-term direction. Extract via linear regression or differencing
- **Seasonality**: periodic patterns. Extract via Fourier features or seasonal decomposition
- **Residual**: random component after removing trend and seasonality

Fourier features for capturing periodicity:

$$
x_k = \sin\left(\frac{2\pi k t}{T}\right), \quad x_{k+1} = \cos\left(\frac{2\pi k t}{T}\right), \quad k = 1, 2, \ldots
$$

## Implementation

```python
import pandas as pd
import numpy as np

def create_temporal_features(df, date_col="timestamp"):
    dt = pd.to_datetime(df[date_col])
    df["hour"] = dt.dt.hour
    df["dow"] = dt.dt.dayofweek
    df["month"] = dt.dt.month

    # Cyclical encoding
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    # Lag features (careful: sort by time first!)
    df = df.sort_values(date_col)
    for lag in [1, 7, 30]:
        df[f"value_lag_{lag}"] = df["value"].shift(lag)

    # Rolling stats
    df["rolling_7d_mean"] = df["value"].rolling(7).mean()
    df["rolling_7d_std"] = df["value"].rolling(7).std()
    return df
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Cyclical encoding | Time-of-day, day-of-week | Sin/cos preserves cyclical adjacency |
| Lag feature leakage | Time series CV | Never use future data; use expanding or sliding window CV |
| Recency features | User behavior | Time since last action is a powerful feature |
| Holiday/event flags | Demand forecasting | Binary or categorical flags for known events |

### Common Interview Questions
- [ ] How do you encode hour-of-day for a linear model?
- [ ] What is the risk of data leakage with lag features?
- [ ] How do you handle time series cross-validation?
- [ ] Design features for predicting next-day demand.
- [ ] How do you capture both daily and weekly seasonality?

## Key Takeaways

- [ ] Cyclical encoding (sin/cos) is essential for periodic features in non-tree models
- [ ] Lag features + rolling statistics are the core of time series feature engineering
- [ ] Always sort by time before creating lags; never shuffle time series data
- [ ] Time series CV: use expanding window or walk-forward validation, never random split
- [ ] Recency features (time since X) are among the most powerful predictors in recommendation
"""

CONTENT["pillar2.feature_engineering.missing_values"] = r"""# Missing Value Handling

## Overview
Missing data is ubiquitous in real-world ML. Proper handling prevents bias and information loss. Interviews test understanding of missingness types, imputation strategies, and how different models handle missing values natively.

## Core Concepts

### Types of Missingness

| Type | Definition | Example | Implication |
|------|-----------|---------|-------------|
| MCAR | Missing Completely At Random | Random sensor failures | Safe to drop; no bias |
| MAR | Missing At Random (depends on observed) | High-income people skip income question less | Imputation using observed features works |
| MNAR | Missing Not At Random (depends on unobserved) | Sick patients miss appointments | Hardest; may need domain modeling |

### Imputation Strategies

**Simple Imputation**:
- Mean/Median: fast, biased (reduces variance)
- Mode: for categorical features
- Constant: use a sentinel value (e.g., -1, "UNKNOWN")

**Model-Based Imputation**:
- **KNN Imputer**: impute from $k$ nearest neighbors' values
- **Iterative Imputer (MICE)**: multiple imputation by chained equations. Each feature is modeled as a function of other features iteratively
- **Matrix factorization**: for recommendation-style missing data

**Indicator Features**:
Add binary column $\text{is\_missing}_j$ to preserve missingness information:

$$
x_{\text{is\_missing},j} = \begin{cases} 1 & \text{if } x_j \text{ is missing} \\ 0 & \text{otherwise} \end{cases}
$$

This is often more valuable than the imputed value itself.

### Native Handling by Models

| Model | Handles Missing? | How |
|-------|-----------------|-----|
| XGBoost | Yes | Learns optimal default direction at each split |
| LightGBM | Yes | Groups NaN into a separate bin |
| CatBoost | Yes | Internal encoding for NaN |
| Linear models | No | Must impute |
| Neural nets | No | Must impute or use masking |

## Implementation

```python
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
import numpy as np

# Strategy: impute + indicator
def add_missing_indicators(X, cols):
    for col in cols:
        X[f"{col}_missing"] = X[col].isna().astype(int)
    return X

# Pipeline with KNN imputation
pipe = Pipeline([
    ("imputer", KNNImputer(n_neighbors=5, weights="distance")),
    ("model", model),
])

# For tree models: just pass NaN through
# XGBoost handles it natively
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Missingness as a feature | Any pipeline | Missing indicator often has predictive power |
| MNAR handling | Medical/financial data | Missingness itself is informative; model it explicitly |
| Test-time missing | Production deployment | Same imputation pipeline must work for new data |
| Multiple imputation | Statistical inference | Single imputation underestimates uncertainty; MICE is gold standard |

### Common Interview Questions
- [ ] How do you determine if data is MCAR, MAR, or MNAR?
- [ ] When would you drop rows vs. impute?
- [ ] Why add missing indicator columns?
- [ ] How does XGBoost handle missing values internally?
- [ ] Design a missing value strategy for a production recommendation system.

## Key Takeaways

- [ ] Always add missing indicator columns alongside imputation
- [ ] Tree models (XGBoost/LightGBM) handle missing values natively -- prefer them when data is sparse
- [ ] Mean imputation is simple but biases variance downward; use with indicator features
- [ ] MICE (iterative imputer) is the gold standard for statistical analysis
- [ ] Fit imputers on training data only; apply to test data (prevent leakage)
"""

CONTENT["pillar2.feature_engineering.feature_selection"] = r"""# Feature Selection

## Overview
Feature selection reduces dimensionality, prevents overfitting, improves interpretability, and speeds up training. Three main approaches: filter, wrapper, and embedded methods. Understanding when and how to apply each is essential for ML pipeline design interviews.

## Core Concepts

### Filter Methods
Score features independently of the model:

**Mutual Information**:

$$
I(X; Y) = \sum_{x,y} p(x,y) \log \frac{p(x,y)}{p(x)p(y)}
$$

Captures nonlinear dependencies. Works for both classification and regression.

**Correlation-based**: Pearson correlation for linear relationships. Remove features with $|r| > 0.95$ to address multicollinearity.

**Variance threshold**: remove near-constant features ($\text{Var}(X_j) < \epsilon$).

**Chi-squared test**: for categorical features vs. categorical target.

### Wrapper Methods
Use model performance to evaluate feature subsets:

- **Forward selection**: start empty, add best feature one at a time
- **Backward elimination**: start with all features, remove worst one at a time
- **Recursive Feature Elimination (RFE)**: train model, remove least important feature, repeat

Computationally expensive: $O(d)$ model trainings per step.

### Embedded Methods
Feature selection built into model training:

**L1 regularization (Lasso)**: drives coefficients to zero. Features with $w_j = 0$ are eliminated.

**Tree-based importance**:
- **Impurity-based**: sum of Gini/entropy reduction across all splits on feature $j$
- **Permutation importance**: measure accuracy drop when feature $j$ is shuffled

$$
\text{PI}_j = \text{score}_{\text{original}} - \text{score}_{\text{permuted}_j}
$$

**SHAP values**: theoretically grounded feature importance based on Shapley values from game theory:

$$
\phi_j = \sum_{S \subseteq F \setminus \{j\}} \frac{|S|!(|F|-|S|-1)!}{|F|!}[f(S \cup \{j\}) - f(S)]
$$

## Implementation

```python
from sklearn.feature_selection import (
    SelectKBest, mutual_info_classif, RFE
)
from sklearn.ensemble import RandomForestClassifier

# Filter: mutual information
selector = SelectKBest(mutual_info_classif, k=20)
X_selected = selector.fit_transform(X_train, y_train)

# Embedded: L1 with stability selection
from sklearn.linear_model import LogisticRegression
lr = LogisticRegression(penalty="l1", solver="saga", C=0.1)
lr.fit(X_train, y_train)
selected = [f for f, w in zip(features, lr.coef_[0]) if abs(w) > 0]

# SHAP
import shap
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Filter first, then model | Large feature space | Filter is cheap; removes obvious noise before expensive methods |
| Permutation vs. impurity importance | Tree models | Impurity importance is biased toward high-cardinality features |
| SHAP for production | Feature importance in deployment | SHAP is model-agnostic and theoretically sound |
| Feature selection pipeline | System design | Feature store should track feature importance over time |

### Common Interview Questions
- [ ] Compare filter, wrapper, and embedded methods.
- [ ] Why is impurity-based importance biased for high-cardinality features?
- [ ] How does L1 regularization perform feature selection?
- [ ] When would you use SHAP over permutation importance?
- [ ] Design a feature selection pipeline for a model with 10K features.

## Key Takeaways

- [ ] Filter methods (MI, correlation) are fast pre-screening tools
- [ ] L1/Lasso: embedded feature selection via sparsity
- [ ] Permutation importance > impurity importance (less biased)
- [ ] SHAP values: gold standard for feature importance, based on game theory
- [ ] In practice: combine multiple methods -- filter (cheap), embedded (training), SHAP (interpretation)
"""

# ===== SAMPLING & CLASS IMBALANCE =====

CONTENT["pillar2.sampling_class_imbalance.oversampling"] = r"""# Oversampling Techniques

## Overview
Class imbalance occurs when one class vastly outnumbers others (e.g., fraud detection: 0.1% positive). Oversampling creates synthetic minority examples to balance the training distribution. Understanding when and how to oversample is critical for real-world ML systems.

## Core Concepts

### Random Oversampling
Duplicate random minority class samples. Simple but risks overfitting to specific examples.

### SMOTE (Synthetic Minority Over-sampling Technique)
Generate synthetic samples by interpolating between minority class neighbors:

1. For minority sample $x_i$, find $k$ nearest minority neighbors
2. Pick a random neighbor $x_{nn}$
3. Create synthetic sample: $x_{\text{new}} = x_i + \lambda(x_{nn} - x_i)$, where $\lambda \sim U(0,1)$

**Variants**:

| Variant | Modification | When to Use |
|---------|-------------|-------------|
| SMOTE | Interpolate between neighbors | General purpose |
| Borderline-SMOTE | Only oversample borderline points | Noisy boundaries |
| ADASYN | More synthesis for harder examples | Adaptive difficulty |
| SMOTE-ENN | SMOTE + Edited Nearest Neighbors cleanup | Clean decision boundary |
| SMOTE-NC | Handles numerical + categorical | Mixed feature types |

### Important Rules

1. **Only oversample training data**: never apply to validation/test sets
2. **Oversample after splitting**: prevents data leakage
3. **Combine with undersampling**: SMOTE + random undersampling of majority often works best
4. **Consider alternatives first**: class weights, focal loss, threshold tuning

### When NOT to Oversample
- Tree models with native class weights (XGBoost `scale_pos_weight`)
- Very large datasets (undersampling majority may be better)
- When the minority class has very few examples ($< 10$) -- SMOTE fails

## Implementation

```python
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.combine import SMOTETomek
from imblearn.pipeline import Pipeline as ImbPipeline

# SMOTE in a pipeline (safe: only applies to training)
pipe = ImbPipeline([
    ("smote", SMOTE(sampling_strategy=0.5, k_neighbors=5)),
    ("model", XGBClassifier(scale_pos_weight=1)),
])
pipe.fit(X_train, y_train)
# Evaluation on original (imbalanced) test set
y_pred = pipe.predict(X_test)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| SMOTE placement | ML pipeline design | Must be inside CV loop, applied only to training folds |
| SMOTE + undersampling | Severe imbalance | Combine for best results (e.g., SMOTETomek) |
| Alternatives to oversampling | System design | Class weights, cost-sensitive learning, threshold tuning |
| Metric selection | Imbalanced evaluation | Use AUC-PR, F1, not accuracy |

### Common Interview Questions
- [ ] Explain SMOTE and how it generates synthetic samples.
- [ ] Why must oversampling happen after the train/test split?
- [ ] When would you prefer class weights over SMOTE?
- [ ] What are the limitations of SMOTE?
- [ ] Design a fraud detection pipeline handling 0.01% positive rate.

## Key Takeaways

- [ ] SMOTE: interpolate between minority neighbors -- the standard oversampling method
- [ ] Always oversample inside CV, never before splitting
- [ ] Class weights (e.g., `scale_pos_weight` in XGBoost) are simpler and often sufficient
- [ ] Combine SMOTE with undersampling (SMOTETomek, SMOTE-ENN) for cleaner boundaries
- [ ] Evaluate with AUC-PR or F1, never accuracy, on the original imbalanced test set
"""

CONTENT["pillar2.sampling_class_imbalance.loss_reweighting"] = r"""# Loss Reweighting

## Overview
Loss reweighting addresses class imbalance by assigning higher loss weights to minority class errors. Unlike oversampling, it doesn't create synthetic data -- it changes the optimization objective. Often simpler and more effective than resampling approaches.

## Core Concepts

### Inverse Frequency Weighting
Weight each class inversely proportional to its frequency:

$$
w_k = \frac{n}{K \cdot n_k}
$$

where $n$ = total samples, $K$ = number of classes, $n_k$ = samples in class $k$.

**Effective number weighting** (Cui et al., 2019):

$$
w_k = \frac{1 - \beta}{1 - \beta^{n_k}}, \quad \beta \in [0, 1)
$$

As $\beta \to 1$, approaches inverse frequency. $\beta = 0.999$ is common for long-tailed distributions.

### Weighted Loss Functions

**Weighted Cross-Entropy**:

$$
\mathcal{L} = -\frac{1}{n}\sum_i w_{y_i} \left[y_i \log \hat{p}_i + (1-y_i)\log(1-\hat{p}_i)\right]
$$

**Focal Loss** (Lin et al., 2017):

$$
\mathcal{L}_{\text{focal}} = -\alpha_t (1-p_t)^\gamma \log(p_t)
$$

$\gamma > 0$ down-weights easy examples; $\alpha_t$ balances class frequencies. Standard: $\gamma = 2, \alpha = 0.25$.

### Cost-Sensitive Learning
Asymmetric misclassification costs:

$$
\text{Expected Cost} = C_{FP} \cdot P(FP) + C_{FN} \cdot P(FN)
$$

Set class weight $= C_{FN}/C_{FP}$ for the positive class. Common in medical diagnosis (missing disease is worse than false alarm).

### Framework-Specific Implementation

| Framework | Parameter |
|-----------|-----------|
| sklearn | `class_weight="balanced"` or custom dict |
| XGBoost | `scale_pos_weight = n_neg / n_pos` |
| LightGBM | `is_unbalance=True` or `scale_pos_weight` |
| PyTorch | `weight` tensor in `nn.CrossEntropyLoss` |
| TensorFlow | `class_weight` dict in `model.fit()` |

## Implementation

```python
import torch
import torch.nn as nn
import numpy as np

# Inverse frequency weights
class_counts = np.bincount(y_train)
weights = 1.0 / class_counts
weights = weights / weights.sum() * len(class_counts)
loss_fn = nn.CrossEntropyLoss(
    weight=torch.tensor(weights, dtype=torch.float32)
)

# XGBoost
from xgboost import XGBClassifier
model = XGBClassifier(
    scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1])
)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Weights vs. oversampling | "How to handle imbalance?" | Weights: no extra data, no leakage risk. Oversampling: better for very few minority samples |
| Focal loss motivation | Object detection | Hard example mining without explicit sampling |
| Business cost alignment | "Cost of false negative?" | Map business costs to class weights |
| Calibration after reweighting | Probability estimates needed | Reweighting biases probabilities; recalibrate with Platt scaling |

### Common Interview Questions
- [ ] How does `scale_pos_weight` work in XGBoost?
- [ ] Compare class weights vs. SMOTE for handling imbalance.
- [ ] When would you use focal loss over weighted cross-entropy?
- [ ] How do class weights affect the decision boundary?
- [ ] After applying class weights, are the predicted probabilities calibrated?

## Key Takeaways

- [ ] Class weights are simpler than oversampling: no synthetic data, no leakage risk
- [ ] `scale_pos_weight = n_neg/n_pos` in XGBoost is the most common approach
- [ ] Focal loss: reduces loss for well-classified examples, superior for extreme imbalance
- [ ] Reweighting shifts the decision boundary but mis-calibrates probabilities -- recalibrate
- [ ] Cost-sensitive learning: align weights with business costs (FN vs. FP asymmetry)
"""

# ===== MODEL SELECTION & VALIDATION =====

CONTENT["pillar2.model_selection_validation.cross_validation"] = r"""# Cross-Validation

## Overview
Cross-validation (CV) estimates model generalization performance and is essential for hyperparameter tuning and model selection. Understanding CV strategies, their assumptions, and common pitfalls (data leakage) is fundamental for MLE interviews.

## Core Concepts

### K-Fold Cross-Validation
Split data into $K$ equal folds. Train on $K-1$ folds, validate on the remaining fold. Repeat $K$ times:

$$
\text{CV Score} = \frac{1}{K}\sum_{k=1}^{K} \text{Score}(f^{(-k)}, D_k)
$$

where $f^{(-k)}$ is the model trained without fold $k$, evaluated on fold $k$.

Standard: $K = 5$ or $K = 10$. Tradeoff: larger $K$ = less bias, more variance, more compute.

### Stratified K-Fold
Maintain class proportions in each fold. Essential for imbalanced datasets.

### Leave-One-Out (LOO)
$K = n$ (each sample is its own fold). Nearly unbiased but high variance and computationally expensive. Useful for very small datasets.

### Time Series CV
Data is ordered by time. Cannot use random splits (data leakage from future).

**Expanding Window**:

| Fold | Train | Test |
|------|-------|------|
| 1 | $[1, T_1]$ | $[T_1+1, T_2]$ |
| 2 | $[1, T_2]$ | $[T_2+1, T_3]$ |
| 3 | $[1, T_3]$ | $[T_3+1, T_4]$ |

**Sliding Window**: fixed-size training window. Better when older data is less relevant.

### Group K-Fold
When samples are grouped (e.g., multiple samples per user). Ensures all samples from a group are in the same fold. Prevents information leakage from the same entity appearing in both train and test.

### Nested Cross-Validation
Outer loop: estimate generalization. Inner loop: tune hyperparameters.

```
Outer fold 1: [Train: inner CV for HP tuning] -> [Test: evaluate best HP]
Outer fold 2: [Train: inner CV for HP tuning] -> [Test: evaluate best HP]
...
```

Prevents optimistic bias from tuning on the same data used for evaluation.

## Implementation

```python
from sklearn.model_selection import (
    StratifiedKFold, TimeSeriesSplit, GroupKFold, cross_val_score
)

# Stratified K-Fold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=skf, scoring="roc_auc")
print(f"AUC: {scores.mean():.3f} +/- {scores.std():.3f}")

# Time Series Split
tscv = TimeSeriesSplit(n_splits=5, gap=7)  # 7-day gap
for train_idx, test_idx in tscv.split(X):
    model.fit(X[train_idx], y[train_idx])
    score = model.score(X[test_idx], y[test_idx])

# Group K-Fold (e.g., by user_id)
gkf = GroupKFold(n_splits=5)
scores = cross_val_score(model, X, y, cv=gkf, groups=user_ids)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| CV strategy selection | "How to evaluate?" | Random: Stratified K-Fold. Time: TimeSeriesSplit. Groups: GroupKFold |
| Data leakage in CV | Feature engineering | Preprocessing must be inside CV loop (fit on train fold only) |
| Nested CV | Model comparison | Outer loop evaluates, inner loop tunes -- prevents overfitting to CV |
| CV vs. holdout | Small vs. large data | CV for small data (reliable estimate); holdout for large data (faster) |

### Common Interview Questions
- [ ] Why is stratified K-fold important for imbalanced data?
- [ ] How does data leakage occur in cross-validation?
- [ ] When must you use time series CV instead of random CV?
- [ ] What is the difference between K-fold and nested CV?
- [ ] How do you choose between 5-fold and 10-fold CV?

## Key Takeaways

- [ ] K-Fold: standard for i.i.d. data. Use Stratified for classification
- [ ] Time series: must use temporal splits -- never random
- [ ] Group K-Fold: when data has natural groups (users, sessions, patients)
- [ ] All preprocessing must be inside the CV loop to prevent leakage
- [ ] Nested CV for unbiased evaluation when also tuning hyperparameters
"""

CONTENT["pillar2.model_selection_validation.hyperparameter_tuning"] = r"""# Hyperparameter Tuning

## Overview
Hyperparameter tuning optimizes the parameters not learned during training (learning rate, regularization strength, tree depth). Efficient tuning strategies can mean the difference between a mediocre and a strong model. Interviews test understanding of search strategies and their tradeoffs.

## Core Concepts

### Grid Search
Exhaustively evaluate all combinations. Guaranteed to find best in grid but exponential cost: $O(p^d)$ for $p$ values per $d$ hyperparameters.

### Random Search (Bergstra & Bengio, 2012)
Sample hyperparameter combinations randomly. More efficient than grid search:

**Key insight**: most objectives depend on only a few hyperparameters. Random search explores the important dimensions more thoroughly than grid search for the same budget.

With $n$ random trials and $d$ hyperparameters, if only $d_{\text{eff}}$ matter:
- Random search: effectively $n^{d/d_{\text{eff}}}$ evaluations in important dimensions
- Grid search: only $n^{1/d}$ evaluations per dimension

### Bayesian Optimization
Build a surrogate model (typically Gaussian Process or TPE) of the objective function:

1. Fit surrogate to observed $(x, y)$ pairs
2. Select next $x$ by maximizing acquisition function (Expected Improvement, UCB)
3. Evaluate true objective at $x$
4. Update surrogate and repeat

**Expected Improvement**:

$$
\text{EI}(x) = E[\max(0, f(x) - f(x^*))]
$$

Balances exploration (uncertain regions) and exploitation (promising regions).

### Hyperband / ASHA
Multi-fidelity methods: train many configurations for few epochs, promote promising ones:

1. Start $n$ random configurations with budget $b_{\min}$
2. Evaluate, keep top $1/\eta$ fraction
3. Increase budget by $\eta$, repeat until $b_{\max}$

Much faster than full training for each configuration. Successive Halving is the core primitive.

### Key Hyperparameters by Model

| Model | Critical HPs | Search Range |
|-------|-------------|-------------|
| XGBoost | `max_depth`, `learning_rate`, `n_estimators` | [3-10], [0.01-0.3], [100-1000] |
| Neural Net | `lr`, `batch_size`, `dropout`, `hidden_dim` | [1e-5-1e-2], [16-512], [0.1-0.5], [64-1024] |
| SVM | `C`, `gamma` | [1e-3-1e3], [1e-4-1e1] |
| Random Forest | `n_estimators`, `max_depth`, `min_samples_leaf` | [100-1000], [5-30], [1-20] |

## Implementation

```python
import optuna

# Optuna with Bayesian optimization (TPE)
def objective(trial):
    params = {
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("lr", 1e-3, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample", 0.6, 1.0),
        "reg_lambda": trial.suggest_float("lambda", 1e-3, 10, log=True),
    }
    model = XGBClassifier(**params, n_estimators=500, early_stopping_rounds=50)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    return model.best_score

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Random > Grid | Any tuning | Random search is provably more efficient for most problems |
| Bayesian for expensive evals | Deep learning, large datasets | Each eval is costly; Bayesian uses info from prior evals |
| Early stopping as HP | Tree boosting | `n_estimators` via early stopping, not grid search |
| Log-scale search | LR, regularization | Log-uniform sampling: `lr ~ 10^U(-4, -1)` |

### Common Interview Questions
- [ ] Why is random search often better than grid search?
- [ ] Explain Bayesian optimization and the acquisition function.
- [ ] How does Hyperband achieve efficiency?
- [ ] What hyperparameters would you tune first for XGBoost?
- [ ] How do you avoid overfitting during hyperparameter tuning?

## Key Takeaways

- [ ] Random search > grid search: better coverage of important dimensions
- [ ] Bayesian optimization (Optuna/TPE): best for expensive evaluations
- [ ] Hyperband/ASHA: multi-fidelity methods for fast initial screening
- [ ] Search on log scale for learning rate and regularization
- [ ] Use nested CV to prevent overfitting to the tuning set
"""

CONTENT["pillar2.model_selection_validation.calibration"] = r"""# Model Calibration

## Overview
A well-calibrated model outputs probabilities that reflect true likelihoods: if it predicts 80% probability, the event should occur ~80% of the time. Calibration is critical when probabilities drive downstream decisions (ad bidding, medical diagnosis, risk scoring).

## Core Concepts

### What is Calibration?
A model $\hat{p}$ is calibrated if:

$$
P(Y=1 | \hat{p}(X) = p) = p, \quad \forall p \in [0,1]
$$

**Reliability diagram**: plot predicted probabilities (x-axis) vs. observed frequencies (y-axis). Perfect calibration = diagonal line.

### Calibration Metrics

**Expected Calibration Error (ECE)**:

$$
\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{n} |acc(B_b) - \text{conf}(B_b)|
$$

Partition predictions into $B$ bins; compare average confidence vs. accuracy per bin.

**Brier Score** (proper scoring rule):

$$
\text{BS} = \frac{1}{n}\sum_{i=1}^{n}(\hat{p}_i - y_i)^2
$$

Decomposes into: reliability (calibration) + resolution (discrimination) + uncertainty.

### Calibration Methods

**Platt Scaling** (parametric):
Fit a logistic regression on model outputs:

$$
\hat{p}_{\text{cal}} = \sigma(a \cdot f(x) + b)
$$

Learn $a, b$ on a held-out calibration set. Works well for sigmoid-shaped miscalibration.

**Isotonic Regression** (non-parametric):
Fit a non-decreasing step function mapping model scores to calibrated probabilities. More flexible but needs more calibration data.

**Temperature Scaling** (neural nets):
Single parameter $T > 0$:

$$
\hat{p}_{\text{cal}} = \text{softmax}(z/T)
$$

$T > 1$: soften predictions (reduce overconfidence). Optimal $T$ found on validation set.

### Which Models Need Calibration?

| Model | Calibration Quality | Fix |
|-------|-------------------|-----|
| Logistic Regression | Good (natively calibrated) | Usually none |
| Random Forest | Poor (peaked at 0 and 1) | Platt or Isotonic |
| Gradient Boosted Trees | Moderate | Platt scaling |
| Neural Networks | Poor (overconfident) | Temperature scaling |
| SVM | N/A (not probabilistic) | Platt scaling |

## Implementation

```python
from sklearn.calibration import (
    CalibratedClassifierCV, calibration_curve
)
import matplotlib.pyplot as plt

# Platt scaling (sigmoid)
calibrated = CalibratedClassifierCV(
    base_estimator=model, method="sigmoid", cv=5
)
calibrated.fit(X_train, y_train)

# Reliability diagram
prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
plt.plot(prob_pred, prob_true, marker="o")
plt.plot([0, 1], [0, 1], "--")
plt.xlabel("Mean predicted probability")
plt.ylabel("Fraction of positives")
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Calibration for bidding | Ad systems | Predicted probability directly determines bid price |
| Temperature scaling | Deep learning | Single parameter, preserves ranking, simple to implement |
| Post-hoc vs. during training | System design | Post-hoc (Platt/Isotonic) is standard; training-time (mixup, label smoothing) helps too |
| Calibration vs. discrimination | "What metric?" | AUC measures discrimination; ECE measures calibration. Both needed |

### Common Interview Questions
- [ ] What does it mean for a model to be well-calibrated?
- [ ] Why are Random Forests poorly calibrated?
- [ ] Compare Platt scaling vs. isotonic regression.
- [ ] When is calibration more important than discrimination?
- [ ] How would you calibrate a model in a production ad system?

## Key Takeaways

- [ ] Calibration = predicted probabilities match observed frequencies
- [ ] ECE and reliability diagrams are the primary calibration diagnostics
- [ ] Platt scaling: parametric (2 params), good for smooth miscalibration
- [ ] Isotonic regression: non-parametric, flexible, needs more data
- [ ] Temperature scaling: standard for neural nets, single parameter $T$
"""

# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

def main() -> None:
    """Populate Pillar 2 leaf nodes with content."""
    engine = get_engine()
    SessionLocal.configure(bind=engine)

    with SessionLocal() as db:
        updated = 0
        missing = []

        for path, content in CONTENT.items():
            node = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if node is None:
                missing.append(path)
                continue

            node.description = content.strip()
            updated += 1

        db.commit()

    print(f"Updated {updated} framework nodes.")
    if missing:
        print(f"WARNING: {len(missing)} paths not found: {missing}")
    print("Done.")


if __name__ == "__main__":
    main()
