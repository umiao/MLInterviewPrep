"""Insert the formal Kantorovich primal + Kantorovich-Rubinstein dual
definitions of Wasserstein distance into node 222
(ml-fundamentals/classical_ml/cross-entropy-kl-divergence), right after
the intro sentence of the expanded Wasserstein bullet and before the
KL-contrast example bullet.

Per user Discord 2026-04-20 follow-up (msg 1495989626878300160).

Idempotent via sentinel marker.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 222

# Anchor: end of the intro sentence added in commit 2c091e3, immediately
# before the '与 KL 的关键差别' bullet.
ANCHOR = "依赖样本空间的几何**，是真正的距离（对称 + 三角不等式）。\n\n- **与 KL 的关键差别（具体例子）**"
MARKER = "<!-- FOLLOWUP_20260420_WASSERSTEIN_FORMAL_DEF -->"
INSERT = r"""依赖样本空间的几何**，是真正的距离（对称 + 三角不等式）。

<!-- FOLLOWUP_20260420_WASSERSTEIN_FORMAL_DEF -->

**Formal 定义 — Kantorovich Primal (最优传输形式)**：

$$W_p(P, Q) = \left( \inf_{\gamma \in \Pi(P, Q)} \int_{\mathcal{X} \times \mathcal{X}} d(x, y)^p \, \mathrm{d}\gamma(x, y) \right)^{1/p}$$

其中 $\Pi(P, Q)$ 是所有以 $P$、$Q$ 为边缘分布的**联合分布**（coupling / transport plan）的集合；$\gamma(x, y)$ 表示"从 $x$ 搬多少质量到 $y$"（所以约束是 $\int \gamma(x, \cdot) \mathrm{d}y = P(x)$、$\int \gamma(\cdot, y) \mathrm{d}x = Q(y)$）；$d(x, y)^p$ 是单位质量的搬运代价，$d$ 通常取 Euclidean。$p = 1$ 就是 **EMD / $W_1$**。

**Kantorovich–Rubinstein Dual** — WGAN 实际优化的形式（$p = 1$）：

$$W_1(P, Q) = \sup_{\|f\|_L \le 1} \ \mathbb{E}_{x \sim P}[f(x)] - \mathbb{E}_{x \sim Q}[f(x)]$$

$\sup$ 取遍所有 **1-Lipschitz** 函数 $f$（即 $|f(x) - f(y)| \le d(x, y)$）。WGAN 的 critic 就在学这个 $f$——原始 WGAN 用 weight clipping、WGAN-GP 用 gradient penalty，都是在强制 1-Lipschitz 约束；dual 形式让 $W_1$ 可以用 stochastic gradient descent 优化。

- **与 KL 的关键差别（具体例子）**"""


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

    if MARKER in desc:
        print(f"[SKIP] marker already present ({before_len} chars)")
        conn.close()
        return 0

    if ANCHOR not in desc:
        print("[FAIL] anchor not found in node 222 description", file=sys.stderr)
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
