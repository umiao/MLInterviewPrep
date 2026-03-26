# Ensemble Methods: Random Forest and Gradient Boosting

## Overview

Ensemble methods combine multiple weak learners to produce a stronger model. The two dominant paradigms -- bagging (variance reduction via parallel independent models) and boosting (bias reduction via sequential dependent models) -- underpin the most successful tabular ML algorithms: Random Forest, GBDT, XGBoost, and LightGBM. These are among the most frequently asked topics in MLE interviews, both for conceptual understanding and practical trade-off analysis.

## Core Concepts

### Bagging vs Boosting

The two fundamental ensemble strategies differ in how they combine weak learners:

**Bagging** (Bootstrap Aggregating):
1. Sample $k$ training sets from data via bootstrap (sampling with replacement)
2. Train $k$ independent models in parallel (each model has equal weight)
3. Aggregate predictions: majority vote (classification) or average (regression)

**Boosting**:
1. Train weak learners sequentially; each focuses on errors of the previous ensemble
2. Adjust sample weights or fit residuals at each round
3. Combine with weighted sum (learners with lower error get higher weight)

| Aspect | Bagging | Boosting |
|--------|---------|----------|
| Sample selection | Bootstrap (with replacement), independent sets | Same data, but sample weights change per round |
| Model weights | Equal for all learners | Weighted by accuracy |
| Training order | Parallel (independent) | Sequential (dependent) |
| Bias-variance effect | Reduces variance | Reduces bias |
| Overfitting risk | Low (averaging smooths) | Higher (can overfit noise) |
| Representative | Random Forest | GBDT, XGBoost, LightGBM |

### Decision Tree Splits

Trees partition feature space by selecting the split that maximizes a purity criterion:

**Information Gain** (used by ID3/C4.5):

$$
\text{IG}(D, A) = H(D) - \sum_{v \in \text{Values}(A)} \frac{|D_v|}{|D|} H(D_v)
$$

where $H(D) = -\sum_k p_k \log_2 p_k$ is the entropy.

**Gini Impurity** (used by CART, default in sklearn):

$$
\text{Gini}(D) = 1 - \sum_{k=1}^{K} p_k^2
$$

A split is chosen to maximize the decrease in Gini impurity (or equivalently, maximize information gain).

**Key interview point:** A single decision tree has high variance -- small data perturbations cause large structural changes. This instability is a feature for ensembles: diverse trees produce better aggregates.

### Random Forest

Random Forest = Bagging + Decision Trees + Random Feature Selection.

**Algorithm:**
1. Draw $k$ bootstrap samples from the training set
2. For each sample, grow a decision tree. At each node, randomly select $m$ features from $M$ total ($m \ll M$, typically $m = \sqrt{M}$ for classification, $m = M/3$ for regression)
3. Choose the best split among the $m$ features
4. Grow trees fully (no pruning typically needed)
5. Aggregate: majority vote or mean prediction

**Why random feature selection helps:** Without it, all trees would split on the same dominant features and be correlated. Random subsets decorrelate the trees, so averaging actually reduces variance. This is the key insight beyond basic bagging.

**Feature importance:** Measured by mean decrease in impurity (MDI) across all splits using that feature, or permutation importance (shuffle feature values, measure accuracy drop).

**Advantages:**
- Handles high-dimensional data without feature selection
- Naturally resistant to overfitting (averaging reduces variance)
- Provides feature importance rankings
- Highly parallelizable
- Robust to missing data and class imbalance

**Disadvantages:**
- Biased toward features with more unique values (more split options)
- Can overfit on noisy regression tasks
- Less interpretable than a single tree

### Gradient Boosting (GBM/GBDT)

GBM performs gradient descent in function space rather than parameter space. Each new weak learner fits the negative gradient of the loss function with respect to the current ensemble's predictions.

**Core idea:** Given cumulative model $F_{k-1}(x)$ after round $k-1$:

$$
F_k(x) = F_{k-1}(x) + \alpha \cdot h_k(x)
$$

where $h_k(x)$ is the new tree that fits the negative gradient:

$$
h_k(x_i) \approx -\frac{\partial L(y_i, \hat{y})}{\partial F_{k-1}(x_i)}
$$

and $\alpha$ is the learning rate (shrinkage).

**Regression example** ($L = (y - \hat{y})^2$):
- Negative gradient: $y_i - F_{k-1}(x_i)$ (the residual)
- Each tree literally fits the residuals of the previous ensemble

**Classification example** ($L$ = cross-entropy):
- Model predicts log-odds: $F_{k-1}(x) = \log\frac{p}{1-p}$
- Probability: $p_{k-1} = \frac{1}{1 + e^{-F_{k-1}}}$ (sigmoid)
- Negative gradient: $y_i - p_{k-1}(x_i)$ (observed minus predicted probability)

