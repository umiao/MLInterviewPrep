"""Seed: T-P0-893 [Meta-MLSD] sd42 meta-top3-comments-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for
``slug='meta-top3-comments-golden'`` (sd42) with a Chinese-narration +
English-terms speaking skeleton distilled from sd42's existing 45-min
口播稿 (which lives in the ``dataflow`` column, ~10.5KB, produced by
``scripts/seed_meta_top3_comments_golden_sd.py``).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892). The
machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD42_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker (the single 压舱石 twist; here:
    selection bias on unexposed comments -- sd42's signature difficulty)
  - 3-5 ``[floating-twist]`` markers (4 used: Selection Bias / Relational
    Comment / Early-Comment Time-Bias / Compliance Category-Error)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI no-bundle: own URI ``sd://meta-top3-comments-golden``;
    sibling goldens referenced via ``sd://<slug>`` (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SCOPE GUARD DIFFERS FROM sd41:
  sd41 (Reels) is the ``oral_narrative`` archetype where architecture /
  production_constraints / tradeoffs / defense are deliberately NULL, so
  sd41's seed scope-guards them as *empty*. sd42 is the default
  ``structured_reference`` archetype (per ``schemas/meta_mlsd_canonical.yaml``
  > ``document_archetypes`` note: "oral_narrative ships ONLY on sd41"): its
  architecture / dataflow / tradeoffs / defense are *legitimately populated*.
  Therefore this seed's scope guard does NOT assert those columns are empty
  -- it fingerprints every column EXCEPT ``verbal_outline`` and ``updated_at``
  before the write and asserts the fingerprint is byte-identical after,
  enforcing the task contract "ONLY touch verbal_outline; other fields stay
  as-is" without making a false oral_narrative assumption.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed
(``seed_meta_top3_comments_golden_sd.py``); a verbal-only seed recomputing it
would couple two seeds.

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd42 row -- run
``scripts/seed_meta_top3_comments_golden_sd.py`` first if missing).

Usage::

    python scripts/seed_meta_meta_top3_comments_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-top3-comments-golden"
SENTINEL = "<!-- SD42_VERBAL_V1_20260515 -->"

# Mechanical-check contract (mirrors sd41 golden template). Keep these
# literals unique in VERBAL_OUTLINE.
DOMINANT_MARKER = "[DOMINANT]"
FLOATING_TWIST_MARKER = "[floating-twist]"
BEST_ANCHOR_MARKER = "[best-anchor]"
WORST_ANCHOR_MARKER = "[worst-anchor]"
MIN_CHARS = 2500          # AC hard floor
TARGET_MIN, TARGET_MAX = 3000, 5000   # template target band
FLOATING_TWIST_MIN, FLOATING_TWIST_MAX = 3, 5

# All columns EXCEPT verbal_outline (the one we set) and updated_at (bumped
# only when verbal_outline changes). The scope guard fingerprints these and
# asserts byte-identity across the write.
SCOPE_GUARD_COLUMNS = (
    "id", "slug", "title", "subtitle", "diagram_filename", "overview",
    "architecture", "dataflow", "formulas", "production_constraints",
    "tradeoffs", "defense", "display_order", "created_at", "content_hash",
    "source_path", "cheat_sheet",
)


VERBAL_OUTLINE = f"""\
{SENTINEL}
# Top-3 Comments — Verbal Outline (45min 口播骨架)

> sd42 (Top-3 Comments under a Post) 的口播骨架。完整逐字稿在本题 `dataflow` tab; 方法论 (timing skeleton / Strong Moment 调度 / 8 meta-rules) 在 `cd://96`。本题严格 1-problem-1-URI: `sd://meta-top3-comments-golden`, 不 bundle sibling golden。

## 0 · 一句话主干

post 评论区 top-3 选取: 给定 (viewer, post), 从该 post comment pool 选 3 条置顶。pool bounded → 无 retrieval, formulate 成 ranking + set-selection: in-storage pre-filter (toxicity hard filter + 去重) → 两阶段 point-wise ranking (L1 cheap / L2 deep multi-task) → **Maximal Marginal Relevance** (MMR, 最大边际相关性) set rerank。objective 押 user-end (north-star = weekly commenter return rate); integrity guardrail 大头。input = (viewer, context, candidate comment), pool 是 corpus 非 input。

## Floating Twists — 调度图 (本题 4 个, 1 个压舱石)

