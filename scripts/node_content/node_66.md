# Support Vector Machines（支持向量机）

## Overview

**SVM（Support Vector Machines，支持向量机）** 通过寻找最大间隔超平面来分离不同类别的数据。虽然在工业界使用频率不如树模型集成方法，但SVM在面试中极其重要：它考察对优化问题、核方法和偏差-方差权衡的深入理解。SVM在小数据场景、文本分类和高维稀疏数据上表现出色。

SVM的核心思想是 **Structural Risk Minimization（结构风险最小化）**，不仅最小化训练误差，还通过最大化间隔来控制模型复杂度，从而在泛化性能上具有理论保证。与 **ERM（Empirical Risk Minimization，经验风险最小化）** 不同，SRM在经验风险基础上加入了描述模型复杂度的正则项，这正是SVM理论上优于感知机的根本原因。

## Core Concepts

### Hard-Margin SVM（硬间隔SVM）

对于线性可分数据，寻找超平面 $w^Tx + b = 0$ 使得间隔 $\frac{2}{\|w\|}$ 最大化。**Primal Problem（原始问题）**：

$$\min_{w,b} \frac{1}{2}\|w\|^2 \quad \text{s.t.} \quad y_i(w^Tx_i + b) \geq 1 \;\forall i$$

几何解释：**Functional Margin（函数间隔）** 定义为 $\hat{\gamma}_i = y_i(w^Tx_i + b)$，而 **Geometric Margin（几何间隔）** 则是 $\gamma_i = \frac{y_i(w^Tx_i + b)}{\|w\|}$。最大化几何间隔 $\frac{2}{\|w\|}$ 等价于最小化 $\|w\|^2$（在函数间隔归一化为1的条件下）。

### Soft-Margin SVM（软间隔SVM）

现实数据通常不完全线性可分，引入 **Slack Variables（松弛变量）** $\xi_i \geq 0$ 允许部分样本违反间隔约束：

$$\min_{w,b,\xi} \frac{1}{2}\|w\|^2 + C\sum_{i=1}^{n} \xi_i \quad \text{s.t.} \quad y_i(w^Tx_i + b) \geq 1 - \xi_i, \; \xi_i \geq 0$$

参数 $C$（**Regularization Parameter，正则化参数**）的作用：
- $C$ 很大：对误分类惩罚重，间隔小，模型复杂度高（低偏差、高方差）
- $C$ 很小：允许更多误分类，间隔大，模型更简单（高偏差、低方差）
- $\xi_i = 0$：样本在间隔之外（正确分类且距离足够）
- $0 < \xi_i < 1$：样本在间隔之内但正确分类
- $\xi_i = 1$：样本恰好在决策边界上
- $\xi_i > 1$：样本被误分类

还有一种替代形式使用 **$\ell_2$ Soft Margin（$\ell_2$软间隔）**：将 $C\sum \xi_i$ 替换为 $C\sum \xi_i^2$，对偶问题中不再有 $\alpha_i \leq C$ 的上界约束，但对异常值更敏感。

### Dual Formulation（对偶问题推导）

通过 **Lagrange Multipliers（拉格朗日乘子）** $\alpha_i$ 将原始问题转化为对偶问题。推导过程如下：

**Step 1**：构造拉格朗日函数：

$$L(w,b,\xi,\alpha,\mu) = \frac{1}{2}\|w\|^2 + C\sum\xi_i - \sum\alpha_i[y_i(w^Tx_i+b)-1+\xi_i] - \sum\mu_i\xi_i$$

**Step 2**：对原始变量求偏导并令其为零：

$$\frac{\partial L}{\partial w} = 0 \Rightarrow w = \sum\alpha_i y_i x_i$$

上式说明 $w$ 是支持向量的线性组合，这是SVM稀疏性的来源。

$$\frac{\partial L}{\partial b} = 0 \Rightarrow \sum\alpha_i y_i = 0$$

$$\frac{\partial L}{\partial \xi_i} = 0 \Rightarrow \alpha_i + \mu_i = C \Rightarrow 0 \leq \alpha_i \leq C$$

**Step 3**：代入拉格朗日函数得到对偶问题：

$$\max_\alpha \sum_{i=1}^{n} \alpha_i - \frac{1}{2}\sum_{i,j} \alpha_i \alpha_j y_i y_j K(x_i, x_j)$$

$$\text{s.t.} \quad 0 \leq \alpha_i \leq C, \quad \sum_{i=1}^{n} \alpha_i y_i = 0$$

对偶形式的优势：
1. 约束更简单（**Box Constraints，箱式约束**）
2. 目标函数只涉及样本之间的内积 $x_i^T x_j$，可用核函数替代
3. 解的稀疏性：只有 **Support Vectors（支持向量）** 的 $\alpha_i > 0$
4. 当特征维度远大于样本数时，对偶问题的规模更小

**Strong Duality（强对偶性）**：由于原始问题是凸二次规划且满足 **Slater's Condition（Slater条件）**，强对偶性成立，即原始问题和对偶问题的最优值相等。

