"""Structural polish for failure-cluster examples EX-15/16/17/30.

Adds principle_tags (read-modify-write, no removals) and appends
narration-risk guard paragraphs to risk_statement. Idempotent: each
edit is gated on a sentinel string so re-running is safe.
"""
import json
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "mle_prep.db"

SENTINEL_NRG = "<!-- NRG-v1 -->"
SENTINEL_TPV = "<!-- TPV-v1 -->"

EDITS = {
    "EX-15": {
        "add_tags": ["failure", "humility", "process_improvement_from_incident"],
        "append_risk": (
            SENTINEL_NRG,
            f"\n\n{SENTINEL_NRG} NARRATION-RISK GUARD: This is a 'failure that became a "
            "process improvement' story. The risk in narration is that the "
            "cross-team-alignment-mechanism tail makes the failure itself feel small. "
            "STOP the story at the lesson ('I learned to surface informal stakeholder "
            "relationships before deprecating shared infrastructure'); only mention the "
            "cross-team mechanism if the interviewer asks 'what changed afterwards'.",
        ),
    },
    "EX-16": {
        "add_tags": ["failure", "humility", "cross_boundary_failure"],
        "append_risk": (
            SENTINEL_TPV,
            f"\n\n{SENTINEL_NRG} {SENTINEL_TPV} NARRATION-RISK GUARD + TEMPORAL POV: "
            "This story has a redemption tail (the declarative artifactory invitation) "
            "that risks the disguised-success trap. For pure-failure / mistake / 'what "
            "would you do differently' questions, STOP the story at the rollback and the "
            "new cross-team-reviewer policy. The artifactory invitation belongs to a "
            "separate framing of the same incident (a calculated-risk / paradigm-shift "
            "cut) and must NOT be appended to the failure narration. At the moment of "
            "the incident, before the artifactory invitation existed, this WAS a failure "
            "full stop -- and that is the only POV the interviewer should hear when they "
            "asked a failure question.",
        ),
    },
    "EX-17": {
        "add_tags": ["failure", "humility"],
        "append_risk": (
            SENTINEL_NRG,
            f"\n\n{SENTINEL_NRG} NARRATION-RISK GUARD: The temptation in this story is "
            "to lean on 'I built credibility back', which sounds like a redemption arc. "
            "The actual lesson is that I failed to push back on the manager-driven "
            "shortcut under pressure. Frame the lesson as 'I learned to gate-keep my own "
            "work even when my manager is the one cutting the corner', and let the "
            "credibility recovery be IMPLIED, not narrated.",
        ),
    },
    "EX-30": {
        "add_tags": ["failure"],
        "append_risk": (
            SENTINEL_NRG,
            f"\n\n{SENTINEL_NRG} NARRATION-RISK GUARD: See existing 'Use this story for "
            "failure-type questions...' clause above. This story is the cluster's gold "
            "standard and needs no additional guard.",
        ),
    },
}


def patch_example(conn: sqlite3.Connection, example_id: str, edits: dict) -> bool:
    """Apply structural edits to one example. Returns True if DB was modified."""
    row = conn.execute(
        "SELECT principle_tags, risk_statement FROM behavioral_examples WHERE example_id=?",
        (example_id,),
    ).fetchone()
    if not row:
        print(f"[ERROR] {example_id} not found in DB")
        return False

    tags_json, risk = row
    changed = False

    tags = json.loads(tags_json)
    for t in edits["add_tags"]:
        if t not in tags:
            tags.append(t)
            changed = True
            print(f"[patch] {example_id}: added tag '{t}'")
        else:
            print(f"[skip] {example_id}: tag '{t}' already present")

    sentinel, text = edits["append_risk"]
    if sentinel not in (risk or ""):
        risk = (risk or "") + text
        changed = True
        print(f"[patch] {example_id}: appended risk guard ({sentinel})")
    else:
        print(f"[skip] {example_id}: risk guard already present ({sentinel})")

    if changed:
        conn.execute(
            "UPDATE behavioral_examples SET principle_tags=?, risk_statement=? WHERE example_id=?",
            (json.dumps(tags, ensure_ascii=False), risk, example_id),
        )

    return changed


def verify(conn: sqlite3.Connection) -> bool:
    """Run verification checks. Returns True if all pass."""
    ok = True
    for eid in ["EX-15", "EX-16", "EX-17", "EX-30"]:
        row = conn.execute(
            "SELECT principle_tags, risk_statement FROM behavioral_examples WHERE example_id=?",
            (eid,),
        ).fetchone()
        if not row:
            print(f"[FAIL] {eid} not found")
            ok = False
            continue

        tags = json.loads(row[0])
        risk = row[1] or ""

        if "failure" not in tags:
            print(f"[FAIL] {eid}: 'failure' not in principle_tags")
            ok = False
        else:
            print(f"[PASS] {eid}: 'failure' in principle_tags")

        if SENTINEL_NRG not in risk:
            print(f"[FAIL] {eid}: sentinel '{SENTINEL_NRG}' not in risk_statement")
            ok = False
        else:
            print(f"[PASS] {eid}: sentinel '{SENTINEL_NRG}' present")

    row16 = conn.execute(
        "SELECT risk_statement FROM behavioral_examples WHERE example_id='EX-16'",
    ).fetchone()
    if row16 and SENTINEL_TPV not in (row16[0] or ""):
        print(f"[FAIL] EX-16: sentinel '{SENTINEL_TPV}' not in risk_statement")
        ok = False
    else:
        print(f"[PASS] EX-16: sentinel '{SENTINEL_TPV}' present")

    return ok


def main() -> None:
    conn = sqlite3.connect(str(DB))
    any_changed = False

    for eid, edits in EDITS.items():
        if patch_example(conn, eid, edits):
            any_changed = True

    if any_changed:
        conn.commit()
        print("\n[ok] changes committed to DB")
    else:
        print("\n[ok] no changes needed (already patched)")

    print("\n--- Verification ---")
    if not verify(conn):
        conn.close()
        sys.exit(1)

    print("\n[DONE] all checks passed")
    conn.close()


if __name__ == "__main__":
    main()
