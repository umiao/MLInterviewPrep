# BQ-DEPTH-09 probe_notes Calibration (4 samples)

Review gate for T-P1-580. Attach to Discord for user review BEFORE downstream
work (BQ-DEPTH-10 primary batch / BQ-DEPTH-11 bulk probe_notes) starts.

## Primary assignment summary

| Question | Primary story | Rationale |
|----------|---------------|-----------|
| OWN-1 (took complete ownership of a failure) | EX-15 (Model Deprecation Incident) | Dashboard blind-spot ownership + absorb-rollback-first sequence are textbook "complete ownership" signals. |
| PS-6 (calculated risk) | EX-16 (Cross-DC Deployment) | Solo cross-DC rollout after formal PD quota denial is the cleanest "calculated, not reckless" framing in the pool. |
| ADP-19 (most challenging feedback) | EX-17 (Senior IC Feedback) | Reliance-vs-trust frame pivot is exactly the L5 differentiator the stem probes. |
| ADP-5 (mistake / handling / lesson) | EX-30 (Hash Capability Misdesign) | 3-stage handling arc + mental-model-class lesson ("domain depth != design authority"). |

Each primary is a distinct question -- no two stories share a primary Q in
this calibration batch, and the partial unique index
`ux_qel_primary_per_question` enforces the invariant at DB level.

---

## Schema (4 required fields per probe_notes JSON)

1. **core_signal** - 1-2 sentence 中文: 这题本质在问什么 L5 signal
2. **what_good_looks_like** - 3-5 bullets 中文+英文术语: L4 bar 答出这些即过
3. **what_L5_adds** - 2-3 bullets: L5 bar 在 L4 基础上再多一层 (structural reframe / risk_statement / org-level lesson)
4. **common_failure_modes** - 3-4 bullets: junior answer / redemption tail / scapegoating / 当场扣分的点

No `angle_label` field. Angle lives in prose inside the 4 fields.

---

## Sample 1: OWN-1 (primary story: EX-15)

**Question**: "Give an example of a time when you took complete ownership of a failure."

**core_signal**:
这题本质在问: 能否在 failure 发生时做到 first-person 的 structural ownership,
而不是把 blame 分散到工具/团队/流程。L5 bar 是不止 own execution, 还能 own
自己 frame 里 embed 的 blind spot (dashboard 抓不到什么 / instrumentation 缺口)。

**what_good_looks_like** (L4 bar):
- 明确 first-person attribution: 用 "I / my decision / my dashboard", 不用 "we / the team / the framework"。EX-15 primary 动作: "my traffic dashboard missed hardcoded calls in the search engine"。
- Absorb downstream pain FIRST, 再 argue process: rollback 先跑, 被 block 的 3-4 Query Understanding 团队先解套, 然后才谈 structural fix。顺序 inverted 会 kill ownership signal。
- Concrete blast radius: 具体到 "3-4 pipelines / 1 week recovery / N teams blocked", 不是 abstract "it caused issues"。量级感 = credibility。
- Correction loop 可 trace: 我如何发现 breakage (alert? user report?), 哪些是 recoverable 哪些 sunk, 哪些 counterpart 我需要主动 credit-protect。

**what_L5_adds**:
- 把 failure locus 从 execution layer 抬到 structural framing layer: 不止承认 "dashboard miss 了 hardcoded calls", 而是承认 "my mental model of the traffic surface was incomplete" -- 这是 design-time 的 gap, 不是 monitoring-time 的 gap。
- Org-level risk-if-not-addressed: 同 class failure 在 shared-infra governance 上会 reproduce (EX-15 的 ownership-transfer-as-third-path 就是 risk 的 structural fix, 不是单次 patch)。
- Credit 抑制: cost 和 accountability 全部留给自己, 不抢 counterpart 收拾残局的功劳, 这是 L5 区别于 L4 的 self-awareness 表现。

**common_failure_modes**:
- Junior 答案: "I should have written more tests / added more monitoring" -- 停在 tactical 层, 没有 frame-level reframe, reviewer 直接给 L4 以下。
- Redemption tail 太甜: 把 story 讲成 "I failed BUT then I saved the day and everyone thanked me" -- L5 bar 要的是 clean failure 的勇气, 不是 comeback arc。
- Scapegoating via abstraction: "团队的 convention 是这样的 / dashboard 没 surface 这个 / framework 就是这样设计的" -- 即使属实也会 kill ownership, 当场扣分。
- 没有具体 blast radius: 只有 "it broke production" 没有 "3-4 teams, specific Query Understanding pipelines, 1-week recovery" -- reviewer 会怀疑是编的或者规模太小。

---

## Sample 2: PS-6 (primary story: EX-16)

**Question**: "Describe a time when you took a calculated risk. What was the outcome?"

