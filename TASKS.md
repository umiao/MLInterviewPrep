# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-445: [ML-Fund] Cost-sensitive model selection: FP/FN decision rubric + Pinterest/Google examples
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: when two models have near-equal accuracy/AUC, how to choose. Steps: (1) quantify FP vs FN business cost; (2) pick operating point on PR curve along cost-weighted axis; (3) threshold recalibration; (4) class-weighted CE / cost-sensitive loss. AC: (a) expand framework_node id=17 (Model Selection & Validation) description from 0b -> >=3000b with decision rubric + worked example. (b) Seed one hub doc at docs/ml_cost_sensitive_selection.md with Pinterest unsafe-content (high FN cost) + Google Ads (high FP cost) concrete cases. (c) LINK to existing Google doc 62 (Calibration drill) -- do NOT duplicate Platt/Isotonic/Temperature math, only reference. Target <=2500 words. Pyramid base -- no fancy expansion. Depends on: none.

#### T-P0-446: [ML-Fund] Logistic regression coefficient interpretation: odds ratio for categorical + boolean variables
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: typical Google/LinkedIn screen: 'LR coef 0.7 on one-hot vs reference -- what does it mean?'. Cover: (a) continuous feature one-unit change -> exp(beta); (b) categorical with k levels (one-hot, reference level, exp(beta_k) vs reference baseline); (c) boolean variable exp(beta). Include 3-example decision script. AC: expand framework_node id=64 (Linear Models) description from 145b -> >=3000b. NO new doc -- node description is enough. Do NOT duplicate content from Google DNN gist (doc 52). Pyramid base. Depends on: none.

#### T-P0-447: [ML-Fund] Bagging vs Boosting decision rubric + XGBoost/LightGBM mechanics
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Gap: (1) when bagging (high variance, stable base learner) vs boosting (high bias, weak learner). (2) XGBoost core: 2nd-order Taylor, L1/L2 reg term, sparse-aware split, histogram approx. (3) LightGBM: leaf-wise growth, GOSS, EFB, native categorical. (4) XGB vs LGB latency/memory at scale. Google/Pinterest screen: 'why LGB beats XGB on wide datasets'. AC: (a) populate framework_node id=65 (Tree Models) description 124b -> >=4000b. (b) Seed one-pager docs/bagging_boosting_xgb_lgb_1pager.md. LINK to Google LambdaMART doc 60 -- do not re-derive gradient boosting basics covered there. <=3000 words. Pyramid base -- don't go deep on optimizer-specific hyperparameters, stay at decision-rubric level. Depends on: none.

#### T-P0-448: [ML-Fund] Classical model pitches: KNN / Naive Bayes / K-Means / DBSCAN when-to-use
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: node 71 Clustering stub + no NB/KNN nodes. Pitch-format 1-pager: per model -> (what / assumption / when use / when avoid / complexity / Pinterest or Google angle). Pitch-level ONLY -- do NOT re-derive Bayes theorem or k-means convergence proof. Topics: KNN (lazy, curse of dim, needs normalization), NB (feature independence, text baseline), K-Means (centroid, K choice via elbow/silhouette, sensitive to init), DBSCAN (density, eps/minPts tuning, non-convex clusters). AC: (a) expand framework_node id=71 (Clustering) desc 115b -> >=2500b. (b) Seed docs/classical_model_pitches.md. (c) Reference data/t4_knn_kmeans.md and data/t5_naive_bayes.md if present -- do NOT duplicate their derivations, link only. <=2000 words. Depends on: none.

#### T-P0-449: [DL-Fund] Activation functions unified: ReLU/LeakyReLU/Sigmoid/Tanh/Softmax when and why
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: no standalone activation-functions node. Single comparison table: {activation, range, derivative, vanishing-grad risk, compute cost, typical use}. Why ReLU default for vision (cheap, non-saturating on positives, induces sparsity). Why sigmoid at binary output. Softmax for multi-class + temperature tricks (distillation/sampling). Leaky/PReLU as dying-ReLU fix. AC: expand framework_node id=77 (Training Tricks) description 135b -> >=3000b including the table + 3 when-to-pick examples. NO new doc. Pyramid base -- pitch-level, no deep math on smoothness theory. Depends on: none.

