"""Seed script: Insert Adobe Prep Day6 -- Mock Interview Questions + STAR-T Stories note.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day6: Mock Interview Questions + STAR-T Project Stories"

CONTENT = r"""# Mock Interview Questions + STAR-T Project Stories (Adobe Prep Day 6)

> This note prepares you for the behavioral and technical interview rounds.
> It provides the STAR-T storytelling framework, 3 project story outlines
> mapped to Adobe's JD, 13 high-frequency technical questions with structured
> answer outlines, interview speech templates, and a common error correction
> quick-reference card.

---

## 1. STAR-T Framework

The STAR-T framework extends the classic STAR method with a **Transfer** step
that bridges your experience to the target role. This is especially powerful
when your past project context differs from the interviewer's domain.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">STAR-T Framework</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Letter</th>
<th style="padding:8px 16px; text-align:left;">Component</th>
<th style="padding:8px 16px; text-align:left;">What to Include</th>
<th style="padding:8px 16px; text-align:left;">Time</th>
</tr>
<tr style="background:#4a90d9; color:white;">
<td style="padding:8px 16px;"><b>S</b></td>
<td style="padding:8px 16px;">Situation</td>
<td style="padding:8px 16px;">Team, product, scale, constraint. Set the stage in 1-2 sentences.</td>
<td style="padding:8px 16px;">~15s</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;"><b>T</b></td>
<td style="padding:8px 16px;">Task</td>
<td style="padding:8px 16px;">Your specific responsibility. What was the problem you owned?</td>
<td style="padding:8px 16px;">~15s</td>
</tr>
<tr style="background:#2d6a4f; color:white;">
<td style="padding:8px 16px;"><b>A</b></td>
<td style="padding:8px 16px;">Approach</td>
<td style="padding:8px 16px;">Technical decisions, tradeoffs, alternatives considered. This is the core -- show depth.</td>
<td style="padding:8px 16px;">~60s</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;"><b>R</b></td>
<td style="padding:8px 16px;">Result</td>
<td style="padding:8px 16px;">Quantified impact: latency, throughput, accuracy, cost. Use concrete numbers.</td>
<td style="padding:8px 16px;">~15s</td>
</tr>
<tr style="background:#8b5cf6; color:white;">
<td style="padding:8px 16px;"><b>T</b></td>
<td style="padding:8px 16px;">Transfer</td>
<td style="padding:8px 16px;">Bridge to Adobe: "At Adobe's scale with Firefly / Document Cloud / Creative Cloud, I would apply this by..."</td>
<td style="padding:8px 16px;">~15s</td>
</tr>
</table>
<div style="margin-top:12px; color:#ccc; font-size:12px;">
Total: ~2 minutes per story. Practice to stay under 2.5 min.
</div>
</div>
</div>

### STAR-T Template (fill in for each story)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<pre style="color:#ccc; font-size:13px;">
STORY TEMPLATE:

[S] "On the ___ team at ___, we were building ___ that served ___ users/requests.
     The main constraint was ___."

[T] "I was responsible for ___. The specific challenge was ___."

[A] "I chose to ___ because ___. I considered ___ as an alternative, but ___.
     The key technical insight was ___. I implemented ___ which involved ___."

[R] "This resulted in ___ (metric improvement). Specifically: ___% improvement
     in ___, reducing ___ from ___ to ___."

[T] "At Adobe, this directly applies to ___ because ___. For example, in
     Firefly's ___ pipeline, the same approach would ___."
</pre>
</div>

### Tips for STAR-T Delivery

- **Lead with the punchline:** Start with the result if the question asks "tell me about a time you improved X"
- **Be specific:** "Reduced latency by 40%" beats "significantly improved performance"
- **Own your decisions:** Use "I" not "we" for your specific contributions
- **Prepare follow-ups:** For each story, anticipate 2-3 drill-down questions
- **Practice the Transfer:** The bridge to Adobe should feel natural, not forced

---

## 2. Project Story Outlines (Mapped to Adobe JD)

### Story 1: Model Serving Optimization (Inference Pipeline)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Story 1: Inference Pipeline Optimization</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
[S] ML team serving a production model with growing request volume.
    Latency SLA: P99 < 200ms. Current P99: ~450ms under peak load.

[T] Owned end-to-end inference optimization. Needed to hit SLA without
    adding GPU capacity (cost constraint).

