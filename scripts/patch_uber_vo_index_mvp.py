"""Patch id=37 'Uber VO 完整准备指南' to act as the multi-charter MVP index.

T-P0-632 ([UBER-VO-5 MVP]): Adds anchor-deep-link tables for Round 2 (ML
Coding, db://84#...) and Round 3 (ML SD, db://85#...), a top-level Charter
quick-index, a Round 1 reference to id=81, a Round 4 cross-link to
/behavioral/themes?company=uber, and a bottom HR Call section linking id=36.

The patch is idempotent via sentinel HTML comment markers
(``<!-- T-P0-632:<KEY> BEGIN/END -->``). Re-running with unchanged block
content yields zero net change. All existing H2 heading TEXT is preserved
(anchor-stability invariant from T-P1-631 also applies here).

Resolves NEW_DOC_ID and NEW_SD_DOC_ID at runtime from
``company_documents`` titles to avoid hard-coded ids drifting.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"

COMPANY_ID = 5  # Uber
TARGET_DOC_TITLE = "Uber VO 完整准备指南 (Virtual Onsite)"
LC_INDEX_DOC_ID = 81
DESIGN_PREP_DOC_ID = 33
HR_CALL_DOC_ID = 36
ML_CODING_TITLE_LIKE = "%Uber ML Coding Golden%"
ML_SD_TITLE_LIKE = "%Uber ML System Design Golden%"


def compute_hash(content: str) -> str:
    """SHA-256 over UTF-8 bytes — used as the idempotency key."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def resolve_doc_id(cursor: sqlite3.Cursor, title_like: str) -> int:
    """Look up a single doc id by title LIKE pattern.

    Errors out loudly if 0 or >1 rows match — keeps the script honest
    when upstream seed runs are missing or ambiguous.
    """
    cursor.execute(
        "SELECT id FROM company_documents "
        "WHERE company_id = ? AND title LIKE ?",
        (COMPANY_ID, title_like),
    )
    rows = cursor.fetchall()
    if len(rows) != 1:
        raise SystemExit(
            f"[ERROR] expected exactly 1 row matching {title_like!r}, "
            f"got {len(rows)}: {rows}"
        )
    return int(rows[0][0])


def render_charters_block(ml_coding_id: int, ml_sd_id: int) -> str:
    """Top-level multi-charter quick index inserted before '## 一、VO概览'."""
    return (
        "## 多 Charter 快速索引\n"
        "\n"
        "> Uber VO 共 4 轮主面 + 1 轮 HR. 本节是多 charter 入口, "
        "每一行直接 deep-link 到对应 Golden Answer / 索引文档.\n"
        "\n"
        "| Charter | 入口文档 | 重点内容 |\n"
        "|---------|---------|----------|\n"
        f"| Round 1 LC 算法题 | [Uber LC 题库索引视图](db://{LC_INDEX_DOC_ID}) | "
        "47 题按算法家族 (Tree / Graph / DP / Sliding Window 等) 索引 |\n"
        f"| Round 2 ML Coding | [Uber ML Coding Golden Answer 集合](db://{ml_coding_id}) | "
        "几何中位数 / Kmeans (numpy-only) / Linear Reg / Logistic Reg 4 道 from-scratch |\n"
        f"| Round 3 ML System Design | [Uber ML System Design Golden Answers](db://{ml_sd_id}) | "
        "Uber Eats 餐厅推荐 + Budget-Constrained Promo Recommendation |\n"
        "| Round 4 Behavioral | "
        "[/behavioral/themes?company=uber](/behavioral/themes?company=uber) | "
        "Trust / Respect / Conviction 三大维度按主题筛选 |\n"
        f"| HR Call | [Uber HR Call Prep Notes](db://{HR_CALL_DOC_ID}) | "
        "HR Round 高频问题、薪酬、签证 |\n"
        "\n"
        "---\n"
    )


def render_r1_index_block() -> str:
    """One-line Round 1 pointer to id=81 — slotted into the existing 关联资源 list."""
    return (
        f"- See [Uber LC 题库索引视图](db://{LC_INDEX_DOC_ID}) "
        "for the curated 47-problem index by family.\n"
    )


