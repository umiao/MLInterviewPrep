# BQ Link Distribution Audit (T-P0-573)

Generated: 2026-04-23 15:02 (script: `scripts/audit_bq_link_distribution.py`)

Inputs: `data/mle_prep.db` -- 271 rows in `question_example_links`, 115 questions, 35 stories.

## Purpose

Phase A of the BQ-DEPTH plan (`docs/bq_golden_trait_matrix.md`) is **cut-before-schema**: prune spurious links *before* Phase B adds the `is_primary` / `probe_notes` columns. Adding a primary flag on top of placeholder or stale-framing notes would bake the noise in. This audit enumerates the prune surface per-link so the user can approve/reject row by row.

The audit is read-only: it does not touch the database. The apply step is T-P0-574, which is gated on user approval of the prune list in section 3.

## Methodology

- **Primary-concept threshold**: a question with >= 3 story links is a candidate for Phase-B `is_primary` designation (picks one story as the go-to, others are backups).
- **Angle-thinking threshold**: a story with >= 5 question links needs different facets per link or risks angle collapse under the drill.
- **Prune heuristics**:
  - (a) placeholder: matches `^Brand recall .* story$` (old BLOG framing before the 2-part rewrite).
  - (b) boilerplate: note length < 60 chars and not a placeholder.
  - (c) stale-framing: attached to a Phase-A-II rewrite-target story (EX-01, EX-02, EX-33); re-audit after the story is rewritten.
- **Coverage gap**: question whose non-boilerplate link count is 0.

## 1. Questions with >= 3 story links (primary concept needed)

Total questions with >= 3 linked stories: **33**. These are the questions that Phase-B probe_notes should anchor to a *primary* story; the remaining links become explicit backups. Without a primary designation the interview drill has to re-pick each time, and the same story ends up told with the same facet across questions (the failure mode the matrix doc guards against).

| Question | Category | Links | Text |
|----------|----------|-------|------|
| `COM-2` | communication | 14 | Describe a time when you had to persuade others to change direction. |
| `INN-4` | innovation | 6 | Describe a time when you implemented an innovative solution. |
| `OWN-11` | ownership | 6 | Tell me about a time when you took ownership of a challenging situation. |
| `PS-1` | problem_solving | 6 | Walk me through a difficult technical decision you had to make. |
| `COL-5` | collaboration | 5 | How do you align different teams or stakeholders on a shared goal? |
| `IMP-10` | impact | 5 | Give an example of a project where you focused on long-term impact. |
| `IMP-4` | impact | 5 | Give an example of a time you improved a process or system that added significant value. |
| `INN-8` | innovation | 5 | Describe a time when you questioned a traditional approach and proposed something new. |
| `OWN-6` | ownership | 5 | Tell me about a time when you took a bold risk at work. |
| `PS-11` | problem_solving | 5 | Describe a time when you used data to make a key decision. |
| `PS-2` | problem_solving | 5 | Describe a time when you solved a problem creatively. |
| `ADP-15` | adaptability | 4 | What's the biggest lesson you've learned from a failed project? |
| `ADP-4` | adaptability | 4 | Explain a situation where you had to adapt your approach mid-project. |
| `ADP-5` | adaptability | 4 | Describe a time when you made a mistake. How did you handle it, and what did you learn? |
| `INN-5` | innovation | 4 | Tell me about a time when you improved an inefficient process. |
| `INN-6` | innovation | 4 | What's a new process or strategy you proposed that led to a major improvement? |
| `OWN-1` | ownership | 4 | Give an example of a time when you took complete ownership of a failure. |
| `ADP-14` | adaptability | 3 | Describe a time when you faced a significant roadblock and how you pushed through it. |
| `ADP-18` | adaptability | 3 | Tell me about a recent mistake you made and what you learned from it. |
| `COL-3` | collaboration | 3 | Tell me about a time you worked with a cross-functional team to achieve a common goal. |
| `COL-7` | collaboration | 3 | Tell me about a project where you worked closely with both technical and non-technical... |
| `COM-1` | communication | 3 | How do you explain complex technical details to a non-technical stakeholder? |
| `EXE-5` | execution | 3 | Tell me about a time when you managed a large-scale project with tight deadlines. |
| `IMP-15` | impact | 3 | Give an example of when you advocated for responsible practices in product design. |
| `INN-1` | innovation | 3 | Describe a time when you identified an opportunity for improvement. |
| `INN-14` | innovation | 3 | Tell me about a process you put in place that improved the team's productivity. |
| `INN-15` | innovation | 3 | Give an example of when you helped establish best practices for your team. |
| `INN-7` | innovation | 3 | How do you ensure you're not just solving the immediate problem but also thinking strat... |
| `INN-9` | innovation | 3 | Tell me about a time when you developed a creative solution to a complex problem. |
| `LDR-3` | leadership | 3 | Tell me about a time you had to make a tough call as a leader. |
| `OWN-10` | ownership | 3 | How do you demonstrate Meta's value of focusing on long-term impact? |
| `OWN-8` | ownership | 3 | Describe a situation where you were moving fast and made a mistake. |
| `PS-4` | problem_solving | 3 | Give an example of a time when you analyzed a complex problem and broke it down. |

