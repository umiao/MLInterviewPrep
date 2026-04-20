"""Append 6 follow-up angles to the Bias-Variance Tradeoff node (id=67)
per user request 2026-04-20:

1. Explicit cross-term expansion (after Derivation)
2. Loss-function prerequisite note (squared loss only; Domingos 2000 for classification)
3. Diagnostic Fingerprints subsection (train/val error pattern + learning-size curve
   gap behavior) — inserted between Diagnostic Curves and Regularization.
4. Capacity-knob framing sentence above the per-model table.
5. One-line regularization mechanism (effective hypothesis space contraction).
6. Remedies Quick-List above the big Remedies Matrix.

Idempotent: checks for sentinel markers before inserting. Safe to re-run.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 67

# --- Anchors & inserts ---------------------------------------------------

# 1 & 2: Cross-term expansion + loss caveat, inserted after the Derivation proof
ANCHOR_1 = "$$= \\text{Bias}^2 + \\text{Variance}$$\n\n### Model Complexity Spectrum"
INSERT_1_MARKER = "<!-- FOLLOWUP_20260420_DERIVATION_NOTES -->"
INSERT_1 = r"""$$= \text{Bias}^2 + \text{Variance}$$

<!-- FOLLOWUP_20260420_DERIVATION_NOTES -->

> **交叉项显式展开**（面试官常追问"写出这一步"）：$E_D[(f - \hat{f})\epsilon] = E_D[f - \hat{f}] \cdot E[\epsilon] = 0$，用到 $\epsilon$ 独立于 $D$ 且 $E[\epsilon]=0$。
>
> **损失函数前提**：该加法分解是 **Squared Loss (MSE) 专属**。**0-1 Loss** 与 **Cross-Entropy** 没有这么干净的形式（Domingos 2000 有推广版本，结构更复杂）——分类题不要强套这条公式。

### Model Complexity Spectrum"""

# 3: Diagnostic Fingerprints — inserted between Diagnostic Curves and Regularization
ANCHOR_3 = "（**Stochastic Gradient Descent** (SGD, 随机梯度下降) 隐式正则化、**Flat Minima** (平坦极小值) 等）。\n\n### Regularization as Bias-Variance Control"
INSERT_3_MARKER = "<!-- FOLLOWUP_20260420_DIAGNOSTIC_FINGERPRINTS -->"
INSERT_3 = r"""（**Stochastic Gradient Descent** (SGD, 随机梯度下降) 隐式正则化、**Flat Minima** (平坦极小值) 等）。

<!-- FOLLOWUP_20260420_DIAGNOSTIC_FINGERPRINTS -->

### Diagnostic Fingerprints（诊断指纹：High Bias vs High Variance）

先诊断再开处方——选错方向，后续措施全反。

| 观察维度 | High Bias（欠拟合） | High Variance（过拟合） |
|---------|---------------------|------------------------|
| Train error | 高 | 低（可接近 0） |
| Validation error | 高 | 高 |
| Train-Val gap | **小**（两条贴合） | **大**（拉开明显） |
| Learning Curve（误差 vs 训练集大小 $n$） | 两条汇聚于**同一较高 plateau**，加数据无效 | gap 随 $n$ 增大**持续收窄**，加数据见效 |

**口诀：gap 小而高 = 偏差；gap 大 = 方差。** 与上节复杂度曲线互补——复杂度曲线定位 U 形底，learning curve 判定"加数据 vs 换模型"。

### Regularization as Bias-Variance Control"""

# 4: Capacity-knob framing above per-model table
ANCHOR_4 = "### Bias-Variance for Different Models（不同模型的偏差-方差特性）\n\n| 模型 | 偏差 | 方差 | 调控手段 |"
INSERT_4_MARKER = "<!-- FOLLOWUP_20260420_CAPACITY_KNOB -->"
INSERT_4 = r"""### Bias-Variance for Different Models（不同模型的偏差-方差特性）

<!-- FOLLOWUP_20260420_CAPACITY_KNOB -->

**统一 framing**：每个经典模型都有一个**容量旋钮**——调大 = 低 bias / 高 variance，调小反之。面试官爱追问旋钮是谁，加两句记忆锚点：

- **KNN**：$k$ 就是旋钮；$k=1$ 极端低偏差高方差。
- **Decision Tree**：深度 / min_samples_leaf；深而未剪枝 = 低偏差高方差。
- **Polynomial Regression**：多项式阶数 $d$。
- **Random Forest**：**降 variance 的典型**（bagging + 降相关系数 $\rho$，偏差几乎不变）。
- **GBDT / XGBoost**：**降 bias 的典型**（序列拟合残差；方差靠 lr + early stopping + max_depth 控制）。

| 模型 | 偏差 | 方差 | 调控手段 |"""

