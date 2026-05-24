"""Propagate the EX-16 rewrite to all dependent DB fields.

Companion to `_rewrite_ex16_cross_dc_story_20260420.py` which only
updated the STAR fields.

Updates:
- title: from "Stretching Beyond Comfort Zone" to
  "Counterpart Bandwidth as a Line Item" (matches EX-15's
  kill-line-as-title pattern: "Reframing Conflict into a Governance
  Pattern")
- cn_elevator_pitch: rewritten via canonical seed
  `seed_master_pitches.py` (edited inline as part of this change);
  this script also writes the same value directly so the DB stays
  consistent without requiring a re-run of the canonical seed
- principle_tags: drop "execution" (new story isn't about execution
  speed); add "counterpart_bandwidth", "org_policy_creation",
  "restraint" (the strongest character signal: choosing not to
  deflect with available evidence)
- 6 relevance_notes on linked questions: each rewritten to match
  both the question's framing AND the new story angle. Critical
  case: ADP-12's old note explicitly referenced the now-dropped
  artifactory tail -- new note pivots to the line-item lesson as
  the "what would you do differently" angle.

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
EXAMPLE_ID = "EX-16"

NEW_TITLE = (
    "Cross-Datacenter Deployment Incident --- Counterpart Bandwidth as a Line Item"
)

NEW_CN_PITCH = (
    "Manager 没拿到 cross-team PD quota 让我独自扛 release-by-DC rollout；"
    "DC2 几分钟内 panic out，rollback 是我的，没拿手上的证据指对方而是 "
    "framing 成 context gap，事后推动了 search engine 层的 cross-team "
    "senior-bench approver policy"
    " | KEY FACTS: DC2 几分钟 panic out"
    " | 三分之一 quarter 修复 + RCA 代价"
    " | senior IC joint debug 揭出 partial artifactory migration"
    " | org-level approver policy 至今 in effect"
)

NEW_PRINCIPLE_TAGS = [
    "adaptability",
    "ownership",
    "failure",
    "humility",
    "cross_boundary_failure",
    "counterpart_bandwidth",
    "org_policy_creation",
    "restraint",
]

# question_id (string) -> new relevance_note. Each frames the story to
# match what the question is asking, drawing on the new STAR.
RELEVANCE_NOTES: dict[str, str] = {
    "PS-6": (
        "Calculated risk: took on the cross-team-boundary delivery solo "
        "when formal PD quota wasn't approved. The delivery part went "
        "south at DC2; the risk-handling part -- owning the rollback "
        "and not deflecting with available evidence -- held up."
    ),
    "OWN-6": (
        "Bold risk: took the cross-DC rollout solo when manager couldn't "
        "get cross-team PD quota. Outcome was mixed -- clean DC1, broken "
        "DC2, durable structural lesson about counterpart bandwidth as "
        "a planned line item."
    ),
    "ADP-12": (
        "Project didn't go as planned -- the rollout broke a system I "
        "shared with a counterpart team. What I'd do differently: treat "
        "counterpart bandwidth as a planned line item, not a favor; keep "
        "their senior IC in the loop informally before the change, not "
        "after."
    ),
    "ADP-1": (
        "Quickly learned the search engine's cross-DC deployment "
        "patterns under incident pressure -- including the partial "
        "declarative artifactory migration that wrapped statically-"
        "compiled C++ underneath."
    ),
    "ADP-5": (
        "Made a mistake because I trusted the dashboard / artifactory "
        "abstractions without verifying what they actually wrapped. "
        "Owned the rollback, framed the RCA honestly, and converted the "
        "lesson into a counterpart-approver policy."
    ),
    "ADP-15": (
        "Biggest lesson: counterpart bandwidth isn't a favor I should "
        "feel awkward asking for -- it's a line item I plan around. "
        "When formal bandwidth doesn't come through, keep their senior "
        "IC informally in the loop before the change, not after."
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
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex16_propagate")
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
