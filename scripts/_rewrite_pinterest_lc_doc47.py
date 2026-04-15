"""Rewrite Pinterest LC Must-Do doc (company_documents id=47).

Changes requested by user:
- Drop static review templates (Pattern Clusters, Core Patterns Cheat Sheet,
  Common Traps, Daily Review Template) — redundant once every problem has
  full Chinese notes.
- Merge all problem tables (Core 14, 2025-11 Expansion, Custom) into a single
  top-to-bottom reading flow so the doc is coherent as a review index.
- Replace redundant Status/Notes columns (all say "Done / Written") with a
  Chinese 考察要点 column (English technical terms allowed).
- Keep navigation-useful sections: SD modules, BQ cross-ref, LC<->SD map.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DOC_ID = 47

NEW_CONTENT = r"""# Pinterest LC Must-Do -- Review & Index

> 14 道 must-do + 2025-11 扩展 + 若干 Pinterest custom 题。全部已完成 + 中文 notes（含 code review）。
> 点题目标题在侧边抽屉里打开完整解法。所有"考察要点"用中文写成，保留英文术语。

---

## 核心 14 道 (2026-04-12 清单)

| # | LC | Title | Diff | Pattern | 考察要点 |
|---|-----|-------|------|---------|---------|
| 1 | 332 | [Reconstruct Itinerary](lc://332) | Hard | Hierholzer | 后序 append + reverse；死胡同排到尾部再翻转；min-heap 保字典序 |
| 2 | 465 | [Optimal Account Balancing](lc://465) | Hard | Bitmask DP | 最大零和子集数 → 答案 = n - 子集数；submask 用 `sub=(sub-1)&mask` 保 O(3^n) |
| 3 | 815 | [Bus Routes](lc://815) | Hard | BFS on route graph | 节点是 **bus 路线不是站点**；visited 标记路线；LC 1135 反向 follow-up |
| 4 | 322 | [Coin Change](lc://322) | Med | Unbounded Knapsack | `dp[i]=min(dp[i-c]+1)`；初值 inf；顺序遍历 coin 允许重复取 |
| 5 | 282 | [Expression Add Operators](lc://282) | Hard | Backtrack + `prev` | `*` 的处理：`cur - prev + prev*x`；前导零用 `break` 剪枝 |
| 6 | 1055 | [Shortest Way to Form String](lc://1055) | Med | Greedy / 二分加速 | 每段在 source 贪心匹配；用 `next[pos][ch]` 预处理可 O((s+t)·26) |
| 7 | 311 | [Sparse Matrix Multiplication](lc://311) | Med | Sparse Hashmap | 只存非零行/列；`A·B` 按 A 的 nnz 行 · B 的 nnz 列；2-D 版 LC 1570 |
| 8 | 2402 | [Meeting Rooms III](lc://2402) | Hard | 双堆模拟 | `free`=空闲房 min-heap、`busy`=(end, id) min-heap；tuple tiebreak 自动排序 |
| 9 | 1110 | [Delete Nodes And Return Forest](lc://1110) | Med | DFS 状态上下传 | `is_root` **往下传**（父是否被删）；`None` **往上返**（让父自动 unlink） |
| 10 | 1244 | [Design A Leaderboard](lc://1244) | Med | Hash + size-K heap | 手写 size-K min-heap + `heapreplace`；lazy heap 仅在读稀疏、玩家百万级才值 |
| 11 | 410 | [Split Array Largest Sum](lc://410) | Hard | 二分答案 / DP | `beg=max(nums), end=sum(nums)`；可行性判断用贪心切段；或 O(n²k) DP |
| 12 | 43 | [Multiply Strings](lc://43) | Med | 数字模拟 | `ansArr[i+j+1] += d_i*d_j`，`ansArr[i+j] += carry`；长度 m+n 或 m+n-1 |
| 13 | 642 | [Design Search Autocomplete System](lc://642) | Hard | Trie + Top-K | 每个 Trie 节点挂 sentence→count 字典；top(3) 用 size-3 min-heap + tuple 排序 |
| 14 | 1723 | [Find Minimum Time to Finish All Jobs](lc://1723) | Hard | 二分答案 + 回溯剪枝 | 二分 max-load；可行性用回溯；sort desc + skip duplicate worker 是大剪枝 |

---

## 扩展 & Follow-up 题

2025-11 Discord onsite 转述 + 核心 14 的 follow-up 姊妹题。全部打 Pinterest tag。

| # | LC | Title | Diff | Pattern | 考察要点 | 来源 |
|---|-----|-------|------|---------|---------|------|
| 1 | 84 | [Largest Rectangle in Histogram](lc://84) | Hard | Monotonic Stack | 递增栈 + 前后 0 哨兵；pop 时 `width = i - stack[-1] - 1`；所有 histogram/skyline 题的基础 | 2025-11 dump |
| 2 | 85 | [Maximal Rectangle](lc://85) | Hard | 2-D → Histogram | 每行 `heights[j] += 1 if '1' else 0`，跑 n 次 LC 84；O(m·n) | 2025-11 dump |
| 3 | 392 | [Is Subsequence](lc://392) | Easy | 双指针 | 同向扫；follow-up 大量 t 查询 → `next_pos[i][ch]` DP 每次 O(\|t\|·26) | 2025-11 dump |
| 4 | 1135 | [Connecting Cities With Min Cost](lc://1135) | Med | MST (Kruskal + UF + heap) | 边按权进堆；UF 判环；合并 n-1 次提前返回；不连通 -1。**LC 815 的"带权"姊妹题** | LC 815 follow-up |
| 5 | 1526 | [Minimum Number of Increments on Subarrays](lc://1526) | Hard | Diff greedy | 答案 = 正向 first-difference 之和；`ans += max(0, a[i]-a[i-1])` | 2025-11 dump |
| 6 | 1564 | [Put Boxes Into Warehouse I](lc://1564) | Med | Greedy + prefix-min | warehouse 做 prefix-min 保证 height 单调；box 按高度 desc 贪心放 | 2025-11 dump |
| 7 | 1570 | [Dot Product of Two Sparse Vectors](lc://1570) | Med | Sparse Hashmap | 只存 nonzero；点积时**遍历 nnz 少的那边**查另一边。**LC 311 的 1-D 版** | LC 311 follow-up |
| 8 | 1580 | [Put Boxes Into Warehouse II](lc://1580) | Hard | 两端双指针 | warehouse 无单调性 → 从两端向中间指针；每个 box 选能进的一端 | 2025-11 dump |
| 9 | 1851 | [Minimum Interval to Include Each Query](lc://1851) | Hard | Offline sort + heap | 按 query 升序；把左端≤q 的区间入 heap，pop 掉右端<q 的；最小 length 即答 | 2025-11 dump |
| 10 | 3229 | [Min Ops to Make Array = Target](lc://3229) | Hard | Signed diff greedy | 1526 推广：diff 换号要重置累计；正负两段分开算 | 2025-11 dump |

---

## Pinterest Custom 题 (无 LC 对应)

Onsite 报告中无直接 LC 映射的题目；完整中文解法在 `problems.notes`，按 title 搜索。

| # | Title | Core Pattern | 考察要点 |
|---|-------|-------------|---------|
| 1 | [Escape Room Game State](db://1068) | BFS / 状态机 | 状态 = `(people_positions, room_open_bitmask)`；多 actor 联合状态空间 BFS |
| 2 | [Lighthouse 2D Light Propagation](db://1071) | Grid 模拟 + 递归 | 光束 DFS；splitter 分叉；`(row,col,dir)` 去重防循环 |
| 3 | [Prefix-Match First-Word-Index](db://1072) | Binary Search / Trie | `bisect_left` 在已排序 dict 上 O(log n)；Trie 版每节点存最早 index |
| 4 | [Grant Access on DAG](db://1075) | BFS/DFS on DAG | Topological 传播；visited 防重；起点集合初始化很关键 |
| 5 | [Pin Connectivity Streaming Edges](db://1076) | Union-Find | 路径压缩 + 按秩合并；流式加边查连通 |
| 6 | [round() from scratch (string in)](db://1073) | 数字字符串运算 | 显式 banker's rounding vs half-up；不能用 `float()` 绕过 |
| 7 | [round by precision p](db://1074) | 同 #6 推广 | 对齐到第 p 位后做 rounding；正负号与小数点处理 |
| 8 | [LC 332 Loop Follow-up Addendum](lc://332) | 图 + 环检测 | 变体：判断行程是否必须重访某条边 |

---

## System Design 模块

每个 Pinterest 风格 SD 写作在 `docs/pinterest/`；含问题 framing / metrics / data / model / training / serving / online eval / failure modes。

| # | Topic | Link | 关联 LC |
|---|-------|------|---------|
| 1 | Ad CTR Prediction | [system_design_ad_ctr](/system-design/pinterest-ad-ctr) | [LC 322](lc://322) (budget pacing DP 类比) |
| 2 | User & Item Embeddings | [system_design_embeddings](/system-design/pinterest-embeddings) | [LC 311](lc://311), [LC 1570](lc://1570) |
| 3 | Personalized Chatbot Pins | [system_design_chatbot_pins](/system-design/pinterest-chatbot-pins) | [LC 282](lc://282) (prompt-parse backtrack 类比) |
| 4 | Pin Ranking | [system_design_pin_ranking](/system-design/pinterest-pin-ranking) | [LC 1244](lc://1244), [LC 2402](lc://2402) |
| 5 | Pins Search | [system_design_pins_search](/system-design/pinterest-pins-search) | [LC 642](lc://642), [LC 392](lc://392), [LC 1055](lc://1055) |
| 6 | Notification Recommendation | [system_design_notification_reco](/system-design/pinterest-notification-reco) | -- |
| 7 | Catalog Bulk Update | [system_design_catalog_bulk_update](/system-design/pinterest-catalog-bulk-update) | [LC 1526](lc://1526), [LC 3229](lc://3229) |

---

## BQ

- **Pinterest BQ Question Map (2025-11)**: [bq_question_map](/companies/29/prep?doc=48) -- 5 条 onsite BQ prompt 对应 2-3 条最匹配的 EX-XX 故事。

---

## 面试准备前的最后 sanity check

- **recruiter 对话材料**：[Pinterest Senior MLE Recruiter Call Prep](/companies/29/prep?doc=39)
- **进度**：核心 14 + 扩展 & follow-up 10 + custom 8 = **32 题全部 done + 中文 notes**
- **来源**：user-provided 2026-04-12 via Discord + 2025-11 Discord dump + follow-up 2026-04-15

*Last refactored: 2026-04-15.*
"""


def main() -> None:
    """UPDATE doc 47 content. Idempotent: checks marker before writing."""
    marker = "*Last refactored: 2026-04-15.*"
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, content FROM company_documents WHERE id = ?", (DOC_ID,)
        ).fetchone()
        if row is None:
            raise SystemExit(f"doc id={DOC_ID} not found")
        if marker in row[1]:
            print(f"[NOOP] doc {DOC_ID} already refactored (marker present)")
            return
        conn.execute(
            "UPDATE company_documents SET content = ? WHERE id = ?",
            (NEW_CONTENT, DOC_ID),
        )
        conn.commit()
        print(
            f"[UPDATED] doc {DOC_ID} ({len(row[1])} -> {len(NEW_CONTENT)} chars)"
        )


if __name__ == "__main__":
    main()
