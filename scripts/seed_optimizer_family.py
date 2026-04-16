"""Seed: T-P0-450 -- Optimizer family derivation chain.

Deliverables:
 (a) framework_node id=74 (Gradient Descent Family) description: 141b ->
     >=5000b. Ports the SGD -> Momentum -> AdaGrad -> RMSProp -> Adam
     derivation chain from data/t8_optimizers.md into the DB-resident
     description so the framework tree is self-contained.

NO new doc per task AC -- node description is sized to fit the pyramid
base. Skips LARS / LAMB / Lion (out of scope per task spec). AdamW is
kept because the decoupled-weight-decay note is the sister to "when NOT
Adam" guidance and is the standard interview follow-up.

Idempotent: running twice produces the same DB state.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 74
MIN_BYTES = 5000

NODE_DESCRIPTION = """# Gradient Descent Family -- SGD -> Momentum -> AdaGrad -> RMSProp -> Adam

## Scope

Pitch-level derivation chain for the five canonical optimizers covering
~99% of production deep learning. Two evolutionary axes:

- **Momentum axis**: SGD -> +Momentum -> +Nesterov -- smooths the
  *first moment* (gradient direction) to dampen valley oscillation and
  escape shallow saddles.
- **Adaptive axis**: AdaGrad -> RMSProp -> Adam -- rescales by the
  *second moment* (gradient magnitude) so each parameter gets its own
  effective learning rate.

Adam = Momentum + RMSProp + bias correction. AdamW decouples weight
decay from the gradient step and is the modern default for transformers.
LARS / LAMB / Lion are intentionally out of scope here -- see the
fancy-optimizers backlog if you ever need them.

Sits under `pillar2.optimization` next to LR Scheduling (75),
Convergence & Loss Landscape (76), and Activation Functions (77).

## 1. SGD -- the baseline

Update rule:

    theta_{t+1} = theta_t - eta * g_t       g_t = grad L(theta_t)

**Behavior**: high variance per step (mini-batch noise), oscillates in
narrow valleys (short axis dominates), stalls at saddle points where
the gradient is near zero. With a *constant* learning rate it never
truly converges -- the step does not vanish near a minimum.

**Why we still teach it**: it is the algorithmic skeleton every other
optimizer extends. All differences below are in the *direction* term
(replace g_t with a smoothed / rescaled vector).

## 2. SGD + Momentum -- exponentially-weighted gradient

Introduce a velocity v_t accumulating past gradients (typical beta=0.9):

    v_t       = beta * v_{t-1} + g_t
    theta_{t+1} = theta_t - eta * v_t

**Physical intuition**: a ball rolling down the loss surface. v_t is
velocity, beta is friction (beta=0 -> no memory, beta=1 -> no friction).

**Why it works on elongated valleys**:
- Long axis: gradient is small but consistent -> v_t accumulates ->
  *acceleration*.
- Short axis: gradient is large but oscillating -> +/- terms cancel ->
  *damping*.

**Effective step amplification**: when g is constant, v_t -> g/(1-beta).
beta=0.9 amplifies the effective step by 10x -- so when you turn on
momentum you typically need to *drop* the base lr by ~5-10x or the
training will diverge.

**Nesterov (NAG)**: evaluate the gradient at the look-ahead position
theta_t - eta*beta*v_{t-1} instead of theta_t. Theoretically faster on
convex problems (O(1/T^2) vs O(1/T)) but the practical lift on neural
nets is small; ship the basic momentum form unless you have a reason.

## 3. AdaGrad -- per-parameter LR with monotone decay

Maintain a running sum of squared gradients per coordinate:

    G_{t,j}       = sum_{tau=1..t} g_{tau,j}^2
    theta_{t+1,j} = theta_{t,j} - eta / sqrt(G_{t,j} + eps) * g_{t,j}