def render_r2_mlcoding_block(ml_coding_id: int) -> str:
    """Round 2 — 4 anchor-deep-links into the ML Coding Golden Answer doc."""
    return (
        "### ML Coding Golden Answers (Staff-Level)\n"
        "\n"
        "| 题目 | Deep-Link |\n"
        "|------|-----------|\n"
        f"| 几何中位数 (Geometric Median) | "
        f"[db://{ml_coding_id}#geometric-median]"
        f"(db://{ml_coding_id}#geometric-median) |\n"
        f"| K-Means (numpy-only) | "
        f"[db://{ml_coding_id}#kmeans-numpy]"
        f"(db://{ml_coding_id}#kmeans-numpy) |\n"
        f"| Linear Regression from scratch | "
        f"[db://{ml_coding_id}#linear-regression-from-scratch]"
        f"(db://{ml_coding_id}#linear-regression-from-scratch) |\n"
        f"| Logistic Regression from scratch | "
        f"[db://{ml_coding_id}#logistic-regression-from-scratch]"
        f"(db://{ml_coding_id}#logistic-regression-from-scratch) |\n"
        "\n"
        "> 每题均为 Staff-level Golden Answer "
        "(题目 → Clarify → Brute-force → Optimal → Trade-off → "
        "Follow-up scaling → 行业黑话). "
        f"跨题通用面试要点见 [db://{ml_coding_id}#cross-cutting-tactics]"
        f"(db://{ml_coding_id}#cross-cutting-tactics).\n"
    )


def render_r3_mlsd_block(ml_sd_id: int) -> str:
    """Round 3 — 2 anchor-deep-links into the ML System Design doc + id=33 callout."""
    return (
        "### ML System Design Golden Answers (Staff-Level)\n"
        "\n"
        "| 题目 | Deep-Link |\n"
        "|------|-----------|\n"
        "| Uber Eats 餐厅推荐系统 (Restaurant Recommendation) | "
        f"[db://{ml_sd_id}#uber-eats-restaurant-rec]"
        f"(db://{ml_sd_id}#uber-eats-restaurant-rec) |\n"
        "| Budget-Constrained Promo Recommendation (uplift × Lagrangian) | "
        f"[db://{ml_sd_id}#budget-promo-recommendation]"
        f"(db://{ml_sd_id}#budget-promo-recommendation) |\n"
        "\n"
        "> 跨题通用 Senior 信号速查表见 "
        f"[db://{ml_sd_id}#cross-cutting-senior-signals]"
        f"(db://{ml_sd_id}#cross-cutting-senior-signals).\n"
        "\n"
        "> 搜推系统强化点详见 "
        f"[Uber BPS Design & Architecture Prep](db://{DESIGN_PREP_DOC_ID}) — "
        "含 13 个搜推强化关键词 (training-serving skew, MMoE, two-tower, H3, "
        "position bias, off-policy eval, cluster A/B, feature snapshot, "
        "Michelangelo, graceful degradation, Model+Policy 双层防御 等) "
        "的强化讨论.\n"
    )


def render_r4_behavioral_block() -> str:
    """Round 4 — cross-link to /behavioral/themes?company=uber."""
    return (
        "### 跨主题筛选\n"
        "\n"
        "> 按主题筛选 Uber 行为面试题: "
        "[/behavioral/themes?company=uber](/behavioral/themes?company=uber) "
        "— 按 Trust / Respect / Conviction 三大维度过滤所有 Uber 行为面试题, "
        "支持公司 + 主题双重 filter.\n"
    )


def render_hr_call_block() -> str:
    """Bottom HR Call section pointing to id=36."""
    return (
        "## HR Call 准备\n"
        "\n"
        f"详见 [Uber HR Call Prep Notes](db://{HR_CALL_DOC_ID}) — 涵盖 HR Round 高频问题、"
        "Q&A 准备、薪酬讨论提示、签证 (visa) 与 logistics 问题等.\n"
        "\n"
        "---\n"
    )


