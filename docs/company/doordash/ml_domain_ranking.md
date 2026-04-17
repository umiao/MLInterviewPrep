# DoorDash ML Domain Prep: Ranking Models + Multi-Task Learning Deep Dive

> DoorDash ML Domain Knowledge Interview Prep
> Interviewer: Ajaykrishna Karthikeyan | Date: 2026-04-14
> Focus: Ranking Model Architectures, Multi-Task Learning, LTR, Multi-Objective Optimization

---

## 1. Deep Ranking Model Architectures

### 1.1 Evolution Timeline

```
LR + Manual Features (2010s)
    |
FM / FFM (Feature Interactions)
    |
Wide & Deep (2016, Google)
    |
DeepFM (2017, Huawei)
    |
DCN (2017, Google)  -->  DCN-v2 (2020, Google)
    |
xDeepFM (2018, MSRA)
    |
AutoInt (2019, Peking U)
```

### 1.2 Wide & Deep (Google, 2016)

**核心思想**: 将记忆能力 (memorization) 和泛化能力 (generalization) 结合.

```
          Output
           |
      [Sigmoid]
         |
    [Dense Layer]
       /     \
Wide Side    Deep Side
  |              |
[Cross features]  [Embedding -> MLP]
  |              |
raw features   sparse features
```

- **Wide**: 手动交叉特征 (e.g., `installed_app x impression_app`), 线性模型, 记忆 co-occurrence patterns
- **Deep**: Embedding + MLP, 学习 unseen feature combinations, 泛化到新的交叉

**联合训练**: $\hat{y} = \sigma(w_{wide}^T [x, \phi(x)] + w_{deep}^T a^{(L)} + b)$

**局限性**: Wide 侧需要手动特征工程, 交叉特征的选择依赖领域知识.

### 1.3 DeepFM (Huawei, 2017)

**改进**: 用 FM (Factorization Machine) 替换 Wide 侧, 自动学习二阶交叉.

```
          Output
           |
      [Sigmoid]
         |
    [Dense Layer]
       /     \
FM Component  Deep Component
  |              |
[Auto 2nd-order]  [Embedding -> MLP]
  |              |
  Shared Embedding Layer
         |
    sparse features
```

- **FM Component**: $\sum_{i=1}^{n}\sum_{j=i+1}^{n} \langle v_i, v_j \rangle x_i x_j$ -- 自动二阶交叉, $O(kn)$ 复杂度
- **共享嵌入**: FM 和 Deep 共享 embedding, 减少参数, 信息互补
- **优势**: 无需手动特征工程; FM 捕获显式交叉, DNN 捕获高阶隐式交叉

### 1.4 DCN / DCN-v2 (Google, 2017/2020)

**核心思想**: 用 Cross Network 显式建模有界高阶特征交叉.

**DCN Cross Layer**:

$$x_{l+1} = x_0 \cdot x_l^T w_l + b_l + x_l$$

其中 $x_0$ 是输入, $x_l$ 是第 $l$ 层输出. 每层增加一阶交叉, $L$ 层 Cross Network 建模最高 $(L+1)$ 阶交叉.

**DCN-v2 改进**:

$$x_{l+1} = x_0 \odot (W_l x_l + b_l) + x_l$$

- DCN 原版: weight 是向量 $w_l \in \mathbb{R}^d$, 输出是 $x_0$ 的秩-1 变换 -- 表达力受限
- DCN-v2: weight 是矩阵 $W_l \in \mathbb{R}^{d \times d}$, 输出是 $x_0$ 的全秩变换 -- 表达力更强
- **混合专家 (MoE) 变体**: $W_l = \sum_{i=1}^{K} G_i(x_l) \cdot E_i$, 用 gating 选择专家, 减少参数量

**DCN-v2 架构选择**:
- **Stacked**: Cross Network -> Deep Network, 串行
- **Parallel**: Cross Network || Deep Network, 最后拼接 -- 实践中通常效果更好

### 1.5 xDeepFM (MSRA, 2018)

