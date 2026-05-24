# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""
Add 7 autorun tasks + 1 wire-up task for Meta MLSD top-9 口播稿 batch.

Anchors (Q9 + Q8) already inserted manually as id=45, id=46.
Remaining 7: Q10, Q12, Q4, Q2, Q5, Q6, Q11.
Wire-up: cd94 family table URI update for all 9 + drawer header retrofit.

Each task description points to scripts/mlsd_top9_spec.md for shared template
+ inlines the per-problem twist seeds and slug.
"""

import subprocess
import sys
import re
import json
from pathlib import Path

TASK_DB = ".claude/hooks/task_db.py"


SHARED_HEADER = """Meta MLSD top-9 口播稿 batch -- creates one row in system_designs.

READ FIRST: scripts/mlsd_top9_spec.md (locked template + positive rubric + reference anchors + validation contract + out-of-scope list).

ANCHORS for style/length calibration:
- meta-fb-newsfeed-golden (id=45) -- BEST-case Meta-native anchor
- meta-yelp-restaurant-golden (id=46) -- WORST-case non-Meta anchor
Inherit the EXACT template these use. ~10k chars total (overview + verbal_outline only; rest NULL).

VALIDATION (mechanical only -- per user directive 2026-05-14, NO quality regex):
sqlite3 data/mle_prep.db "SELECT length(overview)+length(verbal_outline), slug FROM system_designs WHERE slug='<SLUG>';"
Expect total 8000-13000, slug exact. Quality is human spot-check via rubric in spec doc.

COMMIT: EXPECTED_FILES=data/mle_prep.db (plus any one-shot insert script under scripts/). Format: [<TASK_ID>] [Meta-MLSD] Add <SLUG> 口播稿 row (twist-threaded solving + SM slot map)

OUT-OF-SCOPE: do NOT populate architecture/dataflow/formulas/etc.; do NOT write verbatim 60-word SM hook phrases; do NOT update cd94 (wire-up task does that)."""


TASKS = [
    {
        "priority": "P0",
        "complexity": "M",
        "title": "[Meta-MLSD] Add meta-ig-story-golden 口播稿 row (Q10 IG Story, author-tray reframe)",
        "description": SHARED_HEADER + """

THIS PROBLEM: Q10 IG Story Recommendation
TARGET SLUG: meta-ig-story-golden
CD94 SOURCE: read `### Q10. IG Story Recommendation` block from company_documents.id=94

TWIST SEEDS (expand each into [generic default → unique property → design implication] with ≥2 "Interacts with #N" clauses):

1. **DOMINANT -- Author-tray-not-story granularity reframe** -- Generic ranking unit is the story (per-story scoring then sort); but IG users consume by author (watch all of Alice's stories then jump to Bob's). Ranking unit is the **author-tray**, NOT the story. Changes the entire architecture: a story-level deep model is solving the wrong granularity problem.
2. **Skip-to-next-author negative + dwell-per-story label** -- Skip-to-next-author is a uniquely strong negative signal (IG-story-specific implicit dismissal). Combined with per-story dwell as the within-tray positive signal. Click is too noisy.
3. **Within-tray autoregressive sequencing** -- Within a single author's tray, story order matters and is itself a ranking problem. Author-tray ordering across authors + story sequencing within each tray = two-level ranking problem. This is NEW vs cd94 -- card only has author-tray, not within-tray sequencing.
4. **Close-friend prior carries across days even though stories don't (cold-start cure)** -- 24h hard expiry means no per-story history persists. But close-friend / family signals DO persist across days. Cold-start every day is cured by historical author-level priors, not story-level. NEW vs cd94 card.

