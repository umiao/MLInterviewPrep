# DoorDash ML Domain Prep: ML Fundamentals Rapid Review + Quick-Fire Q&A

> DoorDash ML Domain Knowledge Interview Prep
> Interviewer: Ajaykrishna Karthikeyan | Date: 2026-04-14
> Focus: ML Fundamentals interspersed during domain interview

---

## 1. Optimization

### 1.1 SGD Family

| Optimizer | Update Rule | Key Idea | When to Use |
|-----------|------------|----------|-------------|
| SGD | $w \leftarrow w - \eta \nabla L$ | 最基本的梯度下降 | Convex problems, baseline |
| SGD+Momentum | $v \leftarrow \beta v + \nabla L$; $w \leftarrow w - \eta v$ | 动量累积加速收敛 | 大多数 CNN 训练 |
| Nesterov | 先看 momentum 方向, 再算梯度 | "前瞻" 减少振荡 | 改进版 Momentum |
| Adagrad | 每参数自适应 LR: $\eta / \sqrt{G + \epsilon}$ | 稀疏特征自动放大 LR | NLP / sparse features |
| RMSProp | 指数衰减的 $G$: $G \leftarrow \gamma G + (1-\gamma)g^2$ | 解决 Adagrad LR 单调递减 | RNN 训练 |
| Adam | Momentum + RMSProp + bias correction | 一阶矩 + 二阶矩自适应 | **默认首选**, 大多数 DL 任务 |
| AdamW | Adam + decoupled weight decay | 正确实现 L2 正则 | Transformer / BERT fine-tuning |
| LAMB | Layer-wise adaptive LR + Adam | 大 batch 训练稳定 | 分布式大规模预训练 |

**Adam 公式细节**:
$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$$
$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$$
$$\hat{m}_t = m_t / (1-\beta_1^t), \quad \hat{v}_t = v_t / (1-\beta_2^t)$$
$$w_t = w_{t-1} - \eta \cdot \hat{m}_t / (\sqrt{\hat{v}_t} + \epsilon)$$

默认超参: $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$

### 1.2 Learning Rate Scheduling

| Schedule | Formula | Characteristics |
|----------|---------|-----------------|
| Step Decay | 每 N epoch 乘以 $\gamma$ | 简单, 需要手动调 |
| Cosine Annealing | $\eta_t = \eta_{min} + \frac{1}{2}(\eta_{max}-\eta_{min})(1+\cos(\frac{t}{T}\pi))$ | 平滑下降, Transformer 常用 |
| Warmup + Cosine | 前 $T_w$ 步线性增长, 之后 cosine 衰减 | **Transformer 标配** |
| OneCycleLR | 先升后降, 一个大周期 | Super-convergence, 快速训练 |
| ReduceOnPlateau | 验证集 loss 停滞时降 LR | 自适应, 但延迟响应 |

**Warmup 的意义**: 训练初期 Adam 的二阶矩估计不准 (bias correction 不够), 小 LR 避免初始大梯度把模型带偏. 通常 warmup 5-10% 的总步数.

### 1.3 Gradient Issues

**Vanishing Gradient (梯度消失)**:
- 原因: 深层网络连乘 sigmoid/tanh 导数 (< 1), 梯度指数衰减
- 解决: ReLU 激活函数, Residual connections (ResNet), Batch Normalization, LSTM/GRU gating

**Exploding Gradient (梯度爆炸)**:
- 原因: 权重矩阵谱半径 > 1, 梯度指数增长
- 解决: Gradient clipping ($\lVert g \rVert > c \Rightarrow g \leftarrow c \cdot g / \lVert g \rVert$), 更小 LR, 权重初始化 (Xavier/He)

**Dead ReLU**:
- 原因: 负区间梯度为 0, 神经元永远不激活
- 解决: Leaky ReLU ($f(x) = \max(0.01x, x)$), PReLU, ELU, GELU

---

## 2. Regularization

### 2.1 Weight Regularization

