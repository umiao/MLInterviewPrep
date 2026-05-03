# Geometric Median (Weiszfeld + Vardi-Zhang variant)

> **TL;DR** -- $$\arg\min_x \sum_i \|x - x_i\|_2$$ 的 $$L_2$$ 多维"中位数". $$L_1$$ 可逐轴分解, $$L_2$$ 不可分解, 无闭式解.
> **核心循环**: (1) 距离 $$d_i = \|x - x_i\|$$; (2) Weiszfeld 不动点 $$x \leftarrow \sum w_i x_i / \sum w_i$$, $$w_i = 1/d_i$$; (3) $$\|\Delta x\| < \text{tol}$$ 停.
> **退化情形**: iterate 撞到样本点 $$x_j$$ 时 $$w_j \to \infty$$ -- Vardi-Zhang 拆 sum, 用 $$T(x)$$ 与 $$x_j$$ 的凸组合替代; 当 $$R \leq \eta_j$$ 直接证明 $$x_j$$ 就是几何中位数.
> **凸但不光滑**: 目标处处凸, 样本点处不可微; Weiszfeld 一阶下降, **线性收敛**到全局最优, 加 $$\varepsilon$$ 工程修补会改不动点 (有偏).
> **复杂度**: 单步 $$O(nd)$$, 总 $$O(Tnd)$$, $$T \approx 10\text{-}50$$. 1D 退化为排序 median $$O(n \log n)$$.

---

## 实现

### 0. Function signature

无训练状态, 单函数; 输入点集 + 收敛参数, 输出 $$d$$ 维中位数向量.

```python
import numpy as np

def geometric_median(points: np.ndarray,
                     max_iter: int = 200,
                     tol: float = 1e-7) -> np.ndarray:
    points = np.asarray(points, dtype=float)         # (n, d)
    x = points.mean(axis=0)                          # centroid init
    ...
```

### 1. Initialization -- centroid as starting point

Centroid 是 $$L_2^2$$ 最优解, 落在凸包内, 几乎不与样本点重合, 对噪声温和样本最稳; per-axis median 也常用, 但少数样本场景偶尔命中样本点立即触发退化分支.

```python
x = points.mean(axis=0)                              # (d,)
```

### 2. Standard Weiszfeld step -- IRLS update

权重 $$w_i = 1/d_i$$, 加权重心一次迈过去. 等价于 $$\min \sum w_i \|x - x_i\|^2$$ 的 IRLS 解 (每步基于上步距离重算权重) -- 与 Logistic Regression 的 Newton/IRLS 求解器同族.

```python
diffs = points - x                                   # (n, d)
dists = np.linalg.norm(diffs, axis=1)                # (n,)
inv_d = 1.0 / dists                                  # (n,)
x_new = (points * inv_d[:, None]).sum(axis=0) / inv_d.sum()
```

### 3. Degeneracy guard -- Vardi-Zhang variant

iterate 撞到样本点时 $$d_j = 0$$, 朴素 $$1/d_j$$ 触发 `inf` 污染整步. Vardi-Zhang 把 sum 拆"命中 / 未命中"两半: $$T(x)$$ 是只在未命中样本上的标准 Weiszfeld; $$R(x) = \|\sum_{i \notin J} (x - x_i)/d_i\|$$ 是次梯度的 norm. 当 $$R \leq \eta_j$$ (命中样本数), 当前点已是几何中位数 (最优性证书, 无需再迭代); 否则用 $$T(x)$$ 与命中点 $$x$$ 的凸组合更新.

```python
singular = dists < tol                               # (n,) bool
if np.any(singular):
    eta = int(singular.sum())                        # repeats at x
    inv_d = 1.0 / dists[~singular]                   # (m,)
    T = (points[~singular] * inv_d[:, None]).sum(axis=0) / inv_d.sum()
    R = float(np.linalg.norm(
        ((x - points[~singular]) * inv_d[:, None]).sum(axis=0)
    ))
    if R <= eta:                                     # x IS the geometric median
        return x
    gamma = max(0.0, 1.0 - eta / R)                  # else: anchor-point fallback
    x_new = gamma * T + (1.0 - gamma) * x
```

工程上常见的"$$d_i \to d_i + \varepsilon$$"修补能避免 NaN, 但**改了不动点方程**, 解从真正的几何中位数偏成有偏估计. Vardi-Zhang 是 unbiased 标准修正.

### 4. Main loop -- iterate with stopping criteria

把 step 2/3 编进迭代; 收敛判据是步长 $$\|x_{t+1} - x_t\| < \text{tol}$$, 配合 max_iter 二选一. 命中样本+证书条件触发时直接 return.

