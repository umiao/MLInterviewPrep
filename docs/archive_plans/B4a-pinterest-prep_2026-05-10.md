# B4a Pinterest-prep -- Archive Dry-Run Plan (2026-05-10)

> Per `docs/workflow/company_internalization_protocol.md` -- the dry-run gate. WRITES NOTHING TO DB. User reviews §2 (causal-proof matrix) and §5 (promotion candidates), then explicitly approves before any apply step.

- **Company**: Pinterest (id=29, status=onsite)
- **Audit source**: `docs/audit/company_kg_internalization_audit_2026-05-10.md` (T-P1-798) -- Pinterest row: S3 = 102 041 B across 12 docs, S4/S5/S6 all 0
- **Subset scope**: prep = the loop-narrative + scheduling-flavour docs that describe **how the Pinterest onsite is structured** and the **interview-craft moves** the user plans to make. Not deep-dive prose (that is CONCEPTS), not LC/BQ tag indices (that is TOC). The 3 docs in scope:
  - `company_documents.id=39` -- "Pinterest Senior MLE -- Recruiter Call Prep" (4 636 chars; 2026-04-08 recruiter-call digest + Phone Screen breakdown + 5-round VO breakdown + CTCI 7-step + BUD/BCR + coding checklist + Pinterest research resource list + mission/values)
  - `company_documents.id=49` -- "Pinterest LC Investigation: Restaurant Intervals" (1 686 chars; candidate-comparison + LC 1851 selection rationale for the "餐馆区间" 2025-11 面经题)
  - `company_documents.id=83` -- "[Pinterest] ML Virtual Onsite Prep" (5 522 chars; 5-round VO playbook with per-round expectations + traps + common patterns + 60-second pre-exit cheat sheet)
- **Sister plans (NOT in scope here, separate B4a tasks)**:
  - T-P0-810 (Pinterest-TOC, drafted): docs 47 / 48 / 66 -- navigation indices. Owns the S2 trim + the 34 S4 + 15 S6 tag rows.
  - T-P0-811 (Pinterest-CONCEPTS, drafted): docs 58 / 70 / 71 / 73 / 74 / 75 -- deep-dive prose. Owns the ~16 S5 INSERT rows and the 5 required new meta-prep nodes.
- **Surfaces touched here**: S3 only (3 docs). S1 empty. S2 [OWNED-BY: B4a-pinterest-toc] (skip). S4 [OWNED-BY: B4a-pinterest-toc] (the LC 1851 tag from doc 49's investigation is already in the TOC plan's `likely` row at problem_id=144). S5 [OWNED-BY: B4a-pinterest-concepts] (skip; the 3 prep docs do not narrate per-KG-node Pinterest flavours, only interview-craft). S6 [OWNED-BY: B4a-pinterest-toc] (skip).
- **Apply gate**: "ok 执行" or equivalent green light from user. Silence is not the gate.

> **Cross-plan ownership note**: of the 3 Pinterest B4a plans, this prep plan is the **lightest** -- the prep docs' substantive content is largely **interview-craft already covered by meta-prep/onsite-loop-templates/* and meta-prep/code-pad-best-practices/* canonical nodes**. The actual migration shape is "extend kg://297-301 + kg://276-281 description with 5-6 small subsections" rather than "create new nodes". The §5 promotion load is correspondingly the lightest of the 3 (4 recommended extensions, 0 required new nodes).

---

## §1 Inventory snapshot

### S1 -- `companies.prep_notes` (pn_len = NULL)

Empty. Skip.

### S2 -- `companies.notes` (446 bytes)

`[OWNED-BY: B4a-pinterest-toc]`. The 446-byte admin-metadata + recruiter-call summary lives in the TOC plan's §2 / §4.4. This prep plan skips the S2 row to avoid 3-way conflicting UPDATEs.

### S3 -- prep subset, 3 docs / 11 844 chars / 16 764 UTF-8 bytes

| id | chars  | bytes  | doc_kind  | source_path | title                                                |
|---:|-------:|-------:|-----------|-------------|------------------------------------------------------|
| 39 |  4 636 |  6 550 | prep_note | (none)      | Pinterest Senior MLE -- Recruiter Call Prep          |
| 49 |  1 686 |  2 974 | prep_note | (none)      | Pinterest LC Investigation: Restaurant Intervals     |
| 83 |  5 522 |  7 240 | prep_note | (none)      | [Pinterest] ML Virtual Onsite Prep                   |

(Audit roll-up reports S3 = 102 041 B across 12 docs; the 3 prep docs above are 16 764 B / 12 docs ~= 16 % of the total. The TOC subset is 21 140 B (~21 %); the CONCEPTS subset is 64 137 B (~63 %). Sum 16 764 + 21 140 + 64 137 = 102 041 .)

**First 200 chars per doc**:

- **id=39** "# Pinterest Senior ML Engineer -- 面试准备笔记 / > **2026-04-08 Recruiter Call 总结** / > 与 Pinterest recruiter David 通话完毕，面试结构及准备要点整理如下 / ## 基本信息 / - **职级**: Senior Level / - **薪资**: ~$500K/年 TC / - **招聘模式**: 统招，HC 有限（目前约 5 个）"
- **id=49** "# Pinterest LC 调研笔记：「寻找餐馆区间」 / > 来源：Pinterest 2025-11 面经 dump。原题名「寻找餐馆区间」，无 LC 编号 / > 本文档记录候选对照、判定与结论 / ## 候选对照 / 面经候选：LC 1779 / 2563 / 1094 / 1851"
- **id=83** "<!-- PINTEREST_ONSITE_PREP_20260428 --> / # Pinterest ML Virtual Onsite — Prep 笔记 / > **Schedule lives on the Dashboard** (left-nav first item) — InterviewTimeline widget reads `interview_events` table. This doc is for prep narrative only. / > 5 场 virtual onsite，no particular order: 2× DSA (45 min) + 1× ML Practitioner (60 min) + 1× ML System Design (60 min) + 1× Competency/HM (45 min)"

**Per-doc topic counts** (markdown `## H2 / ### H3` headings; doc 49 has no H3):

| id | H2 sections | H3 sections | total |
|---:|---:|---:|---:|
| 39 | 7 (基本信息 / 面试结构总览 / 面试环境 / Phone Screen 准备要点 / Coding 面试方法论 / 准备清单 / 推荐准备资源 / 关于 Pinterest / 与现有准备材料的交叉引用) | 6 (Phone Screen / Virtual Onsite / 1 ML Project / 2 ML Fundamentals / 3 Coding / Gayle / BUD / 5 种优化 / BCR / 绝对不要做 / 需要立即行动 / 准备计划 / 刷题平台 / Pinterest 相关) | ~15 |
| 49 | 3 (候选对照 / 判定 / 落库动作 / 若结论有误) | 2 (依据 / 模式速记) | 5 |
| 83 | 6 (DSA×2 / ML Practitioner / ML SD / Competency / 共通 pattern / 60秒 cheat sheet) | 4 (4-评估维度 / 高频题型 / 核心议题 / 4个高频 SD 题) | ~10 |