**core_signal**:
这题本质在问: risk-taking 的成熟度 -- 能否 articulate 为什么 risk 是
calculated (不是 reckless, 也不是 伪 risk), 以及 outcome 混合时能否
cleanly 区分 delivery outcome 和 risk-handling outcome。L5 bar 是能承认
delivery 出问题但 risk-handling 的 structural lesson 是 portable 的。

**what_good_looks_like** (L4 bar):
- Ex-ante (不是 hindsight) 列清 "risk 是什么 / reward 是什么 / mitigation 是什么": EX-16 primary 动作 = "cross-DC rollout solo, formal PD quota denied, I accepted counterpart bandwidth gap as the main risk"。
- Decision-making criteria 具体: 为什么 accept 这个 risk (cost of delay > expected cost of partial failure, alternative 是无限期 block, etc.), 不是 "I just decided to go for it"。
- Outcome 不粉饰: 讲 partial failure (DC1 clean, DC2 broken) 而不是把 story 讲成 clean win。Honest mixed-outcome 反而加分。
- Mitigation 动作 ex-ante 就 design: staged rollout / monitoring / rollback plan, 不是 post-hoc 安慰自己说 "其实我也想过"。

**what_L5_adds**:
- 关键的 L5 动作: 把 "delivery outcome (混合)" 和 "risk-handling outcome (可 abstract 成原则)" 显式 separate。EX-16 的 "counterpart bandwidth as a planned line item" 就是 risk class 级别的 lesson, 不是 "ask for help earlier" 这种 tactical rule。
- Org-level aftershock: 这次 risk 之后我对同类 decision 的 default 变了 (e.g., "I now refuse to take cross-team delivery without formally booked counterpart bandwidth, even if it means de-scoping")。Default-shift > lesson-statement。
- Risk 归属 internal: 即使 counterpart 没 deliver, 也把 risk 归因于 "my choice to proceed without booked bandwidth" 而不是 "their team 没给 quota"。

**common_failure_modes**:
- Reckless 伪装成 calculated: "I just trusted my instinct and went for it" -- 没有 ex-ante mitigation design, reviewer 听出是 gambling 不是 calculation。
- Risk-averse 伪装成 calculated: 讲一个其实没什么 downside 的 "风险" (e.g., "I took the risk of writing a design doc before getting approval") -- L5 bar 要的是 real stakes, 没 stakes 的 "risk" 直接 downgrade。
- Pure clean-win outcome: 让 risk 听起来像 safe bet, 削弱 story 的 weight; 反而 mixed 或 partial-failure outcome 更能 demonstrate risk-handling maturity。
- Blame counterpart: "if team X had given me bandwidth this wouldn't have happened" -- 把 risk ownership 推给别人, 当场扣 deliver-results + ownership 双 signal。

---

## Sample 3: ADP-19 (primary story: EX-17)

**Question**: "What's the most challenging piece of feedback you've received?"

**core_signal**:
这题本质在问: 面对 tough feedback 的 default reflex -- 是 defensive unpack
还是 frame pivot。L5 bar 是能承认 feedback-giver 的 mental model 比自己的
更准, 把 feedback 抽象成 defaults-class growth area (一整类 behavior),
而不是单次 patch。

**what_good_looks_like** (L4 bar):
- 具体 reproduce 当时 feedback 的 weight: EX-17 primary 情境 = "a senior IC refused to keep reviewing my code" -- 这种 action-level feedback (不是 words-only) 让 reviewer 相信 stakes 是真的。
- 第一反应 honestly: "I initially wanted to walk him through the technical context (researcher's late naming changes broke a verified PR)" -- 不假装 gracefully accepted, defensive 第一反应是人性, 承认它反而加分。
- Behavior change 有 specific 触发 action: 拒绝 manager 提出的 explain-away offer / 自己主动 rebuild consistency, 不是 generic "I became more open to feedback"。
- 时间轴清晰: feedback 时刻 -> 消化 window -> validation through consistency wins back trust, 没有 overnight redemption。

**what_L5_adds**:
- Frame pivot 动作: 不是 "I adjusted my behavior", 而是 "I realized I had conflated being relied on with being trusted" -- EX-17 primary 的 "reliance vs trust" 区分就是 mental-model-class 的 reframe, 不是 tactical patch。
- Defaults-class 抽象: feedback 不是 fix 一个 PR review, 是 re-calibrate 我整个 "接受 manager-given framing 而没 own deep context" 的 default。
- Cost acceptance 成熟: 承认 trust 需要时间 rebuild, 没有 "第二天 he immediately started trusting me again" 的廉价 redemption。

