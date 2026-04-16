"""Seed: T-P0-451 -- DL Training Pitfalls 1-pager.

Deliverables:
 (a) docs/dl_training_pitfalls_1pager.md -- StudyNoteBuilder-rendered pitch
     covering Focal loss, BatchNorm/LayerNorm train-vs-eval trap, and
     vanishing/exploding gradients with init + clipping + residual fixes.
 (b) framework_node id=77 (Training Tricks) description: extend with a
     second section appended AFTER the activation-functions content from
     T-P0-449, keeping the same node as the container for the Gap-6
     training-tricks addendum. Combined node size grows from ~7120b.

Scope: <=3500 words combined budget. Pyramid base pitch-level; no deep
math on LayerNorm invariance proofs -- just the practical train/eval trap,
the modality choice, and the interview pitfalls.

Idempotent: running twice produces the same DB state and identical file.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from study_note_builder import FormulaBlock, StudyNoteBuilder

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 77
DOC_FILENAME = "dl_training_pitfalls_1pager.md"

# Sentinel so we can idempotently replace the addendum without drifting.
ADDENDUM_MARK_BEGIN = "<!-- BEGIN T-P0-451 dl-training-pitfalls -->"
ADDENDUM_MARK_END = "<!-- END T-P0-451 dl-training-pitfalls -->"

NODE_ADDENDUM = f"""{ADDENDUM_MARK_BEGIN}

## DL Training Pitfalls (Focal Loss / BN-LN / Vanishing-Exploding)

Second Gap-6 pitch on the same Training-Tricks node. Covers three scattered
production traps that come up in almost every DL interview once the
activation question above has been answered. Full worked examples live in
`docs/dl_training_pitfalls_1pager.md`; this section is the pitch-level
rubric.

### Focal Loss -- When Class Imbalance Breaks BCE

Standard binary cross-entropy weights every sample the same. In heavy-imbalance
regimes (object detection with ~1000:1 background:foreground, click-through
rate with ~100:1 non-click:click) BCE is dominated by the easy negatives and
the model converges to a near-constant predictor. Focal loss (Lin et al.
2017, "Focal Loss for Dense Object Detection") fixes this:

- `FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)` where `p_t` is the
  model's probability of the true class.
- **alpha_t**: static per-class weight (typical 0.25 for the majority class,
  0.75 for the minority) -- same knob as plain class-weighted BCE.
- **gamma** (focusing parameter, typical 2.0): down-weights confident correct
  predictions by `(1 - p_t)^gamma`. A well-classified sample at p=0.9 gets a
  weight of 0.01 vs a hard sample at p=0.5 which still weighs 0.25.

**When NOT to use focal loss**:
1. Balanced or mildly imbalanced data (< 10:1) -- plain BCE or class-weighted
   BCE is simpler and converges faster.
2. You need calibrated probabilities for downstream ranking -- focal loss
   systematically under-confident on hard examples; add temperature
   scaling post-hoc or use BCE + class weights instead.
3. Labels are noisy -- focal loss up-weights misclassified samples, which
   by construction up-weights label noise too.

### BatchNorm vs LayerNorm -- Train/Eval Trap + Sequence Use Case

**BatchNorm** normalises each feature across the batch dimension:
`x_hat = (x - mu_batch) / sqrt(var_batch + eps)`, then scale + shift by
learned gamma, beta. Two modes:
- **Train mode**: uses the current batch's mean/var; updates a running
  average (momentum typically 0.1) that is frozen at eval time.
- **Eval mode**: uses the frozen running mean/var. `model.eval()` must be
  called before inference or the layer will use the single-batch statistics,
  which for batch-size-1 inference is exactly the zero vector (NaN division
  after variance = 0).

The classic BN bug is deploying a model without `model.eval()` and seeing
mysterious per-request output drift. A second classic: freezing a pre-trained
backbone for fine-tuning but forgetting to also put BN into eval mode --
BN's running stats get corrupted by the small fine-tune dataset.

