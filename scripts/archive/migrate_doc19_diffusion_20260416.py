"""KG-M-01: Migrate Doc 19 Diffusion Models to canonical framework_node.

Doc 19 (Adobe MLE Prep All-in-One) contains a Diffusion Models 深度指南
(sections 1-10, 13-16) that the legacy 合集 audit flagged as SOLE SOURCE
in the corpus -- DDPM/DDIM, CFG, ControlNet, IP-Adapter, VAE, SDE/ODE
unification, score matching, ε vs x_0 vs v parameterization. None of
this lives in any framework_node or other doc. Per the KG migration
protocol we (a) lift the canonical concept tree to a NEW framework_node
under pillar6, (b) preserve the longer paper-style write-up as a
standalone doc, (c) plant a > **正典** pointer at the top of Doc 19's
diffusion section, (d) record the relationships in concept_links, and
(e) snapshot the pre-migration Doc 19 to archive/pre_kg/.

Deliverables (all idempotent, single sentinel guards re-run):
  1. archive/pre_kg/20260416/adobe_doc19_pre_diffusion_migration.md
     (full pre-migration Doc 19 content; written once).
  2. NEW framework_node at pillar6.diffusion_models (parent=6, depth=1)
     with a 10-12k char canonical_hub description covering DDPM forward
     /reverse, noise schedule, time conditioning, latent diffusion, CFG,
     conditioning panorama, ControlNet/IP-Adapter, DDPM-vs-DDIM, ε/x_0/v
     parameterization, VAE+reparameterization, SDE/ODE+score matching,
     UNet→DiT, interview pitfalls. Doc_kind marker = canonical_hub.
  3. docs/diffusion_models_canonical.md -- full paper-style deep dive
     (sections 1-10 + 13-16 from Doc 19, positional encoding/KV-cache
     stripped because they belong to other nodes).
  4. Doc 19 patched: a > **正典** [Diffusion Models](/framework/<id>)
     blockquote inserted directly under the # Diffusion Models heading.
  5. concept_links rows:
       framework_node:<new_id>  -- absorbed_from --> company_document:19
       framework_node:<new_id>  -- mentions      --> company_document:19
       company_document:19      -- canonical     --> framework_node:<new_id>

Sentinel: '<!-- KG_M_01_DIFFUSION_20260416 -->' in the framework_node's
description, the standalone doc, and the patched Doc 19 region. On
re-run, presence of the sentinel triggers [UNCHANGED] and skips writes.

Acceptance invariants enforced (rollback on violation):
  - canonical_node description length in [8000, 14000]
  - standalone doc length >= 18000 chars
  - Doc 19 still contains the sentinel and the 正典 blockquote
  - all 3 concept_links rows present
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "mle_prep.db"
ARCHIVE = ROOT / "archive" / "pre_kg" / "20260416" / "adobe_doc19_pre_diffusion_migration.md"
STANDALONE = ROOT / "docs" / "diffusion_models_canonical.md"

SENTINEL = "<!-- KG_M_01_DIFFUSION_20260416 -->"
DOC19_ID = 19
NODE_PATH = "pillar6.diffusion_models"
NODE_TITLE = "Diffusion Models (DDPM / DDIM / CFG / Score-Based)"
PILLAR6_ID = 6


# ---------------------------------------------------------------------------
# Canonical framework_node description (target ~10500 chars, in [8000, 14000])
# ---------------------------------------------------------------------------

NODE_DESCRIPTION = f"""<!-- doc_kind: canonical_hub -->
<!-- canonical_topic: diffusion_models -->
{SENTINEL}

# Diffusion Models 正典枢纽：DDPM / DDIM / CFG / Score-Based 统一视角

> **前置** [Position Encoding (pillar6.transformer.position_encoding)](/framework/143)
> **前置** [Self-Attention (pillar6.transformer.self_attention)](/framework/141)
> **前置** [Expectation & Variance (pillar7.probability_statistics)](/framework/167)

## Overview

**Diffusion Models（扩散模型）** 是一类把"生成"建模成"逐步去噪"的概率模型。前向过程把干净数据 $x_0$ 在 $T$ 步内加噪到近似纯高斯噪声 $x_T$，反向过程训练一个神经网络把噪声一步步去掉、还原数据分布。本节点是扩散家族的**正典枢纽**——它统一 **DDPM / DDIM / Score Matching / SDE / ODE** 五条主流叙述，定型 $\\epsilon$-prediction、Latent Diffusion、CFG、ControlNet 等核心机制，并指出 UNet → DiT 的架构演进趋势。完整的 paper 风格深推导见 [Diffusion Models Canonical Deep Dive](/docs/diffusion_models_canonical.md)；Adobe 面试视角的速记请见 [Adobe Doc 19](/companies/adobe/documents/19) 的 Day 1 章节。

