# MLE Interview Prep System — Technical Design

## 1. 技术栈选型

| 层次 | 选型 | 理由 |
|------|------|------|
| Frontend | React (Vite) + Tailwind CSS | 快速开发，组件化，丰富生态 |
| Backend | Python FastAPI | 异步性能好，类型安全，与ML生态无缝衔接 |
| Database | SQLite (via SQLAlchemy) | 零配置，单文件便携，够用 |
| LLM | Anthropic API (Claude Sonnet) | 速度快，成本低，代码/ML理解力强 |
| Scraper | Playwright (Python) | 现代，headless，反检测能力优于Selenium |
| 部署 | 本地 Docker Compose 或裸跑 | 个人工具，不需要云部署 |

## 2. 数据库 Schema

```sql
-- ============================================================
-- Module 1: LeetCode Tracker
-- ============================================================

CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 基本信息
    leetcode_id INTEGER,              -- LC 题号 (nullable, 非LC题为空)
    title TEXT NOT NULL,
    url TEXT,
    difficulty TEXT CHECK(difficulty IN ('easy','medium','hard')),
    -- 分类标签
    tags TEXT,                         -- JSON array: ["array","two-pointers","sliding-window"]
    pattern TEXT,                      -- 主 pattern: "sliding_window", "bfs", "dp_knapsack"...
    category TEXT DEFAULT 'algorithm', -- "algorithm" | "ml_coding" | "system_design"
    -- 来源追踪
    source TEXT,                       -- "blind75", "neetcode150", "company_tag", "interview_report"
    company_tags TEXT,                 -- JSON array: ["google","uber","airbnb"]
    -- 状态
    priority INTEGER DEFAULT 2,        -- 1=must_do, 2=should_do, 3=nice_to_have
    is_completed BOOLEAN DEFAULT FALSE,
    comfort_level INTEGER DEFAULT 0,   -- 0=未做, 1=勉强, 2=需要提示, 3=能做出, 4=熟练, 5=秒杀
    -- 时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_attempted_at TIMESTAMP,
    next_review_at TIMESTAMP           -- 间隔重复调度
);

CREATE TABLE attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL REFERENCES problems(id),
    -- 本次尝试
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER,          -- 用时（秒）
    result TEXT CHECK(result IN ('solved','hint','failed','timeout')),
    -- 自评
    approach_notes TEXT,               -- 简短记录思路 (markdown)
    complexity_time TEXT,              -- "O(n log n)"
    complexity_space TEXT,             -- "O(n)"
    -- LLM 交互
    llm_review TEXT,                   -- LLM 给出的 review (JSON: {verdict, optimal_approach, feedback})
    -- 间隔重复
    comfort_after INTEGER,            -- 做完后的 comfort_level (1-5)
    
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);

-- 快问快答对话记录
CREATE TABLE qa_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER REFERENCES problems(id),  -- nullable: 可以是独立问答
    topic TEXT,                         -- "sliding_window", "transformer_attention", etc.
    messages TEXT NOT NULL,             -- JSON array: [{role, content, timestamp}]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT                        -- LLM 生成的 session 总结
);

-- ============================================================
-- Module 2: Interview Experience Scraper
-- ============================================================

CREATE TABLE seed_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    source_site TEXT NOT NULL,          -- "blind", "1point3acres", "leetcode_discuss", "glassdoor"
    company TEXT,                       -- target company filter
    role_filter TEXT,                   -- "mle", "ml_engineer", "applied_scientist"
    is_active BOOLEAN DEFAULT TRUE,
    last_checked_at TIMESTAMP,
    check_interval_hours INTEGER DEFAULT 24,  -- 检查频率
    content_hash TEXT                   -- 页面 hash，检测变更
);

CREATE TABLE scraped_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seed_url_id INTEGER REFERENCES seed_urls(id),
    url TEXT NOT NULL,
    raw_html TEXT,                      -- 压缩存储原始 HTML
    extracted_text TEXT,                -- 清洗后的纯文本
    content_hash TEXT NOT NULL,         -- 用于去重
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(url, content_hash)           -- 同一 URL 相同内容不重复存
);

CREATE TABLE interview_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scraped_page_id INTEGER REFERENCES scraped_pages(id),
    -- 提取的结构化信息
    company TEXT,
    role TEXT,                          -- "MLE", "Applied Scientist", "Research Engineer"
    level TEXT,                         -- "L4", "L5", "E5", "Senior", "Staff"
    interview_round TEXT,              -- "phone", "onsite_coding", "onsite_ml_design", "behavioral"
    year INTEGER,
    -- 题目
    question_text TEXT NOT NULL,
    question_type TEXT,                 -- "coding", "ml_theory", "ml_system_design", "behavioral", "ml_coding"
    -- 关联
    tags TEXT,                          -- JSON array
    mapped_framework_node_id INTEGER REFERENCES framework_nodes(id),
    -- 状态
    is_reviewed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    difficulty_estimate TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Module 3: Framework Progress Tracker
-- ============================================================

CREATE TABLE framework_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 层级结构
    parent_id INTEGER REFERENCES framework_nodes(id),
    path TEXT NOT NULL UNIQUE,          -- "pillar1.coding.dp.knapsack" (materialized path)
    depth INTEGER NOT NULL DEFAULT 0,   -- 0=pillar, 1=category, 2=subcategory, 3=topic
    -- 内容
    title TEXT NOT NULL,
    description TEXT,
    -- 权重与优先级
    importance REAL DEFAULT 1.0,        -- 0.0-1.0, 基于公司覆盖率计算
    priority TEXT DEFAULT 'P1',         -- P0/P1/P2/P3
    estimated_hours REAL,               -- 预估学习时间
    -- 进度
    status TEXT DEFAULT 'not_started',  -- not_started | in_progress | review | mastered
    progress_pct REAL DEFAULT 0.0,      -- 0-100
    confidence_level INTEGER DEFAULT 0, -- 0-5
    -- 公司关联
    relevant_companies TEXT,            -- JSON array: ["google","uber"]
    -- 时间
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_studied_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学习记录
CREATE TABLE study_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_node_id INTEGER NOT NULL REFERENCES framework_nodes(id),
    date DATE NOT NULL,
    duration_minutes INTEGER NOT NULL,
    activity_type TEXT,                 -- "reading", "practice", "mock_interview", "review", "flashcard"
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 公司信息
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    group_tag TEXT,                     -- "llm_first", "search_ranking", "marketplace", "infra", "product_ml"
    interview_stages TEXT,             -- JSON: [{name, type, duration, notes}]
    status TEXT DEFAULT 'applied',     -- applied | phone_screen | onsite | offer | rejected
    applied_at DATE,
    notes TEXT
);

-- 公司-知识点权重矩阵
CREATE TABLE company_topic_weights (
    company_id INTEGER REFERENCES companies(id),
    framework_node_id INTEGER REFERENCES framework_nodes(id),
    weight REAL DEFAULT 1.0,           -- 该公司对该知识点的考察权重 (0-5)
    PRIMARY KEY (company_id, framework_node_id)
);

-- ============================================================
-- Views: 预计算常用查询
-- ============================================================

CREATE VIEW v_problem_stats AS
SELECT 
    p.pattern,
    p.difficulty,
    COUNT(*) as total,
    SUM(CASE WHEN p.is_completed THEN 1 ELSE 0 END) as completed,
    AVG(p.comfort_level) as avg_comfort,
    AVG(a.duration_seconds) as avg_time_seconds
FROM problems p
LEFT JOIN attempts a ON a.problem_id = p.id
GROUP BY p.pattern, p.difficulty;

CREATE VIEW v_weekly_progress AS
SELECT 
    fn.path,
    fn.title,
    fn.importance,
    fn.progress_pct,
    fn.confidence_level,
    COALESCE(SUM(sl.duration_minutes), 0) as week_minutes
FROM framework_nodes fn
LEFT JOIN study_logs sl ON sl.framework_node_id = fn.id 
    AND sl.date >= date('now', '-7 days')
GROUP BY fn.id;
```

