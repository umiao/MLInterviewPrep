"""Seed: T-P0-892 [Meta-MLSD] sd41 meta-reels-golden verbal_outline (GOLDEN TEMPLATE).

Populates ``system_designs.verbal_outline`` for ``slug='meta-reels-golden'``
(sd41) with a Chinese-narration + English-terms speaking skeleton extracted
from the existing 45-min 口播稿 (which lives in the ``dataflow`` column,
8.6KB, produced by ``scripts/seed_meta_reels_golden_sd.py``).

WHY a separate seed (not folded into seed_meta_reels_golden_sd.py):
  sd41 is the ``oral_narrative`` archetype. Per
  ``schemas/meta_mlsd_canonical.yaml`` >
  ``document_archetypes.values.oral_narrative.contract.nullable_fields``,
  ``verbal_outline`` is *legal-NULL* (the archetype's seed deliberately NULLs
  it). It is NOT *forbidden* -- ``sd_golden.fields.verbal_outline`` is
  ``required: false, apply_3rule: false`` with only the
  ``R-XPAGE-verbal-no-cd96-dup`` duplication guard. The Meta-MLSD harmonization
  batch (T-P0-892 .. T-P0-896 + sd46-sd53) opts each of the 13 sd-goldens INTO
  a populated verbal_outline so the SystemDesignDrawer (which renders
  verbal_outline first since T-P0-891) has a consistent "speaking skeleton"
  tab. ``audit_meta_mlsd_3rule.py`` skips nullable columns regardless of
  whether they are NULL or populated, so this is audit-safe.

GOLDEN TEMPLATE: this is sd41 and DEFINES the verbal_outline shape that
sd42-sd53 mirror (T-P0-893 .. and the sd46-sd53 follow-on batch). The
machine-checkable contract this template establishes:
  - sentinel marker on line 1: ``<!-- SD41_VERBAL_V1_20260515 -->``
  - exactly 1 ``[DOMINANT]`` marker (the single strongest / 压舱石 twist)
  - 3-5 ``[floating-twist]`` markers (the cross-cutting twists, one per
    section; the DOMINANT one carries BOTH markers)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` (calibration anchors)
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI no-bundle: links sibling goldens via ``sd://<slug>``,
    never bundles them into this row
  - target length 3000-5000 chars (AC floor: >= 2500)

SCOPE: this seed touches ONLY ``verbal_outline`` (+ ``updated_at`` when the
value actually changes). It deliberately does NOT recompute ``content_hash``
or touch any other column -- ``content_hash`` is owned by the main archetype
seed (``seed_meta_reels_golden_sd.py``); a verbal-only seed recomputing it
would couple two seeds. The task contract is "ONLY touch verbal_outline;
other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd41 row -- run
``scripts/seed_meta_reels_golden_sd.py`` first if missing).

Usage::

    python scripts/seed_meta_reels_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-reels-golden"
SENTINEL = "<!-- SD41_VERBAL_V1_20260515 -->"

# Mechanical-check contract (also asserted in validate() and mirrored by
# sd42-sd53). Keep these literals unique in VERBAL_OUTLINE.
DOMINANT_MARKER = "[DOMINANT]"
FLOATING_TWIST_MARKER = "[floating-twist]"
BEST_ANCHOR_MARKER = "[best-anchor]"
WORST_ANCHOR_MARKER = "[worst-anchor]"
MIN_CHARS = 2500          # AC hard floor
TARGET_MIN, TARGET_MAX = 3000, 5000   # template target band
FLOATING_TWIST_MIN, FLOATING_TWIST_MAX = 3, 5


VERBAL_OUTLINE = f"""\
{SENTINEL}
# Reels Home Feed — Verbal Outline (45min 口播骨架)

> sd41 (Reels Home Feed Recommendation) 的口播骨架 / speaking skeleton。完整逐字稿在本题 `dataflow` tab; 方法论 (timing skeleton / Strong Moment / 8 meta-rules) 在 `cd://96`。此 outline 是进面前扫一眼的"主干 + twist 调度图"。本题严格 1-problem-1-URI: `sd://meta-reels-golden`, 不 bundle sibling golden。

## 0 · 一句话主干 (开口前在脑子里默跑一遍)

把题 formulate 成 Reels home feed 推荐: 给定 (user, context), 从亿级 corpus 返回一个有序 feed。两阶段漏斗——多路 retrieval (60/20/20 个性化/trending/diversity) → **Deep Learning Recommendation Model** (DLRM, 深度学习推荐模型) multi-task ranking → whole-page rerank; **User-Generated Content** (UGC, 用户生成内容) 的 multimodal embedding 在 upload 时算好缓存。objective 押 user-end 中长期价值 (7 日 retention / session 时长), revenue 与 integrity 进 guardrail。视频库是 corpus, 不是 model input——一次 request 的 input 是 (user, context, candidate item) 三组 feature。

