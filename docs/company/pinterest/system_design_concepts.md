# Pinterest System Design: 核心概念与术语 Deep-Dive Index

> Pinterest tab 主索引文档。各 H2 章节下沉每个核心概念的 deep-dive 内容；
> 七个 7 个 SD 文档（ad-ctr / embeddings / chatbot-pins / pin-ranking / pins-search /
> notification-reco / catalog-bulk-update）作为应用案例引用回此文档的对应章节。
>
> 编写策略: 中文叙事 + 全英文术语首次出现时给出 (Full English Form / 中文释义)；
> 只有此索引页里集中展开"是什么 / 为什么 / 何时用 / 与什么对比"，避免在 7 个 SD
> 子文档里重复堆叠。

---

## 1. 多任务与排序架构 (Multi-Task & Ranking Architectures)

> 这一节集中展开排序模型的演进谱系: 从 **Wide & Deep** 的 memorization+generalization
> 双塔, 到 **DeepFM/AutoInt/DCN-v2** 这条 "自动学 feature interaction" 主线, 再到
> **DLRM** 的工业标准化, 然后是检索侧的 **DSSM/Two-Tower**, 最后到多任务的 **MMoE/PLE**。
> 每个术语按 "Full Name + 直觉 + Pinterest 应用 + vs 替代方案" 4 段展开。

### B-1. Wide & Deep (W&D, 宽深模型)

- **Full Name**: Wide & Deep Learning for Recommender Systems (Google 2016).
- **直觉解释**: 把 **memorization** (wide 部分: 线性模型 + 人工 cross feature, 记住高频组合)
  和 **generalization** (deep 部分: 多层 MLP, 通过 embedding 学未见过的组合) 联合训练。
  公式上, $\hat{y} = \sigma(w_{wide}^\top [x, \phi(x)] + w_{deep}^\top a^{(L)} + b)$, 其中
  $\phi(x)$ 是人工 cross feature, $a^{(L)}$ 是 deep tower 最后一层激活。
- **Pinterest 实际应用**: 在 `system_design_pin_ranking.md` §4.3 替代方案表中,
  W&D 被列为"已被 MMOE + DCN-v2 超过"的 baseline; `system_design_ad_ctr.md` §4.2
  也把 W&D 作为对照组(优点: 简单, wide 部分可解释; 缺点: cross 特征需手工)。
- **何时选 vs 替代**: 当工程团队无能力维护 embedding 服务、且 cross feature 已有领域专家
  挖好时选 W&D。**vs DeepFM**: DeepFM 用 FM 自动学二阶 cross, 省掉人工 wide。

### B-2. DeepFM (Deep Factorization Machine, 深度因子分解机)

- **Full Name**: Deep Factorization Machine (Huawei 2017)。
- **直觉解释**: 把 W&D 的 wide 部分换成 **FM (Factorization Machine)**, 让模型自动学所有
  field 的二阶特征交叉。FM 部分: $\hat{y}_{FM} = w_0 + \sum_i w_i x_i + \sum_{i<j} \langle v_i, v_j \rangle x_i x_j$,
  其中 $v_i \in \mathbb{R}^k$ 是 field $i$ 的隐向量, 二阶 cross 通过内积自动学得, 无需人工设计。
  Deep 部分仍然是 MLP, 共享同一套 embedding。
- **Pinterest 实际应用**: `system_design_ad_ctr.md` §4.2 把 DeepFM 列为 L2 heavy ranker
  的 baseline 推荐选型, 因为广告侧 sparse feature 多 (user_country × ad_category × time-of-day),
  人工设计 cross 不现实。
- **何时选 vs 替代**: 短期上线、稀疏类目特征极多时选 DeepFM。**vs DCN-v2**: DCN-v2 显式
  cross 层可学高阶交叉 (3 阶以上), DeepFM 仅二阶; 但 DCN-v2 参数量更大。

### B-3. AutoInt (Automatic Feature Interaction Learning, 自动特征交叉)

