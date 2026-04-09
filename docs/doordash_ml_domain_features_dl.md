# DoorDash ML Domain Prep: Feature Engineering + Deep Learning Modules for RecSys

> DoorDash ML Domain Knowledge Interview Prep
> Interviewer: Ajaykrishna Karthikeyan | Date: 2026-04-14
> Focus: Feature Engineering, Embeddings, Attention Mechanisms, Sequence Models, GNNs, Feature Interactions

---

## 1. Feature Engineering for RecSys

### 1.1 Four Feature Categories

推荐系统的特征可分为四大类, 每类在 ranking model 中扮演不同角色:

| Category | Description | DoorDash Examples |
|----------|-------------|-------------------|
| User Features | 用户画像 + 历史行为 | 历史订单频率, 平均客单价, 偏好菜系, 活跃时段, 配送地址 |
| Item Features | 物品/商家静态属性 | 商家评分, 菜品价格, 配送费, 菜系标签, 营业时间 |
| Context Features | 实时上下文信号 | 时间 (午餐/晚餐), 天气, 用户位置, 设备类型, 是否首单 |
| Cross Features | 用户-物品交互特征 | 用户对该商家的历史下单次数, 用户对该菜系的偏好度, 距离 |

### 1.2 DoorDash Feature Engineering 特殊性

DoorDash 作为三边市场 (消费者-商家-骑手), 特征工程有独特挑战:

**供给侧特征 (Supply-Side)**:
- 商家实时营业状态, 当前订单负荷, 预计出餐时间
- 骑手可用性, 配送区域覆盖率
- 菜品库存状态 (售罄标记)

**需求侧特征 (Demand-Side)**:
- 区域订单密度, 高峰时段预测
- 用户 price sensitivity (通过 DashPass 状态, 历史订单金额推断)

**实时特征 (Real-Time)**:
- ETA 预估 (影响用户决策的关键因素)
- 动态定价 / 配送费
- Surge pricing 状态

### 1.3 Feature Processing Pipeline

```
Raw Data Sources
    |
    v
[Feature Store]  -- 离线特征 (daily batch) + 在线特征 (streaming)
    |
    v
[Feature Transformation]
    |-- Numerical: log-transform, z-score, bucketing
    |-- Categorical: hashing, embedding lookup
    |-- Sequence: recent N interactions -> embedding
    |-- Cross: user x item interaction history
    |
    v
[Feature Serving] -- low-latency lookup (<5ms)
    |
    v
Model Input
```

**离线 vs 在线特征**:
- **离线** (batch, 小时/天级更新): 用户长期偏好, 商家历史评分, 菜系 embedding
- **近线** (streaming, 分钟级): 最近30分钟订单数, 商家当前等待时间
- **在线** (real-time, 请求级): 用户位置, 当前时间, 请求上下文

---

## 2. Embedding Techniques

### 2.1 ID Embedding

最基本的 embedding 方式: 为每个离散 ID 分配一个可学习向量.

$$e_i = W_{embed}[i] \in \mathbb{R}^d$$

- **优点**: 简单高效, 端到端学习
- **缺点**: 冷启动问题 (新 ID 无训练数据), 高基数时参数量爆炸

**DoorDash 应用**: User ID embedding, Store ID embedding, Cuisine ID embedding

### 2.2 Hashing Trick (Feature Hashing)

解决高基数离散特征的参数爆炸问题:

$$\text{index} = \text{hash}(\text{feature\_value}) \mod B$$

其中 $B$ 是 hash bucket 数量.

- **优点**: 固定参数量, 自动处理新 ID, 无需维护 vocabulary
- **缺点**: Hash 冲突导致信息损失
- **改进**: Double hashing -- 用两个 hash 函数, 拼接结果减少冲突影响
- **实践**: Facebook 的 DLRM 和 DoorDash 大规模 sparse features 都使用 hashing trick

### 2.3 Sequence Embedding

将用户行为序列编码为固定长度向量:

**方法一: Mean/Sum Pooling**
$$e_{user} = \frac{1}{T} \sum_{t=1}^{T} e_{item_t}$$

简单但丢失顺序信息.

**方法二: GRU/LSTM**
$$h_t = \text{GRU}(e_{item_t}, h_{t-1})$$
$$e_{user} = h_T$$

