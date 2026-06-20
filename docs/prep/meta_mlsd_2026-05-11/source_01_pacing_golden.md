
节奏把控建议（45min 假设）
我会推荐这个时间分配作为 golden template：

节奏上的具体调整
基于上面的分析，给你一个更新的 timing 建议，注意我把"strong moment 时刻"显式标出来了：

0-3 min：Framing（独裁式，60秒说完一个 proposal，30秒确认）
3-5 min：* Strong moment #1: 指出 problem 的 unique twist（"the core decision here is X, not Y"）
5-12 min：Data & labels（中等深度，重点 surface 1 个 bias 问题）
12-15 min：* Strong moment #2: 一个 sophisticated label 或 bias 洞察
15-25 min：Model（two-stage，主动问面试官想 deep dive 哪边）
25-28 min：* Strong moment #3: 一个 production scar 或量化直觉
28-35 min：Evaluation（offline + online + counterfactual）
35-40 min：* Strong moment #4: zoom-out summary + top 3 risks
40-45 min：Serving / monitoring（轻描淡写）+ Q&A





这里有几个 Meta 特别在乎的点，你要主动 surface：

Multi-objective / multi-task：notification 不只是 CTR，要考虑 long-term engagement、unsubscribe rate、user fatigue
Negative feedback / user fatigue modeling：Meta 在 notification 这块踩过坑，对 send-or-not gating 很敏感
Counterfactual evaluation：因为有 exposure bias，IPS / off-policy evaluation 是加分项
Calibration：跨 surface（email/push/in-app）混排需要概率校准

关于"减少沟通澄清"的取舍
你的直觉对了一半。减少澄清的"广度"是对的，但不要减少澄清的"深度"。区别是：

[FAIL] 不要再 triage email/push/in-app/portal 这种 surface 维度
[FAIL] 不要展开 FR/NFR/QPS/availability
[DONE] 要快速锁定一句话假设："I'll assume we're optimizing for in-app notification ranking with a daily candidate pool of ~1000 per user, latency budget ~200ms"——说完就往下走，不等面试官反复确认
[DONE] 要在每个 ML 决策点 surface trade-off，但自己给出推荐答案，不要把选择权抛回去

面试官说 "on track" 但给了"加面"的 feedback——我的解读是：方向对，但深度和决断力不够。你被自己的澄清习惯拖慢了，没来得及展示 ML 深度。这次要"快速 frame、自信决策、深入 ML 内核"。
Golden example 的构造
我建议你自己准备一个 canonical 题目（比如就用 push notification ranking 或 feed ranking），把它打磨成 25-30 分钟能完整走完的版本，然后真题来了套用 + 局部调整。Meta 常见题型其实就那么几个：feed ranking、ads ranking、notification、friend recommendation、reels recommendation、harmful content detection。底层框架高度复用。



"Unambiguous strong signal" 长什么样
Meta 面试官写 feedback 时会找具体的 "moment"。他们不会写"候选人整体不错"，会写"candidate showed strong ML depth when discussing X"。所以你要在面试中主动制造这种 moment。
几个高 ROI 的 moment 类型：
1. 一个出乎意料的 trade-off 洞察
比如讨论 label 时，主动说："One non-obvious issue here is that using click as label creates a feedback loop with our retrieval—items we show more get more clicks, which reinforces showing them. I'd want to add a small fraction of randomized exposure or use IPS weighting to break this."
这种话面试官一听就会在 feedback 里写"showed sophisticated thinking on exposure bias"。
2. 一个量化的直觉
不是"this model is faster"，而是"a two-tower with 128-dim embeddings can do ~10k candidate scoring in single-digit ms on CPU, which fits our latency budget; a cross-encoder would be 100x slower so we reserve it for top-100 reranking"。
数字让你显得 senior。即使数字不精确，方向对就行。
3. 一个 production scar
"In my eBay work, we found that adding more features beyond ~200 actually hurt because the model overfit to training distribution shifts. So I'd start with a focused feature set and validate freshness/coverage before expanding."
这种话只有真做过的人能说，面试官 calibrate 你的 level 时会立刻 +1。
4. 一个 framework-level 的总结
中段结束时主动说："Let me zoom out for a sec—we've covered retrieval, ranking, and labels. The three biggest risks I see in this design are: (1) cold start for new notification types, (2) calibration across surfaces if we mix push and in-app, (3) long-term fatigue not captured in our offline metric. I'd want to address these in order—want me to go deeper on any?"
这个动作 同时展示了 system thinking 和 communication，是 E5 signal。

