"""
Insert meta-ads-golden system_design row (T-P0-885).

Q4 Ads Recommendation, top-9 batch, kou-bo-gao only.
Template locked from anchors id=45 (meta-fb-newsfeed-golden) and id=46
(meta-yelp-restaurant-golden); see scripts/mlsd_top9_spec.md.

Dominant twist: calibrated probability feeds an auction, not ordinal rank --
the bid x pCTR x pConversion x quality math demands a calibrated probability
space, and a pairwise NDCG-style loss silently breaks auction economics.
Three interacting twists: multi-task heads with delayed-feedback windowed
labels (pCTR is fast, pConversion is up to 7d delayed), advertiser
game-theory (counterfactual / IPS replay BEFORE A/B because advertisers
adapt their bids to the model -- pure online A/B violates i.i.d. across the
advertiser population), and pacing/budget is OUTSIDE the ML loss (ML emits
calibrated probability; pacing composes it -- folding pacing into ML loss
is a senior-trap anti-pattern).

Idempotent: skips insert if slug already exists.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

OVERVIEW = """# Ads Recommendation -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Emit a **calibrated probability** of click and conversion per (user, ad), so a downstream **second-price auction** composes them with advertiser bid and quality score into the final ranking. The product objective is NOT ordinal-rank quality -- it is **auction-correct calibration**: `bid * pCTR * pConversion * quality` is the auction math; pairwise NDCG-style loss silently breaks the economics.

**Input per request**: user_id + session context (device, geo, funnel) + per-ad features (advertiser_id, creative embedding, campaign bid-type {CPC/CPM/oCPM}, vertical, frequency-cap state) + per-(u, ad) cross (prior impression/click/conversion, surface-of-origin, time-since-last-exposure). Candidate pool filtered upstream (targeting + brand-safety + frequency-cap) -- ranker sees hundreds-to-low-thousands per request.

**Output**: per-(u, ad) {pCTR, pConversion, pQuality} emitted into the auction, NOT a ranking list. Auction composes `bid * pCTR * pConversion * quality_score` and produces the served slate + second-price billing. Pacing / budget sits BELOW the auction; ML never sees a pacing variable in its loss.

**Scale anchor**: ~3B users, multi-million advertisers, hundreds-to-low-thousands candidates per request after retrieval+targeting, p99 ranker ~80-120ms, conversion attribution 1-7d per objective. Methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution shape.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- Calibrated probability feeds an auction, not an ordinal rank** -- Generic ranker optimizes NDCG / pairwise. Ads MUST output **calibrated** P(click) and P(conversion) because the auction is `bid * pCTR * pConversion * quality` and second-price billing depends on the **absolute** probability scale across advertisers. Pairwise loss breaks bid comparability and silently under-charges second-price. Objective: **logloss + explicit calibration head**, NOT pairwise. NEW vs cd94 (which lists "calibrated probability" without naming logloss + auction-billing dependency). Interacts with #3 (IPS reweighting needs an absolute probability scale) and #4 (pacing composes multiplicatively, not as a loss term).

