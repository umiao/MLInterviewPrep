"""Seed: T-P0-448 -- Classical model pitches: KNN / NB / K-Means / DBSCAN.

Deliverables:
 (a) framework_node id=71 (Clustering) description: 115b -> >=2500b clustering
     decision rubric (K-Means vs DBSCAN), with cross-link to the broader
     classical-model pitch one-pager.
 (b) docs/classical_model_pitches.md -- pitch-level one-pager covering KNN,
     Naive Bayes, K-Means, DBSCAN. <=2000 words.

LINK out to data/t4_knn_kmeans.md and data/t5_naive_bayes.md for derivations
and from-scratch implementations. Do NOT re-derive Bayes' theorem or
K-Means convergence here.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from study_note_builder import StudyNoteBuilder

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 71
DOC_FILENAME = "classical_model_pitches.md"

NODE_DESCRIPTION = """# Clustering -- K-Means vs DBSCAN Decision Rubric

## Scope

Pitch-level rubric for the two clustering algorithms most asked in tabular ML
interviews: **K-Means** (centroid / partitional) and **DBSCAN** (density /
non-parametric). KNN and Naive Bayes are supervised so they sit under node 12
(Supervised Learning), but they share the "classical 4" pitch one-pager:
`docs/classical_model_pitches.md`. From-scratch derivations and Lloyd / KD-Tree
mechanics live in `data/t4_knn_kmeans.md` -- this node intentionally does not
re-derive them.

## K-Means vs DBSCAN -- Pick by Data Geometry

| Dimension | K-Means | DBSCAN |
| --- | --- | --- |
| Cluster shape | Convex / spherical (L2 ball) | Arbitrary, non-convex, density-connected |
| Need K up front | Yes (elbow / silhouette) | No (eps + minPts replace K) |
| Outliers | Forced into nearest cluster | Labelled `-1` (noise) |
| Cluster count | Fixed K | Auto from density |
| Scaling | Sensitive (StandardScaler required) | Sensitive (eps depends on scale) |
| Density assumption | Roughly equal-size, equal-variance clusters | Roughly uniform within-cluster density |
| Complexity (train) | O(n * K * d * iters) | O(n log n) with index, O(n^2) without |
| Reproducibility | Sensitive to init -> use **K-Means++** + n_init >= 10 | Deterministic given eps / minPts |
| Failure mode | Bad on moons / rings / unequal density | Bad when clusters have very different densities |

**Decision rule of thumb**:
- Roughly spherical clusters, known K, large N -> **K-Means** (Mini-Batch
  K-Means scales to billions of rows).
- Unknown K, anomaly / noise detection, non-convex shapes -> **DBSCAN**
  (or HDBSCAN for variable density).
- Hierarchical structure needed (dendrogram / cut-at-level) -> agglomerative
  clustering (out of scope here, link only).

## K Choice for K-Means (Skim, Don't Re-Derive)

- **Elbow method**: plot inertia (within-cluster sum of squares) vs K, pick
  the inflection point. Subjective; fails when no clear elbow.
- **Silhouette score**: average `(b - a) / max(a, b)` per sample where a =
  intra-cluster distance, b = nearest-other-cluster distance. Higher is
  better; in [-1, 1].
- **Gap statistic**: compare inertia to a uniform-random reference. Slow but
  more principled.
- **Domain prior**: often K is set by product / business (e.g. 5-tier user
  segmentation), and the algorithm just refines centroids.

See `data/t4_knn_kmeans.md` for the four standard stopping conditions
(centroid shift, label-change count, max iters, inertia delta) and a
from-scratch Lloyd implementation -- this node only covers the pick.

## DBSCAN Tuning (eps + minPts)

- `minPts` rule of thumb: `2 * d` for d-dimensional data (Ester et al. 1996).
- `eps` from k-distance plot: sort each point's distance to its k-th
  neighbour (k = minPts), pick the knee. Same elbow logic as K-Means.
- Both knobs scale with feature scaling -- always StandardScaler first.

## Pinterest / Google Interview Angles

- **Pinterest visual-search clustering**: K-Means on image embeddings (CLIP /
  ResNet) with K in the thousands; Mini-Batch K-Means or **FAISS**'s
  approximate K-Means is the production choice. Followups: how does cosine
  vs L2 change the centroid update? (Spherical K-Means renormalises
  centroids to unit length each iter.)