Recommended interactions: Twist 1 interacts with Twist 3 (granularity reframe enables within-tray sequencing as natural follow-up); Twist 2 interacts with Twist 1 (the skip-to-next negative is uniquely tied to author-tray granularity); Twist 4 interacts with Twist 1 (author-level prior is the cold-start cure ONLY because the granularity is author-tray).""",
    },

    {
        "priority": "P0",
        "complexity": "M",
        "title": "[Meta-MLSD] Add meta-event-attendance-golden 口播稿 row (Q12 Predict Event Attendance)",
        "description": SHARED_HEADER + """

THIS PROBLEM: Q12 Predict if User Attends FB Event
TARGET SLUG: meta-event-attendance-golden
CD94 SOURCE: read `### Q12. Predict If User Attends FB Event` block from id=94. cd94 explicitly flags "上次答烂大概率在此" -- the prediction-as-feature framing failure is the failure mode.

TWIST SEEDS:

1. **DOMINANT -- Prediction-as-feature -- ask the downstream consumer FIRST** -- Generic binary classifier assumes the model output ships as a score; but here the output is consumed by some DOWNSTREAM (recommendation ranking? notification gating? capacity planning?). The architecture differs significantly per consumer. Skipping this question is the failure mode cd94 calls out. The SM #1 hook IS the clarification: "Before designing this, the most important question is: who consumes the prediction?"
2. **RSVP-vs-attend split label -- different model per target** -- "RSVP" and "actual attendance" are different things. ~30% of RSVPs don't show. The target depends on downstream: capacity-planning wants attend, notification-gating wants RSVP, recommendation-ranking wants either calibrated. Different models for different consumers. Interacts with #1.
3. **Time-to-event feature warps model regime** -- 1-month-out attendance prediction is dominated by interest match + calendar conflicts; 1-day-out is dominated by weather + reminder + social-context-changes. The model itself shifts regime as time-to-event collapses. Time-to-event isn't a feature -- it's a regime switcher. NEW vs cd94 card. Interacts with #2 (regime change affects which sub-label dominates).
4. **Calibration target depends on downstream** -- Brier for capacity, AUC for ranking, RMSE for notify-gating. The CALIBRATION objective itself differs per downstream consumer. NEW vs cd94 card. Interacts with #1, #2.""",
    },

    {
        "priority": "P0",
        "complexity": "M",
        "title": "[Meta-MLSD] Add meta-ads-golden 口播稿 row (Q4 Ads, auction-mediated calibrated probability)",
        "description": SHARED_HEADER + """

THIS PROBLEM: Q4 Ads Recommendation
TARGET SLUG: meta-ads-golden
CD94 SOURCE: `### Q4. Ads Recommendation` block from id=94.

TWIST SEEDS:

1. **DOMINANT -- Calibrated probability feeds an auction, not ordinal rank** -- Generic ranker optimizes NDCG / pairwise; ads MUST output calibrated P(click) and P(conversion) because the auction math is `bid × pCTR × pConversion × quality`. The moment you switch to pairwise for NDCG gains, you've broken the auction economics. Logloss + calibration, NOT pairwise.
2. **Multi-task heads with delayed-feedback windowed labels** -- pCTR / pConversion / pQuality split heads. Conversion can be 7 days delayed (or more). Delayed-feedback model with windowed labels + bias correction. NEW vs cd94 card -- card mentions "delayed feedback" but doesn't frame as bias-corrected windowing.
3. **Advertiser game-theory -- IPS/counterfactual replay before A/B because advertisers re-bid** -- Advertisers are adaptive: they observe your ranking and re-bid. A pure online A/B violates the i.i.d. assumption because the advertiser population is non-stationary under your model. Counterfactual replay BEFORE A/B is structural, not optional. NEW vs cd94 card. Interacts with #1 (calibrated prob is needed because advertiser bidding strategy depends on it).
4. **Pacing/budget is OUTSIDE the ML loss -- ML emits probability, pacing layer composes** -- Common failure: trying to fold pacing/budget into the ML objective. Correct: ML emits calibrated probability, pacing layer below ML uses it. This is a boundary signal -- senior candidates know where ML ends.

Recommended interactions: Twist 1 ↔ Twist 3 (calibration is what makes adaptive-bidder analysis tractable); Twist 1 ↔ Twist 4 (calibration is what lets the pacing layer compose).""",
    },

    {
        "priority": "P1",
        "complexity": "M",
        "title": "[Meta-MLSD] Add meta-v2v-search-golden 口播稿 row (Q2 Video-to-Video Search, multi-facet retrieval)",
        "description": SHARED_HEADER + """

THIS PROBLEM: Q2 Video-to-Video Search (no text query)
TARGET SLUG: meta-v2v-search-golden
CD94 SOURCE: `### Q2. Video-to-Video Search` block from id=94.

TWIST SEEDS:

1. **DOMINANT -- "Similar" is undefined; multi-facet retrieval, learn facet weight from session** -- No text query means "similar" can mean visually-similar, audio-similar, or intent-similar. These pull in different directions. Generic single-fused-embedding flattens; correct is multi-facet retrieval (each facet ~1/3 of slate) with learned facet weights from session click telemetry.
2. **Per-modality encoder + L2-normalize-BEFORE-fusion** -- Each modality (visual / audio / OCR-text) has its own encoder. Critical subtle point: L2-normalize EACH modality embedding BEFORE fusion -- otherwise one modality (typically audio, which has higher raw norm) dominates the fused score. NEW vs cd94 card (card mentions per-modality but not the normalize-before-fusion subtlety).
3. **Session-time learned facet weights from click telemetry** -- Which facet matters depends on user's session intent ("did they click the visually-similar slot or the audio-similar slot in this session?"). Online learning of per-session facet weights via Thompson sampling. NEW vs cd94 card. Interacts with #1.
4. **Single-stage retrieval + cold-start friendly (content-only)** -- Single-stage because the query IS the video (no user side, no two-tower). Cold-start friendly: new video uploads can be indexed immediately on content embedding.

Recommended interactions: Twist 1 ↔ Twist 3 (facet weights are what make multi-facet retrieval actually work in session); Twist 2 ↔ Twist 1 (L2-normalize is what makes facets composable).""",
    },

    {
        "priority": "P1",
        "complexity": "M",
        "title": "[Meta-MLSD] Add meta-event-rec-golden 口播稿 row (Q5 Event Rec, sparse + temporal + dual cold-start)",
        "description": SHARED_HEADER + """

THIS PROBLEM: Q5 Event Recommendation (FB Events)
TARGET SLUG: meta-event-rec-golden
CD94 SOURCE: `### Q5. Event Recommendation` block from id=94.

TWIST SEEDS:

1. **DOMINANT -- Dual cold-start (events new/expire constantly + per-user RSVP frequency ~3/yr too sparse for CF)** -- Per-user CF is unworkable: a typical user RSVPs to ~3 events per year. Content-based retrieval over event metadata + LLM-extracted event aspect graph dominates as the primary lever. Reframe: this is NOT a CF problem.
2. **Geo + time + capacity are HARD filters, not soft features** -- Geo distance, time-availability for the user, and event capacity (sold-out) are hard filters at candidate gen. Folding into the scoring function is the generic-ranker mistake. Interacts with #1 (after hard filters, content-based aspect matching dominates the remaining candidates).
3. **Friend-going as strongest personalization + selection-bias correction** -- Friends-going-to-event is the strongest personalization signal but is itself selection-biased (friends only attend events that already passed some filter). Need IPS-style correction OR cohort-based prior. NEW vs cd94 card (card lists "friend-going as strong feature" but doesn't surface the selection-bias trap).
4. **Capacity calibration sold-out re-ranking** -- Once an event is near-capacity, the model should de-emphasize it for new users even if the prediction is high -- you don't want to deliver a recommendation to a user who can't RSVP. Post-prediction layer, not in the model. NEW vs cd94 card. Interacts with #2 (capacity is a hard filter at the binary edge, but calibration handles the soft near-capacity boundary).""",
    },

    {
        "priority": "P1",
        "complexity": "M",
        "title": "[Meta-MLSD] Add meta-location-rec-golden 口播稿 row (Q6 Location Rec, context-dominant)",
        "description": SHARED_HEADER + """

THIS PROBLEM: Q6 Personalized Location Recommendation
TARGET SLUG: meta-location-rec-golden
CD94 SOURCE: `### Q6. Personalized Location Recommendation` block from id=94.

TWIST SEEDS:

1. **DOMINANT -- Context (time / weather / calendar / party-size) is the primary intent disambiguator, NOT one feature among many** -- Same user at 9am vs 9pm has completely different intents. Static user preference profile gives an average that is no one's actual preference. Context is the primary disambiguator, not just a context feature.
2. **Intent classification as intermediate task (food / coffee / activity / nightlife)** -- Surface intent classification BEFORE ranking; condition the ranker on the predicted intent class. NEW vs cd94 card -- card lists as puzzle piece but doesn't frame as senior-signal SM. Interacts with #1 (context is the input to intent classification).
3. **Walk-vs-drive candidate-set switch (3-mile vs 30-mile)** -- The candidate set radius itself depends on inferred transportation mode. Walking → 3-mile candidate set; driving → 30-mile. This switches the candidate gen layer, not just a ranking feature. NEW vs cd94 card. Interacts with #1 (context includes location + time + weather which together infer mode).
4. **Diversity in re-ranking (don't return 5 cafes when user wanted variety)** -- Final slate diversity constraint -- MMR-style re-ranking across intent classes / POI categories.""",
    },

    {
        "priority": "P2",
        "complexity": "M",
        "title": "[Meta-MLSD] Add meta-spotify-music-golden 口播稿 row (Q11 Spotify, audio + session + relisten positive)",
        "description": SHARED_HEADER + """

THIS PROBLEM: Q11 Spotify Music Recommendation (NOTE: non-Meta product, Tier-3 template fill per user 2026-05-14 directive)
TARGET SLUG: meta-spotify-music-golden
CD94 SOURCE: `### Q11. Spotify Music Recommendation` block from id=94.

TWIST SEEDS:

1. **DOMINANT -- Relisten is positive, not redundant (inverts dedup logic)** -- One feature distinguishes music rec from almost every other recommendation domain: relisten is a 5-star signal, not saturation. A user playing the same song 50 times is loving it, not fatiguing. This inverts the deduplication logic standard in video / article rec. Architectural implication: NO post-ranking dedup; instead, relisten frequency is a positive feature.
2. **Audio embedding from spectrogram is the cold-start lever** -- Metadata (artist / genre / era) is too coarse to handle the long-tail. Spectrogram-based audio embedding handles new-artist cold-start: index a new track at upload time with no playcount data. Interacts with #1 (relisten as positive only works when content embedding is strong enough to surface relistenable tracks).
3. **Session mood coherence as autoregressive constraint (NOT pointwise scoring)** -- Within a session, mood should NOT jump (rock → classical → rock is bad). Sequential model conditioned on session prefix, not pointwise next-song scoring. NEW vs cd94 card. Interacts with #1 (relisten positive within mood coherence -- repeating same track stays in mood; repeating across moods can violate it).
4. **Skip-rate as primary label, not play-count** -- Play-count is gameable (auto-play counts). Skip-rate (skip within first 30 seconds) is a strong negative signal. Primary label is `play-to-completion`, NOT play-count. NEW vs cd94 card.""",
    },
]


