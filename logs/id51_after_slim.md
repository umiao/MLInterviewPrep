<!-- HUB_REORG_20260419_SLIM51 -->
# Google 面试准备 — 2026-04-20 mock + 2026-04-21 R1 (rescheduled)

> R1 改期至周二 (2026-04-21)；周一 (2026-04-20) 多了一场 Google Champion Mock Coding。**正式 R1 优先级高于任何冲突的 mock interview**。

---

## 日程 (Pacific Time)

| 日期 | 时段 | 时长 | 类型 | 准备重点 |
|------|------|------|------|---------|
| **Mon 2026-04-20** | **10:00 – 11:00** | 60 min | **Google Champion Mock Coding** (Google Meet) | 算法 / DS / 现场口述 + 边界 + 复杂度 |
| **Tue 2026-04-21** | **11:15 – 12:00** | 45 min | **R1 #1 — ML Basics & Knowledge** | ML domain / 模型理论 / 数据 + 特征 / ML-product 判断 |
| Tue 2026-04-21 | 12:00 – 13:15 | 75 min buffer | 午餐 / 复盘切换 | 站起来走动，别一直想上一场 |
| **Tue 2026-04-21** | **13:15 – 14:00** | 45 min | **R1 #2 — BQ / Googleyness & Leadership** | STAR stories / 四属性对应 / 真实冲突场景 |

### Day-of Logistics
- Mock (4/20)：Google Meet 链接在 Google Calendar 邀请；提前 5 分钟加入；这是 Google Champion Program 唯一一场 mock，**不要 no-show**。
- 正式 R1 (4/21)：Zoom 链接在 Google Calendar 邀请，**提前 5 分钟加入**
- 双屏：主屏视频，副屏放这份 prep note + `bq_improved_stories.md` + 一张空白 scratch
- 纸笔 + 水 + 耳机备用（Zoom 断了切手机热点）
- 中间 75 min buffer (12:00 – 13:15)：先吃饭，**不看 R1 #1 的复盘**，大脑会挂在上一场。后半段快速过 Round 2 的 story short-list。

---

## Round 1 — ML Basics & Knowledge (4/21 11:15)

>四个考察维度详见 [Recruiter Call Prep](db://38) §ML Domain Interview 考察方向

### 深度问答准备 (high-signal 话题)
- **Ranking losses**: BCE / pairwise hinge / listwise ListNet / LambdaRank — 推导 + 何时用
- **Calibration**: Platt / Isotonic / temperature scaling；GMB bidding 的校准陷阱
- **Eval offline/online 不一致**: counterfactual eval / IPS / 去偏 NDCG（我的 SIGIR paper）
- **LTR → Two-tower retrieval**: 为什么分层、negative sampling 策略
- **A/B test**: 样本量、MDE、SRM、novelty effect (已有 study note: pillar7.probability_statistics.ab_test_sample_size)
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

## Round 2 — BQ / Googleyness & Leadership (4/21 13:15)

>4 Hiring Attributes + 5 Googleyness 子信号详见 [Recruiter Call Prep](db://38) §G&L 考察方向

### Story Short-list (对应 Googleyness)

| Signal | Story | 关键一句话 |
|--------|-------|-----------|
| Ambiguity + Bias for Action | **EX-01 Hacker Week** | "一周内从发现 intent collapse 到 prototype 验证，没人让我做，是 silent failure 让我做的" |
| Challenge status quo + Have backbone | **EX-03 GMB vs Sale NDCG** | "行业标准指标系统性偏好低价商品，我从第一性原理质疑并提出替代" |
| Collaboration + Earn trust | **EX-04 Stakeholder 教育** | "MRR 下降引发警惕，我要解释为什么'变差'的指标恰恰说明系统在变好" |
| **Conflict w/ Manager (polished)** | **EX-02 主动转团队 → [`[google-g&l] STORY A`](./bq_improved_stories.md#google-gl-story-a-conflict-with-manager----strategic-team-transfer-ex-02)** | "经理说超出 scope，我没继续在错误边界硬推，转到 Final Ranking team 重新定义问题" |
| **Conflict across Teams (polished)** | **EX-08 VP escalation → [`[google-g&l] STORY B`](./bq_improved_stories.md#google-gl-story-b-conflict-across-teams----vp-escalation-on-cumulative-degradation-ex-08)** | "模块数量激增导致质量退化时，我推动建立模块仲裁机制，不是回避升级" |
| **Failure + Growth (polished)** | **EX-17 Harsh feedback → [`[google-g&l] STORY C`](./bq_improved_stories.md#google-gl-story-c-failure--growth----harsh-feedback-into-mutual-respect-ex-17)** | "senior IC 说我缺乏基本工程素养，我没辩解，把 researcher 改动的锅也接下来，最终从对立变成最常 review 我 PR 的人" |

> **T-P0-200 polish note (2026-04-14)**: The three rows marked **polished** link to STAR 2-3 min versions in `bq_improved_stories.md` under the `# [google-g&l]` section, each tagged with the Google Hiring Attribute + Googleyness sub-signal they target. Use those versions for Round 2 delivery; the Tier-1 originals (EX-02/08/17) remain canonical for non-Google interviews.

---

## Last-minute 心态

- **不要**在 Round 1 背公式，**要**讲真实的 ranking/eval 经验
- **不要**在 Round 2 把 story 讲成 PR 稿，**要**讲具体的对话和权衡
- Round 1 被挑战时不要立刻改答案——**先澄清 assumption**，再调整
- Round 2 被追问细节时不要编——**承认不记得 exact 数字**，给 range + reasoning
- Mock interview 冲突的话，**正式 Google 面试优先**，mock 可以改期/取消
- 4/20 Google Champion Mock 是难得的 dry-run 机会：用它对齐口述节奏、scratch 习惯、protocol；不要把它当成"练手"敷衍。

祝好运。