## 1. Forward Process & Variance Preservation（方差守恒前向过程）

**单步加噪**：以预设噪声调度 $\\beta_t \\in (0,1)$ 控制每步注入的高斯噪声幅度：

$$q(x_t \\mid x_{{t-1}}) = \\mathcal{{N}}\\!\\bigl(x_t;\\; \\sqrt{{1-\\beta_t}}\\,x_{{t-1}},\\; \\beta_t \\mathbf{{I}}\\bigr)$$

**累积量**：$\\alpha_t = 1-\\beta_t$，$\\bar{{\\alpha}}_t = \\prod_{{s=1}}^{{t}} \\alpha_s$。借助高斯叠加性可一步跳到任意 $t$：

$$x_t = \\sqrt{{\\bar{{\\alpha}}_t}}\\, x_0 + \\sqrt{{1-\\bar{{\\alpha}}_t}}\\,\\epsilon,\\quad \\epsilon \\sim \\mathcal{{N}}(0, \\mathbf{{I}})$$

**方差守恒**：若 $\\mathrm{{Var}}(x_0)=1$，则 $\\mathrm{{Var}}(x_t) = \\bar{{\\alpha}}_t + (1-\\bar{{\\alpha}}_t) = 1$ 恒成立。系数带根号是因为它操作的是**标准差层面**——直接把 $\\bar{{\\alpha}}_t$ 当系数会得到 $\\bar{{\\alpha}}_t^2 + (1-\\bar{{\\alpha}}_t)^2 \\neq 1$，破坏分布形状。这是扩散模型最核心的代数不变量，所有后续推导都依赖它。

## 2. Noise Schedule（$\\beta_t$ 调度）

$\\beta_t$ 是**预设的超参数**，训练前固定，训练 / 推理共用同一套查找表。两种主流调度：

- **Linear** (DDPM 原版)：$\\beta_t$ 从 $10^{{-4}}$ 线性增至 $0.02$，$T=1000$。问题：后期 $\\bar{{\\alpha}}_t$ 骤降，信息突然消失。
- **Cosine** (Nichol & Dhariwal 2021)：先设计 $\\bar{{\\alpha}}_t$ 余弦曲线，再反推 $\\beta_t$。信息销毁更均匀，FID 显著改善——这是"先定义行为再推参数"的设计哲学典范。

所有时间相关量 $(\\beta_t, \\alpha_t, \\bar{{\\alpha}}_t, \\sigma_t^2)$ 都是 $t$ 的确定函数，预先算好存表。**网络唯一要学的**是 $\\epsilon_\\theta(x_t, t)$。

## 3. Time Conditioning（一个网络处理所有时间步）

UNet 必须知道当前 $t$，因为同样模糊的图可能是 $t=500$ 的猫也可能是 $t=200$ 的雾，不告诉网络 $t$ 它无法校准预测尺度。注入方式与 Transformer 位置编码同构：

$$\\text{{emb}}(t)_{{2i}} = \\sin\\!\\Bigl(\\frac{{t}}{{10000^{{2i/d}}}}\\Bigr),\\quad \\text{{emb}}(t)_{{2i+1}} = \\cos\\!\\Bigl(\\frac{{t}}{{10000^{{2i/d}}}}\\Bigr)$$

整数 $t$ → sinusoidal embedding → MLP → 在每个 ResBlock 中以 **scale + shift (AdaGN)** 调制特征：$h \\leftarrow \\gamma(t)\\cdot \\mathrm{{GroupNorm}}(h) + \\beta(t)$。这让单一 UNet 用同一组权重处理 $T=1000$ 个不同噪声水平的去噪任务。

## 4. Reverse Process & ε-Prediction（反向过程与噪声预测目标）

**简化训练目标**（DDPM 原始 ELBO 经 reweight 后退化为 MSE）：

$$\\mathcal{{L}} = \\mathbb{{E}}_{{t, x_0, \\epsilon}}\\!\\bigl[\\,\\|\\epsilon - \\epsilon_\\theta(x_t, t)\\|^2\\,\\bigr]$$

**为什么预测 $\\epsilon$ 而非 $x_0$**？目标方差恒定。$\\mathrm{{Var}}[\\epsilon]=\\mathbf{{I}}$ 在所有 $t$ 不变；$\\mathrm{{Var}}[x_0|x_t]=\\frac{{1-\\bar{{\\alpha}}_t}}{{\\bar{{\\alpha}}_t}}\\mathbf{{I}}$，在 $t \\to T$ 时**爆炸**——梯度 landscape 变得极不稳定。$\\epsilon$-prediction 还有一个等价性：

