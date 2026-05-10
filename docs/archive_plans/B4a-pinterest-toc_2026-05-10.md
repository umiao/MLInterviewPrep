# B4a Pinterest-TOC -- Archive Dry-Run Plan (2026-05-10)

> Per `docs/workflow/company_internalization_protocol.md` -- the dry-run gate. WRITES NOTHING TO DB. User reviews §2 (causal-proof matrix) and §5 (promotion candidates), then explicitly approves before any apply step.

- **Company**: Pinterest (id=29, status=onsite)
- **Audit source**: `docs/audit/company_kg_internalization_audit_2026-05-10.md` (T-P1-798)
- **Subset scope**: TOC = "table-of-contents / index" docs, i.e. the navigation surface that lists / cross-links other docs and rows. The 3 docs in scope:
  - `company_documents.id=47` -- "Pinterest LC Must-Do: Review & Index" (LC patterns table + SD module table)
  - `company_documents.id=48` -- "Pinterest BQ Question Map" (BQ Q -> EX-XX mapping)
  - `company_documents.id=66` -- "Pinterest Prep Card Index" (JSON `card_index`: 10 LC pattern cards)
- **Sister plans (NOT in scope here, separate B4a tasks)**:
  - T-P0-811 (Pinterest-CONCEPTS): docs 58 / 70 / 71 / 73 / 74 / 75 (deep-dive prose)
  - T-P0-812 (Pinterest-prep): docs 39 / 49 / 83 (recruiter-call + per-LC drill + onsite prep narrative)
- **Surfaces touched here**: S2 (shared across the 3 Pinterest plans -- decision on S2 ownership noted below), S3 (3 docs), S4 (currently 0 rows -- TOC implies tags), S6 (currently 0 rows -- BQ map implies tags). S1 empty. S5 untouched (no node-tag overrides in TOC).
- **Apply gate**: "ok 执行" or equivalent green light from user. Silence is not the gate.

> **S2 ownership note**: `companies.notes` (446 B) is a single global column shared across all 3 Pinterest B4a subset plans. To avoid 3-way conflicting UPDATE plans, this TOC plan owns the S2 migration. The Pinterest-CONCEPTS and Pinterest-prep plans will explicitly mark S2 as `[OWNED-BY: B4a-pinterest-toc]` and skip the row.

---

## §1 Inventory snapshot

### S1 -- `companies.prep_notes` (pn_len = NULL)

Empty. Skip.

### S2 -- `companies.notes` (446 bytes, candidate_% = 100.0)

```
Senior ML Engineer position
TC ~$500K/yr
Hiring model: general pool, ~5 HC available, competitive Team Match required

2026-04-08 Recruiter Call Summary:
- Phone Screen (60min): ML Project Discussion + 3 ML Fundamentals questions + Coding
- Virtual Onsite (5 rounds x 60min): Coding x2, ML Deep Dive, ML System Modeling, BQ
- Environment: Google Meet + CoderPad (no compiler)
- Phone screen time TBD -- need to send 3+ availability slots to David
```

- topics = 0 (flat prose; no headings)
- kg_refs = 0
- drawer_links = 0

### S3 -- TOC subset, 3 docs / 17 072 chars / ~21 140 UTF-8 bytes

| id | chars  | bytes  | doc_kind    | source_path | title                                              |
|---:|-------:|-------:|-------------|-------------|----------------------------------------------------|
| 47 |  7 174 |  8 706 | prep_note   | (none)      | Pinterest LC Must-Do: Review & Index               |
| 48 |  2 592 |  4 138 | prep_note   | (none)      | Pinterest BQ Question Map                          |
| 66 |  7 306 |  8 296 | card_index  | (none)      | Pinterest Prep Card Index                          |

(Audit roll-up reports S3 = 102 041 B across 12 docs; the 3 TOC docs above are 21 140 B / 12 docs ~= 21 % of the total. Remaining 9 docs = CONCEPTS + prep subsets, addressed by sister plans.)

**First 200 chars per doc**:

- **id=47** "# Pinterest LC Must-Do -- Review & Index / > 14 道 must-do + 2025-11 扩展 + 若干 Pinterest custom 题。全部已完成 + 中文 notes（含 code review）。 / > 点题目标题在侧边抽屉里打开完整解法。所有'考察要点'用中文写成，保留英文术语。"
- **id=48** "# Pinterest BQ 问题到故事映射 (2025-11) / > 覆盖 Pinterest behavioral round 收集到的 5 个高频问题，每题给出 2-3 个最契合的 post-rework 故事（见 `docs/bq_behavioral_examples.json`），并用一句话点明该故事的最佳切入角度。"
- **id=66** "{ \"schema_version\": 1, \"cards\": [ { \"name_zh\": \"字符串/数字运算\", \"name_en\": \"String / Digit Arithmetic\", \"summary_zh\": \"核心：carry propagation, partition('.') 解析, shift-based 精度舍入\", \"problems\": [...] ..."

### S4 -- `problem_company_tags` (0 rows for Pinterest, candidate_% = 0)

**Currently empty**. The TOC docs (id=47 + id=66) collectively reference 26 LC numbers + 8 Pinterest-custom non-LC problems = 34 distinct problems that should be tagged to Pinterest in S4 but currently are not. **Migration target for §2.**

### S5 -- `node_company_tags` (0 rows for Pinterest)

