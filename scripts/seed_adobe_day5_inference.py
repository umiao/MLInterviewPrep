"""Seed script: Insert Adobe Prep Day5 -- Inference Optimization + Project Narrative note.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day5: Inference Optimization + Project Narrative"

CONTENT = r"""# Inference Optimization + Project Narrative (Adobe Prep Day 5)

> Modern LLMs are expensive to serve. Understanding the full inference optimization
> stack -- from attention-level tricks (FlashAttention) to weight compression
> (quantization) to serving-system designs (continuous batching, speculative decoding)
> -- is critical for Adobe-scale deployment. This note also maps your project
> experience to Adobe interview framing.

---

## 1. FlashAttention

### The memory bottleneck

Standard self-attention computes:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) V$$

For sequence length $N$ and head dimension $d$:
- $QK^T$ produces an $N \times N$ attention matrix
- This matrix must be materialized in GPU **HBM** (High Bandwidth Memory)
- Memory: $O(N^2)$. For $N = 8192$, that is 512 MB per head per layer (fp32)

The bottleneck is not FLOPs but **memory I/O**: reading/writing the $N \times N$ matrix
from HBM is the dominant cost.

### SRAM vs HBM

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">GPU Memory Hierarchy</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Memory</th>
<th style="padding:8px 16px; text-align:left;">Size</th>
<th style="padding:8px 16px; text-align:left;">Bandwidth</th>
<th style="padding:8px 16px; text-align:left;">Latency</th>
</tr>
<tr style="background:#4a90d9; color:white;">
<td style="padding:8px 16px;"><b>SRAM (on-chip)</b></td>
<td style="padding:8px 16px;">~20 MB (A100)</td>
<td style="padding:8px 16px;">~19 TB/s</td>
<td style="padding:8px 16px;">~1 ns</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">HBM (off-chip)</td>
<td style="padding:8px 16px;">40-80 GB (A100)</td>
<td style="padding:8px 16px;">~2 TB/s</td>
<td style="padding:8px 16px;">~100 ns</td>
</tr>
</table>
<div style="margin-top:12px; color:#ccc;">
HBM is ~10x slower than SRAM. Standard attention does 3 HBM round-trips:<br/>
(1) read Q,K -> (2) write N x N matrix to HBM -> (3) read it back for softmax x V
</div>
</div>
</div>

### FlashAttention algorithm (tiling)

**Core idea:** Never materialize the full $N \times N$ attention matrix. Instead, compute
attention in **tiles** that fit in SRAM.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">FlashAttention Tiled Computation</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
Algorithm: FlashAttention (simplified)

For each block of queries Q_i (size B_r x d):
  Load Q_i into SRAM
  Initialize: O_i = 0, l_i = 0, m_i = -inf  (output, sum, max)

  For each block of keys/values K_j, V_j (size B_c x d):
    Load K_j, V_j into SRAM
    Compute S_ij = Q_i @ K_j^T / sqrt(d)    -- in SRAM, B_r x B_c tile
    Compute local softmax statistics:
      m_ij = rowmax(S_ij)
      P_ij = exp(S_ij - m_ij)
      l_ij = rowsum(P_ij)
    Update running softmax (online softmax trick):
      m_new = max(m_i, m_ij)
      l_new = exp(m_i - m_new) * l_i + exp(m_ij - m_new) * l_ij
      O_i = (exp(m_i - m_new) * l_i * O_i + exp(m_ij - m_new) * P_ij @ V_j) / l_new
      m_i, l_i = m_new, l_new

  Write O_i to HBM  (only one HBM write per Q block!)
</pre>
</div>
</div>
</div>

**Key insight:** The "online softmax" trick maintains running statistics so we can
compute exact softmax without storing the full $N \times N$ matrix. Each tile is
computed entirely in SRAM, with only Q, K, V reads and O writes going to HBM.