$$\\nabla_{{x_t}} \\log p_t(x_t) \\;=\\; -\\frac{{\\epsilon}}{{\\sqrt{{1-\\bar{{\\alpha}}_t}}}}\\;\\approx\\;-\\frac{{\\epsilon_\\theta(x_t,t)}}{{\\sqrt{{1-\\bar{{\\alpha}}_t}}}}$$

预测噪声 = 估计 **score function**（denoising score matching, Vincent 2011）。这是 DDPM、Score Matching、SDE 反向过程三者统一的代数证据。

**$v$-prediction**（Salimans & Ho 2022）：定义 $v_t = \\sqrt{{\\bar{{\\alpha}}_t}}\\,\\epsilon - \\sqrt{{1-\\bar{{\\alpha}}_t}}\\,x_0$；当 $t \\to 0$ 时 $v \\approx -x_0$（预测信号），$t \\to T$ 时 $v \\approx \\epsilon$（预测噪声），SNR 全程加权均匀。SD v2 / SDXL / Imagen Video 默认使用。

## 5. Sampling: DDPM vs DDIM（同一个网络，两种采样器）

**关键认知**：DDPM 与 DDIM **训练完全相同**——同一个 UNet、同一个 MSE loss。差异只在推理时的反向更新规则：

| 维度 | DDPM | DDIM |
| --- | --- | --- |
| 反向数学框架 | SDE（含 Langevin 噪声） | ODE（probability flow） |
| 采样公式 | $x_{{t-1}} = \\mu_\\theta + \\sigma_t\\,z,\\; z\\sim\\mathcal{{N}}(0,\\mathbf{{I}})$ | $x_{{t-1}} = \\mu_\\theta$（确定性） |
| 步数 | ~1000（必须小步） | 20-50（可大跨步） |
| 同一起点 | 每次生成不同图 | 永远同一张图 |
| Latent 插值 | 不支持 | 支持（轨迹光滑） |

**predicted mean** 的统一形式（两者共享）：

$$\\mu_\\theta(x_t,t) = \\frac{{1}}{{\\sqrt{{\\alpha_t}}}}\\!\\left(x_t - \\frac{{1-\\alpha_t}}{{\\sqrt{{1-\\bar{{\\alpha}}_t}}}}\\,\\epsilon_\\theta(x_t,t)\\right)$$

**为什么 DDIM 能去掉随机项？** DDPM 的训练目标只依赖**边际分布** $q(x_t|x_0)$，不依赖中间联合分布 $q(x_{{t-1}},x_t|x_0)$。DDIM 据此构造**非马尔可夫**反向过程：边际分布与 DDPM 完全一致，但反向方差为零。等价的轨迹、确定的路径，所以可以大跨步——有随机噪声时跳大步会累积偏移（"风中下山"），无随机噪声时光滑曲线随便跳（"晴天大步跨"）。DDIM 还提供 $\\eta\\in[0,1]$ 在两者间连续插值（$\\eta=0$ 纯 DDIM、$\\eta=1$ 退化 DDPM）。

## 6. Latent Diffusion / Stable Diffusion Pipeline

**核心创新**：直接在 512×512×3 ≈ 786k 维像素空间扩散计算量爆炸，**Stable Diffusion** 用预训练 VAE 把图像压到 64×64×4 = 16k 维 latent，在那里做扩散，再用 VAE decoder 上采样回像素。压缩比 $\\sim 48\\times$。

```
Text Prompt -> CLIP Text Encoder -> Cross-Attention -> UNet (iterative denoise) -> VAE Decoder -> Pixel Image
```

**Cross-Attention 注入文本**：UNet 每个 attention 层 $Q$ 来自 noisy latent（图像问"我这位置该长什么"），$K/V$ 来自 CLIP 文本 embedding（文本答"这里是猫的耳朵"）。每个图像位置可自由关注任意 token，实现非空间对齐的语义控制。

**关键数字（SD v1.5）**：512×512 像素、64×64×4 latent、VAE 8× 下采样、CLIP 77×768 text embedding、典型 20-50 步采样。

## 7. Classifier-Free Guidance (CFG)

**CFG** 是**推理时策略**（不改架构）。训练时以 ~10% 概率把条件 $c$ 替换为空 $\\varnothing$，让同一个 UNet 同时学到 conditional 与 unconditional 预测。推理放大条件方向：

$$\\hat{{\\epsilon}} = \\epsilon_\\theta(x_t, \\varnothing) + w\\cdot\\bigl(\\epsilon_\\theta(x_t, c) - \\epsilon_\\theta(x_t, \\varnothing)\\bigr)$$

