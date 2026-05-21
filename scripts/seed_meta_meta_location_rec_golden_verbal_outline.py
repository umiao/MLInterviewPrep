"""Seed: T-P0-903 [Meta-MLSD] sd52 meta-location-rec-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for ``slug='meta-location-rec-golden'``
(sd52) with a Chinese-narration + English-terms speaking skeleton distilled
from sd52's existing English-only verbal_outline (~8.9KB).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45, sd46, sd47, sd48, sd49, sd50, sd51 mirrors. The
machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD52_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **Context As Primary Intent Disambiguator** twist, sd52's signature
    framing: same user at 9am vs 9pm has *different* intents; static long-
    horizon profile gives an average no one wants at any moment, so context
    (time / weather / calendar / mobility-mode) is the primary lever -- NOT
    a residual feature. Skipping this is the failure mode that pulls Location
    Rec back into a generic user-POI CF / static-profile answer; almost every
    other sd52 decision derives from this fork (context-conditioned ANN,
    intent classifier cascade, mode-keyed radius switch).
  - 3-5 ``[floating-twist]`` markers (4 used: Context-Primary-Disambiguator /
    Mode-Keyed-Radius-Hard-Switch / Classifier-Then-Ranker /
    Post-Ranker-MMR-Diversity)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI: own URI ``sd://meta-location-rec-golden``; sibling
    goldens referenced via the ``cd://96`` hub at the end (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd52 is the ``oral_narrative`` archetype: architecture /
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

  Because sd52 is oral_narrative (matching sd41/sd43/sd44/sd45/sd46/sd47/
  sd48/sd49/sd50/sd51), this seed uses the sd41-style scope guard (assert
  architecture / production_constraints / tradeoffs / defense remain NULL
  after the write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references its own ``sd://meta-location-rec-golden``
URI in twist/anchor/section text. Sibling goldens appear only at the end
"复用边界" section as "via ``cd://96``" pointers, mirroring the sd49/sd50/sd51
pattern. They are not bundled into the body of the problem.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed;
a verbal-only seed recomputing it would couple two seeds. The task contract
is "ONLY touch verbal_outline; other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd52 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_location_rec_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-location-rec-golden"
SENTINEL = "<!-- SD52_VERBAL_V1_20260515 -->"

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
# Meta Location Recommendation — Verbal Outline (45min 口播骨架)

> sd52 口播骨架。方法论 `cd://96`。1-problem-1-URI: `sd://meta-location-rec-golden`, 不 bundle。主特点: **context** (time/weather/calendar/mode) 是 primary intent disambiguator——同一用户 9am vs 9pm 意图不同。主杆 context-conditioned retrieval + intent classifier 级联, 不是 user-POI **Collaborative Filtering** (CF, 协同过滤)。

## 0 · 一句话主干

输出 per-surface visit-conditional-save slate。漏斗——mode 推断 + radius 硬切 (3mi walk / 30mi drive) → context-conditioned **Approximate Nearest Neighbor** (ANN, 近似最近邻) over (metadata + **Large Language Model** (LLM, 大语言模型) aspect-tag + photo emb), **Hierarchical Navigable Small World** (HNSW, 分层可导航小世界) + **H3** city-cell shard + per-cell intent partition → intent classifier → **Gradient-Boosted Decision Tree** (GBDT, 梯度提升决策树) per-intent cascade → **Maximal Marginal Relevance** (MMR, 最大边际相关) post-rank。scale: ~3B users, ~100M POIs, p99 ~80ms。

## Floating Twists (4 个, 1 个压舱石)

### Twist 1 · Context As Primary Intent Disambiguator  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

压舱石。同一用户 9am coffee / 9pm nightlife——static long-horizon profile 给的是两端平均, 任何 moment 都不是真实偏好。**I pick** context-conditioned retrieval + intent classifier over static-profile / 用户级 CF **because** intent momentary + user-POI 稀疏, context 比 user-POI factor 多承载信号; **switches to** static profile 仅 cold-start user (<30天) 走 per-city prior 兜底。整场兑现 4 次: framing / candidate-gen / classifier / wrap。

### Twist 2 · Walk-vs-Drive Radius Is HARD Switch  {FLOATING_TWIST_MARKER}

不当 soft distance feature——loss 会把 "30mi + 高 affinity" 学成 "2mi + 中 affinity" 替代品, 对 walker 物理不成立。**I pick** mode-keyed radius 硬切 (3mi walk / 30mi drive / 5mi unknown) over soft fold-in **because** soft fold 学不可行 substitution; **costs**: mode classifier 周 refit + ~1.5x "unknown" pool inflation; **switches to** soft distance 仅 池内 tiebreaker。

### Twist 3 · Classifier-Then-Ranker (Intent As Senior-signal Abstraction)  {FLOATING_TWIST_MARKER}

intent classification 是 intermediate task, 不折 end-to-end。小 **Mixture-of-Experts** (MoE, 混合专家) classifier over context → soft distribution 跨 ~6 intent class (food/coffee/activity/nightlife/errand/other) → GBDT per-intent 级联。**I pick** classifier-then-ranker over end-to-end deep **because** intent 是 senior-signal 抽象, 能独立 A/B classifier (drift dashboard 显形, end-to-end loss 埋掉); **costs**: per-session intent label + nightlife <5% imbalance。

### Twist 4 · Post-Ranker MMR Diversity (Not Loss-folded)  {FLOATING_TWIST_MARKER}

MMR 摆 ranker 之后: score = ranker - λ · max-sim-to-selected, sim 跨 (intent-class, POI-cat, emb-cosine); per-surface λ + per-intent quota。**I pick** post-ranker MMR over diversity-as-feature **because** 折 loss couple λ 与 ranker, 产品没法 per-surface 调 (nearby-tab 容 4 cafe; push 推 variety), 独立层 A/B 不动 model; 新 POI <14天 content-only + per-cell quality-gated burst (避 spam)。

## Anchor Calibration

{BEST_ANCHOR_MARKER} 满分锚: 开口立 "9am coffee vs 9pm nightlife → context primary disambiguator" reframe; 4 twist 兑现; label **visit-conditional-save** 不 flat click; walk/drive 硬切; classifier-then-ranker; MMR 后置不进 loss; eval 按 time × mode × intent-class 切; counterfactual replay 摆 A/B 前; city-cluster A/B; wrap 3 risk。

{WORST_ANCHOR_MARKER} 不及格锚: static long-horizon profile 当主杆; flat click 当 label 学 clickbait; distance 当 soft feature 让 30mi-walk 替 2mi; end-to-end deep 埋掉 classifier A/B; diversity 折进 loss; flat top-line 埋掉 intent-class collapse——没认出 context-primary + 物理硬切 + senior-signal classifier 三个结构。

## 8 段顺序 (一句导航 cue; 连续说)

1. Framing — context-primary (T1) + mode radius (T2) + classifier→ranker (T3); ~3B users / ~100M POIs / p99 80ms。
2. Data & Label — click=noise, save=intent (~40% no-visit), visit=ground-truth; 主 **visit-conditional-save**; search-suggest 单走 save-only。
3. Candidate Gen — mode classifier (15min lat/lon delta + time + weather) → radius 硬切 (T2); context ANN + HNSW + H3 city-cell shard + per-cell intent partition。
4. Classifier + Ranker — MoE classifier (T3) → 6 intent class → GBDT per-intent cascade; O(100) feature (context cos / aspect-tag / hours / price / weather / residual)。
5. Diversity & Cold-start — post-ranker MMR (T4) per-surface λ + per-intent quota; 新 POI content-only + quality-gated burst; new user 走 per-city prior。
6. Eval — 按 time × mode × intent-class 切; counterfactual replay 摆 A/B 前 (mask 上游 slate position); city-cluster A/B (无 friend-going leak)。
7. Boundary — context primary 不 static profile; CF 弱 (POI 稳 但 per-user visit 稀疏); distance 不进 loss; integrity 单列 gate。
8. Wrap — 3 risk: (a) context drift (remote-work 改 mid-day intent) — 月度 refit; (b) mode 误分类 cliff — smoothed boundary; (c) diversity 过校 — intent-confidence-gated λ。

## 复用边界 (1-problem-1-URI)

context-primary + 硬切 radius + classifier→ranker + 后置 MMR + per-cell intent partition 是 sd52 (`sd://meta-location-rec-golden`) carve-up。mode 硬切 + intent classifier 当 intermediate task 是 location-rec 独有——见 `cd://96` 与 `sd://meta-reels-golden` / `sd://meta-event-rec-golden` / `sd://meta-yelp-restaurant-golden`, 不 bundle。
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
    if "sd://meta-location-rec-golden" not in body:
        errs.append("missing own sd://meta-location-rec-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd52 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd52 row)."
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

    sd52 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd52 is "
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

    print("\n[DONE] sd52 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
