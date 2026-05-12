一、Family Taxonomy（30 秒判断题型）
#题目Family核心 unique twist 一句话1Top 3 comments extractionIntra-item ranking候选池极小、top slot 影响下游对话质量2Video-to-video searchPure retrieval (no query)"相似"无法被 query 定义，多 facet3Friend recommendationGraph-native图结构是 retrieval 本身，reciprocity 决定 label4Ads recommendationAuction-mediated要 calibrated probability，多 stakeholder5Event recommendationSparse + temporal双重 cold-start，事件会过期6Location recommendationContext-dominantPOI 稳定，user intent 在 request time 才出现7Weapon ad classifierAdversarial classificationAttack 模式演化，cost asymmetric8Yelp restaurantAspect-richReview text 是主导信号，aspect 级匹配9FB News FeedHeterogeneous ranking多内容类型，社交图权重，MSI 而非 engagement10IG StoryTime-bounded sequential24h 过期，author-tray 而非 item ranking11Spotify musicAudio + session音频 embedding + session 连续性 + relisten 正向12Predict event attendancePrediction-as-feature必须先问"下游谁用这个 prediction"13ReelsSession-continuous ranking见 golden example

二、Cross-cutting Reusable Pieces（你的"积木库"）
跨题通用，记熟一次到处用：
积木何时套用一句 justificationTwo-tower retrieval + deep rankingStandard rec/feed/search 默认架构retrieval 走 ANN，ranking 走 latency 富余下的 deep modelMultimodal embedding precomputed at upload内容为视频/图/音频把内容理解开销跟 serving cost 解耦，刷新只在 encoder 升级时Multi-task heads (engagement / quality / strong negative)任何 user feedback 非单一信号单 binary label 损失信息；多 head 还能 post-train tune 权重IPS / counterfactual replay任何讨论 exposure bias / A/B safetyoffline 数据有 bias，replay 在 A/B 前过滤明显 broken candidateActive exploration policy (onboarding + re-explore + content ramp)想 push 到 E5 信号重构 exposure bias 为 data acquisition 问题（高级 reframe）LLM-as-teacher → distilled studentLabel scarcity / 内容理解任务Teacher 离线 bulk inference，student 在线 serving，符合 2025 Meta 实践Long-term holdout (~5% users, 30+ days)任何讨论 evaluation 完整性短 A/B 抓不到 retention/filter bubble/fatigueCalibration check across surfaces多 surface 混排或概率被下游消费跨 head 的 score 不可比时 ranking 失真Slice metrics by confounder任何 evaluation 段aggregate 数字会掩盖 sub-group failure（duration、new vs return user）

三、Per-Question 详细卡片
每张卡片同样结构：Twist → Puzzle pieces → Anti-patterns → Strong moment hook。

Q1. Top 3 Comments Extraction
Unique Twist: 这是 intra-item ranking，不是 cross-item ranking。候选池只有几十到几千，且 position 0 的 comment 是下游 conversation 的种子——比 user engagement 更深远。
Puzzle Pieces
PieceWhySingle-stage ranking（跳过 retrieval）N 小，retrieval 没必要Quality-weighted score（不止 engagement）Top comment 被下游看到，representativeness 比 raw likes 重要Time-normalized engagement label早 commenter 自动赢 raw like 数，要除以暴露时长Author authority featureverified/历史质量是稳定信号Diversity constraint不要 3 条都同一作者 / 同一情感倾向Adversarial-aware（first-poster gaming）有人专门抢沙发，要 detect
Anti-patterns

套两阶段 retrieval+ranking 框架（N 太小，浪费）
用 raw like count 当 label（早 commenter 永远赢）
只优化"被选中 comment 的 engagement"，不想下游影响

Strong Moment: "The comment at position 0 isn't just a ranked result—it becomes the seed of the conversation that the next thousand viewers see. So we're optimizing downstream conversation quality, not just the engagement of the selected comments."