## 3. Module 1: LeetCode Tracker — 详细设计

### 3.1 核心功能

**A. Problem Dashboard**
- 按 pattern/difficulty/company 的多维度看板
- 进度环 (Blind75 完成度, NeetCode150 完成度)
- 今日待复习队列 (基于间隔重复算法 SM-2)
- 薄弱 pattern 高亮 (comfort_level < 3 的 pattern)

**B. 计时做题界面**
- 选题后启动计时器
- 做题过程中可以记录思路笔记 (markdown)
- 完成后填写: result, complexity, comfort_level
- 自动触发 LLM review

**C. LLM 快问快答 (核心特色)**

这是最有价值的功能。设计为轻量级对话框，目标是**训练最快速地从题目到最优解的思维路径**。

```
用户流程:
1. 选择一道题 (或输入新题)
2. 用 1-3 句话描述自己的思路/approach
3. LLM 立即评价:
   - ✅ 思路正确 → 追问: "时间复杂度? 能否优化?"
   - ⚠️ 思路可行但非最优 → 提示: "考虑过 X pattern 吗?"
   - ❌ 思路有误 → 引导: "这个 edge case 会怎样?"
4. 可以继续追问，形成短对话
5. 最终 LLM 给出总结: {verdict, optimal_approach, key_insight}
```

