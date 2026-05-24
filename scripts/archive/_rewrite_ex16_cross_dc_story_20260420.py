"""Rewrite EX-16 (Cross-Datacenter Deployment Incident).

Replaces situation/task/action/result/risk_statement on
behavioral_examples.example_id='EX-16' with the user's structurally
reframed version (Discord msgs 1496028547267952713 + 1496037840377872395).

Why the rewrite: existing v1 read as "stretching beyond comfort zone"
with a redemption tail (declarative artifactory invitation). The new
story is a failure-cut focused on (a) owning a cross-team delivery the
manager couldn't get budgeted support for, (b) absorbing the rollback
without deflecting available evidence, (c) institutionalizing
counterpart bandwidth as a required line item via a senior-bench
approver policy.

The artifactory tail is intentionally dropped from this STAR (the
existing NRG-v1 had already warned this tail risks the disguised-success
trap on failure questions). The drop has link-side consequences for
PS-6, OWN-6, ADP-12 -- handled in the companion propagation script
`_propagate_ex16_rewrite_20260420.py`.

NRG-v1 + TPV-v1 (the two-guard pair on the old version) are both
replaced by NRG-v2 fitting the new story shape: pacing beats for the
4 high-signal moments + frame-coherence guidance for the 6 different
question framings the story still serves.

Idempotent: situation startswith "Manager couldn't get the cross-team
PD quota" indicates the rewrite is already applied.
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
EXAMPLE_ID = "EX-16"

IDEMPOTENT_MARKER = "Manager couldn't get the cross-team PD quota"

NEW_SITUATION = (
    "Manager couldn't get the cross-team PD quota for a search-latency "
    "optimization. She told me to take it solo. I picked it up and "
    "planned a release-by-DC rollout to three datacenters."
)

NEW_TASK = (
    "Deliver the rollout without formal bandwidth from the counterpart "
    "team. The deeper risk was structural -- nobody had a full map of "
    "what the declarative artifactory actually wrapped underneath, so "
    "any cross-DC change was a coin flip on hidden coupling."
)

NEW_ACTION = (
    "First DC went in clean. Second DC panicked out within minutes.\n\n"
    "The rollback was mine. Master was unhealthy and I needed an "
    "admin-level approver from the backend team. I posted in the shared "
    "channel -- flat description, no theory, no framing. Approval in "
    "minutes.\n\n"
    "A senior IC from that team jumped in to debug with me. We were "
    "both surprised: under the declarative artifactory was a layer of "
    "statically-compiled C++ libraries and runtime; the migration had "
    "only been partial. Neither of us had known.\n\n"
    "The senior director ran the RCA. I had evidence I could have "
    "pointed at the counterpart team. I didn't. I framed it as a "
    "context gap and a comms gap, because that was the honest read.\n\n"
    "After things settled, I drove an org-level practice in the search "
    "engine: any cross-team-boundary change requires a designated "
    "approver from the counterpart team's senior bench, not the default "
    "2-approver review."
)

NEW_RESULT = (
    "Pipeline recovered the same day. Third-DC rollout slipped. I lost "
    "about a third of a quarter to recovery and RCA, and I had to "
    "rebuild trust with a team whose system I'd just destabilized.\n\n"
    "The policy is still in effect. Every cross-team change in search "
    "engine still routes through it.\n\n"
    "The lesson: **counterpart bandwidth isn't a favor I should feel "
    "awkward asking for -- it's a line item I plan around.** When "
    "formal bandwidth doesn't come through, I keep their senior IC in "
    "the loop informally before the change, not after."
)

NEW_RISK = (
    "The structural risk isn't that this incident recurs. The hazard "
    "lives in any system where the migration is half-done and the "
    "load-bearing context -- here, that the declarative artifactory "
    "still wraps statically-compiled C++ -- only exists in human "
    "heads. Every cross-boundary change in that kind of system walks "
    "into the same minefield.\n\n"
    "The new policy converts the counterpart's deep context from "
    "something each engineer has to know to ask about into a required "
    "input on the change form. It doesn't fix the half-finished "
    "migration, but it stops the next person from blowing up the next "
    "time the hidden coupling matters.\n\n"
    "<!-- NRG-v2 --> NARRATION GUARD: Pace the four high-signal beats -- "
    "pause after \"panicked out within minutes\" before \"the rollback "
    "was mine\" (let the failure land), pause after \"neither of us had "
    "known\" before the RCA reveal (the surprise is the point), brief "
    "beat after \"I didn't\" in the deflection-choice. For pure-failure "
    "questions (failure_setback theme, ADP-5, ADP-15) end at the "
    "line-item lesson and skip the original-engineer artifactory-"
    "invitation arc -- that arc belongs to a separate calculated-risk "
    "framing (linked via PS-6, OWN-6, ADP-12 only). For \"what would "
    "you do differently\" (ADP-12) lead with the line-item lesson and "
    "treat the policy as the mechanism. For calculated-risk / bold-risk "
    "questions (PS-6, OWN-6) frame the risk as taking the cross-boundary "
    "delivery solo without budgeted support, with mixed outcome: clean "
    "DC1, broken DC2, durable structural lesson. Deliver the manager "
    "opener as agency context -- emphasis on \"I picked it up\", not "
    "\"she dumped it on me\"."
)


def main() -> int:
    if not DB.exists():
        print(f"[FAIL] db not found: {DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT id, title, situation FROM behavioral_examples "
        "WHERE example_id = ?",
        (EXAMPLE_ID,),
    ).fetchone()
    if row is None:
        print(f"[FAIL] {EXAMPLE_ID} not found", file=sys.stderr)
        conn.close()
        return 2

    row_id, title, current_situation = row

    if current_situation and current_situation.startswith(IDEMPOTENT_MARKER):
        print(f"[SKIP] {EXAMPLE_ID} already rewritten")
        conn.close()
        return 0

    conn.close()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex16_rewrite")
    shutil.copy2(DB, backup)
    print(f"[BACKUP] {backup.name}")

    conn = sqlite3.connect(str(DB))
    before = conn.execute(
        "SELECT length(situation), length(task), length(action), "
        "length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (row_id,),
    ).fetchone()

    conn.execute(
        "UPDATE behavioral_examples "
        "SET situation = ?, task = ?, action = ?, result = ?, "
        "risk_statement = ? "
        "WHERE id = ?",
        (NEW_SITUATION, NEW_TASK, NEW_ACTION, NEW_RESULT, NEW_RISK, row_id),
    )
    conn.commit()

    after = conn.execute(
        "SELECT length(situation), length(task), length(action), "
        "length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (row_id,),
    ).fetchone()
    conn.close()

    fields = ["situation", "task", "action", "result", "risk_statement"]
    print(f"[OK] {EXAMPLE_ID} (id={row_id}) '{title}' rewritten:")
    for f, b, a in zip(fields, before, after):
        sign = "+" if a >= b else ""
        print(f"  {f:<16} {b:>5} -> {a:>5} chars ({sign}{a - b})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
