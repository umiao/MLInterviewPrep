# BQ Link Distribution Audit (T-P0-573)

Generated: 2026-04-21 01:46 (script: `scripts/audit_bq_link_distribution.py`)

Inputs: `data/mle_prep.db` -- 266 rows in `question_example_links`, 115 questions, 34 stories.

## Purpose

Phase A of the BQ-DEPTH plan (`docs/bq_golden_trait_matrix.md`) is **cut-before-schema**: prune spurious links *before* Phase B adds the `is_primary` / `probe_notes` columns. Adding a primary flag on top of placeholder or stale-framing notes would bake the noise in. This audit enumerates the prune surface per-link so the user can approve/reject row by row.

The audit is read-only: it does not touch the database. The apply step is T-P0-574, which is gated on user approval of the prune list in section 3.

## Methodology

- **Primary-concept threshold**: a question with >= 3 story links is a candidate for Phase-B `is_primary` designation (picks one story as the go-to, others are backups).
- **Angle-thinking threshold**: a story with >= 5 question links needs different facets per link or risks angle collapse under the drill.
- **Prune heuristics**:
  - (a) placeholder: matches `^Brand recall .* story$` (old BLOG framing before the 2-part rewrite).
  - (b) boilerplate: note length < 60 chars and not a placeholder.
  - (c) stale-framing: attached to a Phase-A-II rewrite-target story (EX-01, EX-02, EX-14, EX-33); re-audit after the story is rewritten.
- **Coverage gap**: question whose non-boilerplate link count is 0.

## 1. Questions with >= 3 story links (primary concept needed)

Total questions with >= 3 linked stories: **29**. These are the questions that Phase-B probe_notes should anchor to a *primary* story; the remaining links become explicit backups. Without a primary designation the interview drill has to re-pick each time, and the same story ends up told with the same facet across questions (the failure mode the matrix doc guards against).

| Question | Category | Links | Text |
|----------|----------|-------|------|
| `COM-2` | communication | 15 | Describe a time when you had to persuade others to change direction. |
| `PS-1` | problem_solving | 7 | Walk me through a difficult technical decision you had to make. |
| `PS-2` | problem_solving | 7 | Describe a time when you solved a problem creatively. |
| `INN-4` | innovation | 6 | Describe a time when you implemented an innovative solution. |
| `OWN-11` | ownership | 6 | Tell me about a time when you took ownership of a challenging situation. |
| `IMP-4` | impact | 5 | Give an example of a time you improved a process or system that added significant value. |
| `INN-8` | innovation | 5 | Describe a time when you questioned a traditional approach and proposed something new. |
| `OWN-6` | ownership | 5 | Tell me about a time when you took a bold risk at work. |
| `PS-11` | problem_solving | 5 | Describe a time when you used data to make a key decision. |
| `ADP-15` | adaptability | 4 | What's the biggest lesson you've learned from a failed project? |
| `ADP-4` | adaptability | 4 | Explain a situation where you had to adapt your approach mid-project. |
| `ADP-5` | adaptability | 4 | Describe a time when you made a mistake. How did you handle it, and what did you learn? |
| `COL-5` | collaboration | 4 | How do you align different teams or stakeholders on a shared goal? |
| `IMP-10` | impact | 4 | Give an example of a project where you focused on long-term impact. |
| `INN-5` | innovation | 4 | Tell me about a time when you improved an inefficient process. |
| `OWN-1` | ownership | 4 | Give an example of a time when you took complete ownership of a failure. |
| `PS-4` | problem_solving | 4 | Give an example of a time when you analyzed a complex problem and broke it down. |
| `ADP-14` | adaptability | 3 | Describe a time when you faced a significant roadblock and how you pushed through it. |
| `ADP-18` | adaptability | 3 | Tell me about a recent mistake you made and what you learned from it. |
| `COM-1` | communication | 3 | How do you explain complex technical details to a non-technical stakeholder? |
| `EXE-5` | execution | 3 | Tell me about a time when you managed a large-scale project with tight deadlines. |
| `IMP-15` | impact | 3 | Give an example of when you advocated for responsible practices in product design. |
| `INN-1` | innovation | 3 | Describe a time when you identified an opportunity for improvement. |
| `INN-14` | innovation | 3 | Tell me about a process you put in place that improved the team's productivity. |
| `INN-6` | innovation | 3 | What's a new process or strategy you proposed that led to a major improvement? |
| `INN-9` | innovation | 3 | Tell me about a time when you developed a creative solution to a complex problem. |
| `LDR-1` | leadership | 3 | Describe a time when you coached or mentored someone. |
| `LDR-3` | leadership | 3 | Tell me about a time you had to make a tough call as a leader. |
| `OWN-8` | ownership | 3 | Describe a situation where you were moving fast and made a mistake. |

