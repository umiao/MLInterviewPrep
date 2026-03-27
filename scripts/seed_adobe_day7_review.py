"""Seed script: Insert Adobe Prep Day7 -- Review Checklist + Concept Map + Error Cards.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day7: Review Checklist + Concept Map + Error Cards"

CONTENT = r"""# Review Checklist + Concept Map + Error Cards (Adobe Prep Day 7)

> Final review day. This note consolidates all 6 previous days into:
> (1) Master checklist with checkbox items across all domains,
> (2) HTML concept map showing cross-topic connections,
> (3) Error correction quick-reference table,
> (4) Daily time allocation table,
> (5) Formula cheat sheet with all key equations.
> All formulas use 440.

---

## 1. Master Review Checklist

Use this checklist on the morning of the interview. Check each box when
you can explain the concept from memory, including the key formula.

### Domain 1: Diffusion Models (Day 1)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#4a90d9; margin-bottom:12px;">Diffusion Models Checklist</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:6px 12px; text-align:left; width:30px;"></th>
<th style="padding:6px 12px; text-align:left;">Topic</th>
<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>
</tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>DDPM Forward Process</td>
<td>Can write x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon from memory</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>DDPM Reverse Process</td>
<td>Know that model predicts noise epsilon_theta(x_t, t), not x_0 directly</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Training Objective</td>
<td>Simple MSE loss: E[||epsilon - epsilon_theta(x_t, t)||^2], t sampled uniformly</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Noise Schedules</td>
<td>Linear vs Cosine -- cosine preserves more signal at early steps, better for high-res</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>DDIM Sampler</td>
<td>Same trained model, deterministic sampling, 50 steps vs DDPM 1000 steps</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Latent Diffusion / Stable Diffusion</td>
<td>VAE encodes 512x512x3 to 64x64x4 (8x spatial compression), diffusion in latent space</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Classifier-Free Guidance (CFG)</td>
<td>epsilon_hat = epsilon_uncond + w * (epsilon_cond - epsilon_uncond), typical w=7.5</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Score-Based / SDE View</td>
<td>Score = grad log p(x), forward SDE + reverse SDE framework unifies DDPM/SMLD</td></tr>
</table>
</div>

### Domain 2: RLHF/DPO Alignment + Distillation (Day 2)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#2d6a4f; margin-bottom:12px;">Alignment + Distillation Checklist</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:6px 12px; text-align:left; width:30px;"></th>
<th style="padding:6px 12px; text-align:left;">Topic</th>
<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>
</tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>RLHF 3-Stage Pipeline</td>
<td>SFT -> Reward Model (Bradley-Terry) -> PPO fine-tuning with KL penalty</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Bradley-Terry Model</td>
<td>P(y_w > y_l) = sigma(r(y_w) - r(y_l)), trained on human preference pairs</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>DPO Closed-Form</td>
<td>L_DPO = -E[log sigma(beta * (log pi/pi_ref(y_w) - log pi/pi_ref(y_l)))], no reward model needed</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>RLHF vs DPO Tradeoffs</td>
<td>RLHF: more flexible, reward hacking risk, 3 models. DPO: simpler, needs reference model, beta-sensitive</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Reward Hacking</td>
<td>Model exploits reward model flaws (verbosity, formatting). Fix: KL constraint, reward ensemble</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Variants (RLAIF, IPO, KTO)</td>
<td>RLAIF: AI-generated preferences. IPO: removes log sigmoid. KTO: single-response (no pairs)</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>LLM Distillation</td>
<td>L_KD = alpha*T^2*KL(p_teacher || p_student) + (1-alpha)*CE. Higher T = softer distribution</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Distillation Architecture</td>
<td>70B to 7B: reduce layers, hidden_dim, num_heads. Keep vocab_size, tokenizer</td></tr>
</table>
</div>

