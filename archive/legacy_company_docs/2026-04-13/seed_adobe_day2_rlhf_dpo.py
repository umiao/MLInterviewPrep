"""Seed script: Insert Adobe Prep Day2 -- RLHF/DPO Alignment + LLM Distillation study note.

Uses StudyNoteBuilder for typed content generation with FormulaBlock,
auto-bolded terms, prerequisites, and fail-fast single-dollar detection.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import importlib.util
import sys
from pathlib import Path

# Import StudyNoteBuilder from scripts/study_note_builder.py
_BUILDER_PATH = Path(__file__).resolve().parent / "study_note_builder.py"
_spec = importlib.util.spec_from_file_location("study_note_builder", _BUILDER_PATH)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["study_note_builder"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
StudyNoteBuilder = _mod.StudyNoteBuilder
FormulaBlock = _mod.FormulaBlock

COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day2: RLHF/DPO Alignment + LLM Distillation"

# -- HTML Diagram: RLHF 3-Stage Pipeline --
RLHF_PIPELINE_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<span style="background:#4a90d9; padding:6px 12px; border-radius:4px; '
    'color:white;">Stage 1: SFT</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#6b4c9a; padding:6px 12px; border-radius:4px; '
    'color:white;">Stage 2: Reward Model</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#27ae60; padding:6px 12px; border-radius:4px; '
    'color:white;">Stage 3: PPO</span>\n'
    '<br/><br/>\n'
    '<span style="color:#aaa; font-size:12px;">Pretrained LLM</span>\n'
    '<span style="color:#888;"> -> </span>\n'
    '<span style="color:#aaa; font-size:12px;">Fine-tune on demonstrations</span>\n'
    '<span style="color:#888;"> -> </span>\n'
    '<span style="color:#aaa; font-size:12px;">Train preference scorer</span>\n'
    '<span style="color:#888;"> -> </span>\n'
    '<span style="color:#aaa; font-size:12px;">Optimize policy with RL</span>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: DPO vs RLHF Comparison --
DPO_VS_RLHF_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:16px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0; font-size:13px;">\n'
    '<div style="text-align:center; margin-bottom:8px; '
    'font-weight:bold; color:#4a90d9;">RLHF vs DPO Pipeline</div>\n'
    '<pre>\n'
    'RLHF:  Pretrained -> SFT -> Reward Model -> PPO -> Aligned\n'
    '       [3 stages]   [4 models at train time]\n'
    '\n'
    'DPO:   Pretrained -> SFT -> DPO Loss -> Aligned\n'
    '       [2 stages]   [2 models at train time]\n'
    '</pre>\n'
    '</div>'
)

# -- HTML Diagram: Distillation Flow --
DISTILLATION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<span style="background:#c0392b; padding:6px 12px; border-radius:4px; '
    'color:white;">Teacher (70B, frozen)</span>\n'
    '<br/><br/>\n'
    '<span style="color:#aaa;">soft logits (temperature T)</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#d4a017; padding:6px 12px; border-radius:4px; '
    'color:black;">KL Divergence Loss</span>\n'
    '<span style="color:#888;"> <--- </span>\n'
    '<span style="color:#aaa;">soft logits (temperature T)</span>\n'
    '<br/><br/>\n'
    '<span style="background:#27ae60; padding:6px 12px; border-radius:4px; '
    'color:white;">Student (7B, trainable)</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#4a90d9; padding:6px 12px; border-radius:4px; '
    'color:white;">Hard-Label CE Loss</span>\n'
    '<span style="color:#888;"> <--- </span>\n'
    '<span style="color:#aaa;">ground truth labels</span>\n'
    '</div>\n'
    '</div>'
)


def build_day2() -> "StudyNoteBuilder":
    """Build the Day 2 RLHF/DPO + Distillation study note."""
    b = StudyNoteBuilder()

    b.set_title("RLHF/DPO Alignment + LLM Distillation (Adobe Prep Day 2)")

    # -- Prerequisites --
    b.add_prerequisites([
        "Language model pretraining (next-token prediction, cross-entropy loss)",
        "Basic reinforcement learning (policy, reward, objective functions)",
        "Probability fundamentals (sigmoid, KL divergence, softmax)",
        "Day 1: Diffusion Models (cross-reference: latent space, UNet conditioning)",
    ])

    # -- Term Registry --
    b.add_term(
        "RLHF", "Reinforcement Learning from Human Feedback",
        "3-stage pipeline (SFT -> Reward Model -> PPO) that aligns LLMs to human preferences"
    )
    b.add_term(
        "DPO", "Direct Preference Optimization",
        "Eliminates the reward model and RL loop, optimizing preferences directly via a classification loss"
    )
    b.add_term(
        "SFT", "Supervised Fine-Tuning",
        "Stage 1 of RLHF: fine-tune pretrained model on high-quality demonstration data"
    )
    b.add_term(
        "PPO", "Proximal Policy Optimization",
        "RL algorithm used in Stage 3 of RLHF, with clipped surrogate objective for stable updates"
    )
    b.add_term(
        "Bradley-Terry", "Bradley-Terry Model",
        "Preference model where P(A > B) = sigmoid(score_A - score_B), used in reward model training"
    )
    b.add_term(
        "KL divergence", "Kullback-Leibler Divergence",
        "Measures how one probability distribution differs from another; used as regularizer in RLHF"
    )
    b.add_term(
        "reward hacking", "Reward Hacking",
        "When the policy exploits flaws in the reward model to produce high-scoring but nonsensical outputs"
    )
    b.add_term(
        "knowledge distillation", "Knowledge Distillation",
        "Transferring knowledge from a large teacher model to a smaller student model via soft targets"
    )
    b.add_term(
        "dark knowledge", "Dark Knowledge",
        "Inter-class relationships revealed by soft probability distributions at high temperature"
    )

    # -- Section 1: RLHF Pipeline --
    b.add_section("1. RLHF: Three-Step Pipeline", [
        ("> Aligning LLMs to human preferences is the bridge from 'next-token predictor' to\n"
         "> 'useful assistant.' Master the 3-step RLHF pipeline, DPO's elegant shortcut,\n"
         "> and how distillation compresses capabilities into smaller models."),

        "RLHF converts a pretrained LLM into an aligned model through "
        "three sequential stages.",
    ])

    b.add_diagram_html(RLHF_PIPELINE_DIAGRAM)

    # -- Section 1a: Stage 1 SFT --
    b.add_section("### Stage 1: Supervised Fine-Tuning (SFT)", [
        "Fine-tune the pretrained model on high-quality demonstration data "
        "(prompt, ideal_response) pairs.",

        "**Intuition:** SFT teaches the model the format and style of helpful "
        "responses. It is the foundation -- without SFT, the model's outputs "
        "are too noisy for reward model training to work effectively.",

        FormulaBlock(
            latex=r"L_{\text{SFT}} = -\mathbb{E}_{(x,y) \sim D_{\text{demo}}} "
                  r"\left[ \sum_{t=1}^{|y|} \log \pi_{\text{SFT}}(y_t \mid x, y_{<t}) \right]",
            explanation="Standard next-token cross-entropy loss on demonstration data. "
                        "This produces the starting policy $\\pi_{\\text{SFT}}$:",
        ),
    ])

    # -- Section 1b: Stage 2 Reward Model --
    b.add_section("### Stage 2: Reward Model Training", [
        "Collect human preference data: given prompt $x$, a human ranks two "
        "responses $y_w \\succ y_l$ (winner vs loser).",

        "**Intuition:** Instead of trying to specify 'what is a good response' with "
        "a formula, we let humans express preferences between pairs. The reward model "
        "learns to predict which response a human would prefer.",

        "The Bradley-Terry preference model defines:",

        FormulaBlock(
            latex=r"P(y_w \succ y_l \mid x) = \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))",
            explanation="Probability that the winner is preferred, where $\\sigma$ is "
                        "the sigmoid function and $r_\\phi$ is the reward model "
                        "(typically the SFT model with a scalar head replacing the LM head):",
        ),

        FormulaBlock(
            latex=r"L_{\text{RM}} = -\mathbb{E}_{(x, y_w, y_l) \sim D_{\text{pref}}} "
                  r"\left[ \log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l)) \right]",
            explanation="Reward model loss (negative log-likelihood of the observed preferences):",
        ),

        "**Key insight:** The reward model only needs to produce *relative* scores, "
        "not absolute ones. The Bradley-Terry model captures this: only the difference "
        "$r(y_w) - r(y_l)$ matters.",
    ])

    # -- Section 1c: Stage 3 PPO --
    b.add_section("### Stage 3: PPO Optimization", [
        "Use the trained reward model to optimize the policy via "
        "Proximal Policy Optimization.",

        "**Intuition:** Now we have a 'judge' (the reward model). We let the policy "
        "generate responses, score them, and update toward higher-scoring outputs. "
        "The KL penalty keeps it from straying too far from the SFT starting point.",

        FormulaBlock(
            latex=r"\max_{\pi_\theta} \; \mathbb{E}_{x \sim D,\, y \sim \pi_\theta(\cdot|x)} "
                  r"\left[ r_\phi(x, y) - \beta \cdot D_{\text{KL}}"
                  r"(\pi_\theta(\cdot|x) \,\|\, \pi_{\text{SFT}}(\cdot|x)) \right]",
            explanation="RLHF objective -- maximize reward while staying close to the SFT policy:",
        ),

        "where:\n"
        "- $r_\\phi(x, y)$: reward model score for the generated response\n"
        "- $\\beta$: KL penalty coefficient (prevents reward hacking)\n"
        "- $D_{\\text{KL}}$: KL divergence from the SFT policy (regularization)",

        "**Why the KL penalty?** Without it, the policy collapses to exploit reward "
        "model weaknesses (reward hacking) -- producing gibberish that scores high "
        "on the imperfect reward model but is nonsensical.",

        FormulaBlock(
            latex=r"L_{\text{PPO}} = \mathbb{E}_t \left[ \min\left( "
                  r"\frac{\pi_\theta(a_t|s_t)}{\pi_{\text{old}}(a_t|s_t)} A_t, \; "
                  r"\text{clip}\left(\frac{\pi_\theta}{\pi_{\text{old}}}, "
                  r"1-\epsilon, 1+\epsilon\right) A_t \right) \right]",
            explanation="PPO clip objective (the RL update itself), where $A_t$ is the "
                        "advantage estimate and $\\epsilon \\approx 0.2$ is the clip range:",
        ),
    ])

    # -- Section 2: DPO --
    b.add_section("2. DPO: Direct Preference Optimization", [
        "DPO eliminates the reward model and RL loop entirely, optimizing "
        "preferences directly.",

        "### Core insight\n\n"
        "The optimal policy under the RLHF objective has a closed-form relationship "
        "to the reward:",

        FormulaBlock(
            latex=r"r^*(x, y) = \beta \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} "
                  r"+ \beta \log Z(x)",
            explanation="Reward as a function of the optimal policy, where $Z(x)$ is "
                        "the partition function (intractable but cancels out in Bradley-Terry):",
        ),

        "Substituting into the Bradley-Terry model:",

        FormulaBlock(
            latex=r"P(y_w \succ y_l | x) = \sigma\left(\beta \log "
                  r"\frac{\pi^*(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log "
                  r"\frac{\pi^*(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)",
            explanation="Preference probability expressed purely in terms of policy "
                        "log-ratios (the partition function $Z(x)$ cancels because we "
                        "only use *differences*):",
        ),
    ])

    # -- Section 2a: DPO Loss --
    b.add_section("### DPO Loss Function", [
        FormulaBlock(
            latex=r"L_{\text{DPO}} = -\mathbb{E}_{(x, y_w, y_l) \sim D} "
                  r"\left[ \log \sigma\left(\beta \left( \log "
                  r"\frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \log "
                  r"\frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} "
                  r"\right)\right) \right]",
            explanation="The DPO loss -- a classification loss directly on the policy, "
                        "with no reward model or RL loop:",
        ),

        "**Derivation intuition:**\n"
        "1. Start from the RLHF objective with KL constraint\n"
        "2. Write the optimal policy in closed form (Lagrangian solution)\n"
        "3. Express the reward in terms of log-probability ratios\n"
        "4. Substitute into the Bradley-Terry preference model\n"
        "5. The partition function $Z(x)$ cancels because we only use *differences*\n"
        "6. What remains is a classification loss directly on the policy",
    ])

    # -- Section 2b: DPO Gradient --
    b.add_section("### DPO Gradient Intuition", [
        "The gradient of $L_{\\text{DPO}}$ simultaneously:\n"
        "- **Increases** $\\pi_\\theta(y_w|x)$ (make the winner more likely)\n"
        "- **Decreases** $\\pi_\\theta(y_l|x)$ (make the loser less likely)\n"
        "- The magnitude is weighted by how 'surprising' the current ranking is",

        "When $\\pi_\\theta$ already strongly prefers $y_w$, the gradient is small "
        "(already correct). When $\\pi_\\theta$ wrongly prefers $y_l$, the gradient "
        "is large (needs correction).",
    ])

    # -- Section 3: DPO vs RLHF Comparison --
    b.add_section("3. DPO vs RLHF Comparison", [])

    b.add_diagram_html(DPO_VS_RLHF_DIAGRAM)

    b.add_comparison_table(
        headers=["Aspect", "RLHF (PPO)", "DPO"],
        rows=[
            ["**Pipeline**", "3 stages: SFT -> RM -> PPO",
             "2 stages: SFT -> DPO"],
            ["**Models at train time**", "4 (policy, ref, reward, value)",
             "2 (policy, ref)"],
            ["**GPU memory**", "Very high (4 models)",
             "Moderate (2 models)"],
            ["**Training stability**", "Fragile (RL hyperparams)",
             "Stable (cross-entropy-like loss)"],
            ["**Reward model needed**", "Yes (explicit)",
             "No (implicit in policy)"],
            ["**Hyperparameters**", "PPO clip, LRs, GAE lambda, KL coeff",
             "Just $\\beta$ (and standard LR)"],
            ["**Reward hacking risk**", "Higher (explicit RM can be exploited)",
             "Lower (no explicit RM to exploit)"],
            ["**Iterative improvement**", "Easy (regenerate, re-rank)",
             "Harder (need new preference data)"],
            ["**Online exploration**", "Yes (PPO generates new trajectories)",
             "No (offline, fixed dataset)"],
            ["**Performance ceiling**", "Higher (with good RM + compute)",
             "Comparable for most tasks"],
            ["**Industry adoption**", "OpenAI (GPT-4, early), Anthropic",
             "Meta (Llama 2+), most open-source"],
        ],
        title="Head-to-Head Comparison",
    )

    b.add_section("### When to Choose Which", [
        "- **DPO** when: limited compute, simpler pipeline desired, single-round "
        "alignment, offline preference data\n"
        "- **RLHF** when: large compute budget, need iterative self-improvement, "
        "want online exploration, reward model has other uses (filtering, ranking)",
    ])

    # -- Section 4: Variants and Extensions --
    b.add_section("4. Variants and Extensions", [
        "### RLHF variants",
    ])

    b.add_comparison_table(
        headers=["Method", "Key Idea"],
        rows=[
            ["**RLAIF** (Constitutional AI)", "AI generates preferences instead of humans"],
            ["**RAFT** (Reward-rAnked Fine-Tuning)", "Filter SFT data by reward score, skip RL"],
            ["**ReMax**", "Simpler RL algorithm replacing PPO (REINFORCE + baseline)"],
            ["**GRPO**", "Group Relative Policy Optimization -- no value model needed"],
        ],
        title="RLHF Variants",
    )

    b.add_section("### DPO variants", [])

    b.add_comparison_table(
        headers=["Method", "Key Change from DPO"],
        rows=[
            ["**IPO** (Identity PO)", "Replaces log-sigmoid with squared hinge loss -- prevents overfitting"],
            ["**KTO**", "Works with binary (good/bad) labels instead of paired comparisons"],
            ["**ORPO**", "Combines SFT and preference optimization in one stage"],
            ["**SimPO**", "Reference-free DPO -- uses sequence length-normalized log-prob"],
        ],
        title="DPO Variants",
    )

    # -- Section 5: LLM Distillation --
    b.add_section("5. LLM Distillation", [
        "Distillation transfers knowledge from a large 'teacher' model to a "
        "smaller 'student' model.",

        "**Intuition:** The teacher's soft probability distribution over classes "
        "contains far richer information than hard labels alone. A cat image might "
        "get 90% cat, 8% dog, 2% car -- the 8% dog tells the student that cats "
        "and dogs are visually similar, which hard labels never reveal. This is "
        "dark knowledge (Hinton et al.).",

        "### Standard knowledge distillation",
    ])

    b.add_diagram_html(DISTILLATION_DIAGRAM)

    b.add_section("### Core Distillation Formula", [
        FormulaBlock(
            latex=r"L_{\text{KD}} = \alpha \cdot T^2 \cdot D_{\text{KL}}"
                  r"\left(p_{\text{teacher}}^{(T)} \,\|\, p_{\text{student}}^{(T)}\right) "
                  r"+ (1 - \alpha) \cdot L_{\text{CE}}(y, p_{\text{student}}^{(1)})",
            explanation="Combined distillation loss: KL divergence on soft targets + "
                        "cross-entropy on hard labels:",
        ),

        "where:\n"
        "- $p^{(T)}$ = softmax with temperature $T$: "
        "$p_i^{(T)} = \\frac{\\exp(z_i / T)}{\\sum_j \\exp(z_j / T)}$\n"
        "- $T$: temperature (typically 2-20). Higher $T$ = softer distribution = more dark knowledge\n"
        "- $\\alpha$: weight between distillation loss and hard-label loss (typically 0.5-0.9)\n"
        "- $T^2$ factor: compensates for the reduced gradient magnitude at higher temperatures",
    ])

    # -- Section 5b: Why Temperature Works --
    b.add_section("### Why Temperature Scaling Works", [
        "At $T = 1$ (standard softmax):\n"
        "- Top class gets ~99% probability, everything else is ~0\n"
        "- Student only learns 'the answer is class A' -- no inter-class relationships",

        "At $T > 1$ (soft targets):\n"
        "- Distribution is 'smoother' -- reveals the teacher's uncertainty\n"
        "- 'Cat is similar to dog but not to car' is encoded in the soft probabilities\n"
        "- This dark knowledge (Hinton et al.) is the key insight of distillation",
    ])

    # -- Section 5c: LLM-Specific Strategies --
    b.add_section("### LLM-Specific Distillation Strategies", [])

    b.add_comparison_table(
        headers=["Strategy", "How It Works", "Example"],
        rows=[
            ["**Logit distillation**", "Match teacher/student output distributions",
             "Standard KD on vocabulary logits"],
            ["**Feature distillation**", "Match intermediate representations",
             "Align hidden states at matching layers"],
            ["**Sequence-level KD**", "Student trains on teacher-generated text",
             "Teacher generates responses, student does SFT"],
            ["**Step-by-step distillation**", "Teacher provides reasoning chains",
             "Student learns to produce rationale + answer"],
        ],
    )

    # -- Section 5d: 70B -> 7B Design --
    b.add_section("### 70B -> 7B Design Considerations", [
        "**Architecture choices:**\n"
        "- Student typically has same vocabulary as teacher\n"
        "- Reduce: num_layers (e.g., 80 -> 32), hidden_dim (e.g., 8192 -> 4096), num_heads\n"
        "- Keep: tokenizer, vocabulary, context length",

        "**Training recipe:**\n"
        "1. Initialize student from scratch (or from a pretrained 7B)\n"
        "2. Use teacher to generate high-quality completions for diverse prompts\n"
        "3. Train student with mixed objective: logit KD + sequence-level KD\n"
        "4. Typical ratio: 10-50x more training tokens than standard pretraining",
    ])

    b.add_comparison_table(
        headers=["Model", "Params", "FP16 Memory", "With Optimizer (AdamW)"],
        rows=[
            ["70B teacher (inference)", "70B", "~140 GB", "N/A (frozen)"],
            ["7B student (training)", "7B", "~14 GB", "~56 GB (4x for Adam states)"],
            ["Total minimum", "--", "--", "~196 GB (~3x A100 80GB)"],
        ],
        title="Memory Estimation",
    )

    # -- Section 5e: Distillation Quality Metrics --
    b.add_comparison_table(
        headers=["Metric", "What It Measures"],
        rows=[
            ["**Perplexity gap**", "How close student PPL is to teacher PPL"],
            ["**Task accuracy retention**", "% of teacher accuracy preserved (aim for >90%)"],
            ["**Latency speedup**", "Inference FLOPs ratio (70B/7B ~ 10x)"],
            ["**KL divergence**", "Distribution similarity on held-out data"],
        ],
        title="Distillation Quality Metrics",
    )

    # -- Section 6: Common Misunderstandings --
    b.add_section("6. Common Misunderstandings (Error Corrections)", [
        "### Misunderstanding 1: 'DPO does not use a reward model at all'\n\n"
        "**Correction:** DPO has an *implicit* reward model. You can extract it:\n"
        "$r(x, y) = \\beta \\log \\frac{\\pi_\\theta(y|x)}{\\pi_{\\text{ref}}(y|x)}$. "
        "The key is that DPO doesn't require *training* a separate reward model -- "
        "it's folded into the policy.",

        "### Misunderstanding 2: 'RLHF requires millions of preference labels'\n\n"
        "**Correction:** The reward model stage typically uses 50K-500K comparison pairs. "
        "The PPO stage generates new data online. InstructGPT used ~33K training prompts "
        "with 40K comparisons.",

        "### Misunderstanding 3: 'KL penalty in RLHF just prevents forgetting'\n\n"
        "**Correction:** The primary purpose is preventing *reward hacking* -- the policy "
        "exploiting flaws in the reward model. Preventing catastrophic forgetting is a "
        "secondary benefit. Without KL penalty, the model generates high-reward gibberish.",

        "### Misunderstanding 4: 'Distillation only works with the same architecture'\n\n"
        "**Correction:** Cross-architecture distillation works (e.g., GPT-style -> "
        "encoder-decoder). The key requirement is matching output spaces (same "
        "vocabulary/tokenizer) for logit-level distillation, or using sequence-level KD "
        "for different tokenizers.",

        "### Misunderstanding 5: 'Higher temperature always means better distillation'\n\n"
        "**Correction:** There's an optimal range (typically $T = 2$-$10$). Too high "
        "and the distribution becomes uniform, losing discriminative information. Too low "
        "and you don't get enough dark knowledge. $T$ should be tuned on a validation set.",
    ])

    # -- Self-Check --
    b.add_checklist("Self-Check Questions", [
        "**Q1:** Draw the 3-stage RLHF pipeline. For each stage, name the "
        "input data type, the loss function, and what model is being trained.",
        "**Q2:** Write the DPO loss from memory. Explain why the partition "
        "function $Z(x)$ cancels out.",
        "**Q3:** You have a 70B teacher and want a 7B student. Walk through "
        "the distillation recipe: what loss function, what temperature, how "
        "much data, how many GPUs?",
        "**Q4:** Compare DPO and RLHF on 5 dimensions: compute cost, stability, "
        "performance ceiling, data requirements, and online exploration capability.",
        "**Q5:** What is reward hacking and why does the KL penalty prevent it? "
        "Cross-reference: how does CFG guidance scale in Day 1 (Diffusion) "
        "present a similar quality-diversity trade-off?",
    ])

    # -- Quick Reference --
    b.add_section("Quick Reference Card", [
        "```\n"
        "RLHF Pipeline:  Pretrained -> SFT -> Reward Model -> PPO -> Aligned Model\n"
        "RM Loss:        L = -E[log sigmoid(r(y_w) - r(y_l))]       (Bradley-Terry)\n"
        "RLHF Obj:       max E[r(x,y) - beta * KL(pi || pi_ref)]\n"
        "DPO Loss:       L = -E[log sigma(beta * (log(pi/pi_ref)(y_w) - log(pi/pi_ref)(y_l)))]\n"
        "KD Loss:        L = alpha * T^2 * KL(p_teacher^T || p_student^T) + (1-alpha) * CE\n"
        "Temperature:    p_i^T = exp(z_i/T) / sum(exp(z_j/T))       (T>1 = softer)\n"
        "```",
    ])

    return b


def main() -> None:
    """Build and save the RLHF/DPO + Distillation study note to mle_prep.db."""
    b = build_day2()

    # Build first to validate (fail-fast on single-dollar)
    content = b.build()

    # Validate the built content
    warnings = StudyNoteBuilder.validate(content)
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")

    print(f"[INFO] Built content: {len(content)} chars")

    # Save to database (idempotent -- updates if title exists)
    b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)


if __name__ == "__main__":
    main()