**LLM Prompt 设计:**

```python
REVIEW_SYSTEM_PROMPT = """
You are an expert algorithm interview coach for a mid-senior MLE candidate.

Your job:
1. Evaluate the candidate's approach for correctness and optimality
2. Push them toward the OPTIMAL solution in the FEWEST exchanges
3. Be concise and direct — this is speed training, not tutoring

Rules:
- If approach is optimal: confirm, ask for complexity, suggest edge cases
- If approach works but suboptimal: hint at the better pattern (don't give full answer)
- If approach is wrong: identify the specific flaw, give a targeted hint
- Always state the optimal time/space complexity
- Reference specific patterns: sliding window, monotonic stack, union-find, etc.
- For ML coding: check mathematical correctness AND computational efficiency

Response format (JSON):
{
  "verdict": "optimal" | "suboptimal" | "incorrect" | "needs_clarification",
  "feedback": "concise feedback (2-3 sentences max)",
  "hint": "one-line hint if suboptimal/incorrect (null if optimal)",
  "optimal_complexity": {"time": "O(...)", "space": "O(...)"},
  "pattern": "the relevant algorithm pattern",
  "follow_up": "one follow-up question to deepen understanding"
}
"""
```

**D. 间隔重复 (Spaced Repetition)**

使用 SM-2 变体:
```python
def compute_next_review(comfort_level: int, previous_interval_days: int) -> int:
    """SM-2 simplified for coding problems."""
    if comfort_level <= 2:  # 不熟练，很快复习
        return 1
    elif comfort_level == 3:  # 能做但不够快
        return max(2, previous_interval_days)
    elif comfort_level == 4:  # 熟练
        return int(previous_interval_days * 2.0)
    else:  # comfort_level == 5, 秒杀
        return int(previous_interval_days * 2.5)
```

### 3.2 UI 设计要点

```
┌─────────────────────────────────────────────────────┐
│  LeetCode Tracker                     [+ Add Problem]│
├─────────────┬───────────────────────────────────────┤
│ Filters     │  Problem List / Kanban View            │
│ ☑ Blind75   │  ┌─────────────────────────────────┐  │
│ ☑ NeetCode  │  │ #3 Longest Substring    Medium  │  │
│ Pattern:    │  │ Pattern: Sliding Window          │  │
│ [Dropdown]  │  │ Comfort: ⭐⭐⭐☆☆  Last: 3d ago │  │
│ Difficulty: │  │ [Practice] [Quick Review] [Skip] │  │
│ [E][M][H]   │  └─────────────────────────────────┘  │
│ Company:    │  ┌─────────────────────────────────┐  │
│ [Multi-sel] │  │ #146 LRU Cache           Medium  │  │
│             │  │ Pattern: Design / HashMap+DLL    │  │
│ ─────────── │  │ Comfort: ⭐⭐☆☆☆  REVIEW DUE!  │  │
│ Stats:      │  │ [Practice] [Quick Review] [Skip] │  │
│ Done: 45/75 │  └─────────────────────────────────┘  │
│ Avg: ⭐3.2  │                                       │
│ Weak: DP,   │  ──── Quick Review Panel ────────── │
│ Graph       │  │ You: "Use hashmap + DLL, O(1)"  │  │
│             │  │ AI: ✅ Correct! What about       │  │
│             │  │     thread safety for concurrent  │  │
│             │  │     access?                       │  │
│             │  │ [Your reply...]          [Send]  │  │
│             │  └─────────────────────────────────┘  │
└─────────────┴───────────────────────────────────────┘
```

