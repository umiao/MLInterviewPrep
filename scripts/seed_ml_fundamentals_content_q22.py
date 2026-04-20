"""Seed: T-P0-544 -- ML Fundamentals Y-depth Q#22 MoE routing + load balancing.

[T-MLF-06b] Applies the calibrated Y-depth template (locked in T-P0-543
zeta1 review) to Question 22 (MoE routing and load-balancing aux loss)
into framework_nodes.description for the leaf at path
'ml-fundamentals/llm_stats/moe-routing-load-balancing'.

Y-depth = deep expansion. Per the 5-section template:

  1. 问题设定       -- MoE definition, routing as a sparse-dispatch
                       problem, load-balancing motivation.
  2. 推导           -- top-k gating softmax; Switch Transformer aux
                       loss L_aux = alpha * N * sum(f_i * P_i) with
                       f_i = token fraction (non-differentiable) and
                       P_i = mean router prob (differentiable); why
                       f * P is a differentiable surrogate for the
                       variance of load; capacity factor + drop-token.
  3. 物理意义       -- expert-collapse feedback loop; why uniform
                       minimizes f_i * P_i; capacity factor tradeoff;
                       differences between Switch (k=1) and Mixtral
                       (k=2) in aux-loss behavior.
  4. 常见追问预判   -- 6 items (k=1 vs k=2; router z-loss; batch-
                       level vs sequence-level balancing; inference
                       cost; MoE fine-tuning instability; why dense
                       soft-routing lost).
  5. 参考           -- 4+ paper refs (Shazeer 2017, Fedus 2021 Switch,
                       Lepikhin 2020 GShard, Jiang 2024 Mixtral,
                       Zoph 2022 ST-MoE).

Acronyms first-occurrence expanded in bold **English** (acronym, 中文)
per data/ml_fundamentals_inventory.yaml acronyms_to_expand: MoE, TopK.
Additional first-occurrence acronyms inline: FFN, GShard, FLOPs.

Idempotency:
  - Expected description is a single raw-string constant.
  - Second run yields updated=0 skipped=1 conflict=0.
  - SHA-256 of (path, description) captured pre/post for audit.
  - If the existing description is neither the placeholder
    'TODO[MLF-moe-routing-load-balancing]' nor the new content,
    script aborts with [CONFLICT] before any write.

Acceptance:
  - framework_nodes row at path
    'ml-fundamentals/llm_stats/moe-routing-load-balancing' updated.
  - Description contains KaTeX math ($ or $$) and section headers (## ).
  - Re-run is no-op (updated=0).
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

TARGET_PATH = "ml-fundamentals/llm_stats/moe-routing-load-balancing"
PLACEHOLDER = "TODO[MLF-moe-routing-load-balancing]"


DESC_MOE_ROUTING = r"""# MoE 路由与负载均衡损失

## 1. 问题设定

**Mixture of Experts** (MoE, 专家混合) 的核心想法是**条件计算**（conditional computation）：用一个稀疏的门控网络把每个 token 分派给 $N$ 个专家子网络中的少数几个，只对被选中的专家做前向/反向。这样参数总量可以做到 $N\times$ 但每 token 的计算量与单个专家相当——从 Transformer 的角度看，就是把密集的 **Feed-Forward Network** (FFN, 前馈网络) 块替换成"$N$ 个 FFN + 一个路由器"的稀疏块。

形式化：输入 token 表示 $x \in \mathbb{R}^{d}$，有 $N$ 个专家 $\{E_1, \ldots, E_N\}$，每个 $E_i: \mathbb{R}^d \to \mathbb{R}^d$。路由器 $W_r \in \mathbb{R}^{N \times d}$ 给出门控 logits $W_r x$，经过 softmax 得到概率 $p(x) \in \Delta^{N-1}$。**Top-K routing** (TopK, 取前 K 路由) 只保留概率最大的 $k$ 个专家（$k \ll N$）：

$$\mathrm{MoE}(x) \;=\; \sum_{i \in \mathrm{TopK}(p(x),\,k)} \tilde{p}_i(x)\cdot E_i(x)$$

其中 $\tilde{p}_i$ 是 TopK 保留下来的概率重归一化（除以被选中概率之和）。$k=1$ 是 Switch Transformer，$k=2$ 是 GShard / Mixtral。

