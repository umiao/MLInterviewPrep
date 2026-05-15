"""Retrofit Meta MLSD doc 96 (Main Hub) with Drawer 入口 header + dedupe (T-P0-845, T-P0-871).

Per T-P0-845 ([Meta-MLSD I]) + T-P0-871 ([META-MLSD-CD96-LINK-IN]). Target:
company_documents.id=96, company_id=31, title '[Meta-MLSD] 45min Playbook + 4
Strong Moments' (is_golden=1, default first-page Meta MLSD entry).

Two-part edit:
1. Prepend a prominent Drawer 入口 顶部 section (8 entries, NO self-link
   cd://96) + horizontal rule before the body. The 4 sd-golden worked
   examples (Reels / Top-3 / Weapon Ads / Friend Rec) are grouped at the top
   of the table; cd-sibling docs + generic cookbook follow.
2. Dedupe: REMOVE the existing mid-doc 'Section 8 Drawer — 深内容入口' (from
   T-P0-840 initial seed; its 3 entries are now superseded by the new top
   section). Renumber the original 'Section 9. 30 秒判题流程' → 'Section 8.'.

Section 2's inline reference `[Reels Home Feed (45min walkthrough) →](sd://
meta-reels-golden)` is narrative prose, KEPT verbatim (dedupe only applies
to the drawer-index style section).

DRAWER URI INVENTORY (8 entries, NO self-link cd://96):
  - sd://meta-reels-golden                  (T-P0-837)
  - sd://meta-top3-comments-golden          (T-P0-868, added to canonical via T-P0-871)
  - sd://meta-weapon-ads-golden             (T-P0-869, added via T-P0-871)
  - sd://meta-friend-rec-golden             (T-P0-870, added via T-P0-871)
  - cd://94                                  (Family Taxonomy + 13 Question Cards)
  - cd://95                                  (Cross-cutting 积木库)
  - cd://97                                  (T-A: RecSys 核心模型 8 工作)
  - sd://interview-recommendation-system     (general RecSys SD cookbook)

DEPS resolved at runtime (fail loud if any drift):
  - cd://94, cd://95, cd://97 must exist with expected title fragments
  - sd://meta-reels-golden, sd://interview-recommendation-system slugs resolve

Idempotency: sentinel <!-- META_MLSD_DRAWER_HEADER_96_20260512 --> placed as
the first content line. The body transform (drop old Section 8 + renumber)
is itself idempotent. On re-run, if sentinel present + content byte-identical,
report UNCHANGED with 0 writes.

Self-link contract: cd://96 must NOT appear in the prepended Drawer 入口
section (checked via post-write scan over the prepended block only — body
may keep any pre-existing inline cross-references unchanged).

Style: NO emoji; blockquote `> ` prefix on every drawer line; `**[label](URI)**`
bold-link format; horizontal rule `---` separator before body.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

SENTINEL = "<!-- META_MLSD_DRAWER_HEADER_96_20260512 -->"

COMPANY_ID = 31  # Meta
DOC_ID = 96
EXPECTED_TITLE = "[Meta-MLSD] 45min Playbook + 4 Strong Moments"

# Sibling drawer references (17 entries: 13 sd-goldens covering cd94 Q1-Q13 +
# 4 cd/cookbook complementary entries). NO self-link cd://96.
# Per user directive 2026-05-15 -- full 13-题 family in drawer for one-click
# access to any walkthrough.
FAMILY_TAXONOMY_DOC_ID = 94    # 13 题 Family Taxonomy
CROSS_CUTTING_DOC_ID = 95      # Cross-cutting 积木库
RECSYS_MODELS_DOC_ID = 97      # T-A: RecSys 核心模型 8 工作 (per T-P0-842)
SD_GENERIC_RECSYS = "interview-recommendation-system"

# 13 sd-goldens, ordered by cd94 Family Taxonomy Q-number (Q1..Q13):
SD_Q1_TOP3_GOLDEN = "meta-top3-comments-golden"     # T-P0-868
SD_Q2_V2V_GOLDEN = "meta-v2v-search-golden"         # T-P1-886 (top-9 batch)
SD_Q3_FRIEND_GOLDEN = "meta-friend-rec-golden"      # T-P0-870
SD_Q4_ADS_GOLDEN = "meta-ads-golden"                # T-P0-885 (top-9 batch)
SD_Q5_EVENT_REC_GOLDEN = "meta-event-rec-golden"    # T-P1-887 (top-9 batch)
SD_Q6_LOCATION_GOLDEN = "meta-location-rec-golden"  # T-P1-888 (top-9 batch)
SD_Q7_WEAPON_GOLDEN = "meta-weapon-ads-golden"      # T-P0-869
SD_Q8_YELP_GOLDEN = "meta-yelp-restaurant-golden"   # N1.5 anchor (top-9 batch)
SD_Q9_NEWSFEED_GOLDEN = "meta-fb-newsfeed-golden"   # N1 anchor (top-9 batch)
SD_Q10_IG_STORY_GOLDEN = "meta-ig-story-golden"     # T-P0-883 (top-9 batch)
SD_Q11_SPOTIFY_GOLDEN = "meta-spotify-music-golden" # T-P2-889 (top-9 batch)
SD_Q12_EVENT_ATTEND_GOLDEN = "meta-event-attendance-golden"  # T-P0-884 (top-9 batch)
SD_Q13_REELS_GOLDEN = "meta-reels-golden"           # T-P0-837

# Back-compat aliases for any caller importing the old names:
SD_REELS_GOLDEN = SD_Q13_REELS_GOLDEN
SD_TOP3_GOLDEN = SD_Q1_TOP3_GOLDEN
SD_WEAPON_GOLDEN = SD_Q7_WEAPON_GOLDEN
SD_FRIEND_GOLDEN = SD_Q3_FRIEND_GOLDEN

# Body dedupe markers. Section indices bumped +1 after T-P0-847 inserted
# 'Section 2 Twist 挖掘方法论' into the seed; Drawer is now Section 9 and
# the trailing 30 秒判题 flow is Section 10 (collapsed back to 9 here).
SECTION_DRAWER_OLD = "## 9. Drawer — 深内容入口"
SECTION_TRIAGE_OLD = "## 10. 30 秒判题流程"
SECTION_TRIAGE_NEW = "## 9. 30 秒判题流程"

DRAWER_INDEX = f"""> ## Drawer 入口（点击展开详读）
>
> **13 题 Family Goldens** (cd94 Q1-Q13 顺序, 每行一个 sd-golden 口播稿):
>
> | 入口 | 内容 | 何时打开 |
> | --- | --- | --- |
> | **[Q1 · Top-3 Comments Golden](sd://{SD_Q1_TOP3_GOLDEN})** | Intra-item ranking · 单池小候选 · position-0 决定下游 conversation | 候选池极小 + label-heavy + selection-bias 主例 |
> | **[Q2 · Video-to-Video Search Golden](sd://{SD_Q2_V2V_GOLDEN})** | Pure retrieval (no query) · multi-facet · L2-normalize-before-fusion | "similar undefined" 多 facet + session-learned facet 权重 |
> | **[Q3 · Friend Recommendation Golden](sd://{SD_Q3_FRIEND_GOLDEN})** | Graph-native · P(send)×P(accept) bilateral · MMoE 双头 + cluster A/B | 图结构 retrieval + reciprocity-aware label + NRT 双边信号 |
> | **[Q4 · Ads Recommendation Golden](sd://{SD_Q4_ADS_GOLDEN})** | Auction-mediated · 必须 calibrated probability · IPS replay before A/B | bid×pCTR×pConversion×quality + delayed-feedback + 广告主博弈 |
> | **[Q5 · Event Recommendation Golden](sd://{SD_Q5_EVENT_REC_GOLDEN})** | 双 cold-start (event new/expire + 用户 RSVP 极稀) · content-based 主导 | 不能套 user-item CF + hard filter geo/time/capacity + 友选偏差 |
> | **[Q6 · Location Recommendation Golden](sd://{SD_Q6_LOCATION_GOLDEN})** | Context (time/weather/calendar/party) 是主导 intent disambiguator | 9am/9pm 同一用户 intent 不同 + intent 分类中间任务 + walk-vs-drive |
> | **[Q7 · Weapon Ads Classifier Golden](sd://{SD_Q7_WEAPON_GOLDEN})** | Adversarial T&S · admission-cascade · shared-scale calibration | cascade + 三段 eval + 多模态 T&S + LLM-teacher distill |
> | **[Q8 · Yelp Restaurant Golden](sd://{SD_Q8_YELP_GOLDEN})** | Aspect-level matching from review text (rating-CF 上限低) | LLM aspect 抽取 + 用户自评 self-referential profile + 照片新鲜度 |
> | **[Q9 · FB News Feed Golden](sd://{SD_Q9_NEWSFEED_GOLDEN})** | Heterogeneous · **MSI** 而非 engagement · 多源 CG · integrity 乘性下调 | MSI 标签层级 + 多源混合 + close-friend bypass + integrity cascade |
> | **[Q10 · IG Story Golden](sd://{SD_Q10_IG_STORY_GOLDEN})** | Author-tray 不是 story 是 ranking unit · 24h 硬过期 · 跳到下作者 = 负标 | author-tray reframe + tray 内 autoregressive + 闭友 prior 跨日 |
> | **[Q11 · Spotify Music Golden](sd://{SD_Q11_SPOTIFY_GOLDEN})** | Relisten = positive (反转视频/文章 dedup 逻辑) · 音频 spectrogram emb | session mood 连续 + skip-rate 主负 + relisten-30d 是 feature 不是 dedup |
> | **[Q12 · Predict Event Attendance Golden](sd://{SD_Q12_EVENT_ATTEND_GOLDEN})** | Prediction-as-feature · 必须先问下游 consumer (ranking/notify/capacity) | RSVP-vs-attend 标签分裂 + time-to-event 切换 model regime + calibration 取决于下游 |
> | **[Q13 · Reels Home Feed Golden](sd://{SD_Q13_REELS_GOLDEN})** | Session-continuous ranking · 多模态 UGC · watch-completion-ratio | Reels 这题 end-to-end (DLRM / multi-task / multimodal / 反 feedback loop) |
>
> **配套 cd / cookbook 入口**:
>
> | 入口 | 内容 | 何时打开 |
> | --- | --- | --- |
> | **[13 题 Family Taxonomy](cd://{FAMILY_TAXONOMY_DOC_ID})** | Q1-Q13 卡片 + 题型识别 + 30 秒判 family | 拿到新题, 30 秒锁定 family |
> | **[Cross-cutting 9 ML 积木](cd://{CROSS_CUTTING_DOC_ID})** | Two-Tower / IPS / LLM-teacher / Calibration | 套通用 ML 模块 |
> | **[RecSys 核心模型 8 工作](cd://{RECSYS_MODELS_DOC_ID})** | DCN / DLRM / HSTU / RankMixer / RQ-VAE / CF | 模型层面 deep-dive |
> | **[通用 RecSys SD Cookbook](sd://{SD_GENERIC_RECSYS})** | Two-Tower + DLRM + MMoE 教科书 | 想看通用 RecSys 而不止 Meta |

---

"""

PREPENDED_BLOCK = f"{SENTINEL}\n\n{DRAWER_INDEX}"


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def transform_body(body: str) -> str:
    """Drop body Drawer section + renumber trailing triage section (idempotent)."""
    # Idempotent: if already transformed, no-op.
    if SECTION_DRAWER_OLD not in body:
        if SECTION_TRIAGE_NEW in body:
            return body
        raise RuntimeError(
            "body lacks both drawer header "
            f"{SECTION_DRAWER_OLD!r} and post-transform header "
            f"{SECTION_TRIAGE_NEW!r}; refusing to guess"
        )

    start = body.find(SECTION_DRAWER_OLD)
    next_sec = body.find(SECTION_TRIAGE_OLD, start)
    if next_sec == -1:
        raise RuntimeError(
            f"triage marker {SECTION_TRIAGE_OLD!r} not found after "
            f"drawer section at offset {start}"
        )

    # Remove block from `## 9. Drawer ...` through (exclusive) `## 10. ...`.
    # The original `---\n\n` separator that preceded the drawer section is
    # preserved (it now separates Section 8 from the renumbered Section 9).
    trimmed = body[:start] + body[next_sec:]
    return trimmed.replace(SECTION_TRIAGE_OLD, SECTION_TRIAGE_NEW, 1)


def build_content(existing_body: str) -> str:
    """Assemble final content = sentinel + drawer index + transformed body."""
    return f"{PREPENDED_BLOCK}{transform_body(existing_body)}"


def validate_content(content: str, transformed_body: str) -> None:
    """Sanity checks mirroring T-P0-845 acceptance criteria."""
    # AC #1: content STARTS WITH `> ## Drawer 入口` (after sentinel + blank).
    if not content.startswith(SENTINEL):
        raise RuntimeError(
            f"sentinel must be first line of content; got {content[:80]!r}"
        )
    lines = content.splitlines()
    first_visible = next(
        (
            ln
            for ln in lines[1:]
            if ln.strip() and not ln.strip().startswith("<!--")
        ),
        None,
    )
    if first_visible is None or not first_visible.startswith("> ## Drawer 入口"):
        raise RuntimeError(
            f"first visible line should be Drawer 入口 blockquote; "
            f"got {first_visible!r}"
        )

    # AC #2 (2026-05-15 widened from 8 to 17): 17 unique drawer URIs each appear
    # exactly once IN PREPENDED BLOCK; cd://96 (self) must NOT appear.
    # The 13 sd-goldens (cd94 Q1-Q13 family) are required by
    # schemas/meta_mlsd_canonical.yaml cd96_playbook.drawer_header.must_link_sd_goldens.
    # History: T-P0-845 base (5), T-P0-871 (5→8: +weapon+friend),
    # 2026-05-15 (8→17: +9 top-9-batch sd-goldens for full 13-题 family coverage).
    drawer_uris = [
        # 13 sd-goldens (Q1-Q13 from cd94 family)
        f"sd://{SD_Q1_TOP3_GOLDEN}",
        f"sd://{SD_Q2_V2V_GOLDEN}",
        f"sd://{SD_Q3_FRIEND_GOLDEN}",
        f"sd://{SD_Q4_ADS_GOLDEN}",
        f"sd://{SD_Q5_EVENT_REC_GOLDEN}",
        f"sd://{SD_Q6_LOCATION_GOLDEN}",
        f"sd://{SD_Q7_WEAPON_GOLDEN}",
        f"sd://{SD_Q8_YELP_GOLDEN}",
        f"sd://{SD_Q9_NEWSFEED_GOLDEN}",
        f"sd://{SD_Q10_IG_STORY_GOLDEN}",
        f"sd://{SD_Q11_SPOTIFY_GOLDEN}",
        f"sd://{SD_Q12_EVENT_ATTEND_GOLDEN}",
        f"sd://{SD_Q13_REELS_GOLDEN}",
        # 4 cd / cookbook complementary entries
        f"cd://{FAMILY_TAXONOMY_DOC_ID}",
        f"cd://{CROSS_CUTTING_DOC_ID}",
        f"cd://{RECSYS_MODELS_DOC_ID}",
        f"sd://{SD_GENERIC_RECSYS}",
    ]
    for uri in drawer_uris:
        c = PREPENDED_BLOCK.count(uri)
        if c != 1:
            raise RuntimeError(
                f"drawer URI {uri!r} appears {c}x in prepended block; "
                f"expected exactly 1"
            )

    self_uri = f"cd://{DOC_ID}"
    if self_uri in PREPENDED_BLOCK:
        raise RuntimeError(
            f"self-link violation: {self_uri!r} found in prepended block"
        )

    # AC #3: body Drawer section fully removed.
    if SECTION_DRAWER_OLD in content:
        raise RuntimeError(
            f"dedupe failed: {SECTION_DRAWER_OLD!r} still present in content"
        )

    # AC #4: triage section renumbered (## 10. → ## 9.).
    if SECTION_TRIAGE_OLD in content:
        raise RuntimeError(
            f"renumber failed: {SECTION_TRIAGE_OLD!r} still present"
        )
    if SECTION_TRIAGE_NEW not in content:
        raise RuntimeError(
            f"renumber failed: {SECTION_TRIAGE_NEW!r} not found in content"
        )

    # AC #5: H2 count = 1 (Drawer 入口 inside blockquote, `> ## `) + 9
    # (Sections 1..9 after T-P0-847 inserted 'Twist 挖掘方法论' as new
    # Section 2). Both `## ` and `> ## ` are counted via lines starting
    # with `## ` after stripping leading `> `.
    h2_lines = [
        ln for ln in lines
        if ln.lstrip("> ").startswith("## ")
    ]
    if len(h2_lines) != 10:
        raise RuntimeError(
            f"expected 10 H2 headings (1 Drawer 入口 + 9 sections); "
            f"got {len(h2_lines)}: {h2_lines}"
        )
    # Verify sections 1..9 numeric headers all present (in body, not blockquote).
    body_h2 = [ln for ln in lines if ln.startswith("## ")]
    for n in range(1, 10):
        if not any(ln.startswith(f"## {n}.") for ln in body_h2):
            raise RuntimeError(
                f"missing body section header `## {n}.` in renumbered content"
            )

    # AC #6: length range. 2026-05-15 bumped 20000 -> 23000:
    # drawer block grew 8→17 rows (+9 sd-golden entries with twist + when-to-open
    # cells, ~2.2KB total). Body unchanged. Prior bumps: T-P0-874 16000→20000,
    # T-P0-871 14000→16000 (5→8 drawer + §1 cells), base 14000 (T-P0-845).
    n_chars = len(content)
    if not (10500 <= n_chars <= 23000):
        raise RuntimeError(
            f"content char-length {n_chars} not in [10500, 23000]"
        )

    # AC: body preserved verbatim — content must end with transformed_body
    # (no destructive edit beyond the documented Section 8 dedupe).
    if not content.endswith(transformed_body):
        raise RuntimeError(
            "transformed body not preserved verbatim at end of content"
        )

    # AC: required body landmarks still present (section indices bumped +1
    # after T-P0-847 inserted 'Twist 挖掘方法论' as new Section 2).
    required_body_fragments = [
        "<!-- META_MLSD_MAIN_HUB_20260511 -->",
        "# Meta MLSD 45-min Playbook",
        "## 1. 节奏 Timing Skeleton (45min)",
        "## 2. Twist 挖掘方法论",
        "## 3. 4 Strong Moments",
        "Strong Moment #1",
        "Strong Moment #4",
        "## 8. E4 标准 vs E5 加分上限",
        # Inline narrative reference in Section 3 must survive.
        "[Reels Home Feed (45min walkthrough, 8 段台词 verbatim) →]"
        f"(sd://{SD_REELS_GOLDEN})",
    ]
    for frag in required_body_fragments:
        if frag not in content:
            raise RuntimeError(f"body landmark missing: {frag!r}")

    # NO emoji style rule — applied to the prepended block only.
    for ch in PREPENDED_BLOCK:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1F9FF
            or 0x2600 <= cp <= 0x27BF  # Misc Symbols / Dingbats
        ):
            raise RuntimeError(
                f"emoji-like char detected in prepended block at "
                f"U+{cp:04X}: {ch!r}"
            )


def main() -> int:
    """Retrofit doc 96 with Drawer 入口 header + dedupe (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, company_id, title, content "
            "FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_documents.id={DOC_ID} not found")
            return 1
        existing_id, existing_company, existing_title, existing_content = row
        if existing_company != COMPANY_ID:
            print(
                f"[ERROR] expected company_id={COMPANY_ID}, got "
                f"{existing_company}"
            )
            return 1
        if existing_title != EXPECTED_TITLE:
            print(
                f"[ERROR] title drift: expected {EXPECTED_TITLE!r}, got "
                f"{existing_title!r}"
            )
            return 1
        print(
            f"[OK] target: id={existing_id} title={existing_title!r} "
            f"chars={len(existing_content)}"
        )

        # Strip prepended block (if sentinel present) before transforming body.
        # 2026-05-15: switched from `len(PREPENDED_BLOCK)` to body-sentinel-anchored
        # locator. The length-based strip silently truncated body Section 1 when
        # PREPENDED_BLOCK grew across runs (drawer 8→17 widening). Body sentinel
        # `META_MLSD_MAIN_HUB_20260511` is invariant; everything before it is
        # prepended-drawer scaffolding.
        BODY_SENTINEL = "<!-- META_MLSD_MAIN_HUB_20260511 -->"
        if existing_content.startswith(SENTINEL):
            body_start = existing_content.find(BODY_SENTINEL)
            if body_start == -1:
                print(
                    f"[ERROR] sentinel {SENTINEL!r} present but body sentinel "
                    f"{BODY_SENTINEL!r} not found; refusing to guess strip length"
                )
                return 1
            body_raw = existing_content[body_start:]
        else:
            body_raw = existing_content

        # Defensive sibling backlink check (cd:// + sd://).
        sibling_specs = [
            (FAMILY_TAXONOMY_DOC_ID, "Family Taxonomy"),
            (CROSS_CUTTING_DOC_ID, "Cross-cutting"),
            (RECSYS_MODELS_DOC_ID, "推荐系统核心模型"),
        ]
        for cd_id, title_frag in sibling_specs:
            r = conn.execute(
                "SELECT id, title FROM company_documents "
                "WHERE id = ? AND company_id = ?",
                (cd_id, COMPANY_ID),
            ).fetchone()
            if r is None or title_frag not in r[1]:
                print(
                    f"[ERROR] cd://{cd_id} ({title_frag}) backlink "
                    f"missing or drifted: row={r!r}"
                )
                return 1
            print(f"[OK] cd://{cd_id} verified: {r[1]!r}")

        for slug in (
            SD_REELS_GOLDEN,
            SD_TOP3_GOLDEN,
            SD_WEAPON_GOLDEN,
            SD_FRIEND_GOLDEN,
            SD_GENERIC_RECSYS,
        ):
            sd = conn.execute(
                "SELECT id, slug FROM system_designs WHERE slug = ?",
                (slug,),
            ).fetchone()
            if sd is None:
                print(f"[ERROR] sd://{slug} missing")
                return 1
            print(f"[OK] sd://{slug} verified: id={sd[0]}")

        # Build + validate new content.
        transformed = transform_body(body_raw)
        content = build_content(body_raw)
        validate_content(content, transformed)
        print(
            f"[OK] content validated: chars={len(content)} "
            f"bytes={len(content.encode('utf-8'))}"
        )

        # Idempotency gate.
        if content == existing_content:
            print(
                "[UNCHANGED] sentinel present + content byte-identical; "
                "0 writes"
            )
            print("[OK] post-validation passed")
            return 0

        if existing_content.startswith(SENTINEL):
            print(
                "[WARN] sentinel present but content drifted; will re-write"
            )

        # UPDATE.
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(content)
        conn.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, updated_at = ? "
            "WHERE id = ?",
            (content, new_hash, now, DOC_ID),
        )
        conn.commit()
        old_len = len(existing_content)
        print(
            f"[UPDATE] id={DOC_ID} old_chars={old_len} "
            f"new_chars={len(content)} delta={len(content) - old_len:+d} "
            f"hash={new_hash[:12]}..."
        )

        # Post-write re-read sanity.
        post = conn.execute(
            "SELECT content, updated_at FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()
        if post[0] != content:
            print("[ERROR] post-write content readback mismatch")
            return 1
        if not post[1].startswith(datetime.now(UTC).strftime("%Y-%m-%d")):
            print(
                f"[WARN] updated_at not today's date: {post[1]!r} "
                f"(may be timezone drift, non-fatal)"
            )
        print(f"[OK] post-write readback verified; updated_at={post[1]!r}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