Q2. Video-to-Video Search (no text)
Unique Twist: 没有 text query，"相似"本身需要被定义。视觉相似 / 音频相似 / 用途相似是三个 axis，互相不重合。
Puzzle Pieces
PieceWhyPer-modality encoder（visual / audio / OCR-caption）各 modality 独立 embeddingL2-normalize per modality before fusion不 normalize 一个 modality 会 dominateMulti-facet retrieval（每 facet 各 retrieve 一批）user intent 不可知，先 cover 多 axisLearned fusion weights from click/dwell用户点击哪个 facet 来的结果 → learn weightSingle-stage（query 是 video，没有 user tower）没有 user side，不需要 two-tower 的 user encoderCold-start friendly（content-only）新 video 一上传就可索引
Anti-patterns

单一 fused embedding 不做 modality normalize
强行套 two-tower with user side（这题没有 user-specific query）
假装 query intent 已知

Strong Moment: "'Similar' is undefined here—it could mean visually similar, audio-similar, or intent-similar, and these pull in different directions. I'd treat this as multi-facet retrieval and let user interaction learn which axis matters in their session."

Q3. Friend Recommendation
Unique Twist: 图结构是 retrieval 本身，不是 feature。Reciprocity（双向接受）才是真 positive。Dismissal 是异常强的负信号。
Puzzle Pieces
PieceWhyGraph traversal retrieval（2-hop, entity overlap）候选空间 = extended network，不是全局 item 池Graph features (mutual friends, communities, shared groups)图结构 native signalReciprocity-aware label（accept 才算 positive）单向 send 不可靠Negative signal from dismissal已 ignore 的不要再推，是强 signalPrivacy hard filters（block, restricted, 年龄差等）红线，不能 ML soft-handleEntity overlap cold-start（school/work/location）新账号没 graph，用 entity match
Anti-patterns

两塔走 user embedding similarity（忽略图结构）
把 send-request 当 positive label（接收方 ignore 你也 +1）
把 dismissal 当作"待会再试"的 neutral

Strong Moment: "The strongest signal in this domain is actually the negative—a user dismissing a PYMK suggestion is a far more reliable label than them sending a friend request, because the request can be one-sided while dismissal is unambiguous."

Q4. Ads Recommendation
Unique Twist: 输出必须是 calibrated probability，不是 ordinal score——auction 的 bid × pCTR 数学要求 calibration。多 stakeholder（user / advertiser / platform），conversion 有延迟。
Puzzle Pieces
PieceWhyLogloss + calibration（不用 pairwise）pairwise 破坏 calibrationMulti-task: pCTR + pConversion + pQuality不同目标分头预测再合Final score = bid × pCTR × pConversion × qualityAuction 输入Delayed feedback model（windowed labels）购买可能 7 天后发生，naive training 偏向短延迟Counterfactual / IPS replay before A/BA/B 会影响 advertiser bidding，counterfactual 更安全Pacing & budget 在 ML 之外处理ML 输出 probability，pacing 是 downstream control
Anti-patterns

用 NDCG / pairwise loss
把所有 conversion 当 same-day 处理
把 advertiser 当 static（他们会 react 你的模型变化）
把 pacing/budget 塞进 ML loss

Strong Moment: "Ads ranking isn't really ranking—it's calibrated probability estimation feeding an auction. The moment you switch to a pairwise loss for NDCG gains, you've broken the auction economics."

Q5. Event Recommendation
Unique Twist: 双重 cold-start（event 一直新+一直死，user RSVP 频率极低），geo+time 是硬约束不是 feature，conversion 高成本（commit time，不是点击）。
Puzzle Pieces
PieceWhyContent-based retrieval 主导per-user 数据太稀疏，CF 不够Hard filter: geo radius + time window + capacity不能跨地理硬推Multi-label: click / RSVP / attendclick 是 noise，RSVP 是 intent，attend 是 ground truthFriend-going 作为强 feature强 social signal，但小心 selection biasCold-start ramp for new events（quality-gated burst）新 event 没历史，需要 exposure 启动Time-decay calibration（越近 event 越要 calibrated）下游可能用 prob 决定 notify
Anti-patterns

纯 CF 套 user-item matrix（per-user 太稀疏）
soft-filter 地理位置（你不能去 500 mile 外的 event）
用 click 当主 label
忽略 capacity / 已 fully booked 的 event

