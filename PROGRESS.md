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
> 41 session entries archived as of 2026-03-31.

## 2026-03-26 -- [T-P1-200] Add Adobe phone screen event to interview timeline
- **What I did**: Added Adobe phone screen event to the interview timeline. Created Adobe company entry (id=23, status=phone_screen) and interview event (id=6, event_type=phone_screen, scheduled_at=2026-03-30T09:00:00, status=upcoming). Description notes exact time TBD. Also updated seed_interview_events.py with the Adobe event for idempotent re-seeding.
- **Deliverables**: `data/mle_prep.db` updated (new company + event), `scripts/seed_interview_events.py` modified
- **Sanity check result**: Verified via SQL: Adobe phone screen appears in timeline sorted by date, Adobe company exists with status=phone_screen. All 6 events display correctly.
- **Status**: [DONE]
## 2026-03-26 -- [T-P1-201] Parse staging LC file: extract problems for LinkedIn/Uber/Adobe
- **What I did**: Wrote parser script (scripts/parse_staging_lc.py) to extract all LeetCode problems from staging file 'LC to be added'. Handles two format zones: Zone1 (lines 1-334, 208 problems, no difficulty) and Zone2 (lines 337-3561, 806 problems, with pct+difficulty). All tagged with LinkedIn+Uber+Adobe company tags.
- **Deliverables**: `scripts/parse_staging_lc.py` (parser), `data/staging_lc_parsed.json` (1014 problems)
- **Sanity check result**: 1014 unique problems, no duplicates, 208+806=1014, all have company_tags, frequency_rank 1-1014 preserved
- **Status**: [DONE]
## 2026-03-26 -- [T-P1-202] Batch import parsed LC problems into DB with company tags
- **What I did**: Wrote import script (scripts/import_staging_lc.py) that reads staging_lc_parsed.json and imports into mle_prep.db. For 144 existing problems: merged LinkedIn/Uber/Adobe company_tags, filled missing difficulty. For 870 new problems: inserted with leetcode_id, title, URL (generated from title slug), difficulty, category=algorithm, company_tags. Supports --dry-run flag.
- **Deliverables**: `scripts/import_staging_lc.py` (import script)
- **Sanity check result**: 1029 total problems in DB (158 pre-existing + 870 new + 1 null-id). All 1014 parsed problems have LinkedIn+Uber+Adobe tags. 0 duplicate leetcode_ids. 86 problems with notes preserved, 88 completed problems preserved. 15 pre-existing problems not in parsed file correctly retained without new tags.
- **Status**: [DONE]
## 2026-03-26 -- [T-P1-203] Verify imported problems: counts, tags, frequency order
- **What I did**: Wrote verification script (scripts/verify_lc_import.py) with 5 checks: (1) company tag counts = 1014 each, (2) first/last 10 parsed problems match DB by leetcode_id and title, (3) data retention (86 notes, 88 completed, 15 untagged pre-existing), (4) no duplicate leetcode_ids (1028 distinct), (5) all 1028 URLs well-formed (1023 leetcode.com + 5 alternative sources).
- **Deliverables**: `scripts/verify_lc_import.py` (verification script)
- **Sanity check result**: All 5 checks pass. 1029 total problems, 1014 correctly tagged with LinkedIn+Uber+Adobe.
- **Status**: [DONE]
## 2026-03-26 -- [T-P1-204] Add real-time HH:MM:SS countdown to dashboard timeline events
- **What I did**: Replaced static countdown text (e.g. "in 3 days") with a live ticking HH:MM:SS countdown in InterviewTimeline.tsx. Created useCountdown hook using useState+useEffect+setInterval(1000ms). Removed old countdown() function. Added font-mono class for consistent digit width.
- **Deliverables**: `src/frontend/src/components/timeline/InterviewTimeline.tsx` (useCountdown hook + EventCard integration)
- **Sanity check result**: TypeScript compiles cleanly (tsc --noEmit passes). Hook only runs for upcoming events (isPast=false guard preserved). Past events show no countdown. Format strictly HH:MM:SS with zero-padding.
- **Status**: [DONE]
## 2026-03-26 -- [T-P1-205] Add Company Frequency tab to Problems page
- **What I did**: Added "Company Freq" tab to Problems page showing 1014 LinkedIn/Uber/Adobe frequency-sorted problems. Backend: added `frequency_rank` column to Problem model, added it to sort_by options and API response, increased limit to 1200. Created migration script to populate frequency_rank from parsed JSON. Frontend: new tab with purple-themed progress bar, company filter buttons (LinkedIn/Uber/Adobe), flat table sorted by frequency rank with Rank column. Hid sidebar source/company filters when on this tab.
- **Deliverables**: `src/backend/models/problem.py` (frequency_rank column), `src/backend/routers/problems.py` (sort + response), `src/backend/schemas/problem.py` (response field), `src/frontend/src/types/problem.ts` (type updates), `src/frontend/src/pages/Problems.tsx` (tab + render), `scripts/add_frequency_rank.py` (migration)
- **Sanity check result**: TypeScript compiles cleanly. All 1006 tests pass. 1014 rows updated with frequency_rank (1-1014). Python ruff clean. Backend imports verified.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-210] Adobe Prep Day1: Diffusion Models deep-dive note
- **What I did**: Created comprehensive Diffusion Models study note as CompanyDocument under Adobe (id=23). Content covers: (1) DDPM forward process with full math (reparameterization trick, alpha-bar closed form), (2) Reverse process (denoising network, MSE loss, sampling algorithm), (3) Latent Diffusion / Stable Diffusion pipeline with HTML concept diagram (Text->CLIP->Cross-Attention->UNet->VAE->Image), (4) CFG formula with guidance scale explanation, (5) Noise schedules (linear vs cosine comparison), (6) Advanced topics (DDIM, Score-based SDE). Includes 4 self-check questions and quick reference card.
- **Deliverables**: `scripts/seed_adobe_day1_diffusion.py` (seed script, idempotent)
- **Sanity check result**: Document inserted (id=5, 8676 chars). All 6 required sections present. HTML diagram renders. 4 checkbox self-check questions. Ruff clean. Idempotent re-run skips correctly.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-211] Adobe Prep Day2: RLHF/DPO alignment + LLM distillation note
- **What I did**: Created comprehensive RLHF/DPO + LLM Distillation study note as CompanyDocument under Adobe (id=23). Content covers: (1) RLHF 3-step pipeline (SFT -> Reward Model -> PPO) with HTML flow diagram, (2) Bradley-Terry preference model and RM loss, (3) PPO objective with KL penalty explanation, (4) DPO loss with full derivation intuition (closed-form optimal policy -> BT substitution -> Z(x) cancellation), (5) DPO vs RLHF comparison table (11 dimensions), (6) RLHF/DPO variants (RLAIF, GRPO, IPO, KTO, SimPO, ORPO), (7) LLM Distillation: KL divergence loss, temperature scaling, dark knowledge, 70B->7B design with memory estimation, (8) 5 common misunderstandings with corrections. Includes 4 self-check questions and quick reference card.
- **Deliverables**: `scripts/seed_adobe_day2_rlhf_dpo.py` (seed script, idempotent)
- **Sanity check result**: Document inserted (id=6, 13286 chars). All 6 required sections present. HTML diagram renders. 4 checkbox self-check questions. Ruff clean. Idempotent re-run skips correctly.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-212] Adobe Prep Day3: Distributed training (DP/TP/PP/FSDP) note
- **What I did**: Created comprehensive Distributed Training study note as CompanyDocument under Adobe (id=23). Content covers: (1) Overview diagram with 4 parallelism strategies comparison table, (2) Data Parallelism: AllReduce, gradient bucketing, memory formula (16P per GPU), PyTorch DDP, (3) Tensor Parallelism: MLP column-row split, attention head split, communication pattern, intra-node only, (4) Pipeline Parallelism: naive bubble, micro-batch pipelining, bubble fraction formula, GPipe/1F1B variants, (5) FSDP/ZeRO Stages 1/2/3 with memory table and communication analysis, (6) Selection guide: 13B on 8xA100 worked example with memory estimation formula, (7) 3D parallelism: layout diagram, real-world examples (GPT-3, PaLM, Llama), (8) 5 common misunderstandings. Includes 4 self-check questions and quick reference card.
- **Deliverables**: `scripts/seed_adobe_day3_distributed.py` (seed script, idempotent)
- **Sanity check result**: Document inserted (id=7, 17374 chars). All 8 required sections present. 12 HTML diagram blocks. 4 checkbox self-check questions. Ruff clean. Idempotent re-run skips correctly.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-213] Adobe Prep Day4: RoPE + long context + video generation note
- **What I did**: Created comprehensive RoPE + Long Context + Video Generation study note as CompanyDocument under Adobe (id=23). Content covers: (1) Why PE matters (4 requirements), (2) RoPE: rotation matrix formulation, theta_i formula, proof that q_m*k_n depends only on m-n, efficient complex-number implementation, (3) PE comparison table (Sinusoidal vs Learned vs ALiBi vs RoPE), (4) Long context methods: Position Interpolation (linear scaling), NTK-aware scaling (base freq adjustment), YaRN (per-dimension PI/NTK + attention temp), summary table, (5) Video generation: 3D VAE (temporal+spatial compression), temporal attention, motion modules, Sora/DiT architecture with spacetime patches, challenges table (5 challenges), Adobe Firefly context, (6) 5 common misunderstandings with corrections. Includes 4 self-check questions and quick reference card.
- **Deliverables**: `scripts/seed_adobe_day4_rope_video.py` (seed script, idempotent)
- **Sanity check result**: Document inserted (id=8, 22549 chars). All 6 main sections present. 23 HTML div blocks. 4 checkbox self-check questions. All 10 required topics present (RoPE, theta_i, PI, NTK, YaRN, Video, DiT, temporal attention, 3D VAE, Firefly). Ruff clean. Idempotent re-run skips correctly.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-214] Adobe Prep Day5: Inference optimization + project narrative note
- **What I did**: Created comprehensive Inference Optimization + Project Narrative study note as CompanyDocument under Adobe (id=23). Content covers: (1) FlashAttention: SRAM vs HBM memory hierarchy, tiled computation algorithm, online softmax trick, IO complexity O(N^2 d^2/M), FA2/FA3 improvements, (2) Quantization comparison: GPTQ (OBS-based, Hessian compensation), AWQ (salient channel scaling), Weight-only INT4 (RTN), W8A8 (SmoothQuant), (3) Serving: KV-cache memory analysis, KV-cache quantization, PagedAttention (virtual memory with block tables, CoW), Continuous Batching (iteration-level scheduling), Speculative Decoding (draft-verify, provably lossless), serving framework comparison table, (4) Project narrative mapping table: 6 experience->Adobe framing pairs (operator fusion->FlashAttention, compression->GPTQ/AWQ, HW profiling->KV-cache, batch pipeline->continuous batching, cascade inference->speculative decoding, mixed precision->FP8), (5) 5 common misunderstandings with corrections. Includes 5 self-check questions and quick reference card.
- **Deliverables**: `scripts/seed_adobe_day5_inference.py` (seed script, idempotent)
- **Sanity check result**: Document inserted (id=9, 25315 chars). All 5 main sections present. 33 HTML div blocks. 5 self-check questions. All 10 required topics present (FlashAttention, SRAM, HBM, GPTQ, AWQ, SmoothQuant, PagedAttention, Continuous Batching, Speculative Decoding, KV-Cache). Ruff clean. Idempotent re-run skips correctly.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-215] Adobe Prep Day6: Mock interview questions + STAR-T project stories
- **What I did**: Created comprehensive Mock Interview Questions + STAR-T Project Stories study note as CompanyDocument under Adobe (id=23). Content covers: (1) STAR-T framework (Situation/Task/Approach/Result/Transfer) with timing guide and fill-in template, delivery tips, (2) 3 project story outlines mapped to Adobe JD: inference pipeline optimization (quantization + continuous batching -> 63% P99 reduction), distributed training (FSDP + mixed precision -> 6.7x speedup), data quality + alignment (DPO -> +18% user satisfaction), each with drill-down questions, (3) 13 high-frequency interview questions with structured answer outlines: Diffusion (Q1-4: DDPM, CFG, Latent Diffusion, DDPM vs DDIM), Inference (Q5-7: FlashAttention, Speculative Decoding, GPTQ vs AWQ), Distributed (Q8-10: DP/TP/PP comparison, FSDP, debug slow training), Alignment (Q11-12: RLHF vs DPO, reward hacking), System Design (Q13: text-to-image at Adobe scale), (4) Interview speech templates: opening (30s), handling unknowns (3 options), steering to strengths (bridge technique), asking good questions (5 prepared Adobe questions), (5) 10-item error correction quick-reference table covering all 6 domains. Includes 5 self-check questions and quick reference card.
- **Deliverables**: `scripts/seed_adobe_day6_mock_interview.py` (seed script, idempotent)
- **Sanity check result**: Document inserted (id=10, 41619 chars). All 5 main sections present. 76 HTML div blocks. 5 self-check questions. All 13 required topics present (STAR-T, DDPM, CFG, Latent Diffusion, FlashAttention, Speculative Decoding, GPTQ, AWQ, FSDP, DPO, RLHF, PagedAttention, RoPE). Ruff clean. Idempotent re-run skips correctly.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-216] Adobe Prep Day7: Review checklist + concept map + error cards
- **What I did**: Created final review note as CompanyDocument under Adobe (id=23). Content covers: (1) Master review checklist with checkbox items across all 6 domains (Diffusion, Alignment/DPO, Distributed, RoPE/Video, Inference, Interview Skills) -- 48 total items with key verification points, (2) HTML concept map showing cross-topic connections (Diffusion->Video, Inference<->Distributed, RoPE->LongContext->FlashAttention, etc.) with 8 connection explanations, (3) 7 error correction cards for common misunderstandings (iterative denoising, DPO needs ref model, TP!=DP, RoPE is fixed, spec decode is lossless, FSDP!=PP, FlashAttention is IO not compute optimization), (4) Daily time allocation table: 290 study + 150 practice = 440 total minutes across 7 days, (5) Formula cheat sheet consolidating all key equations from 6 domains, (6) 5 cross-domain self-check questions, (7) Quick reference card.
- **Deliverables**: `scripts/seed_adobe_day7_review.py` (seed script, idempotent)
- **Sanity check result**: Document inserted (id=11, 35457 chars). All 7 sections present. 69 HTML div blocks. 6 domain checklists present. 7 error cards. All 13 key topics present (DDPM, CFG, DPO, RLHF, FSDP, RoPE, FlashAttention, PagedAttention, GPTQ, AWQ, STAR-T, Speculative, 440). 5 self-check questions. Ruff clean. Idempotent re-run skips correctly.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-227] Minimal StudyNoteBuilder + FormulaBlock typed constraint
- **What I did**: Created `scripts/study_note_builder.py` with FormulaBlock dataclass (auto-wraps latex in $$) and StudyNoteBuilder class. Builder methods: set_title, add_prerequisites, add_term (glossary + auto-bold first occurrence), add_section (str | FormulaBlock blocks), add_diagram_html, add_comparison_table, add_interview_qa, add_checklist. build() pipeline: HTML comment header, Prerequisites, Key Terms glossary, sections, auto-bold terms in prose, fail-fast orphan single-dollar detection. validate() classmethod for scanning existing docs. save_to_db() with idempotent insert.
- **Deliverables**: `scripts/study_note_builder.py` (builder module), `tests/test_study_note_builder.py` (25 tests)
- **Sanity check result**: 25/25 tests pass. Ruff clean. FormulaBlock guarantees $$. Single-dollar in prose raises ValueError. Auto-bold works on first occurrence only. save_to_db idempotent. validate() detects single-dollar and missing header.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-228] Enable rehype-raw in MarkdownPreview
- **What I did**: Installed rehype-raw package and added it to MarkdownPreview.tsx rehypePlugins array (before rehypeKatex). This enables raw HTML in markdown content to render as actual DOM elements instead of being stripped.
- **Deliverables**: `src/frontend/src/components/ui/MarkdownPreview.tsx` (added rehype-raw import + plugin), `src/frontend/package.json` + `package-lock.json` (rehype-raw dependency)
- **Sanity check result**: TypeScript compiles cleanly (tsc --noEmit). Vite production build succeeds. rehype-raw placed before rehypeKatex in plugin chain so HTML passes through before KaTeX processes math.
- **Status**: [DONE]
## 2026-03-27 -- [T-P0-229] Pilot: Rewrite Day 1 (Diffusion) end-to-end with Builder
- **What I did**: Rewrote seed_adobe_day1_diffusion.py to use StudyNoteBuilder API instead of raw strings. Fixed Builder gap: added paired inline math ($...$) support to _check_single_dollars and validate (only orphan/unpaired $ flagged now). Added noise schedule ASCII diagram. Enhanced content with: Prerequisites (4 items), Term Registry (9 terms: DDPM, VAE, UNet, CFG, CLIP, latent space, noise schedule, epsilon-prediction, cross-attention), FormulaBlock for all 9 display math formulas, intuitive explanations before each formula, 2 HTML diagrams (pipeline + noise schedule), comparison tables, self-check checklist. Updated DB document id=5 (8676 -> 12183 chars). Added 3 new tests for inline math support.
- **Deliverables**: `scripts/study_note_builder.py` (inline math support in _check_single_dollars + validate), `scripts/seed_adobe_day1_diffusion.py` (full Builder rewrite), `tests/test_study_note_builder.py` (3 new/updated tests: orphan dollar, paired inline math, validate paired math)
- **Sanity check result**: 27/27 tests pass. 0 validation warnings. 17/17 content checks pass (header, title, prerequisites, 5 terms registered, FormulaBlock $$, HTML diagrams, checklist, quick reference, no orphan $, auto-bold, intuitions, inline math). TypeScript clean. Builder API validated -- works for full document generation.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-229 --status completed`
## 2026-03-27 -- [T-P0-232] Add Builder convention to CLAUDE.md + update memory
- **What I did**: Codified StudyNoteBuilder convention in CLAUDE.md: (1) Code Style section: added "Study Note Generation" rule requiring StudyNoteBuilder + FormulaBlock for all study notes, (2) Prohibited Actions section: added "Never write study note content as raw strings" with explanation of what validation raw strings bypass. Created memory file feedback_study_note_builder.md with Builder usage rules and reference to canonical example. Updated MEMORY.md index.
- **Deliverables**: `CLAUDE.md` (2 additions: Code Style + Prohibited Actions), `memory/feedback_study_note_builder.md` (new), `memory/MEMORY.md` (updated index)
- **Sanity check result**: Both CLAUDE.md sections read correctly. Memory file created with proper frontmatter.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-232 --status completed`
## 2026-03-27 -- [T-P0-230] Scale: Rewrite Day 2 RLHF/DPO with validated Builder (1/6)
- **What I did**: Rewrote seed_adobe_day2_rlhf_dpo.py from raw string format to StudyNoteBuilder API. Added: Prerequisites (4 items incl. Day 1 cross-reference), Term Registry (9 terms: RLHF, DPO, SFT, PPO, Bradley-Terry, KL divergence, reward hacking, knowledge distillation, dark knowledge), FormulaBlock for all 9 display math formulas (SFT loss, BT model, RM loss, RLHF objective, PPO clip, reward-policy relation, DPO BT substitution, DPO loss, KD loss), 3 HTML diagrams (RLHF pipeline, DPO vs RLHF, distillation flow), comparison tables (11-dimension RLHF vs DPO, RLHF variants, DPO variants, distillation strategies, memory estimation, quality metrics), intuitive prose before each formula, 5 error correction cards, 5 self-check questions with Day 1 cross-reference, quick reference card. Deleted old raw-string doc from DB, inserted Builder-generated version.
- **Deliverables**: `scripts/seed_adobe_day2_rlhf_dpo.py` (full Builder rewrite)
- **Sanity check result**: 0 validation warnings. Builder header present. All sections present (Prerequisites, Key Terms, 6 content sections, Self-Check, Quick Reference). Zero orphan single-dollar signs. 17,852 chars (up from 13,286). HTML diagrams, comparison tables, cross-references all verified.
- **Status**: [PARTIAL] (1 of 6 docs rewritten; Days 3-7 remain)
- **Request**: No task_db status change (task still in progress)
## 2026-03-27 -- [T-P0-230] Rewrite Day 3 Distributed Training doc with StudyNoteBuilder (2/6)
- **What I did**: Rewrote seed_adobe_day3_distributed.py from raw string format to StudyNoteBuilder API. Added: Prerequisites (4 items incl. Day 2/Day 5 cross-references), Term Registry (12 terms: DP, TP, PP, FSDP, ZeRO, AllReduce, AllGather, ReduceScatter, NVLink, activation checkpointing, 3D parallelism, DDP), FormulaBlock for all display math (AllReduce average, AllReduce volume, column/row split matrices, partial sum, TP comm, naive bubble, micro-batch bubble, ZeRO Stage 3 volume, memory estimation, activation memory), 3 HTML diagrams (parallelism overview table, ZeRO stages memory table, 3D parallelism layout), comparison tables (PP variants, FSDP vs DDP, bandwidth ordering, real-world 3D examples), 5 error correction cards, 5 self-check questions with Day 5 cross-reference, quick reference card. Deleted old raw-string doc from DB, inserted Builder-generated version.
- **Deliverables**: `scripts/seed_adobe_day3_distributed.py` (full Builder rewrite)
- **Sanity check result**: 0 validation warnings. Builder header present. All 13 sections present (Prerequisites, Key Terms, 8 content sections, Self-Check, Quick Reference). 19,574 chars (up from 17,374). 3 HTML diagrams, 12 terms, cross-references verified.
- **Status**: [PARTIAL] (2 of 6 docs rewritten; Days 4-7 remain)
- **Request**: No task_db status change (task still in progress)
## 2026-03-27 -- [T-P0-230] Rewrite Day 4 RoPE + Video doc with StudyNoteBuilder (3/6)
- **What I did**: Rewrote seed_adobe_day4_rope_video.py from raw string format to StudyNoteBuilder API. Added: Prerequisites (4 items incl. Day 1/Day 3 cross-references), Term Registry (11 terms: RoPE, PE, PI, NTK, YaRN, DiT, 3D VAE, KV-cache, temporal attention, ALiBi, AdaLN), FormulaBlock for all display math (theta_i base frequency, rotation matrix R_m, q/k rotation, dot-product relative proof, RoPE efficient implementation, PI position scaling, NTK base frequency, YaRN attention temperature), 5 HTML diagrams (RoPE rotation, YaRN dimension grouping, video diffusion architecture, DiT architecture, video challenges), comparison tables (PE methods 4-way, long context methods 4-way), 5 error correction cards, 5 self-check questions with Day 1 cross-reference + new Q5 (video token count calculation), quick reference card. Deleted old raw-string doc from DB, inserted Builder-generated version.
- **Deliverables**: `scripts/seed_adobe_day4_rope_video.py` (full Builder rewrite)
- **Sanity check result**: 0 validation warnings. Builder header present. All 11 sections present (Prerequisites, Key Terms, 6 content sections, Self-Check, Quick Reference). 21,838 chars (down from 22,549 -- HTML diagrams preserved, raw-string overhead removed). 5 HTML diagrams, 11 terms, cross-references verified.
- **Status**: [PARTIAL] (3 of 6 docs rewritten; Days 5-7 remain)
- **Request**: No task_db status change (task still in progress)
## 2026-03-27 -- [T-P0-230] Rewrite Day 5 Inference doc with StudyNoteBuilder (4/6)
- **What I did**: Rewrote seed_adobe_day5_inference.py from raw string format to StudyNoteBuilder API. Added: Prerequisites (4 items incl. Day 1/Day 3/Day 4 cross-references), Term Registry (13 terms: FlashAttention, HBM, SRAM, GPTQ, AWQ, SmoothQuant, KV-cache, PagedAttention, vLLM, Continuous Batching, Speculative Decoding, OBS, TensorRT-LLM), FormulaBlock for all display math (standard attention, GPTQ Hessian compensation, SmoothQuant transformation, KV-cache memory formula), 7 HTML diagrams (GPU memory hierarchy, FlashAttention tiling, IO complexity, PagedAttention, continuous batching, speculative decoding, project mapping table), comparison tables (quantization methods 4-way, serving frameworks 4-way), 5 error correction cards, 5 self-check questions with Day 3/Day 4 cross-references, quick reference card. Deleted old raw-string doc from DB, inserted Builder-generated version.
- **Deliverables**: `scripts/seed_adobe_day5_inference.py` (full Builder rewrite)
- **Sanity check result**: 0 validation warnings. Builder header present. 18 sections (Prerequisites, Key Terms, 6 content sections with subsections, Self-Check, Quick Reference). 25,610 chars (up from 25,315 -- added prerequisites, term registry, cross-references). 7 HTML diagrams, 13 terms, 40 math regions, cross-references verified.
- **Status**: [PARTIAL] (4 of 6 docs rewritten; Days 6-7 remain)
- **Request**: No task_db status change (task still in progress)
## 2026-03-27 -- [T-P0-230] Rewrite Day 6 Mock Interview doc with StudyNoteBuilder (5/6)
- **What I did**: Rewrote seed_adobe_day6_mock_interview.py from raw string format to StudyNoteBuilder API. Added: Prerequisites (5 items cross-referencing Days 1-5), Term Registry (14 terms: STAR-T, DDPM, DDIM, CFG, LDM, FlashAttention, GPTQ, AWQ, FSDP, DPO, RLHF, PPO, KV-cache, DiT), FormulaBlock for all display math (13 math regions: DDPM forward/jump/loss, CFG equation, FlashAttention IO complexity, speculative decoding acceptance/correction, PP bubble, FSDP memory, Bradley-Terry, RLHF objective, DPO loss, KL constraint), 23 HTML diagrams (STAR-T framework table, fill-in template, 3 project story outlines, 13 Q&A answer blocks, 4 speech templates, error correction table, quick reference card), 5 self-check questions with Day 1/2/3/5 cross-references, comparison of all 13 interview domains. Deleted old raw-string doc from DB, inserted Builder-generated version.
- **Deliverables**: `scripts/seed_adobe_day6_mock_interview.py` (full Builder rewrite)
- **Sanity check result**: 0 validation warnings. Builder header present. 33 sections (Prerequisites, Key Terms, 5 major content sections with subsections, Self-Check, Quick Reference). 45,631 chars (up from 41,619 -- added prerequisites, term registry, FormulaBlock math, cross-references). 23 HTML diagrams, 14 terms, 13 math regions, cross-references verified.
- **Status**: [PARTIAL] (5 of 6 docs rewritten; Day 7 remains)
- **Request**: No task_db status change (task still in progress)
## 2026-03-27 -- [T-P0-230] Rewrite Day 7 Review doc with StudyNoteBuilder (6/6)
- **What I did**: Rewrote seed_adobe_day7_review.py from raw string format to StudyNoteBuilder API. Added: Prerequisites (6 items cross-referencing all Days 1-6), Term Registry (20 terms: DDPM, DDIM, CFG, LDM, RLHF, DPO, PPO, FSDP, TP, PP, RoPE, FlashAttention, GPTQ, AWQ, KV-cache, DiT, YaRN, STAR-T, SmoothQuant, PagedAttention), FormulaBlock for all display math (15 formula blocks: DDPM forward/loss, CFG, Bradley-Terry, DPO loss, KD loss, memory-per-param, FSDP memory, PP bubble, RoPE angle, PI scaling, NTK scaling, FlashAttention IO, KV-cache size, speculative decoding acceptance), 14 HTML diagrams (6 domain checklists, concept map with cross-topic connections table, 7 error correction cards, time allocation table, 5 formula cheat sheet tables, self-check questions, quick reference card), 5 self-check questions with Day 1-6 cross-references, checklist tracker. Deleted old raw-string doc from DB, inserted Builder-generated version.
- **Deliverables**: `scripts/seed_adobe_day7_review.py` (full Builder rewrite)
- **Sanity check result**: 0 validation warnings. Builder header present. 20 sections, 65 HTML blocks, 20 terms, 15 formula blocks, 9 cross-references, 41,436 chars. All content preserved from original.
- **Status**: [DONE] (6 of 6 docs rewritten; T-P0-230 complete -- all 7 Adobe docs now use StudyNoteBuilder)
- **Request**: `task_db.py update T-P0-230 --status completed`
## 2026-03-27 -- [T-P1-231] Fix PrepNotesPage tab overflow: document dropdown
- **What I did**: Replaced document tab buttons in PrepNotesPage.tsx with a `<select>` dropdown. Tab bar now has max 3 items: Notes, Documents (N) dropdown, Forum Posts. When a document is selected from the dropdown, its title appears as a subtitle below the tab bar. Dropdown styling matches TabButton appearance (same padding, colors, rounded corners). Highlight state applied when a doc is actively selected.
- **Deliverables**: `src/frontend/src/pages/PrepNotesPage.tsx`
- **Sanity check result**: TypeScript compiles with no errors (`npx tsc --noEmit` clean). Tab bar limited to 3 items max -- no overflow on any screen size.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-231 --status completed`
## 2026-03-27 -- [T-P0-233] Day1 Expansion A: PE deep-dive + sinusoidal derivation + KV-Cache
- **What I did**: Created seed_adobe_day1_expansion_a.py that adds 3 new sections to the existing Day 1 document (id=18). Section 11: Positional Embedding deep-dive covering absolute PE, sinusoidal PE with full derivation (rotation matrix interpretation, proof that PE(pos+k) = linear transform of PE(pos) via trigonometric addition), relative PE (Shaw et al.), RoPE (rotation of Q/K vectors, relative position proof), 5-way comparison table (Learned/Sinusoidal/Shaw/RoPE/ALiBi). Section 12: KV-Cache mechanism covering why only K/V are cached (Q is per-token), memory formula (2 * n_layers * d_model * seq_len * dtype_bytes) with LLaMA-2 7B worked example, optimization techniques table (MQA/GQA/PagedAttention/Sliding Window/Quantized KV), Prefill vs Decode phase analysis. Section 13: Why predict noise not x_0, covering variance analysis (epsilon has constant variance, x_0 variance explodes), score matching equivalence, v-prediction as alternative, 3-way comparison table, conversion formulas between all three parameterizations.
- **Deliverables**: `scripts/seed_adobe_day1_expansion_a.py` (expansion seed script)
- **Sanity check result**: Document updated (12188 -> 19451 chars, +7263). All 3 new sections present (11, 12, 13). Display math formulas with $$. Comparison tables rendered. Self-Check and Quick Reference sections preserved in correct order after new content.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-233 --status completed`
## 2026-03-27 -- [T-P0-234] Day1 Expansion B: VAE details + ControlNet deep-dive + industry landscape
- **What I did**: Created seed_adobe_day1_expansion_b.py that adds 3 new sections to the existing Day 1 document (id=18). Section 14: VAE deep-dive covering encoder/decoder architecture, KL divergence regularization (closed-form formula for two Gaussians), reparameterization trick (z=mu+sigma*epsilon for differentiable sampling), beta-VAE tradeoff, VAE vs VQ-VAE comparison table. Section 15: ControlNet expanded covering complete architecture (frozen UNet + trainable copy + zero conv), training procedure (600 GPU-hours vs 150K for SD from scratch), multi-ControlNet composition (weighted sum), ControlNet vs T2I-Adapter comparison table, IP-Adapter architecture (CLIP image encoder + decoupled cross-attention with separate K/V projections). Section 16: Industry landscape covering 9 major products table (SD, SDXL, SD3, Midjourney, DALL-E 3, Firefly, Imagen, Flux, Fooocus), UNet->DiT architecture evolution, 6 application domains, and interview Q&A.
- **Deliverables**: `scripts/seed_adobe_day1_expansion_b.py` (expansion seed script)
- **Sanity check result**: Document updated (19451 -> 27409 chars, +7958). All 3 new sections present (14, 15, 16). No blank lines between table rows. Comparison tables rendered. Self-Check and Quick Reference sections preserved in correct order after new content.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-234 --status completed`
## 2026-03-27 -- [T-P0-235] Day1 Expansion C: Answer all checklist questions
- **What I did**: Created seed_adobe_day1_expansion_c.py that answers all 10 existing Self-Check questions and adds 6 new checklist items for expanded content (sections 11-16). Each question gets a comprehensive 3-5 sentence blockquote answer in Chinese, referencing specific formulas from the note. New questions cover: PE comparison (4 methods), KV-Cache memory estimation, noise/x0/v-prediction variance analysis, VAE reparameterization trick, ControlNet training procedure, and industry product comparison.
- **Deliverables**: `scripts/seed_adobe_day1_expansion_c.py` (expansion seed script)
- **Sanity check result**: Document updated (27409 -> 35620 chars, +8211). 16 answers for 16 checklist items (10 original + 6 new). All answers in blockquote format. Self-Check and Quick Reference sections preserved. No blank lines between table rows.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-235 --status completed`
## 2026-03-27 -- [T-P0-236] Rewrite Day 2 (RLHF/DPO/Distillation) to Chinese
- **What I did**: Created seed_adobe_day2_chinese.py that replaces the English Day 2 document (company_documents id=12, 17852 chars) with comprehensive Chinese version (14575 chars). Content sourced from user supplement file (笔记2更新.md, 507 lines). All 8 sections covered: RLHF 3-stage pipeline with full math (SFT/RM/PPO formulas), DPO 4-step derivation (Z(x) cancellation), PPO clip mechanism + 4-model GPU analysis, DPO vs RLHF multi-dimensional comparison table, variants (GRPO/RLAIF/KTO/SimPO/IPO/ORPO), LLM distillation (dark knowledge, temperature, T-squared correction, 70B->7B recipe with memory estimation), 5 error corrections table, 5 Q&As with blockquote answers, and formula cheat sheet. Used StudyNoteBuilder with 14 FormulaBlock instances for proper math rendering.
- **Deliverables**: `scripts/seed_adobe_day2_chinese.py` (seed script)
- **Sanity check result**: Document updated (17852 -> 14575 chars). 14 formula blocks, 5 checklist items with answers, 9 blockquote lines, 0 table blank-line issues, 0 emoji, 0 validation warnings.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-236 --status completed`
## 2026-03-27 -- [T-P0-237] Rewrite Day 3 (Distributed Training) to Chinese
- **What I did**: Created seed_adobe_day3_chinese.py that replaces the English Day 3 document (company_documents id=13, 19574 chars) with comprehensive Chinese version (13780 chars). Content sourced from user supplement file (笔记3更新.md, 385 lines). All 14 sections covered: 13B memory estimation (16P formula), HBM vs SRAM, 4-strategy panorama table, DP detail (AllReduce = ReduceScatter+AllGather, gradient bucketing, limitations), TP detail (column-row split, why column-first, attention head split, NVLink constraint), PP detail (bubble formula, micro-batch, GPipe/1F1B/Interleaved), FSDP/ZeRO Stages 1-3 (forward/backward workflow), 3D parallelism (TP*PP*DP with real configs: GPT-3/PaLM/Llama), activation checkpointing (sqrt(L) strategy), comm primitives, 5 misconceptions, decision tree, memory cards, 5 Q&As with answers. Used StudyNoteBuilder with 8 FormulaBlock instances.
- **Deliverables**: `scripts/seed_adobe_day3_chinese.py` (seed script)
- **Sanity check result**: Document updated (19574 -> 13780 chars). 8 formula blocks, 5 checklist items with answers, 8 blockquote lines, 0 table blank-line issues, 0 emoji, 0 validation warnings.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-237 --status completed`
## 2026-03-28 -- [T-P2-209] Verify db-missing warning already present in session_context.py
- **What I did**: Investigated T-P2-209 which asked to port db_missing_warning from template to MLInterviewPrep session_context.py. Found the feature already exists at lines 475-490 of MLInterviewPrep's session_context.py. The template actually does NOT have this block (grep confirmed 0 matches). Task description had the direction backwards. Marked as completed since the feature is already present.
- **Deliverables**: No code changes needed
- **Sanity check result**: Grep confirmed db_missing_warning exists in MLInterviewPrep (4 matches) and is absent from template (0 matches). All remaining tasks (T-P2-185/186/187/206/207/208) are SYNC tasks targeting helixos or template, blocked by cross-project file permissions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-209 --status completed`
## 2026-03-28 -- [T-P2-185] Add no-bare-python rule to helixos CLAUDE.md Prohibited Actions
- **What I did**: Added the "Never use bare python in hook commands or scripts" rule to both the shared template (blog_proj/shared/claude_md_shared.md) and re-synced helixos CLAUDE.md via sync.py. The rule warns about the Windows Store stub (exit 49) and directs to use /c/Anaconda/python.exe absolute path.
- **Deliverables**: blog_proj/shared/claude_md_shared.md (added rule), helixos/CLAUDE.md (re-synced)
- **Sanity check result**: Grep confirmed "bare.*python" appears at line 93 of helixos CLAUDE.md. Sync script ran successfully.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-185 --status completed`
## 2026-03-31 -- [T-P1-147] ML Fundamentals Doc T5: Naive Bayes from scratch
- **What I did**: Created comprehensive Naive Bayes from-scratch content (599 lines, 21.7K chars). Bayes' theorem foundation and derivation, conditional independence assumption ("Naive") with full justification (4 reasons why it works despite being wrong), parameter complexity comparison. Laplace Smoothing with Dirichlet prior interpretation and alpha analysis. Three variants: Gaussian NB (continuous features, var_smoothing), Multinomial NB (count features, text classification), Bernoulli NB (binary features, explicit absence modeling) with comparison table. Pure Python implementations of all 3 variants with log-space computation and log-sum-exp trick. sklearn verification for all 3 (Iris dataset + 20newsgroups text). Pros/cons analysis, NB vs LR (generative vs discriminative) comparison with Ng & Jordan reference, 5 interview Q&As, practical application guide.
- **Deliverables**: `MLInterviewPrep/data/t5_naive_bayes.md`
- **Sanity check result**: File is 599 lines, 21,709 bytes. Contains 7 Python code blocks (3 from-scratch + 3 sklearn + 1 log-sum-exp), 12 major sections, all required elements verified (Bayes theorem, Naive derivation, Laplace, Gaussian, Multinomial, Bernoulli, sklearn).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-147 --status completed`
## 2026-03-31 -- [T-P1-148] ML Fundamentals Doc T6: Tree models comprehensive
- **What I did**: Created comprehensive tree models from-scratch content (1143 lines, 41.5K chars). Decision Tree fundamentals with 3 impurity measures (Entropy, Gini, Classification Error) and full calculation example. ID3/C4.5/CART three-algorithm comparison with Information Gain, Gain Ratio, Gini derivations and complete "tennis" dataset worked example. Pruning: Pre-Pruning (5 sklearn params), Post-Pruning, CCP with cost-complexity objective derivation and sklearn code. Random Forest: core principle, Variance formula derivation showing Bagging reduces second term and Feature Subsampling reduces correlation (first term), OOB error. AdaBoost: complete algorithm derivation with epsilon/alpha/weight update formulas, exponential loss connection, Decision Stump implementation. GBDT: negative gradient (pseudo-residual) framework for arbitrary loss, Shrinkage analysis, 6 regularization methods. XGBoost/LightGBM/CatBoost comparison with second-order Taylor expansion. Pure Python implementations of Decision Tree, Random Forest, AdaBoost, GBDT with sklearn verification for all 4. 5 interview Q&As, application guide, comprehensive comparison table.
- **Deliverables**: `MLInterviewPrep/data/t6_tree_models.md`
- **Sanity check result**: File is 1143 lines, 41,485 bytes. Contains 9 Python code blocks (4 from-scratch implementations + 4 sklearn verifications + 1 CCP demo), 12 major sections. All required elements verified (ID3/C4.5/CART, Pruning, Random Forest, AdaBoost, GBDT, Shrinkage).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-148 --status completed`
## 2026-03-31 -- [T-P1-149] ML Fundamentals Doc T7: Weight Initialization from scratch
- **What I did**: Created comprehensive weight initialization from-scratch content (731 lines, 27.2K chars). Variance propagation analysis framework with full derivation. Failed initialization analysis: zero init (symmetry problem), too-large init (variance explosion), too-small init (signal vanishing) with demo code. Xavier/Glorot: forward constraint, backward constraint, harmonic compromise derivation, normal and uniform forms, Sigmoid/Tanh applicability analysis. He/Kaiming: ReLU half-interval truncation proof via half-Gaussian integral, factor-2 compensation, fan_in/fan_out modes, Leaky ReLU adjustment formula. Other methods: Orthogonal (QR decomposition, RNN use case), LSUV (data-driven), Fixup (BN-free ResNets). Pure Python implementations of Xavier normal/uniform, He normal/uniform/leaky, Orthogonal init, and variance propagation verification experiment. LoRA initialization strategy (from Doc 17): zero B + random A, why no symmetry breaking issue. PyTorch API verification: all init functions, MLP with hooks for variance tracking, Conv2d fan calculation. 5 interview Q&As, practical lookup table (10 scenarios), formula summary table.
- **Deliverables**: `MLInterviewPrep/data/t7_weight_initialization.md`
- **Sanity check result**: File is 731 lines, 27,150 bytes. Contains 7 Python code blocks (4 from-scratch implementations + 1 variance experiment + 1 PyTorch verification + 1 zero-init demo), 12 major sections. All required elements verified (zero init, Xavier derivation, He derivation, Leaky ReLU, Orthogonal, LoRA, PyTorch API).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-149 --status completed`
## 2026-03-31 -- [T-P0-244] Uber BPS: Update phone screen prep doc with BPS format
- **What I did**: Rewrote docs/uber_phone_screen_prep.md from the old 2-round phone screen format to the recruiter-confirmed BPS (Behavioral + Problem Solving) format. Updated structure: 5min intro, 40-50min coding+D&A, 5min Q&A. Added 9 sections: BPS format overview, time allocation strategy, problem-solving approach, problem categorization by pattern (BFS/DFS 11 problems, UF 3, BS 5, DP 4, monotonic stack, sliding window, OOD 3, greedy/math 3), D&A prep with 2 project walkthroughs and diagram elements, ML fundamentals review (KNN deep-dive + 10 core concepts), HackerRank tips (before/during/gotchas), content area priority summary, and comprehensive BPS checklist. Incorporated 1p3a interview reports for pattern analysis and tips.
- **Deliverables**: `docs/uber_phone_screen_prep.md` (309 lines, 15.5KB)
- **Sanity check result**: All 6 task requirements verified: (1) Updated BPS structure with recruiter timing, (2) D&A prep with project diagrams, (3) ML fundamentals + KNN section, (4) Problem categorization by 8 patterns with 30+ problems, (5) HackerRank tips section, (6) Time allocation table. Cross-reference from uber_hr_call_prep.md still works.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-244 --status completed`
## 2026-03-31 -- [T-P0-241] Uber BPS: Seed 1p3a interview problems into DB
- **What I did**: Created seed script to parse all Uber interview problems from staging/uber题目整理.txt into mle_prep.db. Step 1: Updated 18 existing LC problems (230, 547, 337, 1020, 977, 815, 981, 17, 23, 1197, 1697, 549, 987, 79, 994, 2503, 2858, 2791) with '1point3acres' source badge and [1p3a Uber] interview notes (variants, follow-ups, tips from 1p3a reports). Created LC 1696 (Jump Game VI) as new entry. Step 2: Created 25 custom non-LC problem entries with titles, descriptions, tags, patterns, and detailed notes preserving original Chinese context. Problems include: Purchase Optimization, Customer Revenue & Referral Tracking, Uber Rider Connection Log, Cart & Pricing Engine OOD, Parking Lot OOD, Driver Queue SD, and 19 more. Step 3: Updated Uber BPS interview event (#8) with problem pool reference (44 1p3a-sourced problems: 19 LC + 25 custom).
- **Deliverables**: `scripts/seed_uber_1p3a_problems.py`, `data/mle_prep.db` (updated)
- **Sanity check result**: 19/19 LC problems verified with Uber tag + 1p3a source + notes. 25 custom problems created. Interview event #8 updated with 44-problem reference. Script is idempotent (re-run skips existing entries).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-241 --status completed`
## 2026-03-31 -- [T-P0-241] Supplement: Add missing custom problems + cleanup duplicates
- **What I did**: Created additional seed script (seed_uber_bps_problems.py) that added 8 missing custom problems: Elevator Binary Search (OA), Server Throughput with Heap (OA), Cart & Pricing Engine (OOD), Min Operations n to 0 (NAF), Shortest Subarray with k Distinct Integers, N-ary Tree 3-Part Problem, Min Edge Reversal for Optimal Root (Re-rooting DP), Palindrome Paths in Tree (Bitmask XOR). Also updated interview event description. Cleaned up 6 near-duplicate entries caused by slight title differences between seed scripts. Re-verified all 19 LC problems have Uber tag + 1p3a source + interview notes.
- **Deliverables**: `scripts/seed_uber_bps_problems.py`, `data/mle_prep.db` (updated: 27 custom + 19 LC = 46 total Uber BPS problems)
- **Sanity check result**: 19/19 LC verified OK. 27 custom problems (no duplicates). Interview event updated. 6 duplicates cleaned.
- **Status**: [DONE]
- **Request**: No task status change (T-P0-241 already completed)
## 2026-03-31 -- [T-P0-242] Uber BPS: LC solutions for all 19 Uber-tagged problems
- **What I did**: Created comprehensive solutions document covering all 19 LC problems from Uber BPS interviews. Each solution includes: approach explanation, clean Python code, time/space complexity analysis. CRITICAL follow-ups and variants included: LC 230 (6 approaches: iterative, recursive, kth largest, Morris O(1) space, augmented BST, flatten), LC 981 (3 follow-ups: 1M+ req/sec sharding, thread safety, amortized complexity), LC 17 (10-digit phone number variant with iterative approach), LC 79 (8-direction straight line variant), LC 1197 (finite board variant), LC 1697 (reversed edge weight >= k variant), LC 2858 (re-rooting DP with 1-indexed warning), LC 2791 (bitmask XOR palindrome path counting), LC 1696 (jump +prime ending in 3 variant with sieve). Solutions organized by pattern: tree (230, 337, 549, 987, 2858, 2791), graph/BFS (994, 1020, 815, 1197, 2503), union-find (547, 1697), binary search (981, 977), backtracking (17, 79), heap (23), DP (1696). Session 2: Also seeded all 19 solutions into DB notes field via `scripts/seed_uber_lc_solutions.py` (idempotent).
- **Deliverables**: `docs/uber_bps_lc_solutions.md` (1017 lines), `scripts/seed_uber_lc_solutions.py`, `data/mle_prep.db` (19 problems updated with solution notes)
- **Sanity check result**: 19/19 LC problems verified with solutions in both doc and DB. Script is idempotent (re-run skips existing). 6 variants, 4+ follow-ups documented. All solutions include time/space complexity.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-242 --status completed`
## 2026-03-31 -- [T-P0-243] Uber BPS: Solutions for all 25 custom non-LC interview problems
- **What I did**: Created comprehensive solutions document covering all 25 custom (non-LeetCode) Uber BPS interview problems. Each solution includes: reconstructed problem statement, approach explanation, clean Python code, time/space complexity, edge cases, and follow-ups. Key problems with detailed follow-ups: (3) Rider Connection Log -- Union Find base + BFS rebuild for block events, (6) Cart & Pricing Engine OOD -- Strategy pattern with surge/membership/promo rules and receipt breakdown, (16) Parking Lot OOD -- O(1) optimized version with free-spot queues, (19) Re-rooting DP for edge reversal, (20) Palindrome paths with bitmask XOR. Problems organized by pattern: Binary Search (1,4,13,15), BFS/DFS (7,22,23,25), Union Find (3), DP (18,19,20), Greedy (9,17), Monotonic Stack (11), Sliding Window (10), Heap (5), OOD (2,6,16), Grid (8,21), Tree (14), Tracking (12). Summary table and pattern quick reference included.
- **Deliverables**: `docs/uber_bps_custom_solutions.md` (2615 lines, 25 problems)
- **Sanity check result**: 25/25 problems verified with solutions. All follow-ups from task spec covered. Summary table matches all problems. Pattern quick reference cross-references all 25.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-243 --status completed`
## 2026-03-31 -- [T-P1-247] Uber BPS: Problem pattern cheat sheet by algorithm
- **What I did**: Created comprehensive pattern cheat sheet organizing all 44 Uber BPS problems (19 LC + 25 custom) by algorithm pattern. 14 pattern sections each with: recognition signals, code template, problem table with key insights and complexity, and practical tips. Includes full complexity summary tables for both LC and custom problems, plus a decision-tree flowchart for pattern recognition during interviews.
- **Deliverables**: `docs/uber_bps_pattern_cheatsheet.md` (721 lines, 14 patterns, 44 problems)
- **Sanity check result**: All 19 LC problems and 25 custom problems present in summary tables. Every problem appears in at least one pattern section. Decision tree covers all major pattern signals.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-247 --status completed`
## 2026-03-31 -- [T-P0-243] Seed custom solutions into DB notes
- **What I did**: Created `scripts/seed_uber_custom_solutions.py` to parse `docs/uber_bps_custom_solutions.md` and seed detailed solutions into DB notes field for all 22 custom problems (3 LC variants correctly skipped). Script is idempotent via `[Uber BPS Custom Solution]` tag check. Also committed the solutions doc (2615 lines) and pattern cheat sheet from previous uncommitted sessions.
- **Deliverables**: `scripts/seed_uber_custom_solutions.py`, `data/mle_prep.db` (22 problems updated with 1700-6200 char solution notes each)
- **Sanity check result**: 22/22 custom problems seeded, 3 LC variants skipped. Re-run produces 0 updates (idempotent). All notes contain Python code blocks and complexity analysis.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-243 --status completed`
## 2026-03-31 -- [T-P1-245] Create D&A prep document for Uber BPS
- **What I did**: Committed `docs/uber_bps_design_architecture.md` (614 lines) created in a prior session. Document covers: 2 project showcases (Ranking-as-Allocation, LLM Eval Pipeline) with ASCII diagrams, end-to-end flows, and trade-off discussions; STAR-T trade-off framework; 5 Uber system design patterns (Driver Maps, Shopping Cart, Driver Queue, ETA, Food Ordering); common D&A follow-ups from 1p3a reports; communication tips; practice checklist.
- **Deliverables**: `docs/uber_bps_design_architecture.md`
- **Sanity check result**: All 4 task requirements met: (1) project showcases with diagrams, (2) trade-off discussions, (3) 5 Uber SD patterns, (4) 1p3a follow-ups. Document cross-references `uber_phone_screen_prep.md`.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-245 --status completed`
## 2026-03-31 -- [T-P1-246] KNN from-scratch + ML fundamentals review
- **What I did**: Created `docs/uber_bps_knn_ml_fundamentals.md` (679 lines) covering KNN implementation from scratch with full Python class (classification + regression, 4 distance metrics, weighted voting), k selection strategies, optimization data structures (KD-Tree, Ball Tree, LSH), 6 KNN interview questions with answers, and ML fundamentals review (bias-variance, overfitting/regularization, cross-validation, evaluation metrics, feature engineering). Includes quick-fire Q&A cheat sheet for the ~5min ML segment.
- **Deliverables**: `docs/uber_bps_knn_ml_fundamentals.md`
- **Sanity check result**: All 5 task requirements met: (1) KNN from scratch with distance metrics/k selection/weighted KNN, (2) classification vs regression, (3) KD-Tree/Ball Tree/LSH optimization, (4) interview Qs covering curse of dimensionality/feature scaling/categorical features, (5) ML fundamentals: bias-variance/overfitting/CV/metrics.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-246 --status completed`
## 2026-03-31 -- [T-P2-240] Add _temp*.json pattern to .gitignore
- **What I did**: Added `_temp*.json` and `_temp*.py` patterns to `.gitignore` to prevent accidental commits of temp artifacts from content seeding scripts.
- **Deliverables**: `.gitignore` (updated)
- **Sanity check result**: `_temp_docs.json` no longer appears in `git status` output after adding the pattern.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-240 --status completed`
## 2026-03-31 -- [T-P2-248] Create timed mock interview problem sets
- **What I did**: Created `docs/uber_bps_mock_sets.md` with 3 timed mock BPS interview sets (45min each). Set 1: LC 230 variant + Rider Connection UF. Set 2: LC 994 BFS + Purchase Optimization BS. Set 3: LC 547 graph + Cart Pricing OOD. Each set includes problem statements, follow-ups, scoring rubrics, debrief checklists, and a practice schedule.
- **Deliverables**: `docs/uber_bps_mock_sets.md` (new, 364 lines)
- **Sanity check result**: All 3 sets contain correct problem pairings per task spec. Each has 1 medium (20 min) + 1 medium-hard (20 min) + follow-ups (5 min). Problems reference solutions in existing docs.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-248 --status completed`
## 2026-03-31 -- [T-P0-249] Import Uber BPS prep docs into company_documents
- **What I did**: Imported 8 Uber prep documents into company_documents table (company_id=5). Updated existing doc#3 (Phone Screen Prep, 2499 chars) with full uber_phone_screen_prep.md content (15,479 chars). Inserted 7 new docs: LC Solutions, Custom Solutions, Pattern Cheat Sheet, Design & Architecture, KNN & ML Fundamentals, Mock Interview Sets, HR Call Prep. Updated Uber prep_notes with document index header referencing all 9 documents.
- **Deliverables**: `scripts/import_uber_bps_docs.py` (new), `data/mle_prep.db` (9 Uber docs, 398,963 total chars)
- **Sanity check result**: All 9 documents verified in DB with correct titles, source_type=prep_doc, and content lengths matching source files. Prep_notes updated from 22,889 to 23,788 chars with reference index.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-249 --status completed`
## 2026-03-31 -- [T-P0-250] Organize LinkedIn prep notes into company_documents
- **What I did**: Cleaned up 5 LinkedIn document titles (removed Chinese, made descriptive). Updated LinkedIn prep_notes (company_id=1) with document index header listing all 9 documents (matching Uber format). Added solution notes for 16 key LinkedIn problems that lacked them: LC 210, 380, 236, 314, 127, 176, 181, 366, 311, 362, 394, 1249, 528, 348, 227, 588. These cover the prep checklist problems and top-frequency Questions Index problems.
- **Deliverables**: `scripts/organize_linkedin_docs.py` (new), `data/mle_prep.db` (9 LinkedIn docs with clean titles, 125 problems now have notes)
- **Sanity check result**: All 9 documents verified with proper English titles. prep_notes updated from 1886 to 2736 chars with document index. All 16 key problems confirmed with notes. Total LinkedIn problems with notes increased from 109 to 125.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-250 --status completed`

## 2026-03-31 -- [T-P0-252] Condense ML Fundamentals From-Scratch guide
- **What I did**: Audited all 8 source files (t1-t8, 162K chars total) for code duplication. Identified 5 major duplication categories: mini-batch GD loops (t1/t2/t3), PyTorch training loops (t1/t2/t3), logistic regression L2 variant (t3), sklearn verification patterns (t5/t6), optimizer implementations (t8). Applied targeted condensation: removed duplicate logistic SGD from t1 (covered in t3), merged logistic_regression + logistic_regression_l2 into single function with lam parameter in t3, condensed 3 PyTorch implementations to config table referencing t1 canonical template, removed duplicate GLM section from t3 (identical to t2 Section 10), extracted optimizer template pattern in t8 with collapsible full implementations, consolidated sklearn verifications in t5/t6 to compact format.
- **Deliverables**: `scripts/condense_ml_fundamentals.py` (new condensation script), 6 modified source files (t1/t2/t3/t5/t6/t8), `data/mle_prep.db` (docs 27/28/29 updated with condensed merged content)
- **Sanity check result**: Source files reduced from 162,050 to 151,482 chars (6.5% reduction, 10.5K chars saved). All theory, derivations, and interview Q&A preserved. Key structural improvements: cross-topic references added, duplicate code eliminated, optimizer implementations shown as template + core update logic. DB docs 27/28/29 all updated to 151,774 chars (from 162,209).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-252 --status completed`