- **Google ad / query clustering**: DBSCAN on user-session embeddings to find
  bot rings or coordinated campaigns -- the noise label `-1` is the actual
  signal. Followups: why DBSCAN over K-Means here? (Coordinated campaigns
  form tight, dense pockets in a sparse legitimate-traffic background --
  exactly DBSCAN's strength.)

## Sister Nodes & Pointers

- **Classical-4 pitch one-pager (KNN, NB, K-Means, DBSCAN)**:
  `docs/classical_model_pitches.md` -- when-to-use rubric for all four.
- **K-Means + KNN derivations and from-scratch code**:
  `data/t4_knn_kmeans.md`. Do not re-derive the Lloyd update or the
  KD-Tree query here.
- **Naive Bayes derivation**: `data/t5_naive_bayes.md` (sister supervised
  classical model, lives under node 12).
- **Dimensionality Reduction (node 72)**: PCA / t-SNE / UMAP -- often run
  as a pre-clustering step to avoid curse of dimensionality.
- **Evaluation Metrics (node 70)**: silhouette, Davies-Bouldin,
  Calinski-Harabasz for unsupervised cluster quality; Adjusted Rand Index
  / Normalised Mutual Information when labels exist for validation.

## Interview Pitfalls

1. Running K-Means on un-scaled features -- Euclidean distance is dominated
   by the largest-range column. Always StandardScaler / MinMaxScaler first.
2. Random init for K-Means -- catastrophic local optima. Use **K-Means++**
   (sklearn default since 0.16) and `n_init >= 10`.
3. DBSCAN with mixed-density clusters -- one eps cannot fit both. Switch to
   **HDBSCAN** (hierarchical DBSCAN) which lets each cluster have its own
   density.
4. Treating K-Means inertia as a model-selection metric across different K
   -- it monotonically decreases. Use silhouette / gap statistic instead.
5. Confusing K-Means and KNN because both use K. K-Means is unsupervised
   clustering; KNN is supervised lazy classification / regression. They
   share nothing but the letter K.
"""


def update_framework_node() -> int:
    """Update framework_node id=71 description; return byte length."""
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, title FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            sys.exit(1)
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (NODE_DESCRIPTION, NODE_ID),
        )
        conn.commit()
        size = conn.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(f"[DONE] framework_node id={NODE_ID} description: {size} bytes")
        return size
    finally:
        conn.close()


def build_one_pager() -> StudyNoteBuilder:
    """Build the classical-4 model pitch one-pager."""
    b = StudyNoteBuilder()
    b.set_title("Classical Model Pitches -- KNN / Naive Bayes / K-Means / DBSCAN")

    b.add_prerequisites([
        "Bias-variance tradeoff (framework_node 67)",
        "Distance metrics (L1/L2/cosine) -- see data/t4_knn_kmeans.md Part I",
        "Bayes' theorem and conditional independence -- see data/t5_naive_bayes.md",
    ])

    b.add_term("KNN", "K-Nearest Neighbors",
               "Lazy supervised model: predict by majority vote (classification) or mean (regression) of k closest training points")
    b.add_term("NB", "Naive Bayes",
               "Generative classifier built on Bayes' rule plus conditional-independence assumption between features given the class")
    b.add_term("K-Means", "Lloyd's algorithm",
               "Partitional clustering: assign each point to nearest centroid, then update centroid as cluster mean; repeat until convergence")
    b.add_term("DBSCAN", "Density-Based Spatial Clustering of Applications with Noise",
               "Density clustering: a point is a core point if >= minPts neighbours within eps; clusters grow by density-reachability; outliers labelled noise")

    # Section 0: Overview / pick rubric across the four
    b.add_section("0. Pick the Right Classical Model -- Cross-Cutting Rubric", [
        "These four models cover the four classical interview cells: lazy "
        "(**KNN**), generative (**NB**), centroid-clustering (**K-Means**), "
        "density-clustering (**DBSCAN**). They are interview staples not because "
        "they win benchmarks but because the *assumption each makes* maps cleanly "
        "to a question about your data.",
        "**One-line pick guide**:",
        "- Need a no-training-time baseline + small dataset -> **KNN**.",
        "- Need a fast text or spam baseline + interpretable probabilities -> **Naive Bayes**.",
        "- Roughly spherical clusters, known K, scale matters -> **K-Means**.",
        "- Unknown K, non-convex shapes, want noise labels -> **DBSCAN**.",
        "Each of the four pitches below follows the same six-line format: "
        "**what / assumption / when use / when avoid / complexity / interview angle**. "
        "Derivations and from-scratch code live in the linked t4 / t5 docs.",
    ])

    # Section 1: KNN
    b.add_section("1. KNN -- Lazy Supervised Baseline", [
        "**What**: at predict time, find the k closest training points (L1, L2, "
        "or cosine), vote (classification) or average (regression). No model is "
        "fit at training time -- the training set IS the model.",
        "**Assumption**: nearby points in feature space have similar labels. "
        "Implicitly assumes a meaningful distance metric and feature scaling.",
        "**When use**: small dataset (<100k rows), low / moderate dimensionality "
        "(<50 features after PCA), need interpretable per-prediction explanations "
        "('your nearest neighbours had label X'), fast prototyping baseline. "
        "Strong on collaborative filtering and one-shot classification.",
        "**When avoid**: high-dimensional data without scaling -- distances "
        "concentrate (the **curse of dimensionality**: in d >> 1 dimensions, the "
        "ratio of nearest to farthest neighbour distance approaches 1, so 'closest "
        "k' becomes meaningless). Avoid for large-N online serving (predict cost "
        "is O(n * d) without an index, O(log n) with KD-Tree only for d < ~20). "
        "Avoid when features have wildly different units and you have not scaled.",
        "**Complexity**: train O(1) (just store data) or O(n log n) to build a "
        "KD-Tree / Ball-Tree index. Predict O(k * n * d) brute-force, O(k * log n) "
        "with KD-Tree (low d). Memory O(n * d) -- you keep the full training set.",
        "**Interview angle (Pinterest visual search)**: KNN on image embeddings "
        "is the canonical similar-pin retrieval pattern, but production uses "
        "**FAISS / ScaNN** approximate nearest neighbour (ANN) instead of exact "
        "KNN -- exact is infeasible at billion-pin scale. Followup hook: 'how does "
        "ANN trade accuracy for latency?' (HNSW graph traversal: log-N hops, "
        "recall@10 ~99% at 100x speedup). See `data/t4_knn_kmeans.md` Part I for "
        "L1 / L2 / cosine derivations and KD-Tree query mechanics.",
    ])

    # Section 2: Naive Bayes
    b.add_section("2. Naive Bayes -- Generative Text Baseline", [
        "**What**: classify by maximum a posteriori (MAP) under Bayes' rule, "
        "assuming features are conditionally independent given the class. Three "
        "common variants: **Gaussian NB** (continuous features), **Multinomial NB** "
        "(word counts), **Bernoulli NB** (binary feature presence). Probabilities "
        "are estimated by counting + Laplace smoothing.",
        "**Assumption**: features are conditionally independent given the class "
        "-- the 'naive' part. Almost never literally true, yet works surprisingly "
        "well because the *decision boundary* is robust even when probability "
        "estimates are biased.",
        "**When use**: text classification (spam / sentiment / topic), "
        "high-dimensional sparse features, very small training sets where "
        "discriminative models overfit, real-time low-latency serving (Multinomial "
        "NB scoring is O(d) per doc), strong baseline before reaching for a "
        "transformer.",
        "**When avoid**: features with strong correlation that hurts the decision "
        "boundary (image pixels, gene expression panels). Avoid when calibrated "
        "probabilities matter -- NB probabilities are typically over-confident "
        "(driven to 0/1 by the product of many independence-assumption terms). "
        "Run isotonic / Platt calibration if you need true probabilities.",
        "**Complexity**: train O(n * d) -- one pass over training data per class. "
        "Predict O(d * C) for C classes. Memory O(d * C) -- only the per-class "
        "feature statistics, not the data. This is the cheapest non-trivial "
        "classifier.",
        "**Interview angle (Pinterest spam / Google email spam)**: Multinomial NB "
        "with Laplace smoothing and TF-IDF features is the textbook spam baseline. "
        "Followup hook: 'why Laplace smoothing?' (otherwise a single zero count for "
        "an unseen word x in class c makes the entire posterior P(c | doc) = 0). "
        "Modern stacks replace NB with a small DistilBERT classifier, but NB "
        "remains the latency-floor and the explainability fallback. See "
        "`data/t5_naive_bayes.md` for Bayes' theorem derivation, the Naive "
        "assumption proof, Laplace smoothing math, and Gaussian / Multinomial / "
        "Bernoulli variants worked end-to-end.",
    ])

    # Section 3: K-Means
    b.add_section("3. K-Means -- Centroid Clustering", [
        "**What**: partition n points into K clusters by alternating two steps: "
        "(1) assign each point to its nearest centroid (L2), (2) update each "
        "centroid to the mean of its assigned points. Iterate until centroids "
        "stop moving (or label changes drop below a threshold, or max-iters).",
        "**Assumption**: clusters are convex (roughly spherical, equal variance) "
        "and roughly equal-sized. The L2 objective is non-convex globally, so "
        "Lloyd's algorithm only converges to a local minimum -- multiple restarts "
        "with **K-Means++** init are standard.",
        "**When use**: known K (or willing to sweep K via elbow / silhouette), "
        "very large N (Mini-Batch K-Means scales to billions), need interpretable "
        "centroids ('cluster 3 is users who shop on weekends'), need a fast "
        "vector-quantisation step before another model (K-Means as feature "
        "extractor for image patches).",
        "**When avoid**: non-convex clusters (moons, rings) -- K-Means cuts them "
        "in half. Avoid when clusters have very different sizes / densities -- "
        "the L2 objective forces small dense clusters to merge into large diffuse "
        "ones. Avoid with categorical features (Euclidean mean is meaningless) -- "
        "use K-Modes / K-Prototypes instead.",
        "**Complexity**: train O(n * K * d * iters), typically iters < 100 for "
        "K-Means++. Predict O(K * d) per point (just nearest-centroid lookup). "
        "Memory O((n + K) * d). Mini-Batch variant trades a tiny accuracy hit for "
        "10-100x training speedup at scale.",
        "**Interview angle (Pinterest user segmentation, Google query clustering)**: "
        "K-Means on user / query embeddings with K in the hundreds-to-thousands "
        "is the canonical large-scale segmentation pipeline. Followup hook: "
        "'why K-Means++ over random init?' (K-Means++ picks centroids with "
        "probability proportional to squared distance from already-picked centroids "
        "-- spreads them out, gives O(log K)-competitive expected loss vs the "
        "optimum). See `data/t4_knn_kmeans.md` Part II for Lloyd's algorithm, "
        "K-Means++ math, and the four standard stopping conditions.",
    ])

    # Section 4: DBSCAN
    b.add_section("4. DBSCAN -- Density Clustering With Noise Labels", [
        "**What**: a point is a **core point** if it has at least `minPts` "
        "neighbours within radius `eps`. Two core points are density-connected "
        "if reachable by a chain of core points; clusters are maximal "
        "density-connected sets. Non-core points within eps of a core are border "
        "points; everything else is noise (label `-1`).",
        "**Assumption**: clusters have roughly uniform density, separated by "
        "lower-density regions. No assumption on cluster shape -- DBSCAN finds "
        "moons, rings, and arbitrary blobs that K-Means cannot.",
        "**When use**: unknown K, non-convex clusters, want noise / outlier "
        "detection as a first-class output (the `-1` label is the signal in many "
        "fraud / anomaly use cases), spatial data (geo coordinates, lat / lon).",
        "**When avoid**: clusters with widely different densities -- one eps "
        "cannot fit both. Switch to **HDBSCAN** (hierarchical DBSCAN), which "
        "lets each cluster have its own density. Avoid in high-dimensional space "
        "(>~10 features) -- density itself loses meaning under the curse of "
        "dimensionality. Avoid when you need an exact K (DBSCAN does not give "
        "you that knob).",
        "**Complexity**: train O(n log n) with a spatial index (KD-Tree / R-Tree, "
        "low d), O(n^2) brute-force in high d. Predict requires re-running "
        "DBSCAN -- the algorithm does not produce a parametric model, so new "
        "points need either the index lookup or a wrapper classifier.",
        "**Interview angle (Google bot-ring detection, Pinterest fraud)**: DBSCAN "
        "on user-session embeddings finds tight, dense pockets of coordinated "
        "behaviour against a sparse legitimate-traffic background -- exactly "
        "DBSCAN's strength. Followup hook: 'how do you pick eps?' (k-distance "
        "plot: sort each point's distance to its k-th nearest neighbour, pick "
        "the knee -- same elbow logic as K-Means K choice).",
    ])

    # Section 5: Cheat-sheet table
    b.add_comparison_table(
        headers=["Model", "Type", "Train cost", "Predict cost", "Best fit", "Worst fit"],
        rows=[
            ["KNN", "Lazy supervised", "O(1) brute / O(n log n) KD-Tree", "O(k * n * d) brute / O(k log n) KD-Tree", "Small N, low d, prototyping", "High d, large N online"],
            ["Naive Bayes", "Generative supervised", "O(n * d)", "O(d * C)", "Text / spam, sparse, small N", "Strong feature correlation, calibrated prob"],
            ["K-Means", "Centroid clustering", "O(n * K * d * iters)", "O(K * d)", "Spherical clusters, known K", "Non-convex shapes, mixed density"],
            ["DBSCAN", "Density clustering", "O(n log n) / O(n^2)", "Re-run on new pts", "Unknown K, noise as signal", "High d, mixed density"],
        ],
        title="Classical-4 Cheat Sheet",
    )

    # Section 6: Cross-link out
    b.add_section("5. Pointers (Avoid Re-Deriving)", [
        "- **KNN + K-Means derivations and from-scratch Python**: "
        "`data/t4_knn_kmeans.md` (covers L1 / L2 / cosine, KD-Tree query, "
        "Lloyd's algorithm, K-Means++ init, four stopping conditions).",
        "- **Naive Bayes derivation, Laplace smoothing, three variants**: "
        "`data/t5_naive_bayes.md` (covers Bayes' theorem -> Naive form -> "
        "Gaussian / Multinomial / Bernoulli end-to-end).",
        "- **Clustering decision rubric (K-Means vs DBSCAN)**: framework_node 71 "
        "(this one-pager's parent in the unsupervised tree).",
        "- **Bias-variance lens** (KNN: low-bias high-variance for small k, "
        "high-bias low-variance for large k): framework_node 67.",
        "- **Dimensionality Reduction (PCA / t-SNE / UMAP)**: framework_node 72 -- "
        "often run as a pre-clustering / pre-KNN step to dodge the curse of "
        "dimensionality.",
        "- **HDBSCAN, K-Modes, K-Prototypes, agglomerative clustering**: "
        "explicitly out of scope here. Add separate nodes if interview signal warrants.",
    ])

    # Section 7: Interview self-check
    b.add_checklist("Interview Self-Check", [
        "I can name each model's core assumption in one sentence.",
        "I can explain why KNN fails in high dimensions (curse of dimensionality / distance concentration).",
        "I know why Naive Bayes works despite the independence assumption being false (the decision boundary is robust even when probabilities are biased).",
        "I can explain when K-Means cuts a cluster in half (non-convex shape, e.g. moons / rings).",
        "I can pick eps for DBSCAN using a k-distance plot.",
        "I can answer 'K-Means vs KNN' without confusing them (clustering vs lazy classification; they share only the letter K).",
        "I know that K-Means inertia monotonically decreases in K, so do not use it for K selection -- use silhouette / gap.",
    ])

    return b


def write_one_pager() -> int:
    """Render the one-pager to docs/. Returns char length."""
    builder = build_one_pager()
    content = builder.build()
    doc_path = REPO_ROOT / "docs" / DOC_FILENAME
    doc_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {doc_path.name} ({len(content)} chars)")
    return len(content)


def main() -> None:
    """Run both deliverables and sanity-check budgets."""
    node_size = update_framework_node()
    doc_size = write_one_pager()
    if node_size < 2500:
        print(f"[FAIL] node {NODE_ID} = {node_size} bytes, target >=2500")
        sys.exit(1)
    doc_path = REPO_ROOT / "docs" / DOC_FILENAME
    doc_words = len(doc_path.read_text(encoding="utf-8").split())
    node_words = len(NODE_DESCRIPTION.split())
    total_words = doc_words + node_words
    print(f"[INFO] node words={node_words}, doc words={doc_words}, total={total_words}")
    if doc_words > 2000:
        print(f"[WARN] doc word count {doc_words} exceeds 2000 budget")
    print(f"[OK] T-P0-448 deliverables: node={node_size}b (>=2500), doc={doc_size} chars.")


if __name__ == "__main__":
    main()
