"""T-P2-459: Pinterest SD gap-fill -- unsafe multimodal + query expansion.

Seeds ONE Pinterest company_document (doc_kind=prep_note) titled
"Pinterest SD Gap-Fill: Unsafe Multimodal + Query Expansion" covering two
interview-known gaps at PITCH level (not code / not full design):

  (A) Unsafe content detection (image + text multimodal)
      - Early fusion vs late fusion trade-off
      - Modality dropout during training (handle missing captions / stripped alt-text)
      - Asymmetric confidence thresholds (ship only SFW-confident; flag borderline)
      - Human-in-loop rules (escalation, label feedback, calibration)

  (B) Query expansion for recall boost -- without changing ranking algo
      - SynSet / synonym lookup (taxonomy-driven)
      - Query rewriting via small LLM (paraphrase, spelling normalize, intent)
      - Embedding-based query-to-query similarity (ANN over past-query embeddings)
      - Click-driven expansion (co-click -> pseudo-synonyms)
      - Cross-link to Pinterest Sketch/Streaming doc (id=58) for ANN context

Idempotent: upserts by (company_id=29, title).

NO new framework_node. NO code snippets beyond config-level pseudo-config.
Pyramid top: <=3000 words. Paper / system references by name only.

Usage::

    python scripts/seed_pinterest_sd_gap_fill_20260416.py
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
DOC_TITLE = "Pinterest SD Gap-Fill: Unsafe Multimodal + Query Expansion"
SKETCH_DOC_ID = 58  # "Pinterest Sketch/Streaming Theory 1-Pager"


# ==========================================================================
# Doc content
# ==========================================================================

def build_doc() -> str:
    b = StudyNoteBuilder()
    b.set_title("Pinterest SD Gap-Fill: Unsafe Multimodal + Query Expansion")

    b.add_prerequisites([
        "Pinterest visual+text tower 直觉 (CLIP / 双塔 embedding)",
        "ANN 检索基础 (HNSW / IVF-PQ，细节见 doc 58 Sketch/Streaming)",
        "Precision/Recall + PR-AUC 对 imbalanced 任务的读数",
        "基础 transformer cross-attention (此文不再推)",
    ])

    b.add_term("SFW", "Safe For Work",
        "平台可展示内容；该 doc 里所有 unsafe 预测都以 SFW 为参照类")
    b.add_term("NSFW", "Not Safe For Work",
        "unsafe 伞状标签；Pinterest 细分到 porn / violence / self-harm / drug / hate 等多头")
    b.add_term("CLIP", "Contrastive Language-Image Pretraining (Radford 2021)",
        "文本塔 + 图像塔对比学习，Pinterest unsafe / retrieval 的标配 backbone")
    b.add_term("SynSet", "Synonym Set",
        "taxonomy 里同义词组；此 doc 用于 query expansion 的规则式召回")
    b.add_term("ANN", "Approximate Nearest Neighbor",
        "HNSW / IVF-PQ 召回；query-to-query 和 query-to-pin 都依赖它")
    b.add_term("HIL", "Human-in-the-Loop",
        "borderline 预测 -> 人审 queue；审核结果回流训练 / 校准")
    b.add_term("PSI", "Population Stability Index",
        "输入分布漂移监控；unsafe 模型上线后必须跑 (见 T-P2-460)")

    # ==================================================================
    # SECTION A -- UNSAFE CONTENT (image + text multimodal)
    # ==================================================================
    b.add_section("A. Unsafe Content Detection (image + text multimodal)", [
        (
            "**定位 (pitch)**：Pinterest 每张 Pin 同时带**图像** (缩略图 / 原图) 和**文本** "
            "(title、description、board name、creator 上传 tag)。unsafe 检测必须吃这两路，"
            "单模态都有盲区：纯图模型漏掉文字挑衅 / 钓鱼文案配无害图；纯文模型漏掉图里的违规"
            "视觉元素。下面只讨论**融合策略 + 训练技巧 + 上线决策**，**不重推** CLIP loss / "
            "transformer attention。"
        ),
    ])

    b.add_comparison_table(
        headers=["维度", "**Early Fusion**", "**Late Fusion**", "**Hybrid / Cross-Attn**"],
        rows=[
            [
                "融合位置",
                "在**特征层**拼接 (image_emb concat text_emb) -> 一个分类头",
                "每模态**各自出 logit / prob**，再加权 / 规则合并",
                "**cross-attention** 让 text token 看 image patch (或反之)",
            ],
            [
                "表达力",
                "中等：早期交互学到跨模态关联",
                "**弱**：模态间无直接交互，只在决策层叠加",
                "**最强**：token 级细粒度交互 (e.g. ALBEF / BLIP 风格)",
            ],
            [
                "训练数据需求",
                "需对齐良好的 image-text pair",
                "**低**：两模态可独立训再上线拼",
                "**高**：cross-attention 要足够多样本防 overfit",
            ],
            [
                "缺失模态鲁棒性",
                "**脆**：text 缺 -> embedding 置零 / 噪声",
                "**强**：text 缺就走纯图分支",
                "中：需要训练时显式 modality dropout (下文)",
            ],
            [
                "解释性",
                "弱 (单一黑盒 logit)",
                "**强**：可看每模态 confidence，写规则",
                "中：attention map 可可视化但非 faithful",
            ],
            [
                "Pinterest 落地偏好",
                "Early: MVP / 低 traffic 类目",
                "**Late: 主力**，因为缺失文本极常见 + 合规团队要可解释",
                "Hybrid: 头部类目 (porn / self-harm) 高召回场景",
            ],
        ],
        title="A.1 三种融合策略对比 (不展开模型结构)",
    )

    b.add_section("A.2 结论：Pinterest 默认 Late Fusion + 头部类目 Hybrid", [
        (
            "工程默认是**两段式**：(1) **image-only head** (ResNet / ViT + 多头 NSFW 细分类)、"
            "**text-only head** (多语言 encoder，e.g. XLM-R / E5-small) 各自出 per-label "
            "prob；(2) **融合层**：规则 + 轻量 MLP 吃两路 logits + 少量 metadata (creator "
            "reputation、board NSFW 历史、上传渠道)。这一路的**主要好处是合规可解释**：审核团队"
            "能直接看到\"图方无风险但文案触发 drug\"这种具体原因。**头部高风险类目** (porn、"
            "self-harm、CSAM) 另跑一条**cross-attention hybrid 模型**做高召回兜底，和 late "
            "fusion 结果**取 OR** (宁可误伤不漏检)。"
        ),
    ])

    b.add_section("A.3 Modality Dropout (训练技巧)", [
        (
            "**问题**：线上 30%~50% 的 Pin text 为空 / 机翻 / alt-text 被 strip。如果训练数据"
            "全是完整的 image+text pair，late-fusion 的文本分支在生产上会遇到分布外输入 "
            "(空字符串 embedding) 给出噪声 logit，拖累融合决策。"
        ),
        (
            "**做法**：训练时以概率 **p_text_drop ~ 0.2~0.3** 把 text 置空 (传入特殊 [EMPTY] "
            "token)、以概率 **p_img_drop ~ 0.05** 把 image 替换成 gray placeholder。这让模型"
            "学会\"当某一路缺失时退化到另一路\"。融合层进一步接入**模态 mask** 作为 feature，"
            "让 MLP 知道哪一路是置信的。Dropout 概率要对齐线上实际缺失率，PSI 监控 drift "
            "(见 T-P2-460)。"
        ),
    ])

    b.add_section("A.4 Asymmetric Confidence Thresholds (上线决策规则)", [
        (
            "**核心 insight**：unsafe 检测是**极度 class-imbalanced** 的多标签任务 "
            "(NSFW 占大盘 <0.5%)，且**两类错误代价不对称**：漏检 NSFW → 用户投诉 / 品牌"
            "风险 / 监管罚款；误判 SFW → 创作者申诉 / 流量损失。所以**不要用单一 0.5 阈值**。"
        ),
    ])
    b.add_comparison_table(
        headers=["决策带", "阈值示例 (per label)", "动作", "SLA"],
        rows=[
            [
                "**高置信 SFW**",
                "p_unsafe < **0.05**",
                "直接分发 (进入 ranking pool)",
                "无人审",
            ],
            [
                "**灰带 borderline**",
                "**0.05 <= p_unsafe < 0.70**",
                "**暂缓分发** + 进 HIL queue",
                "**<=24h** 人审回补",
            ],
            [
                "**高置信 unsafe**",
                "p_unsafe >= **0.70**",
                "**立刻下架** + creator notice",
                "支持申诉 5 个工作日",
            ],
            [
                "**超高风险 (CSAM/self-harm)**",
                "单独模型 + **规则或**",
                "**先拦再审**，任何可疑都先下",
                "24h 法务 review",
            ],
        ],
        title="A.5 非对称阈值配置 (pitch-level，具体数字按类目校准)",
    )

    b.add_section("A.6 Human-in-Loop 规则", [
        (
            "**三条核心规则**："
        ),
        (
            "1. **灰带必审**：所有落在 borderline (上表第 2 行) 的 Pin 必须 24h 内有人审结论，"
            "不允许自动放行也不允许自动删除。审核结果以\"高质量 label\"回流下一个训练"
            "cycle，优先放入**主动学习**采样池。"
        ),
        (
            "2. **审核团队不做 true/false 二选，而是打 multi-label**：跟模型的多头对齐 (porn、"
            "violence、self-harm、drug、hate、misinfo)，这样能**发现模型单头性能问题** "
            "(e.g. drug 头 recall 垮了但 porn 头正常)，而不是只知道整体 AUC 掉了。"
        ),
        (
            "3. **审核一致性与校准**：每批审核里**塞 3%~5% 已知 ground-truth gold** 测审核员"
            "准确率；审核员 per-label 的 sensitivity bias 纳入权重，**不是所有审核意见等权回流**。"
            "这条避免\"人工噪声污染训练集\"，和模型 calibration 一起维护。"
        ),
    ])

    b.add_section("A.7 上线 + 监控红线 (简表)", [
        "- **PSI 监控**：image embedding、text embedding、融合层输入三路分开算 PSI；PSI > 0.25 告警。",
        "- **Per-label PR-AUC**：不用整体 AUC (imbalanced 下无意义)，盯 per-label PR-AUC + top-K "
          "recall@precision=0.99。",
        "- **Shadow mode**：新版本先跑 72h shadow，看 borderline queue 量级是否爆炸 (若 +30% "
          "说明校准漂了)。",
        "- **红线**：任何 model / 阈值改动若导致 **CSAM / self-harm 召回下降 >= 1pp**，立刻回滚，"
          "不走灰度。",
    ])

    # ==================================================================
    # SECTION B -- QUERY EXPANSION FOR RECALL BOOST
    # ==================================================================
    b.add_section("B. Query Expansion for Recall Boost (without changing ranking)", [
        (
            "**定位 (pitch)**：\"在**不重训 ranking 模型**的前提下把 recall 往上顶一截\" 是"
            "一个经典的 SD 题。落地策略是**在 query 侧做改写 + 扩展**，把\"一个 query\"变成\""
            "多个 query 并集 ANN 召回\"，再走原 ranking。核心前提：**召回是上限、ranking 是"
            "天花板**——召回漏掉的 Pin ranking 再强也救不回来，所以 query expansion 常是短期"
            "收益最大的杠杆。**ANN 机制本身**见 doc 58 (Pinterest Sketch/Streaming 1-Pager) 的"
            "HNSW/IVF-PQ 小节，此文不再重复。"
        ),
    ])

    b.add_comparison_table(
        headers=["策略", "机制", "适用场景", "延迟 / 成本", "**Pinterest 优先级**"],
        rows=[
            [
                "**1. SynSet 规则查表**",
                "query -> taxonomy SynSet -> 同义词集合",
                "强 tail 词 / 多语言同义 (e.g. \"sofa\" <-> \"couch\")",
                "**<5ms** (内存 dict)",
                "**P0 baseline**，always on",
            ],
            [
                "**2. 小 LLM 改写**",
                "distilled small LM (<=300M) 生成 N 条 paraphrase",
                "拼写纠错、意图澄清 (\"室内植物好养\" -> \"耐阴室内植物\")",
                "**20~50ms** (edge cache + batch)",
                "**P1** 头部 segment 灰度",
            ],
            [
                "**3. Query-to-query ANN**",
                "历史 query embedding 库 -> ANN top-K 近邻 query",
                "高频 query 有邻居时特别强 (头部流量 40%+)",
                "**<10ms** (HNSW in-memory)",
                "**P0**，必上",
            ],
            [
                "**4. Click-driven 扩展**",
                "共点 (co-click) / 共同加 board 的 pseudo-synonym 挖掘",
                "发现非字面同义 (\"birthday cake\" <-> \"buttercream\")",
                "离线挖，**<5ms** lookup",
                "**P0**，和 #3 互补",
            ],
            [
                "**5. Cross-lingual 扩展**",
                "多语言 embedding (e.g. LaBSE) query -> 其他语言邻近 query",
                "全球用户 / 小语种库存稀疏",
                "**<10ms**",
                "**P1** 多语言市场",
            ],
        ],
        title="B.1 五种 query expansion 策略对比",
    )

    b.add_section("B.2 组合策略 (pipeline 视角)", [
        (
            "**推荐做法**：五条路**并联召回 + 去重 + 加权归并**，而不是串联。"
        ),
        (
            "- **Step 1 Generate**：同时跑 #1 (SynSet)、#3 (q2q ANN)、#4 (click-driven)，"
            "每路产出 0~K 个扩展 query，每个带 source + score。头部 segment 额外跑 #2 (小 LLM) "
            "和 #5 (多语言)。"
        ),
        (
            "- **Step 2 De-dup + Cap**：query 文本做 normalize (lowercase / 去空格 / 去 emoji)，"
            "dedup。限制总扩展 query 数 <= **N=6**，避免 ANN 放大太多噪声。"
        ),
        (
            "- **Step 3 Parallel ANN**：原 query + 扩展 query 全部走 ANN (HNSW/IVF-PQ，见"
            f" doc {SKETCH_DOC_ID})，每个出 top-K=200。"
        ),
        (
            "- **Step 4 Merge + Dedup Pin**：pin_id 级 dedup；每个 pin 的分数 = "
            "**max(score over all source queries) × source_weight(source)**，source_weight "
            "给原 query 1.0、SynSet 0.9、co-click 0.8、小 LLM 0.6 (按离线 AB 校准)。"
        ),
        (
            "- **Step 5 Pass to Ranking**：合并后的 candidate pool 直接喂给**原 ranking 模型"
            "**。ranking 不变，只是 candidate 池变宽、更多样。这是\"不改 ranking\"的关键。"
        ),
    ])

    b.add_section("B.3 离线挖掘 (click-driven SynSet) 的工程要点", [
        (
            "- **co-click 图**：node = query，edge weight = |users who clicked same pin within "
            "session|。对**低频 query** 要加 smoothing，否则偶然共点被放大成伪同义。"
        ),
        (
            "- **heavy hitter 控制**：极度高频 query (\"recipe\"、\"outfit\") 会和所有 query "
            "共现，必须 IDF / PPMI 加权，否则 top neighbor 全是 stopword 类。"
        ),
        (
            "- **时效**：co-click 图按 **T=28 天** 滚动，季节性 query (holiday、back-to-"
            "school) 才跟得上。embedding 索引同样定期 rebuild (见 doc 58 Count-Min Sketch / "
            "heavy hitter 流式估计范式)。"
        ),
    ])

    b.add_section("B.4 不改 ranking 的收益上限 (实诚)", [
        (
            "**长话短说**：这类策略在 Pinterest 量级能推到 **+2~5% recall@100**、**+1~3% save "
            "rate** 是合理预期，但**不会**有 +10% 这种巨变——因为 ranking 模型本身在做类似的"
            "semantic 匹配。真正的杠杆点是**覆盖 tail + 多语言 + 拼写容错**，头部流量的增益"
            "往往被现有 ranking 稀释。面试里被追问 \"为什么不直接重训 ranking\" 的正确回答是："
            "(1) ranking 迭代周期长 / 风险高；(2) expansion 是 query 侧改动，**可灰度到任意"
            "细粒度** (per query type、per country)；(3) 两件事**不冲突**，该做都做。"
        ),
    ])

    # ==================================================================
    # INTERVIEW QA (keep compact, 2-3 per section)
    # ==================================================================
    b.add_interview_qa(
        "Pinterest unsafe 检测为什么不直接上一个 end-to-end CLIP 分类器？",
        (
            "三个原因：(1) **合规可解释性**——审核团队要知道是图触发还是文触发，单一 logit 说不"
            "清；(2) **模态缺失鲁棒性**——30%~50% Pin text 空，late fusion + modality dropout "
            "比 end-to-end 稳；(3) **多头差异化**——不同 unsafe 类目 (porn vs hate vs drug) "
            "特征源差别大，late fusion 允许每头用不同 backbone / threshold。End-to-end 只在"
            "**头部高风险类目**做 hybrid cross-attn 兜底。"
        ),
    )
    b.add_interview_qa(
        "为什么 unsafe 模型不能用 0.5 做阈值？",
        (
            "两个原因：(1) class imbalance (NSFW <0.5%)，模型输出分布严重偏 0，0.5 几乎没"
            "样本；(2) **错误代价非对称**——漏检 NSFW 的代价是误伤 SFW 的 10~100 倍。所以用"
            "**三段阈值**：<0.05 直接过；0.05~0.70 进 HIL queue；>=0.70 直接下架。具体数字"
            "按 per-label 的 PR 曲线卡 precision@target 定。"
        ),
    )
    b.add_interview_qa(
        "query expansion 有没有可能把 recall 拉起来但 precision 暴跌？",
        (
            "会。两条防线：(1) **每路扩展 query 带 source_weight**，衰减非字面扩展 (小 LLM / "
            "co-click) 在 merge 时的分数；(2) **不换 ranking 模型**——expansion 只拓宽候选池，"
            "最终 ranking 再按 save-rate / engagement 排序，noise query 带进来的烂 pin 会被"
            "ranking 丢到后面。AB 监控 precision@10 和 save-rate；若下滑 >1%，关扩展 source "
            "精排 weight 或下线。"
        ),
    )

    # ==================================================================
    # CHECKLIST (short, pitch-level)
    # ==================================================================
    b.add_checklist("Pitch-Level Self-Check", [
        "能一张表讲清 early / late / hybrid fusion 的权衡 + Pinterest 默认选 late",
        "能讲 modality dropout 的训练目的 (线上 text 缺失率对齐)",
        "能讲三段非对称阈值 + HIL 回流的意义 (asymmetric cost)",
        "能讲 5 种 query expansion 策略 + 并联而非串联的组合范式",
        "能讲 click-driven SynSet 的 heavy-hitter / 时效 pitfall",
        f"能主动 link 到 Pinterest Sketch doc (id={SKETCH_DOC_ID}) 的 ANN / heavy-hitter 机制",
        "能给出 +2~5% recall@100 的实诚收益上限，不吹",
    ])

    # ==================================================================
    # CROSS-REF BLOCK
    # ==================================================================
    b.add_section("Cross-Reference (Pinterest prep ecosystem)", [
        f"- **doc id={SKETCH_DOC_ID}** Pinterest Sketch/Streaming 1-Pager -- HNSW / IVF-PQ / "
          "Count-Min Sketch / HLL / heavy hitter 机制；本文 B 节的 ANN 和 click-driven 挖掘全部"
          "引用其中的结构。",
        "- **T-P2-460** Responsible AI + Monitoring Playbook (P2 兄弟任务) -- PSI / KS / 再训练"
          "节奏、bias 公平性；本文 A.7 监控红线和 B 节的 co-click 漂移告警都归此。",
        "- **T-P2-458** Generative Models Pitch -- 3.3 节 (视觉搜索增广) 的合成图红线 "
          "(\"generative 只做召回 rehearsal，不直接展示给用户\") 和本文 unsafe 检测是同一套"
          "安全红线。",
    ])

    return b.build()


# ==========================================================================
# DB helpers (match T-P2-458 pattern)
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


def count_weighted_tokens(text: str) -> int:
    """Rough weighted token: EN word ~= 1 token, 1 CJK char ~= 1 token."""
    en_words = sum(1 for tok in text.split() if any(c.isascii() and c.isalpha() for c in tok))
    cjk_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    return en_words + cjk_chars


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    content = build_doc()
    warns = StudyNoteBuilder.validate(content)
    for w in warns:
        print(f"[WARN] {w}")

    length = len(content)
    tokens = count_weighted_tokens(content)
    print(f"[BUILT] gap-fill doc length={length} chars  ~weighted_tokens={tokens}")

    # AC: <=3000 words pitch-only. Loose bound in chars.
    if tokens > 3000:
        print(f"[FAIL] weighted_tokens={tokens} exceeds 3000 cap")
        sys.exit(1)
    if length > 18000:
        print(f"[WARN] length={length} chars unusually large for pitch doc")

    # Sanity: must reference the Sketch doc id
    if f"id={SKETCH_DOC_ID}" not in content and f"doc {SKETCH_DOC_ID}" not in content:
        print(f"[FAIL] content does not link to Pinterest sketch doc id={SKETCH_DOC_ID}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Verify sketch doc 58 still exists (defensive)
        row = conn.execute(
            "SELECT id, title FROM company_documents WHERE id = ?", (SKETCH_DOC_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] referenced sketch doc id={SKETCH_DOC_ID} not found in DB")
            sys.exit(1)
        print(f"[CROSS-REF] confirmed sketch doc id={row[0]} title='{row[1]}'")

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

    print("[DONE] Pinterest SD gap-fill (unsafe + query expansion) seed complete")


if __name__ == "__main__":
    main()
