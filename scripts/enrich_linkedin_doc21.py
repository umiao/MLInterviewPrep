"""Enrich LinkedIn doc#21 (Probability/Stats) with missing code, acronyms, follow-ups.

Task: T-P0-263
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_content(conn: sqlite3.Connection) -> str:
    """Read doc#21 content."""
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=21")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#21 not found")
        sys.exit(1)
    return row[0]


def enrich(content: str) -> str:
    """Apply all enrichments to doc#21."""

    # ── Acronym expansions (first occurrence) ──
    # Q1: CDF not expanded
    content = content.replace(
        "**核心方法: Inverse CDF Sampling（逆累积分布函数采样）**",
        "**核心方法: Inverse CDF (Cumulative Distribution Function，累积分布函数) Sampling**",
    )

    # Q2: iid not expanded
    content = content.replace(
        "**Case 1: iid（独立同分布）**",
        "**Case 1: iid (independent and identically distributed，独立同分布)**",
    )

    # Q6: SMOTE not expanded
    content = content.replace(
        "**SMOTE** (Synthetic Minority Over-sampling Technique)",
        "**SMOTE (Synthetic Minority Over-sampling Technique，合成少数类过采样技术)**",
    )

    # Q6: AUC-ROC not expanded
    content = content.replace(
        "- **AUC-ROC**: 阈值无关的评估",
        "- **AUC-ROC (Area Under the Receiver Operating Characteristic Curve，接收者操作特征曲线下面积)**: 阈值无关的评估",
    )

    # Q6: PR Curve not expanded
    content = content.replace(
        "- **PR Curve (Precision-Recall curve)**: 在极端imbalance下比ROC更informative",
        "- **PR Curve (Precision-Recall Curve，精确率-召回率曲线)**: 在极端imbalance下比ROC更informative",
    )

    # Q7: KS test not expanded
    content = content.replace(
        "   - KS test (Kolmogorov-Smirnov test): 检验两个分布是否相同",
        "   - **KS test (Kolmogorov-Smirnov test，柯尔莫哥洛夫-斯米尔诺夫检验)**: 检验两个分布是否相同",
    )

    # Q8: CV not expanded on first use in Q7
    content = content.replace(
        "3. **Cross-validation on sample**: 在样本内做k-fold CV",
        "3. **Cross-validation on sample**: 在样本内做k-fold CV (Cross-Validation，交叉验证)",
    )

    # Q9: OLS not expanded
    content = content.replace(
        "**无正则化的OLS（Ordinary Least Squares）**:",
        "**无正则化的OLS (Ordinary Least Squares，最小二乘法)**:",
    )

    # Q10: OOB not expanded
    content = content.replace(
        "- 使用OOB (Out-of-Bag) error估计泛化误差",
        "- 使用**OOB (Out-of-Bag，袋外) error**估计泛化误差",
    )

    # Q10: SHAP not expanded
    content = content.replace(
        "| 解释性 | Feature importance | Feature importance + SHAP |",
        "| 解释性 | Feature importance | Feature importance + SHAP (SHapley Additive exPlanations) |",
    )

    # Q14: GLM not expanded -- already has expansion inline, good

    # ── Add Python code + follow-ups to Q4 (Queueing Theory) ──
    q4_old_interview = """### 面试要点

- 先说结论：单队列更好
- 解释 "same mean, lower variance"
- 提到statistical multiplexing（资源池化）的概念
- 如果被问公式，写出M/M/c的基本设定即可
- 现实中银行、机场安检都在向单队列转变

---

## 5."""

    q4_new = """### Python代码

```python
import numpy as np
from typing import Tuple

def simulate_queues(
    n_servers: int = 5,
    arrival_rate: float = 4.0,
    service_rate: float = 1.0,
    n_customers: int = 10000,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    \"\"\"Simulate single-queue vs multi-queue wait times.

    Returns (single_queue_waits, multi_queue_waits).
    \"\"\"
    rng = np.random.default_rng(seed)

    # Inter-arrival times (Poisson process)
    inter_arrivals = rng.exponential(1.0 / arrival_rate, n_customers)
    arrivals = np.cumsum(inter_arrivals)

    # Service times
    service_times = rng.exponential(1.0 / service_rate, n_customers)

    # Single queue (M/M/c): assign to earliest-free server
    server_free_at = np.zeros(n_servers)
    single_waits = np.zeros(n_customers)
    for i in range(n_customers):
        earliest = server_free_at.min()
        wait = max(0, earliest - arrivals[i])
        single_waits[i] = wait
        idx = server_free_at.argmin()
        server_free_at[idx] = max(arrivals[i], earliest) + service_times[i]

    # Multi queue: random assignment to one of c queues
    queue_free_at = np.zeros(n_servers)
    multi_waits = np.zeros(n_customers)
    for i in range(n_customers):
        q = rng.integers(n_servers)
        wait = max(0, queue_free_at[q] - arrivals[i])
        multi_waits[i] = wait
        queue_free_at[q] = max(arrivals[i], queue_free_at[q]) + service_times[i]

    return single_waits, multi_waits


single_w, multi_w = simulate_queues()
print(f"Single queue: mean={single_w.mean():.2f}, std={single_w.std():.2f}")
print(f"Multi queue:  mean={multi_w.mean():.2f}, std={multi_w.std():.2f}")
print(f"Variance ratio (multi/single): {multi_w.var() / single_w.var():.2f}")
```

### 常见Follow-up

1. **如果柜员速度不同怎么办？** 单队列优势更大，因为快柜员能更多地服务队首客户。
2. **多队列允许换队呢？** 允许"jockeying"（换队）可以缩小差距，但不如单队列稳定。
3. **实际应用？** 超市自助结账、呼叫中心（单队列 + 多agent）、云计算负载均衡。

### 面试要点

- 先说结论：单队列更好
- 解释 "same mean, lower variance"
- 提到**statistical multiplexing（统计复用/资源池化）**的概念
- 如果被问公式，写出M/M/c的基本设定即可
- 现实中银行、机场安检都在向单队列转变

---

## 5."""

    content = content.replace(q4_old_interview, q4_new)

    # ── Add Python code + follow-ups to Q6 (Class Imbalance) ──
    q6_old_interview = """### 面试要点

- 分data-level、algorithm-level、evaluation三个层面回答
- SMOTE是高频考点，要能解释原理
- 强调不要用accuracy，用precision/recall/F1/AUC
- 提到anomaly detection作为extreme imbalance的替代方案

---

## 7."""

    q6_new = """### Python代码

```python
import numpy as np
from typing import Tuple

def smote_1d(
    minority: np.ndarray, n_synthetic: int, k: int = 5, seed: int = 42
) -> np.ndarray:
    \"\"\"Simplified 1D SMOTE implementation.

    For each synthetic sample: pick a minority point, find its k nearest
    neighbors among minority class, interpolate with a random neighbor.
    \"\"\"
    rng = np.random.default_rng(seed)
    synthetic = np.zeros(n_synthetic)

    for i in range(n_synthetic):
        idx = rng.integers(len(minority))
        anchor = minority[idx]
        # k nearest neighbors (1D: sort by distance)
        dists = np.abs(minority - anchor)
        neighbor_indices = np.argsort(dists)[1 : k + 1]
        neighbor = minority[rng.choice(neighbor_indices)]
        lam = rng.random()
        synthetic[i] = anchor + lam * (neighbor - anchor)

    return synthetic


def class_weight_loss(
    y_true: np.ndarray, y_pred_prob: np.ndarray
) -> float:
    \"\"\"Weighted binary cross-entropy loss.\"\"\"
    n_pos = y_true.sum()
    n_neg = len(y_true) - n_pos
    w_pos = len(y_true) / (2 * n_pos) if n_pos > 0 else 1.0
    w_neg = len(y_true) / (2 * n_neg) if n_neg > 0 else 1.0
    weights = np.where(y_true == 1, w_pos, w_neg)
    eps = 1e-15
    loss = -weights * (
        y_true * np.log(y_pred_prob + eps)
        + (1 - y_true) * np.log(1 - y_pred_prob + eps)
    )
    return loss.mean()


# Demo
np.random.seed(42)
minority_data = np.random.normal(5, 1, 20)
synthetic_data = smote_1d(minority_data, 30)
print(f"Original minority: {len(minority_data)} samples, "
      f"mean={minority_data.mean():.2f}")
print(f"Synthetic: {len(synthetic_data)} samples, "
      f"mean={synthetic_data.mean():.2f}")
```

### 常见Follow-up

1. **SMOTE的局限性？** 在高维空间中插值可能生成不合理样本（"噪声"），Borderline-SMOTE只在决策边界附近生成。
2. **什么时候不应该用oversampling？** 当少数类本身是noise/outlier时（如欺诈检测中的标注错误）。
3. **如何选择precision vs recall的tradeoff？** 取决于业务代价：医疗诊断优先recall（漏诊代价高），spam过滤优先precision（误判代价高）。
4. **Focal Loss是什么？** 下调easy-to-classify样本的权重: $FL = -\\alpha_t(1-p_t)^\\gamma \\log(p_t)$，常用于目标检测。

### 面试要点

- 分data-level、algorithm-level、evaluation三个层面回答
- SMOTE是高频考点，要能解释原理
- 强调不要用accuracy，用precision/recall/F1/AUC
- 提到anomaly detection作为extreme imbalance的替代方案

---

## 7."""

    content = content.replace(q6_old_interview, q6_new)

    # ── Add Python code + follow-ups to Q7 (Sampling from Large Dataset) ──
    q7_old_interview = """### 面试要点

- 核心: "sample representativeness" + "out-of-sample validation"
- KS test是验证分布一致性的标准工具
- 一定要提到hold-out set来自full data而非sample
- Bootstrap检查模型稳定性是加分项

---

## 8."""

    q7_new = """### Python代码

```python
import numpy as np
from typing import Tuple

def ks_statistic(sample1: np.ndarray, sample2: np.ndarray) -> float:
    \"\"\"Compute two-sample KS statistic (max CDF difference).\"\"\"
    combined = np.sort(np.concatenate([sample1, sample2]))
    cdf1 = np.searchsorted(np.sort(sample1), combined, side="right") / len(sample1)
    cdf2 = np.searchsorted(np.sort(sample2), combined, side="right") / len(sample2)
    return float(np.max(np.abs(cdf1 - cdf2)))


def stratified_sample(
    data: np.ndarray, labels: np.ndarray, frac: float = 0.1, seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    \"\"\"Stratified sampling preserving class proportions.\"\"\"
    rng = np.random.default_rng(seed)
    indices = []
    for label in np.unique(labels):
        class_idx = np.where(labels == label)[0]
        n_sample = max(1, int(len(class_idx) * frac))
        chosen = rng.choice(class_idx, n_sample, replace=False)
        indices.extend(chosen)
    indices = np.array(indices)
    return data[indices], labels[indices]


def bootstrap_stability(
    data: np.ndarray, labels: np.ndarray, n_bootstraps: int = 20
) -> float:
    \"\"\"Estimate model performance variance via bootstrap.\"\"\"
    rng = np.random.default_rng(42)
    accuracies = []
    for _ in range(n_bootstraps):
        idx = rng.choice(len(data), len(data), replace=True)
        oob_mask = np.ones(len(data), dtype=bool)
        oob_mask[idx] = False
        if oob_mask.sum() == 0:
            continue
        # Simple nearest-centroid classifier for demo
        train_x, train_y = data[idx], labels[idx]
        test_x, test_y = data[oob_mask], labels[oob_mask]
        centroids = {}
        for label in np.unique(train_y):
            centroids[label] = train_x[train_y == label].mean(axis=0)
        preds = []
        for x in test_x:
            best_label = min(centroids, key=lambda l: np.sum((x - centroids[l])**2))
            preds.append(best_label)
        acc = np.mean(np.array(preds) == test_y)
        accuracies.append(acc)
    return float(np.std(accuracies))


# Demo: verify sample representativeness
np.random.seed(42)
full_data = np.random.normal(0, 1, 10000)
sample_data = np.random.choice(full_data, 1000, replace=False)
ks = ks_statistic(full_data, sample_data)
print(f"KS statistic (full vs sample): {ks:.4f}")
print(f"KS < 0.05 -> distributions similar: {ks < 0.05}")
```

### 常见Follow-up

1. **样本量多大才够？** 取决于模型复杂度和特征维度。经验法则：至少10x特征数。可以用learning curve判断。
2. **如果数据有temporal dependency？** 不能随机采样，必须按时间切分（time-based split），否则会有data leakage。
3. **KS test的p-value阈值？** 通常p < 0.05表示分布显著不同，但大样本下几乎总是显著，需要结合效应量（KS statistic值）判断。

### 面试要点

- 核心: "sample representativeness" + "out-of-sample validation"
- KS test是验证分布一致性的标准工具
- 一定要提到hold-out set来自full data而非sample
- Bootstrap检查模型稳定性是加分项

---

## 8."""

    content = content.replace(q7_old_interview, q7_new)

    # ── Add Python code + follow-ups to Q8 (Overfitting Prevention) ──
    q8_old_interview = """### 面试要点

- 至少提到3-4种方法，覆盖单树和ensemble两个层面
- 理解pre-pruning和post-pruning的区别
- Boosting + early stopping是最实用的组合
- 面试中可以结合具体参数名解释（sklearn的参数名）

---

## 9."""

    q8_new = """### Python代码

```python
import numpy as np
from typing import List, Tuple

def demo_overfitting_tree() -> None:
    \"\"\"Show effect of max_depth on train vs test error (decision stump).\"\"\"
    rng = np.random.default_rng(42)
    n = 200
    x = rng.uniform(0, 10, n)
    y = np.sin(x) + rng.normal(0, 0.3, n)

    # Split
    train_x, test_x = x[:150], x[150:]
    train_y, test_y = y[:150], y[150:]

    # Simulate depth effect: polynomial fits of increasing degree
    for degree in [1, 3, 5, 15]:
        coeffs = np.polyfit(train_x, train_y, degree)
        train_pred = np.polyval(coeffs, train_x)
        test_pred = np.polyval(coeffs, test_x)
        train_mse = np.mean((train_y - train_pred) ** 2)
        test_mse = np.mean((test_y - test_pred) ** 2)
        print(f"Degree {degree:2d}: train MSE={train_mse:.4f}, "
              f"test MSE={test_mse:.4f}")


def early_stopping_demo(
    losses: List[float], patience: int = 5
) -> int:
    \"\"\"Return epoch to stop at given validation losses and patience.\"\"\"
    best_loss = float("inf")
    wait = 0
    best_epoch = 0
    for epoch, loss in enumerate(losses):
        if loss < best_loss:
            best_loss = loss
            wait = 0
            best_epoch = epoch
        else:
            wait += 1
            if wait >= patience:
                return best_epoch
    return best_epoch


demo_overfitting_tree()

# Early stopping example
val_losses = [1.0, 0.8, 0.6, 0.5, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53]
stop_at = early_stopping_demo(val_losses, patience=3)
print(f"Early stopping at epoch {stop_at} (val_loss={val_losses[stop_at]:.2f})")
```

### 常见Follow-up

1. **增加树的数量会让RF overfit吗？** 不会。Breiman证明了RF随着树的增加，泛化误差收敛到一个上界，不会发散。但Boosting会。
2. **什么时候用RF vs XGBoost？** 数据量小/特征少用RF更稳定；大数据集+调参时间充裕用XGBoost通常精度更高。
3. **Cost-complexity pruning怎么选alpha？** 通过交叉验证: 对不同alpha值计算CV error，选择1-SE rule下的最大alpha。

### 面试要点

- 至少提到3-4种方法，覆盖单树和ensemble两个层面
- 理解pre-pruning和post-pruning的区别
- Boosting + early stopping是最实用的组合
- 面试中可以结合具体参数名解释（sklearn的参数名）

---

## 9."""

    content = content.replace(q8_old_interview, q8_new)

    # ── Add Python code + follow-ups to Q9 (L1/L2 Regularization) ──
    q9_old_interview = """### 面试要点

- 核心: 正则化通过向零收缩引入bias，换取更低的variance
- 能写出Ridge的闭式解并推导bias
- 提及bias-variance tradeoff
- L1的额外特性: sparsity / feature selection
- James-Stein estimator是高级加分项

---

## 10."""

    q9_new = """### Python代码

```python
import numpy as np
from typing import Tuple

def ridge_regression(
    X: np.ndarray, y: np.ndarray, lam: float
) -> np.ndarray:
    \"\"\"Ridge regression closed-form solution.\"\"\"
    n_features = X.shape[1]
    return np.linalg.solve(
        X.T @ X + lam * np.eye(n_features), X.T @ y
    )


def demo_ridge_bias() -> None:
    \"\"\"Demonstrate bias-variance tradeoff with Ridge.\"\"\"
    rng = np.random.default_rng(42)
    n, p = 50, 10
    beta_true = rng.standard_normal(p)
    X = rng.standard_normal((n, p))
    y = X @ beta_true + rng.normal(0, 0.5, n)

    print(f"True beta norm: {np.linalg.norm(beta_true):.3f}")
    for lam in [0, 0.1, 1.0, 10.0, 100.0]:
        beta_hat = ridge_regression(X, y, lam)
        bias = np.linalg.norm(beta_hat - beta_true)
        print(f"lambda={lam:6.1f}: ||beta_hat||={np.linalg.norm(beta_hat):.3f}, "
              f"bias(||beta_hat - beta_true||)={bias:.3f}")


def lasso_coordinate_descent(
    X: np.ndarray, y: np.ndarray, lam: float,
    max_iter: int = 1000, tol: float = 1e-6,
) -> np.ndarray:
    \"\"\"Simple coordinate descent for Lasso.\"\"\"
    n, p = X.shape
    beta = np.zeros(p)
    for _ in range(max_iter):
        beta_old = beta.copy()
        for j in range(p):
            residual = y - X @ beta + X[:, j] * beta[j]
            rho = X[:, j] @ residual / n
            beta[j] = np.sign(rho) * max(abs(rho) - lam / n, 0)
        if np.max(np.abs(beta - beta_old)) < tol:
            break
    return beta


demo_ridge_bias()
```

### 常见Follow-up

1. **Elastic Net是什么？** 结合L1和L2: $\\lambda_1\\|\\beta\\|_1 + \\lambda_2\\|\\beta\\|_2^2$。当特征之间有相关性时，Lasso只保留一个，Elastic Net保留一组。
2. **为什么L1产生sparsity但L2不会？** 几何解释：L1的约束区域（菱形）有尖角，等高线更容易在坐标轴上与之相切，使系数恰好为0。
3. **Bayesian解释？** L2 = Gaussian prior on weights; L1 = Laplace prior on weights。Laplace分布在0处的密度峰值更高，鼓励稀疏。

### 面试要点

- 核心: 正则化通过向零收缩引入bias，换取更低的variance
- 能写出Ridge的闭式解并推导bias
- 提及bias-variance tradeoff
- L1的额外特性: sparsity / feature selection
- James-Stein estimator是高级加分项

---

## 10."""

    content = content.replace(q9_old_interview, q9_new)

    # ── Add Python code + follow-ups to Q10 (Random Forest) ──
    q10_old_interview = """### 面试要点

- 核心: Bagging + Feature subsampling
- 联系到第2题的variance公式: $\\rho\\sigma^2 + \\frac{(1-\\rho)\\sigma^2}{N}$
- 明确RF降低variance，Boosting降低bias
- OOB error是RF的独特优势，不需要额外validation set

---

## 11."""

    q10_new = (
        '### Python代码\n'
        '\n'
        '```python\n'
        'import numpy as np\n'
        'from typing import List, Tuple\n'
        '\n'
        'def bootstrap_sample(\n'
        '    X: np.ndarray, y: np.ndarray, rng: np.random.Generator\n'
        ') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:\n'
        '    """Bootstrap sample + return OOB indices."""\n'
        '    n = len(X)\n'
        '    idx = rng.choice(n, n, replace=True)\n'
        '    oob_mask = np.ones(n, dtype=bool)\n'
        '    oob_mask[idx] = False\n'
        '    return X[idx], y[idx], oob_mask\n'
        '\n'
        '\n'
        'def simple_tree_predict(\n'
        '    X_train: np.ndarray, y_train: np.ndarray,\n'
        '    X_test: np.ndarray, feature_subset: np.ndarray,\n'
        ') -> np.ndarray:\n'
        '    """Minimal stump: split on best feature at median."""\n'
        '    best_mse = float("inf")\n'
        '    best_pred = np.full(len(X_test), y_train.mean())\n'
        '\n'
        '    for f in feature_subset:\n'
        '        threshold = np.median(X_train[:, f])\n'
        '        left = y_train[X_train[:, f] <= threshold]\n'
        '        right = y_train[X_train[:, f] > threshold]\n'
        '        if len(left) == 0 or len(right) == 0:\n'
        '            continue\n'
        '        pred = np.where(\n'
        '            X_test[:, f] <= threshold, left.mean(), right.mean()\n'
        '        )\n'
        '        mse = np.mean((y_train - np.where(\n'
        '            X_train[:, f] <= threshold, left.mean(), right.mean()\n'
        '        )) ** 2)\n'
        '        if mse < best_mse:\n'
        '            best_mse = mse\n'
        '            best_pred = pred\n'
        '\n'
        '    return best_pred\n'
        '\n'
        '\n'
        'def random_forest_demo(\n'
        '    X: np.ndarray, y: np.ndarray,\n'
        '    n_trees: int = 50, max_features: int = 3,\n'
        ') -> Tuple[float, float]:\n'
        '    """Simple RF demo returning OOB MSE."""\n'
        '    rng = np.random.default_rng(42)\n'
        '    n, p = X.shape\n'
        '    oob_preds = np.zeros(n)\n'
        '    oob_counts = np.zeros(n)\n'
        '\n'
        '    for _ in range(n_trees):\n'
        '        X_boot, y_boot, oob_mask = bootstrap_sample(X, y, rng)\n'
        '        features = rng.choice(p, min(max_features, p), replace=False)\n'
        '        preds = simple_tree_predict(X_boot, y_boot, X, features)\n'
        '\n'
        '        oob_preds[oob_mask] += preds[oob_mask]\n'
        '        oob_counts[oob_mask] += 1\n'
        '\n'
        '    valid = oob_counts > 0\n'
        '    oob_mse = np.mean((y[valid] - oob_preds[valid] / oob_counts[valid]) ** 2)\n'
        '    return oob_mse\n'
        '\n'
        '\n'
        '# Demo\n'
        'np.random.seed(42)\n'
        'X_demo = np.random.randn(200, 5)\n'
        'y_demo = 3 * X_demo[:, 0] - 2 * X_demo[:, 1] + np.random.randn(200) * 0.5\n'
        'oob_error = random_forest_demo(X_demo, y_demo)\n'
        'print(f"RF OOB MSE: {oob_error:.4f}")\n'
        '```\n'
        '\n'
        '### 常见Follow-up\n'
        '\n'
        '1. **OOB error是什么？** 每棵树的bootstrap sample约覆盖63.2%数据（$1 - 1/e$）。剩余36.8%可以作为该树的验证集。汇总所有树的OOB预测得到泛化误差估计，无需单独的validation set。\n'
        '2. **Feature Importance怎么算？** (a) Mean Decrease Impurity: 每个特征在所有树中减少的impurity之和。(b) Permutation Importance: 随机打乱某个特征，观察OOB error增加多少。后者更可靠但更慢。\n'
        '3. **RF能处理缺失值吗？** 可以用surrogate splits（类似CART），或者用proximity matrix填补缺失值。\n'
        '\n'
        '### 面试要点\n'
        '\n'
        '- 核心: Bagging + Feature subsampling\n'
        '- 联系到第2题的variance公式: $\\rho\\sigma^2 + \\frac{(1-\\rho)\\sigma^2}{N}$\n'
        '- 明确RF降低variance，Boosting降低bias\n'
        '- OOB error是RF的独特优势，不需要额外validation set\n'
        '\n'
        '---\n'
        '\n'
        '## 11.'
    )

    content = content.replace(q10_old_interview, q10_new)

    # ── Add Python code + follow-ups to Q14 (Linear vs Logistic) ──
    q14_old_interview = """### 面试要点

- 关键词: GLM (Generalized Linear Model)
- 能清楚说出两者的link function区别
- 强调共同点: linear predictor $X\\beta$
- 如果被追问multiclass: Logistic Regression可以通过One-vs-Rest或Softmax扩展
- 这是LinkedIn面经中的surprise question，准备好不常见的角度

---

## 附录"""

    q14_new = (
        '### Python代码\n'
        '\n'
        '```python\n'
        'import numpy as np\n'
        'from typing import Tuple\n'
        '\n'
        'def linear_regression_fit(\n'
        '    X: np.ndarray, y: np.ndarray\n'
        ') -> np.ndarray:\n'
        '    """OLS closed-form: beta = (X^T X)^{-1} X^T y."""\n'
        '    return np.linalg.solve(X.T @ X, X.T @ y)\n'
        '\n'
        '\n'
        'def sigmoid(z: np.ndarray) -> np.ndarray:\n'
        '    """Numerically stable sigmoid function."""\n'
        '    return np.where(\n'
        '        z >= 0,\n'
        '        1.0 / (1.0 + np.exp(-z)),\n'
        '        np.exp(z) / (1.0 + np.exp(z)),\n'
        '    )\n'
        '\n'
        '\n'
        'def logistic_regression_fit(\n'
        '    X: np.ndarray, y: np.ndarray,\n'
        '    lr: float = 0.1, max_iter: int = 1000,\n'
        ') -> np.ndarray:\n'
        '    """Logistic regression via gradient descent."""\n'
        '    beta = np.zeros(X.shape[1])\n'
        '    for _ in range(max_iter):\n'
        '        p = sigmoid(X @ beta)\n'
        '        gradient = X.T @ (p - y) / len(y)\n'
        '        beta -= lr * gradient\n'
        '    return beta\n'
        '\n'
        '\n'
        'def glm_comparison() -> None:\n'
        '    """Show linear and logistic regression as GLM special cases."""\n'
        '    rng = np.random.default_rng(42)\n'
        '    n = 200\n'
        '    X = np.column_stack([np.ones(n), rng.standard_normal((n, 2))])\n'
        '    beta_true = np.array([0.5, 1.0, -0.5])\n'
        '\n'
        '    # Linear regression: identity link\n'
        '    eta = X @ beta_true\n'
        '    y_linear = eta + rng.normal(0, 0.3, n)\n'
        '    beta_lin = linear_regression_fit(X, y_linear)\n'
        '    print("Linear Regression (identity link):")\n'
        '    print(f"  True:      {beta_true}")\n'
        '    print(f"  Estimated: {beta_lin.round(3)}")\n'
        '\n'
        '    # Logistic regression: logit link\n'
        '    p_true = sigmoid(eta)\n'
        '    y_binary = rng.binomial(1, p_true)\n'
        '    beta_log = logistic_regression_fit(X, y_binary)\n'
        '    print("Logistic Regression (logit link):")\n'
        '    print(f"  True:      {beta_true}")\n'
        '    print(f"  Estimated: {beta_log.round(3)}")\n'
        '    print(f"\\nBoth use linear predictor eta = X @ beta")\n'
        '    print(f"Linear: E[Y|X] = eta (identity)")\n'
        '    print(f"Logistic: P(Y=1|X) = sigmoid(eta) (logit link)")\n'
        '\n'
        '\n'
        'glm_comparison()\n'
        '```\n'
        '\n'
        '### 常见Follow-up\n'
        '\n'
        '1. **Probit Regression是什么？** 另一个GLM：link function是标准正态CDF的逆函数 $\\Phi^{-1}(p) = X\\beta$。和logistic结果接近，但在尾部行为不同。\n'
        '2. **为什么logistic没有闭式解？** 因为log-likelihood对beta求导后的方程是非线性的（含sigmoid），必须用迭代优化（Newton-Raphson / IRLS）。\n'
        '3. **GLM还有哪些常见例子？** Poisson回归（log link）用于计数数据，Gamma回归（inverse link）用于正连续数据。\n'
        '\n'
        '### 面试要点\n'
        '\n'
        '- 关键词: **GLM (Generalized Linear Model，广义线性模型)**\n'
        '- 能清楚说出两者的link function区别\n'
        '- 强调共同点: linear predictor $X\\beta$\n'
        '- 如果被追问multiclass: Logistic Regression可以通过One-vs-Rest或Softmax扩展\n'
        '- 这是LinkedIn面经中的surprise question，准备好不常见的角度\n'
        '\n'
        '---\n'
        '\n'
        '## 附录'
    )

    content = content.replace(q14_old_interview, q14_new)

    # ── Add follow-ups to Q1 (Weighted Sampling) ──
    q1_old = """### 面试要点

- 首先明确softmax归一化保证 $\\sum p_i = 1$
- Inverse CDF是最经典的方法，面试中优先提
- 注意浮点精度问题（cumsum最后一项强制设为1.0）
- 被追问优化时提Alias Method: $O(1)$ per sample
- 提及可以用 `numpy.random.choice` 验证实现的正确性

---

## 2."""

    q1_new = """### 常见Follow-up

1. **Alias Method具体怎么实现？** 预处理阶段将每个概率拆成两部分构建alias table。每次采样只需一次随机数+一次比较，$O(1)$时间。
2. **如果概率分布会动态变化怎么办？** 使用Fenwick Tree (Binary Indexed Tree，树状数组)维护前缀和，支持$O(\\log N)$更新和$O(\\log N)$采样。
3. **GPU上如何批量采样？** 预计算CDF后，生成一批uniform random numbers，用并行binary search映射。

### 面试要点

- 首先明确softmax归一化保证 $\\sum p_i = 1$
- Inverse CDF是最经典的方法，面试中优先提
- 注意浮点精度问题（cumsum最后一项强制设为1.0）
- 被追问优化时提Alias Method: $O(1)$ per sample
- 提及可以用 `numpy.random.choice` 验证实现的正确性

---

## 2."""

    content = content.replace(q1_old, q1_new)

    # ── Add follow-ups to Q3 (Simpson's Paradox) ──
    q3_old = """### 面试要点

- 第一反应就说 "This is Simpson's Paradox"
- 强调confounding variable: 城市、时区、用户base rate不同
- 解决方案: balanced dataset + stratified analysis
- 被问CI时，回答在stratum内计算，推荐CMH test
- LinkedIn面经原题高频出现

---

## 4."""

    q3_new = """### 常见Follow-up

1. **如何在实验设计阶段避免Simpson's Paradox？** 使用**randomized controlled trial (RCT，随机对照试验)**，确保treatment和control组在所有stratum中比例一致。
2. **还有哪些类似的统计悖论？** Berkson's Paradox（选择偏差导致虚假负相关）、Lord's Paradox（同一数据用ANCOVA和差值法得到相反结论）。
3. **A/B test中如何处理？** 使用stratified randomization或post-stratification调整，确保每个segment（城市/平台/用户类型）中treatment分配均衡。

### 面试要点

- 第一反应就说 "This is Simpson's Paradox"
- 强调confounding variable: 城市、时区、用户base rate不同
- 解决方案: balanced dataset + stratified analysis
- 被问CI时，回答在stratum内计算，推荐CMH test
- LinkedIn面经原题高频出现

---

## 4."""

    content = content.replace(q3_old, q3_new)

    # ── Add follow-ups to Q5 (Distributions) ──
    q5_old = """### 面试要点

- Part 1: 关键词 "bimodal distribution"，要能解释为什么合并后不是normal
- Part 2: 关键词 "right-skewed"，Mode < Median < Mean
- 准备好在白板上画出distribution的形状
- 被追问时可以讨论log-normal vs power-law的区别

---

## 6."""

    q5_new = """### 常见Follow-up

1. **Log-normal和Power-law怎么区分？** Log-normal: $\\log(X) \\sim N(\\mu, \\sigma^2)$，尾部衰减比power-law快。Power-law: $P(X > x) \\propto x^{-\\alpha}$，尾部更重（heavy tail）。可以用log-log图：power-law在log-log图上是直线。
2. **如果男女比例不是50:50呢？** 仍然是mixture但可能不是明显的bimodal。当一个component的权重很小时，混合分布近似为单峰。
3. **LinkedIn connections的分布可以用来做什么？** 识别异常账户（bot检测）、推荐系统的cold-start分析、网络图分析中的degree distribution。

### 面试要点

- Part 1: 关键词 "bimodal distribution"，要能解释为什么合并后不是normal
- Part 2: 关键词 "right-skewed"，Mode < Median < Mean
- 准备好在白板上画出distribution的形状
- 被追问时可以讨论log-normal vs power-law的区别

---

## 6."""

    content = content.replace(q5_old, q5_new)

    # ── Add follow-ups to Q2 (N Random Variables) ──
    q2_old = """### 面试要点

- 先写iid case，再推广到correlated case
- 核心公式推导要流畅，注意 $\\frac{1}{N^2}$ 提出来
- **必须**主动联系Random Forest，这是面试官最想听到的
- 强调 $\\rho$ 是RF的核心bottleneck，解释feature subsampling如何降低 $\\rho$
- LinkedIn面经反复出现此题，是高频必考题

---

## 3."""

    q2_new = """### 常见Follow-up

1. **如果N个变量不同分布（方差不同）怎么办？** $\\text{Var}(\\bar{X}) = \\frac{1}{N^2}\\sum_i \\sigma_i^2$（iid情况下各方差不同时）。加权平均 $\\bar{X}_w = \\sum w_i X_i$ 中最优权重 $w_i \\propto 1/\\sigma_i^2$（inverse variance weighting）。
2. **Boosting中树的correlation？** Boosting的树是sequential的（每棵修正前一棵的残差），所以树之间有很强的dependency，不适用这个简单的averaging公式。Boosting通过shrinkage（learning rate）控制variance。
3. **如何实际测量RF中树的correlation？** 取每对树在同一组test data上的预测值，计算Pearson correlation，取平均。

### 面试要点

- 先写iid case，再推广到correlated case
- 核心公式推导要流畅，注意 $\\frac{1}{N^2}$ 提出来
- **必须**主动联系Random Forest，这是面试官最想听到的
- 强调 $\\rho$ 是RF的核心bottleneck，解释feature subsampling如何降低 $\\rho$
- LinkedIn面经反复出现此题，是高频必考题

---

## 3."""

    content = content.replace(q2_old, q2_new)

    # ── Add follow-ups to Q11 (MLE/GMM/EM) ──
    q11_old = """### 面试要点

- MLE推导要流畅，特别是对 $\\mu$ 和 $\\sigma^2$ 的求导
- 注意MLE的 $\\hat{\\sigma}^2$ 是biased的（除以n不是n-1）
- GMM不能直接MLE的原因: log里面有sum
- EM的两步要清楚: E-step算responsibility, M-step更新参数
- 强调EM收敛到local maximum，可以多次random initialization

---

## 12."""

    q11_new = """### 常见Follow-up

1. **EM和gradient descent的区别？** EM利用了问题的概率结构（latent variables），每步都保证似然不减。GD是通用优化，EM在某些结构化问题上收敛更快。
2. **如何选择GMM的K（component数）？** 用BIC (Bayesian Information Criterion，贝叶斯信息准则): $BIC = -2\\ell + k\\log n$，选择BIC最小的K。也可用AIC或交叉验证。
3. **MLE的asymptotic properties？** 在正则条件下，MLE是consistent（$\\hat{\\theta} \\to \\theta$），asymptotically normal，且asymptotically efficient（达到Cramer-Rao Lower Bound）。

### 面试要点

- MLE推导要流畅，特别是对 $\\mu$ 和 $\\sigma^2$ 的求导
- 注意MLE的 $\\hat{\\sigma}^2$ 是biased的（除以n不是n-1）
- GMM不能直接MLE的原因: log里面有sum
- EM的两步要清楚: E-step算responsibility, M-step更新参数
- 强调EM收敛到local maximum，可以多次random initialization

---

## 12."""

    content = content.replace(q11_old, q11_new)

    # ── Add follow-ups to Q13 (Biased Coin) ──
    q13_old = """### 面试要点

- 分两步走: biased -> fair -> uniform，不要试图一步到位
- Von Neumann's trick是核心，必须理解为什么(01)和(10)概率相等
- 解释rejection sampling的效率: 期望次数是有限的
- Follow-up: 如何优化？可以一次生成更多bits减少浪费

---

## 14."""

    q13_new = """### 常见Follow-up

1. **如何优化减少浪费？** 不丢弃(00)和(11)的结果，而是递归利用它们的信息。例如，(00)(11)序列本身也是一个biased coin（$P=p^2/(p^2+(1-p)^2)$），可以再次应用Von Neumann trick。
2. **如果p未知且非常接近0或1？** 效率极低，因为接受概率$2p(1-p)$趋近0。可以用Peres (1992)的iterated Von Neumann方法提高效率。
3. **如何生成0到N-1的均匀分布（N不是2的幂）？** 同样的rejection方法：找最小的$k$使得$2^k \\geq N$，生成k bit，reject $\\geq N$的结果。

### 面试要点

- 分两步走: biased -> fair -> uniform，不要试图一步到位
- Von Neumann's trick是核心，必须理解为什么(01)和(10)概率相等
- 解释rejection sampling的效率: 期望次数是有限的
- Follow-up: 如何优化？可以一次生成更多bits减少浪费

---

## 14."""

    content = content.replace(q13_old, q13_new)

    # ── Update appendix with new topics ──
    old_appendix_end = """*本文档整理自一亩三分地LinkedIn面经，覆盖了Phone Screen和Onsite ML Fundamentals轮次中出现的所有概率统计题目。建议结合白板练习公式推导和代码书写。*"""

    new_appendix_end = """| L1/L2 Regularization | Ridge closed-form + bias, Lasso sparsity | High |
| Linear vs Logistic | GLM framework, link functions | Medium |

---

*本文档整理自一亩三分地LinkedIn面经，覆盖了Phone Screen和Onsite ML Fundamentals轮次中出现的所有概率统计题目。建议结合白板练习公式推导和代码书写。每道题建议练习: (1) 写出核心公式推导 (2) 手写Python代码 (3) 准备2-3个follow-up回答。*"""

    content = content.replace(old_appendix_end, new_appendix_end)

    # Fix the appendix table -- add missing rows
    old_table_end = """| Biased -> Fair Coin | Von Neumann's trick | Low-Medium |

---"""

    new_table_end = """| Biased -> Fair Coin | Von Neumann's trick | Low-Medium |
| Overfitting (Trees) | max_depth, pruning, early stopping | Medium |
| L1/L2 Regularization | Ridge closed-form + bias, Lasso sparsity | High |
| Linear vs Logistic | GLM framework, link functions | Medium |

---"""

    content = content.replace(old_table_end, new_table_end)

    # Remove duplicate appendix rows (the ones we added at the end)
    content = content.replace(
        """| L1/L2 Regularization | Ridge closed-form + bias, Lasso sparsity | High |
| Linear vs Logistic | GLM framework, link functions | Medium |

---

*本文档整理自一亩三分地LinkedIn面经""",
        """---

*本文档整理自一亩三分地LinkedIn面经""",
    )

    return content


