"""Seed: T-P0-901 [Meta-MLSD] sd50 meta-v2v-search-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for ``slug='meta-v2v-search-golden'``
(sd50) with a Chinese-narration + English-terms speaking skeleton distilled
from sd50's existing English-only verbal_outline (~8.4KB).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45, sd46, sd47, sd48, sd49 mirrors. The machine-checkable
contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD50_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **"Similar" is undefined without text query** twist, sd50's signature
    framing: V2V has no text query, so visual / audio / intent pull in
    different directions, the dominant axis is per-session and unobservable
    at query time. Skipping this is the failure-mode that flattens V2V to a
    single fused-cosine retrieval and collapses multi-facet back to one
    axis; almost every other sd50 decision derives from this fork.
  - 3-5 ``[floating-twist]`` markers (4 used: Similar-Is-Undefined-Multi-Facet /
    L2-Normalize-Before-Fusion / Session-Time-Thompson-Facet-Weights /
    Content-Only-Single-Stage-Cold-Start)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI: own URI ``sd://meta-v2v-search-golden``; sibling goldens
    referenced via the ``cd://96`` hub at the end (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd50 is the ``oral_narrative`` archetype: architecture /
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

  Because sd50 is oral_narrative (matching sd41/sd43/sd44/sd45/sd46/sd47/
  sd48/sd49), this seed uses the sd41-style scope guard (assert architecture
  / production_constraints / tradeoffs / defense remain NULL after the
  write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references its own ``sd://meta-v2v-search-golden``
URI in twist/anchor/section text. Sibling goldens appear only at the end
"复用边界" section as "via ``cd://96``" pointers, mirroring the sd49 pattern.
They are not bundled into the body of the problem.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed;
a verbal-only seed recomputing it would couple two seeds. The task contract
is "ONLY touch verbal_outline; other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd50 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_v2v_search_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-v2v-search-golden"
SENTINEL = "<!-- SD50_VERBAL_V1_20260515 -->"

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
# Meta Video-to-Video Search — Verbal Outline (45min 口播骨架)

> sd50 口播骨架。方法论 `cd://96`。1-problem-1-URI: `sd://meta-v2v-search-golden`, 不 bundle。V2V 没 text query, "similar" 未定义; 三轴 (visual / audio / intent) per-session 各拉一边——所以是 **multi-facet retrieval** 配 session-time facet 权重, 不是单 fused-cosine。

## 0 · 一句话主干

V2V: query 即视频, 输出 facet-conditional ~10k-50k slate。漏斗——三路 per-modality encoder (visual transformer / audio log-mel / OCR 冻结 text encoder) 各自 **L2-normalize** (二范数归一化) → 每 facet 一个 **Approximate Nearest Neighbor** (ANN, 近似最近邻) HNSW 索引 (M=32, ef=200), 各 ~5k-15k → per-facet quota merge, quota 由 session-time **Thompson Sampling** (汤普森采样) over **Beta posterior** (Beta 后验) per-facet in-session **Click-Through Rate** (CTR, 点击率) 给 → 轻量 **Gradient-Boosted Decision Tree** (GBDT, 梯度提升决策树) reranker facet 内排 → **Inverse Propensity Score** (IPS, 反向倾向分数) replay → session-level cluster-randomized A/B。scale: ~B-scale corpus, p99 ~50-80ms, 无 user 侧 tower。

## Floating Twists — 调度图 (4 个, 1 个压舱石)

> twist 不绑某层, "漂"在整场: framing 立, body 兑现。

### Twist 1 · "Similar" Is Undefined Without Text Query  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石。没 text query, "similar" 未定义——三轴 (visual/audio/intent) 各拉一边, dominant 轴 per-session 且 query 时不可观测。**I pick** multi-facet retrieval + session-time facet 权重 over 单 fused-embedding cosine **because** 单 fused 把不同向轴拍平, axis 错就 retrieve 错; **switches to** single-cosine 仅 corpus 单 modality 主导 (不成立)。整场兑现 4 次: framing / encoder / slate-merge / eval 切 facet-conditional **Normalized Discounted Cumulative Gain** (NDCG, 归一化折损累积增益) 不 flat **Area Under ROC Curve** (AUC, ROC 曲线下面积)。

### Twist 2 · L2-Normalize-Before-Fusion  {FLOATING_TWIST_MARKER}

每 modality embedding 必在 fusion / slate-merge 前 L2-normalize。audio raw-norm 偏高, 不 pre-normalize 会在 merge 时 silently 主导, 把 multi-facet 塌回单轴。**I pick** pre-fusion L2-normalize over post-fusion **because** post-fusion normalize 的是已被主导的向量, 信号丢了 normalize 不回来; **costs**: per-modality norm-monitor + 中位数 norm 漂 >20% 报警 + encoder retrain 后 re-anchor。

### Twist 3 · Session-Time Thompson-Sampled Facet Weights  {FLOATING_TWIST_MARKER}

dominant facet 是 **per-session** 不是 per-user。每 facet 一 Beta posterior 跟 in-session CTR, 每 query Thompson sample 三值 normalize 到 simplex 就是下条 query slate quota; session 结束 reset, 2-3 query 内 dominant 浮出。**I pick** session-scoped Thompson + Beta over per-user batch-trained 权重 **because** per-user 解不了 within-session axis-shift; **costs**: per-session 3 Beta + reset + query 1 uniform prior 冷启偏置。

### Twist 4 · Content-Only Single-Stage + Cold-Start  {FLOATING_TWIST_MARKER}

query 即视频, 无 user 侧 embedding 可 dot-product——V2V 是 single-stage content-only, 无 two-tower。Bolt on user tower 砸 content-only cold-start (新上传 <24h 靠 content-only embedding 直接进 facet ANN)。**I pick** single-stage content-only over two-tower **because** 个性化已被 Twist 3 facet 权重吸收, 它正解 within-session axis-shift; cold-start eval 用 <24h held-out slice 看 retrieval slot share。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: 开口立 "'similar' 没 text query 未定义, 三轴 per-session" reframe; 4 twist body 兑现; pre-fusion L2-normalize 不 post-fusion; session-time Thompson + Beta over per-user; eval 切 per-facet recall@K + facet-conditional NDCG + IPS replay before A/B + **session-level cluster-randomized** A/B (per-user 会跨 session 泄漏 facet 权重 policy); wrap 3 risk。

{WORST_ANCHOR_MARKER} 不及格锚: 单 fused-cosine; 不 pre-normalize 让 audio 主导; per-user 权重解 axis-shift; bolt on user tower 砸 content-only cold-start; flat AUC + per-user A/B——没认出这是 multi-facet + 无 text query 题, 答成普通 two-tower 推荐题。

## 8 段顺序 (一句导航 cue; 真讲连续说不报标题)

1. Framing — reframe V2V 为 multi-facet + session-time facet 权重 (Twist 1); 边界 (B-scale / p99 50-80ms / single-stage content-only); 4 twist declarative。
2. Data & Label — facet-conditional click/dwell (provenance 留 logged feature) 不 flat; 喂 Twist 3 online loop。
3. Per-modality Encoders — visual / audio / OCR 并行; 必 pre-fusion L2-normalize (Twist 2)。
4. Multi-facet Retrieval — 每 facet 一 HNSW, per-facet quota merge, quota 由 Twist 3 Thompson+Beta 给。
5. Ranking — 轻量 GBDT facet 内排; integrity multiplier 共享尺度, 不进 click reward。
6. Eval — per-facet recall@K + facet-conditional NDCG; IPS replay 摆 A/B 前; session-level cluster-randomized A/B; cold-start slice <24h 验 Twist 4。
7. Boundary — single-stage content-only (Twist 4); 无 user tower; integrity 不折 loss。
8. Wrap — 3 risk: (a) visual tower retrain 致 modality-norm drift 重 dominance (norm-monitor + re-anchor); (b) query-1 cold-start uniform prior 偏轴 (cross-session backoff); (c) integrity 不均匀压制 facet 致 Thompson reward 偏置 (integrity 单列不折 reward)。

## 复用边界 (1-problem-1-URI)

multi-facet ANN + session-time Thompson facet 权重 + pre-fusion L2-normalize + content-only single-stage 是 sd50 carve-up。其他 Meta sd-goldens 共用 ~50% encoder backbone, 但无 text query + 多 facet ANN 是 V2V 独有——见 `cd://96` 与 `sd://meta-reels-golden` / `sd://meta-fb-newsfeed-golden` / `sd://meta-ig-story-golden` / `sd://meta-friend-rec-golden` / `sd://meta-ads-golden`, 不 bundle。
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
    if "sd://meta-v2v-search-golden" not in body:
        errs.append("missing own sd://meta-v2v-search-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd50 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd50 row)."
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

    sd50 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd50 is "
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

    print("\n[DONE] sd50 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
