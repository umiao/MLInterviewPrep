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

> 这一节集中展开排序 loss 的三大范式 (**pointwise / pairwise / listwise**) 与对应的
> 代表方法 (**LambdaRank / ListNet / ListMLE**), 以及在 ranker 输出之后做多样性 / 多目标
> 调整的工具 (**DPP** 行列式点过程 / **Submodular** 子模优化 / **Pareto frontier** 多目标
> 前沿)。Pinterest 的实践是: ranking model 内部的 loss 选型按场景挑 LambdaRank 或 listwise,
> ranker 输出之后用 MMR/DPP/submodular 做 re-rank, 多目标头之间的权重则用 Pareto front 扫描
> 选点。注: position-bias 纠偏 (IPS / DLA) 留到 §5 (PINT-CONCEPTS-F) 与 LLM 微调一起讨论,
> 此处不展开。

### D-1. LTR (Learning-to-Rank, 学习排序)

- **Full Name**: Learning-to-Rank。
- **直觉解释**: 给定 query $q$ 和候选文档列表 $\{d_1, \ldots, d_n\}$, 学习一个打分函数
  $f(q, d)$ 让相关 doc 排在前面。三大 loss 范式的核心区别是**计算 loss 时同时看几个 doc**:
  **(a) pointwise** 单个 (q, d) 一例, 把 ranking 退化成回归 / 二分类
  ($\mathcal{L} = \sum_i \ell(f(q, d_i), y_i)$, 例如 BCE/MSE);
  **(b) pairwise** 一对 $(d_+, d_-)$, 学 margin
  ($\mathcal{L} = \sum_{(i,j): y_i > y_j} \log(1 + e^{-(f_i - f_j)})$, 即 RankNet 损失);
  **(c) listwise** 整个候选列表, 直接对齐 NDCG/MAP 等 list-level metric。pointwise 简单但
  忽略 doc 间相对关系; pairwise 对齐排序信号但只用局部对; listwise 最贴合指标但训练开销大。
- **Pinterest 实际应用**: `system_design_pins_search.md` §4.2 明确写出三范式选型对比表,
  生产线选择是 **L1 用 pairwise LambdaRank** (粗排一遍学相对序更直接),
  **L2 用 pointwise multi-task** (多目标 head 各自独立 BCE, 方便组合 MMoE)。
  `system_design_pin_ranking.md` §4 同样在 L2 用 pointwise BCE per-head + MMoE 共享底层,
  避免 listwise 的训练 batch 内列表组装开销。
- **何时选 vs 替代**: 候选量大、需要 GPU batch 训练时选 pointwise; 排序敏感 + label 是相对
  偏好 (click vs no-click 对) 时选 pairwise; 评估指标是 NDCG@k 且能拼出列表 (例如搜索 query
  日志) 时选 listwise。**vs RL-based ranking**: RL (例如 SlateQ) 能建模 list 内交互但训练
  不稳, 工业 baseline 仍是 LTR 三范式。

### D-2. LambdaRank (Lambda Ranking, λ 加权对偶排序)

- **Full Name**: LambdaRank (Burges et al., MSR 2006), pairwise/listwise 混合。
- **直觉解释**: 痛点 —— RankNet 用 pairwise logistic loss 学相对序, 但所有 (i, j) 对权重相同,
  对 NDCG 这种 top-heavy 指标不友好 (排第 1 的错误比排第 100 的错误重要得多)。
  LambdaRank 的关键 trick 是把 RankNet 梯度乘以 **$|\Delta \mathrm{NDCG}_{ij}|$** ——
  即"交换 $i, j$ 两 doc 后 NDCG 变化的绝对值":
  $$\lambda_{ij} = \frac{-\sigma}{1 + e^{\sigma(s_i - s_j)}} \cdot |\Delta \mathrm{NDCG}_{ij}|$$
  其中 $s_i = f(q, d_i)$。直观: 高位的 swap 拿到大梯度, 低位的 swap 拿到小梯度,
  让模型把"力气"花在 head positions 上。后续 LambdaMART 把该 lambda 接到 GBDT 上是
  Yahoo / Bing learn-to-rank 的经典工业方案。
- **Pinterest 实际应用**: `system_design_pins_search.md` §4.2 中, **L1 light ranker**
  (双塔 DNN) 用 LambdaRank loss 训练: $(query, pin_+, pin_-)$ pair, label 是 engagement
  权重 (repin > click > impression), $\Delta \mathrm{NDCG}$ 用 ideal ranking 算。这样
  L1 出口 top-1k 已对齐 NDCG, L2 才能在窄候选集上做精细多目标。
- **何时选 vs 替代**: 单一 ranking metric (NDCG@k 或 MAP) + 有明确相对偏好对的训练数据时选
  LambdaRank。**vs ListNet/ListMLE**: LambdaRank 工程更稳 (pairwise sample 容易组 batch),
  ListNet/MLE 更贴 listwise objective 但训练数据每条都要拼整列表; 工业搜索/推荐里
  LambdaRank/LambdaMART 仍是首选。