- **Full Name**: Automatic Feature Interaction Learning via Self-Attentive Neural Networks (2019)。
- **直觉解释**: 用 **multi-head self-attention** 在 feature field 维度上做交叉,
  让每个 field 通过 attention 权重 "看到" 其他 field 来动态生成高阶组合。
  核心: $h_i = \sum_j \alpha_{ij} (W_v e_j)$, $\alpha_{ij} = \mathrm{softmax}_j(\langle W_q e_i, W_k e_j \rangle / \sqrt{d})$。
  堆叠 $L$ 层 attention 即可学到 $L$ 阶交叉。
- **Pinterest 实际应用**: `system_design_ad_ctr.md` §4.2 把 AutoInt 列为 A/B 候选模型 ——
  对解释性要求不高的广告 CTR 预估场景, 适合做 challenger 拿增量。
- **何时选 vs 替代**: 想要高阶 (3+) 特征交叉、且不在乎可解释性时选 AutoInt。
  **vs DCN-v2**: AutoInt 用 attention 隐式学交叉, DCN-v2 用 cross layer 显式构造,
  AutoInt 训练慢但表达力强。

### B-4. DCN-v2 (Deep & Cross Network v2, 深度与交叉网络 v2)

- **Full Name**: Deep & Cross Network V2 (Google 2020, V1 from 2017)。
- **直觉解释**: 在 deep MLP 之外并联一条 **cross network**, 显式构造任意阶特征交叉。
  v2 cross layer 公式:
  $$x_{l+1} = x_0 \odot (W_l x_l + b_l) + x_l$$
  其中 $\odot$ 是 element-wise 乘法, $x_0$ 是输入特征向量。$L$ 层堆叠后得到 $L+1$ 阶
  显式 cross。v2 相对 v1 把标量 $w_l$ 升级为矩阵 $W_l$, 表达力大幅提升。
- **Pinterest 实际应用**: `system_design_pin_ranking.md` §4.2 中, L2 heavy ranker 的
  shared bottom 就是 "embedding lookup + DCN-v2 cross + 3 层 MLP" 的组合, 用来在进
  MMoE expert 之前先做一遍显式 feature 交叉。
- **何时选 vs 替代**: 当 feature 之间已知有强 cross 信号 (如 user × pin × context),
  且需要可控的交叉阶数时选 DCN-v2。**vs DeepFM**: DCN-v2 阶数可调, DeepFM 固定二阶。

### B-5. DLRM (Deep Learning Recommendation Model, 深度推荐模型)

- **Full Name**: Deep Learning Recommendation Model (Meta 2019)。
- **直觉解释**: Meta 开源的工业级推荐基线。结构为: dense feature 过 bottom MLP → 与
  sparse feature embedding 一起做 **pairwise dot-product interaction** ($\langle e_i, e_j \rangle$,
  类似 FM 的二阶) → 拼接后过 top MLP → output。重点是用 model parallelism + data
  parallelism 组合训练超大 embedding table (TB 级)。
- **Pinterest 实际应用**: Pinterest 没有公开宣称使用 DLRM 命名的模型, 但 `system_design_ad_ctr.md`
  中 L2 ranker 的 "embedding + dense MLP + interaction + top MLP" 整体结构与 DLRM 同源,
  本质上是 DLRM 家族的变体。把 DLRM 作为面试中讨论 "工业级推荐基线长什么样" 的标准参考点。
- **何时选 vs 替代**: 在大规模分布式训练 (千亿参数 embedding) 场景下, DLRM 的 PyTorch
  开源实现 + FBGEMM 算子是最成熟选择。**vs DeepFM/DCN-v2**: DLRM 更工程化 (重 infra
  优化), DeepFM/DCN-v2 更模型创新 (重 interaction 设计)。

### B-6. DSSM (Deep Structured Semantic Model, 深度语义匹配模型)

- **Full Name**: Deep Structured Semantic Model (Microsoft 2013)。
- **直觉解释**: 最早的双塔 (two-tower) 范式 —— query 塔和 document 塔分别独立编码到
  同一向量空间, 训练目标用 cosine similarity + softmax over negatives。
  $\mathcal{L} = -\log \frac{\exp(\cos(q, d^+) / \tau)}{\sum_{d \in D} \exp(\cos(q, d) / \tau)}$。
  关键贡献: 把检索问题统一成 "embedding 相似度搜索"。