### Weak-relevance tail spot-check

Per user direction, we specifically inspect the highest-count questions for weak-relevance tail -- links where the note is generic enough that the pair adds noise rather than optionality. Each tail below is sorted by note length ascending (shortest/most-generic first).

#### `COM-2` (14 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `EX-24` | 65 | Persuaded VP to limit scope rather than combo-launch all policies |
| `EX-13` | 80 | Persuaded team to adopt contribution-based authorship norms over gift authorship |
| `EX-02` | 84 | Persuaded new team to take on diversity ranking by reframing it as a ranking problem |
| `EX-19` | 84 | Persuaded PM to change experiment approach based on technical evidence of confounder |
| `BLOG-04` | 90 | Persuaded manager and Senior Director to adopt new goal framework despite initial pushback |
| `BLOG-03` | 92 | Persuaded ads team to accept interpretable LLM signals instead of direct policy/model access |
| `EX-18` | 96 | Persuaded leadership to deprioritize distributed training based on resource/feasibility analysis |
| `EX-07` | 100 | Persuaded team and XFN stakeholders to change direction from model tuning to dataset/formulation fix |
| `EX-04` | 109 | Persuaded leadership to change optimization targets by reframing MRR decrease as evidence of correct behavior |
| `EX-20` | 124 | Multi-phase persuasion: data research, industry cases, legal framework, then escalation when working-level persuasion failed |
| `EX-14` | 132 | Walked manager off the agentic-search headline path using ROI math, not vision -- pivot was an infrastructure argument, not a pitch. |
| `EX-33` | 138 | Persuade others to change direction - core influence-without-authority match; convinced the org to deprecate a top-down strategic project. |
| `EX-12B` | 197 | Persuaded leadership with utilization data and persuaded researchers with pain-first empathy — didn't mandate notebook deprecation, made the alternative viable enough that cooperation was rational. |
| `EX-34` | 232 | Persuaded the principal researcher (and downstream the team) to change direction by reframing the question and honoring his underlying concern. Use this for the 'persuade by translation' pattern, n... |

#### `PS-1` (6 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `EX-03` | 90 | Difficult technical decision: challenged industry-standard Sale NDCG proxy in favor of GMB |
| `BLOG-01` | 96 | Technical decision between compound key lookup vs query rewrite, chose based on latency analysis |
| `EX-05` | 118 | Difficult technical decision: chose cheap rejection + early exit over three alternatives based on traffic distribution |
| `EX-20` | 130 | Difficult technical decision: seller-only vs. seller-listing cross-modeling, with non-obvious compliance and business implications |
| `EX-21` | 158 | Difficult technical decision: build interim solution vs. wait for delayed infrastructure, with non-obvious insight that core and peripheral could be separated |
| `EX-09B` | 223 | Difficult technical decision: rejecting the natural query-rewrite path (which had clear prior art and incremental LLM upside) in favor of co-developing proxy item generation, on the basis of an irr... |

#### `PS-2` (5 links)