举个例子，notification ranking 和 feed ranking 的最大区别是什么？

Feed 是 pull-based，user 主动来，所以 ranking 就是 ranking
Notification 是 push-based，最重要的决策不是 rank，是 send-or-not

如果你上次面试没强调这个"send-or-not gating layer 是 notification 区别于通用 ranking 的核心"，那就是错过了一个 strong moment 的机会。下次（无论什么题）都要找到这个 "this problem's unique twist"，然后围绕它组织你的 design。



E4 级别能被识别为 strong 的 ML moment 长这样：

Label design 的 nuance：positive/negative 怎么定义、delayed feedback 怎么处理、implicit vs explicit、label leakage 风险
Feature 的 ML 视角（不是 infra 视角）：static vs dynamic、user-side vs item-side、cross feature、feature staleness 对模型的影响、embedding 的 cold start
Modeling 的迭代路径：从 logistic regression baseline → GBDT → two-tower → DLRM 这样的演进，每一步解决什么问题、引入什么 cost
Evaluation 的多层次：offline AUC/NDCG → counterfactual / replay → online A/B → long-term holdout
Trade-off articulation：每个决策点说出"我选 A 因为 X，代价是 Y，如果 Z 变化我会切到 B"



"feature 是放在 indexing 里还是 separate service""I'd separate retrieval features from ranking features—retrieval needs to be in the index for sub-ms lookup, so we're limited to lightweight signals there. Ranking can pull richer features async. This shapes what kind of model we can use at each stage."
"logging 和 training 高度耦合，write 量很大""One thing I want to flag for training data: we need to log not just clicks but also impressions and the features at serving time, because training-serving skew is a real risk. The logging volume is non-trivial—if storage becomes a constraint, I'd sample negatives rather than reduce features."
"read/write ratio 在 recall + feature expansion 下不简单""The fan-out from query to candidates to scored items affects our feature freshness strategy—if we expand 1 query to 10k candidates, we can't afford fresh features per candidate, so I'd use precomputed item embeddings and only compute fresh features for the user side."
"distributed aggregator 和 node 同步""For ranking with a deep model, I'd actually keep scoring on one node per request rather than distribute—the network cost of feature shipping usually outweighs the compute savings. This is a lesson I learned at eBay."


E4 必须做到的：

Pick a reasonable model and justify with clear trade-offs
Identify the top 2-3 risks in the design
Show production sense (data freshness, monitoring, rollback)
Drive the conversation forward without getting stuck




═══ FRAMING (first 5 min) ═══
- Declarative open: "I'll frame this as X with two intrinsic specialties..."
- 2 twists (NOT 4), each 45-60s, with why/what/trade-off
- End: "I'm choosing not to deep-dive on [X, Y] but flag as risks"
- Confirm with yes/no question

═══ MENTAL RULES throughout ═══
1. List 3 bullets → immediately pick 1 to expand 60s
2. When I say "let me think out loud" → buy 1s, then deliver
3. Each major decision: state choice + 1 trade-off + production scar
4. When interviewer looks puzzled → "let me park that, more important is..."
5. ML-native terms only. NO: SLA, NFR, FR, QPS, read/write ratio,
   service, API, cache, network.
   YES: model class, label, feature, bias, objective, evaluation,
   freshness, drift, calibration

═══ 4 STRONG MOMENTS (pre-allocate) ═══
1. Multi-modal lifecycle (framing): pretrained backbone + fine-tune
   + upload-time compute + quarterly refresh + cost decoupling
2. Label schema (data section): multi-head (watch ratio, strong+,
   early-skip), duration confounder, ambiguous middle