- **Pinterest 实际应用**: DSSM 是 `system_design_pins_search.md` §3.2 中 Two-Tower 模型的
  概念祖先 —— Pinterest 把 DSSM 思想升级为 BERT-small (query) + ViT/CLIP (pin image) 的
  现代 two-tower, 但训练目标 (in-batch InfoNCE) 仍然是 DSSM 范式的延伸。
- **何时选 vs 替代**: 当 query 和 doc 是异构模态 (text vs image) 且需要离线预计算 doc emb
  时选 DSSM 范式。**vs Cross-encoder (BERT pair)**: DSSM 慢一点但可 ANN 索引 (~1ms/查询);
  cross-encoder 精度高但每个 (query, doc) pair 要现场 forward, 无法做大规模检索。

### B-7. Two-Tower (双塔模型)

- **Full Name**: Two-Tower Model (DSSM 的现代统称, 也叫 Bi-Encoder)。
- **直觉解释**: user/query 塔和 item/doc 塔解耦, 在线只算 query 塔 (轻), item 塔
  离线预计算并灌进 ANN 索引。打分 = $\langle q_{\text{emb}}, p_{\text{emb}} \rangle / (\|q\| \|p\|)$。
  训练用 in-batch negatives + hard negatives + sampled softmax。优势: latency O(query tower)
  而不是 O(N items), 能做亿级候选检索。
- **Pinterest 实际应用**: 两个核心场景。**(1) 检索侧**: `system_design_pins_search.md` §3.2 用
  BERT-small + CLIP 的双塔做语义召回, HNSW 索引 5B pins。**(2) L1 light ranker**:
  `system_design_pin_ranking.md` §4.1 用双塔 DNN 做 2k → 600 的轻排, latency <20ms。
- **何时选 vs 替代**: 超大候选集合 (>1M) + 严格 latency 预算 (<50ms) 时必选 Two-Tower。
  **vs MMoE/DCN-v2**: 后者是 ranking model (输入 ~hundreds 候选, 算 cross feature),
  Two-Tower 是 retrieval model (输入 ~millions 候选, 不算 user-item cross)。

### B-8. MMoE (Multi-gate Mixture of Experts, 多门控专家混合)

- **Full Name**: Multi-gate Mixture-of-Experts (Google 2018)。
- **直觉解释**: 多任务学习时, "shared-bottom" 共享所有任务的底层会出现 task conflict
  (pCTR 和 pHide 梯度方向相反 → 跷跷板)。MMoE 在共享 bottom 之上引入 $K$ 个 expert
  子网络, 每个 task 配一个 **softmax gate** 选 expert 组合:
  $$y_t = h_t\!\Big(\sum_{k=1}^K g_t(x)_k \cdot E_k(x)\Big), \quad g_t(x) = \mathrm{softmax}(W_t x)$$
  这样 task 之间通过 gate 软分配 expert, 既共享底层 embedding 又允许 task-specific 路径。
- **Pinterest 实际应用**: 三处主要部署。**(1)** `system_design_pin_ranking.md` §4.2 L2
  heavy ranker, 8 experts × 6 heads (pRepin / pClick / pCloseup / pLongClick / pHide /
  pVideoCompletion + LTV)。**(2)** `system_design_pins_search.md` §4.2 L2 ranker,
  4 experts, 4 gate (CTR/Repin/Closeup/Hide)。**(3)** `system_design_notification_reco.md`
  §3 推送排序, 4-6 experts 分别建模 open / disable / unsubscribe / long-term value。
- **何时选 vs 替代**: 任务数 ≤ ~10 且任务相关性中等时选 MMoE。**vs PLE**: 当任务严重
  冲突 (跷跷板明显) 时升级到 PLE; **vs Shared-Bottom**: 任务有冲突时一律弃用 shared-bottom。

### B-9. PLE (Progressive Layered Extraction, 渐进分层抽取)

- **Full Name**: Progressive Layered Extraction (Tencent 2020)。
- **直觉解释**: MMoE 的 expert 是完全共享的, 当任务严重冲突时仍会出现跷跷板。
  PLE 把 expert 显式拆成 **shared experts** (所有 task 共用) + **task-specific experts**
  (单一 task 私有), 每层 gate 只让 task $t$ 看到 "shared experts ∪ task-$t$ specific
  experts", 隔离冲突信号。多层堆叠后形成 progressive extraction:
  $E_t^{(l+1)} = \mathrm{Gate}_t^{(l)}(\text{Shared}^{(l)} \cup \text{Specific}_t^{(l)})$。