#### T-P0-450: [DL-Fund] Optimizer family: SGD -> Momentum -> AdaGrad -> RMSProp -> Adam derivation chain
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Gap: node 74 Gradient Descent Family is stub (141b). Existing study note source: data/t8_optimizers.md (port into DB). Cover update rules with math: SGD (high variance), Momentum (velocity smoothing), AdaGrad (per-param LR decay -> freezes late), RMSProp (decaying avg fixes freeze), Adam (Momentum + RMSProp + bias correction). When NOT Adam: vision/generalization often favors SGD+Momentum + cosine schedule. AC: (a) port content from data/t8_optimizers.md; (b) expand framework_node id=74 description 141b -> >=5000b. (c) Optional docs/optimizer_family.md only if node size overflows. Pyramid base. Do NOT expand to LARS/LAMB/Lion (fancy -- skip). Depends on: none.

#### T-P0-451: [DL-Fund] DL training pitfalls 1-pager: Focal loss + BatchNorm/LayerNorm + vanishing/exploding gradients
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-449
- **Description**: Gap: three scattered pitfall topics consolidated. (1) Focal loss: alpha/gamma, class imbalance, when NOT to use (already balanced data). (2) BatchNorm: train vs eval mode common trap, internal-covariate-shift motivation (now disputed), why LayerNorm is used for sequences/transformers. (3) Vanishing/exploding grads: sigmoid/tanh stacks, residual connections fix, gradient clipping, Xavier (tanh) vs He (ReLU) init. AC: (a) seed docs/dl_training_pitfalls_1pager.md. (b) Expand framework_node id=77 (Training Tricks) description (AFTER Gap-5 activation-functions task, same node) by adding a second section. <=3500 words. Pyramid base. Depends on: T-P0-<gap5>.

#### T-P0-452: [Meta-Cleanup] Sketch family unification: 3-axis view + terminology grounding across sketch docs
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: User-flagged: compact-DS content (CMS/HLL/SS/Bloom) duplicated across framework_nodes 196/197/103 + Pinterest doc 58, each treating primitives as independent solutions -> redundant text + term drift (HLL-family vs HLL-instance).

GOAL: adopt user's 3-axis unified framework as the canonical lens. Primitives become specific axis-combinations, not separate topics. Eliminate duplicate math/formulas across docs.

AUDIT TARGETS (read-only verified):
- framework_node 196 (pillar1.streaming_topk, 7924b) -- PRIMARY CANONICAL
- framework_node 197 (pillar1.scaling_resource_model, 8845b) -- references 196
- framework_node 103 (pillar3.building_blocks.realtime_features, 5216b) -- tangential
- company_document 58 (Pinterest Sketch/Streaming 1-Pager, 3817b)
- LinkedIn docs 21/22 (huge合集) -- scan for any CMS/HLL section, add pointer if found

THREE ORTHOGONAL AXES (adopt as canonical vocabulary everywhere):
1. Hash source: flow label (canonical) / Bernoulli per-arrival / other dimension (timestamp, payload feature)
2. Counter/register structure: scalar counter (CMS) / log counter (Morris) / bitmap register (PCSA, HLL variants)
3. Aggregation operator: idempotent max (-> cardinality) / accumulative sum-or-set-bit (-> frequency)

KEY TECHNICAL CONCEPTS to add to node 196 (currently missing):
- CMM (Count-Mean-Min) > plain CM: f_hat(x) = (w*bucket - N)/(w-1); use MEDIAN across rows (not min post-correction). Light-flow relative-error improvement vs CMS.
- Bernoulli frequency sketch: each arrival independently passes Bernoulli(p); survivors enter bucket. Error ~ sqrt(f(x))/p. Complements CMS's eps*||a||_1 -- heavy-flow-friendly where CMS relative error explodes for light flows.
- Bitmap register generalization (beyond HLL max): each register stores bit vector, read statistics from patterns (longest-run, bit occupancy). Higher info utilization than HLL max-only, walks back toward PCSA route. Saturation handled by large m + saturation-aware estimator.
- Unified 'test once' view: cardinality = per-flow-label test (max idempotent dedupes reruns); frequency = per-arrival test (accumulates). Same underlying structure, switch trigger semantics.

