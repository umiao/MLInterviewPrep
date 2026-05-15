"""
Insert meta-spotify-music-golden system_design row (T-P2-889).

Q11 Spotify Music Recommendation, top-9 batch, kou-bo-gao only. Template locked
from anchors id=45 (meta-fb-newsfeed-golden) and id=46 (meta-yelp-restaurant-
golden); see scripts/mlsd_top9_spec.md. Tier-3 (non-Meta) per 2026-05-14 user
directive.

Dominant twist: relisten is positive, not redundant -- a user playing the same
song 50 times is a 5-star signal, not saturation. This inverts the dedup logic
standard in video / article rec. Interacting twists: audio embedding from
spectrogram as the cold-start lever (metadata is too coarse for ~60k new tracks
per day); session mood coherence as autoregressive constraint (sequential model
over session prefix, NOT pointwise scoring); skip-rate (<30s) as primary
negative label (play-count is gameable by auto-play queue).

Idempotent: skips insert if slug already exists.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

OVERVIEW = """# Spotify Music Recommendation -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Given user u + (session context, surface), return next-track (Radio / Autoplay) OR ranked playlist (Discover Weekly / Daily Mix) -- product objective is **play-to-completion** (PTC: ≥30s OR ≥80% of track) with **skip-within-30s as strong negative**. NOT play-count (auto-play queue inflates it) and NOT click. Music has one structural specialty: **relisten is positive** -- same song 50 times is a 5-star signal, not saturation -- so **NO post-ranking dedup**. Spotify is not a Meta product; structural twists transfer but Meta signal hierarchies do not.

**Input per request**: user_id + session context (last ~10-50 tracks + derived mood vector, time-of-day, device, geo) + (optional) explicit seed (track / artist / playlist). Long-horizon user preference is a **residual within the session-conditioned pool**, not the primary lever.

**Output**: next-track (Radio) OR ranked playlist (Discover Weekly ~30, Daily Mix ~50, Radio infinite-stream), per-track provenance preserved (audio-sim / CF / new-release burst) for diversity policy + cold-track exposure monitor. Downstream: client audio engine; reward is PTC vs early-skip.

**Scale anchor**: ~500M MAU, ~100M tracks (~60k new per day, long-tail), p99 ~100ms for Radio next-track, batch ~6h overnight for Discover Weekly. Methodology lives in `cd://96`; this row owns only the solution shape.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- Relisten is positive, not redundant (inverts dedup logic)** -- Generic video / article rankers dedup consumed items. WRONG for music: same song played 50 times is a 5-star signal, not saturation -- the single property distinguishing music from nearly every other rec domain. **Correct**: NO post-ranking dedup; recently-played tracks stay in pool with positive prior; relisten-frequency-30d is a positive feature. Interacts with #2 (works only when content embedding surfaces relistenable AND fresh tracks together) and #3 (relisten within mood stays in mood; cross-mood relisten can violate coherence).