- **Pinterest 实际应用**: `system_design_ad_ctr.md` §4.2 提及 "可用 MMoE 或 PLE 动态路由"
  作为 multi-task 多目标的可选项 —— 当 pCTR / pCVR / pCloseup 冲突明显 (例如 pCTR↑
  导致 pCVR↓) 时, PLE 的 task-specific expert 隔离能缓解跷跷板。生产中 Pinterest 主线
  仍用 MMoE 作为 baseline, PLE 作为 A/B challenger。
- **何时选 vs 替代**: MMoE 上线后跷跷板严重 (一个 task 涨另一个 task 跌 >2%) 时升级到 PLE。
  **vs MMoE**: PLE 参数多 ~30%、训练慢 ~20%, 但跷跷板缓解明显; 任务冲突弱时不必引入。

---

## 2. 检索与近邻搜索 (Retrieval & ANN)

> 这一节集中展开向量检索栈: 从 **ANN** 这个总命题出发, 到三大主流索引方法
> (**HNSW** 图索引 / **IVF** 倒排聚类 / **PQ** 乘积量化), 再到两个工业级开源库
> (**Faiss** / **ScaNN**), 最后是图神经网络 inductive embedding 的开山之作 **GraphSAGE**
> 与所有检索系统都要面对的 **冷启动** 问题。每个术语按 "Full Name + 直觉 + Pinterest
> 应用 + vs 替代方案" 4 段展开。注: PinSAGE / ItemSage 等 Pinterest 专属 GNN 系统
> 的 deep-dive 在 §7 (PINT-CONCEPTS-H), 此处仅作为 GraphSAGE 的应用案例引用。

### C-1. ANN (Approximate Nearest Neighbor, 近似最近邻)

- **Full Name**: Approximate Nearest Neighbor Search。
- **直觉解释**: 给定 query 向量 $q \in \mathbb{R}^D$ 与 doc 向量库 $\mathcal{D} = \{p_i\}_{i=1}^N$,
  找 top-$k$ 距离最近的 $p_i$, 但**容忍少量错误** (recall ≈ 0.9~0.97) 换取 100~1000x
  latency 提升。Brute-force 是 $O(N \cdot D)$, ANN 索引可降到 $O(\log N \cdot D)$ 甚至常数级。
  评估指标: recall@k = (ANN top-k ∩ exact top-k) / k, 配合 QPS 和 P99 latency 看 Pareto。
- **Pinterest 实际应用**: 几乎所有检索路径都依赖 ANN —— `system_design_pins_search.md` §3.2
  的 5B pins HNSW 召回、`system_design_ad_ctr.md` §3 的广告 candidate generation、
  `system_design_notification_reco.md` §3 的推送候选集生成、`system_design_chatbot_pins.md` §3
  的对话式 pin 检索, 全部建立在 ANN 索引之上。
- **何时选 vs 替代**: 候选库 $N > 10^6$ 且 latency 预算 < 50ms 时必选 ANN。**vs brute-force**:
  $N < 10^4$ 时直接 Faiss `IndexFlatIP` 即可, 上 ANN 反而引入 recall 损失。

### C-2. HNSW (Hierarchical Navigable Small World, 层次可导航小世界图)

- **Full Name**: Hierarchical Navigable Small World graph (Malkov & Yashunin 2018)。
- **直觉解释**: 图索引方案。把每个向量当作图节点, 在节点上构造**多层** skip-list-like
  结构: 顶层节点稀疏 (类似高速路出口), 底层包含全部点 (类似乡间小路)。查询从顶层入口
  贪心走 → 每层跳到当前最接近 query 的邻居 → 直到底层精排得 top-$k$。构建复杂度
  $O(N \log N)$, 查询期望复杂度 $O(\log N)$。两个关键超参: $M$ (每节点邻居数, 典型 16~32)
  和 `efSearch` (查询时维护的候选堆大小, 越大 recall 越高 latency 越慢)。
