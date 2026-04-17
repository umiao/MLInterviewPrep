# Integrated Company Prep Portal — 详细设计方案 (v2, 经审查修订)

> **撰写时间**: 2026-04-14
> **紧急度**: P0（Google 2026-04-17 面试 3 天倒计时）
> **状态**: 已应用审查意见 v2
>
> **v2 修订（基于 2026-04-14 code review）**:
> - Schema probes 完成：`behavioral_examples` 无 company_id（需新表）；`company_documents` 已有 content_hash+source_path (migration 18 已落)；`behavioral_questions` 有 `company_target` 字段可利用；`knowledge_cards` 无 related_* 列（T-221 需降级为 tag-based 推断）；`sync_docs_to_db.py` 当前只 UPSERT 按 target_id/slug，**不支持 create-new-row**（T-217 必须先 patch 脚本）
> - Migration runner: `src/backend/database.py::MIGRATIONS` 列表，append-only；**无 rollback**（只能手写反向 SQL）。下一个 version = 19
> - 新增字段：`company_documents.doc_kind` ENUM `(prep_note, hub_doc, recruiter_call, other)`
> - `google_attribute` → `company_attribute` 重命名（去 Google-泄漏）
> - 删除 `group_tag` 字段（职责与 hub doc 叙事重叠）
> - N+1 AC 量化：pytest + sqlalchemy event 监听 assert SQL count
> - 估算修正：10h → **14-16h**，紧急路径完成 ≈ 周三晚/周四
> - task_db 先只入 **Phase 1+2 的 6 条**（T-214..T-219），后续审计后再追加
> - `auto_from_interview_log` 枚举值保留（零成本预留）
> - T-216a `?doc=N` 深链用 Playwright/vitest 回归测试替代手动 smoke
> - Drawer 用 `navigate(..., {push: true})`；tab 切换用 `replace`

---

## 1. 执行摘要

当前 `/companies/:id/prep` 只展示 `company_documents` 表里的 markdown，无法看到：
- 最近种入 `framework_nodes` 的 ML 理论/SD 笔记（5 个 Google 新节点）
- 最近加入 `problems` 表的自定义题（7 个 Google 新题 + 改写的 LC 扩充）
- 磁盘上的 md 文件（如 `docs/company/google/2026-04-17_prep.md`、`docs/company/google/dnn_papers_gist.md`）
- `bq_improved_stories.md` 里的 `[google-g&l]` section

Google 面试 3 天后开考，必须在此之前让 Google 的 prep 页面能一站式看到所有相关内容。

本方案提出**混合聚合架构**：
- **M:N tag 表**（problem/framework_node ↔ company）做程序化聚合
- **Hub 文档**做人工策展 + 叙事引导
- **统一 API + 4-tab 前端**渲染 drawer-first 体验
- 逐步弃用现有孤立的 Questions tab

---

## 2. 当前状态审计（已验证）

### 2.1 数据分布
| 内容类型 | 位置 | Google 相关内容 | 与公司的关联 |
|---------|------|-------|------------|
| 公司文档 | `company_documents` | 1 条（id=38 recruiter call prep） | [Y] `company_id=3` |
| 编程题 | `problems` | 7 条新 custom (id 1080-1086) + LC 扩充 | [N] **无 company_id 列**（仅 `source` 字符串） |
| 理论笔记 | `framework_nodes.description` | 5 条新节点 (id 193,195,196,197,198) | [N] **无关联** |
| 磁盘 md | `docs/*.md` | 3 份 Google 相关 | [N] **未入库** |
| BQ 故事 | `behavioral_examples` | EX-02/08/17 polish | [N] 无直接 company 关联（现有 `behavioral_themes`/`question_theme_tags` 不是 per-company） |
| Knowledge cards | `knowledge_cards` + `company_card_overlays` | 已有 Google overlay 可能性未知 | [Y] `company_card_overlays.company_id` |

### 2.2 现有 Prep 页前端行为
- `PrepNotesPage.tsx / DocumentViewer` 只渲染 `company_documents`
- 支持 `?doc=N` 深链 + `lc://` / `db://` 链接 drawer（T-P1-190 / T-P0-195 加的）
- 无 problems / framework_nodes / BQ 聚合

### 2.3 结论
缺失的是**聚合层**：数据基本都存在，但没有"给定 company_id，这个公司相关的所有准备材料"的 model + API + UI。

