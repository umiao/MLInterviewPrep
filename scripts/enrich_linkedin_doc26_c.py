"""Enrich LinkedIn doc#26 (Question Index) -- System Design Q24-Q35.

Task: T-P0-262 (Part 3/4)
Adds comprehensive solutions for system design questions Q24-Q35.
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
    """Apply enrichments to System Design questions Q24-Q35."""

    # ── Q24: Distributed Key-Value Store ──
    content = content.replace(
        """**解法要点**:
- Space: O(d * w), typically d=5-7, w = e/epsilon

---

### Q25.""",
        """**解答**:

**Architecture (架构)**:

**1. Sharding (分片)**:
- **Consistent Hashing (一致性哈希)**: 将 key 映射到 hash ring 上，每个节点负责 ring 上的一段范围。添加/移除节点只影响相邻分片，数据迁移量 O(K/N)
- **Virtual Nodes**: 每个物理节点映射多个虚拟节点，改善负载均衡

**2. Replication (复制)**:
- N 个 replicas per partition (通常 N=3)
- **Replica Placement**: 不同 rack/AZ (Availability Zone，可用区) 部署，容灾

**3. Consistency (一致性)**:
- **Quorum Protocol**: W + R > N 保证强一致性 (W=写入确认数, R=读取节点数, N=副本数)
- 常见配置: N=3, W=2, R=2 (强一致) 或 W=1, R=1 (高可用/最终一致)
- **Vector Clock (向量时钟)**: 每个节点维护一个版本向量，检测并发写入冲突

**4. Conflict Resolution (冲突解决)**:
- Last-Writer-Wins (LWW，最后写入者胜): 简单但可能丢失数据
- Application-level merge: 让应用层决定如何合并冲突 (如 Amazon Dynamo 的 shopping cart)

**5. Failure Handling**:
- **Hinted Handoff**: 目标节点不可用时，写入临时代理节点，恢复后转移
- **Anti-Entropy (反熵)**: 后台 Merkle Tree 比对修复不一致数据

**Key Trade-off**: CAP Theorem (CAP 定理) -- Consistency, Availability, Partition Tolerance 三选二。LinkedIn 的 Voldemort 选择 AP (高可用 + 分区容错)，牺牲强一致性。

---

### Q25."""
    )

    # ── Q25: Metrics Monitoring System ──
    content = content.replace(
        """**题目**: Design a metrics monitoring system for a large-scale distributed infrastructure like LinkedIn. Cover: choice of time-series database vs NoSQL, efficient indexing strategies for time-series data, LSM tree compaction principles, and how to collect system-level and application-level metrics from nodes and containers.

---

### Q26.""",
        """**题目**: Design a metrics monitoring system for a large-scale distributed infrastructure like LinkedIn. Cover: choice of time-series database vs NoSQL, efficient indexing strategies for time-series data, LSM tree compaction principles, and how to collect system-level and application-level metrics from nodes and containers.

**解答**:

**Architecture**:

**1. Data Collection Layer (数据采集层)**:
- **Agent-based**: 每台机器运行 metrics agent (类似 Telegraf/collectd)，采集 CPU, memory, disk, network
- **Application SDK**: 业务代码通过 SDK 上报自定义指标 (latency, error rate, throughput)
- **Push vs Pull**: Push (agent 主动发送) 适合短生命周期容器；Pull (Prometheus 模式) 适合稳定服务

**2. Ingestion & Storage (存储层)**:
- **TSDB (Time-Series Database，时序数据库)**: 专为时间序列优化
  - 写入密集: LSM Tree (Log-Structured Merge Tree) 结构，顺序写入 + 后台 compaction
  - 压缩: delta-of-delta encoding (时间戳), gorilla compression (浮点值)
  - 代表: InfluxDB, OpenTSDB, Prometheus
- **LSM Compaction**: MemTable -> L0 SSTable -> L1 -> ... 逐层合并，减少读放大
- **Data Retention**: 高精度数据保留 7 天，降采样 (downsampling) 后保留 1 年

**3. Indexing (索引)**:
- **Tag-based Index**: metric_name + tags (host, service, region) 的倒排索引
- **Time-partitioned**: 按时间分区，查询只扫描相关时间段

**4. Query & Alerting (查询与告警)**:
- **Dashboard**: Grafana 实时可视化
- **Alert Rules**: 基于阈值、趋势、异常检测 (如 3-sigma rule, EWMA (Exponentially Weighted Moving Average，指数加权移动平均))
- **Anomaly Detection**: 使用 ML 模型识别非 threshold-based 的异常模式

**Scalability**: 水平扩展存储节点 + 分片 by metric name hash。LinkedIn 的 inGraphs 系统处理 billions of metrics/day。

---

### Q26."""
    )

    # ── Q26: User Job Classification ──
    content = content.replace(
        """**题目**: Given a LinkedIn webpage showing user profile information, design a system to classify each user into a job category (e.g., software engineer, data scientist, product manager) and extract relevant attributes. How would you approach feature engineering, model selection, and handling edge cases like career changers or multi-role users?

---

### Q27.""",
        """**题目**: Given a LinkedIn webpage showing user profile information, design a system to classify each user into a job category (e.g., software engineer, data scientist, product manager) and extract relevant attributes. How would you approach feature engineering, model selection, and handling edge cases like career changers or multi-role users?

**解答**:

**1. Feature Engineering (特征工程)**:
- **Text Features**: title, headline, summary, experience descriptions -> TF-IDF (Term Frequency-Inverse Document Frequency) 或 BERT (Bidirectional Encoder Representations from Transformers) embeddings
- **Structured Features**: industry, skills (endorsed), education (degree, field), years of experience
- **Network Features**: 相似职位的 connections 比例，所在 company 的行业
- **Temporal Features**: 职位变化频率，最近职位的停留时间

**2. Model Architecture**:
- **Baseline**: Multi-class logistic regression / gradient boosted trees (XGBoost) on TF-IDF + structured features
- **Advanced**: Fine-tuned BERT on title + summary text，concat with structured features，feed into MLP (Multi-Layer Perceptron，多层感知机)
- **Label Taxonomy**: ~50-200 标准化职位类别 (可用 O*NET 或 LinkedIn 自有 taxonomy)

**3. Edge Cases (边缘情况)**:
- **Career Changers**: 使用最近的职位 (time-weighted) + skill endorsements 作为更强信号
- **Multi-role Users**: 支持 multi-label classification (每个用户可属于多个类别)，或按 primary/secondary 分类
- **Sparse Profiles**: 只有 title 没有 summary 的用户 -> 用 title 单特征模型作为 fallback

**4. Pipeline**:
- Offline batch: 定期重新分类所有用户 (daily/weekly)
- Online: 新注册用户 real-time 分类 (使用轻量模型)
- Feedback loop: 用户编辑 title/skills 时触发重新分类

**Evaluation**: Precision/Recall per category + macro-averaged F1。对高价值类别 (如 recruiter, executive) 重点关注。

---

### Q27."""
    )

    # ── Q27: Recruiter Candidate Search ──
    content = content.replace(
        """**题目**: Design a system to help LinkedIn recruiters find suitable candidates for job openings. Cover the end-to-end pipeline: understanding recruiter intent, candidate retrieval, ranking, matching, and recommendation...

---

### Q28.""",
        """**题目**: Design a system to help LinkedIn recruiters find suitable candidates for job openings. Cover the end-to-end pipeline: understanding recruiter intent, candidate retrieval, ranking, matching, and recommendation...

**解答**:

**End-to-End Pipeline**:

**1. Query Understanding (意图理解)**:
- 解析 recruiter 搜索: job title, skills, location, seniority, company type
- Query expansion: "ML Engineer" -> also search "Machine Learning", "Deep Learning", "AI Engineer"
- 使用 NLP (Natural Language Processing，自然语言处理) 提取结构化 intent

**2. Candidate Retrieval (候选人检索)**:
- **Stage 1 -- Recall (召回)**: 从 500M+ profiles 中快速筛选到 ~10K 候选人
  - Inverted index on skills, title, location
  - Embedding-based ANN (Approximate Nearest Neighbor，近似最近邻) 搜索: FAISS/ScaNN
- **Stage 2 -- Ranking (精排)**: 对 ~10K 候选人用复杂模型排序到 top 100
  - Features: skill match score, experience relevance, location fit, engagement signals (是否活跃求职)

**3. Matching Model**:
- **Two-tower model**: Recruiter intent embedding + Candidate profile embedding，计算 cosine similarity
- **Cross-attention model**: 将 job description 和 candidate profile 联合编码，捕获细粒度匹配
- **Training data**: 历史 InMail 回复 (positive), 查看但未联系 (negative)

**4. Key Features**:
- Skill overlap ratio, title semantic similarity, seniority match
- Candidate responsiveness (InMail 历史回复率)
- Geographic willingness (是否愿意 relocate)
- Network proximity (共同 connections)

**5. Trade-offs**:
- **Precision vs Recall**: Recruiter 宁可少看几个 (high precision) 也不想翻很多不相关的 (low precision)
- **Active vs Passive**: 主动求职者 vs 被动候选人的不同信号
- **Fairness**: 避免性别、年龄、种族偏差 -- 需要 bias audit 和 fairness constraints

---

### Q28."""
    )

    # ── Q28: Job Search Metrics Framework ──
    content = content.replace(
        """**题目**: Design the metrics framework for LinkedIn's job search and ranking module. What metrics would you track (click-through rate, application rate, time spent, search frequency)? What features matter most for job ranking, and how would you measure the overall health of the job search experience?

---

### Q29.""",
        """**题目**: Design the metrics framework for LinkedIn's job search and ranking module. What metrics would you track (click-through rate, application rate, time spent, search frequency)? What features matter most for job ranking, and how would you measure the overall health of the job search experience?

**解答**:

**Metrics Hierarchy (指标层次)**:

**North Star Metric**: Qualified Applications per Searcher (每个搜索者的有效申请数)

**1. Funnel Metrics (漏斗指标)**:
- **Search -> Click**: CTR (Click-Through Rate) = clicks / impressions per search
- **Click -> Apply**: Application Rate = applications / job detail views
- **Apply -> Interview**: Response Rate (需要 employer 端数据)
- **Overall**: Search-to-Apply Rate = applications / searches

**2. Engagement Metrics**:
- Search frequency per user per week
- Avg jobs viewed per session
- Time spent on job detail page (区分 reading vs bouncing)
- Save/bookmark rate

**3. Quality Metrics**:
- **Relevance**: Position of clicked job in result list (MRR -- Mean Reciprocal Rank，平均倒数排名)
- **NDCG (Normalized Discounted Cumulative Gain，归一化折损累积增益)**: 评估排序质量
- **Zero-result rate**: 搜索无结果的比例 (越低越好)
- **Pogo-sticking rate**: 点击后快速返回搜索结果的比例 (表示结果不相关)

**4. Health Metrics**:
- DAU/WAU of job search feature
- Searcher retention (7-day, 30-day)
- Job seeker -> applied -> hired 的完整转化率

**Job Ranking Features**: title match, skill overlap, location distance, company size preference, seniority match, salary range, recency of posting, employer responsiveness score

---

### Q29."""
    )

    # ── Q29: Feed Ranking System ──
    content = content.replace(
        """**题目**: Design LinkedIn's feed ranking system. What features would you consider for ranking content in a user's feed? Cover content features, user features, interaction features, and how you would balance relevance, engagement, and content diversity.

---

### Q30.""",
        """**题目**: Design LinkedIn's feed ranking system. What features would you consider for ranking content in a user's feed? Cover content features, user features, interaction features, and how you would balance relevance, engagement, and content diversity.

**解答**:

**Multi-Stage Ranking Pipeline**:

**Stage 1 -- Candidate Generation (候选生成)**:
- 来源: connections' posts, followed creators, suggested content, ads
- 从 millions 筛选到 ~1000 candidates

**Stage 2 -- Scoring (打分)**:
- 预测 P(like), P(comment), P(share), P(click), P(hide)
- Final score = weighted combination: w1*P(like) + w2*P(comment) + w3*P(share) - w4*P(hide)

**Feature Categories**:

| 类别 | 特征示例 |
|------|---------|
| **User Features** | industry, seniority, past engagement patterns, active hours |
| **Content Features** | post type (text/image/video/article), length, hashtags, language |
| **Author Features** | follower count, avg engagement rate, connection degree |
| **Context Features** | time of day, device, session depth (第几次刷新) |
| **Cross Features** | user-author industry match, user-topic affinity |

**Diversity & Quality Balance**:
- **MMR (Maximal Marginal Relevance，最大边际相关性)**: 在 relevance 和 diversity 之间 trade-off，避免连续展示同类内容
- **Content type quota**: 每个 feed session 中限制同类型内容比例 (如最多 30% video)
- **Anti-viral**: 对 low-quality viral content (clickbait) 加惩罚项
- **Creator side optimization**: 确保优质创作者获得足够曝光，维护 creator ecosystem

**Model Architecture**: Deep neural network (Wide & Deep 或 DCN (Deep & Cross Network)) with embedding layers for categorical features。LinkedIn 实际使用 multi-objective optimization 同时优化多个 engagement signals。

---

### Q30."""
    )

    # ── Q30: Job Application Rate Dropping ──
    content = content.replace(
        """**题目**: LinkedIn's job application rate has been dropping. You are given data showing the overall application funnel...

---

### Q31.""",
        """**题目**: LinkedIn's job application rate has been dropping. You are given data showing the overall application funnel...

**解答**:

**Structured Investigation Framework (结构化排查框架)**:

**Step 1: Clarify & Scope (澄清)**:
- 定义 "application rate" = applications / job views? or applications / active users?
- 时间范围: 突然下降还是渐进趋势?
- 全局 vs 局部: 所有市场/平台都下降还是某个 segment?

**Step 2: Funnel Decomposition (漏斗分解)**:
```
Job Search -> Job Impression -> Job Click -> Job Detail View -> Apply Click -> Submit Application
```
找到哪一步的转化率下降最大

**Step 3: Segmentation Analysis (分层分析)**:
- **By Platform**: Mobile vs Desktop vs App (例如新版 App 的 apply button 位置变了?)
- **By Geography**: 某个市场的下降可能源于季节性或竞争
- **By User Type**: New vs returning users, premium vs free
- **By Job Type**: 某些行业/职位类型下降更多?
- **By Employer**: 大公司 vs 小公司的 job posting 质量

**Step 4: Hypothesis Generation (假设生成)**:
1. **Product Change**: 近期是否有 UI 改动影响 apply flow?
2. **Supply Side**: Job posting 数量或质量下降? (经济不景气?)
3. **Competition**: 竞品 (Indeed, Glassdoor) 是否推出新功能?
4. **Technical**: 页面加载变慢? Apply button 异常?
5. **External**: 季节性因素 (假期, 毕业季后)?

**Step 5: Validation & Action**:
- A/B test 验证假设
- 如果是 UI 问题: revert 或 fix
- 如果是 supply 问题: 提升 job posting 质量，incentivize employers

---

### Q31."""
    )

    # ── Q31: Frequent Business Travelers ──
    content = content.replace(
        """**题目**: How would you identify frequent business travelers from LinkedIn data? What features would you extract (job title, travel frequency, location changes, geo clusters, international company connections, connections distribution)? How would you handle issues with IP address and VPN accuracy for geo-based features?

**Follow-ups**:
- How would you handle issues with IP address and VPN accuracy for geo-based features?

---

### Q32.""",
        """**题目**: How would you identify frequent business travelers from LinkedIn data? What features would you extract (job title, travel frequency, location changes, geo clusters, international company connections, connections distribution)? How would you handle issues with IP address and VPN accuracy for geo-based features?

**解答**:

**Feature Engineering (特征工程)**:

**1. Profile-based Features (静态特征)**:
- Job title keywords: "consultant", "sales director", "regional manager", "field engineer"
- Industry: consulting, enterprise sales, auditing -- 高出差行业
- Company type: 跨国企业, 多 office 公司
- Skills: "business development", "client management"

**2. Behavioral Features (行为特征)**:
- **Login location changes**: 短时间内从不同城市/国家登录 (IP geolocation)
- **Geo clusters**: 过去 90 天 unique 城市数、国家数
- **Session timezone shifts**: 频繁的时区变化
- **Connection distribution**: connections 分布在多个城市/国家的比例
- **Content engagement**: 与 travel/airport/hotel 相关内容的互动

**3. IP & VPN Handling (VPN 处理)**:
- VPN 检测: 已知 VPN IP 范围、数据中心 IP 标记
- 多信号融合: IP location + device GPS (mobile) + timezone + language settings
- 置信度评分: 当多信号一致时高置信，只有 IP 时低置信
- Fallback: 如果 IP 不可靠，更依赖 profile 和 connection 特征

**Model**:
- Binary classification: frequent_traveler = 1/0
- Ground truth: 可以用 self-reported travel frequency (profile survey) 或 expense report data (enterprise partners)
- Gradient boosted trees (XGBoost/LightGBM) 适合 mixed feature types

**Follow-up**: VPN accuracy -- 最好的策略是 ensemble multiple location signals，不过度依赖任何单一来源。对于 mobile 用户，GPS 数据比 IP 更可靠。

---

### Q32."""
    )

    # ── Q32: LinkedIn Learning Recommendation ──
    content = content.replace(
        """**题目**: Design a recommendation system for LinkedIn Learning. Who are the target users? What features would you use for course recommendations? Additionally, how would you approach ad targeting for travel company advertisements on LinkedIn (e.g., recommending ads for travel services to the right audience)?

---

### Q33.""",
        """**题目**: Design a recommendation system for LinkedIn Learning. Who are the target users? What features would you use for course recommendations? Additionally, how would you approach ad targeting for travel company advertisements on LinkedIn (e.g., recommending ads for travel services to the right audience)?

**解答**:

**Target Users**: (1) 职业转型者 (career changers), (2) 技能提升者 (upskilling), (3) 企业培训学员 (corporate learners), (4) 学生/求职者

**Recommendation Architecture**:

**1. Candidate Generation (候选生成)**:
- **Content-based**: 基于用户 skills gap (profile skills vs desired job skills) 推荐弥补差距的课程
- **Collaborative Filtering (协同过滤)**: "和你相似的人也学了这些课程"
- **Trending**: 行业内热门课程 (trending in your industry)

**2. Features**:
| 类别 | 特征 |
|------|------|
| User | current skills, target role, industry, seniority, learning history |
| Course | topic, difficulty, duration, instructor rating, completion rate |
| Cross | skill-course relevance score, peer enrollment rate |
| Context | time of year (new year resolutions), job market trends |

**3. Ranking Model**:
- Predict P(enroll), P(complete), P(rate_high)
- Score = w1*P(enroll) + w2*P(complete) + w3*P(rate_high)
- 注重 completion 而非仅 enrollment，因为完成课程才有真正价值

**4. Cold Start (冷启动)**:
- 新用户: 基于 profile (title, skills) 推荐入门课程
- 新课程: 基于 content similarity 与热门课程比较

**Ad Targeting (旅行广告)**:
- Audience: 使用 Q31 的 frequent traveler 模型识别目标受众
- Lookalike audience: 找与已知商旅人士行为相似的用户
- Context: 在 travel-related content 旁展示 (contextual targeting)

---

### Q33."""
    )

    # ── Q33: Propensity Model for Premium ──
    content = content.replace(
        """**题目**: Design a propensity model to predict which LinkedIn users are likely to purchase LinkedIn Premium or a generative AI subscription. You are given sample data with columns: Date, MemberID, Converted (0/1), and various feature columns...

---

### Q34.""",
        """**题目**: Design a propensity model to predict which LinkedIn users are likely to purchase LinkedIn Premium or a generative AI subscription. You are given sample data with columns: Date, MemberID, Converted (0/1), and various feature columns...

**解答**:

**1. Problem Framing**:
- Binary classification: Converted = 1 (purchased) / 0 (not purchased)
- Class imbalance: conversion rate 通常 < 5%，需要特殊处理

**2. Feature Engineering**:
- **Engagement**: login frequency, pages viewed, features used, time spent
- **Job-seeking signals**: job searches, applications submitted, profile updates
- **Network**: connection count, InMail usage, group memberships
- **Premium trial**: 是否使用过 free trial, trial 期间的活跃度
- **Temporal**: 注册时长, 最近活跃度变化趋势
- **Device**: mobile vs desktop (mobile 用户更常 convert?)

**3. Class Imbalance Handling (类不平衡处理)**:
- **SMOTE (Synthetic Minority Over-sampling Technique)**: 合成少数类样本
- **Cost-sensitive learning**: 对 positive class 赋予更高权重
- **Threshold tuning**: 调整分类阈值而非使用默认 0.5
- **Evaluation**: 用 AUC-ROC 和 Precision-Recall AUC 而非 accuracy

**4. Model Selection**:
- **Baseline**: Logistic Regression (可解释性强，适合初版)
- **Production**: XGBoost/LightGBM (处理 mixed features 好，支持 feature importance)
- **Feature Selection**: 用 permutation importance 或 SHAP (SHapley Additive exPlanations) values

**5. Deployment**:
- 每日批量预测 all users 的 conversion probability
- 按 propensity score 分桶: high (>0.3), medium (0.1-0.3), low (<0.1)
- High propensity 用户: targeted email campaign, personalized offer
- Medium: show Premium feature highlights in-app
- Evaluation: lift chart, calibration plot, A/B test of targeting strategy

---

### Q34."""
    )

    # ── Q34: Personalized Job Ranking ──
    content = content.replace(
        """**题目**: Design a personalized job ranking model for LinkedIn. How would you rank jobs for an individual user? What features would you use (user personality/preferences, seniority level, search context, keywords, headline, summary, connections at company, skills, endorsements)? Describe the model architecture and training approach.

---

### Q35.""",
        """**题目**: Design a personalized job ranking model for LinkedIn. How would you rank jobs for an individual user? What features would you use (user personality/preferences, seniority level, search context, keywords, headline, summary, connections at company, skills, endorsements)? Describe the model architecture and training approach.

**解答**:

**1. Feature Categories**:

| Category | Features |
|----------|----------|
| **Query** | search keywords, filters (location, salary, remote) |
| **User** | skills, seniority, industry, past applications, saved jobs |
| **Job** | title, description embedding, company, location, salary range, posting date |
| **Cross** | skill-job match score, title similarity, connections at company, company-user industry match |
| **Context** | device, time of day, session position (first search vs refinement) |

**2. Model Architecture -- LTR (Learning to Rank，学习排序)**:
- **Pointwise**: Predict P(apply | user, job) with binary cross-entropy
- **Pairwise**: 给定 (user, job_a, job_b)，预测哪个 job 更 relevant (如 RankNet, LambdaRank)
- **Listwise**: 直接优化 NDCG (如 LambdaMART)

**推荐**: Two-stage approach
- Stage 1: Lightweight model (logistic regression / small NN) 对 ~1000 candidates 粗排
- Stage 2: Heavy model (deep cross network) 对 top ~100 精排

**3. Training Data**:
- **Positive**: applied jobs, saved jobs, long-viewed jobs (>30s on detail page)
- **Negative**: impressed but not clicked, clicked but quickly bounced
- **Label hierarchy**: apply > save > long_view > click > impression (multi-level relevance)

**4. Evaluation**:
- Offline: NDCG@10, MRR, Precision@5
- Online: Application rate, CTR, search-to-apply conversion, user retention
- A/B test: new model vs current model on random user splits

**5. Personalization Key Insight**: "Connections at company" 是 LinkedIn 独有的强 signal -- 用户更倾向于申请有认识人的公司。

---

### Q35."""
    )

    # ── Q35: User Segmentation & Market Sizing ──
    content = content.replace(
        """**题目**: LinkedIn has 500M+ users. Identify the top 5 user segments, estimate each segment's market size, and estimate the opportunity sizing for sales professionals specifically...

---""",
        """**题目**: LinkedIn has 500M+ users. Identify the top 5 user segments, estimate each segment's market size, and estimate the opportunity sizing for sales professionals specifically...

**解答**:

**Top 5 User Segments (用户分层)**:

| Segment | Est. Size | % of Users | Revenue Model |
|---------|-----------|------------|---------------|
| **1. Job Seekers** | ~100M | 20% | Premium Career ($30/mo), job ads |
| **2. Recruiters / HR** | ~25M | 5% | Recruiter Lite/Pro ($100-800/mo), job postings |
| **3. Sales Professionals** | ~50M | 10% | Sales Navigator ($80-135/mo) |
| **4. Content Creators / Influencers** | ~15M | 3% | Premium features, newsletter tools |
| **5. Passive Professionals** | ~310M | 62% | Ad revenue (feed ads, sponsored content) |

**Sales Professional Opportunity Sizing (销售人员机会估算)**:

**TAM (Total Addressable Market，总可寻址市场)**:
- 全球销售从业者 ~50M on LinkedIn
- 潜在 Sales Navigator 用户: ~50M * 有付费意愿比例 (~20%) = 10M
- TAM = 10M * $100/mo * 12 = $12B/year

**SAM (Serviceable Addressable Market，可服务市场)**:
- 英语市场 + 大中型企业: ~3M potential users
- SAM = 3M * $100/mo * 12 = $3.6B/year

**SOM (Serviceable Obtainable Market，可获得市场)**:
- 当前市场份额 ~800K subscribers (公开数据估算)
- SOM = 800K * $100/mo * 12 = ~$960M/year

**Growth Levers**: (1) SMB (Small-Medium Business，中小企业) 市场渗透, (2) 非英语市场扩展, (3) AI-powered features 提升付费转化

---"""
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
    print("System Design Q24-Q35: all 12 questions enriched with full solutions")
    conn.close()


if __name__ == "__main__":
    main()
