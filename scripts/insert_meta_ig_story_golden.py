"""
Insert meta-ig-story-golden system_design row (T-P0-883).

Q10 IG Story Recommendation, top-9 batch, kou-bo-gao only.
Template locked from anchors id=45 (meta-fb-newsfeed-golden) and id=46
(meta-yelp-restaurant-golden); see scripts/mlsd_top9_spec.md.

Dominant twist: author-tray-not-story granularity reframe -- the unit of
ranking is the author-tray, NOT the individual story. Users consume by
author (watch all of Alice's stories then jump to Bob's), so per-story
scoring solves the wrong granularity. Three interacting twists:
skip-to-next-author negative + dwell-per-story label, within-tray
autoregressive sequencing (two-level ranking: author-tray ordering across
authors + story sequence within tray), and close-friend prior carries
across days even though stories don't (cold-start cure since 24h hard
expiry breaks per-story history but author-level priors persist).

Backfill note: this script reconstructs an idempotent seed for an existing
DB row that was inserted during the 2026-05-14 autorun (T-P0-883). The
autorun agent inserted the row and marked the task completed via task_db
but timed out before committing the seed script -- recovery committed here
to satisfy Invariant 3 (every DB content row backed by a git-tracked
idempotent seed). Source-of-truth is now this script.

Idempotent: skips insert if slug already exists.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SLUG = "meta-ig-story-golden"
TITLE = "Meta MLSD Golden Example: IG Story Recommendation (口播稿 only, 45min walkthrough)"
SUBTITLE = "Author-tray granularity reframe + skip-to-next-author negative + within-tray autoregressive sequencing + close-friend cold-start cure"
DISPLAY_ORDER = 209


OVERVIEW = """# IG Story Recommendation -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Rank a personalized IG Story tray-of-trays for a user opening the Stories rail, optimizing for **author-level engagement-and-retention** -- progression through an author's full story sequence + next-day return -- where the **unit of ranking is the author-tray, not the individual story**. Any design scoring stories independently is solving the wrong granularity.

**Input per request**: user_id + session context (time-of-day, device, last-rail-open marker) + active story inventory after the 24h hard window + follow-graph (friends, close-friends, family) + follow-adjacent (mutual-overlap). Per-author features: relationship strength, historical per-author dwell, within-tray story count. Per-story features (used inside within-tray sequencing only): cover-embedding, within-tray recency, content-type.

**Output**: ~30-60 visible author-trays on the rail (left-to-right) + within-tray play order per author. Cross-tray ranker emits author-level scores for rail position; per-author sequence model decides within-tray play order.

**Scale anchor**: ~500M DAU on Stories, ~300-1000 eligible stories per request after 24h + follow-graph gate, p99 ~80ms rail-rank + ~40ms within-tray sequence. Methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution shape.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- Author-tray-not-story granularity reframe** -- Generic ranking treats the story as the unit (per-story score, then sort). But IG users **consume by author**: watch all of Alice's stories, swipe to Bob. The unit of ranking is the **author-tray**, not the story. Not a feature tweak -- it changes the **architecture**: per-story deep rankers solve the wrong granularity, and item-level two-tower retrieval flattens the author-level signal. Model class is **two-stage**: cross-tray ranking decides which authors surface in what rail order; within-tray sequencing decides per-story play order within each. Interacts with #3 (within-tray sequencing is the natural follow-up once author-tray is locked) and #2 (skip-to-next-author negative is uniquely tied to this granularity).

**Twist 2 -- Skip-to-next-author negative + dwell-per-story label** -- Generic implicit-feedback uses click as positive and non-impression as negative. Stories has a uniquely strong implicit negative tied to tray granularity: **skip-to-next-author** (user swipes mid-tray to the next author) -- a clean signal THIS tray is misordered against current interest. Positive is **per-story dwell** within the chosen tray (every story auto-plays, so click is meaningless). Label: `tray_positive = full_tray_watched OR mean(dwell/content_length) > 0.6`; `tray_negative = skip-to-next-author within 1.5s of tray entry`. Interacts with #1 (on a per-story ranker, skip-to-next-author collapses into longer non-impression noise).

**Twist 3 -- Within-tray autoregressive sequencing** -- Once a user enters Alice's tray, the **order of Alice's stories matters and is its own ranking sub-problem**. Default is reverse-chronological; the model can learn Alice's 5pm big-event reveal should play before her 3pm "good morning" story for THIS viewer. Implementation: a **lightweight per-author autoregressive sequence model** running AFTER cross-tray ranking, labeled on within-tray dwell-completion. NEW vs cd94 (which flags author-tray granularity but leaves within-tray ordering unspecified). Interacts with #1 (within-tray ordering is the natural extension once author-tray granularity is the chosen unit).