### Weak-relevance tail spot-check

Per user direction, we specifically inspect the highest-count questions for weak-relevance tail -- links where the note is generic enough that the pair adds noise rather than optionality. Each tail below is sorted by note length ascending (shortest/most-generic first).

#### `COM-2` (15 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `BLOG-01` | 27 | Brand recall two-part story |
| `BLOG-01B` | 28 | Brand recall deep dive story |
| `EX-24` | 65 | Persuaded VP to limit scope rather than combo-launch all policies |
| `EX-14` | 79 | Persuaded manager to pivot from flashy agentic search to pragmatic LLM-as-Judge |
| `EX-13` | 80 | Persuaded team to adopt contribution-based authorship norms over gift authorship |
| `EX-02` | 84 | Persuaded new team to take on diversity ranking by reframing it as a ranking problem |
| `EX-19` | 84 | Persuaded PM to change experiment approach based on technical evidence of confounder |
| `BLOG-04` | 90 | Persuaded manager and Senior Director to adopt new goal framework despite initial pushback |
| `BLOG-03` | 92 | Persuaded ads team to accept interpretable LLM signals instead of direct policy/model access |
| `EX-18` | 96 | Persuaded leadership to deprioritize distributed training based on resource/feasibility analysis |
| `EX-07` | 100 | Persuaded team and XFN stakeholders to change direction from model tuning to dataset/formulation fix |
| `EX-04` | 109 | Persuaded leadership to change optimization targets by reframing MRR decrease as evidence of correct behavior |
| `EX-20` | 124 | Multi-phase persuasion: data research, industry cases, legal framework, then escalation when working-level persuasion failed |
| `EX-33` | 138 | Persuade others to change direction - core influence-without-authority match; convinced the org to deprecate a top-down strategic project. |
| `EX-34` | 232 | Persuaded the principal researcher (and downstream the team) to change direction by reframing the question and honoring his underlying concern. Use this for the 'persuade by translation' pattern, n... |

#### `PS-1` (7 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `BLOG-01B` | 28 | Brand recall deep dive story |
| `EX-03` | 90 | Difficult technical decision: challenged industry-standard Sale NDCG proxy in favor of GMB |
| `BLOG-01` | 96 | Technical decision between compound key lookup vs query rewrite, chose based on latency analysis |
| `EX-05` | 118 | Difficult technical decision: chose cheap rejection + early exit over three alternatives based on traffic distribution |
| `EX-20` | 130 | Difficult technical decision: seller-only vs. seller-listing cross-modeling, with non-obvious compliance and business implications |
| `EX-21` | 158 | Difficult technical decision: build interim solution vs. wait for delayed infrastructure, with non-obvious insight that core and peripheral could be separated |
| `EX-09B` | 223 | Difficult technical decision: rejecting the natural query-rewrite path (which had clear prior art and incremental LLM upside) in favor of co-developing proxy item generation, on the basis of an irr... |

#### `PS-2` (7 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `BLOG-01` | 27 | Brand recall two-part story |
| `BLOG-01B` | 28 | Brand recall deep dive story |
| `EX-09` | 82 | Creative solution: proxy items instead of query rewriting to bridge LLM-search gap |
| `EX-14` | 86 | Creative pivot: found LLM-as-Judge as low-hanging fruit instead of full agentic search |
| `EX-19` | 95 | Creative compromise: time-based experiment design instead of buyer-ID splits for seller testing |
| `BLOG-03` | 102 | Solved the real problem (trust gap in model judgment) not the surface request (tune pass-through rate) |
| `EX-01` | 113 | Creative solution: diversity-blending algorithm that surfaced invisible user intents without rewriting the ranker |

#### `OWN-11` (6 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `EX-02` | 85 | Took ownership of a challenging situation by transferring teams to follow the problem |
| `EX-01` | 96 | Took ownership of a problem the organization did not know existed, grew it into 200M+ initiative |
| `BLOG-04` | 97 | Self-initiated reform of a broken system as a stakeholder, not waiting for someone else to fix it |
| `EX-05` | 105 | As sole MLE, took ownership of both the model problem and the system-coupling failures no one anticipated |
| `BLOG-03` | 115 | Took ownership of a politically sensitive cross-org conflict and delivered a solution that protected org principles |
| `EX-33B` | 149 | Ownership of a challenging situation, but lean on the 'taking responsibility for STOPPING' angle, not the 'taking responsibility for shipping' angle. |