| Method | Penalty Term | Effect on Weights | Use Case |
|--------|-------------|-------------------|----------|
| L1 (Lasso) | $\lambda \sum \lvert w_i \rvert$ | 稀疏化 (很多权重变为 0) | Feature selection |
| L2 (Ridge) | $\lambda \sum w_i^2$ | 均匀缩小权重, 不稀疏 | 防过拟合 (默认选择) |
| Elastic Net | $\lambda_1 \sum \lvert w_i \rvert + \lambda_2 \sum w_i^2$ | 结合 L1 稀疏 + L2 平滑 | 高维 + 共线性 |

**L1 为什么产生稀疏解**: L1 的梯度在 $w=0$ 处不连续 (subgradient 为 $\pm \lambda$), 优化路径倾向于"撞到"坐标轴上. 几何上, L1 约束区域是菱形, 等高线更容易在角点 (稀疏点) 相切.

### 2.2 Dropout

- 训练时随机以概率 $p$ 置零神经元, 推理时乘以 $(1-p)$ (或训练时用 inverted dropout: 除以 $1-p$)
- **Intuition**: 等价于训练 $2^n$ 个子网络的 ensemble; 防止 co-adaptation
- 常用 $p=0.1$ (Transformer) 到 $p=0.5$ (FC layers)
- **DropConnect**: 随机 mask 权重而非激活值 (更细粒度)
- **DropPath** (Stochastic Depth): 随机跳过整个 residual block, 用于深层网络

### 2.3 Normalization Layers

| Method | Normalization Dimension | When to Use |
|--------|------------------------|-------------|
| Batch Norm (BN) | across batch, per channel | CNN (batch 够大时) |
| Layer Norm (LN) | across features, per sample | **Transformer / NLP** (batch 大小无关) |
| Instance Norm (IN) | per sample, per channel | Style transfer |
| Group Norm (GN) | per sample, per channel-group | 小 batch CNN (detection/segmentation) |
| RMSNorm | Layer Norm without mean centering | LLaMA, 计算更快 |

**BN 公式**:
$$\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \quad y_i = \gamma \hat{x}_i + \beta$$

$\gamma, \beta$ 是可学习参数, 让网络可以恢复原始分布. 推理时用 running mean/variance.

**BN vs LN 的核心区别**: BN 在 batch 维度做归一化 (依赖 batch size, 不适合 RNN/变长序列), LN 在 feature 维度做归一化 (每个样本独立, 与 batch 无关).

### 2.4 Other Regularization Techniques

- **Data Augmentation**: 扩大有效训练集 (crop, flip, mixup, cutout, RandAugment)
- **Early Stopping**: 验证集性能不再提升时停止训练
- **Label Smoothing**: $y_{smooth} = (1-\alpha) y_{hard} + \alpha / K$, 防止过度自信
- **Weight Decay**: 等价于 L2 (SGD), 但 Adam 中 decoupled (AdamW) 效果更好

---

## 3. Evaluation Metrics

### 3.1 Classification Metrics

| Metric | Formula | When to Use |
|--------|---------|-------------|
| Accuracy | $(TP+TN) / N$ | 类别平衡时 |
| Precision | $TP / (TP+FP)$ | 关注"预测为正的准确性" (spam detection) |
| Recall | $TP / (TP+FN)$ | 关注"不漏掉正例" (cancer detection) |
| F1 | $2 \cdot P \cdot R / (P+R)$ | Precision-Recall 的 harmonic mean |
| AUC-ROC | TPR vs FPR 曲线下面积 | **阈值无关**的整体排序能力, 工业界常用 |
| AUC-PR (AP) | Precision vs Recall 曲线下面积 | **类别不平衡**时比 AUC-ROC 更有区分度 |
| Log Loss | $-\frac{1}{N}\sum [y\log p + (1-y)\log(1-p)]$ | 需要评估概率校准时 |

**AUC-ROC 解释**: 随机取一个正样本和一个负样本, 模型给正样本打分高于负样本的概率. AUC=0.5 等于随机, AUC=1.0 完美分离.

**为什么不平衡时 AUC-ROC 会误导**: 当负样本远多于正样本时, FPR = FP/(FP+TN) 中 TN 很大, 即使 FP 不少 FPR 也很小, 导致 ROC 曲线看起来很好. PR-AUC 不受 TN 影响, 更真实反映模型在正类上的表现.

### 3.2 Ranking Metrics

