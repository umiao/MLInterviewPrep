"""Apply 3 interview-depth followups to EM + GMM leaf node 216
(path: ml-fundamentals/unsupervised/em-and-gmm).

Per user Discord 2026-04-20:
  A. After the E-step responsibility formula, add a note clarifying
     that the ratio is between probability DENSITIES (not probabilities),
     and that the dx in both numerator and denominator cancels — so
     densities can be used directly. Address the natural "can gamma_{nk}
     exceed 1?" question.
  B. Expand the 'how to choose K' bullet in section 6: separate BIC,
     AIC, and held-out likelihood with concrete formulas / trade-offs.
  C. Expand the DPMM reference with: (1) under what condition a new K
     is triggered (CRP posterior predictive comparison), (2) how
     assignment parameters update (Gibbs / variational stick-breaking),
     and the role of the concentration parameter alpha.

Idempotent via sentinel markers. Each edit is guarded by a unique
HTML comment so re-running is safe.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 216

# --- Insert A: density-ratio note after the responsibility formula -------
ANCHOR_A = "就是 Bayes 规则。直觉：样本 $n$ 有多大比例\"属于\"分量 $k$。\n\n**M 步 — 加权 MLE**"
MARKER_A = "<!-- FOLLOWUP_20260420_DENSITY_RATIO_NOTE -->"
INSERT_A = r"""就是 Bayes 规则。直觉：样本 $n$ 有多大比例"属于"分量 $k$。

<!-- FOLLOWUP_20260420_DENSITY_RATIO_NOTE -->

> **为什么能直接用密度之比？**（常见追问）分子分母都是**概率密度** (probability density) 而不是概率；对连续 $x$，要用严格的条件概率定义应该写成
>
> $$\gamma_{nk} = \lim_{\mathrm{d}x \to 0} \frac{\pi_k\, \mathcal{N}(x_n \mid \mu_k, \Sigma_k)\,\mathrm{d}x}{\sum_j \pi_j\, \mathcal{N}(x_n \mid \mu_j, \Sigma_j)\,\mathrm{d}x}$$
>
> 分子分母里的 $\mathrm{d}x$ **完全一样**、直接约掉，就得到密度之比——这就是"为什么可以用密度公式代入 Bayes 规则"的严格依据。另一个容易踩的点：**单个密度值 $\mathcal{N}(x \mid \mu_k, \Sigma_k)$ 可以 >1**（窄分量更明显），但经过分母归一化后 $\gamma_{nk} \in [0, 1]$ 且 $\sum_k \gamma_{nk} = 1$，仍然是合法概率。

**M 步 — 加权 MLE**"""

# --- Insert B+C: replace the combined 'choose K' bullet with two
# expanded bullets (BIC/AIC/held-out + DPMM).
ANCHOR_BC = "- **怎么选 K**：BIC / AIC，或跑 `BayesianGaussianMixture`（**Dirichlet Process Mixture Model**，DPMM，狄利克雷过程混合模型）把 K 设得偏大让它自动压掉多余分量。"
MARKER_BC = "<!-- FOLLOWUP_20260420_K_SELECTION_AND_DPMM -->"
INSERT_BC = r"""<!-- FOLLOWUP_20260420_K_SELECTION_AND_DPMM -->
- **怎么选 K**——三种主流做法各有适用场景：
  - **BIC** (贝叶斯信息准则) $= -2 \log \hat{L} + p \log N$，其中 $p$ 是自由参数数 ($K-1 + K \cdot d + K \cdot d(d+1)/2$ for full covariance)、$N$ 是样本数。扫 $K = 1 \ldots K_{\max}$ 取 BIC 最小者；$\log N$ 罚项较重，倾向保守的 $K$。样本多时更可靠。
  - **AIC** (赤池信息准则) $= -2 \log \hat{L} + 2p$。罚项 $2 < \log N$（当 $N > 7$），比 BIC 更"宽容"，倾向选略大的 $K$；样本少或关注预测误差的场景下更合适。
  - **Held-out likelihood**：train/val 切分，$K^* = \arg\max_K \log p(x_{\text{val}} \mid \hat{\theta}_K^{\text{train}})$。不需要显式参数罚项、思路最易解释（和 cross-validation 一致），**面试首选答案**；缺点是需要 val set 且受切分方差影响。
  - 实战：三者一起跑，看"最佳 $K$"落在哪个 plateau；三者严重分歧说明数据不足或模型 mis-specified，要回头换假设（如 tied covariance）而不是硬选数字。
- **Dirichlet Process Mixture Model (DPMM, 狄利克雷过程混合模型)**——让 $K$ 自适应增长，把"选 K"从模型选择问题**内化成参数推断**：
  - **触发新分量的条件**（Chinese Restaurant Process, CRP 视角）：第 $n$ 个样本分配到第 $k$ 桌的未归一化概率是 $N_k \cdot p(x_n \mid \theta_k)$（坐已有桌，权重 = 当前人数 × 在该分量下的似然）；分配到**新桌**的未归一化概率是 $\alpha \cdot \int p(x_n \mid \theta)\, p(\theta \mid G_0)\, \mathrm{d}\theta$（开新桌，权重 = concentration $\alpha$ × 新参数采自 base measure $G_0$ 后的边际似然）。只有当**已有所有分量都解释得很差**、且 $\alpha \cdot$ 边际似然相对更高时，才触发开新 $K$。
  - **concentration parameter $\alpha$**：$\alpha$ 大 → 爱开新桌，最终分量多且碎；$\alpha$ 小 → 收敛到少数大分量。$\alpha$ 自身通常再放 Gamma 先验同时采样。
  - **参数如何更新**：
    - **Gibbs sampling**：轮流对每个点重采 $z_n$（按上面的 CRP 条件概率）→ 对每个分量用当前成员重采 $\theta_k$（Gaussian-Inverse-Wishart 共轭让后验采样闭式）。
    - **Variational (scikit-learn `BayesianGaussianMixture`)**：truncated stick-breaking 设一个 $K_{\max}$ 上界 + mean-field 近似，迭代更新每个分量的 $(\pi_k, \mu_k, \Sigma_k)$ 的变分参数；多余分量的 $\pi_k$ 会被自动压向 0（"自动选 K"的实现方式），收敛速度远快于 Gibbs。
  - **一句话**：DPMM 把 "K 是超参数" 变成 "$\alpha$ 是超参数"，但 $\alpha$ 的影响比 $K$ 平滑得多。"""


EDITS = [
    ("density_ratio_note", ANCHOR_A, MARKER_A, INSERT_A),
    ("k_selection_and_dpmm", ANCHOR_BC, MARKER_BC, INSERT_BC),
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
