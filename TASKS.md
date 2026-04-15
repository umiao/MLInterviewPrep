# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-424: [Slack-SFDC] HR call Wed 2026-04-15 14:00 EST = 11:00 PT
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Slack (Salesforce) ML team recruiter call. 时间: 04/15 Wed 14:00 EST = 13:00 CST = 11:00 PT. 30-45 min 预期. 准备: (1) 自我介绍 90s; (2) 为什么对 Slack ML 感兴趣 (协作场景 ranking/search/summarization); (3) current role + 主线故事 (Pinterest Etsy); (4) timeline + comp expectation; (5) 3 个提问准备 (team structure / ML problem 类型 / interview loop). Calendar 加入, Zoom 链接待收.

#### T-P0-429: [Google/R2] G&L top-20 common questions × bq_improved_stories 映射 audit (HR 建议)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: HR source: 'you can anticipate 90%... top 20 questions, 3 answers for each, detailed and data-driven'. AC: (1) 列出 top 20 (tell me about time / disagreed / failed / ambiguity / difficult stakeholder / pushback manager / hardest decision / went above beyond / mentored / lead without authority / handled feedback / conflict / deadline pressure / learned new skill / ethical choice / mistake / proudest / user-first over metric / ambiguous priority / feedback given to peer); (2) 每题至少 1 条 bq_improved_stories 故事可用; (3) 识别覆盖空洞(哪几题没故事映射到); (4) EX-02/08/17 已 polished 够用; (5) 输出 gap list 到 bq_todo_tracker.md.

#### T-P0-433: [Google R2] G&L top-20 common questions × 6 polished stories 映射 audit
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: HR 明建议: top 20 questions × 3 answers each. Deliverable: update docs/bq_todo_tracker.md + append section to company_documents (company_id=3). AC: (1) 列 20 common BQ (disagreed/failed/ambiguity/stakeholder/pushback/hardest decision/above beyond/mentor/lead w/o authority/feedback/conflict/deadline/learn skill/ethical/mistake/proud/user-first/ambiguous priority/peer feedback/cross-team); (2) 每题标注 bq_improved_stories 里 1-3 条可用 story (EX-01..EX-17); (3) 识别覆盖空洞; (4) EX-02/08/17 已 polished 够用不再改.

#### T-P0-435: [LC] K-largest heap/quickselect 家族 drill: 703 + 973 + 378
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: 三题都未完成, 用户点名 K-largest/sketch 方向必须 drill. AC 三题各自: (A) LC 703 Kth Largest in Stream — min-heap size k 核心模板, add() O(log k); (B) LC 973 K Closest Points — max-heap 或 quickselect 双解, 复杂度对比; (C) LC 378 Kth Smallest in Sorted Matrix — binary search on value + count≤mid (和你做过的 LC 410 同家族, 迁移). 三题都写 problems.notes 中文 + set is_completed=1. 另外写一段对比: heap O(n log k) vs quickselect 平均 O(n) 最坏 O(n²) vs bucket sort O(n).

#### T-P0-436: [LC/Pinterest] Sketch/Streaming 理论 1-pager (company_id=29)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: 用户明确说 K-largest 要结合 sketch 做法. Deliverable: docs/pinterest_sketch_streaming_1pager.md, ingest company_documents (company_id=29 Pinterest, doc_kind=prep_note). 不要求会手写 sketch 代码, 要求知道方法 + 场景. AC 四条各 3-4 行: (1) Count-Min Sketch: 多哈希取 min, overestimate-only, 适合 top-K heavy hitter; (2) Space-Saving (Misra-Gries): O(1/ε) 空间估 heavy hitter, 比 CMS 空间省; (3) Reservoir Sampling (LC 382/398): 流中等概率抽 k, Pinterest 广告采样; (4) HyperLogLog: 估 cardinality 不是 top-K 但大数据背景常问. 末尾: 一句话桥 — 面试官问 Pinterest 实时 top-K trending pins 时的答题套路 (full heap 不扩展 → CMS 估 freq + min-heap 维 top-K).

### P1 -- Should Have (agentic intelligence)

#### T-P0-415: [Google/R1] LambdaRank/LambdaMART 推导 + pointwise/pairwise/listwise 对比自测
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap vs staging 13: staging 无 ranking loss 推导. Round1 必考. AC: (1) 默写 RankNet pairwise sigmoid loss; (2) LambdaRank 如何用 deltaNDCG 加权 pairwise gradient; (3) pointwise BCE/pairwise/ListNet softmax 何时用; (4) 挂钩 Sale NDCG → GMB 故事. Ref: doordash_ml_domain_ranking.md section 4.

#### T-P0-416: [Google/R1] NDCG/MAP/MRR 定义 + position bias 拷打自测
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: staging 只讲 ROC/PR. AC: (1) 默写 DCG=Σ(2^rel-1)/log2(i+1), NDCG=DCG/IDCG; (2) 为什么 MAP 不适合 graded relevance; (3) position bias 污染 offline NDCG (examination hypothesis); (4) 数值例子对比 MAP vs NDCG.

#### T-P0-417: [Google/R1] Calibration 三法 (Platt/Isotonic/Temperature) + GMB bidding 校准陷阱
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: staging 没提. Round1 recruiter 明列. AC: (1) Platt=logistic over logit; (2) Isotonic preserve ranking 粒度粗; (3) Temperature 只调 T 不改 argmax; (4) reliability diagram/ECE; (5) 为什么 GMB bidding 需 calibrated 概率 (miscalib → 系统性 over/under-bid).

