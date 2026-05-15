"""
Insert meta-v2v-search-golden system_design row (T-P1-886).

Q2 Video-to-Video Search (no text query), top-9 batch, kou-bo-gao only.
Template locked from anchors id=45 (meta-fb-newsfeed-golden) and id=46
(meta-yelp-restaurant-golden); see scripts/mlsd_top9_spec.md.

Dominant twist: "similar" is undefined when there is no text query (visual /
audio / intent axes pull in different directions), so retrieval must be
multi-facet (each facet ~1/3 of slate) and the facet weights must be learned
session-time from click telemetry -- NOT a single fused embedding. Interacting
twists: per-modality encoder + L2-normalize-BEFORE-fusion (otherwise the
higher-raw-norm modality dominates), session-time learned facet weights from
click/dwell via Thompson sampling, single-stage retrieval (query IS the
video, no user side, no two-tower) + cold-start friendly (new video upload
indexed immediately on content embedding).

Idempotent: skips insert if slug already exists.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

OVERVIEW = """# Video-to-Video Search -- 45min Golden Walkthrough (口播稿 only)

## §1 Problem Definition

**Objective**: Given a **query video** (no text, no user-side intent signal), return a ranked slate of **similar videos** -- where "similar" is intrinsically **multi-axis** (visual / audio / intent) and the per-session winning axis is unobservable at query time. The product objective is NOT a single fused-cosine score; it is a **multi-facet slate with online learned per-session facet weights** so in-session click/dwell can reveal the user's actual axis-of-interest.

**Input per request**: query_video_id + per-session context (device, surface, last K interaction events in session). The query video is decomposed into **three modality embeddings** -- visual (frame embeddings from a pretrained video tower), audio (spectrogram-derived audio tower), OCR-text (frozen text encoder over extracted OCR tokens). No user-side tower, no text query.

**Output**: ranked slate of ~25-50 candidates with **per-facet provenance preserved** (which facet retrieved each candidate). Provenance is a first-class feature because session-time facet-weight learning operates on facet-conditional click/dwell, not flat global click.