### IO complexity

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">IO Complexity Comparison</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Method</th>
<th style="padding:8px 16px; text-align:left;">HBM Reads/Writes</th>
<th style="padding:8px 16px; text-align:left;">Memory</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Standard attention</td>
<td style="padding:8px 16px;">$O(N^2 d + N^2)$</td>
<td style="padding:8px 16px;">$O(N^2)$</td>
</tr>
<tr style="background:#2d6a4f; color:white;">
<td style="padding:8px 16px;"><b>FlashAttention</b></td>
<td style="padding:8px 16px;">$O(N^2 d^2 / M)$</td>
<td style="padding:8px 16px;">$O(N)$</td>
</tr>
</table>
<div style="margin-top:8px; color:#ccc; font-size:12px;">
$M$ = SRAM size. For typical $d = 128$ and $M = 100$KB, FlashAttention does
$\sim$5-9x fewer HBM accesses. Wall-clock speedup: 2-4x on A100.
</div>
</div>
</div>

### FlashAttention-2 improvements

- Better **work partitioning** between GPU thread blocks (reduce non-matmul FLOPs)
- Parallelism over the **sequence length** dimension (not just batch/heads)
- ~2x faster than FlashAttention-1, reaching 50-73% of theoretical matmul FLOPS

### FlashAttention-3 (Hopper GPUs)

- Exploits **asynchronous execution** (TMA + WGMMA on H100)
- **FP8 support** for even higher throughput
- Intra-warp pipelining: overlap GEMM and softmax computation

---

## 2. Quantization

### Why quantize?

A 70B parameter model in fp16 requires $70 \times 10^9 \times 2 = 140$ GB -- more than
a single A100 (80GB). Quantization reduces weight (and optionally activation) precision
to fit larger models on fewer GPUs and increase throughput.

### Quantization methods comparison

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Quantization Methods Comparison</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 12px; text-align:left;">Method</th>
<th style="padding:8px 12px; text-align:left;">What's quantized</th>
<th style="padding:8px 12px; text-align:left;">Precision</th>
<th style="padding:8px 12px; text-align:left;">Calibration</th>
<th style="padding:8px 12px; text-align:left;">Key idea</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">GPTQ</td>
<td style="padding:8px 12px;">Weights only</td>
<td style="padding:8px 12px;">INT4 / INT3</td>
<td style="padding:8px 12px;">Post-training (128 samples)</td>
<td style="padding:8px 12px;">Layer-wise OBS: quantize columns sequentially, compensate error in remaining columns</td>
</tr>
<tr>
<td style="padding:8px 12px;">AWQ</td>
<td style="padding:8px 12px;">Weights only</td>
<td style="padding:8px 12px;">INT4</td>
<td style="padding:8px 12px;">Post-training</td>
<td style="padding:8px 12px;">Protect salient weights (1% channels carrying most activation magnitude) by per-channel scaling before quantization</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">Weight-only INT4</td>
<td style="padding:8px 12px;">Weights only</td>
<td style="padding:8px 12px;">INT4</td>
<td style="padding:8px 12px;">RTN (round-to-nearest)</td>
<td style="padding:8px 12px;">Simplest: group-wise round-to-nearest with scale/zero-point per group (e.g., 128 elements)</td>
</tr>
<tr>
<td style="padding:8px 12px;">W8A8</td>
<td style="padding:8px 12px;">Weights + activations</td>
<td style="padding:8px 12px;">INT8 / FP8</td>
<td style="padding:8px 12px;">Post-training or QAT</td>
<td style="padding:8px 12px;">Quantize both W and A to 8-bit. Enables INT8 GEMM on tensor cores. SmoothQuant migrates difficulty from activations to weights.</td>
</tr>
</table>
</div>
</div>

### GPTQ deep-dive

Based on Optimal Brain Surgeon (OBS). For each layer:

