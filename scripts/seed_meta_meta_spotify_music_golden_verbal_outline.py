"""Seed: T-P0-904 [Meta-MLSD] sd53 meta-spotify-music-golden verbal_outline.

Populates ``system_designs.verbal_outline`` for ``slug='meta-spotify-music-golden'``
(sd53) with a Chinese-narration + English-terms speaking skeleton distilled
from sd53's existing English-only verbal_outline (~9.3KB).

GOLDEN-TEMPLATE MIRROR: this row mirrors the sd41 golden template defined by
``scripts/seed_meta_reels_golden_verbal_outline.py`` (T-P0-892) and the sd42,
sd43, sd44, sd45, sd46, sd47, sd48, sd49, sd50, sd51, sd52 mirrors. The
machine-checkable contract is identical:
  - sentinel marker on line 1 (here: ``<!-- SD53_VERBAL_V1_20260515 -->``)
  - exactly 1 ``[DOMINANT]`` marker -- the single 压舱石 twist; here the
    **Relisten Is Positive Signal Not Redundant** twist, sd53's signature
    framing that inverts dedup logic standard across video / article rec:
    same song played 50 times is a 5-star signal, not saturation, so there
    is NO post-ranking dedup. Skipping this is the failure mode that pulls
    music rec back into a generic CF answer with default dedup; almost
    every other sd53 decision derives from this fork (relisten-pool
    injection, per-surface quota with relisten-bias dial, per-track
    relisten-count as positive feature not fatigue flag).
  - 3-5 ``[floating-twist]`` markers (4 used: Relisten-Positive-Not-Redundant /
    Audio-Embedding-Cold-start-Lever / Sequential-Transformer-Mood-Coherence /
    PTC-And-Early-Skip-Over-Playcount)
  - exactly 1 ``[best-anchor]`` + 1 ``[worst-anchor]`` calibration anchors
  - Chinese narration prose + English ML terms; first occurrence of each
    English term uses ``**English full name** (acronym, 中文译名)``
  - 1-problem-1-URI: own URI ``sd://meta-spotify-music-golden``; sibling
    goldens referenced via the ``cd://96`` hub at the end (never bundled)
  - target length 3000-5000 chars (AC floor: >= 2500)

ARCHETYPE NOTE -- SAME SCOPE GUARD AS sd41 (NOT sd42):
  sd53 is the ``oral_narrative`` archetype: architecture /
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

  Because sd53 is oral_narrative (matching sd41/sd43/sd44/sd45/sd46/sd47/
  sd48/sd49/sd50/sd51/sd52), this seed uses the sd41-style scope guard
  (assert architecture / production_constraints / tradeoffs / defense
  remain NULL after the write), NOT the sd42-style fingerprint guard.

1-PROBLEM-1-URI: the body references its own ``sd://meta-spotify-music-golden``
URI in twist/anchor/section text. Sibling goldens appear only at the end
"复用边界" section as "via ``cd://96``" pointers, mirroring the sd49/sd50/sd51/
sd52 pattern. They are not bundled into the body of the problem.

SCOPE: touches ONLY ``verbal_outline`` (+ ``updated_at`` when the value
actually changes). Deliberately does NOT recompute ``content_hash`` or touch
any other column -- ``content_hash`` is owned by the main archetype seed;
a verbal-only seed recomputing it would couple two seeds. The task contract
is "ONLY touch verbal_outline; other fields stay as-is".

IDEMPOTENT: keyed on ``slug``. If ``verbal_outline`` already equals the
target payload, this is a strict no-op (``updated_at`` is NOT bumped), so
running twice yields a byte-identical DB state. The row must already exist
(this seed does not create the sd53 row -- it must have been seeded by the
main archetype seed first).

Usage::

    python scripts/seed_meta_meta_spotify_music_golden_verbal_outline.py [--db data/mle_prep.db] [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

SLUG = "meta-spotify-music-golden"
SENTINEL = "<!-- SD53_VERBAL_V1_20260515 -->"

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
# Meta Spotify-Style Music Recommendation — Verbal Outline (45min 口播骨架)

> sd53 口播骨架。方法论 `cd://96`。1-problem-1-URI: `sd://meta-spotify-music-golden`, 不 bundle。主特点: **relisten 是正信号不是冗余**, 同曲 50 次 = 5 星, **无 post-ranking dedup**。主杆 audio + **Collaborative Filtering** (CF, 协同过滤) + relisten-pool 三源召回 → sequential transformer over session prefix → per-surface quota, 不是 video-rec 默认去重 ranker。

## 0 · 一句话主干

per-surface next-track / slate。漏斗——audio-emb **Approximate Nearest Neighbor** (ANN, 近似最近邻) over log-mel-spectrogram **Convolutional Neural Network** (CNN, 卷积神经网络) 128-256d + CF two-tower ANN + relisten-pool (不去重) → transformer over session prefix (last ~20 tracks) → per-surface quota (Radio 高 relisten / Discover 高 new-track) → **Inverse Propensity Scoring** (IPS, 逆倾向打分) replay 校 auto-play-queue。scale: ~500M **Monthly Active Users** (MAU, 月活), ~100M tracks (~60k 新/天), p99 ~100ms。

## Floating Twists (4 个, 1 个压舱石)

### Twist 1 · Relisten Is Positive Signal, NOT Redundant  {FLOATING_TWIST_MARKER} {DOMINANT_MARKER}

压舱石。music 反转 video / article 默认 dedup——同曲 50 次 = 5 星不是 saturation。**I pick** 不做 post-rank dedup + relisten-pool injection over 默认去重 **because** dedup 压最强正信号; relisten-count-30d 当**正 feature**, 不是 fatigue flag; **costs**: 单曲 runaway 正环路, 需 per-user track-entropy monitor + 阈值后 boost cap; **switches to** 软抑制仅单轨超 entropy 阈值时。整场兑现 4 次。

### Twist 2 · Audio Embedding from Spectrogram As Cold-start Lever  {FLOATING_TWIST_MARKER}

CNN over log-mel-spectrogram → 128-256d, upload-time 索引到 **Hierarchical Navigable Small World** (HNSW, 分层可导航小世界)。**I pick** audio-emb ANN over CF-only **because** metadata (artist / genre / **Beats Per Minute** (BPM, 每分钟节拍) / energy / valence) 对 ~60k 新轨/天太粗, CF 对 zero-playcount 长尾有硬上限; upload-time 索引让零播放新轨进池; **costs**: 周度 CNN refit + spectrogram 预处理 + 双索引; **switches to** CF-only 仅 <30s 短轨 / 错标 podcast。

### Twist 3 · Sequential Transformer over Session Prefix (Mood Coherence Is Autoregressive)  {FLOATING_TWIST_MARKER}

mood coherence 是 within-session 主载信号——pointwise **Gradient-Boosted Decision Tree** (GBDT, 梯度提升决策树) 把 "rock→classical→rock" 当通过, session-abandon 在 mood 跳变时尖峰, pointwise loss 看不见。**I pick** transformer over session prefix (last ~20 tracks audio_emb + meta + **Play-To-Completion** (PTC, 完播)) over pointwise GBDT **because** mood coherence 是 autoregressive constraint 不是 user-static feature; **costs**: ~10x ranker latency (top-200 截断 + per-session **Key-Value cache** (KV-cache, 键值缓存) 复用兜); **switches to** GBDT pointwise 仅 Discover Weekly batch (session 缺席)。

### Twist 4 · PTC + Early-Skip Over Play-count (Play-count Is Gameable)  {FLOATING_TWIST_MARKER}

play-count 被 auto-play queue 灌水——count 涨但无主动选择, 当 label 学的是队列默认行为不是偏好。**I pick** PTC (≥30s OR ≥80%) 主正 + early-skip (<30s) 主负 over play-count **because** PTC 绑定主动 engagement, early-skip 显性暴露错配; **costs**: per-track-duration 归一化, label-delay, 低频用户稀疏; **switches to** play-count 仅 cold track 兜底。

## Anchor Calibration

{BEST_ANCHOR_MARKER} 满分锚: 开口立 "relisten 正信号 不 dedup" reframe; 4 twist 兑现; label PTC + early-skip; audio-emb upload-time 索引解 cold-start; transformer session-prefix; per-surface quota 不折 loss; eval 按 mood × cold-track × relisten × tenure 切; IPS replay; cluster-randomized A/B; wrap 3 risk。

{WORST_ANCHOR_MARKER} 不及格锚: 默认 dedup 压掉 relisten 正信号; play-count 当主 label 学队列默认; CF-only 撞 ~60k 新轨/天硬上限; pointwise GBDT 让 mood 跳变溜过; diversity 折进 loss; flat top-line 埋掉 cold-track skip 尖峰——没认出 relisten-positive + audio-cold-start + sequential mood-coherence 三结构。

## 8 段顺序 (一句导航 cue; 连续说)

1. Framing — relisten-positive (T1) + audio cold-start (T2) + sequential mood (T3); ~500M MAU / ~100M tracks (~60k 新/天) / p99 100ms。
2. Data & Label — PTC 主正, early-skip <30s 主负 (T4); save / add-to-playlist 显性正; relisten-count-30d 是正 feature (T1)。
3. Candidate Gen — 三源: audio-emb ANN (CNN log-mel→HNSW, upload-time T2) + CF two-tower ANN + relisten-pool injection (不去重 T1)。
4. Ranking — transformer over session prefix (T3), last ~20 tracks → next-track logit; 非 pointwise GBDT。
5. Diversity & Cold-start — per-surface quota: Radio 高 relisten / Discover 高 new-track (~10-20%); cold track <14d audio-emb ANN + quality-gated burst; cold user <30d audio-affinity backoff + popularity prior。
6. Eval — per-surface 切 (Radio: skip + session-len, Discover: 首周 PTC + save), 按 mood × cold-track × relisten × tenure 分层; IPS replay; cluster-randomized A/B。
7. Boundary — 不 dedup; play-count 不当主 label; pure CF 不撑长尾; pointwise 不撑 mood; diversity 不进 loss; integrity 单列 gate。
8. Wrap — 3 risk: (a) CF popularity collapse 当 audio 退化 — cold-track quota dashboard; (b) mood-classifier drift (lo-fi / hyperpop) — 季度 taxonomy refresh; (c) relisten saturation pathology — track-entropy monitor + boost cap。

## 复用边界 (1-problem-1-URI)

relisten-positive 不 dedup + audio-emb upload-time 索引 + transformer session-prefix + per-surface quota 是 sd53 (`sd://meta-spotify-music-golden`) carve-up。mood coherence 当 autoregressive constraint 是音乐独有——见 `cd://96` 与 `sd://meta-reels-golden`, 不 bundle。
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
    if "sd://meta-spotify-music-golden" not in body:
        errs.append("missing own sd://meta-spotify-music-golden URI reference")

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
            f"ERROR: no system_designs row for slug={SLUG}. The sd53 row "
            f"must already exist (this seed only populates verbal_outline on "
            f"an existing row; it does not create the sd53 row)."
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

    sd53 is the oral_narrative archetype: this uses the sd41-style scope
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
                f"(this seed must touch ONLY verbal_outline; sd53 is "
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

    print("\n[DONE] sd53 verbal_outline golden-mirror seed: all ACs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