| Metric | Formula | Key Property |
|--------|---------|--------------|
| NDCG@K | $DCG@K / IDCG@K$ where $DCG = \sum_{i=1}^{K} \frac{2^{rel_i}-1}{\log_2(i+1)}$ | 考虑位置 + graded relevance |
| MAP@K | $\frac{1}{\lvert Q \rvert} \sum_q \frac{1}{\lvert R_q \rvert} \sum_{k=1}^{K} P(k) \cdot rel(k)$ | 考虑位置 + binary relevance |
| MRR | $\frac{1}{\lvert Q \rvert} \sum_q \frac{1}{rank_q}$ | 只关注第一个正确结果的位置 |
| Precision@K | Top K 中相关的比例 | 简单, 不考虑顺序 |
| Recall@K | Top K 中覆盖了多少相关的 | Retrieval 阶段核心指标 |
| Hit Rate@K | 至少一个相关出现在 Top K 的 query 比例 | Retrieval 简化版 |

**NDCG 的优势**: 同时考虑排序位置 (位置越靠前权重越大) 和相关性等级 (不仅仅是 0/1), 且归一化到 [0,1]. DoorDash 的 Ranking 模型常以 NDCG 为主要离线指标.

### 3.3 Calibration

模型输出的概率应该反映真实概率: 如果模型对一批样本预测 $p=0.3$, 其中应该约 30% 是正例.

**Calibration 方法**:
- **Reliability Diagram**: 将预测概率分桶, 画实际正比例 vs 预测均值
- **ECE (Expected Calibration Error)**: $\sum_{b=1}^{B} \frac{n_b}{N} \lvert acc_b - conf_b \rvert$
- **Platt Scaling**: logistic regression on logits ($p = \sigma(a \cdot z + b)$)
- **Temperature Scaling**: $p = \sigma(z/T)$, 只有一个参数 $T$ (post-hoc, 不影响排序)
- **Isotonic Regression**: 非参数, 阶梯函数拟合

**DoorDash 场景**: 排序模型的 CTR/CVR 预测需要 calibrated, 因为下游用于 bid optimization 和 revenue estimation. 如果预测系统性偏高/低, 会导致 GMV 预估不准.

### 3.4 Offline-Online Gap

离线指标好不代表线上效果好, 常见原因:

| Gap Source | Description | Mitigation |
|-----------|-------------|------------|
| Selection Bias | 离线数据只有被展示过的 item | Counterfactual learning, IPW |
| Position Bias | 用户更容易点击靠前的位置 | Position debiasing (PAL) |
| Delayed Feedback | 转化可能在展示后数天才发生 | Delayed conversion modeling |
| Distribution Shift | 模型上线后改变用户行为 | A/B test, 持续训练 |
| Metric Mismatch | 离线优化 AUC, 线上关心 GMV/DAU | 设计 proxy metric 尽量贴近业务 |
| Feature Leakage | 训练时用了未来信息 | 严格时间切分 |

**最佳实践**: 永远以 A/B test 结果为准. 离线评估用于快速筛选候选模型, 减少 A/B test 的次数.

---

## 4. Loss Functions

### 4.1 Classification Losses

| Loss | Formula | Use Case |
|------|---------|----------|
| BCE | $-[y\log\sigma(z) + (1-y)\log(1-\sigma(z))]$ | Binary classification (CTR/CVR) |
| Cross-Entropy | $-\sum_c y_c \log p_c$ | Multi-class classification |
| Focal Loss | $-\alpha_t (1-p_t)^\gamma \log(p_t)$ | **Class imbalance** (原 RetinaNet) |
| Hinge Loss | $\max(0, 1-y \cdot f(x))$ | SVM, margin-based |
| Label Smoothing CE | CE with $y_{smooth}$ | 防止 overconfident predictions |

**Focal Loss 详解**: 当 $\gamma > 0$ 时, 对"易分类样本" (高 $p_t$) 的 loss 大幅降低, 让模型聚焦于难例. $\gamma=2$ 是常用值. 在 DoorDash 中, 点击率通常只有几个百分点, focal loss 帮助模型关注少量正例.

### 4.2 Metric Learning Losses