1. Compute Hessian $H = 2X^TX$ from calibration data (128 samples typical)
2. For each column $j$ (in order):
   - Quantize weight $w_j$ to nearest quantized value $\hat{w}_j$
   - Compute quantization error: $\delta_j = w_j - \hat{w}_j$
   - **Compensate** remaining columns: $W_{:, j+1:} \mathrel{-}= \delta_j \cdot \frac{H_{j, j+1:}}{H_{j,j}}$
3. This sequential error compensation keeps the layer output close to fp16 output

**Why GPTQ works well:** The Hessian-based compensation means each quantization error is
optimally distributed across remaining weights, not just accumulated.

### AWQ deep-dive

Key observation: not all weights are equally important. ~1% of weight channels correspond
to large activation magnitudes (salient channels). Quantizing these causes disproportionate error.

AWQ solution:
1. Find salient channels: sort by activation magnitude, top 1% are "salient"
2. Apply per-channel scaling: $s_j = \max(|X_j|)^\alpha$ with $\alpha \approx 0.5$
3. Scale weights: $W' = W \cdot \text{diag}(s)$, quantize $W'$
4. Absorb scaling into previous layer's output (no runtime overhead)

**AWQ vs GPTQ:**
- AWQ is faster to quantize (no sequential column processing)
- AWQ often has better quality at INT4 (protects the channels that matter most)
- GPTQ has more theoretical backing (OBS framework)

### SmoothQuant (for W8A8)

Activations have outlier channels that are hard to quantize. SmoothQuant migrates the
quantization difficulty from activations to weights:

$$Y = (X \text{diag}(s)^{-1}) \cdot (\text{diag}(s) W) = \hat{X} \hat{W}$$

Choose $s$ to balance the per-channel ranges: $s_j = \max(|X_j|)^\alpha / \max(|W_j|)^{1-\alpha}$.
After smoothing, both $\hat{X}$ and $\hat{W}$ have manageable ranges for INT8 quantization.

---

## 3. Serving Optimization

### 3.1 KV-Cache

During autoregressive generation, each new token attends to all previous tokens.
Without caching, we recompute all keys and values at every step: $O(N^2)$ total compute
for $N$ tokens.

**KV-Cache:** Store computed K, V tensors for past tokens. Each new token only computes
its own Q, K, V and attends to cached K, V.

- Compute savings: from $O(N^2 d)$ to $O(Nd)$ per step
- Memory cost: $2 \times L \times N \times H \times d \times \text{bytes}$ (2 for K and V, $L$ layers, $H$ heads)
- For Llama-70B at 4096 tokens: ~10 GB of KV-cache per request (fp16)

### 3.2 KV-Cache Quantization

KV-cache is the biggest memory consumer during inference. Quantizing it:

- **INT8 KV-cache:** Halves memory with minimal quality loss (per-token quantization)
- **INT4 KV-cache:** 4x reduction, slight quality degradation on long contexts
- **Per-head vs per-token quantization:** Per-head is simpler; per-token adapts better to outliers

### 3.3 PagedAttention (vLLM)

**Problem:** KV-cache is allocated as contiguous memory per request. With variable-length
sequences, this causes **internal fragmentation** (allocated but unused memory) and prevents
sharing prefixes between requests.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">PagedAttention (vLLM)</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
Traditional KV-cache:
  Request 1: [KKKKKKKK-------]  (8 tokens, 15 slots allocated = 7 wasted)
  Request 2: [KKKK-----------]  (4 tokens, 15 slots allocated = 11 wasted)
  Internal fragmentation: ~60% memory wasted

PagedAttention (virtual memory for KV-cache):
  Physical blocks: [B0][B1][B2][B3][B4][B5]...
  Request 1 page table: B0->B2->B5  (3 blocks, no waste)
  Request 2 page table: B1->B3      (2 blocks, no waste)

  Benefits:
  - Near-zero fragmentation (block-level granularity)
  - Copy-on-write for shared prefixes (beam search, system prompts)
  - Dynamic allocation: no pre-reservation needed
</pre>
</div>
</div>
</div>

