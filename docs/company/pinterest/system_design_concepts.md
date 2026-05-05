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

> 待补充于 T-P1-742 (PINT-CONCEPTS-C)。
>
> 涵盖: HNSW / IVF / Faiss / ScaNN / DiskANN 的对比、查询/构建复杂度、
> recall-vs-latency 曲线，PinSAGE 双塔检索路径、user/item embedding 解耦设计。

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
