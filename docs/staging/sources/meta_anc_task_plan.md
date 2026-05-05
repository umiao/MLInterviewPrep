# Meta AI-Native Coding Prep -- 10-Task Execution Plan (v3 -- review-fixes-applied)

Generated 2026-04-30 from task_db.py state. v3 incorporates 7 fixes from independent review (5/1 03:23Z):

- **FIX #1**: Header clarified -- source has 7 numbered sections; plan splits Section 4 (其他 AI Coding MLE/实习向 bundle) into 2 drawers (Sparse Matrix + Linear Regression) for cleaner spotlight, giving 8 drawer rows total.
- **FIX #3**: Idempotency key switched from (source, title) to (source, pattern). `pattern` is the stable slug; `title` may evolve for style. Hub uses sentinel-only key (drop content_hash).
- **FIX #4** (priority-1 per reviewer): T-P0-279 wire-in now mandates (a) backup dump to `data/backups/cd_82_anc_wirein_<UTC-ISO>.md` BEFORE any modification; (b) two-phase sentinel-anchor approach -- Phase 1 installs `<!-- ANC_WIREIN_AFTER -->` once if missing, Phase 2 splits-on-anchor for content insert/replace; (c) schedule table edit also sentinel-bracketed via `<!-- ANC_SCHED BEGIN/END -->`; (d) `--dry-run` CLI flag.
- **FIX #5**: NOOP detection now semantic (strip per-line trailing whitespace, force LF, collapse 3+ blank lines). Forbids non-deterministic sources (no datetime.now / unsorted dict iter / random) in description generation.
- **FIX #6**: T-P0-271 length budget revised: total 6-8KB but the verbatim AI Prompt block (~2KB from source lines 138-150) is excluded from the budget -- counted as a fenced code block thats its own thing.
- **FIX #7**: All scripts must do `COMPANY_ID = session.query(Company).filter(Company.name == "Meta").one().id` then `assert COMPANY_ID == 31`. No magic numbers; assertion fails loud.
- **FIX #8**: Each problem-row task ends with REQUIRED-KEYWORDS list (6 per task). Script must assert ALL keywords appear in inserted description; if any missing -> abort with diagnostic. Catches accidental section drops during distillation.
- **SKIP #2** (per reviewer discretion grant): boilerplate-shared protocol section. The 9-step block is duplicated across 8 tasks but tolerated for now to avoid +1 file dependency surface for autonomous workers.

Source material: `MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md` (53KB, 7 numbered sections -> 8 drawer rows).

Drawer pattern: each problem -> `db://N` (problems row, key = (source, pattern)) | hub doc -> `cd://N` (company_documents row, key = sentinel HTML comment) | wire-in -> two-phase sentinel-anchor edit of cd://82 with mandatory backup.

---

## T-P0-270  [P0/M]  STATUS: active

**Title**: [META-ANC-1] Maze Solver drawer (Q1 print-priority -> Q5 bomb-mask, BFS with state bitmask)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='bfs_state_bitmask')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_maze_solver --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 1, lines 1-113).

Goal: Insert ONE problems row that becomes the db://<id> drawer for the Maze Solver Meta AI-Native Coding question. Distill the 5-question ladder into a single drawer doc with extracted 要点.

PER-TASK CONSTANTS:
  slug = 'meta_anc_maze_solver'
  pattern = 'bfs_state_bitmask'
  script path = MLInterviewPrep/scripts/content_meta_anc_maze_solver.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='bfs_state_bitmask')

Drawer description content (Chinese narration + English terms; first-use as **English** (acronym, 中文); sentence-fragment golden-voice rhythm, NOT AI explainer mode):

Sections required (compose into description column):
1. 题面 5-question ladder (Q1 print priority -> Q5 bombs)
2. 解法谱系表 (vanilla BFS / + visited / + directional gates / + key-door bitmask / + bomb mask) with 复杂度 column
3. 状态空间洞察 (path length 从 复杂度 消失; mask 维度才是真正指数源)
4. 核心 idiom 代码段 (3 块): bitmask key codec | bomb-mask wall lookup helper | directional get_neighbors
5. AI 协同分工对照表 (做对 vs 翻车): bitmask 自己写, blast-area helper 让 AI 写; 复杂度公式自己复算
6. 速查 cheat-sheet 7 条 (面试前 5 分钟扫: 状态维度想清楚 / visited 用完整 state / bitmask 位算对 / 派生信息查表 / 起点终点优先级 / 复杂度口头分析 / k 太大临界点)

