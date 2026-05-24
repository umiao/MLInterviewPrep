# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Translate and expand framework_nodes 80-88 to Chinese with expansion."""
import os
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "mle_prep.db"
)

TRANSLATIONS = {}

# ============================================================
# Node 80: Text Features
# ============================================================
TRANSLATIONS[80] = r"""# Text Features

## Overview

**Text Feature Engineering（文本特征工程）** 将非结构化文本数据转换为机器学习模型可以处理的数值表示。这一领域涵盖了从经典的 **Bag-of-Words（词袋模型）** 到现代 **Transformer Embeddings（Transformer嵌入）** 的广泛方法。理解各种方法之间的权衡对于 **NLP (Natural Language Processing，自然语言处理)** 系统设计面试至关重要。

文本特征工程的核心挑战在于：如何在保留语义信息的同时，将变长、高维的文本数据映射到固定维度的数值空间。不同方法在表达能力、计算效率和可解释性之间做出不同的取舍。

## Core Concepts

### Bag-of-Words 与 TF-IDF

**Bag-of-Words (BoW，词袋模型)**：将文档表示为词频的计数向量，忽略词序。每个维度对应词汇表中的一个词，值为该词在文档中出现的次数。BoW 的主要局限在于忽略了词序和语义关系，但其简单高效，适合作为基线方法。

**TF-IDF (Term Frequency-Inverse Document Frequency，词频-逆文档频率)**：通过结合词频和逆文档频率来衡量词语在文档中的重要程度：

$$\text{TF-IDF}(t,d) = \text{TF}(t,d) \times \text{IDF}(t) = \frac{f_{t,d}}{\sum_t f_{t,d}} \times \log\frac{N}{|\{d: t \in d\}|}$$

其中 $f_{t,d}$ 是词 $t$ 在文档 $d$ 中的出现次数，$N$ 是文档总数，$|\{d: t \in d\}|$ 是包含词 $t$ 的文档数。

- **TF (Term Frequency，词频)**：衡量词在当前文档中的重要程度，出现越多越重要
- **IDF (Inverse Document Frequency，逆文档频率)**：衡量词的稀有程度，在越少文档中出现的词越有区分力

常用变体包括：
- **Sublinear TF（亚线性词频）**：使用 $1 + \log(\text{TF})$ 替代原始词频，抑制高频词的影响
- **Smooth IDF（平滑逆文档频率）**：使用 $\log\frac{N+1}{\text{df}+1} + 1$ 避免零除错误

### N-grams（N元组）

**N-grams（N元组）** 通过捕获局部词序来丰富文本表示：

- **Unigrams（一元组）**：单个词，如 "machine"、"learning"
- **Bigrams（二元组）**：连续词对，如 "machine learning"、"deep neural"
- **Trigrams（三元组）**：连续三个词，如 "deep neural network"
- **Character N-grams（字符N元组）**：子词级别的模式，如 "##ing"、"pre##"

字符级N元组的一个重要优势是能够处理 **OOV (Out-of-Vocabulary，词汇表外)** 词汇和拼写错误，因为它们在子词级别进行匹配。

### 文本预处理流水线

标准文本预处理步骤（顺序很重要）：

1. **Tokenization（分词）**：将文本分割为词元（tokens）
2. **Lowercasing（小写化）**：统一大小写
3. **Stop Word Removal（停用词移除）**：去掉 "the"、"is"、"at" 等高频低信息词
4. **Stemming/Lemmatization（词干提取/词形还原）**：将词归约到基本形式（"running" -> "run"）
5. **Rare Word Filtering（低频词过滤）**：移除出现次数过少的词

### 子词分词方法

现代NLP模型广泛使用子词分词方法来平衡词汇表大小和覆盖率：

- **BPE (Byte-Pair Encoding，字节对编码)**：迭代合并最频繁的字符对，用于GPT系列模型
- **WordPiece**：类似BPE但基于似然进行合并，用于BERT
- **SentencePiece**：语言无关的子词分词，直接在原始文本上操作，不需要预分词

这些方法可以有效处理OOV问题，同时保持合理的词汇表大小（通常30K-50K个token）。

### Word Embeddings（词嵌入）

**Word2Vec**（Mikolov等人提出）：将每个词映射到一个低维稠密向量，使语义相近的词在向量空间中距离较近。

- **CBOW (Continuous Bag-of-Words，连续词袋模型)**：从上下文词预测中心词，训练速度快，适合高频词
- **Skip-gram（跳字模型）**：从中心词预测上下文词，适合低频词和小数据集

$$P(w_o|w_i) = \frac{\exp(v_{w_o}'^T v_{w_i})}{\sum_{w=1}^{V}\exp(v_w'^T v_{w_i})}$$

其中 $v_{w_i}$ 是输入词的向量，$v_{w_o}'$ 是输出词的向量，$V$ 是词汇表大小。实际训练中使用 **Negative Sampling（负采样）** 或 **Hierarchical Softmax（层次Softmax）** 来加速计算。

**GloVe (Global Vectors，全局向量)**：通过分解词共现矩阵学习词向量：

$$\log X_{ij} = w_i^T \tilde{w}_j + b_i + \tilde{b}_j$$

其中 $X_{ij}$ 是词 $i$ 和词 $j$ 的共现次数。GloVe结合了矩阵分解的全局统计信息和局部上下文窗口的优点。

**FastText**：扩展Word2Vec，将每个词表示为其字符N元组嵌入的平均值。关键优势是能够为未见过的词生成有意义的嵌入向量。

### Sentence/Document Embeddings（句子/文档嵌入）

| 方法 | 质量 | 速度 | 适用场景 |
|------|------|------|---------|
| Average word vectors（词向量平均） | 一般 | 快 | 快速基线 |
| TF-IDF weighted average（TF-IDF加权平均） | 较好 | 快 | 改进基线 |
| **Sentence-BERT** | 高 | 中等 | 语义相似度计算 |
| OpenAI embeddings | 很高 | API调用 | 生产级检索系统 |

## Implementation

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# TF-IDF with n-grams
tfidf = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=5,
    max_df=0.95,
)
X = tfidf.fit_transform(documents)

# Sentence embeddings via sentence-transformers
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(documents, batch_size=32)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| TF-IDF vs. 嵌入 | "如何表示文本？" | TF-IDF：可解释、速度快；嵌入：捕获语义关系 |
| 降维 | 大规模词汇表 | Hash Vectorizer（哈希向量化器）、在TF-IDF上做Truncated SVD（截断奇异值分解） |
| NLP特征工程 | 文本分类 | 结合TF-IDF特征与手工特征（文本长度、实体计数等） |
| 嵌入微调 | 领域特定任务 | 在领域数据上微调Sentence-BERT用于检索 |

### Common Interview Questions

- [ ] 解释TF-IDF以及为什么IDF很重要
- [ ] 比较Word2Vec的CBOW和Skip-gram两种架构
- [ ] 如何处理词汇表外（OOV）的词？
- [ ] 什么时候使用TF-IDF而不是Transformer嵌入？
- [ ] 设计一个用于重复检测的文本相似度系统

## Key Takeaways

- [ ] TF-IDF：分类任务的强基线；速度快、可解释、无需训练
- [ ] Word2Vec/GloVe：稠密词级嵌入，捕获语义关系（如"国王-男人+女人=女王"）
- [ ] FastText：通过子词嵌入处理OOV问题，对形态丰富的语言特别有效
- [ ] Sentence-BERT：当前语义相似度和检索任务的首选方法
- [ ] 实践建议：从TF-IDF + 逻辑回归开始，效果不够时再升级到嵌入方法
"""

