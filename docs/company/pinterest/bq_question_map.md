# Pinterest BQ 问题到故事映射 (2025-11)

> 覆盖 Pinterest behavioral round 收集到的 5 个高频问题，每题给出 2-3 个最契合的 post-rework 故事（见 `docs/bq_behavioral_examples.json`），并用一句话点明该故事的最佳切入角度。优先级 = 列表顺序。

## Q1. 独立主导一个端到端项目（讲一个你从头到尾 own 下来的项目）

| 优先 | Story | 一句话 angle |
|------|-------|-------------|
| 1 | **EX-06** Allocation Framework Platform Primitive | 从 Hacker Week 原型 → 跨团队复用 → 年化 200M+ 影响，完整展示从发现问题到扩成平台能力的端到端所有权。|
| 2 | **EX-23** NYC C2C Policy Launch | 2 周 test + 1 月 launch 的硬 deadline，跨 30+ 人组织，强调独立把控 scope + 节奏 + 结果。|
| 3 | **EX-14** LLM-as-Judge | 从模糊 GenAI mandate 出发，先用 1 周 ROI math 杀掉 agentic search headline path，再独立把 LLM-as-Judge 落到 relevance backlog，scaled 成被广告等多团队复用的 measurement infra。|

## Q2. 需求从何而来（你怎么判断这个问题值得做？）

| 优先 | Story | 一句话 angle |
|------|-------|-------------|
| 1 | **EX-01** Intent Collapse Discovery | 没人派活，自己挖 abandoned-query log 发现 intent collapse，强调从数据里识别 invisible failure 的判断力。|
| 2 | **EX-03** Sale NDCG Proxy First-Principles | 质疑现有 proxy metric、回到用户真实行为定义问题，突出"需求来自对指标局限性的一手观察"。|
| 3 | **EX-09** Conversational Search Proxy Item | 当上游 LLM rewrite 不 work 时，把模糊的"让对话搜索更好"转成具体 proxy-item 方案，展示把技术症状翻译成产品需求的过程。|

## Q3. 在不属于你职责范围的事情上主动出击（stepping ahead）

| 优先 | Story | 一句话 angle |
|------|-------|-------------|
| 1 | **EX-08** Module Proliferation → VP Escalation | production baseline 退化只有我注意到，尽管不在职责内，一路推到 VP 并催生了模块仲裁系统。|
| 2 | **EX-01** Intent Collapse Discovery | Hacker Week 期间自主识别并 prototype 的问题，事后才把它变成正式项目——主动承担典型案例。|
| 3 | **EX-15** Model Deprecation Incident | 本来只是 on-call 删模型，主动把隐式依赖转成显式 contract，额外把下游团队 unblock 完。|

## Q4. 收到负面反馈 / 别人对你不满（difficult feedback received）

| 优先 | Story | 一句话 angle |
|------|-------|-------------|
| 1 | **EX-17** Senior IC Difficult Feedback | Senior IC 直接指出我 PR 流程不规范，讲如何把对抗变成 checklist 制度、最终建立互信。|
| 2 | **EX-13** Authorship Dispute | 同事质疑我的贡献并争夺一作，讲如何基于证据据理力争、并把结果抽象成团队长期规则。|
| 3 | **EX-02** Manager Resistance to Diversity Ranking | 经理认为方向不在 charter 内、不给实验 slot，讲如何消化这个反馈 → 换组 → 最终用 +1% GMB 证明判断。|

## Q5. 与错过 deadline 的同事合作（teammate missing deadlines）

| 优先 | Story | 一句话 angle |
|------|-------|-------------|
| 1 | **EX-11** Intern Overpromise / Goal Visibility | 实习生被同事投诉"只在自学 deadline 全拖"，我介入发现是沟通问题，帮他重构 update 节奏，最终拿到 return offer。|
| 2 | **EX-22** Hashing Delegation | 同事坚持换方案导致当前 block，我把决定权 delegate 出去、用 timebox 控风险，反而挖出一个 latent bug。|
| 3 | **EX-15** Model Deprecation Incident | 下游团队没按时响应依赖迁移计划、deadline 被动滑落，讲我如何 on-call 2 天内把每个 broken consumer 拉回来。|

---

## 使用说明

- 每题可根据面试官关注点在 2-3 个 story 中选最贴切的一个深讲；另外 1-2 个作为 follow-up 备份。
- 所有 EX-XX 引用均指向 `docs/bq_behavioral_examples.json` 中的 post-rework 版本（metric 已具象化、Action 已 "I" 化）。
- 跨题复用时优先避免用同一个 story 回答两个问题；若必须复用（如 EX-01），提前设计好不同角度的切入。