**Twist 2 -- Multi-task heads with delayed-feedback windowed labels + bias correction** -- pCTR / pConversion / pQuality split heads share a transformer backbone; pCTR is fast (seconds), pConversion is up to 7d delayed for purchase, longer for app-install / lifetime-value. Naive same-day windowing under-counts the late-converting tail and silently shifts pConversion calibration. Fix: **delayed-feedback model with per-objective windowed labels + bias correction** modeling the unobserved tail of the delay distribution and reweighting rather than truncating. NEW vs cd94 (mentions "delayed feedback" but doesn't name windowing-bias-correction as the architectural choice). Interacts with #1 (bias-corrected pConversion stays calibrated as window varies) and #3 (same missing-label reweighting structure as IPS).

**Twist 3 -- Advertiser game-theory: IPS / counterfactual replay BEFORE A/B because advertisers re-bid** -- Advertisers are adaptive: they observe your ranking, see win-rates / CPMs shift, and **re-bid against your model**. Online A/B violates i.i.d. across the advertiser population -- the advertiser distribution is non-stationary under the treatment. **IPS replay is structural, not optional** -- replay logged impressions with IPS-corrected propensity weights BEFORE exposing live advertiser-side adaptation. NEW vs cd94 (lists IPS replay but doesn't frame as the i.i.d.-violation root cause). Interacts with #1 (IPS reweighting needs Twist 1's calibrated scale) and #2 (same missing-label correction structure).

**Twist 4 -- Pacing / budget lives OUTSIDE the ML loss; ML emits probability, pacing composes** -- Senior-trap: fold pacing / budget / frequency-cap into ML loss as a multi-objective term. WRONG. ML emits calibrated per-(u, ad) probability; a **separate pacing layer** (PID controller or LP-style proportional dispatcher per campaign) composes it with spend rate, remaining budget, pacing target into the eligibility multiplier. **Boundary tell** for senior candidates -- you know where the ML loss surface ends. NEW vs cd94 (lists it without framing as the senior-level boundary signal). Interacts with #1 (composition is multiplicative on calibrated probability)."""


VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min **(driven by Twist 1)**
"Ads ranking is not really ranking -- it is **calibrated probability estimation feeding an auction**. `bid * pCTR * pConversion * quality` is the auction math and second-price billing depends on absolute probability scale across advertisers, so calibration is load-bearing in a way it is not for organic feed. Swap logloss for pairwise NDCG and bid comparisons across users go non-meaningful, second-price under-charges. Dominant constraint: logloss + explicit calibration head, not ordinal accuracy." Scale: ~3B users, hundreds-to-low-thousands candidates, p99 ~80-120ms, conversion-attribution 1-7d. Sub-structure: 5 parts -- data/label, retrieval, multi-task ranker, eval+calibration, pacing boundary. Yes/no close.

### Data / Label 3-12 min **(driven by Twist 2, interacts with Twist 1)**
Three task labels: y_click (fast), y_conversion (delayed, 1-7d per objective), y_quality (post-impression survey + integrity classifier). pCTR is straight binary logloss. For pConversion, **delayed-feedback windowing** is the architectural choice: at training time the label is partially observed because conversion can still arrive inside the attribution window. **I pick** delayed-feedback with per-objective windowed labels + bias correction over naive same-day cutoff **because** truncation under-counts the slow-converting tail and silently shifts pConversion calibration ~10-30% downward on purchase campaigns; **costs**: per-campaign delay estimation + nightly bias-correction reweighting; **switches to** naive same-day only for in-platform CTA where delay <1h. Per-objective splits (purchase vs app-install vs lead-gen) have different delay-distribution priors -- per-objective windowing, NOT one global window.

### Retrieval-as-Feature-Store 12-18 min **(driven by Twist 1, interacts with Twist 4)**
Candidate pool is filtered upstream (targeting + brand-safety + frequency-cap) -- ranker sees what survived. **I pick** retrieval-as-upstream-contract (feature-store + eligible-candidate stream) over ranker-side candidate gen **because** advertiser-side targeting (geo / demographic / lookalike / exclusion) is policy owned by advertiser-tools, not ML inference; **costs**: contract + per-(u, advertiser) eligibility cache + freshness SLA on frequency-cap state; **switches to** ranker-side only if the targeting cache cannot meet p99. Per-(u, ad) features: user context, ad features (creative embedding from a frozen visual+text tower, campaign bid-type, vertical), cross features (prior impression/click/conversion, time-since-last-exposure -- the frequency-cap feedback), surface-of-origin one-hot.

### Multi-task Ranking 18-28 min **(driven by Twists 1 + 2, interacts with Twist 4)**
**MMoE backbone, three split heads {pCTR, pConversion, pQuality}** at the final layer. Each head is per-label logloss, NOT shared cross-entropy. The fused score the auction sees is NOT a learned weighted sum: it is `bid * pCTR * pConversion * quality_score` where bid and quality_score enter at auction time. **I pick** MMoE shared backbone + per-head logloss over a single multi-label head **because** the label distributions differ sharply (pCTR ~10% pos, pConversion ~0.1-1%, pQuality survey-derived) and shared CE under-fits the rare-conversion tail; **costs**: per-head sample-weight tuning + per-head calibration + expert-utilization slice; **switches to** single-head only if conversion sample size drops below rare-event threshold. **Critical**: loss surface ends at head outputs -- no pacing / budget / frequency-cap term in loss (Twist 4).

### Calibration + Counterfactual Eval 28-38 min **(driven by Twists 1 + 3, interacts with Twist 2)**
Calibration is the **second non-negotiable** after logloss. **Per-cohort isotonic** at head outputs -- one calibrator per {advertiser-vertical x campaign-objective x surface}, NOT one global. **I pick** sliced isotonic over a global Platt **because** auction billing depends on cross-advertiser comparability and a global calibrator mis-prices the long tail of small advertisers; **costs**: ~50-200 calibrators tracked + drift detector + per-cohort min-sample guard. IPS replay is **structural, not optional** (Twist 3): online A/B's i.i.d. assumption fails because **advertisers re-bid** -- the advertiser distribution is non-stationary under the treatment. Replay logged impressions with IPS-corrected propensity weights, score offline against win-rate + CPM + conversion delta, BEFORE live advertiser adaptation. **Switches to** A/B-first only for null-effect releases where advertiser adaptation is mechanically impossible.

### Wrap + Pacing Boundary 38-45 min **(driven by Twist 4)**
**Where does ML stop?** ML emits calibrated {pCTR, pConversion, pQuality}. Auction multiplies in bid + quality_score. A **pacing layer** (PID controller or LP-style proportional dispatcher per campaign) composes pCTR * pConversion with spend rate, remaining budget, pacing target into the eligibility multiplier; frequency-cap composes similarly. **I pick** pacing-as-separate-layer over folding pacing into ML loss **because** pacing is closed-loop seconds-to-minutes and ML retraining is daily-to-weekly -- the time-scales don't match, and folding pacing into ML guarantees lag-driven oscillation against the budget closed loop; **costs**: per-campaign controller + ML/pacing handshake (multiplier shape, log-space addition); **switches to** loss-side pacing only as a knowingly-built learned-pacing research bet. Top 3 risks: (1) **calibration drift after creative-tower retrain** -- frozen tower drift shifts per-cohort calibration; mitigate via daily-sliced reliability-diagram + auto-recalibration before propagating to auction. (2) **delayed-feedback bias collapse after attribution-window policy change** -- 1d to 7d flip mis-fits the windowed-label bias; mitigate via per-campaign window-policy version + per-version bias-correction job. (3) **IPS-replay propensity staleness** -- old logged propensities under-estimate current bias; mitigate via rolling propensity model + replay-window cap at its retrain cadence. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 reframe -- "Ads ranking is not ranking, it is calibrated probability feeding an auction; pairwise loss for NDCG gains silently breaks auction economics and second-price billing"
- **SM #2 (12-15 min)**: Twist 2 -- "delayed-feedback windowed labels with explicit bias correction, not naive same-day cutoff -- otherwise pConversion calibration drops 10-30% on purchase campaigns"
- **SM #3 (25-28 min)**: Twist 3 -- "advertisers re-bid against your model so online A/B violates i.i.d. across the advertiser population; IPS counterfactual replay BEFORE A/B is structural, not optional"
- **SM #4 (38-42 min)**: zoom-out + Twist 4 pacing boundary + top 3 risks -- "where does ML stop? ML emits calibrated probability, pacing layer composes; folding pacing into ML loss is the senior-trap"

## §5 Drift recovery + 3-way handoff

**Drift to generic NDCG ranker**: "Returning to ML core -- calibrated probability feeding an auction, not ordinal ranking. `bid * pCTR * pConversion * quality` depends on absolute probability scale across advertisers, so logloss + per-cohort isotonic is non-negotiable; pairwise breaks second-price billing."

**Asks scale early**: "~3B users, hundreds-to-low-thousands candidates per request after targeting, p99 ~80-120ms, conversion-attribution 1-7d per objective; ML doesn't shift with QPS, but per-cohort calibration cardinality does (~50-200 calibrators)."

**Asks cold-start prematurely**: "Park new-advertiser cold-start until calibration -- creative embedding from the frozen tower + per-vertical prior backoff to category mean conversion handle the long tail once per-cohort isotonic is in place."

**Asks why not fold pacing into ML loss**: "Closed-loop time-scale mismatch: pacing is seconds-to-minutes feedback against advertiser budget, ML retraining is daily-to-weekly; folding pacing into ML guarantees lag-driven oscillation. ML emits calibrated probability; pacing composes multiplicatively. Boundary tell."

**Handoff (3-way)**: "Want me to deepen the **multi-task heads + delayed-feedback windowed labels + bias correction**, the **IPS counterfactual replay + i.i.d.-violation framing**, or the **per-cohort isotonic calibration + ML/pacing boundary + auction composition**?\""""


ROW = {
    "slug": "meta-ads-golden",
    "title": "Meta MLSD Golden Example: Ads Recommendation (口播稿 only, 45min walkthrough)",
    "subtitle": "Calibrated probability feeds auction + multi-task heads with delayed-feedback windowed labels + IPS replay before A/B + pacing outside ML loss",
    "overview": OVERVIEW,
    "verbal_outline": VERBAL_OUTLINE,
    "display_order": 220,
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
