"""Append 5 follow-up angles to ML Fundamentals leaf node id=209
(path: ml-fundamentals/classical_ml/bias-variance-tradeoff).

Per user Discord 2026-04-20, target node is the public ML Fundamentals
page, NOT the pillar2 canonical hub (id=67). The leaf is ~1419 chars
and uses numbered sections (1-4); additions must be tight.

Augmentations (keyed to user's 6 points):
- Explicit one-term cross-product expansion appended to section 2
- MSE-only caveat appended to section 2's "MSE 下成立" sentence
- New section 5: Diagnostic Fingerprints (train/val + learning curve)
- New section 6: Remedies Quick-List (2 bullets)
- New section 7: 经典模型容量旋钮 (6 one-liners)
- New section 8: 正则化一句话机理

Idempotent via sentinel comment markers. Safe to re-run.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 209

# --- Insert 1: expand one cross term + loss caveat into section 2 --------
ANCHOR_1 = "这条分解式在 **Mean Squared Error** (MSE, 均方误差) 损失下成立。"
INSERT_1_MARKER = "<!-- FOLLOWUP_20260420_CROSS_TERM_AND_LOSS -->"
INSERT_1 = r"""这条分解式在 **Mean Squared Error** (MSE, 均方误差) 损失下成立。

<!-- FOLLOWUP_20260420_CROSS_TERM_AND_LOSS -->

> **交叉项展开示例**（面试官常追问"写一项给我看看"）：$E_{D,\epsilon}[(\bar{f} - \hat{f}_D)\epsilon] = E_D[\bar{f} - \hat{f}_D] \cdot E[\epsilon] = 0 \cdot 0 = 0$，依赖 $\epsilon \perp D$ 与 $E[\epsilon]=0$。另外两项同理。
>
> **换损失函数就不成立**：对 **0-1 Loss** 与 **Cross-Entropy** (交叉熵) 没有这么干净的加法分解（Domingos 2000 _A Unified Bias-Variance Decomposition_ 有推广版本，结构更复杂）——分类问题不要强套这条公式。"""

# --- Insert 2: Sections 5/6/7/8 appended to end of description -----------
# Anchor on end of section 4 content (last paragraph of the current doc).
ANCHOR_2 = "所以更准确的说法是：\"在经典欠参数化区域，沿容量轴存在 bias-variance 权衡\"，而不是\"降 bias 必然升 variance\"。"
INSERT_2_MARKER = "<!-- FOLLOWUP_20260420_SECTIONS_5_TO_8 -->"
INSERT_2 = r"""所以更准确的说法是："在经典欠参数化区域，沿容量轴存在 bias-variance 权衡"，而不是"降 bias 必然升 variance"。

<!-- FOLLOWUP_20260420_SECTIONS_5_TO_8 -->

## 5. 诊断：高偏差 vs 高方差（先诊断再开处方）

| 观察维度 | High Bias（欠拟合） | High Variance（过拟合） |
|---------|---------------------|------------------------|
| Train error | 高 | 低（可接近 0） |
| Validation error | 高 | 高 |
| Train-Val gap | **小**（两条贴合） | **大**（拉开明显） |
| Learning Curve（误差 vs 训练集大小 $n$） | 两条汇聚于**同一较高 plateau**，加数据无效 | gap 随 $n$ 增大**持续收窄**，加数据见效 |

**口诀：gap 小而高 = 偏差；gap 大 = 方差。** 与上一节容量-误差 U 曲线互补——容量曲线定位 U 形底，learning curve 判定"加数据 vs 换模型"。

## 6. 应对手段（白板先写这两行，再展开细节）

- **降 Bias**：增大容量（更深/更宽/更高阶）、加信号强的特征、**减弱**正则、训练更久、换更强模型族（线性 → 树 → 神经网络）。
- **降 Variance**：**加数据**（真实 / 增广）、加正则化（L1 / L2 / Dropout / Weight Decay）、Early Stopping、Bagging / Random Forest、**降**容量（剪枝 / 减层 / 减宽）。

## 7. 经典模型的容量旋钮（面试常追问"旋钮是谁"）

每个经典模型都有一个容量旋钮——调大 = 低 bias / 高 variance，调小反之：

- **K-Nearest Neighbors (KNN)**：$k$。$k=1$ 极端低偏差高方差；$k$ 大 → 反过来。
- **Decision Tree**：深度 / min_samples_leaf。深而未剪枝 = 低偏差高方差。
- **Polynomial Regression**：多项式阶数 $d$。
- **Random Forest**：**降 variance 的典型**——bagging 深树 + 降低相关系数 $\rho$，偏差几乎不变。
- **Gradient Boosted Decision Trees (GBDT / XGBoost)**：**降 bias 的典型**——序列拟合残差消偏差；方差靠学习率 + early stopping + max_depth 控制。
- **Deep Neural Network (DNN)**：宽度 / 深度 / 训练时长；Dropout / Weight Decay 是标配方差控制。

## 8. 正则化的一句话机理

L2 / Dropout / Weight Decay / Early Stopping 的本质是**收缩 effective hypothesis space** (有效假设类)——容量名义不变，但可达解的子集变小，相当于在 U 形曲线的容量轴上**把模型向左拉一档**，注入一点 bias 换更多 variance 下降。所以永远是"加正则 = 降方差"，而不是"降偏差"。"""

EDITS = [
    ("cross_term_and_loss", ANCHOR_1, INSERT_1_MARKER, INSERT_1),
    ("sections_5_to_8", ANCHOR_2, INSERT_2_MARKER, INSERT_2),
]


def main() -> int:
    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
    ).fetchone()
    if row is None:
        print(f"[FAIL] node id={NODE_ID} not found", file=sys.stderr)
        conn.close()
        return 1

    desc = row[0]
    before_len = len(desc)
    applied: list[str] = []
    skipped: list[str] = []

    for name, anchor, marker, insert in EDITS:
        if marker in desc:
            skipped.append(name)
            continue
        if anchor not in desc:
            print(f"[FAIL] anchor missing for '{name}'", file=sys.stderr)
            conn.close()
            return 2
        if desc.count(anchor) != 1:
            print(f"[FAIL] anchor for '{name}' not unique", file=sys.stderr)
            conn.close()
            return 3
        desc = desc.replace(anchor, insert, 1)
        applied.append(name)

    if not applied:
        print(f"[SKIP] all {len(EDITS)} followups already present ({before_len} chars)")
        conn.close()
        return 0

    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?", (desc, NODE_ID)
    )
    conn.commit()
    conn.close()
    print(f"[OK] node {NODE_ID} description {before_len} -> {len(desc)} chars (+{len(desc) - before_len})")
    print(f"[OK] applied: {', '.join(applied)}")
    if skipped:
        print(f"[SKIP] already present: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