**Win**: parameters that get frequent large gradients automatically get
*smaller* effective lr; rarely-updated parameters keep a larger lr.
This is exactly the right behavior for **sparse features** -- AdaGrad
was the SOTA optimizer for word embeddings and click-prediction
features around 2011-2014.

**Fatal flaw**: G_{t,j} is monotonically increasing -> effective lr
monotonically *decreases* and goes to zero. The optimizer freezes
before reaching the minimum on any long training run. Anyone who has
trained AdaGrad past 50k steps has seen the loss curve flatline early.

## 4. RMSProp -- swap the sum for an EMA

Replace the cumulative sum with an exponential moving average (typical
gamma=0.9):

    v_t       = gamma * v_{t-1} + (1 - gamma) * g_t^2
    theta_{t+1} = theta_t - eta / sqrt(v_t + eps) * g_t

EMA only "remembers" the last ~1/(1-gamma) ~= 10 steps of gradient
magnitude. Old large gradients fade out, so v_t stays bounded and the
effective lr does not collapse to zero. This is the *one fix* that
unblocks adaptive lr for long training runs.

Hyperparameter defaults (Hinton 2012 Coursera): gamma=0.9, eta=1e-3,
eps=1e-8. RMSProp was never formally published -- it lives in lecture
slides -- but it is what unblocked Adam.

## 5. Adam -- Momentum + RMSProp + bias correction

Track *both* the first moment (mean gradient, like Momentum) and the
second moment (mean squared gradient, like RMSProp):

    m_t = beta1 * m_{t-1} + (1 - beta1) * g_t            # 1st moment
    v_t = beta2 * v_{t-1} + (1 - beta2) * g_t^2          # 2nd moment

**Bias correction** -- the only non-obvious piece:

    m_hat_t = m_t / (1 - beta1^t)
    v_hat_t = v_t / (1 - beta2^t)
    theta_{t+1} = theta_t - eta * m_hat_t / (sqrt(v_hat_t) + eps)

**Why bias correction matters**: m and v are initialized to zero, so
in the first few steps they are biased toward zero. With beta2=0.999,
v_100 ~= 0.095 * E[g^2] -- only 9.5% of the true value. Without
correction, the denominator sqrt(v) is too small in the warm-up regime
and the step explodes. The 1/(1-beta^t) factor exactly cancels this
zero-init bias; for t >> 1/(1-beta) the correction factor approaches 1
and disappears.

**Default hyperparameters** (work surprisingly well across tasks):
beta1=0.9, beta2=0.999, eps=1e-8, eta=1e-3. The "Adam works out of the
box" reputation comes from how well-calibrated these defaults are.

## 6. AdamW -- decoupled weight decay

Adam + L2 regularization is *not* the same as Adam + weight decay.
With L2 you fold lambda*theta into the gradient *before* m/v are
computed, so the regularization is rescaled by 1/sqrt(v_hat) -- per-
parameter and inconsistent. AdamW (Loshchilov & Hutter 2019) decouples:

    theta_{t+1} = (1 - lambda*eta) * theta_t
                  - eta * m_hat_t / (sqrt(v_hat_t) + eps)

The (1 - lambda*eta) shrink applies uniformly to every parameter,
independent of m / v. This is the **correct** weight decay and is the
default in modern transformer training. Interview keyword:
**decoupled weight decay**.

## 7. When NOT Adam -- vision and generalization

Adam converges *fast* but often to *sharp* minima with worse test-set
generalization than SGD + Momentum + a good schedule. The trade is
well-known:

| Dimension | SGD + Momentum | Adam / AdamW |
| --- | --- | --- |
| Convergence speed | slow, needs careful tuning | fast, defaults usually work |
| Final generalization | often best (CV competitions, ImageNet leaderboards) | sometimes converges to sharp minima |
| Hyperparameter sensitivity | high (eta must be tuned per dataset) | low (defaults survive) |
| Memory overhead | 1x param-count (just v) | 2x param-count (m and v) |
| Typical domain | CV / "I want the last 0.5% accuracy" | NLP / transformers / fast prototyping |

