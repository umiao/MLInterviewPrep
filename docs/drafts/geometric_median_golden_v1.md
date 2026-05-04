# Geometric Median (Weiszfeld + Vardi-Zhang variant)

> **TL;DR** -- 目标 $$f(x) = \sum_i \|x - p_i\|_2$$ 凸但不光滑 ($$L_2$$ 范数在 0 不可导). 非样本点处梯度 $$\nabla f = \sum_i (x - p_i)/\|x - p_i\|$$ 是 $$N$$ 个**单位向量**之和, $$\|\nabla f\| \leq N$$ -- GD 永不爆.
> **Plain GD**: 4 行 numpy, 但 constant lr 难调 (远点 grad $$\approx N$$ 大, 近最优时单位向量互消 $$\to 0$$, 一个 lr 通吃不了).
> **Adaptive-lr fix**: 取 $$\eta_t = 1 / \sum_i (1/d_i)$$, GD update 坍缩为 Weiszfeld 加权重心 $$x \leftarrow \sum (p_i/d_i) / \sum (1/d_i)$$ -- **Weiszfeld 即参数自由 adaptive-lr GD**.
> **退化情形**: iterate 撞到样本点 $$p_j$$ (multiplicity $$\eta_j$$) 时单位向量未定义. Vardi-Zhang KKT 证书: $$R = \|\sum_{i \notin J} (p_j - p_i)/d_i\| \leq \eta_j$$ 时 $$p_j$$ 即几何中位数; 否则 $$T(x)$$ 与 $$x$$ 凸组合.
> **复杂度**: 单步 $$O(nd)$$, 总 $$O(Tnd)$$, **线性收敛**. 1D 退化为排序 median.

---

## 1. Derivation -- gradient is a sum of unit vectors

$$f$$ 凸 (norm 之和) 但在每个 $$p_i$$ 处不光滑 ($$L_2$$ norm 在 0 处不可导).

**非样本点** ($$x \neq p_i, \forall i$$): 链式法则给

$$\nabla f(x) = \sum_i \frac{x - p_i}{\|x - p_i\|} = \sum_i u_i$$

每项是从 $$p_i$$ 指向 $$x$$ 的**单位向量**, 故 $$\|\nabla f\| \leq N$$ 全局有界.

**样本点** ($$x = p_j$$, multiplicity $$\eta_j$$, 索引集 $$J$$): 不可微, subdifferential

$$\partial f(p_j) = \Big\{ \sum_{i \notin J} u_i + v : \|v\| \leq \eta_j \Big\}$$

**最优性**: $$0 \in \partial f(p_j) \iff R = \big\|\sum_{i \notin J} u_i\big\| \leq \eta_j$$ -- Vardi-Zhang 的 KKT 证书.

---

## 2. Plain GD (constant lr)

```python
def geometric_median_gd(points, lr=0.01, max_iter=1000, eps=1e-8):
    x = points.mean(axis=0)
    for _ in range(max_iter):
        diff = x - points
        dist = np.maximum(np.linalg.norm(diff, axis=1, keepdims=True), eps)
        grad = (diff / dist).sum(axis=0)
        x = x - lr * grad
    return x
```

两点观察: (a) $$\|grad\| \leq N$$ 即使近样本点也不爆 -- `eps` 仅防 $$1/0$$, 不影响梯度尺度. (b) **近最优时单位向量互消**, $$\|grad\| \to 0$$: constant lr 远处震荡 / 近处龟速, 难通吃.

---

## 3. Adaptive lr is exactly Weiszfeld

把 lr 设成 $$\eta_t = 1 / \sum_i (1/d_i)$$ (即调和均值 / N), 代入 GD update:

$$x_{t+1} = x - \frac{1}{\sum_i 1/d_i} \sum_i \frac{x - p_i}{d_i} = \frac{\sum_i p_i / d_i}{\sum_i 1/d_i}$$

**这就是 Weiszfeld 不动点**: 加权重心, $$w_i = 1/d_i$$ -- **近样本拉力大**. 近样本点保守缩步 (步长被 $$1/\sum w_i$$ 拉小), 空旷处大步迈 -- **参数自由 adaptive GD**.

```python
def _weiszfeld_step(points, dists):                    # dists all > 0
    inv_d = 1.0 / dists                                # (n,)
    return (points * inv_d[:, None]).sum(0) / inv_d.sum()
```

也是 IRLS: $$\min \sum w_i \|x - p_i\|^2$$ 加权重心闭式解, 每步用上步距离重算权重 -- 与 LR Newton/IRLS 同族.

---

## 4. Zero-distance: subgradient certificate (Vardi-Zhang)

iterate 撞到样本点 $$p_j$$ (multiplicity $$\eta_j$$) 时 $$1/d_j$$ 爆, Weiszfeld 卡住. 工程修补 $$d_i \leftarrow d_i + \varepsilon$$ 避免 NaN, 但**改了不动点方程**, 解从真正的几何中位数偏成有偏估计.

**Vardi-Zhang variant** (unbiased) 用 Section 1 的几何最优性: 拆 sum 为命中 $$J$$ / 未命中 $$\overline{J}$$ 两半.

$$T(x) = \frac{\sum_{i \notin J} p_i / d_i}{\sum_{i \notin J} 1 / d_i}, \quad R = \Big\|\sum_{i \notin J} \frac{p_j - p_i}{d_i}\Big\|$$