SYSTEM DESIGN section (production pattern, goes into node 196 + Pinterest 58):
- Layered architecture: cold filter (admission control) eats Zipf long-tail one-hit wonders; main sketch only sees 'promising' flows. Typical: 1/8 sampling + k-position-full-pass.
- Two-layer bucketing: outer = flow -> m registers (cross-array collision suppression); inner = per-arrival -> register-bit (bit occupancy as freq proxy). Two orthogonal noise sources, tune independently.
- Epoch-based reset + warm-up: sub-second reset prevents drift; previous epoch warms cold filter so true cold-start happens only once. Implicit assumption: heavy-hitter temporal locality (holds for network traffic).

TERMINOLOGY GROUNDING (must appear up front in every touched doc):
- 'HLL' in network-measurement community = family (hash + geometric/Bernoulli sampling + m-way bucketing)
- 'HLL' in DB/general systems community strictly = Flajolet 2007 cardinality estimator (max-aggregation instance)
- Cross-community discussion must first declare family vs instance to avoid looking unsound.

ONE-LINER (canonical doc closing): 'Textbook teaches primitives; production teaches composition. 3-axis lens (hash source / counter structure / aggregation operator) + layered system design is the core frame for translating textbook sketches to engineering solutions.'

ACCEPTANCE CRITERIA:
1. framework_node 196 rewritten around 3-axis framework: primitives positioned as specific axis combos. CMM + Bernoulli-freq + bitmap-register + 'test once' view + system-design section all added. Terminology grounding in Key Terms. Length 10000-14000b (from 7924b -- conservative expansion, no fluff).
2. framework_node 197: CMS/HLL mention reduced to 2-line definition + explicit pointer to 196. Duplicate formulas removed.
3. framework_node 103: Key Terms CMS/HLL lines reduced to 1-line + pointer to 196. No duplicate math.
4. company_document 58 rewritten as Pinterest-specific COMPOSITION 1-pager atop the canonical: primitives pointed to 196; focuses on Pinterest-specific combos (e.g. trending pins via axis-combo X; abuse detection via combo Y). Length 4000-6000b.
5. Every 'HLL' mention across the 4 touched artifacts labels family-vs-instance on first use.
6. Deliverable: one idempotent seed script scripts/consolidate_sketch_family_20260416.py that upserts all 4 artifacts; safe to re-run. No new stray seed scripts.
7. Sanity: after running, grep for CMS/HLL math formulas -- should appear ONCE (in node 196), not duplicated across 103/197/58.

EXPLICIT NON-GOALS:
- Do NOT introduce new primitives (Bloom variants, t-digest, quantile sketches). Keep scope to frequency + cardinality.
- Do NOT expand to distributed-merge mechanics at length (covered elsewhere or out of scope).
- Do NOT touch node 151 (pretraining) or 143 (position encoding) even though they grep-matched 'sketch' (false positives).
- Do NOT modify LinkedIn合集 docs unless they genuinely have duplicate sketch math (a pointer is enough if they have only passing mention).

Confidence gate verification:
- Context sufficiency: YES -- 4 exact doc IDs + char targets + axis taxonomy from user
- Cross-company reuse: YES -- node 196 is pillar1 (company-agnostic), Pinterest doc 58 uses 196 as base, Google/LinkedIn future prep gets unified terminology
- Duplication risk: NONE -- consolidation task by design; the 14 prior tasks (227-240) touch zero of {103, 196, 197, doc 58}

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

