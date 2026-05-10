"""Seed: T-P1-804 [KG-INT B3-2] -- meta-prep/system-design-must-knows children.

Distills cross-company ML system-design (SD) vocabulary from the 10 P0+P1
companies' SD prep surfaces (S1 prep_notes, S3 company_documents) into
shared `meta-prep/system-design-must-knows/<slug>` framework_nodes per the
promotion threshold locked in `docs/workflow/promotion_criteria.md`
(>=3 of 11 P0+P1 companies AND de-companiable wording).

A regex-driven term coverage scan was run across the SD-titled docs of
the 10 P0+P1 companies (LinkedIn id=22, Meta id=91, DoorDash ids=4/40/41/
42/43/45, Google ids=64/65/72, Uber ids=33/85, Pinterest ids=70/74,
Adobe id=13, TikTok prep_notes, Slack id=59, PARSPEC prep_notes). 22
terms cleared the >=3 threshold and were rewritten into de-companiable
"must-know" plays. Each child node embeds:

  - 1-2 sentence definition + intuition
  - Why-it-matters / where-it-shows-up paragraph
  - Cross-links via kg://N (framework_nodes.id) for adjacent ML pillar nodes
    and sd://<slug> (system_designs.slug) for the canonical SD card(s).
  - Top failure modes / interview anti-patterns
  - relevant_companies CSV listing the >=3 P0+P1 sources

The parent stub `meta-prep/system-design-must-knows` (T-P1-800) had a
`TODO[KG-INT-B3-2]` marker. This seed updates the parent description to
a real summary on first run.

Safety:
  1. SHA-256 of the `meta-prep/system-design-must-knows` subtree captured
     pre/post.
  2. Refuses to overwrite a child whose title/description/companies have
     drifted from this seed (someone hand-edited it).
  3. Idempotent: re-run yields inserted=0, updated=0, skipped=23
     (1 parent + 22 children).
  4. Parent description UPDATED only on first run (TODO marker present).
  5. Post-run invariant: exactly 23 rows match
     path = 'meta-prep/system-design-must-knows' OR
     path LIKE 'meta-prep/system-design-must-knows/%'.
  6. AC checks:
       - children count >= 20
       - each child has >=3 valid P0+P1 sources in relevant_companies
       - description contains at least one kg:// or sd:// cross-link

Usage:
    python scripts/seed_meta_prep_sd_must_knows.py
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

PARENT_PATH = "meta-prep/system-design-must-knows"
PARENT_TITLE = "System Design Must-Knows"
PARENT_DESCRIPTION_NEW = (
    "跨公司 ML/system-design round 收集到的 must-know 词汇与 design plays "
    "(shared SD substrate, distilled from 10 P0+P1 companies' SD prep surfaces). "
    "子节点按 SD 主题拆分: retrieval (two-tower / ANN / negative sampling), "
    "ranking (multi-stage funnel / cross-encoder rerank / LTR / MMoE-PLE / "
    "DLRM-DeepFM-DCN), evaluation (NDCG / calibration / A-B testing / debiasing), "
    "infra (feature store / stream-batch / sharding / cache / sketches / geo), "
    "和 serving optimization (distillation / quantization / latency budget). "
    "每个子节点带 kg://N 与 sd://slug cross-links 指向具体 framework_node 与 "
    "system_designs 卡片. Authoring per-company SD answer 时优先复用此处定义 + "
    "trade-off 论证, company-specific framing 留在 pillar8.company_specific."
)
PARENT_TODO_MARKER = "TODO[KG-INT-B3-2]"

P0P1_COMPANY_NAMES = {
    "LinkedIn", "DoorDash", "Google", "Uber", "Adobe",
    "TikTok", "Slack", "PARSPEC", "Pinterest", "Meta",
}

# Each tuple: (slug, title, description, [companies])
# Description should embed at least one kg://N or sd://<slug> cross-link.
CLUSTERS: list[tuple[str, str, str, list[str]]] = [
    (
        "two-tower-dual-encoder",
        "Two-Tower / Dual-Encoder Retrieval",
        "User tower 与 item tower 独立编码后用 dot-product / cosine 打分 -- "
        "纯解耦 (decoupled) 设计的核心收益是 item embedding 可离线预计算 + 建 ANN "
        "(Approximate Nearest Neighbor) 索引, 在线只算 user embedding 后做 ANN "
        "search, 召回 millions->1k 候选的 latency 控在 10ms 以内. "
        "代价: 没有 cross-attention, 任何 query x doc 交叉特征只能放在 reranker. "
        "Standard production pattern: two-tower 召回 -> cross-encoder 精排. "
        "口述捷径: '双塔 = 点积打分 = 离线建索引 = 亚毫秒检索'. "
        "Cross-links: framework node kg://98 (pillar3.building_blocks.two_tower_model), "
        "canonical SD cards sd://interview-recommendation-system "
        "(DLRM/MMoE/Two-Tower cookbook), sd://pinterest-embeddings, "
        "sd://pinterest-pin-ranking. Anti-patterns: 用户向量里塞候选侧 feature "
        "(破坏解耦), 在召回阶段就上 cross-encoder, 忽视 item tower 重训需 "
        "全 corpus 重编码的 cost.",
        ["DoorDash", "Google", "Meta", "Pinterest", "Uber"],
    ),
    (
        "ann-hnsw-ivf-pq",
        "ANN: HNSW vs IVF-PQ for Vector Retrieval",
        "ANN (Approximate Nearest Neighbor, 近似最近邻) 是十亿级向量检索的标配. "
        "两大主流方案: (1) HNSW (Hierarchical Navigable Small World, 分层小世界图) "
        "图结构, recall 95-97% @100, 亚毫秒延迟, 内存大, 支持增量插入; "
        "(2) IVF-PQ (Inverted File + Product Quantization, 倒排+乘积量化) "
        "先粗聚类再压缩, 内存省, 召回 85-92% @100, 需周期性重建. "
        "选型主轴: index 更新频率 + 内存预算 + 召回门槛. 高更新+高 recall 选 HNSW; "
        "静态 corpus + 大规模 + 内存敏感 选 IVF-PQ. "
        "Cross-links: kg://100 (pillar3.building_blocks.ann), "
        "sd://interview-recommendation-system (Two-Tower 召回卡), "
        "sd://pinterest-embeddings. Anti-patterns: 不区分 efSearch / nprobe 与 "
        "recall-latency 曲线; 把 ANN 当 exact KNN 用; 忽略 dimension 与 PQ "
        "subquantizer 数的耦合.",
        ["DoorDash", "Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "infonce-and-negative-sampling",
        "InfoNCE Loss + Negative Sampling Strategies",
        "Two-tower 训练的主力损失是 InfoNCE (Information Noise-Contrastive "
        "Estimation): 在一个正样本 + K 个负样本上做 softmax 交叉熵, 模型质量被 "
        "K 个负样本的分布支配. 四类负样本各有 failure mode: (a) random negatives "
        "无偏但太简单, 模型只学粗主题; (b) in-batch negatives 白送 K=batch-1 但 "
        "popularity bias (流行度偏差) 严重, 高频 item 被过度惩罚, 需 sampled-"
        "softmax logQ 修正; (c) hard negatives (相似但不相关) 提升精度但需 "
        "curriculum 防 model collapse; (d) mixed (random+hard+in-batch) "
        "工业界标配. Cross-links: kg://98 (two_tower_model), "
        "kg://102 (pillar3.building_blocks.embedding), "
        "sd://interview-recommendation-system. Anti-patterns: 全用 random "
        "negatives 训出 'topic match but no relevance' 模型; in-batch 不加 "
        "logQ 修正导致线下涨分线上跌.",
        ["DoorDash", "Google", "Pinterest", "Uber"],
    ),
    (
        "multi-stage-funnel",
        "Multi-Stage Retrieval-Ranking Funnel",
        "现代推荐 / 搜索 / 广告系统都是 4-stage 漏斗 (funnel): retrieval "
        "(millions -> 1k, <10ms, ANN/inner product) -> pre-ranking / coarse "
        "ranking (1k -> 200, <5ms, distilled model) -> ranking / fine ranking "
        "(200 -> 50, <50ms, full feature cross + DCN/DLRM) -> re-ranking "
        "(50 -> 20, <10ms, business rules + diversity + fairness). 核心权衡: "
        "Retrieval 求 recall@K, Ranking 求 NDCG/AUC, Re-ranking 求 multi-"
        "objective trade-off. 每一级的 model complexity 和 latency budget "
        "递增, candidate scale 递减. Cross-links: kg://99 "
        "(pillar3.building_blocks.multi_stage_ranking), "
        "sd://pinterest-pin-ranking, sd://interview-recommendation-system. "
        "Anti-patterns: 用一个 monolithic 大模型扫全量候选 (latency 爆掉); "
        "在 retrieval 阶段加 pairwise 特征 (失去 ANN 能力); pre-ranking 太复杂 "
        "导致 distillation 收益消失.",
        ["DoorDash", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "cross-encoder-rerank",
        "Cross-Encoder / Cross-Attention Reranker",
        "Cross-encoder (cross-attention reranker, 跨塔重排器) 把 (query, doc) "
        "拼接进同一个 transformer/MLP, token 级联合 attention 学到 'query 词 A "
        "与 doc 词 B 的交互' 这类双塔学不了的信号. 代价: 无法预计算, 必须在线对 "
        "K 个候选逐对评分, latency O(K). 工业标配: top-K (K=50-200) 候选用 "
        "cross-encoder 重排; 更深一步可上 ColBERT 风格 late-interaction "
        "(token-level 后期交互, ~10x memory 换 recall). Cross-links: "
        "kg://99 (multi_stage_ranking), sd://pinterest-pin-ranking, "
        "sd://interview-recommendation-system. Anti-patterns: 用 cross-encoder "
        "替代 retrieval (latency 爆掉); 把 cross 特征塞进双塔 user tower "
        "(破坏离线索引前提).",
        ["DoorDash", "Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "ltr-pointwise-pairwise-listwise",
        "Learning-to-Rank: Pointwise / Pairwise / Listwise",
        "LTR (Learning to Rank, 学习排序) 三大范式: (a) Pointwise -- 逐条预测 "
        "P(click) / 评分, 简单但忽略 list 内相对关系 (LR/GBDT/DNN regressor); "
        "(b) Pairwise -- 优化 pair (i,j) 的相对顺序, 经典 RankNet/LambdaRank, "
        "梯度按 NDCG-delta 加权; (c) Listwise -- 直接优化 list-level 指标 "
        "(NDCG / MAP), LambdaMART / ListNet / softmax cross-entropy on "
        "permutations. 工业界主流: pairwise (LambdaRank) 因 listwise 训练 "
        "复杂且收益边际化. Cross-links: kg://114 (pillar4.search_ir."
        "learning_to_rank), sd://pinterest-pin-ranking. Anti-patterns: "
        "pointwise 在 head-tail query 间 calibration 不一致; pairwise 把 "
        "ties 当 negative 训; listwise 在小 list 上梯度噪声大.",
        ["DoorDash", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "mmoe-ple-multitask",
        "Multi-Task Learning: MMoE / PLE / Shared-Bottom",
        "MTL (Multi-Task Learning, 多任务学习) 在 ranking 里同时学 CTR + CVR + "
        "dwell-time + share. 三种架构演进: (1) Shared-Bottom -- 底层共享 "
        "embeddings + per-task tower, 简单但负迁移 (negative transfer); "
        "(2) MMoE (Multi-gate Mixture-of-Experts) -- 多个 expert + per-task "
        "gating network, 任务相关性低时优于 shared-bottom; (3) PLE "
        "(Progressive Layered Extraction) -- 显式分 task-shared experts 与 "
        "task-specific experts, 进一步缓解 seesaw phenomenon (跷跷板效应). "
        "面试常追问: expert 数怎么定 (一般 4-8); gate 是 softmax 还是 top-K. "
        "Cross-links: kg://107 (pillar3.building_blocks.multi_task_learning), "
        "sd://interview-recommendation-system, sd://pinterest-pin-ranking. "
        "Anti-patterns: 任务量纲差异不做 loss weighting; 把 negative-transfer "
        "盲扔给 'add more experts'.",
        ["DoorDash", "Google", "Meta", "TikTok", "Uber"],
    ),
    (
        "dlrm-deepfm-dcn-feature-cross",
        "Feature-Cross Models: DLRM / DeepFM / DCN / Wide&Deep",
        "Ranking 模型的核心是 explicit + implicit feature crossing. "
        "演进谱系: (1) Wide&Deep -- 手工 cross + DNN 并联; (2) DeepFM -- "
        "FM (Factorization Machine) 自动二阶 cross + DNN 高阶; (3) DCN "
        "(Deep & Cross Network) -- cross network 显式高阶, 每层 x_{l+1} = "
        "x_0 x_l^T w_l + x_l; (4) DLRM (Meta Deep Learning Recommendation "
        "Model) -- sparse embeddings + dense MLP + dot-product interaction; "
        "(5) DIN/DIEN/BST -- 引入 sequence + attention 学 user 行为. "
        "面试常追问: cross 几阶够 (一般 2-3 阶后边际收益消失); 为什么不直接堆 "
        "MLP (FM-like 结构对 sparse feature 更 sample-efficient). "
        "Cross-links: kg://118 (pillar4.ads_monetization.ctr_prediction), "
        "kg://110 (pillar4.recommender_systems.deep_recommendation), "
        "sd://pinterest-ad-ctr, sd://interview-recommendation-system. "
        "Anti-patterns: 把 DLRM 当 ranking 银弹忽略 retrieval 阶段; "
        "embedding 维度盲堆.",
        ["DoorDash", "LinkedIn", "Meta", "TikTok", "Uber"],
    ),
    (
        "cold-start-strategies",
        "Cold-Start: User / Item / Tenant",
        "Cold-start (冷启动) 三类: new-user (无行为), new-item (无 interaction), "
        "new-tenant (新城市/新品类). 通用打法: (a) Content-based fallback -- "
        "item metadata + text/image embedding 进 two-tower; (b) Meta-learning "
        "/ MAML -- 少样本快速适应; (c) Bandit exploration -- Thompson sampling "
        "/ epsilon-greedy 主动 explore 收集信号; (d) Borrow signal from "
        "similar entities -- e.g. 新餐厅借类目+地理邻居的 baseline. "
        "面试常追问: cold-item 怎么避免 popularity bias 把它埋掉 (用 "
        "exploration bucket 给保底曝光). Cross-links: kg://199 "
        "(pillar4.recommender_systems.cold_start), kg://105 "
        "(exploration_exploitation), sd://interview-recommendation-system. "
        "Anti-patterns: 等行为数据攒够再 rank (永远 cold); 全靠 popularity "
        "(新 item 永远进不了 top-K).",
        ["DoorDash", "Google", "LinkedIn", "Meta", "TikTok", "Uber"],
    ),
    (
        "ndcg-recall-mrr-eval",
        "Ranking Evaluation: NDCG / Recall@K / MRR / MAP",
        "Ranking metric 选型: (a) NDCG@K (Normalized Discounted Cumulative "
        "Gain) -- 关心 graded relevance + 位置折扣, 主流 ranking 指标; "
        "(b) Recall@K -- retrieval 阶段主指标, 关心 top-K 是否包含相关 doc; "
        "(c) MRR (Mean Reciprocal Rank) -- 关心第一个相关结果的位置, "
        "适合 known-item search (autocomplete / QA); (d) MAP (Mean Average "
        "Precision) -- 平均 precision over recall levels. 选型: 推荐 feed "
        "用 NDCG, retrieval 用 Recall@K, 搜索用 MRR + NDCG. "
        "Cross-links: kg://99 (multi_stage_ranking), sd://pinterest-pin-ranking, "
        "sd://interview-recommendation-system. Anti-patterns: 用 AUC 评 ranking "
        "(忽略位置); NDCG 不指定 K (K=10 vs K=100 结论可能反); 离线指标涨但 "
        "线上 A/B 跌 (说明 metric proxy 失效).",
        ["DoorDash", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "calibration-isotonic-platt",
        "Probability Calibration: Isotonic / Platt / Temperature",
        "CTR / CVR / fraud-score 类模型出 logit 后必须 calibration (校准) -- "
        "raw model output 不等于 P(click). 三大方法: (1) Platt scaling -- "
        "用 logistic regression 拟合 logit, 假设输出近似高斯, 适合 SVM/小数据; "
        "(2) Isotonic regression -- 非参数单调回归, 灵活但需 1k+ holdout 样本; "
        "(3) Temperature scaling -- 单参数 T 除 logit, 适合 deep learning, "
        "保 ranking 不变. Multi-class 推 vector scaling. 面试常追问: "
        "calibration drift 怎么监控 (ECE / Brier score / reliability diagram); "
        "ranking-only 任务是否需 calibration (排序任务不需, 但混合 ranking + "
        "bidding / Lagrangian 优化必需). Cross-links: kg://118 "
        "(ctr_prediction), sd://pinterest-ad-ctr, "
        "sd://interview-ad-click-aggregator. Anti-patterns: 把 raw sigmoid "
        "当概率用; calibration 在 train set 上拟合 (必须 holdout); "
        "忽略 segment-level miscalibration.",
        ["DoorDash", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "diversity-mmr-dpp",
        "Diversity Reranking: MMR / DPP / Constraint",
        "Diversity (多样性) reranking 防 feed/SERP 同质化. 三类方法: "
        "(1) MMR (Maximal Marginal Relevance) -- 贪心选下一个 item 最大化 "
        "lambda*relevance - (1-lambda)*max-similarity-to-selected, "
        "O(K^2), 简单工业用最多; (2) DPP (Determinantal Point Process) -- "
        "用 kernel matrix 决定 subset, 数学上更 principled, 但 O(K^3); "
        "(3) Constraint-based -- per-category exposure floor / fairness "
        "guarantee, 转 LP / ILP 求解. 面试常追问: lambda 怎么调 (offline "
        "tune on holdout NDCG@K @ diversity-bucket); 多样性指标怎么量化 "
        "(intra-list distance / category coverage / entropy). Cross-links: "
        "kg://99 (multi_stage_ranking), sd://interview-recommendation-system, "
        "sd://pinterest-pin-ranking. Anti-patterns: 把 MMR 当 'always 提升 "
        "用户体验' 不做 A/B; diversity 加太重导致相关性塌方.",
        ["DoorDash", "Google", "LinkedIn", "Meta", "Uber"],
    ),
    (
        "ab-testing-experiment-framework",
        "A/B Testing & Experiment Framework",
        "A/B test (随机对照实验) 是 ranking/recsys 上线唯一 ground truth. "
        "核心组件: (1) bucketing -- 用户级 vs session 级 vs request 级 hash "
        "分桶, 用户级最常用; (2) sample size / power calc -- alpha/beta + "
        "MDE (Minimum Detectable Effect) 决定流量分配 + 跑多久; "
        "(3) guardrail metrics -- 北极星指标 + latency / crash / fairness "
        "护栏, 任一 guardrail 显著负即 abort; (4) novelty effect -- 新功能 "
        "前 1-2 周收益虚高, 须 ramp + 长期 holdout; (5) interference -- "
        "marketplace / network effect 下 SUTVA 假设破坏, 需 cluster "
        "randomization 或 switchback. Cross-links: kg://104 "
        "(pillar3.building_blocks.ab_testing), sd://pinterest-pin-ranking, "
        "sd://interview-recommendation-system. Anti-patterns: 不预 commit "
        "metric 然后 cherry-pick (p-hacking); A/B 显著 -> ship 不看 segment; "
        "guardrail metric 缺位.",
        ["DoorDash", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "exploration-exploitation-bandit",
        "Exploration vs Exploitation: Bandit Algorithms",
        "Recsys / search 永远在 explore (收集 cold/long-tail item 信号) 与 "
        "exploit (推 known-good item 拿短期 reward) 之间权衡. 三大 bandit "
        "算法: (1) epsilon-greedy -- 概率 epsilon 随机, 简单粗暴, "
        "epsilon decay schedule 是关键; (2) UCB (Upper Confidence Bound) -- "
        "score = mean + c*sqrt(ln(t)/n), confidence-driven exploration; "
        "(3) Thompson sampling -- Bayesian posterior 采样选 arm, 工业界口碑 "
        "最好, sample efficient. Contextual bandit (LinUCB / neural bandit) "
        "把 user/item context 喂入. 应用: cold-start exploration, "
        "新创意 (creative) testing, A/B 替代品. Cross-links: kg://105 "
        "(exploration_exploitation), kg://199 (cold_start), "
        "sd://interview-recommendation-system. Anti-patterns: 永远 exploit "
        "(long-tail 永远不动); exploration 比例不衰减 (用户体验受损).",
        ["DoorDash", "LinkedIn", "Uber"],
    ),
    (
        "popularity-bias-debiasing",
        "Popularity Bias / Position Bias / Selection Bias",
        "训练数据本身有 bias: (a) popularity bias -- 高频 item 在 in-batch "
        "negative 里被过度惩罚, 排序里又被过度曝光, 形成 'rich-get-richer' "
        "正反馈; (b) position bias -- 用户更倾向点高位 item, 导致 click "
        "数据天然偏向高位; (c) selection bias -- 只看到 ranker exposed 的 "
        "item, 没 exposed 的永远没 label. 修法: (1) sampled-softmax logQ "
        "修正去 popularity bias; (2) position bias 用 PAL (Position-Aware "
        "Learning) / IPS (Inverse Propensity Scoring) 折去; (3) selection "
        "bias 用 logging policy + IPS 或 doubly-robust estimator. 面试 "
        "follow-up: 怎么验证 debiasing 真有效 (offline counterfactual eval "
        "+ online A/B). Cross-links: kg://99 (multi_stage_ranking), "
        "kg://121 (causal_inference), sd://pinterest-pin-ranking. "
        "Anti-patterns: 把 click 当 ground-truth label 训; debiasing 没做 "
        "counterfactual sanity check.",
        ["DoorDash", "Google", "Uber"],
    ),
    (
        "feature-store",
        "Feature Store: Online + Offline Parity",
        "Feature store (特征库) 是 ML 系统中 feature 的 single source of "
        "truth, 解决 train-serve skew (训练-服务偏移). 双栈架构: "
        "(a) offline store -- Hive / Iceberg / Delta, 训练 pipeline 拉数据, "
        "supports time-travel join + point-in-time correctness; "
        "(b) online store -- Redis / DynamoDB / Cassandra, serving 路径 "
        "毫秒读取. 关键组件: feature definition DSL, materialization job, "
        "feature versioning, monitoring (drift detection). 工业代表: "
        "Uber Michelangelo, Airbnb Zipline, Feast (开源). 面试 follow-up: "
        "TTL 怎么定 (real-time feature 几秒, batch feature 小时-天); "
        "online/offline parity 怎么保 (同一份 transformation code path). "
        "Cross-links: kg://101 (pillar3.building_blocks.feature_store), "
        "kg://135 (pillar5.data_infra.feature_store), kg://103 "
        "(realtime_features), sd://interview-recommendation-system. "
        "Anti-patterns: train 用 offline aggregation serve 用 raw event "
        "(skew); 不监控 feature drift.",
        ["DoorDash", "LinkedIn", "TikTok", "Uber"],
    ),
    (
        "stream-batch-lambda-kappa",
        "Stream + Batch: Lambda / Kappa Architecture",
        "实时数据 pipeline 两大架构: (1) Lambda architecture -- batch layer "
        "(Spark / Hadoop, 高准确度低 freshness) + speed layer (Flink / "
        "Kafka Streams, 低延迟近似), 双写后 query layer 合并. 缺点: 双套 "
        "code path 维护成本高; (2) Kappa architecture -- 全 stream "
        "(Flink + Kafka), reprocess 历史数据靠重放 log, 单套 code path. "
        "组件栈: Kafka (message bus, ordered partitioned log), Flink "
        "(stateful streaming, exactly-once via 2PC + checkpoint), "
        "Spark (batch + structured streaming). 关键概念: watermark "
        "(event-time vs processing-time), windowing, exactly-once "
        "(idempotent producer + transactional commit). 应用: 实时 CTR "
        "聚合, 实时特征更新, fraud 实时检测. Cross-links: kg://103 "
        "(realtime_features), kg://134 (pillar5.data_infra.data_processing), "
        "sd://interview-ad-click-aggregator (Lambda 经典案例), "
        "sd://distributed-task-queue (idempotency). Anti-patterns: 全用 "
        "batch 错失 freshness 收益; 全用 stream 但 reprocess 能力差.",
        ["DoorDash", "Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "consistent-hashing-sharding",
        "Consistent Hashing / Sharding / Partitioning",
        "Consistent hashing (一致性哈希) 解决 distributed cache / sharded "
        "DB 扩缩容时 minimal key reshuffling -- 加减节点只动 1/N 的 key, "
        "不是全量 rehash. 实现: hash ring + virtual nodes (vnode, 解决 "
        "hot spot 不均衡), 每节点持 100-200 vnode. 应用: Cassandra / "
        "DynamoDB partition, Redis cluster, CDN edge selection, "
        "distributed cache (Memcached). 配套: rendezvous hashing "
        "(替代方案, 无 ring 状态), jump hash (Google, 极简). 面试 "
        "follow-up: 怎么处理 hot key (replication + per-key cache layer + "
        "split shard); 数据倾斜 (skew) 怎么 detect (per-shard QPS / latency "
        "监控). Cross-links: sd://interview-distributed-cache, "
        "sd://database-comparison (Cassandra), sd://interview-news-feed. "
        "Anti-patterns: 不用 vnode 导致负载倾斜; resharding 时不做 "
        "double-write 导致数据丢失.",
        ["Adobe", "LinkedIn", "Meta", "Uber"],
    ),
    (
        "cache-strategies-lru-lfu",
        "Cache Strategies: LRU / LFU / TTL / Write-Through",
        "Cache 是 latency optimization 的第一招. 淘汰策略 (eviction): "
        "(a) LRU (Least Recently Used) -- 双向链表 + hash, O(1) op, "
        "适合时间局部性 (temporal locality); (b) LFU (Least Frequently "
        "Used) -- counter-based, 适合稳定热点; (c) TTL (Time-To-Live) -- "
        "时间窗口, 适合时效数据; (d) ARC / W-TinyLFU -- 自适应混合. "
        "写策略: write-through (同写 cache + DB, 强一致, 慢) vs "
        "write-back (只写 cache, 异步刷, 快但可能丢) vs cache-aside "
        "(应用层 read-through, 最常用). 三大灾难: cache penetration "
        "(穿透, 查不存在 key 直击 DB, 救法: bloom filter + 空值缓存); "
        "cache breakdown (击穿, 热 key 失效瞬间打爆 DB, 救法: mutex / "
        "永不过期 + 后台刷新); cache avalanche (雪崩, 大量 key 同时失效, "
        "救法: 随机 TTL + 多级缓存). Cross-links: kg://133 "
        "(pillar5.serving_infra.latency_optimization), "
        "sd://interview-distributed-cache, sd://interview-news-feed. "
        "Anti-patterns: 不监控 cache hit rate; TTL 全相同导致雪崩.",
        ["DoorDash", "Google", "LinkedIn", "Meta", "Uber"],
    ),
    (
        "count-min-sketch-heavy-hitters",
        "Streaming Approximations: CMS / Heavy Hitters / HyperLogLog",
        "流式近似 (streaming approximation) 算法在亚线性空间内估计大数据 "
        "属性. 三大经典: (1) Count-Min Sketch (CMS) -- d 个 hash function + "
        "w 列计数器 matrix, O(1) update + 估计 freq, 误差 +/- epsilon * "
        "total_count w.p. 1-delta; (2) Misra-Gries / Space-Saving -- "
        "heavy hitters (>theta% 频率) 检测, 维护 1/theta 个 candidate slot; "
        "(3) HyperLogLog -- distinct count 近似, 1.5KB 估 1B+ unique items, "
        "误差 ~2%. 应用: top-K trending search query, DDoS hot-IP detection, "
        "real-time analytics, ad fraud. 面试常考: 为什么不用精确 hash map "
        "(memory 爆); 误差 vs 内存 trade-off 怎么调 (w / d 与 epsilon / "
        "delta 的关系). Cross-links: sd://interview-top-k-heavy-hitters "
        "(canonical SD), sd://interview-search-autocomplete (trending query), "
        "sd://interview-ad-click-aggregator. Anti-patterns: 把 CMS 当精确 "
        "(只能上界估); HLL 用在小数据 (反而占空间).",
        ["LinkedIn", "Meta", "Pinterest"],
    ),
    (
        "geohash-h3-quadtree",
        "Geo-Spatial Indexing: Geohash / H3 / S2 / Quadtree",
        "地理位置查询 (proximity / radius / nearest) 必须有 spatial index. "
        "四大方案: (1) Geohash -- base32 编码 lat/lng 为字符串, prefix "
        "match 即邻近, 简单但 cell 不均匀 (赤道大极地小); (2) H3 (Uber) -- "
        "六边形 hex grid, 邻居 always 6 个, 距离均匀, 多层级 (resolution "
        "0-15); (3) S2 (Google) -- 球面 cell tree, Hilbert curve, "
        "地理 query 友好; (4) Quadtree -- 递归四分, 适合非均匀分布. "
        "应用: rideshare (找半径内司机), food delivery (3-10mi 餐厅), "
        "Nearby Friends, geofencing. 面试常考: 为什么 H3 选 hexagon "
        "(邻居距离均匀, 不像 square 对角邻居距离不同); cell resolution "
        "怎么定 (与 query radius 匹配, 一般 cell 边长 ~ radius). "
        "Cross-links: kg://119 (dynamic_pricing), kg://120 (eta_prediction), "
        "sd://interview-proximity-service (Yelp 经典), "
        "sd://interview-ride-sharing (Uber). Anti-patterns: 用 lat/lng "
        "做 B-tree query (扫全表); cell resolution 与 radius 不匹配 "
        "导致检索过多 cell.",
        ["DoorDash", "Meta", "Uber"],
    ),
    (
        "back-of-envelope-p99-budget",
        "Back-of-Envelope Estimation + P99 Latency Budget",
        "SD 面试开局必走两步: (1) Back-of-envelope (规模估算) -- DAU * "
        "请求/用户/天 / 86400 = QPS, 峰值 5-8x (注意: 外卖/广告等 traffic "
        "极 peaky, 按 8x 预留); 存储 = N entities * size, 区分热冷; "
        "(2) Latency budget -- p99 (99th percentile) 是 SLA 主指标, 不是 "
        "p50. Feed serving 典型预算: API gateway 5ms + retrieval 10ms + "
        "ranking 30ms + rerank 10ms + serialization 10ms = ~70ms, 留 30ms "
        "buffer 凑 p99 < 100ms. P99 比 p50 高 5-10x 是常态 (long-tail "
        "GC pause / network jitter / hot key). 关键 trade-off: pre-compute "
        "vs on-the-fly (latency 紧就预计算 + 牺牲 freshness). Cross-links: "
        "kg://133 (latency_optimization), sd://interview-news-feed, "
        "sd://interview-recommendation-system. Anti-patterns: 报 average "
        "latency (隐藏 long tail); SLA 与 capacity 算分裂 (容量按 peak QPS "
        "+ p99 latency 一起算).",
        ["Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "knowledge-distillation",
        "Knowledge Distillation: Teacher -> Student",
        "Knowledge distillation (知识蒸馏) 把大 teacher model 的知识 "
        "压缩进小 student model -- student 不仅学 hard label (ground truth), "
        "还学 teacher 的 soft probability (logit / temperature-scaled "
        "softmax), 保住 teacher 的 dark knowledge (类间相似性). 三大用途: "
        "(1) serving 加速 -- 训练时大模型, 部署小模型, latency / cost / "
        "memory 降一个数量级; (2) pre-ranking -- 用 fine-ranker 蒸 "
        "pre-ranker (DoorDash / TikTok / Uber 都这么干); (3) cross-domain "
        "transfer -- text/image teacher -> light embedder. 损失: KL "
        "divergence(student || teacher) + alpha * cross-entropy(student, "
        "label), temperature T 调节 soft target 分布. Cross-links: "
        "kg://106 (pillar3.building_blocks.knowledge_distillation), "
        "kg://131 (pillar5.serving_infra.optimization), "
        "kg://132 (pillar5.serving_infra.llm_serving). Anti-patterns: "
        "蒸出来的 student 在 long-tail data 上崩 (teacher 也不会的事 student "
        "更不会); 不用 temperature scaling 直接蒸 hard label (退化为普通 "
        "supervised training).",
        ["DoorDash", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "quantization-pruning-serving-opt",
        "Serving Optimization: Quantization / Pruning / Mixed Precision",
        "Latency / cost / memory 三联优化: (1) Quantization (量化) -- "
        "weight + activation 从 FP32 -> INT8 / INT4, 推理加速 2-4x, "
        "memory 减 4-8x. PTQ (Post-Training Quantization) 简单但精度损失 "
        "大; QAT (Quantization-Aware Training) 训练时模拟量化噪声, "
        "精度损失 <1%. LLM 主流: GPTQ / AWQ / SmoothQuant. "
        "(2) Pruning (剪枝) -- 把绝对值小的 weight 置零, structured "
        "pruning (整 channel / head 删除) 真省 FLOPs, unstructured 稀疏 "
        "性硬件难加速. (3) Mixed precision -- FP16 / BF16 训练 + FP32 "
        "master weight, 速度翻倍 + 精度无损. (4) Distillation 配合 "
        "quantization 是 production LLM serving 标配. Cross-links: "
        "kg://131 (pillar5.serving_infra.optimization), kg://133 "
        "(latency_optimization), kg://127 (pillar5.training_infra."
        "mixed_precision), kg://132 (llm_serving). Anti-patterns: PTQ "
        "上来就 INT4 不验 accuracy regression; 把 unstructured pruning "
        "当 latency 优化 (硬件不支持稀疏不会快).",
        ["Adobe", "DoorDash", "Google", "LinkedIn", "Pinterest"],
    ),
]


def sha256_subtree(conn: sqlite3.Connection) -> str:
    """SHA-256 of all 'meta-prep/system-design-must-knows%' rows, ordered by path."""
    rows = conn.execute(
        "SELECT path, depth, title, description, relevant_companies "
        "FROM framework_nodes "
        "WHERE path = ? OR path LIKE 'meta-prep/system-design-must-knows/%' "
        "ORDER BY path",
        (PARENT_PATH,),
    ).fetchall()
    h = hashlib.sha256()
    for r in rows:
        h.update(repr(r).encode("utf-8"))
    return h.hexdigest()


def update_parent_description(
    conn: sqlite3.Connection, parent_id: int, current_desc: str | None
) -> str:
    """Update parent description if still TODO; otherwise SKIP."""
    if current_desc and PARENT_TODO_MARKER in current_desc:
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (PARENT_DESCRIPTION_NEW, parent_id),
        )
        return "UPDATED"
    if current_desc == PARENT_DESCRIPTION_NEW:
        return "SKIPPED"
    raise RuntimeError(
        f"[CONFLICT] parent description has been edited to something "
        f"other than the TODO marker or the seed's target text. "
        f"Refusing to overwrite. Current: {current_desc!r}"
    )


def upsert_child(
    conn: sqlite3.Connection,
    *,
    parent_id: int,
    slug: str,
    title: str,
    description: str,
    relevant_companies_csv: str,
) -> tuple[str, int]:
    """Insert child if absent; SKIP if present with matching content."""
    path = f"{PARENT_PATH}/{slug}"
    existing = conn.execute(
        "SELECT id, title, description, relevant_companies "
        "FROM framework_nodes WHERE path = ?",
        (path,),
    ).fetchone()
    if existing is not None:
        node_id, ex_title, ex_desc, ex_companies = existing
        if (ex_title == title and ex_desc == description
                and (ex_companies or "") == relevant_companies_csv):
            return "SKIPPED", node_id
        raise RuntimeError(
            f"[CONFLICT] path={path!r} exists but content has drifted from "
            f"seed. title_match={ex_title == title} "
            f"desc_match={ex_desc == description} "
            f"companies_match={(ex_companies or '') == relevant_companies_csv}. "
            f"Refusing to overwrite hand-edited content; resolve by either "
            f"reverting the edit or updating the seed."
        )
    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description,
             importance, priority, status, progress_pct, relevant_companies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (parent_id, path, 2, title, description,
         0.7, "P1", "not_started", 0.0, relevant_companies_csv),
    )
    return "INSERTED", cur.lastrowid


CROSS_LINK_RE = re.compile(r"(kg://\d+|sd://[a-z0-9-]+)")


def assert_promotion_threshold() -> None:
    """Static AC: each cluster has >=3 P0+P1 sources, all valid names; >=20 children;
    each description embeds at least one kg:// or sd:// cross-link."""
    if len(CLUSTERS) < 20:
        raise AssertionError(
            f"[AC-FAIL] only {len(CLUSTERS)} clusters defined; AC requires >=20"
        )
    seen_slugs: set[str] = set()
    for slug, _title, description, companies in CLUSTERS:
        if slug in seen_slugs:
            raise AssertionError(f"[AC-FAIL] duplicate slug {slug!r}")
        seen_slugs.add(slug)
        if len(companies) < 3:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has only {len(companies)} sources; "
                f"promotion threshold is >=3"
            )
        if len(companies) != len(set(companies)):
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has duplicate sources: {companies}"
            )
        invalid = set(companies) - P0P1_COMPANY_NAMES
        if invalid:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} references non-P0+P1 companies: "
                f"{sorted(invalid)}"
            )
        if not CROSS_LINK_RE.search(description):
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} description has no kg:// or sd:// "
                f"cross-link"
            )


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Update parent description (if TODO) and seed N child clusters."""
    counts = {"INSERTED": 0, "UPDATED": 0, "SKIPPED": 0}

    parent = conn.execute(
        "SELECT id, description FROM framework_nodes WHERE path = ?",
        (PARENT_PATH,),
    ).fetchone()
    if parent is None:
        raise RuntimeError(
            f"[FAIL] parent {PARENT_PATH!r} does not exist; "
            f"run scripts/seed_meta_prep_pillar.py first (T-P1-800)."
        )
    parent_id, parent_desc = parent
    parent_action = update_parent_description(conn, parent_id, parent_desc)
    counts[parent_action] += 1
    print(f"[{parent_action}] parent id={parent_id} path={PARENT_PATH}")

    for slug, title, description, companies in CLUSTERS:
        relevant_companies_csv = ",".join(companies)
        action, child_id = upsert_child(
            conn,
            parent_id=parent_id,
            slug=slug,
            title=title,
            description=description,
            relevant_companies_csv=relevant_companies_csv,
        )
        counts[action] += 1
        n_links = len(CROSS_LINK_RE.findall(description))
        print(
            f"[{action}] child  id={child_id} "
            f"slug={slug} sources={len(companies)} cross_links={n_links}"
        )

    return counts


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    assert_promotion_threshold()
    print(
        f"[AC-OK] all {len(CLUSTERS)} clusters have >=3 valid P0+P1 sources "
        f"and embed at least one kg:// or sd:// cross-link"
    )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_subtree(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = seed(conn)
        conn.commit()

        post_hash = sha256_subtree(conn)
        print(f"[POST] sha256={post_hash}")

        total = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes "
            "WHERE path = ? OR path LIKE 'meta-prep/system-design-must-knows/%'",
            (PARENT_PATH,),
        ).fetchone()[0]
    finally:
        conn.close()

    print(
        f"[SUMMARY] inserted={counts['INSERTED']} "
        f"updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total_in_subtree={total}"
    )

    expected_total = 1 + len(CLUSTERS)
    if total != expected_total:
        print(f"[FAIL] Expected {expected_total} rows, got {total}")
        sys.exit(1)
    touched = counts["INSERTED"] + counts["UPDATED"] + counts["SKIPPED"]
    if touched != expected_total:
        print(f"[FAIL] Expected to touch {expected_total} nodes, touched {touched}")
        sys.exit(1)
    print("[DONE]")


if __name__ == "__main__":
    main()