---

## 3. 架构决策

### 3.1 核心决策：混合 tag + hub doc

#### 为什么不只用 hub doc
- 每当加新题都要改 hub doc → 维护成本高
- 无法自动 surface 新增内容
- Hub 文档越长越难阅读

#### 为什么不只用 tag
- 机器聚合的列表没有顺序、分组、叙事
- 面试前 "day 1 应该看什么" 这种需求无法表达
- 新内容可能 relevance 过低，需要人工 pin

#### 混合方案
- Tag 表负责"完整清单 + 程序化关联"
- Hub doc 负责"人工策展 + 叙事引导 + 关键推荐"
- 两者都出现在 Prep 页，用户可以自由在"详尽列表"和"策展推荐"间切换

### 3.2 M:N 表 vs JSON 列

**选 M:N 表**，原因:
1. 查询 "公司 X 的所有 core 题" = 标准 JOIN，性能好，可加索引
2. 反向查询 "题目 Y 被哪些公司 tag" 也是 JOIN
3. `relevance` / `source` / `notes` / `added_at` 等关联属性自然挂在关联上
4. 未来加字段（如 interviewer_day, last_seen_in_report）不破坏 problems 表
5. JSON 列在 SQLite 上无高效索引，百万级时会慢

**代价**:
- 多 2 张表、2 个 migration、2 个 SQLAlchemy model
- ORM 层稍复杂（但 SQLAlchemy relationship 语法很直白）

**判断**：代价可接受，好处决定性，选 M:N。

### 3.3 为何保留 knowledge_cards 体系

T-P1-185/189 已落地的 `knowledge_cards + company_card_overlays` 解决的是"跨公司共享知识卡 + 公司视角 overlay"。这是**内容层**；本方案的 tag 系统是**关联层**。互不冲突：
- Knowledge cards 继续存"核心知识点"（如 activation functions）
- Problems/framework_nodes 继续存"题目/理论深潜"
- Tag 把上述三类内容都能关联到公司
- Hub doc 把这三类推荐给用户

---

## 4. 数据层详细设计

### 4.1 Schema

```sql
-- Migration 19: add problem_company_tags
CREATE TABLE problem_company_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    relevance TEXT NOT NULL DEFAULT 'likely' CHECK(relevance IN ('core','likely','stretch')),
    source TEXT NOT NULL DEFAULT 'manual' CHECK(source IN ('manual','auto_from_doc_ref','auto_from_overlay','auto_from_interview_log')),
    group_tag TEXT,                     -- e.g. "day1_coding", "phone_screen", free-form
    notes TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, company_id)      -- one edge per pair; updates go through UPSERT
);
CREATE INDEX ix_pct_company ON problem_company_tags(company_id, relevance);
CREATE INDEX ix_pct_problem ON problem_company_tags(problem_id);

-- Migration 20: add node_company_tags
CREATE TABLE node_company_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL REFERENCES framework_nodes(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    relevance TEXT NOT NULL DEFAULT 'likely' CHECK(relevance IN ('core','likely','stretch')),
    source TEXT NOT NULL DEFAULT 'manual' CHECK(source IN ('manual','auto_from_doc_ref','auto_from_overlay')),
    group_tag TEXT,
    notes TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(node_id, company_id)
);
CREATE INDEX ix_nct_company ON node_company_tags(company_id, relevance);

-- Migration 21: add behavioral_example_company_tags (for BQ stories)
CREATE TABLE behavioral_example_company_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    example_id INTEGER NOT NULL REFERENCES behavioral_examples(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    relevance TEXT NOT NULL DEFAULT 'likely',
    source TEXT NOT NULL DEFAULT 'manual',
    google_attribute TEXT,              -- e.g. "googleyness", "leadership"（Google 专用子分类）
    notes TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(example_id, company_id)
);
CREATE INDEX ix_bect_company ON behavioral_example_company_tags(company_id, relevance);
```

### 4.2 SQLAlchemy 模型

```python
# src/backend/models.py
class ProblemCompanyTag(Base):
    __tablename__ = "problem_company_tags"
    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    relevance = Column(String, nullable=False, default="likely")
    source = Column(String, nullable=False, default="manual")
    group_tag = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    added_at = Column(DateTime, server_default=func.current_timestamp())
    problem = relationship("Problem", back_populates="company_tags")
    company = relationship("Company", back_populates="problem_tags")
    __table_args__ = (UniqueConstraint("problem_id", "company_id"),)

# 同理 NodeCompanyTag, BehavioralExampleCompanyTag
# Problem / Company / FrameworkNode / BehavioralExample 模型加对应 relationship
```

