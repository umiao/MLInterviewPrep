"""KG-M-02: Migrate Doc 19 RoPE + Long Context to canonical framework_node.

Sibling of KG-M-01 (diffusion). Doc 19 (Adobe MLE Prep All-in-One) has a
Day-4 review note titled `# RoPE + 长上下文扩展 + 视频生成 — 面试复习笔记`
that the legacy 合集 audit flagged as SOLE SOURCE in the corpus for the
**RoPE full derivation** ($R_m^T R_n = R_{n-m}$ proof, efficient
element-wise form, Q/K-only projection), **Position Interpolation (PI)**,
**NTK-aware scaling** (base-theta adjustment), and **YaRN** (per-frequency
mixed PI/NTK + attention temperature). Node 143
(`pillar6.transformer.position_encoding`) already covers the Sinusoidal /
ALiBi overview but stops short of the RoPE proof + long-context math. Per
the KG migration protocol we (a) lift the canonical concept tree to a
NEW framework_node under pillar6.transformer, (b) preserve the longer
paper-style write-up as a standalone doc, (c) plant a > **正典** pointer
at the top of Doc 19's RoPE section, (d) record the relationships in
concept_links, and (e) snapshot the pre-migration Doc 19 to
archive/pre_kg/.

Scope of canonical extraction (covered by this migration):
  Section 1 位置编码：为什么重要
  Section 2 RoPE：旋转位置编码 (2.1-2.5)
  Section 3 PE 方法对比
  Section 4 长上下文扩展方法 (4.0-4.3 + 对比总结)
  Section 6 (misconceptions 1, 2, 5 -- RoPE/long-context items only)
  Section 7 (Q1 RoPE proof, Q2 PI-vs-NTK -- RoPE/long-context items only)
  Section 8 quick-reference card (RoPE + long-context rows only)

Explicitly excluded (deferred to a separate future migration):
  Section 5 视频生成 (3D VAE, temporal attention, DiT/Sora, Firefly)
  Section 6 误解 3, 4 (video generation items)
  Section 7 Q3, Q4, Q5 (video generation items)

Deliverables (all idempotent, single sentinel guards re-run):
  1. archive/pre_kg/20260416/adobe_doc19_pre_rope_longctx_migration.md
     (full pre-migration Doc 19 content; written once).
  2. NEW framework_node at pillar6.transformer.long_context_rope
     (parent=32, depth=2, importance=0.95, P0) with a ~10-12k char
     canonical_hub description covering the 8 canonical sections above.
  3. docs/rope_long_context_canonical.md -- full paper-style deep dive
     (sections 1-4 + 6 [items 1/2/5] + 7 [Q1/Q2] + 8 [RoPE rows] from
     Doc 19, video-generation content stripped).
  4. Doc 19 patched: a > **正典** [RoPE & Long Context]() blockquote
     inserted directly under the `# RoPE + 长上下文扩展 + 视频生成`
     heading.
  5. concept_links rows:
       framework_node:<new_id>  -- absorbed_from --> company_document:19
       framework_node:<new_id>  -- mentions      --> company_document:19
       company_document:19      -- canonical     --> framework_node:<new_id>

Sentinel: '<!-- KG_M_02_ROPE_LONGCTX_20260416 -->' in the framework_node's
description, the standalone doc, and the patched Doc 19 region. On
re-run, presence of the sentinel triggers [UNCHANGED] and skips writes.

Acceptance invariants enforced (rollback on violation):
  - canonical_node description length in [8000, 14000]
  - standalone doc length >= 7500 chars (the RoPE segment in Doc 19 is
    naturally smaller than the diffusion segment; after stripping section 5
    video generation and five video-related Q&A/误解 items, ~8k chars
    remain -- KG-M-01's 18000-char floor would be unrealistic here)
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
ARCHIVE = ROOT / "archive" / "pre_kg" / "20260416" / "adobe_doc19_pre_rope_longctx_migration.md"
STANDALONE = ROOT / "docs" / "rope_long_context_canonical.md"

SENTINEL = "<!-- KG_M_02_ROPE_LONGCTX_20260416 -->"
DOC19_ID = 19
NODE_PATH = "pillar6.transformer.long_context_rope"
NODE_TITLE = "RoPE & Long Context Extension (PI / NTK-aware / YaRN)"
TRANSFORMER_PARENT_ID = 32  # pillar6.transformer


# ---------------------------------------------------------------------------
# Canonical framework_node description (target ~10500 chars, in [8000, 14000])
# ---------------------------------------------------------------------------

NODE_DESCRIPTION = f"""<!-- doc_kind: canonical_hub -->
<!-- canonical_topic: rope_long_context -->
{SENTINEL}