**guidance scale $w$**：$w=1$ 退化为标准条件生成；$w=7.5$（SD v1 典型）增强 prompt 遵循度但多样性下降；$w$ 过大产生过饱和 artifacts。**代价**：每步两次前向（条件 + 无条件），推理成本 $2\\times$。

## 8. Conditioning Injection Panorama（条件注入全景）

| 条件类型 | 注入方式 | 几何 / 语义性质 |
| --- | --- | --- |
| 文本描述 | Cross-Attention（Q=图像, K/V=文本） | 全局语义、非空间对齐 |
| 边缘 / 深度 / 姿态 | **ControlNet**（特征逐层相加） | 像素级空间对齐 |
| 遮罩 / 参考图 (inpainting) | Channel concatenation | 直接空间输入，输入通道 4→9 |
| 风格参考图 | **IP-Adapter**（独立 cross-attn） | 全局风格、与文本并行 |
| 文本强度放大 | **CFG**（推理策略） | 不改结构、改采样 |

**为什么空间对齐条件不用 cross-attention？** Cross-attention 的全局感受野会把"左上角的边缘"扩散到全图。逐层特征相加（ControlNet）保留像素级精确对应。

## 9. ControlNet：Zero Convolution 设计哲学

**架构**：(1) 冻结预训练 UNet（locked copy）；(2) 克隆 encoder blocks 作为 trainable copy；(3) 两者用 1×1 **zero convolution**（权重和偏置初始化为 0）连接；trainable copy 输出经 zero conv 后**加到** locked copy 对应层。

**Zero conv 的意义**：训练第 0 步输出恒为 0 → 等于没加任何条件 → 完全保留预训练能力；训练逐步进行，权重从 0 **由梯度自动增长**——不需要人为 schedule，不会因随机初始化梯度灾难性遗忘。这是"不破坏已有能力，渐进式引入新能力"的范式（与 LoRA 零初始化、residual connection 一脉相承）。

**训练成本**：单条件类型约 600 GPU-hours (8×A100)，远低于从头训练 SD 的 $\\sim 150{{,}}000$ GPU-hours——核心价值是**0.4% 成本撬动 100% 能力扩展**。

**多 ControlNet 组合**：$\\text{{output}} = \\text{{UNet}}(x_t) + \\sum_i w_i\\cdot\\text{{ControlNet}}_i(x_t, c_i)$；$\\sum w_i \\in [1.0, 1.5]$ 常用，互补条件（pose+depth）效果好，冗余条件（双 edge）易冲突。

## 10. IP-Adapter：图像作为 Prompt

IP-Adapter (Image Prompt Adapter) 注入 CLIP 图像特征作为风格 / 内容参考。**关键创新**：**decoupled cross-attention**——不与文本共享 K/V，而是在每层新增独立的 $K_i, V_i$ 投影：

$$\\text{{output}} = \\text{{Attn}}(Q, K_t, V_t) + \\lambda\\cdot \\text{{Attn}}(Q, K_i, V_i)$$

文本与图像各占独立"通道"，互不干扰。训练参数仅 ~22M，远小于 ControlNet 的 ~361M。

## 11. SDE / ODE 统一框架

将离散扩散推广到连续时间：

- **前向 SDE**：$dx = f(x,t)\\,dt + g(t)\\,dw$
- **反向 SDE**：$dx = [f(x,t) - g(t)^2 \\nabla_x \\log p_t(x)]\\,dt + g(t)\\,d\\bar{{w}}$
- **Probability Flow ODE**：$dx = [f(x,t) - \\tfrac{{1}}{{2}} g(t)^2 \\nabla_x \\log p_t(x)]\\,dt$（去随机项）

| 方法 | SDE 框架角色 |
| --- | --- |
| DDPM 采样 | 反向 SDE 的离散化（带 Langevin 噪声） |
| DDIM 采样 | 反向 ODE 的数值解（无噪声） |
| Score Matching | 直接训练网络估计 $\\nabla_x \\log p_t(x)$ |

**统一一句话**：DDPM 定义过程，Score Matching 提供训练目标，SDE/ODE 提供采样器选择——三者殊途同归。

## 12. VAE：Stable Diffusion 的潜在空间引擎

**ELBO loss** 由两部分组成：

$$\\mathcal{{L}}_{{\\text{{VAE}}}} = \\underbrace{{\\mathbb{{E}}_{{q_\\phi(z|x)}}[-\\log p_\\theta(x|z)]}}_{{\\text{{Reconstruction}}}} + \\underbrace{{D_{{\\mathrm{{KL}}}}\\!\\bigl(q_\\phi(z|x)\\,\\Vert\\,\\mathcal{{N}}(0,\\mathbf{{I}})\\bigr)}}_{{\\text{{KL Regularization}}}}$$

