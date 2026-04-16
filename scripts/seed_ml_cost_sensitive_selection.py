"""Seed: ML-Fund cost-sensitive model selection hub doc + framework_node id=17.

Covers T-P0-445 AC:
 (a) Expand framework_node id=17 (Model Selection & Validation) description
     with decision rubric + worked example (>=3000 bytes).
 (b) Seed docs/ml_cost_sensitive_selection.md using StudyNoteBuilder with
     Pinterest unsafe-content (high FN cost) + Google Ads (high FP cost) cases.
 (c) Reference google_calibration_drill.md (doc 62) -- do NOT duplicate
     Platt/Isotonic/Temperature math.

Pyramid base -- no fancy expansion. Target <=2500 words for the hub doc.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
DOC_PATH = REPO_ROOT / "docs" / "ml_cost_sensitive_selection.md"
NODE_ID = 17  # pillar2.model_selection_validation


def build_hub_doc() -> StudyNoteBuilder:
    """Build the cost-sensitive model selection hub doc."""
    b = StudyNoteBuilder()
    b.set_title("Cost-Sensitive Model Selection -- FP/FN Rubric + Pinterest / Google Ads Cases")

    b.add_prerequisites([
        "Confusion matrix (TP/FP/TN/FN) and core metrics (precision, recall, F1)",
        "Precision-Recall curve, ROC curve, AUC",
        "Binary cross-entropy loss and class weights",
        "Threshold-based decision rule p_hat >= tau -> positive",
    ])

    b.add_term("FN", "False Negative",
               "Missed positive: the true label is 1 but the model predicted 0")
    b.add_term("FP", "False Positive",
               "Wrong alarm: the true label is 0 but the model predicted 1")
    b.add_term("EC", "Expected Cost",
               "Expected business loss per prediction; weighted sum of C_FN * P(FN) + C_FP * P(FP)")
    b.add_term("CSL", "Cost-Sensitive Loss",
               "Training loss with per-class or per-sample weights that mirror business cost")
    b.add_term("PR", "Precision-Recall curve",
               "Precision vs recall across thresholds; the right curve to read for imbalanced / cost-sensitive problems")

    # --- Section 0: Framing ---
    b.add_section("0. The Question This Doc Answers", [
        "Two classifiers arrive on your desk. Model A has AUC 0.812, model B has AUC 0.809. "
        "PR-AUC is within 0.5 points. Which do you ship? AUC / PR-AUC alone cannot answer this -- "
        "they score the ranking globally, not the operating point where the business actually lives. "
        "The real question is: at the production threshold, which model loses less money?",
        "This doc gives a 4-step rubric for that decision, then walks through two concrete cases "
        "that sit on opposite ends of the cost spectrum: Pinterest unsafe-content filtering "
        "(miss is catastrophic -- high FN cost) and Google Ads quality filtering "
        "(false block is catastrophic -- high FP cost).",
        "Scope note: calibration techniques (Platt / Isotonic / Temperature) are referenced but "
        "not derived here -- see `docs/google_calibration_drill.md` for the math. "
        "This doc focuses on the selection and threshold layer that sits on top of calibrated scores.",
    ])

    # --- Section 1: Decision Rubric ---
    b.add_section("1. Four-Step Decision Rubric", [
        "**Step 1. Quantify FP and FN unit cost in business units.** "
        "Translate each error into dollars, user-trust decay, or regulator risk -- whatever the "
        "business actually tracks. Pull the number from product / legal / finance; do not invent it.",
        "**Step 2. Pick the operating point by minimizing expected cost, not by maximizing F1.** "
        "F1 treats FP and FN symmetrically. If FN is 100x worse than FP, F1 is the wrong objective.",
        FormulaBlock(
            latex=(
                r"\text{EC}(\tau) = C_{\text{FN}} \cdot (1 - \text{Recall}(\tau)) \cdot \pi "
                r"+ C_{\text{FP}} \cdot \text{FPR}(\tau) \cdot (1 - \pi)"
            ),
            explanation=(
                "Expected cost per prediction at threshold tau, where pi is the positive prior. "
                "Sweep tau across the validation set, pick the tau that minimizes EC:"
            ),
        ),
        "**Step 3. Recalibrate the threshold per slice, not globally.** "
        "Cost ratios drift by region, device, language. Maintain a threshold table -- "
        "one tau per slice -- and re-fit weekly. Global tau hides slice-level harm.",
        "**Step 4. If shifting the threshold is not enough, change the loss.** "
        "Class-weighted cross-entropy, Focal loss (gamma on hard negatives), or an asymmetric "
        "cost-sensitive loss bakes the cost ratio directly into training, so the gradient "
        "optimizes the right objective from the start.",
        FormulaBlock(
            latex=(
                r"\mathcal{L}_{\text{CSL}} = -\frac{1}{N} \sum_i "
                r"\bigl[w_{+}\, y_i \log \hat{p}_i + w_{-}\, (1-y_i) \log(1 - \hat{p}_i)\bigr], "
                r"\quad \frac{w_{+}}{w_{-}} \approx \frac{C_{\text{FN}}}{C_{\text{FP}}}"
            ),
            explanation=(
                "Class-weighted cross-entropy: the ratio of positive to negative weight mirrors "
                "the cost ratio. Simple, monotone in the weight ratio, and drop-in for any "
                "cross-entropy pipeline:"
            ),
        ),
    ])

    # --- Section 2: Rubric table ---
    b.add_section("2. Pick-The-Lever Cheatsheet", [
        "Use the smallest lever that moves EC below the target. Escalate only if the prior "
        "lever maxes out.",
    ])
    b.add_comparison_table(
        ["Lever", "When to reach for it", "Cost", "Pitfall"],
        [
            ["Threshold sweep", "Cost ratio <=10:1, scores are well-calibrated", "Trivial (minutes)", "Drifts with distribution; re-sweep weekly"],
            ["Per-slice threshold table", "Cost ratio varies by slice (region, device)", "Low (data plumbing)", "Table bloat; cap at ~20 slices"],
            ["Class-weighted CE", "Cost ratio 10:1 to 100:1, training pipeline available", "Moderate (re-train)", "Over-weighting tanks PR-AUC on dominant class"],
            ["Focal loss (gamma=2)", "Extreme imbalance + many easy negatives dominating loss", "Moderate (hyperparam tune)", "Converges slowly; watch recall curves"],
            ["Cost-matrix objective", "Cost ratio >100:1 or asymmetric per-sample cost", "High (custom loss)", "Needs cost labels, not just class labels"],
            ["Ensemble + reject option", "High-cost slices + human reviewer in the loop", "High (infra)", "Queue design and SLA contract matter more than model"],
        ],
        title="Lever ladder: threshold -> class weight -> loss -> ensemble",
    )

    # --- Section 3: Pinterest unsafe-content (HIGH FN COST) ---
    b.add_section("3. Case Study A -- Pinterest Unsafe-Content (High FN Cost)", [
        "Setup: binary classifier flags pins as unsafe (self-harm, hate, CSAM-adjacent). "
        "Positive prior pi ~ 0.1% of organic pins. Two candidates:",
        "- Model A: PR-AUC 0.74, recall at tau=0.5 is 0.82, precision 0.61.",
        "- Model B: PR-AUC 0.72, recall at tau=0.5 is 0.78, precision 0.68.",
        "Naive read: A has higher PR-AUC and higher recall -- ship A. "
        "This is the trap. Step 1 of the rubric: quantify cost.",
        "Unit costs (illustrative, order-of-magnitude; all figures in USD):",
        "- C_FN (miss an unsafe pin): ~500 USD in brand / regulator risk per miss on a viral pin, "
        "plus unbounded tail risk (Section 230 exposure, press cycles). Treat as dominant.",
        "- C_FP (wrongly block a safe pin): ~0.50 USD creator goodwill + 0.05 USD lost ad revenue; "
        "reversible via appeal queue.",
        "Cost ratio ~ 1000:1. At this ratio, the EC-minimizing threshold is far below 0.5. "
        "Sweep both models on the validation set using the EC formula from Section 1.",
        "Worked numbers (per 1M pins, pi = 0.001; all EC values in USD):",
        "- Model A at tau=0.20: recall 0.94, FPR 0.08. EC = 500 * 0.06 * 1000 + 0.50 * 0.08 * 999000 = 30,000 + 39,960 ~= 69,960.",
        "- Model B at tau=0.15: recall 0.91, FPR 0.05. EC = 500 * 0.09 * 1000 + 0.50 * 0.05 * 999000 = 45,000 + 24,975 ~= 69,975.",
        "- Model A at tau=0.10 (push recall harder): recall 0.97, FPR 0.15. EC = 500 * 0.03 * 1000 + 0.50 * 0.15 * 999000 = 15,000 + 74,925 ~= 89,925. Over-blocking flips the sign.",
        "Decision: ship A at tau=0.20. Lower tau hurts because FP volume scales with the negative-heavy prior. "
        "Then bolt on Step 4: class-weighted cross-entropy with w+/w- ~= 50 (not 1000 -- gradient clipping and "
        "dataset scale cap the effective ratio) and a human-review queue on 0.15 <= p_hat < 0.20 (reject-option band).",
        "Monitoring: track FN rate by slice (language, region, creator-cohort). An unsafe-class FN spike in a single "
        "locale is far more actionable than a global PR-AUC drop.",
    ])

    # --- Section 4: Google Ads (HIGH FP COST) ---
    b.add_section("4. Case Study B -- Google Ads Policy Filter (High FP Cost)", [
        "Setup: binary classifier blocks ads that violate policy (misleading claims, restricted verticals). "
        "Positive prior pi ~ 2% of ad impressions. Two candidates with near-equal ROC-AUC.",
        "Cost asymmetry runs the other way vs. Pinterest (figures in USD):",
        "- C_FP (wrongly block a compliant ad): ~3-20 USD lost revenue per blocked impression * advertiser LTV damage; "
        "long-tail advertisers churn after 2-3 false blocks.",
        "- C_FN (let a violating ad through): ~0.50 USD regulator / user-trust cost per impression, amortized across "
        "the catch-net of downstream human review and advertiser-level reputation scores.",
        "Cost ratio inverts to C_FP / C_FN ~ 20:1 to 50:1. The EC-minimizing threshold sits HIGH -- "
        "err on letting the ad run, catch the bad ones via a second-pass reviewer.",
        "Calibration is now load-bearing (see `docs/google_calibration_drill.md`): bid = value * P(conversion), "
        "and a miscalibrated policy score that shifts P by factor k shifts CPA by factor 1/k even when ROC-AUC is flat. "
        "Temperature scaling on the policy model is standard before the threshold is applied.",
        "Concrete lever mix:",
        "- Raise tau to ~0.85 to cut FP aggressively; accept a recall drop.",
        "- Route 0.60 <= p_hat < 0.85 into a human-reviewer SLA (reject-option band).",
        "- Class-weighted CE with w-/w+ ~= 5 (under-weight positives to drive the decision boundary away from the safe class).",
        "- Per-advertiser threshold: long-tenure, low-violation advertisers get tau=0.90; new advertisers stay at 0.75.",
        "Decision: the model with slightly lower recall but higher precision wins at the production operating point, "
        "because the dominant cost term is FP * C_FP * (1-pi). Use the EC formula to compare, NOT F1.",
    ])

    # --- Section 5: Generalizing + interview map ---
    b.add_section("5. When Two Models Look Equal -- Interview Answer", [
        "If the interviewer hands you \"AUC 0.812 vs 0.809, pick one,\" the expected answer walks the rubric:",
        "1. \"First I'd ask product what FP and FN cost in dollars. Without that number, AUC cannot distinguish them.\"",
        "2. \"Given the cost ratio, I'd plot both on the PR curve and pick the tau that minimizes expected cost on the validation set.\"",
        "3. \"If cost ratio is lopsided (Pinterest unsafe-content >500:1 or Google Ads 20:1 the other way), I'd also add class-weighted CE or Focal and retrain, because threshold tuning alone caps at the ROC frontier of the current model.\"",
        "4. \"Finally I'd set up per-slice thresholds and a reject-option band for the borderline scores so a human reviewer clears the ambiguous tail.\"",
        "This maps cleanly to node 70 (Evaluation Metrics) for the metric definitions, node 16 (Sampling & Class Imbalance) for training-time levers, and the calibration drill for the probability-layer math.",
    ])

    # --- Section 6: Self-check ---
    b.add_checklist("2-Minute Oral Self-Check", [
        "State the expected-cost formula EC = C_FN * (1-Recall) * pi + C_FP * FPR * (1-pi)",
        "Explain why F1 is the wrong objective under asymmetric cost",
        "Pinterest unsafe-content: FN dominates, tau < 0.5, class weight w+/w- > 1, reject-option band for review",
        "Google Ads: FP dominates, tau > 0.5, class weight w-/w+ > 1, calibration matters for bid impact",
        "Per-slice threshold table beats one global tau",
        "Lever ladder: threshold -> class weight -> Focal / cost-sensitive loss -> ensemble + reject option",
        "Reference to google_calibration_drill.md for Platt / Isotonic / Temperature math",
        "Metric feeds into node 70 (Evaluation); imbalance technique feeds from node 16 (Sampling)",
    ])

    return b


NODE_DESCRIPTION = """# Model Selection & Validation（模型选择与验证）

