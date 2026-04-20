# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-540: [T-MLF-03.5] [BARRIER] Template lock checkpoint: dev server review + canonical snippet
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-539
- **Description**: BARRIER TASK: runner MUST stop here pending user review. Steps:
  1. Start frontend dev server (cd src/frontend && npm run dev) in background; verify it serves on localhost
  2. For each of the 7 Cat 1-2 leaves (#1-4 + #5/#6/#7 per inventory), open the drawer in browser and capture rendering notes (KaTeX OK? bold terms? section breaks? GFM tables OK?)
  3. Produce docs/ml_fundamentals_template.md — canonical 5-section markdown template (问题设定 / 推导 / 物理意义 / 常见追问 / 参考) with concrete formatting rules
  4. Append a [BARRIER-AWAITING-USER] entry to PROGRESS.md
  5. CRITICAL: end the session with 'task_db.py update T-P0-540 --status review' (NOT --status completed). This leaves T-P0-541 blocked so the orchestrator's has-unblocked check returns false and the runner exits, prompting the user to manually review the template before approving downstream content fills.
  6. Commit template doc + PROGRESS entry as '[T-MLF-03.5] Template lock checkpoint - awaiting user review'

After user reviews docs/ml_fundamentals_template.md and approves, they will run 'task_db.py update T-P0-540 --status completed' and re-launch autonomous_run.sh.

#### T-P0-541: [T-MLF-04] T1 content fill Cat 3-4 (7 Q: Unsupervised + DL Training)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-540
- **Description**: Write description markdown for 7 leaves per the canonical template (from gamma_barrier):
  Cat 3 (Unsupervised): #8 K-means, #9 EM+GMM
  Cat 4 (DL Training): #10 BN vs LN, #11 Adam/SGD/AdamW, #12 Gradient Vanish/Explode, #13 Dropout, #14 Activation Evolution

T1 = verbatim cleanup; #10/#11/#14 have non-trivial acronym expansion (BN/LN/GELU/GLU/SwiGLU).
Via scripts/seed_ml_fundamentals_content_cat34.py (idempotent).

#### T-P0-542: [T-MLF-05] T2 content fill Cat 5 (6 Q: Attention & Transformer)
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-541
- **Description**: Write description markdown for 6 leaves:
  #15 Self-Attention Complexity (merge with its linear-attention deep-dive subsection)
  #16 Scaled Dot-Product (why /√d)
  #17 MHA/MQA/GQA — REBUILD the comparison table (original is collapsed in attachment)
  #18 Position Encoding (Sinusoidal/Learned/RoPE/ALiBi)
  #19 KV Cache — FIX the LLaMA-2-7B memory formula (original is mis-formatted)
  #20 Pre-norm vs Post-norm

T2 = polish: full acronym expansion (SSM, HBM, SRAM, RoPE, ALiBi, NTK, YaRN, QK-Norm, µP) + format-bug fixes.
Via scripts/seed_ml_fundamentals_content_cat5.py (idempotent).

#### T-P0-543: [T-MLF-06a] [BARRIER] T3 Y-depth #21 SFT/RLHF/DPO (calibration session)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-542
- **Description**: CALIBRATION BARRIER: runner MUST stop here pending user review.

Write a full Y-depth golden answer for Q#21 (SFT / RLHF / DPO) into framework_nodes.description for the leaf at path 'ml-fundamentals/llm_stats/sft-rlhf-dpo' via scripts/seed_ml_fundamentals_content_q21.py (idempotent, sha256 guard).

5-section structure (per template from T-P0-540 review):
  1. 问题设定 — three objective types defined rigorously
  2. 推导 — Bradley-Terry RM loss; PPO with KL-constraint; DPO closed-form derivation showing Z(x) cancellation step-by-step
  3. 物理意义 — why ref model stays as KL anchor; what 'reward hacking' means; why DPO is supervised but still aligned
  4. 常见追问预判 — 5+ items (DPO vs IPO vs KTO; β temperature interpretation; offline vs online; reward overoptimization; iterative DPO)
  5. 参考 — 2-3 paper refs

Full acronyms on first occurrence, formatted **English** (acronym, 中文): SFT (Supervised Fine-Tuning), RLHF (Reinforcement Learning from Human Feedback), DPO (Direct Preference Optimization), PPO (Proximal Policy Optimization), RM (Reward Model), KL (Kullback-Leibler), MLE (Maximum Likelihood Estimation).

CRITICAL: end the session with 'task_db.py update T-P0-543 --status review' (NOT completed). Leaves T-P0-544 blocked so user can read the rendered drawer and confirm the Y-depth standard before T-P0-544/545 reuse it as template.

Commit as '[T-MLF-06a] DPO golden answer Y-depth calibration - awaiting user review'.

#### T-P0-544: [T-MLF-06b] T3 Y-depth #22 MoE routing + load balancing (template from zeta1)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-543
- **Description**: Apply the calibrated Y-depth template (from zeta1 review) to #22 MoE.

Four sections with: top-k routing math, load-balancing aux loss derivation (f_i, P_i), expert collapse definition, capacity factor definition, Switch (k=1) vs Mixtral (k=2) examples, drop-token behavior.

Full acronyms: MoE=Mixture of Experts.
Via scripts/seed_ml_fundamentals_content_q22.py (idempotent).

#### T-P0-545: [T-MLF-06c] T3 Y-depth #25 MLE vs MAP (upgraded from X to Y)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-544
- **Description**: Upgrade #25 from original X-depth (acronym-only) to full Y-depth.

Original covers ~60% already (Gaussian→L2 and Laplace→L1 derivations present). Add:
  Section 1: Frequentist vs Bayesian framing
  Section 2: Full MLE/MAP derivation + prior-as-regularizer equivalence (keep existing)
  Section 3: Physical meaning — prior 'sharpness' σ or b controls λ
  Section 4: 常见追问 (conjugate priors, n→∞ limit, when to prefer MAP, credible vs confidence intervals)

Full acronyms: MLE=Maximum Likelihood Estimation, MAP=Maximum A Posteriori, KKT=Karush-Kuhn-Tucker.
Via scripts/seed_ml_fundamentals_content_q25.py (idempotent).

#### T-P0-546: [T-MLF-06d] T3 X-depth batch #23/#24/#26/#27 (Tokenization, Chinchilla, CLT/LLN, A/B test)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-545
- **Description**: X-depth: keep original structure, expand all acronyms on first use, fix formula context holes.

  #23 Tokenization — BPE=Byte Pair Encoding, PMI=Pointwise Mutual Information; preserve BPE/WordPiece/SentencePiece comparison
  #24 Chinchilla scaling — add Kaplan 2020 / Hoffmann 2022 paper refs; formalize '~20 tokens/param' rule; add inference-cost note
  #26 CLT vs LLN — CLT=Central Limit Theorem, LLN=Law of Large Numbers; define iid, a.s., →_P, →_d symbols
  #27 A/B test — FWER=Family-Wise Error Rate, FDR=False Discovery Rate, MDE=Minimum Detectable Effect, BH=Benjamini-Hochberg; add power=1-β intuition

Via scripts/seed_ml_fundamentals_content_q2324_2627.py (idempotent).

#### T-P0-547: [T-MLF-07] MLFundamentals.tsx page + ?cat=&slug= deep-link
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-546
- **Description**: Create src/frontend/src/pages/MLFundamentals.tsx modeled on QuickIndex.tsx:
  - Top tab bar: 6 categories (classical_ml, eval_data, unsupervised, dl_training, attention_transformer, llm_stats)
  - URL state: ?cat=<cat_slug>&slug=<question_slug>
  - Each category: grid of cards (title_zh / title_en / interview_freq badge)
  - Card click → FrameworkNodeDrawer opens with that leaf's description
  - Deep-link behavior: on page load, if ?slug= present, auto-open drawer; closing drawer clears slug from URL; changing tab preserves slug if valid in new cat else clears
  - Footer cross-link: '延伸: MLSD pillar' + '/quick-index?section=ml'

Route added in App.tsx: '/ml-fundamentals'.
AC: build passes (npm run build); all 27 drawers open; URL deep-link shared across reload.

#### T-P0-548: [T-MLF-08] Sidebar navItem + route wiring
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-547
- **Description**: Edit src/frontend/src/components/Sidebar.tsx:
  add { to: '/ml-fundamentals', label: 'ML 八股文' } between Quick Index and Framework in navItems.

AC: sidebar shows new item at correct position; clicking navigates to /ml-fundamentals; no TS errors.

### P1 -- Should Have (agentic intelligence)

#### T-P1-549: [T-MLF-09] KaTeX/drawer smoke test — all 27 drawers
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-548
- **Description**: Run npm run dev; manually open every one of the 27 question drawers; record rendering status in docs/ml_fundamentals_smoke.md.

Per drawer: {slug, KaTeX OK y/n, GFM table OK y/n, callout render OK y/n, notes}.

If anything broken: file follow-up task via task_db.py add; do NOT fix silently.
AC: smoke report committed; each of 27 has a row.

#### T-P1-550: [T-MLF-10] Content QA pass — acronyms, formula context, term definitions
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-549
- **Description**: Walk each of 27 leaf descriptions and verify:
  (1) every acronym has first-occurrence full expansion in **English** (缩写, 中文) format
  (2) every standalone formula has surrounding prose context
  (3) any jargon (expert collapse, FWER, MDE, ...) has inline definition
Any issue found: update the corresponding seed_ml_fundamentals_content_*.py and re-run; do NOT edit DB directly.

AC: diffs committed; sha256 of affected rows changed; seed re-run is no-op.

### P2 -- Nice to Have

#### T-P2-551: [T-MLF-11] Google Prep Hub id=53 cross-link to /ml-fundamentals
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-550
- **Description**: Via scripts/seed_google_hub_mlf_crosslink.py (idempotent with sha256 guard):
  append to company_documents.content id=53 a new '系统性八股文复习' bucket above the Fundamentals bucket, linking to '/ml-fundamentals'.
Preserve all existing Tier-2/3 buckets byte-identical (sha256 guarded).

AC: id=53 has new bucket; runs twice: 1 update / 0 updates.

### P3 -- Stretch Goals

## Blocked

#### T-P1-184: [SYNC] helixos: Fix broken hooks -- use absolute Python path + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: All hooks in helixos settings.json use bare python which resolves to the Windows Store stub (exit 49) on this machine. MLInterviewPrep already has the fix applied.

Actions needed:
1. Copy .claude/hooks/setup_python_env.sh from MLInterviewPrep to helixos (writes Anaconda to CLAUDE_ENV_FILE)
2. Update helixos .claude/settings.json: replace all python with /c/Anaconda/python.exe in ALL hook commands
3. Add SessionStart hook entry for setup_python_env.sh

BLOCKED: Claude Code file permissions block writes to helixos .claude/hooks/ directory from MLInterviewPrep session. Must be done from a helixos session or manually.

#### T-P1-238: [SYNC] Fix helixos: replace bare python with absolute path in settings.json hooks
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/settings.json uses bare `python` for all hook commands (plan_mode_hook, block_dangerous, commit_msg_guard, secret_guard, tasks_md_guard, file_watch_warn, yaml_validate, lint_check, test_check, archive_check, session_context). Per CLAUDE.md Prohibited Actions: bare python resolves to Windows Store stub (exit code 49) and hooks silently fail. Fix: replace all `python "$CLAUDE_PROJECT_DIR/..."` with `/c/Anaconda/python.exe "$CLAUDE_PROJECT_DIR/..."`. Source: MLInterviewPrep settings.json (already fixed). Also add setup_python_env.sh as first SessionStart hook (bash "$CLAUDE_PROJECT_DIR/.claude/hooks/setup_python_env.sh") -- MLInterviewPrep has this, helixos does not. Copy setup_python_env.sh from MLInterviewPrep if not present.

#### T-P1-254: [SYNC] helixos: Fix bare python in settings.json + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: CRITICAL: helixos settings.json uses bare python for ALL hook commands. On Windows, bare python resolves to the AppData Store stub (exit code 49), silently breaking all hooks. Fix: (1) Replace all bare python with /c/Anaconda/python.exe in settings.json. (2) Add setup_python_env.sh SessionStart hook (copy from MLInterviewPrep) to inject Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE. CLAUDE.md already documents this prohibition (added 2026-03-21 via propagation) but the fix was never applied. This is the same root cause as MLInterviewPrep lesson [2026-03-20] #bash-tool #path.

#### T-P1-319: [SYNC] helixos: Fix bare python in settings.json hooks (critical)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ALL hook commands in helixos settings.json use bare python instead of /c/Anaconda/python.exe. This causes exit code 49 on Windows Store stub. Also missing setup_python_env.sh in SessionStart. Actions: (1) Replace python with /c/Anaconda/python.exe in every hook command. (2) Add setup_python_env.sh as first SessionStart hook copied from MLInterviewPrep. Source: MLInterviewPrep settings.json, LESSONS.md 2026-03-20.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/hooks/test_check.py still imports and uses check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed the cache in T-P2-188 (commit abf6543), per the lesson that stop caches can produce false passes when files change between sessions.

Action: Update helixos/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove check_stop_cache/write_stop_cache import and usage. Run tests after to confirm hook still works.

Source: MLInterviewPrep/.claude/hooks/test_check.py (current, cache-free version).

#### T-P2-208: [SYNC] Remove deprecated stop-cache from template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: claude-code-project-template/.claude/hooks/test_check.py still uses check_stop_cache/write_stop_cache from hook_utils. The lesson [2026-03-18] established that stop caches cause false PASS results when files change between sessions. MLInterviewPrep already fixed this.

Action: Update template/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove cache import and usage. The template is the reference baseline, so it should have the best-known version of all hooks.

Source: MLInterviewPrep/.claude/hooks/test_check.py.

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

#### T-P2-255: [DEBT] helixos: Remove deprecated stop cache usage from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: test_check.py imports check_stop_cache and write_stop_cache from hook_utils and uses them to skip re-running tests in the same session. These deprecated caching functions were removed from the hook architecture (LESSONS.md lesson [2026-03-18]: removed lint cache so every Stop hook runs fresh). The caching logic means test failures can be silently skipped if tests passed earlier in the same session. Fix: Remove the cache check/write calls from test_check.py so tests always run fresh on Stop. Keep check_stop_cache/write_stop_cache in hook_utils.py only if other hooks still use them.

#### T-P2-320: [SYNC] helixos: Remove deprecated stop-cache from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos test_check.py still uses check_stop_cache/write_stop_cache which were deprecated per LESSONS.md 2026-03-18. Cache can produce false passes when files change between cache write and next session. MLInterviewPrep already removed this. Action: Remove cache imports and calls from test_check.py; clean up hook_utils.py if no other callers.

## Completed Tasks

> 494 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-19** -- T-P2-536: T-GOOG-REORG-PREFIX: Add [R1/Bucket] prefix to 14 Tier-3 doc titles for visual grouping on /prep. ## Context
- [x] **2026-04-19** -- T-P2-533: T-GOOG-CN-DRILL-BATCH: Batch-upgrade 11 Google drill docs + id=72 Bridge to ≥50% CN prose (from 30-47%). ## Context
- [x] **2026-04-19** -- T-P2-521: [DEBT] MLInterviewPrep: Customize CLAUDE.md.local with project overview and tech stack. CLAUDE.md.local still has template placeholder text (generated from claude-code-project-template). Specific gaps:
- [x] **2026-04-19** -- T-P2-517: KG-UX-18: Drawer rendering polish (GFM, rehype-raw, blockquote + callout styling). ## Context
- [x] **2026-04-19** -- T-P1-535: T-GOOG-REORG-SLIM51: Slim id=51 by replacing Round 1 ML-dims + Round 2 G&L-attrs with db://38 refs (~6213→~4500 chars). ## Context
- [x] **2026-04-19** -- T-P1-534: T-GOOG-REORG-HUB: Rewrite id=53 Prep Hub to pure 3-tier navigation index (~3558→~700 chars). ## Context
- [x] **2026-04-19** -- T-P1-532: T-GOOG-CN-57: Rewrite company_documents id=57 'Staging 13 Flashcards' to Chinese-prose narration (12K chars, 0%→≥60% CN). ## Context
- [x] **2026-04-19** -- T-P1-531: T-GOOG-CN-52: Rewrite company_documents id=52 'Google DNN / Key Papers Gist' to Chinese-prose narration (9.5K chars, 0%→≥60% CN). ## Context
- [x] **2026-04-19** -- T-P1-530: T-GOOG-DEDUPE: Dedupe Google prep docs id=38/51/53 schedule overlap + refresh dates to 4/20 mock + 4/21 R1 (NO archive, NO delete). ## Context
- [x] **2026-04-19** -- T-P1-529: T-MLSD-WORKED-95-V2: Rewrite id=95 Fraud & Trust Safety under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-528: T-MLSD-WORKED-94-V2: Rewrite id=94 Computer Vision Systems under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-527: T-MLSD-WORKED-93-V2: Rewrite id=93 NLP & LLM Systems under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P0-539: [T-MLF-03] T1 content fill Cat 1-2 (7 Q: Classical ML & Losses + Eval/Data). Write description markdown for 7 leaves:
- [x] **2026-04-19** -- T-P0-538: [T-MLF-02] seed_ml_fundamentals_skeleton.py: root + 6 category + 27 leaf stubs. Create scripts/seed_ml_fundamentals_skeleton.py (idempotent, Python 3.11+, encoding=utf-8).
- [x] **2026-04-19** -- T-P0-537: [T-MLF-01] Parse attachment -> ml_fundamentals_inventory.yaml (27 Q, tier + interview_freq columns). Parse the 85KB 'ML high-freq' attachment at C:/Users/Shenghui Xu/.claude/channels/discord/inbox/1776657806963-1495635943
