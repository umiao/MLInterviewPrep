"""
Insert meta-location-rec-golden system_design row (T-P1-888).

Q6 Personalized Location Recommendation, top-9 batch, kou-bo-gao only. Template
locked from anchors id=45 (meta-fb-newsfeed-golden) and id=46
(meta-yelp-restaurant-golden); see scripts/mlsd_top9_spec.md.

Dominant twist: context (time, weather, calendar, party-size) is the primary
intent disambiguator, NOT one feature among many -- the same user at 9am vs 9pm
has completely different intents, so a static user preference profile gives the
average of those intents, which is no one's actual preference at any moment.
Interacting twists: intent classification (food / coffee / activity / nightlife)
as intermediate task BEFORE ranking; walk-vs-drive candidate-set switch (3-mile
vs 30-mile radius) keyed off context-inferred transportation mode; MMR-style
diversity re-rank across intent classes and POI categories.

Idempotent: skips insert if slug already exists.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

OVERVIEW = """# Personalized Location Recommendation -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Given a user u + (geo, request-time context), return a ranked slate of POIs (restaurants, cafes, parks, venues) to visit -- product objective is **visit / booking** (check-in or reservation), NOT click. POI inventory is **long-tail stable** (~100M POIs, low churn) while user intent is **momentary**: the same user at 9am wants coffee, at 9pm wants nightlife. Optimizing click trains for clickbait POIs; correct target binds prediction to physical follow-through.

**Input per request**: user_id + (lat/lon, local-time, day-of-week, weather, calendar gap, recent queries, party-size if known). Retrieval feeds **context-conditioned POI ANN** (POI embeddings precomputed offline; context vector built at request time) + **intent-class-routed cascade**. User long-horizon preference is a residual within the context-selected pool, NOT the primary lever.

**Output**: ranked slate of ~10-30 POIs with per-POI provenance (predicted intent-class + content-similarity) preserved for diversity re-rank and downstream surface routing. Surface routing: nearby-tab is browse ordering, search-suggest is auto-complete intent, push-recommend is thresholded against send-budget.

**Scale anchor**: ~3B users, ~100M POIs (low churn), p99 ~80ms nearby-tab vs ~200ms search-suggest, city-keyed H3-cell shards plus per-cell intent-class partitions. Methodology lives in `cd://96`; this row owns the solution shape only.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- Context (time / weather / calendar / party-size) is the PRIMARY intent disambiguator, NOT one feature among many** -- Generic reaches for static user-preference + context as side feature. WRONG: same user at 9am vs 9pm has different intents; static profile gives the average, no one's actual preference at any moment. **Correct**: context vector is primary input to retrieval AND ranking; user long-horizon preference is a residual within the context-selected pool. NEW vs cd94 (names context-as-primary, not as candidate-gen conditioner). Interacts with #2 (context feeds classifier), #3 (context infers mode -> radius switch), #4 (diversity respects predicted intent proportions).

