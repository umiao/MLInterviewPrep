"""T-P1-453: CNN Foundation 1-Pager for Pinterest Visual Search.

Seeds one Pinterest company_document (doc_kind=prep_note) titled
"CNN Foundation for Visual Search" covering:
  (1) Conv op mechanics: stride/pad/dilation, receptive field, parameter sharing
  (2) Pooling: max vs avg, Global Average Pool replacing FC
  (3) Architectures one-liner: VGG / ResNet / EfficientNet (pyramid mid --
      explicitly defers NAS / ViT internals to separate tasks)
  (4) Transfer learning: head-only vs full fine-tune, when to freeze backbone,
      BN quirks when fine-tuning
  (5) Augmentation catalog: geometric / color / Mixup / CutMix / Cutout +
      text-image pair aug for multimodal (Pinterest relevance)

Also appends a Pinterest-specific-angle section to framework_node id=122
(Image Classification) via surgical patch -- preserves existing generic CV
content, points readers at the canonical doc for Pinterest-specific
composition.

Idempotent: safe to re-run. Company doc is upserted by (company_id, title);
node 122 patch checks whether the marker section already exists.

Usage::

    python scripts/seed_pinterest_cnn_foundation_20260416.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"

PINTEREST_COMPANY_ID = 29
DOC_TITLE = "CNN Foundation for Visual Search"
NODE_122_ID = 122
NODE_122_PATCH_MARKER = "### Pinterest Visual-Search Angle"


# ==========================================================================
# Doc content: CNN Foundation for Visual Search (Pinterest angle)
# ==========================================================================

def build_cnn_foundation_doc() -> str:
    b = StudyNoteBuilder()
    b.set_title("CNN Foundation for Visual Search (Pinterest-angled 1-Pager)")

    b.add_prerequisites([
        "线性代数：矩阵乘法、卷积作为稀疏线性算子",
        "基础梯度下降 + 反向传播链式法则",
        "Numpy 张量形状直觉：(N, C, H, W) / (N, H, W, C) 两种约定",
        "基本概率：Gaussian noise、Bernoulli dropout、Beta 分布（Mixup 采样）",
    ])

    b.add_term("CNN", "Convolutional Neural Network",
        "参数共享 + 局部连接的平移等变特征提取器；图像任务默认骨干")
    b.add_term("RF", "Receptive Field",
        "某层某位置激活依赖的输入区域；判断\"看到了多大上下文\"的核心量")
    b.add_term("GAP", "Global Average Pooling",
        "对 feature map 每通道取空间平均；替代 FC 层，参数量骤减 + 正则化效果")
    b.add_term("BN", "Batch Normalization",
        "按 mini-batch 统计归一化激活；训练时用 batch stats，推理用 running stats")
    b.add_term("TL", "Transfer Learning",
        "借用预训练骨干特征；在视觉任务中几乎总是默认策略（除非数据 > 千万级）")
    b.add_term("ResNet", "Residual Network (He et al. 2015)",
        "跳跃连接让梯度绕过非线性块；把\"深度训得起来\"从瓶颈变成非问题")
    b.add_term("VGG", "Visual Geometry Group Net (Simonyan & Zisserman 2014)",
        "全用 3x3 卷积堆叠 + 2x2 max pool；结构极简，参数巨多（~138M）")
    b.add_term("EfficientNet", "Compound Scaling Network (Tan & Le 2019)",
        "复合缩放 depth/width/resolution 三维度，用 NAS 搜基础结构 + 手工缩放规则")
    b.add_term("Mixup", "Linear Interpolation Augmentation",
        "对两张图像做像素线性插值，标签同步插值；正则 + calibration 改善")
    b.add_term("CutMix", "Region-Replacement Augmentation",
        "把一张图的矩形区域粘到另一张上，标签按面积比例加权；保留空间结构")
    b.add_term("Cutout", "Random Rectangle Masking",
        "遮挡图像的随机矩形区域（填 0 或噪声）；简单正则，防过拟合局部特征")

    # ----------------------------------------------------------------------
    b.add_section("1. Conv Op Mechanics (stride / pad / dilation / RF)", [
        (
            "**卷积 = 局部加权求和 + 参数共享**。相比全连接，空间位置共享同一滤波器，"
            "参数量不随输入分辨率爆炸——这是 CNN 能扩展到 224x224 甚至 640x640 的根本。"
        ),
        FormulaBlock(
            latex=(
                r"H_{\text{out}} = "
                r"\left\lfloor \frac{H + 2p - d(k-1) - 1}{s} \right\rfloor + 1"
            ),
            explanation=(
                "**通用输出尺寸公式**（含 **Dilation（扩张率）** `d`）：stride `s`、"
                "padding `p`、kernel `k`、dilation `d`。`d=1` 退化为常见公式 "
                r"`(H + 2p - k)/s + 1`。面试必背。"
            ),
        ),
        (
            "**参数量**（单层）：`C_out * (C_in * k * k + 1)`，其中 `+1` 是 bias。"
            "举例：`3x3 conv, C_in=64, C_out=128` => `128 * (64*9 + 1) = 73,856` 个参数。"
        ),
        (
            "**感受野（RF）递推**：第 `l` 层 RF 等于上一层 RF 加上 `(k_l - 1) * ∏_{i<l} s_i`——"
            "stride 叠乘是关键，每 stride=2 之后新层的每 pixel 跨度翻倍。"
            "ResNet-50 的 stage4 末端 RF 已经覆盖输入 >1/2，足以做 object-level 判别。"
            "**Dilation** 是在不降分辨率时增 RF 的手段（空洞卷积，分割/检测常用）。"
        ),
        (
            "**1x1 conv 的三重身份**：(a) **通道投影**（linear mix across channels），"
            "(b) **参数量瓶颈**（ResNet bottleneck 先 1x1 降维再 3x3 再 1x1 升回），"
            "(c) **全卷积化的 FC 层**（做 dense prediction 时保留空间维）。"
        ),
        (
            "**Depthwise Separable Conv**（MobileNet / EfficientNet 核心）：先做 depthwise "
            "(每通道独立 kxk) 再 1x1 pointwise——参数量从 `C_in*C_out*k^2` 降到 "
            "`C_in*k^2 + C_in*C_out`，移动端推理的标配。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_section("2. Pooling: Max vs Avg, GAP Replacing FC", [
        (
            "**Max pool**：保留局部最强响应，对小位移鲁棒；**Avg pool**：平滑激活，"
            "保留整体能量。早期 CNN 用 max pool 降采样，现代架构（ResNet 后）"
            "多用 `stride=2 conv` 替代 pool——可学习的降采样更灵活。"
        ),
        (
            "**Global Average Pooling (GAP)**：对最后 feature map 每通道求空间平均 -> "
            "得到一个 `C` 维向量，直接接 softmax（或线性头）。对比传统 `Flatten + FC`："
            "\n  - **参数量**：VGG-16 的三个 FC 占总参数 ~90%；GAP 把这部分砍到 0；"
            "\n  - **正则化**：GAP 天然 translation-invariant，防过拟合；"
            "\n  - **可解释性**：每个通道的空间平均 = 该 class 的 spatial score map（CAM 基础）。"
            "\n 现代架构（ResNet 以降）默认 `GAP + Linear`，几乎不再用 `Flatten + FC`。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_comparison_table(
        headers=["架构", "年", "核心创新一句话", "参数量", "ImageNet Top-1"],
        rows=[
            ["**VGG-16**", "2014", "堆深 3x3 卷积 + 2x2 pool；结构极简", "~138M", "74.4%"],
            ["**ResNet-50**", "2015", "跳跃连接让梯度绕过非线性块，深度不再是瓶颈", "~25.5M", "76.1%"],
            ["**EfficientNet-B0**", "2019", "复合缩放 depth/width/resolution + NAS 基础块", "~5.3M", "77.1%"],
            ["**EfficientNet-B7**", "2019", "B0 基础块 + 复合缩放到 B7 规模", "~66M", "84.3%"],
        ],
        title="3. Architectures One-Liner (pyramid mid; NAS / ViT internals 见单独节点)",
    )
    # Extra text after the table (need to add as raw section since comparison
    # table is added as __table__):
    b.add_section("3.1 Architecture Notes (compact)", [
        (
            "- **VGG**：极简、全 3x3、无 BN（原版），参数巨多 -> 用作\"感知损失\"的"
            "特征提取器仍非常常见（样式迁移、GAN 评估）。"
        ),
        FormulaBlock(
            latex=r"\mathbf{y} = \mathcal{F}(\mathbf{x}, \{W_i\}) + \mathbf{x}",
            explanation=(
                "- **ResNet 残差块**：学习残差 `F(x)` 再加回 `x`。梯度反向时"
                "跳跃连接给梯度一条无非线性衰减的\"直通路\"，解决超深网络的 "
                "**Vanishing Gradient（梯度消失）**；BN 协同解决 "
                "**internal covariate shift**。这是 >150 层能训的核心原因。"
            ),
        ),
        (
            "- **EfficientNet**：用 NAS 搜出基础块（MBConv：depthwise separable + "
            "squeeze-excitation），再用**复合缩放规则**同步放大三维度："
            r"`depth = alpha^phi, width = beta^phi, resolution = gamma^phi`，"
            "`alpha*beta^2*gamma^2 ≈ 2`，单缩放维度的帕累托前沿。"
            "Pinterest 视觉塔（PinSage / Pinnability 视觉特征）的落地选型"
            "常用 EfficientNet 或 ResNet-50 的蒸馏版——精度/成本权衡好。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_section("4. Transfer Learning: Head-Only vs Full Fine-Tune", [
        (
            "**默认决策树**（Pinterest 视觉任务实战约 90% 走这条）：\n"
            "  1. **数据少 (<10k per class)** + 目标域接近 ImageNet（自然图像、商品图）"
            "=> **head-only**：冻结骨干，只训 classifier 头；几分钟收敛，不易过拟合。\n"
            "  2. **数据中等 (10k~100k)** + 域有偏移（Pin 风格、食物特写）=> "
            "**Full fine-tune + 判别性学习率**：顶层用 `lr_base`、底层用 `lr_base * 0.1~0.01`，"
            "防止破坏低层通用特征。\n"
            "  3. **数据极多 (>1M) 或强烈风格（医学、卫星）** => **从零训或 SSL 预训练** + "
            "full fine-tune。"
        ),
        (
            "**Progressive Unfreezing（渐进解冻）**：先 head-only 收敛 -> 再解冻顶两 stage -> "
            "再全解冻；每步用更小 lr。学界标准做法（fast.ai 倡导），防 "
            "**catastrophic forgetting（灾难性遗忘）**。"
        ),
        (
            "**BN 在微调时的坑（必考点）**：\n"
            "  - **坑 1**：直接 full fine-tune 小 batch 时，BN 的 batch stats 不稳，"
            "性能反而劣化。**解法**：微调阶段把 BN 设 `eval()` / `track_running_stats=False`，"
            "仍用预训练的 running mean/var，只学 `gamma/beta`。\n"
            "  - **坑 2**：domain gap 大时，running stats 完全错。**解法**：短暂重新估计"
            "（几百 step 只前向、只更新 BN stats），再正常训练。\n"
            "  - **坑 3**：混合精度训练 + BN 在早期 step 会 NaN。**解法**：BN 统计量用 fp32 累加。\n"
            "  **面试要点**：被问微调时务必主动提 BN 处理，否则被视为\"只会 API 调用\"。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_comparison_table(
        headers=["技术", "变换轴", "何时用", "Pinterest 适用"],
        rows=[
            ["**Random Crop + Flip**", "空间", "始终用（自然图像不变性）", "Pin 图像核心增广"],
            ["**Color Jitter / ColorAug**", "颜色", "自然图像、光照变化大", "Pin 风格迁移耐受"],
            ["**Random Erasing / Cutout**", "空间遮挡", "防过拟合局部特征", "搜索-保存信号避免过拟合 watermark"],
            ["**Mixup**", "像素插值", "正则化 + 校准改善", "分类头训练（商品 catalog）"],
            ["**CutMix**", "区域替换", "定位/检测也受益于空间结构保留", "多标签 Pin 分类"],
            ["**RandAugment**", "策略搜索", "大规模训练、不想手调", "视觉塔预训练的默认 pipeline"],
            ["**Text-Image 配对增广**", "模态一致", "多模态对比学习（CLIP-style）", "Pinterest shop 视觉+标题双塔"],
        ],
        title="5. Augmentation Catalog (geom / color / mixup / cutout / cutmix + multimodal)",
    )

    b.add_section("5.1 Mixup Math (要默写)", [
        FormulaBlock(
            latex=r"\tilde{x} = \lambda x_i + (1-\lambda) x_j, \quad \lambda \sim \text{Beta}(\alpha, \alpha)",
            explanation=(
                "像素插值 + 标签插值 `tilde_y = lambda*y_i + (1-lambda)*y_j`。"
                r"`alpha=0.2` 是常见值（分布两端聚集，接近原图；`alpha=1` 则均匀）。"
                "训练时每 batch 独立采样 `lambda`，防过拟合 + 提升 calibration。"
            ),
        ),
        (
            "**CutMix 替代**：随机 bbox `B`，`tilde_x = M ⊙ x_i + (1-M) ⊙ x_j`，"
            "`tilde_y = (|B|/HW) * y_j + (1 - |B|/HW) * y_i`。"
            "区别于 Mixup：保留完整物体部分（对定位更友好），视觉效果不那么\"糊\"。"
        ),
        (
            "**多模态增广**（Pinterest 双塔关键）：文本侧同步做 dropout-token / synonym-swap，"
            "图像侧做 geom/color；**关键约束**：两塔增广必须**保持语义对齐**——"
            "不能图像 cutmix 换了主体而文本描述没变，否则正样本对被破坏。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_section("6. Pinterest Visual-Search Angle (composition)", [
        (
            "Pinterest 视觉任务的主线 = **视觉塔 embedding + 下游多消费者**："
            "\n  - **PinSage / Pinnability 视觉特征塔**：ResNet-50 或 EfficientNet 骨干 "
            "+ GAP + projection head -> 256~512 维 embedding；\n"
            "  - **下游消费**：视觉搜索 (query image -> ANN 最近 Pin)、风格相似、"
            "广告 CTR 模型的视觉侧特征、shop 商品匹配（商品图 vs Pin 图的对比学习）。"
        ),
        (
            "**关键选型信号**（面试叙述顺序）：\n"
            "  1. **骨干选 ResNet-50 vs EfficientNet-B3/B4** -> 精度/成本：ResNet-50 工程成熟、"
            "蒸馏和量化工具链完备；EfficientNet 同精度下推理更快但\"难调\"。\n"
            "  2. **输入分辨率 224 vs 384** -> 推理成本 2.9x vs 召回 @10 提升 ~2%，"
            "广告侧通常 224 足够，视觉搜索头可能升 320/384。\n"
            "  3. **Aug pipeline**：RandAugment + Mixup 做骨干预训练；下游任务 head fine-tune 时"
            "关掉 Mixup（标签插值破坏对比学习正样本对定义）。\n"
            "  4. **对比学习 vs 分类**：embedding 塔通常 contrastive loss（InfoNCE / triplet），"
            "端到端比\"先分类再取倒数第二层\"高 5~10% 召回——面试时主动比较这两条路径。"
        ),
        (
            "**多模态扩展**（引流向 `[Pinterest-NLP]` 任务 T-P1-454）：视觉塔 embedding "
            "+ 文本塔（Pin title / description）embedding 对齐到同一空间；"
            "训练时正样本对 = (Pin 图, Pin 标题)，负样本对 = 随机采 + hard negative 挖掘。"
            "Pinterest 内部的 **ItemSage** 就是这种双塔统一；与 CLIP 的差别在 domain "
            "(UGC Pin 描述噪声更大) 和规模 (更多重复/近似重复样本)。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_interview_qa(
        "面试官问：设计 Pinterest 的相似 Pin 推荐，视觉骨干怎么选？",
        (
            "**3 步回答**：\n"
            "  1. **澄清**：端到端学 embedding 还是复用预训练塔？训练数据量级？延迟预算？\n"
            "  2. **默认选型**：ResNet-50 + GAP + 256 维 projection head；InfoNCE 对比学习，"
            "正样本 = 同 board 的 Pin，负样本 = batch 内 in-batch negatives + hard negative mining；\n"
            "  3. **成本优化**：视觉塔离线 batch 推理 + ANN 索引（HNSW / FAISS），"
            "线上仅算 query Pin embedding 后 ANN 召回 top-K。"
            "**加分**：主动提 224 vs 384 分辨率成本/精度权衡、distill 到 EfficientNet 降推理成本、"
            "BN 在 fine-tune 时要 track running stats 不用 batch stats。"
        ),
    )
    b.add_interview_qa(
        "ResNet 的 skip connection 到底为什么帮助训练？直观 + 梯度两种解释。",
        (
            "**直观**：网络从\"从零学 H(x)\"变成\"学 H(x) - x 的残差\"——identity "
            "已经是合理起点，残差只需学扰动，容易优化。**梯度**：反向传播时 `d(F(x)+x)/dx = "
            "dF/dx + 1`，`+1` 项提供无衰减的直通路，防梯度消失；"
            "即使 `F` 的 Jacobian 很小，总梯度仍 >=1，深层也能收敛。"
            "**额外**：BN 协同处理 internal covariate shift，两者共同把训 100+ 层从瓶颈变非问题。"
        ),
    )
    b.add_interview_qa(
        "Mixup 和 CutMix 有什么区别？视觉搜索任务更适合用哪个？",
        (
            "**区别**：Mixup = 像素级线性插值（图像会\"糊\"），标签线性加权；"
            "CutMix = 区域替换（保留完整物体部分），标签按面积加权。"
            "**视觉搜索任务选 CutMix**：embedding 塔要学\"这个 Pin 是关于某物体\"的表示，"
            "Mixup 的糊化会破坏视觉的局部判别性；CutMix 保留原始物体像素，"
            "embedding 对物体的敏感度不被稀释。**但对比学习阶段两者都关掉**——"
            "正负样本对定义依赖单一图像的语义完整。"
        ),
    )
    b.add_interview_qa(
        "微调 ImageNet 预训练模型到 Pinterest 商品分类，BN 要怎么处理？",
        (
            "**经典坑**：直接 `model.train()` + 小 batch（Pinterest 商品 catalog 每类样本少）"
            "-> BN 用 batch stats 噪声巨大 -> 性能劣化甚至不收敛。\n"
            "**解法 1（推荐）**：`model.eval()` 模式下用 ImageNet running stats，"
            "仅训 `gamma/beta` + classifier 头；若需要训骨干，`track_running_stats=False` "
            "保持 running stats 冻结。\n"
            "**解法 2（domain gap 大时）**：先短暂 `eval + 前向` 跑几百 step 更新 running stats 到 "
            "Pinterest 分布，再恢复正常训练。\n"
            "**加分**：提 GroupNorm/LayerNorm 可作为 BN 替代（小 batch 下更稳）；"
            "Pinterest 多模态任务里 text encoder 通常本来就 LayerNorm，视觉塔改 GN 后两塔训练"
            "超参更一致。"
        ),
    )

    # ----------------------------------------------------------------------
    b.add_checklist("Pinterest-Specific Self-Check", [
        "能默写卷积输出尺寸（含 dilation）+ 参数量公式",
        "能解释感受野递推，举例 ResNet-50 末端 RF 覆盖输入 >=1/2",
        "能一句话区分 VGG / ResNet / EfficientNet 的核心创新",
        "能回答\"GAP 替代 FC 的三个好处\"（参数量/正则/可解释性）",
        "能给 head-only / 渐进解冻 / full fine-tune 三档决策树",
        "能主动提微调时 BN 的三个坑及对应解法",
        "能区分 Mixup vs CutMix，并解释视觉搜索任务为何偏 CutMix",
        "能把 Pinterest 视觉塔设计拆成：骨干 + 分辨率 + aug + loss 四个维度",
        "能引流到 ItemSage 双塔多模态 (向 T-P1-454 展开)",
    ])

    return b.build()


# ==========================================================================
# Node 122 surgical patch: append Pinterest-angle section
# ==========================================================================

NODE_122_APPEND_BLOCK = (
    "\n\n"
    "### Pinterest Visual-Search Angle\n"
    "\n"
    "Pinterest 视觉任务（PinSage / Pinnability / ItemSage 视觉塔）几乎总是走 "
    "**ResNet-50 或 EfficientNet 骨干 + GAP + projection head** 的组合；下游分视觉搜索、"
    "相似 Pin、广告 CTR 视觉特征、商品图-Pin 图对比学习四类消费者。\n"
    "\n"
    "**Pinterest 相关的 CV 选型信号**（一句话列表，细节走公司文档）：\n"
    "\n"
    "- **骨干**：ResNet-50 (工程成熟) vs EfficientNet-B3 (同精度更省)——"
    "Pinterest 实战偏 ResNet-50 + 蒸馏/量化。\n"
    "- **分辨率**：224 (广告 CTR 够用) vs 320/384 (视觉搜索召回 +2%，推理 2.9x)——"
    "任务-成本权衡。\n"
    "- **Aug**：RandAugment + Mixup 用于骨干预训练；对比学习阶段两者都关掉。\n"
    "- **Loss**：embedding 塔用 InfoNCE / triplet，**不要**先分类再取倒数第二层"
    "（召回低 5-10%）。\n"
    "- **BN 微调坑**：预训练模型 fine-tune 时 `eval()` 或 `track_running_stats=False`，"
    "防小 batch stats 噪声打崩已学特征。\n"
    "\n"
    "公司文档：**Pinterest `CNN Foundation for Visual Search`**（company_documents，"
    "含 conv 机制推导、感受野递推、架构对比、迁移学习决策树、Aug 目录、面试 QA）。\n"
)


def patch_node_122_description(description: str) -> tuple[str, bool]:
    """Append Pinterest-angle block to node 122 if not already present."""
    if NODE_122_PATCH_MARKER in (description or ""):
        return description, False
    return (description or "") + NODE_122_APPEND_BLOCK, True


# ==========================================================================
# DB helpers
# ==========================================================================

def upsert_company_document(
    conn: sqlite3.Connection,
    company_id: int,
    title: str,
    content: str,
    doc_kind: str = "prep_note",
    source_type: str = "manual",
) -> tuple[int, str, int]:
    """Insert or update company_document by (company_id, title).

    Returns (doc_id, action, content_length).
    """
    row = conn.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (company_id, title),
    ).fetchone()
    if row:
        doc_id = row[0]
        conn.execute(
            "UPDATE company_documents SET content = ?, doc_kind = ?, "
            "source_type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (content, doc_kind, source_type, doc_id),
        )
        action = "UPDATED"
    else:
        cur = conn.execute(
            "INSERT INTO company_documents "
            "(company_id, title, content, source_type, doc_kind) "
            "VALUES (?, ?, ?, ?, ?)",
            (company_id, title, content, source_type, doc_kind),
        )
        doc_id = cur.lastrowid
        action = "INSERTED"
    new_len = conn.execute(
        "SELECT length(content) FROM company_documents WHERE id = ?", (doc_id,)
    ).fetchone()[0]
    return doc_id, action, new_len


def patch_framework_node_by_id(
    conn: sqlite3.Connection,
    node_id: int,
    patcher,
) -> tuple[int, str, int]:
    """Apply surgical patch to framework_node description by id."""
    row = conn.execute(
        "SELECT id, description FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()
    if not row:
        print(f"[FAIL] framework_node id={node_id} not found")
        sys.exit(1)
    nid, desc = row
    new_desc, changed = patcher(desc)
    if not changed:
        return nid, "UNCHANGED", len(desc or "")
    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?",
        (new_desc, nid),
    )
    new_len = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (nid,)
    ).fetchone()[0]
    return nid, "PATCHED", new_len


# ==========================================================================
# Main
# ==========================================================================

def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    content = build_cnn_foundation_doc()
    warns = StudyNoteBuilder.validate(content)
    for w in warns:
        print(f"[WARN] {w}")
    length = len(content)
    print(f"[BUILT] cnn_foundation doc length={length} chars")

    if not (6000 <= length <= 16000):
        print(
            f"[WARN] length={length} outside loose target [6000, 16000] "
            "(AC cap: <= ~2500 words = ~15000 bytes of mixed zh/en)"
        )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        did, action, dlen = upsert_company_document(
            conn, PINTEREST_COMPANY_ID, DOC_TITLE, content
        )
        print(
            f"[{action}] company_document id={did} "
            f"title='{DOC_TITLE}' length={dlen}"
        )

        nid, action, nlen = patch_framework_node_by_id(
            conn, NODE_122_ID, patch_node_122_description
        )
        print(f"[{action}] framework_node id={nid} length={nlen}")

        conn.commit()
    finally:
        conn.close()

    print("[DONE] Pinterest CNN foundation seed complete")


if __name__ == "__main__":
    main()