**负载均衡问题**的来源：朴素训练下路由器会陷入**expert collapse**（专家坍塌）——少数几个专家接走绝大部分 token，其它专家拿不到梯度，进一步退化为死专家。表现是训练 loss 停滞、参数利用率低、评估效果接近稠密小模型。因此需要显式的**负载均衡辅助损失**（load-balancing auxiliary loss）强制门控把 token 分布拉均匀。

| 组件 | 形状 / 维度 | 角色 |
|------|-----------|------|
| 路由器 $W_r$ | $N \times d$ | 对 token 输出专家 logits |
| $p(x) = \mathrm{softmax}(W_r x)$ | $\Delta^{N-1}$ | 软分配概率 |
| 专家 $E_i$ | FFN 或任意子模块 | 真正做计算 |
| 容量因子 $C$ | 标量（$\ge 1$） | 每专家可处理 token 数上限 |
| 辅助损失 $\mathcal{L}_{\text{aux}}$ | 标量 | 拉均匀 + 防坍塌 |

## 2. 推导

### 2.1 Top-K 门控

给定一个 batch 的 $T$ 个 token $\{x_t\}_{t=1}^{T}$，路由 logits 和概率：

$$g_i(x_t) = (W_r x_t)_i,\qquad p_i(x_t) = \frac{\exp(g_i(x_t))}{\sum_{j=1}^{N} \exp(g_j(x_t))}$$

定义 TopK 指示：对每个 $x_t$，记 $\mathcal{T}_k(x_t) = \{i : p_i(x_t) \in \text{top-}k\}$。稀疏门控为

$$\hat{p}_i(x_t) \;=\; \begin{cases} p_i(x_t) / \sum_{j \in \mathcal{T}_k(x_t)} p_j(x_t), & i \in \mathcal{T}_k(x_t) \\ 0, & \text{else}\end{cases}$$

前向 $\mathrm{MoE}(x_t) = \sum_i \hat{p}_i(x_t) E_i(x_t)$。梯度**只沿被选中的 $k$ 个专家**反传，这也是 MoE 省算力的来源。

### 2.2 Switch Transformer 的 $L_{\text{aux}} = \alpha N \sum f_i P_i$ 推导

理想的负载均衡目标是让"每个专家接到的 token 数"均等。直接目标是最小化 token 分布向量 $f = (f_1, \ldots, f_N)$ 的方差（或等价的 $\ell_2$ 范数）：

$$f_i \;=\; \frac{1}{T}\,\sum_{t=1}^{T} \mathbf{1}\!\big[i \in \mathcal{T}_k(x_t)\big] \quad \text{(token fraction to expert }i\text{)}$$

问题：$f_i$ 通过 argmax（即 TopK 选择）计算，**对 $W_r$ 不可导**——TopK 是硬选，路由梯度通不过来。

**Switch Transformer** 的解决方案（Fedus 2021）：引入一个**可导的代理** $P_i$——每个专家在整个 batch 上的**平均软概率**：

$$P_i \;=\; \frac{1}{T}\,\sum_{t=1}^{T} p_i(x_t) \quad \text{(mean router probability to expert }i\text{)}$$

$P_i$ 用的是连续 softmax 概率，**对 $W_r$ 完全可导**。辅助损失取两者的**内积**：

$$\boxed{\;\mathcal{L}_{\text{aux}} \;=\; \alpha\,N\,\sum_{i=1}^{N} f_i \cdot P_i\;}$$

$\alpha$ 是权重（通常 $10^{-2}$），乘 $N$ 让 loss 的最小值与 $N$ 无关（见下）。反向传播时 $f_i$ 当常数（只是个"打卡记录"），只通过 $P_i$ 把梯度送回路由器，推动 $P_i$ 在"被分到 token 多的专家 $i$"上减小——等价于把下次 token 从拥挤专家推开。

**最小值分析**：由 Cauchy-Schwarz 或直接拉格朗日求解，在约束 $\sum f_i = k$（每个 token 分到 $k$ 个专家，token 总数 $T$ 归一到 $k$）、$\sum P_i = 1$ 下，$\sum f_i P_i$ 在 $f$ 与 $P$ 都**均匀分布** $f_i = k/N,\,P_i = 1/N$ 时取最小：

$$\min \sum_{i} f_i P_i \;=\; N \cdot \frac{k}{N} \cdot \frac{1}{N} \;=\; \frac{k}{N}$$

