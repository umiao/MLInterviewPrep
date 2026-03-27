"""Seed script: Insert Adobe Prep Day4 -- RoPE + Long Context + Video Generation note.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day4: RoPE + Long Context + Video Generation"

CONTENT = r"""# RoPE + Long Context + Video Generation (Adobe Prep Day 4)

> Positional encoding is how transformers know token order. RoPE is the modern
> standard -- understand its math, why it enables relative position awareness,
> and how it extends to long contexts. Video generation adds the temporal axis:
> know the core architectural choices Adobe cares about.

---

## 1. Positional Encoding -- Why It Matters

Transformers are **permutation-invariant** without positional information: attention
computes the same output regardless of token order. Positional encoding breaks this
symmetry by injecting position information into the representation.

### Key requirements for a good PE scheme

1. **Unique** encoding per position
2. **Bounded** values (no explosion at long positions)
3. **Relative distance** awareness (attention should depend on $m - n$, not absolute $m, n$)
4. **Extrapolation** to unseen lengths (train on 4K, infer on 32K+)

---

## 2. RoPE: Rotary Position Embedding

### Core idea

Instead of *adding* a position vector, RoPE **rotates** query and key vectors in 2D subspaces.
The rotation angle is proportional to the position index, so the dot product $q_m \cdot k_n$
depends only on the relative distance $m - n$.

### Mathematical formulation

For a $d$-dimensional embedding, group dimensions into $d/2$ pairs. Each pair $(x_{2i}, x_{2i+1})$
is treated as a 2D vector and rotated by angle $m \cdot \theta_i$:

$$\theta_i = \frac{1}{10000^{2i/d}}, \quad i = 0, 1, \ldots, d/2 - 1$$

The rotation for position $m$:

$$R_m = \begin{pmatrix} \cos(m\theta_0) & -\sin(m\theta_0) & & \\ \sin(m\theta_0) & \cos(m\theta_0) & & \\ & & \cos(m\theta_1) & -\sin(m\theta_1) \\ & & \sin(m\theta_1) & \cos(m\theta_1) \\ & & & & \ddots \end{pmatrix}$$

Applied to queries and keys:

$$\tilde{q}_m = R_m q_m, \quad \tilde{k}_n = R_n k_n$$

### Why the dot product depends only on $m - n$

$$\tilde{q}_m^T \tilde{k}_n = q_m^T R_m^T R_n k_n = q_m^T R_{n-m} k_n$$

This works because rotation matrices satisfy $R_m^T R_n = R_{n-m}$ (rotation by the difference).
The attention score between positions $m$ and $n$ is a function of the **relative distance** $m - n$,
not the absolute positions -- exactly what we want.

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">RoPE Rotation Diagram (2D subspace)</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
  Position m=0:  q0 = (x, y)        -- no rotation
  Position m=1:  q1 = rotate(q, theta)  -- rotate by theta
  Position m=2:  q2 = rotate(q, 2*theta) -- rotate by 2*theta
  ...
  Position m=k:  qk = rotate(q, k*theta) -- rotate by k*theta

  Dot product: q_m . k_n = f(q, k, m-n)
  (only depends on relative distance!)

  theta_i = 1 / 10000^(2i/d)
  Low-freq pairs (large i): slow rotation  -> capture long-range patterns
  High-freq pairs (small i): fast rotation -> capture local patterns
</pre>
</div>
</div>
</div>

### Efficient implementation (complex number trick)

Instead of building a sparse rotation matrix, RoPE can be computed element-wise:

$$\text{RoPE}(x_m) = x_m \odot \cos(m\theta) + \text{rotate\_half}(x_m) \odot \sin(m\theta)$$

where $\text{rotate\_half}$ swaps pairs and negates: $(x_0, x_1, x_2, x_3, \ldots) \to (-x_1, x_0, -x_3, x_2, \ldots)$.

<pre style="background:#111; padding:12px; border-radius:4px; color:#ccc; font-size:13px;">
# PyTorch-style implementation
def apply_rope(x, freqs_cos, freqs_sin):
    # x: (batch, seq_len, n_heads, head_dim)
    # freqs_cos, freqs_sin: (seq_len, head_dim/2)
    x_r = x.float().reshape(*x.shape[:-1], -1, 2)
    x_real, x_imag = x_r[..., 0], x_r[..., 1]
    # Rotation in 2D: (a+bi)(cos+sin*i) = (a*cos - b*sin) + (a*sin + b*cos)i
    out_real = x_real * freqs_cos - x_imag * freqs_sin
    out_imag = x_real * freqs_sin + x_imag * freqs_cos
    return torch.stack([out_real, out_imag], dim=-1).flatten(-2)
