# Anomaly Detection（异常检测）

## Overview

**Anomaly Detection（异常检测）** 识别显著偏离正常模式的数据点。在欺诈检测、系统监控和数据质量控制中至关重要。面试中考察对统计方法与ML方法的理解，以及在没有标签时如何评估检测器性能。

异常检测的核心挑战在于：正常数据量大但异常数据极少（甚至完全没有标签），模型必须在几乎没有正样本的情况下学会区分。与传统的二分类不同，异常检测通常作为 **One-Class Classification（单类分类）** 问题来处理——模型只学习正常数据的分布，偏离该分布的点被视为异常。这使得异常检测方法在概念上更接近密度估计而非判别分类。

## Core Concepts

### Types of Anomalies（异常类型）

| 类型 | 描述 | 示例 |
|------|------|------|
| **Point Anomaly（点异常）** | 单个数据点偏离整体分布 | 一笔异常大额交易 |
| **Contextual Anomaly（上下文异常）** | 在特定上下文中异常 | 夏天温度-10°C |
| **Collective Anomaly（集合异常）** | 一组数据点共同构成异常 | 短时间内多次小额交易 |

### Statistical Methods（统计方法）

#### Z-Score（Z分数）

标记 $|z| > 3$ 的点为异常：

$$z = \frac{x - \mu}{\sigma}$$

假设数据服从高斯分布。简单快速，但对非高斯数据效果差。

**Modified Z-Score（改进Z分数）**：使用中位数和 **MAD（Median Absolute Deviation，中位绝对偏差）** 替代均值和标准差，对异常值更鲁棒：

$$z_{mod} = \frac{0.6745(x - \text{median})}{\text{MAD}}$$

#### Mahalanobis Distance（马氏距离）

考虑特征间相关性的多变量距离：

$$D_M(x) = \sqrt{(x-\mu)^T \Sigma^{-1} (x-\mu)}$$

当 $\Sigma = I$（单位矩阵）时退化为欧氏距离。马氏距离考虑了数据的协方差结构，沿方差大的方向距离被缩小。

**假设**：数据近似多元高斯分布。$D_M^2$ 服从 $\chi^2_d$ 分布（$d$ 为维度），可用统计检验确定阈值。

#### IQR Method（四分位距法）

$$\text{lower} = Q_1 - 1.5 \times IQR, \quad \text{upper} = Q_3 + 1.5 \times IQR$$

其中 $IQR = Q_3 - Q_1$。不依赖分布假设，适用于单变量异常检测。

### Isolation Forest（孤立森林）

核心洞察：**异常点更容易被隔离**（需要更少的随机分割）。

**算法**：
1. 随机选择特征和分割值构建 **Isolation Tree（孤立树）**
2. 异常点到达叶节点的路径更短
3. 异常分数基于平均路径长度 $E[h(x)]$：

$$s(x, n) = 2^{-E[h(x)]/c(n)}$$

其中 $c(n) = 2H(n-1) - 2(n-1)/n$ 是 **BST（Binary Search Tree，二叉搜索树）** 中的平均路径长度，$H(k)$ 是调和数。

| 分数 | 含义 |
|------|------|
| $s \to 1$ | 高度疑似异常 |
| $s \to 0.5$ | 正常点 |
| $s \to 0$ | 正常且典型 |

**优势**：
- 线性时间复杂度 $O(n\log n)$
- 不需要距离计算或密度估计
- 对高维数据效果好
- 不需要假设数据分布
- `contamination` 参数设置预期异常比例

### Extended Isolation Forest（扩展孤立森林）

标准孤立森林只沿坐标轴分割，可能产生偏差（对轴对齐的异常不敏感）。**Extended Isolation Forest** 使用随机超平面分割：

$$\text{split}: w^T x \leq b$$

其中 $w$ 是随机法向量，$b$ 是随机阈值。这样可以在任意方向上隔离异常。

### One-Class SVM（单类SVM）

在核空间中学习围绕正常数据的决策边界：

$$\min_{w,\xi,\rho} \frac{1}{2}\|w\|^2 + \frac{1}{\nu n}\sum_i \xi_i - \rho \quad \text{s.t.} \quad w^T\phi(x_i) \geq \rho - \xi_i$$

参数 $\nu$ 控制异常比例的上界（也是支持向量比例的下界）。

**SVDD（Support Vector Data Description，支持向量数据描述）**：寻找包围正常数据的最小超球体，而非超平面。

### LOF（Local Outlier Factor，局部异常因子）

基于局部密度的方法——相对于邻居的密度来判断异常：

$$\text{LOF}(x) = \frac{1}{k}\sum_{o \in N_k(x)}\frac{\text{lrd}(o)}{\text{lrd}(x)}$$

其中 **lrd（local reachability density，局部可达密度）** 是 $x$ 的 $k$ 个最近邻的平均可达距离的倒数。

LOF > 1 表示密度低于邻居（可能是异常）。

**优势**：能检测 **Local Anomaly（局部异常）**——在全局分布中正常但在局部邻域中异常的点。

### Autoencoder-Based Detection（基于自编码器的检测）

在正常数据上训练自编码器，异常点的重建误差更高：

$$\text{anomaly\_score}(x) = \|x - \text{decode}(\text{encode}(x))\|^2$$

设定重建误差阈值：通常使用正常数据重建误差的某个百分位数（如95th或99th）。

