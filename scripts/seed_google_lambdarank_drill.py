"""Seed: Google R1 LambdaRank/LambdaMART derivation drill (company_id=3).

Covers the 4-point AC from T-P0-415:
(1) RankNet pairwise sigmoid loss from memory
(2) LambdaRank weighting pairwise gradient with deltaNDCG
(3) Pointwise BCE / pairwise / listwise (ListNet softmax) when-to-use matrix
(4) Sale NDCG -> GMB bidding story hook (eBay Ranking-as-Allocation)

Reference: docs/prep_learning_to_rank.md, docs/doordash_ml_domain_ranking.md section 4.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3
DOC_TITLE = "LambdaRank / LambdaMART Drill (Google R1 Prep)"


def build_note() -> StudyNoteBuilder:
    """Build the LambdaRank/LambdaMART drill study note."""
    b = StudyNoteBuilder()
    b.set_title("LambdaRank / LambdaMART Derivation Drill -- Google R1 Prep")

    b.add_prerequisites([
        "Supervised learning, cross-entropy loss, sigmoid gradient",
        "Gradient Boosted Decision Trees (MART / XGBoost / LightGBM)",
        "NDCG / DCG definitions (see google_ndcg_map_mrr_drill.md companion)",
    ])

    b.add_term("LTR", "Learning to Rank",
               "Supervised training of a scoring function over (query, doc) pairs")
    b.add_term("RankNet", "Pairwise cross-entropy ranking loss (Burges 2005)",
               "Logistic loss on score difference s_i - s_j for labelled pair (i,j)")
    b.add_term("LambdaRank", "NDCG-weighted pseudo-gradient (Burges 2006)",
               "lambda_ij = RankNet gradient scaled by |deltaNDCG_ij| swap impact")
    b.add_term("LambdaMART", "LambdaRank gradients plugged into MART / GBDT",
               "Industry-standard LTR: XGBoost rank:ndcg, LightGBM LambdaRank")
    b.add_term("DCG", "Discounted Cumulative Gain",
               "Sum of (2^y - 1) / log2(i+1) over top-K positions")
    b.add_term("NDCG", "Normalized DCG",
               "DCG divided by IDCG (ideal ordering) -- per-query normalization")
    b.add_term("BCE", "Binary Cross-Entropy",
               "Pointwise logistic loss for click/purchase prediction")
    b.add_term("ListNet", "Listwise softmax cross-entropy over top-1 distribution",
               "Loss compares softmax(s) to softmax(y) over all docs of a query")

    # ---------- AC (1): RankNet pairwise sigmoid loss ----------
    b.add_section("1. RankNet -- Pairwise Sigmoid Loss (Memorize This)", [
        "Setup: query q with candidate docs; labelled pair (i, j) has y_i > y_j. "
        "Model produces scalar scores s_i = f(x_i), s_j = f(x_j). "
        "Goal: push s_i above s_j.",
        FormulaBlock(
            latex=r"P_{ij} \;=\; \Pr(i \succ j) \;=\; \sigma\!\bigl(s_i - s_j\bigr) \;=\; \frac{1}{1 + e^{-(s_i - s_j)}}",
            explanation="Model the pairwise preference as a sigmoid of the score gap:",
        ),
        FormulaBlock(
            latex=r"\mathcal{L}_{ij} \;=\; -\log P_{ij} \;=\; \log\!\bigl(1 + e^{-(s_i - s_j)}\bigr)",
            explanation="Cross-entropy target is 1 (i should outrank j), so the loss is:",
        ),
        "Gradient drop (key for the live board):",
        FormulaBlock(
            latex=(
                r"\frac{\partial \mathcal{L}_{ij}}{\partial s_i}"
                r" \;=\; -\,(1 - P_{ij})"
                r"\qquad"
                r"\frac{\partial \mathcal{L}_{ij}}{\partial s_j}"
                r" \;=\; +\,(1 - P_{ij})"
            ),
            explanation="Symmetric: push s_i up, push s_j down by the same amount.",
        ),
        "Oral shortcut: 'RankNet = logistic loss on score difference. "
        "Gradient magnitude is 1 - P_ij -- big when the model is wrong "
        "(P_ij close to 0), zero when the model is right.'",
        "Fatal limitation: every misranked pair is weighted equally. "
        "Swapping positions 1 and 2 costs the same as swapping positions "
        "99 and 100, but the top pair hurts users far more.",
    ])

    # ---------- AC (2): LambdaRank deltaNDCG weighting ----------
    b.add_section("2. LambdaRank -- deltaNDCG-Weighted Pairwise Gradient", [
        "Trick: do not differentiate NDCG (argsort is discrete). "
        "Instead, multiply the RankNet per-pair gradient by the absolute "
        "NDCG change |deltaNDCG_ij| that would result from swapping "
        "the two documents' positions.",
        FormulaBlock(
            latex=(
                r"\lambda_{ij} \;=\; \underbrace{-\,(1 - P_{ij})}_{\text{RankNet grad}}"
                r"\;\cdot\;\underbrace{\bigl|\Delta\mathrm{NDCG}_{ij}\bigr|}_{\text{swap impact}}"
            ),
            explanation="Lambda gradient = RankNet direction times swap magnitude:",
        ),
        FormulaBlock(
            latex=(
                r"\bigl|\Delta\mathrm{NDCG}_{ij}\bigr| \;=\; \frac{1}{\mathrm{IDCG}}"
                r"\,\bigl|\,2^{y_i} - 2^{y_j}\bigr|"
                r"\,\left|\,\frac{1}{\log_2(p_i + 1)} - \frac{1}{\log_2(p_j + 1)}\right|"
            ),
            explanation="Swap delta: only the two positions' DCG contributions change.",
        ),
        "Per-document aggregation -- each doc sums over every pair it is in:",
        FormulaBlock(
            latex=(
                r"\lambda_i \;=\; \sum_{j\,:\,y_i > y_j} \lambda_{ij}"
                r"\;-\; \sum_{j\,:\,y_j > y_i} \lambda_{ji}"
            ),
            explanation="Pseudo-gradient on doc i. Negative lambda_i pushes score up.",
        ),
        "LambdaMART = feed (lambda_i, w_i) to MART as (gradient, hessian). "
        "The Hessian approximation is w_ij = P_ij (1 - P_ij) * |deltaNDCG_ij|. "
        "Tree splitting and leaf values are identical to vanilla XGBoost -- "
        "only the gradient source changes.",
        "Why this concentrates capacity at the top: near position 1 the "
        "1/log2(p+1) discount is ~1, near position 100 it is ~0.14, so the "
        "same label swap produces a 7x larger |deltaNDCG| at the top. "
        "Self-regulating convergence: as ranking approaches ideal, both "
        "(1 - P_ij) and |deltaNDCG_ij| shrink -- updates vanish on their own.",
        "Oral shortcut: 'LambdaRank = RankNet gradient times |deltaNDCG| of "
        "the swap. Top-of-list misorderings get large deltaNDCG and dominate "
        "the gradient. LambdaMART plugs these pseudo-gradients into GBDT.'",
    ])

    # ---------- AC (3): Pointwise BCE / Pairwise / Listwise comparison ----------
    b.add_section("3. Pointwise BCE vs Pairwise vs ListNet (When to Use Which)", [
        "The three LTR paradigms differ in the unit of the loss:",
    ])

    b.add_comparison_table(
        headers=["Paradigm", "Loss formula", "Per query complexity", "When to pick"],
        rows=[
            [
                "Pointwise BCE",
                "L = sum_i [ -y_i log sigma(s_i) - (1 - y_i) log(1 - sigma(s_i)) ]",
                "O(n)",
                "Binary engagement labels (click / purchase); "
                "need calibrated probabilities; CTR, pOrder heads in MTL",
            ],
            [
                "Pairwise (RankNet)",
                "L = sum_{i>j} log(1 + exp(-(s_i - s_j)))",
                "O(n^2) pairs (sampleable)",
                "Preference pairs available; want relative ordering "
                "without caring about absolute score calibration",
            ],
            [
                "Listwise (ListNet)",
                "L = - sum_i softmax(y)_i * log softmax(s)_i",
                "O(n) with one softmax per query",
                "Full query list; want the top-1 distribution to match "
                "the label distribution; smooth listwise surrogate",
            ],
            [
                "Listwise (LambdaMART)",
                "pseudo-grad lambda_i = sum_j RankNet * |deltaNDCG|",
                "O(n^2) pairs per query",
                "Graded relevance + ranking metric (NDCG / MAP) is the "
                "business goal; GBDT-friendly; production default",
            ],
        ],
        title="LTR Paradigm Cheat Sheet",
    )

    b.add_section("3. (continued)", [
        "Key decision rules:",
        "- If the label is a scalar probability (click / order), start with "
        "pointwise BCE. It is cheap, parallelizable across docs, and gives "
        "calibrated scores usable for bidding and threshold decisions.",
        "- If you only care about the order (recall tasks, candidate "
        "generation re-ranking), pairwise is the minimal upgrade that "
        "teaches the model about relative preference.",
        "- If graded relevance labels exist and NDCG is the headline "
        "metric, go listwise -- LambdaMART in production (GBDT), ListNet "
        "or ApproxNDCG in neural stacks. These are the only losses that "
        "are position-aware by construction.",
        "- In multi-task ranking (DoorDash / eBay feed, Etsy search) "
        "pointwise MTL heads (pClick, pOrder, pGMV) are combined in a "
        "linear fusion score; pure listwise is rarer because you want "
        "calibrated heads for downstream bidding.",
        "Oral shortcut: 'Pointwise for calibrated heads, pairwise for "
        "order-only tasks, listwise (LambdaMART) when graded NDCG is the "
        "target. ListNet softmax is the smooth listwise option for neural "
        "rankers when you do not want GBDT.'",
    ])

    # ---------- AC (4): Sale NDCG -> GMB bidding story hook ----------
    b.add_section("4. Story Hook -- Sale NDCG to GMB Bidding (eBay Ranking-as-Allocation)", [
        "The Google panel loves to push: 'so you picked NDCG, why is that "
        "the right objective?' The best answer is the Sale-NDCG cautionary "
        "tale because it shows you know NDCG's failure modes, not just the "
        "formula.",
        "30-second story arc:",
        "- Team optimized Sale NDCG = NDCG weighted by purchase conversion. "
        "Standard choice. Shipped fine for years.",
        "- Discovered systematic bias: cheap items have higher conversion "
        "rates, so Sale NDCG ranked a \\$5 accessory above a \\$100 necklace. "
        "Local metric up, marketplace GMB (Gross Merchandise Bought) flat.",
        "- Root cause: Sale NDCG's gain = 2^y - 1 ignored item value. "
        "LambdaMART was faithfully optimizing a misaligned surrogate.",
        "- Fix: re-cast ranking as an allocation problem -- predict pClick, "
        "pOrder, expected revenue per exposure separately (pointwise MTL, "
        "BCE / regression heads), then allocate slots by a GMB-bid score "
        "w1 * pClick + w2 * pOrder + w3 * pOrder * value - w4 * risk. "
        "This is Ranking-as-Allocation.",
        "- Result: +1% GMB on the first A/B, and the allocation primitive "
        "generalized to Ads, Monetization, promo modules.",
        "Why this lands for a Google ranking role:",
        "- Shows deep understanding that NDCG is a surrogate, not a business "
        "objective. LambdaMART optimizing NDCG perfectly can still hurt GMB.",
        "- Demonstrates fluency in the pointwise MTL + score fusion pattern "
        "that dominates modern e-commerce ranking (DoorDash section 3 fusion "
        "score is structurally identical).",
        "- Gives a concrete bridge to calibration: GMB bidding fails if "
        "pClick / pOrder are miscalibrated -- connects naturally to the "
        "calibration drill (T-P0-417) if asked.",
        "Oral shortcut: 'NDCG is a surrogate. Sale NDCG ignored item value "
        "-- cheap items beat expensive ones on rank. Fix was Ranking-as-"
        "Allocation: calibrated MTL heads fused into a GMB bid score. "
        "+1% GMB first experiment.'",
    ])

    # ---------- Summary checklist ----------
    b.add_checklist("2-Minute Oral Self-Check", [
        "Write RankNet loss: log(1 + exp(-(s_i - s_j))) from memory",
        "State RankNet gradient dL/ds_i = -(1 - P_ij)",
        "Name the fatal flaw of RankNet (all pairs weighted equally)",
        "Write lambda_ij = -(1 - P_ij) * |deltaNDCG_ij| from memory",
        "Explain why |deltaNDCG| concentrates capacity at the top (discount 1/log2 is larger there)",
        "LambdaMART = (lambda_i, w_i) fed to GBDT as (gradient, hessian)",
        "Pointwise BCE -- when (calibrated click / order heads, MTL)",
        "Pairwise RankNet -- when (order-only, no graded labels)",
        "Listwise (ListNet / LambdaMART) -- when (graded labels, NDCG goal)",
        "Sale NDCG story: cheap items beat expensive ones -> Ranking-as-Allocation -> +1% GMB",
        "Bridge to calibration: GMB bidding needs calibrated pClick/pOrder",
    ])

    return b


def main() -> None:
    """Build and save the LambdaRank/LambdaMART drill note."""
    b = build_note()
    content = b.build()

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    out_path = docs_dir / "google_lambdarank_drill.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {out_path} ({len(content)} chars)")

    doc_id = b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)
    print(f"[DONE] DB document id={doc_id}")


if __name__ == "__main__":
    main()
