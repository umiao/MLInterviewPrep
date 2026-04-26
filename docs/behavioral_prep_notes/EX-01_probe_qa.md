# EX-01 (Search Diversity --- Intent Collapse via Item-vs-Page Diagnosis) --- Probe Q&A + Delivery Notes

This file holds **interview prep material** for EX-01, kept separate from the
DB-stored STAR fields (which are the interview-ready content). DB carries
title/situation/task/action/result/risk + an NRG-v1 narration guard;
this file carries the full set of anticipated probes + answer directions +
delivery cues used during practice and live delivery prep.

Style follows the 2026-04-21 user direction (Discord msg 1496054494696575056):
"中英混合也不需要去多改" --- content kept in 中英混合 style for delivery prep.

Linked story: `behavioral_examples.example_id='EX-01'` (id=1).
Principle tags: invisible_to_standard_metrics / root_cause_diagnosis /
item_vs_page_level_reasoning / self_initiated_direction /
end_to_end_prototype_one_week / problem_framing_before_persuasion /
ambiguous_assignment_ownership / dashboard_blindspot_discipline.

---

## 5 Anticipated Probes + Answer Directions

### Q1: "200M+ annualized over multiple years --- how do you actually attribute that to your diversity blend, vs. concurrent ranker work?"

**应答方向 (这是最危险的问题, 直球答 attribution)**: 不要答"是我搭的所以是我的功劳", junior 答案。答: "我把 attribution 拆成两段。第一段是 Hacker Week 那次实验 -- diversity blend on / off, holdout traffic, 直接读 GMB 和 multi-intent slice 的 conversion delta, 那段 causal 是干净的, ballpark 几个 million 量级。第二段 200M+ 是 follow-on -- 我的 prototype 之后被其他 vertical 复用 (homepage, related items, etc), 也催生了后续 holistic ranking 的几个项目, 那段我不 claim sole authorship, 我 claim methodology origin。我对面试官的 framing 是 -- 这是我 *originated* 的 line of work, 不是 'I personally drove 200M', 那两个不是同一件事。"

### Q2: "你说 dashboard 是健康的。但肯定有人在看 conversion rate 或 session abandon rate -- 'invisible' 是你后 framing 的吗, 还是当时真没人在看?"

**应答方向 (self-narrative honesty 检验)**: "Fair callout。当时 dashboard 看的是 query-level CTR + GMB aggregate, 这两个指标 dominant-intent 用户是健康的, aggregate 就是健康的, 这是 frame 不变 -- it really wasn't visible *in the metrics being watched*。但你说得对, abandon-log 数据是一直在的, slice 不是新工具 -- 是没人去 slice。所以更准确的 framing 不是 'invisible', 是 'invisible *to the dashboard culture*'。这是 organizational blindspot, 不是 instrumentation 缺失。我从那以后 design metric 第一个问 'this metric is healthy means *who* is happy, and who is not measured'。"

### Q3: "一周从 hunch 到 defensible diagnosis 加 working prototype 加 experiment framework -- 哪些 corner 你 cut 了, 真实的 vs marketed?"

**应答方向 (velocity 真实度检验)**: "几个 cut: (1) abandon-log slice 我只跑了一个 query category sample (~200 query) 不是全量, 全量是后续 rigor 阶段补的。(2) blending 算法是 simplest possible -- intent-coverage proxy 用了 category prior, 不是 learned re-weighting, 那个是第二阶段。(3) experiment framework 我复用现有的 A/B 平台, 没自己搭。真正 hard 的部分是 prototype 不是 framing -- framing 我有信心, 因为 abandon-log + purchase data 那个 evidence chain 很硬。一周不是 'I built everything from scratch', 是 'I made a defensible enough case to keep going'。"

### Q4: "Item-level vs page-level reasoning 在 IR community 是 well-known 的 -- 为什么你 team 当时没意识到?"

**应答方向 (避免贬低 team / 避免 'obvious in hindsight' 陷阱)**: "在 IR literature 里确实 well-known -- learning-to-rank 论文从 RankNet 时代就讨论 listwise vs pointwise。但我们的 ranker 不是从 IR theory top-down 设计的, 是从 e-commerce conversion optimization bottom-up 长出来的, item-level scoring 是历史路径, 不是 ignorance。Team 意识到 page-level 的成本和 ROI 不明确, 所以一直 deprioritized。我做的不是 introduce new theory, 是 *quantify the cost of not doing it* -- abandon-log slice 把那个 hidden cost surface 出来, 让 'should we go page-level' 变成有数据支撑的 question。这是 prioritization, 不是 discovery。"

### Q5: "Strongest counterargument to diversity blending 是什么 -- review 时谁最 skeptical, 为什么?"

**应答方向 (critique-resilience 检验, L5 要 own counterargument 不是 dismiss)**: "Strongest pushback: 'diversity is hurting your dominant-intent users, you are robbing Peter to pay Paul'。Reviewer 担心 the half that *was* served well 会被 blend 拖低 conversion。这是 fair concern -- intent-coverage proxy 不是 free lunch。我的回答不是 'no, it's strictly better', 是 'yes, there is a tradeoff and I quantified it' -- dominant-intent slice 的 conversion 确实有 small negative delta, 但 minority-intent slice 的 positive delta 是 ~5x larger because the baseline was so low。Aggregate GMB 净正。这个 tradeoff framing 是 review 通过的关键 -- 不是因为我 prove 它没成本, 是因为我 owned the cost 并 show net positive。"

---

## 口述 Delivery 提醒

- **"The dashboard was fine because the dominant-intent users were fine. The missing half was invisible."** 这两句是 hook 的核心, 中间停一拍。这是 NRG-v1 要求的 "invisible half" lead -- 不能跳过去直接 "200M impact"。

- **"Item-level scoring was producing page-level homogeneity, by design."** "by design" 那两个字要重读。这是 structural diagnosis, 不是 calibration miss -- 这个区分是 L5 signal, 不要快带过。

- **200M+ / SIGIR 这两个 token 只在 Result 段说一次, 不要在 lead 或 lesson 里复述**。NRG-v1 明确说 boast-stack 会把 L5 diagnosis 故事 demote 成 L4 trophy 故事。如果面试官追问 outcome 才展开。

- **Lesson 句 "Healthy metric could be measuring only the users the system didn't lose"** 讲完立刻停。Crisp lesson 规则 -- 不要补 "and that's why I always..."。

- **如果面试官 cut off 中段**, standalone close 是 NRG-v1 给的那句: "Item-level scoring creates page-level homogeneity --- any healthy-looking metric could be measuring only the users the system didn't lose." 背熟这句, 任何 abort point 都能用它收尾。
