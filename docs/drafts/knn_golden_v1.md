# K-Nearest Neighbors (KNN + Weighted)

## TL;DR

Lazy learner: 训练 = 存数据, 所有 compute 推迟到 `predict`. 三步: (1) 算 query 到所有训练点的欧氏距离; (2) `argpartition` 取 Top-K (平均 $O(n)$); (3) 投票 (分类) / 平均 (回归). 三种 weighting: `uniform`, `inverse` $w_i = 1/(d_i + \varepsilon)$, `gaussian` $w_i = \exp(-d_i^2 / 2\sigma^2)$. 失败模式: `inverse` 漏 $\varepsilon$ 在 $d=0$ 处爆 `inf`; 高维下距离趋同 (curse of dimensionality). 复杂度: 训练 $O(1)$, 单 query brute-force $O(nd)$, KD-tree 低维 $O(d \log n)$, 空间 $O(nd)$.

---

## 实现

### 0. Class skeleton

```python
import numpy as np

class KNN:
    def __init__(self, k: int = 5):
        self.k = k
        self.X = None    # (n, d)
        self.y = None    # (n,)
```

### 1. fit -- store data, no training

Lazy: 仅存 `(X, y)`, 所有 compute 推迟到 `predict` -- 增量更新友好 (无需重训), 但训练集必须常驻内存.

```python
def fit(self, X, y):
    self.X, self.y = X, y
    return self
```

### 2. Distance -- naive broadcast (vectorized)

直接 `(a - b) ** 2` 求和开方, 数值稳定 + 可读性最高. `np.expand_dims` 在 `axis=1 / axis=0` 各插入一个 size=1 的轴, 触发 broadcast 一次性算所有 pair.

```python
def _euclidean(self, Xq):
    # Xq: (nq, d), self.X: (nt, d)
    # np.expand_dims 最显式; 等价 sugar: Xq[:, None, :] / Xq[:, np.newaxis, :]
    diff = np.expand_dims(Xq, 1) - np.expand_dims(self.X, 0)  # (nq, nt, d)
    return np.sqrt((diff ** 2).sum(axis=2))                    # (nq, nt)
```

为什么 broadcast 不是 `np.zeros((nq, nt, d))` 再赋值? Broadcast 的两个输入是 virtual view (零拷贝), 输出张量直接一步分配 -- 预分配 zeros 再填等于多写一遍逻辑且更慢. `None / np.newaxis / expand_dims` 是同一行为的不同糖衣.

代价: 中间张量 `(nq, nt, d)` 内存爆炸. 大数据用 expansion trick (见拓展 A).

### 3. Top-K -- `argpartition`, NOT `argsort`

`argpartition` 平均 $O(n)$ (Quickselect, 仅保证第 K 位左小右大, 不排序前 K) -- KNN 只需 SET. `argsort` $O(n \log n)$ 在 $n = 10^6$ 时多花 ~20×.

```python
def _topk_idx(self, dist):
    # dist: (nq, nt)
    return np.argpartition(dist, kth=self.k, axis=1)[:, :self.k]   # (nq, k)
```

### 4. Predict -- classification (uniform majority vote)

V1 默认 uniform vote. Weighted 变体直接替换 `scores` 那行 (见 Weighting Variants 表).

```python
def predict(self, Xq):
    dist = self._euclidean(Xq)                                    # (nq, nt)
    idx = self._topk_idx(dist)                                    # (nq, k)
    nbr_y = self.y[idx]                                           # (nq, k)

    # ---- weighted 情况下解开下面这行, 用对应 kernel 替换 scores ----
    # nbr_d = np.take_along_axis(dist, idx, axis=1)               # (nq, k)
    # w = 1.0 / (nbr_d + 1e-9)                                    # inverse
    # w = np.exp(-(nbr_d ** 2) / (2 * sigma ** 2))                # gaussian
    # scores[:, j] = (w * (nbr_y == c)).sum(axis=1)

    classes = np.unique(self.y)                                   # (|C|,)
    scores = np.stack(
        [(nbr_y == c).sum(axis=1) for c in classes], axis=1
    )                                                             # (nq, |C|)
    return classes[scores.argmax(axis=1)]                         # (nq,)
```

---

## Weighting Variants

|              | Uniform        | Inverse $1/(d+\varepsilon)$  | Gaussian $e^{-d^2/2\sigma^2}$  |
| ------------ | -------------- | ------------------------------ | -------------------------------- |
| 衰减形式     | 阶跃           | 多项式 (慢)                    | 指数 (快)                        |
| 失败模式     | 偶 K 易 tie    | $d=0$ 漏 $\varepsilon$ 爆 NaN | $\sigma$ 选错退化              |
| 实践默认值   | 奇 K           | $\varepsilon = 10^{-9}$       | $\sigma$ = 邻居距离中位数      |
| 是否需 tune  | 否             | 否 ($\varepsilon$ 是常数守卫) | 是 ($\sigma$ 是带宽超参)       |

**一句话**: weighted KNN 把 "硬 top-K cutoff" 改成连续权重, 对 K 选错鲁棒性更高 -- 默认 `inverse`, 数据光滑时换 `gaussian`.

**NOTE**: `inverse` 不是 `gaussian` 的特例. 两者是不同衰减族 (多项式 vs 指数); Gaussian 用 $\sigma$ 换掉 $\varepsilon$, 把 "数值守卫" 问题转移成 "带宽 tune" 问题, 不是免费午餐.

---

## Regression 扩展 (假设 $y \in \mathbb{R}$ 连续)

KNN regression 的前提是 label 加减取平均有意义 (房价, 温度, **CTR** (Click-Through Rate, 点击率), 停留时长). 聚合方式从 mode -> mean:

$$\hat{y} = \frac{\sum_i w_i \, y_i}{\sum_i w_i}$$

