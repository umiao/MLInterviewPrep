"""T-P2-458: Generative Models Pitch for Pinterest (restrained, pitch-only).

Seeds ONE Pinterest company_document (doc_kind=prep_note) titled
"Generative Models Pitch for Pinterest" covering:
  (1) A single comparison table: GAN / VAE / Diffusion across the axes
      {core mechanism, failure mode, inference speed, SOTA quality}.
  (2) One paragraph per Pinterest use case:
      - Pin image generation (creator assist, data aug for long-tail categories)
      - Style transfer for boards (board-level aesthetic consistency)
      - Visual-search result augmentation (retrieval diversity, query expansion)
  (3) Paper citations only; NO ELBO re-derivation, NO DDPM sampling derivation.
  (4) NO new framework_node created (pitch-level, avoids tree bloat at P2).

Idempotent: upserts by (company_id=29, title).

Usage::

    python scripts/seed_pinterest_generative_pitch_20260416.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"

PINTEREST_COMPANY_ID = 29
DOC_TITLE = "Generative Models Pitch for Pinterest"


# ==========================================================================
# Doc content
# ==========================================================================

def build_doc() -> str:
    b = StudyNoteBuilder()
    b.set_title("Generative Models Pitch for Pinterest (GAN / VAE / Diffusion)")

    b.add_prerequisites([
        "基础概率 + Gaussian prior (不在此文档重推)",
        "VAE ELBO、DDPM forward/reverse 的结论级熟悉 (细节见引用论文)",
        "Pinterest 视觉塔落地直觉 (ResNet / EfficientNet + embedding 消费者)",
    ])

    b.add_term("GAN", "Generative Adversarial Network (Goodfellow et al. 2014)",
        "generator-discriminator 博弈；单次前向采样极快，易 mode collapse")
    b.add_term("VAE", "Variational Auto-Encoder (Kingma & Welling 2013)",
        "encoder-decoder + ELBO；latent 空间连续利于插值，样本偏糊")
    b.add_term("DDPM", "Denoising Diffusion Probabilistic Model (Ho et al. 2020)",
        "前向加噪 + 学去噪；样本 SOTA 但 1000 步采样慢")
    b.add_term("DDIM", "Denoising Diffusion Implicit Model (Song et al. 2020)",
        "Diffusion 的确定性跳步采样器，10~50 步可出样，是\"慢\"痛点的工程解")
    b.add_term("LDM", "Latent Diffusion Model (Rombach et al. 2022)",
        "把 diffusion 搬到 VAE 压缩过的 latent 空间；Stable Diffusion 的底层范式")
    b.add_term("FID", "Frechet Inception Distance",
        "对比真实图像与生成图像在 Inception 特征上的 Gaussian 矩差；越低越好")
    b.add_term("CFG", "Classifier-Free Guidance (Ho & Salimans 2022)",
        "Diffusion 条件采样增强：同时训有/无条件两个分支，采样时外推放大条件影响")

    # ------------------------------------------------------------------
    # Single unified comparison table (the "one table" AC calls for)
    # ------------------------------------------------------------------
    b.add_comparison_table(
        headers=[
            "维度", "**GAN**", "**VAE**", "**Diffusion (DDPM / LDM)**",
        ],
        rows=[
            [
                "核心机制",
                "generator vs discriminator 对抗 (minimax)",
                "encoder q(z|x) + decoder p(x|z)，优化 ELBO",
                "前向加噪 T 步 -> 学反向去噪网络 eps_theta",
            ],
            [
                "训练稳定性",
                "**脆弱**：两网络博弈易震荡 / 崩塌",
                "**稳定**：单一 ELBO，重构 + KL 两项",
                "**稳定**：回归 MSE 于噪声，超参鲁棒",
            ],
            [
                "典型失败",
                "**mode collapse** (只生成少数模式)",
                "**输出偏糊** (像素 MSE + Gaussian 解码器的固有代价)",
                "**采样慢** (DDPM 1000 步)；DDIM/LCM 已大幅缓解",
            ],
            [
                "采样速度",
                "**一次前向极快** (~ms 级)",
                "**一次前向极快** (~ms 级)",
                "原生慢 (秒级)；**DDIM 20~50 步** 或 LCM ~4 步可达 ~100ms",
            ],
            [
                "样本质量 (FID)",
                "风格化/人脸 SOTA 过 (StyleGAN)；类内多样性弱",
                "低分辨率 OK；高分辨率质量明显输给 GAN / Diffusion",
                "**当前 SOTA** (文本到图、类别到图、条件生成普遍领先)",
            ],
            [
                "可控性",
                "latent 可编辑 (StyleGAN W+)，但条件注入较硬",
                "latent 插值天然，文本条件需额外对齐",
                "CFG + cross-attention 让**文本/条件控制最灵活**",
            ],
            [
                "Pinterest 落地偏好",
                "轻量风格迁移、历史资产 (StyleGAN 工具链)",
                "embedding 辅助 / 压缩到 latent 供下游消费",
                "**主力生成路径** (LDM + CFG + LoRA 做 Pin 样式/布局)",
            ],
        ],
        title="1. 一张对比表 (pitch-level, 不展开推导)",
    )

    b.add_section("1.1 补充要点 (面试口述时 3 句带过)", [
        (
            "- **三者共享 evidence**：都在学 `p_theta(x)` 的近似；GAN 用隐式采样器，"
            "VAE 用显式 likelihood 下界，Diffusion 用分数匹配等价的去噪目标。"
        ),
        (
            "- **当前工程现状**：Pinterest 量级的图像生成业务线**默认走 LDM (Stable Diffusion)"
            " + LoRA + ControlNet** 的组合 (2022-2024 行业共识)；GAN 工具链仍在**风格化、"
            "人像增强**这类窄场景里活着；纯 VAE 现在基本只在\"压 latent 给 diffusion 用\""
            "这个角色里出现。"
        ),
        (
            "- **不展开的承诺**：ELBO 推导见 Kingma & Welling 2013 §2；DDPM forward/reverse "
            "参数化见 Ho et al. 2020 §2~§3；本文档不重复推导，面试官问再拉白板。"
        ),
    ])

    # ------------------------------------------------------------------
    # Use-case paragraphs (the three AC-required paragraphs)
    # ------------------------------------------------------------------
    b.add_section("2. Pinterest Use Case 1: Pin 图像生成 (creator assist + long-tail aug)", [
        (
            "**定位**：面向 creator 的\"AI 出图助手\" + 面向平台的\"长尾类目数据增广\"。"
            "落地架构是 **LDM (Stable Diffusion 基座) + Pinterest 内部图像集 fine-tune + LoRA "
            "adapter 叠风格**：base 模型承担文本理解和通用图像 prior；fine-tune 让分布对齐 Pin "
            "特有的构图 (top-down 俯视、生活化布景、文字少)；LoRA 做 per-segment 样式 (家居、"
            "手工、食物) 的轻量切换。采样侧用 **CFG scale 7~8 + DDIM 20~50 步**，QPS 压力"
            "通过 **latent 缓存 + 文本 embedding 缓存** 缓解。数据增广侧：长尾类目 (冷门 DIY 手工) "
            "用 diffusion 合成 Pin 补充训练集，显著改善 **shop-the-look** 和广告分类器的 "
            "tail AUC；关键约束是**合成 Pin 进训练前要跑 detector 过滤**，防止 hallucinated 物体"
            "污染 embedding 塔的正样本对 (引流到 T-P2-459 unsafe-content 任务)。"
            "参考：Rombach et al. 2022 (Latent Diffusion)、Hu et al. 2021 (LoRA)、Ho & Salimans 2022 (CFG)。"
        ),
    ])

    b.add_section("3. Pinterest Use Case 2: Board 级风格迁移 (aesthetic consistency)", [
        (
            "**定位**：用户把多张 Pin 聚到一个 board 想表达一致美学 (e.g. \"Scandinavian 客厅\")，"
            "平台可以做**两件事**：(a) **推荐侧**——把 board 已有 Pin 的视觉塔 embedding 聚合，"
            "再用风格相似召回补齐；(b) **生成侧**——给 creator 一键\"让这张 Pin 匹配 board 风格\"。"
            "生成侧的技术路径有两条：**GAN 系 (StyleGAN + style mixing)** 适合稳定、已有强 style "
            "先验的窄风格迁移 (历史项目沉淀的工具链仍有价值)；**Diffusion 系 (img2img + IP-Adapter "
            "/ ControlNet)** 适合开放式风格迁移，**控制力和泛化力都显著更强**。Pinterest 规模下"
            "新项目**偏向 diffusion**：IP-Adapter 把 board 内代表 Pin 的 CLIP embedding 作为"
            "视觉条件注入，ControlNet 保持原 Pin 的布局/姿态，最终兼顾\"保持结构 + 换风格\"。"
            "参考：Karras et al. 2019 (StyleGAN2)、Ye et al. 2023 (IP-Adapter)、Zhang et al. 2023 (ControlNet)。"
        ),
    ])

    b.add_section("4. Pinterest Use Case 3: 视觉搜索结果增广 (retrieval diversity + query expansion)", [
        (
            "**定位**：query Pin 召回 top-K 时常见两类痛点——(a) **多样性不足** (top-K 同构)、"
            "(b) **长尾 query 召回稀疏**。生成模型的角色是\"给检索侧造可搜的视觉候选\"而不是替代"
            "检索本身。**做法**：(1) **Query expansion**——对 query Pin 做 diffusion img2img "
            "(低 strength, e.g. 0.2~0.4) 生成 N 个风格微扰变体，每个变体走同一视觉塔做 ANN 检索，"
            "并集后再融合重排，**在不换模型的前提下提升召回多样性**；(2) **Tail catalog 补齐**——"
            "对检索不足的小类目用 diffusion 合成虚拟\"种子 Pin\"，embedding 进 ANN 索引只做"
            "**召回 rehearsal** (不进最终展示)，引导真实 Pin 浮现。**关键红线**：生成图**永远不**"
            "直接展示给用户，只当 query 端的数据增广；合成图也要打标为合成，monitoring 面板追踪"
            "它们在 shown CTR 里的占比长期归零 (引流到 T-P2-460 responsible AI 监控任务)。"
            "参考：Rombach et al. 2022 (LDM)、Radford et al. 2021 (CLIP for cross-modal retrieval)。"
        ),
    ])

    # ------------------------------------------------------------------
    # Compact interview QA (keep short — pitch-only doc)
    # ------------------------------------------------------------------
    b.add_interview_qa(
        "Pinterest 要上生成式模型，GAN / VAE / Diffusion 你默认选谁？",
        (
            "**默认 diffusion (LDM)**。理由三条：(1) 条件可控性 (CFG + cross-attention + "
            "ControlNet/IP-Adapter) 显著强于 GAN 和 VAE；(2) 训练稳定，LoRA 微调门槛低，"
            "适配 Pinterest 多品类多风格；(3) 采样慢的痛点有 DDIM/LCM 工程解，不再是阻塞。"
            "**GAN 保留场景**：窄风格化、已有 StyleGAN 资产的任务。"
            "**VAE 保留场景**：只当 LDM 的 latent encoder，不单独承担生成。"
        ),
    )
    b.add_interview_qa(
        "生成图直接展示给 Pinterest 用户有什么红线？",
        (
            "**三条红线**：(a) **unsafe content** (NSFW / 暴力 / 版权) 必须过 detector 才能"
            "进任何 user-facing 链路 (对接 T-P2-459)；(b) **合成标识**——展示侧需要 badge"
            " 或水印，符合 FTC / EU AI Act 的合成披露义务；(c) **反馈回路防污染**——合成图"
            "收集到的 CTR/save 信号若回流训练数据，会强化 hallucination，必须在 feature "
            "pipeline 隔离 (对接 T-P2-460 monitoring)。工程默认：**generative 只做 "
            "creator-side tool 和 retrieval-side 增广**，最终展示给用户的图优先用真实 Pin。"
        ),
    )

    # ------------------------------------------------------------------
    # Compact checklist
    # ------------------------------------------------------------------
    b.add_checklist("Pitch-Level Self-Check", [
        "一句话说清 GAN / VAE / Diffusion 的核心机制差异 (对抗 / ELBO / 去噪)",
        "能讲 3 种典型失败模式 (mode collapse / 糊 / 慢) 及对应工程解",
        "能给 Pinterest 3 个 use case 配 paper 名，不展开 ELBO / DDPM 推导",
        "能讲 LDM 为什么是当前工业默认 (稳定 + 可控 + LoRA 生态)",
        "能主动提 responsible AI 红线：unsafe / 合成标识 / 反馈回路污染",
    ])

    return b.build()


# ==========================================================================
# DB helpers (match T-P1-453 pattern)
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


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    content = build_doc()
    warns = StudyNoteBuilder.validate(content)
    for w in warns:
        print(f"[WARN] {w}")

    length = len(content)
    # Rough word count (zh char + en word). AC cap: <=1500 words ~= <=9000 bytes
    # of mixed zh/en. Use a loose bound.
    print(f"[BUILT] generative pitch doc length={length} chars")
    if length > 9500:
        print(
            f"[WARN] length={length} exceeds loose 9500-char cap "
            "(AC: <=1500 words pitch-only)"
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
        conn.commit()
    finally:
        conn.close()

    print("[DONE] Pinterest generative-models pitch seed complete")


if __name__ == "__main__":
    main()