| example | note len | relevance_note |
|---------|---------:|----------------|
| `EX-09` | 82 | Creative solution: proxy items instead of query rewriting to bridge LLM-search gap |
| `EX-19` | 95 | Creative compromise: time-based experiment design instead of buyer-ID splits for seller testing |
| `BLOG-03` | 102 | Solved the real problem (trust gap in model judgment) not the surface request (tune pass-through rate) |
| `EX-01` | 113 | Creative solution: diversity-blending algorithm that surfaced invisible user intents without rewriting the ranker |
| `EX-14` | 157 | Disqualified the headline agentic-search path with ROI math, then found low-hanging fruit at the relevance backlog -- creativity in scoping, not in building. |

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
| `EX-09` | 64 | Innovative solution that maximized existing infrastructure reuse |
| `EX-01` | 87 | Innovative diversity-blending solution validated during Hacker Week, published at SIGIR |
| `BLOG-03` | 101 | Built LLM judgment pipeline producing 18K labels/day at $500 vs $0.30-0.80/label for human annotation |
| `EX-14` | 118 | LLM-as-Judge for relevance labeling -- the move wasn't the technique, it was the pivot away from agentic search to it. |
| `EX-21` | 139 | Innovative solution: used caching system + param injection to replicate the declarative system's core value without its full infrastructure |
| `EX-09B` | 303 | Innovative solution context: the proxy-item path was a non-obvious architectural alternative that the team had to design from scratch; the privacy concern was the forcing function that motivated th... |

## 2. Stories with >= 5 question links (angle thinking needed)

Total stories with >= 5 linked questions: **32**. When one story is pulled into many questions the risk is angle collapse -- the same STAR retold verbatim, which makes the drill brittle and gives the interviewer a broken-record signal. The trait matrix already maps the expected facet per (story, theme); these stories are the ones that most need probe_notes to keep the facets distinct.

| Story | Title | Q-Links | Questions spanned (categories) |
|-------|-------|--------:|-------------------------------|
| `EX-01` | Search Diversity: Intent Collapse Discovery | 16 | adaptability, execution, impact, innovation, ownership, problem_solving |
| `EX-12B` | Notebook -> ML Platform Migration --- Team Utilization 5% to 40% vi... | 16 | collaboration, communication, impact, innovation, ownership |
| `EX-23` | Large-Scale Project with Tight Deadlines --- NYC C2C Policy Launch | 14 | adaptability, collaboration, execution, ownership, problem_solving |
| `EX-05` | Relevance Filtering: Deployment Feasibility Under Latency Constraints | 13 | adaptability, execution, innovation, ownership, problem_solving |
| `EX-14` | LLM Exploration --- Killing the Agentic Mandate with One Week of RO... | 13 | adaptability, communication, execution, impact, innovation, problem_solving |
| `EX-33` | MoE -> Allocation Paradigm Shift - Org-Level Reframe via Honest Neg... | 12 | collaboration, communication, impact, innovation, ownership, problem_solving |
| `BLOG-04` | Goal Tracking Reform: Honest Metrics Over Cosmetic Delivery | 11 | adaptability, collaboration, communication, impact, innovation, leadership, ownership |
| `BLOG-03` | Cross-Org Boundary Defense via LLM Relevance Pipeline | 10 | collaboration, communication, execution, impact, innovation, ownership, problem_solving |
| `EX-06` | Allocation Framework as Reusable Platform Primitive — 200M+ Impact | 10 | execution, impact, innovation, ownership, problem_solving |
| `EX-09` | Conversational Search — Proxy Item Breakthrough | 10 | adaptability, execution, innovation, problem_solving |
| `EX-15` | Model Deprecation Incident --- Reframing Conflict into a Governance... | 10 | adaptability, communication, innovation, ownership |
| `EX-02` | Overcoming Manager Resistance via Proactive Team Transfer | 8 | adaptability, collaboration, communication, ownership |
| `EX-21` | Tech Debt Balance --- Declarative Artifactory Proof of Concept | 8 | execution, impact, innovation, problem_solving |
| `EX-11` | Mentoring Intern on Overpromise / Goal Visibility | 7 | leadership, ownership |
| `EX-17` | Difficult Feedback from Senior IC --- Reliance vs. Trust | 7 | adaptability, communication, ownership |
| `EX-20` | Seller Risk Modeling Fairness --- Ethical Dilemma and Escalation | 7 | communication, impact, problem_solving |
| `EX-03` | Challenging Sale NDCG Proxy — First Principles Rethinking | 6 | collaboration, impact, innovation, problem_solving |
| `EX-08` | Module Proliferation Prod Degradation — Escalation to VP | 6 | adaptability, communication, innovation, ownership, problem_solving |
| `EX-12` | Helping PhD Interns Transition from Notebook to Production Stack | 6 | leadership |
| `EX-13` | Authorship Dispute --- Navigating Conflict and Establishing Norms | 6 | collaboration, communication, innovation, leadership |
| `EX-16` | Cross-Datacenter Deployment Incident --- Counterpart Bandwidth as a... | 6 | adaptability, ownership, problem_solving |
| `EX-18` | Pushing Back on Unreasonable Scope --- Distributed Training | 6 | collaboration, communication, execution, problem_solving |
| `EX-22` | Delegation Decision --- Hashing Algorithm for Experiment Platform | 6 | leadership, problem_solving |
| `EX-30` | Hash Capability Misdesign --- Domain Depth Is Not Design Authority | 6 | adaptability, execution, ownership |
| `EX-33B` | MoE Over-Iteration: A Model Believer's Humility Lesson on Problem F... | 6 | adaptability, execution, ownership |
| `EX-34` | BBE Risk Policy: Seller-Level vs Listing-Level — Disagreeing with a... | 6 | communication, impact, leadership |
| `BLOG-01` | Brand Recall: Influence -- Changing the Researcher-Engineer Dynamic | 5 | adaptability, collaboration, communication, problem_solving |
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