**Impact:** vLLM achieves 2-4x higher throughput than HuggingFace text-generation-inference
by reducing KV-cache memory waste from ~60% to ~4%.

### 3.4 Continuous Batching

**Problem:** Traditional batching waits for all requests in a batch to finish before
processing new ones. Short requests waste GPU cycles waiting for long ones.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Static vs Continuous Batching</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
Static batching:
  Step 1: [A1][B1][C1]  -- 3 requests start together
  Step 2: [A2][B2][C2]
  Step 3: [A3][--][C3]  -- B finished at step 2, slot wasted
  Step 4: [A4][--][--]  -- C finished at step 3, slot wasted
  Step 5: [A5][--][--]  -- GPU 67% idle!
  --> New request D must wait for entire batch to finish

Continuous batching (iteration-level scheduling):
  Step 1: [A1][B1][C1]
  Step 2: [A2][B2][C2]
  Step 3: [A3][D1][C3]  -- B done, D immediately fills slot
  Step 4: [A4][D2][E1]  -- C done, E immediately fills slot
  Step 5: [A5][D3][E2]  -- GPU always full!
  --> No idle slots, new requests start immediately
</pre>
</div>
</div>
</div>

**Implementation:** Orca (2022) introduced iteration-level scheduling. Each decode step,
the scheduler can add/remove requests from the active batch. Combined with PagedAttention,
this maximizes GPU utilization.

### 3.5 Speculative Decoding

**Problem:** Autoregressive decoding is inherently sequential -- each token depends on the
previous one. The GPU is underutilized because generating one token uses the same memory
bandwidth as generating many.

**Idea:** Use a small **draft model** to generate $K$ candidate tokens quickly, then
verify all $K$ tokens in **parallel** with the large target model.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Speculative Decoding</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
Standard decoding (1 token per forward pass):
  Step 1: "The" -> target model -> "cat"
  Step 2: "The cat" -> target model -> "sat"
  Step 3: "The cat sat" -> target model -> "on"
  Total: 3 forward passes of target model

Speculative decoding:
  Draft step: "The" -> draft model -> "cat sat on" (3 tokens, fast)
  Verify step: "The [cat sat on]" -> target model (1 forward pass!)
    - Verify each: P_target("cat"|"The") >= P_draft("cat"|"The")? YES
    - P_target("sat"|"The cat") >= P_draft("sat"|"The cat")? YES
    - P_target("on"|"The cat sat") >= P_draft("on"|"The cat sat")? YES
  All accepted! 3 tokens from 1 target forward pass.

  If token 2 rejected: keep tokens before rejection, resample from target.
  Acceptance rate: ~70-90% for well-matched draft models.
</pre>
</div>
</div>
</div>

**Key properties:**
- **Lossless:** The output distribution is identical to the target model (rejection sampling ensures this)
- **Speedup:** $\sim K \times \text{acceptance\_rate}$ tokens per target forward pass
- Typical: 2-3x speedup with $K = 5$ and 70-80% acceptance rate
- **Draft model:** Can be a smaller version (e.g., 7B draft for 70B target), a quantized version, or even a simple n-gram model

### 3.6 Serving stack comparison

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">LLM Serving Frameworks</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 12px; text-align:left;">Framework</th>
<th style="padding:8px 12px; text-align:left;">Key feature</th>
<th style="padding:8px 12px; text-align:left;">Quantization</th>
<th style="padding:8px 12px; text-align:left;">Batching</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;"><b>vLLM</b></td>
<td style="padding:8px 12px;">PagedAttention</td>
<td style="padding:8px 12px;">GPTQ, AWQ, FP8</td>
<td style="padding:8px 12px;">Continuous</td>
</tr>
<tr>
<td style="padding:8px 12px;">TensorRT-LLM</td>
<td style="padding:8px 12px;">NVIDIA kernel fusion</td>
<td style="padding:8px 12px;">INT4/INT8/FP8</td>
<td style="padding:8px 12px;">In-flight batching</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">TGI (HuggingFace)</td>
<td style="padding:8px 12px;">Easy deployment</td>
<td style="padding:8px 12px;">GPTQ, bitsandbytes</td>
<td style="padding:8px 12px;">Continuous</td>
</tr>
<tr>
<td style="padding:8px 12px;">SGLang</td>
<td style="padding:8px 12px;">RadixAttention (prefix caching)</td>
<td style="padding:8px 12px;">AWQ, FP8</td>
<td style="padding:8px 12px;">Continuous</td>
</tr>
</table>
</div>
</div>

