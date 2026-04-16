# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-453: [Pinterest-CV] CNN foundation 1-pager: conv mechanics + ResNet/VGG/EfficientNet + transfer learning + data aug
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Gap: Pinterest is visual-content-first, but CV framework_nodes 122/123 are shallow (5733b+6231b). (1) Conv op: stride/pad/dilation, receptive field growth, parameter sharing. (2) Pool: max vs avg, global avg pool replacing FC. (3) Architectures one-liner each: VGG (deep stacked 3x3), ResNet (skip connections enable deep training), EfficientNet (compound scaling depth/width/resolution). (4) Transfer learning: head-only vs full fine-tune, when to freeze backbone, BN quirks when fine-tuning. (5) Augmentation catalog: geom/color/mixup/cutout/cutmix + text-image pair aug for multimodal. AC: (a) seed Pinterest company_document (company_id=29, doc_kind=prep_note) titled 'CNN Foundation for Visual Search'. (b) Expand framework_node id=122 (Image Classification) description to include Pinterest-specific angle. <=2500 words. Pyramid mid -- don't go into NAS / vision transformer internals (separate task). Depends on: none.

#### T-P1-454: [Pinterest-NLP] Word2Vec/GloVe history + ViT + cross-modal attention supplement
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: pre-transformer embedding history missing entirely; node 164 (Vision-Language Models) covers CLIP/LLaVA shallowly but no ViT detail or cross-modal attention contrast. (1) Word2Vec (CBOW, skip-gram, negative sampling) + GloVe (co-occurrence matrix) as HISTORY -- why moved past: context-free embeddings. (2) ViT: patch embedding, [CLS] token, positional embedding, why scales beyond CNN. (3) Cross-modal attention: CLIP's dual-encoder contrastive alignment vs self-attention (in-modality); mention BLIP-2's Q-Former as fusion step. AC: expand framework_node id=164 description + add brief predecessor context in node 148 (BERT Family) description. Optional docs/nlp_pretransformer_to_vit_bridge.md if content exceeds. <=2000 words. Pyramid mid. Depends on: none.

#### T-P1-455: [Pinterest-RecSys] Cold-start strategies: user + item + pin bootstrap
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: cold-start absent from pillar4.recommender_systems nodes (108/109/110 cover CF/content-based/deep but not cold-start). Strategies: (1) Content-based first-shot (Pinterest Pin = image+text, can embed immediately). (2) Cross-domain transfer (demographics, geo, device). (3) Meta-learning (MAML for fast adaptation). (4) Contextual bandits for explore/exploit. (5) Popular/trending baseline fallback. Pinterest-specific: fresh-pin surge from new boards, creator side cold-start. AC: (a) create new depth-2 framework_node 'Cold Start' under pillar4.recommender_systems (path pillar4.recommender_systems.cold_start). Description >=3500b. (b) Seed Pinterest company_document. <=2000 words. Pyramid mid. Depends on: none.

#### T-P1-456: [ML-RecSys] Matrix factorization: SGD vs ALS + bridge from CF to embedding models
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: node 108 (Collaborative Filtering) covers CF concept but not the MF mechanics bridging CF -> Two-Tower. (1) Bias-only -> Funk-SVD (PMF) -> biased-MF (user bias + item bias + inner product). (2) Training: SGD (mini-batch, noisy, online-friendly) vs ALS (closed-form per block, parallelizable, offline). (3) Conceptual bridge: MF is the ancestor of Two-Tower -- user_emb * item_emb dot product but with learned towers instead of fixed lookup. AC: expand framework_node id=108 description AND optional docs/mf_to_two_tower_bridge.md. LINK to Google Two-Tower doc 64 -- do NOT re-derive InfoNCE or sampled-softmax (covered there). <=1500 words. Pyramid mid. Depends on: none.

#### T-P1-457: [Phase 0.5b] Template v1.1 post-Sketch revision: drawer tab render order + Optimization granularity example
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-452
- **Description**: DEFERRED revision of Phase 0.5 content template after T-P0-241 Sketch sample ships real-world signal. Per independent reviewer: (🟡 3) add Optimization (SGD/Adam/二阶) worked example to §2.3 granularity decision table + append horizontal/vertical heuristic boundary: 'when a horizontal topic's interview depth requirement exceeds one node's §3 budget (~3000b always-visible), still split'. (🟡 4) declare canonical drawer tab render order:  -- rationale: progressive disclosure by depth of follow-up, interview_deep being the natural extension of §3.4, derivation/history placed deepest/most-background. May also revise based on Sketch author-experience signals. Deliverable: template doc updated in place to v1.1. Depends on T-P0-241 (need real Sketch sample to validate/reject these assumptions).

### P2 -- Nice to Have