## Overview

模型选择不是简单地挑选验证集上 AUC 最高的模型。当两个候选模型的全局排序指标（AUC / PR-AUC）几乎相等时，决定胜负的是**生产运行点上的期望成本**：FP 和 FN 各自的业务代价、所在阈值的 Precision/Recall、以及校准后的概率质量。这一节回答"两个指标接近的模型如何二选一"这个高频面试问题。

## Core Decision Rubric（核心决策四步法）

### Step 1. Quantify FP vs FN Business Cost

把两类错误翻译成可比单位（通常是美元，也可以是用户信任、监管风险）：

- $C_{FN}$：漏判一个正样本的代价。对于 Pinterest 的不安全内容（self-harm / hate / CSAM-adjacent），一次漏判可能引发品牌与监管连带风险，单次可按 \\$500 估算，长尾风险不封顶。
- $C_{FP}$：误报一个负样本的代价。对 Google Ads 政策过滤，误拦合规广告意味着广告主侧营收损失 + LTV 衰减，单次 \\$3–\\$20。

比值 $C_{FN} / C_{FP}$ 决定阈值该往左还是往右挪。别让工程师拍脑袋，一定去 PM / 法务 / Finance 问数字。

### Step 2. Pick Operating Point by Expected Cost (NOT F1)

