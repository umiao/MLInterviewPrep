"""Seed: T-P0-447 -- Bagging vs Boosting + XGBoost/LightGBM mechanics.

Deliverables:
 (a) framework_node id=65 (Tree Models) description: 124b -> ~5000b decision rubric.
 (b) docs/bagging_boosting_xgb_lgb_1pager.md -- pyramid-base XGB/LGB one-pager.

LINK out to LambdaMART doc 60 for gradient-boosting derivations + ranking;
do NOT re-derive AdaBoost / GBDT loss-gradient basics here.

Pyramid base: decision-rubric level. No deep dive into hyperparameter tuning.
Combined word budget: <= 3000 words.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from study_note_builder import FormulaBlock, StudyNoteBuilder

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 65
DOC_FILENAME = "bagging_boosting_xgb_lgb_1pager.md"

NODE_DESCRIPTION = """# Tree Models -- Bagging vs Boosting Decision Rubric

## Scope

CART / Random Forest / AdaBoost / GBDT / XGBoost / LightGBM. This node is the
**decision lens**: when to reach for bagging vs boosting, and when to pick
XGBoost vs LightGBM. Detailed XGB/LGB mechanics live in
`docs/bagging_boosting_xgb_lgb_1pager.md` (sibling deliverable). Gradient
boosting math + ranking applications (MART / LambdaMART) live in Google R1
prep doc 60 -- this node only summarises the engineering trade-offs.

## Bagging vs Boosting -- Pick by Bias-Variance Profile

| Dimension | Bagging (Random Forest) | Boosting (GBDT family) |
| --- | --- | --- |
| Base learner | Strong, high-variance (deep trees) | Weak, high-bias (shallow trees, depth 4-8) |
| Goal | Reduce **variance** via averaging | Reduce **bias** via stage-wise correction |
| Training | Embarrassingly parallel (independent trees) | Sequential (each tree fits previous residuals) |
| Overfit risk | Low; more trees = strictly better | High; needs early stopping + regularisation |
| Noise tolerance | Robust (averaging cancels noise) | Sensitive (boosts noisy mistakes too) |
| Tabular SOTA | Strong baseline | **State of the art** (XGBoost / LightGBM / CatBoost) |
| Interpretability | Feature importance from impurity drop | Same + SHAP commonly applied |

**Decision rule of thumb**:
- Base learner already low-bias (deep CART) and you mostly worry about
  variance -> **bagging** (Random Forest).
- Base learner is weak / high-bias (shallow stump) and you want to push
  accuracy on tabular data -> **boosting** (GBDT, XGB, LGB).
- Heavy label noise / mislabelled rows -> prefer bagging; boosting will
  chase the noise.
- Need a fast, no-tuning baseline -> Random Forest. Need top-of-leaderboard
  tabular performance -> XGBoost or LightGBM.

## Quick Mechanics (See Doc 60 for Full Derivations)

- **Random Forest** = bagging + per-split feature subsampling
  (sqrt(p) for classification, p/3 for regression). Out-of-bag (OOB) error
  gives a free validation estimate.
- **AdaBoost** = forward stage-wise additive model with exponential loss;
  re-weights misclassified samples each round.
- **GBDT (gradient boosting)** = each new tree fits the negative gradient of
  a differentiable loss with respect to the current ensemble's prediction.
  Loss-agnostic (regression L2, classification BCE, ranking LambdaRank...).
- **XGBoost** = GBDT + 2nd-order Taylor expansion + L1/L2 regularisation +
  sparse-aware split + histogram approximation.
- **LightGBM** = histogram + leaf-wise growth + GOSS sampling + EFB
  feature bundling + native categorical handling.

## XGBoost vs LightGBM -- Library Pick

| Criterion | XGBoost | LightGBM |
| --- | --- | --- |
| Tree growth | Level-wise (depth-balanced) | Leaf-wise (loss-greedy) |
| Speed on wide / sparse data | Good | **Better** (EFB + GOSS) |
| Memory | Higher | **Lower** (uint8 bins) |
| Categorical features | Needs one-hot / encoding | **Native** |
| Small dataset overfit risk | Lower (level-wise more conservative) | Higher (leaf-wise) |
| Distributed training | Mature (Spark, Dask) | Mature; faster on wide data |
| Default pick | Production stability, broad ecosystem | Wide tabular / heavy categoricals / large N |

Pinterest / Google interview hook: "why does LightGBM beat XGBoost on wide
datasets?" -> EFB collapses mutually-exclusive sparse columns into one bundle,
GOSS skips most low-gradient rows -> per-iteration cost drops dramatically
when p is large.

## Sister Nodes & Pointers

