"""Seed Google R2 Coding Index doc + append crosslink in Google Prep Hub.

T-P0-692 [MLI-E2]. Creates a new company_documents row under company_id=3
(Google) titled '[Google] R2 Coding Index' that lists R2-coding-only entries
(R1 fundamentals / R3 system design / behavioral are excluded). Each entry is
a ProblemDrawer link via the `db://<id>` URI scheme so the drawer reuses the
problems-table content (matching memory feedback_dblc_drawer_links: ALL index
entries use db:// for problems, never cd:// which routes to company_documents).

Seeded with the FIRST entry: matrix rotation -> db://73 (LeetCode 48 'Rotate
Image' with the rectangular n*m generalization landed in T-P0-691 / T-P0-286).

Two artefacts, both idempotent:

  1. INSERT-or-UPDATE a company_documents row (sentinel
     `<!-- GOOGLE_R2_INDEX_20260502 -->`); doc_kind='prep_note' to match the
     existing Google convention (kinds present today: drill x11, prep_note x5,
     hub_doc x1; 'prep_note' is the closest fit for an index-style page and
     mirrors the precedent set by `scripts/seed_uber_lc_index.py`).

  2. UPSERT-append a sentinel-guarded crosslink block in the Google Prep Hub
     (company_documents.id=53) pointing at the new index via cd://<index_id>.
     Uses begin/end sentinel pair so re-runs replace the block in place rather
     than appending duplicates -- the block contains the index id which is
     unknown until step 1 commits, so byte-identical guard from
     scripts/seed_google_hub_mlf_crosslink.py does not apply.

Idempotency contract:
  - First run on clean DB: 1 INSERT (index) + 1 UPDATE (hub) = 2 writes
  - Second run (no content drift): 0 writes (both UNCHANGED)

Run: python scripts/seed_google_r2_coding_index_20260502.py
"""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

GOOGLE_COMPANY_ID = 3
HUB_DOC_ID = 53

INDEX_TITLE = "[Google] R2 Coding Index"
INDEX_DOC_KIND = "prep_note"
INDEX_SENTINEL = "<!-- GOOGLE_R2_INDEX_20260502 -->"

HUB_BLOCK_BEGIN = "<!-- GOOGLE_R2_INDEX_HUB_LINK_20260502 -->"
HUB_BLOCK_END = "<!-- /GOOGLE_R2_INDEX_HUB_LINK_20260502 -->"


def _sha256(s: str) -> str:
    """Return hex sha256 of the UTF-8 encoding of s."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _fetch_problem_meta(
    conn: sqlite3.Connection, problem_id: int
) -> tuple[int, int | None, str, str | None, str | None, str | None]:
    """Return (id, leetcode_id, title, difficulty, family, pattern) for problems.id=problem_id."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, difficulty, family, pattern "
        "FROM problems WHERE id = ?",
        (problem_id,),
    ).fetchone()
    if row is None:
        raise SystemExit(
            f"[FAIL] problems.id={problem_id} missing -- T-P0-691 must run first"
        )
    return row


def _fetch_problem_meta_by_title(
    conn: sqlite3.Connection, title: str
) -> tuple[int, int | None, str, str | None, str | None, str | None]:
    """Return (id, leetcode_id, title, difficulty, family, pattern) for the row matching title.

    Used for entries seeded by sibling scripts (e.g.,
    `seed_google_r2_three_problems_20260503.py`) where the row id is not known
    at index-generation time. Title is the canonical key for custom-interview
    problems per CLAUDE.md `Idempotent seed pattern per row type`.
    """
    row = conn.execute(
        "SELECT id, leetcode_id, title, difficulty, family, pattern "
        "FROM problems WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        raise SystemExit(
            f"[FAIL] problems.title={title!r} missing -- "
            "seed_google_r2_three_problems_20260503.py must run first"
        )
    return row


def _fetch_problem_meta_by_leetcode_id(
    conn: sqlite3.Connection, leetcode_id: int
) -> tuple[int, int | None, str, str | None, str | None, str | None]:
    """Return (id, leetcode_id, title, difficulty, family, pattern) for the row matching leetcode_id.

    Canonical key for LC-numbered problems per CLAUDE.md
    `Idempotent seed pattern per row type`.
    """
    row = conn.execute(
        "SELECT id, leetcode_id, title, difficulty, family, pattern "
        "FROM problems WHERE leetcode_id = ?",
        (leetcode_id,),
    ).fetchone()
    if row is None:
        raise SystemExit(
            f"[FAIL] problems.leetcode_id={leetcode_id} missing -- "
            "the corresponding seed_*.py must run first"
        )
    return row