F1 把 FP 与 FN 视作对称，这在多数业务里是错的。应最小化期望成本：

$$\\text{EC}(\\tau) = C_{FN} \\cdot (1 - \\text{Recall}(\\tau)) \\cdot \\pi + C_{FP} \\cdot \\text{FPR}(\\tau) \\cdot (1 - \\pi)$$

其中 $\\pi$ 是正类先验。在验证集上扫 $\\tau$，选最小 EC 的点。两个看似并列的模型，常在不同 $\\tau^{*}$ 下拉开 10–30% 的 EC 差距。

### Step 3. Threshold Recalibration Per Slice

成本比会随 region / device / language / user-cohort 漂移。维护一张**按切片的阈值表**，一周重拟一次，而不是全局一个 $\\tau$。全局 $\\tau$ 会在小切片上掩盖系统性伤害（某语种的漏报率飙升，整体指标却看不出来）。

### Step 4. Change the Loss (when threshold alone caps out)

当 $C_{FN} / C_{FP}$ 的比值超过单纯调阈值能覆盖的范围（经验上 >10:1 开始需要），把成本直接烧进训练目标：

- **Class-weighted Cross-Entropy**：$\\mathcal{L} = -\\frac{1}{N}\\sum_i [w_{+} y_i \\log \\hat{p}_i + w_{-} (1-y_i) \\log(1-\\hat{p}_i)]$，令 $w_{+}/w_{-} \\approx C_{FN}/C_{FP}$（通常上限 ~50，梯度会饱和）。
- **Focal Loss**：$-\\alpha_t (1 - p_t)^{\\gamma} \\log p_t$，适合极端不平衡 + 大量"易学负样本"主导梯度的场景（典型如 RetinaNet / 不安全内容检测）。
- **Cost-matrix objective**：直接把每个样本的 $C_{FN}, C_{FP}$ 作为权重塞进 loss，适用于 cost 由业务侧直接标注的场景（金融欺诈、医疗分诊）。