#### `INN-4` (6 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `EX-14` | 55 | Innovative LLM-as-Judge solution for relevance labeling |
| `EX-09` | 64 | Innovative solution that maximized existing infrastructure reuse |
| `EX-01` | 87 | Innovative diversity-blending solution validated during Hacker Week, published at SIGIR |
| `BLOG-03` | 101 | Built LLM judgment pipeline producing 18K labels/day at $500 vs $0.30-0.80/label for human annotation |
| `EX-21` | 139 | Innovative solution: used caching system + param injection to replicate the declarative system's core value without its full infrastructure |
| `EX-09B` | 303 | Innovative solution context: the proxy-item path was a non-obvious architectural alternative that the team had to design from scratch; the privacy concern was the forcing function that motivated th... |

## 2. Stories with >= 5 question links (angle thinking needed)

Total stories with >= 5 linked questions: **32**. When one story is pulled into many questions the risk is angle collapse -- the same STAR retold verbatim, which makes the drill brittle and gives the interviewer a broken-record signal. The trait matrix already maps the expected facet per (story, theme); these stories are the ones that most need probe_notes to keep the facets distinct.

| Story | Title | Q-Links | Questions spanned (categories) |
|-------|-------|--------:|-------------------------------|
| `EX-01` | Search Diversity: Intent Collapse Discovery | 16 | adaptability, execution, impact, innovation, ownership, problem_solving |
| `EX-23` | Large-Scale Project with Tight Deadlines --- NYC C2C Policy Launch | 14 | adaptability, collaboration, execution, ownership, problem_solving |
| `EX-05` | Relevance Filtering: Deployment Feasibility Under Latency Constraints | 13 | adaptability, execution, innovation, ownership, problem_solving |
| `EX-14` | LLM Exploration --- From Vague AI Mandate to Pragmatic LLM-as-Judge | 13 | adaptability, communication, execution, impact, innovation, problem_solving |
| `EX-33` | MoE -> Allocation Paradigm Shift - Org-Level Reframe via Honest Neg... | 12 | collaboration, communication, impact, innovation, ownership, problem_solving |
| `BLOG-04` | Goal Tracking Reform: Honest Metrics Over Cosmetic Delivery | 11 | adaptability, collaboration, communication, impact, innovation, leadership, ownership |
| `BLOG-03` | Cross-Org Boundary Defense via LLM Relevance Pipeline | 10 | collaboration, communication, execution, impact, innovation, ownership, problem_solving |
| `EX-06` | Allocation Framework as Reusable Platform Primitive — 200M+ Impact | 10 | execution, impact, innovation, ownership, problem_solving |
| `EX-09` | Conversational Search — Proxy Item Breakthrough | 10 | adaptability, execution, innovation, problem_solving |
| `EX-15` | Model Deprecation Incident --- Reframing Conflict into a Governance... | 10 | adaptability, communication, innovation, ownership |
| `BLOG-01` | Brand Recall: Influence -- Changing the Researcher-Engineer Dynamic | 9 | adaptability, collaboration, communication, impact, leadership, problem_solving |
| `EX-12` | Helping PhD Interns Transition from Notebook to Production Stack | 9 | innovation, leadership |
| `EX-02` | Overcoming Manager Resistance via Proactive Team Transfer | 8 | adaptability, collaboration, communication, ownership |
| `EX-21` | Tech Debt Balance --- Declarative Artifactory Proof of Concept | 8 | execution, impact, innovation, problem_solving |
| `EX-11` | Mentoring Intern on Overpromise / Goal Visibility | 7 | leadership, ownership |
| `EX-17` | Difficult Feedback from Senior IC --- Reliance vs. Trust | 7 | adaptability, communication, ownership |
| `EX-20` | Seller Risk Modeling Fairness --- Ethical Dilemma and Escalation | 7 | communication, impact, problem_solving |
| `EX-03` | Challenging Sale NDCG Proxy — First Principles Rethinking | 6 | collaboration, impact, innovation, problem_solving |
| `EX-08` | Module Proliferation Prod Degradation — Escalation to VP | 6 | adaptability, communication, innovation, ownership, problem_solving |
| `EX-13` | Authorship Dispute --- Navigating Conflict and Establishing Norms | 6 | collaboration, communication, innovation, leadership |
| `EX-16` | Cross-Datacenter Deployment Incident --- Counterpart Bandwidth as a... | 6 | adaptability, ownership, problem_solving |
| `EX-18` | Pushing Back on Unreasonable Scope --- Distributed Training | 6 | collaboration, communication, execution, problem_solving |
| `EX-22` | Delegation Decision --- Hashing Algorithm for Experiment Platform | 6 | leadership, problem_solving |
| `EX-30` | Hash Capability Misdesign --- Domain Depth Is Not Design Authority | 6 | adaptability, execution, ownership |
| `EX-33B` | MoE Over-Iteration: A Model Believer's Humility Lesson on Problem F... | 6 | adaptability, execution, ownership |
| `EX-34` | BBE Risk Policy: Seller-Level vs Listing-Level — Disagreeing with a... | 6 | communication, impact, leadership |
| `BLOG-01B` | Brand Recall: Deep Dive -- Challenging the Evaluation Blind Spot | 5 | communication, impact, problem_solving |
| `EX-04` | MRR Paradox — Educating Stakeholders on Metric Limitations | 5 | collaboration, communication, impact, problem_solving |
| `EX-07` | Relevance Dataset Bias — Challenging the Self-Fulfilling Prophecy | 5 | collaboration, communication, innovation, problem_solving |
| `EX-09B` | Conversational Search Privacy: Proxy Item Generation Eliminates Raw... | 5 | impact, innovation, problem_solving |
| `EX-10` | Experimental Rigor — Designing Debiased Evaluation Framework | 5 | execution, impact, innovation, ownership, problem_solving |
| `EX-24` | Explaining Allocation Problem to VP --- C2C Policy Launch Communica... | 5 | collaboration, communication, innovation, problem_solving |

