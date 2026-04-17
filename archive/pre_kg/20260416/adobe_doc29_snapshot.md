<!-- Pre-delete snapshot of company_documents.id=29 -->
<!-- company=Adobe title=ML Fundamentals From-Scratch 完整指南 (8大主题合并) -->
<!-- byte-identical duplicate of id=28 (Uber); deleted per T-P1-479 -->

# ML Fundamentals From-Scratch Complete Guide (8 Topics Merged)

> Condensed guide: duplicated code reduced to canonical examples + cross-references.
> Each topic standalone-readable. Cross-topic references marked as "see TX Section Y".

---

# T1: Gradient Descent 手写实现 + 理论

> 本节覆盖：Loss Function 定义、手写求导、Batch/SGD/Mini-batch 三种变体从零实现（纯Python + PyTorch）、Gradient Clipping。
> 合并来源：Doc 24 Section 3, Framework Node 74

---

## 1. Loss Function 定义

### 1.1 MSE（Mean Squared Error，均方误差）

用于回归任务：

$$\mathcal{L}_{\text{MSE}} = \frac{1}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)^2$$

其中 $\hat{y}_i = w^Tx_i + b$。

**对参数的梯度**：

$$\frac{\partial \mathcal{L}}{\partial w} = -\frac{2}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)x_i$$

$$\frac{\partial \mathcal{L}}{\partial b} = -\frac{2}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)$$

### 1.2 BCE（Binary Cross-Entropy，二元交叉熵）

用于二分类任务（$\hat{y}_i = \sigma(w^Tx_i + b)$，$\sigma$ 为 **Sigmoid** 函数）：

$$\mathcal{L}_{\text{BCE}} = -\frac{1}{N}\sum_{i=1}^{N}\left[y_i\log\hat{y}_i + (1-y_i)\log(1-\hat{y}_i)\right]$$

**对 logit $z_i = w^Tx_i + b$ 的梯度**（利用 $\sigma'(z) = \sigma(z)(1-\sigma(z))$）：

$$\frac{\partial \mathcal{L}}{\partial z_i} = \hat{y}_i - y_i$$

$$\frac{\partial \mathcal{L}}{\partial w} = \frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i - y_i)x_i$$

> **面试技巧**：BCE 对 logit 的梯度形式 $(\hat{y} - y)$ 和 MSE 对线性输出的梯度形式一样简洁——这不是巧合，而是 **GLM（Generalized Linear Model，广义线性模型）** 的统一性质。

---

## 2. 手写求导示例

### 2.1 标量情形：$f(x) = x^3 - 2x + 1$

$$f'(x) = 3x^2 - 2$$

在 $x=2$ 处：$f'(2) = 3 \times 4 - 2 = 10$

### 2.2 MSE Loss 对权重的求导（向量形式）

设 $\hat{\mathbf{y}} = \mathbf{X}\mathbf{w}$，$\mathcal{L} = \frac{1}{N}\|\mathbf{y} - \mathbf{X}\mathbf{w}\|^2$：

$$\frac{\partial \mathcal{L}}{\partial \mathbf{w}} = -\frac{2}{N}\mathbf{X}^T(\mathbf{y} - \mathbf{X}\mathbf{w})$$

**推导过程**：

$$\mathcal{L} = \frac{1}{N}(\mathbf{y} - \mathbf{X}\mathbf{w})^T(\mathbf{y} - \mathbf{X}\mathbf{w})$$

$$= \frac{1}{N}(\mathbf{y}^T\mathbf{y} - 2\mathbf{w}^T\mathbf{X}^T\mathbf{y} + \mathbf{w}^T\mathbf{X}^T\mathbf{X}\mathbf{w})$$

$$\frac{\partial \mathcal{L}}{\partial \mathbf{w}} = \frac{1}{N}(-2\mathbf{X}^T\mathbf{y} + 2\mathbf{X}^T\mathbf{X}\mathbf{w}) = -\frac{2}{N}\mathbf{X}^T(\mathbf{y} - \mathbf{X}\mathbf{w})$$

### 2.3 Sigmoid + BCE Loss 求导链

设 $z = w^Tx + b$，$\hat{y} = \sigma(z)$，$\mathcal{L} = -[y\log\hat{y} + (1-y)\log(1-\hat{y})]$：

$$\frac{\partial \mathcal{L}}{\partial \hat{y}} = -\frac{y}{\hat{y}} + \frac{1-y}{1-\hat{y}}$$

$$\frac{\partial \hat{y}}{\partial z} = \hat{y}(1-\hat{y})$$

$$\frac{\partial \mathcal{L}}{\partial z} = \frac{\partial \mathcal{L}}{\partial \hat{y}} \cdot \frac{\partial \hat{y}}{\partial z} = \left(-\frac{y}{\hat{y}} + \frac{1-y}{1-\hat{y}}\right)\hat{y}(1-\hat{y}) = \hat{y} - y$$

$$\frac{\partial \mathcal{L}}{\partial w} = (\hat{y} - y)x, \quad \frac{\partial \mathcal{L}}{\partial b} = \hat{y} - y$$

> **关键结论**：无论 MSE+线性 还是 BCE+Sigmoid，梯度都简化为 $(\hat{y}-y) \cdot x$ 形式。

---

## 3. 梯度下降核心原理

### 3.1 更新规则

$$w_{t+1} = w_t - \eta \nabla \mathcal{L}(w_t)$$

**来源于一阶泰勒展开**：

$$\mathcal{L}(w + \Delta w) \approx \mathcal{L}(w) + \nabla\mathcal{L}(w)^T \Delta w$$

在约束 $\|\Delta w\| \leq \eta$ 下，最小化方向为 $\Delta w = -\eta \frac{\nabla\mathcal{L}}{\|\nabla\mathcal{L}\|}$，即负梯度方向。

### 3.2 三种变体对比

| | **Batch GD（批量梯度下降）** | **Mini-batch GD（小批量梯度下降）** | **SGD（Stochastic GD，随机梯度下降）** |
|---|---|---|---|
| 每次用多少数据 | 全部 $N$ 个 | $B$ 个 (如32, 64, 256) | 1个 |
| 梯度估计 | $$g = \frac{1}{N}\sum_{i=1}^N \nabla L_i$$ | $$g = \frac{1}{B}\sum_{i=1}^B \nabla L_i$$ | $$g = \nabla L_i$$ |
| 梯度噪声 | 无 (精确梯度) | 中等 | 很大 |
| 每步计算量 | 最大 | 中等 | 最小 |
| 收敛轨迹 | 平滑 | 适度震荡 | 剧烈震荡 |
| 能否逃出局部最优 | 难 | 有可能 | 最容易 |

### 3.3 Batch Size 影响分析

**计算效率**：大 batch 可以更好地利用GPU并行，throughput (samples/sec) 更高。但超过GPU memory上限后无法再增大。

**收敛速度 (steps)**：大 batch 每步梯度更准，但**不一定**收敛到更好的解。实际上大 batch 通常需要更多 epoch 才能达到同样的 loss。

**Gradient Noise 的正面作用**：小 batch 引入的噪声反而是有益的！
- 噪声帮助跳出 **Sharp Minima（尖锐极小值）**
- 大 batch 倾向于收敛到 sharp minima → 泛化差

**泛化能力**：
- **关键发现** (Keskar et al., 2017)：大 batch 倾向 sharp minima，小 batch 倾向 **Flat Minima（平坦极小值）**
- Flat minima 对参数扰动不敏感 → 在测试集上表现更稳定
- 经验法则：batch size 太大会伤害泛化

**Linear Scaling Rule（线性缩放规则）**：如果 batch size 乘以 $k$，学习率也要乘以 $k$（但有上限，太大会不稳定）。

**实际建议**：
- 默认从 batch_size=32 或 64 开始
- 如果GPU利用率不高，适当增大
- 如果泛化gap大（train好test差），减小 batch size
- **Learning Rate Warmup（学习率预热）** 对大 batch 很重要

---

## 4. 从零实现：纯 Python

### 4.1 Batch Gradient Descent（线性回归 + MSE）

```python
import numpy as np

def batch_gradient_descent(X, y, lr=0.01, epochs=1000):
    """
    Batch GD for linear regression (MSE loss).
    X: (N, D), y: (N,)
    """
    N, D = X.shape
    w = np.zeros(D)
    b = 0.0
    losses = []

    for epoch in range(epochs):
        # Forward: predictions
        y_hat = X @ w + b                      # (N,)

        # Loss: MSE
        loss = np.mean((y - y_hat) ** 2)
        losses.append(loss)

        # Gradient (full batch)
        error = y_hat - y                       # (N,)
        grad_w = (2 / N) * (X.T @ error)       # (D,)
        grad_b = (2 / N) * np.sum(error)        # scalar

        # Update
        w -= lr * grad_w
        b -= lr * grad_b

    return w, b, losses
```

### 4.2 SGD（每次1个样本）

```python
def sgd(X, y, lr=0.01, epochs=100):
    """
    Stochastic GD: update per sample.
    """
    N, D = X.shape
    w = np.zeros(D)
    b = 0.0
    losses = []

    for epoch in range(epochs):
        # Shuffle data each epoch
        indices = np.random.permutation(N)
        epoch_loss = 0.0

        for i in indices:
            xi, yi = X[i], y[i]
            y_hat = xi @ w + b

            # Gradient (single sample)
            error = y_hat - yi
            grad_w = 2 * error * xi             # (D,)
            grad_b = 2 * error                  # scalar

            w -= lr * grad_w
            b -= lr * grad_b
            epoch_loss += error ** 2

        losses.append(epoch_loss / N)

    return w, b, losses
```

### 4.3 Mini-batch GD

```python
def mini_batch_gd(X, y, lr=0.01, epochs=100, batch_size=32):
    """
    Mini-batch GD: update per batch of B samples.
    """
    N, D = X.shape
    w = np.zeros(D)
    b = 0.0
    losses = []

    for epoch in range(epochs):
        indices = np.random.permutation(N)
        epoch_loss = 0.0
        n_batches = 0

        for start in range(0, N, batch_size):
            batch_idx = indices[start:start + batch_size]
            X_b, y_b = X[batch_idx], y[batch_idx]
            B = len(X_b)

            # Forward
            y_hat = X_b @ w + b

            # Gradient (mini-batch)
            error = y_hat - y_b
            grad_w = (2 / B) * (X_b.T @ error)
            grad_b = (2 / B) * np.sum(error)

            # Update
            w -= lr * grad_w
            b -= lr * grad_b

            epoch_loss += np.mean(error ** 2)
            n_batches += 1

        losses.append(epoch_loss / n_batches)

    return w, b, losses
```

---

## 5. PyTorch 实现

### 5.1 手动 GD（不用 optimizer）

```python
import torch

def manual_gd_pytorch(X, y, lr=0.01, epochs=500):
    """
    Manual gradient descent using PyTorch autograd.
    Demonstrates the raw update loop without torch.optim.
    """
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)

    w = torch.zeros(X.shape[1], requires_grad=True)
    b = torch.zeros(1, requires_grad=True)

    for epoch in range(epochs):
        # Forward
        y_hat = X_t @ w + b
        loss = torch.mean((y_t - y_hat) ** 2)

        # Backward
        loss.backward()

        # Update (no_grad to avoid tracking)
        with torch.no_grad():
            w -= lr * w.grad
            b -= lr * b.grad

        # Zero gradients
        w.grad.zero_()
        b.grad.zero_()

    return w.detach().numpy(), b.detach().numpy()
```

### 5.2 Mini-batch with DataLoader

```python
import torch
from torch.utils.data import TensorDataset, DataLoader

def train_with_dataloader(X, y, lr=0.01, epochs=100, batch_size=32):
    """
    Standard PyTorch training loop with DataLoader.
    """
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    dataset = TensorDataset(X_t, y_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = torch.nn.Linear(X.shape[1], 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    criterion = torch.nn.MSELoss()

    for epoch in range(epochs):
        for X_batch, y_batch in loader:
            y_hat = model(X_batch).squeeze()
            loss = criterion(y_hat, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return model
```

### 5.3 使用 Adam + Learning Rate Scheduler

```python
def train_adam_with_scheduler(X, y, epochs=200, batch_size=64):
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    loader = DataLoader(TensorDataset(X_t, y_t), batch_size=batch_size, shuffle=True)

    model = torch.nn.Linear(X.shape[1], 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = torch.nn.MSELoss()

    for epoch in range(epochs):
        for X_b, y_b in loader:
            y_hat = model(X_b).squeeze()
            loss = criterion(y_hat, y_b)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        scheduler.step()

    return model
```

---

## 6. Gradient Clipping 实现

### 6.1 原理

防止 **Exploding Gradients（梯度爆炸）**，在更新前裁剪梯度：

**按范数裁剪（Clip by Norm）**：

$$g \leftarrow g \cdot \min\left(1, \frac{\theta}{\|g\|}\right)$$

保持梯度方向不变，只缩小过大的梯度。

**按值裁剪（Clip by Value）**：

$$g_j \leftarrow \text{clip}(g_j, -\theta, \theta)$$

逐元素裁剪，可能改变梯度方向。

### 6.2 纯 Python 实现

```python
def clip_grad_by_norm(grads, max_norm=1.0):
    """
    Clip gradients by global norm.
    grads: list of numpy arrays
    """
    total_norm = np.sqrt(sum(np.sum(g ** 2) for g in grads))
    clip_coef = max_norm / (total_norm + 1e-6)
    if clip_coef < 1.0:
        for g in grads:
            g *= clip_coef
    return grads, total_norm

def clip_grad_by_value(grads, max_val=1.0):
    """Clip gradients element-wise."""
    return [np.clip(g, -max_val, max_val) for g in grads]
```

### 6.3 Mini-batch GD + Gradient Clipping

与 Section 4.3 的 `mini_batch_gd` 相同，仅在梯度更新前加两行裁剪：

```python
# 在 grad_w, grad_b 计算后、w -= lr * grad_w 之前加入:
[grad_w, grad_b_arr], _ = clip_grad_by_norm(
    [grad_w, np.array([grad_b])], max_norm=max_norm
)
grad_b = grad_b_arr[0]
```

完整实现 = Section 4.3 `mini_batch_gd` + 上述 3 行 + 函数签名加 `max_norm` 参数。

### 6.4 PyTorch Gradient Clipping

```python
# Standard practice: clip after backward(), before step()
optimizer.zero_grad()
loss.backward()

# Method 1: Clip by global norm (recommended, preserves direction)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Method 2: Clip by value
torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=1.0)

optimizer.step()
```

---

## 7. 面试要点总结

### 必须掌握的推导

| 题目 | 关键结果 |
|------|---------|
| MSE 对 $w$ 求导 | $-\frac{2}{N}\mathbf{X}^T(\mathbf{y}-\hat{\mathbf{y}})$ |
| BCE+Sigmoid 对 $w$ 求导 | $\frac{1}{N}\mathbf{X}^T(\hat{\mathbf{y}}-\mathbf{y})$ |
| 泰勒展开推导 GD | 一阶展开 → 负梯度方向最小化 |
| Gradient clipping by norm | $g \cdot \min(1, \theta/\|g\|)$，保持方向 |

### 高频面试问题

- **手写 GD 更新公式并解释每一项**
  - $w_{t+1} = w_t - \eta \nabla\mathcal{L}(w_t)$：$\eta$ 是学习率，$\nabla\mathcal{L}$ 是梯度
- **Batch/SGD/Mini-batch 区别？哪个泛化最好？**
  - Mini-batch 最佳折中；小 batch 的 gradient noise 帮助收敛到 flat minima → 泛化更好
- **Batch size 越大越好吗？**
  - 不是。大 batch 倾向 sharp minima（Keskar 2017），泛化差。需要配合 learning rate warmup 和 linear scaling rule
- **什么是 gradient clipping？什么时候用？**
  - 防止梯度爆炸，RNN/Transformer 训练标准做法。按范数裁剪优于按值裁剪（保持方向）
- **从泰勒展开推导梯度下降？**
  - $\mathcal{L}(w+\Delta w) \approx \mathcal{L}(w) + \nabla\mathcal{L}^T\Delta w$，约束 $\|\Delta w\|\leq\eta$ 下取最小 → $\Delta w = -\eta\nabla\mathcal{L}/\|\nabla\mathcal{L}\|$

### Follow-up 准备

- 如何让大 batch 也能泛化好？→ **LARS/LAMB** optimizer + learning rate warmup
- Learning rate 如何调？→ Warmup + Cosine Decay / Step Decay
- 梯度消失怎么办？→ 残差连接、**BatchNorm（Batch Normalization，批归一化）**、正确初始化（详见 T7）
- SGD vs Adam？→ 详见 T8 Optimizers 章节


---

# T2: Linear Regression 手写实现 + 理论

> 本节覆盖：Normal Equation 推导、GD 实现、两种求法对比、6 大假设、矩阵形式代码、正则化。
> 合并来源：Doc 24 Section 2 (GLM 部分), Framework Node 64

---

## 1. 模型定义

### 1.1 标量形式

$$\hat{y} = w_1x_1 + w_2x_2 + \cdots + w_Dx_D + b$$

### 1.2 矩阵形式

设 $\mathbf{X} \in \mathbb{R}^{N \times D}$（$N$ 个样本，$D$ 个特征），$\mathbf{y} \in \mathbb{R}^N$，$\mathbf{w} \in \mathbb{R}^D$：

$$\hat{\mathbf{y}} = \mathbf{X}\mathbf{w} + b$$

为简化推导，将 bias 吸收到权重中：在 $\mathbf{X}$ 最后加一列全 1，$\mathbf{w}$ 增加一维。则：

$$\hat{\mathbf{y}} = \mathbf{X}\mathbf{w}$$

其中 $\mathbf{X} \in \mathbb{R}^{N \times (D+1)}$，$\mathbf{w} \in \mathbb{R}^{D+1}$。

---

## 2. Loss Function：MSE

$$\mathcal{L}(\mathbf{w}) = \frac{1}{N}\|\mathbf{y} - \mathbf{X}\mathbf{w}\|^2 = \frac{1}{N}(\mathbf{y} - \mathbf{X}\mathbf{w})^T(\mathbf{y} - \mathbf{X}\mathbf{w})$$

展开：

$$\mathcal{L} = \frac{1}{N}\left(\mathbf{y}^T\mathbf{y} - 2\mathbf{w}^T\mathbf{X}^T\mathbf{y} + \mathbf{w}^T\mathbf{X}^T\mathbf{X}\mathbf{w}\right)$$

**为什么用 MSE？**
- 假设误差 $\epsilon \sim \mathcal{N}(0, \sigma^2)$，则 **MLE（Maximum Likelihood Estimation，最大似然估计）** 等价于最小化 MSE
- MSE 对 $\mathbf{w}$ 是凸函数，保证全局最优解存在且唯一（当 $\mathbf{X}^T\mathbf{X}$ 可逆时）

---

## 3. 求解方法一：Normal Equation（正规方程）

### 3.1 推导

对 $\mathcal{L}$ 关于 $\mathbf{w}$ 求导并令其为零：

$$\frac{\partial \mathcal{L}}{\partial \mathbf{w}} = \frac{1}{N}(-2\mathbf{X}^T\mathbf{y} + 2\mathbf{X}^T\mathbf{X}\mathbf{w}) = 0$$

$$\mathbf{X}^T\mathbf{X}\mathbf{w} = \mathbf{X}^T\mathbf{y}$$

$$\boxed{\mathbf{w}^* = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}}$$

### 3.2 推导中用到的矩阵微积分

| 公式 | 结果 |
|------|------|
| $\frac{\partial}{\partial \mathbf{w}}(\mathbf{a}^T\mathbf{w})$ | $\mathbf{a}$ |
| $\frac{\partial}{\partial \mathbf{w}}(\mathbf{w}^T\mathbf{A}\mathbf{w})$ | $(\mathbf{A} + \mathbf{A}^T)\mathbf{w}$（$\mathbf{A}$ 对称时为 $2\mathbf{A}\mathbf{w}$） |
| $\frac{\partial}{\partial \mathbf{w}}\|\mathbf{y} - \mathbf{X}\mathbf{w}\|^2$ | $-2\mathbf{X}^T(\mathbf{y} - \mathbf{X}\mathbf{w})$ |

### 3.3 Normal Equation 的限制

- 需要计算 $(\mathbf{X}^T\mathbf{X})^{-1}$，复杂度 $O(D^3)$
- 当 $D$ 很大（>10,000）时不实际
- 当 $\mathbf{X}^T\mathbf{X}$ 不可逆（特征共线性）时无法直接求解 → 用伪逆 $(\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})^{-1}$（即 Ridge 回归）

### 3.4 纯 Python 实现

```python
import numpy as np

def normal_equation(X, y):
    """
    Closed-form solution for linear regression.
    X: (N, D) feature matrix (without bias column)
    y: (N,) target vector
    Returns: w (D+1,) including bias as last element
    """
    N = X.shape[0]
    # Add bias column
    X_aug = np.hstack([X, np.ones((N, 1))])

    # w* = (X^T X)^{-1} X^T y
    XtX = X_aug.T @ X_aug
    Xty = X_aug.T @ y
    w = np.linalg.solve(XtX, Xty)  # More stable than np.linalg.inv
    return w

# --- Example ---
np.random.seed(42)
X = np.random.randn(100, 3)
w_true = np.array([2.0, -1.0, 0.5])
y = X @ w_true + 3.0 + np.random.randn(100) * 0.1  # bias=3.0

w_hat = normal_equation(X, y)
print(f"True weights: {w_true}, bias: 3.0")
print(f"Estimated:    {w_hat[:3]}, bias: {w_hat[3]:.4f}")
```

> **面试注意**：用 `np.linalg.solve` 而非 `np.linalg.inv`，数值更稳定且更快（$O(D^3)$ vs $O(D^3)$ 但常数更小）。

---

## 4. 求解方法二：Gradient Descent

### 4.1 梯度推导

$$\frac{\partial \mathcal{L}}{\partial \mathbf{w}} = -\frac{2}{N}\mathbf{X}^T(\mathbf{y} - \mathbf{X}\mathbf{w})$$

更新规则：

$$\mathbf{w}_{t+1} = \mathbf{w}_t - \eta \cdot \left(-\frac{2}{N}\mathbf{X}^T(\mathbf{y} - \mathbf{X}\mathbf{w}_t)\right) = \mathbf{w}_t + \frac{2\eta}{N}\mathbf{X}^T(\mathbf{y} - \mathbf{X}\mathbf{w}_t)$$

### 4.2 纯 Python 实现（Batch GD + Mini-batch）

> **结构与 T1 Section 4.3 `mini_batch_gd` 相同**，仅以下两处不同：
> 1. 将 bias 吸收到 `X_aug`（增广矩阵），无单独的 `b`
> 2. 梯度公式不同：`grad = -(2/B) * (X_b.T @ residual)`（注意负号——用 residual = y - y_hat）

```python
def linear_regression_gd(X, y, lr=0.01, epochs=1000, batch_size=None):
    """Linear regression via gradient descent."""
    N, D = X.shape
    X_aug = np.hstack([X, np.ones((N, 1))])  # Absorb bias into X
    w = np.zeros(D + 1)
    losses = []
    if batch_size is None:
        batch_size = N

    for epoch in range(epochs):
        indices = np.random.permutation(N)
        epoch_loss, n_batches = 0.0, 0
        for start in range(0, N, batch_size):
            idx = indices[start:start + batch_size]
            X_b, y_b = X_aug[idx], y[idx]
            B = len(X_b)
            y_hat = X_b @ w
            # KEY DIFFERENCE: gradient uses augmented X, residual formulation
            grad = -(2 / B) * (X_b.T @ (y_b - y_hat))
            w -= lr * grad
            epoch_loss += np.mean((y_b - y_hat) ** 2)
            n_batches += 1
        losses.append(epoch_loss / n_batches)
    return w, losses
```

---

## 5. 两种方法对比

| | **Normal Equation** | **Gradient Descent** |
|---|---|---|
| 时间复杂度 | $O(ND^2 + D^3)$ | $O(NDE)$，$E$ = epochs |
| 适用场景 | $D < 10{,}000$ | 任意 $D$ |
| 超参数 | 无 | $\eta$, epochs, batch_size |
| 数值稳定性 | 需要 $\mathbf{X}^T\mathbf{X}$ 可逆 | 总是可用 |
| 内存 | 需要存储 $D \times D$ 矩阵 | 只需一个 batch |
| 在线学习 | 不支持 | 天然支持（SGD） |
| 实际工业界 | sklearn 默认用 SVD 分解 | 大数据/深度学习标配 |

**面试结论**：小数据 + 低维度 → Normal Equation；大数据 / 高维 / 需要在线更新 → GD。

---

## 6. 六大假设（OLS Assumptions）

**OLS（Ordinary Least Squares，普通最小二乘法）** 的经典假设：

### 6.1 线性假设（Linearity）

$$E[y|\mathbf{x}] = \mathbf{x}^T\mathbf{w}$$

- 因变量与自变量之间是线性关系
- **检验**：残差图（residual plot），残差应随机分布，无明显模式
- **违反后果**：模型系统性偏差（underfitting）
- **修复**：添加多项式特征、对数变换、非线性模型

### 6.2 独立性（Independence of Errors）

$$\text{Cov}(\epsilon_i, \epsilon_j) = 0 \quad \forall i \neq j$$

- 误差项之间相互独立
- **常见违反场景**：时间序列数据（相邻时间点的误差相关）
- **检验**：Durbin-Watson 检验（值接近 2 表示无自相关）
- **违反后果**：标准误估计不准确，t 检验和 F 检验失效

### 6.3 同方差性（Homoscedasticity）

$$\text{Var}(\epsilon_i) = \sigma^2 \quad \forall i$$

- 误差项方差恒定，不随 $x$ 变化
- **违反场景**：收入预测（高收入人群方差更大）
- **检验**：Breusch-Pagan 检验、残差 vs 拟合值图
- **违反后果**：OLS 仍无偏，但不再是 **BLUE（Best Linear Unbiased Estimator，最佳线性无偏估计）**
- **修复**：**WLS（Weighted Least Squares，加权最小二乘）**、对 $y$ 取对数

### 6.4 误差正态性（Normality of Errors）

$$\epsilon_i \sim \mathcal{N}(0, \sigma^2)$$

- **用途**：做假设检验和构造置信区间时需要
- **大样本时**：中心极限定理保证系数近似正态，此假设可放宽
- **检验**：Q-Q plot、Shapiro-Wilk 检验
- **注意**：OLS 求解本身不需要正态性假设（MLE 需要）

### 6.5 无多重共线性（No Perfect Multicollinearity）

$$\text{rank}(\mathbf{X}) = D + 1$$

- 特征之间不存在完美线性关系
- **违反后果**：$\mathbf{X}^T\mathbf{X}$ 不可逆，Normal Equation 无解
- **近似共线性后果**：系数估计方差极大，不稳定
- **检验**：**VIF（Variance Inflation Factor，方差膨胀因子）**，VIF > 10 表示严重共线性
- **修复**：删除冗余特征、**PCA（Principal Component Analysis，主成分分析）** 降维、Ridge 正则化

### 6.6 外生性（Exogeneity）

$$E[\epsilon|\mathbf{X}] = 0$$

- 误差项与自变量不相关
- **违反场景**：遗漏变量偏差（omitted variable bias）——重要变量没有纳入模型
- **违反后果**：OLS 估计有偏且不一致
- **修复**：添加遗漏变量、**IV（Instrumental Variables，工具变量）** 方法

### 假设总结表

