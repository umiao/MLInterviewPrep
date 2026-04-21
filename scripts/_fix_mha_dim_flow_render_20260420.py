"""Fix two issues in the FOLLOWUP_20260420_MHA_DIM_FLOW block on node 225:

1. Residual connection formula was wrapped in backticks (code span) so
   LaTeX \text{Attn}(x) rendered literally instead of as math. Swap to
   inline math delimiters.
2. Unicode check/cross emojis in the misconception bullets violate the
   project no-emoji rule. Replace with ASCII tags **[误]** / **[对]**.

Idempotent: each replacement's source (buggy) string is unique; after
fix the source no longer appears. Safe to re-run.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
NODE_ID = 225

REPLACEMENTS: list[tuple[str, str]] = [
    # 1. residual formula: code span -> inline math
    (
        "residual connection `x = x + \\text{Attn}(x)` 成立",
        "residual connection $x = x + \\text{Attn}(x)$ 成立",
    ),
    # 2a. misconception 1
    (
        "- \u274c \"\u8f93\u5165\u88ab\u5207\u6210 $h$ \u4efd\u9001\u8fdb $h$ \u4e2a head\" \u2192 \u2705 \u6bcf\u4e2a head \u62ff**\u5b8c\u6574\u7684 $X$**\uff0c\u5207\u7684\u662f\u6295\u5f71\u51fa\u7684**\u7279\u5f81\u5b50\u7a7a\u95f4**\u3002",
        "- **[误]** \"输入被切成 $h$ 份送进 $h$ 个 head\" → **[对]** 每个 head 拿**完整的 $X$**，切的是投影出的**特征子空间**。",
    ),
    # 2b. misconception 2
    (
        "- \u274c \"\u6574\u5c42 Attention \u8f93\u51fa\u7ef4\u5ea6\u662f $d / h$\" \u2192 \u2705 **\u5355\u4e2a head \u662f $d / h$\uff0c\u6574\u5c42 concat + $W^O$ \u540e\u4ecd\u662f $d$**\u3002",
        "- **[误]** \"整层 Attention 输出维度是 $d / h$\" → **[对]** **单个 head 是 $d / h$，整层 concat + $W^O$ 后仍是 $d$**。",
    ),
    # 2c. misconception 3
    (
        "- \u274c \"MQA \u91cc multi-head \u5c31\u6ca1\u610f\u4e49\u4e86\uff08$K, V$ \u90fd\u4e00\u6837\uff09\" \u2192 \u2705 \u6bcf\u4e2a head \u4ecd\u6709**\u72ec\u7acb\u7684 $W_i^Q$**\uff0c\u4e0d\u540c $Q_i$ \u5bf9\u540c\u4e00\u4efd $K, V$ \u7b97\u51fa\u4e0d\u540c\u7684 attention \u6743\u91cd\u3001\u8bfb\u51fa\u4e0d\u540c\u7684\u503c\u3002\u7c7b\u6bd4\uff1a**\u540c\u4e00\u4e2a\u56fe\u4e66\u9986\uff08$K, V$\uff09\uff0c\u4e0d\u540c\u8bfb\u8005\uff08$Q_i$\uff09\u5e26\u4e0d\u540c\u95ee\u9898\u67e5\u51fa\u4e0d\u540c\u4e66\u5355\u3002**",
        "- **[误]** \"MQA 里 multi-head 就没意义了（$K, V$ 都一样）\" → **[对]** 每个 head 仍有**独立的 $W_i^Q$**，不同 $Q_i$ 对同一份 $K, V$ 算出不同的 attention 权重、读出不同的值。类比：**同一个图书馆（$K, V$），不同读者（$Q_i$）带不同问题查出不同书单。**",
    ),
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

    for i, (old, new) in enumerate(REPLACEMENTS):
        if old in desc:
            count = desc.count(old)
            if count != 1:
                print(f"[FAIL] replacement {i} not unique: {count} occurrences", file=sys.stderr)
                conn.close()
                return 3
            desc = desc.replace(old, new, 1)
            applied.append(f"#{i}")
        elif new in desc:
            skipped.append(f"#{i}")
        else:
            print(f"[FAIL] replacement {i}: neither old nor new string found", file=sys.stderr)
            conn.close()
            return 2

    if not applied:
        print(f"[SKIP] all {len(REPLACEMENTS)} fixes already applied ({before_len} chars)")
        conn.close()
        return 0

    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE id = ?", (desc, NODE_ID)
    )
    conn.commit()
    conn.close()
    print(f"[OK] node {NODE_ID} description {before_len} -> {len(desc)} chars ({len(desc) - before_len:+d})")
    print(f"[OK] applied: {', '.join(applied)}")
    if skipped:
        print(f"[SKIP] already applied: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
