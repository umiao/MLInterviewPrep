"""Minimal-diff clarification on node 222 (ml-fundamentals/classical_ml/
cross-entropy-kl-divergence):

Per user Discord 2026-04-20: common conflation of KL divergence with
Earth Mover's Distance / Wasserstein. Add two small, targeted edits:

1. Section 1 KL definition -- a one-line caveat that KL is
   information-theoretic, not geometric; the 'moving dirt' image
   belongs to Wasserstein.
2. Section 7 Wasserstein bullet -- expand with: (a) EMD = Wasserstein
   W_1 identity, (b) concrete contrast (P=delta_0 vs Q=delta_1000 and
   Q=delta_1 give identical KL but very different W_1), (c) explicit
   'moving dirt intuition belongs to Wasserstein, not KL'.

Idempotent via sentinel markers.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 222

# --- Insert 1: one-line caveat right after KL 'asymmetric distance' line ---
ANCHOR_1 = "$\\ge 0$，当且仅当 $P = Q$ 时 $= 0$。非对称：$D_{\\text{KL}}(P \\| Q) \\ne D_{\\text{KL}}(Q \\| P)$。"
MARKER_1 = "<!-- FOLLOWUP_20260420_KL_NOT_EMD -->"
INSERT_1 = r"""$\ge 0$，当且仅当 $P = Q$ 时 $= 0$。非对称：$D_{\text{KL}}(P \| Q) \ne D_{\text{KL}}(Q \| P)$。

<!-- FOLLOWUP_20260420_KL_NOT_EMD -->

> **KL 不是"搬土距离"**（常见误会）：这里说的"距离"是**信息论意义**上的（用 $Q$ 的最优编码去编码 $P$ 的样本时平均多花的比特数），**不是几何距离**。KL 完全不 care 样本空间里 $i$ 之间的距离有多远——"搬土 / Earth Mover" 的直觉属于 **Wasserstein** (见下方 §7)，不能套到 KL 上。记忆锚点：**KL = 赌注比率 / 编码代价；Wasserstein = 搬运成本**。"""

# --- Insert 2: replace the short Wasserstein bullet with an expanded version ---
ANCHOR_2 = "**Wasserstein distance**：KL / JS 在两个分布几乎不重叠时会爆炸或饱和（GAN 训练不稳的根源）。Wasserstein 度量考虑\"运输成本\"，即使无重叠也给出有意义的梯度，**Wasserstein GAN** (WGAN, Wasserstein 生成对抗网络) 用的就是它。"
MARKER_2 = "<!-- FOLLOWUP_20260420_WASSERSTEIN_EMD_CONTRAST -->"
INSERT_2 = r"""<!-- FOLLOWUP_20260420_WASSERSTEIN_EMD_CONTRAST -->

**Wasserstein distance / Earth Mover's Distance (EMD)**：**"搬土距离" EMD 就是 Wasserstein** $W_1$（同一个量的两种叫法——直觉叫法 vs 数学叫法）。把 $P$、$Q$ 当成两堆沙子，$W_1(P, Q)$ = 把 $P$ 搬运成 $Q$ 的最小"质量 × 距离"工作量，**依赖样本空间的几何**，是真正的距离（对称 + 三角不等式）。

- **与 KL 的关键差别（具体例子）**：$P = \delta_{0}$、$Q_A = \delta_{1000}$、$Q_B = \delta_{1}$——$D_{\text{KL}}(P \| Q_A) = D_{\text{KL}}(P \| Q_B) = \infty$（support 不交，KL 两种情况完全一样）；而 $W_1(P, Q_A) = 1000$、$W_1(P, Q_B) = 1$，敏感度差别巨大。KL 只看概率值的**比例**、不看 $i$ 之间的**距离**；Wasserstein 反之。
- **WGAN 动机**：训练初期真实 / 生成分布 support 几乎必然不重叠 → KL / JS 给常数或 $\infty$、梯度消失；Wasserstein 仍然随分布距离**平滑变化**、梯度有意义——这就是 **Wasserstein GAN** (WGAN) 的核心动机。"""


EDITS = [
    ("kl_not_emd", ANCHOR_1, MARKER_1, INSERT_1),
    ("wasserstein_contrast", ANCHOR_2, MARKER_2, INSERT_2),
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
            print(f"[FAIL] anchor for '{name}' not unique: {desc.count(anchor)} occurrences", file=sys.stderr)
            conn.close()
            return 3
        desc = desc.replace(anchor, insert, 1)
        applied.append(name)

    if not applied:
        print(f"[SKIP] all {len(EDITS)} edits already present ({before_len} chars)")
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
