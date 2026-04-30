# INVARIANT-3-EXEMPT: behavioral prep doc; ISO-8601 (2026-05-01 onsite date) co-occurs with name-shape tokens (e.g., 'Senior IC', 'researcher') in narrative prose, not schedule data. Target row IS company_documents.content (a prep_note), not interview_events.
"""Seed Meta AI-Native Behavioral 5-Pack prep doc (T-P0-669).

Companion to seed_meta_ai_native_prep.py (golden landing),
seed_meta_ainative_codepad_prompt.py (code-pad playbook), and
seed_meta_ainative_breadth_5pts.py (domain-breadth talking points).
This doc tightens 5 behavioral stories specifically angled for the
'AI-native impactful engineer' framing of the Meta onsite (2026-05-01).

Source: docs/bq_behavioral_examples.json (read-only). Five stories:
  EX-14  GenAI ROI Math (LLM-as-Judge over agentic search)
  BLOG-03 Cross-Org Boundary Defense via LLM Relevance Pipeline
  EX-01  Search Diversity Intent-Collapse (Hacker Week)
  EX-05  XGBoost Deployment Latency + Silent CI Failure
  EX-17  Difficult Feedback from Senior IC -- Trust vs Reliance

Each story: 30-45 sec Chinese spoken pitch + English kill-line +
'AI-native angle' callout (why this story specifically demonstrates
AI-native impact, not generic SWE) + match-question hints (BQ themes).

Idempotency: sentinel <!-- META_AINATIVE_BEHAVIORAL_5PACK_20260430 -->.
Style: Chinese narration + English technical term expansion on first
use, per content_style memory. No emoji (project invariant).
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_AINATIVE_BEHAVIORAL_5PACK_20260430 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta] AI-Native Behavioral 5-Pack"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r'''
# Meta AI-Native Behavioral 5-Pack

> 配套 [Meta] AI-Native Onsite Prep golden 文档 + Code-Pad
> Prompt + Domain Breadth 5 Talking Points. 本篇专门解决一件事:
> **当 interviewer 在 behavioral round 里问到经典 BQ 题, 比如 "tell me
> about a time you used AI for impact" / "tell me about a hard bug" /
> "tell me about difficult feedback"**, 你不要 generic 回答, 直接从下面
> 5 个 story 里挑 1 个最贴当前 question 的, 30-45 秒讲完 (S-T-A-R 压缩),
> 留 kill-line 让 interviewer 记住, 留 file path / artifact 给他追问.
>
> Source: `docs/bq_behavioral_examples.json` (read-only) 的 EX-14, BLOG-03,
> EX-01, EX-05, EX-17. 这 5 条特意挑出来 -- 每条都能写成 generic SWE story,
> 但每条又有一个 **AI-native angle** 是 Meta AI-native role 真正在 hire 的:
> feasibility-first 砍 bad AI 想法, 把 conflict 转成 AI tooling product,
> 在 ambiguous 问题上 framing diagnose, 在 LLM-in-harness 时代 own deployment
> reality, 不把判断 outsource 给 LLM.

每个 story 模板:
- **30-45 sec spoken pitch (中文 narration + 英文术语)** -- 嘴上讲的版本
- **English kill-line** -- 一句话让 interviewer 记住 framing
- **AI-native angle (1-2 句)** -- 为什么这条专门 demo Meta AI-native role,
  而不是 generic SWE
- **Match-question hints** -- 这条 cover 哪些 Meta BQ theme

---

## §1 Story 1 -- EX-14 GenAI ROI Math (Killing Agentic Search with One Week)

### 30-45 sec spoken pitch

> "2023 年公司 leadership 说 'upgrade to GenAI' -- 给我一个 sandbox, API
> credits, 没有 requirements, 没有 LLM precedent in 我们 production stack.
> 大家默认要做 agentic search demo. 我第一周不写 prototype, 写 ROI math
> feasibility study: LLM 接不到 indexing pipeline, 读不到 live inventory,
> throughput 在 40K-peak surface 上只能跑到 tens of QPS, latency
> prohibitive. 数字直接 disqualify 那条 path -- 在 sunk cost 还没让 kill
> 政治成本变高之前. 省下来的 budget 我转去做 LLM-as-Judge for relevance
> labeling -- 严重 mislabel + human annotator 之间 inter-rater agreement
> 低的 backlog. Build 阶段还撞过三个独立 issue: low inter-rater agreement
> 让 AI-vs-human alignment 这个 metric 失效, 早期 instruction-following
> 不成熟 (JSON failures, NSFW blocks), 还有一个我 trace 到 dataset quality
> 不是 model quality 的 no-lift offline comparison. 最后这套 LLM-as-Judge
> 跨多个 relevance metric 全 win, 从我一个人 explore scale 到 production
> measurement infrastructure for relevance team, then ads, then several
> other groups."

### English kill-line

> "The cheapest move in a vague AI mandate is the one nobody assigns --
> disqualify the obvious path with a week of ROI math before sunk cost
> makes the kill politically expensive. Feasibility is the real authoring;
> pitch decks are downstream of it."

### AI-native angle (why this story for Meta AI-native specifically)

Meta AI-native role 真正怕的不是 'this engineer can't build with LLMs',
而是 'this engineer will burn 8 weeks on an agentic demo before doing the
math'. EX-14 直接 demo 反向能力: **feasibility-first discipline + 用 ROI
math 去 kill bad AI ideas before prototype**. 这是 Meta AI org 在
2026 年最稀缺的 signal -- agentic hype 退潮, 留下来的是会算 QPS / latency
/ integration cost 的 ML engineer.

### Match-question hints (Meta BQ theme cover)

- "Tell me about a time you used AI for business impact" -- $500/day 18K
  labels, 1.5% GMB lift via LLM-as-Judge
- "How do you decide what to build with LLMs?" -- ROI math first, novelty
  last
- "Tell me about a time you went against the grain" -- killed the
  agentic-search headline path leadership half-imagined
- "Cost discipline / scoping ambiguous mandate" -- $0.30-0.80/label human
  vs $500/day for 18K labels via LLM
- Meta principle: **move fast** (1 week feasibility kill) + **build
  awesome things** (infrastructure-over-demo)

---

## §2 Story 2 -- BLOG-03 Cross-Org Boundary Defense via LLM Pipeline

### 30-45 sec spoken pitch

> "Q2-Q3 那段时间 ads team 来要 access -- 想 tune 我们 relevance filter 的
> pass-through rate. Org boundary 是 ads 优化 revenue, relevance 优化
> absolute quality threshold; 让他们直接调 threshold 等于让 ads 政策替
> relevance 决策. 我没硬拒绝 -- 拒绝就是 zero-sum. 我 reframe 这个
> conflict: ads 真正缺的不是 policy access, 是 **interpretable relevance
> signal** 让他们自己做 trade-off. 我用 Q2-Q3 时间 build 了一条 LLM
> judgment pipeline -- 每天产 18K labels at $500 total, 对比 vendor 的
> human annotation **$0.30-0.80 per label** 是 1/10 到 1/30. 关键 design
> decision: pipeline 是 ads team 的 input signal, 不是 relevance team 的
> policy override -- 两 team 各拿 own 的: relevance 守住 quality
> threshold, ads 拿到 interpretable signal. 这条 pipeline 后来 scale 成
> all search result sets 的 standard relevance signal, 贡献 1.5% GMB lift."

### English kill-line

> "I held the org boundary by turning the conflict into a product. Ads
> didn't actually need access to our policy -- they needed an
> interpretable signal. I built it as LLM-as-Judge. Both sides got what
> they needed."

### AI-native angle

Meta AI-native role 经常被人想成 'add LLM to existing feature'. BLOG-03
demo 高一阶能力: **把 cross-org political conflict 转化成 AI tooling
product**. LLM 不是 feature, 是 ops lever -- 用 LLM 当 measurement
infrastructure 让两 team 各自 OKR 都能 advance. 这是 Meta AI org 在做
GenAI productization 时最重要的 transferable skill: 不是技术问题, 是
"用 LLM 把不可调和的 trade-off 变成可观测的 signal" 这种 product framing.

### Match-question hints

- COL-3: "Tell me about cross-functional collaboration" -- direct
  answer, ads + relevance org boundary
- COL-9: "Competing priorities" -- ads tunable pass-through vs relevance
  absolute threshold
- COM-2: "Persuaded stakeholders" -- ads accepted interpretable LLM
  signals over policy access
- INN-9: "Creative solution" -- turned boundary conflict into a product
- IMP-4: "Long-term impact" -- pipeline became standard signal, 1.5% GMB
- Meta principle: **focus on impact** + **build awesome things**

---

## §3 Story 3 -- EX-01 Search Diversity Intent Collapse (Hacker Week)

### 30-45 sec spoken pitch

> "Hacker Week 我自己挑了一个题 -- search ranker 在 silently fail 在
> multi-intent queries 上, e.g. 'pokemon' 搜索结果 90%+ trading cards,
> 但购买数据显示一半买家想要 games / toys / figures. Standard dashboard
> 显示 ranker 健康 -- 因为 dominant-intent users 是健康的, 看不见的那一半
> users 就 invisible. 我先 abandon-log slice -- 按 post-impression
> drop-off 排序 query, 几百个 high-volume multi-intent queries 都同一种
> collapse 模式. 不是单 query bug, 是 systematic bias. Root-cause call:
> ranker 是 per-item scoring, 没 page-level reasoning -- top candidates
> 都同一类, page 自然 homogeneous. 这是 structural gap, 不是 calibration
> miss. Prototype: 在现有 ranker 上叠 diversity-blending layer, 用便宜的
> intent-coverage proxy. 一周内 abandon-log pipeline + blending algorithm
> + experiment framework 都跑通了. 后来 compounded across verticals,
> 200M+ annualized impact, methodology 写成 SIGIR paper."

### English kill-line

> "Item-level scoring creates page-level homogeneity. The dashboard was
> healthy because the dominant-intent users were healthy -- the missing
> half was invisible. Before trusting any 'healthy' search metric I now
> ask which users it's measuring and which ones it cannot see."

### AI-native angle

Meta AI-native role 表面上是 LLM application, 底层 still是 ML system
diagnosis under ambiguity. EX-01 demo 的不是 GenAI, 是 **AI engineer 在
ambiguous problem 上的 framing + diagnosis muscle**: 用 abandon-log slice
找 invisible failure, 用 item-vs-page 这一句话定结构层级, 一周内 ship
end-to-end. 在 LLM 时代这套能力 transfer 到诊断 RAG / agent 失败 -- 同样是
"per-step looks fine, system-level outcome is bad" 的 page-level vs
item-level pattern.

### Match-question hints

- INN-2: "Self-initiated direction" -- self-framed Hacker Week scope
- PS-15: "Used data to identify problem others missed" -- abandon-log
  slice vs purchase-distribution slice
- INN-8: "Challenged the default" -- standard metrics looked healthy,
  argued they measured only retained users
- OWN-9: "Moved fast with incomplete information" -- one Hacker Week,
  no funded scope
- EXE-5: "Deadline-tight end-to-end delivery"
- Meta principle: **be bold** + **focus on impact**

---

## §4 Story 4 -- EX-05 XGBoost Deployment + Silent CI Failure

### 30-45 sec spoken pitch

> "我作为 sole MLE on relevance filtering project, 团队两个月 build 了一个
> 几千棵 tree 的 XGBoost model, 准 accuracy 高. 但 deployment 时发现
> +10% latency overhead, 而 budget 是 <=1% -- 完全过不去. 我没去 shrink
> big model -- reframe 是 **80%+ candidate items 是 obviously irrelevant,
> 它们根本不需要大模型**. 我 try 了三条路 (early exit / feature-pruned /
> cheap rejection), 两条死了, cheap rejection + early exit 把 computation
> 砍 order of magnitude 过了 latency budget. 然后撞到一个 insidious wall
> -- silent CI failure: tests pass 但 production 结果错. Trace 到
> downstream system 在 URL > 16K chars 时 truncate JSON field, 上游
> 不报错下游悄悄取 stale value. Fix 后 GMB on null/low-intent queries
> +4-6%. Cheap rejection + early exit pattern 后来被 reuse 在另两个
> deployment, silent failure 教训直接产出 team standard: end-to-end
> payload stress test before every launch."

### English kill-line

> "The reframe wasn't 'how do we shrink the big model' -- it was 'most
> requests don't deserve the big model at all'. The real constraint
> wasn't model performance vs complexity -- it was the coupling between
> the model and every system it touches. Green CI does not mean correct
> production."

### AI-native angle

Meta AI-native role 在 2026 年最现实的 trap 是 **'LLM-in-harness 跑通
demo 但 production 结果错'** -- 同 EX-05 silent CI failure 同一个 class
of bug, 只是从 XGBoost JSON truncation 换成 LLM tool-call shape mismatch
or context truncation. EX-05 demo 的是 **owning deployment reality, not
just modeling reality**. 这正是 Meta 把 'green CI broken prod' 列为
AI-native role 真正风险的原因 -- 我已经踩过这个 class 的坑, 已经把它
turn into team standard.

### Match-question hints

- ADP-15: "Biggest lesson" -- define deployment envelope before model
  design
- EXE-3: "Solved complex multi-layer problem" -- model latency +
  system-coupling silent failure
- INN-15: "Created best practice" -- payload stress test as team
  standard
- OWN-8: "Sole MLE under deadline pressure" -- both model and
  system-level blockers
- Meta principle: **focus on long-term impact** (durable team standard,
  not just one-launch fix) + **be direct, respect each other** (calling
  out a silent CI gap to leadership)

---

## §5 Story 5 -- EX-17 Difficult Feedback from Senior IC (Trust vs Reliance)

### 30-45 sec spoken pitch

> "Manager 让我支援一个 researcher 的 urgent model engine change.
> Researcher 有 project context 但很少 merge code. 我 follow 她的 suggestion,
> 直接从她 branch 上 raise PR -- unconventional 但 technically possible.
> 我跑完所有 test 之后, researcher 又改了一些 naming, 把 build 弄断了, 让
> 我那条 'verified' PR 立刻 invalid. Senior IC 看到之后给了我 harsh
> feedback -- 说我 lack basic engineering quality, 拒绝 review 我 PR.
> 第一反应是 demoralized. 跟 manager 聊完, 我意识到一个 lesson: 有时候你
> 必须 accountable for things 不是你做的也不在你 familiarity 范围内. 我
> develop 了一套更好的 engineer-researcher collaboration practice (跟
> existing org policy 'PR should be engineer-owned' 对齐), proactively
> reach out 那位 senior IC 解释 full context + 分享 improvement plan. 后来
> 我们 build 了 mutual respect, 成了 professional friends, 两个都在 org 内
> 以 rigorous checklist + fast response + conscientious on-call 出名.
> Kill-line: **'I conflated being relied on with being trusted.'**
> 'Reliable' 是 deliver task, 'trusted' 是 own outcome 不管 task 是不是
> 你自己做的."

### English kill-line

> "I conflated being relied on with being trusted. Reliable means I
> deliver the task. Trusted means I own the outcome even when I didn't
> do the work. The senior IC didn't doubt my code -- he doubted whether
> I would defend the artifact past my own boundary."

### AI-native angle

LLM-coding 时代这条 story 重要在 -- **AI 让你随手能 produce 看起来
verified 的 PR, 但 senior IC 真正担心的是 'this engineer will accept
LLM output as ground truth and lose the trust gate'**. EX-17 直接 demo
反向能力: 我不把 judgment outsource 给 LLM, 也不把 ownership outsource
给 PR-author 是不是我自己. 在 AI-assisted 时代 'I conflated being relied
on with being trusted' 这条 distinction 比 ever 都重要 -- LLM 让 'reliable'
变得 cheap, 'trusted' 变得稀缺. Meta AI-native role 在 hire 后者.

### Match-question hints

- ADP-19: "Most challenging feedback received" -- direct match
- COM-5: "Received harsh feedback" -- proactive outreach + improvement
  plan
- ADP-16: "Turned negative relationship into professional friendship"
- OWN-3: "Difficult feedback handled constructively"
- ADP-17: "Adjusted approach to credibility-building"
- Meta principle: **be direct, respect each other** + **earn trust** --
  EX-17 是 trust 的反面教材 + recovery, 比纯 success story 更 real

---

## §6 离场前 60 秒 cheat sheet (5 个 BQ trigger -> story map)

| Interviewer signal                                         | Drop this story          |
|------------------------------------------------------------|--------------------------|
| "Time you used AI for business impact / cost discipline"   | §1 EX-14 (ROI math)      |
| "Cross-functional collaboration / boundary / influence"    | §2 BLOG-03 (LLM pipeline)|
| "Hard bug / ambiguous problem / framing under no scope"    | §3 EX-01 (intent collapse)|
| "Time things broke in production / silent failure / latency"| §4 EX-05 (XGBoost + CI) |
| "Difficult feedback / failure / credibility recovery"      | §5 EX-17 (trust vs reliance)|

**Common trap**: 听到一个 BQ keyword 立刻挑 1 条最近想到的 story 讲. **Don't**.
先 echo back interviewer 的 signal (1 句), 然后 announce 你要讲哪个 (1 句:
"Let me tell you about a project from 2023 where ..."), 再进入 30-45 秒
S-T-A-R. 最后留 kill-line + 一个 file path / artifact ("if you want the
numbers I can walk you through `docs/bq_behavioral_examples.json` EX-14
during follow-up").

**Prep ritual (面试前 5 分钟)**: 把这 5 条用嘴 narrate 一遍 -- 不是看 doc,
是 actually speak. 时间不够就跳到 kill-line + AI-native angle 那 2 行.
卡壳的那条说明今天 framing 还没 land, 改去看那条 source EX-XX 在 JSON
里的 action 段.

---

> **核心 mental model**: AI-native behavioral 不是 "I have used AI", 而是
> "**I make AI-native judgments under ambiguity**". 上面 5 条每条都给一个
> 具体 judgment moment: feasibility-first kill (§1), conflict-as-product
> (§2), framing under no scope (§3), deployment reality ownership (§4),
> trust vs reliance distinction (§5). 这是 Meta AI-native role 真正在
> hire 的 signal -- 不是 LLM API 熟练度, 是 judgment muscle.
'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## §1 Story 1 -- EX-14 GenAI ROI Math",
        "## §2 Story 2 -- BLOG-03 Cross-Org Boundary Defense",
        "## §3 Story 3 -- EX-01 Search Diversity Intent Collapse",
        "## §4 Story 4 -- EX-05 XGBoost Deployment",
        "## §5 Story 5 -- EX-17 Difficult Feedback from Senior IC",
        "## §6 离场前 60 秒 cheat sheet",
        "### 30-45 sec spoken pitch",
        "### English kill-line",
        "### AI-native angle",
        "### Match-question hints",
        "EX-14",
        "BLOG-03",
        "EX-01",
        "EX-05",
        "EX-17",
        "$500",
        "18K labels",
        "1.5% GMB",
        "200M+",
        "I conflated being relied on with being trusted",
        "feasibility-first",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    emoji_ranges = (
        (0x1F300, 0x1F6FF),
        (0x1F900, 0x1F9FF),
        (0x2600, 0x27BF),
        (0x1F000, 0x1F2FF),
    )
    for ch in content:
        cp = ord(ch)
        for lo, hi in emoji_ranges:
            if lo <= cp <= hi:
                raise RuntimeError(
                    f"emoji char detected at codepoint U+{cp:04X}: {ch!r}"
                )
    if not (8000 <= len(content) <= 20000):
        raise RuntimeError(f"content length {len(content)} outside 8000-20000")


def main() -> int:
    """Upsert the Meta AI-Native Behavioral 5-Pack doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        cur = conn.execute(
            "SELECT id, content FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        )
        existing = cur.fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(CONTENT)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "content_hash, is_golden, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    new_hash,
                    0,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} len={len(CONTENT)} "
                f"hash={new_hash[:12]}..."
            )
        else:
            existing_id, existing_content = existing
            if SENTINEL in existing_content and existing_content == CONTENT:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel + content "
                    f"match; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, updated_at = ? "
                    "WHERE id = ?",
                    (CONTENT, new_hash, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(CONTENT)} delta={len(CONTENT)-old_len:+d}"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