WIREUP_TASK = {
    "priority": "P0",
    "complexity": "S",
    "title": "[Meta-MLSD] cd94 family table wire-up: link all 9 new sd:// URIs + re-run drawer header retrofit",
    "description": """Meta MLSD top-9 batch FINAL wire-up task -- depends on all 7 autorun tasks landing first.

GOAL: cd94 (id=94) Family Taxonomy row currently has `—` in the URI column for 12 of 13 problems (only Q13 Reels has sd://meta-reels-golden). After this batch, ALL 13 should have URIs.

WORK:
1. Update Section 1 "Family Taxonomy 总表" in `company_documents.content` WHERE id=94: replace `—` in URI column (or add an explicit URI column) so each Q row links to its sd:// URI:
   - Q1 Top-3 Comments → sd://meta-top3-comments-golden
   - Q2 V2V Search → sd://meta-v2v-search-golden
   - Q3 Friend Rec → sd://meta-friend-rec-golden
   - Q4 Ads → sd://meta-ads-golden
   - Q5 Event Rec → sd://meta-event-rec-golden
   - Q6 Location → sd://meta-location-rec-golden
   - Q7 Weapon Ads → sd://meta-weapon-ads-golden
   - Q8 Yelp → sd://meta-yelp-restaurant-golden
   - Q9 FB News Feed → sd://meta-fb-newsfeed-golden
   - Q10 IG Story → sd://meta-ig-story-golden
   - Q11 Spotify → sd://meta-spotify-music-golden
   - Q12 Event Attendance → sd://meta-event-attendance-golden
   - Q13 Reels → sd://meta-reels-golden (already in place)

   Implementation: prefer adding the link inline to each Q row's heading (e.g., `### Q1. Top 3 Comments Extraction → [sd-golden](sd://meta-top3-comments-golden)`) AND in the Section 1 table.

2. **Re-run drawer header retrofit** -- per `feedback_meta_mlsd_reseed_drawer_overwrite.md` memory, ANY content rewrite of cd94 wipes the drawer header. Run:
   `python scripts/retrofit_meta_mlsd_94_drawer_header.py` (or whichever exists for cd94)
   If the script doesn't exist, look at how it was done last time (search `<!-- META_MLSD_DRAWER_HEADER_94_20260512 -->` in PROGRESS.md history).

3. Verify cd94 still has drawer header at top + all 13 URI cells populated:
   `sqlite3 data/mle_prep.db "SELECT substr(content,1,500) FROM company_documents WHERE id=94;"` -- should still show META_MLSD_DRAWER_HEADER_94 marker.

4. EXPECTED_FILES=data/mle_prep.db (+ scripts/<retrofit_script>.py if newly created)

Commit: [<TASK_ID>] [Meta-MLSD] cd94 wire-up: link 9 new sd:// URIs + re-run drawer header retrofit""",
}


