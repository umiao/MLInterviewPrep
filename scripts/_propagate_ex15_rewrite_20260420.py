"""Propagate the EX-15 (id=19) rewrite to all dependent DB fields.

Companion to `_rewrite_ex15_deprecation_story_20260420.py` which only updated
the STAR fields. This script handles the propagation surface that an audit
surfaced after the fact: title, cn_elevator_pitch, principle_tags, and the
relevance_notes on all 10 question_example_links pointing at id=19.

Why each field matters (what user sees on which surface):
- title: appears on the failure_setback theme card, in story-arcs view,
  in every question's "linked stories" list, in the drawer header.
- cn_elevator_pitch: appears as the card summary + the KEY FACTS pills on
  the failure_setback theme grid (parsed by parsePitch in the React card).
- principle_tags: shown in the card / drawer / story-arcs as live tags.
  Old tags 'innovation' and 'process_improvement_from_incident' described
  the old "process improvement" framing and don't fit the structural-reframe
  story; we drop them and add 'structural_reframe',
  'shared_infrastructure_governance', 'credibility_first'.
- relevance_notes: shown when a question lists its linked stories. All 10
  of EX-15's existing notes describe the old narrative ("VP-level meetings",
  "despite following correct process", "safety knobs", "process improvements
  to prevent recurrence", etc.) -- each is rewritten to the new angle that
  matches the question's framing.

Idempotent via a per-row marker column: we check whether the title already
matches NEW_TITLE; if so, all writes skip.

Source of truth note: the cn_elevator_pitch canonical seed is
`scripts/seed_master_pitches.py`, which has been edited inline as part of
this same change so re-running it produces the new pitch. The title and
principle_tags don't have an upstream seed -- this script becomes their
source of truth. Per CLAUDE.md invariant 3: every DB content row needs a
git-tracked idempotent seed script. The 10 relevance_notes likewise have
no upstream seed; this script becomes their source.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
ROW_ID = 19
EXAMPLE_ID = "EX-15"

NEW_TITLE = (
    "Model Deprecation Incident --- Reframing Conflict into a Governance Pattern"
)

NEW_CN_PITCH = (
    "我自己的 traffic dashboard 盲区漏掉了 hardcoded 调用，下线 legacy model 后 "
    "3-4 个 Query Understanding pipeline 被 block；不争流程对错先吃 rollback，"
    "一周内全部 unblock 换到 credibility，再把 \"谁必须迁移\" 这道单选题 reframe 为 "
    "含 ownership transfer 的双选题，推到 senior leadership 划清 capacity ownership "
    "边界"
    " | KEY FACTS: 1 周 unblock 3-4 pipelines"
    " | dashboard 盲区 (URL params 不记 hardcoded)"
    " | 引入 ownership transfer 第三选项"
    " | senior leadership boundary 决议"
)

NEW_PRINCIPLE_TAGS = [
    "adaptability",
    "ownership",
    "failure",
    "humility",
    "structural_reframe",
    "shared_infrastructure_governance",
    "credibility_first",
]

# question_id (string) -> new relevance_note. Each note is rewritten to match
# both the question's framing AND the new story angle. We key by question_id
# (not numeric id) so the script survives renumbering.
RELEVANCE_NOTES: dict[str, str] = {
    "OWN-1": (
        "Owned the failure -- my traffic dashboard tracked URL-param calls "
        "but missed hardcoded calls in the search engine. Absorbed the "
        "rollback before pushing for any structural change."
    ),
    "OWN-7": (
        "Resilience: didn't argue process under pressure -- absorbed the "
        "rollback, used the recovery week to earn standing for a deeper "
        "structural change at the leadership level."
    ),
    "OWN-8": (
        "Moving fast on a long-deferred ticket, I trusted the dashboard "
        "without checking what it didn't measure -- it tracked URL-param "
        "calls but missed hardcoded ones in the search engine."
    ),
    "COM-3": (
        "Had to tell 3-4 Query Understanding teams their pipelines were "
        "blocked by my deprecation. Led with rollback execution and a "
        "concrete recovery timeline before introducing the harder "
        "ownership-boundary conversation."
    ),
    "INN-5": (
        "Reframed deprecation from a one-way notice into a two-way "
        "negotiation -- introduced ownership-transfer as a third path, "
        "escalated to senior leadership for a capacity-budget boundary "
        "decision that became a reusable governance pattern."
    ),
    "ADP-2": (
        "Adjusted approach mid-incident: stopped defending the process, "
        "absorbed the rollback, then reframed the underlying capacity-vs-"
        "stability conflict at the leadership level."
    ),
    "ADP-5": (
        "Owned a deprecation that broke 3-4 pipelines because the traffic "
        "dashboard missed hardcoded calls. Absorbed rollback first, then "
        "drove a structural fix to prevent recurrence."
    ),
    "ADP-11": (
        "A 'clean' deprecation broke production within minutes. Recovered "
        "all pipelines within a week, then converted the underlying "
        "zero-sum capacity conflict into a sustainable governance pattern."
    ),
    "ADP-13": (
        "Handled the failure by absorbing the rollback before arguing "
        "process. Built sustainable resilience by reframing the capacity-"
        "vs-stability conflict at the org level rather than patching it "
        "with comms mechanisms."
    ),
    "ADP-14": (
        "Roadblock was structural, not technical -- finite indexing "
        "capacity vs. perpetual stability expectations. Pushed through by "
        "introducing ownership-transfer as a third path acceptable to "
        "leadership."
    ),
}


def main() -> int:
    if not DB.exists():
        print(f"[FAIL] db not found: {DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT example_id, title FROM behavioral_examples WHERE id = ?",
        (ROW_ID,),
    ).fetchone()
    if row is None:
        print(f"[FAIL] row id={ROW_ID} not found", file=sys.stderr)
        conn.close()
        return 2

    ex_id, current_title = row
    if ex_id != EXAMPLE_ID:
        print(
            f"[FAIL] row id={ROW_ID} is example_id={ex_id}, expected {EXAMPLE_ID}",
            file=sys.stderr,
        )
        conn.close()
        return 3

    if current_title == NEW_TITLE:
        print(f"[SKIP] {EXAMPLE_ID} title already matches NEW_TITLE")
        conn.close()
        return 0

    conn.close()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex15_propagate")
    shutil.copy2(DB, backup)
    print(f"[BACKUP] {backup.name}")

    conn = sqlite3.connect(str(DB))

    # 1) title + cn_elevator_pitch + principle_tags
    conn.execute(
        "UPDATE behavioral_examples "
        "SET title = ?, cn_elevator_pitch = ?, principle_tags = ? "
        "WHERE id = ?",
        (NEW_TITLE, NEW_CN_PITCH, json.dumps(NEW_PRINCIPLE_TAGS), ROW_ID),
    )
    print(f"[OK] {EXAMPLE_ID} title/pitch/tags updated")

    # 2) Each relevance_note (10 rows). Lookup by question_id string.
    notes_updated = 0
    notes_missing: list[str] = []
    for qid, note in RELEVANCE_NOTES.items():
        q_row = conn.execute(
            "SELECT id FROM behavioral_questions WHERE question_id = ?",
            (qid,),
        ).fetchone()
        if q_row is None:
            notes_missing.append(qid)
            continue
        q_pk = q_row[0]
        cur = conn.execute(
            "UPDATE question_example_links "
            "SET relevance_note = ? "
            "WHERE question_id = ? AND example_id = ?",
            (note, q_pk, ROW_ID),
        )
        if cur.rowcount == 1:
            notes_updated += 1
        elif cur.rowcount == 0:
            notes_missing.append(f"{qid} (no link row)")
        else:
            notes_missing.append(f"{qid} (multi-row update: {cur.rowcount})")

    conn.commit()
    conn.close()

    print(f"[OK] {notes_updated}/{len(RELEVANCE_NOTES)} relevance_notes updated")
    if notes_missing:
        print(f"[WARN] missing/anomalous: {notes_missing}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
