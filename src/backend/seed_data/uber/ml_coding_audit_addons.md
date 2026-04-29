<!-- T-P1-635:AUDIT-AUX BEGIN -->
<h2 id="audit-aux-cards">6. Audit-Discovered 辅助卡片 (Depth-2 Auxiliary Cards)</h2>

> **来源**: T-P0-628 audit (`logs/uber_mlcoding_mlsd_audit.md` §2 NEW rows N7-N8). 这两张卡是 ML Coding 与 ML SD (Budget-constrained Promo) 之间的桥梁知识 — 在 Round 2 ML Coding 不会直接被要求"写代码", 但 Round 3 ML SD 谈到 uplift / 预算分配时, 面试官可能 drill 到 implementation 细节, 这两张卡负责把 "口头 SD 框架" 落到 "30 行 numpy 思路". Depth-2 = skeleton + bullets, 不展开成 Staff Golden full coding answer.

---

<h3 id="uplift-meta-learners">6.1 Multi-treatment Uplift Modeling 直觉卡 (S/T/X-learner + Calibration)</h3>

**Problem framing**: 给定 (X, T, Y) — feature, treatment indicator, outcome. 估计 individual treatment effect ITE = E[Y(1) - Y(0) | X = x]. 单一 binary treatment 时直接选 meta-learner; multi-treatment 时还要选 encoding.

**Meta-learner 速查表 (M = outcome model 数量)**:

| 学习器 | 训练流程 | M | 适用场景 | 主要弱点 |
|---|---|---|---|---|
| **S-learner** (Single) | 把 T 当成普通 feature, 训练单个 $\mu(X, T)$ | 1 | T 信号强 / 数据少 | 当 T 维度小 (1 bit) 而 X 高维, T 信号被淹没; 高 reg 下 ITE 估计为 0 |
| **T-learner** (Two) | 分别训练 $\mu_t(X), \mu_c(X)$, ITE = $\mu_t - \mu_c$ | 2 | treated/control 量级接近 | 不平衡时 minority 模型方差大; 不共享信息浪费 |
| **X-learner** (Cross) | (1) 同 T-learner 训 $\mu_t, \mu_c$; (2) impute counterfactual residual $D_t = Y - \mu_c(X)$ on treated, $D_c = \mu_t(X) - Y$ on control; (3) 训 $\tau_t(X), \tau_c(X)$ on residuals; (4) blend by propensity $g(x)$: $\tau(x) = g(x)\tau_c(x) + (1-g(x))\tau_t(x)$ | 4 + propensity | 高度不平衡 (e.g. treated 5%) | 4 模型 + propensity, 调参成本高 |
| **DR-learner** (Doubly Robust) | combine outcome + propensity model; 任一正确即 consistent | 2 + propensity | 不确定哪个 nuisance model 对 | 估计 propensity overlap 差时方差爆炸 |
| **Causal Forest** | 改造 random forest, split criterion = treatment-effect heterogeneity | tree ensemble | 非线性 + 自然 ITE 区间估计 | 黑盒, 解释难; 中小数据集 honest splitting 浪费样本 |

**Multi-treatment encoding trade-off** (T 不止 0/1, 而是 K 个 promo level $\{t_0, t_1, \ldots, t_{K-1}\}$):

| Encoding | 表征 | 参数量 | 适用 | 风险 |
|---|---|---|---|---|
| **One-hot** | T 编为 K-1 dummy | $\propto K$ | T 间无 ordinal 关系 (类别) | K 大时参数爆炸; 没见过的组合不能外推 |
| **Ordinal** | T 编为单 scalar (0,1,...,K-1) | $\propto 1$ | T 是 monotone ladder (e.g. 折扣金额 \$1/\$2/\$5) | 强假设线性单调; 错则误差大 |
| **Continuous** | T 直接是金额 \$amount | 1 | T 本质连续 | 训练域外预测 (e.g. \$50 promo 训练时只见过 \$1-10) 危险 |
| **Per-T 模型** | K 个独立 T-learner | $\propto K$ models | K 小 (≤ 5) + 数据多 | K 大时不可行 |

**面试常踩雷**: 候选人把 multi-treatment 当 K 个 binary 问题分别学 → 浪费跨 T 共享信息. 反之, 一律 one-hot 不利用 ordinal 结构 → 在 promo \$5 vs \$6 这种相邻档位上学不到 smoothness.

**Calibration via isotonic regression** (uplift 输出 → 可下游约束优化 (LP) 用):

