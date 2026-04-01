# Uber BPS -- KNN 从零实现 + ML 基础复习

> **目的**：招聘方明确提到 **KNN (K-Nearest Neighbors，K近邻)** 和 ML 基础是 BPS 评估内容。
> 本文档涵盖 KNN 从零实现以及在约5分钟 ML 基础环节中可能考察的核心 ML 概念。
>
> Task: T-P1-246

---

## Table of Contents

1. [KNN From Scratch (Python)](#1-knn-from-scratch-python)
2. [Distance Metrics](#2-distance-metrics)
3. [Choosing k](#3-choosing-k)
4. [Weighted KNN](#4-weighted-knn)
5. [Classification vs Regression](#5-classification-vs-regression)
6. [Optimization: KD-Tree, Ball Tree, LSH](#6-optimization-kd-tree-ball-tree-lsh)
7. [KNN Interview Questions](#7-knn-interview-questions)
8. [ML Fundamentals: Bias-Variance Tradeoff](#8-ml-fundamentals-bias-variance-tradeoff)
9. [ML Fundamentals: Overfitting and Regularization](#9-ml-fundamentals-overfitting-and-regularization)
10. [ML Fundamentals: Cross-Validation](#10-ml-fundamentals-cross-validation)
11. [ML Fundamentals: Evaluation Metrics](#11-ml-fundamentals-evaluation-metrics)
12. [ML Fundamentals: Feature Engineering](#12-ml-fundamentals-feature-engineering)
13. [Quick-Fire Q&A Cheat Sheet](#13-quick-fire-qa-cheat-sheet)

---

## 1. KNN From Scratch (Python)

### 1.1 Core Implementation（核心实现）

```python
import numpy as np
from collections import Counter
from typing import Optional


class KNN:
    """K-Nearest Neighbors classifier/regressor from scratch."""

    def __init__(
        self,
        k: int = 5,
        metric: str = "euclidean",
        task: str = "classification",
        weighted: bool = False,
    ):
        self.k = k
        self.metric = metric
        self.task = task  # "classification" or "regression"
        self.weighted = weighted
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "KNN":
        """Store training data. KNN is a lazy learner -- no model is built."""
        self.X_train = np.array(X, dtype=float)
        self.y_train = np.array(y)
        return self

    def _compute_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Compute distance between two points."""
        if self.metric == "euclidean":
            return np.sqrt(np.sum((x1 - x2) ** 2))
        elif self.metric == "manhattan":
            return np.sum(np.abs(x1 - x2))
        elif self.metric == "cosine":
            dot = np.dot(x1, x2)
            norm = np.linalg.norm(x1) * np.linalg.norm(x2)
            if norm == 0:
                return 1.0
            return 1.0 - dot / norm
        elif self.metric == "minkowski":
            p = 3  # generalized; euclidean=2, manhattan=1
            return np.sum(np.abs(x1 - x2) ** p) ** (1.0 / p)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")

    def _get_neighbors(self, x: np.ndarray) -> tuple:
        """Return indices and distances of k nearest neighbors."""
        distances = np.array([
            self._compute_distance(x, x_train) for x_train in self.X_train
        ])
        k_indices = np.argsort(distances)[: self.k]
        k_distances = distances[k_indices]
        return k_indices, k_distances

    def _predict_single(self, x: np.ndarray):
        """Predict for a single sample."""
        k_indices, k_distances = self._get_neighbors(x)
        k_labels = self.y_train[k_indices]

        if self.task == "classification":
            if self.weighted:
                # Inverse distance weighting
                weights = 1.0 / (k_distances + 1e-8)
                vote_counts: dict = {}
                for label, w in zip(k_labels, weights):
                    vote_counts[label] = vote_counts.get(label, 0) + w
                return max(vote_counts, key=vote_counts.get)
            else:
                # Majority vote
                counter = Counter(k_labels)
                return counter.most_common(1)[0][0]
        else:  # regression
            if self.weighted:
                weights = 1.0 / (k_distances + 1e-8)
                return np.average(k_labels.astype(float), weights=weights)
            else:
                return np.mean(k_labels.astype(float))

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict for multiple samples."""
        X = np.array(X, dtype=float)
        return np.array([self._predict_single(x) for x in X])

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Accuracy (classification) or R^2 (regression)."""
        predictions = self.predict(X)
        if self.task == "classification":
            return np.mean(predictions == y)
        else:
            y = np.array(y, dtype=float)
            ss_res = np.sum((y - predictions) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
```

### 1.2 Usage Example（使用示例）

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = KNN(k=5, metric="euclidean", task="classification", weighted=True)
model.fit(X_train, y_train)
print(f"Accuracy: {model.score(X_test, y_test):.3f}")
```

### 1.3 Key Properties of KNN（KNN 关键特性）

| 属性 | 值 |
|------|---|
| 类型 | 基于实例的 / 惰性学习器 |
| 训练成本 | O(1) -- 仅存储数据 |
| 预测成本 | O(n*d) 每次查询（暴力法） |
| 内存 | O(n*d) -- 存储所有训练数据 |
| 参数化？ | 否 -- 决策边界由数据决定 |
| 能处理非线性？ | 是 -- 自然捕获复杂边界 |

---

## 2. Distance Metrics（距离度量）

### 2.1 Common Metrics（常用度量）

| 度量 | 公式 | 使用场景 |
|------|------|----------|
| **Euclidean (L2，欧几里得距离)** | sqrt(sum((x_i - y_i)^2)) | 连续特征默认选择，且尺度一致 |
| **Manhattan (L1，曼哈顿距离)** | sum(\|x_i - y_i\|) | 高维数据、稀疏特征、对异常值鲁棒 |
| **Cosine（余弦距离）** | 1 - (x . y) / (\|\|x\|\| * \|\|y\|\|) | 文本/NLP（TF-IDF 向量），量级无关时 |
| **Minkowski (Lp，闵可夫斯基距离)** | (sum(\|x_i - y_i\|^p))^(1/p) | 通用形式；p=1 为 Manhattan，p=2 为 Euclidean |
| **Hamming（汉明距离）** | 不同坐标的比例 | 类别型/二值特征 |

### 2.2 Feature Scaling is Critical（特征缩放至关重要）

KNN 基于距离，因此尺度较大的特征会主导计算。**必须归一化。**

```python
# StandardScaler: zero mean, unit variance
X_scaled = (X - X.mean(axis=0)) / X.std(axis=0)

# MinMaxScaler: [0, 1] range
X_scaled = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
```

**面试回答**："KNN 计算距离，因此不同尺度的特征会使距离计算产生偏差。一个范围在0-1000的特征会压倒一个范围在0-1的特征。我会在拟合 KNN 之前应用 StandardScaler 或 MinMaxScaler。"

---

## 3. Choosing k（选择 k 值）

### 3.1 Effect of k（k 值的影响）

| 小 k (如 1-3) | 大 k (如 50+) |
|---------------|--------------|
| 低偏差、高方差 | 高偏差、低方差 |
| 对噪声/异常值敏感 | 更平滑的决策边界 |
| 风险：过拟合 | 风险：欠拟合 |
| 捕获局部模式 | 对全局趋势取平均 |

### 3.2 How to Select k（如何选择 k）

1. **交叉验证**：尝试 k = 1, 3, 5, 7, ..., sqrt(n)。选择 **CV (Cross-Validation，交叉验证)** 分数最好的 k。
2. **经验法则**：k = sqrt(n) 是常用起点。
3. **二分类用奇数 k**：避免多数投票时出现平局。
4. **拐点法**：画出准确率 vs k 的图，选择提升趋于平缓的"拐点"。

```python
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

best_k, best_score = 1, 0
for k in range(1, 30, 2):
    scores = cross_val_score(
        KNeighborsClassifier(n_neighbors=k), X_train, y_train, cv=5
    )
    if scores.mean() > best_score:
        best_k, best_score = k, scores.mean()
```

---

## 4. Weighted KNN（加权 KNN）

### 4.1 Why Weight?（为什么加权？）

标准 KNN 给所有 k 个邻居同等投票权。但距离为0.1的邻居应该比距离为10的邻居权重更大。

### 4.2 Weighting Schemes（加权方案）

| 方案 | 权重公式 | 优点 |
|------|----------|------|
| **Uniform（均匀）** | w_i = 1 | 简单，数据密集时有效 |
| **Inverse distance（逆距离）** | w_i = 1 / d_i | 较近邻居主导 |
| **Gaussian kernel（高斯核）** | w_i = exp(-d_i^2 / (2 * sigma^2)) | 平滑衰减，带宽可调 |

### 4.3 When Weighted KNN Helps（加权 KNN 何时有用）

- **类别分布倾斜**：少数类邻居在距离近时获得公平权重
- **边界重叠**：减少过渡区域的误分类
- **噪声数据**：距离远的噪声点贡献更小

---

## 5. Classification vs Regression（分类 vs 回归）

### 5.1 KNN for Classification（KNN 分类）

- **输出**：k 个邻居中最常见的标签（多数投票）
- **平局处理**：按距离打破（最近邻获胜）或随机
- **概率**：P(class=c) = count(class=c in neighbors) / k

### 5.2 KNN for Regression（KNN 回归）

- **输出**：k 个邻居值的均值（或加权均值）
- **变体**：邻居的中位数（对异常值鲁棒）

### 5.3 Comparison Table（对比表）

| 方面 | 分类 | 回归 |
|------|------|------|
| 输出 | 离散标签 | 连续值 |
| 聚合方式 | 多数投票 | 均值 / 加权均值 |
| 评估指标 | Accuracy, F1 | MSE, R^2 |
| 加权优势 | 减少平局歧义 | 平滑预测 |

---

## 6. Optimization: KD-Tree, Ball Tree, LSH（优化方法）

### 6.1 Why Optimize?（为什么需要优化？）

暴力 KNN 每次查询 O(n*d)。当 n=100万、d=100 时太慢。

### 6.2 KD-Tree

```
构建：沿方差最大的维度递归分割数据。
      每个节点存储分割维度 + 分割值。
查询：遍历树，剪枝那些边界框比当前第 k 近距离更远的分支。
```

| 属性 | 值 |
|------|---|
| 构建时间 | O(n log n) |
| 查询时间 | O(log n) 平均，O(n) 最坏 |
| 最适合 | 低维度 (d < 20) |
| 失效场景 | 高维：所有维度距离近似相等，无法有效剪枝 |

### 6.3 Ball Tree

```
构建：将数据递归划分为超球体（球）。
      每个节点存储圆心 + 半径。
查询：剪枝那些最近点比第 k 近距离更远的球。
```

| 属性 | 值 |
|------|---|
| 构建时间 | O(n log n) |
| 查询时间 | O(log n) 平均 |
| 最适合 | 中等维度 (d < 100)，非欧几里得度量 |
| 相比 KD-Tree 优势 | 支持任意度量，在较高维度表现更好 |

### 6.4 LSH (Locality-Sensitive Hashing，局部敏感哈希)

```
思路：将相似点以高概率哈希到同一桶。
      多个哈希表 + 哈希函数减少假阴性。
      查询：哈希查询点，仅在其桶内搜索。
```

| 属性 | 值 |
|------|---|
| 构建时间 | O(n * L)，L = 哈希表数量 |
| 查询时间 | O(L) 摊销 -- 亚线性 |
| 最适合 | 极高维度 (d > 100)，近似最近邻 |
| 权衡 | 近似的 -- 可能遗漏真正的最近邻 |
| Uber 使用？ | 是 -- 司机-乘客匹配使用空间哈希 |

### 6.5 Comparison（对比）

| 方法 | 精确？ | 最佳维度范围 | 查询复杂度 |
|------|--------|-------------|-----------|
| 暴力法 | 是 | 任意 | O(n*d) |
| KD-Tree | 是 | d < 20 | O(log n) 平均 |
| Ball Tree | 是 | d < 100 | O(log n) 平均 |
| LSH | 近似 | d > 100 | 亚线性 |
| **FAISS (Facebook AI Similarity Search)** | 近似 | 任意 | 亚线性 (GPU) |

---

## 7. KNN Interview Questions（KNN 面试题）

### Q1: 什么是维度灾难？它如何影响 KNN？

**回答**：在高维空间中，所有点变得近似等距。比率 (max_distance - min_distance) / min_distance 随维度增长趋近于0。这意味着 KNN 无法区分有意义的邻居和随机点。

**对 KNN 的影响**：
- 基于距离的邻居选择变得无意义
- 所有 k 个邻居距离大致相同
- 决策边界变得不可靠
- KD-Tree 剪枝失败（无法有效分区）

**缓解方法**：
- KNN 之前进行降维（**PCA (Principal Component Analysis，主成分分析)**、t-SNE、自编码器）
- 特征选择，只保留有信息量的维度
- 使用 Manhattan 距离（在高维比 Euclidean 更鲁棒）
- 转向近似方法（LSH、FAISS）

### Q2: KNN 如何处理类别型特征？

**回答**：
1. **One-hot encoding（独热编码）**：将类别转为二值向量，使用 Euclidean/Hamming 距离
2. **Ordinal encoding（序数编码）**：如果类别有自然顺序（如 low/medium/high）
3. **Hamming distance**：计算类别维度上的不匹配数
4. **Gower distance**：混合度量，结合 Euclidean（连续）+ Hamming（类别）
5. **Embedding（嵌入）**：学习稠密表示（如神经网络的实体嵌入）

### Q3: KNN vs Logistic Regression -- 何时用哪个？

| 方面 | KNN | **Logistic Regression（逻辑回归）** |
|------|-----|------------------------------------|
| 决策边界 | 非线性、局部 | 线性（或用多项式特征） |
| 可解释性 | 低（无系数） | 高（系数 = 特征重要性） |
| 训练速度 | O(1) | O(n*d) -- 迭代 |
| 预测速度 | O(n*d) | O(d) -- 快 |
| 特征缩放 | 必须 | 有帮助但非必须 |
| 高维 | 差（维度灾难） | 处理良好 |
| 小数据集 | 好 | 可能欠拟合 |

### Q4: KNN 如何处理类别不平衡？

**问题**：如果95%的邻居是 A 类，KNN 几乎总是预测 A。

**解决方案**：
1. **加权 KNN**：逆距离加权使更近的少数类样本影响更大
2. **调整 k**：如果少数类样本聚集紧密，较小的 k 有帮助
3. **SMOTE (Synthetic Minority Over-sampling Technique，合成少数类过采样)**：在现有少数类邻居之间插值生成新样本
4. **类别加权投票**：将每个投票乘以类别频率的倒数
5. **基于半径**：使用半径 r 内的所有邻居而非固定 k

### Q5: 距离相同/平局怎么办？

**回答**：当多个点共享第 k 近距离时：
1. **全部包含**（k 变为可变）-- sklearn 暴力法的默认行为
2. **随机打破平局** -- 任意但一致
3. **使用加权 KNN** -- 距离可以解决大多数平局
4. **奇数 k** -- 有助于二分类投票平局

### Q6: KNN 能用于异常检测吗？

**回答**：可以。计算每个点到 k 个最近邻的平均距离。平均邻居距离高的点是异常点。

```python
def knn_anomaly_scores(X, k=5):
    """Higher score = more anomalous."""
    scores = []
    for i, x in enumerate(X):
        distances = sorted([
            np.linalg.norm(x - X[j]) for j in range(len(X)) if j != i
        ])[:k]
        scores.append(np.mean(distances))
    return np.array(scores)
```

---

## 8. ML Fundamentals: Bias-Variance Tradeoff（偏差-方差权衡）

### 8.1 Definitions（定义）

| 术语 | 定义 | 直觉 |
|------|------|------|
| **Bias（偏差）** | 过度简化假设导致的误差 | 模型太简单，遗漏模式 |
| **Variance（方差）** | 对训练数据波动的敏感性导致的误差 | 模型记住了噪声 |
| **Irreducible error（不可约误差）** | 数据本身的噪声 | 任何模型都无法消除 |

**总误差 = Bias^2 + Variance + 不可约误差**

### 8.2 Tradeoff Visualization（权衡可视化）

```
Error
  ^
  |  \                    /
  |   \   Total Error   /
  |    \     ____      /
  |     \   /    \    /
  |      \_/      \  /
  |   Bias^2   Variance
  |
  +-------------------------> Model Complexity
     Simple                Complex
```

### 8.3 Examples（示例）

| 模型 | 偏差 | 方差 | 示例 |
|------|------|------|------|
| 线性回归（少特征） | 高 | 低 | 对非线性数据欠拟合 |
| 深度神经网络 | 低 | 高 | 在小数据集上过拟合 |
| KNN k=1 | 低 | 高 | 记住训练数据 |
| KNN k=n | 高 | 低 | 预测全局多数类 |
| **Random Forest（随机森林）** | 低 | 中 | Bagging 降低方差 |

### 8.4 Interview Answer Template（面试回答模板）

"偏差-方差权衡意味着我们不能同时最小化两者。简单模型（高偏差）一致地遗漏模式，但在不同训练集上给出稳定的预测。复杂模型（高方差）捕获模式，但预测随不同训练数据大幅波动。最佳点是总误差最小的模型复杂度。我们通过交叉验证来找到它。"

---

## 9. ML Fundamentals: Overfitting and Regularization（过拟合与正则化）

### 9.1 Signs of Overfitting（过拟合的迹象）

- 训练准确率 >> 验证准确率（差距大）
- 模型在已见数据上表现好，在未见数据上表现差
- 学习曲线：训练损失持续下降，验证损失上升

### 9.2 Regularization Techniques（正则化技术）

| 技术 | 工作原理 | 应用场景 |
|------|----------|----------|
| **L1 (Lasso)** | 将 sum(\|w_i\|) 加到损失；驱动权重为0 | 特征选择 |
| **L2 (Ridge)** | 将 sum(w_i^2) 加到损失；收缩权重 | 防止权重过大 |
| **Elastic Net** | L1 + L2 结合 | 两者优点兼得 |
| **Dropout** | 训练时随机置零神经元 | 神经网络 |
| **Early stopping（早停）** | 验证损失上升时停止训练 | 任何迭代模型 |
| **Data augmentation（数据增强）** | 增加有效训练集大小 | 图像/NLP 模型 |
| **Ensemble methods（集成方法）** | Bagging 降低方差（Random Forest） | 通用 |

### 9.3 L1 vs L2 Interview Answer（L1 vs L2 面试回答）

"L1 将权重的绝对值加到损失中，产生稀疏解——某些权重变为恰好为零，适用于特征选择。L2 将权重的平方加到损失中，将所有权重收缩向零但很少恰好为零——当所有特征都可能相关时更好。L1 给出菱形约束区域（角接触坐标轴），L2 给出圆形区域。L1 的角就是系数为零的地方。"

---

## 10. ML Fundamentals: Cross-Validation（交叉验证）

### 10.1 Types（类型）

| 方法 | 描述 | 使用场景 |
|------|------|----------|
| **k-Fold CV** | 将数据分成 k 份，k-1份训练、1份验证，轮换 | 默认选择 (k=5 或 10) |
| **Stratified k-Fold** | k-Fold 但保持每份中的类别比例 | 不平衡分类 |
| **Leave-One-Out (LOO)** | k-Fold 其中 k=n | 极小数据集 |
| **Time-series split** | 用过去训练、用未来验证（不打乱） | 时序数据——绝不泄露未来信息 |
| **Holdout** | 单次 train/val/test 分割 | 大数据集（CV 成本太高时） |

### 10.2 Common Mistakes（常见错误）

1. **数据泄露**：分割前在整个数据集上拟合 scaler。修正：仅在训练集上拟合 scaler，再变换验证集。
2. **用测试集调参**：测试集只能使用一次。修正：用验证集或嵌套 CV 调参。
3. **打乱时序数据**：破坏时间结构。修正：使用 TimeSeriesSplit。

### 10.3 Interview Answer（面试回答）

"我默认使用分层5折交叉验证。它在保持类别平衡的同时给出可靠的泛化性能估计。对于时序数据，我切换到 TimeSeriesSplit 以避免泄露未来信息。我始终在 CV 循环内拟合预处理步骤（缩放、编码）以防止数据泄露。"

---

## 11. ML Fundamentals: Evaluation Metrics（评估指标）

### 11.1 Classification Metrics（分类指标）

| 指标 | 公式 | 使用场景 |
|------|------|----------|
| **Accuracy（准确率）** | (TP+TN) / (TP+TN+FP+FN) | 类别平衡时 |
| **Precision（精确率）** | TP / (TP+FP) | 假阳性代价高（垃圾邮件过滤） |
| **Recall（召回率）** | TP / (TP+FN) | 假阴性代价高（疾病筛查） |
| **F1** | 2 * P * R / (P + R) | 平衡 precision 和 recall |
| **AUC-ROC (Area Under ROC Curve，ROC曲线下面积)** | ROC 曲线下面积 | 基于排序、阈值无关 |
| **Log loss** | -mean(y*log(p) + (1-y)*log(1-p)) | 概率预测 |

### 11.2 Regression Metrics（回归指标）

| 指标 | 公式 | 解读 |
|------|------|------|
| **MSE (Mean Squared Error，均方误差)** | mean((y - y_hat)^2) | 对大误差惩罚重 |
| **RMSE (Root MSE，均方根误差)** | sqrt(MSE) | 与目标同单位 |
| **MAE (Mean Absolute Error，平均绝对误差)** | mean(\|y - y_hat\|) | 对异常值鲁棒 |
| **R^2（决定系数）** | 1 - SS_res / SS_tot | 解释的方差比例（1=完美） |
| **MAPE** | mean(\|y - y_hat\| / \|y\|) * 100 | 百分比误差，易解释 |

### 11.3 Confusion Matrix Quick Reference（混淆矩阵速查）

```
                  Predicted
                  Pos    Neg
Actual  Pos  [   TP  |  FN  ]   <- Recall = TP / (TP + FN)
        Neg  [   FP  |  TN  ]
                  ^
                  Precision = TP / (TP + FP)
```

### 11.4 AUC-ROC Interview Answer（AUC-ROC 面试回答）

"AUC-ROC 衡量模型将正样本排在负样本之上的能力，与阈值无关。AUC 为0.5意味着随机猜测；1.0意味着完美分离。当我关心排序质量而非特定阈值时使用它。对于不平衡数据集，我倾向使用 **AUC-PR (Precision-Recall Curve，精确率-召回率曲线)**，因为当负样本远多于正样本时 ROC 可能过于乐观。"

---

## 12. ML Fundamentals: Feature Engineering（特征工程）

### 12.1 Common Techniques（常用技术）

| 技术 | 示例 | 使用场景 |
|------|------|----------|
| **Scaling（缩放）** | StandardScaler, MinMaxScaler | 基于距离的模型（KNN, **SVM (Support Vector Machine，支持向量机)**） |
| **Log transform（对数变换）** | log(income) | 右偏分布 |
| **Binning（分箱）** | Age -> age_group | 在线性模型中捕获非线性关系 |
| **Interaction features（交互特征）** | x1 * x2 | 已知特征交互 |
| **Polynomial features（多项式特征）** | x, x^2, x^3 | 线性模型中的非线性模式 |
| **Target encoding（目标编码）** | Category -> mean(target) per category | 高基数类别型 |
| **Embedding（嵌入）** | Word2Vec, 实体嵌入 | 文本、有语义的类别型 |

### 12.2 Feature Selection Methods（特征选择方法）

| 方法 | 类型 | 工作方式 |
|------|------|----------|
| **Correlation filter（相关性过滤）** | Filter | 移除与目标低相关的特征 |
| **Variance threshold（方差阈值）** | Filter | 移除近常量特征 |
| **L1 regularization（L1 正则化）** | Embedded | Lasso 驱动无关权重为零 |
| **Mutual information（互信息）** | Filter | 信息论相关性度量 |
| **RFE (Recursive Feature Elimination，递归特征消除)** | Wrapper | 迭代移除最不重要的特征 |
| **Tree-based importance（基于树的重要性）** | Embedded | Random Forest / **XGBoost (eXtreme Gradient Boosting)** 特征重要性 |

---

## 13. Quick-Fire Q&A Cheat Sheet（快速问答速查表）

这些是一亩三分地 Uber BPS 面经中报告的快速 ML 问题。练习在30-60秒内给出每个回答。

### Bias-Variance（偏差-方差）

**Q: 什么是偏差-方差权衡？**
A: 总误差 = bias^2 + variance + 噪声。简单模型高偏差（欠拟合），复杂模型高方差（过拟合）。我们通过交叉验证调节复杂度（正则化、KNN 的 k 值、树深度）来最小化总误差。

### Overfitting（过拟合）

**Q: 如何判断模型是否过拟合？如何解决？**
A: 训练准确率远高于验证准确率。解决：更多数据、正则化（L1/L2）、dropout、更简单模型、早停、用交叉验证调参。

### KNN Basics（KNN 基础）

**Q: 解释 KNN。优缺点是什么？**
A: 惰性学习器，通过 k 个最近邻的多数投票进行分类。优点：简单、无需训练、天然非线性。缺点：预测慢 O(n*d)、维度灾难、需要特征缩放、存储所有数据。

**Q: KNN 如何选择 k？**
A: 在一系列 k 值上交叉验证。k=1 过拟合，k=n 欠拟合。常用起点：k=sqrt(n)。二分类用奇数 k 避免平局。

### Metrics（指标）

**Q: 什么时候用 precision vs recall？**
A: 假阳性代价高时用 Precision（垃圾邮件过滤——不要拦截正常邮件）。假阴性代价高时用 Recall（癌症筛查——不要漏诊）。F1 平衡两者。

**Q: 解释 AUC-ROC。**
A: 在所有阈值下绘制真阳性率 vs 假阳性率的曲线下面积。0.5 = 随机，1.0 = 完美。衡量排序质量，与阈值无关。不平衡数据用 AUC-PR 更好。

### Regularization（正则化）

**Q: 什么是正则化？L1 vs L2？**
A: 对模型权重的惩罚以防过拟合。L1 (Lasso) 加 |w|，产生稀疏模型（特征选择）。L2 (Ridge) 加 w^2，收缩所有权重（无稀疏性）。Elastic Net 结合两者。

### Cross-Validation

**Q: 为什么用交叉验证而非单次 train/test 分割？**
A: 单次分割方差高——性能取决于哪些数据落在测试集中。k-Fold CV 在 k 个不同分割上取平均，给出更可靠的估计。也允许不碰测试集就调参。

### Trees and Ensembles（树和集成）

**Q: Random Forest vs Gradient Boosting？**
A: Random Forest：bagging（并行树，降低方差）。**Gradient Boosting（梯度提升）**：boosting（序列树，每棵纠正前一棵的错误，降低偏差）。RF 对超参数更鲁棒；GB 通常达到更高准确率但更容易过拟合。

### Dimensionality Reduction（降维）

**Q: 什么是 PCA？何时使用？**
A: **PCA (Principal Component Analysis，主成分分析)** 找到最大方差的正交方向，将数据投影到前 k 个分量上。用于 KNN/SVM 前降维、可视化（2D/3D）、或消除多重共线性。局限：仅线性——非线性结构用 t-SNE 或自编码器。

### Uber-Specific ML（Uber 特定 ML 问题）

**Q: 如何在 Uber 使用 KNN？**
A: (1) 司机-乘客匹配：使用空间索引（2D GPS 的 KD-Tree）找到乘客位置附近 k 个最近的可用司机。(2) **ETA (Estimated Time of Arrival，预计到达时间)** 估算：找到 k 个最相似的历史行程（特征：距离、时段、路况）并取其实际时长的平均值。(3) 欺诈检测：异常交易与 k 个最近合法交易的平均距离很高。

---

## Summary: What to Review the Night Before（面试前夜复习清单）

1. **KNN**：实现、距离度量、k 值选择、加权 KNN、维度灾难
2. **偏差-方差**：定义、权衡曲线、按模型类型举例
3. **过拟合**：迹象、正则化（L1/L2/dropout/早停）
4. **交叉验证**：k-Fold、分层、时序分割、数据泄露陷阱
5. **指标**：Precision/Recall/F1、AUC-ROC vs AUC-PR、MSE/MAE/R^2
6. **练习**：大声在30-60秒内回答每个快速问答
