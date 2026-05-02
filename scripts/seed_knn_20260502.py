"""Seed: T-P0-687 [MLI-C] -- KNN + Weighted KNN ml_coding handwritten solution.

Adds a new `problems` row mirroring the K-Means(1064) notes style:
- title='K-Nearest Neighbors (KNN + Weighted)'
- category='ml_coding', difficulty='medium'
- notes contain 题目描述 / 核心代码 (vanilla + weighted) / 关键要点 / 面试追问 / 复杂度

Canonical key for upsert: title + source. Source-of-truth for content lives
in this file's CONTENT/DESCRIPTION constants, never edited via DB writes.

Idempotency:
- INSERT skipped if a row with the same title+source already exists.
- UPDATE skipped if existing description+notes are byte-equal to the
  canonical payload. Otherwise the row is rewritten in place. Second run
  with no upstream change = 0 writes.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "K-Nearest Neighbors (KNN + Weighted)"
SOURCE = "ml-coding-handwritten-2026-05-02"
DIFFICULTY = "medium"
PATTERN = "ML Implementation"
CATEGORY = "ml_coding"
TAGS = '["ml-fundamentals", "knn", "implementation"]'
COMPANY_TAGS = '["Uber", "LinkedIn", "Pinterest"]'
PRIORITY = 1

DESCRIPTION = (
    "**K-Nearest Neighbors (KNN + Weighted)**: 从零实现 KNN 分类/回归, 包含 "
    "vanilla majority-vote 与两种 weighted 变体 (1/(d+epsilon) 与 Gaussian "
    "kernel w_i = exp(-d_i^2 / (2 sigma^2))). 显式覆盖 classification "
    "(weighted majority vote / argmax over weighted class probabilities) "
    "与 regression (weighted average y_hat = sum(w_i * y_i) / sum(w_i)) "
    "两种任务.\n\n"
    "核心步骤: (1) 计算 query 到所有训练点的欧氏距离; (2) np.argpartition 取 "
    "Top-K (O(N) 部分排序, 优于 argsort 的 O(N log N)); (3a) 分类: 投票 / "
    "加权投票; (3b) 回归: 平均 / 加权平均. 关键 ML 讨论点: K 选择 "
    "(cross-validation), tie-breaking, 1/(d+epsilon) 中 epsilon 的必要性, "
    "Gaussian 核 sigma 调节, curse of dimensionality, KD-tree / Ball-tree "
    "把单次 query 从 O(N*d) 降到平均 O(log N * d)."
)

NOTES = r"""## K-Nearest Neighbors (KNN + Weighted)

### 题目描述
从零实现 KNN, 同时支持:
1. **Vanilla KNN classifier**: 取最近 K 个邻居, 按多数投票 (majority vote) 决定类别.
2. **Weighted KNN** (TWO weighting schemes side-by-side):
   - **Inverse-distance**: $w_i = 1 / (d_i + \varepsilon)$, 其中 $\varepsilon$ 是
     一个很小的正数 (e.g. `1e-9`), 用以处理 query 与训练点重合 ($d_i = 0$) 的
     情况, 避免 `ZeroDivisionError`.
   - **Gaussian kernel**: $w_i = \exp(-d_i^2 / (2\sigma^2))$, 其中 $\sigma$ 是
     bandwidth 超参数, 控制权重随距离衰减的快慢.
3. **Classification AND regression** 均要覆盖:
   - 分类: weighted majority vote (对每个候选类别求 $\sum_{i: y_i = c} w_i$,
     取 argmax).
   - 回归: $\hat{y} = \sum_i w_i y_i / \sum_i w_i$.

### 核心代码