**Key difference from parameter-space gradient descent:**
- Parameter space: use gradient to update model weights
- Function space: use gradient to fit an entirely new function (tree)

### XGBoost

XGBoost (eXtreme Gradient Boosting) improves on GBM with three key innovations:

**1. Second-order Taylor expansion:**

The objective at round $t$:

$$
\mathcal{L}^{(t)} = \sum_{i=1}^n \left[ g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i) \right] + \Omega(f_t)
$$

where $g_i = \frac{\partial L}{\partial \hat{y}_i^{(t-1)}}$ (first derivative) and $h_i = \frac{\partial^2 L}{\partial (\hat{y}_i^{(t-1)})^2}$ (second derivative). Using the Hessian enables better approximation of arbitrary loss functions and faster convergence.

**2. Regularization:**

$$
\Omega(f_t) = \gamma T + \frac{1}{2} \lambda \sum_{j=1}^{T} \omega_j^2
$$

where $T$ = number of leaf nodes and $\omega_j$ = leaf weights. $\gamma$ penalizes tree complexity (number of leaves); $\lambda$ applies L2 regularization on leaf weights.

**3. Optimal leaf weight:**

For leaf node $j$, grouping samples by their assigned leaf ($I_j$), define $G_j = \sum_{i \in I_j} g_i$ and $H_j = \sum_{i \in I_j} h_i$. The closed-form optimal weight is:

$$
\omega_j^* = -\frac{G_j}{H_j + \lambda}
$$

and the corresponding minimum loss:

$$
\mathcal{L}^* = -\frac{1}{2} \sum_{j=1}^{T} \frac{G_j^2}{H_j + \lambda} + \gamma T
$$

**Split gain** for a candidate split: compare loss before and after splitting. A split is accepted only if the gain exceeds $\gamma$ (built-in pruning).

**Block processing:** XGBoost stores pre-sorted feature columns in compressed column (CSC) blocks for parallel split-finding across features.

### LightGBM

LightGBM targets efficiency on large datasets through four innovations:

**1. Leaf-wise growth** (vs level-wise):
- Most GBDT (including XGBoost default) grows level-wise: split all leaves at the same depth
- LightGBM grows leaf-wise: always splits the leaf with the highest gain
- Result: better accuracy with fewer splits, but risk of overfitting (controlled by `max_depth`)

**2. Histogram binning:**
- Discretize continuous features into $k$ bins (default 255), stored as `uint8`
- Reduces candidate split points from $O(n_\text{unique})$ to $O(k)$
- Memory: `float32` per value becomes `uint8` per value
- Trade-off: slight accuracy loss, but acts as regularization; much faster
- Histogram subtraction trick: one child's histogram = parent histogram - sibling histogram (saves half the computation)

**3. GOSS (Gradient-based One-Side Sampling):**
- Samples with small gradients are already well-trained
- Keep all samples with top-$a\%$ largest gradients; randomly sample $b\%$ from the rest
- Multiply the small-gradient samples by $\frac{1-a}{b}$ to maintain distribution
- Reduces data size while preserving information gain accuracy

**4. EFB (Exclusive Feature Bundling):**
- In sparse high-dimensional data, many features are mutually exclusive (rarely non-zero simultaneously)
- Bundle exclusive features into one feature (different value ranges per original feature via offset)
- Finding optimal bundles is NP-hard; reduced to graph coloring (features = vertices, edges = non-exclusive pairs)
- Heuristic: sort by degree, greedily assign to bundles with acceptable conflict ratio

**Categorical feature handling:**
- One-hot encoding is bad for trees: forces one-vs-rest splits with tiny gain
- LightGBM uses many-to-many splits (e.g., "is dog OR cat" vs rest)
- Sort categories by label mean, then search for optimal split point along the sorted order

**Practical note:** LightGBM is sensitive to overfitting on small datasets (< 10K samples).

## Implementation