Length target: 4-7KB. Distill the source -- the source IS golden, do NOT rewrite for prose; preserve original phrasings where punchy.

Per memory feedback_match_golden_voice: sentence fragments, spoken-English rhythm, no explainer mode. Per feedback_content_style_cn_en: Chinese narration with English terms.

Commit: '[META-ANC-1] Add Maze Solver drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'bitmask', 'BFS', 'blast', '复杂度', 'visited', '状态空间'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_maze_solver -->

```

---

## T-P0-271  [P0/S]  STATUS: active

**Title**: [META-ANC-2] Max Unique Char Subset drawer (backtrack -> state-comp DP w/ XOR-prev trick)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='bitmask_dp_subset_sum')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_max_unique_char_subset --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 2, lines 129-150).

Goal: Insert ONE problems row that becomes the db://<id> drawer for the Max Unique Character Subset Meta AI-Native Coding question.

PER-TASK CONSTANTS:
  slug = 'meta_anc_max_unique_char_subset'
  pattern = 'bitmask_dp_subset_sum'
  script path = MLInterviewPrep/scripts/content_meta_anc_max_unique_char_subset.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='bitmask_dp_subset_sum')

Drawer description sections:
1. 题面 (单词列表 -> 选子集字母两两不重叠且覆盖最多)
2. 解法谱系表 (Q1-Q2 backtracking O(2^n) / Q3-Q4 state-compression DP O(n*2^26) -> 万级数据)
3. **核心 元规律**: XOR-prev 技巧 (因不相交约束 prev|word == prev^word, dp value = single int 而非 prev 指针 Node)
4. 关键代码 idiom: dp[mask] -> word_index 字典 + snapshot iteration (0/1 背包性) + 路径重建
5. 预处理 3 步 (bitmap / popcount filter / anagram dedup)
6. 剪枝: 一旦 mask == (1<<26)-1 立即 return
7. AI 协同 prompt 模板 (照搬源材料 38-150 lines 那段 prompt -- 这是金句, 完整保留)
8. 一句话 元规律: '不相交约束让 OR 退化成 XOR' -- 面试用来秀洞察

Length target: 4-6KB.

Commit: '[META-ANC-2] Add Max Unique Char Subset drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'XOR', 'bitmap', 'state-compression', 'snapshot', 'anagram', '不相交'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_max_unique_char_subset -->

LENGTH-TARGET REVISION (FIX #6 -- verbatim block excluded from budget): Total 6-8KB, but the "AI Prompt 模板" verbatim block (~2KB from source lines 138-150) is excluded from the budget -- count it as a fenced code block thats its own thing. Sections 1-6 + 8 fit within 4-6KB; section 7 (verbatim prompt) is +2KB on top.
```

---

## T-P0-272  [P0/M]  STATUS: active

**Title**: [META-ANC-3] Friend Recommendation drawer (L1 valid-fix -> L6 senior framing, 6-layer ladder)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='graph_recommendation_topk')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_friend_recommendation --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 3, lines 156-228).

Goal: Insert ONE problems row that becomes the db://<id> drawer for the Friend Recommendation question. This题 is ABOUT how to use AI itself -- the L6 元能力 layer is the differentiator.

PER-TASK CONSTANTS:
  slug = 'meta_anc_friend_recommendation'
  pattern = 'graph_recommendation_topk'
  script path = MLInterviewPrep/scripts/content_meta_anc_friend_recommendation.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='graph_recommendation_topk')

Drawer description sections (PRESERVE the 6-layer L1-L6 structure -- it IS the answer):

L1 无 AI: valid_recommend 必查清单 (排除自指 / 已有好友 / 去重 / 对称性 / 空集 / 类型边界); test 名反推 bug; 修复时不要顺手重构.
L2 AI 辅助实现: 第一发 prompt 完整结构 (类定义+签名+测试+约束) 让 success rate 30->80%; paste 前三件事扫一遍; 增量 debug; 迭代失败止损信号; 5 个常见 AI 幻觉模式.
L3 AI 输出过滤: 'AI 给十个可用两个'; 好友推荐指标光谱表 (graph-only / demographic / 行为日志); Adamic-Adar 一句话原理.
L4 算法实现+复杂度: Top-K Mutual Friends 朴素 O(n*f + n log k); 2-Hop 优化 O(f^2) 何时用; 'based on input interface 选算法' 的回答模板; 复杂度两段论 (主导项 + 优化方向).
L5 测试覆盖: Mutual Friends 测试最小覆盖集 (7 条); 让 AI 生成测试的 prompt 模式 ('写测试覆盖以下场景' 列具体 5-7 条); 测试也要 paste 前扫.
L6 元能力 (这层最值钱): 主动声明 '我不采纳什么' (AI 建议基于 interest, 但 User 类没 interest 字段 -> 排除); '够用即可' 的工程取舍; 把 AI 当协作者而非代写的措辞 (外化思考过程 边操作边讲).