def _fmt_index_row(
    meta: tuple[int, int | None, str, str | None, str | None, str | None],
    summary: str,
) -> str:
    """Format one '- [LC N. title](db://id) `[diff]` -- summary. *family|pattern*' line."""
    pid, lc, title, diff, family, pattern = meta
    diff_label = (diff or "?").lower()
    lc_label = f"LC {lc}. " if lc is not None else ""
    meta_bits: list[str] = []
    if family:
        meta_bits.append(f"family: `{family}`")
    if pattern:
        meta_bits.append(f"pattern: `{pattern}`")
    meta_suffix = f"  *{' | '.join(meta_bits)}*" if meta_bits else ""
    return (
        f"- [{lc_label}{title}](db://{pid}) "
        f"`[{diff_label}]` -- {summary}{meta_suffix}"
    )


def build_index_content(conn: sqlite3.Connection) -> str:
    """Build the markdown body for the new R2 Coding Index doc."""
    # Matrix / Geometry -- LC 48 from T-P0-691
    lc48 = _fetch_problem_meta(conn, 73)
    lc48_row = _fmt_index_row(
        lc48,
        "90deg/180deg/270deg rotate; 方阵 O(1) in-place `H circ T`; "
        "矩形 n*m 的推广含 D_4 二面体子群分析"
        "({e, H, V, R_180} 保形)、Cate-Twigg 1977 cycle leaders、"
        "`Theta(nm)` 下界完整推导.",
    )

    # Matrix / Flood Fill -- Number of Square Islands (Google R2 custom, 2026-05-07 Discord drop)
    square_islands = _fetch_problem_meta_by_title(conn, "Number of Square Islands")
    square_islands_row = _fmt_index_row(
        square_islands,
        "n*m grid 4-连通极大 1-块, 数恰好填满 k*k 实心正方形的 island 个数. "
        "**首选 BFS + bounding box O(nm)**: 每块记 size + (rmin,rmax,cmin,cmax), "
        "判定 (rmax-rmin == cmax-cmin) AND size == side^2, 极大性靠 BFS 自然保证. "
        "**进阶 2D 前缀和 O(nm * min(n,m))**: 枚举 (r1,c1,k), 内部 sum == k^2 + "
        "**护城河四边 sum == 0** (越界 clip) 显式约束极大, 内层 break 单调剪枝. "
        "L 形里嵌的全 1 子矩形是关键反例 -- 缺护城河会误判.",
    )

    # Prefix Sum / Hash -- 2 custom-interview problems from T-P1-718 (R2 2026-05)
    gold = _fetch_problem_meta_by_title(conn, "Gold Chain 平分")
    gold_row = _fmt_index_row(
        gold,
        "前缀和 + 二分; 移除一节后两段等重; 切点分 i 左 / i 右两 case, "
        "每个 target 在严格递增 P 中至多一位; followup 返所有方案.",
    )

    eq_endpoint = _fetch_problem_meta_by_title(conn, "等值端点最大子数组和")
    eq_row = _fmt_index_row(
        eq_endpoint,
        "按值分组, 每个 v 维护最小 P[i] + arg_min; 先并入再结算覆盖 i==j; "
        "followup 严格 O(1) 退回 O(n^2).",
    )

    # Prefix Sum / Hash -- Necklace 均分 D/R 两人公平切分 (2026-05-07 Discord drop)
    necklace = _fetch_problem_meta_by_title(
        conn, "Necklace 均分 (D/R 两人公平切分)"
    )
    necklace_row = _fmt_index_row(
        necklace,
        "D/R 两色字符串均分给两人 (#D=#R 偶): **<= 2 刀必存在** "
        "(Necklace Splitting Theorem k=2 特例) -> 化归为长度 n/2 的"
        "**固定窗口** 找 f(j)=f(j-m) (其中 f(k)=D(k)-R(k) 前缀差). "
        "存在性证明用**离散 IVT + 奇偶性**: g(k)=f(k)-f(k-m), 边界 g(m)=f(m), g(n)=-f(m), "
        "步长 in {-2,0,+2} 且 g 始终偶 (因 m 偶), 不可能跳过 0. O(n) 时间, O(1) 空间.",
    )

    # String / Two Pointers -- 字符串至多一次交换判等 (Google R1 custom, 2026-05-07 Discord drop)
    one_swap = _fetch_problem_meta_by_title(conn, "字符串至多一次交换判等")
    one_swap_row = _fmt_index_row(
        one_swap,
        "**Google R1 简单题** -- str1 经至多一次字母交换变 str2? "
        "一遍扫收集 `str1[i] != str2[i]` 的下标 diff: `len==0` -> True "
        "(至多一次允许零次); `len==2` 且交叉匹配 "
        "`str1[i]==str2[j] AND str1[j]==str2[i]` -> True; 其他 -> False. "
        "短路版 O(1) 空间 (>=3 diff 立即返回). **辨析 LC 859 'Buddy Strings' "
        "是恰好一次**, str1==str2 还要求 str1 有重复字母, 边界微差面试要先问清楚.",
    )

    # String / Two Pointers -- LC 777 Swap Adjacent in LR String (2026-05-07 Discord drop)
    lc777 = _fetch_problem_meta_by_leetcode_id(conn, 777)
    lc777_row = _fmt_index_row(
        lc777,
        "L/R/X 三字符串经 `LX -> XL` (L 左移) / `XR -> RX` (R 右移) 互转可达性. "
        "**智力题, 两条不变量**: (1) 滤 X 后字符序列必须完全相同 -- L/R 相对顺序"
        "锁死 (swap 都涉及 X, L/R 永远不交叉); (2) L 起始 idx >= 目标 idx, "
        "R 起始 idx <= 目标 idx -- 方向单向. 双方满足 ⇔ 可达; O(n) 双指针一遍扫."
        " 同 LC 2337 `_` 替换 `X` 是同一族.",
    )

    # String / Two Pointers -- LC 2337 from T-P1-718 (R2 2026-05)
    lc2337 = _fetch_problem_meta_by_title(conn, "Move Pieces to Obtain a String")
    lc2337_row = _fmt_index_row(
        lc2337,
        "抽非 _ 字母比对; L 只允许 i_start >= i_target, "
        "R 只允许 i_start <= i_target.",
    )

    # Sliding Window -- LC 3859 (leetcode.cn weekly contest, 双条件容斥)
    lc3859 = _fetch_problem_meta_by_leetcode_id(conn, 3859)
    lc3859_row = _fmt_index_row(
        lc3859,
        "双条件容斥: `atLeast(k, k) - atLeast(k+1, k)`; "
        "滑窗内维护 `freq` 和 `numFreqGeM` 两个量, 缩窗到刚好不满足后 "
        "`ans += left` 利用单调性一次性加 left 个左端点.",
    )

    # Stack / 单调栈 -- Fountain Flood (Google R2 custom, 2026-05-07 Discord drop)
    fountain = _fetch_problem_meta_by_title(conn, "Fountain Flood")
    fountain_row = _fmt_index_row(
        fountain,
        "升序 fountains 列表, 每个喷泉淹**严格小于**自身高度的左右连续段, "
        "遇到 `>=` 阻挡; 输出 64-bit chunk bitmask. **LC 84 单调栈一族**: "
        "递减栈一遍扫求 L[i] / R[i] = 两侧最近 `>= heights[i]` 的下标, "
        "弹栈条件**严格 `<`** -- 等高不弹否则等高喷泉互穿. "
        "每个喷泉 -> `[L+1, R-1]` 闭区间, 升序 fountains -> ranges 升序, "
        "interval merge 一遍降到不重叠. Bitmask 染色按 chunk 切, "
        "in-chunk partial `((1<<len)-1)<<off` / 整 chunk `~0ULL`. "
        "总 O(n+k) + O(n/64) 染色.",
    )

    # Stack / 单调栈 -- LC 496 Next Greater Element I (2026-05-07 Discord drop, 简略)
    lc496 = _fetch_problem_meta_by_leetcode_id(conn, 496)
    lc496_row = _fmt_index_row(
        lc496,
        "**单调递减栈模板题** -- nums1 是 nums2 子集, 求每个 nums1 元素在 nums2 中右侧第一个更大值. "
        "一遍扫 nums2: 栈顶 `<` 当前值时 pop 并赋 next-greater 到 hash 表; nums1 查表 (默认 -1). "
        "O(n+m) 时间. **变体**: LC 503 循环数组 (串两遍 i%n), LC 739 Daily Temperatures (栈存下标).",
    )

    # Stack / 单调栈 -- LC 1673 Find the Most Competitive Subsequence (2026-05-07 Discord drop)
    lc1673 = _fetch_problem_meta_by_leetcode_id(conn, 1673)
    lc1673_row = _fmt_index_row(
        lc1673,
        "**单调栈 + 删除预算** -- 选长度 k 字典序最小子序列 ⇔ 删 (n-k) 个数字. "
        "递增栈一遍扫: 栈非空 + 栈顶 `>` num + 还有预算时 pop, 否则 append; "
        "末尾 `stack[:k]` 处理预算没花完的递增数组. 三件套缺一不可 (尤其预算耗尽要立刻停 pop). "
        "O(n) 时间 / O(k) 空间. **LC 402 同模板** (预算变 k, 字典序递增栈), "
        "**LC 316/1081** 多一层 \"保留约束\", **LC 321** 双数组拓展.",
    )

    # Sweep Line / 离散化 / 线段树 -- 蛋糕水平分割线 (T-P1-XXX 2026-05-05 prep)
    cake = _fetch_problem_meta_by_title(conn, "蛋糕水平分割线")
    cake_row = _fmt_index_row(
        cake,
        "水平线平分蛋糕面积. 三种解法层层递进: 二分 L 暴力 -> 扫描线 + 线性插值 "
        "(独立面积 O(n log n)) -> 扫描线 + 离散化 + 线段树 (几何并集 O(n log n)). "
        "重点讲透 `CoverageSegTree`: cover/length 双字段; 仅根 length[1] 对外语义正确; "
        "成对 +1/-1 不变量 -> 不需要 pushdown.",
    )

    # Bipartite Matching / König -- 2 problems from 2026-05-05 Discord drop
    roof = _fetch_problem_meta_by_title(conn, "屋顶补漏（最小行列覆盖）")
    roof_row = _fmt_index_row(
        roof,
        "m*n 0/1 矩阵, 用整行/整列木板盖所有 1; 行/列 -> bipartite 左/右, "
        "1 -> 边; 最少木板 = 最小点覆盖 = (König) 最大匹配; Hungarian DFS 增广路, "
        "易错点 visited 必须每个 u 重置.",
    )

    rook = _fetch_problem_meta_by_title(conn, "棋盘放最多车（带阻挡型障碍）")
    rook_row = _fmt_index_row(
        rook,
        "n*m 棋盘带阻挡 #, 求最多互不攻击的车; 障碍把行/列切成段, "
        "互斥单位从整行整列下沉到 (水平段, 垂直段); 每个空格 (H, V) 唯一 -> "
        "天然无重边的二分图最大匹配; 屋顶补漏的段细化推广.",
    )

    # Math / Combinatorics / 容斥 -- 循环密码锁 Combination 计数 (2026-05-05 Discord drop)
    combo_lock = _fetch_problem_meta_by_title(conn, "循环密码锁 Combination 计数")
    combo_lock_row = _fmt_index_row(
        combo_lock,
        "3 位循环转盘锁, 两个密码 user/bypass, 每位循环距离 <= 2 算通过; "
        "整体 OR 不可拆成逐位 OR; 容斥 |A union B| = |A| + |B| - |A cap B|, "
        "每位独立用集合交集统一处理 N <= 9 双侧 wrap-around 边界, "
        "省掉闭式 5 - d 的脑力开销; O(1).",
    )

    # Design / Data Structure / 方法论 -- K-th Largest 决策树 (2026-05-05 Discord drop)
    kth_method = _fetch_problem_meta_by_title(conn, "K-th Largest Collection 方法论")
    kth_method_row = _fmt_index_row(
        kth_method,
        "支持 insert(x) + kLargest() 的设计题方法论决策树: k 固定首选 size-k "
        "min-heap (LC 703), k 变化用 SortedList / Order Statistic Tree; "
        "次级维度 insert/query 比、值域 (桶)、删除 (双 heap lazy)、分布式 "
        "(local top-k merge)、多 k (必须 sorted/OST). 一句话: 先问 k 是否固定.",
    )

    # Graph / 连通分量 -- 文件与指令的级联故障 (2026-05-05 Discord drop)
    cascade = _fetch_problem_meta_by_title(conn, "文件与指令的级联故障")
    cascade_row = _fmt_index_row(
        cascade,
        "Doc + Query 二部图, 初始坏 Query 触发对称级联损坏; 核心洞察: "
        "Doc 损坏 ⟺ 与某初始坏 Query 同一连通分量, 退化成多源可达性. "
        "BFS 一次性求解 O(N+M) 首选 (反向索引 q->docs + 双 visited 集合); "
        "Union-Find 适合在线/多组查询, 易错点 visited 必须用 set, "
        "初始 Query 可能不在任何 Doc 中要 .get 兜底.",
    )

    # Graph / Dijkstra -- LC 778 Swim in Rising Water (2026-05-07 Discord index-only drop)
    lc778 = _fetch_problem_meta_by_leetcode_id(conn, 778)
    lc778_row = _fmt_index_row(
        lc778,
        "**最小瓶颈路径** (minimax path) -- 不是最短距离, 是路径上**最大值最小化**. "
        "改良 Dijkstra: 最小堆按 grid 值 push, 弹出时 `ret = max(ret, curCost)` 而非"
        "累加; 第一次到达终点即最优. visited 入堆即标记防重复. O(n^2 log n). "
        "替代: 二分答案 + BFS/DFS, 或 Union Find 按值升序合并到起终点连通. "
        "**同族**: LC 1631 (相邻差最大值最小化) / LC 1102 (路径最小值最大化, maximin).",
    )

    # Graph / 连通分量 -- LC 1101 Earliest Moment Everyone Become Friends + breakup follow-up (2026-05-07 Discord drop)
    lc1101 = _fetch_problem_meta_by_leetcode_id(conn, 1101)
    lc1101_row = _fmt_index_row(
        lc1101,
        "Vanilla DSU: 按 timestamp 升序合并, 真合并时 count -= 1, "
        "count == 1 即返回; O(m log m). **Follow-up 允许 breakup**: "
        "**禁用路径压缩** (与 rollback 互斥), union-by-rank only; 每次 "
        "union 压 snapshot 栈 `(rx, ry, old_rank_rx)`, breakup 弹栈反向"
        "赋值即可. 同 root 占位 op 也要压栈否则 op 流对不齐. "
        "**LIFO 假设**: 栈式 rollback 只能撤销最近 union; 任意时间点 "
        "breakup 是全动态连通性, 离线 D&C + rollback DSU 或 Link-Cut Trees.",
    )

    # Tree / Graph Validation -- UAG 是否为 valid binary tree (2026-05-07 Discord drop)
    uag_btree = _fetch_problem_meta_by_title(
        conn, "Undirected Acyclic Graph 是否为 Valid Binary Tree"
    )
    uag_btree_row = _fmt_index_row(
        uag_btree,
        "无向无环图判定为 binary tree: 三件套 acyclic + edges = N-1 + max_degree <= 3; "
        "等价 \"无环 + N-1 边 ⇔ 连通\" 来自 N 点 k 块森林必有 N-k 边; "
        "任一 degree <= 2 的点 (挑叶子) 即合法 root. "
        "Follow-up 同层同色: 候选 root 限定 degree <= 2, 暴力 O(N^2) BFS 早退; "
        "优化口子换根 DP O(N) 或异色对划禁止区域 (路径中点偶距离才约束).",
    )

    # Tree / Traversal -- 文件系统总大小计算 (Google R2 custom, 2026-05-07 Discord drop)
    fs_total = _fetch_problem_meta_by_title(conn, "文件系统总大小计算")
    fs_total_row = _fmt_index_row(
        fs_total,
        "文件系统树, 文件有 size, 目录 size = 子节点和, 求总大小. "
        "**真正的考点是开场澄清三连**: tree vs graph (symlink 成环)? 单次 vs 多次查询? 深度多大 (爆栈)? "
        "四档解法演进: Level 1 cycle-detection DFS (graph) -> Level 2 strict-tree 递归 -> "
        "Level 3 cache (多次查询; 最优做法是**直接挂 size 字段到节点**省 hash) -> "
        "Level 4 颜色标记法迭代后序 (防爆栈). **复盘**: 优化要分清是为时间 / 空间 / 健壮性, 三者手段完全不同.",
    )

    # BST / Tree Manipulation -- LC 450 Delete Node in a BST (2026-05-07 Discord drop)
    lc450 = _fetch_problem_meta_by_leetcode_id(conn, 450)
    lc450_row = _fmt_index_row(
        lc450,
        "BST 删除两步走: 递归 BST 二分找; 命中后三 case (0/1 child 直顶替, "
        "2 child 结构嫁接 -- 把 left 整团挂到 right 子树最左叶的 .left). "
        "封装为 `root.left = deleteNode(...)` 模板, 调用方挂回去. "
        "结构嫁接 vs successor-copy 两种主流写法: 前者短不改值但可能加深, 后者经典稳树高但改 root.val. "
        "O(h) 时间, 平均 O(log N) 最坏 O(N).",
    )

    # Matrix / Simulation -- LC 289 Game of Life (2026-05-07 Discord drop)
    lc289 = _fetch_problem_meta_by_leetcode_id(conn, 289)
    lc289_row = _fmt_index_row(
        lc289,
        "GoL 同时性更新核心是读写分离: 双 set 暂存 (O(mn) 空间) -> 原地状态编码 "
        "0/1/2/3 四态同时编码 \"原值+新值\" + 收尾 %2 归一化 (O(1) 额外); "
        "判邻居用 `in (1, 2)` 不是 `==1`. "
        "Follow-up 无限稀疏板: live set + 邻居计数 dict, 复杂度脱离板大小. "
        "易错 8 邻域别漏对角, dead+L=3 复活分支别漏.",
    )

    # Queue / Simulation -- 门禁通行模拟 (2026-05-07 Discord drop)
    door = _fetch_problem_meta_by_title(conn, "门禁通行模拟")
    door_row = _fmt_index_row(
        door,
        "口述题: 门每秒过 1 人, 同秒冲突按\"前一秒方向\"决优先 (idle/start 默认出门, "
        "同方向按原索引). **重点先问 6 个澄清** (吞吐量 / \"前一秒\"语义 / timestamp 重复 / "
        "已排序? / state 类型 / 数据规模) -- 上来就写代码反被反问。"
        "实现: 两 deque (enter_q/exit_q) + prev 状态 (-1/0/1) + 4 步主循环 "
        "(admit / 都空则跳时间-重置 prev / 按 prev 选队 / 出队). "
        "最大坑: 时间跳跃后**必须**把 prev 设回 idle 否则方向继承错乱. O(n log n) 排序.",
    )

    # DP / Counting -- LC 276 Paint Fence + 环形 follow-up (2026-05-07 Discord drop)
    lc276 = _fetch_problem_meta_by_leetcode_id(conn, 276)
    lc276_row = _fmt_index_row(
        lc276,
        "n 柱 k 色, 任意三连不全同色 (注意不是相邻不同色). "
        "线性版同色对称性把颜色维度消掉得 `same(i)=diff(i-1)`、"
        "`diff(i)=(k-1)*(same(i-1)+diff(i-1))`, 等价闭式 "
        "`a(n)=(k-1)*(a(n-1)+a(n-2))`. **环形 follow-up** 别试容斥, "
        "wrap 三连有两个 `(p_{n-1},p_n,p_1)` 和 `(p_n,p_1,p_2)` 容易漏; "
        "通用套路: 枚举头两位 `(p_1,p_2)` 锁住耦合, 剩下用同款线性 DP, "
        "末态查两个 wrap 三连即可. 教训: **不确定容斥就让 DP 兜底**.",
    )

    # Heap / Simulation -- LC 1606 Find Servers That Handled Most Number of Requests (2026-05-07 Discord drop)
    lc1606 = _fetch_problem_meta_by_leetcode_id(conn, 1606)
    lc1606_row = _fmt_index_row(
        lc1606,
        "环形找下一个空闲 server (i % k 起顺时针, 一圈不到就丢). "
        "方法一 SortedList(free) + min-heap(busy): `bisect_left(target)` "
        "二分, 落到末尾回卷 `free[0]`. 方法二只用 `heapq` + 编码技巧: "
        "把 idx 编码成 `i + (idx - i) % k`, 单堆 pop 即得 -- 滑窗不变量 "
        "(处理请求 i 之前堆里所有编码都在 [i, i+k-1]) 保证堆顶就是顺时针最近的空闲. "
        "Python `%` 永非负所以代码简洁, 移植 C++/Java/Go 须 `((idx - i) % k + k) % k`. "
        "O(n log k).",
    )

    # Heap / Simulation -- LC 1882 Process Tasks Using Servers (2026-05-05 Discord drop)
    lc1882 = _fetch_problem_meta_by_leetcode_id(conn, 1882)
    lc1882_row = _fmt_index_row(
        lc1882,
        "事件驱动模拟双堆: available 按 (weight, idx)、busy 按 "
        "(free_time, weight, idx); 任务 i 先释放 free_time <= i 的 busy "
        "回 available, 空了则弹 busy 顶部并把 taskTime 跳到该 free_time, "
        "避免按 tick 推进; busy 顶部已处理 tie-breaking 不需 release-all-then-pick. "
        "O((n+m) log n).",
    )

    lines: list[str] = [
        INDEX_SENTINEL,
        "",
        "# [Google] R2 Coding Index",
        "",
        "> **R2 Coding only** -- 不含 R1 ML fundamentals / R3 system design / behavioral。",
        "> 每条点击进入 ProblemDrawer 渲染 `problems` 表的完整笔记。",
        "> 使用 `db://<problems.id>` URI; 不使用 `cd://`(后者指向 `company_documents`)。",
        "",
        "## 收录标准",
        "",
        "- **R2 Coding only**: Google 现场的算法/数据结构题, 不含 ML fundamentals 八股、ML system design、behavioral。",
        "- **来源**: 真题 / 高频面经 / 同事面经 / 自定义扩展(如本期 LC 48 的矩形推广)。",
        "- **链接**: 一律 `db://<problems.id>` -- 复用 ProblemDrawer 渲染 `problems.notes`。",
        "  绝不使用 `cd://<id>` -- `cd://` 指向 `company_documents`, 会路由到错的 drawer 或 404。",
        "",
        "## 题目列表",
        "",
        "### Matrix / Geometry",
        "",
        lc48_row,
        "",
        "### Matrix / Flood Fill",
        "",
        square_islands_row,
        "",
        "### Prefix Sum / Hash",
        "",
        gold_row,
        eq_row,
        necklace_row,
        "",
        "### String / Two Pointers",
        "",
        one_swap_row,
        lc777_row,
        lc2337_row,
        "",
        "### Sliding Window",
        "",
        lc3859_row,
        "",
        "### Stack / 单调栈",
        "",
        fountain_row,
        lc496_row,
        lc1673_row,
        "",
        "### Sweep Line / 离散化 / 线段树",
        "",
        cake_row,
        "",
        "### Bipartite Matching / König",
        "",
        roof_row,
        rook_row,
        "",
        "### Math / Combinatorics / 容斥",
        "",
        combo_lock_row,
        "",
        "### Design / Data Structure / 方法论",
        "",
        kth_method_row,
        "",
        "### Graph / 连通分量",
        "",
        cascade_row,
        lc1101_row,
        "",
        "### Graph / Dijkstra",
        "",
        lc778_row,
        "",
        "### Tree / Graph Validation",
        "",
        uag_btree_row,
        "",
        "### Tree / Traversal",
        "",
        fs_total_row,
        "",
        "### BST / Tree Manipulation",
        "",
        lc450_row,
        "",
        "### Matrix / Simulation",
        "",
        lc289_row,
        "",
        "### Queue / Simulation",
        "",
        door_row,
        "",
        "### Heap / Simulation",
        "",
        lc1606_row,
        lc1882_row,
        "",
        "### DP / Counting",
        "",
        lc276_row,
        "",
        "---",
        "",
        "## 维护说明",
        "",
        f"本文档由 `scripts/seed_google_r2_coding_index_20260502.py` 生成,"
        f" sentinel = `{INDEX_SENTINEL}`。",
        "新增题目: 在脚本 `build_index_content()` 中按分组追加一行 `db://<id>`"
        " 后重跑脚本; 幂等替换整个文档内容。",
        "",
    ]
    return "\n".join(lines)