## 4. Module 2: Interview Experience Scraper — 详细设计

### 4.1 设计原则

```
保守策略:
- 请求间隔: 10-30 秒随机延迟
- 每日限额: 每个站点最多 20 页
- User-Agent 轮换 (3-5 个常见浏览器)
- 优先 robots.txt 遵从
- 支持手动粘贴模式 (不走爬虫)
```

### 4.2 Scraper Pipeline

```
Seed URLs → Playwright Fetch → HTML → Content Extractor → Question Extractor (LLM) → DB
    ↓              ↓                        ↓                       ↓
 Schedule    Rate Limiter           BeautifulSoup +         Anthropic API
 (cron)      + Dedup (hash)        site-specific rules     structured extraction
```

**Site-Specific Extractors:**

```python
SITE_CONFIGS = {
    "blind": {
        "base_url": "https://www.teamblind.com",
        "selectors": {
            "post_list": "div.post-item",
            "post_title": "h3.title",
            "post_body": "div.body-text",
            "next_page": "a.next-page"
        },
        "rate_limit_seconds": (15, 30),  # min, max random delay
    },
    "1point3acres": {
        "base_url": "https://www.1point3acres.com",
        "selectors": {
            "post_list": "div.thread-item",
            "post_title": "a.thread-title",
            "post_body": "div.thread-content",
        },
        "rate_limit_seconds": (20, 45),
    },
    "leetcode_discuss": {
        "base_url": "https://leetcode.com/discuss",
        "selectors": {
            "post_list": "div.topic-item",
            "post_title": "a.title-link",
            "post_body": "div.discuss-markdown-container",
        },
        "rate_limit_seconds": (10, 20),
    },
}
```

**LLM 结构化提取 Prompt:**

```python
EXTRACT_PROMPT = """
Given this interview experience post, extract ALL interview questions mentioned.

For EACH question, provide:
1. company: the company name
2. role: the role (MLE, Applied Scientist, etc.)
3. level: seniority level if mentioned
4. round: which interview round (phone, onsite coding, ML design, behavioral)
5. question_text: the actual question (preserve technical details)
6. question_type: one of [coding, ml_theory, ml_system_design, ml_coding, behavioral, general_system_design]
7. tags: relevant topic tags

Return JSON array. If no clear questions found, return [].
Example:
[
  {
    "company": "Google",
    "role": "MLE",
    "level": "L5",
    "round": "onsite_ml_design",
    "question_text": "Design a real-time spam detection system for Gmail",
    "question_type": "ml_system_design",
    "tags": ["spam_detection", "real_time", "text_classification", "gmail"]
  }
]
"""
```

### 4.3 手动收集模式

即使不用爬虫，也提供:
- **粘贴板**: 直接粘贴面经文本 → LLM 提取 → 入库
- **URL 提交**: 输入 URL → 后端 fetch → 提取 → 入库
- **批量导入**: CSV/JSON 文件上传

### 4.4 更新检测

```python
async def check_for_updates(seed_url: SeedURL):
    """轻量级检测: 只 HEAD 请求或首屏 hash 对比"""
    page = await browser.new_page()
    await page.goto(seed_url.url, wait_until="domcontentloaded")
    
    # 只取首屏关键区域的文本 hash
    content = await page.inner_text(SITE_CONFIGS[seed_url.source_site]["selectors"]["post_list"])
    new_hash = hashlib.md5(content.encode()).hexdigest()
    
    if new_hash != seed_url.content_hash:
        # 有更新 → 标记为需要完整爬取
        return True, new_hash
    return False, None
```

## 5. Module 3: Framework Progress Tracker — 详细设计

### 5.1 核心功能

**A. 知识树可视化**
- Treemap / Sunburst 展示所有 Pillar → Category → Topic
- 颜色编码: 红(未开始) → 黄(进行中) → 绿(已掌握)
- 大小编码: importance 权重 (越重要越大)
- 点击展开到具体 topic

