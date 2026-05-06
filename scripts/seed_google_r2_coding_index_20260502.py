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
        "### Prefix Sum / Hash",
        "",
        gold_row,
        eq_row,
        "",
        "### String / Two Pointers",
        "",
        lc2337_row,
        "",
        "### Sliding Window",
        "",
        lc3859_row,
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
