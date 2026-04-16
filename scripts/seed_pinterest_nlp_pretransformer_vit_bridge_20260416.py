"""T-P1-454: Pre-transformer embedding history + ViT + cross-modal attention.

Surgical patches:
  (1) framework_node id=148 (BERT Family): append "### Pre-Transformer Embedding
      History" addendum covering Word2Vec (CBOW / skip-gram / negative sampling)
      + GloVe (co-occurrence matrix) and the context-free embedding limitation
      that motivated transformers.
  (2) framework_node id=164 (Vision-Language Models): append two sections:
      "### Vision Transformer (ViT) Internals" (patch embedding, [CLS] token,
      positional embedding, why scales beyond CNN) and "### Cross-Modal
      Attention vs In-Modality Self-Attention" (CLIP dual-encoder contrastive
      alignment vs self-attention; BLIP-2 Q-Former as fusion step).

Both patches use marker headings for idempotency. Pyramid mid; aim <=2000
combined words across the two addenda.

Usage::

    python scripts/seed_pinterest_nlp_pretransformer_vit_bridge_20260416.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mle_prep.db"

NODE_148_ID = 148
NODE_148_MARKER = "### Pre-Transformer Embedding History"

NODE_164_ID = 164
NODE_164_MARKER = "### Vision Transformer (ViT) Internals"


# ==========================================================================
# Node 148 addendum: Word2Vec / GloVe history and why transformers won
# ==========================================================================

NODE_148_APPEND = (
    "\n\n"
    "### Pre-Transformer Embedding History\n"
    "\n"
    "BERT 不是从天而降——它的直接前辈是 **Word2Vec / GloVe** 的"
    "**Static Word Embedding（静态词嵌入）** 时代（2013-2017）。理解这段史"
    "前史能让面试官看到你的 NLP 时代感。\n"
    "\n"
    "**Word2Vec (Mikolov et al., 2013)** 的两种训练目标：\n"
    "\n"
    "- **CBOW (Continuous Bag-of-Words，连续词袋)**：用窗口内上下文词预测"
    "中心词——`P(w_t | w_{t-k}, ..., w_{t+k})`。训练快、对高频词友好。\n"
    "- **Skip-Gram**：反过来用中心词预测上下文——`P(w_{t+j} | w_t)`。对低"
    "频词学得更好，是论文里的主推目标。\n"
    "\n"
    "$$\\mathcal{L}_{\\text{skip-gram}} = -\\frac{1}{T}\\sum_{t=1}^{T}"
    "\\sum_{-k \\le j \\le k, j \\ne 0} \\log P(w_{t+j} | w_t)$$\n"
    "\n"
    "softmax 分母对全词表求和（数十万词）成本爆炸，工程上用 "
    "**Negative Sampling（负采样）** 近似——每个正样本对配 k 个噪声词，把多"
    "分类降维成 k+1 个二分类：\n"
    "\n"
    "$$\\mathcal{L}_{\\text{NEG}} = -\\log \\sigma(v_{w_O}^T v_{w_I}) - "
    "\\sum_{i=1}^{k} \\mathbb{E}_{w_n \\sim P_n(w)} \\log \\sigma(-v_{w_n}^T "
    "v_{w_I})$$\n"
    "\n"
    "其中 `P_n(w) ∝ U(w)^{0.75}`（unigram 频率的 0.75 次幂，平滑高频词）。\n"
    "\n"
    "**GloVe (Pennington et al., 2014)** 走的是另一条路——**Global Co-occurrence"
    " Matrix Factorization（全局共现矩阵分解）**。先扫一遍语料构建词-词共现矩阵 "
    "`X_ij`（词 j 出现在词 i 上下文里的次数），再优化：\n"
    "\n"
    "$$\\mathcal{L}_{\\text{GloVe}} = \\sum_{i,j=1}^{V} f(X_{ij}) "
    "\\left(v_i^T \\tilde{v}_j + b_i + \\tilde{b}_j - \\log X_{ij}\\right)^2$$\n"
    "\n"
    "其中 `f(X_ij)` 是权重函数，对稀有共现降权、对极高频共现封顶。GloVe 的"
    "卖点：把 Word2Vec 的局部窗口信号和矩阵分解的全局统计信号结合。\n"
    "\n"
    "**为什么这一代被淘汰？** 一句话：**Context-Free（无上下文）**。\n"
    "\n"
    "- 一个词只对应一个向量。`bank` 在 `river bank`（河岸）和 `bank account`"
    "（银行账户）里共享同一向量——下游模型必须自己拆消歧。\n"
    "- 无法处理 OOV / 子词形态。后来 fastText 用 character n-gram 缓解，但仍"
    "是静态。\n"
    "- 无法建模词序内的语义组合。`man bites dog` 和 `dog bites man` 的词袋表示"
    "几乎相同。\n"
    "\n"
    "**ELMo (Peters et al., 2018)** 用双向 LSTM 给出第一个**Contextualized "
    "Embedding（上下文化嵌入）**——同一个词在不同句子里有不同向量。BERT 把这"
    "条路从 LSTM 升级到双向 Transformer，并把表示从\"特征提取\"升级到\"端到端"
    "微调\"，由此奠定 2018+ 的范式。\n"
    "\n"
    "**面试钩子**：被问 BERT 时主动提一句\"它解决了 Word2Vec/GloVe 的 "
    "context-free 局限——同一个 `bank` 在双向 self-attention 下能基于左右上下"
    "文动态编码\"，立刻显出比只会背 BERT 公式的候选人更扎实的史观。\n"
)


# ==========================================================================
# Node 164 addendum: ViT internals + cross-modal attention contrast
# ==========================================================================

NODE_164_APPEND = (
    "\n\n"
    "### Vision Transformer (ViT) Internals\n"
    "\n"
    "CLIP 的图像塔默认是 **ViT (Vision Transformer，视觉变换器)**——"
    "Dosovitskiy et al. (2020) 把纯 Transformer 直接搬到视觉，跳过"
    "卷积归纳偏置，凭数据规模碾压 CNN。理解 ViT 三步走：\n"
    "\n"
    "**1. Patch Embedding（图块嵌入）**——把图像切成不重叠的 `P x P` 小块"
    "（典型 `P=16`），每块展平成 `P^2 * C` 维向量再线性投影到 `D` 维 token。"
    "`224x224` 图像 + `16x16` patch => `(224/16)^2 = 196` 个 token。等价于"
    "一个 `P x P` stride=`P` 的卷积——所以\"ViT 没有卷积\"严格说不对，是"
    "\"只有第一层卷积\"。\n"
    "\n"
    "$$z_0 = [x_{\\text{cls}}; x_p^1 W_E; x_p^2 W_E; \\ldots; x_p^N W_E] + "
    "E_{\\text{pos}}$$\n"
    "\n"
    "**2. [CLS] Token + Positional Embedding**——在 196 个 patch token 前面"
    "拼一个可学习的 `[CLS]` token（同 BERT），再叠加可学习的 1D positional "
    "embedding（每个位置一个 `D` 维向量）。注意是 1D 不是 2D——"
    "ViT 论文实测 2D-aware positional embedding 收益微乎其微，1D 学习式够用。"
    "`[CLS]` 经 12/24 层 self-attention 后聚合全局信息，输出接线性头做分类。\n"
    "\n"
    "**3. 标准 Transformer Encoder 堆叠**——每层 `MSA -> Add&Norm -> MLP -> "
    "Add&Norm`，PreNorm 变体（LayerNorm 在子层前）训练更稳。\n"
    "\n"
    "**为什么 ViT 在大数据下碾压 CNN？** 三点：\n"
    "\n"
    "- **CNN 的归纳偏置是双刃剑**：locality + translation equivariance 在小"
    "数据时是先验红利，在大数据时是表达天花板——CNN 难以学跨远距 patch 的"
    "全局关系。\n"
    "- **Self-attention 的全局感受野**：从第一层起每个 token 就能看到所有其他"
    "token，相当于第 0 层就有 \"全图感受野\"，CNN 要堆几十层才能逼近。\n"
    "- **可扩展性更线性**：参数量翻倍 -> 性能近似线性提升；CNN 在 EfficientNet"
    "之后已显饱和。但 ViT 在 ImageNet-1K (1.3M) 量级反而不如 ResNet——这是 "
    "**JFT-300M 临界点**：~10M+ 数据后 ViT 反超，量越大差距越大。\n"
    "\n"
    "**Pinterest / 多模态视角**：CLIP 用 ViT-B/16 或 ViT-L/14 当图像塔，主要"
    "因为 patch token 序列天然适合和文本 token 序列做对比/交叉——CNN 的 GAP"
    "向量信息更压缩，跨模态对齐时损失更多。视觉搜索召回任务里，ViT 嵌入比同"
    "参数量 ResNet 嵌入的零样本检索 +3~6%。\n"
    "\n"
    "**与 CLIP 的连接**：CLIP 的 ViT 移除了 `[CLS]` 后的分类头，改成线性投影"
    "到联合 embedding 空间，并对所有 token（含 `[CLS]`）做平均池化前的 layer"
    "norm；这些是\"对比学习版 ViT\"区别于\"分类版 ViT\"的细节。\n"
    "\n"
    "### Cross-Modal Attention vs In-Modality Self-Attention\n"
    "\n"
    "多模态融合的核心选择 = **何时让两个模态见面**？三种主流路径：\n"
    "\n"
    "**1. Late Fusion / Dual Encoder（晚融合双塔）— CLIP 路径**：图像塔和文"
    "本塔**完全独立**做 self-attention（in-modality 内部建模），最后在共享"
    "embedding 空间用对比损失对齐。两塔之间**没有任何 cross-attention**——"
    "对齐信号只来自 InfoNCE loss 的梯度。\n"
    "\n"
    "- 优点：检索/召回场景可离线预计算两侧 embedding，线上只算一侧 + ANN，"
    "延迟极低；视觉塔可独立蒸馏/量化部署。\n"
    "- 限制：表达力受限——两塔间只通过一个标量相似度沟通，没法做\"看图答题\""
    "类细粒度推理。\n"
    "\n"
    "**2. Early Fusion / Cross-Attention（早融合交叉注意力）— Flamingo / "
    "BLIP 路径**：在解码器/语言塔的某些层插入 cross-attention，`Query` 来自"
    "文本 token，`Key/Value` 来自视觉 token：\n"
    "\n"
    "$$\\text{CrossAttn}(Q_{\\text{text}}, K_{\\text{img}}, V_{\\text{img}}) "
    "= \\text{softmax}\\left(\\frac{Q_{\\text{text}} K_{\\text{img}}^T}"
    "{\\sqrt{d_k}}\\right) V_{\\text{img}}$$\n"
    "\n"
    "对比 in-modality self-attention 的区别**只有 K/V 的来源**——self-attention"
    "里 Q/K/V 都来自同一序列，cross-attention 里 Q 来自一个序列、K/V 来自另"
    "一个。Flamingo 加 tanh gating 让 cross-attention 可学习地\"逐渐打开\"，"
    "防止训练初期破坏预训练 LLM 能力。\n"
    "\n"
    "- 优点：视觉信息可在 LLM 每层注入，支持复杂指令跟随、VQA、grounding。\n"
    "- 限制：在线推理必须两塔都跑，无法离线缓存视觉 embedding 复用；"
    "不适合大规模检索。\n"
    "\n"
    "**3. Q-Former 中介融合 — BLIP-2 路径**：Salesforce 的 BLIP-2 (Li et al., "
    "2023) 在冻结的 ViT 和冻结的 LLM 之间插一个轻量 **Q-Former (Querying "
    "Transformer，查询变换器)**——一组可学习的 32 个 query token，通过 "
    "cross-attention 从 ViT 的视觉 token 里\"提炼\"信息，再喂给 LLM 当软提"
    "示。\n"
    "\n"
    "- 第一阶段：Q-Former 与 ViT 配对训练 image-text matching / image-text "
    "contrastive / image-grounded text generation 三任务，让 query token 学会"
    "压缩视觉语义；\n"
    "- 第二阶段：把 query token 投影到 LLM embedding 空间，仅训投影层；ViT "
    "和 LLM 全程冻结。\n"
    "- 关键收益：训练成本骤降（仅 ~1.2 亿可训参数），且可即插即换 LLM "
    "(OPT/FlanT5/LLaMA)。是\"用 cross-attention 做 cheap fusion\"的经典范式。\n"
    "\n"
    "**面试速答框架**：被问\"多模态怎么融合\"先反问任务——\n"
    "- **检索/召回**（Pinterest 视觉搜索） => CLIP-style 双塔 + InfoNCE；\n"
    "- **VQA/对话**（Pinterest Lens 问答） => BLIP-2 / LLaVA 系，cross-attention 或 projection 注入 LLM；\n"
    "- **生成/编辑**（Pinterest Stable Diffusion 控制） => CLIP 文本塔 + cross-attention 控制 U-Net。\n"
    "\n"
    "**与上文 BERT 史前史的呼应**：Word2Vec 是\"无上下文嵌入\"，CLIP 是\"跨"
    "模态对比学习对齐的上下文嵌入\"——核心进展都是\"把更多上下文（语言上下文、"
    "视觉上下文、跨模态上下文）压进同一向量空间\"。这条主线一旦讲出来，多模"
    "态面试就从\"背架构\"变成\"讲表示学习史\"。\n"
)


# ==========================================================================
# DB helper: surgical append by id with marker idempotency
# ==========================================================================

def patch_node(
    conn: sqlite3.Connection, node_id: int, marker: str, append_block: str,
) -> tuple[str, int]:
    """Append ``append_block`` to framework_node description if marker absent.

    Returns (action, new_length).
    """
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()
    if not row:
        print(f"[FAIL] framework_node id={node_id} not found")
        sys.exit(1)
    desc = row[0] or ""
    if marker in desc:
        return "UNCHANGED", len(desc)
    new_desc = desc + append_block
    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?",
        (new_desc, node_id),
    )
    return "PATCHED", len(new_desc)


def main() -> None:
    """Apply both addenda; print word counts for AC verification."""
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    n148_words = len(NODE_148_APPEND.split())
    n164_words = len(NODE_164_APPEND.split())
    total = n148_words + n164_words
    print(f"[BUILT] node 148 addendum words={n148_words}")
    print(f"[BUILT] node 164 addendum words={n164_words}")
    print(f"[BUILT] total words={total} (AC cap: <=2000)")
    if total > 2000:
        print(f"[WARN] total {total} > 2000 word budget")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        action_148, len_148 = patch_node(
            conn, NODE_148_ID, NODE_148_MARKER, NODE_148_APPEND
        )
        print(f"[{action_148}] framework_node id={NODE_148_ID} length={len_148}")

        action_164, len_164 = patch_node(
            conn, NODE_164_ID, NODE_164_MARKER, NODE_164_APPEND
        )
        print(f"[{action_164}] framework_node id={NODE_164_ID} length={len_164}")

        conn.commit()
    finally:
        conn.close()

    print("[DONE] T-P1-454 pre-transformer + ViT + cross-modal addenda applied")


if __name__ == "__main__":
    main()
