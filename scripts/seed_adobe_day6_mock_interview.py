"""Seed script: Insert Adobe Prep Day6 -- Mock Interview Questions + STAR-T Stories note.

Uses StudyNoteBuilder for typed content generation with FormulaBlock,
auto-bolded terms, prerequisites, and fail-fast single-dollar detection.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: deletes old raw-string version, inserts Builder-generated version.
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
DOC_TITLE = "Adobe Prep Day6: Mock Interview Questions + STAR-T Project Stories"

# ---------------------------------------------------------------------------
# HTML Diagrams
# ---------------------------------------------------------------------------

# -- STAR-T Framework Table --
STAR_T_FRAMEWORK_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">STAR-T Framework</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Letter</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Component</th>\n'
    '<th style="padding:8px 16px; text-align:left;">What to Include</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Time</th>\n'
    '</tr>\n'
    '<tr style="background:#4a90d9; color:white;">\n'
    '<td style="padding:8px 16px;"><b>S</b></td>\n'
    '<td style="padding:8px 16px;">Situation</td>\n'
    '<td style="padding:8px 16px;">Team, product, scale, constraint. Set the stage in 1-2 sentences.</td>\n'
    '<td style="padding:8px 16px;">~15s</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;"><b>T</b></td>\n'
    '<td style="padding:8px 16px;">Task</td>\n'
    '<td style="padding:8px 16px;">Your specific responsibility. What was the problem you owned?</td>\n'
    '<td style="padding:8px 16px;">~15s</td>\n'
    '</tr>\n'
    '<tr style="background:#2d6a4f; color:white;">\n'
    '<td style="padding:8px 16px;"><b>A</b></td>\n'
    '<td style="padding:8px 16px;">Approach</td>\n'
    '<td style="padding:8px 16px;">Technical decisions, tradeoffs, alternatives considered. This is the core -- show depth.</td>\n'
    '<td style="padding:8px 16px;">~60s</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;"><b>R</b></td>\n'
    '<td style="padding:8px 16px;">Result</td>\n'
    '<td style="padding:8px 16px;">Quantified impact: latency, throughput, accuracy, cost. Use concrete numbers.</td>\n'
    '<td style="padding:8px 16px;">~15s</td>\n'
    '</tr>\n'
    '<tr style="background:#8b5cf6; color:white;">\n'
    '<td style="padding:8px 16px;"><b>T</b></td>\n'
    '<td style="padding:8px 16px;">Transfer</td>\n'
    '<td style="padding:8px 16px;">Bridge to Adobe: "At Adobe\'s scale with Firefly / Document Cloud / Creative Cloud, I would apply this by..."</td>\n'
    '<td style="padding:8px 16px;">~15s</td>\n'
    '</tr>\n'
    '</table>\n'
    '<div style="margin-top:12px; color:#ccc; font-size:12px;">\n'
    'Total: ~2 minutes per story. Practice to stay under 2.5 min.\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- STAR-T Fill-in Template --
STAR_T_TEMPLATE_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'STORY TEMPLATE:\n'
    '\n'
    '[S] "On the ___ team at ___, we were building ___ that served ___ users/requests.\n'
    '     The main constraint was ___."\n'
    '\n'
    '[T] "I was responsible for ___. The specific challenge was ___."\n'
    '\n'
    '[A] "I chose to ___ because ___. I considered ___ as an alternative, but ___.\n'
    '     The key technical insight was ___. I implemented ___ which involved ___."\n'
    '\n'
    '[R] "This resulted in ___ (metric improvement). Specifically: ___% improvement\n'
    '     in ___, reducing ___ from ___ to ___."\n'
    '\n'
    '[T] "At Adobe, this directly applies to ___ because ___. For example, in\n'
    '     Firefly\'s ___ pipeline, the same approach would ___."\n'
    '</pre>\n'
    '</div>'
)

# -- Story 1: Inference Pipeline Optimization --
STORY1_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Story 1: Inference Pipeline Optimization</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    '[S] ML team serving a production model with growing request volume.\n'
    '    Latency SLA: P99 < 200ms. Current P99: ~450ms under peak load.\n'
    '\n'
    '[T] Owned end-to-end inference optimization. Needed to hit SLA without\n'
    '    adding GPU capacity (cost constraint).\n'
    '\n'
    '[A] Profiled the pipeline end-to-end:\n'
    '    - Identified KV-cache memory fragmentation as primary bottleneck\n'
    '    - Implemented operator fusion to reduce HBM round-trips\n'
    '      (analogous to FlashAttention\'s tiling approach)\n'
    '    - Applied INT8 weight quantization with per-channel scaling\n'
    '      (SmoothQuant-inspired activation migration)\n'
    '    - Redesigned batching: moved from static to iteration-level\n'
    '      scheduling (continuous batching pattern)\n'
    '    - Considered INT4 quantization but accuracy regression on\n'
    '      edge cases was >2% -- chose INT8 as the Pareto-optimal point\n'
    '\n'
    '[R] P99 latency: 450ms -> 165ms (63% reduction)\n'
    '    Throughput: 2.4x improvement without additional GPUs\n'
    '    Model accuracy: <0.3% degradation (within tolerance)\n'
    '\n'
    '[T] At Adobe, Firefly serves millions of image generation requests.\n'
    '    The same profiling-first, quantize-smartly, batch-efficiently\n'
    '    approach directly applies to their diffusion model serving stack.\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- Story 2: Distributed Training --
STORY2_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Story 2: Distributed Training</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    '[S] Training a large model that did not fit on a single GPU.\n'
    '    Team of 3 engineers, 8-GPU cluster available.\n'
    '\n'
    '[T] Designed and implemented the distributed training strategy.\n'
    '    Goal: linear scaling efficiency while maintaining convergence.\n'
    '\n'
    '[A] Analyzed model size vs memory:\n'
    '    - Model params + optimizer states exceeded single GPU memory\n'
    '    - Implemented FSDP (Fully Sharded Data Parallelism) for memory\n'
    '      efficiency: shard params, gradients, AND optimizer states\n'
    '    - Used mixed-precision training (bf16 forward/backward, fp32\n'
    '      master weights) to halve activation memory\n'
    '    - Applied gradient checkpointing on transformer blocks to trade\n'
    '      compute for memory (recompute activations in backward pass)\n'
    '    - Tuned: all-reduce bucket size, gradient accumulation steps,\n'
    '      learning rate warmup schedule for multi-GPU stability\n'
    '\n'
    '    Considered alternatives:\n'
    '    - Pure DP: OOM on single GPU (model too large)\n'
    '    - Pipeline parallelism: uneven stage splitting caused bubbles\n'
    '    - FSDP won: memory-efficient + near-linear scaling\n'
    '\n'
    '[R] Training time: 14 days -> 2.1 days (6.7x speedup on 8 GPUs)\n'
    '    Scaling efficiency: 84% (vs theoretical 100% linear)\n'
    '    Memory per GPU: reduced from OOM to 68% utilization\n'
    '\n'
    '[T] Adobe trains foundation models for Firefly and document AI.\n'
    '    FSDP + mixed precision is exactly their stack. My experience\n'
    '    debugging communication overhead and tuning sharding strategies\n'
    '    translates directly.\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- Story 3: Data Quality + Alignment --
STORY3_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Story 3: Data Quality + Alignment</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    '[S] Production model generating outputs that were technically correct\n'
    '    but misaligned with user intent. User satisfaction scores declining.\n'
    '    Feedback data was available but not being leveraged.\n'
    '\n'
    '[T] Led the effort to incorporate human feedback into the model\n'
    '    improvement loop. Owned data pipeline + training changes.\n'
    '\n'
    '[A] Built a three-stage improvement pipeline:\n'
    '    1. Data collection: designed annotation interface, collected\n'
    '       preference pairs (chosen vs rejected outputs)\n'
    '    2. Reward model: trained a reward model on preference data\n'
    '       to score output quality (Bradley-Terry preference model)\n'
    '    3. Alignment: applied DPO (Direct Preference Optimization)\n'
    '       rather than full RLHF -- simpler, no separate RL loop\n'
    '       - DPO loss: directly optimizes policy using preference pairs\n'
    '       - Avoided PPO instability and reward hacking issues\n'
    '    4. Evaluation: built automated eval pipeline with human-in-loop\n'
    '       validation on edge cases\n'
    '\n'
    '    Key decision: DPO over RLHF\n'
    '    - RLHF requires reward model + PPO training loop (complex)\n'
    '    - DPO achieves comparable quality with single supervised step\n'
    '    - Trade-off: DPO is less flexible for iterative reward shaping\n'
    '\n'
    '[R] User satisfaction: +18% (measured via A/B test, n=5000)\n'
    '    Output quality score (reward model): 0.72 -> 0.89\n'
    '    Training cost: 3x cheaper than equivalent RLHF pipeline\n'
    '\n'
    '[T] Adobe\'s generative AI products (Firefly, Acrobat AI) need\n'
    '    alignment with creative intent and brand safety. My experience\n'
    '    building preference-based alignment pipelines directly applies\n'
    '    to their content generation quality loop.\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- Q&A diagrams --
Q1_DDPM_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q1: Explain the forward and reverse process of DDPM</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>Forward process (diffusion):</b>\n'
    '<br/>- Gradually add Gaussian noise over T steps\n'
    '<br/>- Closed-form jump to any timestep via the reparameterization trick\n'
    '<br/>- After T steps (~1000), x_T is approximately pure Gaussian noise\n'
    '<br/><br/>\n'
    '<b>Reverse process (denoising):</b>\n'
    '<br/>- Learn p_theta(x_{t-1} | x_t) parameterized by a neural network\n'
    '<br/>- Network predicts the noise epsilon_theta(x_t, t)\n'
    '<br/>- Generate by sampling x_T ~ N(0,I) then iteratively denoising\n'
    '<br/><br/>\n'
    '<b>Key point:</b> The forward process has no learnable parameters. '
    'All learning is in the reverse process (the denoiser network).\n'
    '</div>\n'
    '</div>'
)

Q2_CFG_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q2: What is classifier-free guidance (CFG) and why is it used?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>Problem:</b> Unconditional diffusion models generate diverse but often low-quality/irrelevant outputs.\n'
    '<br/><br/>\n'
    '<b>Classifier guidance:</b> Use gradient of a separate classifier p(y|x_t) to steer generation. '
    'Problem: requires a trained classifier that works on noisy inputs.\n'
    '<br/><br/>\n'
    '<b>Classifier-free guidance (CFG):</b>\n'
    '<br/>- Train ONE model with conditional and unconditional denoising (randomly drop condition during training)\n'
    '<br/>- At inference: eps_guided = eps_uncond + w * (eps_cond - eps_uncond)\n'
    '<br/>- w > 1 amplifies the condition signal. Typical w = 7.5 for text-to-image.\n'
    '<br/><br/>\n'
    '<b>Tradeoff:</b> Higher w = better text alignment but lower diversity and potential artifacts. '
    'w = 1 = no guidance. w too high = oversaturated/distorted images.\n'
    '<br/><br/>\n'
    '<b>Why it matters at Adobe:</b> Firefly uses CFG to ensure generated images match text prompts '
    'while maintaining visual quality.\n'
    '</div>\n'
    '</div>'
)

Q3_LATENT_DIFFUSION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q3: How does Latent Diffusion (Stable Diffusion) differ from pixel-space diffusion?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>Pixel-space diffusion:</b> Operates on full-resolution images (e.g., 512x512x3). Very expensive.\n'
    '<br/><br/>\n'
    '<b>Latent diffusion:</b>\n'
    '<br/>- Step 1: Train a VAE to encode images to a compact latent space (e.g., 64x64x4) -- 8x spatial compression\n'
    '<br/>- Step 2: Run the diffusion process in latent space\n'
    '<br/>- Step 3: Decode latent back to pixel space via VAE decoder\n'
    '<br/><br/>\n'
    '<b>Benefits:</b>\n'
    '<br/>- 64x fewer pixels to denoise (64x64 vs 512x512)\n'
    '<br/>- Training is ~10x faster\n'
    '<br/>- Inference is ~10x faster\n'
    '<br/>- Latent space captures semantic structure, improving generation quality\n'
    '<br/><br/>\n'
    '<b>Conditioning:</b> Cross-attention between latent features and text embeddings (CLIP/T5).\n'
    '<br/><br/>\n'
    '<b>Key point:</b> The VAE is trained separately and frozen during diffusion training. '
    'Perceptual quality depends on VAE quality.\n'
    '</div>\n'
    '</div>'
)

Q4_DDPM_VS_DDIM_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q4: Compare DDPM vs DDIM sampling. When would you use each?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>DDPM sampling:</b>\n'
    '<br/>- Stochastic: adds noise at each reverse step\n'
    '<br/>- Requires all T steps (typically T=1000) for good quality\n'
    '<br/>- Slow but high diversity\n'
    '<br/><br/>\n'
    '<b>DDIM sampling:</b>\n'
    '<br/>- Deterministic: removes the noise injection in reverse steps\n'
    '<br/>- Can skip steps (e.g., 50 steps instead of 1000) with minimal quality loss\n'
    '<br/>- Same trained model -- DDIM is just a different sampling schedule\n'
    '<br/>- Enables interpolation in latent space (deterministic mapping x_T -> x_0)\n'
    '<br/><br/>\n'
    '<b>When to use:</b>\n'
    '<br/>- DDPM: when diversity matters and compute budget allows (creative exploration)\n'
    '<br/>- DDIM: production serving (fast), image editing (deterministic inversion), interpolation\n'
    '<br/><br/>\n'
    '<b>Modern samplers:</b> DPM-Solver, DPM-Solver++ achieve good quality in 10-25 steps '
    'by treating the diffusion ODE more carefully.\n'
    '</div>\n'
    '</div>'
)

Q5_FLASH_ATTENTION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q5: Explain FlashAttention. Why is it faster without reducing FLOPs?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>Problem:</b> Standard attention materializes the N x N attention matrix in HBM. '
    'The bottleneck is memory I/O, not compute.\n'
    '<br/><br/>\n'
    '<b>FlashAttention solution:</b>\n'
    '<br/>- Tile the computation: process Q, K, V in blocks that fit in SRAM (~20MB on A100)\n'
    '<br/>- Never write the full N x N matrix to HBM\n'
    '<br/>- Use the "online softmax" trick to maintain running max and sum across tiles\n'
    '<br/><br/>\n'
    '<b>Result:</b> Same FLOPs (slightly more due to recomputation in backward), '
    'but 2-4x wall-clock speedup on A100 because HBM access is the bottleneck '
    '(2 TB/s) vs SRAM (19 TB/s).\n'
    '<br/><br/>\n'
    '<b>Common misconception to preempt:</b> "FlashAttention is faster because it does less computation." '
    'No -- it does the same computation but minimizes expensive HBM reads/writes.\n'
    '</div>\n'
    '</div>'
)

Q6_SPECULATIVE_DECODING_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q6: How does speculative decoding work? Prove it is lossless.</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>Mechanism:</b>\n'
    '<br/>1. Draft model generates K candidate tokens autoregressively (fast, small model)\n'
    '<br/>2. Target model verifies all K tokens in one forward pass (parallel)\n'
    '<br/>3. For each token i: if P_target(token_i) >= P_draft(token_i), accept\n'
    '<br/>4. If token i is rejected: resample from adjusted distribution, discard tokens i+1..K\n'
    '<br/>5. Always generate at least 1 token (the resampled one)\n'
    '<br/><br/>\n'
    '<b>Why lossless:</b>\n'
    '<br/>- Rejection sampling guarantees: the accepted tokens follow P_target exactly\n'
    '<br/>- Accepted with probability min(1, P_target(x) / P_draft(x))\n'
    '<br/>- Rejected tokens are resampled from: norm(max(0, P_target(x) - P_draft(x)))\n'
    '<br/>- This is the standard rejection sampling correction -- mathematically, '
    'the output distribution equals P_target\n'
    '<br/><br/>\n'
    '<b>Speedup:</b> ~K * acceptance_rate tokens per target forward pass. '
    'Typical: 2-3x with K=5, 70-80% acceptance.\n'
    '<br/><br/>\n'
    '<b>Draft model choices:</b> Smaller version of target, quantized target, '
    'n-gram model, or Medusa-style parallel heads.\n'
    '</div>\n'
    '</div>'
)

Q7_GPTQ_AWQ_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q7: Compare GPTQ vs AWQ. When would you choose each?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>GPTQ:</b>\n'
    '<br/>- Based on Optimal Brain Surgeon (OBS)\n'
    '<br/>- Quantizes weights column-by-column, compensating error in remaining columns using Hessian\n'
    '<br/>- Requires calibration data (~128 samples) for Hessian computation\n'
    '<br/>- Strong theoretical foundation (minimizes layer-wise output error)\n'
    '<br/>- Slower to quantize (sequential column processing)\n'
    '<br/><br/>\n'
    '<b>AWQ:</b>\n'
    '<br/>- Observes: ~1% of weight channels are "salient" (correspond to large activations)\n'
    '<br/>- Applies per-channel scaling to protect salient channels before quantization\n'
    '<br/>- Scaling factor absorbed into previous layer (zero runtime overhead)\n'
    '<br/>- Faster quantization, often better quality at INT4\n'
    '<br/><br/>\n'
    '<b>When to choose:</b>\n'
    '<br/>- GPTQ: when you need maximum quality and calibration data is available, '
    'or for very small models where every bit matters\n'
    '<br/>- AWQ: for production deployment where quantization speed matters, '
    'and for larger models (>13B) where it typically wins\n'
    '<br/>- Both: INT4 weight-only, post-training, compatible with vLLM/TensorRT-LLM\n'
    '</div>\n'
    '</div>'
)

Q8_DP_TP_PP_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q8: Compare Data Parallelism, Tensor Parallelism, and Pipeline Parallelism</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>Data Parallelism (DP):</b>\n'
    '<br/>- Each GPU holds a full model copy, processes different data batches\n'
    '<br/>- Synchronize gradients via all-reduce after backward pass\n'
    '<br/>- Simple but requires model to fit on one GPU\n'
    '<br/>- Communication: gradient all-reduce O(params) per step\n'
    '<br/><br/>\n'
    '<b>Tensor Parallelism (TP):</b>\n'
    '<br/>- Split individual layers (e.g., attention heads, MLP columns) across GPUs\n'
    '<br/>- Each GPU computes part of each layer, then all-reduce activations\n'
    '<br/>- Requires high-bandwidth interconnect (NVLink) -- within a node only\n'
    '<br/>- Communication: activation all-reduce at every layer\n'
    '<br/><br/>\n'
    '<b>Pipeline Parallelism (PP):</b>\n'
    '<br/>- Assign different layers to different GPUs (stage 0: layers 0-15, stage 1: layers 16-31)\n'
    '<br/>- Micro-batching to reduce bubble time (idle GPU time between stages)\n'
    '<br/>- Communication: activation tensors between stages (point-to-point)\n'
    '<br/><br/>\n'
    '<b>Combining them (3D parallelism):</b> TP within nodes (fast NVLink), '
    'PP across nodes (slower network), DP across node groups.\n'
    '</div>\n'
    '</div>'
)

Q9_FSDP_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q9: What is FSDP and how does it differ from standard DP?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>Standard DP memory usage per GPU:</b>\n'
    '<br/>- Full model parameters (e.g., 2 bytes/param in fp16)\n'
    '<br/>- Full gradients (2 bytes/param)\n'
    '<br/>- Full optimizer states (8 bytes/param for Adam: momentum + variance + fp32 copy)\n'
    '<br/>- Total: ~12 bytes/param per GPU (all redundant copies!)\n'
    '<br/><br/>\n'
    '<b>FSDP (Fully Sharded Data Parallelism) / ZeRO:</b>\n'
    '<br/>- ZeRO Stage 1: Shard optimizer states only -> 4 + 8/N bytes/param\n'
    '<br/>- ZeRO Stage 2: Shard optimizer states + gradients -> 2 + (2+8)/N bytes/param\n'
    '<br/>- ZeRO Stage 3 / FSDP: Shard everything (params + gradients + optimizer) -> (2+2+8)/N bytes/param\n'
    '<br/>- All-gather params before forward/backward, reduce-scatter gradients after\n'
    '<br/><br/>\n'
    '<b>Tradeoff:</b> FSDP uses ~N times less memory but adds communication overhead '
    '(all-gather at each layer). Works well when communication bandwidth is high (intra-node NVLink).\n'
    '<br/><br/>\n'
    '<b>Practical tip:</b> FSDP with mixed precision (bf16 compute, fp32 master weights) '
    'is the default for training models 7B-70B on typical clusters.\n'
    '</div>\n'
    '</div>'
)

Q10_DEBUG_DISTRIBUTED_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q10: How do you debug slow distributed training?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline (systematic approach):</b>\n'
    '<br/><br/>\n'
    '<b>Step 1: Profile</b>\n'
    '<br/>- Use PyTorch Profiler or NVIDIA Nsight to get per-operation breakdown\n'
    '<br/>- Identify: is bottleneck compute, communication, or memory (OOM -> swapping)?\n'
    '<br/><br/>\n'
    '<b>Step 2: Check communication</b>\n'
    '<br/>- Measure all-reduce time vs compute time ratio\n'
    '<br/>- If communication-bound: increase compute-to-communication ratio '
    '(larger batch, gradient accumulation)\n'
    '<br/>- Check NCCL topology: is NVLink being used? Or falling back to PCIe?\n'
    '<br/><br/>\n'
    '<b>Step 3: Check GPU utilization</b>\n'
    '<br/>- nvidia-smi: are all GPUs at ~100% utilization?\n'
    '<br/>- Uneven utilization = load imbalance (PP bubble, uneven data distribution)\n'
    '<br/><br/>\n'
    '<b>Step 4: Check memory</b>\n'
    '<br/>- Activation memory: apply gradient checkpointing (selective, not full)\n'
    '<br/>- Optimizer memory: switch to FSDP if using standard DP\n'
    '<br/><br/>\n'
    '<b>Common fixes:</b>\n'
    '<br/>- Overlap communication with computation (async all-reduce)\n'
    '<br/>- Tune all-reduce bucket size (PyTorch default may not be optimal)\n'
    '<br/>- Use bf16 mixed precision if not already\n'
    '<br/>- Increase gradient accumulation steps to amortize communication\n'
    '</div>\n'
    '</div>'
)

Q11_RLHF_VS_DPO_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q11: Compare RLHF vs DPO. What are the tradeoffs?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>RLHF (3 stages):</b>\n'
    '<br/>1. SFT: Fine-tune base model on high-quality demonstrations\n'
    '<br/>2. Reward Model: Train RM on preference pairs using Bradley-Terry model\n'
    '<br/>3. PPO: Optimize policy to maximize reward while staying close to SFT model (KL penalty)\n'
    '<br/><br/>\n'
    '<b>DPO (1 stage after SFT):</b>\n'
    '<br/>- Key insight: the optimal policy under RLHF objective has a closed-form '
    'relationship with the reward\n'
    '<br/>- Substitute into Bradley-Terry -> DPO loss that directly optimizes the policy\n'
    '<br/>- No separate reward model, no RL training loop\n'
    '<br/><br/>\n'
    '<b>Tradeoffs:</b>\n'
    '<br/>- RLHF: more flexible (reward model can be used for other purposes, iterative refinement), '
    'but unstable (PPO tuning, reward hacking)\n'
    '<br/>- DPO: simpler, more stable, cheaper compute, but less flexible '
    '(no explicit reward signal for analysis)\n'
    '<br/>- DPO may underperform RLHF on tasks requiring very precise reward shaping\n'
    '</div>\n'
    '</div>'
)

Q12_REWARD_HACKING_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q12: What is reward hacking and how do you prevent it?</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline:</b>\n'
    '<br/><br/>\n'
    '<b>What it is:</b> The policy exploits imperfections in the reward model to achieve '
    'high reward without actually improving quality. Example: generating verbose, repetitive text '
    'that scores high on a length-biased reward model.\n'
    '<br/><br/>\n'
    '<b>Why it happens:</b> The reward model is a proxy for human preference, not a perfect measure. '
    'Any proxy metric can be gamed when optimized too aggressively (Goodhart\'s Law).\n'
    '<br/><br/>\n'
    '<b>Prevention strategies:</b>\n'
    '<br/>1. <b>KL penalty:</b> Constrain policy to stay close to reference model\n'
    '<br/>2. <b>Reward model ensemble:</b> Use multiple RMs and take the minimum/mean '
    'to reduce exploitable patterns\n'
    '<br/>3. <b>Iterative RLHF:</b> Periodically retrain RM on outputs from the current policy '
    '(captures new failure modes)\n'
    '<br/>4. <b>Constitutional AI:</b> Add rule-based constraints alongside learned rewards\n'
    '<br/>5. <b>DPO:</b> Implicitly constrains via the reference model in the loss -- '
    'less prone to extreme reward hacking\n'
    '<br/><br/>\n'
    '<b>Detection:</b> Monitor reward vs actual human preference correlation. '
    'If reward increases but human eval plateaus/drops, reward hacking is occurring.\n'
    '</div>\n'
    '</div>'
)

Q13_SYSTEM_DESIGN_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Q13: Design a text-to-image generation system at Adobe scale</div>\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">\n'
    '<b>Answer outline (structured approach):</b>\n'
    '<br/><br/>\n'
    '<b>Step 1: Clarify requirements</b>\n'
    '<br/>- Latency: P99 < 10s for 1024x1024 image\n'
    '<br/>- Throughput: 1000+ requests/sec globally\n'
    '<br/>- Quality: photorealistic, text-aligned, no artifacts\n'
    '<br/>- Safety: content filtering, copyright awareness\n'
    '<br/><br/>\n'
    '<b>Step 2: Model architecture</b>\n'
    '<br/>- Latent diffusion model (LDM) with VAE encoder/decoder\n'
    '<br/>- Text encoder: CLIP + T5-XXL for rich text understanding\n'
    '<br/>- U-Net / DiT (Diffusion Transformer) backbone\n'
    '<br/>- CFG guidance scale tuned per use case\n'
    '<br/><br/>\n'
    '<b>Step 3: Inference optimization</b>\n'
    '<br/>- FlashAttention in all attention layers\n'
    '<br/>- INT8/FP8 quantization for weights (AWQ for quality preservation)\n'
    '<br/>- Reduced sampling steps: DPM-Solver++ (20-25 steps vs 50)\n'
    '<br/>- KV-cache optimization for any autoregressive components\n'
    '<br/><br/>\n'
    '<b>Step 4: Serving architecture</b>\n'
    '<br/>- Continuous batching with dynamic batch sizing\n'
    '<br/>- Multi-tier GPU allocation: A100/H100 for generation, smaller GPUs for safety checks\n'
    '<br/>- Prefix caching for system prompt / style conditioning (RadixAttention)\n'
    '<br/>- CDN for caching popular prompt templates\n'
    '<br/><br/>\n'
    '<b>Step 5: Safety and quality</b>\n'
    '<br/>- Pre-generation: prompt classifier (reject harmful/copyright-infringing prompts)\n'
    '<br/>- Post-generation: NSFW classifier + watermarking (Content Credentials)\n'
    '<br/>- A/B testing framework for model quality comparison\n'
    '<br/><br/>\n'
    '<b>Step 6: Training pipeline</b>\n'
    '<br/>- FSDP on multi-node GPU cluster\n'
    '<br/>- Curated dataset with licensing metadata (Adobe Stock)\n'
    '<br/>- RLHF/DPO alignment for aesthetic quality and prompt faithfulness\n'
    '<br/>- Continuous training with human feedback loop\n'
    '</div>\n'
    '</div>'
)

# -- Speech Templates --
SPEECH_OPENING_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'TEMPLATE: Self-Introduction (30 seconds)\n'
    '\n'
    '"Hi, I\'m [name]. I\'m a machine learning engineer with experience in\n'
    '[model training/inference optimization/distributed systems]. Most recently,\n'
    'I worked on [brief project description -- 1 sentence]. I\'m excited about\n'
    'this role at Adobe because [specific reason tied to JD -- e.g., \'the\n'
    'intersection of generative AI and creative tools is exactly where I want\n'
    'to apply my skills in production ML systems\']."\n'
    '\n'
    'KEY RULES:\n'
    '- Under 30 seconds\n'
    '- Mention 1-2 relevant skills\n'
    '- Reference 1 specific Adobe product or technology\n'
    '- End with forward-looking enthusiasm, not a history lesson\n'
    '</pre>\n'
    '</div>'
)

SPEECH_UNKNOWN_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'TEMPLATE: When You Don\'t Know the Answer\n'
    '\n'
    'Option A -- Partial knowledge:\n'
    '"I\'m not deeply familiar with [specific topic], but here\'s what I understand:\n'
    '[share what you know]. My intuition is [educated guess based on fundamentals].\n'
    'I\'d want to verify this by [how you\'d look it up]."\n'
    '\n'
    'Option B -- Related knowledge:\n'
    '"I haven\'t worked directly with [topic], but I\'ve worked with [related topic]\n'
    'which shares [specific similarity]. Based on that experience, I\'d approach\n'
    'this by [apply transferable principles]."\n'
    '\n'
    'Option C -- Complete unknown:\n'
    '"That\'s outside my current experience. I\'d start by [first concrete step\n'
    'to learn it -- read the paper, set up a toy experiment, review documentation].\n'
    'In my experience learning [similar past technology], I was able to get\n'
    'productive within [timeframe]."\n'
    '\n'
    'KEY RULES:\n'
    '- Never bluff. Interviewers can tell.\n'
    '- Always share adjacent knowledge -- show your reasoning process.\n'
    '- End with a concrete learning plan, not "I\'d Google it."\n'
    '</pre>\n'
    '</div>'
)

SPEECH_STEERING_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'TEMPLATE: Redirecting to Strength Areas\n'
    '\n'
    'Bridge phrases:\n'
    '- "That reminds me of a related challenge I solved in [your strong area]..."\n'
    '- "The underlying principle there is [fundamental concept], which I applied\n'
    '   when I [specific experience]..."\n'
    '- "At a higher level, this is about [abstraction], and my experience\n'
    '   with [related project] taught me..."\n'
    '\n'
    'EXAMPLE:\n'
    'Interviewer: "How would you implement mixture-of-experts routing?"\n'
    'You (if unfamiliar with MoE specifics):\n'
    '"I haven\'t implemented MoE routing specifically, but the core challenge --\n'
    'dynamically routing computation to specialized sub-networks -- is similar\n'
    'to the cascading inference pipeline I built where a lightweight classifier\n'
    'routes inputs to the appropriate expert model. In my case, [describe your\n'
    'experience]. The MoE version would be similar but at the layer level rather\n'
    'than the model level, with the added challenge of load balancing across\n'
    'experts to prevent routing collapse."\n'
    '\n'
    'KEY RULES:\n'
    '- The bridge must be genuine -- don\'t force connections that aren\'t there\n'
    '- Acknowledge the gap before bridging\n'
    '- Show that you understand the PRINCIPLES even if you lack the specifics\n'
    '</pre>\n'
    '</div>'
)

SPEECH_QUESTIONS_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'PREPARED QUESTIONS FOR ADOBE:\n'
    '\n'
    'Technical depth:\n'
    '1. "What\'s the current inference stack for Firefly -- are you using\n'
    '    FlashAttention / quantization / speculative decoding in production?"\n'
    '2. "How do you handle the tradeoff between generation quality and latency\n'
    '    for real-time features vs batch processing?"\n'
    '\n'
    'Team and culture:\n'
    '3. "How does the ML team collaborate with the product/design teams\n'
    '    on new generative features?"\n'
    '4. "What does the model iteration cycle look like -- from research\n'
    '    prototype to production deployment?"\n'
    '\n'
    'Growth:\n'
    '5. "What are the biggest technical challenges the team is working\n'
    '    on in the next 6-12 months?"\n'
    '\n'
    'KEY RULES:\n'
    '- Ask max 2-3 questions (respect time)\n'
    '- Prefer questions that show you\'ve done research on Adobe\n'
    '- Avoid questions about salary, PTO, or benefits in technical rounds\n'
    '</pre>\n'
    '</div>'
)

# -- Error Correction Table --
ERROR_CORRECTION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Error Correction Quick-Reference</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:2px solid #555;">\n'
    '<th style="padding:8px 12px; text-align:left; width:30px;">#</th>\n'
    '<th style="padding:8px 12px; text-align:left;">Common Wrong Statement</th>\n'
    '<th style="padding:8px 12px; text-align:left;">Correct Understanding</th>\n'
    '<th style="padding:8px 12px; text-align:left;">Domain</th>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">1</td>\n'
    '<td style="padding:8px 12px;">"FlashAttention reduces FLOPs"</td>\n'
    '<td style="padding:8px 12px;">Same FLOPs (slightly more in backward). Speedup is from reduced HBM I/O, not compute.</td>\n'
    '<td style="padding:8px 12px;">Inference</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">2</td>\n'
    '<td style="padding:8px 12px;">"Speculative decoding changes the output"</td>\n'
    '<td style="padding:8px 12px;">Provably lossless via rejection sampling. Output distribution = target model exactly.</td>\n'
    '<td style="padding:8px 12px;">Inference</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">3</td>\n'
    '<td style="padding:8px 12px;">"DPO doesn\'t need a reference model"</td>\n'
    '<td style="padding:8px 12px;">DPO requires pi_ref (the SFT model) in its loss. It avoids a separate reward model, not a reference model.</td>\n'
    '<td style="padding:8px 12px;">Alignment</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">4</td>\n'
    '<td style="padding:8px 12px;">"DDPM and DDIM are different models"</td>\n'
    '<td style="padding:8px 12px;">Same trained model, different sampling procedures. DDIM reinterprets the reverse process as deterministic.</td>\n'
    '<td style="padding:8px 12px;">Diffusion</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">5</td>\n'
    '<td style="padding:8px 12px;">"Diffusion models generate from noise to image in one step"</td>\n'
    '<td style="padding:8px 12px;">Iterative denoising: T steps (10-1000). Each step removes a small amount of noise. Fast samplers reduce steps but still need multiple.</td>\n'
    '<td style="padding:8px 12px;">Diffusion</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">6</td>\n'
    '<td style="padding:8px 12px;">"Tensor parallelism = splitting data across GPUs"</td>\n'
    '<td style="padding:8px 12px;">TP splits model layers (weight matrices) across GPUs. Data parallelism splits data. They are orthogonal strategies.</td>\n'
    '<td style="padding:8px 12px;">Distributed</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">7</td>\n'
    '<td style="padding:8px 12px;">"RoPE is a learnable positional encoding"</td>\n'
    '<td style="padding:8px 12px;">RoPE is fixed (not learned). It applies rotation matrices based on position. The rotation angles are derived from a formula, not trained.</td>\n'
    '<td style="padding:8px 12px;">Architecture</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">8</td>\n'
    '<td style="padding:8px 12px;">"KV-cache is optional for efficiency"</td>\n'
    '<td style="padding:8px 12px;">Without KV-cache, generating N tokens costs O(N^2) total compute. It is essential, not optional. The question is how to manage it (PagedAttention, quantization).</td>\n'
    '<td style="padding:8px 12px;">Inference</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">9</td>\n'
    '<td style="padding:8px 12px;">"CFG just scales up the text embedding"</td>\n'
    '<td style="padding:8px 12px;">CFG extrapolates between unconditional and conditional noise predictions: eps_guided = eps_uncond + w*(eps_cond - eps_uncond). It operates on noise predictions, not embeddings.</td>\n'
    '<td style="padding:8px 12px;">Diffusion</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">10</td>\n'
    '<td style="padding:8px 12px;">"FSDP is just pipeline parallelism"</td>\n'
    '<td style="padding:8px 12px;">FSDP shards parameters/gradients/optimizer states across GPUs (like ZeRO-3). Each GPU still processes full forward/backward. PP assigns different layers to different GPUs.</td>\n'
    '<td style="padding:8px 12px;">Distributed</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)

# -- Quick Reference Card --
QUICK_REFERENCE_DIAGRAM = (
    '<pre style="background:#111; padding:12px; border-radius:4px; color:#ccc; font-size:13px;">\n'
    'STAR-T: Situation (15s) -> Task (15s) -> Approach (60s) -> Result (15s) -> Transfer (15s)\n'
    '    Total: ~2 min per story. Lead with punchline. Use "I" not "we".\n'
    '\n'
    '3 Stories:\n'
    '    1. Inference Pipeline: quantization + continuous batching + operator fusion -> 63% P99 reduction\n'
    '    2. Distributed Training: FSDP + mixed precision + gradient checkpointing -> 6.7x speedup (8 GPUs)\n'
    '    3. Data Quality + Alignment: DPO preference optimization -> +18% user satisfaction\n'
    '\n'
    '13 Questions by Domain:\n'
    '    Diffusion (Q1-4): DDPM forward/reverse, CFG, Latent Diffusion, DDPM vs DDIM\n'
    '    Inference (Q5-7): FlashAttention, Speculative Decoding, GPTQ vs AWQ\n'
    '    Distributed (Q8-10): DP/TP/PP comparison, FSDP vs DP, Debug slow training\n'
    '    Alignment (Q11-12): RLHF vs DPO tradeoffs, Reward hacking prevention\n'
    '    System Design (Q13): Text-to-image at scale (6-step framework)\n'
    '\n'
    'Speech Templates:\n'
    '    Opening: 30s max. Name + skill + project + Adobe enthusiasm.\n'
    '    Unknown: Share adjacent knowledge, never bluff, end with learning plan.\n'
    '    Steering: Bridge phrase -> acknowledge gap -> show principles -> redirect to strength.\n'
    '    Questions: 2-3 max. Show research. Avoid HR topics in tech rounds.\n'
    '\n'
    '10 Error Corrections:\n'
    '    FlashAttention: same FLOPs, fewer HBM trips (not fewer computations)\n'
    '    Speculative decoding: lossless (rejection sampling)\n'
    '    DPO: needs pi_ref (no reward model, but yes reference model)\n'
    '    DDIM: same model as DDPM (different sampler)\n'
    '    TP != DP: TP splits layers, DP splits data\n'
    '    RoPE: fixed (not learned)\n'
    '    FSDP != PP: FSDP shards params, PP assigns layers\n'
    '</pre>'
)


def build_day6_note() -> StudyNoteBuilder:
    """Build the Day 6 Mock Interview note using StudyNoteBuilder."""
    builder = StudyNoteBuilder()

    builder.set_title(
        "Mock Interview Questions + STAR-T Project Stories (Adobe Prep Day 6)"
    )

    # -- Prerequisites --
    builder.add_prerequisites([
        "Day 1: Diffusion Models Deep-Dive (DDPM, DDIM, CFG, Latent Diffusion)",
        "Day 2: RLHF/DPO Alignment + LLM Distillation (Bradley-Terry, PPO, DPO loss)",
        "Day 3: Distributed Training (DP, TP, PP, FSDP/ZeRO)",
        "Day 4: RoPE + Long Context + Video Generation (positional encoding, NTK-aware scaling)",
        "Day 5: Inference Optimization (FlashAttention, quantization, KV-cache, speculative decoding)",
    ])

    # -- Term Registry --
    builder.add_term("STAR-T", "Situation-Task-Approach-Result-Transfer",
                     "Extended STAR framework with Transfer step to bridge experience to target role")
    builder.add_term("DDPM", "Denoising Diffusion Probabilistic Model",
                     "Generates data by learning to reverse a noise process")
    builder.add_term("DDIM", "Denoising Diffusion Implicit Model",
                     "Deterministic sampler for diffusion models, enables fast generation")
    builder.add_term("CFG", "Classifier-Free Guidance",
                     "Steers diffusion generation toward a condition without a separate classifier")
    builder.add_term("LDM", "Latent Diffusion Model",
                     "Runs diffusion in a compressed latent space for efficiency")
    builder.add_term("FlashAttention", "IO-Aware Exact Attention",
                     "Tiled attention that avoids materializing N x N matrix in HBM")
    builder.add_term("GPTQ", "Generative Pre-trained Transformer Quantization",
                     "Post-training weight quantization using Hessian-based error compensation")
    builder.add_term("AWQ", "Activation-Aware Weight Quantization",
                     "Protects salient weight channels based on activation magnitudes")
    builder.add_term("FSDP", "Fully Sharded Data Parallelism",
                     "Shards parameters, gradients, and optimizer states across GPUs (ZeRO-3)")
    builder.add_term("DPO", "Direct Preference Optimization",
                     "Aligns models using preference pairs without a separate reward model")
    builder.add_term("RLHF", "Reinforcement Learning from Human Feedback",
                     "3-stage alignment: SFT -> Reward Model -> PPO policy optimization")
    builder.add_term("PPO", "Proximal Policy Optimization",
                     "RL algorithm used in RLHF to optimize policy with KL constraint")
    builder.add_term("KV-cache", "Key-Value Cache",
                     "Stores computed K/V tensors to avoid recomputation during autoregressive generation")
    builder.add_term("DiT", "Diffusion Transformer",
                     "Replaces U-Net with transformer backbone for diffusion models")

    # -- Section 1: STAR-T Framework --
    builder.add_section("1. STAR-T Framework", [
        "The STAR-T framework extends the classic STAR method with a **Transfer** step "
        "that bridges your experience to the target role. This is especially powerful "
        "when your past project context differs from the interviewer's domain.",
    ])
    builder.add_diagram_html(STAR_T_FRAMEWORK_DIAGRAM)

    builder.add_section("STAR-T Template (fill in for each story)", [])
    builder.add_diagram_html(STAR_T_TEMPLATE_DIAGRAM)

    builder.add_section("Tips for STAR-T Delivery", [
        "- **Lead with the punchline:** Start with the result if the question asks "
        '"tell me about a time you improved X"',
        '- **Be specific:** "Reduced latency by 40%" beats "significantly improved performance"',
        '- **Own your decisions:** Use "I" not "we" for your specific contributions',
        "- **Prepare follow-ups:** For each story, anticipate 2-3 drill-down questions",
        "- **Practice the Transfer:** The bridge to Adobe should feel natural, not forced",
    ])

    # -- Section 2: Project Story Outlines --
    builder.add_section("2. Project Story Outlines (Mapped to Adobe JD)", [
        "Three prepared stories covering inference, distributed training, and alignment -- "
        "the core competencies in the Adobe MLE job description.",
    ])

    builder.add_section("Story 1: Model Serving Optimization (Inference Pipeline)", [])
    builder.add_diagram_html(STORY1_DIAGRAM)
    builder.add_section("Story 1 -- Alignment & Drill-Downs", [
        "**Adobe JD alignment:** Model deployment, inference optimization, serving at scale",
        "",
        "**Drill-down questions to prepare:**",
        "- How did you choose between INT4 and INT8 quantization?",
        "- How did you measure accuracy degradation after quantization?",
        "- What would you do differently at 10x the current scale?",
    ])

    builder.add_section("Story 2: Distributed Training System", [])
    builder.add_diagram_html(STORY2_DIAGRAM)
    builder.add_section("Story 2 -- Alignment & Drill-Downs", [
        "**Adobe JD alignment:** Large-scale training, distributed systems, GPU optimization",
        "",
        "**Drill-down questions to prepare:**",
        "- Why FSDP over DeepSpeed ZeRO? What are the tradeoffs?",
        "- How did you debug the gap between 84% and 100% scaling efficiency?",
        "- How would you add tensor parallelism for an even larger model?",
    ])

    builder.add_section("Story 3: Data Pipeline + Model Quality Improvement", [])
    builder.add_diagram_html(STORY3_DIAGRAM)
    builder.add_section("Story 3 -- Alignment & Drill-Downs", [
        "**Adobe JD alignment:** RLHF/DPO, model quality, user-centric ML, data pipeline",
        "",
        "**Drill-down questions to prepare:**",
        "- How did you ensure annotation quality and inter-annotator agreement?",
        "- When would you choose RLHF over DPO?",
        "- How do you detect reward hacking or mode collapse?",
    ])

    # -- Section 3: High-Frequency Interview Questions --
    builder.add_section("3. High-Frequency Interview Questions (13 Questions)", [
        "Structured answer outlines for the most commonly asked technical questions, "
        "organized by domain. Each answer is designed for 60-90 second verbal delivery. "
        "Cross-references: Q1-Q4 -> Day 1, Q5-Q7 -> Day 5, Q8-Q10 -> Day 3, Q11-Q12 -> Day 2.",
    ])

    builder.add_section("Diffusion Models (Q1-Q4)", [])
    builder.add_diagram_html(Q1_DDPM_DIAGRAM)

    # Q1 formulas
    builder.add_section("Q1 Key Formulas", [
        FormulaBlock(
            latex=r"q(x_t \mid x_{t-1}) = \mathcal{N}(x_t;\, \sqrt{1-\beta_t}\, x_{t-1},\, \beta_t \mathbf{I})",
            explanation="Forward step -- adding noise:",
        ),
        FormulaBlock(
            latex=r"x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1-\bar\alpha_t}\, \epsilon, \quad \epsilon \sim \mathcal{N}(0, \mathbf{I})",
            explanation="Closed-form jump to any timestep:",
        ),
        FormulaBlock(
            latex=r"\mathcal{L} = \mathbb{E}\bigl[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\bigr]",
            explanation="Simplified training loss:",
        ),
    ])

    builder.add_diagram_html(Q2_CFG_DIAGRAM)

    # Q2 formula
    builder.add_section("Q2 Key Formula", [
        FormulaBlock(
            latex=r"\epsilon_{\text{guided}} = \epsilon_{\text{uncond}} + w \cdot (\epsilon_{\text{cond}} - \epsilon_{\text{uncond}})",
            explanation="CFG guidance equation (w > 1 amplifies condition signal):",
        ),
    ])

    builder.add_diagram_html(Q3_LATENT_DIFFUSION_DIAGRAM)
    builder.add_diagram_html(Q4_DDPM_VS_DDIM_DIAGRAM)

    builder.add_section("Inference Optimization (Q5-Q7)", [])
    builder.add_diagram_html(Q5_FLASH_ATTENTION_DIAGRAM)

    # Q5 formula
    builder.add_section("Q5 Key Formula", [
        FormulaBlock(
            latex=r"\text{IO}_{\text{flash}} = O\!\left(\frac{N^2 d^2}{M}\right) \quad\text{vs}\quad \text{IO}_{\text{standard}} = O(N^2 d + N^2)",
            explanation="IO complexity comparison (M = SRAM size):",
        ),
    ])

    builder.add_diagram_html(Q6_SPECULATIVE_DECODING_DIAGRAM)

    # Q6 formula
    builder.add_section("Q6 Key Formulas", [
        FormulaBlock(
            latex=r"P(\text{accept token}_i) = \min\!\left(1,\, \frac{P_{\text{target}}(x)}{P_{\text{draft}}(x)}\right)",
            explanation="Acceptance probability (rejection sampling):",
        ),
        FormulaBlock(
            latex=r"P_{\text{resample}} = \text{norm}\bigl(\max(0,\, P_{\text{target}}(x) - P_{\text{draft}}(x))\bigr)",
            explanation="Correction distribution for rejected tokens:",
        ),
    ])

    builder.add_diagram_html(Q7_GPTQ_AWQ_DIAGRAM)

    builder.add_section("Distributed Training (Q8-Q10)", [])
    builder.add_diagram_html(Q8_DP_TP_PP_DIAGRAM)

    # Q8 formula
    builder.add_section("Q8 Key Formula", [
        FormulaBlock(
            latex=r"\text{PP bubble} = \frac{P - 1}{P - 1 + M}",
            explanation="Pipeline parallelism bubble overhead (P = stages, M = micro-batches):",
        ),
    ])

    builder.add_diagram_html(Q9_FSDP_DIAGRAM)

    # Q9 formula
    builder.add_section("Q9 Key Formula", [
        FormulaBlock(
            latex=r"\text{FSDP memory/GPU} = \frac{2 + 2 + 8}{N} = \frac{12}{N}\;\text{bytes/param}",
            explanation="ZeRO Stage 3 / FSDP memory per GPU (N = number of GPUs):",
        ),
    ])

    builder.add_diagram_html(Q10_DEBUG_DISTRIBUTED_DIAGRAM)

    builder.add_section("Alignment (Q11-Q12)", [])
    builder.add_diagram_html(Q11_RLHF_VS_DPO_DIAGRAM)

    # Q11 formulas
    builder.add_section("Q11 Key Formulas", [
        FormulaBlock(
            latex=r"P(y_w \succ y_l) = \sigma\bigl(r(y_w) - r(y_l)\bigr)",
            explanation="Bradley-Terry preference model:",
        ),
        FormulaBlock(
            latex=r"J_{\text{RLHF}} = \mathbb{E}\bigl[r(y)\bigr] - \beta \cdot \text{KL}(\pi \| \pi_{\text{ref}})",
            explanation="RLHF objective (reward minus KL penalty):",
        ),
        FormulaBlock(
            latex=r"\mathcal{L}_{\text{DPO}} = -\mathbb{E}\!\left[\log \sigma\!\left(\beta \log \frac{\pi(y_w)}{\pi_{\text{ref}}(y_w)} - \beta \log \frac{\pi(y_l)}{\pi_{\text{ref}}(y_l)}\right)\right]",
            explanation="DPO loss (directly optimizes policy without reward model):",
        ),
    ])

    builder.add_diagram_html(Q12_REWARD_HACKING_DIAGRAM)

    # Q12 formula
    builder.add_section("Q12 Key Formula", [
        FormulaBlock(
            latex=r"J = r(y) - \beta \cdot \text{KL}(\pi \| \pi_{\text{ref}})",
            explanation="KL-constrained objective to prevent reward hacking (higher beta = more conservative):",
        ),
    ])

    builder.add_section("System Design (Q13)", [])
    builder.add_diagram_html(Q13_SYSTEM_DESIGN_DIAGRAM)

    # -- Section 4: Interview Speech Templates --
    builder.add_section("4. Interview Speech Templates", [
        "Prepared verbal templates for common interview situations. "
        "Practice each template out loud until delivery feels natural.",
    ])

    builder.add_section("Opening (First 30 seconds)", [])
    builder.add_diagram_html(SPEECH_OPENING_DIAGRAM)

    builder.add_section("Handling Unknown Questions", [])
    builder.add_diagram_html(SPEECH_UNKNOWN_DIAGRAM)

    builder.add_section("Steering to Your Strengths", [])
    builder.add_diagram_html(SPEECH_STEERING_DIAGRAM)

    builder.add_section("Asking Good Questions (End of Interview)", [])
    builder.add_diagram_html(SPEECH_QUESTIONS_DIAGRAM)

    # -- Section 5: Error Correction Quick-Reference --
    builder.add_section("5. Common Error Correction Quick-Reference Card", [
        "Cross-domain error corrections covering Days 1-5. Review these before each "
        "mock interview to avoid common misconceptions that interviewers test for.",
    ])
    builder.add_diagram_html(ERROR_CORRECTION_DIAGRAM)

    # -- Self-Check Questions --
    builder.add_checklist("Self-Check Questions", [
        "Walk through the STAR-T framework. Give a 2-minute version of Story 1 "
        "(inference optimization) out loud. (Cross-ref: Day 5 inference concepts)",
        "An interviewer asks \"Explain FlashAttention.\" Deliver a 90-second answer "
        "without looking at notes. (Cross-ref: Day 5 FlashAttention section)",
        'An interviewer asks about a topic you don\'t know (e.g., "How does '
        'mixture-of-experts routing work?"). Practice the bridge-to-strength technique.',
        "Explain the DPO vs RLHF tradeoff. Include the math (Bradley-Terry, DPO loss). "
        "Under 2 minutes. (Cross-ref: Day 2 alignment section)",
        "Design a text-to-image system for Adobe. Cover all 6 steps of the system design "
        "outline in 5 minutes. (Cross-ref: Day 1 diffusion, Day 3 FSDP, Day 5 inference)",
    ])

    # -- Quick Reference Card --
    builder.add_section("Quick Reference Card", [])
    builder.add_diagram_html(QUICK_REFERENCE_DIAGRAM)

    return builder


def main() -> None:
    """Build and save Day 6 note to database."""
    import sqlite3

    db_path = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
    if not db_path.exists():
        print(f"[FAIL] Database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))

    # Check Adobe exists
    row = conn.execute(
        "SELECT id FROM companies WHERE id = ?", (COMPANY_ID,)
    ).fetchone()
    if not row:
        print(f"[FAIL] Company id={COMPANY_ID} not found in DB")
        conn.close()
        sys.exit(1)

    # Delete old version if present (idempotent rewrite)
    old = conn.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    ).fetchone()
    if old:
        conn.execute("DELETE FROM company_documents WHERE id = ?", (old[0],))
        conn.commit()
        print(f"[INFO] Deleted old document id={old[0]}: {DOC_TITLE}")

    # Build and insert new version
    builder = build_day6_note()
    content = builder.build()

    conn.execute(
        "INSERT INTO company_documents (company_id, title, content, source_type) "
        "VALUES (?, ?, ?, ?)",
        (COMPANY_ID, DOC_TITLE, content, "manual"),
    )
    conn.commit()

    # Verify
    doc = conn.execute(
        "SELECT id, length(content) FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    ).fetchone()
    print(
        f"[DONE] Inserted document id={doc[0]}, "
        f"title='{DOC_TITLE}', content_length={doc[1]} chars"
    )

    # Validate
    warnings = StudyNoteBuilder.validate(content)
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")
    else:
        print("[DONE] 0 validation warnings")

    conn.close()


if __name__ == "__main__":
    main()