- **Pinterest 实际应用**: `system_design_pins_search.md` §3.2 用 HNSW 索引 5B pins
  (768 维 embedding), 召回 top-1k 候选 latency < 5ms; `system_design_embeddings.md`
  中 user/pin embedding 服务底层就是分片的 HNSW shard。
- **何时选 vs 替代**: 高 recall (≥ 0.95) + 低 latency (< 10ms) + 内存够 (≈ $D \cdot N \cdot 4$
  字节再加 ~30% 图结构开销) 时选 HNSW。**vs IVF**: HNSW recall 明显更高但内存占用大;
  IVF 内存省 ~4x 但 recall 略低且 `nprobe` 调参敏感。

### C-3. IVF (Inverted File Index, 倒排文件索引)

- **Full Name**: Inverted File Index (借自文本检索的倒排索引概念)。
- **直觉解释**: 先用 k-means 把所有 doc 向量聚成 $K$ 个簇 (典型 $K = \sqrt{N}$),
  每个簇有 centroid。查询时只扫 query 距离最近的 `nprobe` 个簇内向量 (而非全集)。
  把全集搜索 $O(N)$ 降为 $O(K + N \cdot \mathrm{nprobe} / K)$, 当 $K = \sqrt{N}$ 且
  `nprobe` 是常数时近似 $O(\sqrt{N})$。常和 PQ 组合成 **IVF-PQ** 进一步省内存。
- **Pinterest 实际应用**: `system_design_ad_ctr.md` §3 中, 当广告候选量 ~50M 但 RAM 预算
  紧张时, 用 IVF-PQ 代替 HNSW 做 ad-side 检索 —— 内存从 ~150GB 降到 ~10GB,
  recall 从 0.97 降到 0.90, 但广告侧后段还有 ranker 兜底, 召回稍弱可接受。
- **何时选 vs 替代**: 内存受限 + 可接受 recall 0.85~0.92 + 候选库 $N \in [10^7, 10^9]$
  时选 IVF。**vs HNSW**: IVF 构建快、内存省、动态 add/remove 友好, 但 recall 上限低于
  HNSW; HNSW 反过来内存吃紧但 recall 上限可达 0.99。

### C-4. PQ (Product Quantization, 乘积量化)

- **Full Name**: Product Quantization for Nearest Neighbor Search (Jegou et al. 2011)。
- **直觉解释**: 把 $D$ 维向量切成 $M$ 段 (每段 $D/M$ 维), 每段独立 k-means 量化到
  $2^b$ 个 codeword。原本 $D \cdot 32$ bit 的 float 向量被压成 $M \cdot b$ bit
  (典型 $D = 768, M = 96, b = 8$, 压缩约 32x)。查询距离用预算好的查表加速:
  $$d(q, p) \approx \sum_{m=1}^{M} d\big(q_m,\ c_{p,m}\big)$$
  其中 $c_{p,m}$ 是 $p$ 在第 $m$ 段的量化中心 ID 对应的 codeword。
- **Pinterest 实际应用**: `system_design_embeddings.md` 中 5B pin embedding 全量存内存
  不可行 (5B × 768 × 4B = 15TB), 用 PQ 压到 ~500GB 后用 IVF-PQ 索引落到单机
  + 跨 shard 分布式检索, 是 ad-side 与 shopping-graph 的标准方案。
- **何时选 vs 替代**: 向量数 $> 10^8$ + 内存吃紧 + 可接受 recall 0.85~0.92 时必选 PQ。
  **vs Scalar Quantization (FP32→INT8)**: SQ 实现简单但仅压缩 4x; PQ 压缩 16~32x 且
  recall 仍可保 0.9, 工业级首选 PQ。

### C-5. Faiss (Facebook AI Similarity Search, FB 向量检索库)

- **Full Name**: Facebook AI Similarity Search library (Meta 2017)。
- **直觉解释**: Meta 开源的向量检索库, 提供所有主流索引 (`IndexFlat` / `IndexIVF` /
  `IndexHNSW` / `IndexIVFPQ` / `IndexBinary` / GPU-Faiss) 的 C++ + Python 实现, 支持
  GPU 大 batch 检索。是工业界向量检索的事实标准, 论文 "Billion-scale similarity search
  with GPUs" 公开了核心算法。
