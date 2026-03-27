"""Seed script: Insert Adobe Prep Day3 -- Distributed Training study note.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day3: Distributed Training (DP/TP/PP/FSDP)"

CONTENT = r"""# Distributed Training: DP / TP / PP / FSDP (Adobe Prep Day 3)

> Training large models on multiple GPUs requires splitting work across devices.
> Four parallelism strategies exist -- each splits a different axis. Master when
> to use which, how they compose into 3D parallelism, and the memory math.

---

## 1. The Four Parallelism Strategies -- Overview

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:16px; font-size:16px; color:#fff; font-weight:bold;">How Each Strategy Splits Work</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Strategy</th>
<th style="padding:8px 16px; text-align:left;">What is split</th>
<th style="padding:8px 16px; text-align:left;">Across</th>
<th style="padding:8px 16px; text-align:left;">Communication</th>
</tr>
<tr style="background:#4a90d9; color:white;">
<td style="padding:8px 16px;">Data Parallel (DP)</td>
<td style="padding:8px 16px;">Data (mini-batch)</td>
<td style="padding:8px 16px;">All GPUs</td>
<td style="padding:8px 16px;">AllReduce gradients</td>
</tr>
<tr style="background:#6b4c9a; color:white;">
<td style="padding:8px 16px;">Tensor Parallel (TP)</td>
<td style="padding:8px 16px;">Weight matrices (intra-layer)</td>
<td style="padding:8px 16px;">GPUs within a node</td>
<td style="padding:8px 16px;">AllReduce activations</td>
</tr>
<tr style="background:#2d6a4f; color:white;">
<td style="padding:8px 16px;">Pipeline Parallel (PP)</td>
<td style="padding:8px 16px;">Layers (inter-layer)</td>
<td style="padding:8px 16px;">Across nodes</td>
<td style="padding:8px 16px;">Point-to-point activations</td>
</tr>
<tr style="background:#d4a017; color:black;">
<td style="padding:8px 16px;">FSDP / ZeRO</td>
<td style="padding:8px 16px;">Parameters + optimizer states</td>
<td style="padding:8px 16px;">All GPUs</td>
<td style="padding:8px 16px;">AllGather params, ReduceScatter grads</td>
</tr>
</table>
</div>
</div>

---

## 2. Data Parallelism (DP)

The simplest strategy: every GPU holds a **full copy** of the model and processes a different mini-batch slice.

### How it works

1. **Replicate** the model on $N$ GPUs
2. **Split** the global batch $B$ into $N$ micro-batches of size $B/N$
3. Each GPU computes forward + backward on its micro-batch
4. **AllReduce** gradients across all GPUs (sum and average)
5. Each GPU updates its local copy with the averaged gradient

### AllReduce

$$\bar{g} = \frac{1}{N} \sum_{i=1}^{N} g_i$$

The AllReduce operation ensures every GPU ends up with the same averaged gradient $\bar{g}$. Implemented as ReduceScatter + AllGather (ring-based) for bandwidth efficiency.

**Communication cost per step:**

$$\text{AllReduce volume} = 2 \cdot (N-1)/N \cdot |\theta| \approx 2|\theta| \quad \text{(for large } N \text{)}$$

where $|\theta|$ is the total parameter count. The factor of 2 comes from ReduceScatter + AllGather.

### Limitations

- **Memory**: Each GPU must hold the full model + optimizer states + activations
- For a model with $P$ parameters in FP16 + AdamW optimizer:
  - Parameters: $2P$ bytes (FP16)
  - Gradients: $2P$ bytes (FP16)
  - Optimizer states: $12P$ bytes (FP32 params + FP32 momentum + FP32 variance)
  - **Total: $16P$ bytes per GPU** (same on every GPU -- wasteful!)
- Does not scale beyond models that fit on a single GPU

### PyTorch DDP

```python
# PyTorch DistributedDataParallel
model = DDP(model, device_ids=[local_rank])
# Automatically: gradient AllReduce overlapped with backward pass
```

Key optimization: **gradient bucketing** -- overlaps communication with computation by starting AllReduce on earlier layers while later layers are still computing backward.

---

## 3. Tensor Parallelism (TP)

Splits individual **weight matrices** across GPUs within a single layer. Best for intra-node (fast NVLink interconnect).

### MLP column-row split

For a 2-layer MLP: $Y = \text{GeLU}(XA) \cdot B$

**Column parallel (first linear):**

Split $A$ column-wise across $N$ GPUs:

$$A = [A_1 | A_2 | \ldots | A_N]$$

Each GPU $i$ computes $Y_i = \text{GeLU}(X A_i)$ independently. GeLU is element-wise, so no communication needed here.

**Row parallel (second linear):**

Split $B$ row-wise:

$$B = \begin{bmatrix} B_1 \\ B_2 \\ \vdots \\ B_N \end{bmatrix}$$

Each GPU $i$ computes $Z_i = Y_i B_i$ (partial result). Then **AllReduce** to get the final output:

$$Z = \sum_{i=1}^{N} Z_i$$

**Communication:** 1 AllReduce per MLP block (after the row-parallel layer).

### Attention head split

Multi-head attention is naturally parallelizable:

- $h$ attention heads split across $N$ GPUs ($h/N$ heads per GPU)
- Each GPU computes $Q_i, K_i, V_i$ projections and attention for its heads
- After attention, the output projections are row-parallel
- **1 AllReduce** per attention block

### Communication pattern per transformer layer

$$\text{TP comm per layer} = 2 \times \text{AllReduce}(d_{\text{model}}) \quad \text{(1 for MLP + 1 for attention)}$$

### When to use TP

- **Within a node** where NVLink provides 600+ GB/s bandwidth
- Typical TP degree: 2, 4, or 8 (matching GPUs per node)
- Cross-node TP is usually too slow (network bandwidth is 10-100x lower than NVLink)

---

## 4. Pipeline Parallelism (PP)

Splits the model **layer-wise** across GPUs. GPU 0 gets layers 0-9, GPU 1 gets layers 10-19, etc.

### Naive pipeline (bubble problem)

With $N$ pipeline stages and 1 micro-batch:

```
GPU 0: [Fwd]...........[Bwd]
GPU 1:      [Fwd]...........[Bwd]
GPU 2:           [Fwd]...........[Bwd]
GPU 3:                [Fwd]...........[Bwd]
                                          ^^^ Lots of idle time (bubble)
```

**Bubble fraction** (naive):

$$\text{Bubble} = \frac{N - 1}{N} \quad \text{(e.g., 75\% idle for 4 stages!)}$$

### Micro-batch pipelining (GPipe / PipeDream)

Split the mini-batch into $M$ micro-batches and pipeline them:

```
GPU 0: [F1][F2][F3][F4]............[B4][B3][B2][B1]
GPU 1:     [F1][F2][F3][F4]....[B4][B3][B2][B1]
GPU 2:         [F1][F2][F3][F4][B4][B3][B2][B1]
GPU 3:             [F1][F2][F3][F4][B3][B2][B1]
```

**Reduced bubble fraction:**

$$\text{Bubble} = \frac{N - 1}{N + M - 1}$$

With $M \gg N$, bubble fraction approaches 0. Typical: $M = 4N$ gives $\sim 20\%$ bubble.

### Communication

- Only **point-to-point** between adjacent stages (activation tensors)
- Much less bandwidth than AllReduce -- good for cross-node
- Communication volume: activation size of the boundary layer

### Variants

| Method | Key feature |
|--------|-------------|
| **GPipe** | All-forward then all-backward, gradient accumulation over micro-batches |
| **PipeDream-1F1B** | Interleave 1 forward + 1 backward per step, reduces peak memory |
| **Interleaved PP** | Assign non-contiguous layers to stages (virtual stages) |

---

## 5. FSDP / ZeRO (Fully Sharded Data Parallelism)

FSDP addresses the memory redundancy of standard DP by **sharding** parameters, gradients, and optimizer states across GPUs.

### ZeRO stages

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">ZeRO Memory per GPU ($P$ params, $N$ GPUs, FP16 + AdamW)</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Stage</th>
<th style="padding:8px 16px; text-align:left;">What is sharded</th>
<th style="padding:8px 16px; text-align:left;">Memory per GPU</th>
<th style="padding:8px 16px; text-align:left;">vs Baseline (16P)</th>
</tr>
<tr>
<td style="padding:8px 16px;">Baseline (DDP)</td>
<td style="padding:8px 16px;">Nothing</td>
<td style="padding:8px 16px;">$16P$ bytes</td>
<td style="padding:8px 16px;">1x</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">ZeRO Stage 1</td>
<td style="padding:8px 16px;">Optimizer states</td>
<td style="padding:8px 16px;">$4P + 12P/N$ bytes</td>
<td style="padding:8px 16px;">~4x reduction at $N=64$</td>
</tr>
<tr>
<td style="padding:8px 16px;">ZeRO Stage 2</td>
<td style="padding:8px 16px;">Optimizer + gradients</td>
<td style="padding:8px 16px;">$2P + (2P + 12P)/N$ bytes</td>
<td style="padding:8px 16px;">~8x at $N=64$</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">ZeRO Stage 3 (FSDP)</td>
<td style="padding:8px 16px;">Optimizer + gradients + parameters</td>
<td style="padding:8px 16px;">$16P/N$ bytes</td>
<td style="padding:8px 16px;">$N$x reduction</td>
</tr>
</table>
</div>
</div>