3. Exposure bias reframe (bias section): data acquisition policy,
   onboarding + re-exploration + content cold-start ramp,
   failure modes, "different lever than IPS"
4. Zoom-out summary (35-40 min): top 3 risks, 1 long-term failure mode

═══ TIMING ═══
0-5    Framing
5-12   Data & labels  ← strong moment #2
12-18  Features
18-25  Model (ask interviewer which side to deepen)
25-30  Bias / objective  ← strong moment #3
30-37  Evaluation
37-42  Zoom-out + risks  ← strong moment #4
42-45  Serving (light) + Q&A

═══ IF YOU FEEL YOU'RE DRIFTING ═══
- to generic SD → "let me return to the ML core"
- to too many topics → "let me prioritize the top 2"
- to one-liner mode → "let me go deeper on this"

═══ E4 NOT E5 ═══
- Don't invent novel methods
- Don't over-scope ("2 years out we'd...")
- DO: confident execution of standard playbook + 1-2 deeper insights



Golden Example: Reels Home Feed Recommendation (E4 MLE, Meta-style 45 min)
下面这份是你明天可以直接 plug-in 的参考。我会标注时间锚点、关键台词、和4 个 strong moment 的精确投放位置。所有内容都是 canonical 形态——也就是说，你今晚把它读熟、internalize 关键句式，明天遇到任何 recommendation 类题目（Reels / Feed / Notification / Friend rec）都可以复用 80% 的结构。

整体节奏哲学
前 5 分钟独裁式 framing → 中段 30 分钟你主导但邀请面试官选方向 → 最后 10 分钟主动 zoom-out + 邀请 deep dive
4 个 strong moment 预先分配到固定位置——不要临场决定。
ML-native vocabulary only——下意识审查每一句话，infra 词汇（SLA / QPS / cache / service / read-write ratio）只在面试官主动问 serving 时才出现。

时间表
0-5 min    Framing                          ← Strong Moment #1
5-12 min   Data & Labels                    ← Strong Moment #2
12-18 min  Features
18-26 min  Model architecture
26-32 min  Bias & objectives                ← Strong Moment #3
32-38 min  Evaluation
38-42 min  Zoom-out + top risks             ← Strong Moment #4
42-45 min  Serving (light) + Q&A

0-5 min · Framing
你的开场（60-90 秒，declarative）

"I'll frame this as a recommendation system for Reels in the home feed, with retrieval plus ranking as the core structure. There are two intrinsic specialties of this problem that will drive most of my design decisions, and I want to put them on the table upfront.
First, Reels are short-form videos, which means content understanding cannot rely on metadata or text alone. Most Reels are UGC with minimal text, and trends are visual or audio-driven. So I'd compute multimodal embeddings—a pretrained video encoder for visual frames, an audio encoder for soundtracks, and a text encoder for any captions—fused into a single content embedding computed once at upload time. I'd start with pretrained backbones and fine-tune on a Reels-specific contrastive objective, where co-engaged videos are positives. The embedding gets refreshed only when we improve the encoder, roughly quarterly. This decouples content understanding cost from serving cost.
Second, Reels consumption is session-based and continuous. Unlike a structured feed where a user picks one item, Reels users consume tens of videos sequentially in a single session. This creates within-session dynamics—diversity collapse, fatigue, interest drift—that we have to model explicitly. The implication is that we need within-session features computed at request time, not just batch user profiles, and our ranking model needs to be session-aware not just user-aware.
I'm choosing not to deep-dive on cold-start, content moderation, or multi-resolution storage for now, but I'll flag them as risks later.
Does this framing make sense, or is there a different angle you'd like me to anchor on?"

* Strong Moment #1 = 上面的 "First" 段
为什么 strong: pretrained + fine-tune + upload-time compute + quarterly refresh + decoupling。每一句话都是 production-aware ML decision，不是 buzzword。
关键句式

"I'll frame this as X with two intrinsic specialties..."
"I'm choosing not to deep-dive on [X, Y]..."
"Does this make sense, or is there a different angle..."

[FAIL] 不要说的话

"Let me clarify the requirements" / "What's the QPS?" / "What's the latency budget?" / "Which surface—mobile or web?"
"I'm going to follow a standard recommendation pipeline..."（cookbook 语言）


