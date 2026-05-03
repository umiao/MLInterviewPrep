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

KNN 是 lazy learner: 没有训练循环, `fit` 只把 `(X, y)` 存下来, 所有 compute 推迟到 `predict`. 这也是 KNN 对训练数据增量更新友好的根因 (无需重训).

```python
def fit(self, X, y):
    self.X_train, self.y_train = X, y
    return self
```

### 2. Distance -- vectorized euclidean

展开 $$\|a - b\|^2 = \|a\|^2 + \|b\|^2 - 2 a \cdot b$$, 用 broadcasting 一次算 all query × all train. 浮点可能产生轻微负数, `sqrt` 前 clip 到 $$\geq 0$$ 防 `NaN`.

```python
def _pairwise_euclidean(self, X_query):
    sq_q = np.sum(X_query ** 2, axis=1, keepdims=True)         # (nq, 1)
    sq_t = np.sum(self.X_train ** 2, axis=1, keepdims=True).T  # (1, nt)
    cross = X_query @ self.X_train.T                            # (nq, nt)
    sq_dist = np.maximum(sq_q + sq_t - 2 * cross, 0.0)          # avoid sqrt(<0)
    return np.sqrt(sq_dist)
```

### 3. Top-K -- `argpartition`, NOT `argsort`

`np.argpartition` 平均 $$O(n)$$ (Quickselect), 仅保证"第 K 位左侧都更小, 右侧都更大", 不排序前 K 之间. KNN 只需 SET, 排序是浪费. `argsort` 是 $$O(n \log n)$$ -- 在 $$n=10^6, K=5$$ 时多花约 20×.

```python
def _topk_indices(self, distances):
    return np.argpartition(distances, kth=self.k, axis=1)[:, :self.k]
```

### 4. Vote / Average -- weighting variants + predict

差异仅在最后一步: 分类是 **weighted majority vote** (每候选类对权重求和取 `argmax`), 回归是 **weighted average** $$\hat y = \sum_i w_i y_i / \sum_i w_i$$. 三种 weighting 共享同一权重函数, 下游分支只看 `task`.

**Uniform**: $$w_i = 1$$, 退化成原始 majority vote / 平均.

**Inverse-distance**: $$w_i = 1 / (d_i + \varepsilon)$$. $$\varepsilon$$ 是关键 -- query 落在训练点上 ($$d_i = 0$$) 时, $$1/d_i = \infty$$ 在 sum 里污染整个 batch 成 `NaN`; 加 $$\varepsilon = 10^{-9}$$ 后该点 $$w \approx 10^9$$ (有限但远大于其它邻居), 正是想要的"精确命中支配"语义.

**Gaussian / RBF**: $$w_i = \exp(-d_i^2 / (2\sigma^2))$$. $$\sigma \to 0$$ 退化成 1-NN, $$\sigma \to \infty$$ 退化成 uniform. 实战 $$\sigma$$ 取 K 个邻居距离的中位数 (Silverman 简化) 或 5-fold CV 搜.

```python
def _weights(self, neighbor_dists):
    if self.weighting == "uniform":
        return np.ones_like(neighbor_dists)
    if self.weighting == "inverse":
        return 1.0 / (neighbor_dists + self.epsilon)
    if self.weighting == "gaussian":
        return np.exp(-(neighbor_dists ** 2) / (2.0 * self.sigma ** 2))
    raise ValueError(self.weighting)

def predict(self, X_query):
    distances = self._pairwise_euclidean(X_query)               # (nq, nt)
    topk_idx = self._topk_indices(distances)                    # (nq, k)
    neighbor_dists = np.take_along_axis(distances, topk_idx, axis=1)
    neighbor_labels = self.y_train[topk_idx]                    # (nq, k)
    weights = self._weights(neighbor_dists)                     # (nq, k)

    if self.task == "regression":
        return np.sum(weights * neighbor_labels, axis=1) / np.sum(weights, axis=1)

    classes = np.unique(self.y_train)
    scores = np.zeros((X_query.shape[0], len(classes)))
    for j, c in enumerate(classes):
        mask = (neighbor_labels == c).astype(weights.dtype)
        scores[:, j] = np.sum(weights * mask, axis=1)
    return classes[np.argmax(scores, axis=1)]
```

---

## Weighting Variants

|              | Uniform        | Inverse $$1/(d+\varepsilon)$$  | Gaussian $$e^{-d^2/2\sigma^2}$$  |
| ------------ | -------------- | ------------------------------ | -------------------------------- |
| 选择方式     | 等权多数票     | 距离倒数加权                    | RBF 核加权                       |
| 失败模式     | 偶 K 易 tie    | $$d=0$$ 漏 $$\varepsilon$$ 爆 NaN | $$\sigma$$ 选错退化              |
| 实践默认值   | 奇 K           | $$\varepsilon = 10^{-9}$$       | $$\sigma$$ = 邻居距离中位数      |
| 复杂度       | $$O(K)$$       | $$O(K)$$                        | $$O(K)$$                         |

**一句话**: weighted KNN 把"硬 top-K cutoff"改成连续权重, 近邻贡献大、远邻贡献小, 对 K 选错鲁棒性更高 -- 默认从 `inverse` 起步, 数据光滑时换 `gaussian`.

---

## 面试追问 (Cheat Sheet)

> **Q: K 怎么选?**

- 5-fold CV 在 $$\{1, 3, 5, \ldots, \sqrt{n}\}$$ 上扫描, 选 validation 最优.
- 太小过拟合 (单点噪声主导), 太大欠拟合 (类边界被平滑).
- 偶 K 易 tie, 多分类无效; weighted vote 实数权重几乎不可能完全 tie.

> **Q: Curse of dimensionality?**

- 高维下所有点距离趋于相等, KNN 失去判别力.
- 经验 $$d \gtrsim 10$$ 即明显退化 -- 需 PCA / LDA / autoencoder 降维.
- 或换 metric learning (LMNN, NCA) 学"同类近异类远"的距离.

> **Q: 加速 query?**

- Brute force 单 query $$O(nd)$$, 大数据吃不消.
- KD-tree 低维 ($$d \leq 20$$) 平均 $$O(\log n \cdot d)$$, worst case $$O(n)$$.
- ANN (FAISS / HNSW / ScaNN) 在 $$d \sim 10^2\text{--}10^3$$ 压到亚秒, 召回 < 100%.

> **Q: 分类 vs 回归 weighting 差异?**

- 共享: 距离, top-K, weighting; 差异仅在最后一步.
- 分类 $$\text{score}(c) = \sum_{i: y_i = c} w_i$$, 取 $$\arg\max$$.
- 回归 $$\hat y = \sum w_i y_i / \sum w_i$$. Uniform 退化 = 多数票 / 平均.

> **Q: 为什么必须特征缩放?**

- 欧氏距离对量级敏感: 收入 ($$10^4$$) 会主导年龄 ($$10^1$$) 距离.
- `StandardScaler` (zero-mean unit-var) 是 distance-based 模型 (KNN / SVM / K-Means) 的共同前置.

> **Q: Lazy vs eager learning?**

- KNN 训练 $$O(1)$$ 存数据, 推理 $$O(nd)$$ -- 训练数据频繁更新友好.
- 决策树 / NN 是 eager: 训练慢, 推理 $$O(d)$$ 或 $$O(\text{depth})$$.
- KNN 致命点: 必须存全部训练数据 ($$O(nd)$$ 空间), 大数据场景退役主因.
