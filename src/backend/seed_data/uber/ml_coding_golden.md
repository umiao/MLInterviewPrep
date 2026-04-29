# Uber ML Coding Golden Answer 集合 (Staff-Level)

> **Source**: 2026-04 Uber VO 复盘整理 (Round 2 ML Coding 4 题 Staff-level Golden Answers)
> **Scope**: 4 道核心 ML coding 题 — Geometric Median, K-Means (numpy-only), Linear Regression from scratch, Logistic Regression from scratch
> **Style**: 中文叙述 + 英文术语 (English term first, 中文 in parens for first occurrence). 每题结构: 题目 → Clarify → Brute-force → Optimal → Trade-off → Follow-up scaling → 行业黑话.
> **Anchors**: 每个 H2 都用 kebab-case stable HTML id, 供 T-P0-632 的 deep-link 使用 (`/docs/<doc-id>#<anchor>`).

---

## 目录 (Table of Contents)

1. [几何中位数 (Geometric Median)](#geometric-median)
2. [K-Means (numpy-only)](#kmeans-numpy)
3. [线性回归 from scratch (Linear Regression)](#linear-regression-from-scratch)
4. [逻辑回归 from scratch (Logistic Regression)](#logistic-regression-from-scratch)
5. [跨题通用面试要点 (Cross-cutting Interview Tactics)](#cross-cutting-tactics)
6. [Audit-Discovered 辅助卡片 (Depth-2 Auxiliary Cards)](#audit-aux-cards)
   - 6.1 [Multi-treatment Uplift Modeling 直觉卡](#uplift-meta-learners)
   - 6.2 [Lagrangian Relaxation 伪代码卡](#lagrangian-relaxation)

---

<h2 id="geometric-median">1. 几何中位数 (Geometric Median)</h2>

### 1.1 题目 (Problem)

给定 $n$ 个 $d$ 维点 $\{p_1, p_2, \ldots, p_n\} \subset \mathbb{R}^d$, 求一个点 $x^* \in \mathbb{R}^d$ 使得**到所有点的 L2 距离之和最小**:

$$x^* = \arg\min_{x \in \mathbb{R}^d} \sum_{i=1}^{n} \lVert x - p_i \rVert_2$$

注意是**距离之和**, 不是**距离平方之和** (后者的 closed-form 解就是质心 mean). 几何中位数没有 closed-form, 必须迭代求解.

**面试常踩雷点**: 候选人脱口说 "取 mean 就行了" — 这是 L2² 的最优解, 不是 L2 的最优解. **mean ≠ argmin Σ‖x−pᵢ‖**.

LeetCode 接近的题: 462 *Minimum Moves to Equal Array Elements II* (1D 版本, 答案是 median). 高维 d ≥ 2 没有 LC 直接对应, Uber/Lyft 类会问.

### 1.2 Clarify (澄清问题)

VO 实战 clarify 清单:
- 维度 $d$? (一维 → median; ≥ 2 维 → 几何中位数)
- 点数 $n$ 量级? ($n \le 10^4$ → Weiszfeld 直接跑; $n \ge 10^7$ → 需要 sub-sampling / coreset)
- 是否允许返回**近似解**? 数值容差 $\epsilon$ 多少?
- 输入是否含**重合点** ($x = p_i$ 是 degenerate case, 梯度未定义)?
- 是否带权重 (weighted geometric median)?

### 1.3 Brute-force (暴力 baseline)

直接做 **gradient descent (梯度下降, GD)** 在目标函数 $f(x) = \sum_i \lVert x - p_i \rVert_2$ 上. 梯度为:

$$\nabla f(x) = \sum_{i=1}^{n} \frac{x - p_i}{\lVert x - p_i \rVert_2}$$

学习率 $\eta$ 调参, 复杂度 $O(\text{iter} \cdot n \cdot d)$. 缺点: 学习率难选, 收敛慢, 在 $x = p_i$ 处梯度 blow up.

### 1.4 Optimal — Weiszfeld 迭代

**Weiszfeld algorithm (魏斯菲尔德算法, 1937)** 是几何中位数的 canonical 解法. 关键 insight: 把梯度 = 0 的不动点方程写成 fixed-point iteration:

$$x^{(t+1)} = \frac{\sum_{i=1}^{n} \frac{p_i}{\lVert x^{(t)} - p_i \rVert_2}}{\sum_{i=1}^{n} \frac{1}{\lVert x^{(t)} - p_i \rVert_2}}$$

直观理解: 下一步 $x$ 是所有 $p_i$ 的**加权平均**, 权重 = 当前距离的倒数 (越近的点权重越大). 这是一个 IRLS (Iteratively Reweighted Least Squares) 形式.

**收敛性**: 在非 degenerate 情况下保证收敛到全局最优 (目标函数是凸的, 因为是凸函数之和). 在 degenerate case ($x^{(t)}$ 落在某个 $p_i$ 上) 需要特殊处理 — 加 $\epsilon$ smoothing.

```python
import numpy as np

def geometric_median(
    points: np.ndarray,
    eps: float = 1e-5,
    max_iter: int = 200,
    tol: float = 1e-7,
) -> np.ndarray:
    """Weiszfeld iteration for geometric median.

    points: (n, d) array
    eps:    smoothing to avoid div-by-zero when x lands on a point
    """
    x = points.mean(axis=0)  # init at centroid
    for _ in range(max_iter):
        diff = points - x                           # (n, d)
        dists = np.linalg.norm(diff, axis=1)        # (n,)
        weights = 1.0 / np.maximum(dists, eps)      # (n,)
        x_new = (points * weights[:, None]).sum(axis=0) / weights.sum()
        if np.linalg.norm(x_new - x) < tol:
            return x_new
        x = x_new
    return x


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    pts = rng.normal(size=(100, 2))
    pts[0] = [10.0, 10.0]   # outlier
    print("mean:           ", pts.mean(axis=0))
    print("geometric median:", geometric_median(pts))
```

跑出来 mean 被 outlier 拉偏, geometric median 鲁棒.

**复杂度**: 每次迭代 $O(n \cdot d)$, 通常 50–200 步收敛 → 总 $O(\text{iter} \cdot n \cdot d)$.

### 1.5 Trade-off (权衡)

| 方法 | 优点 | 缺点 |
|---|---|---|
| Mean (centroid) | $O(nd)$ closed-form | 解的是 L2² 不是 L2; 不鲁棒于 outlier |
| GD on $f(x)$ | 通用 | 学习率敏感, degenerate case 会 blow up |
| **Weiszfeld** | 无超参, 收敛证明, IRLS 解释清晰 | degenerate case 需 smoothing; 高维收敛慢 |
| Smoothed L-BFGS | quasi-Newton 加速 | 实现复杂, sklearn 没现成 |
| Coordinate descent | 容易并行化 | 收敛速率与 Weiszfeld 类似 |

**鲁棒性**: 几何中位数是 **breakdown point = 50%** 的 robust estimator (要污染一半以上的点才能拉偏), 而 mean 的 breakdown point = 0%. 这正是 Uber 用它处理 GPS noise / driver location aggregation 的原因.

### 1.6 Follow-up scaling (大规模)

面试官常问: "$n = 10^9$ 怎么办?"

**思路 1 — Sub-sampling**: 随机采样 $m \ll n$ 个点估计 geometric median. 误差 $O(1/\sqrt{m})$, 实践中 $m = 10^4$ 足够.

**思路 2 — Coreset**: 构造一个加权小集合 $S$ 使得 $\sum_{p \in S} w_p \lVert x - p \rVert \approx \sum_{i} \lVert x - p_i \rVert$ for all $x$. 经典构造: Feldman & Langberg 2011, $|S| = O(d / \epsilon^2)$.

**思路 3 — Distributed / streaming**:
- 把数据分到 $k$ 台机器, 每台算一个 local geometric median, 再对 $k$ 个 median **取 median of medians** (geometric median of geometric medians, GM-of-GM). 误差有理论 bound, 是 streaming 标准做法.
- Mini-batch SGD on $f(x)$ 也可, 学习率用 inverse-distance 自适应 (Online Weiszfeld).

**思路 4 — GPU / tensorize**: Weiszfeld 全 vectorized, 直接搬到 PyTorch / JAX, 单卡跑 $n = 10^7$ 在毫秒级.

### 1.7 行业黑话 (Industry idioms)

- "**取 median 而不是 mean**" 是 robust statistics 的招牌动作; 在 Uber 这种 heavy-tail (waiting time, surge, ETA error) 场景几乎必备.
- "**Breakdown point**" — 一个 estimator 在多少比例污染下还能撑住. mean = 0%, median = 50%, geometric median = 50%, trimmed mean (10%) = 10%.
- "**IRLS (Iteratively Reweighted Least Squares)**" — Weiszfeld, robust regression (Huber), GLM 都是这一族.
- 面试官会用 "median 不可微所以怎么做凸优化?" 钓你 — 回 "目标函数本身凸但不可微于 $x = p_i$, 用 sub-gradient 或 smoothed L1 (Huber-like) 就行".

---

<h2 id="kmeans-numpy">2. K-Means (numpy-only)</h2>

### 2.1 题目 (Problem)

实现 **K-Means clustering (K均值聚类)**, **只允许使用 numpy**, 不允许 sklearn / scipy. 输入: $X \in \mathbb{R}^{n \times d}$, 簇数 $k$. 输出: cluster assignment $\{0, 1, \ldots, k-1\}^n$ 和 centroids $C \in \mathbb{R}^{k \times d}$.

**对应 problems table**: id=1064 [db://1064] *K-Means Pure Python Implementation (K-Means++)*.

### 2.2 Clarify

- $n$, $d$, $k$ 量级 (决定是否能 batch)?
- **初始化策略**: 随机 / K-Means++?
- **停止条件**: max iter / centroid shift < tol / SSE 收敛 / labels 无变化 — 用哪个 (最好 OR 多个组合)?
- **空 cluster 处理**: 重启 / 从最远点取 / 删除?
- **distance metric**: Euclidean only, 还是 Mahalanobis / cosine?
- **复现性**: 随机种子 fixed?

### 2.3 Brute-force (Lloyd's algorithm)

经典 Lloyd 迭代:
1. 随机初始化 $k$ 个 centroids.
2. **Assignment step**: 每个点分配到最近 centroid.
3. **Update step**: 每个 cluster 的 centroid = 该 cluster 内点的均值.
4. 重复 2–3 直到 centroids 不动.

复杂度 $O(n \cdot k \cdot d)$ per iter. 通常 $\le 50$ iter 收敛.

### 2.4 Optimal — vectorized + K-Means++

**K-Means++ initialization**: 第一个 centroid 随机选; 后续每个 centroid 按 $D(x)^2$ 加权概率采样, 其中 $D(x)$ 是 $x$ 到最近已选 centroid 的距离. 这把"坏初值"的概率从 random init 的 $\Theta(\log k)$ 期望 SSE-blowup 压到 $O(\log k)$ 倍最优.

```python
import numpy as np


def _pairwise_sq_dist(X: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Vectorized squared Euclidean distance, returns (n, k)."""
    # ||x - c||^2 = ||x||^2 + ||c||^2 - 2 x·c
    x_sq = (X * X).sum(axis=1, keepdims=True)         # (n, 1)
    c_sq = (C * C).sum(axis=1)                        # (k,)
    cross = X @ C.T                                    # (n, k)
    return x_sq + c_sq - 2.0 * cross


def kmeans_pp_init(X: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n = X.shape[0]
    centroids = np.empty((k, X.shape[1]), dtype=X.dtype)
    centroids[0] = X[rng.integers(n)]
    closest_sq = _pairwise_sq_dist(X, centroids[:1]).ravel()
    for j in range(1, k):
        probs = closest_sq / closest_sq.sum()
        idx = rng.choice(n, p=probs)
        centroids[j] = X[idx]
        new_d = _pairwise_sq_dist(X, centroids[j:j + 1]).ravel()
        closest_sq = np.minimum(closest_sq, new_d)
    return centroids


def kmeans(
    X: np.ndarray,
    k: int,
    max_iter: int = 100,
    tol: float = 1e-4,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Returns (labels, centroids, final_sse)."""
    rng = np.random.default_rng(seed)
    C = kmeans_pp_init(X, k, rng)
    prev_labels = np.full(X.shape[0], -1)
    for _ in range(max_iter):
        d2 = _pairwise_sq_dist(X, C)            # (n, k)
        labels = d2.argmin(axis=1)              # (n,)
        if np.array_equal(labels, prev_labels):
            break
        C_new = np.empty_like(C)
        for j in range(k):
            mask = labels == j
            if mask.any():
                C_new[j] = X[mask].mean(axis=0)
            else:
                # empty cluster: re-init from farthest point
                far_idx = d2.min(axis=1).argmax()
                C_new[j] = X[far_idx]
        if np.linalg.norm(C_new - C) < tol:
            C = C_new
            break
        C, prev_labels = C_new, labels
    sse = float(_pairwise_sq_dist(X, C)[np.arange(X.shape[0]), labels].sum())
    return labels, C, sse


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    X = np.vstack([
        rng.normal(loc=[0, 0], size=(100, 2)),
        rng.normal(loc=[5, 5], size=(100, 2)),
        rng.normal(loc=[0, 5], size=(100, 2)),
    ])
    labels, C, sse = kmeans(X, k=3)
    print("centroids:", C)
    print("SSE:     ", sse)
```

**关键 vectorization 点**:
- `_pairwise_sq_dist` 用展开式 $\lVert x-c \rVert^2 = \lVert x \rVert^2 + \lVert c \rVert^2 - 2 x \cdot c$, 避免 broadcast `(n,d)-(k,d)` 产生 `(n,k,d)` 中间张量 (内存 $O(nkd)$ 退化为 $O(nk)$).
- assignment 用 `argmin(axis=1)`, 完全 vectorized.
- empty cluster: 不 silently 跳过 — 一定要重启, 不然下次 iter 会 NaN.

### 2.5 Trade-off

| 选择 | 优 | 劣 |
|---|---|---|
| Random init | 简单 | 期望 SSE 比最优差 $\Theta(\log k)$ |
| **K-Means++** | $O(\log k)$-competitive 期望 SSE | 初始化 $O(nk)$, 但常数小 |
| Mini-batch K-Means | 大数据可扩展 | 收敛轻微抖动 |
| Bisecting K-Means | 树状, 自适应 $k$ | 实现复杂 |
| Gaussian Mixture (EM) | soft assignment + cov | 慢 ~10x, 易 local optima |

**K 怎么选**: Elbow method (SSE vs k 拐点); silhouette score; Gap statistic; X-means (BIC). 实战常以下游业务指标 (recall@K / latency) 反向选 $k$.

### 2.6 Follow-up scaling

面试官递进式拷问:

**Q: "$n = 10^9$ 不能放进单机内存怎么办?"** → **mini-batch K-Means**: 每次只用一个 mini-batch 更新 centroid (online update), 在 $X$ 上做 streaming pass. sklearn 的 `MiniBatchKMeans` 就是这个.

**Q: "Distributed?"** → 把数据分 partition, **map**: 每个 partition 计算 local sum + count per cluster; **reduce**: 全局合并求新 centroid. 这是 Spark MLlib K-Means 的实现. 通信开销 $O(k \cdot d)$ per iter (centroids 广播), 不正比于 $n$.

**Q: "$k = 10^6$ (extreme large k, e.g. embedding clustering)?"** → 不能再 brute-force assignment. 用 **ANN (Approximate Nearest Neighbor) index** (HNSW / IVF) 做 assignment step; centroid update 用 inverted index 增量维护. 实践 → **FAISS** 的 IVF-PQ, 这是百万级 codebook 的标配.

**Q: "Streaming, 数据来一条处理一条?"** → **online K-Means / sequential K-Means**: 用 stochastic approximation, $C_j \leftarrow C_j + \eta_t (x - C_j)$ where $\eta_t = 1/n_j$. 与 SGD 同理.

**Q: "怎么并行化?"** → assignment 完全 data-parallel; update 是 gather + reduce. GPU 上 $O(n \cdot k \cdot d)$ matmul 直接跑, FAISS GPU 单卡能 cluster 1B 向量到 $k = 10^6$ 在小时级.

### 2.7 行业黑话

- "**K-Means 不鲁棒于 outlier**" → K-Medoids / K-Medians 替代 (前者用 medoid 当中心, 后者用每维 median).
- "**球形假设**" — K-Means 隐含 cluster 是各向同性 (isotropic) 高斯; 椭圆 cluster 用 GMM, 非凸 cluster 用 spectral / DBSCAN.
- "**Lloyd's algorithm 是 EM 的特例**" — hard EM on isotropic equal-variance GMM. 知道这个等价性会显得 Staff-level.
- "**Curse of dimensionality**" — $d$ 大时所有点的距离趋近相同, K-Means 失效. 通常先 PCA / autoencoder 降到 $d \le 50$ 再聚类.

---

<h2 id="linear-regression-from-scratch">3. 线性回归 from scratch (Linear Regression)</h2>

### 3.1 题目

实现 **Linear Regression (线性回归)**, 不用 sklearn. 必须**端到端跑通**: 生成 toy data → train → 预测 → 打印 loss.

**要求**: 至少给出 closed-form (normal equation) 和 gradient descent 两种解法; 加 L2 regularization (Ridge); 处理数值稳定性.

### 3.2 Clarify

- 输入是否带 intercept (bias term)? (标准做法: 把 $X$ augment 一列全 1)
- 是否 standardize features? (GD 收敛速度强相关, normal equation 不影响)
- $n$ 和 $d$ 量级? ($d^3$ 的 normal equation 在 $d > 10^4$ 不可行)
- regularization $\lambda$ 给定还是要 tune?
- 评估指标: MSE / RMSE / R²?

### 3.3 Brute-force — Closed-form (Normal Equation)

模型: $y = X\beta + \epsilon$, $\beta \in \mathbb{R}^d$.

OLS (Ordinary Least Squares) 目标:

$$\min_\beta \lVert X\beta - y \rVert_2^2$$

求导设 0:

$$\hat\beta = (X^\top X)^{-1} X^\top y$$

加 L2 reg (Ridge) 后: $\hat\beta = (X^\top X + \lambda I)^{-1} X^\top y$, 这也保证 $X^\top X$ 即使 singular 时也可逆.

**复杂度**: $O(nd^2 + d^3)$. $d \le 10^3$ 直接干; 否则换 GD/SGD.

### 3.4 Optimal — closed-form via QR / SVD + GD baseline

**数值稳定性陷阱**: 直接 `np.linalg.inv(X.T @ X)` 会放大 condition number 平方. 正确做法用 **QR decomposition** 或 **SVD**.

```python
import numpy as np


def add_intercept(X: np.ndarray) -> np.ndarray:
    return np.hstack([np.ones((X.shape[0], 1)), X])


def linreg_normal_eq(X: np.ndarray, y: np.ndarray, l2: float = 0.0) -> np.ndarray:
    """Solve via Cholesky on (X'X + lambda I); stable for moderate d."""
    Xb = add_intercept(X)
    d = Xb.shape[1]
    A = Xb.T @ Xb + l2 * np.eye(d)
    b = Xb.T @ y
    return np.linalg.solve(A, b)


def linreg_qr(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Solve via QR — best numerical stability for ill-conditioned X."""
    Xb = add_intercept(X)
    Q, R = np.linalg.qr(Xb)
    return np.linalg.solve(R, Q.T @ y)


def linreg_gd(
    X: np.ndarray,
    y: np.ndarray,
    lr: float = 0.01,
    epochs: int = 1000,
    l2: float = 0.0,
    verbose: bool = False,
) -> tuple[np.ndarray, list[float]]:
    Xb = add_intercept(X)
    n, d = Xb.shape
    beta = np.zeros(d)
    losses = []
    for ep in range(epochs):
        pred = Xb @ beta
        err = pred - y
        grad = (2.0 / n) * (Xb.T @ err) + 2.0 * l2 * beta
        beta -= lr * grad
        loss = float((err ** 2).mean()) + l2 * float(beta @ beta)
        losses.append(loss)
        if verbose and ep % 100 == 0:
            print(f"epoch {ep:4d}  mse={loss:.6f}")
    return beta, losses


def predict(X: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return add_intercept(X) @ beta


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n, d = 200, 3
    X = rng.normal(size=(n, d))
    true_beta = np.array([2.0, -1.5, 0.7, 3.0])  # bias=2, weights=[-1.5,0.7,3.0]
    y = add_intercept(X) @ true_beta + rng.normal(scale=0.5, size=n)

    beta_ne = linreg_normal_eq(X, y)
    beta_qr = linreg_qr(X, y)
    beta_gd, losses = linreg_gd(X, y, lr=0.01, epochs=1000, verbose=True)

    print("true beta :", true_beta)
    print("normal eq :", beta_ne)
    print("QR        :", beta_qr)
    print("GD        :", beta_gd)
    print("MSE (test):", float(((predict(X, beta_qr) - y) ** 2).mean()))
```

**端到端验证**: 三种方法应该收敛到几乎相同的 $\beta$, 而且接近 `true_beta`.

### 3.5 Trade-off

| 方法 | 适用 | 优 | 劣 |
|---|---|---|---|
| **Normal eq (Cholesky)** | $d \le 10^3$ | 一步搞定; 无超参 | $O(d^3)$ |
| **QR / SVD** | $d \le 10^4$, 病态 | 数值最稳 | 略慢 (常数大) |
| **GD / SGD** | $d \gg 10^3$ 或 streaming | scale 友好 | 学习率/收敛要 tune |
| **L-BFGS** | mid $d$ | 二阶, 收敛快 | 实现复杂 |
| **CG (Conjugate Gradient)** | sparse $X$ | 不显式存 $X^\top X$ | 病态时慢 |

**Ridge ($L_2$) vs Lasso ($L_1$)**: Ridge 解析解, 解稀缺缩放; Lasso 用 coordinate descent / proximal, 产生稀疏解 (feature selection). Elastic Net 折中.

**多重共线性**: $X^\top X$ 接近 singular → $\beta$ 方差爆炸. 用 Ridge 直接修复 (加 $\lambda I$); 或先 PCA 降维.

### 3.6 Follow-up scaling

**Q: "$n = 10^9$, $d = 10^6$, sparse?"** → **CG on $X^\top X \beta = X^\top y$**, 不显式存矩阵; 用 sparse-matvec. Spark MLlib 的 LinearRegression 走这条路.

**Q: "Streaming / online?"** → **RLS (Recursive Least Squares)**: 来一条样本就更新 $\beta$ 和 $P = (X^\top X)^{-1}$. 用 Sherman-Morrison 公式做秩 1 更新, 复杂度 $O(d^2)$ per sample, 比重训快 $O(n)$ 倍.

**Q: "Distributed?"** → **map-reduce**: 各 partition 计算 local $X_i^\top X_i$ 和 $X_i^\top y_i$, reduce sum 得到全局; 再单机 solve. 通信 $O(d^2)$ per iter (与 $n$ 无关).

**Q: "Heteroscedastic noise?"** → **WLS (Weighted Least Squares)**: 用方差倒数加权, $\hat\beta = (X^\top W X)^{-1} X^\top W y$.

**Q: "outlier 多?"** → **robust regression** (Huber loss / RANSAC); Huber 用 IRLS 解, 与 Weiszfeld 同族.

### 3.7 行业黑话

- "**Bias-variance trade-off**" — Ridge 增大 bias 换 variance 减少, MSE 在中间最小.
- "**Condition number**" — $\kappa(X^\top X) = \kappa(X)^2$, 这就是为什么病态时**不能**直接 invert.
- "**Sufficient statistics**" — 线性回归在 distributed 训练下只需传 $(X^\top X, X^\top y)$, 不传原数据.
- "**Frequentist 和 Bayesian 视角**" — Ridge 等价于 Gaussian prior on $\beta$ 的 MAP; Lasso 是 Laplace prior.

---

<h2 id="logistic-regression-from-scratch">4. 逻辑回归 from scratch (Logistic Regression)</h2>

### 4.1 题目

实现 **Logistic Regression (逻辑回归, LR)** 二分类版本, 不用 sklearn. 端到端跑通: 生成 toy data → fit (GD/SGD) → 预测 prob → 评估 accuracy/AUC.

### 4.2 Clarify

- 二分类还是多分类 (multinomial / softmax)?
- L1 / L2 / 无 reg?
- 优化器: GD / SGD / Newton (IRLS) / L-BFGS?
- 类别不平衡? (需要 class_weight 或 reweighted loss)
- 评估: accuracy / precision / recall / F1 / AUC / log-loss?

### 4.3 Brute-force — vanilla GD on log-loss

模型 (sigmoid):

$$p(y=1 \mid x) = \sigma(x^\top \beta) = \frac{1}{1 + e^{-x^\top \beta}}$$

**Cross-entropy / log-loss** (负对数似然):

$$\mathcal{L}(\beta) = -\frac{1}{n} \sum_{i=1}^{n} \left[ y_i \log \sigma(x_i^\top \beta) + (1 - y_i) \log(1 - \sigma(x_i^\top \beta)) \right]$$

**梯度** (推导关键: $\sigma'(z) = \sigma(z)(1-\sigma(z))$, 然后 chain rule 神奇地化简成 $(\hat p - y) x$):

$$\nabla_\beta \mathcal{L} = \frac{1}{n} X^\top (\sigma(X\beta) - y)$$

形式与线性回归 GD 几乎一样, 只是 $\hat y = X\beta$ 换成 $\hat y = \sigma(X\beta)$.

### 4.4 Optimal — GD + numerical stable sigmoid + L2 reg

**数值陷阱**: `1 / (1 + exp(-z))` 当 $z \ll 0$ 时 `exp(-z)` overflow → inf → NaN. 必须用 stable 版:

```python
def sigmoid(z: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid."""
    out = np.empty_like(z, dtype=np.float64)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out
```

类似地 `log(sigmoid(z))` 该用 `-log1p(exp(-z))` (`np.logaddexp(0, -z)` 取负).

完整实现:

```python
import numpy as np


def add_intercept(X: np.ndarray) -> np.ndarray:
    return np.hstack([np.ones((X.shape[0], 1)), X])


def sigmoid(z: np.ndarray) -> np.ndarray:
    out = np.empty_like(z, dtype=np.float64)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def log_loss(y_true: np.ndarray, p: np.ndarray, eps: float = 1e-12) -> float:
    p = np.clip(p, eps, 1.0 - eps)
    return float(-(y_true * np.log(p) + (1 - y_true) * np.log(1 - p)).mean())


def logreg_gd(
    X: np.ndarray,
    y: np.ndarray,
    lr: float = 0.1,
    epochs: int = 1000,
    l2: float = 0.0,
    verbose: bool = False,
) -> tuple[np.ndarray, list[float]]:
    Xb = add_intercept(X)
    n, d = Xb.shape
    beta = np.zeros(d)
    losses = []
    for ep in range(epochs):
        z = Xb @ beta
        p = sigmoid(z)
        # gradient: (1/n) X.T (p - y) + 2 l2 beta (don't reg the bias term)
        grad = (Xb.T @ (p - y)) / n
        if l2 > 0:
            grad[1:] += 2.0 * l2 * beta[1:]
        beta -= lr * grad
        loss = log_loss(y, p)
        if l2 > 0:
            loss += l2 * float(beta[1:] @ beta[1:])
        losses.append(loss)
        if verbose and ep % 100 == 0:
            print(f"epoch {ep:4d}  loss={loss:.6f}")
    return beta, losses


def predict_proba(X: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return sigmoid(add_intercept(X) @ beta)


def predict(X: np.ndarray, beta: np.ndarray, thr: float = 0.5) -> np.ndarray:
    return (predict_proba(X, beta) >= thr).astype(int)


def auc(y_true: np.ndarray, p: np.ndarray) -> float:
    """Mann-Whitney U / Wilcoxon ROC-AUC, no sklearn."""
    pos = p[y_true == 1]
    neg = p[y_true == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # rank approach: count #(pos > neg) + 0.5 * #(pos == neg)
    all_scores = np.concatenate([pos, neg])
    all_labels = np.concatenate([np.ones_like(pos), np.zeros_like(neg)])
    order = np.argsort(all_scores, kind="stable")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(all_scores) + 1)
    # average ranks for ties
    sorted_scores = all_scores[order]
    i = 0
    while i < len(sorted_scores):
        j = i
        while j + 1 < len(sorted_scores) and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            ranks[order[i:j + 1]] = avg
        i = j + 1
    n_pos = len(pos)
    n_neg = len(neg)
    sum_ranks_pos = ranks[all_labels == 1].sum()
    return float((sum_ranks_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n, d = 500, 4
    X = rng.normal(size=(n, d))
    true_beta = np.array([0.5, 1.5, -2.0, 0.7, 1.0])  # incl. bias
    z_true = add_intercept(X) @ true_beta
    p_true = 1.0 / (1.0 + np.exp(-z_true))
    y = (rng.uniform(size=n) < p_true).astype(int)

    beta, losses = logreg_gd(X, y, lr=0.1, epochs=1000, l2=1e-3, verbose=True)
    p = predict_proba(X, beta)
    yhat = (p >= 0.5).astype(int)
    print("learned beta:", beta)
    print("acc :", float((yhat == y).mean()))
    print("auc :", auc(y, p))
```

跑出来 acc 通常 0.85+, AUC 0.92+.

### 4.5 Trade-off

| 优化器 | 适合 | 注意 |
|---|---|---|
| **GD / SGD** | 数据大 / online | 学习率难 tune; 加 momentum / Adam |
| **Newton (IRLS)** | $d$ 中等 ($\le 10^3$) | 用 Hessian $X^\top \text{diag}(p(1-p)) X$, $O(nd^2 + d^3)$ per iter; sklearn 默认 |
| **L-BFGS** | $d$ 大但内存够 | 最常用 baseline |
| **SAG / SAGA** | $n$ 大且 strongly convex | 线性收敛, sklearn `solver='saga'` |

**为啥不用 MSE loss?** 因为 sigmoid + MSE 是非凸的, 而 sigmoid + log-loss 是 convex (这是 GLM 选择 link function + canonical loss 的根本原因).

**Decision boundary**: $x^\top \beta = 0$ 是 hyperplane (线性边界). 想要非线性 → kernel trick, polynomial features, 或上 NN.

**Class imbalance**:
- **class_weight**: 在 loss 里乘 $w_y$, 等价于 oversampling minority.
- **threshold tuning**: 不一定 0.5 — 用 PR / F1 曲线选最优 threshold.
- **focal loss**: 对 well-classified 样本降权, 用于 detection.

### 4.6 Follow-up scaling

**Q: "百万样本 + 千维 sparse feature?"** → **L-BFGS + sparse matvec**, 或 **SGD + L2 reg + 早停**. sklearn `LogisticRegression(solver='saga', penalty='l1')` 支持 sparse.

**Q: "Multi-class?"** → **softmax (multinomial)** 或 **one-vs-rest (OvR)**. softmax 在概率校准上更好; OvR 训练更并行但 prob 不归一化.

**Q: "Distributed?"** → 同 linear regression: 各 partition 计算 local gradient, reduce sum, broadcast 新 $\beta$. 标准 parameter-server 工作流.

**Q: "Calibration 不准?"** → log-loss optimal 不保证概率校准 (尤其在类别不平衡 + L2 reg). 用 **Platt scaling** 或 **isotonic regression** 二阶段校准.

**Q: "Online learning?"** → **FTRL-Proximal (Follow-The-Regularized-Leader)** — Google 大规模 CTR 模型 (Ad click) 标配. 维持 per-coord $z, n$ 状态, 支持 L1 + L2, online sparse.

### 4.7 行业黑话

- "**LR 是 GLM (Generalized Linear Model) 的 logit link 实例**" — 知道这个会显得 GLM 思维.
- "**Cross-entropy = NLL of Bernoulli**" — 这两个名字是同一回事, 别在面试官提一个时表现成另一个不认识.
- "**Coefficient 解读**: $\beta_j$ = 1 unit increase in $x_j$ → log-odds 加 $\beta_j$, odds-ratio 乘 $e^{\beta_j}$." 这是 LR 在医疗 / 风控领域 still beats NN 的核心原因 — 可解释.
- "**Wald test / likelihood-ratio test**" — coefficient 显著性检验. 在金融 / 保险类公司是必考点.
- "**Calibration vs Discrimination**" — AUC 衡量 ranking 能力 (discrimination), Brier score / reliability diagram 衡量校准 (calibration). 一个模型 AUC 高不代表 prob 准.

---

<h2 id="cross-cutting-tactics">5. 跨题通用面试要点 (Cross-cutting Interview Tactics)</h2>

### 5.1 这 4 题的共同面试结构

Uber VO ML coding 不是纯 LeetCode — 你写出来还要**讲明白**. 推荐 talk track:

1. **Restate** — 用自己的话复述题, 暴露隐含假设. (3 mins)
2. **Clarify** — 维度 / 量级 / 数值容差 / I/O 格式. (2 mins)
3. **Brute-force first** — 先给 $O(\cdot)$ 最差但正确的方案, 给面试官信号 "我不会被 stuck on perfection". (5 mins)
4. **Optimize** — 一步一步加 vectorization / better init / regularization. 写代码同时口述 trade-off. (15 mins)
5. **Run** — 必须 actual `python file.py`, 打印 loss / accuracy / output. 面试官会要求"跑一下" — 没跑过的代码不算交付. (5 mins)
6. **Scaling Q&A** — sub-sampling, distributed, streaming, GPU. (10 mins)
7. **Trade-off Q&A** — 数值稳定性, init 选择, regularization, 评估指标. (10 mins)

### 5.2 共同的数值稳定性陷阱

| 陷阱 | 错的写法 | 对的写法 |
|---|---|---|
| sigmoid overflow | `1/(1+np.exp(-z))` | branch by sign (见上) |
| log(sigmoid) | `np.log(sigmoid(z))` | `-np.logaddexp(0, -z)` |
| inv(X.T @ X) | `np.linalg.inv(X.T @ X)` | `np.linalg.solve(...)` 或 QR |
| pairwise dist | `((X[:,None]-C[None])**2).sum(-1)` | $\lVert x \rVert^2 + \lVert c \rVert^2 - 2 x \cdot c$ |
| div by 0 in Weiszfeld | `1/dist` | `1/np.maximum(dist, eps)` |
| empty cluster in K-Means | `X[mask].mean()` 当 mask 全 False | reinit from farthest point |
| log(0) in log-loss | 直接传 `p=0` | `np.clip(p, eps, 1-eps)` |

### 5.3 共同的 follow-up scaling 套路

记住这个 4-tier 答题模板:

1. **In-memory single machine** (默认, $n \le 10^6$): 直接 numpy vectorize.
2. **Mini-batch / sub-sampling** ($n \le 10^9$): 用 subset 估计, 或 mini-batch SGD.
3. **Distributed** ($n \ge 10^{10}$): map-reduce on sufficient statistics ($X^\top X$, gradient sums); 通信复杂度 $\propto d$ 不 $\propto n$.
4. **GPU / streaming**: tensor 化全套, 或 online update with stochastic approximation.

### 5.4 共同的"行业黑话"开关词

讲到这些词, 面试官会 nod 或在 hire packet 里写 "showed Staff-level depth":

- breakdown point, robust statistic, IRLS
- condition number, numerical stability, $\kappa(X)^2$ 陷阱
- K-Means++ guarantees, Lloyd-as-EM
- bias-variance trade-off, MAP-as-Ridge
- GLM, link function, canonical loss, FTRL
- Platt / isotonic calibration, Brier score
- map-reduce on sufficient statistics, parameter server, async vs sync SGD

---

> **作者注**: 这 4 题是 Uber Round 2 ML Coding 的 canonical set. 不要等到 VO 当天才"现想 vectorization", 提前把代码 muscle-memory 化, 然后用前三天把 trade-off + 行业黑话过一遍即可上场.