Length target: 6-9KB. 6-layer 结构是这道题的核心信号 -- 别压缩掉.

Commit: '[META-ANC-3] Add Friend Recommendation drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'valid_recommend', 'mutual', 'Adamic-Adar', '2-Hop', 'L6', '元能力'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_friend_recommendation -->

```

---

## T-P0-273  [P0/S]  STATUS: active

**Title**: [META-ANC-4] Sparse Matrix Ops drawer (COO/CSR/CSC + 双指针 dot + matmul subcubic)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='sparse_format_dot_product')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_sparse_matrix_ops --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 4 first half, lines 235-265).

Goal: Insert ONE problems row (db://<id> drawer) for sparse matrix operations.

PER-TASK CONSTANTS:
  slug = 'meta_anc_sparse_matrix_ops'
  pattern = 'sparse_format_dot_product'
  script path = MLInterviewPrep/scripts/content_meta_anc_sparse_matrix_ops.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='sparse_format_dot_product')

Drawer description sections:
1. 题面 (稀疏向量点积 / 稀疏矩阵乘法; 让 NNZ 取代维度成为复杂度主导)
2. 三种存储格式对照表 (COO 三元组构建快 / CSR 按行 SpMV 友好 / CSC 按列 SpMV^T 友好); 工业惯例: 构建期 COO -> .tocsr()/.tocsc()
3. 核心 idiom: 双指针稀疏点积代码段 (排序版 O(nnz1+nnz2)); 一稀一稠用 hash 查 O(nnz_small)
4. 矩阵乘法 < O(n^3) 的主流算法表 (Strassen O(n^2.807) / Coppersmith-Winograd O(n^2.37) / Alman-VW 2024 O(n^2.371))
5. 工业反差: BLAS GEMM 仍 O(n^3) 但靠 cache blocking + SIMD/AVX + 多线程 -- 理论复杂度 != 实际性能 (用来回答 'why not Strassen in production')
6. 高频 follow-up: 稀疏未排序怎么办 (hash) / 稀疏转置 (CSR<->CSC O(1)) / CSR x CSC 经典搭配 (A 取行 B 取列 归约成稀疏点积)
7. AI 协同点: 让 AI 对比格式性能差异 + 生成各格式的 toy benchmark; 自己掌握选型逻辑

Length target: 3-5KB.

Commit: '[META-ANC-4] Add Sparse Matrix Ops drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'COO', 'CSR', 'CSC', '双指针', 'Strassen', 'BLAS'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_sparse_matrix_ops -->

```

---

## T-P0-274  [P0/S]  STATUS: active

**Title**: [META-ANC-5] Linear Regression drawer (closed-form X^TX + Ridge/Lasso/SGD follow-ups)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='normal_equation_lstsq')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_linear_regression --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 4 second half, lines 267-286).

Goal: Insert ONE problems row (db://<id> drawer) for hand-derived linear regression.

PER-TASK CONSTANTS:
  slug = 'meta_anc_linear_regression'
  pattern = 'normal_equation_lstsq'
  script path = MLInterviewPrep/scripts/content_meta_anc_linear_regression.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='normal_equation_lstsq')

Drawer description sections:
1. 题面 (给点集 最小化 MSE 推导并实现 closed-form)
2. 推导过程 (3 行): L(w) = ||Xw - y||^2 -> grad = 2X^T(Xw-y) -> w = (X^TX)^{-1} X^T y
3. **关键 dimension argument**: 求导出来是 X^T 不是 X 是为了维度对齐 (grad 必须 d x 1, Xw-y 是 n x 1, 所以前面乘 X^T in R^{d x n}). 这一句话能讲清就显示懂 calculus.
4. 三种实现对照表 (np.linalg.inv 教科书慢且不稳 / np.linalg.solve 推荐 LU 分解 / np.linalg.pinv 最稳 SVD 处理奇异)
5. 复杂度: O(nd^2 + d^3); d 大 -> GD/SGD
6. 高频 follow-up Q&A 表:
   - Q1: L2 Ridge 闭式解 (X^TX + lambda I 永远可逆)
   - Q2: L1 Lasso 为何无闭式解 (|w| 在 0 处不可导 -> coordinate descent + soft-thresholding)
   - Q3: 共线性怎么办 (Ridge / pinv / 删特征 / PCA)
   - Q4: Batch GD vs Mini-batch vs SGD 三者对比 (噪声 / 探索性 / GPU 友好性)
   - Q5: 稀疏向量未排序 (hash O(nnz1+nnz2))