**KL 正则化**强制 latent 分布接近标准高斯——保证 latent 空间**连续**（相近 $z$ → 相似图）和**完整**（任意采样 $z$ 都能解码）。

**重参数化技巧（Reparameterization Trick）**：从 $z\\sim\\mathcal{{N}}(\\mu,\\sigma^2)$ 采样不可微，无法反传。改写为 $z = \\mu + \\sigma\\odot\\epsilon$，$\\epsilon\\sim\\mathcal{{N}}(0,\\mathbf{{I}})$——把随机性外置，$z$ 对 $\\mu,\\sigma$ 都可微。这是所有 VAE 变体（含 SD 的潜在空间 VAE）能端到端训练的关键。

**$\\beta$-VAE**：$\\mathcal{{L}} = \\text{{Recon}} + \\beta\\cdot D_{{\\mathrm{{KL}}}}$。SD 用极小的 KL 权重（$\\sim 10^{{-6}}$），因为 latent 空间的"平滑性"由扩散模型本身保证，VAE 专注高质量重建。

**VAE vs VQ-VAE**：VAE 用连续 latent + KL 正则；VQ-VAE 用离散 codebook（K 个 entry）+ commitment loss + EMA codebook update + straight-through estimator。SD 用 VAE，DALL-E v1 用 VQ-VAE。

## 13. UNet → DiT 架构演进

**UNet 时代 (2020-2023)**：DDPM、SD 1.x/2.x、SDXL 都用 UNet。UNet 的 skip connections 天然适合"先破坏再恢复"的扩散过程，但 attention 层占比少、scaling 受限。

**DiT 时代 (2023-)**：Peebles & Xie (2023) 的 **Diffusion Transformer (DiT)** 用纯 Transformer 替代 UNet：图像 patch 化（类似 ViT）后过 transformer blocks，时间步与类别条件通过 **AdaLN** 注入。优势：(1) scaling law 更好（参数翻倍质量持续提升）；(2) 与 LLM 共享 GPU kernel 与推理优化；(3) 多模态统一（patch、token、frame 都是 token）。SD3 的 MMDiT、Flux、推测中的 DALL-E 3 都采用 DiT。

类比：CNN→ViT 是视觉的 transformer 化，UNet→DiT 是扩散的 transformer 化。

## Interview Pitfalls（常见误区）

- **"DDPM 与 DDIM 是不同模型"** —— 错。同一个 UNet、同一套训练，差异只在采样规则。
- **"加噪公式系数不带根号也行"** —— 错。带根号是因为操作的是标准差；不带根号会破坏方差守恒。
- **"$\\beta_t$ 是网络学的"** —— 错。$\\beta_t$ 是预设超参数，存查找表，训练 / 推理共用。
- **"$x_0$-prediction 等价于 $\\epsilon$-prediction"** —— 数学可互转，但目标方差不同：$x_0$ 在 $t\\to T$ 时方差爆炸，训练不稳定。
- **"CFG 只是后处理 trick"** —— CFG 需要训练时随机丢弃条件，与采样规则配对，不是单纯 inference trick。
- **"ControlNet 用随机初始化即可，0 初始化只是细节"** —— 错。Zero conv 是核心：随机初始化会在第一步破坏预训练 UNet；零初始化保证渐进式引入。
- **"DDIM 凭推理修改就能跳步是 free lunch"** —— 不完全。跳步质量上限取决于 $\\epsilon_\\theta$ 在大噪声水平的预测准确度；一般 20 步以下质量明显下降。
- **"Stable Diffusion 在像素空间扩散"** —— 错。SD 是 **Latent** Diffusion，像素 ↔ latent 由 VAE 完成。
- **"IP-Adapter 把图像 token 拼到文本 token 上"** —— 错。IP-Adapter 用 **decoupled cross-attention**，文本与图像各有独立的 K/V 投影。
- **"扩散模型只能生成图像"** —— 不对。Audio (DiffWave)、video (Stable Video Diffusion / Sora)、3D (DreamFusion)、protein (RFdiffusion) 都已应用扩散框架。

## Components（统摄的周边节点 / 文档）

- [Position Encoding (pillar6.transformer.position_encoding)](/framework/143) -- sinusoidal embedding 与 RoPE 的来源；本节点的 time embedding 与之同源。
- [Self-Attention (pillar6.transformer.self_attention)](/framework/141) -- Cross-Attention 的语义对齐机制依赖 self-attention 基础。
- [Vision-Language Models (pillar6.multimodal.vision_language)](/framework/164) -- CLIP / LLaVA 是文本条件注入的上游。
- [Generative AI Systems Design (pillar3.design_problems.genai)](/framework/97) -- 扩散模型在 ML system design 中的部署视角。
- [Adobe MLE Prep Day 1: Diffusion 深度指南 (Doc 19)](/companies/adobe/documents/19) -- 面试速记口吻、扩展实例与 Self-Check QA。
- [Diffusion Models Canonical Deep Dive](/docs/diffusion_models_canonical.md) -- 标准化的 paper 风格深推导（独立长文）。