**Twist 4 -- Close-friend prior carries across days even though stories don't (cold-start cure)** -- 24h hard expiry means **no per-story interaction history persists** -- every day is cold-start at the story level. But **author-level priors persist**: close-friend / family / high-historical-dwell relationships are stable across days. That is the cold-start cure. Interacts with #1 (the cure works ONLY because the granularity is the author-tray -- on a per-story ranker, no persistent unit exists to attach a prior to)."""


VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min **(driven by Twist 1)**
"Two intrinsic specialties of IG Story drive the design -- **author-tray is the unit of ranking** (not the story) and **skip-to-next-author is the dominant implicit negative**. They interact: the negative only exists because the granularity is the tray; on a per-story model it collapses into noise. Scale: ~500M DAU on Stories, ~300-1000 eligible stories per request after the 24h + follow-graph gate, p99 ~80ms rail-rank + ~40ms within-tray sequence. Choosing not to deep-dive on ingest cache or 24h-expiry GC; can surface on probe." Sub-structure: data/label, retrieval, two-stage ranking, eval. Yes/no close.

### Data / Label 3-12 min **(driven by Twist 2, interacts with Twist 1)**
Label is where this design separates from generic ranking. Positive is **tray-positive**: `tray_positive = full_tray_watched OR mean(dwell/content_length) > 0.6`. Dominant **negative** is **skip-to-next-author within 1.5s of tray entry** -- a clean misordered-tray signal that exists only because Twist 1 makes the tray the unit. **I pick** tray-level positives over story-level positives **because** consumption is tray-by-tray (users do not pick-and-choose stories across authors); **costs**: a tray-aggregation job over the impression stream + per-cohort calibration of the 1.5s skip threshold; **switches to** story-level positives only if a within-tray click-out pattern (e.g., reshare) emerges and dominates dwell. Per-story dwell is preserved as the within-tray sequencing label for Twist 3, NOT as the cross-tray positive. Click is too noisy here -- stories auto-play, so click is meaningless; tap-forward and tap-back are within-tray signals, not cross-tray.

### Retrieval 12-18 min **(driven by Twist 4, interacts with Twist 1)**
Candidate construction is **hard-filter-first, not similarity-first**: (1) **24h hard expiry** removes stale stories -- **eligibility, not a feature** (cd94 anti-pattern: do not fold recency into ranker score); (2) **follow-graph + close-friends list** -- only followed authors + close-friends + family enter, with follow-adjacent (mutual-overlap) as a secondary source quota-capped at ~10% of the rail; (3) **per-author tray rollup** -- collapse N stories per author into one tray entity carrying `story_count`, `latest_post_ts`, `mean_content_type` as tray-level features. **I pick** hard-filter + tray-rollup over unified two-tower **because** Twist 1's bridge entity is the author-tray, not an item-vector; two-tower would flatten the per-author story-count + recency-distribution that feed Twist 3's sequence model; **costs**: tray-rollup job + Thompson-sampled follow-adjacent quota; **switches to** two-tower only if tray-rollup engineering becomes prohibitive AND within-tray sequencing is dropped. Cold-start uses **author-level relationship priors** (Twist 4) because 24h expiry means story-level history can't persist.

### Cross-tray Ranking 18-25 min **(driven by Twists 1 + 2, interacts with Twist 4)**
Cross-tray ranker is **multi-task** {p_tray_positive, p_skip_to_next_author, p_close_friend_dwell} sharing a transformer backbone, scored by `S_tray = w1*p_tray_positive - w2*p_skip + w3*p_close_friend_dwell`. Fusion weights are **learned** in offline counterfactual replay against tray-positive delta + skip reduction. Twist-4's relationship prior enters as a **multiplier** on the fused score for close-friend / family authors -- not a feature -- because the effect compounds multiplicatively (close friends with low predicted engagement still surface above strangers with equal engagement). **I pick** prior-as-multiplier over prior-as-feature **because** the structural effect is multiplicative; **costs**: per-cohort prior-strength tuning + lower-bound to prevent saturation; **switches to** prior-as-feature only if the multiplier monopolizes the rail (mitigate via per-cohort close-friend tray cap).

### Within-tray Sequencing 25-32 min **(driven by Twist 3, interacts with Twist 1)**
After cross-tray ranking, a **per-author autoregressive sequence model** decides within-tray order. Default is reverse-chronological; model overrides when warranted. Input per story: cover-embedding, time-of-post, content-type, within-tray dwell history for THIS user-author pair. Label: within-tray-dwell-completion. Model class: small **GRU or 2-layer transformer** conditional on tray history, NOT a per-story deep CNN over the image (cover IS the auto-play preview, so cover-embedding suffices). **I pick** per-author sequence model over flat per-story ranker **because** within-tray context (same-author same-tray) is the dominant signal; **costs**: ~40ms additional inference call in the rail budget; **switches to** chronological default only if lift over reverse-chronological is < 2%.

