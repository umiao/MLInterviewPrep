# Behavioral Q-Example Link Spot-Check (T-P2-356)

Generated: 2026-04-11 12:44
Seed: 20260411
Sample size: 10

## Reviewer instructions

For each link, mark **exactly one** decision box with `[x]`. If you choose `update-note`, fill the fenced `text` block under **Updated relevance_note** with the replacement text. Leave unchecked entries untouched -- the apply step will skip them.

Do not edit or remove the `<!-- link_row_id: N -->` markers. They are the machine-parseable anchors used by apply mode.

---

### 1. ADP-15 -> EX-05
<!-- link_row_id: 20 -->

- **Question**: What's the biggest lesson you've learned from a failed project?
- **Example title**: Relevance Filtering: Deployment Feasibility Under Latency Constraints
- **Situation**: As tech lead and sole MLE on a relevance filtering project, my team spent two months building a high-accuracy XGBoost model with thousands of trees. At deployment time, we discovered the model added +10% latency overh...
- **Result**: Shipped the feature meeting the <=1% latency target. GMB on null/low-intent queries improved +4-6%. The cheap rejection + early exit pattern was later reused for two other model deployments. The silent failure lesson...
- **Current relevance_note**: Biggest lesson: define deployment envelope (latency, payload limits, system coupling) before model design

**Decision** (mark exactly one):

- [ ] keep
- [ ] drop
- [x] update-note

**Updated relevance_note** (fill only if update-note):

```text
Biggest failure lesson: we over-built a thousands-of-trees XGBoost by implicitly pattern-matching on other teams' model-depth trend, without first checking whether our own problem shape justified it. Our traffic distribution showed 80%+ of requests did not need the big model at all -- cheap rejection + early exit replaced it. Meta-lesson: do not anchor architecture decisions to cross-team envy or adopted-tech imitation. Anchor to your own problem assumptions, data distributions, and application scenarios.
```

---

### 2. COL-8 -> EX-23
<!-- link_row_id: 170 -->

- **Question**: Describe a time when you managed expectations for multiple stakeholders.
- **Example title**: Large-Scale Project with Tight Deadlines --- NYC C2C Policy Launch
- **Situation**: Our NYC C2C business had been declining for weeks as competitors captured market share, and the VP demanded a test within 2 weeks and a launch proposal within 1 month -- with 30+ people across the org needing to coord...
- **Result**: Project **delivered within the VP's deadline**. More critically, I prevented the team from making a costly mistake: blindly combo-launching all policies would have shown disappointing results (policies canceling each...
- **Current relevance_note**: Managed VP expectations on timeline and scope while coordinating with multiple technical teams

**Decision** (mark exactly one):

- [x] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 3. EXE-5 -> EX-23
<!-- link_row_id: 159 -->

- **Question**: Tell me about a time when you managed a large-scale project with tight deadlines.
- **Example title**: Large-Scale Project with Tight Deadlines --- NYC C2C Policy Launch
- **Situation**: Our NYC C2C business had been declining for weeks as competitors captured market share, and the VP demanded a test within 2 weeks and a launch proposal within 1 month -- with 30+ people across the org needing to coord...
- **Result**: Project **delivered within the VP's deadline**. More critically, I prevented the team from making a costly mistake: blindly combo-launching all policies would have shown disappointing results (policies canceling each...
- **Current relevance_note**: Managed 30+ person project under VP 2-week test deadline

**Decision** (mark exactly one):

- [x] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 4. ADP-6 -> EX-05
<!-- link_row_id: 218 -->

- **Question**: Tell me about a project that started with a lot of ambiguity. How did you navigate it?
- **Example title**: Relevance Filtering: Deployment Feasibility Under Latency Constraints
- **Situation**: As tech lead and sole MLE on a relevance filtering project, my team spent two months building a high-accuracy XGBoost model with thousands of trees. At deployment time, we discovered the model added +10% latency overh...
- **Result**: Shipped the feature meeting the <=1% latency target. GMB on null/low-intent queries improved +4-6%. The cheap rejection + early exit pattern was later reused for two other model deployments. The silent failure lesson...
- **Current relevance_note**: Project started with ambiguity about what 'deployment feasibility' even meant -- expanded from model-layer to full system coupling

**Decision** (mark exactly one):

- [x] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 5. OWN-4 -> EX-23
<!-- link_row_id: 165 -->