| Loss | Input | Formula | Key Idea |
|------|-------|---------|----------|
| Contrastive | Pair | $y \cdot d^2 + (1-y) \cdot \max(0, m-d)^2$ | 正对拉近, 负对推远 |
| Triplet | (anchor, pos, neg) | $\max(0, d(a,p) - d(a,n) + m)$ | 正比负更近 + margin |
| InfoNCE | 1 pos + K neg | $-\log \frac{\exp(sim(q,k^+)/\tau)}{\sum_i \exp(sim(q,k_i)/\tau)}$ | SimCLR/CLIP/Contrastive Learning |
| Circle Loss | Flexible pairs | 自适应 margin + 加权 | 统一 pair-wise 和 class-level |

**Triplet Loss Mining**: 随机选 triplet 太容易 (大部分 margin 已满足, loss=0, 无梯度). 需要 hard negative mining (选最近的负例) 或 semi-hard mining (选 margin 内但正确侧的负例).

### 4.3 Regression & Ranking Losses

| Loss | Formula | Use Case |
|------|---------|----------|
| MSE | $\frac{1}{N}\sum(y-\hat{y})^2$ | 回归, 对 outlier 敏感 |
| MAE | $\frac{1}{N}\sum\lvert y-\hat{y}\rvert$ | 回归, robust to outlier |
| Huber | MSE if $\lvert e \rvert < \delta$ else MAE | 综合 MSE + MAE 优点 |
| Pairwise (BPR) | $-\log\sigma(s_i - s_j)$ for $i \succ j$ | 推荐排序 (BPR) |
| ListNet | CE between score distribution and relevance distribution | Listwise ranking |
| LambdaRank | 按 NDCG 变化量加权 pairwise loss | **直接优化 NDCG** |

---

## 5. Overfitting & Underfitting

### 5.1 Diagnosis

```
Training Loss Low  + Val Loss Low   = Good fit
Training Loss Low  + Val Loss High  = OVERFITTING
Training Loss High + Val Loss High  = UNDERFITTING
Training Loss High + Val Loss Low   = Data leakage / bug
```

### 5.2 Overfitting Solutions (by priority)

1. **More data** -- 最有效, 但往往最贵
2. **Data augmentation** -- 等效增加数据量
3. **Regularization** -- L2, Dropout, Label Smoothing
4. **Early stopping** -- 简单有效
5. **Reduce model size** -- 减少参数量
6. **Ensemble** -- Bagging 平均减少 variance

### 5.3 Underfitting Solutions

1. **Increase model capacity** -- 更多层/更宽
2. **Better features** -- Feature engineering, embeddings
3. **Train longer** -- 确认收敛了吗?
4. **Reduce regularization** -- 如果 regularization 过强
5. **Change architecture** -- 可能模型族不合适

### 5.4 Bias-Variance Tradeoff

$$Error = Bias^2 + Variance + Irreducible\ Noise$$

| | High Bias | High Variance |
|---|-----------|--------------|
| 表现 | Underfitting | Overfitting |
| Train Error | High | Low |
| Val Error | High | High |
| 模型 | 太简单 (linear model on complex data) | 太复杂 (deep net on small data) |
| 解决 | 加模型复杂度, 更好的特征 | 更多数据, 正则化, 减小模型 |

**Ensemble 如何降低 Variance**: Bagging (e.g., Random Forest) 独立训练多个 high-variance 模型, 预测取平均. 平均 $n$ 个独立模型, variance 降为 $\sigma^2/n$. Boosting 则主要降低 Bias (逐步修正残差).

---

## 6. Convex vs Non-Convex Optimization

### 6.1 Convex Functions

**定义**: $f(\lambda x + (1-\lambda)y) \leq \lambda f(x) + (1-\lambda) f(y)$, 任意两点连线在函数上方.

**性质**:
- 只有一个全局最优 (local minimum = global minimum)
- 梯度下降保证收敛到全局最优
- 例: Linear regression (MSE), Logistic regression, SVM (hinge loss)

### 6.2 Non-Convex in Deep Learning

**现实**: 深度网络的 loss landscape 是高度非凸的, 存在大量:
- **Local minima**: 很多, 但大部分质量接近全局最优 (经验发现)
- **Saddle points**: 高维空间中比 local minima 更常见, 梯度为 0 但不是极值
- **Plateaus**: 平坦区域, 梯度极小, 训练停滞

