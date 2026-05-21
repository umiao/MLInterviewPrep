"""Seed: T-P0-898 [Meta-MLSD] sd47 meta-ig-story-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for ``slug='meta-ig-story-golden'``
(sd47) with a Chinese-narration + English-terms speaking skeleton distilled
from sd47's existing English-only verbal_outline (~8.8KB).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45, sd46 mirrors. The machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD47_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **Author-tray is the unit of ranking** twist (NOT the story), sd47's
    signature framing: the unit of cross-tray ranking is the author-tray,
    and within-tray sequencing is a separate sub-ranking step. Per-story
    score-then-sort is solving the wrong granularity; almost every other
    sd47 design decision derives from this framing.
  - 3-5 ``[floating-twist]`` markers (4 used: Author-tray as Unit /
    Skip-to-next-author Implicit Negative / Within-tray Autoregressive
    Sequencing / Hard 24h+Follow-graph Eligibility + Relationship Prior as
    Multiplier)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI no-bundle: own URI ``sd://meta-ig-story-golden``;
    sibling goldens referenced via ``sd://<slug>`` (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd47 is the ``oral_narrative`` archetype: architecture /
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

  Because sd47 is oral_narrative (matching sd41/sd43/sd44/sd45/sd46), this
  seed uses the sd41-style scope guard (assert architecture /
  production_constraints / tradeoffs / defense remain NULL after the
  write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references ONLY its own
``sd://meta-ig-story-golden`` URI. Sibling goldens are reached via the
``cd://96`` hub or named individually via ``sd://<slug>``, NEVER bundled
into this row.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed;
a verbal-only seed recomputing it would couple two seeds. The task contract
is "ONLY touch verbal_outline; other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd47 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_ig_story_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-ig-story-golden"
SENTINEL = "<!-- SD47_VERBAL_V1_20260515 -->"

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
# IG Story Recommendation — Verbal Outline (45min 口播骨架)

> sd47 口播骨架。方法论在 `cd://96`。1-problem-1-URI: `sd://meta-ig-story-golden`, 不 bundle sibling。**Meaningful Social Interaction** (MSI, 有意义社交互动) 在 Story 具体化为 close-friend 交互 + next-day return。

## 0 · 一句话主干

IG Story: 给定 (user, context, time), follow-graph + 24h 内活跃 author-tray 中排序返 rail。漏斗——**hard 24h + follow-graph + close-friends eligibility** → per-author tray-rollup retrieval → cross-tray multi-task ranker (tray-positive / skip / close-friend dwell) + relationship-prior **乘性**叠加 → within-tray autoregressive 序列模型定 tray 内顺序。objective 押 **tray-positive + next-day return**, 不是 rail dwell。scale: ~500M **Daily Active Users** (DAU, 日活用户) on Stories, 24h gate 后 ~300-1000 候选 story, p99 ~80ms+40ms。

## Floating Twists — 调度图 (4 个, 1 个压舱石)

> twist 不绑漏斗某层, "漂"在整场: framing 立, body 兑现。主动调度。

### Twist 1 · Author-tray IS the Unit of Ranking (not the story)  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石。Story 消费单位是 **author-tray** (作者当日 N 条 story 打包), 用户 tray-by-tray 翻, 不跨作者挑单 story。把 cross-tray ranking 与 within-tray sequencing 分两阶段——前排作者, 后排作者内 story。per-story score-then-sort 是 generic-feed category error, 解错粒度。落地: tray-rollup 把 N 条 story 压成 entity 携 `story_count` / `latest_post_ts` / `mean_content_type`; per-story dwell 留 Twist 3。**I pick** author-tray over two-tower **because** 后者 flatten per-author story-count / recency 分布。整场兑现 3 次——retrieval / cross-tray / within-tray。

### Twist 2 · Skip-to-Next-Author = Dominant Implicit Negative  {FLOATING_TWIST_MARKER}

进 tray 1.5s 内 skip-to-next-author 是 misordered-tray 信号——干净、强、tray-粒度独有。**只在 Twist 1 把 tray 当 unit 时存在**, 落 per-story ranker 坍塌成噪声。auto-play 下 story-level click 无意义。**costs**: tray-aggregation + per-cohort 校 1.5s 阈值。

### Twist 3 · Within-tray Autoregressive Sequencing (NOT chronological)  {FLOATING_TWIST_MARKER}

cross-tray ranker 决哪个 author 上 rail, **per-author autoregressive 序列模型** 决 tray 内顺序——倒序时间 baseline, 模型有 lift 时覆盖。big-event-first (婚礼 / 出游) 经常 beat reverse-chronological。模型: 轻 **Gated Recurrent Unit** (GRU, 门控循环单元) 或 2 层 **Transformer**, 输入 cover-embedding + post-time + content-type + user-author 历史 dwell; label = within-tray dwell-completion。**costs**: ~40ms inference; switches to 倒序仅当 lift < 2%。

### Twist 4 · Hard Eligibility (24h+Follow-graph) + Relationship Prior as Multiplier  {FLOATING_TWIST_MARKER}

两层 hard filter 不当 feature: (a) 24h 过期是 **eligibility, 不是新鲜度 feature** (cd94 anti-pattern); (b) follow-graph + close-friends 硬入口, follow-adjacent quota-cap ~10% rail。close-friend relationship-prior **乘性 multiplier 不当 feature** (`S_final = S_fused * relationship_prior`)——效应结构上乘性 (close-friend 即便预测低也应排在 stranger 同分之上)。冷启动靠 author-level 关系 prior。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: framing 立 4 twist body 兑现; author-tray 作 unit 纠 per-story category error; 1.5s-skip 是 tray-粒度独有负样本; within-tray **Autoregressive** (AR, 自回归) 序列在 cross-tray 之后; 24h + follow-graph 是 hard eligibility; relationship prior 乘性 multiplier; eval 3 surface (sliced by relationship-tier × time-of-day × tray-length / **Inverse Propensity Score** (IPS, 反向倾向分数) counterfactual replay / A/B 用 tray-positive + next-day return); wrap 3 risk + alarm。

{WORST_ANCHOR_MARKER} 不及格锚: 当 per-story 题 (解错粒度); 24h 过期塞 ranker 当 freshness; close-friend 关系当 feature 不当 multiplier; within-tray 默认倒序不引序列; A/B 用 rail-dwell (易被 dramatic stranger 刷高); 不提 skip 长 tray bias / close-friend monopolization / 序列 over-fit。

## 8 段顺序 (一句导航 cue; 真讲连续说不报标题)

1. Framing — 边界 (~500M Story DAU / 80ms+40ms p99 **Service Level Objective** (SLO, 服务水平目标)) + tray-positive + next-day return > rail dwell + 4 twist declarative。
2. Data & Label — tray-positive = full-tray-watched 或 mean(dwell/length) > 0.6; 1.5s-skip dominant negative (Twist 2)。
3. Retrieval — hard 24h + follow-graph + close-friends eligibility (Twist 4); per-author tray-rollup (Twist 1)。
4. Cross-tray Ranking — multi-task {{p_tray_positive, p_skip, p_close_friend_dwell}}, `S_tray = w1*p_pos - w2*p_skip + w3*p_cf_dwell`; relationship 乘性叠加 (Twist 4)。
5. Within-tray Sequencing — per-author AR 序列 (Twist 3): cover-embedding + post-time + content-type + 历史 dwell → tray 内顺序。
6. Bias / Cold-start — tray-粒度 IPS replay 修长尾曝光; 新作者走 follow-adjacent cohort prior + 平滑 blending。
7. Eval — sliced by relationship-tier × time-of-day × tray-length (flat AUC 会被 multiplier 吃掉); IPS replay; A/B = tray-positive + next-day return。
8. Wrap — 3 risk (close-friend prior monopolize 需 per-cohort cap + ~10% diversity floor / 1.5s skip 与 tray-length 相关需 normalize / 序列 over-fit 高活作者)。

## 复用边界 (1-problem-1-URI)

author-tray 作 unit + 1.5s skip + within-tray AR + 24h hard eligibility + relationship multiplier 是本题 carve-up。Reels / FB News Feed / Top-3 Comments / Friend Rec / Ads 结构 ~70% 复用但 twist 调度图不同 (本题压舱石 tray-粒度 vs Reels session-粒度), 各自独立 URI——见 `cd://96` hub 与 `sd://meta-reels-golden` / `sd://meta-fb-newsfeed-golden` / `sd://meta-top3-comments-golden` / `sd://meta-friend-rec-golden` / `sd://meta-weapon-ads-golden`, 不 bundle。
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
    if "sd://meta-ig-story-golden" not in body:
        errs.append("missing own sd://meta-ig-story-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd47 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd47 row)."
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

    sd47 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd47 is "
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

    print("\n[DONE] sd47 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
