"""Seed: T-P0-900 [Meta-MLSD] sd49 meta-ads-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for ``slug='meta-ads-golden'``
(sd49) with a Chinese-narration + English-terms speaking skeleton distilled
from sd49's existing English-only verbal_outline (~8.4KB).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45, sd46, sd47, sd48 mirrors. The machine-checkable contract is
identical:
  - sentinel marker on line 1 (here: ``<!-- SD49_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **Ads ranking IS calibrated probability feeding an auction** twist, sd49's
    signature framing: the system is NOT generic ordinal ranking; it is
    calibrated probability estimation feeding a second-price auction whose
    math (``bid * pCTR * pConversion * quality_score``) depends on absolute
    probability scale across advertisers. Skipping this is the failure-mode
    that swaps logloss for pairwise NDCG and silently breaks second-price
    billing; almost every other sd49 decision derives from this fork.
  - 3-5 ``[floating-twist]`` markers (4 used: Ads-IS-Calibrated-Probability /
    Delayed-Feedback-Windowed-Labels / IPS-Replay-Is-Structural /
    ML-Pacing-Boundary)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI: own URI ``sd://meta-ads-golden``; sibling goldens
    referenced via the ``cd://96`` hub at the end (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd49 is the ``oral_narrative`` archetype: architecture /
  production_constraints / tradeoffs / defense are all NULL (the archetype's
  legal-NULL columns per ``schemas/meta_mlsd_canonical.yaml`` >
  ``document_archetypes.values.oral_narrative.contract.nullable_fields``).
  ``verbal_outline`` is NULLable but NOT forbidden -- ``sd_golden.fields``
  is ``required: false, apply_3rule: false`` with only the
  ``R-XPAGE-verbal-no-cd96-dup`` duplication guard. The Meta-MLSD
  harmonization batch opts each of the 13 sd-goldens INTO a populated
  verbal_outline so the SystemDesignDrawer (which renders verbal_outline
  first since T-P0-891) has a consistent speaking skeleton tab.
  ``audit_meta_mlsd_3rule.py`` skips nullable columns regardless of whether
  they are NULL or populated, so this is audit-safe.

  Because sd49 is oral_narrative (matching sd41/sd43/sd44/sd45/sd46/sd47/sd48),
  this seed uses the sd41-style scope guard (assert architecture /
  production_constraints / tradeoffs / defense remain NULL after the
  write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references its own ``sd://meta-ads-golden`` URI in
twist/anchor/section text. Sibling goldens appear only at the end "复用边界"
section as "via ``cd://96``" pointers, mirroring the sd48 pattern. They are
not bundled into the body of the problem.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed;
a verbal-only seed recomputing it would couple two seeds. The task contract
is "ONLY touch verbal_outline; other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd49 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_ads_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-ads-golden"
SENTINEL = "<!-- SD49_VERBAL_V1_20260515 -->"

# Mechanical-check contract (mirrors sd41 golden template). Keep these
# literals unique in VERBAL_OUTLINE.
DOMINANT_MARKER = "[DOMINANT]"
FLOATING_TWIST_MARKER = "[floating-twist]"
BEST_ANCHOR_MARKER = "[best-anchor]"
WORST_ANCHOR_MARKER = "[worst-anchor]"
MIN_CHARS = 2500          # AC hard floor
TARGET_MIN, TARGET_MAX = 3000, 5000   # template target band
FLOATING_TWIST_MIN, FLOATING_TWIST_MAX = 3, 5


VERBAL_OUTLINE = f"""\
{SENTINEL}
# Meta Ads Ranking — Verbal Outline (45min 口播骨架)

> sd49 口播骨架。方法论 `cd://96`。1-problem-1-URI: `sd://meta-ads-golden`, 不 bundle。Ads 不是 ranking, 是 **calibrated probability** feeding 二价 auction; billing 依赖 advertiser 间 absolute probability scale。

## 0 · 一句话主干

