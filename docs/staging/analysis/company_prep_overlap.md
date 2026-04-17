# Company Prep Overlap Audit — LinkedIn / Uber / Adobe

- **Task**: T-P0-184 (audit only; no code changes here)
- **Generated**: 2026-04-13
- **Scope**: 4 LinkedIn content notes (~148 KB), 5 Uber BPS docs (~195 KB), 13 Adobe seed scripts
- **Downstream work**: T-P1-185 executes the chosen consolidation plan; raw originals must be copied to `archive/legacy_company_docs/YYYY-MM-DD/` before any edit there.

---

## 1. File inventory

### LinkedIn (`MLInterviewPrep/data/linkedin_*_notes_content.md`)
| File | Size | Primary sections |
|---|---|---|
| `linkedin_bq_ps_notes_content.md` | 21 KB | BQ-1…BQ-9 (L11–222); PS-1 home-page traffic decline (L228); PS-2 feed A/B test (L275); interview technique (L347) |
| `linkedin_ml_coding_notes_content.md` | 42 KB | ANN (L1), Logistic Regression (L81), Gradient Descent variants (L142), Overfitting / L1 vs L2 (L193), Decision Tree (L263), Random Forest vs Boosting (L313), MLE + EM (L368), K-means impl (L431), Sparse matmul (L606), Stratified sampling (L744), LRU Cache + threading (L847), Service-dependency DFS (L1002) |
| `linkedin_prob_notes_content.md` | 35 KB | Weighted prob sampling (L29), RV mean/var (L108), Simpson's paradox (L193), Queueing (L286), Distributions (L333), Class imbalance (L429), Large-dataset sampling (L484), Tree overfitting (L530), L1/L2 bias (L575), RF theory (L625), MLE / GMM (L689), Reservoir sampling (L817), Biased coin → uniform (L895), Linear ↔ logistic equivalence (L969) |
| `linkedin_sd_notes_content.md` | 49 KB | Typeahead (L26), Short-video reco (L96), Metrics monitoring (L180), Job scheduler (L278), Single-machine KV store (L367), InMail LLM personalization (L462), Top-K search words (L565), Ranking system (L639), isMalicious API (L699), LinkedIn Skills mining (L775), Inverted-doc search (L853), SD interview strategy (L956) |

### Uber (`MLInterviewPrep/docs/uber_bps_*.md`)
| File | Size | Primary sections |
|---|---|---|
| `uber_bps_custom_solutions.md` | 78 KB | 25 custom coding problems (L41+): purchase opt, rider-connection union-find, elevator binary search, server throughput heap, cart pricing, circular-array jump, robot grid, monotonic-stack discount, parking-lot OOD, 2-D BFS grid, etc. |
| `uber_bps_design_architecture.md` | 31 KB | D&A format (L28); ranking-as-allocation project (L59); LLM-eval pipeline project (L166); STAR-T trade-off (L274); Uber patterns — driver maps / cart / driver queue / ETA / food ordering (L299); follow-ups (L491) |
| `uber_bps_knn_ml_fundamentals.md` | 27 KB | KNN core (L30), distance metrics + feature scaling (L158), k selection (L186), weighted KNN (L219), KNN optimization KD-tree / Ball-tree / LSH (L265), interview Q&A (L329), bias-variance (L405), overfitting / regularization (L449), cross-validation (L475), eval metrics (L499), feature eng (L539), quick-fire Q&A (L568), Uber-specific ML — ranking / CTR (L614) |
| `uber_bps_lc_solutions.md` | 33 KB | 19 LeetCode solutions (BST Kth smallest, provinces/union-find, house robber III, rotting oranges, merge K lists, bus routes, phone combos, word search, squares sorted array, vertical order, knight moves, edge-length-limited paths, longest consec, min edge reversals, palindrome paths, jump game VI) |
| `uber_bps_pattern_cheatsheet.md` | 27 KB | BFS (L34), DFS/backtracking (L87), tree DP (L127), union-find (L180), binary search (L234), DP re-rooting (L277), greedy (L332), heap (L356), sliding window (L396), monotonic stack (L441), two pointers (L480), OOD (L502), grid (L536), bitmask (L560), complexity summary (L584) |