### Weak-relevance tail spot-check (high-link stories)

Per user direction we inspect the 5 highest-count stories for tails where the note is short enough that the link is doing no work. Each story below is sorted by note length ascending.

#### `EX-01` (16 links) -- Search Diversity: Intent Collapse Discovery

| question | category | note len | relevance_note |
|----------|----------|---------:|----------------|
| `INN-1` | innovation | 75 | Identified a problem no one else saw -- standard metrics masked the failure |
| `ADP-20` | adaptability | 85 | Self-initiated Hacker Week project driven by curiosity about abandoned query patterns |
| `INN-2` | innovation | 86 | Entirely self-started project, from problem discovery to working prototype in one week |
| `INN-4` | innovation | 87 | Innovative diversity-blending solution validated during Hacker Week, published at SIGIR |
| `IMP-2` | impact | 91 | Prioritized user experience: half of users on multi-intent queries were completely unserved |
| `INN-10` | innovation | 96 | Identified intent collapse as innovation area by questioning why standard metrics looked healthy |
| `OWN-11` | ownership | 96 | Took ownership of a problem the organization did not know existed, grew it into 200M+ initiative |
| `OWN-9` | ownership | 97 | Built prototype with incomplete information -- one week, no guarantee it would work or get funded |
| `OWN-6` | ownership | 104 | Bold risk: invested entire Hacker Week on an unassigned problem that challenged core ranking assumptions |
| `INN-8` | innovation | 106 | Challenged the status quo: questioned why healthy-looking metrics masked half the user base being unserved |
| `INN-9` | innovation | 113 | Creative solution to a complex problem: cheap intent-coverage proxy instead of expensive holistic ranking rewrite |
| `PS-2` | problem_solving | 113 | Creative solution: diversity-blending algorithm that surfaced invisible user intents without rewriting the ranker |
| `EXE-5` | execution | 114 | Delivered end-to-end prototype (data pipeline + algorithm + experiment framework) in one-week Hacker Week deadline |
| `PS-11` | problem_solving | 114 | Used purchase data to prove the ranking system was failing -- display metrics said fine, purchase data said broken |
| `IMP-10` | impact | 116 | Long-term impact: grew from one-week prototype to multi-year 200M+ initiative that changed org-wide ranking approach |
| `PS-15` | problem_solving | 116 | Identified intent collapse through data analysis -- purchase distributions vs display distributions revealed the gap |

#### `EX-23` (14 links) -- Large-Scale Project with Tight Deadlines --- NYC C2C Policy Launch

| question | category | note len | relevance_note |
|----------|----------|---------:|----------------|
| `OWN-2` | ownership | 48 | Went above and beyond to meet VP 2-week deadline |
| `EXE-5` | execution | 56 | Managed 30+ person project under VP 2-week test deadline |
| `PS-4` | problem_solving | 60 | Broke down complex problem: logging vs gateway vs allocation |
| `EXE-9` | execution | 61 | Recovered from silent upstream overwrite causing test failure |
| `EXE-12` | execution | 66 | Shifted priorities when combo launch structural problem discovered |
| `EXE-6` | execution | 70 | Balanced VP urgency, upstream gateway team fix, and combo launch scope |
| `COL-7` | collaboration | 71 | Worked with 30+ people across technical teams and VP-level stakeholders |
| `EXE-7` | execution | 83 | Handled delay caused by upstream gateway team silently overwriting control property |
| `EXE-10` | execution | 91 | Managed 2-week test deadline + 1-month launch proposal + daily updates + weekly VP meetings |
| `EXE-14` | execution | 91 | Maintained daily team updates and weekly VP cadence while managing 30+ person critical path |
| `COL-9` | collaboration | 93 | Balanced competing priorities: VP urgency, gateway team fix, and combo launch scope tradeoffs |
| `ADP-3` | adaptability | 94 | Requirements shifted when structural problem discovered mid-project, adapted scope accordingly |
| `COL-8` | collaboration | 94 | Managed VP expectations on timeline and scope while coordinating with multiple technical teams |
| `PS-8` | problem_solving | 104 | High uncertainty project: unknown logging issues, silent upstream failures, untested policy interactions |