> twist 不绑漏斗某一层, "漂"在整场: framing declarative 立, body 每个 component 兑现一次。主动调度, 别等挖。

### Twist 1 · Selection Bias on Unexposed Comments  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石——负向 label 才是核心难点。三阶: explicit (dislike/report) 直接用; exposed-not-engaged 拿独立 logging-policy model 估 propensity 做 **Inverse Propensity Score** (IPS, 反向倾向分数) reweighting; unexposed 是 naive 崩点 (全标负 = 教模型"没捞到的都是坏的"), 当 unknown 用 5% per-session bandit budget backfill。整场兑现 3 次: label (batch 配比)、model (bias tower 二道防线)、wrap (复利快过 mitigation → circuit breaker)。

### Twist 2 · Comment ≠ Generic Item (Relational Signal)  {FLOATING_TWIST_MARKER}

comment 是 ultra-short text (可能就 'lol'), 文本 low-signal, predictive 的是"谁说的 + viewer↔commenter 关系"——主导信号 relational 非 content-intrinsic。后果: (1) commenter 是 sub-entity 有自己 embedding 跨 post 学 shared representation; (2) 最 predictive 的是 viewer×commenter pair-level cross, serving 现算。这是 retrieval 只能 ranking、two-tower 做不了的结构性原因: dot product 表达不了 pair-level interaction。

### Twist 3 · Early-Comment Time-Bias  {FLOATING_TWIST_MARKER}

post 早期评论拿不成比例曝光, raw engagement count 把"到达时间"和"质量"confound。兑现: label 用 engagement-to-impression ratio (debias 前置到 label 层, 比 bias tower 早一道); feature 段 early engagement velocity 用 rate 非 count; serving 段该 feature 必须 streaming (否则 framing 承诺的 mitigation 跑不起来)。

### Twist 4 · Community Health 是 Guardrail 不是 Head  {FLOATING_TWIST_MARKER}

toxicity 是 disqualifying 的, 不是"engagement 少一点"。把 compliance 塞进 ranker head 或 loss 软项是常犯 category error。落地: toxicity 在 in-storage pre-filter 做 hard filter (ranker 之前), L2 只留 toxicity monitor head 观测不排序; metric 侧卡硬阈, 与 fairness 同 enforcement lane。model 段主动纠正。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: framing 就把 3 twist + selection-bias 压舱石 declarative 立起并 body 逐一兑现; 正向 label 用 engagement-to-impression ratio 并讲清为何前置 debias; 负向三阶 + IPS + 5% bandit 讲透; reranker 主动说"选 MMR 不选 **Determinantal Point Process** (DPP, 行列式点过程): n=3 太短, determinant 被单对 cosine 主导, top-10+ 才切 DPP"——本题最重要 trade-off; A/B user/session 级并解释 set 内 item 互相影响; wrap 3 risk, 尤其"reply 涨但 commenter return 跌 = rage gaming proxy → 4 周 holdout"。

{WORST_ANCHOR_MARKER} 不及格锚: comment pool 当 model input; toxicity 当 ranker head/loss 软项; unexposed 一律标负; two-tower 做 retrieval; n=3 硬上 DPP; A/B 用 impression 级; 当成普通 **Click-Through Rate** (CTR, 点击率) 排序题——本质是没认出 comment 的 relational + bounded-pool 结构。

## 8 段顺序 (真讲时连续说, 不报标题; 每段一句导航 cue)

1. Framing — ranking + set-selection; 边界 (亿级 **Daily Active Users** (DAU, 日活用户) / p99 200ms **Service Level Objective** (SLO, 服务水平目标)); 单一 north-star; 3 twist declarative。
2. Metrics — 3 proxy 挂 alignment; reply rate 配 sentiment (rage-comment); list-level diversity; guardrail (toxicity/report/p99)。
3. Labels (核心难点) — 正向 engagement-to-impression ratio; 负向三阶 + bandit; leakage guard。
4. Features — 四象限; 重点 commenter sub-entity + viewer×commenter pair cross (Twist 2)。
5. Model — pre-filter hard filter → L1 → L2 multi-task (shared bottom 起, negative transfer 升 **Multi-gate Mixture-of-Experts** (MMOE, 多门控专家混合)) + bias tower; rerank MMR 不 DPP; 冷启动 default fallback。
6. Evaluation — offline weighted **Normalized Discounted Cumulative Gain** (NDCG, 归一化折损累计增益) + binary **Area Under the Curve** (AUC, 曲线下面积); A/B user/session 级 + list-level **Mean Reciprocal Rank** (MRR, 平均倒数排名); monitor 四信号 (gap / **Kullback-Leibler divergence** (KL, KL 散度) shift / **Population Stability Index** (PSI, 群体稳定性指数) / engagement MA); 4 周 holdout。
7. Serving — shadow feature logging (async pub-sub; scar: inline 顶 p99 +30%); velocity streaming; prefetch 并行 RPC; hot post cache 5min TTL。
8. Wrap — zoom out + 3 risk (selection bias 复利 / loss 权重漂移 / reply 涨但 commenter return 跌 = proxy gaming, 4 周 holdout 抓)。

