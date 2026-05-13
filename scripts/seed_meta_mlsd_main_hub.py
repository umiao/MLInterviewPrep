"""Seed Meta MLSD main hub page (T-P0-840).

Per T-P0-840 ([Meta-MLSD D]). Target: company_documents row for company_id=31
(Meta) titled '[Meta-MLSD] 45min Playbook + 4 Strong Moments'.

This is the main hub: ~6KB high-density summary, all heavy content links out
to drawers. T-P0-833 will later promote this to is_golden=1 so it becomes
Meta company default first page.

DEPS (resolved at task start, verified runtime):
  - sd://meta-reels-golden  → canonical 45-min walkthrough (T-P0-837)
  - cd://94                 → Family Taxonomy + 13 question cards (T-P0-838)
  - cd://95                 → Cross-cutting 9-piece reusable library (T-P0-839)

SOURCE:
  docs/prep/meta_mlsd_2026-05-11/source_01_pacing_golden.md
    - Lines 1-68:   timing split / strong moment ROI / E4 vs E5 / 4 moments
    - Lines 93-138: Framing/Body/Strong/Zoom-out 元结构 + ML-native vocab +
                    timing skeleton + E4 NOT E5 + drift recovery
    - Lines 353-362: 8 meta-rules

DB TARGET: data/mle_prep.db, table=company_documents
  is_golden  = 0 (T-P0-833 promotes to 1 later)
  doc_kind   = 'prep_note'
  source_type = 'manual'

Idempotency: sentinel <!-- META_MLSD_MAIN_HUB_20260511 --> gates the write.
Second run = 0 writes when content is byte-identical.

Style:
  - Chinese narration + English ML terms (first-occurrence pattern)
  - Hook phrase = English verbatim (don't translate)
  - Compact tables; main page hard cap 8KB → if larger, push to drawer
  - NO strong-moment 全文台词 (that's in sd://meta-reels-golden)
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_MLSD_MAIN_HUB_20260511 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-MLSD] 45min Playbook + 4 Strong Moments"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"
IS_GOLDEN = 0

FAMILY_DOC_ID = 94  # T-P0-838
JIMU_DOC_ID = 95    # T-P0-839
RECSYS_MODELS_DOC_ID = 97  # T-A: RecSys 核心模型 8 工作 (T-P0-842)
SD_SLUG = "meta-reels-golden"  # T-P0-837

CONTENT = f"""{SENTINEL}

# Meta MLSD 45-min Playbook (加面 2026-05-XX)

> **当一次面试通知**: 用户被临时通知 Meta ML Design 加面. 这本 hub 是 30 分钟可读完的高密度 playbook. 重内容全部下沉到 drawer — 此页只放骨架 + 关键句式 + 4 strong moment 投放位置 + 决策树.

---

## 1. 节奏 Timing Skeleton (45min)