- **Question**: Tell me about a time when you had to take responsibility for a team's performance.
- **Example title**: Large-Scale Project with Tight Deadlines --- NYC C2C Policy Launch
- **Situation**: Our NYC C2C business had been declining for weeks as competitors captured market share, and the VP demanded a test within 2 weeks and a launch proposal within 1 month -- with 30+ people across the org needing to coord...
- **Result**: Project **delivered within the VP's deadline**. More critically, I prevented the team from making a costly mistake: blindly combo-launching all policies would have shown disappointing results (policies canceling each...
- **Current relevance_note**: Took responsibility for 30+ person team performance and VP-level delivery

**Decision** (mark exactly one):

- [ ] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 6. ADP-18 -> EX-17
<!-- link_row_id: 94 -->

- **Question**: Tell me about a recent mistake you made and what you learned from it.
- **Example title**: Difficult Feedback from Senior IC --- Building Credibility
- **Situation**: A senior IC gave me harsh feedback -- saying I "lacked basic engineering quality" -- after a researcher I was supporting made late naming changes that broke a build on a PR I had verified, and the senior IC refused to...
- **Result**: **Built mutual respect** with the senior IC and became good professional friends. We both became known in the org for rigorous checklist adherence and fast response times. The engineer-researcher collaboration policy...
- **Current relevance_note**: Learned from mistake: PRs should always be engineer-owned, improved collaboration process

**Decision** (mark exactly one):

- [ ] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 7. INN-13 -> EX-21
<!-- link_row_id: 155 -->

- **Question**: How do you approach improving a well-established but inefficient process?
- **Example title**: Tech Debt Balance --- Declarative Artifactory Proof of Concept
- **Situation**: Features I was building required the team's new declarative artifactory system, but that system was repeatedly delayed with no clear timeline -- blocking feature delivery that the business needed now.
- **Result**: Feature **shipped on time** with business win, rather than being blocked for a year. When the declarative system finally became ready, migration was smooth -- the core expression implementation was already consistent,...
- **Current relevance_note**: Improved well-established but manual Artifactory config process with declarative PoC

**Decision** (mark exactly one):

- [ ] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 8. IMP-9 -> EX-21
<!-- link_row_id: 157 -->

- **Question**: How do you weigh short-term gains against long-term goals?
- **Example title**: Tech Debt Balance --- Declarative Artifactory Proof of Concept
- **Situation**: Features I was building required the team's new declarative artifactory system, but that system was repeatedly delayed with no clear timeline -- blocking feature delivery that the business needed now.
- **Result**: Feature **shipped on time** with business win, rather than being blocked for a year. When the declarative system finally became ready, migration was smooth -- the core expression implementation was already consistent,...
- **Current relevance_note**: Weighed short-term manual config against long-term declarative approach

**Decision** (mark exactly one):

- [ ] keep
- [x] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 9. IMP-13 -> EX-20
<!-- link_row_id: 153 -->

- **Question**: Tell me about a time when you had to make a tough ethical decision on a project.
- **Example title**: Seller Risk Modeling Fairness --- Ethical Dilemma and Escalation
- **Situation**: While reviewing risk guardrails, I discovered our seller risk model systematically penalized new sellers -- they received high risk scores with zero transaction history, creating a vicious cycle where they could never...
- **Result**: Leadership reviewed both perspectives, **collaborated with legal department**, and confirmed the precision modeling direction -- evaluating sellers through listing quality cross-modeling rather than blanket penalties....
- **Current relevance_note**: Escalated ethical concern about seller risk model fairness rather than shipping known-biased model

**Decision** (mark exactly one):

- [x] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---

### 10. IMP-5 -> EX-03
<!-- link_row_id: 13 -->

- **Question**: How do you approach defining success for a project?
- **Example title**: Challenging Sale NDCG Proxy — First Principles Rethinking
- **Situation**: Our search ranking team was optimizing Sale NDCG -- an industry-standard metric -- but I discovered it systematically prioritized cheap items over expensive ones, causing a \$100 necklace to rank below \$5 accessories...
- **Result**: Switching to GMB proxy fundamentally improved ranking behavior. High-quality, authenticated listings saw significant GMB uplift, and the insight that **"proxy selection is the most underestimated ML decision"** became...
- **Current relevance_note**: Redefined what success means for ranking: GMB over Sale NDCG

**Decision** (mark exactly one):

- [x] keep
- [ ] drop
- [ ] update-note

**Updated relevance_note** (fill only if update-note):

```text

```

---