| # | 假设 | 违反后果 | 检验方法 |
|---|------|---------|---------|
| 1 | Linearity | 系统偏差 | 残差图 |
| 2 | Independence | 标准误不准 | Durbin-Watson |
| 3 | Homoscedasticity | 不再 BLUE | Breusch-Pagan |
| 4 | Normality | 检验失效 | Q-Q plot |
| 5 | No Multicollinearity | 不可逆/不稳定 | VIF |
| 6 | Exogeneity | 有偏估计 | 领域知识 |

---

## 7. 正则化：Ridge 与 Lasso

### 7.1 Ridge Regression（L2 正则化）

$$\mathcal{L}_{\text{Ridge}} = \frac{1}{N}\|\mathbf{y} - \mathbf{X}\mathbf{w}\|^2 + \lambda\|\mathbf{w}\|_2^2$$

**闭式解**：

$$\mathbf{w}^*_{\text{Ridge}} = (\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})^{-1}\mathbf{X}^T\mathbf{y}$$

- $\lambda > 0$ 保证矩阵可逆，解决共线性问题
- 缩小系数但不会变成 0
- 几何解释：约束 $\|\mathbf{w}\|_2^2 \leq t$，等高线与圆的切点

### 7.2 Lasso Regression（L1 正则化）

$$\mathcal{L}_{\text{Lasso}} = \frac{1}{N}\|\mathbf{y} - \mathbf{X}\mathbf{w}\|^2 + \lambda\|\mathbf{w}\|_1$$

- **无闭式解**，需要用坐标下降法（Coordinate Descent）或次梯度法
- 可以产生稀疏解（部分 $w_j = 0$）→ 自动特征选择
- 几何解释：约束 $\|\mathbf{w}\|_1 \leq t$，等高线与菱形的角点

### 7.3 Ridge vs Lasso 对比

| | **Ridge (L2)** | **Lasso (L1)** |
|---|---|---|
| 惩罚项 | $\lambda\|\mathbf{w}\|_2^2$ | $\lambda\|\mathbf{w}\|_1$ |
| 闭式解 | 有 | 无 |
| 稀疏性 | 不产生稀疏 | 产生稀疏（特征选择） |
| 共线特征处理 | 系数平均分配 | 随机选一个，其余为 0 |
| 适用场景 | 特征都重要 | 很多无关特征 |

### 7.4 Ridge 实现

```python
def ridge_regression(X, y, lam=1.0):
    """
    Ridge regression closed-form solution.
    lam: regularization strength (lambda)
    """
    N = X.shape[0]
    X_aug = np.hstack([X, np.ones((N, 1))])
    D = X_aug.shape[1]

    # w* = (X^T X + lambda * I)^{-1} X^T y
    # Note: don't regularize the bias term
    reg_matrix = lam * np.eye(D)
    reg_matrix[-1, -1] = 0  # No regularization on bias

    w = np.linalg.solve(X_aug.T @ X_aug + reg_matrix, X_aug.T @ y)
    return w
```

---

## 8. PyTorch 实现

### 8.1 手动实现（Normal Equation）

```python
import torch

def normal_equation_torch(X, y):
    """Normal equation using PyTorch (GPU-compatible)."""
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    N = X_t.shape[0]

    # Add bias column
    ones = torch.ones(N, 1)
    X_aug = torch.cat([X_t, ones], dim=1)

    # w* = (X^T X)^{-1} X^T y
    w = torch.linalg.solve(X_aug.T @ X_aug, X_aug.T @ y_t)
    return w.numpy()
```

### 8.2 GD with nn.Linear

> **与 T1 Section 5.2 `train_with_dataloader` 结构完全相同**，仅配置不同：

```python
def train_linear_regression(X, y, lr=0.01, epochs=200, batch_size=32,
                            weight_decay=0.0):
    """PyTorch linear regression. Same loop as T1 Sec 5.2."""
    # Setup: same as T1 canonical template
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    loader = DataLoader(TensorDataset(X_t, y_t), batch_size=batch_size, shuffle=True)

    model = torch.nn.Linear(X.shape[1], 1)       # Config: 1 output
    optimizer = torch.optim.SGD(model.parameters(), lr=lr,
                                weight_decay=weight_decay)  # Config: weight_decay for Ridge
    criterion = torch.nn.MSELoss()                # Config: MSE loss

    # Training loop: identical to T1 Section 5.2
    for epoch in range(epochs):
        for X_b, y_b in loader:
            y_hat = model(X_b).squeeze()
            loss = criterion(y_hat, y_b)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    w = model.weight.detach().numpy().flatten()
    b = model.bias.detach().item()
    return w, b
```

### 8.3 sklearn 对比验证

```python
from sklearn.linear_model import LinearRegression, Ridge

# --- Verify our implementations against sklearn ---
np.random.seed(42)
X = np.random.randn(200, 5)
w_true = np.array([3.0, -2.0, 1.5, 0.0, -0.5])
y = X @ w_true + 2.0 + np.random.randn(200) * 0.5

# sklearn
sk_model = LinearRegression().fit(X, y)
print("sklearn weights:", sk_model.coef_, "bias:", sk_model.intercept_)

# Normal equation
w_ne = normal_equation(X, y)
print("Normal eq weights:", w_ne[:5], "bias:", w_ne[5])

# GD
w_gd, losses = linear_regression_gd(X, y, lr=0.01, epochs=2000)
print("GD weights:", w_gd[:5], "bias:", w_gd[5])
print(f"Final MSE: {losses[-1]:.6f}")
```

---

## 9. MLE 视角：为什么 MSE = MLE

假设 $y = \mathbf{x}^T\mathbf{w} + \epsilon$，$\epsilon \sim \mathcal{N}(0, \sigma^2)$，则：

$$p(y|\mathbf{x}, \mathbf{w}) = \frac{1}{\sqrt{2\pi}\sigma}\exp\left(-\frac{(y - \mathbf{x}^T\mathbf{w})^2}{2\sigma^2}\right)$$

对 $N$ 个独立样本，对数似然为：

$$\log L = -\frac{N}{2}\log(2\pi\sigma^2) - \frac{1}{2\sigma^2}\sum_{i=1}^N(y_i - \mathbf{x}_i^T\mathbf{w})^2$$

最大化 $\log L$ 等价于最小化：

$$\sum_{i=1}^N(y_i - \mathbf{x}_i^T\mathbf{w})^2 = N \cdot \text{MSE}$$

**结论**：在高斯噪声假设下，MSE 的解 = MLE 的解。这也解释了为什么正态性假设对 MLE 推导很重要，但对 OLS 求解本身不必要。

---

## 10. GLM 视角：Linear vs Logistic（合并 Doc 24 Section 2.3）

**GLM（Generalized Linear Model，广义线性模型）** 框架下，Linear Regression 和 Logistic Regression 是同一模型族：

| | **Linear Regression** | **Logistic Regression** |
|---|---|---|
| 响应变量分布 | Normal (Gaussian) | Bernoulli |
| Link function | Identity: $\mu = \mathbf{w}^T\mathbf{x}$ | Logit: $\log\frac{p}{1-p} = \mathbf{w}^T\mathbf{x}$ |
| 输出 | 连续实数 $(-\infty, +\infty)$ | 概率 $\in (0,1)$ |
| Loss | MSE (from Gaussian MLE) | BCE (from Bernoulli MLE) |
| 梯度形式 | $(\hat{y} - y)\mathbf{x}$ | $(\hat{y} - y)\mathbf{x}$ |

GLM 三要素：(1) 指数族分布，(2) 线性预测子 $\eta = \mathbf{w}^T\mathbf{x}$，(3) link function 连接 $\eta$ 和分布均值。

> **面试高分点**：梯度形式相同 $(\hat{y}-y)\mathbf{x}$ 不是巧合，而是指数族分布的统一性质（canonical link function）。

---

## 11. 面试要点总结

### 必须掌握的推导

| 题目 | 关键结果 |
|------|---------|
| Normal Equation 推导 | $\mathbf{w}^* = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}$ |
| MSE 梯度（矩阵形式） | $-\frac{2}{N}\mathbf{X}^T(\mathbf{y} - \mathbf{X}\mathbf{w})$ |
| Ridge 闭式解 | $(\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})^{-1}\mathbf{X}^T\mathbf{y}$ |
| MSE = MLE | 高斯噪声下最小化 MSE 等价于最大化似然 |

### 高频面试问题

- **Normal Equation 推导并说明什么时候用 / 不用？**
  - 推导：对 MSE 求导令为零。$D < 10{,}000$ 且无共线性时用；$D$ 很大或需在线学习时用 GD
- **Linear Regression 有哪些假设？违反了怎么办？**
  - 6 大假设：线性/独立/同方差/正态/无共线/外生。违反时分别有对应修复（见 Section 6）
- **Ridge vs Lasso 区别？什么时候选哪个？**
  - Ridge 缩小不置零，Lasso 可产生稀疏。特征多且大部分无关 → Lasso；特征都相关 → Ridge
- **GD vs Normal Equation 怎么选？**
  - 小 $D$（<10K）→ Normal Equation 精确且快；大 $D$ / 大 $N$ / 在线 → GD
- **为什么 MSE 是 MLE？**
  - 假设误差正态分布，最大化对数似然等价于最小化残差平方和
- **Linear Regression 和 Logistic Regression 数学上为什么是"同一模型"？**
  - GLM 框架：同一模型族，只改变分布假设和 link function。梯度形式都是 $(\hat{y}-y)\mathbf{x}$

### R-squared（决定系数 / 拟合优度）详解

**$R^2$（R-squared，决定系数，Coefficient of Determination）** 衡量模型对因变量方差的解释程度，取值范围通常为 $[0, 1]$。

#### 核心公式

$$
R^2 = 1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}}
$$

其中：

- **$\text{SS}_{\text{res}}$（Residual Sum of Squares，残差平方和）**：实际值与预测值的差距

$$
\text{SS}_{\text{res}} = \sum_{i=1}^{N}(y_i - \hat{y}_i)^2
$$

- **$\text{SS}_{\text{tot}}$（Total Sum of Squares，总平方和）**：实际值与均值的差距

$$
\text{SS}_{\text{tot}} = \sum_{i=1}^{N}(y_i - \bar{y})^2
$$

- **$\text{SS}_{\text{reg}}$（Regression Sum of Squares，回归平方和）**：预测值与均值的差距（模型解释的部分）

$$
\text{SS}_{\text{reg}} = \sum_{i=1}^{N}(\hat{y}_i - \bar{y})^2
$$

**关系**：$\text{SS}_{\text{tot}} = \text{SS}_{\text{res}} + \text{SS}_{\text{reg}}$（仅在含截距的 **OLS, Ordinary Least Squares（普通最小二乘法）** 下严格成立）

#### 直觉理解

| $R^2$ 值 | 含义 |
|:---:|:---|
| $1.0$ | 模型完美拟合，$\text{SS}_{\text{res}} = 0$ |
| $0.8$ | 模型解释了 80% 的方差，20% 为残差 |
| $0.0$ | 模型等价于用均值预测，$\hat{y}_i = \bar{y}$ |
| $< 0$ | 模型比均值还差（非线性模型或无截距时可能出现） |

#### Adjusted R-squared（调整决定系数）

$R^2$ 的问题：每增加一个特征，$R^2$ 只增不减（即使特征无用）。**Adjusted $R^2$** 对特征数量做惩罚：

$$
R^2_{\text{adj}} = 1 - \frac{(1 - R^2)(N - 1)}{N - D - 1}
$$

其中 $N$ 为样本数，$D$ 为特征数。增加无用特征时 $R^2_{\text{adj}}$ 会下降。

#### Python 计算

```python
def r_squared(y_true, y_pred):
    """计算 R-squared (决定系数)。"""
    ss_res = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred))
    y_mean = sum(y_true) / len(y_true)
    ss_tot = sum((yt - y_mean) ** 2 for yt in y_true)
    return 1 - ss_res / ss_tot

def adjusted_r_squared(y_true, y_pred, n_features):
    """计算 Adjusted R-squared。"""
    r2 = r_squared(y_true, y_pred)
    n = len(y_true)
    return 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
```

#### 面试常见 Follow-up

- **$R^2$ 一定在 $[0,1]$ 之间吗？** → 不一定。无截距模型或非 OLS 方法可以产生负值
- **$R^2$ 高就说明模型好吗？** → 不一定。过拟合时 $R^2$ 很高但泛化差；应看测试集 $R^2$ 或用 Adjusted $R^2$
- **$R^2$ 和 **MSE（Mean Squared Error，均方误差）** 的关系？** → $R^2 = 1 - \frac{N \cdot \text{MSE}}{\text{SS}_{\text{tot}}}$，$R^2$ 是归一化的 MSE

### Follow-up 准备

- 过拟合怎么办？→ L1/L2 正则化（详见 Section 7）、增加数据、减少特征
- 如何处理非线性关系？→ 多项式特征、核方法、直接用神经网络
- 特征共线性会怎样？→ 系数不稳定、方差大、**VIF（Variance Inflation Factor，方差膨胀因子）** 检测、Ridge 修复


---

# T3: Logistic Regression 手写实现 + 理论

> 本节覆盖：Sigmoid 推导、BCE Loss 从 MLE 推导、梯度标量→矩阵形式、手写 Python 实现、Decision Boundary、多分类扩展。
> 合并来源：Doc 24 Section 2 (Logistic Regression 深入), Framework Node 64

---

## 1. 模型定义

### 1.1 从 Log-Odds 到 Sigmoid

Logistic Regression 对 **log-odds（对数几率）** 做线性建模：

$$\log\frac{p}{1-p} = \mathbf{w}^T\mathbf{x} + b$$

其中 $p = P(Y=1|\mathbf{x})$。解出 $p$：

$$p = \frac{1}{1+e^{-(\mathbf{w}^T\mathbf{x}+b)}} = \sigma(\mathbf{w}^T\mathbf{x}+b)$$

### 1.2 Sigmoid 函数性质

$$\sigma(z) = \frac{1}{1+e^{-z}}$$

关键性质：

| 性质 | 公式 |
|------|------|
| 值域 | $(0, 1)$ |
| 对称性 | $\sigma(-z) = 1 - \sigma(z)$ |
| 导数 | $\sigma'(z) = \sigma(z)(1 - \sigma(z))$ |
| 单调性 | 严格递增 |
| 极限 | $\lim_{z\to+\infty}\sigma(z) = 1$，$\lim_{z\to-\infty}\sigma(z) = 0$ |

**导数推导**：

$$\sigma'(z) = \frac{e^{-z}}{(1+e^{-z})^2} = \frac{1}{1+e^{-z}} \cdot \frac{e^{-z}}{1+e^{-z}} = \sigma(z)(1-\sigma(z))$$

> **面试高分点**：Sigmoid 导数最大值在 $z=0$ 处取得，为 $0.25$。这意味着梯度天然被缩小，层数多时导致 **Vanishing Gradient（梯度消失）** 问题，所以深度网络隐藏层不用 Sigmoid。

### 1.3 为什么输出是概率（合并 Doc 24 Section 2.1）

不只是"Sigmoid 输出在 0 到 1 之间"这么简单：

1. **概率论角度**：假设 $P(Y=1|X)$ 服从 Bernoulli 分布，对 log-odds 做线性假设是自然的（Bernoulli 分布的 canonical link function）
2. **满足概率公理**：$0 < p < 1$ 且 $P(Y=0) = 1 - P(Y=1)$
3. **MLE 推导**：BCE Loss 是从 **NLL（Negative Log-Likelihood，负对数似然）** 直接推出来的，不是拍脑袋选的

### 1.4 矩阵形式

设 $\mathbf{X} \in \mathbb{R}^{N \times D}$，$\mathbf{y} \in \{0,1\}^N$，$\mathbf{w} \in \mathbb{R}^D$，$b \in \mathbb{R}$：

$$\mathbf{z} = \mathbf{X}\mathbf{w} + b \in \mathbb{R}^N$$

$$\hat{\mathbf{y}} = \sigma(\mathbf{z}) \in (0,1)^N$$

其中 $\sigma$ 逐元素应用。

---

## 2. Loss Function：BCE（Binary Cross-Entropy）

### 2.1 从 MLE 推导 BCE（合并 Doc 24 Section 2.2）

假设 $y \in \{0,1\}$，单个样本的似然函数为：

$$P(y|\mathbf{x}) = \hat{y}^y(1-\hat{y})^{1-y}$$

对 $N$ 个独立样本，对数似然为：

$$\log L = \sum_{i=1}^{N}\left[y_i\log\hat{y}_i + (1-y_i)\log(1-\hat{y}_i)\right]$$

最大化对数似然 = 最小化负对数似然（**NLL**）：

$$\boxed{\mathcal{L}_{\text{BCE}} = -\frac{1}{N}\sum_{i=1}^{N}\left[y_i\log\hat{y}_i + (1-y_i)\log(1-\hat{y}_i)\right]}$$

### 2.2 为什么用 BCE 而不用 MSE？

| | **BCE + Sigmoid** | **MSE + Sigmoid** |
|---|---|---|
| Loss Surface | 凸的，保证全局最优 | 非凸，有局部极小值 |
| 梯度形式 | $(\hat{y}-y)\mathbf{x}$，不含 $\sigma'$ | 含 $\sigma'(z)$ 项，梯度小 |
| 收敛速度 | 快（误差大时梯度大） | 慢（Sigmoid 饱和区梯度消失） |
| 理论基础 | MLE 直接推导 | 无概率解释 |

**直觉解释**：当 $y=1$ 但 $\hat{y} \approx 0$ 时：
- BCE: $-\log(\hat{y}) \to +\infty$，惩罚极大
- MSE: $(1-\hat{y})^2 \approx 1$，惩罚有限

BCE 对错误预测的惩罚更重，驱动模型更快修正。

---

## 3. 梯度推导：标量 → 矩阵形式

### 3.1 标量形式（单样本）

设 $z = \mathbf{w}^T\mathbf{x} + b$，$\hat{y} = \sigma(z)$，$\mathcal{L} = -[y\log\hat{y} + (1-y)\log(1-\hat{y})]$：

**Step 1**: $\frac{\partial \mathcal{L}}{\partial \hat{y}} = -\frac{y}{\hat{y}} + \frac{1-y}{1-\hat{y}}$

**Step 2**: $\frac{\partial \hat{y}}{\partial z} = \hat{y}(1-\hat{y})$

**Step 3** (Chain Rule):

$$\frac{\partial \mathcal{L}}{\partial z} = \frac{\partial \mathcal{L}}{\partial \hat{y}} \cdot \frac{\partial \hat{y}}{\partial z} = \left(-\frac{y}{\hat{y}} + \frac{1-y}{1-\hat{y}}\right)\hat{y}(1-\hat{y})$$

展开化简：

$$= -y(1-\hat{y}) + (1-y)\hat{y} = \hat{y} - y$$

**Step 4**:

$$\frac{\partial \mathcal{L}}{\partial w_j} = (\hat{y} - y)x_j, \quad \frac{\partial \mathcal{L}}{\partial b} = \hat{y} - y$$

> **关键结论**：梯度简化为 $(\hat{y}-y)\mathbf{x}$，Sigmoid 导数项在化简中消掉了。这不是巧合，而是 **GLM（Generalized Linear Model，广义线性模型）** 中 canonical link function 的统一性质。

### 3.2 向量形式（N 个样本）

$$\frac{\partial \mathcal{L}}{\partial \mathbf{w}} = \frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i - y_i)\mathbf{x}_i$$

$$\frac{\partial \mathcal{L}}{\partial b} = \frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i - y_i)$$

### 3.3 矩阵形式

$$\boxed{\frac{\partial \mathcal{L}}{\partial \mathbf{w}} = \frac{1}{N}\mathbf{X}^T(\hat{\mathbf{y}} - \mathbf{y})}$$

$$\frac{\partial \mathcal{L}}{\partial b} = \frac{1}{N}\mathbf{1}^T(\hat{\mathbf{y}} - \mathbf{y})$$

其中 $\hat{\mathbf{y}} = \sigma(\mathbf{X}\mathbf{w} + b) \in \mathbb{R}^N$。

**与 Linear Regression 的对比**：

| | **Linear Regression (MSE)** | **Logistic Regression (BCE)** |
|---|---|---|
| 梯度 | $-\frac{2}{N}\mathbf{X}^T(\mathbf{y} - \hat{\mathbf{y}})$ | $\frac{1}{N}\mathbf{X}^T(\hat{\mathbf{y}} - \mathbf{y})$ |
| 核心项 | $(\hat{y}-y)\mathbf{x}$ | $(\hat{y}-y)\mathbf{x}$ |
| $\hat{y}$ 定义 | $\mathbf{X}\mathbf{w}$ | $\sigma(\mathbf{X}\mathbf{w})$ |

形式完全一致，只是 $\hat{y}$ 的计算不同。

---

## 4. 纯 Python 实现

### 4.1 Sigmoid 与数值稳定性

```python
import numpy as np

def sigmoid(z):
    """
    Numerically stable sigmoid.
    Avoids overflow in exp(-z) for large positive z
    and overflow in exp(z) for large negative z.
    """
    return np.where(
        z >= 0,
        1 / (1 + np.exp(-z)),
        np.exp(z) / (1 + np.exp(z))
    )
```

> **面试注意**：直接用 `1/(1+np.exp(-z))` 在 $z \ll 0$ 时会导致 `np.exp(-z)` 溢出。分支写法避免此问题。

### 4.2 BCE Loss 计算（数值稳定版）

```python
def bce_loss(y, y_hat, eps=1e-12):
    """
    Binary cross-entropy loss with numerical stability.
    eps prevents log(0).
    """
    y_hat = np.clip(y_hat, eps, 1 - eps)
    return -np.mean(y * np.log(y_hat) + (1 - y) * np.log(1 - y_hat))
```

### 4.3 Mini-batch Logistic Regression（含可选 L2 正则化）

```python
def logistic_regression(X, y, lr=0.01, epochs=200, batch_size=32, lam=0.0):
    """
    Logistic regression via mini-batch gradient descent.
    lam > 0 enables L2 regularization: Loss = BCE + (lam/2)*||w||^2
    """
    N, D = X.shape
    w = np.zeros(D)
    b = 0.0
    losses = []

    for epoch in range(epochs):
        indices = np.random.permutation(N)
        epoch_loss, n_batches = 0.0, 0

        for start in range(0, N, batch_size):
            batch_idx = indices[start:start + batch_size]
            X_b, y_b = X[batch_idx], y[batch_idx]
            B = len(X_b)

            z = X_b @ w + b
            y_hat = sigmoid(z)

            epoch_loss += bce_loss(y_b, y_hat)
            n_batches += 1

            error = y_hat - y_b
            grad_w = (1 / B) * (X_b.T @ error) + lam * w  # L2: + lam*w
            grad_b = (1 / B) * np.sum(error)

            w -= lr * grad_w
            b -= lr * grad_b

        losses.append(epoch_loss / n_batches)

    return w, b, losses

# --- Example ---
np.random.seed(42)
X = np.random.randn(500, 2)
y = (X @ np.array([1.0, 2.0]) + 0.5 > 0).astype(float)

w, b, losses = logistic_regression(X, y, lr=0.1, epochs=300)
print(f"Learned weights: w={w}, b={b:.4f}")
print(f"Final BCE loss: {losses[-1]:.6f}")

# With L2 regularization:
w_l2, b_l2, _ = logistic_regression(X, y, lr=0.1, epochs=300, lam=0.01)
print(f"L2 weights: w={w_l2}, b={b_l2:.4f}")
```

---

## 5. Decision Boundary

### 5.1 数学定义

Decision boundary 是 $P(Y=1|\mathbf{x}) = 0.5$ 的等高线，即：

$$\sigma(\mathbf{w}^T\mathbf{x} + b) = 0.5 \iff \mathbf{w}^T\mathbf{x} + b = 0$$

对二维情形 ($D=2$)：

$$w_1x_1 + w_2x_2 + b = 0 \implies x_2 = -\frac{w_1}{w_2}x_1 - \frac{b}{w_2}$$

这是一条直线。**Logistic Regression 是线性分类器**——decision boundary 永远是超平面。

### 5.2 几何解释

- $\mathbf{w}$ 是 decision boundary 的法向量
- $\mathbf{w}$ 指向 $P(Y=1) > 0.5$ 的方向
- $|b|/\|\mathbf{w}\|$ 是原点到 boundary 的距离
- 离 boundary 越远，预测概率越接近 0 或 1（Sigmoid 饱和）

### 5.3 可视化代码

```python
def plot_decision_boundary(X, y, w, b):
    """
    Plot 2D decision boundary for logistic regression.
    X: (N, 2), y: (N,), w: (2,), b: scalar
    """
    import matplotlib.pyplot as plt

    # Plot data points
    pos = y == 1
    neg = y == 0
    plt.scatter(X[pos, 0], X[pos, 1], c='blue', label='y=1', alpha=0.5)
    plt.scatter(X[neg, 0], X[neg, 1], c='red', label='y=0', alpha=0.5)

    # Decision boundary: w1*x1 + w2*x2 + b = 0
    x1_range = np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 100)
    x2_boundary = -(w[0] * x1_range + b) / w[1]

    plt.plot(x1_range, x2_boundary, 'k-', linewidth=2, label='boundary')
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.legend()
    plt.title('Logistic Regression Decision Boundary')
    plt.show()
```

---

## 6. 多分类扩展：Softmax Regression

### 6.1 从二分类到多分类

当 $K > 2$ 类时，将 Sigmoid 替换为 **Softmax**：

$$P(Y=k|\mathbf{x}) = \frac{e^{\mathbf{w}_k^T\mathbf{x} + b_k}}{\sum_{j=1}^{K}e^{\mathbf{w}_j^T\mathbf{x} + b_j}}, \quad k = 1, \ldots, K$$

参数变为权重矩阵 $\mathbf{W} \in \mathbb{R}^{D \times K}$，$\mathbf{b} \in \mathbb{R}^K$。

### 6.2 Softmax 性质

| 性质 | 说明 |
|------|------|
| 输出归一化 | $\sum_k P(Y=k) = 1$ |
| 平移不变性 | $\text{softmax}(\mathbf{z} + c) = \text{softmax}(\mathbf{z})$（用于数值稳定） |
| $K=2$ 退化为 Sigmoid | $\text{softmax}(z_1, z_2)$ 中 $P(Y=1) = \sigma(z_1 - z_2)$ |

### 6.3 CE（Cross-Entropy，交叉熵）Loss

$$\mathcal{L}_{\text{CE}} = -\frac{1}{N}\sum_{i=1}^{N}\sum_{k=1}^{K}y_{ik}\log\hat{y}_{ik}$$

其中 $y_{ik}$ 是 one-hot 编码。当 $K=2$ 时退化为 BCE。

### 6.4 Softmax 梯度

对 logit $z_k$：

$$\frac{\partial \mathcal{L}}{\partial z_k} = \hat{y}_k - y_k$$

形式与二分类完全一致。矩阵形式：

$$\frac{\partial \mathcal{L}}{\partial \mathbf{W}} = \frac{1}{N}\mathbf{X}^T(\hat{\mathbf{Y}} - \mathbf{Y})$$

其中 $\hat{\mathbf{Y}}, \mathbf{Y} \in \mathbb{R}^{N \times K}$。

### 6.5 纯 Python Softmax 实现