### Domain 3: Distributed Training (Day 3)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#d4a017; margin-bottom:12px;">Distributed Training Checklist</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:6px 12px; text-align:left; width:30px;"></th>
<th style="padding:6px 12px; text-align:left;">Topic</th>
<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>
</tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Data Parallelism (DP/DDP)</td>
<td>Replicate model on each GPU, AllReduce gradients. Memory: 16P per GPU (no savings)</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Tensor Parallelism (TP)</td>
<td>Split weight matrices within a layer. MLP: column-parallel then row-parallel. Needs NVLink</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Pipeline Parallelism (PP)</td>
<td>Assign layers to GPUs sequentially. Bubble fraction: (N-1)/(N+M-1). Micro-batches reduce bubble</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>FSDP / ZeRO</td>
<td>Shard optimizer+gradients+params across GPUs. Memory: 16P/N. All-gather before forward, reduce-scatter after backward</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>ZeRO Stages</td>
<td>Stage1: optimizer states. Stage2: +gradients. Stage3: +parameters. Progressive memory reduction</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Memory Formula</td>
<td>Per-param: 2 (fp16 weight) + 2 (fp16 grad) + 12 (Adam: fp32 weight + momentum + variance) = 16 bytes</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>3D Parallelism</td>
<td>TP (intra-node NVLink) x PP (cross-node) x DP (remaining). GPT-3: TP=8, PP=16, DP=8</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Selection Guide</td>
<td>Fits 1 GPU: DDP. Fits 1 node: FSDP. Exceeds 1 node: 3D parallelism (TP+PP+DP)</td></tr>
</table>
</div>

