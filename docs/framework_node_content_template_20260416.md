# framework_node Content Template — Phase 0.5 Deliverable

**Status**: Template v1, pending user review
**Supersedes**: §3–§5 of `docs/knowledge_graph_design_20260416.md` (data model / link convention / visualization). Those concerns become Phase 4+.
**Why this exists**: KG design v1 and its reviewer both optimized the wrong axis. User's actual goal is per-node **one-stop coverage + progressive disclosure**. This template defines the shape a single framework_node page should take, so "what goes on this page" and "how deep to go" stop being authoring guesses.
**Date**: 2026-04-16

---

## 1. The Contract a Node Page Makes With Its Reader

A reader landing on `/framework/{id}` should be able to say, within 60 seconds of reading the always-visible section:

> *"I know the 80% that an MLE interview at my target level would ask about this topic, and I know what I'd click to expand if they pushed me on the remaining 20%."*

Everything in this template exists to make that contract enforceable and uniform across the 47 existing nodes.

---

## 2. Granularity Rule (when to split vs when to consolidate)

The biggest authoring question this template resolves. Principle: **a node is a unit that an interview would ask about as one question.**

### 2.1 Create a new node if ANY of these hold

- **Distinct interview question**: "Do you know X?" where X is a topic the interviewer would name as one. (Bias-Variance is one. Overfitting is NOT a separate node — it's a drawer tab inside Bias-Variance.)
- **Distinct domain vertical**: LLM pretraining, Tree models, Learning-to-Rank, Computer Vision, RecSys retrieval, RLHF — these are verticals an MLE specializes IN, not facets of one framework. Each gets its own page.
- **> 1 page of unique content** that doesn't reduce to "see node Y".
- **Separable prerequisite stack**: the topic's prerequisites don't overlap significantly with the candidate parent node.

### 2.2 Consolidate into an existing node's drawer if ALL of these hold

- Shares mathematical framing with the parent (e.g., CLT / LLN / hypothesis testing all live under Probability Fundamentals; they don't each need a page unless the depth exceeds typical MLE scope).
- The consolidated always-visible fits under ~3000 bytes without losing the 80% contract.
- The subtopic stands naturally as a drawer tab (`derivation`, `variants`, `code`, etc.).

### 2.3 Worked granularity examples

| Candidate topic | Decision | Reason |
|---|---|---|
| Bias-Variance / Overfitting / Underfitting | **One node** (existing node 67) | Same interview question; overfitting → drawer tab `variants` |
| Logistic Regression / Softmax Regression | **One node** | Same framework; softmax → drawer tab `variants` |
| LR / Decision Trees / Random Forest | **Separate nodes** | Different interview questions, different algo families |
| Transformer self-attention / multi-head attention | **One node** (existing node 141) | MHA is an extension of self-attn, same question |
| BERT / GPT / LLaMA | **Separate nodes** (existing 148/149/150) | Different architectural traditions, different questions |
| CLT / LLN / Markov inequality | **One node** "Probability Inequalities & Limit Theorems" — if new | Shares framing; each becomes a drawer tab. **Unless** user expects deeper treatment for some specific role. |
| LLM pretraining / RLHF / SFT / LoRA | **Separate nodes** (existing 151–154) | Each is a distinct research + interview topic |
| LambdaRank / LambdaMART | **One node** | Same algorithm family, MART is the extension |
| Learning-to-Rank (pointwise/pairwise/listwise) | **Separate from LambdaRank** | Broader framing; LambdaRank is one instance under listwise |

### 2.4 User's explicit granularity guidance (captured verbatim)

> "LLM - TreeModel - Learning To Rank 各种 domain knowledge 必定不能放在一起或者一个单一的 page; 而 statisticals 如果不太复杂 我希望能集成进一个 page 除非情况超出了我的控制或者对 MLE 的一般要求"

Operational translation: **domain verticals split, foundational horizontals consolidate**. When in doubt, ask: would an MLE specializing in the parent skill vertical already know this subtopic implicitly? If yes → drawer. If no → new node.

### 2.5 Escape hatch for consolidated nodes (Q8 follow-through)

The consolidation principle (§2.2, §2.4) is intentionally aggressive for pillar7 (Math/Stats) — target ~5 canonical nodes rather than ~15 granular ones. But if a specific interview genuinely demands depth that exceeds a consolidated node's always-visible budget (§3.1's 3000b) AND cannot fit a drawer tab (§4.1.1's 1.2× overflow rule), split opportunistically at that moment. Examples where this escape hatch is likely to trigger:
- A/B-test peeking correction (if a role deep-dives beyond typical MLE scope)
- Specific Bayesian inference procedures if a Bayesian-modeling role demands more than one MCMC variant
- Rare estimator families (e.g., M-estimators, U-statistics) outside general MLE expectation

Rule: consolidation is the default; split is the signal-triggered exception, never pre-emptive.

---

## 3. Always-Visible Section Schema (the 80% contract)

Every framework_node.description, when rendered, leads with these 5 sections **in this order**. Size budget: combined ≤ 3000 bytes. Chinese prose; English for math, algorithm names at first use, and complexity notation.

### 3.1 `## 一句话定义 + Intuition`
- 2–4 sentences. The pitch you'd give in an interview's first 30 seconds.
- Includes the concept's first-principles motivation, not just its definition.
- Example: *"Bias-Variance tradeoff 说的是模型预测误差可分解为 bias²（欠拟合） + variance（过拟合） + irreducible noise；正则化和模型复杂度的选择，本质上是在这三项之间做权衡。"*

### 3.2 `## 核心公式 / 算法骨架`
- 1–3 formulas maximum, each with 1-sentence gloss.
- If the concept is algorithmic, a ≤ 20-line pseudocode block (not full implementation — that goes in drawer).
- Use LaTeX (`$...$` inline, `$$...$$` display).
- **Statement of result only — no derivations.** §3.2 writes the conclusion (equation + conditions for validity in one line). Any "因为…所以…" / "by Markov..." / "because this term goes to zero..." chain belongs in drawer `derivation`. This rule prevents §3.2 and drawer.derivation from overlapping; a reader who only reads always-visible should see WHAT is true, and click `derivation` when they need WHY.

### 3.3 `## Tradeoffs & 常见误解`
- 3–5 bulleted items.
- Each item = one axis of tradeoff OR one misconception with correction.
- No full derivations; if a point needs one, put it in drawer and link.

### 3.4 `## 面试常见问法`
- 2–3 question framings you've actually seen (or realistically expect).
- For each: 2–3 sentences of response skeleton.
- Tags the company if known (e.g., `[Google L5]`, `[Pinterest Senior MLE]`).
- **Sourcing tag required (one of three, mandatory)**. Every framing must carry one of these markers so PR review can distinguish documented interview content from speculation:
  - `[实际来自: doc-{id} §{section}]` — the framing is attested in an existing `company_document` (paste the doc id and section heading).
  - `[改编自: {source}]` — adapted from a named source (e.g., `[改编自: Etsy 2020 SIGIR position-bias talk]`, `[改编自: Google DNN/Key Papers Gist]`).
  - `[预期问法: {reasoning one-liner}]` — explicitly speculative; include the reasoning (e.g., `[预期问法: Pinterest 从卡片尺寸约束出发反问 CLIP patch size]`). This tag forces the author to own the guess instead of laundering it as fact.
- A framing missing its tag is a PR block. This rule also surfaces as a secondary signal: a node with many `[预期问法]` tags and few `[实际来自]` is under-sourced and should be deprioritized for canonical status.

### 3.5 `## Prerequisites` *(existing convention, keep)*
- Bulleted list of prerequisite topics, with links to sibling framework_nodes when applicable.
- 3–6 items.

---

## 4. Drawer Content Schema (progressive disclosure)

Everything beyond the always-visible belongs in drawer tabs. **Drawer tabs are optional per node — only create tabs that have substance.** No empty stubs.

### 4.1 Tab menu (canonical names; stable across all nodes)

| Tab key | Tab title (CN/EN) | When to include | Size budget |
|---|---|---|---|
| `derivation` | 完整推导 / Full Derivation | Concept has a non-trivial proof or derivation | ≤ 5000b |
| `code` | 手写实现 / From-Scratch Code | Concept maps to an implementable algorithm | ≤ 5000b (one clean Python block + 3-line commentary per section) |
| `variants` | 变体与边界 / Variants & Edges | Has named variants (Focal vs CE, LR vs Softmax, etc.) or subtle edge cases | ≤ 4000b |
| `interview_deep` | 面试深度追问 / Deeper Interview Angles | The interviewer pushed beyond §3.4's 2–3 framings | ≤ 3000b |
| `see_also` | 相关链接 / See Also | Cross-refs: sibling framework_nodes + company-doc back-links | ≤ 1500b |
| `history` | 历史与出处 / History & References | Seminal papers, authors, year, industry adoption | ≤ 1500b |

### 4.1.1 Budget overflow as split signal

A drawer tab that runs consistently **> 1.2× its §4.1 budget** (i.e., ~20% over) is treated as a signal — the subtopic wants to become its own framework_node rather than a tab. This is the operational link between drawer-budget discipline and §2 granularity rule: drawers cap the cost of progressive disclosure; when the cap binds twice on the same tab, split.

### 4.2 What does NOT belong in a drawer

- Content that duplicates §3.1–§3.4 verbatim. Each drawer tab must add depth, not restate.
- Cross-node content. If a sub-topic gets long enough to warrant its own structure, it wants to be its own node (§2).
- Marketing prose. Drawers are reference material, not tutorials.

### 4.3 Author-facing rule

> Write the always-visible first. Only add a drawer tab when you catch yourself wanting to say *"but actually, if you push me on that..."* That's the signal. If you never hit that signal, the node needs no drawer at all.

---

## 5. Drawer Content Mechanism (how it lives in the DB)

**Decision**: use **markdown heading convention inside `framework_node.description`**. No new table, no new column, no HTML comments.

### 5.1 Convention

```markdown
# {Node Title}

## 一句话定义 + Intuition
...

## 核心公式 / 算法骨架
...

## Tradeoffs & 常见误解
...

## 面试常见问法
...

## Prerequisites
...

<!-- ============ DRAWER BELOW ============ -->

## Drawer: derivation
...

## Drawer: code
...

## Drawer: see_also
...
```

### 5.2 Why this mechanism

- **Zero schema change**: the current `framework_node.description TEXT` column holds everything.
- **Markdown-degrades-gracefully**: a plain markdown viewer (or the current /framework/N page today) still renders everything — drawer tabs just appear as additional H2 sections.
- **Simple parser**: frontend splits on `## Drawer:` to populate drawer tabs; everything before the first such heading is always-visible.
- **Author writes one document**: no context switches between columns.
- **Scope-creep protection**: adding a tab that isn't in §4.1's menu fails code review; frontend only renders known tab keys.

### 5.3 Frontend implication

- Render always-visible content normally in the page body.
- Below it, a drawer component (shadcn `Collapsible` or `Accordion` already in frontend dependencies — verify) shows each `Drawer: {key}` as a collapsed tab.
- Tabs render in the §4.1 canonical order, regardless of author's markdown order. **(Note: the canonical render order is deferred to v1.1 pending Sketch-sample signal — see Revision Log.)**
- **Parse-marker rule**: `## Drawer: {key}` headings are markdown parse markers only. The frontend drawer component MUST NOT re-render the `## Drawer: {key}` heading inside the tab content body — the tab title is already shown by the drawer UI. Double-rendering the heading inside the body is a bug. Main page body similarly must not render any content from below the first `## Drawer:` marker.
- If no `## Drawer:` headings exist, the drawer component does not render at all (empty stub suppression).

---

## 6. Writing Rules

### 6.1 Language

- Prose: **Chinese by default** (follows `feedback_lc_notes_chinese.md`).
- **English preserved**: math (LaTeX), code blocks, algorithm names at first mention followed by Chinese gloss (`LambdaRank（λ 排名）`), complexity notation (`O(n log n)`), library names.

### 6.2 Cross-linking

- When an always-visible sentence references another canonical concept, link it inline:
  `...详见 [Bias-Variance](/framework/67) 的 variance 项...`
- When a company document is the source/inspiration for a drawer tab's content, mention it in prose:
  `(此视角源自 Pinterest senior MLE 复习的 sketch/streaming 1-pager)`
- **No machine-parseable comments** (no `<!-- KG:67:reference -->`). If a graph view is built later (Phase 4+), a regex + LLM pass can extract these on demand.

### 6.3 Company back-links (in the `see_also` drawer only)

- Form: `- [{Company}]({company_doc_url}) — {short reason}`
- Curated by human during consolidation, not auto-generated.
- Maximum 4–5 entries per node (taste signal: if more, company docs are under-migrated).

### 6.4 Drawer tab independence

- Each drawer tab is self-contained: a reader who clicks only `code` must not need to read `derivation` first for the code to make sense. Use a 1–2 line preamble per tab if needed.

### 6.5 PR description convention (migration natural queue)

When a migration PR touches framework_node X, the PR description lists **adjacent non-touched nodes** under a `### Next candidates` section:
- **Siblings** under the same pillar (same `parent_id` in framework_nodes).
- **Nodes X references** via inline markdown links in the rewrite.

This builds a natural migration queue without centralized planning — reviewers and future authors can see what's next without guessing, and "adjacent" is objective (not subjective-priority). A migration session is expected to read this list before picking its own target.

---

## 7. Worked Sample — `framework_node 196 Streaming Top-K`

This is the template populated for one node. It becomes the pattern reference.

### 7.1 Always-visible (≤ 3000 bytes)

```markdown
# Streaming Top-K: Compact Sketches 三轴统一视角

## 一句话定义 + Intuition
Streaming Top-K 问题是在单次扫描、亚线性内存的约束下估计流中的频次或基数。工程里看到的 CMS、HyperLogLog（HLL）、Space-Saving（SS）等"名字算法"，不是三个独立解，而是**三个正交设计轴**（hash 来源 / counter 结构 / 聚合算子）上的具体组合点。理解这三轴比背诵算法名更重要——production 的 sketch 几乎都是 composition。

## 核心公式 / 算法骨架
三轴分解：
- **Hash 来源**：flow label（canonical）/ 随机数 Bernoulli per-arrival / 其他维度
- **Counter 结构**：标量 counter（CMS）/ log counter（Morris）/ bitmap register（PCSA、HLL 变体）
- **聚合算子**：幂等 max（→ cardinality）/ 累积 sum-or-set-bit（→ frequency）

CMS 误差界：$\hat{f}(x) \leq f(x) + \varepsilon \|a\|_1$ with probability $\geq 1-\delta$（取 $w = \lceil e/\varepsilon \rceil$, $d = \lceil \ln(1/\delta) \rceil$）。
HLL 标准误：$\sim 1.04 / \sqrt{m}$。

## Tradeoffs & 常见误解
- **CMS 只高估不低估**——跨行 min 压碰撞；CMM 修正后用 median，不再是 upper bound。
- **"HLL" 是 family 还是 instance**：网络测量社区指一个 family；DB 社区严格指 Flajolet 2007 max 聚合实例。跨圈讨论先做 term grounding。
- **Light-flow 误差塌方**：CMS 的 $\varepsilon \|a\|_1$ 对 heavy flow 友好，对 light flow 相对误差爆炸——Bernoulli freq sketch（误差 $\sim \sqrt{f(x)}/p$）互补。
- **饱和是 bitmap register 的主要问题**，靠 m 大 + saturation-aware estimator 处理，不要无脑加 bit 位宽。

## 面试常见问法
1. **"Pinterest trending pins 怎么做？"** 答：CMS 追踪 pin 曝光频次 + min-heap 维护 top-K；每到一条事件更新 CMS 和堆。
2. **"HLL 为什么用调和平均？"** 答：标准算术平均对少数高 register 值过度敏感；调和平均把小值权重放大，对 outlier 鲁棒。
3. **"10GB 流算 distinct count，预算 1MB"** 答：HLL m=2^14 约 16KB 就能做到 <1% 误差，远低于预算；如果是 sliding window 需要 HLL+decay 或 sliding HLL。

## Prerequisites
- 哈希函数与 universal hashing
- 概率尾界（Markov / Chebyshev / Chernoff）
- Pigeonhole 直觉
- 流式计算模型 (single-pass, sublinear memory)
```

### 7.2 Drawer tabs (each ≤ the §4.1 budget)

```markdown
## Drawer: derivation
{CMS 误差界证明 via Markov + 联合界；HLL 调和平均的推导来自 Flajolet 2007; CMM 的 unbiased 估计推导}

## Drawer: code
{CMS 的 from-scratch Python（d 行 w 列，pairwise independent hash）；HLL 简化版；Space-Saving 的 Misra-Gries 变体}

## Drawer: variants
{CMS vs CM (Count-Mean-Min 用 median)、Bernoulli frequency sketch、bitmap register generalization (从 max-only 走回 PCSA)}

## Drawer: interview_deep
{"分布式 top-K 怎么 merge？" CMS 可加性、SS 合并较复杂；"滑动窗口下如何？" 分层 sketch + epoch reset；"cold start？" warm-up via 上一 epoch}

## Drawer: see_also
- [framework_node 197 Scaling & Resource Model](/framework/197) — 把 sketch 放到 L4 coding 框架里
- [framework_node 103 Real-time Feature Computation](/framework/103) — sketch 在 feature store 的应用
- [Pinterest sketch/streaming 1-pager (doc 58)](...) — Pinterest 面试角度

## Drawer: history
- Cormode & Muthukrishnan 2005 "An improved data stream summary: the count-min sketch and its applications"
- Flajolet, Fusy, Gandouet, Meunier 2007 "HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm"
- Metwally, Agrawal, El Abbadi 2005 "Efficient computation of frequent and top-K elements in data streams"
```

This sample is **not** authoritative yet — T-P0-241 delivers the final content. The template is what T-P0-241 will follow.

---

## 8. How This Template Interacts With Existing Phase Plan

Reminder: the KG design doc v1 proposed 4 phases. After this template, phases realign as:

| Phase | Scope | Status after this doc |
|---|---|---|
| **0** (original) | Design review of KG doc v1 | Superseded by this template on §3–§5 |
| **0.5 (new)** | **This template** — authoring schema | **DONE on commit** |
| **1** (original) | DB schema + concept_links + /kg scaffold | **Deferred**: only author-tool (CLI helper) stays; schema + link table punt to Phase 4+ |
| **2** (original) | 3 concept consolidations | **Retargeted**: 1 concept first (Sketch via T-P0-241), validate workflow + template, then 1–2 more |
| **3** (original) | Systematic migration | **Unchanged conceptually**; starts only after Phase 2 workflow is validated |
| **4** (original) | Graph viz + concept_links table | **Unchanged**; remains optional / signal-gated |

Orthogonal concerns that do not block any phase:
- **Google R1 translation**: separate task, deadline-driven, independent of KG work.
- **autonomous_run.sh currently processing T-P0-227..241**: those are gap-fill content tasks, unaffected by this template. They can be rewritten per the template later if needed, but no urgency.

---

## 9. Open Questions (Numbered, Please Reply By Number)

Recommended defaults in **bold**.

1. **Always-visible section count + names**: `一句话定义+Intuition / 核心公式 / Tradeoffs / 面试常见问法 / Prerequisites` (5 sections). Accept or modify?
   - **Default: accept as-is**

2. **Drawer tab menu**: `derivation / code / variants / interview_deep / see_also / history` (6 tabs, all optional). Accept, trim, or add?
   - **Default: accept 6-tab menu**

3. **Drawer mechanism**: markdown `## Drawer: {key}` convention inside `framework_node.description`, parsed at render time — vs a new `framework_node_drawers` table with rows per tab. Recommendation: markdown convention (no schema change, author-friendly, degrades gracefully).
   - **Default: markdown convention**

4. **Size budgets**: always-visible ≤ 3000b; drawer tabs ≤ 1500–5000b per §4.1. Too tight, too loose, or right?
   - **Default: accept**; will revisit after Sketch sample validates.

5. **Granularity rule application**: §2's "interview-question unit" rule. Any concept in your head where this rule misclassifies? (e.g., should Transformer architecture be split further than current nodes 141–147? Should CLT get its own node or stay merged?)
   - **Default: trust §2 for now**; flag anomalies during Phase 2 migration.

6. **Frontend work**: does the drawer UI (Accordion / Collapsible) need a task created now, or wait until after Sketch canonical content exists?
   - **Default: create task but don't start work**; Sketch can validate against inline markdown rendering first.

7. **Existing node migration timing**: do we apply the template to all 47 nodes at once, or opportunistically as each node gets touched in Phase 2+?
   - **Default: opportunistic**; avoid mass-rewrite without user review per node.

8. **Statistics consolidation specifically**: your phrase "statisticals 如果不太复杂 我希望能集成进一个 page". Translation: pillar7 (Math/Stats) gets ~3–5 consolidated nodes (Probability Fundamentals, Statistical Tests, Estimation, Linear Algebra, Calculus/Optimization) rather than ~15 granular ones. Confirm this reading?
   - **Default: yes, consolidate pillar7 to ~5 nodes**; create splits only when depth demands.

---

## 10. What This Doc Explicitly Does NOT Decide

- Whether to build `/kg` graph visualization (Phase 4+ concern).
- Whether to add `concept_links` table (deferred — the markdown inline links are sufficient for now).
- Which specific concepts get consolidated in Phase 2 (beyond Sketch via T-P0-241).
- Translation of Google R1 docs (orthogonal task).
- Any rewrite of the 15 in-flight T-P0-227..241 tasks.

Those each need their own decision point or task.

---

## Revision Log

- **v1 (2026-04-16, earlier)**: Initial Phase 0.5 deliverable. Responds to user review of KG design v1 + third-party reviewer critique; reframes from cross-doc graph to per-node UX contract.

- **v1.0.1 (2026-04-16, later)**: Tightening pass per second reviewer feedback. Critical changes before T-P0-241 Sketch execution:
  - §3.2 adds **"statement-of-result only" rule** — all "because/therefore" chains belong in drawer `derivation`. Closes the §3.2↔drawer.derivation boundary ambiguity.
  - §3.4 adds **mandatory sourcing tag** on every interview framing: `[实际来自: doc-{id} §{section}]` / `[改编自: {source}]` / `[预期问法: {reasoning}]`. Eliminates silent fabrication; missing tag is a PR block.
  - §4.1.1 (new) — **20% budget overflow is a split signal**, wiring drawer discipline to §2 granularity.
  - §5.3 adds **parse-marker rule** — frontend must not double-render `## Drawer: {key}` heading in tab body; main page must not render below first drawer marker.
  - §6.5 (new) — **PR description next-candidates convention** — every migration PR lists adjacent non-touched nodes, building a natural migration queue.
  - §2.5 (new) — **consolidation escape hatch** — pillar7 consolidation defaults to ~5 nodes but splits opportunistically when always-visible + drawer can't contain a legitimate deep-dive.

- **v1.1 (planned, post-Sketch via T-P1-245)**: Deferred revisions requiring real-world signal.
  - §2.3: Optimization (SGD/Adam/二阶) worked example + horizontal/vertical depth-override heuristic.
  - §4.1 / §5.3: canonical drawer-tab render order (proposed: `interview_deep → variants → code → derivation → see_also → history`).
  - Any tightening/loosening surfaced by T-P0-241 Sketch authoring experience.
