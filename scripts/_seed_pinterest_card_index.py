"""Seed the Pinterest card_index document (T-P1-440).

Creates a single `card_index` company_document under Pinterest (company_id=29)
that groups the 29 Pinterest-tagged problems into 10 cluster cards. Also tags
LC 85 (Maximal Rectangle, problems.id=242) with 'Pinterest' in the JSON
company_tags column so it surfaces on the Pinterest problems tab.

Idempotent: re-running updates the existing card_index doc in place
(matched by company_id + doc_kind + title) instead of creating duplicates.

Commit: [T-P1-440] (internal ID T-P1-224 per task spec)
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PINTEREST_COMPANY_ID = 29
DOC_TITLE = "Pinterest Prep Card Index"
DOC_KIND = "card_index"
SOURCE_TYPE = "manual"

LC_85_PROBLEM_ID = 242  # verified: problems.id=242 has leetcode_id=85

# Card definitions: each card lists problems.id values in display order.
# Summaries emphasize the shared pattern/skill the card exercises.
CARDS: list[dict] = [
    {
        "name_zh": "字符串/数字运算",
        "name_en": "String / Digit Arithmetic",
        "summary_zh": "核心：carry propagation, partition('.') 解析, shift-based 精度舍入",
        "problems": [
            (135, "逐位乘法 pos[i+j] / pos[i+j+1]"),
            (1073, "half-up 进位链，禁用 float()"),
            (1074, "shift 复用 1073 + 还原"),
        ],
    },
    {
        "name_zh": "单调栈/直方图",
        "name_en": "Monotonic Stack / Histogram",
        "summary_zh": "核心：单调递增栈 + 哨兵，2D 转 1D 直方图",
        "problems": [
            (85, "单调栈 + 左右边界，O(n) 扫描"),
            (242, "每行做一次 LC 84，累积最大矩形"),
        ],
    },
    {
        "name_zh": "贪心差分",
        "name_en": "Greedy on Differences",
        "summary_zh": "核心：相邻差分取正/绝对值，O(n) 一次扫描",
        "problems": [
            (236, "相邻差分取正累加即最小操作数"),
            (157, "通用差分：abs(diff)/2 + edge"),
        ],
    },
    {
        "name_zh": "仓储/箱子装填",
        "name_en": "Warehouse / Box Packing",
        "summary_zh": "核心：prefix-min 房间约束 + 贪心匹配（单向/双向）",
        "problems": [
            (1069, "排序 + 前缀最小房间容量"),
            (1070, "双指针双向贪心装填"),
        ],
    },
    {
        "name_zh": "图论/欧拉/BFS",
        "name_en": "Graph / Eulerian / BFS",
        "summary_zh": "核心：Hierholzer 欧拉路径、多源 BFS、结算差分",
        "problems": [
            (148, "字典序 Hierholzer 欧拉路径"),
            (217, "站点 -> 公交路线倒排 + 多源 BFS"),
            (214, "净额差分 + 回溯搜索最少交易"),
        ],
    },
    {
        "name_zh": "回溯/DFS",
        "name_en": "Backtracking / DFS",
        "summary_zh": "核心：运算符枚举、树剪枝、工人-工时状压/回溯",
        "problems": [
            (439, "+/-/* 运算符插入 + 连续乘法修正"),
            (1066, "后序 DFS 同时删除与返回森林"),
            (1067, "回溯 + 剪枝最小化最大工时"),
        ],
    },
    {
        "name_zh": "DP/二分",
        "name_en": "DP / Binary Search",
        "summary_zh": "核心：完全背包、二分答案+可行性、贪心覆盖",
        "problems": [
            (55, "完全背包 DP，O(amount * n)"),
            (265, "二分 largest sum + 可行性贪心"),
            (498, "贪心指针覆盖 + 跳跃表加速"),
        ],
    },
    {
        "name_zh": "堆/模拟/设计",
        "name_en": "Heap / Simulation / Design",
        "summary_zh": "核心：双堆会议室、排行榜热点、Trie + 权重 top-K、稀疏矩阵",
        "problems": [
            (258, "双堆：free/busy 会议室调度"),
            (199, "HashMap + top-K 堆排行榜"),
            (237, "Trie + 节点级 top-3 补全"),
            (277, "dict-of-dict 稀疏矩阵乘法"),
        ],
    },
    {
        "name_zh": "区间/子序列",
        "name_en": "Interval / Subsequence",
        "summary_zh": "核心：离线排序 + 小顶堆，双指针子序列匹配",
        "problems": [
            (144, "离线按 query 扫描 + 小顶堆"),
            (417, "双指针线性子序列判断"),
        ],
    },
    {
        "name_zh": "Pinterest 定制题",
        "name_en": "Pinterest Custom",
        "summary_zh": "核心：面经专属—逃脱房、光束传播、前缀词典、DAG 权限、Pin 连通",
        "problems": [
            (1068, "BFS 状态 = (rooms, people) 元组"),
            (1071, "BFS 光束 + 镜子/分束传播"),
            (1072, "lower_bound + 前缀匹配验证"),
            (1075, "DAG 权限传播 + 拓扑或记忆化"),
            (1076, "并查集 + 动态关系连通性"),
        ],
    },
]


def build_card_payload(conn: sqlite3.Connection) -> dict:
    """Build the JSON content, resolving (leetcode_id, title) per problem."""
    cards_out = []
    for card in CARDS:
        problems_out = []
        for pid, one_liner in card["problems"]:
            row = conn.execute(
                "SELECT leetcode_id, title FROM problems WHERE id=?", (pid,)
            ).fetchone()
            if row is None:
                raise SystemExit(f"[FAIL] problems.id={pid} not found")
            lc_id, title = row
            problems_out.append(
                {
                    "id": pid,
                    "leetcode_id": lc_id,
                    "title": title,
                    "one_liner": one_liner,
                }
            )
        cards_out.append(
            {
                "name_zh": card["name_zh"],
                "name_en": card["name_en"],
                "summary_zh": card["summary_zh"],
                "problems": problems_out,
            }
        )
    return {"schema_version": 1, "cards": cards_out}


def tag_lc85_pinterest(conn: sqlite3.Connection) -> None:
    """Append 'Pinterest' to LC 85's company_tags JSON list (idempotent)."""
    row = conn.execute(
        "SELECT company_tags FROM problems WHERE id=?", (LC_85_PROBLEM_ID,)
    ).fetchone()
    if row is None:
        raise SystemExit(f"[FAIL] problems.id={LC_85_PROBLEM_ID} (LC 85) missing")
    raw = row[0]
    tags = json.loads(raw) if raw else []
    if "Pinterest" in tags:
        print("[SKIP] LC 85 already tagged Pinterest")
        return
    tags.append("Pinterest")
    conn.execute(
        "UPDATE problems SET company_tags=? WHERE id=?",
        (json.dumps(tags, ensure_ascii=False), LC_85_PROBLEM_ID),
    )
    print(f"[DONE] LC 85 company_tags -> {tags}")