> 398 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P2-438: [DEBT] MLInterviewPrep: httpx duplicated in pyproject.toml main + dev groups. pyproject.toml lists httpx==0.27.2 in both [project].dependencies (main) and [project.optional-dependencies].dev. This i
- [x] **2026-04-16** -- T-P2-437: [SYNC] Propagate 4 new MLInterviewPrep lessons to helixos LESSONS.md. 4 lessons from MLInterviewPrep (2026-04-10 to 2026-04-15) not yet in helixos LESSONS.md. All apply to helixos. (1) 2026-
- [x] **2026-04-16** -- T-P1-423: [Google/R1] Train-serve skew/leakage/时序 split 拷打. AC: (1) target encoding K-fold leakage + fold-out 修正; (2) 为什么 ranking 必须 time-based split; (3) feature store parity 三种 s
- [x] **2026-04-16** -- T-P1-422: [Google/R1] Feature drift 监控: PSI/KL/JS 区别 + alert threshold. AC: (1) PSI=Σ(a-e)·ln(a/e), 0.1 warn/0.25 critical; (2) KL 不对称无界, JS 对称 bounded; (3) 连续用 KS; (4) concept drift P(y|x) vs
- [x] **2026-04-16** -- T-P1-421: [Google/R1] A/B test 严谨性: sample size/SRM/CUPED/novelty. pillar7 有基础但缺 drill. AC: (1) n=(z+z)^2·2σ²/Δ²; (2) SRM 是 randomization 健康性不是结果; (3) CUPED 用 pre-period covariate 降 varia
- [x] **2026-04-15** -- T-P1-444: Problems tab: Custom-mode company-grouped view. # Problems tab: Custom-mode company-grouped view (T-ML-xxx)
- [x] **2026-04-15** -- T-P1-443: Problems tab: Custom badge + source-type filter switch. # Problems tab: Custom badge + source-type filter (T-ML-xxx)
- [x] **2026-04-15** -- T-P1-442: Pinterest card index: integrate tab=index into PrepNotesPage. # Pinterest Card Index: Integrate tab=index into PrepNotesPage (T-P1-226)
- [x] **2026-04-15** -- T-P1-441: Pinterest card index: frontend CardGrid component. # Pinterest Card Index: Frontend CardGrid Component (T-P1-225)
- [x] **2026-04-15** -- T-P1-440: Pinterest card index: backend + data prep. # Pinterest Card Index: Backend + Data Prep (T-P1-224)
- [x] **2026-04-15** -- T-P0-424: [Slack-SFDC] HR call Wed 2026-04-15 14:00 EST = 11:00 PT. Slack (Salesforce) ML team recruiter call. 时间: 04/15 Wed 14:00 EST = 13:00 CST = 11:00 PT. 30-45 min 预期. 准备: (1) 自我介绍 90
- [x] **2026-04-15** -- T-P0-420: [Google/R1] Multi-objective ranking: DPP/MMR + Etsy diversity 故事机制. Etsy diversity 必被追问机制. AC: (1) MMR = λ·rel-(1-λ)·max_sim; (2) DPP 用 det(L_S) 同时 model rel(对角) + diversity(非对角); (3) inte
- [x] **2026-04-15** -- T-P0-419: [Google/R1] Two-tower retrieval 深挖 (超越 InfoNCE 基础). staging 11 覆盖 InfoNCE 但缺系统级. AC: (1) 为什么两塔 (query 塔不看 doc 侧 → offline index); (2) negative sampling 四种 + failure mode; (
- [x] **2026-04-15** -- T-P0-418: [Google/R1] IPS/counterfactual eval/去偏 NDCG (SIGIR paper talking points). Gap: staging 无. SIGIR paper 必问. AC: (1) IPS 重加权 1/P(shown); (2) examination hypothesis P(click)=P(exam)·P(rel); (3) SNIP
- [x] **2026-04-15** -- T-P0-417: [Google/R1] Calibration 三法 (Platt/Isotonic/Temperature) + GMB bidding 校准陷阱. Gap: staging 没提. Round1 recruiter 明列. AC: (1) Platt=logistic over logit; (2) Isotonic preserve ranking 粒度粗; (3) Temperat
- [x] **2026-04-15** -- T-P0-416: [Google/R1] NDCG/MAP/MRR 定义 + position bias 拷打自测. Gap: staging 只讲 ROC/PR. AC: (1) 默写 DCG=Σ(2^rel-1)/log2(i+1), NDCG=DCG/IDCG; (2) 为什么 MAP 不适合 graded relevance; (3) positi
- [x] **2026-04-15** -- T-P0-415: [Google/R1] LambdaRank/LambdaMART 推导 + pointwise/pairwise/listwise 对比自测. Gap vs staging 13: staging 无 ranking loss 推导. Round1 必考. AC: (1) 默写 RankNet pairwise sigmoid loss; (2) LambdaRank 如何用 de