**Per-doc kg_refs / drawer_links** (best-effort grep; the prep docs were authored pre-URI-convention so kg://N counts are 0):

| id | kg_refs (kg:// URIs) | drawer_links (db://, cd://) | notes |
|---:|---:|---:|---|
| 39 | 0 | 0 | references "Pillar 2 (ML Fundamentals & Theory) -- 192 framework nodes" + "28 system design 模块" + "29 行为面试案例" + "1058 道题目" via prose; no canonical URIs |
| 49 | 0 | 0 | references `bq_behavioral_examples.json` slug; references LC 1779/2563/1094/1851 by LC number not db:// URI |
| 83 | 0 | 0 | references "interview_events table" + "Dashboard / InterviewTimeline widget" + Patrick Halina blog URL + Pinterest Engineering blog URLs |

**Substantive content classes** (per-doc, used as the §2 row grouping):

| id | substantive content classes |
|---:|---|
| 39 | (a) 5-round VO breakdown table; (b) Phone Screen 60-min breakdown table; (c) Pinterest-specific environment (Google Meet + CoderPad-no-compiler); (d) ML Project Discussion 7-bullet topic coverage list; (e) ML Fundamentals 6-topic review list; (f) CTCI 7-step + BUD + 5-optimization + BCR + "不要做" interview-craft block; (g) coding 10-point checklist from David (recruiter); (h) Pinterest research-resource link bundle (Engineering Blog / Publications / GitHub / StackShare / Careers / PinFlex / Patrick Halina); (i) Pinterest mission + 5 core values; (j) cross-reference to in-repo prep materials (Pillar 2 / SD 模块 / BQ 案例 / 题库 / 项目 deep-dive) |
| 49 | (a) candidate-comparison 4-row table (LC 1779 vs 2563 vs 1094 vs 1851); (b) 4-criteria 判定 rationale (区间 关键词 / 寻找 语义 / 餐馆 主题改写 / 难度); (c) LC 1851 mode 速记 (offline sort + heap-by-length + r<q pop); (d) 落库动作 (S4 INSERT for problems.id=144); (e) 若结论有误 fallback (LC 1094 / LC 2563 alternates 互相迁移成本低) |
| 83 | (a) 5-round structure top-line (2× DSA 45m + ML Practitioner 60m + ML SD 60m + Competency/HM 45m, no particular order); (b) DSA round expectations (production-quality + tightly-scoped + 1-2 题/45 min + algo vs systems-flavored sub-classes); (c) ML Practitioner 4-dim rubric (Problem framing & model selection / Featurization / Deployment / Evaluation & online); (d) ML Practitioner 高频题型 (Detect unsafe / Ad CTR / Homefeed Lightweight Ranking); (e) ML SD pre-question 4-clarify (候选类型 / responsive / scale / latency tier); (f) ML SD 核心议题 5-axis (training cadence / retrieval / ranking / serving / monitoring); (g) ML SD 4 高频题 (Homefeed candidate-gen / Homefeed personalized / Pinterest Search ranking / Ads Funnel); (h) ML SD 面试官特别看的 4-point (infra→modeling / UI→labels / failure-debug / recent paper); (i) Competency/HM 4-axis prep (deep-dive / challenge-2 / impact framing / HM 隐线); (j) 5-round 共通 pattern 5-row 翻车 vs 做对 table; (k) 60-second pre-exit cheat sheet 4-bullet; (l) prep-call (4/29 14:00 PT) 5-bullet 确认清单 (ephemeral) |

### S4 -- `problem_company_tags`

`[OWNED-BY: B4a-pinterest-toc]`. The only prep-doc S4 candidate is the LC 1851 row (driven by doc 49's investigation) -- already present in the TOC plan's `likely` row at problem_id=144 with source=`B4a-pinterest-toc-archive-2026-05-10` and notes=`LC 1851 离线排序 + heap 弹失效 (2025-11)`. Skip.

### S5 -- `node_company_tags`

`[OWNED-BY: B4a-pinterest-concepts]`. Pinterest's S5 rows are owned by the CONCEPTS plan (~16 rows on kg://122 / 139 / 200 / 252 / 254 / 260 / 265 / 266 / 271 + new nodes). The 3 prep docs do not narrate per-KG-node Pinterest flavours -- their content is **interview-craft about how to navigate Pinterest's loop**, not technical takes on KG nodes -- so no S5 rows originate here. Skip.

### S6 -- `behavioral_example_company_tags`

`[OWNED-BY: B4a-pinterest-toc]`. The BQ Q->Story matrix lives in doc id=48 (TOC subset). The prep docs (doc 83 in particular) reference behavioral round only at a structural level ("Competency/HM round = 45 min, 1 deep-dive + 2 challenges + impact framing"), not at the story-mapping level. Skip.

---

## §2 Migration matrix (4-tuple causal-proof)

One row per archive candidate. Target URIs:
- `kg://N` = `framework_nodes.id = N` (canonical)
- `db://N` = `problems.id = N` (used cross-ref only; prep docs don't write to `problems`)
- `cd://N` = `company_documents.id = N` (only used for the surviving thin hub doc)
- `sd://<slug>` = `meta-prep/system-design-must-knows/<slug>` framework_node by path (resolves to `kg://N` via path lookup)

Rows are grouped by surface (S3 only for this plan), then by doc, then by archive candidate.

### S3 -- per-doc rows

#### Doc id=39 "Pinterest Senior MLE -- Recruiter Call Prep" (4 636 chars, prep_note)

This doc is the **2026-04-08 recruiter-call digest** capturing loop structure + interview environment + a CTCI-flavoured coding self-prep block + a Pinterest research resource bundle. The loop-structure rows already have canonical homes in `meta-prep/onsite-loop-templates/*`; the CTCI / BUD / BCR rows live in `meta-prep/code-pad-best-practices/*`.

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| 基本信息 (Senior Level / TC ~$500K / 统招 ~5 HC / Team Match required) | id=39 char 0-300 | `companies.notes` (S2) -- TOC plan §4.4 keeps "Senior MLE / TC ~$500K / general pool ~5 HC / Team Match required" admin block | `SELECT notes FROM companies WHERE id=29` -- post-archive ~150 B contains "Senior ML Engineer / TC ~$500K / general pool / Team Match" |
| Phone Screen 60-min breakdown (Intro+ML Project 10-15min / 3 ML Fundamentals 15-20min / 1 Coding 25-30min) | id=39 §"Phone Screen" table, char 300-600 | `kg://298` (pre-loop-recruiter-and-tech-screen) §"60-min phone-screen 3-block template". **§5 promotion candidate**: extend kg://298 description with the 3-block-time-budget template (the same shape recurs at Meta L6 / Google R0 / Uber). | `SELECT description FROM framework_nodes WHERE id=298` -- post-promotion contains "Intro + ML Project ~10-15m / 3 ML Fundamentals ~15-20m / 1 Coding ~25-30m" |
| 5-round VO breakdown table (R1 LC / R2 LC / R3 ML Deep Dive / R4 ML SD / R5 BQ, each 60 min) | id=39 §"Virtual Onsite" table, char 600-900 | `kg://297` (standard-4-round-mle-vo) §"5-round variant (DSA×2 + ML Practitioner + ML SD + BQ)". **§5 promotion candidate** (same as TOC plan §5 cand 3; cross-ref). | `SELECT description FROM framework_nodes WHERE id=297` -- post-promotion contains "5-round variant" subsection enumerating {DSA×2, ML Practitioner, ML SD, BQ} |
| 面试环境 (Google Meet + CoderPad-no-compiler + Python/Java/C++ 推荐 + 稳定网络) | id=39 §"面试环境" block, char 900-1100 | `kg://281` (language-choice-python-default) §"code-pad environments matrix" -- Pinterest is one of N code-pad-environment rows. **§5 promotion candidate** (also flagged in TOC plan §5 cand 4). | `SELECT description FROM framework_nodes WHERE id=281` -- post-promotion contains a "code-pad environments matrix" subsection that lists CoderPad-no-compiler + which companies use it |
| Phone Screen / ML Project Discussion 7-bullet topic coverage (背景&目标 / 方法选择 / 你的贡献 / 数据&特征 / 训练&评估 / 部署&效果 / 挑战&解决) | id=39 §"1 ML Project Discussion" block, char 1100-1500 | `kg://301` (project-deep-dive-round) §"7-bullet topic coverage checklist". **§5 promotion candidate**: extend kg://301 with this checklist (already overlaps with doc 83 §4 deep-dive section -- consolidated migration). | `SELECT description FROM framework_nodes WHERE id=301` -- post-promotion contains "项目背景&业务目标 / ML 方法选择 / 你的贡献 / 数据处理&特征 / 模型训练&评估指标 / 上线部署&效果 / 挑战&解决" 7-bullet list |
| Phone Screen / ML Fundamentals 6-topic review (Logistic Regression / Variance-Bias / Regularization / Decision Trees / Convex / Model Evaluation) | id=39 §"2 ML Fundamentals" block, char 1500-1900 | `kg://298` (pre-loop-recruiter-and-tech-screen) §"ML Fundamentals topic catalog" (these 6 topics are textbook + generic; the official Pinterest Prep Guide bundle is annotated in `companies.notes` admin block already). **§5 promotion candidate**: extend kg://298 with the 6-topic generic catalog. | `SELECT description FROM framework_nodes WHERE id=298` -- post-promotion contains "Logistic Regression / Bias-Variance / Regularization L1+L2 / Decision Trees + Ensembles / Convex Optimization / Model Evaluation precision+recall+AUC" |
| Phone Screen / Coding "LC Medium~Hard + follow-up + edge cases" framing | id=39 §"3 Coding Challenge" block, char 1900-2050 | merges into `kg://298` §"coding sub-round" (same as the TOC plan's pointer to kg://298 for phone-screen structure) | (same query as above row) -- contains "LC Medium ~ Hard" + "follow-up + edge cases" 1-line framing |
| CTCI 7-step framework (Listen / Example / Brute Force / Optimize / Walk Through / Implement / Test) | id=39 §"Gayle Laakmann McDowell" block, char 2050-2450 | already canonical in `kg://276` (clarify-restate-before-typing) + `kg://277` (think-out-loud-narration) + `kg://280` (walk-through-before-implement) + `kg://279` (bud-bottleneck-unnecessary-duplicated). The 7-step list maps as: Listen→kg://276, Example→kg://276, Brute Force→kg://279, Optimize→kg://279, Walk Through→kg://280, Implement→kg://280, Test→kg://278 (enumerate-edge-cases-bullet-list). **§5 promotion candidate (low priority)**: add a single mnemonic-7-step description bullet to `kg://244` (parent code-pad-best-practices) that names the CTCI canonical sequence and points to the 5 child nodes -- recoverable as a "what's the 7-step order" lookup. | `SELECT description FROM framework_nodes WHERE id IN (244, 276, 277, 278, 279, 280)` -- the 7 steps map to the 5 child nodes (Listen/Example shared by 276; BruteForce/Optimize shared by 279; Walk-Through/Implement shared by 280; Test = 278) |
| BUD optimization (Bottleneck / Unnecessary / Duplicated) | id=39 §"BUD 优化法" block, char 2450-2600 | `kg://279` (bud-bottleneck-unnecessary-duplicated) -- already canonical | `SELECT title, description FROM framework_nodes WHERE id=279` -- title contains "BUD" + description covers all 3 letters |
| 5 种优化思路 (BUD / DIY / Simplify&Generalize / Base Case&Build / Data Structure Brainstorm) | id=39 §"5 种优化思路" block, char 2600-2800 | the 5-fold optimization mnemonic is interview-craft. **§5 promotion candidate**: extend `kg://279` description with the 5-name catalog (BUD is already there; add the other 4 with 1-line definitions each). | `SELECT description FROM framework_nodes WHERE id=279` -- post-promotion contains "DIY (manual+reverse-engineer) / Simplify+Generalize / Base Case+Build / Data Structure Brainstorm" |
| BCR (Best Conceivable Runtime) -- theoretical lower bound; stop optimizing when matched | id=39 §"BCR" block, char 2800-2950 | **§5 promotion candidate**: extend `kg://279` description with a BCR sub-bullet (BCR is the theoretical floor; reaching it = stop). Generic interview-craft; recurring at any algorithmic round. | (same query) -- post-promotion contains "BCR" + "theoretical lower bound" |
| "绝对不要做的事" 4-bullet (忽略题目信息 / 纯脑中想 / 迷糊硬写代码 / 没得面试官认可就开始写代码) | id=39 §"绝对不要做的事" block, char 2950-3100 | inverse-form of canonical: covered by `kg://276` (clarify-restate) + `kg://280` (walk-through-before-implement) + `kg://277` (think-out-loud). The 4-bullet "don't do" list inverts to 4 canonical "do" rules. Drop the negative phrasing; substantive content already there. | (queries above) -- each anti-pattern has a corresponding canonical positive rule |
| David (Recruiter) coding 10-point checklist (clarifying Qs / DS&Algo justification / time-space complexity / no syntax / 最优解 / corner&edge / 防御性 / 验证 / think-out-loud / follow-up prep) | id=39 §"Coding 面试核心 Checklist" block, char 3100-3550 | each bullet maps to a canonical: clarifying Qs→kg://276; DS&Algo→kg://279; complexity→kg://279/280; no syntax→kg://281 (language-choice + code-pad quirks); 最优解→kg://279; corner&edge→kg://278; 防御性 / 验证→kg://280; think-out-loud→kg://277; follow-up→kg://298 §"coding sub-round" (already promoted above). The recruiter-citation flavour ("from David") drops; substantive content already canonical. | `SELECT description FROM framework_nodes WHERE id IN (276, 277, 278, 279, 280, 281, 298)` -- each canonical contains the substantive rule from the 10-point list |
| 准备清单 / "需要立即行动" 3-bullet (回复 3+ 可用时段 / 发简历 / 准备 ML 项目) | id=39 §"需要立即行动" block, char 3550-3700 | **drop** -- ephemeral 2026-04-08 action items, already resolved (Pinterest is `status=onsite`, recruiter call past). Cross-link to `interview_events` (Dashboard.InterviewTimeline) for any future scheduling. | `SELECT name, status FROM companies WHERE id=29` -- already `onsite`  |
| 准备清单 / "准备计划" 7-bullet (复习 ML Fund / LC Medium-Hard 计时 / CTCI 7 步 / CoderPad 熟悉 / Pinterest Eng Blog / Patrick Halina blog / BQ 故事) | id=39 §"准备计划" block, char 3700-3950 | each bullet maps to a study-plan item: ML Fund→kg://298 §"ML Fundamentals topic catalog" (promoted above); LC 计时→kg://297 + `problem_attempts` table convention; CTCI→kg://276-280 (canonical); CoderPad→kg://281 (promoted above); Pinterest blogs→see "Pinterest research-resource bundle" row below; BQ 故事→kg://300 + S6 tags (TOC plan owns). The 7-bullet plan itself is study-flow scaffolding, no novel claim; drops as a list, items live in canonical homes. | (queries above for each canonical) |
| 推荐准备资源 / 刷题平台 (LeetCode / HackerEarth / CareerCup / GeeksforGeeks / TopCoder URLs) | id=39 §"刷题平台" block, char 3950-4100 | the 5 platforms are **generic interview-prep resources** (not Pinterest-specific). **§5 promotion candidate (low priority, deferred)**: extend `kg://241` (lc-keyword-checklists parent) description with a "practice-platform catalog" 5-bullet list. Cross-company: every company benefits from this list. | post-promotion: `SELECT description FROM framework_nodes WHERE id=241` -- contains "LeetCode / HackerEarth / CareerCup / GeeksforGeeks / TopCoder" |
| 推荐准备资源 / Pinterest 相关 (Pinterest Eng Blog / Publications / GitHub / StackShare / Careers / PinFlex / Patrick Halina blog URLs) | id=39 §"Pinterest 相关" block, char 4100-4400 | **The most Pinterest-specific block in the doc.** Migrates to: (a) a Pinterest-flavoured §5 row -- but the CONCEPTS plan owns S5 and this URL-bundle isn't a per-KG-node Pinterest take, it's a company-level resource list; (b) survives in the **§3 skeleton's `## Resources` subsection** of the merged Pinterest hub doc (cd://new) as a 7-link bullet list. **§5 promotion candidate**: T-P1-821 considers a `companies.resource_links` schema extension (or a Pinterest-specific `cd://` resource doc) so future companies can mirror this pattern. **Causal-proof gate**: the 7 URLs MUST land in the merged hub doc's §"Resources" subsection before id=39 is deleted, else the link bundle is unrecoverable from canonical nodes (no meta-prep node lists per-company blog URLs). | `grep -c "Pinterest Engineering Blog\|Patrick Halina\|PinFlex" <merged-hub-doc-content>` -- expect 1 for each URL post-archive (Pinterest hub doc retains the 7-link bundle); `SELECT length(content) FROM company_documents WHERE company_id=29 AND doc_kind='hub_doc'` -- contains the 7 URLs |
| 关于 Pinterest / mission + 5 core values (Put Pinners First / Aim for Extraordinary / Create Belonging / Act as One / Win or Learn) | id=39 §"关于 Pinterest" block, char 4400-4500 | **drop** -- corporate-values prose is admin-flavour, not a substantive claim. Cross-link to `pinterestcareers.com` URL (already in the Resources bundle row above). The values themselves are a 30-second self-introduction warm-up at most; no kg target needed. | n/a; the 7 URLs in the Resources bundle suffice for cross-reference |
| 与现有准备材料的交叉引用 (Pillar 2 / 28 SD 模块 / 29 BQ 案例 / 1058 题 / 3 deep-dive 项目) | id=39 §"与现有准备材料的交叉引用" table, char 4500-4636 | the table is **a map of in-repo resources, snapshotted 2026-04-08**. The counts (192 / 28 / 29 / 1058 / 3) are stale already (post 2026-04 work has added nodes + problems + stories). **Drop**; the live counts are available from the audit roll-up + the navbar Knowledge Graph view. Cross-link to `kg://241` (lc-keyword-checklists) + `kg://242` (system-design-must-knows) + `kg://245-250` (behavioral-clusters) as the canonical "see also" set. | n/a; canonical KG roots replace the snapshot |

**Causal-proof gate for id=39**: archive cannot proceed until (a) Pinterest research-resource link bundle (7 URLs) lands in the merged hub doc's `## Resources` subsection; (b) the 5-round VO variant extension on kg://297 lands OR is explicitly deferred with `kg://297 §5-round variant` placeholder accepted in the merged skeleton; (c) the ML Fundamentals 6-topic catalog on kg://298 lands. Without (a), the Patrick Halina blog + Pinterest Engineering Blog URLs are unrecoverable. (b) and (c) are softer: the substantive 5-round shape is captured in doc 83 (also archived this plan) and the 6 ML Fundamentals topics are textbook -- but cleanest archive has them promoted.

#### Doc id=49 "Pinterest LC Investigation: Restaurant Intervals" (1 686 chars, prep_note)

This doc is a **single-question investigation note**: the 2025-11 面经 has a "寻找餐馆区间"题 without LC#, and 4 candidates (LC 1779 / 2563 / 1094 / 1851) were evaluated against 4 criteria (关键词 / 寻找 语义 / 餐馆主题 / 难度); LC 1851 wins. The substantive output is the S4 tag on LC 1851 (already in TOC plan's `likely` row) + the pattern speed-memo (offline sort + heap-by-length + r<q pop).

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| 候选对照 4-row table (LC 1779 / 2563 / 1094 / 1851 + 难度 + 核心套路 + 与"餐馆区间"契合度) | id=49 §"候选对照" table, char 100-700 | the **table itself drops** -- the 3 rejected candidates (LC 1779, 2563, 1094) were rejected; no claim about them survives the archive. LC 1851 row is preserved via TOC plan's S4 `likely` tag on problem_id=144. The investigation-as-prose value (showing the reader HOW to disambiguate) is generic interview-craft, see promotion row below. | `SELECT pct.* FROM problem_company_tags pct WHERE pct.company_id=29 AND pct.problem_id=144` -- 1 row, notes contains "LC 1851 离线排序 + heap 弹失效 (2025-11)" |
| 4-criteria 判定 rationale (1. 关键词「区间」对齐; 2. 「寻找」语义对齐; 3. 「餐馆」主题改写自然 LBS 场景; 4. Pinterest Must-Do 偏 Hard) | id=49 §"判定 / 依据" block, char 700-1200 | the **4-criteria disambiguation rubric** (关键词 / 语义 / 主题改写 / 难度) is **generic interview-craft** -- it applies any time a 面经 题 lacks an LC#. **§5 promotion candidate**: extend `kg://284` (binary-search-and-on-answer; or alternatively a new sibling under `kg://241`) description with a "LC-题面-to-LC#-identification 4-criteria rubric" subsection. Cross-company applicable but defer 3-company threshold check to T-P1-821. | (post-promotion if landed) `SELECT description FROM framework_nodes WHERE id=284` -- contains "关键词对齐 / 语义对齐 / 主题改写自然度 / 难度对齐" 4-criteria identification rubric |
| LC 1851 模式速记 (离线: queries 按值排序 + intervals 按左端排序; 小顶堆 keyed by 区间长度; 遍历 q, push `l<=q`, pop `r<q`, top = 答案) | id=49 §"模式速记" block, char 1200-1500 | `kg://291` (intervals-merge-meeting-rooms) §"min-interval-cover query template" addendum AND/OR `problems.notes` for problem_id=144 (LC 1851). The mode is generic intervals-family pattern. **§5 promotion candidate (medium priority)**: extend `kg://291` with the "min-interval-cover query" template; the LC 1851-specific micro-walk also belongs in `problems.notes`. Per TOC plan's note about `problems.one_liner` field, this could land in problems.one_liner OR problems.notes. | `SELECT description FROM framework_nodes WHERE id=291` -- post-promotion contains "离线 queries + intervals 排序 + 小顶堆 keyed by 长度 + pop r<q" template; `SELECT notes FROM problems WHERE id=144` -- contains the mode 速记 verbatim |
| 落库动作 (`Pinterest` 追加到 problems.id=144 company_tags) | id=49 §"落库动作" block, char 1500-1600 | **superseded** by the new S4 row on problem_company_tags (the join-table replacement for the legacy `problems.company_tags` JSON column). Verify the legacy column is also updated OR the migration to S4 is complete enough that legacy column is read-only. | `SELECT pct.* FROM problem_company_tags pct WHERE pct.company_id=29 AND pct.problem_id=144` -- 1 row (already covered by TOC plan §4.5 `likely` block); `SELECT company_tags FROM problems WHERE id=144` -- already `["Pinterest"]` per current DB state |
| "若结论有误" fallback (LC 1094 / 2563 也是 Pinterest Must-Do 周边套路 410/2402 家族；复习互相迁移成本低) | id=49 §"若结论有误" block, char 1600-1686 | the fallback caveat ITSELF drops (it's a "we might be wrong" hedge). The substantive claim "LC 1094 (差分扫描线) + LC 2563 (排序+二分) + LC 410 + LC 2402 是 interval/heap 同家族, 互相迁移" survives via the TOC plan's existing S4 rows: LC 410 (id=265, core) + LC 2402 (id=258, core) + LC 1851 (id=144, likely). LC 1094 and 2563 are NOT in the TOC plan's S4 tags -- if user wants them as Pinterest-flagged fallbacks, add as 2 extra `likely` rows in TOC plan §4.5 (cross-plan amendment). **Decision pending user review**: add LC 1094 + LC 2563 to TOC plan's S4 `likely` list, OR accept loss of "investigation fallback" prose. Default: **accept loss** (the 2 candidates are not Pinterest-anchored; they're just same-family LC#s). | (default decision) no new S4 rows; investigation prose drops with restore.sql as the rollback path |

**Causal-proof gate for id=49**: archive cannot proceed until (a) the LC 1851 mode 速记 is captured in either `kg://291` description OR `problems.notes` for problem_id=144 -- the 5-step "离线 / 排序 / 小顶堆 / pop / top" template is the only unrecoverable substantive content. (b) The 4-criteria identification rubric is optional / promotable but its loss is a craft-loss not a claim-loss.

#### Doc id=83 "[Pinterest] ML Virtual Onsite Prep" (5 522 chars, prep_note)

This doc is the **5-round VO playbook** authored 2026-04-28 (per the HTML comment `PINTEREST_ONSITE_PREP_20260428`). It's the most substantive of the 3 prep docs -- contains 4 per-round rubrics + a common-pattern table + a 60-second pre-exit cheat sheet. Each per-round rubric is largely **de-companied interview-craft** (the 4-dim ML Practitioner rubric applies at any production-MLE company); the Pinterest-specific anchors are limited to (a) "Detect unsafe / Ad CTR / Homefeed Lightweight Ranking" 3-题型 listing (which is per-CONCEPTS docs 74 / 73 + S5 rows owned by CONCEPTS plan); (b) "Homefeed candidate-gen / Homefeed personalized / Pinterest Search ranking / Ads Funnel" 4-高频-SD-题 listing (also CONCEPTS-flavoured).

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| Intro line: "Schedule lives on the Dashboard (left-nav first item) — InterviewTimeline widget reads `interview_events` table. This doc is for prep narrative only." | id=83 char 80-280 | **drop** -- this line is **meta**: it documents the dashboard split, not interview content. The routing rule itself is in CLAUDE.md "Surface Identification" table. Pinterest schedule events live in `interview_events`, not in `company_documents.content` (per invariant3_guard.py + the dashboard skill). | `SELECT * FROM interview_events WHERE company_id=29` -- Pinterest onsite events live here, not in this doc; CLAUDE.md routing rule covers the meta-claim |
| 5-round structure top-line (2× DSA 45m + 1× ML Practitioner 60m + 1× ML SD 60m + 1× Competency/HM 45m, no particular order, ~4h 10m total) | id=83 char 280-450 | `kg://297` (standard-4-round-mle-vo) §"5-round variant" addendum (same as doc 39's 5-round table row + TOC plan §5 cand 3). **§5 promotion candidate**: extend kg://297 with the variant including the per-round duration breakdown (45 vs 60 min asymmetry is a strong signal). | `SELECT description FROM framework_nodes WHERE id=297` -- contains "5-round variant: 2× DSA 45m + ML Practitioner 60m + ML SD 60m + BQ 45m, no particular order" |
| "Core framing: 不是 model 调参员，是从 problem framing 一路 own 到 deployment 的工程师" | id=83 char 450-600 | `kg://301` (project-deep-dive-round) §"core framing" 1-liner addendum; also `kg://299` (ml-system-design-round) §"ownership framing". Generic; recurring at all production-MLE roles. **§5 promotion candidate (low priority)**. | `SELECT description FROM framework_nodes WHERE id IN (299, 301)` -- contains "own from problem framing to deployment" framing |
| §1 DSA × 2 expectations (production-quality + clean code, not LC 速通; 45min/1-2 题; 比 phone screen 标准更严) | id=83 §1 char 600-1000 | `kg://297` §"5-round variant" (above row) addendum + the DSA-quality bar is inherent to `kg://297` already. No new row needed. | `SELECT description FROM framework_nodes WHERE id=297` -- contains "production-quality + clean-code DSA bar" |
| §1 DSA / 永远先 clarify + 边讲边写 + Code review 视角 + 题型预期 (一场偏 algo, 一场偏 systems-flavored LRU/rate-limiter/scheduler) + Trap (套模板 / import 替代实现 / happy-path 跑通就交) | id=83 §1 sub-bullets char 1000-1500 | each maps to canonical: clarify→kg://276; 边讲边写→kg://277; Code review 视角→kg://278 (enumerate edge cases) + kg://280 (walk-through-before-implement); 题型预期 systems-flavored→**new §5 promotion candidate** to `kg://297` §"DSA sub-types" (algo vs systems-flavored), since the systems-flavored sub-class (LRU / rate-limiter / scheduler) is recurring at Senior+ levels across companies. Traps: each is the negative form of canonical (套模板=anti-kg://279; import 替代=anti-kg://281 §"don't use stdlib for the answer"; happy-path=anti-kg://278). | `SELECT description FROM framework_nodes WHERE id IN (276, 277, 278, 279, 280, 281, 297)` -- each canonical contains the positive rule; kg://297 post-promotion contains "DSA sub-types: algo (graph/DP/two-pointer/interval) + systems-flavored (LRU/rate-limiter/scheduler)" |
| §2 ML Practitioner 4-dim rubric: (1) Problem framing & model selection -- ML vs heuristic, ranking 正负样本, regression GT, offline metric ↔ business; (2) Featurization -- dense/sparse 数量, feature importance (SHAP/permutation/gradient), 防 overfit (reg/dropout/early-stop/CV); (3) Deployment -- offline→online (TF Serving / Triton / batched), QPS 上限, p99 budget, run-time fallback, cold-start; (4) Evaluation & online -- A/B sample size + power + MDE + multiple comparison + guardrail (latency/fairness) | id=83 §2 char 1500-2900 | **The substantive core of doc 83.** `kg://301` (project-deep-dive-round) §"ML Practitioner 4-dim rubric" subsection. **§5 promotion candidate (HIGH value)**: this is the most recurring rubric at L5+/L6 MLE rounds (Meta, Google, Pinterest, Uber, DoorDash all probe these 4 dims). Cross-company near-certain. | `SELECT description FROM framework_nodes WHERE id=301` -- post-promotion contains the 4 named dimensions verbatim with sub-bullets (especially "guardrail metric latency/fairness" + "MDE / power / multiple comparison" + "feature importance SHAP/permutation/gradient") |
| §2 ML Practitioner 高频题型 sample (Detect unsafe content + Ad CTR + Homefeed Lightweight Ranking) | id=83 §2 trailer char 2900-3050 | the 3 题型 are Pinterest-specific composition recipes -- each maps to a CONCEPTS-plan S5 row: "Detect unsafe" → doc 74 → S5 on `kg://<new fusion node>` + `kg://<new asym-thresholds>` (CONCEPTS §5 cand 3+4); "Ad CTR" → CONCEPTS S5 on `kg://259` + `kg://262`; "Homefeed Lightweight Ranking" → CONCEPTS S5 on `kg://255` + `kg://258`. **Already covered by CONCEPTS plan**. | (CONCEPTS plan §2 / §4.5 -- those S5 rows are the substantive home of the 3 题型) |
| §3 ML SD pre-question 4-clarify (候选类型 / responsive 程度 / 用户量 + corpus + 单用户 reco / latency tier 1ms 1s 1min 1h) | id=83 §3 sub-bullet char 3050-3300 | `kg://299` (ml-system-design-round) §"pre-question 4-clarify protocol". **§5 promotion candidate (HIGH value)**: clarify-first is universal but the 4 specific axes (类型 / responsive / scale / latency tier) are the canonical Pinterest/Patrick-Halina framework -- generic enough to cross-company. | `SELECT description FROM framework_nodes WHERE id=299` -- post-promotion contains "4-clarify: 候选类型 / responsive (near-realtime vs batch) / 用户量+corpus+单用户 reco 数 / latency tier 1ms-1s-1min-1h" |
| §3 ML SD 核心议题 5-axis (training cadence / retrieval HNSW-LSH-FAISS-two-tower / ranking GBDT-DNN-Transformer / serving monolith-microservice-cache-fallback / monitoring data-drift+model-drift) | id=83 §3 axis-list char 3300-3700 | `kg://299` §"5-axis core agenda" (or sub-list). Each axis maps to a canonical: training cadence → `kg://267` (feature-store) + `kg://268` (lambda/kappa); retrieval → `kg://253` (ANN HNSW IVF PQ); ranking → `kg://259` (feature-cross) + `kg://257` (LtR); serving → `kg://273` (p99-budget); monitoring → `kg://139` (monitoring) + new `kg://<drift-monitoring>` from CONCEPTS plan. **§5 promotion candidate**: extend `kg://299` with the 5-axis enumeration as the standard sub-headings of any ML SD answer. | (queries above) -- kg://299 post-promotion contains the 5 named axes; each axis has a canonical kg:// child link |
| §3 ML SD 4 高频 SD 题 (Homefeed near-realtime candidate gen / Homefeed responsive personalized reco / Pinterest Search ranking / Ads Funnel retrieval→ranking→auction→pacing) | id=83 §3 题型-list char 3700-3950 | these 4 are **Pinterest-specific SD prompts**, mirroring the 7 sd:// writeups in TOC plan §"SD module" (which delegate to CONCEPTS docs). Cross-link: each 题 maps to a `sd://pinterest-<slug>` already in TOC plan §3 skeleton. **No new node needed** -- the prompts survive via TOC's SD module table + CONCEPTS's deep-dive prose. | TOC plan §3 "## SD module" 7-row table; `grep -c "sd://pinterest-" <merged-hub-content>` -- expect 7 sd:// links |
| §3 ML SD 面试官特别看的 4-point (infra→modeling 单向影响 / UI→labels 单向影响 / 失败模式 debug / 最近读的 ML paper / 行业 idea) | id=83 §3 trailer char 3950-4250 | each maps to canonical: infra→modeling → `kg://299` §"infra-modeling coupling" 1-liner; UI→labels → `kg://299` §"label-collection through UI" 1-liner; 失败模式 debug → `kg://299` §"failure-mode debug" (traffic shadow / online eval / counterfactual / user-control); recent paper / industry idea → `kg://301` §"recent-paper readiness" 1-liner. **§5 promotion candidate**: extend `kg://299` description with these 4 sub-points (high-value because they're easy to forget under interview pressure). | `SELECT description FROM framework_nodes WHERE id=299` -- post-promotion contains the 4 sub-points; `SELECT description FROM framework_nodes WHERE id=301` -- contains "recent paper ready 5-min" 1-liner |
| §3 ML SD 资源 (Pixie blog + HNSW paper + Two-Tower YouTube paper + User Sequence Modeling for Pinterest Ads blog URLs) | id=83 §3 资源 char 4250-4500 | the 4 URLs are Pinterest-specific resource bundle. Same shape as doc 39's "Pinterest 相关" row above. **Migrates to the merged hub doc's §"Resources" subsection** (one of the 7 URLs from doc 39 + these 4 new ones = consolidated 11-link bundle). **Causal-proof gate**: the Pixie blog + User-Sequence-Modeling blog URLs are Pinterest-specific (not generic textbook); their loss is unrecoverable from canonical nodes. | `grep -c "pixie\|user-action-sequence-modeling" <merged-hub-doc-content>` -- expect 1 each post-archive |
| §4 Competency / HM (45 min): deep-dive 5-min/15-min two versions / challenge 2 (技术失误 + 协作失误) / impact framing (business 数字 + ML 指标双线) / HM 隐线 (协作 + give feedback + receive feedback) + 1 collaborator story + 1 mentor story + Trap (deep-dive 只技术不决策权 / challenge 只发生不学到 / 全说 "我们" 不说 "我") | id=83 §4 char 4500-5100 | `kg://300` (behavioral-bq-round) §"competency/HM round playbook" subsection + `kg://301` (project-deep-dive-round) §"5-min/15-min two-version prep" addendum. **§5 promotion candidate (medium-high value)**: extend `kg://300` description with the 4-axis HM rubric (deep-dive / challenge-2 / impact framing / HM 隐线) + the 3 traps (decision-rights / learned-from / I-vs-we pronoun). Cross-company: every L5+ role has an HM round with this shape. | `SELECT description FROM framework_nodes WHERE id IN (300, 301)` -- post-promotion contains "deep-dive 5-min + 15-min two versions"; kg://300 contains the 4-axis rubric + 3 traps |
| §5 共通 pattern 5-row 翻车 vs 做对 table (clarify / Tradeoff first / Real-world flavor / Pinterest 语境 / Self-critical) | id=83 §5 char 5100-5400 | the 5-row table is **generic interview-craft** (the "Pinterest 语境" row is the only Pinterest-flavored axis -- substitutes for any company's product surface). **§5 promotion candidate**: extend `kg://297` (standard-4-round-mle-vo) §"cross-round common patterns" with the 5-row 翻车-做对 table (substituting "company-specific product context" for "Pinterest 语境"). High-value, generic enough. | `SELECT description FROM framework_nodes WHERE id=297` -- post-promotion contains the 5-axis cross-round 翻车-做对 table |
| §6 60-second pre-exit cheat sheet 4-bullet (clarify-or-high-level opening / 2+ tradeoffs / company-product context / surface failure mode) | id=83 §6 char 5400-5500 | **§5 promotion candidate**: extend `kg://297` §"in-round self-check" with the 4-bullet checklist. Generic. | `SELECT description FROM framework_nodes WHERE id=297` -- post-promotion contains "60s pre-exit self-check: clarify-opening / 2+ tradeoffs / product context / surface failure mode" |
| Trailer: "prep call (4/29 14:00 PT) 要确认的事" 5-bullet (onsite 具体日期 / 5 场顺序 / take-home 有无 / 面试官 ML team 哪个组 / HM 是谁) | id=83 trailer char 5400-5522 | **drop** -- ephemeral 2026-04-28 prep-call agenda, action items resolved (Pinterest is `status=onsite`, recruiter call past, interviewer info either captured in `interview_events` or no longer relevant). | `SELECT * FROM interview_events WHERE company_id=29` -- if interviewer info is needed it lives here, not in doc 83 |

**Causal-proof gate for id=83**: archive cannot proceed until (a) the 4-dim ML Practitioner rubric (Problem framing / Featurization / Deployment / Evaluation) lands in `kg://301` description -- this is the highest-value single piece of substantive content in the entire prep subset; (b) the ML SD 4-clarify + 5-axis + 4-面试官-watching extensions land in `kg://299` description; (c) the HM 4-axis rubric + 3 traps land in `kg://300` description; (d) the §3 resource URLs (Pixie blog + user-action-sequence-modeling blog) are captured in the merged hub doc's `## Resources` subsection. Without (a), the 4-dim rubric is unrecoverable from any single canonical node (each axis exists piecewise, but the integrated rubric does not).

---

## §3 Skeleton preview

The **prep half** of the merged Pinterest hub doc (decision (b) from TOC plan §3: new `hub_doc` row). The TOC plan owns the LC + BQ + SD-module sections; the CONCEPTS plan owns the per-KG-node Pinterest-flavour S5 rows (and any deep-dive SD writeup subsections referenced via `sd://pinterest-<slug>`); this plan's §3 half is the **loop-narrative + resources + per-round expectations** subsections.

> **Cross-plan integration**: the apply seed (`scripts/_archive_pinterest_2026-05-10.py`, single-shot, all 3 subsets) consolidates §3 from all 3 plans into one merged markdown. This §3 skeleton shows the **prep half** only -- subsections that the prep plan owns. Section order in the final hub doc:
>
> 1. `## Loop Structure (5-round VO)` -- prep plan (this half) + TOC plan cross-link
> 2. `## R1 LC + R2 LC` -- TOC plan owns
> 3. `## SD module (Pinterest-flavour wraps)` -- TOC plan owns (delegates to CONCEPTS prose)
> 4. `## R3 ML Practitioner & R4 ML SD round expectations` -- **prep plan owns** (this half)
> 5. `## R5 Competency / HM round expectations` -- **prep plan owns** (this half)
> 6. `## BQ -- 5 Q × 2-3 stories matrix` -- TOC plan owns
> 7. `## Resources (Pinterest-specific link bundle)` -- **prep plan owns** (this half)
> 8. `## Schedule / 行政` -- TOC plan owns

```markdown
<!-- HUB_REORG_20260510_B4A_PINTEREST_PREP_HALF -->

## Loop Structure (5-round VO)  <!-- prep plan + TOC cross-link -->

- [Pre-loop: Recruiter call + Tech screen](kg://298) -- `pre-loop-recruiter-and-tech-screen` (60 min phone screen: ~10-15 min ML Project Discussion + ~15-20 min 3 ML Fundamentals + ~25-30 min 1 Coding LC Medium-Hard)
- [Standard 4-round MLE Virtual Onsite](kg://297) §"Pinterest 5-round 变体" -- **2× DSA 45 min + 1× ML Practitioner 60 min + 1× ML System Design 60 min + 1× Competency/HM 45 min, no particular order, ~4h 10m total**
- [ML System Design Round playbook](kg://299) -- detailed expectations + 4-clarify protocol + 5-axis agenda below
- [Behavioral / BQ Round playbook](kg://300) -- detailed expectations + 4-axis HM rubric below
- [Project Deep-Dive Round playbook](kg://301) -- detailed expectations + 4-dim ML Practitioner rubric below

环境 (Pinterest-specific): **Google Meet + CoderPad，无 compiler**。Python / Java / C++ 任选（面试官最熟悉这三种）。Code-pad 注意事项参 [kg://281](kg://281) §"CoderPad 模式" + [kg://276](kg://276) clarify-restate-before-typing。

## R3 ML Practitioner & R4 ML SD round expectations  <!-- prep plan owns -->

### R3 ML Practitioner (60 min) — 4-dim rubric

面试官会逐一钻这 4 个评估维度（参 [kg://301](kg://301) §"4-dim ML Practitioner rubric"，本节是 Pinterest 落地版）:

1. **Problem framing & model selection**: 为什么要 ML（vs heuristic / rule-based / 历史最优解）/ 怎么 frame（ranking → 正负样本怎么造；regression → ground truth 怎么得到）/ 选了什么 model + 跟其它候选的 tradeoff / offline metric 跟 business objective 怎么对齐。
2. **Featurization**: dense / sparse 数量 / feature importance (SHAP / permutation / gradient) / 训练集 vs feature 维度怎么防 overfit (reg / dropout / early-stop / CV) / **trap: 不能只说"我加了正则" -- 要讲为什么这个 reg 合适**。
3. **Deployment**: offline trained → online serve (TF Serving / Triton / batched inference) / QPS 上限 / p99 budget / run-time 缺 feature 怎么 fallback (default / impute / parent feature) / cold-start 怎么处理 (content-based / popularity prior / two-tower 上 sample-efficient retrieval -- 详 [kg://260](kg://260) cold-start).
4. **Evaluation & online**: A/B sample size + power + MDE + multiple comparison correction / guardrail metric (latency 不能升 / fairness 不能降 -- 详 [kg://273](kg://273) p99-budget + CONCEPTS plan 的 fairness 新节点).

Pinterest 高频题型 sample (3 题，详细配方见 CONCEPTS half + S5 rows):

- **Detect unsafe content at Pinterest scale** -- multimodal fusion (kg://TBD-multimodal-fusion) + asymmetric thresholds (kg://TBD-asym-thresholds) + HIL queue. `node_company_tags.company_attribute='pinterest-unsafe-late-fusion-default'` + `'pinterest-unsafe-csam-rollback-redline'`.
- **Ad CTR prediction** -- feature-cross ([kg://259](kg://259)) + calibration ([kg://262](kg://262)). Pinterest 落地: `sd://pinterest-ad-ctr` (CONCEPTS).
- **Homefeed Lightweight Ranking** -- latency-bound, 不能上 cross-encoder. Multi-stage funnel ([kg://255](kg://255)) + MMoE ([kg://258](kg://258)). Pinterest 落地: `sd://pinterest-pin-ranking` (CONCEPTS).

### R4 ML System Design (60 min) — 4-clarify + 5-axis agenda

永远先 gather requirement (4-clarify protocol; 参 [kg://299](kg://299) §"pre-question 4-clarify"):

- 候选类型 / 推荐场景?
- 多 responsive (near-realtime vs batch)?
- 用户量 / corpus 大小 / 单用户 reco 数?
- Latency 目标 (1 ms / 1 s / 1 min / 1 h — 不同 tier 完全不同架构)

核心议题 5-axis (每个都要能讲 pros / cons / 何时不用; 参 [kg://299](kg://299) §"5-axis core agenda"):

- Training cadence: online vs nightly batch -- 详 [kg://267](kg://267) feature-store + [kg://268](kg://268) lambda/kappa
- Retrieval: HNSW / LSH / FAISS / Two-Tower -- 详 [kg://253](kg://253) ANN-HNSW-IVF-PQ + [kg://252](kg://252) two-tower
- Ranking: GBDT vs DNN vs Transformer -- 详 [kg://257](kg://257) LtR + [kg://259](kg://259) feature-cross + [kg://258](kg://258) MMoE
- Serving: monolith vs microservice / cache 策略 / fallback path -- 详 [kg://273](kg://273) p99-budget
- Monitoring: data drift / model drift / online vs offline metric divergence -- 详 [kg://139](kg://139) monitoring + CONCEPTS plan's new `kg://TBD-drift-monitoring`

Pinterest 高频 SD 题 4 道 (详 TOC plan §"SD module" 表; 每条对应 sd:// 写法):

- Homefeed near-realtime candidate gen → `sd://pinterest-embeddings`
- Homefeed responsive personalized recommendation → `sd://pinterest-pin-ranking`
- Pinterest Search ranking → `sd://pinterest-pins-search`
- Ads Funnel (retrieval → ranking → auction → pacing) → `sd://pinterest-ad-ctr` + CONCEPTS Funnel writeup

面试官特别看的 4 点 (参 [kg://299](kg://299) §"interviewer-watching 4-points"):

- infra 选择如何影响 modeling capability (例: feature store delay → 不能用最新行为)
- product UI 如何影响 label gathering (impression / click / save / repin 是不同强度的 implicit feedback)
- 失败模式: bad reco 怎么 debug (traffic shadow / online eval / counterfactual / 用户 control 接口)
- 最近读的 ML paper / 行业 idea — 准备 1-2 个能讲 5 分钟的 (参 [kg://301](kg://301) §"recent-paper readiness")

## R5 Competency / HM (45 min) round expectations  <!-- prep plan owns -->

ML leader 跟你聊 background / passion / 团队风格 / 怎么 handle challenge. 4-axis rubric (参 [kg://300](kg://300) §"competency/HM playbook"):

- **Deep-dive 项目**: 你的 role / technical challenge / 决策 / impact (具体数字) / 学到什么. **准备 5-min short + 15-min long 两个版本** (参 [kg://301](kg://301) §"5-min/15-min two-version prep").
- **Challenge / 失误 ×2**: 一个技术失误 (e.g., 上线后发现 metric 选错) + 一个协作失误 (e.g., 跟 PM 沟通 misalignment). 每个都讲 *学到什么 + 现在怎么做* (参 [kg://249](kg://249) failure-and-difficult-feedback + [kg://251](kg://251) STAR-T-STARR).
- **Impact framing**: business 数字 + ML 指标双线 ("CTR +X% / 直接收入 $Ym / latency 不变 / 之后被 N 个团队 adopt") -- 参 [kg://246](kg://246) project-ownership-end-to-end.
- **HM 隐线**: 你跟同事工作时是什么样? (协作 / give feedback / receive feedback). 准备 1 个 collaborator story (cross-link [S6](db://29#s6) `conflict-resolution-cross-team` cluster) + 1 个 mentor story (cross-link [kg://248](kg://248) technical-leadership-mentorship).

**3 traps (HM round-specific)**:

- Deep-dive 时只讲技术不讲 **决策权** (谁拍板 / 你拍板 / 你建议但别人拍板 -- 3 种角色要分清).
- 讲 challenge 时只讲 *发生了什么* 不讲 *学到什么*.
- 提到 team 时全说 "我们" 不说 "我" (混淆 individual contribution vs team output).

## Resources (Pinterest-specific link bundle)  <!-- prep plan owns -->

**Recruiter David 推荐的资源** (2026-04-08 recruiter call):

- [Pinterest Engineering Blog](https://medium.com/pinterest-engineering) -- 主要的 ML 系统 + 产品 blog 源
- [Pinterest Publications](https://labs.pinterest.com/publications) -- 学术 paper 索引
- [Pinterest Open Source (GitHub)](https://github.com/pinterest) -- 工具 + 库
- [Pinterest Tech Stack (StackShare)](https://stackshare.io/pinterest/pinterest) -- 技术栈一览
- [Pinterest Careers & Life](https://www.pinterestcareers.com/) + [PinFlex 混合办公](https://www.pinterestcareers.com/pinflex/) -- 公司文化
- [Patrick Halina's Blog](https://www.patrickhalina.com/) -- Pinterest ML Manager 的面试技巧，**ML SD round 的官方 framework**: http://patrickhalina.com/posts/ml-systems-design-interview-guide/

**ML SD round 具体读物** (从 doc 83 §3 资源整合):

- [Pixie blog (Pinterest Recommendation System update)](https://medium.com/pinterest-engineering/an-update-on-pixie-pinterests-recommendation-system-6f273f737e1b)
- [HNSW paper (Malkov & Yashunin 2016)](https://arxiv.org/abs/1603.09320)
- [Two-Tower (YouTube paper, Covington et al. 2016)](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45530.pdf)
- [User Action Sequence Modeling for Pinterest Ads (Pinterest Eng blog)](https://medium.com/pinterest-engineering/user-action-sequence-modeling-for-pinterest-ads-engagement-modeling-21139cab8f4e)

**通用刷题平台**:

- [LeetCode](https://leetcode.com/) -- Medium ~ Hard
- [HackerEarth](https://www.hackerearth.com/) / [CareerCup](https://www.careercup.com/) / [GeeksforGeeks](https://www.geeksforgeeks.org/) / [TopCoder](https://www.topcoder.com/)

(每条点击在浏览器新开页面; 这些链接是 Pinterest-specific bundle 的 hub doc 唯一保留位置 -- 不进入 kg:// 节点 description, 因 per-company URL bundle 不是 KG 知识本体。)
```

**Skeleton renders check**: All URIs (`kg://N`, `db://N`, `cd://N`, `sd://<slug>`) follow existing CompanyDrawer.Notes drawer-link routing. The `kg://TBD-multimodal-fusion` + `kg://TBD-asym-thresholds` placeholders for the 3-题型 unsafe-detection link are flagged TODOs that resolve when CONCEPTS plan's §5 cand 3 / cand 4 (multimodal-fusion-strategies + asymmetric-thresholds-and-hil-queue) land. **Apply gate**: archive blocks until either (a) those CONCEPTS new nodes land OR (b) the placeholders are explicitly accepted in the merged skeleton.

---

## §4 Hard-archive checklist

Apply order matters. Each step is a discrete artifact; if any fails, abort and roll back via `restore.sql`.

> **Cross-plan ordering**: Pinterest prep archive should NOT run before sister plans T-P0-810 (TOC) and T-P0-811 (CONCEPTS) are also reviewed and approved. Reasons:
> 1. The §3 skeleton above is only the prep half -- the surviving hub doc must contain all 3 halves merged.
> 2. Doc 49's substantive content (LC 1851 S4 tag + mode 速记) depends on the TOC plan's §4.5 INSERT row for problem_id=144 having landed (causal-proof gate).
> 3. Doc 83's "3 题型 unsafe-detection" link depends on the CONCEPTS plan's new fusion + asym-thresholds nodes having landed.
> 4. The Pinterest-specific resource URL bundle (11 links) lives in the merged hub doc's `## Resources` subsection -- this plan contributes the prep-side content but the hub doc insertion is single-shot from the consolidated apply seed.
> Therefore §4 below is **partial** -- the actual apply seed (`scripts/_archive_pinterest_2026-05-10.py`, single-shot, all 3 subsets) consolidates §4 from all 3 plans.

### 4.1 DB backup (shared, runs once)

```bash
cp data/mle_prep.db data/mle_prep.db.bak.$(date -u +%Y%m%dT%H%M%SZ)_pre_pinterest_archive
```

(Identical to TOC plan §4.1 and CONCEPTS plan §4.1; runs once for the consolidated apply seed.)

### 4.2 DELETE rows from `company_documents` -- prep subset

```sql
-- prep subset: all 3 docs deleted (no rewrite-in-place since the new hub_doc INSERT covers the surviving content)
DELETE FROM company_documents
WHERE id IN (39, 49, 83);
```

**Hold list** (do NOT delete until contingent gates clear):

- id=39 -- holds on (a) Pinterest research-resource link bundle (7 URLs) landing in merged hub doc's `## Resources` subsection; (b) optionally on `kg://297` 5-round variant + `kg://298` ML Fundamentals 6-topic + `kg://281` code-pad-environments-matrix promotions (softer holds; if deferred, the loss is craft-loss not claim-loss).
- id=49 -- holds on (a) LC 1851 S4 row from TOC plan §4.5 having landed; (b) the LC 1851 mode 速记 (offline sort + heap-by-length + r<q pop) landing in EITHER `kg://291` description OR `problems.notes` for problem_id=144. If neither lands, the 5-step template is unrecoverable.
- id=83 -- holds on (a) `kg://301` 4-dim ML Practitioner rubric promotion; (b) `kg://299` 4-clarify + 5-axis + 4-watching extensions; (c) `kg://300` 4-axis HM rubric + 3 traps; (d) §3 resource URLs (Pixie + user-action-sequence-modeling) landing in merged hub doc's `## Resources` subsection. (a) is the strongest gate.

### 4.3 INSERT new `hub_doc` for Pinterest (decision (b), shared with TOC + CONCEPTS plans)

```sql
INSERT INTO company_documents (company_id, doc_kind, title, content, content_hash, source_path, created_at, updated_at)
VALUES (29, 'hub_doc', 'Pinterest Senior MLE -- Prep Index',
        '<MERGED §3 skeleton (TOC + CONCEPTS + prep halves)>',
        '<sha256 of merged skeleton>', NULL,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

(Same INSERT as TOC plan §4.3 / CONCEPTS plan §4.4; content is the merged TOC + CONCEPTS + prep skeleton; content_hash recomputed once across all 3 halves. This plan contributes the §"Loop Structure" + §"R3/R4 expectations" + §"R5 expectations" + §"Resources" subsections.)

### 4.4 UPDATE on existing kg nodes -- description promotions (prep-plan-driven; ~4 rows)

The prep plan does NOT write any S5 INSERTs (CONCEPTS owns those). It DOES contribute description text to 4-5 existing kg nodes via the §5 promotions below. The single-shot apply seed runs an UPDATE on each:

```sql
-- kg://297 standard-4-round-mle-vo: 5-round variant + cross-round common patterns + 60s self-check
UPDATE framework_nodes
SET description = description || '

## 5-round variant (DSA × 2)
Used by Pinterest (id=29) and similar production-MLE companies. Shape: 2× DSA 45 min + 1× ML Practitioner 60 min + 1× ML System Design 60 min + 1× Competency/HM 45 min, no particular order. The 5-round variant differs from standard 4-round by splitting coding into 2 sub-rounds: one algo-flavored (graph / DP / two-pointer / interval), one systems-flavored (LRU / rate-limiter / scheduler).

## Cross-round common patterns (5-axis 翻车 vs 做对)

| 维度 | 做对 | 翻车 |
|---|---|---|
| Clarify before coding | 3-5 clarifying questions; write constraints down | Assume default spec, dive in |
| Tradeoff first | Every choice names "chose A, gave up X" | "I chose X because X is good" |
| Real-world flavor | Scale / latency / cost / monitoring | Math + model architecture only |
| Company-product context | Use the company''s product vocab (Pin / Board / Homefeed) | Generic "user / item" placeholders |
| Self-critical | Surface weakness + improvement spontaneously | "This is the perfect approach" |

## 60-second pre-exit self-check (any round)
1. First sentence: clarification or high-level? (Neither = restart)
2. Stated ≥ 2 tradeoffs?
3. Used the company-product vocab?
4. Surfaced ≥ 1 failure mode / limitation?'
WHERE id = 297;

-- kg://298 pre-loop-recruiter-and-tech-screen: 60-min phone screen 3-block template + ML Fundamentals 6-topic catalog
UPDATE framework_nodes
SET description = description || '

## 60-min phone-screen 3-block template
- ~10-15 min: Intro + ML Project Discussion (one deep-dive project, candidate-led)
- ~15-20 min: 3 random ML Fundamentals questions (catalog below)
- ~25-30 min: 1 Coding Challenge (LC Medium ~ Hard + follow-up + edge cases)

## ML Fundamentals topic catalog (Pinterest official Prep Guide)
1. Logistic Regression -- 原理 / 损失函数 / 梯度
2. Variance / Bias tradeoff -- under-fit vs over-fit
3. Regularization L1 vs L2 -- 为什么有效 / 如何选择
4. Decision Trees -- 分裂标准 / 剪枝 / ensemble (RF / GBDT / XGBoost)
5. Convex Functions -- 凸优化为什么重要 / 非凸怎么办
6. Model Evaluation -- precision / recall / F1 / AUC-ROC / cross-validation'
WHERE id = 298;

-- kg://299 ml-system-design-round: pre-question 4-clarify + 5-axis core agenda + 4-watching points + infra-modeling coupling
UPDATE framework_nodes
SET description = description || '

## Pre-question 4-clarify protocol (Patrick Halina framework)
1. 候选类型 / 推荐场景? (Pin / Ad / Search query / Notification)
2. Responsive (near-realtime vs batch)?
3. 用户量 / corpus 大小 / 单用户 reco 数?
4. Latency tier (1ms / 1s / 1min / 1h -- different tier completely different architecture)

## 5-axis core agenda (each axis: pros / cons / when not to use)
- Training cadence: online vs nightly batch
- Retrieval: HNSW / LSH / FAISS / Two-Tower (recall vs latency vs index-update cost)
- Ranking: GBDT vs DNN vs Transformer (latency / interpretability / feature scale)
- Serving: monolith vs microservice / cache / fallback path
- Monitoring: data drift / model drift / online vs offline metric divergence

## Interviewer-watching 4-points
- Infra → modeling: how infra choice limits modeling capability (e.g., feature-store delay → can''t use most-recent behaviour)
- UI → labels: product UI shapes label-gathering (impression / click / save / repin = different implicit-feedback strengths)
- Failure-mode debug: bad reco → traffic shadow / online eval / counterfactual / user-control interface
- Recent paper / industry idea: prep 1-2 papers you can present in 5 min'
WHERE id = 299;

-- kg://300 behavioral-bq-round: competency/HM round 4-axis rubric + 3 traps
UPDATE framework_nodes
SET description = description || '

## Competency / HM round 4-axis rubric (45 min)
1. **Deep-dive project**: prep 5-min short + 15-min long two versions. Role / technical challenge / decision / impact (concrete numbers) / what learned.
2. **Challenge × 2**: one technical failure (e.g., picked wrong metric and shipped) + one collaboration failure (e.g., PM misalignment). Each: what you learned + what you do now.
3. **Impact framing**: business numbers + ML metric dual-line ("CTR +X% / direct revenue $Ym / latency unchanged / N teams adopted after").
4. **HM 隐线** (what you''re like with teammates): 1 collaborator story + 1 mentor story.

## 3 traps (HM round-specific)
- Deep-dive without 决策权 distinction: clarify "I decided" vs "I recommended, X decided" vs "team decided"
- Challenge without 学到 part: only describe what happened, not what you learned
- "我们" vs "我" pronoun: blurring individual contribution vs team output'
WHERE id = 300;

-- kg://301 project-deep-dive-round: 4-dim ML Practitioner rubric + 7-bullet ML Project topic coverage + 5-min/15-min two-version prep
UPDATE framework_nodes
SET description = description || '

## 4-dim ML Practitioner rubric (60 min ML Practitioner round / project deep-dive)
1. **Problem framing & model selection**: ML vs heuristic / ranking 正负样本 / regression GT / offline metric ↔ business objective alignment.
2. **Featurization**: dense/sparse count / feature importance (SHAP / permutation / gradient) / 防 overfit (reg / dropout / early-stop / CV). Trap: "我加了正则" without saying *why this regularizer fits*.
3. **Deployment**: offline → online serve (TF Serving / Triton / batched) / QPS ceiling / p99 budget / run-time feature fallback (default / impute / parent) / cold-start.
4. **Evaluation & online**: A/B sample-size + power + MDE + multiple-comparison correction + guardrail metric (latency must not rise / fairness must not drop).

## 7-bullet ML Project topic coverage (Phone Screen / R3)
- Project background & business goal
- ML method choice + why (tradeoff vs candidates)
- Your specific contribution and role
- Data processing & feature engineering
- Model training & evaluation metrics
- Deployment & online effect
- Challenges encountered & how resolved

## 5-min short + 15-min long two-version prep
Both must hit role / decisions / impact / what learned, but 15-min version adds: deeper failure-mode analysis + follow-up team adoption + alternatives considered.'
WHERE id = 301;
```

(The 5 UPDATEs above are the prep plan's net DB-write footprint. No S4 / S5 / S6 INSERTs originate here. Idempotency: the apply seed must check whether the appended marker (e.g., `## 5-round variant (DSA × 2)`) already exists in `description` before re-appending -- prevents duplicate appends on re-run. Recommended sentinel: a unique header string per UPDATE that the seed greps for.)

### 4.5 Seed script moves

The prep subset has 4 seed scripts to archive:

```bash
mkdir -p archive/seed_scripts/2026-05-10/pinterest-prep/
git mv scripts/_add_pinterest_hr_prep_2026-04-30.py    archive/seed_scripts/2026-05-10/pinterest-prep/
git mv scripts/_add_pinterest_vo_2026-05-05_06.py      archive/seed_scripts/2026-05-10/pinterest-prep/
git mv scripts/seed_pinterest_prep.py                  archive/seed_scripts/2026-05-10/pinterest-prep/
git mv scripts/seed_pinterest_onsite_prep.py           archive/seed_scripts/2026-05-10/pinterest-prep/
```

**Do NOT move**:
- `scripts/seed_pinterest_companies_row.py` -- seeds the surviving `companies.id=29` row (S2 owned by TOC plan)
- `scripts/seed_pinterest_lc_problems.py` -- seeds the `problems` table rows referenced by S4 tags (TOC plan-owned)
- `scripts/seed_pinterest_lc_voice_refactor_465_1723.py` -- targets `problems.notes` for problem_id=214 + 1067 (LC 465 + 1723), unrelated to prep subset
- `scripts/seed_pinterest_lc_must_do_sd_drawer_links.py` -- targets TOC subset (id=47/66 drawer links); TOC plan owns its move
- `scripts/seed_pinterest_card_index_lc_426_1293_20260506.py` -- targets TOC subset (id=66 card index); TOC plan owns its move

Enumerate every Pinterest seed via `grep -l "company_id\s*=\s*29\|Pinterest" scripts/seed_*.py scripts/_*.py` and cross-check against the union of TOC plan §4.7 + CONCEPTS plan §4.6 + this plan §4.5 to ensure full coverage. The 3 lists together must cover all Pinterest-touching seed scripts. Any leftover seed is a hold reason.

### 4.6 restore.sql generation

Generate `archive/company_internalized/pinterest_2026-05-10/restore.sql` containing (prep subset):

- INSERT statements for all 3 prep docs (id=39, 49, 83) with original `content`, `content_hash`, `source_path`, `doc_kind`
- UPDATE statements to REVERT the 5 description-appends on kg://297 / 298 / 299 / 300 / 301 (each UPDATE captures the pre-append description; reverse-UPDATE truncates back to that text)

Same artifact path as TOC plan §4.8 and CONCEPTS plan §4.7 -- restore.sql is unified across all 3 subsets. Generated by the apply seed BEFORE any DELETE / UPDATE runs.

### 4.7 Sentinel idempotency

Apply seed prints `[SKIP]` on second run. Sentinels (prep subset):

- No row exists in `company_documents` with id IN (39, 49, 83)
- Each of kg://297 / 298 / 299 / 300 / 301 has its description containing the unique header string (sentinel marker) appended by §4.4 (greppable, e.g., `## 5-round variant (DSA × 2)` for kg://297, `## 60-min phone-screen 3-block template` for kg://298, `## Pre-question 4-clarify protocol` for kg://299, `## Competency / HM round 4-axis rubric` for kg://300, `## 4-dim ML Practitioner rubric` for kg://301)
- The merged Pinterest hub doc contains the §"Resources" subsection with the 11 Pinterest-specific URLs (Pinterest Engineering Blog / Publications / GitHub / StackShare / Careers / PinFlex / Patrick Halina blog + Pixie blog + HNSW arxiv + Two-Tower YouTube paper + User Action Sequence Modeling blog)

### 4.8 Smoke checks

- `python scripts/audit_uri_consistency.py` -- 0 ERRORs. All `kg://TBD-*` placeholders either resolved or in audit allowlist with TODO ticket.
- `python scripts/_audit_company_kg_internalization.py` -- Pinterest row in roll-up: S3 bytes ~= merged-skeleton size (post-archive expected: TOC half + CONCEPTS half + prep half consolidated, ~3-5 KB total for a thin hub doc; vs pre-archive 102 041 B); S4 = 34 (TOC plan-owned, prep contributes 0 new); S5 = ~16 (CONCEPTS plan-owned, prep contributes 0); S6 = 13 (TOC plan-owned, prep contributes 0); S2 ~= 150 B (TOC plan-owned trim).
- Frontend smoke (`cd src/frontend && npm run dev`, navigate to `/companies/29`): CompanyDrawer.Notes renders the merged skeleton. Spot-click on prep-plan-owned content: (a) 5 `kg://` links from `## Loop Structure` (kg://297 / 298 / 299 / 300 / 301) -- all resolve; (b) the §"R3 ML Practitioner" `kg://259` + `kg://262` cross-links resolve; (c) §"R4 ML SD" `kg://253` + `kg://252` + `kg://273` resolve; (d) the §"Resources" 11-URL bundle opens external URLs in new tabs.

---

## §5 Promotion candidates flagged for meta-prep

Patterns spotted in Pinterest prep docs that meet (or appear to meet) the >=3 P0+P1 companies threshold AND de-companiable wording. T-P1-821 (`B4-promotion`) consolidates these across all B4a plans. **The prep plan has the lightest §5 load of the 3 Pinterest plans** -- 4 recommended description extensions (all to existing nodes), 0 required new nodes. The 4 extensions are critical for causal-proof gates on doc 39 + doc 83 archive (without them, ~5 substantive rubrics become unrecoverable from any single canonical node).

### Required (description-extension promotions whose absence blocks doc 39 / 83 archive)

1. **kg://301 `meta-prep/onsite-loop-templates/project-deep-dive-round` -- 4-dim ML Practitioner rubric + 7-bullet ML Project topic coverage + 5-min/15-min two-version prep** (REQUIRED for doc 83 archive)
   - Pattern: 4-dim rubric (Problem framing & model selection / Featurization / Deployment / Evaluation & online) + 7-bullet ML Project topic coverage (背景&目标 / 方法&tradeoff / 你的贡献 / 数据&特征 / 训练&评估 / 部署&效果 / 挑战&解决) + 5-min/15-min two-version prep.
   - Companies (so far): Pinterest (doc 39 + doc 83). Cross-company: Meta L6 (ML Project deep-dive round = standard), Google L5+ (ML Practitioner round = same shape), Uber MLE (project deep-dive standard), DoorDash (model + deployment round). 3-company threshold trivially met after T-P1-821 reads other plans.
   - 1-line excerpt: "ML Practitioner / Project Deep-Dive round 4-dim rubric: problem framing (ML vs heuristic / label generation / metric ↔ business alignment) + featurization (count / importance method / overfit prevention) + deployment (online serving / QPS / latency / fallback / cold-start) + evaluation & online (A/B sizing / guardrail metric); two-version prep 5-min summary + 15-min deep-dive for HM vs IC interviewers."

2. **kg://299 `meta-prep/onsite-loop-templates/ml-system-design-round` -- pre-question 4-clarify + 5-axis core agenda + 4-watching points** (REQUIRED for doc 83 archive)
   - Pattern: Patrick-Halina-style 4-clarify (候选类型 / responsive / 用户量+corpus+单用户 reco / latency tier) + 5-axis core agenda (training cadence / retrieval / ranking / serving / monitoring) + 4-watching points (infra → modeling / UI → labels / failure-debug / recent-paper).
   - Companies (so far): Pinterest (doc 83). Cross-company: Meta ML SD (same Halina-framework descendant), Google L5+ ML SD, Anthropic / OpenAI applied AI SD, Uber / DoorDash SD. 3-company threshold trivially met.
   - 1-line excerpt: "ML SD round protocol: clarify-first 4-axis (候选 type / responsive / scale / latency tier 1ms-1s-1min-1h) → 5-axis agenda (training cadence + retrieval HNSW/two-tower + ranking GBDT/DNN + serving cache/fallback + monitoring data/model drift) → watch for 4 signals (infra→modeling coupling / UI→label-design coupling / failure-mode-debug protocol / recent-paper readiness)."

3. **kg://300 `meta-prep/onsite-loop-templates/behavioral-bq-round` -- competency/HM 4-axis rubric + 3 traps** (REQUIRED for doc 83 archive)
   - Pattern: 4-axis HM rubric (deep-dive project / challenge × 2 / impact framing dual-line / HM 隐线 = collaborator + mentor stories) + 3 traps (deep-dive 决策权 / challenge 学到 / 我们-vs-我 pronoun).
   - Companies (so far): Pinterest (doc 83). Cross-company: every L5+ HM round at Meta, Google, Pinterest, Uber, DoorDash. 3-company trivially met.
   - 1-line excerpt: "HM / Competency round 4-axis rubric: deep-dive project (5-min + 15-min versions) / challenge × 2 (technical failure + collaboration failure, each with what-learned) / impact framing (business number + ML metric dual-line) / HM 隐线 (collaborator + mentor stories); 3 traps: 决策权 distinction (decided / recommended / team-decided), challenge without learned-part, 我们-vs-我 pronoun blurring."

4. **kg://297 `meta-prep/onsite-loop-templates/standard-4-round-mle-vo` -- 5-round variant + cross-round 5-axis common patterns + 60-second pre-exit self-check** (REQUIRED for doc 39 + doc 83 archive; partially overlapping with TOC plan §5 cand 3)
   - Pattern: (a) 5-round variant shape (2× DSA 45 min + ML Practitioner 60 min + ML SD 60 min + HM 45 min, no particular order, ~4h 10m) + DSA sub-types (algo vs systems-flavored); (b) 5-axis cross-round common patterns (clarify-first / tradeoff-first / real-world flavour / product context / self-critical) 翻车 vs 做对 table; (c) 60-second pre-exit 4-bullet self-check.
   - Companies (so far): Pinterest (S2 + id=39 + id=83) + TOC plan §5 cand 3 noted. Cross-company: any production-MLE company with a 5-round loop (Snap / Roblox / Coinbase / Reddit). 3-company threshold near-certain.
   - Recommendation: T-P1-821 merges this plan's §5 cand 4 + TOC plan's §5 cand 3 + (any sibling 5-round companies found in other plans) into a single coherent kg://297 description extension.

### Recommended (description-extension promotions; lower-blocking, softer hold)

5. **kg://298 `meta-prep/onsite-loop-templates/pre-loop-recruiter-and-tech-screen` -- 60-min phone-screen 3-block template + ML Fundamentals 6-topic catalog** (RECOMMENDED for doc 39 archive)
   - Pattern: 60-min phone-screen 3-block (Intro+Project / 3 ML Fund / 1 Coding) time-budget template + ML Fundamentals 6-topic catalog (Logistic Regression / Bias-Variance / Regularization L1+L2 / Decision Trees + Ensembles / Convex / Model Evaluation).
   - Companies (so far): Pinterest (doc 39). Cross-company: Meta R0 phone screen + Google phone screen + Uber phone screen -- all 3 use the same 3-block template. 3-company near-certain.
   - 1-line excerpt: "Pre-loop phone screen 60-min: ~10-15m Intro + ML Project Discussion + ~15-20m 3 ML Fundamentals + ~25-30m 1 Coding LC Medium-Hard; ML Fundamentals catalog: Logistic Regression / Variance-Bias / Regularization L1+L2 / Decision Trees+Ensembles / Convex Optimization / Model Evaluation precision+recall+AUC+CV."

6. **kg://281 `meta-prep/code-pad-best-practices/language-choice-python-default` -- code-pad environments matrix** (RECOMMENDED; overlapping with TOC plan §5 cand 4)
   - Pattern: per-company code-pad environment list (CoderPad-no-compiler / Google-internal-CIDER / VSCode-Live-Share / Replit / etc.) + per-environment quirks affecting how to dry-run code mentally.
   - Companies (so far): Pinterest (S2 = "CoderPad no compiler"; also in doc 39 + doc 83 §1). Cross-company: Google (CIDER), Meta (CoderPad), DoorDash (CoderPad). 3-company near-certain.
   - Recommendation: T-P1-821 merges this plan's §5 cand 6 with TOC plan's §5 cand 4 (same target).

7. **kg://279 `meta-prep/code-pad-best-practices/bud-bottleneck-unnecessary-duplicated` -- BCR + 5-optimization-thoughts mnemonic** (RECOMMENDED; low priority)
   - Pattern: extend BUD description with (a) BCR (Best Conceivable Runtime) -- when matched, stop optimizing; (b) 5 named optimization thoughts (BUD / DIY / Simplify+Generalize / Base Case+Build / Data Structure Brainstorm).
   - Companies (so far): Pinterest (doc 39). Cross-company: CTCI is the canonical reference; generic interview-craft. 3-company easily met.
   - 1-line excerpt: "BCR (Best Conceivable Runtime) = theoretical lower bound; when matched, stop optimizing; 5-name optimization toolkit: BUD (bottleneck/unnecessary/duplicated) + DIY (manual + reverse-engineer) + Simplify&Generalize + Base-Case&Build + Data-Structure-Brainstorm."

8. **kg://291 `meta-prep/lc-keyword-checklists/intervals-merge-meeting-rooms` -- min-interval-cover query template** (RECOMMENDED; covers doc 49's LC 1851 mode 速记 substantive content)
   - Pattern: min-interval-cover query template (offline algorithm; sort queries + intervals; min-heap keyed by interval length; push `l ≤ q`, pop `r < q`, top = answer). Applies to LC 1851 and the entire min-cover-query interval family.
   - Companies (so far): Pinterest (doc 49). Cross-company: any company with LC 1851 / LC 2402 / LC 410 in must-do (Pinterest + likely Uber / DoorDash / Snap). 3-company near-certain.
   - Recommendation: T-P1-821 extends `kg://291` description with the template (the LC 1851 problems.notes is the per-problem home; the kg://291 description is the pattern-level home).

### Recommended (cross-cutting)

9. **`meta-prep/lc-keyword-checklists/ambiguous-面经-题-identification` (or extension of kg://241 parent)** -- 4-criteria disambiguation rubric (DEFERRED; doc 49 craft-level)
   - Pattern: when a 面经 题 lacks an LC# but has hints (中文/英文 关键词 + 主题改写 hint + 难度), the 4-criteria identification rubric (关键词对齐 / 语义对齐 / 主题改写自然度 / 难度对齐) lets one cross-reference candidate LC#s. Doc 49's LC 1851 selection is the worked example.
   - Companies (so far): Pinterest (doc 49) only. **Defer** -- 1-company threshold not met; the rubric is craft-level, not claim-level.
   - Recommendation: T-P1-821 considers this in next-cycle (Pinterest is the first company with a fully written-out 候选对照 disambiguation note; if another company surfaces a similar workflow, promote then).

10. **Per-company resource link bundle convention (cross-cutting; schema/UX extension)** (RECOMMENDED for doc 39 + doc 83 archive)
    - Pattern: each company has a 5-15 link resource bundle (engineering blog / publications / GitHub / careers / interview-prep blog), currently scattered in prep_notes / company_documents. The merged hub doc's `## Resources` subsection is the per-company home.
    - Companies (so far): Pinterest (11 URLs from doc 39 + doc 83). Generic: every onsite company benefits. 3-company trivially met after T-P1-821 reads other plans.
    - Recommendation: T-P1-821 establishes a UX convention: per-company hub doc MUST have a `## Resources` subsection with engineering blog + publications + careers + interview-prep blog URLs. (No schema change needed; the convention is markdown-level.)

---

## Apply gate

User reviews §2 (causal-proof matrix -- ~30 rows across 3 docs + 5 description-promotion targets) and §5 (4 required + 6 recommended promotion candidates). Approval gate: explicit "ok 执行".

**Holds**:

- Archive of doc 83 contingent on §5 candidates 1 + 2 + 3 (kg://301 + kg://299 + kg://300 description extensions) landing first OR explicit accept-loss with restore.sql as fallback.
- Archive of doc 39 contingent on §5 candidate 4 (kg://297 5-round variant + cross-round patterns) landing AND the Pinterest resource URL bundle (7 URLs) landing in the merged hub doc.
- Archive of doc 49 contingent on (a) TOC plan §4.5 LC 1851 S4 row having landed AND (b) the LC 1851 mode 速记 landing in EITHER §5 cand 8 (kg://291 description) OR problems.notes for problem_id=144.
- Cross-plan: do NOT run the apply seed until sister plans T-P0-810 (TOC) and T-P0-811 (CONCEPTS) are also reviewed -- this prep plan contributes the §3 "Loop Structure" + "R3/R4/R5 expectations" + "Resources" subsections of the merged hub doc; the single-shot apply seed consolidates all three.
- S5 / S6 / S4 / S2 ownership invariants: this plan does NOT INSERT into S4 (TOC owns) / S5 (CONCEPTS owns) / S6 (TOC owns); only UPDATE-appends on 5 kg nodes + DELETE 3 docs + contribute hub-doc subsections.

**Discord ping**: `B4a-pinterest-prep plan ready -- docs/archive_plans/B4a-pinterest-prep_2026-05-10.md -- 3 loop-narrative docs in scope (id=39 recruiter-call prep / id=49 LC 1851 investigation / id=83 ML VO 5-round prep), 17 KB prose -> 5 kg-node description extensions (kg://297 / 298 / 299 / 300 / 301) + 11-URL Resources bundle in merged hub doc. Review §2 + §5; "ok 执行" to apply (after sister TOC + CONCEPTS plans also approved).`
