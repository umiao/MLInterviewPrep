"""Seed: T-P0-897 [Meta-MLSD] sd46 meta-yelp-restaurant-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for
``slug='meta-yelp-restaurant-golden'`` (sd46) with a Chinese-narration +
English-terms speaking skeleton distilled from sd46's existing English-only
verbal_outline (~7KB) + overview block.

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45 mirrors. The machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD46_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **Review-text aspect matching beats rating-CF** twist, sd46's signature
    framing (two 4-star restaurants are not equivalent; the lift comes from
    LLM-extracted aspect graphs matched to a user's self-referential
    aspect-preference profile, NOT from collaborative-filtering refinement
    on star ratings)
  - 3-5 ``[floating-twist]`` markers (4 used: Aspect Graph from Review Text /
    Self-referential User Profile / Photo+Visit Recency Freshness Multiplier /
    Hard Eligibility geo+open-now is NOT a Soft Feature)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI no-bundle: own URI ``sd://meta-yelp-restaurant-golden``;
    sibling goldens referenced via ``sd://<slug>`` (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

YELP-vs-META CAVEAT (preserved from overview): Yelp is *not* a Meta product;
structural twists (aspect taxonomy, self-referential profile, freshness
override, hard eligibility) transfer cleanly, but Meta-specific signal
hierarchies (MSI, engagement-vs-meaningful) do NOT apply here. This sd
deliberately lives in the Meta-MLSD batch as a contrast case demonstrating
that the twist-threaded framework generalizes beyond Meta's MSI objective.

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd46 is the ``oral_narrative`` archetype: architecture /
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

  Because sd46 is oral_narrative (matching sd41/sd43/sd44/sd45), this seed
  uses the sd41-style scope guard (assert architecture /
  production_constraints / tradeoffs / defense remain NULL after the write),
  NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references ONLY its own
``sd://meta-yelp-restaurant-golden`` URI. Sibling goldens are reached via
the ``cd://96`` hub or named individually via ``sd://<slug>``, NEVER bundled
into this row.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed;
a verbal-only seed recomputing it would couple two seeds. The task contract
is "ONLY touch verbal_outline; other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd46 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_yelp_restaurant_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-yelp-restaurant-golden"
SENTINEL = "<!-- SD46_VERBAL_V1_20260515 -->"

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
# Yelp Restaurant Recommendation — Verbal Outline (45min 口播骨架)

> sd46 (Yelp Restaurant Rec) 口播骨架。方法论在 `cd://96`。1-problem-1-URI: `sd://meta-yelp-restaurant-golden`, 不 bundle sibling。注: Yelp **不是** Meta 产品, 结构 twist 通用, 但 Meta 的 **Meaningful Social Interaction** (MSI, 有意义社交互动) 目标层级在本题不适用。

## 0 · 一句话主干

Yelp 餐厅推荐: 给定 (user, geo, time, optional query), 从 ~10M 餐厅按"转化质量匹配"返回 ~10-25 listing。漏斗——**hard geo + open-now eligibility** → aspect-overlap retrieval (50 维稀疏 cosine) → multi-task ranker (visit / post-visit-positive / dwell) 融合 + freshness multiplier → page rerank。objective 押 **post-visit positive** (回访 + 正向 review back + dwell > 30s), **不是** listing click。scale: ~30M **Monthly Active Users** (MAU, 月活用户), ~10M 餐厅, 200ms p99, 地理预过滤后 hundreds 候选。

## Floating Twists — 调度图 (4 个, 1 个压舱石)

> twist 不绑漏斗某层, "漂"在整场: framing 立, body 兑现。主动调度。

### Twist 1 · Aspect Graph from Review Text (not rating-CF)  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石。两家 4-star 餐厅可以完全不同体验 (vibe / dietary / group-size / occasion 正交), 通用 rating-**Collaborative Filtering** (CF, 协同过滤) 有硬天花板, lift 来自 **Large Language Model** (LLM, 大语言模型) 抽 aspect-graph 做 aspect 级匹配。落地: 每餐厅 ~50 维稀疏 aspect 向量 (cuisine / dietary / ambience / service / price / group-size / occasion), LLM teacher 蒸馏 student 离线周更, > 20 条新 review 触发即时再抽。**I pick** aspect-taxonomy bridge over user-embedding **because** taxonomy 让 retrieval / ranking 共享可解释空间; **costs** 季度 refresh + 新 aspect 漂移监控。整场兑现 3 次——data/label / retrieval / eval。

### Twist 2 · Self-referential User Profile (from own review writing)  {FLOATING_TWIST_MARKER}

user aspect-weight 来自 **用户自己写的 review**, 不来自 explicit 设置 / click——写过 3 次 "loved the quiet patio" 就有 `quiet` `outdoor` 偏好。**I pick** self-ref over click-embedding **because** click 噪声大 + 被 ranking 反向偏置; **costs** 低写评用户 profile 欠定 (Bias 段处理)。与 Twist 1 共享 aspect taxonomy 双侧桥接。

### Twist 3 · Photo + Visit-recency Freshness Multiplier  {FLOATING_TWIST_MARKER}

餐厅会漂移 (服务塌房 / 小店变 loud), 3 年前 review 过时。处理: 近期照片 + visit dwell-time 作 **乘性** freshness multiplier——`final = aspect_prior(s) * freshness_mult`。**I pick** 乘性 over feature **because** drift 对静态 prior 是乘性叠加。对抗面: photo-bomb 刷新 — authority weighting (verified-visit > unverified) 配套。

### Twist 4 · Hard Eligibility (geo + open-now) is NOT a Soft Feature  {FLOATING_TWIST_MARKER}

geo 距离 + 营业状态是 candidate-gen **hard filter**, 不是 ranker soft feature。closed restaurant 完美 aspect-match 得分 = 0。折进 scoring 是 generic-ranker category error, 必须主动纠。geo 半径按 query intent 自适应 (~1mi casual / ~10mi special-occasion)。与 Twist 3 互补 (open-now = current, freshness mult = historical)。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: framing 把 4 twist 立起 body 兑现; rating-CF 有硬天花板 lift 在 LLM aspect-graph + 共享 taxonomy; profile 从用户自己 review 抽 (self-ref); freshness 是乘性 multiplier 认 photo-bomb + authority weighting; eligibility 是 hard filter 纠 "塞 ranker soft loss" category error; eval 3 surface (sliced / **Inverse Propensity Score** (IPS, 反向倾向分数) counterfactual replay / A/B 用 post-visit-positive lift); wrap 3 risk + alarm。

{WORST_ANCHOR_MARKER} 不及格锚: 当普通 rating-CF 题, lift 押 rating 微调; profile 从 click 拉 embedding 没认 self-ref; freshness 塞 ranker 当 feature; eligibility 塞 ranker 当 soft loss; A/B 用 click lift; 不提 taxonomy refresh / cohort fallback / photo authority——本质没认出 aspect 题。

## 8 段顺序 (一句导航 cue; 真讲连续说不报标题)

1. Framing — 边界 (~30M MAU / ~10M 餐厅 / 200ms p99 **Service Level Objective** (SLO, 服务水平目标)) + post-visit-positive > click + 4 twist declarative + Yelp ≠ Meta (MSI 不适用)。
2. Data & Label — 双侧 aspect mining: 餐厅侧 LLM teacher 蒸馏 student weekly (Twist 1); 用户侧 self-ref profile (Twist 2); label = visit + post-visit-positive, 不是 listing click。
3. Retrieval — hard geo + open-now (Twist 4) → 50 维 sparse cosine aspect overlap 拉 hundreds (Twist 1); 新餐厅冷启靠初评 aspect + business attribute。
4. Ranking — multi-task {{p_visit, p_positive_postvisit, p_dwell_listing}} 融合对齐 post-visit-positive; aspect-match 作强连续 feature; recent photo + visit-recency 作 freshness multiplier 在 aspect_prior 上 (Twist 3)。
5. Bias — Twist 2 副作用: 写多者 bias 偏陈述偏好, 安静用户欠定; 低 review-count 走 cohort prior + 平滑 blending; 别假装信号薄时 profile 是 fully personalized。
6. Eval — sliced by aspect-axis × review-count-bucket; IPS counterfactual replay 修长尾曝光偏; A/B = post-visit-positive lift, 不是 click lift。
7. Drift Recovery — 被引向 rating-CF / two-tower / rating-as-feature 时, 三段回扣线拉回 aspect graph + self-ref profile 主轴。
8. Wrap — 3 risk (aspect taxonomy 陈旧需季度 LLM 再抽 / 低 review-count cohort 过渡颠簸需平滑 + 稳定度 metric / photo-freshness 对抗需 verified-visit authority)。

## 复用边界 (1-problem-1-URI)

LLM aspect graph + self-ref user profile + 乘性 freshness multiplier + hard geo/open-now 是本题 carve-up。Reels / FB News Feed / Top-3 Comments / Friend Rec / Ads 结构 ~70% 复用但 twist 调度图不同 (本题压舱石 aspect-text-matching), 各自独立 URI——见 `cd://96` hub 与 `sd://meta-reels-golden` / `sd://meta-fb-newsfeed-golden` / `sd://meta-top3-comments-golden` / `sd://meta-friend-rec-golden` / `sd://meta-weapon-ads-golden`, 不在此 row 内 bundle。
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
    if "sd://meta-yelp-restaurant-golden" not in body:
        errs.append("missing own sd://meta-yelp-restaurant-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd46 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd46 row)."
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

    sd46 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd46 is "
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

    print("\n[DONE] sd46 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
