"""
Insert meta-event-rec-golden system_design row (T-P1-887).

Q5 FB Event Recommendation, top-9 batch, kou-bo-gao only. Template locked from
anchors id=45 (meta-fb-newsfeed-golden) and id=46 (meta-yelp-restaurant-golden);
see scripts/mlsd_top9_spec.md.

Dominant twist: dual cold-start (events new/expire continuously + per-user RSVP
frequency ~3/yr too sparse for CF) reframes this as content-based retrieval
over event metadata + LLM-extracted aspect graph, NOT a user-item CF problem.
Interacting twists: geo+time+capacity are HARD filters at candidate gen (not
soft scoring features); friend-going is strongest personalization but
selection-biased so IPS correction is mandatory; capacity calibration
soft-downranks near-sold-out events as a post-prediction layer.

Idempotent: skips insert if slug already exists.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

OVERVIEW = """# FB Event Recommendation -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Given a user u + (geo, time-window, social context), return a ranked slate of events to RSVP/attend -- product objective is **attended-RSVP** (RSVP-conditional attendance), NOT click. Conversion cost is unusually high (physical show-up at a place at a time), so click optimizes clickbait events; correct target composes intent with reality.

**Input per request**: user_id + (lat/lon + radius, time-window, surface ∈ {feed-suggested, events-tab, push-notification}) + per-user social-graph slice. Retrieval feeds **content-based ANN over event-metadata embeddings** + **friends-going aggregator**. User-side embedding is residual at most -- CF cannot carry per-user RSVP ~3/year.

**Output**: ranked slate of ~10-30 events with per-event provenance preserved (content-similarity vs friend-going vs locality popularity). Provenance feeds Twist 3's IPS correction and per-surface diversity quota. Downstream per surface: feed-suggested is ordering, push is thresholded against send-budget, events-tab is fuller browse.

**Scale anchor**: ~3B FB users, ~10M active events (new/dead continuously), p99 ~120ms feed-suggested vs ~500ms async push, geo-keyed H3-cell shards. Methodology lives in `cd://96`; this row owns the solution shape only.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- Dual cold-start + per-user RSVP ~3/yr makes CF non-viable; content-based retrieval is primary** -- Generic recommendation reaches for user-item CF. WRONG: (a) per-user RSVP ~3/year, user-event matrix has ~zero row density, MF cannot extract factors from 3 observations; (b) ~30% of event pool churns weekly, half the columns re-cold-start continuously. **Correct**: content-based ANN over event-metadata embeddings (title, description, host, category, LLM-aspect tags -- genre, vibe, formality), social signal as strong feature. User-side carries long-horizon category/aspect prior, NOT a CF matrix slot. NEW vs cd94 (names sparsity but not dual cold-start as load-bearing reframe). Interacts with #2 (hard filters reduce pool before content scoring), #3 (social signal substitutes for CF personalization), #4 (ramp gates on capacity headroom).

**Twist 2 -- Geo + time + capacity are HARD filters at candidate gen, NOT soft scoring features** -- Folding distance, calendar conflict, and remaining-capacity into the ranker as continuous features is the generic-ranker mistake -- loss surface learns "30mi + high-affinity" as substitute for "2mi + mid-affinity", which never substitutes (user cannot be in two places). **Hard-filter at candidate gen**: drop if distance > radius, if start-time conflicts with calendar/working-hours, if saturated. Only after these pass does content-scoring + social run. NEW vs cd94 (lists hard-filter, not the soft-fold-in trap). Interacts with #1 (post-filter content dominates residual ranking) and #4 (asymmetric: hard at full, soft near full).

**Twist 3 -- Friend-going is strongest personalization, BUT itself selection-biased; IPS correction is mandatory** -- Friend-going is empirically highest-AUC single feature AND output of upstream selection: friends RSVP only to events that already passed some filter. Treating friend-going as exogenous overcounts events the system already favors -- positive-feedback loop crowding out novel candidates. **Correction**: IPS-weighted friend-going by 1/p(friend exposed), propensity from upstream-exposure logs OR cohort prior over friend's per-event-type surface base-rate. NEW vs cd94 (lists as strong feature, not selection-bias trap). Interacts with #1 (social carries personalization CF cannot) and #4 (de-biased friend-going must compose with capacity downrank).