## Key Takeaways

- **方差守恒**是扩散模型最核心的代数不变量；系数带根号是因为操作标准差。
- **$\\epsilon$-prediction = score matching**，统一了 DDPM、Score Matching、SDE 三套语言。
- **DDPM ≡ DDIM (训练)，DDPM ≠ DDIM (采样)**：同一个 UNet，SDE vs ODE 两条路径。
- **CFG**：训练时随机丢条件 + 推理时放大方向，$2\\times$ 算力换 prompt 遵循度。
- **Latent Diffusion** = "VAE 压缩 + 扩散 + VAE 解码"，48× 压缩让消费级 GPU 跑通 SD。
- **ControlNet 的核心是 zero conv**——零初始化才能不破坏预训练，权重靠梯度自然增长。
- **$v$-prediction** 让目标方差全程均匀；SD v2 / SDXL 默认。
- **UNet → DiT** 是扩散家族继承 LLM scaling law 的关键架构演进。

> **后续** [Vision-Language Models](/framework/164)
> **后续** [Generative AI Systems Design](/framework/97)
"""

NODE_DESCRIPTION = NODE_DESCRIPTION.rstrip() + "\n"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_doc19_content(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id=?", (DOC19_ID,)
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Doc {DOC19_ID} not found in DB")
    return row[0]


def _archive_pre_migration(current_content: str) -> tuple[str, str]:
    """Write the archive snapshot exactly once.

    The archive must capture the **pre-migration** state, so we never
    overwrite an existing file -- on the first run we snapshot whatever is
    currently in the DB (which is by definition pre-migration), and on every
    subsequent run we read the immutable snapshot back. Returns
    `(snapshot_content, status)` so callers can build derived artefacts from
    the truly-pre-migration text instead of a partially-patched DB row.
    """
    if ARCHIVE.exists():
        return ARCHIVE.read_text(encoding="utf-8"), "unchanged"
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_text(current_content, encoding="utf-8")
    return current_content, "written"


# Diffusion segment boundaries on the pre-migration Doc 19. We anchor on the
# explicit start- and end-H1 strings so the extraction survives offset drift
# and skips spurious `# comment` lines that appear inside code blocks (the
# diffusion section embeds a Python pseudocode block whose first line
# `# DDPM 采样伪代码` would otherwise be mis-detected as an H1 terminator).
DIFFUSION_H1 = "# Diffusion Models 深度指南 (Adobe Prep Day 1)"
DIFFUSION_END_H1 = "# RLHF / DPO Alignment + LLM Distillation"


def _build_standalone_deepdive(pre_migration_doc19: str) -> str:
    """Extract diffusion-specific sections from the pre-migration Doc 19.

    The diffusion segment spans from `# Diffusion Models 深度指南` up to (but
    excluding) `# RLHF / DPO Alignment + LLM Distillation`. Inside that
    segment, sections 11 (Positional Embedding) and 12 (KV-Cache) are
    mis-filed transformer / LLM-inference content -- they belong to nodes
    143 and 156 respectively, not to the diffusion canonical hub. The deep
    dive doc therefore preserves sections 1-10 plus 13-16, joined into a
    single paper-style document with a sentinel header.

    The input MUST be the pre-migration Doc 19 (read from the archive
    snapshot), not the patched live DB row -- otherwise the inserted
    `> **正典**` pointer block ends up duplicated in the deep-dive.
    """
    h1_start = pre_migration_doc19.find(DIFFUSION_H1)
    if h1_start < 0:
        raise RuntimeError(f"Pre-migration Doc 19 missing H1: {DIFFUSION_H1!r}")
    h1_end = pre_migration_doc19.find(DIFFUSION_END_H1, h1_start + len(DIFFUSION_H1))
    if h1_end < 0:
        raise RuntimeError(f"Pre-migration Doc 19 missing end H1: {DIFFUSION_END_H1!r}")
    diffusion_segment = pre_migration_doc19[h1_start:h1_end]

    # Identify each `## N.` section header position.
    section_re = re.compile(
        r"^## (\d+)\.\s+(.+)$", re.MULTILINE
    )
    matches = list(section_re.finditer(diffusion_segment))
    if not matches:
        raise RuntimeError("No section headings found in Doc 19 diffusion segment")

    # Group by section number; section 11 = Positional Embedding, 12 = KV-Cache
    # both excluded. Section 12 appears twice in Doc 19 (a continuation block);
    # we drop both. Sections 1-10 + 13-16 retained.
    EXCLUDED = {11, 12}
    keep_spans: list[tuple[int, int]] = []
    for idx, m in enumerate(matches):
        sec_num = int(m.group(1))
        if sec_num in EXCLUDED:
            continue
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(diffusion_segment)
        keep_spans.append((start, end))

    # Preamble: from offset 0 of segment up to first `## 1.` heading
    first_h2 = matches[0].start()
    preamble = diffusion_segment[:first_h2]

    body_parts = [diffusion_segment[s:e] for s, e in keep_spans]
    body = "".join(body_parts)

    header = (
        f"{SENTINEL}\n\n"
        "# Diffusion Models — Canonical Deep Dive\n\n"
        f"> **正典节点** [Diffusion Models ({NODE_PATH})](/framework/<NODE_ID>)\n\n"
        "> 本文是 KG-M-01 迁移自 Adobe Doc 19 的 paper 风格深推导，**与正典节点共生**。"
        "结构对应：节点给出 12-section 概览与 interview pitfalls；本文给出从 DDPM 到 IP-Adapter 的完整章节式深推导。"
        "Sections 11 (Positional Embedding) 与 12 (KV-Cache) 为 Doc 19 误归类的 transformer / LLM-inference 内容，"
        "已分别由 [Position Encoding](/framework/143) 与 [KV Cache](/framework/156) 节点承载，故此处剔除。\n\n---\n\n"
    )
    standalone = header + preamble + body
    return standalone.rstrip() + "\n"


def _write_standalone(content: str) -> str:
    if STANDALONE.exists() and STANDALONE.read_text(encoding="utf-8") == content:
        return "unchanged"
    STANDALONE.parent.mkdir(parents=True, exist_ok=True)
    STANDALONE.write_text(content, encoding="utf-8")
    return "written"


def _upsert_node(conn: sqlite3.Connection) -> tuple[int, str]:
    existing = conn.execute(
        "SELECT id, description FROM framework_nodes WHERE path=?",
        (NODE_PATH,),
    ).fetchone()
    if existing:
        node_id, current_desc = existing
        if (current_desc or "") == NODE_DESCRIPTION:
            return node_id, "unchanged"
        conn.execute(
            "UPDATE framework_nodes SET description=?, title=? WHERE id=?",
            (NODE_DESCRIPTION, NODE_TITLE, node_id),
        )
        return node_id, "updated"
    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description, importance, priority, status, progress_pct)
        VALUES (?, ?, 1, ?, ?, 0.95, 'P0', 'not_started', 0.0)
        """,
        (PILLAR6_ID, NODE_PATH, NODE_TITLE, NODE_DESCRIPTION),
    )
    return cur.lastrowid, "inserted"