## Worked Example（对照实例）

目标：1M 条候选 pins，$\\pi = 0.001$（0.1% 不安全），$C_{FN} = \\$500$，$C_{FP} = \\$0.5$。

| Model | $\\tau$ | Recall | FPR | FN cost | FP cost | Total EC |
|-------|--------|--------|-----|---------|---------|----------|
| A | 0.50 | 0.82 | 0.01 | \\$90,000 | \\$4,995 | \\$94,995 |
| A | 0.20 | 0.94 | 0.08 | \\$30,000 | \\$39,960 | \\$69,960 |
| A | 0.10 | 0.97 | 0.15 | \\$15,000 | \\$74,925 | \\$89,925 |
| B | 0.15 | 0.91 | 0.05 | \\$45,000 | \\$24,975 | \\$69,975 |

结论：Model A 在 $\\tau = 0.20$ 与 Model B 在 $\\tau = 0.15$ 基本打平；默认阈值 0.5 比两者贵 35%。这正是"AUC 相近也要走 Step 2"的原因。

## Sister Nodes & Handoff

- **Evaluation Metrics (node 70)**：Precision / Recall / F-beta / PR-AUC 的定义与读法。本节假定读者已熟悉。
- **Sampling & Class Imbalance (node 16)**：过采样 / 欠采样 / SMOTE，是 Step 4 前的一层轻量级手段。
- **Calibration drill (doc 62, Google R1)**：Platt / Isotonic / Temperature 的数学与 GMB bidding 陷阱，本节不重复。
- **Hub doc**：`docs/ml_cost_sensitive_selection.md` 展开 Pinterest 不安全内容（FN 主导）与 Google Ads（FP 主导）两个对照案例。

