# Dimensionality Reduction（降维）

## Overview

**Dimensionality Reduction（降维）** 将高维数据投影到低维空间，同时保留重要结构。它在可视化、特征工程和对抗 **Curse of Dimensionality（维度灾难）** 中至关重要。**PCA（Principal Component Analysis，主成分分析）** 是面试中最常考的降维技术。

## Core Concepts

### PCA（Principal Component Analysis，主成分分析）

找到数据方差最大的正交方向。给定中心化数据 $X \in \mathbb{R}^{n \times d}$：

**方法一：特征分解**

计算协方差矩阵 $C = \frac{1}{n-1}X^TX$，对 $C$ 做特征分解：

$$C = V\Lambda V^T$$

特征向量 $V$ 的列即为主成分方向，特征值 $\Lambda$ 表示各方向的方差大小。

**方法二：SVD（Singular Value Decomposition，奇异值分解）**

$$X = U\Sigma V^T$$

其中 $U \in \mathbb{R}^{n \times n}$（左奇异向量），$\Sigma \in \mathbb{R}^{n \times d}$（奇异值对角矩阵），$V \in \mathbb{R}^{d \times d}$（右奇异向量，即主成分方向）。

投影数据：$Z = XV_k$（保留前 $k$ 个主成分），$V_k$ 是 $V$ 的前 $k$ 列。

**PCA与SVD的关系**：$X^TX = V\Sigma^T U^T U \Sigma V^T = V\Sigma^2 V^T$，因此PCA特征值 $\lambda_i = \frac{\sigma_i^2}{n-1}$。实际中直接用SVD比计算协方差矩阵更数值稳定。

**方差解释比**：

$$\text{Explained Variance Ratio} = \frac{\sum_{i=1}^{k} \sigma_i^2}{\sum_{i=1}^{d} \sigma_i^2}$$

常用启发式：选择保留95%方差的 $k$。

**PCA的最大方差视角**：第一个主成分 $w_1$ 最大化投影方差：

$$w_1 = \arg\max_{\|w\|=1} w^T C w$$

由拉格朗日乘子法得到 $Cw_1 = \lambda_1 w_1$，即 $w_1$ 是协方差矩阵的最大特征值对应的特征向量。

**PCA的最小重建误差视角**：保留 $k$ 个主成分等价于最小化重建误差：

$$\min_{W_k} \sum_{i=1}^{n}\|x_i - W_k W_k^T x_i\|^2$$

两个视角得到相同结果——这是PCA的优美之处。

### Kernel PCA（核PCA）

对于非线性结构，在核诱导的特征空间中执行PCA：

$$K_{ij} = \phi(x_i)^T\phi(x_j)$$

先中心化核矩阵：$\tilde{K} = K - \frac{1}{n}\mathbf{1}K - K\frac{1}{n}\mathbf{1} + \frac{1}{n}\mathbf{1}K\frac{1}{n}\mathbf{1}$

然后对 $\tilde{K}$ 做特征分解。常用核：**RBF（Radial Basis Function，径向基函数）**、**Polynomial（多项式核）**。

**与线性PCA的关系**：当核函数为线性核 $K(x,z) = x^Tz$ 时，Kernel PCA退化为标准PCA。

### t-SNE（t-分布随机邻域嵌入）

**t-SNE（t-distributed Stochastic Neighbor Embedding）** 是非线性的2D/3D可视化技术，通过保持局部结构来实现降维。

**高维空间**中的相似性用高斯分布建模：

$$p_{j|i} = \frac{\exp(-\|x_i-x_j\|^2/2\sigma_i^2)}{\sum_{k\neq i}\exp(-\|x_i-x_k\|^2/2\sigma_i^2)}$$

对称化：$p_{ij} = \frac{p_{j|i} + p_{i|j}}{2n}$

**低维空间**中的相似性用 **Student's t-Distribution（学生t分布）**（自由度为1，即柯西分布）建模：

$$q_{ij} = \frac{(1+\|y_i-y_j\|^2)^{-1}}{\sum_{k\neq l}(1+\|y_k-y_l\|^2)^{-1}}$$

**为什么用t分布而非高斯？** t分布有更重的尾部（heavy tails），允许低维空间中远距离的点有更大的距离，缓解了 **Crowding Problem（拥挤问题）**——在高维中等距的点在低维中无法保持等距。

通过梯度下降最小化 **KL Divergence（KL散度）**：

$$\min_{Y} KL(P\|Q) = \sum_{i \neq j} p_{ij}\log\frac{p_{ij}}{q_{ij}}$$

**Perplexity（困惑度）** 参数控制有效邻域大小，通常设为5-50。

**t-SNE的关键注意事项**：
- 簇的**大小和密度**在可视化中没有意义
- 簇之间的**距离**没有意义
- 只有**拓扑关系**（哪些点聚在一起）有意义
- 不能用于新测试点（非参数方法，没有学到映射函数）
- 不同的随机初始化可能得到不同结果——需要多次运行

### UMAP（统一流形近似和投影）

**UMAP（Uniform Manifold Approximation and Projection）** 是t-SNE的更快替代方案，且能更好地保留全局结构。基于 **Topological Data Analysis（拓扑数据分析）** 和 **Riemannian Geometry（黎曼几何）**。

**与t-SNE的关键区别**：
- 速度更快（可处理百万级数据点）
- 更好地保留全局结构（簇间距离更有意义）
- 可以对新数据点做变换（有 `transform` 方法）
- `n_neighbors` 参数类似于t-SNE的perplexity
- `min_dist` 控制嵌入中点的最小距离（紧凑度）

### Autoencoder for Dimensionality Reduction（自编码器降维）

**Autoencoder（自编码器）** 是一种神经网络，训练目标是重建输入：