def _patch_doc19(conn: sqlite3.Connection, original: str, node_id: int) -> tuple[str, str]:
    """Insert the > **正典** pointer + sentinel directly under the diffusion H1.

    The patch is placed once, immediately after the `# Diffusion Models 深度指南`
    line and before the existing `## Prerequisites` section. Re-runs detect the
    sentinel and skip; otherwise it splices the pointer block in.
    """
    if SENTINEL in original:
        return original, "unchanged"

    pointer_block = (
        f"\n{SENTINEL}\n"
        f"> **正典** [Diffusion Models ({NODE_PATH})](/framework/{node_id})\n"
        f"> 本节为 Adobe 面试视角的速记 / 扩展实例与 Self-Check。完整概念树与 paper 风格深推导见正典节点与 [docs/diffusion_models_canonical.md](/docs/diffusion_models_canonical.md)。\n"
    )
    target = "# Diffusion Models 深度指南 (Adobe Prep Day 1)"
    if target not in original:
        raise RuntimeError(
            f"Doc 19 missing expected heading: {target!r}; cannot place 正典 pointer"
        )
    new_content = original.replace(target, target + pointer_block, 1)
    conn.execute(
        "UPDATE company_documents SET content=? WHERE id=?",
        (new_content, DOC19_ID),
    )
    return new_content, "patched"


