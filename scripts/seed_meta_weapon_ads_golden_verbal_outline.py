"""Seed: T-P0-894 [Meta-MLSD] sd43 meta-weapon-ads-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for
``slug='meta-weapon-ads-golden'`` (sd43) with a Chinese-narration +
English-terms speaking skeleton distilled from sd43's continuous 45-min
口播稿 (which lives in the ``dataflow`` column, produced by
``scripts/seed_meta_weapon_ads_golden_sd.py``, the oral_narrative archetype
seed migrated by T-P0-894).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892). The
machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD43_VERBAL_V1_20260516 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    multi-modal multi-layer **adversarial classification** twist, sd43's
    signature difficulty (per T-P0-894 spec: signature = adversarial
    classification)
  - 3-5 ``[floating-twist]`` markers (4 used: Adversarial / Liability
    Asymmetry / Admission Posture / Legal-Adjacent Boundary)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd43 was migrated to the ``oral_narrative`` archetype by T-P0-894 (same as
  sd41 Reels). Per ``schemas/meta_mlsd_canonical.yaml`` >
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

  Because sd43 is oral_narrative, this seed uses the sd41-style scope guard
  (assert architecture / production_constraints / tradeoffs / defense are
  empty after the write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI (T-P0-894 tightening vs sd41/sd42): the body references ONLY
its own ``sd://meta-weapon-ads-golden`` URI. Sibling goldens are reached via
the ``cd://96`` hub, NOT via sibling ``sd://`` links in this row (no bundle).

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed
(``seed_meta_weapon_ads_golden_sd.py``); a verbal-only seed recomputing it
would couple two seeds. The task contract is "ONLY touch verbal_outline;
other fields stay as-is". RUN ORDER: the main archetype seed NULLs
verbal_outline, so this verbal seed must run AFTER it (it is authoritative
for this column).

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd43 row -- run
``scripts/seed_meta_weapon_ads_golden_sd.py`` first if missing).

Usage::

    python scripts/seed_meta_weapon_ads_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
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

SLUG = "meta-weapon-ads-golden"
SENTINEL = "<!-- SD43_VERBAL_V1_20260516 -->"

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
# Weapon Ads Classifier — Verbal Outline (45min 口播骨架)

> sd43 (Weapon Ads Classifier, T&S classification) 的口播骨架。完整逐字稿在本题 `dataflow` tab; 方法论 (timing skeleton / Strong Moment 调度 / 8 meta-rules) 在 `cd://96`。此 outline 是进面前扫一眼的"主干 + twist 调度图", 严格 1-problem-1-URI: `sd://meta-weapon-ads-golden`, 不 bundle sibling golden。

## 0 · 一句话主干 (开口前默跑一遍)

一上来就 reframe: 这不是二分类器, 是一个 **Trust & Safety** (T&S, 信任与安全) **admission cascade**——模型产出 calibrated P(weapon), allow / limit / block 由上游 admission-policy 层做。3-stage cascade (cheap pre-screen → multi-modal main → human escalation), 全 stage shared-scale calibrated, main tower late-fusion concat + classification / uncertainty 双 head。input 是单条 ad creative 的多 modality 特征, retrieval N/A。objective 押 policy-violation-recall on frozen golden set, raw accuracy 被负类主导是假指标。

## Floating Twists — 调度图 (本题 4 个, 1 个压舱石)

> twist 不绑 cascade 某一 stage, "漂"在整场: framing declarative 立, body 每个 component 兑现一次。主动调度, 别等挖。

### Twist 1 · Multi-modal Multi-layer Adversarial  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

整场压舱石——这是 adversarial classification 题, 非普通分类。对手 rotate the medium: 价格搬进图、违禁词转写、landing page cloaking、seller 换号。落地: **Optical Character Recognition** (OCR, 光学字符识别) 抽图内文字 + **Contrastive Language-Image Pretraining** (CLIP, 图文对比预训练) 对抗增强 fine-tune + 2-hop seller-graph **Graph Neural Network** (GNN, 图神经网络) 三 modality late-fusion concat。整场兑现 3 次: feature 三象限、model (缺 modality degrade gracefully)、eval (adversarial red-team + 周 counterfactual audit 抓"对的答案错的理由")。

### Twist 2 · Bidirectional Liability Asymmetry  {FLOATING_TWIST_MARKER}

砍掉合法持牌 gun-store 广告是 **false positive** (FP, 假阳性), 代价是 **Federal Firearms License** (FFL, 联邦枪械执照) holder 的 regulatory complaint; 放过非法私枪交易是 **false negative** (FN, 假阴性), 代价是 DOJ subpoena。代价不对称且 flips by jurisdiction——Texas FP 贵, New York FN 贵。兑现: per-region calibrated threshold table (region x category ~60 cells, 周刷), 非全局 cutoff——全局 cutoff 在 base rate 随 region 漂时系统性 over/under-pull。

### Twist 3 · Platform Admission Posture is Upstream  {FLOATING_TWIST_MARKER}

模型输出不是动作, 是要和 jurisdiction / seller posture compose 的 posterior。落地: cascade 每 stage per-region temperature scaling 到同一个 calibrated **P(weapon)** scale, threshold 才能跨 stage 组合。边界: 没有 shared-scale calibration, stage-1 与 stage-2 threshold 代表不同先验, cascade 不 compose——calibration 从锦上添花变成正确性前提。

### Twist 4 · Legal-Adjacent Boundary IS the ML Hard Problem  {FLOATING_TWIST_MARKER}

难的不是明显的步枪, 是 sport-knife / antique / 持牌 seller 这条 legal-adjacent middle——reviewer 自己就 disagree, 那个 disagreement 恰是 policy 层要的信号。落地: disagreement-aware label (reviewer variance 进 uncertainty head, 不被 majority-vote 抹掉) + **Large Language Model** (LLM, 大语言模型)-multimodal teacher distillation 解 label 稀缺 (student ~98% teacher recall @ ~5% cost)。Data&Label 段的 signature nuance, 主动讲。

## Anchor Calibration — best vs worst

{BEST_ANCHOR_MARKER} 满分锚: 开口立"admission cascade 非二分类器"reframe + 4 twist declarative 并 body 逐一兑现; label 用 disagreement-aware 并讲清严格强于 majority-vote; 三套 eval set 各 gate 一个 production action 不 collapse; calibration 是 per-region shared-scale temperature + 每晚 **Expected Calibration Error** (ECE, 期望校准误差) drift gate 当 circuit breaker; 收尾 3 risk + alarm, 尤其"frozen calibrated 但 rolling silently miscalibrated"。

{WORST_ANCHOR_MARKER} 不及格锚: 当普通二分类做, 单 modality (只 caption); compliance/liability 揉进单一 weighted loss; majority-vote 抹掉 disagreement; 全局单一 threshold 不分 jurisdiction; cascade 不做 shared-scale calibration 以为 threshold 自然 compose; eval 只 monitor 一个 **Area Under the Curve** (AUC, 曲线下面积)——本质没认出这是 adversarial + admission-posture 题。

## 8 段顺序 (真讲时连续说, 不报标题; 每段一句导航 cue)

1. Framing — reframe 成 admission cascade; 边界 (几百万/日 · O(100) regions · p99 5ms·80ms·human 4h); recall > accuracy; 4 twist declarative。
2. Data & Label — disagreement-aware label (consensus + variance) 核心; LLM teacher distill 解长尾; 三套 eval set 不 collapse。
3. Features — 四象限, 重 item-side (OCR/CLIP) + seller relational (2-hop graph 6h 刷); seller-graph twist 落地。
4. Model — 3-stage cascade 非 end-to-end (serving-cost + calibration 双 decomposition); late-fusion 非 early fusion; shared-scale calibration 是 compose 前提。
5. Cold-start — new-seller 走 2-hop seller-graph verified-identity prior 兜底; fallback graph → region x category → 全局。
6. Evaluation — 周 counterfactual shortcut audit + 三套 eval set + 小时级 **Kullback-Leibler divergence** (KL, KL 散度) drift; 按 region/seller-verification 切。
7. Serving — 三档 latency; seller-graph 6h 刷; policy threshold 独立 change-management lane (shadow + 1/5/25/100% canary + 3 guardrail 自动 halt)。
8. Wrap — zoom out + 3 risk (seller-graph 窗口太宽 / frozen calibrated 但 rolling miscalibrated / disagreement 被 majority-vote 抹掉)。

## 复用边界 (1-problem-1-URI)

此 outline 的 admission-cascade + shared-scale calibration + OCR/CLIP/seller-graph trio + disagreement-aware label + 三套 eval set 调度是 **Weapon Ads (T&S classification)** 的 carve-up。其他 Meta MLSD 题型结构与 twist 调度图不同, 各自独立 URI——统一 mapping 见 `cd://96` hub, 本 row 只认 `sd://meta-weapon-ads-golden`, 不 bundle sibling。
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

    # 1-problem-1-URI: this row must reference its own sd:// URI ...
    if "sd://meta-weapon-ads-golden" not in body:
        errs.append("missing own sd://meta-weapon-ads-golden URI reference")
    # ... and (T-P0-894 tightening) must NOT bundle any sibling sd:// link.
    # Use the same slug grammar as audit_meta_mlsd_3rule.py's
    # R-XPAGE-sd-link-resolves regex so prose like "sd:// hub" (a space after
    # the scheme) is not mis-detected as a link.
    for slug in re.findall(r"sd://([a-z0-9][a-z0-9_-]*)", body):
        if slug != "meta-weapon-ads-golden":
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
            f"scripts/seed_meta_weapon_ads_golden_sd.py first (this seed only "
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

    sd43 is oral_narrative (same as sd41): architecture /
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
                f"(this seed must touch ONLY verbal_outline; sd43 is "
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

    print("\n[DONE] sd43 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
