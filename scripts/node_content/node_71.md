# Clustering（聚类）

## Overview

**Clustering（聚类）** 在没有标签的情况下将相似数据点分组，属于 **Unsupervised Learning（无监督学习）** 的核心方法。在MLE面试中，聚类对于客户分群、异常检测和特征工程都至关重要。核心考点包括：理解不同聚类算法的假设、可扩展性以及在没有真实标签时如何评估聚类质量。聚类问题没有唯一正确答案——不同算法基于不同的相似性定义和优化目标，产生不同的分组结果。

## Core Concepts

### K-Means（K均值聚类）

最小化簇内平方和 **WCSS（Within-Cluster Sum of Squares，簇内平方和）**：

$$\arg\min_{\mu_1,...,\mu_K} \sum_{k=1}^{K}\sum_{x_i \in C_k} \|x_i - \mu_k\|^2$$

**算法流程**：
1. 初始化 $K$ 个质心
2. 将每个点分配到最近的质心
3. 更新质心为簇内均值
4. 重复直到收敛（质心不再变化或达到最大迭代次数）

时间复杂度：$O(nKdT)$，其中 $n$ 是样本数，$K$ 是簇数，$d$ 是维度，$T$ 是迭代次数。

**K-Means++**（智能初始化）：第一个质心随机选择，后续质心按概率 $P(x) \propto D(x)^2$（到最近已选质心的距离的平方）采样。可证明是 $O(\log K)$-competitive的最优解的近似。

**K-Means的局限性**：
- 假设簇是 **Spherical（球形）** 且大小相似
- 对初始化敏感（K-Means++缓解但不完全解决）
- 必须预先指定 $K$
- 对 **Outliers（异常值）** 敏感（因为使用均值）
- 只能发现凸形簇

**Mini-Batch K-Means**：每次迭代只使用一小批数据更新质心。适用于 $n > 100K$ 的大规模数据，收敛更快但结果略差。

### DBSCAN（基于密度的聚类）

**DBSCAN（Density-Based Spatial Clustering of Applications with Noise，基于密度的噪声应用空间聚类）** 根据密度将点分组到高密度区域，将稀疏区域的点标记为噪声。

参数：$\epsilon$（邻域半径）、$\text{minPts}$（核心点的最小邻居数）。

| 点类型 | 定义 | 角色 |
|--------|------|------|
| **Core Point（核心点）** | $\epsilon$ 邻域内有 $\geq \text{minPts}$ 个邻居 | 构成簇的核心 |
| **Border Point（边界点）** | 在核心点的 $\epsilon$ 邻域内但自身不是核心点 | 簇的边缘 |
| **Noise Point（噪声点）** | 既不是核心点也不是边界点 | 被标记为异常值 |

**优势**：发现任意形状的簇、自动处理噪声、不需要预先指定 $K$。
**劣势**：对 $\epsilon$ 和 $\text{minPts}$ 敏感；密度差异大的数据表现不佳；高维数据中距离度量退化。

**参数选择**：使用 **K-distance Plot（K距离图）**——计算每个点到第 $k$ 近邻的距离并排序，选择"拐点"处的距离作为 $\epsilon$。

时间复杂度：$O(n^2)$（无空间索引）或 $O(n\log n)$（有 **KD-Tree / Ball-Tree** 空间索引）。

### HDBSCAN（层次密度聚类）

**HDBSCAN（Hierarchical DBSCAN，层次化DBSCAN）** 是DBSCAN的改进版，不需要固定的 $\epsilon$：
- 在多个 $\epsilon$ 尺度上构建层次聚类
- 使用 **Mutual Reachability Distance（相互可达距离）** 平滑密度估计
- 自动提取最稳定的簇
- 参数只需 `min_cluster_size`，比DBSCAN更鲁棒

### Hierarchical Clustering（层次聚类）

- **Agglomerative（凝聚法/自底向上）**：从 $n$ 个簇开始，逐步合并最近的簇对
- **Divisive（分裂法/自顶向下）**：从1个簇开始，递归分裂

**Linkage Criteria（链接准则）** 定义簇间距离：

| 链接类型 | 距离定义 | 特点 |
|---------|---------|------|
| **Single（单链接）** | 两簇最近点距离 | 发现细长形簇，对噪声敏感 |
| **Complete（全链接）** | 两簇最远点距离 | 倾向球形簇，对异常值敏感 |
| **Average（平均链接）** | 所有点对距离的均值 | 折中 |
| **Ward（Ward法）** | 合并后方差增量最小 | 倾向等大的球形簇 |

**Dendrogram（树状图）** 可视化合并过程，通过在不同高度"切割"得到不同数量的簇。

时间复杂度：$O(n^2\log n)$（一般）或 $O(n^3)$（朴素实现）。

### GMM（Gaussian Mixture Models，高斯混合模型）

概率聚类：每个簇是一个高斯分布 $\mathcal{N}(\mu_k, \Sigma_k)$：

$$p(x) = \sum_{k=1}^{K} \pi_k \mathcal{N}(x|\mu_k, \Sigma_k)$$

其中 $\pi_k$ 是第 $k$ 个成分的混合权重（$\sum \pi_k = 1$）。

通过 **EM（Expectation-Maximization，期望最大化）** 算法拟合：
- **E步**：计算每个点属于每个簇的后验概率（**Responsibility，责任值**）
- **M步**：用加权统计量更新 $\mu_k, \Sigma_k, \pi_k$