def _insert_concept_links(conn: sqlite3.Connection, node_id: int) -> tuple[int, int]:
    """Insert the three concept_links rows idempotently."""
    rows = [
        ("framework_node", node_id, "company_document", DOC19_ID,
         "absorbed_from",
         "Adobe Doc 19 Diffusion section is sole-source; canonical migrated to node (KG-M-01)"),
        ("framework_node", node_id, "company_document", DOC19_ID,
         "mentions",
         "Adobe Doc 19 retains the diffusion speed-write under the 正典 pointer (KG-M-01)"),
        ("company_document", DOC19_ID, "framework_node", node_id,
         "canonical",
         "Adobe Doc 19 diffusion section defers to the canonical hub (KG-M-01)"),
    ]
    inserted = skipped = 0
    for src_kind, src_id, dst_kind, dst_id, relation, note in rows:
        existing = conn.execute(
            "SELECT 1 FROM concept_links WHERE src_kind=? AND src_id=? "
            "AND dst_kind=? AND dst_id=? AND relation=?",
            (src_kind, src_id, dst_kind, dst_id, relation),
        ).fetchone()
        if existing:
            skipped += 1
            continue
        conn.execute(
            "INSERT INTO concept_links "
            "(src_kind, src_id, dst_kind, dst_id, relation, weight, note) "
            "VALUES (?, ?, ?, ?, ?, 1.0, ?)",
            (src_kind, src_id, dst_kind, dst_id, relation, note),
        )
        inserted += 1
    return inserted, skipped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not DB.exists():
        print(f"[FAIL] DB not found: {DB}")
        return 2

    conn = sqlite3.connect(str(DB))
    try:
        current_doc19 = _load_doc19_content(conn)

        # Step 1: archive snapshot. Captures pre-migration state on first run;
        # on re-runs it reads the immutable snapshot back, ensuring derived
        # artefacts (Step 3) build from genuinely pre-migration text rather
        # than from a partially-patched DB row.
        pre_migration_doc19, archive_status = _archive_pre_migration(current_doc19)

        # Step 2: framework_node upsert. Doing this first so the standalone
        # doc and Doc 19 patch can reference the assigned id.
        node_id, node_status = _upsert_node(conn)

        # Step 3: standalone deep-dive doc. Always built from the
        # pre-migration archive so the sentinel-guarded pointer block does
        # not leak into the extracted segment on re-runs.
        deepdive = _build_standalone_deepdive(pre_migration_doc19).replace(
            "<NODE_ID>", str(node_id)
        )
        deepdive_status = _write_standalone(deepdive)

        # Step 4: patch Doc 19 with 正典 pointer + sentinel.
        patched_doc19, patch_status = _patch_doc19(conn, current_doc19, node_id)

        # Step 5: concept_links.
        inserted, skipped = _insert_concept_links(conn, node_id)

        # Acceptance invariants ------------------------------------------------
        node_len = conn.execute(
            "SELECT length(description) FROM framework_nodes WHERE id=?",
            (node_id,),
        ).fetchone()[0]
        deepdive_len = len(deepdive)
        problems: list[str] = []
        if not (8000 <= node_len <= 14000):
            problems.append(
                f"node {node_id} description length {node_len} outside [8000, 14000]"
            )
        if deepdive_len < 18000:
            problems.append(
                f"standalone deep dive length {deepdive_len} < 18000 chars"
            )
        if SENTINEL not in patched_doc19:
            problems.append("Doc 19 missing sentinel after patch")
        link_count = conn.execute(
            "SELECT COUNT(*) FROM concept_links WHERE "
            "(src_kind='framework_node' AND src_id=? AND dst_kind='company_document' AND dst_id=?) OR "
            "(src_kind='company_document' AND src_id=? AND dst_kind='framework_node' AND dst_id=?)",
            (node_id, DOC19_ID, DOC19_ID, node_id),
        ).fetchone()[0]
        if link_count < 3:
            problems.append(f"expected >=3 concept_links rows, found {link_count}")

        if problems:
            conn.rollback()
            print("[FAIL] invariants violated (transaction rolled back):")
            for p in problems:
                print(f"  - {p}")
            return 1
        conn.commit()
    finally:
        conn.close()

    tag = {
        "inserted": "[INSERTED]",
        "updated":  "[UPDATED] ",
        "unchanged": "[UNCHANGED]",
        "patched":  "[PATCHED] ",
        "written":  "[WRITTEN] ",
    }
    print(f"{tag.get(node_status, node_status)} framework_node id={node_id} "
          f"path={NODE_PATH} length={node_len}")
    print(f"{tag.get(deepdive_status, deepdive_status)} {STANDALONE.relative_to(ROOT)} "
          f"length={deepdive_len}")
    print(f"{tag.get(archive_status, archive_status)} {ARCHIVE.relative_to(ROOT)}")
    print(f"{tag.get(patch_status, patch_status)} company_document id={DOC19_ID} (Doc 19)")
    print(f"[LINKS] inserted={inserted} skipped={skipped} (total={link_count})")
    print("[DONE] KG-M-01 diffusion canonical migration complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