#### `EX-12B` (16 links) -- Notebook -> ML Platform Migration --- Team Utilization 5% to 40% via Template+Profile A...

| question | category | note len | relevance_note |
|----------|----------|---------:|----------------|
| `INN-5` | innovation | 111 | Team-wide migration off notebook onto ML platform; utilization 5%→40%, legacy R models back on refresh cadence. |
| `INN-11` | innovation | 143 | Migrated entire research team off ad-hoc notebook environments onto a mature ML platform with template+profile abstraction; utilization 5%→40%. |
| `INN-14` | innovation | 146 | Template+profile abstraction codified as team best practice; new researchers fork-and-go, team iteration velocity + production solidity both rose. |
| `INN-15` | innovation | 165 | Codified team-accepted best practice: template repos + profile-like config so researchers describe training / exploration declaratively; fork-and-go for new joiners. |
| `COL-5` | collaboration | 169 | Aligned researchers (worried about losing notebook capability) with platform team (scoped initially to k8s + ephemeral pods) around a shared roadmap that satisfied both. |
| `INN-13` | innovation | 171 | Well-established notebook workflow was inefficient at <5% utilization; team-wide migration with template+profile abstraction improved it without killing research velocity. |
| `OWN-10` | ownership | 175 | Prioritized platform-level change (persistent dev + reusable pipelines into ML platform roadmap) over short-term migration; capabilities later became defaults for other teams. |
| `IMP-4` | impact | 176 | Notebook→ML platform migration: utilization 5%→40%, freed capacity benefits other workloads, legacy R models refreshable, platform capabilities became defaults for other teams. |
| `INN-7` | innovation | 176 | Didn't just fix notebook waste — pushed platform roadmap beyond ephemeral pods toward persistent dev + reusable pipelines; strategic bet that later became ML platform defaults. |
| `IMP-8` | impact | 179 | Built template+profile abstraction that scales horizontally (fork-and-go) rather than by coaching hours; platform capabilities pushed during migration became ML platform defaults. |
| `COL-3` | collaboration | 193 | Two-way translator between Research Science and ML platform / Infra — carried RS workflow requirements (HDFS, Spark, LnP, debug tooling) into platform roadmap so migration preserved capability. |
| `COM-2` | communication | 197 | Persuaded leadership with utilization data and persuaded researchers with pain-first empathy — didn't mandate notebook deprecation, made the alternative viable enough that cooperation was rational. |
| `INN-6` | innovation | 198 | Proposed template + profile abstraction on top of ML platform runtime — the process change that made researcher adoption default and delivered utilization 5%→40% + platform-wide capability defaults. |
| `IMP-10` | impact | 204 | Short-term: team utilization 5%→40% + unblocked refreshable legacy models. Long-term: platform capabilities adopted org-wide as defaults; reframed "DS can't ship production" from skill gap to tooli... |
| `COL-7` | collaboration | 206 | RS (non-infra) + ML platform engineers (non-research) had no shared language; translated in both directions — surfaced <5% utilization to leadership, carried HDFS/Spark/LnP requirements into platfo... |
| `IMP-6` | impact | 212 | Template+profile abstraction sustains onboarding for new researchers without coaching overhead; auto model versioning + historical weights + real-time CPU/GPU diagnostics replaced notebook-era ad-h... |

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

#### `EX-14` (13 links) -- LLM Exploration --- Killing the Agentic Mandate with One Week of ROI Math