**核心思想**: 在 vector-wise level (而非 bit-wise) 显式建模有界阶特征交叉.

$$X_k^h = \sum_{i=1}^{H_{k-1}} \sum_{j=1}^{m} W_{ij}^{k,h} (X_{k-1}^i \circ X_0^j)$$

- CIN (Compressed Interaction Network): 类似 CNN 的方式在 embedding vectors 之间做外积
- 每层产生 $H_k$ 个 feature maps, 第 $k$ 层建模 $(k+1)$ 阶交叉
- 最终 sum pooling 每层 feature maps, 拼接后输出

**vs DCN**: DCN 是 bit-wise 交叉 (标量级别); xDeepFM 是 vector-wise (embedding 向量级别), 保留了 field 结构信息.

### 1.6 AutoInt (2019)

**核心思想**: 用 Multi-Head Self-Attention 自动学习特征交叉.

$$\alpha_{ij}^h = \frac{\exp(\phi^h(e_i, e_j))}{\sum_{k} \exp(\phi^h(e_i, e_k))}$$
$$\tilde{e}_i^h = \sum_j \alpha_{ij}^h (W_{value}^h e_j)$$

- 每个 head 学习不同的交互模式
- 堆叠多层 attention = 高阶交叉
- **优势**: 可解释 (attention weights 可视化哪些特征交叉最重要)

### 1.7 Architecture Comparison Summary

| Model | Feature Cross | Order | Side Info | Params | Interpretability |
|-------|--------------|-------|-----------|--------|-----------------|
| Wide & Deep | Manual | Explicit 2nd | Manual | Low | High (Wide) |
| DeepFM | Auto (FM) | Explicit 2nd + Implicit high | None needed | Medium | Medium |
| DCN-v2 | Auto (Cross Net) | Bounded L+1 | None needed | Medium-High | Medium |
| xDeepFM | Auto (CIN) | Bounded, vector-wise | None needed | High | Medium |
| AutoInt | Auto (Attention) | Unbounded | None needed | Medium | High (attn weights) |

**实践选择**: DCN-v2 (Parallel) 是目前工业界最常用的 ranking model backbone, 兼顾表达力与训练稳定性. DoorDash 的 Universal Ranker 大概率基于类似架构.

---

## 2. Multi-Task Learning (MTL) for Ranking

### 2.1 为什么 Ranking 需要 MTL

推荐系统的 ranking 阶段需要同时预测多个用户行为:

| Task | Label | Business Meaning |
|------|-------|-----------------|
| Click | 0/1 | 用户是否点击商家/菜品 |
| Add-to-Cart | 0/1 | 是否加入购物车 |
| Order (Conversion) | 0/1 | 是否最终下单 |
| Order Value | float | 订单金额 (GMV) |
| Satisfaction | 0/1 | 订单后满意度 / 评分 |
| Reorder | 0/1 | 是否复购 |

**单任务 vs 多任务**:
- 单任务: 为每个目标训练独立模型, 参数不共享, 无法利用任务间相关性
- 多任务: 共享底层表示, 不同任务互为正则, 数据效率更高, 部署成本更低

### 2.2 Shared-Bottom (Hard Parameter Sharing)

```
Task A Head    Task B Head
    |              |
  [MLP_A]       [MLP_B]
    \             /
     Shared Bottom
         |
    [Shared MLP]
         |
      Features
```

- **优点**: 简单, 参数少, 天然正则化
- **缺点**: 所有任务被迫使用相同的底层表示 -- 当任务关联性弱 (如 click vs satisfaction) 时, 会发生 **负迁移 (negative transfer)**: 一个任务的梯度干扰另一个任务的学习

### 2.3 MMoE (Multi-gate Mixture-of-Experts, Google 2018)

**核心思想**: 多个专家网络 + 每个任务有独立的 gating network, 软选择专家组合.