5-12 min · Data & Labels
你的展开（4-5 分钟）

"Let me walk through this in three parts: data sources, label schema, and biases. I'll start with labels since they're the most non-trivial for Reels.
Data sources: We have impression logs (what we showed), engagement logs (watch time, likes, comments, shares, follows, swipe events), and content metadata (uploader, duration, embeddings, hashtags). We also have user-side data: long-term profile, recent session history, and demographic features where available.
Label schema — and this is where Reels diverges from standard ranking problems. I'd argue against a single binary label, in favor of multiple labels feeding multi-task heads:"

* Strong Moment #2 starts here (60-90 秒)

"Label 1: normalized watch ratio, defined as watch_time divided by video_duration, capped at 1.0. Critical to normalize—raw watch time would systematically over-weight long content. A 3-second video watched fully should count as much as a 60-second video watched fully.
Label 2: strong positive (binary)—explicit engagement like, comment, share, follow, save. Sparse but high-precision.
Label 3: strong negative (binary)—early swipe-away, defined as user swiping within the first 2-3 seconds or before 20% completion. This is the implicit hard-negative signal that's unique to Reels and crucial for breaking exposure bias in negative sampling.
Important nuance: the ambiguous middle. A user who watches 50% then swipes is genuinely ambiguous—not a hard negative, not a strong positive. I'd treat it as weakly positive on the watch-ratio head and exclude it entirely from the early-skip head. Forcing a binary label on ambiguous data adds noise.
One thing I want to flag: video duration is a confounder for almost every engagement label. A 5-second loop is much easier to complete than a 60-second clip. So duration becomes both a feature input and an evaluation slice—we should be looking at metrics conditioned on duration buckets, not just aggregate."

Strong Moment #2 ends. 然后过渡：

"I'll come back to biases in a moment when we discuss exploration—but at the data layer, the dominant risk is that all our labels are conditioned on what we chose to show. Let me hold that thought and move to features unless you want to deepen labels first."

关键 verbal patterns

"Let me walk through this in N parts: A, B, C"
"And this is where Reels diverges..."
"One thing I want to flag: [a non-obvious risk]"
"Let me hold that thought and move to X unless you want to deepen Y first"


12-18 min · Features
简洁展开（3-4 分钟，不是 strong moment 区，节奏要快）

"Features fall into four buckets:

User features: long-term profile (embedding learned from past engagement), demographic, recent topic exposure (last N sessions)
Content features: the multimodal embedding I mentioned, uploader features, duration, recency, historical engagement statistics
Context features: time of day, device, network type, session position (how many Reels in this session so far)
Cross features: user-content historical interaction (has user followed uploader? engaged with similar content recently?)

The non-trivial design choice here is session-context features—things like 'topic exposure in the last 5 items in this session', 'average watch ratio so far this session', 'swipe rate this session'. These have to be computed at request time, not pre-aggregated. They're the main lever for handling within-session fatigue and drift.
One trade-off: fresh user features versus stale precomputed features. For Reels I'd compute user-side features fresh at request, but content-side features can be precomputed and cached—content state changes slower than user state."

关键 pattern
列 4 个 bucket → 然后选 1 个 (session-context) expand——这是 mental rule "列完 bullet 立刻 expand 一个" 的应用。

18-26 min · Model Architecture
你的展开（约 6-8 分钟，邀请面试官选 deepening 方向）

"Two-stage: retrieval and ranking.
Retrieval: I'd use a two-tower architecture—user tower and content tower—producing dense embeddings, with approximate nearest-neighbor search over the content index. The user tower takes user features + recent session history; the content tower takes the multimodal content embedding + content metadata. Training objective is contrastive: positive pairs from engagement logs, negatives sampled from in-batch plus a small fraction of hard negatives mined from early-skip events.
I'd actually run multiple retrieval channels in parallel: (1) the main two-tower personalized channel, (2) a trending/recency channel that surfaces fresh content with limited history, (3) a diversity channel that pulls from under-represented content clusters relative to the user's recent history. Each channel contributes a fraction of the candidate pool—maybe 60/20/20.
Ranking: a deeper model—DLRM-style architecture with separate towers for sparse and dense features, deep cross network for feature interactions, and multi-task heads corresponding to my label schema: watch-ratio head, explicit-engagement head, early-skip head. The async precompute window for home feed gives us latency headroom to afford this depth.
Final score is a weighted combination of head predictions, with weights tunable post-training. This is intentional—it lets us adjust the engagement-versus-quality trade-off without retraining.
Want me to deepen retrieval, ranking architecture, or the multi-task head design?"

