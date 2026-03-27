"""Seed script: Insert Adobe Prep Day1 -- Diffusion Models study note.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: skips if a document with the same title already exists.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day1: Diffusion Models Deep-Dive"

CONTENT = r"""# Diffusion Models Deep-Dive (Adobe Prep Day 1)

> Adobe's core generative AI technology -- Firefly is built on latent diffusion.
> Master the math, the pipeline, and the design choices.

---

## 1. DDPM Forward Process (Adding Noise)

The forward process gradually adds Gaussian noise to data $x_0$ over $T$ timesteps.

### Single-step transition

$$q(x_t \mid x_{t-1}) = \mathcal{N}(x_t;\, \sqrt{1 - \beta_t}\, x_{t-1},\; \beta_t \mathbf{I})$$

where $\beta_t \in (0, 1)$ is the noise schedule at step $t$.

### Reparameterization trick (closed-form sampling)

Define:
- $\alpha_t = 1 - \beta_t$
- $\bar{\alpha}_t = \prod_{s=1}^{t} \alpha_s$

Then we can sample $x_t$ directly from $x_0$ without iterating:

$$q(x_t \mid x_0) = \mathcal{N}(x_t;\, \sqrt{\bar{\alpha}_t}\, x_0,\; (1 - \bar{\alpha}_t)\, \mathbf{I})$$

**Sampling formula:**

$$x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1 - \bar{\alpha}_t}\, \epsilon, \quad \epsilon \sim \mathcal{N}(0, \mathbf{I})$$

**Key insight:** As $t \to T$, $\bar{\alpha}_T \to 0$, so $x_T \approx \epsilon$ (pure noise).

---

## 2. Reverse Process (Denoising)

The reverse process learns to denoise: $p_\theta(x_{t-1} \mid x_t)$.

### Parameterization

$$p_\theta(x_{t-1} \mid x_t) = \mathcal{N}(x_{t-1};\, \mu_\theta(x_t, t),\; \sigma_t^2 \mathbf{I})$$

where the mean is predicted as:

$$\mu_\theta(x_t, t) = \frac{1}{\sqrt{\alpha_t}} \left( x_t - \frac{\beta_t}{\sqrt{1 - \bar{\alpha}_t}}\, \epsilon_\theta(x_t, t) \right)$$

The network $\epsilon_\theta$ predicts the noise $\epsilon$ that was added.

### Training objective (simplified MSE loss)

$$L_{\text{simple}} = \mathbb{E}_{t, x_0, \epsilon} \left[ \| \epsilon - \epsilon_\theta(x_t, t) \|^2 \right]$$

where $t \sim \text{Uniform}(1, T)$, $\epsilon \sim \mathcal{N}(0, \mathbf{I})$, and $x_t$ is computed via the reparameterization trick.

### Sampling algorithm

```
x_T ~ N(0, I)
for t = T, T-1, ..., 1:
    z ~ N(0, I) if t > 1, else z = 0
    x_{t-1} = (1/sqrt(alpha_t)) * (x_t - beta_t/sqrt(1-alpha_bar_t) * eps_theta(x_t, t)) + sigma_t * z
return x_0
```

---

## 3. Latent Diffusion / Stable Diffusion Pipeline

Instead of diffusing in pixel space (expensive), Latent Diffusion operates in a compressed latent space.

### Architecture pipeline

<div style="background:#1a1a2e; padding:20px; border-radius:8px; margin:16px 0; font-family:monospace; color:#e0e0e0;">
<div style="text-align:center; font-size:14px;">
<span style="background:#4a90d9; padding:6px 12px; border-radius:4px; color:white;">Text Prompt</span>
<span style="color:#888;"> ---> </span>
<span style="background:#6b4c9a; padding:6px 12px; border-radius:4px; color:white;">CLIP Text Encoder</span>
<span style="color:#888;"> ---> </span>
<span style="color:#aaa;">text embeddings</span>
<br/><br/>
<span style="color:#aaa;">text embeddings</span>
<span style="color:#888;"> ---> </span>
<span style="background:#2d6a4f; padding:6px 12px; border-radius:4px; color:white;">Cross-Attention in UNet</span>
<span style="color:#888;"> ---> </span>
<span style="background:#d4a017; padding:6px 12px; border-radius:4px; color:black;">UNet (denoise in latent space)</span>
<br/><br/>
<span style="background:#d4a017; padding:6px 12px; border-radius:4px; color:black;">Denoised Latent z_0</span>
<span style="color:#888;"> ---> </span>
<span style="background:#c0392b; padding:6px 12px; border-radius:4px; color:white;">VAE Decoder</span>
<span style="color:#888;"> ---> </span>
<span style="background:#27ae60; padding:6px 12px; border-radius:4px; color:white;">Output Image</span>
</div>
</div>

### Key components

| Component | Role | Details |
|-----------|------|---------|
| **VAE Encoder** | Compress image to latent | $z = \text{Enc}(x)$, typically 8x spatial downsampling |
| **VAE Decoder** | Reconstruct from latent | $\hat{x} = \text{Dec}(z_0)$ |
| **UNet** | Predict noise in latent space | Time-conditioned, with cross-attention for text |
| **CLIP Text Encoder** | Encode text prompt | Produces token embeddings for cross-attention |
| **Cross-Attention** | Condition UNet on text | $\text{Attention}(Q_{\text{image}}, K_{\text{text}}, V_{\text{text}})$ |
| **Scheduler** | Control denoising steps | DDPM, DDIM, DPM-Solver, etc. |