---

## 4. Project Narrative Mapping

> Map your real project experience to Adobe interview framing. The goal is to show
> that you have hands-on experience with the concepts Adobe cares about, even if
> you used them in a different context.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Experience -> Adobe Interview Framing</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Your Experience</th>
<th style="padding:8px 16px; text-align:left;">Adobe-Relevant Topic</th>
<th style="padding:8px 16px; text-align:left;">How to Frame It</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Operator fusion in inference pipeline</td>
<td style="padding:8px 16px;">FlashAttention kernel design</td>
<td style="padding:8px 16px;">"I optimized inference by fusing attention operators, similar to how FlashAttention fuses QKV computation to reduce HBM round-trips. I understand the memory hierarchy tradeoffs."</td>
</tr>
<tr>
<td style="padding:8px 16px;">Model compression / pruning work</td>
<td style="padding:8px 16px;">GPTQ / AWQ quantization</td>
<td style="padding:8px 16px;">"I applied weight quantization to deploy models on resource-constrained hardware. I can discuss the tradeoff between GPTQ (Hessian-based compensation) and AWQ (salience-aware scaling)."</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">HW-aware optimization</td>
<td style="padding:8px 16px;">KV-cache optimization</td>
<td style="padding:8px 16px;">"I profiled GPU memory usage and identified KV-cache as the bottleneck. I can discuss PagedAttention's virtual memory approach and KV-cache quantization strategies."</td>
</tr>
<tr>
<td style="padding:8px 16px;">Batch processing pipeline</td>
<td style="padding:8px 16px;">Continuous batching / serving</td>
<td style="padding:8px 16px;">"I designed batch processing systems that dynamically schedule work to maximize throughput, analogous to continuous batching in LLM serving."</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Multi-model inference pipeline</td>
<td style="padding:8px 16px;">Speculative decoding</td>
<td style="padding:8px 16px;">"I built cascading inference pipelines where a fast model triages and a large model handles hard cases -- the same draft/verify paradigm as speculative decoding."</td>
</tr>
<tr>
<td style="padding:8px 16px;">Distributed training with mixed precision</td>
<td style="padding:8px 16px;">FP8 training / inference</td>
<td style="padding:8px 16px;">"I used mixed-precision training (fp16/bf16) to double throughput. FP8 extends this further, and I understand the loss scaling and dynamic range challenges."</td>
</tr>
</table>
</div>
</div>

### How to use this table in interviews

1. **Listen for the keyword** in the interviewer's question
2. **Lead with your experience** ("In my project, I...")
3. **Bridge to the Adobe concept** ("This is similar to how FlashAttention...")
4. **Show depth** by discussing tradeoffs or limitations you encountered
5. **Connect to Adobe's scale** ("At Adobe's scale with Firefly, this becomes even more critical because...")

---

## 5. Common Misunderstandings (Error Corrections)

### Misunderstanding 1: "FlashAttention reduces the number of FLOPs"
**Correction:** FlashAttention performs the **same number of FLOPs** as standard attention
(actually slightly more due to recomputation in the backward pass). The speedup comes
entirely from reducing **HBM I/O** -- the bottleneck is memory bandwidth, not compute.
FlashAttention is IO-aware, not compute-efficient.

### Misunderstanding 2: "Quantization always degrades model quality significantly"
**Correction:** INT4 weight-only quantization (GPTQ, AWQ) typically loses <1% on benchmarks
for models >7B parameters. The key insight is that larger models are more robust to
quantization because individual weight values matter less when there are billions of them.
The quality gap narrows with model scale.