关键 move

多 retrieval channel + 量化比例 (60/20/20) = senior signal
结尾邀请面试官选 deepening 方向 = collaborative mode 切换
不要主动深入所有三个——面试官选哪个再深入

如果面试官选 "ranking"，你的 deep dive：

"For ranking, the core architecture is sparse-feature embeddings + dense-feature MLP, then a deep cross network for interactions, then multi-task heads. The non-obvious decisions are:

Sharing strategy across heads: shared backbone, head-specific top layers. Watch-ratio and engagement are correlated enough to benefit from shared representation.
Loss weighting: I'd start with equal weighting and tune via Pareto-style search on offline metrics, not gradient-based loss balancing—it's more interpretable and the heads aren't competitive enough to require sophisticated balancing.
Sequence modeling: for session-aware ranking, I'd add a transformer or GRU layer over the last K items in the session, producing a session-context embedding that feeds the ranking model."



26-32 min · Bias & Objectives
Bias 段（这是 Strong Moment #3）

"I want to spend time here because I think bias handling is where most recommendation systems underinvest.
The dominant bias in Reels is exposure bias—we only have labels on content we chose to show. This creates a feedback loop where the model reinforces past retrieval decisions and progressively narrows the recommendation space. Three layers of mitigation:
Standard correction at training time: IPS or propensity weighting on training samples, weighting inversely by probability-of-exposure. This corrects bias in the data we have."

* Strong Moment #3 核心段（90 秒）

"But I want to push the framing further—I'd reframe exposure bias as a system-level data acquisition problem, not just a training-time statistical correction. Three places we can intervene:
First, onboarding as labeled exploration. New users go through cold-start anyway. Rather than treating cold-start as a constraint to overcome, treat it as an opportunity to collect high-quality preference labels under controlled exposure—surface a curated diverse set covering distinct content clusters, and use early engagement as relatively unbiased preference signals.
Second, periodic re-exploration for existing users. Allocate a small fraction—say 5%—of impressions per session to controlled exploration: content from under-represented clusters relative to the user's recent history. Dual purpose: bias mitigation and interest-drift detection.
Third, content-side cold-start ramp. New uploads have no engagement history. Guarantee fresh content an impression budget in its first hours, gated by quality filters to avoid spam capture.
Failure modes to watch: (1) exploration budget being gamed by low-quality content—mitigate with quality eligibility filters; (2) UX degradation from over-aggressive exploration—cap per-session budget and A/B test; (3) exploration data still being biased if retrieval already filtered out long-tail—need to ensure exploration draws from a wider candidate pool than production retrieval.
Why this matters more than IPS alone: IPS corrects bias in the data you have. This approach changes the data you collect. It's a stronger lever, but it requires cross-functional cost—product and growth pay part of the bill that ML would otherwise pay in accuracy loss."

Strong Moment #3 结束。然后 objectives：

"On objectives, I'd combine three:

User engagement (multi-head, as discussed)
Ecosystem value—creator retention signals, content diversity at the platform level
Compliance and safety—policy violations, low-quality content

Combination strategy: multi-task heads for engagement and ecosystem (tunable weighted combination), but compliance applied as a hard filter at re-ranking, not as a loss term. Compliance violations aren't 'less engagement'—they're disqualifying. Treating them as a soft loss term is a category error that recommendation teams often make."

关键 verbal patterns

"I want to push the framing further—I'd reframe X as Y, not just Z"
"Why this matters more than [standard approach]: [trade-off articulation]"
"Treating X as a soft Y is a category error" ← 这种 phrasing 是 senior signal