- **Pinterest 实际应用**: 内部 embedding service (`system_design_embeddings.md`) 长期使用
  Faiss IVF-PQ 作为 ad / shopping-graph 检索后端; `system_design_pins_search.md` 后来切到
  自研 HNSW 服务以降 P99 latency, 但训练阶段的 in-batch negative mining + offline candidate
  generation 仍依赖 Faiss GPU 索引。
- **何时选 vs 替代**: 需要 GPU 加速 + batch 检索 (训练阶段) 或多种索引互通时选 Faiss。
  **vs ScaNN**: Faiss 通用性强、社区大、GPU 算子成熟; ScaNN 在 small-batch CPU MIPS 任务上
  recall-latency Pareto 更优。

### C-6. ScaNN (Scalable Nearest Neighbors, Google 向量检索库)

- **Full Name**: Scalable Nearest Neighbors (Google 2020, 论文 "Accelerating Large-Scale
  Inference with Anisotropic Vector Quantization", ICML 2020)。
- **直觉解释**: Google 开源的 ANN 库, 核心创新是 **AVQ (Anisotropic Vector Quantization)**:
  在 PQ 量化时, **优先保证 query 方向上的内积误差小**, 而非欧氏距离方向均匀小。
  数学上把量化误差 loss 加权: $\mathcal{L} = \mathbb{E}_q[w_\parallel (e_\parallel)^2 + w_\perp (e_\perp)^2]$,
  其中 $e_\parallel$ 是 $p - \hat{p}$ 在 $q$ 方向的分量。在 MIPS (Maximum Inner Product
  Search, 即双塔召回的核心算子) 任务上, 比 IVF-PQ recall 提升 5~10%。
- **Pinterest 实际应用**: 没有公开宣称在生产中使用 ScaNN, 但在面试中作为讨论
  "MIPS 检索方案对比" 的标准参考点 (与 Faiss IVF-PQ 并列), 也是 TF/JAX 生态中
  双塔召回的默认 ANN 后端。
- **何时选 vs 替代**: TF/JAX 生态 + MIPS 任务 (双塔点积召回) + 严格 recall 预算时选 ScaNN。
  **vs Faiss**: ScaNN 在 MIPS Pareto 上略优, 但社区小、缺 GPU 实现, 无法做训练阶段大 batch
  candidate sampling。

### C-7. GraphSAGE (Graph Sample and Aggregate, 图采样聚合 GNN)

- **Full Name**: Graph SAmple and aggreGatE (Hamilton et al. NeurIPS 2017)。
- **直觉解释**: 图神经网络 (GNN) 的 **inductive** 版本 —— 不需要为每个新节点重训整图,
  只用邻居采样 + aggregator (mean / pool / LSTM) 学到固定大小的邻域 embedding。
  第 $k$ 层节点 $v$ 的更新公式:
  $$h_v^{(k)} = \sigma\Big(W^{(k)} \cdot \mathrm{CONCAT}\big(h_v^{(k-1)},\ \mathrm{AGG}_k(\{h_u^{(k-1)}: u \in \mathcal{N}(v)\})\big)\Big)$$
  其中 $\mathcal{N}(v)$ 是 $v$ 的固定大小邻居采样集 (例如每层采 25 个邻居)。
  关键贡献: 解耦"邻居数"和"图规模", 让 GNN 能 scale 到亿级节点。
- **Pinterest 实际应用**: GraphSAGE 是 **PinSAGE** (`system_design_embeddings.md` 的核心
  embedding 模型, 详见 §7) 的直接前身 —— Pinterest 把 GraphSAGE 应用到 pin-board 二部图上,
  通过 random walk 采邻居 + importance pooling 学 pin embedding, 是工业界第一个亿级 GNN
  系统 (论文 KDD 2018 "Graph Convolutional Neural Networks for Web-Scale Recommender Systems")。
- **何时选 vs 替代**: 图规模 > $10^6$ 节点 + 需要 inductive (新节点上线即可推理, 不重训)
  + 节点有丰富 feature 时选 GraphSAGE 系。**vs GCN (transductive)**: GCN 推理时需要全图
  Laplacian, 新节点必须重训; GraphSAGE 通过邻居采样 + 参数共享支持在线推理。
  **vs GAT (Graph Attention)**: GAT 用 attention 加权邻居, 表达力强但训练慢且对 hub 节点
  不友好; GraphSAGE 用 mean/max pool 工程上更稳。

### C-8. Cold-start (冷启动问题)

- **Full Name**: Cold-start problem in recommender systems (无历史交互的新用户 / 新 item
  推荐)。
- **直觉解释**: 新 user (无点击历史) 或新 item (无被点击次数) 在协同过滤 / 行为驱动 ranker
  下打分接近零, 导致曝光差 → 收集不到反馈 → 永远冷的**恶性循环**。解法分两类:
  **(a) content-based**: 用 item meta (text/image embedding) 或 user demographic 替代
  行为信号, 把冷 item 投到与其内容相似的 hot item 邻域;
  **(b) exploration**: ε-greedy / UCB / Thompson sampling, 强制把冷 item 混入流量一段时间
  收集 reward 后再加权。一般工业系统两条腿走路。
- **Pinterest 实际应用**: 三个核心场景。**(1)** `system_design_pin_ranking.md` §6 中, 新 pin
  上线后前 24h 强制混入 5% 流量做 explore, 收集 pCTR / pRepin 后再加权进 ranker;
  **(2)** `system_design_catalog_bulk_update.md` §3 catalog 新品上架时, 用 image embedding
  (CLIP) + text embedding (BERT-small) 直接跑 two-tower 检索, 完全不依赖历史交互;
  **(3)** `system_design_notification_reco.md` §3 中新用户用 signup-time interest tags +
  demographic 做内容驱动 candidate gen, 等收集到 ~10 次行为后再切入协同过滤路径。
- **何时选 vs 替代**: 新 item 比例 > 1% 或新 user DAU 占比 > 5% 时**必须**做冷启策略,
  否则系统会逐渐"老化"。**vs Bandit-based exploration (UCB / TS)**: bandit 数学上最优
  (regret bound 可证) 但工程复杂 (要维护 per-item 后验); ε-greedy 实战足够好且实现简单,
  Pinterest 主线用 ε-greedy + content-based 组合。

---

## 3. 排序方法 (Learning-to-Rank Methods)

> 待补充于 T-P1-743 (PINT-CONCEPTS-D)。
>
> 涵盖: Pointwise / Pairwise / Listwise (RankNet, LambdaRank, LambdaMART, ListNet),
> NDCG-aware loss, position-bias correction (IPS / DLA), Pinterest 在 home feed +
> search 中的实际选型。

---

## 4. 评估指标 (Evaluation Metrics)

> 待补充于 T-P1-744 (PINT-CONCEPTS-E)。
>
> 涵盖: AUC / GAUC / NDCG@k / MAP / MRR / Hit-Rate@k / Precision-Recall / log-loss /
> calibration error (ECE), online vs offline 一致性、proxy metric 选择陷阱。

---

## 5. 纠偏与 LLM 微调 (Debiasing & LLM Fine-Tuning)

> 待补充于 T-P1-745 (PINT-CONCEPTS-F)。
>
> 涵盖: Position Bias / Selection Bias / Popularity Bias / Exposure Bias 的成因与
> 缓解 (IPS, DR, DLA, counterfactual logging), LLM SFT vs RLHF vs DPO vs ORPO,
> Pinterest chatbot 微调流水线。

---

## 6. 基础设施与业务 KPI (Infrastructure & Business KPIs)

> 待补充于 T-P1-746 (PINT-CONCEPTS-G)。
>
> 涵盖: Feature Store (Online vs Offline, point-in-time correctness), Model Serving
> (Triton / TorchServe / Ray Serve), A/B testing 平台、北极星指标 (DAU, time-spent,
> repin rate, ad CTR, ROAS), guardrail metrics。

---

## 7. Pinterest 专属系统 (Pinterest-Specific Systems)

> 待补充于 T-P1-747 (PINT-CONCEPTS-H)。
>
> 涵盖: PinSAGE / Pin2Vec / SearchSAGE / Homefeed Ranker / Shopping Graph /
> Catalog Pipeline 的内部架构与演进史，以及 Pinterest engineering blog 中已公开
> 的设计决策。

---
