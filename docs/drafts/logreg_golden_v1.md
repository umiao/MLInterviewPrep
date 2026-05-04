# Logistic Regression (Sigmoid + Stable BCE + GD)

## TL;DR

二分类 GLM, 单样本 $z = w^\top x + b$ (logit), $p = \sigma(z) = 1/(1 + e^{-z})$. Bernoulli MLE 等价最小化 BCE. **核心三步**: (1) 前向 $z = Xw + b\mathbf{1}$, $p = \sigma(z)$; (2) sigmoid + CE "漂亮消去" 给出 $\nabla_w L = \frac{1}{n} X^\top (p - y)$ — 与 Linear Regression MSE 同形 (GLM 框架); (3) full-batch GD 直到 loss 收敛. 凸优化 (Hessian $\frac{1}{n} X^\top \mathrm{diag}(p(1-p)) X \succeq 0$), 但**无闭式解** (sigmoid 把似然变非二次). 复杂度: GD 单步 $O(nd)$; Newton/IRLS 单步 $O(nd^2 + d^3)$. 工业灵魂在拓展 A: logits-space stable BCE $L = \max(z, 0) - zy + \log(1 + e^{-|z|})$ — 防 $\log(0)$ 的标准把戏.

---

## 推导 — sigmoid + CE 的"漂亮消去"

单样本 logit $z = w^\top x + b$, 预测 $p = \sigma(z)$. Bernoulli 似然 $p^y (1-p)^{1-y}$ 取负对数得 BCE:

$$\ell(w, b) = -y \log p - (1 - y) \log(1 - p)$$

链式求 $\partial \ell / \partial w$, 用恒等式 $\sigma'(z) = p(1 - p)$:

$$\frac{\partial \ell}{\partial w} = \underbrace{\left(-\frac{y}{p} + \frac{1 - y}{1 - p}\right)}_{\partial \ell / \partial p} \cdot \underbrace{p(1 - p)}_{\partial p / \partial z} \cdot \underbrace{x}_{\partial z / \partial w}$$

前两段直接合并: $-y(1-p) + (1-y)p = p - y$. 整段塌缩到

$$\boxed{\nabla_w \ell = (p - y)\, x, \quad \frac{\partial \ell}{\partial b} = p - y}$$

这是 sigmoid 与 log 的共轭关系: $\sigma'$ 的 $p(1-p)$ 被 $\partial \ell / \partial p$ 里的 $1/p$, $1/(1-p)$ 精确抵消, 留下"残差 × 输入"的干净形式. MSE + sigmoid 没这个性质 — $\sigma'$ 不消, 大 $|z|$ 处梯度 $\propto p(1-p) \to 0$, 错得越离谱学得越慢.

**Batch 形式 (GLM 框架)**: 把 $n$ 个样本堆成 $X \in \mathbb{R}^{n \times d}$, $z = Xw + b\mathbf{1} \in \mathbb{R}^n$, $p = \sigma(z)$. 全局损失 $L = \frac{1}{n} \sum_i \ell_i$ 的梯度

$$\nabla_w L = \frac{1}{n} X^\top (p - y), \qquad \frac{\partial L}{\partial b} = \frac{1}{n} \mathbf{1}^\top (p - y)$$

与 Linear Regression 的 $\nabla_w L_{\text{MSE}} = \frac{2}{n} X^\top (\hat y - y)$ **完全同构** — $X^\top$ 把 $n$ 维残差投回 $d$ 维参数空间, 只换 link function ($\sigma$ vs identity). 这就是 GLM (Generalized Linear Model) 的统一形态: Linear / Logistic / Poisson 共享 $X^\top \cdot \text{residual}$ 的梯度模式.

> **记号约定**: 单样本用 $w^\top x$ (列向量内积, 与 fundamentals / 教科书一致); batch 用 $Xw$ ($X$ 是 $n \times d$ 行堆, numpy `X @ w`). 不混用 $wx$ — 在 row-vector 约定下成立但与本项目列向量约定冲突.

---

## 实现

### 0. Class skeleton

```python
import numpy as np
from typing import Optional

class LogisticRegression:
    def __init__(self, learning_rate: float = 1e-1,
                 max_iterations: int = 1000,
                 convergence_threshold: float = 1e-6,
                 l2_lambda: float = 0.0,
                 fit_intercept: bool = True):
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.l2_lambda = l2_lambda
        self.fit_intercept = fit_intercept
        self.coef_: Optional[np.ndarray] = None         # (d,)
        self.intercept_: float = 0.0                    # scalar
        self.training_loss_history: list[float] = []    # per-iter BCE
```

