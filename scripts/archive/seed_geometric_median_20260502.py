"""Seed: T-P0-690 / T-P0-704 -- Geometric Median (Weber problem) ml_coding.

Two responsibilities:

1. UPSERT the Geometric Median problem row (originally INSERTed under
   T-P0-690; migrated to the golden-style notes + renamed title under
   T-P0-704). Notes content lives in
   ``docs/drafts/geometric_median_golden_v1.md`` (per
   ``docs/methodology/ml_impl_note_rewrite_spec.md``); this script reads
   that file and writes it to ``problems.notes`` with a sentinel prepended.

2. UPSERT a one-line cross-link block in ``problems.id=262`` (Best Meeting
   Point) pointing back to this problem (the L2 cousin of LC 296's L1
   per-axis median).

Title migration (T-P0-704):
- Old: ``Geometric Median (Weber 问题, L2 距离和最小)``
- New: ``Geometric Median (Weiszfeld + Vardi-Zhang variant)``
- The lookup tries the new title first, falls back to the old title for
  one-time migration, and renames in place if found under the old title.

Length cap (per spec): payload (sentinel + draft body) must be <= 6,800
chars. Current draft is well under that.

Idempotency:
- Sentinel ``<!-- GEOMETRIC_MEDIAN_GOLDEN_V1_20260502 -->`` is the first
  line of the new notes payload. Re-runs detect it; if existing notes are
  byte-equal to the canonical payload AND title matches, [SKIP] with 0
  writes. Otherwise UPDATE in place.
- Sentinel ``<!-- GEOMETRIC_MEDIAN_CROSSLINK_20260502 -->`` guards the
  cross-link block in problems.id=262.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
DRAFT_PATH = REPO_ROOT / "docs" / "drafts" / "geometric_median_golden_v1.md"

TITLE = "Geometric Median (Weiszfeld + Vardi-Zhang variant)"
OLD_TITLE = "Geometric Median (Weber 问题, L2 距离和最小)"
SOURCE = "ml-coding-handwritten-2026-05-02"
DIFFICULTY = "medium"
PATTERN = "ML Implementation"
CATEGORY = "ml_coding"
TAGS = '["ml-fundamentals", "geometric-median", "weiszfeld", "robust-statistics", "implementation"]'
COMPANY_TAGS = '["Meta", "Uber", "DoorDash", "Pinterest"]'
PRIORITY = 1

SENTINEL = "<!-- GEOMETRIC_MEDIAN_GOLDEN_V1_20260502 -->"
CROSSLINK_SENTINEL = "<!-- GEOMETRIC_MEDIAN_CROSSLINK_20260502 -->"
BEST_MEETING_POINT_ID = 262
LENGTH_CAP = 6800

DESCRIPTION = (
    "**Geometric Median (Weber 问题)**: 给定 N 个二维点 "
    "$\\{x_1, \\dots, x_N\\}$, 找点 $x^*$ 使 $\\sum_i \\|x^* - x_i\\|_2$ "
    "最小 (L2 距离和). 这是 Fermat-Weber location problem 的经典形式, "
    "也是 L1 距离 (Manhattan, db://262 Best Meeting Point) 在 L2 度量下的"
    "对应版本. 关键区别: L1 距离按维度可分解 -> 每轴取中位数即可; "
    "L2 距离**不可分解**, 没有闭式解, 必须迭代求解.\n\n"
    "经典算法: **Weiszfeld 迭代** -- 把目标函数的一阶最优条件 "
    "$\\nabla f(x) = \\sum_i (x - x_i)/\\|x - x_i\\| = 0$ 改写成不动点形式 "
    "$x = (\\sum_i x_i / d_i) / (\\sum_i 1 / d_i)$. 退化情形 (迭代点恰好"
    "落在样本点上, 分母为零) 由 Vardi-Zhang variant 给出标准修正.\n\n"
    "归类理由: 几何中位数严格属于 robust statistics / numerical "
    "optimization, 但 ml_coding 收录的标准是更宽的: 我们包含 (a) ML 算法"
    "实现 (KMeans/KNN/LR/LogReg) 或 (b) 与 ML/统计有直接联系的数值优化"
    "问题. 几何中位数符合 (b): Weiszfeld 是凸 L2 距离和目标的 IRLS / "
    "梯度下降变体, M-estimator / 鲁棒均值在 robust regression 与 robust "
    "clustering 初始化里直接用到; k=1 K-Means 用 L2^2 cost 给出 centroid, "
    "本题给的是 k=1 + L2 (非平方) 时的多维 'median' -- 一个干净的桥梁."
)


def build_payload() -> str:
    """Read the golden draft and prepend the sentinel as the first line."""
    body = DRAFT_PATH.read_text(encoding="utf-8")
    return f"{SENTINEL}\n{body}"


CROSSLINK_TEMPLATE = (
    "\n\n" + CROSSLINK_SENTINEL + "\n"
    "### L2 版本 (Geometric Median / Weber 问题)\n\n"
    "本题 (LC 296) 用 L1 (Manhattan) 距离, 按轴分解 -> 各轴中位数.\n"
    "把距离改成 L2 (Euclidean) 不平方就成了 Fermat-Weber location problem,\n"
    "目标 $\\sum \\|x - x_i\\|_2$ **不可分解**, 无闭式解, 必须用\n"
    "**Weiszfeld 迭代** + Vardi-Zhang variant 退化修正.\n\n"
    "完整笔记: [Geometric Median (Weiszfeld + Vardi-Zhang variant)](db://{new_id})\n"
)


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1
    if not DRAFT_PATH.exists():
        print(f"[FAIL] Draft not found: {DRAFT_PATH}")
        return 1

    notes_payload = build_payload()
    if len(notes_payload) > LENGTH_CAP:
        print(
            f"[FAIL] Notes payload {len(notes_payload)} chars exceeds cap "
            f"{LENGTH_CAP}. Trim the draft."
        )
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        # ---- Step 1: UPSERT the Geometric Median row ----
        # Try the new title first; fall back to the old title for one-time
        # migration (T-P0-704 rename: drop "1999", use "variant").
        row = conn.execute(
            "SELECT id, title, description, notes "
            "FROM problems WHERE title = ? AND source = ?",
            (TITLE, SOURCE),
        ).fetchone()
        if row is None:
            row = conn.execute(
                "SELECT id, title, description, notes "
                "FROM problems WHERE title = ? AND source = ?",
                (OLD_TITLE, SOURCE),
            ).fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        if row is None:
            cur = conn.execute(
                "INSERT INTO problems "
                "(title, description, notes, difficulty, pattern, "
                "category, tags, source, company_tags, priority, "
                "is_completed, comfort_level, description_source, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "0, 0, 'manual', ?)",
                (
                    TITLE,
                    DESCRIPTION,
                    notes_payload,
                    DIFFICULTY,
                    PATTERN,
                    CATEGORY,
                    TAGS,
                    SOURCE,
                    COMPANY_TAGS,
                    PRIORITY,
                    now,
                ),
            )
            new_id = int(cur.lastrowid or 0)
            conn.commit()
            print(
                f"[INSERT] '{TITLE}' id={new_id} "
                f"description={len(DESCRIPTION)} notes={len(notes_payload)} chars"
            )
            inserted_new = True
        else:
            pid, old_title, old_desc, old_notes = row
            old_title = old_title or ""
            old_desc = old_desc or ""
            old_notes = old_notes or ""
            new_id = int(pid)
            if (
                old_title == TITLE
                and old_desc == DESCRIPTION
                and old_notes == notes_payload
            ):
                print(
                    f"[SKIP] id={pid} '{TITLE}' title+description+notes "
                    f"byte-equal (notes={len(old_notes)})"
                )
                inserted_new = False
            else:
                conn.execute(
                    "UPDATE problems "
                    "SET title = ?, description = ?, notes = ?, "
                    "    difficulty = ?, pattern = ?, category = ?, "
                    "    tags = ?, company_tags = ?, priority = ? "
                    "WHERE id = ?",
                    (
                        TITLE,
                        DESCRIPTION,
                        notes_payload,
                        DIFFICULTY,
                        PATTERN,
                        CATEGORY,
                        TAGS,
                        COMPANY_TAGS,
                        PRIORITY,
                        pid,
                    ),
                )
                conn.commit()

                check = conn.execute(
                    "SELECT title, notes FROM problems WHERE id = ?", (pid,)
                ).fetchone()
                check_title, check_notes = check
                if check_title != TITLE or check_notes != notes_payload:
                    print("[FAIL] Title or notes do not match payload after write")
                    return 1
                if not check_notes.startswith(SENTINEL):
                    print("[FAIL] Sentinel not at start of notes after write")
                    return 1

                title_action = "RENAME+" if old_title != TITLE else ""
                print(
                    f"[{title_action}UPDATE] id={pid} '{old_title}' -> '{TITLE}', "
                    f"notes {len(old_notes)} -> {len(notes_payload)} chars"
                )
                inserted_new = False

        # ---- Step 2: UPSERT cross-link block in problems.id=262 ----
        bmp_row = conn.execute(
            "SELECT id, notes FROM problems WHERE id = ?",
            (BEST_MEETING_POINT_ID,),
        ).fetchone()
        if bmp_row is None:
            print(
                f"[WARN] problems.id={BEST_MEETING_POINT_ID} "
                "(Best Meeting Point) not found -- skipping cross-link"
            )
            return 0

        bmp_id, bmp_notes = bmp_row
        bmp_notes = bmp_notes or ""
        crosslink = CROSSLINK_TEMPLATE.format(new_id=new_id)

        if CROSSLINK_SENTINEL in bmp_notes:
            existing_idx = bmp_notes.find(CROSSLINK_SENTINEL)
            existing_block = bmp_notes[existing_idx - 2:]  # include "\n\n"
            if existing_block.rstrip() == crosslink.rstrip():
                print(
                    f"[SKIP] id={bmp_id} (Best Meeting Point) already has "
                    f"geometric-median cross-link (-> id={new_id})"
                )
            else:
                rebuilt = bmp_notes[: existing_idx - 2].rstrip() + crosslink
                conn.execute(
                    "UPDATE problems SET notes = ? WHERE id = ?",
                    (rebuilt, bmp_id),
                )
                conn.commit()
                print(
                    f"[UPDATE] id={bmp_id} (Best Meeting Point) "
                    f"cross-link rewritten -> id={new_id}, "
                    f"notes {len(bmp_notes)} -> {len(rebuilt)} chars"
                )
        else:
            rebuilt = bmp_notes.rstrip() + crosslink
            conn.execute(
                "UPDATE problems SET notes = ? WHERE id = ?",
                (rebuilt, bmp_id),
            )
            conn.commit()
            print(
                f"[APPEND] id={bmp_id} (Best Meeting Point) "
                f"+ geometric-median cross-link (-> id={new_id}), "
                f"notes {len(bmp_notes)} -> {len(rebuilt)} chars "
                f"(inserted_new_row={inserted_new})"
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
