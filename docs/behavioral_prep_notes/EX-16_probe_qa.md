# EX-16 (Cross-Datacenter Deployment Incident --- Counterpart Bandwidth as a Line Item) --- Probe Q&A + Delivery Notes

This file holds **interview prep material** for EX-16, kept separate from the
DB-stored STAR fields (which are the interview-ready content). DB carries
title/situation/task/action/result/risk + an NRG-v2 narration guard;
this file carries the full set of anticipated probes + answer directions +
delivery cues used during practice and live delivery prep.

Style follows the 2026-04-21 user direction (Discord msg 1496054494696575056):
"中英混合也不需要去多改" --- content kept in 中英混合 style for delivery prep.

Linked story: `behavioral_examples.example_id='EX-16'` (id=20).
Principle tags: adaptability / ownership / failure / humility /
cross_boundary_failure / counterpart_bandwidth / org_policy_creation / restraint.

---

## 5 Anticipated Probes + Answer Directions

### Q1: "你 manager 拿不到 PD quota 让你独自扛 -- 那个时候你为什么没 push back, 为什么没拒绝 take 一个没 cross-team 支持的 release?"

**应答方向 (这是最危险的问题, 不要 deflect 到 'manager said so')**: 不要答 "manager 安排我就做", junior 答案 = abdication of agency。答: "Push back 是有的, 但不是拒接。我 raise 的是 'this carries hidden coupling risk, we should at least flag it to the counterpart team's senior IC informally'。我 manager 的判断是 -- 我们 latency optimization 的窗口期就这一个 quarter, 等 quota approval 会错过, 让我用 release-by-DC 控 blast radius。我接受了那个 framing, 因为 manager 的 risk-reward 判断在 her scope 是合理的。但 *接受 framing 不等于免责* -- 我 picked it up, 后果 (DC2 panic + 1/3 quarter 修复) 也是我的, 不是 manager 的。如果 redo, 我会 push 一步: '即使 informal, 我 ping 对方 senior IC 30 分钟, 拿一个 sanity check'。这一步当时我没做, 是 *I should have*, 不是 'manager should have made me'。"

### Q2: "你说 RCA 的时候没 point at counterpart team -- 但他们 migration half-done 是结构问题, 不 surface 不就是 over-correction, 让 org 学不到 lesson 吗?"

**应答方向 (discipline-vs-self-flagellation, L5 要 own choice 不是 retreat)**: "Fair distinction。我没 point at them in *the blame allocation*, 但我 *did surface* the structural finding -- senior IC 和我 joint debug 的发现 (declarative artifactory 下面是 statically-compiled C++) 完整写进了 RCA, 那段 fact 没 hide。我 *没* 做的是 in-meeting framing 'this happened because their migration was incomplete' -- 那个 framing 即使 technically true, 在 RCA 当下会让 director 默认是 finger-pointing, structural finding 会被 read 成 deflection。我把 fact 留在 doc, framing 上 own context gap, 是为了让 finding 被听见。Org-level lesson 也确实 learned 了 -- new policy (cross-team senior approver) 至今 in effect, 这是 finding 被 institutional internalize 的证据。Self-flagellation 那个 read 我 reject, 这是 sequencing decision 不是 over-correction。"

### Q3: "1/3 quarter 是真实的 cost -- 你 manager 当时怎么 react, 你做了什么 rebuild trust *with her*, 不止是和对面 team?"

**应答方向 (manager-relationship probe, 大部分人忽略这一面)**: "好问题, 这一面我平时讲 story 时确实没主动 surface。Manager 的 reaction 是 mixed -- 一方面她 own 了她的 staffing decision (no PD quota 时让我 solo carry), 没把 outcome 推给我; 另一方面我能感觉到 weekly 1:1 里有 trust recalibration -- 后续 cross-team 的项目她会更 hands-on 一些, 不会再 'pick it up solo' 那个 default。我 rebuild 的方式: (1) 主动把 incident retrospective 翻成 next-quarter 的 risk register input, 不让她代我 carry。(2) 后续 quarter 我 self-impose 更 conservative 的 scope, 把 delivered impact 拉回 baseline, 让她重新校准 'what can be trusted to him solo'。大概两个 quarter 之后 default 才回到 incident 之前。"