```python
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# Random Forest
rf = RandomForestClassifier(
    n_estimators=100,
    max_features="sqrt",  # m = sqrt(M) for classification
    oob_score=True,        # out-of-bag estimate (free validation)
)
rf.fit(X_train, y_train)
importances = rf.feature_importances_  # mean decrease in impurity

# Gradient Boosting (sklearn)
gb = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=3,           # shallow trees for boosting
    subsample=0.8,         # stochastic gradient boosting
)

# XGBoost
xgb = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    reg_alpha=0.1,         # L1 regularization
    reg_lambda=1.0,        # L2 regularization (lambda)
    gamma=0.1,             # min split gain (gamma)
    tree_method="hist",    # histogram-based (faster)
)

# LightGBM
lgbm = LGBMClassifier(
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=31,         # leaf-wise control (not max_depth)
    min_child_samples=20,  # prevent overfitting on small leaves
    feature_fraction=0.8,  # column subsampling
    bagging_fraction=0.8,  # row subsampling
    verbose=-1,
)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Bagging vs boosting | Asked to compare ensemble strategies | Bagging reduces variance (parallel, equal weight); boosting reduces bias (sequential, adaptive) |
| RF feature selection | Why does random feature selection help? | Decorrelates trees so averaging actually reduces variance; without it, all trees look similar |
| GBM intuition | What is gradient boosting doing? | Gradient descent in function space: each tree fits the negative gradient (residuals) of the loss |
| XGBoost advantages | Why XGBoost over plain GBM? | 2nd-order Taylor (better loss approx + faster convergence), built-in regularization, parallel block processing |
| LightGBM speed | Why is LightGBM faster? | Histogram binning (uint8 vs float32), leaf-wise growth (fewer splits for same accuracy), GOSS + EFB |
| XGB vs LGBM choice | When to use which? | XGBoost: smaller data, need full control; LightGBM: large data (>10K), high-dimensional, speed-critical |
| Overfitting control | How to prevent boosting from overfitting? | Learning rate shrinkage, early stopping, max_depth, regularization (gamma, lambda), subsampling |

### Common Interview Questions

- [ ] Bagging vs boosting: explain the core difference in terms of bias-variance
- [ ] Why does random feature selection help Random Forest beyond basic bagging?
- [ ] What is gradient boosting doing mathematically? (function space gradient descent)
- [ ] How does XGBoost regularize compared to plain GBM?
- [ ] XGBoost vs LightGBM: when would you choose one over the other?
- [ ] Why is LightGBM faster than XGBoost? (name at least 3 reasons)
- [ ] How do you tune a gradient boosting model to prevent overfitting?

## Comparisons

### Bagging vs Boosting

| Aspect | Bagging (Random Forest) | Boosting (GBM/XGB/LGBM) |
|--------|------------------------|--------------------------|
| Training | Parallel, independent | Sequential, dependent |
| Sample usage | Bootstrap (with replacement) | Weighted or full data |
| Model weights | Equal | Weighted by accuracy |
| Primary effect | Reduces variance | Reduces bias |
| Overfitting risk | Low | Higher (without regularization) |
| Speed | Highly parallelizable | Inherently sequential |

### GBM vs XGBoost vs LightGBM

| Aspect | GBM (sklearn) | XGBoost | LightGBM |
|--------|---------------|---------|----------|
| Loss approximation | 1st-order gradient | 2nd-order Taylor (g + h) | 2nd-order Taylor |
| Regularization | None built-in | $\gamma T + \frac{\lambda}{2}\sum\omega_j^2$ | Similar + GOSS sampling |
| Tree growth | Level-wise | Level-wise (default) | Leaf-wise |
| Split finding | Exact | Pre-sorted blocks | Histogram binning (255 bins) |
| Memory per feature | float32 | float32 (sorted) | uint8 (binned) |
| Categorical features | Needs encoding | Needs encoding | Native many-to-many splits |
| Sparse data | No special handling | Sparse-aware | EFB (exclusive feature bundling) |
| Best for | Small data, baselines | Medium data, competitions | Large data, production |

### When to Use What

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quick baseline, interpretable | Random Forest | No tuning needed, OOB score, feature importance |
| Small dataset (< 10K) | XGBoost or RF | LightGBM overfits on small data |
| Large dataset (> 100K) | LightGBM | Histogram binning + GOSS = fast |
| High-dimensional sparse | LightGBM | EFB bundles exclusive features |
| Competition / max accuracy | XGBoost or LightGBM | Tune both, pick winner |
| Need for probability calibration | Any + Platt scaling | Boosted trees often poorly calibrated |

## Key Takeaways

- [ ] Bagging reduces variance by averaging independent models; boosting reduces bias by sequentially correcting errors
- [ ] Random Forest key insight: random feature subset at each split decorrelates trees, making the average more effective
- [ ] GBM performs gradient descent in function space: each tree fits $-\frac{\partial L}{\partial F_{k-1}(x)}$, the negative gradient of the loss
- [ ] XGBoost uses 2nd-order Taylor expansion ($g_i$ and $h_i$) for better loss approximation; optimal leaf weight is $\omega_j^* = -G_j / (H_j + \lambda)$
- [ ] XGBoost regularization: $\Omega(f) = \gamma T + \frac{\lambda}{2}\sum\omega_j^2$ penalizes both tree complexity and leaf magnitudes
- [ ] LightGBM leaf-wise growth splits the highest-gain leaf first, achieving better accuracy per split but risking overfitting
- [ ] LightGBM histogram binning: float32 to uint8, reduces split candidates from $O(n)$ to $O(255)$, acts as implicit regularization
- [ ] GOSS keeps high-gradient samples (under-trained) and subsamples low-gradient ones; EFB bundles mutually exclusive sparse features via graph coloring