```python
import numpy as np
from typing import Literal, Optional

class KNN:
    # KNN classifier + regressor with vanilla and weighted variants.
    #
    # Design choices (探讨于 "关键要点"):
    #   - argpartition for top-K (O(N) avg) instead of argsort (O(N log N)).
    #   - 1 / (d + eps) with explicit small eps to handle d == 0.
    #   - Gaussian kernel w = exp(-d^2 / (2 sigma^2)) for smooth weighting.
    #   - Both classification (weighted majority vote) and regression
    #     (weighted average y_hat = sum w_i y_i / sum w_i) supported.

    def __init__(
        self,
        k: int = 5,
        task: Literal["classification", "regression"] = "classification",
        weighting: Literal["uniform", "inverse", "gaussian"] = "uniform",
        sigma: float = 1.0,
        epsilon: float = 1e-9,
    ):
        self.k = k
        self.task = task
        self.weighting = weighting
        self.sigma = sigma                    # bandwidth for Gaussian kernel
        self.epsilon = epsilon                # 1 / (d + eps) safety guard
        self.X_train: Optional[np.ndarray] = None    # shape (n_train, d)
        self.y_train: Optional[np.ndarray] = None    # shape (n_train,)

    # ---- Training (KNN is lazy: just store the data) ----

    def fit(self, X: np.ndarray, y: np.ndarray) -> "KNN":
        # KNN has NO training phase -- we just memorize (X, y).
        # All compute happens in predict() (instance-based / lazy learning).
        self.X_train, self.y_train = X, y
        return self

    # ---- Distance computation ----

    def _pairwise_euclidean(self, X_query: np.ndarray) -> np.ndarray:
        # Returns shape (n_query, n_train) Euclidean distance matrix.
        # Vectorized: ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b
        # Numerical guard: clip to >= 0 before sqrt (floating-point can
        # produce tiny negatives that crash sqrt).
        sq_query = np.sum(X_query ** 2, axis=1, keepdims=True)         # (nq, 1)
        sq_train = np.sum(self.X_train ** 2, axis=1, keepdims=True).T  # (1, nt)
        cross = X_query @ self.X_train.T                               # (nq, nt)
        sq_dist = np.maximum(sq_query + sq_train - 2 * cross, 0.0)
        return np.sqrt(sq_dist)

    # ---- Top-K selection ----

    def _topk_indices(self, distances: np.ndarray) -> np.ndarray:
        # For each query row, return indices of the K smallest distances.
        # np.argpartition is O(N) average, vs np.argsort O(N log N).
        # Note: argpartition does NOT sort the K returned indices among
        # themselves; that's fine for KNN since we only need the SET.
        return np.argpartition(distances, kth=self.k, axis=1)[:, : self.k]

    # ---- Weight computation (the three schemes) ----

    def _compute_weights(self, neighbor_dists: np.ndarray) -> np.ndarray:
        # neighbor_dists shape: (n_query, k). Returns same shape.
        if self.weighting == "uniform":
            return np.ones_like(neighbor_dists)
        if self.weighting == "inverse":
            # 1 / (d + epsilon) -- epsilon is CRITICAL: when query == a
            # training point, d == 0 -> 1/d = inf -> NaN downstream.
            # With epsilon, that point gets weight ~1/eps (very large but
            # finite), which is the correct semantics: "exact match
            # dominates". Without epsilon, you'd see RuntimeWarning and
            # silent NaN propagation in the weighted vote.
            return 1.0 / (neighbor_dists + self.epsilon)
        if self.weighting == "gaussian":
            # w = exp(-d^2 / (2 sigma^2)) -- standard RBF / Parzen kernel.
            # sigma controls bandwidth: small sigma -> very local (only
            # nearest neighbor matters); large sigma -> approaches
            # uniform. Tune via cross-validation on held-out fold.
            return np.exp(-(neighbor_dists ** 2) / (2.0 * self.sigma ** 2))
        raise ValueError(f"Unknown weighting: {self.weighting}")

    # ---- Prediction (classification + regression) ----

    def predict(self, X_query: np.ndarray) -> np.ndarray:
        distances = self._pairwise_euclidean(X_query)            # (nq, nt)
        topk_idx = self._topk_indices(distances)                  # (nq, k)
        # Gather the K nearest distances and labels for each query row.
        neighbor_dists = np.take_along_axis(distances, topk_idx, axis=1)
        neighbor_labels = self.y_train[topk_idx]                  # (nq, k)
        weights = self._compute_weights(neighbor_dists)           # (nq, k)

        if self.task == "regression":
            # Weighted average: y_hat = sum(w_i y_i) / sum(w_i)
            numerator = np.sum(weights * neighbor_labels, axis=1)
            denominator = np.sum(weights, axis=1)
            return numerator / denominator

        # Classification: weighted majority vote.
        # For each query, sum weights per candidate class -> argmax.
        # Ties broken by np.argmax's "first occurrence" rule, which under
        # numpy means the lower class label wins (deterministic).
        classes = np.unique(self.y_train)
        # class_scores shape: (n_query, n_classes)
        class_scores = np.zeros((X_query.shape[0], len(classes)))
        for j, c in enumerate(classes):
            mask = (neighbor_labels == c).astype(weights.dtype)
            class_scores[:, j] = np.sum(weights * mask, axis=1)
        return classes[np.argmax(class_scores, axis=1)]
```

