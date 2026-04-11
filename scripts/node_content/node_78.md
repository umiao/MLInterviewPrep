# Numerical Features（数值特征处理）

## Overview

数值特征的正确处理是ML流水线的基础。缩放、变换和交互特征会显著影响模型性能。**Tree Models（树模型）** 对单调变换不变，但 **Linear Models（线性模型）** 和神经网络需要仔细的预处理。掌握各种缩放方法的适用场景和 **Data Leakage（数据泄漏）** 的防范是面试核心考点。好的特征工程往往比模型选择更能提升性能——"garbage in, garbage out"是ML的基本原则。

## Core Concepts

### Scaling Methods（缩放方法）

| 方法 | 公式 | 适用场景 | 特点 |
|------|------|---------|------|
| **StandardScaler（标准化）** | $z = \frac{x - \mu}{\sigma}$ | 近似高斯分布的特征 | 最常用，使均值为0方差为1 |
| **MinMaxScaler（最小最大缩放）** | $z = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$ | 有界特征、神经网络 | 缩放到[0,1]，对异常值敏感 |
| **RobustScaler（鲁棒缩放）** | $z = \frac{x - \text{median}}{\text{IQR}}$ | 含异常值的数据 | 用中位数和IQR替代均值和标准差 |
| **MaxAbsScaler（最大绝对值缩放）** | $z = \frac{x}{\|x_{\max}\|}$ | 稀疏数据 | 保持零值不变 |
| **Normalizer（归一化器）** | $z_i = \frac{x_i}{\|x\|_p}$ | 样本级归一化 | 每行独立归一化到单位范数 |

**何时需要缩放**：
- **必须缩放**：SVM、KNN、线性回归/逻辑回归（正则化时）、神经网络、PCA、K-Means
- **不需要缩放**：决策树、随机森林、XGBoost/LightGBM（树模型基于分裂点，不受尺度影响）

**为什么正则化需要缩放**：L1/L2惩罚 $\lambda\sum|\theta_j|$ 对所有参数施加相同强度的惩罚。如果特征尺度不同，大尺度特征的系数天然更小，受惩罚更轻——缩放确保正则化公平地作用于所有特征。

### Transformations（变换）

**Log Transform（对数变换）**：$x' = \log(x + 1)$

处理右偏分布（如收入、计数数据）。加1避免 $\log(0)$。使分布更接近正态，减少异常值的影响。

**Square Root Transform（平方根变换）**：$x' = \sqrt{x}$

对计数数据效果好，比log变换更温和。

**Box-Cox Transform（Box-Cox变换）**：

$$x' = \begin{cases} \frac{x^\lambda - 1}{\lambda} & \lambda \neq 0 \\ \log(x) & \lambda = 0 \end{cases}$$

要求 $x > 0$。自动找到最优 $\lambda$ 使变换后分布最接近正态。$\lambda = 1$：无变换；$\lambda = 0$：log变换；$\lambda = 0.5$：平方根变换。

**Yeo-Johnson Transform（Yeo-Johnson变换）**：Box-Cox的推广，能处理负值和零值。sklearn的 `PowerTransformer` 默认使用Yeo-Johnson。

**Quantile Transform（分位数变换）**：

$$x' = F^{-1}_{\text{target}}(F_{\text{empirical}}(x))$$

非参数方法，将任意分布映射到均匀或正态分布。但会破坏特征之间的关系——映射是按单个特征独立进行的。

### Binning / Discretization（分箱/离散化）

将连续特征转换为类别特征：

| 方法 | 描述 | 适用场景 |
|------|------|---------|
| **Equal-Width（等宽分箱）** | 固定宽度的箱边界 | 均匀分布的数据 |
| **Equal-Frequency / Quantile（等频/分位数分箱）** | 每箱相同数量的样本 | 偏斜分布 |
| **Domain-Driven（业务驱动分箱）** | 基于领域知识的边界 | 年龄段、收入区间 |
| **Decision Tree Binning（决策树分箱）** | 用决策树找最优分割点 | 自动捕捉非线性关系 |

**分箱的价值**：
- 在线性模型中捕捉非线性效应（如年龄对保险费用的分段线性关系）
- 减少噪声和异常值的影响
- 处理非线性关系而不需要复杂模型
- **信息损失**：分箱会丢失箱内的排序信息

### Interaction Features（交互特征）

$$x_{\text{product}} = x_i \cdot x_j, \quad x_{\text{ratio}} = \frac{x_i}{x_j + \epsilon}$$

**多项式特征**：`PolynomialFeatures(degree=2, interaction_only=True)` 生成所有两两交互项 $x_i x_j$（不含 $x_i^2$）。

**注意特征爆炸**：$d$ 个特征的二阶交互产生 $\binom{d}{2}$ 个新特征。$d = 100$ 时有4950个交互特征——需要配合正则化或特征选择使用。

### Outlier Handling（异常值处理）

| 方法 | 描述 | 适用场景 |
|------|------|---------|
| **Clipping / Winsorizing（截断）** | $x' = \text{clip}(x, P_1, P_{99})$ | 保留样本但限制极端值 |
| **Log Transform** | 压缩大值的尺度 | 右偏分布 |
| **RobustScaler** | 用中位数和IQR缩放 | 缩放时降低异常值影响 |
| **删除** | 移除异常样本 | 确认是数据错误时 |
| **标记** | 添加 `is_outlier` 特征 | 异常值本身有信息时 |

### Data Leakage Prevention（数据泄漏防范）