def run_add(task):
    cmd = [
        sys.executable,
        TASK_DB,
        "add",
        "--title", task["title"],
        "--priority", task["priority"],
        "--complexity", task["complexity"],
        "--description", task["description"],
    ]
    if task.get("depends_on"):
        cmd.extend(["--depends-on", task["depends_on"]])
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        print(f"FAIL: {task['title']}", file=sys.stderr)
        print(out.stderr, file=sys.stderr)
        sys.exit(1)
    # extract task ID from stdout
    text = out.stdout + out.stderr
    m = re.search(r"T-P\d-\d+", text)
    if not m:
        print(f"No task ID in output: {text}", file=sys.stderr)
        sys.exit(1)
    task_id = m.group(0)
    print(f"ADDED {task_id}  {task['title']}")
    return task_id


def main():
    new_ids = []
    for t in TASKS:
        new_ids.append(run_add(t))

    # wire-up depends on all 7
    WIREUP_TASK["depends_on"] = ",".join(new_ids)
    wireup_id = run_add(WIREUP_TASK)

    print(f"\n7 autorun tasks: {','.join(new_ids)}")
    print(f"1 wire-up task: {wireup_id}")
    print(f"\nLaunch with: bash scripts/autonomous_run.sh 8 --allow-dirty")


if __name__ == "__main__":
    main()