#### T-P0-418: [Google/R1] IPS/counterfactual eval/去偏 NDCG (SIGIR paper talking points)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Gap: staging 无. SIGIR paper 必问. AC: (1) IPS 重加权 1/P(shown); (2) examination hypothesis P(click)=P(exam)·P(rel); (3) SNIPS self-normalize (bias/variance tradeoff); (4) 一句话讲自己 contribution + 一句话最大 limitation; (5) 'propensity estimation 怎么来的'.

#### T-P0-419: [Google/R1] Two-tower retrieval 深挖 (超越 InfoNCE 基础)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: staging 11 覆盖 InfoNCE 但缺系统级. AC: (1) 为什么两塔 (query 塔不看 doc 侧 → offline index); (2) negative sampling 四种 + failure mode; (3) HNSW vs IVF-PQ recall/latency tradeoff; (4) offline recall@K vs online NDCG 断裂 = training-serving skew. Ref: doordash_retrieval.md section 2.

#### T-P0-420: [Google/R1] Multi-objective ranking: DPP/MMR + Etsy diversity 故事机制
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Etsy diversity 必被追问机制. AC: (1) MMR = λ·rel-(1-λ)·max_sim; (2) DPP 用 det(L_S) 同时 model rel(对角) + diversity(非对角); (3) intent collapse → allocation primitive 平台化 = module arbitration; (4) 和 uncertainty weighting/GradNorm/Pareto 正交. Ref: doordash_ranking §5.

### P2 -- Nice to Have

#### T-P1-421: [Google/R1] A/B test 严谨性: sample size/SRM/CUPED/novelty
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: pillar7 有基础但缺 drill. AC: (1) n=(z+z)^2·2σ²/Δ²; (2) SRM 是 randomization 健康性不是结果; (3) CUPED 用 pre-period covariate 降 variance; (4) novelty 早期正偏/primacy 负偏 1 周洗期; (5) Etsy GMB 碰过哪个 trap.

#### T-P1-422: [Google/R1] Feature drift 监控: PSI/KL/JS 区别 + alert threshold
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: AC: (1) PSI=Σ(a-e)·ln(a/e), 0.1 warn/0.25 critical; (2) KL 不对称无界, JS 对称 bounded; (3) 连续用 KS; (4) concept drift P(y|x) vs covariate shift P(x); (5) 分 feature/分段 alert.

#### T-P1-423: [Google/R1] Train-serve skew/leakage/时序 split 拷打
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: AC: (1) target encoding K-fold leakage + fold-out 修正; (2) 为什么 ranking 必须 time-based split; (3) feature store parity 三种 skew (时间戳/null 语义/填充); (4) label leakage: future-only aggregates; (5) 一个真实踩坑.

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

> 382 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-14** -- T-P0-434: [LC] 攻下 85 Maximal Rectangle + 写中文笔记. LC 85 未完成, 用户明确点名考核重点. AC: (1) solve 一次不 peek; (2) 核心解法 = 每行转 histogram, heights[j]+=1 若'1' else 0, 跑 LC 84 单调栈; (3) 时间 
- [x] **2026-04-14** -- T-P0-432: [Google R1] Staging 13 题 2-min 口头答复本 (company_id=3). 把 staging/04_14_ML问题深入拷打.md 13 题压缩成问答卡. Deliverable: docs/google_staging_13_flashcards.md, ingest company_documents (com
- [x] **2026-04-14** -- T-P0-431: [Google R1] Bias/Variance + 过拟合诊断 drill note (company_id=3). 用户点名必须操练到位. Deliverable: docs/google_bias_variance_drill.md, ingest company_documents (company_id=3). AC: (1) 默写 E_D[(y-
- [x] **2026-04-14** -- T-P0-430: [Google R1] Regularization 全景合并深挖 note (company_id=3). Gap: staging 零散提了 L2/dropout/AdamW, 但用户明确点名要合并深挖. Deliverable: docs/google_regularization_deep_dive.md, ingest as compan
- [x] **2026-04-14** -- T-P0-414: Fix 4 failing CI checks (test/lint/emoji/migration). Migration _add_column_if_missing skipped; 3 ruff errors fixed; 17 emoji replaced with ASCII tags; 32 migration tests now
- [x] **2026-04-13** -- T-P2-413: [Pinterest/integration] Enrich Pinterest index doc with new sections. Final integration after all new LC/custom/SD content lands. Refresh company_documents id=47 to include: (1) new LC secti
- [x] **2026-04-13** -- T-P2-396: [Pinterest/LC] Investigate + notes: 寻找餐馆区间. Pinterest dump 2025-11 mentions this with no LC number. Research to identify the actual LC mapping (candidates: LC 1779 
- [x] **2026-04-13** -- T-P1-412: [Pinterest/BQ] Map Pinterest BQ questions to existing stories. Pinterest BQ (2025-11): (1) project led end-to-end, (2) where requirement came from, (3) stepping ahead when not respons
- [x] **2026-04-13** -- T-P1-411: [Pinterest/SD] ML SD: Personalized Chat Bot Recommending Pins. Pinterest SD 2025-11. (1) conversation understanding (LLM multi-turn state), (2) intent classification (ask-pins vs chit
- [x] **2026-04-13** -- T-P1-409: [Pinterest/SD] SD: User & Item Embeddings. Pinterest SD 2025-11. (1) objective (self-supervised contrastive / supervised from engagement), (2) encoder (towers, use
- [x] **2026-04-13** -- T-P1-408: [Pinterest/SD] SD: Ad CTR prediction. Pinterest SD 2025-11. (1) data pipeline (impressions/clicks with attribution), (2) feature engineering (user/ad/context 
- [x] **2026-04-13** -- T-P1-404: [Pinterest/custom] LC 332 loop follow-up addendum. Pinterest coding 2025-11 follow-up to LC 332: what if tickets form a cycle? Explain Hierholzer already handles Eulerian 
