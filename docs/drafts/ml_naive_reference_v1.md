<!-- ML_NAIVE_REFERENCE_V1_20260504 -->
# ML 朴素实现汇总 (Naive Reference Implementations)

> KNN / KMeans / LogReg 三套 ref impl, 统一变量约定 (N/M/D/k/C). 不涉及 LR closed-form (lstsq) 与 Geometric Median Weiszfeld iteration -- 那两个走各自笔记 (db://1102, db://1108).

## Variable conventions

- **N**: number of training samples
- **M**: number of test samples
- **D**: feature dimension
- **k**: hyperparameter (num neighbors / num clusters)
- **C**: number of classes

## Vectorization tricks featured

- Pairwise squared distance via expansion: $\|x-y\|^2 = \|x\|^2 + \|y\|^2 - 2\,x \cdot y$ (memory $O(MN)$, not $O(MND)$)
- `np.argpartition` for top-k: $O(N)$ per row, vs `np.argsort` $O(N \log N)$
- Broadcasting one-hot vote: `(M,k,1) == (C,)` -> `(M,k,C)` boolean tensor, sum over axis=1
- k-means++ init: sample next centroid with probability $\propto D(x)^2$ (min squared distance to chosen centroids)
- Empty-cluster reseed: when an M-step assigns 0 members to cluster $j$, re-seed at the point farthest from its current centroid
- BCE + sigmoid is the GLM canonical link: gradient simplifies to $\nabla_z L = p - y$, the sigmoid derivative cancels

---

## Full implementation

```python
"""
Coding Interview Prep: KNN, KMeans, Logistic Regression
========================================================
Clean reference implementations with consistent variable naming.

Conventions used throughout:
    N = number of training samples
    M = number of test samples
    D = feature dimension
    k = hyperparameter (num neighbors / num clusters)
    C = number of classes

Key tricks demonstrated:
    - Vectorized pairwise distances via ||x-y||^2 = ||x||^2 + ||y||^2 - 2 x.y
    - argpartition (O(N)) instead of argsort (O(N log N)) for top-k
    - Broadcasting for one-hot voting: (M,k,1) == (C,) -> (M,k,C)
    - k-means++ initialization (min over centroids, then normalize)
    - Empty-cluster handling (re-seed farthest point)
    - BCE + sigmoid: gradient simplifies to (p - y) — GLM canonical link
"""

import numpy as np


# =============================================================================
# 1. KNN  (lazy supervised classifier)
# =============================================================================
def knn_predict(X_train, y_train, X_test, k):
    """
    X_train: (N, D)
    y_train: (N,)  integer labels in [0, C)
    X_test:  (M, D)
    k:       int, number of neighbors
    return:  (M,) predicted labels
    """
    N, D = X_train.shape
    M = X_test.shape[0]
    C = int(y_train.max()) + 1

    # Pairwise squared distance via expansion (memory: O(M*N), not O(M*N*D))
    x_te_sq = (X_test ** 2).sum(axis=1, keepdims=True)    # (M, 1)
    x_tr_sq = (X_train ** 2).sum(axis=1)                   # (N,)
    cross = X_test @ X_train.T                             # (M, N)
    dists_sq = np.maximum(x_te_sq + x_tr_sq - 2 * cross, 0)  # (M, N)

    # Top-k nearest neighbors: argpartition is O(N) per row
    knn_idx = np.argpartition(dists_sq, kth=k, axis=1)[:, :k]  # (M, k)
    knn_labels = y_train[knn_idx]                              # (M, k)

    # Majority vote via broadcasting
    # (M, k, 1) == (C,)  →  (M, k, C) bool
    votes = (knn_labels[:, :, None] == np.arange(C)).sum(axis=1)  # (M, C)
    return votes.argmax(axis=1)


# =============================================================================
# 2. KMeans  (Lloyd's algorithm + k-means++ init + empty-cluster handling)
# =============================================================================
def kmeans(X, k, max_iter=100, tol=1e-4, seed=0):
    """
    X:        (N, D)
    k:        int, number of clusters
    max_iter: int
    tol:      stop when max centroid shift < tol
    seed:     int
    return:   centroids (k, D), labels (N,)
    """
    N, D = X.shape
    rng = np.random.default_rng(seed)

    # ---- k-means++ initialization ----
    # First centroid: uniform random.
    # Each next centroid: sampled with prob ∝ D(x)^2 to nearest chosen centroid.
    centroids = np.empty((k, D))
    centroids[0] = X[rng.integers(N)]
    for j in range(1, k):
        diff = X[:, None, :] - centroids[None, :j, :]    # (N, j, D)
        d2 = (diff ** 2).sum(axis=2).min(axis=1)          # (N,) min over chosen
        probs = d2 / d2.sum()
        centroids[j] = X[rng.choice(N, p=probs)]

    # ---- Lloyd's iteration ----
    for _ in range(max_iter):
        # E-step: assign each point to its nearest centroid
        diff = X[:, None, :] - centroids[None, :, :]      # (N, k, D)
        dists_sq = (diff ** 2).sum(axis=2)                 # (N, k)
        labels = dists_sq.argmin(axis=1)                   # (N,)

        # M-step: recompute centroid as mean of its members; handle empty clusters
        new_centroids = np.empty_like(centroids)
        for j in range(k):
            members = X[labels == j]
            if len(members) == 0:
                # Empty cluster: re-seed at the point farthest from its centroid
                far_idx = dists_sq.min(axis=1).argmax()
                new_centroids[j] = X[far_idx]
            else:
                new_centroids[j] = members.mean(axis=0)

        # Convergence check
        shift = np.linalg.norm(new_centroids - centroids, axis=1).max()
        centroids = new_centroids
        if shift < tol:
            break

    # Final assignment with converged centroids (so labels match)
    diff = X[:, None, :] - centroids[None, :, :]
    labels = (diff ** 2).sum(axis=2).argmin(axis=1)
    return centroids, labels


# =============================================================================
# 3. Logistic Regression  (binary, batch gradient descent)
# =============================================================================
def sigmoid(z):
    """Numerically stable sigmoid: split on sign of z to avoid overflow."""
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def train_logistic_regression(X, y, lr=0.1, n_iter=1000):
    """
    X:      (N, D)
    y:      (N,) in {0, 1}
    return: W (D,), b (scalar)

    Loss (from MLE on Bernoulli):
        L = -1/N * sum[ y log p + (1-y) log(1-p) ]    where p = sigmoid(X W + b)

    Gradients (BCE + sigmoid is the canonical-link GLM pairing,
    so the sigmoid derivative cancels and we get a clean form):
        dL/dz = p - y
        dL/dW = X^T (p - y) / N
        dL/db = 1^T (p - y) / N        # implemented as err.sum() / N
    """
    N, D = X.shape
    W = np.zeros(D)        # LR loss is convex; zero init is fine
    b = 0.0

    for _ in range(n_iter):
        z = X @ W + b                  # (N,)
        p = sigmoid(z)                 # (N,)
        err = p - y                    # (N,)

        dW = X.T @ err / N             # (D,)
        db = err.sum() / N             # scalar  ( == 1^T err / N )

        W -= lr * dW
        b -= lr * db

    return W, b


def predict_logistic_regression(X, W, b, threshold=0.5):
    """Return (M,) {0, 1} predictions."""
    return (sigmoid(X @ W + b) >= threshold).astype(int)


# =============================================================================
# Sanity-check demos
# =============================================================================
if __name__ == "__main__":
    rng = np.random.default_rng(42)

    # --- KNN demo ---
    X_tr = rng.normal(size=(200, 4))
    y_tr = (X_tr[:, 0] + X_tr[:, 1] > 0).astype(int)
    X_te = rng.normal(size=(50, 4))
    y_te = (X_te[:, 0] + X_te[:, 1] > 0).astype(int)
    pred = knn_predict(X_tr, y_tr, X_te, k=5)
    print(f"[KNN]    accuracy: {(pred == y_te).mean():.3f}")

    # --- KMeans demo ---
    centers = np.array([[0.0, 0.0], [5.0, 5.0], [0.0, 5.0]])
    X = np.vstack([rng.normal(c, 0.5, size=(100, 2)) for c in centers])
    cents, labs = kmeans(X, k=3, seed=0)
    print(f"[KMeans] centroids shape {cents.shape}, labels shape {labs.shape}")
    print(f"         learned centers (sorted):")
    for c in sorted(cents.tolist()):
        print(f"           {c}")

    # --- LR demo ---
    X = rng.normal(size=(500, 3))
    true_w = np.array([1.0, -2.0, 0.5])
    true_b = 0.3
    p_true = sigmoid(X @ true_w + true_b)
    y = (rng.uniform(size=500) < p_true).astype(int)
    W, b = train_logistic_regression(X, y, lr=0.5, n_iter=2000)
    pred = predict_logistic_regression(X, W, b)
    print(f"[LR]     accuracy: {(pred == y).mean():.3f}")
    print(f"         learned W = {W.round(3)}, b = {b:.3f}")
    print(f"         true    W = {true_w},      b = {true_b}")
```
