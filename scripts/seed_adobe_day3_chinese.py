"""Rewrite Adobe Day 3 (Distributed Training) in Chinese.

Incorporates user's comprehensive supplement covering:
- 13B memory estimation (16P formula)
- HBM vs SRAM GPU memory model
- 4-strategy panorama table (DP/TP/PP/FSDP)
- DP detail (AllReduce = ReduceScatter+AllGather, gradient bucketing)
- TP detail (column-row split, why column-first, attention head split, NVLink)
- PP detail (bubble formula, micro-batch, GPipe/1F1B/Interleaved)
- FSDP/ZeRO Stages 1-3 (forward/backward workflow)
- 3D parallelism (TP*PP*DP with real configs: GPT-3/PaLM/Llama)
- Activation checkpointing (sqrt(L) strategy)
- Communication primitives, 5 misconceptions, decision tree, memory cards
- 5 Q&As with answers
"""
import importlib.util
import sqlite3
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

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DOC_ID = 13  # Adobe Prep Day3
COMPANY_ID = 23


def build_day3_chinese() -> StudyNoteBuilder:
    b = StudyNoteBuilder()
    b.set_title("Distributed Training: DP / TP / PP / FSDP (Adobe Prep Day 3)")

    b.add_prerequisites([
        "Neural network training (forward/backward, gradient descent)",
        "Basic linear algebra (matrix multiplication, transpose)",
        "GPU memory model (HBM, SRAM)",
    ])

    # Register terms
    b.add_term("DP", "Data Parallelism",
               "each GPU holds full model, splits data batch")
    b.add_term("TP", "Tensor Parallelism",
               "splits weight matrices within a single layer across GPUs")
    b.add_term("PP", "Pipeline Parallelism",
               "splits model layers across GPUs, data flows like a pipeline")
    b.add_term("FSDP", "Fully Sharded Data Parallel",
               "ZeRO Stage 3 -- shards params+grads+optimizer across GPUs")
    b.add_term("ZeRO", "Zero Redundancy Optimizer",
               "3-stage memory optimization eliminating redundant storage")
    b.add_term("AllReduce", "AllReduce",
               "collective op: sum tensors across GPUs, all get result")
    b.add_term("AllGather", "AllGather",
               "collective op: concatenate shards, all GPUs get full tensor")
    b.add_term("ReduceScatter", "ReduceScatter",
               "collective op: sum then split, each GPU gets 1/N of result")
    b.add_term("NVLink", "NVLink",
               "high-bandwidth intra-node GPU interconnect (600+ GB/s)")
    b.add_term("DDP", "Distributed Data Parallel",
               "PyTorch's standard DP implementation with gradient bucketing")
    b.add_term("3D Parallelism", "3D Parallelism",
               "TP x PP x DP combined strategy for training very large models")
    b.add_term("Activation Checkpointing", "Activation Checkpointing",
               "trade compute for memory by recomputing activations during backward")

    # ===== Section 1: Why Distributed Training? =====
    b.add_section("1. Why Distributed Training?", [
        "### Core Problem: Model Too Large for Single GPU",
        "",
        "13B model + FP16 + AdamW:",
        "",
        "| Item | Precision | Bytes/Param | Total (13B) |\n"
        "| --- | --- | --- | --- |\n"
        "| Params | FP16 | 2 bytes | 26 GB |\n"
        "| Gradients | FP16 | 2 bytes | 26 GB |\n"
        "| FP32 param copy | FP32 | 4 bytes | 52 GB |\n"
        "| Momentum (1st moment) | FP32 | 4 bytes | 52 GB |\n"
        "| Variance (2nd moment) | FP32 | 4 bytes | 52 GB |\n"
        "| **Total** | | **16 bytes** | **208 GB** |",
        "",
        "**A100 = 80 GB, gap = 2.6x. Cannot fit on a single GPU.**",
        "",
        "### Memory Formula (Must Memorize)",
        "",
        FormulaBlock(
            latex=r"\text{Total Memory} = \underbrace{16P}_{\text{params+grads+optimizer}} + \underbrace{a \cdot B \cdot s \cdot h}_{\text{activations}}",
            explanation="",
        ),
        "- $P$ = number of parameters, $a$ = number of layers, $B$ = micro-batch size, $s$ = sequence length, $h$ = hidden dim",
        "- Optimizer states take 12P (75% of total) -- the largest component",
    ])

    # ===== Section 2: GPU Memory Model =====
    b.add_section("2. GPU Memory: HBM vs SRAM", [
        "| | HBM (\"big warehouse\") | SRAM (\"workbench\") |\n"
        "| --- | --- | --- |\n"
        "| Capacity | Large (A100: 80 GB) | Tiny (A100: ~20 MB) |\n"
        "| Speed | Fast (~2 TB/s) | Very fast (~19 TB/s) |\n"
        "| Stores | Params, grads, optimizer states, activations | Current compute tile |",
        "",
        "**Key insight**: All parallelism strategies aim to fit data into limited HBM.",
    ])

    # ===== Section 3: Four-Strategy Panorama =====
    b.add_section("3. Four Parallelism Strategies Overview", [
        "| Strategy | What is split | Comm type | Comm volume | Best interconnect |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| **DP** | Data (mini-batch) | AllReduce gradients | $2|\\theta|$/step | Cross-node OK |\n"
        "| **TP** | Weight matrices (intra-layer) | AllReduce activations | 2x per layer | NVLink (intra-node) |\n"
        "| **PP** | Layers (inter-layer) | Point-to-point activations | Lowest | Best for cross-node |\n"
        "| **FSDP/ZeRO** | Params+grads+optimizer | AllGather + ReduceScatter | $3|\\theta|$/step | Cross-node OK |",
    ])

    # ===== Section 4: Data Parallelism (DP) =====
    b.add_section("4. Data Parallelism (DP)", [
        "### Workflow",
        "",
        "1. **Replicate model** to N GPUs (each holds full copy)",
        "2. **Split data**: global batch $B$ -> each GPU gets $B/N$",
        "3. **Compute independently**: forward + backward, each gets gradient $g_i$",
        "4. **AllReduce**: average gradients",
        "",
        FormulaBlock(
            latex=r"\bar{g} = \frac{1}{N}\sum_{i=1}^{N} g_i",
            explanation="",
        ),
        "5. **Update independently**: each uses same averaged gradient, stays in sync",
        "",
        "### AllReduce = ReduceScatter + AllGather",
        "",
        "Ring-based implementation:",
        "",
        "- ReduceScatter: each GPU splits into N chunks -> ring comm -> each GPU holds 1/N of sum",
        "- AllGather: each GPU broadcasts its 1/N -> all GPUs get complete gradient",
        "",
        FormulaBlock(
            latex=r"\text{Comm volume} = 2 \cdot \frac{N-1}{N} \cdot |\theta| \approx 2|\theta|",
            explanation="",
        ),
        "### PyTorch DDP: Gradient Bucketing",
        "",
        "**Gradient Bucketing**: backward pass and AllReduce **overlap** -- later layers start communicating while earlier layers are still computing gradients.",
        "",
        "### DP Limitations",
        "",
        "- Each GPU stores full $16P$ -> single GPU must fit entire model",
        "- N GPUs store N copies of the same data -> massive memory waste",
        "- **Cannot scale to models that don't fit on a single GPU**",
    ])

    # ===== Section 5: Tensor Parallelism (TP) =====
    b.add_section("5. Tensor Parallelism (TP)", [
        "### Core Idea",
        "",
        "Split a single layer's weight matrix -- each GPU stores and computes a portion.",
        "",
        "### MLP Column-Row Split",
        "",
        "For $Y = \\text{GeLU}(XA) \\cdot B$:",
        "",
        "**Layer 1 -- Column Parallel**:",
        "- $A = [A_1 | A_2 | \\dots | A_N]$",
        "- Each GPU computes $Y_i = \\text{GeLU}(X \\cdot A_i)$",
        "- GeLU is element-wise -> **no communication needed**",
        "",
        "**Layer 2 -- Row Parallel**:",
        "- $B = [B_1; B_2; \\dots; B_N]^T$",
        "- Each GPU computes partial sum $Z_i = Y_i \\cdot B_i$",
        "- **AllReduce** to get sum: $Z = \\sum Z_i$",
        "",
        "**Entire MLP block needs only 1 AllReduce.**",
        "",
        "### Why Must It Be Column-First?",
        "",
        "If reversed (row-first then column):",
        "- Row split output is partial sum, must AllReduce BEFORE GeLU",
        "- $\\text{GeLU}(a+b) \\neq \\text{GeLU}(a) + \\text{GeLU}(b)$ (nonlinearity is not decomposable!)",
        "- Results in 2 AllReduce per MLP block, doubling communication",
        "",
        "### Attention Head Split",
        "",
        "- $h$ attention heads naturally split to N GPUs ($h/N$ heads/GPU)",
        "- Each independently computes Q, K, V and attention",
        "- Output projection uses row parallel -> 1 AllReduce",
        "",
        "### Communication Per Transformer Layer",
        "",
        FormulaBlock(
            latex=r"\text{TP comm/layer} = 2 \times \text{AllReduce}(d_{\text{model}}) \quad \text{(MLP 1x + Attention 1x)}",
            explanation="",
        ),
        "### TP Hard Constraint: Intra-Node Only",
        "",
        "| Interconnect | Bandwidth |\n"
        "| --- | --- |\n"
        "| NVLink (intra-node) | 600+ GB/s |\n"
        "| Cross-node network | ~50 GB/s |",
        "",
        "40 layers x 2x/layer = 80 AllReduce per step. Cross-node would be 10-12x slower, GPUs mostly waiting.",
        "",
        "**TP degree is usually 2, 4, or 8 (matching intra-node GPU count).**",
    ])

    # ===== Section 6: Pipeline Parallelism (PP) =====
    b.add_section("6. Pipeline Parallelism (PP)", [
        "### Core Idea",
        "",
        "Split model by layers. Different GPUs handle different layers, data flows through like a pipeline.",
        "",
        "### Naive Pipeline Bubble",
        "",
        FormulaBlock(
            latex=r"\text{Bubble}_{\text{naive}} = \frac{N-1}{N}",
            explanation="",
        ),
        "4 stages -> 75% idle!",
        "",
        "### Micro-Batch Pipelining",
        "",
        "Split mini-batch into $M$ micro-batches that flow through sequentially:",
        "",
        FormulaBlock(
            latex=r"\text{Bubble}_{\text{micro}} = \frac{N-1}{N+M-1}",
            explanation="",
        ),
        "| N (stages) | M (micro-batches) | Bubble |\n"
        "| --- | --- | --- |\n"
        "| 4 | 4 | 43% |\n"
        "| 4 | 8 | 27% |\n"
        "| 4 | 16 | 16% |\n"
        "| 4 | 28+ | <10% |",
        "",
        "**In practice: $M = 4N$, accepting ~20% bubble.**",
        "",
        "### Three PP Variants",
        "",
        "| Method | Characteristics |\n"
        "| --- | --- |\n"
        "| **GPipe** | All forward first, then all backward; peak memory high |\n"
        "| **PipeDream 1F1B** | After warmup, alternate 1-forward-1-backward; peak memory low; **most common** |\n"
        "| **Interleaved PP** | Non-contiguous layer assignment (virtual stages); smaller bubble |",
        "",
        "### PP Communication Characteristics",
        "",
        "- Only **point-to-point** activation transfer between adjacent stages",
        "- Lowest communication volume and bandwidth requirement",
        "- **Best suited for cross-node communication**",
    ])

    # ===== Section 7: FSDP / ZeRO =====
    b.add_section("7. FSDP / ZeRO", [
        "### Core Idea",
        "",
        "Progressively shard the redundant params, gradients, and optimizer states in DP across all GPUs.",
        "",
        "### ZeRO Three Stages",
        "",
        "| Stage | What is sharded | Per-GPU memory | Savings vs 16P (N=64) |\n"
        "| --- | --- | --- | --- |\n"
        "| Baseline (DDP) | Nothing | $16P$ | 1x |\n"
        "| **Stage 1** | Optimizer states | $4P + 12P/N$ | ~4x |\n"
        "| **Stage 2** | + Gradients | $2P + 14P/N$ | ~8x |\n"
        "| **Stage 3 (FSDP)** | + Parameters | $16P/N$ | Nx |",
        "",
        "### Stage 3 Workflow (\"Save normally, borrow on demand\")",
        "",
        "**Forward pass** (per layer):",
        "1. AllGather: collect complete parameters",
        "2. Forward compute",
        "3. Discard non-owned parameters",
        "",
        "**Backward pass** (per layer):",
        "1. AllGather: collect complete parameters again",
        "2. Compute gradients",
        "3. ReduceScatter: shard gradients across GPUs",
        "4. Discard non-owned parameters",
        "",
        "### FSDP vs DDP Communication",
        "",
        "| | DDP | FSDP (Stage 3) |\n"
        "| --- | --- | --- |\n"
        "| Comm volume | $2|\\theta|$ | $3|\\theta|$ (50% more) |\n"
        "| Extra source | -- | Forward AllGather ($+|\\theta|$) |\n"
        "| Per-GPU memory | $16P$ | $16P/N$ |",
        "",
        "### Decision",
        "",
        "> $16P \\leq$ single GPU memory -> **DDP** (simple and efficient)",
        ">",
        "> $16P >$ single GPU memory -> **FSDP** (50% extra comm buys \"can train vs cannot train\")",
    ])

    # ===== Section 8: 3D Parallelism =====
    b.add_section("8. 3D Parallelism", [
        "### Core Principle",
        "",
        "**Highest communication intensity -> fastest interconnect**",
        "",
        "| Strategy | Comm intensity | Assigned to | Bandwidth |\n"
        "| --- | --- | --- | --- |\n"
        "| **TP** | Highest (2x AllReduce/layer) | Intra-node | NVLink 600+ GB/s |\n"
        "| **PP** | Medium (point-to-point) | Cross-node | InfiniBand ~50 GB/s |\n"
        "| **DP/FSDP** | Lower (1x/step, can overlap) | Remaining GPUs | InfiniBand ~50 GB/s |",
        "",
        FormulaBlock(
            latex=r"\text{Total GPUs} = TP \times PP \times DP",
            explanation="",
        ),
        "### Configuration Decision Flow",
        "",
        "```\n1. TP = intra-node GPU count (usually = 8)\n"
        "2. PP = enough to fit each stage into node memory (not too large, avoid bubbles)\n"
        "3. DP = Total GPUs / (TP x PP)\n```",
        "",
        "### Example: 64 GPUs = 8 nodes x 8 GPUs",
        "",
        "Config: TP=8 x PP=4 x DP=2",
        "",
        "```\n              DP replica 0          DP replica 1\n"
        "PP Stage 0:  Node 0 (TP=8)        Node 1 (TP=8)\n"
        "PP Stage 1:  Node 2 (TP=8)        Node 3 (TP=8)\n"
        "PP Stage 2:  Node 4 (TP=8)        Node 5 (TP=8)\n"
        "PP Stage 3:  Node 6 (TP=8)        Node 7 (TP=8)\n```",
        "",
        "### Real-World Configurations",
        "",
        "| Model | Params | GPUs | TP | PP | DP |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| GPT-3 | 175B | 1024 A100 | 8 | 16 | 8 |\n"
        "| PaLM | 540B | 6144 TPU | 8 | 12 | 64 |\n"
        "| Llama 3 405B | 405B | 16K H100 | 8 | 16 | 128 |\n"
        "| Llama 2 70B | 70B | 256 A100 | 8 | 4 | 8 |",
        "",
        "**Pattern**: TP is almost always 8; larger models need larger PP; throughput scales mainly by increasing DP.",
    ])

    # ===== Section 9: Activation Checkpointing =====
    b.add_section("9. Activation Checkpointing", [
        "### Problem",
        "",
        "Forward activations must be retained for backward pass. For 13B model ($h=5120, s=2048, B=1$, 40 layers):",
        "",
        FormulaBlock(
            latex=r"\text{Per-layer activation} \approx 2 \cdot B \cdot s \cdot h \cdot \left(10 + \frac{24s}{h}\right) \approx 200 \text{ MB}",
            explanation="",
        ),
        "40 layers = **8 GB**",
        "",
        "### Solution",
        "",
        "**Don't store activations -- recompute during backward pass.** Trade compute for memory.",
        "",
        "- Only store activations at $\\sqrt{L}$ checkpoint layers ($L$ = total layers)",
        "- During backward, recompute from nearest checkpoint",
        "- 40 layers -> store ~6 layers -> save ~85% activation memory",
        "",
        "**Cost**: ~33% more compute (one extra partial forward pass).",
    ])

    # ===== Section 10: Communication Primitives =====
    b.add_section("10. Communication Primitives Quick Reference", [
        "| Primitive | Function | Use case |\n"
        "| --- | --- | --- |\n"
        "| **AllReduce** | Sum tensors across all GPUs -> every GPU gets result | DP gradient sync, TP activation merge |\n"
        "| **AllGather** | Concatenate shards -> every GPU gets full tensor | FSDP forward: collect params |\n"
        "| **ReduceScatter** | Sum then split -> each GPU gets 1/N of result | FSDP backward: distribute grads |\n"
        "| **P2P (Send/Recv)** | Point-to-point transfer | PP adjacent stage activation transfer |",
        "",
        "**AllReduce = ReduceScatter + AllGather**",
    ])

    # ===== Section 11: Common Misconceptions =====
    b.add_section("11. Common Misconceptions", [
        "| Misconception | Correction |\n"
        "| --- | --- |\n"
        "| FSDP is model parallelism | FSDP is a **data parallelism** variant -- each GPU still processes different data |\n"
        "| TP can work across nodes | 2 AllReduce per layer, 10x+ slower cross-node, practically never used |\n"
        "| PP has no cost | Bubble is real: 4 stages + 4 micro-batches = 43% idle |\n"
        "| ZeRO-3 comm = DDP | FSDP is $3|\\theta|$, DDP is $2|\\theta|$, 50% more |\n"
        "| More parallelism is always better | Over-parallelization -> comm overhead + per-GPU batch too small -> throughput drops |",
    ])

    # ===== Section 12: Decision Tree =====
    b.add_section("12. Decision Tree", [
        "```\nCan model + optimizer fit on single GPU? (16P <= GPU memory?)\n"
        "+-- YES -> DDP (simplest)\n"
        "+-- NO -> Can FSDP sharding fit? (16P/N + activations <= GPU memory?)\n"
        "     +-- YES -> FSDP\n"
        "     +-- NO -> 3D Parallelism\n"
        "              +-- TP = 8 (intra-node NVLink)\n"
        "              +-- PP = fit each stage into node\n"
        "              +-- DP = Total GPUs / (TP x PP)\n```",
    ])

    # ===== Section 13: Quick Memory Cards =====
    b.add_section("13. Quick Memory Cards", [
        "```\nDP:    Full model x N copies, AllReduce gradients. Memory 16P/GPU.\n"
        "TP:    Split weight matrices, column->row. 2x AllReduce/layer. NVLink only.\n"
        "PP:    Split layers, pipeline. Bubble = (N-1)/(N+M-1). P2P comm.\n"
        "FSDP:  Shard params+grads+optimizer. Memory 16P/N. Comm 3|theta|.\n"
        "ZeRO:  S1=shard optimizer, S2=+grads, S3=+params (=FSDP).\n"
        "3D:    TP(intra-node) x PP(cross-node) x DP(remaining).\n"
        "16P:   2P(params) + 2P(grads) + 4P(FP32 copy) + 4P(momentum) + 4P(variance).\n"
        "ActCkpt: Recompute instead of store, save ~85% activation mem, +33% compute.\n```",
    ])

    # ===== Section 14: Self-Check Questions + Answers =====
    b.add_section("14. Self-Check Questions + Answers", [
        "### Q1: Memory Estimation",
        "",
        "- [ ] **Q1:** 13B model, 8x A100 80GB. Compute per-GPU memory for DDP / ZeRO-S1 / ZeRO-S3.",
        "",
        "> - DDP: $16 \\times 13 = 208$ GB -> cannot fit"
        " - S1: $4 \\times 13 + 12 \\times 13 / 8 = 52 + 19.5 = 71.5$ GB -> barely fits"
        " - S3: $16 \\times 13 / 8 = 26$ GB -> plenty of room (54 GB remaining)",
        "",
        "### Q2: Bubble Calculation",
        "",
        "- [ ] **Q2:** 4 stages, 16 micro-batches. Calculate bubble. How many micro-batches for <10%?",
        "",
        "> $\\frac{3}{19} \\approx 15.8\\%$. For $\\frac{3}{M+3} < 0.1$, solve $M > 27$, so at least **28**.",
        "",
        "### Q3: TP Column-Row Split",
        "",
        "- [ ] **Q3:** Why column-first? What happens if reversed?",
        "",
        "> Row-first -> output is partial sum -> must AllReduce before GeLU -> extra communication."
        " Because $\\text{GeLU}(a+b) \\neq \\text{GeLU}(a) + \\text{GeLU}(b)$.",
        "",
        "### Q4: 3D Parallelism Design",
        "",
        "- [ ] **Q4:** 128 H100, 16 nodes x 8 GPUs, 70B model. Design the parallelism config.",
        "",
        "> TP=8 (NVLink) x PP=4 (each stage ~17.5B, fits) x DP=4 (128/32).",
        "",
        "### Q5: FSDP vs DDP",
        "",
        "- [ ] **Q5:** When is the 50% extra communication worth it?",
        "",
        "> When $16P >$ single GPU memory (\"can train vs cannot train\");"
        " when $16P \\leq$ single GPU memory, not worth it -- DDP is simpler and faster.",
    ])

    return b