def upsert_block(content: str, key: str, body: str, anchor_pattern: str,
                 mode: str) -> str:
    """Idempotent insert-or-replace of a sentinel-bracketed block.

    If sentinel pair exists, replace its body. Otherwise, locate the regex
    ``anchor_pattern`` (first match) and inject the block ``mode``-relative to
    it. ``mode`` is one of ``"before"`` or ``"after"``.
    """
    begin = f"<!-- T-P0-632:{key} BEGIN -->"
    end = f"<!-- T-P0-632:{key} END -->"
    new_block = f"{begin}\n{body}{end}\n"

    sentinel_re = re.compile(
        re.escape(begin) + r".*?" + re.escape(end) + r"\n?",
        re.DOTALL,
    )
    if sentinel_re.search(content):
        return sentinel_re.sub(new_block, content, count=1)

    m = re.search(anchor_pattern, content)
    if not m:
        raise SystemExit(
            f"[ERROR] anchor pattern {anchor_pattern!r} not found for key {key!r}"
        )
    if mode == "before":
        return content[: m.start()] + new_block + "\n" + content[m.start():]
    if mode == "after":
        return content[: m.end()] + "\n" + new_block + content[m.end():]
    raise SystemExit(f"[ERROR] unknown mode {mode!r} for key {key!r}")


def patch_content(original: str, ml_coding_id: int, ml_sd_id: int) -> str:
    """Apply all six MVP patches in order. Idempotent across re-runs."""
    out = original

    out = upsert_block(
        out,
        key="CHARTERS",
        body=render_charters_block(ml_coding_id, ml_sd_id),
        anchor_pattern=r"## 一、VO概览",
        mode="before",
    )

    out = upsert_block(
        out,
        key="R1-INDEX",
        body=render_r1_index_block(),
        anchor_pattern=(
            r"- \[Uber LeetCode题目列表 \(Reddit\)\][^\n]*-- \*\*必须全部完成\*\*\n"
        ),
        mode="after",
    )

    out = upsert_block(
        out,
        key="R2-MLCODING",
        body=render_r2_mlcoding_block(ml_coding_id),
        anchor_pattern=(
            r"### 关联资源\n"
            r"- \*\*ML Fundamentals From-Scratch[^\n]*\n"
            r"- \*\*KNN & ML Fundamentals Review[^\n]*\n"
        ),
        mode="after",
    )

    out = upsert_block(
        out,
        key="R3-MLSD",
        body=render_r3_mlsd_block(ml_sd_id),
        anchor_pattern=(
            r"### System Design常见主题\n"
            r"(?:- \[ \] [^\n]*\n)+"
        ),
        mode="after",
    )

    out = upsert_block(
        out,
        key="R4-BEHAVIORAL",
        body=render_r4_behavioral_block(),
        anchor_pattern=(
            r"### Behavioral准备清单\n"
            r"(?:- \[ \] [^\n]*\n)+"
        ),
        mode="after",
    )

    out = upsert_block(
        out,
        key="HR-CALL",
        body=render_hr_call_block(),
        anchor_pattern=r"## 七、重要链接汇总",
        mode="before",
    )

    return out


def main() -> int:
    """Read id=37 content, patch via sentinel UPSERT, write back if changed."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    ml_coding_id = resolve_doc_id(cursor, ML_CODING_TITLE_LIKE)
    ml_sd_id = resolve_doc_id(cursor, ML_SD_TITLE_LIKE)
    print(f"[RESOLVE] ml_coding_id={ml_coding_id} ml_sd_id={ml_sd_id}")

    cursor.execute(
        "SELECT id, content, content_hash FROM company_documents "
        "WHERE company_id = ? AND title = ?",
        (COMPANY_ID, TARGET_DOC_TITLE),
    )
    row = cursor.fetchone()
    if row is None:
        raise SystemExit(
            f"[ERROR] target doc not found: company_id={COMPANY_ID} "
            f"title={TARGET_DOC_TITLE!r}"
        )
    doc_id, original, old_hash = row

    new_content = patch_content(original, ml_coding_id, ml_sd_id)
    new_hash = compute_hash(new_content)

    if new_hash == old_hash:
        print(f"[NOOP]   doc_id={doc_id} content_hash unchanged "
              f"({new_hash[:12]}) -- idempotent re-run")
        conn.close()
        return 0

    cursor.execute(
        "UPDATE company_documents SET "
        "content = ?, content_hash = ?, updated_at = datetime('now') "
        "WHERE id = ?",
        (new_content, new_hash, doc_id),
    )
    conn.commit()
    print(f"[UPDATE] doc_id={doc_id} chars={len(new_content)} "
          f"old={old_hash[:12] if old_hash else 'NULL'} new={new_hash[:12]}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