> **每行 4 tag**: rhythm (节奏轴 vocab) + twist (sd:// callback) + scale (数字 anchor) + trade (一句话 trade-off / 节奏规则). `-` 表示该 tag 在此 row 不适用 (rhythm + trade 必须非空, twist + scale 可空).

| 时间段 (time_band) | rhythm | Strong moment | Twist (sd://) | Scale anchor | Trade-off / 节奏规则 |
| --- | --- | --- | --- | --- | --- |
| 0-3 min | Framing | - | - | - | 60s declarative propose + 30s yes/no 收尾; 前 90s no-clarification — costs surface 广度, gains 节奏 |
| 3-5 min | Framing | #1 | unique ML-native twist · sd://{SD_SLUG} | - | I pick 1 ML-native twist over generic SDE framing; costs broader scope, gains "this candidate understands the problem class" signal |
| 5-12 min | Data | - | - | label schema 3-part (source / schema / bias) | I pick source-then-label-then-bias walk over flat enumeration; costs verbatim preamble, gains rhythm |
| 12-15 min | Data | #2 | multi-head label + duration confounder + ambiguous-middle · sd://{SD_SLUG} | multi-task heads (click / watch / like / share) | I pick multi-task heads over single binary; costs label-store complexity, switches to single label if data <10M events/day |
| 15-25 min | Model | - | - | retrieval ~10k candidate + ranking 200ms budget; two-tower 128-dim | I pick retrieval-then-ranking funnel + deepen ONE branch (主动问面试官); costs the other branch's depth, gains face-time on senior signal axis |
| 25-28 min | Bias | #3 | quantified production scar · sd://{SD_SLUG} | two-tower 128-dim, ~10k candidate, single-digit ms p99; ~200 features ceiling | I pick focused ~200-feature set over kitchen-sink; costs marginal recall, gains training-distribution stability (eBay scar) |
| 28-35 min | Evaluation | - | - | offline sliced + counterfactual replay + online A/B + long-term holdout | I pick counterfactual replay + long-term holdout over A/B-only; costs setup time, gains exposure-bias defense |
| 35-40 min | Zoomout | #4 | top 3 risks + invite deepening · sd://{SD_SLUG} | - | I pick zoom-out-and-rank-3-risks over linear brain-dump; costs 3-min budget, gains E5 system-thinking + communication signal |
| 40-45 min | Serving | - | - | cache / index / latency budget surfaced only on probe | I pick deprioritize-serving over deep-dive; costs perceived serving knowledge, gains "know what matters" senior signal |

---

## 2. Twist 挖掘方法论

> 任何新题, 30 秒过 4 轴定位 + 4 段模板推导 twist; 不要靠题感. Reels 7 条 twist 是这套方法的 worked example, 投放在 Strong Moment #1.

### 2.1 顶层 4 轴 (拿到题先过一遍)

| 维度轴 | 检查点 | Reels 示例 |
| --- | --- | --- |
| **业务结构** | marketplace 模式 / 内容形态 / 入口语义 (search vs feed vs notification) | Home feed 入口 = 无 explicit query intent + 双边 creator marketplace |
| **数据特性** | 模态 (text/visual/audio) / label noise / 偏差 surface (position / duration / selection) | 多模态 UGC + watch-time noisy + feedback loop selection bias |
| **用户行为** | session 长度 / fatigue / 双边对称性 (creator vs consumer) | Session-level fatigue + slate 内 redundancy; creator equity |
| **系统约束** | scale (candidate pool / QPS) / latency / freshness | 10^8 candidate + 200ms budget + content freshness 小时级 |

**用法**: 30 秒过一遍 4 轴, 每轴标记 1-2 个非通用属性, 转化为 design implication.

> §2.2 (abstract 4-段 template) 已下沉到 sd-golden worked examples (T-P0-866): 抽象模板换成 4 个 concrete 45-min walkthrough (Reels Golden / Top-3 Comments Golden / Weapon Ads Golden / Friend Rec Golden, links in 顶部 Drawer 入口). cd96 是 homepage 只放方法论 + 4 strong moment 投放位置; 推导细节读 drawer 里的 sd-golden.

### 2.3 Reels Homefeed 7-twist worked example

> 用 Reels 作示例, 忽略短/长视频差; 此处列 Generic 对比 + 核心特点 + Design implications, AI 补充见 2.4.

1. **Homefeed = no explicit query intent**
   - Generic 对比: search 有 query token 做强信号; feed 没有
   - 核心特点: user 表征本身就是 query
   - Design implications: retrieval 必须 user-conditioned 2-tower + **hybrid serving** (active user 离线 batch cache + fresh content 在线 incremental, blend at retrieval)
2. **Multimodal UGC** (visual + audio + text caption)
   - Generic 对比: tabular feature CTR 模型用 hand-crafted embedding 即可
   - 核心特点: 内容形态高维异构 + cold-start 频繁
   - Design implications: visual + audio + text encoder + 多模态融合 (cross-attention / concat); UGC 级联到 label / guardrail / cold-start
3. **Personalized (user-conditioned) ranking**
   - Generic 对比: 经典 LambdaRank 等是 user-independent listwise
   - 核心特点: 用户偏好高度个性化, listwise interaction 必须 conditioned on user
   - Design implications: 2-tower 解决 scale + DLRM / DCN deep crossing 解决 personalization depth
4. **Watch-time as primary signal**
   - Generic 对比: 通用 ranking 用 binary click 二分类
   - 核心特点: Reels 完成度比绝对秒数更可比 (15s 短视频 vs 60s 视频不可同尺度)
   - Design implications: weighted logistic / multi-task heads (click / watch / like / share); Reels 版微调: completion ratio > 绝对秒数
5. **Two-sided marketplace / creator equity**
   - Generic 对比: 单边 ranking 只优化 consumer utility
   - 核心特点: creator 也是利益方 (创作者激励 / 长尾保护)
   - Design implications: creator-level diversity + 长尾保底曝光 + creator retention metric
6. **Session-level fatigue / slate optimization**
   - Generic 对比: pointwise scoring 独立打分每个 item
   - 核心特点: session 内对相似内容产生 fatigue; slate 内顺序与组合都影响 utility
   - Design implications: page-aware re-ranking, MMR (Maximal Marginal Relevance), DPP; session-level metric (session length / dwell)
7. **Feedback loop / selection bias**
   - Generic 对比: 假设 training distribution = serving distribution
   - 核心特点: 模型输出影响下一轮 training label, exposure 偏差累积 (T-D 第 10 积木的本体, 互相引用)
   - Design implications: **IPS (Inverse Propensity Score)** + epsilon-greedy / Thompson sampling + counterfactual replay

### 2.4 AI 补充: 2 个最容易讲错的细节

**(a) Personalized ≠ pointwise** (cd://{RECSYS_MODELS_DOC_ID} §2 DLRM 也有对应 sidebar, 互相 cross-reference): 学习目标轴 (pointwise / pairwise / listwise) 与 打分函数输入轴 (user-independent / personalized) **正交**. DLRM 就是 personalized + pointwise. 现场表述应是 "user-independent ranking 不适用" 而不是 "pointwise 不适用".

**(b) UGC 级联**: UGC 不只影响 feature, 还级联到 label / guardrail / cold-start:
- **Label**: UGC 上不能 raw click 当 label (creator spam / clickbait 高), 需要 watch-time + 人工标注 sub-graph
- **Guardrail**: retrieval 阶段 hard filter (NSFW / 违规) — 不能放到 ranking 才 filter, candidate set 会污染
- **Cold-start**: content embedding 是必要 (反向加强 — collaborative filtering 单独不够, item-side embedding 才能 cold-start)

---

## 3. 4 Strong Moments — 预分配到固定位置

> 不要临场决定. 每个 moment 包含 mechanism (为什么 strong) + timing-window + hook phrase (英文 verbatim).

### Strong Moment #1 — Unique twist 洞察 (Framing, 3-5 min)
**Mechanism**: 在 framing 末尾 surface 该题区别于通用 ranking 的 1 个 ML-native twist (e.g. Reels 是 session-based not item-pick; Notification 是 send-or-not gating not rank). 面试官 calibrate level 时立即识别为 "this candidate understands the problem class". **何时投放**: framing yes/no 收尾前 60s. **Hook phrase**: *"There are two intrinsic specialties of this problem that will drive most of my design decisions, and I want to put them on the table upfront."*

### Strong Moment #2 — Sophisticated label / bias insight (Data, 12-15 min)
**Mechanism**: 不止说 "I'll use clicks as label", 而是展开 multi-head label schema + 1 个 non-obvious confounder (duration / position bias) + ambiguous middle 处理. 这是 E4 必备 label-nuance signal. **何时投放**: data 段过完 source 后, 切到 label schema 前. **Hook phrase**: *"And this is where [problem] diverges from standard ranking — I'd argue against a single binary label, in favor of multiple labels feeding multi-task heads."*

### Strong Moment #3 — Production scar / 量化直觉 (Model or Bias, 25-28 min)
**Mechanism**: 一句带数字的 production insight, 或一段 eBay scar. 数字让 candidate 显 senior 即使数字不精确, 方向对就行. **何时投放**: model 段你自己 deep dive 时, 或 bias 段切到 mitigation 时. **Hook phrase**: *"In my eBay work, we found that adding more features beyond ~200 actually hurt because the model overfit to training distribution shifts. So I'd start with a focused feature set and validate freshness/coverage before expanding."*

### Strong Moment #4 — Zoom-out summary + top 3 risks (35-40 min)
**Mechanism**: framework-level 总结 + 3 个 risk 各带 mechanism + alarm signal. 同时展示 system thinking 和 communication, 是 E5 boundary signal. **何时投放**: evaluation 段结束后, serving 段开始前. **Hook phrase**: *"Let me zoom out for a sec — we've covered retrieval, ranking, and labels. The three biggest risks I see in this design are: (1) ..., (2) ..., (3) ...  I'd want to address these in order — want me to go deeper on any?"*

→ **完整 Reels Golden Example 走全套 4 moments**: [Reels Home Feed (45min walkthrough, 8 段台词 verbatim) →](sd://{SD_SLUG})

---

## 4. ML-Native Vocabulary — YES / NO 对照

| ❌ NO (SDE-SD 词, 会被 calibrate "didn't show ML depth") | ✅ YES (ML-native, 显 senior) |
| --- | --- |
| SLA / NFR / FR / QPS / read-write ratio | model class / label / feature / objective |
| service / API / cache / network | bias / drift / freshness / calibration |
| availability / consistency / replication | counterfactual / IPS / propensity / holdout |

**规则**: serving 段被面试官主动追问时再说 cache / index / latency budget. ML SD round 上每句话先下意识审查 — 出现 NO 列词 = 立刻切到对应 YES 列 reframe.

---

## 5. Framing / Body / Strong / Zoom-out 元结构

**Framing (60-90s)**: 2-twist thesis (each 45-60s), 每 twist 含 what / why-this-problem-specific / ML implication / cost; 末尾 active deprioritize "I'm choosing not to deep-dive on X, Y" + yes/no 收尾. **Body (each section)**: sub-section announcement ("N parts: A, B, C") → list bullets → 立刻 pick 1 expand 60s → surface 1 non-obvious risk → transition "unless you want to deepen X". **Strong (4 个预分配)**: state reframe → 3 concrete actions with who/what/cost/量化 → failure modes + mitigation → trade-off ("X is stronger but costs Y"). **Zoom-out (3 min before end)**: 3-sentence summary → top 3 risks with mechanism + alarm signal → invite deepening.

**机械规则**: 列完 N 个 bullets **立刻** pick 1 expand 到 60s — 不要列完直接停在 bullet 层.

---

## 6. 偏好节奏 Meta-rules (8 条)

1. 前 90s 不要问 clarification 问题 — 直接 propose framing 并用 yes/no 收尾.
2. 每个开放问题给 60-90s 回答 — 不要 30s, 不要 2 min.
3. 列完 N 个 bullets 立刻 pick 1 expand — 机械规则, 不允许停在 bullet 层.
4. 每个 strong moment 包含 trade-off — "X is stronger but costs Y".
5. 每 8-10 min 主动 zoom-out 或邀请方向选择 — 避免线性 brain dump.
6. 面试官表情困惑时立刻 park 当前 topic — *"let me park that, more important is..."*
7. Serving 段主动短 — 这是 deprioritize signal, 显示 know-what-matters.
8. Wrap 时一定有 top-N risks — E5 boundary signal, 也是 E4 strong 必备.

---

## 7. 减少澄清的广度 NOT 深度

减少 clarification 的"广度"是对的, 但**不要**减少"深度". 区别: ❌ 不再 triage email / push / in-app / portal 这种 surface 维度 ❌ 不展开 FR / NFR / QPS / availability ✅ **要**快速锁一句话假设 (*"I'll assume we're optimizing for in-app notification ranking with a daily candidate pool of ~1000 per user, latency budget ~200ms"*) 说完就往下走, 不等面试官反复确认; ✅ 每个 ML 决策点 surface trade-off, 但**自己**给推荐答案, 不把选择权抛回去. 上一面 "on track" 但加面 = 方向对, 深度和决断力不够 — 这次"快速 frame、自信决策、深入 ML 内核".

---

## 8. E4 标准 vs E5 加分上限

| 维度 | E4 必须做到 (4 条) | E5 加分项 (3 条) |
| --- | --- | --- |
| 模型选择 | Pick a reasonable model + justify trade-offs | Novel reframe (e.g. "exposure bias 是 data acquisition 不是 training correction") |
| 风险识别 | Identify top 2-3 risks in the design | Cross-functional thinking (product / growth pays part of ML's bill) |
| Production sense | Data freshness / monitoring / rollback awareness | Paper citation (DLRM / DCN-V2 / MMoE / specific arxiv) |
| 驱动节奏 | Drive conversation forward without getting stuck | (E5 不强求 V1→V2 演进, 但有则加分) |

**E4 NOT E5 边界警告**: 不要 invent novel methods; 不要 over-scope ("2 years out we'd..."); **DO**: confident execution of standard playbook + 1-2 deeper insights. 加面被 push 的诱惑是去够 E5 但反而 miss E4 必做 — 优先 4 必做, 再够加分项.

---

## 9. Drawer — 深内容入口

- **完整 45-min 端到端台词 (Reels Home Feed)**: 8 段 verbatim 台词 + 4 strong moment 精确投放位置 + 关键 verbal pattern → [sd://{SD_SLUG}](sd://{SD_SLUG})
- **Family Taxonomy + 13 题型卡片 (Q1-Q13)**: 每题 Twist / Puzzle pieces / Anti-patterns / Hook phrase → [cd://{FAMILY_DOC_ID}](cd://{FAMILY_DOC_ID})
- **Cross-cutting 9 个 ML 积木库 (跨题通用思维模块)**: two-tower / multimodal embedding / multi-head / IPS / active exploration / LLM-teacher / long-term holdout / calibration / slice metrics → [cd://{JIMU_DOC_ID}](cd://{JIMU_DOC_ID})

---

## 10. 30 秒判题流程

看到题 → 30s 内判断 family (rec / ranking / classification / search / event / graph) → 跳到 [cd://{FAMILY_DOC_ID}](cd://{FAMILY_DOC_ID}) 找对应卡片读其 Twist + Puzzle pieces + Hook phrase → 从 [cd://{JIMU_DOC_ID}](cd://{JIMU_DOC_ID}) 取适配积木 (rec/ranking 类默认套 1+3+4+5+7; classification 类套 6+7+9; cold-start heavy 类套 2+5; graph 类不套 two-tower) → 投放 hook phrase → 按 Section 1 timing skeleton 走 45 分钟 → 35-40 min 必投放 Strong Moment #4 zoom-out + top 3 risks.
"""


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload (mirrors task spec AC)."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")

    # T-P0-866: Section 1 timing table grew from 4-col to 6-col (R-TIMING-row-4tag);
    # Section 2.2 abstract template deleted (R-FORBID-per-twist-4-section-template).
    # Net: +~900 chars (bigger table) - ~480 chars (deleted §2.2 body) = +~420.
    # Upper bound bumped from 12000 to 13000 to accommodate.
    n = len(content)
    if not (8500 <= n <= 13000):
        raise RuntimeError(f"content char-length {n} not in [8500, 13000]")

    # AC #3: 3 drawer URIs (sd://meta-reels-golden + cd://94 + cd://95).
    for uri in (
        f"sd://{SD_SLUG}",
        f"cd://{FAMILY_DOC_ID}",
        f"cd://{JIMU_DOC_ID}",
    ):
        if uri not in content:
            raise RuntimeError(f"drawer URI missing: {uri!r}")

    # T-P0-847: 10 H2 sections (Section 2 'Twist 挖掘方法论' inserted).
    h2_count = sum(1 for ln in content.splitlines() if ln.startswith("## "))
    if h2_count != 10:
        raise RuntimeError(f"expected 10 '## ' H2 sections, got {h2_count}")

    # AC #5: 4 'Strong Moment #' anchors (#1-#4).
    for i in range(1, 5):
        if f"Strong Moment #{i}" not in content:
            raise RuntimeError(f"Strong Moment #{i} marker missing")

    # AC #6: YES/NO table — NO column has >=2 of (SLA, QPS, ...) AND
    # YES column has >=2 of (label, feature, ...).
    no_terms = ["SLA", "QPS", "NFR", "FR", "service", "API", "cache"]
    yes_terms = [
        "label",
        "feature",
        "objective",
        "bias",
        "calibration",
        "drift",
        "counterfactual",
    ]
    no_hits = sum(1 for t in no_terms if t in content)
    yes_hits = sum(1 for t in yes_terms if t in content)
    if no_hits < 2:
        raise RuntimeError(
            f"YES/NO table NO column: need >=2 of {no_terms}, got {no_hits}"
        )
    if yes_hits < 2:
        raise RuntimeError(
            f"YES/NO table YES column: need >=2 of {yes_terms}, got {yes_hits}"
        )

    # Section 1 timing skeleton: 9-row markdown table (header + sep + 9 rows
    # >= 11 lines starting with '|').
    table_lines = [
        ln for ln in content.splitlines() if ln.lstrip().startswith("|")
    ]
    if len(table_lines) < 11:
        raise RuntimeError(
            f"timing skeleton table too short: {len(table_lines)} '|'-lines; "
            f"need >=11 (header + sep + 9 data rows)"
        )

    # T-P0-866: Section 1 timing table MUST be 6 columns per R-TIMING-row-4tag
    # (time_band | rhythm | strong_moment_slot | tag_twist | tag_scale | tag_trade).
    # Locate the Section 1 table by scanning from "## 1." heading to next "## ".
    lines = content.splitlines()
    sec1_start = next(
        (i for i, ln in enumerate(lines) if ln.startswith("## 1.")), None
    )
    if sec1_start is None:
        raise RuntimeError("Section 1 heading '## 1.' not found")
    sec1_end = next(
        (
            i
            for i, ln in enumerate(lines[sec1_start + 1:], sec1_start + 1)
            if ln.startswith("## ")
        ),
        len(lines),
    )
    sec1_table_rows = [
        ln for ln in lines[sec1_start:sec1_end]
        if ln.lstrip().startswith("|") and "---" not in ln
    ]
    if len(sec1_table_rows) < 10:  # 1 header + 9 data rows
        raise RuntimeError(
            f"Section 1 timing table has {len(sec1_table_rows)} non-sep rows; "
            f"need >=10 (1 header + 9 data rows)"
        )
    # Each row must have exactly 6 cells (5 internal "|" + 2 outer = 7 pipe chars).
    for row in sec1_table_rows:
        pipe_count = row.count("|")
        if pipe_count != 7:
            raise RuntimeError(
                f"Section 1 row has {pipe_count} '|' chars (need 7 for 6 cols): "
                f"{row[:120]!r}"
            )

    # T-P0-866: forbidden_pattern R-FORBID-per-twist-4-section-template must
    # NOT match. Scope = cd96_playbook.
    import re
    forbidden = re.compile(
        r"Per-twist 4-section template|Per-twist 4\s*段推导模板",
        re.IGNORECASE,
    )
    if forbidden.search(content):
        raise RuntimeError(
            "R-FORBID-per-twist-4-section-template matched; §2.2 should be deleted"
        )


def main() -> int:
    """Upsert the Meta MLSD main hub doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)
    print(
        f"[OK] content validated: chars={len(CONTENT)} "
        f"bytes={len(CONTENT.encode('utf-8'))}"
    )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # 1. Verify Meta company.
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        # 2. Defensive: verify all 3 upstream drawers exist (fail-loud per
        # task spec — "若任何 query 返回 0 行 → 报错 + 不要 INSERT").
        family = conn.execute(
            "SELECT id, title FROM company_documents "
            "WHERE id = ? AND company_id = ?",
            (FAMILY_DOC_ID, COMPANY_ID),
        ).fetchone()
        if family is None or "Family Taxonomy" not in family[1]:
            print(
                f"[ERROR] cd://{FAMILY_DOC_ID} (Family Taxonomy) backlink "
                f"missing or drifted: row={family!r}"
            )
            return 1
        print(f"[OK] cd://{FAMILY_DOC_ID} verified: {family[1]!r}")

        jimu = conn.execute(
            "SELECT id, title FROM company_documents "
            "WHERE id = ? AND company_id = ?",
            (JIMU_DOC_ID, COMPANY_ID),
        ).fetchone()
        if jimu is None or "Cross-cutting" not in jimu[1]:
            print(
                f"[ERROR] cd://{JIMU_DOC_ID} (Cross-cutting) backlink "
                f"missing or drifted: row={jimu!r}"
            )
            return 1
        print(f"[OK] cd://{JIMU_DOC_ID} verified: {jimu[1]!r}")

        sd = conn.execute(
            "SELECT id, slug FROM system_designs WHERE slug = ?",
            (SD_SLUG,),
        ).fetchone()
        if sd is None:
            print(f"[ERROR] sd://{SD_SLUG} (Reels Golden) missing")
            return 1
        print(f"[OK] sd://{SD_SLUG} verified: id={sd[0]}")

        # 3. Upsert.
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
                "is_golden, content_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    IS_GOLDEN,
                    new_hash,
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
                f"[INSERT] id={new_id} chars={len(CONTENT)} "
                f"bytes={len(CONTENT.encode('utf-8'))} "
                f"hash={new_hash[:12]}..."
            )
        else:
            existing_id, existing_content = existing
            if SENTINEL in existing_content and existing_content == CONTENT:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel present + "
                    f"content byte-identical; 0 writes"
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
                    f"new_len={len(CONTENT)} delta={len(CONTENT) - old_len:+d}"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
