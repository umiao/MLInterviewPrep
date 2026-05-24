# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Seed script: Insert Adobe Prep Day5 -- Inference Optimization + Project Narrative note.

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
DOC_TITLE = "Adobe Prep Day5: Inference Optimization + Project Narrative"

# -- HTML Diagram: GPU Memory Hierarchy --
GPU_MEMORY_HIERARCHY_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">GPU Memory Hierarchy</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Memory</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Size</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Bandwidth</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Latency</th>\n'
    '</tr>\n'
    '<tr style="background:#4a90d9; color:white;">\n'
    '<td style="padding:8px 16px;"><b>SRAM (on-chip)</b></td>\n'
    '<td style="padding:8px 16px;">~20 MB (A100)</td>\n'
    '<td style="padding:8px 16px;">~19 TB/s</td>\n'
    '<td style="padding:8px 16px;">~1 ns</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">HBM (off-chip)</td>\n'
    '<td style="padding:8px 16px;">40-80 GB (A100)</td>\n'
    '<td style="padding:8px 16px;">~2 TB/s</td>\n'
    '<td style="padding:8px 16px;">~100 ns</td>\n'
    '</tr>\n'
    '</table>\n'
    '<div style="margin-top:12px; color:#ccc;">\n'
    'HBM is ~10x slower than SRAM. Standard attention does 3 HBM round-trips:<br/>\n'
    '(1) read Q,K -> (2) write N x N matrix to HBM -> (3) read it back for softmax x V\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: FlashAttention Tiled Computation --
FLASH_ATTENTION_TILED_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">FlashAttention Tiled Computation</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'Algorithm: FlashAttention (simplified)\n'
    '\n'
    'For each block of queries Q_i (size B_r x d):\n'
    '  Load Q_i into SRAM\n'
    '  Initialize: O_i = 0, l_i = 0, m_i = -inf  (output, sum, max)\n'
    '\n'
    '  For each block of keys/values K_j, V_j (size B_c x d):\n'
    '    Load K_j, V_j into SRAM\n'
    '    Compute S_ij = Q_i @ K_j^T / sqrt(d)    -- in SRAM, B_r x B_c tile\n'
    '    Compute local softmax statistics:\n'
    '      m_ij = rowmax(S_ij)\n'
    '      P_ij = exp(S_ij - m_ij)\n'
    '      l_ij = rowsum(P_ij)\n'
    '    Update running softmax (online softmax trick):\n'
    '      m_new = max(m_i, m_ij)\n'
    '      l_new = exp(m_i - m_new) * l_i + exp(m_ij - m_new) * l_ij\n'
    '      O_i = (exp(m_i - m_new) * l_i * O_i + exp(m_ij - m_new) * P_ij @ V_j) / l_new\n'
    '      m_i, l_i = m_new, l_new\n'
    '\n'
    '  Write O_i to HBM  (only one HBM write per Q block!)\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: IO Complexity Comparison --
IO_COMPLEXITY_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">IO Complexity Comparison</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Method</th>\n'
    '<th style="padding:8px 16px; text-align:left;">HBM Reads/Writes</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Memory</th>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Standard attention</td>\n'
    '<td style="padding:8px 16px;">O(N^2 d + N^2)</td>\n'
    '<td style="padding:8px 16px;">O(N^2)</td>\n'
    '</tr>\n'
    '<tr style="background:#2d6a4f; color:white;">\n'
    '<td style="padding:8px 16px;"><b>FlashAttention</b></td>\n'
    '<td style="padding:8px 16px;">O(N^2 d^2 / M)</td>\n'
    '<td style="padding:8px 16px;">O(N)</td>\n'
    '</tr>\n'
    '</table>\n'
    '<div style="margin-top:8px; color:#ccc; font-size:12px;">\n'
    'M = SRAM size. For typical d = 128 and M = 100KB, FlashAttention does\n'
    '~5-9x fewer HBM accesses. Wall-clock speedup: 2-4x on A100.\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: PagedAttention (vLLM) --