$$\text{Encoder}: z = f(x), \quad \text{Decoder}: \hat{x} = g(z)$$

$$\min \|x - g(f(x))\|^2$$

当编码器和解码器都是单层线性的时候，自编码器的解等价于PCA。非线性自编码器可以学习更复杂的低维表示。

**VAE（Variational Autoencoder，变分自编码器）** 增加了概率框架和正则化：

$$\mathcal{L} = \text{Reconstruction Loss} + D_{KL}(q(z|x) \| p(z))$$

### Comparison Table（方法对比）

| 方法 | 线性 | 保留结构 | 速度 | 适用场景 | 可处理新数据 |
|------|------|---------|------|---------|------------|
| PCA | 是 | 全局方差 | 快 | 特征降维、预处理 | 是 |
| Kernel PCA | 否 | 非线性方差 | 中 | 非线性结构 | 是（近似） |
| t-SNE | 否 | 局部结构 | 慢 | 2D可视化 | 否 |
| UMAP | 否 | 局部+全局 | 快 | 可视化、聚类 | 是 |
| Autoencoder | 否 | 学习到的表示 | 慢（训练） | 复杂非线性降维 | 是 |

### Curse of Dimensionality（维度灾难）

高维空间中的几个反直觉现象：
- **距离集中**：所有点对之间的距离趋于相等，$\frac{d_{max}-d_{min}}{d_{min}} \to 0$
- **体积集中于表面**：$d$维单位球的体积随$d$增大趋近于零
- **最近邻退化**：最近邻和最远邻的距离差异变得可以忽略
- **稀疏性**：填充高维空间需要指数级增长的数据点

这就是为什么高维数据需要降维：距离度量在高维中失去区分能力。

### Random Projection（随机投影）

基于 **Johnson-Lindenstrauss Lemma（JL引理）**：$n$ 个高维点可以投影到 $O(\log n / \epsilon^2)$ 维空间，同时以 $(1 \pm \epsilon)$ 的因子保持所有点对距离。

$$z = Rx, \quad R \in \mathbb{R}^{k \times d}, \quad R_{ij} \sim \mathcal{N}(0, 1/k)$$

速度极快，适用于非常高维的数据（如文本的TF-IDF向量）。sklearn中有 `GaussianRandomProjection` 和 `SparseRandomProjection`。

### Truncated SVD / LSA（截断SVD / 潜在语义分析）

对TF-IDF矩阵做SVD降维：$X \approx U_k \Sigma_k V_k^T$。与PCA不同的是，Truncated SVD不需要中心化，适用于稀疏矩阵（如文本的词-文档矩阵）。

在NLP中称为 **LSA（Latent Semantic Analysis，潜在语义分析）**，捕获词之间的潜在语义关系。

### Factor Analysis（因子分析）

与PCA类似但假设数据由潜在因子生成：$x = Wz + \mu + \epsilon$，其中 $z$ 是潜在因子，$\epsilon$ 是观测噪声。与PCA的关键区别是因子分析建模了每个特征独立的噪声方差，而PCA假设等方差噪声。

## Implementation

```python
from sklearn.decomposition import PCA, KernelPCA, IncrementalPCA
from sklearn.manifold import TSNE
import umap
import numpy as np

# PCA with variance threshold
pca = PCA(n_components=0.95)  # 保留95%方差
X_reduced = pca.fit_transform(X)
print(f"降维: {X.shape[1]} -> {X_reduced.shape[1]} 维")
print(f"各主成分方差解释比: {pca.explained_variance_ratio_[:5]}")

# Incremental PCA for large datasets（大数据增量PCA）
ipca = IncrementalPCA(n_components=50, batch_size=1000)
for batch in np.array_split(X, 100):
    ipca.partial_fit(batch)
X_reduced = ipca.transform(X)

# t-SNE for visualization
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_2d = tsne.fit_transform(X)  # 注意：不能对新数据transform

# UMAP (faster, better global structure)
reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1)
X_2d = reducer.fit_transform(X)
X_new_2d = reducer.transform(X_new)  # 可以变换新数据
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| PCA做特征工程 | 高维特征 | 减少多重共线性，在线性模型前使用 |
| t-SNE陷阱 | 可视化解读 | 簇大小/距离无意义；只有拓扑关系有意义 |
| PCA vs 自编码器 | 非线性降维 | 线性PCA = 线性激活的单层自编码器 |
| 维度灾难 | "为什么降维？" | 高维中距离度量失效 |
| 选择主成分数 | "保留多少维？" | 95%方差阈值或肘部法 |

### Common Interview Questions

- **从最大方差角度推导PCA？** 最大化 $w^TCw$ 在 $\|w\|=1$ 约束下，拉格朗日乘子法得特征向量
- **PCA和SVD的关系？** $X = U\Sigma V^T$，PCA特征值=$\sigma_i^2/(n-1)$，主成分方向=$V$的列
- **为什么不能对新测试点用t-SNE？** t-SNE是非参数优化，没有学到映射函数；需要重新运行全部数据
- **何时选PCA而非自编码器？** 数据近似线性、需要可解释性、计算资源有限时
- **如何选择PCA主成分数？** 方差解释比累计达95%、肘部法、交叉验证

## Key Takeaways

- PCA：协方差矩阵的特征分解（或等价地，数据矩阵的SVD）
- PCA前必须中心化数据，通常还需要标准化
- t-SNE：仅用于可视化；簇大小和距离不具备统计意义
- UMAP：比t-SNE更快，全局结构更好，可处理大规模数据且支持新数据变换
- 线性PCA = 线性自编码器；非线性自编码器可捕获更复杂的结构
- 经验法则：PCA做预处理，t-SNE/UMAP做可视化
- 维度灾难使得高维中的距离度量失效——降维是必要的预处理步骤