**为什么 SGD 仍然 work**:
1. 高维空间中, saddle point 的概率远大于 local minima (需要所有 Hessian 特征值同号)
2. SGD 的噪声帮助逃离 saddle points 和 sharp minima
3. 经验上, 大多数 local minima 的 loss 值很接近 (loss landscape 在高维中 "surprisingly well-behaved")
4. 过参数化 (overparameterization) 让 loss landscape 更平滑, 更容易优化

**Sharp vs Flat Minima**: Flat minima 泛化更好 (对参数扰动不敏感). Large batch training 倾向于 sharp minima (泛化差), 因此需要 warmup + large LR 等技巧.

---

## 7. Weight Initialization

| Method | Formula | Best For |
|--------|---------|----------|
| Xavier (Glorot) | $W \sim \mathcal{N}(0, 2/(n_{in}+n_{out}))$ | Sigmoid / Tanh |
| He (Kaiming) | $W \sim \mathcal{N}(0, 2/n_{in})$ | **ReLU** (标准选择) |
| Orthogonal | $W = QR$ decomposition | RNN |
| Pre-trained | Transfer learning | **NLP/CV 实际首选** |

**为什么初始化很重要**: 如果初始权重太大, 激活值爆炸 -> 梯度爆炸; 太小, 激活值趋向 0 -> 梯度消失. Xavier/He 保证前向传播和反向传播时激活值和梯度的方差在各层之间保持稳定.

---

## 8. Activation Functions

| Function | Formula | Range | Pros | Cons |
|----------|---------|-------|------|------|
| Sigmoid | $\sigma(x) = 1/(1+e^{-x})$ | (0,1) | 概率输出 | 梯度消失, 非零中心 |
| Tanh | $(e^x-e^{-x})/(e^x+e^{-x})$ | (-1,1) | 零中心 | 梯度消失 |
| ReLU | $\max(0,x)$ | $[0,\infty)$ | 简单高效, 缓解梯度消失 | Dead ReLU |
| Leaky ReLU | $\max(\alpha x, x)$ | $(-\infty,\infty)$ | 解决 Dead ReLU | 多一个超参 |
| GELU | $x \cdot \Phi(x)$ | smooth | **Transformer 标准** | 计算稍贵 |
| Swish/SiLU | $x \cdot \sigma(x)$ | smooth | 自门控, 效果好 | 计算稍贵 |
| Softmax | $e^{z_i}/\sum e^{z_j}$ | (0,1), sum=1 | 多分类概率输出 | 仅用于输出层 |

---

## 9. Feature Engineering for ML

### 9.1 Numerical Features

- **Normalization**: Min-Max ($[0,1]$) or Z-score ($\mu=0, \sigma=1$)
- **Log Transform**: 处理右偏分布 (e.g., price, revenue)
- **Binning / Bucketing**: 连续变量离散化, 捕捉非线性关系
- **Interaction Features**: $x_1 \times x_2$, 手动捕捉交叉效应

### 9.2 Categorical Features

- **One-Hot Encoding**: 低基数 categorical
- **Label Encoding**: tree models (有序)
- **Embedding**: 高基数 categorical (user_id, item_id), **DL 中首选**
- **Target Encoding**: 用目标变量均值编码, 注意 data leakage (需要 fold-wise)
- **Hashing Trick**: 固定维度, 处理未知类别

### 9.3 Text Features

- **TF-IDF**: 传统, 稀疏, 可解释
- **Word2Vec / GloVe**: 静态 word embedding
- **BERT / Sentence-BERT**: 上下文感知 embedding, 当前主流

### 9.4 DoorDash-Specific Features

| Feature Category | Examples |
|-----------------|----------|
| User | 历史订单类别分布, 平均客单价, 活跃时段, cuisine preference embedding |
| Store | 评分, 评论数, 客单价, prep time, 距离, 品类, 营业时段 |
| Context | 时间 (午餐/晚餐/深夜), 天气, 节假日, 位置 |
| Cross | user-store 历史交互次数, user-cuisine affinity, user-price_range match |

---

## 10. Quick-Fire Q&A

