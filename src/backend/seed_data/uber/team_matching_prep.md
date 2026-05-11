# Uber Team Matching Prep — Rider ML & UberEats Feed

> 默认顺序最前面。两个 30-min team match call 的诊断剧本 + 决策框架。SWE final round 已结束，team match 是发 offer 前最后一道筛子，反向也是你筛 charter 的最后机会。

---

## TL;DR — 30 分钟用法

每场 call 节奏建议：
- **0-5 min**：让对方讲 team / charter / roadmap，listen，don't interrupt。
- **5-22 min**：按下面 Q1→Q5 的优先级问，不要全问，问到信号收敛即可。
- **22-27 min**：选 1-2 个"两个组都要问"的 bucket。
- **27-30 min**：表达兴趣 + 谈下一步 timeline（关键：把 1 周 push 到 3 周）。

### 决策框架

```
[两组诊断] ─┬─ 都偏 negative?    ──Yes──> 推迟 Uber decision，1w → 3w，等 G/M
            ├─ 只一个加分?       ──Yes──> 加分组当 floor，继续等 G/M；G/M 来后用 Uber 谈 comp
            └─ 都加分?            ──Yes──> 选 manager + roadmap fit 更好的（不纠结 ceiling 差）
```

**红线**：任何一组若 metric 主导是 **revenue squeeze**（你已在 Marketplace Sim 那个组见过同样 pattern）→ 即使其他都好也警惕。同样的 charter problem 会拖你 2 年。

**Senior 这一跳的核心**：ship 一个能讲的 narrative，不是组的 ceiling。Roadmap fit > 组的天花板。

---

## Team 1: Rider ML

### JD 提炼
在 **Rides** app 内做 product **recommendation** / **merchandising**，帮 rider 在 5-10 个 ride product 中找到合适的。
方向 claim：**intent modeling**、**relevance vs discovery**、**contextual targeting**、**joint marketplace optimization** (joint marketplace opt, 联合市场优化)。
Past claim：$B-scale incremental revenue。

### 核心担忧
**Reduced form** 是 **price discrimination** (价格歧视) dressed as personalization。

- Item space 极小（5-10 product）；
- 主导 signal 是 **WTP** (willingness to pay, 支付意愿)；
- 当 user stated preference 与 model rec 冲突时的 **default** 直接决定 charter 是 user-centric 还是 revenue-squeeze。

### 诊断问题（按重要性）

**Q1（最关键）— 过去 12 个月最大的 ship win，metric 是什么？**
- 加分：**incremental booking** / **retention** / **marketplace efficiency**
- 扣分：纯 **revenue lift**
- 后续：如果对方说 "revenue lift"，追问 "怎么 attribution 的？是 net new booking 还是同样 booking 收更多？"

**Q2 — User-choice override 行为**
当 user 主动选了 product A、模型推荐 product B，product 的 default 行为是什么？UI 是否会把 model 选择 over user 选择？
- 加分：user choice 优先，model 只在 user 没选时 surface
- 扣分：UI default 偏离 user choice（这就是 price discrimination 的招牌）

**Q3 — Roadmap 比例**
下个 quarter roadmap 里 **incremental model tuning** vs **新方向**（intent / joint opt）的比例？
- 加分：有真新方向（且能给具体 example）
- 扣分：roadmap 全是 incremental tuning（feature engineering、re-ranking 微调、AB 跑）

**Q4 — JD 方向落地度**
JD 里那些方向（**multi-task learning** / **bandits** / **CF for multi-objective**）目前是 active workstream 还是 aspirational？给一个具体 example。
- 加分：active workstream，能给具体 example（论文 / 上线 / wins）
- 扣分：JD 方向都是 aspirational（"我们在 explore..." 是危险信号）

**Q5 — Senior IC outflow**
团队过去两年 promote 到 **staff** 的 senior IC 比例？manager 带过的 senior 现在都去哪了？
- 加分：staff 流出到更高 level（外部跳槽到更大组也算）
- 扣分：senior 都横向走 / 沉默离职 / 全在原 level 卡住

---

## Team 2: UberEats Feed

### JD 提炼
**HomeFeed** 端到端 recommendation system，覆盖 **model quality** + **serving foundation** + **data foundation**。地理 bounded 的 **hierarchical recall** (分层召回)：先餐馆后品类。

### 核心担忧
- Feed 是不是真正的流量入口（vs **search** / **reorder**）；
- Item space 比 Instagram / YouTube 小一个数量级；
- JD 把 model + serving + data foundation 都列出 → 可能大量 infra glue 而非 algo work；
- Eats 整体 margin 限制资源优先级。

### 诊断问题（按重要性）

