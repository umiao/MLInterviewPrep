# MLSD L5 Gap Audit (2026-04-18)

Gap audit of 10 existing Pillar 3 design-problem nodes (`framework_nodes.id` 89-97, 198) against the canonical L5 paradigm published in T-P0-510 (`framework_nodes.id=18`). Output of T-P1-511 (`T-MLSD-AUDIT-01`). Sole deliverable; no DB mutations.

## Methodology

Each problem is scored against id=18's **Appendix A · Unified Template Skeleton**. Two dimensions:

1. **Required Sections (8 scored, 0/1/2 each, max 16)** — drawn from Appendix A's ordered list. Scored columns skip the purely-administrative `# Title`, `> positioning`, and `## Prerequisites` items (these are boilerplate) and focus on the 8 content-heavy sections:
   - `§1 Clarify` — `## 1. Requirements Clarification` (functional / non-functional with numbers / out-of-scope)
   - `§2 Capacity` — `## 2. Capacity Estimation` (DAU -> QPS -> Storage -> Bandwidth chain)
   - `§3 Arch` — `## 3. High-Level Architecture` (3-5 services sliced by read/write + SLA)
   - `§4 DeepDive` — `## 4. Deep Dives` (>= 2 topics, 5-step: essence / options / pick+why / scale-out / edges)
   - `§5 DR` — `## 5. Reliability & Monitoring` (4-layer failure domain + downgrade table + SLO)
   - `§6 Summary` — `## 6. Summary & Tradeoffs`
   - `§Q&A` — `## Interview Q&A`
   - `§SelfCheck` — `## Self-Check` (mapped to id=18's 7-category pass-bar checklist)

   Scoring rubric per section:
   - `2` — fully present and meets L5 spec (structure, numbers, tables, or formulas as required).
   - `1` — topic present but informal; fails at least one Appendix A sub-requirement.
   - `0` — section absent or unrecognizable.

2. **Quality Gates (6 pass/fail, max 6)** — copied verbatim from Appendix A:
   - G1. Description length >= 8000 chars.
   - G2. Section 2 gives >= 2 concrete numbers and explicitly binds each to a downstream architecture decision.
   - G3. Section 3 has a table (or equivalent list) listing services and their SLA.
   - G4. Section 4 has >= 2 deep dives, each containing >= 1 pseudocode or SQL snippet.
   - G5. Section 5 contains >= 3 concrete SLOs (not generic "high availability").
   - G6. Self-Check maps each of id=18's 7 pass-bar categories (Requirements / Capacity / Architecture / DeepDive / Reliability / Monitoring / Communication).

Grand total = Section score (/16) + Gate score (/6) = **/22**.

## Score Matrix

| Node | §1 Clarify | §2 Capacity | §3 Arch | §4 DeepDive | §5 DR | §6 Summary | §Q&A | §SelfCheck | Total/16 | Gates/6 | Grand/22 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| id=89 Search & Retrieval | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=90 Recommendation Systems | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=91 Ads & Click Prediction | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=92 Marketplace & Logistics | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=93 NLP & LLM Systems | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=94 Computer Vision Systems | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=95 Fraud & Trust Safety | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=96 ML Infrastructure Design | 0 | 0 | 1 | 1 | 1 | 1 | 2 | 0 | 6/16 | 0/6 | **6/22** |
| id=97 Generative AI Systems | 0 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 5/16 | 0/6 | **5/22** |
| id=198 Real-Time Rec System | 2 | 1 | 1 | 1 | 2 | 0 | 2 | 2 | 11/16 | 2/6 | **13/22** |

**Distribution**: 9 of 10 problems score in a tight 5-6/22 band (classic skeleton); id=198 is an outlier at 13/22 because it was authored after Pillar 3 content-style shifted toward structured sections.

## Per-Problem Gap Summary

### id=89 Search & Retrieval Systems (5/22)

**Current heading inventory**: Overview, Core Concepts (Query Understanding Pipeline, Multi-Stage Retrieval Architecture, BM25 Scoring, Relevance Metrics, Learning to Rank), Implementation, Interview Patterns (Common Interview Questions), Comparisons, Key Takeaways, Advanced Topics (Hybrid Retrieval, Query Rewriting with LLM, Distributed Index Architecture).

**Has:**
- Rich ML/IR content on multi-stage retrieval, BM25, LTR (valuable raw material for §4).
- `## Interview Patterns -> Common Interview Questions` (re-labels to §Q&A cleanly).
- Mention of "low latency" and DAU framing (generic, not quantified).

**Missing (vs Appendix A):**
- All 6 L5-skeleton sections: no Clarification, Capacity, High-Level Arch (§3), Reliability & Monitoring (§5), Summary & Tradeoffs (§6), Self-Check.
- No Prerequisites link back to `id=18 System Design Framework`.
- `## 2. Capacity Estimation`: zero concrete numbers — needs `DAU=500M -> 100K avg QPS, peak 300K QPS -> index size 200TB -> 20 shards x 10TB each` style derivation.
- `## 3. High-Level Architecture`: has an "architecture" paragraph but NOT sliced by read/write + SLA. Needs table: Query Service (p99 50ms, read-heavy) / Indexing Service (batch write, throughput-oriented) / Ranking Service (p99 80ms, CPU-heavy) / Feature Store (p99 5ms, read-only).
- `## 4. Deep Dives`: existing "Advanced Topics" subsections are narrative, not 5-step. Needs essence/options/pick/scale-out/edges for at least 2 topics (e.g., inverted-index sharding strategy; hybrid BM25+BERT retrieval cost budget).
- `## 5. Reliability & Monitoring`: absent. Needs 4-layer failure domain + downgrade table (e.g., BERT retrieval down -> BM25-only fallback) + 3 SLOs.
- `## Self-Check`: absent.

**Recommended fill**: Apply the **Uniform Migration Recipe** (see below) + search-specific content: inverted-index sharding math (docs/shard), query rewrite latency budget, BM25 vs. dense retrieval tradeoff with recall/precision numbers, hybrid retrieval merge strategies.

### id=90 Recommendation Systems (5/22)

**Current heading inventory**: Overview, Core Concepts (System Architecture, Candidate Generation, Matrix Factorization, Deep Ranking Models, Ranking Loss Functions), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (Feedback Loop, Real-time Architecture, Diversity, Evaluation Beyond Accuracy).

**Has:**
- Strong ML content on funnel (CG -> ranking -> re-ranking), loss functions, MF/deep ranking.
- "Real-time Recommendation Architecture" subsection — partial §3 coverage.
- Some SLA-adjacent mention in Advanced Topics.

**Missing:**
- All L5-skeleton sections absent (§1, §2, §3-formal, §5, §6, Self-Check).
- No Prerequisites link to id=18.
- `§2 Capacity`: zero QPS/storage numbers. Needs DAU=100M -> 5B recs/day -> 60K QPS avg / 180K peak -> 200GB event log/day.
- `§3 Architecture`: "System Architecture" paragraph exists but no service-by-SLA table. Needs CG Service (p99 30ms) / Ranking Service (p99 100ms) / Re-Ranker (p99 20ms) / Feature Store (p99 5ms) breakdown.
- `§4 Deep Dives` not 5-step-structured.
- `§5 Reliability & Monitoring`: absent. Should add cold-start fallback chain, feature-store PSI monitoring, ranking-model timeout -> CG-only fallback.
- `§Self-Check`: absent.

**Overlap warning**: id=198 (Real-Time Rec) covers much of the same ground at a deeper level. When filling id=90, define clear scope: id=90 = general / textbook rec, id=198 = real-time Uber/DoorDash-style deep dive.

**Recommended fill**: Uniform Migration Recipe + point the Prerequisites/Deep Dive back to id=198 for the real-time deep dive; keep id=90 as the general canonical rec-system reference.

### id=91 Ads & Click Prediction (5/22)

**Current heading inventory**: Overview, Core Concepts (Ads Serving Pipeline, CTR Prediction, Feature Categories, Model Architecture Evolution, Auction Mechanisms, Calibration, Budget Pacing), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (Attribution, Creative Optimization, Privacy-Preserving Ads, Real-time Bidding Pipeline).

**Has:**
- Auction mechanism (GSP/VCG), calibration (Platt/isotonic), CTR models — excellent raw depth.
- "Ads Serving Pipeline" — informal §3.
- Privacy-preserving ads reference (important for Meta/Apple/Google relevance).

**Missing:**
- All L5-skeleton sections absent.
- `§2 Capacity`: no QPS / impression volume / storage numbers. Needs 200K QPS peak auction QPS -> impression log 5TB/day -> cold storage tier.
- `§3 Architecture`: no service-by-SLA table. Ads servers (p99 80ms, strict budget constraint), Bidder (p99 30ms), Budget-pacing Service (stateful), Attribution Pipeline (batch).
- `§4 Deep Dives`: narrative, not 5-step. Candidates: RTB pipeline design, CTR calibration for imbalanced data, budget pacing algorithms (PID vs LP).
- `§5 Reliability & Monitoring`: absent. Critical for ads: bidding-model timeout -> fallback to static CPM, budget-overrun circuit-breaker, audit-log consistency for ad revenue accounting.
- `§Summary`: Key Takeaways has bullets, not explicit tradeoffs-and-unexplored-points summary.
- `§Self-Check`: absent.

**Recommended fill**: Uniform Migration Recipe + ads-specific deep dives: RTB pipeline with wall-clock budget, multi-objective auction (eCPM vs user-experience), privacy sandboxing post-3P-cookie, feedback-loop bias in CTR training.

### id=92 Marketplace & Logistics (5/22)

**Current heading inventory**: Overview, Core Concepts (Two-Sided Marketplace Architecture, Dynamic Pricing/Surge, ETA Prediction, Matching/Dispatch Optimization, Key Metrics, Geospatial Features), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (Multi-Objective Optimization, Simulation Environment, Pricing Strategy Design, Order Batching & Routing).

**Has:**
- Strong Uber/DoorDash-relevant domain material: surge pricing, ETA, H3 geospatial indexing, dispatch.
- Two-sided market supply/demand framing.
- Multi-objective (driver earnings + rider ETA + marketplace balance) mention.

**Missing:**
- All L5-skeleton sections absent; this problem WILL be upgraded by T-P1-512 so gaps here are the canonical input to that task.
- `§2 Capacity`: no concrete numbers. Needs DAU=10M riders + 1M drivers, peak ride-request 30K QPS, location-update 200K QPS, trip log 1TB/day.
- `§3 Architecture`: pipeline exists in text but needs formal service table: Location Service (high-write-high-read, 200ms p99, Redis Geo) / Matching Service (read-heavy, 500ms p99, in-memory) / Trip Service (strong-consistent, 1s SLA, MySQL) / Payment Service (strong-consistent + audit, 2s SLA, MySQL + WAL). This is literally the example id=18 gives in Stage 3 — id=92 is the textbook candidate for that template.
- `§4 Deep Dives`: need 5-step on: (a) dispatch matching algorithm (greedy vs batched LP vs ILP) with scale-out; (b) surge-pricing loop with hotspot handling; (c) ETA prediction with feature freshness.
- `§5 Reliability & Monitoring`: absent. Must have: driver-location staleness threshold, trip-state idempotency, dispatch timeout -> fallback to simple-nearest, surge circuit-breaker, SLO on p99 dispatch latency + business metric (match-rate, cancel-rate).
- `§Self-Check`: absent.

**Priority 1 for fill** (T-P1-512 already staged). This is the single highest-leverage problem for the user's Uber final-round interview window.

### id=93 NLP & LLM Systems (5/22)

**Current heading inventory**: Overview, Core Concepts (LLM Application Architecture, RAG System Design, Prompt Engineering Patterns, Cost Optimization, Evaluation Framework), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (Fine-tuning Strategies, LLM Evaluation, Hallucination Mitigation).

**Has:**
- RAG architecture overview.
- Cost optimization and evaluation framework mentions (partial §2 and §5 flavor).
- Some SLA-adjacent mention (latency budget for RAG).

**Missing:**
- All L5-skeleton sections absent.
- `§2 Capacity`: mentions cost but no structured QPS/storage/bandwidth chain. Needs 10K RAG-QPS peak, 1M embeddings at 768d = ~3GB vector store, token-cost model.
- `§3 Architecture`: LLM Application Architecture paragraph, not service-by-SLA sliced. Needs Orchestrator (p99 500ms) / Vector DB (p99 20ms) / Re-Ranker (p99 50ms) / LLM Gateway (p99 variable with streaming). Plus storage-selection table (vector: Pinecone/Weaviate/pgvector; cache: Redis; document: S3).
- `§4 Deep Dives`: need 5-step on: (a) RAG vs fine-tuning decision framework; (b) vector-store sharding + freshness; (c) hallucination guard-rails.
- `§5 Reliability & Monitoring`: absent. Must add: LLM provider failover, context-window overflow downgrade, prompt-injection monitor, hallucination-rate as business SLO.
- `§Self-Check`: absent.

**Overlap warning**: id=97 Generative AI covers diffusion + GenAI, id=93 covers text/LLM — clear enough split if both are upgraded.

### id=94 Computer Vision Systems (5/22)

**Current heading inventory**: Overview, Core Concepts (CV Pipeline Architecture, Model Architecture Choices, Object Detection Metrics, NMS, Serving Considerations, Data Augmentation), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (Multi-Sensor Fusion, Data Flywheel for CV, Edge Deployment Optimization).

**Has:**
- Detection/NMS/mAP depth.
- "Serving Considerations" subsection — partial §3 / §5 hybrid.
- Edge deployment mention — relevant for L5 tradeoff discussion.

**Missing:**
- All L5-skeleton sections absent.
- `§2 Capacity`: no QPS or image-volume numbers. Needs 10K frame QPS peak, 1M images/day @ 2MB = 2TB/day storage, GPU cluster sizing.
- `§3 Architecture`: needs service-by-SLA table: Image Ingest (write-heavy, async), Detection Service (p99 300ms, GPU), Tracking Service (stateful, low-latency), Model Registry, Label Store.
- `§4 Deep Dives`: need 5-step on: (a) edge vs cloud inference tradeoff; (b) active-learning loop for label economics; (c) multi-sensor fusion failure modes.
- `§5 Reliability & Monitoring`: absent. Need: GPU memory OOM circuit-breaker, model-drift on production image distribution (domain shift), calibration on detection confidence.
- `§Self-Check`: absent.

**Priority**: lower for user's target set unless an interview explicitly targets CV (e.g., Tesla, autonomous vehicle cos).

### id=95 Fraud & Trust Safety (5/22)

**Current heading inventory**: Overview, Core Concepts (Fraud Detection Pipeline, Feature Engineering for Fraud, Class Imbalance Handling, Evaluation Metrics, Adversarial Considerations), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (Explainability, Adaptive Risk Thresholds, Anti-Money Laundering).

**Has:**
- Fraud-specific content: class-imbalance handling, precision/recall at specific operating points, adversarial considerations.
- Adaptive thresholds — partial §5 / §6 flavor.

**Missing:**
- All L5-skeleton sections absent.
- `§2 Capacity`: no transaction-volume numbers. Need 50K txn/QPS peak, 99.99%+ recall at 0.1% FP operating point.
- `§3 Architecture`: no service-by-SLA table. Need Real-Time Scoring (p99 50ms, sync), Review Queue (async), Case Management (human-in-loop), Feature Store for velocity features.
- `§4 Deep Dives`: need 5-step on: (a) cost-sensitive threshold selection; (b) graph-based fraud detection at scale; (c) adversarial-robust feature selection.
- `§5 Reliability & Monitoring`: absent. Critical for fraud: concept-drift from adversarial actors (weekly PSI), false-positive rate SLO (business impact), fallback to rules-engine when ML service times out.
- `§Self-Check`: absent.

**Priority**: lower for user's current target list unless explicitly targeted.

### id=96 ML Infrastructure Design (6/22)

**Current heading inventory**: Overview, Core Concepts (ML Platform Architecture, Training Pipeline Design, Model Serving Patterns, Feature Store Architecture, Model Monitoring, Safe Model Deployment), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (GPU Cluster Management, Experiment Tracking & Reproducibility, Continuous Training Pipeline).

**Has (stronger than siblings):**
- "ML Platform Architecture", "Model Serving Patterns", "Feature Store Architecture" cover ~2/3 of L5 §3 requirement.
- "Model Monitoring" and "Safe Model Deployment" give partial §5 coverage (hence +1 on §5 vs. peers).
- Six SLA/p-latency mentions in scattered bullets — most of any peer.

**Missing:**
- `§1 Clarification`: absent.
- `§2 Capacity`: one QPS mention, no DAU -> storage chain. Needs training data volume (100TB), model count (~1000), daily inference QPS aggregate, GPU node count estimate.
- `§3 Architecture` (partial): has component list but NOT sliced by read/write + SLA. Needs Training Orchestrator (batch, long-running), Serving Gateway (p99 50ms, read-heavy), Feature Store online (p99 5ms) / offline (batch), Model Registry (CRUD), Monitoring Pipeline (streaming).
- `§4 Deep Dives`: need 5-step on: (a) feature-store consistency (train-serve skew); (b) safe-deployment (canary + shadow + rollback); (c) multi-tenant GPU scheduling.
- `§5 Reliability & Monitoring` (partial, give 1): existing "Model Monitoring" + "Safe Deployment" cover some; missing 4-layer failure domain + formal downgrade table + concrete business SLO.
- `§Summary`: Key Takeaways exists; upgrade to explicit tradeoffs.
- `§Self-Check`: absent.

**Priority**: mid — highly relevant for L5+ signal (ML platform roles at large cos). Stronger starting state means smaller lift to upgrade.

### id=97 Generative AI Systems (5/22)

**Current heading inventory**: Overview, Core Concepts (GenAI Application Architecture, Model Selection Strategy, Diffusion Models - Image Generation, Serving Optimization, Safety & Alignment), Implementation, Interview Patterns, Comparisons, Key Takeaways, Advanced Topics (Diffusion Model Architecture Evolution, Video Generation Challenges, Content Safety Pipeline, Cost Optimization).

**Has:**
- GenAI-specific content: diffusion, safety, content moderation.
- Cost-optimization section — partial §2 flavor.

**Missing:**
- All L5-skeleton sections absent.
- `§2 Capacity`: no numbers. Needs requests/day, average tokens/image-size, GPU-hour / inference-cost model.
- `§3 Architecture`: need service-by-SLA: GenAI Gateway (p99 varies by modality), Model Server (GPU, batch), Content Safety Classifier (p99 200ms), Cache Layer (cost reduction), Storage for generated artifacts.
- `§4 Deep Dives`: need 5-step on: (a) diffusion-model serving (batching + cache); (b) content-safety pipeline (pre/post filters); (c) multi-modal model cost tradeoffs.
- `§5 Reliability & Monitoring`: absent. Need: model-provider failover, content-safety false-negative rate SLO, cost-per-request SLO (unit economics).
- `§Self-Check`: absent.

### id=198 Real-Time Recommendation System Design (13/22) — OUTLIER

**Current heading inventory**: Prerequisites, Key Terms, 1. Problem Framing & Clarify-First, 2. Baseline -> Deep Pipeline, 3. Two-Tower Retrieval + ANN, 4. Ranking: Deep Models + MTL, 5. Re-Ranking, 6. Training, 7. Cold Start (+ 7b Exploration), 8. Monitoring & Drift Detection, 9. Iteration Flywheel, 10. Latency vs Accuracy Tradeoffs, 11. Serving Architecture, 12. Interview Q&A, Self-Check.

**Has (closest to L5 of all 10 nodes):**
- Prerequisites link structure (but not to id=18 specifically — needs update).
- Section 1 "Problem Framing & Clarify-First" with mandatory clarification checklist (strong §1 = 2).
- Extensive deep-dive content across sections 3, 4, 5, 7, 10 (domain depth is excellent).
- Section 8 Monitoring + Drift Detection with PSI formula (partial §5 = 2 for monitoring emphasis + fallback chain in section 11).
- Section 11 Serving Architecture with ASCII diagram and component-level breakdown.
- Section 12 Interview Q&A is extensive.
- Self-Check present (§SelfCheck = 2).

**Missing (to reach L5 bar):**
- Prerequisites does NOT link back to id=18 System Design Framework — needs one-line reference per Appendix A spec.
- `§2 Capacity`: scattered mentions (p99 < 200ms, 1B DAU, 100M items) but NO structured DAU -> QPS -> Storage -> Bandwidth chain with explicit decision bindings.
- `§3 Architecture`: has ASCII diagram and component breakdown, but NO formal services-by-SLA table (row per service with read/write type, SLA, storage, rationale). Scattered SLAs need consolidation.
- `§4 Deep Dives`: deep topics exist but NOT structured as 5-step (essence / options / pick+why / scale-out / edges). Could be refactored without rewriting content.
- `§6 Summary & Tradeoffs`: absent. Section 10 is latency/accuracy tradeoff taxonomy, not a summary of the design's core decisions + tradeoffs + unexplored points.
- `§Self-Check` is topic-specific (two-tower, MMoE, ...) — does NOT map to id=18's 7 pass-bar categories. Needs reformulation to Requirements/Capacity/Architecture/DeepDive/Reliability/Monitoring/Communication buckets.

**Quality Gates** (2/6 passing):
- [x] G1 length >= 8000: PASS (13380 chars).
- [ ] G2 capacity 2 numbers + decisions: FAIL — numbers are scattered; no explicit "this number drives X decision" binding.
- [ ] G3 service + SLA table: FAIL — has ASCII diagram, no structured table.
- [ ] G4 Deep Dive pseudocode/SQL: FAIL — math formulas exist but no pseudocode or SQL blocks.
- [x] G5 >= 3 SLOs: PASS (p99 < 200ms end-to-end, FS p99 < 5ms, retrieval 30ms / pre-rank 20ms / ranking 100ms / re-rank 20ms).
- [ ] G6 Self-Check 7-category map: FAIL — current self-check is topic-based.

**Recommended fill for T-P1-513**: Targeted additions (NOT rewrite) — prepend a proper `## 2. Capacity Estimation` with DAU=1B -> QPS=500K peak -> storage breakdown; convert section 11 text+diagram into a formal services-SLA table; add `## 6. Summary & Tradeoffs`; refactor self-check into 7-category buckets with checkboxes. Preserve the rich domain content as-is.

## Prioritized Fill Order

Ranked by business relevance to user's upcoming interview context (project_uber_final_round for id=92, broad-applicability factor for id=198 / id=90, company signal intensity for remaining cards).

| Rank | Node | Driver | Existing Task |
|---|---|---|---|
| 1 | id=92 Marketplace & Logistics | Uber final round; id=18 Stage 3 uses ride-sharing as the canonical example so this problem has the strongest "example-of-the-template" fit | **T-P1-512 staged** |
| 2 | id=198 Real-Time Rec | Broadest applicability (covers 80% of rec-system interview questions); also has the shortest fill path because structure is 60% there | **T-P1-513 staged** |
| 3 | id=90 Recommendation Systems | Canonical rec-system reference; adjacent to id=198; high for DoorDash / Pinterest / Meta | *(fill task not yet staged)* |
| 4 | id=89 Search & Retrieval | Google / Pinterest / LinkedIn core; has solid ML depth to preserve | *(fill task not yet staged)* |
| 5 | id=91 Ads & Click Prediction | Meta / Google / TikTok ads-org relevance | *(fill task not yet staged)* |
| 6 | id=97 Generative AI Systems | LLM trend; OpenAI / Anthropic / any GenAI-focused interview | *(fill task not yet staged)* |
| 7 | id=96 ML Infrastructure Design | L5+ signal topic; already has strongest starting state so highest ROI per char | *(fill task not yet staged)* |
| 8 | id=93 NLP & LLM Systems | Overlap with id=97; fill after 97 to define scope split | *(fill task not yet staged)* |
| 9 | id=94 Computer Vision Systems | Niche unless target company demands CV | *(fill task not yet staged)* |
| 10 | id=95 Fraud & Trust Safety | Lower priority for user's current target roles | *(fill task not yet staged)* |

After T-P1-512 and T-P1-513 complete, Stage 4 task-staging should create **8 fill tasks** (`T-MLSD-FILL-<node_id>`) for ranks 3-10. This audit doc is the input for staging those fill specs.

## Uniform Migration Recipe (applies to id=89 / 90 / 91 / 93 / 94 / 95 / 96 / 97)

All 8 classic problems in this set share the identical starting skeleton: `Overview / Core Concepts / Implementation / Interview Patterns / Comparisons / Key Takeaways / Advanced Topics`. The migration to the L5 template is therefore mechanical:

### Step 1 — Demote existing ML content under `## 4. Deep Dives`

Move the 7 existing sections into an umbrella `## 4. Deep Dives` as `###` subsections. Preserve all content; only the heading level and order change.

```
## 4. Deep Dives

### 4.1 <Existing "Core Concepts" content, split into logically cohesive deep dives>

### 4.2 <"Advanced Topics" content, promoted to peer subsections>

### 4.3 ML-Domain Content (nested — matches Appendix A "Optional Sections")
  - Implementation
  - Comparisons
  - Key Takeaways
```

For each deep dive that is interview-critical (usually 2-3), wrap in the 5-step structure: **essence / options / pick+why / scale-out / edges**.

### Step 2 — Insert fresh L5 skeleton sections

Prepend (before the demoted §4) in exact order:

1. `> <one-line positioning>` (right after the title).
2. `## Prerequisites` — include the required line: `→ 参见 [id=18 System Design Framework](/kg?node=n18)`.
3. `## 1. Requirements Clarification` — functional / non-functional with concrete numbers / out-of-scope.
4. `## 2. Capacity Estimation` — full DAU -> QPS (avg + peak) -> Storage -> Bandwidth chain; every number must bind to a downstream decision.
5. `## 3. High-Level Architecture` — 3-5 services sliced by read/write + SLA in table form; include storage-selection-table.

Append (after the demoted §4):

6. `## 5. Reliability & Monitoring` — 4-layer failure domain + downgrade table + >= 3 SLOs (must include one business metric).
7. `## 6. Summary & Tradeoffs` — 3 biggest tradeoffs + what would deepen with 30 more minutes + design's biggest weakness + mitigation.
8. `## Interview Q&A` — rename existing "Interview Patterns / Common Interview Questions" verbatim.
9. `## Self-Check` — checkboxes against id=18's 7 categories.

### Step 3 — Domain-tailor fresh content per problem

Each problem's §2 capacity numbers, §3 service table, §5 SLOs, and §6 tradeoffs are domain-specific. The Uniform Recipe handles structure only; the domain-specific data points for each problem are in its **Per-Problem Gap Summary** above (the "Recommended fill" line of each node).

### Step 4 — Quality gate validation

Before committing, verify all 6 Appendix A Quality Gates pass:
1. length >= 8000 chars
2. §2 has >= 2 concrete numbers bound to decisions
3. §3 has service + SLA table
4. §4 has >= 2 deep dives, each with pseudocode/SQL
5. §5 has >= 3 concrete SLOs (not "high availability")
6. §Self-Check maps the 7 id=18 pass-bar categories

This recipe does NOT apply to id=198 (which is already partly structured — see T-P1-513 notes for targeted additions instead).

## Audit Closing Notes

- Total work remaining: after T-P1-512 (id=92) and T-P1-513 (id=198), an additional 8 fill tasks are needed (ranks 3-10 in the Prioritized Fill Order).
- This doc is the canonical input for Stage 4 fill-task staging; it lists both the uniform structural migration and the per-problem domain-specific fill pointers.
- No DB mutations were made by this audit — deliverable is this markdown file only.