</pre>

---

## 3. PE Comparison Table

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Positional Encoding Methods Comparison</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 12px; text-align:left;">Method</th>
<th style="padding:8px 12px; text-align:left;">Type</th>
<th style="padding:8px 12px; text-align:left;">Relative?</th>
<th style="padding:8px 12px; text-align:left;">Extrapolation</th>
<th style="padding:8px 12px; text-align:left;">Used in</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">Sinusoidal (Vaswani 2017)</td>
<td style="padding:8px 12px;">Additive, fixed</td>
<td style="padding:8px 12px;">Weak (via dot product)</td>
<td style="padding:8px 12px;">Poor</td>
<td style="padding:8px 12px;">Original Transformer</td>
</tr>
<tr>
<td style="padding:8px 12px;">Learned Absolute</td>
<td style="padding:8px 12px;">Additive, learned</td>
<td style="padding:8px 12px;">No</td>
<td style="padding:8px 12px;">None (fixed max len)</td>
<td style="padding:8px 12px;">BERT, GPT-2</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">ALiBi</td>
<td style="padding:8px 12px;">Attention bias</td>
<td style="padding:8px 12px;">Yes (linear penalty)</td>
<td style="padding:8px 12px;">Good</td>
<td style="padding:8px 12px;">BLOOM, MPT</td>
</tr>
<tr>
<td style="padding:8px 12px;"><b>RoPE</b></td>
<td style="padding:8px 12px;">Multiplicative (rotation)</td>
<td style="padding:8px 12px;"><b>Yes (by construction)</b></td>
<td style="padding:8px 12px;">Moderate (needs scaling)</td>
<td style="padding:8px 12px;"><b>Llama, Mistral, Qwen, Gemma</b></td>
</tr>
</table>
</div>
</div>

**Why RoPE won:**
- Relative position encoding is a mathematical property, not an approximation
- No additional parameters (unlike learned PE)
- Compatible with KV-cache (rotation is per-token, no recomputation needed)
- Efficient: element-wise ops, no matrix multiplication overhead

**RoPE vs Sinusoidal:**
- Sinusoidal adds position vectors: $h_m = x_m + PE_m$. The dot product $h_m^T h_n$ contains cross terms
  $x_m^T PE_n + PE_m^T x_n + PE_m^T PE_n$ -- the relative signal is mixed with absolute terms.
- RoPE multiplies (rotates): the rotation cleanly factors out, giving pure relative dependence.

---

## 4. Long Context Methods

RoPE trained on length $L$ degrades at length $> L$ because the rotation angles become
out-of-distribution. Several methods extend the context window without full retraining.

### 4.1 Position Interpolation (PI)

**Idea:** Instead of extrapolating to unseen positions, **compress** positions to fit within
the trained range.

$$m' = m \cdot \frac{L_{\text{train}}}{L_{\text{target}}}$$

For example, to extend from 4K to 32K: scale all positions by $4096/32768 = 1/8$.
Position 32000 becomes position 4000 -- within the trained range.

**Pros:** Simple, effective with minimal fine-tuning (~1000 steps).
**Cons:** Compresses nearby positions, reducing local resolution.

### 4.2 NTK-aware Scaling

**Idea:** The problem with PI is it scales all frequencies equally. High-frequency components
(small $i$, responsible for local patterns) are hurt most by compression. NTK-aware scaling
modifies the **base frequency** instead:

$$\theta_i' = \frac{1}{(b \cdot \alpha)^{2i/d}} \quad \text{where } \alpha = \frac{L_{\text{target}}}{L_{\text{train}}}$$

This effectively:
- Keeps high-frequency dimensions (local patterns) mostly unchanged
- Stretches low-frequency dimensions (long-range patterns) to accommodate longer contexts

**Intuition:** Like changing the base of the number system rather than compressing all digits.

### 4.3 YaRN (Yet another RoPE extensioN)