### Q1: Adam vs SGD -- 什么时候用哪个?
**A**: Adam 是默认首选, 收敛快, 超参鲁棒. 但在某些任务 (如 ImageNet 训练) SGD+Momentum 最终泛化更好, 因为 Adam 可能收敛到 sharp minima. 实际做法: Adam 快速探索, 最后用 SGD fine-tune (SWA). Transformer 训练一般全程用 AdamW.

**Follow-up**: Adam 为什么可能泛化差?
- Adam 的自适应 LR 对 informative gradient (大梯度) 反而缩小步长, 可能导致收敛到 sharp minima. 此外 Adam 的有效 LR bound 取决于 $\beta_2$, 接近 1 时步长可能过大.

### Q2: BN 在 training 和 inference 时的区别?
**A**: Training 时用当前 mini-batch 的 $\mu, \sigma^2$; Inference 时用训练过程中累积的 running mean/variance (exponential moving average). 因此 BN 在推理时不依赖 batch, 但训练时 batch size 太小会导致统计量不稳定.

**Follow-up**: 为什么 Transformer 用 LN 不用 BN?
- NLP 中 batch 内序列长度不同, BN 在 batch 维度计算统计量不合理. LN 对每个 sample 的 feature 维度归一化, 与 batch 无关, 更适合变长序列.

### Q3: AUC-ROC 是 0.95, 模型一定好吗?
**A**: 不一定. (1) 如果正负比例极端 (1:1000), AUC-ROC 可能虚高, 应该看 PR-AUC. (2) AUC 衡量的是排序能力, 不保证概率校准 (预测的 0.7 不一定真的是 70% 概率). (3) AUC 是全阈值的平均, 你实际部署时用的阈值区间可能 AUC 贡献很小. (4) Offline AUC 好不代表 online 效果好 (selection bias, distribution shift).

**Follow-up**: 怎么选择关注 Precision 还是 Recall?
- 取决于业务 false positive vs false negative 的代价. 垃圾邮件检测: FP 代价高 (误杀正常邮件) -> 优化 Precision. 癌症筛查: FN 代价高 (漏诊) -> 优化 Recall. DoorDash fraud detection: 平衡 (FP = 误封商家影响体验, FN = 损失钱).

### Q4: 什么是 Focal Loss? 为什么在 class imbalance 时比 BCE 好?
**A**: Focal Loss = $-\alpha_t(1-p_t)^\gamma \log(p_t)$. 对高置信度 (易分类) 样本降低权重 -- 例如 $p_t=0.9$ 时 $(1-0.9)^2 = 0.01$, loss 减少 100x. 这让模型把梯度集中在难例和少数类上. 相比 class weight rebalancing, Focal Loss 更细粒度 (按样本难度, 不仅按类别).

**Follow-up**: DoorDash 点击预测用 Focal Loss 吗?
- 可以用, 但实际中更常见的方案是: (1) 负采样 (negative sampling) 控制正负比例到 1:5~1:10. (2) Calibration layer 修正采样带来的概率偏差. Focal Loss 在 detection (RetinaNet) 中验证最多, CTR 场景业界用得不如负采样普遍.

### Q5: L1 vs L2 正则化怎么选?
**A**: L1 产生稀疏解 (自动 feature selection), L2 产生小但非零的权重 (smooth). 如果你有很多无关特征想自动筛选, 用 L1 (Lasso). 如果特征都有用只是想防过拟合, 用 L2 (Ridge). DL 中几乎都用 L2 / weight decay (因为特征选择由 embedding 层隐式完成).

**Follow-up**: Weight decay 和 L2 有什么区别?
- 对 SGD 它们等价: L2 penalty 的梯度就是 $\lambda w$, 更新后 $w \leftarrow (1-\eta\lambda)w - \eta g$. 但对 Adam, L2 的梯度被自适应 LR scale 了, 效果不一样. AdamW 把 weight decay 从梯度更新中 decouple 出来: $w \leftarrow (1-\lambda)w - \eta \cdot adam\_update$, 这才是"正确的" L2 效果.

### Q6: Gradient Clipping 怎么设置?
**A**: 两种方式: (1) **Clip by norm**: $\lVert g \rVert > c$ 时缩放到 $c$, 保持方向. (2) **Clip by value**: 每个分量截断到 $[-c, c]$, 可能改变方向. 通常用 clip by norm, $c=1.0$ 或 $c=5.0$. Transformer 训练标配 clip=1.0.