```python
def softmax(z):
    """
    Numerically stable softmax.
    z: (N, K) logits
    Returns: (N, K) probabilities
    """
    z_shifted = z - np.max(z, axis=1, keepdims=True)  # Stability
    exp_z = np.exp(z_shifted)
    return exp_z / np.sum(exp_z, axis=1, keepdims=True)

def softmax_regression(X, y, K, lr=0.01, epochs=200, batch_size=32):
    """
    Softmax regression (multinomial logistic regression).
    X: (N, D), y: (N,) integer labels 0..K-1
    K: number of classes
    Returns: W (D, K), b (K,)
    """
    N, D = X.shape
    W = np.zeros((D, K))
    b = np.zeros(K)

    # One-hot encode y
    Y_onehot = np.zeros((N, K))
    Y_onehot[np.arange(N), y.astype(int)] = 1.0

    for epoch in range(epochs):
        indices = np.random.permutation(N)
        for start in range(0, N, batch_size):
            batch_idx = indices[start:start + batch_size]
            X_b = X[batch_idx]
            Y_b = Y_onehot[batch_idx]
            B = len(X_b)

            # Forward
            logits = X_b @ W + b               # (B, K)
            probs = softmax(logits)             # (B, K)

            # Gradient
            error = probs - Y_b                 # (B, K)
            grad_W = (1 / B) * (X_b.T @ error) # (D, K)
            grad_b = (1 / B) * np.sum(error, axis=0)  # (K,)

            W -= lr * grad_W
            b -= lr * grad_b

    return W, b
```

---

## 7. PyTorch 实现

### 7.1-7.3 PyTorch 实现（三种配置）

> **训练循环与 T1 Section 5.2 完全相同**。三种配置仅在 model/criterion/标签类型不同：

| 配置 | model | criterion | 标签类型 | 关键点 |
|------|-------|-----------|---------|--------|
| **Binary (手动)** | `w = torch.zeros(D, requires_grad=True)` | 手动 BCE | float | 用 `loss.backward()` + 手动 `w -= lr * w.grad` |
| **Binary (标准)** | `nn.Linear(D, 1)` | `BCEWithLogitsLoss()` | float | 无需手动 Sigmoid，数值更稳定 |
| **Multi-class** | `nn.Linear(D, K)` | `CrossEntropyLoss()` | long (int) | 输入为 raw logits，无需手动 Softmax |

```python
# --- Binary: nn.Linear + BCEWithLogitsLoss (推荐) ---
model = torch.nn.Linear(X.shape[1], 1)
optimizer = torch.optim.SGD(model.parameters(), lr=lr, weight_decay=weight_decay)
criterion = torch.nn.BCEWithLogitsLoss()  # Sigmoid+BCE合并，数值稳定

# --- Multi-class: nn.Linear + CrossEntropyLoss ---
model = torch.nn.Linear(X.shape[1], K)
optimizer = torch.optim.SGD(model.parameters(), lr=lr)
criterion = torch.nn.CrossEntropyLoss()   # LogSoftmax+NLLLoss合并
y_t = torch.tensor(y, dtype=torch.long)   # 注意：标签为整数
```

> **面试注意**：`BCEWithLogitsLoss` 将 Sigmoid 和 BCE 合并计算，利用 log-sum-exp 技巧避免数值溢出，比先 Sigmoid 再 BCE 更稳定。`CrossEntropyLoss` 同理。

### 7.4 sklearn 对比验证

```python
from sklearn.linear_model import LogisticRegression

# --- Verify our implementation against sklearn ---
np.random.seed(42)
X = np.random.randn(500, 2)
y = (X @ np.array([1.0, 2.0]) + 0.5 > 0).astype(float)

# sklearn (default: L2 regularization with C=1.0)
sk_model = LogisticRegression(max_iter=1000).fit(X, y)
print("sklearn weights:", sk_model.coef_.flatten(), "bias:", sk_model.intercept_[0])

# Our implementation
w_ours, b_ours, losses = logistic_regression(X, y, lr=0.1, epochs=500)
print("Our weights:", w_ours, "bias:", b_ours)

# PyTorch
w_pt, b_pt = train_logistic_pytorch(X, y, lr=0.1, epochs=500)
print("PyTorch weights:", w_pt, "bias:", b_pt)

# Accuracy comparison
y_sk = sk_model.predict(X)
y_ours = (sigmoid(X @ w_ours + b_ours) > 0.5).astype(float)
print(f"sklearn acc: {np.mean(y_sk == y):.4f}")
print(f"Ours acc:    {np.mean(y_ours == y):.4f}")
```

---

## 8. Logistic Regression 的凸性证明

### 8.1 为什么 BCE + Sigmoid 是凸的

对单个样本，BCE Loss 关于 $z = \mathbf{w}^T\mathbf{x} + b$ 的二阶导：

$$\frac{\partial^2 \mathcal{L}}{\partial z^2} = \hat{y}(1-\hat{y}) > 0 \quad \forall z$$

因此 $\mathcal{L}$ 对 $z$ 是严格凸的。

对 $\mathbf{w}$ 的 Hessian：

$$\mathbf{H} = \frac{1}{N}\mathbf{X}^T\mathbf{S}\mathbf{X}$$

其中 $\mathbf{S} = \text{diag}(\hat{y}_i(1-\hat{y}_i))$ 是对角矩阵，所有对角元素 > 0。因此 $\mathbf{H}$ 是 **PSD（Positive Semi-Definite，半正定）**，BCE Loss 对 $\mathbf{w}$ 是凸的。

> **面试注意**：凸性意味着 GD 可以找到全局最优。但加了正则化后仍是凸的（L2 正则化的 Hessian 为 $\mathbf{H} + \lambda\mathbf{I}$，仍是 PSD）。

---

## 10. 面试要点总结

### 必须掌握的推导

| 题目 | 关键结果 |
|------|---------|
| Sigmoid 导数 | $\sigma'(z) = \sigma(z)(1-\sigma(z))$ |
| BCE 从 MLE 推导 | NLL of Bernoulli → $-[y\log\hat{y}+(1-y)\log(1-\hat{y})]$ |
| BCE 对 $\mathbf{w}$ 的梯度（矩阵形式） | $\frac{1}{N}\mathbf{X}^T(\hat{\mathbf{y}} - \mathbf{y})$ |
| Softmax 梯度 | $\hat{y}_k - y_k$（形式一致） |
| Decision boundary | $\mathbf{w}^T\mathbf{x} + b = 0$（超平面） |

### 高频面试问题

- **为什么 Logistic Regression 输出是概率？**
  - 不只是 Sigmoid 映射到 (0,1)。是对 log-odds 做线性假设（Bernoulli 的 canonical link），满足概率公理，BCE 从 MLE 推导而来
- **推导 BCE Loss 并说明为什么不用 MSE？**
  - BCE = NLL of Bernoulli MLE。MSE + Sigmoid 非凸且梯度含 $\sigma'$ 项导致梯度消失，BCE + Sigmoid 凸且梯度简洁
- **手写 Logistic Regression 的梯度并实现 GD？**
  - 标量: $(\hat{y}-y)x$。矩阵: $\frac{1}{N}\mathbf{X}^T(\hat{\mathbf{y}}-\mathbf{y})$。实现见 Section 4.3
- **Decision boundary 是什么形状？**
  - 超平面 $\mathbf{w}^T\mathbf{x}+b=0$。Logistic Regression 是线性分类器。非线性 boundary 需要加特征变换或用 kernel
- **Logistic Regression 和 Linear Regression 数学上为什么是"同一模型"？**
  - GLM 框架：同一模型族，只改变分布假设（Gaussian→Bernoulli）和 link function（Identity→Logit）。梯度形式都是 $(\hat{y}-y)\mathbf{x}$
- **多分类怎么办？**
  - Softmax + Categorical CE（Multinomial Logistic Regression）。$K=2$ 时退化为 Sigmoid + BCE

### Follow-up 准备

- 过拟合怎么办？→ L1/L2 正则化（sklearn 的 `C` 参数 = $1/\lambda$），增加数据
- 特征需要标准化吗？→ 需要。GD 对特征尺度敏感，不同尺度导致等高线椭圆形，收敛慢
- 类别不平衡怎么办？→ 加权 BCE（`class_weight='balanced'`）、过采样（SMOTE）、阈值调整
- Logistic Regression 能处理非线性吗？→ 本身不行（线性 boundary），但可以加多项式特征 / kernel trick
- 和 SVM 的区别？→ LR 输出概率、优化 BCE（全局）；SVM 优化 hinge loss（只关注 boundary 附近的 support vectors）
- 和 Neural Network 的关系？→ 单层无隐藏层的 NN = Logistic Regression。加隐藏层后就能学非线性 boundary


---

# T4: KNN + K-Means 手写实现 + 理论

> 本节覆盖：KNN 距离度量（L1/L2/Cosine）、k 选择、KD-Tree 加速；K-Means Lloyd 算法、K-Means++ 初始化、4 种停止条件、纯 Python 实现。
> 合并来源：Doc 24 Section 8 (K-means 实现与停止条件), Framework Node 60 + 71

---

## Part I: KNN（K-Nearest Neighbors，K近邻）

---

## 1. 算法核心思想

KNN 是 **Lazy Learning（惰性学习）** 的代表：训练阶段不做任何计算，预测时直接查询训练集中距离最近的 $k$ 个样本。

**分类**：多数投票 (Majority Voting)

$$\hat{y} = \arg\max_c \sum_{i \in \mathcal{N}_k(x)} \mathbb{1}[y_i = c]$$

**回归**：均值

$$\hat{y} = \frac{1}{k}\sum_{i \in \mathcal{N}_k(x)} y_i$$

其中 $\mathcal{N}_k(x)$ 为距 $x$ 最近的 $k$ 个邻居的索引集合。

---

## 2. 距离度量（Distance Metrics）

### 2.1 L1 距离（Manhattan Distance，曼哈顿距离）

$$d_1(\mathbf{x}, \mathbf{z}) = \sum_{j=1}^{D} |x_j - z_j|$$

- 对每个维度的偏差线性累加
- 在高维空间中比 L2 更鲁棒（不会被单一维度上的大偏差主导）
- 适合稀疏数据

### 2.2 L2 距离（Euclidean Distance，欧氏距离）

$$d_2(\mathbf{x}, \mathbf{z}) = \sqrt{\sum_{j=1}^{D} (x_j - z_j)^2}$$

- 最常用的距离度量
- 受尺度影响大 → 必须 **Feature Scaling（特征缩放）**
- 实际计算中常用 $d_2^2$ 省去开方（单调性不变）

### 2.3 Cosine Distance（余弦距离）

$$d_{\cos}(\mathbf{x}, \mathbf{z}) = 1 - \frac{\mathbf{x} \cdot \mathbf{z}}{\|\mathbf{x}\|\|\mathbf{z}\|}$$

- 衡量方向相似性，忽略向量模长
- 适合 **NLP（Natural Language Processing，自然语言处理）** 中的文本向量、TF-IDF 特征
- $d_{\cos} \in [0, 2]$（非负特征时 $\in [0, 1]$）

### 2.4 Minkowski Distance（闵可夫斯基距离）

$$d_p(\mathbf{x}, \mathbf{z}) = \left(\sum_{j=1}^{D} |x_j - z_j|^p\right)^{1/p}$$

L1 和 L2 分别是 $p=1$ 和 $p=2$ 的特例。

### 2.5 距离度量选择对比

| 距离 | 优势 | 劣势 | 适用场景 |
|------|------|------|----------|
| L1 | 对 outlier 鲁棒，稀疏友好 | 不可微（$x_j = z_j$ 处） | 稀疏数据、推荐系统 |
| L2 | 几何直觉清晰，处处可微 | 高维退化、尺度敏感 | 低中维连续特征 |
| Cosine | 尺度不变 | 忽略幅度信息 | 文本相似度、嵌入向量 |

---

## 3. k 的选择

### 3.1 k 的影响

| k 值 | Bias | Variance | 效果 |
|------|------|----------|------|
| 小 k（如 1-3） | 低 | 高 | 决策边界复杂，易过拟合，对噪声敏感 |
| 大 k（如 N） | 高 | 低 | 决策边界平滑，趋向多数类，欠拟合 |

### 3.2 选择策略

1. **Cross-Validation（交叉验证）**：对 $k = 1, 3, 5, 7, \ldots$ 做 5-fold CV，选验证准确率最高的 k
2. **经验法则**：$k \approx \sqrt{N}$（$N$ 为样本量），取奇数避免平票
3. **Elbow Method（肘部法则）**：画 k vs 验证误差曲线，选拐点

### 3.3 加权 KNN（Weighted KNN）

对距离较近的邻居赋予更高权重：

$$w_i = \frac{1}{d(\mathbf{x}, \mathbf{x}_i) + \epsilon}$$

$$\hat{y} = \arg\max_c \sum_{i \in \mathcal{N}_k(x)} w_i \cdot \mathbb{1}[y_i = c]$$

其中 $\epsilon$ 防止除零。sklearn 中设置 `weights='distance'`。

---

## 4. KD-Tree 加速

### 4.1 暴力搜索的问题

暴力 KNN 时间复杂度 $O(ND)$（$N$ 个训练样本，$D$ 维），不适合大规模数据。

### 4.2 KD-Tree（K-Dimensional Tree，K维树）

一种二叉树空间索引结构，递归地按某一维度将空间划分为两半。

**构建过程**：
1. 选择方差最大的维度 $j$（或循环选维度）
2. 按该维度的中位数划分数据为左、右子树
3. 递归构建，直到节点包含 $\leq$ 1 个样本

**查询过程（找最近邻）**：
1. 从根节点递归向下，按划分维度进入左/右子树
2. 到达叶节点后，记录为当前最近邻
3. **回溯剪枝**：检查当前节点另一侧子树——如果查询点到划分超平面的距离 $\geq$ 当前最近距离，则可以剪掉整个子树

**复杂度**：

| 操作 | 平均 | 最坏 |
|------|------|------|
| 构建 | $O(N \log N)$ | $O(N \log N)$ |
| 查询 | $O(\log N)$ | $O(N)$（高维退化） |
| 空间 | $O(N)$ | $O(N)$ |

### 4.3 高维问题（Curse of Dimensionality）

当维度 $D$ 较大时（经验上 $D > 20$），KD-Tree 退化到暴力搜索。原因：

- 高维空间中所有点之间的距离趋于相等
- 剪枝失效，几乎每个分支都需要访问

**替代方案**：
- **Ball-Tree**：用超球体而非超平面划分，高维时比 KD-Tree 好
- **LSH（Locality-Sensitive Hashing，局部敏感哈希）**：近似最近邻，$O(1)$ 查询但有召回率损失
- **FAISS**：Facebook 开源的大规模向量检索库，支持 GPU 加速

---

## 5. 纯 Python 实现

```python
import numpy as np
from collections import Counter
from typing import Optional

class KNNClassifier:
    """K-Nearest Neighbors 分类器 — 纯 NumPy 实现。"""

    def __init__(self, k: int = 5, metric: str = 'l2',
                 weights: str = 'uniform'):
        """
        Args:
            k: 邻居数量
            metric: 距离度量 ('l1', 'l2', 'cosine')
            weights: 'uniform' 或 'distance'
        """
        self.k = k
        self.metric = metric
        self.weights = weights
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'KNNClassifier':
        """存储训练数据（惰性学习，无计算）。"""
        self.X_train = X.copy()
        self.y_train = y.copy()
        return self

    def _compute_distances(self, x: np.ndarray) -> np.ndarray:
        """计算单个查询点到所有训练样本的距离。"""
        if self.metric == 'l1':
            return np.sum(np.abs(self.X_train - x), axis=1)
        elif self.metric == 'l2':
            return np.sqrt(np.sum((self.X_train - x) ** 2, axis=1))
        elif self.metric == 'cosine':
            dot = self.X_train @ x
            norms = np.linalg.norm(self.X_train, axis=1) * np.linalg.norm(x)
            # 防止除零
            norms = np.maximum(norms, 1e-10)
            return 1.0 - dot / norms
        else:
            raise ValueError(f"Unknown metric: {self.metric}")

    def _predict_single(self, x: np.ndarray) -> int:
        """对单个样本预测类别。"""
        distances = self._compute_distances(x)
        # 找到 k 个最近邻的索引
        k_indices = np.argsort(distances)[:self.k]
        k_labels = self.y_train[k_indices]

        if self.weights == 'uniform':
            # 多数投票
            counter = Counter(k_labels.tolist())
            return counter.most_common(1)[0][0]
        else:
            # 距离加权投票
            k_dists = distances[k_indices]
            weights = 1.0 / (k_dists + 1e-10)
            class_weights: dict[int, float] = {}
            for label, w in zip(k_labels.tolist(), weights):
                class_weights[label] = class_weights.get(label, 0.0) + w
            return max(class_weights, key=class_weights.get)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """对多个样本预测。"""
        return np.array([self._predict_single(x) for x in X])

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """计算分类准确率。"""
        preds = self.predict(X)
        return np.mean(preds == y)


# --- 使用示例 ---
if __name__ == "__main__":
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    knn = KNNClassifier(k=5, metric='l2', weights='uniform')
    knn.fit(X_train, y_train)
    acc = knn.score(X_test, y_test)
    print(f"KNN accuracy: {acc:.4f}")  # 通常 > 0.95
```

### 5.1 简易 KD-Tree 实现

```python
import numpy as np
from typing import Optional, Tuple, List

class KDNode:
    """KD-Tree 节点。"""
    def __init__(self, point: np.ndarray, label: int,
                 split_dim: int, left: Optional['KDNode'] = None,
                 right: Optional['KDNode'] = None):
        self.point = point
        self.label = label
        self.split_dim = split_dim
        self.left = left
        self.right = right

class KDTree:
    """KD-Tree 最近邻搜索。"""

    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.root = self._build(X, y, depth=0)

    def _build(self, X: np.ndarray, y: np.ndarray,
               depth: int) -> Optional[KDNode]:
        if len(X) == 0:
            return None
        D = X.shape[1]
        # 按方差最大的维度划分（也可用 depth % D 循环）
        split_dim = depth % D
        sorted_idx = np.argsort(X[:, split_dim])
        mid = len(X) // 2
        return KDNode(
            point=X[sorted_idx[mid]],
            label=y[sorted_idx[mid]],
            split_dim=split_dim,
            left=self._build(X[sorted_idx[:mid]],
                             y[sorted_idx[:mid]], depth + 1),
            right=self._build(X[sorted_idx[mid + 1:]],
                              y[sorted_idx[mid + 1:]], depth + 1),
        )

    def query(self, x: np.ndarray,
              k: int = 1) -> List[Tuple[float, int]]:
        """返回 k 个最近邻的 (距离, 标签) 列表。"""
        import heapq
        # 最大堆（存负距离）保持 k 个最近的
        best: List[Tuple[float, int]] = []  # (-dist, label)

        def _search(node: Optional[KDNode]) -> None:
            if node is None:
                return
            dist = np.sqrt(np.sum((node.point - x) ** 2))
            # 更新堆
            if len(best) < k:
                heapq.heappush(best, (-dist, node.label))
            elif dist < -best[0][0]:
                heapq.heapreplace(best, (-dist, node.label))

            # 决定先搜索哪一侧
            diff = x[node.split_dim] - node.point[node.split_dim]
            close, far = (node.left, node.right) if diff <= 0 \
                else (node.right, node.left)
            _search(close)

            # 剪枝：如果到划分平面的距离 < 当前最远距离，需要搜索另一侧
            if len(best) < k or abs(diff) < -best[0][0]:
                _search(far)

        _search(self.root)
        return [(abs(d), lbl) for d, lbl in sorted(best, reverse=True)]
```

---

## 6. sklearn 验证

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
import numpy as np

X, y = load_iris(return_X_y=True)

# 不同 k 值的交叉验证
for k in [1, 3, 5, 7, 9]:
    clf = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    scores = cross_val_score(clf, X, y, cv=5)
    print(f"k={k}: accuracy={scores.mean():.4f} (+/- {scores.std():.4f})")

# 加权 KNN
clf_weighted = KNeighborsClassifier(n_neighbors=5, weights='distance')
scores = cross_val_score(clf_weighted, X, y, cv=5)
print(f"Weighted KNN: accuracy={scores.mean():.4f}")
```

---

## 7. KNN 面试要点总结

| 考点 | 关键回答 |
|------|----------|
| 时间复杂度 | 训练 $O(1)$，预测 $O(ND)$（暴力）或 $O(\log N)$（KD-Tree 低维） |
| 必须预处理 | **Feature Scaling**（StandardScaler / MinMaxScaler），否则大尺度特征主导距离 |
| k 怎么选 | Cross-validation，$k \approx \sqrt{N}$ 经验，取奇数 |
| 高维失效 | **Curse of Dimensionality（维度灾难）**，距离趋于相等 → 先降维（PCA） |
| vs Naive Bayes | KNN 非参数、无假设；NB 假设特征独立、训练快 |
| 优缺点 | 优：简单、无训练、非参数 / 缺：预测慢、内存大、高维差 |

---

## Part II: K-Means（K均值聚类）

---

## 8. 算法核心：Lloyd 算法

K-Means 最小化 **WCSS（Within-Cluster Sum of Squares，簇内平方和）**：

$$J = \sum_{k=1}^{K} \sum_{\mathbf{x}_i \in C_k} \|\mathbf{x}_i - \boldsymbol{\mu}_k\|^2$$

### 8.1 Lloyd 算法流程

1. **初始化**：选择 $K$ 个初始质心 $\boldsymbol{\mu}_1, \ldots, \boldsymbol{\mu}_K$
2. **E-step（Assignment，分配）**：将每个点分配到最近的质心
   $$c_i = \arg\min_k \|\mathbf{x}_i - \boldsymbol{\mu}_k\|^2$$
3. **M-step（Update，更新）**：重新计算每个簇的质心
   $$\boldsymbol{\mu}_k = \frac{1}{|C_k|}\sum_{\mathbf{x}_i \in C_k} \mathbf{x}_i$$
4. 重复步骤 2-3 直到收敛

### 8.2 为什么一定收敛？

- 每次 E-step 和 M-step 都不会增加目标函数 $J$
- E-step：固定 $\boldsymbol{\mu}$，每个点选最近质心 → $J$ 不增
- M-step：固定分配，均值是最小化 $\sum \|\mathbf{x}_i - \boldsymbol{\mu}\|^2$ 的解 → $J$ 不增
- $J \geq 0$ 有下界，单调不增 → 必定收敛
- **但只保证收敛到局部最优**，不保证全局最优

---

## 9. K-Means++ 初始化

随机初始化可能选到很近的点 → 收敛慢，容易陷入差的局部最优。

### 9.1 K-Means++ 算法

1. 随机选第一个质心 $\boldsymbol{\mu}_1$
2. 对每个数据点 $\mathbf{x}_i$，计算到已选质心的最短距离 $D(\mathbf{x}_i)$
3. 按概率 $P(\mathbf{x}_i) = \frac{D(\mathbf{x}_i)^2}{\sum_j D(\mathbf{x}_j)^2}$ 选下一个质心
4. 重复步骤 2-3 直到选够 $K$ 个质心

**直觉**：距离已有质心越远的点，被选为新质心的概率越高 → 初始质心分散在数据空间中。

**理论保证**：K-Means++ 的期望 WCSS 是最优解的 $O(\log K)$ 倍。

---

## 10. 停止条件（Stopping Criteria）

> **面试重点！** 必须列出至少 3 种停止条件。

| # | 条件 | 公式 | 说明 |
|---|------|------|------|
| 1 | Centroid 变化小于阈值 | $\max_k \|\boldsymbol{\mu}_k^{(t)} - \boldsymbol{\mu}_k^{(t-1)}\| < \epsilon$ | 最常用 |
| 2 | 达到最大迭代次数 | $t \geq T_{\max}$ | 安全阀，防止无限循环 |
| 3 | 样本分配不再变化 | $\forall i: c_i^{(t)} = c_i^{(t-1)}$ | 最严格的收敛条件 |
| 4 | **SSE（Sum of Squared Errors，误差平方和）** 变化小于阈值 | $|J^{(t)} - J^{(t-1)}| < \delta$ | 目标函数层面的判断 |

实际中**同时使用多个条件**（任一满足就停止）。

---

## 11. 纯 Python 实现（含 K-Means++）

> 合并自 Doc 24 Section 8，补充了完整的停止条件和空 cluster 处理。

```python
import numpy as np
from typing import Optional

class KMeans:
    """K-Means 聚类 — 纯 NumPy 实现，含 K-Means++ 和 4 种停止条件。"""

    def __init__(self, k: int, max_iters: int = 300,
                 tol: float = 1e-4, random_state: Optional[int] = None):
        """
        Args:
            k: 聚类数量
            max_iters: 最大迭代次数（停止条件 2）
            tol: centroid 变化阈值（停止条件 1）
            random_state: 随机种子
        """
        self.k = k
        self.max_iters = max_iters
        self.tol = tol
        self.rng = np.random.RandomState(random_state)
        self.centroids: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.inertia_: Optional[float] = None  # SSE

    def _init_centroids_pp(self, X: np.ndarray) -> np.ndarray:
        """K-Means++ 初始化。"""
        n = X.shape[0]
        centroids = [X[self.rng.randint(n)]]

        for _ in range(1, self.k):
            # 每个点到最近已选质心的距离平方
            dists = np.min([np.sum((X - c) ** 2, axis=1)
                            for c in centroids], axis=0)
            probs = dists / dists.sum()
            idx = self.rng.choice(n, p=probs)
            centroids.append(X[idx])

        return np.array(centroids)

    def _assign_clusters(self, X: np.ndarray) -> np.ndarray:
        """E-step: 将每个点分配到最近的质心。"""
        # distances shape: (n_samples, k)
        distances = np.array([
            np.sum((X - c) ** 2, axis=1) for c in self.centroids
        ]).T
        return np.argmin(distances, axis=1)

    def _update_centroids(self, X: np.ndarray,
                          labels: np.ndarray) -> np.ndarray:
        """M-step: 重新计算每个簇的质心。"""
        new_centroids = np.zeros_like(self.centroids)
        for j in range(self.k):
            members = X[labels == j]
            if len(members) > 0:
                new_centroids[j] = members.mean(axis=0)
            else:
                # 空 cluster 处理：随机重新初始化
                new_centroids[j] = X[self.rng.randint(X.shape[0])]
        return new_centroids

    def _compute_sse(self, X: np.ndarray,
                     labels: np.ndarray) -> float:
        """计算 SSE (inertia)。"""
        sse = 0.0
        for j in range(self.k):
            members = X[labels == j]
            if len(members) > 0:
                sse += np.sum((members - self.centroids[j]) ** 2)
        return sse

    def fit(self, X: np.ndarray) -> 'KMeans':
        """
        训练 K-Means 模型。

        4 种停止条件（任一满足即停止）:
        1. centroid 变化 < tol
        2. 达到 max_iters
        3. assignment 不变
        4. SSE 变化 < tol
        """
        self.centroids = self._init_centroids_pp(X)
        prev_labels = None
        prev_sse = float('inf')

        for t in range(self.max_iters):  # 停止条件 2
            # E-step
            self.labels = self._assign_clusters(X)

            # 停止条件 3: assignment 不变
            if prev_labels is not None and \
               np.array_equal(self.labels, prev_labels):
                break

            # M-step
            new_centroids = self._update_centroids(X, self.labels)

            # 停止条件 1: centroid 变化 < tol
            centroid_shift = np.max(
                np.sqrt(np.sum(
                    (new_centroids - self.centroids) ** 2, axis=1
                ))
            )
            self.centroids = new_centroids

            # 停止条件 4: SSE 变化 < tol
            current_sse = self._compute_sse(X, self.labels)
            sse_change = abs(prev_sse - current_sse)

            if centroid_shift < self.tol or sse_change < self.tol:
                break

            prev_labels = self.labels.copy()
            prev_sse = current_sse

        self.inertia_ = self._compute_sse(X, self.labels)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """对新数据预测 cluster assignment。"""
        return self._assign_clusters(X)


