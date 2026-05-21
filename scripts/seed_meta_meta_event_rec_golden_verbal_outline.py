"""Seed: T-P0-902 [Meta-MLSD] sd51 meta-event-rec-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for ``slug='meta-event-rec-golden'``
(sd51) with a Chinese-narration + English-terms speaking skeleton distilled
from sd51's existing English-only verbal_outline (~8.6KB).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45, sd46, sd47, sd48, sd49, sd50 mirrors. The machine-checkable
contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD51_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **Dual Cold-start ⇒ CF Non-viable** twist, sd51's signature framing:
    per-user RSVP ~3/year + events churn ~30%/week, matrix is ~empty AND
    half the columns re-cold-start continuously, so Matrix Factorization
    cannot extract factors. Skipping this is the failure mode that pulls
    Event Rec back into a generic user-item CF answer; almost every other
    sd51 decision derives from this fork (content-based primary, aspect-tag
    graph, friend-going as personalization carrier, new-event ramp).
  - 3-5 ``[floating-twist]`` markers (4 used: Dual-Cold-start-CF-Non-viable /
    Geo-Time-Capacity-Hard-Filters / Friend-going-IPS-correction /
    Capacity-Asymmetric-Quality-gated-Ramp)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI: own URI ``sd://meta-event-rec-golden``; sibling goldens
    referenced via the ``cd://96`` hub at the end (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd51 is the ``oral_narrative`` archetype: architecture /
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

  Because sd51 is oral_narrative (matching sd41/sd43/sd44/sd45/sd46/sd47/
  sd48/sd49/sd50), this seed uses the sd41-style scope guard (assert
  architecture / production_constraints / tradeoffs / defense remain NULL
  after the write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references its own ``sd://meta-event-rec-golden``
URI in twist/anchor/section text. Sibling goldens appear only at the end
"复用边界" section as "via ``cd://96``" pointers, mirroring the sd49/sd50
pattern. They are not bundled into the body of the problem.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed;
a verbal-only seed recomputing it would couple two seeds. The task contract
is "ONLY touch verbal_outline; other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd51 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_event_rec_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-event-rec-golden"
SENTINEL = "<!-- SD51_VERBAL_V1_20260515 -->"

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
# Meta Event Recommendation — Verbal Outline (45min 口播骨架)

> sd51 口播骨架。方法论 `cd://96`。1-problem-1-URI: `sd://meta-event-rec-golden`, 不 bundle。FB Event Rec 是 **dual cold-start** (**Répondez S'il Vous Plaît** (RSVP, 回复确认) ~3/年 + events ~30%/周 churn), **Collaborative Filtering** (CF, 协同过滤) 不可行——主杆 content + **Large Language Model** (LLM, 大语言模型) aspect-tag 图谱, 不是 **Matrix Factorization** (MF, 矩阵分解)。

## 0 · 一句话主干

输出 per-surface attended-RSVP slate。漏斗——hard-filter (geo/time/capacity) → content-based **Approximate Nearest Neighbor** (ANN, 近似最近邻) over (metadata + LLM aspect-tag), HNSW + geo-keyed **H3** cell shard ∥ friend-going aggregator → **Gradient-Boosted Decision Tree** (GBDT, 梯度提升决策树) with **Inverse Propensity Score** (IPS, 反向倾向分数) friend-going weight → capacity post-multiplier + new-event quality-gated burst → IPS replay → social-cluster A/B。scale: ~3B users, ~10M events, p99 ~120ms feed / ~500ms push。

## Floating Twists — 调度图 (4 个, 1 个压舱石)

> twist "漂"在整场: framing 立, body 兑现。

### Twist 1 · Dual Cold-start ⇒ CF Non-viable  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石。RSVP ~3/年 → row 密度 ~0; events ~30%/周 churn → 半 column 持续 cold-start——MF 双向抽不出 factor。**I pick** content ANN + LLM aspect-tag 图谱 over user-item CF/MF **because** content embedding 跨 churn 可迁移; **switches to** CF 仅 RSVP >50/年 (不成立)。整场兑现 4 次: framing / candidate-gen / cold-start / wrap "why-not-CF"。

### Twist 2 · Geo + Time + Capacity Are HARD Filters  {FLOATING_TWIST_MARKER}

不当 soft feature。loss 会把 "30mi + 高 affinity" 学成 "2mi + 中 affinity" 替代品——substitution 物理不成立。**I pick** hard-filter-then-score over soft fold-in **because** soft fold 学不可行 substitution, 输出违物理 slate; **costs**: pool 早裁, aspect-tag 补漏; **switches to** boundary soft (radius 0.95-1.0) 仅平滑。

### Twist 3 · Friend-going Strongest AND Selection-biased  {FLOATING_TWIST_MARKER}

稀疏下唯一可用 personalization, 但 selection-biased: 朋友只 RSVP 系统已展示的 event。raw friend-going 放大 already-favored——positive-feedback loop 挤 novel。**I pick** IPS-weighted (1/p(friend exposed)) over raw **because** raw 是反馈环路, IPS 破环; **costs**: per-friend exposure log + 周 propensity refit + per-event-type clip; eval 必 **social-cluster** A/B (per-user 跨 user 泄露)。

### Twist 4 · Capacity Asymmetric + Quality-gated Burst  {FLOATING_TWIST_MARKER}

>=100% 硬 drop (Twist 2); >=85% 软 downrank post-prediction `1 - sigmoid(α·(fill-0.85))`。**I pick** post-prediction multiplicative over capacity-as-feature **because** 折进 model couple policy 与 retraining, 产品无法独立 A/B; **costs**: per-surface α + staleness monitor。新 event <24h: **quality-gated burst** bootstrap friend-going, 门控 host-strength + aspect-tag confidence (避 spam)。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: 开口立 "RSVP ~3/年 + events ~30%/周 churn = dual cold-start, CF non-viable" reframe; 4 twist 兑现; label **attended-RSVP** (RSVP × attendance) 不 flat click; geo/time/capacity 硬切; IPS-weighted friend-going + 周 propensity refit; capacity post-multiplier 不进 loss; cold-start ramp gate host-strength + aspect-tag; IPS replay 摆 A/B 前; **social-cluster** A/B; wrap 3 risk。

{WORST_ANCHOR_MARKER} 不及格锚: MF 当主杆; flat click 当 label 学 clickbait; geo/time/capacity 当 soft feature; raw friend-going 不 IPS 致 positive-feedback; capacity 折进 loss; cold-start spam; per-user A/B 让 friend-going 网络效应污染 control——没认出 dual cold-start + network-effect leak 两个结构。

## 8 段顺序 (一句导航 cue; 真讲连续说不报标题)

1. Framing — dual cold-start + CF non-viable + content/aspect-tag 主杆 (Twist 1); ~3B users / ~10M events / p99 120ms。
2. Data & Label — click=noise, RSVP=intent (~30% no-show), attend=ground-truth; primary **attended-RSVP**; push 单走 RSVP-only。
3. Candidate Gen — geo/time/capacity 硬切 (Twist 2); content ANN 冻结 encoder + HNSW + H3 shard; friend-going aggregator (>=2 友) 并行。
4. Ranking — GBDT over O(100) feature (content cosine / aspect-tag / host-strength / IPS friend-going / 社交距离); IPS-weighted (Twist 3); 周 refit + per-event-type clip; cohort prior fallback。
5. Capacity & Cold-start — post-multiplier (Twist 4) 不进 loss; 新 event quality-gated burst gate host-strength + aspect-tag; user <30d 走 category prior backoff。
6. Eval — per-surface (attended-RSVP feed / RSVP@send-budget push / diversity events-tab), dual-cold-start cohort 切; IPS replay 摆 A/B 前; **social-cluster** A/B。
7. Boundary — content primary 不 CF; capacity 不进 loss; aspect-tag + host-strength 当 spam gate; integrity 单列。
8. Wrap — 3 risk: (a) IPS clip drift (周 refit + drift 检测); (b) cold-start ramp 撞 spam (manual review for new-host × new-event); (c) capacity counter lag (freshness SLO + pessimistic-fill)。

## 复用边界 (1-problem-1-URI)

dual cold-start + 硬切 + IPS friend-going + capacity post-multiplier + social-cluster A/B 是 sd51 (`sd://meta-event-rec-golden`) carve-up。其他 sd-goldens 共用 ~50% backbone, 但 dual cold-start + 物理硬切 + 网络效应 cluster A/B 是 event-rec 独有——见 `cd://96` 与 `sd://meta-reels-golden` / `sd://meta-fb-newsfeed-golden` / `sd://meta-event-attendance-golden` / `sd://meta-friend-rec-golden` / `sd://meta-ads-golden`, 不 bundle。
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
    if "sd://meta-event-rec-golden" not in body:
        errs.append("missing own sd://meta-event-rec-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd51 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd51 row)."
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

    sd51 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd51 is "
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

    print("\n[DONE] sd51 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
