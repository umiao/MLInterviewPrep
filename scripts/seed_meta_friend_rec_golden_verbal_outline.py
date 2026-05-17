"""Seed: T-P0-895 [Meta-MLSD] sd44 meta-friend-rec-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for
``slug='meta-friend-rec-golden'`` (sd44) with a Chinese-narration +
English-terms speaking skeleton distilled from sd44's continuous 45-min
口播稿 (which lives in the ``dataflow`` column, produced by
``scripts/seed_meta_friend_rec_golden_sd.py``, the oral_narrative archetype
seed migrated by T-P0-895).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd43
mirror by ``scripts/seed_meta_weapon_ads_golden_verbal_outline.py``
(T-P0-894). The machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD44_VERBAL_V1_20260516 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **graph-native bilateral matching** twist, sd44's signature difficulty
    (per T-P0-895 spec: signature = graph-native)
  - 3-5 ``[floating-twist]`` markers (4 used: Graph-native Bilateral /
    Network-effect Counterfactual / NRT Bilateral Signal / Abuse-posture
    Upstream)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd44 was migrated to the ``oral_narrative`` archetype by T-P0-895 (same as
  sd41 Reels and sd43 Weapon-Ads). Per ``schemas/meta_mlsd_canonical.yaml`` >
  ``document_archetypes.values.oral_narrative.contract.nullable_fields``,
  architecture / production_constraints / tradeoffs / defense /
  verbal_outline are legal-NULL (the archetype seed deliberately NULLs them;
  their content is inlined in the dataflow narrative). ``verbal_outline`` is
  NULLable but NOT forbidden -- ``sd_golden.fields.verbal_outline`` is
  ``required: false, apply_3rule: false`` with only the
  ``R-XPAGE-verbal-no-cd96-dup`` duplication guard. The Meta-MLSD
  harmonization batch (T-P0-892 .. T-P0-896 + sd46-sd53) opts each of the 13
  sd-goldens INTO a populated verbal_outline so the SystemDesignDrawer (which
  renders verbal_outline first since T-P0-891) has a consistent speaking
  skeleton tab. ``audit_meta_mlsd_3rule.py`` skips nullable columns whether
  NULL or populated, so this is audit-safe.

  Because sd44 is oral_narrative, this seed uses the sd41-style scope guard
  (assert architecture / production_constraints / tradeoffs / defense are
  empty after the write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI (mirroring T-P0-894): the body references ONLY its own
``sd://meta-friend-rec-golden`` URI. Sibling goldens are reached via the
``cd://96`` hub, NOT via sibling ``sd://`` links in this row (no bundle).

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed
(``seed_meta_friend_rec_golden_sd.py``); a verbal-only seed recomputing it
would couple two seeds. The task contract is "ONLY touch verbal_outline;
other fields stay as-is". RUN ORDER: the main archetype seed NULLs
verbal_outline, so this verbal seed must run AFTER it (it is authoritative
for this column).

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd44 row -- run
``scripts/seed_meta_friend_rec_golden_sd.py`` first if missing).

Usage::

    python scripts/seed_meta_friend_rec_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-friend-rec-golden"
SENTINEL = "<!-- SD44_VERBAL_V1_20260516 -->"

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
# Friend Recommendation — Verbal Outline (45min 口播骨架)

> sd44 (Friend Recommendation, Bilateral matching) 的口播骨架。完整逐字稿在本题 `dataflow` tab; 方法论在 `cd://96`。此 outline 是进面前扫一眼的"主干 + twist 调度图", 严格 1-problem-1-URI: `sd://meta-friend-rec-golden`, 不 bundle sibling。

## 0 · 一句话主干 (开口前默跑一遍)

一上来就 reframe: 这不是 single P(click) ranker, 是长在 social graph 上的 **bilateral matching** (双边匹配) 问题——target 是 `P(send) x P(accept)`, 由 sender intent 和 receiver receptivity 两个物理非对称分布相乘。方案: abuse-aware admission gate → 5-channel retrieval funnel (mutual / 2-hop / two-tower / cohort / inferred-real-life) → **Multi-gate Mixture-of-Experts** (MMoE, 多门控专家混合) multi-head bilateral ranker, NRT 双侧信号 score time join, serving score = product per-relationship-type calibrated。friend graph 是 corpus 不是 input。objective 押 28 天 sustained-bilateral-engagement, raw acceptance 可刷是假指标。

## Floating Twists — 调度图 (本题 4 个, 1 个压舱石)

> twist 不绑 funnel 某一层, "漂"在整场: framing declarative 立, body 逐一兑现。主动调度, 别等挖。

### Twist 1 · Graph-native Bilateral Matching  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石——这题最 signature 的是它 graph-native: 整个问题活在一张秒级 mutate 的 social graph 上, 这性质同时派生后三个 twist。落地: target 是两个非对称分布乘积; MMoE multi-head bilateral——shared bottom + 两 gating head 各 route expert 到 P(send) / P(accept) tower; serving 取 product 非 sum (product 是 calibrated bilateral 概率非 ranking, growth / safety threshold 才能同刻度 compose)。整场兑现 3 次: feature (interaction graph relational 最重)、model (5-channel graph retrieval)、eval (graph spillover 逼出 cluster-randomized)。

### Twist 2 · Network-effect Counterfactual  {FLOATING_TWIST_MARKER}

treatment effect 沿 friend edge 泄漏, 两臂互污。落地: cluster-randomized **A/B** (随机对照实验) 在 **Louvain / Leiden** (社区发现算法) community cluster 上做, 方差用 **Leave-One-Cluster-Out** (LOCO, 留一簇外) delta method 恢复 (cluster 不均, naive 标准误低估 2-4x)。**Stable Unit Treatment Value Assumption** (SUTVA, 个体处理稳定性假设)-violation 诊断进实验契约: cluster 与 user-level 偏离 > 20% 即 reject user-level。代价: 每 cell ~10x sample size + 每周 clustering 刷新; 踩过 user-level 高估 ~40% 的坑。

### Twist 3 · NRT Bilateral Signal  {FLOATING_TWIST_MARKER}

friend graph 秒级 mutate, 双方 recent state 只在 score time 有信息量, daily snapshot 漏 90%+ recent-action surface。落地: **Near-Real-Time** (NRT, 近实时) 双侧 streaming join——**Kafka** -> **Flink** (流处理引擎) 维护双侧 last-N 秒 accept/reject/block, score time 当 state feature join 进 ranker, 端到端 60s SLA, hot-key lookup p99 < 10 ms。边界: 不能 batch precompute (recent-action 秒级衰减); 退化时 daily-batch fallback + freshness > 5min 软报警。

### Twist 4 · Abuse-posture is Upstream  {FLOATING_TWIST_MARKER}

spammer 把 P(send) 拉满、abuse-victim 把 P(accept-from-stranger) 压到底, abuse 过滤必须在 retrieval 之前不是事后 rerank——spammer recs 绝不能进候选池。落地: abuse-aware admission gate 守在 retrieval 前 (abuse-flag 6h 刷新) + per-relationship-type calibration 让 growth 与 safety threshold 同刻度 compose。signature nuance: 正样本定义本身是 senior judgment, 主动讲。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: 开口立"graph-native bilateral matching 非 single ranker"reframe + 4 twist declarative 并 body 逐一兑现; bilateral positive (send AND accept AND 28 天 >=1 post-accept) 并讲清严格强于 send-only; serving 取 product per-relationship-type calibrated 主动纠正 single-weighted-loss category error; 实验用 cluster-randomized A/B + LOCO + SUTVA 诊断并解释 why; 收尾 3 risk + alarm, 尤其"user-level 高估 ~40% → cluster-randomized 是实际 change-management surface"。

{WORST_ANCHOR_MARKER} 不及格锚: 当 single P(click) ranker 做; P(send)/P(accept) 揉进单一 weighted loss; serving 取 sum 丢 calibrated-bilateral; user-level A/B 不管 spillover; abuse 当事后 rerank; NRT 当 daily-batch 聚合——没认出这是 graph-native 双边匹配题。

## 8 段顺序 (真讲时连续说, 不报标题; 每段一句导航 cue)

1. Framing — reframe 成 graph-native bilateral matching; 边界 (几亿 DAU · 几十亿 edge · ~10k 池 · top-K 20 · p99 100ms); objective 押 28 天 engagement; 4 twist declarative。
2. Data & Label — bilateral positive (send AND accept AND 28 天 post-accept); 非对称 negative 70/30 (P(send)) vs 50/50 (P(accept)); 三套 eval set 不 collapse。
3. Features — 四象限, 重 interaction relational (mutual-friend + Adamic-Adar + channel-of-origin one-hot); NRT lane 是 state feature。
4. Model — 5-channel retrieval funnel + MMoE multi-head bilateral; serving 取 product 非 sum; per-relationship-type calibration 是 compose 前提。
5. Cold-start — new-user 走 inferred-real-life + 2-hop graph prior; fallback graph → cohort → 全局; 仍过 abuse gate。
6. Evaluation — cluster-randomized A/B + LOCO 方差 + SUTVA 诊断; 三套 eval set 各 gate 一个 action; 小时级双 head KL drift。
7. Serving — retrieval 5 路并行; NRT 双侧 score-time join; cluster-canary rollout (shadow + 1/5/25/100% + 3 guardrail)。
8. Wrap — zoom out + 3 risk (NRT freshness 太宽 / user-level spillover 高估 / bilateral 当 single weighted-loss category error)。

## 复用边界 (1-problem-1-URI)

此 outline 的 graph-native bilateral matching + MMoE multi-head P(send)xP(accept) + 5-channel funnel + NRT 双侧 score-time signal + cluster-randomized A/B + abuse-aware gate 调度是 **Friend Recommendation** 的 carve-up。其他题型 twist 调度图不同, 各自独立 URI——mapping 见 `cd://96` hub, 本 row 只认 `sd://meta-friend-rec-golden`, 不 bundle sibling。
"""