def upsert_index_doc(conn: sqlite3.Connection) -> tuple[int, str]:
    """INSERT or UPDATE the R2 Coding Index doc. Return (doc_id, action).

    action one of: 'INSERTED' | 'UPDATED' | 'UNCHANGED'.
    """
    content = build_index_content(conn)
    content_hash = _sha256(content)

    existing = conn.execute(
        "SELECT id, content_hash FROM company_documents "
        "WHERE company_id = ? AND title = ?",
        (GOOGLE_COMPANY_ID, INDEX_TITLE),
    ).fetchone()

    if existing:
        doc_id, old_hash = existing
        if old_hash == content_hash:
            return doc_id, "UNCHANGED"
        conn.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, "
            "    updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            (content, content_hash, doc_id),
        )
        return doc_id, "UPDATED"

    cur = conn.execute(
        "INSERT INTO company_documents "
        "(company_id, title, content, source_type, doc_kind, "
        " content_hash, is_golden) "
        "VALUES (?, ?, ?, 'prep_doc', ?, ?, 0)",
        (
            GOOGLE_COMPANY_ID,
            INDEX_TITLE,
            content,
            INDEX_DOC_KIND,
            content_hash,
        ),
    )
    return int(cur.lastrowid), "INSERTED"


def build_hub_block(index_doc_id: int) -> str:
    """Return the sentinel-wrapped crosslink block to UPSERT into the hub doc."""
    return (
        f"{HUB_BLOCK_BEGIN}\n"
        "\n"
        "**R2 Coding Index**\n"
        f"- [Google R2 Coding Index](cd://{index_doc_id}) -- "
        "R2 算法/DS 题目导航(db:// 入 ProblemDrawer)\n"
        f"{HUB_BLOCK_END}\n"
    )