32-38 min · Evaluation
你的展开（约 4-5 分钟）

"Three layers: offline, online, long-term.
Offline metrics: per-head metrics first—NDCG and weighted watch ratio for the engagement head, AUC for explicit engagement and early-skip. Then aggregate ranking metrics: session-level diversity, coverage of long-tail content. Critically, all metrics are sliced by video duration buckets because of the confounder I mentioned, and by user segment (new vs established).
Counterfactual / replay evaluation: before going to A/B test, I'd use logged data with IPS-weighted replay to estimate online performance. This catches obviously broken candidates before exposing users.
Online A/B: standard, but with non-standard guardrails. Beyond per-event engagement, I'd track session-level metrics—session length, return rate, day-N retention—because Reels' real value is sessions per user, not clicks per item.
Long-term holdout: a small slice of users held out from new model launches for 30+ days, to detect long-term degradation that short A/B can't catch—filter bubble narrowing, creator-side ecosystem effects, fatigue accumulation.
One thing I want to flag: the alignment problem between offline and online. Offline NDCG improvements don't always translate to online retention. I'd track this correlation explicitly and recalibrate offline metrics when they drift from online outcomes."

关键 senior signal

Slicing by confounder (duration buckets, user segments)
Counterfactual replay before A/B
Session-level, not item-level metrics for Reels
Long-term holdout for delayed effects
Offline-online alignment as itself a metric


38-42 min · Zoom-out + Top Risks
* Strong Moment #4（约 2-3 分钟）

"Let me zoom out for a moment and summarize the design, then flag the top risks I see.
We have a two-stage retrieval-plus-ranking system with multimodal content understanding, multi-task ranking heads, session-aware features, exposure bias mitigation via active exploration policy, and evaluation across offline, online, and long-term layers.
The top three risks:
Risk 1: Exposure bias compounding faster than mitigation can correct. Our mitigations are partial—5% exploration budget may not be enough if the feedback loop is strong. I'd want to monitor content diversity served over time and have a circuit breaker if diversity drops below threshold.
Risk 2: Multi-task loss imbalance over time. Heads may drift in relative importance as the data distribution shifts. I'd build retraining pipelines that re-tune head weights, not just retrain weights at fixed loss combinations.
Risk 3: Long-term engagement versus short-term watch time. Watch-ratio optimization can be gamed by clickbait or rage content. The pairing with explicit engagement signals partially addresses it, but the real defense is the long-term holdout and quality-survey signals I mentioned in evaluation. If we ever see watch ratio going up but retention going down, that's the most important alarm.
Are there parts of the design you'd like me to deepen?"

关键 pattern

"Let me zoom out—[summary in 3 sentences]"
"Top N risks" + 每个 risk 包含 mechanism + mitigation
结尾邀请深入而不是 "I'm done"


42-45 min · Serving + Q&A
轻描淡写（最多 2 分钟）

"On serving, two-stage matches our two-stage model: ANN-based retrieval over the content index returns ~1000 candidates, ranking scores them with the deep model. Multimodal embeddings are precomputed at upload, so serving-time content cost is minimal. User-side features computed at request, content-side features cached. We can precompute a candidate pool for active users during predictable idle windows and refresh at request time with fresh ranking. I won't go deeper unless you'd like—happy to discuss monitoring or rollback if useful."

这一段的目的
主动 deprioritize——告诉面试官你 aware of serving 但不在 ML SD round 上花预算。"I won't go deeper unless you'd like" 是 graceful exit。

这份 golden example 的元结构（你 internalize 的核心）
Framing (60-90s)
├── 2 specialty thesis (each 45-60s)
├── what / why-Reels-specific / ML implication / cost
└── Active deprioritization + yes/no check

Body段 (每段)
├── Sub-section announcement ("N parts: A, B, C")
├── List bullets → pick 1 expand to 60s
├── Surface 1 non-obvious risk / confounder
└── Transition with "unless you want to deepen X"

Strong Moment (4 个预分配)
├── State the reframe / non-standard claim
├── 3 concrete actions with who/what/cost/量化
├── Failure modes + mitigation
└── Trade-off articulation ("why this beats X")