### 关键要点

**1. Top-K selection: `argpartition` 优于 `argsort`**
- `np.argsort(distances)[:k]` 是 $O(N \log N)$, 完整排序后取前 K.
- `np.argpartition(distances, k)[:k]` 是平均 $O(N)$ -- 基于
  Quickselect, 只保证"第 K 位之前都比它小, 之后都比它大", 不保证前 K
  之间有序. KNN 只需要 SET, 不需要顺序, 所以是免费的加速.
- 量级对比: $N = 10^6$, K=5 时 argsort ~20M ops, argpartition ~1M ops.

**2. Why `1 / (d + epsilon)` instead of `1 / d`**
- 当 query 点恰好与某个训练点重合 ($d = 0$), `1 / d = inf` 触发
  RuntimeWarning, inf 在 sum 中累积成 NaN, 整个 query 的预测就废了.
- 加 $\varepsilon = 10^{-9}$ 之后: 重合点 $w \approx 10^9$ (远大于其它
  邻居的权重, 但有限), 这正是我们想要的 "exact match dominates" 语义.
- 不能用 try/except 兜底: 向量化代码里没有"单点报错"的概念, 一旦触发
  warning, 整个 batch 都会受 NaN 污染.

**3. Gaussian kernel 与 `sigma` 调节**
- $w_i = \exp(-d_i^2 / (2\sigma^2))$ 把"距离衰减"从 hard cutoff (top-K)
  改成连续平滑曲线.
- $\sigma \to 0$: 仅最近邻有非零权重, 退化为 1-NN.
- $\sigma \to \infty$: 所有邻居权重趋于 1, 退化为 uniform.
- 实战常用做法: $\sigma$ 设为 K 个邻居距离的中位数 (Silverman's rule
  的简化版), 或按 5-fold CV 搜索.

**4. Classification vs Regression 的统一框架**
- 二者共享: 距离计算, top-K 选择, 权重计算.
- 差异仅在最后一步:
  - 回归: $\hat{y} = \frac{\sum_i w_i y_i}{\sum_i w_i}$ (加权平均).
  - 分类: 对每个候选类 $c$ 计算 $\text{score}(c) = \sum_{i: y_i = c} w_i$,
    取 $\arg\max_c \text{score}(c)$ (加权投票).
- Vanilla majority vote 等价于 weighting='uniform' 下的加权投票, 因为所有
  $w_i = 1$, score 退化成"邻居中类别为 $c$ 的个数".

**5. Tie-breaking**
- 偶数 K 时分类容易平票. 处理方式 (优先级从高到低):
  - 用奇数 K (二分类时常见做法, 但多分类无效).
  - Inverse-distance / Gaussian weighted vote 几乎不可能完全平票 (实数权重).
  - 平票时取距离更近的那一类.
  - 退而求其次: 取标签编码更小的那一类 (`np.argmax` 的默认行为, 至少
    确定性, 不会随机).

### 面试追问

- **K 怎么选?** Cross-validation (典型 5-fold), 在 `[1, 3, 5, ..., sqrt(N)]`
  网格上扫描, 选 validation accuracy / RMSE 最优的. 太小 -> overfit
  (单点噪声主导); 太大 -> underfit (类别边界被过度平滑).
