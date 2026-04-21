"""Insert a condensed 'dimension-flow + common misconceptions' block
into node 225 (ml-fundamentals/attention_transformer/mha-mqa-gqa).

Per user Discord 2026-04-20 (with supplied raw notes). User asked for
critical distillation emphasizing common misconceptions, kept tight.

Adds one block between section 1 closing question and section 2
derivation. Covers:
  - dimension flow X (n, d) -> heads (n, d/h) -> concat (n, d) -> W^O,
    and why this is the precondition for residual + infinite stacking
  - three invariants (input fully shared, each head outputs d/h,
    d mod h == 0)
  - three common interview misconceptions:
    * input is NOT split across heads, projected features are
    * per-head output is d/h but layer output is still d
    * under MQA, multi-head still matters because Q_i differ

Idempotent via sentinel marker.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 225

ANCHOR = "问题：为什么 bottleneck 是 KV 而不是 Q？三种方案怎么取舍？\n\n## 2. 推导：KV head 共享怎么省显存"
MARKER = "<!-- FOLLOWUP_20260420_MHA_DIM_FLOW -->"
INSERT = r"""问题：为什么 bottleneck 是 KV 而不是 Q？三种方案怎么取舍？

<!-- FOLLOWUP_20260420_MHA_DIM_FLOW -->

**先把 MHA 本身想清楚（3 条 invariant + 3 个高频误区）**

**维度流**：$X \in \mathbb{R}^{n \times d}$ $\xrightarrow{W_i^{Q,K,V}}$ 每个 head $\mathbb{R}^{n \times d_{\text{head}}}$（$d_{\text{head}} = d / h$）$\xrightarrow{\text{concat } h \text{ 个}}$ $\mathbb{R}^{n \times d}$ $\xrightarrow{W^O}$ $\mathbb{R}^{n \times d}$。**整层输入 = 输出 = $d$**——这正是 residual connection `x = x + \text{Attn}(x)` 成立、Attention 层能**无限堆叠**的前提。

- **输入完整共享**：所有 head 看到的是**同一个 $X$**；切分只发生在**投影后的特征维度**上（不是切 batch、不是切 token）。
- **每个 head 输出 $d / h$ 维**，$h$ 个 concat 之后自动对齐回 $d$；设计约束 $d \bmod h = 0$。
- **MQA / GQA 不破坏这个结构**：只是把 $h$ 套 $W^K, W^V$ 压成 $1$ 套（MQA）或 $g$ 套（GQA），$W_i^Q$ 仍然每个 head 一套，其余维度守恒不变。

**面试高频 3 个误区**：

- ❌ "输入被切成 $h$ 份送进 $h$ 个 head" → ✅ 每个 head 拿**完整的 $X$**，切的是投影出的**特征子空间**。
- ❌ "整层 Attention 输出维度是 $d / h$" → ✅ **单个 head 是 $d / h$，整层 concat + $W^O$ 后仍是 $d$**。
- ❌ "MQA 里 multi-head 就没意义了（$K, V$ 都一样）" → ✅ 每个 head 仍有**独立的 $W_i^Q$**，不同 $Q_i$ 对同一份 $K, V$ 算出不同的 attention 权重、读出不同的值。类比：**同一个图书馆（$K, V$），不同读者（$Q_i$）带不同问题查出不同书单。**

## 2. 推导：KV head 共享怎么省显存"""


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
        print("[FAIL] anchor not found in node 225 description", file=sys.stderr)
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