所以 $\mathcal{L}_{\text{aux}}^{\min} = \alpha \cdot N \cdot k/N = \alpha k$——与 $N$ 无关，仅与 $k$ 相关。这就是为什么原论文写成"$\alpha N \sum f_i P_i$"的形式：归一化让超参 $\alpha$ 在不同 $N$ 下可迁移。极端失衡时（所有 token 到一个专家）$f_i P_i$ 只有一个非零项，且 $f_i P_i \approx 1 \cdot 1 = 1$，于是 $\mathcal{L}_{\text{aux}} \approx \alpha N$，随 $N$ 线性放大——强惩罚。

### 2.3 容量因子与 token 丢弃

即便辅助损失把平均分布拉均匀，每个 batch 内仍可能有短时不均衡。为了让每个专家并行计算能固定 tile 大小（静态形状对 GPU/TPU 很重要），MoE 把每个专家的**处理上限**设为：

$$\text{capacity}_i \;=\; \lceil C \cdot k \cdot T / N \rceil$$

$C \ge 1$ 是**容量因子**（capacity factor）。当分到某专家的 token 数超出 capacity，多出来的 token 被**丢弃**（drop），其 MoE 输出以 residual 形式直通到下一层，不经过任何专家计算。

- $C=1.0$：理论均匀时刚好装下，一有波动就丢 token；训练速度快但有精度损失。
- $C=1.25$~$2.0$：常见训练值，允许 25%-100% 缓冲；Switch 用 $C=1.25$ 训练、$C=2.0$ 推理。
- $C \to \infty$：不丢 token，但 tile 要预留最坏情况的大小，浮点运算量 **FLoating-point OPerations** (FLOPs, 浮点运算次数) 上升、效率下降。

drop 的 token 数是 $\mathcal{L}_{\text{aux}}$ 之外的另一个监控指标（drop rate）——训练早期可以到 10%-20%，随训练下降到 <1%。

### 2.4 Router z-loss：数值稳定的正则

Switch 和 ST-MoE（Zoph 2022）观察到：路由 softmax 的 logit 幅度会慢慢 drift 到很大值（因为 $W_r$ 学着"自信分配"），半精度下 $\exp(g_i)$ 会溢出到 inf/NaN。**z-loss** 额外加一项：

$$\mathcal{L}_{z} \;=\; \gamma \cdot \frac{1}{T}\sum_{t=1}^{T} \Big(\log \sum_{i} \exp(g_i(x_t))\Big)^2$$

即惩罚 log-sum-exp（softmax 的配分函数）的大小，把 logits 拉回 $O(1)$。$\gamma \sim 10^{-3}$。这个损失不改变分布形状（相加常数不变分布），只限制绝对幅度。

## 3. 物理意义

### 3.1 为什么 $f \cdot P$ 是方差的可导代理

想让 $f$ 均匀，直接目标是最小化 $\sum_i (f_i - k/N)^2 = \sum f_i^2 - $ const。但 $f_i$ 不可导，所以用**协变量** $P_i$（可导，且与 $f_i$ 正相关——$P$ 高的专家更容易被 TopK 选中，从而 $f$ 也高）来替身。$\sum f_i P_i$ 可以理解成 $f$ 和 $P$ 的**未中心化协方差**：两者都向同一专家倾斜时乘积很大，都分散时乘积很小。对 $P_i$ 求梯度会把概率从已经分到很多 token 的专家上搬走——这正是想要的"流出拥挤专家"效果。

这个设计的聪明之处：$f$ 提供"真实信号"（实际分派情况），$P$ 提供"可导把手"（可以反传到 $W_r$）。如果只用 $\sum P_i^2$，惩罚的是 softmax 的 sharpness 而非实际失衡；如果能让 $f$ 可导（用 Gumbel-TopK 等技巧），就不需要 $P$ 了——但代价是更复杂的采样机制。Switch 的选择是**以最简单的方式把不可导信号嫁接到可导代理**。

### 3.2 专家坍塌的正反馈循环

坍塌不是随机坏运气，而是**路由决策与专家训练的正反馈**：

1. 初始化时某专家 $E_i$ 恰好对某类 token 响应更强 → 路由器 logit 偏向 $E_i$。
2. $E_i$ 拿到更多 token → 梯度更多 → 在这类 token 上学得更好 → 对它们响应更强。
3. 回到 1，放大。其它专家因拿不到这类 token 而停留在初始化附近，变成"死专家"。

