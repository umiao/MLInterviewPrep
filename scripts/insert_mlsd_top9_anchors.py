"""
Insert N1 (Q9 FB News Feed) + N1.5 (Q8 Yelp) anchor system_design rows for
Meta MLSD 13-question family top-9 batch (komantxe top9).

These two rows are the manual calibration anchors — best-case (Q9, Meta-native,
twist-dense) + worst-case (Q8, non-Meta, sparse). Remaining 7 problems run
through autonomous_run.sh inheriting this exact template.

Template (locked):
  overview:        §1 problem definition + §2 dominant twist + 2-4 interacting constraints
  verbal_outline:  §3 twist-threaded solving (6 sections, each opens with `(driven by Twist N · interacts with M)`)
                   + §4 SM slot map (light, 4 bullets)
                   + §5 drift-recovery + 3-way handoff
Target length: 4k-5.5k chars total per row.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# =====================================================================
# N1 — Q9 FB News Feed (BEST-CASE ANCHOR — Meta-native, twist-dense)
# =====================================================================

Q9_OVERVIEW = """# FB News Feed -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Rank a personalized feed of heterogeneous items (status / photo / video / link / milestone) drawn from multi-source candidate generation (friends / groups / pages), optimizing for **Meaningful Social Interaction (MSI)** -- a weighted composite where close-friend comments dominate passive likes from acquaintances -- not raw engagement.

**Input per request**: user_id + session context (time, device, last-seen marker) + recent on-platform interaction history (last N-day window). At candidate-gen time pulls O(thousands) of items across friend network (1-hop + 2-hop with decay), groups joined (recency-weighted), pages followed (engagement-recency).

**Output**: ordered list of ~25 items per visible page + prefetch buffer for next page; each item carries a fused score = product of N task heads with MSI-tuned per-source weights, multiplicatively downranked by integrity admission cascade.

**Scale anchor**: ~3B DAU, ~10k candidate items per user per request, ranker p99 ~80ms, candidate gen ~30ms, integrity classifier inline. Methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution shape.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- MSI reframe, not engagement** -- Generic news-feed ranking optimizes for click / dwell / engagement, but Meta's stated product objective is **MSI**: a `like` from a stranger is worth less than a `comment` from a close friend. This is not a feature-weight tweak -- it changes the **label hierarchy at training time** and the **task-head fusion weights at score time**. Any design that flattens this to `predict click` is fighting the company's product direction. Interacts with #2 (per-source MSI weights differ) and #4 (integrity reweights conditional on MSI prior).

**Twist 2 -- Heterogeneous content + multi-source candidate gen** -- Friends / groups / pages have different retrieval logic, different intrinsic engagement priors, and different MSI semantics. A `share` from a friend means something different than a `share` from a page. Pure cross-source ranking flattens this; the fix is **per-source retrieval + cross-source learned blending weights with source-of-origin preserved as a one-hot ranker feature** so per-source recall is independently debuggable. Interacts with #1 (per-source MSI head weights).

**Twist 3 -- Close-friend recency override (the 2022 close-friends-tab regime)** -- For close-friend / family relationships, engagement-history alone is too coarse to surface time-critical updates. Meta exposed an explicit **close-friends-tab that bypasses the algo feed and reorders reverse-chronologically** for that subset. Architecturally this is a **dual-feed render path** + a model-side **soft override** in the main feed when close-friend signal exceeds threshold AND item is < 6h old. Interacts with #1 (close-friend label already inflates MSI weight) -- correlated, not orthogonal.