### 4.3 Relevance 语义

| 值 | 含义 | 选择判据 |
|----|------|---------|
| `core` | 面试大概率出，must-prep | 直接来源于面试录音 / 公司 recruiter 提示 / 极高频 |
| `likely` | 领域相关，中概率 | 岗位描述匹配 / 过去面经多次出现 |
| `stretch` | 边缘覆盖 | 关联知识点，做完 core/likely 再做 |

前端按 relevance 分组渲染。

### 4.4 Source 语义（溯源 + 信任度）

| 值 | 来源 | 可被覆盖 |
|----|------|---------|
| `manual` | 用户直接 tag | 最高优先级，不被 auto 覆盖 |
| `auto_from_doc_ref` | 扫 company_documents 内的 LC NNN / db://NNN 链接得到 | 可被 manual 覆盖 |
| `auto_from_overlay` | 扫 company_card_overlays 涉及到的 knowledge_card 再关联到 problems/nodes | 可被 manual 覆盖 |
| `auto_from_interview_log` | 预留：未来如果有面试实录表 | 高于 auto_from_doc_ref |

---

## 5. API 层详细设计

### 5.1 统一 Prep 聚合端点

**`GET /api/companies/:id/prep`**

Response:
```json
{
  "company": {"id": 3, "name": "Google"},
  "hub_doc": {"id": 99, "title": "Google 2026-04-17 Prep Hub", "content": "...md..."} | null,
  "documents": [
    {"id": 38, "title": "Google Recruiter Call Prep", "updated_at": "..."}
  ],
  "problems": {
    "core":    [{"id": 1081, "title": "Sum of Good Subarrays", "leetcode_id": null, "tag": {"relevance":"core","source":"manual","group":"day1_coding","notes":"user stumped previously"}}],
    "likely":  [...],
    "stretch": [...]
  },
  "framework_nodes": {
    "core":    [{"id": 195, "title": "Bias-Variance & L1/L2 Geometric View", "path": "pillar2.regularization.bias_variance_geometric", "progress_pct": 0}],
    "likely":  [...],
    "stretch": [...]
  },
  "knowledge_cards": [
    {"card": {...}, "overlay": {...}}   // 已通过 /api/knowledge_cards?company_id=N 存在
  ],
  "behavioral_stories": [
    {"example_id": 17, "title_zh": "Harsh feedback → mutual respect", "google_attribute": "googleyness", "tag": {...}}
  ]
}
```

只返 metadata + 关联字段；**content 不内联**（title + id 给前端拿去开 drawer 即可）。`hub_doc.content` 是唯一内联的（短，需要顶部渲染）。

### 5.2 Tag 管理端点（curator UI 预留）

- `POST /api/companies/:id/problem-tags` body: `{problem_id, relevance, source, group_tag, notes}` → UPSERT
- `DELETE /api/companies/:id/problem-tags/:problem_id`
- 同理 node-tags、example-tags

前端 MVP 用不上这几个（Phase 5 才需要 UI），但 T-2 API 设计要一次做完避免未来 breaking。

### 5.3 现有端点保留

- `/api/companies/:id/documents/*` 不动（旧前端还在用）
- `/api/knowledge_cards?company_id=N` 不动
- `/api/problems/:id` + `/api/framework/nodes/:id` 不动（drawer 继续用）

---

## 6. 前端层详细设计

### 6.1 Route & 页面

**`/companies/:id/prep`** 复用现有 `PrepNotesPage.tsx`，内部重构为 4-tab layout。

顶部（始终可见）：
- 公司名称 + logo（如果有）
- Hub doc markdown 渲染（如果 `hub_doc` 非 null）
- 快捷统计：`Coding 12 core / 8 likely / 5 stretch · Framework 5 core ...`

### 6.2 Tab 架构