$\mathcal{L}_{\text{aux}}$ 打断循环：一旦 $E_i$ 开始独占，$P_i \uparrow f_i \uparrow$，$\mathcal{L}_{\text{aux}}$ 项 $f_i P_i$ 快速增长，梯度把 $P_i$ 压下来。$\alpha$ 太小则不足以压制（看到 drop rate 高 + 少数专家占主导）；太大则牺牲路由质量（专家内容不分化，退化为随机路由）。

### 3.3 Switch ($k=1$) vs Mixtral ($k=2$) 的工程差异

- **Switch**（Fedus 2021）：$k=1$，每 token 只去一个专家。计算省（只算 1 个 FFN），负载最"硬"——任何不均都会在 capacity 上表现；训练 tricks 多（抖动路由、precision trade-off）。
- **Mixtral**（Jiang 2024）：$k=2$，每 token 去两个专家。计算略多（2 个 FFN），但两个专家分担让负载平滑很多；梯度路径双份，训练更稳。Mistral 8×7B 和 Mixtral 8×22B 都是 $k=2$。
- **GShard**（Lepikhin 2020）：早期论文同时用过 $k=2$ 和 $k=2$ 的"第二专家随机选"变体，目的是注入噪声防坍塌。

经验：$k=1$ 对 token-level 特化更强但更难训；$k=2$ 是效果/稳定性折中。LLaMA-4（传闻）、DeepSeek-V2/V3 都采用更激进的 $N$ 很大（100+ 专家）配 $k=8$-$16$ 的细粒度 MoE——更多专家 + 高 $k$ 让每个专家更专、组合更灵活。

## 4. 常见追问预判

### 4.1 $k=1$ vs $k=2$：稳定性-特化 trade-off

$k=1$ 强迫每 token 只能"承诺"一个专家，更逼近"专家"在字面意义上的分工（每个专家负责特定 token 分布的一片）；但硬 argmax 让训练对初始化和路由抖动敏感，需要更大的 $\alpha$ 和更仔细的 warmup。$k=2$ 本质是对专家输出做混合（两个专家的加权和），容量需求翻倍但梯度路径更丰富、专家坍塌更难发生。在等参数 + 等 FLOPs 的对比下，$k=2$ 通常收敛更快、最终 loss 低 0.02-0.05 nats。选 $k=1$ 的理由主要是推理计算预算紧（Switch 的核心卖点）。

### 4.2 序列级 vs batch 级 vs 全局负载均衡

$f_i$ 和 $P_i$ 是在什么粒度上平均？三种选择：

- **Token 级 / batch 级**（最常见）：把当前 batch 的所有 token 统一统计 $f_i, P_i$。一个 batch 内可能有 prompt + completion 共数千 token，粒度够细，辅助损失最贴近实际并行需求。
- **序列级**：在每条序列内平均。会强迫每条序列都用满所有专家，和"不同序列有不同领域"的假设冲突；实践几乎不用。
- **全局/长时平均**：用 moving average 维护 $f_i$。更稳但滞后；Switch 原实验发现 batch 级就够。

还有专门的 **device-level balancing**：$N$ 个专家分布在多 GPU 上，除了要 token 均匀还要每 GPU 的工作量均匀。DeepSeek-V3 提出 device-level aux loss 在 $\mathcal{L}_{\text{aux}}$ 基础上再叠一层按设备分组的惩罚。

### 4.3 推理成本：参数量 vs 激活量

MoE 最诱人的数学：总参数 $N$-倍但每 token FLOPs 只有 $k$-倍。然而推理时**所有专家的参数仍需加载到显存**——$N=8$ 专家的 Mixtral 8×7B 实际显存占用接近 47B 稠密模型（不是 7B）。内存墙让 MoE 在端侧 / 小显存设备上的优势被削弱，主要受益场景是服务端 batch 推理（专家的加载成本被 batch 分摊，每 token 成本回到 $k$-倍）。这是为什么 MoE 在云端训练/推理大放异彩，但端侧还是稠密模型为主。

### 4.4 MoE 微调的不稳定性

MoE 预训练完成后做 **Supervised Fine-Tuning** (SFT, 监督微调) 时路由器极易退化——fine-tune 数据分布窄，路由器过拟合到 SFT 分布的"少数几个专家"，$\mathcal{L}_{\text{aux}}$ 又被 fine-tune 损失盖掉。缓解手段：(i) fine-tune 时**冻结路由器**，让 token 分派保持 pretrain 的模式；(ii) 保留 $\mathcal{L}_{\text{aux}}$ 并适度放大 $\alpha$；(iii) 用 MoE-aware SFT（对专家并行 forward + 对 loss 做加权）。ST-MoE 论文有专章讨论这个问题。

