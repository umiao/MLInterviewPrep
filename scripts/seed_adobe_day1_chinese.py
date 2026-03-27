"""Rewrite Adobe Day 1 (Diffusion Models) in Chinese with comprehensive expansions.

Incorporates user's supplement notes covering:
- Math symbol clarifications
- Variance conservation deep-dive
- Noise schedule beta_t mechanics
- Time step modeling rationale
- Sinusoidal embedding + UNet injection
- Condition injection panorama (Cross-Attention, ControlNet, IP-Adapter)
- ControlNet zero convolution philosophy
- DDIM + SDE unified framework
- Interview quick reference
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from study_note_builder import FormulaBlock, StudyNoteBuilder


def build_day1_chinese() -> StudyNoteBuilder:
    b = StudyNoteBuilder()
    b.set_title("Diffusion Models 深度指南 (Adobe Prep Day 1)")

    b.add_prerequisites([
        "基础概率论: 高斯分布、条件概率、贝叶斯定理",
        "神经网络基础: 前向/反向传播、损失函数、梯度下降",
        "VAE 概念: 编码器-解码器架构、潜在空间 (latent space)",
        "卷积神经网络: 卷积操作、特征图、UNet 跳跃连接",
    ])

    # Register all terms
    b.add_term("DDPM", "Denoising Diffusion Probabilistic Models",
               "通过逐步去噪来生成数据的概率模型")
    b.add_term("VAE", "Variational Autoencoder",
               "变分自编码器，将高维数据压缩到低维潜在空间")
    b.add_term("UNet", "U-shaped Network",
               "编码器-解码器对称结构，带跳跃连接的卷积网络")
    b.add_term("CFG", "Classifier-Free Guidance",
               "无分类器引导，推理时放大条件方向的采样策略")
    b.add_term("CLIP", "Contrastive Language-Image Pre-training",
               "对比学习预训练的图文对齐模型")
    b.add_term("DDIM", "Denoising Diffusion Implicit Models",
               "确定性采样方法，可跳步加速推理")
    b.add_term("SDE", "Stochastic Differential Equation",
               "随机微分方程，统一描述扩散过程的连续时间框架")
    b.add_term("ODE", "Ordinary Differential Equation",
               "常微分方程，DDIM 对应的确定性轨迹")
    b.add_term("ControlNet", "ControlNet",
               "通过零卷积渐进式注入空间控制信号的网络结构")
    b.add_term("IP-Adapter", "Image Prompt Adapter",
               "通过额外 cross-attention 层注入图像风格参考")
    b.add_term("Score Function", "Score Function",
               "数据分布的对数梯度，指向密度增大方向")

    # ===== Section 1: Math Foundations =====
    b.add_section("1. 数学符号与基础概念", [
        "在深入 Diffusion 模型之前，先明确几个核心数学符号的含义。",

        "### $\\mathcal{N}$ -- 高斯分布 (Gaussian Distribution)",
        "$\\mathcal{N}(x;\\, \\mu,\\, \\sigma^2)$ 表示变量 $x$ 服从均值为 $\\mu$、方差为 $\\sigma^2$ 的正态分布。",
        "当我们写 $q(x_t \\mid x_0) = \\mathcal{N}(x_t;\\, \\sqrt{\\bar{\\alpha}_t}\\, x_0,\\; (1 - \\bar{\\alpha}_t)\\, \\mathbf{I})$ 时：",
        "- $x_t$ 是随机变量（第 $t$ 步的噪声图像）",
        "- 均值 = $\\sqrt{\\bar{\\alpha}_t}\\, x_0$（原始图像被缩放）",
        "- 协方差矩阵 = $(1 - \\bar{\\alpha}_t)\\, \\mathbf{I}$（各维度独立同方差噪声）",

        "### $\\mathbf{I}$ -- 单位矩阵 (Identity Matrix)",
        "图像是高维数据（如 64x64x4 = 16,384 维）。$\\mathbf{I}$ 是对应维度的单位矩阵，意味着：",
        "- **每个维度（每个像素/通道）的噪声是独立的**",
        "- **每个维度的噪声方差相同**",
        "即我们往每个像素上加同等大小的、互不相关的高斯噪声。",
    ])

    # ===== Section 2: Forward Process =====
    b.add_section("2. 前向过程: 逐步加噪与方差守恒", [
        "**DDPM** 的前向过程将干净图像 $x_0$ 逐步加噪，经过 $T$ 步变成纯高斯噪声。",

        "### 单步加噪",
        "每一步在前一步结果上加少量高斯噪声，$\\beta_t \\in (0, 1)$ 控制噪声强度：",
        FormulaBlock(
            latex=r"q(x_t \mid x_{t-1}) = \mathcal{N}(x_t;\, \sqrt{1 - \beta_t}\, x_{t-1},\; \beta_t \mathbf{I})",
            explanation="单步加噪公式: 将前一步图像缩放 (信号衰减) 并加入方差为 beta_t 的噪声",
        ),

        "### 重参数化技巧: 一步跳到任意 $t$",
        "定义累积量：$\\alpha_t = 1 - \\beta_t$，$\\bar{\\alpha}_t = \\prod_{s=1}^{t} \\alpha_s$（累积信号保留率）。",
        "利用高斯分布的叠加性质，可以从 $x_0$ 直接采样 $x_t$，无需逐步迭代：",
        FormulaBlock(
            latex=r"x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1 - \bar{\alpha}_t}\, \epsilon, \quad \epsilon \sim \mathcal{N}(0, \mathbf{I})",
            explanation="一步采样公式: 信号部分 (根号alpha_bar * x_0) + 噪声部分 (根号(1-alpha_bar) * epsilon)",
        ),
        "**关键洞察:** 当 $t \\to T$ 时，$\\bar{\\alpha}_T \\to 0$，所以 $x_T \\approx \\epsilon$（纯噪声）。",

        "### 方差守恒: 为什么系数带根号？",
        "前向过程的核心约束是**总方差保持不变**（假设 $\\text{Var}(x_0) = 1$）：",
        FormulaBlock(
            latex=r"\text{Var}(x_t) = (\sqrt{\bar{\alpha}_t})^2 \cdot 1 + (\sqrt{1-\bar{\alpha}_t})^2 \cdot 1 = \bar{\alpha}_t + (1-\bar{\alpha}_t) = 1",
            explanation="方差守恒验证: 信号方差 + 噪声方差 = 1，总能量不变",
        ),
        "**标准差 vs 方差的区别** -- 这是常见混淆点：",

        "| 层面 | 信号部分 | 噪声部分 |",
        "|------|---------|---------|",
        "| **采样公式**（操作数值，用标准差） | $\\sqrt{\\bar{\\alpha}_t} \\cdot x_0$ | $\\sqrt{1-\\bar{\\alpha}_t} \\cdot \\epsilon$ |",
        "| **分布表达**（描述统计量，用方差） | 均值 = $\\sqrt{\\bar{\\alpha}_t}\\, x_0$ | 方差 = $(1-\\bar{\\alpha}_t)\\,\\mathbf{I}$ |",

        "**直觉总结:** 前向过程的本质是**在保持总方差守恒的前提下，逐步把信号能量转移成噪声能量**。",
    ])

    # ===== Section 3: Noise Schedule =====
    b.add_section("3. 噪声调度 $\\beta_t$ 的本质", [
        "### $\\beta_t$ 是预设的，不是学习的",
        "在原始 DDPM 中，$\\beta_t$ 从 $\\beta_1 = 10^{-4}$ 到 $\\beta_T = 0.02$ 线性插值，$T = 1000$ 步。"
        "这些数值是经验性选择的，**训练前完全固定，训练和推理用同一套**。",

        "### 推理时 $\\beta_t$ 不会动态调整",
        "图像逐步变清晰，不是因为 $\\beta_t$ 在变小，而是因为：",
        "- 早期（$t$ 大）：图像几乎全是噪声，网络做**粗略轮廓恢复**",
        "- 后期（$t$ 小）：图像已比较清晰，网络做**细节精修**",
        "- 每步减去的噪声量自然递减，因为剩余噪声越来越少",

        "### 所有变量都是 $t$ 的确定函数",

        "| 变量 | 含义 | 由 $t$ 决定？ |",
        "|------|------|-------------|",
        "| $\\beta_t$ | 单步噪声强度 | 由 schedule 查表 |",
        "| $\\alpha_t = 1-\\beta_t$ | 单步信号保留率 | 是 |",
        "| $\\bar{\\alpha}_t = \\prod \\alpha_s$ | 累积信号保留率 | 是 |",
        "| $\\sigma_t^2$ | 反向过程方差 | 通常设为 $\\beta_t$ 或 $\\tilde{\\beta}_t$ |",

        "**$t$ 是唯一的时钟，所有调度参数都是 $t$ 的确定函数，训练前就全部算好存成查找表。** "
        "网络唯一要学的是 $\\epsilon_\\theta(x_t, t)$ -- 给定噪声图和时钟，预测噪声。",

        "### Cosine vs Linear Schedule",
        "- **Linear**: $\\beta_t$ 从 $10^{-4}$ 线性增到 $0.02$。问题：后期 $\\bar{\\alpha}_t$ 骤降，信息突然消失",
        "- **Cosine**: 先设计 $\\bar{\\alpha}_t$ 的形状（余弦曲线），再反推 $\\beta_t$。信息销毁更均匀",
        "**设计哲学:** Cosine schedule 是\"先定义行为再推参数\"的典范。",
    ])

    # ===== Section 4: Time Step Modeling =====
    b.add_section("4. 为什么需要显式建模时间步 $t$", [
        "### 只告诉网络 $\\beta_t$ 不够",
        "$\\beta_t$ 只描述**单步噪声增量**，但网络需要知道的是**累积到现在，这张图被噪了多少**"
        " -- 这由 $\\bar{\\alpha}_t$ 描述，而 $\\bar{\\alpha}_t$ 是 $t$ 的函数。",

        "### 直觉",
        "- **$t = 990$**: 图像几乎是纯噪声，网络需要大胆地预测大幅度噪声",
        "- **$t = 10$**: 图像只有轻微噪声，网络需要精细地预测微弱噪声",
        "如果不告诉网络 $t$，它无法知道当前图片的噪声程度。同一张模糊的图，可能是 $t=500$ 的猫，"
        "也可能是 $t=200$ 的雾。网络需要 $t$ 来**校准预测尺度**。",

        "### Sinusoidal Embedding: 整数 $t$ -> 高维向量",
        "直接把标量 $t=500$ 丢给网络效果不好（数值尺度问题）。用和 Transformer 位置编码相同的方法：",
        FormulaBlock(
            latex=r"\text{emb}(t)_{2i} = \sin\!\left(\frac{t}{10000^{2i/d}}\right), \quad \text{emb}(t)_{2i+1} = \cos\!\left(\frac{t}{10000^{2i/d}}\right)",
            explanation="Sinusoidal 时间编码: 低频分量区分大阶段 (t=10 vs t=990), 高频分量区分相邻步 (t=500 vs t=501)",
        ),
        "再接一个可学习 MLP 变换: $t_{\\text{emb}} = \\text{MLP}(\\text{sinusoidal}(t))$（典型: 256维 -> Linear -> SiLU -> Linear -> 256维）",

        "### Scale + Shift 注入: 在每个 ResBlock 中调制特征",
        "```\nResNet Block 前向过程:\n"
        "1. h = Conv(x)                      # 正常卷积\n"
        "2. h = GroupNorm(h)                  # 归一化\n"
        "3. scale, shift = Linear(t_emb)      # 时间向量 -> 两组参数\n"
        "4. h = scale * h + shift             # 用时间信息调制特征\n"
        "5. h = activation(h)\n"
        "6. h = Conv(h)                       # 再一次卷积\n```",
        "**直觉:** 这在告诉每一层 -- \"现在是第500步，噪声程度是这样的，请相应调整你的特征处理方式。\"",
        "这也是为什么**一个 UNet 能处理所有 $T$ 个时间步** -- 它不是 $T$ 个不同的网络，"
        "而是一个网络通过时间条件化来适应不同的去噪难度。",
    ])

    # ===== Section 5: Reverse Process =====
    b.add_section("5. 反向过程: 从噪声生成图像", [
        "### 核心思想",
        "训练一个神经网络 $\\epsilon_\\theta(x_t, t)$ 来预测加在 $x_t$ 上的噪声 $\\epsilon$。",

        "### 训练目标 (简化 MSE Loss)",
        FormulaBlock(
            latex=r"\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon}\!\left[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\right]",
            explanation="训练损失: 预测噪声与真实噪声的均方误差。极简但高效。",
        ),
        "**为什么预测噪声 $\\epsilon$ 而非直接预测 $x_0$?**",
        "- $\\epsilon$-prediction 的方差更小、训练更稳定",
        "- 等价于估计 **Score Function** $\\nabla_x \\log p_t(x)$（见后文 SDE 统一框架）",

        "### 采样算法 (DDPM)",
        "从纯噪声 $x_T \\sim \\mathcal{N}(0, \\mathbf{I})$ 开始，逐步去噪：",
        "```\nfor t = T, T-1, ..., 1:\n"
        "    predicted_noise = UNet(x_t, t)\n"
        "    x_{t-1} = denoise_step(x_t, predicted_noise, t)  # 用 beta_t 系数\n"
        "    if t > 1: x_{t-1} += sigma_t * z  # 加少量随机噪声\nreturn x_0\n```",
    ])

    # ===== Section 6: Latent Diffusion =====
    b.add_section("6. Latent Diffusion / Stable Diffusion Pipeline", [
        "### 核心创新: 在潜在空间做扩散",
        "直接在像素空间（512x512x3 = 786,432维）做扩散计算量巨大。"
        "**Stable Diffusion** 的核心思路: 先用 **VAE** 将图像压缩到低维潜在空间，在那里做扩散。",

        "### 完整推理 Pipeline",
        '<div style="background:#f8f9fa; padding:16px; border-radius:8px; margin:16px 0; font-family:monospace; text-align:center;">'
        '<div style="display:flex; align-items:center; justify-content:center; gap:8px; flex-wrap:wrap;">'
        '<span style="background:#4a90d9; padding:6px 12px; border-radius:4px; color:white;">Text Prompt</span>'
        '<span style="color:#666;">-></span>'
        '<span style="background:#6b4c9a; padding:6px 12px; border-radius:4px; color:white;">CLIP Text Encoder</span>'
        '<span style="color:#666;">-></span>'
        '<span style="background:#d4a843; padding:6px 12px; border-radius:4px; color:white;">Cross-Attention</span>'
        '<span style="color:#666;">-></span>'
        '<span style="background:#c0392b; padding:6px 12px; border-radius:4px; color:white;">UNet (iterative denoise)</span>'
        '<span style="color:#666;">-></span>'
        '<span style="background:#27ae60; padding:6px 12px; border-radius:4px; color:white;">VAE Decoder</span>'
        '<span style="color:#666;">-></span>'
        '<span style="background:#2c3e50; padding:6px 12px; border-radius:4px; color:white;">Pixel Image</span>'
        '</div></div>',

        "### 关键数字",

        "| 指标 | 数值 |",
        "|------|------|",
        "| 像素分辨率 | 512x512 (v1.5), 1024x1024 (SDXL) |",
        "| Latent 维度 | 64x64x4 |",
        "| VAE 空间降采样 | 8x |",
        "| 压缩比 | ~48x (786,432 -> 16,384) |",

        "### Cross-Attention: 文本如何控制图像",
        "在 UNet 的每个 attention 层中：",
        "- **Query** 来自 noisy latent（图像问：\"我这个位置应该生成什么？\"）",
        "- **Key/Value** 来自 CLIP text embedding（文本答：\"这里应该是猫的耳朵\"）",
        "每个图像位置可以自由关注任意文本 token，实现灵活的语义对齐。",
    ])

    # ===== Section 7: CFG =====
    b.add_section("7. Classifier-Free Guidance (CFG)", [
        "**CFG** 是一种**推理策略**（不改网络结构），通过放大条件方向来增强生成质量。",

        "### 训练: 随机丢弃条件",
        "训练时以一定概率（如 10%）用空条件 $\\varnothing$ 替代文本条件，"
        "让同一个网络同时学会 conditional 和 unconditional 生成。",

        "### 推理公式",
        FormulaBlock(
            latex=r"\hat{\epsilon} = \epsilon_\theta(x_t, \varnothing) + w \cdot (\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing))",
            explanation="CFG 公式: unconditional 预测 + w 倍的 (conditional - unconditional) 方向",
        ),
        "- $w$ 是 **guidance scale**:",
        "  - $w = 1$: 标准 conditional generation",
        "  - $w = 7.5$（典型值）: 增强文本一致性，图像更\"听话\"但多样性下降",
        "  - $w$ 过大: 出现 artifacts（过饱和、不自然）",
        "  - $w < 1$: 更自由，多样性增加但可能偏离 prompt",
        "- **代价**: 每步需要两次前向传播（一次 conditional，一次 unconditional），推理成本 2x",
    ])

    # ===== Section 8: Condition Injection Panorama =====
    b.add_section("8. 条件注入方式全景", [
        "不同类型的条件需要不同的注入机制。这是面试中展示系统性理解的好机会。",

        "| 条件类型 | 注入方式 | 原因 |",
        "|---------|---------|------|",
        "| **文本描述** | Cross-Attention (Q=图像, K/V=文本) | 语义级别，非空间对齐。图像每个位置自由关注任意词 |",
        "| **边缘/深度/姿态图** | **ControlNet** (特征逐层相加) | 空间对齐，像素级对应。左上角边缘 -> 左上角内容 |",
        "| **遮罩/参考图 (inpainting)** | Channel concatenation (通道拼接) | 直接空间输入，输入通道从 4 -> 9 |",
        "| **风格参考图** | **IP-Adapter** (额外 cross-attn 层) | 全局风格，不需空间对齐，与文本 cross-attn 并行 |",
        "| **放大文本效果** | **CFG** (推理策略) | 不改结构，只改采样 |",

        "### 为什么空间对齐的条件不用 Cross-Attention?",
        "Cross-Attention 的优势在于**灵活的、非对齐的关联** -- \"cat\" 可以影响图像任何位置。"
        "但对于边缘图这种**像素级一一对应**的条件，逐层特征相加比 attention 更直接、更精确。",
    ])

    # ===== Section 9: ControlNet =====
    b.add_section("9. ControlNet 的 Zero Convolution 设计哲学", [
        "### 架构",
        "```\n控制信号 (边缘图)\n      |\n"
        "UNet Encoder 副本 -> 特征 f\n"
        "      | (zero conv: 1x1卷积, 初始权重=0)\n"
        "原始 UNet <- 正常接收 z_t, t, text\n"
        "      |\n"
        "h_new = h + 0*f = h    <- 训练初始，完全不受影响\n```",

        "### 1x1 卷积是什么?",
        "本质是**逐像素的线性变换** -- 不看邻居像素，只在**通道维度**上做线性组合。"
        "用 1x1 卷积是因为空间信息已由 ControlNet 副本的正常卷积处理好了。",

        "### 为什么初始权重为 0?",
        "**核心问题:** 原始 UNet 是花巨大算力预训练好的。如果一上来就用随机权重往里加东西，"
        "等于往精密系统注入随机噪声 -- **预训练能力会被立刻破坏**。",
        "Zero conv 保证了:",
        "1. **训练第 0 步**: ControlNet 完全透明，原始 UNet 照常工作",
        "2. **训练逐步进行**: 权重从 0 **自然增长**，控制信号渐进式引入",
        "3. **训练结束**: 权重长到合适大小，ControlNet 有效施加空间控制",

        "### 权重增长是自动的，不是人为调度的",

        "| | Scheduled LR | Zero Conv |",
        "|---|---|---|",
        "| 谁控制变化 | 人为预设的 schedule | 梯度下降自动学习 |",
        "| 控制什么 | 所有参数的学习率 | 特定连接的权重值本身 |",
        "| 需要调参 | 需要选 schedule 和超参 | 不需要，初始化为 0 即可 |",
        "| 最终值 | LR 通常趋向 0 | 权重长到任务需要的大小 |",

        '**设计哲学:** "不破坏已有能力，渐进式引入新能力" -- 与 LoRA 的零初始化、residual connection 一脉相承。',
    ])

    # ===== Section 10: DDIM + SDE =====
    b.add_section("10. DDIM 与 SDE 统一框架", [
        "### DDIM: 确定性采样 + 跳步加速",
        "去掉 DDPM 采样中的随机噪声项，使采样变为**确定性**:",
        "```\nDDPM:  x_{t-1} = predicted_mean + sigma_t * z    (z 是随机噪声)\n"
        "DDIM:  x_{t-1} = predicted_mean + 0               (无随机项)\n```",
        "**同一个训好的 UNet，不用重新训练。**",

        "### 为什么确定性采样可以跳步?",
        "DDPM 逐步走是因为每步随机噪声需后续步骤处理，跳步积累误差。"
        "DDIM 没有随机噪声，本质是求解一个 **ODE**，可以用大步长:",
        "- DDPM: $t = 1000, 999, 998, \\ldots$ (1000步)",
        "- DDIM: $t = 1000, 800, 600, 400, 200, 0$ (5步)",
        "- 实践中 **20-50 步**即可接近 DDPM 质量，速度提升 20-50x",

        "### DDIM 的额外能力: Latent 插值",
        "确定性采样意味着**同一噪声输入永远生成同一张图**，latent 空间变得有意义:",
        FormulaBlock(
            latex=r"z_{\text{interp}} = (1-\lambda)\, z_A + \lambda\, z_B",
            explanation="对两个 latent 做线性插值后采样，得到平滑过渡。DDPM 的随机采样无法做到。",
        ),

        "### SDE 统一框架 (面试概念级)",
        "将扩散过程从离散推广到连续时间:",
        "- **前向 SDE**: $dx = f(x,t)\\,dt + g(t)\\,dw$ (加噪)",
        "- **反向 SDE**: $dx = [f(x,t) - g(t)^2 \\nabla_x \\log p_t(x)]\\,dt + g(t)\\,d\\bar{w}$ (去噪)",
        "其中 $\\nabla_x \\log p_t(x)$ 是 **Score Function** -- 指向数据密度增大的方向。",

        "### 三种方法的统一",

        "| 方法 | 在 SDE 框架中的角色 |",
        "|------|-------------------|",
        "| DDPM | 反向 SDE 的离散化，带随机项 |",
        "| DDIM | 反向 SDE 对应的 ODE (probability flow ODE) |",
        "| Score matching | 直接训练网络估计 score function |",

        "### $\\epsilon$-prediction 和 score function 的关系",
        FormulaBlock(
            latex=r"\nabla_x \log p_t(x) = -\frac{\epsilon_\theta(x_t, t)}{\sqrt{1-\bar{\alpha}_t}}",
            explanation="预测噪声就等价于估计 score function，只差一个和 alpha_bar_t 相关的缩放系数。",
        ),
    ])

    # ===== Self-check =====
    b.add_checklist("Self-Check Questions", [
        "画出 Stable Diffusion 的完整推理 pipeline (Text -> CLIP -> UNet -> VAE -> Image)",
        "写出 CFG 公式并解释 guidance scale w 的影响",
        "解释为什么在 latent space 做 diffusion 而不是 pixel space",
        "写出训练目标 (MSE loss) 并解释为什么预测噪声而不是直接预测 x_0",
        "解释方差守恒: 为什么采样公式的系数带根号？标准差 vs 方差的区别",
        "解释 beta_t 的角色: 它是训练的还是预设的？推理时会变吗？",
        "解释为什么 UNet 需要知道时间步 t，以及 sinusoidal embedding 的注入机制",
        "列出 5 种条件注入方式及其适用场景 (Cross-Attention, ControlNet, concat, IP-Adapter, CFG)",
        "解释 ControlNet 的 zero convolution 设计哲学",
        "用一句话描述 DDPM/DDIM/Score matching 在 SDE 框架下的统一关系",
    ])

    # ===== Quick Reference =====
    b.add_section("面试快速参考", [
        "### 完整知识链",
        "```\n1. 前向过程: x_t = sqrt(a_bar_t) * x_0 + sqrt(1-a_bar_t) * eps  (方差守恒)\n"
        "2. 反向过程: UNet 预测 eps, MSE loss 训练                          (极简目标)\n"
        "3. Latent Diffusion: VAE 压缩 -> latent 空间扩散 -> VAE 解码       (48x 压缩)\n"
        "4. 文本控制: CLIP 编码 -> Cross-Attention 注入 UNet                 (Q=图像, K/V=文本)\n"
        "5. CFG: 两次前向传播, 放大文本方向                                  (w=7.5 典型值)\n"
        "6. Noise Schedule: cosine 优于 linear                              (均匀信息销毁)\n"
        "7. 时间注入: sinusoidal -> MLP -> scale+shift 每个 ResBlock         (一个UNet全时间步)\n"
        "8. ControlNet: zero conv 渐进引入空间控制                          (不破坏预训练)\n"
        "9. DDIM: 确定性采样, 20-50步, 支持插值                             (ODE 视角)\n"
        "10. SDE 框架: 统一 DDPM/DDIM/Score matching                        (eps = -score)\n```",

        "### 设计哲学总结",
        "1. **方差守恒**: 加噪保持总能量不变，系数带根号是因为在标准差层面操作",
        "2. **预测噪声而非原图**: epsilon-prediction 方差更小、训练更稳定，等价于 score estimation",
        "3. **先定义行为再推参数**: cosine schedule 先设计 alpha_bar_t 形状，再反推 beta_t",
        "4. **不破坏已有能力**: zero conv / LoRA 零初始化，渐进式引入新能力",
        "5. **一个网络适配所有步**: 通过 sinusoidal embedding + scale/shift 让单一 UNet 处理全部时间步",
    ])

    return b


if __name__ == "__main__":
    import sqlite3

    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "mle_prep.db")
    builder = build_day1_chinese()
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

    # Save to DB (replace existing Day 1 doc)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM company_documents WHERE id=5")
    cur.execute(
        "INSERT INTO company_documents (company_id, title, content, source_type) VALUES (?, ?, ?, ?)",
        (23, "Adobe Prep Day1: Diffusion Models 深度指南", content, "manual"),
    )
    conn.commit()
    new_id = cur.lastrowid
    print(f"Saved as company_document id={new_id}")
    conn.close()
