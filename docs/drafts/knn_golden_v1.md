# K-Nearest Neighbors (KNN + Weighted)

> **TL;DR** -- 实例化的 lazy learner, 训练 = 存数据, 全部 compute 推迟到 `predict`.
> **核心三步**: (1) 算 query 到所有训练点的欧氏距离; (2) `argpartition` 取 Top-K (平均 $$O(n)$$); (3) 投票 / 加权平均.
> **三种 weighting**: `uniform`, `inverse` $$w_i = 1/(d_i+\varepsilon)$$, `gaussian` $$w_i = e^{-d_i^2/(2\sigma^2)}$$.
> **失败模式**: $$d_i = 0$$ 时 `1/d` 触发 `inf`, 必须加 $$\varepsilon$$; 高维下距离趋同 (curse of dimensionality).
> **复杂度**: 训练 $$O(1)$$, 单 query brute force $$O(nd)$$, KD-tree 低维 $$O(\log n \cdot d)$$, 空间 $$O(nd)$$.

---

## 实现

### 0. Class skeleton

```python
import numpy as np
from typing import Literal, Optional

class KNN:
    def __init__(self, k: int = 5,
                 task: Literal["classification", "regression"] = "classification",
                 weighting: Literal["uniform", "inverse", "gaussian"] = "uniform",
                 sigma: float = 1.0,
                 epsilon: float = 1e-9):
        self.k = k
        self.task = task
        self.weighting = weighting
        self.sigma = sigma                              # gaussian bandwidth
        self.epsilon = epsilon                          # 1/(d+eps) guard
        self.X_train: Optional[np.ndarray] = None       # (n, d)
        self.y_train: Optional[np.ndarray] = None       # (n,)
```

### 1. fit -- store data, no training

Lazy: 仅存 `(X, y)`, 所有 compute 推迟到 `predict` -- 增量更新友好 (无需重训).

```python
def fit(self, X, y):
    self.X_train, self.y_train = X, y
    return self
```

### 2. Distance -- vectorized euclidean

展开 $$\|a - b\|^2 = \|a\|^2 + \|b\|^2 - 2 a \cdot b$$, broadcasting 一次算所有 pair; `sqrt` 前 clip $$\geq 0$$ 防 fp `NaN`.

```python
def _pairwise_euclidean(self, X_query):
    # X_query: (nq, d), self.X_train: (nt, d)
    sq_q = np.sum(X_query ** 2, axis=1, keepdims=True)          # (nq, 1)
    sq_t_col = np.sum(self.X_train ** 2, axis=1, keepdims=True) # (nt, 1)
    sq_t = sq_t_col.T                                            # (1, nt)
    cross = X_query @ self.X_train.T                             # (nq, nt)
    raw = sq_q + sq_t - 2 * cross                                # (nq, nt) raw squared dist
    sq_dist = np.maximum(raw, 0.0)                               # (nq, nt) clip <0 fp noise
    return np.sqrt(sq_dist)                                      # (nq, nt)
```

### 3. Top-K -- `argpartition`, NOT `argsort`

`argpartition` 平均 $$O(n)$$ (Quickselect, 仅保证第 K 位左小右大, 不排序前 K) -- KNN 只需 SET; `argsort` $$O(n \log n)$$ 在 $$n=10^6$$ 时多花 20×.

```python
def _topk_indices(self, distances):
    # distances: (nq, nt)
    partitioned = np.argpartition(distances, kth=self.k, axis=1)  # (nq, nt)
    return partitioned[:, :self.k]                                # (nq, k)
```

### 4. Vote / Average -- weighting variants + predict

分类: **weighted majority vote** ($$\arg\max_c \sum_{i:y_i=c} w_i$$); 回归: **weighted average** $$\hat y = \sum_i w_i y_i / \sum_i w_i$$. 三种 weighting 共享同一权重函数, 下表对比.