**BN motivation** was "internal covariate shift" (Ioffe & Szegedy 2015), but
Santurkar et al. 2018 ("How Does Batch Normalization Help Optimization?")
showed the real win is **smoother loss landscape** + higher allowable
learning rates. Pitch the new story, not the original.

**LayerNorm** normalises across the feature dimension of a single sample,
independent of batch. Pick LN over BN when:
1. **Transformers / sequence models**: variable sequence length makes BN
   statistics unstable across batches -- LN normalises each token's hidden
   vector independently.
2. **Small batches** (RL, contrastive learning with hard-negatives,
   memory-constrained LLM fine-tune): BN needs batch sizes >= 16 for stable
   statistics; LN works at batch size 1.
3. **Online / streaming inference**: no batch dimension at serve time ->
   BN's running stats + eval-mode trap go away entirely.
4. **Variable-length or padded inputs**: BN over padded positions pollutes
   the running mean; LN restricted to real tokens avoids this.

GroupNorm (Wu & He 2018) and RMSNorm (the modern LLM default, Zhang & Sennrich
2019 via T5 / LLaMA-2+) are LN variants worth naming once -- GroupNorm for
CNNs with small batch, RMSNorm for LLMs (drops the mean-centring step, ~7%
compute saving, empirically matches LN).

### Vanishing / Exploding Gradients + Init + Clipping + Residual

Deep stacks multiply gradients through many Jacobians. If each Jacobian has
a spectral radius < 1 the product shrinks geometrically (**vanishing**) and
early layers stop learning; if the spectral radius > 1 the product blows up
(**exploding**) and training diverges. Three canonical triggers and three
canonical fixes:

**Triggers**
1. **Sigmoid / tanh stacks**: saturated derivatives (max 0.25 for sigmoid,
   1.0 for tanh) multiply to zero through 10+ layers. This is why ReLU
   replaced sigmoid in hidden layers.
2. **RNN / LSTM over long sequences**: the same recurrent weight matrix is
   multiplied T times; if its spectral radius is not exactly 1 you either
   vanish or explode over long horizons.
3. **Poor initialisation**: weights sampled from N(0, 1) have expected
   activation variance growing with layer width; the forward pass explodes
   before gradients can even be computed.

**Fixes**
1. **Residual / skip connections (He et al. 2015, ResNet)**: `y = F(x) + x`
   keeps an identity path so the worst-case gradient is still 1, not 0.
   Makes 100+ layer networks trainable; the same trick is why the Transformer
   block is `x + Attention(LN(x))` / `x + FFN(LN(x))`.
2. **Gradient clipping**: clip by global norm (`clip_grad_norm_(params, 1.0)`)
   or by value. Essential for RNNs and for large-batch Transformer training
   where a single outlier batch can blow up the running Adam second-moment.
3. **Xavier / He initialisation**: pick weight variance so forward and backward
   signals stay O(1):
   - **Xavier** (Glorot & Bengio 2010) for tanh / sigmoid:
     `Var(W) = 2 / (fan_in + fan_out)`.
   - **He** (He et al. 2015) for ReLU / LeakyReLU:
     `Var(W) = 2 / fan_in` -- doubles Xavier's variance to compensate for
     ReLU zeroing out roughly half the activations.

PyTorch default for `nn.Linear` is Kaiming-uniform (He-variant); `nn.Conv2d`
defaults to Kaiming-normal fan-in. Frameworks mostly "just work" on CNN / MLP
but you must set `a` / `nonlinearity` correctly when using LeakyReLU or
custom activations -- the default assumes plain ReLU.

### Interview Pitfalls (Gap-6 Addendum)

1. Using **focal loss on balanced data** -- adds noise without signal.
   The interviewer wants you to name the imbalance threshold (~10:1) at
   which focal pays off.
2. Deploying a BN-bearing model **without `.eval()`** and blaming the
   framework for non-deterministic output. Any PyTorch answer should mention
   `model.eval()` before inference and `torch.no_grad()` for efficiency.
