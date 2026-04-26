# EX-17 (Difficult Feedback from Senior IC --- Reliance vs. Trust) --- Probe Q&A + Delivery Notes

This file holds **interview prep material** for EX-17, kept separate from the
DB-stored STAR fields (which are the interview-ready content). DB carries
title/situation/task/action/result/risk + an NRG-v2 narration guard;
this file carries the full set of anticipated probes + answer directions +
delivery cues used during practice and live delivery prep.

Style follows the 2026-04-21 user direction (Discord msg 1496054494696575056):
"中英混合也不需要去多改" --- content kept in 中英混合 style for delivery prep.

Linked story: `behavioral_examples.example_id='EX-17'` (id=21).
Principle tags: adaptability / ownership / failure / humility /
have_backbone / frame_ownership / earn_trust / restraint.

---

## 5 Anticipated Probes + Answer Directions

### Q1: "你拒了 manager 帮你 explain --- 但 manager 是 set the framing 的人。只 own 自己的 blame, 是不是变相 protect 她, 反而让 org learn 不到 lesson?"

**应答方向 (这是最危险的问题, 直球答 manager-protection inversion)**: 不要答 "我不想给 manager 添麻烦", junior 答案 = 把 character signal 弱化成 deference。答: "这个 distinction 我当时想得很清楚 -- *blame allocation* 和 *organizational learning* 不是同一件事, 我拒的是前者, 不是后者。Manager 的 framing 'researcher owns deep context, you only do surface review' 是个 process gap, 这个 gap 我后来在 team retrospective 里 explicitly raised, lessons 入了 team practice (engineer-researcher ownership boundary)。所以 org learning 是 happen 了, 只是不在 senior IC 那一刻 happen。我拒 manager protection 是因为 -- 在 senior IC 当下的 frame 里, 'engineer caught in bad setup' 这个 narrative 一旦被她讲, 我下次又被同样 setup 时还是会 cave, 因为 organizationally 我 learned 的是 'manager 会替我兜', 不是 'I should have held the gate'。Org learning 走 retrospective 通道, individual learning 必须我自己 carry, 这两个 channel 不能合并。"

### Q2: "你说 'reliance 不等于 trust' --- 但 senior IC 是因为你 execute manager instruction 而生气。真正的 failure 不是 manager 的 process 坏了吗, 不是你的 gate-keeping?"

**应答方向 (reframe-the-blame, L5 要 reject 这个 escape hatch)**: "Tempting reframe, 但 false。Manager 的 framing 是 sub-optimal, 是的; 但 org policy 是 explicit -- engineer owns their PR, 那条 policy 我 aware, manager 的 framing 不能 override policy。Senior IC 生气的不是 'CI broke', 也不是 'manager set bad framing', 是 'you executed an instruction that bypassed policy you knew, and you didn't push back on the framing'。这个 attribution 准确 -- failure point 在我 *accepted the framing* 那一刻, 不在 manager *提出 framing* 那一刻。Manager process 是 contributing factor; gate-keeping 缺失是 *proximate cause*。Senior IC 的 anger 是 calibrated 在 proximate cause, 这是他作为 reviewer 的 correct read。如果我 accept 'manager process 是 root cause' 这个 reframe, 我就不需要改任何自己的 default, 这个 lesson 等于没学。"

### Q3: "2 个月 rebuild trust, 'consistency, no grand gestures' --- 这是 vague claim。week-by-week 你具体做了什么?"

**应答方向 (specificity 检验, 不要含糊带过)**: "拆开讲: Week 1-2: 主动 ping senior IC 问 'next time you review my PR, what specific gate would you want me to apply', 拿到具体 checklist (ownership scope, naming convention check, test coverage on touched modules)。我开始 every PR self-apply 然后 explicit 写在 PR description, 让 reviewer 不需要 reverse-engineer 我有没有 review。Week 3-6: Manager-mediated review -- 每个我 author 的 PR 先走 manager 一轮 walk-through, 再 ping senior IC, 让 he sees 我已经过了一道独立 gate, 不是 raw output。Week 7-8: Manager 退出 mediation, 我直接 send PR, senior IC 开始 incremental engage -- 第一次只 comment 不 block, 第二次 normal review, 第三次他主动 ping 我 review 他的。On-call: 我那两个月把 on-call rotation 接得密, 凌晨 alert 我 first responder, 让 'reliable under pressure' 那个 baseline 不掉。这些都是 small repeated signals, 没单独一个是 grand gesture, 加在一起 cover 2 个月。"