### 4.5 为什么 soft-routing（稠密混合）没流行

"所有专家都按 $p_i$ 加权" = 稠密的专家混合，路由是可导的 softmax 而非 argmax，根本不需要 $\mathcal{L}_{\text{aux}}$。问题是它**没解决算力问题**——每 token 要算所有 $N$ 个专家，完全退化成 "$N$ 倍宽的 FFN"，参数膨胀但算力不降，MoE 的稀疏收益全部丢失。Shazeer 2017 在稀疏化上的核心贡献正是发现"足够大的 $N$ + 硬 TopK"才能让条件计算有意义。

### 4.6 Auxiliary-loss-free 路由（DeepSeek-V3 路径）

DeepSeek-V3（2024）提出**bias-only load balancing**：给每个专家一个可训练的偏置 $b_i$，加到路由 logits 上：$\tilde{g}_i = g_i + b_i$，再做 TopK。当某专家被过度使用时，监控器会自动**下调** $b_i$，把路由压力推向其他专家。没有辅助损失、没有对路由 logits 的额外惩罚，完全靠 bias 的闭环反馈实现均衡，训练梯度更干净（$\mathcal{L}_{\text{aux}}$ 会和主任务梯度竞争）。这是目前大规模 MoE（几百专家）的新趋势，缺点是需要小心调 bias 更新的动态稳定性。

## 5. 参考

- Shazeer et al. 2017, *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer* —— 现代 MoE 的原始论文，引入稀疏 TopK 路由、importance loss、load loss 的前身。
- Lepikhin et al. 2020, *GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding* —— $k=2$ 路由 + 容量因子 + 跨设备并行，MoE 走向 scale 的工程正典。
- Fedus et al. 2021, *Switch Transformer: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity* —— $k=1$、$\mathcal{L}_{\text{aux}} = \alpha N \sum f_i P_i$、capacity factor $C$ 的规范形式，上面 §2.2 的推导严格按照这篇。
- Zoph et al. 2022, *ST-MoE: Designing Stable and Transferable Sparse Expert Models* —— router z-loss、MoE 微调稳定性的工程 playbook。
- Jiang et al. 2024, *Mixtral of Experts* —— Mixtral 8×7B 的工程细节（$k=2$、8 专家、SwiGLU FFN），当代最普及的开源 MoE 基线。
"""


def sha256_of_description(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pair of the target leaf."""
    h = hashlib.sha256()
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE path = ?", (TARGET_PATH,)
    ).fetchone()
    h.update(TARGET_PATH.encode("utf-8"))
    h.update(b"\x00")
    h.update((row[0] or "").encode("utf-8"))
    h.update(b"\x00")
    return h.hexdigest()


def validate_content(path: str, content: str) -> None:
    """AC: description must contain KaTeX math + at least one section header."""
    if "$" not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no $...$ math delimiter found")
    if "## " not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no '## ' section header found")


def main() -> int:
    """Update the single Q#22 leaf with the Y-depth golden answer (idempotent)."""
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    validate_content(TARGET_PATH, DESC_MOE_ROUTING)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_description(conn)
        print(f"[PRE]  sha256={pre_hash}")

        row = conn.execute(
            "SELECT id, description FROM framework_nodes WHERE path = ?",
            (TARGET_PATH,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] missing node at path={TARGET_PATH}")
            return 1
        node_id, current = row

        if current == DESC_MOE_ROUTING:
            print(f"[SKIP]   id={node_id} path={TARGET_PATH} (already up-to-date)")
            counts = {"UPDATED": 0, "SKIPPED": 1}
        elif current != PLACEHOLDER:
            preview = (current or "")[:80].replace("\n", " ")
            raise RuntimeError(
                f"[CONFLICT] path={TARGET_PATH}: existing description neither "
                f"placeholder nor expected new content. current[:80]={preview!r}"
            )
        else:
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (DESC_MOE_ROUTING, node_id),
            )
            conn.commit()
            counts = {"UPDATED": 1, "SKIPPED": 0}
            print(
                f"[UPDATE] id={node_id} path={TARGET_PATH} "
                f"len={len(DESC_MOE_ROUTING)} (was {len(current)})"
            )

        post_hash = sha256_of_description(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    total = counts["UPDATED"] + counts["SKIPPED"]
    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={total} (expected 1)"
    )
    if total != 1:
        print("[FAIL] expected to touch exactly 1 leaf")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