- Uplift score 通常**不是校准 probability** — 它是 conditional treatment effect, 数值取决于 outcome 量纲 (revenue \$ / conversion rate / CTR). LP 需要可加 utility, 所以要 calibrate 到统一尺度.
- **Isotonic regression** = piecewise constant monotone fit. 优点: non-parametric, 保 rank order, 不假设 sigmoid 形状. 缺点: 数据少时阶跃噪声大.
- **Platt scaling** = 在 raw score 上拟合 logistic ($P = \sigma(a \cdot \text{score} + b)$). 优点: 数据少更稳; 缺点: 强假设 sigmoid 形状.
- **实操选择**: 校准集 ≥ 1k → isotonic (更 flexible); 校准集 < 1k → Platt.
- **Multi-T 校准**: 对每个 T level 单独 calibrate (T-by-T isotonic), 不要共享 — 不同 promo 的"高 uplift" 概率分布不同.

**Coding skeleton (X-learner, ~25 行)**:

```python
def x_learner(X, T, Y, X_test):
    # Step 1: outcome models
    mu_t = LightGBM().fit(X[T==1], Y[T==1])
    mu_c = LightGBM().fit(X[T==0], Y[T==0])
    # Step 2: imputed residual (counterfactual)
    D_treated = Y[T==1] - mu_c.predict(X[T==1])
    D_control = mu_t.predict(X[T==0]) - Y[T==0]
    # Step 3: treatment-effect models on residuals
    tau_t = LightGBM().fit(X[T==1], D_treated)
    tau_c = LightGBM().fit(X[T==0], D_control)
    # Step 4: blend by propensity g(x) = P(T=1|X)
    g = LogisticRegression().fit(X, T).predict_proba(X_test)[:, 1]
    return g * tau_c.predict(X_test) + (1 - g) * tau_t.predict(X_test)
```