捕获序列依赖, 但长序列训练慢.

**方法三: Transformer**
$$e_{user} = \text{TransformerEncoder}([e_{item_1}, ..., e_{item_T}])$$

Self-attention 捕获任意距离的依赖, 并行训练; 但计算量 $O(T^2 d)$.

### 2.4 Pretrained Embeddings

利用外部预训练模型生成高质量 embedding:

| Source | Model | Feature | Use Case |
|--------|-------|---------|----------|
| Text | BERT / Sentence-BERT | 菜品描述, 商家名称, 用户 review | 语义匹配, cold-start |
| Image | CLIP / ResNet | 菜品图片, 商家封面 | 视觉吸引力, 图文匹配 |
| Graph | Node2Vec / GraphSAGE | User-Item 交互图 | 协同过滤信号 |

**BERT for DoorDash**:
- 菜品描述 embedding: 捕获 "spicy chicken sandwich" 和 "hot crispy chicken burger" 的语义相似性
- Query-item matching: 用户搜索 "ramen" 匹配 "Japanese noodle soup"

**CLIP for DoorDash**:
- 多模态匹配: 菜品图片 + 文字描述的联合 embedding
- 潜在应用: 用户拍照搜索 ("I want something like this")

### 2.5 Shared Embedding Tables

多任务 / 多模型间共享 embedding 以提高效率:

```
Embedding Table (Store ID -> d-dim)
       |
   +---+---+---+
   |       |       |
Retrieval  Ranking  Re-Ranking
Model      Model    Model
```

**优点**: 减少参数量, 训练信号更丰富 (所有任务共同更新 embedding), 推理时只维护一份
**挑战**: 不同阶段对 embedding 的需求不同 (retrieval 需要 ANN-friendly, ranking 需要 expressive)
**解决**: 共享 base embedding + 每个阶段的 task-specific projection layer

---

## 3. Attention Mechanisms in RecSys

### 3.1 DIN (Deep Interest Network, Alibaba 2018)

**核心思想**: 不同候选物品应该激活用户历史中不同的兴趣 -- 用 attention 做自适应加权.

```
候选物品 Ad
    |
    v
[Attention Unit]  <-- 计算 Ad 与每个历史行为的相关性
    |
User Behavior Sequence: [item_1, item_2, ..., item_T]
    |
    v
Weighted Sum = sum(alpha_i * e_i)  -- 动态用户兴趣表示
    |
    v
[MLP] -> CTR Prediction
```

**Attention 计算**:
$$\alpha_i = \frac{\exp(f(e_i, e_{ad}))}{\sum_j \exp(f(e_j, e_{ad}))}$$

其中 $f$ 是一个小型 MLP: $f(e_i, e_{ad}) = \text{MLP}([e_i, e_{ad}, e_i - e_{ad}, e_i \odot e_{ad}])$

**关键创新**:
- **不用 softmax 归一化**: DIN 原始实现中, attention weight 不做 softmax, 保留了 "总兴趣强度" 信息 (如果用户历史中没有相关行为, 所有 weight 都很小)
- **Dice 激活函数**: 自适应的 PReLU 变体, 根据数据分布调整激活阈值

### 3.2 DIEN (Deep Interest Evolution Network, Alibaba 2019)

**改进**: DIN 只建模静态兴趣, DIEN 建模兴趣的**演化过程**.

```
候选物品 Ad
    |
    v
[AUGRU] -- Attention-based GRU, 用 Ad 调制兴趣演化
    |
Interest Evolution: h_1 -> h_2 -> ... -> h_T
    |
[GRU] -- Auxiliary loss: 每步预测下一次点击
    |
Behavior Sequence: [item_1, item_2, ..., item_T]
```

**两层结构**:
1. **Interest Extractor (GRU)**: 从行为序列中提取兴趣状态, 辅助 loss 确保每步 hidden state 有效
2. **Interest Evolution (AUGRU)**: 用候选物品的 attention 调制 GRU 的 update gate, 只让相关兴趣参与演化

$$\tilde{u}_t' = \alpha_t \cdot u_t'$$

其中 $\alpha_t$ 是候选物品对时刻 $t$ 的 attention weight, $u_t'$ 是 GRU update gate.