def main() -> None:
    """Enrich doc#21 and update database."""
    conn = sqlite3.connect(str(DB_PATH))
    original = get_content(conn)
    enriched = enrich(original)

    if original == enriched:
        print("WARNING: No changes were made!")
        conn.close()
        sys.exit(1)

    # Verify all replacements worked by checking for new content
    checks = [
        ("Q4 code", "def simulate_queues("),
        ("Q6 code", "def smote_1d("),
        ("Q7 code", "def ks_statistic("),
        ("Q8 code", "def demo_overfitting_tree("),
        ("Q9 code", "def ridge_regression("),
        ("Q10 code", "def bootstrap_sample("),
        ("Q14 code", "def glm_comparison("),
        ("CDF acronym", "CDF (Cumulative Distribution Function"),
        ("iid acronym", "iid (independent and identically distributed"),
        ("OLS acronym", "OLS (Ordinary Least Squares"),
        ("SMOTE acronym", "SMOTE (Synthetic Minority Over-sampling Technique"),
        ("AUC-ROC acronym", "AUC-ROC (Area Under the Receiver Operating Characteristic"),
        ("OOB acronym", "OOB (Out-of-Bag"),
        ("Q1 follow-ups", "Alias Method具体怎么实现"),
        ("Q2 follow-ups", "Boosting中树的correlation"),
        ("Q3 follow-ups", "randomized controlled trial"),
        ("Q5 follow-ups", "Log-normal和Power-law怎么区分"),
        ("Q11 follow-ups", "EM和gradient descent的区别"),
        ("Q13 follow-ups", "如何优化减少浪费"),
    ]

    failed = []
    for name, check_str in checks:
        if check_str not in enriched:
            failed.append(name)

    if failed:
        print(f"FAILED checks: {failed}")
        # Debug: save to file for inspection
        with open("_debug_enriched.txt", "w", encoding="utf-8") as f:
            f.write(enriched)
        conn.close()
        sys.exit(1)

    # Update database
    cur = conn.cursor()
    cur.execute(
        "UPDATE company_documents SET content=?, updated_at=datetime('now') WHERE id=21",
        (enriched,),
    )
    conn.commit()

    print(f"Original: {len(original)} chars")
    print(f"Enriched: {len(enriched)} chars")
    print(f"Added: {len(enriched) - len(original)} chars")
    print(f"All {len(checks)} checks passed")
    print("Database updated successfully")

    conn.close()


if __name__ == "__main__":
    main()