### 1. Sigmoid (vanilla)

教科书形式 $1 / (1 + e^{-z})$ 直接写. 大负 $z$ 时 $e^{-z}$ 上溢 `inf` → 结果 `0.0` (sigmoid 真值确实近 0, 但下游 BCE 的 $\log(0)$ 才是火药 — 拓展 A 集中处理). 数值改进版按 $z$ 符号分支让 `exp` arg 永远 $\leq 0$, 与拓展 A / softmax LSE 同源.

```python
@staticmethod
def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))                   # (n,)
```

### 2. BCE loss (vanilla)

照搬 per-sample $-[y \log p + (1-y) \log(1-p)]$, mean over batch. $\varepsilon$-clip 是 textbook 防御 (`log(0)` → `log(eps)` 不爆 `nan`), 但大 $|z|$ 时梯度仍偏离真值; 工业用 logits-space 形式 (拓展 A).

```python
@staticmethod
def _bce_loss(p, y):
    # p: (n,) in (0, 1), y: (n,) in {0, 1}
    eps = 1e-12                                       # clip 防 log(0); 真正解法见拓展 A
    p = np.clip(p, eps, 1 - eps)
    per_sample = -(y * np.log(p) + (1 - y) * np.log(1 - p))   # (n,)
    return float(per_sample.mean())                   # scalar
```

### 3. fit — full-batch GD with optional L2

NN-style: `w` / `b` 是两个独立参数, 各算各的梯度 (`grad_w`, `grad_b`) 各自 update — 上方推导给出 $\nabla_w \ell = (p - y) x$ 与 $\partial \ell / \partial b = p - y$, 实现照搬. L2 仅作用在 `w`, `b` 永不参与 (augment-bias 反模式见 Takeaway / cheat-sheet).

```python
def fit(self, X, y):
    # X: (n, d), y: (n,) in {0, 1}
    n, d = X.shape
    w = np.zeros(d)                                        # (d,)
    b = 0.0                                                # scalar
    previous_loss = float("inf")
    self.training_loss_history = []

    for _ in range(self.max_iterations):                   # Criterion 1: max iter
        z = X @ w + b                                      # (n,)
        p = self._sigmoid(z)                               # (n,)
        residual = p - y                                   # (n,)  prediction residual
        grad_w = (X.T @ residual) / n                      # (d,)
        if self.l2_lambda > 0.0:
            grad_w = grad_w + 2.0 * self.l2_lambda * w     # L2 only on w, never on b
        w = w - self.learning_rate * grad_w                # (d,)
        if self.fit_intercept:
            grad_b = float(residual.mean())                # scalar
            b = b - self.learning_rate * grad_b            # scalar

        current_loss = self._bce_loss(p, y)
        self.training_loss_history.append(current_loss)
        # Criterion 2: loss change below tol
        if abs(previous_loss - current_loss) < self.convergence_threshold:
            break
        previous_loss = current_loss

    self.coef_, self.intercept_ = w, b
    return self
```

**Takeaway**: `w` / `b` 各算各梯度各自 update — NN 训练循环的通用范式 (一层 affine + bias). LR 闭式解里"拼一列 1 折成 $w_0$"是 lstsq 专属技巧 (一次只解一个 $Ax = b$); LogReg 无闭式解 (sigmoid 让 NLL 非二次), 一开始就该 NN-style — 把 augment-bias 移植到 GD / LogReg / NN 是 anti-pattern.

### 4. predict / predict_proba

`predict_proba` 给概率, `predict` 用阈值 (默认 0.5) 切硬标签. **调阈值**是应对 class imbalance 的第一招 (不动模型即可).

```python
def predict_proba(self, X):
    # X: (m, d)
    z = X @ self.coef_ + self.intercept_              # (m,)
    return self._sigmoid(z)                            # (m,)

def predict(self, X, threshold: float = 0.5):
    return (self.predict_proba(X) >= threshold).astype(int)   # (m,)
```

---

## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 200, 4
X = np.random.randn(N, D)
y = (X @ np.random.randn(D) > 0).astype(int)
lr = LogisticRegression().fit(X, y)
preds = lr.predict(X)
probs = lr.predict_proba(X)
assert preds.shape == (N,)
assert probs.shape == (N,)
print(f"Train accuracy = {(preds == y).mean():.3f}")
```

---

## 面试追问 (Cheat Sheet)

> **Q: 为什么 LR 没有闭式解?**

- Sigmoid 让对数似然变成关于 $w$ 的非二次函数, 一阶条件 $X^\top(\sigma(Xw) - y) = 0$ 不能 algebraic 解出 $w$.
- LR 仍是凸 (Hessian $\frac{1}{n} X^\top \mathrm{diag}(p(1-p)) X \succeq 0$), GD / Newton / L-BFGS 都全局收敛 — 没闭式不代表难解.
- 对比: Linear Regression 损失二次, 一阶条件线性, $\hat w = (X^\top X)^{-1} X^\top y$ 即 closed-form.

> **Q: Bias 应该怎么处理? 为什么不学 LR 闭式那种 augment 一列 1?**

- **GD 路径 (LogReg / NN 通用)**: `w` / `b` 两个独立参数, `grad_w = X^T(p-y)/n`, `grad_b = mean(p-y)`, 各自 update — Section 3 即此范式.
- **augment 一列 1 折 $w_0$** 是 LR **闭式解**专属 (`lstsq` 一次解一个 $Ax = b$, 拼列让 lstsq 同时吃 bias). LogReg 无闭式解, 这个 trick 在 LogReg 上**无任何合法用途**; 移植到 NN 更是 anti-pattern — 失去 freeze / warm-start bias 的独立控制, 而 NN 训练循环正建立在"每参数独立 grad / 独立 step"原语上.
- **L2 不作用到 bias** (`grad_w += 2λw`, `grad_b` 纯残差均值): 等价于 $\lambda \mathrm{diag}([0,1,\dots,1]) w$, bias 整体平移自由度不该被惩罚.

> **Q: 为什么用 BCE 不用 MSE?**

- **凸性**: BCE + sigmoid 凸; MSE + sigmoid 非凸 (有多个 local minima).
- **梯度饱和**: MSE 梯度 $= (\hat y - y)\, p(1-p)\, x$, 大 $|z|$ 处 $p(1-p) \to 0$ — 错得越离谱学得越慢; BCE 把 $p(1-p)$ 消掉留 $(p-y) x$, 错得越离谱越饱满.
- **概率解释**: BCE 是 Bernoulli MLE; MSE 对应 Gaussian noise, 二分类上属于模型误设.

> **Q: Softmax 多分类怎么扩展?**

- $p_k = e^{z_k} / \sum_j e^{z_j}$, 损失 $L = -\frac{1}{n} \sum_i \sum_k y_{ik} \log p_{ik}$ ($Y$ one-hot).
- 梯度 $\nabla_W L = \frac{1}{n} X^\top (P - Y)$ — 与二分类**完全同构**, $W$ 升到 $(d, K)$.
- Stable softmax: 减 $\max_j z_j$ 再 exp (与拓展 A 的 $|z|$ 同源 LSE trick).

> **Q: Newton / IRLS 与 GD 的关系?**

- Newton: $w \leftarrow w - H^{-1} \nabla L$, $H = \frac{1}{n} X^\top \mathrm{diag}(p(1-p)) X$, 二阶收敛.
- IRLS = Newton 在 LR 上的具体形式 (每步解 weighted least squares).
- 代价 $O(nd^2 + d^3)$; $d \geq 10^4$ 退到 GD; **L-BFGS** 是常见折中 (sklearn 默认).

> **Q: 类别不平衡怎么办?**

- **调阈值** (训练不变, predict 时把 0.5 降到 ROC 上 recall/precision 平衡处) — 单这一步解决大多数实际问题.
- **class weight / pos_weight**: BCE 给正样本乘 $\beta = $ neg/pos 比例.
- **Focal loss** $-(1 - p_t)^\gamma \log p_t$ 对易分样本降权, $\gamma = 2$ (RetinaNet 标配).

> **Q: L1 vs L2 正则的几何含义?**

- **L2 (Ridge)**: $+\lambda \|w\|_2^2$, 梯度 $+2\lambda w$; Gaussian prior, 各 $w_j$ shrinkage 但**不为 0**.
- **L1 (Lasso)**: $+\lambda \|w\|_1$, 次梯度 $\lambda \mathrm{sign}(w)$; Laplace prior, **稀疏解** (自带特征选择).
- 几何: L2 等高线圆 (各方向 shrink); L1 菱形 (顶点在轴上 $\Rightarrow$ 解落在轴上 = 稀疏).

> **Q: Calibration — 输出 $p$ 是真概率吗?**

- LR 在 BCE 训练下**理论上 calibrated**, class imbalance / 强正则可能偏离.
- 检查: **reliability diagram** (predict_proba 分箱, 完美应贴对角线).
- **Platt scaling**: 验证集再训 $P_{\text{cal}} = \sigma(a z + b)$; **Isotonic** 更灵活但需 >1000 验证样本.

> **Q: SGD vs full-batch GD?**

- Full-batch: 梯度无偏方差 0, $n$ 大单步装不下. SGD / mini-batch (32-256): 方差大但 GPU SIMD 友好, 噪声跳鞍点 (LR 凸不重要, NN 关键).
- LR 凸, 三者最终都收敛同一全局最优, 只差路径.

---

## 拓展

### A. 数值稳定性 — logits-space stable BCE (这道题的工业灵魂)

**朴素 BCE 的两路爆炸**: $L = -[y \log p + (1-y) \log(1-p)]$ 中, $z \to +\infty$ 时 $p \to 1$, $1 - p$ 触底 `0.0`, $\log(1 - p) = -\infty$ → loss 变 `nan`; $z \to -\infty$ 同理 $\log p$ 爆. Clip $p$ 到 $[\varepsilon, 1 - \varepsilon]$ (vanilla 实现里那行 `np.clip`) 是把错误**藏起来** — 大 $|z|$ 时梯度仍偏离 sigmoid 真梯度, 训练发散.

**正确做法: 全程在 logits $z$ 上算**. 先把 $\log p$ / $\log(1-p)$ 直接展成 $z$:

$$\log p = \log \sigma(z) = -\log(1 + e^{-z}), \qquad \log(1 - p) = -z - \log(1 + e^{-z}) = -\log(1 + e^z)$$

代回 BCE 并合并:

$$\ell = y \log(1 + e^{-z}) + (1 - y) \log(1 + e^z) = \log(1 + e^z) - z y$$

但 $\log(1 + e^z)$ 在大 $z$ 上仍上溢 ($e^{800}$ 即 `inf`). 用恒等式 $\log(1 + e^z) = \max(z, 0) + \log(1 + e^{-|z|})$ 把主导项显式抽出 ($z > 0$: 主导 $z$; $z < 0$: 主导 $0$, 余项 $\log(1 + e^z)$ 自然安全):

$$\boxed{\ell = \max(z, 0) - z y + \log(1 + e^{-|z|})}$$

- $\max(z, 0)$: ReLU on logits, 把 $z$ 大正时主导项显式吃掉.
- $\log(1 + e^{-|z|})$: 永远在 $[0, \log 2] \approx [0, 0.693]$, 既不上溢也不下溢.
- 等价 numpy: `np.logaddexp(0, z) - z * y`. 这是 PyTorch `F.binary_cross_entropy_with_logits` / TF `sigmoid_cross_entropy_with_logits` 的实现核心.

```python
@staticmethod
def _stable_bce_loss(z, y):
    # z: (n,) logits, y: (n,) in {0, 1}
    pos_part = np.maximum(z, 0.0)                     # (n,)  ReLU on logits
    log_part = np.log1p(np.exp(-np.abs(z)))           # (n,)  in [0, log 2], safe
    per_sample = pos_part - z * y + log_part          # (n,)
    return float(per_sample.mean())                   # scalar
```

替换 `fit` 里 `_bce_loss(p, y)` 为 `_stable_bce_loss(z, y)` 即可上线. 梯度 $\nabla_w L = X^\top (p - y) / n$ 不变 — 推导阶段 $\sigma'$ 已被消掉, 数值上和 logit-space loss 自洽; 只有 forward loss 值需要换写法.

**Sigmoid sign-branch & softmax LSE 同源**: 按 $z$ 符号分支让 `exp` arg $\leq 0$; softmax 减 $\max_j z_j$ 同源. BCE-with-logits / cross-entropy-from-logits / log-sum-exp 共享 "在 logits 空间算" 这一招.

### B. 学习率上界 + 标准化

收敛要求 $\eta < 2 / \lambda_{\max}\!\left(\frac{1}{n} X^\top \mathrm{diag}(p(1-p)) X\right)$. 实战: 先 zero-mean unit-variance, $\lambda_{\max} = O(1)$, $\eta = 0.1$ 即稳, 不收敛再砍半.
