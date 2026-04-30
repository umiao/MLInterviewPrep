"""Seed Pinterest ML virtual onsite prep doc as the golden landing for company_id=29.

Source: Pinterest recruiter prep email + onsite loop overview attached to
Discord msg 1498909265539104789 (2026-04-28). Distilled into a 临场速查
landing doc covering all 5 sessions (DSA x2, ML Practitioner, ML SD,
Competency/HM) with eval criteria, sample topics, and Pinterest-specific
product framing (Pin / Board / Homefeed / Search / Ads).

Idempotency: sentinel <!-- PINTEREST_ONSITE_PREP_20260428 --> gates the write.
Second run = 0 writes when content is byte-identical.

Style: Chinese narration + English technical terms. No emoji.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- PINTEREST_ONSITE_PREP_20260428 -->"

COMPANY_ID = 29  # Pinterest
DOC_TITLE = "[Pinterest] ML Virtual Onsite Prep"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r'''
# Pinterest ML Virtual Onsite — Prep 笔记

> **Schedule lives on the Dashboard** (left-nav first item) — InterviewTimeline widget reads `interview_events` table. This doc is for prep narrative only.
>
> 5 场 virtual onsite，**no particular order**: 2× DSA (45 min) + 1× ML Practitioner (60 min) + 1× ML System Design (60 min) + 1× Competency/HM (45 min)。总 ~4h 10min。
> 核心 framing: 你不是 model 调参员，是从 problem framing 一路 own 到 deployment 的工程师，每个决策都能讲清 *为什么* 和 *放弃了什么*。

---

## §1 DSA × 2 (45 min × 2，1-2 题/场)

预期: 题面 tightly-scoped；要 production-quality + clean code，不是 leetcode 速通。Hint: 类似 phone screen 但只给 45 min 解 1-2 题，标准更严。

- **永远先 clarify**: input/output / 范围 / null / 是否就地修改 / 时空预算。沉默直接写 = 失分。
- **边讲边写**: 思路、复杂度、为什么选这个数据结构都口头讲。这场对标 "你写 PR + 同事 review"。
- **Code review 视角**: 写完自己走一遍 — off-by-one / 共享 collection mutate / 空 + 单元素 corner / 变量名是否自解释。
- **题型预期**: 一场偏算法 (graph / DP / two-pointer / interval)，一场偏 systems-flavored (LRU / rate limiter / scheduler，有状态)。
- **Trap**: 套模板但参数对不上；用 import 替代真正的实现 (Pinterest 想看你写出来，不是 import sortedcontainers)；happy-path 跑通就交，没考虑 corner。

---

## §2 ML Practitioner (60 min)

预期: 你 own 一个 model 从 framing 到 deployment 的全流程，**手边准备一个真的 deep-dive 项目**。

**4 个评估维度** (面试官会逐一钻):

1. **Problem framing & model selection**
   - 为什么要 ML？(vs heuristic / rule-based / 历史最优解)
   - 怎么 frame？ranking → 怎么造正负样本；regression → ground truth 怎么得到
   - 选了什么 model，跟其它候选的 tradeoff？
   - Offline metric 跟 business objective 怎么对齐？

2. **Featurization**
   - 多少 dense / sparse？feature importance 怎么算 (SHAP / permutation / gradient)？
   - 训练集 vs feature 维度，怎么防 overfit (reg / dropout / early stop / CV)？
   - Trap: 不能只说 "我加了正则" — 要讲 *为什么这个 reg 合适*。

3. **Deployment**
   - offline trained → online serve 怎么做 (TF Serving / Triton / batched inference)？
   - QPS 上限？latency p99 budget？
   - run-time 缺 feature 怎么 fallback (default / impute / parent feature)？
   - cold-start 怎么处理 (content-based / popularity prior / two-tower 上 sample-efficient retrieval)？

4. **Evaluation & online**
   - online A/B sample size / power / MDE / multiple comparison correction
   - guardrail metric (latency 不能升 / fairness 不能降)

**高频题型** (Pinterest 给的 sample):
- Detect unsafe content at Pinterest scale
- Ad CTR prediction (relevance + targeting + business obj)
- Homefeed Lightweight Ranking (latency-bound，不能上 cross-encoder)

---

## §3 ML System Design (60 min)

预期: 把 ML 嵌进 internet-scale 系统，**infra ↔ modeling 双向影响**都能讲。Patrick Halina 的 ML SD guide 是这场的官方 framework: http://patrickhalina.com/posts/ml-systems-design-interview-guide/

**永远先 gather requirement**:
- 候选类型 / 推荐场景？
- 多 responsive (near-realtime vs batch)？
- 用户量 / corpus 大小 / 单用户 reco 数？
- Latency 目标 (1ms / 1s / 1min / 1h — 不同 tier 完全不同架构)

**核心议题** (每个都要能讲 pros / cons / 何时不用):
- Training cadence: online vs nightly batch
- Retrieval: HNSW / LSH / FAISS / Two-Tower (recall vs latency vs index update cost)
- Ranking: GBDT vs DNN vs Transformer (latency / interpretability / feature scale)
- Serving: monolith vs microservice / cache 策略 / fallback path
- Monitoring: data drift / model drift / online vs offline metric divergence

**4 个高频 SD 题** (Pinterest 列的):
- Homefeed near-realtime candidate gen
- Homefeed responsive personalized recommendation
- Pinterest Search ranking
- Ads Funnel (retrieval → ranking → auction → pacing)

**面试官特别看的**:
- infra 选择如何影响 modeling capability (例: feature store delay → 不能用最新行为)
- product UI 如何影响 label gathering (impression / click / save / repin 是不同强度的 implicit feedback)
- 失败模式: bad reco 怎么 debug (traffic shadow / online eval / counterfactual / 用户 control 接口)
- 你最近读的 ML 论文 / 行业 idea — 准备 1-2 个能讲 5 分钟的

**资源** (官方推荐):
- Pixie blog: https://medium.com/pinterest-engineering/an-update-on-pixie-pinterests-recommendation-system-6f273f737e1b
- HNSW: https://arxiv.org/abs/1603.09320
- Two-Tower (YouTube): https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45530.pdf
- User Sequence Modeling for Pinterest Ads: https://medium.com/pinterest-engineering/user-action-sequence-modeling-for-pinterest-ads-engagement-modeling-21139cab8f4e

---

## §4 Competency / HM (45 min)

预期: ML leader 跟你聊 background / passion / 团队风格 / 怎么 handle challenge。**1 个 deep-dive 项目准备好** (5 min short / 15 min long 两个版本)。

- **Deep-dive 项目**: 你的 role / technical challenge / 决策 / impact (具体数字) / 学到什么。
- **Challenge / 失误**: 准备 2 个 — 一个技术失误 (e.g. 上线后发现 metric 选错) + 一个协作失误 (e.g. 跟 PM 沟通 misalignment)，每个都讲 *学到什么 + 现在怎么做*。
- **Impact framing**: business 数字 + ML 指标双线 ("CTR +X% / 直接收入 $Ym / latency 不变 / 之后被 N 个团队 adopt")。
- **HM 的隐线**: 你跟同事工作时是什么样？(协作、给 feedback、接 feedback)。准备 1 个 collaborator story + 1 个 mentor story。
- **Trap**: deep-dive 时只讲技术不讲 *决策权*；讲 challenge 时只讲发生了什么不讲 *学到什么*；提到 team 时全说 "我们" 不说 "我"。

---

## §5 共通 pattern (5 场都适用)

| 维度 | 做对的样子 | 翻车的样子 |
|------|-----------|-----------|
| 先 clarify 再下笔 | 3-5 个澄清问题，约束写出来 | 假设默认 spec 直接开始 |
| Tradeoff first | 每个选择都讲 *选 A 放弃了 B 的什么* | "我用 X 因为 X 好" |
| Real-world flavor | 讲 scale / latency / cost / monitoring | 只讲数学和 model 架构 |
| Pinterest 语境 | Pin / Board / Homefeed / Search / Ads | 通用 "user / item" 替身 |
| Self-critical | 主动指出方案缺点和可改进 | 一路 "这个方案完美" |

---

## §6 离场前 60 秒 cheat sheet

1. 我开口的第一句是 **clarification 还是 high-level**? (都不是 = 重置)
2. 我有没有讲过至少 **2 个 tradeoff**?
3. 我有没有用 Pinterest 的产品语境 (Pin / Homefeed / Search / Ads)?
4. 我有没有在某处主动 **surface 失败模式或 limitation**?

---

> **prep call (4/29 14:00 PT) 要确认的事**: (1) onsite 具体日期 (this week 哪两天) (2) 5 场顺序 (3) 是否有 take-home (4) 面试官是 ML team 哪个组 (5) HM 是谁。

'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## §1 DSA",
        "## §2 ML Practitioner",
        "## §3 ML System Design",
        "## §4 Competency / HM",
        "## §5 共通 pattern",
        "## §6 离场前 60 秒",
        "Patrick Halina",
        "HNSW",
        "Two-Tower",
        "Pixie",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    # No emoji invariant.
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
    if not (3000 <= len(content) <= 6000):
        raise RuntimeError(f"content length {len(content)} outside 3000-6000")


def main() -> int:
    """Upsert the Pinterest onsite prep doc as golden (idempotent)."""
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
            "SELECT id, content, is_golden FROM company_documents "
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
                "content_hash, is_golden, golden_at, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    new_hash,
                    1,
                    now,
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
                f"hash={new_hash[:12]}... is_golden=1"
            )
        else:
            existing_id, existing_content, existing_golden = existing
            if (
                SENTINEL in existing_content
                and existing_content == CONTENT
                and existing_golden == 1
            ):
                print(
                    f"[UNCHANGED] id={existing_id} sentinel + content + "
                    f"is_golden=1 all match; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, is_golden = ?, "
                    "golden_at = COALESCE(golden_at, ?), updated_at = ? "
                    "WHERE id = ?",
                    (CONTENT, new_hash, 1, now, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(CONTENT)} delta={len(CONTENT)-old_len:+d} "
                    f"is_golden -> 1"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
