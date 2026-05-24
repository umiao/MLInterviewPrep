"""Seed: T-P0-686 [MLI-B] -- Append vanilla random-init helper to K-Means notes.

Targets problems.id=1064 ("K-Means Pure Python Implementation (K-Means++)").
Adds a parallel `_init_centers_random` utility plus a contrast block covering
failure modes, distance-weighted sampling intuition, and the precise
Arthur-Vassilvitskii (2007) K-Means++ guarantee. Does NOT modify the existing
`_init_centers_plusplus` or `fit()` flow -- the new section is appended at the
end of the markdown body.

Idempotency:
- Sentinel `<!-- KMEANS_VANILLA_INIT_20260502 -->` gates the UPSERT.
- Second run: if sentinel present AND the substring from the sentinel onwards
  is byte-equal to the canonical addendum, [SKIP] with 0 writes. If sentinel
  present but bytes differ (drift), the addendum is rewritten in place.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
PROBLEM_ID = 1064
SENTINEL = "<!-- KMEANS_VANILLA_INIT_20260502 -->"

ADDENDUM = r"""

---

<!-- KMEANS_VANILLA_INIT_20260502 -->

### 附录: Vanilla Random Init 对照实现 (Forgy method)

教学性补充: 与 K-Means++ 并列对照, 看清"距离加权采样 (distance-weighted
sampling)"为何关键. 不替换 `fit()` 的初始化流程, 仅作为可选的 sibling
helper 给出, 现有 `_init_centers_plusplus` 与 4 种停止条件保持原状.

```python
def _init_centers_random(self, data: np.ndarray) -> np.ndarray:
    # Vanilla random initialization (Forgy method).
    # 从 data 中均匀无放回 (uniform without replacement) 采样 K 个真实
    # 数据点作为初始 centers; 与 K-Means++ 仅在"如何挑后续 K-1 个 center"
    # 这一步上有差异.
    #
    # 为什么是"从数据点中采样" 而非"在 bounding box 内均匀采坐标":
    #   - bounding box 采样 (在每个维度的 [min, max] 内独立均匀) 会在
    #     数据稀疏区域生成 centers, 首轮 E-step 极易出现"无最近点"的
    #     empty cluster.
    #   - 对 non-convex / 流形结构 (manifold-shaped) 的簇尤其糟糕 ——
    #     bounding box 内绝大多数体积都落在所有真实簇之外, 初始 center
    #     完全无意义, M-step 计算 cluster mean 时会触发空 cluster fallback.
    #   - 直接从 data 采样保证每个初始 center 都"在数据流形上",
    #     至少初始那一个点本身就属于它自己的 cluster, 不会立刻空掉.
    num_samples = data.shape[0]
    # replace=False: 同一个 data point 不会成为两个 initial centers
    # (否则首轮就有两个完全重合的 centers, 等价于 K-1 个簇).
    chosen_idx = self.rng.choice(
        num_samples, size=self.num_clusters, replace=False
    )
    return data[chosen_idx]
```

#### Vanilla Random vs. K-Means++ 三大差异

**1. Failure modes (失败模式)**

- **Empty clusters**: 两个随机 centers 恰好挨得很近, 离它们最近的点都被
  其中一个抢走 -> 另一个空, M-step 算 mean 时除以 0. 本实现的
  `_recompute_centers` 用 random fallback 顶住, 但等价于"丢掉一个 K
  并重启", 收敛质量打折.
- **Local-optima dependence on seed**: 不同 `random_state` 收敛到不同
  SSE (sum of squared errors). 实战需要 multi-restart (sklearn 默认
  `n_init=10`, 取 SSE 最小的那次), K-Means++ 通常 `n_init=1` 就够.
- **Slow convergence**: centers 初始挤在一起时, 头几轮 E-step / M-step
  都在重新分布 centers, 总迭代数显著增加.

**2. Probabilistic distance-weighted sampling (K-Means++ 的概率距离加权)**

K-Means++ 的第一个 center 仍是均匀随机, 之后的 K-1 个按下式采样:

$$P(x \text{ as next center}) \propto D(x)^2, \quad D(x) = \min_{c \in \text{chosen}} \|x - c\|$$

- $D(x)^2$ 加权让采样**偏向"现有 centers 覆盖不足的区域" (under-covered
  regions)** —— 距离越远, 被选概率越大 (按平方放大), 自然把 centers 推开.
