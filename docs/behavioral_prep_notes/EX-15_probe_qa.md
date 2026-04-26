# EX-15 (Model Deprecation Incident --- Reframing Conflict into a Governance Pattern) --- Probe Q&A + Delivery Notes

This file holds **interview prep material** for EX-15, kept separate from the
DB-stored STAR fields (which are the interview-ready content). DB carries
title/situation/task/action/result/risk + an NRG-v2 narration guard;
this file carries the full set of anticipated probes + answer directions +
delivery cues used during practice and live delivery prep.

Style follows the 2026-04-21 user direction (Discord msg 1496054494696575056):
"中英混合也不需要去多改" --- content kept in 中英混合 style for delivery prep.

Linked story: `behavioral_examples.example_id='EX-15'` (id=19).
Principle tags: adaptability / ownership / failure / humility /
structural_reframe / shared_infrastructure_governance / credibility_first.

---

## 5 Anticipated Probes + Answer Directions

### Q1: "你 deprecate 之前为什么没 check hardcoded calls? 这看着像基本的 on-call discipline 缺失。"

**应答方向 (这是最危险的问题, 不要 deflect 到 dashboard)**: 不要答 "dashboard 不全是 dashboard 的问题", junior 答案 = blame the tool。答: "Honest answer -- 我用了 dashboard 当 source of truth, 这是我的 due diligence 不到位。Dashboard 只 track URL-param 调用, 这一点其实有 institutional knowledge -- 我应该问 'what does this dashboard *not* see' 而不是 'does this dashboard show zero'。这个 negative-space inquiry 是我事后 build into deprecation checklist 的第一项。所以 short answer -- 这是 process gap; immediate ownership 是我; 我 fix 的方式是把 negative-space check 写进 protocol, 不是修 dashboard。"

### Q2: "你的 ownership-transfer framework 听着挺 clever, 但是不是变相让 consumer team 不用迁到更好的 infra?"

**应答方向 (reframe-as-deflection 检验, L5 要 own tradeoff)**: "对, 这是 framework 的真实 cost。ownership-transfer 给 consumer team 一个 'opt out of migration' 的 escape hatch -- 我们 search engine team 的 capacity 拿回来了, 但 org 整体会 fragment, 同样 calibration 在两个地方维护。我接受这个 tradeoff 是因为 zero-sum conflict 的另一边 -- '所有 consumer 必须迁' -- 在 organizational reality 下根本推不动, 推一年还是死结。Ownership-transfer 是 *imperfect-but-shippable*, 把 deadlock unblock 比 fragment cost 重要。这个 framework 不是 universal solution, 是 zero-sum 资源冲突时的 compromise mechanism。"

### Q3: "你怎么 convince senior leadership? 你当时没 organizational power, 这种 boundary 决议通常需要 director-level push。"

**应答方向 (influence-without-authority 具体化)**: "几个 enabling factor: (1) 那一周 rollback execution -- 3-4 个 pipeline 全部 unblock -- 给我换到 credibility, leadership 看我的 escalation 不是 'engineer complaining', 是 'engineer who already absorbed the cost asking for structural fix'。(2) Framing -- 我没 propose '我们 team 的 quota 应该被保护', propose 的是 'capacity ownership boundary 需要明确, 这是 org 问题不是 team 问题'。这个 framing 让 leader 不需要在 my team vs other team 之间 pick side, 只需要 acknowledge 现状有 ambiguity。(3) 我 surfaced 第三选项 ownership-transfer -- leader 不喜欢 binary 选择, 给他第三 option 让 decision feel solvable。这三点合起来才推得动, 单独任何一点都不够。"

### Q4: "你说 'deprecation is a negotiation, not an announcement' --- 但分布式系统里有时候你必须 unilaterally deprecate (security, compliance)。这个 lesson 什么时候是错的?"

**应答方向 (lesson-falsifiability, L5 要 own lesson 的 boundary)**: "Good challenge -- lesson 的 boundary 是 *consumer-facing infrastructure with optional consumption*。Security / compliance 那种 forced deprecation 不在 boundary 里 -- 那是 announcement + grace period + hard cutoff, negotiation 反而是 anti-pattern。我的 lesson 适用面: 当 deprecation 的目的是 *reclaim shared resource* 而 consumer 有 viable alternative path, negotiation 才是对的 framing。如果 consumer 没 alternative (legacy DB schema must die for security 漏洞), unilateral 是对的, 这种情况 my lesson 不 apply。我把 lesson 写得 absolute 是为了 candidate 表达 brevity, 实战 boundary 我清楚。"

### Q5: "这个 pattern 你后来再用过吗? 给一个具体的第二例, framework worked 或 failed 都行。"

**应答方向 (pattern-validation, 没有 second example 不要硬编)**: "用过两次, 一次 worked 一次 partial。Worked: 后来 retire 一组 indexing macro, 同样 zero-sum 资源冲突, 我 propose 同样 ownership-transfer 选项, 一个团队选 own, 三个 migrate, 一周内 closed。Partial: 还有一次涉及 cross-org system, 我 framework 推到 consumer team 的 director 那里被 stuck 了三个月 -- 那次 failure mode 是 ownership-transfer 需要 consumer team 有 maintenance budget, cross-org 情况下 budget 不在我能 visible 的 place, framework 假设破裂。Pattern 的 fragile point -- 它假设 receiving team 有 capacity 接 ownership, cross-org 时不一定成立。"

---

## 口述 Delivery 提醒

- **Lead 要先 ack failure**, NRG-v2 明确说 -- 不要直接跳到 ownership-transfer reframe 那部分。说 "dashboard 漏掉了 hardcoded calls, 3-4 个 pipeline 被 block" 之前不要 frame 任何 cleverness。

- **"Don't argue about who followed the right process --- just absorb the rollback."** 这句话语速放慢。这是 character signal -- L5 在 conflict 的第一选择是 absorb cost, 不是 protect record。

- **"That week of credibility bought me the standing to push a deeper change."** "credibility bought ... standing" 那个 frame 不要含混 -- 这是 sequencing logic (do X first to earn right to do Y), 是 L5 的 organizational calculus 而不是 raw cleverness。

- **Reframe 那段** -- "我引入第三 option ownership-transfer" -- 讲得 deliberate, 不要快。这是 story 的 pivot, 也是 most-quoted line。

- **Lesson "deprecation is a negotiation, not an announcement"** 讲完立刻停。NRG-v2 给的 standalone close 就是这句, 任何中段被 cut 都用它收尾。