| question | category | note len | relevance_note |
|----------|----------|---------:|----------------|
| `INN-6` | innovation | 97 | LLM-as-Judge became production measurement infrastructure adopted by ads and several other teams. |
| `ADP-10` | adaptability | 99 | Built a 1-week structured feasibility on the obvious path before committing to any LLM application. |
| `ADP-7` | adaptability | 102 | Vague AI mandate had no requirements -- substituted feasibility analysis for the missing requirements. |
| `ADP-6` | adaptability | 108 | No requirements, no LLM precedent in our stack -- scoped through feasibility math rather than brainstorming. |
| `ADP-4` | adaptability | 115 | Killed the agentic-search path with 1-week feasibility math, pivoted to LLM-as-Judge against the relevance backlog. |
| `INN-3` | innovation | 115 | Picked LLM-as-Judge over agentic search by feasibility-first scoping -- ROI math chose the experiment, not novelty. |
| `IMP-4` | impact | 117 | Solo LLM-as-Judge exploration scaled into org-wide measurement infrastructure adopted by ads and several other teams. |
| `INN-4` | innovation | 118 | LLM-as-Judge for relevance labeling -- the move wasn't the technique, it was the pivot away from agentic search to it. |
| `EXE-4` | execution | 122 | Took the LLM industry hype as input but applied feasibility math to disqualify the headline application before chasing it. |
| `ADP-8` | adaptability | 125 | Made the agentic-search disqualification call from QPS, latency, and integration numbers alone, before any prototype existed. |
| `ADP-1` | adaptability | 131 | 1-week ROI-math feasibility study scoped a no-precedent GenAI mandate -- learned the LLM stack via disqualification, not tutorials. |
| `COM-2` | communication | 132 | Walked manager off the agentic-search headline path using ROI math, not vision -- pivot was an infrastructure argument, not a pitch. |
| `PS-2` | problem_solving | 157 | Disqualified the headline agentic-search path with ROI math, then found low-hanging fruit at the relevance backlog -- creativity in scoping, not in building. |

## 3. Prune candidates (per-link accept/reject)

Three sub-buckets, roughly ordered by severity. The user reviews each row and decides KEEP / DROP / UPDATE-NOTE; this audit does NOT write to the DB (cut-before-schema means user approval is the gate). Every row includes the full `relevance_note` text so the decision can be made in-line without a round-trip to the database.

| Bucket | Count |
|--------|------:|
| (a) Old-framing placeholder | 3 |
| (b) Single-sentence boilerplate (< 60 chars, non-placeholder) | 3 |
| (c) Stale-framing (story scheduled for Phase-A-II rewrite) | 36 |
| **Total unique link rows flagged** | **42** |

### 3(a) Old-framing placeholders

These notes literally contain the old `Brand recall X story` placeholder text -- the story was re-titled but the link note was never rewritten. Recommended action: **DROP or UPDATE-NOTE**. A note like 'Brand recall two-part story' does not tell the drill-runner *which* facet of that story matches this question, so the link is doing less work than the title of the story it points to.

| link_id | question | story | note len | relevance_note |
|--------:|----------|-------|---------:|----------------|
| 184 | `ADP-3` | `BLOG-01` | 27 | Brand recall two-part story |
| 189 | `IMP-1` | `BLOG-01B` | 28 | Brand recall deep dive story |
| 181 | `PS-3` | `BLOG-01` | 27 | Brand recall two-part story |

### 3(b) Single-sentence boilerplate

Notes shorter than 60 characters with no explicit placeholder marker. Most are loose paraphrases of the question stem ('Mentored PhD interns through production stack transition' for LDR-1) rather than a specific facet lock. Recommended action: **UPDATE-NOTE** to a facet-specific line per `docs/bq_golden_trait_matrix.md`, or DROP if a stronger story already covers the same angle.

| link_id | question | story | note len | relevance_note |
|--------:|----------|-------|---------:|----------------|
| 159 | `EXE-5` | `EX-23` | 56 | Managed 30+ person project under VP 2-week test deadline |
| 64 | `LDR-1` | `EX-12` | 56 | Mentored PhD interns through production stack transition |
| 164 | `OWN-2` | `EX-23` | 48 | Went above and beyond to meet VP 2-week deadline |

### 3(c) Stale-framing (Phase-A-II rewrite targets)

Links attached to `EX-01`, `EX-02`, `EX-33`. These stories are scheduled to be rewritten per the golden trait matrix plan (T-P0-575/576/577/578); the note may not survive the rewrite untouched. Recommended action: **DEFER** decision until after story rewrite, then re-audit with the new STAR in hand. Listed here only so the scope of the post-rewrite re-audit is explicit now.

