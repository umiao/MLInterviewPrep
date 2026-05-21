"""Seed: T-P0-896 [Meta-MLSD] sd45 meta-fb-newsfeed-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for
``slug='meta-fb-newsfeed-golden'`` (sd45) with a Chinese-narration +
English-terms speaking skeleton distilled from sd45's existing English-only
verbal_outline (~7KB) + overview block (which together hold the FB News Feed
45-min walkthrough material; sd45 has ``dataflow=NULL`` -- unlike the other
oral_narrative goldens, sd45 carries its content in ``verbal_outline`` /
``overview`` rather than ``dataflow``).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44 mirrors. The machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD45_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **MSI-as-label-hierarchy** twist, sd45's signature difficulty (MSI is
    Meta's stated product objective, NOT a feature-weight tweak on top of
    engagement -- it changes the label hierarchy and the task-head fusion
    weights at score time)
  - 3-5 ``[floating-twist]`` markers (4 used: MSI Label Hierarchy /
    Heterogeneous Multi-source Candidate Gen / Close-friend Recency Override
    / Integrity Multiplicative Downrank)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI no-bundle: own URI ``sd://meta-fb-newsfeed-golden``;
    sibling goldens referenced via ``sd://<slug>`` (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd45 is the ``oral_narrative`` archetype: architecture /
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

  Because sd45 is oral_narrative (matching sd41/sd43/sd44), this seed uses
  the sd41-style scope guard (assert architecture / production_constraints /
  tradeoffs / defense remain NULL after the write), NOT the sd42-style
  fingerprint guard.

1-PROBLEM-1-URI: the body references ONLY its own
``sd://meta-fb-newsfeed-golden`` URI. Sibling goldens are reached via the
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
(this seed does not create the sd45 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_fb_newsfeed_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-fb-newsfeed-golden"
SENTINEL = "<!-- SD45_VERBAL_V1_20260515 -->"

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
# FB News Feed — Verbal Outline (45min 口播骨架)

> sd45 (FB News Feed) 口播骨架。逐字稿在本题 `overview`; 方法论在 `cd://96`。1-problem-1-URI: `sd://meta-fb-newsfeed-golden`, 不 bundle sibling。

## 0 · 一句话主干

FB News Feed 个性化排序: 从亿级异构 corpus (friends / groups / pages) 返回有序 feed。漏斗——多路 retrieval (按 source 独立, one-hot 保留) → multi-task ranker (per-source heads 共享 backbone) → integrity 乘性下沉。objective **不是** engagement 而是 **Meaningful Social Interaction** (MSI, 有意义社交互动): 密友 `comment` 权重 >> 陌生人 `like`——是 label hierarchy 不是 feature 权重微调。scale: ~3B **Daily Active Users** (DAU, 日活用户), 单次请求 ~10k 候选, ranker p99 ~80ms + CG ~30ms。input = (user, context, candidate item), corpus 不是 input。

## Floating Twists — 调度图 (4 个, 1 个压舱石)

> twist 不绑漏斗某层, "漂"在整场: framing declarative 立, body 每个 component 兑现一次。主动调度, 别等挖。

### Twist 1 · MSI Label Hierarchy (not Engagement)  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石。通用 news-feed 押 click / dwell, Meta 目标是 MSI——不是叠权重, 是 **label hierarchy 改了**: 训练正向按 MSI 加权采样, 打分 multi-task head 融合权重 `w_k(source)` learned 不手设 (offline counterfactual replay 对 MSI delta 优化)。**I pick** learned 权重 over 硬编码表, **because** 静态表随行为漂移; **costs** 月度 re-tune + close-friend-comment weight 跌 10% 告警。整场兑现 3 次——label / ranking / eval (8 周 holdout 抓 engagement 涨但 MSI 跌)。

### Twist 2 · Heterogeneous Multi-source Candidate Gen  {FLOATING_TWIST_MARKER}

friends / groups / pages 三路逻辑不同, MSI 语义也不同 (friend `share` ≠ page `share`)。落地: 三路并行 (friend 1-hop+2-hop strength decay; groups recency within active; pages engagement-recency), **source-of-origin one-hot 保留**作 ranker feature, 让 per-source recall 各自可调试。跨源不是统一 embedding cosine, 是 **per-source ceiling quota** (~60% friends / 25% groups / 15% pages), Thompson sampling 按 MSI delta 调。**Switches to** 统一双塔仅在 per-source 可调试性不再 critical 时。

### Twist 3 · Close-friend Recency Override  {FLOATING_TWIST_MARKER}

密友 / 家人纯 engagement history 太粗, 错过"妹妹刚发"是典型 failure。Meta 已 ship close-friends-tab 反向时序 bypass 算法。落两条: (a) dual-feed 路径 (close-friends-tab 关 ranker, 只跑 integrity); (b) 主 feed 加 **soft bypass head**——close-friend signal × item < 6h 给 boost。**I pick** soft over hard quota, **because** quota 在 close-friend list 空 / 偏斜时 brittle。与 Twist 1 correlated 协同 (close-friend 本就抬 MSI 权重)。

### Twist 4 · Integrity Multiplicative Downrank  {FLOATING_TWIST_MARKER}

misinfo / clickbait 不是 hard-remove——做 calibrated shared-scale **乘性**: `final = MSI(s) * (1 - p_integrity)^alpha`。结构和 Weapon Ads (`sd://meta-weapon-ads-golden`) cascade 同形, 但作 multiplier 不作 admission gate。**I pick** 乘性 over hard-cut, **because** integrity 分类器 calibrated, hard-cut 丢 calibration。主动说: 有时 MSI-positive 被压是 **正确的**——平台价值是 alignment 不是 engagement。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: framing 把 4 twist 立起 body 逐一兑现; label 是 MSI 加权多任务向量, 主动讲 label hierarchy 改写不是 feature-weight 微调; retrieval 讲 per-source quota Thompson sampling + source-of-origin one-hot; ranker 融合权重学不手设, close-friend bypass 是 soft 不 quota; integrity 是 multiplicative downrank 不是 admission gate, 主动纠正"MSI-positive 被压有时是对的"; eval 3 surface (sliced / **Inverse Propensity Score** (IPS, 反向倾向分数) counterfactual replay / 8 周 holdout); wrap 3 risk + alarm。

{WORST_ANCHOR_MARKER} 不及格锚: 当普通 **Click-Through Rate** (CTR, 点击率) 题押 click; MSI 当权重微调; 统一双塔丢 source-of-origin; integrity 塞 ranker head 当 soft loss (category error); A/B 用 impression 级 (feed 内 item 互相污染); long-term holdout 没提——本质没认出 MSI 题。

## 8 段顺序 (一句导航 cue; 真讲连续说不报标题)

1. Framing — 边界 (~3B DAU / ~10k 候选 / p99 80ms ranker + 30ms CG **Service Level Objective** (SLO, 服务水平目标)) + MSI > engagement + 4 twist declarative。
2. Data & Label — multi-task vector {{p_click, p_comment, p_like, p_share, p_dwell, p_reaction_type}} + MSI 融合 (Twist 1); 密友 `comment` ≈ 10-20× 弱关系 `like`; per-source 头从 backbone 末端 split。
3. Retrieval — 三路并行 (friend / group / page), source-of-origin one-hot (Twist 2); quota Thompson sampling against MSI delta; 冷启动 entity-overlap。
4. Ranking — per-source heads 共享 backbone; `MSI(s) = Σ_k w_k(source) * p_k`; offline counterfactual replay 对 MSI delta 优化。
5. Close-friend — close-friends-tab 反向时序 + integrity 乘性 (dual-feed); 主 feed soft bypass head × signal × age < 6h (Twist 3)。
6. Integrity — `(1 - p_integrity)^alpha` 乘性 (Twist 4); 与 Weapon Ads cascade 同形但作乘子不作 gate。
7. Evaluation — sliced by content_type × source × close-friend tier (不 flat **Area Under the Curve** (AUC, 曲线下面积)); IPS counterfactual replay before A/B; 8 周 long-term holdout; A/B user/session 级。
8. Wrap — 3 risk (MSI 权重 staleness / integrity prior collapse / close-friend bypass 对抗 → implicit 互动史 over declared list)。

## 复用边界 (1-problem-1-URI)

multi-source CG + MSI multi-task + integrity 乘性 + close-friend bypass 是本题 carve-up。Reels / Top-3 Comments / Friend Rec / Ads 结构 ~70% 复用但 twist 调度图不同 (本题压舱石 MSI label hierarchy, Reels 是 session dynamics, Top-3 Comments 是 selection bias), 各自独立 URI——见 `cd://96` hub 与 `sd://meta-reels-golden` / `sd://meta-top3-comments-golden` / `sd://meta-friend-rec-golden` / `sd://meta-weapon-ads-golden`, 不在此 row 内 bundle。
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
    if "sd://meta-fb-newsfeed-golden" not in body:
        errs.append("missing own sd://meta-fb-newsfeed-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd45 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd45 row)."
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

    sd45 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd45 is "
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

    print("\n[DONE] sd45 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
