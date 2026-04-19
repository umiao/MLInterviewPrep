# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-512: T-MLSD-WORKED-92: Upgrade Marketplace & Logistics (id=92) to L5-bar gold standard
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-510, T-P1-511
- **Description**: ## Context
Depends on T-P0-510 (L5 framework + Appendix A Unified Template) + T-P1-511 (audit identifies this problem's specific gaps). id=92 Marketplace & Logistics is the closest mapping to the Uber ride-hailing dry run that produced the L5 framework. Upgrade it FIRST as the exemplar — every other classic-design problem's fill task will reference this as the gold standard.

## Input material
- id=18 Appendix A "Unified Template Skeleton" (the 11-section structure + quality gates)
- Uber dry run content from user's Discord doc (this is the DOMAIN-SPECIFIC source material that tailors the template to ride-hailing)
- Existing id=92 content (5400 chars, 8 headings: Overview / Core Concepts / Implementation / Interview Patterns / Comparisons / Key Takeaways / Advanced Topics) — contains surge-pricing math, ETA component decomposition, Hungarian algorithm formulation, key metrics table

## Rewrite plan — follow Appendix A EXACTLY, preserve all existing ML content

```
# Marketplace & Logistics (L5 Gold-Standard Design)
> 打车 / 外卖 / 双边物流平台 — Uber/DoorDash 风格

## Prerequisites
→ 参见 [id=18 System Design Framework](/kg?node=n18)
> 本题是"地理绑定 + 实时匹配 + 动态定价"系统的代表。建议先读 id=18 再回到本题。

## 1. Requirements Clarification (5m)
- Functional: 下单→匹配→追踪→支付 端到端
- Non-functional: 10K DAU 单城, 600 同时在线司机, 匹配 p95<30s, 位置 5s 一次, 强一致只在"司机派单"
- Out-of-scope: 拼车、路线规划、多车型
- [5 mandatory clarifying Qs table from id=18, instantiated for marketplace]

## 2. Capacity Estimation (5m)
- 600 driver × 5s⁻¹ = 120 writes/s → Redis 单机足够
- 峰值 500 concurrent geo queries → READ 是真正战场
- Storage: location 6KB/s, trip ~500 bytes/order × 10K/day ≈ 5MB/day
- 这些数字直接驱动："单机 Redis GEO"、"不做跨城 sharding v1"

## 3. High-Level Architecture (15m) — 5 services split by r/w + SLA
- Location Service (write-heavy + read-heavy, eventual, low SLA)
- Matching Service (read-heavy, write-light, low-latency + strong consistency on dispatch)
- Trip Service (low QPS, strong consistency, transactional state machine)
- Payment Service (ultra-low QPS, absolute consistency, external deps)
- Notification Service (high fanout, loss-tolerant)
- Numbered 8-step end-to-end data flow (client → gateway → trip.create → match.find+CAS → notify.push → accept → trip.active → location-relay)
- Storage selection table (driver-hot → Redis GEO; driver-history → Cassandra; trip → PostgreSQL; payment → PostgreSQL + audit; user → PostgreSQL + Redis)

## 4. Deep Dives (25m) — 3 topics
### 4a. Geo spatial index & proximity query
- Redis GEO (GEOADD / GEOSEARCH BYRADIUS) command examples
- 5-step analysis (essence: spatial prune → options: flat vs GeoHash vs S2 → pick: Redis GEO at single-city scale → scale-out: city sharding → S2 → edges: polar regions, date-line)

### 4b. Driver state machine + dispatch concurrency
- CAS SQL: UPDATE drivers SET status='pending_accept' WHERE driver_id=:id AND status='available'
- Redis alternative: SET driver:lock:{id} NX EX 15
- Why NOT ZooKeeper here (business lock vs coordination service — L5 signal)
- TTL prevents lock-hang
- State-machine diagram (available → pending_accept → on_trip → available)

### 4c. Dynamic pricing / ETA / dispatch optimization (PROMOTED from existing ML content)
- Keep existing surge pricing log-linear model formula
- Keep existing ETA component decomposition
- Keep existing Hungarian vs greedy vs batch tradeoff

## 5. Reliability & Monitoring (5m)
- 4-layer failure domain (machine / AZ / region / degradation)
- KEY L6 SIGNAL: "打车是地理绑定业务 — SF 挂了 NYC 兜底没意义" — 多 region 是为覆盖不是兜底
- Degradation table: payment-gw timeout → async pre-auth; matching overload → 拒单返回"附近暂无车"; location failure → 30s coarse geohash; map API down → 历史 ETA 均值
- SLOs: availability 99.9%, match p95<30s p99<2min, duplicate-dispatch rate<0.01%
- Supply/demand ratio dashboard (平台命根)

## 6. Summary & Tradeoffs (5m)
- 按 id=18 模板收尾：5 个核心决策 + 关键 tradeoff + 未讨论点 + 想继续深入的 topic

## Interview Q&A
[Keep existing, expand to 4-5 Qs if thin — cover: surge fairness, long-trip handling, driver earnings, cross-city]

## Self-Check (按 id=18 7-section pass-bar)
- [ ] Requirements Clarification ✅ (具体数字+强一致边界)
- [ ] Capacity Estimation ✅ (2 个数字直接驱动架构决策)
- [ ] ...
[list all 7 sections, each with checkmark + one-line justification]
```

## Deliverables
Idempotent seed script `scripts/seed_node_92_marketplace_l5_20260418.py`:
- DB backup + history row + UPDATE id=92
- Hash-check idempotent

## Acceptance Criteria
- [ ] id=92 description length 9000-11000 chars (from 5400)
- [ ] Description passes ALL Appendix A quality gates from id=18:
  - [ ] Length ≥ 8000 chars ✅
  - [ ] Section 2 has ≥ 2 specific numbers + architecture decision they drove
  - [ ] Section 3 has service table with SLA per service
  - [ ] Section 4 has ≥ 2 deep dives, each with pseudocode/SQL snippet
  - [ ] Section 5 has ≥ 3 concrete SLOs
  - [ ] Self-Check section has 7 checkmarks with one-line justifications each
- [ ] ALL existing ML content preserved (surge formula, ETA components, Hungarian) — relocated to Section 4c, NOT deleted
- [ ] Seed script idempotent (hash-match → no-op)
- [ ] `framework_nodes_description_history` captures the current 5400-char content before overwrite
- [ ] `npm run build` green
- [ ] Manual smoke: /kg?node=n92 renders cleanly; Prerequisites section shows working link to id=18 which itself renders the Appendix A template

#### T-P1-513: T-MLSD-WORKED-198: Upgrade Real-Time Rec System (id=198) with L5 skeleton
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-510, T-P1-511
- **Description**: ## Context
Depends on T-P0-510 (framework + Appendix A template) + T-P1-511 (audit). id=198 "Real-Time Recommendation System Design" already has the richest structure in Pillar 3 (13380 chars, 12 sections covering framing / baselines / two-tower / ranking / re-ranking / training / cold-start / monitoring / rollout / latency / serving / Q&A). It's the SECOND exemplar — demonstrates how the L5 template applies when a problem already has substantive domain content.

## Input material
- id=18 Appendix A Unified Template (the 11-section required structure + quality gates)
- Existing id=198 content (12 sections, 13380 chars) — preserve in full

## Rewrite plan — MAP existing sections to template sections, ADD the missing ones

### Mapping existing → template
| id=18 Appendix A template | id=198 existing section |
|---|---|
| 1. Requirements Clarification | Section 1 "Problem Framing & Clarify-First" ← already exists, good |
| 2. Capacity Estimation | **MISSING** — must add |
| 3. High-Level Architecture | Section 11 "Serving Architecture" ← exists but needs service-by-SLA breakdown + storage table added |
| 4. Deep Dives | Sections 2-10 (baselines, two-tower, ranking, cold start, exploration, monitoring, rollout, latency) ← already strong; relabel as Deep Dives 4a-4h |
| 5. Reliability & Monitoring | Section 8 "Monitoring & Drift Detection" ← exists; add SLO bar + business metrics |
| 6. Summary & Tradeoffs | **MISSING** — must add a consolidated tradeoff table |
| Interview Q&A | Section 12 ← exists |
| Self-Check | existing "Self-Check (面试前必过)" ← exists, good |

### Additions (in order to insert)

**A. Insert new Section "2b. Capacity Estimation" after existing Section 1**
- 100M DAU rec product
- Retrieval QPS: 100M × 2 sessions/day × 10 requests/session / 86400 = 23K QPS peak → ×3 peak = 70K QPS
- Ranking QPS: 70K × 500 candidates / 100 (batched) = 350K ranker invocations
- Storage: 500M items × 128d float32 = 256GB embeddings → must fit in memory sharded
- Bandwidth: 70K × 10KB response = 700MB/s aggregate
- Decision drivers: "256GB embeddings drives ANN-index sharding"; "350K ranker QPS drives GPU inference cluster sizing"

**B. Enhance Section 11 Serving Architecture with service-by-SLA table**
- Gateway (low latency, high availability)
- Retrieval Service (p99<20ms, stateless, horizontal)
- Ranking Service (p99<50ms, GPU, stateful batched)
- Feature Store Service (p99<10ms, Redis-backed)
- Embedding Index Service (p99<15ms, sharded ANN)
- Experiment/Flag Service (cacheable, low SLA)
- Logging/Event Bus (async, loss-tolerant)
- Add storage selection table (embeddings→FAISS/ScaNN; hot features→Redis; user profile→PostgreSQL+Redis; event log→Kafka→S3; experiments→Unleash/LaunchDarkly)

**C. Insert new Section "12b. L5 Tradeoff Table" before existing Self-Check**
At minimum 7 rows: retrieval (two-tower vs ANN-over-all) / ranking (XGBoost vs DNN vs MoE) / cold-start (popularity vs content-based vs MF fallback) / exploration (ε-greedy vs Thompson vs LinUCB) / serving (sync vs streaming) / feature freshness (online vs offline) / model rollout (shadow vs A/B vs bandits). Each row: pick + why + when-to-change.

**D. Extend Section 8 Monitoring with explicit SLO bar**
- Availability: 99.9% (43m/month budget)
- Retrieval: p99<30ms, success rate>99.95%
- E2E: p99<200ms (retrieval + ranking + rerank)
- CTR guardrail: rollout must not drop CTR >0.5%
- Embedding drift: KL(online_dist || offline_dist)<0.1 (alert)

**E. Prepend new Section "0. Time Budget" at the top**
Show 5/5/15/25/5/5 breakdown applied to rec system; map each existing section to which stage

**F. Add "6. Summary & Tradeoffs" as a NEW section between existing 11 and 12**
Consolidate from the L5 Tradeoff Table + call out un-discussed points (multimodal, long-tail fairness, privacy-preserving personalization)

## Deliverables
Idempotent seed script `scripts/seed_node_198_rec_l5_20260418.py`:
- DB backup + history row + UPDATE id=198

## Acceptance Criteria
- [ ] id=198 description length: 16000-19500 chars (from 13380) — growth from additions A-F
- [ ] ALL existing 12 sections still present with content unchanged except minor additions
- [ ] New sections "0. Time Budget", "2b. Capacity Estimation", "12b. L5 Tradeoff Table" all present with substantive content
- [ ] Section 11 Serving Architecture has service-by-SLA table (≥7 rows) + storage selection table (≥5 rows)
- [ ] Section 8 has SLO subsection with ≥ 5 concrete SLOs
- [ ] New Section 6 "Summary & Tradeoffs" is between existing S11 and S12
- [ ] Description passes ALL Appendix A quality gates from id=18
- [ ] Self-Check section has 7 checkmarks mapped to id=18 pass-bar
- [ ] Seed script idempotent
- [ ] `framework_nodes_description_history` captures pre-update content
- [ ] `npm run build` green
- [ ] Manual smoke: /kg?node=n198 renders cleanly; link to id=18 in Prerequisites works; all new tables format correctly

### P2 -- Nice to Have

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

> 462 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-18** -- T-P2-503: KG-UX-12: Audit/migrate scattered content_length checks + LESSONS entry. ## Problem
- [x] **2026-04-18** -- T-P2-500: [DEBT] CLAUDE.md: Remove duplicate Key Constraints section. CLAUDE.md has two ## Key Constraints sections (lines 15 and 34) with nearly identical content. The first is a template p
- [x] **2026-04-18** -- T-P1-511: T-MLSD-AUDIT-01: Score 10 design problems against L5 framework, produce gap report. ## Context
- [x] **2026-04-18** -- T-P1-509: KG-CONTENT-02: Add LC 1392 Longest Happy Prefix to KMP family (kmp[n-1] canonical application). ## Context
- [x] **2026-04-18** -- T-P1-508: KG-CONTENT-01: Add KMP family to Quick Index + expand KMP section in Array/String node (n44). ## Context
- [x] **2026-04-18** -- T-P1-507: KG-UX-17: TreeNav click must honor hasContent gate (extract activateNode helper). ## Problem
- [x] **2026-04-18** -- T-P1-506: KG-UX-15: Category node expanded/collapsed visual distinction (saturation + chevron). ## Problem
- [x] **2026-04-18** -- T-P1-505: KG-UX-16: Cold-load defaults to first pillar at zoom 1.0 (not fitView all). ## Problem
- [x] **2026-04-18** -- T-P1-504: Fix rewrite_nodes_to_cn.py: preserve canonical_hub HTML comment markers. CN rewrite (commit 295ada1) stripped HTML comment markers (<!-- doc_kind: canonical_hub -->, sentinel blocks) from frame
- [x] **2026-04-18** -- T-P1-502: KG-UX-14: Initial fitView maxZoom cap + URL deeplink direct-focus. ## Problem
- [x] **2026-04-18** -- T-P1-501: KG-UX-10: Empty-content nodes skip drawer (tri-state click) + hasContent util. ## Problem
- [x] **2026-04-18** -- T-P1-499: [SYNC] Fix settings.json: replace bare python with /c/Anaconda/python.exe. All 8 hook commands in .claude/settings.json use bare python instead of /c/Anaconda/python.exe. This violates the CLAUDE
- [x] **2026-04-18** -- T-P0-510: T-MLSD-FRAMEWORK-01: Populate id=18 'System Design Framework' with canonical L5 paradigm. ## Context
- [x] **2026-04-17** -- T-P2-492: KG-UX-06: Bezier edges, pillar-colored, spacing polish. Current edges are orthogonal smoothstep with flat gray. Upgrade to bezier curves colored by source pillar for mindmap ae
- [x] **2026-04-17** -- T-P1-498: KG-CN-01: Rewrite node descriptions to CN narration + full English terms. Rewrite framework_nodes.description to Chinese narration + English full-expansion terms. Pilot on 4 nodes validated qual
- [x] **2026-04-17** -- T-P1-491: KG-UX-05: Swimlane layout - per-pillar ELK vertically stacked. Current layered layout stacks 8 pillars in leftmost column causing cross-pillar overlap and visual chaos. Refactor to sw
- [x] **2026-04-17** -- T-P1-490: KG-UX-04: 0-children categories act as leaves; stub badge. 7 depth-1 categories (SQL Fundamentals, OOD SOLID, Diffusion Models, etc.) have 0 children. Expanding them does nothing 
- [x] **2026-04-17** -- T-P1-486: [KG-VIZ-R03] Interaction: tooltip, keyboard a11y, expand-all, hover edge highlight. Post-polish interaction refinements. Scoped per user review (cut edge legend toggle, pillar filter buttons, +/-/0 shortc
- [x] **2026-04-17** -- T-P0-497: KG-UX-09: TreeNav click -> expand ancestors + setCenter on canvas. Wire TreeNav (KG-UX-08) to the canvas. Clicking an entry in TreeNav should: (1) setExpanded to include all ancestors of 