**common_failure_modes**:
- Softball feedback: 挑一个其实不 challenging 的 feedback 讲 (e.g., "my manager said I should communicate updates more often") -- reviewer 看穿后直接 downgrade, 因为 "most challenging" 的 bar 被自己降了。
- Defensive unpacking: "原因其实是 researcher 改了 name / 原因是 CI 没 catch / 所以 feedback 其实 half-fair" -- 即使事实如此, reviewer 会 kill earn-trust + humility signal。
- Redemption tail 太快: "听完 feedback 我第二天就改了, 他 immediately 开始 trust me" -- 不真实, L5 reviewer 知道 trust rebuild 是 weeks-to-months 级。
- Agree-to-disagree framing: "I respectfully disagreed but adjusted my communication style" -- 没有 real frame pivot, 停在 cosmetic 层, 丢 have-backbone 信号。

---

## Sample 4: ADP-5 (primary story: EX-30)

**Question**: "Describe a time when you made a mistake. How did you handle it, and what did you learn?"

**core_signal**:
这题本质在问: mistake / handling / lesson 三段能否 balanced 呈现, 且
lesson 是 mental-model 级的 default shift (不是 tactical patch)。L5 bar 是
lesson 能 transfer 到未来 design decisions, 而不是 "I learned to be more
careful"。

**what_good_looks_like** (L4 bar):
- Clean failure 不加 rescue tail: EX-30 primary 的 "It was rejected. And this is where I stopped." 就是 L5 的 clean-failure 动作 -- 承认 failure 就在这里结束, 不编 comeback。
- Handling 部分 concrete 3 步: (1) escalation landed + owned; (2) proposed wrong rescue (cross-4-team multi-quarter infra change); (3) rescue 被 reject 后接受 reject, 不 re-litigate。
- Lesson 可操作 + portable: "domain depth is not design authority. The authority belongs to whoever consumes the output." -- 这是 design-time default shift, 不是 "I should have asked more questions"。
- First-person blame 一路到底: 不怪 PM 没告诉我, 不怪 indexing team 没来 review, 不怪 framework 没 surface -- blame 全程在 "my framing of hash as math object"。

**what_L5_adds**:
- Mental-model shift 的高度: "domain depth != design authority" 是 class-level 的 reframe, reviewer 可以直接 imagine 我在下个 design 里是怎么用的 (先问 "whose decision depends on this output")。
- Structural follow-on signal: 承认 orphan design 之后 leaked 成 experiment-level confounding, 说明 mistake 的 blast radius 比最初理解的更大 -- 这是 L5 的 self-audit 动作。
- Cost-benefit 的 perspective pivot: 从 "individual 视角 (保留我的 design)" 切换到 "org 视角 (cost 分散到 4 个团队)" 是 L5 specific 的 ownership 表达。

**common_failure_modes**:
- Safe/trivial mistake: "I typo-ed a config" / "I forgot to merge a PR" -- reviewer 看穿是在避重就轻, 直接 downgrade。Bar 是 real stakes。
- Rescue tail 重点失衡: "mistake 之后我加班三天全部 recovery 回来, 最后 launch on time" -- lesson 被 rescue 淹没, L5 reviewer 想看的是 clean failure + abstract lesson, 不是 redemption arc。
- Lesson 太 generic: "I learned to communicate more" / "I learned to ask for help" -- 没 default-shift, reviewer 无法 imagine 我下次怎么不同。
- Scapegoating via abstraction: "the framework didn't surface this" / "PM didn't tell me" -- 把 blame 甩给 tool / counterpart 而不是 own frame, 当场扣 ownership。

---

## Review questions for user

Before moving to BQ-DEPTH-10 (primary batch for top 40) / BQ-DEPTH-11 (bulk
probe_notes for remaining ~36), please confirm / redirect on:

1. **Schema split adequacy**: Are the 4 fields (core_signal /
   what_good_looks_like / what_L5_adds / common_failure_modes) sufficient,
   or is there an axis I'm missing? (e.g., "how to transition into the
   primary story when the stem is ambiguous" -- currently folded into
   what_good_looks_like.)

2. **中英混合 balance**: Chinese carries the structural claims; English
   carries the L5 reviewer-vocabulary terms (default-shift, risk-handling
   maturity, earn-trust signal). Is this the right register for bulk
   application, or should I shift toward more English (interview delivery
   simulation) or more Chinese (study-note reading)?

3. **L5 bar specificity**: Each what_L5_adds bullet anchors on a concrete
   phrase from the primary story (e.g., "counterpart bandwidth as a planned
   line item" for EX-16 / "domain depth != design authority" for EX-30).
   Should I maintain this story-anchor pattern for bulk, or should L5 bar
   be story-agnostic (so the probe_notes survive a story swap)?

4. **common_failure_modes tone**: Current style names specific anti-patterns
   ("softball feedback", "redemption tail too sweet", "scapegoating via
   abstraction"). Should these be named + labeled consistently across all
   probe_notes (treating them as a shared vocabulary), or is story-specific
   naming OK?

5. **Primary assignments**: EX-15 -> OWN-1, EX-16 -> PS-6, EX-17 -> ADP-19,
   EX-30 -> ADP-5. Any swap suggestions before I lock these and move to
   BQ-DEPTH-10's top-40 batch?