# --- 使用示例 ---
if __name__ == "__main__":
    np.random.seed(42)
    # 生成 3 个簇的合成数据
    X = np.vstack([
        np.random.randn(100, 2) + [2, 2],
        np.random.randn(100, 2) + [-2, -2],
        np.random.randn(100, 2) + [2, -2],
    ])

    km = KMeans(k=3, max_iters=100, tol=1e-4, random_state=42)
    km.fit(X)
    print(f"Final SSE: {km.inertia_:.2f}")
    print(f"Centroids:\n{km.centroids}")
```

---

## 12. 选择 K 的方法

### 12.1 Elbow Method（肘部法则）

对 $K = 1, 2, \ldots, K_{\max}$，计算 WCSS（inertia），画 K vs WCSS 曲线，选"拐点"处的 K。

```python
import numpy as np
import matplotlib.pyplot as plt

def elbow_method(X: np.ndarray, k_range: range) -> None:
    """画 Elbow 曲线帮助选择 K。"""
    inertias = []
    for k in k_range:
        km = KMeans(k=k, random_state=42)
        km.fit(X)
        inertias.append(km.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(list(k_range), inertias, 'bo-')
    plt.xlabel('K')
    plt.ylabel('WCSS (Inertia)')
    plt.title('Elbow Method')
    plt.grid(True)
    plt.show()
```

### 12.2 Silhouette Score（轮廓系数）

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

- $a(i)$：点 $i$ 到同簇所有其他点的平均距离（簇内紧密度）
- $b(i)$：点 $i$ 到最近其他簇所有点的平均距离（簇间分离度）
- $s(i) \in [-1, 1]$：越接近 1 越好

```python
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans as SKKMeans

best_k, best_score = 2, -1
for k in range(2, 10):
    km = SKKMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    score = silhouette_score(X, labels)
    print(f"K={k}: silhouette={score:.4f}")
    if score > best_score:
        best_k, best_score = k, score
print(f"Best K={best_k} (silhouette={best_score:.4f})")
```

### 12.3 Gap Statistic

比较真实数据的 WCSS 与在均匀分布参考数据上的 WCSS：

$$\text{Gap}(K) = \mathbb{E}[\log W_K^{\text{ref}}] - \log W_K$$

选择使 Gap 最大的 K。

---

## 13. K-Means 与 EM/GMM 的关系

| 特性 | K-Means | **GMM（Gaussian Mixture Model，高斯混合模型）** |
|------|---------|------|
| 分配方式 | **Hard assignment**（每个点只属于一个簇） | **Soft assignment**（概率属于多个簇） |
| 簇形状 | 球形（各向同性） | 椭圆形（任意协方差矩阵） |
| 优化算法 | Lloyd 迭代 | **EM（Expectation-Maximization，期望最大化）** |
| 关系 | K-Means 是 GMM 的特例 | 各分量等方差 + hard assignment = K-Means |

**数学联系**：GMM 中令所有高斯分量的协方差为 $\sigma^2 \mathbf{I}$，当 $\sigma \to 0$ 时，soft assignment 退化为 hard assignment，EM 退化为 Lloyd 算法。

---

## 14. sklearn 验证与对比

```python
from sklearn.cluster import KMeans as SKKMeans
from sklearn.datasets import make_blobs
import numpy as np

# 生成数据
X, y_true = make_blobs(n_samples=300, centers=3,
                        cluster_std=1.0, random_state=42)

# sklearn K-Means
sk_km = SKKMeans(n_clusters=3, init='k-means++',
                  n_init=10, random_state=42)
sk_labels = sk_km.fit_predict(X)
print(f"sklearn inertia: {sk_km.inertia_:.2f}")
print(f"sklearn centroids:\n{sk_km.cluster_centers_}")

# 自实现 K-Means
my_km = KMeans(k=3, random_state=42)
my_km.fit(X)
print(f"\nCustom inertia: {my_km.inertia_:.2f}")
print(f"Custom centroids:\n{my_km.centroids}")
```

---

## 15. K-Means 面试要点总结

| 考点 | 关键回答 |
|------|----------|
| 时间复杂度 | $O(NKdT)$：$N$ 样本, $K$ 簇, $d$ 维度, $T$ 迭代 |
| 停止条件 | **4 种**：centroid 变化、max iter、assignment 不变、SSE 变化 |
| 为什么收敛 | 每步 $J$ 不增 + $J \geq 0$ 有下界 → 单调有界必收敛 |
| 局部最优 | 多次随机初始化（`n_init`）或 K-Means++ |
| 选 K | Elbow Method、Silhouette Score、Gap Statistic |
| 空 cluster | 随机重新初始化或选离现有质心最远的点 |
| vs GMM | K-Means 是 GMM（等方差 + hard assignment）的特例 |
| 局限 | 只能找凸形/球形簇、对 outlier 敏感、需预设 K |
| 必须预处理 | **Feature Scaling**，否则大尺度特征主导距离 |

---

## 16. 面试高频 Follow-up

**Q: K-Means 对 outlier 敏感，怎么办？**
- 用 **K-Medoids**（PAM 算法）：用中位数点代替均值，对 outlier 更鲁棒
- 先做异常检测（如 IQR、DBSCAN）去除 outlier
- 用 Mini-Batch K-Means 减少单个 outlier 的影响

**Q: 非凸形簇怎么办？**
- **DBSCAN**：基于密度的聚类，能发现任意形状
- **Spectral Clustering（谱聚类）**：基于图拉普拉斯矩阵
- **HDBSCAN**：层次化 DBSCAN，不需要固定 $\epsilon$

**Q: 大规模数据怎么办？**
- **Mini-Batch K-Means**：每次迭代只用一小批数据更新质心，适合 $N > 100K$
- **FAISS**：Facebook 开源向量检索库，支持 GPU 加速的 K-Means
- **Bisecting K-Means**：递归二分，sklearn 1.1+ 支持


---

# T5: Naive Bayes 手写实现 + 理论

> 本节覆盖：贝叶斯定理→原始形式→Naive 形式完整推导，"Naive"假设的含义与合理性，Laplace Smoothing，Gaussian/Multinomial/Bernoulli 三大变体，纯 Python 实现，sklearn 验证。
> 全新内容，Framework Node 12

---

## 1. 贝叶斯定理基础（Bayes' Theorem）

---

### 1.1 原始贝叶斯定理

给定事件 $A$ 和 $B$，由条件概率定义：

$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

各项含义：

| 项 | 名称 | 含义 |
|----|------|------|
| $P(A\|B)$ | **Posterior（后验概率）** | 观测到 $B$ 后对 $A$ 的更新信念 |
| $P(B\|A)$ | **Likelihood（似然）** | 在 $A$ 成立时观测到 $B$ 的概率 |
| $P(A)$ | **Prior（先验概率）** | 观测 $B$ 之前对 $A$ 的信念 |
| $P(B)$ | **Evidence（证据）** | $B$ 的边缘概率，起归一化作用 |

**推导**：

$$P(A \cap B) = P(A|B) \cdot P(B) = P(B|A) \cdot P(A)$$

两边除以 $P(B)$ 即得贝叶斯定理。

### 1.2 分类问题中的贝叶斯定理

将 $A$ 替换为类别 $Y=c_k$，$B$ 替换为特征向量 $\mathbf{x} = (x_1, x_2, \ldots, x_D)$：

$$P(Y=c_k | \mathbf{x}) = \frac{P(\mathbf{x} | Y=c_k) \cdot P(Y=c_k)}{P(\mathbf{x})}$$

分类决策选后验最大的类：

$$\hat{y} = \arg\max_{c_k} P(Y=c_k | \mathbf{x})$$

由于 $P(\mathbf{x})$ 对所有类别相同，可省略：

$$\hat{y} = \arg\max_{c_k} P(\mathbf{x} | Y=c_k) \cdot P(Y=c_k)$$

**问题**：直接估计 $P(\mathbf{x} | Y=c_k) = P(x_1, x_2, \ldots, x_D | Y=c_k)$ 需要指数级样本——$D$ 个特征、每个有 $M$ 种取值时，需估计 $M^D$ 个联合概率。

---

## 2. 从原始形式到 Naive 形式

---

### 2.1 条件独立假设（Conditional Independence Assumption）

**Naive 假设**：给定类别 $Y$，所有特征之间条件独立：

$$P(x_1, x_2, \ldots, x_D | Y=c_k) = \prod_{d=1}^{D} P(x_d | Y=c_k)$$

### 2.2 Naive Bayes 分类器完整公式

将条件独立假设代入贝叶斯公式：

$$\hat{y} = \arg\max_{c_k} P(Y=c_k) \prod_{d=1}^{D} P(x_d | Y=c_k)$$

取对数避免浮点下溢（连乘极小的概率值）：

$$\hat{y} = \arg\max_{c_k} \left[\log P(Y=c_k) + \sum_{d=1}^{D} \log P(x_d | Y=c_k)\right]$$

### 2.3 参数复杂度对比

| 方法 | 需估计的参数数量 | 所需样本量 |
|------|-----------------|-----------|
| 完整联合分布 | $O(K \cdot M^D)$ | 指数级 |
| Naive Bayes | $O(K \cdot D \cdot M)$ | 线性级 |

其中 $K$ = 类别数，$D$ = 特征维度，$M$ = 每个特征的取值数。

### 2.4 为什么叫"Naive"

"Naive"指条件独立假设几乎在所有实际数据中都不成立。例如：

- 文本分类中，"machine" 和 "learning" 高度共现
- 医学诊断中，"发烧" 和 "咳嗽" 不独立

**为什么假设"错误"但模型仍然有效**：

1. **分类只需正确排序**：不需要精确概率值，只要最大后验类正确即可
2. **估计误差互相抵消**：跨特征的概率高估和低估部分对冲
3. **偏差-方差权衡**：独立假设引入偏差，但大幅降低方差。数据有限时，低方差模型更优
4. **"错而有用"**：George Box 名言——"All models are wrong, but some are useful"

---

## 3. 先验与似然的估计

---

### 3.1 类先验 $P(Y=c_k)$

通过训练集中的类别频率估计（**MLE（Maximum Likelihood Estimation，最大似然估计）**）：

$$P(Y=c_k) = \frac{N_k}{N}$$

其中 $N_k$ = 类别 $c_k$ 的样本数，$N$ = 总样本数。

### 3.2 类条件似然 $P(x_d | Y=c_k)$

估计方式取决于特征类型，对应 Naive Bayes 的三大变体（详见 Section 4-6）。

---

## 4. Laplace Smoothing（拉普拉斯平滑）

---

### 4.1 零概率问题

对离散特征，MLE 估计为：

$$P(x_d = v_j | Y=c_k) = \frac{\text{count}(x_d = v_j \text{ and } Y=c_k)}{N_k}$$

**致命缺陷**：如果某个特征值 $v_j$ 在类别 $c_k$ 的训练样本中从未出现，则 $P(x_d = v_j | Y=c_k) = 0$，整个连乘结果为零——一个"没见过"的特征值就否决了所有其他特征的证据。

### 4.2 加法平滑（Additive Smoothing）

引入平滑参数 $\alpha > 0$：

$$P(x_d = v_j | Y=c_k) = \frac{\text{count}(x_d = v_j, Y=c_k) + \alpha}{N_k + \alpha \cdot M_d}$$

其中 $M_d$ = 特征 $d$ 的取值总数。

类先验也做平滑：

$$P(Y=c_k) = \frac{N_k + \alpha}{N + \alpha \cdot K}$$

### 4.3 $\alpha$ 的含义

| $\alpha$ 值 | 名称 | 效果 |
|-------------|------|------|
| $\alpha = 0$ | 无平滑（MLE） | 有零概率风险 |
| $\alpha = 1$ | Laplace Smoothing | 等价于在每个计数上加 1（均匀先验） |
| $0 < \alpha < 1$ | Lidstone Smoothing | 比 Laplace 更温和 |
| $\alpha \to \infty$ | 过度平滑 | 所有概率趋向均匀分布 $1/M_d$ |

### 4.4 数学直觉

Laplace Smoothing 等价于对类条件分布加一个 **Dirichlet Prior（狄利克雷先验）**。$\alpha = 1$ 对应均匀 Dirichlet 先验——"在看到任何数据前，假设每个取值出现了 1 次"。

这是 **MAP（Maximum A Posteriori，最大后验估计）** 而非纯 MLE。

---

## 5. 三大变体

---

### 5.1 Multinomial Naive Bayes（多项式朴素贝叶斯）

**适用场景**：特征为离散计数值（词频、TF 值）

**似然模型**：每个类别的特征分布服从多项式分布：

$$P(\mathbf{x} | Y=c_k) \propto \prod_{d=1}^{D} \theta_{dk}^{x_d}$$

其中 $\theta_{dk} = P(\text{feature } d | Y=c_k)$，使用 Laplace Smoothing 估计：

$$\theta_{dk} = \frac{\sum_{i: y_i=c_k} x_{id} + \alpha}{\sum_{d'=1}^{D} \sum_{i: y_i=c_k} x_{id'} + \alpha \cdot D}$$

**典型应用**：文本分类（spam detection, sentiment analysis）中使用 **BoW（Bag of Words，词袋模型）** 或 **TF（Term Frequency，词频）** 特征。

### 5.2 Gaussian Naive Bayes（高斯朴素贝叶斯）

**适用场景**：特征为连续值

**似然模型**：假设每个特征在每个类别下服从高斯分布：

$$P(x_d | Y=c_k) = \frac{1}{\sqrt{2\pi\sigma_{dk}^2}} \exp\left(-\frac{(x_d - \mu_{dk})^2}{2\sigma_{dk}^2}\right)$$

参数估计：

$$\mu_{dk} = \frac{1}{N_k}\sum_{i: y_i=c_k} x_{id}$$

$$\sigma_{dk}^2 = \frac{1}{N_k}\sum_{i: y_i=c_k} (x_{id} - \mu_{dk})^2$$

**注意**：实践中常添加方差平滑项 $\epsilon$（如 sklearn 的 `var_smoothing=1e-9`），防止 $\sigma_{dk}^2 = 0$ 导致密度函数爆炸。

**局限性**：

- 假设每个特征单模态（Unimodal）对称分布
- 如果实际分布是双峰或偏态，效果会很差
- 对 **Outlier（离群值）** 敏感（高斯分布尾部衰减快）

### 5.3 Bernoulli Naive Bayes（伯努利朴素贝叶斯）

**适用场景**：特征为二值（0/1）

**似然模型**：

$$P(\mathbf{x} | Y=c_k) = \prod_{d=1}^{D} p_{dk}^{x_d} (1-p_{dk})^{1-x_d}$$

其中 $p_{dk} = P(x_d = 1 | Y=c_k)$，使用 Laplace Smoothing 估计：

$$p_{dk} = \frac{\text{count}(x_d = 1, Y=c_k) + \alpha}{N_k + 2\alpha}$$

**与 Multinomial 的关键区别**：

| 方面 | Multinomial NB | Bernoulli NB |
|------|---------------|-------------|
| 特征类型 | 词频/计数 | 是否出现（0/1） |
| 缺失特征处理 | 忽略 | 显式建模（$1 - p_{dk}$ 项） |
| 文本表示 | TF 向量 | 二值向量 |
| 长文本效果 | 更好 | 较差（忽略频率信息） |
| 短文本效果 | 一般 | 更好（"不出现"也是信号） |

> **面试要点**：Bernoulli NB 的核心优势是**显式建模特征的缺失**——$x_d = 0$ 时贡献 $\log(1-p_{dk})$，而 Multinomial NB 对 $x_d = 0$ 不计入。

### 5.4 三大变体选择指南

| 变体 | 特征类型 | 分布假设 | 典型应用 |
|------|---------|---------|---------|
| Gaussian NB | 连续数值 | 高斯分布 | 传感器数据、Iris 数据集 |
| Multinomial NB | 离散计数 | 多项式分布 | 文本分类（TF/TF-IDF） |
| Bernoulli NB | 二值 0/1 | 伯努利分布 | 短文本、二值特征 |

---

## 6. Naive Bayes 优缺点

---

### 6.1 优点

1. **训练极快**：只需扫描数据一遍计算频率/均值/方差，复杂度 $O(N \cdot D)$
2. **预测极快**：$O(D \cdot K)$——每个特征查表/计算 × 类别数
3. **小数据表现好**：参数少（$O(K \cdot D)$ 个），低方差，不容易过拟合
4. **天然处理多分类**：不需要 OvR/OvO 等策略
5. **增量学习（Online Learning）**：新数据到来只需更新计数/统计量
6. **抗无关特征**：无关特征对所有类别的似然贡献相近，不影响排序

### 6.2 缺点

1. **条件独立假设**：特征高度相关时性能下降
2. **概率校准差**：输出概率值往往过于极端（接近 0 或 1），需要 **Calibration（概率校准）**（如 Platt Scaling, Isotonic Regression）
3. **连续特征假设受限**：Gaussian NB 假设单模态，对复杂分布无能为力
4. **表达能力有限**：线性决策边界，无法捕获特征交互

### 6.3 Naive Bayes vs Logistic Regression（Generative vs Discriminative，生成式 vs 判别式）

| 方面 | Naive Bayes（生成式） | Logistic Regression（判别式） |
|------|---------------------|-------------------------------|
| 建模目标 | 联合分布 $P(\mathbf{x}, Y)$ via $P(\mathbf{x}\|Y) P(Y)$ | 条件分布 $P(Y\|\mathbf{x})$ |
| 独立性假设 | 必需 | 不需要 |
| 训练数据需求 | 少（利用先验结构） | 多（无分布假设） |
| 收敛速度 | 快速到达渐近线 | 渐近精度更高 |
| 概率校准 | 差（极端概率） | 好 |
| 缺失特征 | 自然处理（跳过缺失维度） | 需要插补 |
| **经验规律** | **$N < D$ 或数据极少时选 NB** | **$N$ 充足时选 LR** |

> **Ng & Jordan (2002)** 经典论文结论：在有限数据下 Naive Bayes 收敛更快，但 Logistic Regression 的渐近误差更低。交叉点通常在 $N \approx 10^3$ 附近。

---

## 7. 纯 Python 手写实现

---

### 7.1 Gaussian Naive Bayes from Scratch

```python
import numpy as np
from collections import defaultdict

class GaussianNBFromScratch:
    """Gaussian Naive Bayes classifier - from scratch."""

    def __init__(self, var_smoothing: float = 1e-9):
        self.var_smoothing = var_smoothing
        self.classes_ = None
        self.priors_ = {}       # P(Y=c_k)
        self.means_ = {}        # mu_{dk}
        self.variances_ = {}    # sigma_{dk}^2

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GaussianNBFromScratch":
        self.classes_ = np.unique(y)
        n_samples = len(y)

        for c in self.classes_:
            X_c = X[y == c]
            self.priors_[c] = len(X_c) / n_samples
            self.means_[c] = X_c.mean(axis=0)
            self.variances_[c] = X_c.var(axis=0) + self.var_smoothing

        return self

    def _log_likelihood(self, x: np.ndarray, c) -> float:
        """Compute log P(x | Y=c) assuming Gaussian per feature."""
        mu = self.means_[c]
        var = self.variances_[c]
        # log N(x; mu, var) = -0.5 * [log(2*pi*var) + (x-mu)^2/var]
        log_probs = -0.5 * (np.log(2 * np.pi * var) + (x - mu) ** 2 / var)
        return np.sum(log_probs)

    def predict(self, X: np.ndarray) -> np.ndarray:
        predictions = []
        for x in X:
            posteriors = {}
            for c in self.classes_:
                log_prior = np.log(self.priors_[c])
                log_lhood = self._log_likelihood(x, c)
                posteriors[c] = log_prior + log_lhood
            predictions.append(max(posteriors, key=posteriors.get))
        return np.array(predictions)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return calibrated posterior probabilities via log-sum-exp."""
        all_probs = []
        for x in X:
            log_posts = np.array([
                np.log(self.priors_[c]) + self._log_likelihood(x, c)
                for c in self.classes_
            ])
            # log-sum-exp trick for numerical stability
            max_lp = np.max(log_posts)
            log_sum = max_lp + np.log(np.sum(np.exp(log_posts - max_lp)))
            probs = np.exp(log_posts - log_sum)
            all_probs.append(probs)
        return np.array(all_probs)
```

### 7.2 Multinomial Naive Bayes from Scratch

```python
class MultinomialNBFromScratch:
    """Multinomial Naive Bayes with Laplace smoothing - from scratch."""

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.classes_ = None
        self.log_priors_ = {}
        self.log_likelihoods_ = {}  # log theta_{dk}

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MultinomialNBFromScratch":
        self.classes_ = np.unique(y)
        n_samples, n_features = X.shape

        for c in self.classes_:
            X_c = X[y == c]
            # Prior with Laplace smoothing
            self.log_priors_[c] = np.log(
                (len(X_c) + self.alpha) / (n_samples + self.alpha * len(self.classes_))
            )
            # Feature counts per class + smoothing
            feature_counts = X_c.sum(axis=0) + self.alpha
            total_count = feature_counts.sum()
            # theta_{dk} = (count_dk + alpha) / (sum_counts_k + alpha * D)
            self.log_likelihoods_[c] = np.log(feature_counts / total_count)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        predictions = []
        for x in X:
            posteriors = {}
            for c in self.classes_:
                # log P(Y=c) + sum_d x_d * log theta_{dk}
                posteriors[c] = self.log_priors_[c] + np.sum(x * self.log_likelihoods_[c])
            predictions.append(max(posteriors, key=posteriors.get))
        return np.array(predictions)
```

### 7.3 Bernoulli Naive Bayes from Scratch

```python
class BernoulliNBFromScratch:
    """Bernoulli Naive Bayes with Laplace smoothing - from scratch.

    Key difference from Multinomial: explicitly models feature ABSENCE.
    """

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.classes_ = None
        self.log_priors_ = {}
        self.log_p_ = {}       # log p_{dk}
        self.log_1_minus_p_ = {}  # log (1 - p_{dk})

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BernoulliNBFromScratch":
        self.classes_ = np.unique(y)
        n_samples, n_features = X.shape

        for c in self.classes_:
            X_c = X[y == c]
            n_c = len(X_c)
            self.log_priors_[c] = np.log(
                (n_c + self.alpha) / (n_samples + self.alpha * len(self.classes_))
            )
            # p_{dk} = (count(x_d=1, Y=c) + alpha) / (N_c + 2*alpha)
            p = (X_c.sum(axis=0) + self.alpha) / (n_c + 2 * self.alpha)
            self.log_p_[c] = np.log(p)
            self.log_1_minus_p_[c] = np.log(1 - p)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        predictions = []
        for x in X:
            posteriors = {}
            for c in self.classes_:
                # log P(Y=c) + sum_d [x_d * log p_dk + (1 - x_d) * log(1 - p_dk)]
                log_post = self.log_priors_[c] + np.sum(
                    x * self.log_p_[c] + (1 - x) * self.log_1_minus_p_[c]
                )
                posteriors[c] = log_post
            predictions.append(max(posteriors, key=posteriors.get))
        return np.array(predictions)
```

---

## 8. sklearn 验证

---

> 所有三种 NB 变体使用相同的验证模式：from-scratch vs sklearn accuracy 对比。

```python
from sklearn.datasets import load_iris, fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB as SklearnMNB, BernoulliNB as SklearnBNB
from sklearn.metrics import accuracy_score

# === Gaussian NB (Iris dataset, continuous features) ===
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

gnb = GaussianNBFromScratch(var_smoothing=1e-9)
gnb.fit(X_train, y_train)
print(f"Gaussian NB - scratch: {accuracy_score(y_test, gnb.predict(X_test)):.4f}")
print(f"Gaussian NB - sklearn: {accuracy_score(y_test, GaussianNB(var_smoothing=1e-9).fit(X_train, y_train).predict(X_test)):.4f}")

# === Multinomial NB (20newsgroups, word count features) ===
cats = ['sci.space', 'rec.sport.baseball']
train_data = fetch_20newsgroups(subset='train', categories=cats, random_state=42)
test_data = fetch_20newsgroups(subset='test', categories=cats, random_state=42)
vec = CountVectorizer(max_features=5000)
X_tr = vec.fit_transform(train_data.data).toarray()
X_te = vec.transform(test_data.data).toarray()

mnb = MultinomialNBFromScratch(alpha=1.0)
mnb.fit(X_tr, train_data.target)
print(f"Multinomial NB - scratch: {accuracy_score(test_data.target, mnb.predict(X_te)):.4f}")
print(f"Multinomial NB - sklearn: {accuracy_score(test_data.target, SklearnMNB(alpha=1.0).fit(X_tr, train_data.target).predict(X_te)):.4f}")

# === Bernoulli NB (binarized text features) ===
X_tr_bin, X_te_bin = (X_tr > 0).astype(int), (X_te > 0).astype(int)
bnb = BernoulliNBFromScratch(alpha=1.0)
bnb.fit(X_tr_bin, train_data.target)
print(f"Bernoulli NB - scratch: {accuracy_score(test_data.target, bnb.predict(X_te_bin)):.4f}")
print(f"Bernoulli NB - sklearn: {accuracy_score(test_data.target, SklearnBNB(alpha=1.0).fit(X_tr_bin, train_data.target).predict(X_te_bin)):.4f}")
```

---

## 9. Log-Sum-Exp 技巧

---

在实现 `predict_proba` 时，需要将 log 后验转换回概率并归一化。直接 `exp()` 会上溢/下溢。

**Log-Sum-Exp Trick**：

$$\log\sum_k e^{a_k} = a_{\max} + \log\sum_k e^{a_k - a_{\max}}$$

```python
def log_sum_exp(log_values: np.ndarray) -> float:
    """Numerically stable log-sum-exp."""
    a_max = np.max(log_values)
    return a_max + np.log(np.sum(np.exp(log_values - a_max)))

# Usage: convert log posteriors to probabilities
log_posteriors = np.array([log_p_c1, log_p_c2, log_p_c3])
log_norm = log_sum_exp(log_posteriors)
probs = np.exp(log_posteriors - log_norm)  # sums to 1.0
```

---

## 10. 面试高频问题

---

### Q1: 为什么 Naive Bayes 在特征不独立时仍然有效？

分类只需后验概率的**排序**正确，不需要精确值。即使独立假设导致概率估计有偏差，只要 $\arg\max$ 不变，分类就正确。Domingos & Pazzani (1997) 的经典论文形式化了这一观察。

### Q2: Naive Bayes 的决策边界是什么形状？

**线性决策边界**。取两个类的 log 后验之差：

$$\log\frac{P(Y=c_1|\mathbf{x})}{P(Y=c_2|\mathbf{x})} = \underbrace{\log\frac{P(Y=c_1)}{P(Y=c_2)}}_{\text{bias}} + \sum_{d=1}^{D}\underbrace{\left[\log P(x_d|c_1) - \log P(x_d|c_2)\right]}_{\text{per-feature contribution}}$$

对 Gaussian NB，展开高斯 log 密度后是 $x_d$ 的线性函数（当方差相等时）或二次函数（方差不等时）。

### Q3: 什么时候用 Naive Bayes 而不是更复杂的模型？

- 训练数据极少（$N < 100$），复杂模型会过拟合
- 特征维度极高（$D \gg N$），如文本分类中词表可达 $10^5$
- 需要实时预测的在线系统
- 作为 **Baseline（基线模型）**——如果 NB 就够好，不需要更复杂的模型

### Q4: Laplace Smoothing 的 $\alpha$ 如何选择？

通过 **Cross-Validation（交叉验证）** 在 $\{0.01, 0.1, 0.5, 1.0, 2.0, 5.0\}$ 等候选值中选择。$\alpha$ 过小无法有效防止零概率，$\alpha$ 过大则所有概率趋向均匀分布（信息被抹平）。

### Q5: 如何处理连续特征不服从高斯分布的情况？

1. **离散化（Discretization/Binning）**：将连续值分桶后用 Multinomial NB
2. **非参数密度估计**：用 **KDE（Kernel Density Estimation，核密度估计）** 替代高斯假设
3. **换模型**：使用不依赖分布假设的判别式模型（LR, SVM, 树模型）

---

## 11. 实际应用场景

---

| 应用场景 | 推荐变体 | 原因 |
|---------|---------|------|
| 垃圾邮件过滤 | Multinomial NB | 词频特征，高维稀疏，训练快 |
| 情感分析 | Multinomial/Bernoulli NB | 文本分类任务 |
| 医疗诊断 | Gaussian NB | 检查指标为连续值 |
| 推荐系统中的冷启动 | 任意 NB | 数据极少时 NB 优于协同过滤 |
| 实时分类系统 | 任意 NB | $O(DK)$ 预测速度极快 |
| 多标签分类 | Binary Relevance + Bernoulli NB | 每个标签独立二分类 |

---

## 12. 总结对比表

---

| 方面 | Gaussian NB | Multinomial NB | Bernoulli NB |
|------|-----------|----------------|-------------|
| 特征类型 | 连续 | 离散计数 | 二值 0/1 |
| 分布假设 | $\mathcal{N}(\mu, \sigma^2)$ | 多项式 | 伯努利 |
| 平滑方式 | 方差 $+\epsilon$ | Laplace ($\alpha$) | Laplace ($\alpha$) |
| 建模缺失特征 | N/A | 忽略 | 显式建模 |
| 参数估计 | 均值 + 方差 | 词频 + 平滑 | 出现概率 + 平滑 |
| 训练复杂度 | $O(ND)$ | $O(ND)$ | $O(ND)$ |
| 预测复杂度 | $O(DK)$ | $O(DK)$ | $O(DK)$ |
| 最佳场景 | 传感器数据 | 长文本 TF | 短文本二值 |


---

# T6: Tree Models 手写实现 + 理论

> 本节覆盖：Decision Tree 三大算法（ID3/C4.5/CART）对比与分裂准则计算，Pruning（Pre/Post/CCP），Random Forest 原理与 Variance 推导，AdaBoost 权重完整推导，GBDT 残差拟合 + Shrinkage，纯 Python 实现，sklearn 验证。
> 合并来源：Doc 24 Section 5-6, Framework Node 65

---

## 1. Decision Tree 基础

---

### 1.1 核心思想

Decision Tree 通过递归地将特征空间分割为矩形区域，在每个区域内做出预测：

- **分类树（Classification Tree）**：叶节点输出多数类标签或类别概率分布
- **回归树（Regression Tree）**：叶节点输出该区域内样本目标值的均值

**关键问题**：每次分裂时，如何选择最优特征和分裂点？

### 1.2 不纯度度量（Impurity Measures）

设节点 $t$ 中类别 $k$ 的比例为 $p_k$，共 $K$ 个类别。

**信息熵（Entropy）**：

$$H(t) = -\sum_{k=1}^{K} p_k \log_2 p_k$$

- 范围 $[0, \log_2 K]$，纯节点 $H = 0$
- 二分类时 $H = -p\log_2 p - (1-p)\log_2(1-p)$，在 $p=0.5$ 时最大

**基尼不纯度（Gini Impurity）**：

$$\text{Gini}(t) = 1 - \sum_{k=1}^{K} p_k^2 = \sum_{k \neq k'} p_k p_{k'}$$

- 范围 $[0, 1 - 1/K]$，纯节点 $\text{Gini} = 0$
- 物理含义：从节点中随机抽取两个样本，类别不同的概率
- 二分类时 $\text{Gini} = 2p(1-p)$，在 $p=0.5$ 时最大

**分类误差率（Classification Error）**：

$$\text{Error}(t) = 1 - \max_k p_k$$

- 仅用于剪枝评估，不用于分裂——对概率变化不敏感，无法区分分裂质量

### 1.3 计算示例

节点有 10 个样本：6 个正类，4 个负类（$p_+ = 0.6, p_- = 0.4$）：

$$H = -0.6\log_2 0.6 - 0.4\log_2 0.4 = 0.442 + 0.529 = 0.971 \text{ bits}$$

$$\text{Gini} = 1 - (0.6^2 + 0.4^2) = 1 - 0.52 = 0.48$$

$$\text{Error} = 1 - 0.6 = 0.4$$

---

## 2. ID3 / C4.5 / CART 三大算法对比

---

### 2.1 ID3（Iterative Dichotomiser 3，Quinlan 1986）

**分裂准则**：**Information Gain（信息增益）**

$$\text{IG}(D, A) = H(D) - \sum_{v \in \text{Values}(A)} \frac{|D_v|}{|D|} H(D_v)$$

其中 $D$ 是当前数据集，$A$ 是候选特征，$D_v$ 是特征 $A$ 取值为 $v$ 的子集。

**缺陷**：偏好取值多的特征。极端例子：用"ID"做分裂，每个子节点只有一个样本，$H(D_v)=0$，信息增益最大——但完全没有泛化能力。

**局限性**：
- 只能处理离散特征
- 不支持缺失值
- 没有剪枝机制
- 偏好多值特征

### 2.2 C4.5（Quinlan 1993）

**分裂准则**：**Information Gain Ratio（信息增益率）**

$$\text{GainRatio}(D, A) = \frac{\text{IG}(D, A)}{\text{SplitInfo}(D, A)}$$

其中分裂信息量（Split Information）：

$$\text{SplitInfo}(D, A) = -\sum_{v \in \text{Values}(A)} \frac{|D_v|}{|D|} \log_2 \frac{|D_v|}{|D|}$$

**直觉**：SplitInfo 是特征 $A$ 取值分布的熵。取值越多、分布越均匀，SplitInfo 越大，从而惩罚多值特征。

**注意**：C4.5 不直接选 GainRatio 最大的特征，而是先选 IG 高于均值的特征子集，再在其中选 GainRatio 最高的——避免 SplitInfo 极大导致 GainRatio 极小的陷阱。

**相对 ID3 的改进**：
- 支持连续特征（排序后二分查找最优阈值）
- 支持缺失值处理（按比例分配到各子节点）
- 引入剪枝（Pessimistic Error Pruning）
- 用 Gain Ratio 修正多值偏好

### 2.3 CART（Classification and Regression Trees，Breiman 1984）

**分裂准则**：
- 分类：**Gini Impurity** 的加权减少
- 回归：**MSE（Mean Squared Error）** / 方差的加权减少

$$\Delta\text{Gini}(D, A, s) = \text{Gini}(D) - \frac{|D_L|}{|D|}\text{Gini}(D_L) - \frac{|D_R|}{|D|}\text{Gini}(D_R)$$

$$\Delta\text{MSE}(D, A, s) = \text{MSE}(D) - \frac{|D_L|}{|D|}\text{MSE}(D_L) - \frac{|D_R|}{|D|}\text{MSE}(D_R)$$

其中 $s$ 是分裂阈值，$D_L, D_R$ 是左右子集。

**CART 的核心特征**：
- **永远是二叉树**（Binary Tree）：每次只分裂为两个子节点
- 离散特征也做二分（$\{v_1, v_3\}$ vs $\{v_2, v_4, v_5\}$）
- ID3/C4.5 是多叉树（每个取值一个分支）

**回归树分裂**：对连续目标值，遍历每个特征的每个切分点 $s$，选择使左右子节点 MSE 之和最小的 $(A, s)$：

$$\min_{A, s} \left[\min_{c_L} \sum_{x_i \in D_L} (y_i - c_L)^2 + \min_{c_R} \sum_{x_i \in D_R} (y_i - c_R)^2\right]$$

其中 $c_L = \text{mean}(y_i : x_i \in D_L)$，$c_R = \text{mean}(y_i : x_i \in D_R)$。

### 2.4 三大算法对比总表

| 方面 | ID3 | C4.5 | CART |
|------|-----|------|------|
| 年份 | 1986 | 1993 | 1984 |
| 分裂准则 | Information Gain | Gain Ratio | Gini (分类) / MSE (回归) |
| 树结构 | 多叉树 | 多叉树 | **二叉树** |
| 特征类型 | 仅离散 | 离散 + 连续 | 离散 + 连续 |
| 缺失值处理 | 不支持 | 支持（按比例分配） | 支持（代理分裂） |
| 剪枝 | 无 | Pessimistic Error Pruning | **CCP（Cost Complexity Pruning）** |
| 回归能力 | 无 | 无 | 支持 |
| sklearn 实现 | 无 | 无 | `DecisionTreeClassifier` / `Regressor` |

> **面试要点**：sklearn 的 `DecisionTreeClassifier` 使用的是 **CART** 算法，默认 `criterion='gini'`，也支持 `'entropy'`（此时用信息增益，不是增益率）。sklearn 不实现 ID3 或 C4.5。

### 2.5 分裂准则完整计算示例

训练数据：14 个样本，特征"天气"有 3 个取值（晴/阴/雨），目标"是否打网球"。

| 天气 | 打球=Yes | 打球=No | 合计 |
|------|---------|---------|------|
| 晴 | 2 | 3 | 5 |
| 阴 | 4 | 0 | 4 |
| 雨 | 3 | 2 | 5 |
| **合计** | **9** | **5** | **14** |

**Step 1: 父节点熵**

$$H(D) = -\frac{9}{14}\log_2\frac{9}{14} - \frac{5}{14}\log_2\frac{5}{14} = 0.940$$

**Step 2: 各子节点熵**

$$H(D_\text{晴}) = -\frac{2}{5}\log_2\frac{2}{5} - \frac{3}{5}\log_2\frac{3}{5} = 0.971$$

$$H(D_\text{阴}) = -\frac{4}{4}\log_2\frac{4}{4} - \frac{0}{4}\log_2\frac{0}{4} = 0$$

$$H(D_\text{雨}) = -\frac{3}{5}\log_2\frac{3}{5} - \frac{2}{5}\log_2\frac{2}{5} = 0.971$$

**Step 3: Information Gain (ID3)**

$$\text{IG} = 0.940 - \frac{5}{14}(0.971) - \frac{4}{14}(0) - \frac{5}{14}(0.971) = 0.940 - 0.693 = 0.247$$

**Step 4: Gain Ratio (C4.5)**

$$\text{SplitInfo} = -\frac{5}{14}\log_2\frac{5}{14} - \frac{4}{14}\log_2\frac{4}{14} - \frac{5}{14}\log_2\frac{5}{14} = 1.577$$

$$\text{GainRatio} = \frac{0.247}{1.577} = 0.157$$

**Step 5: Gini (CART) — 二分法**

CART 对 3 值特征做二分，需要尝试所有可能的二分方式：

$\{$晴$\}$ vs $\{$阴, 雨$\}$: $\text{Gini}_L = 2 \cdot \frac{2}{5} \cdot \frac{3}{5} = 0.48$, $\text{Gini}_R = 1 - (\frac{7}{9})^2 - (\frac{2}{9})^2 = 0.346$

$$\Delta\text{Gini} = 0.459 - \frac{5}{14}(0.48) - \frac{9}{14}(0.346) = 0.459 - 0.171 - 0.222 = 0.066$$

（其中父节点 $\text{Gini}(D) = 2 \cdot \frac{9}{14} \cdot \frac{5}{14} = 0.459$）

---

## 3. Pruning（剪枝）

---

### 3.1 为什么需要剪枝

完全生长的 Decision Tree 会完美拟合训练数据（training error = 0），但泛化能力差——经典的 **Overfitting（过拟合）** 问题：

- 每个叶节点只有 1 个样本 → 记住了每个训练点包括噪声
- 高 Variance，低 Bias

### 3.2 Pre-Pruning（预剪枝）

在树生长过程中提前停止分裂。通过超参数控制：

| 参数 | sklearn 名称 | 作用 |
|------|-------------|------|
| 最大深度 | `max_depth` | 限制树的层数 |
| 叶节点最少样本 | `min_samples_leaf` | 叶节点至少包含 N 个样本 |
| 分裂最少样本 | `min_samples_split` | 节点样本数 < N 时停止分裂 |
| 最大叶节点数 | `max_leaf_nodes` | 限制叶节点总数 |
| 最小不纯度减少 | `min_impurity_decrease` | 分裂带来的不纯度减少 < 阈值时停止 |

**优点**：简单高效，减少训练时间
**缺点**：可能过早停止（欠拟合），因为当前分裂不显著 ≠ 后续分裂无价值

### 3.3 Post-Pruning（后剪枝）

先让树充分生长，再从底部向上剪去不必要的子树。

**基本思想**：如果一棵子树被替换为叶节点后，验证集上的误差不增加（或增加在可接受范围内），则剪掉。

### 3.4 CCP（Cost Complexity Pruning / Minimal Cost-Complexity Pruning）

CART 使用的后剪枝方法，也是 sklearn 实现的方法（`ccp_alpha` 参数）。

**目标函数**：

$$R_\alpha(T) = R(T) + \alpha \cdot |T|$$

其中：
- $R(T)$ = 树 $T$ 的训练误差（分类用误分类率，回归用 MSE）
- $|T|$ = 树 $T$ 的叶节点数（复杂度度量）
- $\alpha \geq 0$ = 正则化参数（penalty per leaf）

**算法流程**：

1. 从完全生长的树 $T_0$ 开始
2. 对树中每个内部节点 $t$，计算"有效 $\alpha$"：

$$\alpha_{\text{eff}}(t) = \frac{R(t) - R(T_t)}{|T_t| - 1}$$

其中 $R(t)$ = 将 $t$ 替换为叶节点的误差，$R(T_t)$ = 以 $t$ 为根的子树的误差，$|T_t|$ = 子树叶节点数。

3. 剪掉 $\alpha_{\text{eff}}$ 最小的内部节点（它的子树"性价比最低"）
4. 得到一系列嵌套子树 $T_0 \supset T_1 \supset \cdots \supset T_{\text{root}}$
5. 用交叉验证选择最优 $\alpha$（即最优子树）

**直觉**：$\alpha$ 越大，惩罚越重，树越简单。$\alpha = 0$ 保留完整树，$\alpha \to \infty$ 只剩根节点。

```python
# sklearn CCP 示例
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
import numpy as np

X, y = load_iris(return_X_y=True)

# Step 1: 获取有效 alpha 序列
clf = DecisionTreeClassifier(random_state=42)
clf.fit(X, y)
path = clf.cost_complexity_pruning_path(X, y)
ccp_alphas = path.ccp_alphas

# Step 2: 对每个 alpha 交叉验证
scores = []
for alpha in ccp_alphas:
    tree = DecisionTreeClassifier(ccp_alpha=alpha, random_state=42)
    cv_score = cross_val_score(tree, X, y, cv=5, scoring='accuracy')
    scores.append(cv_score.mean())

# Step 3: 选择最优 alpha
best_alpha = ccp_alphas[np.argmax(scores)]
print(f"Best ccp_alpha: {best_alpha:.4f}")
print(f"Best CV accuracy: {max(scores):.4f}")

# Step 4: 用最优 alpha 训练最终模型
final_tree = DecisionTreeClassifier(ccp_alpha=best_alpha, random_state=42)
final_tree.fit(X, y)
print(f"Number of leaves: {final_tree.get_n_leaves()}")
print(f"Tree depth: {final_tree.get_depth()}")
```

### 3.5 Pre-Pruning vs Post-Pruning 对比

| 方面 | Pre-Pruning | Post-Pruning (CCP) |
|------|------------|-------------------|
| 时机 | 生长时 | 生长后 |
| 风险 | 过早停止（欠拟合） | 计算成本更高 |
| 调参 | 多个超参数组合 | 单一 $\alpha$ 参数 |
| 效果 | 可能错过深层有价值分裂 | 更全面评估 |
| sklearn | `max_depth`, `min_samples_*` | `ccp_alpha` |

> **面试要点**：实践中常 **组合使用**——用 Pre-Pruning 设置合理上限（如 `max_depth=20`），再用 CCP 精细调节。

---

## 4. Decision Tree 纯 Python 实现

---

### 4.1 CART 分类树 from Scratch

```python
import numpy as np
from collections import Counter

class TreeNode:
    """A node in the decision tree."""

    def __init__(self, feature_idx=None, threshold=None,
                 left=None, right=None, value=None):
        self.feature_idx = feature_idx  # split feature index
        self.threshold = threshold      # split threshold
        self.left = left                # left subtree (<=)
        self.right = right              # right subtree (>)
        self.value = value              # leaf prediction (class label)


class DecisionTreeFromScratch:
    """CART decision tree classifier using Gini impurity - from scratch."""

    def __init__(self, max_depth=None, min_samples_split=2,
                 min_samples_leaf=1):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.root = None

    def _gini(self, y: np.ndarray) -> float:
        """Compute Gini impurity."""
        counts = np.bincount(y)
        probs = counts / len(y)
        return 1.0 - np.sum(probs ** 2)

    def _best_split(self, X: np.ndarray, y: np.ndarray):
        """Find best (feature, threshold) by maximizing Gini decrease."""
        n_samples, n_features = X.shape
        best_gain = -1.0
        best_feat, best_thresh = None, None

        parent_gini = self._gini(y)

        for feat_idx in range(n_features):
            thresholds = np.unique(X[:, feat_idx])
            for thresh in thresholds:
                left_mask = X[:, feat_idx] <= thresh
                right_mask = ~left_mask
                n_left = left_mask.sum()
                n_right = right_mask.sum()

                if n_left < self.min_samples_leaf or \
                   n_right < self.min_samples_leaf:
                    continue

                gini_left = self._gini(y[left_mask])
                gini_right = self._gini(y[right_mask])
                weighted_gini = (n_left * gini_left +
                                 n_right * gini_right) / n_samples
                gain = parent_gini - weighted_gini

                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat_idx
                    best_thresh = thresh

        return best_feat, best_thresh, best_gain

    def _build_tree(self, X: np.ndarray, y: np.ndarray,
                    depth: int) -> TreeNode:
        """Recursively build the tree."""
        n_samples = len(y)

        # Stopping conditions
        if (self.max_depth is not None and depth >= self.max_depth) or \
           n_samples < self.min_samples_split or \
           len(np.unique(y)) == 1:
            leaf_value = Counter(y).most_common(1)[0][0]
            return TreeNode(value=leaf_value)

        feat_idx, thresh, gain = self._best_split(X, y)

        if gain <= 0 or feat_idx is None:
            leaf_value = Counter(y).most_common(1)[0][0]
            return TreeNode(value=leaf_value)

        left_mask = X[:, feat_idx] <= thresh
        left = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right = self._build_tree(X[~left_mask], y[~left_mask], depth + 1)

        return TreeNode(feature_idx=feat_idx, threshold=thresh,
                        left=left, right=right)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DecisionTreeFromScratch":
        self.root = self._build_tree(X, y, depth=0)
        return self

    def _predict_one(self, x: np.ndarray, node: TreeNode) -> int:
        """Traverse tree for single sample."""
        if node.value is not None:
            return node.value
        if x[node.feature_idx] <= node.threshold:
            return self._predict_one(x, node.left)
        return self._predict_one(x, node.right)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self._predict_one(x, self.root) for x in X])
```

### 4.2 sklearn 验证

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

dt_scratch = DecisionTreeFromScratch(max_depth=5)
dt_scratch.fit(X_train, y_train)
dt_sklearn = DecisionTreeClassifier(max_depth=5, random_state=42).fit(X_train, y_train)

print(f"Scratch: {accuracy_score(y_test, dt_scratch.predict(X_test)):.4f}")
print(f"sklearn: {accuracy_score(y_test, dt_sklearn.predict(X_test)):.4f}")
```

---

## 5. Random Forest

---

### 5.1 核心原理

Random Forest = **Bagging（Bootstrap Aggregating）** + **Feature Subsampling** + **Decision Trees**

1. **Bootstrap Sampling**：从 $N$ 个训练样本中有放回采样 $N$ 个，构建 $T$ 棵树
2. **Feature Subsampling**：每次分裂时，从 $D$ 个特征中随机选 $m$ 个候选特征
   - 分类：$m = \sqrt{D}$（sklearn 默认）
   - 回归：$m = D/3$
3. **聚合（Aggregation）**：
   - 分类：投票（Majority Vote）
   - 回归：平均（Mean）

### 5.2 Variance 推导——为什么 Random Forest 有效

单棵深度 Decision Tree：高 Variance，低 Bias。

设 $T$ 棵树的预测分别为 $Z_1, Z_2, \ldots, Z_T$，每棵树的方差为 $\sigma^2$，任意两棵树之间的相关系数为 $\rho$。

聚合预测 $\bar{Z} = \frac{1}{T}\sum_{i=1}^{T} Z_i$。

$$\text{Var}(\bar{Z}) = \text{Var}\left(\frac{1}{T}\sum_{i=1}^{T} Z_i\right)$$

展开协方差：

$$= \frac{1}{T^2}\left[\sum_{i=1}^{T}\text{Var}(Z_i) + \sum_{i \neq j}\text{Cov}(Z_i, Z_j)\right]$$

$$= \frac{1}{T^2}\left[T\sigma^2 + T(T-1)\rho\sigma^2\right]$$

$$= \frac{\sigma^2}{T} + \frac{T-1}{T}\rho\sigma^2$$

当 $T$ 足够大时：

$$\text{Var}(\bar{Z}) \approx \rho\sigma^2 + \frac{(1-\rho)\sigma^2}{T}$$

**两个降低 Variance 的机制**：

| 机制 | 作用 | 影响项 |
|------|------|--------|
| **Bagging**（增大 $T$） | 增加树的数量 | 减小第二项 $\frac{(1-\rho)\sigma^2}{T}$ |
| **Feature Subsampling**（减小 $m$） | 降低树之间的相关性 $\rho$ | 减小第一项 $\rho\sigma^2$ |

> **关键洞察**：纯 Bagging（不做 Feature Subsampling）时 $\rho$ 较高，因为所有树都会选择相同的强特征做首次分裂。Feature Subsampling 强制树使用不同的特征子集，降低 $\rho$，这就是 Random Forest 优于纯 Bagging 的原因。

### 5.3 OOB（Out-of-Bag）Error

每次 Bootstrap 采样约有 $1 - (1 - 1/N)^N \approx 1 - 1/e \approx 63.2\%$ 的样本被选中，剩余 $\approx 36.8\%$ 未被选中（OOB 样本）。

对每个样本 $x_i$，收集所有**未使用 $x_i$ 训练的树**的预测，取投票/平均作为 OOB 预测。OOB Error 是这些预测的误差。

**优势**：无需额外划分验证集，自带"免费"的泛化误差估计。

### 5.4 Leaf Node 输出

**不一定是 0 或 1**：

- **分类树**：叶节点输出多数类标签，`predict_proba()` 返回类别比例
- **回归树**：叶节点输出样本均值（连续值）
- **Gradient Boosting 中的树**：叶节点输出 gradient residual（任意实数）

### 5.5 Random Forest 纯 Python 实现

```python
import numpy as np
from collections import Counter

class RandomForestFromScratch:
    """Random Forest classifier - from scratch.

    Uses DecisionTreeFromScratch as base learner with bootstrap + feature subsampling.
    """

    def __init__(self, n_estimators=100, max_depth=None,
                 max_features="sqrt", random_state=42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.random_state = random_state
        self.trees = []
        self.feature_indices = []  # features used by each tree

    def _get_n_features(self, n_total):
        if self.max_features == "sqrt":
            return max(1, int(np.sqrt(n_total)))
        elif self.max_features == "log2":
            return max(1, int(np.log2(n_total)))
        elif isinstance(self.max_features, int):
            return self.max_features
        return n_total  # use all features

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestFromScratch":
        rng = np.random.RandomState(self.random_state)
        n_samples, n_features = X.shape
        m = self._get_n_features(n_features)

        self.trees = []
        self.feature_indices = []

        for _ in range(self.n_estimators):
            # Bootstrap sampling
            indices = rng.choice(n_samples, size=n_samples, replace=True)
            X_boot = X[indices]
            y_boot = y[indices]

            # Feature subsampling
            feat_idx = rng.choice(n_features, size=m, replace=False)
            feat_idx.sort()
            self.feature_indices.append(feat_idx)

            # Train tree on bootstrap sample with feature subset
            tree = DecisionTreeFromScratch(
                max_depth=self.max_depth, min_samples_split=2
            )
            tree.fit(X_boot[:, feat_idx], y_boot)
            self.trees.append(tree)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        # Collect predictions from all trees
        all_preds = np.array([
            tree.predict(X[:, feat_idx])
            for tree, feat_idx in zip(self.trees, self.feature_indices)
        ])  # shape: (n_estimators, n_samples)

        # Majority vote
        predictions = []
        for i in range(X.shape[0]):
            votes = all_preds[:, i]
            predictions.append(Counter(votes).most_common(1)[0][0])
        return np.array(predictions)
```

### 5.6 Random Forest sklearn 验证

```python
from sklearn.ensemble import RandomForestClassifier

# Same Iris train/test split as Section 4.2
rf_scratch = RandomForestFromScratch(n_estimators=100, max_depth=5, random_state=42)
rf_scratch.fit(X_train, y_train)
rf_sklearn = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42).fit(X_train, y_train)

print(f"RF scratch: {accuracy_score(y_test, rf_scratch.predict(X_test)):.4f}")
print(f"RF sklearn: {accuracy_score(y_test, rf_sklearn.predict(X_test)):.4f}")
```

### 5.7 Random Forest vs Boosting 对比

| 方面 | Random Forest | Boosting (GBDT/XGBoost) |
|------|--------------|------------------------|
| 训练方式 | 并行（独立训练） | 串行（每棵树修正前面的错误） |
| 解决的问题 | 降低 Variance | 降低 Bias（也降低 Variance） |
| 过拟合风险 | 低（天然正则化） | 高（需要调参控制） |
| 树的深度 | 通常很深（fully grown） | 通常很浅（weak learners, depth 3-8） |
| 关键超参 | `n_estimators`, `max_features` | `learning_rate`, `n_estimators`, `max_depth` |
| 增加树数 | 不会过拟合（Variance 单调下降） | 可能过拟合（需 early stopping） |
| 计算效率 | 可并行化 | 必须串行 |

---

## 6. AdaBoost（Adaptive Boosting）

---

### 6.1 核心思想

AdaBoost 是第一个成功的 Boosting 算法（Freund & Schapire, 1997）。核心思想：

1. 训练一系列 **Weak Learner（弱学习器）**（通常是 depth-1 的 Decision Stump）
2. 每轮给**分错的样本增加权重**，让下一个弱学习器聚焦于难分样本
3. 最终预测是所有弱学习器的**加权投票**

### 6.2 完整算法推导

给定训练集 $\{(x_i, y_i)\}_{i=1}^{N}$，$y_i \in \{-1, +1\}$。

**初始化**：样本权重均匀分布

$$w_i^{(1)} = \frac{1}{N}, \quad i = 1, 2, \ldots, N$$

**第 $t$ 轮（$t = 1, 2, \ldots, T$）**：

**Step 1**：用加权数据集训练弱学习器 $h_t(x)$，最小化加权错误率：

$$\epsilon_t = \sum_{i=1}^{N} w_i^{(t)} \cdot \mathbb{1}[h_t(x_i) \neq y_i] = \frac{\text{错分样本的权重之和}}{\text{总权重}}$$

**Step 2**：计算弱学习器的投票权重：

$$\alpha_t = \frac{1}{2}\ln\frac{1 - \epsilon_t}{\epsilon_t}$$

**$\alpha_t$ 的性质**：
- $\epsilon_t = 0$（完美分类）：$\alpha_t \to +\infty$（权重极大）
- $\epsilon_t = 0.5$（随机猜测）：$\alpha_t = 0$（无贡献）
- $\epsilon_t > 0.5$（比随机差）：$\alpha_t < 0$（反转预测）

**Step 3**：更新样本权重：

$$w_i^{(t+1)} = w_i^{(t)} \cdot \exp\left(-\alpha_t \cdot y_i \cdot h_t(x_i)\right)$$

然后归一化：$w_i^{(t+1)} \leftarrow \frac{w_i^{(t+1)}}{\sum_{j=1}^{N} w_j^{(t+1)}}$

**更新规则的直觉**：
- 分对的样本（$y_i \cdot h_t(x_i) = +1$）：权重乘以 $e^{-\alpha_t} < 1$，**权重降低**
- 分错的样本（$y_i \cdot h_t(x_i) = -1$）：权重乘以 $e^{+\alpha_t} > 1$，**权重增加**

**最终输出**：

$$H(x) = \text{sign}\left(\sum_{t=1}^{T} \alpha_t \cdot h_t(x)\right)$$

### 6.3 AdaBoost 与指数损失的关系

AdaBoost 等价于在 **Exponential Loss（指数损失）** 下做 **Forward Stagewise Additive Modeling（前向逐步加法模型）**。

指数损失函数：

$$L(y, f(x)) = \exp(-y \cdot f(x))$$

其中 $f(x) = \sum_{t=1}^{T} \alpha_t h_t(x)$。

在第 $t$ 轮，固定前 $t-1$ 个弱学习器，最小化：

$$(\alpha_t, h_t) = \arg\min_{\alpha, h} \sum_{i=1}^{N} \exp\left(-y_i \left[f_{t-1}(x_i) + \alpha \cdot h(x_i)\right]\right)$$

令 $w_i^{(t)} = \exp(-y_i \cdot f_{t-1}(x_i))$，化简后恰好得到上述 $\alpha_t$ 和权重更新公式。

### 6.4 AdaBoost 纯 Python 实现

```python
import numpy as np

class DecisionStump:
    """Depth-1 decision tree (decision stump) for AdaBoost."""

    def __init__(self):
        self.feature_idx = None
        self.threshold = None
        self.polarity = 1  # 1 or -1

    def fit(self, X: np.ndarray, y: np.ndarray,
            weights: np.ndarray) -> "DecisionStump":
        n_samples, n_features = X.shape
        best_error = float('inf')

        for feat_idx in range(n_features):
            thresholds = np.unique(X[:, feat_idx])
            for thresh in thresholds:
                for polarity in [1, -1]:
                    pred = np.ones(n_samples)
                    if polarity == 1:
                        pred[X[:, feat_idx] <= thresh] = -1
                    else:
                        pred[X[:, feat_idx] > thresh] = -1

                    error = np.sum(weights[pred != y])

                    if error < best_error:
                        best_error = error
                        self.feature_idx = feat_idx
                        self.threshold = thresh
                        self.polarity = polarity

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        pred = np.ones(X.shape[0])
        if self.polarity == 1:
            pred[X[:, self.feature_idx] <= self.threshold] = -1
        else:
            pred[X[:, self.feature_idx] > self.threshold] = -1
        return pred


class AdaBoostFromScratch:
    """AdaBoost binary classifier - from scratch.

    Uses decision stumps as weak learners.
    Labels must be {-1, +1}.
    """

    def __init__(self, n_estimators=50):
        self.n_estimators = n_estimators
        self.alphas = []
        self.stumps = []

    def fit(self, X: np.ndarray, y: np.ndarray) -> "AdaBoostFromScratch":
        n_samples = len(y)
        weights = np.full(n_samples, 1.0 / n_samples)

        self.alphas = []
        self.stumps = []

        for _ in range(self.n_estimators):
            # Step 1: Train weak learner
            stump = DecisionStump()
            stump.fit(X, y, weights)
            predictions = stump.predict(X)

            # Step 2: Compute weighted error
            misclassified = predictions != y
            epsilon = np.sum(weights * misclassified)

            # Avoid division by zero / log(0)
            epsilon = np.clip(epsilon, 1e-10, 1 - 1e-10)

            # Step 3: Compute learner weight
            alpha = 0.5 * np.log((1 - epsilon) / epsilon)

            # Step 4: Update sample weights
            weights *= np.exp(-alpha * y * predictions)
            weights /= np.sum(weights)  # normalize

            self.alphas.append(alpha)
            self.stumps.append(stump)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        # Weighted vote of all stumps
        stump_preds = np.array([
            alpha * stump.predict(X)
            for alpha, stump in zip(self.alphas, self.stumps)
        ])
        return np.sign(np.sum(stump_preds, axis=0))
```

### 6.5 AdaBoost sklearn 验证

```python
from sklearn.ensemble import AdaBoostClassifier
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=500, n_features=10, random_state=42)
y_ada = 2 * y - 1  # {0,1} -> {-1,+1}
X_train, X_test, y_train, y_test = train_test_split(X, y_ada, test_size=0.3, random_state=42)

ada_scratch = AdaBoostFromScratch(n_estimators=50)
ada_scratch.fit(X_train, y_train)
y_train_sk, y_test_sk = (y_train + 1) // 2, (y_test + 1) // 2
ada_sk = AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1),
                            n_estimators=50, random_state=42, algorithm='SAMME')
ada_sk.fit(X_train, y_train_sk)

print(f"AdaBoost scratch: {accuracy_score(y_test, ada_scratch.predict(X_test)):.4f}")
print(f"AdaBoost sklearn: {accuracy_score(y_test_sk, ada_sk.predict(X_test)):.4f}")
```

---

## 7. GBDT（Gradient Boosted Decision Trees）

---

### 7.1 核心思想

GBDT（Friedman, 2001）是 Boosting 的一般化框架：

- AdaBoost：指数损失 + 样本权重调整
- **GBDT**：**任意可微损失函数** + **拟合负梯度（残差）**

核心区别：GBDT 不调整样本权重，而是让每棵新树去拟合当前模型的 **负梯度（Negative Gradient）**，也称为 **伪残差（Pseudo-Residuals）**。

### 7.2 算法流程

给定损失函数 $L(y, f(x))$，训练集 $\{(x_i, y_i)\}_{i=1}^{N}$。

**初始化**：

$$f_0(x) = \arg\min_c \sum_{i=1}^{N} L(y_i, c)$$

对 MSE 损失：$f_0(x) = \bar{y}$（训练集目标值均值）

**第 $t$ 轮（$t = 1, 2, \ldots, T$）**：

**Step 1**：计算伪残差（负梯度）：

$$r_{it} = -\frac{\partial L(y_i, f(x_i))}{\partial f(x_i)}\bigg|_{f = f_{t-1}}$$

对不同损失函数：
- **MSE**：$L = \frac{1}{2}(y - f)^2 \Rightarrow r_{it} = y_i - f_{t-1}(x_i)$（就是真正的残差）
- **Log Loss（二分类）**：$L = -[y\log p + (1-y)\log(1-p)] \Rightarrow r_{it} = y_i - p_i$
- **MAE**：$L = |y - f| \Rightarrow r_{it} = \text{sign}(y_i - f_{t-1}(x_i))$

**Step 2**：拟合一棵回归树 $h_t(x)$ 到伪残差 $\{(x_i, r_{it})\}$

**Step 3**：对树的每个叶节点区域 $R_{jt}$，计算最优叶值：

$$\gamma_{jt} = \arg\min_\gamma \sum_{x_i \in R_{jt}} L(y_i, f_{t-1}(x_i) + \gamma)$$

**Step 4**：更新模型（加上 **Shrinkage**）：

$$f_t(x) = f_{t-1}(x) + \eta \cdot \sum_{j=1}^{J_t} \gamma_{jt} \cdot \mathbb{1}[x \in R_{jt}]$$

其中 $\eta \in (0, 1]$ 是 **Learning Rate（学习率）**。

### 7.3 Shrinkage（收缩）的作用

$$f_t(x) = f_{t-1}(x) + \eta \cdot h_t(x)$$

| $\eta$ | 效果 |
|---------|------|
| $\eta = 1$ | 无 Shrinkage，每棵树的贡献不缩放 |
| $\eta = 0.1$ | 每棵树只贡献 10%，需要更多树 |
| $\eta \to 0$ | 极慢收敛，但泛化更好 |

**Shrinkage 的直觉**：类似于 Gradient Descent 中的学习率。步长太大容易跳过最优解（过拟合），步长小+更多步骤 → 更平滑的逼近。

**经验规律**（Friedman, 2001）：
- $\eta \leq 0.1$ 配合 Early Stopping 通常效果最好
- $\eta$ 越小需要越多的树，**$\eta$ 和 `n_estimators` 需要联合调参**

### 7.4 GBDT 正则化手段

| 方法 | 参数 | 作用 |
|------|------|------|
| Shrinkage | `learning_rate` | 缩小每棵树贡献 |
| 树的深度限制 | `max_depth` | 限制单棵树复杂度（通常 3-8） |
| Subsampling | `subsample` | 每轮只用部分数据（类似 SGD） |
| Early Stopping | `n_iter_no_change` | 验证集误差不再下降时停止 |
| L2 正则化 | `reg_lambda` (XGBoost) | 叶值的 L2 惩罚 |
| 最大叶节点数 | `max_leaf_nodes` | 控制树的大小 |

### 7.5 GBDT 回归纯 Python 实现

```python
import numpy as np

class GBDTRegressorFromScratch:
    """Gradient Boosted Decision Trees for regression (MSE loss) - from scratch.

    Uses DecisionTreeFromScratch (regression variant) as base learner.
    For simplicity, uses sklearn DecisionTreeRegressor internally.
    """

    def __init__(self, n_estimators=100, learning_rate=0.1,
                 max_depth=3, subsample=1.0, random_state=42):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.random_state = random_state
        self.trees = []
        self.f0 = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GBDTRegressorFromScratch":
        from sklearn.tree import DecisionTreeRegressor

        rng = np.random.RandomState(self.random_state)
        n_samples = len(y)

        # Step 0: Initialize with mean
        self.f0 = np.mean(y)
        f = np.full(n_samples, self.f0)

        self.trees = []

        for _ in range(self.n_estimators):
            # Step 1: Compute pseudo-residuals (negative gradient of MSE)
            residuals = y - f

            # Subsampling
            if self.subsample < 1.0:
                n_sub = max(1, int(n_samples * self.subsample))
                idx = rng.choice(n_samples, size=n_sub, replace=False)
                X_sub, r_sub = X[idx], residuals[idx]
            else:
                X_sub, r_sub = X, residuals

            # Step 2: Fit regression tree to residuals
            tree = DecisionTreeRegressor(
                max_depth=self.max_depth, random_state=rng.randint(10000)
            )
            tree.fit(X_sub, r_sub)
            self.trees.append(tree)

            # Step 3: Update model with shrinkage
            f += self.learning_rate * tree.predict(X)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        f = np.full(X.shape[0], self.f0)
        for tree in self.trees:
            f += self.learning_rate * tree.predict(X)
        return f
```

### 7.6 GBDT sklearn 验证

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.datasets import make_regression
from sklearn.metrics import mean_squared_error

X, y = make_regression(n_samples=500, n_features=10, noise=10.0, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

gbdt_scratch = GBDTRegressorFromScratch(n_estimators=100, learning_rate=0.1, max_depth=3)
gbdt_scratch.fit(X_train, y_train)
gbdt_sk = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gbdt_sk.fit(X_train, y_train)

print(f"GBDT scratch MSE: {mean_squared_error(y_test, gbdt_scratch.predict(X_test)):.2f}")
print(f"GBDT sklearn MSE: {mean_squared_error(y_test, gbdt_sk.predict(X_test)):.2f}")
```

---

## 8. XGBoost / LightGBM / CatBoost 简要对比

---

| 方面 | XGBoost | LightGBM | CatBoost |
|------|---------|----------|----------|
| 树生长策略 | Level-wise（逐层） | **Leaf-wise（逐叶）** | Oblivious Trees（对称树） |
| 分裂查找 | Exact + Approximate | **Histogram-based** | Ordered Boosting |
| 类别特征 | 需要手动编码 | 原生支持 | **原生支持（最佳）** |
| 缺失值 | 自动处理（学习方向） | 自动处理 | 自动处理 |
| 速度 | 中等 | **最快** | 较慢 |
| GPU 支持 | 是 | 是 | 是 |
| 过拟合风险 | 中（需调参） | 高（Leaf-wise 更激进） | 低（对称树天然正则） |
| **何时选用** | 通用默认选择 | 大数据集/高维 | 类别特征多/调参少 |

**XGBoost 的关键改进**（相对于原始 GBDT）：

1. **二阶泰勒展开**：目标函数用一阶梯度 $g_i$ 和二阶梯度 $h_i$（Hessian）近似

$$\text{Obj}^{(t)} \approx \sum_{i=1}^{N}\left[g_i f_t(x_i) + \frac{1}{2}h_i f_t^2(x_i)\right] + \Omega(f_t)$$

2. **显式正则化**：$\Omega(f_t) = \gamma T + \frac{1}{2}\lambda\sum_{j=1}^{T}w_j^2$（叶数惩罚 + L2 叶值惩罚）
3. **最优叶值闭式解**：$w_j^* = -\frac{\sum_{i \in I_j} g_i}{\sum_{i \in I_j} h_i + \lambda}$
4. **分裂增益**：$\text{Gain} = \frac{1}{2}\left[\frac{G_L^2}{H_L + \lambda} + \frac{G_R^2}{H_R + \lambda} - \frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right] - \gamma$

---

## 9. 树模型优缺点总结

---

### 9.1 优点

1. **可解释性强**：可以可视化决策路径，输出 Feature Importance
2. **无需特征缩放**：基于阈值分裂，不受特征尺度影响
3. **处理非线性关系**：天然处理特征交互和非线性边界
4. **对异常值鲁棒**：分裂基于排序/阈值，不受极端值影响
5. **处理缺失值**：CART 使用代理分裂，XGBoost 自动学习方向
6. **混合特征类型**：同时处理数值型和类别型特征

### 9.2 缺点

1. **单棵树容易过拟合**：需要剪枝或集成
2. **不稳定**：数据小变动可能导致完全不同的树结构（高 Variance）
3. **贪心分裂**：不能保证全局最优
4. **不擅长外推**：预测值限制在训练数据范围内
5. **偏好多数类**：不平衡数据需要处理
6. **线性关系效率低**：简单线性关系需要多次分裂来逼近

### 9.3 Overfitting 防止方法总结

**单棵树**：
- 限制深度（`max_depth`）
- 限制叶节点样本数（`min_samples_leaf`）
- Post-Pruning（CCP）

**集成（Random Forest）**：
- 增加树数 → 降低 Variance（不会过拟合）
- 减小 `max_features` → 降低树间相关性

**集成（Boosting）**：
- Shrinkage（`learning_rate`）
- Early Stopping
- Subsampling
- L1/L2 正则化（XGBoost）

---

## 10. 面试高频问题

---

### Q1: ID3/C4.5/CART 的核心区别是什么？

- **ID3**：用 Information Gain 分裂，只支持离散特征，偏好多值特征
- **C4.5**：用 Gain Ratio 修正 ID3 的多值偏好，支持连续特征和缺失值
- **CART**：用 Gini/MSE，永远是二叉树，支持分类和回归，配合 CCP 剪枝
- sklearn 只实现了 **CART**

### Q2: Random Forest 为什么不容易过拟合？

Variance 公式推导：$\text{Var}(\bar{Z}) \approx \rho\sigma^2 + \frac{(1-\rho)\sigma^2}{T}$

- 增加 $T$ 减小第二项（Bagging 效果）
- Feature Subsampling 降低 $\rho$（树间去相关）
- 但**不是不会过拟合**：树极多时可能过拟合噪声，且 Bagging 不降低 Bias

### Q3: AdaBoost 和 GBDT 的本质区别？

| 方面 | AdaBoost | GBDT |
|------|----------|------|
| 错误纠正方式 | 调整样本权重 | 拟合负梯度（伪残差） |
| 损失函数 | 固定（指数损失） | 任意可微损失 |
| 弱学习器 | 通常 Decision Stump | 深度 3-8 的树 |
| 对异常值 | **敏感**（指数损失放大异常值影响） | 可选 Huber/MAE 损失抗异常值 |
| 数学本质 | 指数损失下的前向逐步加法模型 | 函数空间的梯度下降 |

### Q4: GBDT 中 Shrinkage 的作用？与 `n_estimators` 的关系？

Shrinkage（learning_rate $\eta$）缩小每棵树的贡献。$\eta$ 越小：
- 每棵树步长更小 → 逼近更平滑 → 泛化更好
- 需要更多树 → $\eta$ 和 `n_estimators` 必须联合调参
- 经验：$\eta \leq 0.1$ + Early Stopping 通常最优

### Q5: 什么时候用 Random Forest vs GBDT/XGBoost？

- **Random Forest**：数据量中等、不想花时间调参、需要并行训练、对结果可解释性有要求
- **GBDT/XGBoost**：追求最高精度、竞赛场景、可以投入调参时间、有 Early Stopping 机制
- **经验规律**：在 Kaggle 竞赛中，Boosting 几乎总是优于 Random Forest；在生产环境中，Random Forest 更稳健

---

## 11. 实际应用场景

---

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 快速 Baseline | 单棵 Decision Tree | 可解释，快速迭代 |
| 中等精度 + 稳定性 | Random Forest | 不容易过拟合，无需调参 |
| 最高精度 | XGBoost / LightGBM | Boosting + 正则化 |
| 大量类别特征 | CatBoost | 原生支持类别编码 |
| 大数据集 + 高维 | LightGBM | Histogram-based + Leaf-wise，速度最快 |
| 需要可解释性 | 单棵树 + SHAP | SHAP 解释 Boosting 模型 |

---

## 12. 总结对比表

---

| 方面 | Decision Tree | Random Forest | AdaBoost | GBDT |
|------|--------------|--------------|----------|------|
| 训练方式 | 单棵递归分裂 | 并行 Bagging | 串行加权 | 串行拟合残差 |
| 分裂准则 | Gini / Entropy / MSE | Gini + Feature Sub | 加权分类误差 | 负梯度 |
| 基学习器 | - | 深树 | Decision Stump | 浅树 (depth 3-8) |
| 主要降低 | Bias | **Variance** | Bias | **Bias** |
| 过拟合控制 | 剪枝 | 树数+特征采样 | 较弱 | Shrinkage+Early Stop |
| Outlier 敏感度 | 低 | 低 | **高** | 可调（Huber Loss） |
| 可解释性 | 最高 | Feature Importance | 低 | Feature Importance |
| sklearn 类 | `DecisionTree*` | `RandomForest*` | `AdaBoostClassifier` | `GradientBoosting*` |


---

# T7: Weight Initialization 完整推导 + 实现

> 本节覆盖：全零/随机初始化失败分析，Xavier/Glorot 方差守恒推导（前向+反向折中），He/Kaiming 初始化 ReLU 补偿推导，Orthogonal/LSUV/Fixup 等其他方法，纯 Python 实现 + PyTorch API 验证，LoRA 初始化策略。
> 合并来源：Doc 17 (LoRA init), Doc 20, Framework Node 77

---

## 1. 为什么初始化很重要？

---

### 1.1 核心问题

神经网络训练中，权重初始化决定了：

- **前向传播**：每层激活值的数值范围（方差是否保持稳定）
- **反向传播**：梯度的数值范围（是否发生梯度消失/爆炸）

一个 $L$ 层网络中，如果每层将方差乘以因子 $\alpha$：

- 前向传播后输出方差 $\approx \alpha^L \cdot \text{Var}(x)$
- $\alpha > 1$：激活值指数增长 $\rightarrow$ **数值溢出（Overflow）**
- $\alpha < 1$：激活值指数衰减 $\rightarrow$ **信号消失**
- $\alpha = 1$：方差守恒 $\rightarrow$ **理想状态**

### 1.2 方差传播分析框架

设第 $l$ 层为线性变换 $y^{(l)} = W^{(l)} x^{(l)} + b^{(l)}$，其中 $W^{(l)} \in \mathbb{R}^{n_{\text{out}} \times n_{\text{in}}}$。

假设权重 $w_{ij}$ 与输入 $x_j$ 独立，且均值为零：

$$\text{Var}(y_i) = \sum_{j=1}^{n_{\text{in}}} \text{Var}(w_{ij}) \cdot \text{Var}(x_j) = n_{\text{in}} \cdot \text{Var}(w) \cdot \text{Var}(x)$$

**推导过程**：

$$y_i = \sum_{j=1}^{n_{\text{in}}} w_{ij} x_j$$

由于 $\mathbb{E}[w_{ij}] = 0$，$\mathbb{E}[x_j] = 0$（中心化输入），且 $w_{ij} \perp x_j$：

$$\text{Var}(y_i) = \text{Var}\left(\sum_j w_{ij} x_j\right) = \sum_j \text{Var}(w_{ij} x_j)$$

$$= \sum_j \left[\mathbb{E}[w_{ij}^2]\mathbb{E}[x_j^2] - (\mathbb{E}[w_{ij}])^2(\mathbb{E}[x_j])^2\right] = \sum_j \text{Var}(w_{ij}) \cdot \text{Var}(x_j)$$

因此，要保持方差守恒 $\text{Var}(y) = \text{Var}(x)$：

$$n_{\text{in}} \cdot \text{Var}(w) = 1 \quad \Rightarrow \quad \text{Var}(w) = \frac{1}{n_{\text{in}}}$$

---

## 2. 失败的初始化方案

---

### 2.1 全零初始化（Zero Initialization）

$$W^{(l)} = \mathbf{0}, \quad b^{(l)} = 0$$

**为什么完全失败？** —— **对称性问题（Symmetry Problem）**

1. 所有神经元在第一次前向传播中输出相同值
2. 反向传播中所有神经元收到相同梯度
3. 参数更新完全相同 $\rightarrow$ 所有神经元永远保持一致
4. 网络退化为**单神经元等价物**，表达能力丧失

```python
import numpy as np

def demo_zero_init():
    """演示全零初始化导致的对称性问题"""
    np.random.seed(42)
    X = np.random.randn(4, 3)  # 4 samples, 3 features
    
    # 全零初始化
    W1 = np.zeros((3, 4))  # layer 1: 3->4
    W2 = np.zeros((4, 1))  # layer 2: 4->1
    
    # 前向传播
    h = np.maximum(0, X @ W1)  # ReLU
    print(f"Hidden layer output:\n{h}")
    # 输出全为0, 所有神经元完全相同
    
    # 即使经过梯度更新, 对称性也不会被打破
    # 因为 dL/dW1 的每一列都完全相同

demo_zero_init()
```

输出：

```
Hidden layer output:
[[0. 0. 0. 0.]
 [0. 0. 0. 0.]
 [0. 0. 0. 0.]
 [0. 0. 0. 0.]]
```

**例外**：偏置 $b$ 可以初始化为零（因为各神经元偏置更新方向由各自权重决定，不会对称）。LoRA 的 B 矩阵零初始化也是合理的（见第 8 节）。

### 2.2 过大随机初始化

$$W^{(l)} \sim \mathcal{N}(0, 1)$$

对于 $n_{\text{in}} = 512$ 的层：

$$\text{Var}(y) = n_{\text{in}} \cdot \text{Var}(w) \cdot \text{Var}(x) = 512 \cdot 1 \cdot \text{Var}(x) = 512 \cdot \text{Var}(x)$$

每层方差放大 512 倍！经过 $L$ 层：方差 $\sim 512^L$

```python
def demo_large_init(n_layers=10, n_hidden=512):
    """演示过大初始化导致激活值爆炸"""
    x = np.random.randn(1, n_hidden)
    for i in range(n_layers):
        W = np.random.randn(n_hidden, n_hidden)  # Var(w) = 1, 过大
        x = np.maximum(0, x @ W)  # ReLU
    print(f"After {n_layers} layers: mean={np.mean(x):.2e}, var={np.var(x):.2e}")
    # 数值爆炸到天文数字或溢出为 inf

demo_large_init()
```

### 2.3 过小随机初始化

$$W^{(l)} \sim \mathcal{N}(0, 0.001^2)$$

$$\text{Var}(y) = 512 \cdot 10^{-6} \cdot \text{Var}(x) = 0.000512 \cdot \text{Var}(x)$$

每层方差缩小约 2000 倍！经过 $L$ 层：所有激活值趋近于零，梯度消失。

```python
def demo_small_init(n_layers=10, n_hidden=512):
    """演示过小初始化导致信号消失"""
    x = np.random.randn(1, n_hidden)
    for i in range(n_layers):
        W = np.random.randn(n_hidden, n_hidden) * 0.001  # 过小
        x = np.tanh(x @ W)
    print(f"After {n_layers} layers: mean={np.mean(x):.2e}, var={np.var(x):.2e}")
    # 所有激活值趋近于 0

demo_small_init()
```

### 2.4 对比总结

| 初始化方案 | $\text{Var}(w)$ | 每层方差因子 ($n_{\text{in}}=512$) | 结果 |
|:---:|:---:|:---:|:---:|
| 全零 | 0 | 0 | 对称性，网络退化 |
| $\mathcal{N}(0, 1)$ | 1 | 512 | 激活值爆炸 |
| $\mathcal{N}(0, 0.001^2)$ | $10^{-6}$ | $5.12 \times 10^{-4}$ | 信号消失 |
| **正确** ($1/n_{\text{in}}$) | $1/512$ | **1** | **方差守恒** |

---

## 3. Xavier / Glorot Initialization

---

> Glorot & Bengio, 2010: *Understanding the difficulty of training deep feedforward neural networks*

### 3.1 前向传播约束

从 1.2 节的方差传播公式，要保持前向传播方差守恒：

$$\text{Var}(y) = n_{\text{in}} \cdot \text{Var}(w) \cdot \text{Var}(x) = \text{Var}(x)$$

$$\Rightarrow \text{Var}(w) = \frac{1}{n_{\text{in}}}$$

### 3.2 反向传播约束

设损失对第 $l$ 层输出的梯度为 $\delta^{(l)} = \frac{\partial \mathcal{L}}{\partial y^{(l)}}$。

反向传播时（线性层，忽略激活函数导数）：

$$\delta^{(l-1)} = (W^{(l)})^T \delta^{(l)}$$

类似前向分析：

$$\text{Var}(\delta^{(l-1)}_j) = n_{\text{out}} \cdot \text{Var}(w) \cdot \text{Var}(\delta^{(l)})$$

要保持梯度方差守恒：

$$n_{\text{out}} \cdot \text{Var}(w) = 1 \quad \Rightarrow \quad \text{Var}(w) = \frac{1}{n_{\text{out}}}$$

### 3.3 折中：Xavier 公式

前向要求 $\text{Var}(w) = 1/n_{\text{in}}$，反向要求 $\text{Var}(w) = 1/n_{\text{out}}$。

当 $n_{\text{in}} \neq n_{\text{out}}$ 时无法同时满足，取**调和折中**：

$$\boxed{\text{Var}(w) = \frac{2}{n_{\text{in}} + n_{\text{out}}}}$$

**正态分布形式**：

$$W \sim \mathcal{N}\left(0, \; \frac{2}{n_{\text{in}} + n_{\text{out}}}\right)$$

**均匀分布形式**：

利用均匀分布 $U[-a, a]$ 的方差为 $a^2/3$：

$$\frac{a^2}{3} = \frac{2}{n_{\text{in}} + n_{\text{out}}} \quad \Rightarrow \quad a = \sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}$$

$$W \sim U\left[-\sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}, \; \sqrt{\frac{6}{n_{\text{in}} + n_{\text{out}}}}\right]$$

### 3.4 适用场景与局限

**适用**：
- **Sigmoid** 激活函数（在零点附近近似线性）
- **Tanh（Hyperbolic Tangent，双曲正切）** 激活函数
- 输出层（通常无激活或 Softmax）

**不适用**：
- **ReLU** 及其变体——Xavier 推导假设激活函数关于零点对称，ReLU 将一半输出置零，方差被额外减半

### 3.5 为什么对 Sigmoid/Tanh 有效？

Xavier 推导假设激活函数 $f(x)$ 在零点附近近似线性，即 $f(x) \approx x$。

- $\tanh(x)$：在 $x=0$ 处 $\tanh'(0) = 1$，线性近似良好
- $\sigma(x)$：在 $x=0$ 处 $\sigma'(0) = 0.25$，线性近似尚可（但方差会缩小）

**注意**：对于 Sigmoid，由于 $\sigma'(0) = 0.25 \neq 1$，Xavier 并非完美匹配。实践中 Tanh 是 Xavier 的最佳搭配。

---

## 4. He / Kaiming Initialization

---

> He et al., 2015: *Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification*

### 4.1 ReLU 的方差衰减问题

ReLU 定义：$f(x) = \max(0, x)$

当输入 $x \sim \mathcal{N}(0, \sigma^2)$（对称分布，零均值）时：

- 约一半的值被置零（$x < 0$ 的部分）
- $\mathbb{E}[f(x)^2] = \mathbb{E}[\max(0,x)^2]$

计算 ReLU 输出的二阶矩：

$$\mathbb{E}[\max(0,x)^2] = \int_0^{\infty} x^2 \cdot \frac{1}{\sqrt{2\pi}\sigma} e^{-x^2/(2\sigma^2)} dx = \frac{\sigma^2}{2}$$

**推导**（半高斯积分）：

$$\int_0^{\infty} x^2 \cdot \frac{1}{\sqrt{2\pi}\sigma} e^{-x^2/(2\sigma^2)} dx = \frac{1}{2} \int_{-\infty}^{\infty} x^2 \cdot \frac{1}{\sqrt{2\pi}\sigma} e^{-x^2/(2\sigma^2)} dx = \frac{1}{2} \cdot \sigma^2$$

（利用 $x^2$ 为偶函数，被积函数关于零对称，半区间积分恰为全区间的一半）

由于 ReLU 输出均值不为零，$\text{Var}(\text{ReLU}(x)) = \mathbb{E}[\text{ReLU}(x)^2] - (\mathbb{E}[\text{ReLU}(x)])^2$，但在实践中我们关注的是二阶矩的传播。ReLU 将信号的二阶矩减半：

$$\mathbb{E}[(\text{ReLU}(y))^2] = \frac{1}{2} \mathbb{E}[y^2]$$

### 4.2 完整方差传播

结合线性层 + ReLU：

$$\mathbb{E}[(x^{(l+1)})^2] = \mathbb{E}[(\text{ReLU}(W^{(l)}x^{(l)}))^2] = \frac{1}{2} \cdot n_{\text{in}} \cdot \text{Var}(w^{(l)}) \cdot \mathbb{E}[(x^{(l)})^2]$$

要保持二阶矩守恒：

$$\frac{1}{2} \cdot n_{\text{in}} \cdot \text{Var}(w) = 1$$

$$\boxed{\text{Var}(w) = \frac{2}{n_{\text{in}}}}$$

这就是 **He Initialization（He 初始化）** 公式。因子 2 正是为了补偿 ReLU 丢弃一半信号。

### 4.3 He 初始化的两种模式

**fan_in 模式**（默认，保持前向传播方差）：

$$W \sim \mathcal{N}\left(0, \; \frac{2}{n_{\text{in}}}\right)$$

**fan_out 模式**（保持反向传播方差）：

$$W \sim \mathcal{N}\left(0, \; \frac{2}{n_{\text{out}}}\right)$$

**如何选择？**
- `fan_in`：用于大多数情况，保证前向传播信号稳定
- `fan_out`：当网络宽度递减（如分类头）时，优先稳定梯度回传

**均匀分布形式**：

$$W \sim U\left[-\sqrt{\frac{6}{n_{\text{in}}}}, \; \sqrt{\frac{6}{n_{\text{in}}}}\right]$$

### 4.4 Leaky ReLU 的调整

Leaky ReLU：$f(x) = \max(\alpha x, x)$，其中 $\alpha$ 是负半轴斜率（通常 $\alpha = 0.01$）。

Leaky ReLU 的二阶矩：

$$\mathbb{E}[f(x)^2] = \frac{1 + \alpha^2}{2} \cdot \sigma^2$$

（正半轴贡献 $\sigma^2/2$，负半轴贡献 $\alpha^2 \sigma^2 / 2$）

因此方差守恒条件变为：

$$\text{Var}(w) = \frac{2}{(1 + \alpha^2) \cdot n_{\text{in}}}$$

当 $\alpha = 0$ 时退化为标准 He 初始化。PyTorch 的 `kaiming_normal_` 默认支持 `a` 参数指定 Leaky ReLU 的负斜率。

---

## 5. Xavier vs He 对比

---

| 特性 | Xavier / Glorot | He / Kaiming |
|:---:|:---:|:---:|
| 论文 | Glorot & Bengio, 2010 | He et al., 2015 |
| 方差公式 | $\frac{2}{n_{\text{in}} + n_{\text{out}}}$ | $\frac{2}{n_{\text{in}}}$ |
| 前向/反向 | 折中（同时考虑） | 默认保前向（fan_in） |
| 适用激活 | Sigmoid, Tanh | ReLU, Leaky ReLU, PReLU |
| 推导假设 | 线性激活 $f(x) \approx x$ | ReLU 半区间截断 |
| 关键差异 | 无需补偿因子 | 因子 2 补偿 ReLU 的方差减半 |

**面试快速记忆**：

- Xavier：$\text{Var} = \frac{2}{n_{\text{in}} + n_{\text{out}}}$（前向+反向折中）
- He：$\text{Var} = \frac{2}{n_{\text{in}}}$（ReLU 补偿 $\times 2$）
- 两者都用 $n_{\text{in}}$ 做分母基数，Xavier 多了 $n_{\text{out}}$，He 多了因子 2

---

## 6. 其他初始化方法

---

### 6.1 Orthogonal Initialization（正交初始化）

将权重矩阵初始化为正交矩阵（或其缩放版本），即 $W^TW = I$。

**核心性质**：正交矩阵的所有奇异值为 1，因此：
- 前向传播：$\|Wx\| = \|x\|$，范数严格保持
- 反向传播：$\|W^T\delta\| = \|\delta\|$，梯度范数不变

**生成方法**：对随机高斯矩阵做 **QR 分解**或 **SVD（Singular Value Decomposition，奇异值分解）**，取正交部分。

**适用场景**：
- **RNN（Recurrent Neural Network，循环神经网络）**：隐状态转移矩阵 $W_h$ 反复乘以自身，正交性防止长序列梯度消失/爆炸
- 深层网络需要严格的范数保持时

### 6.2 LSUV（Layer-Sequential Unit-Variance，逐层单位方差初始化）

**数据驱动**的初始化方法：

1. 先用正交初始化所有权重
2. 逐层用一个 mini-batch 数据做前向传播
3. 测量每层输出方差，将权重缩放使输出方差 $\approx 1$
4. 重复直到所有层方差稳定

**优势**：不依赖理论假设（线性/ReLU），适用于任意激活函数和复杂架构。

### 6.3 Fixup Initialization

允许在**没有 BatchNorm（Batch Normalization，批归一化）** 的情况下训练深度残差网络。

核心思想：将残差分支的最后一层权重初始化为零（或接近零），使得网络初始行为接近恒等映射。对于 $L$ 个残差块：

$$W_{\text{last}} \leftarrow W_{\text{last}} \cdot L^{-1/(2m-2)}$$

其中 $m$ 是每个残差块中的层数。

### 6.4 方法对比

| 方法 | 理论基础 | 数据依赖 | 适用场景 |
|:---:|:---:|:---:|:---:|
| Xavier | 方差守恒（线性） | 否 | Sigmoid/Tanh |
| He | 方差守恒（ReLU） | 否 | ReLU 及变体 |
| Orthogonal | 范数保持（正交） | 否 | RNN, 极深网络 |
| LSUV | 经验方差归一 | 是 | 任意架构 |
| Fixup | 残差零初始化 | 否 | ResNet without BN |

---

## 7. 纯 Python 从零实现

---

```python
import numpy as np

# ============================================================
# 7.1 Xavier Initialization (Glorot)
# ============================================================
def xavier_normal(n_in: int, n_out: int) -> np.ndarray:
    """Xavier normal initialization.
    
    Var(w) = 2 / (n_in + n_out)
    """
    std = np.sqrt(2.0 / (n_in + n_out))
    return np.random.randn(n_in, n_out) * std

def xavier_uniform(n_in: int, n_out: int) -> np.ndarray:
    """Xavier uniform initialization.
    
    W ~ U[-a, a], a = sqrt(6 / (n_in + n_out))
    """
    a = np.sqrt(6.0 / (n_in + n_out))
    return np.random.uniform(-a, a, size=(n_in, n_out))

# ============================================================
# 7.2 He/Kaiming Initialization
# ============================================================
def he_normal(n_in: int, n_out: int, mode: str = "fan_in") -> np.ndarray:
    """He/Kaiming normal initialization for ReLU.
    
    fan_in:  Var(w) = 2 / n_in  (preserve forward variance)
    fan_out: Var(w) = 2 / n_out (preserve backward variance)
    """
    fan = n_in if mode == "fan_in" else n_out
    std = np.sqrt(2.0 / fan)
    return np.random.randn(n_in, n_out) * std

def he_uniform(n_in: int, n_out: int, mode: str = "fan_in") -> np.ndarray:
    """He/Kaiming uniform initialization for ReLU."""
    fan = n_in if mode == "fan_in" else n_out
    a = np.sqrt(6.0 / fan)
    return np.random.uniform(-a, a, size=(n_in, n_out))

def he_leaky_relu(n_in: int, n_out: int, alpha: float = 0.01) -> np.ndarray:
    """He initialization adjusted for Leaky ReLU.
    
    Var(w) = 2 / ((1 + alpha^2) * n_in)
    """
    std = np.sqrt(2.0 / ((1 + alpha**2) * n_in))
    return np.random.randn(n_in, n_out) * std

# ============================================================
# 7.3 Orthogonal Initialization
# ============================================================
def orthogonal_init(n_in: int, n_out: int, gain: float = 1.0) -> np.ndarray:
    """Orthogonal initialization via QR decomposition."""
    # 生成随机高斯矩阵
    a = np.random.randn(n_in, n_out)
    # QR 分解
    if n_in >= n_out:
        q, r = np.linalg.qr(a)
        q = q[:, :n_out]
    else:
        q, r = np.linalg.qr(a.T)
        q = q[:, :n_in].T
    # 确保符号一致性 (使 Q 的对角线为正)
    d = np.diag(r)
    sign = np.sign(d)
    q *= sign
    return q * gain

# ============================================================
# 7.4 方差验证实验
# ============================================================
def verify_variance_propagation():
    """验证不同初始化方法在多层网络中的方差传播"""
    np.random.seed(42)
    n_samples = 1000
    n_hidden = 256
    n_layers = 20
    
    methods = {
        "N(0,1) -- too large": lambda ni, no: np.random.randn(ni, no),
        "N(0,0.001) -- too small": lambda ni, no: np.random.randn(ni, no) * 0.001,
        "Xavier normal": xavier_normal,
        "He normal": he_normal,
    }
    
    activations = {
        "tanh": np.tanh,
        "relu": lambda x: np.maximum(0, x),
    }
    
    print(f"{'Method':<25} {'Activation':<10} {'Layer 1 Var':>12} {'Layer 10 Var':>13} {'Layer 20 Var':>13}")
    print("-" * 75)
    
    for method_name, init_fn in methods.items():
        for act_name, act_fn in activations.items():
            x = np.random.randn(n_samples, n_hidden)
            variances = []
            for layer in range(n_layers):
                W = init_fn(n_hidden, n_hidden)
                x = act_fn(x @ W)
                if layer in [0, 9, 19]:
                    variances.append(np.var(x))
            
            v1, v10, v20 = variances
            print(f"{method_name:<25} {act_name:<10} {v1:>12.6f} {v10:>13.6f} {v20:>13.6f}")
    
    print()
    print("Ideal: variance stays ~1.0 across all layers")
    print("Xavier + tanh: stable | He + relu: stable")

verify_variance_propagation()
```

**预期输出**（数值因随机种子而异，趋势一致）：

```
Method                    Activation  Layer 1 Var Layer 10 Var Layer 20 Var
---------------------------------------------------------------------------
N(0,1) -- too large       tanh           1.000000      1.000000      1.000000
N(0,1) -- too large       relu                inf           inf           inf
N(0,0.001) -- too small   tanh           0.000000      0.000000      0.000000
N(0,0.001) -- too small   relu           0.000000      0.000000      0.000000
Xavier normal             tanh           0.660000      0.380000      0.230000
Xavier normal             relu           0.500000      0.030000      0.002000
He normal                 tanh           1.000000      1.000000      0.950000
He normal                 relu           1.000000      0.950000      0.900000
```

**关键观察**：
- $\mathcal{N}(0,1)$ + tanh：tanh 将输出压到 $[-1,1]$，方差饱和为 1（但 Sigmoid/Tanh 饱和区梯度消失）
- $\mathcal{N}(0,1)$ + ReLU：方差指数爆炸至 inf
- Xavier + tanh：方差缓慢衰减（实际中可接受）
- Xavier + ReLU：方差快速衰减（每层减半）
- **He + ReLU**：方差保持稳定 $\approx 1$ -- **最佳搭配**

---

## 8. LoRA 初始化策略

---

> 来自 Doc 17: LoRA 核心公式

**LoRA（Low-Rank Adaptation，低秩适配）** 将预训练权重分解为：

$$W' = W + BA$$

其中：
- $W \in \mathbb{R}^{d_{\text{out}} \times d_{\text{in}}}$：原始预训练权重，**冻结不动**
- $A \in \mathbb{R}^{r \times d_{\text{in}}}$：**高斯随机初始化**（Kaiming 或标准正态）
- $B \in \mathbb{R}^{d_{\text{out}} \times r}$：**零初始化**
- $r \ll \min(d_{\text{in}}, d_{\text{out}})$：低秩维度

**为什么 B 用零初始化？**

训练开始时 $BA = \mathbf{0} \cdot A = \mathbf{0}$，因此 $W' = W + \mathbf{0} = W$。

这保证**训练起点与原始预训练模型完全一致**，LoRA 从"无修改"状态开始逐步学习适配。

**注意**：这里零初始化不会导致对称性问题，因为：
1. $A$ 是随机初始化的，打破了对称性
2. $B$ 的梯度通过 $A$ 传播：$\frac{\partial \mathcal{L}}{\partial B} = \frac{\partial \mathcal{L}}{\partial y} \cdot A^T$，各行梯度不同
3. 经过第一次更新后 $B$ 各行不再相同

---

## 9. PyTorch API 验证

---

```python
import torch
import torch.nn as nn

# ============================================================
# 9.1 PyTorch 内置初始化函数
# ============================================================

# Xavier / Glorot
linear1 = nn.Linear(512, 256)
nn.init.xavier_normal_(linear1.weight)    # N(0, 2/(512+256))
nn.init.xavier_uniform_(linear1.weight)   # U[-a, a], a = sqrt(6/(512+256))
print(f"Xavier normal var: {linear1.weight.var().item():.6f}")
print(f"Theory: {2/(512+256):.6f}")

# He / Kaiming
linear2 = nn.Linear(512, 256)
nn.init.kaiming_normal_(linear2.weight, mode='fan_in', nonlinearity='relu')
print(f"\nHe normal (fan_in) var: {linear2.weight.var().item():.6f}")
print(f"Theory: {2/512:.6f}")

nn.init.kaiming_normal_(linear2.weight, mode='fan_out', nonlinearity='relu')
print(f"He normal (fan_out) var: {linear2.weight.var().item():.6f}")
print(f"Theory: {2/256:.6f}")

# Leaky ReLU with negative slope a=0.2
nn.init.kaiming_normal_(linear2.weight, a=0.2, mode='fan_in', nonlinearity='leaky_relu')
print(f"\nHe Leaky ReLU (a=0.2) var: {linear2.weight.var().item():.6f}")
print(f"Theory: {2/((1+0.04)*512):.6f}")

# Orthogonal
linear3 = nn.Linear(256, 256)
nn.init.orthogonal_(linear3.weight, gain=1.0)
# 验证正交性: W^T W ≈ I
WtW = linear3.weight @ linear3.weight.T
print(f"\nOrthogonal: ||W^TW - I||_F = {torch.norm(WtW - torch.eye(256)).item():.6f}")

# ============================================================
# 9.2 完整网络初始化示例
# ============================================================

class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, n_layers: int):
        super().__init__()
        layers = []
        dims = [input_dim] + [hidden_dim] * (n_layers - 1) + [output_dim]
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i+1]))
            if i < len(dims) - 2:  # 最后一层不加 ReLU
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)
        self._init_weights()
    
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)  # 偏置零初始化
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

# 验证方差传播
model = MLP(256, 256, 10, n_layers=10)
x = torch.randn(64, 256)

# Hook 观察每层激活值方差
variances = []
def hook_fn(module, input, output):
    variances.append(output.var().item())

hooks = []
for m in model.modules():
    if isinstance(m, nn.ReLU):
        hooks.append(m.register_forward_hook(hook_fn))

with torch.no_grad():
    _ = model(x)

for h in hooks:
    h.remove()

print("\nActivation variance per ReLU layer (He init):")
for i, v in enumerate(variances):
    bar = "#" * int(min(v * 20, 40))
    print(f"  Layer {i+1}: {v:.4f} {bar}")

# ============================================================
# 9.3 CNN 初始化（卷积层的 fan_in/fan_out）
# ============================================================

conv = nn.Conv2d(64, 128, kernel_size=3, padding=1)
nn.init.kaiming_normal_(conv.weight, mode='fan_in', nonlinearity='relu')

# 对于 Conv2d: fan_in = C_in * K * K, fan_out = C_out * K * K
fan_in = 64 * 3 * 3   # = 576
fan_out = 128 * 3 * 3  # = 1152
print(f"\nConv2d He init:")
print(f"  fan_in = {fan_in}, fan_out = {fan_out}")
print(f"  Weight var: {conv.weight.var().item():.6f}")
print(f"  Theory (2/fan_in): {2/fan_in:.6f}")
```

---

## 10. 面试高频问答

---

### Q1: 为什么不能全零初始化？

**A**: 全零初始化导致**对称性问题**。同一层的所有神经元接收相同输入、产生相同输出、收到相同梯度、做相同更新——永远无法区分。网络退化为等效于单个神经元的表达能力。必须用**随机初始化**打破对称性。

### Q2: Xavier 和 He 的核心区别是什么？

**A**: 两者都基于**方差守恒**原则，区别在于对激活函数的假设：
- **Xavier** 假设激活函数近似线性（适合 Sigmoid/Tanh），方差 $= 2/(n_{\text{in}} + n_{\text{out}})$
- **He** 考虑 ReLU 将一半激活值置零导致方差减半，额外乘以 2 补偿，方差 $= 2/n_{\text{in}}$

如果对 ReLU 网络用 Xavier，方差会每层减半，深层网络信号消失。

### Q3: Kaiming init 的 fan_in 和 fan_out 模式如何选择？

**A**: 
- **fan_in**（默认）：保证前向传播中激活值方差稳定。适合大多数场景
- **fan_out**：保证反向传播中梯度方差稳定。适用于网络宽度递减的情况（如分类头）

实践中 fan_in 最常用。PyTorch 默认 `kaiming_uniform_` with fan_in。

### Q4: 现代深度学习中初始化还重要吗？（有了 BN/LN 之后）

**A**: **仍然重要**，但影响降低了。

- **BatchNorm（Batch Normalization，批归一化）** / **LayerNorm（Layer Normalization，层归一化）** 在每层重新归一化激活值，部分缓解了初始化问题
- 但不良初始化仍会导致：训练初期不稳定、收敛速度慢、陷入较差的局部极小
- **Transformer** 通常使用 Xavier 或缩放后的正态分布（如 GPT 系列将残差分支缩放 $1/\sqrt{N}$）
- 预训练模型（**BERT（Bidirectional Encoder Representations from Transformers，双向编码器表示）**、**GPT（Generative Pre-trained Transformer，生成式预训练变换器）**）微调时，初始化来自预训练权重

### Q5: 卷积层的 fan_in 和 fan_out 怎么计算？

**A**: 对于 `Conv2d(C_in, C_out, kernel_size=K)`：
- $\text{fan\_in} = C_{\text{in}} \times K \times K$
- $\text{fan\_out} = C_{\text{out}} \times K \times K$

直觉：fan_in 是一个输出像素连接的输入参数数量（感受野大小 $\times$ 输入通道数）。

---

## 11. 实用初始化速查表

---

| 场景 | 推荐初始化 | PyTorch API |
|:---:|:---:|:---:|
| Linear + ReLU | He normal (fan_in) | `nn.init.kaiming_normal_(w, nonlinearity='relu')` |
| Linear + Leaky ReLU | He with alpha | `nn.init.kaiming_normal_(w, a=0.01, nonlinearity='leaky_relu')` |
| Linear + Tanh/Sigmoid | Xavier normal | `nn.init.xavier_normal_(w)` |
| Conv2d + ReLU | He normal | `nn.init.kaiming_normal_(w, nonlinearity='relu')` |
| RNN hidden-to-hidden | Orthogonal | `nn.init.orthogonal_(w)` |
| Transformer (GPT-style) | Xavier + 残差缩放 | `nn.init.normal_(w, std=0.02)` |
| ResNet without BN | Fixup | 手动缩放残差分支 |
| LoRA matrix A | Kaiming / Normal | `nn.init.kaiming_uniform_(A)` |
| LoRA matrix B | Zero | `nn.init.zeros_(B)` |
| Bias | Zero | `nn.init.zeros_(b)` |
| Embedding | Normal(0, 1) | `nn.init.normal_(emb.weight)` |

---

## 12. 关键公式汇总

---

| 方法 | 方差公式 | 推导核心假设 |
|:---:|:---:|:---:|
| Xavier (Normal) | $\text{Var}(w) = \frac{2}{n_{\text{in}} + n_{\text{out}}}$ | $f(x) \approx x$（线性近似），前向+反向折中 |
| Xavier (Uniform) | $W \sim U\left[-\sqrt{\frac{6}{n_{\text{in}}+n_{\text{out}}}}, \sqrt{\frac{6}{n_{\text{in}}+n_{\text{out}}}}\right]$ | 同上，均匀分布 $\text{Var} = a^2/3$ |
| He (Normal, fan_in) | $\text{Var}(w) = \frac{2}{n_{\text{in}}}$ | ReLU 将二阶矩减半，$\times 2$ 补偿 |
| He (Leaky ReLU) | $\text{Var}(w) = \frac{2}{(1+\alpha^2) \cdot n_{\text{in}}}$ | Leaky ReLU 负半轴有 $\alpha$ 斜率 |
| Orthogonal | $W^TW = I$（奇异值全为 1） | 范数保持：$\|Wx\| = \|x\|$ |


---

# T8: Optimizers 完整推导 + 从零实现

> 本节覆盖：SGD/Momentum/NAG/AdaGrad/RMSProp/Adam/AdamW 公式推导与直觉，从零 Python 实现（5种核心优化器），PyTorch API 验证与对比，Learning Rate Schedule（Warmup + Cosine Decay），LAMB/LARS 大批量训练，优化器选型决策树。
> 合并来源：Doc 17 E2 (Adam vs AdamW decoupled weight decay), Framework Node 74

---

## 1. 优化器的本质

---

### 1.1 为什么需要优化器？

神经网络训练的核心是最小化损失函数 $\mathcal{L}(\theta)$，其中 $\theta$ 是模型参数。由于损失函数通常非凸且高维，无法求解析解，必须用迭代方法逼近最优解。

**一阶泰勒展开**推导更新规则：

$$\mathcal{L}(\theta + \Delta\theta) \approx \mathcal{L}(\theta) + \nabla\mathcal{L}(\theta)^T \Delta\theta$$

在约束 $\|\Delta\theta\| \leq \eta$ 下，使上式最小的方向是负梯度方向：

$$\Delta\theta^* = -\eta \frac{\nabla\mathcal{L}}{\|\nabla\mathcal{L}\|}$$

简化为标准更新规则：

$$\theta_{t+1} = \theta_t - \eta \nabla\mathcal{L}(\theta_t)$$

### 1.2 优化器的演化路线

```
Vanilla SGD → +Momentum（加速收敛）→ +Nesterov（前瞻校正）
                                                  ↓
AdaGrad（参数自适应学习率）→ RMSProp（修复衰减）→ Adam（动量+自适应）→ AdamW（解耦衰减）
                                                                              ↓
                                                                    LAMB/LARS（大batch缩放）
```

两条主线：
- **动量线**：SGD $\rightarrow$ Momentum $\rightarrow$ NAG，关注梯度方向的一阶矩（均值）
- **自适应线**：AdaGrad $\rightarrow$ RMSProp $\rightarrow$ Adam，关注梯度大小的二阶矩（方差）

---

## 2. SGD 及 Momentum 系列

---

### 2.1 Vanilla SGD（随机梯度下降）

**更新规则**：

$$\theta_{t+1} = \theta_t - \eta g_t$$

其中 $g_t = \nabla\mathcal{L}(\theta_t)$（或 mini-batch 上的梯度估计）。

**问题**：
- 在狭长山谷中（条件数大），沿短轴振荡、沿长轴缓慢前进
- 鞍点处梯度近零，更新几乎停滞

### 2.2 SGD + Momentum（动量法）

引入速度变量 $v_t$ 积累历史梯度：

$$v_t = \beta v_{t-1} + g_t$$

$$\theta_{t+1} = \theta_t - \eta v_t$$

典型值 $\beta = 0.9$。

**物理直觉**：小球在损失曲面上滚动。$v_t$ 是速度，$\beta$ 是摩擦系数（$\beta = 0$ 无记忆，$\beta = 1$ 无摩擦）。

**为什么有效**：考虑椭圆形损失曲面——
- 长轴方向：梯度小但方向一致 $\rightarrow$ 动量累积加速
- 短轴方向：梯度大但方向振荡 $\rightarrow$ 正负抵消，减少振荡

**有效学习率分析**：当梯度恒定为 $g$ 时，$v_t$ 收敛到 $\frac{g}{1-\beta}$。实际步长放大 $\frac{1}{1-\beta}$ 倍（$\beta=0.9$ 时放大 10 倍）。

### 2.3 NAG（Nesterov Accelerated Gradient，Nesterov 加速梯度）

先按动量"前看"一步，再在前看位置计算梯度：

$$v_t = \beta v_{t-1} + \nabla\mathcal{L}(\theta_t - \eta\beta v_{t-1})$$

$$\theta_{t+1} = \theta_t - \eta v_t$$

**直觉**：Momentum 是"盲冲"，NAG 是"先探路再修正"。如果前看位置的梯度方向与动量不同，可以提前减速。

**理论优势**：对凸函数收敛率 $O(1/T^2)$，优于 Momentum 的 $O(1/T)$。

---

## 3. 自适应学习率系列

---

### 3.1 AdaGrad（Adaptive Gradient，自适应梯度）

为每个参数维护独立的学习率，基于历史梯度平方的累积：

$$G_{t,j} = \sum_{\tau=1}^{t} g_{\tau,j}^2$$

$$\theta_{t+1,j} = \theta_{t,j} - \frac{\eta}{\sqrt{G_{t,j} + \epsilon}} g_{t,j}$$

**直觉**：频繁更新的参数（大 $G_{t,j}$）学习率自动变小；稀少更新的参数保持较大学习率。非常适合稀疏数据（如 **NLP（Natural Language Processing，自然语言处理）** 中的词向量）。

**致命问题**：$G_{t,j}$ 单调递增 $\rightarrow$ 学习率持续下降 $\rightarrow$ 训练后期过早停止学习。

### 3.2 RMSProp（Root Mean Square Propagation，均方根传播）

用 **EMA（Exponential Moving Average，指数移动平均）** 替代累积和，解决 AdaGrad 的衰减问题：

$$v_t = \gamma v_{t-1} + (1-\gamma) g_t^2$$

$$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{v_t + \epsilon}} g_t$$

典型值 $\gamma = 0.9$，$\eta = 0.001$（Hinton 2012 Coursera 推荐）。

**为什么 EMA 修复了问题**：EMA 只关注近期梯度，遗忘久远的大梯度。等效窗口长度 $\approx \frac{1}{1-\gamma}$（$\gamma=0.9$ 时约看最近 10 步）。

**注意**：RMSProp 从未正式发表论文，仅来自 Hinton 的 Coursera 课程讲义。

### 3.3 Adam（Adaptive Moment Estimation，自适应矩估计）

结合 Momentum（一阶矩）和 RMSProp（二阶矩）：

**一阶矩（均值/方向）**：

$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$$

**二阶矩（方差/缩放）**：

$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$$

**Bias Correction（偏差校正）**：

$$\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t}$$

**参数更新**：

$$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t$$

**默认超参数**：$\beta_1 = 0.9$，$\beta_2 = 0.999$，$\epsilon = 10^{-8}$，$\eta = 0.001$

**为什么需要偏差校正？**

初始 $m_0 = v_0 = 0$。展开 $m_t$：

$$m_t = (1-\beta_1)\sum_{\tau=1}^{t} \beta_1^{t-\tau} g_\tau$$

取期望（假设 $g_\tau$ 同分布）：

$$\mathbb{E}[m_t] = \mathbb{E}[g] \cdot (1-\beta_1) \sum_{\tau=1}^{t} \beta_1^{t-\tau} = \mathbb{E}[g] \cdot (1-\beta_1^t)$$

因此 $\mathbb{E}[\hat{m}_t] = \frac{\mathbb{E}[m_t]}{1-\beta_1^t} = \mathbb{E}[g]$，消除偏差。

当 $t=1$ 时：$m_1 = (1-\beta_1)g_1$，不校正则只有 $0.1 g_1$；校正后 $\hat{m}_1 = g_1$。

### 3.4 AdamW（Decoupled Weight Decay，解耦权重衰减）

**问题**（来源：Loshchilov & Hutter 2019，合并自 Adobe Doc 17 E2）：

在标准 Adam 中使用 L2 正则化时：

$$\mathcal{L}' = \mathcal{L} + \frac{\lambda}{2}\|\theta\|^2 \implies g_t' = g_t + \lambda\theta_t$$

L2 梯度 $\lambda\theta_t$ 进入了 $m_t$ 和 $v_t$ 的计算，被自适应缩放 $\frac{1}{\sqrt{\hat{v}_t}+\epsilon}$ 调整。不同参数受到的正则化强度不同，这**不是**我们想要的。

**AdamW 修复**：将权重衰减从梯度中分离，直接作用于参数：

$$\theta_{t+1} = (1-\lambda\eta)\theta_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t$$

| | Adam + L2 | AdamW (decoupled) |
|---|---|---|
| 实现 | $g' = g + \lambda\theta$，衰减梯度进入 $m_t, v_t$ | 参数更新时直接减：$\theta \leftarrow (1-\lambda\eta)\theta$ |
| 问题 | 正则化强度被自适应 lr 调制，各参数不一致 | 解耦后正则化干净一致 |
| 现状 | 已过时 | **Transformer（变换器）** 训练标配 |

面试关键词：**decoupled weight decay**

---

## 4. 从零实现（纯 Python）

---

### 4.1 统一框架：目标函数

使用 Rosenbrock 函数作为测试目标（经典优化基准）：

$$f(x, y) = (a - x)^2 + b(y - x^2)^2$$

全局最小值在 $(a, b)=(1, 100)$ 时位于 $(1, 1)$。此函数有狭长弯曲的山谷，非常适合测试优化器。

```python
import numpy as np

def rosenbrock(params):
    """Rosenbrock function: f(x,y) = (1-x)^2 + 100*(y-x^2)^2"""
    x, y = params
    return (1 - x)**2 + 100 * (y - x**2)**2

def rosenbrock_grad(params):
    """Gradient of Rosenbrock function"""
    x, y = params
    dx = -2 * (1 - x) + 200 * (y - x**2) * (-2 * x)
    dy = 200 * (y - x**2)
    return np.array([dx, dy])
```

### 4.2-4.6 五种优化器从零实现

> 所有优化器共享同一循环骨架，仅**状态变量初始化**和**更新逻辑**不同：

```python
# === SHARED SKELETON ===
def optimizer_template(grad_fn, params_init, n_steps, **config):
    params = np.array(params_init, dtype=np.float64)
    # ... initialize state variables ...
    history = []
    for t in range(1, n_steps + 1):
        g = grad_fn(params)
        # ... algorithm-specific update ...
        history.append(params.copy())
    return params, history
```

**各优化器核心更新逻辑**（仅列出与骨架不同的部分）：

```python
# === 4.2 SGD + Momentum ===
# State: v = zeros_like(params)
# Update:
v = beta * v + g
params = params - lr * v

# === 4.3 AdaGrad ===
# State: G = zeros_like(params)  (cumulative squared gradients)
# Update:
G += g ** 2
params = params - lr / np.sqrt(G + eps) * g

# === 4.4 RMSProp ===
# State: v = zeros_like(params)  (EMA of squared gradients)
# Update:
v = gamma * v + (1 - gamma) * g ** 2
params = params - lr / np.sqrt(v + eps) * g

# === 4.5 Adam ===
# State: m, v = zeros_like(params)  (1st & 2nd moment)
# Update (note: loop starts at t=1 for bias correction):
m = beta1 * m + (1 - beta1) * g
v = beta2 * v + (1 - beta2) * g ** 2
m_hat = m / (1 - beta1 ** t)           # bias correction
v_hat = v / (1 - beta2 ** t)           # bias correction
params = params - lr * m_hat / (np.sqrt(v_hat) + eps)

# === 4.6 AdamW (decoupled weight decay) ===
# State: m, v = zeros_like(params)
# Update (KEY: weight decay NOT in gradient):
m = beta1 * m + (1 - beta1) * g        # g is clean, no lambda*theta
v = beta2 * v + (1 - beta2) * g ** 2
m_hat = m / (1 - beta1 ** t)
v_hat = v / (1 - beta2 ** t)
params = (1 - lr * weight_decay) * params \
         - lr * m_hat / (np.sqrt(v_hat) + eps)
```

<details>
<summary>完整可运行实现（点击展开）</summary>

```python
def sgd_momentum(grad_fn, params_init, lr=0.001, beta=0.9, n_steps=5000):
    params = np.array(params_init, dtype=np.float64)
    v = np.zeros_like(params)
    history = []
    for t in range(n_steps):
        g = grad_fn(params)
        v = beta * v + g
        params = params - lr * v
        history.append(params.copy())
    return params, history

def adagrad(grad_fn, params_init, lr=0.01, eps=1e-8, n_steps=5000):
    params = np.array(params_init, dtype=np.float64)
    G = np.zeros_like(params)
    history = []
    for t in range(n_steps):
        g = grad_fn(params)
        G += g ** 2
        params = params - lr / np.sqrt(G + eps) * g
        history.append(params.copy())
    return params, history

def rmsprop(grad_fn, params_init, lr=0.001, gamma=0.9, eps=1e-8, n_steps=5000):
    params = np.array(params_init, dtype=np.float64)
    v = np.zeros_like(params)
    history = []
    for t in range(n_steps):
        g = grad_fn(params)
        v = gamma * v + (1 - gamma) * g ** 2
        params = params - lr / np.sqrt(v + eps) * g
        history.append(params.copy())
    return params, history

def adam(grad_fn, params_init, lr=0.001, beta1=0.9, beta2=0.999,
         eps=1e-8, n_steps=5000):
    params = np.array(params_init, dtype=np.float64)
    m = np.zeros_like(params)
    v = np.zeros_like(params)
    history = []
    for t in range(1, n_steps + 1):
        g = grad_fn(params)
        m = beta1 * m + (1 - beta1) * g
        v = beta2 * v + (1 - beta2) * g ** 2
        m_hat = m / (1 - beta1 ** t)
        v_hat = v / (1 - beta2 ** t)
        params = params - lr * m_hat / (np.sqrt(v_hat) + eps)
        history.append(params.copy())
    return params, history

def adamw(grad_fn, params_init, lr=0.001, beta1=0.9, beta2=0.999,
          eps=1e-8, weight_decay=0.01, n_steps=5000):
    params = np.array(params_init, dtype=np.float64)
    m = np.zeros_like(params)
    v = np.zeros_like(params)
    history = []
    for t in range(1, n_steps + 1):
        g = grad_fn(params)
        m = beta1 * m + (1 - beta1) * g
        v = beta2 * v + (1 - beta2) * g ** 2
        m_hat = m / (1 - beta1 ** t)
        v_hat = v / (1 - beta2 ** t)
        params = (1 - lr * weight_decay) * params \
                 - lr * m_hat / (np.sqrt(v_hat) + eps)
        history.append(params.copy())
    return params, history
```

</details>

---

## 5. 运行比较：5 种优化器在 Rosenbrock 函数上的表现

---

```python
import numpy as np

# ---- Objective: Rosenbrock ----
def rosenbrock(p):
    x, y = p
    return (1 - x)**2 + 100 * (y - x**2)**2

def rosenbrock_grad(p):
    x, y = p
    return np.array([-2*(1-x) - 400*x*(y - x**2), 200*(y - x**2)])

# ---- Optimizers (from Section 4) ----
def run_optimizer(name, opt_fn, kwargs, start, n_steps=10000):
    params, history = opt_fn(rosenbrock_grad, start, n_steps=n_steps, **kwargs)
    final_loss = rosenbrock(params)
    dist = np.linalg.norm(params - np.array([1.0, 1.0]))
    print(f"{name:20s} | final=({params[0]:.6f}, {params[1]:.6f}) | "
          f"loss={final_loss:.2e} | dist_to_opt={dist:.2e}")
    return params, history

start = np.array([-1.0, 1.0])
n = 10000

print(f"{'Optimizer':20s} | {'Final params':30s} | {'Loss':10s} | Distance")
print("-" * 85)
run_optimizer("SGD (no momentum)", sgd_momentum, dict(lr=0.0001, beta=0.0), start, n)
run_optimizer("SGD + Momentum",    sgd_momentum, dict(lr=0.0001, beta=0.9), start, n)
run_optimizer("AdaGrad",           adagrad,       dict(lr=0.1),              start, n)
run_optimizer("RMSProp",           rmsprop,       dict(lr=0.001, gamma=0.9), start, n)
run_optimizer("Adam",              adam,           dict(lr=0.001),            start, n)
```

**预期输出**（具体数值因浮点略异）：

```
Optimizer            | Final params                   | Loss       | Distance
-------------------------------------------------------------------------------------
SGD (no momentum)    | final=(0.363444, 0.129058) | loss=4.06e-01 | dist_to_opt=1.08e+00
SGD + Momentum       | final=(0.992607, 0.985238) | loss=5.47e-05 | dist_to_opt=1.65e-02
AdaGrad              | final=(0.999430, 0.998858) | loss=3.25e-07 | dist_to_opt=1.28e-03
RMSProp              | final=(1.000316, 0.999133) | loss=2.25e-04 | dist_to_opt=9.23e-04
Adam                 | final=(1.000000, 0.999999) | loss=2.80e-11 | dist_to_opt=1.22e-06
```

**观察**：
- Vanilla SGD（lr=0.0001）在 10K 步内远未收敛——Rosenbrock 的狭长山谷需要更多迭代或更大学习率
- Momentum 加速约 4 个数量级（loss 从 0.4 降到 5e-5）
- Adam 收敛最精确（loss $\sim 10^{-11}$），因为自适应学习率能处理 Rosenbrock 的各向异性
- AdaGrad 表现不错但学习率持续衰减限制了最终精度

---

## 6. PyTorch API 验证

---

```python
import torch
import torch.nn as nn

# Simple 2-layer network for demonstration
class TwoLayerNet(nn.Module):
    def __init__(self, d_in=10, d_hidden=50, d_out=1):
        super().__init__()
        self.fc1 = nn.Linear(d_in, d_hidden)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(d_hidden, d_out)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

# Generate synthetic regression data
torch.manual_seed(42)
X = torch.randn(200, 10)
y = X[:, 0] * 2 + X[:, 1] * (-1) + 0.5 * torch.randn(200)
y = y.unsqueeze(1)

def train(optimizer_cls, opt_kwargs, epochs=200):
    """Train and return final loss for comparison."""
    torch.manual_seed(42)
    model = TwoLayerNet()
    criterion = nn.MSELoss()
    optimizer = optimizer_cls(model.parameters(), **opt_kwargs)

    losses = []
    for epoch in range(epochs):
        pred = model(X)
        loss = criterion(pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        losses.append(loss.item())

    return losses[-1], losses

# ---- Compare 5 optimizers ----
configs = [
    ("SGD",          torch.optim.SGD,    dict(lr=0.01)),
    ("SGD+Momentum", torch.optim.SGD,    dict(lr=0.01, momentum=0.9)),
    ("AdaGrad",      torch.optim.Adagrad,dict(lr=0.01)),
    ("RMSProp",      torch.optim.RMSprop,dict(lr=0.001)),
    ("Adam",         torch.optim.Adam,   dict(lr=0.001)),
    ("AdamW",        torch.optim.AdamW,  dict(lr=0.001, weight_decay=0.01)),
]

print(f"{'Optimizer':15s} | Final MSE Loss")
print("-" * 35)
for name, cls, kwargs in configs:
    final_loss, _ = train(cls, kwargs)
    print(f"{name:15s} | {final_loss:.6f}")
```

**预期输出**：

```
Optimizer       | Final MSE Loss
-----------------------------------
SGD             | 0.287432
SGD+Momentum    | 0.254891
AdaGrad         | 0.260143
RMSProp         | 0.247856
Adam            | 0.248012
AdamW           | 0.249301
```

### 6.1 PyTorch 常用 API 速查

```python
# SGD with momentum + weight decay (L2)
optimizer = torch.optim.SGD(
    model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4,
    nesterov=True  # enable NAG
)

# Adam (default hyperparams work well)
optimizer = torch.optim.Adam(
    model.parameters(), lr=1e-3, betas=(0.9, 0.999), eps=1e-8
)

# AdamW (standard for Transformers)
optimizer = torch.optim.AdamW(
    model.parameters(), lr=1e-3, weight_decay=0.01
)

# Gradient clipping (before optimizer.step())
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Per-parameter group (different lr for backbone vs head)
optimizer = torch.optim.AdamW([
    {"params": model.backbone.parameters(), "lr": 1e-5},
    {"params": model.head.parameters(),     "lr": 1e-3},
], weight_decay=0.01)
```

---

## 7. Learning Rate Schedule（学习率调度）

---

### 7.1 为什么需要调度？

固定学习率的两难：
- 太大 $\rightarrow$ 训练后期在最优值附近振荡，无法精确收敛
- 太小 $\rightarrow$ 训练前期收敛极慢

**解决方案**：动态调整 $\eta_t$，前期大步探索，后期小步精修。

### 7.2 常见调度策略

| 策略 | 公式 | 适用场景 |
|:---:|:---:|:---:|
| Step Decay | $\eta_t = \eta_0 \cdot \gamma^{\lfloor t/S \rfloor}$ | 经典 CNN（每 30 epoch 衰减 0.1） |
| Cosine Annealing | $\eta_t = \eta_{\min} + \frac{1}{2}(\eta_0 - \eta_{\min})(1 + \cos\frac{\pi t}{T})$ | 现代训练标配 |
| Linear Warmup | $\eta_t = \eta_0 \cdot \frac{t}{T_{\text{warmup}}}$ | Transformer 前 $T_{\text{warmup}}$ 步 |
| Warmup + Cosine | 先线性 warmup 再 cosine decay | **LLM（Large Language Model，大语言模型）** 训练标准 |

### 7.3 Warmup + Cosine Decay 实现

```python
import math

def warmup_cosine_lr(step, total_steps, warmup_steps, max_lr, min_lr=0.0):
    """
    Warmup + Cosine Annealing learning rate schedule.

    Phase 1 (step < warmup_steps): linear warmup from 0 to max_lr
    Phase 2 (step >= warmup_steps): cosine decay from max_lr to min_lr

    Used by: GPT-3, LLaMA, most modern LLM training

    Args:
        step: current training step
        total_steps: total number of training steps
        warmup_steps: number of warmup steps
        max_lr: peak learning rate
        min_lr: minimum learning rate at end of cosine decay

    Returns:
        learning rate for this step
    """
    if step < warmup_steps:
        # Linear warmup
        return max_lr * step / warmup_steps
    else:
        # Cosine decay
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * progress))


# Demo: print schedule for 1000 steps with 100 warmup
total, warmup, peak = 1000, 100, 1e-3
checkpoints = [0, 50, 100, 250, 500, 750, 999]
print("Step | Learning Rate")
print("-" * 25)
for s in checkpoints:
    lr = warmup_cosine_lr(s, total, warmup, peak, min_lr=1e-5)
    print(f"{s:4d} | {lr:.6f}")
```

**预期输出**：

```
Step | Learning Rate
-------------------------
   0 | 0.000000
  50 | 0.000500
 100 | 0.001000
 250 | 0.000934
 500 | 0.000591
 750 | 0.000187
 999 | 0.000010
```

### 7.4 PyTorch LR Scheduler API

```python
from torch.optim.lr_scheduler import CosineAnnealingLR, LinearLR, SequentialLR

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

# Warmup + Cosine in PyTorch
warmup_scheduler = LinearLR(optimizer, start_factor=0.01, total_iters=100)
cosine_scheduler = CosineAnnealingLR(optimizer, T_max=900, eta_min=1e-5)
scheduler = SequentialLR(optimizer, [warmup_scheduler, cosine_scheduler], milestones=[100])

# In training loop:
# for epoch in range(epochs):
#     train_one_epoch(...)
#     scheduler.step()
```

---

## 8. LAMB/LARS：大批量训练优化器

---

### 8.1 为什么大 batch 需要特殊处理？

大 batch 训练的核心问题：不同层的参数范数和梯度范数差异巨大。统一学习率导致某些层更新过大（发散）或过小（停滞）。

**Linear Scaling Rule（线性缩放规则）**：$\eta \propto B$（batch size 翻倍，学习率翻倍），但仅在一定范围内有效。

### 8.2 LARS（Layer-wise Adaptive Rate Scaling，层级自适应速率缩放）

$$\eta_l = \eta \cdot \frac{\|w_l\|}{\|\nabla\mathcal{L}(w_l)\| + \lambda\|w_l\|}$$

为每层独立计算学习率缩放因子 $\frac{\|w_l\|}{\|g_l\|}$（参数范数与梯度范数之比）。

**直觉**：参数大但梯度小的层 $\rightarrow$ 大步更新；参数小但梯度大的层 $\rightarrow$ 小步更新。

### 8.3 LAMB（Layer-wise Adaptive Moments optimizer for Batch training）

$$r_t = \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} + \lambda w_t$$

$$w_{t+1} = w_t - \eta \cdot \frac{\|w_t\|}{\|r_t\|} \cdot r_t$$

LAMB = Adam + 层级自适应缩放。用于大 batch 预训练（如 BERT 预训练用 batch size = 65536）。

---

## 9. Gradient Clipping（梯度裁剪）

> 详细原理和纯 Python 实现见 T1 Section 6。此处仅列要点。

- **按范数裁剪**（推荐）：$g \leftarrow g \cdot \min(1, \theta/\|g\|)$，保持方向，RNN/Transformer 标配
- **按值裁剪**：逐元素 $\text{clip}(g_j, -\theta, \theta)$，可能改变方向
- PyTorch: `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)`

---

## 10. 优化器对比总表

---

| 优化器 | 一阶矩 | 二阶矩 | 偏差校正 | 适用场景 | 关键超参数 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| SGD | - | - | - | 基线对照 | $\eta$ |
| SGD+Momentum | EMA | - | - | 经典 CNN 训练 | $\eta, \beta$ |
| NAG | EMA(前瞻) | - | - | 需要更快凸收敛 | $\eta, \beta$ |
| AdaGrad | - | 累积和 | - | 稀疏数据/NLP | $\eta$ |
| RMSProp | - | EMA | - | RNN 训练 | $\eta, \gamma$ |
| Adam | EMA | EMA | 是 | 通用快速收敛 | $\eta, \beta_1, \beta_2$ |
| AdamW | EMA | EMA | 是 | Transformer 标配 | $\eta, \beta_1, \beta_2, \lambda$ |
| LAMB | EMA | EMA | 是 | 大 batch 预训练 | $\eta, \lambda$ |

---

## 11. SGD vs Adam 之争

---

一个高频面试话题：

| 维度 | SGD + Momentum | Adam/AdamW |
|:---:|:---:|:---:|
| 收敛速度 | 慢，需要精心调参 | 快，默认参数就能用 |
| 泛化性能 | 充分调参后可能更好 | 有时收敛到尖锐极小值 |
| 超参敏感性 | 高（$\eta$ 必须精调） | 低（默认值通常够用） |
| 内存开销 | 低（仅存 $v$） | 高（存 $m$ 和 $v$，参数量 $\times 2$） |
| 典型领域 | CV 竞赛/需要极致性能 | NLP/Transformer/快速原型 |

**现代共识**：
- 快速原型 / NLP / Transformer $\rightarrow$ **AdamW**
- 计算机视觉竞赛 / 极致性能 $\rightarrow$ SGD + Momentum + 精心调参
- 预训练大模型 $\rightarrow$ AdamW（甚至 LAMB/LARS 用于超大 batch）
- SGD 找到 **Flat Minima（平坦极小值）** 泛化更好的假说有理论支持（**SAM（Sharpness-Aware Minimization，锐度感知最小化）** 进一步证实）

---

## 12. 面试 Q&A

---

### Q1: 逐步解释 Adam 的工作原理？$m_t$ 和 $v_t$ 分别代表什么？

**A**: Adam 维护两个 EMA：
- $m_t$：梯度的一阶矩（均值），提供**方向**信息，等价于 Momentum
- $v_t$：梯度平方的二阶矩（未中心化方差），提供**缩放**信息，等价于 RMSProp

偏差校正 $\hat{m}_t = m_t/(1-\beta_1^t)$ 消除零初始化带来的初始偏差。更新公式 $\theta \leftarrow \theta - \eta\hat{m}_t/(\sqrt{\hat{v}_t}+\epsilon)$ 结合方向和自适应步长。

### Q2: AdamW 为什么修复了 Adam 的权重衰减问题？

**A**: Adam + L2 中，权重衰减梯度 $\lambda\theta$ 进入 $m_t$ 和 $v_t$，被自适应缩放 $1/\sqrt{\hat{v}_t}$ 调制。结果：频繁更新的参数（大 $\hat{v}_t$）受到更弱的正则化，这不是我们想要的均匀正则化。AdamW 将权重衰减直接从参数中减去：$\theta \leftarrow (1-\lambda\eta)\theta - \eta\hat{m}_t/(\sqrt{\hat{v}_t}+\epsilon)$，正则化强度不受自适应缩放影响。

### Q3: 何时选 SGD + Momentum 而非 Adam？

**A**: 当有充足计算资源调参时。SGD 在 CV 任务（ResNet、ImageNet）上充分调参后泛化性能可能更好，因为 SGD 更倾向于收敛到平坦极小值。实际工程中，如果项目周期紧或不确定最优超参，Adam/AdamW 是更稳妥的选择。

### Q4: 偏差校正在什么情况下重要？

**A**: 在训练早期（$t$ 小时）最重要。$\beta_2 = 0.999$ 意味着前 $\sim 1000$ 步 $v_t$ 严重偏小（$1-0.999^{100} \approx 0.095$），不校正会导致分母过小、步长过大。随着 $t$ 增大，$\beta^t \to 0$，校正因子趋近 1，影响消失。

### Q5: 什么是 Learning Rate Warmup？为什么 Transformer 需要它？

**A**: Warmup 是在训练初始阶段逐步增大学习率（通常从 0 线性增到目标值）。Transformer 需要 warmup 因为：(1) 初始权重随机，前几步梯度方向不可靠，大学习率会导致训练不稳定；(2) Adam 的 $v_t$ 估计在早期不准确，偏差校正虽有帮助但大 $\eta$ 仍可能 overshoot；(3) Layer Norm 在初始阶段的梯度尺度不稳定。典型设置：warmup 占总步数的 1-5%。

---

## 13. 优化器选型决策树

---

```
需要优化器 →
  ├─ Transformer / NLP / LLM?
  │   └─ AdamW + Warmup + Cosine Decay (标准配置)
  │       └─ 超大 batch (>4K)? → 加 LAMB/LARS
  ├─ CV 竞赛 / 需要极致泛化?
  │   └─ SGD + Momentum(0.9) + Step/Cosine LR Decay
  ├─ 稀疏特征 / 推荐系统?
  │   └─ AdaGrad 或 Adam
  ├─ RNN / 序列模型?
  │   └─ RMSProp 或 Adam + Gradient Clipping
  └─ 快速原型 / 不确定?
      └─ Adam(lr=1e-3) — 通用默认选择
```

---

## 14. 关键公式汇总

---

| 优化器 | 核心更新公式 | 关键特性 |
|:---:|:---:|:---:|
| SGD | $\theta \leftarrow \theta - \eta g$ | 最简单，无状态 |
| Momentum | $v \leftarrow \beta v + g;\; \theta \leftarrow \theta - \eta v$ | 加速收敛，抑制振荡 |
| NAG | 在 $\theta - \eta\beta v$ 处计算梯度 | 前瞻校正，凸收敛 $O(1/T^2)$ |
| AdaGrad | $G \leftarrow G + g^2;\; \theta \leftarrow \theta - \frac{\eta}{\sqrt{G+\epsilon}}g$ | 参数自适应，适合稀疏 |
| RMSProp | $v \leftarrow \gamma v + (1-\gamma)g^2;\; \theta \leftarrow \theta - \frac{\eta}{\sqrt{v+\epsilon}}g$ | EMA 替代累积，解决衰减 |
| Adam | $m, v$ 的 EMA + 偏差校正 | 最通用的自适应优化器 |
| AdamW | Adam + 解耦 $\theta \leftarrow (1-\lambda\eta)\theta$ | Transformer 标配 |
