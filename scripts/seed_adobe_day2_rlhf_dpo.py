"""Seed script: Insert Adobe Prep Day2 -- RLHF/DPO Alignment + LLM Distillation study note.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day2: RLHF/DPO Alignment + LLM Distillation"

CONTENT = r"""# RLHF/DPO Alignment + LLM Distillation (Adobe Prep Day 2)

> Aligning LLMs to human preferences is the bridge from "next-token predictor" to
> "useful assistant." Master the 3-step RLHF pipeline, DPO's elegant shortcut,
> and how distillation compresses capabilities into smaller models.

---

## 1. RLHF: Three-Step Pipeline

RLHF (Reinforcement Learning from Human Feedback) converts a pretrained LLM into an
aligned model through three sequential stages.

### Pipeline overview

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<span style="background:#4a90d9; padding:6px 12px; border-radius:4px; color:white;">Stage 1: SFT</span>
<span style="color:#888;"> ---> </span>
<span style="background:#6b4c9a; padding:6px 12px; border-radius:4px; color:white;">Stage 2: Reward Model</span>
<span style="color:#888;"> ---> </span>
<span style="background:#27ae60; padding:6px 12px; border-radius:4px; color:white;">Stage 3: PPO</span>
<br/><br/>
<span style="color:#aaa; font-size:12px;">Pretrained LLM</span>
<span style="color:#888;"> -> </span>
<span style="color:#aaa; font-size:12px;">Fine-tune on demonstrations</span>
<span style="color:#888;"> -> </span>
<span style="color:#aaa; font-size:12px;">Train preference scorer</span>
<span style="color:#888;"> -> </span>
<span style="color:#aaa; font-size:12px;">Optimize policy with RL</span>
</div>
</div>

### Stage 1: Supervised Fine-Tuning (SFT)

Fine-tune the pretrained model on high-quality demonstration data (prompt, ideal_response) pairs.

$$L_{\text{SFT}} = -\mathbb{E}_{(x,y) \sim D_{\text{demo}}} \left[ \sum_{t=1}^{|y|} \log \pi_{\text{SFT}}(y_t \mid x, y_{<t}) \right]$$

This produces $\pi_{\text{SFT}}$ -- the starting policy for RLHF.

### Stage 2: Reward Model Training

Collect human preference data: given prompt $x$, human ranks two responses $y_w \succ y_l$ (winner vs loser).

**Bradley-Terry preference model:**

$$P(y_w \succ y_l \mid x) = \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))$$

where $\sigma$ is the sigmoid function and $r_\phi$ is the reward model (typically the SFT model with a scalar head replacing the LM head).

**Reward model loss:**

$$L_{\text{RM}} = -\mathbb{E}_{(x, y_w, y_l) \sim D_{\text{pref}}} \left[ \log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l)) \right]$$

**Key insight:** The reward model only needs to produce *relative* scores, not absolute ones. The Bradley-Terry model captures this: only the difference $r(y_w) - r(y_l)$ matters.

### Stage 3: PPO Optimization

Use the trained reward model to optimize the policy via Proximal Policy Optimization.

**RLHF objective:**

$$\max_{\pi_\theta} \; \mathbb{E}_{x \sim D,\, y \sim \pi_\theta(\cdot|x)} \left[ r_\phi(x, y) - \beta \cdot D_{\text{KL}}(\pi_\theta(\cdot|x) \,\|\, \pi_{\text{SFT}}(\cdot|x)) \right]$$

where:
- $r_\phi(x, y)$: reward model score for the generated response
- $\beta$: KL penalty coefficient (prevents reward hacking)
- $D_{\text{KL}}$: KL divergence from the SFT policy (regularization)

**Why the KL penalty?** Without it, the policy collapses to exploit reward model weaknesses (reward hacking) -- producing gibberish that scores high on the imperfect reward model but is nonsensical.

**PPO clip objective** (the RL update itself):

$$L_{\text{PPO}} = \mathbb{E}_t \left[ \min\left( \frac{\pi_\theta(a_t|s_t)}{\pi_{\text{old}}(a_t|s_t)} A_t, \; \text{clip}\left(\frac{\pi_\theta}{\pi_{\text{old}}}, 1-\epsilon, 1+\epsilon\right) A_t \right) \right]$$

where $A_t$ is the advantage estimate and $\epsilon \approx 0.2$ is the clip range.

---

## 2. DPO: Direct Preference Optimization

DPO eliminates the reward model and RL loop entirely, optimizing preferences directly.

### Core insight

The optimal policy under the RLHF objective has a closed-form relationship to the reward:

$$r^*(x, y) = \beta \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \beta \log Z(x)$$

where $Z(x)$ is the partition function (intractable but cancels out in Bradley-Terry).

Substituting into the Bradley-Terry model:

$$P(y_w \succ y_l | x) = \sigma\left(\beta \log \frac{\pi^*(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi^*(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$

### DPO loss function

$$L_{\text{DPO}} = -\mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log \sigma\left(\beta \left( \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right)\right) \right]$$

**Derivation intuition:**
1. Start from the RLHF objective with KL constraint
2. Write the optimal policy in closed form (Lagrangian solution)
3. Express the reward in terms of log-probability ratios
4. Substitute into the Bradley-Terry preference model
5. The partition function $Z(x)$ cancels because we only use *differences*
6. What remains is a classification loss directly on the policy

### DPO gradient intuition

The gradient of $L_{\text{DPO}}$ simultaneously:
- **Increases** $\pi_\theta(y_w|x)$ (make the winner more likely)
- **Decreases** $\pi_\theta(y_l|x)$ (make the loser less likely)
- The magnitude is weighted by how "surprising" the current ranking is

When $\pi_\theta$ already strongly prefers $y_w$, the gradient is small (already correct). When $\pi_\theta$ wrongly prefers $y_l$, the gradient is large (needs correction).

---

## 3. DPO vs RLHF Comparison

| Aspect | RLHF (PPO) | DPO |
|--------|------------|-----|
| **Pipeline** | 3 stages: SFT -> RM -> PPO | 2 stages: SFT -> DPO |
| **Models at train time** | 4 (policy, ref, reward, value) | 2 (policy, ref) |
| **GPU memory** | Very high (4 models) | Moderate (2 models) |
| **Training stability** | Fragile (RL hyperparams) | Stable (standard cross-entropy-like loss) |
| **Reward model needed** | Yes (explicit) | No (implicit in policy) |
| **Hyperparameters** | PPO clip, learning rates, GAE lambda, KL coeff | Just $\beta$ (and standard LR) |
| **Reward hacking risk** | Higher (explicit RM can be exploited) | Lower (no explicit RM to exploit) |
| **Iterative improvement** | Easy (regenerate with new policy, re-rank) | Harder (need new preference data per round) |
| **Online exploration** | Yes (PPO generates new trajectories) | No (offline, fixed dataset) |
| **Performance ceiling** | Higher (with good RM + enough compute) | Comparable for most tasks |
| **Industry adoption** | OpenAI (GPT-4, early), Anthropic | Meta (Llama 2+), most open-source |

### When to choose which

- **DPO** when: limited compute, simpler pipeline desired, single-round alignment, offline preference data
- **RLHF** when: large compute budget, need iterative self-improvement, want online exploration, reward model has other uses (filtering, ranking)

---

## 4. Variants and Extensions

### RLHF variants

| Method | Key idea |
|--------|----------|
| **RLAIF** (Constitutional AI) | AI generates preferences instead of humans |
| **RAFT** (Reward-rAnked Fine-Tuning) | Filter SFT data by reward score, skip RL |
| **ReMax** | Simpler RL algorithm replacing PPO (REINFORCE + baseline) |
| **GRPO** | Group Relative Policy Optimization -- no value model needed |

### DPO variants

| Method | Key change from DPO |
|--------|---------------------|
| **IPO** (Identity PO) | Replaces log-sigmoid with squared hinge loss -- prevents overfitting |
| **KTO** | Works with binary (good/bad) labels instead of paired comparisons |
| **ORPO** | Combines SFT and preference optimization in one stage |
| **SimPO** | Reference-free DPO -- uses sequence length-normalized log-prob |

---

## 5. LLM Distillation

Distillation transfers knowledge from a large "teacher" model to a smaller "student" model.

### Standard knowledge distillation

**Core formula -- KL divergence on logit distributions:**

$$L_{\text{KD}} = \alpha \cdot T^2 \cdot D_{\text{KL}}\left(p_{\text{teacher}}^{(T)} \,\|\, p_{\text{student}}^{(T)}\right) + (1 - \alpha) \cdot L_{\text{CE}}(y, p_{\text{student}}^{(1)})$$

where:
- $p^{(T)}$ = softmax with temperature $T$: $\; p_i^{(T)} = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$
- $T$: temperature (typically 2-20). Higher $T$ = softer distribution = more dark knowledge
- $\alpha$: weight between distillation loss and hard-label loss (typically 0.5-0.9)
- $T^2$ factor: compensates for the reduced gradient magnitude at higher temperatures

### Why temperature scaling works

At $T = 1$ (standard softmax):
- Top class gets ~99% probability, everything else is ~0
- Student only learns "the answer is class A" -- no inter-class relationships

At $T > 1$ (soft targets):
- Distribution is "smoother" -- reveals the teacher's uncertainty
- "Cat is similar to dog but not to car" is encoded in the soft probabilities
- This "dark knowledge" (Hinton et al.) is the key insight of distillation

### LLM-specific distillation strategies

| Strategy | How it works | Example |
|----------|-------------|---------|
| **Logit distillation** | Match teacher/student output distributions | Standard KD on vocabulary logits |
| **Feature distillation** | Match intermediate representations | Align hidden states at matching layers |
| **Sequence-level KD** | Student trains on teacher-generated text | Teacher generates responses, student does SFT |
| **Step-by-step distillation** | Teacher provides reasoning chains | Student learns to produce rationale + answer |

### 70B -> 7B design considerations

For a practical 70B -> 7B distillation:

**Architecture choices:**
- Student typically has same vocabulary as teacher
- Reduce: num_layers (e.g., 80 -> 32), hidden_dim (e.g., 8192 -> 4096), num_heads
- Keep: tokenizer, vocabulary, context length

**Training recipe:**
1. Initialize student from scratch (or from a pretrained 7B)
2. Use teacher to generate high-quality completions for diverse prompts
3. Train student with mixed objective: logit KD + sequence-level KD
4. Typical ratio: 10-50x more training tokens than standard pretraining

**Memory estimation:**

| Model | Params | FP16 memory | With optimizer (AdamW) |
|-------|--------|-------------|----------------------|
| 70B teacher (inference) | 70B | ~140 GB | N/A (frozen) |
| 7B student (training) | 7B | ~14 GB | ~56 GB (4x for Adam states) |
| Total minimum | -- | -- | ~196 GB (~3x A100 80GB) |

### Distillation quality metrics

| Metric | What it measures |
|--------|-----------------|
| **Perplexity gap** | How close student PPL is to teacher PPL |
| **Task accuracy retention** | % of teacher accuracy preserved (aim for >90%) |
| **Latency speedup** | Inference FLOPs ratio (70B/7B ~ 10x) |
| **KL divergence** | Distribution similarity on held-out data |

---

## 6. Common Misunderstandings (Error Corrections)

### Misunderstanding 1: "DPO doesn't use a reward model at all"
**Correction:** DPO has an *implicit* reward model. You can extract it:
$r(x, y) = \beta \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)}$. The key is that DPO
doesn't require *training* a separate reward model -- it's folded into the policy.

### Misunderstanding 2: "RLHF requires millions of preference labels"
**Correction:** The reward model stage typically uses 50K-500K comparison pairs. The PPO
stage generates new data online. InstructGPT used ~33K training prompts with 40K comparisons.

### Misunderstanding 3: "KL penalty in RLHF just prevents forgetting"
**Correction:** The primary purpose is preventing *reward hacking* -- the policy exploiting
flaws in the reward model. Preventing catastrophic forgetting is a secondary benefit.
Without KL penalty, the model generates high-reward gibberish.

### Misunderstanding 4: "Distillation only works with the same architecture"
**Correction:** Cross-architecture distillation works (e.g., GPT-style -> encoder-decoder).
The key requirement is matching output spaces (same vocabulary/tokenizer) for logit-level
distillation, or using sequence-level KD for different tokenizers.

### Misunderstanding 5: "Higher temperature always means better distillation"
**Correction:** There's an optimal range (typically $T = 2$-$10$). Too high and the
distribution becomes uniform, losing discriminative information. Too low and you don't
get enough dark knowledge. $T$ should be tuned on a validation set.

---

## Self-Check Questions

- [ ] **Q1:** Draw the 3-stage RLHF pipeline. For each stage, name the input data type, the loss function, and what model is being trained.
- [ ] **Q2:** Write the DPO loss from memory. Explain why the partition function $Z(x)$ cancels out.
- [ ] **Q3:** You have a 70B teacher and want a 7B student. Walk through the distillation recipe: what loss function, what temperature, how much data, how many GPUs?
- [ ] **Q4:** Compare DPO and RLHF on 5 dimensions: compute cost, stability, performance ceiling, data requirements, and online exploration capability.

---

## Quick Reference Card

```
RLHF Pipeline:  Pretrained -> SFT -> Reward Model -> PPO -> Aligned Model
RM Loss:        L = -E[log sigmoid(r(y_w) - r(y_l))]       (Bradley-Terry)
RLHF Obj:       max E[r(x,y) - beta * KL(pi || pi_ref)]
DPO Loss:       L = -E[log sigma(beta * (log(pi/pi_ref)(y_w) - log(pi/pi_ref)(y_l)))]
KD Loss:        L = alpha * T^2 * KL(p_teacher^T || p_student^T) + (1-alpha) * CE
Temperature:    p_i^T = exp(z_i/T) / sum(exp(z_j/T))       (T>1 = softer)
```
"""


def main() -> None:
    """Insert the RLHF/DPO + Distillation study note into mle_prep.db."""
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))

    # Check Adobe exists
    row = conn.execute(
        "SELECT id FROM companies WHERE id = ?", (COMPANY_ID,)
    ).fetchone()
    if not row:
        print(f"[FAIL] Company id={COMPANY_ID} not found in DB")
        conn.close()
        sys.exit(1)

    # Idempotent: skip if already exists
    existing = conn.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    ).fetchone()
    if existing:
        print(f"[SKIP] Document already exists (id={existing[0]}): {DOC_TITLE}")
        conn.close()
        return

    conn.execute(
        "INSERT INTO company_documents (company_id, title, content, source_type) VALUES (?, ?, ?, ?)",
        (COMPANY_ID, DOC_TITLE, CONTENT, "manual"),
    )
    conn.commit()

    # Verify
    doc = conn.execute(
        "SELECT id, title, length(content) FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    ).fetchone()
    print(f"[DONE] Inserted document id={doc[0]}, title='{doc[1]}', content_length={doc[2]} chars")

    conn.close()


if __name__ == "__main__":
    main()