### Adobe (`MLInterviewPrep/scripts/seed_adobe_day{1..7}_*.py`)
| File | LOC | Primary sections (slug + section titles inside `sections=[...]`) |
|---|---|---|
| `seed_adobe_day1_diffusion.py` | 441 | Diffusion deep-dive (L85); DDPM forward (L134); reverse (L180); Latent/Stable Diffusion (L230); CFG (L268); noise schedules (L310); advanced (L362) |
| `seed_adobe_day1_chinese.py` | 415 | Chinese mirror of day1 diffusion (L23+) |
| `seed_adobe_day1_expansion_{a,b,c}.py` | 382/403/355 | Positional embeddings + KV-cache + RoPE variants; VAE/VQ-VAE, ControlNet vs T2I-Adapter; additional diffusion variants |
| `seed_adobe_day2_rlhf_dpo.py` | 549 | RLHF+DPO+distillation (L98); 3-step pipeline SFT/RM/PPO (L147); DPO (L240); DPO vs RLHF (L301); variants (L342); distillation (L371); 70B→7B (L433); misconceptions (L469) |
| `seed_adobe_day2_chinese.py` | 578 | Chinese mirror of day2 RLHF/DPO (L34+) |
| `seed_adobe_day3_distributed.py` | 597 | Distributed training DP/TP/PP/FSDP (L147); four-parallelism overview (L210); ZeRO stage 1/2/3 (L379/386/392); 13B-on-8×A100 selection (L430); 3-D parallelism (L477) |
| `seed_adobe_day3_chinese.py` | 514 | Chinese mirror of day3 distributed (L37+) |
| `seed_adobe_day4_rope_video.py` | 651 | Positional encoding (L272); RoPE (L291); complex-number impl (L336); comparison table (L362); long-context YaRN/ALiBi (L396); video gen components (L467); Sora/DiT (L512); Adobe Firefly context (L533) |
| `seed_adobe_day5_inference.py` | 665 | FlashAttention tiling (L322); quantization GPTQ/AWQ/SmoothQuant (L379); serving — PagedAttention, continuous batching, speculative decoding (L459); project narrative (L543) |
| `seed_adobe_day6_mock_interview.py` | 1228 | End-to-end mock interview script (cross-cuts all prior days) |
| `seed_adobe_day7_review.py` | 946 | Consolidation / flashcard review |

---

## 2. Topic overlap matrix

Rows = canonical topic. Cells give company file + anchor line. `—` means no coverage.