def upsert_hub_block(
    conn: sqlite3.Connection, index_doc_id: int
) -> str:
    """Append-or-replace the sentinel-guarded crosslink block in the hub doc.

    Returns one of: 'INSERTED' | 'UPDATED' | 'UNCHANGED'.

    Block is matched by the begin/end sentinel pair. If both sentinels are
    found, the block (inclusive of both sentinels and trailing newline) is
    replaced. Otherwise the block is appended at end-of-content.
    """
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id = ?",
        (HUB_DOC_ID,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"[FAIL] hub doc id={HUB_DOC_ID} missing")
    old_content = row[0] or ""

    new_block = build_hub_block(index_doc_id)

    has_begin = HUB_BLOCK_BEGIN in old_content
    has_end = HUB_BLOCK_END in old_content
    if has_begin != has_end:
        raise SystemExit(
            "[FAIL] hub doc has only one of the begin/end sentinels -- "
            "manual repair required before re-running"
        )

    if has_begin and has_end:
        begin_idx = old_content.index(HUB_BLOCK_BEGIN)
        end_idx = old_content.index(HUB_BLOCK_END) + len(HUB_BLOCK_END)
        # Consume trailing newline if present so re-insertion stays clean.
        if end_idx < len(old_content) and old_content[end_idx] == "\n":
            end_idx += 1
        new_content = old_content[:begin_idx] + new_block + old_content[end_idx:]
    else:
        sep = "" if old_content.endswith("\n\n") else (
            "\n" if old_content.endswith("\n") else "\n\n"
        )
        new_content = old_content + sep + new_block

    if new_content == old_content:
        return "UNCHANGED"

    conn.execute(
        "UPDATE company_documents "
        "SET content = ?, content_hash = ?, "
        "    updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (new_content, _sha256(new_content), HUB_DOC_ID),
    )
    return "UPDATED" if has_begin else "INSERTED"


def main() -> int:
    """Run both idempotent UPSERTs (index doc + hub crosslink). Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_google_r2_index")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        # Verify the linked problem exists BEFORE writing anything.
        _fetch_problem_meta(conn, 73)

        doc_id, doc_action = upsert_index_doc(conn)
        print(f"[{doc_action}] index doc id={doc_id} title={INDEX_TITLE!r}")

        hub_action = upsert_hub_block(conn, doc_id)
        print(
            f"[{hub_action}] hub doc id={HUB_DOC_ID} "
            f"crosslink -> cd://{doc_id}"
        )

        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