## Interview Oral Script (30 seconds)

"AUC 衡量全局排序，不看运行点。两个 AUC 接近的模型要比较的是在生产阈值上的期望成本。我会先问 PM 要 $C_{FN}$ 与 $C_{FP}$ 的单位成本，用 $\\text{EC}(\\tau) = C_{FN}(1-\\text{Recall})\\pi + C_{FP} \\cdot \\text{FPR} \\cdot (1-\\pi)$ 在验证集上扫阈值，挑最小 EC 的点。如果成本比大到单纯调阈值不够，就上 class-weighted CE 或 Focal Loss，把成本直接烧进训练目标。最后维护一张按切片的阈值表，而不是全局一个 $\\tau$。"

## Pitfalls (interviewer bait)

1. 用 Accuracy / F1 回答 cost-sensitive 场景——立刻暴露不熟业务。
2. "调阈值就够了"——阈值只能沿当前模型的 ROC 前沿移动，封顶受模型本身限制；成本比极端时必须改 loss。
3. "class weight 越大越好"——过度 upweight 会把 Precision / PR-AUC 打穿，典型上限 ~50，再高要用 Focal 或 cost-matrix。
4. 忽略校准——概率本身不准时，阈值选得再对也是选错位。先过一遍 Temperature / Isotonic，再做本节的阈值决策。
"""


def write_hub_doc() -> tuple[int, int]:
    """Write the hub doc to disk. Returns (char_count, word_count)."""
    b = build_hub_doc()
    content = b.build()
    DOC_PATH.write_text(content, encoding="utf-8")
    word_count = len(content.split())
    print(f"[DONE] Wrote {DOC_PATH} ({len(content)} chars, ~{word_count} words)")
    return len(content), word_count


def update_framework_node() -> int:
    """Update framework_node id=17 description. Returns byte length."""
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, title FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            sys.exit(1)
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (NODE_DESCRIPTION, NODE_ID),
        )
        conn.commit()
        size = conn.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(f"[DONE] framework_node id={NODE_ID} description updated: {size} chars")
        return size
    finally:
        conn.close()


def main() -> None:
    """Run the seed: write hub doc and update framework node."""
    chars, words = write_hub_doc()
    node_size = update_framework_node()

    # Sanity checks
    if node_size < 3000:
        print(f"[FAIL] framework_node id={NODE_ID} description is {node_size} bytes, target >=3000")
        sys.exit(1)
    if words > 2500:
        print(f"[WARN] Hub doc has {words} words, target <=2500")
    print(f"[OK] All acceptance checks passed (node={node_size} bytes, doc={words} words).")


if __name__ == "__main__":
    main()