| Tab | URL | 内容 | Drawer 类型 |
|-----|-----|------|-----------|
| **Docs** | `?tab=docs[&doc=N]` | company_documents 下拉选择，现有 DocumentViewer 不变 | 内嵌 MarkdownPreview |
| **Coding** | `?tab=coding[&problem=N]` | problems 按 relevance 分组，卡片列表 | ProblemDrawer（已有） |
| **Framework** | `?tab=framework[&node=N]` | nodes 按 relevance 分组 | FrameworkNodeDrawer（T-P0-186 已建） |
| **BQ** | `?tab=bq[&example=N]` | behavioral_examples tagged，按 Google attribute 分组（Google 特有） | BehavioralDrawer（新组件）|

### 6.3 组件复用

- `MarkdownPreview`：hub doc + drawer 内容 全复用
- `ProblemDrawer`：已支持 lcId/dbId；直接 reuse
- `FrameworkNodeDrawer`：T-P0-186 新建，reuse
- **`BehavioralDrawer`（新）**：包一层 SlideOverPanel + MarkdownPreview + fetch `/api/behavioral/examples/:id`，~60 行

### 6.4 URL 深链规范

单一 source of truth = URL query params。切 tab 或开 drawer 都改 URL（`navigate({search})` 非 push），刷新页面可恢复状态。

### 6.5 响应式 + A11y

- 移动端 4 tab 变 dropdown（现有 Tailwind 断点约定）
- 所有卡片 `role="button"`、`aria-label`
- Drawer 关闭 focus 回到 trigger（SlideOverPanel 已有）

---

## 7. 14 任务详单（每条有完整 AC）

---

### T-214 [P0, M, Phase 1] Migration + Models for tag tables

**目标**：落地 3 张 tag 表 + SQLAlchemy 模型，为 Phase 2+ 铺路。

**AC**
1. 新建 `src/backend/migrations/019_add_problem_company_tags.sql`、`020_add_node_company_tags.sql`、`021_add_behavioral_example_company_tags.sql`，内容严格遵循 §4.1 DDL
2. `src/backend/models.py` 加 3 个新 class + Problem/FrameworkNode/Company/BehavioralExample 反向 relationship
3. Alembic or custom migration runner 能 apply + rollback
4. 单元测试 `tests/test_tag_models.py`: create→read→update→delete + unique constraint + cascade on parent delete
5. 运行所有现有测试无回归

**依赖**：无
**风险**：现有 migration runner 是否支持顺序？先 check `src/backend/migrations/__init__.py`

---

### T-215 [P0, M, Phase 1] Unified `/api/companies/:id/prep` endpoint

**目标**：一个端点聚合 docs + 三类 tagged content + hub doc。

**AC**
1. 新路由 `src/backend/routers/companies.py::get_company_prep`
2. Response 严格遵循 §5.1 JSON schema
3. `hub_doc` 识别逻辑：company_documents 中 `title` 以 "Prep Hub" 或 frontmatter `kind: hub_doc` 标记者为 hub（最多 1 个；多个时返 most-recently-updated）
4. 三类 tagged content 按 relevance 三段式返回，每段内按 `added_at DESC`
5. N+1 查询检查：用 `selectinload` 或显式 JOIN，prep 页一次请求 <= 5 个 SQL
6. 端点单元测试 + FastAPI TestClient 集成测试（3 公司 × 各 5 tag 的 seed fixture）
7. OpenAPI schema 文档化

**依赖**：T-214
**风险**：N+1 查询 + 嵌套 relationship，必须 benchmark

---

### T-216a [P0, M, Phase 1] Frontend Coding tab + Problem drawer integration

**目标**：prep 页新增 Coding tab，按 relevance 分组渲染 tagged problems，点击开 ProblemDrawer。

**AC**
1. `PrepNotesPage.tsx` 重构为 tabbed layout（用现有 Tab 组件，如果没有新建 `components/ui/Tabs.tsx`）
2. 新增 `CodingTab` 组件：请求 `/api/companies/:id/prep` 取 `problems`，按 core/likely/stretch 三段渲染卡片
3. 卡片点击 → setSearchParams({tab:'coding', problem: id}) + 开 ProblemDrawer
4. URL 恢复：初次加载如 `?tab=coding&problem=1081` 时自动切 tab 并打开对应 drawer
5. 空态处理：tagged problems 为 0 时渲染 "No coding problems tagged for this company yet" + 链接到 curator
6. `npm run build` 通过
7. 手动 smoke: /companies/3/prep?tab=coding&problem=1081 恢复 drawer + 内容正确

**依赖**：T-215
**风险**：现有 PrepNotesPage DocumentViewer 重构可能破坏 ?doc=N 深链（回归测试必须）