PAGED_ATTENTION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">PagedAttention (vLLM)</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'Traditional KV-cache:\n'
    '  Request 1: [KKKKKKKK-------]  (8 tokens, 15 slots allocated = 7 wasted)\n'
    '  Request 2: [KKKK-----------]  (4 tokens, 15 slots allocated = 11 wasted)\n'
    '  Internal fragmentation: ~60% memory wasted\n'
    '\n'
    'PagedAttention (virtual memory for KV-cache):\n'
    '  Physical blocks: [B0][B1][B2][B3][B4][B5]...\n'
    '  Request 1 page table: B0->B2->B5  (3 blocks, no waste)\n'
    '  Request 2 page table: B1->B3      (2 blocks, no waste)\n'
    '\n'
    '  Benefits:\n'
    '  - Near-zero fragmentation (block-level granularity)\n'
    '  - Copy-on-write for shared prefixes (beam search, system prompts)\n'
    '  - Dynamic allocation: no pre-reservation needed\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: Static vs Continuous Batching --
CONTINUOUS_BATCHING_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Static vs Continuous Batching</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'Static batching:\n'
    '  Step 1: [A1][B1][C1]  -- 3 requests start together\n'
    '  Step 2: [A2][B2][C2]\n'
    '  Step 3: [A3][--][C3]  -- B finished at step 2, slot wasted\n'
    '  Step 4: [A4][--][--]  -- C finished at step 3, slot wasted\n'
    '  Step 5: [A5][--][--]  -- GPU 67% idle!\n'
    '  --> New request D must wait for entire batch to finish\n'
    '\n'
    'Continuous batching (iteration-level scheduling):\n'
    '  Step 1: [A1][B1][C1]\n'
    '  Step 2: [A2][B2][C2]\n'
    '  Step 3: [A3][D1][C3]  -- B done, D immediately fills slot\n'
    '  Step 4: [A4][D2][E1]  -- C done, E immediately fills slot\n'
    '  Step 5: [A5][D3][E2]  -- GPU always full!\n'
    '  --> No idle slots, new requests start immediately\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: Speculative Decoding --
SPECULATIVE_DECODING_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Speculative Decoding</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<pre style="color:#ccc; font-size:13px;">\n'
    'Standard decoding (1 token per forward pass):\n'
    '  Step 1: "The" -> target model -> "cat"\n'
    '  Step 2: "The cat" -> target model -> "sat"\n'
    '  Step 3: "The cat sat" -> target model -> "on"\n'
    '  Total: 3 forward passes of target model\n'
    '\n'
    'Speculative decoding:\n'
    '  Draft step: "The" -> draft model -> "cat sat on" (3 tokens, fast)\n'
    '  Verify step: "The [cat sat on]" -> target model (1 forward pass!)\n'
    '    - Verify each: P_target("cat"|"The") >= P_draft("cat"|"The")? YES\n'
    '    - P_target("sat"|"The cat") >= P_draft("sat"|"The cat")? YES\n'
    '    - P_target("on"|"The cat sat") >= P_draft("on"|"The cat sat")? YES\n'
    '  All accepted! 3 tokens from 1 target forward pass.\n'
    '\n'
    '  If token 2 rejected: keep tokens before rejection, resample from target.\n'
    '  Acceptance rate: ~70-90% for well-matched draft models.\n'
    '</pre>\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: Experience -> Adobe Interview Framing --
PROJECT_MAPPING_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">Experience -> Adobe Interview Framing</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Your Experience</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Adobe-Relevant Topic</th>\n'
    '<th style="padding:8px 16px; text-align:left;">How to Frame It</th>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Operator fusion in inference pipeline</td>\n'
    '<td style="padding:8px 16px;">FlashAttention kernel design</td>\n'
    '<td style="padding:8px 16px;">"I optimized inference by fusing attention operators, '
    'similar to how FlashAttention fuses QKV computation to reduce HBM round-trips. '
    'I understand the memory hierarchy tradeoffs."</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Model compression / pruning work</td>\n'
    '<td style="padding:8px 16px;">GPTQ / AWQ quantization</td>\n'
    '<td style="padding:8px 16px;">"I applied weight quantization to deploy models on '
    'resource-constrained hardware. I can discuss the tradeoff between GPTQ (Hessian-based '
    'compensation) and AWQ (salience-aware scaling)."</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">HW-aware optimization</td>\n'
    '<td style="padding:8px 16px;">KV-cache optimization</td>\n'
    '<td style="padding:8px 16px;">"I profiled GPU memory usage and identified KV-cache as '
    'the bottleneck. I can discuss PagedAttention\'s virtual memory approach and KV-cache '
    'quantization strategies."</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Batch processing pipeline</td>\n'
    '<td style="padding:8px 16px;">Continuous batching / serving</td>\n'
    '<td style="padding:8px 16px;">"I designed batch processing systems that dynamically '
    'schedule work to maximize throughput, analogous to continuous batching in LLM serving."</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">Multi-model inference pipeline</td>\n'
    '<td style="padding:8px 16px;">Speculative decoding</td>\n'
    '<td style="padding:8px 16px;">"I built cascading inference pipelines where a fast model '
    'triages and a large model handles hard cases -- the same draft/verify paradigm as '
    'speculative decoding."</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Distributed training with mixed precision</td>\n'
    '<td style="padding:8px 16px;">FP8 training / inference</td>\n'
    '<td style="padding:8px 16px;">"I used mixed-precision training (fp16/bf16) to double '
    'throughput. FP8 extends this further, and I understand the loss scaling and dynamic '
    'range challenges."</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)