# RoPE & Long Context Extension 正典枢纽：RoPE / PI / NTK-aware / YaRN

> **前置** [Self-Attention (pillar6.transformer.self_attention)](/framework/141)
> **前置** [Multi-Head Attention (pillar6.transformer.multi_head_attention)](/framework/142)
> **前置** [Position Encoding (pillar6.transformer.position_encoding)](/framework/143)

## Overview

**RoPE (Rotary Position Embedding，旋转位置嵌入)** 通过把 Q/K 向量在 2D 子空间上旋转一个与位置成正比的角度来注入位置信号。它是 LLaMA / Mistral / Qwen / Gemma 等现代 LLM 的默认位置编码机制，也是**长上下文扩展**三件套（PI / NTK-aware / YaRN）的数学基础。本节点是 RoPE 家族与长上下文方法的**正典枢纽**——它定型 $R_m^T R_n = R_{{n-m}}$ 的相对距离证明、频率分配的 `rotate_half` 高效实现、RoPE 只作用在 Q/K 上的设计取舍，并统一 **Position Interpolation (PI)**、**NTK-aware Scaling**、**YaRN** 三条长上下文扩展路径。完整 paper 风格推导见 [RoPE & Long Context Canonical Deep Dive](/docs/rope_long_context_canonical.md)；Adobe 面试视角的速记请见 [Adobe Doc 19](/companies/adobe/documents/19) 的 Day 4 章节。

## 1. 位置编码：为什么重要

Transformer 本身是**置换不变的 (permutation-invariant)**：没有位置信息时，attention 对任何 token 顺序产生相同输出——「狗咬人」与「人咬狗」无法区分。位置编码就是打破这个对称性的机制。

**好的位置编码需要满足四个条件**：

1. **唯一性**：每个位置有独一无二的编码。
2. **有界性**：位置再大，编码值也不会爆炸。
3. **相对距离感知**：attention 应依赖 $m-n$（相对距离），而非绝对位置 $m, n$。
4. **外推能力**：训练时用 4K 长度，推理时能处理 32K+。

本节点后续所有方法的优劣评判都围绕这四点展开。

## 2. RoPE：核心直觉与频率设计

传统方法（Sinusoidal、Learned）是**加法**：把位置向量加到 token embedding 上。**RoPE 换了思路——不加，而是旋转**：把 Q/K 向量在 2D 平面上旋转一个与位置成正比的角度。时钟比喻：位置 0 的指针指向 12 点，位置 1 转一小格、位置 2 转两小格……两根指针的夹角只取决于它们隔了几格，与各自指向哪里无关——这就是「相对位置」。

**频率设计**：embedding 维度为 $d$，分成 $d/2$ 对。第 $i$ 对的旋转频率：

$$\\theta_i = \\frac{{1}}{{10000^{{2i/d}}}},\\quad i = 0, 1, \\ldots, d/2 - 1$$

- **小 $i$（前面的维度）**：$\\theta_i$ 大，旋转快 → 捕捉**局部 / 短距离**模式。
- **大 $i$（后面的维度）**：$\\theta_i$ 小，旋转慢 → 捕捉**长距离**模式。

> 多刻度尺子比喻：有的刻度精细（毫米）、有的粗糙（厘米），合在一起同时量近的和远的。