- 这是一个**软化的 Farthest Point Sampling (FPS)**: FPS 是
  `argmax D(x)` (deterministic), K-Means++ 是按 $D(x)^2$ 抽样
  (stochastic). 软化的好处是对 **outliers 鲁棒** —— 一个孤立的 outlier
  在 FPS 下必被选中, 在 K-Means++ 下只是"概率较高", 不会必然主导.
- 代价: 每选一个 center 都要重算所有点到最近 center 的 D, 总复杂度
  $O(N \cdot K \cdot d)$, 但相对 Lloyd 主循环 $O(N \cdot K \cdot d \cdot T)$
  完全可忽略.

**3. Theoretical guarantee (Arthur & Vassilvitskii, 2007)**

精确陈述 (避免常见的"O(log K) bound"误传 —— 它不是 worst-case 上界,
也不是渐近意义上的, 而是带常数的期望竞争比):

$$\mathbb{E}[\phi] \leq 8(\ln k + 2) \cdot \phi_{\text{OPT}}$$

其中:
- $\phi$ 是 K-Means++ **初始化结束时**(0 次 Lloyd 迭代)的 SSE.
- $\phi_{\text{OPT}}$ 是该数据集上**任意聚类**的最优 SSE (NP-hard 求解).
- $\mathbb{E}[\cdot]$ 是对 K-Means++ 内部随机抽样的期望.

意义: 仅靠 init 阶段, K-Means++ 就把期望 SSE 控制在最优解的
$8(\ln k + 2)$ 倍以内 —— 这是一个 **expected $O(\log k)$
competitive ratio**. 之后再跑 Lloyd 迭代只会让 SSE 单调下降, 所以最终
聚类质量也享有同样量级的保证.

Vanilla random init **没有任何此类保证** —— 最坏情况下, SSE 可以是最优
的任意倍数 (paper 给了构造性反例: K 个等距簇, random init 把所有 centers
都丢进同一个簇时 SSE 趋于 $\Theta(N)$ 倍最优).

参考: Arthur, D., & Vassilvitskii, S. (2007). *k-means++: The Advantages
of Careful Seeding*. SODA 2007 (Proceedings of the eighteenth annual
ACM-SIAM symposium on Discrete algorithms), pp. 1027-1035.

#### 何时还会刻意选 vanilla random?

- **教学场景**: 让学生先看到 random init 的 empty cluster / 慢收敛,
  再引出 K-Means++ 的"为什么要这样改".
- **数据极大且 K 极小**, 想省掉 K-Means++ 的 $O(N \cdot K)$ init 开销
  (实践中很少, 一次 init 量级远小于 Lloyd 主循环).
- **配合 `n_init >> 1` 的 multi-restart 策略**, 用算力换"碰巧好的种子"
  (sklearn `KMeans(init='random', n_init=50)` 即此思路).
- **需要可复现的 baseline 对照**, 论文里报告 K-Means++ 提升幅度时常用
  vanilla random 作为下界对照.
"""


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT id, title, notes FROM problems WHERE id = ?",
            (PROBLEM_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] No row for problems.id={PROBLEM_ID}")
            return 1
        pid, title, old_notes = row
        old_notes = old_notes or ""

        if SENTINEL in old_notes:
            if old_notes.endswith(ADDENDUM):
                print(
                    f"[SKIP] id={pid} sentinel present and addendum byte-equal "
                    f"(notes_len={len(old_notes)})"
                )
                return 0
            sentinel_idx = old_notes.find(SENTINEL)
            # Trim back to before the addendum's leading "\n\n---\n\n" separator.
            sep = "\n\n---\n\n"
            cut = old_notes.rfind(sep, 0, sentinel_idx)
            prefix = old_notes[:cut] if cut != -1 else old_notes[:sentinel_idx]
            new_notes = prefix.rstrip() + ADDENDUM
            action = "REWRITE"
        else:
            new_notes = old_notes.rstrip() + ADDENDUM
            action = "APPEND"

        conn.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (new_notes, pid),
        )
        conn.commit()

        check = conn.execute(
            "SELECT notes FROM problems WHERE id = ?", (pid,)
        ).fetchone()[0]
        if SENTINEL not in check:
            print("[FAIL] Sentinel missing after write")
            return 1

        print(
            f"[{action}] id={pid} '{title}' notes "
            f"{len(old_notes)} -> {len(new_notes)} chars"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