| # | Topic | LinkedIn | Uber | Adobe | Tier |
|---|---|---|---|---|---|
| 1 | Activation functions (ReLU/SiLU/SwiGLU) | ml_coding:30 | — | day5_inference:67 (context) | SHARED (LI canonical) |
| 2 | Loss functions (BCE/CE/MSE/BPR) | ml_coding:44 | — | day1_diffusion:136 (diffusion-only) | SHARED (LI canonical) |
| 3 | Optimizers (Adam/AdamW/SGD) | ml_coding:54 | — | — | COMPANY-SPECIFIC (LI) |
| 4 | Bias–variance tradeoff | — | knn_ml:405 | day3_distributed:255 (aside) | SHARED (Uber canonical) |
| 5 | Overfitting & L1/L2 regularization | ml_coding:193; prob:529, 575 | knn_ml:449 | day2_rlhf:420 | **SHARED — duplicate risk** |
| 6 | Cross-validation (k-fold / stratified) | — | knn_ml:475 | — | COMPANY-SPECIFIC (Uber) |
| 7 | Classification metrics (P/R/F1/AUC/ROC/PR) | prob:429 (class imbalance) | knn_ml:499 | day5_inference:407 (quant quality) | SHARED |
| 8 | Logistic regression derivation | ml_coding:79; prob:969 | knn_ml:354 (vs KNN) | — | SHARED (LI canonical) |
| 9 | KNN (distance, k, weighted, KD/Ball/LSH) | — | knn_ml:30–327 | — | COMPANY-SPECIFIC (Uber) |
| 10 | Decision trees / RF / boosting | ml_coding:263, 313; prob:530, 625 | knn_ml:604 (cheatsheet) | — | SHARED (LI canonical) |
| 11 | Gradient descent variants (BGD/SGD/mini) | ml_coding:142 | — | day1_diffusion:310 (noise-sched analogy) | COMPANY-SPECIFIC (LI); Adobe not a dup |
| 12 | K-means (impl + stopping) | ml_coding:431 | — | — | COMPANY-SPECIFIC (LI) |
| 13 | MLE / EM / GMM | ml_coding:368; prob:689 | — | day2_rlhf:240 (PPO analogy) | COMPANY-SPECIFIC (LI); Adobe not a dup |
| 14 | Feature engineering & scaling | — | knn_ml:158, 539 | day5_inference:67 (quant-sensitive) | SHARED (Uber canonical) |
| 15 | Sampling (weighted / reservoir / stratified) | ml_coding:744; prob:29, 484, 817, 895 | — | — | COMPANY-SPECIFIC (LI) |
| 16 | Simpson's paradox / A/B pitfalls | prob:193; bq_ps:275 | — | — | COMPANY-SPECIFIC (LI) |
| 17 | Queueing / distributions / class imbalance | prob:286, 333, 429 | — | — | COMPANY-SPECIFIC (LI) |
| 18 | LRU cache + threading | ml_coding:847 | cheatsheet:502 (OOD); custom:1473 (parking-lot OOD) | — | SHARED (LI canonical for LRU; Uber adds OOD parking variant) |
| 19 | Sparse matmul / inverted-index | ml_coding:606; sd:853 | — | — | COMPANY-SPECIFIC (LI) |
| 20 | Service-dep graph / DFS on DAG | ml_coding:1002 | cheatsheet:87; custom (various) | — | SHARED (cheatsheet is pattern level only) |
| 21 | Typeahead / autocomplete | sd:26 | — | — | COMPANY-SPECIFIC (LI) |
| 22 | Short-video / feed recommendation & ranking | sd:96, 639; bq_ps:275 | knn_ml:614; design:59 (ranking-as-allocation) | — | **SHARED — product-angle divergent** |
| 23 | Metrics / anomaly monitoring | sd:180 | — | — | COMPANY-SPECIFIC (LI) |
| 24 | Job scheduler / rate limiting | sd:278 | cheatsheet:332 (greedy); custom (throughput heap) | — | SHARED (pattern-vs-system) |
| 25 | KV store design | sd:367 | — | — | COMPANY-SPECIFIC (LI) |
| 26 | Top-K (stream / heap) | sd:565 | cheatsheet:356 (heap); custom (throughput) | — | SHARED (pattern-vs-system) |
| 27 | LLM personalization (InMail) | sd:462 | — | day2_rlhf:147; day5_inference:543 (serving) | **SHARED — different layers** |
| 28 | Classification (malicious / safety API) | sd:699 | — | — | COMPANY-SPECIFIC (LI) |
| 29 | Skills mining / entity resolution | sd:775 | — | — | COMPANY-SPECIFIC (LI) |
| 30 | Attention / Transformers (self-attn, MHA) | — | — | day4_rope_video:272; day5_inference:322 | COMPANY-SPECIFIC (Adobe) |
| 31 | Positional encoding (abs/rel/RoPE/ALiBi/YaRN) | — | — | day1_expansion_a; day4_rope_video:272–465 | COMPANY-SPECIFIC (Adobe) |
| 32 | KV cache, long context | — | — | day1_expansion_a; day4_rope_video:396 | COMPANY-SPECIFIC (Adobe) |
| 33 | RLHF + DPO alignment | — | — | day2_rlhf:147–342; day2_chinese:34 | COMPANY-SPECIFIC (Adobe); **day2_rlhf ↔ day2_chinese DUPLICATE (EN/中)** |
| 34 | LLM distillation (70B→7B) | — | — | day2_rlhf:371–460 | COMPANY-SPECIFIC (Adobe) |
| 35 | Distributed training (DP/TP/PP/FSDP/ZeRO) | — | — | day3_distributed:147–511; day3_chinese:37 | COMPANY-SPECIFIC (Adobe); **day3_distributed ↔ day3_chinese DUPLICATE (EN/中)** |
| 36 | Diffusion models (DDPM/LDM/CFG, VAE, ControlNet) | — | — | day1_diffusion; day1_chinese; day1_expansion_{a,b,c} | COMPANY-SPECIFIC (Adobe); **day1_diffusion ↔ day1_chinese DUPLICATE (EN/中)** |
| 37 | Inference opt (FlashAttn / quant / PagedAttn / spec-dec) | — | — | day5_inference:322–519 | COMPANY-SPECIFIC (Adobe) |
| 38 | Video generation (Sora / DiT / Firefly) | — | — | day4_rope_video:467–545 | COMPANY-SPECIFIC (Adobe) |
| 39 | Behavioral / Product-sense storytelling | bq_ps:11–345 | design:274 (STAR-T); hr_call (scope) | day6_mock_interview | COMPANY-SPECIFIC (format-divergent) |
| 40 | Algorithm pattern cheatsheets (BFS/DFS/UF/DP/heap/MS/2P/bitmask) | ml_coding:1002 (one DFS) | cheatsheet:34–584 | — | COMPANY-SPECIFIC (Uber canonical) |
| 41 | LeetCode individual solutions | — | lc_solutions (19); custom (25) | — | COMPANY-SPECIFIC (Uber) — overlaps with global LC table in DB |

