# Categorical Features（类别特征处理）

## Overview

**Categorical Features（类别特征）** 是ML中最常见的特征类型之一——用户ID、产品类别、地理位置、职业等都是类别特征。如何将类别特征编码为模型可用的数值表示，对模型性能有重大影响。选择错误的编码方式可能引入虚假的序关系、导致维度爆炸、或造成 **Data Leakage（数据泄漏）**。

类别特征的核心挑战在于：类别之间通常没有自然的数值顺序关系，但模型需要数值输入。不同的编码方法适用于不同的基数（类别数量）和模型类型。

## Core Concepts

### One-Hot Encoding（独热编码）

将每个类别转换为一个二进制向量，只有一位为1：

$$\text{color} \in \{\text{red}, \text{green}, \text{blue}\} \to \begin{cases} \text{red}: [1, 0, 0] \\ \text{green}: [0, 1, 0] \\ \text{blue}: [0, 0, 1] \end{cases}$$

**优点**：不引入序关系，适用于所有模型，含义清晰
**缺点**：高基数特征（如城市、用户ID）会导致 **Dimensionality Explosion（维度爆炸）**
**注意**：对线性模型可以去掉一列（**Drop First，去首列**）避免多重共线性（$K-1$ 列即可完全表示 $K$ 个类别）

适用场景：低基数特征（$K \leq 20$），线性模型，逻辑回归

### Label Encoding（标签编码）

将每个类别映射为一个整数：

$$\text{red} \to 0, \quad \text{green} \to 1, \quad \text{blue} \to 2$$

**风险**：引入了虚假的序关系（模型可能认为 $\text{blue} > \text{green} > \text{red}$）
**安全使用场景**：树模型（决策树、随机森林、XGBoost/LightGBM）——它们基于分裂点，不受数值大小关系影响

对于线性模型和神经网络，标签编码通常不合适（除非类别确实有序，如教育水平：小学<中学<大学）。

### Ordinal Encoding（有序编码）

对有自然顺序的类别使用：

$$\text{low} \to 0, \quad \text{medium} \to 1, \quad \text{high} \to 2$$

与Label Encoding的区别：Ordinal Encoding是有意义的，反映了类别的真实序关系。

### Target Encoding（目标编码）

用目标变量的统计量（如均值）替换类别值：

$$\hat{y}_c = \lambda \bar{y}_c + (1-\lambda) \bar{y}_{\text{global}}$$

其中 $\bar{y}_c$ 是类别 $c$ 的目标均值，$\bar{y}_{\text{global}}$ 是全局目标均值，$\lambda$ 是正则化参数（**Smoothing Factor，平滑因子**）。

**平滑的必要性**：如果某类别只有很少的样本（如只有1个），其均值完全不可靠。平滑将稀有类别的编码拉向全局均值。常用的平滑公式：

$$\lambda = \frac{n_c}{n_c + m}$$

其中 $n_c$ 是类别 $c$ 的样本数，$m$ 是平滑参数（通常设为10-100）。$n_c$ 很小时 $\lambda \to 0$，编码接近全局均值。

**数据泄漏风险**：Target Encoding直接使用了目标变量，如果在全部训练数据上计算再应用到训练数据本身，会严重过拟合。

**防止泄漏的方法**：
1. **K-Fold Target Encoding（K折目标编码）**：将训练数据分为K折，每折使用其余K-1折的目标均值编码
2. **Leave-One-Out（留一法）**：每个样本使用除自身外所有同类别样本的目标均值
3. **添加噪声**：在编码值上添加随机噪声
4. **只在训练集上计算，严格应用到测试集**

CatBoost内置了一种称为 **Ordered Target Statistics（有序目标统计量）** 的Target Encoding方法，按时间顺序计算避免泄漏。

### Frequency Encoding（频率编码）

用类别出现的频率替换类别值：

$$\text{encode}(c) = \frac{\text{count}(c)}{n}$$

**优点**：简单、不需要目标变量、无泄漏风险、保持了类别的"重要性"信息
**缺点**：不同类别可能有相同频率（冲突）；不包含目标变量信息
**适用场景**：作为快速基线，或与其他编码方法组合

### Count Encoding（计数编码）

与频率编码类似，但使用原始计数而非比例：

$$\text{encode}(c) = \text{count}(c)$$

### Binary Encoding（二进制编码）

先将类别映射为整数，再将整数转换为二进制表示：

$$\text{类别A} \to 0 \to [0,0,0], \quad \text{类别B} \to 1 \to [0,0,1], \quad \text{类别C} \to 2 \to [0,1,0]$$

$K$ 个类别只需要 $\lceil\log_2 K\rceil$ 列，是One-Hot和Label Encoding之间的折中。适用于中等基数（$20 < K < 1000$）。

### Embedding Encoding（嵌入编码）

在神经网络中，将类别映射为可学习的低维稠密向量：

$$\text{embed}(c) = W_{c,:} \in \mathbb{R}^{d}$$

其中 $W \in \mathbb{R}^{K \times d}$ 是 **Embedding Matrix（嵌入矩阵）**，$d$ 是嵌入维度。