```
Task A Head         Task B Head
    |                   |
  [MLP_A]             [MLP_B]
    |                   |
Gate_A output       Gate_B output
    |                   |
   Sum(g_A * experts)  Sum(g_B * experts)
    |                   |
    +---+---+---+---+---+
    | E1 | E2 | E3 | E4 |    <-- Shared Expert Pool
    +---+---+---+---+---+
            |
         Features
```

$$f^k(x) = \sum_{i=1}^{n} g_i^k(x) \cdot E_i(x)$$

其中 $g^k(x) = \text{softmax}(W_{gate}^k \cdot x)$ 是任务 $k$ 的 gating 输出.

- **关键优势**: 不同任务可以 softly 选择不同的专家组合, 减少负迁移
- **Gate 学到什么**: 高关联任务的 gate 分布相似; 低关联任务的 gate 分布差异大
- **实验验证**: 在任务相关性低时, MMoE 显著优于 Shared-Bottom; 任务相关性高时, 二者接近

### 2.4 PLE (Progressive Layered Extraction, Tencent 2020)

**改进 MMoE**: 引入任务特有专家 (task-specific experts) 和渐进式提取.

```
           Task A Head          Task B Head
               |                    |
           [Tower_A]            [Tower_B]
               |                    |
Gate_A:   [g_A * experts]     [g_B * experts]     <-- Extraction Layer 2
               |                    |
         +----+----+----+----+----+----+
         |EA_2|EA_2| ES_2|ES_2|EB_2|EB_2|         <-- Task-A, Shared, Task-B Experts
         +----+----+----+----+----+----+
               |                    |
Gate_A:   [g_A * experts]     [g_B * experts]     <-- Extraction Layer 1
               |                    |
         +----+----+----+----+----+----+
         |EA_1|EA_1| ES_1|ES_1|EB_1|EB_1|         <-- Task-A, Shared, Task-B Experts
         +----+----+----+----+----+----+
                       |
                    Features
```

- **三类专家**: Task-specific (只对应一个任务), Shared (所有任务共享), 各自由任务 gate 加权
- **渐进提取**: 多层 extraction, 每层逐步细化任务特有表示
- **vs MMoE**: PLE 显式区分共享 vs 任务特有, 更好地防止负迁移; 多层结构让表示逐步分化

### 2.5 ESMM (Entire Space Multi-Task Model, Alibaba 2018)

**解决问题**: CVR (conversion rate) 预估面临 **样本选择偏差 (sample selection bias)** -- 训练集只有被点击的样本, 但推理时需要对所有曝光样品预测.

**核心公式**:

$$P(\text{conversion} \mid \text{impression}) = P(\text{click} \mid \text{impression}) \times P(\text{conversion} \mid \text{click})$$

即 $pCTCVR = pCTR \times pCVR$

- CTR 任务在全量曝光空间训练 (无偏)
- CVR 任务隐式地也在全量空间学习 (通过乘法关系)
- 两个 tower 共享 embedding 层
- **DoorDash 应用**: $P(\text{order}) = P(\text{click on restaurant}) \times P(\text{order} \mid \text{click})$

### 2.6 Progressive Training & Curriculum

**渐进式训练策略**:

1. **Pre-train shared layers** on the most data-rich task (e.g., CTR has most labels)
2. **Add auxiliary tasks** gradually, starting from most related
3. **Task sampling**: 按任务样本量或重要性调整 mini-batch 中不同任务的比例

**Curriculum learning**:
- 先学简单任务 (click prediction), 再学困难任务 (long-term satisfaction)
- 简单任务的梯度帮助底层特征学习; 困难任务再微调上层

### 2.7 Negative Transfer: Detection & Mitigation

**症状**: 加入新任务后, 原有任务的指标下降.

**诊断方法**:
1. 单任务 baseline vs 多任务, 逐任务对比
2. 观察 gate 分布 -- 如果某任务的 gate 几乎均匀, 说明没有找到有用的专家模式
3. 梯度冲突分析: 不同任务在共享参数上的梯度是否方向相反

