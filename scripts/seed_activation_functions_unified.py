"""Seed: T-P0-449 -- Activation functions unified pitch.

Deliverables:
 (a) framework_node id=77 (Training Tricks) description: 135b -> >=3000b
     activation-functions when-to-pick rubric covering ReLU / LeakyReLU /
     Sigmoid / Tanh / Softmax, with a single comparison table, three
     when-to-pick examples, and cross-links to sister optimization nodes.

NO new doc per task AC. Pyramid-base pitch-level -- no deep math on
smoothness theory; derivatives shown only in the table.

Idempotent: running twice produces the same DB state.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 77
MIN_BYTES = 3000

NODE_DESCRIPTION = """# Activation Functions -- ReLU / LeakyReLU / Sigmoid / Tanh / Softmax

## Scope

Pitch-level when-to-pick rubric for the five activation functions covering
~99% of production deep learning. This node intentionally skips smoothness
theory and universal-approximation proofs -- those belong under node 76
(Convergence & Loss Landscape). Here we only answer: given a layer position
(hidden vs output) and a task (regression / binary / multi-class / vision
feature-map), which activation do you pick and why?

Sits under `pillar2.optimization` next to Learning Rate Scheduling (75) and
Training Tricks proper (weight init, clipping, batch size -- see the
Training-Tricks addendum in node 14's Optimization pillar overview).

## Comparison Table

| Activation | Formula | Range | Derivative | Vanishing-grad risk | Compute cost | Typical use |
| --- | --- | --- | --- | --- | --- | --- |
| **ReLU** | `max(0, x)` | [0, +inf) | 1 if x > 0 else 0 | None on positives; **dying ReLU** on negatives | Cheapest (one comparison) | Default hidden activation for CNN / MLP |
| **LeakyReLU / PReLU** | `x if x>0 else a*x` (a ~ 0.01, PReLU learns a) | (-inf, +inf) | 1 or a | None | Cheap | Dying-ReLU fix; GANs, deep stacks |
| **Sigmoid** | `1 / (1 + exp(-x))` | (0, 1) | s(x)(1-s(x)), max 0.25 | **Severe** on saturation | Expensive (exp) | Binary-classification output only |
| **Tanh** | `(e^x - e^-x) / (e^x + e^-x)` | (-1, 1) | 1 - tanh^2(x), max 1.0 | Moderate on saturation | Expensive | RNN / LSTM gates; zero-centered hidden |
| **Softmax** | `exp(x_i) / sum_j exp(x_j)` | (0, 1), sums to 1 | `s_i(d_ij - s_j)` (Jacobian) | N/A (used with cross-entropy) | Expensive (exp + norm) | Multi-class output |

**Modern alternatives worth mentioning once** (out of scope for this pitch):
**GELU** (transformers default), **SiLU / Swish** (EfficientNet / LLaMA),
**Mish**. All are smooth ReLU variants; pick based on benchmark rather than
theory.

## Why ReLU Is the Default Hidden Activation (Vision + MLP)

1. **Cheap**: a single `max` op; no `exp`. Matters at training scale -- a
   ResNet-50 forward pass calls ReLU millions of times per batch.
2. **Non-saturating on the positive side**: gradient is exactly 1 for
   x > 0, so no vanishing-gradient choke point in deep stacks. This is
   the single biggest win over sigmoid / tanh and is why ReLU unblocked
   networks beyond ~10 layers.
3. **Induces sparsity**: ~50% of activations are exactly 0 on random
   inputs, which acts as a cheap regularizer and gives faster downstream
   matmuls (zero-skipping in some kernels).
4. **Cost**: the **dying ReLU** problem -- if a neuron's pre-activation is
   negative for every training point, its gradient is always 0 and it
   never updates. Fix with **LeakyReLU** (tiny slope on negatives) or
   **PReLU** (learn the slope per channel). Monitor % dead neurons during
   training.

## Why Sigmoid Only at Binary Output (Never Hidden)

- Squashes any real number into (0, 1), so it is the natural probability
  head for a binary classifier. Pairs cleanly with **BCE loss** -- the
  combined `sigmoid + BCE` gradient simplifies to `(p - y)`, and PyTorch's
  `BCEWithLogitsLoss` fuses the two for log-sum-exp numerical stability.
- **Do not** use sigmoid in hidden layers: its max derivative is 0.25,
  and it saturates (derivative -> 0) once `|x| > 5`. Stack ten sigmoid
  layers and you multiply ten sub-0.25 numbers -- gradient vanishes to
  zero before it reaches the first layer. This was the central problem
  ReLU solved in 2011.
- **Tanh** is zero-centered (mean-0 outputs help downstream optimization)
  and has a max derivative of 1.0, so it is the RNN / LSTM gate default
  -- but it still saturates, so skip it for deep feed-forward stacks.

## Softmax for Multi-class + Temperature Tricks

- Softmax is **joint** across logits (every output depends on every
  input), so it is the correct output for mutually-exclusive multi-class.
  Pair with **CrossEntropyLoss** (which in PyTorch fuses `log_softmax +
  NLL` for numerical stability -- never apply softmax manually before
  passing to `CrossEntropyLoss`).
- **Temperature scaling**: replace `softmax(z)` with `softmax(z / T)`:
  - `T < 1` **sharpens** the distribution -> used to build a sharp
    teacher distribution for **knowledge distillation** and to produce
    the argmax-like "hard" labels in some self-training regimes.
  - `T > 1` **smooths** the distribution -> used for diversity in
    sampling (LLM decoding), and to soften the student's target in
    **Hinton-style distillation** (paired with `T^2` loss scaling).
  - `T = 1` is the vanilla softmax.
- Use **multi-label** (independent per-class sigmoid + BCE) instead of
  softmax when a sample can have multiple labels (tag prediction).

## Three When-to-Pick Examples

1. **ResNet-50 hidden layers on ImageNet**: ReLU (default). Cheap,
   deep-friendly, well-tested. Dying-ReLU on ImageNet is rare because
   BatchNorm keeps activations centered; if you do see dead neurons,
   swap in LeakyReLU(0.01) as a drop-in.
2. **Binary spam classifier output head**: Sigmoid + `BCEWithLogitsLoss`.
   Never softmax with 2 classes -- you waste one degree of freedom and
   double the parameters on the output bias. Read off `p = sigmoid(z)`
   directly.
3. **ImageNet-1K multi-class output head**: Softmax + `CrossEntropyLoss`.
   In PyTorch, feed raw logits to `CrossEntropyLoss` (it applies
   `log_softmax` internally) -- applying softmax yourself first gives a
   mathematically valid but numerically-unstable "double softmax"
   gradient.

## Sister Nodes & Pointers

- **Gradient Descent Family (node 74)**: where the gradient that flows
  through each activation's derivative originates.
- **Learning Rate Scheduling (node 75)**: deep stacks with ReLU rely on
  warmup + cosine decay to avoid exploding early-layer updates.
- **Convergence & Loss Landscape (node 76)**: where non-convexity and
  saddle-point behavior is treated rigorously -- including why dying
  ReLU is technically a set of degenerate stationary points.
- **DL Training Pitfalls one-pager (task T-P0-451)**: paired node
  covering focal loss, BatchNorm / LayerNorm, vanishing / exploding
  gradients with remediations -- depends on this activation rubric.

## Interview Pitfalls

1. Using **sigmoid in hidden layers** of a deep network -- classic
   vanishing-gradient trap. Answer should name the 0.25 max-derivative
   math and point to ReLU as the 2011 fix.
2. Applying **softmax before `CrossEntropyLoss`** in PyTorch -- the
   loss already applies `log_softmax`; manual softmax double-applies
   and loses numerical stability (log-sum-exp trick).
3. Ignoring **dying ReLU** monitoring -- no standard metric is logged
   by default. Instrument `% of zero activations per layer`; persistent
   >90% is the red flag.
4. Picking softmax for a **2-class problem** -- sigmoid + BCE is the
   canonical choice (half the output-bias parameters, same decision
   boundary).
5. Forgetting that **multi-label != multi-class** -- multi-label uses
   per-class sigmoid + BCE, not softmax. Asked as a trap in recsys /
   tag-prediction rounds.
"""


def update_framework_node() -> int:
    """Update framework_node id=77 description; return byte length.

    Raises SystemExit on missing DB or missing node. Idempotent.
    """
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
        before = conn.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (NODE_DESCRIPTION, NODE_ID),
        )
        conn.commit()
        after = conn.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(f"[DONE] framework_node id={NODE_ID} ({row[1]}): {before} -> {after} bytes")
        return after
    finally:
        conn.close()


def main() -> None:
    """Entry point: update node + verify byte budget."""
    size = update_framework_node()
    if size < MIN_BYTES:
        print(f"[FAIL] Node description {size}b < {MIN_BYTES}b target")
        sys.exit(1)
    print(f"[PASS] Node description {size}b >= {MIN_BYTES}b target")


if __name__ == "__main__":
    main()