**Cross-link**: 这张卡的下游是 [ml_sd_golden.md §5 Budget Promo Stage 3 — Uplift Modeling Deep Dive](#budget-promo-recommendation). SD 阶段被 drill "为什么选 X-learner 不选 S-learner", 答 "treated 占比只有 5%, S-learner 在 high-reg 下会把 treatment effect 估计为 0; X-learner 的 propensity-weighted blending 在 imbalance 下方差最低".

**6.1 行业黑话**:
- "**ITE vs ATE vs CATE**" — Individual / Average / Conditional Average treatment effect. CATE = ITE 但 conditioned on subgroup, 是 uplift 模型的目标.
- "**Counterfactual outcome**" — Y(1) given T=0 是反事实 — 不可观测, 必须 impute.
- "**Propensity overlap**" — overlap assumption: $0 < g(x) < 1$ for all $x$. 违反 (e.g. 某 segment 100% treated) → 因果识别失败.
- "**Doubly robust**" — DR-learner 即 outcome OR propensity 任一正确, 估计 consistent.
- "**Honest splitting**" (Causal Forest) — 用一半数据决定 split, 另一半估计 leaf treatment effect, 避免 overfitting bias.

---

<h3 id="lagrangian-relaxation">6.2 Lagrangian Relaxation 伪代码卡 (Binary-Search-on-λ)</h3>

**Problem framing**: 预算约束分配 (Budget-Constrained Promo Allocation) 原始 ILP:

$$\max_{x_{ia}} \sum_{i=1}^{N} \sum_{a=1}^{K} u_{ia} \cdot x_{ia} \quad \text{s.t.} \quad \sum_{i,a} c_{ia} \cdot x_{ia} \le B, \quad \sum_{a} x_{ia} = 1, \quad x_{ia} \in \{0, 1\}$$

直接 ILP solve 不 scale (N=10M users × K=5 promo levels = 5 × 10^7 binary vars). 标准做法: **Lagrangian relaxation + binary search on dual variable λ**.

**Dual reformulation**:

$$\mathcal{L}(x, \lambda) = \sum_{i,a} u_{ia} x_{ia} - \lambda \left( \sum_{i,a} c_{ia} x_{ia} - B \right) = \sum_{i} \sum_{a} (u_{ia} - \lambda c_{ia}) x_{ia} + \lambda B$$

**关键 insight**: 给定固定 $\lambda$, 拉格朗日量在用户间**完全 decouple** — 每个用户独立选 $a^*_i = \arg\max_a (u_{ia} - \lambda c_{ia})$. 这就把 N=10M 用户的 joint LP 拆成 N 个独立的 K-way argmax.

**Outer loop**: binary search on $\lambda$ 找使预算恰好绑定的 $\lambda^*$:

- $\lambda$ ↑ → 用户更倾向选 cheap action (因为 $-\lambda c$ 项主导) → 总开销 ↓
- $\lambda$ ↓ → 用户倾向选 expensive but high-utility action → 总开销 ↑
- 单调函数 → 二分

**Pseudocode (~14 行)**:

```python
def lagrangian_promo_allocate(u, c, B, lam_lo=0.0, lam_hi=10.0, tol=1e-3):
    """
    u: (N, K) utility (predicted incremental revenue per (user, action))
    c: (N, K) cost (promo dollar amount; c[:, 0] = 0 for no-promo baseline)
    B: scalar budget constraint
    Returns: (N,) chosen action index per user
    """
    while lam_hi - lam_lo > tol:
        lam = (lam_lo + lam_hi) / 2
        # Decoupled per-user argmax — vectorized O(NK)
        score = u - lam * c                      # (N, K)
        action = score.argmax(axis=1)            # (N,)
        spent = c[np.arange(len(c)), action].sum()
        if spent > B:
            lam_lo = lam                         # too expensive → push lam up
        else:
            lam_hi = lam                         # under-budget → pull lam down
    return action
```

**Complexity**:
- Per binary-search iteration: $O(NK)$ for vectorized score + argmax + cost-sum.
- Outer loop: $\log_2(\Lambda / \epsilon)$ iterations, 通常 ~30 次.
- Total: $O(NK \log(\Lambda / \epsilon))$ — 对 N=10^7, K=5, 30 iter → 1.5 × 10^9 elementary ops, vectorized numpy 上几秒钟.

**Why it scales to N=10M**:
1. **Per-user 独立** — 单 iteration 内 user-level 计算可 map-reduce / Spark partition.
2. **数值轻** — 没有 LP solver 的内点法 / simplex 大 matrix factorization.
3. **Warm start** — 每天 rerun 时 $\lambda^*$ 漂移小, 用昨天的值起 binary search 收敛更快.

**LP relaxation vs Lagrangian vs Greedy 对比**:

| 方法 | 解的精度 | 复杂度 | 何时用 |
|---|---|---|---|
| **直接 ILP** | 全局最优 | NP-hard, N≤1k 才可行 | 离线小问题 / debugging |
| **LP relaxation + rounding** | sub-optimal (rounding gap) | $O(N^{1.5})$ 或更差 (interior point) | N≤100k, 需精度证书 |
| **Lagrangian relaxation** | weak duality bound, gap 小 (~1%) | $O(NK \log(1/\epsilon))$ | **N=1M~100M canonical 选择** |
| **Greedy (sort by ROI = u/c)** | 0.5-approx for knapsack-like | $O(NK \log(NK))$ | baseline / 实时 fallback |

**Online 流式扩展**: 实际生产是 **PID controller pacing** 而非批量 binary search:
- $\lambda_t$ 跟踪累计花费 vs 计划花费, 用 PID 控制器 (proportional + integral + derivative) 调整 $\lambda$.
- 优点: 应对流量波动 / cost noise, day-of 不需重跑全量.
- 与离线 Lagrangian 一致性: 离线训出的 $\lambda^*$ 作为 PID 起点 + 安全边界.

**面试常踩雷**:
1. 候选人直接说"上 LP solver" → 没考虑 N=10M scale, 内点法 cubic complexity → fail Staff bar.
2. "Greedy by ROI" → 在 budget 紧 + cost 不一致时是 0.5-approx, 损失 50% utility, 错过 Lagrangian 的 ~99%-optimal.
3. 忘了 **complementary slackness** — 最优解在 budget 严格绑定时 $\lambda^* > 0$; budget 宽松时 $\lambda^* = 0$. 二分搜不到 binding point 要 short-circuit.

**Cross-link**: 这张卡的上游是 [ml_sd_golden.md §6 Budget Promo Stage 4 — Constrained Optimization](#budget-promo-recommendation). SD 阶段被 drill "为什么不直接 LP", 答 "N=10M 用户 × K=5 档 promo, LP 内点法 $O(N^{1.5})$ → 5 万亿 ops, 跑不动. Lagrangian 拆分到用户独立 argmax, $O(NK \log)$, 加 Spark map-reduce, 半小时一轮; 在线再用 PID 跟踪".

**6.2 行业黑话**:
- "**Weak duality**" — Lagrangian 给出原问题的 upper bound (max problem); gap 通常 < 1% 在凸/线性问题上.
- "**Complementary slackness**" — KKT 条件之一: 最优 $\lambda^*$ 与 budget constraint 绑定关系 ($\lambda^* (\sum c_{ia} x_{ia} - B) = 0$).
- "**Decoupling via dual**" — Lagrangian 的核心好处, 把 coupled 约束 (跨用户 budget) 转成 independent per-user subproblem.
- "**PID pacing**" — proportional-integral-derivative controller 在线 budget 跟踪, 业界标配 (Google AdWords / LinkedIn / Uber Promo 都用).
- "**Switchback test**" — 测 Lagrangian 策略 vs greedy/no-promo, time-bucketed switchback 比 user-randomization 更适合 marketplace 干预 (避免 spillover).

---

> **作者补注 (T-P1-635 audit-aux)**: 这两张卡的 ROI 在于"Round 3 ML SD 谈到 promo / uplift / Lagrangian 时, 你能 30 秒里把 implementation 思路打出来", 而不是真的去现场写 25 行代码. 把 §6.1 的 X-learner 4 步骤 + §6.2 的 binary search on λ 伪代码内化成口述能力即可.

<!-- T-P1-635:AUDIT-AUX END -->
