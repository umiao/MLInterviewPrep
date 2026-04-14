"""Seed: Google R1 Bias/Variance + overfitting diagnosis drill note (company_id=3).

Covers the 5-point AC from T-P0-431. Each section is a 30-second oral answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3
DOC_TITLE = "Bias-Variance + Overfitting Diagnosis Drill (Google R1 Prep)"


def build_note() -> StudyNoteBuilder:
    """Build the bias-variance drill study note."""
    b = StudyNoteBuilder()
    b.set_title("Bias-Variance + Overfitting Diagnosis Drill -- Google R1 Prep")

    b.add_prerequisites([
        "Supervised learning setup (train set, test set, loss function)",
        "Ensemble methods basics (bagging, boosting)",
        "Random Forest and Gradient Boosted Trees",
    ])

    b.add_term("MSE", "Mean Squared Error", "Expected squared prediction error")
    b.add_term("Bias", "Systematic error",
               "Error from wrong model assumptions; underfitting signal")
    b.add_term("Variance", "Sensitivity to training set",
               "Error from model fitting noise; overfitting signal")
    b.add_term("RF", "Random Forest",
               "Bagged deep trees with random feature subsets to reduce correlation")
    b.add_term("GBDT", "Gradient Boosted Decision Trees",
               "Sequential shallow trees that additively reduce bias")
    b.add_term("Bagging", "Bootstrap Aggregating",
               "Train B models on bootstrap samples and average predictions")

    # --- AC (1): Bias-Variance decomposition ---
    b.add_section("1. Bias-Variance Decomposition (Memorize This)", [
        "For a fixed test point x, the expected prediction error over all "
        "possible training sets D of size n decomposes into three irreducible terms:",
        FormulaBlock(
            latex=(
                r"\mathbb{E}_D\!\bigl[(y - f_D(x))^2\bigr]"
                r" = \text{Bias}^2 + \text{Variance} + \sigma^2"
            ),
            explanation="The master equation:",
        ),
        "Where each term is defined as:",
        FormulaBlock(
            latex=(
                r"\text{Bias}^2 = \bigl(\mathbb{E}_D[f_D(x)] - f^*(x)\bigr)^2"
            ),
            explanation="Bias squared: how far the average model is from the truth:",
        ),
        FormulaBlock(
            latex=(
                r"\text{Variance} = \mathbb{E}_D\!\bigl["
                r"(f_D(x) - \mathbb{E}_D[f_D(x)])^2\bigr]"
            ),
            explanation="Variance: how much the model changes across different training sets:",
        ),
        FormulaBlock(
            latex=r"\sigma^2 = \mathbb{E}\!\bigl[(y - f^*(x))^2\bigr]",
            explanation="Irreducible noise: inherent randomness in the data (Bayes error):",
        ),
        "Oral shortcut: 'Expected test MSE = bias-squared plus variance plus noise. "
        "Bias is how wrong the average model is. Variance is how jumpy the model is "
        "across training sets. Noise you cannot touch.'",
    ])

    # --- AC (2): Label cheat sheet ---
    b.add_section("2. Diagnosis Label Cheat Sheet", [
        "The complexity-error relationship drives all diagnosis:",
        FormulaBlock(
            latex=(
                r"\text{Model complexity} \uparrow "
                r"\;\Rightarrow\; \text{Bias} \downarrow,\;"
                r"\text{Variance} \uparrow"
            ),
            explanation="The fundamental tradeoff:",
        ),
    ])

    b.add_comparison_table(
        headers=["Symptom", "Diagnosis", "Fix"],
        rows=[
            ["High train error, high test error", "Underfitting (high bias)",
             "More features, more complex model, less regularization"],
            ["Low train error, high test error", "Overfitting (high variance)",
             "More data, regularization, simpler model, dropout, early stopping"],
            ["Low train error, low test error", "Good fit", "Ship it"],
            ["High train error, low test error", "Data leakage or evaluation bug",
             "Audit pipeline, check for target leakage"],
        ],
        title="4-Quadrant Diagnosis Table",
    )

    b.add_section("2. (continued)", [
        "Oral shortcut: 'Underfit = both errors high = bias dominates. "
        "Overfit = gap between train and test = variance dominates. "
        "Leakage = test better than train = something is wrong.'",
    ])

    # --- AC (3): Bagging variance formula ---
    b.add_section("3. Bagging Variance Formula + RF Insight", [
        "When you average B models, the variance of the ensemble depends on "
        "the pairwise correlation rho between individual model predictions:",
        FormulaBlock(
            latex=(
                r"\text{Var}_{\text{bag}} = \rho\,\sigma_{\text{tree}}^2"
                r" + \frac{1-\rho}{B}\,\sigma_{\text{tree}}^2"
            ),
            explanation="Bagging variance (rho = avg pairwise correlation, sigma^2 = single tree variance):",
        ),
        "As B grows to infinity, the second term vanishes:",
        FormulaBlock(
            latex=(
                r"\lim_{B \to \infty} \text{Var}_{\text{bag}}"
                r" = \rho\,\sigma_{\text{tree}}^2"
            ),
            explanation="The floor: more trees cannot reduce variance below rho * sigma^2:",
        ),
        "This is the key insight: bagging alone hits a floor determined by "
        "correlation rho. Random Forest breaks this floor by randomly selecting "
        "m features at each split (typically m = sqrt(p) for classification, "
        "m = p/3 for regression). This de-correlates the trees, lowering rho, "
        "and thus lowering the variance floor.",
        "Oral shortcut: 'Bagging's variance floor is rho * sigma-squared. "
        "RF lowers rho by randomizing features at each split. "
        "Lower rho = lower floor = better ensemble.'",
    ])

    # --- AC (4): RF deep trees vs GBDT shallow trees ---
    b.add_section("4. RF Deep Trees vs GBDT Shallow Trees (Dual Aesthetics)", [
        "RF and GBDT attack the bias-variance tradeoff from opposite ends:",
    ])

    b.add_comparison_table(
        headers=["", "Random Forest", "GBDT"],
        rows=[
            ["Base learner", "Deep, unpruned trees (low bias, high variance)",
             "Shallow trees / stumps (high bias, low variance)"],
            ["Ensemble strategy", "Parallel (bagging) -- reduces variance",
             "Sequential (boosting) -- reduces bias"],
            ["Overfitting risk", "Rarely overfits by adding more trees",
             "Can overfit if too many rounds or too deep"],
            ["Key hyperparams", "n_estimators, max_features",
             "n_estimators, learning_rate, max_depth"],
            ["Bias-variance lever", "Random feature subsets lower rho (variance)",
             "Each tree fits residual (bias reduction)"],
        ],
        title="RF vs GBDT Duality",
    )

    b.add_section("4. (continued)", [
        "Why this duality works: RF starts with high-variance base learners and "
        "averages them to reduce variance. GBDT starts with high-bias base "
        "learners and sequentially corrects them to reduce bias. Both arrive at "
        "a sweet spot from opposite directions.",
        FormulaBlock(
            latex=(
                r"\text{RF: } f(x) = \frac{1}{B}\sum_{b=1}^{B} T_b(x)"
                r"\qquad\text{(average of deep trees)}"
            ),
            explanation="RF averages independent deep trees:",
        ),
        FormulaBlock(
            latex=(
                r"\text{GBDT: } f(x) = \sum_{m=1}^{M} \eta\,h_m(x)"
                r"\qquad\text{(sum of shallow trees on residuals)}"
            ),
            explanation="GBDT additively combines shallow trees with learning rate eta:",
        ),
        "Oral shortcut: 'RF = deep trees averaged to kill variance. "
        "GBDT = shallow trees stacked to kill bias. Opposite entry points, "
        "same destination.'",
    ])

    # --- AC (5): Learning curve reading ---
    b.add_section("5. Learning Curve -- Four Diagnostic Shapes", [
        "Plot train error and validation error as a function of training set size. "
        "The shape tells you what is wrong and what will help:",
    ])

    b.add_comparison_table(
        headers=["Shape", "Train Error", "Val Error", "Diagnosis", "Action"],
        rows=[
            ["Large gap, both converging",
             "Low", "High but decreasing",
             "High variance (overfit)", "More data will help; or regularize"],
            ["Small gap, both high",
             "High", "High, close to train",
             "High bias (underfit)", "More data will NOT help; need more capacity"],
            ["Gap closes, both low",
             "Low", "Low, converging to train",
             "Good fit", "Optimal complexity; more data gives diminishing returns"],
            ["Train stays near zero, val flat high",
             "Near zero", "High, flat",
             "Severe overfit + memorization",
             "Model memorizes; need regularization or simpler model, not more data"],
        ],
        title="Learning Curve Diagnostic Shapes",
    )

    b.add_section("5. (continued)", [
        "Key rules of thumb for reading learning curves:",
        "- If train-val gap is large: variance problem. More data or regularization.",
        "- If both curves plateau high: bias problem. More features or capacity.",
        "- If train error = 0: model memorizes. Red flag for overfitting.",
        "- Convergence level indicates irreducible error (Bayes rate) under "
        "the current model class.",
        "",
        "Oral shortcut: 'Big gap = variance, add data. Both high = bias, add "
        "capacity. Train zero + val high = memorizing, regularize.'",
    ])

    # --- Summary checklist ---
    b.add_checklist("2-Minute Oral Self-Check", [
        "Write E_D[(y-f_D)^2] = Bias^2 + Var + sigma^2 from memory",
        "Name all three terms and what each means in one sentence",
        "Complexity up => bias down, variance up (say it)",
        "Underfit = both errors high; overfit = gap between train and test",
        "Bagging variance = rho*sigma^2 + (1-rho)/B*sigma^2, floor at rho*sigma^2",
        "RF lowers rho by randomizing features; GBDT reduces bias sequentially",
        "RF = deep trees averaged; GBDT = shallow trees stacked (opposite entry points)",
        "Learning curve: big gap = variance; both high = bias; train=0 = memorizing",
    ])

    return b


def main() -> None:
    """Build and save the bias-variance drill note."""
    b = build_note()
    content = b.build()

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    out_path = docs_dir / "google_bias_variance_drill.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {out_path} ({len(content)} chars)")

    doc_id = b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)
    print(f"[DONE] DB document id={doc_id}")


if __name__ == "__main__":
    main()
