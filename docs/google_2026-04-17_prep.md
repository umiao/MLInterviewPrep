---
target_table: company_documents
company_id: 3
doc_kind: prep_note
title: 'Google 2026-04-17 Interview Prep Note'
target_id: 51
---
# Google 面试准备 — 2026-04-17 (周五)

> 第一轮 On-site Virtual 两场连背。**优先级高于任何冲突的 mock interview**。

---

## 日程 (Pacific Time)

| 时段 | 时长 | 类型 | 准备重点 |
|------|------|------|---------|
| **13:00 – 13:45** | 45 min | **Interview #1 — ML Basics & Knowledge** | ML domain / 模型理论 / 数据 + 特征 / ML-product 判断 |
| 13:45 – 14:15 | 30 min buffer | 休息 / 喝水 / 快速复盘 | 站起来走动，别一直想上一场 |
| **14:15 – 15:00** | 45 min | **Interview #2 — BQ / Googleyness & Leadership** | STAR stories / 四属性对应 / 真实冲突场景 |

### Day-of Logistics
- Zoom 链接在 Google Calendar 邀请里，**提前 5 分钟加入**
- 双屏：主屏视频，副屏放这份 prep note + `bq_improved_stories.md` + 一张空白 scratch
- 纸笔 + 水 + 耳机备用（Zoom 断了切手机热点）
- 中间 30 min：**不看 1st 的复盘**，大脑会挂在上一场。就快速过 Round 2 的 story short-list。

---

## Round 1 — ML Basics & Knowledge (13:00)

### 面试官期待的维度 (来自 recruiter call)

1. **ML Paradigm 与迭代经验**
   - 我的主线：Pointwise → Pairwise → Listwise 的真实迁移决策
   - 何时换 paradigm / 为什么换 / 数据或业务信号是什么
   - **可讲案例**: Etsy Search diversity project (intent collapse → GMB 排序 → allocation primitive 平台化)

2. **数据分析与处理**
   - 数据质量、Sale NDCG 的偏差、GMB 作为正确代理目标
   - 采样、特征 leakage、train-serve skew

3. **ML + 产品判断**
   - Diversity vs MRR 指标悖论的 stakeholder 沟通
   - 什么时候 ship / 什么时候 hold / 模块仲裁机制

4. **深度问答准备 (high-signal 话题)**
   - **Ranking losses**: BCE / pairwise hinge / listwise ListNet / LambdaRank — 推导 + 何时用
   - **Calibration**: Platt / Isotonic / temperature scaling；GMB bidding 的校准陷阱
   - **Eval offline/online 不一致**: counterfactual eval / IPS / 去偏 NDCG（我的 SIGIR paper）
   - **LTR → Two-tower retrieval**: 为什么分层、negative sampling 策略
   - **A/B test**: 样本量、MDE、SRM、novelty effect、CUPED、Etsy GMB trap (drill: `docs/google_ab_test_rigor_drill.md`; 基础 note: pillar7.probability_statistics.ab_test_sample_size)
   - **Feature drift / 监控**: PSI、KL、Jensen-Shannon、分阶段 alert

### 快速复习 pointer
- `docs/doordash_ml_domain_ranking.md` — 排序损失 + eval
- `docs/doordash_ml_domain_features_dl.md` — 特征工程 + DL 基础
- `docs/doordash_ml_domain_fundamentals.md` — bias/variance, regularization
- `docs/doordash_ml_domain_case_study.md` — 完整 ML case 结构
- `/framework/pillar7` — 概率统计（A/B 样本量 note 已就绪）

### 开场 / 自我介绍 (90 秒版)
"我是 Shenghui，目前 Pinterest staff SWE，之前在 Etsy 主导 search ranking。两条主线：一是 search diversity，发现 intent collapse 问题，重新定义评估指标为 GMB 而非 Sale NDCG，最终平台化成可复用的 allocation primitive，跨垂直达成 200M+ 年化 GMB。二是线上实验严谨性，设计去偏 NDCG 框架发表于 SIGIR。我最擅长把模糊的业务信号翻译成具体的 ranking/eval 问题。"

---

## Round 2 — BQ / Googleyness & Leadership (14:15)

### Google 的 Hiring Attributes (4 条 — 重点第 4 条)

