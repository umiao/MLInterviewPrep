"""Seed: T-P0-899 [Meta-MLSD] sd48 meta-event-attendance-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for ``slug='meta-event-attendance-golden'``
(sd48) with a Chinese-narration + English-terms speaking skeleton distilled
from sd48's existing English-only verbal_outline (~8.7KB).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45, sd46, sd47 mirrors. The machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD48_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **Consumer dictates architecture** twist, sd48's signature framing: the
    downstream consumer (ranking vs notification-gating vs capacity-planning)
    fixes label, calibration and eval. Skipping this is the failure-mode
    that locks the whole stack to the wrong objective; almost every other
    sd48 decision derives from this fork.
  - 3-5 ``[floating-twist]`` markers (4 used: Consumer-dictates-Architecture /
    RSVP-and-Attend Are Different Labels / Time-to-event as Regime Switcher /
    Per-(consumer, regime) Sliced Calibration)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI no-bundle: own URI ``sd://meta-event-attendance-golden``;
    sibling goldens referenced via ``sd://<slug>`` (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd48 is the ``oral_narrative`` archetype: architecture /
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

  Because sd48 is oral_narrative (matching sd41/sd43/sd44/sd45/sd46/sd47),
  this seed uses the sd41-style scope guard (assert architecture /
  production_constraints / tradeoffs / defense remain NULL after the
  write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references ONLY its own
``sd://meta-event-attendance-golden`` URI. Sibling goldens are reached via the
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
(this seed does not create the sd48 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_event_attendance_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-event-attendance-golden"
SENTINEL = "<!-- SD48_VERBAL_V1_20260515 -->"

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
# Predict-FB-Event-Attendance — Verbal Outline (45min 口播骨架)

> sd48 口播骨架。方法论 `cd://96`。1-problem-1-URI: `sd://meta-event-attendance-golden`, 不 bundle。p(attend) 是 **feature** 不是 end-product, 下游 consumer 决 label / calibration / eval。

## 0 · 一句话主干

Predict-FB-Event-Attendance: 给定 (user, event, time-to-event), 输出 calibrated p(attend) 给下游 consumer。漏斗——**consumer fork** (ranking / notification / capacity) → consumer-supplied 候选 → **Multi-gate Mixture-of-Experts** (MMoE, 多门控混合专家) 双 task head {{p_RSVP, p_attend}}, time-to-event soft-gate 长短 horizon expert → per-(consumer, regime) sliced calibrator → consumer-specific eval。scale: ~3B users / ~10M events / p99 ~120ms ranking。

## Floating Twists — 调度图 (4 个, 1 个压舱石)

> twist 不绑某层, "漂"在整场: framing 立, body 兑现。主动调度。

### Twist 1 · Consumer Dictates Architecture (NOT a generic p-attend model)  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石。p(attend) 是 **feature** 不是 end-product, 下游 consumer 决一切: ranking 要 calibrated online; notification 只评已推 event 关 operating point; capacity 要 aggregated expected-attendees, batch OK 但 calibration critical。Skipping 锁死错 objective。**I pick** SM #1 先 fork over 通用 ranker **because** 三 consumer label / calibrator / eval 数学不同。整场兑现 4 次——framing / data-label / calibration / eval。

### Twist 2 · RSVP and Attend Are Different Labels  {FLOATING_TWIST_MARKER}

~30% RSVP 不到场。consumer 决切分: ranking→`attend`, notification→`RSVP`, capacity→`attend`。**I pick** multi-task head 两 calibrated 输出 {{p_RSVP, p_attend}} 共享 backbone over 两独立模型 **because** 特征重合度高, joint 学 p(attend|p_RSVP) 本身就是 capacity 要的 calibration 信号; RSVP 进 attend head 作 **feature** 不当 label 否则 leak。confirmed-attend = check-in + post-event survey + photo-tag。

### Twist 3 · Time-to-event Is a Regime Switcher (NOT a feature)  {FLOATING_TWIST_MARKER}

不是普通 feature 是 **regime 切换变量**: >72h 长 horizon expert (interest + calendar + social), <72h 短 (weather + reminder + last-minute)。**I pick** MMoE soft-gating over hard-split **because** ~24-72h 边界 fuzzy 且 per-event-type, soft gate 学 per-type; **costs**: ~3x 参数 + per-expert drift 监控; **switches to** hard-split 仅当 expert-collapse。backbone shared **Transformer**, 后 2 层 diverge。new-event-type 冷启动 (cd94: 演唱会 vs 婚礼 vs meetup) 走 embedding + per-type 先验回退到 category-mean。

### Twist 4 · Per-(consumer, regime) Sliced Calibration  {FLOATING_TWIST_MARKER}

三 calibrator: (a) **Isotonic Regression** (保序回归) 给 capacity (Brier 最优); (b) **Platt Scaling** (普拉特缩放) 给 ranking (**Area Under ROC Curve** (AUC, ROC 曲线下面积) 保序); (c) per-threshold cost-aware 给 notification (send-budget)。各 regime-conditional 因 RSVP→attend 在 weather+reminder dominate 后跳变。**I pick** 三 over 一 shared **because** objective 数学不同。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: 4 twist body 兑现; SM #1 先 fork consumer; RSVP/attend 切分 + RSVP 当 feature; time-to-event MMoE soft-gate regime; 三 calibrator per-(consumer, regime); eval 3 surface (sliced / **Inverse Propensity Score** (IPS, 反向倾向分数) replay / consumer-specific A/B); wrap 3 risk。

{WORST_ANCHOR_MARKER} 不及格锚: 通用 p-attend ranker 不 fork; RSVP 当 label 致 leak; time-to-event 当普通 feature; 一 global calibrator; eval 用 raw AUC; 不提 expert-collapse / calibration drift / 婚礼 tiny-sample 风险。

## 8 段顺序 (一句导航 cue; 真讲连续说不报标题)

1. Framing — 边界 (~3B users / ~10M events / 120ms p99 **Service Level Objective** (SLO, 服务水平目标)) + SM #1 fork consumer (Twist 1) + 4 twist declarative。
2. Data & Label — RSVP/attend 切分 (Twist 2): consumer 决 label, multi-task head, RSVP 进 attend head 作 feature。
3. Retrieval-as-Feature-Store — consumer 已 retrieval, 此处 assemble per-(u, e) feature (time_to_event / event_type / host_strength / friends_going / capacity_pressure / 历史 attendance / weather lookahead / RSVP)。
4. Regime-Aware Ranking — MMoE soft-gating (Twist 3): >72h 长, <72h 短, 双 task head 出 {{p_RSVP, p_attend}}, 后 2 层 diverge; new-event-type 走 embedding + category-mean 回退。
5. Calibration — per-(consumer, regime) sliced (Twist 4): isotonic / Platt / cost-aware-threshold。
6. Bias / Cold-start — IPS replay 修曝光 bias; 新 event-type per-type 先验 + smoothed blending; 婚礼小样本 per-cohort 最小样本量 guard。
7. Eval — sliced per-consumer per-regime (Brier capacity / **Normalized Discounted Cumulative Gain** (NDCG, 归一化折损累积增益) @K ranking / precision-at-send-budget notification, time-to-event 桶 slice); IPS replay; A/B = consumer-specific metric NOT raw AUC。
8. Wrap — 3 risk: (a) wrong-consumer lock-in (SM #1 + 早 offline replay); (b) MMoE expert-collapse (per-regime 样本权 + utilization slice + hard-split 回退); (c) RSVP-policy 改后 calibration drift (日 Brier drift monitor + auto-rollback if > 2x baseline)。

## 复用边界 (1-problem-1-URI)

consumer-fork + RSVP/attend 切分 + time-to-event regime + per-(consumer, regime) calibration 是本题 carve-up。Reels / FB News Feed / Top-3 Comments / Friend Rec / Ads ~70% 复用但 twist 调度图不同, 各自独立 URI——见 `cd://96` 与 `sd://meta-reels-golden` / `sd://meta-fb-newsfeed-golden` / `sd://meta-top3-comments-golden` / `sd://meta-friend-rec-golden` / `sd://meta-weapon-ads-golden`, 不 bundle。
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
    if "sd://meta-event-attendance-golden" not in body:
        errs.append("missing own sd://meta-event-attendance-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd48 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd48 row)."
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

    sd48 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd48 is "
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

    print("\n[DONE] sd48 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