**Scale anchor**: ~B-scale video corpus, ~10k-50k facet-conditional candidates per request (pre-merge across 3 facets), p99 retrieval ~50-80ms, indexer ingests new videos on content-only embedding (no user-interaction prerequisite). Methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96`; this row owns only the solution shape.

## §2 Twists (dominant + interacting constraints)

**Twist 1 -- DOMINANT -- "Similar" is undefined; multi-facet retrieval with session-time learned facet weights** -- Generic V2V flattens to a single fused-embedding cosine. WRONG here: with no text query, "similar" decomposes into **visual / audio / intent** axes that pull in different directions, and the dominant axis is **per-session and unobservable at query time**. Correct architecture: **multi-facet retrieval** -- each facet gets a slate quota from its own ANN index, and per-session facet weights are learned online from in-session click/dwell. A single fused embedding is wrong for ~2/3 of sessions in expectation. NEW vs cd94 (names multi-facet but doesn't frame session-time weight learning as load-bearing). Interacts with #3 (per-session weights make multi-facet actually work) and #2 (L2-normalize keeps facets composable under merge).

**Twist 2 -- Per-modality encoder + L2-normalize-BEFORE-fusion** -- Each modality has its own encoder (visual, audio, OCR-text). Subtle architectural point: **L2-normalize each modality embedding BEFORE fusion / slate-merge**, NOT after. Without pre-normalization the higher-raw-norm modality (empirically audio -- spectrogram embeddings carry more energy than contrastive-trained visual) silently dominates the merge, collapsing multi-facet back to single-axis. Post-fusion normalize cannot recover -- dominance is locked in before normalization runs. NEW vs cd94 (doesn't name normalize-BEFORE-fusion as silent-dominance prevention). Interacts with #1 (mechanical precondition that lets multi-facet stay multi-facet under merge).

**Twist 3 -- Session-time learned facet weights via Thompson sampling** -- Facet-weight learning is **online**, not offline-trained: the model updates weights within the same session, not on retraining cadence. **Thompson sampling per facet** with click + dwell reward -- each facet keeps a Beta posterior over its in-session CTR; sample, normalize the three samples to a simplex, that is the next-query slate quota. Within 2-3 queries the dominant facet emerges from a uniform cold-start prior. NEW vs cd94 (mentions click/dwell feedback but doesn't name Thompson + session-scoped Beta). Interacts with #1 (facet weights operationalize Twist 1) and #4 (exploration provides cold-start coverage for new videos with no signal).

**Twist 4 -- Single-stage retrieval + cold-start friendly (content-only indexing)** -- The query IS the video; no user-side embedding to dot-product against. **Single-stage retrieval** (per-facet ANN over content embeddings, slate-merge under Twist 3 weights, light reranker for diversification/integrity). New uploads are indexable **immediately** on content-only embedding -- no user-interaction prerequisite. Senior-trap: bolting on a user-side tower for "personalization" re-introduces two-tower the problem doesn't need and breaks cold-start. Interacts with #3 (Thompson covers session cold-start; content-only embedding covers corpus cold-start)."""


VERBAL_OUTLINE = """## §3 Twist-threaded solving

### Framing 0-3 min **(driven by Twist 1)**
"V2V has one intrinsic specialty: **no text query, so 'similar' is undefined** -- visual / audio / intent pull in different directions, dominant axis is per-session and unobservable at query time. That makes this **multi-facet retrieval with session-time learned facet weights**, not single fused-cosine. Second specialty: the query IS the video, so single-stage content-only retrieval -- no user-side tower, new videos are cold-start friendly. Scale: ~B-scale corpus, ~10k-50k facet-conditional candidates, p99 ~50-80ms." Sub-structure: 5 parts -- data/label, per-modality encoders, multi-facet retrieval, ranking, eval. Yes/no close.

### Data / Label 3-12 min **(driven by Twist 1, interacts with Twist 3)**
Label is **facet-conditional**, not flat. Per-modality encoders pretrain separately on their own positive-pair definition (visual: contrastive on watch-pair positives; audio: contrastive on spectrogram-pair positives; OCR-text: frozen text encoder). At retrieval, the label is **session click/dwell conditional on facet provenance** -- did the user click a candidate from visual, audio, or OCR facet? That conditional label feeds Twist 3's online loop. **I pick** facet-conditional click/dwell over flat click **because** flat click cannot distinguish "user prefers visual-similar" from "visual-facet candidates happened to rank higher pre-merge"; **costs**: facet-provenance preserved as per-candidate logged feature + per-facet click counters; **switches to** flat click only for offline pretraining of encoders, never for the session-time learner.

### Per-modality encoders + L2-normalize-before-fusion 12-18 min **(driven by Twist 2, interacts with Twist 1)**
Three encoders run in parallel: visual (transformer over uniformly-sampled frames), audio (log-mel spectrogram windows), OCR-text (frozen text encoder over OCR tokens). Load-bearing: **L2-normalize each modality embedding BEFORE any fusion / slate-merge**. Without pre-normalization, audio (higher raw-norm at this scale) silently dominates the merge, collapsing multi-facet to single-axis. **I pick** per-modality L2-normalize-before-fusion over post-fusion normalization **because** post-fusion normalizes the already-dominated vector and cannot recover lost facet signal -- dominance is locked in before normalization; **costs**: per-modality norm-monitor + alert if median norm drifts >20% post-encoder-retrain; **switches to** post-fusion only if pre-fusion creates an empirical slate-level regression (it does not).

### Multi-facet retrieval with session-time facet weights 18-30 min **(driven by Twists 1 + 3, interacts with Twist 2)**
Each facet has its **own ANN index** (HNSW M=32, ef_construction=200); each returns ~5k-15k candidates per query. Slate is built by **per-facet quota merge** -- each facet's share is proportional to its session-time learned weight. Twist 3 mechanic: **per-facet Beta posterior over in-session CTR**, Thompson sample per query, normalize the three samples to a simplex -- that is the next-query slate quota. Within-session cold start: uniform prior gives ~1/3 each on query 1; within 2-3 queries the dominant facet emerges. **I pick** session-scoped Thompson + Beta posterior over fixed or per-user batch-trained weights **because** the dominant facet is per-session not per-user; per-user weights cannot solve within-session axis-shift (a visually-curious landing can pivot to audio-curious mid-session); **costs**: per-session state for 3 Beta posteriors + reset on session-end + cold-start prior bias on query 1; **switches to** fixed weights only if session length is too short for the Beta to converge (it is not).

### Ranking + Diversification 30-38 min **(driven by Twist 1, interacts with Twist 4)**
After slate-merge, a **light GBDT reranker** over O(50) candidate-side features (per-facet rank/score, recency, duration, creator quality, integrity multiplier) orders **within** each facet's quota -- it does NOT re-mix facets; quota is locked by Twist 3. Integrity downrank is a shared-scale multiplier (same cascade as cd://96 Weapon Ads). **I pick** light GBDT over deep cross-network **because** heavy lifting is in facet-quota selection (Twist 3) and encoder quality (Twist 2); deep over-engineers within-facet ordering for marginal NDCG at latency cost; **costs**: weekly GBDT retrain + per-facet rank as feature; **switches to** deep only if within-facet diversification becomes the dominant bottleneck.

### Eval 38-45 min **(driven by Twists 1 + 3)**
Three surfaces, all **facet-conditional**: (1) per-facet recall@K + slate NDCG conditioned on inferred-session-axis (labeled subset), not flat AUC; (2) **IPS counterfactual replay** before A/B -- logged slate is biased toward prior facet weights, so the new policy looks artificially good on aligned sessions without IPS; (3) **cluster-randomized A/B at session level** (NOT user) -- Twist 3's per-session weights are the unit of treatment; per-user randomization leaks policy across sessions. **Cold-start eval**: held-out slice of <24h videos, measure retrieval slot share to verify Twist 4's content-only indexing surfaces new uploads.

Top 3 risks: (1) **Modality-norm drift** -- a re-trained visual tower can shift visual median norm and re-dominate; mitigate via per-modality norm-monitor + auto re-anchor of pre-fusion normalization. (2) **Session cold-start on query 1** -- uniform prior may not match user's axis; mitigate via short-horizon cross-session backoff prior when in-session signal is empty. (3) **Facet-weight reward leakage from integrity downrank** -- if integrity suppresses one facet's clicks more than others, Thompson's reward is biased; mitigate via integrity-multiplier as separate term, not folded into click reward. Invite deepen-which-side.

## §4 SM slot map (light)

- **SM #1 (3-5 min)**: Twist 1 reframe -- "'Similar' is undefined without text query -- visual / audio / intent pull in different directions, dominant axis is per-session and unobservable at query time, so multi-facet retrieval with session-time learned facet weights, not single fused-cosine"
- **SM #2 (12-15 min)**: Twist 2 -- "L2-normalize each modality BEFORE fusion, not after -- otherwise audio's higher raw-norm silently dominates the merge and collapses multi-facet back to single-axis; post-fusion normalize cannot recover lost facet signal"
- **SM #3 (22-26 min)**: Twist 1+3 interaction -- "per-facet Beta posterior over in-session CTR, Thompson sample per query, normalize to simplex for next-query slate quota; within 2-3 queries the dominant axis emerges from a uniform cold-start prior"
- **SM #4 (38-42 min)**: zoom-out + top 3 risks + session-level cluster-randomized A/B as the eval-correctness anchor (per-user randomization leaks the facet-weight policy across sessions)

## §5 Drift recovery + 3-way handoff

**Drift to generic V2V single-cosine**: "Returning to ML core -- 'similar' is undefined without text query, so multi-facet retrieval with per-session learned facet weights, not a single fused-embedding cosine. Single fused flattens the axes that pull in different directions; dominant axis is per-session, unobservable at query time."

**Asks scale early**: "~B-scale corpus, ~10k-50k facet-conditional candidates after per-facet ANN, p99 ~50-80ms; ML decisions don't shift with QPS, only per-facet HNSW shard layout does."

**Asks cold-start prematurely**: "Two cold-starts -- corpus-level (new uploads) handled by Twist 4's content-only embedding indexing; session-level (query 1) handled by Twist 3's uniform Beta prior with short-horizon cross-session backoff. Park both until multi-facet retrieval is laid out."

**Asks why not two-tower with user side**: "The query IS the video -- no user-side embedding to dot-product against. Bolting on a user tower re-introduces two-tower and breaks content-only cold-start; **I pick** single-stage content-only **over** two-tower **because** the personalization a user tower carries is already absorbed by Twist 3's session-time facet weights, which solve within-session axis-shift."

**Handoff (3-way)**: "Want me to deepen the **per-modality encoders + L2-normalize-before-fusion**, the **session-time Thompson-sampled facet weights + Beta posterior mechanics**, or the **single-stage content-only retrieval + cold-start eval split**?\""""


ROW = {
    "slug": "meta-v2v-search-golden",
    "title": "Meta MLSD Golden Example: Video-to-Video Search (口播稿 only, 45min walkthrough)",
    "subtitle": "Multi-facet retrieval + session-time learned facet weights + L2-normalize-before-fusion + single-stage content-only indexing",
    "overview": OVERVIEW,
    "verbal_outline": VERBAL_OUTLINE,
    "display_order": 230,
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
