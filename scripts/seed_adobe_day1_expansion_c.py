"""Seed script: Answer all checklist questions in Adobe Prep Day1.

Expansion C:
  - Answers all 10 existing Self-Check questions with blockquote responses
  - Adds 6 new checklist items for expanded content (sections 11-16)
  - New items also have blockquote answers
  - All answers written in Chinese

Format: keeps the - [ ] checkbox, adds > **Answer**: blockquote below each.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DOC_ID = 18  # Adobe Prep Day1


# Each answer is a comprehensive 3-5 sentence interview-ready response in Chinese,
# referencing specific formulas and concepts from the note.
ANSWERS: dict[str, str] = {
    # --- 10 existing questions ---

    "画出 Stable Diffusion 的完整推理 pipeline (Text -> CLIP -> UNet -> VAE -> Image)": (
        "Stable Diffusion 推理 pipeline 分为 4 个阶段: "
        "(1) 文本编码: 用户 prompt 经过 CLIP text encoder 得到 77x768 的 token embedding 序列; "
        "(2) 噪声初始化: 在 64x64x4 的 latent space 中采样随机高斯噪声 $z_T \\sim \\mathcal{N}(0, \\mathbf{I})$; "
        "(3) 迭代去噪: UNet 以 $z_t$、时间步 $t$、文本 embedding 为输入，预测噪声 $\\epsilon_\\theta$，"
        "通过 DDPM/DDIM 采样公式逐步去噪 (通常 20-50 步)，每步做两次前向传播 (CFG: 有条件 + 无条件); "
        "(4) VAE 解码: 最终 latent $z_0$ 经 VAE decoder 上采样 8 倍得到 512x512x3 的 RGB 图像。"
        "关键数字: latent 压缩比 48x (512x512x3 -> 64x64x4)，CFG 典型 $w=7.5$。"
    ),

    "写出 CFG 公式并解释 guidance scale w 的影响": (
        "CFG 推理公式: $\\hat{\\epsilon} = \\epsilon_\\theta(x_t, \\varnothing) "
        "+ w \\cdot (\\epsilon_\\theta(x_t, c) - \\epsilon_\\theta(x_t, \\varnothing))$，"
        "其中 $\\epsilon_\\theta(x_t, c)$ 是有条件预测，$\\epsilon_\\theta(x_t, \\varnothing)$ 是无条件预测，"
        "$w$ 是 guidance scale。当 $w=1$ 时退化为标准条件生成; "
        "$w>1$ 时放大条件方向 (生成更符合 prompt 但多样性下降); $w$ 过大会产生过饱和伪影。"
        "训练时以 10% 概率随机丢弃条件 (用空 prompt 替代)，让模型同时学会有条件和无条件生成。"
        "典型值: SD v1.x 使用 $w=7.5$，SDXL 使用 $w=5.0$-$7.0$。"
    ),

    "解释为什么在 latent space 做 diffusion 而不是 pixel space": (
        "在 pixel space 直接做 diffusion 计算量巨大: 512x512x3 = 786,432 维空间上做 UNet 前向传播。"
        "Latent Diffusion 用预训练 VAE 将图像压缩到 64x64x4 = 16,384 维 (压缩比 48 倍)，"
        "在此低维空间做扩散过程。优势有三: (1) 计算量减少约 48 倍，使消费级 GPU 可用; "
        "(2) VAE 的潜在空间已去除感知冗余 (perceptual redundancy)，只保留语义信息，"
        "扩散模型可以专注于学习语义分布; (3) VAE 只需训练一次，扩散模型和条件模块可以独立迭代。"
        "缺点是 VAE 解码会引入少量重建损失 (面部细节模糊)，但总体收益远大于代价。"
    ),

    "写出训练目标 (MSE loss) 并解释为什么预测噪声而不是直接预测 x_0": (
        "简化 MSE 训练目标: $\\mathcal{L} = \\mathbb{E}_{t, x_0, \\epsilon}"
        "\\big[\\|\\epsilon - \\epsilon_\\theta(x_t, t)\\|^2\\big]$，"
        "其中 $x_t = \\sqrt{\\bar{\\alpha}_t}\\,x_0 + \\sqrt{1-\\bar{\\alpha}_t}\\,\\epsilon$。"
        "预测噪声 ($\\epsilon$-prediction) 优于预测 $x_0$ 的核心原因是**目标方差恒定**: "
        "$\\text{Var}[\\epsilon] = \\mathbf{I}$ 在所有 $t$ 上不变; "
        "而 $\\text{Var}[x_0|x_t] = \\frac{1-\\bar{\\alpha}_t}{\\bar{\\alpha}_t}\\mathbf{I}$，"
        "在 $t$ 接近 $T$ 时趋向无穷，导致梯度不稳定。"
        "此外，$\\epsilon$-prediction 等价于 denoising score matching: "
        "$\\nabla_{x_t}\\log p_t(x_t) \\approx -\\epsilon_\\theta/\\sqrt{1-\\bar{\\alpha}_t}$，"
        "统一了 DDPM、Score matching 和 SDE 框架。"
    ),

    "解释方差守恒: 为什么采样公式的系数带根号？标准差 vs 方差的区别": (
        "前向过程公式 $x_t = \\sqrt{\\bar{\\alpha}_t}\\,x_0 + \\sqrt{1-\\bar{\\alpha}_t}\\,\\epsilon$ "
        "中系数带根号是因为在**标准差层面**操作，不是方差层面。"
        "方差守恒推导: $\\text{Var}[x_t] = (\\sqrt{\\bar{\\alpha}_t})^2 \\cdot \\text{Var}[x_0] "
        "+ (\\sqrt{1-\\bar{\\alpha}_t})^2 \\cdot \\text{Var}[\\epsilon] "
        "= \\bar{\\alpha}_t + (1-\\bar{\\alpha}_t) = 1$ (假设 $\\text{Var}[x_0]=1$, $\\text{Var}[\\epsilon]=1$)。"
        "如果不带根号而直接用 $\\bar{\\alpha}_t$ 和 $1-\\bar{\\alpha}_t$ 作系数，则方差为 "
        "$\\bar{\\alpha}_t^2 + (1-\\bar{\\alpha}_t)^2 \\neq 1$，破坏分布一致性。"
        "标准差 $\\sigma = \\sqrt{\\text{Var}}$; 混淆两者会导致加噪过强或过弱。"
        "这也是为什么 noise schedule 定义在 $\\beta_t$ (方差) 但加噪公式的系数是 $\\sqrt{\\cdot}$ (标准差)。"
    ),

    "解释 beta_t 的角色: 它是训练的还是预设的？推理时会变吗？": (
        "$\\beta_t$ 是**预设的超参数**，不是可学习的参数。Linear schedule 设 $\\beta_1=10^{-4}$, "
        "$\\beta_T=0.02$，等差递增; Cosine schedule 先定义 $\\bar{\\alpha}_t$ 的形状再反推 $\\beta_t$。"
        "训练时 $\\beta_t$ 固定不变，由此确定 $\\alpha_t = 1-\\beta_t$, "
        "$\\bar{\\alpha}_t = \\prod_{s=1}^{t}\\alpha_s$ 等所有相关量。"
        "推理时 $\\beta_t$ 同样固定 -- 采样公式 (DDPM/DDIM) 使用与训练相同的 schedule。"
        "所有与时间相关的量 ($\\beta_t, \\alpha_t, \\bar{\\alpha}_t, \\sigma_t$) 都是 $t$ 的确定函数，"
        "可以预先计算为查找表。网络唯一学习的是去噪函数 $\\epsilon_\\theta(x_t, t)$ 本身。"
    ),

    "解释为什么 UNet 需要知道时间步 t，以及 sinusoidal embedding 的注入机制": (
        "同一个 UNet 处理从 $t=1$ (几乎无噪声) 到 $t=T$ (纯噪声) 的所有时间步，"
        "但不同噪声水平需要完全不同的去噪策略。如果不告诉网络当前 $t$，"
        "它无法判断输入的噪声程度，也无法选择正确的去噪行为。"
        "仅通过 $\\beta_t$ 是不够的 -- $\\beta_t$ 只描述相邻步的变化，网络需要全局噪声水平信息。"
        "注入机制: 整数 $t$ 先通过 sinusoidal embedding 映射到高维向量 "
        "(与 Transformer 的位置编码相同的公式: $\\sin(t/10000^{2i/d})$, $\\cos(t/10000^{2i/d})$)，"
        "再经 2 层 MLP 变换，最终在每个 ResBlock 中通过 scale + shift (AdaGN) 调制特征: "
        "$h = \\gamma(t) \\cdot \\text{GroupNorm}(x) + \\beta(t)$。这让网络在每一层都能根据 $t$ 调整行为。"
    ),

    "列出 5 种条件注入方式及其适用场景 (Cross-Attention, ControlNet, concat, **IP-Adapter**, CFG)": (
        "5 种条件注入方式: "
        "(1) **Cross-Attention**: 文本条件的标准方式，$Q$ 来自图像特征，$K/V$ 来自 CLIP 文本 embedding，"
        "适合全局语义控制 (prompt 描述); "
        "(2) **ControlNet**: 通过冻结 UNet + 可训练副本 + zero conv 注入空间条件 "
        "(Canny edge, pose, depth map)，精确控制空间结构; "
        "(3) **Concat (通道拼接)**: 将条件图与噪声 latent 在通道维拼接后输入 UNet，"
        "用于 inpainting (mask + masked image) 和 img2img; "
        "(4) **IP-Adapter**: 通过 decoupled cross-attention 注入 CLIP 图像特征 "
        "(独立的 $K_i/V_i$ 投影)，适合风格迁移和图像参考; "
        "(5) **CFG (Classifier-Free Guidance)**: 推理时技术而非架构修改，"
        "通过放大条件/无条件预测差值来增强 prompt 遵循度。"
        "空间对齐条件 (edge/pose) 用 ControlNet/concat 而非 cross-attention，"
        "因为 attention 的全局感受野会模糊空间细节。"
    ),

    "解释 ControlNet 的 zero convolution 设计哲学": (
        "ControlNet 的核心设计是: 冻结预训练 UNet，克隆其 encoder 作为可训练副本，"
        "通过 1x1 zero convolution (权重和偏置初始化为 0) 连接两者。"
        "Zero conv 的设计哲学是**安全的渐进式学习**: 训练初期 zero conv 输出恒为 0，"
        "等于没有加入任何条件信号，完全保留预训练 UNet 的生成能力; "
        "随着训练进行，zero conv 权重从 0 自动增长，条件信号逐渐注入。"
        "权重增长速率由梯度自动决定，不需要人为的 warm-up 或调度策略。"
        "这保证了训练不会在初期因随机初始化的大梯度破坏预训练权重 -- "
        "对比: 如果用 Xavier/Kaiming 初始化，初始输出就是随机噪声，直接叠加到 UNet 会灾难性遗忘。"
        "训练成本仅约 600 GPU-hours (A100)，远低于从头训练 SD 的 150,000 GPU-hours。"
    ),

    "用一句话描述 DDPM/DDIM/Score matching 在 SDE 框架下的统一关系": (
        "SDE 统一视角: **DDPM 对应前向 SDE 的离散化 (加噪)，"
        "Score matching 训练网络估计 score function $\\nabla_{x_t}\\log p_t(x_t)$，"
        "DDIM 是反向 ODE (probability flow ODE) 的数值解 (确定性采样)**。"
        "具体来说，$\\epsilon$-prediction 与 score function 仅差一个缩放系数: "
        "$\\nabla_{x_t}\\log p_t(x_t) = -\\epsilon/\\sqrt{1-\\bar{\\alpha}_t}$。"
        "DDPM 的随机采样对应反向 SDE (含 Langevin noise)，DDIM 的确定性采样对应反向 ODE (无 noise)。"
        "三者殊途同归: DDPM 定义过程，Score matching 提供训练目标，SDE/ODE 提供灵活的采样器选择。"
    ),

    # --- 6 new questions for expanded content (sections 11-16) ---

    "比较 4 种位置编码方法 (Learned Absolute, Sinusoidal, Shaw Relative, RoPE) 的优劣和代表模型": (
        "(1) **Learned Absolute**: 每个位置学习 $d$-维向量加到 embedding，简单有效但长度固定为 $L_{\\max}$，"
        "无法泛化到训练时未见的序列长度，代表模型 GPT-2/BERT; "
        "(2) **Sinusoidal**: 用 $\\sin/\\cos$ 不同频率手工设计，核心性质是相对位置可表示为旋转矩阵 "
        "$\\text{PE}(\\text{pos}+k) = M_k \\cdot \\text{PE}(\\text{pos})$，理论上可外推但实际效果有限，"
        "代表原始 Transformer; "
        "(3) **Shaw Relative**: 在 attention score 中直接加入可学习的相对距离向量 $a_{ij}^K$，"
        "天然支持任意长度但实现复杂，代表 Transformer-XL; "
        "(4) **RoPE**: 将旋转矩阵直接应用到 Q/K 向量 (非 embedding)，利用 $R_m^\\top R_n = R_{n-m}$ "
        "使 attention score 只依赖相对位置，支持 NTK-aware 长度外推，代表 LLaMA/Qwen。"
        "面试趋势: 当前主流 LLM 几乎全部使用 RoPE。"
    ),

    "推导 KV-Cache 的显存公式，并估算 LLaMA-2 7B 在 4096 上下文时的 cache 大小": (
        "KV-Cache 公式: $\\text{Memory} = 2 \\times n_{\\text{layers}} \\times d_{\\text{model}} "
        "\\times \\text{seq\\_len} \\times \\text{dtype\\_bytes}$。"
        "因子 2 是因为需要同时缓存 K 和 V 两个矩阵。每层每个 token 缓存一个 K 向量和一个 V 向量，"
        "维度均为 $d_{\\text{model}}$。"
        "LLaMA-2 7B 估算: $n_{\\text{layers}}=32$, $d_{\\text{model}}=4096$, float16 (2 bytes), "
        "seq_len=4096: $2 \\times 32 \\times 4096 \\times 4096 \\times 2 = 2$ GB。"
        "若 seq_len=32K 则 cache 为 16 GB，超过模型参数本身 (14GB)! "
        "KV-Cache 与 seq_len 线性增长是长上下文推理的主要瓶颈。"
        "优化方法: GQA (LLaMA-2 70B 使用，cache 缩小 $1/4$-$1/8$)、"
        "Paged Attention (vLLM，消除显存碎片)、Sliding Window (Mistral，固定上限)。"
    ),

    "解释 noise ($\\epsilon$) prediction vs $x_0$ prediction vs $v$-prediction 的方差差异和适用场景": (
        "三种参数化的核心差异在目标方差: "
        "$\\epsilon$-prediction 的目标 $\\epsilon \\sim \\mathcal{N}(0,\\mathbf{I})$，方差恒为 1; "
        "$x_0$-prediction 的目标方差 $\\frac{1-\\bar{\\alpha}_t}{\\bar{\\alpha}_t}$，"
        "在 $t \\to T$ 时趋向无穷，导致大 $t$ 时梯度爆炸; "
        "$v$-prediction ($v = \\sqrt{\\bar{\\alpha}_t}\\epsilon - \\sqrt{1-\\bar{\\alpha}_t}x_0$) "
        "在 $t \\approx 0$ 时退化为预测信号，$t \\approx T$ 时退化为预测噪声，方差全程近似均匀。"
        "实际使用: DDPM 和 SD v1.x 用 $\\epsilon$-prediction; SD v2 和 SDXL 部分训练用 $v$-prediction; "
        "$x_0$-prediction 较少直接使用但可通过公式互转: "
        "$\\hat{x}_0 = (x_t - \\sqrt{1-\\bar{\\alpha}_t}\\hat{\\epsilon})/\\sqrt{\\bar{\\alpha}_t}$。"
    ),

    "解释 VAE 重参数化技巧 (reparameterization trick) 解决了什么问题，写出公式": (
        "问题: VAE 需要从 encoder 输出的分布 $q_\\phi(z|x) = \\mathcal{N}(\\mu, \\sigma^2)$ "
        "中采样 $z$，但「采样」操作不可微分，梯度无法通过 $z$ 反向传播到 encoder 参数 $\\phi$。"
        "重参数化技巧将随机性分离到与模型参数无关的外部噪声: "
        "$z = \\mu + \\sigma \\odot \\epsilon$, $\\epsilon \\sim \\mathcal{N}(0, \\mathbf{I})$。"
        "这样 $z$ 对 $\\mu$ 和 $\\sigma$ 都是可微的确定性函数 (加法和乘法)，"
        "梯度可以正常回传: $\\partial z/\\partial \\mu = 1$, $\\partial z/\\partial \\sigma = \\epsilon$。"
        "训练时每次前向传播采样不同的 $\\epsilon$，等价于对 ELBO loss 做单样本 Monte Carlo 估计。"
        "这个技巧是所有 VAE 变体 (包括 SD 的潜在空间 VAE) 能端到端训练的关键。"
    ),

    "描述 ControlNet 的训练流程: 冻结了什么，训练了什么，为什么训练成本远低于从头训练 SD": (
        "ControlNet 训练流程: (1) **冻结**原始 SD UNet 的全部参数 (locked copy); "
        "(2) **克隆** UNet 的 encoder blocks (约 50% 参数) 作为 trainable copy; "
        "(3) 在每个连接点插入 1x1 zero conv (weight=0, bias=0); "
        "(4) 用 (image, condition, prompt) 三元组训练，loss 与标准 SD 相同的 $\\epsilon$-prediction MSE。"
        "训练成本低的原因: 克隆保留了 SD 学到的图像理解能力，训练只需学习「条件信息如何对齐到已有特征」; "
        "zero conv 保证初始输出为 0 (不破坏预训练)，避免灾难性遗忘; "
        "实际训练量约 600 GPU-hours (8xA100)，仅为从头训练 SD (约 150,000 GPU-hours) 的 0.4%。"
        "多 ControlNet 可通过加权求和组合: $\\text{output} = \\text{UNet}(x_t) + \\sum_i w_i \\cdot \\text{ControlNet}_i(x_t, c_i)$。"
    ),

    "对比 SD/SDXL/SD3/Midjourney/Firefly 的架构差异和各自定位": (
        "**SD 1.x/2.x**: UNet + CLIP text encoder，最广泛的开源基础模型，社区生态庞大，适合研究和 fine-tune; "
        "**SDXL**: 更大的 UNet + 双 CLIP encoder (OpenCLIP ViT-G + CLIP ViT-L)，质量提升但推理更慢; "
        "**SD3**: 用 MMDiT (Multimodal Diffusion Transformer) 替代 UNet，采用 Flow Matching 训练，"
        "代表 UNet -> DiT 的架构演进; "
        "**Midjourney**: 闭源服务，美学风格最强，Discord 交互，适合创意设计但不可定制部署; "
        "**Adobe Firefly**: 闭源企业级产品，核心卖点是**版权安全** -- 仅用 Adobe Stock 授权数据训练，"
        "适合商业场景。架构演进趋势: UNet -> DiT，因为 Transformer 有更好的 scaling law、"
        "与 LLM 共享基础设施、天然支持多模态统一。"
    ),
}


def build_updated_selfcheck(existing_content: str) -> str:
    """Replace Self-Check section with answered version + new questions."""
    # Find Self-Check section boundaries
    sc_marker = "### Self-Check Questions"
    sc_idx = existing_content.find(sc_marker)
    if sc_idx == -1:
        print("[FAIL] Self-Check Questions section not found")
        sys.exit(1)

    # Find next section after Self-Check (## 面试快速参考)
    next_section_marker = "\n## "
    after_sc = existing_content[sc_idx + len(sc_marker):]
    next_idx = after_sc.find(next_section_marker)
    # next_idx == -1 means Self-Check is the last section
    sc_end = len(existing_content) if next_idx == -1 else sc_idx + len(sc_marker) + next_idx

    # Extract existing checklist lines
    sc_block = existing_content[sc_idx:sc_end]
    existing_lines = [
        line.strip() for line in sc_block.split("\n")
        if line.strip().startswith("- [ ]")
    ]

    # Build new Self-Check section
    parts: list[str] = [sc_marker, ""]

    # Process existing questions -- add answers
    for line in existing_lines:
        # Extract question text (after "- [ ] ")
        q_text = line[6:].strip()
        parts.append(line)

        # Find matching answer
        answer = None
        for key, val in ANSWERS.items():
            if key in q_text or q_text in key:
                answer = val
                break

        if answer:
            # Format as blockquote
            parts.append("")
            answer_lines = f"> **Answer**: {answer}".split("\n")
            parts.extend(answer_lines)
        else:
            parts.append("")
            parts.append(f"> **Answer**: (TODO: answer for \"{q_text[:40]}...\")")

        parts.append("")

    # Add 6 new questions for expanded content
    new_questions = [
        "比较 4 种位置编码方法 (Learned Absolute, Sinusoidal, Shaw Relative, RoPE) 的优劣和代表模型",
        "推导 KV-Cache 的显存公式，并估算 LLaMA-2 7B 在 4096 上下文时的 cache 大小",
        "解释 noise ($\\epsilon$) prediction vs $x_0$ prediction vs $v$-prediction 的方差差异和适用场景",
        "解释 VAE 重参数化技巧 (reparameterization trick) 解决了什么问题，写出公式",
        "描述 ControlNet 的训练流程: 冻结了什么，训练了什么，为什么训练成本远低于从头训练 SD",
        "对比 SD/SDXL/SD3/Midjourney/Firefly 的架构差异和各自定位",
    ]

    for q in new_questions:
        parts.append(f"- [ ] {q}")
        parts.append("")
        answer = ANSWERS.get(q, "(TODO)")
        answer_lines = f"> **Answer**: {answer}".split("\n")
        parts.extend(answer_lines)
        parts.append("")

    new_sc = "\n".join(parts).rstrip()

    # Replace old Self-Check with new
    updated = existing_content[:sc_idx] + new_sc + "\n" + existing_content[sc_end:]
    return updated


def main() -> None:
    """Answer all checklist questions and add new ones."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?", (DOC_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] Document id={DOC_ID} not found")
            sys.exit(1)

        existing = row[0]
        updated = build_updated_selfcheck(existing)

        # Update in DB
        conn.execute(
            "UPDATE company_documents SET content = ? WHERE id = ?",
            (updated, DOC_ID),
        )
        conn.commit()

        old_len = len(existing)
        new_len = len(updated)
        print(
            f"[DONE] Updated document id={DOC_ID}: "
            f"{old_len} -> {new_len} chars (+{new_len - old_len})"
        )

        # Verify: count answered questions
        answered = updated.count("> **Answer**:")
        checkboxes = updated.count("- [ ]")
        print(f"[DONE] {answered} answers for {checkboxes} checklist items")

        # Verify: all original questions preserved
        original_q_count = existing.count("- [ ]")
        print(
            f"[DONE] Original questions: {original_q_count}, "
            f"New total: {checkboxes} (+{checkboxes - original_q_count} new)"
        )

        # Verify: Self-Check and Quick Reference preserved
        if "### Self-Check Questions" in updated:
            print("[DONE] Self-Check Questions section preserved")
        if "## 面试快速参考" in updated:
            print("[DONE] Quick Reference section preserved")

        # Verify no blank lines between table rows (regression check)
        table_issue = False
        lines = updated.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("|") and i + 1 < len(lines):
                if lines[i + 1].strip() == "" and i + 2 < len(lines) and lines[i + 2].startswith("|"):
                    table_issue = True
                    break
        if table_issue:
            print("[WARN] Found blank line between table rows")
        else:
            print("[DONE] No blank lines between table rows")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