### Q4: "Lesson 学到之后, 你后来有没有真的对 manager instruction 说过 'no'? 给一个具体例子, 不然 lesson 没 stick。"

**应答方向 (behavior-change validation, 这是 lesson stickiness 终极检验)**: "有, 一次。后来 quarter-end crunch, manager ask 我接一个 model rollout, 类似 setup -- another team's branch, 我 surface review only。我直接 push back: 'I will do surface review, but I am not signing off as PR author --- if I am the merge gate I need ownership scope, otherwise the original author or a researcher with deep context needs to be co-author or the PR sponsor'。Manager 当下 friction 是有的, 但我没让步。最后 resolution: original team 的一个 senior 进来做 co-author, 我做 surface review, merge gate 双签。这个 push-back 是 EX-17 lesson 唯一 hard test -- 如果我 cave 了, lesson 没学到。Cave 的诱惑当时是有的 -- 'manager 不高兴' 那种 organizational discomfort 比 'next senior IC anger' 那种 hypothetical 风险 immediate, 所以这一次 hold 是真实的 cost。我能讲这个例子, 是 lesson stick 的 evidence。"

### Q5: "Senior IC 可以 escalate 给你 manager, 他 chose 拒 review。这告诉你他在 read 什么? 你换位会怎么做?"

**应答方向 (empathy-through-counterpart, L5 要能 reconstruct 对方 frame)**: "他的 read 我事后想是 -- escalate 是 management problem, 但 gate-keeping 是 individual-engineer 的 character 问题, character 问题不是 manager fix 的, 是 engineer 自己 fix 的。他拒 review 是 forcing function -- 让我没退路, 必须自己面对 'I executed without owning'。Escalate 给 manager, manager 会做 process change (e.g. 加 review checklist), 但我个人的 default 不会变, 下次同样 pressure 我还是会 cave。他 choose 用最 expensive 的 mechanism (refusing review = blocks the merge = cost 落到我 quarter delivery 上) 来 trigger character-level change, 不是 process-level fix。这是 senior IC 的 mentorship choice, 不是 anger -- anger 会 escalate, mentorship 会 force introspection。换位我会做同样选择, 只是我现在能 articulate 这个 distinction, 当时只能 react。"

---

## 口述 Delivery 提醒

- **NRG-v2 三个 high-signal beat** 严格 pace:
  1. "I declined." 单句一行, 讲完停一拍。这是全 story 最强 character signal, 不能含混带过。
  2. "He was right to" 之后停一拍, 再说 "My explanation was technically accurate and completely beside the point。" 这个 admission 需要 space。
  3. Lesson "They're different" 之后短停, 不要补 "and that's why..."。

- **"Reliance means the team needs your hands. Trust means the team believes you'll hold the line."** 这两句 parallel 结构, 语速放慢, 是 lesson 的 crystallization。

- **"Second-order outcome" (teammates inviting reviews)** 那段语气保持 flat。NRG-v2 明确说 -- 这是 process behavior change 不是 popularity recovery, 不要 warm tone, 不要 implied 'good professional friends' 那种 redemption-arc。

- **如果是 COM-5 ("disagreed-with feedback")**: 开场必须 "I initially wanted to push back with technical context", 然后 reveal 自己的 maturation。直接讲 lesson 会显得 too-rehearsed。

- **如果是 OWN-3 / ADP-19 / ADP-17 (handle / seek / grow-from feedback)**: 以 gate-keeping insight 作为 actionable lesson 开场, 不是 reliance-vs-trust framing。后者是 abstract, 前者是 hands-on takeaway。

- **Manager-decline beat (拒 manager protection) 不要 soften**。"I declined" 是 character signal 锚点, 不要补 "she was being kind" 之类的 cushion -- cushion 会把 backbone signal 弱化。
