"""
Insert meta-event-attendance-golden system_design row (T-P0-884).

Q12 Predict If User Attends FB Event, top-9 batch, kou-bo-gao only.
Template locked from anchors id=45 (meta-fb-newsfeed-golden) and id=46
(meta-yelp-restaurant-golden); see scripts/mlsd_top9_spec.md.

Dominant twist: prediction-as-feature -- the downstream consumer
(recommendation ranking / notification gating / capacity planning) decides
the architecture. Skipping this clarification is the failure mode cd94
explicitly flags ("上次答烂大概率在此"). Three interacting twists: RSVP-vs-
attend split label per consumer, time-to-event as a model regime switcher
(1-month-out vs 1-day-out are different model worlds), and a calibration
target that itself differs per consumer (Brier for capacity, AUC for
ranking, RMSE for notify-gating).

Idempotent: skips insert if slug already exists.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

OVERVIEW = """# FB Event Attendance Prediction -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Emit a **calibrated probability** that user u attends event e in a fixed window, where the **calibration target itself depends on the downstream consumer** -- ranking wants relative-order, capacity wants well-calibrated absolute, notification-gating wants a cost-aware threshold. Shipping a single binary score without first clarifying the consumer is the cd94-flagged failure mode.

**Input per request**: user_id + event_id + (time_to_event, event_type, host_id, host_strength, friends_going_count, capacity_pressure, weather if time_to_event small) + per-user historical attendance per event-type + RSVP signal if present (feature on the attend head, NOT the label). Surface depends on consumer: ranking scores ALL (u, candidate) pairs; notification-gating scores only already-recommended events; capacity aggregates over all RSVPs to a host.

**Output**: calibrated p(attend) per (u,e) -- consumed by (a) ranking as a feature in a fused score, (b) notification-gating as a thresholded send-or-not under per-cohort send-budget, OR (c) capacity as a sum over expected attendees feeding host-side overflow alerts. Same underlying model only when calibration objectives overlap.

**Scale anchor**: ~3B FB users, ~10M active events, ~50-500 candidates per ranking request, p99 ~120ms ranking vs ~500ms async notification-gating vs daily-batch capacity. Methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution shape.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- Prediction-as-feature: ask the downstream consumer FIRST** -- Generic binary-classifier framing assumes the score ships AS the product. Here it is a feature consumed by something downstream, and the **architecture differs per consumer**: ranking wants pairwise-relative scores over a candidate pool, notification-gating wants calibrated thresholds against a send-budget, capacity wants well-calibrated absolute aggregate. Skipping this question is the cd94-flagged failure mode (上次答烂大概率在此). SM #1 IS the clarification -- a **scope-defining first move**, not a feature tweak. Default: ranking, confirmed before drafting. Interacts with #2 (consumer picks the split label) and #4 (consumer picks the calibration objective).

**Twist 2 -- RSVP-vs-attend split label, different target per consumer** -- ~30% of RSVPs don't show; RSVP is social-signaling noise, attend is ground-truth. Capacity wants `attend` (RSVP overcounts), notification-gating wants `RSVP` (gate on intent), ranking wants `attend` calibrated. One multi-task head with two calibrated outputs {p_RSVP, p_attend} sharing a backbone -- NOT a shared label. Interacts with #1 (consumer picks the served head) and #3 (regime shift at ~1-day-out widens the RSVP→attend gap sharply).

**Twist 3 -- Time-to-event is a model regime switcher (NOT a feature)** -- Long-horizon is dominated by **interest match + social context + calendar conflicts**; short-horizon by **weather + reminder + last-minute social changes**. Treating time_to_event as one feature among many under-fits BOTH regimes. NEW vs cd94 (lists time_to_event without the regime framing). Implementation: MMoE with time-to-event as a soft-gating variable, OR two hard-split models at ~24-72h. Interacts with #2 (RSVP→attend conversion drops once weather + reminder dominate) and #4 (per-regime calibration required because conversion distribution shifts).

**Twist 4 -- Calibration target itself differs per consumer** -- **Capacity** requires **Brier score** (absolute probability, count-unbiased aggregation). **Notification-gating** requires **per-threshold cost-weighted error** -- precision at the operating point, NOT the full 0-1 range. **Ranking** requires **NDCG/AUC** (ordering stability) + per-cohort isotonic Platt for smooth fused-score insertion. A shared calibrator silently optimizes for whichever consumer dominates training prevalence. NEW vs cd94 ("calibrated probability" generically). Sliced per-(consumer, regime) eval is the only honest measurement. Interacts with #1 (consumer picks the metric) and #3 (regime determines per-slice sample size and drift)."""


VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min **(driven by Twist 1)**
"Before designing this, the most important question is: **who consumes the prediction?** Ranking, notification-gating, and capacity-planning produce three different architectures. Ranking needs calibrated p(attend) per (u, candidate) pair, online over the recall pool. Notification-gating only scores already-recommended events -- smaller surface, operating point matters more than order. Capacity needs aggregated expected-attendees per event -- batch is fine, calibration is critical. **My default is recommendation ranking** -- can you confirm before I draft?" Scale: ~3B users, ~10M events, p99 ~120ms ranking. Sub-structure: data/label, feature-store, regime-aware ranking, calibration, eval.

### Data / Label 3-12 min **(driven by Twist 2, interacts with Twist 1)**
**RSVP and attend are different targets** -- ~30% of RSVPs don't show. Label by Twist 1's consumer: ranking → `attend`, notification-gating → `RSVP`, capacity → `attend`. **I pick** a multi-task head with two calibrated outputs {p_RSVP, p_attend} sharing a backbone over two separate models **because** features overlap heavily and joint learning of p(attend | p_RSVP) is itself the calibration signal capacity needs; **costs**: per-task calibration job + per-cohort {time-to-event x event-type} sample-size guard against rare slices; **switches to** two separate models only if negative transfer surfaces in the long-horizon regime. RSVP enters as a **feature** on the attend head, NOT as the label -- otherwise we leak. Confirmed-attend via check-in + post-event survey + photo-tag heuristics, per-source weight calibrated to known cohorts.

### Retrieval-as-Feature-Store 12-18 min **(driven by Twist 1)**
The candidate pool is supplied by whichever consumer ingests us. Ranking: recall pool from the ranking system's retrieval (geo + interest + follow-graph). Notification-gating: the already-recommended event set. Capacity: all RSVPs to a given host. **I pick** feature-store assembly over re-running candidate generation **because** the consumer has already done retrieval and a second source-of-truth would drift; **costs**: contract with the consumer's recall pool + per-cohort QPS budget; **switches to** independent retrieval only if the consumer can't supply a candidate set (capacity fallback to RSVP-roster join). Per-(u, e) features: time_to_event, event_type, host_strength, friends_going_count, capacity_pressure, per-user historical attendance per event-type, weather lookahead if time_to_event < 7d, RSVP signal.

### Regime-Aware Ranking 18-28 min **(driven by Twist 3, interacts with Twists 2 + 1)**
**MMoE with time-to-event as the soft-gating variable**: long-horizon expert at time_to_event > 72h (interest + calendar + social); short-horizon expert at < 72h (weather + reminder + last-minute social). Two task heads {p_RSVP, p_attend} from Twist 2. **I pick** MMoE soft-gating over hard-split two-model **because** the regime boundary (~24-72h) is fuzzy and per-event-type -- soft gating learns it per event-type rather than imposing one cutoff; **costs**: ~3x parameters + per-expert drift monitoring + harder feature attribution; **switches to** hard-split only if expert-collapse appears (one expert dominates the gate across all buckets -- detectable via expert-utilization slice). Backbone: shared transformer over (user, event, social-context); experts diverge at the last 2 layers. Cold-start for new event types (cd94-listed: 演唱会 vs 婚礼 vs meetup) via event-type embeddings + per-type prior backoff to category mean conversion.

### Calibration 28-32 min **(driven by Twist 4, interacts with Twists 1 + 3)**
**Per-(consumer, regime) sliced** -- one global head silently optimizes for the wrong consumer. Three calibrators: (a) **isotonic** for capacity (Brier-optimal absolute probability), (b) **Platt** for ranking (AUC-preserving + smooth surface for the downstream fused score), (c) **per-threshold cost-aware** for notification-gating (calibrate at the send-budget operating point, NOT the full 0-1 range). Each is regime-conditional because RSVP→attend conversion jumps once weather + reminder dominate. **I pick** three calibrators over one shared **because** the objectives are mathematically different (Brier-min vs AUC-preserving vs cost-aware-threshold); **costs**: 3x calibration jobs + per-consumer drift detector + per-regime sample-size guard; **switches to** shared only if cross-consumer demand drops to a single primary use case.

