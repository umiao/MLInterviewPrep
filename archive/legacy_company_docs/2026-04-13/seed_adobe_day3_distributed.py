"""Seed script: Insert Adobe Prep Day3 -- Distributed Training study note.

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
DOC_TITLE = "Adobe Prep Day3: Distributed Training (DP/TP/PP/FSDP)"

# -- HTML Diagram: Four Parallelism Strategies Overview --
PARALLELISM_OVERVIEW_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:16px; font-size:16px; color:#fff; '
    'font-weight:bold;">How Each Strategy Splits Work</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; '
    'color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Strategy</th>\n'
    '<th style="padding:8px 16px; text-align:left;">What is split</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Across</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Communication</th>\n'
    '</tr>\n'
    '<tr style="background:#4a90d9; color:white;">\n'
    '<td style="padding:8px 16px;">Data Parallel (DP)</td>\n'
    '<td style="padding:8px 16px;">Data (mini-batch)</td>\n'
    '<td style="padding:8px 16px;">All GPUs</td>\n'
    '<td style="padding:8px 16px;">AllReduce gradients</td>\n'
    '</tr>\n'
    '<tr style="background:#6b4c9a; color:white;">\n'
    '<td style="padding:8px 16px;">Tensor Parallel (TP)</td>\n'
    '<td style="padding:8px 16px;">Weight matrices (intra-layer)</td>\n'
    '<td style="padding:8px 16px;">GPUs within a node</td>\n'
    '<td style="padding:8px 16px;">AllReduce activations</td>\n'
    '</tr>\n'
    '<tr style="background:#2d6a4f; color:white;">\n'
    '<td style="padding:8px 16px;">Pipeline Parallel (PP)</td>\n'
    '<td style="padding:8px 16px;">Layers (inter-layer)</td>\n'
    '<td style="padding:8px 16px;">Across nodes</td>\n'
    '<td style="padding:8px 16px;">Point-to-point activations</td>\n'
    '</tr>\n'
    '<tr style="background:#d4a017; color:black;">\n'
    '<td style="padding:8px 16px;">FSDP / ZeRO</td>\n'
    '<td style="padding:8px 16px;">Parameters + optimizer states</td>\n'
    '<td style="padding:8px 16px;">All GPUs</td>\n'
    '<td style="padding:8px 16px;">AllGather params, ReduceScatter grads</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: ZeRO Stages Memory --
ZERO_STAGES_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">ZeRO Memory per GPU '
    '($$P$$ params, $$N$$ GPUs, FP16 + AdamW)</div>\n'
    '<table style="margin:0 auto; border-collapse:collapse; '
    'color:#e0e0e0; font-size:13px;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:8px 16px; text-align:left;">Stage</th>\n'
    '<th style="padding:8px 16px; text-align:left;">What is sharded</th>\n'
    '<th style="padding:8px 16px; text-align:left;">Memory per GPU</th>\n'
    '<th style="padding:8px 16px; text-align:left;">vs Baseline (16P)</th>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">Baseline (DDP)</td>\n'
    '<td style="padding:8px 16px;">Nothing</td>\n'
    '<td style="padding:8px 16px;">$$16P$$ bytes</td>\n'
    '<td style="padding:8px 16px;">1x</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">ZeRO Stage 1</td>\n'
    '<td style="padding:8px 16px;">Optimizer states</td>\n'
    '<td style="padding:8px 16px;">$$4P + 12P/N$$ bytes</td>\n'
    '<td style="padding:8px 16px;">~4x reduction at $$N=64$$</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 16px;">ZeRO Stage 2</td>\n'
    '<td style="padding:8px 16px;">Optimizer + gradients</td>\n'
    '<td style="padding:8px 16px;">$$2P + (2P + 12P)/N$$ bytes</td>\n'
    '<td style="padding:8px 16px;">~8x at $$N=64$$</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 16px;">ZeRO Stage 3 (FSDP)</td>\n'
    '<td style="padding:8px 16px;">Optimizer + gradients + parameters</td>\n'
    '<td style="padding:8px 16px;">$$16P/N$$ bytes</td>\n'
    '<td style="padding:8px 16px;">$$N$$x reduction</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)

# -- HTML Diagram: 3D Parallelism Layout --
THREE_D_PARALLELISM_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="text-align:center; font-size:14px;">\n'
    '<div style="margin-bottom:12px; font-size:16px; color:#fff; '
    'font-weight:bold;">3D Parallelism Layout (64 GPUs = 8 nodes x 8 GPUs/node)</div>\n'
    '<div style="color:#aaa; margin-bottom:12px;">\n'
    'TP=8 (within node, NVLink) x PP=4 (across nodes) x DP=2 (remaining)\n'
    '</div>\n'
    '<div style="color:#ccc; text-align:left; padding:0 20px;">\n'
    '<div>Node 0 (8 GPUs): TP group for pipeline stage 0, DP replica 0</div>\n'
    '<div>Node 1 (8 GPUs): TP group for pipeline stage 0, DP replica 1</div>\n'
    '<div>Node 2 (8 GPUs): TP group for pipeline stage 1, DP replica 0</div>\n'
    '<div>Node 3 (8 GPUs): TP group for pipeline stage 1, DP replica 1</div>\n'
    '<div>Node 4 (8 GPUs): TP group for pipeline stage 2, DP replica 0</div>\n'
    '<div>Node 5 (8 GPUs): TP group for pipeline stage 2, DP replica 1</div>\n'
    '<div>Node 6 (8 GPUs): TP group for pipeline stage 3, DP replica 0</div>\n'
    '<div>Node 7 (8 GPUs): TP group for pipeline stage 3, DP replica 1</div>\n'
    '</div>\n'
    '<div style="color:#888; margin-top:12px; font-size:12px;">\n'
    'Total: 64 GPUs | TP*PP*DP = 8*4*2 = 64\n'
    '</div>\n'
    '</div>\n'
    '</div>'
)


def build_day3() -> "StudyNoteBuilder":
    """Build the Day 3 Distributed Training study note."""
    b = StudyNoteBuilder()

    b.set_title(
        "Distributed Training: DP / TP / PP / FSDP (Adobe Prep Day 3)"
    )

    # -- Prerequisites --
    b.add_prerequisites([
        "Neural network training fundamentals (forward pass, backward pass, gradient descent)",
        "GPU memory model (HBM, SRAM) -- see Day 5: Inference Optimization",
        "Basic linear algebra (matrix multiplication, partitioning)",
        "Day 2: RLHF/DPO (cross-reference: PPO training requires distributed infra at scale)",
    ])

    # -- Term Registry --
    b.add_term(
        "DP", "Data Parallelism",
        "Replicate entire model on each GPU, split data; AllReduce gradients after each step"
    )
    b.add_term(
        "TP", "Tensor Parallelism",
        "Split weight matrices intra-layer across GPUs; requires high-bandwidth interconnect (NVLink)"
    )
    b.add_term(
        "PP", "Pipeline Parallelism",
        "Split model layers across GPUs in a pipeline; introduces bubble overhead"
    )
    b.add_term(
        "FSDP", "Fully Sharded Data Parallelism",
        "PyTorch implementation of ZeRO Stage 3; shards params, grads, and optimizer states"
    )
    b.add_term(
        "ZeRO", "Zero Redundancy Optimizer",
        "DeepSpeed technique with 3 stages of progressive sharding to eliminate memory redundancy"
    )
    b.add_term(
        "AllReduce", "AllReduce Collective",
        "Communication primitive that sums tensors across all GPUs and distributes the result"
    )
    b.add_term(
        "AllGather", "AllGather Collective",
        "Communication primitive that concatenates shards from all GPUs so each has the full tensor"
    )
    b.add_term(
        "ReduceScatter", "ReduceScatter Collective",
        "Communication primitive that reduces (sums) and distributes disjoint shards to each GPU"
    )
    b.add_term(
        "NVLink", "NVLink Interconnect",
        "High-bandwidth GPU-to-GPU interconnect (600+ GB/s), used for intra-node TP communication"
    )
    b.add_term(
        "activation checkpointing", "Activation Checkpointing",
        "Trade compute for memory: recompute activations during backward instead of storing them"
    )
    b.add_term(
        "3D parallelism", "3D Parallelism",
        "Composition of TP (intra-node) x PP (cross-node) x DP (remaining GPUs)"
    )
    b.add_term(
        "DDP", "Distributed Data Parallel",
        "PyTorch's standard DP implementation with overlapped gradient AllReduce"
    )

    # -- Section 1: Overview --
    b.add_section("1. The Four Parallelism Strategies -- Overview", [
        ("> Training large models on multiple GPUs requires splitting work across devices.\n"
         "> Four parallelism strategies exist -- each splits a different axis. Master when\n"
         "> to use which, how they compose into 3D parallelism, and the memory math."),
    ])

    b.add_diagram_html(PARALLELISM_OVERVIEW_DIAGRAM)

    # -- Section 2: Data Parallelism --
    b.add_section("2. Data Parallelism (DP)", [
        "The simplest strategy: every GPU holds a **full copy** of the model "
        "and processes a different mini-batch slice.",

        "### How it works\n\n"
        "1. **Replicate** the model on $$N$$ GPUs\n"
        "2. **Split** the global batch $$B$$ into $$N$$ micro-batches of size $$B/N$$\n"
        "3. Each GPU computes forward + backward on its micro-batch\n"
        "4. **AllReduce** gradients across all GPUs (sum and average)\n"
        "5. Each GPU updates its local copy with the averaged gradient",

        "### AllReduce\n\n"
        "The AllReduce operation ensures every GPU ends up with the same averaged "
        "gradient. Implemented as ReduceScatter + AllGather (ring-based) for bandwidth efficiency.",

        FormulaBlock(
            latex=r"\bar{g} = \frac{1}{N} \sum_{i=1}^{N} g_i",
            explanation="Averaged gradient across all GPUs after AllReduce:",
        ),

        FormulaBlock(
            latex=r"\text{AllReduce volume} = 2 \cdot \frac{N-1}{N} "
                  r"\cdot |\theta| \approx 2|\theta| \quad \text{(for large } N \text{)}",
            explanation="Communication cost per step, where $$|\\theta|$$ is the total parameter count. "
                        "The factor of 2 comes from ReduceScatter + AllGather:",
        ),

        "### Limitations\n\n"
        "- **Memory**: Each GPU must hold the full model + optimizer states + activations\n"
        "- For a model with $$P$$ parameters in FP16 + AdamW optimizer:\n"
        "  - Parameters: $$2P$$ bytes (FP16)\n"
        "  - Gradients: $$2P$$ bytes (FP16)\n"
        "  - Optimizer states: $$12P$$ bytes (FP32 params + FP32 momentum + FP32 variance)\n"
        "  - **Total: $$16P$$ bytes per GPU** (same on every GPU -- wasteful!)\n"
        "- Does not scale beyond models that fit on a single GPU",

        "### PyTorch DDP\n\n"
        "```python\n"
        "# PyTorch DistributedDataParallel\n"
        "model = DDP(model, device_ids=[local_rank])\n"
        "# Automatically: gradient AllReduce overlapped with backward pass\n"
        "```\n\n"
        "Key optimization: **gradient bucketing** -- overlaps communication with "
        "computation by starting AllReduce on earlier layers while later layers "
        "are still computing backward.",
    ])

    # -- Section 3: Tensor Parallelism --
    b.add_section("3. Tensor Parallelism (TP)", [
        "Splits individual **weight matrices** across GPUs within a single layer. "
        "Best for intra-node (fast NVLink interconnect).",

        "### MLP column-row split\n\n"
        "For a 2-layer MLP: $$Y = \\text{GeLU}(XA) \\cdot B$$",

        "**Column parallel (first linear):**\n\n"
        "Split $$A$$ column-wise across $$N$$ GPUs:",

        FormulaBlock(
            latex=r"A = [A_1 | A_2 | \ldots | A_N]",
            explanation="Each GPU $$i$$ computes $$Y_i = \\text{GeLU}(X A_i)$$ independently. "
                        "GeLU is element-wise, so no communication needed here:",
        ),

        "**Row parallel (second linear):**\n\n"
        "Split $$B$$ row-wise:",

        FormulaBlock(
            latex=r"B = \begin{bmatrix} B_1 \\ B_2 \\ \vdots \\ B_N \end{bmatrix}",
            explanation="Each GPU $$i$$ computes $$Z_i = Y_i B_i$$ (partial result):",
        ),

        FormulaBlock(
            latex=r"Z = \sum_{i=1}^{N} Z_i",
            explanation="Then **AllReduce** to get the final output:",
        ),

        "**Communication:** 1 AllReduce per MLP block (after the row-parallel layer).",

        "### Attention head split\n\n"
        "Multi-head attention is naturally parallelizable:\n"
        "- $$h$$ attention heads split across $$N$$ GPUs ($$h/N$$ heads per GPU)\n"
        "- Each GPU computes $$Q_i, K_i, V_i$$ projections and attention for its heads\n"
        "- After attention, the output projections are row-parallel\n"
        "- **1 AllReduce** per attention block",

        FormulaBlock(
            latex=r"\text{TP comm per layer} = 2 \times \text{AllReduce}(d_{\text{model}}) "
                  r"\quad \text{(1 for MLP + 1 for attention)}",
            explanation="Communication pattern per transformer layer:",
        ),

        "### When to use TP\n\n"
        "- **Within a node** where NVLink provides 600+ GB/s bandwidth\n"
        "- Typical TP degree: 2, 4, or 8 (matching GPUs per node)\n"
        "- Cross-node TP is usually too slow (network bandwidth is 10-100x lower than NVLink)",
    ])

    # -- Section 4: Pipeline Parallelism --
    b.add_section("4. Pipeline Parallelism (PP)", [
        "Splits the model **layer-wise** across GPUs. GPU 0 gets layers 0-9, "
        "GPU 1 gets layers 10-19, etc.",

        "### Naive pipeline (bubble problem)\n\n"
        "With $$N$$ pipeline stages and 1 micro-batch:\n\n"
        "```\n"
        "GPU 0: [Fwd]...........[Bwd]\n"
        "GPU 1:      [Fwd]...........[Bwd]\n"
        "GPU 2:           [Fwd]...........[Bwd]\n"
        "GPU 3:                [Fwd]...........[Bwd]\n"
        "                                          ^^^ Lots of idle time (bubble)\n"
        "```",

        FormulaBlock(
            latex=r"\text{Bubble}_{\text{naive}} = \frac{N - 1}{N}"
                  r" \quad \text{(e.g., 75\% idle for 4 stages!)}",
            explanation="**Bubble fraction** with naive pipelining:",
        ),

        "### Micro-batch pipelining (GPipe / PipeDream)\n\n"
        "Split the mini-batch into $$M$$ micro-batches and pipeline them:\n\n"
        "```\n"
        "GPU 0: [F1][F2][F3][F4]............[B4][B3][B2][B1]\n"
        "GPU 1:     [F1][F2][F3][F4]....[B4][B3][B2][B1]\n"
        "GPU 2:         [F1][F2][F3][F4][B4][B3][B2][B1]\n"
        "GPU 3:             [F1][F2][F3][F4][B3][B2][B1]\n"
        "```",

        FormulaBlock(
            latex=r"\text{Bubble}_{\text{micro}} = \frac{N - 1}{N + M - 1}",
            explanation="**Reduced bubble fraction.** With $$M \\gg N$$, bubble fraction "
                        "approaches 0. Typical: $$M = 4N$$ gives ~20% bubble:",
        ),

        "### Communication\n\n"
        "- Only **point-to-point** between adjacent stages (activation tensors)\n"
        "- Much less bandwidth than AllReduce -- good for cross-node\n"
        "- Communication volume: activation size of the boundary layer",
    ])

    b.add_comparison_table(
        headers=["Method", "Key Feature"],
        rows=[
            ["**GPipe**", "All-forward then all-backward, gradient accumulation over micro-batches"],
            ["**PipeDream-1F1B**", "Interleave 1 forward + 1 backward per step, reduces peak memory"],
            ["**Interleaved PP**", "Assign non-contiguous layers to stages (virtual stages)"],
        ],
        title="Pipeline Parallelism Variants",
    )

    # -- Section 5: FSDP / ZeRO --
    b.add_section("5. FSDP / ZeRO (Fully Sharded Data Parallelism)", [
        "FSDP addresses the memory redundancy of standard DP by **sharding** "
        "parameters, gradients, and optimizer states across GPUs.",

        "### ZeRO stages",
    ])

    b.add_diagram_html(ZERO_STAGES_DIAGRAM)

    b.add_section("### ZeRO Stage 1: Shard optimizer states", [
        "- Each GPU stores $$1/N$$ of the optimizer states (momentum, variance)\n"
        "- Parameters and gradients are still fully replicated\n"
        "- After AllReduce of gradients, each GPU updates only its $$1/N$$ shard of optimizer states\n"
        "- Then AllGather to broadcast updated parameters",
    ])

    b.add_section("### ZeRO Stage 2: + Shard gradients", [
        "- Gradients are also sharded: use **ReduceScatter** instead of AllReduce\n"
        "- Each GPU only keeps the $$1/N$$ gradient shard it needs for its optimizer shard\n"
        "- Eliminates gradient memory redundancy",
    ])

    b.add_section("### ZeRO Stage 3 / FSDP: + Shard parameters", [
        "- Parameters themselves are sharded -- each GPU holds only $$1/N$$ of the weights\n"
        "- **Forward pass:** AllGather parameters for each layer, compute, discard non-owned params\n"
        "- **Backward pass:** AllGather parameters again, compute gradients, ReduceScatter gradients",

        FormulaBlock(
            latex=r"\text{Volume per step} = 3 \times |\theta| "
                  r"\quad \text{(1.5x more than DDP's } 2|\theta| \text{)}",
            explanation="**Communication (Stage 3).** Breakdown: AllGather in forward "
                        "($$|\\theta|$$) + AllGather in backward ($$|\\theta|$$) + "
                        "ReduceScatter gradients ($$|\\theta|$$):",
        ),

        "### PyTorch FSDP\n\n"
        "```python\n"
        "from torch.distributed.fsdp import FullyShardedDataParallel as FSDP\n"
        "\n"
        "model = FSDP(\n"
        "    model,\n"
        "    sharding_strategy=ShardingStrategy.FULL_SHARD,  # Stage 3\n"
        "    auto_wrap_policy=transformer_auto_wrap_policy,\n"
        "    mixed_precision=MixedPrecision(param_dtype=torch.float16),\n"
        ")\n"
        "```",
    ])

    b.add_comparison_table(
        headers=["Aspect", "DDP", "FSDP"],
        rows=[
            ["**Memory per GPU**", "$$16P$$", "$$16P/N$$"],
            ["**Communication**", "$$2|\\theta|$$", "$$3|\\theta|$$ (1.5x more)"],
            ["**Implementation**", "Simple", "More complex (AllGather/ReduceScatter scheduling)"],
            ["**Best for**", "Model fits on 1 GPU", "Model too large for 1 GPU"],
        ],
        title="FSDP vs DDP Trade-off",
    )

    # -- Section 6: Selection Guide --
    b.add_section("6. Selection Guide: 13B Model on 8x A100 80GB", [
        "### Memory estimation formula\n\n"
        "For a model with $$P$$ parameters, mixed-precision training with AdamW:",

        FormulaBlock(
            latex=r"\text{Memory per GPU} = \underbrace{2P}_{\text{FP16 params}} "
                  r"+ \underbrace{2P}_{\text{FP16 grads}} "
                  r"+ \underbrace{12P}_{\text{Adam states (FP32)}} "
                  r"+ \underbrace{a \cdot B \cdot s \cdot h}_{\text{activations}}",
            explanation="where $$a$$ = number of layers, $$B$$ = micro-batch size, "
                        "$$s$$ = sequence length, $$h$$ = hidden dimension:",
        ),

        "### Worked example: 13B parameters\n\n"
        "**Parameter memory (no sharding):**\n"
        "- $$P = 13 \\times 10^9$$\n"
        "- Full: $$16P = 16 \\times 13\\text{B} = 208\\text{ GB}$$ -- does NOT fit on a single A100 80GB\n\n"
        "**With FSDP (ZeRO Stage 3) on 8 GPUs:**\n"
        "- $$16P / 8 = 26\\text{ GB per GPU}$$ for params + optimizer\n"
        "- Leaves ~54 GB for activations + buffers -- comfortably fits",

        "### Decision tree\n\n"
        "```\n"
        "Can the model + optimizer fit on 1 GPU?\n"
        "  YES -> Use DDP (simplest)\n"
        "  NO  -> Does it fit with FSDP across available GPUs?\n"
        "    YES -> Use FSDP (ZeRO Stage 3)\n"
        "    NO  -> Add Pipeline Parallelism (split layers across nodes)\n"
        "           + Tensor Parallelism (within node) -> 3D Parallelism\n"
        "```",

        "### Activation memory estimation\n\n"
        "For a transformer layer:",

        FormulaBlock(
            latex=r"\text{Activation memory per layer} \approx "
                  r"2 \cdot B \cdot s \cdot h \cdot \left(10 + \frac{24s}{h}\right)",
            explanation="For 13B model ($$h = 5120$$, $$s = 2048$$, $$B = 1$$): "
                        "per layer ~200 MB, 40 layers ~8 GB:",
        ),

        "With **activation checkpointing** (recompute instead of store): reduces "
        "to $$\\sqrt{L}$$ layers stored, where $$L$$ = number of layers. For 40 layers: "
        "store ~6 layers, save ~85% activation memory.",
    ])

    # -- Section 7: 3D Parallelism --
    b.add_section("7. 3D Parallelism", [
        "Production systems (GPT-3, PaLM, Llama 3 405B) combine all three strategies.",

        "### Typical configuration",
    ])

    b.add_diagram_html(THREE_D_PARALLELISM_DIAGRAM)

    b.add_comparison_table(
        headers=["Strategy", "Bandwidth Needs", "Best Interconnect", "Assigned To"],
        rows=[
            ["**TP**", "Highest (AllReduce per layer)", "NVLink (600+ GB/s)", "Intra-node"],
            ["**PP**", "Medium (activation P2P)", "Inter-node network", "Across nodes"],
            ["**DP/FSDP**", "Lower (AllReduce per step)", "Inter-node network", "Remaining GPUs"],
        ],
        title="Why This Ordering?",
    )

    b.add_section("### Key principle", [
        "Place the most communication-intensive parallelism on the fastest interconnect.",
    ])

    b.add_comparison_table(
        headers=["Model", "Params", "GPUs", "TP", "PP", "DP"],
        rows=[
            ["GPT-3", "175B", "1024 A100", "8", "16", "8"],
            ["PaLM", "540B", "6144 TPU", "8", "12", "64"],
            ["Llama 3 405B", "405B", "16K H100", "8", "16", "128"],
            ["Llama 2 70B", "70B", "256 A100", "8", "4", "8"],
        ],
        title="Real-World 3D Parallelism Examples",
    )

    # -- Section 8: Common Misunderstandings --
    b.add_section("8. Common Misunderstandings (Error Corrections)", [
        "### Misunderstanding 1: 'FSDP is the same as model parallelism'\n\n"
        "**Correction:** FSDP is a memory-efficient variant of *data parallelism*. "
        "Each GPU still processes different data. The model parameters are sharded for "
        "memory savings but are AllGathered before each forward/backward computation. "
        "True model parallelism (TP/PP) splits the computation itself.",

        "### Misunderstanding 2: 'Tensor Parallelism works well across nodes'\n\n"
        "**Correction:** TP requires AllReduce of activations *twice per layer* "
        "(once for attention, once for MLP). This is extremely bandwidth-intensive. "
        "Across nodes with ~50 GB/s network (vs ~600 GB/s NVLink), TP becomes a "
        "severe bottleneck. TP is almost always intra-node only.",

        "### Misunderstanding 3: 'Pipeline parallelism is free -- just split layers'\n\n"
        "**Correction:** The pipeline bubble is a real efficiency loss. With 4 pipeline "
        "stages and 4 micro-batches, bubble fraction is $$3/7 \\approx 43\\%$$. You need "
        "$$M \\gg N$$ micro-batches to amortize the bubble, which increases memory pressure "
        "(more activations stored simultaneously).",

        "### Misunderstanding 4: 'ZeRO Stage 3 has the same communication cost as DDP'\n\n"
        "**Correction:** ZeRO Stage 3 requires ~$$3|\\theta|$$ communication per step vs "
        "DDP's ~$$2|\\theta|$$. The extra $$|\\theta|$$ comes from AllGather in the "
        "forward pass. This is a 50% communication overhead -- acceptable because it "
        "enables training models that don't fit in DDP.",

        "### Misunderstanding 5: 'You always want the maximum degree of parallelism'\n\n"
        "**Correction:** Higher parallelism degree means smaller per-GPU batch size "
        "and more communication overhead. There's an optimal trade-off. For example, "
        "TP=8 with 8-way attention heads is natural, but TP=16 would split heads "
        "sub-optimally and add cross-node communication. Over-parallelizing can "
        "*reduce* throughput.",
    ])

    # -- Self-Check --
    b.add_checklist("Self-Check Questions", [
        "**Q1:** For a 13B parameter model on 8x A100 80GB GPUs, calculate the "
        "memory per GPU with (a) DDP, (b) ZeRO Stage 1, (c) ZeRO Stage 3. "
        "Which stages fit?",
        "**Q2:** Draw the pipeline bubble for 4 stages and 8 micro-batches "
        "using 1F1B scheduling. Calculate the bubble fraction.",
        "**Q3:** Explain why Tensor Parallelism splits MLP column-wise first, "
        "then row-wise. What goes wrong if you do row-first then column?",
        "**Q4:** You have 128 H100 GPUs across 16 nodes (8 GPUs/node). Design "
        "the 3D parallelism layout for a 70B model. Justify each choice.",
        "**Q5:** Compare FSDP's communication volume ($$3|\\theta|$$) with DDP's "
        "($$2|\\theta|$$). When is the 50% overhead worth it? Cross-reference: "
        "how does the memory estimation relate to Day 5 (Inference Optimization)?",
    ])

    # -- Quick Reference --
    b.add_section("Quick Reference Card", [
        "```\n"
        "DP:    Full model on each GPU, AllReduce gradients. Memory: 16P per GPU.\n"
        "TP:    Split weight matrices intra-layer. 2 AllReduce per transformer layer.\n"
        "PP:    Split layers across GPUs. Bubble = (N-1)/(N+M-1). P2P comms only.\n"
        "FSDP:  Shard params+grads+optimizer. Memory: 16P/N per GPU. Comms: 3|theta|.\n"
        "ZeRO:  Stage1=shard optimizer, Stage2=+grads, Stage3=+params (=FSDP).\n"
        "3D:    TP(intra-node, NVLink) x PP(cross-node) x DP(remaining).\n"
        "Memory formula: 2P(params) + 2P(grads) + 12P(Adam) + activations.\n"
        "Activation ckpt: Recompute instead of store. Saves ~sqrt(L)/L memory.\n"
        "```",
    ])

    return b


def main() -> None:
    """Build and save the Distributed Training study note to mle_prep.db."""
    b = build_day3()

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