```python
def _weights(self, neighbor_dists):
    # neighbor_dists: (nq, k)
    if self.weighting == "uniform":
        return np.ones_like(neighbor_dists)                      # (nq, k)
    if self.weighting == "inverse":
        return 1.0 / (neighbor_dists + self.epsilon)             # (nq, k)
    if self.weighting == "gaussian":
        sq = neighbor_dists ** 2                                 # (nq, k)
        scaled = sq / (2.0 * self.sigma ** 2)                    # (nq, k)
        return np.exp(-scaled)                                   # (nq, k)
    raise ValueError(self.weighting)

def predict(self, X_query):
    # X_query: (nq, d)
    distances = self._pairwise_euclidean(X_query)                # (nq, nt)
    topk_idx = self._topk_indices(distances)                     # (nq, k)
    neighbor_dists = np.take_along_axis(distances, topk_idx, axis=1)  # (nq, k)
    neighbor_labels = self.y_train[topk_idx]                     # (nq, k)
    weights = self._weights(neighbor_dists)                      # (nq, k)

    if self.task == "regression":
        weighted = weights * neighbor_labels                      # (nq, k)
        numerator = np.sum(weighted, axis=1)                      # (nq,)
        denominator = np.sum(weights, axis=1)                     # (nq,)
        return numerator / denominator                            # (nq,)

    classes = np.unique(self.y_train)                            # (n_classes,)
    scores = np.zeros((X_query.shape[0], len(classes)))          # (nq, n_classes)
    for j, c in enumerate(classes):
        mask = (neighbor_labels == c).astype(weights.dtype)      # (nq, k)
        scores[:, j] = np.sum(weights * mask, axis=1)            # (nq,)
    return classes[np.argmax(scores, axis=1)]                    # (nq,)
```

---

## Weighting Variants

|              | Uniform        | Inverse $$1/(d+\varepsilon)$$  | Gaussian $$e^{-d^2/2\sigma^2}$$  |
| ------------ | -------------- | ------------------------------ | -------------------------------- |
| 选择方式     | 等权多数票     | 距离倒数加权                    | RBF 核加权                       |
| 失败模式     | 偶 K 易 tie    | $$d=0$$ 漏 $$\varepsilon$$ 爆 NaN | $$\sigma$$ 选错退化              |
| 实践默认值   | 奇 K           | $$\varepsilon = 10^{-9}$$       | $$\sigma$$ = 邻居距离中位数      |

**一句话**: weighted KNN 把"硬 top-K cutoff"改成连续权重, 对 K 选错鲁棒性更高 -- 默认 `inverse`, 数据光滑时换 `gaussian`.

---

## 面试追问 (Cheat Sheet)

> **Q: K 怎么选?**

- 5-fold CV 在 $$\{1, 3, 5, \ldots, \sqrt{n}\}$$ 扫描, 选 validation 最优.
- 太小过拟合 (单点噪声主导), 太大欠拟合 (类边界被平滑); 奇 K 防 tie.

> **Q: Curse of dimensionality?**

- 高维下所有点距离趋于相等, KNN 失去判别力; 经验 $$d \gtrsim 10$$ 即明显退化.
- 解法: PCA / LDA / autoencoder 先降维, 或 metric learning (LMNN, NCA) 学"同类近异类远".

> **Q: 加速 query?**

- Brute force $$O(nd)$$ -> KD-tree 低维 ($$d \leq 20$$) 平均 $$O(\log n \cdot d)$$, worst $$O(n)$$.
- ANN (FAISS / HNSW / ScaNN) 在 $$d \sim 10^2$$--$$10^3$$ 压到亚秒, 召回 < 100%.

> **Q: 为什么必须特征缩放?**

- 欧氏距离对量级敏感: 收入 ($$10^4$$) 会主导年龄 ($$10^1$$).
- `StandardScaler` 是 distance-based 模型 (KNN / SVM / K-Means) 的共同前置.

> **Q: Lazy vs eager learning?**

- KNN 训 $$O(1)$$ 推 $$O(nd)$$, 增量更新友好但必存 $$O(nd)$$ 训练数据 (大数据退役主因).
- 决策树 / NN 是 eager: 训练慢, 推理 $$O(d)$$.

---

## End-to-end test

```python
import numpy as np
np.random.seed(0)
N_train, N_test, D, K = 100, 20, 4, 5
X_train = np.random.rand(N_train, D)
y_train = np.random.randint(0, 3, N_train)
X_test = np.random.rand(N_test, D)
knn = KNN(k=K).fit(X_train, y_train)
preds = knn.predict(X_test)
assert preds.shape == (N_test,)
print(f"Predicted classes: {np.unique(preds)}")
```