**KKT Conditions（KKT条件，Karush-Kuhn-Tucker条件）**：

$$\alpha_i [y_i(w^Tx_i + b) - 1 + \xi_i] = 0$$

$$\mu_i \xi_i = (C - \alpha_i)\xi_i = 0$$

KKT条件的完整分析：
- $\alpha_i = 0$：样本不是支持向量，$y_i(w^Tx_i + b) \geq 1$，不影响决策边界
- $0 < \alpha_i < C$：样本恰好在间隔边界上，$\xi_i = 0$，$y_i(w^Tx_i + b) = 1$
- $\alpha_i = C$：样本在间隔内部或被误分类，$\xi_i > 0$

### Kernel Trick（核技巧）

**Kernel Trick（核技巧）** 允许在高维（甚至无限维）特征空间中计算内积，而不需要显式计算映射 $\phi(x)$：

$$K(x, z) = \phi(x)^T \phi(z)$$

核心思想是：我们不需要知道 $\phi$ 的具体形式，只需要能高效计算内积。对偶形式中的目标函数只涉及 $x_i^Tx_j$，将其替换为 $K(x_i, x_j)$ 即可在高维空间中操作。

**Mercer's Theorem（Mercer定理）**：一个对称函数 $K(x,z)$ 是有效核函数的充要条件是对任意有限样本集，对应的 **Gram Matrix（格拉姆矩阵）** $K_{ij} = K(x_i, x_j)$ 是半正定的。

**常用核函数详表**：

| 核函数 | 公式 | 参数 | 适用场景 | 特征空间维度 |
|--------|------|------|---------|-------------|
| **Linear（线性核）** | $K(x,z) = x^Tz$ | 无 | 高维稀疏数据（文本分类） | 与输入空间相同 |
| **Polynomial（多项式核）** | $K(x,z) = (\gamma x^Tz + r)^d$ | $d$, $\gamma$, $r$ | 特征交互、图像处理 | $\binom{n+d}{d}$ |
| **RBF/Gaussian（高斯核）** | $K(x,z) = \exp(-\gamma\|x-z\|^2)$ | $\gamma = \frac{1}{2\sigma^2}$ | 通用非线性问题 | 无限维 |
| **Sigmoid（Sigmoid核）** | $K(x,z) = \tanh(\gamma x^Tz + r)$ | $\gamma$, $r$ | 类似神经网络 | 不总满足Mercer条件 |
| **Laplacian（拉普拉斯核）** | $K(x,z) = \exp(-\gamma\|x-z\|_1)$ | $\gamma$ | 对噪声更鲁棒 | 无限维 |

**RBF核的深入理解**：
- $\gamma$ 控制每个支持向量的影响范围。$\gamma$ 大时影响范围小，决策边界复杂（高方差）；$\gamma$ 小时影响范围大，决策边界平滑（高偏差）
- RBF核将数据映射到无限维空间——泰勒展开：$\exp(-\gamma\|x-z\|^2) = \exp(-\gamma\|x\|^2)\exp(-\gamma\|z\|^2)\sum_{k=0}^{\infty}\frac{(2\gamma)^k}{k!}(x^Tz)^k$
- **自定义核函数**：只要满足Mercer条件，可以设计领域特定核函数。例如 **String Kernel（字符串核）** 用于文本，**Graph Kernel（图核）** 用于分子结构

### SMO Algorithm（序列最小最优化算法）

**SMO（Sequential Minimal Optimization，序列最小最优化）** 是求解SVM对偶问题最常用的算法（John Platt，1998年）。核心是将大规模 **QP（Quadratic Programming，二次规划）** 问题分解为最小子问题：

**算法流程**：
1. 初始化所有 $\alpha_i = 0$
2. 选择两个变量 $\alpha_i, \alpha_j$（因等式约束 $\sum \alpha_k y_k = 0$，至少需同时更新两个）
3. 固定其他变量，对 $\alpha_i, \alpha_j$ 求解——简单的一维二次规划，有解析解
4. 更新并裁剪到可行域 $[0, C]$
5. 更新阈值 $b$ 和误差缓存
6. 重复直到所有样本满足KKT条件

**解析更新公式**：$\alpha_j^{new} = \alpha_j^{old} + \frac{y_j(E_i - E_j)}{\eta}$，其中 $\eta = K_{ii} + K_{jj} - 2K_{ij}$，$E_i = f(x_i) - y_i$ 是预测误差。然后裁剪到 $[L, H]$，由等式约束得 $\alpha_i^{new}$。

**变量选择启发式**：外层循环遍历违反KKT条件的样本（优先非边界样本 $0 < \alpha_i < C$）；内层循环选择使 $|E_i - E_j|$ 最大的 $\alpha_j$。

时间复杂度：$O(n^2)$ 到 $O(n^3)$；空间复杂度：$O(n^2)$（核矩阵，可缓存优化）。

### SVM vs Logistic Regression（SVM与逻辑回归对比）