> 注意：这个频率公式和原始 Transformer 的 Sinusoidal PE 完全一样；**区别在于注入方式**——Sinusoidal 用加法，RoPE 用旋转。

## 3. RoPE 旋转矩阵与相对距离证明（核心证明）

**旋转矩阵**。位置 $m$、第 $i$ 维度对的旋转：

$$\\begin{{pmatrix}} \\tilde{{x}}_{{2i}} \\\\ \\tilde{{x}}_{{2i+1}} \\end{{pmatrix}} = \\begin{{pmatrix}} \\cos(m\\theta_i) & -\\sin(m\\theta_i) \\\\ \\sin(m\\theta_i) & \\cos(m\\theta_i) \\end{{pmatrix}} \\begin{{pmatrix}} x_{{2i}} \\\\ x_{{2i+1}} \\end{{pmatrix}}$$

整体是分块对角矩阵 $R_m = \\mathrm{{diag}}(R^{{(0)}}_m, R^{{(1)}}_m, \\ldots, R^{{(d/2-1)}}_m)$。应用到 Q 和 K：$\\tilde{{q}}_m = R_m\\,q_m$，$\\tilde{{k}}_n = R_n\\,k_n$。

**关键性质**：$R_m^T R_n = R_{{n-m}}$。两步推导：

1. **旋转矩阵的转置等于逆旋转**：$R_m^T = R_{{-m}}$。
2. **两个旋转的复合 = 角度相加**：$R_{{-m}}\\cdot R_n = R_{{n-m}}$，展开矩阵乘法后用三角和差公式 $\\cos(A-B) = \\cos A\\cos B + \\sin A\\sin B$ 合并即得。

因此 attention score：

$$\\tilde{{q}}_m^T \\tilde{{k}}_n = q_m^T R_m^T R_n k_n = q_m^T R_{{n-m}} k_n$$

**绝对位置 $m, n$ 消失，只剩相对距离 $n-m$。证毕**。这是 RoPE 与 Sinusoidal 最本质的差异——后者的点积 $h_m^T h_n = (x_m+PE_m)^T(x_n+PE_n)$ 展开含 $x_m^T PE_n + PE_m^T x_n + PE_m^T PE_n$ 交叉项，相对信号与内容信号混杂；RoPE 的点积是**干净的纯相对**。

## 4. 高效实现与 Q/K-only 作用域

**element-wise 实现**（无需构造稀疏旋转矩阵）：

$$\\mathrm{{RoPE}}(x_m) = x_m \\odot \\cos(m\\theta) + \\mathrm{{rotate\\_half}}(x_m) \\odot \\sin(m\\theta)$$

其中 `rotate_half`：$(x_0, x_1, x_2, x_3, \\ldots) \\to (-x_1, x_0, -x_3, x_2, \\ldots)$。本质就是 2D 旋转的分量形式：$a\\cos\\theta - b\\sin\\theta$ 和 $a\\sin\\theta + b\\cos\\theta$。

**作用域仅限 Q 和 K**：

$$x \\xrightarrow{{W_Q}} q \\xrightarrow{{\\mathrm{{RoPE}}}} \\tilde{{q}} \\xrightarrow{{\\mathrm{{dot\\,product}}}} \\text{{attention score}}$$

- **Value 不旋转**：RoPE 只影响「谁关注谁」（路由），不影响「关注到之后传什么信息」（内容）。
- **RoPE 之后没有 MLP**：点积按维度对应相乘，不做 cross-dimension mixing；MLP 会破坏「同一维度对内部旋转」的几何。
- **$W_Q, W_K$ 是 learned 的**：模型可以学会把需要高频位置信号的信息路由到小 $i$ 维度，把需要低频信号的路由到大 $i$ 维度。**频率分配固定，语义路由可学**。

## 5. PE 方法对比

