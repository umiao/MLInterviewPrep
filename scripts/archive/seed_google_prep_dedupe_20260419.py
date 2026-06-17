"""Dedupe Google prep docs id=51 + id=53 schedule overlap, refresh dates.

Per T-P1-530 [T-GOOG-DEDUPE]. Google R1 was rescheduled from
2026-04-17 (Fri) to 2026-04-21 (Tue), and a Google Champion mock coding
slot was added 2026-04-20 (Mon) 10:00-11:00 PT.

Authoritative schedule (data/mle_prep.db.interview_events rows 28/29/30):
  - Mon 2026-04-20 10:00 PT, 60 min  -- Google Champion Mock Coding (Meet)
  - Tue 2026-04-21 11:15 PT, 45 min  -- R1 #1 ML Basics & Knowledge
  - Tue 2026-04-21 13:15 PT, 45 min  -- R1 #2 BQ / Googleyness & Leadership

Scope (narrow, reversible):
  - id=38 NOT touched (recruiter-call prep stays as-is)
  - id=51 schedule table refreshed; rest of doc preserved verbatim
  - id=53 schedule table stripped (rely on db://51 link); header + intro
    refreshed; Round 1 / Round 2 / Coding link sections preserved
  - No doc deleted, no doc_kind change

Idempotent: each doc has a sentinel `<!-- DEDUPED_20260419 -->` near the top.
If the sentinel is present in the stored content, the doc is left untouched.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- DEDUPED_20260419 -->"


# -------------------------------------------------------------------------
# Doc 51 -- Google Interview Prep Note (schedule + day-of logistics)
# -------------------------------------------------------------------------
DOC_51 = SENTINEL + """
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
- 4/20 Google Champion Mock 是难得的 dry-run 机会：用它对齐口述节奏、scratch 习惯、protocol；不要把它当成"练手"敷衍

祝好运。
"""


# -------------------------------------------------------------------------
# Doc 53 -- Google Prep Hub (links aggregator; schedule deduped to db://51)
# -------------------------------------------------------------------------
DOC_53 = SENTINEL + """
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
"""


DOCS = {
    51: ("Google 2026-04-17 Interview Prep Note", DOC_51),
    53: ("Google 2026-04-17 Prep Hub", DOC_53),
}


def main() -> int:
    """Apply schedule dedupe + date refresh to id=51 + id=53 idempotently."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        updated = 0
        unchanged = 0
        for did, (expected_title, new_content) in DOCS.items():
            row = conn.execute(
                "SELECT title, content FROM company_documents WHERE id = ?",
                (did,),
            ).fetchone()
            if row is None:
                print(f"[ERROR] doc {did} not found")
                continue
            cur_title, cur_content = row
            if SENTINEL in cur_content:
                print(f"[UNCHANGED] doc {did} ({cur_title}) -- sentinel present")
                unchanged += 1
                continue
            if cur_title != expected_title:
                print(
                    f"[WARN] doc {did} title mismatch: stored={cur_title!r} "
                    f"expected={expected_title!r} -- title NOT changed"
                )
            new_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()
            now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.execute(
                "UPDATE company_documents "
                "SET content = ?, content_hash = ?, updated_at = ? "
                "WHERE id = ?",
                (new_content, new_hash, now, did),
            )
            conn.commit()
            old_len = len(cur_content)
            new_len = len(new_content)
            print(
                f"[UPDATE] doc {did} rows={cur.rowcount} "
                f"old_len={old_len} new_len={new_len} delta={new_len - old_len:+d}"
            )
            updated += 1
        # id=38 sanity guard -- never touched, just print current hash
        row38 = conn.execute(
            "SELECT title, length(content), content_hash FROM company_documents WHERE id = 38"
        ).fetchone()
        if row38:
            print(
                f"[GUARD] doc 38 untouched: title={row38[0]!r} len={row38[1]} "
                f"hash={row38[2][:12]}..."
            )
        print(f"Summary: updated={updated}, unchanged={unchanged}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