### Three-tier classification summary

- **SHARED (canonical candidate — merge into cross-company store)**: topics 1, 2, 4, 5, 7, 8, 10, 14, 18, 22, 24, 26, 27, 20.  Total: 14.
- **COMPANY-SPECIFIC (product / interview-format angle — keep as overlay)**:
  - LinkedIn: 3, 11, 12, 13, 15, 16, 17, 19, 21, 23, 25, 28, 29 and all behavioral / product-sense (39).
  - Uber: 6, 9, 40, 41, plus product patterns embedded in `design_architecture.md` (Uber Eats cart, driver queue, ETA estimator).
  - Adobe: 30, 31, 32, 34, 37, 38, plus the Firefly / 70B-Adobe-context framing inside otherwise-generic topics (33, 35, 36).
- **DUPLICATE (near-identical prose, consolidation target)**:
  - **Within Adobe itself**: `day1_diffusion.py` ↔ `day1_chinese.py`; `day2_rlhf_dpo.py` ↔ `day2_chinese.py`; `day3_distributed.py` ↔ `day3_chinese.py`. These are bilingual mirrors of the same module — largest dedup win on the Adobe side (≈1.5 KLOC). Keep Chinese as source-of-truth per `feedback_lc_notes_chinese`; demote English variants to auto-generated glossary or drop entirely.
  - **Across companies**: Overfitting & L1/L2 (topic 5) appears four times (ml_coding:193, prob:529, prob:575, knn_ml:449) with ≥60% prose overlap — strongest cross-company dedup candidate.
  - **Partial prose overlap**: ranking/feed reco (22) and LLM personalization (27) differ in product framing but share formulas (DCG/NDCG, BPR, CTR calibration) — merge formulas, keep product framing as overlay.

---

## 3. Consolidation plan

Two options. **Recommendation: Option A (knowledge_cards table with company overlays)** — it inherits the existing DB-first architecture of this repo (framework_nodes, problems, company_documents) and the QuickIndex/Drawer UI already rendered from DB; a markdown-tree alternative would fight that grain.

### Option A — `knowledge_cards` table + company overlays (RECOMMENDED)

