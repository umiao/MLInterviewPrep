# Progress Log

> Append-only session log. Each session adds an entry at the bottom.
> Never edit previous entries.

<!-- Entry format:

## YYYY-MM-DD HH:MM -- [T-XX-N] Brief Title
- **What I did**: 1-3 sentences on concrete actions taken
- **Deliverables**: List of files created/modified
- **Sanity check result**: What I verified and the outcome
- **Status**: [DONE] Done / [PARTIAL] Partial (what remains) / [BLOCKED] Blocked (why)
- **Request**: Cross off TASK-XXX / Move TASK-XXX to In Progress / No change

-->

> Older entries archived to [archive/progress_log.md](archive/progress_log.md).
> 150+ session entries archived as of 2026-04-10.


## 2026-04-08 -- [T-P1-314] SD Prep: Design Ticketmaster / Hotel Reservation
- **What I did**: Created seed script `scripts/content_interview_ticket_reservation.py` with all 8 sections in Chinese with English technical terms preserved. Covers seat inventory with distributed locking (PostgreSQL `SELECT FOR UPDATE SKIP LOCKED`), payment hold TTL (Redis TTL + DB fallback scanner), virtual queue for flash sales (Redis Sorted Set, 5000 users/batch), overbooking probability model (hotel scenario with no-show rate), idempotent payment processing (triple-layer: client key + DB UNIQUE + gateway Idempotency-Key), waitlist notification, anti-scalper measures (Verified Fan + device fingerprint + purchase limits). Capacity estimation: 50M users, 2M DAU, 500K daily orders, 1M+ concurrent users during flash sale, 15K peak seat-selection QPS (after virtual queue), 511 GB/year storage. Created SystemDesign DB record with slug `interview-ticket-reservation`, display_order=116. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_ticket_reservation.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 20,374 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-314 --status completed`

## 2026-04-08 -- [T-P1-315] SD Prep: Design a Web Crawler
- **What I did**: Created seed script `scripts/content_interview_web_crawler.py` with all 8 sections in Chinese with English technical terms preserved. Covers URL Frontier dual-layer design (priority queue + per-host queue), distributed crawling with consistent hashing and virtual nodes, Bloom Filter deduplication (10B URLs in 11.2 GB memory at 1% FPR), SimHash content dedup (Hamming distance <= 3), robots.txt politeness enforcement with per-domain token bucket rate limiting, multi-datacenter geographic crawling strategy, spider trap detection, and fault tolerance (RocksDB persistent Frontier + Kafka replay). Capacity estimation: 15B pages/month, ~5,800 avg QPS (17,400 peak), 4.6 Gbps bandwidth (13.8 peak), 300 TB/month storage, 35-63 crawler nodes. Created SystemDesign DB record with slug `interview-web-crawler`, display_order=117. Added topic card slug to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_web_crawler.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 22,744 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-315 --status completed`

## 2026-04-08 -- [T-P1-316] SD Prep: Design an Auction System (eBay)
- **What I did**: Created seed script `scripts/content_interview_auction_system.py` with all 8 sections in Chinese with English technical terms preserved. Covers real-time bidding via WebSocket + Redis Pub/Sub, bid ordering with Snowflake monotonic timestamps, auction state machine (SCHEDULED->ACTIVE->ENDING->CLOSED->SETTLING->COMPLETED), proxy bidding engine, anti-sniping soft close mechanism (5-min window with max extension cap), hot auction isolation via Kafka serialization pipeline, payment escrow flow, Shill Bidding detection (rule engine + ML anomaly detection). Capacity estimation: 1.65K avg bid QPS (8.3K peak), 248K peak read QPS, 10.4 TB/year bid storage, 30 GB Redis, 20 WebSocket servers for 1M concurrent connections. Created SystemDesign DB record with slug `interview-auction-system`, display_order=118. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_auction_system.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 24,271 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-316 --status completed`

## 2026-04-08 -- [T-P1-317] SD Prep: Design a Distributed Cache
- **What I did**: Created seed script `scripts/content_interview_distributed_cache.py` with all 8 sections in Chinese with English technical terms preserved. Covers consistent hashing with virtual nodes (150 VNodes/physical node), LRU/LFU/TinyLFU eviction policies, Cache-Aside vs Write-Through vs Write-Behind patterns, cache stampede prevention (Singleflight + probabilistic early refresh), hot key mitigation (L1 local cache + key replication), cache penetration defense (Bloom Filter + null caching), cache avalanche prevention (TTL jitter), CDC-driven invalidation pipeline (Debezium -> Kafka -> Invalidation Consumer), two-phase online migration for cluster resizing. Capacity estimation: 57K avg read QPS (173K peak), 5.7K avg write QPS (17K peak), 200 GB effective cache (300 GB with metadata), 10 nodes (5 Primary + 5 Replica). Created SystemDesign DB record with slug `interview-distributed-cache`, display_order=119. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_distributed_cache.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 24,637 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-317 --status completed`

