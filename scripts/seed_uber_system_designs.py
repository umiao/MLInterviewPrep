"""Seed script: promote Uber golden answers from doc 85 to system_designs rows.

Two Staff-level ML System Design golden answers currently live only inside
``company_documents`` id=85 (markdown). This script promotes them to first-class
``system_designs`` rows so they appear on the /system-design page (new "Uber"
tab) and the Cheat Sheet tab.

Source of truth: doc 85 (``company_documents.content``) remains the canonical
long-form narrative. These rows are a *structured projection* of its sections
1.x / 2.x into the 9 system_designs columns; each ``overview`` links back to the
canonical doc via a ``cd://85`` deep-link rather than fully duplicating it.

Display order: 400 / 401. The literal task spec said 200 / 201, but those are
already occupied by Pinterest rows (pinterest-ad-ctr=200, pinterest-embeddings=201)
and fall inside the frontend's Pinterest tab band [199, 300). 400/401 sit in a
fresh band that backs a dedicated "Uber" tab (see SystemDesignList.tsx).

Idempotent: upserts by slug (insert if missing, else update title/subtitle/order
and all content sections, including cheat_sheet).

Run::

    python scripts/seed_uber_system_designs.py
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

# ---------------------------------------------------------------------------
# Row 1: Uber Eats Restaurant Recommendation (doc 85 section 1.x)
# ---------------------------------------------------------------------------

_RESTAURANT_OVERVIEW = r"""## 题目 (Problem)

设计一个 **Uber Eats 的餐厅推荐系统 (Restaurant Recommendation System)** — App
首页『为你推荐』模块 (home feed personalized module) 的个性化餐厅 feed。目标
Level: **Staff (L6)**。