### D-3. ListNet (List-wise Neural network, 列表级神经网络排序)

- **Full Name**: Learning to Rank: from Pairwise Approach to Listwise Approach (Cao et al.,
  Microsoft 2007)。
- **直觉解释**: 第一个真正 listwise 的 LTR 方法。把整个候选列表的打分 $\{s_i\}$ 通过 softmax
  转为**top-1 概率分布**, 真实 label 也转为 top-1 分布 (label 越高概率越大), 然后两个分布
  之间算 cross-entropy:
  $$\mathcal{L}_{\text{ListNet}} = -\sum_{i=1}^n \frac{e^{y_i}}{\sum_j e^{y_j}} \log \frac{e^{s_i}}{\sum_j e^{s_j}}$$
  解决了 pairwise 方法的"对内独立性"假设 (RankNet 把每对当独立样本忽略列表结构)。
- **Pinterest 实际应用**: `system_design_pins_search.md` §4.2 在三范式对比表中把 ListNet
  列为 listwise 候选之一, 与 ListMLE 并列 ("Pointwise (BCE) | Pairwise (LambdaRank) |
  Listwise (ListNet/ListMLE)"); Pinterest 当前生产没采用 ListNet 主线, 因为 L2 multi-task
  pointwise + MMoE 已能拿到大头收益, listwise 上线 ROI 不够清晰, 但保留作为 challenger 选项。
- **何时选 vs 替代**: 训练数据天然成列表 (一次 query 的全部候选有相对序 label) + 列表长度
  适中 (≤ 几十) + 主要看 top-1/top-3 时选 ListNet。**vs LambdaRank**: ListNet 直接 listwise,
  对齐 list-level metric 更彻底, 但训练 batch 设计复杂; LambdaRank 用 $\Delta\mathrm{NDCG}$
  trick 在 pairwise 框架里近似 listwise, 工程上更友好。

### D-4. ListMLE (List-wise Maximum Likelihood Estimation, 列表级极大似然)

- **Full Name**: Listwise Approach to Learning to Rank: Theory and Algorithm (Xia et al.,
  ICML 2008)。
- **直觉解释**: ListNet 用 top-1 分布只匹配第一名, 对靠后的位置不敏感。ListMLE 改用
  **Plackett-Luce 模型** —— 假设观察到的排列 $\pi^*$ 是依概率从分数分布逐位置抽样得到的,
  目标是最大化该排列的似然:
  $$\mathcal{L}_{\text{ListMLE}} = -\log \prod_{i=1}^n \frac{\exp(s_{\pi^*(i)})}{\sum_{k=i}^n \exp(s_{\pi^*(k)})}$$
  即"在剩余候选中, $\pi^*(i)$ 被选为第 $i$ 名的概率"连乘。优势: 对整条排列建模而不仅 top-1,
  对靠后位置也提供梯度信号。
- **Pinterest 实际应用**: `system_design_pins_search.md` §4.2 的三范式对比表把 ListMLE
  与 ListNet 并列为 listwise 选项之一; 生产同样未直接上 ListMLE, 但在面试里作为
  "为什么 listwise 不如 pairwise 落地" 的对照点 —— 训练效率 + label 噪声敏感性是主要阻力。
- **何时选 vs 替代**: 完整排列 label (而非仅相对偏好对) + 重视靠后位置的相对序时选 ListMLE。
  **vs ListNet**: ListMLE 用 Plackett-Luce 全排列似然, 比 ListNet 的 top-1 分布信息量更大,
  但对 label 噪声敏感 (一个错的中间位置会污染整个似然链); ListNet 对 label 噪声更鲁棒。

### D-5. DPP (Determinantal Point Process, 行列式点过程)

- **Full Name**: Determinantal Point Process (来自量子物理的概率模型, Macchi 1975, ML
  改造 Kulesza & Taskar 2012)。
- **直觉解释**: 从候选集 $\mathcal{Y} = \{1, \ldots, N\}$ 中**采样一个子集** $S \subseteq \mathcal{Y}$,
  每个子集的概率正比于一个**核矩阵 $L$ 的子矩阵行列式**:
  $$P(S) \propto \det(L_S)$$
  其中 $L = D^\top D$, $D$ 行向量是 item embedding, 对角元 $L_{ii}$ 编码 item 质量,
  非对角元 $L_{ij}$ 编码 item $i, j$ 的相似度。**核心数学性质**: 行列式 $\det(L_S)$ 几何上等于
  embedding 张成空间的体积平方 → 体积大需要 (a) 每个 item quality 高、(b) item 间夹角大
  (彼此差异大), 所以采样自然倾向 "high-quality + diverse" 子集。比 MMR 的贪心多样性更
  principled, 且有多项式时间精确推断算法。
- **Pinterest 实际应用**: 没有公开宣称在生产中采用 DPP, 但作为 `system_design_pin_ranking.md`
  §5 re-ranking 阶段的"理论备选" —— 当前生产用 MMR (Maximal Marginal Relevance, 贪心
  多样性) 但 PM/researcher 在面试/blog 中常以 DPP 作为"如果要严格证明多样性最优解"
  时的 next-step 选项。是讨论"为什么不用 DPP 而用 MMR"的标准对比锚点 (答: MMR 工程
  $O(K^2)$ 简单, DPP 数学美但 $O(K^3)$ 矩阵分解 + 调参复杂)。
- **何时选 vs 替代**: 候选集小 (≤ 数百) + 多样性约束严格 + 有 budget 调核函数时选 DPP。
  **vs MMR**: MMR 是 DPP 的一阶贪心近似, 实战 90% 场景效果接近且简单; DPP 在小池+严格
  diversity (例如新闻头条 5 条) 才显出优势。

### D-6. Submodular (Submodular Optimization, 子模优化)

- **Full Name**: Submodular function maximization (组合优化分支, 推荐系统中用于 coverage +
  diversity 选择)。
- **直觉解释**: 集合函数 $f: 2^V \to \mathbb{R}$ 称为**子模 (submodular)** 当且仅当对任意
  $A \subseteq B \subseteq V$ 和 $v \notin B$, **边际收益递减**:
  $$f(A \cup \{v\}) - f(A) \geq f(B \cup \{v\}) - f(B)$$
  直观: 第 11 个 item 的"新增价值"小于第 1 个。重要性: 对单调 (monotone) submodular 函数
  $f$, 在 cardinality constraint $|S| \leq k$ 下用**贪心算法** (每次选边际收益最大的 item)
  能保证 $\geq (1 - 1/e) \approx 0.63$ 倍最优解 (Nemhauser 1978)。常见 submodular 目标: 覆盖
  $f(S) = |\bigcup_{i \in S} \mathrm{topics}(i)|$, facility location, log-determinant
  ($\log \det L_S$, 即 DPP 的 log 形式)。
- **Pinterest 实际应用**: `system_design_notification_reco.md` §3 中 Email digest 选 5-10 个
  pin 时, 用**submodular selection (coverage + diversity)** 在 ranker 输出之后做 second pass:
  目标函数 = 覆盖的 topic 数 + 创作者多样性 - 同 creator 重复惩罚, 贪心选 top-k 即可保证
  接近最优。这种 second-pass 比直接在 ranker loss 里加 diversity 项更模块化, 也好 A/B 调权重。
- **何时选 vs 替代**: 选 top-$k$ 子集 + 目标可表达成 coverage / facility location / 分散度
  + $k$ 不大 (~10) 时选 submodular 贪心。**vs MMR**: MMR 是一种特殊的 submodular surrogate
  (相似度惩罚项); submodular 框架更通用, 能直接编码 "覆盖 N 个 topic" 这种约束。
  **vs DPP**: 二者都给出 quality+diversity, submodular 适合 coverage 类目标, DPP 适合
  embedding-based 几何多样性。

### D-7. Pareto Frontier (Pareto 前沿, 多目标最优面)

- **Full Name**: Pareto Frontier / Pareto Front, 借自经济学的多目标最优概念。
- **直觉解释**: 推荐 ranker 同时优化 N 个目标 (pCTR / pRepin / pHide / time-spent / ROAS),
  这些目标常**冲突**: 提 CTR 可能掉 long-term retention, 提多样性可能掉 CTR。一个解 $w$ 称为
  **Pareto-optimal** 当且仅当不存在另一个解 $w'$ 在所有目标上都不更差且至少一个目标更好;
  所有 Pareto-optimal 解构成 **Pareto frontier**。工程做法: 离线对多目标加权
  $\mathcal{L} = \sum_t w_t \mathcal{L}_t$, **网格搜索 $\{w_t\}$** 跑出大量配置, 在 (objective_1,
  objective_2, ...) 空间画散点, 取前沿曲线给 PM 选点 (PM 在前沿上挑"最符合本季度业务取舍"
  的那个 $w^*$)。
- **Pinterest 实际应用**: `system_design_pin_ranking.md` §5 明确写出 Pareto front scan 流程:
  "离线对权重网格搜索, 画 (repin, hide) / (repin, session) trade-off 曲线, PM 选点", 然后
  把选定的 $w^*$ 喂给 L2 multi-task 头的加权融合 ($\hat{y} = \sum_t w_t \hat{y}_t$);
  `system_design_ad_ctr.md` §6 的多目标 (CTR + CVR + LTV) 同样用 Pareto 前沿作候选集。
  此外 ANN 索引选型 (HNSW vs IVF-PQ) 也常画 (recall, latency) 的 Pareto 看 (见 §2 C-1)。
- **何时选 vs 替代**: 多目标 ranker / 多目标 retrieval 选型 + 没有单一标量目标统治时用
  Pareto frontier。**vs Lagrangian / weighted sum 单点优化**: 单点权重需要先验, Pareto front
  把"探所有 trade-off"和"按业务挑点"解耦, 工程上更稳。**vs scalarization (固定 $w$)**:
  固定 $w$ 假定业务取舍永不变, Pareto 留住灵活性 (业务转向时可换前沿上别的点而无需重训)。

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