**B. 公司优先级矩阵**
- 根据 target companies 自动计算每个 topic 的综合权重
- 权重公式: `topic_priority = Σ(company_weight[c] × topic_relevance[c][t])` 对所有 target companies c
- 可以调整公司优先级 (比如 Google onsite 下周，临时调高权重)

**C. 精力分配建议**
```python
def suggest_study_plan(target_companies: list, available_hours: float, days_until_interview: int):
    """
    基于以下因素推荐今日学习计划:
    1. topic importance (公司权重加权)
    2. current progress (越落后越优先)
    3. diminishing returns (已经 mastered 的不再分配)
    4. 间隔重复 (该复习的优先)
    5. diversity (避免连续学同类内容)
    """
    # 计算每个 topic 的 urgency score
    # urgency = importance × (1 - progress) × recency_decay × company_deadline_factor
    pass
```

**D. 学习日志**
- 每次学习记录: topic, duration, activity_type
- 自动更新 progress_pct
- 周报/月报: 时间分布、进度趋势、薄弱项提醒

### 5.2 UI 设计要点

```
┌──────────────────────────────────────────────────────┐
│  Framework Tracker                    Week 3 of 8    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─ Overall Progress ────────────────────────────┐  │
│  │  ████████████░░░░░░░░ 42%    68/162 topics    │  │
│  │  This week: 12.5 hours  │  Target: 15 hours   │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Today's Plan (auto-generated) ───────────────┐  │
│  │  1. [P0] ML System Design: RecSys      45min  │  │
│  │  2. [P0] Coding: DP patterns (3 probs) 60min  │  │
│  │  3. [P1] Transformer: attention impl.  30min  │  │
│  │  4. [P0] Behavioral: STAR story #5     20min  │  │
│  │  5. [Review] Coding: Sliding window    15min  │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Knowledge Tree (Treemap) ────────────────────┐  │
│  │  ┌──────────────┐ ┌────────┐ ┌──────────────┐│  │
│  │  │  ML System   │ │ Coding │ │   LLM/DL     ││  │
│  │  │  Design 35%  │ │  55%   │ │    28%       ││  │
│  │  │  ▓▓░░░░░░░░  │ │ ▓▓▓▓░░ │ │ ▓▓░░░░░░░░  ││  │
│  │  └──────────────┘ └────────┘ └──────────────┘│  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────────┐│  │
│  │  │Behav.│ │ Math │ │Infra │ │  ML Theory   ││  │
│  │  │ 60%  │ │ 40%  │ │ 20%  │ │    45%       ││  │
│  │  └──────┘ └──────┘ └──────┘ └──────────────┘│  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Company Deadlines ───────────────────────────┐  │
│  │  Google: Onsite in 12 days  [Focus Mode]      │  │
│  │  Uber: Phone screen in 5 days                 │  │
│  │  Airbnb: Applied (waiting)                    │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## 6. API Routes 设计

```python
# ============ Module 1: LeetCode ============
GET    /api/problems                    # 列表 (支持 filter/sort/search)
POST   /api/problems                    # 新增题目
PUT    /api/problems/{id}               # 更新题目信息
DELETE /api/problems/{id}               # 删除

POST   /api/problems/{id}/attempts      # 记录一次做题
GET    /api/problems/{id}/attempts      # 历史记录

POST   /api/problems/{id}/review        # LLM 快速 review (传入 approach text)
POST   /api/qa/chat                     # 通用快问快答 (传入 messages)

GET    /api/problems/stats              # 统计看板数据
GET    /api/problems/review-queue       # 今日待复习队列

# ============ Module 2: Scraper ============
GET    /api/scraper/seeds               # 种子 URL 列表
POST   /api/scraper/seeds               # 添加种子 URL
POST   /api/scraper/run                 # 手动触发爬取
POST   /api/scraper/paste               # 粘贴文本 → 提取
GET    /api/scraper/status              # 爬取状态

GET    /api/questions                    # 面试题列表 (支持 filter)
PUT    /api/questions/{id}              # 标记/编辑
POST   /api/questions/{id}/analyze      # LLM 分析题目 + 生成解答思路