| 方法 | 类型 | 相对位置？ | 外推能力 | 代表模型 |
| --- | --- | --- | --- | --- |
| Sinusoidal (2017) | 加法，固定 | 弱（dot product 含交叉项） | 差 | 原始 Transformer |
| Learned Absolute | 加法，可学 | 无 | 无（固定最大长度） | BERT, GPT-2 |
| ALiBi | Attention 偏置 | 是（线性惩罚） | 好 | BLOOM, MPT |
| **RoPE** | **乘法（旋转）** | **是（数学精确）** | **中等（需扩展方法）** | **LLaMA, Mistral, Qwen, Gemma** |

**RoPE 成为主流的四大原因**：(1) 相对位置是**数学性质**而非近似；(2) **零额外参数**（不像 Learned PE）；(3) **KV-cache 友好**（每个 token 独立旋转，不需重算历史 token）；(4) **计算高效**（element-wise cos/sin）。

## 6. 长上下文问题的根源

模型训练时最长见过 $L$ 个 token，每个维度 $i$ 见过的最大旋转角度为 $L \\cdot \\theta_i$。推理时若位置 $m > L$，旋转角度超出训练分布 (out-of-distribution)，attention 崩溃。**核心矛盾：位置变大 → 角度超出训练分布 → 模型无法处理**。三条主流扩展路径如下：PI 压缩位置、NTK 调整频率、YaRN 分维度混合 + 温度。

## 7. Position Interpolation (PI)：等比压缩位置

**思路**：不外推，压回训练范围内做插值。从 4K 扩展到 32K，所有位置乘以 $4096 / 32768 = 1/8$：

$$m' = m \\cdot \\frac{{L_{{\\text{{train}}}}}}{{L_{{\\text{{target}}}}}}$$

位置 32000 → 位置 4000，回到训练范围。**优点**：极其简单，fine-tune ~1000 步即可（Chen et al. 2023, Meta）。**缺点**：对**所有频率维度做均匀压缩**；高频维度原本用来区分相邻 token，压缩后相邻位置角度差缩小 → **局部分辨率下降**（尺子整体缩小 8 倍——厘米级测量没问题，毫米精度丢了）。

## 8. NTK-aware Scaling：只拉伸低频

**思路**：PI 的问题在于高频被误伤。NTK-aware 修改 RoPE 的 base frequency $b=10000$，让高频基本不变、只拉伸低频：

$$\\theta_i' = \\frac{{1}}{{(b\\cdot \\alpha)^{{2i/d}}}},\\quad \\alpha = \\frac{{L_{{\\text{{target}}}}}}{{L_{{\\text{{train}}}}}}$$

- **小 $i$（高频）**：指数 $2i/d$ 小，$\\alpha$ 影响被稀释，频率**几乎不变**。
- **大 $i$（低频）**：指数大，频率**显著降低**，容纳更远位置。

> 尺子比喻：只把厘米刻度拉宽来量更长的东西，毫米刻度保持不变。

**优点**：保留高频局部模式，甚至 **zero-shot 可用**（无需 fine-tune 即可获得可用效果，llama.cpp 社区率先推广）。**命名由来**：Neural Tangent Kernel 理论揭示网络对不同频率特征学习速度不同，作者借此视角发现应**区别对待不同频率维度**，故名 "NTK-aware"。

## 9. YaRN：分维度精细处理 + 调温度

**思路**：按频率分三组，各自最优处理：

| 频率组 | 维度 | 处理方式 |
| --- | --- | --- |
| 高频（局部） | 小 $i$ | 不动，保持原样 |
| 中频 | 中间 $i$ | PI 与 NTK 的混合 |
| 低频（长距离） | 大 $i$ | 完全用 PI 插值 |

**Attention 温度缩放**：上下文变长后 attention 分布变平坦（信息熵增加），用温度因子 $\\sqrt{{t}}$ 补偿：

$$\\mathrm{{Attention}}(Q, K, V) = \\mathrm{{softmax}}\\!\\left(\\frac{{QK^T}}{{\\sqrt{{d}}\\cdot \\sqrt{{t}}}}\\right)V$$