## 复用边界 (1-problem-1-URI)

此 outline 的 ranking + set-selection + 4-twist 调度是 Top-3 Comments 的 carve-up。与 Reels 2-stage 结构 ~70% 复用但 twist 调度图不同 (本题压舱石 selection bias, Reels session dynamics; 本题 bounded 跳过 retrieval, Reels 多路召回), 各自独立 URI——见 `cd://96` hub 与 `sd://meta-reels-golden` / `sd://meta-fb-newsfeed-golden` / `sd://meta-friend-rec-golden`, 不在此 row 内 bundle。
"""


def _now() -> str:
    """Return an ISO-8601 UTC timestamp with seconds precision."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def _content_self_check() -> list[str]:
    """Validate the in-module payload against the golden-template contract.

    Run before any DB write so a malformed template fails fast. Mirrors the
    sd41 reference assertion set (T-P0-892).
    """
    errs: list[str] = []
    body = VERBAL_OUTLINE
    n = len(body)

    if not body.startswith(SENTINEL):
        errs.append(f"sentinel {SENTINEL!r} must be on line 1")
    if n < MIN_CHARS:
        errs.append(f"length={n} < AC floor {MIN_CHARS}")
    if not (TARGET_MIN <= n <= TARGET_MAX):
        errs.append(
            f"length={n} outside template target band "
            f"[{TARGET_MIN}, {TARGET_MAX}]"
        )

    dom = body.count(DOMINANT_MARKER)
    if dom != 1:
        errs.append(f"expected exactly 1 {DOMINANT_MARKER}, found {dom}")

    ft = body.count(FLOATING_TWIST_MARKER)
    if not (FLOATING_TWIST_MIN <= ft <= FLOATING_TWIST_MAX):
        errs.append(
            f"expected {FLOATING_TWIST_MIN}-{FLOATING_TWIST_MAX} "
            f"{FLOATING_TWIST_MARKER}, found {ft}"
        )

    for marker in (BEST_ANCHOR_MARKER, WORST_ANCHOR_MARKER):
        c = body.count(marker)
        if c != 1:
            errs.append(f"expected exactly 1 {marker}, found {c}")

    # 1-problem-1-URI: this row must reference its own sd:// URI.
    if "sd://meta-top3-comments-golden" not in body:
        errs.append("missing own sd://meta-top3-comments-golden URI reference")

    # R-DRAWER-no-sd-drawer: no cd96 drawer table inside an sd-golden body.
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Doc ") and "sd://" in stripped:
            errs.append("forbidden cd96 drawer-header table literal present")
            break

    return errs


def _fingerprint(cur: sqlite3.Cursor) -> str:
    """Return a sha256 over every column EXCEPT verbal_outline / updated_at.

    Used as the scope guard: sd42 is the ``structured_reference`` archetype
    (its architecture / dataflow / tradeoffs / defense are legitimately
    populated, unlike sd41's ``oral_narrative``), so the guard cannot assert
    those columns are empty -- it asserts they are byte-identical across the
    write instead.
    """
    cols = ", ".join(SCOPE_GUARD_COLUMNS)
    cur.execute(f"SELECT {cols} FROM system_designs WHERE slug = ?", (SLUG,))
    row = cur.fetchone()
    if row is None:
        raise SystemExit(
            f"ERROR: no system_designs row for slug={SLUG}. Run "
            f"scripts/seed_meta_top3_comments_golden_sd.py first (this seed "
            f"only populates verbal_outline on an existing row)."
        )
    h = hashlib.sha256()
    for val in row:
        h.update(b"\x00")
        h.update(repr(val).encode("utf-8"))
    return h.hexdigest()