#### `EX-05` (13 links) -- Relevance Filtering: Deployment Feasibility Under Latency Constraints

| question | category | note len | relevance_note |
|----------|----------|---------:|----------------|
| `INN-5` | innovation | 93 | Established end-to-end payload stress test as team standard after discovering silent failures |
| `OWN-8` | ownership | 103 | As sole MLE, identified and resolved both model-level and system-level blockers under deadline pressure |
| `OWN-11` | ownership | 105 | As sole MLE, took ownership of both the model problem and the system-coupling failures no one anticipated |
| `PS-10` | problem_solving | 105 | Trade-off: accuracy vs latency, chose cheap rejection + early exit based on traffic distribution analysis |
| `INN-15` | innovation | 107 | Created best practice: payload stress test verifying data integrity at every downstream stage before launch |
| `EXE-5` | execution | 109 | Shipped under tight deadline with no fallback -- two months invested, <=1% latency budget, had to find a path |
| `ADP-14` | adaptability | 114 | Significant roadblock (silent CI failures with no error signals) -- traced to URL length and JSON field truncation |
| `EXE-3` | execution | 115 | Solved complex multi-layer problem: model latency + system-coupling silent failures (URL length, JSON field limits) |
| `ADP-5` | adaptability | 116 | Over-invested in deep models for two months before confronting latency -- learned to front-load deployability checks |
| `PS-1` | problem_solving | 118 | Difficult technical decision: chose cheap rejection + early exit over three alternatives based on traffic distribution |
| `PS-4` | problem_solving | 120 | Broke down a complex deployment problem into three layers: model architecture, latency optimization, and system coupling |
| `ADP-6` | adaptability | 130 | Project started with ambiguity about what 'deployment feasibility' even meant -- expanded from model-layer to full system coupling |
| `ADP-15` | adaptability | 510 | Biggest failure lesson: we over-built a thousands-of-trees XGBoost by implicitly pattern-matching on other teams' model-depth trend, without first checking whether our own problem shape justified i... |

#### `EX-14` (13 links) -- LLM Exploration --- From Vague AI Mandate to Pragmatic LLM-as-Judge

| question | category | note len | relevance_note |
|----------|----------|---------:|----------------|
| `INN-4` | innovation | 55 | Innovative LLM-as-Judge solution for relevance labeling |
| `EXE-4` | execution | 69 | Incorporated LLM industry trends into pragmatic team project planning |
| `ADP-4` | adaptability | 73 | Adapted approach mid-project: pivoted from agentic search to LLM-as-Judge |
| `ADP-7` | adaptability | 74 | LLM exploration started with incomplete requirements from vague AI mandate |
| `ADP-8` | adaptability | 75 | Made decisions with limited data about LLM feasibility in production search |
| `IMP-4` | impact | 75 | LLM-as-Judge became production infrastructure adopted across multiple teams |
| `ADP-1` | adaptability | 76 | Quickly learned LLM capabilities when given vague AI mandate from leadership |
| `COM-2` | communication | 79 | Persuaded manager to pivot from flashy agentic search to pragmatic LLM-as-Judge |
| `INN-3` | innovation | 82 | Explored LLM technologies to find pragmatic application matching team capabilities |
| `ADP-10` | adaptability | 83 | Created structured plan to evaluate LLM applications in highly ambiguous AI mandate |
| `INN-6` | innovation | 85 | Proposed LLM-as-Judge strategy that became major relevance measurement infrastructure |
| `PS-2` | problem_solving | 86 | Creative pivot: found LLM-as-Judge as low-hanging fruit instead of full agentic search |
| `ADP-6` | adaptability | 96 | Navigated highly ambiguous project with no clear requirements or precedent for LLM in production |

#### `EX-33` (12 links) -- MoE -> Allocation Paradigm Shift - Org-Level Reframe via Honest Negative Result