| Attribute | 考察重点 | 我的对应 stories |
|-----------|---------|----------------|
| **1. General Cognitive Ability (GCA)** | 结构化解决模糊问题的能力 | Hacker Week intent collapse (EX-01) |
| **2. Leadership (emergent)** | 没有 title 也能推动决策 / 跨团队影响 | 主动转团队 (EX-02)、VP 层面 escalation (EX-08) |
| **3. Role-Related Knowledge** | ML depth + 系统判断 | GMB 指标重定义 (EX-03)、SIGIR paper (EX-10) |
| **4. Googleyness** | Ambiguity / Bias for Action / Collaboration / Growth / User-first | 下方 Story Map |

### Googleyness 的 5 个子信号 (Google 官方 rubric)

1. **Thrives in ambiguity** — 没人告诉你做什么时你在做什么？
2. **Values feedback** — 被质疑/被否时如何反应
3. **Challenges status quo** — 质疑既有标准（Sale NDCG → GMB 就是典型）
4. **Does the right thing** — 用户/数据优先 vs 指标 gaming
5. **Collaboration** — 跨 team / 跨 function

### Story Short-list (对应 Googleyness)

| Signal | Story | 关键一句话 |
|--------|-------|-----------|
| Ambiguity + Bias for Action | **EX-01 Hacker Week** | "一周内从发现 intent collapse 到 prototype 验证，没人让我做，是 silent failure 让我做的" |
| Challenge status quo + Have backbone | **EX-03 GMB vs Sale NDCG** | "行业标准指标系统性偏好低价商品，我从第一性原理质疑并提出替代" |
| Collaboration + Earn trust | **EX-04 Stakeholder 教育** | "MRR 下降引发警惕，我要解释为什么'变差'的指标恰恰说明系统在变好" |
| **Conflict w/ Manager (polished)** | **EX-02 主动转团队 → [`[google-g&l] STORY A`](./bq_improved_stories.md#google-gl-story-a-conflict-with-manager----strategic-team-transfer-ex-02)** | "经理说超出 scope，我没继续在错误边界硬推，转到 Final Ranking team 重新定义问题" |
| **Conflict across Teams (polished)** | **EX-08 VP escalation → [`[google-g&l] STORY B`](./bq_improved_stories.md#google-gl-story-b-conflict-across-teams----vp-escalation-on-cumulative-degradation-ex-08)** | "模块数量激增导致质量退化时，我推动建立模块仲裁机制，不是回避升级" |
| **Failure + Growth (polished)** | **EX-17 Harsh feedback → [`[google-g&l] STORY C`](./bq_improved_stories.md#google-gl-story-c-failure--growth----harsh-feedback-into-mutual-respect-ex-17)** | "senior IC 说我缺乏基本工程素养，我没辩解，把 researcher 改动的锅也接下，最终从对立变成最常 review 我 PR 的人" |

> **T-P0-200 polish note (2026-04-14)**: The three rows marked **polished** link to STAR 2-3 min versions in `bq_improved_stories.md` under the `# [google-g&l]` section, each tagged with the Google Hiring Attribute + Googleyness sub-signal they target. Use those versions for Round 2 delivery; the Tier-1 originals (EX-02/08/17) remain canonical for non-Google interviews.

### STAR 结构提醒 (2-3 min per story)
- **S** 30s: 情境 + 为什么重要
- **T** 15s: 我的角色 / 目标
- **A** 90s: **具体**动作（决策、权衡、与谁沟通、怎么说服）
- **R** 30s: 量化结果 + 一行 learning

### 典型 G&L 问题预测
- Tell me about a time you disagreed with a decision → **EX-02 / EX-03**
- A project that failed or went sideways → 选一个带 growth 的
- Working with a difficult stakeholder → **EX-04**
- How do you handle ambiguity → **EX-01**
- Time you pushed back against your manager → **EX-02**
- Hardest technical decision → **EX-03 (GMB)** 或 **EX-06 (平台化决策)**

### 复习 pointer
- `docs/bq_improved_stories.md` — 完整故事文本
- `docs/bq_story_arcs.json` — 六条 arc 的结构化索引
- `docs/bq_clustered_questions.json` — 问题主题聚类

---

## Last-minute 心态

- **不要**在 Round 1 背公式，**要**讲真实的 ranking/eval 经验
- **不要**在 Round 2 把 story 讲成 PR 稿，**要**讲具体的对话和权衡
- Round 1 被挑战时不要立刻改答案——**先澄清 assumption**，再调整
- Round 2 被追问细节时不要编——**承认不记得 exact 数字**，给 range + reasoning
- Mock interview 冲突的话，**正式 Google 面试优先**，mock 可以改期/取消

祝好运。