Zoom-out (3 min before end)
├── 3-sentence summary
├── Top 3 risks with mechanism + alarm signal
└── Invite deepening

偏好节奏的 meta-rules（我作为面试官最喜欢的候选人节奏）

前 90 秒不要问澄清问题——直接 propose framing 并用 yes/no 收尾
每个开放问题给 60-90 秒回答——不要 30 秒，不要 2 分钟
列完 N 个 bullets 立刻 pick 1 expand——机械规则
每个 strong moment 包含 trade-off——"X is stronger but costs Y"
每 8-10 分钟主动 zoom-out 或邀请方向选择——避免线性 brain dump
当面试官表情困惑时立刻 park 当前 topic——"let me park that, more important is..."
Serving 段主动短——这是 deprioritize signal
Wrap 时一定有 top-N risks——这是 E5 边界 signal，也是 E4 strong 必备








题目：短视频推荐系统（类似TikTok/Reels）
楼主的方案：
检索：Two-Tower model做candidate generation
精排：DCN-V2 / MMoE多目标（P(click), P(comment), P(share), E(watch_percentage)）
重排：Business logic + diversity保障
Feature engineering：视频特征、用户特征、交叉特征、GraphSAGE社交特征、上下文特征
探索：Contextual bandits（epsilon-greedy + Thompson sampling, 2% exploration traffic）
Cold start处理
追问的点： position bias（用inverse propensity weighting）、training/serving skew、feedback loop问题。
整体表现：Strong E5, borderline E6。




最终结果：E5通过，进team matching。 没拿到E6有点遗憾，主要是MLSD没有展示V1→V2的迭代思维，citation of specific papers也不够。

------------

ML design 不求背题，关键是思路要顺。做到下面三点基本就稳了：
        1.        问题拆得干净（目标、指标、限制能说清楚）. Waral dи,
        2.        方案有取舍（为什么选这个模型/特征，trade-off 能讲）
        3.        能讲自己做过的完整项目（怎么做、踩过什么坑、效果如何）

面试官主要看你的判断，不看你讲多复杂。能把逻辑讲通就够了。

设计一个ML系统detect一个广告里包不包含weapon。

-----
ML system design是设计一个系统去predict facebook events里面人会不会参加。回答的稀烂。申别的SDE的时候准备过很多SDE的system design被彻底卷回原来的套路，疯狂画各种方框，最后没时间讲ML里的重点比如metric和eval之类的。。。肯定是超级烂的feedback

---

对于ML design的答题框架的话，我基本上把题目分成了两大类：
Recommendation/Search/Ads: 这类问题基本上的大结构就是retrieval -> ranking -> re-ranking。只要围绕着这个结构讲，基本上不会出大问题。讲的时候要注意每个design的选择。就像平时工作写design doc，要比较不同的option的优劣，然后再提出自己的proposal。Retrieval主要用的是two tower deep retrieval模型， 然后ranking用的多数是multi-task deep learning模型。
Bad ads/Relevance: 这类题目要侧重数据的来源（人工标注），以及如何解决数据量比较小的问题。现在基本上都用LLM finetune teacher，然后用teacher来做bulk inference，最后distill到student来解决这类问题。

不了解的可以搜一下，基本这个问题可以抽象为你有很多user，很多item，一定的历史数据(user买item后的rating)，现在你要决定推荐哪些新的东西给每个user

具体到你被问的问题，可能会有一定的变种，举几个例子
1. Yelp饭馆的推荐，涉及到了geolocation information
2. Facebook Newsfeed推荐，涉及到了不同user之前的networking
3. Ins Story推荐，每条Story是独一无二的并且是有时间性的
4. Spotify音乐推荐，怎么把音乐做个embedding


ML Design，经典地点推荐设计

1. 给定news feed和所有的评论，抽取top3 评论
    2. 做一个视频搜索系统，input output 都只有视频，没有文字
    3. Recommender system
    4. recommendation friends
    5. ads recommendation
    6. event recommendation
    7. design a personalized location recommendation system
    8. classify if an ads is weapon sale or not

    9. restaurant recommendations