## 2026-04-08 -- [T-P2-318] SD Prep: Update landing page with all topics + category grouping
- **What I did**: Refactored SystemDesignList.tsx Interview Prep tab to dynamically fetch topics from DB (display_order >= 100) instead of hardcoded array. Grouped 20 topics into 6 categories: Core Infrastructure (4), Social & Real-time (4), Location & Geo (2), Search & Data (4), Storage & Media (2), Specialized (4). Removed "Coming Soon" state -- all cards are now clickable. Kept difficulty badges and tags as client-side metadata map (TOPIC_META keyed by slug). Also fixed eBay tab to filter display_order < 100 so interview topics don't appear there.
- **Deliverables**: `src/frontend/src/pages/SystemDesignList.tsx` (modified)
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 20 topics covered in TOPIC_META. Category grouping renders correctly.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-318 --status completed`

## 2026-04-08 -- Google Recruiter Call Notes Sync
- **What I did**: Organized Google recruiter call notes from Discord into structured prep document. Created `docs/google_recruiter_call_prep.md` covering interview structure (Round 1 virtual: ML Domain 45min + G&L 45min; Round 2 onsite: Coding x2 45min each), key takeaways (ML paradigm iteration, data analysis, product insight, multi-team leadership, user-first mindset), self-intro draft, prep checklists, and cross-references to existing materials. Seeded document into DB as company_document #38. Updated Google company status from `applied` to `phone_screen`, set 5 interview stages, marked recruiter call event as completed.
- **Deliverables**: `docs/google_recruiter_call_prep.md` (new), `scripts/seed_google_prep.py` (new), DB records updated (companies, company_documents, interview_events)
- **Sanity check result**: Verified DB state -- Google status=phone_screen, 5 stages set (recruiter call completed), document #38 seeded (7516 chars), recruiter call event marked completed.
- **Status**: [DONE]

## 2026-04-09 -- Pinterest & DoorDash Interview Pipeline Updates
- **What I did**: (1) Converted Google prep doc to Chinese (`docs/google_recruiter_call_prep.md`), re-seeded to DB. (2) Created Pinterest recruiter call prep doc in Chinese (`docs/pinterest_recruiter_call_prep.md`), seeded as company_document #39, updated Pinterest status from `applied` to `phone_screen`, set 7 interview stages, marked recruiter call event completed. Created `scripts/seed_pinterest_prep.py`. (3) Added DoorDash ML Domain Knowledge interview event (Apr 14, 9:00-10:00 AM PDT, interviewer Ajaykrishna Karthikeyan), updated DoorDash interview stages.
- **Deliverables**: `docs/google_recruiter_call_prep.md` (updated to Chinese), `docs/pinterest_recruiter_call_prep.md` (new), `scripts/seed_pinterest_prep.py` (new), DB records updated for Google, Pinterest, DoorDash
- **Sanity check result**: Verified all three companies in DB -- Google doc updated, Pinterest status=phone_screen with 7 stages and doc #39 (4636 chars), DoorDash interview event #18 added with correct datetime and stages.
- **Status**: [DONE]

## 2026-04-09 -- DoorDash ML Domain Prep Task Planning
- **What I did**: Analyzed staging materials (`DoorDash_Search_RecSys_Interview_Prep.md`, 15K chars) and existing DB resources. Designed 7-task plan for comprehensive DoorDash ML Domain prep, expanding beyond the staging doc to include cutting-edge methods: generative retrieval (DSI/GENRE/TIGER), diffusion models for RecSys, multi-modal rec (CLIP), causal inference, RL slate optimization, CL4SRec, LightGCN, neural bandits, DCNv2, ESMM, PAL debiasing, etc. Recorded 7 tasks in task_db: T-P0-325 through T-P0-329 (5 P0 tasks) + T-P1-330, T-P1-331 (2 P1 tasks, T-P1-331 depends on all others). Regenerated TASKS.md.
- **Deliverables**: 7 tasks in task_db (T-P0-325 to T-P1-331), TASKS.md regenerated
- **Sanity check result**: All 7 tasks confirmed created with correct IDs, priorities, complexities, and dependencies. TASKS.md regenerated successfully.
- **Status**: [DONE] -- awaiting user approval to start execution via autonomous_run.sh

## 2026-04-09 -- [T-P0-325] DoorDash ML Domain: RecSys Architecture + Retrieval Deep Dive
- **What I did**: Created comprehensive prep doc (16.6K chars) covering multi-stage RecSys pipeline, Two-Tower model deep dive (architecture, loss functions, negative sampling, ANN serving), beyond-Two-Tower methods (MIND, PinSage, LightGCN, DSI/GENRE/TIGER generative retrieval), cold-start embedding strategies, DoorDash-specific challenges (three-sided marketplace, geo-sparsity, cross-vertical retrieval, real-time constraints), and 10 detailed Q&As. Created seed script and seeded to company_documents (id=40).
- **Deliverables**: docs/doordash_ml_domain_retrieval.md, scripts/seed_doordash_retrieval.py, DB record id=40
- **Sanity check result**: 1033 tests pass. Doc seeded to DB (16,599 chars). Content verified.
- **Status**: [DONE]

## 2026-04-09 -- [T-P0-326] DoorDash ML Domain: Ranking Models + Multi-Task Learning Deep Dive
- **What I did**: Created comprehensive prep doc (19.5K chars) covering: (1) Deep ranking architectures: Wide&Deep, DeepFM, DCN/DCN-v2, xDeepFM, AutoInt with comparison table. (2) MTL: Shared-Bottom, MMoE, PLE, ESMM, progressive training, negative transfer detection/mitigation. (3) DoorDash Universal Ranker architecture reconstruction with feature categories. (4) LTR: Pointwise/Pairwise/Listwise, LambdaMART, Deep LTR (cross-ref prep_learning_to_rank.md). (5) Multi-objective optimization: scalarization, uncertainty weighting, GradNorm, Pareto/MGDA/PCGrad. (6) Advanced: calibration (Platt/isotonic/temperature), delayed feedback (FNW/DEFER), sample selection bias, position bias (PAL/IPW). (7) 10 detailed Q&As. Created seed script and seeded to company_documents (id=41).
- **Deliverables**: docs/doordash_ml_domain_ranking.md, scripts/seed_doordash_ranking.py, DB record id=41
- **Sanity check result**: 1033 tests pass. Doc seeded to DB (19,485 chars). Content verified.
- **Status**: [DONE]

## 2026-04-09 -- [T-P0-327] DoorDash ML Domain: Feature Engineering + DL Modules for RecSys
- **What I did**: Created comprehensive prep doc (28K chars) covering: (1) Four feature categories with DoorDash mapping + supply/demand/real-time features. (2) Embedding techniques: ID, hashing trick (double hashing, signed hashing), sequence (mean pooling/GRU/Transformer), pretrained (BERT/CLIP), shared embedding tables. (3) Attention in RecSys: DIN (target attention), DIEN (interest evolution + AUGRU), BST (Transformer + target token), AutoInt (cross-ref ranking doc). (4) Sequence modeling: GRU4Rec, SASRec (causal Transformer), BERT4Rec (bidirectional), CL4SRec (contrastive learning). (5) GNN: GraphSAGE, GAT, PinSage (industrial 30B scale), LightGCN. (6) Feature interaction: FM, FFM, FiBiNET (SENET + bilinear). (7) DoorDash architecture synthesis diagram. (8) 10 detailed Q&As. Created seed script and seeded to company_documents (id=42).
- **Deliverables**: docs/doordash_ml_domain_features_dl.md, scripts/seed_doordash_features_dl.py, DB record id=42
- **Sanity check result**: 1033 tests pass. Doc seeded to DB (28,001 chars). Content verified.
- **Status**: [DONE]

## 2026-04-09 -- [T-P0-328] DoorDash ML Domain: Search + Semantic Matching + Bias/Debiasing
- **What I did**: Created comprehensive prep doc (23K chars) covering: (1) Query Understanding: intent classification, query rewriting (spell correction, expansion, relaxation), NER (BiLSTM-CRF/BERT), full pipeline diagram. (2) Semantic Matching evolution: BM25 -> DSSM (dual-tower) -> ColBERT (late interaction MaxSim) -> Cross-Encoder BERT, with comparison table and DoorDash stage mapping. (3) DoorDash Search Evolution: Phase 1 (LR+ES), Phase 2 (DNN + dual-tower + MTL), Phase 3 (cross-vertical unified search). (4) Bias/Debiasing: position bias (IPW, ULTR, PAL), exposure bias, selection bias (MNAR, DR estimator), popularity bias (calibration, causal debiasing), summary table. (5) Exploration vs Exploitation: epsilon-greedy, UCB, Thompson Sampling, contextual bandits (LinUCB), neural bandits, DoorDash exploration injection design. (6) Diversity/Fairness: MMR, DPP, fairness constraints, re-ranking pipeline. (7) Full DoorDash search architecture diagram. (8) 10 detailed Q&As. Created seed script and seeded to company_documents (id=43).
- **Deliverables**: docs/doordash_ml_domain_search.md, scripts/seed_doordash_search.py, DB record id=43
- **Sanity check result**: 1033 tests pass. Doc seeded to DB (23,091 chars). Content verified.
- **Status**: [DONE]

## 2026-04-09 -- [T-P0-329] DoorDash ML Domain: ML Fundamentals Rapid Review + Quick-Fire Q&A
- **What I did**: Created comprehensive prep doc (18K chars) covering: (1) Optimization: SGD family comparison table (SGD/Momentum/Nesterov/Adagrad/RMSProp/Adam/AdamW/LAMB) with Adam formula details. (2) LR Scheduling: Step/Cosine/Warmup+Cosine/OneCycle/ReduceOnPlateau with warmup rationale. (3) Gradient Issues: vanishing/exploding/dead ReLU with solutions. (4) Regularization: L1/L2/ElasticNet with L1 sparsity explanation, Dropout variants, BN/LN/IN/GN/RMSNorm comparison. (5) Evaluation Metrics: Classification (AUC-ROC/PR-AUC/LogLoss), Ranking (NDCG/MAP/MRR), Calibration (ECE/Platt/Temperature), Offline-Online Gap analysis. (6) Loss Functions: Classification (BCE/CE/Focal/Hinge), Metric Learning (Contrastive/Triplet/InfoNCE), Ranking (BPR/ListNet/LambdaRank). (7) Overfitting/Underfitting diagnosis + Bias-Variance tradeoff. (8) Convex vs Non-Convex optimization. (9) Weight Initialization + Activation Functions. (10) Feature Engineering for DoorDash. (11) 10 detailed quick-fire Q&As with follow-ups. (12) Summary cheatsheet. Created seed script and seeded to company_documents (id=44).
- **Deliverables**: docs/doordash_ml_domain_fundamentals.md, scripts/seed_doordash_fundamentals.py, DB record id=44
- **Sanity check result**: 1033 tests pass. Doc seeded to DB (18,058 chars). Content verified.
- **Status**: [DONE]

## 2026-04-09 -- [T-P1-330] DoorDash ML Domain: LLM+RecSys Frontiers + Cross-Vertical Transfer
- **What I did**: Created comprehensive prep doc (21.8K chars) covering: (1) LLM+RecSys 4 integration paradigms: Feature Extractor, Scoring/Reranker, Conversational Agent, Generator with DoorDash examples. (2) Cross-Vertical Feature Generation: three-sided marketplace challenges, Hierarchical RAG architecture, FAN (Familiarity+Affordability+Novelty) framework with formulas. (3) Semantic ID + Generative Recommendation: RQ-VAE, TIGER/P5/GPT4Rec comparison, DoorDash hierarchical taxonomy design. (4) Frontier Methods: Diffusion models (DiffRec), Multi-Modal CLIP-based rec, Causal Inference (IPS/Doubly Robust/position bias), RL for Slate Optimization (contextual bandits, SlateQ). (5) Prompt-Based Recommendation: P5-style unified framework, In-Context Learning for cold-start. (6) LLM vs Traditional RecSys trade-off table. (7) 7 detailed Q&As: cross-vertical LLM enhancement, Semantic ID advantages, diffusion ROI, RL vs greedy ranking, LLM ROI evaluation framework, latency-aware deployment architecture, eBay-to-DoorDash experience mapping. (8) Summary cheatsheet with 12 topic rows.
- **Deliverables**: docs/doordash_ml_domain_llm_frontier.md, scripts/seed_doordash_llm_frontier.py, DB record id=45
- **Sanity check result**: 1033 tests pass. Doc seeded to DB (21,781 chars). Content verified.
- **Status**: [DONE]

## 2026-04-09 -- [T-P1-331] DoorDash ML Domain: Case Study Mock Answers + SCOPE Templates
- **What I did**: Created comprehensive case study prep doc (30.9K chars) covering: (1) SCOPE framework reference with time budgets. (2) 5 full case studies with SCOPE structure: Restaurant Recommender (4-stage pipeline, DCN-v2+MMoE), Spicy Ramen Search (hybrid retrieval, 2-pass ranking), Cold-Start Merchant (content-based warm-start, Thompson Sampling), Multi-Objective Homepage (scalarization+constraints, fairness bonus), Cross-Vertical Transfer (shared encoder, LLM feature bridge, FAN framework). (3) 7 deep dive follow-up Q&As: position bias, A/B testing, feature freshness, feedback loops, merchant fairness, surge handling, online vs batch learning. (4) eBay experience mapping with interview talking points for 3 parallels. (5) Clarifying question templates (4 categories). (6) Sprint checklist (Day -3 to Day). (7) Summary cheatsheet.
- **Deliverables**: docs/doordash_ml_domain_case_study.md, scripts/seed_doordash_case_study.py, DB record id=46
- **Sanity check result**: 1033 tests pass. Doc seeded to DB (30,917 chars). Content verified.
- **Status**: [DONE]

## 2026-04-09 -- LC 1834 Single-Threaded CPU solution update
- **What I did**: Updated LeetCode problem 1834 (Single-Threaded CPU, id=554) with user's solution and detailed analysis. Added DoorDash to company_tags (now: LinkedIn, Uber, Adobe, DoorDash). Wrote notes covering: Heap + Simulation approach, O(n log n) complexity, SJF greedy pattern, edge cases (same arrival time, idle gaps, tie-breaking), related problems (LC 253/621/1882). Marked is_completed=1.
- **Deliverables**: DB problem id=554 updated (notes 2.4K chars, company_tags, is_completed, last_attempted_at)
- **Sanity check result**: Verified DB -- tags=["LinkedIn","Uber","Adobe","DoorDash"], is_completed=1, notes length=2415.
- **Status**: [DONE]

## 2026-04-09 -- Pinterest phone screen event added
- **What I did**: Added Pinterest Technical Virtual Phone Interview event (Apr 16, 2:00-3:00 PM PDT, Sr. MLE Core Engineering) as interview_event #19. Updated Phone Screen stage status from "upcoming" to "scheduled".
- **Deliverables**: DB interview_events #19, company stages updated
- **Sanity check result**: INSERT confirmed (id=19), stage update confirmed.
- **Status**: [DONE]

## 2026-04-10 -- Baking Studio improvement task planning
- **What I did**: Explored Baking Studio codebase (RecipeCard, BakingStudio, FilterBar, RecipeCombiner, ScalingCalculator, baking_seed.py) and planned 3 improvement tasks: T-P1-332 (compact RecipeCard UI + category grouping with captions), T-P1-333 (multi-size 4+6 inch toggle select with ingredient summing), T-P1-334 (add 3 new recipes: coconut jelly, sago, mango cream). All recorded in task_db, TASKS.md regenerated.
- **Deliverables**: 3 tasks in task_db (T-P1-332 to T-P1-334), TASKS.md regenerated
- **Sanity check result**: All 3 tasks confirmed created with correct IDs and descriptions.
- **Status**: [DONE] -- awaiting user approval to execute

## 2026-04-10 -- [T-P1-332] Baking Studio compact RecipeCard + category grouping
- **What I did**: Redesigned RecipeCard to be compact (reduced padding, smaller text, single-row name+badge layout, truncated names). Added category grouping in BakingStudio browse mode -- recipes are now grouped under section headers (Base/Cream/Decoration/Complete) with descriptive captions. Removed unused category pill from cards since category is now shown via section headers. Maintained per-cake-type color themes.
- **Deliverables**: RecipeCard.tsx (compact layout), BakingStudio.tsx (category grouping with CATEGORY_SECTIONS + groupByCategory)
- **Sanity check result**: TypeScript type check passes, Vite build succeeds
- **Status**: [DONE]

## 2026-04-10 -- [T-P1-334] Baking Studio: add 3 new recipes
- **What I did**: Added 3 new preset recipes to baking_seed.py: Coconut Milk Jelly (cream, 5 ingredients), Sago (decoration, 1 ingredient), Mango Cream (cream, 3 ingredients). All cream_cake type, universal size. Added 4 new inventory items (coconut milk, gelatin sheets, sago, mango jam).
- **Deliverables**: src/backend/services/baking_seed.py (recipes #10-12 + 4 inventory items)
- **Sanity check result**: All 12 recipes load correctly, 1033 tests pass
- **Status**: [DONE]

## 2026-04-10 -- [T-P1-333] Baking Studio: multi-size select (4+6 inch) with ingredient summing
- **What I did**: Changed FilterBar size selector from single-select to multi-toggle (checkbox-like). Clicking 4-inch and 6-inch independently toggles each; "All" clears selections. Updated RecipeFilters type (size -> sizes array), useBaking hook (client-side multi-size filtering), and extended ScalingCalculator's multi-size ingredient summing from chiffon-only to all recipe types. FilterBar selections flow through RecipeDetail to ScalingCalculator via filterSizes prop.
- **Deliverables**: FilterBar.tsx, ScalingCalculator.tsx, RecipeDetail.tsx, BakingStudio.tsx, baking.ts (RecipeFilters), useBaking.ts
- **Sanity check result**: TypeScript check clean, Vite build succeeds, 1033 tests pass
- **Status**: [DONE]

## 2026-04-10 -- Baking Studio hotfixes: missing recipes + card compaction
- **What I did**: (1) Inserted 3 new recipes directly into DB (coconut jelly #10, sago #11, mango cream #12) -- seed function was skipping because `if existing == 0` check blocked insertion when presets already existed. Added 4 new inventory items. (2) Fixed `seed_baking_data()` to check by name instead of count, so new presets are inserted alongside existing ones. (3) Further compacted RecipeCard to single-line layout: [size icon] [name + zh name inline] [ingredient count] [type badge], reduced padding to `px-2.5 py-1.5`, grid gap `gap-1.5`, section spacing `space-y-4`.
- **Deliverables**: `RecipeCard.tsx` (compacted), `BakingStudio.tsx` (tighter spacing), `baking_seed.py` (fixed seed logic), DB updated with 3 recipes + 4 inventory items
- **Sanity check result**: TypeScript clean, 1033 tests pass, DB verified with 12 recipes and 24 inventory items.
- **Status**: [DONE]

## 2026-04-10 -- Baking Studio: fix recipe visibility + build + Playwright verification
- **What I did**: (1) Found recipes weren't visible because earlier DB insert didn't persist (WAL mode concurrent connection issue). Re-inserted 3 recipes (Coconut Milk Jelly #10, Sago #11, Mango Cream #12) + 4 inventory items, verified via API (12 recipes returned). (2) Fixed TypeScript build error -- `tsc -b` (strict mode in tsconfig.app.json) required explicit type annotation on `items.map((recipe: BakingRecipe))` that `tsc --noEmit` didn't catch. Rebuilt frontend dist/. (3) Used Playwright to take headless screenshot of Baking Studio page, verifying cards are compact single-line layout, category grouping works, and all 12 recipes visible.
- **Deliverables**: `BakingStudio.tsx` (type fix), `dist/` rebuilt, DB verified with 12 recipes, Playwright screenshot at `data/baking_studio_screenshot.png`
- **Sanity check result**: API returns 12 recipes, `npm run build` succeeds, Playwright screenshot confirms visual layout.
- **Status**: [DONE]

## 2026-04-10 -- Visual testing harness: RCA + revised plan + task recording
- **What I did**: (1) Conducted root cause analysis of 4 Baking Studio failures -- identified unified root cause: "validating on a surface not isomorphic to the production path." (2) Designed initial visual testing harness (Playwright pixel diff), received reviewer feedback that it was over-engineered. (3) Revised plan per reviewer: dropped pixel diff/baseline/PostToolUse hooks (YAGNI), refocused on `npm run build` in Stop hook + DOM assertions + API curl smoke check. (4) Recorded 4 tasks: T-P0-335 (npm run build in Stop hook), T-P0-336 (smoke_check.py with DOM + API assertions), T-P0-337 (CLAUDE.md validation rules), T-P1-338 (screenshot archiving, no diff). (5) Updated LESSONS.md with unified production-path validation lesson.
- **Deliverables**: 4 tasks in task_db (T-P0-335 to T-P1-338), LESSONS.md updated, TASKS.md regenerated
- **Sanity check result**: All 4 tasks confirmed created. LESSONS.md entry verified.
- **Status**: [DONE] -- awaiting user approval to execute P0 tasks

## 2026-04-10 -- [T-P0-335] Stop hook: add npm run build to test_check.py
- **What I did**: Added `run_frontend_build()` function to `.claude/hooks/test_check.py` that runs `npm run build` (which executes `tsc -b && vite build`) before allowing session exit. This ensures the Stop hook validates against the production build path, not just tests. Used `shutil.which("npm")` to resolve npm path on Windows (bare `npm` fails in subprocess but `npm.cmd` is found by `shutil.which`). Gracefully skips if npm or package.json not found.
- **Deliverables**: `.claude/hooks/test_check.py` updated
- **Sanity check result**: Ran hook directly via `/c/Anaconda/python.exe .claude/hooks/test_check.py` -- both frontend build and pytest passed, exit code 0. Also verified `npm run build` independently succeeds in src/frontend/.
- **Status**: [DONE]

## 2026-04-10 -- [T-P0-337] CLAUDE.md: add production-path validation rules
- **What I did**: Added two hard rules to the Verification Requirements section of CLAUDE.md: (1) Side-effect verification must go through the consumer (API curl), not the producer (DB SELECT). (2) Validation must use the production build path (npm run build, not tsc --noEmit). Both rules encode the root lesson from T-P0-335: verification must happen on a surface isomorphic to the production path. Also archived older PROGRESS.md entries to archive/progress_log.md.
- **Deliverables**: `CLAUDE.md` updated (2 new rules in Verification Requirements), `PROGRESS.md` archived
- **Sanity check result**: 1033 tests pass. CLAUDE.md rules are clear and actionable.
- **Status**: [DONE]

## 2026-04-10 -- [T-P0-336] Smoke check: DOM assertions + API verification script
- **What I did**: Created `scripts/smoke_check.py` with (1) server liveness checks for localhost:5173 and localhost:8100, (2) Playwright-based DOM assertions for 4 key pages (/, /baking, /problems, /system-design) checking element existence and count lower bounds, (3) API verification for 3 endpoints (/api/baking/recipes >= 10, /api/problems >= 1, /api/system-design/topics >= 1) using urllib, (4) graceful skip (exit 2) when servers not running. Created `tests/test_smoke_check.py` with 7 tests including a mock HTTP server for API checks. Could not integrate into `test_check.py` Stop hook due to sensitive file permissions in autonomous mode -- script runs standalone.
- **Deliverables**: `scripts/smoke_check.py` (new), `tests/test_smoke_check.py` (new)
- **Sanity check result**: 1040 tests pass (7 new). Script exits gracefully with code 2 when servers not running.
- **Status**: [PARTIAL] Stop hook integration in test_check.py blocked by sensitive file permissions -- needs interactive session.

## 2026-04-10 -- [T-P1-338] Smoke check: add screenshot archiving
- **What I did**: Extended `scripts/smoke_check.py` with screenshot archiving: after DOM assertions pass for each page, saves a full-page screenshot to `data/visual_archive/{slug}_{timestamp}.png`. Added auto-cleanup to keep only last 10 screenshots per page slug. Helper functions: `_page_slug()` (path to filesystem slug), `_cleanup_old_screenshots()` (prune oldest beyond limit), `_save_screenshot()` (save + cleanup). The `run_page_checks()` now accepts an optional `archive_dir` parameter for testability. Added 9 new tests covering slug conversion, cleanup logic, and screenshot save/error handling.
- **Deliverables**: `scripts/smoke_check.py` (modified), `tests/test_smoke_check.py` (modified)
- **Sanity check result**: 1049 tests pass (9 new).
- **Status**: [DONE]

## 2026-04-10 -- LC 1055: Pinterest tag + Chinese solution note
- **What I did**: (1) Added "Pinterest" to `company_tags` on problem row 498 (leetcode_id 1055, Shortest Way to Form String) -- now ["LinkedIn","Uber","Adobe","Pinterest"]. (2) Wrote ~2.8k-char Chinese solution note following existing format sections (思路 / 关键技巧 / 核心代码 / 注意点 / 复杂度 / 另一种思路). Note preserves the user-provided greedy + binary-search Python code verbatim and briefly mentions the alternative `next[i][c]` preprocessing approach (position-0 -1 check for no-solution detection) without writing that implementation. (3) Marked `is_completed = 1` per feedback_problem_db_sync.md convention.
- **Deliverables**: `data/mle_prep.db` row 498 updated; `scripts/_update_1055.py` idempotent one-off update script (follows existing `_update_*.py` pattern).
- **Sanity check result**: Queried DB post-update -- company_tags contains Pinterest, notes length 2782, is_completed=1, UTF-8 Chinese characters read back correctly. URL + description already present (no fetch needed).
- **Status**: [DONE]

## 2026-04-10 -- LC 1055: code cleanup + DP alternative
- **What I did**: Extended the solution note per user follow-up. (1) Cleaned up the original greedy+bisect code: removed unused `nSource`/`nTarget`, replaced hand-rolled binary search with `bisect.bisect_left` (original had dead `mid` computation after the `while` loop), collapsed two-pass preprocessing into single `defaultdict(list)` pass, hoisted the -1 check to an up-front `set(target) - set(source)` check, added inline comment on `return ans + 1` wrap semantics. (2) Wrote full DP alternative: `nxt[i][c]` table of size (n+1)x26, filled backwards — `nxt[n][*] = -1`, `nxt[i][c] = i if source[i] == c else nxt[i+1][c]` — giving O(1) per-char lookup in the main loop. Total O(26n + m) time, O(26n) space. (3) Replaced 核心代码 and 另一种思路 sections; notes length now 4781 chars.
- **Deliverables**: `scripts/_update_1055_v2.py` (idempotent), `data/mle_prep.db` row 498 `notes` updated.
- **Sanity check result**: Ran both implementations against 5 cases: `("abc","abcbc")=2`, `("abc","acdbc")=-1`, `("xyz","xzyxz")=3`, `("abc","abc")=1`, `("abc","aaa")=3`. All pass. Idempotent re-run prints `[SKIP] ... already up to date`.
- **Status**: [DONE]

## 2026-04-10 -- LC 2128: add problem + Chinese solution note (Google)
- **What I did**: Inserted new problem row for LC 2128 "Remove All Ones With Row and Column Flips" (Premium, previously not in DB). Set URL, fetched description, tags=["Math","Bit Manipulation","Matrix","XOR","Greedy"], pattern="Math", is_completed=1, comfort_level=3. Wrote ~3.6k-char Chinese solution note with sections 思路 (GF(2) derivation: grid[i][j] = r_i XOR c_j, so every row must equal first row or its complement) / 关键技巧 / 核心代码 (user's base solution) / 注意点 / 复杂度 / 空间优化 (O(1) extra space: compare element-by-element against grid[0][j] or grid[0][j]^1 based on grid[i][0] vs grid[0][0]) / 另一种思路. Per user follow-up, added "Google" to company_tags (now ["LinkedIn","Uber","Adobe","Google"]) — user confirmed this is primarily a Google problem.
- **Deliverables**: `data/mle_prep.db` new row id=1065, `scripts/_update_2128.py` idempotent update script.
- **Sanity check result**: Ran both V1 (base) and V2 (O(1)-space) against 3 test cases: `[[0,1,0],[1,0,1],[0,1,0]]`=True, `[[1,1,0],[0,0,0],[0,0,0]]`=False, `[[0]]`=True — all pass. DB post-update: company_tags contains Google, notes length 3606, UTF-8 roundtrip verified.
- **Status**: [DONE]

## 2026-04-10 -- Record Uber final round schedule in dashboard
- **What I did**: Inserted 4 Uber final-round interview events into `interview_events` table (rows 20-23, company_id=5, status=upcoming, all 60min, location=Zoom). Apr 27: Coding 2 (Bo Cui, 10-11am PDT, event_type=technical), Design & Architecture New Problem (Ke Chen, 1:30-2:30pm PDT, event_type=system_design), Collaboration & Leadership (Yifan Ma, 3:30-4:30pm PDT, event_type=behavioral). Apr 29: Coding 1 Algorithms & DS (Ali Shameli, 11am-12pm PDT, event_type=technical). All times stored as naive Pacific per project convention. Also saved `project_uber_final_round.md` memory entry to orient future MLInterviewPrep prep sessions toward this deadline.
- **Deliverables**: `scripts/_add_uber_final_round.py` (idempotent insert), `data/mle_prep.db` rows 20-23, memory file `project_uber_final_round.md` + MEMORY.md index entry.
- **Sanity check result**: Queried DB post-insert — all 4 rows present with correct event_type (matching `ck_event_type` constraint from `src/backend/models/timeline.py` EVENT_TYPES tuple) and status=upcoming. Re-ran script, all 4 rows skipped (idempotent).
- **Status**: [DONE]

## 2026-04-10 -- Cross-project unpushed-commit audit + safe push
- **What I did**: Scanned all 8 git repos in the workspace for unpushed commits, ran `scripts/scan_secrets.py --all --json` + per-commit diff secret scan. Findings: 913 scanner hits, 0 real secrets in tracked files or unpushed diffs (all live credentials live in gitignored `.env`/`.secret`). 3 repos had ahead-only unpushed commits; 1 (blog_proj main) was diverged (1 ahead / 5 behind) and deliberately SKIPPED to avoid destroying 5 upstream commits. Pushed: MLInterviewPrep main (67 commits, a84eafd→943275f), helixos main (2 commits, a6530b4→4d5ee14), blog_proj blog-refactor (10 commits, 79b7a7e→e1003ad).
- **Deliverables**: 3 successful `git push origin <branch>` operations (no --force). blog_proj main intentionally untouched.
- **Sanity check result**: Post-push `git log @{u}..HEAD` = 0 for all 3 pushed branches. blog_proj main still reports 5 behind / 1 ahead (unchanged, as intended). No secret scanner findings in any pushed diff.
- **Status**: [DONE]. Follow-up needed from user: decide how to reconcile blog_proj main divergence (merge/rebase the 5 upstream commits or intentionally force-push — requires judgment, not pre-authorized).