# ============ Module 3: Framework ============
GET    /api/framework/tree              # 完整知识树
PUT    /api/framework/nodes/{id}        # 更新节点进度
POST   /api/framework/nodes/{id}/log    # 记录学习日志
GET    /api/framework/suggest           # AI 推荐今日计划
GET    /api/framework/stats             # 统计数据 (进度/时间/弱项)

GET    /api/companies                   # 公司列表及状态
PUT    /api/companies/{id}              # 更新公司状态
GET    /api/companies/{id}/focus        # 某公司的重点复习清单

# ============ 全局 ============
GET    /api/dashboard                   # 汇总首页数据
POST   /api/import                      # 批量导入 (CSV/JSON)
GET    /api/export                      # 导出所有数据
```

## 7. 项目结构

```
mle-prep/
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Settings (API keys, DB path)
│   ├── database.py                # SQLAlchemy setup + models
│   ├── models/
│   │   ├── problem.py
│   │   ├── framework.py
│   │   ├── scraper.py
│   │   └── company.py
│   ├── routers/
│   │   ├── problems.py
│   │   ├── qa.py
│   │   ├── scraper.py
│   │   ├── framework.py
│   │   └── companies.py
│   ├── services/
│   │   ├── llm_service.py         # Anthropic API wrapper
│   │   ├── spaced_repetition.py   # SM-2 算法
│   │   ├── study_planner.py       # 学习计划生成
│   │   └── question_extractor.py  # LLM-based extraction
│   ├── scraper/
│   │   ├── crawler.py             # Playwright crawler
│   │   ├── extractors.py          # Site-specific extractors
│   │   ├── scheduler.py           # Cron scheduling
│   │   └── site_configs.py        # Per-site configs
│   └── seed_data/
│       ├── blind75.json           # 预置题库
│       ├── neetcode150.json
│       └── framework_tree.json    # 预置知识树 (从你的 markdown 生成)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx       # 汇总首页
│   │   │   ├── LeetCodeTracker.jsx  # Module 1
│   │   │   ├── QuickReview.jsx      # LLM 对话组件
│   │   │   ├── FrameworkTracker.jsx  # Module 3
│   │   │   ├── InterviewQuestions.jsx # Module 2 浏览
│   │   │   └── CompanyBoard.jsx     # 公司管理
│   │   ├── components/
│   │   │   ├── ProblemCard.jsx
│   │   │   ├── Timer.jsx
│   │   │   ├── ChatPanel.jsx       # Quick Q&A 聊天框
│   │   │   ├── KnowledgeTreemap.jsx # D3 treemap
│   │   │   ├── ProgressRing.jsx
│   │   │   ├── StudyPlanCard.jsx
│   │   │   └── CompanyTimeline.jsx
│   │   ├── hooks/
│   │   │   ├── useApi.js
│   │   │   ├── useTimer.js
│   │   │   └── useSpacedRepetition.js
│   │   └── utils/
│   │       ├── api.js              # Fetch wrapper
│   │       └── constants.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   └── mle_prep.db                # SQLite 数据库文件
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 8. 实现优先级

### Phase 1 (MVP — 1-2 天)
- [ ] SQLite schema + seed data (Blind75 + 知识树)
- [ ] FastAPI 骨架 + problems CRUD
- [ ] React 基础页面 + problem list/filter
- [ ] LLM quick review endpoint (最核心功能)
- [ ] 基础 framework tree view

### Phase 2 (Core — 3-5 天)
- [ ] 做题计时器 + attempt 记录
- [ ] 间隔重复调度
- [ ] Framework progress tracking + study log
- [ ] Knowledge treemap 可视化 (D3)
- [ ] 公司管理 + deadline tracking
- [ ] 手动粘贴面经 → LLM 提取

### Phase 3 (Polish — 3-5 天)
- [ ] Playwright scraper (conservative mode)
- [ ] 更新检测 cron
- [ ] AI 学习计划推荐
- [ ] 统计 dashboard (进度趋势, 时间分布)
- [ ] 数据导入/导出
- [ ] 面试题 → 知识树节点 mapping

### Phase 4 (Nice-to-have)
- [ ] 面经题目自动匹配 LeetCode 题库
- [ ] Mock interview 模式 (LLM 扮演面试官)
- [ ] 移动端适配
- [ ] 进度分享 (生成报告图)