# ============================================================
# Node 81: Temporal Features
# ============================================================
TRANSLATIONS[81] = r"""# Temporal Features

## Overview

**Temporal Feature Engineering（时间特征工程）** 从时间戳和时间序列数据中提取模式，是预测、推荐系统和欺诈检测等领域的关键技术。核心挑战在于正确编码周期性模式、捕获时间依赖关系，同时避免 **Data Leakage（数据泄露）**。

时间特征工程的独特之处在于数据的有序性——未来信息不能用于预测过去。这一约束贯穿特征构建、交叉验证到模型评估的整个流程。

## Core Concepts

### Timestamp Decomposition（时间戳分解）

从原始时间戳中提取丰富的时间成分：

| 特征 | 取值范围 | 捕获的模式 |
|------|---------|-----------|
| Hour of day（小时） | 0-23 | 日内模式（高峰时段、凌晨低谷） |
| Day of week（星期几） | 0-6 | 周内模式（工作日/周末差异） |
| Month（月份） | 1-12 | 季节性模式 |
| Is holiday（是否节假日） | 0/1 | 节假日效应 |
| Time since event（距事件时间） | 连续值 | 时效性（上次购买、上次登录间隔） |
| Day of year（一年中第几天） | 1-366 | 年度周期 |
| Quarter（季度） | 1-4 | 季度性业务模式 |
| Is weekend（是否周末） | 0/1 | 周末/工作日二分特征 |

### Cyclical Encoding（周期性编码）

对于具有周期性的特征（如小时、星期几），直接使用数值会导致边界不连续问题（例如23点和0点在数值上差距很大，但实际上相邻）。使用正弦/余弦编码解决这一问题：

$$x_{\sin} = \sin\left(\frac{2\pi \cdot t}{T}\right), \quad x_{\cos} = \cos\left(\frac{2\pi \cdot t}{T}\right)$$

其中 $T$ 是周期长度（小时为24，星期为7，月份为12）。这种编码确保了：
- 23点和0点的编码值相邻（连续性）
- 每个时间点由两个值唯一确定（无信息损失）
- 适合线性模型和神经网络（树模型通常不需要）

### Lag Features（滞后特征）

对于时间序列数据，创建滞后值作为特征：

$$x_{t-1}, x_{t-2}, \ldots, x_{t-k}$$

**关键注意**：创建滞后特征前必须按时间排序，且不能使用未来数据。

**Rolling Statistics（滚动统计量）**：在固定窗口内计算均值、标准差、最小值、最大值：

$$\text{rolling\_mean}_{w}(t) = \frac{1}{w}\sum_{i=0}^{w-1} x_{t-i}$$

其中 $w$ 是窗口大小。常用窗口包括7天（周模式）、30天（月模式）、365天（年模式）。

**EMA (Exponential Moving Average，指数移动平均)**：对近期数据赋予更高权重：

$$\text{EMA}_t = \alpha \cdot x_t + (1-\alpha) \cdot \text{EMA}_{t-1}$$

其中 $\alpha \in (0, 1)$ 是平滑系数。$\alpha$ 越大，对近期数据越敏感。EMA的优势是不需要存储整个窗口的数据，计算效率高。

### Trend and Seasonality（趋势与季节性）

时间序列分解的三个核心成分：
- **Trend（趋势）**：长期方向性变化。通过线性回归或差分提取
- **Seasonality（季节性）**：周期性重复模式。通过傅里叶特征或季节分解提取
- **Residual（残差）**：去除趋势和季节性后的随机成分

**Fourier Features（傅里叶特征）** 用于捕获多重周期性：

$$x_k = \sin\left(\frac{2\pi k t}{T}\right), \quad x_{k+1} = \cos\left(\frac{2\pi k t}{T}\right), \quad k = 1, 2, \ldots, K$$

其中 $K$ 控制傅里叶级数的阶数。$K$ 越大，能捕获越复杂的季节性模式，但也增加了过拟合风险。通常 $K = 3\text{-}5$ 足以捕获主要周期。

### Time-Series Cross-Validation（时间序列交叉验证）

时间序列数据绝不能使用随机划分，否则会导致数据泄露（用未来预测过去）。

**Expanding Window（扩展窗口）**：训练集不断扩大

| 折 | 训练集 | 测试集 |
|----|-------|-------|
| 1 | $[1, T_1]$ | $[T_1+1, T_2]$ |
| 2 | $[1, T_2]$ | $[T_2+1, T_3]$ |
| 3 | $[1, T_3]$ | $[T_3+1, T_4]$ |

**Sliding Window（滑动窗口）**：固定大小的训练窗口。适用于旧数据相关性较低的场景（如用户行为随时间变化较大）。

**Gap Period（间隔期）**：在训练集和测试集之间设置间隔期，模拟实际部署中的预测延迟。

## Implementation

```python
import pandas as pd
import numpy as np

def create_temporal_features(df, date_col="timestamp"):
    dt = pd.to_datetime(df[date_col])
    df["hour"] = dt.dt.hour
    df["dow"] = dt.dt.dayofweek
    df["month"] = dt.dt.month

    # Cyclical encoding
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    # Lag features (careful: sort by time first!)
    df = df.sort_values(date_col)
    for lag in [1, 7, 30]:
        df[f"value_lag_{lag}"] = df["value"].shift(lag)

    # Rolling stats
    df["rolling_7d_mean"] = df["value"].rolling(7).mean()
    df["rolling_7d_std"] = df["value"].rolling(7).std()
    return df
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 周期性编码 | 时间/星期特征 | sin/cos保持周期性邻接关系 |
| 滞后特征泄露 | 时间序列CV | 绝不使用未来数据；使用扩展或滑动窗口CV |
| 时效性特征 | 用户行为建模 | "距上次操作的时间"是非常强的特征 |
| 节假日/事件标志 | 需求预测 | 已知事件的二值或分类标志 |

### Common Interview Questions

- [ ] 如何为线性模型编码"一天中的小时"特征？
- [ ] 使用滞后特征时数据泄露的风险是什么？
- [ ] 如何进行时间序列交叉验证？
- [ ] 设计用于预测次日需求的特征
- [ ] 如何同时捕获日级和周级的季节性模式？

## Key Takeaways

- [ ] 周期性编码（sin/cos）对非树模型处理周期性特征至关重要
- [ ] 滞后特征 + 滚动统计量是时间序列特征工程的核心
- [ ] 创建滞后特征前务必按时间排序；绝不打乱时间序列数据
- [ ] 时间序列CV：使用扩展窗口或前进式验证，绝不使用随机划分
- [ ] 时效性特征（距X的时间）是推荐系统中最强大的预测因子之一
"""