---

### T-216b [P0, M, Phase 1] Frontend Framework tab + node drawer

**目标**：同 T-216a 但 Framework tab。

**AC**
1. 新增 `FrameworkTab` 组件，渲染 tagged framework_nodes 按 relevance 分组
2. 卡片点击开 FrameworkNodeDrawer（T-P0-186 已有）
3. URL `?tab=framework&node=195` 恢复
4. 卡片上显示 pillar 归属 + progress_pct 进度徽章
5. build + smoke 同 T-216a

**依赖**：T-216a（shared Tabs skeleton）
**风险**：低

---

### T-216c [P0, S, Phase 1] Frontend BQ tab + BehavioralDrawer

**目标**：同上但 BQ tab。Google 尤其需要 Googleyness 子分组。

**AC**
1. 新组件 `BehavioralDrawer.tsx`（~60 行）：SlideOverPanel + MarkdownPreview + fetch `/api/behavioral/examples/:id`
2. `BQTab` 组件渲染 tagged behavioral_examples
3. Google 专用视图：如果 `company.name == "Google"` 按 `google_attribute` (cognitive/leadership/role/googleyness) 分组；否则按 relevance
4. URL `?tab=bq&example=17` 恢复
5. build + smoke

**依赖**：T-216b
**风险**：behavioral_examples schema 是否有 markdown 内容字段需验证；如果没有可能需要 join behavioral_questions

---

### T-217 [P0, M, Phase 2] Sync Google md files → company_documents

**目标**：用 T-P1-213 的 `sync_docs_to_db.py`（已落地）把 3 份磁盘 md 入库。

**AC**
1. `docs/company/google/2026-04-17_prep.md` + `docs/company/google/dnn_papers_gist.md` 头部加 YAML frontmatter:
   ```yaml
   ---
   target_table: company_documents
   company_id: 3
   source_type: prep_note
   ---
   ```
2. `docs/bq_improved_stories.md` 的 `[google-g&l]` section 单独拆到 `docs/company/google/bq_polished_stories.md` + frontmatter（保留原文件不变以免影响通用 BQ 页）
3. 运行 `sync_docs_to_db.py --apply` 创建 3 条新 company_documents 行
4. 验证：`/api/companies/3/documents` 列表出现 3 个新 doc（或更新了现有）
5. 再次运行 sync 脚本：0 change（幂等）

**依赖**：T-P1-213 已完成
**风险**：frontmatter 语法必须和 sync 脚本一致；如果 sync 脚本没设计好 company_id 字段需要先 patch 脚本

---

### T-218 [P0, S, Phase 2] Tag 7 Google problems + 5 framework nodes

**目标**：把已生成的内容挂上 Google tag。

**AC**
1. 新脚本 `scripts/tag_google_content.py`（idempotent，基于 UPSERT）:
   - Problems (relevance=core, source=manual, group_tag='2026-04-17_onsite'):
     - 1080 Shortest Path A→B
     - 1081 Sum of Good Subarrays
     - 1082 Longest Non-dec
     - 1083 Jammed Keyboard
     - 1084 Dynamic Connectivity
     - 1086 Distributed Word Count + KNN
   - Problems (relevance=likely):
     - LC 347 Top K Frequent / LC 224 Basic Calc / LC 692 Top K Words / LC 207/210 Course Schedule / LC 770 Calc IV / LC 772 Calc III
   - Framework nodes (relevance=core):
     - 195 bias-variance
     - 196 streaming top-k
     - 197 scaling resource model
     - 198 realtime recommendation
   - Framework nodes (relevance=likely):
     - 193 AB test sample size
2. Behavioral tags (脚本也做):
   - EX-02 / EX-08 / EX-17 → Google, google_attribute 分别为 leadership / leadership / googleyness, relevance=core
3. 运行后验证：`/api/companies/3/prep` 返回的三段式 JSON 能看到上述内容
4. 再次运行：0 diff

**依赖**：T-214, T-217（hub doc 用到 problem id，建议在 hub 写完前跑）
**风险**：低

---

### T-219 [P0, S, Phase 2] 建 Google 2026-04-17 Prep Hub 文档

**目标**：写一篇叙事 hub doc 作为 prep 页顶部渲染入口。