**Follow-up**: 什么时候需要 gradient clipping?
- RNN/LSTM 训练 (长序列反向传播), Transformer 训练 (大模型稳定性), 任何发现训练中 loss spike 的情况. 如果不 clip, 一个 outlier batch 的大梯度可能一步就毁掉模型.

### Q7: NDCG 和 MAP 的区别?
**A**: NDCG 支持多级相关性 (0/1/2/3), MAP 只有二值相关 (0/1). NDCG 用 $\log_2$ 做位置折扣, MAP 用 Precision@k 累积. 推荐系统中 NDCG 更常用因为相关性天然是连续的 (predicted score). 信息检索中 MAP 历史上更常用 (文档要么相关要么不相关).

**Follow-up**: DoorDash 用什么离线指标?
- 主要: NDCG (排序质量), AUC (点击预测). 辅助: MRR (第一个好结果位置), Recall@K (retrieval 阶段). 在线: CTR, CVR, GMV, order completion rate.

### Q8: 什么是 Temperature Scaling? 什么时候用?
**A**: $p = \text{softmax}(z/T)$. $T>1$ 使分布更平坦 (less confident), $T<1$ 更尖锐 (more confident). 用途: (1) Post-hoc calibration: 在 validation set 上优化 $T$ 使 ECE 最小, 不影响排序 (NDCG/AUC 不变). (2) Knowledge distillation: 高 $T$ 使 soft targets 更 informative. (3) LLM generation: $T$ 控制输出多样性.

**Follow-up**: Temperature Scaling 和 Platt Scaling 的区别?
- Temperature Scaling 只有 1 个参数 $T$, Platt Scaling 有 2 个参数 ($a, b$): $p = \sigma(az+b)$. Temperature 不改变排序, Platt 可能改变排序 (当 $b \neq 0$). Temperature 更简单, 过拟合风险更低.

### Q9: Dropout 在 test time 怎么处理?
**A**: Test time 关闭 Dropout (所有神经元都激活). 为了保持期望输出不变, 权重乘以 $(1-p)$ -- 或者更常见的做法是 **inverted dropout**: 训练时输出除以 $(1-p)$, 这样测试时不需要任何修改. PyTorch 的 `model.eval()` 自动处理.

**Follow-up**: MC Dropout 是什么?
- Monte Carlo Dropout: 推理时也开启 Dropout, 多次 forward pass, 取均值作为预测, 方差作为 uncertainty 估计. 这是一种近似 Bayesian inference, 用于 uncertainty quantification.

### Q10: 什么是 Gradient Accumulation? 什么时候用?
**A**: 多个 mini-batch 的梯度累加后再更新一次参数, 等效于更大的 batch size. 用于: GPU 内存不足以放大 batch (常见于 Transformer 大模型). 例如 batch=8 + gradient_accumulation_steps=4 等效于 batch=32, 但每次只用 batch=8 的显存.

**Follow-up**: 大 batch 训练有什么问题?
- (1) 泛化可能变差 (sharp minima). (2) 需要同步调大 LR (linear scaling rule: $\eta \propto B$). (3) 需要 warmup 稳定初期训练. (4) Communication overhead in distributed training. 解决: LARS/LAMB optimizer, warmup, cosine schedule.

---

## 11. Summary Cheatsheet

```
Optimizer:    Adam (default) -> AdamW (Transformer) -> SGD+Momentum (CV fine-tune)
LR Schedule:  Warmup + Cosine (Transformer) | ReduceOnPlateau (quick experiments)
Regularize:   L2/WeightDecay + Dropout + LabelSmoothing + EarlyStopping
Normalization: LN (Transformer) | BN (CNN) | GN (small batch CNN)
Activation:   GELU (Transformer) | ReLU/LeakyReLU (CNN) | Sigmoid (output only)
Init:         He (ReLU) | Xavier (Sigmoid/Tanh) | Pre-trained (NLP/CV)
Loss:         BCE (binary) | CE (multi-class) | Focal (imbalanced) | InfoNCE (contrastive)
Eval:         AUC-ROC + PR-AUC (classification) | NDCG@K (ranking) | ECE (calibration)
```