Ads Ranking: 输出 calibrated {{pCTR, pConversion, pQuality}} 给 auction 做 `bid * pCTR * pConversion * quality_score` second-price 计费。漏斗——上游 targeting + brand-safety + frequency-cap 已 filter → **Multi-gate Mixture-of-Experts** (MMoE, 多门控混合专家) shared backbone + 三 split head (per-label logloss) → per-(vertical x objective x surface) **Isotonic Regression** (保序回归) → **Inverse Propensity Score** (IPS, 反向倾向分数) replay → A/B → auction + 独立 pacing。scale: ~3B users, p99 ~80-120ms, attribution 1-7d。

## Floating Twists — 调度图 (4 个, 1 个压舱石)

> twist 不绑某层, "漂"在整场: framing 立, body 兑现。

### Twist 1 · Ads IS Calibrated Probability Feeding an Auction  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石。不是 ordinal ranking, 是 calibrated probability feeding 二价 auction: `bid * pCTR * pConversion * quality_score`, billing 依赖 advertiser 间 absolute scale。换 pairwise **Normalized Discounted Cumulative Gain** (NDCG, 归一化折损累积增益) loss 表面涨 auction 崩——二价 under-charges。**I pick** logloss + 显式 calibration head over pairwise **because** auction 经济正确性 > ordinal 准确率。整场兑现 4 次: framing / head 各 logloss / sliced isotonic / wrap auction 边界。

### Twist 2 · Delayed-feedback Windowed Labels  {FLOATING_TWIST_MARKER}

pConversion 在 1-7d **attribution window** 内陆续到达, partially observed。**I pick** delayed-feedback windowed labels + per-objective bias correction over naive same-day cutoff **because** truncation under-counts 慢转化尾, calibration silently 下偏 ~10-30% on purchase; **costs**: per-campaign delay 估计 + 夜 reweighting; **switches to** same-day 仅 in-platform CTA。Purchase / app-install / lead-gen 各 delay 先验, per-objective NOT global。

### Twist 3 · IPS Replay Is Structural (advertisers re-bid)  {FLOATING_TWIST_MARKER}

Online A/B 在 ads 违反 i.i.d.——是 **advertiser-level**: 广告主 treatment 下重新 bid, advertiser 分布非平稳。**I pick** IPS counterfactual replay BEFORE A/B over A/B-first **because** A/B 数 days 后 advertiser 已 adapt, lift 被 response 污染; **switches to** A/B-first 仅 advertiser adaptation 机械不可能。Replay 打 win-rate / **Cost Per Mille** (CPM, 千次曝光成本) / conversion delta。

### Twist 4 · ML/Pacing Boundary (pacing 不进 loss)  {FLOATING_TWIST_MARKER}

ML 只 emit calibrated {{pCTR, pConversion, pQuality}}; auction 乘 bid + quality_score; **pacing 层** (PID 或 per-campaign LP dispatcher) 把 pCTR * pConversion 与 budget 合成 eligibility multiplier。**I pick** pacing-as-separate-layer over fold-into-ML-loss **because** pacing 秒-分钟闭环, ML 日-周, 时间尺度不匹配——折进 loss 必 lag-driven oscillation。senior trap: 折进 ML 看似"端到端"实则系统性振荡。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: 开口立 "Ads 是 calibrated probability feeding auction" reframe; 4 twist body 兑现; 三 head 各 logloss; sliced isotonic 不 global Platt; IPS replay 摆 A/B 之前; eval 切 reliability diagram + win-rate + CPM + conversion delta, NOT raw **Area Under ROC Curve** (AUC, ROC 曲线下面积); wrap 3 risk + ML/pacing 边界。

{WORST_ANCHOR_MARKER} 不及格锚: 通用 ranker 上 pairwise NDCG; pConversion same-day cutoff 不 bias-correct; 全局 Platt; A/B 直接上不做 IPS; pacing/budget 揉进 loss; eval 只看 AUC——没认出这是 auction-feeding probability 题。