| question | category | note len | relevance_note |
|----------|----------|---------:|----------------|
| `OWN-10` | ownership | 103 | Long-term impact demonstration - multi-quarter paradigm push across the org, not a single-quarter ship. |
| `IMP-10` | impact | 111 | Long-term impact example - the full Allocation policy 200M+ GMB arc and team rename from ranking to allocation. |
| `OWN-6` | ownership | 121 | Bold risk at work - 'start test' framing staked my personal track record on a paradigm bet with no carry-over protection. |
| `PS-6` | problem_solving | 130 | Calculated risk - short-term personal cost (no carry-over cover) traded for long-term org value (paradigm shift + 200M+ GMB tail). |
| `IMP-4` | impact | 131 | Improved a process/system adding significant value - paradigm shift yielded 200M+ annualized GMB and a durable mental-model change. |
| `IMP-9` | impact | 131 | Short-term vs long-term tradeoff - forgoing carry-over protection and a 'launchable' MoE expert for long-term paradigm credibility. |
| `INN-6` | innovation | 134 | New process/strategy with major improvement - the allocation policy proposal replaced ranker-centric planning as the team's main line. |
| `INN-1` | innovation | 137 | Identified an opportunity for improvement - recognized the paradigm gap between pairwise ranking and the industry's whole-page direction. |
| `COM-2` | communication | 138 | Persuade others to change direction - core influence-without-authority match; convinced the org to deprecate a top-down strategic project. |
| `INN-8` | innovation | 138 | Questioned a traditional approach - pairwise distributed ranking - and proposed reranking + allocation policy as the replacement paradigm. |
| `COL-5` | collaboration | 147 | Align teams/stakeholders on shared goal - coalition building over several quarters with senior ICs and my manager before the empirical chip landed. |
| `OWN-9` | ownership | 151 | Innovate without all the information - ran an 80-GPU empirical test as the way forward under strategic uncertainty; the negative result was the signal. |

## 3. Prune candidates (per-link accept/reject)

Three sub-buckets, roughly ordered by severity. The user reviews each row and decides KEEP / DROP / UPDATE-NOTE; this audit does NOT write to the DB (cut-before-schema means user approval is the gate). Every row includes the full `relevance_note` text so the decision can be made in-line without a round-trip to the database.

| Bucket | Count |
|--------|------:|
| (a) Old-framing placeholder | 11 |
| (b) Single-sentence boilerplate (< 60 chars, non-placeholder) | 4 |
| (c) Stale-framing (story scheduled for Phase-A-II rewrite) | 48 |
| **Total unique link rows flagged** | **63** |

### 3(a) Old-framing placeholders

These notes literally contain the old `Brand recall X story` placeholder text -- the story was re-titled but the link note was never rewritten. Recommended action: **DROP or UPDATE-NOTE**. A note like 'Brand recall two-part story' does not tell the drill-runner *which* facet of that story matches this question, so the link is doing less work than the title of the story it points to.

| link_id | question | story | note len | relevance_note |
|--------:|----------|-------|---------:|----------------|
| 184 | `ADP-3` | `BLOG-01` | 27 | Brand recall two-part story |
| 179 | `COM-2` | `BLOG-01` | 27 | Brand recall two-part story |
| 190 | `COM-2` | `BLOG-01B` | 28 | Brand recall deep dive story |
| 189 | `IMP-1` | `BLOG-01B` | 28 | Brand recall deep dive story |
| 186 | `IMP-4` | `BLOG-01` | 27 | Brand recall two-part story |
| 183 | `LDR-1` | `BLOG-01` | 27 | Brand recall two-part story |
| 187 | `PS-1` | `BLOG-01B` | 28 | Brand recall deep dive story |
| 180 | `PS-2` | `BLOG-01` | 27 | Brand recall two-part story |
| 191 | `PS-2` | `BLOG-01B` | 28 | Brand recall deep dive story |
| 181 | `PS-3` | `BLOG-01` | 27 | Brand recall two-part story |
| 188 | `PS-4` | `BLOG-01B` | 28 | Brand recall deep dive story |

### 3(b) Single-sentence boilerplate

Notes shorter than 60 characters with no explicit placeholder marker. Most are loose paraphrases of the question stem ('Mentored PhD interns through production stack transition' for LDR-1) rather than a specific facet lock. Recommended action: **UPDATE-NOTE** to a facet-specific line per `docs/bq_golden_trait_matrix.md`, or DROP if a stronger story already covers the same angle.

| link_id | question | story | note len | relevance_note |
|--------:|----------|-------|---------:|----------------|
| 159 | `EXE-5` | `EX-23` | 56 | Managed 30+ person project under VP 2-week test deadline |
| 76 | `INN-4` | `EX-14` | 55 | Innovative LLM-as-Judge solution for relevance labeling |
| 64 | `LDR-1` | `EX-12` | 56 | Mentored PhD interns through production stack transition |
| 164 | `OWN-2` | `EX-23` | 48 | Went above and beyond to meet VP 2-week deadline |