**结果**：只需 ~400 步 fine-tune，质量最好——LLaMA 3.1（128K 上下文）默认使用 YaRN。**命名由来**："Yet another RoPE extensioN"——CS 领域自嘲式命名，类似 YAML (Yet Another Markup Language)。

## 10. 三法对比速查

| 方法 | 一句话 | Fine-tuning | 质量 |
| --- | --- | --- | --- |
| PI | 等比压缩所有位置 | ~1K 步 | 好，但丢局部细节 |
| NTK-aware | 改 base frequency，保高频、拉低频 | ~1K 步（或 zero-shot） | 更好的局部保留 |
| **YaRN** | **分维度 PI/NTK + 温度缩放** | **~400 步** | **最佳** |

## Interview Pitfalls（常见误区）

- **「RoPE 是绝对位置编码」** —— 不全对。编码机制是绝对的（每个位置 $m$ 得到确定的旋转角度），但产生的 attention pattern 是**纯相对的**（$\\tilde{{q}}_m^T \\tilde{{k}}_n$ 只依赖 $n-m$）。准确说法：**绝对编码，相对效果**。
- **「PI 和 NTK 做的是同一件事」** —— 错。PI 对**所有频率维度均匀压缩**（伤害高频局部分辨率）；NTK 修改 base frequency，**只拉伸低频、保护高频**。一句话：**PI 压缩位置，NTK 调整频率**。
- **「RoPE 天然支持任意长度」** —— 错。RoPE 在训练长度内很好，超出后旋转角度 out-of-distribution，attention 崩溃。需要 PI/NTK/YaRN 扩展。准确表述：**RoPE 使长上下文成为可能，而非处理长上下文**。
- **「RoPE 也作用在 V 上」** —— 错。RoPE 只旋转 Q 和 K；V 保持不变，因为旋转 V 会扭曲传递给下游 token 的内容信号。
- **「频率公式与 Sinusoidal 不同」** —— 错。$\\theta_i = 1/10000^{{2i/d}}$ 与原始 Sinusoidal PE 完全一样，区别只在**注入方式**（加法 vs 旋转）。
- **「Sinusoidal 外推能力强所以无需扩展」** —— 实际上 Sinusoidal 在长距离的点积衰减不稳定，RoPE 在训练分布内的相对精度优于 Sinusoidal，两者在长度外推上都有困难。
- **「YaRN 只是 PI + NTK 平均」** —— 错。YaRN 是**按频率分组的精细混合** + attention temperature scaling，三件事一起做。

## Components（统摄的周边节点 / 文档）

- [Position Encoding (pillar6.transformer.position_encoding)](/framework/143) -- Sinusoidal / Learned / ALiBi 的基础叙述；本节点是其 RoPE 与长上下文扩展的深度枢纽。
- [Self-Attention (pillar6.transformer.self_attention)](/framework/141) -- RoPE 的相对距离证明依赖 self-attention 的点积结构。
- [Multi-Head Attention (pillar6.transformer.multi_head_attention)](/framework/142) -- RoPE 按 head 内 2D 子空间旋转；多头结构决定 $d/2$ 对的数量。
- [KV Cache & PagedAttention (pillar6.llm_inference.kv_cache)](/framework/156) -- RoPE 的「每 token 独立旋转」是 KV-cache 能生效的几何前提。
- [Adobe MLE Prep Day 4: RoPE + 长上下文扩展 + 视频生成 (Doc 19)](/companies/adobe/documents/19) -- 面试速记口吻、扩展实例与 Self-Check QA。
- [RoPE & Long Context Canonical Deep Dive](/docs/rope_long_context_canonical.md) -- 标准化的 paper 风格深推导（独立长文）。

## Key Takeaways

