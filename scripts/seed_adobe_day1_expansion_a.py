"""Seed script: Expand Adobe Prep Day1 with 3 new sections.

Expansion A adds:
  11. Positional Embedding deep-dive (absolute, sinusoidal derivation, relative, RoPE)
  12. KV-Cache mechanism (why cache K/V, memory formula, inference optimization)
  13. Why predict noise not x_0 (variance analysis, score matching, v-prediction)

Uses StudyNoteBuilder for section/formula construction, then patches the
existing document in mle_prep.db (id=18) by inserting before Self-Check.
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
DOC_ID = 18  # Adobe Prep Day1


def build_new_sections() -> str:
    """Build the 3 new sections using StudyNoteBuilder, return markdown."""
    b = StudyNoteBuilder()
    b.set_title("_expansion_tmp_")

    # Register terms used in the new sections
    b.add_term("RoPE", "Rotary Position Embedding",
               "Relative position encoding via rotation matrices")
    b.add_term("KV-Cache", "Key-Value Cache",
               "Caches K and V tensors from previous tokens to avoid recomputation")
    b.add_term("PE", "Position Embedding",
               "Injecting sequence position information into token representations")
    b.add_term("MHA", "Multi-Head Attention",
               "Parallel attention heads with different learned projections")

    # ---- Section 11: Positional Embedding Deep-Dive ----
    b.add_section("11. Positional Embedding 深度解析", [
        "Transformer 的 self-attention 是 **置换不变的** (permutation invariant): "
        "打乱输入顺序，输出也只是同样打乱。因此必须显式注入位置信息。",

        "### 11.1 Absolute Positional Embedding (Learned)\n\n"
        "最直接的方法: 为每个位置 $\\text{pos} \\in [0, L_{\\max})$ "
        "学习一个 $d$-维向量 $\\mathbf{p}_{\\text{pos}} \\in \\mathbb{R}^d$，"
        "加到 token embedding 上:\n\n"
        "$\\mathbf{h}_{\\text{pos}} = \\mathbf{x}_{\\text{pos}} + \\mathbf{p}_{\\text{pos}}$\n\n"
        "**优点**: 简单有效，GPT-2/BERT 使用。\n"
        "**缺点**: 最大长度固定为 $L_{\\max}$，无法泛化到更长序列; "
        "不直接编码相对距离。",

        "### 11.2 Sinusoidal Positional Embedding (Vaswani et al., 2017)\n\n"
        "原始 Transformer 提出的手工设计方案，无需学习参数。",

        FormulaBlock(
            latex=(r"\text{PE}(\text{pos}, 2i) = \sin\!\left("
                   r"\frac{\text{pos}}{10000^{2i/d}}\right), \quad "
                   r"\text{PE}(\text{pos}, 2i+1) = \cos\!\left("
                   r"\frac{\text{pos}}{10000^{2i/d}}\right)"),
            explanation="Sinusoidal PE 公式 -- 偶数维用 sin，奇数维用 cos:",
        ),

        "**频率直觉**: 第 $i$ 维的频率为 $\\omega_i = 1/10000^{2i/d}$。"
        "低维变化快 (像秒针)，高维变化慢 (像时针)。不同维度以不同周期编码位置，"
        "类似于数字的不同进制位。",

        "### 11.2.1 核心性质: 相对位置的线性变换\n\n"
        "**定理**: 存在只依赖偏移量 $k$ 的线性变换 $M_k$，使得:\n\n"
        "$\\text{PE}(\\text{pos}+k) = M_k \\cdot \\text{PE}(\\text{pos})$\n\n"
        "**证明** (以第 $i$ 组 sin/cos 对为例):",

        FormulaBlock(
            latex=(r"\begin{pmatrix} \sin(\omega_i(\text{pos}+k)) \\"
                   r" \cos(\omega_i(\text{pos}+k)) \end{pmatrix}"
                   r" = \begin{pmatrix} \cos(\omega_i k) & \sin(\omega_i k) \\"
                   r" -\sin(\omega_i k) & \cos(\omega_i k) \end{pmatrix}"
                   r" \begin{pmatrix} \sin(\omega_i \cdot \text{pos}) \\"
                   r" \cos(\omega_i \cdot \text{pos}) \end{pmatrix}"),
            explanation="三角函数加法公式展开后，可以写成旋转矩阵乘以原始 PE:",
        ),

        "这正是 **二维旋转矩阵** $R(\\omega_i k)$! 旋转角度只取决于偏移 $k$ "
        "和频率 $\\omega_i$，与绝对位置 pos 无关。\n\n"
        "**意义**: 点积 $\\text{PE}(\\text{pos})^\\top \\text{PE}(\\text{pos}+k)$ "
        "只依赖 $k$ 而非 pos，因此 attention score 能感知相对距离。\n\n"
        "**为什么用 sin/cos 配对?** 单独用 sin 无法区分正负偏移 ($\\sin$ 不是单射)。"
        "sin + cos 配对构成完整的旋转群，正负偏移对应正反旋转方向。",

        "### 11.3 Relative Positional Embedding (Shaw et al., 2018)\n\n"
        "不编码绝对位置，而是在 attention 计算中直接加入相对距离信息:\n\n"
        "$e_{ij} = \\frac{x_i W_Q (x_j W_K + a_{ij}^K)^\\top}{\\sqrt{d_k}}$\n\n"
        "其中 $a_{ij}^K$ 是可学习的相对位置向量，$i-j$ 相同则共享。"
        "通常裁剪到 $[-k, k]$ 范围。\n\n"
        "**优点**: 天然支持任意长度; attention score 直接编码相对距离。\n"
        "**缺点**: 实现复杂，需要修改 attention 计算; 增加少量参数。",

        "### 11.4 RoPE (Rotary Position Embedding, Su et al., 2021)\n\n"
        "RoPE 将 sinusoidal PE 的旋转思想直接应用到 attention 的 Q/K 向量上 "
        "(而非加到 embedding)。",

        FormulaBlock(
            latex=(r"f_q(\mathbf{x}_m, m) = R_{\Theta,m} W_Q \mathbf{x}_m, \quad "
                   r"f_k(\mathbf{x}_n, n) = R_{\Theta,n} W_K \mathbf{x}_n"),
            explanation="RoPE 对 Q 和 K 分别应用位置相关的旋转矩阵 $R_{\\Theta,m}$:",
        ),

        "其中 $R_{\\Theta,m}$ 是分块对角旋转矩阵，每个 2x2 块旋转角度为 "
        "$m \\cdot \\theta_i$，$\\theta_i = 10000^{-2i/d}$ (与 sinusoidal PE 相同的频率)。\n\n"
        "**关键性质**: $f_q(m)^\\top f_k(n) = (W_Q x_m)^\\top R_{\\Theta,n-m} (W_K x_n)$\n\n"
        "点积只依赖相对位置 $n - m$ (旋转矩阵正交性: $R_m^\\top R_n = R_{n-m}$)。",

        "### 11.5 位置编码方法对比",
    ])

    b.add_comparison_table(
        headers=["方法", "类型", "相对位置", "长度外推", "代表模型"],
        rows=[
            ["Learned Absolute", "加到 embedding", "间接 (通过 dot product)", "不支持", "GPT-2, BERT"],
            ["Sinusoidal", "加到 embedding", "线性变换性质", "理论上可以", "Transformer (original)"],
            ["Shaw Relative", "修改 attention score", "显式建模", "支持 (裁剪范围内)", "Transformer-XL"],
            ["RoPE", "旋转 Q/K 向量", "旋转矩阵差", "NTK-aware 扩展", "LLaMA, GPT-NeoX, Qwen"],
            ["ALiBi", "attention bias", "线性衰减", "天然支持", "BLOOM, MPT"],
        ],
        title="Positional Embedding 方法对比",
    )

    # ---- Section 12: KV-Cache Mechanism ----
    b.add_section("12. KV-Cache: 自回归推理加速的核心", [
        "自回归生成时，每个新 token 需要和所有之前的 token 做 attention。"
        "如果每次都重新计算所有 token 的 K 和 V，复杂度是 $O(n^2)$; "
        "KV-Cache 将其降为 $O(n)$ per token。",

        "### 12.1 为什么只缓存 K 和 V，不缓存 Q?\n\n"
        "在自回归生成中:\n"
        "- **Q (Query)**: 只需要当前 token 的 query 向量，用于和所有 K 做点积\n"
        "- **K (Key)**: 所有已生成 token 的 key 向量，每次新增一个\n"
        "- **V (Value)**: 所有已生成 token 的 value 向量，每次新增一个\n\n"
        "Attention 计算: $\\text{Attn}(q_t, K_{1:t}, V_{1:t}) = "
        "\\text{softmax}(q_t K_{1:t}^\\top / \\sqrt{d_k}) \\cdot V_{1:t}$\n\n"
        "**Q 不需要缓存**: 因为每步只用当前 token 的 $q_t$，用完即弃。\n"
        "**K/V 必须缓存**: 因为每步都需要所有之前 token 的 K 和 V，"
        "不缓存就要重新计算 (线性层前向传播)。",

        "### 12.2 KV-Cache 显存公式",

        FormulaBlock(
            latex=(r"\text{KV-Cache Memory} = 2 \times n_{\text{layers}} "
                   r"\times d_{\text{model}} \times \text{seq\_len} "
                   r"\times \text{dtype\_bytes}"),
            explanation="每层缓存 K 和 V 两个矩阵 (因子 2)，每个形状为 "
                        "[seq\\_len, d\\_model]:",
        ),

        "**实例计算** (LLaMA-2 7B):\n"
        "- $n_{\\text{layers}} = 32$, $d_{\\text{model}} = 4096$, "
        "dtype = float16 (2 bytes)\n"
        "- seq_len = 4096 时: $2 \\times 32 \\times 4096 \\times 4096 \\times 2 "
        "= 2$ GB\n"
        "- seq_len = 32K 时: 16 GB (cache 占比超过模型参数!)\n\n"
        "**面试重点**: KV-Cache 的显存消耗和 seq_len 成线性关系，"
        "这是长上下文推理的主要瓶颈。",

        "### 12.3 KV-Cache 优化技术",
    ])

    b.add_comparison_table(
        headers=["技术", "原理", "效果"],
        rows=[
            ["Multi-Query Attention (MQA)",
             "所有 head 共享一组 K/V",
             "Cache 缩小到 $1/n_{\\text{heads}}$"],
            ["Grouped-Query Attention (GQA)",
             "每组 head 共享一组 K/V (MQA 和 MHA 的折中)",
             "LLaMA-2 70B 使用，Cache 缩小到 $1/4$ -- $1/8$"],
            ["Paged Attention (vLLM)",
             "KV-Cache 分页管理，避免碎片",
             "显存利用率接近 100%，支持更大 batch"],
            ["Sliding Window (Mistral)",
             "只缓存最近 W 个 token 的 KV",
             "固定显存上限，适合长序列"],
            ["Quantized KV-Cache",
             "将 KV 从 FP16 量化到 INT8/INT4",
             "显存减半/四分之一，精度损失微小"],
        ],
        title="KV-Cache 优化方法",
    )

    b.add_section("12. KV-Cache (续): Prefill vs Decode 阶段", [
        "### 12.4 两阶段推理\n\n"
        "1. **Prefill 阶段**: 输入 prompt 的所有 token 并行计算，填充 KV-Cache。"
        "这一步是 compute-bound (大矩阵乘法)。\n"
        "2. **Decode 阶段**: 逐 token 生成，每步只计算一个新 token 的 Q 并查询 Cache。"
        "这一步是 memory-bound (读取大量 KV-Cache，但计算量小)。\n\n"
        "**面试角度**: Prefill 瓶颈在算力 (FLOPS)，Decode 瓶颈在显存带宽 (GB/s)。"
        "这解释了为什么 batch size 大时 decode throughput 提升有限 -- "
        "受限于从 HBM 读取 KV-Cache 的带宽。",
    ])

    # ---- Section 13: Why Predict Noise, Not x_0 ----
    b.add_section("13. 为什么预测噪声而不是预测 $x_0$: 深度分析", [
        "DDPM 的训练目标是预测加入的噪声 $\\epsilon$，而非直接预测干净图像 $x_0$。"
        "这个选择有深刻的数学原因。",

        "### 13.1 方差分析: $\\epsilon$-prediction 的优势\n\n"
        "三种等价的参数化方式:\n"
        "- **$\\epsilon$-prediction**: 网络预测添加的噪声 $\\epsilon_\\theta(x_t, t)$\n"
        "- **$x_0$-prediction**: 网络直接预测干净图像 $\\hat{x}_0(x_t, t)$\n"
        "- **$v$-prediction**: 网络预测 $v = \\sqrt{\\bar{\\alpha}_t}\\,\\epsilon "
        "- \\sqrt{1-\\bar{\\alpha}_t}\\,x_0$",

        "**关键差异在于目标的方差**:",

        FormulaBlock(
            latex=(r"\text{Var}[\epsilon] = \mathbf{I} \quad "
                   r"\text{(constant across all } t\text{)}"),
            explanation="$\\epsilon$-prediction 的目标方差恒定:",
        ),

        FormulaBlock(
            latex=(r"\text{Var}[x_0 \mid x_t] = "
                   r"\frac{1-\bar{\alpha}_t}{\bar{\alpha}_t} \mathbf{I} "
                   r"\quad \text{(varies with } t\text{, explodes as } "
                   r"\bar{\alpha}_t \to 0\text{)}"),
            explanation="$x_0$-prediction 的目标方差随 $t$ 变化，"
                        "在 $t$ 接近 $T$ 时趋向无穷:",
        ),

        "**直觉**: 当 $t$ 很大时 (图像几乎是纯噪声)，要从 $x_t$ 预测 $x_0$ "
        "相当于从噪声中凭空重建原图 -- 目标方差极大，梯度不稳定。"
        "而预测噪声 $\\epsilon$ 的目标始终是单位方差的标准高斯噪声，"
        "loss landscape 更平滑。",

        "### 13.2 与 Score Matching 的等价性\n\n"
        "Score function 定义为对数概率的梯度:",

        FormulaBlock(
            latex=(r"\nabla_{x_t} \log p_t(x_t) = "
                   r"-\frac{\epsilon}{\sqrt{1-\bar{\alpha}_t}} "
                   r"\approx -\frac{\epsilon_\theta(x_t, t)}"
                   r"{\sqrt{1-\bar{\alpha}_t}}"),
            explanation="预测噪声等价于估计 score function，仅差一个缩放系数:",
        ),

        "这意味着 DDPM 的 $\\epsilon$-prediction 训练等价于 **denoising score matching** "
        "(Vincent 2011)。Score function 指向数据密度增加最快的方向 -- "
        "从噪声走向数据。预测 $\\epsilon$ 就是在估计这个方向。\n\n"
        "**统一视角**: DDPM ($\\epsilon$-prediction) = Score Matching (估计 score) = "
        "SDE 反向过程 (Langevin dynamics)，三者殊途同归。",

        "### 13.3 $v$-prediction: 折中方案 (Salimans & Ho, 2022)\n\n"
        "$v$-prediction 定义目标为:",

        FormulaBlock(
            latex=(r"v_t = \sqrt{\bar{\alpha}_t}\,\epsilon "
                   r"- \sqrt{1-\bar{\alpha}_t}\,x_0"),
            explanation="$v$ 是噪声和信号的加权组合，权重随 $t$ 平滑变化:",
        ),

        "**优势**:\n"
        "- 在 $t \\approx 0$ (几乎无噪声) 时，$v \\approx -x_0$，网络预测信号\n"
        "- 在 $t \\approx T$ (纯噪声) 时，$v \\approx \\epsilon$，网络预测噪声\n"
        "- 方差在所有 $t$ 上近似均匀，训练更稳定\n"
        "- Stable Diffusion v2 和 SDXL 的部分训练使用 $v$-prediction\n\n"
        "### 13.4 三种参数化的转换关系\n\n"
        "给定 $x_t$, $t$, 和网络输出，三种参数化可以互相转换:\n\n"
        "- 从 $\\hat{\\epsilon}$ 恢复: "
        "$\\hat{x}_0 = (x_t - \\sqrt{1-\\bar{\\alpha}_t}\\,\\hat{\\epsilon}) "
        "/ \\sqrt{\\bar{\\alpha}_t}$\n"
        "- 从 $\\hat{x}_0$ 恢复: "
        "$\\hat{\\epsilon} = (x_t - \\sqrt{\\bar{\\alpha}_t}\\,\\hat{x}_0) "
        "/ \\sqrt{1-\\bar{\\alpha}_t}$\n"
        "- 从 $\\hat{v}$ 恢复: "
        "$\\hat{x}_0 = \\sqrt{\\bar{\\alpha}_t}\\,x_t "
        "- \\sqrt{1-\\bar{\\alpha}_t}\\,\\hat{v}$",
    ])

    b.add_comparison_table(
        headers=["参数化", "目标方差", "训练稳定性", "SNR 加权", "代表模型"],
        rows=[
            ["$\\epsilon$-prediction",
             "恒定 ($\\mathbf{I}$)",
             "高 (均匀 loss)",
             "高 SNR 时段权重过大",
             "DDPM, SD v1.x"],
            ["$x_0$-prediction",
             "随 $t$ 增大而爆炸",
             "低 ($t$ 大时不稳定)",
             "低 SNR 时段权重过大",
             "DALL-E (部分)"],
            ["$v$-prediction",
             "近似均匀",
             "最高",
             "近似均匀加权",
             "SD v2, SDXL, Imagen Video"],
        ],
        title="三种参数化方式对比",
    )

    # Build and extract just the section content (skip header/prereqs/terms)
    content = b.build()

    # Extract from section 11 onward (skip title, prerequisites, key terms)
    lines = content.split("\n")
    section_start = None
    for i, line in enumerate(lines):
        if line.startswith("## 11."):
            section_start = i
            break

    if section_start is None:
        print("[FAIL] Could not find section 11 in built content")
        sys.exit(1)

    return "\n".join(lines[section_start:]).rstrip()


def main() -> None:
    """Insert 3 new sections into existing Day1 document."""
    new_sections = build_new_sections()

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?", (DOC_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] Document id={DOC_ID} not found")
            sys.exit(1)

        existing = row[0]

        # Insert new sections before "### Self-Check Questions"
        marker = "### Self-Check Questions"
        idx = existing.find(marker)
        if idx == -1:
            # Fallback: append before "## 面试快速参考"
            marker = "## 面试快速参考"
            idx = existing.find(marker)
        if idx == -1:
            # Last resort: append at end
            updated = existing.rstrip() + "\n\n" + new_sections + "\n"
        else:
            updated = (
                existing[:idx].rstrip()
                + "\n\n"
                + new_sections
                + "\n\n"
                + existing[idx:]
            )

        # Validate no orphan dollar signs
        warnings = StudyNoteBuilder.validate(updated)
        if warnings:
            for w in warnings:
                print(f"[WARN] {w}")

        # Update in DB
        conn.execute(
            "UPDATE company_documents SET content = ? WHERE id = ?",
            (updated, DOC_ID),
        )
        conn.commit()

        new_len = len(updated)
        old_len = len(existing)
        print(
            f"[DONE] Updated document id={DOC_ID}: "
            f"{old_len} -> {new_len} chars (+{new_len - old_len})"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