# ============================================================
# Node 82: Missing Value Handling
# ============================================================
TRANSLATIONS[82] = r"""# Missing Value Handling

## Overview

**Missing Value Handling（缺失值处理）** 是实际机器学习项目中不可避免的环节。正确处理缺失数据可以防止偏差和信息损失。面试中重点考察对缺失类型的理解、填充策略的选择，以及不同模型如何原生处理缺失值。

在生产环境中，缺失数据的处理策略直接影响模型的公平性和可靠性。不当处理可能导致系统性偏差，特别是当缺失不是随机发生时。

## Core Concepts

### Types of Missingness（缺失类型）

理解缺失机制是选择正确处理策略的基础：

| 类型 | 全称与定义 | 示例 | 处理含义 |
|------|-----------|------|---------|
| **MCAR** | **Missing Completely At Random（完全随机缺失）**：缺失与任何变量（包括自身）无关 | 传感器随机故障 | 可安全删除；不引入偏差 |
| **MAR** | **Missing At Random（随机缺失）**：缺失取决于已观测的变量 | 高收入人群更倾向于不填写收入字段 | 可使用已观测特征进行填充 |
| **MNAR** | **Missing Not At Random（非随机缺失）**：缺失取决于未观测的变量（包括缺失值本身） | 病情严重的患者更可能错过随访 | 最困难；可能需要领域建模 |

**形式化定义**：设 $Y$ 为完整数据，$R$ 为缺失指示矩阵（$R_{ij} = 1$ 表示第 $i$ 行第 $j$ 列缺失），则：
- MCAR: $P(R | Y) = P(R)$，即缺失概率与数据值完全无关
- MAR: $P(R | Y) = P(R | Y_{\text{obs}})$，即缺失概率仅取决于已观测值
- MNAR: $P(R | Y) \neq P(R | Y_{\text{obs}})$，即缺失概率取决于未观测值

### Imputation Strategies（填充策略）

**Simple Imputation（简单填充）**：
- **Mean/Median（均值/中位数）**：速度快但会降低数据方差，使分布变窄
- **Mode（众数）**：适用于分类特征
- **Constant（常数）**：使用哨兵值（如 -1、"UNKNOWN"），但需注意某些模型可能将哨兵值视为有意义的数值

**Model-Based Imputation（基于模型的填充）**：

- **KNN Imputer（K近邻填充）**：使用 $k$ 个最近邻的值来填充缺失值。距离计算仅基于非缺失特征。优点是捕获局部结构，缺点是计算开销大（$O(n^2)$）

- **Iterative Imputer / MICE (Multiple Imputation by Chained Equations，链式方程多重填充)**：将每个含缺失的特征建模为其他特征的函数，迭代进行：
  1. 用简单方法初始化所有缺失值
  2. 对每个含缺失的特征，以其他特征为输入训练回归模型
  3. 用模型预测值替换该特征的缺失值
  4. 重复步骤2-3直到收敛

  MICE是统计分析中的"金标准"方法，能够生成多组填充结果以量化不确定性。

- **Matrix Factorization（矩阵分解）**：适用于推荐系统风格的缺失数据（用户-物品矩阵）

### Indicator Features（缺失指示特征）

添加二值列 $\text{is\_missing}_j$ 来保留缺失信息：

$$x_{\text{is\_missing},j} = \begin{cases} 1 & \text{if } x_j \text{ is missing} \\ 0 & \text{otherwise} \end{cases}$$

缺失指示特征的价值往往超过填充值本身，因为：
- 缺失本身可能是预测性信号（如用户不填写某字段可能反映特定行为模式）
- 下游模型可以学习针对缺失和非缺失数据使用不同策略
- 在MNAR情况下，这种信息尤其重要

### Native Handling by Models（模型的原生缺失处理）

| 模型 | 处理缺失？ | 方式 |
|------|-----------|------|
| **XGBoost** | 是 | 在每个分裂节点学习最优默认方向（缺失值走左还是走右） |
| **LightGBM** | 是 | 将NaN分组到单独的bin中 |
| **CatBoost** | 是 | 内部NaN编码机制 |
| 线性模型 | 否 | 必须填充 |
| 神经网络 | 否 | 必须填充或使用masking（遮蔽） |

## Implementation

```python
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
import numpy as np

# Strategy: impute + indicator
def add_missing_indicators(X, cols):
    for col in cols:
        X[f"{col}_missing"] = X[col].isna().astype(int)
    return X

# Pipeline with KNN imputation
pipe = Pipeline([
    ("imputer", KNNImputer(n_neighbors=5, weights="distance")),
    ("model", model),
])

# For tree models: just pass NaN through
# XGBoost handles it natively
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 缺失作为特征 | 任何流水线 | 缺失指示特征通常有预测能力 |
| MNAR处理 | 医疗/金融数据 | 缺失本身是信息性的；需显式建模 |
| 测试时缺失 | 生产部署 | 相同的填充流水线必须适用于新数据 |
| 多重填充 | 统计推断 | 单次填充低估不确定性；MICE是金标准 |

### Common Interview Questions

- [ ] 如何判断数据是MCAR、MAR还是MNAR？
- [ ] 什么时候应该删除行而不是填充？
- [ ] 为什么要添加缺失指示列？
- [ ] XGBoost内部如何处理缺失值？
- [ ] 为生产推荐系统设计缺失值处理策略

## Key Takeaways

- [ ] 在填充的同时始终添加缺失指示列
- [ ] 树模型（XGBoost/LightGBM）原生处理缺失值——数据稀疏时优先选用
- [ ] 均值填充简单但会向下偏置方差；需配合指示特征使用
- [ ] MICE（迭代填充器）是统计分析的金标准方法
- [ ] 填充器仅在训练数据上拟合，应用到测试数据（防止泄露）
"""