### Domain 4: RoPE + Long Context + Video Generation (Day 4)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#8b5cf6; margin-bottom:12px;">RoPE + Long Context + Video Checklist</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:6px 12px; text-align:left; width:30px;"></th>
<th style="padding:6px 12px; text-align:left;">Topic</th>
<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>
</tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>RoPE Core Idea</td>
<td>Rotate q,k by position-dependent angle: theta_i = 1/10000^(2i/d). q_m^T k_n depends only on (m-n)</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>RoPE vs Other PE</td>
<td>RoPE: fixed (not learned), relative position, no max length. Sinusoidal: absolute, fixed. ALiBi: linear bias</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Position Interpolation (PI)</td>
<td>Scale position: m' = m * (L_train / L_target). Simple but needs fine-tuning</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>NTK-Aware Scaling</td>
<td>Scale base frequency: theta_i' = 1/(b*alpha)^(2i/d). No fine-tuning needed for moderate extension</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>YaRN</td>
<td>Per-dimension PI/NTK blend + attention temperature scaling. Best quality for large extensions</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Video Diffusion Architecture</td>
<td>3D VAE (T*H*W to T'*H'*W'), temporal + spatial attention layers, frame consistency</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>DiT (Diffusion Transformer)</td>
<td>Spacetime patches, AdaLN-Zero conditioning. Replaces U-Net with transformer backbone</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Adobe Firefly Context</td>
<td>Firefly Image to Firefly Video: add temporal layers. Key challenges: temporal consistency, motion, memory</td></tr>
</table>
</div>

### Domain 5: Inference Optimization (Day 5)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#e07a5f; margin-bottom:12px;">Inference Optimization Checklist</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:6px 12px; text-align:left; width:30px;"></th>
<th style="padding:6px 12px; text-align:left;">Topic</th>
<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>
</tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>FlashAttention</td>
<td>Tiled computation in SRAM (19 TB/s). IO: O(N^2*d^2/M) vs standard O(N^2*d + N^2). Online softmax trick</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>GPTQ</td>
<td>Layer-wise OBS, sequential error compensation, INT4 weight-only. Post-training, no retraining</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>AWQ</td>
<td>Protect 1% salient channels via per-channel scaling. INT4. Observation: 1% weights matter 10x more</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>SmoothQuant (W8A8)</td>
<td>Migrate quantization difficulty from activations to weights. Per-channel smooth factor s_j</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>KV-Cache</td>
<td>Size: 2*L*N*H*d bytes per sequence. Biggest inference memory consumer for long sequences</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>PagedAttention</td>
<td>Virtual memory for KV-cache: blocks + page tables. Eliminates fragmentation. Copy-on-write for beam search</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Continuous Batching</td>
<td>Iteration-level scheduling: new requests join mid-batch. No idle GPU slots waiting for longest sequence</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Speculative Decoding</td>
<td>Draft model proposes K tokens, target verifies in parallel. Lossless (rejection sampling). ~2-3x speedup</td></tr>
</table>
</div>

### Domain 6: Interview Skills (Day 6)

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#ff6b6b; margin-bottom:12px;">Interview Skills Checklist</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:6px 12px; text-align:left; width:30px;"></th>
<th style="padding:6px 12px; text-align:left;">Topic</th>
<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>
</tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>STAR-T Framework</td>
<td>Situation(15s) -> Task(15s) -> Approach(60s) -> Result(15s) -> Transfer(15s). Total ~2min</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Story 1: Inference Pipeline</td>
<td>KV-cache + operator fusion + INT8 + continuous batching -> 63% P99 reduction, 2.4x throughput</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Story 2: Distributed Training</td>
<td>FSDP + mixed precision + gradient checkpointing -> 6.7x speedup, 84% scaling efficiency on 8 GPUs</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Story 3: Data Quality + DPO</td>
<td>Preference pipeline + reward model + DPO -> +18% satisfaction, 3x cheaper than RLHF</td></tr>
<tr><td style="padding:6px 12px;">[ ]</td><td>Opening Template</td>
<td>30-second elevator pitch: background, current focus, why Adobe. Practice it smooth</td></tr>
<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Handling Unknowns</td>
<td>3 options: reason from first principles, relate to known concept, say "I'd look into X because Y"</td></tr>
</table>
</div>

---

## 2. Concept Map: Cross-Topic Connections

This map shows how topics from all 6 days interconnect. Follow the arrows
to see how mastering one topic strengthens understanding of related ones.

<div style="background:#0d1117; padding:24px; border-radius:12px; margin:16px 0; font-family:monospace; color:#e0e0e0; overflow-x:auto;">
<div style="text-align:center; font-size:16px; font-weight:bold; color:#fff; margin-bottom:20px;">
Adobe ML Interview Concept Map
</div>

<pre style="color:#e0e0e0; font-size:12px; line-height:1.6; text-align:center;">
                          +-------------------+
                          |   DIFFUSION (D1)  |
                          |  DDPM / CFG / LDM |
                          +--------+----------+
                                   |
                    +--------------+--------------+
                    |                             |
                    v                             v
          +-----------------+           +------------------+
          | VIDEO GEN (D4)  |           | LATENT SPACE     |
          | 3D VAE + DiT    |           | VAE compression  |
          | Temporal attn   |           | 8x downsample    |
          +--------+--------+           +--------+---------+
                   |                             |
                   |    +------------------------+
                   |    |
                   v    v
          +-----------------+           +------------------+
          | INFERENCE (D5)  |<--------->| DISTRIBUTED (D3) |
          | FlashAttn, KV$  |  train    | DP / TP / PP     |
          | Quant, vLLM     |  vs serve | FSDP / ZeRO      |
          +--------+--------+           +--------+---------+
                   |                             |
                   |         +---------+         |
                   +-------->| MEMORY  |<--------+
                             | MGMT    |
                             +---------+
                             | Train: 16P/N    |
                             | Serve: KV-cache  |
                             | Both: activation |
                             +--------+---------+
                                      |
                   +------------------+------------------+
                   |                                     |
                   v                                     v
          +-----------------+           +------------------+
          | ROPE / PE (D4)  |           | ALIGNMENT (D2)   |
          | theta_i formula |           | RLHF / DPO       |
          | PI / NTK / YaRN |           | Distillation      |
          +--------+--------+           +--------+---------+
                   |                             |
                   +----------+    +-------------+
                              |    |
                              v    v
                    +-------------------+
                    | LONG CONTEXT (D4) |
                    | RoPE extension    |
                    | KV-cache growth   |
                    | FlashAttn needed  |
                    +-------------------+
</pre>

<div style="margin-top:16px; padding:12px; background:#1a1a2e; border-radius:8px;">
<div style="font-weight:bold; color:#4a90d9; margin-bottom:8px;">Key Cross-Topic Connections</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">
<tr style="border-bottom:1px solid #333;">
<th style="padding:6px 10px; text-align:left;">Connection</th>
<th style="padding:6px 10px; text-align:left;">Why It Matters</th>
</tr>
<tr><td style="padding:6px 10px;">Diffusion -> Video Gen</td>
<td style="padding:6px 10px;">Video diffusion adds temporal layers to image diffusion (Firefly Image -> Firefly Video)</td></tr>
<tr style="background:#222;"><td style="padding:6px 10px;">Latent Space -> Inference</td>
<td style="padding:6px 10px;">VAE compression reduces diffusion compute. Same principle: work in compact space</td></tr>
<tr><td style="padding:6px 10px;">Inference <-> Distributed</td>
<td style="padding:6px 10px;">Training uses TP/PP/FSDP; serving uses TP + KV-cache sharding. Both manage GPU memory</td></tr>
<tr style="background:#222;"><td style="padding:6px 10px;">Memory Management (shared)</td>
<td style="padding:6px 10px;">Training: 16P bytes/param. Serving: KV-cache dominates. Both: activation checkpointing</td></tr>
<tr><td style="padding:6px 10px;">RoPE -> Long Context</td>
<td style="padding:6px 10px;">RoPE extension (PI/NTK/YaRN) enables longer sequences, but KV-cache grows linearly</td></tr>
<tr style="background:#222;"><td style="padding:6px 10px;">Long Context -> FlashAttention</td>
<td style="padding:6px 10px;">Longer sequences make O(N^2) attention critical. FlashAttention makes it feasible</td></tr>
<tr><td style="padding:6px 10px;">Alignment -> Distillation</td>
<td style="padding:6px 10px;">Aligned large model (teacher) distilled to small model (student). DPO + KD pipeline</td></tr>
<tr style="background:#222;"><td style="padding:6px 10px;">DPO -> Project Story 3</td>
<td style="padding:6px 10px;">Your data quality project used DPO for alignment -- direct interview connection</td></tr>
</table>
</div>
</div>

---

## 3. Error Correction Quick-Reference Cards

These are the most common misunderstandings, compiled from all 6 days.
Review each card and make sure you would NOT make these mistakes in an interview.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#ff6b6b; margin-bottom:12px;">Error Correction Cards (7 Common Misunderstandings)</div>

<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; border-left:4px solid #ff4444; border-radius:4px;">
<div style="color:#ff6b6b; font-weight:bold;">Card 1: "DDPM generates images from random noise in one step"</div>
<div style="color:#888; margin:4px 0;">WRONG. DDPM uses T=1000 iterative denoising steps. Each step removes a small amount of noise.</div>
<div style="color:#4a90d9;">CORRECT: x_T (pure noise) -> x_{T-1} -> ... -> x_0 (clean image). DDIM can reduce to ~50 steps but still iterative.</div>
</div>

<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; border-left:4px solid #ff4444; border-radius:4px;">
<div style="color:#ff6b6b; font-weight:bold;">Card 2: "DPO eliminates the need for any reference model"</div>
<div style="color:#888; margin:4px 0;">WRONG. DPO eliminates the REWARD model, but still requires a REFERENCE policy (pi_ref).</div>
<div style="color:#4a90d9;">CORRECT: DPO loss uses log(pi_theta/pi_ref) for both y_w and y_l. pi_ref is the SFT checkpoint, frozen during DPO training.</div>
</div>

<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; border-left:4px solid #ff4444; border-radius:4px;">
<div style="color:#ff6b6b; font-weight:bold;">Card 3: "Tensor Parallelism = Data Parallelism across layers"</div>
<div style="color:#888; margin:4px 0;">WRONG. TP splits weight MATRICES within a single layer. DP replicates the full model and splits DATA.</div>
<div style="color:#4a90d9;">CORRECT: TP splits columns/rows of W. DP splits mini-batch. PP assigns whole layers to different GPUs. FSDP shards parameters.</div>
</div>

<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; border-left:4px solid #ff4444; border-radius:4px;">
<div style="color:#ff6b6b; font-weight:bold;">Card 4: "RoPE is a learned positional embedding"</div>
<div style="color:#888; margin:4px 0;">WRONG. RoPE is deterministic (fixed), not learned. Angles are computed from position and dimension index.</div>
<div style="color:#4a90d9;">CORRECT: theta_i = 1/10000^(2i/d) is a fixed formula. No learnable parameters. This is what enables length extrapolation via PI/NTK.</div>
</div>

<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; border-left:4px solid #ff4444; border-radius:4px;">
<div style="color:#ff6b6b; font-weight:bold;">Card 5: "Speculative decoding changes the output distribution"</div>
<div style="color:#888; margin:4px 0;">WRONG. Speculative decoding is LOSSLESS -- the output distribution is identical to the target model.</div>
<div style="color:#4a90d9;">CORRECT: Rejection sampling ensures accepted tokens match the target model's distribution exactly. Speed gain comes from parallel verification, not approximation.</div>
</div>

<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; border-left:4px solid #ff4444; border-radius:4px;">
<div style="color:#ff6b6b; font-weight:bold;">Card 6: "FSDP is the same as Pipeline Parallelism"</div>
<div style="color:#888; margin:4px 0;">WRONG. FSDP shards all parameters across GPUs (any param can be on any GPU). PP assigns whole layers sequentially.</div>
<div style="color:#4a90d9;">CORRECT: FSDP = each GPU holds 1/N of every parameter, all-gathers before compute. PP = GPU 0 has layers 0-3, GPU 1 has layers 4-7, etc. Different communication patterns.</div>
</div>

<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; border-left:4px solid #ff4444; border-radius:4px;">
<div style="color:#ff6b6b; font-weight:bold;">Card 7: "FlashAttention reduces the computational complexity of attention"</div>
<div style="color:#888; margin:4px 0;">WRONG. FlashAttention does NOT change the O(N^2*d) compute (same number of FLOPs).</div>
<div style="color:#4a90d9;">CORRECT: FlashAttention reduces IO complexity from O(N^2*d + N^2) to O(N^2*d^2/M) by tiling in SRAM. Same math, fewer memory round-trips. It is an IO optimization, not a compute optimization.</div>
</div>
</div>

---

## 4. Daily Time Allocation Table

Suggested time allocation for a 7-day prep cycle. Use this to calibrate
how much time to spend on each domain during the final review.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#fff; margin-bottom:12px;">7-Day Prep Schedule</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">
<tr style="border-bottom:2px solid #444;">
<th style="padding:8px 12px; text-align:left;">Day</th>
<th style="padding:8px 12px; text-align:left;">Domain</th>
<th style="padding:8px 12px; text-align:center;">Study (min)</th>
<th style="padding:8px 12px; text-align:center;">Practice (min)</th>
<th style="padding:8px 12px; text-align:center;">Total (min)</th>
<th style="padding:8px 12px; text-align:left;">Focus</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">Day 1</td>
<td style="padding:8px 12px;">Diffusion Models</td>
<td style="padding:8px 12px; text-align:center;">50</td>
<td style="padding:8px 12px; text-align:center;">20</td>
<td style="padding:8px 12px; text-align:center;">70</td>
<td style="padding:8px 12px;">Formulas, DDPM/DDIM, CFG, Stable Diffusion pipeline</td>
</tr>
<tr>
<td style="padding:8px 12px;">Day 2</td>
<td style="padding:8px 12px;">RLHF/DPO + Distill</td>
<td style="padding:8px 12px; text-align:center;">45</td>
<td style="padding:8px 12px; text-align:center;">15</td>
<td style="padding:8px 12px; text-align:center;">60</td>
<td style="padding:8px 12px;">3-stage RLHF, DPO loss, comparison, distillation</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">Day 3</td>
<td style="padding:8px 12px;">Distributed Training</td>
<td style="padding:8px 12px; text-align:center;">50</td>
<td style="padding:8px 12px; text-align:center;">15</td>
<td style="padding:8px 12px; text-align:center;">65</td>
<td style="padding:8px 12px;">DP/TP/PP/FSDP, memory math, 3D parallelism</td>
</tr>
<tr>
<td style="padding:8px 12px;">Day 4</td>
<td style="padding:8px 12px;">RoPE + Video Gen</td>
<td style="padding:8px 12px; text-align:center;">45</td>
<td style="padding:8px 12px; text-align:center;">15</td>
<td style="padding:8px 12px; text-align:center;">60</td>
<td style="padding:8px 12px;">RoPE math, PI/NTK/YaRN, video diffusion, DiT</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">Day 5</td>
<td style="padding:8px 12px;">Inference Optim</td>
<td style="padding:8px 12px; text-align:center;">50</td>
<td style="padding:8px 12px; text-align:center;">15</td>
<td style="padding:8px 12px; text-align:center;">65</td>
<td style="padding:8px 12px;">FlashAttn, quant, KV-cache, PagedAttn, spec decode</td>
</tr>
<tr>
<td style="padding:8px 12px;">Day 6</td>
<td style="padding:8px 12px;">Mock Interview</td>
<td style="padding:8px 12px; text-align:center;">20</td>
<td style="padding:8px 12px; text-align:center;">40</td>
<td style="padding:8px 12px; text-align:center;">60</td>
<td style="padding:8px 12px;">STAR-T stories, 13 Q&A drill, speech templates</td>
</tr>
<tr style="background:#333; border-top:2px solid #4a90d9;">
<td style="padding:8px 12px; font-weight:bold;">Day 7</td>
<td style="padding:8px 12px; font-weight:bold;">Review</td>
<td style="padding:8px 12px; text-align:center; font-weight:bold;">30</td>
<td style="padding:8px 12px; text-align:center; font-weight:bold;">30</td>
<td style="padding:8px 12px; text-align:center; font-weight:bold;">60</td>
<td style="padding:8px 12px; font-weight:bold;">This note: checklist, concept map, error cards, formulas</td>
</tr>
<tr style="border-top:2px solid #666;">
<td style="padding:8px 12px;" colspan="2"><b>Total</b></td>
<td style="padding:8px 12px; text-align:center;"><b>290</b></td>
<td style="padding:8px 12px; text-align:center;"><b>150</b></td>
<td style="padding:8px 12px; text-align:center;"><b>440</b></td>
<td style="padding:8px 12px;">~7.3 hours total across 7 days</td>
</tr>
</table>
</div>

---

## 5. Formula Cheat Sheet

All key formulas consolidated in one place. Practice writing each from memory.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#fff; margin-bottom:16px;">Formula Cheat Sheet (All Domains)</div>

<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">
<div style="color:#4a90d9; font-weight:bold; margin-bottom:8px;">Diffusion Models</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888; width:140px;">Forward process</td>
<td style="padding:6px 10px;">x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon,  epsilon ~ N(0, I)</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">Training loss</td>
<td style="padding:6px 10px;">L = E_{t,x_0,epsilon}[ ||epsilon - epsilon_theta(x_t, t)||^2 ]</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">CFG</td>
<td style="padding:6px 10px;">epsilon_hat = epsilon_uncond + w * (epsilon_cond - epsilon_uncond),  w = 7.5 typical</td>
</tr>
<tr>
<td style="padding:6px 10px; color:#888;">VAE compression</td>
<td style="padding:6px 10px;">512x512x3 -> 64x64x4 (8x spatial, latent diffusion)</td>
</tr>
</table>
</div>

<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">
<div style="color:#2d6a4f; font-weight:bold; margin-bottom:8px;">Alignment (RLHF / DPO)</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888; width:140px;">Bradley-Terry</td>
<td style="padding:6px 10px;">P(y_w > y_l) = sigma(r_phi(y_w) - r_phi(y_l))</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">DPO loss</td>
<td style="padding:6px 10px;">L = -E[log sigma(beta * (log(pi/pi_ref)(y_w) - log(pi/pi_ref)(y_l)))]</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">KD loss</td>
<td style="padding:6px 10px;">L_KD = alpha * T^2 * KL(p_teacher^T || p_student^T) + (1 - alpha) * CE(y, p_student)</td>
</tr>
<tr>
<td style="padding:6px 10px; color:#888;">Temperature</td>
<td style="padding:6px 10px;">p_i^T = exp(z_i / T) / sum_j(exp(z_j / T))</td>
</tr>
</table>
</div>

<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">
<div style="color:#d4a017; font-weight:bold; margin-bottom:8px;">Distributed Training</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888; width:140px;">Memory per param</td>
<td style="padding:6px 10px;">16 bytes = 2(fp16 wt) + 2(fp16 grad) + 4(fp32 wt) + 4(momentum) + 4(variance)</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">DDP memory</td>
<td style="padding:6px 10px;">16P bytes per GPU (no savings, full replica)</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">FSDP memory</td>
<td style="padding:6px 10px;">16P / N bytes per GPU (N = number of GPUs)</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">PP bubble</td>
<td style="padding:6px 10px;">(N - 1) / (N + M - 1),  N = stages, M = micro-batches</td>
</tr>
<tr>
<td style="padding:6px 10px; color:#888;">3D layout</td>
<td style="padding:6px 10px;">TP(intra-node NVLink) x PP(cross-node) x DP(remaining GPUs)</td>
</tr>
</table>
</div>

<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">
<div style="color:#8b5cf6; font-weight:bold; margin-bottom:8px;">RoPE + Long Context</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888; width:140px;">RoPE angle</td>
<td style="padding:6px 10px;">theta_i = 1 / 10000^(2i / d),  rotation by m * theta_i at position m</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">Relative position</td>
<td style="padding:6px 10px;">q_m^T k_n depends only on (m - n), not absolute positions</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">Position Interp</td>
<td style="padding:6px 10px;">m' = m * (L_train / L_target)</td>
</tr>
<tr>
<td style="padding:6px 10px; color:#888;">NTK scaling</td>
<td style="padding:6px 10px;">theta_i' = 1 / (b * alpha)^(2i / d),  alpha = L_target / L_train</td>
</tr>
</table>
</div>

<div style="padding:12px; background:#222; border-radius:4px;">
<div style="color:#e07a5f; font-weight:bold; margin-bottom:8px;">Inference Optimization</div>
<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888; width:140px;">FlashAttn IO</td>
<td style="padding:6px 10px;">O(N^2 * d^2 / M) vs standard O(N^2 * d + N^2),  M = SRAM size</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">KV-cache size</td>
<td style="padding:6px 10px;">2 * L * N * H * d bytes per sequence (L=layers, N=seq_len, H=heads, d=head_dim)</td>
</tr>
<tr style="border-bottom:1px solid #333;">
<td style="padding:6px 10px; color:#888;">SRAM vs HBM</td>
<td style="padding:6px 10px;">SRAM: ~20 MB, 19 TB/s  |  HBM: ~80 GB, 2 TB/s  (A100)</td>
</tr>
<tr>
<td style="padding:6px 10px; color:#888;">Spec decode</td>
<td style="padding:6px 10px;">Draft K tokens, verify in 1 forward pass. Accept rate ~70-80%. Speedup ~2-3x</td>
</tr>
</table>
</div>
</div>

---

## Self-Check Questions

Answer these without looking at the notes. If you struggle with any,
go back to the relevant day's note.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#fff; margin-bottom:12px;">Final Review Self-Check (5 Questions)</div>

<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">
<b style="color:#4a90d9;">Q1 (Cross-domain):</b> You're serving a Stable Diffusion model at Adobe scale.
Which inference optimizations from Day 5 apply to diffusion models vs autoregressive LLMs?
What is different about KV-cache usage in diffusion vs LLM serving?
</div>

<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">
<b style="color:#2d6a4f;">Q2 (Formula):</b> Write the DPO loss from memory. Then explain: if beta is too small,
what happens? If beta is too large? How does this relate to the KL constraint in RLHF?
</div>

<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">
<b style="color:#d4a017;">Q3 (System Design):</b> You need to train a 70B parameter model on 64 A100 80GB GPUs.
Design the parallelism strategy. Show the memory calculation. Explain why you chose each parallelism type.
</div>

<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">
<b style="color:#8b5cf6;">Q4 (Connection):</b> How does RoPE's relative position property help with
FlashAttention's tiling? Does the tiling strategy need to change for relative vs absolute position encodings?
</div>

<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">
<b style="color:#e07a5f;">Q5 (Project Story):</b> Walk through your inference optimization project using STAR-T.
Keep it under 2 minutes. Include specific numbers and bridge to Adobe Firefly serving at the end.
</div>
</div>

---

## Quick Reference Card

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="font-size:15px; font-weight:bold; color:#fff; margin-bottom:12px;">Interview Day Quick Reference</div>
<pre style="color:#e0e0e0; font-size:12px; line-height:1.8;">
DIFFUSION:  x_t = sqrt(a_bar)*x_0 + sqrt(1-a_bar)*eps  |  CFG: w=7.5  |  T=1000
ALIGNMENT:  RLHF = SFT+RM+PPO  |  DPO = no reward model, yes ref model  |  beta=0.1-0.5
DISTRIBUTED: DDP=16P  |  FSDP=16P/N  |  TP=intra-node  |  PP bubble=(N-1)/(N+M-1)
ROPE:       theta=1/10000^(2i/d)  |  fixed, not learned  |  PI: scale m  |  NTK: scale base
INFERENCE:  FlashAttn=IO opt  |  KV$=2LNHd  |  SpecDec=lossless  |  PagedAttn=virtual mem
STORIES:    Inference(63% P99)  |  DistTrain(6.7x)  |  DPO(+18% sat)  |  STAR-T ~2min
TOTAL PREP: 440 minutes across 7 days (290 study + 150 practice)
</pre>
</div>
"""


def main() -> None:
    """Insert the Review Checklist + Concept Map + Error Cards note into mle_prep.db."""
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
