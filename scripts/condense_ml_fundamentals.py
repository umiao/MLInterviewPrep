"""
T-P0-252: Condense ML Fundamentals From-Scratch guide.

Strategy:
1. t1: Remove Section 4.4 (logistic SGD, covered better in t3).
   Condense Section 6.3 (clipping example) to diff-style.
2. t2: Replace GD implementation with compact reference + delta.
   Replace PyTorch 8.2 with compact config-focused version.
3. t3: Merge logistic_regression + logistic_regression_l2 into one.
   Condense PyTorch 7.1-7.3 to config table referencing t1 canonical.
   Remove Section 9 (GLM, identical to t2 Section 10).
4. t5: Consolidate 3 sklearn verification sections into compact format.
5. t6: Consolidate sklearn verification sections.
6. t8: Condense 5 optimizer implementations using template pattern.

Preserves: All theory/derivation, interview Q&A, formulas.
Reduces: Duplicate code, verbose sklearn verifications, repeated loop structures.
"""

import re
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def read_file(name: str) -> str:
    """Read a source file."""
    return (DATA_DIR / name).read_text(encoding="utf-8")


def write_file(name: str, content: str) -> None:
    """Write a condensed file."""
    (DATA_DIR / name).write_text(content, encoding="utf-8")


# ============================================================
# T1: Remove Section 4.4, condense Section 6.3
# ============================================================
def condense_t1(text: str) -> str:
    # Remove Section 4.4 (logistic regression SGD) - covered better in t3
    # Find from "### 4.4 Logistic Regression" to "---\n\n## 5."
    text = re.sub(
        r"### 4\.4 Logistic Regression \+ BCE.*?(?=---\n\n## 5\.)",
        "",
        text,
        flags=re.DOTALL,
    )

    # Condense Section 6.3: replace full mini_batch_gd_with_clipping with diff reference
    old_63 = re.search(
        r"(### 6\.3 Mini-batch GD \+ Gradient Clipping.*?)(?=### 6\.4)",
        text,
        re.DOTALL,
    )
    if old_63:
        new_63 = """### 6.3 Mini-batch GD + Gradient Clipping

与 Section 4.3 的 `mini_batch_gd` 相同，仅在梯度更新前加两行裁剪：

```python
# 在 grad_w, grad_b 计算后、w -= lr * grad_w 之前加入:
[grad_w, grad_b_arr], _ = clip_grad_by_norm(
    [grad_w, np.array([grad_b])], max_norm=max_norm
)
grad_b = grad_b_arr[0]
```

完整实现 = Section 4.3 `mini_batch_gd` + 上述 3 行 + 函数签名加 `max_norm` 参数。

"""
        text = text[: old_63.start()] + new_63 + text[old_63.end() :]

    return text