**缓解策略**:
- MMoE/PLE 架构 (soft routing)
- Gradient surgery: PCGrad (投影掉冲突方向), CAGrad (找 Pareto 改善方向)
- Task weighting: 动态调整任务权重 (见 Section 5)
- 增加 task-specific capacity

---

## 3. DoorDash Universal Ranker

### 3.1 Architecture Reconstruction

基于 DoorDash 公开技术博客和行业实践推测:

```
                  pClick    pOrder    pSatisfaction    ETA_error
                    |          |           |              |
                 [Task-specific Towers (MLP each)]
                    |          |           |              |
                  Gate_1    Gate_2     Gate_3          Gate_4
                    \         |          |             /
                     Expert_1  Expert_2  Expert_3  Expert_shared
                           \      |       /
                        Cross Network (DCN-v2)
                               |
                     [Feature Processing Layer]
                               |
         +----------+----------+----------+----------+
         | User     | Store    | Item     | Context  |
         | Features | Features | Features | Features |
         +----------+----------+----------+----------+
```

**特征分类 (DoorDash 视角)**:

| Category | Examples |
|----------|---------|
| User | 历史订单频次, 品类偏好, 平均消费, 位置, 活跃时段 |
| Store | 评分, 品类, 价格区间, 准备时长, 历史订单量, 新商家标记 |
| Item | 菜品名 embedding, 价格, 热度, 照片质量分 |
| Context | 时间 (午餐/晚餐/深夜), 天气, 节假日, 促销, 地理距离, ETA |
| Cross | User-Store 交叉 (用户对该品类的历史), User-Context (用户在该时段的偏好) |

### 3.2 Multi-Objective Final Score

最终排序分通常是多目标加权:

$$score = w_1 \cdot pClick + w_2 \cdot pOrder + w_3 \cdot pOrder \cdot estimatedGMV + w_4 \cdot pSatisfaction - w_5 \cdot ETApenalty$$

权重通过 A/B 实验和业务目标调整. 可能有 Pareto 优化或约束优化方式 (见 Section 5).

---

## 4. Learning to Rank (LTR)

> 详细数学推导参考: `docs/prep_learning_to_rank.md`

### 4.1 三种范式

| Paradigm | Loss Formulation | Pros | Cons |
|----------|-----------------|------|------|
| Pointwise | $L = \sum_i \ell(f(x_i), y_i)$ | 简单, 标准回归/分类 | 忽略文档间相对顺序 |
| Pairwise | $L = \sum_{i>j} \ell(f(x_i) - f(x_j))$ | 捕获偏好关系 | $O(n^2)$ 对, 不直接优化排名指标 |
| Listwise | $L = \sum_q \ell(\pi_q, y_q)$ | 直接优化 NDCG 等指标 | 复杂度高, NDCG 不可微需近似 |

### 4.2 LambdaMART -- 工业标准

**核心公式**:

$$\lambda_{ij} = -\sigma(1 - P_{ij}) \cdot \lvert\Delta NDCG_{ij}\rvert$$

其中 $P_{ij} = \sigma(\sigma(s_i - s_j))$ 是模型预测 $i$ 排在 $j$ 前的概率, $\lvert\Delta NDCG_{ij}\rvert$ 是交换 $i, j$ 位置后的 NDCG 变化.

**关键洞察**: Lambda gradient = RankNet pairwise gradient $\times$ NDCG swap impact. 这使得:
- Top 位置的错误获得更大梯度 (因为 $\Delta NDCG$ 更大)
- 隐式优化 NDCG, 无需 NDCG 可微

**LambdaMART = Lambda gradients + GBDT (XGBoost/LightGBM)**:
- 每轮 boosting: 排序 -> 枚举 pairs -> 计算 $\lambda_i, w_i$ -> 建树 -> 更新分数
- 工业中 LightGBM ranker 最常用

### 4.3 Deep LTR

Neural LTR 用 DNN 替代 GBDT:

