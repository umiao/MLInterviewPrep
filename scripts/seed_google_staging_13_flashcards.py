"""Seed: Google R1 staging 13-question flashcards (company_id=3).

Compresses the 13 weak-spot diagnostic blocks from mock interview into
Q/A flash cards. Each answer is under 100 words with at least one formula
or numeric example. Ends with 3 mnemonics + 30-min pre-interview checklist.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3
DOC_TITLE = "Staging 13 Flashcards (Google R1 Prep)"
OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "google_staging_13_flashcards.md"
)


def build_note() -> StudyNoteBuilder:
    """Build the 13-card flashcard study note."""
    b = StudyNoteBuilder()
    b.set_title(
        "Google R1 Staging -- 13 Flashcards (2-min Oral Answers)"
    )

    b.add_prerequisites([
        "ML fundamentals (loss, gradient, regularization)",
        "Deep learning basics (backprop, optimizers, normalization)",
        "Embedding methods (word2vec, contrastive learning)",
    ])

    b.add_term("GBDT", "Gradient Boosted Decision Trees",
               "Sequential shallow trees fitting negative gradients")
    b.add_term("BN", "Batch Normalization",
               "Normalize per-channel over (N,H,W); uses running stats at inference")
    b.add_term("LN", "Layer Normalization",
               "Normalize per-sample over (C,H,W); no batch dependency")
    b.add_term("SGNS", "Skip-Gram Negative Sampling",
               "Binary-classification word embedding; implicit PMI factorization")
    b.add_term("InfoNCE", "Info Noise-Contrastive Estimation",
               "(k+1)-class softmax loss for contrastive learning")
    b.add_term("AdamW", "Adam with decoupled Weight decay",
               "Fixes L2 dilution in Adam by applying decay outside adaptive step")

    # --- Card 1: Bias-Variance ---
    b.add_section("Card 1: Bias-Variance Decomposition", [
        "**Q:** Write the bias-variance decomposition and state which direction "
        "each term moves when model complexity increases.",
        "",
        "**A:**",
        FormulaBlock(
            latex=(
                r"\mathbb{E}_D[(y - f_D(x))^2]"
                r" = \text{Bias}^2 + \text{Variance} + \sigma^2"
            ),
        ),
        "Complexity up: Bias down (more flexible), Variance up (data-sensitive). "
        "Mnemonic: **complex = low bias + high variance**. "
        "Bagging (RF) averages B models to cut variance; floor is "
        "$\\rho\\sigma^2$ where $\\rho$ is pairwise correlation -- "
        "RF uses random feature subsets to lower $\\rho$. "
        "Boosting (GBDT) stacks shallow trees to cut bias.",
    ])

    # --- Card 2: GBDT ---
    b.add_section("Card 2: GBDT Core + Regularization", [
        "**Q:** Write the GBDT update rule. What is the single most important "
        "regularization and why did you forget it in the mock?",
        "",
        "**A:**",
        FormulaBlock(
            latex=r"F_m(x) = F_{m-1}(x) + \nu \cdot h_m(x)",
            explanation="Each tree fits the negative gradient of the current loss:",
        ),
        "The most important regularization is **learning rate** "
        "$\\nu \\in [0.01, 0.1]$: small $\\nu$ + many trees + early stopping. "
        "Each tree only partially corrects, preventing any single tree from dominating. "
        "XGBoost adds: (1) second-order Taylor (Hessian in split gain), "
        "(2) explicit regularization $\\Omega = \\gamma T + \\frac{1}{2}\\lambda\\|w\\|^2$.",
    ])

    # --- Card 3: Tree vs NN on Tabular ---
    b.add_section("Card 3: Tree vs NN on Tabular Data", [
        "**Q:** Why do trees beat NNs on tabular data? Answer at the "
        "inductive-bias level, not 'memorization.'",
        "",
        "**A:** Trees: (1) axis-aligned splits = scaling-free, "
        "(2) per-feature independent = matches heterogeneous columns, "
        "(3) info-gain selection = robust to irrelevant features, "
        "(4) rank-based = outlier-robust. "
        "NNs assume: smoothness (tabular has jumps, e.g. age 17 vs 18), "
        "locality + translation invariance (meaningless for tables), "
        "hierarchical composition (no such structure in tables), "
        "large data (tabular often 1K-10K samples). "
        "Ref: Grinsztajn et al. 2022 -- NN over-smooths decision boundaries + "
        "is not robust to uninformative features.",
    ])

    # --- Card 4: Class Imbalance ---
    b.add_section("Card 4: Class Imbalance (Metrics First)", [
        "**Q:** What is Step 0 when facing class imbalance? Give the full "
        "priority stack.",
        "",
        "**A:** Step 0: **Change the metric** (accuracy is useless). "
        "Use PR AUC / F1 / business cost. Ask: what is the relative cost of FN vs FP? "
        "Step 1 (no data change): threshold tuning, class weights, "
        "Focal Loss $FL = -(1-p_t)^\\gamma \\log p_t$ ($\\gamma=2$). "
        "Step 2 (data change): under-sampling + EasyEnsemble + recalibrate; "
        "SMOTE only for low-dim numeric (fails high-dim, hurts GBDT). "
        "Step 3: GBDT is inherently robust; NN needs focal loss; "
        "always use stratified K-fold.",
    ])

    # --- Card 5: ROC AUC vs PR AUC ---
    b.add_section("Card 5: ROC AUC vs PR AUC Under Imbalance", [
        "**Q:** 100 positives, 999,900 negatives. Model catches 90 TP with "
        "1000 FP. Compute FPR and Precision. Why does ROC lie?",
        "",
        "**A:** FPR = 1000/999900 = 0.001 (ROC barely moves right). "
        "Precision = 90/1090 = 8.3% (terrible). "
        "FPR denominator is the massive negative pool -- any reasonable FP count "
        "gets diluted to near zero. "
        "Precision denominator is TP+FP, directly sensitive to false alarms. "
        "Rule: same-dataset model selection uses PR AUC; "
        "cross-dataset comparison can use ROC AUC (rank-invariant to class prior).",
    ])

    # --- Card 6: Softmax Numerical Stability ---
    b.add_section("Card 6: Softmax Numerical Stability", [
        "**Q:** Softmax has two numerical failure modes. Name both and the fix.",
        "",
        "**A:** Overflow: $e^{1000}$ = inf. "
        "Underflow: all logits very negative, every $e^{x_i}$ = 0, denominator = 0. "
        "Fix: log-sum-exp trick --",
        FormulaBlock(
            latex=(
                r"\text{softmax}(x)_i = "
                r"\frac{e^{x_i - m}}{\sum_j e^{x_j - m}}"
                r", \quad m = \max_j x_j"
            ),
        ),
        "After shift: all exponents are in $(-\\infty, 0]$, so no overflow; "
        "the max term is $e^0=1$, so denominator is at least 1, no underflow. "
        "Fused cross-entropy stays in logit space: "
        "$L = -x_y + \\text{LSE}(x)$, avoiding the precision-killing "
        "round-trip through tiny probabilities.",
    ])

    # --- Card 7: Online Softmax Rescale ---
    b.add_section("Card 7: Online Softmax Rescale Factor", [
        "**Q:** In streaming/tiled softmax, why can't you just add partial sums? "
        "Derive the rescale factor.",
        "",
        "**A:** Two partial sums use different bases "
        "($m_{\\text{old}}$ vs $m_{\\text{block}}$). Rebasing identity:",
        FormulaBlock(
            latex=(
                r"\ell_{\text{new}} = "
                r"e^{m_{\text{old}} - m_{\text{new}}} \ell_{\text{old}}"
                r" + e^{m_{\text{block}} - m_{\text{new}}} \ell_{\text{block}}"
            ),
        ),
        "Numeric example: $m_{\\text{old}}=0, \\ell_{\\text{old}}=1$; "
        "new logit=10. Correct: $e^{-10}+1 \\approx 1.00005$. "
        "Without factor: $1+1=2$ (2x error, attention collapses). "
        "This single math fact underlies FlashAttention, tiled attention, "
        "and ring attention.",
    ])

    # --- Card 8: Batch Normalization ---
    b.add_section("Card 8: Batch Normalization", [
        "**Q:** Why does BN work? Cite the paper that disproved the original "
        "explanation.",
        "",
        "**A:** Original claim (Ioffe & Szegedy 2015): reduces Internal Covariate "
        "Shift (ICS). Disproof (Santurkar et al. 2018, MIT): adding noise to "
        "increase ICS after BN -- BN still works. True mechanism: BN smooths the "
        "loss landscape (smaller Lipschitz constant), enabling larger LR without "
        "divergence.",
        FormulaBlock(
            latex=(
                r"\hat{x} = \frac{x - \mu_B}"
                r"{\sqrt{\sigma_B^2 + \epsilon}}"
                r", \quad y = \gamma \hat{x} + \beta"
            ),
        ),
        "Small batch ($B \\leq 4$): stats noisy, gradients unstable, running "
        "average biased. Alternatives: LN (Transformer), GN (detection), "
        "IN (style transfer). Transformer uses LN because: variable seq length, "
        "small batch, and LN has no train-vs-inference gap.",
    ])

    # --- Card 9: BN + Dropout Variance Shift ---
    b.add_section("Card 9: BN + Dropout Variance Shift", [
        "**Q:** Why shouldn't you put Dropout before BN? Derive the variance "
        "mismatch.",
        "",
        "**A:** Dropout preserves mean but not variance. "
        "With drop rate $p$: $\\text{Var}(y) = \\frac{p}{1-p} x^2$ extra variance. "
        "At inference dropout is off, so actual variance is smaller than training. "
        "BN's running $\\sigma^2$ was learned from high-variance (dropout-on) "
        "activations. At inference it divides low-variance input by that large "
        "$\\sigma$ -- outputs shrink, all downstream layers shift.",
        "",
        "Fix: (1) put dropout only after all BN layers (before final classifier), "
        "(2) modern ResNets use BN without dropout, "
        "(3) Transformers use LN + dropout safely (LN has no running stats). "
        "Mnemonic: **Dropout preserves mean not variance; BN stores training variance.**",
    ])

    # --- Card 10: SGNS / word2vec ---
    b.add_section("Card 10: SGNS / word2vec", [
        "**Q:** Write the SGNS loss. What did Levy & Goldberg 2014 prove about it?",
        "",
        "**A:**",
        FormulaBlock(
            latex=(
                r"L = -\log\sigma(v_c^\top v_w)"
                r" - \sum_{i=1}^k \mathbb{E}_{c_i^- \sim P_n}"
                r"[\log\sigma(-v_{c_i^-}^\top v_w)]"
            ),
        ),
        "Push true-pair dot product up, random-pair down. $k$ = 5-20 negatives. "
        "$P_n$ = unigram$^{3/4}$. Only updates $1+k$ embeddings per step "
        "(vs full $V$-class softmax).",
        "",
        "Levy & Goldberg: SGNS implicitly factorizes a shifted PMI matrix: "
        "$v_w^\\top v_c = \\text{PMI}(w,c) - \\log k$. "
        "This unifies neural embeddings with classical count-based methods (LSA). "
        "Direction reminder: Skip-gram = center predicts context; "
        "CBOW = context predicts center (closer to BERT MLM direction).",
    ])

    # --- Card 11: InfoNCE + Contrastive Learning ---
    b.add_section("Card 11: InfoNCE and Contrastive Learning", [
        "**Q:** Write the InfoNCE loss. Why is it better than SGNS? "
        "Write the 5-line in-batch negatives code.",
        "",
        "**A:**",
        FormulaBlock(
            latex=(
                r"L = -\log\frac{\exp(s(x, x^+))}"
                r"{\exp(s(x, x^+)) + \sum_{i=1}^k \exp(s(x, x_i^-))}"
            ),
            explanation="Where $s(x,y) = f(x)^\\top f(y) / \\tau$:",
        ),
        "Advantages over SGNS: (1) all negatives coupled in one softmax denominator "
        "-- hardest negative gets largest gradient automatically; "
        "(2) mutual information lower bound: "
        "$I(x; x^+) \\geq \\log(k+1) - L$; "
        "(3) temperature $\\tau$ controls sharpness "
        "(SimCLR 0.1, CLIP 0.07 learnable).",
        "",
        "In-batch negatives (5 lines):",
        "```python\n"
        "Q = query_encoder(queries)   # [B, d]\n"
        "D = doc_encoder(docs)        # [B, d]\n"
        "S = Q @ D.T / tau            # [B, B]\n"
        "labels = torch.arange(B)\n"
        "loss = F.cross_entropy(S, labels)\n"
        "```",
        "Diagonal = positives, off-diagonal = negatives. Large batch = more "
        "negatives = better (CLIP uses 32K). Watch for false negatives in batch.",
    ])

    # --- Card 12: Adam / AdamW ---
    b.add_section("Card 12: Adam / AdamW", [
        "**Q:** Write Adam's 4 update equations. Why are L2 and weight decay "
        "not equivalent in Adam? How does AdamW fix it?",
        "",
        "**A:**",
        FormulaBlock(
            latex=(
                r"m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t"
                r", \quad v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2"
            ),
            explanation="First moment (mean) and second moment (uncentered variance):",
        ),
        FormulaBlock(
            latex=(
                r"\hat{m}_t = \frac{m_t}{1-\beta_1^t}"
                r", \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t}"
            ),
            explanation="Bias correction (early steps use short window):",
        ),
        FormulaBlock(
            latex=(
                r"\theta_{t+1} = \theta_t - \eta"
                r"\frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}"
            ),
            explanation="Update with per-parameter adaptive LR:",
        ),
        "$v_t$ is gradient squared (second moment), NOT Hessian -- Adam is first-order. "
        "L2 penalty gradient $g + \\lambda\\theta$ enters $m, v$, then gets divided "
        "by $\\sqrt{v_t}$ -- for large-weight directions $\\sqrt{v}$ is also large, "
        "so the decay gets diluted. AdamW fix:",
        FormulaBlock(
            latex=(
                r"\theta_{t+1} = \theta_t - \eta\!\left("
                r"\frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}"
                r" + \lambda\theta_t\right)"
            ),
            explanation="Decoupled weight decay -- applied outside the adaptive step:",
        ),
        "Transformers always use AdamW: different layers (embedding/attention/FFN/LN) "
        "have vastly different gradient magnitudes -- uniform LR (SGD) can't handle this.",
    ])

    # --- Card 13: NaN Debugging Checklist ---
    b.add_section("Card 13: NaN Debugging Checklist", [
        "**Q:** Your training goes NaN at step 5000. Walk through the systematic "
        "debug sequence.",
        "",
        "**A:** First: `torch.autograd.set_detect_anomaly(True)` to locate the "
        "first NaN op. Save checkpoint + seed + global step for reproducibility.",
        "",
        "Priority-ordered causes:",
        "1. **LR too high / no warmup / no grad clip** (~50%): "
        "check gradient norm spike before NaN. Fix: `clip_grad_norm_(params, 1.0)` "
        "+ warmup + lower peak LR. Transformers without warmup almost always explode.",
        "2. **Numerical overflow** (~30%): forgot $\\sqrt{d_k}$ in attention; "
        "fp16 cap is 65504; hand-written log(0). Fix: use bf16 (same exponent range "
        "as fp32) or fp16 + GradScaler.",
        "3. **Data issues** (~10%): label out of $[0, V)$; input has NaN; "
        "all-padding batch makes softmax denominator 0. Fix: dataloader asserts.",
        "4. **Norm epsilon underflow** (~5%): LN/BN $\\epsilon=10^{-8}$ underflows "
        "in fp16. Fix: set $\\epsilon=10^{-5}$.",
        "5. **Adam epsilon + rare embeddings** (~5%): $v_t \\approx 0$ for rare "
        "tokens. Fix: Adam $\\epsilon$ from $10^{-8}$ to $10^{-6}$.",
        "",
        "Meta principle: 90% of debug time is localizing WHICH tensor went NaN first. "
        "Once found, the cause is usually obvious.",
    ])

    # --- 3 Mnemonics ---
    b.add_section("3 Mnemonics to Memorize", [
        '1. "Complex model = low bias + high variance" (prevents label swap)',
        '2. "Dropout preserves mean not variance; BN stores training variance" '
        "(variance shift)",
        '3. "Adam L2 gets diluted by sqrt(v); AdamW pulls decay outside" '
        "(weight decay fix)",
    ])

    # --- Pre-interview checklist ---
    b.add_checklist("Pre-Interview Night Checklist (30 min)", [
        "Bias/Variance definition + label direction (Card 1)",
        "Bagging formula + GBDT learning rate (Cards 1-2)",
        "Tree vs NN inductive bias: 4 vs 4 (Card 3)",
        "Imbalance Step 0 = change metric (Card 4)",
        "ROC vs PR numeric example: FPR=0.001, Prec=8.3% (Card 5)",
        "Softmax LSE expansion: L = -x_y + LSE(x) (Card 6)",
        "BN ICS disproved by Santurkar 2018 (Card 8)",
        "Variance shift mnemonic (Card 9)",
        "Levy & Goldberg PMI conclusion (Card 10)",
        "InfoNCE formula + in-batch 5-line code (Card 11)",
        "AdamW decoupled decay formula (Card 12)",
        "NaN debug: detect_anomaly -> grad norm -> overflow -> data -> eps (Card 13)",
    ])

    # --- 3 Answer Habits ---
    b.add_section("3 Answer Habits (Meta)", [
        "1. **Every answer must include one formula or one numeric example.** "
        "If you can't express it as an equation or number, you haven't finished answering.",
        "2. **Before using an analogy, verify the shared mechanism has a formula.** "
        'Bad: "momentum is like PPO." Good: "both use EMA, formula is..."',
        "3. **Mechanism questions: start from definition, derive step by step.** "
        "Don't jump to countermeasures when asked 'why.'",
    ])

    return b


def main() -> None:
    """Generate flashcard doc and ingest into DB."""
    builder = build_note()
    content = builder.build()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {OUTPUT_PATH} ({len(content)} chars)")

    builder.save_to_db(COMPANY_ID, DOC_TITLE)


if __name__ == "__main__":
    main()