- **Bias-Variance Tradeoff (node 67)**: foundational lens this rubric is
  built on; bagging targets variance, boosting targets bias.
- **Regularization (node 69)**: XGBoost's L1/L2 + gamma + min_child_weight
  are direct regularisation terms in the structure score; LightGBM adds
  min_data_in_leaf as a leaf-size guard.
- **Loss Functions (node 68)**: GBDT plugs in any twice-differentiable loss
  (BCE, L2, Huber, LambdaRank). XGB needs both gradient and Hessian.
- **Evaluation Metrics (node 70)**: tree models give native feature
  importance and pair well with SHAP for production debugging.
- **LambdaMART drill (doc 60)**: full math for RankNet / LambdaRank
  pseudo-gradients plugged into MART; do not re-derive here.
- **Sketch / streaming (node 196 / doc 58)**: XGB / LGB feature stores
  often use sketches for high-cardinality categorical aggregates.

## Interview Pitfalls

1. Saying "boosting always beats bagging" -- with heavy label noise or
   small data, RF is more robust and needs no tuning.
2. Forgetting bagging's parallelism advantage -- in a constrained
   training-time budget, RF wins because trees train independently.
3. Using XGBoost on a 50k-feature sparse matrix -- LightGBM EFB + GOSS will
   be 5-10x faster with comparable accuracy.
4. Letting LightGBM grow leaf-wise on a small (~1k row) dataset without
   capping max_depth / min_data_in_leaf -- guaranteed overfit.
5. Confusing AdaBoost (exp loss, reweight samples) with GBDT (any
   differentiable loss, fit gradient). They share the additive frame but
   not the optimisation target.
6. Quoting XGB / LGB as "deep learning" -- they are tree ensembles. The
   correct framing is "gradient boosting on decision trees".
