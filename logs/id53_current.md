<!-- DEDUPED_20260419 -->
# Google SWE III 面试 — Prep Hub

> 统一入口：本文聚合所有 Round 1 / Round 2 / Coding 必要链接。
> 详细日程与 day-of logistics 见 [Google Interview Prep Note (2026-04-20/21 rescheduled)](db://51) 与 [DNN Key Papers Gist](db://52).

## 日程 (rescheduled)

2026-04-20 周一 mock coding + 2026-04-21 周二 R1 ×2 — 完整 PT 时段表与 day-of logistics 请见 [db://51](db://51)。

---

## Round 1 — ML Basics & Knowledge

### 核心 framework nodes (必过)

- [195 — Bias-Variance & L1/L2 Geometric View](/framework/195/notes)
- [196 — Streaming Top-K: Precise, Probabilistic, Distributed](/framework/196/notes)
- [197 — Scaling & Resource Model (L4 Extension)](/framework/197/notes)
- [198 — Real-Time Recommendation System Design](/framework/198/notes)

### 可能被追问 (likely)

- [193 — A/B Test Sample Size](/framework/193/notes)

### Likely LC 问题 (ML 系统相关)

- [LC 347 Top K Frequent Elements](db://5) — 配合 streaming top-K / bounded vs unbounded 讨论
- [LC 692 Top K Frequent Words](db://393) — 分布式 Top-K / K-way merge
- [LC 224 Basic Calculator](db://273) — 表达式解析 / 栈 vs 递归
- [LC 772 Basic Calculator III](db://254) — 嵌套优先级 / 状态机
- [LC 207 Course Schedule](db://45) — 拓扑排序 / 依赖图
- [LC 210 Course Schedule II](db://113) — 拓扑顺序输出 / damaged node follow-up

---

## Round 2 — G&L (BQ / Googleyness & Leadership)

### 3 polished stories (对应 Google Hiring Attributes)

| Ex-ID | 主题 | Google Attribute |
|-------|------|------------------|
| [EX-02](db://2) | Conflict with Manager → Strategic Team Transfer | **Leadership (emergent)** |
| [EX-08](db://8) | Module Proliferation → VP Escalation | **Leadership (emergent)** |
| [EX-17](db://21) | Harsh Feedback → Mutual Respect | **Googleyness (growth)** |

### 6 predicted G&L 问题 + best-story 映射

| # | 预测问题 | 首选 Story |
|---|----------|-----------|
| 1 | Tell me about a time you disagreed with a decision | EX-02 |
| 2 | A project that failed or went sideways | EX-17 |
| 3 | How do you handle ambiguity / no clear owner | EX-02 |
| 4 | A time you pushed back against your manager | EX-02 |
| 5 | Cross-team conflict / escalation | EX-08 |
| 6 | Hardest feedback you received and what you did | EX-17 |

详细 STAR 2–3 min 版本见 `docs/bq_improved_stories.md` 的 `[google-g&l]` 段落。

---

## Round — Onsite Coding (custom + likely LC)

### 7 custom Google 问题 (core — 必掌握)

| db_id | 问题 | 关键技术 |
|-------|------|---------|
| [1080](db://1080) | Shortest Path A→B (undirected, unweighted) | BFS + 父指针重建路径 |
| [1081](db://1081) | Sum of Good Subarrays (max-min ≤ 1) | **用户曾卡住 — 优先复习**。双指针 + 单调队列 O(N) |
| [1082](db://1082) | Longest Non-decreasing Subarray | O(N) 扫描 + 1-replace follow-up |
| [1083](db://1083) | Jammed Keyboard Dictionary Match | 签名桶 + Trie |
| [1084](db://1084) | Fully Dynamic Connectivity | 线段树 over time + rollback DSU |
| [1085](db://1085) | Basic Calculator IV (LC 770) | 符号表达式展开 + 合并同类项 |
| [1086](db://1086) | Distributed Word Count + KNN/K-means + Kernel Density | MapReduce + 0-shot 估计 |

### Likely LC (Coding round 复用)

- [LC 347](db://5) / [LC 692](db://393) — Top-K 家族
- [LC 224](db://273) / [LC 772](db://254) — 表达式计算家族
- [LC 207](db://45) / [LC 210](db://113) — 拓扑排序家族

---

## Last-Minute 心态 Checklist

- 4/20 Google Champion Mock：当成 dry-run 对齐口述节奏与 scratch 习惯，不要敷衍
- Round 1 被挑战时**先澄清 assumption**，再调整 — 不要立即改答案
- Round 2 STAR 讲**具体对话**，不要讲成 PR 稿；数字不记得给 range + reasoning
- Coding 先**写 signature + 给测例**，再写 brute force，再优化 — 不要跳 brute force
- 每题最后**主动提 follow-up** (scaling / distributed / edge cases) — 彰显 L4 成熟度
- Zoom / Meet 提前 5 分钟加入；双屏：主屏视频 + 副屏 prep hub + 空白 scratch
- Mock 与正式 R1 时间不冲突（mock 4/20、R1 4/21），正常各自全力以赴
