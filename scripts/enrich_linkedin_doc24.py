"""Enrich LinkedIn doc#24 (ML Fundamentals + Coding) with acronym expansion,
follow-up Q&A, Python code for theory sections, and practical examples.

Task: T-P0-265
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_content(conn: sqlite3.Connection) -> str:
    """Read doc#24 content."""
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=24")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#24 not found")
        sys.exit(1)
    return row[0]


def enrich(content: str) -> str:
    """Apply all enrichments to doc#24."""

    # ================================================================
    # PART 1: Acronym expansions (first occurrence of each)
    # ================================================================

    # Title-level: ANN
    content = content.replace(
        "## 1. ANN Deep Dive",
        "## 1. ANN (Artificial Neural Network，人工神经网络) Deep Dive",
    )

    # BCE in section 1.2
    content = content.replace(
        "| 二分类 | Binary Cross-Entropy (BCE)",
        "| 二分类 | **BCE (Binary Cross-Entropy，二元交叉熵)**",
    )

    # MSE in section 1.2 - already has partial expansion
    content = content.replace(
        "| 回归 | **MSE (Mean Squared Error，均方误差)**",
        "| 回归 | **MSE (Mean Squared Error，均方误差)**",
    )

    # Adam acronym expansion in 1.3
    content = content.replace(
        "Adam = **Ada**ptive **M**oment Estimation",
        "**Adam (Adaptive Moment Estimation，自适应矩估计)**",
    )

    # SGD in section 3 TOC
    content = content.replace(
        "Batch GD vs SGD vs Mini-batch",
        "Batch GD vs **SGD (Stochastic Gradient Descent，随机梯度下降)** vs Mini-batch",
    )

    # GLM in section 2.3
    content = content.replace(
        "#### 2.3 与 Linear Regression 的关系 (GLM 角度)",
        "#### 2.3 与 Linear Regression 的关系 (GLM (Generalized Linear Model，广义线性模型) 角度)",
    )

    # NLL in section 2.2
    content = content.replace(
        "对整个数据集取负对数似然 (NLL)：",
        "对整个数据集取负对数似然 (**NLL, Negative Log-Likelihood，负对数似然**)：",
    )

    # BCE in section 2.2 title
    content = content.replace(
        "#### 2.2 BCE Loss 推导",
        "#### 2.2 BCE (Binary Cross-Entropy) Loss 推导",
    )

    # OLS in section 4.4
    content = content.replace(
        "无正则化的OLS (Ordinary Least Squares)",
        "无正则化的**OLS (Ordinary Least Squares，普通最小二乘法)**",
    )

    # MLE title expansion
    content = content.replace(
        "## 7. MLE 推导",
        "## 7. MLE (Maximum Likelihood Estimation，最大似然估计) 推导",
    )

    # GMM expansion
    content = content.replace(
        "**Gaussian Mixture Model**: $p(x)",
        "**GMM (Gaussian Mixture Model，高斯混合模型)**: $p(x)",
    )

    # EM expansion
    content = content.replace(
        "#### 7.3 EM Algorithm 原理",
        "#### 7.3 EM (Expectation-Maximization，期望最大化) Algorithm 原理",
    )

    # GBDT in section 6.3
    content = content.replace(
        "#### 6.3 Random Forest vs Boosting (GBDT/XGBoost)",
        "#### 6.3 Random Forest vs Boosting (**GBDT (Gradient Boosted Decision Trees，梯度提升决策树)**/XGBoost)",
    )

    # SSE in section 8.1 - already partially expanded inline
    content = content.replace(
        "4. ****SSE (Sum of Squared Errors，误差平方和)**",
        "4. **SSE (Sum of Squared Errors，误差平方和)**",
    )

    # BFS in section 12.1
    content = content.replace(
        "本质: **图的遍历** (BFS/DFS)",
        "本质: **图的遍历** (**BFS (Breadth-First Search，广度优先搜索)**/DFS (Depth-First Search，深度优先搜索))",
    )

    # CSR in section 9.2
    content = content.replace(
        '"""稀疏矩阵：CSR-like 格式存储。',
        '"""稀疏矩阵：CSR (Compressed Sparse Row，压缩稀疏行) 格式存储。',
    )

    # SMOTE in appendix
    content = content.replace(
        "oversampling (SMOTE), undersampling",
        "oversampling (**SMOTE (Synthetic Minority Over-sampling Technique，合成少数类过采样技术)**), undersampling",
    )

    # MAE in section 1.2
    content = content.replace(
        "MSE when small, MAE when large",
        "MSE when small, **MAE (Mean Absolute Error，平均绝对误差)** when large",
    )

    # BPR in section 1.2
    content = content.replace(
        "Pairwise Hinge / BPR Loss",
        "Pairwise Hinge / **BPR (Bayesian Personalized Ranking，贝叶斯个性化排序)** Loss",
    )

    # CE in appendix follow-up row - already partially in text
    content = content.replace(
        "Softmax + Categorical **CE (Cross-Entropy，交叉熵)** (Multinomial Logistic Regression)",
        "Softmax + Categorical **CE (Cross-Entropy，交叉熵)** = Multinomial Logistic Regression",
    )

    # LARS/LAMB in section 3.3
    content = content.replace(
        "→ LARS/LAMB optimizer",
        "→ **LARS (Layer-wise Adaptive Rate Scaling)**/LAMB (Layer-wise Adaptive Moments for Batch training) optimizer",
    )

    # RMSProp in section 1.3
    content = content.replace(
        "结合了 Momentum 和 RMSProp：",
        "结合了 Momentum (动量) 和 **RMSProp (Root Mean Square Propagation，均方根传播)**：",
    )

    # i.i.d. in section 7.1
    content = content.replace(
        "给定 i.i.d. 样本",
        "给定 **i.i.d. (independent and identically distributed，独立同分布)** 样本",
    )

    # ================================================================
    # PART 2: Add detailed follow-up Q&A to each section
    # ================================================================

    # Section 1: ANN follow-ups
    content = content.replace(
        "- 常见follow-up: Adam vs AdamW (weight decay vs L2 regularization 的区别)\n\n---\n\n## 2. Logistic Regression 深入",
        """- 常见follow-up: Adam vs AdamW (weight decay vs L2 regularization 的区别)

### Follow-up 问题详解

**Q: AdamW 和 Adam 有什么区别？为什么 AdamW 更好？**

Adam 中的 L2 regularization 是加在梯度上的：$g_t = \\nabla L + \\lambda w$，这意味着 weight decay 的效果会被 adaptive learning rate 缩放。AdamW 将 weight decay 解耦，直接在参数更新时减去：$w_{t+1} = w_t - \\eta(\\frac{\\hat{m}_t}{\\sqrt{\\hat{v}_t}+\\epsilon} + \\lambda w_t)$。这保证了 weight decay 的强度不受梯度历史影响，正则化效果更一致。现代深度学习几乎都用 AdamW。

**Q: Dying ReLU 问题怎么解决？**

Dying ReLU 指某些神经元的输入始终为负，梯度永远为0，神经元"死亡"。解决方案：
- **Leaky ReLU**: $f(x) = \\max(0.01x, x)$，负值区域有小斜率
- **PReLU (Parametric ReLU)**: 斜率可学习，$f(x) = \\max(\\alpha x, x)$
- **ELU**: $f(x) = x$ if $x>0$, $\\alpha(e^x-1)$ if $x\\leq0$
- 使用合适的权重初始化 (He initialization)
- 降低学习率

```python
import numpy as np

def relu(x: np.ndarray) -> np.ndarray:
    \"\"\"Standard ReLU.\"\"\"
    return np.maximum(0, x)

def leaky_relu(x: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    \"\"\"Leaky ReLU: prevents dying neurons.\"\"\"
    return np.where(x > 0, x, alpha * x)

def silu(x: np.ndarray) -> np.ndarray:
    \"\"\"SiLU/Swish: smooth, non-monotonic.\"\"\"
    return x / (1 + np.exp(-x))

# Comparison
x = np.linspace(-3, 3, 7)
print(f"x:          {x}")
print(f"ReLU:       {relu(x)}")
print(f"LeakyReLU:  {leaky_relu(x)}")
print(f"SiLU:       {np.round(silu(x), 3)}")
```

**Q: 怎么选 learning rate scheduler？**

常见策略：
- **Step decay**: 每 N 个 epoch 乘以 0.1 (简单有效)
- **Cosine annealing**: 学习率按余弦曲线衰减到最小值，常用于 vision
- **Warmup + decay**: 前几个 epoch 线性增大 LR，之后衰减。大 batch 训练必备
- **ReduceLROnPlateau**: 当 val loss 不再下降时自动降低 LR
- **One Cycle**: 先升后降，训练速度快 (Leslie Smith 提出)

---

## 2. Logistic Regression 深入""",
    )

    # Section 2: Logistic Regression follow-ups
    # NOTE: The CE acronym replacement above changed "(Multinomial" to "= Multinomial"
    content = content.replace(
        "- Follow-up: 多分类怎么办？→ Softmax + Categorical **CE (Cross-Entropy，交叉熵)** = Multinomial Logistic Regression\n\n---\n\n## 3. Gradient Descent",
        """- Follow-up: 多分类怎么办？→ Softmax + Categorical **CE (Cross-Entropy，交叉熵)** (Multinomial Logistic Regression)

### Follow-up 问题详解

**Q: Logistic Regression 的决策边界是什么形状？**

线性的。$w^Tx + b = 0$ 定义了一个超平面，将特征空间分为两半。这就是为什么 Logistic Regression 是线性分类器 — 它只能处理线性可分的数据。对于非线性可分的数据，可以：
- 添加多项式特征 (polynomial features)
- 使用 kernel trick (类似 SVM)
- 换用更复杂的模型 (Neural Network, Tree-based)

**Q: Logistic Regression 怎么处理多分类？**

```python
import numpy as np

def softmax(z: np.ndarray) -> np.ndarray:
    \"\"\"Softmax: 多分类输出层，将logits转为概率分布。

    数值稳定版本：减去最大值防止 exp overflow。
    \"\"\"
    z_shifted = z - np.max(z, axis=-1, keepdims=True)
    exp_z = np.exp(z_shifted)
    return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

def categorical_cross_entropy(
    y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-15
) -> float:
    \"\"\"多分类交叉熵损失。

    Args:
        y_true: one-hot 编码的真实标签 (N, C)
        y_pred: softmax 输出的概率 (N, C)
    \"\"\"
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(np.sum(y_true * np.log(y_pred), axis=-1))

# 示例: 3分类
logits = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, 0.3]])
probs = softmax(logits)
print(f"Softmax probs: {np.round(probs, 3)}")
# 每行和为1
print(f"Row sums: {np.round(probs.sum(axis=1), 3)}")
```

**Q: Logistic Regression 和 SVM (Support Vector Machine，支持向量机) 有什么区别？**

| | Logistic Regression | SVM |
|---|---|---|
| 输出 | 概率 $p \\in (0,1)$ | 分类标签 (距离超平面的margin) |
| 损失函数 | Log loss (BCE) | Hinge loss: $\\max(0, 1-y\\cdot f(x))$ |
| 对 outlier | 敏感 (所有点都影响决策边界) | 鲁棒 (只有 support vectors 影响) |
| 适用场景 | 需要概率输出时 | 高维稀疏数据 (text) |

---

## 3. Gradient Descent""",
    )

    # Section 3: Gradient Descent follow-ups
    content = content.replace(
        "- Follow-up: 有没有方法让大batch也能泛化好？→ LARS/LAMB optimizer, learning rate warmup\n\n---\n\n## 4. Overfitting / Underfitting",
        """- Follow-up: 有没有方法让大batch也能泛化好？→ **LARS (Layer-wise Adaptive Rate Scaling)**/LAMB (Layer-wise Adaptive Moments for Batch training) optimizer, learning rate warmup

### Follow-up 问题详解

**Q: 梯度消失和梯度爆炸是什么？怎么解决？**

- **梯度消失 (Vanishing Gradient)**: 深层网络中，梯度经过多层反向传播后变得极小 (接近0)，导致浅层参数几乎不更新。常见于 sigmoid/tanh 激活 (导数最大0.25)。
- **梯度爆炸 (Exploding Gradient)**: 梯度值不断累乘导致极大，参数更新跳跃，训练不稳定。常见于 RNN。

解决方案：
- 梯度消失: ReLU 激活, Residual connections (skip connections), Batch Normalization, LSTM/GRU (RNN场景)
- 梯度爆炸: Gradient clipping ($\\|g\\| > \\text{threshold}$ 时缩放), 合适的权重初始化 (Xavier/He), 降低学习率

```python
import numpy as np

def gradient_clip(gradients: list[np.ndarray], max_norm: float = 1.0) -> list[np.ndarray]:
    \"\"\"Gradient clipping by global norm.

    如果梯度的全局范数超过 max_norm，等比例缩放所有梯度。
    \"\"\"
    total_norm = np.sqrt(sum(np.sum(g ** 2) for g in gradients))
    clip_coef = max_norm / (total_norm + 1e-6)
    if clip_coef < 1.0:
        gradients = [g * clip_coef for g in gradients]
    return gradients

# 示例
grads = [np.array([3.0, 4.0]), np.array([5.0, 12.0])]
print(f"Before clip - norms: {[np.linalg.norm(g) for g in grads]}")
clipped = gradient_clip(grads, max_norm=5.0)
print(f"After clip  - norms: {[np.round(np.linalg.norm(g), 3) for g in clipped]}")
```

**Q: Learning rate 太大或太小会怎样？**

- **太大**: 更新步幅过大，loss 震荡甚至发散 (diverge)
- **太小**: 收敛极慢，可能卡在局部极小值或鞍点 (saddle point)
- **最佳实践**: 使用 learning rate finder (Leslie Smith 方法) — 从极小 LR 开始逐步增大，找到 loss 下降最快的区间

---

## 4. Overfitting / Underfitting""",
    )

    # Section 4: Overfitting follow-ups
    content = content.replace(
        "- Follow-up: Dropout 和 L2 的关系？→ Dropout 近似等价于 L2 正则化 (Wager et al.)\n\n---\n\n## 5. Decision Tree",
        """- Follow-up: Dropout 和 L2 的关系？→ Dropout 近似等价于 L2 正则化 (Wager et al.)

### Follow-up 问题详解

**Q: Dropout 的工作原理是什么？推理时有什么不同？**

训练时：每个神经元以概率 $p$ (通常0.5) 被随机"关闭"(输出设为0)。这迫使网络学习冗余表示，不依赖任何单个神经元。

推理时 (Inference)：**不 dropout**，所有神经元都参与。但因为训练时只有 $(1-p)$ 的神经元活跃，权重的期望输出会变大。两种处理方式：
- **Standard dropout**: 推理时将权重乘以 $(1-p)$
- **Inverted dropout** (常用): 训练时将输出除以 $(1-p)$，推理时不需要额外操作

```python
import numpy as np

def dropout_forward(x: np.ndarray, p: float = 0.5, training: bool = True) -> np.ndarray:
    \"\"\"Inverted dropout implementation.

    Args:
        x: input activations
        p: dropout probability (概率丢弃)
        training: True for training, False for inference
    \"\"\"
    if not training or p == 0:
        return x
    # 生成 mask: 1/(1-p) 缩放保持期望不变
    mask = (np.random.rand(*x.shape) > p).astype(float) / (1 - p)
    return x * mask

# 示例
np.random.seed(42)
x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
print(f"Original:      {x}")
print(f"Training (p=0.5): {dropout_forward(x, p=0.5, training=True)}")
print(f"Inference:     {dropout_forward(x, p=0.5, training=False)}")
```

**Q: Bias-Variance Tradeoff 怎么用来指导模型选择？**

| 现象 | 诊断 | 解决方案 |
|------|------|---------|
| Train high, Val high | High bias (underfitting) | 增加模型复杂度、添加特征、减少正则化 |
| Train low, Val high | High variance (overfitting) | 增加数据、加强正则化、减少特征、Ensemble |
| Train low, Val low | Good fit | 部署 |

**Ensemble 方法降低 variance 的原理**: 如果有 $T$ 个独立模型各有 variance $\\sigma^2$，平均后 variance 变成 $\\sigma^2/T$。实际中模型不完全独立，但 Bagging (Random Forest) 通过 bootstrap + feature subsampling 尽量降低相关性。

---

## 5. Decision Tree""",
    )

    # Section 5: Decision Tree follow-ups
    content = content.replace(
        "- Follow-up: 为什么 Random Forest 不容易 overfit？→ Bagging + feature subsampling 降低 variance\n\n---\n\n## 6. Random Forest 详解",
        """- Follow-up: 为什么 Random Forest 不容易 overfit？→ Bagging + feature subsampling 降低 variance

### Follow-up 问题详解

**Q: Gini Impurity 和 Information Gain (Entropy) 有什么区别？用哪个？**

两者都衡量节点的"纯度"，用于选择最佳分裂特征：

- **Gini Impurity**: $G = 1 - \\sum_{c=1}^C p_c^2$。范围 $[0, 0.5]$ (二分类)。计算快。
- **Entropy (信息熵)**: $H = -\\sum_{c=1}^C p_c \\log_2 p_c$。范围 $[0, 1]$ (二分类)。涉及 log 运算，稍慢。
- **Information Gain (IG)** = 分裂前 Entropy - 分裂后加权 Entropy

实际差别很小。sklearn 默认用 Gini (更快)。当类别多且分布不均时，Entropy 可能略好。

```python
import numpy as np

def gini_impurity(labels: np.ndarray) -> float:
    \"\"\"Calculate Gini impurity for a node.\"\"\"
    _, counts = np.unique(labels, return_counts=True)
    probs = counts / counts.sum()
    return 1 - np.sum(probs ** 2)

def entropy(labels: np.ndarray) -> float:
    \"\"\"Calculate entropy for a node.\"\"\"
    _, counts = np.unique(labels, return_counts=True)
    probs = counts / counts.sum()
    return -np.sum(probs * np.log2(probs + 1e-10))

# 示例
pure = np.array([1, 1, 1, 1])
mixed = np.array([1, 1, 0, 0])
skewed = np.array([1, 1, 1, 0])
for name, arr in [("Pure", pure), ("Mixed 50/50", mixed), ("Skewed 75/25", skewed)]:
    print(f"{name:15s}: Gini={gini_impurity(arr):.3f}, Entropy={entropy(arr):.3f}")
```

**Q: Feature importance 是怎么算的？**

两种主要方法：
- **Impurity-based (MDI, Mean Decrease in Impurity)**: 每次分裂时，计算该特征带来的 impurity 减少量，所有树上累加。sklearn `.feature_importances_` 默认方法。缺点：对高基数特征有偏。
- **Permutation importance**: 随机打乱某个特征的值，观察模型性能下降多少。更可靠但更慢。

---

## 6. Random Forest 详解""",
    )

    # Section 6: Random Forest follow-ups
    content = content.replace(
        "- Follow-up: **OOB (Out-of-Bag，袋外样本)** error 是什么？→ 每棵树有约 36.8% 的样本没被选中，可用作验证集\n\n---\n\n## 7. MLE 推导",
        """- Follow-up: **OOB (Out-of-Bag，袋外样本)** error 是什么？→ 每棵树有约 36.8% 的样本没被选中，可用作验证集

### Follow-up 问题详解

**Q: OOB error 为什么约 36.8% 的样本没被选中？**

Bootstrap 有放回采样 $N$ 次，某个样本在一次抽样中不被选中的概率是 $(1 - 1/N)$。$N$ 次都不被选中的概率是：

$(1 - 1/N)^N \\to e^{-1} \\approx 0.368$

所以约 36.8% 的样本没被用于训练该树，可以当作验证集。OOB error 是一种免费的交叉验证，不需要额外划分数据。

**Q: XGBoost 和 Random Forest 怎么选？**

| 场景 | 推荐 | 原因 |
|------|------|------|
| 数据量小 (<10K) | Random Forest | 不容易 overfit, 少调参 |
| 表格数据竞赛 | XGBoost/LightGBM | Boosting 效果更好 |
| 需要 feature importance | Random Forest | MDI 简单直观 |
| 需要概率校准 | XGBoost | 自带 calibration |
| 训练时间紧 | Random Forest | 可完全并行 |
| 特征有缺失值 | XGBoost | 原生支持缺失值处理 |

**Q: Bagging vs Boosting 的核心区别？**

```
Bagging (Bootstrap AGGregatING):
  Data ──> [Bootstrap Sample 1] ──> Tree 1 ──┐
  Data ──> [Bootstrap Sample 2] ──> Tree 2 ──┼──> 平均/投票 ──> 最终预测
  Data ──> [Bootstrap Sample 3] ──> Tree 3 ──┘
  (并行训练, 减少 variance)

Boosting:
  Data ──> Tree 1 ──> Residual 1 ──> Tree 2 ──> Residual 2 ──> Tree 3 ──> ...
  (串行训练, 减少 bias, 每棵树修正前一棵的错误)
```

---

## 7. MLE (Maximum Likelihood Estimation，最大似然估计) 推导""",
    )

    # Section 7: MLE follow-ups
    content = content.replace(
        "- Follow-up: EM 和 K-means 的关系？→ K-means 是 EM 的特例 (hard assignment, 等方差)\n\n---\n\n## 8. K-means 实现与停止条件",
        """- Follow-up: EM 和 K-means 的关系？→ K-means 是 EM 的特例 (hard assignment, 等方差)

### Follow-up 问题详解

**Q: MLE 和 MAP (Maximum A Posteriori，最大后验估计) 有什么区别？**

| | MLE | MAP |
|---|---|---|
| 目标 | $\\arg\\max_\\theta P(D|\\theta)$ | $\\arg\\max_\\theta P(\\theta|D) = P(D|\\theta)P(\\theta)$ |
| 先验 | 无 (或说均匀先验) | 有先验 $P(\\theta)$ |
| 正则化关系 | 无正则化 | L2正则化 = 高斯先验的MAP |
| 过拟合 | 更容易 | 先验起正则化作用 |

**关键洞察**: L2 正则化等价于对参数施加 Gaussian 先验 $P(w) \\sim N(0, \\sigma^2)$ 的 MAP 估计。L1 正则化等价于 Laplace 先验。

```python
import numpy as np

def mle_normal(data: np.ndarray) -> tuple[float, float]:
    \"\"\"Normal distribution MLE: mu = mean, sigma^2 = (1/n) * sum((x-mu)^2).

    注意：MLE 的方差估计是有偏的 (除以 n 而非 n-1)。
    \"\"\"
    mu_hat = np.mean(data)
    sigma2_hat = np.mean((data - mu_hat) ** 2)  # 有偏
    return mu_hat, sigma2_hat

def unbiased_variance(data: np.ndarray) -> float:
    \"\"\"无偏方差估计 (Bessel's correction): 除以 n-1。\"\"\"
    return np.var(data, ddof=1)

# 示例
np.random.seed(42)
data = np.random.normal(loc=5.0, scale=2.0, size=20)
mu, sigma2 = mle_normal(data)
print(f"True: mu=5.0, sigma^2=4.0")
print(f"MLE:  mu={mu:.3f}, sigma^2={sigma2:.3f} (biased)")
print(f"Unbiased variance: {unbiased_variance(data):.3f}")
```

**Q: EM Algorithm 一定收敛吗？收敛到全局最优吗？**

- EM 保证 log-likelihood **单调不递减**，所以一定收敛
- 但只保证收敛到 **局部最优**，不保证全局最优
- 解决方案：多次随机初始化，取 log-likelihood 最大的结果
- K-means++ 初始化可以显著改善 GMM-EM 的起点质量

---

## 8. K-means 实现与停止条件""",
    )

    # Section 8: K-means follow-ups
    content = content.replace(
        "- Follow-up: K-means 和 EM/GMM 的关系？→ K-means 是 GMM + EM 的特例 (hard assignment, 各component等方差)\n\n---\n\n## 9. Sparse Vector / Matrix Multiplication",
        """- Follow-up: K-means 和 EM/GMM 的关系？→ K-means 是 GMM + EM 的特例 (hard assignment, 各component等方差)

### Follow-up 问题详解

**Q: K-means 的时间复杂度和空间复杂度？**

- 时间: $O(n \\cdot k \\cdot d \\cdot T)$，$n$=样本数, $k$=聚类数, $d$=维度, $T$=迭代次数
- 空间: $O(n \\cdot d + k \\cdot d)$ (存储数据 + centroids)
- sklearn 的 MiniBatchKMeans 可以处理大数据集: 每次只用一个 mini-batch 更新 centroids

**Q: K-means 对初始化敏感吗？K-means++ 是怎么工作的？**

非常敏感。随机初始化可能导致：
- 多个 centroid 落在同一个 cluster → 该 cluster 被过度分割
- 某些 cluster 没有 centroid → 完全被忽略
- 收敛到差的局部最优

K-means++ 解决方案：选择彼此尽量远的初始 centroids
1. 随机选第一个 centroid
2. 对每个点计算到最近已选 centroid 的距离 $D(x)$
3. 以 $D(x)^2$ 为概率选下一个 centroid (越远越可能被选中)
4. 重复直到选够 $k$ 个

**Q: K-means 有什么替代方案？**

| 方法 | 优势 | 适用场景 |
|------|------|---------|
| DBSCAN | 不需要预设 K, 能发现任意形状 cluster | 噪声数据, 非凸 cluster |
| GMM | 软分配 (概率), 椭圆形 cluster | 需要概率输出 |
| Hierarchical | 不需要预设 K, 产生层次结构 | 需要 dendrogram 分析 |
| Spectral | 能发现非凸 cluster | 图结构数据 |

---

## 9. Sparse Vector / Matrix Multiplication""",
    )

    # Section 9: Sparse follow-ups
    content = content.replace(
        "- Follow-up: 分布式场景怎么做？→ 按行分块到不同机器\n\n---\n\n## 10. Stratified Sampling 实现",
        """- Follow-up: 分布式场景怎么做？→ 按行分块到不同机器

### Follow-up 问题详解

**Q: 如果一个 vector 特别稀疏，另一个很密集，怎么优化 dot product？**

用 binary search: 遍历稀疏的 vector 的非零元素，在密集 vector 中用二分查找匹配的 index。时间复杂度 $O(nnz_{sparse} \\cdot \\log(nnz_{dense}))$，当 $nnz_{sparse} \\ll nnz_{dense}$ 时远优于双指针的 $O(nnz_{sparse} + nnz_{dense})$。

```python
import bisect
from typing import List, Tuple

def sparse_dot_binary_search(
    sparse: List[Tuple[int, float]],
    dense: List[Tuple[int, float]],
) -> float:
    \"\"\"当一个向量远比另一个稀疏时，用二分查找优化。

    Time: O(nnz_sparse * log(nnz_dense))
    \"\"\"
    dense_indices = [idx for idx, _ in dense]
    dense_values = {idx: val for idx, val in dense}
    result = 0.0
    for idx, val in sparse:
        pos = bisect.bisect_left(dense_indices, idx)
        if pos < len(dense_indices) and dense_indices[pos] == idx:
            result += val * dense_values[idx]
    return result
```

**Q: Sparse Matrix 有哪些常见存储格式？**

| 格式 | 全称 | 适用场景 |
|------|------|---------|
| **COO (Coordinate)** | 三元组 (row, col, val) | 构建矩阵 |
| **CSR (Compressed Sparse Row)** | 行压缩 | 行切片, 矩阵乘法 |
| **CSC (Compressed Sparse Column)** | 列压缩 | 列切片 |
| **DOK (Dictionary of Keys)** | 字典存储 | 增量构建 |

scipy.sparse 提供了所有这些格式。面试中一般用 COO 或 dict-of-lists 即可。

---

## 10. Stratified Sampling 实现""",
    )

    # Section 10: Stratified Sampling follow-ups
    content = content.replace(
        "- Follow-up: 怎么保证采样的reproducibility？→ random seed\n\n---\n\n## 11. LRU Cache + 多线程 Follow-up",
        """- Follow-up: 怎么保证采样的reproducibility？→ random seed

### Follow-up 问题详解

**Q: Stratified Sampling 和 Random Sampling 的区别？什么时候必须用分层采样？**

Random sampling 从全体数据中随机抽取，如果类别不平衡 (如正样本1%，负样本99%)，小样本中可能完全没有正样本。Stratified sampling 保证每个类别按比例 (或等量) 被采样。

**必须使用的场景**：
- 类别极度不平衡 (欺诈检测、稀有疾病诊断)
- 训练/验证/测试集划分 (确保每个集合都包含所有类)
- A/B test 中按用户特征分层确保组间可比

sklearn 中直接支持：`train_test_split(X, y, stratify=y)`

**Q: 有放回采样 vs 无放回采样？**

| | 有放回 (with replacement) | 无放回 (without replacement) |
|---|---|---|
| Python | `random.choices()` | `random.sample()` |
| 特点 | 同一样本可被选多次 | 每个样本最多选一次 |
| 用途 | Bootstrap, Bagging | 通常的数据划分 |
| 样本量限制 | 无限制 | 不能超过总体大小 |

---

## 11. LRU Cache + 多线程 Follow-up""",
    )

    # Section 11: LRU follow-ups
    content = content.replace(
        "- 面试中 Coding with AI 轮要注意：让 AI 生成代码后你要能 review 并发现 bug\n\n---\n\n## 12. Service Dependency",
        """- 面试中 Coding with AI 轮要注意：让 AI 生成代码后你要能 review 并发现 bug

### Follow-up 问题详解

**Q: LFU (Least Frequently Used) Cache 和 LRU 有什么区别？**

| | LRU | **LFU (Least Frequently Used，最不经常使用)** |
|---|---|---|
| 淘汰策略 | 最久未使用 | 使用次数最少 |
| 数据结构 | HashMap + DoublyLinkedList | HashMap + 频率桶 (min-heap 或链表) |
| 适用场景 | 时间局部性强 | 频率分布稳定 |
| 缺点 | 忽略频率信息 | 新元素容易被淘汰 (cold start) |

**Q: Python 的 `functools.lru_cache` 和手写 LRU 有什么不同？**

`@lru_cache` 是装饰器，只能缓存函数调用结果 (memoization)。底层用 dict + doubly-linked list，但只支持 hashable 参数。手写 LRU 更灵活：可以自定义过期策略、支持多线程、与外部存储集成。

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    \"\"\"用 lru_cache 做记忆化递归。\"\"\"
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(f"fib(50) = {fibonacci(50)}")
print(f"Cache info: {fibonacci.cache_info()}")
# CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)
```

**Q: 分布式 LRU Cache 怎么设计？**

核心挑战：多台机器上维护一致的 LRU 顺序。

方案：
1. **Consistent Hashing (一致性哈希)** 将 key 分配到不同机器，每台机器独立维护 LRU
2. **Redis** 直接用 Redis 的内存淘汰策略 (`maxmemory-policy allkeys-lru`)
3. **两级缓存**: L1 本地 LRU (进程内) + L2 分布式缓存 (Redis/Memcached)

---

## 12. Service Dependency""",
    )

    # Section 12: Service Dependency follow-ups
    content = content.replace(
        "- 面试官注意的不是你写的有多快，而是你能否有效地和 AI 协作、发现 AI 的错误\n\n---\n\n## 附录",
        """- 面试官注意的不是你写的有多快，而是你能否有效地和 AI 协作、发现 AI 的错误

### Follow-up 问题详解

**Q: 如果依赖图有环 (circular dependency) 怎么办？**

代码中已用 `affected` set (visited set) 防止无限循环。只有未访问的节点才加入队列。这是标准的 BFS 防环处理。

如果面试官要求检测环本身 (Cycle Detection)：
- **DFS + 三色标记** (白/灰/黑): 遇到灰色节点 = 环
- **Topological Sort (拓扑排序)**: 如果排序后节点数 < 总节点数，则有环
- **Kahn's Algorithm**: BFS-based 拓扑排序

```python
from collections import defaultdict, deque
from typing import Dict, List

def detect_cycle(dependencies: Dict[str, List[str]]) -> bool:
    \"\"\"用 Kahn's algorithm (BFS拓扑排序) 检测依赖图中的环。

    如果无法完成拓扑排序 (排序后节点数 < 总节点数), 则存在环。
    \"\"\"
    # 构建正向图和入度表
    in_degree: Dict[str, int] = defaultdict(int)
    graph: Dict[str, List[str]] = defaultdict(list)
    all_nodes = set()

    for service, deps in dependencies.items():
        all_nodes.add(service)
        for dep in deps:
            all_nodes.add(dep)
            graph[dep].append(service)
            in_degree[service] += 1

    # BFS: 从入度为0的节点开始
    queue = deque([n for n in all_nodes if in_degree[n] == 0])
    sorted_count = 0

    while queue:
        node = queue.popleft()
        sorted_count += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    has_cycle = sorted_count < len(all_nodes)
    return has_cycle

# 测试
deps_no_cycle = {"A": ["B"], "B": ["C"], "C": []}
deps_with_cycle = {"A": ["B"], "B": ["C"], "C": ["A"]}
print(f"No cycle: {detect_cycle(deps_no_cycle)}")     # False
print(f"Has cycle: {detect_cycle(deps_with_cycle)}")   # True
```

**Q: 如何找出 critical service (单点故障)?**

**Critical service**: 如果它挂了，受影响的服务数量最多。找法：对每个 service 模拟挂掉，计算受影响数量，取最大值。

```python
def find_critical_services(
    dependencies: Dict[str, List[str]], top_n: int = 3
) -> List[tuple]:
    \"\"\"找出影响范围最大的 critical services.\"\"\"
    from collections import deque

    def count_affected(deps: Dict[str, List[str]], failed: str) -> int:
        reverse = defaultdict(list)
        for svc, dep_list in deps.items():
            for d in dep_list:
                reverse[d].append(svc)
        visited = set()
        queue = deque([failed])
        while queue:
            curr = queue.popleft()
            for dep in reverse.get(curr, []):
                if dep not in visited:
                    visited.add(dep)
                    queue.append(dep)
        return len(visited)

    results = []
    for service in dependencies:
        affected = count_affected(dependencies, service)
        results.append((service, affected))
    results.sort(key=lambda x: -x[1])
    return results[:top_n]
```

---

## 附录""",
    )

    # ================================================================
    # PART 3: Enhance the appendix follow-up table
    # ================================================================
    content = content.replace(
        "| Service Dep | 环怎么办? | visited set 防止无限循环 (代码已包含) |",
        """| Service Dep | 环怎么办? | visited set 防止无限循环 (代码已包含) |
| ANN | Batch Norm 原理? | 标准化每层输入: $\\hat{x} = (x-\\mu)/\\sigma$, 然后 $\\gamma\\hat{x}+\\beta$ |
| MLE | MLE vs MAP? | MAP = MLE + 先验, L2正则 = Gaussian先验MAP |
| K-means | DBSCAN 原理? | 基于密度, 不需预设K, 能处理噪声和非凸cluster |
| Overfitting | Early Stopping 怎么实现? | 监控val loss, patience=N epochs不改善则停止 |
| Decision Tree | XGBoost 的核心创新? | 二阶Taylor展开 + 正则化目标 + 稀疏感知 |""",
    )

    return content


def save_content(conn: sqlite3.Connection, content: str) -> None:
    """Write enriched content back to doc#24."""
    cur = conn.cursor()
    cur.execute(
        "UPDATE company_documents SET content=? WHERE id=24",
        (content,),
    )
    conn.commit()


def main() -> None:
    """Run enrichment pipeline."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        original = get_content(conn)
        print(f"Original length: {len(original)}c")

        enriched = enrich(original)
        print(f"Enriched length: {len(enriched)}c")
        print(f"Added: {len(enriched) - len(original)}c")

        save_content(conn, enriched)
        print("Saved to database.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