#### T-P2-458: [Pinterest-Gen] GAN / VAE / Diffusion contrast one-pager + Pinterest use cases
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: no generative-model contrast at pitch level. Pinterest angle (visual content): pin generation, style transfer for boards, visual-search result augmentation. KE-JI (restrained): pitch-only. AC: (a) seed one Pinterest company_document 'Generative Models Pitch for Pinterest' with single comparison table {GAN: adversarial/mode-collapse-risk/fast-inference; VAE: latent-space/blurry-output/fast; Diffusion: SOTA-quality/slow-but-DDIM-fixes}. (b) One paragraph per Pinterest use case. (c) DO NOT re-derive VAE ELBO or DDPM forward/reverse sampling -- cite papers instead. (d) NO new framework_node (avoid tree bloat at P2). <=1500 words. Pyramid top -- restrained. Depends on: none.

#### T-P2-459: [Pinterest-SD] Multimodal unsafe content detection + query expansion recall boost
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: Gap: two known Pinterest SD interview prompts -- neither has a dedicated doc. (1) Unsafe content (image+text multimodal): early fusion vs late fusion trade-off, modality dropout during training, asymmetric confidence thresholds (ship only SFW-confident content), human-in-loop rules. (2) Query expansion for recall boost WITHOUT changing ranking algo: SynSet lookup, query rewriting via small LLM, embedding-based query-to-query similarity, click-driven expansion. AC: seed ONE combined Pinterest company_document 'Pinterest SD Gap-Fill: Unsafe Multimodal + Query Expansion'. <=3000 words. Pyramid top -- restrained, design-level pitch not code. Link to Pinterest sketch doc 58 for ANN/recall context. Depends on: none.

#### T-P2-460: [Pinterest-SD] Responsible AI / Inclusive AI + model monitoring & retraining playbook
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: Pinterest brands on 'Inclusive AI' (skin-tone-fair visual search case study) but no prep doc covers it. Bundle with model monitoring. (1) Bias detection: group metrics on protected attributes, equal-opportunity / demographic-parity basics. (2) Fair-aware constrained ranking (post-hoc re-rank). (3) Drift: PSI, KS, performance drift thresholds. (4) Retraining cadence: scheduled vs trigger-based. AC: seed Pinterest company_document 'Responsible AI + Monitoring Playbook'. <=2000 words. Pyramid top -- restrained. Depends on: none.

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

> 414 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P2-438: [DEBT] MLInterviewPrep: httpx duplicated in pyproject.toml main + dev groups. pyproject.toml lists httpx==0.27.2 in both [project].dependencies (main) and [project.optional-dependencies].dev. This i
- [x] **2026-04-16** -- T-P2-437: [SYNC] Propagate 4 new MLInterviewPrep lessons to helixos LESSONS.md. 4 lessons from MLInterviewPrep (2026-04-10 to 2026-04-15) not yet in helixos LESSONS.md. All apply to helixos. (1) 2026-
- [x] **2026-04-16** -- T-P1-423: [Google/R1] Train-serve skew/leakage/时序 split 拷打. AC: (1) target encoding K-fold leakage + fold-out 修正; (2) 为什么 ranking 必须 time-based split; (3) feature store parity 三种 s
- [x] **2026-04-16** -- T-P1-422: [Google/R1] Feature drift 监控: PSI/KL/JS 区别 + alert threshold. AC: (1) PSI=Σ(a-e)·ln(a/e), 0.1 warn/0.25 critical; (2) KL 不对称无界, JS 对称 bounded; (3) 连续用 KS; (4) concept drift P(y|x) vs
- [x] **2026-04-16** -- T-P0-452: [Meta-Cleanup] Sketch family unification: 3-axis view + terminology grounding across sketch docs. User-flagged: compact-DS content (CMS/HLL/SS/Bloom) duplicated across framework_nodes 196/197/103 + Pinterest doc 58, ea
- [x] **2026-04-16** -- T-P0-451: [DL-Fund] DL training pitfalls 1-pager: Focal loss + BatchNorm/LayerNorm + vanishing/exploding gradients. Gap: three scattered pitfall topics consolidated. (1) Focal loss: alpha/gamma, class imbalance, when NOT to use (already
- [x] **2026-04-16** -- T-P0-450: [DL-Fund] Optimizer family: SGD -> Momentum -> AdaGrad -> RMSProp -> Adam derivation chain. Gap: node 74 Gradient Descent Family is stub (141b). Existing study note source: data/t8_optimizers.md (port into DB). C
- [x] **2026-04-16** -- T-P0-449: [DL-Fund] Activation functions unified: ReLU/LeakyReLU/Sigmoid/Tanh/Softmax when and why. Gap: no standalone activation-functions node. Single comparison table: {activation, range, derivative, vanishing-grad ri
- [x] **2026-04-16** -- T-P0-448: [ML-Fund] Classical model pitches: KNN / Naive Bayes / K-Means / DBSCAN when-to-use. Gap: node 71 Clustering stub + no NB/KNN nodes. Pitch-format 1-pager: per model -> (what / assumption / when use / when 