3. Quoting "internal covariate shift" as BN's raison d'etre without
   mentioning the 2018 Santurkar correction -- dates the candidate.
4. Using **BatchNorm inside a Transformer** -- signals you have not read
   the original paper. LN is the default; RMSNorm is the modern variant.
5. Calling **He vs Xavier** interchangeable -- they differ by a factor of 2
   to compensate for ReLU's half-zero output distribution.
6. Forgetting to **clip gradients** in RNN / LSTM training -- exploding
   gradient is the textbook RNN failure mode.
7. Using **residual blocks without LN/BN** in a 100-layer stack -- pre-LN
   Transformers need LN inside the residual branch to actually benefit
   from the skip connection's gradient-preservation.

### Pointers

- **Activation functions (above, same node 77)**: source of the derivatives
  that vanish / explode through deep stacks.
- **Gradient Descent Family (node 74)**: Adam's bias correction and
  second-moment normalisation partially compensate for exploding gradients
  but do not replace clipping.
- **Learning Rate Scheduling (node 75)**: warmup + cosine decay is the
  standard way to stabilise early Transformer training where LN + He init +
  residual alone are not enough.
- **Convergence & Loss Landscape (node 76)**: formal treatment of why
  skip connections change the loss landscape's conditioning.

{ADDENDUM_MARK_END}
"""


def update_framework_node() -> tuple[int, int]:
    """Append (or replace) the T-P0-451 addendum on node 77's description.

    Returns (before_bytes, after_bytes). Idempotent: if the sentinel markers
    are already present, the addendum block is replaced in place, so running
    this script N times leaves the DB in the same state.
    """
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, title, description FROM framework_nodes WHERE id = ?",
            (NODE_ID,),
        ).fetchone()
        if not row:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            sys.exit(1)
        _id, title, current = row
        before = len(current or "")

        if ADDENDUM_MARK_BEGIN in current and ADDENDUM_MARK_END in current:
            # Replace existing addendum block in place (idempotent).
            start = current.index(ADDENDUM_MARK_BEGIN)
            end = current.index(ADDENDUM_MARK_END) + len(ADDENDUM_MARK_END)
            new_description = current[:start] + NODE_ADDENDUM.strip() + current[end:]
        else:
            # First run: append.
            new_description = current.rstrip() + "\n\n" + NODE_ADDENDUM
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (new_description, NODE_ID),
        )
        conn.commit()
        after = conn.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(
            f"[DONE] framework_node id={NODE_ID} ({title}): "
            f"{before} -> {after} bytes"
        )
        return before, after
    finally:
        conn.close()


def build_one_pager() -> StudyNoteBuilder:
    """Build the DL training pitfalls one-pager via StudyNoteBuilder."""
    b = StudyNoteBuilder()
    b.set_title("DL Training Pitfalls -- Focal / BN-LN / Vanishing-Exploding")

    b.add_prerequisites([
        "Activation functions basics -- framework_node 77 first section",
        "Cross-entropy loss + BCE",
        "Backpropagation + chain rule",
        "Xavier / He init intuition",
    ])

    b.add_term("FL", "Focal Loss (Lin et al. 2017)",
               "BCE variant with (1-p_t)^gamma modulator for imbalanced detection")
    b.add_term("BN", "BatchNorm (Ioffe & Szegedy 2015)",
               "Per-feature normalisation across the batch dimension; train vs eval mode")
    b.add_term("LN", "LayerNorm (Ba et al. 2016)",
               "Per-sample normalisation across the feature dimension; transformer default")
    b.add_term("RMSNorm", "Root Mean Square LayerNorm (Zhang & Sennrich 2019)",
               "LN variant with no mean-centring; LLaMA / modern LLM default")
    b.add_term("ICS", "Internal Covariate Shift (Ioffe & Szegedy 2015)",
               "Original BN motivation; superseded by smoother-loss-landscape explanation")

    # Section 1: Focal Loss
    b.add_section("1. Focal Loss -- Heavy Class Imbalance", [
        "Heavy class imbalance (object detection ~1000:1 background:foreground, "
        "CTR prediction ~100:1 non-click:click, rare-disease diagnosis) breaks "
        "plain binary cross-entropy. Easy negatives dominate the gradient and "
        "the model converges to a near-constant predictor. Class-weighted BCE "
        "helps but still spends most of its capacity on easy examples. **FL** "
        "fixes the second problem by **down-weighting easy correctly-classified "
        "samples**.",
        FormulaBlock(
            latex=r"\mathrm{FL}(p_t) = -\alpha_t \cdot (1 - p_t)^\gamma \cdot \log(p_t)",
            explanation="Definition (Lin et al. 2017, 'Focal Loss for Dense Object Detection'):",
        ),
        "where `p_t` is the model's predicted probability for the true class, "
        "`alpha_t` is a static per-class weight (Lin et al. recommend 0.25 for "
        "the majority class, 0.75 for minority -- same knob as class-weighted "
        "BCE), and **gamma** (focusing parameter, typical 2.0) down-weights "
        "confident correct predictions.",
        "**Worked intuition**: at `p_t = 0.9` the modulator is "
        "`(1 - 0.9)^2 = 0.01`; at `p_t = 0.5` it is `0.25`. A well-classified "
        "sample gets 25x less weight than a hard sample. At gamma = 0 focal "
        "loss degenerates to class-weighted BCE.",
        "**Typical hyperparameters** (Lin et al.): alpha=0.25, gamma=2.0 on "
        "RetinaNet + MS-COCO. Treat these as a starting point; gamma in [1, 5] "
        "is the usual sweep range.",
        "**When NOT to use focal loss**:",
        "1. **Balanced data / mild imbalance (<10:1)**: plain BCE or "
        "class-weighted BCE converges faster with the same accuracy. Focal "
        "loss adds a hyperparameter without signal.",
        "2. **Need calibrated probabilities downstream** (ranking, budget "
        "allocation, cost-sensitive decision): focal loss is systematically "
        "under-confident -- it deliberately keeps hard examples from converging "
        "to high-confidence predictions. Add temperature scaling post-hoc or "
        "switch to BCE + class weights + Platt scaling.",
        "3. **Noisy labels**: focal loss up-weights misclassified samples, so "
        "label noise gets amplified by `(1 - p_t)^gamma`.",
        "4. **You already use a strong hard-negative mining pipeline**: OHEM "
        "and focal loss solve overlapping problems; stacking them over-focuses "
        "on outliers.",
    ])

    # Section 2: BN vs LN
    b.add_section("2. BatchNorm vs LayerNorm -- Train/Eval + Sequence Use Case", [
        "**BN** normalises each feature across the batch dimension:",
        FormulaBlock(
            latex=r"\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \qquad y_i = \gamma \hat{x}_i + \beta",
            explanation="Per-feature normalisation with learned affine gamma, beta:",
        ),
        "**Two modes** that every production user gets bitten by at least once:",
        "- **Train mode (`model.train()`)**: uses the current batch's mu, sigma; "
        "updates a running estimate with momentum (PyTorch default 0.1) that is "
        "frozen for inference.",
        "- **Eval mode (`model.eval()`)**: uses the running mu, sigma. Forgetting "
        "to call `.eval()` before inference is the canonical BN bug -- a "
        "batch-size-1 inference in train mode divides by `sqrt(var_B + eps)` "
        "where `var_B = 0`, producing constant zeros.",
        "**Second classic bug**: freezing a pre-trained backbone for fine-tuning "
        "but leaving BN in train mode -- the small fine-tune dataset corrupts "
        "the running stats. Always set `module.eval()` on frozen BN layers, or "
        "set `track_running_stats=False`.",
        "**Why ICS is the wrong story**: Ioffe & Szegedy's 2015 paper motivated "
        "BN as fixing **ICS** (activations of deeper layers depending on "
        "previous-layer stats that shift during training). Santurkar et al. 2018 "
        "(`How Does Batch Normalization Help Optimization?`) showed empirically "
        "that BN's real benefit is a **smoother loss landscape** (bounded "
        "Lipschitz constant of the loss and gradients) that allows larger "
        "learning rates. Cite Santurkar, not Ioffe, when asked 'why does BN "
        "help?'.",
        "**LN** normalises across the feature dimension of one sample, "
        "independent of batch size:",
        FormulaBlock(
            latex=r"\hat{x}_{i,j} = \frac{x_{i,j} - \mu_i}{\sqrt{\sigma_i^2 + \epsilon}}, \qquad \mu_i = \tfrac{1}{d}\sum_{k} x_{i,k}",
            explanation="Per-sample, per-position normalisation over feature dim d:",
        ),
        "**Pick LN over BN when**:",
        "1. **Transformers / sequence models**: variable sequence lengths and "
        "per-token normalisation semantics. BN statistics get polluted by "
        "padded positions; LN is applied per token independently.",
        "2. **Small batch sizes** (RL, hard-negative contrastive learning, "
        "memory-constrained LLM fine-tune): BN needs batch >= 16 for stable "
        "batch statistics; LN works at batch size 1.",
        "3. **Online / streaming inference** with batch = 1: no running-stats "
        "eval-mode trap, because LN has no running stats.",
        "4. **RNN / LSTM** where BN across time steps is ill-defined.",
        "**Variants worth naming**: **GroupNorm** (Wu & He 2018) for small-batch "
        "CNN, splits channels into G groups and normalises each. **RMSNorm** "
        "(Zhang & Sennrich 2019) drops the mean-centering step -- LLaMA / modern "
        "LLMs use it for ~7% compute saving with empirically-matched accuracy. "
        "**InstanceNorm** for style transfer. **BatchRenorm** for small-batch BN.",
    ])

    # Section 3: Vanishing / exploding gradients
    b.add_section("3. Vanishing / Exploding Gradients -- Init + Clip + Residual", [
        "Backprop through L layers multiplies L Jacobians. The product's "
        "spectral radius grows or shrinks geometrically with L. When it "
        "shrinks, early layers stop learning (**vanishing**). When it blows up, "
        "training diverges (**exploding**).",
        "**Three canonical triggers**:",
        "1. **Sigmoid / tanh stacks**: saturated derivatives (max 0.25 for "
        "sigmoid, 1.0 for tanh) multiply to zero through 10+ layers. The "
        "central 2011-2015 reason ReLU replaced sigmoid in hidden layers.",
        "2. **RNN / LSTM over long sequences**: the same recurrent weight "
        "matrix is multiplied T times; unless its spectral radius is exactly 1 "
        "gradients either vanish or explode over long horizons. LSTM's cell "
        "state + forget gate were designed to give gradients a near-identity "
        "path.",
        "3. **Bad initialisation**: weights sampled from N(0, 1) cause "
        "activation variance to grow with layer width; forward pass explodes "
        "before gradients can even be computed.",
        "**Three canonical fixes**:",
        "**Fix 1 -- Residual / skip connections** (He et al. 2015, ResNet): "
        "`y = F(x) + x` provides an identity path so the worst-case Jacobian "
        "is still I, not 0. Enables 100+ layer CNNs and is why every "
        "Transformer block uses `x + Attention(LN(x))` and `x + FFN(LN(x))`.",
        "**Fix 2 -- Gradient clipping**: cap the global gradient norm before "
        "the optimizer step. PyTorch: `torch.nn.utils.clip_grad_norm_(params, "
        "max_norm=1.0)`. Clip-by-value is an alternative but clip-by-norm "
        "preserves direction. Essential for RNNs and for large-batch "
        "Transformer training where a single outlier batch can blow up Adam's "
        "running second moment and break subsequent updates.",
        "**Fix 3 -- Variance-preserving init** (Xavier for tanh, He for ReLU):",
        FormulaBlock(
            latex=r"\mathrm{Xavier:}\ \mathrm{Var}(W) = \frac{2}{n_\mathrm{in} + n_\mathrm{out}}, \qquad \mathrm{He:}\ \mathrm{Var}(W) = \frac{2}{n_\mathrm{in}}",
            explanation="Pick init variance to keep forward signal and backward gradient O(1):",
        ),
        "Xavier (Glorot & Bengio 2010) targets tanh / sigmoid networks; He "
        "et al. 2015 doubled the variance for ReLU to compensate for ReLU "
        "zeroing out approximately half the pre-activations. PyTorch default "
        "`nn.Linear` uses **Kaiming-uniform** (He-variant); `nn.Conv2d` uses "
        "Kaiming-normal fan-in. When using LeakyReLU / PReLU, pass the correct "
        "`a` / `nonlinearity` argument to `kaiming_normal_` or the init "
        "variance will be off.",
        "**Interaction with LN / BN**: pre-LN transformer (`LN -> Attn -> +x`) "
        "trains without warmup at large depth; post-LN (`Attn -> +x -> LN`, "
        "the original 2017 paper) needs warmup because the residual's early "
        "gradient has no normalisation. This is why modern LLMs (GPT-2 onwards, "
        "LLaMA) all use pre-LN.",
    ])

    # Section 4: Interview pitfalls
    b.add_checklist("Interview Self-Check", [
        "I can state focal loss's formula and name the two hyperparameters.",
        "I can list three scenarios where focal loss is the WRONG choice.",
        "I can explain BN train vs eval mode and name the batch-size-1 inference bug.",
        "I can cite Santurkar 2018's smoother-loss-landscape explanation over Ioffe's ICS story.",
        "I can list three reasons transformers use LN instead of BN.",
        "I can name RMSNorm and say what it drops compared to LN.",
        "I can explain why He init doubles Xavier's variance.",
        "I can pair each vanishing/exploding trigger with its canonical fix.",
        "I know pre-LN vs post-LN and why modern LLMs use pre-LN.",
    ])

    # Section 5: Pointers
    b.add_section("Pointers (Avoid Re-Deriving)", [
        "- **Activation functions + ReLU / sigmoid / softmax picks**: "
        "framework_node 77 first section (T-P0-449). This one-pager assumes "
        "you already picked the right activation -- the pitfalls here are "
        "the training-dynamics layer above that choice.",
        "- **Adam + bias correction**: framework_node 74 (T-P0-450). Adam "
        "partially compensates for exploding gradients via its running "
        "second-moment normalisation but does **not** replace clipping.",
        "- **Cosine + warmup LR schedules for Transformers**: framework_node "
        "75. Warmup is the standard hedge against early-training exploding "
        "gradients in post-LN Transformer training.",
        "- **Convergence & loss landscape theory**: framework_node 76.",
        "- **Focal loss derivation + label smoothing + balanced sampling**: "
        "if the interview drills deeper, mention **label smoothing** "
        "(Szegedy 2016) as an orthogonal fix to over-confident predictions, "
        "and **balanced / hard-negative mining** as an orthogonal fix to "
        "class imbalance. Either can stack with focal loss but rarely all "
        "three at once.",
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
    """Run both deliverables and sanity-check combined word budget."""
    before, after = update_framework_node()
    doc_size = write_one_pager()
    doc_path = REPO_ROOT / "docs" / DOC_FILENAME
    doc_words = len(doc_path.read_text(encoding="utf-8").split())
    addendum_words = len(NODE_ADDENDUM.split())
    total_words = doc_words + addendum_words
    print(
        f"[INFO] node addendum words={addendum_words}, "
        f"doc words={doc_words}, total={total_words}"
    )
    if after < 9000:
        print(f"[FAIL] node {NODE_ID} = {after} bytes, target >= 9000")
        sys.exit(1)
    if total_words > 3500:
        print(f"[FAIL] combined word count {total_words} exceeds 3500 budget")
        sys.exit(1)
    print(
        f"[OK] T-P0-451: node={after}b (from {before}b), "
        f"doc={doc_size} chars, combined={total_words} words."
    )


if __name__ == "__main__":
    main()