- **Pointwise DNN**: 最简单, 预测 relevance score, 用 BCE/MSE loss
- **Pairwise DNN**: 用 RankNet loss 训练
- **Listwise DNN**: ApproxNDCG (用 sigmoid 近似排序), SoftRank, NeuralNDCG

**实践**: 大多数工业推荐系统在 ranking 阶段用 DNN pointwise (预测 pClick/pOrder) 而非纯 LTR loss. LTR loss 更多用于 search ranking (有 explicit relevance labels).

### 4.4 DoorDash LTR 应用

- **Search ranking**: 用户搜索 "pizza" -> 候选餐厅排序. 适合 LTR, 因为有 query-document 结构
- **Feed ranking**: 首页推荐, 没有 explicit query. 通常用 pointwise MTL (预测 click/order/satisfaction)
- **Hybrid**: Pre-ranking 用 LambdaMART (特征工程 + GBDT, 快且稳), Full ranking 用 DNN MTL

---

## 5. Multi-Objective Optimization & Fusion

### 5.1 Scalarization (线性加权)

$$\min_\theta \sum_{k=1}^{K} w_k \mathcal{L}_k(\theta)$$

- **优点**: 简单, 直观
- **缺点**: 权重 $w_k$ 需要手动调整; 只能找到凸 Pareto front 上的点; 不同 loss scale 需要归一化

### 5.2 Uncertainty Weighting (Kendall et al., 2018)

通过每个任务的 homoscedastic uncertainty 自适应调整权重:

$$\mathcal{L} = \sum_{k=1}^{K} \frac{1}{2\sigma_k^2} \mathcal{L}_k + \log \sigma_k$$

- $\sigma_k$ 是可学习参数, 表示任务 $k$ 的不确定性
- 高不确定性任务自动降权, 避免不确定的 loss 主导训练
- $\log \sigma_k$ 正则项防止 $\sigma_k \to \infty$ (等同于忽略所有任务)

### 5.3 GradNorm (Chen et al., 2018)

**核心思想**: 动态调整任务权重, 使所有任务的梯度 norm 在训练过程中保持平衡.

$$\tilde{G}_k(t) = \lVert w_k(t) \nabla_{\theta_{sh}} \mathcal{L}_k \rVert_2$$

目标: 让 $\tilde{G}_k(t)$ 接近共同目标 $\bar{G}(t) \cdot [r_k(t)]^\alpha$, 其中 $r_k(t) = \tilde{L}_k(t) / \bar{\tilde{L}}(t)$ 是任务 $k$ 的相对逆训练速度.

- 训练慢的任务 ($r_k$ 大) 被赋予更大权重
- $\alpha$ 控制平衡强度: $\alpha = 0$ 等同均匀权重; $\alpha$ 大则强制平衡

### 5.4 Pareto Optimization

**目标**: 找到 Pareto-optimal 解, 即没有任何目标可以改善而不恶化其他目标.

**MGDA (Multiple Gradient Descent Algorithm)**:
- 在共享参数的梯度空间中, 找到一个更新方向使所有任务的 loss 都不增
- 求解: $\min_{d} \lVert d \rVert_2^2 \quad s.t. \quad \nabla_\theta \mathcal{L}_k^T d \leq 0, \forall k$
- 等价于找梯度的最小范数凸组合

**PCGrad (Projecting Conflicting Gradients)**:
- 当两个任务梯度冲突 ($g_i \cdot g_j < 0$), 将 $g_i$ 投影到 $g_j$ 的法平面
- $g_i' = g_i - \frac{g_i \cdot g_j}{\lVert g_j \rVert^2} g_j$
- 简单有效, 可用于任何 MTL 架构

### 5.5 DoorDash Multi-Objective 实践

**Scalarization + Knob tuning**:
- 线性加权公式 (Section 3.2) 中的权重通过 A/B 实验确定
- 调整 $w_{GMV}$ vs $w_{satisfaction}$ 实现业务目标平衡

