"""T-P2-460: Pinterest Responsible AI + Monitoring Playbook.

Seeds ONE Pinterest company_document (doc_kind=prep_note) titled
"Responsible AI + Monitoring Playbook for Pinterest" covering four pitch-level
gaps flagged as missing from the Pinterest prep set:

  (A) Bias detection -- Inclusive AI anchored on Pinterest's own
      "skin-tone fair visual search" case study. Group metrics on protected
      attributes; demographic parity / equal opportunity / equalized odds
      trade-off.
  (B) Fair-aware constrained ranking via **post-hoc re-rank** (no ranking
      model retrain required). Slot quotas, min-exposure bounds, honest
      utility / fairness trade-off.
  (C) Drift monitoring -- PSI / KS / KL-JS trade-offs, per-feature vs output
      drift, performance drift alert thresholds.
  (D) Retraining cadence -- scheduled vs trigger-based; explicit trigger
      rules (PSI breach, per-slice regression, feedback SLA).

AC: <=2000 words. Pitch-top, restrained. Idempotent upsert by
(company_id=29, title). No new framework_node, no code.

Usage::

    python scripts/seed_pinterest_responsible_ai_monitoring_20260416.py
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
DOC_TITLE = "Responsible AI + Monitoring Playbook for Pinterest"
SKETCH_DOC_ID = 58  # "Pinterest Sketch/Streaming Theory 1-Pager"
GAP_FILL_DOC_ID = 74  # "Pinterest SD Gap-Fill: Unsafe Multimodal + Query Expansion"


# ==========================================================================
# Doc content
# ==========================================================================

def build_doc() -> str:
    b = StudyNoteBuilder()
    b.set_title("Responsible AI + Monitoring Playbook for Pinterest")

    b.add_prerequisites([
        "Pinterest 双塔 / CLIP retrieval 和 ranking 的基本 pipeline",
        "Precision / Recall / PR-AUC 在 imbalanced 下的含义",
        "ANN 召回 + ranking 两段结构 (doc 58 Sketch/Streaming 有结构图)",
        "基本 AB test 读数 (CTR / save-rate / precision@K)",
    ])

    b.add_term("DP", "Demographic Parity",
        "每组的正预测率相同：P(Y_hat=1 | G=a) = P(Y_hat=1 | G=b)")
    b.add_term("EO", "Equal Opportunity",
        "真正例在每组的召回相同：P(Y_hat=1 | Y=1, G=a) = P(Y_hat=1 | Y=1, G=b)")
    b.add_term("EOdd", "Equalized Odds",
        "每组 TPR 和 FPR 都相同 (EO 的强化版)")
    b.add_term("PSI", "Population Stability Index",
        "分布漂移指标: sum_i (a_i - e_i) * ln(a_i / e_i)")
    b.add_term("KS", "Kolmogorov-Smirnov",
        "两分布 CDF 最大差异，连续单特征首选")
    b.add_term("HIL", "Human-in-the-Loop",
        "审核人员回流；详见 doc 74 (gap-fill doc) A.6 节")

    # ==================================================================
    # SECTION A -- BIAS DETECTION / INCLUSIVE AI
    # ==================================================================
    b.add_section("A. Inclusive AI 与 Bias Detection", [
        (
            "**定位 (pitch)**：Pinterest 自 2018 年起在 \"skin-tone fair visual search\" "
            "问题上做过公开工作——同一条搜索词 (e.g. \"wedding hair\", \"eye makeup\")，"
            "结果 pool 必须覆盖不同肤色区间，不然女性有色用户会感觉 \"搜我自己都搜不到"
            "自己\"。工程做法不是在训练 loss 上塞 fairness term，而是**离线检测 + 线上"
            "re-rank** 两手：先用 skin-tone bucket (Monk Skin Tone 10 档 / Fitzpatrick "
            "6 档) 算组指标，再在 serving 层做 slot-based quota。下面只讨论**检测指标**"
            "和**权衡** (re-rank 放到 Section B)。"
        ),
    ])

    b.add_comparison_table(
        headers=["指标", "定义 (口语)", "何时用", "Pinterest 场景"],
        rows=[
            [
                "**Demographic Parity (DP)**",
                "每组被\"推荐\"的**比例**相同",
                "库存端 exposure 均衡；不关心基准率差异",
                "visual search result pool 按 skin-tone 10 档均衡曝光",
            ],
            [
                "**Equal Opportunity (EO)**",
                "每组**真正例召回**相同 (TPR)",
                "有明确 ground-truth 正例标签；关心\"该被推荐的被推\"",
                "creator 收益分配 / unsafe 模型 per-group recall",
            ],
            [
                "**Equalized Odds**",
                "每组 TPR 和 FPR 都相同",
                "高合规场景 (unsafe 漏检 vs 误删双约束)",
                "CSAM / self-harm 模型 per-group 审计",
            ],
            [
                "**Calibration within group**",
                "每组 P(Y=1 | score=s) 都一致",
                "score 需要被下游当 probability 用时",
                "ads pCTR 模型；校准不齐会污染 ranking",
            ],
        ],
        title="A.1 四个主流公平性定义 (pitch-level 对比)",
    )

    b.add_section("A.2 面试陷阱：三者不可同时满足", [
        (
            "**Impossibility result (Chouldechova 2017)**：两组基准率 P(Y=1 | G) 不等"
            "且分类器非完美时，**DP / EO / calibration 三者最多满足其二**。所以要**按业"
            "务代价选**——exposure 公平选 DP、召回公平选 EO、score 当 probability 用"
            "时守 calibration；没有三者都调到 0 的工程目标。"
        ),
    ])

    # ==================================================================
    # SECTION B -- FAIR-AWARE CONSTRAINED RANKING (POST-HOC)
    # ==================================================================
    b.add_section("B. Fair-aware Constrained Ranking (Post-hoc Re-rank)", [
        (
            "**定位 (pitch)**：**不动 ranking 模型权重**，只在模型出分之后按"
            "组做 re-rank，最廉价、可灰度、可一键回滚。Pinterest (和大多数大厂) "
            "都**优先**用这条路，理由：(1) 训练期 fairness loss 难调、回退困难；"
            "(2) 公平性需求**随政策 / PR 事件**变化快，post-hoc 改 config 就能上；"
            "(3) 模型主力指标 (save-rate、CTR) 不被公平性约束直接拖累训练。"
        ),
    ])

    b.add_comparison_table(
        headers=["策略", "机制", "公平性类型", "代价"],
        rows=[
            [
                "**Slot Quota**",
                "top-K 结果里每组至少 m_g 个 slot",
                "**DP** (exposure 比例)",
                "低：只在边界 slot 替换",
            ],
            [
                "**Min-Exposure Floor**",
                "保证每组累计曝光 >= floor_g",
                "**DP** 的累积版",
                "中：需要 session-level 状态",
            ],
            [
                "**Calibrated Re-rank**",
                "按组 score 分位数调整排序",
                "**Calibration** (per group)",
                "高：需要离线估组分位数",
            ],
            [
                "**Constrained Optimization**",
                "在 ranking score 上叠加 Lagrangian 约束",
                "任意 (DP / EO / EOdd)",
                "最高：等价部分重训，回滚慢",
            ],
        ],
        title="B.1 四种 post-hoc 公平性 re-rank 策略",
    )

    b.add_section("B.2 Pinterest 默认选哪个 + 老实话", [
        (
            "**默认 slot quota + min-exposure floor 两段式**：top-10 结果里 skin-tone 每"
            "档至少 1 个 slot；session 级再保证每档累计曝光不低于 floor (e.g. 5%)。"
            "这是 skin-tone fair visual search 公开博客里披露过的大方向。"
        ),
        (
            "**老实话**：post-hoc re-rank 会**牺牲 head 组的 relevance**——某些组的最"
            "相关 pin 被挤出 top-K。量级通常是 **-0.3% ~ -1% save-rate**，换来的是"
            "**长尾用户满意度 + 监管 / 品牌风险下降**。面试不要吹 \"两者都赢\"——老老"
            "实实说 \"小代价换大下行保护\" 才是工程师视角。"
        ),
    ])

    # ==================================================================
    # SECTION C -- DRIFT MONITORING
    # ==================================================================
    b.add_section("C. Drift Monitoring (PSI / KS / KL-JS)", [
        (
            "**定位 (pitch)**：上线模型不是 \"打完就散\"，每一条 feature、每一路 embedding、"
            "最终 score 都要有 drift 告警。Pinterest 每天 ~50B pin impression，特征分布"
            "一天就能飘到无法识别，早期告警决定 incident 深浅。"
        ),
    ])

    b.add_comparison_table(
        headers=["指标", "公式 / 性质", "何时用", "告警阈值 (经验)"],
        rows=[
            [
                "**PSI**",
                "sum_i (a_i - e_i) * ln(a_i / e_i)，对称有界",
                "**分箱后**的单变量分布对比 (主力)",
                "**0.1 warn / 0.25 critical**",
            ],
            [
                "**KS**",
                "max |F_a(x) - F_e(x)|，连续分布 CDF 差",
                "连续单特征，不需分箱",
                "> **0.1** 关注，> 0.2 告警",
            ],
            [
                "**KL divergence**",
                "sum a * ln(a / e)，不对称、无上界",
                "分布比较且明确 reference (e=历史)",
                "不设硬阈值；和基线 KL 比",
            ],
            [
                "**JS divergence**",
                "KL 的对称 bounded 版 (0~log2)",
                "两侧都可能漂时 (e.g. A/B 对比)",
                "> **0.1** 告警",
            ],
            [
                "**Performance drift**",
                "per-slice PR-AUC / save-rate 的 week-over-week",
                "终极 source of truth",
                "**单 slice 下跌 > 1pp 连续 3 天** 触发重训",
            ],
        ],
        title="C.1 五种 drift 指标对比",
    )

    b.add_section("C.2 监控什么 (pitch 三层)", [
        (
            "- **Input drift**：每个关键 feature 的 PSI / KS，按 group (国家 / 语种 / "
            "skin-tone bucket) 拆开算，总体 OK 不代表子群 OK。"
        ),
        (
            "- **Embedding drift**：双塔 image / text embedding 各自算 PSI on "
            "quantile-binned L2 norm 或 per-dim PCA top-k 投影；embedding drift 往往早于"
            "performance drift 1~2 天。"
        ),
        (
            "- **Output + performance drift**：score 分布 PSI + per-slice PR-AUC / "
            "save-rate；output drift 是给**产品团队**的告警，performance drift 是给"
            "**ML 团队**的告警，触发条件不一样。"
        ),
    ])

    # ==================================================================
    # SECTION D -- RETRAINING CADENCE
    # ==================================================================
    b.add_section("D. Retraining Cadence (Scheduled vs Trigger-based)", [
        (
            "**定位 (pitch)**：重训成本高 (数据 pipeline、compute、validate、灰度)，但"
            "不重训就吃 drift。两种节奏**并存**而不是二选一。"
        ),
    ])

    b.add_comparison_table(
        headers=["节奏", "触发条件", "优点", "缺点"],
        rows=[
            [
                "**Scheduled**",
                "固定 cadence (weekly / biweekly / monthly)",
                "可预测，pipeline 稳定，回滚演练常态化",
                "对突发 drift 反应慢 (一个 cycle 窗口)",
            ],
            [
                "**Trigger-based**",
                "PSI / performance 阈值破线后立即 kick off",
                "快速响应 (holiday、热点事件、数据污染)",
                "训练资源不可预测；可能和 scheduled 冲突",
            ],
            [
                "**混合 (推荐)**",
                "scheduled 每周一次 + trigger 超阈值额外重训",
                "稳态 + 异常双覆盖，Pinterest 默认",
                "需要 trigger 去重 / 资源调度",
            ],
        ],
        title="D.1 两种节奏 + 混合默认",
    )

    b.add_section("D.2 Trigger 的硬规则 (避免 trigger storm)", [
        (
            "- **去抖 (debounce)**：同一 trigger 24h 内只起一次；PSI > 0.25 但连续 6h 内"
            "回到 < 0.2 就撤告警。"
        ),
        (
            "- **分层阈值**：warn (PSI > 0.1) 只通知 owner；critical (PSI > 0.25) 才"
            "kick off 重训 pipeline；emergency (一类 safety regress) 才 page on-call。"
        ),
        (
            "- **Rollback gate**：trigger-based 重训模型**必须**经 shadow + 1% 灰度 24h "
            "才能全量，**不允许** \"告警触发 -> 直接全量\"。"
        ),
        (
            "- **Feedback loop SLA**：HIL 审核回流的 label 必须在 **<=72h** 内进入下一轮"
            "训练集；超 72h 的审核 label 判为\"时效失效\"，只入长期评测集不入训练。"
        ),
    ])

    # ==================================================================
    # INTERVIEW QA (compact, 3)
    # ==================================================================
    b.add_interview_qa(
        "demographic parity 和 equal opportunity 冲突时怎么选？",
        (
            "按**业务代价**选，不按\"更公平\"选。Pinterest visual search exposure 公平"
            "(搜索结果里每档肤色的比例) 选 **DP**；creator 收益 / unsafe 模型 per-group "
            "召回选 **EO**。DP 和 EO 只有在两组基准率 (P(Y=1 | G)) 相等时才能同时满足，"
            "生产场景几乎不可能，所以一定要**预先定义**哪个指标是北极星。"
        ),
    )
    b.add_interview_qa(
        "PSI 告警阈值 0.1 / 0.25 是怎么来的？",
        (
            "**经验法则 (industry standard, 非理论推导)**：PSI < 0.1 表示 population "
            "基本稳定；0.1~0.25 中等漂移需要关注；> 0.25 表示显著漂移需要干预。用之前"
            "要**按特征校准**——高基数 id 类特征自然波动大，阈值可以放宽；binary 关键"
            "feature 阈值要更紧 (e.g. 0.05 / 0.15)。**不要**盲目套 0.1 / 0.25 到所有"
            "特征。"
        ),
    )
    b.add_interview_qa(
        "为什么 fairness 优先做 post-hoc re-rank 而不是训练期 fairness loss？",
        (
            "三点：**可回滚** (config 30 分钟回滚 vs 重训)、**可灰度** (按国家 / 语言"
            "细粒度开关)、**需求变化快** (今天 skin-tone、下季度 body-type)。代价是"
            "**小幅 relevance 损失** (~0.3-1% save)，但下行保护 (PR / 监管) 远超收益。"
        ),
    )

    # ==================================================================
    # CHECKLIST
    # ==================================================================
    b.add_checklist("Pitch-Level Self-Check", [
        "能讲 DP / EO / equalized odds / calibration 四者定义 + Pinterest 场景映射",
        "能讲 impossibility result (DP / EO / calibration 三选二)",
        "能讲 post-hoc re-rank 默认选 slot quota + min-exposure + 代价 (-0.3~1% save)",
        "能讲 PSI 0.1 / 0.25 阈值 + per-feature 校准必要",
        "能讲 input / embedding / output / performance 四层 drift 监控",
        "能讲 scheduled + trigger 混合节奏 + debounce / 分层阈值 / rollback gate",
        "能主动 link unsafe detection (doc 74) 和 ANN (doc 58) 的兄弟章节",
    ])

    # ==================================================================
    # CROSS-REF BLOCK
    # ==================================================================
    b.add_section("Cross-Reference", [
        f"- **doc id={GAP_FILL_DOC_ID}** Pinterest SD Gap-Fill (Unsafe Multimodal + Query "
          "Expansion) -- A.7 监控红线 (PSI + per-label PR-AUC + shadow mode) 是本文 C / D "
          "节在 unsafe 场景的具体化，两文互为 pointer。",
        f"- **doc id={SKETCH_DOC_ID}** Pinterest Sketch/Streaming Theory 1-Pager -- drift "
          "监控的底层 streaming 估计 (Count-Min / HLL / heavy hitter) 在那里；本文不重复。",
        "- **T-P2-458 / T-P2-459** 兄弟 gap-fill 任务 -- 覆盖 generative models、unsafe + "
          "query expansion；和本文的公平性 / 监控共同构成 Pinterest Responsible AI 三角。",
    ])

    return b.build()


# ==========================================================================
# DB helpers (match T-P2-459 gap-fill pattern)
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
    print(f"[BUILT] responsible-ai doc length={length} chars  ~weighted_tokens={tokens}")

    # AC: <=2000 words pitch-only.
    if tokens > 2000:
        print(f"[FAIL] weighted_tokens={tokens} exceeds 2000 cap")
        sys.exit(1)
    if length > 14000:
        print(f"[WARN] length={length} chars unusually large for pitch doc")

    # Sanity: must reference gap-fill doc (74) and sketch doc (58)
    if f"id={GAP_FILL_DOC_ID}" not in content:
        print(f"[FAIL] content does not link gap-fill doc id={GAP_FILL_DOC_ID}")
        sys.exit(1)
    if f"id={SKETCH_DOC_ID}" not in content:
        print(f"[FAIL] content does not link sketch doc id={SKETCH_DOC_ID}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Defensive: verify cross-ref docs exist
        for ref_id in (GAP_FILL_DOC_ID, SKETCH_DOC_ID):
            row = conn.execute(
                "SELECT id, title FROM company_documents WHERE id = ?", (ref_id,)
            ).fetchone()
            if not row:
                print(f"[FAIL] cross-ref doc id={ref_id} not found in DB")
                sys.exit(1)
            print(f"[CROSS-REF] confirmed doc id={row[0]} title='{row[1]}'")

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

    print("[DONE] Pinterest Responsible AI + Monitoring Playbook seed complete")


if __name__ == "__main__":
    main()