**变体**：
- **VAE**：用 **ELBO（Evidence Lower Bound，证据下界）** 作为异常分数
- **时序自编码器**：LSTM/Transformer自编码器用于序列异常
- **对比学习**：学习正常数据的表示，异常在表示空间中偏离

### Time Series Anomaly Detection（时序异常检测）

| 方法 | 描述 | 适用场景 |
|------|------|---------|
| **滚动统计** | 计算滑动窗口的均值/标准差，超出范围为异常 | 简单基线 |
| **STL分解** | 分解为趋势+季节+残差，残差异常检测 | 有季节性的数据 |
| **Prophet** | Facebook的时序预测模型，超出置信区间为异常 | 有多重季节性 |
| **LSTM Autoencoder** | 重建误差作为异常分数 | 复杂时序模式 |
| **Spectral Residual** | 频域分析，检测显著性 | 实时检测 |

### Ensemble Methods for Anomaly Detection（集成异常检测方法）

组合多个检测器可以提高鲁棒性：

**投票法**：多个独立检测器对每个点投票，超过阈值的标记为异常。
**分数融合**：将不同检测器的异常分数归一化后取加权平均。
**级联法**：粗筛（高召回率）→ 精筛（高精确率）→ 人工审核。

**实际生产系统**通常组合规则引擎（已知模式）+ ML模型（未知模式）+ 人工审核。

### Evaluation Strategies（评估策略）

在没有标签时评估异常检测器的几种方法：

| 方法 | 描述 | 局限性 |
|------|------|--------|
| **注入合成异常** | 在正常数据中人工添加已知异常 | 合成异常可能不代表真实异常 |
| **Precision@K** | 标记top-K异常分数的点，人工审核 | 依赖领域专家 |
| **业务指标** | 欺诈金额减少、故障发现率 | 有延迟，不适合快速迭代 |
| **A/B测试** | 对比不同检测器的在线表现 | 需要生产环境支持 |

### Anomaly Detection in Production（生产环境中的异常检测）

**数据漂移**：正常模式会随时间变化，需要定期重训练或使用在线学习。
**Alert Fatigue（警报疲劳）**：过多误报导致运维人员忽视真正的警报——阈值设置是业务与技术的权衡。
**冷启动**：新系统缺乏历史数据，需要用领域知识设定初始规则，逐步过渡到数据驱动。

## Implementation

```python
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor

# Isolation Forest
iso = IsolationForest(
    n_estimators=200,
    contamination=0.01,  # 预期异常比例
    max_features=1.0,
    random_state=42
)
iso.fit(X_train)  # 在正常数据上训练
scores = iso.decision_function(X_test)  # 越低越异常
predictions = iso.predict(X_test)  # -1 = 异常, 1 = 正常

# LOF
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.01)
predictions = lof.fit_predict(X)  # -1 = 异常

# Autoencoder anomaly detection (PyTorch)
import torch.nn as nn
class AnomalyAutoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim=32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128), nn.ReLU(),
            nn.Linear(128, latent_dim))
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128), nn.ReLU(),
            nn.Linear(128, input_dim))

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)
# 异常分数 = reconstruction MSE
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| 方法选择 | 表格/序列/图像 | 表格：孤立森林；高维：自编码器；时序：LSTM AE |
| 评估挑战 | 无标签 | 合成异常、领域专家审核、业务指标 |
| 特征工程 | 时序异常 | 计算滚动统计，然后应用点异常检测 |
| 阈值选择 | 生产部署 | 业务成本决定阈值；警报疲劳 vs 漏检 |
| 概念漂移 | 长期部署 | 正常模式会变化，需要定期重训练 |

### Common Interview Questions

- **为什么孤立森林对异常检测有效？** 异常点在特征空间中稀疏且不同，更少的随机分割就能隔离
- **如何检测服务器指标的时序异常？** STL分解+残差统计检验，或LSTM自编码器
- **孤立森林 vs 单类SVM对比？** IF更快、更可扩展、无参数假设；OC-SVM在小数据+核方法时更好
- **无标签异常如何评估？** Precision@k（标记top-k为异常，人工审核）、业务指标（欺诈金额减少）、专家审核
- **设计支付平台的欺诈检测系统？** 特征工程（交易频率、金额、地理）→孤立森林初筛→规则引擎→人工审核→反馈循环

## Key Takeaways

- 孤立森林：快速、可扩展、无假设——表格数据的默认选择
- 统计方法（Z-score、马氏距离）：简单、可解释，但需要分布假设
- 自编码器：最适合高维数据，重建误差作为异常指标
- LOF：能检测局部异常（全局正常但局部密度异常）
- 评估是最难的部分——使用Precision@k、业务指标或专家审核
- 生产中：组合多个检测器，使用人在回路（human-in-the-loop）调整阈值
- 时序异常需要特殊处理：滑动窗口特征、季节性分解、序列模型
- 区分点异常、上下文异常和集合异常有助于选择正确的检测方法
- 孤立森林的核心直觉简洁有力：异常点在随机树中路径更短
- One-Class SVM通过参数 $\nu$ 控制异常比例上界，适合小数据集
- 生产系统通常需要多层防御：规则引擎（已知模式）+ ML模型（未知模式）+ 人工审核
- 马氏距离考虑了特征相关性，是多变量异常检测的基础工具
- Extended Isolation Forest通过随机超平面分割解决了标准IF对坐标轴对齐的偏差问题
- 面试中重点掌握孤立森林原理和实际部署中的阈值选择策略