**AC**
1. 新建 `docs/company/google/2026-04-17_prep_hub.md`（frontmatter `kind: hub_doc`, `company_id: 3`）
2. 内容结构：
   - 顶部：日程 + 3 天倒计时
   - Round 1 ML Basics：关键话题清单 + 链接到 framework_node id 195/196/197/198/193
   - Round 1 补充题：链接到 LC 347/692/207/210 problems (db://id)
   - Round 2 G&L：3 个 polished 故事链接 + 典型问题预测
   - Onsite Coding：7 个 custom problem 链接
   - Last-minute 心态：提醒列表
3. 运行 `sync_docs_to_db.py --apply` 入库
4. 验证 `/api/companies/3/prep.hub_doc` 返回该文档
5. 前端 smoke（依赖 T-216a）：/companies/3/prep 顶部渲染该 hub

**依赖**：T-217, T-218
**风险**：T-216a/b/c 未完成时只能验 API 层

---

### T-220 [P1, M, Phase 3] 自动 tag 回填脚本（基于 doc ref）

**目标**：扫现有 company_documents 内的 `db://NNN`、`lc://NNN`、`[...](./pinterest/xyz.md)` 链接，自动生成 tag，覆盖 Pinterest/Uber/Adobe/LinkedIn。

**AC**
1. `scripts/autotag_from_docrefs.py`：
   - 遍历所有 company_documents，正则抽 `db://(\d+)`、`lc://(\d+)`、`/problems/(\d+)`
   - 对每个抽到的 problem_id，UPSERT `problem_company_tags (problem_id, company_id, relevance='likely', source='auto_from_doc_ref', notes='from doc_id=X')`
   - `source=manual` 的 tag 不覆盖（SQL 判断），只追加新的或升级到 manual
2. 同时扫 framework-node 引用：如 `/framework/nodes/NNN` 或 `[...](framework://NNN)`（如果有）
3. Dry-run flag 先看 diff
4. 运行后验证每个公司 `/api/companies/:id/prep` 都有非空 problems/nodes 三段式
5. 幂等：二次运行 0 变化

**依赖**：T-214
**风险**：Uber 有 4 docs，Pinterest 有 2，链接格式是否一致需先 audit；可能需要多种 regex

---

### T-221 [P1, S, Phase 3] 自动 tag from knowledge_card overlays

**目标**：T-P1-185 落地的 company_card_overlays 是天然的"公司关心这张知识卡"信号，把对应的 framework_nodes（如果 card 关联到 node）或相关 problems tag 到公司。

**AC**
1. `scripts/autotag_from_overlays.py`：
   - 对每个 overlay，查对应 knowledge_card 的 `related_problem_ids` / `related_node_ids` 字段（如果 cards 没有，先 T-220 后退到手动 mapping）
   - UPSERT tag `source='auto_from_overlay'`
2. Dry-run + 幂等

**依赖**：T-220（明确 card 是否需要加 related_* 字段）
**风险**：knowledge_cards 表结构是否有 related_* 字段需先 check

---

### T-222 [P1, M, Phase 4] Questions tab 弃用 — 审计阶段

**目标**：写 deprecation plan，不动代码。

**AC**
1. 产出 `docs/plans/questions_tab_deprecation.md`：
   - `behavioral_questions` 表当前行数 + sample rows
   - `interview_questions` 表同
   - `qa_sessions` 表同
   - 前端哪些页面 import 哪个 API 读这些表（grep）
   - 每条内容迁移目的地：
     - 纯技术 Q → framework_nodes.description 追加 Q&A section
     - 公司 BQ Q → `company_documents` 新建一条或追加到 hub
     - 通用 BQ 问题 → `behavioral_questions` 暂保留（不删）
   - 预估工作量 + 风险 + 回滚方案
2. Ticket 里附该文档

**依赖**：无
**风险**：低

---

### T-223 [P1, M, Phase 4] 执行 Questions 迁移

**目标**：按 T-222 方案迁移，旧表标 deprecated 但保留。

**AC**
1. 迁移脚本 `scripts/migrate_questions_to_new_layout.py`：按 T-222 mapping 插入新位置
2. 旧表加 `_deprecated_at` 列 + 运行时 `deprecated_at=now()` 防再写入（SQLAlchemy level warning）
3. 前端所有 Questions tab 读取 API 不变但后端 log warning
4. 保留数据 90 天再删（不在此 ticket 内）

**依赖**：T-222
**风险**：高（迁移数据正确性），需 diff check

---

### T-224 [P1, S, Phase 4] 前端移除 Questions tab

**目标**：导航隐藏 Questions，老 URL 301 到新 prep 页。

**AC**
1. `App.tsx` 删除 `/questions` route 或保留但渲染 `<Redirect to="/companies" />`
2. `Navbar.tsx` 删 Questions 链接
3. 所有 `<Link to="/questions...">` 追踪删除
4. build 通过

**依赖**：T-223
**风险**：低

---

### T-225 [P2, S, Phase 5] Curator UI：relevance promote/demote

**目标**：前端 prep 页内编辑 tag。

**AC**
1. 每个卡片右上角齿轮图标 → 小 popover: `[Core | Likely | Stretch | Remove]`
2. 调用 T-215 里预留的 POST/DELETE endpoint
3. `source` 自动升级为 `manual`
4. 操作乐观 UI，失败回滚

**依赖**：T-216a/b/c
**风险**：低

---

## 8. 依赖图

```
T-214 ──> T-215 ──> T-216a ──> T-216b ──> T-216c ──> (frontend 完整)
  │          │          │
  │          │          └────> T-217 ──> T-218 ──> T-219 (Google 紧急完)
  │          │
  │          └────> T-220 ──> T-221 (auto-tag 完)
  │
  └────> T-222 ──> T-223 ──> T-224 (Questions 弃用完)

T-225 独立，依赖整个 Phase 1 完成
```

**关键路径（Google 面试前）**：T-214 → T-215 → T-216a → T-217 → T-218 → T-219

估算：214 (2h) + 215 (2h) + 216a (3h) + 217 (1h) + 218 (1h) + 219 (1h) = **~10 工作时**（autonomous 串行大概 2-3 轮 orchestrator）

216b/c 可以和 Google 紧急并行跑，周五前做完即可。

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| T-215 API N+1 查询 | 性能退化 | 强制 selectinload + SQL count 测试 |
| T-216a 重构破坏 ?doc=N 深链 | 老用户流程坏 | 保留 DocumentViewer 不动，tabbed layout 外包 |
| T-218 tag 数据错位 | prep 页显示不相关题 | tag script 先 dry-run 让你 review，再 apply |
| T-220 regex 漏抓 | Phase 3 聚合不完整 | 先手抽样 2 公司验证 regex 后再 scale |
| T-223 Questions 数据丢失 | 旧 BQ 失联 | 旧表不删只标 deprecated，至少保 90 天 |
| autonomous session context 耗尽 | 任务中途失败 | 已预拆 T-3 → 3a/b/c，每条 ≤ M |

---

## 10. 决策点（等 user 批）

1. **Tag 表是 3 张还是 2 张**？BehavioralExample 如果当前 schema 已支持 company 关联可跳过 Migration 21。需要先 probe。
2. **T-3 是否拆成 3a/b/c**？我强烈建议拆。
3. **Google 紧急路径是否只做 T-214/215/216a/217/218/219**（忽略 216b/c 到周日再做）？
4. **是否预留"tag `source=auto_from_interview_log` 未来接面试录音"字段**？值得，几乎免费。
5. **Questions tab 的 3 张表（behavioral_questions / interview_questions / qa_sessions）是否全部弃用**，还是选择性保留？Phase 4 审计 T-222 会给出建议，但大方向可以先定。

---

## 11. 立即可开跑的子集（如果批了）

批准后顺序：
1. `task_db.py batch` 一次性加 14 条
2. `autonomous_run.sh` 跑 T-214 → T-215 → T-216a → T-217 → T-218 → T-219 （**6 session = Google 紧急路径**）
3. 检查 `/companies/3/prep` 能看到完整聚合
4. 第二轮跑 T-216b/c + T-220/221（Uber/Pinterest 准备完）
5. 第三轮 T-222 审计后决定 T-223/224

---

## 12. 不在本方案范围（显式排除）

- 不删任何现有数据（archive only）
- 不重构 `knowledge_cards` / `overlays`（它们继续服务内容层）
- 不改 `/framework` 独立页行为（仍是全局 tree 视图）
- 不改 `/problems/:id` 独立页（仍可直达）
- 不做面试录音自动入库（留作未来字段预留）
- 不做 A/B test on 用户是否点击推荐（留作 Phase 6 策展智能）
