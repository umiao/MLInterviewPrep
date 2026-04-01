# Uber BPS -- KNN From Scratch + ML Fundamentals Review

> **Purpose**: Recruiter explicitly mentions KNN and ML fundamentals as BPS evaluation
> topics. This document covers KNN implementation from scratch and core ML concepts
> likely tested in the ~5min ML fundamentals segment.
>
> Task: T-P1-246

---

## Table of Contents

1. [KNN From Scratch (Python)](#1-knn-from-scratch-python)
2. [Distance Metrics](#2-distance-metrics)
3. [Choosing k](#3-choosing-k)
4. [Weighted KNN](#4-weighted-knn)
5. [Classification vs Regression](#5-classification-vs-regression)
6. [Optimization: KD-Tree, Ball Tree, LSH](#6-optimization-kd-tree-ball-tree-lsh)
7. [KNN Interview Questions](#7-knn-interview-questions)
8. [ML Fundamentals: Bias-Variance Tradeoff](#8-ml-fundamentals-bias-variance-tradeoff)
9. [ML Fundamentals: Overfitting and Regularization](#9-ml-fundamentals-overfitting-and-regularization)
10. [ML Fundamentals: Cross-Validation](#10-ml-fundamentals-cross-validation)
11. [ML Fundamentals: Evaluation Metrics](#11-ml-fundamentals-evaluation-metrics)
12. [ML Fundamentals: Feature Engineering](#12-ml-fundamentals-feature-engineering)
13. [Quick-Fire Q&A Cheat Sheet](#13-quick-fire-qa-cheat-sheet)

---

## 1. KNN From Scratch (Python)

### 1.1 Core Implementation

```python
import numpy as np
from collections import Counter
from typing import Optional


class KNN:
    """K-Nearest Neighbors classifier/regressor from scratch."""

    def __init__(
        self,
        k: int = 5,
        metric: str = "euclidean",
        task: str = "classification",
        weighted: bool = False,
    ):
        self.k = k
        self.metric = metric
        self.task = task  # "classification" or "regression"
        self.weighted = weighted
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "KNN":
        """Store training data. KNN is a lazy learner -- no model is built."""
        self.X_train = np.array(X, dtype=float)
        self.y_train = np.array(y)
        return self

    def _compute_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Compute distance between two points."""
        if self.metric == "euclidean":
            return np.sqrt(np.sum((x1 - x2) ** 2))
        elif self.metric == "manhattan":
            return np.sum(np.abs(x1 - x2))
        elif self.metric == "cosine":
            dot = np.dot(x1, x2)
            norm = np.linalg.norm(x1) * np.linalg.norm(x2)
            if norm == 0:
                return 1.0
            return 1.0 - dot / norm
        elif self.metric == "minkowski":
            p = 3  # generalized; euclidean=2, manhattan=1
            return np.sum(np.abs(x1 - x2) ** p) ** (1.0 / p)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")

    def _get_neighbors(self, x: np.ndarray) -> tuple:
        """Return indices and distances of k nearest neighbors."""
        distances = np.array([
            self._compute_distance(x, x_train) for x_train in self.X_train
        ])
        k_indices = np.argsort(distances)[: self.k]
        k_distances = distances[k_indices]
        return k_indices, k_distances

    def _predict_single(self, x: np.ndarray):
        """Predict for a single sample."""
        k_indices, k_distances = self._get_neighbors(x)
        k_labels = self.y_train[k_indices]

        if self.task == "classification":
            if self.weighted:
                # Inverse distance weighting
                weights = 1.0 / (k_distances + 1e-8)
                vote_counts: dict = {}
                for label, w in zip(k_labels, weights):
                    vote_counts[label] = vote_counts.get(label, 0) + w
                return max(vote_counts, key=vote_counts.get)
            else:
                # Majority vote
                counter = Counter(k_labels)
                return counter.most_common(1)[0][0]
        else:  # regression
            if self.weighted:
                weights = 1.0 / (k_distances + 1e-8)
                return np.average(k_labels.astype(float), weights=weights)
            else:
                return np.mean(k_labels.astype(float))

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict for multiple samples."""
        X = np.array(X, dtype=float)
        return np.array([self._predict_single(x) for x in X])

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Accuracy (classification) or R^2 (regression)."""
        predictions = self.predict(X)
        if self.task == "classification":
            return np.mean(predictions == y)
        else:
            y = np.array(y, dtype=float)
            ss_res = np.sum((y - predictions) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
```

### 1.2 Usage Example

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = KNN(k=5, metric="euclidean", task="classification", weighted=True)
model.fit(X_train, y_train)
print(f"Accuracy: {model.score(X_test, y_test):.3f}")
```

### 1.3 Key Properties of KNN

| Property | Value |
|----------|-------|
| Type | Instance-based / lazy learner |
| Training cost | O(1) -- just stores data |
| Prediction cost | O(n*d) per query (brute force) |
| Memory | O(n*d) -- stores all training data |
| Parametric? | No -- decision boundary shaped by data |
| Handles nonlinear? | Yes -- naturally captures complex boundaries |

---

## 2. Distance Metrics

### 2.1 Common Metrics

| Metric | Formula | When to Use |
|--------|---------|-------------|
| **Euclidean (L2)** | sqrt(sum((x_i - y_i)^2)) | Default for continuous features, same scale |
| **Manhattan (L1)** | sum(\|x_i - y_i\|) | High-dimensional data, sparse features, robust to outliers |
| **Cosine** | 1 - (x . y) / (\|\|x\|\| * \|\|y\|\|) | Text/NLP (TF-IDF vectors), when magnitude irrelevant |
| **Minkowski (Lp)** | (sum(\|x_i - y_i\|^p))^(1/p) | Generalized; p=1 is Manhattan, p=2 is Euclidean |
| **Hamming** | fraction of differing coordinates | Categorical/binary features |

### 2.2 Feature Scaling is Critical

KNN is distance-based, so features with larger scales dominate. **Always normalize.**

```python
# StandardScaler: zero mean, unit variance
X_scaled = (X - X.mean(axis=0)) / X.std(axis=0)

# MinMaxScaler: [0, 1] range
X_scaled = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
```

**Interview answer**: "KNN computes distances, so features on different scales will
bias the distance computation. A feature ranging 0-1000 would dominate over one ranging
0-1. I would apply StandardScaler or MinMaxScaler before fitting KNN."

---

## 3. Choosing k

### 3.1 Effect of k

| Small k (e.g., 1-3) | Large k (e.g., 50+) |
|---------------------|---------------------|
| Low bias, high variance | High bias, low variance |
| Sensitive to noise/outliers | Smoother decision boundaries |
| Risk: overfitting | Risk: underfitting |
| Captures local patterns | Averages over global trends |

### 3.2 How to Select k

1. **Cross-validation**: Try k = 1, 3, 5, 7, ..., sqrt(n). Pick k with best CV score.
2. **Rule of thumb**: k = sqrt(n) is a common starting point.
3. **Odd k for binary classification**: Avoids ties in majority voting.
4. **Elbow method**: Plot accuracy vs k, pick the "elbow" where improvement plateaus.

```python
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

best_k, best_score = 1, 0
for k in range(1, 30, 2):
    scores = cross_val_score(
        KNeighborsClassifier(n_neighbors=k), X_train, y_train, cv=5
    )
    if scores.mean() > best_score:
        best_k, best_score = k, scores.mean()
```

---

## 4. Weighted KNN

### 4.1 Why Weight?

Standard KNN gives equal vote to all k neighbors. But a neighbor at distance 0.1
should count more than one at distance 10.

### 4.2 Weighting Schemes

| Scheme | Weight Formula | Pros |
|--------|---------------|------|
| **Uniform** | w_i = 1 | Simple, works when data is dense |
| **Inverse distance** | w_i = 1 / d_i | Closer neighbors dominate |
| **Gaussian kernel** | w_i = exp(-d_i^2 / (2 * sigma^2)) | Smooth falloff, tunable bandwidth |

### 4.3 When Weighted KNN Helps

- **Skewed class distribution**: Minority class neighbors get fair weight when close
- **Overlapping boundaries**: Reduces misclassification in transition zones
- **Noisy data**: Distant noisy points contribute less

---

## 5. Classification vs Regression

### 5.1 KNN for Classification

- **Output**: Most common label among k neighbors (majority vote)
- **Ties**: Break by distance (closest neighbor wins) or random
- **Probabilistic**: P(class=c) = count(class=c in neighbors) / k

### 5.2 KNN for Regression

- **Output**: Mean (or weighted mean) of k neighbors' values
- **Variant**: Median of neighbors (robust to outliers)

### 5.3 Comparison Table

| Aspect | Classification | Regression |
|--------|---------------|------------|
| Output | Discrete label | Continuous value |
| Aggregation | Majority vote | Mean / weighted mean |
| Metric | Accuracy, F1 | MSE, R^2 |
| Weighting benefit | Reduces tie ambiguity | Smooths predictions |

---

## 6. Optimization: KD-Tree, Ball Tree, LSH

### 6.1 Why Optimize?

Brute-force KNN is O(n*d) per query. For n=1M, d=100, that is too slow.

### 6.2 KD-Tree

```
Build: recursively split data along the dimension with highest variance.
       Each node stores split dimension + split value.
Query: traverse tree, prune branches whose bounding box is farther
       than current k-th nearest distance.
```

| Property | Value |
|----------|-------|
| Build time | O(n log n) |
| Query time | O(log n) average, O(n) worst case |
| Best for | Low dimensions (d < 20) |
| Fails when | High-d: all dimensions roughly equidistant, no pruning possible |

### 6.3 Ball Tree

```
Build: recursively partition data into hyperspheres (balls).
       Each node stores center + radius.
Query: prune balls whose closest point is farther than k-th nearest.
```

| Property | Value |
|----------|-------|
| Build time | O(n log n) |
| Query time | O(log n) average |
| Best for | Moderate dimensions (d < 100), non-Euclidean metrics |
| Advantage over KD-Tree | Works with arbitrary metrics, better in higher d |

### 6.4 Locality-Sensitive Hashing (LSH)

```
Idea: hash similar points to the same bucket with high probability.
      Multiple hash tables + hash functions reduce false negatives.
      Query: hash the query point, search only within its bucket(s).
```

| Property | Value |
|----------|-------|
| Build time | O(n * L) where L = number of hash tables |
| Query time | O(L) amortized -- sub-linear |
| Best for | Very high dimensions (d > 100), approximate NN |
| Tradeoff | Approximate -- may miss true nearest neighbors |
| Used at Uber? | Yes -- matching drivers to riders uses spatial hashing |

### 6.5 Comparison

| Method | Exact? | Best d range | Query complexity |
|--------|--------|-------------|-----------------|
| Brute force | Yes | Any | O(n*d) |
| KD-Tree | Yes | d < 20 | O(log n) avg |
| Ball Tree | Yes | d < 100 | O(log n) avg |
| LSH | Approximate | d > 100 | Sub-linear |
| FAISS (Facebook) | Approximate | Any | Sub-linear (GPU) |

---

## 7. KNN Interview Questions

### Q1: What is the curse of dimensionality and how does it affect KNN?

**Answer**: In high dimensions, all points become approximately equidistant. The
ratio (max_distance - min_distance) / min_distance approaches 0 as dimensions grow.
This means KNN cannot distinguish meaningful neighbors from random points.

**Consequences for KNN**:
- Distance-based neighbor selection becomes meaningless
- All k neighbors are roughly the same distance away
- Decision boundaries become unreliable
- KD-Tree pruning fails (no effective partitioning)

**Mitigations**:
- Dimensionality reduction (PCA, t-SNE, autoencoders) before KNN
- Feature selection to keep only informative dimensions
- Use Manhattan distance (more robust in high-d than Euclidean)
- Switch to approximate methods (LSH, FAISS)

### Q2: How do you handle categorical features in KNN?

**Answer**:
1. **One-hot encoding**: Convert categories to binary vectors, use Euclidean/Hamming
2. **Ordinal encoding**: If categories have natural order (e.g., low/medium/high)
3. **Hamming distance**: Count mismatches across categorical dimensions
4. **Gower distance**: Mixed metric combining Euclidean (continuous) + Hamming (categorical)
5. **Embedding**: Learn dense representations (e.g., entity embeddings from neural nets)

### Q3: KNN vs Logistic Regression -- when to use which?

| Aspect | KNN | Logistic Regression |
|--------|-----|-------------------|
| Decision boundary | Nonlinear, local | Linear (or poly with features) |
| Interpretability | Low (no coefficients) | High (coefficients = feature importance) |
| Training speed | O(1) | O(n*d) -- iterative |
| Prediction speed | O(n*d) | O(d) -- fast |
| Feature scaling | Required | Helpful but not required |
| High dimensions | Poor (curse of dimensionality) | Handles well |
| Small dataset | Good | May underfit |

### Q4: How does KNN handle imbalanced classes?

**Problem**: If 95% of neighbors are class A, KNN almost always predicts A.

**Solutions**:
1. **Weighted KNN**: Inverse distance weighting gives closer minority samples more influence
2. **Adjust k**: Smaller k helps if minority samples cluster tightly
3. **SMOTE**: Oversample minority class by interpolating between existing minority neighbors
4. **Class-weighted voting**: Multiply each vote by inverse class frequency
5. **Radius-based**: Use all neighbors within radius r instead of fixed k

### Q5: What happens with duplicate/tied distances?

**Answer**: When multiple points share the k-th nearest distance:
1. **Include all** (k becomes variable) -- sklearn default with `algorithm='brute'`
2. **Random tiebreak** -- arbitrary but consistent
3. **Use weighted KNN** -- distances resolve most ties
4. **Odd k** -- helps for binary classification vote ties

### Q6: Can KNN be used for anomaly detection?

**Answer**: Yes. Compute the average distance to k nearest neighbors for each point.
Points with high average neighbor distance are anomalies.

```python
def knn_anomaly_scores(X, k=5):
    """Higher score = more anomalous."""
    scores = []
    for i, x in enumerate(X):
        distances = sorted([
            np.linalg.norm(x - X[j]) for j in range(len(X)) if j != i
        ])[:k]
        scores.append(np.mean(distances))
    return np.array(scores)
```

---

## 8. ML Fundamentals: Bias-Variance Tradeoff

### 8.1 Definitions

| Term | Definition | Intuition |
|------|-----------|-----------|
| **Bias** | Error from oversimplified assumptions | Model is too simple, misses patterns |
| **Variance** | Error from sensitivity to training data fluctuations | Model memorizes noise |
| **Irreducible error** | Noise in the data itself | Cannot be reduced by any model |

**Total error = Bias^2 + Variance + Irreducible error**

### 8.2 Tradeoff Visualization

```
Error
  ^
  |  \                    /
  |   \   Total Error   /
  |    \     ____      /
  |     \   /    \    /
  |      \_/      \  /
  |   Bias^2   Variance
  |
  +-------------------------> Model Complexity
     Simple                Complex
```

### 8.3 Examples

| Model | Bias | Variance | Example |
|-------|------|----------|---------|
| Linear regression (few features) | High | Low | Underfits nonlinear data |
| Deep neural network | Low | High | Overfits small datasets |
| KNN with k=1 | Low | High | Memorizes training data |
| KNN with k=n | High | Low | Predicts global majority class |
| Random forest | Low | Medium | Bagging reduces variance |

### 8.4 Interview Answer Template

"The bias-variance tradeoff means we cannot simultaneously minimize both. A simple
model (high bias) consistently misses patterns but gives stable predictions across
different training sets. A complex model (high variance) captures patterns but its
predictions swing wildly with different training data. The sweet spot is the model
complexity where total error is minimized. We find it through cross-validation."

---

## 9. ML Fundamentals: Overfitting and Regularization

### 9.1 Signs of Overfitting

- Training accuracy >> validation accuracy (large gap)
- Model performs well on seen data, poorly on unseen data
- Learning curve: training loss keeps decreasing, validation loss increases

### 9.2 Regularization Techniques

| Technique | How it works | Used in |
|-----------|-------------|---------|
| **L1 (Lasso)** | Adds sum(\|w_i\|) to loss; drives weights to 0 | Feature selection |
| **L2 (Ridge)** | Adds sum(w_i^2) to loss; shrinks weights | Prevents large weights |
| **Elastic Net** | L1 + L2 combined | Best of both |
| **Dropout** | Randomly zero neurons during training | Neural networks |
| **Early stopping** | Stop training when validation loss increases | Any iterative model |
| **Data augmentation** | Increase effective training set size | Image/NLP models |
| **Ensemble methods** | Bagging reduces variance (Random Forest) | General |

### 9.3 L1 vs L2 Interview Answer

"L1 adds the absolute value of weights to the loss, producing sparse solutions where
some weights become exactly zero -- useful for feature selection. L2 adds squared
weights, shrinking all weights toward zero but rarely to exactly zero -- better when
all features are potentially relevant. L1 gives a diamond-shaped constraint region
(corners touch axes), L2 gives a circular region. The corners of L1 are where
coefficients hit zero."

---

## 10. ML Fundamentals: Cross-Validation

### 10.1 Types

| Method | Description | When to Use |
|--------|-------------|-------------|
| **k-Fold CV** | Split data into k folds, train on k-1, validate on 1, rotate | Default choice (k=5 or 10) |
| **Stratified k-Fold** | k-Fold but preserves class ratios in each fold | Imbalanced classification |
| **Leave-One-Out (LOO)** | k-Fold where k=n | Very small datasets |
| **Time-series split** | Train on past, validate on future (no shuffling) | Temporal data -- never leak future |
| **Holdout** | Single train/val/test split | Large datasets where CV is expensive |

### 10.2 Common Mistakes

1. **Data leakage**: Fitting scaler on entire dataset before splitting.
   Fix: fit scaler on training fold only, transform validation fold.
2. **Using test set for hyperparameter tuning**: Test set should only be used once.
   Fix: use validation set or nested CV for tuning.
3. **Shuffling time-series data**: Destroys temporal structure.
   Fix: use TimeSeriesSplit.

### 10.3 Interview Answer

"I use stratified 5-fold cross-validation as my default. It gives a reliable estimate
of generalization performance while preserving class balance. For time-series data,
I switch to TimeSeriesSplit to avoid leaking future information. I always fit
preprocessing steps (scaling, encoding) inside the CV loop to prevent data leakage."

---

## 11. ML Fundamentals: Evaluation Metrics

### 11.1 Classification Metrics

| Metric | Formula | When to Use |
|--------|---------|-------------|
| **Accuracy** | (TP+TN) / (TP+TN+FP+FN) | Balanced classes |
| **Precision** | TP / (TP+FP) | Cost of false positive is high (spam filter) |
| **Recall** | TP / (TP+FN) | Cost of false negative is high (disease screening) |
| **F1** | 2 * P * R / (P + R) | Balance precision and recall |
| **AUC-ROC** | Area under ROC curve | Rank-based, threshold-independent |
| **Log loss** | -mean(y*log(p) + (1-y)*log(1-p)) | Probabilistic predictions |

### 11.2 Regression Metrics

| Metric | Formula | Interpretation |
|--------|---------|---------------|
| **MSE** | mean((y - y_hat)^2) | Penalizes large errors heavily |
| **RMSE** | sqrt(MSE) | Same units as target |
| **MAE** | mean(\|y - y_hat\|) | Robust to outliers |
| **R^2** | 1 - SS_res / SS_tot | Fraction of variance explained (1=perfect) |
| **MAPE** | mean(\|y - y_hat\| / \|y\|) * 100 | Percentage error, interpretable |

### 11.3 Confusion Matrix Quick Reference

```
                  Predicted
                  Pos    Neg
Actual  Pos  [   TP  |  FN  ]   <- Recall = TP / (TP + FN)
        Neg  [   FP  |  TN  ]
                  ^
                  Precision = TP / (TP + FP)
```

### 11.4 AUC-ROC Interview Answer

"AUC-ROC measures how well the model ranks positive examples above negative ones,
independent of threshold. An AUC of 0.5 means random guessing; 1.0 means perfect
separation. I use it when I care about ranking quality rather than a specific threshold.
For imbalanced datasets, I prefer AUC-PR (precision-recall curve) because ROC can be
misleadingly optimistic when negatives vastly outnumber positives."

---

## 12. ML Fundamentals: Feature Engineering

### 12.1 Common Techniques

| Technique | Example | When |
|-----------|---------|------|
| **Scaling** | StandardScaler, MinMaxScaler | Distance-based models (KNN, SVM) |
| **Log transform** | log(income) | Right-skewed distributions |
| **Binning** | Age -> age_group | Capture nonlinear relationships in linear models |
| **Interaction features** | x1 * x2 | Known feature interactions |
| **Polynomial features** | x, x^2, x^3 | Nonlinear patterns in linear models |
| **Target encoding** | Category -> mean(target) per category | High-cardinality categoricals |
| **Embedding** | Word2Vec, entity embeddings | Text, categorical with semantic meaning |

### 12.2 Feature Selection Methods

| Method | Type | How |
|--------|------|-----|
| **Correlation filter** | Filter | Remove features with low correlation to target |
| **Variance threshold** | Filter | Remove near-constant features |
| **L1 regularization** | Embedded | Lasso drives irrelevant weights to zero |
| **Mutual information** | Filter | Information-theoretic relevance measure |
| **Recursive Feature Elimination** | Wrapper | Iteratively remove least important features |
| **Tree-based importance** | Embedded | Random Forest / XGBoost feature importances |

---

## 13. Quick-Fire Q&A Cheat Sheet

These are the rapid-fire ML questions reported in 1p3a Uber BPS interviews. Practice
delivering each answer in 30-60 seconds.

### Bias-Variance

**Q: What is bias-variance tradeoff?**
A: Total error = bias^2 + variance + noise. Simple models have high bias (underfit),
complex models have high variance (overfit). We tune complexity (regularization, k in KNN,
tree depth) via cross-validation to minimize total error.

### Overfitting

**Q: How do you know if a model is overfitting? How do you fix it?**
A: Training accuracy much higher than validation accuracy. Fix: more data, regularization
(L1/L2), dropout, simpler model, early stopping, cross-validation for hyperparameter tuning.

### KNN Basics

**Q: Explain KNN. What are its pros and cons?**
A: Lazy learner that classifies by majority vote of k nearest neighbors. Pros: simple,
no training, naturally nonlinear. Cons: slow prediction O(n*d), curse of dimensionality,
needs feature scaling, stores all data in memory.

**Q: How do you choose k in KNN?**
A: Cross-validation over a range of k values. k=1 overfits, k=n underfits. Common
starting point: k=sqrt(n). Use odd k for binary classification to avoid ties.

### Metrics

**Q: When would you use precision vs recall?**
A: Precision when false positives are costly (spam filter -- don't block real email).
Recall when false negatives are costly (cancer screening -- don't miss sick patients).
F1 balances both.

**Q: Explain AUC-ROC.**
A: Area under the curve plotting true positive rate vs false positive rate at all
thresholds. 0.5 = random, 1.0 = perfect. Measures ranking quality, threshold-independent.
For imbalanced data, prefer AUC-PR.

### Regularization

**Q: What is regularization? L1 vs L2?**
A: Penalty on model weights to prevent overfitting. L1 (Lasso) adds |w|, produces sparse
models (feature selection). L2 (Ridge) adds w^2, shrinks all weights (no sparsity).
Elastic Net combines both.

### Cross-Validation

**Q: Why cross-validation instead of a single train/test split?**
A: Single split is high variance -- performance depends on which data lands in test set.
k-Fold CV averages over k different splits, giving a more reliable estimate. Also lets
you tune hyperparameters without touching the test set.

### Trees and Ensembles

**Q: Random Forest vs Gradient Boosting?**
A: Random Forest: bagging (parallel trees, reduces variance). Gradient Boosting: boosting
(sequential trees, each corrects previous errors, reduces bias). RF is more robust to
hyperparameters; GB often achieves higher accuracy but is easier to overfit.

### Dimensionality Reduction

**Q: What is PCA and when would you use it?**
A: Principal Component Analysis finds orthogonal directions of maximum variance and
projects data onto the top-k components. Use it to reduce dimensionality before KNN/SVM,
for visualization (2D/3D), or to remove multicollinearity. Limitation: linear only --
for nonlinear structure, use t-SNE or autoencoders.

### Uber-Specific ML

**Q: How would you use KNN at Uber?**
A: (1) Driver-rider matching: find k nearest available drivers to a rider's location
using spatial indexing (KD-Tree for 2D GPS). (2) ETA estimation: find k most similar
past trips (features: distance, time of day, traffic) and average their actual duration.
(3) Fraud detection: anomalous transactions have high average distance to k nearest
legitimate transactions.

---

## Summary: What to Review the Night Before

1. **KNN**: Implementation, distance metrics, k selection, weighted KNN, curse of dimensionality
2. **Bias-variance**: Definition, tradeoff curve, examples by model type
3. **Overfitting**: Signs, regularization (L1/L2/dropout/early stopping)
4. **Cross-validation**: k-Fold, stratified, time-series split, data leakage pitfalls
5. **Metrics**: Precision/recall/F1, AUC-ROC vs AUC-PR, MSE/MAE/R^2
6. **Practice**: Deliver each quick-fire answer in 30-60 seconds aloud