- **RoPE = 旋转而非加法**：$\\tilde{{q}} = R_m q,\\;\\tilde{{k}} = R_n k$，点积只依赖 $n-m$——绝对编码，相对效果。
- **$R_m^T R_n = R_{{n-m}}$ 是核心代数不变量**，由旋转的转置=逆 + 复合=角度相加组合而来。
- **频率分配固定 $\\theta_i = 1/10000^{{2i/d}}$**，但 $W_Q, W_K$ 可学——模型自行决定把哪类语义路由到哪个频率维度。
- **RoPE 只旋转 Q/K、不旋转 V**，RoPE 之后不能接 MLP，否则破坏「同一维度对内部旋转」的几何。
- **PI 压缩位置**（伤高频），**NTK 调整频率**（保高频、拉低频），**YaRN 分维度混合 + 温度**（最佳质量，LLaMA 3.1 默认）。
- **长上下文不是 RoPE 的免费午餐**：训练分布外旋转角度会崩溃，必须借助 PI/NTK/YaRN 三条路径之一 fine-tune。

> **后续** [KV Cache & PagedAttention](/framework/156)
> **后续** [Attention Variants (MQA, GQA, Flash Attention)](/framework/146)
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
    """Write the archive snapshot exactly once (captures pre-migration state)."""
    if ARCHIVE.exists():
        return ARCHIVE.read_text(encoding="utf-8"), "unchanged"
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_text(current_content, encoding="utf-8")
    return current_content, "written"


ROPE_H1 = "# RoPE + 长上下文扩展 + 视频生成 — 面试复习笔记"
ROPE_END_H1 = "# Day 5：推理优化 + 项目叙事映射（Adobe 面试准备）"

# Section 5 (视频生成) is excluded from the canonical deep-dive. So are the
# video-generation items inside sections 6 and 7. We slice by `## N.` and
# `### N.M` headings and keep only RoPE / long-context content.
EXCLUDED_H2_NUMS = {5}  # Section 5 视频生成 entirely excluded
EXCLUDED_H3_LABELS = {
    "### 误解 3",  # 视频生成就是每帧跑一次图像模型
    "### 误解 4",  # Sora 用的是 U-Net
    "### Q3",      # Spatial vs Temporal Attention
    "### Q4",      # DiT vs U-Net
    "### Q5",      # 3D VAE 压缩计算
}