7. AI 协同: 忘公式时让 AI 推导导数 + 给 closed-form 实现; 但 'X^T 是 dimension 对齐' 这种洞察自己讲

Length target: 3-5KB.

Commit: '[META-ANC-5] Add Linear Regression drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'X^TX', 'normal equation', 'Ridge', 'Lasso', 'pinv', 'closed-form'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_linear_regression -->

```

---

## T-P0-275  [P0/M]  STATUS: active

**Title**: [META-ANC-6] Compiler Optimization drawer (cost-model regression + meta-prompt + 3-stage skeleton)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='regression_inference_from_tests')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_compiler_optimization --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 5, lines 289-443).

Goal: Insert ONE problems row (db://<id> drawer) for the compiler-optimization 'reverse-engineer cost from test cases' question. This题 is meta-classic AI-trap题: the cost numbers are NOT universal -- they're problem unknowns to fit, not constants to assume.

PER-TASK CONSTANTS:
  slug = 'meta_anc_compiler_optimization'
  pattern = 'regression_inference_from_tests'
  script path = MLInterviewPrep/scripts/content_meta_anc_compiler_optimization.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='regression_inference_from_tests')

Drawer description sections:
1. 题面 + 楼主翻车回放 (GPT 推理 1/5 cost 是幻觉 -> 自己问 interviewer '有 universal 定义吗?' 答 '没有' -> 反应不过来; 这是 AI 面试最大失分模式)
2. **核心思路一句话**: 把 test cases 当 spec 的一部分而不是验证手段 -> 未知 cost 当回归问题 -> 代码优化和参数拟合是两个可分离子问题, 先固定一个推另一个
3. 三阶段骨架 (建模 / 参数拟合先假定 optimize=identity / 优化形式枚举搜索); '阶段 B 和 C 可独立验证 不要一开始耦合'
4. **Meta-Prompt 模板** (8 块: INPUT / UNKNOWNS / FEATURE EXTRACTION / EQUATIONS / SOLVE / VALIDATE / ITERATE / OUTPUT) -- 完整保留, 这是这题的金句模板
5. 配套代码骨架 (parse / optimize passes / featurize / fit lstsq / search pass combinations) -- 简化保留 5-stage 注释
6. 心法版 5 步 (面试时脑子跑的 checklist): 这题里有没有看似常数实为未知数 / test 是验证我还是定义问题 / 推规则和应用规则分两步 / 朴素模型先拟合看残差 / 残差系统性 (漏特征) vs 随机 (模型形式错)
7. **核心反射**: 'LLM 给的常数永远要问 你怎么得到这个数' -- 答 '标准做法' 且领域无标准 -> 100% 幻觉. 任何 LLM 给的没引用源的具体数值 先假设是错的.

Length target: 6-9KB. Meta-prompt 模板 + 心法 checklist 是核心 takeaway.

Commit: '[META-ANC-6] Add Compiler Optimization drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'Meta-Prompt', 'lstsq', 'IDENTITY', '残差', '幻觉', '回归'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_compiler_optimization -->

```

---

## T-P0-276  [P0/M]  STATUS: active

**Title**: [META-ANC-7] Find Words Containing drawer (5-tier brute -> KMP -> trie-prefix -> trie-substring -> AC)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='multi_pattern_string_matching')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_find_words_containing --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 6, lines 450-674). RICHEST source slice -- 7-part guide.

Goal: Insert ONE problems row (db://<id> drawer) for 'find words containing other words' question. Two-phase Anthropic-style: phase1 NO AI (analyze given code 复杂度), phase2 use AI to optimize. Showcase = 谱系思考 + AI 协作话术.

PER-TASK CONSTANTS:
  slug = 'meta_anc_find_words_containing'
  pattern = 'multi_pattern_string_matching'
  script path = MLInterviewPrep/scripts/content_meta_anc_find_words_containing.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='multi_pattern_string_matching')

