"""Seed script: Expand Adobe Prep Day1 with 3 more sections.

Expansion B adds:
  14. VAE deep-dive (encoder/decoder, KL divergence, reparameterization trick,
      beta-VAE, VQ-VAE comparison)
  15. ControlNet expanded (architecture detail, training procedure, multi-ControlNet
      composition, T2I-Adapter, IP-Adapter)
  16. Industry landscape (major players, architecture evolution UNet->DiT,
      application domains)

Uses StudyNoteBuilder for section/formula construction, then patches the
existing document in mle_prep.db (id=18) by inserting before Self-Check.
"""

import importlib.util
import re
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
    b.add_term("VAE", "Variational Autoencoder",
               "Generative model that learns a smooth latent space via KL regularization")
    b.add_term("VQ-VAE", "Vector Quantized VAE",
               "Discrete-latent variant using a learned codebook")
    b.add_term("ControlNet", "ControlNet",
               "Adds spatial conditioning to pretrained diffusion models via trainable copy")
    b.add_term("DiT", "Diffusion Transformer",
               "Transformer-based diffusion backbone replacing UNet")
    b.add_term("IP-Adapter", "Image Prompt Adapter",
               "Image-conditioned adapter using decoupled cross-attention")

    # ---- Section 14: VAE Deep-Dive ----
    b.add_section("14. VAE 深度解析: Stable Diffusion 的潜在空间引擎", [
        "Stable Diffusion 在 **潜在空间** 而非像素空间做扩散，而将图像映射到潜在空间"
        "的正是 VAE (Variational Autoencoder)。理解 VAE 的数学原理对理解整个 pipeline 至关重要。",

        "### 14.1 VAE 的 Encoder-Decoder 架构\n\n"
        "**Encoder** $q_\\phi(z|x)$: 将图像 $x \\in \\mathbb{R}^{H \\times W \\times 3}$ "
        "映射到潜在分布的参数 $(\\mu, \\sigma^2)$，"
        "其中 $\\mu, \\log\\sigma^2 \\in \\mathbb{R}^{h \\times w \\times c}$ "
        "(SD 中 $h = H/8, w = W/8, c = 4$)。\n\n"
        "**Decoder** $p_\\theta(x|z)$: 从潜在向量 $z$ 重建图像。\n\n"
        "**关键区别 vs 普通 Autoencoder**: VAE 的 encoder 输出的不是确定性向量，而是一个"
        "**概率分布的参数**。每次采样得到不同的 $z$，迫使 decoder 在整个潜在区域都学会重建，"
        "而不是死记单个点。",

        "### 14.2 KL 散度正则化\n\n"
        "VAE 的 loss 由两部分组成:",

        FormulaBlock(
            latex=(r"\mathcal{L}_{\text{VAE}} = "
                   r"\underbrace{\mathbb{E}_{z \sim q_\phi(z|x)}"
                   r"\big[-\log p_\theta(x|z)\big]}_{\text{Reconstruction Loss}}"
                   r" + \underbrace{D_{\text{KL}}\big(q_\phi(z|x) \| "
                   r"\mathcal{N}(0, \mathbf{I})\big)}_{\text{KL Regularization}}"),
            explanation="VAE 的 ELBO (Evidence Lower Bound) loss:",
        ),

        "**Reconstruction Loss**: 衡量重建质量 (像素级 MSE 或感知 loss)。\n\n"
        "**KL Divergence**: 强制 encoder 输出的分布接近标准正态 $\\mathcal{N}(0, \\mathbf{I})$。\n\n"
        "**KL 的闭式解** (两个高斯之间):",

        FormulaBlock(
            latex=(r"D_{\text{KL}} = -\frac{1}{2} \sum_{j=1}^{d} "
                   r"\left(1 + \log\sigma_j^2 - \mu_j^2 - \sigma_j^2\right)"),
            explanation="对每个潜在维度 $j$ 独立计算，无需采样估计:",
        ),

        "**为什么正则化到 $\\mathcal{N}(0, \\mathbf{I})$?**\n"
        "- 保证潜在空间是**连续的** (相近的 $z$ 解码为相似图像) 和**完整的** "
        "(任意采样的 $z$ 都能解码为合理图像)\n"
        "- 没有 KL 正则化，encoder 会把不同类别映射到互相远离的孤立点，中间区域"
        "decoder 无法处理\n"
        "- 这正是 VAE 可以做生成 (而普通 AE 不行) 的核心原因",

        "### 14.3 重参数化技巧 (Reparameterization Trick)\n\n"
        "**问题**: 从 $z \\sim q_\\phi(z|x) = \\mathcal{N}(\\mu, \\sigma^2)$ 采样是"
        "不可微的操作，无法反向传播。\n\n"
        "**解决方案**: 将随机性分离到外部噪声:",

        FormulaBlock(
            latex=r"z = \mu + \sigma \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, \mathbf{I})",
            explanation="重参数化: 采样过程变为确定性变换 + 外部随机噪声:",
        ),

        "**关键洞察**:\n"
        "- $\\epsilon$ 与模型参数无关，梯度可以通过 $\\mu$ 和 $\\sigma$ 正常传播\n"
        "- 这将不可微的「采样」操作转化为可微的「线性变换」\n"
        "- 训练时每次前向传播采样不同的 $\\epsilon$，等价于对 ELBO 做 Monte Carlo 估计\n"
        "- 推理时可以直接用 $z = \\mu$ (取均值) 或采样多次取平均",

        "### 14.4 $\\beta$-VAE: 控制重建与正则化的平衡\n\n"
        "原始 VAE 中 KL 项权重为 1，但实践中常需要调整:",

        FormulaBlock(
            latex=(r"\mathcal{L}_{\beta\text{-VAE}} = "
                   r"\text{Reconstruction Loss} + "
                   r"\beta \cdot D_{\text{KL}}"),
            explanation="$\\beta$-VAE 引入超参数 $\\beta$ 控制正则化强度:",
        ),

        "- $\\beta > 1$: 更强的正则化，潜在空间更平滑可插值，但重建质量下降 "
        "(更模糊)\n"
        "- $\\beta < 1$: 更好的重建质量，但潜在空间可能不连续\n"
        "- $\\beta = 0$: 退化为普通 Autoencoder (没有生成能力)\n\n"
        "**Stable Diffusion 的选择**: SD 使用较小的 KL 权重 (约 $10^{-6}$)，"
        "因为潜在空间的平滑性由扩散模型进一步保证，VAE 侧重高质量重建。",

        "### 14.5 VAE vs VQ-VAE: 连续 vs 离散潜在空间",
    ])

    b.add_comparison_table(
        headers=["特征", "VAE", "VQ-VAE"],
        rows=[
            ["潜在表示", "连续向量 $z \\in \\mathbb{R}^d$",
             "离散 codebook index $z_q \\in \\{1,...,K\\}$"],
            ["正则化", "KL divergence to $\\mathcal{N}(0,\\mathbf{I})$",
             "Codebook commitment loss + EMA update"],
            ["采样方式", "重参数化技巧", "Straight-through estimator"],
            ["潜在空间性质", "连续、可插值", "离散、组合式"],
            ["典型应用", "Stable Diffusion (latent space)",
             "DALL-E (image tokenizer), AudioLM"],
            ["优势", "平滑的潜在空间，易于与扩散模型结合",
             "避免 posterior collapse，高压缩率"],
            ["劣势", "可能产生模糊重建 (KL 过强时)",
             "Codebook collapse，需要精心调参"],
        ],
        title="VAE vs VQ-VAE 对比",
    )

    # ---- Section 15: ControlNet Expanded ----
    b.add_section("15. ControlNet 架构与训练深度解析", [
        "第 9 节介绍了 ControlNet 的 Zero Convolution 设计哲学。"
        "本节深入架构细节、训练流程、多 ControlNet 组合，以及与其他条件注入方法的对比。",

        "### 15.1 ControlNet 的完整架构\n\n"
        "ControlNet 的核心思想: **冻结原始预训练 UNet，创建一个可训练的副本"
        "(trainable copy)，通过 zero convolution 连接。**\n\n"
        "具体结构:\n"
        "1. **Locked Copy**: 原始 SD UNet 的 encoder blocks，权重冻结不更新\n"
        "2. **Trainable Copy**: UNet encoder blocks 的完整拷贝，参数可训练\n"
        "3. **Zero Convolution**: 1x1 卷积层，权重和偏置初始化为 0\n"
        "4. **连接方式**: Trainable copy 的输出经 zero conv 后 **加到** locked copy "
        "对应层的输出上\n\n"
        "**数据流**:\n"
        "- 条件图 (如 Canny edge) 经过轻量 encoder 后输入 trainable copy\n"
        "- Trainable copy 处理条件信息，输出经 zero conv (初始为 0)\n"
        "- Zero conv 输出加到 frozen UNet 的 skip connections 和 middle block 上\n"
        "- 训练初期 zero conv 输出为 0，等于没加条件 -> 不破坏预训练权重\n"
        "- 随训练进行，zero conv 权重逐渐增大 -> 条件信号逐渐注入",

        "### 15.2 训练流程\n\n"
        "**Step 1**: 冻结原始 SD UNet 的所有参数\n\n"
        "**Step 2**: 克隆 UNet encoder (约 50% 的参数) 作为 trainable copy\n\n"
        "**Step 3**: 在每个连接点插入 zero convolution (1x1 conv, weight=0, bias=0)\n\n"
        "**Step 4**: 训练数据为 (image, condition, prompt) 三元组\n\n"
        "**训练 loss**: 与标准 SD 相同的 $\\epsilon$-prediction MSE loss，"
        "只是输入额外包含条件图\n\n"
        "**训练量**: 在单个条件类型 (如 Canny) 上，使用 8 张 A100 训练约 600 GPU-hours。"
        "远小于从头训练 SD (约 150,000 GPU-hours)，这是 ControlNet 设计的核心价值。\n\n"
        "**为什么克隆 encoder 而不是从头训练?**\n"
        "- 克隆保留了 SD 学到的图像理解能力\n"
        "- 只需要学习如何将条件信息对齐到这些特征上\n"
        "- 训练从「不改变任何输出」(zero conv) 开始，安全地渐进式学习",

        "### 15.3 多 ControlNet 组合\n\n"
        "可以同时使用多个 ControlNet (如 pose + depth + canny):\n\n"
        "**组合方式**: 每个 ControlNet 独立处理自己的条件图，输出通过加权求和"
        "后加到 UNet:\n\n"
        "$\\text{output} = \\text{UNet}(x_t) + \\sum_i w_i \\cdot \\text{ControlNet}_i"
        "(x_t, c_i)$\n\n"
        "其中 $w_i$ 是每个 ControlNet 的权重 (condition scale)。\n\n"
        "**实践建议**:\n"
        "- 权重总和建议在 1.0-1.5 之间，过大会产生伪影\n"
        "- 互补条件效果好 (pose + depth)，冗余条件可能冲突 (两种 edge)\n"
        "- 推理速度随 ControlNet 数量线性增加",

        "### 15.4 T2I-Adapter vs ControlNet",
    ])

    b.add_comparison_table(
        headers=["特征", "ControlNet", "T2I-Adapter"],
        rows=[
            ["参数量", "约 361M (UNet encoder 的完整拷贝)",
             "约 77M (轻量级 adapter)"],
            ["训练策略", "冻结原始 UNet + 训练完整 copy",
             "冻结原始 UNet + 训练小型 adapter"],
            ["连接方式", "加到 skip connections + middle block",
             "加到 encoder 的中间特征"],
            ["Zero Conv", "使用 (渐进式注入)", "不使用 (直接加法)"],
            ["条件控制精度", "高 (完整 encoder 容量)", "中等 (参数量有限)"],
            ["训练成本", "约 600 GPU-hours (A100)", "约 100 GPU-hours"],
            ["多条件组合", "加权求和", "加权求和 (更轻量)"],
        ],
        title="ControlNet vs T2I-Adapter 对比",
    )

    b.add_section("15. ControlNet (续): IP-Adapter 架构", [
        "### 15.5 IP-Adapter: 图像作为 Prompt\n\n"
        "IP-Adapter (Image Prompt Adapter) 允许用一张参考图像作为生成条件，"
        "与 ControlNet 的空间条件 (edge, pose) 不同，它提取的是**语义风格信息**。\n\n"
        "**架构**:\n"
        "1. **Image Encoder**: 使用 CLIP image encoder 提取参考图像的特征向量\n"
        "2. **Projection Network**: 线性层将 CLIP 特征投影到与文本 embedding 相同的维度\n"
        "3. **Decoupled Cross-Attention**: 关键创新 -- 不与文本 token 共享 cross-attention，"
        "而是新增一组独立的 K/V 投影层:\n\n"
        "$\\text{Attn}_{\\text{text}} = \\text{softmax}(QK_t^\\top/\\sqrt{d})V_t$\n\n"
        "$\\text{Attn}_{\\text{image}} = \\text{softmax}(QK_i^\\top/\\sqrt{d})V_i$\n\n"
        "$\\text{output} = \\text{Attn}_{\\text{text}} + \\lambda \\cdot "
        "\\text{Attn}_{\\text{image}}$\n\n"
        "其中 $K_t, V_t$ 是文本分支的 K/V (冻结)，$K_i, V_i$ 是图像分支新增的 K/V (可训练)，"
        "$\\lambda$ 控制图像条件的强度。\n\n"
        "**为什么用 Decoupled Cross-Attention?**\n"
        "- 如果图像特征和文本 token 拼接后共享 attention，两种模态会互相干扰\n"
        "- 独立的 K/V 让图像信息有自己的「通道」，不影响文本理解能力\n"
        "- 训练时只需训练图像分支的 K/V 投影 + projection network，非常高效",
    ])

    # ---- Section 16: Industry Landscape ----
    b.add_section("16. 图像生成产业格局与技术演进", [
        "面试中常被问到对行业的理解。以下是截至 2024 年底的主要玩家和技术趋势。",

        "### 16.1 主要产品与公司",
    ])

    b.add_comparison_table(
        headers=["产品", "公司", "架构", "特点", "开源"],
        rows=[
            ["Stable Diffusion 1.x/2.x", "Stability AI", "UNet + CLIP",
             "最广泛的开源基础模型，社区生态庞大", "是"],
            ["SDXL", "Stability AI", "UNet (更大) + dual CLIP",
             "更高质量，双文本 encoder", "是"],
            ["Stable Diffusion 3", "Stability AI", "MMDiT (Multimodal DiT)",
             "Transformer 替代 UNet，Flow Matching", "是"],
            ["Midjourney", "Midjourney Inc.", "未公开",
             "美学风格最强，Discord 交互", "否"],
            ["DALL-E 3", "OpenAI", "未公开 (推测 DiT)",
             "ChatGPT 集成，prompt 理解力强", "否"],
            ["Adobe Firefly", "Adobe", "未公开",
             "企业级，版权安全 (仅用授权数据训练)", "否"],
            ["Imagen 2/3", "Google DeepMind", "Cascaded Diffusion / DiT",
             "极高文本渲染能力", "否"],
            ["Flux", "Black Forest Labs", "DiT-based",
             "SD 原作者团队新作，高质量开源", "部分"],
            ["Fooocus", "社区", "基于 SDXL",
             "简化 UI，类 Midjourney 体验", "是"],
        ],
        title="主要图像生成产品对比 (2024)",
    )

    b.add_section("16. (续): 架构演进与应用", [
        "### 16.2 架构演进: UNet -> DiT\n\n"
        "**UNet 时代** (2020-2023):\n"
        "- DDPM, SD 1.x/2.x, SDXL 均使用 UNet 作为去噪网络\n"
        "- UNet 的 skip connections 天然适合「先破坏再恢复」的扩散过程\n"
        "- 但 UNet 的 attention 层只占部分层，scaling 受限\n\n"
        "**DiT 时代** (2023-至今):\n"
        "- Peebles & Xie (2023) 提出 Diffusion Transformer (DiT): "
        "用纯 Transformer 替代 UNet\n"
        "- 将带噪声的图像 patch 化 (类似 ViT)，用 Transformer blocks 处理\n"
        "- 时间步 $t$ 和类别条件通过 AdaLN (Adaptive Layer Norm) 注入\n"
        "- **优势**: 更好的 scaling law (参数量翻倍 -> 质量持续提升)，"
        "与 LLM 共享基础设施\n"
        "- SD3 的 MMDiT、Flux、DALL-E 3 (推测) 都采用 DiT 架构\n\n"
        "**面试关键点**: 被问到「扩散模型的最新趋势」时，UNet -> DiT 的演进"
        "是核心答案。类比: CNN (视觉) -> ViT (视觉)，UNet (扩散) -> DiT (扩散)。",

        "### 16.3 核心应用领域\n\n"
        "1. **Text-to-Image**: 最成熟的应用，所有主要模型都支持\n"
        "2. **Inpainting**: 擦除并重绘图像区域，SD 有专门的 inpaint 模型 "
        "(额外 mask channel)\n"
        "3. **Outpainting**: 向外扩展图像边界，需要模型理解全局构图\n"
        "4. **Image-to-Image**: 以参考图为起点，加部分噪声后重新去噪，"
        "实现风格迁移/局部修改\n"
        "5. **Style Transfer**: 通过 IP-Adapter / LoRA / DreamBooth 实现风格控制\n"
        "6. **Video Generation**: 将扩散过程扩展到时序维度 "
        "(Stable Video Diffusion, Sora, Kling)\n\n"
        "**视频生成的技术挑战**:\n"
        "- 时序一致性: 帧间不能闪烁或物体突变\n"
        "- 计算量: 16 帧 512x512 的 latent 比单张图大 16 倍\n"
        "- 训练数据: 高质量视频-文本对比图像-文本对稀缺得多",

        "### 16.4 面试常见问题\n\n"
        "**Q: SD 和 Midjourney 的核心差异?**\n"
        "A: SD 是开源模型 (架构/权重公开)，可以 fine-tune 和部署; "
        "Midjourney 是闭源服务，美学质量领先但不可定制。企业场景通常选 SD "
        "(可控、可部署) 或 Adobe Firefly (版权安全)。\n\n"
        "**Q: 为什么大家都在转向 Transformer 架构?**\n"
        "A: 三个原因: (1) Scaling law 更优 -- Transformer 参数翻倍质量持续提升，"
        "UNet 到一定大小后收益递减; (2) 基础设施复用 -- 与 LLM 共享 GPU kernel "
        "和推理优化; (3) 多模态统一 -- Transformer 天然处理序列，"
        "图像 patch、文本 token、音频帧都可以统一为 token 序列。",
    ])

    # Build and extract just the section content (skip header/prereqs/terms)
    content = b.build()

    # Extract from section 14 onward (skip title, prerequisites, key terms)
    lines = content.split("\n")
    section_start = None
    for i, line in enumerate(lines):
        if line.startswith("## 14."):
            section_start = i
            break

    if section_start is None:
        print("[FAIL] Could not find section 14 in built content")
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

        # Verify all 3 new sections are present
        for sec_num in [14, 15, 16]:
            if f"## {sec_num}." not in updated:
                print(f"[FAIL] Section {sec_num} not found in updated document")
                sys.exit(1)
        print("[DONE] All 3 new sections (14, 15, 16) verified present")

        # Verify Self-Check and Quick Reference preserved
        if "### Self-Check Questions" in updated:
            print("[DONE] Self-Check Questions section preserved")
        if "## 面试快速参考" in updated:
            print("[DONE] Quick Reference section preserved")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