**Idea:** Combines the best of PI and NTK with an attention-scaling factor. Divides RoPE
dimensions into three groups:

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">YaRN Dimension Grouping</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Frequency Group</th>
<th style="padding:8px 16px; text-align:left;">RoPE Dimensions</th>
<th style="padding:8px 16px; text-align:left;">Treatment</th>
</tr>
<tr style="background:#4a90d9; color:white;">
<td style="padding:8px 16px;">High frequency (local)</td>
<td style="padding:8px 16px;">Small $i$ (fast rotation)</td>
<td style="padding:8px 16px;">No interpolation (keep as-is)</td>
</tr>
<tr style="background:#6b4c9a; color:white;">
<td style="padding:8px 16px;">Medium frequency</td>
<td style="padding:8px 16px;">Mid $i$</td>
<td style="padding:8px 16px;">Blend of PI and NTK</td>
</tr>
<tr style="background:#2d6a4f; color:white;">
<td style="padding:8px 16px;">Low frequency (long-range)</td>
<td style="padding:8px 16px;">Large $i$ (slow rotation)</td>
<td style="padding:8px 16px;">Full PI interpolation</td>
</tr>
</table>
</div>
</div>

Plus an **attention temperature scaling** factor $\sqrt{t}$ to compensate for the entropy
increase at longer contexts:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d} \cdot \sqrt{t}}\right) V$$

**YaRN achieves the best extrapolation** with minimal fine-tuning and is used in
production models like Llama 3.1 (128K context).

### Long context methods summary

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Long Context Extension Methods</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 12px; text-align:left;">Method</th>
<th style="padding:8px 12px; text-align:left;">Approach</th>
<th style="padding:8px 12px; text-align:left;">Fine-tuning</th>
<th style="padding:8px 12px; text-align:left;">Quality</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;">Position Interpolation</td>
<td style="padding:8px 12px;">Linear position scaling</td>
<td style="padding:8px 12px;">~1K steps</td>
<td style="padding:8px 12px;">Good, loses local detail</td>
</tr>
<tr>
<td style="padding:8px 12px;">NTK-aware Scaling</td>
<td style="padding:8px 12px;">Base frequency adjustment</td>
<td style="padding:8px 12px;">~1K steps (or zero-shot)</td>
<td style="padding:8px 12px;">Better local preservation</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 12px;"><b>YaRN</b></td>
<td style="padding:8px 12px;">Per-dimension PI/NTK + attn temp</td>
<td style="padding:8px 12px;">~400 steps</td>
<td style="padding:8px 12px;"><b>Best overall</b></td>
</tr>
<tr>
<td style="padding:8px 12px;">Sliding Window + Global</td>
<td style="padding:8px 12px;">Local attention + sparse global</td>
<td style="padding:8px 12px;">Architecture change</td>
<td style="padding:8px 12px;">Good for very long (1M+)</td>
</tr>
</table>
</div>
</div>

---

## 5. Video Generation

Adobe is a leader in generative media (Firefly). Video generation extends image generation
along the **temporal axis** -- this is a core area for Adobe interviews.

### 5.1 Core challenge: temporal consistency

A video is a sequence of frames. Generating each frame independently (image model per frame)
produces flickering, inconsistent content. The key challenge:

**Maintain spatial quality per frame while ensuring temporal coherence across frames.**

