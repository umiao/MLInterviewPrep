"""Idempotent seed: create / refresh the 'Uber LC 题库索引视图 (Index View)'
company_document under company_id=5 (Uber).

Source: 47 curated LeetCode problems = (user-provided 50-item list ∩ has-notes)
∪ (the 19 deep-dive entries already in doc id=30 'Uber BPS LeetCode Solutions
Guide'). Sibling to doc id=30; this is the breadth-index, that is the depth-精讲.

Run: python scripts/seed_uber_lc_index.py
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """Mirror of frontend src/utils/slugify.ts so group anchors match the
    heading IDs that MarkdownPreview's HeadingWithId injects.

    Rules (must stay in lockstep with the JS):
      1. lowercase + trim
      2. whitespace runs -> single hyphen
      3. drop chars NOT in [A-Za-z0-9_], CJK Basic (U+4E00..U+9FFF),
         CJK Extension A (U+3400..U+4DBF), or hyphen
      4. collapse multi-hyphens
      5. trim leading/trailing hyphens
    """
    s = text.lower().strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^A-Za-z0-9_一-鿿㐀-䶿-]", "", s)
    s = re.sub(r"-+", "-", s)
    s = re.sub(r"^-|-$", "", s)
    return s

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
UBER_COMPANY_ID = 5
DOC_TITLE = "Uber LC 题库索引视图 (Index View)"
SENTINEL = "<!-- UBER_LC_INDEX_V1 -->"

# 6 problems in problem_company_tags relational table → mark [NEW]
NEW_LC_IDS = {384, 427, 827, 1428, 1429, 2571}

# Group → ordered list of (lc_id, chinese_summary) tuples.
# Title / difficulty / family / pattern fetched live from DB; summaries hand-authored.
GROUPS: list[tuple[str, list[tuple[int, str]]]] = [
    (
        "Tree / 树遍历 + Tree DP",
        [
            (230, "在 BST 中找第 k 小; 中序遍历到第 k 个停, $O(h+k)$"),
            (337, "树形 DP; 每节点返回 (rob, no_rob) 二元组取最优"),
            (545, "二叉树边界; 一遍 DFS + 4 状态 flag (ROOT/LEFT/RIGHT/INNER), deque appendleft 收右边界"),
            (549, "树上最长连续路径 (双向); 后序返回 (inc, dec) 同时更新答案"),
            (987, "按列遍历; DFS 携带 (col, row) 后按 (col, row, val) 排序输出"),
            (2791, "树上回文路径计数; bitmask XOR + DFS, 同奇偶性子树两两组合"),
            (2858, "Tree DP rerooting; 一次 DFS 算根, 二次 DFS 换根传播"),
        ],
    ),
    (
        "Graph / BFS / DFS / Grid",
        [
            (200, "岛屿计数; DFS / BFS 染色, $O(mn)$"),
            (207, "拓扑排序判环; Kahn (BFS) 或 DFS 三色"),
            (210, "拓扑排序输出顺序; Kahn 法直接得序列"),
            (269, "外星字典推字符顺序; 相邻单词比 → 建图 → 拓扑"),
            (815, "公交换乘最少次数; **BFS on stops** (而非 routes), 用 stop_to_routes 映射加速"),
            (864, "状态压缩 BFS; 状态 = (位置, 持有钥匙 bitmask)"),
            (994, "多源 BFS; 所有 rotten 同时入队, 层数 = 时间"),
            (1020, "飞地计数; 反向思路, 从边界 DFS 标记可达陆地后数剩余"),
            (1197, "马最少步; BFS + 对称剪枝到第一象限"),
        ],
    ),
    (
        "Union-Find / 并查集",
        [
            (305, "在线添陆地; UF 维护连通分量数, 新格 union 上下左右"),
            (547, "朋友圈数; UF 模板, 邻接矩阵遍历"),
            (827, "翻一格 0 后最大岛; UF 预标记每岛大小, 枚举 0 格累加邻岛 (用 set 去重)"),
            (1697, "离线查询 + 排序 + UF; 边按权重升序合并到 limit 阈值"),
            (2503, "离线查询 + UF + 多源 BFS; 按 query 阈值递增合并格子"),
        ],
    ),
    (
        "Stateful DS Design / 设计题",
        [
            (146, "LRU Cache; HashMap + 双向链表, get/put 均 $O(1)$"),
            (362, "5min 滑窗计数; 60 桶循环缓冲 或 deque 弹尾"),
            (380, "Insert / Delete / GetRandom $O(1)$; 数组 + map, 删除时 swap-pop"),
            (855, "考场座位最大化最小距离; 排序列表 + 扫相邻对中点 + 端点"),
            (1244, "玩家分数榜; HashMap + 全排序或 BIT 加速 topK"),
            (2402, "双堆模拟 (空闲房 + 占用房); 按开始时间安排会议"),
        ],
    ),
    (
        "Heap / TopK / Greedy",
        [
            (23, "k 路归并; 最小堆维护每路头, $O(N \\log k)$"),
            (502, "IPO 双堆; 入门按 capital 排小顶, 满足资本者入大顶按 profit"),
            (1696, "DP + 单调双端队列; $dp[i] = nums[i] + \\max(dp[i-k..i-1])$"),
        ],
    ),
    (
        "Backtracking / Trie",
        [
            (17, "数字键盘字母组合; 经典回溯, 树深 = 数字位数"),
            (79, "网格找单词; DFS + 临时标记 + 回溯还原"),
            (212, "网格找多词; Trie + DFS, 沿 trie 走避免重复探查每个单词"),
        ],
    ),
    (
        "Sliding Window / Two Pointers",
        [
            (121, "单次买卖; 维护历史最小 + 当前差最大, 一次扫描"),
            (977, "已排序数组平方; 双指针从两端比绝对值, 倒序填结果"),
            (1438, "滑窗 + 单调双队列同时维护 max / min, 差超 limit 时左指针推进"),
        ],
    ),
    (
        "Binary Search / 二分（含答案二分）",
        [
            (162, "找任一峰值; 二分 nums[mid] vs nums[mid+1] 决定方向"),
            (410, "分 m 段最小化最大段和; **二分答案** + 贪心可行性 check"),
            (981, "按时间戳查值; 每 key 一个 (ts, val) 列表, 二分查 ≤ ts 的最大"),
            (2861, "**二分答案**; check(val) 遍 k 机器算 requiredBudget, 'find largest valid' 模板"),
        ],
    ),
    (
        "DP / 区间 / 字符串",
        [
            (5, "最长回文子串; 中心扩展 $O(n^2)$ 或 Manacher $O(n)$"),
            (56, "区间合并; 按起点排序后扫描合并重叠, 经典 interval 模板"),
        ],
    ),
    (
        "Bit / Greedy / Misc",
        [
            (384, "Fisher-Yates 洗牌; 每步从 [i, n-1] 随机 swap, 与 reservoir sampling 同款望远镜概率"),
            (427, "四叉树构造; 递归四分, 全同则叶节点否则建内部节点"),
            (1428, "行排序矩阵找最左 1; 阶梯法 $O(m+n)$ 从右上往左下走"),
            (1429, "流式找首个唯一; 哈希计数 + 双向链表维护当前唯一队列, $O(1)$ 摊还"),
            (2571, "$\\pm 2^k$ 最少操作; 位运算贪心, `n & 3 == 3` 加否则减, 进位链合并 1-run"),
        ],
    ),
]


def fetch_problem_meta(conn: sqlite3.Connection, lc_id: int) -> tuple[str, str, str | None, str | None]:
    """Return (title, difficulty, family, pattern) for a leetcode_id."""
    row = conn.execute(
        "SELECT title, difficulty, family, pattern FROM problems WHERE leetcode_id = ?",
        (lc_id,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"LC {lc_id} not in problems table — fix GROUPS")
    return row


def render_entry(conn: sqlite3.Connection, lc_id: int, summary: str) -> str:
    """Render one bullet line with drawer link + summary + family/pattern suffix."""
    title, difficulty, family, pattern = fetch_problem_meta(conn, lc_id)
    diff_label = (difficulty or "?").lower()
    new_tag = " **[NEW]**" if lc_id in NEW_LC_IDS else ""
    meta_bits: list[str] = []
    if family:
        meta_bits.append(f"family: `{family}`")
    if pattern:
        meta_bits.append(f"pattern: `{pattern}`")
    meta_suffix = f"  *{' | '.join(meta_bits)}*" if meta_bits else ""
    return (
        f"- [LC {lc_id}. {title}](lc://{lc_id}) "
        f"`[{diff_label}]` — {summary}.{new_tag}{meta_suffix}"
    )


def build_content(conn: sqlite3.Connection) -> str:
    """Build the full markdown body, including sentinel + all groups."""
    total = sum(len(items) for _, items in GROUPS)
    new_count = sum(1 for _, items in GROUPS for lc, _ in items if lc in NEW_LC_IDS)

    lines: list[str] = [
        SENTINEL,
        "",
        "# Uber LC 题库索引视图 (Index View)",
        "",
        f"> **{total} 道**带 Uber tag 且**已有题解**的 LeetCode 题目快速导航。",
        "> 与 *Uber BPS LeetCode Solutions Guide* (深度精讲) 是兄弟关系——本文档是**宽度索引**, "
        "那是**深度题解**, 索引中带 `lc://N` 的链接点击会以 SlideOverPanel 弹出该题完整笔记。",
        ">",
        f"> **覆盖**: 47 题 (38 来自用户 curated 50-list 中已有题解的部分 + 9 来自 doc id=30 独占题), "
        "按知识点 / pattern 分 10 组, 组内按 LeetCode id 升序。",
        f"> **`[NEW]`**: 标 `[NEW]` 的 {new_count} 道是 2026-04 期间新加入的, "
        "在 `problem_company_tags` 关系表中也有显式 Uber 关联。",
        ">",
        "> **未列入索引** (无题解, 待补): "
        "LC 679, 719, 1101, 1475, 1931, 2092, 2389, 2561, 3419, 3629; "
        "LC 2954 (DB 缺录入)。",
        "",
        "---",
        "",
        "## 概览",
        "",
        f"| 维度 | 数量 |",
        f"| --- | --- |",
        f"| 总题数 | **{total}** |",
        f"| 分组数 | {len(GROUPS)} |",
        f"| `[NEW]` 标记 | {new_count} |",
        f"| 来自 doc id=30 (深度精讲) | 19 (其中 {len([lc for _, items in GROUPS for lc, _ in items if lc in {17,23,79,230,337,547,549,815,977,981,987,994,1020,1197,1696,1697,2503,2791,2858}])} 道在本索引中) |",
        "",
        "## 分组总览",
        "",
    ]
    lines.append("| # | 分组 | 题数 | LC ids |")
    lines.append("| --- | --- | --- | --- |")
    for idx, (group_name, items) in enumerate(GROUPS, 1):
        ids_str = ", ".join(str(lc) for lc, _ in items)
        anchor = slugify(group_name)
        # Drawer-link to the group section (frontend HeadingWithId injects matching id)
        lines.append(f"| {idx} | [{group_name}](#{anchor}) | {len(items)} | {ids_str} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-group sections
    for group_name, items in GROUPS:
        lines.append(f"## {group_name}")
        lines.append("")
        for lc_id, summary in items:
            lines.append(render_entry(conn, lc_id, summary))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 维护说明")
    lines.append("")
    lines.append(
        "本文档由 `scripts/seed_uber_lc_index.py` 生成，sentinel = "
        f"`{SENTINEL}`。"
    )
    lines.append(
        "添加 / 删除题目: 编辑脚本里的 `GROUPS` 列表后重跑脚本; 幂等替换 "
        "`company_documents` 中本 sentinel 标记的整个内容。"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Build the index doc + INSERT or UPDATE company_documents."""
    if not DB_PATH.exists():
        raise SystemExit(f"DB not found: {DB_PATH}")

    # Backup before write
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_uber_lc_index")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        # Verify all 47 problems exist (fail loud if not)
        for _, items in GROUPS:
            for lc_id, _ in items:
                fetch_problem_meta(conn, lc_id)

        content = build_content(conn)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        existing = conn.execute(
            "SELECT id, content, content_hash FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (UBER_COMPANY_ID, DOC_TITLE),
        ).fetchone()

        if existing:
            doc_id, old_content, old_hash = existing
            if old_hash == content_hash:
                print(
                    f"[UNCHANGED] doc id={doc_id} "
                    f"content_hash matches ({content_hash[:12]}...)"
                )
                return
            conn.execute(
                "UPDATE company_documents "
                "SET content = ?, content_hash = ?, "
                "    updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (content, content_hash, doc_id),
            )
            print(
                f"[UPDATED] doc id={doc_id} "
                f"old_len={len(old_content) if old_content else 0} "
                f"new_len={len(content)} hash={content_hash[:12]}..."
            )
        else:
            cur = conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                " content_hash, is_golden) "
                "VALUES (?, ?, ?, 'prep_doc', 'prep_note', ?, 0)",
                (UBER_COMPANY_ID, DOC_TITLE, content, content_hash),
            )
            print(
                f"[INSERTED] doc id={cur.lastrowid} "
                f"len={len(content)} hash={content_hash[:12]}..."
            )

        conn.commit()


if __name__ == "__main__":
    main()