**维度选择经验法则**：$d \approx \min(50, K // 2)$ 或 $d \approx K^{0.25}$。

**优势**：
- 低维表示（$d \ll K$），适用于高基数特征
- 嵌入向量能捕捉类别之间的语义关系（如相似商品的嵌入更接近）
- 可以预训练（如word2vec、item2vec）然后作为特征使用
- 适合推荐系统中的用户/物品ID编码

**在树模型中使用嵌入**：先在神经网络中训练嵌入，然后提取嵌入向量作为特征输入XGBoost/LightGBM——这是工业界常用的技巧。

### Hashing Trick（哈希技巧）

$$\text{encode}(c) = \text{hash}(c) \mod n_{\text{features}}$$

将类别哈希到固定大小的特征空间。

**优点**：
- 固定维度，不依赖训练时看到的类别（处理 **OOV（Out-Of-Vocabulary，词汇表外）** 值）
- 内存效率高，无需存储类别映射表
- 适用于在线学习和流式数据

**缺点**：
- **Hash Collision（哈希冲突）**：不同类别可能映射到同一位置
- 不可逆（无法从哈希值恢复原始类别）
- 模型可解释性差

sklearn中的 `FeatureHasher` 和 Vowpal Wabbit都使用此方法。

### Handling Unseen Categories（处理未见类别）

生产中经常遇到训练时未出现的类别值：

| 策略 | 描述 | 适用编码 |
|------|------|---------|
| 映射到"unknown" | 所有未知类别统一处理 | One-Hot, Label |
| 使用全局统计量 | 用全局均值替代 | Target Encoding |
| 哈希 | 自然处理新类别 | Hashing Trick |
| 最近邻映射 | 找最相似的已知类别 | Embedding |

### Encoding Selection Guide（编码选择指南）

| 基数 | 模型类型 | 推荐编码 |
|------|---------|---------|
| 低 ($K \leq 10$) | 任意 | One-Hot |
| 中 ($10 < K \leq 100$) | 线性模型 | One-Hot + 正则化 或 Target Encoding |
| 中 ($10 < K \leq 100$) | 树模型 | Label 或 Target Encoding |
| 高 ($K > 100$) | 树模型 | Target Encoding 或 Frequency |
| 高 ($K > 100$) | 神经网络 | Embedding |
| 极高 ($K > 10^6$) | 任意 | Hashing Trick 或 Embedding |

## Implementation

```python
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder
from category_encoders import TargetEncoder, BinaryEncoder, HashingEncoder
import numpy as np

# One-Hot Encoding
ohe = OneHotEncoder(sparse_output=True, handle_unknown="ignore", drop="first")
X_ohe = ohe.fit_transform(X_train[["color"]])

# Target Encoding with smoothing (防泄漏需配合CV)
te = TargetEncoder(cols=["city"], smoothing=10)
X_train["city_encoded"] = te.fit_transform(X_train["city"], y_train)
X_test["city_encoded"] = te.transform(X_test["city"])

# Embedding in PyTorch
import torch.nn as nn
class CategoricalModel(nn.Module):
    def __init__(self, n_categories, embed_dim, n_numeric, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(n_categories, embed_dim)
        self.fc = nn.Linear(embed_dim + n_numeric, output_dim)
    def forward(self, cat_input, num_input):
        embedded = self.embedding(cat_input)
        combined = torch.cat([embedded, num_input], dim=1)
        return self.fc(combined)

# Hashing Trick
from sklearn.feature_extraction import FeatureHasher
hasher = FeatureHasher(n_features=1024, input_type="string")
X_hashed = hasher.transform(X_train["url"].values.reshape(-1, 1))
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| 编码方法选择 | "如何处理类别特征？" | 看基数和模型类型：低基数One-Hot，高基数Embedding/Hashing |
| Target Encoding泄漏 | 数据泄漏面试题 | 必须用K-Fold或LOO方式计算，不能在全部数据上 |
| 树模型 vs 线性模型 | 编码策略不同 | 树模型可以用Label Encoding；线性模型不能 |
| 高基数特征 | 推荐系统/NLP | Embedding是标准做法，可预训练 |
| OOV处理 | 生产部署 | Hashing自然处理；其他方法需要"unknown"桶 |

### Common Interview Questions

- **One-Hot何时不适用？** 高基数特征导致维度爆炸和稀疏性问题
- **Target Encoding如何防止数据泄漏？** K-Fold编码（每折用其余折的目标均值）或添加噪声+平滑
- **为什么Label Encoding对树模型安全但对线性模型不安全？** 树模型只比较大小做分裂，不假设数值间距；线性模型将数值差异直接作为系数的权重
- **Embedding vs One-Hot？** Embedding是低维稠密表示，能捕捉类别语义；One-Hot是高维稀疏表示，无语义
- **Hashing Trick的优缺点？** 优：固定维度、处理OOV；缺：哈希冲突、不可逆

## Key Takeaways

- One-Hot是低基数类别特征的标准选择，但高基数时导致维度爆炸
- Label Encoding只对树模型安全；线性模型需要One-Hot或其他方法
- Target Encoding强大但有数据泄漏风险——必须用K-Fold或LOO方式
- Embedding是高基数特征的最佳选择（神经网络场景），可预训练
- Hashing Trick适用于极高基数和在线学习场景
- Frequency/Count Encoding简单无泄漏，是好的快速基线
- 生产中必须考虑未见类别（OOV）的处理策略
- CatBoost内置的Ordered Target Statistics是Target Encoding的最佳实践
