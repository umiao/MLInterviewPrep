# EX-30 (Hash Capability Misdesign) — Probe Q&A + Delivery Notes

This file holds **interview prep material** for EX-30, kept separate from the
DB-stored STAR fields (which are the interview-ready content). DB carries
title/situation/task/action/result/risk + a compact NRG-v2 with pacing cues;
this file carries the full set of anticipated probes + answer directions +
delivery cues used during practice and live delivery prep.

Per user's explicit request 2026-04-21 (Discord msg 1496054494696575056):
"中英混合也不需要去多改" — content is preserved in user's original
Chinese-English mixed style for delivery prep purposes.

Linked story: `behavioral_examples.example_id='EX-30'` (id=30).
Themes: failure_setback / conflict_disagreement / mentoring_coaching /
scope_creep_ambiguous.

---

## 5 Anticipated Probes + Answer Directions

### Q1: "You said the rescue was self-centered. Walk me through what changed your mind."

**应答方向**: 不要答"有人劝我"。答: "被拒之后我把 cost-benefit 重新算了一遍, 从 org 视角不是我的视角。Benefit 主要归我——保留我的设计。Cost 分散到四个团队, 还撞他们的 high-priority project。这个账在我个人视角算得通, org 视角算不通。这个视角切换是我自己做的, 但 proposal 被拒是那个触发点。"

### Q2: "Why didn't you ask the indexing team before you designed this?"

**应答方向 (这是最危险的问题, 直球答)**: "Fair question。我当时的 frame 是 hash 作为 math object, indexing team 在我心里是不同 domain。现在我知道 output 的 consumer surface 决定 prior art 在哪里, 不是 domain 标签。这是我 design habit 里现在前置的一步。"

### Q3: "You mentioned the orphan design later leaked as experiment-level confounding. Tell me more."

**应答方向**: 这就是你的 L5+ 弹药仓。展开讲你自己发现 every vertical 都 green 反常 → 反向检验 → 发现 page-level treatment spillover → 尝试 day-by-day 和时段切换 mitigation → too noisy → 这个限制让你意识到 orphan 状态的第二种 leak。这段只在被 probe 时讲, 不主动开。

### Q4: "If you redid day 1, what would you do differently?"

**应答方向 (避免 junior 答案 "先问 DS")**: "我会先问一个问题——这个设计的 output 会进入谁的决策路径。不是 'who might use it', 是 'whose decision depends on this'。DS 的 launch analysis 是决策路径, 他们是 day-1 stakeholder。其他下游可能是 latent consumer, 可以 agnostic。这个区分是我现在 design 的第一步。"

### Q5: "What did your team change after this?"

**应答方向 (L5 不要求 team-level change, 诚实答)**: "团队流程我没有推动改变, 这不是我的 scope。我自己的 design 动作改了, 就是 Q4 里讲的那个前置问题。我也开始主动学 Netflix 这类 platform 在 experimentation infra 上的做法, 在 design review 时引用。"

---

## 口述 Delivery 提醒

- **"It was rejected. And this is where I stopped."** 这两句之间停一拍。这是你的 slow-down moment, 用呼吸标记它。面试官会记住这个停顿。

- **"By my hash-expert standard, it was worse. By the DS consumer standard, it was traceable and auditable."** 这两句并列, 语速放慢。这是 lesson 的具象化。

- **Lesson 那句 "Domain depth is not design authority"** 讲完立刻停。不要补 "so I learned that..."。Crisp lesson 的规则是讲完即止。

- **Risk if not addressed 段不是补充, 是升华**。语气要稳, 不要快。这段在展示你能把个人 failure 抽象成 structural risk, 这是 L5 bar 的关键动作。