**Constraint-based**:
- 优化主目标 (GMV), 同时约束满意度不低于阈值
- $\max GMV \quad s.t. \quad satisfaction \geq \tau, \quad ETA \leq T_{max}$
- 实现: Lagrangian relaxation 或 constrained policy optimization

---

## 6. Advanced Topics

### 6.1 Calibration

**问题**: Ranking models 的预测分数是否是 well-calibrated probabilities?

**重要性**: 在 multi-objective scoring ($score = w \cdot pClick + ...$), 如果 pClick 系统性偏高, 最终排序被扭曲.

**方法**:
- **Platt Scaling**: 训练后, 学习 $\hat{p} = \sigma(a \cdot s + b)$ 将 logit 映射到校准概率
- **Isotonic Regression**: 非参数方法, 保序回归
- **Temperature Scaling**: $\hat{p} = \sigma(s / T)$, 学习温度 $T$

**Expected Calibration Error (ECE)**:

$$ECE = \sum_{m=1}^{M} \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$$

将预测分 bin 后, 比较每个 bin 的平均预测概率与真实正例比例.

### 6.2 Delayed Feedback

**问题**: Conversion 事件可能在 click 后数小时甚至数天发生. 如果训练时 label window 太短, 很多正例被错标为负例.

**方法**:

1. **Fake Negative Weighted (FNW)**: 对训练时标记为负的样本, 根据时间窗口赋予权重. 早期的 "负" 样本更可能是 fake negative, 给更低权重.

2. **DEFER (Delayed Feedback Estimation for Ranking)**: 联合建模 conversion probability 和 delay distribution:
   $$P(\text{no conversion by } t) = 1 - P(C=1) + P(C=1) \cdot P(D > t)$$
   其中 $D$ 是 delay 随机变量.

3. **Multi-window training**: 用多个 label window (1h, 24h, 7d) 训练不同模型, ensemble.

**DoorDash 场景**: 用户 click 后可能浏览菜单 10-30 分钟才下单. Label window 通常 1-2 小时. 深夜外卖的 delay 可能更长.

### 6.3 Sample Selection Bias

**问题**: 模型只在用户看到并交互过的数据上训练, 但推理时要对所有候选评分.

**Exposure bias**: 被展示在高位的 item 天然获得更多 click, 模型学到的是 "位置效应" 而非真实偏好.

**缓解**:
- **ESMM** (Section 2.5): 在全量曝光空间训练
- **Position debiasing**: 训练时加入 position feature, 推理时置为默认值
- **IPW (Inverse Propensity Weighting)**: 根据曝光概率反向加权:
  $$\mathcal{L}_{IPW} = \sum_i \frac{1}{p_i} \ell(f(x_i), y_i)$$
  其中 $p_i$ 是 item $i$ 被展示的概率

### 6.4 Position Bias & Unbiased LTR

**Position bias**: 用户更倾向点击排在前面的结果, 即使后面的结果更相关.

$$P(\text{click} \mid q, d, pos) = P(\text{examine} \mid pos) \cdot P(\text{relevant} \mid q, d)$$

**PAL (Position-Aware Learning)**: 训练时显式建模位置: $logit = f(x) + g(pos)$; 推理时去掉位置项.

**Unbiased LTR (IPW approach)**:
- 用 randomized experiments 估计 examination probability $P(\text{examine} \mid pos)$
- 每个样本权重 $= 1 / P(\text{examine} \mid pos)$
- 消除位置对学习的影响

---

## 7. Q&A: Expected Interview Questions

### Q1: Wide & Deep vs DeepFM vs DCN-v2, 你在实际项目中会怎么选?

**A**: 主要看特征交叉的需求和工程约束:
- **Wide & Deep**: 如果有强领域知识, 知道哪些特征交叉重要, 且需要快速迭代. 但 Wide 侧需要手动特征工程.
- **DeepFM**: 如果想自动学习二阶交叉, 不想做特征工程. FM 侧 $O(kn)$ 高效. 适合特征量大但交叉模式未知的场景.
- **DCN-v2**: 如果需要高阶显式交叉且愿意承受稍大的计算开销. Cross Network 可以建模到 $(L+1)$ 阶. 实践中 DCN-v2 Parallel 是最常见选择, 兼顾表达力和稳定性.
- **我的实际选择**: 在 eBay ranking 中, 我们用了类似 DCN-v2 的架构, 因为商品属性多, 需要自动发现高阶交叉 (如 price x brand x category x user_history).