代码上替换 `predict` 的最后两行: `return (w * nbr_y).sum(1) / w.sum(1)`.

离散标签上做 weighted mean 完全没意义 (类别 0=猫 / 1=狗 / 2=鸟 平均出 1.7 是什么?) -- 所以 classification 用 mode, regression 用 mean, 两种根本不同的聚合, 不是 weighted 与否的差异.

与 K-Means 无关 (K-Means 无监督无 label). 本质是 Nadaraya-Watson kernel regression 的近邻版: 在 query 邻域内假设 $y$ 近似常数, 加权平均得到局部估计.

---

## End-to-end test

```python
import numpy as np
np.random.seed(0)
N_train, N_test, D, K = 100, 20, 4, 5
X_train = np.random.rand(N_train, D)
y_train = np.random.randint(0, 3, N_train)
X_test  = np.random.rand(N_test, D)
knn = KNN(k=K).fit(X_train, y_train)
preds = knn.predict(X_test)
assert preds.shape == (N_test,)
print(f"Predicted classes: {np.unique(preds)}")
```

---

## 拓展

### A. Distance expansion trick (内存换数值稳定性)

展开 $\|a-b\|^2 = \|a\|^2 + \|b\|^2 - 2 a \cdot b$, 中间张量从 $(n_q, n_t, d)$ 降到 $(n_q, n_t)$. 代价: 大数相消有 fp 噪声, `sqrt` 前必须 clip $\geq 0$ 防 NaN.

```python
sq_q  = (Xq ** 2).sum(axis=1, keepdims=True)         # (nq, 1)
sq_t  = (self.X ** 2).sum(axis=1, keepdims=True).T   # (1, nt)
raw   = sq_q + sq_t - 2 * Xq @ self.X.T              # (nq, nt)
dist  = np.sqrt(np.maximum(raw, 0.0))                # clip <0 fp noise
```

何时用: 训练集到百万级, $d$ 中等 (几十到几百), 内存吃紧. 否则 naive 更稳更清晰. sklearn 默认 expansion 是为了大规模场景, 不是因为它本身更优.

### B. 其他距离 (默认 Euclidean, 1 句话备用知识)

- **Manhattan** (L1) $\sum |a_i - b_i|$: 对 outlier 鲁棒, 高维 / 稀疏数据 (文本词袋) 更稳.
- **Cosine** $1 - \frac{a \cdot b}{\|a\| \|b\|}$: 只看方向不看长度, embeddings / **TF-IDF** (Term Frequency--Inverse Document Frequency, 词频--逆文档频率) 标配; 等价于 L2-normalize 后做欧氏.
- **Mahalanobis** $\sqrt{(a-b)^T \Sigma^{-1} (a-b)}$: 用协方差白化, 考虑特征相关性; 等价于 "先用 $\Sigma^{-1/2}$ 白化空间, 再做欧氏" -- metric learning (**LMNN** (Large Margin Nearest Neighbor) / **NCA** (Neighbourhood Components Analysis)) 入口.

### C. Kernel function 统一视角

任何单调递减的 $k: \mathbb{R}_+ \to \mathbb{R}_+$ 都可以做 weighting 函数. Uniform / Inverse / Gaussian 是同一家族里的不同选择, **互不包含**. 选 kernel = 选你对 "邻居影响半径" 的先验: 阶跃 (uniform), 慢衰减 (inverse), 快衰减 (gaussian).

---

## 面试追问 (Cheat Sheet)

> **Q: K 怎么选?**

5-fold CV 在 $\{1, 3, 5, \ldots, \sqrt{n}\}$ 上扫, 选 validation 最优. 太小过拟合 (单点噪声主导), 太大欠拟合 (类边界被平滑); 奇 K 防 tie.

> **Q: Curse of dimensionality?**

高维下所有点距离趋于相等, KNN 失去判别力; 经验 $d \gtrsim 10$ 即明显退化. 解法: **PCA** (Principal Component Analysis, 主成分分析) / autoencoder 降维, 或 metric learning (LMNN / NCA) 学 "同类近异类远".

> **Q: 加速 query?**

Brute-force $O(nd)$ -> KD-tree 低维 ($d \leq 20$) 平均 $O(d \log n)$, worst $O(n)$. 高维上 **ANN** (Approximate Nearest Neighbor, 近似最近邻) (FAISS / HNSW / ScaNN) 压到亚秒, 召回 < 100%.

> **Q: 为什么必须特征缩放?**

欧氏距离对量级敏感: 收入 ($10^4$) 主导年龄 ($10^1$). `StandardScaler` 是 distance-based 模型 (KNN / SVM / K-Means) 共同前置.

> **Q: Lazy vs eager learning?**

KNN 训 $O(1)$ / 推 $O(nd)$, 增量更新友好但必存 $O(nd)$ 训练数据 (大数据退役主因). 决策树 / NN 是 eager: 训练慢, 推理 $O(d)$.

> **Q: Imbalanced classification 下 KNN 的 trap?**

多数类天然在邻居里占多数, KNN 倾向预测多数类. 解法: (1) `inverse / gaussian` weighting 让最近邻发言权更大; (2) class-prior 反加权 $w_i \cdot 1/\text{freq}(y_i)$; (3) **SMOTE** (Synthetic Minority Over-sampling Technique, 合成少数类过采样) 上采样少数类.

> **Q: KNN regression 和 Nadaraya-Watson 的关系?**

KNN regression 是 Nadaraya-Watson kernel regression 的 "hard-cutoff 近邻版" -- 都是非参数局部加权平均, 前者用 Top-K 截断, 后者用 kernel 在全数据集上加权. Gaussian-weighted KNN 实际上就是带 K 截断的 Nadaraya-Watson.