# ============================================================
# Node 83: Feature Selection
# ============================================================
TRANSLATIONS[83] = r"""# Feature Selection

## Overview

**Feature Selection（特征选择）** 通过减少特征维度来防止过拟合、提高可解释性并加速训练。三大方法类别为 **Filter（过滤法）**、**Wrapper（包装法）** 和 **Embedded（嵌入法）**。理解每种方法的适用场景和局限性对ML流水线设计面试至关重要。

特征选择不仅是模型性能优化的手段，也是理解数据和构建可解释模型的重要工具。在高维数据场景下（如基因组学、NLP），特征选择往往是训练可行模型的前提条件。

## Core Concepts

### Filter Methods（过滤法）

过滤法独立于模型评分特征，计算成本低，适合大规模特征空间的预筛选：

**Mutual Information (MI，互信息)**：衡量两个变量之间的统计依赖程度：

$$I(X; Y) = \sum_{x,y} p(x,y) \log \frac{p(x,y)}{p(x)p(y)}$$

互信息 $I(X;Y) = 0$ 当且仅当 $X$ 和 $Y$ 相互独立。与Pearson相关系数不同，互信息能捕获非线性依赖关系，适用于分类和回归任务。

**Correlation-based（基于相关性）**：Pearson相关系数衡量线性关系。通常移除特征间相关性 $|r| > 0.95$ 的冗余特征以解决 **Multicollinearity（多重共线性）** 问题。多重共线性会导致线性模型的系数不稳定。

**Variance Threshold（方差阈值）**：移除近常数特征（$\text{Var}(X_j) < \epsilon$）。这是最简单的过滤方法，但能快速去除无信息特征。

**Chi-squared Test（卡方检验）**：用于分类特征与分类目标之间的独立性检验。检验统计量衡量观测频率与期望频率之间的偏差。

### Wrapper Methods（包装法）

包装法使用模型性能来评估特征子集，效果通常最好，但计算成本最高：

- **Forward Selection（前向选择）**：从空集开始，逐步添加使性能提升最大的特征
- **Backward Elimination（后向消除）**：从全部特征开始，逐步移除影响最小的特征
- **RFE (Recursive Feature Elimination，递归特征消除)**：训练模型，移除最不重要的特征，重复此过程

计算复杂度：每步需要 $O(d)$ 次模型训练，其中 $d$ 是特征数量。对于大规模特征空间不太实际。

### Embedded Methods（嵌入法）

特征选择内置于模型训练过程中，兼顾效果和效率：

**L1 Regularization / Lasso（L1正则化/套索回归）**：通过L1惩罚项将系数驱动为零。系数 $w_j = 0$ 的特征被自动消除。L1正则化产生稀疏解的数学原因是L1球在坐标轴上有"尖角"，使得最优解更容易落在坐标轴上。

**Tree-based Importance（基于树的重要性）**：

- **Impurity-based（基于不纯度）**：累加特征 $j$ 在所有分裂节点上的Gini/熵减少量
- **Permutation Importance（置换重要性）**：打乱特征 $j$ 的值后衡量精度下降

$$\text{PI}_j = \text{score}_{\text{original}} - \text{score}_{\text{permuted}_j}$$

**注意**：不纯度重要性对高基数特征（如ID类特征）存在偏差，因为这类特征天然有更多分裂机会。置换重要性更公正。

**SHAP (SHapley Additive exPlanations，SHAP值)**：基于博弈论的Shapley值，提供理论上有保证的特征重要性度量：

$$\phi_j = \sum_{S \subseteq F \setminus \{j\}} \frac{|S|!(|F|-|S|-1)!}{|F|!}[f(S \cup \{j\}) - f(S)]$$

其中 $F$ 是全部特征集合，$S$ 是不含特征 $j$ 的任意子集。SHAP值衡量的是特征 $j$ 在所有可能的特征组合中的平均边际贡献。

### 方法对比表

| 方法类别 | 代表方法 | 优点 | 缺点 | 适用场景 |
|---------|---------|------|------|---------|
| Filter | MI, 相关性, 卡方 | 计算快，与模型无关 | 忽略特征交互 | 大规模预筛选 |
| Wrapper | RFE, 前向/后向选择 | 考虑特征交互 | 计算昂贵 | 中小规模特征集 |
| Embedded | L1, 树重要性, SHAP | 训练中自动选择 | 与特定模型绑定 | 通用场景 |

## Implementation

```python
from sklearn.feature_selection import (
    SelectKBest, mutual_info_classif, RFE
)
from sklearn.ensemble import RandomForestClassifier

# Filter: mutual information
selector = SelectKBest(mutual_info_classif, k=20)
X_selected = selector.fit_transform(X_train, y_train)

# Embedded: L1 with stability selection
from sklearn.linear_model import LogisticRegression
lr = LogisticRegression(penalty="l1", solver="saga", C=0.1)
lr.fit(X_train, y_train)
selected = [f for f, w in zip(features, lr.coef_[0]) if abs(w) > 0]

# SHAP
import shap
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 先过滤后建模 | 大特征空间 | 过滤法成本低；先移除明显噪声再用昂贵方法 |
| 置换 vs. 不纯度重要性 | 树模型 | 不纯度重要性对高基数特征有偏差 |
| 生产环境中的SHAP | 部署中的特征重要性 | SHAP与模型无关且有理论保证 |
| 特征选择流水线 | 系统设计 | 特征仓库应随时间追踪特征重要性 |

### Common Interview Questions

- [ ] 比较过滤法、包装法和嵌入法
- [ ] 为什么不纯度重要性对高基数特征存在偏差？
- [ ] L1正则化如何实现特征选择？
- [ ] 什么时候使用SHAP而不是置换重要性？
- [ ] 为10K特征的模型设计特征选择流水线

## Key Takeaways

- [ ] 过滤法（互信息、相关性）是快速预筛工具
- [ ] L1/Lasso：通过稀疏性实现嵌入式特征选择
- [ ] 置换重要性优于不纯度重要性（偏差更小）
- [ ] SHAP值：基于博弈论的特征重要性金标准
- [ ] 实践中：组合多种方法——过滤（廉价）、嵌入（训练时）、SHAP（解释时）
"""

# ============================================================
# Node 84: Oversampling
# ============================================================
TRANSLATIONS[84] = r"""# Oversampling Techniques

## Overview

**Class Imbalance（类别不平衡）** 是指一个类别的样本数量远超其他类别（如欺诈检测中正例仅占0.1%）。**Oversampling（过采样）** 通过为少数类创建合成样本来平衡训练分布。理解何时以及如何进行过采样对构建实际ML系统至关重要。

类别不平衡的核心问题在于模型倾向于"偷懒"——预测所有样本为多数类即可获得很高的准确率，但这在实际业务中是无用的。过采样是解决这一问题的方法之一。

## Core Concepts

### Random Oversampling（随机过采样）

最简单的方法：随机复制少数类样本。优点是简单直接，缺点是容易导致对特定样本的 **Overfitting（过拟合）**，因为模型看到完全相同的样本多次。

### SMOTE (Synthetic Minority Over-sampling Technique，合成少数类过采样技术)

通过在少数类邻居之间插值来生成合成样本，是最广泛使用的过采样方法：

**算法步骤**：
1. 对少数类样本 $x_i$，找到其 $k$ 个最近的少数类邻居
2. 随机选择一个邻居 $x_{nn}$
3. 创建合成样本：

$$x_{\text{new}} = x_i + \lambda(x_{nn} - x_i), \quad \lambda \sim U(0,1)$$

其中 $\lambda$ 是从均匀分布 $U(0,1)$ 中采样的随机数。这确保新样本落在 $x_i$ 和 $x_{nn}$ 之间的线段上。

**SMOTE变体**：

| 变体 | 改进点 | 适用场景 |
|------|-------|---------|
| **SMOTE** | 在邻居间插值 | 通用基线 |
| **Borderline-SMOTE（边界SMOTE）** | 仅对边界点进行过采样 | 噪声决策边界 |
| **ADASYN (Adaptive Synthetic，自适应合成)** | 对更难分类的样本生成更多合成样本 | 自适应难度调整 |
| **SMOTE-ENN** | SMOTE + ENN (Edited Nearest Neighbors，编辑最近邻) 清洗 | 更清晰的决策边界 |
| **SMOTE-NC** | 处理数值+分类混合特征 | 混合特征类型的数据 |

### Important Rules（重要规则）

1. **仅对训练数据过采样**：绝不应用于验证/测试集
2. **划分后再过采样**：先做train/test split，再对训练集过采样，防止数据泄露
3. **结合欠采样使用**：SMOTE + 对多数类随机欠采样通常效果最好
4. **先考虑替代方案**：类别权重、**Focal Loss（焦点损失）**、阈值调整可能更简单有效

### When NOT to Oversample（何时不应过采样）

- 树模型有原生类别权重支持时（如XGBoost的 `scale_pos_weight`），直接用权重更高效
- 数据集非常大时，欠采样多数类可能更好（减少训练时间）
- 少数类样本极少（$< 10$）时——SMOTE无法有效工作，因为难以找到有意义的邻居
- 特征空间维度很高时——高维空间中"邻居"的概念变得模糊

### 过采样对评估指标的影响

过采样改变了训练分布，因此：
- 评估必须在原始（不平衡）测试集上进行
- 不能使用 **Accuracy（准确率）** 作为评估指标
- 应使用 **AUC-PR (Area Under Precision-Recall Curve，精确率-召回率曲线下面积)**、**F1 Score** 或 **AUC-ROC**

## Implementation

```python
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.combine import SMOTETomek
from imblearn.pipeline import Pipeline as ImbPipeline

# SMOTE in a pipeline (safe: only applies to training)
pipe = ImbPipeline([
    ("smote", SMOTE(sampling_strategy=0.5, k_neighbors=5)),
    ("model", XGBClassifier(scale_pos_weight=1)),
])
pipe.fit(X_train, y_train)
# Evaluation on original (imbalanced) test set
y_pred = pipe.predict(X_test)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| SMOTE的位置 | ML流水线设计 | 必须在CV循环内部，仅应用于训练折 |
| SMOTE + 欠采样 | 严重不平衡 | 组合使用效果最佳（如SMOTETomek） |
| 过采样的替代方案 | 系统设计 | 类别权重、代价敏感学习、阈值调整 |
| 指标选择 | 不平衡评估 | 使用AUC-PR、F1，不用准确率 |

### Common Interview Questions

- [ ] 解释SMOTE及其生成合成样本的原理
- [ ] 为什么过采样必须在train/test划分之后进行？
- [ ] 什么时候使用类别权重而不是SMOTE？
- [ ] SMOTE的局限性有哪些？
- [ ] 设计一个处理0.01%正例率的欺诈检测流水线

## Key Takeaways

- [ ] SMOTE：在少数类邻居间插值——标准的过采样方法
- [ ] 过采样始终在CV内部进行，绝不在划分之前
- [ ] 类别权重（如XGBoost的 `scale_pos_weight`）更简单，通常足够
- [ ] 组合使用SMOTE与欠采样（SMOTETomek, SMOTE-ENN）可获得更清晰的边界
- [ ] 在原始不平衡测试集上使用AUC-PR或F1评估，绝不用准确率
"""