**Twist 2 -- Intent classification as intermediate task (food / coffee / activity / nightlife / errand) BEFORE ranking** -- Predicted as soft distribution over ~6 classes from context. Generic ranker folds intent as one feature; correct system runs classifier first, then conditions ranker (or routes per-intent rankers in a cascade). **Senior-signal**: explicit intermediate task lets product A/B classifier independently from ranker; classifier dashboard surfaces drift end-to-end loss buries. NEW vs cd94 card (doesn't frame as senior-signal). Interacts with #1 (context is classifier input) and #4 (quota maps to predicted classes).

**Twist 3 -- Walk-vs-drive candidate-set switch (3-mile vs 30-mile) keyed off context-inferred transportation mode** -- Candidate-set RADIUS depends on inferred mode -- walking 3mi, driving 30mi, transit mode-corridor. **Switches candidate-gen**, not a ranking feature. Folding distance as continuous feature lets loss learn substitutions between "30mi + high-affinity" and "2mi + mid-affinity" -- physically incoherent for a walker. NEW vs cd94 card (lists distance as feature, not switch). Interacts with #1 (mode inferred from context: lat/lon delta + time + weather + calendar gap) and #4 (diversity within radius-bounded pool).

**Twist 4 -- Diversity in re-ranking via MMR across intent classes + POI categories, NOT raw GBDT order** -- Greedy top-K returns 5 cafes within 0.5mi when classifier says "70% coffee, 30% activity". **MMR re-rank**: ranker score minus λ · max-similarity-to-already-selected; similarity over (intent-class, POI-category, embedding-cosine). Decouples diversity policy from ranker -- product tunes λ + quota per surface without retraining. NEW vs cd94 card (lists diversity, not as policy split). Interacts with #2 (quota maps to predicted intent classes)."""


VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min **(driven by Twist 1)**
"Location Rec has one specialty: **context (time / weather / calendar / party) is the primary intent disambiguator** -- same user at 9am vs 9pm has different intents; static profile gives an average no one wants at any moment. Primary lever is context-conditioned retrieval + intent classification BEFORE ranking. Second: **walk-vs-drive switches candidate-set radius (3mi vs 30mi)**, not a soft distance feature. Third: **diversity is MMR re-rank across intent classes + POI categories**. Scale: ~3B users, ~100M POIs, p99 ~80ms nearby-tab." Sub-structure: data/label, context-conditioned candidate gen + radius switch, intent classification + ranking, diversity + cold-start, eval. Yes/no close.

### Data / Label 3-12 min **(driven by Twist 1, interacts with Twist 2)**
Three signals: **click = noise** (clickbait hero-photo POIs), **save = intent** (~40% no-visit), **visit / booking = ground-truth** (check-in OR reservation OR mobile-geo dwell >5min + survey on uncertain). Primary label is **visit-conditional-save**. **I pick** visit-conditional-save over flat click **because** click optimizes clickbait, flat save optimizes aspirational saves ("fancy steakhouse" never visited), composed label binds prediction to physical follow-through; **costs**: per-source calibration + label-delay ~1d-7d + geo-dwell precision in dense indoor venues; **switches to** save-only on search-suggest where intent gates the surface. Features: per-POI (category + hours + price + LLM-aspect-tags + photo/review embedding); per-context (time-of-day + day-of-week + weather + calendar-gap + recent-query); per-user (long-horizon category preference -- residual, NOT primary).

### Context-conditioned candidate gen + radius switch 12-20 min **(driven by Twists 1 + 3)**
Two-stage. Stage 1: **infer transportation mode** from context (lat/lon delta over last 15min + time + weather + calendar gap) -- walking / driving / transit / unknown -- sets candidate-set **radius** (3mi / 30mi / mode-corridor / default 5mi). Stage 2: **context-conditioned POI ANN** -- POI embeddings precomputed offline (~100M, low churn); query embedding = user residual + context projection, HNSW M=32 ef_construction=200, city-keyed H3-cell shards with per-cell intent-class partitions. **I pick** mode-keyed radius switch over soft distance feature **because** distance-as-feature lets loss treat "30mi + high-affinity" as substitute for "2mi + mid-affinity" -- physically incoherent for a walker; **costs**: mode-classifier weekly refit + ~1.5x pool inflation for "unknown" + smoothed boundary (no hard cliff for borderline POIs); **switches to** soft distance only inside the radius-bounded pool as a within-mode tiebreaker.

### Intent classification + ranking 20-30 min **(driven by Twist 2, interacts with Twists 1 + 4)**
Classifier first: small MoE over context -> soft distribution across ~6 intent classes (food / coffee / activity / nightlife / errand / other). Then **GBDT ranker** conditioned on predicted intent (per-intent cascade, OR single ranker with intent one-hot + confidence). O(100) features: context-conditioned embedding cosine, LLM-aspect-tag affinity, hours-open match, price match, weather-suitability (outdoor patio downweighted if rain), social-recency, user residual. **I pick** classifier-then-ranker over end-to-end **because** intent is a senior-signal abstraction product can A/B independently -- classifier dashboard surfaces drift end-to-end loss buries; **costs**: per-session intent labels (semi-supervised from query stream + survey sample) + class-imbalance (nightlife <5%, errand sparse); **switches to** single ranker with intent-features only when classifier confidence is calibrated low (mixed-intent sessions, route both cascade legs with attenuated quota).

### Diversity re-rank + cold-start 30-35 min **(driven by Twist 4, interacts with Twist 2)**
**MMR re-rank** AFTER ranker: greedy score = ranker_score - λ · max-similarity-to-already-selected, similarity over (intent-class, POI-category, embedding-cosine). Per-surface λ + per-intent quota -- if classifier says "70% coffee, 30% activity", slate respects ~7:3. **I pick** post-ranker MMR over diversity-as-feature **because** folding into ranker couples it to the loss -- product cannot tune λ per surface (nearby-tab tolerates 4 cafes if coffee-intent; push pushes for variety), independent layer A/B's policy without retraining; **costs**: per-surface λ + per-intent quota + multi-axis similarity; **switches to** ranker-feature only on single-intent fixed surfaces. **Cold-start** for new POIs (<14d): content-only retrieval + quality-gated exposure burst capped per-cell.

### Eval 35-45 min **(driven by Twists 1 + 2 + 4)**
Three surfaces, sliced: (1) **per-surface visit-conditional-save** (nearby-tab) / **save@send-budget** (push) / **query-completion + visit** (search-suggest), sliced by **time-of-day + mode + intent-class** -- must hold uniformly; aggregate gain from drive-coffee-morning while walk-nightlife regresses is SHIP-NO; (2) **counterfactual replay** -- prior model's selection IS the context (logged-action-effect bias), replay must mask prior slate position; (3) **city-cluster A/B** -- per-user randomization works (no friend-going leakage like Event Rec); cluster slicing reveals per-market quality (NYC nightlife mix vs suburban errand mix). **I pick** time + mode + intent slicing over flat top-line **because** aggregate can mask intent-class collapse (model rates everything as "food" because food is 50% of sessions, nightlife regresses silently); **costs**: per-slice sample-size guard + per-intent label audit; **switches to** flat top-line only for pre-launch shadow evals.

Top 3 risks: (1) **context drift** as user-base shifts (post-pandemic remote-work changed mid-day intent mix); rolling context-feature monitor + monthly classifier re-fit. (2) **mode misclassification cliff** -- driver classified as walker gets 3mi pool, misses obvious POIs; smoothed boundary + per-mode confusion-matrix dashboard. (3) **diversity over-correction** -- aggressive λ shows 1 cafe in clear coffee-intent; intent-confidence-gated λ. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 -- "Same user at 9am vs 9pm has different intents -- context isn't one feature, it's the primary disambiguator; static profile gives the average, no one's actual preference at any moment"
- **SM #2 (15-18 min)**: Twist 3 + #1 -- "Walk vs drive switches candidate-set radius itself, 3mi vs 30mi -- soft distance feature lets loss learn substitutions between '30mi + high-affinity' and '2mi + mid-affinity' physically incoherent for a walker"
- **SM #3 (22-25 min)**: Twist 2 -- "Intent classification is the intermediate task -- food / coffee / activity / nightlife as soft distribution BEFORE ranking lets product A/B classifier independently from ranker"
- **SM #4 (38-42 min)**: zoom-out + top 3 risks (context drift / mode-classifier cliff / diversity over-correction) + slice-uniform eval as dominant-twist anchor

## §5 Drift recovery + 3-way handoff

**Drift to static profile / why-not-CF**: "Static profile gives the average of every intent -- 9am coffee + 9pm nightlife average is no one's actual preference at any moment. CF on POI is weak too: corpus IS stable (unlike Event Rec dual cold-start) but per-user POI visits are sparse, so context + intent classification carries more signal than user-POI factors. **I pick** context-conditioned retrieval + classifier **over** static profile + CF **because** intent is momentary; user long-horizon preference is residual, not the primary lever."

**Asks scale early**: "~3B users, ~100M POIs, p99 ~80ms nearby-tab vs ~200ms search-suggest, city-keyed H3-cell shards with per-cell intent-class partitions. ML decisions don't shift with QPS, only HNSW shard layout does."

**Asks cold-start prematurely**: "Two cold-starts -- POI-level (<14d) handled by content-only retrieval + quality-gated exposure burst capped per-cell; user-level (<30d) handled by context-prior backoff (classifier works from context alone; user residual defaults to per-city category prior). Park until candidate gen + classification are laid out."

**Why-not-deep-end-to-end**: "Two-tower deep on context + user + POI is feasible but loses the senior-signal abstraction of intent-as-intermediate-task -- product cannot A/B classifier independently. **I pick** cascade with explicit classifier **over** end-to-end deep **because** intermediate task is the load-bearing surface for explainability + per-component A/B + drift detection."

**Handoff (3-way)**: "Want me to deepen the **context-conditioned retrieval + mode-keyed radius switch**, the **intent classifier + cascade routing**, or the **MMR diversity re-rank + cold-start exposure burst**?\""""


ROW = {
    "slug": "meta-location-rec-golden",
    "title": "Meta MLSD Golden Example: Personalized Location Recommendation (口播稿 only, 45min walkthrough)",
    "subtitle": "Context-as-primary-intent-disambiguator + intent classification as intermediate task + walk-vs-drive radius switch + MMR diversity re-rank",
    "overview": OVERVIEW,
    "verbal_outline": VERBAL_OUTLINE,
    "display_order": 250,
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