# 5: One-line regularization mechanism
ANCHOR_5 = "- 最优的 $\\lambda$ 在两者之间，通过交叉验证选择\n\n### Ensemble Methods and Bias-Variance"
INSERT_5_MARKER = "<!-- FOLLOWUP_20260420_REG_ONELINER -->"
INSERT_5 = r"""- 最优的 $\lambda$ 在两者之间，通过交叉验证选择

<!-- FOLLOWUP_20260420_REG_ONELINER -->

**一句话机理**：正则化（L2 / Dropout / Weight Decay / Early Stopping）的本质是**收缩 effective hypothesis space** (有效假设类)——容量名义不变，但可达解的子集变小，相当于在 U 形曲线的容量轴上**把模型向左拉一档**，注入一点 bias 换更多 variance 下降。所以永远是"加正则 = 降方差"，不是"降偏差"。

### Ensemble Methods and Bias-Variance"""

# 6: Remedies Quick-List above the big matrix
ANCHOR_6 = "## Remedies Matrix（补救措施矩阵）\n\n面试现场拿到\"模型表现不好\"的提问时，**先定位是偏差问题还是方差问题，再从下表按列选择措施**。这张表把所有常见补救措施按\"降偏差 / 降方差 / 两者兼修\"三类对齐。"
INSERT_6_MARKER = "<!-- FOLLOWUP_20260420_REMEDIES_QUICKLIST -->"
INSERT_6 = r"""## Remedies Matrix（补救措施矩阵）

面试现场拿到"模型表现不好"的提问时，**先定位是偏差问题还是方差问题，再从下表按列选择措施**。这张表把所有常见补救措施按"降偏差 / 降方差 / 两者兼修"三类对齐。

<!-- FOLLOWUP_20260420_REMEDIES_QUICKLIST -->

### Remedies Quick-List（口述对照清单，白板先写这两行再展开矩阵）

- **降 Bias**：增大容量（深/宽/高阶）、加信号强的特征、**减弱**正则、训练更久、换更强模型族（线性 → 树 → NN）。
- **降 Variance**：**加数据**（真实 / 增广）、加正则（L1 / L2 / Dropout / Weight Decay）、Early Stopping、Bagging / RF、**降**容量（剪枝 / 减层 / 减宽）。

"""

EDITS = [
    ("derivation_notes", ANCHOR_1, INSERT_1_MARKER, INSERT_1),
    ("diagnostic_fingerprints", ANCHOR_3, INSERT_3_MARKER, INSERT_3),
    ("capacity_knob", ANCHOR_4, INSERT_4_MARKER, INSERT_4),
    ("reg_oneliner", ANCHOR_5, INSERT_5_MARKER, INSERT_5),
    ("remedies_quicklist", ANCHOR_6, INSERT_6_MARKER, INSERT_6),
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
            print(f"[FAIL] anchor missing for '{name}':\n---\n{anchor[:200]}\n---", file=sys.stderr)
            conn.close()
            return 2
        count = desc.count(anchor)
        if count != 1:
            print(f"[FAIL] anchor for '{name}' not unique: {count} occurrences", file=sys.stderr)
            conn.close()
            return 3
        desc = desc.replace(anchor, insert, 1)
        applied.append(name)

    if not applied:
        print(f"[SKIP] all {len(EDITS)} followups already present; description unchanged ({before_len} chars)")
        conn.close()
        return 0

    after_len = len(desc)
    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?", (desc, NODE_ID)
    )
    conn.commit()
    conn.close()

    print(f"[OK] node {NODE_ID} description {before_len} -> {after_len} chars (+{after_len - before_len})")
    print(f"[OK] applied: {', '.join(applied)}")
    if skipped:
        print(f"[SKIP] already present: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