| link_id | question | story | note len | relevance_note |
|--------:|----------|-------|---------:|----------------|
| 6 | `ADP-14` | `EX-02` | 126 | Faced organizational roadblock (no experiment slots, out-of-scope mandate) and found creative workaround through team transfer |
| 124 | `ADP-17` | `EX-02` | 88 | Recognized own gap: had not translated business case into team OKR language early enough |
| 122 | `ADP-20` | `EX-01` | 85 | Self-initiated Hacker Week project driven by curiosity about abandoned query patterns |
| 9 | `ADP-4` | `EX-02` | 90 | Adapted approach mid-project: from pushing within wrong team to strategically transferring |
| 58 | `COL-3` | `EX-02` | 133 | Story I enrichment: drove project across multiple teams — from relevance team to final ranking team, multi-team production deployment |
| 59 | `COL-5` | `EX-02` | 124 | Story I enrichment: aligned different teams on shared goal — reframed diversity as ranking problem to gain cross-team buy-in |
| 259 | `COL-5` | `EX-33` | 147 | Align teams/stakeholders on shared goal - coalition building over several quarters with senior ICs and my manager before the empirical chip landed. |
| 8 | `COM-2` | `EX-02` | 84 | Persuaded new team to take on diversity ranking by reframing it as a ranking problem |
| 258 | `COM-2` | `EX-33` | 138 | Persuade others to change direction - core influence-without-authority match; convinced the org to deprecate a top-down strategic project. |
| 212 | `EXE-5` | `EX-01` | 114 | Delivered end-to-end prototype (data pipeline + algorithm + experiment framework) in one-week Hacker Week deadline |
| 211 | `IMP-10` | `EX-01` | 116 | Long-term impact: grew from one-week prototype to multi-year 200M+ initiative that changed org-wide ranking approach |
| 254 | `IMP-10` | `EX-33` | 111 | Long-term impact example - the full Allocation policy 200M+ GMB arc and team rename from ranking to allocation. |
| 56 | `IMP-2` | `EX-01` | 91 | Prioritized user experience: half of users on multi-intent queries were completely unserved |
| 260 | `IMP-4` | `EX-33` | 131 | Improved a process/system adding significant value - paradigm shift yielded 200M+ annualized GMB and a durable mental-model change. |
| 255 | `IMP-9` | `EX-33` | 131 | Short-term vs long-term tradeoff - forgoing carry-over protection and a 'launchable' MoE expert for long-term paradigm credibility. |
| 2 | `INN-1` | `EX-01` | 75 | Identified a problem no one else saw -- standard metrics masked the failure |
| 261 | `INN-1` | `EX-33` | 137 | Identified an opportunity for improvement - recognized the paradigm gap between pairwise ranking and the industry's whole-page direction. |
| 121 | `INN-10` | `EX-01` | 96 | Identified intent collapse as innovation area by questioning why standard metrics looked healthy |
| 3 | `INN-2` | `EX-01` | 86 | Entirely self-started project, from problem discovery to working prototype in one week |
| 210 | `INN-4` | `EX-01` | 87 | Innovative diversity-blending solution validated during Hacker Week, published at SIGIR |
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
| 252 | `PS-6` | `EX-33` | 130 | Calculated risk - short-term personal cost (no carry-over cover) traded for long-term org value (paradigm shift + 200M+ GMB tail). |

## 4. Coverage gaps (questions with 0 non-boilerplate links)

These are questions whose only links would all be pruned if every section-3 recommendation were accepted. They must be handled before pruning so we do not create 0-link questions: either (i) an existing flagged link gets UPDATE-NOTE instead of DROP, or (ii) a new link from an existing non-flagged story is added. Phase B (schema uplift) should not run until every question has >= 1 non-boilerplate link.

| question | category | total links | all flagged by | text |
|----------|----------|------------:|----------------|------|
| `OWN-9` | ownership | 2 | stale-framing | Explain a time when you had to move fast and innovate without all the informa... |
| `ADP-20` | adaptability | 1 | stale-framing | How do you stay motivated and engaged in your work? |
| `IMP-2` | impact | 1 | stale-framing | Describe a time when you prioritized user experience in a technical decision. |
| `INN-10` | innovation | 1 | stale-framing | How do you identify areas for innovation within an existing project? |
| `INN-2` | innovation | 1 | stale-framing | Tell me about a project or idea you started on your own. |
| `OWN-2` | ownership | 1 | boilerplate | Describe a situation where you went above and beyond to meet a deadline. |