### 3.3 BST (Behavior Sequence Transformer, Alibaba 2019)

**改进**: 用 Transformer 替换 GRU, 解决长序列建模问题.

```
候选物品 Ad
    |          \
    v           \
[Transformer Encoder]  -- Self-attention on behavior sequence + Ad
    |
[item_1, item_2, ..., item_T, Ad]  -- Ad 作为特殊 token 加入序列
    |
Position Encoding (learned)
```

**vs DIN/DIEN**:
- DIN: 只有 target attention, 行为间无交互
- DIEN: GRU 建模序列, 但受限于顺序处理, 长距离依赖困难
- BST: Self-attention 建模任意行为间的关系, 并行计算, 直接将候选物品加入序列做 cross-attention

**工程优化**: 序列长度截断 (通常取最近 50-200 个行为), 减少 $O(T^2)$ 计算开销.

### 3.4 AutoInt (Self-Attentive Feature Interaction)

(详见 ranking prep doc Section 1.6)

将 Multi-Head Self-Attention 应用于**特征交叉**, 而非行为序列. 每个特征 embedding 通过 attention 与其他特征交互, 自动学习高阶交叉.

### 3.5 Attention Mechanisms Comparison

| Model | Attention Target | Sequence | Key Innovation |
|-------|-----------------|----------|----------------|
| DIN | User history -> Candidate | No order | Target-aware interest |
| DIEN | User history -> Candidate | GRU (ordered) | Interest evolution + AUGRU |
| BST | Self-attention on sequence + candidate | Transformer | Parallel, long-range |
| AutoInt | Feature-feature interaction | N/A | Attention for feature cross |

---

## 4. Sequence Modeling for RecSys

### 4.1 GRU4Rec (ICLR 2016, Hidasi et al.)

**首个将 RNN 应用于 session-based recommendation** 的工作.

```
Session: [click_1, click_2, click_3, ...]
    |
    v
[GRU] -> [GRU] -> [GRU] -> prediction
```

- **Session-based**: 不需要用户长期历史, 只用当前 session 的点击序列
- **Ranking Loss**: BPR (Bayesian Personalized Ranking) 或 TOP1 loss
- **Mini-batch 并行**: 将不同 session 的同一时间步打包成 batch, 提高 GPU 利用率

$$L_{BPR} = -\frac{1}{N_s} \sum_{j=1}^{N_s} \log \sigma(\hat{r}_i - \hat{r}_j)$$

其中 $\hat{r}_i$ 是正样本 score, $\hat{r}_j$ 是负样本 score.

### 4.2 SASRec (Self-Attentive Sequential Recommendation, ICDM 2018)

**用 Transformer (单向) 建模用户行为序列**.

```
[item_1, item_2, ..., item_t]
    |
[Embedding + Positional Encoding]
    |
[Transformer Block x L]  -- Causal (left-to-right) attention
    |
[Prediction Head]  -- dot product with candidate item embedding
```

- **单向 Attention (Causal Mask)**: 只能看到历史, 不能看到未来, 适合序列推荐
- **Position Encoding**: Learned positional embedding, 而非 sinusoidal
- **vs GRU4Rec**: 并行训练, 长距离依赖更强, 在大多数数据集上表现更好

### 4.3 BERT4Rec (Sun et al., CIKM 2019)

**将 BERT 的 Masked Language Model 思想应用于推荐**.

```
[item_1, [MASK], item_3, ..., item_t]
    |
[Bidirectional Transformer]
    |
Predict masked items
```

- **双向 Attention**: 同时利用左右上下文, 比 SASRec 信息更丰富
- **Cloze Task**: 随机 mask 序列中的 items, 预测被 mask 的 item (类似 BERT MLM)
- **训练 vs 推理不一致**: 训练时随机 mask, 推理时 mask 最后一个位置 -- 存在 gap
- **vs SASRec**: BERT4Rec 在短序列上优势明显, 长序列上差距缩小

### 4.4 CL4SRec (Contrastive Learning for Sequential Recommendation, 2022)

**将对比学习引入序列推荐, 解决数据稀疏问题**.

**数据增强策略**:
- **Item Crop**: 随机裁剪子序列
- **Item Mask**: 随机 mask 部分 items
- **Item Reorder**: 随机打乱子序列顺序

