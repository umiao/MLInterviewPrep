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

> 待补充于 T-P1-741 (PINT-CONCEPTS-B)。
>
> 涵盖: MMoE / PLE / DLRM / DCN-v2 / Wide & Deep / Two-Tower / Shared-Bottom 的对比、
> 何时用哪种、Pinterest 内部部署细节，以及多任务下的 loss weighting / gradient
> conflict 处理。

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