def _now() -> str:
    """Return an ISO-8601 UTC timestamp with seconds precision."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def _content_self_check() -> list[str]:
    """Validate the in-module payload against the golden-template contract.

    Run before any DB write so a malformed template fails fast. Mirrors the
    sd41 reference assertion set (T-P0-892) and the sd43 mirror (T-P0-894).
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

    # 1-problem-1-URI: this row must reference its own sd:// URI ...
    if "sd://meta-friend-rec-golden" not in body:
        errs.append("missing own sd://meta-friend-rec-golden URI reference")
    # ... and (mirroring T-P0-894) must NOT bundle any sibling sd:// link.
    # Use the same slug grammar as audit_meta_mlsd_3rule.py's
    # R-XPAGE-sd-link-resolves regex so prose like "sd:// hub" (a space after
    # the scheme) is not mis-detected as a link.
    for slug in re.findall(r"sd://([a-z0-9][a-z0-9_-]*)", body):
        if slug != "meta-friend-rec-golden":
            errs.append(
                f"forbidden sibling sd:// link 'sd://{slug}' (1-problem-1-URI: "
                f"own slug only; reach siblings via cd://96 hub)"
            )

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
            f"ERROR: no system_designs row for slug={SLUG}. Run "
            f"scripts/seed_meta_friend_rec_golden_sd.py first (this seed only "
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
    """Post-write DB-side validation against the golden-template contract.

    sd44 is oral_narrative (same as sd41/sd43): architecture /
    production_constraints / tradeoffs / defense are NULL by archetype, so
    this uses the sd41-style scope guard (assert those 4 columns empty after
    the write) -- NOT the sd42-style fingerprint guard.
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

    # Scope guard (sd41-style, oral_narrative): this seed must not have
    # populated the archetype-NULL fields.
    for col, val in (
        ("architecture", architecture),
        ("production_constraints", prod_cons),
        ("tradeoffs", tradeoffs),
        ("defense", defense),
    ):
        if val:
            errs.append(
                f"AC FAIL: scope violation -- {col} unexpectedly non-empty "
                f"(this seed must touch ONLY verbal_outline; sd44 is "
                f"oral_narrative so {col} must stay NULL)"
            )

    print(f"[OK] row id={rid} slug={SLUG}")
    print(f"     verbal_outline chars={n} (target {TARGET_MIN}-{TARGET_MAX})")
    print(f"     markers: DOMINANT={dom} floating-twist={ft}")
    print(
        f"     scope: architecture="
        f"{'NULL' if not architecture else len(architecture)} "
        f"production_constraints="
        f"{'NULL' if not prod_cons else len(prod_cons)} "
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

    print("\n[DONE] sd44 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