**Twist 4 -- Integrity downranking is a shared-scale admission multiplier** -- Misinfo / clickbait / borderline-policy items are **multiplicatively downranked** via a calibrated shared-scale P(integrity-violation), not hard-removed. Structurally this is the **same cascade pattern as Weapon Ads (cd://96 referenced)** but operates as a multiplier on the fused engagement score, not as a binary admission gate. Interacts with #1 (sometimes integrity multiplier drives an MSI-positive item down, and that's correct -- the platform value is alignment, not engagement)."""


Q9_VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min
"Two intrinsic specialties of News Feed drive most of my design -- **MSI as label hierarchy** and **integrity as shared-scale downrank multiplier**. Both interact: the close-friend signal in MSI correlates with integrity-safe content, and that correlation is structural, not coincidental. Scale: ~3B DAU, ~10k candidate items per request, p99 budget ~80ms ranker + ~30ms candidate gen. I'm choosing not to deep-dive on serving cache or shard layout, which I'm happy to surface on probe." Sub-structure announce: 4 parts -- data/label, retrieval, ranking, eval. Yes/no close.

### Data / Label 3-12 min **(driven by Twist 1, interacts with Twist 2)**
Label is where this design separates from generic ranking. I'm not predicting `click`. I'm predicting a **multi-task vector** {p_click, p_comment, p_like, p_share, p_dwell, p_reaction_type} where the **score-fusion weights are tuned to MSI**, not engagement. A close-friend comment is weighted ~10x-20x a 2-hop acquaintance like. **I pick** learned per-source fusion weights over a hard-coded MSI table, **because** a static table goes stale as user behavior shifts; **costs**: monthly re-tune job + drift alert when close-friend-comment weight drops > 10%; **switches to** a hard-coded table only if drift instability dominates -- empirically it does not. Per-source weight differentiation (Twist 2): group `share` differs from friend `share`; per-source heads share their transformer backbone and split at the final layer.

### Retrieval 12-20 min **(driven by Twist 2)**
Candidate gen is **multi-source parallel, not unified**. Friend-network is 1-hop + 2-hop with strength decay; groups-joined is recency-weighted within active groups; pages-followed is engagement-recency-weighted. Each source emits ~500-2000 candidates with **source-of-origin one-hot preserved** as a ranker feature so per-source recall is debuggable independently. Cross-source blending is **not** a single embedding cosine -- it's a **per-source ceiling quota** (e.g., max ~60% friends, max ~25% groups, max ~15% pages) tuned online via Thompson sampling against MSI delta. Cold-start at user level uses entity-overlap (school / work / mutuals). **Switches to** unified two-tower retrieval only if per-source debuggability becomes non-critical -- not at this product stage.

### Ranking 20-30 min **(driven by Twists 1 + 2, interacts with Twist 4)**
Ranker is **multi-task with per-source heads sharing a transformer backbone**, scored by `MSI(s) = Sum_k w_k(source) * p_k`. Critical: the fusion weights `w_k(source)` are **learned**, not hand-set -- offline counterfactual replay optimizes against MSI delta. Then Twist 4 enters: integrity multiplier multiplies the fused score: `final = MSI(s) * (1 - p_integrity)^alpha`. This is structurally the Weapon Ads cascade but as multiplicative downrank, not admission gate. **I pick** multiplicative-downrank over hard-cut **because** the integrity classifier itself is calibrated and operating in a probability space; hard-cut loses the calibration; **costs**: alpha tuning on a weekly cadence; **switches to** hard-cut only if the integrity model's calibration breaks empirically.

### Close-friend handling 30-35 min **(driven by Twist 3, interacts with Twist 1)**
For the close-friends-tab, the algo doesn't run -- reverse-chronological with integrity multiplier still applied. For the main feed, close-friend items get a **soft override**: a learned bypass head adds a relevance boost when close-friend signal exceeds threshold AND item < 6h old. This solves the "I missed my sister's update because Reels saturated my feed" failure mode. **I pick** a soft bypass head over a hard quota **because** hard quotas are brittle when the close-friend list is empty or skewed; **switches to** quota only if bypass head misuse becomes adversarial.

### Eval 35-40 min **(driven by Twists 1 + 4)**
Three surfaces: (1) **offline sliced metrics** -- MSI delta per {content_type x source x close-friend-tier}, not flat AUC, because the dominant twist is hierarchical; (2) **counterfactual replay with IPS correction** before A/B, because logged feed is exposure-biased toward what prior models surfaced; (3) **long-term holdout** (8-week hold-out cohort) for MSI-vs-engagement drift -- short-term A/B can show engagement gain from clickbait that the long-term MSI cohort rejects. Specifically targeting the MSI long-term vs short-term engagement divergence -- this is where the product alignment is actually testable.

### Wrap 40-45 min
Top 3 risks: (1) **MSI weight staleness** -- fusion weights drift as platform demographics shift; mitigate with monthly re-tune + alert on close-friend-comment weight drop > 10%; (2) **integrity prior collapse** -- if integrity classifier becomes overconfident, multiplier saturates near 0 for borderline content; mitigate with calibration audit + lower-bound on multiplier; (3) **close-friend bypass adversarial** -- users gaming declared close-friend list to boost own content; mitigate via implicit close-friend signal (interaction history) over declared list. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 reframe -- "MSI vs engagement is not a feature weight tweak, it's a label hierarchy change"
- **SM #2 (12-15 min)**: Twist 1+2 interaction -- multi-task heads with per-source learned fusion weights; the per-source split is non-obvious senior signal
- **SM #3 (25-28 min)**: Twist 4 -- "integrity downrank is a multiplier on shared P-scale, structurally the same cascade pattern as Weapon Ads cd://96 references"
- **SM #4 (35-40 min)**: zoom-out + top 3 risks above; mention MSI long-term holdout as the alignment-testability point

## §5 Drift recovery + 3-way handoff

**Drift to generic ranking**: "Let me return to the ML core -- for News Feed the question is not p(click), it's MSI(s) = Sum_k w_k(source) * p_k with learned per-source fusion weights, because that is where Meta's stated product objective actually lives."

**Asks scale early**: "~3B DAU, ~10k candidates per request, p99 split 30ms candidate gen / 80ms ranker; ML decisions don't shift with QPS, only sharding / cache strategy does."

**Asks cold-start prematurely**: "Park new-user cold-start until I get through retrieval -- entity-overlap (school / work / mutuals) handles most of it once I've explained the 1+2-hop friend graph traversal and the multi-source quotas."

**Asks why not unified two-tower**: "Two-tower flattens the source-of-origin signal that I need for per-source recall debuggability and per-source MSI weight differentiation; **I pick** per-source parallel retrieval **over** unified two-tower **because** per-source debuggability is more valuable than embedding-space coherence at this product stage."

**Handoff (3-way)**: "Want me to deepen the **MSI multi-task head + learned per-source fusion weights**, the **multi-source candidate gen with Thompson-sampled quotas + source-of-origin one-hot**, or the **integrity multiplier cascade + IPS counterfactual replay eval**?\""""


# =====================================================================
# N1.5 — Q8 Yelp Restaurant (WORST-CASE ANCHOR — non-Meta, sparse twist)
# =====================================================================

Q8_OVERVIEW = """# Yelp Restaurant Recommendation -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Rank a personalized list of restaurants for a user issuing a discovery query (open-ended browse OR query like "dinner near me") optimizing for **conversion-quality matching** -- visit + positive post-visit signal -- where **aspect-level fit** (cuisine, vibe, dietary, group-size, occasion) drives lift far above star-rating averaging. Note: Yelp is **not** a Meta product; structural twists transfer but Meta-specific signal hierarchies do not.

**Input per request**: user_id + geo coordinate + time-of-day + (optional) query term + session context (recent searches, party-size if signaled). User profile carries aspect-preference vector mined from user's own past review writing + dwell-on-listing history. Restaurant profile carries aspect graph (~50-dim taxonomy: cuisine, ambience, dietary, service-style, price, group-size, occasion) extracted from review corpus + business attributes + photo signal.

**Output**: ordered list ~10-25 restaurants per page; final score blends aspect-match + geo-proximity + open-now hard eligibility + freshness multiplier from recent photos/visits.

**Scale anchor**: ~30M MAU, ~10M restaurants globally, ~200ms latency budget; candidate set pre-filtered geographically to ~hundreds before ranking. Methodology lives in `cd://96`; this row owns only the solution shape.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- Review text as primary signal, rating-CF has hard ceiling** -- Two 4-star restaurants can be entirely different experiences along orthogonal axes (cuisine, vibe, dietary, group-size). The lift over rating-based CF does NOT come from collaborative-filtering refinement; it comes from **aspect-level matching from review text**. Mechanically: **LLM-extracted aspect graph per restaurant** + aspect-preference profile per user. This re-defines the entire architecture -- the **aspect taxonomy is the entity that powers both retrieval and ranking**. Interacts with #2 (user-side aspect inference uses the same taxonomy as restaurant-side).

**Twist 2 -- Aspect-from-user's-own-reviews -- self-referential preference inference** -- User aspect-weights are NOT from explicit settings or click history; they're **inferred from what the user has written / dwelled on in their own past reviews**. A user who writes "loved the quiet patio" three times has a `quiet`, `outdoor` preference even if they never tagged it. This **breaks the standard user-embedding-from-clicks paradigm** -- click is too noisy and biased by ranking. Interacts with #1 (shared aspect taxonomy is the bridge between user-side and restaurant-side).

**Twist 3 -- Photo + visit-recency override (time-bounded freshness)** -- Restaurants drift in quality; aspect graphs go stale; a 3-year-old "great service" review may be obsolete. **Recent photo signal + recent visit dwell-time** act as a **freshness multiplier** against historical aspect priors. Interacts with #1 (historical reviews dominate the static aspect prior, recent signals correct the drift).

**Twist 4 -- Hard eligibility (geo + open-now) is NOT a soft feature** -- Geo distance and open-now status are **hard filters at candidate gen**, not soft ranking features. A closed restaurant with perfect aspect match scores zero, not low. Folding eligibility into the scoring function would be a generic-ranker mistake. Interacts with #3 (open-now is current-state, recency override is historical-state correction)."""


Q8_VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min
"Yelp restaurant rec is structurally an **aspect-matching problem, not a star-rating CF problem** -- that's the dominant twist. Two restaurants both rated 4-star can be entirely different experiences along axes like vibe, dietary, group-size, ambience. The lift over rating-CF comes from extracting these aspects from review text and matching to a user's own expressed preferences in their writing. Scale: ~30M MAU, ~10M restaurants, ~200ms budget. I'm choosing not to deep-dive on the recommendation explainability UI, which I can surface on probe." Sub-structure announce: 4 parts -- data/label, retrieval, ranking, eval. Yes/no close.

### Data / Label 3-12 min **(driven by Twists 1 + 2)**
**Two-sided aspect mining**. Restaurant-side: **LLM-extracted aspect graph** from review corpus -- each restaurant gets a sparse aspect vector over a ~50-dim taxonomy (cuisine, dietary, ambience, service-style, price, group-size, occasion). Aspect extraction runs as **LLM-teacher distilled student offline weekly**, with a freshness gate -- restaurants with > 20 new reviews trigger immediate re-extraction. User-side: aspect-preference profile **inferred from user's own review writing** (Twist 2) -- extract aspect-mentions from what the user themselves writes, weighted by review recency. **I pick** self-referential user-profile over click-embedding **because** click is too noisy and ranking-biased; **costs**: low-review-count users get under-determined profiles (handled in §Bias); **switches to** click-embedding only if review-writing rate collapses below a per-cohort floor. Label is **visit + positive post-visit signal** (return visit, positive write-back review, dwell-on-listing > 30s) -- not click on the listing. Click is too noisy.

### Retrieval 12-18 min **(driven by Twists 1, 4)**
Candidate set construction: **hard geo filter** (radius adapted to query intent -- ~1mi for casual, ~10mi for special-occasion) + **open-now eligibility hard filter** (Twist 4), THEN **aspect-overlap retrieval** pulling ~hundreds. **I pick** sparse cosine in 50-dim aspect space over a general two-tower user embedding **because** the aspect taxonomy is the bridge entity from Twist 1 -- two-tower would lose interpretability and aspect-level debuggability; **costs**: a periodic aspect-taxonomy refresh job; **switches to** two-tower only if aspect taxonomy maintenance becomes prohibitive. Cold-start for new restaurants handled by initial-review aspect extraction + business attributes (cuisine, price tier), not by collaborative signal.

### Ranking 18-28 min **(driven by Twists 1 + 3, interacts with Twist 2)**
Ranker is **multi-task** {p_visit, p_positive_postvisit, p_dwell_listing} with fusion weights tuned to **post-visit-positive** (the platform-aligned conversion label), not click. The aspect-match score from retrieval enters as a **strong continuous feature** alongside contextual features (time-of-day, party-size, distance, price). Critical: the **recent photo + visit-recency signal** (Twist 3) enters as a **freshness multiplier** on the aspect prior -- if recent photos / dwell suggest a quality drop or aspect drift (e.g., former-quiet-spot now reviewed as loud), the multiplier downweights the static aspect prior. **I pick** freshness as a multiplier over freshness as a feature **because** drift compounds multiplicatively against the static prior; **costs**: a recent-signals aggregation job; **switches to** freshness-as-feature only if drift dynamics flatten.

### Bias 28-32 min **(driven by Twist 2)**
The self-referential profile (Twist 2) has a subtle trap: **users who write more reviews bias the model toward their stated preferences**, while quiet users have under-determined profiles. **I pick** demographic-cohort aspect-prior fallback for low-review-count users (e.g., users in same age bracket / urban density / past-cuisine-tried) blended with their thin profile via a smooth blending function, transitioning as their review history accrues; **costs**: cohort-prior maintenance + monitoring on transition smoothness; **switches to** raw thin-profile only after a calibrated review-count threshold. Don't pretend the profile is fully personalized when the signal is thin.

### Eval 32-38 min
Three surfaces: (1) **offline sliced metrics** -- visit + post-visit-positive rate per {aspect-axis x user-review-count-bucket}, because the dominant twist is aspect-matching AND Twist 2's bias trap requires slicing by user activity; (2) **counterfactual replay with IPS correction** -- Yelp's logged data is heavily ranking-biased (long-tail restaurants under-exposed), so use IPS-weighted offline replay; (3) **online A/B with metric = post-visit-positive lift, not click lift** -- short-term click can be gamed by recency boosting but post-visit-positive is the conversion truth.

### Wrap 38-45 min
Top 3 risks: (1) **aspect taxonomy staleness** -- new cuisine trends (e.g., "gluten-free" was rare 10y ago, now critical) require refresh; mitigate via quarterly LLM re-extraction with diff review; (2) **user-profile cold-start gap** -- low-review-count users use cohort fallback but the transition can be bumpy; mitigate with smooth blending function + transition-stability metric; (3) **photo-freshness adversarial** -- restaurants gaming recency by photo-bombing their own listings; mitigate via authority weighting (verified-visit photos > unverified). Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 reframe -- "two 4-star restaurants aren't equivalent; the lift comes from aspect-level matching from review text, not rating refinement"
- **SM #2 (12-15 min)**: Twist 2 -- "user-profile from user's own writing is self-referential and breaks the click-embedding paradigm"
- **SM #3 (25-28 min)**: Twist 3 -- "recent photo + visit-recency override handles aspect drift on a time-bounded scale, multiplier not feature"
- **SM #4 (38-42 min)**: zoom-out + top 3 risks above; mention IPS counterfactual replay as the long-tail exposure-bias correction

## §5 Drift recovery + 3-way handoff

**Drift to rating-CF**: "Let me return to the ML core -- rating-CF has a hard ceiling because two 4-star restaurants can be completely different experiences. The lift comes from aspect-level matching extracted from review text PLUS the user's own review writing as a self-referential profile -- this combination is the design."

**Asks scale early**: "~30M MAU, ~10M restaurants, ~200ms budget, geo-filtered candidate set to hundreds; ML decisions don't shift with scale, only the aspect-extraction freshness cadence does."

**Asks for two-tower**: "Two-tower flattens the aspect taxonomy that is the bridge entity here; I pick sparse cosine in 50-dim aspect space over two-tower because the aspect-level debuggability is a stronger product signal than embedding-space coherence."

**Asks rating prematurely**: "Park rating-as-feature until aspect -- rating is a weak signal compared to aspect-match, and folding rating into ranking misses the senior framing."

**Handoff (3-way)**: "Want me to deepen the **LLM aspect-extraction pipeline + freshness gating + taxonomy refresh cadence**, the **self-referential user-profile inference + low-review-count cohort fallback**, or the **photo-freshness multiplier override + IPS counterfactual replay eval**?\""""


# =====================================================================
# INSERTS
# =====================================================================

ROWS = [
    {
        "slug": "meta-fb-newsfeed-golden",
        "title": "Meta MLSD Golden Example: FB News Feed Ranking (口播稿 only, 45min walkthrough)",
        "subtitle": "MSI label hierarchy + multi-source CG + close-friend bypass + integrity multiplier cascade",
        "overview": Q9_OVERVIEW,
        "verbal_outline": Q9_VERBAL_OUTLINE,
        "display_order": 207,
    },
    {
        "slug": "meta-yelp-restaurant-golden",
        "title": "Meta MLSD Golden Example: Yelp Restaurant Recommendation (口播稿 only, 45min walkthrough)",
        "subtitle": "Aspect-level matching from review text + self-referential user profile + photo-freshness multiplier",
        "overview": Q8_OVERVIEW,
        "verbal_outline": Q8_VERBAL_OUTLINE,
        "display_order": 208,
    },
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat(timespec="seconds")
    inserted = []
    for row in ROWS:
        exists = cur.execute(
            "SELECT id FROM system_designs WHERE slug=?", (row["slug"],)
        ).fetchone()
        if exists:
            print(f"SKIP {row['slug']} already exists at id={exists[0]}", file=sys.stderr)
            continue
        cur.execute(
            """
            INSERT INTO system_designs
                (slug, title, subtitle, overview, verbal_outline,
                 display_order, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["slug"],
                row["title"],
                row["subtitle"],
                row["overview"],
                row["verbal_outline"],
                row["display_order"],
                now,
                now,
            ),
        )
        inserted.append((cur.lastrowid, row["slug"]))
    conn.commit()
    conn.close()

    # Verify
    conn = sqlite3.connect(DB_PATH)
    for new_id, slug in inserted:
        row = conn.execute(
            """SELECT id, slug, length(overview), length(verbal_outline),
                      length(overview)+length(verbal_outline) AS total
               FROM system_designs WHERE id=?""",
            (new_id,),
        ).fetchone()
        print(f"OK id={row[0]} slug={row[1]} overview={row[2]} verbal={row[3]} total={row[4]}")
    conn.close()


if __name__ == "__main__":
    main()