# ============================================================
# Node 85: Loss Reweighting
# ============================================================
TRANSLATIONS[85] = r"""# Loss Reweighting

## Overview

**Loss Reweighting（损失重加权）** 通过为少数类错误分配更高的损失权重来解决类别不平衡问题。与过采样不同，它不创建合成数据，而是改变优化目标。通常比重采样方法更简单且更有效。

损失重加权的核心思想是：通过调整损失函数中不同类别的权重，使模型在优化过程中更关注少数类的正确分类。这等效于改变决策边界的位置。

## Core Concepts

### Inverse Frequency Weighting（逆频率加权）

将每个类别的权重设为其频率的倒数：

$$w_c = \frac{N}{C \cdot n_c}$$

其中 $N$ 是总样本数，$C$ 是类别数量，$n_c$ 是第 $c$ 类的样本数。这样少数类获得更高权重，多数类获得更低权重。

**Effective Number Weighting（有效样本数加权）**（Cui等人，2019年提出）：

$$w_c = \frac{1 - \beta}{1 - \beta^{n_c}}, \quad \beta \in [0, 1)$$

当 $\beta \to 1$ 时，趋近于逆频率加权。$\beta = 0.999$ 常用于 **Long-tailed Distribution（长尾分布）** 数据。有效样本数的概念认为，随着样本增加，新增的信息量递减（数据冗余效应）。

### Weighted Loss Functions（加权损失函数）

**Weighted Cross-Entropy（加权交叉熵）**：

$$\mathcal{L} = -\frac{1}{n}\sum_i w_{y_i} \left[y_i \log \hat{p}_i + (1-y_i)\log(1-\hat{p}_i)\right]$$

其中 $w_{y_i}$ 是样本 $i$ 所属类别的权重。本质上是通过权重让少数类的每个错误"更痛"。

**Focal Loss（焦点损失）**（Lin等人，2017年提出，最初用于目标检测中的RetinaNet）：

$$FL(p_t) = -\alpha_t (1-p_t)^\gamma \log(p_t)$$

其中 $p_t$ 是模型对正确类别的预测概率，$\gamma > 0$ 是聚焦参数，$\alpha_t$ 是类别平衡因子。

**Focal Loss的关键机制**：
- $(1-p_t)^\gamma$ 项自动降低已正确分类样本（"简单样本"）的损失
- 当 $\gamma = 0$ 时退化为标准交叉熵
- 标准设置为 $\gamma = 2, \alpha = 0.25$
- 对于被正确分类且 $p_t = 0.9$ 的样本，$\gamma = 2$ 时损失减少为标准交叉熵的1/100

### Cost-Sensitive Learning（代价敏感学习）

当不同类型的误分类有不同的业务代价时：

$$\text{Expected Cost} = C_{FP} \cdot P(FP) + C_{FN} \cdot P(FN)$$

其中 $C_{FP}$ 是 **False Positive（假阳性/误报）** 的代价，$C_{FN}$ 是 **False Negative（假阴性/漏报）** 的代价。

设正类权重 $= C_{FN}/C_{FP}$。典型应用场景：
- 医学诊断：漏诊疾病（FN）远比误诊（FP）代价高
- 欺诈检测：放过欺诈交易（FN）的财务损失远大于误标正常交易（FP）
- 垃圾邮件过滤：误将正常邮件标为垃圾（FP）的用户体验损失大于漏过垃圾邮件（FN）

### Framework-Specific Implementation（框架实现）

| 框架 | 参数设置 |
|------|---------|
| **sklearn** | `class_weight="balanced"` 或自定义字典 |
| **XGBoost** | `scale_pos_weight = n_neg / n_pos` |
| **LightGBM** | `is_unbalance=True` 或 `scale_pos_weight` |
| **PyTorch** | `weight` 张量传入 `nn.CrossEntropyLoss` |
| **TensorFlow** | `class_weight` 字典传入 `model.fit()` |

### 重加权后的校准问题

**重要提示**：损失重加权会改变模型输出的概率校准。重加权后的预测概率不再反映真实概率，因为优化目标已被修改。如果下游需要校准的概率（如广告竞价），必须在重加权后使用 **Platt Scaling（Platt缩放）** 或 **Isotonic Regression（保序回归）** 重新校准。

## Implementation

```python
import torch
import torch.nn as nn
import numpy as np

# Inverse frequency weights
class_counts = np.bincount(y_train)
weights = 1.0 / class_counts
weights = weights / weights.sum() * len(class_counts)
loss_fn = nn.CrossEntropyLoss(
    weight=torch.tensor(weights, dtype=torch.float32)
)

# XGBoost
from xgboost import XGBClassifier
model = XGBClassifier(
    scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1])
)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 权重 vs. 过采样 | "如何处理不平衡？" | 权重：无额外数据，无泄露风险；过采样：少数类极少时更好 |
| Focal Loss动机 | 目标检测 | 难例挖掘无需显式采样 |
| 业务代价对齐 | "假阴性的代价？" | 将业务代价映射到类别权重 |
| 重加权后的校准 | 需要概率估计 | 重加权偏置概率；需用Platt Scaling重校准 |

### Common Interview Questions

- [ ] XGBoost中 `scale_pos_weight` 是如何工作的？
- [ ] 比较类别权重与SMOTE处理不平衡的优缺点
- [ ] 什么时候使用Focal Loss而不是加权交叉熵？
- [ ] 类别权重如何影响决策边界？
- [ ] 应用类别权重后，预测概率还是校准的吗？

## Key Takeaways

- [ ] 类别权重比过采样更简单：无合成数据，无泄露风险
- [ ] `scale_pos_weight = n_neg/n_pos` 是XGBoost中最常用的方法
- [ ] Focal Loss：减少已正确分类样本的损失，在极端不平衡时效果优越
- [ ] 重加权移动决策边界但会破坏概率校准——需重新校准
- [ ] 代价敏感学习：将权重与业务代价对齐（FN vs. FP的不对称性）
"""