```
Original Sequence: [A, B, C, D, E]
    |
Augmentation 1: [A, B, C]     (crop)
Augmentation 2: [A, [M], C, D, E]  (mask)
    |
[Shared Encoder (SASRec)]
    |
Contrastive Loss: same sequence augments -> positive pair
                  different sequences -> negative pairs
```

$$L_{CL} = -\log \frac{\exp(\text{sim}(z_i, z_i') / \tau)}{\sum_{j} \exp(\text{sim}(z_i, z_j') / \tau)}$$

**优势**: 自监督信号补充监督信号, 在稀疏场景 (冷启动用户) 效果提升显著.

### 4.5 Sequence Models Comparison

| Model | Architecture | Direction | Training Objective | Strength |
|-------|-------------|-----------|-------------------|----------|
| GRU4Rec | GRU | Left-to-right | BPR / TOP1 | 简单, session-based |
| SASRec | Transformer | Left-to-right (causal) | Next-item prediction | 并行, 长序列 |
| BERT4Rec | Transformer | Bidirectional | Masked item prediction | 上下文更丰富 |
| CL4SRec | Transformer + CL | Left-to-right | Next-item + Contrastive | 数据稀疏场景 |

**工业实践**: SASRec 架构 (单向 Transformer) 是工业界主流, 因为:
1. 推理时只需 append 新行为, 增量计算
2. 单向 attention 天然适配 "预测下一个" 的 serving 场景
3. BERT4Rec 的双向 attention 在推理时需要特殊处理

---

## 5. Graph Neural Networks for RecSys

### 5.1 Why Graphs for RecSys

推荐系统天然包含图结构:

```
User-Item Bipartite Graph:

User_A ---click---> Item_1
  |                   |
  +---order--> Item_2  +---also_bought---> Item_3
                        |
User_B ---click--------+
```

**图的优势**: 捕获高阶协同过滤信号 -- User_A 和 User_B 都与 Item_2 交互, 说明他们可能有相似偏好 (2-hop connection). 传统 CF 只看 1-hop.

### 5.2 GraphSAGE (Hamilton et al., NeurIPS 2017)

**核心思想**: 通过采样 + 聚合邻居信息学习节点表示, 支持 inductive learning.

$$h_v^{(l)} = \sigma\left(W^{(l)} \cdot \text{CONCAT}(h_v^{(l-1)}, \text{AGG}(\{h_u^{(l-1)}, \forall u \in \mathcal{N}(v)\}))\right)$$

**聚合方式**:
- Mean Aggregator: $\text{AGG} = \text{mean}(\{h_u\})$
- LSTM Aggregator: 将邻居随机排列后输入 LSTM
- Pooling Aggregator: $\text{AGG} = \max(\sigma(W_{pool} h_u + b))$

**关键特性**:
- **Inductive**: 对新节点也能生成 embedding (聚合已有邻居), 解决冷启动
- **Mini-batch 训练**: 采样固定数量邻居, 可扩展到大规模图
- **DoorDash 应用**: 新商家上线, 可通过同区域已有商家的图关系快速生成 embedding

### 5.3 GAT (Graph Attention Network, Velickovic et al., ICLR 2018)

**改进**: 不同邻居的重要性不同, 用 attention 自适应加权.

$$\alpha_{ij} = \frac{\exp(\text{LeakyReLU}(a^T [Wh_i \| Wh_j]))}{\sum_{k \in \mathcal{N}(i)} \exp(\text{LeakyReLU}(a^T [Wh_i \| Wh_k]))}$$

$$h_i' = \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij} W h_j\right)$$

- **Multi-Head Attention**: 类似 Transformer, 多个 attention head 捕获不同关系
- **vs GraphSAGE**: GAT 学习邻居权重, GraphSAGE 用预定义聚合 (mean/max)
- **局限**: 不如 GraphSAGE 可扩展 (attention 计算开销), 但小图上更准确

### 5.4 PinSage (Ying et al., KDD 2018, Pinterest)

**工业级 GNN**: Pinterest 将 GraphSAGE 扩展到 30 亿节点, 180 亿边的生产环境.