**Modern consensus**:
- Transformer / NLP / LLM pretraining -> **AdamW + warmup + cosine
  decay** (sometimes LAMB at huge batch).
- CV competitions where the last 0.5% matters -> **SGD + Momentum(0.9)
  + step or cosine LR decay**, often paired with **SAM** (sharpness-
  aware minimization) to actively prefer flat minima.
- Fast prototyping or unknown task -> **Adam(lr=1e-3)** as the safe
  default.

## 8. Decision Tree

    Need an optimizer ->
      Transformer / NLP / LLM?
        -> AdamW + Warmup + Cosine Decay
        -> Huge batch (>4K)? add LAMB/LARS (out of scope here)
      CV competition / extreme generalization?
        -> SGD + Momentum(0.9) + Step or Cosine LR Decay
      Sparse features / classical recsys?
        -> AdaGrad or Adam
      RNN / sequence model?
        -> RMSProp or Adam + gradient clipping
      Fast prototype / unsure?
        -> Adam(lr=1e-3) -- the universal safe default

## 9. Summary Formula Table

| Optimizer | Update rule | Key property |
| --- | --- | --- |
| SGD | theta -= eta * g | Stateless baseline |
| Momentum | v = beta*v + g; theta -= eta*v | Smooth direction, escape valley wobble |
| Nesterov | gradient at theta - eta*beta*v | Look-ahead correction, O(1/T^2) on convex |
| AdaGrad | G += g^2; theta -= eta/sqrt(G+eps) * g | Per-param lr; freezes late |
| RMSProp | v = gamma*v + (1-gamma)*g^2; theta -= eta/sqrt(v+eps) * g | EMA fixes the AdaGrad freeze |
| Adam | m, v EMAs + bias correction | Momentum + RMSProp; default modern optimizer |
| AdamW | (1 - lambda*eta)*theta - eta * m_hat / (sqrt(v_hat) + eps) | Decoupled weight decay; transformer standard |

## Sister Nodes & Pointers

- **Learning Rate Scheduling (node 75)**: warmup + cosine decay are
  almost always paired with Adam / AdamW -- this node only covers the
  *update rule*, not the schedule on top of it.
- **Convergence & Loss Landscape (node 76)**: where flat-vs-sharp
  minima theory lives, motivating "when NOT Adam".
- **Activation Functions (node 77)**: derivative of the activation is
  what the optimizer ultimately consumes; vanishing-gradient pathology
  there breaks every optimizer here.
- **DL Training Pitfalls one-pager (T-P0-451)**: paired node covering
  focal loss, BatchNorm/LayerNorm, vanishing/exploding gradients with
  remediations.
- **Source study note**: data/t8_optimizers.md has the full from-
  scratch Python implementations, the Rosenbrock benchmark comparison,
  and the PyTorch API cheatsheet.

## Interview Pitfalls

1. **"Why bias correction in Adam?"** -- name the zero-init bias on m
   and v and the 1/(1-beta^t) factor; show that for beta2=0.999 the
   first ~1000 steps see severely under-estimated v.
2. **Confusing L2 with weight decay** -- in plain SGD they are
   identical; in Adam they are *not* (L2 enters via the gradient and
   gets rescaled by sqrt(v_hat)). AdamW is the fix.
3. **Forgetting to scale lr when enabling momentum** -- the effective
   step is amplified by 1/(1-beta) ~= 10x; reuse the SGD lr verbatim
   and training diverges.
4. **Picking Adam for ImageNet leaderboard work** -- SGD + Momentum
   with a good schedule still beats Adam on most CV benchmarks. The
   flat-minima generalization gap is real.
5. **Treating AdaGrad as a viable long-run optimizer** -- it freezes.
   Use it for short fine-tunes or sparse features only.
"""


def update_framework_node() -> int:
    """Update framework_node id=74 description; return byte length.

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