def _build_standalone_deepdive(pre_migration_doc19: str) -> str:
    """Extract RoPE/long-context content from pre-migration Doc 19.

    The RoPE segment spans from `# RoPE + 长上下文扩展 + 视频生成 — 面试复习笔记`
    up to (but excluding) `# Day 5：推理优化 + 项目叙事映射（Adobe 面试准备）`.
    Inside that segment we drop Section 5 (video generation) entirely, and
    the three video-specific Q&A and two video-specific misconceptions.
    The resulting deep-dive is paper-style with a sentinel header.
    """
    h1_start = pre_migration_doc19.find(ROPE_H1)
    if h1_start < 0:
        raise RuntimeError(f"Pre-migration Doc 19 missing H1: {ROPE_H1!r}")
    h1_end = pre_migration_doc19.find(ROPE_END_H1, h1_start + len(ROPE_H1))
    if h1_end < 0:
        raise RuntimeError(f"Pre-migration Doc 19 missing end H1: {ROPE_END_H1!r}")
    rope_segment = pre_migration_doc19[h1_start:h1_end]

    # Strip section 5 (视频生成) entirely: from `## 5. 视频生成` up to the
    # next `## ` heading (section 6).
    sec5_re = re.compile(r"^## 5\.\s+.+$", re.MULTILINE)
    sec5_m = sec5_re.search(rope_segment)
    if not sec5_m:
        raise RuntimeError("Section 5 video generation heading not found")
    next_h2_re = re.compile(r"^## \d+\.\s+.+$", re.MULTILINE)
    next_h2 = next_h2_re.search(rope_segment, sec5_m.end())
    if not next_h2:
        raise RuntimeError("Section 6 heading not found after section 5")
    rope_segment = rope_segment[: sec5_m.start()] + rope_segment[next_h2.start() :]

    # Strip excluded H3 items by slicing [label, next H3 or H2].
    for label in EXCLUDED_H3_LABELS:
        pat = re.compile(
            rf"^{re.escape(label)}[^\n]*\n", re.MULTILINE
        )
        m = pat.search(rope_segment)
        if not m:
            continue
        # find next H3 or H2 header after this one
        after = rope_segment[m.end():]
        next_hdr = re.search(r"^(###? )", after, re.MULTILINE)
        if next_hdr:
            end = m.end() + next_hdr.start()
        else:
            end = len(rope_segment)
        rope_segment = rope_segment[: m.start()] + rope_segment[end:]

    header = (
        f"{SENTINEL}\n\n"
        "# RoPE & Long Context Extension — Canonical Deep Dive\n\n"
        f"> **正典节点** [RoPE & Long Context Extension ({NODE_PATH})](/framework/<NODE_ID>)\n\n"
        "> 本文是 KG-M-02 迁移自 Adobe Doc 19 Day 4 的 paper 风格深推导，**与正典节点共生**。"
        "结构对应：节点给出 10-section 概览与 interview pitfalls；本文保留 Doc 19 中 RoPE / PE / 长上下文扩展 四节的完整叙述。"
        "Section 5 视频生成、误解 3/4、Q3/Q4/Q5 与视频生成直接相关的内容已剔除——它们属于未来的视频生成枢纽节点（pillar6.video_generation，暂未创建）。\n\n---\n\n"
    )
    standalone = header + rope_segment
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
        VALUES (?, ?, 2, ?, ?, 0.95, 'P0', 'not_started', 0.0)
        """,
        (TRANSFORMER_PARENT_ID, NODE_PATH, NODE_TITLE, NODE_DESCRIPTION),
    )
    return cur.lastrowid, "inserted"


def _patch_doc19(conn: sqlite3.Connection, original: str, node_id: int) -> tuple[str, str]:
    """Insert > **正典** pointer + sentinel directly under the RoPE H1."""
    if SENTINEL in original:
        return original, "unchanged"
    pointer_block = (
        f"\n{SENTINEL}\n"
        f"> **正典** [RoPE & Long Context Extension ({NODE_PATH})](/framework/{node_id})\n"
        f"> 本节为 Adobe 面试视角的 RoPE / 长上下文扩展 / 视频生成 速记。RoPE / PI / NTK-aware / YaRN 的完整概念树与 paper 风格深推导见正典节点与 [docs/rope_long_context_canonical.md](/docs/rope_long_context_canonical.md)。视频生成部分（第 5 节）暂未迁移，保留于此。\n"
    )
    if ROPE_H1 not in original:
        raise RuntimeError(
            f"Doc 19 missing expected heading: {ROPE_H1!r}; cannot place 正典 pointer"
        )
    new_content = original.replace(ROPE_H1, ROPE_H1 + pointer_block, 1)
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
         "Adobe Doc 19 Day 4 RoPE + long-context section is sole-source; canonical migrated to node (KG-M-02)"),
        ("framework_node", node_id, "company_document", DOC19_ID,
         "mentions",
         "Adobe Doc 19 retains the RoPE / long-context speed-write under the 正典 pointer (KG-M-02)"),
        ("company_document", DOC19_ID, "framework_node", node_id,
         "canonical",
         "Adobe Doc 19 Day 4 RoPE / long-context section defers to the canonical hub (KG-M-02)"),
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

        pre_migration_doc19, archive_status = _archive_pre_migration(current_doc19)
        node_id, node_status = _upsert_node(conn)
        deepdive = _build_standalone_deepdive(pre_migration_doc19).replace(
            "<NODE_ID>", str(node_id)
        )
        deepdive_status = _write_standalone(deepdive)
        patched_doc19, patch_status = _patch_doc19(conn, current_doc19, node_id)
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
        if deepdive_len < 7500:
            problems.append(
                f"standalone deep dive length {deepdive_len} < 7500 chars"
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
    print("[DONE] KG-M-02 RoPE + long context canonical migration complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
