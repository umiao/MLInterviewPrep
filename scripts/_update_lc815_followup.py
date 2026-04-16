"""Idempotent: append a station-level shortest-path follow-up to LC 815 notes.

LC 815 (Bus Routes) original cost is min transfers, solved with route-BFS.
User asked to add a follow-up for "min stops traversed" (station-level shortest
path), with a sentinel so re-runs don't duplicate content.

Run: python scripts/_update_lc815_followup.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 815
SENTINEL = "<!-- LC815_STATION_SHORTEST_FOLLOWUP -->"

FOLLOWUP = f"""

{SENTINEL}
### Follow-up: 求站点到站点的最短站数距离

原题 LC 815 的代价是"最少换乘次数"，按**路线**做 BFS 即可。若改为"**最少经过站数**"，
就需要把节点从"路线"切换到"**站点**"，做站点级最短路。

**建图方式**：
- 对每条路线，**相邻站点**之间连一条权重 1 的边（环形线路首尾也连）。
- **换乘无需额外处理**——同一物理站点在图中就是同一个节点，自然做了合并。

**查询方式**：
- 边权均为 1 → 直接 BFS，$O(V+E)$。
- 若边权不等（真实距离、换乘 penalty 等）→ 改用 Dijkstra。

**复杂度**：
- 建图：$O(\\sum_i L_i)$，$L_i$ 是第 $i$ 条线路的站数。
- 单次查询：$O(V + E)$，与原题按路线 BFS 同级别。

**不建议预处理线路内点对距离**：
- 单条线路两两配对是 $O(L_i^2)$，总计 $O(\\sum_i L_i^2)$，当某条线路较长时会爆炸，
  且绝大多数点对在真实查询中用不到，不如在线 BFS 按需展开。

**本题 vs follow-up 对照**：

| 维度 | LC 815 原题 | 本 follow-up |
| --- | --- | --- |
| 代价定义 | 最少换乘次数 | 最少经过站数 |
| 节点 | 路线 | 站点 |
| 边 | 两路线共享一个站点则连边 | 同线路相邻站点连边 |
| 算法 | 路线级 BFS | 站点级 BFS / Dijkstra |
| 关键映射 | `stop -> [route_ids]` | 无需换乘映射，站点重合即合并 |

**面试答法**：先指出"换乘数 vs 站数"是两个不同的 cost model，对应不同的建图层级；
然后从原题的路线级 BFS **平滑迁移**到站点级最短路，并说明为什么不建议预处理点对距离。
"""


def main() -> None:
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes = row
        existing_notes = existing_notes or ""

        if SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} -- follow-up already present")
            return

        new_notes = existing_notes.rstrip() + FOLLOWUP
        conn.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (new_notes, pid),
        )
        conn.commit()
        delta = len(new_notes) - len(existing_notes)
        print(f"[UPDATED] LC {LC_ID} id={pid} notes +{delta} chars (now {len(new_notes)})")


if __name__ == "__main__":
    main()