| 方面 | SVM | Logistic Regression |
|------|-----|-------------------|
| 损失函数 | **Hinge Loss（合页损失）**：$\max(0, 1-yf(x))$ | **Log Loss（对数损失）**：$\log(1+e^{-yf(x)})$ |
| 概率输出 | 需 **Platt Scaling（Platt缩放）** | 原生概率输出 |
| 决策边界 | 由支持向量决定 | 由所有样本决定 |
| 核方法 | 天然支持 | 需手动构造特征 |
| 稀疏性 | 解稀疏（仅支持向量） | 解不稀疏（L1正则化除外） |
| 大规模数据 | 不适合（$O(n^2)$ 到 $O(n^3)$） | 适合（$O(nd)$） |
| 异常值 | Hinge loss对远离边界的正确点不敏感 | Log loss对所有点都敏感 |
| 梯度特性 | Hinge loss在 $yf(x)>1$ 处梯度为0 | Log loss梯度始终非零 |

### Multi-class SVM（多类SVM）

SVM原生只支持二分类，多分类扩展：
- **One-vs-Rest (OvR)**：训练 $K$ 个分类器，选得分最高的类别
- **One-vs-One (OvO)**：训练 $\binom{K}{2}$ 个分类器，投票决定
- **DAG SVM（有向无环图SVM）**：基于OvO但用DAG结构，预测只需 $K-1$ 次比较
- **Crammer-Singer方法**：直接求解多类优化问题，计算开销更大

### SVR（Support Vector Regression，支持向量回归）

使用 **$\epsilon$-insensitive loss（$\epsilon$不敏感损失）**：

$$L_\epsilon(y, f(x)) = \max(0, |y - f(x)| - \epsilon)$$

在 $\epsilon$-tube 内的预测误差不被惩罚，管道外的误差线性惩罚。对偶问题引入两组乘子 $\alpha_i, \alpha_i^*$，预测函数 $f(x) = \sum(\alpha_i - \alpha_i^*)K(x_i, x) + b$。**$\nu$-SVR** 用参数 $\nu \in (0,1]$ 自动控制支持向量比例和 $\epsilon$ 管道宽度。

## Implementation

```python
from sklearn.svm import SVC, SVR, LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

# Classification with RBF kernel
pipe = Pipeline([
    ("scaler", StandardScaler()),  # SVM对特征尺度敏感，必须标准化
    ("svm", SVC(kernel="rbf", C=1.0, gamma="scale", probability=True))
])
pipe.fit(X_train, y_train)

# Support vectors analysis
svm_model = pipe.named_steps["svm"]
print(f"Support vectors: {len(svm_model.support_vectors_)} / {len(X_train)}")

# Hyperparameter tuning (log scale grid search)
param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100],
              "svm__gamma": [0.0001, 0.001, 0.01, 0.1, 1]}
gs = GridSearchCV(pipe, param_grid, cv=5, scoring="accuracy")

# Large-scale linear SVM (LIBLINEAR, much faster)
linear_pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", LinearSVC(C=1.0, loss="hinge", max_iter=10000))
])
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| 核函数选择 | 非线性边界 | RBF是默认；高维稀疏用线性核；先试线性再试RBF |
| $C$/$\gamma$ 调参 | 过拟合/欠拟合 | 对数刻度网格搜索 |
| SVM vs LR | 分类器选择 | SVM关注间隔；LR建模概率；大数据优先LR |
| 对偶与核的关系 | 理论深度 | 对偶形式使核技巧成为可能——目标函数只含内积 |

### Common Interview Questions

- **解释核技巧及其工作原理？** 通过 $K(x,z) = \phi(x)^T\phi(z)$ 隐式计算高维内积，要求满足Mercer条件
- **什么是支持向量？** $\alpha_i > 0$ 的样本，完全决定决策边界，其他样本可删除不影响模型
- **$C$ 如何影响决策边界？** $C$ 大→间隔小→可能过拟合；$C$ 小→间隔大→可能欠拟合。$C \to \infty$ 退化为硬间隔
- **何时选SVM而非LR？** 小数据、高维稀疏、需非线性边界、不需概率输出
- **RBF核为何映射到无限维？** 泰勒展开包含所有阶多项式项
- **Hinge vs CE Loss？** Hinge在 $yf(x)>1$ 处梯度为0，产生稀疏解
- **SVM的计算瓶颈？** 核矩阵 $O(n^2)$，SMO $O(n^2\sim n^3)$。解决：LinearSVC $O(nd)$，或近似核方法如 **Nystrom Approximation（Nystrom近似）** 和 **Random Fourier Features（随机傅里叶特征）**

## Key Takeaways

- SVM最大化间隔，原始问题→拉格朗日对偶→KKT条件是完整分析链路
- 核技巧避免显式高维映射，Mercer条件保证核函数有效性
- 支持向量决定边界——SVM的稀疏性优势和鲁棒性来源
- 训练前必须特征缩放（StandardScaler）
- Hinge Loss vs Log Loss vs 0-1 Loss：理解各自梯度特性
- 大规模数据用LinearSVC/LR/树模型；核SVM受限于 $O(n^2)$ 内存
- 近似核方法（Random Fourier Features）可扩展到大规模数据
