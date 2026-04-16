"""Seed: Google R1 Calibration drill note (company_id=3).

Covers T-P0-417 AC:
 (1) Platt = logistic over logit,
 (2) Isotonic preserves ranking, coarse granularity,
 (3) Temperature only tunes T, does not change argmax,
 (4) Reliability diagram / ECE,
 (5) Why GMB bidding needs calibrated probabilities.

Each section is a 30-60 second oral answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3
DOC_TITLE = "Calibration Drill: Platt / Isotonic / Temperature + GMB Bidding Trap (Google R1 Prep)"


def build_note() -> StudyNoteBuilder:
    """Build the calibration drill study note."""
    b = StudyNoteBuilder()
    b.set_title("Calibration Drill -- Platt / Isotonic / Temperature + GMB Bidding Trap")

    b.add_prerequisites([
        "Binary / multiclass classification, logits and softmax",
        "Logistic regression, MLE / cross-entropy loss",
        "Second-price auction basics (value * P = expected payoff)",
    ])

    b.add_term("ECE", "Expected Calibration Error",
               "Weighted average gap between predicted confidence and empirical accuracy across bins")
    b.add_term("Platt", "Platt Scaling",
               "Two-parameter logistic fit on raw logits; turns monotone scores into probabilities")
    b.add_term("Isotonic", "Isotonic Regression",
               "Non-parametric piecewise-constant monotone mapping via Pool-Adjacent-Violators")
    b.add_term("Temperature", "Temperature Scaling",
               "Single-parameter rescaling of logits by 1/T before softmax; preserves argmax")
    b.add_term("NLL", "Negative Log-Likelihood",
               "Cross-entropy loss; objective minimized during temperature fit")
    b.add_term("GMB", "Google Marketing Bidding",
               "Ad auction bidding where bid = value * calibrated P(action); miscalibration = systematic over/under-bid")

    # --- Section 0: Why calibration matters ---
    b.add_section("0. Why Calibration Matters (The Framing)", [
        "A classifier can be discriminative (high AUC, correct ranking) yet "
        "badly miscalibrated: the number it emits is not a probability. "
        "For any decision based on expected value -- bidding, triage, "
        "cost-sensitive routing -- the magnitude of P matters, not just the rank.",
        FormulaBlock(
            latex=r"\text{Perfect calibration: } \Pr(Y=1 \mid \hat{p}(x)=p) = p \quad \forall p \in [0,1]",
            explanation="Definition: among inputs where the model says p=0.3, exactly 30% are positive.",
        ),
        "Modern neural nets are notoriously over-confident. Guo et al. 2017 "
        "showed ResNet confidences on CIFAR-100 cluster near 1.0 while accuracy "
        "sits around 0.75 -- ECE jumps from ~2% (LeNet) to ~15% (ResNet-110).",
        "Oral shortcut: 'AUC measures ranking. Calibration measures whether "
        "the probability can be trusted as a probability. Bidding, triage, "
        "and any expected-value decision depend on the second, not the first.'",
    ])

    # --- AC (1): Platt scaling ---
    b.add_section("1. Platt Scaling = Logistic Over the Logit", [
        "Platt (1999) fits a two-parameter logistic on top of the raw model "
        "score z (or logit). Two scalars A, B, fit by MLE on a held-out "
        "calibration set:",
        FormulaBlock(
            latex=r"\hat{p}(x) = \sigma(A \cdot z(x) + B), \qquad \sigma(u) = \frac{1}{1 + e^{-u}}",
            explanation="Platt mapping: pass the raw logit through a learned sigmoid:",
        ),
        FormulaBlock(
            latex=(
                r"(A^*, B^*) = \arg\min_{A,B} "
                r"-\sum_i \bigl[y_i \log \sigma(A z_i + B) "
                r"+ (1-y_i) \log(1 - \sigma(A z_i + B))\bigr]"
            ),
            explanation="Parameters estimated by minimizing NLL on the calibration split:",
        ),
        "When it works: scores are already roughly linear in log-odds -- SVM "
        "margins, linear models, shallow NNs. Platt only has two degrees of "
        "freedom, so it cannot fix a fundamentally non-monotone distortion.",
        "Pitfall: fitting Platt on the training set leaks -- use a held-out "
        "calibration set (10-20%) or cross-validated fold-out. Platt smoothing "
        "uses pseudo-labels y' = (N_+ + 1) / (N_+ + 2) to avoid over-confidence "
        "at the boundary.",
        "Oral shortcut: 'Platt = two-parameter logistic regression on the "
        "logit. Works when scores are already near-linear in log-odds. "
        "Fit on a held-out set, never on train.'",
    ])

    # --- AC (2): Isotonic regression ---
    b.add_section("2. Isotonic Regression -- Rank Preserving, Coarse Granularity", [
        "Isotonic regression fits a non-parametric monotone non-decreasing "
        "step function m: [0,1] -> [0,1] that maps raw scores to calibrated "
        "probabilities, minimizing weighted squared error subject to "
        "monotonicity:",
        FormulaBlock(
            latex=(
                r"\min_{m} \sum_i \bigl(y_i - m(z_i)\bigr)^2 "
                r"\quad \text{s.t.} \quad z_i \le z_j \Rightarrow m(z_i) \le m(z_j)"
            ),
            explanation="Objective: squared error with a monotone constraint on the mapping:",
        ),
        "Solved by the Pool-Adjacent-Violators (PAV) algorithm in O(n) after "
        "sorting. Output is a piecewise-constant staircase.",
        "Because m is monotone, the ordering of predictions is preserved -- "
        "so AUC, NDCG, and any ranking metric are unchanged. Only the "
        "probability magnitude shifts.",
        "Granularity tradeoff: PAV merges adjacent bins whenever they violate "
        "monotonicity, so the output is coarse -- you get a small number of "
        "distinct probability values (the count depends on data). This is "
        "more flexible than Platt (no linearity assumption) but needs more "
        "calibration data (~1000+ examples) to avoid overfitting.",
        "When to prefer over Platt: scores have non-sigmoidal shape, or you "
        "have abundant calibration data. When to prefer Platt: small "
        "calibration set, or the distortion is close to a sigmoid.",
        "Oral shortcut: 'Isotonic = PAV-fit monotone step function. Preserves "
        "ranking so AUC is untouched, but output is coarse and needs "
        "more data than Platt.'",
    ])

    # --- AC (3): Temperature scaling ---
    b.add_section("3. Temperature Scaling -- Only Tunes T, Argmax Unchanged", [
        "For multiclass logits z in R^K, temperature scaling divides by a "
        "single positive scalar T before softmax:",
        FormulaBlock(
            latex=(
                r"\hat{p}_k(x) = \frac{\exp(z_k(x)/T)}{\sum_{j=1}^{K} \exp(z_j(x)/T)}"
            ),
            explanation="Temperature-scaled softmax: divide logits by T, then softmax as usual:",
        ),
        "Fit T on a held-out validation set by minimizing NLL:",
        FormulaBlock(
            latex=(
                r"T^* = \arg\min_{T > 0} -\sum_i \log \hat{p}_{y_i}(x_i; T)"
            ),
            explanation="One-dimensional convex optimization (scipy.optimize on a scalar):",
        ),
        "The critical property: because softmax is invariant to monotone "
        "rescaling of all logits, the argmax is unchanged:",
        FormulaBlock(
            latex=(
                r"\arg\max_k \hat{p}_k(x; T) = \arg\max_k z_k(x) "
                r"\quad \forall T > 0"
            ),
            explanation="Argmax does not depend on T; accuracy and top-k metrics are preserved exactly:",
        ),
        "Interpretation: T > 1 softens confidence (smooths the distribution); "
        "T < 1 sharpens it. Overconfident models need T > 1.",
        "Why it dominates for deep nets: one parameter, cannot overfit the "
        "calibration set, trivially reversible, and leaves downstream argmax "
        "decisions untouched. Guo et al. 2017 showed it reduces ResNet ECE "
        "from 15% to ~1% on CIFAR-100.",
        "Limitations: T is a global scalar. It cannot fix per-class "
        "miscalibration or non-monotone distortions -- for that, use "
        "vector scaling or Dirichlet calibration.",
        "Oral shortcut: 'Temperature scaling = divide logits by one scalar T, "
        "fit on val NLL. Only reshapes confidence, never flips predictions, "
        "and the default fix for deep net overconfidence.'",
    ])

    # --- Comparison table: three methods ---
    b.add_section("4. Three Methods at a Glance", [
        "Pick by calibration set size, expected shape of distortion, and "
        "whether you need argmax invariance:",
    ])

    b.add_comparison_table(
        headers=["", "Platt", "Isotonic", "Temperature"],
        rows=[
            ["Parameters", "2 (A, B)", "O(unique z)", "1 (T)"],
            ["Rank preserving?", "Yes (monotone sigmoid)", "Yes (monotone step)", "Yes (argmax unchanged)"],
            ["Output granularity", "Smooth", "Coarse (step function)", "Smooth"],
            ["Min calibration data", "~100", "~1000", "~50"],
            ["Best for", "Small data, sigmoid-ish distortion", "Large data, unknown shape", "Deep nets, global overconfidence"],
            ["Typical use", "SVM, shallow models", "GBDT, arbitrary models", "CNNs, transformers"],
            ["Risk", "Underfits non-sigmoid shape", "Overfits on small sets", "Cannot fix per-class bias"],
        ],
        title="Platt vs Isotonic vs Temperature",
    )

    # --- AC (4): Reliability diagram + ECE ---
    b.add_section("5. Reliability Diagram + ECE", [
        "To audit calibration: bin predicted probabilities into M equal-width "
        "bins B_1, ..., B_M (typically M = 10 or 15). For each bin compute "
        "average predicted confidence and empirical accuracy:",
        FormulaBlock(
            latex=(
                r"\text{conf}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} \hat{p}_i, "
                r"\quad "
                r"\text{acc}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} \mathbb{1}[\hat{y}_i = y_i]"
            ),
            explanation="Per-bin average confidence and empirical accuracy:",
        ),
        "Plot acc(B_m) on the y-axis vs conf(B_m) on the x-axis. Perfect "
        "calibration is the y = x diagonal. Points above the diagonal mean "
        "under-confident; below means over-confident.",
        FormulaBlock(
            latex=(
                r"\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} "
                r"\bigl|\text{acc}(B_m) - \text{conf}(B_m)\bigr|"
            ),
            explanation="ECE summarizes the whole diagram as one number: weighted L1 gap:",
        ),
        "Production targets: ECE < 2% on held-out is generally safe for "
        "bidding and ranking downstream; ECE > 5% is a red flag. Always pair "
        "ECE with a reliability diagram -- ECE can hide offsetting errors "
        "(over-confidence in one bin, under-confidence in another).",
        "Sibling metrics: MCE (Maximum Calibration Error, worst bin) for "
        "tail-risk audits; Brier score = mean squared error on probabilities, "
        "which decomposes into calibration + refinement + irreducible noise.",
        "Oral shortcut: 'Reliability diagram = per-bin confidence vs accuracy "
        "against y=x. ECE = bin-weighted L1 gap. Want ECE under 2%, and "
        "never trust ECE without looking at the diagram.'",
    ])

    # --- AC (5): GMB bidding calibration trap ---
    b.add_section("6. GMB Bidding Calibration Trap (The Business Why)", [
        "In a second-price Vickrey auction with expected-value bidding, "
        "the optimal truthful bid for a click-to-conversion ad is:",
        FormulaBlock(
            latex=(
                r"\text{bid}^* = v \cdot \Pr(\text{conversion} \mid \text{click}, x)"
            ),
            explanation="Bid equals advertiser value times calibrated conversion probability:",
        ),
        "Concrete CPA (cost-per-acquisition) target: bid = target_CPA * pCVR, "
        "where pCVR is the model's predicted conversion rate. The expected "
        "cost-per-acquisition only equals the target when pCVR is calibrated.",
        "The trap: if the model is miscalibrated by a global factor k "
        "(pCVR = k * true_CVR everywhere), AUC is perfect, but every bid is "
        "off by k. Over-prediction (k > 1) burns budget on losing auctions; "
        "under-prediction (k < 1) misses winnable auctions. The ranking of "
        "candidate ads may be identical, yet the spend profile is systematically wrong.",
        FormulaBlock(
            latex=(
                r"\text{If } \hat{p} = k \cdot p, \text{ then } "
                r"\mathbb{E}[\text{CPA}] = \frac{\text{target\_CPA}}{k}"
            ),
            explanation="A calibration factor k bakes directly into realized CPA:",
        ),
        "Why offline AUC does not catch this: AUC depends only on pairwise "
        "ranking. Any monotone transformation of scores leaves AUC unchanged, "
        "but shifts the probability magnitudes that set bid levels. This is "
        "why ad systems calibrate at serving time even when AUC is healthy.",
        "Second-order traps: miscalibration often interacts with feature drift "
        "(weekend / holiday traffic) and with auction-density shifts, so "
        "calibration must be monitored on a sliding window (daily ECE + "
        "reliability plot), not just at model launch.",
        "Production pattern: train a discriminative model (XGBoost / DNN) for "
        "AUC, then fit isotonic or Platt on a recent sliding window, "
        "refreshed daily. Temperature scaling is popular for DNN-based "
        "models; isotonic for GBDT-based models.",
        "Oral shortcut: 'In GMB bidding, bid = value * P(action). AUC sees "
        "ranking, calibration sees magnitude. Miscalibration by factor k "
        "means CPA misses target by factor 1/k. Calibrate on a sliding "
        "window at serve time, and monitor ECE daily.'",
    ])

    # --- Numerical toy ---
    b.add_section("7. Numerical Sanity Check (k = 1.5 Over-Confidence)", [
        "Suppose target CPA = 10 USD and true CVR on a slice is 0.04. "
        "Calibrated optimal bid = 10 * 0.04 = 0.40 USD, realized CPA = 10 USD "
        "on that slice.",
        "Miscalibrated model predicts pCVR = 0.06 (k = 1.5). Bid = 10 * 0.06 "
        "= 0.60 USD. Realized cost per conversion = bid / true_CVR = 0.60 / "
        "0.04 = 15 USD. Overspend of 50% per acquisition, with AUC unchanged "
        "because the ranking across slices is preserved.",
        "Under-calibration (k = 0.5) would bid 0.20 USD, losing most auctions "
        "and starving the campaign, again with identical AUC.",
        "Takeaway: a single global k visible only in the reliability diagram "
        "can drive a 50% CPA miss while every offline ranking metric stays green.",
    ])

    # --- Summary checklist ---
    b.add_checklist("2-Minute Oral Self-Check", [
        "Define calibration: Pr(Y=1 | p_hat=p) = p for all p",
        "Platt = sigmoid(A*z + B), 2 params, fit by NLL on held-out set",
        "Isotonic = PAV, monotone step, rank preserving, coarse, needs ~1000+",
        "Temperature = softmax(z / T), single scalar, argmax unchanged, NLL-fit",
        "Reliability diagram: bin-wise conf vs acc against y=x diagonal",
        "ECE = sum |B_m|/N * |acc - conf| over bins; target < 2% in prod",
        "AUC is rank-only; calibration sets magnitude; both matter for bidding",
        "Second-price bid = value * P(action); miscalibration by k => CPA off by 1/k",
        "Calibrate on sliding window at serve time; monitor ECE daily",
        "Platt for small data + sigmoid-ish; Isotonic for large data + unknown shape; Temperature for deep nets",
    ])

    return b


def main() -> None:
    """Build and save the calibration drill note."""
    b = build_note()
    content = b.build()

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    out_path = docs_dir / "google_calibration_drill.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {out_path} ({len(content)} chars)")

    doc_id = b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)
    print(f"[DONE] DB document id={doc_id}")


if __name__ == "__main__":
    main()