### 3(c) Stale-framing (Phase-A-II rewrite targets)

Links attached to `EX-01`, `EX-02`, `EX-14`, `EX-33`. These stories are scheduled to be rewritten per the golden trait matrix plan (T-P0-575/576/577/578); the note may not survive the rewrite untouched. Recommended action: **DEFER** decision until after story rewrite, then re-audit with the new STAR in hand. Listed here only so the scope of the post-rewrite re-audit is explicit now.

| link_id | question | story | note len | relevance_note |
|--------:|----------|-------|---------:|----------------|
| 141 | `ADP-1` | `EX-14` | 76 | Quickly learned LLM capabilities when given vague AI mandate from leadership |
| 143 | `ADP-10` | `EX-14` | 83 | Created structured plan to evaluate LLM applications in highly ambiguous AI mandate |
| 6 | `ADP-14` | `EX-02` | 126 | Faced organizational roadblock (no experiment slots, out-of-scope mandate) and found creative workaround through team transfer |
| 124 | `ADP-17` | `EX-02` | 88 | Recognized own gap: had not translated business case into team OKR language early enough |
| 122 | `ADP-20` | `EX-01` | 85 | Self-initiated Hacker Week project driven by curiosity about abandoned query patterns |
| 9 | `ADP-4` | `EX-02` | 90 | Adapted approach mid-project: from pushing within wrong team to strategically transferring |
| 75 | `ADP-4` | `EX-14` | 73 | Adapted approach mid-project: pivoted from agentic search to LLM-as-Judge |
| 73 | `ADP-6` | `EX-14` | 96 | Navigated highly ambiguous project with no clear requirements or precedent for LLM in production |
| 142 | `ADP-7` | `EX-14` | 74 | LLM exploration started with incomplete requirements from vague AI mandate |
| 74 | `ADP-8` | `EX-14` | 75 | Made decisions with limited data about LLM feasibility in production search |
| 58 | `COL-3` | `EX-02` | 133 | Story I enrichment: drove project across multiple teams — from relevance team to final ranking team, multi-team production deployment |
| 59 | `COL-5` | `EX-02` | 124 | Story I enrichment: aligned different teams on shared goal — reframed diversity as ranking problem to gain cross-team buy-in |
| 259 | `COL-5` | `EX-33` | 147 | Align teams/stakeholders on shared goal - coalition building over several quarters with senior ICs and my manager before the empirical chip landed. |
| 8 | `COM-2` | `EX-02` | 84 | Persuaded new team to take on diversity ranking by reframing it as a ranking problem |
| 78 | `COM-2` | `EX-14` | 79 | Persuaded manager to pivot from flashy agentic search to pragmatic LLM-as-Judge |
| 258 | `COM-2` | `EX-33` | 138 | Persuade others to change direction - core influence-without-authority match; convinced the org to deprecate a top-down strategic project. |
| 144 | `EXE-4` | `EX-14` | 69 | Incorporated LLM industry trends into pragmatic team project planning |
| 212 | `EXE-5` | `EX-01` | 114 | Delivered end-to-end prototype (data pipeline + algorithm + experiment framework) in one-week Hacker Week deadline |
| 211 | `IMP-10` | `EX-01` | 116 | Long-term impact: grew from one-week prototype to multi-year 200M+ initiative that changed org-wide ranking approach |
| 254 | `IMP-10` | `EX-33` | 111 | Long-term impact example - the full Allocation policy 200M+ GMB arc and team rename from ranking to allocation. |
| 56 | `IMP-2` | `EX-01` | 91 | Prioritized user experience: half of users on multi-intent queries were completely unserved |
| 79 | `IMP-4` | `EX-14` | 75 | LLM-as-Judge became production infrastructure adopted across multiple teams |
| 260 | `IMP-4` | `EX-33` | 131 | Improved a process/system adding significant value - paradigm shift yielded 200M+ annualized GMB and a durable mental-model change. |
| 255 | `IMP-9` | `EX-33` | 131 | Short-term vs long-term tradeoff - forgoing carry-over protection and a 'launchable' MoE expert for long-term paradigm credibility. |
| 2 | `INN-1` | `EX-01` | 75 | Identified a problem no one else saw -- standard metrics masked the failure |
| 261 | `INN-1` | `EX-33` | 137 | Identified an opportunity for improvement - recognized the paradigm gap between pairwise ranking and the industry's whole-page direction. |
| 121 | `INN-10` | `EX-01` | 96 | Identified intent collapse as innovation area by questioning why standard metrics looked healthy |
| 3 | `INN-2` | `EX-01` | 86 | Entirely self-started project, from problem discovery to working prototype in one week |
| 140 | `INN-3` | `EX-14` | 82 | Explored LLM technologies to find pragmatic application matching team capabilities |
| 210 | `INN-4` | `EX-01` | 87 | Innovative diversity-blending solution validated during Hacker Week, published at SIGIR |
| 80 | `INN-6` | `EX-14` | 85 | Proposed LLM-as-Judge strategy that became major relevance measurement infrastructure |
| 256 | `INN-6` | `EX-33` | 134 | New process/strategy with major improvement - the allocation policy proposal replaced ranker-centric planning as the team's main line. |
| 209 | `INN-8` | `EX-01` | 106 | Challenged the status quo: questioned why healthy-looking metrics masked half the user base being unserved |
| 257 | `INN-8` | `EX-33` | 138 | Questioned a traditional approach - pairwise distributed ranking - and proposed reranking + allocation policy as the replacement paradigm. |
| 120 | `INN-9` | `EX-01` | 113 | Creative solution to a complex problem: cheap intent-coverage proxy instead of expensive holistic ranking rewrite |
| 253 | `OWN-10` | `EX-33` | 103 | Long-term impact demonstration - multi-quarter paradigm push across the org, not a single-quarter ship. |
| 57 | `OWN-11` | `EX-01` | 96 | Took ownership of a problem the organization did not know existed, grew it into 200M+ initiative |
| 7 | `OWN-11` | `EX-02` | 85 | Took ownership of a challenging situation by transferring teams to follow the problem |
| 1 | `OWN-6` | `EX-01` | 104 | Bold risk: invested entire Hacker Week on an unassigned problem that challenged core ranking assumptions |
| 251 | `OWN-6` | `EX-33` | 121 | Bold risk at work - 'start test' framing staked my personal track record on a paradigm bet with no carry-over protection. |
| 123 | `OWN-7` | `EX-02` | 88 | Showed resilience by transferring teams rather than accepting organizational constraints |
| 119 | `OWN-9` | `EX-01` | 97 | Built prototype with incomplete information -- one week, no guarantee it would work or get funded |
| 262 | `OWN-9` | `EX-33` | 151 | Innovate without all the information - ran an 80-GPU empirical test as the way forward under strategic uncertainty; the negative result was the signal. |
| 208 | `PS-11` | `EX-01` | 114 | Used purchase data to prove the ranking system was failing -- display metrics said fine, purchase data said broken |
| 4 | `PS-15` | `EX-01` | 116 | Identified intent collapse through data analysis -- purchase distributions vs display distributions revealed the gap |
| 5 | `PS-2` | `EX-01` | 113 | Creative solution: diversity-blending algorithm that surfaced invisible user intents without rewriting the ranker |
| 77 | `PS-2` | `EX-14` | 86 | Creative pivot: found LLM-as-Judge as low-hanging fruit instead of full agentic search |
| 252 | `PS-6` | `EX-33` | 130 | Calculated risk - short-term personal cost (no carry-over cover) traded for long-term org value (paradigm shift + 200M+ GMB tail). |