### Misunderstanding 3: "Speculative decoding changes the output distribution"
**Correction:** Speculative decoding with proper rejection sampling produces the **exact
same distribution** as standard autoregressive decoding from the target model. The draft
model only proposes candidates -- rejected tokens are resampled from the corrected
distribution. This is provably lossless (see Leviathan et al., 2023).

### Misunderstanding 4: "KV-cache is just an optimization, you can skip it"
**Correction:** Without KV-cache, generating $N$ tokens requires $O(N^2)$ total compute
(recomputing all attention at each step). With KV-cache, it is $O(N)$ per step.
For a 1000-token generation, that is 1000x compute difference. KV-cache is not optional
for practical LLM serving -- the question is how to manage it efficiently
(PagedAttention, quantization, eviction policies).

### Misunderstanding 5: "Continuous batching means larger batch sizes"
**Correction:** Continuous batching is about **scheduling granularity**, not batch size.
Static batching processes a fixed batch until all requests complete. Continuous batching
allows per-iteration scheduling: finished requests leave and new ones join at each decode
step. This eliminates idle slots, increasing throughput by 2-4x without changing the
maximum batch size.

---

## Self-Check Questions

- [ ] **Q1:** Draw the FlashAttention tiling algorithm. Why does it reduce HBM I/O from $O(N^2)$ to $O(N^2 d^2/M)$? What is the "online softmax" trick?
- [ ] **Q2:** Compare GPTQ vs AWQ: what calibration data does each need? How does GPTQ compensate for quantization error? Why does AWQ focus on "salient" channels?
- [ ] **Q3:** Explain PagedAttention. How does it solve KV-cache fragmentation? How does copy-on-write help with beam search?
- [ ] **Q4:** Describe speculative decoding step by step. Why is it provably lossless? What determines the acceptance rate?
- [ ] **Q5:** You have a 70B model and 2x A100-80GB GPUs. Walk through the inference optimization stack you would deploy (quantization + serving framework + batching strategy).

---

## Quick Reference Card

<pre style="background:#111; padding:12px; border-radius:4px; color:#ccc; font-size:13px;">
FlashAttention: Tiled attention in SRAM. Never materializes N x N matrix.
    IO: O(N^2 d^2 / M) vs standard O(N^2 d + N^2). Memory: O(N) vs O(N^2).
    Key trick: online softmax (running max + sum). Same FLOPs, fewer HBM trips.
    FA2: better parallelism. FA3: async execution + FP8 on Hopper GPUs.

Quantization:
    GPTQ: OBS-based, column-sequential, Hessian compensation. INT4, 128 calibration samples.
    AWQ: protect 1% salient channels via per-channel scaling. Faster than GPTQ.
    W8A8: SmoothQuant migrates outliers from activations to weights. INT8 GEMM.
    Rule of thumb: INT4 weight-only loses <1% for models >7B.

KV-Cache: 2 * L * N * H * d bytes. Biggest memory consumer at inference time.
    PagedAttention: virtual memory for KV-cache. Blocks, page tables, CoW.
    vLLM: 2-4x throughput vs HF TGI via near-zero fragmentation.

Continuous Batching: iteration-level scheduling. No idle slots.
    Finished requests leave, new ones join at each decode step.

Speculative Decoding: Draft model proposes K tokens, target verifies in 1 pass.
    Lossless (rejection sampling). ~2-3x speedup with 70-80% acceptance rate.
    Draft = smaller model, quantized model, or n-gram model.

Project Mapping: operator fusion->FlashAttention, compression->GPTQ/AWQ,
    HW profiling->KV-cache, batch pipeline->continuous batching,
    cascade inference->speculative decoding, mixed precision->FP8.
</pre>
"""


def main() -> None:
    """Insert the Inference Optimization + Project Narrative study note into mle_prep.db."""
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
