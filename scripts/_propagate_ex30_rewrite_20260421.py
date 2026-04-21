"""Propagate the EX-30 rewrite to all dependent DB fields.

Companion to `_rewrite_ex30_hash_misdesign_20260421.py` which only
updated STAR + risk_statement.

Updates:
- title: "Hash Capability Misdesign - Expert Frame Blind Spot" ->
  "Hash Capability Misdesign --- Domain Depth Is Not Design Authority"
  (kill-line as title, parallels EX-15/16/17 system pattern; kept
  "Hash Capability Misdesign" as the entity prefix)
- cn_elevator_pitch: rewritten via canonical seed
  `seed_master_pitches.py` (edited inline as part of this change);
  this script also writes the same value directly so DB stays
  consistent without requiring re-run of canonical seed
- principle_tags: keep all existing 6, add "structural_recognition"
  (the orphan-capability-as-red-flag insight) and "anti_sunk_cost"
  (the "It was rejected. And this is where I stopped." beat)
- 6 relevance_notes on linked questions (OWN-1, OWN-8, ADP-5, ADP-18,
  EXE-2, ADP-15): all already aligned with the story angle (no
  frame-coherence break per pre-draft audit), only refreshed to
  reflect the new kill-line lesson "domain depth is not design
  authority" + new "rescue stopped" beat. EX-30 not in
  bq_story_arcs.json (verified 0 grep hits) — no JSON edit needed.

Idempotent: title equals NEW_TITLE check.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
EXAMPLE_ID = "EX-30"

NEW_TITLE = (
    "Hash Capability Misdesign --- Domain Depth Is Not Design Authority"
)

NEW_CN_PITCH = (
    "高速 PM 合作期以 hash-expert 身份上线数学优雅的 facet hash，下游 2-3 个 "
    "DS 团队被 block 几周 launch analysis；提 cross-four-team rescue 被拒后停了，"
    "认出 rescue 是 self-centered。最终采纳 indexing team 已有的 explicit aspect "
    "cache + stable ID assignment。Kill-line: domain depth is not design "
    "authority——authority belongs to whoever consumes the output"
    " | KEY FACTS: 2-3 个下游 DS team 几周 launch analysis 损失"
    " | cross-four-team multi-quarter rescue 被拒"
    " | \"It was rejected. And this is where I stopped.\""
    " | 采纳 indexing team 现成 prior art"
    " | structural lesson: orphan capability 会 leak 成 experiment-level confounding"
)

NEW_PRINCIPLE_TAGS = [
    "failure",
    "learning",
    "expert_blind_spot",
    "cross_functional",
    "humility",
    "consulted_prior_art",
    "structural_recognition",
    "anti_sunk_cost",
]

# question_id (string) -> new relevance_note. All 6 existing notes were
# already aligned with the story angle per the pre-draft audit; this
# refresh updates each to reference the new kill-line lesson and the
# new "rescue stopped" beat.
RELEVANCE_NOTES: dict[str, str] = {
    "OWN-1": (
        "Clean ownership-of-failure narrative: I owned the hash design, "
        "the failure was attributable to my framing (saw hash as math "
        "object, not as analytical artifact in DS's decision path), and "
        "I narrate the cost to 2-3 downstream DS teams without "
        "deflecting. Critical beat: when my own rescue proposal was "
        "rejected, I stopped instead of pushing harder."
    ),
    "OWN-8": (
        "Moving-fast-and-made-a-mistake fit: the smooth PM collaboration "
        "loop removed friction, which is precisely what let me ship a "
        "design without consumer audit. The lesson is mental-model: "
        "domain depth is not design authority -- the authority belongs "
        "to whoever consumes the output."
    ),
    "ADP-5": (
        "Three-stage handling-a-mistake arc: (1) escalation landed and "
        "I owned it; (2) I proposed a wrong rescue (cross-four-team "
        "multi-quarter infra change to make my elegant hash survive); "
        "(3) when the rescue was rejected I stopped and adopted "
        "indexing team's prior art -- explicit aspect cache + stable "
        "ID. The middle stage is the honest part: the wrong rescue "
        "shows the framing error in motion."
    ),
    "ADP-18": (
        "Recent-mistake-and-lesson framing: the lesson is a mental-"
        "model shift, not a tactical fix. \"Domain depth is not design "
        "authority. The authority belongs to whoever consumes the "
        "output.\" Transferable to any cross-team capability design."
    ),
    "EXE-2": (
        "Setback-in-timelines fit: 2-3 downstream DS teams' launch "
        "analysis blocked for weeks by my design. Mid-flight pivot from "
        "\"more engineering to rescue elegant design\" to \"adopt "
        "indexing team's existing pattern\" -- the time recovery came "
        "from stopping the rescue, not from accelerating it."
    ),
    "ADP-15": (
        "The cleanest unambiguous failure in my story pool: no success-"
        "tail, clear mental-model lesson (domain depth != design "
        "authority), and a structural follow-on signal (orphan "
        "capability leaks into experiment-level confounding in adjacent "
        "work). Use this story for biggest-lesson questions where "
        "interviewer wants a clean failure with abstract takeaway."
    ),
}


def main() -> int:
    if not DB.exists():
        print(f"[FAIL] db not found: {DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT id, title FROM behavioral_examples WHERE example_id = ?",
        (EXAMPLE_ID,),
    ).fetchone()
    if row is None:
        print(f"[FAIL] {EXAMPLE_ID} not found", file=sys.stderr)
        conn.close()
        return 2

    row_id, current_title = row
    if current_title == NEW_TITLE:
        print(f"[SKIP] {EXAMPLE_ID} title already matches NEW_TITLE")
        conn.close()
        return 0

    conn.close()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex30_propagate")
    shutil.copy2(DB, backup)
    print(f"[BACKUP] {backup.name}")

    conn = sqlite3.connect(str(DB))

    conn.execute(
        "UPDATE behavioral_examples "
        "SET title = ?, cn_elevator_pitch = ?, principle_tags = ? "
        "WHERE id = ?",
        (NEW_TITLE, NEW_CN_PITCH, json.dumps(NEW_PRINCIPLE_TAGS), row_id),
    )
    print(f"[OK] {EXAMPLE_ID} title/pitch/tags updated")

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
            (note, q_pk, row_id),
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