### ZeRO Stage 1: Shard optimizer states

- Each GPU stores $1/N$ of the optimizer states (momentum, variance)
- Parameters and gradients are still fully replicated
- After AllReduce of gradients, each GPU updates only its $1/N$ shard of optimizer states
- Then AllGather to broadcast updated parameters

### ZeRO Stage 2: + Shard gradients

- Gradients are also sharded: use **ReduceScatter** instead of AllReduce
- Each GPU only keeps the $1/N$ gradient shard it needs for its optimizer shard
- Eliminates gradient memory redundancy

### ZeRO Stage 3 / FSDP: + Shard parameters

- Parameters themselves are sharded -- each GPU holds only $1/N$ of the weights
- **Forward pass:** AllGather parameters for each layer, compute, discard non-owned params
- **Backward pass:** AllGather parameters again, compute gradients, ReduceScatter gradients

**Communication (Stage 3):**

$$\text{Volume per step} = 3 \times |\theta| \quad \text{(1.5x more than DDP's } 2|\theta| \text{)}$$

Breakdown: AllGather in forward ($|\theta|$) + AllGather in backward ($|\theta|$) + ReduceScatter gradients ($|\theta|$).

### PyTorch FSDP

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,  # Stage 3
    auto_wrap_policy=transformer_auto_wrap_policy,
    mixed_precision=MixedPrecision(param_dtype=torch.float16),
)
```

### FSDP vs DDP trade-off

| Aspect | DDP | FSDP |
|--------|-----|------|
| **Memory per GPU** | $16P$ | $16P/N$ |
| **Communication** | $2|\theta|$ | $3|\theta|$ (1.5x more) |
| **Implementation** | Simple | More complex (AllGather/ReduceScatter scheduling) |
| **Best for** | Model fits on 1 GPU | Model too large for 1 GPU |

---

## 6. Selection Guide: 13B Model on 8x A100 80GB

### Memory estimation formula

For a model with $P$ parameters, mixed-precision training with AdamW:

$$\text{Memory per GPU} = \underbrace{2P}_{\text{FP16 params}} + \underbrace{2P}_{\text{FP16 grads}} + \underbrace{12P}_{\text{Adam states (FP32)}} + \underbrace{a \cdot B \cdot s \cdot h}_{\text{activations}}$$

where $a$ = number of layers, $B$ = micro-batch size, $s$ = sequence length, $h$ = hidden dimension.

### Worked example: 13B parameters

**Parameter memory (no sharding):**
- $P = 13 \times 10^9$
- Full: $16P = 16 \times 13\text{B} = 208\text{ GB}$ -- does NOT fit on a single A100 80GB

**With FSDP (ZeRO Stage 3) on 8 GPUs:**
- $16P / 8 = 26\text{ GB per GPU}$ for params + optimizer
- Leaves ~54 GB for activations + buffers -- comfortably fits

**Decision tree:**

```
Can the model + optimizer fit on 1 GPU?
  YES -> Use DDP (simplest)
  NO  -> Does it fit with FSDP across available GPUs?
    YES -> Use FSDP (ZeRO Stage 3)
    NO  -> Add Pipeline Parallelism (split layers across nodes)
           + Tensor Parallelism (within node) -> 3D Parallelism
```

### Activation memory estimation

For a transformer layer:

$$\text{Activation memory per layer} \approx 2 \cdot B \cdot s \cdot h \cdot (10 + \frac{24s}{h})$$

For 13B model ($h = 5120$, $s = 2048$, $B = 1$):
- Per layer: $\approx 2 \times 1 \times 2048 \times 5120 \times 10 \approx 200\text{ MB}$
- 40 layers: $\approx 8\text{ GB}$

With **activation checkpointing** (recompute instead of store): reduces to $\sqrt{L}$ layers stored, where $L$ = number of layers. For 40 layers: store ~6 layers, save ~85% activation memory.

---

## 7. 3D Parallelism

Production systems (GPT-3, PaLM, Llama 3 405B) combine all three strategies:

### Typical configuration

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">3D Parallelism Layout (64 GPUs = 8 nodes x 8 GPUs/node)</div>
<div style="color:#aaa; margin-bottom:12px;">
TP=8 (within node, NVLink) x PP=4 (across nodes) x DP=2 (remaining)
</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<div>Node 0 (8 GPUs): TP group for pipeline stage 0, DP replica 0</div>
<div>Node 1 (8 GPUs): TP group for pipeline stage 0, DP replica 1</div>
<div>Node 2 (8 GPUs): TP group for pipeline stage 1, DP replica 0</div>
<div>Node 3 (8 GPUs): TP group for pipeline stage 1, DP replica 1</div>
<div>Node 4 (8 GPUs): TP group for pipeline stage 2, DP replica 0</div>
<div>Node 5 (8 GPUs): TP group for pipeline stage 2, DP replica 1</div>
<div>Node 6 (8 GPUs): TP group for pipeline stage 3, DP replica 0</div>
<div>Node 7 (8 GPUs): TP group for pipeline stage 3, DP replica 1</div>
</div>
<div style="color:#888; margin-top:12px; font-size:12px;">
Total: 64 GPUs | TP*PP*DP = 8*4*2 = 64
</div>
</div>
</div>

### Why this ordering?

| Strategy | Bandwidth needs | Best interconnect | Assigned to |
|----------|----------------|-------------------|-------------|
| **TP** | Highest (AllReduce per layer) | NVLink (600+ GB/s) | Intra-node |
| **PP** | Medium (activation P2P) | Inter-node network | Across nodes |
| **DP/FSDP** | Lower (AllReduce per step) | Inter-node network | Remaining GPUs |

**Key principle:** Place the most communication-intensive parallelism on the fastest interconnect.

### Real-world examples

| Model | Params | GPUs | TP | PP | DP |
|-------|--------|------|----|----|-----|
| GPT-3 | 175B | 1024 A100 | 8 | 16 | 8 |
| PaLM | 540B | 6144 TPU | 8 | 12 | 64 |
| Llama 3 405B | 405B | 16K H100 | 8 | 16 | 128 |
| Llama 2 70B | 70B | 256 A100 | 8 | 4 | 8 |

---

## 8. Common Misunderstandings (Error Corrections)

### Misunderstanding 1: "FSDP is the same as model parallelism"
**Correction:** FSDP is a memory-efficient variant of *data parallelism*. Each GPU still processes different data. The model parameters are sharded for memory savings but are AllGathered before each forward/backward computation. True model parallelism (TP/PP) splits the computation itself.

### Misunderstanding 2: "Tensor Parallelism works well across nodes"
**Correction:** TP requires AllReduce of activations *twice per layer* (once for attention, once for MLP). This is extremely bandwidth-intensive. Across nodes with ~50 GB/s network (vs ~600 GB/s NVLink), TP becomes a severe bottleneck. TP is almost always intra-node only.

### Misunderstanding 3: "Pipeline parallelism is free -- just split layers"
**Correction:** The pipeline bubble is a real efficiency loss. With 4 pipeline stages and 4 micro-batches, bubble fraction is $3/7 \approx 43\%$. You need $M \gg N$ micro-batches to amortize the bubble, which increases memory pressure (more activations stored simultaneously).

### Misunderstanding 4: "ZeRO Stage 3 has the same communication cost as DDP"
**Correction:** ZeRO Stage 3 requires ~$3|\theta|$ communication per step vs DDP's ~$2|\theta|$. The extra $|\theta|$ comes from AllGather in the forward pass. This is a 50% communication overhead -- acceptable because it enables training models that don't fit in DDP.

### Misunderstanding 5: "You always want the maximum degree of parallelism"
**Correction:** Higher parallelism degree means smaller per-GPU batch size and more communication overhead. There's an optimal trade-off. For example, TP=8 with 8-way attention heads is natural, but TP=16 would split heads sub-optimally and add cross-node communication. Over-parallelizing can *reduce* throughput.

---

## Self-Check Questions

- [ ] **Q1:** For a 13B parameter model on 8x A100 80GB GPUs, calculate the memory per GPU with (a) DDP, (b) ZeRO Stage 1, (c) ZeRO Stage 3. Which stages fit?
- [ ] **Q2:** Draw the pipeline bubble for 4 stages and 8 micro-batches using 1F1B scheduling. Calculate the bubble fraction.
- [ ] **Q3:** Explain why Tensor Parallelism splits MLP column-wise first, then row-wise. What goes wrong if you do row-first then column?
- [ ] **Q4:** You have 128 H100 GPUs across 16 nodes (8 GPUs/node). Design the 3D parallelism layout for a 70B model. Justify each choice.

---

## Quick Reference Card

```
DP:    Full model on each GPU, AllReduce gradients. Memory: 16P per GPU.
TP:    Split weight matrices intra-layer. 2 AllReduce per transformer layer.
PP:    Split layers across GPUs. Bubble = (N-1)/(N+M-1). P2P comms only.
FSDP:  Shard params+grads+optimizer. Memory: 16P/N per GPU. Comms: 3|theta|.
ZeRO:  Stage1=shard optimizer, Stage2=+grads, Stage3=+params (=FSDP).
3D:    TP(intra-node, NVLink) x PP(cross-node) x DP(remaining).
Memory formula: 2P(params) + 2P(grads) + 12P(Adam) + activations.
Activation ckpt: Recompute instead of store. Saves ~sqrt(L)/L memory.
```
"""


def main() -> None:
    """Insert the Distributed Training study note into mle_prep.db."""
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