def build_day5() -> "StudyNoteBuilder":
    """Build the Day 5 Inference Optimization + Project Narrative study note."""
    b = StudyNoteBuilder()

    b.set_title("Inference Optimization + Project Narrative (Adobe Prep Day 5)")

    # -- Prerequisites --
    b.add_prerequisites([
        "Transformer self-attention mechanism (Day 1: attention basics)",
        "KV-cache concept (Day 4: RoPE + Long Context -- KV-cache compatibility)",
        "Mixed-precision training fp16/bf16 (Day 3: Distributed Training)",
        "Basic GPU architecture: CUDA cores, memory hierarchy",
    ])

    # -- Term Registry --
    b.add_term("FlashAttention", "Flash Attention",
               "IO-aware exact attention algorithm that tiles computation in SRAM "
               "to avoid materializing the N x N attention matrix in HBM")
    b.add_term("HBM", "High Bandwidth Memory",
               "Off-chip GPU memory (~40-80 GB on A100) with ~2 TB/s bandwidth")
    b.add_term("SRAM", "Static Random-Access Memory",
               "On-chip GPU memory (~20 MB on A100) with ~19 TB/s bandwidth, ~100x faster than HBM")
    b.add_term("GPTQ", "GPT Quantization (Optimal Brain Surgeon-based)",
               "Post-training weight quantization using Hessian-based sequential error compensation")
    b.add_term("AWQ", "Activation-aware Weight Quantization",
               "Protects salient weight channels (top 1% by activation magnitude) via per-channel scaling")
    b.add_term("SmoothQuant", "Smooth Quantization",
               "Migrates quantization difficulty from activations to weights for W8A8 quantization")
    b.add_term("KV-cache", "Key-Value Cache",
               "Stores computed K, V tensors for past tokens to avoid recomputation during autoregressive generation")
    b.add_term("PagedAttention", "Paged Attention (vLLM)",
               "Virtual memory system for KV-cache that eliminates fragmentation using block-level allocation")
    b.add_term("vLLM", "Virtual LLM Serving Engine",
               "High-throughput LLM serving framework built on PagedAttention")
    b.add_term("Continuous Batching", "Iteration-level Batch Scheduling",
               "Allows requests to join/leave the active batch at each decode step, eliminating idle GPU slots")
    b.add_term("Speculative Decoding", "Draft-and-Verify Decoding",
               "Uses a small draft model to propose K tokens, verified in parallel by the target model; provably lossless")
    b.add_term("OBS", "Optimal Brain Surgeon",
               "Framework for weight pruning/quantization using Hessian information to compensate errors")
    b.add_term("TensorRT-LLM", "NVIDIA TensorRT for LLMs",
               "NVIDIA's inference engine with kernel fusion and in-flight batching for LLM serving")

    # -- Section 1: FlashAttention --
    b.add_section("1. FlashAttention", [
        "Modern LLMs are expensive to serve. Understanding the full inference optimization "
        "stack -- from attention-level tricks (FlashAttention) to weight compression "
        "(quantization) to serving-system designs (continuous batching, speculative decoding) "
        "-- is critical for Adobe-scale deployment. This note also maps your project "
        "experience to Adobe interview framing.",

        "### The memory bottleneck\n\n"
        "Standard self-attention computes:",

        FormulaBlock(
            latex=r"\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) V",
            explanation="The standard attention formula:",
        ),

        "For sequence length $$N$$ and head dimension $$d$$:\n"
        "- $$QK^T$$ produces an $$N \\times N$$ attention matrix\n"
        "- This matrix must be materialized in GPU HBM (High Bandwidth Memory)\n"
        "- Memory: $$O(N^2)$$. For $$N = 8192$$, that is 512 MB per head per layer (fp32)\n\n"
        "The bottleneck is not FLOPs but **memory I/O**: reading/writing the $$N \\times N$$ "
        "matrix from HBM is the dominant cost.",

        "### SRAM vs HBM",
    ])

    b.add_diagram_html(GPU_MEMORY_HIERARCHY_DIAGRAM)

    b.add_section("### FlashAttention algorithm (tiling)", [
        "**Core idea:** Never materialize the full $$N \\times N$$ attention matrix. "
        "Instead, compute attention in **tiles** that fit in SRAM.",
    ])

    b.add_diagram_html(FLASH_ATTENTION_TILED_DIAGRAM)

    b.add_section("### Online softmax insight", [
        '**Key insight:** The "online softmax" trick maintains running statistics '
        "(max and sum) so we can compute exact softmax without storing the full "
        "$$N \\times N$$ matrix. Each tile is computed entirely in SRAM, with only "
        "Q, K, V reads and O writes going to HBM.",

        "### IO complexity",
    ])

    b.add_diagram_html(IO_COMPLEXITY_DIAGRAM)

    b.add_section("### FlashAttention-2 and -3", [
        "**FlashAttention-2 improvements:**\n"
        "- Better **work partitioning** between GPU thread blocks (reduce non-matmul FLOPs)\n"
        "- Parallelism over the **sequence length** dimension (not just batch/heads)\n"
        "- ~2x faster than FlashAttention-1, reaching 50-73% of theoretical matmul FLOPS\n\n"
        "**FlashAttention-3 (Hopper GPUs):**\n"
        "- Exploits **asynchronous execution** (TMA + WGMMA on H100)\n"
        "- **FP8 support** for even higher throughput\n"
        "- Intra-warp pipelining: overlap GEMM and softmax computation",
    ])

    # -- Section 2: Quantization --
    b.add_section("2. Quantization", [
        "### Why quantize?\n\n"
        "A 70B parameter model in fp16 requires $$70 \\times 10^9 \\times 2 = 140$$ GB -- "
        "more than a single A100 (80GB). Quantization reduces weight (and optionally "
        "activation) precision to fit larger models on fewer GPUs and increase throughput.\n\n"
        "Cross-reference: this connects to Day 3 (Distributed Training) -- quantization "
        "reduces the memory footprint that tensor/pipeline parallelism must distribute.",

        "### Quantization methods comparison",
    ])

    b.add_comparison_table(
        headers=["Method", "What's quantized", "Precision", "Calibration", "Key idea"],
        rows=[
            ["GPTQ", "Weights only", "INT4 / INT3",
             "Post-training (128 samples)",
             "Layer-wise OBS: quantize columns sequentially, compensate error in remaining columns"],
            ["AWQ", "Weights only", "INT4",
             "Post-training",
             "Protect salient weights (1% channels with most activation magnitude) via per-channel scaling"],
            ["Weight-only INT4", "Weights only", "INT4",
             "RTN (round-to-nearest)",
             "Simplest: group-wise round-to-nearest with scale/zero-point per group (e.g., 128 elements)"],
            ["W8A8", "Weights + activations", "INT8 / FP8",
             "Post-training or QAT",
             "Quantize both W and A to 8-bit. Enables INT8 GEMM on tensor cores. SmoothQuant migrates "
             "difficulty from activations to weights."],
        ],
        title="Quantization Methods Comparison",
    )

    b.add_section("### GPTQ deep-dive", [
        "Based on Optimal Brain Surgeon (OBS). For each layer:\n\n"
        "1. Compute Hessian $$H = 2X^TX$$ from calibration data (128 samples typical)\n"
        "2. For each column $$j$$ (in order):\n"
        "   - Quantize weight $$w_j$$ to nearest quantized value $$\\hat{w}_j$$\n"
        "   - Compute quantization error: $$\\delta_j = w_j - \\hat{w}_j$$\n"
        "   - **Compensate** remaining columns:",

        FormulaBlock(
            latex=r"W_{:, j+1:} \mathrel{-}= \delta_j \cdot \frac{H_{j, j+1:}}{H_{j,j}}",
            explanation="The Hessian-based error compensation formula (step 2c of GPTQ):",
        ),

        "3. This sequential error compensation keeps the layer output close to fp16 output\n\n"
        "**Why GPTQ works well:** The Hessian-based compensation means each quantization "
        "error is optimally distributed across remaining weights, not just accumulated.",
    ])

    b.add_section("### AWQ deep-dive", [
        "Key observation: not all weights are equally important. ~1% of weight channels "
        "correspond to large activation magnitudes (salient channels). Quantizing these "
        "causes disproportionate error.\n\n"
        "AWQ solution:\n"
        "1. Find salient channels: sort by activation magnitude, top 1% are \"salient\"\n"
        "2. Apply per-channel scaling: $$s_j = \\max(|X_j|)^\\alpha$$ with $$\\alpha \\approx 0.5$$\n"
        "3. Scale weights: $$W' = W \\cdot \\text{diag}(s)$$, quantize $$W'$$\n"
        "4. Absorb scaling into previous layer's output (no runtime overhead)\n\n"
        "**AWQ vs GPTQ:**\n"
        "- AWQ is faster to quantize (no sequential column processing)\n"
        "- AWQ often has better quality at INT4 (protects the channels that matter most)\n"
        "- GPTQ has more theoretical backing (OBS framework)",
    ])

    b.add_section("### SmoothQuant (for W8A8)", [
        "Activations have outlier channels that are hard to quantize. SmoothQuant migrates "
        "the quantization difficulty from activations to weights:",

        FormulaBlock(
            latex=r"Y = (X \text{diag}(s)^{-1}) \cdot (\text{diag}(s) W) = \hat{X} \hat{W}",
            explanation="The SmoothQuant transformation -- absorb activation outliers into weights:",
        ),

        "Choose $$s$$ to balance the per-channel ranges: "
        "$$s_j = \\max(|X_j|)^\\alpha / \\max(|W_j|)^{1-\\alpha}$$.\n"
        "After smoothing, both $$\\hat{X}$$ and $$\\hat{W}$$ have manageable ranges "
        "for INT8 quantization.",
    ])

    # -- Section 3: Serving Optimization --
    b.add_section("3. Serving Optimization", [
        "### 3.1 KV-Cache\n\n"
        "During autoregressive generation, each new token attends to all previous tokens. "
        "Without caching, we recompute all keys and values at every step: $$O(N^2)$$ total "
        "compute for $$N$$ tokens.\n\n"
        "**KV-Cache:** Store computed K, V tensors for past tokens. Each new token only "
        "computes its own Q, K, V and attends to cached K, V.\n\n"
        "- Compute savings: from $$O(N^2 d)$$ to $$O(Nd)$$ per step\n"
        "- Memory cost:",

        FormulaBlock(
            latex=r"\text{KV-cache} = 2 \times L \times N \times H \times d \times \text{bytes}",
            explanation="KV-cache memory formula (2 for K and V, L layers, N tokens, H heads, "
                        "d head dimension):",
        ),

        "For Llama-70B at 4096 tokens: ~10 GB of KV-cache per request (fp16).\n"
        "Cross-reference: Day 4 (RoPE) discusses how RoPE is KV-cache friendly because "
        "rotation is per-token with no recomputation needed.",

        "### 3.2 KV-Cache Quantization\n\n"
        "KV-cache is the biggest memory consumer during inference. Quantizing it:\n"
        "- **INT8 KV-cache:** Halves memory with minimal quality loss (per-token quantization)\n"
        "- **INT4 KV-cache:** 4x reduction, slight quality degradation on long contexts\n"
        "- **Per-head vs per-token quantization:** Per-head is simpler; per-token adapts better to outliers",

        "### 3.3 PagedAttention (vLLM)\n\n"
        "**Problem:** KV-cache is allocated as contiguous memory per request. With variable-length "
        "sequences, this causes **internal fragmentation** (allocated but unused memory) and "
        "prevents sharing prefixes between requests.",
    ])

    b.add_diagram_html(PAGED_ATTENTION_DIAGRAM)

    b.add_section("### PagedAttention impact", [
        "**Impact:** vLLM achieves 2-4x higher throughput than HuggingFace text-generation-inference "
        "by reducing KV-cache memory waste from ~60% to ~4%.",

        "### 3.4 Continuous Batching\n\n"
        "**Problem:** Traditional batching waits for all requests in a batch to finish before "
        "processing new ones. Short requests waste GPU cycles waiting for long ones.",
    ])

    b.add_diagram_html(CONTINUOUS_BATCHING_DIAGRAM)

    b.add_section("### Continuous batching implementation", [
        "**Implementation:** Orca (2022) introduced iteration-level scheduling. Each decode step, "
        "the scheduler can add/remove requests from the active batch. Combined with PagedAttention, "
        "this maximizes GPU utilization.",

        "### 3.5 Speculative Decoding\n\n"
        "**Problem:** Autoregressive decoding is inherently sequential -- each token depends on "
        "the previous one. The GPU is underutilized because generating one token uses the same "
        "memory bandwidth as generating many.\n\n"
        "**Idea:** Use a small **draft model** to generate $$K$$ candidate tokens quickly, then "
        "verify all $$K$$ tokens in **parallel** with the large target model.",
    ])

    b.add_diagram_html(SPECULATIVE_DECODING_DIAGRAM)

    b.add_section("### Speculative decoding properties", [
        "**Key properties:**\n"
        "- **Lossless:** The output distribution is identical to the target model "
        "(rejection sampling ensures this)\n"
        "- **Speedup:** ~$$K \\times \\text{acceptance\\_rate}$$ tokens per target forward pass\n"
        "- Typical: 2-3x speedup with $$K = 5$$ and 70-80% acceptance rate\n"
        "- **Draft model:** Can be a smaller version (e.g., 7B draft for 70B target), "
        "a quantized version, or even a simple n-gram model",

        "### 3.6 Serving stack comparison",
    ])

    b.add_comparison_table(
        headers=["Framework", "Key feature", "Quantization", "Batching"],
        rows=[
            ["**vLLM**", "PagedAttention", "GPTQ, AWQ, FP8", "Continuous"],
            ["TensorRT-LLM", "NVIDIA kernel fusion", "INT4/INT8/FP8", "In-flight batching"],
            ["TGI (HuggingFace)", "Easy deployment", "GPTQ, bitsandbytes", "Continuous"],
            ["SGLang", "RadixAttention (prefix caching)", "AWQ, FP8", "Continuous"],
        ],
        title="LLM Serving Frameworks",
    )

    # -- Section 4: Project Narrative Mapping --
    b.add_section("4. Project Narrative Mapping", [
        "Map your real project experience to Adobe interview framing. The goal is to show "
        "that you have hands-on experience with the concepts Adobe cares about, even if "
        "you used them in a different context.",
    ])

    b.add_diagram_html(PROJECT_MAPPING_DIAGRAM)

    b.add_section("### How to use this table in interviews", [
        "1. **Listen for the keyword** in the interviewer's question\n"
        "2. **Lead with your experience** (\"In my project, I...\")\n"
        "3. **Bridge to the Adobe concept** (\"This is similar to how FlashAttention...\")\n"
        "4. **Show depth** by discussing tradeoffs or limitations you encountered\n"
        "5. **Connect to Adobe's scale** (\"At Adobe's scale with Firefly, this becomes "
        "even more critical because...\")",
    ])

    # -- Section 5: Common Misunderstandings --
    b.add_section("5. Common Misunderstandings (Error Corrections)", [
        '### Misunderstanding 1: "FlashAttention reduces the number of FLOPs"\n\n'
        "**Correction:** FlashAttention performs the **same number of FLOPs** as standard attention "
        "(actually slightly more due to recomputation in the backward pass). The speedup comes "
        "entirely from reducing **HBM I/O** -- the bottleneck is memory bandwidth, not compute. "
        "FlashAttention is IO-aware, not compute-efficient.",

        '### Misunderstanding 2: "Quantization always degrades model quality significantly"\n\n'
        "**Correction:** INT4 weight-only quantization (GPTQ, AWQ) typically loses <1% on "
        "benchmarks for models >7B parameters. The key insight is that larger models are more "
        "robust to quantization because individual weight values matter less when there are "
        "billions of them. The quality gap narrows with model scale.",

        '### Misunderstanding 3: "Speculative decoding changes the output distribution"\n\n'
        "**Correction:** Speculative decoding with proper rejection sampling produces the "
        "**exact same distribution** as standard autoregressive decoding from the target model. "
        "The draft model only proposes candidates -- rejected tokens are resampled from the "
        "corrected distribution. This is provably lossless (see Leviathan et al., 2023).",

        '### Misunderstanding 4: "KV-cache is just an optimization, you can skip it"\n\n'
        "**Correction:** Without KV-cache, generating $$N$$ tokens requires $$O(N^2)$$ total "
        "compute (recomputing all attention at each step). With KV-cache, it is $$O(N)$$ per "
        "step. For a 1000-token generation, that is 1000x compute difference. KV-cache is not "
        "optional for practical LLM serving -- the question is how to manage it efficiently "
        "(PagedAttention, quantization, eviction policies).",

        '### Misunderstanding 5: "Continuous batching means larger batch sizes"\n\n'
        "**Correction:** Continuous batching is about **scheduling granularity**, not batch size. "
        "Static batching processes a fixed batch until all requests complete. Continuous batching "
        "allows per-iteration scheduling: finished requests leave and new ones join at each decode "
        "step. This eliminates idle slots, increasing throughput by 2-4x without changing the "
        "maximum batch size.",
    ])

    # -- Self-Check --
    b.add_checklist("Self-Check Questions", [
        "**Q1:** Draw the FlashAttention tiling algorithm. Why does it reduce HBM I/O "
        "from $$O(N^2)$$ to $$O(N^2 d^2/M)$$? What is the \"online softmax\" trick?",
        "**Q2:** Compare GPTQ vs AWQ: what calibration data does each need? How does "
        "GPTQ compensate for quantization error? Why does AWQ focus on \"salient\" channels?",
        "**Q3:** Explain PagedAttention. How does it solve KV-cache fragmentation? How "
        "does copy-on-write help with beam search?",
        "**Q4:** Describe speculative decoding step by step. Why is it provably lossless? "
        "What determines the acceptance rate?",
        "**Q5:** You have a 70B model and 2x A100-80GB GPUs. Walk through the inference "
        "optimization stack you would deploy (quantization + serving framework + batching "
        "strategy). Cross-reference: how does this connect to Day 3's tensor parallelism "
        "for splitting across 2 GPUs?",
    ])

    # -- Quick Reference --
    b.add_section("Quick Reference Card", [
        "```\n"
        "FlashAttention: Tiled attention in SRAM. Never materializes N x N matrix.\n"
        "    IO: O(N^2 d^2 / M) vs standard O(N^2 d + N^2). Memory: O(N) vs O(N^2).\n"
        "    Key trick: online softmax (running max + sum). Same FLOPs, fewer HBM trips.\n"
        "    FA2: better parallelism. FA3: async execution + FP8 on Hopper GPUs.\n"
        "\n"
        "Quantization:\n"
        "    GPTQ: OBS-based, column-sequential, Hessian compensation. INT4, 128 calibration samples.\n"
        "    AWQ: protect 1% salient channels via per-channel scaling. Faster than GPTQ.\n"
        "    W8A8: SmoothQuant migrates outliers from activations to weights. INT8 GEMM.\n"
        "    Rule of thumb: INT4 weight-only loses <1% for models >7B.\n"
        "\n"
        "KV-Cache: 2 * L * N * H * d bytes. Biggest memory consumer at inference time.\n"
        "    PagedAttention: virtual memory for KV-cache. Blocks, page tables, CoW.\n"
        "    vLLM: 2-4x throughput vs HF TGI via near-zero fragmentation.\n"
        "\n"
        "Continuous Batching: iteration-level scheduling. No idle slots.\n"
        "    Finished requests leave, new ones join at each decode step.\n"
        "\n"
        "Speculative Decoding: Draft model proposes K tokens, target verifies in 1 pass.\n"
        "    Lossless (rejection sampling). ~2-3x speedup with 70-80% acceptance rate.\n"
        "    Draft = smaller model, quantized model, or n-gram model.\n"
        "\n"
        "Project Mapping: operator fusion->FlashAttention, compression->GPTQ/AWQ,\n"
        "    HW profiling->KV-cache, batch pipeline->continuous batching,\n"
        "    cascade inference->speculative decoding, mixed precision->FP8.\n"
        "```",
    ])

    return b


def main() -> None:
    """Build and save the Inference Optimization + Project Narrative study note to mle_prep.db."""
    b = build_day5()

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
