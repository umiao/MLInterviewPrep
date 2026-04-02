"""Enrich LinkedIn doc#26 (Question Index) -- System Design Q36-Q47.

Task: T-P0-262 (Part 4/4)
Adds comprehensive solutions for system design questions Q36-Q47.
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_content(conn: sqlite3.Connection) -> str:
    """Read doc#26 content."""
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=26")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#26 not found")
        sys.exit(1)
    return row[0]


def enrich(content: str) -> str:
    """Apply enrichments to System Design questions Q36-Q47."""

    # ── Q36: Job Quality Metrics ──
    content = content.replace(
        """**题目**: What metrics would you design to measure job quality on LinkedIn? How would you define a 'high-quality' job posting, and what data signals would you use to measure and rank job posting quality?

---

### Q37.""",
        """**题目**: What metrics would you design to measure job quality on LinkedIn? How would you define a 'high-quality' job posting, and what data signals would you use to measure and rank job posting quality?

**解答**:

**Job Quality Definition (职位质量定义)**:
高质量 job posting = 信息完整 + 真实有效 + 对求职者有吸引力 + employer 积极响应

**Metrics Framework**:

**1. Posting Completeness (信息完整度)**:
- 必填字段覆盖率: title, company, location, description, requirements, salary range
- Description length & richness: 字数、是否包含 responsibilities/qualifications/benefits
- Score: weighted sum of filled fields (salary range 权重高因为用户最关心)

**2. Engagement Signals (用户参与信号)**:
- CTR: impressions -> clicks ratio (高 CTR = 标题和描述吸引人)
- Apply rate: clicks -> applications ratio
- Save/bookmark rate: 表示用户认为值得考虑
- Time on page: 长停留 = 认真阅读 (区分于快速 bounce)

**3. Employer Responsiveness (雇主响应度)**:
- Response rate: 收到申请后多久回复
- Interview rate: applications -> interviews ratio
- Ghosting rate: 申请后无任何反馈的比例 (越低越好)

**4. Outcome Signals (结果信号)**:
- Hire rate: 该 posting 最终是否成功招到人
- Time to fill: 从发布到招满的时间
- Retention: 通过该 posting 招到的人是否留任 6+ 个月

**5. Negative Signals (负面信号)**:
- Report/flag rate: 用户举报虚假/误导性 posting
- Duplicate detection: 同一 posting 反复发布 (可能是 spam)
- Salary accuracy: 面试后实际薪资与 posting 差异

**Composite Score**: Quality = w1*Completeness + w2*Engagement + w3*Responsiveness - w4*NegativeSignals

---

### Q37."""
    )

    # ── Q37: Client Company Identification ──
    content = content.replace(
        """**题目**: How would you identify potential client companies for LinkedIn's sales solutions (Sales Navigator, advertising, recruiting tools)? What features and metrics would you use to score and prioritize companies, and how would you build a CRM-style scoring model?

---

### Q38.""",
        """**题目**: How would you identify potential client companies for LinkedIn's sales solutions (Sales Navigator, advertising, recruiting tools)? What features and metrics would you use to score and prioritize companies, and how would you build a CRM-style scoring model?

**解答**:

**Lead Scoring Model (线索评分模型)**:

**1. Company Features (公司特征)**:
- **Firmographics**: industry, size (employee count), revenue, location, growth rate
- **LinkedIn Presence**: company page followers, content posting frequency, employee profile completeness
- **Hiring Activity**: job postings on LinkedIn, recruiter seat count, InMail volume
- **Current Spend**: 是否已是 LinkedIn 广告客户? 当前 spend level?

**2. Engagement Signals**:
- Company page admin activity (更新频率)
- Employee advocacy: 员工在 LinkedIn 上的活跃度
- Sales Navigator trial usage / demo requests
- Website visits to LinkedIn business solutions pages (if tracking available)

**3. Propensity Model**:
- **Training data**: 历史成交客户 (positive) vs 未成交 leads (negative)
- **Model**: Gradient boosted trees (XGBoost) -- 处理 mixed features 好，可解释
- **Output**: propensity score (0-1) + segment label (hot/warm/cold)

**4. Scoring Framework**:
```
Lead Score = Fit Score (40%) + Engagement Score (30%) + Timing Score (30%)
```
- **Fit Score**: 公司规模、行业、增长率是否匹配目标客户画像
- **Engagement Score**: 与 LinkedIn 产品的互动程度
- **Timing Score**: 是否在采购窗口期 (如 fiscal year start, headcount expansion)

**5. Prioritization**: 按 score 排序分配给 sales team。High score + recent engagement = 优先联系。

---

### Q38."""
    )

    # ── Q38: Keyword Search System ──
    content = content.replace(
        """**题目**: Design a keyword search system for LinkedIn that surfaces the most popular/relevant posts. How would you rank search results for content search? Discuss relevance signals, personalization, and cost metrics for search (cost per search, infrastructure cost per query).

---

### Q39.""",
        """**题目**: Design a keyword search system for LinkedIn that surfaces the most popular/relevant posts. How would you rank search results for content search? Discuss relevance signals, personalization, and cost metrics for search (cost per search, infrastructure cost per query).

**解答**:

**Architecture**:

**1. Indexing Layer (索引层)**:
- **Inverted Index**: 对所有 posts 的文本内容建立倒排索引 (term -> list of post_ids)
- **Real-time Index**: 新 post 发布后几秒内可搜索 (使用 Lucene/Elasticsearch 的 near-real-time refresh)
- **Field-specific Indexing**: title, body, author_name, hashtags 分别索引，支持 field-weighted scoring

**2. Ranking Signals (排序信号)**:
- **Text Relevance**: BM25 score (term frequency, inverse document frequency, document length normalization)
- **Popularity**: likes, comments, shares, views (time-decayed)
- **Freshness**: 发布时间 decay (recent posts 权重更高)
- **Author Authority**: follower count, engagement rate, topic expertise
- **Personalization**: user-author connection degree, shared industry/skills, past engagement with similar content

**3. Ranking Formula**:
```
Score = w1*BM25(query, post) + w2*Popularity_decay(post) + w3*Freshness(post) + w4*Personalization(user, post)
```
权重通过 LTR (Learning to Rank) 模型从 click-through 数据学习

**4. Cost Metrics (成本指标)**:
- **Cost per search**: infra cost / total searches (target: < $0.001/search)
- **Latency**: P50 < 100ms, P99 < 500ms
- **Infrastructure cost**: compute (CPU for ranking) + storage (index size) + network
- **Optimization**: 分层 ranking (cheap recall -> expensive re-ranking), index caching, query result caching

---

### Q39."""
    )

    # ── Q39: Feature Prioritization ──
    content = content.replace(
        """**题目**: How would you decide which feature to build next for a LinkedIn product? Describe a feature prioritization framework. What data would you use to support the decision? How would you estimate impact before building?

---

### Q40.""",
        """**题目**: How would you decide which feature to build next for a LinkedIn product? Describe a feature prioritization framework. What data would you use to support the decision? How would you estimate impact before building?

**解答**:

**Prioritization Framework: RICE Score**

**R - Reach (影响范围)**: 该 feature 影响多少用户?
- 用 DAU/MAU 中的 eligible users 估算
- Example: "智能求职推荐" 影响所有 active job seekers (~100M)

**I - Impact (影响程度)**: 对每个受影响用户的影响有多大?
- Score 1-3: 1=low (slight improvement), 2=medium (noticeable), 3=high (game-changer)
- 基于 user research, competitive analysis, internal data

**C - Confidence (置信度)**: 估算的可靠程度?
- High (80%): 有 A/B test 数据或 strong analogues
- Medium (50%): user research 支持但无量化数据
- Low (20%): 纯直觉/hypothesis

**E - Effort (工程成本)**: 开发、测试、部署所需人月
- 越低越好 (分母)

**RICE Score = (Reach * Impact * Confidence) / Effort**

**Data Sources for Decision**:
1. **User Research**: surveys, user interviews, usability testing
2. **Competitive Analysis**: 竞品是否已有该功能? 用户反馈?
3. **Internal Data**: 相关功能的 engagement metrics, funnel drop-offs
4. **Market Data**: industry trends, analyst reports

**Impact Estimation Methods**:
- **Historical analogues**: 类似 feature 上线后的 metric lift
- **Fake door test**: 展示 feature 入口但不实现，测量 click rate
- **Limited rollout**: 先对 1% 用户开放，外推全量效果
- **Back-of-envelope**: 估算 funnel 改善 -> 最终 metric 变化

---

### Q40."""
    )

    # ── Q40: Profile Visit Metrics ──
    content = content.replace(
        """**题目**: Design the metrics for LinkedIn's profile visit feature. What would you measure to evaluate whether the 'Who Viewed Your Profile' feature is successful? How would you define and track feature success?

---

### Q41.""",
        """**题目**: Design the metrics for LinkedIn's profile visit feature. What would you measure to evaluate whether the 'Who Viewed Your Profile' feature is successful? How would you define and track feature success?

**解答**:

**Feature Value Hypothesis**: "Who Viewed Your Profile" 通过 social curiosity 驱动用户回访和 engagement

**1. Engagement Metrics**:
- **Feature Usage**: DAU of "Who Viewed" page, views per session
- **Notification CTR**: push/email notification about profile views -> click rate
- **Return Visit Rate**: 查看 "Who Viewed" 后 24h 内再次登录的比例
- **Session Depth**: 查看 "Who Viewed" 后是否继续浏览其他页面

**2. Downstream Actions (下游行为)**:
- **Connection Requests**: 查看 viewer profile 后发起 connection request 的比例
- **Profile Updates**: 被浏览后是否更新自己的 profile (motivated by views)
- **InMail Sent**: 是否向 viewer 发送消息
- **Premium Conversion**: "Who Viewed" 是 Premium 的核心卖点 -- 转化率

**3. User Satisfaction**:
- **NPS (Net Promoter Score，净推荐值)**: 对该功能的满意度
- **Privacy Concern Rate**: 因隐私原因关闭可见性的用户比例 (越高 = 功能可能引起不适)

**4. Success Criteria**:
- Primary: Feature DAU 占 total DAU 的 15%+
- Secondary: 使用该功能的用户 7-day retention 比不使用的高 5%+
- Guardrail: Privacy opt-out rate < 10%

**5. Premium Upsell**: 免费用户只看到最近 5 个 viewers，Premium 看到全部 -- 跟踪 upsell conversion rate

---

### Q41."""
    )

    # ── Q41: New Feature Launch Process ──
    content = content.replace(
        """**题目**: You are launching a new feature on LinkedIn. Walk through the full evaluation process: estimating potential market, determining initial data needs, defining success metrics, pre-launch steps, and post-launch user satisfaction measurement.

---

### Q42.""",
        """**题目**: You are launching a new feature on LinkedIn. Walk through the full evaluation process: estimating potential market, determining initial data needs, defining success metrics, pre-launch steps, and post-launch user satisfaction measurement.

**解答**:

**Phase 1: Pre-Launch Planning**

**Market Estimation**:
- TAM: 该 feature 的潜在用户群 (e.g., all LinkedIn users, only recruiters, only job seekers)
- SAM: 实际可触达的用户 (active users in target segment)
- Initial target: 1-5% of SAM for MVP (Minimum Viable Product，最小可行产品)

**Data Requirements**:
- 现有数据: user demographics, behavior logs, engagement patterns
- 新增数据: feature-specific event tracking (impressions, clicks, completions)
- Instrumentation plan: 定义所有 tracking events before development

**Success Metrics (OKR 框架)**:
- **Primary metric**: 直接衡量 feature 价值 (e.g., applications submitted, courses completed)
- **Secondary metrics**: engagement (usage frequency, time spent), adoption rate
- **Guardrail metrics**: 确保不伤害其他指标 (overall DAU, other feature usage, page load time)

**Phase 2: Launch Execution**

- **Staged Rollout**: 1% -> 5% -> 25% -> 100%，每阶段监控 guardrail metrics
- **A/B Test Design**: treatment vs control, 确保统计功效 (power >= 80%)
- **Feature Flags**: 随时可回滚 (kill switch)

**Phase 3: Post-Launch Evaluation**

- **Quantitative**: A/B test results, metric dashboards, cohort analysis
- **Qualitative**: in-app survey (NPS), user interviews, support ticket analysis
- **Long-term**: 30/60/90 day retention curves, LTV (Lifetime Value，用户生命周期价值) impact
- **Decision**: Ship (metrics positive), Iterate (metrics neutral), Kill (metrics negative or guardrail violated)

---

### Q42."""
    )

    # ── Q42: Job Application Tracking Schema ──
    content = content.replace(
        """**题目**: Design a database schema and system for tracking job applications on LinkedIn. Include attributes for users with applied_job, status, connections at the company, application history, etc...

---

### Q43.""",
        """**题目**: Design a database schema and system for tracking job applications on LinkedIn. Include attributes for users with applied_job, status, connections at the company, application history, etc...

**解答**:

**Schema Design**:

```sql
-- Core tables
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    headline VARCHAR(500),
    location VARCHAR(255),
    industry VARCHAR(100),
    seniority_level VARCHAR(50)
);

CREATE TABLE jobs (
    job_id BIGINT PRIMARY KEY,
    company_id BIGINT,
    title VARCHAR(255),
    description TEXT,
    location VARCHAR(255),
    salary_min INT,
    salary_max INT,
    posted_date TIMESTAMP,
    status VARCHAR(20)  -- active/closed/filled
);

CREATE TABLE applications (
    application_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    job_id BIGINT REFERENCES jobs(job_id),
    applied_date TIMESTAMP,
    status VARCHAR(30),  -- submitted/reviewed/interview/offer/rejected/withdrawn
    source VARCHAR(50),  -- search/recommendation/email_alert/referral
    resume_version_id BIGINT,
    cover_letter TEXT,
    UNIQUE(user_id, job_id)
);

CREATE TABLE application_status_history (
    id BIGINT PRIMARY KEY,
    application_id BIGINT REFERENCES applications(application_id),
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    changed_at TIMESTAMP,
    changed_by VARCHAR(20)  -- applicant/employer/system
);

-- Derived/cached for ML features
CREATE TABLE user_company_connections (
    user_id BIGINT,
    company_id BIGINT,
    connection_count INT,
    strongest_connection_degree INT,  -- 1st/2nd/3rd
    PRIMARY KEY(user_id, company_id)
);
```

**Key Design Decisions**:
- **Status History Table**: 记录状态变化轨迹，支持 funnel analysis
- **Source Tracking**: 追踪申请来源，评估各渠道效果
- **Connections Cache**: 预计算用户在目标公司的 connections 数，加速 ranking
- **Indexing**: (user_id, applied_date), (job_id, status), (company_id) 上建索引

---

### Q43."""
    )

    # ── Q43: Push Notification System ──
    content = content.replace(
        """**题目**: Design LinkedIn's push notification system for improving user engagement. Why use push notifications? Which engagement features should you focus on? Discuss time/frequency considerations, conversion funnel (notification -> open -> action), and key metrics (CPA, click notification rate, CVR).

---

### Q44.""",
        """**题目**: Design LinkedIn's push notification system for improving user engagement. Why use push notifications? Which engagement features should you focus on? Discuss time/frequency considerations, conversion funnel (notification -> open -> action), and key metrics (CPA, click notification rate, CVR).

**解答**:

**Why Push Notifications**: 将离线用户拉回平台，提升 DAU 和 engagement depth

**1. Notification Types (按价值排序)**:
- **Social**: "X viewed your profile", "X connected with you", "X endorsed your skill"
- **Content**: "Trending in your industry", "Your post got 100 likes"
- **Job**: "New jobs matching your preferences", "Your application was viewed"
- **Network**: "X started a new position", "X's work anniversary"

**2. Personalization Engine**:
- **Content Selection**: 选择对该用户最 relevant 的通知 (based on past engagement)
- **Timing Optimization**: 在用户历史 active 时段发送 (e.g., 早上通勤时间)
- **Frequency Capping**: 每日上限 (e.g., max 5 push notifications/day)
- **Channel Selection**: push vs email vs in-app，根据用户偏好

**3. Conversion Funnel & Metrics**:
```
Notification Sent -> Delivered -> Opened -> Action Taken
```
- **Delivery Rate**: delivered / sent (受 OS, device settings 影响)
- **Open Rate (CTR)**: opened / delivered (target: 10-15%)
- **CVR (Conversion Rate，转化率)**: action / opened (target: 30-50%)
- **CPA (Cost Per Action)**: infrastructure cost / total actions
- **Opt-out Rate**: 退订率 (guardrail: < 0.5% per day)

**4. Anti-Spam & Quality**:
- **Fatigue Model**: 如果用户连续 3 天不 open notifications，降低频率
- **Relevance Score**: 只发送 predicted P(open) > threshold 的通知
- **A/B Test**: 每个通知 type 独立测试 optimal frequency 和 wording

**5. Key Trade-off**: 发送更多通知 -> 短期 DAU 提升，但 long-term opt-out 率上升。用 long-term retention 而非短期 DAU 作为优化目标。

---

### Q44."""
    )

    # ── Q44: Job Application Count Drop Investigation ──
    content = content.replace(
        """**题目**: LinkedIn's job application count has dropped 10% month-over-month. How would you investigate and diagnose this problem? Walk through a structured approach: supply vs demand analysis, segment analysis, hypothesis generation, and recommended actions.

---

### Q45.""",
        """**题目**: LinkedIn's job application count has dropped 10% month-over-month. How would you investigate and diagnose this problem? Walk through a structured approach: supply vs demand analysis, segment analysis, hypothesis generation, and recommended actions.

**解答**:

**Structured Root-Cause Analysis (结构化根因分析)**:

**Step 1: Metric Decomposition (指标分解)**:
```
Applications = Job Seekers * Searches/Seeker * Jobs_Seen/Search * Apply_Rate
```
哪个因子下降了? 分解后逐一检查。

**Step 2: Supply vs Demand (供给 vs 需求)**:
- **Supply (Job Postings)**: 职位发布总量是否下降? (经济衰退? 季节性?)
- **Demand (Job Seekers)**: 搜索用户数是否下降? 搜索频率是否变化?
- 如果 supply 和 demand 都没变，问题在 conversion (apply rate)

**Step 3: Segmentation (分层分析)**:
- **By Platform**: Mobile/Desktop/App -- 某个平台的 apply flow 是否有 bug?
- **By Region**: US/EU/Asia -- 区域性下降 vs 全局?
- **By Job Category**: Tech/Finance/Healthcare -- 行业特定?
- **By User Segment**: New/Returning, Free/Premium
- **By Employer Segment**: Large/SMB, new/existing employers

**Step 4: Hypothesis Testing**:
1. **Product Bug**: 近期 deploy 是否引入 apply button 异常? -> 检查 error logs
2. **UI Change**: A/B test rollout 是否影响了 apply flow?
3. **Seasonality**: 对比去年同期是否有类似 pattern?
4. **Competition**: 竞品推出新功能抢走用户?
5. **External**: 经济/就业市场变化?

**Step 5: Action Plan**:
- **Quick fix**: 如果是 bug/UI regression -> revert
- **Feature improve**: 如果是 apply flow 摩擦 -> simplify (one-click apply)
- **Supply boost**: 如果是 job posting 下降 -> incentivize employers
- **Monitor**: 设置 alert 当 application count 下降 > 5% week-over-week

---

### Q45."""
    )

    # ── Q45: Recommended Jobs Evaluation ──
    content = content.replace(
        """**题目**: You've launched a 'Recommended Jobs' feature on LinkedIn. How would you measure its performance? What metrics would you track, and how would you compare it against other job discovery methods (search, email alerts, browsing)?

---

### Q46.""",
        """**题目**: You've launched a 'Recommended Jobs' feature on LinkedIn. How would you measure its performance? What metrics would you track, and how would you compare it against other job discovery methods (search, email alerts, browsing)?

**解答**:

**1. Feature-Level Metrics**:
- **Recommendation Quality**: CTR on recommended jobs, apply rate on recommended jobs
- **Coverage**: % of users who receive recommendations, % of jobs that get recommended
- **Diversity**: unique job categories / companies in recommendations per user
- **Freshness**: avg age of recommended jobs (应该优先推荐新发布的)

**2. Comparative Analysis (跨渠道比较)**:

| Channel | CTR | Apply Rate | Quality Signal |
|---------|-----|------------|----------------|
| **Recommended Jobs** | Track | Track | recommendation model quality |
| **Search** | Baseline | Baseline | explicit intent (用户主动搜索) |
| **Email Alerts** | Track | Track | timing + relevance |
| **Browse** | Track | Track | discovery-based |

- **Attribution**: 用户可能先通过 recommendation 看到 job，后来再 search 找到同一 job 申请 -- 需要 attribution model (last-click vs multi-touch)

**3. Incremental Impact**:
- **Key question**: Recommended Jobs 是否带来 incremental applications，还是只是 cannibalize (蚕食) search?
- 方法: A/B test -- treatment group 有 recommendations, control group 没有
- Measure: total applications (not just from recommendation channel)

**4. Long-term Metrics**:
- Job seeker retention: 使用 recommendations 的用户是否更活跃?
- Match quality: 通过 recommendations 申请的 jobs 是否有更高 interview/offer rate?
- User satisfaction: in-app survey on recommendation relevance

**5. Guardrails**:
- 不应降低 search usage (recommendations 补充而非替代 search)
- 不应增加 spam/irrelevant job impressions

---

### Q46."""
    )

    # ── Q46: Application Data Pipeline ──
    content = content.replace(
        """**题目**: Design a system to track and analyze application database attributes for LinkedIn users. Given fields like applied_job, application_status, connections_at_company, and application_history, how would you design the data pipeline and use these attributes to improve job search quality and matching?

---

### Q47.""",
        """**题目**: Design a system to track and analyze application database attributes for LinkedIn users. Given fields like applied_job, application_status, connections_at_company, and application_history, how would you design the data pipeline and use these attributes to improve job search quality and matching?

**解答**:

**Data Pipeline Architecture**:

**1. Data Ingestion (数据采集)**:
- **Event Stream**: 每次 application 状态变化生成事件 (Kafka topic: application_events)
- **Fields**: user_id, job_id, timestamp, action (apply/withdraw/status_change), new_status
- **Enrichment**: join with user profile, job posting, company data in real-time (Flink/Spark Streaming)

**2. Feature Engineering Pipeline**:
```
Raw Events -> Feature Store -> ML Models -> Job Ranking
```

| Feature | Computation | Update Frequency |
|---------|-------------|-----------------|
| application_count_30d | COUNT(applications) per user, last 30 days | Daily batch |
| apply_to_response_rate | responses / applications per user | Daily batch |
| connections_at_company | COUNT(connections) at target company | Real-time (connection changes) |
| application_history_embedding | Sequence model on past application patterns | Weekly batch |
| skill_job_match_score | Cosine similarity(user_skills, job_requirements) | On-demand |

**3. Feature Store (特征存储)**:
- **Online Store**: Redis/DynamoDB for real-time serving (low latency features)
- **Offline Store**: Hive/BigQuery for batch training data
- **Feature consistency**: 确保 training 和 serving 使用相同的 feature 计算逻辑

**4. ML Applications**:
- **Job Ranking**: 用 connections_at_company + application_history 作为 personalization features
- **Success Prediction**: 基于历史 apply->interview->offer patterns 预测成功概率
- **Smart Apply**: 推荐 "Easy Apply" vs "Full Application" based on 历史 response rate
- **Notification Trigger**: 当 application_status 变化时触发个性化通知

**5. Data Quality**: schema validation, null rate monitoring, freshness checks (stale data alert)

---

### Q47."""
    )

    # ── Q47: Keyword Search + Sponsored Results ──
    content = content.replace(
        """**题目**: Design a system for LinkedIn keyword search that surfaces the most popular posts and content. How do you define 'popular'? What ranking signals would you use? Discuss cost metrics including CPC (cost per click), cost per 1000 impressions, and cost per keyword for sponsored search results.

---

## 统计""",
        """**题目**: Design a system for LinkedIn keyword search that surfaces the most popular posts and content. How do you define 'popular'? What ranking signals would you use? Discuss cost metrics including CPC (cost per click), cost per 1000 impressions, and cost per keyword for sponsored search results.

**解答**:

**1. Popularity Definition (定义 "热门")**:
- **Engagement-weighted score**: Score = w1*likes + w2*comments + w3*shares + w4*clicks
- **Time decay**: 使用 exponential decay -- 1 天前的 engagement 权重 > 7 天前
- **Velocity**: engagement 增长速率 (trending 内容初期增速快)
- **Quality adjustment**: 低质量 viral content (clickbait) 降权

**2. Organic Ranking Signals**:
- **Query Relevance**: BM25 text match + semantic similarity (BERT embeddings)
- **Popularity Score**: 如上定义
- **Author Authority**: follower count, expertise in query topic
- **Personalization**: user-author affinity, industry match
- **Freshness**: 时间衰减，优先展示近期内容

**3. Sponsored Search (付费搜索)**:

**Auction Design (竞价设计)**:
- **Second-price auction**: 竞价者支付第二高出价 + $0.01 (incentive-compatible)
- **Ad Rank = Bid * Quality Score**: quality score 包括 predicted CTR, ad relevance, landing page quality
- 高 quality score 的广告可以用更低的出价获得更高的位置

**Cost Metrics**:
- **CPC (Cost Per Click)**: 广告主每次点击付费。CPC = Total Spend / Clicks。适合 conversion-oriented campaigns
- **CPM (Cost Per Mille)**: 每 1000 次展示的费用。CPM = (Spend / Impressions) * 1000。适合 brand awareness
- **Cost per keyword**: 特定关键词的平均 CPC/CPM。高竞争关键词 ("software engineer jobs") 价格更高

**4. Organic vs Sponsored 混合展示**:
- 明确标记 "Sponsored" / "Promoted"
- Sponsored 结果不超过 total results 的 20% (user experience guardrail)
- 监控 organic CTR 是否因 ads 增多而下降 (cannibalization)

**Revenue Optimization**: Maximize long-term revenue = short-term ad revenue + user retention value。过度广告导致用户流失，long-term 收入下降。

---

## 统计"""
    )

    return content


def main() -> None:
    """Apply enrichments and save."""
    conn = sqlite3.connect(str(DB_PATH))
    content = get_content(conn)
    original_len = len(content)

    enriched = enrich(content)

    if enriched == content:
        print("WARNING: No changes applied -- check markers")
        conn.close()
        sys.exit(1)

    conn.execute(
        "UPDATE company_documents SET content=? WHERE id=26",
        (enriched,),
    )
    conn.commit()
    new_len = len(enriched)
    print(f"OK: doc#26 enriched {original_len}c -> {new_len}c (+{new_len - original_len}c)")
    print("System Design Q36-Q47: all 12 questions enriched with full solutions")
    conn.close()


if __name__ == "__main__":
    main()