> 完整长篇叙述见 canonical 源文档 [Uber ML System Design Golden Answers](cd://85)
> (本页是其 section 1.x 的结构化投影 / structured projection)。

### 阶段 0 · 心态与节奏 (开场 30 秒)

> "我先用 3-5 分钟把需求 (requirements) 和 scope 定下来, 然后做规模估算
> (back-of-envelope), 再给一个 high-level 架构。架构出来后我们挑 1-2 个组件做
> deep dive。如果中途你想调整方向, 随时打断我。"

**为什么**: 开场就主导节奏, 把整个 60 分钟的 outline 摊开 — 面试官最怕"看不到
候选人的思路框架"。

### 阶段 1 · 需求澄清 (主动提假设, 而非问开放题)

| 维度 | 我的假设 |
|---|---|
| Feed 形态 | 主页 grid/carousel, ~30 候选, "show more" 进完整推荐页 |
| 个性化粒度 | Per-user, 结合 location + time-of-day + history |
| 配送半径 | 城市核心 3-5mi, 郊区 ~10mi (**不是 20mi, 外卖半径很短**) |
| 实时性 | 首屏预计算, **不要求 in-session 实时 rerank** |
| 广告 | sponsored items 的竞价机制不在本次 scope |

**Non-Functional**: home feed 是首屏, **P99 服务端延迟 < 200ms** (倾向尽量
预计算); 可用性 99.95%+, **graceful degradation** 必须 — 任一 feature service
挂掉要能 fallback 到 popularity-based。

**Out-of-Scope**: in-session rerank、search query understanding、ad auction、
driver 调度 (虽然 ETA 用到它的输出)。

### Success Metrics (主动讲, 体现产品 sense)

- **Product**: Module CTR、CVR (feed->下单转化)、Module adoption rate、
  **Abandonment rate** (用了 feed 没下单转头去 search — home feed 失败的核心信号)。
- **Business**: GMV per session、Search efficiency lift (feed 是否分担 search 负载)、
  长期 retention / DAU。
"""

_RESTAURANT_ARCHITECTURE = r"""## 阶段 3 · High-Level 架构

```
CLIENT (App)
   |
API Gateway / BFF
   |
Feed Service  (orchestrator)
   |
   +-- Context Assembly (user/loc/time/device)
   +-- Feature Store (Online KV: user/item/context feat)
   +-- Restaurant Availability (real-time: open? ETA?)
   |
Candidate Generation  -> ~500-1000
   |  Geo(H3) | ANN(2-tower) | Inverted | Popular | Recent
   |  + Hard filter: "is open / accepting"  <- dead-click 防护
   |
Coarse Ranker (LR / GBDT / light 2-tower)  -> ~100-200
   |
Fine Ranker (DIN / DeepFM / MMoE multi-task)  -> ~30-50
   |  (特征已通过 serving-time snapshot)
   |
Re-ranker  -> ~30
   |  Diversity (MMR / DPP) + Business rules
   |  + Extreme-ETA hard filter + Cold-start boost
   |
[Feed Response]
   |
Logging / Feature Snapshot  <- 关键: snapshot 在 serving 时
   |
Streaming (Kafka/Flink): near-line features -> 回写 Feature Store
   |
Offline (Spark/HDFS): training data prep, model train,
   embedding refresh -> 推回 ANN index, ANN rebuild
```

### 三层时间尺度 (这是 senior 信号)

| 层 | 更新频率 | 例子 |
|---|---|---|
| **Offline (batch)** | 小时 / 天 | 餐厅 embedding、用户 long-term embedding、ANN index |
| **Near-line (streaming)** | 秒 / 分钟 | 用户最近点击、餐厅 ETA、busy 程度、surge |
| **Online (request-time)** | 毫秒 | Ranking inference、context feature、availability filter |

**外卖场景特殊性**: 餐厅"是否还接单 / 当前 ETA"秒级变化, 所以 **near-line 这层
不能省**。这是和 Netflix / Amazon 推荐的核心区别 — 后者物品供给稳定, Uber Eats
的物品 (餐厅) 供给是分钟级动态的。
"""

_RESTAURANT_DATAFLOW = r"""## 阶段 4 · Deep Dive

### Candidate Generation 多路召回 (multi-channel retrieval)

| 召回路 | 算法 | 输出量 | 用途 |
|---|---|---|---|
| Geo | **H3** hexagon index (Uber 自家开源) | ~1000 | 距离硬约束 |
| Embedding ANN | **Two-tower model** + HNSW / IVF | ~500 | 个性化语义匹配 |
| Inverted index | 类目 / 标签倒排 | ~200 | 显式偏好 (爱吃日料) |
| Popularity | 地域 + 时段热门 | ~100 | 兜底 + 冷启动 |
| Recent interaction | 最近交互过的店 + 相似店 | ~100 | 短期兴趣 |

**为什么 H3 而非 geohash** (Uber 面试必答): H3 是 Uber 开源的 hexagonal
hierarchical geospatial index; hexagon 邻居距离均匀 (geohash 方形 grid 对角邻居
距离是边邻居的 $\sqrt{2}$ 倍); 没有 geohash 的边界突变 (相邻点 prefix 可能完全
不同); level 7-9 适合外卖半径。

**Two-tower model** — user / item 两个独立 encoder 共享 embedding 空间:

```
User Tower:  user features + history -> user embedding (256d)
Item Tower:  restaurant features     -> restaurant embedding (256d)
Loss:        in-batch sampled softmax / contrastive
Serving:     user tower 在线 inference (<10ms);
             item tower 离线算好灌进 ANN (HNSW); user emb 在 ANN 找 top-K
```

**多路 merge**: (1) Unified ranking — 各路只输出 candidate id 不带 score, 全交
coarse ranker 重打分 (无需 calibration); (2) Quota allocation — 每路给配额。倾向
#1 (让 ranker 学比手工调配额好), 但冷启动 #2 更稳。

**Sharding vs IVF (常见混淆)**: sharding 按城市/region 切分索引 (地理天然分片);
IVF / HNSW 是 shard 内部的 ANN 加速。两个**都要做**, 不是替代关系。

**冷启动**: 新店用 metadata 映射到已有店 embedding 初始化 (content-based
bootstrap); Thompson sampling / UCB 给新店 impression 探索预算; 业务可加"新店
扶持"硬权重。

### Ranking Model + Feature Pipeline

Fine Ranker 选 **MMoE (Multi-gate Mixture-of-Experts)** 做多目标, bottom 用
**DIN**-style attention 处理用户行为序列。**MMoE vs MoE**: MoE 单目标, gate 路由
到 expert; MMoE 多目标, **每个 task 有自己的 gate**, expert 共享但 task-specific
加权 — 解决多任务相关性差时的 negative transfer。

| 类别 | 例子 |
|---|---|
| User 静态 | 画像、历史下单频率、客单价 |
| User 动态 | 最近 30 天点击/下单序列、最近 1h 行为 (near-line) |
| Item 静态 | 餐厅评分、菜系、价位、地理位置、历史 CTR/CVR |
| Item 动态 | 当前 busy、ETA、当日订单量、是否 surge |
| Context | 时段、星期几、天气、设备、location |
| Cross | user × cuisine 偏好、user × price-band 命中率 |

**Explore intent 不放进主 ranker** — 放 re-ranking 阶段做 diversity (MMR/DPP)
或 bandit, 混进主 ranking objective 容易让模型发散。
"""

_RESTAURANT_FORMULAS = r"""## 规模估算 (Back-of-Envelope) + 排序公式

### 流量

```
DAU            ~50M (全球)
请求/用户/天    ~1.2
平均 QPS        50M * 1.2 / 86400 ~= 700 QPS
峰值倍数        5-8x  <- 外卖是最 peaky 的产品 (lunch + dinner 双峰 + 时区叠加)
峰值 QPS        ~5K-10K
```

**洞察**: capacity planning 按 8x 峰值预留; 缓存要考虑 lunch/dinner 集中失效。

### 读写比

```
每次渲染 = 1 read + ~30 impression + 0-3 click + 0-1 order log
读写比 ~= 1:30+   <- 写远多于读
```

**洞察**: 不能按 read-heavy 设计, **logging pipeline 是核心组件**, 不是 nice-to-have。

### 候选漏斗规模

```
单用户可达餐厅 (3-5mi)  ~300-1000
Candidate generation    ~500-1000
Coarse ranking          ~100-200
Fine ranking            ~30-50
最终 feed               ~30
```

### 存储

| 类别 | 规模 |
|---|---|
| 餐厅 metadata | ~1M * 几 KB ~= 几 GB (在线 KV) |
| 餐厅 embedding | 1M * 256d f32 ~= 1GB (ANN index) |
| 用户 embedding | 200M * 1KB ~= 200GB (分热冷) |
| User-item interaction | TB 量级 (热 Cassandra / 冷 HDFS) |
| **训练数据日志** | **~TB / day — 真正的存储大头** |

**洞察**: **ML 系统的存储瓶颈是训练数据 pipeline, 不是 serving 数据** — 和普通
CRUD 系统最大的区别。

### 多目标融合 (multi-objective fusion)

$$\text{final\_score} = w_1 \cdot P(\text{click}) + w_2 \cdot P(\text{order}) + w_3 \cdot \log(\text{GMV}) - w_4 \cdot P(\text{cancel})$$

权重由业务调优, **PM 和算法 co-own**。
"""

_RESTAURANT_PROD_CONSTRAINTS = r"""## 生产约束

### Training-Serving Skew (最重要的工程问题)

> 训练-服务特征分布不一致是推荐系统最常见的线上 bug, 必须用**系统设计**而不是
> **纪律**来规避。三层防御:

**1. Feature Snapshot at Serving Time** — 不事后重算训练特征, 而在 serving 时把
模型实际看到的特征值原样 log 下来:

```
serving:  features = fetch_features(user, context)
          score = model.predict(features)
          log(request_id, features, score)   <- snapshot
training: join(serving_log, label_log_by_request_id)
          train on logged features (不重算)
```

这样 training/serving **物理上不可能 skew**; 代价是 logging 量大 (列式压缩 + 采样)。

**2. Feature Store (Single Source of Truth)** — Uber 内部叫 **Michelangelo
Palette**; offline 训练和 online serving 共享同一份 feature transformation 代码,
禁止两边各写各的。

**3. Feature Monitoring** — 每天比对 online vs offline feature 分布, KL divergence
/ PSI 报警。事前防御 + 事后监控两层。

### Graceful Degradation (在线 robustness)

- 每个 feature service 拉取设 50ms timeout, 超时用 default value 填充。
- **"是否 fallback" 本身作为一个 feature** 喂给模型。
- 训练时主动模拟 missing pattern (dropout 部分特征), 让模型在 fallback 下也合理。
- 极端情况整个 ranker 不可用 -> 降级到 popularity-based 兜底。

### Freshness / Availability (外卖独有)

> **Hard filter 处理"用户根本下不了单", Soft feature 处理"体验程度差异"。
> Model 学连续信号, policy 兜极端 outlier, 两层防御。**

| 信号 | 进入位置 | 处理 |
|---|---|---|
| 是否营业 / 接单 | Candidate gen 阶段 hard filter | 直接剔除 (避免 dead click) |
| ETA (30 vs 45min) | Ranking feature | Model 学习 |
| Surge / Busy | Ranking feature + Re-rank | Soft + 业务规则 |
| 极端 ETA (>2h) | Re-rank hard filter / 降级 | Policy 兜底 |
| Driver supply 紧张 | Ranking feature | Model 感知 |

**dead click 为何高优**: 推荐关门的店 -> 用户点进去下不了单 -> abandonment 直接
发生 -> 这一单可能流失到 DoorDash -> 直接打击 abandonment rate 和 GMV。
"""

_RESTAURANT_TRADEOFFS = r"""## 权衡取舍 (Trade-off, decision-by-decision)

每个架构决策都主动给两端:

| 决策 | 选项 A (简单) | 选项 B (复杂) | 何时选哪个 |
|---|---|---|---|
| 召回 merge | Unified ranking (统一打分) | Quota allocation (配额) | 冷启动选 B, 否则 A |
| 排序模型 | GBDT | MMoE + DIN | 数据 < 1B sample 用 A, 否则 B |
| ANN 部署 | 单一全局 index | Sharding (按城市) + IVF/HNSW | 生产必 sharding; IVF/HNSW 都要做 |
| Online learning | Daily/hourly batch retrain | Online learning | 主流 batch; 折中: embedding 在线 + ranker 离线 |
| Eval | A/B + holdout | Switchback / cluster-randomized | 单用户独立选 A; 有 supply 干扰选 B |

### Online Learning vs Batch Retraining

主流是 daily / hourly batch retrain。Online learning 风险高 (数据噪声直接进模型)。
折中: **embedding 在线更新 + ranker 离线训练**, 或 incremental fine-tune 每小时一次。

### Model + Policy 双层防御

| 场景 | Model 学的 | Policy 兜的 |
|---|---|---|
| Uber Eats 排序 | ETA / busy / surge soft feature | 是否营业 hard filter, ETA > 2h hard filter |

不是二选一: model 学连续信号, policy 兜极端 outlier。
"""

_RESTAURANT_DEFENSE = r"""## 应答策略 (Adversarial Defense)

### 收尾的 Senior 加分项 (时间充裕时主动抛)

**Position Bias**: 高位曝光 item 天然 CTR 高, 不修正会让模型学到 position 而非
相关性。解法: (1) position 作 feature 训练时输入, **serving 时统一置 0**
(position-as-feature, position-zero-at-serve); (2) **IPS (Inverse Propensity
Scoring)** 给低位样本更高权重, 从 loss 上 debias。

**Counterfactual / Off-Policy Eval**: 上线前用 OPE (IPS / DR / Switch / SNIPS)
估计新模型, 不能只看离线 AUC (AUC 高不代表线上 GMV 高)。**DR (Doubly Robust)**
是生产首选 — outcome model 和 propensity model 任一正确即 unbiased。

**A/B Testing + Cluster-Randomized**: Uber 内部叫 **XP**。推荐系统 A/B 在同城内有
**supply 干扰** (A 组抢了 B 组的 driver), 必要时做 **cluster-randomized /
switchback test** (按城市分组); 看 long-term retention 不只当次 CTR。

### Senior 信号速查 (不及格 vs Staff Golden)

| 维度 | 不及格 | Staff Golden |
|---|---|---|
| 行业黑话 | 概念对没用标准词 | **H3 / two-tower / MMoE / Michelangelo / feature snapshot / graceful degradation / position bias** |
| Training-serving skew | "靠 pipeline 纪律" | **Feature snapshot + Feature store + Monitoring** 三层, 系统兜底不靠人 |
| Online robustness | 默认 feature 必 ready | **Timeout + fallback + 模拟 missing 训练 + popularity 兜底** |
| Model vs Policy | 全交给 policy | **Model 学连续, policy 兜极端**, 两层 |
| 答题密度 | 频繁说"前面提过" | 即使重复也完整说出 reasoning chain |

### 三层防御模式 (事前 / 运行时 / 事后)

| 维度 | 事前 (build-time) | 运行时 (serve-time) | 事后 (monitor-time) |
|---|---|---|---|
| Train-serve skew | Feature store / Michelangelo | Feature snapshot 时 log | KL / PSI 监控 alarm |
| Robustness | 训练模拟 missing pattern | Timeout + fallback default | Latency / error rate 监控 |
| Bias / fairness | Per-segment quota | Re-rank diversity (MMR/DPP) | Per-segment stratified eval |

**话术**: 讲到有名词的概念先说名字再一句话解释 — "我会用 **two-tower model** —
user / item 各一个 tower 共享 embedding 空间, in-batch sampled softmax 训练,
serving 时 item tower 离线算好灌进 ANN, user tower 在线 inference。"
(术语名 + 结构 + 训练方式 + serving 方式 = staff level 密度)
"""

_RESTAURANT_VERBAL = r"""## 口述脉络 (Verbal Outline)

### 3-Minute 版本

这是 Uber Eats home feed 的个性化餐厅推荐。我会按真实面试推进: 先 3-5 分钟定
**需求 / scope / metrics** (重点 metric 是 abandonment rate — feed 失败的核心
信号), 然后 **back-of-envelope** (DAU 50M, peak QPS 5-10K 因为外卖最 peaky,
存储大头是 TB/day 训练日志, 读写比 1:30 写多于读)。

架构是经典 **多级漏斗**: candidate gen (H3 geo + two-tower ANN + inverted +
popular, 加 "is-open" hard filter 防 dead-click) -> coarse -> fine (MMoE + DIN
多目标) -> re-rank (MMR diversity + 极端 ETA filter)。三层时间尺度 (offline 天 /
near-line 秒 / online 毫秒) — near-line 不能省, 因为餐厅接单状态秒级变。

最重要的工程点是 **training-serving skew**: feature snapshot at serving +
Michelangelo feature store + KL/PSI 监控三层。

### 10-Minute 版本

在 3-min 骨架上展开:

**需求 (1.5min)**: functional / non-functional (P99<200ms, 99.95%, graceful
degradation) / out-of-scope / 两层 metrics (product CTR/CVR/abandonment +
business GMV/search-efficiency)。

**规模 (1.5min)**: 流量双峰 + 时区叠加 = 8x 峰值; 读写比 1:30 推出 logging 是核心
组件; 存储瓶颈是训练 pipeline 不是 serving。

**Deep dive — 召回 (2min)**: 多路召回表; H3 vs geohash (Uber 必答); two-tower
结构 + serving; unified vs quota merge; sharding vs IVF 区别; 冷启动
content-bootstrap + bandit。

**Deep dive — 排序 (2min)**: MMoE vs MoE; DIN 行为序列; 特征六分类; 多目标融合
公式; explore intent 放 re-rank 不放主 ranker。

**工程 + senior (3min)**: training-serving skew 三层防御; graceful degradation
(timeout + fallback + 模拟 missing); freshness hard/soft 双层; position bias
(zero-at-serve / IPS); OPE (DR 首选); cluster-randomized A/B (supply 干扰)。
"""

_RESTAURANT_CHEAT_SHEET = r"""## Uber Eats 餐厅推荐 · 一页纸记忆卡

> 面试前 5 分钟扫一眼。源: doc 85 §1.6 / §1.6.1。

```
开场:    Functional / Non-Functional / Out-of-Scope / Metrics
规模:    DAU 50M, QPS peak 5-10K (8x), candidate 300, feed 30
         存储大头: training log ~TB/day | 读写比 1:30+ (写多于读)

架构:    Client -> Gateway -> FeedService
         -> Context + FeatureStore + Availability
         -> Candidate Gen (H3 + Two-tower + Inverted + Popular)
            + Hard filter (open?)
         -> Coarse (GBDT/light 2-tower) -> 100
         -> Fine (MMoE + DIN, multi-task) -> 30
         -> Re-rank (MMR diversity + biz rules + extreme filter)
         -> Logging (Snapshot!) -> Streaming -> Offline -> 回灌

三层:    Offline (天) | Near-line (秒) | Online (ms)

关键词:  H3 (Uber!)  Two-tower  MMoE  DIN
         Feature Snapshot  Michelangelo
         Graceful Degradation (timeout + fallback)
         Hard filter dead-click + Soft feature ETA
         Model + Policy 双层
         Position bias  Off-policy eval (DR)  Cluster A/B
```

### 必说黑话 (会就要说)

| 类别 | 词 |
|---|---|
| 检索 | **H3** (Uber 开源 hexagon geo), **two-tower**, **HNSW / IVF** |
| 排序 | **MMoE** (多 gate 共享 expert), **DIN** (behavior-seq attention) |
| 工程 | **Michelangelo**, **feature snapshot**, **graceful degradation** |
| Senior | **position bias** (zero-at-serve / IPS), **OPE / DR**, **switchback** |

完整长篇见 canonical [doc 85 §1](cd://85)。
"""

# ---------------------------------------------------------------------------
# Row 2: Budget-Constrained Promo Recommendation (doc 85 section 2.x)
# ---------------------------------------------------------------------------

_PROMO_OVERVIEW = r"""## 题目 (Problem)

给定固定 promo budget (例如 **\$10M / 月**), 设计一个 ML 系统决定**给哪些用户发
什么 promo**, 目标是在 budget 约束下**最大化 incremental profit (增量利润)**。
目标 Level: **Staff (L6)**。

> 完整长篇叙述见 canonical 源文档 [Uber ML System Design Golden Answers](cd://85)
> (本页是其 section 2.x 的结构化投影 / structured projection)。

### TL;DR (30 秒版本)

这是一个 **uplift modeling × constrained optimization** 的复合问题:

- **ML 层**: 用 randomized experiment 数据训练 uplift model (T-learner /
  X-learner with XGBoost), 对每个 (user, promo) 预测 incremental profit
  $\tau(u, p)$。
- **优化层**: formulate 为 Multiple-Choice Knapsack (ILP), 用 **Lagrangian
  relaxation** 在 N=10M scale 下并行求解 — 每用户独立 argmax
  $\tau(u,p) - \lambda \cdot c(u,p)$, 外层对 shadow price $\lambda$ 做 binary search。
- **探索层**: uplift 输出上加 **contextual bandit / Thompson sampling**。
- **评估层**: offline 用 IPS / DR estimator, online 用 long-running holdout
  (永远不发 promo 的 control) 量 incremental profit。

### Problem Framing — The Incrementality Trap (核心陷阱)

最大化 **incremental profit**:

$$\text{Profit} = \text{take\_rate} \times \text{incremental\_GMV} - \text{promo\_cost}$$

关键词是 "incremental" — 只算 promo "带来的"额外 GMV。

| 用户 | 不发 | 发 \$5 off | 净影响 |
|---|---|---|---|
| A: 每周下单的活跃用户 | \$30 | \$30 (用了 promo) | **-\$5 (白送)** |
| B: dormant 用户 | \$0 | \$25 (用了 promo) | **+\$25** |

[WRONG] 预测 $P(\text{redeem})$ 或 post-treatment GMV 会**偏向用户 A** — 这是
**cannibalization** (蚕食自有 GMV)。

[RIGHT] 预测 **treatment effect / uplift** (因果效应):

$$\tau(u, p) = E[Y \mid \text{do}(T=p), X=u] - E[Y \mid \text{do}(T=0), X=u]$$

$\text{do}(\cdot)$ 是 Pearl 的 do-operator, 强调因果干预而非条件概率。

### Metrics

- **Winning**: incremental profit per dollar (**iROI**)。
- **Guardrail (不能动)**: Total GMV、retention 30d/90d、fraud rate、per-segment coverage。
- **Counter-metric (易忽略)**: cannibalization rate、redemption ≠ success、LTV impact。
"""

_PROMO_ARCHITECTURE = r"""## 系统架构

```
OFFLINE PIPELINE
  Raw logs (events, promos)
    -> Feature Store
    -> Uplift Model Training
    -> Model Registry
  Raw logs -> Holdout Eval (randomized control = ground truth)
  Model    -> Lagrange Solver -> lambda*
                                   |
                                   v
ONLINE PIPELINE
  User opens app
    -> Feature Lookup
    -> Uplift Inference
    -> Argmax_j (tau[i,j] - lambda* * cost[i,j])  -> return promo
    -> Bandit Explore (exploration bonus)
    -> Budget Pacer (PID) -- 动态调 lambda
    -> Event log -> 回到 Raw logs (closing the loop)
```

**关键 split**: 离线用 historical data + Lagrangian 解出 shadow price
$\lambda^*$; online serving 时每个用户独立算 argmax, 用同一个 $\lambda^*$; budget
pacer 监控实际花费并动态调 $\lambda$。Bandit 与 Lagrangian **正交可组合**:
bandit 决定探索哪些 (user, promo), Lagrangian 决定 budget 下怎么分配。
"""

_PROMO_DATAFLOW = r"""## Clarifying Questions + ML 层 (Uplift Modeling)

### Clarifying Questions (先问再设计)

**Business**: winning metric 是 redemption / incremental GMV / incremental
profit? profit 定义? 时间窗口 (7d/4w/LTV)? 关注哪些 segment? 有 fairness /
per-segment quota 吗?

**Data**: promo catalog 多少种 (决定 K)? 每用户 cooldown? **历史数据有
randomized hold-out 吗 (决定能不能做 causal inference)**? budget 是
daily/weekly/monthly (要不要 pacing)? real-time 还是 batch?

**Operational**: fraud 在 ML 层还是 rule layer? 部署频率? cold-start 用户怎么办?

### Uplift Modeling — 数据要求 (最重要)

Causal inference 的前提是 unbiased treatment assignment:

- 必须有 **randomized hold-out group**: 随机选一部分用户不发 promo 作 ground-truth control。
- 或用 **IPTW (Inverse Propensity Weighting)** 调整 observational data (需 propensity 准确)。
- **没有 randomization 就不要做 uplift modeling** — 会被 selection bias 杀死。

### Meta-learner 框架

| Method | 思路 | 何时用 |
|---|---|---|
| **S-learner** | 单模型, treatment 作 feature $f(X,T)$ | 简单 / treatment 连续 |
| **T-learner** | 训 $f_1(X)$ 和 $f_0(X)$ 算差 | treatment/control 数据都充足 |
| **X-learner** | T-learner + propensity 加权交叉修正 | treatment imbalance 严重 |
| **DR-learner** | Doubly robust, 结合 outcome + propensity | 想 robust to misspec |
| **Causal Forest** | 直接优化 heterogeneous TE | 中等数据 + 要 uncertainty |

**工业界第一版几乎都是: T-learner with XGBoost / LightGBM**。

**Multi-Treatment (K=10 不是 binary)**: (1) Multi-T-learner — 每种 promo 一个
outcome model + control, K+1 个; (2) S-learner with promo as feature — 单模型,
promo 作 categorical。后者数据效率高, 前者更灵活。

**Features**: User (tenure / lifetime orders / AOV / days-since-last / segment),
Promo (discount type/magnitude/expiry), Context (DoW / time / weather / events),
Interaction (past redemption), Cross (user × promo embedding)。

**Calibration**: predicted $\tau$ 必须 well-calibrated (不只关心排序), 因为优化层
要用绝对值算 budget。用 **isotonic regression** / **Platt scaling** 在 hold-out
上 calibrate; 监控 calibration plot (predicted vs actual lift by decile)。
"""

_PROMO_FORMULAS = r"""## 公式: ILP + Lagrangian + Pacing

### ILP Formulation (Multiple-Choice Knapsack)

决策变量 $x_{i,j} \in \{0,1\}$, $i \in$ users, $j \in \{0,1,\ldots,K\}$
($j=0$ = 不发):

$$\text{maximize} \quad \sum_i \sum_j \hat{\tau}_{i,j} \cdot x_{i,j}$$

约束:

$$\sum_j x_{i,j} = 1 \;\; \forall i \qquad \sum_i \sum_j c_{i,j} \cdot x_{i,j} \leq B$$

这是 **MCKP**, NP-hard, 但有特殊结构。

### Lagrangian Relaxation (生产标配)

把 budget 约束吸收进目标, 问题完全 decouple。引入 $\lambda \geq 0$:

$$L(x, \lambda) = \sum_i \left[ \max_j (\hat{\tau}_{i,j} - \lambda \cdot c_{i,j}) \right] + \lambda B$$

**结论**: 每个用户**独立**挑能让 $\hat{\tau}_{i,j} - \lambda c_{i,j}$ 最大的
promo。10M 用户完全并行, 每用户 $O(K)$, 总 $O(NK) \approx 10^8$ ops 秒级完成;
外层只对一个标量 $\lambda$ 做 binary search。$\lambda$ 是 budget 的 **shadow
price** (多花 \$1 budget 的边际 profit)。

```python
import numpy as np

def lagrangian_solve(uplift, cost, B, tol=1e-3):
    # Binary-search shadow price lambda so total spend matches budget B.
    # uplift, cost: (N, K) arrays. Returns (N,) chosen promo indices.
    N = uplift.shape[0]
    lo, hi = 0.0, float((uplift / np.maximum(cost, 1e-9)).max())
    while hi - lo > tol:
        lam = (lo + hi) / 2
        score = uplift - lam * cost          # each user: argmax_j
        choice = score.argmax(axis=1)
        spent = cost[np.arange(N), choice].sum()
        if spent > B:
            lo = lam   # too expensive -> raise penalty
        else:
            hi = lam   # slack remains -> lower penalty
    return choice
```

### LP Relaxation 对比

放松 $x \in [0,1]$ 变 LP, 多项式可解。MCKP 的 LP relaxation 最优解里**最多一个
fractional variable**, 简单 round 损失极小。**何时 LP**: 要精确近似; **何时
Lagrangian**: 要 scale + online (生产首选)。

### Budget Pacing (PID Controller)

Budget 是月预算, greedy 第一周花光不行。用 PID 控制 $\lambda$:

$$\lambda(t+1) = \lambda(t) + K_p \cdot e(t) + K_i \cdot \textstyle\int e + K_d \cdot \frac{de}{dt}, \quad e(t) = \text{expected\_spent} - \text{actual\_spent}$$

花太快 $e<0$ 抬高 $\lambda$ (模型变挑剔); 花太慢 $e>0$ 降低 $\lambda$ (变激进)。
Uber / Lyft / DoorDash 都用类似机制。

### Bandit 与 Lagrangian 组合

$$\text{final\_score}_{i,j} = (\hat{\tau}_{i,j} + \text{exploration\_bonus}_{i,j}) - \lambda \cdot c_{i,j}$$
"""

_PROMO_PROD_CONSTRAINTS = r"""## 生产约束

### Non-functional

| 维度 | 要求 |
|---|---|
| Scale | N=10M 用户 × K=10 promo, 每日决策 |
| Latency | Batch: <2h; Online API: P99 < 200ms |
| Budget compliance | 月底 actual $\leq B$ 且 $\lvert \text{actual}-\text{target} \rvert / \text{target} < 5\%$ |
| Model freshness | Retrain $\geq$ weekly |
| Reliability | 99.9% uptime; graceful degradation to rule-based fallback |

### Online Allocation

Batch 解法假设事先知道所有用户, 但 promo 触发是 real-time (打开 app / 即将取消
订单)。生产做法: (1) 离线用 historical + Lagrangian 算 $\lambda^*$; (2) online
每用户独立算 $\arg\max_j (\hat{\tau}_{i,j} - \lambda^* c_{i,j})$; (3) 监控实际
花费, 必要时动态调 $\lambda$。

### Greedy & Approximation (何时够用)

**Bang-per-buck greedy** (按 $\hat{\tau}/c$ 降序): **pure greedy 没有常数近似比**
(反例: A(2,1) / B(100,100), budget=100, greedy 选 A 后 B 装不下)。**Modified
greedy** = $\max(\text{greedy}, \text{best\_single})$ 是 1/2-approximation。
FPTAS 可做 $(1-\epsilon)$ 但实际不用 (Lagrangian 够好)。**何时 greedy 够**:
budget 不 binding 时 (钱够发给所有 positive-uplift)。

### Common Pitfalls 速查

| Pitfall | 表现 | 解法 |
|---|---|---|
| **Cannibalization** | 给本会下单的用户发 | 用 uplift 不是 $P(\text{redeem})$ |
| **Selection bias** | 历史 promo 非随机 | 必须 randomized holdout |
| **Calibration drift** | predicted vs 实际差很多 | isotonic + 监控 |
| **Budget pacing fail** | 月初花光 / 月末花不掉 | PID on $\lambda$ |
| **Cold start** | 新用户无 features | fallback 到 segment-level policy |
| **Fraud** | 专门刷 promo | rule layer + fraud model 在 ML 之前 |
| **Network effects** | 用户互相分享 code | switchback / cluster A/B |
| **Long-term harm** | 惯坏用户 organic 下降 | 90d retention guardrail |
"""

_PROMO_TRADEOFFS = r"""## 权衡取舍 (Trade-off, decision-by-decision)

| 决策 | 选项 A (简单) | 选项 B (复杂) | 何时选哪个 |
|---|---|---|---|
| Treatment 维度 | Binary / Multi-T-learner | S-learner (promo as feature) | K $\leq$ 3 选 multi-T, K $\geq$ 5 选 S |
| 优化求解 | LP relaxation (精确) | Lagrangian (scale) | N $\leq$ 100K 选 LP, 生产选 Lagrangian |
| 近似 | Modified greedy (1/2) | FPTAS ($1-\epsilon$) | 实际都用 Lagrangian, 上面两个少用 |
| Bandit | $\epsilon$-greedy | Thompson Sampling | Day 1 选 A, 模型成熟选 B |
| Eval | A/B + long-running holdout | Switchback / cluster | 单用户独立 A, 有 spillover B |

### Bandit: Per-User vs Contextual

[WRONG] **Per-user bandit** 不可行: cold start 新用户没 prior; $N \times K$ 个
posterior 参数爆炸; 大部分用户一辈子见 1-2 次 promo 更新不充分。

[RIGHT] **Contextual bandit** (主流): 全局共享 policy, 用户 features 作 context。
LinUCB / Neural LinUCB / Thompson Sampling on uplift posterior。引入节奏: Day 1
$\epsilon$-greedy (5% 随机) -> Phase 2 Thompson (新 promo 频繁上线) -> Phase 3
full RL (决策序列性强 + long-term reward)。

### Model + Policy 双层防御

| 场景 | Model 学的 | Policy 兜的 |
|---|---|---|
| Promo 分配 | Uplift $\hat{\tau}(u,p)$ continuous | fraud rule, per-segment lower bound, cool-down |
"""

_PROMO_DEFENSE = r"""## 应答策略 (Adversarial Defense) — 评估策略为重

### Offline Evaluation / Backtesting (OPE 工具箱)

问题: log data 是 old policy 生成的, 怎么评估 new policy?

**IPS (Inverse Propensity Scoring)**:

$$\hat{V}_{\text{IPS}} = \frac{1}{N} \sum_i \frac{\pi_{\text{new}}(a_i \mid x_i)}{\pi_{\text{old}}(a_i \mid x_i)} \cdot r_i$$

unbiased 但 variance 高 (propensity 接近 0 时爆炸)。

**Doubly Robust (DR)** — **生产首选**:

$$\hat{V}_{\text{DR}} = \frac{1}{N} \sum_i \left[ \hat{q}(x_i, \pi_{\text{new}}) + \frac{\pi_{\text{new}}}{\pi_{\text{old}}} (r_i - \hat{q}(x_i, a_i)) \right]$$

outcome model $\hat{q}$ 或 propensity 任一正确即 unbiased。

**Switch / SNIPS**: Switch 在 importance weight 太大时切到 model-based 控 variance;
SNIPS (Self-Normalized IPS) 除以 weight 之和更稳定。**Counterfactual replay**:
新 policy 在 logged action 上不变的样本可直接复用。

**Backtest checklist**: [DO] holdout 做 ground-truth anchor; 比较多 estimator
(IPS/DR/Switch) 看是否一致; stratified by segment; 检查 propensity overlap。
[DON'T] 不要只看 "predicted profit" (model 自己的输出, 循环论证)。

### Online A/B Testing

**Long-running Holdout (生产关键)**: **永远**留 1-5% 流量完全不发 promo — 是
organic GMV baseline + uplift 训练数据来源 + causal anchor。

> [WARNING] 没有 long-running holdout, 整个 uplift modeling 就是空中楼阁。这是
> **infra 投资**不是 ML 决策。

**Switchback / Cluster-randomized**: promo 有网络效应 (用户互相推荐) 时单用户随机
会 spillover。用 city-level switchback (整城轮流 on/off) 或 cluster-randomized
(社交网络聚类后整簇分配)。

### 必说黑话

因果: **uplift / CATE / ITE / IPTW / propensity**。优化: **MCKP / Lagrangian /
shadow price / PID pacing**。评估: **IPS / DR / Switch / SNIPS / switchback**。
"""

_PROMO_VERBAL = r"""## 口述脉络 (Verbal Outline)

### 3-Minute 版本

这是 budget-constrained promo 分配, 本质是 **uplift modeling × constrained
optimization** 的复合题。我会先 frame: 目标是 **incremental profit** 不是
redemption rate — 否则掉进 incrementality trap, 把钱白送给反正会下单的用户
(cannibalization)。

ML 层用 **uplift model** (T-learner with XGBoost 起步) 对每个 (user, promo) 预测
$\tau$; 前提是有 **randomized holdout** 数据。优化层 formulate 成 **MCKP**, 用
**Lagrangian relaxation** 把 budget 约束吸收进目标, decouple 成每用户独立 argmax,
外层 binary search 一个 shadow price $\lambda$ — 10M 用户秒级并行。

评估靠 offline **DR estimator** + online **long-running holdout** (永久 control)。
Budget pacing 用 **PID** 动态调 $\lambda$ 防月初花光。

### 10-Minute 版本

**Framing (1.5min)**: incrementality trap (两用户表格); uplift 的因果定义
(do-operator); winning metric iROI + guardrail + counter-metric。

**Clarifying (1min)**: 最关键一问 — 有没有 randomized holdout (决定能否 causal)。

**ML 层 (2.5min)**: 数据要求 (randomization / IPTW); meta-learner 表 (S/T/X/DR/
Causal Forest, 工业界 T-learner+XGBoost 起步); multi-treatment (K=10) 两种处理;
calibration 必须 (优化层用绝对值)。

**优化层 (2.5min)**: ILP formulation (变量/目标/约束); Lagrangian decouple 推导
+ shadow price 直觉; LP relaxation 对比 (最多一个 fractional); greedy 近似比反例;
PID budget pacing。

**探索 + 评估 (2.5min)**: contextual bandit (不是 per-user) + 与 Lagrangian
正交组合; OPE 工具箱 (IPS variance 高 / DR 首选 / Switch / SNIPS); long-running
holdout 是 infra 投资; switchback 解 spillover。
"""

_PROMO_CHEAT_SHEET = r"""## Budget-Constrained Promo · 一页纸记忆卡

> 面试前 5 分钟扫一眼。源: doc 85 §2.11。时间紧至少 cover 这 7 件事:

```
1. Frame 成 incremental profit 最大化   (不是 redemption rate)
2. Uplift / causal inference 是核心      (不是普通 supervised)
3. 写出 ILP formulation                  (决策变量 / 目标 / 约束)
4. Lagrangian decomposition 是 scale 解法 (decouple 到独立 user argmax)
5. Long-running holdout + OPE             (DR estimator 加分)
6. Budget pacing                         (PID / shadow price 动态调)
7. Contextual bandit                     (不是 per-user bandit)
```

### 核心公式速记

```
Profit    = take_rate * incremental_GMV - promo_cost
Uplift    tau(u,p) = E[Y|do(T=p),X] - E[Y|do(T=0),X]
Lagrangian 每用户 argmax_j ( tau[i,j] - lambda * cost[i,j] )
          外层 binary-search lambda (shadow price) 使总花费 ~= B
DR        生产首选 OPE; outcome 或 propensity 任一对即 unbiased
```

### 避免的 anti-patterns

- 一上来就谈 model (XGBoost/DNN) — 应先 frame。
- 谈 model 不谈 causal — 直接挂。
- 优化层只说 "用 LP 解" 不展开 — 体现不出对 scale 的理解。
- 不提 evaluation — senior 必扣分。
- 把 "redemption rate" 当 winning metric — 暴露不懂业务。

### 必说黑话

**uplift / CATE / ITE**, **MCKP / Lagrangian / shadow price**, **PID pacing**,
**IPS / DR / Switch / SNIPS**, **long-running holdout**, **contextual bandit**,
**switchback**。

完整长篇见 canonical [doc 85 §2](cd://85)。
"""

# ---------------------------------------------------------------------------
# Module definitions
# ---------------------------------------------------------------------------

# Content section keys, including cheat_sheet (the existing seed_system_designs.py
# omits cheat_sheet from its content_keys; this seed includes it since both rows
# author a one-pager).
_CONTENT_KEYS = [
    "overview",
    "architecture",
    "dataflow",
    "formulas",
    "production_constraints",
    "tradeoffs",
    "defense",
    "verbal_outline",
    "cheat_sheet",
]

MODULES: list[dict[str, object]] = [
    {
        "slug": "uber-eats-restaurant-rec",
        "title": "Uber Eats 餐厅推荐系统 (Restaurant Recommendation)",
        "subtitle": (
            "Staff-level golden answer: home feed 个性化餐厅推荐 — 多级漏斗 "
            "(H3 + two-tower + MMoE) + training-serving skew 三层防御 + "
            "freshness hard/soft 双层"
        ),
        "diagram_filename": None,
        "display_order": 400,
        "overview": _RESTAURANT_OVERVIEW,
        "architecture": _RESTAURANT_ARCHITECTURE,
        "dataflow": _RESTAURANT_DATAFLOW,
        "formulas": _RESTAURANT_FORMULAS,
        "production_constraints": _RESTAURANT_PROD_CONSTRAINTS,
        "tradeoffs": _RESTAURANT_TRADEOFFS,
        "defense": _RESTAURANT_DEFENSE,
        "verbal_outline": _RESTAURANT_VERBAL,
        "cheat_sheet": _RESTAURANT_CHEAT_SHEET,
    },
    {
        "slug": "uber-budget-promo-rec",
        "title": "Budget-Constrained Promo Recommendation (uplift x Lagrangian)",
        "subtitle": (
            "Staff-level golden answer: 固定 budget 下最大化 incremental profit "
            "— uplift modeling (causal) + Multiple-Choice Knapsack / Lagrangian "
            "relaxation + contextual bandit + DR off-policy eval"
        ),
        "diagram_filename": None,
        "display_order": 401,
        "overview": _PROMO_OVERVIEW,
        "architecture": _PROMO_ARCHITECTURE,
        "dataflow": _PROMO_DATAFLOW,
        "formulas": _PROMO_FORMULAS,
        "production_constraints": _PROMO_PROD_CONSTRAINTS,
        "tradeoffs": _PROMO_TRADEOFFS,
        "defense": _PROMO_DEFENSE,
        "verbal_outline": _PROMO_VERBAL,
        "cheat_sheet": _PROMO_CHEAT_SHEET,
    },
]


def seed_uber_system_designs() -> dict[str, int]:
    """Insert or update the two Uber system design modules.

    Idempotent: upserts by slug. On an existing row, refreshes title/subtitle/
    diagram/display_order and every content section (incl. cheat_sheet).

    Returns:
        Dict with counts of inserted and updated records.
    """
    init_db()
    db = SessionLocal()
    inserted = 0
    updated = 0

    try:
        for data in MODULES:
            existing = (
                db.query(SystemDesign)
                .filter(SystemDesign.slug == data["slug"])
                .first()
            )
            if existing:
                existing.title = data["title"]
                existing.subtitle = data["subtitle"]
                existing.diagram_filename = data["diagram_filename"]
                existing.display_order = data["display_order"]
                for key in _CONTENT_KEYS:
                    if key in data:
                        setattr(existing, key, data[key])
                updated += 1
            else:
                kwargs: dict[str, object] = {
                    "slug": data["slug"],
                    "title": data["title"],
                    "subtitle": data["subtitle"],
                    "diagram_filename": data["diagram_filename"],
                    "display_order": data["display_order"],
                }
                for key in _CONTENT_KEYS:
                    if key in data:
                        kwargs[key] = data[key]
                db.add(SystemDesign(**kwargs))
                inserted += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {"inserted": inserted, "updated": updated}


if __name__ == "__main__":
    result = seed_uber_system_designs()
    print(
        f"Seed complete: {result['inserted']} inserted, "
        f"{result['updated']} updated."
    )
