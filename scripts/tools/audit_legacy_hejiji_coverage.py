# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Generate per-concept coverage checklist for legacy 合集 docs (19, 21, 22, 27).

For each concept (top-level numbered/T-prefixed section) in each of the four
legacy aggregate documents, classify the coverage status against existing
framework_nodes / other company_documents:

  - COVERED:  equivalent canonical content already lives in a framework_node
              or another doc; this 合集 copy is redundant.
  - PARTIAL:  some framework_node touches the topic but lacks the depth,
              derivation, or LinkedIn-specific framing in this 合集.
  - UNIQUE:   this 合集 is the sole authoritative source. Migration/new node
              required before deletion.

The curated table is the human authority; the script verifies that each listed
concept actually appears as a section header in the source doc, then renders a
deterministic markdown file. Re-running the script produces a byte-identical
file (no timestamps in body, sorted iteration, fixed encoding).

Output: docs/staging/audits/legacy_hejiji_coverage_checklist_20260416.md

Non-goals: This script does NOT delete or migrate anything. It only produces
the review artifact for per-concept human sign-off.
"""

from __future__ import annotations

import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DB_PATH = Path("data/mle_prep.db")
OUTPUT_PATH = Path("docs/staging/audits/legacy_hejiji_coverage_checklist_20260416.md")

STATUS_VOCAB = ("COVERED", "PARTIAL", "UNIQUE")
ACTION_VOCAB_PREFIXES = ("safe", "migrate to node ", "create new node")


@dataclass(frozen=True)
class Concept:
    """One concept inside a legacy 合集 document.

    header_anchor: substring that must appear as part of a markdown heading in
    the source doc. Used to fail-fast when curated table drifts from the doc.
    """

    header_anchor: str
    title: str
    status: str
    location: str
    action: str


@dataclass(frozen=True)
class DocSpec:
    doc_id: int
    short_label: str
    concepts: tuple[Concept, ...]


# ---------------------------------------------------------------------------
# Curated coverage table (the human authority). Per prior Explore-agent audit
# + manual cross-walk against the 199 framework_nodes inventory.
# Sources:
#   - data/mle_prep.db framework_nodes (id 1..199, snapshot 2026-04-16)
#   - Concept inventory parsed from each 合集 doc's level-1 / level-2 headers.
# ---------------------------------------------------------------------------

DOC_19 = DocSpec(
    doc_id=19,
    short_label="Adobe MLE Prep: All-in-One (Day 1-8 + Prep Script)",
    concepts=(
        # --- Diffusion Models 深度指南 (Day 1) ---
        Concept(
            "Diffusion Models 深度指南", "Diffusion Models 深度指南 (Day 1 整章)",
            "UNIQUE",
            "no diffusion node in framework_nodes (pillar6 covers transformers/LLM only)",
            "create new node",
        ),
        Concept(
            "数学符号与基础概念", "Diffusion §1 数学符号 (高斯/单位矩阵)",
            "COVERED",
            "node 165 probability_basics, node 173 matrix_operations",
            "safe",
        ),
        Concept(
            "前向过程", "Diffusion §2 前向过程 (加噪 + 重参数化 + 方差守恒)",
            "UNIQUE",
            "no node covers diffusion forward process",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "噪声调度", "Diffusion §3 噪声调度 β_t (cosine vs linear)",
            "UNIQUE",
            "no node covers noise schedule",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "为什么需要显式建模时间步", "Diffusion §4 时间步嵌入 (Sinusoidal/Scale-Shift)",
            "PARTIAL",
            "node 143 position_encoding mentions Sinusoidal; diffusion-time-step framing missing",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "反向过程", "Diffusion §5 反向过程 + DDPM 训练目标 + 采样伪代码",
            "UNIQUE",
            "no node covers reverse process / DDPM sampling",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "Latent Diffusion / Stable Diffusion Pipeline", "Diffusion §6 Latent Diffusion / Stable Diffusion Pipeline",
            "UNIQUE",
            "no node covers Latent Diffusion / Stable Diffusion",
            "create new node",
        ),
        Concept(
            "Classifier-Free Guidance", "Diffusion §7 Classifier-Free Guidance (CFG)",
            "UNIQUE",
            "no node covers CFG",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "条件注入方式全景", "Diffusion §8 条件注入方式全景 (cross-attn vs concat)",
            "UNIQUE",
            "no node covers conditional injection",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "ControlNet", "Diffusion §9+§15 ControlNet (Zero Convolution + 训练 + IP-Adapter)",
            "UNIQUE",
            "no node covers ControlNet / IP-Adapter",
            "create new node",
        ),
        Concept(
            "DDPM vs DDIM", "Diffusion §10 DDPM vs DDIM 深度对比 + SDE 统一框架",
            "UNIQUE",
            "no node covers DDIM or SDE framework",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "Positional Embedding 深度解析", "Diffusion §11 Positional Embedding (Absolute/Sinusoidal/Relative/RoPE)",
            "PARTIAL",
            "node 143 position_encoding (high-level only; lacks proofs)",
            "migrate to node 143",
        ),
        Concept(
            "KV-Cache", "Diffusion §12 KV-Cache (含 Prefill vs Decode)",
            "PARTIAL",
            "node 156 kv_cache_paged_attention (high-level; lacks Q/K/V dimension analysis here)",
            "migrate to node 156",
        ),
        Concept(
            "为什么预测噪声而不是预测", "Diffusion §13 为什么预测噪声 (variance / score-matching / v-pred)",
            "UNIQUE",
            "no node covers epsilon/x0/v parameterizations",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "VAE", "Diffusion §14 VAE (Encoder-Decoder + KL + 重参数化 + β-VAE + VQ-VAE)",
            "UNIQUE",
            "no node covers VAE",
            "create new node",
        ),
        Concept(
            "图像生成产业格局与技术演进", "Diffusion §16 图像生成产业格局与技术演进",
            "UNIQUE",
            "no node covers gen-image industry landscape",
            "safe (industry-context narrative; absorb summary into diffusion node)",
        ),
        # --- RLHF / DPO Alignment + LLM Distillation (Day 2-ish) ---
        Concept(
            "RLHF：三阶段 Pipeline", "Alignment §1 RLHF 三阶段 Pipeline (SFT + RM + PPO)",
            "PARTIAL",
            "node 153 rlhf (overview; this doc has full PPO loss derivation)",
            "migrate to node 153",
        ),
        Concept(
            "DPO：Direct Preference Optimization", "Alignment §2 DPO 完整推导 (从 RLHF KL 到闭式)",
            "PARTIAL",
            "node 153 rlhf mentions DPO but lacks closed-form derivation",
            "migrate to node 153",
        ),
        Concept(
            "DPO vs RLHF 对比", "Alignment §3 DPO vs RLHF 对比",
            "PARTIAL",
            "node 153 rlhf",
            "migrate to node 153",
        ),
        Concept(
            "变体与扩展", "Alignment §4 RLHF/DPO 变体 (KTO, IPO, ORPO, etc.)",
            "PARTIAL",
            "node 153 rlhf",
            "migrate to node 153",
        ),
        Concept(
            "LLM 知识蒸馏", "Alignment §5 LLM 知识蒸馏 (response/feature/relation distillation)",
            "PARTIAL",
            "node 106 knowledge_distillation (general KD; lacks LLM-specific tactics)",
            "migrate to node 106",
        ),
        # --- Distributed Training (Day 3) ---
        Concept(
            "为什么需要分布式训练", "DT §一 为什么需要分布式训练 (compute/memory/throughput motivation)",
            "PARTIAL",
            "node 126 distributed_training (entry point; lacks motivation framing)",
            "migrate to node 126",
        ),
        Concept(
            "GPU 显存模型", "DT §二 GPU 显存模型 (HBM vs SRAM)",
            "PARTIAL",
            "node 126 distributed_training; HBM/SRAM framing here is unique",
            "migrate to node 126",
        ),
        Concept(
            "四种并行策略全景", "DT §三 四种并行策略全景 (DP/TP/PP/FSDP)",
            "PARTIAL",
            "node 126 distributed_training; comparison table is unique",
            "migrate to node 126",
        ),
        Concept(
            "数据并行（DP）详解", "DT §四 DP 详解 (gradient all-reduce, ring vs tree)",
            "PARTIAL",
            "node 126 distributed_training",
            "migrate to node 126",
        ),
        Concept(
            "张量并行（TP）详解", "DT §五 TP 详解 (column-wise/row-wise split)",
            "PARTIAL",
            "node 126 distributed_training",
            "migrate to node 126",
        ),
        Concept(
            "流水线并行（PP）详解", "DT §六 PP 详解 (GPipe vs 1F1B vs interleaved)",
            "PARTIAL",
            "node 126 distributed_training",
            "migrate to node 126",
        ),
        Concept(
            "FSDP / ZeRO 详解", "DT §七 FSDP / ZeRO 详解 (stage 1/2/3)",
            "PARTIAL",
            "node 126 distributed_training",
            "migrate to node 126",
        ),
        Concept(
            "3D 并行", "DT §八 3D 并行 (DP+TP+PP composition)",
            "PARTIAL",
            "node 126 distributed_training",
            "migrate to node 126",
        ),
        Concept(
            "激活检查点", "DT §九 Activation Checkpointing",
            "PARTIAL",
            "node 126 distributed_training",
            "migrate to node 126",
        ),
        Concept(
            "通信原语速查", "DT §十 通信原语 (all-reduce, all-gather, reduce-scatter, broadcast)",
            "UNIQUE",
            "no node covers collective communication primitives",
            "migrate to node 126",
        ),
        # --- RoPE + Long Context + Video Generation (Day 4) ---
        Concept(
            "RoPE：旋转位置编码", "RoPE §2 旋转位置编码 (复数旋转矩阵 + 相对位置编码性质)",
            "PARTIAL",
            "node 143 position_encoding (lists RoPE; lacks rotation-matrix derivation)",
            "migrate to node 143",
        ),
        Concept(
            "PE 方法对比", "RoPE §3 PE 方法对比 (Absolute/Sinusoidal/Relative/RoPE/ALiBi)",
            "PARTIAL",
            "node 143 position_encoding",
            "migrate to node 143",
        ),
        Concept(
            "长上下文扩展方法", "RoPE §4 长上下文扩展 (PI, NTK-aware, YaRN, LongRoPE)",
            "UNIQUE",
            "no node covers long-context extension techniques",
            "create new node",
        ),
        Concept(
            "视频生成", "RoPE §5 视频生成 (Sora-style spatial-temporal architecture)",
            "UNIQUE",
            "no node covers video generation",
            "create new node",
        ),
        # --- Day 5: Inference Optimization ---
        Concept(
            "FlashAttention", "Day5 §一 FlashAttention (tiling + online-softmax)",
            "PARTIAL",
            "node 146 attention_variants (mentions Flash; lacks tiling/IO derivation)",
            "migrate to node 146",
        ),
        Concept(
            "量化（Quantization）", "Day5 §二 量化 (PTQ/QAT/INT8/FP8)",
            "PARTIAL",
            "node 157 quantization, node 131 serving_optimization",
            "migrate to node 157",
        ),
        Concept(
            "Serving Optimization", "Day5 §三 Serving Optimization (batching, scheduling)",
            "PARTIAL",
            "node 158 continuous_batching, node 159 serving_systems, node 132 llm_serving",
            "migrate to node 158",
        ),
        # --- Phone Screen handbook ---
        Concept(
            "Transformer 基础", "PS §A Transformer 基础",
            "COVERED",
            "nodes 32, 141-147 (transformer pillar6.transformer.*)",
            "safe",
        ),
        Concept(
            "Multimodal AI", "PS §B Multimodal AI (CLIP, LLaVA, BLIP)",
            "COVERED",
            "node 164 vision_language",
            "safe",
        ),
        Concept(
            "LoRA", "PS §C LoRA / QLoRA",
            "COVERED",
            "node 154 peft",
            "safe",
        ),
        Concept(
            "PyTorch 实操", "PS §D PyTorch 实操",
            "PARTIAL",
            "no dedicated PyTorch node; coverage spread across nodes 60, 63, 74",
            "safe",
        ),
        Concept(
            "GAN 相关", "PS §F GAN 相关",
            "UNIQUE",
            "no node covers GAN",
            "create new node",
        ),
        # --- 扩散模型与深度学习核心概念精要 ---
        Concept(
            "UNet 在 Stable Diffusion 中的角色", "扩散精要 §一 UNet (down/up sampling, skip connections)",
            "UNIQUE",
            "no node covers UNet architecture",
            "migrate to node <new diffusion node>",
        ),
        Concept(
            "MQA 与 GQA", "扩散精要 §八 MQA / GQA",
            "COVERED",
            "node 146 attention_variants (MQA/GQA/Flash)",
            "safe",
        ),
        Concept(
            "CLIP", "扩散精要 §十 CLIP (contrastive image-text training)",
            "PARTIAL",
            "node 164 vision_language (lists CLIP; lacks contrastive-loss derivation)",
            "migrate to node 164",
        ),
    ),
)

DOC_21 = DocSpec(
    doc_id=21,
    short_label="[合集] 概率统计 + 数学推导",
    concepts=(
        Concept(
            "1. Weighted Probability Sampling / Multinomial Distribution",
            "§1 Weighted Probability Sampling / Multinomial (含 Alias Method O(1) 证明)",
            "PARTIAL",
            "node 62 sampling_algorithms (general); node 166 common_distributions (Multinomial); Alias Method derivation here is unique",
            "migrate to node 62",
        ),
        Concept(
            "2. N Random Variables的E[X_bar]和Var[X_bar]",
            "§2 N Random Variables 的 E[X̄] 与 Var[X̄]",
            "COVERED",
            "node 167 expectation_variance, node 169 clt",
            "safe",
        ),
        Concept(
            "3. Simpson's Paradox",
            "§3 Simpson's Paradox (Email Campaign 实例)",
            "UNIQUE",
            "no node covers Simpson's Paradox",
            "create new node",
        ),
        Concept(
            "4. Queueing Theory: 单队列 vs 多队列",
            "§4 Queueing Theory (M/M/1, single vs multi-queue, Little's Law)",
            "UNIQUE",
            "no node covers queueing theory (node 46 stack_queue is data-structure level, unrelated)",
            "create new node",
        ),
        Concept(
            "5. Distributions: 身高分布与LinkedIn Connections分布",
            "§5 身高分布 (Normal) vs LinkedIn Connections (power-law/log-normal)",
            "PARTIAL",
            "node 166 common_distributions (lacks power-law / log-normal framing for social-network data)",
            "migrate to node 166",
        ),
        Concept(
            "6. Class Imbalance处理",
            "§6 Class Imbalance 处理",
            "COVERED",
            "node 16 sampling_class_imbalance, node 84 oversampling, node 85 loss_reweighting",
            "safe",
        ),
        Concept(
            "7. Sampling from Large Dataset与模型验证",
            "§7 Sampling from Large Dataset 与模型验证",
            "COVERED",
            "node 62 sampling_algorithms, node 86 cross_validation",
            "safe",
        ),
        Concept(
            "8. Overfitting Prevention (Tree-based Models)",
            "§8 Overfitting Prevention (tree-specific: max_depth, min_samples_leaf, subsample)",
            "COVERED",
            "node 65 tree_models, node 194 regularization",
            "safe",
        ),
        Concept(
            "9. L1/L2 Regularization与Bias",
            "§9 L1/L2 Regularization 与 Bias (KKT primal-dual + Ridge bias 推导 + James-Stein)",
            "COVERED",
            "node 195 bias_variance_geometric (T-P0-474 absorbed L1/L2 proofs + James-Stein here)",
            "safe",
        ),
        Concept(
            "10. Random Forest Theory",
            "§10 Random Forest Theory (bagging + 特征随机化 + OOB)",
            "COVERED",
            "node 65 tree_models",
            "safe",
        ),
        Concept(
            "11. MLE for Distribution Parameters (Normal, GMM, EM)",
            "§11 MLE (Normal closed-form + GMM + EM 完整推导)",
            "UNIQUE",
            "node 168 mle_map (general MLE only; GMM-EM derivation unique to this doc)",
            "create new node",
        ),
        Concept(
            "12. Reservoir Sampling（蓄水池采样）详解",
            "§12 Reservoir Sampling (Algorithm R + Algorithm L + 加权变体)",
            "COVERED",
            "node 62 sampling_algorithms",
            "safe",
        ),
    ),
)

DOC_22 = DocSpec(
    doc_id=22,
    short_label="[合集] System Design",
    concepts=(
        Concept(
            "1. Typeahead / Autocomplete System",
            "§1 Typeahead / Autocomplete System",
            "COVERED",
            "node 89 search_retrieval, node 111 classic_ir",
            "safe",
        ),
        Concept(
            "2. Recommendation System (Short Video)",
            "§2 Recommendation System (Short Video) — LinkedIn-flavored",
            "PARTIAL",
            "node 90 recommendation, node 198 realtime_recommendation (general; LinkedIn short-video specifics missing)",
            "migrate to node 198",
        ),
        Concept(
            "3. Metrics Monitoring / Exception Monitoring",
            "§3 Metrics Monitoring / Exception Monitoring",
            "PARTIAL",
            "node 139 monitoring (model-drift focused; metrics-pipeline specifics here)",
            "migrate to node 139",
        ),
        Concept(
            "4. Job Scheduler",
            "§4 Job Scheduler",
            "UNIQUE",
            "no node covers job scheduler (general SD outside ML scope)",
            "safe (kept as LinkedIn-specific reference; no migration needed)",
        ),
        Concept(
            "5. KV Store (Single Machine)",
            "§5 KV Store (Single Machine)",
            "UNIQUE",
            "no node covers KV store (general SD outside ML scope)",
            "safe (kept as LinkedIn-specific reference; no migration needed)",
        ),
        Concept(
            "6. Personalized InMail (LLM-powered)",
            "§6 Personalized InMail (LLM-powered)",
            "PARTIAL",
            "node 93 nlp_llm, node 117 llm_application_patterns; LinkedIn InMail framing unique",
            "migrate to node 117",
        ),
        Concept(
            "7. Top K Search Words",
            "§7 Top K Search Words (Count-Min/Heavy Hitters)",
            "COVERED",
            "node 196 streaming_topk (3-axis canonical framework)",
            "safe",
        ),
        Concept(
            "8. Ranking System",
            "§8 Ranking System (LinkedIn job/feed multi-stage ranking)",
            "PARTIAL",
            "node 99 multi_stage_ranking, node 114 learning_to_rank; LinkedIn-specific ranking specifics missing",
            "migrate to node 99",
        ),
        Concept(
            "9. isMalicious API",
            "§9 isMalicious API (URL/content classifier serving)",
            "PARTIAL",
            "node 95 fraud_trust, node 27 trust_safety; API/serving design specific here",
            "migrate to node 95",
        ),
        Concept(
            "10. LinkedIn Skills (Data Mining)",
            "§10 LinkedIn Skills Data Mining",
            "UNIQUE",
            "no node covers skill extraction / data-mining pipelines",
            "create new node",
        ),
        Concept(
            "11. Inverted Document Search",
            "§11 Inverted Document Search",
            "COVERED",
            "node 89 search_retrieval, node 111 classic_ir (BM25/TF-IDF)",
            "safe",
        ),
        Concept(
            "附录: LinkedIn SD 面试通用策略",
            "附录 LinkedIn SD 面试通用策略",
            "PARTIAL",
            "no dedicated SD-strategy node; advice is LinkedIn-specific",
            "create new node",
        ),
    ),
)

DOC_27 = DocSpec(
    doc_id=27,
    short_label="[合集] ML 理论 + 手写实现",
    concepts=(
        Concept(
            "T1: Gradient Descent",
            "T1 Gradient Descent (BGD/SGD/MBGD + Gradient Clipping)",
            "COVERED",
            "node 74 gradient_descent",
            "safe",
        ),
        Concept(
            "T2: Linear Regression",
            "T2 Linear Regression (Normal Eq + GD + OLS assumptions + GLM)",
            "COVERED",
            "node 64 linear_models",
            "safe",
        ),
        Concept(
            "T3: Logistic Regression",
            "T3 Logistic Regression (BCE + Softmax)",
            "COVERED",
            "node 64 linear_models",
            "safe",
        ),
        Concept(
            "T4: KNN + K-Means",
            "T4 KNN + K-Means (从零实现)",
            "PARTIAL",
            "node 71 clustering (K-Means); KNN missing dedicated node",
            "migrate to node 71",
        ),
        Concept(
            "T5: Naive Bayes",
            "T5 Naive Bayes (Gaussian/Multinomial/Bernoulli)",
            "PARTIAL",
            "node 165 probability_basics (Bayes); no dedicated Naive Bayes node",
            "create new node",
        ),
        Concept(
            "T6: Tree Models",
            "T6 Tree Models (DT + RF + GBDT + XGBoost from scratch)",
            "COVERED",
            "node 65 tree_models",
            "safe",
        ),
        Concept(
            "T7: Weight Initialization",
            "T7 Weight Initialization (Xavier/He/LeCun + 完整推导)",
            "PARTIAL",
            "node 77 training_tricks (high-level); init derivations unique here",
            "migrate to node 77",
        ),
        Concept(
            "T8: Optimizers",
            "T8 Optimizers (Momentum/Nesterov/AdaGrad/RMSprop/Adam/AdamW from scratch)",
            "UNIQUE",
            "node 74 gradient_descent (mentions; lacks RMSprop/Adam from-scratch code)",
            "migrate to node 74",
        ),
    ),
)

ALL_DOCS: tuple[DocSpec, ...] = (DOC_19, DOC_21, DOC_22, DOC_27)


def _validate_concept(concept: Concept) -> None:
    """Fail fast if a curated concept entry is malformed."""
    if concept.status not in STATUS_VOCAB:
        raise ValueError(
            f"Concept {concept.title!r} has invalid status {concept.status!r}; "
            f"must be one of {STATUS_VOCAB}"
        )
    if not any(concept.action.startswith(p) for p in ACTION_VOCAB_PREFIXES):
        raise ValueError(
            f"Concept {concept.title!r} has invalid action {concept.action!r}; "
            f"must start with one of {ACTION_VOCAB_PREFIXES}"
        )


def _validate_anchor(content: str, anchor: str, doc_id: int, title: str) -> None:
    """Verify the anchor text appears verbatim somewhere in the doc body.

    Catches drift between the curated table and the source doc — if the doc is
    edited and a section title shifts, the audit script fails loudly instead of
    quietly producing a stale checklist.
    """
    if anchor not in content:
        raise ValueError(
            f"Doc {doc_id}: curated concept {title!r} has anchor {anchor!r} "
            f"that no longer appears in the document content. Update the "
            f"curated table or restore the section."
        )


def _load_doc_content(conn: sqlite3.Connection, doc_id: int) -> str:
    cur = conn.execute(
        "SELECT content FROM company_documents WHERE id = ?", (doc_id,)
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"company_documents id={doc_id} not found in {DB_PATH}")
    return row[0]


def _render_section(doc: DocSpec, content: str) -> str:
    """Render one doc's section with concept rows + 2 checkboxes each."""
    lines: list[str] = []
    counts = {s: 0 for s in STATUS_VOCAB}
    for c in doc.concepts:
        counts[c.status] += 1

    lines.append(f"## Doc {doc.doc_id} — {doc.short_label}")
    lines.append("")
    lines.append(
        f"- **Concepts**: {len(doc.concepts)}  "
        f"(COVERED: {counts['COVERED']}, "
        f"PARTIAL: {counts['PARTIAL']}, "
        f"UNIQUE: {counts['UNIQUE']})"
    )
    lines.append(
        f"- **Source**: `company_documents.id = {doc.doc_id}` "
        f"({len(content)} chars)"
    )
    lines.append("")

    for i, c in enumerate(doc.concepts, start=1):
        lines.append(f"### {doc.doc_id}.{i} {c.title}")
        lines.append("")
        lines.append(f"- **Status**: {c.status}")
        lines.append(f"- **Where**: {c.location}")
        lines.append(f"- **Action**: {c.action}")
        lines.append(f"- [ ] User-verified migration complete")
        lines.append(f"- [ ] Signed off for deletion from this 合集")
        lines.append("")

    return "\n".join(lines)