### Why latent space?

- Pixel-space diffusion on 512x512x3 images is prohibitively expensive
- VAE compresses to 64x64x4 latent -- **64x fewer dimensions**
- Training and inference are much faster with minimal quality loss
- The VAE is trained separately (reconstruction + KL regularization)

---

## 4. Classifier-Free Guidance (CFG)

CFG is the key technique that makes text-to-image generation follow prompts closely.

### Training

During training, randomly drop the conditioning (text) with some probability (e.g., 10%):
- With text: model learns $\epsilon_\theta(x_t, t, c)$ (conditional)
- Without text: model learns $\epsilon_\theta(x_t, t, \varnothing)$ (unconditional)

This trains a single model that can do both conditional and unconditional generation.

### Inference formula

$$\hat{\epsilon} = \epsilon_\theta(x_t, t, \varnothing) + w \cdot \left( \epsilon_\theta(x_t, t, c) - \epsilon_\theta(x_t, t, \varnothing) \right)$$

where:
- $w$ = guidance scale (typically 7-12 for Stable Diffusion)
- $w = 1$: standard conditional generation (no guidance)
- $w > 1$: amplifies the effect of conditioning, sharper but less diverse
- $w = 0$: unconditional generation (ignores text)

**Intuition:** The difference $(\epsilon_\text{cond} - \epsilon_\text{uncond})$ is the "direction toward the text." Scaling by $w > 1$ pushes harder in that direction.

**Trade-off:** Higher $w$ = better text alignment but lower diversity and potential artifacts.

---

## 5. Noise Schedules

The noise schedule $\{\beta_t\}_{t=1}^T$ controls how quickly noise is added.

### Linear schedule (DDPM original)

$$\beta_t = \beta_1 + \frac{t-1}{T-1}(\beta_T - \beta_1)$$

Typical values: $\beta_1 = 10^{-4}$, $\beta_T = 0.02$, $T = 1000$.

**Problem:** $\bar{\alpha}_t$ drops too quickly in the middle steps, wasting capacity on nearly-destroyed images.

### Cosine schedule (Improved DDPM)

$$\bar{\alpha}_t = \frac{f(t)}{f(0)}, \quad f(t) = \cos\left(\frac{t/T + s}{1 + s} \cdot \frac{\pi}{2}\right)^2$$

where $s = 0.008$ is a small offset to prevent $\beta_t$ from being too small near $t = 0$.

**Advantage:** More uniform information destruction rate -- the model gets useful training signal at all timesteps, not just early ones.

### Comparison

| Property | Linear | Cosine |
|----------|--------|--------|
| $\bar{\alpha}_t$ curve | Fast drop in middle | Gradual, S-shaped |
| Noise at $t = T/2$ | Image nearly destroyed | Still recognizable |
| Training efficiency | Wastes mid-range steps | Uniform signal |
| Used in | DDPM (original) | Improved DDPM, most modern models |

---

## 6. Advanced Topics (Interview Depth)

### DDIM (Denoising Diffusion Implicit Models)

- Makes the reverse process **deterministic** (no added noise $z$)
- Allows skipping steps: sample at $t = [1000, 800, 600, ...]$ instead of every step
- Same trained model, just different sampling -- 10-50 steps instead of 1000
- Enables **interpolation** between images in latent space

### Score-based / SDE formulation

- Forward process as a continuous SDE: $dx = f(x,t)\,dt + g(t)\,dw$
- Reverse SDE: $dx = [f(x,t) - g(t)^2 \nabla_x \log p_t(x)]\,dt + g(t)\,d\bar{w}$
- Score function $\nabla_x \log p_t(x)$ is estimated by the neural network
- Unifies DDPM, DDIM, and score matching under one framework

### Key numbers to remember

| Metric | Value |
|--------|-------|
| Typical T (DDPM) | 1000 |
| DDIM inference steps | 20-50 |
| SD latent dimensions | 64x64x4 |
| SD pixel resolution | 512x512 (v1.5), 1024x1024 (SDXL) |
| CFG scale (typical) | 7.5 |
| VAE downsampling | 8x spatial |

---

## Self-Check Questions

- [ ] **Q1:** Write the reparameterization formula for $q(x_t \mid x_0)$. What happens when $t = T$?
- [ ] **Q2:** In the DDPM loss, why do we predict noise $\epsilon$ instead of directly predicting $x_0$ or $x_{t-1}$? (Hint: variance reduction)
- [ ] **Q3:** Explain why Classifier-Free Guidance needs both conditional and unconditional forward passes. What is the computational cost implication?
- [ ] **Q4:** Stable Diffusion operates in 64x64x4 latent space for 512x512 images. Calculate the compression ratio and explain why this doesn't destroy image quality.

---

## Quick Reference Card

```
Forward:  x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * eps
Loss:     L = E[||eps - eps_theta(x_t, t)||^2]
CFG:      eps_hat = eps_uncond + w * (eps_cond - eps_uncond)
Pipeline: Text -> CLIP -> Cross-Attn -> UNet(denoise) -> VAE Decode -> Image
```
"""


def main() -> None:
    """Insert the Diffusion Models study note into mle_prep.db."""
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