### Q2: 解释 MMoE 和 PLE 的区别, 什么时候用哪个?

**A**:
- **MMoE**: 所有专家共享, 每个任务通过 gating 网络 softly 选择专家组合. 当任务之间有一定关联性时有效.
- **PLE**: 在 MMoE 基础上区分 task-specific 和 shared 专家, 且支持多层渐进提取. 当任务间关联性弱或有明确冲突时更好.
- **选择标准**: 如果任务高度相关 (如 click 和 add-to-cart), MMoE 足够. 如果任务相关性低 (如 click 和 long-term satisfaction) 或存在 seesaw effect (一升一降), PLE 更好. PLE 的代价是参数量更大, 训练更慢.

### Q3: 你怎么诊断和解决 MTL 中的负迁移?

**A**: 诊断流程:
1. **Baseline comparison**: 每个任务的单任务 baseline vs MTL 结果. 如果 MTL 后某任务指标下降, 确认负迁移.
2. **Gate analysis**: 查看 MMoE/PLE 的 gate 分布. 如果某任务的 gate 接近均匀分布, 说明没有找到有用的专家模式.
3. **Gradient conflict**: 计算不同任务在共享参数上的梯度余弦相似度. 持续为负说明严重冲突.

解决方案 (由轻到重):
1. 调整 loss weights (增大受害任务权重)
2. 使用 GradNorm 自动平衡
3. PCGrad 投影掉冲突梯度
4. 从 Shared-Bottom 升级到 MMoE, 或从 MMoE 升级到 PLE
5. 增加 task-specific capacity (更大的 tower)
6. 最后手段: 将冲突任务拆成独立模型

### Q4: DoorDash ranking 需要预测哪些目标? 最终排序分怎么算?

**A**: DoorDash 是三边市场 (消费者-商家-骑手), ranking 目标涵盖多方利益:

**预测目标**:
- $pClick$: 用户点击商家概率
- $pOrder$: 用户下单概率 (可用 ESMM 分解)
- $estimatedGMV$: 预估订单金额
- $pSatisfaction$: 用户满意度 (评分, 是否取消, 是否复购)
- $ETAPenalty$: 预估配送时间过长的惩罚

**最终排序分**:
$$score = w_1 \cdot pClick + w_2 \cdot pOrder \cdot estimatedGMV + w_3 \cdot pSatisfaction - w_4 \cdot ETAPenalty$$

权重通过线上 A/B 实验调优. 不同场景 (首页 feed vs 搜索结果 vs 促销 page) 的权重可能不同. 长期趋势是增加 $w_{satisfaction}$ 权重 (用户留存 > 短期 GMV).

### Q5: 解释 Calibration 在多目标排序中的重要性.

**A**: 如果 pClick 系统性高估 (如平均预测 0.3, 真实 0.2), 而 pOrder 校准准确, 那么最终 score 会 over-weight click, 倾向推荐高点击但低转化的 item (clickbait). 这违背了业务目标.

**实践**: 每个 task head 独立做 calibration:
1. 训练后, 在 held-out 集上做 Platt Scaling / Temperature Scaling
2. 监控 ECE, 设定阈值 (如 ECE < 0.02)
3. 定期 recalibrate (每天/每周), 因为分布会 drift

### Q6: 什么是 delayed feedback? DoorDash 场景下怎么处理?

**A**: 用户 click 餐厅后, 可能浏览菜单 15 分钟才下单. 如果训练 label window = 5 分钟, 很多真实转化被标为 negative.