**Twist 4 -- Capacity calibration is POST-prediction soft re-rank, not model input** -- Asymmetric: (a) **>=100%** -- hard drop at candidate gen; (b) **>=85%** -- soft downrank, because converting to RSVP loses value if user shows up and is turned away. Folding capacity as model feature couples policy to the prediction head -- re-trained model silently shifts capacity sensitivity. **Post-prediction multiplicative layer** decouples capacity policy -- product tunes the curve without retraining. NEW vs cd94 (mentions hard-filter, not the policy-layer split). Interacts with #2 (asymmetric capacity, not one continuous feature)."""


VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min **(driven by Twist 1)**
"FB Event Rec has one specialty: **per-user RSVP ~3/year + events churn ~30%/week = dual cold-start, CF non-viable**. Primary lever is content-based retrieval over event metadata + LLM aspect-tag graph, NOT user-item MF. Second: **geo + time + capacity are HARD filters at candidate gen**, not soft features. Third: **friend-going is strongest personalization AND itself selection-biased**, IPS correction is mandatory. Scale: ~3B users, ~10M events, p99 ~120ms." Sub-structure: data/label, hard-filtered candidate gen, content + friend-going retrieval, IPS-corrected ranking, capacity, eval. Yes/no close.

### Data / Label 3-12 min **(driven by Twist 1, interacts with Twist 3)**
Three signals, different reliability: **click = noise**, **RSVP = intent** (~30% no-show), **attend = ground-truth** (check-in + survey + photo-tag). Primary label is **attended-RSVP** -- RSVP conditioned on confirmed attendance, composing intent with reality. **I pick** attended-RSVP over flat click **because** click optimizes clickbait (high cost, low conversion); flat RSVP optimizes social-signaling RSVP (events user wants friends to think they attend); attended-RSVP composes both; **costs**: attend source-mix (check-in ~40%, survey ~10%, photo-tag ~25%, rest unobserved -- per-source weight calibrated) + label-delay ~24h-7d; **switches to** RSVP-only on push where intent gates the send (push's job is "remind", not "predict show-up"). Per-event: title/description/host/category + LLM-aspect tags; per-user: long-horizon category preference + attended-aspect histogram + social context.

### Hard-filtered candidate gen + content-based retrieval 12-20 min **(driven by Twists 1 + 2)**
Hard filters FIRST: (a) **geo** -- drop if distance > radius (feed ~50mi, push ~10mi); (b) **time** -- drop if start-time conflicts with calendar/working-hours; (c) **capacity** -- drop if saturated. Only after these pass does scoring run. **Content-based ANN over event-metadata embeddings** (title + description + host + LLM-aspect-tags via frozen text encoder, HNSW M=32 ef_construction=200, geo-keyed H3-cell shards). Plus **friend-going aggregator** as parallel source (events with >=2 friends RSVP'd, dedupe with content-ANN). **I pick** hard-filter-then-score over soft-fold-in **because** loss surface treats "30mi + high-affinity" as substitute for "2mi + mid-affinity" which never substitutes -- substitution rate is physically incoherent; **costs**: pool dropped early so recall must be re-tuned (LLM-aspect-tag covers semantic neighbors content-ANN misses); **switches to** soft fold-in only at boundary (0.95-1.0 of radius) for a small smoothing term, NOT replacing the hard cut.

### Friend-going + IPS-corrected ranking 20-30 min **(driven by Twist 3, interacts with Twists 1 + 4)**
**GBDT ranker** over O(100) features: content-embedding cosine, LLM-aspect-tag affinity, host-strength, per-event-type prior, recency, **friend-going + IPS-weighted friend-going**, social-graph distance to host, weather if time_to_event < 7d. IPS: friend's RSVP weighted by 1/p(friend was shown the event), propensity from upstream exposure logs OR cohort prior over friend's per-event-type surface base-rate. **I pick** GBDT + IPS-weighted friend-going over raw friend-going **because** friend-going carries the dominant personalization CF cannot deliver but is itself selection-biased -- raw friend-going amplifies events the system already favors, positive-feedback loop crowds out novel candidates; **costs**: per-friend exposure log + per-cohort propensity estimator (weekly refit) + per-event-type IPS-clip ceiling; **switches to** cohort prior (not IPS) only when per-event exposure logging is unreliable (off-platform RSVPs).

### Capacity calibration + new-event exposure ramp 30-35 min **(driven by Twist 4, interacts with Twist 2)**
Asymmetric: **>=100% = hard drop** (Twist 2); **>=85% = soft downrank** post-prediction, multiplicative `1 - sigmoid(α · (fill - 0.85))` AFTER ranker scoring -- product tunes α per surface (push more aggressive; events-tab gentler). **I pick** post-prediction multiplicative over capacity-as-feature **because** folding capacity into the model couples policy to retraining -- re-trained model silently shifts capacity sensitivity, product cannot A/B the curve independently; **costs**: per-surface α + capacity-staleness monitor (counter ~5min max lag); **switches to** feature only if the multiplicative form cannot express a per-surface policy family (it has not). New-event ramp -- **quality-gated burst** of guaranteed exposure for events <24h to bootstrap friend-going -- gates ON capacity headroom AND host-strength + aspect-tag confidence (avoid spam burn).

### Eval 35-45 min **(driven by Twists 1 + 3 + 4)**
Three surfaces, sliced: (1) **per-surface attended-RSVP rate** (feed) / **RSVP@send-budget** (push) / **slate diversity + browse-completion** (events-tab), conditioned on dual-cold-start cohorts (events <24h, users <30d); (2) **IPS-counterfactual replay** before A/B -- logged exposure is biased toward the current friend-going feedback loop, IPS ranker looks artificially good on aligned sessions without IPS replay; (3) **cluster-randomized A/B at social-cluster level** (NOT per-user) -- per-user leaks treatment via friend-going (treated user's friends' exposures contaminate control friend-going feature). **I pick** social-cluster over per-user **because** friend-going creates network-effect leakage per-user treats as noise but is structural; **costs**: cluster definition (community-detection on friend-graph + per-cluster sample-size guard); **switches to** per-user only when friend-going is not a feature (first-week cold-start experiments).

Top 3 risks: (1) **IPS clip ceiling drift** as recommender re-trains; mitigate with weekly propensity re-fit + drift detector on per-event-type weighted-friend-going. (2) **Cold-start ramp on spam** -- aspect-tag confidence high but host-strength low; mitigate with manual review for new-host + new-event intersections. (3) **Capacity-staleness on stale fill** -- counter lag > 15min, sold-out keeps ranking high; mitigate with freshness SLO + pessimistic-fill fallback. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 reframe -- "Per-user RSVP ~3/year + ~30% of events churn weekly -- dual cold-start, CF non-viable, content-based retrieval + LLM aspect graph is primary, not user-item MF"
- **SM #2 (15-18 min)**: Twist 2 + #1 -- "Geo + time + capacity are hard filters at candidate gen, not soft features -- folding as continuous features lets loss learn substitution rates between 'far + high-affinity' and 'near + mid-affinity' that are physically incoherent (user cannot be in two places)"
- **SM #3 (25-28 min)**: Twist 3 -- "Friend-going is strongest personalization AND itself selection-biased -- friends only RSVP to events the system already showed them; IPS-weighted by 1/p(friend exposed) breaks the feedback loop"
- **SM #4 (38-42 min)**: zoom-out + top 3 risks (IPS clip drift / cold-start spam / capacity staleness) + social-cluster A/B as eval anchor (per-user leaks via friend-going)

## §5 Drift recovery + 3-way handoff

**Drift to generic user-item CF / asks why-not-CF**: "CF is non-viable: per-user RSVP ~3/year, matrix has ~zero row density, MF cannot extract factors from 3 observations; ~30% of events churn weekly so half the columns re-cold-start continuously. **I pick** content + social **over** user-item CF **because** content embeddings transfer across corpus churn and friend-going carries the personalization CF cannot deliver at this sparsity; IPS correction breaks the selection-bias feedback loop."

**Asks scale early**: "~3B users, ~10M events, p99 ~120ms feed vs ~500ms async push, geo-keyed H3-cell shards. ML decisions don't shift with QPS, only HNSW shard layout does."

**Asks cold-start prematurely**: "Two cold-starts -- event-level (events <24h, no friend-going signal) handled by Twist 1's content-based retrieval + Twist 4's quality-gated exposure ramp gating on capacity headroom + host-strength + aspect-tag confidence; user-level (users <30d) handled by long-horizon category/aspect prior backoff + surface choice. Park both until candidate gen + ranking are laid out."

**Handoff (3-way)**: "Want me to deepen the **hard-filtered candidate gen + content-based ANN + aspect-tag graph**, the **friend-going IPS correction + cohort propensity estimation**, or the **capacity soft-downrank + new-event quality-gated exposure ramp**?\""""


ROW = {
    "slug": "meta-event-rec-golden",
    "title": "Meta MLSD Golden Example: FB Event Recommendation (口播稿 only, 45min walkthrough)",
    "subtitle": "Dual cold-start + content-based retrieval + hard-filter geo/time/capacity + friend-going IPS correction + capacity soft-downrank",
    "overview": OVERVIEW,
    "verbal_outline": VERBAL_OUTLINE,
    "display_order": 240,
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
