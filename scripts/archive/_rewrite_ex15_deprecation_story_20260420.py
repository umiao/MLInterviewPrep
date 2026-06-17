"""Rewrite EX-15 (behavioral_examples.id=19) "Model Deprecation Incident".

Replaces situation/task/action/result/risk_statement with a polished English
version of the user's Discord rewrite (msg 1496015839172759552 +
1496017015989735536 confirm).

Why the rewrite: original story carried two interview red flags --
(1) defensive "I followed proper process correctly" opener that leaned on
manager backing for VP meetings (deflects ownership), and (2) blamed
"informal stakeholders had undocumented tests" (deflects to victims).
The new version owns the dashboard blind spot (URL-param tracking missed
hardcoded calls), reframes as a structural capacity-vs-stability conflict
rather than a comms failure, and introduces ownership-transfer as a third
path negotiated at senior leadership.

NRG-v1 narration guard is replaced with NRG-v2 fitting the new story shape:
the new failure mode in narration is jumping to the clever ownership-transfer
framework before establishing the failure ack and the rollback execution.

Idempotent via marker: situation field starting with "On-call, I picked up
a long-deferred ticket" indicates the rewrite is already applied.

Project convention (CLAUDE.md): every DB content row needs a git-tracked
idempotent seed script. This is the canonical source for EX-15 content.
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
ROW_ID = 19
EXAMPLE_ID = "EX-15"

IDEMPOTENT_MARKER = "On-call, I picked up a long-deferred ticket"

NEW_SITUATION = (
    "On-call, I picked up a long-deferred ticket: deprecate a set of legacy "
    "models to reclaim indexing capacity. I aligned with my manager and "
    "teammates on the plan, scanned the traffic dashboard to confirm zero "
    "client calls, then executed."
)

NEW_TASK = (
    "Within minutes of the deprecation, incident tickets flooded in. The "
    "dashboard only tracked URL-parameter calls and missed calls hardcoded "
    "directly into the search engine. Three to four Query Understanding "
    "pipelines were blocked. The immediate need was to unblock them, but "
    "the deeper problem was structural: indexing capacity is finite, yet "
    "consumer teams expect models to stay available forever. Without "
    "resolving that conflict, the same incident would recur."
)

NEW_ACTION = (
    "Early call: don't argue about who followed the right process -- just "
    "absorb the rollback. Within a week, every affected pipeline was "
    "restored. That week of credibility bought me the standing to push a "
    "deeper change.\n\n"
    "Then I reframed the problem. The original frame was \"who must comply "
    "with deprecation?\" I introduced a third option: **ownership "
    "transfer**. If a team's calibration had diverged enough that they "
    "truly needed a legacy model long-term, they could fork the code, own "
    "it, and stop consuming our indexing capacity.\n\n"
    "I escalated the framework to senior leadership for a boundary "
    "decision. The conclusion: the search engine team owns the capacity "
    "budget. Consumer teams have two choices -- migrate to the new model, "
    "or take ownership and maintain it themselves."
)

NEW_RESULT = (
    "Leadership aligned on the boundary. After weighing the options, most "
    "consumer usage migrated to the new model; for the handful of legacy "
    "models that were genuinely irreplaceable, consumer teams accepted "
    "ownership and maintained them independently. Short-term: every "
    "blocked team was back online within a week. Long-term: a recurring "
    "zero-sum conflict became a sustainable governance pattern.\n\n"
    "The deepest lesson for me: **deprecation is a negotiation, not an "
    "announcement.** Sending a notice doesn't close the loop. The "
    "compromise path has to be designed in at the proposal stage. I've "
    "carried that principle into every shared-infrastructure change since."
)

NEW_RISK = (
    "Short-term, three to four teams' pipelines stay blocked and "
    "cross-team trust erodes. The real risk is long-term: if I had only "
    "done the rollback without the structural fix, the next time indexing "
    "capacity ran out, the same incident would recur -- at larger scale. "
    "The deeper hazard is permanent ambiguity in ownership boundaries: "
    "the model owner team would slowly drift into being the consumer "
    "teams' implicit maintenance backstop, and our roadmap would be eaten "
    "by legacy load. This isn't a one-incident problem -- it's whether "
    "the org can sustainably operate shared infrastructure.\n\n"
    "<!-- NRG-v2 --> NARRATION GUARD: This is a 'failure -> structural "
    "reframe' story. The narration risk is jumping straight to the "
    "ownership-transfer framework (the clever part) and underweighting "
    "the failure ack. Lead with the dashboard blind spot -- it tracked "
    "URL-param calls but not hardcoded ones in the search engine -- and "
    "the week of rollback execution. Only introduce the ownership-transfer "
    "reframe AFTER establishing both the failure ownership and the "
    "structural-conflict observation. If the interviewer cuts you off "
    "after the rollback, the lesson \"deprecation is a negotiation, not "
    "an announcement\" is the standalone close."
)


def main() -> int:
    if not DB.exists():
        print(f"[FAIL] db not found: {DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT example_id, title, situation FROM behavioral_examples WHERE id = ?",
        (ROW_ID,),
    ).fetchone()
    if row is None:
        print(f"[FAIL] row id={ROW_ID} not found", file=sys.stderr)
        conn.close()
        return 2

    ex_id, title, current_situation = row
    if ex_id != EXAMPLE_ID:
        print(
            f"[FAIL] row id={ROW_ID} is example_id={ex_id}, expected {EXAMPLE_ID}",
            file=sys.stderr,
        )
        conn.close()
        return 3

    if current_situation and current_situation.startswith(IDEMPOTENT_MARKER):
        print(f"[SKIP] {EXAMPLE_ID} already rewritten (situation starts with marker)")
        conn.close()
        return 0

    conn.close()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex15_rewrite")
    shutil.copy2(DB, backup)
    print(f"[BACKUP] {backup.name}")

    conn = sqlite3.connect(str(DB))
    before = conn.execute(
        "SELECT length(situation), length(task), length(action), length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (ROW_ID,),
    ).fetchone()

    conn.execute(
        "UPDATE behavioral_examples "
        "SET situation = ?, task = ?, action = ?, result = ?, risk_statement = ? "
        "WHERE id = ?",
        (NEW_SITUATION, NEW_TASK, NEW_ACTION, NEW_RESULT, NEW_RISK, ROW_ID),
    )
    conn.commit()

    after = conn.execute(
        "SELECT length(situation), length(task), length(action), length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (ROW_ID,),
    ).fetchone()
    conn.close()

    fields = ["situation", "task", "action", "result", "risk_statement"]
    print(f"[OK] {EXAMPLE_ID} (id={ROW_ID}) '{title}' rewritten:")
    for f, b, a in zip(fields, before, after, strict=False):
        sign = "+" if a >= b else ""
        print(f"  {f:<16} {b:>5} -> {a:>5} chars ({sign}{a - b})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