$$T(x)$$ 是 active 部分 Weiszfeld 步; $$R$$ 是 subgradient norm. **$$R \leq \eta_j$$ 即 KKT 证书** -- $$p_j$$ 已是几何中位数, 直接停. 否则 $$\gamma = \max(0, 1 - \eta_j / R)$$, $$x_{t+1} = \gamma T + (1 - \gamma) x$$ -- 向 $$T$$ 走但被 $$\eta_j$$ 拉回 (尊重 subgradient 球约束).

```python
def _vardi_zhang_step(points, x, dists, singular):
    eta = int(singular.sum())
    pts_a = points[~singular]; inv_d = 1.0 / dists[~singular]
    T = (pts_a * inv_d[:, None]).sum(0) / inv_d.sum()
    R_vec = ((x - pts_a) * inv_d[:, None]).sum(0)
    R = float(np.linalg.norm(R_vec))
    if R <= eta:
        return x, True                                  # optimality cert
    gamma = max(0.0, 1.0 - eta / R)
    return gamma * T + (1.0 - gamma) * x, False
```

---

## 5. fit -- centroid init + main loop

Centroid 是 $$L_2^2$$ 最优解, 落在凸包内, 几乎不命中样本点. 主循环每步: 算 dist $$\to$$ 命中走 Vardi-Zhang (含证书短路) $$\to$$ 否则 Weiszfeld $$\to$$ 步长 $$\|\Delta x\| < \text{tol}$$ 停.

```python
def fit(points, max_iter=200, tol=1e-7):
    points = np.asarray(points, dtype=float)
    x = points.mean(axis=0)
    for _ in range(max_iter):
        diffs = points - x
        dists = np.linalg.norm(diffs, axis=1)
        singular = dists < tol
        if np.any(singular):
            x_new, done = _vardi_zhang_step(points, x, dists, singular)
            if done:
                return x_new
        else:
            x_new = _weiszfeld_step(points, dists)
        if np.linalg.norm(x_new - x) < tol:
            return x_new
        x = x_new
    return x
```

---

## 6. Plain GD vs Adaptive-lr Weiszfeld vs Vardi-Zhang

|            | Plain GD                       | Adaptive-lr Weiszfeld         | Vardi-Zhang variant            |
| ---------- | ------------------------------ | ----------------------------- | ------------------------------ |
| 退化处理   | $$\varepsilon$$ 防 $$1/0$$, 有偏 | $$1/0$$ NaN, 卡死             | KKT 证书 + 凸组合, **unbiased** |
| lr 调优    | 难调 (远震荡 / 近龟速)         | **参数自由** ($$\eta = $$ 调和均值/N) | 同 Weiszfeld                   |
| 收敛       | 视 lr, 一般慢                  | 不命中样本时 a.e. 全局最优    | 命中也收敛, 全局最优           |
| 实现       | 4 行                           | 4 行                          | +10 行 mask / $$R$$ / $$\eta$$ |

---

## 面试追问 (Cheat Sheet)

> **Q: 与 mean / coordinate-wise median 的关系?**

- $$L_2^2$$ 最优 $$=$$ **mean** (centroid), 闭式 $$O(n)$$, breakdown $$0$$.
- $$L_1$$ 最优 $$=$$ **逐轴 median**, 1D 排序 $$O(n \log n)$$, 见 [Best Meeting Point](db://262).
- $$L_2$$ 最优 $$=$$ **几何中位数** (本题), 不可分解, 必须迭代.

> **Q: Constant-lr GD 为啥难调, fix 是啥?**

- 远点处 $$\|grad\| \approx N$$ 大, 近最优时单位向量互消 $$\to 0$$: 固定 lr 要么远处震荡要么近处龟速.
- Fix: $$\eta_t = 1 / \sum_i (1/d_i)$$ (harmonic_mean$$/N$$), GD 解析坍缩为 **Weiszfeld** -- 参数自由.

> **Q: 收敛保证?**

- 凸 $$+$$ 下降: 不命中样本时 $$f$$ 单调降, 极限点一阶最优 $$\Rightarrow$$ 全局最优.
- 速度仅**线性**; Newton on smoothed $$f_\varepsilon$$ 二次收敛但单步 $$O(d^3)$$, Weiszfeld 单步 $$O(nd)$$ 更便宜.

> **Q: 离群点鲁棒性 -- breakdown point?**

- centroid: breakdown $$= 0$$ -- 一个样本飞走 centroid 跟着飞.
- 几何中位数: breakdown $$\approx 0.5$$ -- **过半**样本被污染才失效.
- 落地: **Robust Federated Aggregation** 用几何中位数聚合 client 梯度, 抵御 byzantine 客户端.

> **Q: $$N$$ 太大 ($$10^7+$$) 怎么办?**

- **Mini-batch SGD on subgradient**: 单步采 batch 跑 Weiszfeld 一步, 凸目标保证收敛.
- **Coreset / sublinear**: $$\tilde{O}(nd/\varepsilon)$$ 近似算法.
- 工业近似: centroid 或一步 Weiszfeld, 误差 1-5% 够用.

> **Q: 与 k=1 K-Means 的桥梁?**

- k=1 K-Means $$+$$ $$L_2^2$$ cost $$=$$ mean (centroid).
- k=1 K-Means $$+$$ $$L_2$$ cost (不平方) $$=$$ 几何中位数.
- 推广: **k-medians** ($$L_1$$, 逐轴 median); **k-medoids** (PAM, 强制中心是样本点) -- 同族 outlier-robust 聚类.

---

## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 50, 3
points = np.random.rand(N, D)
median = fit(points)
assert median.shape == (D,)
print(f"Geometric median: {median}")
print(f"Mean for comparison: {points.mean(axis=0)}")
```
