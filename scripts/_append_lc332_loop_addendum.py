"""Append Pinterest 2025-11 loop follow-up addendum to LC 332 notes (id=148).

Idempotent: skips if the addendum marker is already present.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
MARKER = "### Pinterest 2025-11 Follow-up"

ADDENDUM = r"""

---

### Pinterest 2025-11 Follow-up: "If the tickets form a cycle?"

**面试官追问**: 如果机票形成一个环（loop），算法还对吗？

**核心答案**: Hierholzer 天然支持 Eulerian **circuit**（闭合环路）—— 无需任何修改。起点 JFK 和终点会是同一个节点，算法的 post-order 反转逻辑把 JFK 既作为第一个也作为最后一个 append，得到形如 `[JFK, ..., JFK]` 的合法行程。

**为什么无需改动？**
- Hierholzer 的不变量是「每次卡在一个 dead-end 就 post-order append，然后回溯继续榨干别的分支」。
- Eulerian path 和 Eulerian circuit 的唯一区别是起点是否等于终点；而 dead-end 的触发条件（`while graph[node]` 变空）对两种情况都成立。
- 对 Eulerian circuit，DFS 最终回到 JFK 时，JFK 的出边已全部用完 -> JFK 变成第一个 post-order append 的节点 -> 反转后它既在头也在尾。

**Eulerian 存在性条件（如果追问「如何判断不可行」）**:

| 场景 | 条件 |
|------|------|
| Eulerian **path**（起点 != 终点） | 恰好 2 个节点的 `\|in - out\|` 为奇（起点 out-in=1，终点 in-out=1），其它所有节点 in=out；且所有有边的节点在底层无向图上连通。 |
| Eulerian **circuit**（起点 = 终点） | 每个节点 in-degree = out-degree；所有有边的节点连通。 |

LC 332 的题面保证一定存在合法行程，所以不需要显式判存在性。但面试官若追问「给定任意 tickets，如何 O(V+E) 判定可行」：
1. 统计每个节点的 in/out degree。
2. 检查上表条件。
3. 在无向化的图上跑一次 BFS/DFS 验证连通性（只考虑有边的节点）。

**环路的一个坑**: 如果图里存在一个跟 JFK 不相连的独立 cycle（例如 `A->B->A`，而 JFK 根本到不了 A），则整个 multigraph 不连通，Eulerian 不存在 —— 仅凭 degree 条件不够，必须加连通性检查。

**口述要点**:
1. "Hierholzer 本身就处理 circuit，因为 dead-end 回溯的机制对 path/circuit 完全一致。"
2. "如果题目改成检测不可行，我会查 degree + 连通性两个条件。"
3. "degree 合法但不连通的反例 = 两个独立的 cycle。"
"""


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.text_factory = str
    cur = conn.cursor()
    row = cur.execute("SELECT notes FROM problems WHERE id=148").fetchone()
    if row is None:
        print("[FAIL] problem id=148 not found")
        return
    notes = row[0] or ""
    if MARKER in notes:
        print("[SKIP] addendum already present")
        return
    new_notes = notes.rstrip() + ADDENDUM
    cur.execute("UPDATE problems SET notes=? WHERE id=148", (new_notes,))
    conn.commit()
    print(f"[UPDATE] id=148 notes {len(notes)} -> {len(new_notes)} chars")


if __name__ == "__main__":
    main()