Strong Moment: "A typical user might RSVP to 3 events a year. Per-user history is too sparse for collaborative filtering to be the primary lever—content embedding over event metadata has to do most of the work, with social signals (friends attending) as the strongest personalization input."

Q6. Personalized Location Recommendation
Unique Twist: POI 本身长期稳定，但 user intent 在 request time 才浮现。同一个咖啡店 9am 是答案，9pm 不是。Context 不是 one of many features——它是主导 intent disambiguator。
Puzzle Pieces
PieceWhyHeavy context features（time, weather, calendar, party size）决定当下 intentPOI embedding 稳定 + offline precomputePOI 本质变化慢Real-time user signal（current location, recent queries）momentary intentIntent classification as intermediate task"吃饭 vs 喝咖啡 vs activity" disambiguate 后再 rankDiversity in re-ranking不要 5 个都是 cafeDistance + travel-time featurewalking 5min vs driving 30min 体验不同
Anti-patterns

把 context 当成一般 feature（它是主信号）
用静态 user preference profile（intent 是 momentary 的）
优化 click 而不是 visit / booking

Strong Moment: "The user at 9am and the same user at 9pm have completely different intents—context isn't one feature among many, it's the primary disambiguator. Without it, we're just recommending the user's average preference, which is no one's actual preference at any moment."

Q7. Weapon Ad Classifier
Unique Twist: Adversarial（bad actors 主动 evade）+ 极端 class imbalance（~0.1% positive）+ multimodal + error cost asymmetric（FN 远比 FP 严重）。
Puzzle Pieces
PieceWhyMultimodal input（image + ad text + landing page）单 modality 漏 image-encoded 武器LLM-as-teacher → distilled studentTeacher 离线 bulk 标，student 在线 serveActive learning loop（attack 模式每周变）静态数据集 3 个月就失效Class imbalance: focal loss / 两阶段 cascadenaive supervised 学不到 0.1% positiveAsymmetric threshold + human reviewFN 是政策违规，FP 是 ad 被错拒Adversarial augmentation（混淆样本合成）模型要 robust to obfuscation
Anti-patterns

对称 thresholding（FN 和 FP 不等价）
静态 training set（attack 每周演化）
单模态（text-only 漏掉 image weapons）
直接用 LLM serve（latency / cost 撑不住）

Strong Moment: "The training set you ship today is broken in three months because attackers evolve. The real system isn't the model—it's the active learning loop. The model is just the current snapshot of an ongoing arms race."

Q8. Yelp Restaurant Recommendation
Unique Twist: Review text 是 dominant signal。Aspect-level matching（quiet / group-friendly / vegan / romantic）超过 rating-level matching 的上限。
Puzzle Pieces
PieceWhyAspect extraction from reviews（LLM-based）"适合约会"这类 aspect 是 review-only signalUser aspect preference from their review history用户写过 review 暴露偏好Aspect-level matching（不止 embedding cosine）比 rating-based CF 信号丰富一个量级Geo + open-now hard filter不能 soft handleTime-of-day relevance（breakfast vs dinner）同店不同时间 relevance 不同Photo / recent visit signal高时效，反映 current quality
Anti-patterns

纯 rating-based CF（信号上限低）
忽略 review text
静态 "good restaurant" 排序（跟"谁问、何时问"无关）

Strong Moment: "Rating-based CF has a hard ceiling because two 4-star restaurants can be completely different experiences. The lift comes from aspect-level matching—extracting 'is this place quiet, group-friendly, vegan-OK' from reviews and matching to the user's expressed preferences in their own review history."

Q9. FB News Feed
Unique Twist: 内容类型异构（status / photo / video / link / milestone / group post），社交图权重显著，Meta 显式从 engagement 转向 MSI（Meaningful Social Interactions）。
Puzzle Pieces
PieceWhyMulti-source candidate generation（friends / groups / pages）不同 source 不同 retrieval logicCross-source ranking最后合一个 feed 要互比Multi-task heads weighted toward MSIcomment from close friend >> like from pageDiversity across content type + source不要刷屏同一 publisherIntegrity downranking（misinfo / clickbait）well-being signal，soft filterReverse-chronology eligibility for close family/friends不能埋掉重要 update
Anti-patterns