## Floating Twists — 调度图 (本题 4 个, 1 个压舱石)

> 这些 twist 不绑定漏斗某一层, 它们"漂"在整场: framing 段 declarative 立起来, 后面每个 component 兑现一次。报的时候按这张图主动调度, 别等面试官挖。

### Twist 1 · Session Dynamics  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

本题最 signature、最强的 twist, 整场的压舱石。Reels 是 session-based 连续消费, 用户一次刷几十个; within-session fatigue / 兴趣 drift / diversity collapse 是 retention 的主杀手。落地: request-time 现算 in-session state feature (本 session 已看几个、累计完播率、最近 K 个 item 的 topic 分布) + session-aware ranker。这个 twist 整场至少兑现 3 次——feature 段 (in-session state 从 cross 单拎出来)、eval 段 (A/B 必须 session/user 级, 不能 impression 级, 因为 session 内 item 互相影响)、wrap 段 (fatigue 累积靠 long-term holdout 抓)。

### Twist 2 · Multimodal Lifecycle  {FLOATING_TWIST_MARKER}

UGC 短视频文本信号稀疏, content understanding 不能靠 metadata。pretrained video/audio/text encoder fused → 256-dim embedding, upload 时算一次、季度 refresh, 把 content-understanding cost 从 serving path 剥离。兑现点: 冷启动 item 靠它进 **Approximate Nearest Neighbor** (ANN, 近似最近邻) retrieval——engagement 统计量全空时这是新视频唯一的内容表征, fallback 到 category/creator 均值而不是 site 均值。

### Twist 3 · Exposure Bias  {FLOATING_TWIST_MARKER}

label 全是 conditioned on 我们推了什么, 本质 biased。处理: position/device 这类 bias feature 进一个独立 shallow bias tower, 训练时正常用、serving 时输入置 0; 比 training-time **Inverse Propensity Score** (IPS, 反向倾向分数) reweighting 更稳、更好 ship。边界一定要主动说: bias tower 只修 surface 过数据*内部*的 selection bias, 修不了根本没 surface 的那一类——必要但不充分, 完整答案靠 exploration 配合 (≈5% per-session 预算, gated by 质量过滤防低质套利)。

### Twist 4 · Ambiguous-Middle Label  {FLOATING_TWIST_MARKER}

看了 50% 然后划走, 既不是 hard negative 也不是 strong positive, 是真 ambiguous。处理: 在 watch-ratio head 当弱正样本 (label 直接用 watch_ratio 值), 在 early-skip head 直接从训练集排除。强行二元化 ambiguous middle 只往训练里加噪声。这是 Data&Label 段的 signature nuance, 必须主动讲, 别等追问。

## Anchor Calibration — best vs worst (自检: 我现在在哪一档)

{BEST_ANCHOR_MARKER} 满分锚: framing 就把 4 个 twist declarative 立起来并在 body 逐一兑现; watch_ratio 必 normalize 且 duration 既当 feature 又当 evaluation slice (主动说 confounder); compliance 是 hard filter 不是 rerank soft loss term, 这个 category error 主动纠正; A/B 用 session/user 级并解释 why; 收尾给 3 个 risk + 对应 alarm, 尤其 "watch time 涨但 retention 跌 → long-term holdout" 这条最重要的报警。

{WORST_ANCHOR_MARKER} 不及格锚: 把视频库当 model input; 单看完播率不提 duration confounder (系统性偏短视频); 把 compliance 塞进 rerank 的 soft objective; A/B 用 impression 级 (session 内污染); multimodal 与 session dynamics 完全没提, 当成一道普通 **Click-Through Rate** (CTR, 点击率) 推荐题做——落到这一档本质就是没认出这是 Reels。

## 8 段顺序 (每段一句话提示; 真讲时连续说, 不报标题)

