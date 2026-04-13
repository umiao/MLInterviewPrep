"""Seed script: Insert Adobe Prep Day1 -- Diffusion Models study note.

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
DOC_TITLE = "Adobe Prep Day1: Diffusion Models Deep-Dive"

# -- HTML Diagram: Stable Diffusion Pipeline --
PIPELINE_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<span style="background:#4a90d9; padding:6px 12px; border-radius:4px; '
    'color:white;">Text Prompt</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#6b4c9a; padding:6px 12px; border-radius:4px; '
    'color:white;">CLIP Text Encoder</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="color:#aaa;">text embeddings</span>\n'
    "<br/><br/>\n"
    '<span style="color:#aaa;">text embeddings</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#2d6a4f; padding:6px 12px; border-radius:4px; '
    'color:white;">Cross-Attention in UNet</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#d4a017; padding:6px 12px; border-radius:4px; '
    'color:black;">UNet (denoise in latent space)</span>\n'
    "<br/><br/>\n"
    '<span style="background:#d4a017; padding:6px 12px; border-radius:4px; '
    'color:black;">Denoised Latent z_0</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#c0392b; padding:6px 12px; border-radius:4px; '
    'color:white;">VAE Decoder</span>\n'
    '<span style="color:#888;"> ---> </span>\n'
    '<span style="background:#27ae60; padding:6px 12px; border-radius:4px; '
    'color:white;">Output Image</span>\n'
    "</div>\n"
    "</div>"
)

# -- HTML Diagram: Noise Schedule Comparison --
NOISE_SCHEDULE_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:16px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0; font-size:13px;">\n'
    '<div style="text-align:center; margin-bottom:8px; '
    'font-weight:bold; color:#4a90d9;">Noise Schedule Comparison</div>\n'
    "<pre>\n"
    "alpha_bar_t\n"
    "  1.0 |*                        Linear: fast drop\n"
    "      | *\n"
    "      |  **\n"
    "  0.5 |    ****                  Cosine: gradual S-curve\n"
    "      |        ********\n"
    "      |                ****\n"
    "  0.0 |____________________*\n"
    "      0    250   500  750  1000\n"
    "              timestep t\n"
    "</pre>\n"
    "</div>"
)


def build_day1() -> StudyNoteBuilder:
    """Build the Day 1 Diffusion Models study note."""
    b = StudyNoteBuilder()

    b.set_title("Diffusion Models Deep-Dive (Adobe Prep Day 1)")

    # -- Prerequisites --
    b.add_prerequisites([
        "Basic probability (Gaussian distributions, Bayes' theorem)",
        "Neural network fundamentals (loss functions, backpropagation)",
        "VAE concept (encoder-decoder, latent space, KL divergence)",
        "Convolutions and image processing basics",
    ])

    # -- Term Registry --
    b.add_term(
        "DDPM", "Denoising Diffusion Probabilistic Model",
        "Generates data by learning to reverse a gradual noise-adding process"
    )
    b.add_term(
        "VAE", "Variational Autoencoder",
        "Encoder-decoder model that compresses images to a latent space"
    )
    b.add_term(
        "UNet", "U-shaped Network",
        "Architecture that predicts noise in diffusion models, with skip connections"
    )
    b.add_term(
        "CFG", "Classifier-Free Guidance",
        "Technique to steer generation toward text prompts without a separate classifier"
    )
    b.add_term(
        "CLIP", "Contrastive Language-Image Pre-training",
        "Encodes text prompts into embeddings for conditioning the UNet"
    )
    b.add_term(
        "latent space", "Latent Space",
        "Compressed representation where diffusion operates (e.g., 64x64x4 vs 512x512x3)"
    )
    b.add_term(
        "noise schedule", "Noise Schedule",
        "Sequence of beta values controlling how fast noise is added per timestep"
    )
    b.add_term(
        "epsilon-prediction", "Epsilon-Prediction",
        "Parameterization where the model predicts the noise added, not the clean image"
    )
    b.add_term(
        "cross-attention", "Cross-Attention",
        "Mechanism that conditions UNet on text embeddings via Q(image), K(text), V(text)"
    )

    # -- Section 1: DDPM Forward Process --
    b.add_section("1. DDPM Forward Process (Adding Noise)", [
        ("> Adobe's core generative AI technology -- Firefly is built on "
         "latent diffusion.\n> Master the math, the pipeline, and the design choices."),

        "The forward process gradually adds Gaussian noise to data $x_0$ "
        "over $T$ timesteps.",

        "**Intuition:** Think of slowly adding static to a TV image. After "
        "enough steps, the image is indistinguishable from pure noise. The "
        "model's job is to learn how to reverse this corruption.",

        "### Single-step transition",

        FormulaBlock(
            latex=r"q(x_t \mid x_{t-1}) = \mathcal{N}(x_t;\, "
                  r"\sqrt{1 - \beta_t}\, x_{t-1},\; \beta_t \mathbf{I})",
            explanation="Each step slightly corrupts the previous image, "
                        "where $\\beta_t \\in (0, 1)$ is the noise schedule at step $t$:",
        ),

        "### Reparameterization trick (closed-form sampling)",

        "Define:\n"
        "- $\\alpha_t = 1 - \\beta_t$\n"
        "- $\\bar{\\alpha}_t = \\prod_{s=1}^{t} \\alpha_s$\n\n"
        "Then we can sample $x_t$ directly from $x_0$ without iterating:",

        FormulaBlock(
            latex=r"q(x_t \mid x_0) = \mathcal{N}(x_t;\, "
                  r"\sqrt{\bar{\alpha}_t}\, x_0,\; "
                  r"(1 - \bar{\alpha}_t)\, \mathbf{I})",
            explanation="Closed-form distribution -- skip all intermediate steps:",
        ),

        FormulaBlock(
            latex=r"x_t = \sqrt{\bar{\alpha}_t}\, x_0 + "
                  r"\sqrt{1 - \bar{\alpha}_t}\, \epsilon, "
                  r"\quad \epsilon \sim \mathcal{N}(0, \mathbf{I})",
            explanation="**Sampling formula** (the formula you must memorize):",
        ),

        "**Key insight:** As $t \\to T$, $\\bar{\\alpha}_T \\to 0$, "
        "so $x_T \\approx \\epsilon$ (pure noise).",
    ])

    # -- Section 2: Reverse Process --
    b.add_section("2. Reverse Process (Denoising)", [
        "The reverse process learns to denoise: $p_\\theta(x_{t-1} \\mid x_t)$.",

        "**Intuition:** Given a noisy image, the model predicts what noise was "
        "added, then subtracts it. Repeating this from pure noise to a clean "
        "image is how diffusion generates new data.",

        "### Parameterization",

        FormulaBlock(
            latex=r"p_\theta(x_{t-1} \mid x_t) = \mathcal{N}(x_{t-1};\, "
                  r"\mu_\theta(x_t, t),\; \sigma_t^2 \mathbf{I})",
            explanation="The reverse distribution, where the mean is predicted by the network:",
        ),

        FormulaBlock(
            latex=r"\mu_\theta(x_t, t) = \frac{1}{\sqrt{\alpha_t}} "
                  r"\left( x_t - \frac{\beta_t}{\sqrt{1 - \bar{\alpha}_t}}\, "
                  r"\epsilon_\theta(x_t, t) \right)",
            explanation="The predicted mean uses epsilon-prediction -- the network "
                        "$\\epsilon_\\theta$ predicts the noise $\\epsilon$ that was added:",
        ),

        "### Training objective (simplified MSE loss)",

        "**Intuition:** The loss is beautifully simple -- just predict the noise. "
        "No complex reconstruction loss, no adversarial training. This simplicity "
        "is why diffusion models are so stable to train compared to GANs.",

        FormulaBlock(
            latex=r"L_{\text{simple}} = \mathbb{E}_{t, x_0, \epsilon} "
                  r"\left[ \| \epsilon - \epsilon_\theta(x_t, t) \|^2 \right]",
            explanation="MSE between actual noise and predicted noise, where "
                        "$t \\sim \\text{Uniform}(1, T)$, "
                        "$\\epsilon \\sim \\mathcal{N}(0, \\mathbf{I})$, "
                        "and $x_t$ is computed via the reparameterization trick:",
        ),

        "### Sampling algorithm\n\n"
        "```\n"
        "x_T ~ N(0, I)\n"
        "for t = T, T-1, ..., 1:\n"
        "    z ~ N(0, I) if t > 1, else z = 0\n"
        "    x_{t-1} = (1/sqrt(alpha_t)) * (x_t - beta_t/sqrt(1-alpha_bar_t) "
        "* eps_theta(x_t, t)) + sigma_t * z\n"
        "return x_0\n"
        "```",
    ])

    # -- Section 3: Latent Diffusion / Stable Diffusion Pipeline --
    b.add_section("3. Latent Diffusion / Stable Diffusion Pipeline", [
        "Instead of diffusing in pixel space (expensive), Latent Diffusion "
        "operates in a compressed latent space.",

        "**Intuition:** Imagine trying to paint a mural by placing individual "
        "atoms vs. using brushstrokes. The latent space is the 'brushstroke' "
        "representation -- captures the essential structure at 64x fewer dimensions.",
    ])

    b.add_diagram_html(PIPELINE_DIAGRAM)

    b.add_comparison_table(
        headers=["Component", "Role", "Details"],
        rows=[
            ["VAE Encoder", "Compress image to latent",
             "$z = \\text{Enc}(x)$, typically 8x spatial downsampling"],
            ["VAE Decoder", "Reconstruct from latent",
             "$\\hat{x} = \\text{Dec}(z_0)$"],
            ["UNet", "Predict noise in latent space",
             "Time-conditioned, with cross-attention for text"],
            ["CLIP Text Encoder", "Encode text prompt",
             "Produces token embeddings for cross-attention"],
            ["Cross-Attention", "Condition UNet on text",
             "$\\text{Attention}(Q_{\\text{image}}, K_{\\text{text}}, V_{\\text{text}})$"],
            ["Scheduler", "Control denoising steps",
             "DDPM, DDIM, DPM-Solver, etc."],
        ],
        title="Key Components",
    )

    b.add_section("Why Latent Space?", [
        "- Pixel-space diffusion on 512x512x3 images is prohibitively expensive\n"
        "- VAE compresses to 64x64x4 latent -- **64x fewer dimensions**\n"
        "- Training and inference are much faster with minimal quality loss\n"
        "- The VAE is trained separately (reconstruction + KL regularization)",
    ])

    # -- Section 4: Classifier-Free Guidance --
    b.add_section("4. Classifier-Free Guidance (CFG)", [
        "CFG is the key technique that makes text-to-image generation follow "
        "prompts closely.",

        "**Intuition:** The model learns what images look like both with and "
        "without a text description. At inference time, it computes the "
        "'direction toward the text' and amplifies it. Higher guidance = "
        "more faithful to the prompt, but less diverse.",

        "### Training\n\n"
        "During training, randomly drop the conditioning (text) with some "
        "probability (e.g., 10%):\n"
        "- With text: model learns $\\epsilon_\\theta(x_t, t, c)$ (conditional)\n"
        "- Without text: model learns $\\epsilon_\\theta(x_t, t, \\varnothing)$ "
        "(unconditional)\n\n"
        "This trains a single model that can do both conditional and unconditional "
        "generation.",

        "### Inference formula",

        FormulaBlock(
            latex=r"\hat{\epsilon} = \epsilon_\theta(x_t, t, \varnothing) + "
                  r"w \cdot \left( \epsilon_\theta(x_t, t, c) - "
                  r"\epsilon_\theta(x_t, t, \varnothing) \right)",
            explanation="The guided prediction interpolates between "
                        "unconditional and conditional, amplified by guidance scale $w$:",
        ),

        "where:\n"
        "- $w$ = guidance scale (typically 7-12 for Stable Diffusion)\n"
        "- $w = 1$: standard conditional generation (no guidance)\n"
        "- $w > 1$: amplifies the effect of conditioning, sharper but less diverse\n"
        "- $w = 0$: unconditional generation (ignores text)\n\n"
        "**Intuition:** The difference "
        "$(\\epsilon_\\text{cond} - \\epsilon_\\text{uncond})$ "
        "is the 'direction toward the text.' Scaling by $w > 1$ pushes harder "
        "in that direction.\n\n"
        "**Trade-off:** Higher $w$ = better text alignment but lower diversity "
        "and potential artifacts.",
    ])

    # -- Section 5: Noise Schedules --
    b.add_section("5. Noise Schedules", [
        "The noise schedule $\\{\\beta_t\\}_{t=1}^T$ controls how quickly "
        "noise is added.",

        "**Intuition:** Think of the noise schedule as controlling the 'pace' "
        "of image destruction. Too fast and the model wastes training on "
        "nearly-destroyed images; too slow and training is inefficient. "
        "The cosine schedule provides a more even pace.",

        "### Linear schedule (DDPM original)",

        FormulaBlock(
            latex=r"\beta_t = \beta_1 + \frac{t-1}{T-1}(\beta_T - \beta_1)",
            explanation="Linear interpolation. Typical values: "
                        "$\\beta_1 = 10^{-4}$, $\\beta_T = 0.02$, $T = 1000$:",
        ),

        "**Problem:** $\\bar{\\alpha}_t$ drops too quickly in the middle steps, "
        "wasting capacity on nearly-destroyed images.",

        "### Cosine schedule (Improved DDPM)",

        FormulaBlock(
            latex=r"\bar{\alpha}_t = \frac{f(t)}{f(0)}, \quad "
                  r"f(t) = \cos\left(\frac{t/T + s}{1 + s} \cdot "
                  r"\frac{\pi}{2}\right)^2",
            explanation="More gradual destruction with offset $s = 0.008$ "
                        "to prevent $\\beta_t$ from being too small near $t = 0$:",
        ),

        "**Advantage:** More uniform information destruction rate -- the model "
        "gets useful training signal at all timesteps, not just early ones.",
    ])

    b.add_diagram_html(NOISE_SCHEDULE_DIAGRAM)

    b.add_comparison_table(
        headers=["Property", "Linear", "Cosine"],
        rows=[
            ["$\\bar{\\alpha}_t$ curve", "Fast drop in middle",
             "Gradual, S-shaped"],
            ["Noise at $t = T/2$", "Image nearly destroyed",
             "Still recognizable"],
            ["Training efficiency", "Wastes mid-range steps",
             "Uniform signal"],
            ["Used in", "DDPM (original)",
             "Improved DDPM, most modern models"],
        ],
        title="Linear vs. Cosine Schedule",
    )

    # -- Section 6: Advanced Topics --
    b.add_section("6. Advanced Topics (Interview Depth)", [
        "### DDIM (Denoising Diffusion Implicit Models)\n\n"
        "- Makes the reverse process **deterministic** (no added noise $z$)\n"
        "- Allows skipping steps: sample at $t = [1000, 800, 600, ...]$ "
        "instead of every step\n"
        "- Same trained model, just different sampling -- 10-50 steps "
        "instead of 1000\n"
        "- Enables **interpolation** between images in latent space",

        "### Score-based / SDE formulation\n\n"
        "- Forward process as a continuous SDE: "
        "$dx = f(x,t)\\,dt + g(t)\\,dw$\n"
        "- Reverse SDE: $dx = [f(x,t) - g(t)^2 \\nabla_x \\log p_t(x)]"
        "\\,dt + g(t)\\,d\\bar{w}$\n"
        "- Score function $\\nabla_x \\log p_t(x)$ is estimated by the "
        "neural network\n"
        "- Unifies DDPM, DDIM, and score matching under one framework",
    ])

    b.add_comparison_table(
        headers=["Metric", "Value"],
        rows=[
            ["Typical T (DDPM)", "1000"],
            ["DDIM inference steps", "20-50"],
            ["SD latent dimensions", "64x64x4"],
            ["SD pixel resolution", "512x512 (v1.5), 1024x1024 (SDXL)"],
            ["CFG scale (typical)", "7.5"],
            ["VAE downsampling", "8x spatial"],
        ],
        title="Key Numbers to Remember",
    )

    # -- Self-Check --
    b.add_checklist("Self-Check Questions", [
        "**Q1:** Write the reparameterization formula for "
        "$q(x_t \\mid x_0)$. What happens when $t = T$?",
        "**Q2:** In the DDPM loss, why do we predict noise $\\epsilon$ "
        "instead of directly predicting $x_0$ or $x_{t-1}$? "
        "(Hint: variance reduction)",
        "**Q3:** Explain why CFG needs both conditional and unconditional "
        "forward passes. What is the computational cost implication?",
        "**Q4:** Stable Diffusion operates in 64x64x4 latent space for "
        "512x512 images. Calculate the compression ratio and explain why "
        "this doesn't destroy image quality.",
    ])

    # -- Quick Reference --
    b.add_section("Quick Reference Card", [
        "```\n"
        "Forward:  x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * eps\n"
        "Loss:     L = E[||eps - eps_theta(x_t, t)||^2]\n"
        "CFG:      eps_hat = eps_uncond + w * (eps_cond - eps_uncond)\n"
        "Pipeline: Text -> CLIP -> Cross-Attn -> UNet(denoise) -> VAE Decode -> Image\n"
        "```",
    ])

    return b


def main() -> None:
    """Build and save the Diffusion Models study note to mle_prep.db."""
    b = build_day1()

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