# ============================================================
# Node 86: Cross-Validation
# ============================================================
TRANSLATIONS[86] = r"""# Cross-Validation

## Overview

**Cross-Validation (CV，交叉验证)** 用于估计模型的泛化性能，是超参数调优和模型选择的基础工具。理解CV策略、其假设条件以及常见陷阱（如数据泄露）是MLE面试的基本要求。

CV的核心价值在于更充分地利用有限数据——每个样本既被用作训练也被用作验证，从而获得更可靠的性能估计。

## Core Concepts

### K-Fold Cross-Validation（K折交叉验证）

将数据分为 $K$ 个等大的折。每次用 $K-1$ 个折训练，剩余1个折验证，重复 $K$ 次：

$$\text{CV Score} = \frac{1}{K}\sum_{k=1}^{K} \text{Score}(f^{(-k)}, D_k)$$

其中 $f^{(-k)}$ 是不含第 $k$ 折训练的模型，$D_k$ 是第 $k$ 个验证折。

标准选择：$K = 5$ 或 $K = 10$。权衡关系：

- 更大的 $K$：每个训练集更大，偏差更低（更接近用全部数据训练的效果）
- 更大的 $K$：验证集更小，方差更高（单折估计更不稳定）
- 更大的 $K$：计算成本更高（需训练更多模型）

### CV估计的偏差-方差

CV估计器本身也有偏差和方差：
- **偏差**来源：训练集只有 $\frac{K-1}{K}$ 的数据，模型比用全部数据训练时略弱
- **方差**来源：各折验证集之间有重叠的训练数据，使得各折的得分不独立
- $K = n$（LOO）偏差最低但方差最高；$K = 5$ 在偏差-方差之间取得较好平衡

### Stratified K-Fold（分层K折）

在每个折中保持类别比例不变。对于不平衡数据集至关重要，否则某些折可能完全不包含少数类样本。

### Leave-One-Out (LOO，留一法)

$K = n$（每个样本单独作为一个折）。几乎无偏但方差高且计算量大。适用于样本极少的数据集。计算复杂度为 $O(n)$ 次模型训练。

### Time Series CV（时间序列交叉验证）

时间数据有序，不能使用随机划分（否则会从未来泄露信息到过去）。

**Expanding Window（扩展窗口）**：

| 折 | 训练集 | 测试集 |
|----|-------|-------|
| 1 | $[1, T_1]$ | $[T_1+1, T_2]$ |
| 2 | $[1, T_2]$ | $[T_2+1, T_3]$ |
| 3 | $[1, T_3]$ | $[T_3+1, T_4]$ |

**Sliding Window（滑动窗口）**：固定大小的训练窗口。当旧数据相关性较低时更合适。

**Gap Period（间隔期）**：在训练和测试之间设置间隔，模拟实际预测延迟。sklearn的 `TimeSeriesSplit` 支持 `gap` 参数。

### Group K-Fold（分组K折）

当样本存在自然分组时（如同一用户的多条记录、同一患者的多次检查）。确保同一组的所有样本在同一折中。防止同一实体同时出现在训练和测试集中造成的信息泄露。

典型场景：
- 用户行为数据：按用户ID分组
- 医疗数据：按患者ID分组
- 图像数据：按来源/拍摄地点分组

### Nested Cross-Validation（嵌套交叉验证）

外层循环估计泛化性能，内层循环调超参数：

```
外层折1: [训练集: 内层CV调参] -> [测试集: 评估最优超参]
外层折2: [训练集: 内层CV调参] -> [测试集: 评估最优超参]
...
```

嵌套CV防止了"在评估数据上调参"导致的乐观偏差。当同时需要模型选择和性能估计时必须使用嵌套CV。

**非嵌套CV的问题**：如果在同一组CV折上既调参又报告性能，调参过程中对验证折的多次评估会导致对该折的间接"过拟合"，使性能估计偏高。

## Implementation

```python
from sklearn.model_selection import (
    StratifiedKFold, TimeSeriesSplit, GroupKFold, cross_val_score
)

# Stratified K-Fold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=skf, scoring="roc_auc")
print(f"AUC: {scores.mean():.3f} +/- {scores.std():.3f}")

# Time Series Split
tscv = TimeSeriesSplit(n_splits=5, gap=7)  # 7-day gap
for train_idx, test_idx in tscv.split(X):
    model.fit(X[train_idx], y[train_idx])
    score = model.score(X[test_idx], y[test_idx])

# Group K-Fold (e.g., by user_id)
gkf = GroupKFold(n_splits=5)
scores = cross_val_score(model, X, y, cv=gkf, groups=user_ids)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| CV策略选择 | "如何评估？" | 随机：分层K折；时间：TimeSeriesSplit；分组：GroupKFold |
| CV中的数据泄露 | 特征工程 | 预处理必须在CV循环内部（仅在训练折上fit） |
| 嵌套CV | 模型比较 | 外层评估，内层调参——防止对CV的过拟合 |
| CV vs. 留出集 | 小数据 vs. 大数据 | CV适合小数据（更可靠）；留出集适合大数据（更快） |

### Common Interview Questions

- [ ] 为什么分层K折对不平衡数据很重要？
- [ ] 交叉验证中数据泄露是如何发生的？
- [ ] 什么时候必须使用时间序列CV而不是随机CV？
- [ ] K折和嵌套CV有什么区别？
- [ ] 如何在5折和10折CV之间做选择？

## Key Takeaways

- [ ] K折：i.i.d.数据的标准方法。分类任务使用分层K折
- [ ] 时间序列：必须使用时间划分——绝不随机
- [ ] 分组K折：数据有自然分组时使用（用户、会话、患者）
- [ ] 所有预处理必须在CV循环内部以防止泄露
- [ ] 同时调参和评估性能时需使用嵌套CV
"""