Drawer description sections (compress source's 7 parts into 6-8 KB):

Part 1 -- 核心理念: AI 时代 coding 面试不考能写代码, 考能否精确指挥 AI 写正确高效代码. 5 信号 (独立分析复杂度 / 估算理论下界 / 列多层级解法 / 精确表达意图 / review AI 输出找问题).

Part 2 -- 与 AI 协作 6 步框架: Clarify (列模糊点) / Lower Bound (理论下界 Ω(N*L)) / Solution Ladder / Pick Sweet Spot (主动 propose tradeoff 比沉默选最优更专业) / 分工原则表 / Verify.

Part 3 -- 解法谱系表 (5 层完整保留):
  L0 Brute O(N^2 * L^2) (in 在 CPython 是 Crochemore-Perrin 最坏 O(L^2))
  L1 KMP O(N^2 * L) (没解决 N pattern 轮试根本问题)
  L2 前缀 Trie O(N*L) (达到下界 但只对前缀)
  L3 子串 Trie O(N*L^2) (大多数面试这层够)
  L4 Aho-Corasick O(N*L + 命中数) (KMP 多模版 -- trie + fail 指针)
  L5 后缀自动机/广义后缀树 O(N*L) (实现 200+ 行 -- 知道存在即可)

Part 4 -- AC 详解精简: 直觉 (KMP 单模 -> AC 多模共享自动机); 三组件 (trie 骨架 / fail 指针 / output 链); fail 指针定义 (P 的最长真后缀使其也是 trie 中某条路径前缀); 'she' + ['he','she','hers'] 例子; 为什么线性 (主指针每前进 1 步 fail 跳跃均摊 O(1)).

Part 5 -- 关键名词速查表 (Trie / KMP failure function / Proper border / AC / Suffix array / Suffix automaton / Z-function / Manacher / 单模 multi-pattern 算法分类).

Part 6 -- AI 协作 4 个 prompt 模板 (Clarify / Verify 复杂度 / Implement / Review) + 4 个反模式 (帮我写高效解 / 最优解是什么 / 帮我做面试题 / 这段代码哪里可优化).

Part 7 -- 完美回答模板 (澄清 -> 下界 -> 谱系 -> 选型 -> 实现 -> 验证 6 阶段话术节奏).

Length target: 8-12KB (这题源料最厚, 谱系表是命脉, 不要砍).

Commit: '[META-ANC-7] Add Find Words Containing drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'Aho-Corasick', 'fail', 'trie', 'KMP', '下界', '谱系'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_find_words_containing -->

```

---

## T-P0-277  [P0/M]  STATUS: active

**Title**: [META-ANC-8] Card Game Sum-15 drawer (5-tier greedy -> heuristic -> backtrack -> MC rollout -> expectimax DP)

**Depends-on**: None

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-1..8 problem-row tasks):

1. Idempotency policy (FIX #3 -- stable slug, not title):
   - Idempotency key for problems row = (source='Meta-AI-Native-Coding-2026-05-01', pattern='backtrack_dp_monte_carlo')
   - The `pattern` column is the STABLE SLUG -- never rewrite it. `title` may evolve for style.
   - Embed sentinel HTML comment <!-- ANC_SLUG: meta_anc_card_game_sum15 --> at top of `description` for grep-based discovery.

2. COMPANY_ID self-check (FIX #7 -- no magic numbers):
   - Script does: COMPANY_ID = session.query(Company).filter(Company.name == 'Meta').one().id
   - Assert COMPANY_ID == 31. Abort if mismatch.

3. NOOP normalization (FIX #5 -- semantic, not bytewise):
   - Before declaring [NOOP] vs [UPDATED], normalize both old + new description: strip per-line trailing whitespace, force LF line endings, collapse 3+ blank lines to 2.
   - Compare normalized strings.
   - Forbid non-deterministic sources: no datetime.now(), no unsorted set/dict iteration, no random in description generation.

4. Required-keywords assertion (FIX #8 -- content QA):
   - After UPSERT, assert ALL keywords in REQUIRED-KEYWORDS list (below) appear in description.
   - If any missing -> abort: "[META-ANC-N] missing keyword '<k>' -- regenerate".
   - Catches the failure mode where a content section gets accidentally dropped.

5. No-emoji + UTF-8 + ruff-clean: scan description for emoji chars; explicit encoding='utf-8'; ruff check passes.

6. Run-twice [NOOP] proof: run script twice; second must report [NOOP] for every row touched. Log both runs.

7. Insert pattern: SQLAlchemy SessionLocal from src.backend.database; problems-INSERT + problem_company_tags-INSERT-OR-IGNORE in single transaction; rollback on error.

8. Reference golden examples:
   - Problems-row pattern: scripts/_add_meta_oa_lc_problems.py (or any _add_*_lc_problems.py)
   - Sentinel-UPSERT pattern: scripts/content_interview_harmful_content_detection.py (META-SD-2)

PER-TASK FIELDS BELOW.

Source: MLInterviewPrep/docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 7, lines 684-770).

Goal: Insert ONE problems row (db://<id> drawer) for the card-game pick-3-summing-to-15 question. 4-question ladder: UT debug -> naive strategy -> simulate measure -> optimize. 经典 AI-trap: 楼主'看了一眼没认真 validate 就贴' = AI 面试最大失分点.

PER-TASK CONSTANTS:
  slug = 'meta_anc_card_game_sum15'
  pattern = 'backtrack_dp_monte_carlo'
  script path = MLInterviewPrep/scripts/content_meta_anc_card_game_sum15.py
  idempotency key = (source='Meta-AI-Native-Coding-2026-05-01', pattern='backtrack_dp_monte_carlo')

Drawer description sections:

1. 题面 + 关键常数 (36 张 = 1..9 各 4 张; 初始 16 张; 完美局 12 对 = 180 分; 13 种合法 rank multiset 列出: (1,5,9)(1,6,8)(1,7,7)(2,4,9)... 全 13 条).

2. 澄清 4 问 (开场必问, 这是 senior signal): 数值能否重复 / 花色须互异 / 输入信息是上帝视角还是只台面 / 终止条件 (台面无 valid triple = game over, 不必等牌库空).

3. 分级解法表 (5 tier 完整保留, 中文 + 复杂度 + 完美率 + 面试用途):
   T1 Naive Greedy (~20-40%) baseline
   T2 Heuristic Greedy (优先拿瓶颈 rank 已堆 4 张 / 不灵活 rank 1 和 9) (~50-60%) 性价比之王
   T3 Table-only Backtrack (DFS+memo, 忽略补牌) (~60%)
   T4 Monte Carlo Rollout (每候选 triple 跑 K 次随机 rollout 取均值) (~80%+) 首选实战
   T5 真 Expectimax DP (state=(table,deck) 对超几何分布求期望) 最优 -- 只口述不写

4. T5 DP 思路口述模板 (state 设计 / Bellman 方程 / 多元超几何分布 draw / 目标=期望分 vs 满分概率两种 Bellman / 状态空间 ~10^6 reachable, Python 慢 C++ 可 -> 实战取 MC rollout 采样近似).

5. Implementation pitfalls 对照表 (mutable default {} 共享坑 / @lru_cache 一行解决 / memo 不必传参 / rank-level DP + 花色 filter 分离).

6. AI 协作 Meta-Prompt 4 步 (CLARIFY 不动键盘 / TIER 口头报 1->5 选 T4 实战 / NARRATE AI 出代码 -> 你读 -> 对面试官讲 X 因为 Y -> 再 paste / BUFFER 留 5 分钟 validate 宁可 T2 讲透不要 T5 贴爆).

7. 一句话防呆: '看了一眼没认真 validate 就贴进去是 AI 面试最大失分点 -- 算法选你 hold 得住的那一档'.

8. 备考迁移 (3Sum / subset-sum / partition-k-subsets 枚举骨架 / Backtrack+memoization 模板 / MC rollout / MCTS 入门 / state 压缩 tuple+lru_cache).

Length target: 5-8KB.

Commit: '[META-ANC-8] Add Card Game Sum-15 drawer (Meta AI-Native Coding inventory)'
REQUIRED-KEYWORDS (FIX #8 content QA -- script must assert all present):
  'Monte Carlo', 'Expectimax', 'rollout', 'lru_cache', 'validate', '澄清'
REQUIRED-SENTINEL: <!-- ANC_SLUG: meta_anc_card_game_sum15 -->

```

---

## T-P0-278  [P0/M]  STATUS: active

**Title**: [META-ANC-9] Hub doc -- AI Native Coding Inventory & Cheat Sheet (cd:// company_document)

**Depends-on**: T-P0-270,T-P0-271,T-P0-272,T-P0-273,T-P0-274,T-P0-275,T-P0-276,T-P0-277

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-9 hub-doc task):

1. Idempotency policy (FIX #3 -- sentinel-only, drop content_hash):
   - Key = (company_id=COMPANY_ID, content LIKE '%META_AI_NATIVE_CODING_INVENTORY_20260501%')
   - The sentinel HTML comment is the ONLY discovery key.
   - DO NOT use content_hash (fragile) or title (style-drift risk).

2. COMPANY_ID self-check (FIX #7): query by name, assert ==31.

3. 8-problem ID discovery: SELECT id, title, pattern, source FROM problems WHERE source='Meta-AI-Native-Coding-2026-05-01' ORDER BY id. Expect EXACTLY 8 rows. If <8: abort "[META-ANC-9] only N drawers found, expected 8 -- run META-ANC-1..8 first".

4. NOOP normalization (FIX #5): semantic compare.

5. Required-keywords assertion: hub content must contain ALL of: ['Maze', 'Max Unique', 'Friend Recommendation', 'Sparse Matrix', 'Linear Regression', 'Compiler', 'Find Words', 'Card Game', '跨题', '离场', 'cd://', 'db://']. Plus assert exactly 8 db:// links present.

6. No-emoji + UTF-8 + ruff-clean (same as problem-row).

7. Run-twice [NOOP] proof.

8. Insert pattern: SessionLocal + UPSERT into company_documents. doc_kind='hub_doc', source_type='manual', is_golden=0.

PER-TASK FIELDS BELOW.

Source: depends on T-P0-270..277 having inserted 8 problems rows with source='Meta-AI-Native-Coding-2026-05-01'.

Goal: Insert ONE company_documents row that becomes a cd://<id> drawer hub for the 8 AI Native Coding problems. Mirrors the Meta-OA hub doc id=80 pattern (drawer-link cards + 跨题 共通考点 + 离场 cheat sheet).

PER-TASK CONSTANTS:
  script path = MLInterviewPrep/scripts/content_meta_anc_inventory_hub.py
  sentinel = '<!-- META_AI_NATIVE_CODING_INVENTORY_20260501 -->'
  doc_kind = 'hub_doc', source_type = 'manual', is_golden = 0
  title = '[Meta] AI-Native Coding Inventory & Cheat Sheet (2026-05-01)'

Hub doc content sections (Chinese narration + English terms; sentence-fragment golden voice; markdown):

1. Front-matter HTML comment marker: <!-- META_AI_NATIVE_CODING_INVENTORY_20260501 -->

2. Header + 用法 (考前/round 间扫这一页; 8 张速查卡片下方; 点 [打开完整题解] 链接 drawer 弹出; ESC 关闭).

3. **快速跳转** 一行 db:// links (8 个).

4. **8 题速查表** (table 列: # / 题目 / 类型 / 最优复杂度 / 核心技巧 / 完整题解 db:// link). 数据从 problems 表实际 query 出来填.

5. 每题速览段落 (each ~6-10 lines, 提炼最关键 3-5 个 bullet, 末尾 [打开完整题解 -> <title>](db://<id>) 链接).

6. **跨题 共通考点** (5-7 条):
   - 状态空间设计是核心考点 (Maze / Card / Max Unique 三题都吃这点)
   - 复杂度自己复算 (AI 给的复杂度公式 100% review 一遍 -- Compiler / Find Words 都中过 trap)
   - 理论下界先想 (Find Words 的 Ω(N*L) / Card 的状态空间 ~10^6)
   - 离散+连续混合时分两步: 先固定一个推另一个 (Compiler 阶段 B/C 解耦)
   - LLM 给的常数没引用源 = 默认是错的 (Compiler 反射 / Maze 复杂度复算)

7. **临场 prompt 写作 4 模板** (Clarify 列模糊点 / Verify 复杂度 / Implement 给算法名+约束+边界 / Review 检查复杂度 + edge case + 易追问行号) -- 复用 Find Words 那 4 个模板.

8. **AI 协作分工通则** (做对 vs 翻车 对照表 -- 状态空间设计自己 / 样板代码 AI / 复杂度推导自己 / 边界 case AI 生成 / Review 自己).

9. **离场 60s checklist** (每场 round 结束前自检 5 条):
   - 我开口第一句是 clarification 还是 high-level idea?
   - 心里的图被 interviewer 看到了吗 (不止 AI 文本)?
   - 主动指出过 AI 输出的 1+ 个问题吗?
   - 对每个选择讲过 tradeoff 吗?
   - 做最终 validate 而非盲贴吗?

10. **AI 面试最大失分模式** (3 条 tombstone): (a) Card Game '看了一眼没认真 validate 就贴' (b) Compiler 'LLM 给常数 没问怎么得到' (c) Friend Recommendation 沉默 paste-试-paste-试 -- 没外化思考过程.

Length target: 8-12KB.

Commit: '[META-ANC-9] Add AI-Native Coding Inventory hub (cd://<id>)'
```

---

## T-P0-279  [P0/S]  STATUS: active

**Title**: [META-ANC-10] Wire AI Native Coding hub into existing onsite-prep hub (id=82, append §T5)

**Depends-on**: T-P0-278

**Description**:

```
[CRITICAL Invariant 3 + v3 review fixes]

PROTOCOL (META-ANC-10 wire-in -- HIGHEST RISK, edits golden cd://82):

1. MANDATORY backup BEFORE any modification (FIX #4 -- priority-1 fix per reviewer):
   - First action: dump_path = f'data/backups/cd_82_anc_wirein_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.md'
   - Write current cd://82 content to dump_path. Log path. Abort if backup write fails.
   - Without backup, wire-in failure has NO rollback.

2. Two-phase sentinel-anchor approach (FIX #4 -- replaces fragile cd://89 string-grep):
   - Phase 1 (anchor install, idempotent): If <!-- ANC_WIREIN_AFTER --> NOT present, insert it after the line containing (cd://89). If (cd://89) not found, abort -- means cd://82 structure changed.
   - Phase 2 (content insert/replace, sentinel-bracketed): Split content on <!-- ANC_WIREIN BEGIN --> ... <!-- ANC_WIREIN END -->. If markers exist, replace inner content. Else append after <!-- ANC_WIREIN_AFTER -->.

3. Idempotency key: full sentinel-bracketed block must be byte-identical between runs (after NOOP normalize per FIX #5). No datetime.now() in inserted content.

4. COMPANY_ID self-check + cd://82 sanity: query Meta.id == 31; AND assert id=82 doc has title LIKE '%AI-Native Onsite Prep%'.

5. New hub id discovery: SELECT id FROM company_documents WHERE company_id=COMPANY_ID AND content LIKE '%META_AI_NATIVE_CODING_INVENTORY_20260501%'. Expect exactly 1. Abort otherwise.

6. Schedule table edit (also two-phase, sentinel-bracketed):
   - Phase A: Wrap existing AI-Native Coding rowspan cell with <!-- ANC_SCHED BEGIN --> ... <!-- ANC_SCHED END --> if not present.
   - Phase B: Replace content within ANC_SCHED markers to include cd://<new_hub_id> link.

7. Run-twice [NOOP] proof: critical here. Second run must show ALL phases NOOP. If not, sentinel logic broken -> data drift risk.

8. Required-keywords assertion: post-update, cd://82 contains ['§T5', f'cd://{new_hub_id}', 'AI-Native Coding Problem Inventory', '<!-- ANC_WIREIN BEGIN -->', '<!-- ANC_WIREIN END -->'].

9. DRY-RUN mode: support --dry-run flag. In dry-run, do backup + Phase 1 + Phase 2 in-memory but don't write to DB; print diff. Default is wet-run.

PER-TASK FIELDS BELOW.

Source: depends on T-P0-278 having created the AI Native Coding Inventory hub doc.

Goal: Edit company_documents id=82 ('[Meta] AI-Native Onsite Prep (2026-05-01)' -- the golden hub the user reads day-of) to add a new §T5 reference linking to the new AI Native Coding Inventory drawer (cd://<new_hub_id>). This wires the new inventory into the day-of reading flow.

PER-TASK CONSTANTS:
  script path = MLInterviewPrep/scripts/patch_meta_onsite_hub_anc_wirein_20260430.py
  target = company_documents id=82 (golden onsite-prep hub)
  backup path template = data/backups/cd_82_anc_wirein_<UTC-ISO>.md
  anchor sentinel = '<!-- ANC_WIREIN_AFTER -->'
  content bracket = '<!-- ANC_WIREIN BEGIN --> ... <!-- ANC_WIREIN END -->'
  schedule bracket = '<!-- ANC_SCHED BEGIN --> ... <!-- ANC_SCHED END -->'
  CLI flag: --dry-run (default off)

Acceptance:
- id=82 content now contains '§T5' and 'cd://<new_hub_id>' string
- The schedule table for 11:00 + 13:00 rows links to the new inventory
- Idempotent: if §T5 already present, replace cd://<id> if it changed but don't double-insert

Per memory feedback_sync_all_surfaces: this IS the day-of surface; sync it.

Commit: '[META-ANC-10] Wire AI-Native Coding inventory into onsite-prep hub (cd://82 §T5)'
```

---