**Schema sketch** (final DDL designed in T-P1-185):
```sql
CREATE TABLE knowledge_cards (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,          -- e.g. "overfitting-l1-l2"
  title TEXT NOT NULL,                -- Chinese display title
  canonical_body TEXT NOT NULL,       -- shared prose (Chinese, English names/formulas intact)
  tags TEXT,                          -- JSON array: ["regularization","ml-theory"]
  source_company TEXT,                -- first-author company (for provenance only)
  source_file TEXT,
  source_line_start INTEGER,
  source_line_end INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE company_card_overlays (
  id INTEGER PRIMARY KEY,
  card_id INTEGER NOT NULL REFERENCES knowledge_cards(id),
  company_id INTEGER NOT NULL,        -- FK to existing companies table
  angle TEXT NOT NULL,                -- "product" | "interview-format" | "translation"
  overlay_body TEXT NOT NULL,         -- what to show stacked under canonical when viewing this company
  source_file TEXT,
  source_line_start INTEGER,
  source_line_end INTEGER,
  UNIQUE(card_id, company_id, angle)
);
```

**Migration approach** (to be executed in T-P1-185):
1. `archive/legacy_company_docs/2026-04-13/` snapshot of every file listed in §1 (`git ls-files` before/after to verify).
2. For each SHARED topic, author one `knowledge_cards` row in Chinese, citing provenance of the line range that contributed most content.
3. For each COMPANY-SPECIFIC variant of a SHARED topic, insert `company_card_overlays` row. True COMPANY-SPECIFIC topics (no shared kernel) stay in `company_documents` / `company_knowledge` as today.
4. The 3 Adobe EN/中 duplicates: keep Chinese seed as source-of-truth, delete English seed after user approval (flagged in the T-P1-185 PR description per AC (4)).
5. Render: `/companies/:id/prep` composes canonical card body + overlays tagged for that company (no duplication); QuickIndex knowledge tabs already hit framework_nodes/knowledge endpoints and can pick up `knowledge_cards` with a thin join.

**Pros**: Consistent with DB-first repo; UI already renders DB content via drawer; overlays keep company product framing; provenance preserved in source_* columns.

**Cons**: Schema churn (two new tables); requires small backend endpoint + drawer tweak; must decide canonical vs overlay split per topic (14 decisions).

### Option B — `shared/` markdown tree with transclusion

Create `docs/shared/<topic>.md` for each SHARED topic; company docs use `<!-- include: shared/overfitting-l1-l2.md -->` tokens expanded by a thin pre-render.

**Pros**: Pure markdown, diffable, no schema change.
**Cons**: Fights existing DB-first rendering; would re-introduce a second source-of-truth alongside `company_documents`; transclusion tooling does not exist and would need to be built; loses searchability via existing `/framework/tree` + `/framework/nodes/:id` endpoints.

### Decision gate

T-P1-185 should start with Option A unless the user overrides. Before any raw-file deletion, T-P1-185 MUST: (a) copy originals to `archive/legacy_company_docs/2026-04-13/`, (b) list deletion candidates in the PR description for explicit approval (AC (4) on T-P1-185).

---

## 4. Quantified dedup opportunity

| Bucket | Files | Est. chars | Notes |
|---|---|---|---|
| Adobe bilingual mirrors (day1/2/3 en ↔ 中) | 6 files | ~90 KB | Largest single win; drop English seeds after Chinese confirmed |
| Overfitting / L1-L2 (topic 5) | 4 locations | ~12 KB | Merge to one card; overlay adds mathematical derivation tone from LinkedIn |
| Classification metrics (topic 7) | 3 locations | ~6 KB | Canonical table; Adobe keeps quantization-quality overlay |
| Bias–variance (topic 4) | 2 locations | ~3 KB | Uber version is canonical; drop Adobe aside |
| Ranking / feed reco (topic 22) | 3 locations | ~10 KB | Canonical formulas; LI keeps InMail overlay, Uber keeps ranking-as-allocation overlay |
| **Estimated total dedup** | — | **~120 KB / ~34%** of 343 KB audited scope | — |

---

## 5. Next steps

1. **User review**: confirm Option A (recommended) or elect Option B.
2. On approval, execute **T-P1-185** which:
   - snapshots raw originals,
   - creates schema + seeds canonical cards in Chinese,
   - wires `/companies/:id/prep` to merged view,
   - lists deletion candidates (EN Adobe mirrors + any wholly-subsumed paragraphs) for explicit approval in PR description.
3. Out-of-scope for this audit: implementation, deletions, schema migration — all tracked under T-P1-185.