### Q4: "你 policy 给每个 cross-team change 加 friction -- 怎么知道这个 friction 值得, 怎么 measure 它真的在 catch 东西而不是单纯 slow down team?"

**应答方向 (policy-cost, 不要 dodge 'all policies look good in retrospect' 陷阱)**: "Honest answer -- 我们没建 rigorous measurement, 这是 policy 的真实 weakness。可以 point 的 evidence 是 indirect: (1) policy 后两年, 同 class incident (cross-boundary structural surprise) recurrence rate 降到接近零 -- 但 attribution 弱, 因为同期 migration 也在推。(2) Approver 反馈里, 'caught 一个潜在 issue' 的 self-report 在 ~15% 的 review 出现, 这是 lower bound。(3) Friction cost 我们没 measure -- engineer 抱怨过 review turnaround 慢, 但没 quantify lost-velocity。如果 redo policy, 我会 build in counterfactual sampling -- 一小部分 cross-team change 走 light-touch path 做 control arm, 让 policy ROI 可 measure。这是 policy design 我事后看的 gap。"

### Q5: "你 frame 这个 lesson 是 'counterpart bandwidth as a line item', 但更 aggressive 的 framing 是 '不要 take 没 formal allocation 的 cross-team work'。为什么不是后者?"

**应答方向 (lesson-aggressiveness, L5 要 defend lesson 的 calibration)**: "因为后一个 lesson 在 organizational reality 里是 actionable=zero。'Don't take work without formal allocation' 听着 disciplined, 实操是 -- L4/L5 engineer 经常被 ask 接 cross-team work without formal quota, 拒了你不是 disciplined, 是 *not delivering*, 那个 cost 也是真实的。我的 lesson 是 calibrated 在 'when I do take it, what's the minimum risk-mitigation step' -- informal counterpart-IC ping。这个 step 是 cheap, 不需要 quota, 不需要 manager approval, individual IC 可以 unilaterally 做。Cheap-and-individually-actionable 是 lesson 能 stick 的 prerequisite。'Don't take work' 那个 framing 听着对, 但下次同样情况发生我还是会 take it, lesson 没 surface area。我选了能让自己 behavior 真的 change 的那个 framing。"

---

## 口述 Delivery 提醒

- **NRG-v2 的 four high-signal beats** 严格 pace:
  1. "DC2 panicked out within minutes" 之后停一拍, 让 failure 落地, 再说 "the rollback was mine"。
  2. "Neither of us had known" 之后停一拍, 再讲 RCA reveal -- surprise 是 the point。
  3. "I didn't" (deflection-choice 那段) 之后短停。
  4. Lesson 句之后立刻停。

- **"I picked it up"** 不是 "she dumped it on me"。NRG-v2 明确要求 emphasis 在 agency。Manager-opener 是 context, 不是 excuse。

- **"Counterpart bandwidth isn't a favor I should feel awkward asking for --- it's a line item I plan around."** 这句是 lesson 的 punchline, "line item" 那两个字重读。

- **Risk-statement 里 "minefield" 那个 metaphor** 如果在 risk-deep 问题被追问 (PS-6 / OWN-6) 才用, 不要在主 narration 里说, 容易 over-dramatize。

- **Multi-question routing 严格执行 NRG-v2**:
  - 纯 failure 题 (failure_setback / ADP-5 / ADP-15): 收在 "line item" lesson, 不展开 calculated-risk arc。
  - "What would you do differently" (ADP-12): 以 line-item lesson 开场, policy 是 mechanism。
  - Calculated-risk / bold-risk (PS-6 / OWN-6): frame risk 为 take cross-boundary solo without budgeted support, 接受 mixed outcome (clean DC1, broken DC2, durable structural lesson)。