**Twist 2 -- Audio embedding from spectrogram is the cold-start lever (metadata too coarse)** -- Metadata (artist / genre / era / BPM) is too coarse for ~60k new tracks per day. A new indie folk track shares artist=unknown, genre=folk with 50k others. **Correct**: CNN over log-mel-spectrogram → 128-256d audio embedding, indexed at upload time with **zero playcount required**; metadata as complementary bias. NEW vs cd94 (doesn't frame as load-bearing cold-start primitive). Interacts with #1 (surfaces relistenable + fresh together) and #4 (audio-nearest neighbor is primary substitute on skip).

**Twist 3 -- Session mood coherence as autoregressive constraint, NOT pointwise scoring** -- Pointwise ranker against user-static profile treats rock → classical → rock as fine when each candidate matches profile, but session-abandon spikes when mood jumps. **Correct**: Transformer over session prefix -- last N (~20) tracks → per-candidate next-track logit conditioned on prefix. NEW vs cd94. Interacts with #1 (sequential context absorbs cross-mood relisten) and #4 (skip-within-session IS the mood-coherence diagnostic).

**Twist 4 -- Skip-rate (<30s) as primary negative label, NOT play-count** -- Play-count is gameable by auto-play queue loops. **Correct**: primary positive is PTC (≥30s OR ≥80% of track), primary negative is skip-within-30s; play-count is noise floor. NEW vs cd94. Interacts with #3 (early-skip mid-session IS the mood-jump diagnostic) and #1 (a track skipped 3 times then played to completion 50 times has both high skip AND high relisten -- track is bimodal, not noise)."""


VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min **(driven by Twist 1)**
"Music rec has one specialty that inverts almost every other rec domain: **relisten is positive, not redundant** -- same song 50 times is a 5-star signal, not saturation. NO post-ranking dedup. Second: **audio embedding from spectrogram is the cold-start lever** -- metadata too coarse for ~60k new tracks per day. Third: **session mood coherence is an autoregressive constraint** -- transformer over session prefix, not pointwise. Fourth: **skip-rate <30s is the primary negative** -- play-count is gameable by auto-play queue. Scale: ~500M MAU, ~100M tracks." Sub-structure: data/label, audio+CF retrieval, sequential ranking + mood coherence, diversity policy + cold-start, eval. Yes/no close.

### Data / Label 3-12 min **(driven by Twist 4, interacts with Twist 1)**
Signals: **PTC** (≥30s OR ≥80% of track) = positive, **skip <30s** = strong negative, **like / save / add-to-playlist** = explicit positive, **relisten-frequency-30d** = positive feature (Twist 1, NOT fatigue flag). **I pick** PTC + early-skip over play-count **because** play-count is gameable by auto-play queue -- counts inflate without active choice -- while PTC binds prediction to active engagement and early-skip surfaces mismatches actively rejected; **costs**: per-track-duration normalization (3-min pop vs 15-min classical), label-delay on within-session future skips, sparsity on infrequent listeners; **switches to** play-count only on cold-start tracks. Features: per-track (audio embedding 128-256d, metadata: artist / genre / era / BPM / energy / valence, popularity quantile); per-user (long-horizon genre + artist preference, recent skip patterns, time-of-day mood histogram, **per-track relisten-count-30d**); per-session (last N tracks, derived mood vector, surface).

### Audio + CF retrieval 12-20 min **(driven by Twist 2, interacts with Twist 1)**
Three-source candidate gen. (a) **Audio-embedding ANN** -- CNN over log-mel-spectrogram → 128-256d, HNSW M=32 ef_construction=200, indexed at upload time so new-artist tracks enter with zero playcount. (b) **CF embedding ANN** -- ALS or two-tower over (user, track, PTC), strong on popular catalog, weak on long-tail. (c) **Relisten-pool injection** -- recently-played tracks with positive PTC stay in pool with positive prior (NO dedup per Twist 1); listen-history is a bonus source, not a blacklist. **I pick** audio + CF + relisten-pool merge over CF-only **because** CF has hard cold-start ceiling (~60k new tracks per day, zero playcount), AND CF-only would dedup recently-played tracks, suppressing the relisten-positive signal; **costs**: weekly CNN refit + spectrogram prep + dual-index maintenance; **switches to** CF-only on very short tracks (<30s), voice memos, mis-tagged podcasts.

### Sequential ranking + mood coherence 20-30 min **(driven by Twist 3, interacts with Twists 1 + 2)**
**Transformer over session prefix** -- input: last N (~20) tracks' (audio_emb + metadata + PTC), candidate: each pool track's (audio_emb + metadata + user-affinity + relisten-count-30d), output: per-candidate next-track logit. NOT pointwise on user-static features. **I pick** sequential autoregressive over pointwise GBDT **because** mood coherence is the load-bearing within-session signal -- pointwise lets the loss treat "rock → classical → rock" as fine when each candidate matches user-static profile, but session-abandon spikes when mood jumps and GBDT loss cannot see why; **costs**: ~10x ranker latency vs GBDT (handled by top-200 truncation + per-session KV-cache reuse); **switches to** GBDT pointwise only on Discover Weekly batch refresh where session context is absent (fall back to long-horizon profile + audio-CF affinity).

### Diversity policy + cold-start 30-36 min **(driven by Twist 1, interacts with Twists 2 + 3)**
**No post-ranking dedup** -- recently-played tracks stay in pool. BUT: **mood-coherence regularizer** caps cross-mood injection rate (Twist 3) AND **new-track exposure quota** ensures ~10-20% of slate is audio-cold tracks to prevent CF-popular collapse (Twist 2). **I pick** explicit per-surface quota over diversity-as-feature **because** dedup-as-default is wrong for music and per-surface tunable quota lets Discover Weekly favor exploration (high new-track, low relisten-bias) vs Radio favor mood-coherent autoplay (low new-track, high relisten-bias on session-mood tracks) without retraining; **costs**: per-surface quota maintenance + cold-track exposure-fairness monitor; **switches to** uniform quota only on premium ad-free surfaces with fixed exploration budget. **Cold-start** new tracks (<14d): audio-embedding ANN at upload time + per-surface new-track quota + quality-gated burst capped per-track-per-day. **Cold-start** new users (<30d): audio-affinity backoff from onboarding seed + popularity prior; transformer prefix backs off to user-prompt seed when prefix is empty.

### Eval 36-45 min **(driven by Twists 3 + 4)**
Three surfaces sliced: (1) **per-surface PTC + skip-rate + session-length** -- Radio (skip-rate + session-length-until-abandon), Discover Weekly (first-week PTC + save-rate), On-Demand search (query-completion + first-play PTC), sliced by **mood-class + cold-track-quota bucket + relisten-bucket + user-tenure**; (2) **counterfactual replay with IPS** -- auto-play queue actions are NOT counterfactually neutral, IPS-weight by candidate-pool exposure; (3) **cluster-randomized A/B by user** (no friend-network leakage like Event Rec). **I pick** mood + cold-track + relisten + tenure slicing over flat top-line **because** aggregate skip-rate masks three patterns -- cold-start track skip spikes while popular improves (audio regressed), mood-coherence breaks show in session-length not per-track skip, relisten-saturation shows in per-track outliers; **costs**: per-slice sample-size guard + mood-class labeling; **switches to** flat top-line only on infra-only A/B. Top 3 risks: (1) **CF popularity collapse** as audio model regresses -- cold-track quota dashboard + audio offline recall monitor. (2) **mood-classifier drift** as genre boundaries shift (lo-fi / hyperpop emerged); quarterly mood-taxonomy refresh. (3) **relisten saturation pathology** -- runaway positive loop on one track; cap per-track relisten boost above per-user threshold + per-user track-entropy monitor. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 -- "Music has one feature that distinguishes it from almost every other rec domain: relisten is positive, not redundant. Same song 50 times = 5-star signal, not saturation -- inverts dedup logic standard in video and article rec"
- **SM #2 (10-12 min)**: Twist 4 + #1 -- "Primary positive is play-to-completion, primary negative is early-skip; play-count is gameable by auto-play queue. Relisten count is a positive feature, not a saturation flag"
- **SM #3 (22-25 min)**: Twist 3 + #1 -- "Session mood coherence is an autoregressive constraint -- transformer over session prefix, not pointwise. Pointwise lets rock → classical → rock slip through because each candidate matches user-static profile"
- **SM #4 (38-42 min)**: zoom-out + top 3 risks (CF popularity collapse / mood-classifier drift / relisten saturation pathology) + IPS counterfactual replay as auto-play-queue bias correction

## §5 Drift recovery + 3-way handoff

**Drift to CF / why-not-pure-CF**: "CF alone has a hard ceiling -- ~60k new tracks per day are long-tail with zero playcount. Pure CF can't enforce session mood coherence (no notion of prefix), and dedup-by-default would suppress the relisten-positive signal. **I pick** audio + CF + sequential transformer **over** pure CF **because** music's three load-bearing properties (relisten-positive, audio-cold-start, mood-coherence) each need a primitive CF cannot provide -- different architecture, not refinements."

**Asks scale early**: "~500M MAU, ~100M tracks (~60k new per day), p99 ~100ms Radio next-track, batch ~6h overnight for Discover Weekly. ML decisions don't shift with QPS, only HNSW shard layout, CNN throughput, and transformer KV-cache budget per session do."

**Asks cold-start prematurely**: "Two cold-starts -- track-level (<14d) via audio-embedding ANN at upload time + per-surface new-track quota + quality-gated burst capped per-track-per-day; user-level (<30d) via audio-affinity backoff from onboarding seed + popularity prior. Park until candidate gen and ranker are laid out."

**Why-not-deep-end-to-end**: "Two-tower deep over (user, track) loses two load-bearing primitives -- doesn't enforce mood coherence (no prefix) and doesn't separate audio-cold-start from CF-popular paths cleanly. **I pick** explicit cascade (audio + CF + relisten-pool → sequential transformer → per-surface quota) **over** end-to-end deep **because** each layer A/B's independently: CNN refit, transformer prefix length, per-surface quota all tunable separately."

**Handoff (3-way)**: "Want me to deepen the **audio CNN spectrogram embedding + cold-start ANN indexing at upload time**, the **transformer sequential ranker + session-prefix KV-cache reuse**, or the **per-surface quota policy + IPS counterfactual replay for auto-play-queue bias correction**?\""""


ROW = {
    "slug": "meta-spotify-music-golden",
    "title": "Meta MLSD Golden Example: Spotify Music Recommendation (口播稿 only, 45min walkthrough)",
    "subtitle": "Relisten-as-positive (inverts dedup) + audio-spectrogram embedding for cold-start + session-mood autoregressive ranker + skip-rate as primary negative label",
    "overview": OVERVIEW,
    "verbal_outline": VERBAL_OUTLINE,
    "display_order": 260,
}


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat(timespec="seconds")

    exists = cur.execute(
        "SELECT id FROM system_designs WHERE slug=?", (ROW["slug"],)
    ).fetchone()
    if exists:
        print(f"SKIP {ROW['slug']} already exists at id={exists[0]}", file=sys.stderr)
        conn.close()
        return 0

    cur.execute(
        """
        INSERT INTO system_designs
            (slug, title, subtitle, overview, verbal_outline,
             display_order, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ROW["slug"],
            ROW["title"],
            ROW["subtitle"],
            ROW["overview"],
            ROW["verbal_outline"],
            ROW["display_order"],
            now,
            now,
        ),
    )
    new_id = cur.lastrowid
    conn.commit()

    row = conn.execute(
        """SELECT id, slug, length(overview), length(verbal_outline),
                  length(overview)+length(verbal_outline) AS total
           FROM system_designs WHERE id=?""",
        (new_id,),
    ).fetchone()
    print(
        f"OK id={row[0]} slug={row[1]} overview={row[2]} verbal={row[3]} total={row[4]}"
    )
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