def upsert_card_index(conn: sqlite3.Connection, payload: dict) -> None:
    """Create or update the single Pinterest card_index document."""
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    row = conn.execute(
        "SELECT id FROM company_documents "
        "WHERE company_id=? AND doc_kind=? AND title=?",
        (PINTEREST_COMPANY_ID, DOC_KIND, DOC_TITLE),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE company_documents "
            "SET content=?, source_type=?, updated_at=CURRENT_TIMESTAMP "
            "WHERE id=?",
            (content, SOURCE_TYPE, row[0]),
        )
        print(f"[DONE] Updated card_index doc id={row[0]}")
    else:
        cur = conn.execute(
            "INSERT INTO company_documents "
            "(company_id, title, content, source_type, doc_kind) "
            "VALUES (?, ?, ?, ?, ?)",
            (PINTEREST_COMPANY_ID, DOC_TITLE, content, SOURCE_TYPE, DOC_KIND),
        )
        print(f"[DONE] Inserted card_index doc id={cur.lastrowid}")


def seed() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("BEGIN")
        tag_lc85_pinterest(conn)
        payload = build_card_payload(conn)
        upsert_card_index(conn, payload)
        conn.execute("COMMIT")

        total = sum(len(card["problems"]) for card in payload["cards"])
        print(
            f"[VERIFY] {len(payload['cards'])} cards, {total} problems total"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