**核心原则**：缩放器/变换器只在训练集上 `fit`，然后用 `transform` 应用到训练集和测试集。

```python
# 正确做法
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 错误做法（泄漏了测试集信息）
scaler.fit(X_all)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

在交叉验证中，缩放必须在每个fold的训练集上独立fit——使用 `Pipeline` 确保正确性。

### Encoding for Models（模型适配编码）

不同模型对数值特征的需求不同：

**梯度下降模型**（线性回归、逻辑回归、SVM、神经网络）：
- 需要标准化或归一化，否则损失景观扁平、收敛慢
- 正则化要求特征在相同尺度上，否则惩罚不公平

**距离度量模型**（KNN、K-Means、DBSCAN）：
- 特征尺度直接影响距离计算，大尺度特征主导结果
- 必须标准化

**树模型**（决策树、随机森林、GBDT）：
- 基于分裂阈值，对单调变换不敏感
- 不需要缩放，但精心构造的比率/交互特征仍可提升性能

### Feature Engineering Best Practices（特征工程最佳实践）

**业务驱动的特征构造**：
- **价格/面积** → 每平方米价格（比原始价格更有意义）
- **纬度/经度** → 到市中心距离（特征的空间含义）
- **生日** → 年龄（而非原始日期）
- **注册时间** → 账户年龄（时间差特征）

**统计特征聚合**：对分组数据（如每个用户的所有交易）计算聚合统计量：
- 均值、中位数、标准差、偏度、峰度
- 最大值、最小值、极差
- 分位数（25th, 75th）
- 计数、缺失比例

**特征的数值稳定性**：
- 除法特征需要添加 $\epsilon$：$\frac{x_i}{x_j + \epsilon}$
- log变换需要确保输入非负：$\log(x + 1)$ 或 $\log(\max(x, \epsilon))$
- 标准化后特征值在 $[-3, 3]$ 范围内是正常的

### Target Leakage in Feature Engineering（特征工程中的目标泄漏）

除了缩放器的泄漏，还需警惕：
- 使用未来信息构造的特征（如用明天的价格预测今天的涨跌）
- 将目标变量的变换作为特征（如商品的历史平均评分包含当前评分）
- 与目标变量高度相关的代理变量（如用"是否发生退货"预测"客户满意度"，但退货数据是后续才有的）

## Implementation

```python
from sklearn.preprocessing import (
    StandardScaler, PowerTransformer, PolynomialFeatures, KBinsDiscretizer
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# 完整的数值特征处理流水线
numeric_pipeline = Pipeline([
    ("power", PowerTransformer(method="yeo-johnson")),  # 正态化
    ("scaler", StandardScaler()),  # 标准化
])

# 不同特征类型的组合处理
preprocessor = ColumnTransformer([
    ("numeric_std", StandardScaler(), standard_cols),
    ("numeric_log", PowerTransformer(), skewed_cols),
    ("numeric_bin", KBinsDiscretizer(n_bins=10, encode="ordinal",
                                      strategy="quantile"), binning_cols),
])

# 交互特征
poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_interactions = poly.fit_transform(X_train)
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| 按模型类型缩放 | "需要缩放吗？" | SVM/KNN/线性/NN必须缩放；树模型不需要 |
| 数据泄漏防范 | "如何预处理？" | 缩放器只在训练集fit；使用Pipeline |
| Log变换处理偏斜 | 右偏严重的特征 | $\log(x+1)$ 简单有效 |
| 特征交叉 | 线性模型 | 手动交互补偿线性假设的局限 |
| 异常值策略 | 数据质量问题 | 先分析原因（错误→删除，真实→截断/变换） |

### Common Interview Questions

- **为什么缩放对基于梯度的优化重要？** 不同尺度的特征导致损失景观扁平，梯度下降在不同方向需要不同步长，降低收敛速度
- **如何处理尺度差异很大的特征？** StandardScaler或RobustScaler（含异常值时）
- **何时用分位数分箱 vs 等宽分箱？** 偏斜数据用分位数分箱确保每箱有足够样本；均匀数据可用等宽
- **如何防止特征预处理中的数据泄漏？** 只在训练集fit，使用Pipeline封装；交叉验证中每fold独立fit
- **设计房价预测模型的特征流水线？** 面积/价格→log变换；经纬度→不变换；房龄→分箱；面积*房间数→交互特征

## Key Takeaways

- 始终只在训练数据上fit变换器（防止数据泄漏）
- StandardScaler是默认选择；含异常值时用RobustScaler
- 右偏数据用Log变换；Box-Cox/Yeo-Johnson自动选择最优变换
- 树模型不需要缩放但受益于精心构造的特征
- 交互特征可以显著提升线性模型性能，但需要配合正则化
- Pipeline封装预处理和模型，确保交叉验证中的正确性
- 分箱将连续特征离散化，可在线性模型中捕捉非线性关系
- 特征构造应以业务理解为驱动（如价格/面积比面积更有意义）
- 统计聚合特征（均值、标准差、分位数）对分组数据非常有效
- 注意数值稳定性：除法加 $\epsilon$，log变换确保非负输入
- 特征工程中的目标泄漏比缩放器泄漏更隐蔽且更危险
- 树模型虽然不需要缩放，但精心构造的比率和交互特征仍能提升性能
- 面试中要能设计端到端的特征处理流水线并解释每步的原因
- Yeo-Johnson是Box-Cox的推广，能处理负值和零值，是PowerTransformer的默认选择
- 分位数变换是非参数方法，强制正态化但会破坏特征间关系