- **Curse of dimensionality**: 高维空间中所有点之间距离趋于相等 ("all
  points are equidistant"), KNN 失去判别力. 经验阈值: $d \gtrsim 10$ 时
  raw KNN 退化, 需要 PCA / LDA / autoencoder 先降维, 或换 metric learning
  (e.g. LMNN, NCA) 让"同类近, 异类远".
- **加速 query**: 朴素是 $O(N \cdot d)$ per query. KD-tree (低维 $d \le 20$)
  把单次 query 降到平均 $O(\log N \cdot d)$ -- 但 worst case 仍是 $O(N)$.
  Ball-tree 在中高维更稳. Ann (FAISS / HNSW / ScaNN) 用 approximate 方法
  在 $d \sim 100\text{--}1000$ 时把 query 压到亚秒级 (代价: 召回 < 100%).
- **Lazy vs eager learning**: KNN 是典型 lazy learner -- training 仅是
  存数据, 所有 compute 推迟到 predict. 对比: 决策树 / 神经网络是 eager,
  training 算完后 inference 极快. trade-off: KNN 适合训练数据频繁更新
  (在线学习无需重训), 但 inference 慢 + 内存占用大.
- **何时 vs. KMeans / GMM**: KNN 是 *supervised* (有 label), KMeans / GMM
  是 *unsupervised* clustering. 三者都用"距离"或"分布"概念, 但 KNN 不学
  原型 (prototype), 直接拿训练点本身做参考, 这也是为什么它对 outlier
  非常敏感 (一个错标的训练点会污染附近所有 query).
- **特征缩放**: 必须做! KNN 是基于欧氏距离, 不同尺度的特征 (e.g. 年龄
  vs. 收入) 会让大尺度特征主导距离. 标准做法: StandardScaler (zero-mean
  unit-variance) 或 MinMaxScaler. 这是 KNN/SVM/K-Means 等 distance-based
  模型的共同前置.

### 复杂度

- **训练**: $O(1)$ -- 只是保存指针, 不做任何计算.
- **预测 (单次 query, brute force)**: $O(N \cdot d)$ for 距离计算, $O(N)$
  for argpartition, $O(K)$ for vote/avg -> 总体 $O(N \cdot d)$.
- **预测 (KD-tree, $d \lesssim 20$)**: 平均 $O(\log N \cdot d)$,
  worst case $O(N \cdot d)$.
- **空间**: $O(N \cdot d)$ -- 必须存全部训练数据, 这是 KNN 的硬成本,
  也是它在大数据场景退役的主因 (相比之下 Logistic Regression 只需存
  $O(d)$ 的权重).
"""


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT id, description, notes FROM problems "
            "WHERE title = ? AND source = ?",
            (TITLE, SOURCE),
        ).fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        if row is None:
            cur = conn.execute(
                "INSERT INTO problems "
                "(title, description, notes, difficulty, pattern, "
                "category, tags, source, company_tags, priority, "
                "is_completed, comfort_level, description_source, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 'manual', ?)",
                (
                    TITLE,
                    DESCRIPTION,
                    NOTES,
                    DIFFICULTY,
                    PATTERN,
                    CATEGORY,
                    TAGS,
                    SOURCE,
                    COMPANY_TAGS,
                    PRIORITY,
                    now,
                ),
            )
            new_id = int(cur.lastrowid or 0)
            conn.commit()
            print(
                f"[INSERT] '{TITLE}' id={new_id} "
                f"description={len(DESCRIPTION)} notes={len(NOTES)} chars"
            )
            return 0

        pid, old_desc, old_notes = row
        old_desc = old_desc or ""
        old_notes = old_notes or ""

        if old_desc == DESCRIPTION and old_notes == NOTES:
            print(
                f"[SKIP] id={pid} '{TITLE}' description+notes byte-equal "
                f"(desc={len(old_desc)} notes={len(old_notes)})"
            )
            return 0

        conn.execute(
            "UPDATE problems "
            "SET description = ?, notes = ?, difficulty = ?, pattern = ?, "
            "    category = ?, tags = ?, company_tags = ?, priority = ? "
            "WHERE id = ?",
            (
                DESCRIPTION,
                NOTES,
                DIFFICULTY,
                PATTERN,
                CATEGORY,
                TAGS,
                COMPANY_TAGS,
                PRIORITY,
                pid,
            ),
        )
        conn.commit()
        print(
            f"[UPDATE] id={pid} '{TITLE}' "
            f"desc {len(old_desc)} -> {len(DESCRIPTION)}, "
            f"notes {len(old_notes)} -> {len(NOTES)} chars"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