# ============================================================
# T2: Condense GD implementation, condense PyTorch
# ============================================================
def condense_t2(text: str) -> str:
    # Replace Section 4.2 GD implementation with compact reference + delta
    old_42 = re.search(
        r"(### 4\.2 纯 Python 实现.*?```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_42:
        new_42 = """### 4.2 纯 Python 实现（Batch GD + Mini-batch）

> **结构与 T1 Section 4.3 `mini_batch_gd` 相同**，仅以下两处不同：
> 1. 将 bias 吸收到 `X_aug`（增广矩阵），无单独的 `b`
> 2. 梯度公式不同：`grad = -(2/B) * (X_b.T @ residual)`（注意负号——用 residual = y - y_hat）

```python
def linear_regression_gd(X, y, lr=0.01, epochs=1000, batch_size=None):
    \"\"\"Linear regression via gradient descent.\"\"\"
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
```"""
        text = text[: old_42.start()] + new_42 + text[old_42.end() :]

    # Replace PyTorch Section 8.2 with compact config-focused version
    old_82 = re.search(
        r"(### 8\.2 GD with nn\.Linear\n\n```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_82:
        new_82 = """### 8.2 GD with nn.Linear

> **与 T1 Section 5.2 `train_with_dataloader` 结构完全相同**，仅配置不同：

```python
def train_linear_regression(X, y, lr=0.01, epochs=200, batch_size=32,
                            weight_decay=0.0):
    \"\"\"PyTorch linear regression. Same loop as T1 Sec 5.2.\"\"\"
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
```"""
        text = text[: old_82.start()] + new_82 + text[old_82.end() :]

    return text


# ============================================================
# T3: Merge L2 variant, condense PyTorch, remove duplicate GLM
# ============================================================
def condense_t3(text: str) -> str:
    # 1. Merge 4.3 + 4.4 into one function with optional lam
    old_43_44 = re.search(
        r"(### 4\.3 Mini-batch Logistic Regression\n\n```python\n.*?### 4\.4 带 L2 正则化版本\n\n```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_43_44:
        new_43 = """### 4.3 Mini-batch Logistic Regression（含可选 L2 正则化）

```python
def logistic_regression(X, y, lr=0.01, epochs=200, batch_size=32, lam=0.0):
    \"\"\"
    Logistic regression via mini-batch gradient descent.
    lam > 0 enables L2 regularization: Loss = BCE + (lam/2)*||w||^2
    \"\"\"
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
```"""
        text = text[: old_43_44.start()] + new_43 + text[old_43_44.end() :]

    # 2. Condense PyTorch sections 7.1-7.3 to show only config diffs
    old_pytorch = re.search(
        r"(### 7\.1 手动实现.*?)(?=### 7\.4 sklearn 对比验证)",
        text,
        re.DOTALL,
    )
    if old_pytorch:
        new_pytorch = """### 7.1-7.3 PyTorch 实现（三种配置）

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

"""
        text = text[: old_pytorch.start()] + new_pytorch + text[old_pytorch.end() :]

    # 3. Remove Section 9 (GLM) - identical to t2 Section 10
    text = re.sub(
        r"---\n\n## 9\. 与 Linear Regression 的统一：GLM 视角.*?(?=---\n\n## 10\. 面试要点总结)",
        "",
        text,
        flags=re.DOTALL,
    )

    # Add cross-reference in the interview section
    old_glm_ref = (
        '- **Logistic Regression \u548c Linear Regression '
        '\u6570\u5b66\u4e0a\u4e3a\u4ec0\u4e48\u662f\u201c\u540c\u4e00\u6a21\u578b\u201d\uff1f**\n'
        '  - GLM \u6846\u67b6\uff1a\u540c\u4e00\u6a21\u578b\u65cf\uff0c'
        '\u53ea\u6539\u53d8\u5206\u5e03\u5047\u8bbe\uff08Gaussian\u2192Bernoulli\uff09'
        '\u548c link function\uff08Identity\u2192Logit\uff09\u3002'
        '\u68af\u5ea6\u5f62\u5f0f\u90fd\u662f $(\\hat{y}-y)\\mathbf{x}$'
    )
    new_glm_ref = (
        '- **Logistic Regression \u548c Linear Regression '
        '\u6570\u5b66\u4e0a\u4e3a\u4ec0\u4e48\u662f\u201c\u540c\u4e00\u6a21\u578b\u201d\uff1f**\n'
        '  - GLM \u6846\u67b6\uff1a\u8be6\u89c1 T2 Section 10\u3002'
        '\u540c\u4e00\u6a21\u578b\u65cf\uff0c\u53ea\u6539\u53d8\u5206\u5e03\u5047\u8bbe\u548c '
        'link function\u3002\u68af\u5ea6\u5f62\u5f0f\u90fd\u662f $(\\hat{y}-y)\\mathbf{x}$'
    )
    text = text.replace(old_glm_ref, new_glm_ref)

    return text


# ============================================================
# T5: Consolidate sklearn verification
# ============================================================
def condense_t5(text: str) -> str:
    old_sklearn = re.search(
        r"(## 8\. sklearn 验证\n\n---\n\n### 8\.1.*?)(?=---\n\n## 9\.)",
        text,
        re.DOTALL,
    )
    if old_sklearn:
        new_sklearn = """## 8. sklearn 验证

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

"""
    if old_sklearn:
        text = text[: old_sklearn.start()] + new_sklearn + text[old_sklearn.end() :]
    return text


# ============================================================
# T6: Consolidate sklearn verification sections
# ============================================================
def condense_t6(text: str) -> str:
    # Condense Decision Tree sklearn verification (Section 4.2)
    old_dt_sklearn = re.search(
        r"(### 4\.2 sklearn 验证\n\n```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_dt_sklearn:
        new_dt_sklearn = """### 4.2 sklearn 验证

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
```"""
        text = text[: old_dt_sklearn.start()] + new_dt_sklearn + text[old_dt_sklearn.end() :]

    # Condense Random Forest sklearn verification (Section 5.6)
    old_rf_sklearn = re.search(
        r"(### 5\.6 Random Forest sklearn 验证\n\n```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_rf_sklearn:
        new_rf_sklearn = """### 5.6 Random Forest sklearn 验证

```python
from sklearn.ensemble import RandomForestClassifier

# Same Iris train/test split as Section 4.2
rf_scratch = RandomForestFromScratch(n_estimators=100, max_depth=5, random_state=42)
rf_scratch.fit(X_train, y_train)
rf_sklearn = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42).fit(X_train, y_train)

print(f"RF scratch: {accuracy_score(y_test, rf_scratch.predict(X_test)):.4f}")
print(f"RF sklearn: {accuracy_score(y_test, rf_sklearn.predict(X_test)):.4f}")
```"""
        text = text[: old_rf_sklearn.start()] + new_rf_sklearn + text[old_rf_sklearn.end() :]

    # Condense AdaBoost sklearn verification (Section 6.5)
    old_ada_sklearn = re.search(
        r"(### 6\.5 AdaBoost sklearn 验证\n\n```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_ada_sklearn:
        new_ada_sklearn = """### 6.5 AdaBoost sklearn 验证

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
```"""
        text = text[: old_ada_sklearn.start()] + new_ada_sklearn + text[old_ada_sklearn.end() :]

    # Condense GBDT sklearn verification (Section 7.6)
    old_gbdt_sklearn = re.search(
        r"(### 7\.6 GBDT sklearn 验证\n\n```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_gbdt_sklearn:
        new_gbdt_sklearn = """### 7.6 GBDT sklearn 验证

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
```"""
        text = text[: old_gbdt_sklearn.start()] + new_gbdt_sklearn + text[old_gbdt_sklearn.end() :]

    return text


# ============================================================
# T8: Condense optimizer implementations with template pattern
# ============================================================
def condense_t8(text: str) -> str:
    # Replace 5 separate optimizer implementations with template + update-only
    old_optimizers = re.search(
        r"(### 4\.2 SGD \+ Momentum 实现\n\n```python\n.*?"
        r"### 4\.6 AdamW 实现\n\n```python\n.*?```)",
        text,
        re.DOTALL,
    )
    if old_optimizers:
        new_optimizers = """### 4.2-4.6 五种优化器从零实现

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
params = (1 - lr * weight_decay) * params \\
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
        params = (1 - lr * weight_decay) * params \\
                 - lr * m_hat / (np.sqrt(v_hat) + eps)
        history.append(params.copy())
    return params, history
```

</details>"""
        text = text[: old_optimizers.start()] + new_optimizers + text[old_optimizers.end() :]

    # Also condense the Gradient Clipping section (Section 9) since T1 already covers it
    old_clip = re.search(
        r"(## 9\. Gradient Clipping.*?)(?=---\n\n## 10\.)",
        text,
        re.DOTALL,
    )
    if old_clip:
        new_clip = """## 9. Gradient Clipping（梯度裁剪）

> 详细原理和纯 Python 实现见 T1 Section 6。此处仅列要点。

- **按范数裁剪**（推荐）：$g \\leftarrow g \\cdot \\min(1, \\theta/\\|g\\|)$，保持方向，RNN/Transformer 标配
- **按值裁剪**：逐元素 $\\text{clip}(g_j, -\\theta, \\theta)$，可能改变方向
- PyTorch: `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)`

"""
        text = text[: old_clip.start()] + new_clip + text[old_clip.end() :]

    return text


# ============================================================
# Merge all files into single document
# ============================================================
def merge_files() -> str:
    """Read all condensed t1-t8 files and merge into one document."""
    header = """# ML Fundamentals From-Scratch Complete Guide (8 Topics Merged)

> 本指南覆盖 8 个核心 ML 主题的理论推导、纯 Python 手写实现和 PyTorch 验证。
> 每个主题可独立阅读，跨主题引用标注为 "详见 TX Section Y"。

---

"""
    parts = []
    for i in range(1, 9):
        content = read_file(f"t{i}_*.md".replace("*", {
            1: "gradient_descent",
            2: "linear_regression",
            3: "logistic_regression",
            4: "knn_kmeans",
            5: "naive_bayes",
            6: "tree_models",
            7: "weight_initialization",
            8: "optimizers",
        }[i]))
        parts.append(content)

    return header + "\n\n---\n\n".join(parts)


# ============================================================
# Main
# ============================================================
def main() -> None:
    print("=== Condensing ML Fundamentals From-Scratch Guide ===")
    print()

    # Read original sizes
    files = [
        "t1_gradient_descent.md",
        "t2_linear_regression.md",
        "t3_logistic_regression.md",
        "t4_knn_kmeans.md",
        "t5_naive_bayes.md",
        "t6_tree_models.md",
        "t7_weight_initialization.md",
        "t8_optimizers.md",
    ]

    original_sizes = {}
    for f in files:
        content = read_file(f)
        original_sizes[f] = len(content)
        print(f"  Original {f}: {len(content):,} chars")

    total_original = sum(original_sizes.values())
    print(f"  TOTAL original: {total_original:,} chars")
    print()

    # Apply condensation
    condensers = {
        "t1_gradient_descent.md": condense_t1,
        "t2_linear_regression.md": condense_t2,
        "t3_logistic_regression.md": condense_t3,
        "t4_knn_kmeans.md": lambda x: x,  # No changes needed
        "t5_naive_bayes.md": condense_t5,
        "t6_tree_models.md": condense_t6,
        "t7_weight_initialization.md": lambda x: x,  # No changes needed
        "t8_optimizers.md": condense_t8,
    }

    condensed_sizes = {}
    for f in files:
        content = read_file(f)
        condensed = condensers[f](content)
        write_file(f, condensed)
        condensed_sizes[f] = len(condensed)
        saved = original_sizes[f] - len(condensed)
        pct = saved / original_sizes[f] * 100 if original_sizes[f] > 0 else 0
        print(f"  Condensed {f}: {len(condensed):,} chars (saved {saved:,}, {pct:.1f}%)")

    total_condensed = sum(condensed_sizes.values())
    total_saved = total_original - total_condensed
    total_pct = total_saved / total_original * 100
    print(f"  TOTAL condensed: {total_condensed:,} chars")
    print(f"  TOTAL saved: {total_saved:,} chars ({total_pct:.1f}%)")
    print()

    # Merge into single document
    print("Merging into single document...")
    merged = merge_files()
    print(f"  Merged document: {len(merged):,} chars")
    print()

    # Update database
    print("Updating database (docs 27, 28, 29)...")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    for doc_id in [27, 28, 29]:
        cursor.execute(
            "UPDATE company_documents SET content = ? WHERE id = ?",
            (merged, doc_id),
        )
        print(f"  Updated doc {doc_id}: {len(merged):,} chars")

    conn.commit()

    # Verify
    cursor.execute(
        "SELECT id, LENGTH(content) FROM company_documents WHERE id IN (27, 28, 29)"
    )
    for row in cursor.fetchall():
        print(f"  Verified doc {row[0]}: {row[1]:,} chars")

    conn.close()
    print()
    print("Done!")


if __name__ == "__main__":
    main()
