"""Rewrite EX-17 (Difficult Feedback from Senior IC).

Replaces situation/task/action/result/risk_statement on
behavioral_examples.example_id='EX-17' with a polished failure-cut
focused on (a) accepting a manager-given framing that let the user
author a PR without owning the deep context, (b) declining manager-
offered protection because that protection would extend the same
shortcut, (c) admitting the user's own technically-accurate explanation
was beside the point, (d) the kill-line lesson "I had conflated being
relied on with being trusted".

User Discord msg 1496042271752323142 supplied the raw rewrite;
1496043894339670101 + 1496044325115527248 confirmed Risk option 1
(expanded "defaults-class risk" version aligned with EX-15 golden
length) + delegated linkage decisions to claude per "酌情".

Existing NRG-v1 already correctly identified the redemption-arc trap
("Built mutual respect" / "good professional friends"). The new STAR
walks the talk by demoting recovery to a flat "second-order outcome"
line; NRG-v2 replaces NRG-v1 with pacing + per-question framing
guidance.

Idempotent: situation+task starts with "A teammate on another
workstream went on unexpected leave mid-launch" indicates rewrite is
already applied.
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
EXAMPLE_ID = "EX-17"

IDEMPOTENT_MARKER = "A teammate on another workstream went on unexpected leave"

# Combined Situation & Task (user's framing -- they merged S+T in raw rewrite).
# Splitting back out: Situation = the inheritance setup; Task = the framing
# acceptance + what the user committed to deliver.
NEW_SITUATION = (
    "A teammate on another workstream went on unexpected leave mid-launch. "
    "I was the only available MLE with merge rights. My manager asked me "
    "to inherit a researcher's remote branch and carry it through the "
    "final checklist to merge."
)

NEW_TASK = (
    "I raised one concern: I could only do surface-level review -- naming, "
    "redundancy, tests. I didn't have deep context on the module. I was "
    "told the researcher had that context and I wasn't expected to own "
    "that layer. I accepted the framing and proceeded."
)

NEW_ACTION = (
    "I verified the PR and marked it ready. Between my verification and "
    "merge, the researcher pushed naming changes I hadn't seen. CI broke. "
    "A senior IC who was reviewing refused to continue. He told me to "
    "find another reviewer or he'd rubber-stamp it. He wasn't angry "
    "about the CI failure. He was angry that I'd executed my manager's "
    "instruction literally without holding my own gate.\n\n"
    "My manager offered to explain the situation to him on my behalf.\n\n"
    "I declined.\n\n"
    "If she explained it, the story would become \"engineer caught in a "
    "bad setup.\" The real story was that I'd accepted a framing that "
    "let me author a PR without owning it, and org policy was explicit "
    "that engineers own their PRs. Accepting her protection would extend "
    "the same shortcut that caused the problem.\n\n"
    "I tried to explain the full context to the senior IC directly. He "
    "refused to hear it. He was right to. My explanation was technically "
    "accurate and completely beside the point.\n\n"
    "I rebuilt through a manager-mediated review process, strict "
    "checklist adherence, and fast on-call responsiveness. No grand "
    "gestures. Just consistency."
)

NEW_RESULT = (
    "Within about two months, the senior IC was reviewing my code "
    "normally again. A second-order outcome: teammates began inviting me "
    "to review their PRs specifically because I'd become known for "
    "citing policy gaps and fast turnaround. The engineer-researcher "
    "ownership boundary became explicit team practice.\n\n"
    "The lesson: **I had conflated being relied on with being trusted. "
    "They're different.** Being relied on means the team needs your "
    "hands under pressure. Being trusted means the team believes you'll "
    "hold the line under that pressure, including saying no. I was "
    "optimizing for the first at the cost of the second."
)

NEW_RISK = (
    "The surface risk was a damaged working relationship with one "
    "senior engineer. The structural risk was that I'd carry the wrong "
    "mental model -- reliance and trust as interchangeable -- into "
    "every future pressure situation. Each \"hands needed now\" moment "
    "would default me to conceding the gate, and the cost of that "
    "default scales with seniority: the more capable I am, the more "
    "often I'll be the one asked to bypass review, and the more damage "
    "each yes does. This isn't an incident-class risk. It's a "
    "defaults-class risk.\n\n"
    "<!-- NRG-v2 --> NARRATION GUARD: Pace the three high-signal beats "
    "-- pause after \"I declined\" (one-word sentence on its own line, "
    "let it land); pause after \"He was right to\" before \"My "
    "explanation was technically accurate and completely beside the "
    "point\" (the admission needs space); brief beat after \"They're "
    "different\" in the lesson. The redemption-arc temptation flagged "
    "by the prior NRG-v1 (lean on \"good professional friends\") is "
    "already cut from the STAR -- but on the \"second-order outcome\" "
    "line (\"teammates began inviting me to review their PRs\"), keep "
    "voice flat: this is process behavior change, not popularity "
    "recovery. If asked COM-5 (\"feedback you disagreed with\"), open "
    "with \"I initially wanted to push back with technical context\" "
    "before revealing the maturation. For OWN-3 / ADP-19 / ADP-17 "
    "(handle / seek / grow-from feedback) lead with the gate-keeping "
    "insight as the actionable lesson. Do not soften the manager-"
    "decline beat -- it is the strongest character signal in the story."
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
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex17_rewrite")
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