"""


def update_framework_node() -> int:
    """Update framework_node id=65 description; return byte length."""
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
    """Build the XGBoost/LightGBM mechanics + decision rubric one-pager."""
    b = StudyNoteBuilder()
    b.set_title("XGBoost vs LightGBM -- Mechanics & Decision Rubric")

    b.add_prerequisites([
        "Decision tree split criteria (Gini / entropy / variance reduction)",
        "Gradient boosting basics -- see doc 60 (LambdaMART drill) for derivations",
        "Bias-variance tradeoff (framework_node 67)",
    ])

    b.add_term("GBDT", "Gradient Boosted Decision Trees",
               "Stage-wise additive ensemble fitting the negative gradient of a loss")
    b.add_term("XGB", "XGBoost (Chen & Guestrin 2016)",
               "GBDT with 2nd-order Taylor, L1/L2 regularisation, sparse-aware splits")
    b.add_term("LGB", "LightGBM (Ke et al. 2017)",
               "Histogram-based GBDT with leaf-wise growth, GOSS, EFB, native categorical")
    b.add_term("GOSS", "Gradient-based One-Side Sampling",
               "Keep all large-gradient rows + random sample of small-gradient rows")
    b.add_term("EFB", "Exclusive Feature Bundling",
               "Bundle mutually-exclusive sparse features into one to shrink feature count")

    # Section 1: XGBoost core
    b.add_section("1. XGBoost Core -- 2nd-Order Taylor + Regularised Structure Score", [
        "**Setup**: at boosting round t the ensemble's current prediction for sample i is "
        "`y_hat_i^(t-1)`. We add a new tree `f_t` to minimise the regularised loss:",
        FormulaBlock(
            latex=r"\mathcal{L}^{(t)} = \sum_{i=1}^{n} \ell\bigl(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)\bigr) + \Omega(f_t)",
        ),
        "Taylor-expand the per-sample loss to **second order** around the current "
        "prediction. Define gradient and Hessian:",
        FormulaBlock(
            latex=r"g_i = \partial_{\hat{y}} \ell(y_i, \hat{y}_i^{(t-1)}), \qquad h_i = \partial^2_{\hat{y}} \ell(y_i, \hat{y}_i^{(t-1)})",
        ),
        "Drop constants -- the round-t objective becomes (note the structure score uses "
        "**both** g and h, while plain GBDT only uses g):",
        FormulaBlock(
            latex=r"\tilde{\mathcal{L}}^{(t)} = \sum_{i=1}^{n} \Bigl[g_i f_t(x_i) + \tfrac{1}{2} h_i f_t(x_i)^2\Bigr] + \Omega(f_t)",
        ),
        "**Regularisation term** -- T leaves with weights `w_j`, plus L1 alpha and L2 lambda:",
        FormulaBlock(
            latex=r"\Omega(f) = \gamma T + \tfrac{1}{2} \lambda \sum_{j=1}^{T} w_j^2 + \alpha \sum_{j=1}^{T} |w_j|",
        ),
        "For a fixed tree structure, the optimal leaf weight and the structure score "
        "(both used to score candidate splits) are closed-form. Let `G_j = sum g_i, "
        "H_j = sum h_i` over samples landing in leaf j (L2-only form shown for clarity):",
        FormulaBlock(
            latex=r"w_j^* = -\frac{G_j}{H_j + \lambda}, \qquad \tilde{\mathcal{L}}^* = -\tfrac{1}{2}\sum_{j=1}^{T} \frac{G_j^2}{H_j + \lambda} + \gamma T",
        ),
        "**Split gain** = (left score + right score) - (parent score) - gamma. A split is "
        "rejected if gain < 0, which is exactly XGBoost's pruning rule.",
        "**Why 2nd-order**: the Hessian acts as an adaptive learning rate per sample. "
        "For squared loss `h_i = 1` (recovers plain GBDT). For BCE the Hessian is "
        "`p_i (1 - p_i)`, which down-weights confident predictions and stabilises the "
        "step. (Plain GBDT uses only `g_i` and is effectively first-order.)",
    ])

    # Section 2: XGBoost engineering tricks
    b.add_section("2. XGBoost Engineering -- Sparse-Aware & Histogram", [
        "**Sparse-aware split finding**: at training time, for each split, XGB tries "
        "sending all missing-value rows down both directions and picks the one with "
        "higher gain. Stored as the leaf's **default direction**. Effect: missing "
        "values, zeros in one-hot encodings, and absent categoricals are handled in "
        "O(#non-missing) time per split rather than O(n).",
        "**Approximate / histogram split** (XGB 1.0+): bucket each feature into ~256 "
        "bins; scan O(#bins) candidate thresholds per feature instead of O(n). "
        "Trades a tiny accuracy hit for a 5-10x speedup; this is the algorithm that "
        "lets XGB compete with LightGBM on speed.",
        "**Distributed split finding**: histogram counts are local to each worker and "
        "merged via all-reduce -- communication cost scales with #features * #bins, "
        "not data size. This is the foundation for XGB on Spark / Dask.",
        "**Column subsampling**: XGB samples features per tree (and per level / per "
        "node) -- a Random Forest-style variance reduction layered on top of boosting.",
    ])

    # Section 3: LightGBM mechanics
    b.add_section("3. LightGBM Mechanics -- Leaf-Wise + GOSS + EFB + Categorical", [
        "**Leaf-wise growth**: at each step, expand the **leaf with the largest loss "
        "reduction**, not the deepest level. Lower training error per added leaf -> "
        "fewer trees needed for the same accuracy. Risk: long, asymmetric trees that "
        "overfit on small datasets. Counter with `max_depth` and `min_data_in_leaf`.",
        "**GOSS (Gradient-based One-Side Sampling)**: large-gradient samples carry "
        "more information about the loss surface, so keep them all (top a% by |g|). "
        "Randomly sample b% from the rest and rescale their gradients by (1 - a) / b "
        "when computing split gain, preserving the gradient distribution in expectation. "
        "Effect: scan ~ (a + b) of the rows per round; typical a = 0.2, b = 0.1 "
        "gives ~3x speedup with negligible accuracy loss.",
        "**EFB (Exclusive Feature Bundling)**: many sparse features (e.g. one-hot of a "
        "100-class categorical) are mutually exclusive -- never non-zero on the same "
        "row. Bundle them into a single feature with an offset trick so the histogram "
        "still distinguishes which original column was active. Reduces effective feature "
        "count from O(p) to O(#bundles), which is what makes LGB **faster on wide / "
        "sparse data**.",
        "**Native categorical**: instead of one-hot, sort categories by `sum(g) / sum(h)` "
        "within the node, then evaluate the optimal binary partition (Fisher 1958). "
        "Avoids the one-hot blowup and finds non-trivial multi-way splits one binary "
        "step at a time. Typical pitfall: setting `categorical_feature` parameter "
        "incorrectly leaves LGB treating the column as numeric (silent perf hit).",
    ])

    # Section 4: Decision rubric
    b.add_section("4. XGB vs LGB -- Decision Rubric (Latency & Memory at Scale)", [
        "Both libraries implement gradient boosting and converge to similar accuracy "
        "on most tabular tasks. The pick is driven by **data shape** and "
        "**operational constraints**, not raw model power.",
        "**Pick LightGBM when**:\n"
        "- Wide feature matrix (10k+ columns) with sparsity -> EFB collapses bundles.\n"
        "- Heavy categoricals -> native handling avoids one-hot blowup.\n"
        "- Memory-constrained training -> uint8 histogram bins use ~1/4 the RAM of XGB hist.\n"
        "- Large N (10M+ rows) -> GOSS skips most low-gradient rows per iteration.",
        "**Pick XGBoost when**:\n"
        "- Smaller dataset (<100k rows) -> level-wise growth is more conservative.\n"
        "- Need maximum production stability and ecosystem maturity (Spark, Dask, "
        "RAPIDS, Triton inference server all have first-class XGB integrations).\n"
        "- Need precise control over split-finding (XGB exposes more knobs).\n"
        "- Already standardised on XGB DMatrix format in your feature store.",
        "**Both are fine when**: <1M rows, mostly numeric features, no extreme width. "
        "The library choice is a footnote; spend tuning budget on features and loss "
        "instead.",
        "**Inference latency**: identical asymptotically (one tree-walk per tree). "
        "LGB tends to be faster in practice because leaf-wise produces fewer trees "
        "for the same accuracy. For online serving, both export to ONNX or Treelite "
        "for sub-millisecond batch scoring.",
    ])

    # Section 5: Comparison table
    b.add_comparison_table(
        headers=["Aspect", "XGBoost", "LightGBM"],
        rows=[
            ["Tree growth", "Level-wise (default) / leaf-wise (`grow_policy=lossguide`)", "Leaf-wise"],
            ["Split-finding", "Exact + histogram approx", "Histogram only"],
            ["Sparse handling", "Sparse-aware default direction", "Same + EFB bundling"],
            ["Categorical", "User encodes (one-hot / target enc)", "Native (Fisher partition)"],
            ["Sampling", "Row + column subsample", "Row + column + **GOSS**"],
            ["2nd-order Taylor", "Yes (g + h)", "Yes (g + h)"],
            ["Regularisation", "L1 + L2 + gamma + min_child_weight", "L1 + L2 + min_data_in_leaf"],
            ["Memory (per row, per feat)", "float32 hist", "uint8 hist"],
            ["Best fit", "<100k rows or production-stable", "Wide / sparse / categorical-heavy / large N"],
        ],
        title="XGBoost vs LightGBM Cheat Sheet",
    )

    # Section 6: Cross-link out
    b.add_section("5. Pointers (Avoid Re-Deriving)", [
        "- **Gradient boosting math + ranking-specific application**: see "
        "`docs/google_lambdamart_drill.md` (DB doc 60). RankNet / LambdaRank "
        "pseudo-gradients plug into XGB (`rank:ndcg`) and LGB (`lambdarank`); "
        "this one-pager intentionally does not re-derive the loss math.",
        "- **Bias-variance framing for bagging vs boosting**: framework_node 67.",
        "- **L1/L2 + gamma regularisation theory**: framework_node 69.",
        "- **Loss-function plug-ins (BCE, L2, Huber, Quantile)**: framework_node 68.",
        "- **CatBoost**: explicitly out of scope here (ordered boosting + symmetric "
        "trees deserve their own pitch); add a separate node if interview signal "
        "warrants it.",
    ])

    # Section 7: Interview self-check
    b.add_checklist("Interview Self-Check", [
        "I can write the XGB structure score and explain why each term is there.",
        "I can name three things LGB does differently from XGB (leaf-wise, GOSS, EFB, native categorical -- pick three).",
        "I can answer 'why is LGB faster on wide datasets?' in two sentences (EFB + GOSS).",
        "I can name a scenario where Random Forest beats GBDT (heavy label noise / small data / training-time-constrained parallel-only).",
        "I know that XGB's sparse-aware split learns a default direction at training time, not at inference.",
        "I can explain why 2nd-order Taylor stabilises the step (Hessian acts as per-sample adaptive learning rate).",
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
    if node_size < 4000:
        print(f"[FAIL] node {NODE_ID} = {node_size} bytes, target >=4000")
        sys.exit(1)
    # Word-count sanity check (combined budget <= 3000 words)
    doc_path = REPO_ROOT / "docs" / DOC_FILENAME
    doc_words = len(doc_path.read_text(encoding="utf-8").split())
    node_words = len(NODE_DESCRIPTION.split())
    total_words = doc_words + node_words
    print(f"[INFO] node words={node_words}, doc words={doc_words}, total={total_words}")
    if total_words > 3000:
        print(f"[WARN] combined word count {total_words} exceeds 3000 budget")
    print(f"[OK] T-P0-447 deliverables: node={node_size}b (>=4000), doc={doc_size} chars.")


if __name__ == "__main__":
    main()
