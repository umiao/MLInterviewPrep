# Uber VO ML Coding + ML System Design — Content Inventory & Gap Audit

> **Task**: T-P0-628 ([UBER-VO-1])
> **As-of**: 2026-04-29
> **Source TXT digested**: `Uber_VO_ML Design和Coding准备.txt` — **973 lines** (4 ML Coding interview prompts + 2 Staff-level ML SD Golden Answers, sourced via Perplexity prep loop on Uber tech-blog + reported VO experience)
> **Scope**: Complete inventory of every ML Coding + ML System Design topic that should land in the Uber VO prep, sourced from BOTH the new staging file AND the 11 existing Uber `company_documents` rows in `data/mle_prep.db`.
> **Downstream gates**: T-P0-629 (ML Coding seed), T-P0-630 (ML SD seed), T-P1-631 (id=33 + id=37 strengthening), T-P1-635 (audit-discovered companion items).

---

## Table of Contents

1. [Per-doc Inventory (all 11 Uber DB docs)](#1-per-doc-inventory)
2. [NEW — items needing fresh Staff-level seeding](#2-new--items-needing-fresh-staff-level-seeding)
3. [EXISTING-NEEDS-STRENGTHENING — id=33 + id=37 search/rec gaps](#3-existing-needs-strengthening--id33--id37-searchrec-gaps)
4. [OUT-OF-SCOPE — explicitly excluded](#4-out-of-scope--explicitly-excluded)
5. [13-Keyword Gap Matrix (search/rec strengthening keywords)](#5-13-keyword-gap-matrix)
6. [Source TXT topic mapping (4+2 items)](#6-source-txt-topic-mapping)
7. [Counts smoke check](#7-counts-smoke-check)

---

## 1. Per-doc Inventory

| id | Title | ML Coding? | ML SD? | Key topics covered | Depth tier | Notes |
|----|-------|-----------|--------|--------------------|-----------|-------|
| 3  | Uber BPS Phone Screen Prep | Partial | Pointer | KNN, bias-variance, eval metrics, CV, regularization, decision trees, boosting | Skeleton+bullets | BPS phone-screen ML-fundamentals warmup |
| 30 | Uber BPS LeetCode Solutions Guide | None | None | BS, tree, DP, etc. | Pointer-only | Pure CS algorithms |
| 31 | Uber BPS Custom Problem Solutions | None | None | prefix sum, OOD patterns | Pointer-only | Pure CS algorithms |
| 32 | Uber BPS Pattern Cheat Sheet by Algorithm | None | None | 16 algo patterns (BFS, DFS, DP, UF, heap...) | Pointer-only | Pure CS algorithms |
| 33 | Uber BPS Design & Architecture Prep | Pointer | Yes | **Ranking-as-Allocation**, MoE, pointwise scoring, allocator (LP/ILP), LLM eval pipeline, **H3**, ETA, dispatch, surge, cart, Michelangelo (referenced) | Staff Golden (partial) | **Primary search/rec strengthening surface**; missing 8 of 13 strengthening keywords |
| 34 | Uber BPS KNN & ML Fundamentals Review | Yes | None | **KNN from scratch** (6 distance metrics, KD-tree / Ball-tree / LSH), bias-variance, overfitting, L1/L2 regularization, CV, precision/recall/F1/AUC, feature engineering | Staff Golden (KNN only) | Deep ML coding for KNN; NO linear/logistic-reg from-scratch, NO kmeans, NO geometric median |
| 35 | Uber BPS Timed Mock Interview Sets | None | None | tree/DP, BFS/prefix sum, graph problem sets | Pointer-only | Pure timed CS practice |
| 36 | Uber HR Call Prep Notes | None | Pointer | Ranking-as-Allocation gloss, LLM eval gloss, ETA, pricing, matching | Skeleton+bullets | Business/culture focus; ML SD only as conversation prompts |
| 37 | Uber VO 完整准备指南 (Virtual Onsite) | Pointer | Pointer | Round 2 ML coding **checklist** (Linear/Logistic Reg, Decision Tree, KNN, K-Means, GD, CV, metrics, bias-variance) — checklist only, NO implementations; Round 3 SD checklist (URL shortener, ride-share, dispatch, ETA, surge — generic) | Skeleton+bullets | **Existing VO checklist/skeleton**; mentions Michelangelo briefly; missing 12 of 13 strengthening keywords |
| 50 | Uber Phone Screen Prep | Partial | Pointer | Same surface as id=3 (KNN, bias-variance, metrics, CV, regularization, decision trees) | Skeleton+bullets | Effectively a duplicate / parallel of id=3 |
| 81 | Uber LC 题库索引视图 (Index View) | None | None | 47 LeetCode problems indexed by pattern | Pointer-only | LC index map |

**Cross-cut observation**: Out of 11 Uber docs, only **id=34** has any from-scratch ML algorithm code (KNN). Linear/Logistic Regression / K-Means / Geometric Median have **zero implementation depth** anywhere in the DB — only checklist mentions in id=37. Search/recommendation system design appears in id=33 but as **generic e-commerce ranking framing (Ranking-as-Allocation)**, NOT Uber-Eats-specific with the full Staff Golden retrieval+ranking+rerank stack.

---

## 2. NEW — items needing fresh Staff-level seeding

| # | Topic | Source citation | Target charter | Proposed depth tier | Target task |
|---|-------|-----------------|----------------|---------------------|-------------|
| N1 | **Geometric median (L2 distance sum minimization)** + scaling follow-up | source TXT lines 2–3; cross-ref existing problem id=262 | ML Coding | Staff Golden Answer (mean ≠ argmin Σ‖x-pᵢ‖, Weiszfeld iteration, gradient/Newton, scaling: BFGS / coordinate descent / approximate via geomedian-of-means / random projection) | T-P0-629 |
| N2 | **K-Means from scratch (numpy)** | source TXT line 6 | ML Coding | Staff Golden Answer (init: k-means++, Lloyd's algo, vectorized assignment, convergence check, edge cases: empty cluster, ties; complexity; mini-batch variant; relation to GMM/EM) | T-P0-629 |
| N3 | **Linear Regression from scratch** (must run) | source TXT line 8 | ML Coding | Staff Golden Answer (closed-form normal eqn, GD/SGD, ridge regularization, train/test split, MSE eval, must execute end-to-end) | T-P0-629 |
| N4 | **Logistic Regression from scratch** (must run) | source TXT line 8 | ML Coding | Staff Golden Answer (sigmoid, cross-entropy loss derivation, GD/SGD, L2 reg, decision boundary, ROC/AUC eval, multi-class softmax extension, must execute end-to-end) | T-P0-629 |
| N5 | **Uber Eats restaurant recommendation system** | source TXT lines 14–451 (full Staff-level answer in source TXT) | ML SD | Staff Golden Answer (verbatim quote with light editing; covers stages 0–6: framing, scale estimate, hi-level arch, deep dive on multi-channel retrieval / H3 / two-tower / MMoE / training-serving skew / freshness + dead-click; closing senior add-ons: position bias, online vs batch, off-policy eval, cluster A/B) | T-P0-630 |
| N6 | **Budget-constrained promo recommendation system (uplift × constrained optimization)** | source TXT lines 453–973 (full Staff-level answer in source TXT) | ML SD | Staff Golden Answer (verbatim quote with light editing; covers TL;DR, problem framing + incrementality trap, clarifying questions, uplift modeling meta-learners (S/T/X/DR/Causal Forest), ILP + Lagrangian decomp, LP relaxation vs Lagrangian vs greedy, online allocation + PID pacing, contextual bandit, OPE (IPS/DR/Switch/SNIPS), long-running holdout + switchback) | T-P0-630 |
| N7 | **Multi-treatment uplift modeling intuition card** (auxiliary) | derived from source TXT §5.3 | ML Coding (depth-2) | Skeleton+bullets (when to use S vs T vs X-learner, multi-T encoding tradeoff, calibration via isotonic) | T-P1-635 |
| N8 | **Lagrangian relaxation pseudocode card** (auxiliary) | source TXT §6.2 (the 14-line Python snippet) | ML Coding (depth-2) | Skeleton+bullets (binary search on λ, decoupled per-user argmax, complexity O(NK) per iter, why scales to N=10M) | T-P1-635 |

**NEW count = 8** (≥ 4 required → smoke pass).

---

## 3. EXISTING-NEEDS-STRENGTHENING — id=33 + id=37 search/rec gaps

These rows are gaps between source TXT's "5 大薄弱处补强" table (source lines 405–412) + Stage-3/4/5 deep dive content vs current id=33 (Design & Architecture) and id=37 (VO 完整准备指南) coverage. Each row = one delta to land via T-P1-631.

| # | Strengthening item | Current coverage | Gap | Target doc | Target task |
|---|---|---|---|---|---|
| S1 | **Training-serving skew** as a system-design concern (feature snapshot at serving + feature store + monitoring three-layer defense) | id=33: NOT mentioned. id=37: NOT mentioned. | Add a new sub-section under id=33 §5 "Uber System Design Patterns" (or §4 trade-off framework) covering the 3-layer defense; add bullet to id=37 Round 3 checklist | id=33 (primary) + id=37 (link) | T-P1-631 |
| S2 | **Online robustness: timeout + fallback + missing-pattern training + popularity tier** | id=33: implied in §4 trade-off but no explicit pattern. id=37: NOT mentioned. | Add explicit "Graceful Degradation" pattern card to id=33 §5; add bullet to id=37 | id=33 + id=37 | T-P1-631 |
| S3 | **Model + Policy two-layer defense** (model learns continuous signals, policy backstops extreme outliers) | id=33: NOT mentioned as named pattern. id=37: NOT mentioned. | Add as a meta-design heuristic under id=33 §4 trade-off framework | id=33 | T-P1-631 |
| S4 | **Two-tower model** (user/item dual-encoder, in-batch sampled softmax, ANN serving) | id=33: NOT mentioned (id=33 covers MoE for ranking, but two-tower retrieval is a different beast). id=37: NOT mentioned. | Add to id=33 §5 retrieval/candidate-gen subsection | id=33 + id=37 | T-P1-631 |
| S5 | **MMoE (Multi-gate Mixture-of-Experts) for multi-task ranking** | id=33: covers MoE generically in Ranking-as-Allocation showcase but NOT MMoE multi-task formulation. id=37: NOT mentioned. | Distinguish MoE (single objective, expert routing) vs MMoE (multi-task, per-task gate) in id=33 §2 | id=33 | T-P1-631 |
| S6 | **Feature snapshot at serving time** | id=33: NOT mentioned. id=37: NOT mentioned. | Make this the first-class anti-skew technique under S1's 3-layer defense | id=33 | T-P1-631 (folded into S1) |
| S7 | **Michelangelo / Feature Store as single source of truth** | id=33: referenced once in §5 patterns. id=37: brief mention in Round 2 ML Coding checklist. | Expand id=33 §5 to dedicate a card to Michelangelo Palette + offline/online feature transformation parity | id=33 | T-P1-631 |
| S8 | **Position bias mitigation** in main ranking (not just LLM eval) | id=33: covered ONLY in LLM evaluation pipeline (§3) for pairwise judge order bias. id=37: NOT mentioned. | Generalize: add to id=33 §5 ranking patterns — "position-as-feature-during-train, set-to-zero-at-serve" + IPS weighting | id=33 | T-P1-631 |
| S9 | **Off-policy evaluation depth (IPS / DR / Switch / SNIPS)** | id=33: §2 mentions "IPS 加权" briefly. id=37: NOT mentioned. | Expand id=33 §2 to enumerate full OPE toolkit + when to choose which estimator + DR's robustness property | id=33 | T-P1-631 |
| S10 | **Cluster-randomized A/B / switchback** for marketplace interference | id=33: NOT mentioned. id=37: NOT mentioned. | Add as a card under id=33 §5 Uber-specific patterns (rationale: driver-supply spillover) | id=33 | T-P1-631 |
| S11 | **Dead-click hard filter (availability-aware candidate gen)** | id=33: NOT mentioned. id=37: NOT mentioned. | Add explicit "is open / accepting orders" hard-filter pattern at candidate-gen stage | id=33 | T-P1-631 |
| S12 | **Logging pipeline as first-class component (read:write ≈ 1:30)** | id=33: NOT mentioned. id=37: NOT mentioned. | Note that ML feed systems are write-heavy and logging is core, not nice-to-have; refer to S6 feature snapshot | id=33 | T-P1-631 |
| S13 | **Three-layer time scale framing (offline batch / near-line streaming / online ms)** | id=33: NOT mentioned. id=37: NOT mentioned. | Add as the canonical structuring frame for ML SD answers — distinguishes Uber from Netflix/Amazon (near-line is mandatory due to second-scale ETA changes) | id=33 | T-P1-631 |

**NEEDS-STRENGTHENING count = 13** (≥ 5 required → smoke pass).

---

## 4. OUT-OF-SCOPE — explicitly excluded

| # | Item | Reason out-of-scope |
|---|------|---------------------|
| O1 | id=30 Uber BPS LeetCode Solutions Guide — pure CS algorithm patterns | Round 1 algo charter, not ML Coding (Round 2) or ML SD (Round 3) |
| O2 | id=31 Uber BPS Custom Problem Solutions — prefix sum, OOD patterns | Round 1 algo charter |
| O3 | id=32 Uber BPS Pattern Cheat Sheet by Algorithm — 16 generic patterns | Round 1 algo charter |
| O4 | id=35 Uber BPS Timed Mock Interview Sets — tree/DP/graph timed sets | Round 1 algo charter |
| O5 | id=81 Uber LC 题库索引视图 (Index View) — LC problem index | Round 1 algo charter (legacy index, deprecating per T-P2-633) |
| O6 | id=36 Uber HR Call Prep Notes — recruiter-call talking points | Round 4 behavioral / HR pre-screen, not ML Coding/SD |
| O7 | id=37 Round 4 Behavioral section (Trust & Collaboration / Diverse Perspectives / Conviction) | Round 4 charter |
| O8 | id=3 + id=50 — phone-screen ML basics (KNN/bias-variance one-liner depth) | Phone-screen prep, not VO ML Coding (depth too shallow + already done) |
| O9 | `_Archived_和HR的准备文件.docx` in staging dir | Archived HR prep, explicitly archived by user |
| O10 | Source TXT §6 "你的 5 大薄弱处补强" table (lines 405–412) | Personal advice meta-card, folds into §5 strengthening rows above (S1–S13) — not a standalone seedable doc section |

**OUT-OF-SCOPE count = 10** (≥ 3 required → smoke pass).

---

## 5. 13-Keyword Gap Matrix

Per AC: explicitly enumerate each strengthening keyword as covered-OR-gap with specific doc-id citation.

| # | Keyword | id=33 (Design & Arch) | id=37 (VO 指南) | Net status |
|---|---------|----------------------|-----------------|------------|
| 1  | training-serving skew | **Gap** (not mentioned) | **Gap** (not mentioned) | **GAP — strengthen via S1/S6** |
| 2  | online robustness (timeout/fallback) | **Gap** (implied in §4 only) | **Gap** | **GAP — strengthen via S2** |
| 3  | Model+Policy two-layer | **Gap** | **Gap** | **GAP — strengthen via S3** |
| 4  | position bias | **Partial** (LLM eval §3 only — pairwise judge order bias; NOT main ranking) | **Gap** | **GAP — strengthen via S8** (extend to main ranking context) |
| 5  | off-policy eval (IPS / DR) | **Partial** (§2 brief "IPS 加权" mention; no DR/Switch/SNIPS depth) | **Gap** | **GAP — strengthen via S9** (full OPE toolkit) |
| 6  | cluster A/B / switchback | **Gap** | **Gap** | **GAP — strengthen via S10** |
| 7  | MMoE (multi-task) | **Partial** (MoE generic in §2, NOT MMoE multi-task) | **Gap** | **GAP — strengthen via S5** |
| 8  | two-tower (retrieval) | **Gap** | **Gap** | **GAP — strengthen via S4** |
| 9  | H3 (Uber hexagonal geo-index) | **Covered** (id=33 §5.1 Driver Maps card) | **Gap** | **PARTIAL — link from id=37 to id=33** |
| 10 | feature snapshot at serving | **Gap** | **Gap** | **GAP — strengthen via S6** (folded into S1) |
| 11 | Michelangelo / feature store | **Partial** (referenced in §5 patterns, no dedicated card) | **Partial** (one-line in Round 2 checklist) | **GAP — strengthen via S7** (dedicated card) |
| 12 | graceful degradation | **Gap** | **Gap** | **GAP — strengthen via S2** |
| 13 | dead-click hard filter (availability) | **Gap** | **Gap** | **GAP — strengthen via S11** |

**Tally**: 1 covered, 4 partial, 8 outright gap. → 12 of 13 keywords need strengthening work in T-P1-631.

---

## 6. Source TXT topic mapping

Per AC: all 4 ML coding + 2 ML SD items from source TXT mapped to NEW or COVERED-DUPLICATE.

| Source TXT location | Item | Charter | Mapping |
|---|------|---------|---------|
| Lines 2–3 | Geometric median + scaling follow-up | ML Coding | **NEW (N1)** — only adjacent surface is problem id=262, no Staff Golden Answer in any company_document |
| Line 6 | Implement K-Means (numpy allowed) | ML Coding | **NEW (N2)** — id=37 lists topic in checklist only; no implementation anywhere |
| Line 8 | Linear Regression from scratch (must run) | ML Coding | **NEW (N3)** — id=37 lists topic in checklist only; no implementation anywhere |
| Line 8 | Logistic Regression from scratch (must run) | ML Coding | **NEW (N4)** — id=37 lists topic in checklist only; no implementation anywhere |
| Lines 14–451 | Uber Eats restaurant recommendation Golden Answer (Stages 0–6) | ML SD | **NEW (N5)** — id=33 has generic Ranking-as-Allocation showcase (NOT Uber-Eats-specific); no dedicated Uber Eats SD answer in any doc |
| Lines 453–973 | Budget-constrained promo Golden Answer (uplift × Lagrangian) | ML SD | **NEW (N6)** — no uplift/Lagrangian/budget-allocation content anywhere in the 11 Uber docs |

**No COVERED-DUPLICATE rows** — all 6 source-TXT items are net-new content.

---

## 7. Counts smoke check

| Section | Required | Actual | Status |
|---------|----------|--------|--------|
| NEW | ≥ 4 | 8 | PASS |
| EXISTING-NEEDS-STRENGTHENING | ≥ 5 | 13 | PASS |
| OUT-OF-SCOPE | ≥ 3 | 10 | PASS |
| All 11 DB docs scanned | 11 | 11 | PASS |
| All 4 ML Coding + 2 ML SD source items mapped | 6 | 6 | PASS |
| 13 keywords explicitly enumerated | 13 | 13 | PASS |
| Each NEW row has target task tag | 8/8 | 8/8 (T-P0-629 ×4, T-P0-630 ×2, T-P1-635 ×2) | PASS |

---

## Appendix A — Raw doc dumps used for this audit

All 11 docs were exported to `logs/uber_doc_dumps/` (one `.md` per id) at audit time. Re-run via:

```bash
python -c "import sqlite3, os; os.makedirs('logs/uber_doc_dumps', exist_ok=True); conn=sqlite3.connect('data/mle_prep.db'); c=conn.cursor(); ids=[3,30,31,32,33,34,35,36,37,50,81]; [open(f'logs/uber_doc_dumps/id{i}.md','w',encoding='utf-8').write(c.execute('SELECT content FROM company_documents WHERE id=?',(i,)).fetchone()[0]) for i in ids]"
```

## Appendix B — Downstream task pipeline

```
T-P0-628 (this audit) ──┬─→ T-P0-629  Seed Uber ML Coding Golden Answer 集合 (uses NEW N1-N4)
                        ├─→ T-P0-630  Seed Uber ML SD Golden Answers     (uses NEW N5-N6)
                        ├─→ T-P1-631  Strengthen id=33 + id=37            (uses S1-S13 + 13-keyword matrix)
                        └─→ T-P1-635  Seed audit-discovered companions    (uses NEW N7-N8)
                                          │
                                          ▼
                                     T-P0-632  Patch id=37 Round 3+4 with anchor links
                                          │
                                          ▼
                                     T-P2-633  Deprecation banner on id=81
                                          │
                                          ▼
                                     T-P0-634  Manual smoke + verification
```