[A] Profiled the pipeline end-to-end:
    - Identified KV-cache memory fragmentation as primary bottleneck
    - Implemented operator fusion to reduce HBM round-trips
      (analogous to FlashAttention's tiling approach)
    - Applied INT8 weight quantization with per-channel scaling
      (SmoothQuant-inspired activation migration)
    - Redesigned batching: moved from static to iteration-level
      scheduling (continuous batching pattern)
    - Considered INT4 quantization but accuracy regression on
      edge cases was >2% -- chose INT8 as the Pareto-optimal point

[R] P99 latency: 450ms -> 165ms (63% reduction)
    Throughput: 2.4x improvement without additional GPUs
    Model accuracy: <0.3% degradation (within tolerance)

[T] At Adobe, Firefly serves millions of image generation requests.
    The same profiling-first, quantize-smartly, batch-efficiently
    approach directly applies to their diffusion model serving stack.
</pre>
</div>
</div>
</div>

**Adobe JD alignment:** Model deployment, inference optimization, serving at scale

**Drill-down questions to prepare:**
- How did you choose between INT4 and INT8 quantization?
- How did you measure accuracy degradation after quantization?
- What would you do differently at 10x the current scale?

### Story 2: Distributed Training System

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Story 2: Distributed Training</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
[S] Training a large model that did not fit on a single GPU.
    Team of 3 engineers, 8-GPU cluster available.

[T] Designed and implemented the distributed training strategy.
    Goal: linear scaling efficiency while maintaining convergence.

[A] Analyzed model size vs memory:
    - Model params + optimizer states exceeded single GPU memory
    - Implemented FSDP (Fully Sharded Data Parallelism) for memory
      efficiency: shard params, gradients, AND optimizer states
    - Used mixed-precision training (bf16 forward/backward, fp32
      master weights) to halve activation memory
    - Applied gradient checkpointing on transformer blocks to trade
      compute for memory (recompute activations in backward pass)
    - Tuned: all-reduce bucket size, gradient accumulation steps,
      learning rate warmup schedule for multi-GPU stability

    Considered alternatives:
    - Pure DP: OOM on single GPU (model too large)
    - Pipeline parallelism: uneven stage splitting caused bubbles
    - FSDP won: memory-efficient + near-linear scaling

[R] Training time: 14 days -> 2.1 days (6.7x speedup on 8 GPUs)
    Scaling efficiency: 84% (vs theoretical 100% linear)
    Memory per GPU: reduced from OOM to 68% utilization

[T] Adobe trains foundation models for Firefly and document AI.
    FSDP + mixed precision is exactly their stack. My experience
    debugging communication overhead and tuning sharding strategies
    translates directly.
</pre>
</div>
</div>
</div>

**Adobe JD alignment:** Large-scale training, distributed systems, GPU optimization

**Drill-down questions to prepare:**
- Why FSDP over DeepSpeed ZeRO? What are the tradeoffs?
- How did you debug the gap between 84% and 100% scaling efficiency?
- How would you add tensor parallelism for an even larger model?

### Story 3: Data Pipeline + Model Quality Improvement

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Story 3: Data Quality + Alignment</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
[S] Production model generating outputs that were technically correct
    but misaligned with user intent. User satisfaction scores declining.
    Feedback data was available but not being leveraged.

[T] Led the effort to incorporate human feedback into the model
    improvement loop. Owned data pipeline + training changes.

[A] Built a three-stage improvement pipeline:
    1. Data collection: designed annotation interface, collected
       preference pairs (chosen vs rejected outputs)
    2. Reward model: trained a reward model on preference data
       to score output quality (Bradley-Terry preference model)
    3. Alignment: applied DPO (Direct Preference Optimization)
       rather than full RLHF -- simpler, no separate RL loop
       - DPO loss: directly optimizes policy using preference pairs
       - Avoided PPO instability and reward hacking issues
    4. Evaluation: built automated eval pipeline with human-in-loop
       validation on edge cases

    Key decision: DPO over RLHF
    - RLHF requires reward model + PPO training loop (complex)
    - DPO achieves comparable quality with single supervised step
    - Trade-off: DPO is less flexible for iterative reward shaping

[R] User satisfaction: +18% (measured via A/B test, n=5000)
    Output quality score (reward model): 0.72 -> 0.89
    Training cost: 3x cheaper than equivalent RLHF pipeline

[T] Adobe's generative AI products (Firefly, Acrobat AI) need
    alignment with creative intent and brand safety. My experience
    building preference-based alignment pipelines directly applies
    to their content generation quality loop.
</pre>
</div>
</div>
</div>

**Adobe JD alignment:** RLHF/DPO, model quality, user-centric ML, data pipeline

**Drill-down questions to prepare:**
- How did you ensure annotation quality and inter-annotator agreement?
- When would you choose RLHF over DPO?
- How do you detect reward hacking or mode collapse?

---

## 3. High-Frequency Interview Questions (13 Questions)

### Diffusion Models (Q1-Q4)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q1: Explain the forward and reverse process of DDPM</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>Forward process (diffusion):</b>
<br/>- Gradually add Gaussian noise over T steps: q(x_t | x_{t-1}) = N(x_t; sqrt(1-beta_t) * x_{t-1}, beta_t * I)
<br/>- Closed-form jump: x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
<br/>- After T steps (~1000), x_T is approximately pure Gaussian noise
<br/><br/>
<b>Reverse process (denoising):</b>
<br/>- Learn p_theta(x_{t-1} | x_t) = N(x_{t-1}; mu_theta(x_t, t), sigma_t^2 * I)
<br/>- Neural network predicts the noise epsilon_theta(x_t, t)
<br/>- Simplified loss: L = E[||epsilon - epsilon_theta(x_t, t)||^2]
<br/>- Generate by sampling x_T ~ N(0,I) then iteratively denoising
<br/><br/>
<b>Key point:</b> The forward process has no learnable parameters. All learning is in the reverse process (the denoiser network).
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q2: What is classifier-free guidance (CFG) and why is it used?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>Problem:</b> Unconditional diffusion models generate diverse but often low-quality/irrelevant outputs.
<br/><br/>
<b>Classifier guidance:</b> Use gradient of a separate classifier p(y|x_t) to steer generation. Problem: requires a trained classifier that works on noisy inputs.
<br/><br/>
<b>Classifier-free guidance (CFG):</b>
<br/>- Train ONE model with conditional and unconditional denoising (randomly drop condition during training)
<br/>- At inference: epsilon_guided = epsilon_uncond + w * (epsilon_cond - epsilon_uncond)
<br/>- w > 1 amplifies the condition signal. Typical w = 7.5 for text-to-image.
<br/><br/>
<b>Tradeoff:</b> Higher w = better text alignment but lower diversity and potential artifacts. w = 1 = no guidance. w too high = oversaturated/distorted images.
<br/><br/>
<b>Why it matters at Adobe:</b> Firefly uses CFG to ensure generated images match text prompts while maintaining visual quality.
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q3: How does Latent Diffusion (Stable Diffusion) differ from pixel-space diffusion?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>Pixel-space diffusion:</b> Operates on full-resolution images (e.g., 512x512x3). Very expensive -- O(H*W) per step.
<br/><br/>
<b>Latent diffusion:</b>
<br/>- Step 1: Train a VAE to encode images to a compact latent space (e.g., 64x64x4) -- 8x spatial compression
<br/>- Step 2: Run the diffusion process in latent space
<br/>- Step 3: Decode latent back to pixel space via VAE decoder
<br/><br/>
<b>Benefits:</b>
<br/>- 64x fewer pixels to denoise (64x64 vs 512x512)
<br/>- Training is ~10x faster
<br/>- Inference is ~10x faster
<br/>- Latent space captures semantic structure, improving generation quality
<br/><br/>
<b>Conditioning:</b> Cross-attention between latent features and text embeddings (CLIP/T5).
<br/><br/>
<b>Key point:</b> The VAE is trained separately and frozen during diffusion training. Perceptual quality depends on VAE quality.
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q4: Compare DDPM vs DDIM sampling. When would you use each?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>DDPM sampling:</b>
<br/>- Stochastic: adds noise at each reverse step
<br/>- Requires all T steps (typically T=1000) for good quality
<br/>- Slow but high diversity
<br/><br/>
<b>DDIM sampling:</b>
<br/>- Deterministic: removes the noise injection in reverse steps
<br/>- Can skip steps (e.g., 50 steps instead of 1000) with minimal quality loss
<br/>- Same trained model -- DDIM is just a different sampling schedule
<br/>- Enables interpolation in latent space (deterministic mapping x_T -> x_0)
<br/><br/>
<b>When to use:</b>
<br/>- DDPM: when diversity matters and compute budget allows (creative exploration)
<br/>- DDIM: production serving (fast), image editing (deterministic inversion), interpolation
<br/><br/>
<b>Modern samplers:</b> DPM-Solver, DPM-Solver++ achieve good quality in 10-25 steps by treating the diffusion ODE more carefully.
</div>
</div>

### Inference Optimization (Q5-Q7)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q5: Explain FlashAttention. Why is it faster without reducing FLOPs?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>Problem:</b> Standard attention materializes the N x N attention matrix in HBM. The bottleneck is memory I/O, not compute.
<br/><br/>
<b>FlashAttention solution:</b>
<br/>- Tile the computation: process Q, K, V in blocks that fit in SRAM (~20MB on A100)
<br/>- Never write the full N x N matrix to HBM
<br/>- Use the "online softmax" trick to maintain running max and sum across tiles
<br/><br/>
<b>IO complexity:</b> O(N^2 d^2 / M) vs standard O(N^2 d + N^2), where M = SRAM size
<br/><br/>
<b>Result:</b> Same FLOPs (slightly more due to recomputation in backward), but 2-4x wall-clock speedup on A100 because HBM access is the bottleneck (2 TB/s) vs SRAM (19 TB/s).
<br/><br/>
<b>Common misconception to preempt:</b> "FlashAttention is faster because it does less computation." No -- it does the same computation but minimizes expensive HBM reads/writes.
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q6: How does speculative decoding work? Prove it is lossless.</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>Mechanism:</b>
<br/>1. Draft model generates K candidate tokens autoregressively (fast, small model)
<br/>2. Target model verifies all K tokens in one forward pass (parallel)
<br/>3. For each token i: if P_target(token_i) >= P_draft(token_i), accept
<br/>4. If token i is rejected: resample from adjusted distribution, discard tokens i+1..K
<br/>5. Always generate at least 1 token (the resampled one)
<br/><br/>
<b>Why lossless:</b>
<br/>- Rejection sampling guarantees: the accepted tokens follow P_target exactly
<br/>- Accepted with probability min(1, P_target(x) / P_draft(x))
<br/>- Rejected tokens are resampled from: norm(max(0, P_target(x) - P_draft(x)))
<br/>- This is the standard rejection sampling correction -- mathematically, the output distribution equals P_target
<br/><br/>
<b>Speedup:</b> ~K * acceptance_rate tokens per target forward pass. Typical: 2-3x with K=5, 70-80% acceptance.
<br/><br/>
<b>Draft model choices:</b> Smaller version of target, quantized target, n-gram model, or Medusa-style parallel heads.
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q7: Compare GPTQ vs AWQ. When would you choose each?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>GPTQ:</b>
<br/>- Based on Optimal Brain Surgeon (OBS)
<br/>- Quantizes weights column-by-column, compensating error in remaining columns using Hessian
<br/>- Requires calibration data (~128 samples) for Hessian computation
<br/>- Strong theoretical foundation (minimizes layer-wise output error)
<br/>- Slower to quantize (sequential column processing)
<br/><br/>
<b>AWQ:</b>
<br/>- Observes: ~1% of weight channels are "salient" (correspond to large activations)
<br/>- Applies per-channel scaling to protect salient channels before quantization
<br/>- Scaling factor absorbed into previous layer (zero runtime overhead)
<br/>- Faster quantization, often better quality at INT4
<br/><br/>
<b>When to choose:</b>
<br/>- GPTQ: when you need maximum quality and calibration data is available, or for very small models where every bit matters
<br/>- AWQ: for production deployment where quantization speed matters, and for larger models (>13B) where it typically wins
<br/>- Both: INT4 weight-only, post-training, compatible with vLLM/TensorRT-LLM
</div>
</div>

### Distributed Training (Q8-Q10)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q8: Compare Data Parallelism, Tensor Parallelism, and Pipeline Parallelism</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>Data Parallelism (DP):</b>
<br/>- Each GPU holds a full model copy, processes different data batches
<br/>- Synchronize gradients via all-reduce after backward pass
<br/>- Simple but requires model to fit on one GPU
<br/>- Communication: gradient all-reduce O(params) per step
<br/><br/>
<b>Tensor Parallelism (TP):</b>
<br/>- Split individual layers (e.g., attention heads, MLP columns) across GPUs
<br/>- Each GPU computes part of each layer, then all-reduce activations
<br/>- Requires high-bandwidth interconnect (NVLink) -- within a node only
<br/>- Communication: activation all-reduce at every layer
<br/><br/>
<b>Pipeline Parallelism (PP):</b>
<br/>- Assign different layers to different GPUs (stage 0: layers 0-15, stage 1: layers 16-31)
<br/>- Micro-batching to reduce bubble time (idle GPU time between stages)
<br/>- Communication: activation tensors between stages (point-to-point)
<br/>- Bubble overhead: ~(P-1)/(P-1+M) where P=stages, M=micro-batches
<br/><br/>
<b>Combining them (3D parallelism):</b> TP within nodes (fast NVLink), PP across nodes (slower network), DP across node groups.
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q9: What is FSDP and how does it differ from standard DP?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>Standard DP memory usage per GPU:</b>
<br/>- Full model parameters (e.g., 2 bytes/param in fp16)
<br/>- Full gradients (2 bytes/param)
<br/>- Full optimizer states (8 bytes/param for Adam: momentum + variance + fp32 copy)
<br/>- Total: ~12 bytes/param per GPU (all redundant copies!)
<br/><br/>
<b>FSDP (Fully Sharded Data Parallelism) / ZeRO:</b>
<br/>- ZeRO Stage 1: Shard optimizer states only -> 4 + 8/N bytes/param
<br/>- ZeRO Stage 2: Shard optimizer states + gradients -> 2 + (2+8)/N bytes/param
<br/>- ZeRO Stage 3 / FSDP: Shard everything (params + gradients + optimizer) -> (2+2+8)/N bytes/param
<br/>- All-gather params before forward/backward, reduce-scatter gradients after
<br/><br/>
<b>Tradeoff:</b> FSDP uses ~N times less memory but adds communication overhead (all-gather at each layer). Works well when communication bandwidth is high (intra-node NVLink).
<br/><br/>
<b>Practical tip:</b> FSDP with mixed precision (bf16 compute, fp32 master weights) is the default for training models 7B-70B on typical clusters.
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q10: How do you debug slow distributed training?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline (systematic approach):</b>
<br/><br/>
<b>Step 1: Profile</b>
<br/>- Use PyTorch Profiler or NVIDIA Nsight to get per-operation breakdown
<br/>- Identify: is bottleneck compute, communication, or memory (OOM -> swapping)?
<br/><br/>
<b>Step 2: Check communication</b>
<br/>- Measure all-reduce time vs compute time ratio
<br/>- If communication-bound: increase compute-to-communication ratio (larger batch, gradient accumulation)
<br/>- Check NCCL topology: is NVLink being used? Or falling back to PCIe?
<br/><br/>
<b>Step 3: Check GPU utilization</b>
<br/>- nvidia-smi: are all GPUs at ~100% utilization?
<br/>- Uneven utilization = load imbalance (PP bubble, uneven data distribution)
<br/><br/>
<b>Step 4: Check memory</b>
<br/>- Activation memory: apply gradient checkpointing (selective, not full)
<br/>- Optimizer memory: switch to FSDP if using standard DP
<br/><br/>
<b>Common fixes:</b>
<br/>- Overlap communication with computation (async all-reduce)
<br/>- Tune all-reduce bucket size (PyTorch default may not be optimal)
<br/>- Use bf16 mixed precision if not already
<br/>- Increase gradient accumulation steps to amortize communication
</div>
</div>

### Alignment (Q11-Q12)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q11: Compare RLHF vs DPO. What are the tradeoffs?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>RLHF (3 stages):</b>
<br/>1. SFT: Fine-tune base model on high-quality demonstrations
<br/>2. Reward Model: Train RM on preference pairs using Bradley-Terry model
<br/>   - P(y_w > y_l) = sigma(r(y_w) - r(y_l))
<br/>3. PPO: Optimize policy to maximize reward while staying close to SFT model (KL penalty)
<br/>   - J = E[r(y)] - beta * KL(pi || pi_ref)
<br/><br/>
<b>DPO (1 stage after SFT):</b>
<br/>- Key insight: the optimal policy under RLHF objective has a closed-form relationship with the reward
<br/>- r(y) = beta * log(pi(y)/pi_ref(y)) + const
<br/>- Substitute into Bradley-Terry -> DPO loss that directly optimizes the policy
<br/>- L_DPO = -E[log sigma(beta * log(pi(y_w)/pi_ref(y_w)) - beta * log(pi(y_l)/pi_ref(y_l)))]
<br/>- No separate reward model, no RL training loop
<br/><br/>
<b>Tradeoffs:</b>
<br/>- RLHF: more flexible (reward model can be used for other purposes, iterative refinement), but unstable (PPO tuning, reward hacking)
<br/>- DPO: simpler, more stable, cheaper compute, but less flexible (no explicit reward signal for analysis)
<br/>- DPO may underperform RLHF on tasks requiring very precise reward shaping
</div>
</div>

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q12: What is reward hacking and how do you prevent it?</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline:</b>
<br/><br/>
<b>What it is:</b> The policy exploits imperfections in the reward model to achieve high reward without actually improving quality. Example: generating verbose, repetitive text that scores high on a length-biased reward model.
<br/><br/>
<b>Why it happens:</b> The reward model is a proxy for human preference, not a perfect measure. Any proxy metric can be gamed when optimized too aggressively (Goodhart's Law).
<br/><br/>
<b>Prevention strategies:</b>
<br/>1. <b>KL penalty:</b> Constrain policy to stay close to reference model: J = r(y) - beta * KL(pi || pi_ref). Higher beta = more conservative.
<br/>2. <b>Reward model ensemble:</b> Use multiple RMs and take the minimum/mean to reduce exploitable patterns
<br/>3. <b>Iterative RLHF:</b> Periodically retrain RM on outputs from the current policy (captures new failure modes)
<br/>4. <b>Constitutional AI:</b> Add rule-based constraints (e.g., safety guidelines) alongside learned rewards
<br/>5. <b>DPO:</b> Implicitly constrains via the reference model in the loss -- less prone to extreme reward hacking
<br/><br/>
<b>Detection:</b> Monitor reward vs actual human preference correlation. If reward increases but human eval plateaus/drops, reward hacking is occurring.
</div>
</div>

### System Design (Q13)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Q13: Design a text-to-image generation system at Adobe scale</div>
</div>
<div style="color:#ccc; text-align:left; padding:0 20px; font-size:13px;">
<b>Answer outline (structured approach):</b>
<br/><br/>
<b>Step 1: Clarify requirements</b>
<br/>- Latency: P99 < 10s for 1024x1024 image
<br/>- Throughput: 1000+ requests/sec globally
<br/>- Quality: photorealistic, text-aligned, no artifacts
<br/>- Safety: content filtering, copyright awareness
<br/><br/>
<b>Step 2: Model architecture</b>
<br/>- Latent diffusion model (LDM) with VAE encoder/decoder
<br/>- Text encoder: CLIP + T5-XXL for rich text understanding
<br/>- U-Net / DiT (Diffusion Transformer) backbone
<br/>- CFG guidance scale tuned per use case (higher for precise prompts)
<br/><br/>
<b>Step 3: Inference optimization</b>
<br/>- FlashAttention in all attention layers
<br/>- INT8/FP8 quantization for weights (AWQ for quality preservation)
<br/>- Reduced sampling steps: DPM-Solver++ (20-25 steps vs 50)
<br/>- KV-cache optimization for any autoregressive components
<br/><br/>
<b>Step 4: Serving architecture</b>
<br/>- Continuous batching with dynamic batch sizing
<br/>- Multi-tier GPU allocation: A100/H100 for generation, smaller GPUs for safety checks
<br/>- Prefix caching for system prompt / style conditioning (RadixAttention)
<br/>- CDN for caching popular prompt templates
<br/><br/>
<b>Step 5: Safety and quality</b>
<br/>- Pre-generation: prompt classifier (reject harmful/copyright-infringing prompts)
<br/>- Post-generation: NSFW classifier + watermarking (Content Credentials)
<br/>- A/B testing framework for model quality comparison
<br/><br/>
<b>Step 6: Training pipeline</b>
<br/>- FSDP on multi-node GPU cluster
<br/>- Curated dataset with licensing metadata (Adobe Stock)
<br/>- RLHF/DPO alignment for aesthetic quality and prompt faithfulness
<br/>- Continuous training with human feedback loop
</div>
</div>

---

## 4. Interview Speech Templates

### Opening (First 30 seconds)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<pre style="color:#ccc; font-size:13px;">
TEMPLATE: Self-Introduction (30 seconds)

"Hi, I'm [name]. I'm a machine learning engineer with experience in
[model training/inference optimization/distributed systems]. Most recently,
I worked on [brief project description -- 1 sentence]. I'm excited about
this role at Adobe because [specific reason tied to JD -- e.g., 'the
intersection of generative AI and creative tools is exactly where I want
to apply my skills in production ML systems']."

KEY RULES:
- Under 30 seconds
- Mention 1-2 relevant skills
- Reference 1 specific Adobe product or technology
- End with forward-looking enthusiasm, not a history lesson
</pre>
</div>

### Handling Unknown Questions

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<pre style="color:#ccc; font-size:13px;">
TEMPLATE: When You Don't Know the Answer

Option A -- Partial knowledge:
"I'm not deeply familiar with [specific topic], but here's what I understand:
[share what you know]. My intuition is [educated guess based on fundamentals].
I'd want to verify this by [how you'd look it up]."

Option B -- Related knowledge:
"I haven't worked directly with [topic], but I've worked with [related topic]
which shares [specific similarity]. Based on that experience, I'd approach
this by [apply transferable principles]."

Option C -- Complete unknown:
"That's outside my current experience. I'd start by [first concrete step
to learn it -- read the paper, set up a toy experiment, review documentation].
In my experience learning [similar past technology], I was able to get
productive within [timeframe]."

KEY RULES:
- Never bluff. Interviewers can tell.
- Always share adjacent knowledge -- show your reasoning process.
- End with a concrete learning plan, not "I'd Google it."
</pre>
</div>

### Steering to Your Strengths

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<pre style="color:#ccc; font-size:13px;">
TEMPLATE: Redirecting to Strength Areas

Bridge phrases:
- "That reminds me of a related challenge I solved in [your strong area]..."
- "The underlying principle there is [fundamental concept], which I applied
   when I [specific experience]..."
- "At a higher level, this is about [abstraction], and my experience
   with [related project] taught me..."

EXAMPLE:
Interviewer: "How would you implement mixture-of-experts routing?"
You (if unfamiliar with MoE specifics):
"I haven't implemented MoE routing specifically, but the core challenge --
dynamically routing computation to specialized sub-networks -- is similar
to the cascading inference pipeline I built where a lightweight classifier
routes inputs to the appropriate expert model. In my case, [describe your
experience]. The MoE version would be similar but at the layer level rather
than the model level, with the added challenge of load balancing across
experts to prevent routing collapse."

KEY RULES:
- The bridge must be genuine -- don't force connections that aren't there
- Acknowledge the gap before bridging
- Show that you understand the PRINCIPLES even if you lack the specifics
</pre>
</div>

### Asking Good Questions (End of Interview)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<pre style="color:#ccc; font-size:13px;">
PREPARED QUESTIONS FOR ADOBE:

Technical depth:
1. "What's the current inference stack for Firefly -- are you using
    FlashAttention / quantization / speculative decoding in production?"
2. "How do you handle the tradeoff between generation quality and latency
    for real-time features vs batch processing?"

Team and culture:
3. "How does the ML team collaborate with the product/design teams
    on new generative features?"
4. "What does the model iteration cycle look like -- from research
    prototype to production deployment?"

Growth:
5. "What are the biggest technical challenges the team is working
    on in the next 6-12 months?"

KEY RULES:
- Ask max 2-3 questions (respect time)
- Prefer questions that show you've done research on Adobe
- Avoid questions about salary, PTO, or benefits in technical rounds
</pre>
</div>

---

## 5. Common Error Correction Quick-Reference Card

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Error Correction Quick-Reference</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:2px solid #555;">
<th style="padding:8px 12px; text-align:left; width:30px;">#</th>
<th style="padding:8px 12px; text-align:left;">Common Wrong Statement</th>
<th style="padding:8px 12px; text-align:left;">Correct Understanding</th>
<th style="padding:8px 12px; text-align:left;">Domain</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">1</td>
<td style="padding:8px 12px;">"FlashAttention reduces FLOPs"</td>
<td style="padding:8px 12px;">Same FLOPs (slightly more in backward). Speedup is from reduced HBM I/O, not compute.</td>
<td style="padding:8px 12px;">Inference</td>
</tr>
<tr>
<td style="padding:8px 12px;">2</td>
<td style="padding:8px 12px;">"Speculative decoding changes the output"</td>
<td style="padding:8px 12px;">Provably lossless via rejection sampling. Output distribution = target model exactly.</td>
<td style="padding:8px 12px;">Inference</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">3</td>
<td style="padding:8px 12px;">"DPO doesn't need a reference model"</td>
<td style="padding:8px 12px;">DPO requires pi_ref (the SFT model) in its loss. It avoids a separate reward model, not a reference model.</td>
<td style="padding:8px 12px;">Alignment</td>
</tr>
<tr>
<td style="padding:8px 12px;">4</td>
<td style="padding:8px 12px;">"DDPM and DDIM are different models"</td>
<td style="padding:8px 12px;">Same trained model, different sampling procedures. DDIM reinterprets the reverse process as deterministic.</td>
<td style="padding:8px 12px;">Diffusion</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">5</td>
<td style="padding:8px 12px;">"Diffusion models generate from noise to image in one step"</td>
<td style="padding:8px 12px;">Iterative denoising: T steps (10-1000). Each step removes a small amount of noise. Fast samplers reduce steps but still need multiple.</td>
<td style="padding:8px 12px;">Diffusion</td>
</tr>
<tr>
<td style="padding:8px 12px;">6</td>
<td style="padding:8px 12px;">"Tensor parallelism = splitting data across GPUs"</td>
<td style="padding:8px 12px;">TP splits model layers (weight matrices) across GPUs. Data parallelism splits data. They are orthogonal strategies.</td>
<td style="padding:8px 12px;">Distributed</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">7</td>
<td style="padding:8px 12px;">"RoPE is a learnable positional encoding"</td>
<td style="padding:8px 12px;">RoPE is fixed (not learned). It applies rotation matrices based on position. The rotation angles (theta_i) are derived from a formula, not trained.</td>
<td style="padding:8px 12px;">Architecture</td>
</tr>
<tr>
<td style="padding:8px 12px;">8</td>
<td style="padding:8px 12px;">"KV-cache is optional for efficiency"</td>
<td style="padding:8px 12px;">Without KV-cache, generating N tokens costs O(N^2) total compute. It is essential, not optional. The question is how to manage it (PagedAttention, quantization).</td>
<td style="padding:8px 12px;">Inference</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">9</td>
<td style="padding:8px 12px;">"CFG just scales up the text embedding"</td>
<td style="padding:8px 12px;">CFG extrapolates between unconditional and conditional noise predictions: eps_guided = eps_uncond + w*(eps_cond - eps_uncond). It operates on noise predictions, not embeddings.</td>
<td style="padding:8px 12px;">Diffusion</td>
</tr>
<tr>
<td style="padding:8px 12px;">10</td>
<td style="padding:8px 12px;">"FSDP is just pipeline parallelism"</td>
<td style="padding:8px 12px;">FSDP shards parameters/gradients/optimizer states across GPUs (like ZeRO-3). Each GPU still processes full forward/backward. PP assigns different layers to different GPUs.</td>
<td style="padding:8px 12px;">Distributed</td>
</tr>
</table>
</div>
</div>

---

## Self-Check Questions

- [ ] **Q1:** Walk through the STAR-T framework. Give a 2-minute version of Story 1 (inference optimization) out loud.
- [ ] **Q2:** An interviewer asks "Explain FlashAttention." Deliver a 90-second answer without looking at notes.
- [ ] **Q3:** An interviewer asks about a topic you don't know (e.g., "How does mixture-of-experts routing work?"). Practice the bridge-to-strength technique.
- [ ] **Q4:** Explain the DPO vs RLHF tradeoff. Include the math (Bradley-Terry, DPO loss). Under 2 minutes.
- [ ] **Q5:** Design a text-to-image system for Adobe. Cover all 6 steps of the system design outline in 5 minutes.

---

## Quick Reference Card

<pre style="background:#111; padding:12px; border-radius:4px; color:#ccc; font-size:13px;">
STAR-T: Situation (15s) -> Task (15s) -> Approach (60s) -> Result (15s) -> Transfer (15s)
    Total: ~2 min per story. Lead with punchline. Use "I" not "we".

3 Stories:
    1. Inference Pipeline: quantization + continuous batching + operator fusion -> 63% P99 reduction
    2. Distributed Training: FSDP + mixed precision + gradient checkpointing -> 6.7x speedup (8 GPUs)
    3. Data Quality + Alignment: DPO preference optimization -> +18% user satisfaction

13 Questions by Domain:
    Diffusion (Q1-4): DDPM forward/reverse, CFG, Latent Diffusion, DDPM vs DDIM
    Inference (Q5-7): FlashAttention, Speculative Decoding, GPTQ vs AWQ
    Distributed (Q8-10): DP/TP/PP comparison, FSDP vs DP, Debug slow training
    Alignment (Q11-12): RLHF vs DPO tradeoffs, Reward hacking prevention
    System Design (Q13): Text-to-image at scale (6-step framework)

Speech Templates:
    Opening: 30s max. Name + skill + project + Adobe enthusiasm.
    Unknown: Share adjacent knowledge, never bluff, end with learning plan.
    Steering: Bridge phrase -> acknowledge gap -> show principles -> redirect to strength.
    Questions: 2-3 max. Show research. Avoid HR topics in tech rounds.

10 Error Corrections:
    FlashAttention: same FLOPs, fewer HBM trips (not fewer computations)
    Speculative decoding: lossless (rejection sampling)
    DPO: needs pi_ref (no reward model, but yes reference model)
    DDIM: same model as DDPM (different sampler)
    TP != DP: TP splits layers, DP splits data
    RoPE: fixed (not learned)
    FSDP != PP: FSDP shards params, PP assigns layers
</pre>
"""


def main() -> None:
    """Insert the Mock Interview Questions + STAR-T Stories note into mle_prep.db."""
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
