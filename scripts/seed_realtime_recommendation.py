"""Seed framework node: pillar3.design_problems.realtime_recommendation.

Creates the leaf ``pillar3.design_problems.realtime_recommendation`` under
``pillar3.design_problems`` and populates its ``description`` via
StudyNoteBuilder. Merges content from the three DoorDash prep files
(ranking, retrieval, search) into a high-level real-time recommendation
system design note. Deep building-block content is linked out to existing
sibling nodes (two_tower_model=98, multi_stage_ranking=99, ann=100,
feature_store=101, realtime_features=103, ab_testing=104).

Usage::

    python scripts/seed_realtime_recommendation.py

Idempotent: re-running updates in place.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"

PARENT_PATH = "pillar3.design_problems"
NODE_PATH = "pillar3.design_problems.realtime_recommendation"
NODE_TITLE = "Real-Time Recommendation System Design"


def build_content() -> str:
    b = StudyNoteBuilder()
    b.set_title("Real-Time Recommendation System: End-to-End Design")

    b.add_prerequisites([
        "多阶段漏斗（multi-stage funnel）：召回 -> 粗排 -> 精排 -> 重排",
        "向量检索与 ANN：内积 / 余弦相似度、HNSW / IVF-PQ 基础",
        "梯度排序模型：Wide&Deep / DeepFM / DCN / MMoE 了解即可",
        "Feature store 概念：online / offline 双写、point-in-time correctness",
        "A/B 实验：功效分析、CUPED、最小可检测提升 MDE",
    ])

    b.add_term("CG", "Candidate Generation",
               "召回阶段，从亿级物品中粗筛数千个候选，优化 Recall")
    b.add_term("LTR", "Learning to Rank",
               "pointwise / pairwise / listwise 三种学习范式")
    b.add_term("MMoE", "Multi-gate Mixture-of-Experts",
               "多任务共享专家、每个任务独立 gate，缓解负迁移")
    b.add_term("PSI", "Population Stability Index",
               "特征 / 打分分布漂移的监测指标，阈值 0.1 / 0.25")
    b.add_term("ANN", "Approximate Nearest Neighbor",
               "在线召回的亚毫秒向量检索；FAISS / HNSW / ScaNN")
    b.add_term("FS", "Feature Store",
               "在线低延迟 KV + 离线批特征仓库双写；解决训练-服务不一致")
    b.add_term("MDE", "Minimum Detectable Effect",
               "A/B 实验能检测到的最小 lift，决定实验样本量与运行时长")

    # ------------------------------------------------------------------
    b.add_section("1. Problem Framing & Clarify-First", [
        (
            "**Real-Time Recommendation（实时推荐）**：面向 feed / 首页 / 搜索落地页，"
            "在用户每次请求时（或每次会话推进时）基于最新上下文和行为重新生成排序列表。"
            "与离线批量推荐（T+1 计算物料池）对立，实时推荐对**延迟（p99 < 200ms）**、"
            "**新鲜度（新物品 < 10 min 可被召回）**、以及**个性化（当前会话行为 < 1 min 生效）**三项同时提出硬约束。"
        ),
        (
            "**面试必问澄清清单（先问再答）**：\n"
            "- **Scale**：DAU、QPS、物品库规模 U、平均每用户每日请求数？\n"
            "- **Latency budget**：端到端 p99 SLA（典型 150-300ms），召回 / 排序 / 重排各多少？\n"
            "- **Freshness**：新物品上架多久可召回？用户实时行为（点击 / 不喜欢）多久可影响下次请求？\n"
            "- **Objectives**：单目标（CTR）还是多目标（点击 + 停留 + 转化 + 次日留存）？业务权重？\n"
            "- **Cold start**：新用户、新物品、新上下文各占比多少？有无侧信息（content）？\n"
            "- **Constraints**：多样性 / 去重 / 广告混排 / 合规黑白名单 / PII？"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("2. Baseline -> Deep Pipeline (从简到深)", [
        (
            "**面试铁律**：先给**baseline**，再讲**deep**。跳过 baseline 直接甩出 two-tower + MMoE + reranker"
            "会让面试官怀疑你是否真正理解权衡。"
        ),
        (
            "**Baseline（1-2 周可上线）**：\n"
            "- **召回**：热门（global top-N by CTR）+ 协同过滤（item2item co-visit matrix）+ 类别回退。\n"
            "- **排序**：Logistic Regression / GBDT（XGBoost / LightGBM），特征 = 用户 side + 物品 side + 交叉统计。\n"
            "- **服务**：离线每日批量生成 <user_id, ranked_items> 表，存 Redis，请求时直接查；新物品走热门池 fallback。\n"
            "- **能上到什么水平**：CTR 通常可达到 deep 模型 70-80% 的相对收益，工程复杂度 1/10。"
        ),
        (
            "**Deep Pipeline（成熟期架构）**：\n"
            "- **召回**：two-tower 模型学 user/item embedding，ANN（HNSW）在线检索 top-1000；"
            "多路召回并联（two-tower + item-CF + 实时行为序列 SASRec + 冷启动热门兜底）。\n"
            "- **粗排（pre-rank）**：小模型（2 层 MLP）对 1000 -> 300，只用轻特征，< 20ms。\n"
            "- **精排（ranking）**：DCN-v2 / DeepFM / MMoE，预测多目标（pCTR, pCVR, pDwell），"
            "融合公式 score = Σ w_k · f(p_k)，< 100ms on 300 items。\n"
            "- **重排（re-ranking）**：业务规则 + 多样性（MMR / DPP）+ 广告混排 + 去重 + 新鲜度 boost。\n"
            "- 见 [多阶段排序建筑块 pillar3.building_blocks.multi_stage_ranking](#)。"
        ),
        FormulaBlock(
            explanation="多目标融合打分（DoorDash Universal Ranker 风格）：",
            latex=r"\text{score}(u, i) = \sum_{k=1}^{K} w_k \cdot \phi_k(\hat{p}_k(u, i))",
        ),
        (
            "其中 phi_k 是对每个目标概率的校准/非线性变换（如 sigmoid 温度调节或 logit 空间加权），"
            "w_k 由业务方案决定（CTR 0.5 + CVR 0.3 + Dwell 0.2 常见起点），"
            "可通过 online A/B 扫描网格或用 multi-gradient descent 自动学习（Pareto front）。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("3. Two-Tower Retrieval + ANN (召回核心)", [
        (
            "**Two-Tower**：用户塔 E_u(u) 和物品塔 E_i(i) 独立编码为 d 维 embedding，"
            "相似度用内积或余弦。训练时用 **in-batch negatives + sampled softmax** 或 **contrastive loss**，"
            "服务时物品塔离线/准实时批量编码，用户塔请求时在线编码，再用 **ANN** 检索 top-N。"
            "详见 [pillar3.building_blocks.two_tower_model](#) 与 [pillar3.building_blocks.ann](#)。"
        ),
        FormulaBlock(
            explanation="Sampled softmax with log-Q correction（纠正热门 item 被采样过多）：",
            latex=r"\mathcal{L} = -\log \frac{\exp(s(u, i^+) - \log Q(i^+))}{\sum_{i \in B} \exp(s(u, i) - \log Q(i))}",
        ),
        (
            "**负采样策略**（面试常问）：\n"
            "- **Random**：最简单，但负样本过易，模型欠挑战。\n"
            "- **In-batch**：mini-batch 内其他正样本作为彼此的负样本，计算高效，自带热门偏置（需 log-Q 纠正）。\n"
            "- **Hard negatives**：从上一轮召回结果里取高分但非点击的样本，显著提升 top-K 精度；"
            "但训练不稳定，通常混合比例 80% easy + 20% hard。\n"
            "- **Mixed negative sampling**：batch-neg + 全局采样 + hard neg 三路混合（工业推荐实践）。"
        ),
        (
            "**ANN 选型**：\n"
            "- **HNSW**：图结构，QPS 最高，内存占用大（2-4x embedding 大小），适合 < 100M 物品；\n"
            "- **IVF-PQ (FAISS)**：倒排 + 乘积量化，内存占用小，精度略低，适合 B 级物品；\n"
            "- **ScaNN (Google)**：anisotropic quantization，在高召回区间精度最好。\n"
            "**新鲜度要求**：HNSW 支持在线 insert；若用静态索引（FAISS IVF-PQ build-once），"
            "新物品需分层索引（主索引 + 小 incremental 索引）并定期合并。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("4. Ranking: Deep Models + Multi-Task Learning", [
        (
            "**特征族**：\n"
            "- **User side**：长期画像（历史类别偏好、复购周期）+ 实时会话（当前 session click seq，< 1 min 延迟）。\n"
            "- **Item side**：静态（类别、价格、店家评分）+ 动态（CTR EMA、近 1h 曝光量、库存）。\n"
            "- **Context**：时间、地点、设备、天气、促销活动。\n"
            "- **Cross**：user × item 历史交互（是否买过、上次点击时间）、user × category 次数、item 协同 embedding。"
        ),
        (
            "**模型选择（2022+ 工业实践）**：\n"
            "- **DCN-v2** 是 CTR 任务的稳健基线：显式交叉 + DNN 并联，易调优，易部署。\n"
            "- **MMoE / PLE** 用于多任务（CTR + CVR + Dwell + Save），缓解**负迁移（negative transfer）**——"
            "共享专家 + 任务独立 gate 决定共享多少。\n"
            "- **ESMM** 解决 CVR 样本选择偏差：只在点击后有 CVR 标签，ESMM 用 pCTR × pCVR|CTR 在全空间训练。\n"
            "- **序列模型（SASRec / BST / DIN）**：注意力对近期行为做动态特征提取，"
            "在新闻 / 短视频流场景中显著优于手工聚合特征。"
        ),
        FormulaBlock(
            explanation="MMoE 任务 k 的输出（n 个共享专家 + 任务独立 gate）：",
            latex=r"y_k = h_k\left(\sum_{j=1}^{n} g_k(x)_j \cdot E_j(x)\right)",
        ),
        (
            "**Calibration**：多目标融合前必须校准——未校准的 sigmoid 输出不能按 `w_k · p_k` 直接加权，"
            "因不同任务的预测置信度尺度不同。常用 **Platt scaling** 或 **isotonic regression** 对 holdout 集拟合。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("5. Re-Ranking: 多样性 / 业务 / 合规", [
        (
            "精排输出按分排序后**必须**过一遍重排器：\n"
            "- **多样性**：MMR（贪心最大边际相关性）或 DPP（行列式点过程）在质量-多样性之间权衡；\n"
            "- **业务规则**：广告混排（每 5 位插 1 ad）、店家多样性（同店不超 2）、类别配比；\n"
            "- **新鲜度 boost**：新物品 / 冷启动物品上位（score + alpha · exp(-age)）；\n"
            "- **合规**：黑白名单、成人内容过滤、品牌互斥（奢侈品不能紧邻折扣）；\n"
            "- **个性化重排**：listwise re-rank 模型（DLCM / PRM）基于整页上下文再次打分。"
        ),
        FormulaBlock(
            explanation="MMR 贪心更新规则（lambda in [0, 1] 控制多样性权重）：",
            latex=r"\text{MMR}(i) = \lambda \cdot \text{rel}(u, i) - (1 - \lambda) \cdot \max_{j \in S} \text{sim}(i, j)",
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("6. Training: Offline + Online 双轨", [
        (
            "**Offline training**：每日 / 每周批训练完整模型（full refresh），用过去 30-90 天日志。"
            "生成新版本模型、特征统计（均值 / 方差 / 分位点）、embedding 表；走 shadow 验证 -> A/B -> 全量 rollout。"
        ),
        (
            "**Online / Incremental training**：\n"
            "- **频率**：每 10-60 min 增量更新（warm-start from latest offline checkpoint）；\n"
            "- **数据**：最近窗口（例如 1h 到 6h）实时日志，**label 等待 attribution window**（点击标签 < 1 min 可得；转化标签可能延迟数天）；\n"
            "- **收益**：新物品新 user 的 embedding 更新、当日热点快速捕获、对热度漂移响应；\n"
            "- **风险**：训练-服务偏差、过拟合短期噪声、catastrophic forgetting；需要 EMA 对齐 + online validation 作兜底。"
        ),
        (
            "**Delayed feedback**：转化事件可能在曝光后 7 天才发生，直接训练会把**未转化**的样本当负样本。"
            "常用 DFM（Delayed Feedback Model, Criteo 2014）学习转化延迟分布，或用 **importance weighting** 修正。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("7. Cold Start (冷启动)", [])
    b.add_comparison_table(
        headers=["场景", "问题", "主要方案"],
        rows=[
            ["新用户", "无历史行为", "注册问卷 / 人口属性模型 / 基于 IP&device 的 look-alike / 热门兜底"],
            ["新物品", "无历史曝光, 无 embedding", "Content-based（文本/图像预训练 embedding）+ 强制探索配额（每页 k 个新 item）"],
            ["新场景", "首次开放城市/品类", "迁移学习（相似城市参数初始化）+ 多臂赌博机（UCB / Thompson）"],
            ["稀疏历史", "行为 < 5 条", "Meta-learning（MAML）或 session-based SASRec"],
            ["冷-热边界", "物品从冷转热", "embedding 快速更新（online learning 高学习率）+ 探索衰减"],
        ],
        title="Cold Start 场景与对策",
    )
    b.add_section("7b. 探索与利用", [
        (
            "**Exploration / Exploitation**：冷物品无历史则 CTR 预估接近先验均值，永远排不上去——必须主动探索。"
            "工业做法：reserve 每页 N 个 slot 给新物品（硬配额），或在 ranking score 里加 **UCB bonus**"
            "`score + c · sqrt(log(T) / n_i)`，或 Thompson sampling 从 Beta 后验采样。"
            "见 [pillar3.building_blocks.exploration_exploitation](#)."
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("8. Monitoring & Drift Detection", [
        (
            "**离线指标**：AUC / GAUC（user-group AUC，去除用户间偏置）、NDCG@K、Recall@K、MAP。"
            "**在线指标**：CTR、CVR、人均停留、次日留存、GMV、多样性熵、负反馈率。"
        ),
        (
            "**Drift 监测**：\n"
            "- **Feature drift**：每小时计算 training 分布 vs serving 分布的 **PSI** / **KL**；阈值 PSI > 0.25 告警；\n"
            "- **Score drift**：模型输出分布日环比 KL，突变触发回滚；\n"
            "- **Label drift**：CTR/CVR 整体均值滑动窗口 z-score；\n"
            "- **Data quality**：feature 缺失率、默认值占比、schema 兼容性。"
        ),
        FormulaBlock(
            explanation="PSI（Population Stability Index），分 B 个桶比较基线 p 与当前 q：",
            latex=r"\text{PSI} = \sum_{b=1}^{B} (q_b - p_b) \cdot \ln \frac{q_b}{p_b}",
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("9. Iteration Flywheel: Shadow -> A/B -> Rollout", [
        (
            "**Shadow traffic**：新模型在线接 100% 流量但**不返回结果**，只记录预测；对比旧模型输出与真实 label 的一致性，"
            "验证上线无崩溃、延迟达标、分数分布合理。\n"
            "**A/B test**：5-10% 流量分桶，跑至少 1-2 周覆盖 weekly seasonality，检查主指标 + guardrail（latency, error rate, 多样性）。"
            "关键概念：**MDE** 决定样本量，CUPED 或方差缩减可降需要量。\n"
            "**Gradual rollout**：A/B 通过后 10% -> 25% -> 50% -> 100%，每步观察 24h 无 regression；\n"
            "**Holdback**：永久保留 1-2% 旧模型流量做**长期效果归因**（30-90 天次日/次周留存）。"
            "详见 [pillar3.building_blocks.ab_testing](#)."
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("10. Latency vs Accuracy Tradeoffs", [
        (
            "p99 < 200ms 的硬约束下，典型分配：**召回 30ms + 粗排 20ms + 精排 100ms + 重排 20ms + 网络/序列化 30ms**。"
            "加大精度往往撞上延迟上限，常用降延迟技术："
        ),
        (
            "- **Distillation（蒸馏）**：大 teacher -> 小 student，精度损失 1-3% 换 5-10x 加速；\n"
            "- **Quantization（量化）**：FP32 -> INT8，embedding/MLP 均适用，精度损失 <1%，2-4x 加速；\n"
            "- **Caching**：user embedding 会话级 cache（< 5 min TTL）、item embedding 天级 cache；\n"
            "- **Two-stage ranking**：精排前用小模型粗排把 candidate 从 1000 削到 300；\n"
            "- **Early exit**：cascade（简单样本走轻模型、难样本升级精模型）；\n"
            "- **Embedding size truncation**：128 -> 64 维常可无损，< 32 维则召回明显下降；\n"
            "- **Batch inference + GPU**：单请求多 item 打包 batch，吞吐随 batch 提升。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("11. Serving Architecture", [
        (
            "```\n"
            "Client --> API Gateway --> Rec Orchestrator\n"
            "                                |\n"
            "          +---------------------+---------------------+\n"
            "          |                     |                     |\n"
            "      User Tower             ANN Index             Feature Store\n"
            "      (CPU/GPU)              (HNSW, shard)         (Redis / RocksDB)\n"
            "          |                     |                     |\n"
            "          +-----------> Candidate Merger <------------+\n"
            "                                |\n"
            "                        Pre-Rank (small MLP)\n"
            "                                |\n"
            "                        Ranking Model (TF-Serving/Triton)\n"
            "                                |\n"
            "                        Re-Ranker (MMR / rules)\n"
            "                                |\n"
            "                        Response (logged to Kafka)\n"
            "```"
        ),
        (
            "**关键组件**：\n"
            "- **Orchestrator**：编排召回并发 / 合并去重 / 超时降级；\n"
            "- **Feature Store**：online 走 Redis/RocksDB，p99 < 5ms；offline 走 S3+Parquet，训练时拉取对齐。"
            "见 [pillar3.building_blocks.feature_store](#) 与 [pillar3.building_blocks.realtime_features](#)。\n"
            "- **Fallback / 降级链**：精排超时 -> 用粗排 -> 用召回分 -> 用热门池；**永远不要返回空结果**。\n"
            "- **Model server**：TF-Serving / Triton，支持多模型版本热加载、A/B 流量切分、GPU 批处理。\n"
            "- **Logging**：曝光 + 点击 + 特征快照（point-in-time）同步进 Kafka -> HDFS，训练用。"
        ),
    ])

    # ------------------------------------------------------------------
    b.add_section("12. Interview Q&A", [])
    b.add_interview_qa(
        "设计一个实时推荐系统，给 1 亿 DAU、100M 物品、p99 < 200ms，你会怎么做？",
        (
            "**先澄清目标**（CTR 单目标 vs 多目标 vs 业务约束）、**新鲜度**（新物品多久可召回）、**冷启动占比**。"
            "假定多目标 + 新物 <10min + 冷启 10%，给**分层架构**："
            "(1) 召回三路并联：two-tower (HNSW, 32 shards) top-500 + item-CF top-200 + 热门兜底 top-100；"
            "(2) 粗排小 MLP 1000 -> 300 (< 20ms)；"
            "(3) 精排 MMoE（CTR+CVR+Dwell）300 items 批量推理，TF-Serving GPU，< 100ms；"
            "(4) 重排 MMR 多样性 + 广告混排 + 合规过滤；"
            "(5) Feature store Redis 存 user/item 特征 p99 < 5ms；"
            "(6) 训练：每日 offline full refresh + 每 30 min incremental；"
            "(7) 监控 PSI / KL / 在线 CTR，shadow -> A/B -> 10/25/50/100% rollout。"
            "**强调延迟分配**与**降级链**。"
        ),
    )
    b.add_interview_qa(
        "新物品冷启动怎么办？特别是刚上架的商品如何不被永久埋没？",
        (
            "**三管齐下**：(1) **Content-based 初始化**：文本/图像过预训练编码器生成初始 item embedding，"
            "即使无交互也能进 two-tower 召回；(2) **硬配额 / 探索 slot**：重排阶段每页保留 k 个新物品位（如 k=2），"
            "或在精排分中加 UCB bonus `c·sqrt(log T / n_i)` 或 Thompson sampling；"
            "(3) **快速 embedding 更新**：冷物品走独立 online learning 通道（高学习率 + 小 batch），"
            "几次点击后 embedding 接近成熟物品，探索衰减。"
            "**监控**：新物品曝光份额、冷-热转化中位时长、冷物品 CTR vs 热物品 CTR 差。"
        ),
    )
    b.add_interview_qa(
        "多目标怎么融合？不同目标量级不一样怎么办？",
        (
            "**Step 1 — 校准**：每个任务 head 的 sigmoid 输出先用 Platt scaling / isotonic regression 校准到真实概率，"
            "否则加权无意义。**Step 2 — 融合公式**：`score = Σ w_k · phi_k(p_k)`，其中 phi_k 可以是 logit、log、"
            "或幂次变换来把不同尺度映射到可加空间（如 CTR 0.1 vs Dwell 60s）。"
            "**Step 3 — 权重学习**：手动网格 + A/B 扫描（起点），或 Pareto multi-gradient descent 自动求前沿，"
            "或 uncertainty weighting / GradNorm 在训练时自适应。"
            "**Step 4 — MMoE/PLE 防负迁移**：共享专家 + 任务独立 gate，"
            "对每个任务选择不同的 expert 组合。监控每任务离线 AUC 不能下降超过 1-2%。"
        ),
    )
    b.add_interview_qa(
        "训练-服务一致性（train-serve skew）如何保证？",
        (
            "**点 1**：特征统一走 **Feature Store** 读写，训练时从 offline 仓库按 **point-in-time** 对齐拉取（"
            "避免拉到未来特征，即 label leakage）；服务时从 online 同源 KV 拉取。"
            "**点 2**：特征变换代码**一份**（Python/C++ 共享库或 feature spec DSL），"
            "训练 pipeline 和在线服务加载同一份 transform。"
            "**点 3**：**Shadow logging** 把线上请求的原始输入 + 特征快照打到 Kafka，"
            "离线可重现打分，对比模型 training 输入差异。**点 4**：部署前 compare_score job "
            "在 holdout 集跑 online vs offline，差异 > 阈值阻止上线。**点 5**：PSI 实时监控特征分布漂移，"
            "及时发现线上特征 bug（默认值变化、schema 错位）。"
        ),
    )
    b.add_interview_qa(
        "A/B test 跑了 1 周，主指标 CTR +0.3%，p-value 0.04，可以全量吗？",
        (
            "**不一定**。要检查：(1) **Guardrail**：latency、error rate、多样性熵、负反馈率、长期留存——"
            "任何一个显著回退都不能全量；(2) **时长**：1 周可能未覆盖 weekly seasonality 和**新奇效应**（new-model bias），"
            "建议至少 2 周 + 跨周末；(3) **样本量 / MDE**：p=0.04 离 0.05 很近，增加样本看是否稳定；"
            "(4) **分桶一致性**：A/A 预实验是否通过？用户/设备分桶是否偏移？"
            "(5) **子群检验**：新用户、低活、长尾品类是否也正向；"
            "(6) **Novelty vs long-term**：新奇收益通常 2 周内衰减，holdback 1-2% 观察 30-90 天次日留存。"
            "通过后 10/25/50/100 四步渐进 rollout。"
        ),
    )

    # ------------------------------------------------------------------
    b.add_checklist("Self-Check (面试前必过)", [
        "能画出 端到端 funnel 图并说出每阶段延迟预算",
        "能解释 two-tower 训练时 in-batch neg + log-Q correction 为什么需要",
        "能区分 HNSW / IVF-PQ / ScaNN 的选型依据",
        "能说明 MMoE 为何缓解负迁移、PLE 相比 MMoE 的改进点",
        "能写出多目标融合公式并解释为何必须先校准",
        "能给出至少 3 种冷启动对策并说明各自适用场景",
        "能列出 5 种延迟-精度权衡技术（蒸馏/量化/缓存/粗排/early exit）",
        "能画出降级链：精排超时 -> ... -> 热门兜底",
        "能解释 PSI 阈值 0.1 / 0.25 意义 + KL drift 监测流程",
        "能讲清 shadow -> A/B(CUPED) -> gradual rollout + holdback 完整流程",
        "能识别 A/B 5 项常见陷阱：新奇效应、分桶偏移、seasonality、guardrail、子群",
        "能解释 delayed feedback（DFM / importance weighting）与 ESMM 各自适用场景",
    ])

    return b.build()


def upsert_leaf(conn: sqlite3.Connection, content: str) -> int:
    parent = conn.execute(
        "SELECT id, depth FROM framework_nodes WHERE path = ?", (PARENT_PATH,)
    ).fetchone()
    if not parent:
        print(f"[FAIL] Parent path {PARENT_PATH} not found")
        sys.exit(1)
    parent_id, parent_depth = parent

    existing = conn.execute(
        "SELECT id FROM framework_nodes WHERE path = ?", (NODE_PATH,)
    ).fetchone()
    if existing:
        node_id = existing[0]
        conn.execute(
            "UPDATE framework_nodes SET description = ?, title = ? WHERE id = ?",
            (content, NODE_TITLE, node_id),
        )
        action = "UPDATED"
    else:
        cur = conn.execute(
            """
            INSERT INTO framework_nodes
                (parent_id, path, depth, title, description, importance, priority, status, progress_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (parent_id, NODE_PATH, parent_depth + 1, NODE_TITLE, content,
             0.95, "P0", "not_started", 0.0),
        )
        node_id = cur.lastrowid
        action = "INSERTED"
    length = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()[0]
    print(f"[{action}] leaf id={node_id} path={NODE_PATH} length={length} chars")
    return node_id


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)
    content = build_content()
    warnings = StudyNoteBuilder.validate(content)
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")
    conn = sqlite3.connect(str(DB_PATH))
    try:
        upsert_leaf(conn, content)
        conn.commit()
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    main()