def upsert(cur: sqlite3.Cursor, dry: bool) -> str:
    """Idempotently set verbal_outline for SLUG; strict no-op if unchanged."""
    cur.execute(
        "SELECT id, verbal_outline FROM system_designs WHERE slug = ?",
        (SLUG,),
    )
    row = cur.fetchone()
    if row is None:
        raise SystemExit(
            f"ERROR: no system_designs row for slug={SLUG}. Run "
            f"scripts/seed_meta_top3_comments_golden_sd.py first (this seed "
            f"only populates verbal_outline on an existing row)."
        )

    rid, current = row
    if current == VERBAL_OUTLINE:
        return f"no-op id={rid} slug={SLUG} (verbal_outline already current)"

    if dry:
        return (
            f"DRY UPDATE id={rid} slug={SLUG} "
            f"verbal_outline: {len(current or '')} -> {len(VERBAL_OUTLINE)} chars"
        )

    cur.execute(
        "UPDATE system_designs SET verbal_outline = :v, updated_at = :now "
        "WHERE slug = :slug",
        {"v": VERBAL_OUTLINE, "now": _now(), "slug": SLUG},
    )
    return (
        f"updated id={rid} slug={SLUG} "
        f"verbal_outline: {len(current or '')} -> {len(VERBAL_OUTLINE)} chars"
    )


def validate(cur: sqlite3.Cursor, scope_fp_before: str) -> list[str]:
    """Post-write DB-side validation against the golden-template contract.

    ``scope_fp_before`` is the fingerprint of all non-(verbal_outline,
    updated_at) columns captured BEFORE the write; this function recomputes
    it and asserts byte-identity (the sd42 scope guard).
    """
    errs: list[str] = []

    cur.execute(
        "SELECT id, verbal_outline FROM system_designs WHERE slug = ?",
        (SLUG,),
    )
    rows = cur.fetchall()
    if len(rows) != 1:
        return [
            f"AC FAIL: expected exactly 1 row for slug={SLUG}, got {len(rows)}"
        ]

    rid, verbal = rows[0]

    if not verbal:
        errs.append("AC FAIL: verbal_outline is empty after seed")
        return errs

    n = len(verbal)
    if n < MIN_CHARS:
        errs.append(f"AC FAIL: verbal_outline length={n} < {MIN_CHARS}")
    if not verbal.startswith(SENTINEL):
        errs.append("AC FAIL: sentinel marker not on line 1")

    dom = verbal.count(DOMINANT_MARKER)
    if dom != 1:
        errs.append(
            f"AC FAIL: mechanical check expects exactly 1 {DOMINANT_MARKER}, "
            f"got {dom}"
        )
    ft = verbal.count(FLOATING_TWIST_MARKER)
    if not (FLOATING_TWIST_MIN <= ft <= FLOATING_TWIST_MAX):
        errs.append(
            f"AC FAIL: mechanical check expects "
            f"{FLOATING_TWIST_MIN}-{FLOATING_TWIST_MAX} "
            f"{FLOATING_TWIST_MARKER} sections, got {ft}"
        )

    # Scope guard: every column except verbal_outline / updated_at must be
    # byte-identical to the pre-write snapshot.
    scope_fp_after = _fingerprint(cur)
    if scope_fp_after != scope_fp_before:
        errs.append(
            "AC FAIL: scope violation -- a column other than verbal_outline "
            "changed (fingerprint mismatch); this seed must touch ONLY "
            "verbal_outline"
        )

    scope_ok = "byte-identical" if scope_fp_after == scope_fp_before else "CHANGED"
    print(f"[OK] row id={rid} slug={SLUG}")
    print(f"     verbal_outline chars={n} (target {TARGET_MIN}-{TARGET_MAX})")
    print(f"     markers: DOMINANT={dom} floating-twist={ft}")
    print(f"     scope guard (other columns): {scope_ok}")
    return errs


def main() -> int:
    """CLI entrypoint."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    self_errs = _content_self_check()
    if self_errs:
        print("[FAIL] in-module template self-check:", file=sys.stderr)
        for e in self_errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERROR: db not found: {db_path}", file=sys.stderr)
        return 1

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    scope_fp_before = _fingerprint(cur)

    action = upsert(cur, args.dry_run)
    print(action)

    if args.dry_run:
        con.rollback()
        print("\nDRY-RUN: rolled back")
        con.close()
        return 0

    con.commit()
    errs = validate(cur, scope_fp_before)
    con.close()

    if errs:
        print("\n[FAIL] validation errors:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\n[DONE] sd42 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