## 8 段顺序 (一句导航 cue; 真讲连续说不报标题)

1. Framing — reframe Ads 为 calibrated probability feeding auction (Twist 1); 边界 (~3B users / p99 80-120ms / 1-7d); logloss 非 pairwise; 4 twist declarative。
2. Data & Label — 三 label {{y_click, y_conversion (delayed), y_quality}}; delayed-feedback windowed + per-objective bias correction (Twist 2)。
3. Retrieval-as-Feature-Store — 上游 targeting + brand-safety + frequency-cap 已 filter; per-(u, advertiser) eligibility cache + 冻结 visual+text tower creative embedding。
4. Multi-task Ranking — MMoE backbone + 三 head 各 logloss; 融合 score 由 auction 数学决定 NOT 学到 weighted sum; pacing/budget 不进 loss (Twist 4)。
5. Calibration — per-(vertical x objective x surface) sliced isotonic ~50-200 calibrator + drift gate; global Platt mis-price 小广告主长尾。
6. Counterfactual Eval — IPS replay BEFORE A/B (Twist 3); rolling propensity + replay window cap; A/B 作 sanity 不作 primary lift。
7. Boundary — ML/pacing (Twist 4): ML emit probability, pacing PID/LP 组合, frequency-cap 外挂, auction 做 second-price billing。
8. Wrap — 3 risk: (a) creative-tower retrain 后 per-cohort calibration drift (daily reliability + auto-recalibration); (b) attribution-window 1d→7d flip 致 bias 失配 (版本化 + per-version bias-correction); (c) IPS propensity stale (rolling propensity + replay cap)。

## 复用边界 (1-problem-1-URI)

auction-feeding probability + delayed-feedback windowed + IPS-before-A/B + ML/pacing 外挂 boundary 是 sd49 carve-up。其他 Meta sd-goldens ~50% 复用 backbone 但 auction + advertiser-re-bid 是 ads 独有——见 `cd://96` 与 `sd://meta-reels-golden` / `sd://meta-fb-newsfeed-golden` / `sd://meta-ig-story-golden` / `sd://meta-top3-comments-golden` / `sd://meta-friend-rec-golden` / `sd://meta-event-attendance-golden`, 不 bundle。
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
    if "sd://meta-ads-golden" not in body:
        errs.append("missing own sd://meta-ads-golden URI reference")

    # R-DRAWER-no-sd-drawer: no cd96 drawer table inside an sd-golden body.
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
            f"ERROR: no system_designs row for slug={SLUG}. The sd49 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd49 row)."
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
    """Post-write DB-side validation against the golden-template contract.

    sd49 is the oral_narrative archetype: this uses the sd41-style scope
    guard (assert architecture / production_constraints / tradeoffs /
    defense remain NULL after the write).
    """
    errs: list[str] = []

    cur.execute(
        "SELECT id, verbal_outline, architecture, production_constraints, "
        "tradeoffs, defense FROM system_designs WHERE slug = ?",
        (SLUG,),
    )
    rows = cur.fetchall()
    if len(rows) != 1:
        return [
            f"AC FAIL: expected exactly 1 row for slug={SLUG}, got {len(rows)}"
        ]

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

    # Scope guard (sd41-style): the 4 oral_narrative legal-NULL columns must
    # remain NULL after this seed runs. This catches accidental writes that
    # would silently violate "ONLY touch verbal_outline".
    for col, val in (
        ("architecture", architecture),
        ("production_constraints", prod_cons),
        ("tradeoffs", tradeoffs),
        ("defense", defense),
    ):
        if val:
            errs.append(
                f"AC FAIL: scope violation -- {col} unexpectedly non-empty "
                f"(this seed must touch ONLY verbal_outline; sd49 is "
                f"oral_narrative archetype)"
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

    print("\n[DONE] sd49 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