### 5.2 Architecture overview

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Video Diffusion Architecture (Latent Video Diffusion)</div>
<div style="color:#ccc; text-align:left; padding:0 20px;">
<pre style="color:#ccc; font-size:13px;">
Input: text prompt + (optional) reference image/video

  Text Encoder (CLIP / T5)
         |
         v
  [3D VAE Encoder]  -- encodes video (T x H x W x 3) -> latent (T' x H' x W' x C)
         |              temporal + spatial compression
         v
  [Denoising Network]  -- iterative noise removal in latent space
  |  Spatial Attention  -- per-frame quality (from image model)
  |  Temporal Attention -- cross-frame consistency
  |  Cross-Attention    -- text conditioning
  |  (repeated L times)
         |
         v
  [3D VAE Decoder]  -- latent -> video frames
         |
         v
  Output: T frames of H x W video
</pre>
</div>
</div>
</div>

### 5.3 Key components

**3D VAE (Variational Autoencoder)**

Unlike image VAE (2D: H x W), video VAE compresses along all three axes:

- **Spatial** compression: $H \times W \to H/8 \times W/8$ (typical 8x)
- **Temporal** compression: $T \to T/4$ (typical 4x)
- Total compression: $4 \times 8 \times 8 = 256\text{x}$ reduction in tokens

This is critical for making video generation computationally feasible -- working in
pixel space would require $T \times H \times W$ tokens (millions for a short clip).

**Temporal attention**

Added to existing spatial attention blocks:

<pre style="background:#111; padding:12px; border-radius:4px; color:#ccc; font-size:13px;">
For each denoising step:
  For each layer:
    1. Spatial self-attention:  attend within each frame (H' x W' tokens)
    2. Temporal self-attention: attend across frames at each spatial location (T' tokens)
    3. Cross-attention:         condition on text embedding
</pre>

Temporal attention enables each spatial position to attend to the same position across
all frames -- enforcing consistency of objects, backgrounds, and motion.

**Motion modules**

Specialized temporal layers that model motion dynamics:
- Temporal convolutions (1D conv across time dimension)
- Temporal attention with relative position encoding
- Often initialized from pre-trained motion patterns

### 5.4 Sora / DiT Architecture

OpenAI's Sora introduced the **Diffusion Transformer (DiT)** approach for video:

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">DiT (Diffusion Transformer) Architecture</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Component</th>
<th style="padding:8px 16px; text-align:left;">Description</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Patchification</td>
<td style="padding:8px 16px;">Convert latent video into <b>spacetime patches</b> (3D patches: t x h x w)</td>
</tr>
<tr>
<td style="padding:8px 16px;">Backbone</td>
<td style="padding:8px 16px;">Standard Transformer (not U-Net!) with full self-attention over all patches</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Conditioning</td>
<td style="padding:8px 16px;">AdaLN-Zero: adaptive layer norm, conditioned on timestep + text</td>
</tr>
<tr>
<td style="padding:8px 16px;">Scaling</td>
<td style="padding:8px 16px;">Pure transformer scales with compute (like LLMs) -- key advantage over U-Net</td>
</tr>
</table>
</div>
</div>

**Why DiT matters:**
- Replaces U-Net with a plain Transformer -- benefits from the same scaling laws as LLMs
- Spacetime patches treat video as a sequence of 3D tokens -- unified spatial + temporal
- Variable resolution and duration via flexible patch counts
- Sora reportedly uses DiT at massive scale (~3B+ params) for minute-long videos

### 5.5 Key challenges in video generation

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<div style="margin-bottom:12px; font-size:16px; color:#fff; font-weight:bold;">Video Generation Challenges</div>
<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">
<tr style="border-bottom:1px solid #444;">
<th style="padding:8px 16px; text-align:left;">Challenge</th>
<th style="padding:8px 16px; text-align:left;">Why it's hard</th>
<th style="padding:8px 16px; text-align:left;">Current approach</th>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Temporal consistency</td>
<td style="padding:8px 16px;">Objects must persist and move coherently</td>
<td style="padding:8px 16px;">Temporal attention + 3D VAE</td>
</tr>
<tr>
<td style="padding:8px 16px;">Motion coherence</td>
<td style="padding:8px 16px;">Physics-plausible motion, no jitter</td>
<td style="padding:8px 16px;">Motion modules, temporal conv</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Memory / compute</td>
<td style="padding:8px 16px;">$O(T \times H \times W)$ tokens; 10s @ 24fps = 240 frames</td>
<td style="padding:8px 16px;">3D VAE compression, latent space diffusion</td>
</tr>
<tr>
<td style="padding:8px 16px;">Long video generation</td>
<td style="padding:8px 16px;">Minutes-long videos exceed memory</td>
<td style="padding:8px 16px;">Autoregressive chunk generation with overlap</td>
</tr>
<tr style="background:#333;">
<td style="padding:8px 16px;">Training data</td>
<td style="padding:8px 16px;">High-quality video-text pairs are scarce</td>
<td style="padding:8px 16px;">Joint image-video training, synthetic captions</td>
</tr>
</table>
</div>
</div>

### 5.6 Adobe Firefly Video context

Adobe's approach leverages:
- **Image model foundation**: Start from a strong image diffusion model (Firefly Image)
- **Temporal layer insertion**: Add temporal attention/conv layers, fine-tune on video data
- **Creative control**: Adobe emphasizes controllability (camera motion, style transfer, reference images) beyond just text-to-video
- **Commercial safety**: Trained on licensed content, content credentials for provenance

---

## 6. Common Misunderstandings (Error Corrections)

### Misunderstanding 1: "RoPE uses absolute position encoding"
**Correction:** RoPE applies absolute rotations, but the dot product between rotated queries
and keys depends only on the **relative** position $m - n$. The encoding mechanism is absolute
(each position gets a specific rotation), but the resulting attention pattern is purely relative.
This distinction is the core insight.

### Misunderstanding 2: "Position Interpolation and NTK-aware scaling do the same thing"
**Correction:** PI scales all positions uniformly (linear compression). NTK modifies the
base frequency, which preferentially stretches low-frequency dimensions while preserving
high-frequency (local) ones. PI hurts local pattern recognition; NTK preserves it.
YaRN combines both approaches per-dimension for the best of both worlds.

### Misunderstanding 3: "Video generation just runs an image model on each frame"
**Correction:** Per-frame generation produces temporally incoherent videos (flickering,
identity changes). Video models must explicitly model temporal dependencies through
temporal attention, temporal convolutions, or 3D (spacetime) architectures. The temporal
modeling is what makes video generation fundamentally harder than image generation.

### Misunderstanding 4: "Sora uses a U-Net like Stable Diffusion"
**Correction:** Sora uses a **Diffusion Transformer (DiT)** -- a plain transformer operating
on spacetime patches, not a convolutional U-Net. This is a key architectural shift: DiT
scales like LLMs (more compute = better quality), while U-Nets have diminishing returns
at scale. Many recent video models (CogVideoX, Hunyuan Video) also adopt DiT.

### Misunderstanding 5: "RoPE can natively handle any context length"
**Correction:** RoPE trained on length $L$ degrades at $>L$ because the rotation angles
become out-of-distribution. The attention logits grow with position distance, causing
distribution shift. Context extension methods (PI, NTK, YaRN) are required to generalize
beyond the training length. "RoPE enables long context" is more accurate than
"RoPE handles long context."

---

## Self-Check Questions

- [ ] **Q1:** Write the RoPE rotation formula for position $m$ in dimension pair $(2i, 2i+1)$. Prove that $\tilde{q}_m^T \tilde{k}_n$ depends only on $m - n$.
- [ ] **Q2:** Compare Position Interpolation vs NTK-aware scaling: which frequency dimensions does each method affect? Why does NTK better preserve local patterns?
- [ ] **Q3:** In a video diffusion model, explain the difference between spatial attention and temporal attention. Why can't spatial attention alone ensure temporal consistency?
- [ ] **Q4:** Describe the DiT (Diffusion Transformer) architecture. What advantage does it have over U-Net for scaling to longer, higher-resolution videos?

---

## Quick Reference Card

<pre style="background:#111; padding:12px; border-radius:4px; color:#ccc; font-size:13px;">
RoPE:       Rotate q,k in 2D subspaces. theta_i = 1/10000^(2i/d).
            q_m . k_n depends on (m-n) only. No extra parameters.
            Efficient: element-wise cos/sin ops. KV-cache friendly.

vs Others:  Sinusoidal=additive,weak relative. Learned=no extrapolation.
            ALiBi=attention bias,linear penalty. RoPE=multiplicative,exact relative.

Long Ctx:   PI: scale positions by L_train/L_target. Simple but loses local detail.
            NTK: modify base freq. Preserves high-freq (local) dimensions.
            YaRN: per-dimension PI/NTK + attention temp. Best quality, ~400 steps.

Video Gen:  3D VAE compresses T x H x W -> latent (256x reduction typical).
            Temporal attention: cross-frame consistency at each spatial location.
            DiT (Sora): spacetime patches + transformer. Scales like LLMs.
            Challenges: temporal consistency, motion, memory, long videos, data.

Adobe:      Firefly Image -> add temporal layers -> Firefly Video.
            Emphasis on controllability + commercial safety (licensed data).
</pre>
"""


def main() -> None:
    """Insert the RoPE + Long Context + Video Generation study note into mle_prep.db."""
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