单 ranking head on raw engagement
套 Reels 的 session-continuous 思路（feed 是 pull-based 浏览，不是 continuous consumption）
忽略 well-being / integrity（Meta 已经把这写进 explicit objective）

Strong Moment: "Meta explicitly moved from engagement optimization to MSI—a like from a stranger is worth less than a comment from a close friend. The label hierarchy isn't a nice-to-have, it's the platform's stated objective. Any design that flattens this back to 'predict click' is fighting the company's own product direction."

Q10. IG Story Recommendation
Unique Twist: 24h 硬过期 + ranking unit is author-tray, not story——你按作者顺序刷，不是逐个 story 单选。这改变整个 architecture。
Puzzle Pieces
PieceWhyAuthor-tray level ranking（不是 story-level）用户按 author 浏览Recency 作硬过滤（24h boundary）不是 feature，是 eligibilitySkip-to-next-author 作负 label这是 story 特有的 implicit negativeClose-friends signal 异常强story 比 feed 更亲密语境Within-tray story sequence modelauthor 多 story 时内部顺序Cold-start every day（content 每天全换）没有跨日 reuse
Anti-patterns

套 item-level ranking（granularity 错）
把 recency 当 feature 排序（它是硬 filter）
忽略 "close friends" / "best friends" 的隐式权重

Strong Moment: "The unit of ranking here isn't story, it's author-tray. Users consume by author, not by individual story—you watch all of Alice's stories then jump to Bob's. This changes the entire architecture: a story-level deep model is solving the wrong granularity problem."

Q11. Spotify Music Recommendation
Unique Twist: 音频 embedding（不止 metadata）+ session/playlist 连续性（mood 不能跳）+ relisten 是正向信号（跟视频相反）。
Puzzle Pieces
PieceWhyAudio embedding from spectrogram内容理解，metadata 不够Metadata features（genre / artist / era）互补的稳定信号Session context（当前在听啥设定 mood）不能从摇滚突跳到古典Sequential model (next-song given playlist so far)session-aware 是必须Repeat consumption as positive听 100 遍同首歌 = 极爱，不是疲劳Cold-start via audio embedding新 artist 没 history，audio 直接可索引
Anti-patterns

忽略 within-session mood 连续性（突变 jarring）
把 relisten 当 redundant / 疲劳信号（错，是正向）
纯 CF（audio understanding 是实打实的 lift）

Strong Moment: "Music has one feature that distinguishes it from almost every other recommendation domain: relisten is positive, not redundant. A user playing the same song 50 times is a five-star signal, not a saturation signal. This inverts the deduplication logic you'd use for video or articles."

Q12. Predict If User Attends FB Event
Unique Twist: 这是 prediction-as-feature 任务——先问"谁消费这个 prediction"，否则整个 design 走偏。这一步你上次答烂的原因可能就在这里。
Puzzle Pieces
PieceWhyStep 0: clarify downstream consumerranking? notification gating? capacity planning? 决定一切Label: RSVP vs actual attendance（两个不同 target）不同模型不同 labelTime-to-event feature（distance-from-now）提前 1 个月 vs 1 天的预测机制不同Social context（friends going, host relation）强 signalCalibrated probability（被下游消费）不是 ranking scoreCold-start for new event types演唱会 vs 婚礼 vs meetup 模式不同
Anti-patterns

不问"谁用这个预测"就开始 design（上次失败大概率在这）
单 label（RSVP 和 attend 是不同问题）
静态 prediction（probability 随 event 临近变化）
当成纯 binary classification 不想下游 calibration

Strong Moment（这一句话救场）: "Before designing this, the most important question is: who consumes the prediction? If it's recommendation ranking, we need calibrated probability for every (user, event) pair. If it's notification gating, we only score the events the user has been recommended. If it's host-side capacity planning, we aggregate. The architecture differs significantly. My default assumption is recommendation ranking—is that the intended use?"

Q13. Reels (reference only)
已在 golden example 详述。核心 twist：multimodal short-form video + session-based continuous consumption + within-session dynamics（diversity collapse / fatigue / drift）。