### Eval 32-40 min **(driven by Twists 1 + 2 + 4)**
Three surfaces: (1) **offline sliced metrics** -- tray-positive and skip rate per {relationship-tier x time-of-day x within-tray-story-count}; sliced because Twists 2 and 4 both vary heavily by tier. **I pick** sliced metrics over flat AUC **because** the close-friend multiplier would dominate aggregate AUC and mask skip-rate regressions for stranger trays; **costs**: a per-slice dashboard + tier-imbalanced minimum-sample-size guard. (2) **Counterfactual replay with IPS correction** before A/B -- logged rail order is heavily biased toward what prior models surfaced, so IPS-weighted replay corrects exposure bias on tray-positive. (3) **Online A/B with metric = next-day return + per-author tray completion**, NOT raw rail-dwell -- short-term rail-dwell can be gamed by surfacing dramatic stranger content, but next-day return is the alignment-testable signal. Within-tray sequence model has its own slice: dwell-completion per content-type, because videos play longer than photos.

### Wrap 40-45 min
Top 3 risks: (1) **close-friend prior monopolization** -- the multiplier can saturate to close-friends-only when a user has many active close-friend stories; mitigate via per-cohort cap on close-friend tray count + Thompson-sampled follow-adjacent diversity floor (~10% rail slot); (2) **skip label leakage to tray length** -- the 1.5s skip window correlates with stories-per-tray (long trays get skipped more), so the negative can leak into "long trays bad" rather than "misordered trays bad"; mitigate via per-tray-length normalization + adversarial slice eval; (3) **per-author sequence model overfit** -- the GRU overfits to high-volume authors and underfits to thin ones; mitigate via per-author sample weighting + cohort-prior fallback for low-history user-author pairs. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 reframe -- "the unit of ranking is the author-tray, not the story; a per-story deep model is solving the wrong granularity"
- **SM #2 (12-15 min)**: Twist 2 -- "skip-to-next-author is a uniquely strong implicit negative that only exists because the unit is the tray; on a per-story ranker it collapses to noise"
- **SM #3 (25-28 min)**: Twist 3 -- "within-tray sequencing is a separate sub-ranking problem with its own autoregressive model; big-event-first beats chronological-first per author"
- **SM #4 (38-42 min)**: zoom-out + top 3 risks above; mention close-friend prior cap + per-tray-length skip normalization as the production-scar headlines

## §5 Drift recovery + 3-way handoff

**Drift to per-story ranking**: "Let me return to the ML core -- the unit of ranking here is the author-tray, not the story, because IG users consume by author. Per-story score-then-sort is the wrong granularity; within-tray ordering is a separate sub-ranking step running AFTER the cross-tray decision."

**Asks scale early**: "~500M DAU on Stories, ~300-1000 eligible stories per request after the 24h + follow-graph gate, p99 ~80ms rail-rank + ~40ms within-tray; ML decisions don't shift with scale, only ingest cache and 24h-expiry GC do."

**Asks cold-start prematurely**: "Park new-user cold-start until I get through retrieval -- author-level relationship priors (close-friend, family, mutual-overlap) handle most of it because story-level history can't persist past the 24h window, but author-level history does."

**Asks why not unified two-tower**: "Two-tower flattens the author-tray entity that is Twist 1's bridge; tray-level features feed BOTH cross-tray ranking AND within-tray sequencing -- two-tower loses that handoff."

**Handoff (3-way)**: "Want me to deepen the **author-tray rollup + cross-tray multi-task ranker + close-friend prior multiplier**, the **within-tray autoregressive sequence model + per-author GRU + cover-embedding features**, or the **skip-to-next-author label engineering + per-tray-length normalization + IPS replay eval**?\""""


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat(timespec="seconds")

    exists = cur.execute(
        "SELECT id FROM system_designs WHERE slug=?", (SLUG,)
    ).fetchone()

    if exists:
        cur.execute(
            """UPDATE system_designs
               SET title=?, subtitle=?, overview=?, verbal_outline=?,
                   display_order=?, updated_at=?
               WHERE slug=?""",
            (TITLE, SUBTITLE, OVERVIEW, VERBAL_OUTLINE, DISPLAY_ORDER, now, SLUG),
        )
        action = "UPDATED"
    else:
        cur.execute(
            """INSERT INTO system_designs
                 (slug, title, subtitle, overview, verbal_outline,
                  display_order, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (SLUG, TITLE, SUBTITLE, OVERVIEW, VERBAL_OUTLINE, DISPLAY_ORDER, now, now),
        )
        action = "INSERTED"

    conn.commit()

    row = cur.execute(
        """SELECT id, slug, length(overview), length(verbal_outline),
                  length(overview)+length(verbal_outline) AS total
           FROM system_designs WHERE slug=?""",
        (SLUG,),
    ).fetchone()
    print(f"{action} id={row[0]} slug={row[1]} overview={row[2]} verbal={row[3]} total={row[4]}")
    conn.close()


if __name__ == "__main__":
    main()