### Eval 32-40 min **(driven by Twist 4, interacts with Twists 1 + 2 + 3)**
Three surfaces: (1) **offline sliced metrics** -- per-consumer per-regime: Brier for capacity, NDCG@K for ranking, precision-at-send-budget for notification-gating, ALL sliced by time-to-event bucket {>30d, 7-30d, 1-7d, <1d}. **I pick** sliced per-consumer over single AUC **because** close-friend / popular-host slices monopolize aggregate AUC and mask short-horizon regressions; **costs**: per-slice dashboard + per-cohort minimum-sample-size guard (婚礼 tiny sample). (2) **Counterfactual replay with IPS** before A/B -- logged pairs are biased toward prior surfaces; IPS-weighted replay corrects exposure bias. (3) **Online A/B with consumer-specific metrics** -- ranking on downstream click-through + post-event satisfaction (NOT raw AUC, gameable by surfacing high-RSVP low-conversion popular events); notification-gating on send-precision + unsubscribe; capacity on overflow false-positive + venue utilization.

### Wrap 40-45 min
Top 3 risks: (1) **wrong-consumer architecture lock-in** -- if Twist 1 is skipped, the calibration + eval stack is mis-fit and finding-out happens only after launch; mitigate via SM #1 confirmation + early per-consumer offline replay. (2) **MMoE expert collapse at the regime boundary** -- short-horizon expert under-fits since long-horizon dominates training (most RSVPs come >7d out); mitigate via per-regime sample weighting + per-expert utilization slice + hard-split fallback. (3) **calibration drift after RSVP-policy changes** -- one-tap RSVP UI shifts the RSVP→attend distribution and silently breaks Brier; mitigate via daily Brier-on-fresh-data drift monitor + auto-rollback if drift > 2x baseline. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 reframe -- "the most important question first: who consumes the prediction? Ranking, notification-gating, capacity produce three different architectures; my default is ranking unless you tell me otherwise"
- **SM #2 (12-15 min)**: Twist 2 -- "RSVP and attend are different labels, ~30% of RSVPs don't show; consumer dictates the split target, multi-task head over a shared backbone lets p(attend|RSVP) become its own calibration signal"
- **SM #3 (25-28 min)**: Twist 3 -- "time-to-event isn't a feature, it's a regime switcher; long-horizon is interest+social, short-horizon is weather+reminder, MMoE-gated experts handle the soft boundary per event-type"
- **SM #4 (38-42 min)**: zoom-out + top 3 risks; production-scar headlines = wrong-consumer lock-in + MMoE expert-collapse + calibration drift after RSVP-policy change

## §5 Drift recovery + 3-way handoff

**Drift to single-target binary classifier**: "Returning to the ML core -- this is prediction-as-feature, not an end-product classifier. The first move is clarifying the downstream consumer; ranking, notification-gating, capacity each pick a different label and calibration. Skipping that is the failure mode I'd flag in my own postmortem."

**Asks scale early**: "~3B users, ~10M active events, ~50-500 candidates per ranking request, p99 ~120ms ranking vs ~500ms async notification-gating vs daily-batch capacity; ML decisions don't shift with scale within a regime, but the regime shift at ~24-72h does."

**Asks cold-start prematurely**: "Park new-event-type cold-start until ranking -- event-type embeddings + per-type prior backoff to category-level mean conversion handle 婚礼 vs meetup vs 演唱会 once the regime-aware MMoE is in place; cold-start is downstream of the regime split."

**Asks why not a shared calibration**: "Mathematically different objectives -- Brier-min for capacity, AUC-preserving for ranking, cost-aware-threshold for notification-gating. A shared calibrator silently optimizes for whichever consumer dominates training; per-consumer per-regime sliced calibration is the only honest path."

**Handoff (3-way)**: "Want me to deepen the **multi-task RSVP-and-attend label split + per-consumer target selection**, the **MMoE regime-aware ranker + time-to-event-gated experts + cold-start for new event types**, or the **per-(consumer, regime) calibration stack + sliced eval + IPS replay**?\""""


ROW = {
    "slug": "meta-event-attendance-golden",
    "title": "Meta MLSD Golden Example: Predict If User Attends FB Event (口播稿 only, 45min walkthrough)",
    "subtitle": "Prediction-as-feature consumer reframe + RSVP-vs-attend split label + time-to-event regime switcher + per-consumer calibration",
    "overview": OVERVIEW,
    "verbal_outline": VERBAL_OUTLINE,
    "display_order": 210,
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