**关键工程优化**:
1. **Random Walk 采样**: 不用全邻居, 用 random walk 的访问频率确定重要邻居
2. **Importance Pooling**: 按 random walk 访问次数加权聚合, 比 uniform sampling 更有效
3. **Producer-Consumer 架构**: GPU 计算 + CPU 采样 pipeline, 最大化吞吐
4. **Curriculum Learning**: 从 easy negatives 逐步过渡到 hard negatives
5. **MapReduce 推理**: 离线 batch 生成所有 item embedding, 存入 ANN index

$$h_v = \text{ReLU}\left(W \cdot \text{CONCAT}\left(h_v, \frac{\sum_{u \in \mathcal{N}(v)} w_u \cdot h_u}{\sum_{u} w_u}\right)\right)$$

其中 $w_u$ 是 random walk 归一化访问频率.

**DoorDash 应用场景**: Store-Store 图 (同一用户在不同商家下单), Cuisine-Cuisine 图, User-Store bipartite graph.

### 5.5 LightGCN (He et al., SIGIR 2020)

**核心思想**: GCN 用于 CF 不需要 feature transformation 和 nonlinear activation -- 去掉反而更好.

$$e_u^{(l+1)} = \sum_{i \in \mathcal{N}(u)} \frac{1}{\sqrt{\mid\mathcal{N}(u)\mid} \sqrt{\mid\mathcal{N}(i)\mid}} e_i^{(l)}$$

$$e_u = \sum_{l=0}^{L} \alpha_l \cdot e_u^{(l)}$$

- **Layer Combination**: 最终 embedding 是各层 embedding 的加权和 (不只是最后一层)
- **简洁设计**: 只做邻居加权平均 + 层间聚合, 无 MLP, 无 activation
- **为什么有效**: 在 User-Item bipartite graph 上, 图结构本身就是最强的信号, 复杂的 transformation 反而引入噪声
- **BPR Loss**: 端到端训练, $L = \sum -\ln\sigma(\hat{y}_{ui} - \hat{y}_{uj}) + \lambda\|E^{(0)}\|^2$

### 5.6 GNN for RecSys Comparison

| Model | Aggregation | Scalability | Inductive | Key Feature |
|-------|------------|-------------|-----------|-------------|
| GraphSAGE | Sample + Aggregate | High (sampling) | Yes | 通用, inductive |
| GAT | Attention-weighted | Medium | Yes | 自适应邻居权重 |
| PinSage | Random walk + Importance | Very High (industrial) | Yes | 30B 节点级生产验证 |
| LightGCN | Symmetric norm, no MLP | High | No (transductive) | CF 场景最优简洁设计 |

---

## 6. Feature Interaction Models

### 6.1 FM (Factorization Machine, Rendle 2010)

**核心思想**: 用低秩分解建模所有特征对的二阶交叉.

$$\hat{y} = w_0 + \sum_{i=1}^{n} w_i x_i + \sum_{i=1}^{n}\sum_{j=i+1}^{n} \langle v_i, v_j \rangle x_i x_j$$

其中 $v_i \in \mathbb{R}^k$ 是特征 $i$ 的隐向量, $\langle v_i, v_j \rangle = \sum_{f=1}^{k} v_{if} v_{jf}$.

**计算技巧**: 交叉项可以化简为 $O(kn)$:

$$\sum_{i}\sum_{j>i} \langle v_i, v_j \rangle x_i x_j = \frac{1}{2}\left[\left(\sum_i v_i x_i\right)^2 - \sum_i (v_i x_i)^2\right]$$

**优势**: 在稀疏数据上比显式交叉特征更好 -- 即使特征对 $(i,j)$ 未共现, 通过 $v_i, v_j$ 各自与其他特征的共现也能学到交叉.

### 6.2 FFM (Field-aware Factorization Machine, Juan et al., 2016)

**改进**: FM 中每个特征只有一个隐向量; FFM 中每个特征对**每个 field** 有不同的隐向量.

$$\hat{y} = w_0 + \sum_i w_i x_i + \sum_{i}\sum_{j>i} \langle v_{i,f_j}, v_{j,f_i} \rangle x_i x_j$$

