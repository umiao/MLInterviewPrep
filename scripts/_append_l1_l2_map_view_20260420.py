"""Append the MLE/MAP / Gaussian-vs-Laplace prior view to the L1 vs L2
Regularization leaf (framework_nodes.id=210, path
ml-fundamentals/classical_ml/l1-vs-l2-regularization).

Per user Discord 2026-04-20: the existing section 4 only states
'Laplace -> L1, Gaussian -> L2' as a table row. Augment with a
dedicated subsection right after section 4 covering:

- OLS = MLE under i.i.d. Gaussian noise
- Adding a prior on w -> MAP -> regularization
- Why Laplace is 'naturally sparse' (spike at 0 + heavy tail encodes
  'most features irrelevant, few strongly relevant')
- lambda = sigma^2 / prior_variance = 1 / signal-to-noise ratio

Inserted between the end of section 4 and '## 5. Elastic Net'.
Idempotent via sentinel marker.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 210

ANCHOR = "Bayesian 先验视角对应 **Maximum a Posteriori** (MAP, 最大后验) 估计：把正则化项看成对 $w$ 的对数先验，与无正则化的 **Maximum Likelihood Estimation** (MLE, 最大似然估计) 之差就是这个先验项。Laplace 先验下 MAP = L1，Gaussian 先验下 MAP = L2。\n\n## 5. 可能追问：Elastic Net"
INSERT_MARKER = "<!-- FOLLOWUP_20260420_MLE_MAP_PRIOR_VIEW -->"
INSERT = r"""Bayesian 先验视角对应 **Maximum a Posteriori** (MAP, 最大后验) 估计：把正则化项看成对 $w$ 的对数先验，与无正则化的 **Maximum Likelihood Estimation** (MLE, 最大似然估计) 之差就是这个先验项。Laplace 先验下 MAP = L1，Gaussian 先验下 MAP = L2。

<!-- FOLLOWUP_20260420_MLE_MAP_PRIOR_VIEW -->

### 深入：MLE / MAP 视角下的正则化

- **OLS = Gaussian 噪声假设下的 MLE**：假定残差 $\epsilon_n \sim \mathcal{N}(0, \sigma^2)$ 独立同分布，写出对数似然后去掉常数就是 $-\sum_n (y_n - x_n^\top w)^2 / (2\sigma^2)$——最大化它等价于最小化 OLS 目标。
- **加 $w$ 的先验 → MAP → 正则化**：$\hat{w}_{\text{MAP}} = \arg\max_w \ \log p(w) + \log p(y \mid w, X)$，多出来的 $\log p(w)$ 就是正则化项。
  - $w \sim \mathcal{N}(0, \tau^2 I)$（Gaussian 先验）→ 罚项 $\propto \|w\|_2^2$ → **L2 (Ridge)**
  - $w_i \sim \text{Laplace}(0, b)$（Laplace 先验）→ 罚项 $\propto \|w\|_1$ → **L1 (Lasso)**
- **Laplace 为何天生稀疏**：Laplace 密度在 $w_i=0$ 处有**尖峰**、尾部比 Gaussian **更重**（见下图脑内示意：Gaussian 是钟形光滑压峰、Laplace 是中间一根尖顶 + 两侧慢衰减）。先验层面就编码了"**绝大多数 feature 无关**（向 0 挤）+ **少数 feature 有强信号**（长尾允许大权重）"这一稀疏假设；Gaussian 尾部太薄，只能"全体向心压"，shrink 但压不到精确的 0。
- **$\lambda$ 的物理意义**：$\lambda = \sigma^2 / \tau^2$（噪声方差 / 先验方差），本质是**信噪比的倒数**——数据越噪（$\sigma$ 越大）或对 $w$ 越没把握（$\tau$ 越大，先验越 flat），$\lambda$ 越大 → 正则化越强。选 $\lambda$ 就是在估计 SNR。

一句话总结：**OLS 是 MLE，L2 / L1 是换两种先验后的 MAP；稀疏不是算法 trick 而是先验形状自带的属性。**

## 5. 可能追问：Elastic Net"""


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

    if INSERT_MARKER in desc:
        print(f"[SKIP] marker already present; description unchanged ({before_len} chars)")
        conn.close()
        return 0

    if ANCHOR not in desc:
        print("[FAIL] anchor not found in node 210 description", file=sys.stderr)
        conn.close()
        return 2

    if desc.count(ANCHOR) != 1:
        print(f"[FAIL] anchor not unique: {desc.count(ANCHOR)} occurrences", file=sys.stderr)
        conn.close()
        return 3

    new_desc = desc.replace(ANCHOR, INSERT, 1)
    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?", (new_desc, NODE_ID)
    )
    conn.commit()
    conn.close()

    print(f"[OK] node {NODE_ID} description {before_len} -> {len(new_desc)} chars (+{len(new_desc) - before_len})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