**Q1（最关键）— Feed 占 GMV attribution**
Feed surface 占 Eats 总 **GMV** (gross merchandise value, 平台总成交) 的 attribution 是多少？（不是流量比例，是 GMV）
- 加分：Feed GMV attribution 大（>30% 是好信号）
- 扣分：Feed 是次要 surface（"discovery" 但 attribution 不到 10%）

**Q2 — Marginal ROI 排序**
和 search / reorder surface 比，Feed 的 **marginal $ ROI** 排第几？组织资源向哪里倾斜？
- 信号：资源倾斜方向 ≈ 你能做的 work 类型 ≈ 你的 promo narrative

**Q3 — Senior ML eng 时间分配**
一个 senior ML eng 一年的时间分配大概是：**modeling** / **infra** / **data work** 各多少？
- 加分：modeling-heavy（>50% 在 modeling）
- 扣分：大量 infra glue（>40% 在搭管道 / debugging serving）

**Q4 — ML platform 成熟度**
现在的 **ML platform** 成熟度——是有 mature serving / training stack 让你专注 modeling，还是要花大量时间 build glue？
- 加分：platform 成熟（Michelangelo 之类的内部 platform 直接用）
- 扣分：platform 不成熟需要自己搭轮子（注意：Uber 公开宣传 Michelangelo，但 Eats Feed 可能不是 first-class 用户）

**Q5 — 新方向投入**
**Generative recsys** (生成式推荐) / **LLM-based ranking** 这种新方向团队有 active 投入吗？还是在跟 **DoorDash** 的 catch-up cycle？
- 加分：有新方向投入（且不是 PR talk）
- 扣分：roadmap 是追赶 DoorDash（"我们要 close gap" 这种 framing）

**Q6 — 团队结构**
团队规模、senior IC 比例、过去两年 staff promo 数量。

---

## 两个组都要问（任选 1-2 个）

1. **Manager 任期 + senior IC outflow**
   Manager 在 Uber / 这个组多久了？过去带过的 senior IC 现在都去哪了？
   _Why：manager turnover + senior outflow 是 leading indicator of dysfunction。_

2. **首个 6 个月 ownership**
   我入职后第一个 6 个月 own 的 problem 是什么？谁交给我？
   _Why：决定 ramp 速度 + ownership 半径 + 能不能在第一年 ship 出 narrative。_

3. **Velocity / 依赖链**
   Ship 一个 model launch 平均要 align 几个团队？依赖链多长？
   _Why：>3 个团队就是 bureaucracy 警告。_

4. **近期离职情况**
   团队近期离职情况？同 level 的人去了哪里？
   _Why：trailing indicator，但比 manager 自己说的 culture 描述真实。_

---

## 加分/扣分速查表

| 维度 | Rider ML 加分 | Rider ML 扣分 | Eats Feed 加分 | Eats Feed 扣分 |
|---|---|---|---|---|
| **Metric 主导** | booking / retention / marketplace eff | 纯 revenue lift | Feed 占 GMV 大 | Feed 是次要 surface |
| **Roadmap** | 有真新方向 | 全是 incremental tuning | 有新方向投入 | 追赶 DoorDash 的 catch-up |
| **Org health** | staff 流出到更高 level | manager / senior 离职多 | senior IC 比例高、staff promo 多 | flat / 全 mid-level |
| **Charter integrity** | UI default 尊重 user choice | UI default override user choice | modeling-heavy 时间分配 | 大量 infra glue |
| **Platform** | — | — | ML platform 成熟可用 | 需要自己搭轮子 |

---

## Call 后写 debrief 的 5 个字段

每场结束后立刻在自己 notes 里填这 5 项（趁记忆还热）：

1. **Metric 主导**：revenue / booking / retention / marketplace / 其他 — 引用对方原话
2. **Charter integrity 信号**：user choice override 行为（Rider）/ Feed GMV 比例（Eats）
3. **Roadmap incremental vs new ratio**：% 估计
4. **Senior IC outflow**：staff promo 数 + 离职去向
5. **总分**：加分项 - 扣分项 ≈ ?；落到决策框架哪一支

---

## Timeline 谈判脚本

Uber 给你 1 周决定 → 你要 3 周。话术：
- "I'm in late stages with a couple of other companies and I want to make this decision based on full information rather than rushed."
- "Can we move the deadline to [3 weeks out date]? I want to give Uber a fair shake by talking to a couple more people on the team and doing my own research."
- 不要主动说哪几家、不要说 G/M 名字。Uber recruiter 会自己 escalate。

如果 push back：第一档 push 2 周，最低线 10 天。1 周 = "no"。