- 特征 $i$ 与 field $f_j$ 的特征交互时用 $v_{i,f_j}$, 与 field $f_k$ 的特征交互时用 $v_{i,f_k}$
- **参数量**: $O(nfk)$ vs FM 的 $O(nk)$, 其中 $f$ 是 field 数
- **效果**: Criteo CTR 竞赛冠军, 在 sparse features 多 field 场景下效果好
- **实践**: 因参数量大, 通常只用于特征数可控的场景

### 6.3 FiBiNET (Feature Importance and Bilinear Feature Interaction, 2019)

**核心思想**: 两个改进 -- (1) SENET 自动学习特征重要性, (2) Bilinear interaction 替代内积.

```
Input Features: [e_1, e_2, ..., e_n]
    |
[SENET Layer]  -- 学习特征重要性权重
    |           s_i = sigmoid(W_2 * ReLU(W_1 * z))
    v           where z = mean_pooling(e_i)
Weighted Features: [s_1*e_1, s_2*e_2, ..., s_n*e_n]
    |
[Bilinear Interaction]
    |-- Inner Product: <v_i, v_j>
    |-- Hadamard:      v_i . (W . v_j)
    |-- Bilinear:      v_i^T W v_j  -- 最灵活
    |
[Concatenate + MLP]
    |
Output
```

**SENET (Squeeze-Excitation Network)**:
- 从 CV 借鉴, 用于学习 feature importance
- Squeeze: 将每个 feature embedding 压缩为标量 (mean pooling)
- Excitation: 通过两层 MLP + sigmoid 生成 importance weight
- Re-weight: 按 importance 缩放原始 embedding

**Bilinear Interaction**:
- 普通内积 $\langle v_i, v_j \rangle$ 表达力有限
- Bilinear: $v_i^T W v_j$ 引入额外参数矩阵 $W$, 学习更丰富的交叉模式
- 三种变体: Field-All (一个共享 $W$), Field-Each (每对 field 一个 $W$), Field-Interaction (每个 field 一个 $W$)

### 6.4 Feature Interaction Evolution

```
Manual Cross Features (2010s)
    |
FM -- 自动二阶交叉, O(kn) (2010)
    |
FFM -- Field-aware, 更细粒度 (2016)
    |
DeepFM -- FM + DNN, 低阶+高阶 (2017)
    |
DCN/DCN-v2 -- 显式有界高阶 (2017/2020)
    |
FiBiNET -- SENET + Bilinear (2019)
    |
AutoInt -- Attention-based 交叉 (2019)
```

---

## 7. DoorDash Feature + DL Architecture Synthesis

### 7.1 Putting It All Together

DoorDash 的推荐系统可能的架构:

```
[User Features]  [Item Features]  [Context]  [User Behavior Seq]  [Graph Embedding]
     |                |              |              |                    |
  [Embed]          [Embed]       [Embed]     [SASRec/DIN]          [PinSage]
     |                |              |              |                    |
     +-------+--------+------+------+------+-------+--------------------+
             |
     [Feature Interaction Layer]  -- DCN-v2 Cross Network
             |
     [Multi-Task Tower]  -- MMoE / PLE
        /     |      \
    Click   Order   Satisfaction
    Head    Head      Head
```

### 7.2 DoorDash-Specific DL Design Considerations

**Challenge 1: Real-Time Features + Deep Models**
- 深度模型推理延迟 vs 实时特征更新频率
- 解决: 特征分层 -- 静态特征 batch 计算, 动态特征 online serving, 模型支持 partial feature update

**Challenge 2: Cross-Vertical Transfer**
- 餐厅/杂货/便利店的用户行为模式不同
- 解决: Shared embedding + vertical-specific tower (类似 MMoE 中不同 expert 对应不同 vertical)

**Challenge 3: Cold-Start**
- 新商家/新菜品无历史交互
- 解决: Content-based features (BERT/CLIP embedding) + Graph-based propagation (GraphSAGE inductive)

**Challenge 4: Sparsity**
- 长尾商家和低频用户的特征稀疏
- 解决: Feature hashing + contrastive learning (CL4SRec 思路) + side information embedding

---

## 8. Interview Q&A

### Q1: DoorDash 推荐系统中, 你会如何设计特征体系?

**A**: 我会按四层组织特征:

1. **User Features**: 长期偏好 (历史订单菜系分布, 平均客单价, 下单时段), 短期意图 (当前 session 浏览序列), DashPass 状态
2. **Store/Item Features**: 评分, 价格区间, 菜系, ETA, 配送费; 图片 embedding (CLIP), 描述 embedding (BERT)
3. **Context Features**: 时间 (meal time), 位置, 天气, 设备, 是否有 promotion
4. **Cross Features**: User-Store 历史 (下单次数, 最近下单时间), User-Cuisine affinity, 距离

特征处理上, 静态特征走 batch pipeline (daily), ETA/库存等走 streaming pipeline (分钟级), 请求级特征 online 计算. 用 Feature Store 统一管理离线/在线特征.

### Q2: 如何处理 DoorDash 的冷启动商家?

**A**: 多信号融合:

1. **Content Embedding**: 用 BERT 编码商家名称+菜品描述, CLIP 编码菜品图片, 获得语义 embedding
2. **Graph Propagation**: 用 GraphSAGE (inductive) 从同区域/同菜系的已有商家传播 embedding
3. **Meta-Learning**: 用相似商家的行为模式做 few-shot adaptation
4. **Exploration**: 给新商家一定曝光配额 (exploration bonus), 用 Thompson Sampling 或 UCB 平衡探索与利用

随着数据积累, 逐步从 content-based 过渡到 collaborative filtering signal.

### Q3: DIN 和 DIEN 的区别是什么? 什么场景用哪个?

**A**:
- **DIN**: Target attention -- 用候选物品对用户历史做 attention 加权. 建模**静态兴趣**, 不考虑行为顺序. 适合用户兴趣比较稳定, 行为序列不长的场景.
- **DIEN**: 在 DIN 基础上加了 GRU 建模兴趣演化. 两层结构: (1) Interest Extractor (GRU + auxiliary loss) 提取兴趣状态, (2) Interest Evolution (AUGRU) 用候选物品调制兴趣演化.

**选择**:
- 如果用户行为有明显时序模式 (如饮食偏好随季节变化, 从健康食品逐渐转向comfort food), 用 DIEN
- 如果更关注 "用户对这个商家感不感兴趣" 的静态匹配, DIN 更简单高效
- 工业实践中, BST (Transformer) 逐渐替代 DIEN, 因为并行训练更快, 长距离依赖更强

### Q4: PinSage 如何扩展到数十亿节点?

**A**: 四个关键工程:

1. **Random Walk 邻居采样**: 不遍历全邻居, 用 random walk 确定最重要的 top-K 邻居, 将 $O(\mid\mathcal{N}\mid)$ 降为 $O(K)$
2. **Importance Pooling**: 按 random walk 访问频率加权聚合, 比 uniform sampling 更有效捕获图结构
3. **Producer-Consumer Pipeline**: CPU 做图采样和特征加载, GPU 做前向/反向传播, 流水线并行
4. **Curriculum Learning**: 训练初期用 random negatives, 后期逐步引入 hard negatives (图距离近但非正样本), 避免模型初期被 hard negatives "带偏"
5. **MapReduce 离线推理**: batch 计算所有 item embedding, 存入 Faiss/HNSW ANN index, serving 时只做 ANN lookup

### Q5: LightGCN 为什么去掉 feature transformation 和 nonlinear activation 效果反而更好?

**A**: 核心原因是**图结构本身就是 User-Item CF 场景中最强的信号**.

- GCN 原始设计是为 node classification (有丰富 node features), feature transformation + ReLU 有助于学习复杂 feature 映射
- 在 CF 场景中, 节点特征只有 ID embedding (one-hot), 没有丰富的属性特征需要非线性变换
- 消息传递 (邻居平均) 本身就在做协同过滤 -- 2-hop 邻居 = "喜欢相同物品的用户也喜欢的其他物品"
- 多余的 $W$ 和 ReLU 反而引入过拟合风险, 因为每层变换会放大噪声
- Layer combination ($\sum_l \alpha_l e^{(l)}$) 融合了不同阶 (1-hop, 2-hop, ...) 的协同信号

### Q6: 对比学习 (CL4SRec) 如何帮助序列推荐?

**A**: 对比学习通过数据增强创造自监督信号:

1. **数据增强**: 对同一序列施加不同扰动 (crop, mask, reorder), 生成正样本对
2. **对比目标**: 同一序列的不同增强互为正样本, 不同序列互为负样本, InfoNCE loss 拉近/推远
3. **效果**: (a) 提供额外训练信号, 缓解标注稀疏 (尤其冷启动用户); (b) 学到更 robust 的序列表示 (对局部扰动不敏感); (c) 改善 embedding 空间的 uniformity

**DoorDash 场景**: 新用户只有几次下单, 监督信号极度稀疏. CL4SRec 风格的自监督可以从有限交互中学到更好的用户表示.

### Q7: Shared Embedding Table 在多阶段 pipeline 中有什么挑战?

**A**: 主要三个挑战:

1. **需求冲突**: Retrieval 需要 embedding 适合 ANN (内积/余弦空间结构好), Ranking 需要 embedding 富含信息 (可能不需要空间结构). 一个 embedding 难以同时满足.
2. **更新频率**: Retrieval model 更新频率可能低于 Ranking model; shared embedding 在一个模型更新后、另一个尚未更新时产生 inconsistency.
3. **梯度冲突**: 不同阶段的 loss 对同一个 embedding 施加不同方向的梯度, 可能导致训练不稳定.

**解决方案**: 共享 base embedding + task-specific projection. Base embedding 接收所有任务的梯度 (用 GradNorm 或 uncertainty weighting 平衡), 每个阶段再加一个轻量 projection layer 适配自身需求.

### Q8: Feature Hashing 的 collision 问题如何缓解?

**A**:

1. **增大 bucket 数**: 经验法则 -- bucket 数 >= 特征基数的 5-10x 时, 冲突影响可忽略
2. **Double Hashing**: 用两个独立 hash 函数, 拼接两个 embedding, 降低冲突概率 $p^2$
3. **Signed Hashing**: 附加一个 sign hash $s(x) \in \{+1, -1\}$, 使冲突 embedding 的期望为零
4. **Hybrid**: 高频特征用 ID embedding (无冲突), 长尾特征用 hashing (节省参数)

**DoorDash**: Store ID (数十万) 可用 ID embedding; Menu Item ID (数百万) 适合 hashing; Query token 用 hashing trick.

### Q9: 在 DoorDash 三边市场中, GNN 如何建模复杂关系?

**A**: 构建异构图 (Heterogeneous Graph):

**节点类型**: User, Store, Item, Cuisine, Region
**边类型**: User-order->Store, User-click->Item, Store-serves->Cuisine, Store-in->Region, Item-belongs->Store

**建模方式**:
1. **Relational GNN**: 不同边类型用不同的 transformation matrix, 如 R-GCN
2. **Meta-path**: User-order->Store-serves->Cuisine-serves<-Store = "与用户常点菜系相同的其他商家"
3. **Multi-relational PinSage**: 在不同关系上分别做 random walk + aggregation, 最终融合

**应用**: (1) Store retrieval: 通过 User-Store 图发现协同过滤信号. (2) Cross-vertical: Cuisine 节点连接不同 vertical 的 store, 实现跨品类推荐. (3) Cold-start: 新商家通过 Region + Cuisine 边接入已有图结构.

### Q10: 如何选择 DIN vs BST vs SASRec 用于 DoorDash 的用户行为建模?

**A**: 取决于场景和约束:

| Dimension | DIN | BST | SASRec |
|-----------|-----|-----|--------|
| Architecture | Target Attention | Transformer + Target Token | Causal Transformer |
| Sequence Length | 短 (~50) | 中 (~100-200) | 长 (~200+) |
| Stage | Ranking (候选已知) | Ranking | Retrieval / Pre-Ranking |
| 是否需要候选物品 | 是 (target-aware) | 是 (target as token) | 否 (next-item pred) |
| 延迟 | 低 | 中 | 中-高 |

**DoorDash Ranking**: BST 或 DIN. 候选商家已知, 需要 target-aware attention. BST 更强但推理更慢.

**DoorDash Retrieval**: SASRec 风格. 预测用户下一次可能下单的商家, 不依赖候选物品, 生成 user embedding 后做 ANN 检索.

**工程权衡**: DIN 最简单, 线上效果和延迟的 tradeoff 最好; BST 效果上限更高但需要更多 GPU; SASRec 适合 retrieval 但需要维护序列 embedding 的增量更新.