1. Framing — formulate + 边界假设 (登录用户主线 / 亿级 DAU / p99 200ms **Service Level Objective** (SLO, 服务水平目标)) + objective(user-end > biz) + 4 twist declarative。
2. Data & Label — signal density vs bias 分层; watch_ratio 主 label 必 normalize; early-skip 是 Reels 天然 hard negative; ambiguous-middle nuance; duration 是 confounder。
3. Features — user/content/context/cross 四类, 把 in-session state 从 cross 单拎出来 (Twist 1 在 feature 层的落地); debias 集中在 feature/model 侧。
4. Model — retrieval vs generative 范式对比 (纠错: generative 对冷启动是弱点不是优势, 新 item 的 **Semantic ID** (SID, 语义 ID) 未必进 codebook); v1 走 retrieval; 多路召回 + log-Q correction; L1/L2 是同一思路的成本梯度 (L1 蒸馏小双塔, 不用 GBDT); rerank 区分 hard filter vs soft diversity (**Maximal Marginal Relevance** (MMR, 最大边际相关性) / **Determinantal Point Process** (DPP, 行列式点过程))。
5. 冷启动 — item 走 content-based + fresh-content channel + 5% exploration; user 走 onboarding 轻量 diverse 集。
6. Evaluation — per-head offline (**Normalized Discounted Cumulative Gain** (NDCG, 归一化折损累计增益) / **Area Under the Curve** (AUC, 曲线下面积)) 按 duration bucket + 用户 segment 切; online A/B session 级; 30 天 long-term holdout; offline-online 对齐显式追踪。
7. Serving / Logging — train-serving skew 首选 serving-time feature snapshot 根治; push-pull serving; retrieval/L1 sharded、L2 集中。
8. Wrap — zoom out + 3 个 risk (exposure bias 复利速度 / multi-task loss 权重漂移需重调 / watch time 涨但 retention 跌)。

## 复用边界 (1-problem-1-URI)

此 outline 的 2-stage + multi-task + 4-twist 调度是 Reels 这一题的 carve-up。Feed / Notification / Friend-rec / Ads / Top-3 Comments 结构 ~80% 复用但 twist 调度图不同, 各自独立 URI——见 `cd://96` hub 与 `sd://meta-top3-comments-golden` / `sd://meta-friend-rec-golden` / `sd://meta-weapon-ads-golden`, 不在此 row 内 bundle。
"""


def _now() -> str:
    """ISO-8601 UTC timestamp with seconds precision."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def _content_self_check() -> list[str]:
    """Validate the in-module payload against the golden-template contract.

    Run before any DB write so a malformed template fails fast (and so
    sd42-sd53, which mirror this shape, have a reference assertion set).
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

    # 1-problem-1-URI: sibling goldens referenced via sd:// (no bundle).
    if "sd://meta-reels-golden" not in body:
        errs.append("missing own sd://meta-reels-golden URI reference")

    # R-FORBID-drawer-header-literal: no cd96 drawer table inside sd-golden.
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Doc ") and "sd://" in stripped:
            errs.append("forbidden cd96 drawer-header table literal present")
            break

    return errs


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
            f"scripts/seed_meta_reels_golden_sd.py first (this seed only "
            f"populates verbal_outline on an existing row)."
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


def validate(cur: sqlite3.Cursor) -> list[str]:
    """Post-write DB-side validation against the golden-template contract."""
    errs: list[str] = []

    cur.execute(
        "SELECT id, verbal_outline, architecture, production_constraints, "
        "tradeoffs, defense FROM system_designs WHERE slug = ?",
        (SLUG,),
    )
    rows = cur.fetchall()
    if len(rows) != 1:
        return [f"AC FAIL: expected exactly 1 row for slug={SLUG}, got {len(rows)}"]

    rid, verbal, architecture, prod_cons, tradeoffs, defense = rows[0]

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

    # Scope guard: this seed must not have populated the archetype-NULL fields.
    for col, val in (
        ("architecture", architecture),
        ("production_constraints", prod_cons),
        ("tradeoffs", tradeoffs),
        ("defense", defense),
    ):
        if val:
            errs.append(
                f"AC FAIL: scope violation -- {col} unexpectedly non-empty "
                f"(this seed must touch ONLY verbal_outline)"
            )

    print(f"[OK] row id={rid} slug={SLUG}")
    print(f"     verbal_outline chars={n} (target {TARGET_MIN}-{TARGET_MAX})")
    print(f"     markers: DOMINANT={dom} floating-twist={ft}")
    print(
        f"     scope: architecture="
        f"{'NULL' if not architecture else len(architecture)} "
        f"tradeoffs={'NULL' if not tradeoffs else len(tradeoffs)} "
        f"defense={'NULL' if not defense else len(defense)}"
    )
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

    action = upsert(cur, args.dry_run)
    print(action)

    if args.dry_run:
        con.rollback()
        print("\nDRY-RUN: rolled back")
        con.close()
        return 0

    con.commit()
    errs = validate(cur)
    con.close()

    if errs:
        print("\n[FAIL] validation errors:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\n[DONE] sd41 verbal_outline golden-template seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