# ============================================================
# Node 87: Hyperparameter Tuning
# ============================================================
TRANSLATIONS[87] = r"""# Hyperparameter Tuning

## Overview

**Hyperparameter Tuning（超参数调优）** 优化那些在训练过程中不被学习的参数（如学习率、正则化强度、树深度）。高效的调优策略可以决定模型是平庸还是优秀。面试中考察对搜索策略及其权衡的理解。

超参数调优本质上是一个 **Black-box Optimization（黑盒优化）** 问题：目标函数（模型在验证集上的性能）昂贵且没有解析梯度。

## Core Concepts

### Grid Search（网格搜索）

穷举评估所有参数组合。保证找到网格中的最优解，但计算成本呈指数增长：

对于 $d$ 个超参数，每个有 $p$ 个候选值，总共需要 $O(p^d)$ 次评估。当 $d > 3$ 时通常不可行。

**优点**：简单可靠，容易并行化
**缺点**：受维度灾难限制，且在不重要的维度上浪费大量计算

### Random Search（随机搜索）（Bergstra & Bengio, 2012年提出）

从参数空间中随机采样超参数组合。比网格搜索更高效：

**核心洞察**：大多数目标函数仅取决于少数几个超参数。随机搜索在相同预算下比网格搜索更彻底地探索重要维度。

直觉理解：假设有两个超参数，但只有一个真正重要。网格搜索 $5 \times 5 = 25$ 次评估只测试了重要维度的5个不同值。随机搜索25次评估能测试重要维度的约25个不同值，覆盖率提高5倍。

对于 $n$ 次随机试验和 $d$ 个超参数，如果只有 $d_{\text{eff}}$ 个重要：
- 随机搜索：在重要维度上有效评估 $n^{d/d_{\text{eff}}}$ 次
- 网格搜索：每个维度仅 $n^{1/d}$ 次评估

### Bayesian Optimization（贝叶斯优化）

构建目标函数的 **Surrogate Model（代理模型）**（通常是 **GP (Gaussian Process，高斯过程)** 或 **TPE (Tree-structured Parzen Estimator，树结构Parzen估计器)**），指导搜索方向：

**算法流程**：
1. 用代理模型拟合已观测的 $(x, y)$ 对
2. 通过最大化 **Acquisition Function（采集函数）** 选择下一个评估点 $x$
3. 在 $x$ 处评估真实目标函数
4. 更新代理模型，重复

**Expected Improvement (EI，期望改进)**：最常用的采集函数：

$$\text{EI}(x) = E[\max(0, f(x) - f(x^*))]$$

其中 $f(x^*)$ 是当前最优值。EI平衡了：
- **Exploration（探索）**：在不确定性大的区域评估（代理模型预测方差大）
- **Exploitation（利用）**：在预测值好的区域评估（代理模型预测均值高）

其他采集函数包括 **UCB (Upper Confidence Bound，置信上界)** 和 **PI (Probability of Improvement，改进概率)**。

### Hyperband / ASHA（超带/异步连续减半算法）

**Multi-fidelity Methods（多保真度方法）**：用少量资源训练大量配置，逐步淘汰差的配置：

**Successive Halving（连续减半）** 是核心原语：
1. 以最小预算 $b_{\min}$ 启动 $n$ 个随机配置
2. 评估性能，保留前 $1/\eta$ 比例的配置
3. 将预算增加 $\eta$ 倍，重复直到达到 $b_{\max}$

**Hyperband** 在不同的初始配置数和最小预算之间进行权衡，运行多轮Successive Halving。

**ASHA (Asynchronous Successive Halving Algorithm，异步连续减半)** 是Hyperband的异步版本，适合分布式环境，不需要等待所有任务完成才做决策。

实际工具推荐：
- **Optuna**：Python首选，支持TPE、CMA-ES等多种采样器，pruning支持好
- **Ray Tune**：适合分布式调优，与多个框架集成好

### Key Hyperparameters by Model（各模型关键超参数）

| 模型 | 关键超参数 | 搜索范围 | 搜索尺度 |
|------|-----------|---------|---------|
| **XGBoost** | `max_depth`, `learning_rate`, `n_estimators` | [3-10], [0.01-0.3], [100-1000] | 线性, 对数, 线性 |
| 神经网络 | `lr`, `batch_size`, `dropout`, `hidden_dim` | [1e-5-1e-2], [16-512], [0.1-0.5], [64-1024] | 对数, 对数, 线性, 对数 |
| **SVM (Support Vector Machine，支持向量机)** | `C`, `gamma` | [1e-3-1e3], [1e-4-1e1] | 对数, 对数 |
| **Random Forest（随机森林）** | `n_estimators`, `max_depth`, `min_samples_leaf` | [100-1000], [5-30], [1-20] | 线性, 线性, 线性 |

**对数尺度搜索**：对于学习率和正则化参数，使用对数均匀采样 $\text{lr} \sim 10^{U(-4, -1)}$，因为这些参数的数量级比精确值更重要。

### 调优最佳实践

1. **先调最重要的参数**：如XGBoost先调 `learning_rate` 和 `max_depth`
2. **使用Early Stopping（早停）** 代替搜索 `n_estimators`
3. **使用嵌套CV** 避免对验证集过拟合
4. **固定随机种子** 确保可复现性
5. **记录所有实验** 用于分析参数敏感度

## Implementation

```python
import optuna

# Optuna with Bayesian optimization (TPE)
def objective(trial):
    params = {
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("lr", 1e-3, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample", 0.6, 1.0),
        "reg_lambda": trial.suggest_float("lambda", 1e-3, 10, log=True),
    }
    model = XGBClassifier(**params, n_estimators=500, early_stopping_rounds=50)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    return model.best_score

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 随机 > 网格 | 任何调优 | 随机搜索可证明对大多数问题更高效 |
| 贝叶斯用于昂贵评估 | 深度学习、大数据集 | 每次评估成本高时，利用先前评估的信息 |
| 早停作为超参数 | 树Boosting | 通过早停确定 `n_estimators`，而非网格搜索 |
| 对数尺度搜索 | 学习率、正则化 | 对数均匀采样：$\text{lr} \sim 10^{U(-4, -1)}$ |

### Common Interview Questions

- [ ] 为什么随机搜索通常优于网格搜索？
- [ ] 解释贝叶斯优化和采集函数
- [ ] Hyperband如何实现效率提升？
- [ ] XGBoost你会先调哪些超参数？
- [ ] 如何在超参数调优过程中避免过拟合？

## Key Takeaways

- [ ] 随机搜索 > 网格搜索：重要维度的覆盖率更好
- [ ] 贝叶斯优化（Optuna/TPE）：昂贵评估时的最优选择
- [ ] Hyperband/ASHA：多保真度方法用于快速初筛
- [ ] 对学习率和正则化参数在对数尺度上搜索
- [ ] 使用嵌套CV防止对调优集的过拟合
"""