def main() -> None:
    builder = build_day3_chinese()
    content = builder.build()
    print(f"Generated content: {len(content)} chars")

    # Validate
    warnings = builder.validate(content)
    if warnings:
        print(f"WARNINGS: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("Validation: PASS (0 warnings)")

    # Save to DB -- update existing doc id=13
    db_path = str(DB_PATH)
    conn = sqlite3.connect(db_path, timeout=10)
    cur = conn.cursor()

    # Get old length for comparison
    cur.execute("SELECT LENGTH(content) FROM company_documents WHERE id=?", (DOC_ID,))
    old_len = cur.fetchone()[0]

    # Update content and title
    new_title = "Adobe Prep Day3: Distributed Training (DP/TP/PP/FSDP)"
    cur.execute(
        "UPDATE company_documents SET content=?, title=? WHERE id=?",
        (content, new_title, DOC_ID),
    )
    conn.commit()

    # Verify
    cur.execute("SELECT LENGTH(content) FROM company_documents WHERE id=?", (DOC_ID,))
    new_len = cur.fetchone()[0]
    print(f"Updated doc id={DOC_ID}: {old_len} -> {new_len} chars ({new_len - old_len:+d})")

    # Verify tables render (no blank lines between table rows)
    lines = content.split("\n")
    table_issues = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and i + 1 < len(lines):
            next_line = lines[i + 1]
            if next_line.strip() == "" and i + 2 < len(lines) and lines[i + 2].strip().startswith("|"):
                table_issues += 1
    print(f"Table rendering check: {table_issues} blank-line issues")

    # Count formulas
    formula_count = content.count("$$")
    print(f"Formula blocks: {formula_count // 2} (double-dollar pairs)")

    # Count checklist items
    checklist_count = content.count("- [ ]")
    print(f"Checklist items: {checklist_count}")

    # Count blockquote answers
    answer_count = len([l for l in lines if l.strip().startswith(">")])
    print(f"Blockquote answers: {answer_count}")

    conn.close()


if __name__ == "__main__":
    main()