## 4. Coverage gaps (questions with 0 non-boilerplate links)

These are questions whose only links would all be pruned if every section-3 recommendation were accepted. They must be handled before pruning so we do not create 0-link questions: either (i) an existing flagged link gets UPDATE-NOTE instead of DROP, or (ii) a new link from an existing non-flagged story is added. Phase B (schema uplift) should not run until every question has >= 1 non-boilerplate link.

| question | category | total links | all flagged by | text |
|----------|----------|------------:|----------------|------|
| `OWN-9` | ownership | 2 | stale-framing | Explain a time when you had to move fast and innovate without all the informa... |
| `ADP-20` | adaptability | 1 | stale-framing | How do you stay motivated and engaged in your work? |
| `ADP-8` | adaptability | 1 | stale-framing | Describe a situation where you had to make decisions with limited data. |
| `EXE-4` | execution | 1 | stale-framing | How do you stay updated with industry trends and incorporate them into your w... |
| `IMP-2` | impact | 1 | stale-framing | Describe a time when you prioritized user experience in a technical decision. |
| `INN-10` | innovation | 1 | stale-framing | How do you identify areas for innovation within an existing project? |
| `INN-2` | innovation | 1 | stale-framing | Tell me about a project or idea you started on your own. |
| `OWN-2` | ownership | 1 | boilerplate | Describe a situation where you went above and beyond to meet a deadline. |

