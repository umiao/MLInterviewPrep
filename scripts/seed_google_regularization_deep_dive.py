"""Seed: Google R1 Regularization deep-dive note (company_id=3).

Covers the 7-point AC from T-P0-430. Each point is a 30-second oral answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3
DOC_TITLE = "Regularization Deep Dive (Google R1 Prep)"


def build_note() -> StudyNoteBuilder:
    """Build the regularization deep-dive study note."""
    b = StudyNoteBuilder()
    b.set_title("Regularization Deep Dive -- Google R1 Prep")

    b.add_prerequisites([
        "Linear regression, gradient descent basics",
        "Bias-variance tradeoff intuition",
        "Neural network training loop (forward/backward pass)",
    ])

    b.add_term("L1", "LASSO / L1 penalty", "Sum of absolute parameter values")
    b.add_term("L2", "Ridge / L2 penalty", "Sum of squared parameter values")
    b.add_term("AdamW", "Adam with decoupled weight decay",
               "Loshchilov & Hutter 2019 fix for Adam + L2 mismatch")
    b.add_term("VRM", "Vicinal Risk Minimization",
               "Augmentation reframes ERM over vicinities of training points")
    b.add_term("Dropout", "Random activation zeroing",
               "Srivastava et al. 2014, interpreted as approximate Bayesian inference")

    # --- AC (1): L1 subgradient geometry ---
    b.add_section("1. L1 -- Why Sparse? (Subgradient Geometry)", [
        "The L1 constraint region is a diamond (cross-polytope). "
        "The loss contours are ellipses. The constrained optimum sits where "
        "ellipse first touches diamond -- which happens at a vertex (axis), "
        "meaning some coordinates are exactly zero.",
        FormulaBlock(
            latex=r"\min_\theta J(\theta) \;\;\text{s.t.}\;\; \|\theta\|_1 \le t",
            explanation="Equivalent constrained form (Lagrangian duality with lambda):",
        ),
        "Subgradient at zero: the subdifferential of |theta_j| at 0 is [-1, +1]. "
        "If the negative gradient of the loss at theta_j=0 falls inside this "
        "interval, the optimum stays at zero -- the parameter is killed.",
        FormulaBlock(
            latex=r"\partial |\theta_j| \big|_{\theta_j=0} = [-1,\,+1]",
            explanation="Subdifferential at the kink:",
        ),
        "Oral shortcut: 'Diamond vertices sit on axes. Ellipse touches vertex "
        "first. That coordinate is zero. More dimensions, more axes to land on, "
        "so L1 gets sparser as p grows.'",
    ])

    # --- AC (2): L2 shrinkage + closed form ---
    b.add_section("2. L2 -- Shrinkage and Closed-Form Solution", [
        "L2 adds a ball constraint. Ellipse touches a smooth sphere, so "
        "the solution is shrunk toward zero but never exactly zero.",
        FormulaBlock(
            latex=r"\hat{w}_{\text{ridge}} = (X^\top X + \lambda I)^{-1} X^\top y",
            explanation="Closed-form Ridge solution (requires only matrix inversion):",
        ),
        "Key insight: lambda I makes the matrix invertible even when X'X is "
        "singular (p > n case). This is why Ridge handles multicollinearity. "
        "The eigenvalues of X'X are shifted by lambda, so small eigenvalues "
        "(unstable directions) get regularized most.",
        FormulaBlock(
            latex=r"\hat{w}_j^{\text{ridge}} = \frac{d_j^2}{d_j^2 + \lambda}\,\hat{w}_j^{\text{OLS}}",
            explanation="Per-eigenvalue shrinkage factor (d_j = j-th singular value of X):",
        ),
        "Oral shortcut: 'Ridge = OLS with inflated diagonal. Small singular values "
        "get shrunk most. Never zero, always dense.'",
    ])

    # --- AC (3): Elastic Net ---
    b.add_section("3. Elastic Net -- Best of Both Worlds", [
        FormulaBlock(
            latex=(
                r"J_{\text{EN}}(\theta) = J(\theta) "
                r"+ \lambda_1 \sum_j |\theta_j| "
                r"+ \lambda_2 \sum_j \theta_j^2"
            ),
            explanation="Elastic Net penalty combines L1 sparsity with L2 grouping:",
        ),
        "Why not just L1? When features are correlated, LASSO arbitrarily picks "
        "one and zeros the rest. Elastic Net's L2 term encourages correlated "
        "features to share weight, then the L1 term selects groups.",
        "Sklearn: `ElasticNet(alpha=a, l1_ratio=r)` where "
        "penalty = a * (r * L1 + (1-r) * L2). "
        "r=1 is LASSO, r=0 is Ridge.",
        "Oral shortcut: 'Elastic Net = group-then-select. L2 keeps correlated "
        "features together; L1 kills entire groups.'",
    ])

    # --- AC (4): Dropout as Bayesian / ensemble ---
    b.add_section("4. Dropout -- Bayesian Approximation and Ensemble View", [
        "Training: each forward pass randomly zeros each unit with probability p. "
        "Inference: use all units, scale activations by (1-p). Inverted dropout "
        "scales during training instead (divide by 1-p) so inference is unchanged.",
        "Ensemble view (Srivastava 2014): With n units, dropout samples from "
        "2^n thinned networks. The averaged prediction approximates an "
        "exponentially large ensemble.",
        "Bayesian view (Gal & Ghahramani 2016): Dropout at test time = "
        "Monte Carlo sampling from an approximate posterior. Running T forward "
        "passes with dropout ON gives predictive mean and uncertainty.",
        FormulaBlock(
            latex=r"\text{Var}[y^*] \approx \frac{1}{T}\sum_{t=1}^{T} f_{\theta_t}(x^*)^2 - \left(\frac{1}{T}\sum_{t=1}^{T} f_{\theta_t}(x^*)\right)^2",
            explanation="MC Dropout variance estimate (each theta_t is a different dropout mask):",
        ),
        "Oral shortcut: 'Dropout = cheap ensemble of 2^n sub-networks. "
        "Keep it on at test time and you get free uncertainty estimates.'",
    ])

    # --- AC (5): Early stopping = implicit L2 ---
    b.add_section("5. Early Stopping -- Implicit L2 Regularization", [
        "Gradient descent with small learning rate from w=0 traces a path through "
        "weight space. Stopping early limits how far w can travel from the origin. "
        "This is equivalent to an L2 penalty whose strength is inversely "
        "proportional to the number of steps.",
        FormulaBlock(
            latex=r"\|w_T\| \le \eta \cdot T \cdot G_{\max}",
            explanation="Norm bound: T steps with learning rate eta and max gradient G:",
        ),
        "Bishop (1995) and Sjoberg & Ljung (1995) showed the formal equivalence: "
        "for quadratic loss, early stopping at step T is equivalent to L2 "
        "regularization with lambda proportional to 1/(eta * T).",
        FormulaBlock(
            latex=r"\lambda_{\text{eff}} \propto \frac{1}{\eta \cdot T}",
            explanation="Effective regularization strength:",
        ),
        "Practical implication: early stopping is the cheapest regularizer -- "
        "no extra hyperparameter beyond patience. But it couples optimization "
        "and regularization, which can be a downside.",
        "Oral shortcut: 'Early stopping = L2 in disguise. Fewer steps = smaller "
        "norm = stronger regularization. Free but couples optimization with "
        "regularization.'",
    ])

    # --- AC (6): L2 vs weight decay in Adam (AdamW) ---
    b.add_section("6. L2 != Weight Decay Under Adam (AdamW Fix)", [
        "In SGD, L2 regularization and weight decay are equivalent:",
        FormulaBlock(
            latex=r"w_{t+1} = w_t - \eta\,(\nabla J + \lambda w_t) = (1 - \eta\lambda)\,w_t - \eta\,\nabla J",
            explanation="SGD with L2 penalty (identical to weight decay factor 1-eta*lambda):",
        ),
        "In Adam, the adaptive per-parameter learning rate breaks this equivalence. "
        "L2 adds lambda*w to the gradient BEFORE the adaptive scaling "
        "(dividing by sqrt(v)). This means the regularization strength varies "
        "per parameter -- parameters with large historical gradients get less "
        "regularization.",
        FormulaBlock(
            latex=r"w_{t+1}^{\text{AdamW}} = (1 - \eta\lambda)\,w_t - \eta\,\frac{m_t}{\sqrt{v_t} + \epsilon}",
            explanation="AdamW: weight decay applied OUTSIDE the adaptive step:",
        ),
        "AdamW (Loshchilov & Hutter 2019) decouples weight decay from the "
        "gradient update. The decay term (1-eta*lambda)*w_t is applied directly, "
        "not filtered through the second moment. This gives uniform regularization "
        "across all parameters.",
        "Oral shortcut: 'Adam's v_t absorbs the L2 gradient, so some weights "
        "barely get regularized. AdamW applies decay after the Adam step, "
        "giving uniform shrinkage. Always use AdamW with transformers.'",
    ])

    # --- AC (7): Data augmentation = VRM ---
    b.add_section("7. Data Augmentation -- Vicinal Risk Minimization", [
        "Standard training minimizes Empirical Risk (ERM): average loss over "
        "the exact training points. Data augmentation replaces each point with "
        "a neighborhood (vicinity) of transformed versions.",
        FormulaBlock(
            latex=r"R_{\text{VRM}} = \frac{1}{n}\sum_{i=1}^{n} \mathbb{E}_{x' \sim \nu(x_i)}[\ell(f(x'), y_i)]",
            explanation="Vicinal Risk: expectation over vicinity distribution nu around each point:",
        ),
        "This is Vicinal Risk Minimization (Chapelle et al. 2000). The vicinity "
        "distribution nu encodes domain knowledge: flips/crops for vision, "
        "synonym replacement for NLP, Mixup for interpolation between points.",
        "Regularization effect: augmentation smooths the decision boundary "
        "because the model must be correct not just at training points but in "
        "their neighborhoods. This reduces variance without increasing bias "
        "(if augmentations are label-preserving).",
        "Oral shortcut: 'Augmentation = training on neighborhoods instead of "
        "points. It smooths the boundary. Formally it is VRM -- the vicinity "
        "kernel replaces the Dirac delta in ERM.'",
    ])

    # --- Summary comparison table ---
    b.add_comparison_table(
        headers=["Method", "What It Constrains", "Oral 10-Second Pitch"],
        rows=[
            ["L1", "Number of active features", "Diamond touches axis vertex => zeros"],
            ["L2 / Ridge", "Magnitude of all weights", "Ball shrinks all; closed-form (X'X+lI)^-1 X'y"],
            ["Elastic Net", "Groups of correlated features", "L2 groups, L1 kills groups"],
            ["Dropout", "Co-adaptation of hidden units", "Ensemble of 2^n sub-nets; MC for uncertainty"],
            ["Early Stopping", "Path length from origin", "Fewer steps = implicit L2; cheapest regularizer"],
            ["AdamW", "Uniform weight magnitude", "Decoupled decay; L2 in Adam is broken"],
            ["Data Aug / VRM", "Decision boundary smoothness", "Train on neighborhoods, not points"],
        ],
        title="7-Method Regularization Panorama",
    )

    b.add_checklist("30-Second Oral Self-Check", [
        "L1 sparsity: diamond geometry + subdifferential at zero",
        "L2 closed-form: (X'X + lambda I)^-1 X'y, per-eigenvalue shrinkage",
        "Elastic Net: group-then-select for correlated features",
        "Dropout: 2^n ensemble + MC Dropout for uncertainty",
        "Early stopping = implicit L2, lambda ~ 1/(eta T)",
        "AdamW: v_t absorbs L2 gradient, so decouple decay",
        "Data aug = VRM: train on vicinities, smooths boundary",
    ])

    return b


def main() -> None:
    """Build and save the regularization deep-dive note."""
    b = build_note()
    content = b.build()

    # Write markdown file
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    out_path = docs_dir / "google_regularization_deep_dive.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {out_path} ({len(content)} chars)")

    # Save to DB
    doc_id = b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)
    print(f"[DONE] DB document id={doc_id}")


if __name__ == "__main__":
    main()
