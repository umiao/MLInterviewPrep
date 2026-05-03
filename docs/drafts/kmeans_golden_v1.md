# K-Means with K-Means++ (Pure Python)

> **TL;DR** — 从零实现的硬聚类算法。
> **核心循环**：(1) K-Means++ 初始化（首个 centroid 随机，后续按 $$D(x)^2$$ 加权采样）；(2) E-step：每点 argmin 到最近 centroid；(3) M-step：每簇取均值；(4) 检查停止条件。
> **4 种停止条件**：max iter / centroid 移动 < tol / labels 不变 / SSE 变化 < tol。
> **空簇处理**：随机重选一个数据点（防 `mean()` 返回 NaN）。
> **复杂度**：时间 $$O(n \cdot k \cdot d \cdot T)$$，空间 $$O((n+k) \cdot d)$$。

---

## 实现

### 0. Class skeleton

```python
import numpy as np
from typing import Optional

class KMeans:
    def __init__(self, num_clusters, max_iterations=300,
                 convergence_threshold=1e-4, random_state=None):
        self.num_clusters = num_clusters
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.rng = np.random.RandomState(random_state)
        self.cluster_centers: Optional[np.ndarray] = None  # (k, d)
        self.cluster_labels: Optional[np.ndarray] = None   # (n,)
        self.total_sse: Optional[float] = None
```

### 1. Initialization — K-Means++ vs Vanilla random

**K-Means++**：首个 centroid 均匀随机，之后按 $$D(x)^2$$ 加权采样（$$D(x)$$ 是点到最近已选 centroid 的距离）。等价于 Farthest Point Sampling 的概率软化版——把 centers 推开，但不必然选中 outlier。

```python
def _init_centers_plusplus(self, data):
    n = data.shape[0]
    centers = [data[self.rng.randint(n)]]
    for _ in range(1, self.num_clusters):
        sq_dists = np.min(
            [np.sum((data - c) ** 2, axis=1) for c in centers], axis=0
        )
        probs = sq_dists / sq_dists.sum()
        centers.append(data[self.rng.choice(n, p=probs)])
    return np.array(centers)
```

**Vanilla random (Forgy)**：从数据点中无放回均匀采样，仅作对比基线。

```python
def _init_centers_random(self, data):
    chosen_idx = self.rng.choice(
        data.shape[0], size=self.num_clusters, replace=False
    )
    return data[chosen_idx]
```

### 2. E-step — Assignment

每个点对所有 centroid 算欧氏距离平方，取 argmin 作为簇归属。

```python
def _assign_to_nearest_center(self, data):
    sq_dists = np.array([
        np.sum((data - c) ** 2, axis=1) for c in self.cluster_centers
    ]).T  # (n, k)
    return np.argmin(sq_dists, axis=1)
```

### 3. M-step — Center update

每簇取均值；空簇随机重选一个数据点，否则 `mean()` 在空数组上会触发 NaN。

```python
def _recompute_centers(self, data, labels):
    updated = np.zeros_like(self.cluster_centers)
    for k in range(self.num_clusters):
        members = data[labels == k]
        if len(members) > 0:
            updated[k] = members.mean(axis=0)
        else:
            updated[k] = data[self.rng.randint(data.shape[0])]
    return updated
```

### 4. Objective — Total SSE

目标函数 $$\text{SSE} = \sum_{k} \sum_{x \in C_k} \|x - \mu_k\|^2$$，用作收敛检测与最终质量度量。

```python
def _compute_total_sse(self, data, labels):
    total = 0.0
    for k in range(self.num_clusters):
        members = data[labels == k]
        if len(members) > 0:
            total += np.sum((members - self.cluster_centers[k]) ** 2)
    return total
```

### 5. Main loop — `fit()` with 4 stopping criteria

主循环交织了所有 4 种停止条件，inline 用 `# Criterion N` 作为锚点。

```python
def fit(self, data):
    self.cluster_centers = self._init_centers_plusplus(data)
    previous_labels, previous_sse = None, float('inf')

    for _ in range(self.max_iterations):              # Criterion 2: max iter
        self.cluster_labels = self._assign_to_nearest_center(data)

        # Criterion 3: assignments unchanged
        if previous_labels is not None and \
           np.array_equal(self.cluster_labels, previous_labels):
            break

        new_centers = self._recompute_centers(data, self.cluster_labels)

        # Criterion 1: max centroid shift
        max_shift = np.max(np.sqrt(np.sum(
            (new_centers - self.cluster_centers) ** 2, axis=1
        )))
        self.cluster_centers = new_centers

        # Criterion 4: SSE change
        current_sse = self._compute_total_sse(data, self.cluster_labels)
        if max_shift < self.convergence_threshold or \
           abs(previous_sse - current_sse) < self.convergence_threshold:
            break

        previous_labels = self.cluster_labels.copy()
        previous_sse = current_sse

    self.total_sse = self._compute_total_sse(data, self.cluster_labels)
    return self
```

### 6. Predict

```python
def predict(self, data):
    return self._assign_to_nearest_center(data)
```

---

## Vanilla Random vs K-Means++

|                | Vanilla Random (Forgy)     | K-Means++                                       |
| -------------- | -------------------------- | ----------------------------------------------- |
| 选择方式       | 数据点中均匀无放回采样     | 首个随机，后续概率 ∝ $$D(x)^2$$                 |
| 失败模式       | 空簇、收敛慢、SSE 方差大   | 都显著缓解                                      |
| Multi-restart  | 必须（sklearn `n_init=10`） | `n_init=1` 通常够                               |
| 理论保证       | 无                         | $$\mathbb{E}[\text{SSE}] \leq 8(\ln k + 2) \cdot \text{OPT}$$ |

**一句话**：K-Means++ = Farthest Point Sampling 的概率软化版——按 $$D(x)^2$$ 抽样既把 centers 推开，又比 deterministic FPS 对 outlier 鲁棒（孤立点只是"概率高"，不必然主导）。

---

## 面试追问 (Cheat Sheet)

> **Q: K 怎么选？**

- **Elbow**：画 K vs SSE 曲线找拐点；缺点是拐点常不明显，主观性强。
- **Silhouette**：$$s = (b-a)/\max(a,b)$$，$$a$$ 是簇内均距、$$b$$ 到最近邻簇均距，取均值最大的 K。
- **Gap statistic**：实际 SSE vs 均匀分布零假设下的期望 SSE，差距最大者。

> **Q: K-Means 的局限？**

- 只能找凸簇（Voronoi 划分）；对 outlier 敏感（mean 被拉偏）；需预设 K；初始化敏感（K-Means++ 缓解）。

> **Q: 与 GMM 的关系？**

- K-Means 是 GMM 的硬分配特例（各向同性、等方差、$$\sigma \to 0$$）。
- GMM 用 EM：E-step 算 responsibility（每点属各簇的概率），M-step 更新 $$\mu, \Sigma, \pi$$，能拟合椭圆形簇。

> **Q: 与 spectral clustering 的区别？**

- K-Means 处理不了非凸簇（同心圆、月牙）。
- Spectral 流程：构相似度图 → Laplacian → 取前 K 个特征向量 → 在特征空间跑 K-Means。代价：$$O(n^3)$$ 特征分解。

> **Q: 大规模数据？**

- **Mini-batch K-Means**：每次随机采 batch 更新 centroid，sklearn 有默认实现。