**GMM vs K-Means**：
- GMM提供 **Soft Assignments（软分配）**（概率），K-Means只有硬分配
- GMM支持椭圆形簇（通过协方差矩阵），K-Means只支持球形
- K-Means是GMM在所有簇协方差为 $\sigma^2 I$ 且取硬分配时的特例
- GMM可用 **BIC（Bayesian Information Criterion，贝叶斯信息准则）** 选择 $K$

### Spectral Clustering（谱聚类）

基于图论的方法：
1. 构建相似度图（$k$-NN图或 $\epsilon$-邻域图）
2. 计算 **Laplacian Matrix（拉普拉斯矩阵）** $L = D - W$
3. 对 $L$ 做特征分解，取最小的 $K$ 个特征向量
4. 在特征向量空间中运行K-Means

适用于非凸形簇，利用了图的连通性而非距离。时间复杂度 $O(n^3)$（特征分解），大规模数据需近似方法。

### Cluster Evaluation（聚类评估）

**有真实标签时**：
- **ARI（Adjusted Rand Index，调整兰德指数）**：衡量两种聚类的一致性，调整了随机因素
- **NMI（Normalized Mutual Information，归一化互信息）**：基于信息论

**无真实标签时（内部指标）**：
- **Silhouette Score（轮廓系数）**：

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

其中 $a(i)$ 是点到同簇其他点的平均距离，$b(i)$ 是点到最近其他簇的平均距离。$s \in [-1, 1]$，越大越好。

- **Davies-Bouldin Index（Davies-Bouldin指数）**：簇内散度与簇间距离之比，越小越好
- **Calinski-Harabasz Index（CH指数）**：簇间方差/簇内方差，越大越好

### Choosing K（选择K值）

- **Elbow Method（肘部法）**：绘制 $K$ vs WCSS（惯性），选择斜率急剧变化的点
- **Silhouette Analysis**：选择平均轮廓系数最高的 $K$
- **Gap Statistic（Gap统计量）**：比较真实数据的WCSS与随机数据的WCSS
- **BIC/AIC**：适用于GMM，平衡拟合质量和模型复杂度
- **领域知识**：业务场景往往有自然的分组数量

### Practical Considerations（实践考量）

**特征缩放**：聚类前必须进行特征缩放。K-Means和DBSCAN都基于距离度量，不同尺度的特征会导致某些特征主导距离计算。推荐使用 **StandardScaler（标准化）** 或 **MinMaxScaler（最小最大缩放）**。

**高维数据的挑战**：在高维空间中，距离度量退化（**Curse of Dimensionality，维度灾难**），所有点对之间的距离趋于相等。解决方案：先用 **PCA（Principal Component Analysis，主成分分析）** 降维，再聚类。

**聚类的应用场景**：
- **客户分群**：基于RFM（**Recency，近度**；**Frequency，频度**；**Monetary，金额度**）特征
- **异常检测**：孤立点不属于任何簇
- **特征工程**：将簇标签作为新特征输入下游模型
- **数据压缩**：用质心替代原始数据（向量量化）
- **半监督学习**：先聚类，再在少量标注簇上训练

**聚类稳定性分析**：多次运行聚类（不同随机种子或子采样），检查结果的一致性。如果聚类结果在多次运行中变化很大，说明数据没有明显的聚类结构或 $K$ 选择不当。

## Implementation

```python
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, adjusted_rand_score

# K-Means with elbow method
inertias = []
sil_scores = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
    km.fit(X)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X, km.labels_))

# DBSCAN
db = DBSCAN(eps=0.5, min_samples=5)
labels = db.fit_predict(X)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = (labels == -1).sum()

# GMM with BIC for model selection
bics = []
for k in range(2, 11):
    gmm = GaussianMixture(n_components=k, random_state=42)
    gmm.fit(X)
    bics.append(gmm.bic(X))
best_k = range(2, 11)[np.argmin(bics)]
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| 选择 $K$ | "多少个簇？" | 肘部法（惯性），轮廓系数，领域知识 |
| K-Means局限性 | 非球形簇 | 用DBSCAN或GMM处理不规则形状 |
| 可扩展性 | 大数据集 | Mini-batch K-Means适合 $n>100K$；DBSCAN无索引时 $O(n^2)$ |
| 无标签评估 | 无真实标签 | 轮廓系数是首选内部验证指标 |
| 客户分群设计 | 系统设计 | 特征工程→标准化→聚类→业务解读→持续监控 |

### Common Interview Questions

- **K-Means何时失败？举例？** 非球形簇、大小差异大的簇、含噪声数据、高维数据
- **DBSCAN如何处理噪声和变密度？** 噪声自动标记；变密度需HDBSCAN
- **K-Means vs GMM：何时选哪个？** 需要概率/软分配/椭圆簇→GMM；快速/大规模→K-Means
- **如何无标签评估聚类质量？** 轮廓系数、DB指数、领域特定验证
- **设计电商客户分群pipeline？** RFM特征→标准化→K-Means/GMM→轮廓系数选K→业务标签解读

## Key Takeaways

- K-Means：快速、简单，假设球形等大簇。K-Means++初始化是标准做法
- DBSCAN：不需指定 $K$，发现任意形状，处理噪声。参数需通过K距离图选择
- GMM：软分配，灵活的簇形状（协方差矩阵），概率框架
- 聚类前始终做特征缩放
- 轮廓系数是首选内部验证指标
- HDBSCAN解决了DBSCAN对 $\epsilon$ 敏感的问题，是现代密度聚类的首选
- 谱聚类利用图的连通性发现非凸形簇，但计算复杂度较高
- 面试中要能根据数据特性（规模、形状、噪声、维度）选择合适的聚类算法
- K-Means的收敛性：目标函数单调递减，但只保证收敛到局部最优。多次运行（`n_init`参数）取最佳结果是标准做法