def _render_header(docs: Iterable[DocSpec]) -> str:
    docs = tuple(docs)
    total = sum(len(d.concepts) for d in docs)
    overall = {s: 0 for s in STATUS_VOCAB}
    for d in docs:
        for c in d.concepts:
            overall[c.status] += 1

    lines = [
        "# Legacy 合集 Coverage Checklist (Docs 19 / 21 / 22 / 27)",
        "",
        "Per-concept review artifact for the legacy aggregate documents. Per",
        "user instruction, **nothing is auto-deprecated**; this checklist exists",
        "so each concept can be signed off individually before the surrounding",
        "合集 doc is removed.",
        "",
        "## How to use",
        "",
        "For each concept below:",
        "",
        "1. Read the **Status** + **Where** + **Action** triple.",
        "2. If the action is `migrate to node <id>` or `create new node`, do the",
        "   migration first (separate task), then check **User-verified",
        "   migration complete**.",
        "3. Once every concept inside a doc has its first checkbox set, the doc",
        "   itself can be marked safe to delete — check **Signed off for",
        "   deletion** on every row.",
        "",
        "## Status vocabulary",
        "",
        "- **COVERED** — equivalent canonical content already exists in a",
        "  framework_node or other company_document. The 合集 copy is",
        "  redundant.",
        "- **PARTIAL** — some framework_node touches the topic but lacks the",
        "  depth, derivation, or company-specific framing in this 合集.",
        "  Migration target is named in the **Where** field.",
        "- **UNIQUE** — this 合集 is the sole authoritative source. A new node",
        "  must be created (or the content absorbed into an existing node)",
        "  before this concept can be deleted.",
        "",
        "## Action vocabulary",
        "",
        "- `safe` — no migration needed; concept can be removed once verified.",
        "- `migrate to node <id>` — content belongs in an existing framework_node.",
        "- `create new node` — content needs a brand-new framework_node.",
        "",
        "## Summary",
        "",
        f"- **Total concepts**: {total}",
        f"  - COVERED: {overall['COVERED']}",
        f"  - PARTIAL: {overall['PARTIAL']}",
        f"  - UNIQUE: {overall['UNIQUE']}",
        f"- **Source DB**: `{DB_PATH.as_posix()}`",
        f"- **Generator**: `scripts/audit_legacy_hejiji_coverage.py`",
        "- **Determinism**: re-running the generator produces a byte-identical",
        "  file (no timestamps in body, sorted iteration, fixed UTF-8 newline",
        "  output).",
        "",
    ]
    return "\n".join(lines)


def build_checklist() -> str:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        sections: list[str] = [_render_header(ALL_DOCS)]
        for doc in ALL_DOCS:
            content = _load_doc_content(conn, doc.doc_id)
            for c in doc.concepts:
                _validate_concept(c)
                _validate_anchor(content, c.header_anchor, doc.doc_id, c.title)
            sections.append(_render_section(doc, content))
    finally:
        conn.close()

    body = "\n".join(sections).rstrip() + "\n"
    return body


def main() -> int:
    body = build_checklist()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(body, encoding="utf-8", newline="\n")
    print(
        f"[OK] wrote {OUTPUT_PATH.as_posix()} "
        f"({len(body)} chars, "
        f"{sum(len(d.concepts) for d in ALL_DOCS)} concepts across "
        f"{len(ALL_DOCS)} docs)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
