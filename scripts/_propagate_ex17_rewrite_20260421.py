"""Propagate the EX-17 rewrite to all dependent DB fields.

Companion to `_rewrite_ex17_senior_ic_feedback_20260421.py` which only
updated STAR + risk_statement.

Updates:
- title: "Building Credibility" -> "Reliance vs. Trust" (kill-line as
  title, parallels EX-15/EX-16 pattern; old title contradicts new
  kill-line lesson "I had conflated being relied on with being
  trusted")
- cn_elevator_pitch: rewritten via canonical seed
  `seed_master_pitches.py` (edited inline as part of this change);
  this script also writes the same value directly so DB stays
  consistent without requiring re-run of canonical seed
- principle_tags: drop "communication" (not the story's core); add
  "have_backbone" (decline manager protection), "frame_ownership"
  (the kill insight -- it's about owning the framing not just the
  artifact), "earn_trust" (the rebuild mechanism), "restraint"
  (chose not to take manager's offered cover)
- 7 relevance_notes on linked questions: each rewritten to match the
  new story angle. Critical case: COM-5 ("feedback you disagreed
  with") -- old note said "responded by proactively reaching out
  with context and improvement plan" but new story explicitly says
  "My explanation was technically accurate and completely beside
  the point. He was right to refuse." Per option A from Discord
  msg 1496044325115527248, the new relevance_note pivots: "initially
  wanted to disagree with technical context, then matured to seeing
  the explanation was beside the point". Other 6 notes refresh to
  the new gate-keeping insight angle.

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
EXAMPLE_ID = "EX-17"

NEW_TITLE = "Difficult Feedback from Senior IC --- Reliance vs. Trust"

NEW_CN_PITCH = (
    "Manager 让我 inherit researcher 的 remote branch 组 surface-level review，"
    "我 raise 了一次 deep-context 担忧后 accept 了\"researcher owns 那层\"的 framing；"
    "CI 后 senior IC 拒继续 review——不是为 CI failure、是为我 literally executed "
    "manager instruction without holding own gate。拒了 manager 提出的揭 protection，"
    "承认自己的 explanation technically accurate but completely beside the point，"
    "靠 consistency 重建 trust"
    " | KEY FACTS: senior IC 拒 review (不是 CI 而是 gate-keeping)"
    " | 拒 manager protection 是全 story 最强 character signal"
    " | 2 个月后 senior IC 恢复 normal review"
    " | engineer-researcher ownership boundary 入 team policy"
)

NEW_PRINCIPLE_TAGS = [
    "adaptability",
    "ownership",
    "failure",
    "humility",
    "have_backbone",
    "frame_ownership",
    "earn_trust",
    "restraint",
]

# question_id (string) -> new relevance_note
RELEVANCE_NOTES: dict[str, str] = {
    "ADP-19": (
        "Most challenging feedback: a senior IC refused to keep "
        "reviewing my code -- not because CI broke, but because I'd "
        "executed my manager's instruction literally without holding "
        "my own gate. The hardest part was admitting his refusal to "
        "hear my explanation was the right call -- my explanation "
        "was technically accurate and completely beside the point."
    ),
    "COM-5": (
        "I initially wanted to disagree with the feedback by walking "
        "the senior IC through the technical context (researcher's "
        "late naming changes broke a verified PR). When he refused "
        "to hear it, I realized my explanation was technically "
        "accurate but completely beside the point -- the actual "
        "failure was accepting a framing that let me author a PR "
        "without owning it. The maturation was from wanting to "
        "disagree to recognizing he was right to refuse."
    ),
    "ADP-16": (
        "Sought direct feedback from a senior IC who had refused to "
        "keep reviewing my code, then sat with the answer rather "
        "than arguing. Recovered through consistency -- manager-"
        "mediated review, strict checklist adherence, fast on-call "
        "responsiveness -- not through grand gestures or "
        "explanation."
    ),
    "ADP-18": (
        "Recent mistake: accepted a manager-given framing that let "
        "me author a PR without owning the deep context. Lesson: I "
        "had conflated being relied on with being trusted -- the "
        "team needs your hands under pressure (reliance), but the "
        "team trusts you only when they believe you'll hold the "
        "line under that pressure, including saying no."
    ),
    "OWN-3": (
        "Handled difficult feedback by absorbing the gate-keeping "
        "insight rather than defending the technically-accurate "
        "explanation. Declined my manager's offer to explain on my "
        "behalf -- accepting her protection would have extended "
        "the same shortcut that caused the problem."
    ),
    "ADP-17": (
        "Senior IC's feedback revealed a defaults-class growth area "
        "-- I'd been optimizing for being relied on (hands under "
        "pressure) at the cost of being trusted (holding the line "
        "under pressure, including saying no). At senior level the "
        "more capable you are, the more often you'll be asked to "
        "bypass review, and the more damage each yes does."
    ),
    "OWN-4": (
        "Took responsibility for a quality gate-keeping failure: "
        "accepted a manager-given framing that let me author a PR "
        "without owning the deep context, then declined her offer "
        "to explain on my behalf because that protection would "
        "have extended the same shortcut. Recovered through a "
        "manager-mediated review process, strict checklist "
        "adherence, and time -- no grand gestures, just "
        "consistency."
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
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex17_propagate")
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