```python
for _ in range(max_iter):                            # Criterion 1: max iter
    diffs = points - x
    dists = np.linalg.norm(diffs, axis=1)

    singular = dists < tol
    if np.any(singular):
        eta = int(singular.sum())
        inv_d = 1.0 / dists[~singular]
        T = (points[~singular] * inv_d[:, None]).sum(axis=0) / inv_d.sum()
        R = float(np.linalg.norm(
            ((x - points[~singular]) * inv_d[:, None]).sum(axis=0)
        ))
        if R <= eta:
            return x                                 # Criterion 2: optimality cert
        gamma = max(0.0, 1.0 - eta / R)
        x_new = gamma * T + (1.0 - gamma) * x
    else:
        inv_d = 1.0 / dists
        x_new = (points * inv_d[:, None]).sum(axis=0) / inv_d.sum()

    if np.linalg.norm(x_new - x) < tol:              # Criterion 3: step size
        return x_new
    x = x_new
return x
```

---

## Vanilla Weiszfeld vs Vardi-Zhang variant

|              | Vanilla Weiszfeld          | Vardi-Zhang variant                      |
| ------------ | -------------------------- | ---------------------------------------- |
| 退化处理     | $$1/0$$ NaN, 卡死          | 拆 sum, 凸组合 + 最优性证书              |
| 收敛性       | iterate 不命中样本时 a.e.  | 命中也收敛, 全局最优                     |
| 实现复杂度   | 4 行                       | +10 行 mask / $$R$$ / $$\eta$$ 计算      |

**一句话**: 加 $$\varepsilon$$ 让 $$1/0$$ 不报错但改了不动点 (有偏); Vardi-Zhang 是 unbiased 标准修正 -- 工程默认值.

---

## 面试追问 (Cheat Sheet)

> **Q: 与 mean / coordinate-wise median 的关系?**

- $$L_2^2$$ 最优 $$=$$ **mean** (centroid), 闭式 $$O(n)$$, breakdown $$0$$.
- $$L_1$$ 最优 $$=$$ **逐轴 median**, 1D 排序 $$O(n \log n)$$, 见 [Best Meeting Point](db://262).
- $$L_2$$ 最优 $$=$$ **几何中位数** (本题), 不可分解, 必须 Weiszfeld.

> **Q: 为什么没闭式解?**

- 一阶条件 $$\sum (x - x_i) / \|x - x_i\| = 0$$ 含 $$x$$ 的 norm, 非线性方程, algebraic 解不出.
- 对比: $$L_1$$ 一阶条件是 sign 函数 (逐轴解耦); $$L_2^2$$ 是线性 (闭式 $$=$$ mean).

> **Q: 收敛保证?**

- 凸 $$+$$ 下降: iterate 不命中样本时 $$f$$ 单调降, 极限点满足一阶最优 $$\Rightarrow$$ 全局最优.
- 速度只是**线性** (一阶), 比 Newton on smoothed $$f_\varepsilon = \sum \sqrt{\|x - x_i\|^2 + \varepsilon^2}$$ (二次收敛, 单步 $$O(d^3)$$) 慢, 但每步 $$O(nd)$$ 便宜.

> **Q: 离群点鲁棒性 -- breakdown point?**

- centroid: breakdown $$= 0$$ -- 一个样本飞走 centroid 跟着飞.
- 几何中位数: breakdown $$\approx 0.5$$ -- **过半**样本被污染才失效.
- 落地: **Robust Federated Aggregation** 把 client 梯度做几何中位数, 抵御少数 byzantine 客户端.

> **Q: $$N$$ 太大 ($$10^7+$$) 怎么办?**

- **Mini-batch SGD on subgradient**: 单步采一个 batch 跑 Weiszfeld 一步, 凸目标保证收敛.
- **Coreset / sublinear**: $$\tilde{O}(nd/\varepsilon)$$ 近似算法, $$\varepsilon \leq 0.01$$ 时显著快.
- 工业近似: 直接 centroid 或一步 Weiszfeld, 误差 1-5% 通常够下游用.

> **Q: 与 k=1 K-Means 的桥梁?**

- k=1 K-Means $$+$$ $$L_2^2$$ cost $$=$$ mean (centroid).
- k=1 K-Means $$+$$ $$L_2$$ cost (不平方) $$=$$ 几何中位数.
- 推广: **k-medians** 用 $$L_1$$ (逐轴 median); **k-medoids** (PAM) 强制中心是样本点 -- 同族 outlier-robust 聚类.
