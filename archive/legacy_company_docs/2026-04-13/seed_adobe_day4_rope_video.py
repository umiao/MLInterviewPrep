"""Seed script: Insert Adobe Prep Day4 -- RoPE + Long Context + Video Generation note.

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
DOC_TITLE = "Adobe Prep Day4: RoPE + Long Context + Video Generation"

# -- HTML Diagram: RoPE Rotation in 2D Subspace --
ROPE_ROTATION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">RoPE Rotation Diagram (2D subspace)</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    '  Position m=0:  q0 = (x, y)        -- no rotation\n'
    '  Position m=1:  q1 = rotate(q, theta)  -- rotate by theta\n'
    '  Position m=2:  q2 = rotate(q, 2*theta) -- rotate by 2*theta\n'
    '  ...\n'
    '  Position m=k:  qk = rotate(q, k*theta) -- rotate by k*theta\n'
    '\n'
    '  Dot product: q_m . k_n = f(q, k, m-n)\n'
    '  (only depends on relative distance!)\n'
    '\n'
    '  theta_i = 1 / 10000^(2i/d)\n'
    '  Low-freq pairs (large i): slow rotation  -> capture long-range patterns\n'
    '  High-freq pairs (small i): fast rotation -> capture local patterns\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: Video Diffusion Architecture --
VIDEO_ARCHITECTURE_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Video Diffusion Architecture (Latent Video Diffusion)</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'Input: text prompt + (optional) reference image/video\n'
    '\n'
    '  Text Encoder (CLIP / T5)\n'
    '         |\n'
    '         v\n'
    '  [3D VAE Encoder]  -- encodes video (T x H x W x 3) -> latent (T\' x H\' x W\' x C)\n'
    '         |              temporal + spatial compression\n'
    '         v\n'
    '  [Denoising Network]  -- iterative noise removal in latent space\n'
    '  |  Spatial Attention  -- per-frame quality (from image model)\n'
    '  |  Temporal Attention -- cross-frame consistency\n'
    '  |  Cross-Attention    -- text conditioning\n'
    '  |  (repeated L times)\n'
    '         |\n'
    '         v\n'
    '  [3D VAE Decoder]  -- latent -> video frames\n'
    '         |\n'
    '         v\n'
    '  Output: T frames of H x W video\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: YaRN Dimension Grouping --
YARN_DIMENSION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">YaRN Dimension Grouping</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; '
    'color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Frequency Group</th>\n'
    '<th style="padding:8px 16px; text-align:left;">RoPE Dimensions</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Treatment</th>\n'
    '</tr>\n'
    '<tr style="background:#4a90d9; color:white;">\n'
    '<td style="padding:8px 16px;">High frequency (local)</td>\n'
    '<td style="padding:8px 16px;">Small $$i$$ (fast rotation)</td>\n'
    '<td style="padding:8px 16px;">No interpolation (keep as-is)</td>\n'
    '</tr>\n'
    '<tr style="background:#6b4c9a; color:white;">\n'
    '<td style="padding:8px 16px;">Medium frequency</td>\n'
    '<td style="padding:8px 16px;">Mid $$i$$</td>\n'
    '<td style="padding:8px 16px;">Blend of PI and NTK</td>\n'
    '</tr>\n'
    '<tr style="background:#2d6a4f; color:white;">\n'
    '<td style="padding:8px 16px;">Low frequency (long-range)</td>\n'
    '<td style="padding:8px 16px;">Large $$i$$ (slow rotation)</td>\n'
    '<td style="padding:8px 16px;">Full PI interpolation</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: DiT Architecture Table --
DIT_ARCHITECTURE_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">DiT (Diffusion Transformer) Architecture</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; '
    'color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Component</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Description</th>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Patchification</td>\n'
    '<td style="padding:8px 16px;">Convert latent video into '
    '<b>spacetime patches</b> (3D patches: t x h x w)</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Backbone</td>\n'
    '<td style="padding:8px 16px;">Standard Transformer (not U-Net!) '
    'with full self-attention over all patches</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Conditioning</td>\n'
    '<td style="padding:8px 16px;">AdaLN-Zero: adaptive layer norm, '
    'conditioned on timestep + text</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Scaling</td>\n'
    '<td style="padding:8px 16px;">Pure transformer scales with compute '
    '(like LLMs) -- key advantage over U-Net</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: Video Generation Challenges --
VIDEO_CHALLENGES_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Video Generation Challenges</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; '
    'color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Challenge</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Why it is hard</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Current approach</th>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Temporal consistency</td>\n'
    '<td style="padding:8px 16px;">Objects must persist and move coherently</td>\n'
    '<td style="padding:8px 16px;">Temporal attention + 3D VAE</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Motion coherence</td>\n'
    '<td style="padding:8px 16px;">Physics-plausible motion, no jitter</td>\n'
    '<td style="padding:8px 16px;">Motion modules, temporal conv</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Memory / compute</td>\n'
    '<td style="padding:8px 16px;">$$O(T \\times H \\times W)$$ tokens; '
    '10s @ 24fps = 240 frames</td>\n'
    '<td style="padding:8px 16px;">3D VAE compression, latent space diffusion</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Long video generation</td>\n'
    '<td style="padding:8px 16px;">Minutes-long videos exceed memory</td>\n'
    '<td style="padding:8px 16px;">Autoregressive chunk generation with overlap</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Training data</td>\n'
    '<td style="padding:8px 16px;">High-quality video-text pairs are scarce</td>\n'
    '<td style="padding:8px 16px;">Joint image-video training, synthetic captions</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)


def build_day4() -> "StudyNoteBuilder":
    """Build the Day 4 RoPE + Long Context + Video Generation study note."""
    b = StudyNoteBuilder()

    b.set_title(
        "RoPE + Long Context + Video Generation (Adobe Prep Day 4)"
    )

    # -- Prerequisites --
    b.add_prerequisites([
        "Transformer self-attention mechanism (Q, K, V projections, dot-product attention)",
        "Basic trigonometry (sine, cosine, rotation matrices)",
        "Day 1: Diffusion Models (cross-reference: video generation builds on image diffusion)",
        "Day 3: Distributed Training (cross-reference: video model training at scale)",
    ])

    # -- Term Registry --
    b.add_term(
        "RoPE", "Rotary Position Embedding",
        "Encodes position by rotating Q/K vectors in 2D subspaces; "
        "dot product depends only on relative distance"
    )
    b.add_term(
        "PE", "Positional Encoding",
        "Mechanism for injecting position information into transformer representations"
    )
    b.add_term(
        "PI", "Position Interpolation",
        "Long-context method that linearly compresses positions into the trained range"
    )
    b.add_term(
        "NTK", "Neural Tangent Kernel (scaling)",
        "Long-context method that modifies the RoPE base frequency to "
        "preserve high-frequency local patterns"
    )
    b.add_term(
        "YaRN", "Yet another RoPE extensioN",
        "Per-dimension blend of PI and NTK with attention temperature scaling; "
        "best long-context quality"
    )
    b.add_term(
        "DiT", "Diffusion Transformer",
        "Replaces U-Net with a plain transformer over spacetime patches; "
        "scales like LLMs"
    )
    b.add_term(
        "3D VAE", "3D Variational Autoencoder",
        "Compresses video along spatial and temporal axes into a compact latent space"
    )
    b.add_term(
        "KV-cache", "Key-Value Cache",
        "Cached K/V tensors from prior tokens for efficient autoregressive inference"
    )
    b.add_term(
        "temporal attention", "Temporal Attention",
        "Attention across frames at each spatial location; enforces cross-frame consistency"
    )
    b.add_term(
        "ALiBi", "Attention with Linear Biases",
        "PE method that adds linear distance penalty to attention scores"
    )
    b.add_term(
        "AdaLN", "Adaptive Layer Normalization",
        "Layer norm conditioned on external signal (timestep, text); used in DiT"
    )

    # -- Section 1: Why Positional Encoding Matters --
    b.add_section("1. Positional Encoding -- Why It Matters", [
        ("> Positional encoding is how transformers know token order. RoPE is the modern\n"
         "> standard -- understand its math, why it enables relative position awareness,\n"
         "> and how it extends to long contexts. Video generation adds the temporal axis:\n"
         "> know the core architectural choices Adobe cares about."),

        "Transformers are **permutation-invariant** without positional information: attention "
        "computes the same output regardless of token order. Positional encoding breaks this "
        "symmetry by injecting position information into the representation.",

        "### Key requirements for a good PE scheme\n\n"
        "1. **Unique** encoding per position\n"
        "2. **Bounded** values (no explosion at long positions)\n"
        "3. **Relative distance** awareness (attention should depend on $$m - n$$, "
        "not absolute $$m, n$$)\n"
        "4. **Extrapolation** to unseen lengths (train on 4K, infer on 32K+)",
    ])

    # -- Section 2: RoPE Mathematical Formulation --
    b.add_section("2. RoPE: Rotary Position Embedding", [
        "### Core idea\n\n"
        "Instead of *adding* a position vector, RoPE **rotates** query and key vectors "
        "in 2D subspaces. The rotation angle is proportional to the position index, "
        "so the dot product $$q_m \\cdot k_n$$ depends only on the relative distance $$m - n$$.",

        "### Mathematical formulation\n\n"
        "For a $$d$$-dimensional embedding, group dimensions into $$d/2$$ pairs. "
        "Each pair $$(x_{2i}, x_{2i+1})$$ is treated as a 2D vector and rotated "
        "by angle $$m \\cdot \\theta_i$$:",

        FormulaBlock(
            latex=r"\theta_i = \frac{1}{10000^{2i/d}}, \quad i = 0, 1, \ldots, d/2 - 1",
            explanation="Base frequency for each dimension pair:",
        ),

        FormulaBlock(
            latex=(r"R_m = \begin{pmatrix} \cos(m\theta_0) & -\sin(m\theta_0) & & \\ "
                   r"\sin(m\theta_0) & \cos(m\theta_0) & & \\ "
                   r"& & \cos(m\theta_1) & -\sin(m\theta_1) \\ "
                   r"& & \sin(m\theta_1) & \cos(m\theta_1) \\ "
                   r"& & & & \ddots \end{pmatrix}"),
            explanation="The block-diagonal rotation matrix for position $$m$$:",
        ),

        "Applied to queries and keys:",

        FormulaBlock(
            latex=r"\tilde{q}_m = R_m q_m, \quad \tilde{k}_n = R_n k_n",
        ),

        "### Why the dot product depends only on $$m - n$$",

        FormulaBlock(
            latex=r"\tilde{q}_m^T \tilde{k}_n = q_m^T R_m^T R_n k_n = q_m^T R_{n-m} k_n",
            explanation="This works because rotation matrices satisfy "
                        "$$R_m^T R_n = R_{n-m}$$ (rotation by the difference). "
                        "The attention score between positions $$m$$ and $$n$$ is a "
                        "function of the **relative distance** $$m - n$$, not the "
                        "absolute positions:",
        ),
    ])

    b.add_diagram_html(ROPE_ROTATION_DIAGRAM)

    b.add_section("### Efficient implementation (complex number trick)", [
        "Instead of building a sparse rotation matrix, RoPE can be computed element-wise:",

        FormulaBlock(
            latex=(r"\text{RoPE}(x_m) = x_m \odot \cos(m\theta) "
                   r"+ \text{rotate\_half}(x_m) \odot \sin(m\theta)"),
            explanation="where `rotate_half` swaps pairs and negates: "
                        "$$(x_0, x_1, x_2, x_3, \\ldots) \\to "
                        "(-x_1, x_0, -x_3, x_2, \\ldots)$$:",
        ),

        "```python\n"
        "# PyTorch-style implementation\n"
        "def apply_rope(x, freqs_cos, freqs_sin):\n"
        "    # x: (batch, seq_len, n_heads, head_dim)\n"
        "    # freqs_cos, freqs_sin: (seq_len, head_dim/2)\n"
        "    x_r = x.float().reshape(*x.shape[:-1], -1, 2)\n"
        "    x_real, x_imag = x_r[..., 0], x_r[..., 1]\n"
        "    # Rotation in 2D: (a+bi)(cos+sin*i) = (a*cos - b*sin) + (a*sin + b*cos)i\n"
        "    out_real = x_real * freqs_cos - x_imag * freqs_sin\n"
        "    out_imag = x_real * freqs_sin + x_imag * freqs_cos\n"
        "    return torch.stack([out_real, out_imag], dim=-1).flatten(-2)\n"
        "```",
    ])

    # -- Section 3: PE Comparison --
    b.add_section("3. PE Comparison Table", [])

    b.add_comparison_table(
        headers=["Method", "Type", "Relative?", "Extrapolation", "Used in"],
        rows=[
            ["Sinusoidal (Vaswani 2017)", "Additive, fixed",
             "Weak (via dot product)", "Poor", "Original Transformer"],
            ["Learned Absolute", "Additive, learned",
             "No", "None (fixed max len)", "BERT, GPT-2"],
            ["**ALiBi**", "Attention bias",
             "Yes (linear penalty)", "Good", "BLOOM, MPT"],
            ["**RoPE**", "Multiplicative (rotation)",
             "**Yes (by construction)**", "Moderate (needs scaling)",
             "**Llama, Mistral, Qwen, Gemma**"],
        ],
        title="Positional Encoding Methods Comparison",
    )

    b.add_section("### Why RoPE won", [
        "- Relative position encoding is a mathematical property, not an approximation\n"
        "- No additional parameters (unlike learned PE)\n"
        "- Compatible with KV-cache (rotation is per-token, no recomputation needed)\n"
        "- Efficient: element-wise ops, no matrix multiplication overhead",

        "**RoPE vs Sinusoidal:**\n\n"
        "- Sinusoidal adds position vectors: $$h_m = x_m + PE_m$$. The dot product "
        "$$h_m^T h_n$$ contains cross terms "
        "$$x_m^T PE_n + PE_m^T x_n + PE_m^T PE_n$$ -- the relative signal is "
        "mixed with absolute terms.\n"
        "- RoPE multiplies (rotates): the rotation cleanly factors out, giving "
        "pure relative dependence.",
    ])

    # -- Section 4: Long Context Methods --
    b.add_section("4. Long Context Methods", [
        "RoPE trained on length $$L$$ degrades at length $$> L$$ because the rotation "
        "angles become out-of-distribution. Several methods extend the context window "
        "without full retraining.",

        "### 4.1 Position Interpolation (PI)\n\n"
        "**Idea:** Instead of extrapolating to unseen positions, **compress** positions "
        "to fit within the trained range.",

        FormulaBlock(
            latex=r"m' = m \cdot \frac{L_{\text{train}}}{L_{\text{target}}}",
            explanation="For example, to extend from 4K to 32K: scale all positions by "
                        "$$4096/32768 = 1/8$$. Position 32000 becomes position 4000 -- "
                        "within the trained range:",
        ),

        "**Pros:** Simple, effective with minimal fine-tuning (~1000 steps).\n"
        "**Cons:** Compresses nearby positions, reducing local resolution.",

        "### 4.2 NTK-aware Scaling\n\n"
        "**Idea:** The problem with PI is it scales all frequencies equally. "
        "High-frequency components (small $$i$$, responsible for local patterns) "
        "are hurt most by compression. NTK-aware scaling modifies the **base frequency** instead:",

        FormulaBlock(
            latex=(r"\theta_i' = \frac{1}{(b \cdot \alpha)^{2i/d}} "
                   r"\quad \text{where } \alpha = \frac{L_{\text{target}}}{L_{\text{train}}}"),
            explanation="This effectively keeps high-frequency dimensions (local patterns) "
                        "mostly unchanged, while stretching low-frequency dimensions "
                        "(long-range patterns) to accommodate longer contexts:",
        ),

        "**Intuition:** Like changing the base of the number system rather than "
        "compressing all digits.",

        "### 4.3 YaRN (Yet another RoPE extensioN)\n\n"
        "**Idea:** Combines the best of PI and NTK with an attention-scaling factor. "
        "Divides RoPE dimensions into three frequency groups:",
    ])

    b.add_diagram_html(YARN_DIMENSION_DIAGRAM)

    b.add_section("### YaRN attention temperature", [
        "Plus an **attention temperature scaling** factor $$\\sqrt{t}$$ to compensate "
        "for the entropy increase at longer contexts:",

        FormulaBlock(
            latex=r"\text{Attention}(Q, K, V) = \text{softmax}\left("
                  r"\frac{QK^T}{\sqrt{d} \cdot \sqrt{t}}\right) V",
            explanation="YaRN achieves the best extrapolation with minimal "
                        "fine-tuning (~400 steps) and is used in production "
                        "models like Llama 3.1 (128K context):",
        ),
    ])

    b.add_comparison_table(
        headers=["Method", "Approach", "Fine-tuning", "Quality"],
        rows=[
            ["**PI**", "Linear position scaling", "~1K steps",
             "Good, loses local detail"],
            ["**NTK**", "Base frequency adjustment", "~1K steps (or zero-shot)",
             "Better local preservation"],
            ["**YaRN**", "Per-dimension PI/NTK + attn temp", "~400 steps",
             "**Best overall**"],
            ["Sliding Window + Global", "Local attention + sparse global",
             "Architecture change", "Good for very long (1M+)"],
        ],
        title="Long Context Extension Methods",
    )

    # -- Section 5: Video Generation --
    b.add_section("5. Video Generation", [
        "Adobe is a leader in generative media (Firefly). Video generation extends "
        "image generation along the **temporal axis** -- this is a core area for "
        "Adobe interviews.",

        "### 5.1 Core challenge: temporal consistency\n\n"
        "A video is a sequence of frames. Generating each frame independently "
        "(image model per frame) produces flickering, inconsistent content. The key challenge:\n\n"
        "**Maintain spatial quality per frame while ensuring temporal coherence across frames.**",

        "### 5.2 Architecture overview",
    ])

    b.add_diagram_html(VIDEO_ARCHITECTURE_DIAGRAM)

    b.add_section("### 5.3 Key components", [
        "**3D VAE (Variational Autoencoder)**\n\n"
        "Unlike image VAE (2D: H x W), video VAE compresses along all three axes:\n\n"
        "- **Spatial** compression: $$H \\times W \\to H/8 \\times W/8$$ (typical 8x)\n"
        "- **Temporal** compression: $$T \\to T/4$$ (typical 4x)\n"
        "- Total compression: $$4 \\times 8 \\times 8 = 256\\text{x}$$ reduction in tokens\n\n"
        "This is critical for making video generation computationally feasible -- "
        "working in pixel space would require $$T \\times H \\times W$$ tokens "
        "(millions for a short clip).",

        "**Temporal attention**\n\n"
        "Added to existing spatial attention blocks:\n\n"
        "```\n"
        "For each denoising step:\n"
        "  For each layer:\n"
        "    1. Spatial self-attention:  attend within each frame (H' x W' tokens)\n"
        "    2. Temporal self-attention: attend across frames at each spatial location (T' tokens)\n"
        "    3. Cross-attention:         condition on text embedding\n"
        "```\n\n"
        "Temporal attention enables each spatial position to attend to the same position "
        "across all frames -- enforcing consistency of objects, backgrounds, and motion.",

        "**Motion modules**\n\n"
        "Specialized temporal layers that model motion dynamics:\n"
        "- Temporal convolutions (1D conv across time dimension)\n"
        "- Temporal attention with relative position encoding\n"
        "- Often initialized from pre-trained motion patterns",
    ])

    # -- Section 5.4: DiT --
    b.add_section("### 5.4 Sora / DiT Architecture", [
        "OpenAI's Sora introduced the **Diffusion Transformer (DiT)** approach for video:",
    ])

    b.add_diagram_html(DIT_ARCHITECTURE_DIAGRAM)

    b.add_section("### Why DiT matters", [
        "- Replaces U-Net with a plain Transformer -- benefits from the same scaling "
        "laws as LLMs\n"
        "- Spacetime patches treat video as a sequence of 3D tokens -- unified "
        "spatial + temporal\n"
        "- Variable resolution and duration via flexible patch counts\n"
        "- Sora reportedly uses DiT at massive scale (~3B+ params) for minute-long videos",
    ])

    # -- Section 5.5: Challenges --
    b.add_section("### 5.5 Key challenges in video generation", [])

    b.add_diagram_html(VIDEO_CHALLENGES_DIAGRAM)

    # -- Section 5.6: Adobe context --
    b.add_section("### 5.6 Adobe Firefly Video context", [
        "Adobe's approach leverages:\n"
        "- **Image model foundation**: Start from a strong image diffusion model "
        "(Firefly Image)\n"
        "- **Temporal layer insertion**: Add temporal attention/conv layers, "
        "fine-tune on video data\n"
        "- **Creative control**: Adobe emphasizes controllability (camera motion, "
        "style transfer, reference images) beyond just text-to-video\n"
        "- **Commercial safety**: Trained on licensed content, content credentials "
        "for provenance",
    ])

    # -- Section 6: Common Misunderstandings --
    b.add_section("6. Common Misunderstandings (Error Corrections)", [
        '### Misunderstanding 1: "RoPE uses absolute position encoding"\n\n'
        "**Correction:** RoPE applies absolute rotations, but the dot product between "
        "rotated queries and keys depends only on the **relative** position $$m - n$$. "
        "The encoding mechanism is absolute (each position gets a specific rotation), "
        "but the resulting attention pattern is purely relative. This distinction is "
        "the core insight.",

        '### Misunderstanding 2: "PI and NTK-aware scaling do the same thing"\n\n'
        "**Correction:** PI scales all positions uniformly (linear compression). NTK "
        "modifies the base frequency, which preferentially stretches low-frequency "
        "dimensions while preserving high-frequency (local) ones. PI hurts local "
        "pattern recognition; NTK preserves it. YaRN combines both approaches "
        "per-dimension for the best of both worlds.",

        '### Misunderstanding 3: "Video generation just runs an image model on each frame"\n\n'
        "**Correction:** Per-frame generation produces temporally incoherent videos "
        "(flickering, identity changes). Video models must explicitly model temporal "
        "dependencies through temporal attention, temporal convolutions, or 3D "
        "(spacetime) architectures. The temporal modeling is what makes video "
        "generation fundamentally harder than image generation.",

        '### Misunderstanding 4: "Sora uses a U-Net like Stable Diffusion"\n\n'
        "**Correction:** Sora uses a **Diffusion Transformer (DiT)** -- a plain "
        "transformer operating on spacetime patches, not a convolutional U-Net. "
        "This is a key architectural shift: DiT scales like LLMs (more compute = "
        "better quality), while U-Nets have diminishing returns at scale. Many "
        "recent video models (CogVideoX, Hunyuan Video) also adopt DiT.",

        '### Misunderstanding 5: "RoPE can natively handle any context length"\n\n'
        "**Correction:** RoPE trained on length $$L$$ degrades at $$>L$$ because "
        "the rotation angles become out-of-distribution. The attention logits grow "
        'with position distance, causing distribution shift. Context extension '
        "methods (PI, NTK, YaRN) are required to generalize beyond the training "
        'length. "RoPE enables long context" is more accurate than '
        '"RoPE handles long context."',
    ])

    # -- Self-Check --
    b.add_checklist("Self-Check Questions", [
        "**Q1:** Write the RoPE rotation formula for position $$m$$ in "
        "dimension pair $$(2i, 2i+1)$$. Prove that "
        "$$\\tilde{q}_m^T \\tilde{k}_n$$ depends only on $$m - n$$.",
        "**Q2:** Compare Position Interpolation vs NTK-aware scaling: which "
        "frequency dimensions does each method affect? Why does NTK better "
        "preserve local patterns?",
        "**Q3:** In a video diffusion model, explain the difference between "
        "spatial attention and temporal attention. Why can't spatial attention "
        "alone ensure temporal consistency? Cross-reference: how does the "
        "denoising process relate to Day 1 (Diffusion Models)?",
        "**Q4:** Describe the DiT (Diffusion Transformer) architecture. What "
        "advantage does it have over U-Net for scaling to longer, "
        "higher-resolution videos?",
        "**Q5:** For a video with $$T=240$$ frames at $$H=1080, W=1920$$, "
        "calculate the token count before and after 3D VAE compression "
        "(8x spatial, 4x temporal). Why is latent-space diffusion essential?",
    ])

    # -- Quick Reference --
    b.add_section("Quick Reference Card", [
        "```\n"
        "RoPE:       Rotate q,k in 2D subspaces. theta_i = 1/10000^(2i/d).\n"
        "            q_m . k_n depends on (m-n) only. No extra parameters.\n"
        "            Efficient: element-wise cos/sin ops. KV-cache friendly.\n"
        "\n"
        "vs Others:  Sinusoidal=additive,weak relative. Learned=no extrapolation.\n"
        "            ALiBi=attention bias,linear penalty. RoPE=multiplicative,exact relative.\n"
        "\n"
        "Long Ctx:   PI: scale positions by L_train/L_target. Simple but loses local detail.\n"
        "            NTK: modify base freq. Preserves high-freq (local) dimensions.\n"
        "            YaRN: per-dimension PI/NTK + attention temp. Best quality, ~400 steps.\n"
        "\n"
        "Video Gen:  3D VAE compresses T x H x W -> latent (256x reduction typical).\n"
        "            Temporal attention: cross-frame consistency at each spatial location.\n"
        "            DiT (Sora): spacetime patches + transformer. Scales like LLMs.\n"
        "            Challenges: temporal consistency, motion, memory, long videos, data.\n"
        "\n"
        "Adobe:      Firefly Image -> add temporal layers -> Firefly Video.\n"
        "            Emphasis on controllability + commercial safety (licensed data).\n"
        "```",
    ])

    return b


def main() -> None:
    """Build and save the RoPE + Video Generation study note to mle_prep.db."""
    b = build_day4()

    # Build first to validate (fail-fast on single-dollar)
    content = b.build()

    # Validate the built content
    warnings = StudyNoteBuilder.validate(content)
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")

    print(f"[INFO] Built content: {len(content)} chars")

    # Save to database (idempotent -- skips if title exists)
    b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)


if __name__ == "__main__":
    main()