**DoorDash 处理方案**:
1. **Label window 选择**: 通常 1-2 小时, 覆盖 95%+ 的真实转化
2. **FNW (Fake Negative Weighting)**: 对 window 内标为 negative 但 "可能是 fake" 的样本降权. 用历史 delay distribution 估计 fake negative 概率.
3. **训练数据 maturation**: 训练数据延迟 2+ 小时使用, 等 label 成熟
4. **多 window ensemble**: 短 window 模型 (实时性强) + 长 window 模型 (label 准确) ensemble

### Q7: ESMM 解决了什么问题? 还有其他方法吗?

**A**: ESMM 解决 CVR 预估的 **样本选择偏差**:
- CVR 传统训练集 = 被点击的样本 (biased subset)
- 但推理时要对所有曝光 item 预测 CVR

ESMM 通过 $pCTCVR = pCTR \times pCVR$ 绕过这个问题, CVR tower 隐式在全量空间训练.

**其他方法**:
- **全量空间直接训练**: 把 impression -> order 作为一个任务, 但正样本极稀疏
- **IPW**: 用 $1/P(\text{click})$ 加权 CVR 训练样本, 但方差大
- **DR (Doubly Robust)**: 结合 IPW + imputation, 更稳定
- **ESCM2 (Alibaba 2022)**: ESMM 升级版, 增加 counterfactual regularization

### Q8: Position bias 在 DoorDash feed ranking 中有多严重? 怎么处理?

**A**: DoorDash 首页 feed 是 vertical list, position bias 显著:
- Position 1 的 CTR 可能是 Position 10 的 5-10 倍
- 如果不处理, 模型会学到 "排在前面 = 好" 的 spurious correlation

**处理方案**:
1. **PAL (Position-Aware Learning)**: 训练时输入 position feature, 推理时置为固定值 (如 position=0)
2. **Randomized experiments**: 对小部分流量随机打乱排序, 收集无偏 click 数据用于评估
3. **Two-stage training**: 先用 randomized data 训练 examination model $P(\text{examine} \mid pos)$, 再用 IPW 训练 relevance model

### Q9: 比较 Uncertainty Weighting 和 GradNorm.

**A**:

| Dimension | Uncertainty Weighting | GradNorm |
|-----------|----------------------|----------|
| Principle | Task uncertainty -> weight | Gradient norm balance |
| Learnable | $\sigma_k$ per task | $w_k$ per task |
| Adaptation | Based on loss magnitude | Based on training speed |
| Key insight | 高 uncertainty 降权 | 慢任务加权 |
| Computation | 极低 (额外 K 参数) | 中 (需要计算梯度 norm) |
| Works well when | Tasks have different noise | Tasks train at different speeds |

**实践**: 可以组合使用 -- Uncertainty Weighting 做初始化, GradNorm 做动态调整.

### Q10: 如果 DoorDash 要从单目标 (CTR) 升级到多目标 ranking, 你会怎么做?

**A**: 分阶段推进:

**Phase 1: 基线验证**
- 保持单目标 CTR 模型不变
- 增加 Order, GMV, Satisfaction 的离线评估指标
- 建立 multi-objective 评估框架 (不只看 AUC, 还看 NDCG@k, satisfaction@k)

**Phase 2: MTL 模型**
- 在 CTR 模型基础上加 task towers (click + order + satisfaction)
- 先用 Shared-Bottom, 验证 MTL 不伤害 CTR
- 如果有负迁移, 升级到 MMoE/PLE

**Phase 3: Multi-objective scoring**
- $score = w_1 \cdot pClick + w_2 \cdot pOrder \cdot GMV + w_3 \cdot pSat$
- 先用固定权重, A/B 实验选最佳组合
- 逐步引入 Uncertainty Weighting / GradNorm

**Phase 4: 持续优化**
- Calibration 监控
- Delayed feedback 处理
- Position debiasing
- 探索 Pareto-based 优化

**关键原则**: 每步都有 rollback plan. MTL 不该一步到位, 而是逐步增加复杂度, 每步验证不退化.