Empty. Not touched by the TOC subset (TOC docs do not narrate per-node Pinterest flavours; that is the CONCEPTS subset's domain).

### S6 -- `behavioral_example_company_tags` (0 rows for Pinterest, candidate_% = 0)

**Currently empty**. The id=48 BQ map references 13 distinct stories (EX-01, EX-02, EX-03, EX-06, EX-08, EX-09, EX-11, EX-13, EX-14, EX-15, EX-17, EX-22, EX-23) across 5 BQ Q's, all needing S6 rows. **Migration target for §2 / §4.5.**

---

## §2 Migration matrix (4-tuple causal-proof)

One row per archive candidate. Target URIs:
- `kg://N` = `framework_nodes.id = N` (canonical)
- `db://N` = `problems.id = N` (LC + Pinterest-custom problems)
- `cd://N` = `company_documents.id = N` (only used for the surviving thin index)
- `sd://<slug>` = `meta-prep/system-design-must-knows/<slug>` framework_node by path (resolves to `kg://N` via path lookup)

Rows are grouped by surface, then by archive candidate.

### S2 -- `companies.notes` (446 bytes)

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| Senior MLE TC $500K + ~5 HC + competitive Team Match | S2 char 0-130 | **keep** in S2 (admin metadata; not loop-structure prose). Trim trailing recruiter-call summary; positions/HC stay. | `SELECT notes FROM companies WHERE id=29` -- post-archive expected ~150 B "Senior ML Engineer position / TC ~$500K/yr / Hiring model: general pool, ~5 HC available, competitive Team Match required" |
| Phone screen structure (60min: ML proj + 3 ML fund + coding) | S2 char 131-260 | `kg://298` (pre-loop-recruiter-and-tech-screen) | `SELECT description FROM framework_nodes WHERE id=298` -- 60-min phone-screen template |
| 5-round VO structure (Coding x2 / ML Deep Dive / ML SD / BQ) | S2 char 261-380 | `kg://297` (standard-4-round-mle-vo) §"5-round Pinterest variant" addendum (Pinterest is a 5-round variant: 2× DSA + ML Practitioner + ML SD + BQ) -- §5 promotion candidate to add the 5-round flavour, OR keep at `kg://297` general 4-round template + cross-link to per-round playbooks `kg://299` (ML SD) + `kg://300` (BQ) | `SELECT description FROM framework_nodes WHERE id IN (297, 299, 300)` |
| Environment (Google Meet + CoderPad, no compiler) | S2 char 381-430 | `kg://297` §"day-of logistics" / §"environment" subsection (CoderPad-no-compiler is a code-pad quirk) -- alternatively `kg://281` (language-choice-python-default) §"code-pad quirks" | `SELECT description FROM framework_nodes WHERE id IN (281, 297)` -- expect "CoderPad" / "no compiler" mention |
| "Phone screen time TBD -- need to send 3+ slots to David" | S2 char 431-446 | **drop** -- ephemeral scheduling note; supersede via `interview_events` once scheduled (and already obsolete: Pinterest is `status=onsite`, the phone-screen is past). | `SELECT name, status FROM companies WHERE id=29` -- already `onsite`; recruiter-call action item resolved |

### S3 -- per-doc rows

#### Doc id=47 "Pinterest LC Must-Do: Review & Index" (7 174 chars, prep_note)

This doc is a 3-table LC index: 14 core + 12 extension/follow-up + 9 Pinterest-custom problems, plus a 7-row SD-module table at the bottom.

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| 14 核心 must-do LC 表 (LC 332/465/815/322/282/1055/311/2402/1110/1244/410/43/642/1723) | id=47 §"核心 14 道" table | S4 tags: 14 INSERT rows in `problem_company_tags` (relevance=`core`, source=`B4a-pinterest-toc-archive-2026-05-10`, notes preserves the 考察要点 中文 hint per row) -- target `problems.id` mapped: 148 / 214 / 217 / 55 / 439 / 498 / 277 / 258 / 1066 / 199 / 265 / 135 / 237 / 1067 | `SELECT pct.problem_id, p.leetcode_id, p.title, pct.relevance, pct.notes FROM problem_company_tags pct JOIN problems p ON p.id=pct.problem_id WHERE pct.company_id=29 ORDER BY pct.problem_id` -- expect 14 core rows post-apply |
| Pattern column (Hierholzer / Bitmask DP / BFS on route graph / Knapsack / Backtrack+prev / Greedy / Sparse / 双堆 / DFS 状态 / Hash+heap / 二分答案 / 数字模拟 / Trie+TopK / 二分答案+回溯) | id=47 §"核心 14 道" Pattern col | already covered by `meta-prep/lc-keyword-checklists/*` nodes: kg://285 (BFS/DFS) / kg://286 (backtracking) / kg://284 (binary-search) / kg://287 (DP knapsack) / kg://288 (heap-topk) / kg://289 (monotonic-stack) / kg://292 (trie) / kg://293 (UF) -- the per-LC mapping survives via `problems.lc_keyword_node_id` join + S4 row | `SELECT path, title FROM framework_nodes WHERE id IN (282,283,284,285,286,287,288,289,290,291,292,293,294,295)` -- 12+ rows expected (lc-keyword-checklists family) |
| 12 扩展 / Follow-up LC 表 (LC 84/85/392/1135/1526/1564/1570/1580/1851/3229/426/1293) + 来源 col (2025-11 dump / LC X follow-up / 2026-05 user dump) | id=47 §"扩展 & Follow-up 题" table | S4 tags: 12 INSERT rows in `problem_company_tags` (relevance=`likely`, source preserves the 来源 hint, notes preserves 考察要点) -- target `problems.id`: 85/242/417/1087/236/1069/239/1070/144/157/332/451 | (same query above) -- post-apply expect 14 core + 12 likely = 26 LC rows |
| Pinterest Custom 题 表 (Escape Room id=1068, Lighthouse id=1071, Prefix-Match id=1072, Grant-Access id=1075, Pin-Connectivity id=1076, round-from-scratch id=1073, round-by-precision id=1074, LC 332 loop-followup, Reverse-Count-and-Say id=1120) | id=47 §"Pinterest Custom 题" table | S4 tags: 8 INSERT rows in `problem_company_tags` (relevance=`core`, source=`B4a-pinterest-toc-archive-2026-05-10`, notes preserves Core Pattern + 考察要点) -- target `problems.id`: 1068/1071/1072/1075/1076/1073/1074/1120. (LC 332 already in core 14 row above; "loop follow-up addendum" is a notes-level annotation on problem 148, not a separate row.) | `SELECT pct.problem_id, p.title FROM problem_company_tags pct JOIN problems p ON p.id=pct.problem_id WHERE pct.company_id=29 AND p.leetcode_id IS NULL ORDER BY pct.problem_id` -- expect 8 rows |
| System Design 模块 表 (Ad CTR / Embeddings / Chatbot Pins / Pin Ranking / Pins Search / Notification Reco / Catalog Bulk Update) -- 7 rows with `sd://pinterest-<slug>` URIs | id=47 §"System Design 模块" table | The 7 `sd://pinterest-<slug>` URIs each point to a Pinterest-flavoured SD writeup. The de-companied substrate is in `meta-prep/system-design-must-knows/*` (`kg://255` multi-stage funnel / `kg://252` two-tower / `kg://259` feature-cross / `kg://258` MMoE / `kg://253` ANN / `kg://272` geohash etc.). The Pinterest-flavour wraps go into the §3 skeleton's "## SD module" subsection as kg:// + sd:// dual-link rows. **No new SD writeups** are created in this plan -- they live in the CONCEPTS subset (T-P0-811) which owns docs 70/71/73/74/75. | `SELECT path FROM framework_nodes WHERE path LIKE 'meta-prep/system-design-must-knows/%' AND path IN ('meta-prep/system-design-must-knows/multi-stage-funnel','meta-prep/system-design-must-knows/two-tower-dual-encoder','meta-prep/system-design-must-knows/dlrm-deepfm-dcn-feature-cross','meta-prep/system-design-must-knows/mmoe-ple-multitask','meta-prep/system-design-must-knows/ann-hnsw-ivf-pq')` -- expect 5+ rows |
| BQ section (1 line: link to id=48 BQ map) | id=47 §"BQ" 1-bullet section | dropped from §3 skeleton; replaced by §"## BQ" subsection that links to S6 tags directly | (same as id=48 row below) |
| "面试准备前的最后 sanity check" 1-bullet block (recruiter call prep link + 进度 35 题 done + 来源 2026-04-12 + 2025-11 + 2026-04-15) | id=47 §"sanity check" trailer | drop -- progress-tracking prose is ephemeral, not a claim to preserve | n/a (information is in commit log + PROGRESS.md) |

#### Doc id=48 "Pinterest BQ Question Map" (2 592 chars, prep_note)

This doc is a 5-Q × 2-3-priority story matrix mapping Pinterest BQ prompts to EX-XX behavioral_examples.

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| Q1 "独立主导端到端项目" -> EX-06 / EX-23 / EX-14 (priority 1/2/3) | id=48 §"Q1" table | S6 tags (3 rows): example_id 6 / 27 / 18 paired with `company_id=29`, `company_attribute='end-to-end-ownership'`, relevance=`core`/`core`/`likely`, notes preserves 一句话 angle | `SELECT be.example_id, be.title, bect.company_attribute, bect.relevance, bect.notes FROM behavioral_examples be JOIN behavioral_example_company_tags bect ON be.id=bect.example_id WHERE bect.company_id=29 AND bect.company_attribute='end-to-end-ownership' ORDER BY bect.relevance DESC` -- expect 3 rows |
| Q2 "需求从何而来" -> EX-01 / EX-03 / EX-09 | id=48 §"Q2" table | S6 tags (3 rows): example_id 1 / 3 / 9 paired with `company_attribute='problem-framing'` | (same query, attribute = problem-framing) -- expect 3 rows |
| Q3 "stepping ahead / 主动出击" -> EX-08 / EX-01 / EX-15 | id=48 §"Q3" table | S6 tags (3 rows; EX-01 is reused with second `company_attribute='ambiguity-self-initiated'`. NOTE: `(example_id, company_id)` uniqueness assumed; if a story appears under 2 attributes, schema requires the row carry the **primary** attribute and the secondary attribute be encoded into `notes`. Verify schema.) | `SELECT bect.* FROM behavioral_example_company_tags bect WHERE bect.company_id=29 AND bect.example_id IN (1,8,19)` -- expect 3 rows; if EX-01 row carries primary='problem-framing' from Q2, notes mention secondary='ambiguity-self-initiated' |
| Q4 "受到负面反馈 / difficult feedback" -> EX-17 / EX-13 / EX-02 | id=48 §"Q4" table | S6 tags (3 rows): example_id 21 / 17 / 2 paired with `company_attribute='failure-and-difficult-feedback'`. Cross-link to `kg://249` (failure-and-difficult-feedback cluster). | `SELECT bect.* FROM behavioral_example_company_tags bect WHERE bect.company_id=29 AND bect.example_id IN (2,17,21) AND bect.company_attribute='failure-and-difficult-feedback'` -- expect 3 rows |
| Q5 "与错过 deadline 的同事合作" -> EX-11 / EX-22 / EX-15 | id=48 §"Q5" table | S6 tags (3 rows): example_id 15 / 26 / 19 paired with `company_attribute='conflict-resolution-cross-team'`. Cross-link to `kg://245` (conflict-resolution cluster). EX-15 reused (Q3 secondary -- handle via notes). | `SELECT bect.* FROM behavioral_example_company_tags bect WHERE bect.company_id=29 AND bect.example_id IN (15,19,26) AND bect.company_attribute='conflict-resolution-cross-team'` -- expect 3 rows |
| 使用说明 1-paragraph (优先级 / 跨题复用规则 / EX-XX -> bq_behavioral_examples.json reference) | id=48 §"使用说明" footer | drop (the rules are in `kg://251` storytelling-framework-starr §"reuse rules"); per-Pinterest specifics survive as the Q -> EX matrix in S6 itself | `SELECT description FROM framework_nodes WHERE id=251` -- contains generic story-reuse / "no double-use across questions" guidance |

**Story uniqueness caveat**: EX-01 and EX-15 each appear under 2 distinct Pinterest BQ Q's. Decision (per protocol §"causal-proof"): each `(example_id, company_id)` row stores its **primary** attribute (the one matching its dominant cluster); the **secondary** attribute is encoded into `notes` as `secondary_attribute=<slug>`. Apply seed must assert this manually (no schema constraint enforces it). Verify via re-audit: `SELECT example_id, company_attribute, notes FROM behavioral_example_company_tags WHERE company_id=29 AND notes LIKE '%secondary_attribute%'` -- expect 2 rows (EX-01 + EX-15).

#### Doc id=66 "Pinterest Prep Card Index" (7 306 chars, card_index JSON)

This doc is a JSON `card_index` artifact (`schema_version: 1`) with 10 pattern cards, each containing 2-4 problems. Total problems referenced (de-duplicated against id=47): 22 problems already covered by id=47's S4 tags + 0 net-new (every problem in id=66 also appears in id=47).

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| 10 pattern cards (字符串/数字运算 / Monotonic Stack / Greedy diff / Warehouse / Graph-Eulerian-BFS / Backtracking / DP-binsearch / Heap-Sim-Design / Interval-Subseq / Pinterest-Custom) | id=66 entire body (JSON) | each card maps to a meta-prep pattern node (where one exists): kg://289 monotonic-stack / kg://290 prefix-sum-difference (closest to "greedy diff") / kg://285 BFS-DFS / kg://286 backtracking / kg://284 binary-search / kg://287 DP / kg://288 heap-topk / kg://291 intervals / kg://282 two-pointers (closest to "interval-subseq" / Is Subsequence) | `SELECT path, title FROM framework_nodes WHERE path LIKE 'meta-prep/lc-keyword-checklists/%'` -- 14 rows; verify each id=66 card has a path it maps to |
| Problems within each card (one_liner per problem) | id=66 `cards[].problems[]` | the per-problem `one_liner` is **finer-grained than current `problems.notes`** -- §5 promotion candidate: extend `problems.notes` (or a new `problem.one_liner` column) with these short hints. Keep id=66 alive until promotion lands (else 22 one-liners become unrecoverable). | `SELECT id, title, length(notes) FROM problems WHERE id IN (135,1073,1074,85,242,236,157,1069,1070,148,217,214,451,439,1066,1067,332,55,265,498,258,199,237,277,144,417,1068,1071,1072,1075,1076,1120) AND notes IS NOT NULL` -- pre-apply baseline; verify post-promotion that one_liner is appended |
| Card "name_zh" / "name_en" / "summary_zh" 中英对照 + 1-line pattern summary | id=66 `cards[].name_*/summary_zh` | each card's 中文 summary covers a pattern-level 考察要点 (e.g. "Hierholzer 欧拉路径 / 多源 BFS / 结算差分" for Graph-Eulerian-BFS) -- merge into corresponding `meta-prep/lc-keyword-checklists/*` node description. §5 promotion candidate "lc-keyword-checklists pattern-summary 中文双语补充". | (post-promotion) `SELECT description FROM framework_nodes WHERE path='meta-prep/lc-keyword-checklists/bfs-dfs-grid-traversal'` -- contains "Hierholzer\|多源 BFS\|Eulerian" |
| "字符串/数字运算" card (LC 43 + 2 Pinterest-custom round() problems) | id=66 cards[0] | **No exact lc-keyword-checklists node** -- §5 promotion candidate: `meta-prep/lc-keyword-checklists/string-digit-arithmetic` (carry propagation / partition / shift-based rounding). Companies-so-far: Pinterest. Generic enough; check Google id=92 (R2 Coding) for parallels. | (post-promotion) `SELECT path FROM framework_nodes WHERE path = 'meta-prep/lc-keyword-checklists/string-digit-arithmetic'` |
| "仓储/箱子装填" card (LC 1564 + LC 1580) | id=66 cards[3] | **No exact node** -- §5 promotion candidate: extend `meta-prep/lc-keyword-checklists/two-pointers` (kg://282) with a "warehouse/box-packing prefix-min" subsection, OR new `meta-prep/lc-keyword-checklists/warehouse-prefix-min`. Cross-company: rare, may not meet 3-company threshold. **Defer**. | n/a until promotion lands |
| "Pinterest 定制题" card (8 custom problems) | id=66 cards[9] | already covered by S4 tags above (custom-relevance=core); the card itself is a per-company group, not a generic pattern -- card-level row drops, problems survive via S4 + the §3 skeleton's "## R2 Coding (Custom)" subsection | (already covered above) |

**Hold archive of id=66 contingent on §5 promotion of**: (a) `lc-keyword-checklists/string-digit-arithmetic` node OR confirmed defer; (b) the per-problem `one_liner` extension (or accepted as information-lossy with explicit user approval).

---

## §3 Skeleton preview

The full markdown that the **surviving Pinterest hub doc** (recommended: a freshly-inserted `cd://66` rewrite, treating id=66's slot as the new hub since it currently has the lowest semantic complexity -- a JSON card_index -- and is less of a loss to overwrite than id=47/48 prose. ALTERNATIVE: introduce a new `hub_doc` row for Pinterest analogous to Google's id=53. **Recommendation: new hub_doc row** since id=66 is JSON and the surviving doc must be markdown-renderable in CompanyDrawer.Notes).

> **Decision pending user review**: (a) overwrite id=66 (JSON -> markdown; doc_kind change) OR (b) insert a new `hub_doc` row (cleaner semantics; mirrors Google's id=53 pattern). Default: **(b) new hub_doc row**.

The surviving Pinterest `hub_doc` will be the union of TOC + CONCEPTS + prep skeletons. **This plan owns the TOC half** of that union; the §3 skeleton below shows the TOC half **only**. Sister plans T-P0-811 (CONCEPTS) and T-P0-812 (prep) author the other halves; B4-promotion (T-P1-821) merges and ratifies the final unified Pinterest hub.

```markdown
<!-- HUB_REORG_20260510_B4A_PINTEREST_TOC_HALF -->
# Pinterest Senior MLE -- Prep Index (TOC half)

> 跨引用进 KG / 元备战节点 + 进 S4 / S6 标签表。Pinterest 专属信息只剩三类：S2 `companies.notes` 行政信息（薪资/HC/Team Match 模式）、S4/S5/S6 标签表（已存于 DB）、本 hub doc 的 drawer 链接索引。深度学习内容请走 KG / `meta-prep/*` 节点（详见 CONCEPTS half）。本 half 专门负责 LC + BQ 导航与映射。

## Loop Structure (5-round VO)

- [Pre-loop: Recruiter call + Tech screen](kg://298) -- `pre-loop-recruiter-and-tech-screen` (60min phone screen + ML proj + 3 ML fund + coding)
- [Standard 4-round MLE Virtual Onsite](kg://297) §"Pinterest 5-round 变体" -- 2× DSA + ML Practitioner + ML SD + BQ
- [ML System Design Round playbook](kg://299) -- ML SD round 即此 playbook + Pinterest SD module table 下方
- [Behavioral / BQ Round playbook](kg://300) -- BQ round 配合本 hub §"BQ" subsection 的 Q->EX 映射 (S6)
- [Project Deep-Dive Round playbook](kg://301) -- ML Practitioner / ML Deep Dive 用此 playbook

环境 (Pinterest-specific): Google Meet + CoderPad，无 compiler。Code-pad 注意事项参 [kg://281](kg://281) §"CoderPad 模式" + [kg://276](kg://276) clarify-restate-before-typing。

## R1 LC + R2 LC -- 26 题 must-do + 8 Pinterest-custom = 34 题

来源: `S4 problem_company_tags WHERE company_id=29` (post-archive 34 行). 每条点击进入 ProblemDrawer，看完整中文解法 + code review。

### Core 14 道 (2026-04-12 清单)

| # | LC  | Pattern (kg://) | Title | 考察要点 |
|---|-----|-----------------|-------|---------|
| 1 | 332 | [BFS/DFS Grid](kg://285) | [Reconstruct Itinerary](db://148) | 后序 append + reverse / Hierholzer / min-heap 字典序 |
| 2 | 465 | [Backtracking](kg://286) | [Optimal Account Balancing](db://214) | Bitmask DP + 最大零和子集 + submask 枚举 |
| 3 | 815 | [BFS/DFS Grid](kg://285) | [Bus Routes](db://217) | 节点 = bus 路线；visited 标记路线；LC 1135 反向 |
| 4 | 322 | [DP Knapsack](kg://287) | [Coin Change](db://55) | Unbounded knapsack `dp[i]=min(dp[i-c]+1)` |
| 5 | 282 | [Backtracking](kg://286) | [Expression Add Operators](db://439) | `*` 处理 `cur - prev + prev*x`；前导零剪枝 |
| 6 | 1055 | [Two Pointers](kg://282) | [Shortest Way to Form String](db://498) | 贪心匹配 + `next[pos][ch]` 加速 |
| 7 | 311 | [Heap/Hash](kg://288) | [Sparse Matrix Multiplication](db://277) | 稀疏 hashmap；nnz 行 / nnz 列 |
| 8 | 2402 | [Heap/Hash](kg://288) | [Meeting Rooms III](db://258) | 双堆 free + busy；tuple tiebreak |
| 9 | 1110 | [Backtracking](kg://286) | [Delete Nodes And Return Forest](db://1066) | DFS 状态上下传 |
| 10 | 1244 | [Heap/Hash](kg://288) | [Design A Leaderboard](db://199) | size-K min-heap + heapreplace |
| 11 | 410 | [Binary Search](kg://284) | [Split Array Largest Sum](db://265) | 二分答案 + 贪心可行性 |
| 12 | 43 | [String/Digit-Arith](kg://TBD) | [Multiply Strings](db://135) | 数字模拟 `pos[i+j+1]` |
| 13 | 642 | [Trie](kg://292) | [Design Search Autocomplete System](db://237) | Trie + 节点级 size-3 min-heap |
| 14 | 1723 | [Backtracking](kg://286) + [Binary Search](kg://284) | [Find Minimum Time to Finish All Jobs](db://1067) | 二分 max-load + 回溯剪枝 |

### Extension / Follow-up 12 道 (2025-11 dump + 2026-05 user dump)

| # | LC  | Pattern (kg://) | Title | 考察要点 | 来源 |
|---|-----|-----------------|-------|---------|------|
| 1 | 84 | [Monotonic Stack](kg://289) | [Largest Rectangle in Histogram](db://85) | 递增栈 + 哨兵 | 2025-11 |
| 2 | 85 | [Monotonic Stack](kg://289) | [Maximal Rectangle](db://242) | 2D -> 1D 直方图 | 2025-11 |
| 3 | 392 | [Two Pointers](kg://282) | [Is Subsequence](db://417) | 同向扫；`next_pos[i][ch]` DP | 2025-11 |
| 4 | 1135 | [Union-Find](kg://293) | [Connecting Cities With Min Cost](db://1087) | MST Kruskal+UF+heap (LC 815 带权姊妹题) | LC 815 follow-up |
| 5 | 1526 | [Prefix Sum/Diff](kg://290) | [Min Number of Increments on Subarrays](db://236) | first-difference 累加 | 2025-11 |
| 6 | 1564 | [Two Pointers](kg://282) | [Put Boxes Into Warehouse I](db://1069) | warehouse prefix-min 单调 | 2025-11 |
| 7 | 1570 | [Heap/Hash](kg://288) | [Dot Product Sparse Vectors](db://239) | LC 311 的 1D 版 | LC 311 follow-up |
| 8 | 1580 | [Two Pointers](kg://282) | [Put Boxes Into Warehouse II](db://1070) | 双端指针；warehouse 无单调 | 2025-11 |
| 9 | 1851 | [Intervals](kg://291) | [Min Interval to Include Each Query](db://144) | 离线排序 + heap 弹失效 | 2025-11 |
| 10 | 3229 | [Prefix Sum/Diff](kg://290) | [Min Ops to Make Array = Target](db://157) | signed diff greedy (LC 1526 推广) | 2025-11 |
| 11 | 426 | [Backtracking](kg://286) | [BST -> Sorted Doubly Linked List](db://332) | 中序 + prev 滚动；尾首闭环 | 2026-05 user |
| 12 | 1293 | [BFS/DFS Grid](kg://285) | [Shortest Path in Grid w/ Obstacles Elim](db://451) | state = (x,y,k_remaining) | 2026-05 user |

### Pinterest Custom (无 LC 对应) -- 8 题

| # | Title | Core Pattern (kg://) | 考察要点 |
|---|-------|---------------------|---------|
| 1 | [Escape Room Game State](db://1068) | [BFS/DFS Grid](kg://285) | (people_pos, room_open_bitmask) 多 actor 联合状态 |
| 2 | [Lighthouse 2D Light Propagation](db://1071) | [BFS/DFS Grid](kg://285) | 光束 DFS + splitter 分叉；`(r,c,dir)` 去重 |
| 3 | [Prefix-Match First-Word-Index](db://1072) | [Binary Search](kg://284) + [Trie](kg://292) | `bisect_left` 已排序 dict 上 O(log n) |
| 4 | [Grant Access on DAG](db://1075) | [Topological Sort](kg://294) | DAG 传播 + visited 防重 |
| 5 | [Pin Connectivity Streaming Edges](db://1076) | [Union-Find](kg://293) | 路径压缩 + 按秩合并；流式连通 |
| 6 | [round() from scratch (string in)](db://1073) | [String/Digit-Arith](kg://TBD) | half-up 进位链；禁用 float() |
| 7 | [round by precision p](db://1074) | [String/Digit-Arith](kg://TBD) | shift 复用 + 还原 |
| 8 | [Reverse Count and Say (screening)](db://1120) | [Backtracking](kg://286) | 每步消耗 2 / 3 字符；count ∈ [1,99] 无前导零 |

(LC 332 "Loop Follow-up Addendum" -- 行程是否必须重访某条边 -- annotated as note on `problems.id=148`, not separate row.)

## SD module (Pinterest-flavour wraps)

7 Pinterest-flavour SD writeups; the de-companied substrate lives in `meta-prep/system-design-must-knows/*`. Pinterest-specific `sd://pinterest-<slug>` references survive in the CONCEPTS half (T-P0-811) which owns the long-form prose; this TOC half just gives the dual-link index.

| # | Topic | Substrate (kg://) | Pinterest writeup |
|---|-------|-------------------|-------------------|
| 1 | Ad CTR Prediction | [kg://259](kg://259) feature-cross + [kg://262](kg://262) calibration | [sd://pinterest-ad-ctr](sd://pinterest-ad-ctr) (CONCEPTS) |
| 2 | User & Item Embeddings | [kg://252](kg://252) two-tower + [kg://254](kg://254) infonce | [sd://pinterest-embeddings](sd://pinterest-embeddings) (CONCEPTS) |
| 3 | Personalized Chatbot Pins | [kg://255](kg://255) multi-stage funnel | [sd://pinterest-chatbot-pins](sd://pinterest-chatbot-pins) (CONCEPTS) |
| 4 | Pin Ranking | [kg://257](kg://257) LtR + [kg://258](kg://258) MMoE + [kg://263](kg://263) MMR/DPP | [sd://pinterest-pin-ranking](sd://pinterest-pin-ranking) (CONCEPTS) |
| 5 | Pins Search | [kg://255](kg://255) funnel + [kg://253](kg://253) ANN + [kg://256](kg://256) cross-encoder | [sd://pinterest-pins-search](sd://pinterest-pins-search) (CONCEPTS) |
| 6 | Notification Recommendation | [kg://265](kg://265) bandit + [kg://273](kg://273) p99-budget | [sd://pinterest-notification-reco](sd://pinterest-notification-reco) (CONCEPTS) |
| 7 | Catalog Bulk Update | [kg://268](kg://268) lambda/kappa + [kg://267](kg://267) feature-store | [sd://pinterest-catalog-bulk-update](sd://pinterest-catalog-bulk-update) (CONCEPTS) |

## BQ -- 5 Q × 2-3 stories matrix (S6 tags)

来源: `S6 behavioral_example_company_tags WHERE company_id=29`. 每条点击进入 BehavioralExampleDrawer。BQ playbook 通用规则参 [kg://300](kg://300) + [kg://251](kg://251) STAR-T-STARR。

| Q (面试官 prompt) | Primary cluster (kg://) | Story 1 (P1) | Story 2 (P2) | Story 3 (P3) |
|---|---|---|---|---|
| Q1: 独立主导端到端项目 | [kg://246](kg://246) project-ownership-end-to-end | [EX-06 Allocation Framework Platform](db://6) | [EX-23 NYC C2C Policy Launch](db://27) | [EX-14 LLM-as-Judge](db://18) |
| Q2: 需求从何而来 | [kg://247](kg://247) ambiguity-self-initiated | [EX-01 Intent Collapse Discovery](db://1) | [EX-03 Sale NDCG Proxy](db://3) | [EX-09 Conversational Search Proxy](db://9) |
| Q3: stepping ahead | [kg://247](kg://247) ambiguity-self-initiated | [EX-08 Module Proliferation -> VP](db://8) | [EX-01 Intent Collapse (reused)](db://1) | [EX-15 Model Deprecation](db://19) |
| Q4: difficult feedback | [kg://249](kg://249) failure-and-difficult-feedback | [EX-17 Senior IC Difficult Feedback](db://21) | [EX-13 Authorship Dispute](db://17) | [EX-02 Manager Resistance to Diversity](db://2) |
| Q5: teammate missing deadlines | [kg://245](kg://245) conflict-resolution-cross-team | [EX-11 Intern Goal Visibility](db://15) | [EX-22 Hashing Delegation](db://26) | [EX-15 Model Deprecation (reused)](db://19) |

(EX-01 / EX-15 reused across 2 Q's -- secondary attribute encoded in S6 `notes`.)

## Schedule / 行政

- 5-round VO 时段、Zoom + CoderPad 链接、面试官姓名: 走 `interview_events` (Dashboard.InterviewTimeline)，**不在本 doc**.
- TC / HC / Team Match 模式: 见 [companies.notes (S2)](db://29#notes) (kept; admin only, ~150 B post-trim).
- Recruiter (David) 沟通历史: 见 commit log + PROGRESS.md, 不在本 doc.
```

**Skeleton renders check**: All URIs (`kg://N`, `db://N`, `cd://N`, `sd://<slug>`) follow existing CompanyDrawer.Notes drawer-link routing. The `kg://TBD` placeholders for `string-digit-arithmetic` will resolve to a real id after T-P1-821 (B4-promotion) creates the new lc-keyword-checklists child. **Apply gate**: archive blocks until §5 promotion lands (or "string-digit-arithmetic" is explicitly deferred and the §3 placeholder is left as a flagged TODO).

---

## §4 Hard-archive checklist

Apply order matters. Each step is a discrete artifact; if any fails, abort and roll back via `restore.sql`.

> **Cross-plan ordering**: Pinterest TOC archive should NOT run before sister plans T-P0-811 (CONCEPTS) and T-P0-812 (prep) are also reviewed and approved, because:
> 1. The §3 skeleton above is only the TOC half -- the surviving hub doc must contain all 3 halves merged.
> 2. S2 trim is shared (this plan owns it but the merged content depends on the other 2 plans' input).
> 3. Apply order: ratify all 3 plans → produce merged §3 skeleton → run apply seed once.
> Therefore §4 below is **partial** -- the actual apply seed (`scripts/_archive_pinterest_2026-05-10.py`, single-shot, all 3 subsets) consolidates §4 from all 3 plans.

### 4.1 DB backup (shared, runs once)

```bash
cp data/mle_prep.db data/mle_prep.db.bak.$(date -u +%Y%m%dT%H%M%SZ)_pre_pinterest_archive
```

### 4.2 DELETE rows from `company_documents` -- TOC subset

```sql
-- TOC subset: 2 of 3 docs are deleted; id=66 either rewrites to markdown OR is replaced by a new hub_doc INSERT (see §3 decision)
DELETE FROM company_documents
WHERE id IN (47, 48);
-- id=66 handled separately in §4.3 (rewrite OR delete-and-replace)
```

**Hold list** (do NOT delete until contingent §5 promotions land):
- id=66 -- waits for `lc-keyword-checklists/string-digit-arithmetic` promotion (or explicit defer) AND for the `problem.one_liner` / `problems.notes` extension (or accepted information loss with explicit user approval).
- id=47 -- archive can proceed first-pass once 34 S4 INSERTs land (causal-proof gate: every LC mentioned in id=47 has a corresponding S4 row).
- id=48 -- archive can proceed first-pass once 15 S6 INSERTs land (causal-proof gate: every Q × Story pair in id=48 has a corresponding S6 row, with secondary attributes in `notes` for the 2 reused stories).

### 4.3 INSERT new `hub_doc` for Pinterest (decision (b))

```sql
INSERT INTO company_documents (company_id, doc_kind, title, content, content_hash, source_path, created_at, updated_at)
VALUES (29, 'hub_doc', 'Pinterest Senior MLE -- Prep Index',
        '<MERGED §3 skeleton (TOC + CONCEPTS + prep halves)>',
        '<sha256 of merged skeleton>', NULL,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

If decision (a) is taken instead (overwrite id=66): UPDATE id=66 with `doc_kind='hub_doc'`, content = merged skeleton.

### 4.4 UPDATE `companies.id=29` notes trim

```sql
-- Trim recruiter-call summary section; keep TC + HC + Team Match admin metadata.
UPDATE companies
SET notes = 'Senior ML Engineer position
TC ~$500K/yr
Hiring model: general pool, ~5 HC available, competitive Team Match required

(Loop structure + 5-round VO breakdown + environment notes -> see meta-prep/onsite-loop-templates/* via Prep Index doc.)'
WHERE id = 29;
```

### 4.5 INSERT 34 `problem_company_tags` rows (S4 from id=47 + id=66)

```sql
-- 14 core LC (relevance='core', source='B4a-pinterest-toc-archive-2026-05-10')
INSERT INTO problem_company_tags (problem_id, company_id, relevance, source, notes, added_at) VALUES
  (148, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 332 Hierholzer 后序 append + reverse; min-heap 保字典序', CURRENT_TIMESTAMP),
  (214, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 465 Bitmask DP 最大零和子集; submask O(3^n)', CURRENT_TIMESTAMP),
  (217, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 815 BFS on route graph; visited 标记路线 (LC 1135 反向)', CURRENT_TIMESTAMP),
  (55,  29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 322 Coin Change unbounded knapsack', CURRENT_TIMESTAMP),
  (439, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 282 Expression Add Operators backtrack + prev (cur - prev + prev*x)', CURRENT_TIMESTAMP),
  (498, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1055 greedy + next[pos][ch] 加速', CURRENT_TIMESTAMP),
  (277, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 311 Sparse Matrix Mult; A nnz row * B nnz col', CURRENT_TIMESTAMP),
  (258, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 2402 Meeting Rooms III; 双堆 free + busy', CURRENT_TIMESTAMP),
  (1066,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1110 Delete Nodes Forest; is_root 下传 / None 上返', CURRENT_TIMESTAMP),
  (199, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1244 Leaderboard; size-K min-heap + heapreplace', CURRENT_TIMESTAMP),
  (265, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 410 Split Array; 二分答案 + 贪心可行性', CURRENT_TIMESTAMP),
  (135, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 43 Multiply Strings; pos[i+j+1] 数字模拟', CURRENT_TIMESTAMP),
  (237, 29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 642 Autocomplete; Trie + node 级 size-3 min-heap', CURRENT_TIMESTAMP),
  (1067,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1723 Min Time Jobs; 二分 max-load + 回溯剪枝', CURRENT_TIMESTAMP)
ON CONFLICT (problem_id, company_id) DO UPDATE SET relevance=excluded.relevance, source=excluded.source, notes=excluded.notes;

-- 12 follow-up / extension LC (relevance='likely')
INSERT INTO problem_company_tags (problem_id, company_id, relevance, source, notes, added_at) VALUES
  (85,  29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 84 Largest Rect Histogram; 单调栈 + 哨兵 (2025-11 dump)', CURRENT_TIMESTAMP),
  (242, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 85 Maximal Rectangle; 2D -> 1D histogram (2025-11 dump)', CURRENT_TIMESTAMP),
  (417, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 392 Is Subsequence; next_pos[i][ch] DP (2025-11 dump)', CURRENT_TIMESTAMP),
  (1087,29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1135 MST Kruskal+UF+heap (LC 815 follow-up)', CURRENT_TIMESTAMP),
  (236, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1526 first-difference 累加 (2025-11)', CURRENT_TIMESTAMP),
  (1069,29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1564 warehouse prefix-min (2025-11)', CURRENT_TIMESTAMP),
  (239, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1570 Sparse dot product (LC 311 1D follow-up)', CURRENT_TIMESTAMP),
  (1070,29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1580 双端指针 box packing (2025-11)', CURRENT_TIMESTAMP),
  (144, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1851 离线排序 + heap 弹失效 (2025-11)', CURRENT_TIMESTAMP),
  (157, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 3229 signed diff greedy (LC 1526 推广)', CURRENT_TIMESTAMP),
  (332, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 426 BST -> DLL 中序 + prev 滚动 (2026-05 user dump)', CURRENT_TIMESTAMP),
  (451, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'LC 1293 BFS state=(x,y,k_remaining) (2026-05 user dump)', CURRENT_TIMESTAMP)
ON CONFLICT (problem_id, company_id) DO UPDATE SET relevance=excluded.relevance, source=excluded.source, notes=excluded.notes;

-- 8 Pinterest-custom (relevance='core')
INSERT INTO problem_company_tags (problem_id, company_id, relevance, source, notes, added_at) VALUES
  (1068,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: Escape Room; (rooms, people) tuple BFS', CURRENT_TIMESTAMP),
  (1071,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: Lighthouse 2D 光束传播 + splitter; (r,c,dir) 去重', CURRENT_TIMESTAMP),
  (1072,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: Prefix-Match First-Word-Index; bisect_left / Trie', CURRENT_TIMESTAMP),
  (1075,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: Grant Access on DAG; topological 传播', CURRENT_TIMESTAMP),
  (1076,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: Pin Connectivity streaming UF', CURRENT_TIMESTAMP),
  (1073,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: round() from scratch (string in, no float)', CURRENT_TIMESTAMP),
  (1074,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: round by precision p; shift 复用 1073', CURRENT_TIMESTAMP),
  (1120,29, 'core', 'B4a-pinterest-toc-archive-2026-05-10', 'Custom: Reverse Count and Say (screening); 2/3-char chunk backtrack', CURRENT_TIMESTAMP)
ON CONFLICT (problem_id, company_id) DO UPDATE SET relevance=excluded.relevance, source=excluded.source, notes=excluded.notes;
```

(Confirm `problem_company_tags` has a unique index on `(problem_id, company_id)` before relying on `ON CONFLICT`. If not: the apply seed must SELECT-then-INSERT idempotently.)

### 4.6 INSERT 15 `behavioral_example_company_tags` rows (S6 from id=48)

```sql
-- Q1 end-to-end-ownership: EX-06, EX-23, EX-14
INSERT INTO behavioral_example_company_tags (example_id, company_id, relevance, source, company_attribute, notes, added_at) VALUES
  (6,  29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'end-to-end-ownership', 'Q1 P1: Allocation Framework Platform Primitive (Hacker Week proto -> 200M+ year impact)', CURRENT_TIMESTAMP),
  (27, 29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'end-to-end-ownership', 'Q1 P2: NYC C2C Policy Launch (2-week test + 1-month launch hard deadlines)', CURRENT_TIMESTAMP),
  (18, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'end-to-end-ownership', 'Q1 P3: LLM-as-Judge (GenAI 探索 -> multi-team adoption)', CURRENT_TIMESTAMP),
  -- Q2 problem-framing: EX-01 (primary), EX-03, EX-09
  (1,  29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'problem-framing', 'Q2 P1: Intent Collapse Discovery (abandoned-query log dive); secondary_attribute=ambiguity-self-initiated (Q3 P2)', CURRENT_TIMESTAMP),
  (3,  29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'problem-framing', 'Q2 P2: Sale NDCG Proxy First-Principles', CURRENT_TIMESTAMP),
  (9,  29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'problem-framing', 'Q2 P3: Conversational Search Proxy Item', CURRENT_TIMESTAMP),
  -- Q3 ambiguity-self-initiated: EX-08, EX-01 (already inserted; secondary in notes), EX-15 (primary)
  (8,  29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'ambiguity-self-initiated', 'Q3 P1: Module Proliferation -> VP Escalation', CURRENT_TIMESTAMP),
  (19, 29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'ambiguity-self-initiated', 'Q3 P3: Model Deprecation Incident; secondary_attribute=conflict-resolution-cross-team (Q5 P3)', CURRENT_TIMESTAMP),
  -- (EX-01 reused under Q3 -- already inserted with primary='problem-framing'; Q3 binding lives in EX-01.notes)
  -- Q4 failure-and-difficult-feedback: EX-17, EX-13, EX-02
  (21, 29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'failure-and-difficult-feedback', 'Q4 P1: Difficult Feedback from Senior IC', CURRENT_TIMESTAMP),
  (17, 29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'failure-and-difficult-feedback', 'Q4 P2: Authorship Dispute', CURRENT_TIMESTAMP),
  (2,  29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'failure-and-difficult-feedback', 'Q4 P3: Manager Resistance to Diversity Ranking', CURRENT_TIMESTAMP),
  -- Q5 conflict-resolution-cross-team: EX-11, EX-22, (EX-15 reused; secondary in EX-15.notes)
  (15, 29, 'core',   'B4a-pinterest-toc-archive-2026-05-10', 'conflict-resolution-cross-team', 'Q5 P1: Mentoring Intern on Overpromise / Goal Visibility', CURRENT_TIMESTAMP),
  (26, 29, 'likely', 'B4a-pinterest-toc-archive-2026-05-10', 'conflict-resolution-cross-team', 'Q5 P2: Hashing Delegation', CURRENT_TIMESTAMP)
ON CONFLICT (example_id, company_id) DO UPDATE SET relevance=excluded.relevance, source=excluded.source, company_attribute=excluded.company_attribute, notes=excluded.notes;
```

(13 distinct stories × 5 Q's = 15 rows total in S6, since EX-01 and EX-15 are each reused once under a secondary Q -- those reuses live in the primary row's `notes`, not as separate rows.)

### 4.7 Seed script moves

```bash
mkdir -p archive/seed_scripts/2026-05-10/pinterest-toc/
git mv scripts/_create_pinterest_lc_index_doc.py archive/seed_scripts/2026-05-10/pinterest-toc/
git mv scripts/_enrich_pinterest_index_doc.py archive/seed_scripts/2026-05-10/pinterest-toc/
git mv scripts/_rewrite_pinterest_lc_doc47.py archive/seed_scripts/2026-05-10/pinterest-toc/
git mv scripts/_seed_pinterest_card_index.py archive/seed_scripts/2026-05-10/pinterest-toc/
git mv scripts/seed_pinterest_card_index_lc_426_1293_20260506.py archive/seed_scripts/2026-05-10/pinterest-toc/
git mv scripts/seed_pinterest_lc_must_do_sd_drawer_links.py archive/seed_scripts/2026-05-10/pinterest-toc/
```

(Run `grep -l "company_id\s*=\s*29\|Pinterest" scripts/seed_*.py scripts/_*.py` first to enumerate every Pinterest seed script. The 6 above are the TOC-subset seeds; CONCEPTS + prep subsets are moved by their respective B4a apply seeds. **Do NOT move** `scripts/seed_pinterest_lc_problems.py` -- it seeds the `problems` table rows themselves, which the new S4 tags reference; keep it active. **Do NOT move** `scripts/seed_pinterest_companies_row.py` -- it seeds the `companies.id=29` row that survives.)

### 4.8 restore.sql generation

Generate `archive/company_internalized/pinterest_2026-05-10/restore.sql` containing (TOC subset):
- INSERT statements for all 3 TOC docs (id=47, 48, 66) with original `content`, `content_hash`, `source_path`
- DELETE statement for the new hub_doc row (decision (b))
- UPDATE statement to revert `companies.id=29.notes` to the pre-archive 446-byte text
- DELETE statements for the 34 S4 INSERTs in §4.5
- DELETE statements for the 13 S6 INSERTs in §4.6

This is the only rollback artifact. Generated by the apply seed BEFORE any DELETE/UPDATE runs.

### 4.9 Sentinel idempotency

Apply seed prints `[SKIP]` on second run. Sentinels (TOC subset):
- `companies.notes` length matches the post-archive expected length (~150 B)
- No row exists in `company_documents` with id IN (47, 48); `company_documents` has a `hub_doc` row WHERE company_id=29 with content_hash matching the merged-§3 skeleton hash
- `SELECT COUNT(*) FROM problem_company_tags WHERE company_id=29` >= 34
- `SELECT COUNT(*) FROM behavioral_example_company_tags WHERE company_id=29` >= 13

### 4.10 Smoke checks

- `python scripts/audit_uri_consistency.py` -- 0 ERRORs (no dangling `kg://`, `db://`, `cd://`, `sd://`)
- `python scripts/_audit_company_kg_internalization.py` -- Pinterest row in roll-up: S3 bytes ~= merged-skeleton size; S4 = 34; S6 = 13 (or 15 with reuse rows); S2 ~= 150 B
- Frontend smoke (`cd src/frontend && npm run dev`, navigate to `/companies/29`): CompanyDrawer.Notes renders the merged skeleton; spot-click 2 `kg://` + 2 `db://` + 1 `sd://` link from the LC table + 1 `db://` from the BQ table; all resolve.

---

## §5 Promotion candidates flagged for meta-prep

Patterns spotted in Pinterest TOC docs that meet (or appear to meet) the >=3 P0+P1 companies threshold AND de-companiable wording. T-P1-821 (`B4-promotion`) consolidates these across all B4a plans.

1. **`meta-prep/lc-keyword-checklists/string-digit-arithmetic`** (single new node)
   - Pattern: carry propagation / partition('.') 解析 / shift-based precision rounding / banker's vs half-up rounding distinction / no-`float()` constraint.
   - Companies (so far): Pinterest (id=66 cards[0] + 3 problems: LC 43 + custom round() + custom round-by-p). Likely match: Google R2 coding (id=92 references LC 43 / digit ops); Uber Eats payment-rounding interviews; verify via grep "round\|carry\|digit" in `company_documents.content` across all companies.
   - Proposed target: `meta-prep/lc-keyword-checklists/string-digit-arithmetic` -- new sibling under kg://241 lc-keyword-checklists.
   - 1-line excerpt (de-companied): "String-digit arithmetic: carry propagation in `pos[i+j+1] += d_i*d_j; pos[i+j] += carry`; shift-based precision rounding by aligning to position p then restoring; banker's vs half-up rounding distinction; the `no-float()` constraint forces explicit decimal-point partition + integer-arithmetic chain."

2. **Per-problem `one_liner` field** (schema extension OR `problems.notes` convention, NOT a new node)
   - Pattern: id=66's JSON card_index stores a 1-liner Chinese hint per problem (e.g. "逐位乘法 pos[i+j] / pos[i+j+1]" for LC 43). This is finer-grained than current `problems.notes` (which is the full solution writeup).
   - Recommendation: T-P1-821 either adds a `problems.one_liner` column OR establishes a `problems.notes` prefix convention (`<ONE_LINER>: ... \n\n<DETAIL>: ...`) so the JSON card_index can be reconstructed from `problems` table directly.
   - Companies (so far): Pinterest (22 problems with one_liners). Generic enough to apply to any company; verify other companies' index docs (Google id=92, future Uber/Meta R2 indexes).
   - 1-line excerpt: "(schema extension) `problems.one_liner`: short Chinese hint, ≤40 chars, suitable for card-index display in side-drawer browser."

3. **`meta-prep/onsite-loop-templates/standard-4-round-mle-vo` -- 5-round Pinterest-style variant** (extension of existing kg://297, NOT a new node)
   - Pattern: Pinterest does 5-round VO instead of standard 4-round (2× DSA + ML Practitioner + ML SD + BQ). The 5-round shape is non-Pinterest-specific: many production-MLE companies (Reddit / Snap / Roblox / Coinbase) likely follow similar.
   - Recommendation: T-P1-821 extends `kg://297` description with a "5-round variants" subsection enumerating 4-round vs 5-round vs 6-round shapes + which axis the extra round adds (DSA-2 / project-deep-dive / coding-2).
   - Companies (so far): Pinterest (S2 + id=39 + id=83). Likely match: any company with 2× DSA + 1× ML SD + 1× ML Practitioner + 1× BQ.

4. **`meta-prep/onsite-loop-templates/code-pad-environment-quirks`** (extension of existing kg://281 OR new sibling, optional)
   - Pattern: CoderPad-no-compiler / Google-internal-CIDER / VSCode-Live-Share / Replit / etc. -- the per-company code-pad environment list affects how to dry-run code mentally.
   - Recommendation: extend `kg://281` (language-choice-python-default) with a "code-pad environments matrix" subsection.
   - Companies (so far): Pinterest (S2 = "CoderPad no compiler"). Likely match: Google (CIDER), Meta (CoderPad), DoorDash (CoderPad). Easy to satisfy 3-company threshold once T-P1-821 reads other plans' §1 inventory.

5. **`meta-prep/behavioral-clusters/<cluster>` per-Q -> Story matrix pattern (NOT a new node; schema/UX extension)**
   - Pattern: id=48 gives a 5-Q × 2-3-priority story matrix. The matrix shape (rows = company-typical BQ Q's, cols = priority-ranked stories) is generic and reusable.
   - Recommendation: T-P1-821 adds a UX convention to `kg://300` behavioral-bq-round playbook §"per-company Q->Story matrix" describing how S6 tags + `company_attribute` + `notes` reconstruct this matrix in the frontend BQ drawer.
   - Companies (so far): Pinterest (id=48 with 5 Q's × 2-3 stories). Google has a 6-story short-list (id=51 §"Story Short-list") which is the same shape -- already promoted in B4a-google §5. Cross-company convergence verified.

6. **`meta-prep/lc-keyword-checklists/warehouse-prefix-min`** (single new node, optional / DEFER)
   - Pattern: warehouse / box-packing problems with prefix-min monotonicity (LC 1564) and 2-pointer dual-direction (LC 1580).
   - Companies (so far): Pinterest only. **Defer** -- 1-company threshold not met; current `kg://282` two-pointers + `kg://290` prefix-sum-difference cover the substrate adequately for now.

---

## Apply gate

User reviews §2 (causal-proof matrix -- ~50 rows across S2 + 3 archive-candidate docs + 34 S4 INSERTs + 15 S6 INSERTs) and §5 (5+1 promotion candidates). Approval gate: explicit "ok 执行".

**Holds**:
- Archive of id=66 contingent on §5 candidate 1 (`string-digit-arithmetic`) + 2 (`one_liner` extension) landing first OR explicit user defer/accept-loss.
- Archive of id=47 / 48 first-pass once 34 S4 + 15 S6 INSERTs land (causal-proof gate: every LC mention + every Q×Story pair has a corresponding tag row).
- Cross-plan: do NOT run the apply seed until sister plans T-P0-811 (Pinterest-CONCEPTS) and T-P0-812 (Pinterest-prep) are also reviewed, so the merged §3 skeleton is consistent with all 3 halves.
- S2 trim is owned by this plan; the other 2 plans must skip the S2 row to avoid 3-way conflicting UPDATEs.

Discord ping: `B4a-pinterest-toc plan ready -- docs/archive_plans/B4a-pinterest-toc_2026-05-10.md -- 3 docs in scope (id=47/48/66), 21 KB prose -> 34 S4 + 15 S6 tag rows + merged hub_doc skeleton. Review §2 + §5; "ok 执行" to apply (after sister CONCEPTS + prep plans also approved).`