# ============================================================
# Node 88: Calibration
# ============================================================
TRANSLATIONS[88] = r"""# Model Calibration

## Overview

**Model Calibration（模型校准）** 确保模型输出的概率反映真实的事件发生可能性：如果模型预测80%的概率，该事件应该大约在80%的时间里发生。当概率值驱动下游决策（广告竞价、医学诊断、风险评分）时，校准至关重要。

许多高判别力的模型（如深度神经网络、Random Forest）输出的"概率"并非真正的概率——它们可能系统性地过度自信或不足自信。校准的目标就是修正这种偏差。

## Core Concepts

### What is Calibration?（什么是校准？）

模型 $\hat{p}$ 是校准的，当且仅当：

$$P(Y=1 | \hat{p}(X) = p) = p, \quad \forall p \in [0,1]$$

即对于所有模型预测概率为 $p$ 的样本群体，其中确实有比例为 $p$ 的正例。

**Reliability Diagram（可靠性图/校准图）**：将预测概率（x轴）与观测频率（y轴）对比。完美校准 = 对角线。

- 曲线在对角线上方：模型 **underconfident（不足自信）**，预测概率低于实际概率
- 曲线在对角线下方：模型 **overconfident（过度自信）**，预测概率高于实际概率

### Calibration Metrics（校准指标）

**ECE (Expected Calibration Error，期望校准误差)**：

$$ECE = \sum_{b=1}^{B} \frac{n_b}{N} |acc(b) - conf(b)|$$

将预测值分为 $B$ 个bin（通常 $B = 10$ 或 $B = 15$），比较每个bin内的平均置信度与实际准确率的偏差。$n_b$ 是第 $b$ 个bin中的样本数，$N$ 是总样本数。

ECE的直觉：它是校准误差在预测值分布上的加权平均。ECE = 0 意味着完美校准。

**Brier Score（布里尔分数）**——一个 **Proper Scoring Rule（正则评分规则）**：

$$BS = \frac{1}{n}\sum_{i=1}^{n}(\hat{p}_i - y_i)^2$$

Brier分数可分解为三个成分：
- **Reliability（可靠性）**：校准误差，越小越好
- **Resolution（分辨力）**：判别能力，越大越好
- **Uncertainty（不确定性）**：数据固有的不确定性，与模型无关

这一分解说明了校准和判别力是模型质量的两个不同维度——一个校准完美但无判别力的模型和一个完全未校准的模型都是无用的。

### Calibration Methods（校准方法）

**Platt Scaling（Platt缩放）**——参数化方法：

在模型输出上拟合一个逻辑回归：

$$\hat{p}_{\text{cal}} = \sigma(a \cdot f(x) + b)$$

在保留的校准集上学习参数 $a$ 和 $b$。其中 $\sigma$ 是sigmoid函数。适用于S形的校准误差（模型输出与真实概率之间是单调的sigmoid关系）。

**优点**：只有2个参数，不容易过拟合，少量校准数据即可
**缺点**：假设校准函数是sigmoid形状，灵活性有限

**Isotonic Regression（保序回归）**——非参数方法：

拟合一个单调不递减的阶梯函数，将模型分数映射到校准概率。比Platt Scaling更灵活，但需要更多校准数据。

**优点**：不假设特定函数形式，能处理任意非线性校准误差
**缺点**：容易过拟合（特别是数据少时），可能产生阶梯状的校准函数

**Temperature Scaling（温度缩放）**——专为神经网络设计：

单一参数 $T > 0$：

$$\hat{p}_{\text{cal}} = \text{softmax}(z/T)$$

其中 $z$ 是模型输出的logits。
- $T > 1$：软化预测（降低过度自信），概率分布更均匀
- $T < 1$：锐化预测，概率分布更集中
- $T = 1$：无变化（原始模型）

最优 $T$ 通过在验证集上最小化 **NLL (Negative Log-Likelihood，负对数似然)** 找到。

温度缩放的关键优势：**保持分类排序不变**（因为softmax的单调性），仅调整概率的"锐度"。

### Which Models Need Calibration?（哪些模型需要校准？）

| 模型 | 校准质量 | 建议处理 |
|------|---------|---------|
| **Logistic Regression（逻辑回归）** | 好（天然校准） | 通常不需要 |
| **Random Forest（随机森林）** | 差（概率集中在0和1附近） | Platt或保序回归 |
| **Gradient Boosted Trees（梯度提升树）** | 中等 | Platt Scaling |
| 神经网络 | 差（过度自信） | 温度缩放 |
| **SVM (Support Vector Machine，支持向量机)** | 不适用（非概率模型） | Platt Scaling |

**为什么随机森林校准差？** 随机森林的预测概率是所有树投票的平均值。由于bagging的特性，概率倾向于被推向0.5（在边界附近），而在远离边界的区域被推向0或1，导致整体校准差。

## Implementation

```python
from sklearn.calibration import (
    CalibratedClassifierCV, calibration_curve
)
import matplotlib.pyplot as plt

# Platt scaling (sigmoid)
calibrated = CalibratedClassifierCV(
    base_estimator=model, method="sigmoid", cv=5
)
calibrated.fit(X_train, y_train)

# Reliability diagram
prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
plt.plot(prob_pred, prob_true, marker="o")
plt.plot([0, 1], [0, 1], "--")
plt.xlabel("Mean predicted probability")
plt.ylabel("Fraction of positives")
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 广告竞价中的校准 | 广告系统 | 预测概率直接决定出价金额 |
| 温度缩放 | 深度学习 | 单参数，保持排序，实现简单 |
| 事后校准 vs. 训练时校准 | 系统设计 | 事后（Platt/保序）是标准方法；训练时（mixup, label smoothing）也有帮助 |
| 校准 vs. 判别力 | "用什么指标？" | AUC衡量判别力；ECE衡量校准。两者都需要 |

### Common Interview Questions

- [ ] 什么是模型校准良好的含义？
- [ ] 为什么随机森林的校准通常较差？
- [ ] 比较Platt Scaling与保序回归
- [ ] 什么时候校准比判别力更重要？
- [ ] 如何在生产广告系统中校准模型？

## Key Takeaways

- [ ] 校准 = 预测概率与观测频率一致
- [ ] ECE和可靠性图是主要的校准诊断工具
- [ ] Platt Scaling：参数化（2个参数），适合平滑的校准误差
- [ ] 保序回归：非参数化，更灵活，需要更多数据
- [ ] 温度缩放：神经网络的标准方法，单一参数 $T$
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA encoding = 'UTF-8'")
    cur = conn.cursor()

    for node_id in range(80, 89):
        # Get current description
        cur.execute("SELECT title, length(description) FROM framework_nodes WHERE id=?", (node_id,))
        title, old_len = cur.fetchone()

        new_desc = TRANSLATIONS[node_id].strip()
        new_len = len(new_desc)

        # Validate
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in new_desc)
        # Check no $$ inside code blocks
        in_code = False
        has_dollar_in_code = False
        for line in new_desc.split('\n'):
            if line.strip().startswith('```'):
                in_code = not in_code
            elif in_code and '$$' in line:
                has_dollar_in_code = True

        if new_len < 5500:
            print(f"WARNING Node {node_id} ({title}): length {new_len} < 5500")
        if not has_chinese:
            print(f"WARNING Node {node_id} ({title}): no Chinese characters found")
        if has_dollar_in_code:
            print(f"WARNING Node {node_id} ({title}): $$ found inside code block")

        # Update
        cur.execute("UPDATE framework_nodes SET description=? WHERE id=?", (new_desc, node_id))
        print(f"Node {node_id} ({title}): {old_len} -> {new_len} chars [OK]")

    conn.commit()
    conn.close()
    print("\nAll 9 nodes updated successfully.")


if __name__ == "__main__":
    main()
