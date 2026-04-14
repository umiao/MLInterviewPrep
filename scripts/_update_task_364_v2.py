"""Rewrite T-P2-364 to an autonomous-safe spec.

Removes [NEEDS-INPUT] from the title and replaces the description with a
mechanical/structural-only polish spec. No new evidence_quotes, no new analogies,
no narrative rewrites -- only principle_tag additions and risk_statement guard
paragraphs using the EX-33B template. Per the user: 'don't skip it, find an
unambiguous version that can autonomously work on it.'
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / ".claude" / "tasks.db"

NEW_TITLE = "Behavioral failure cluster: structural polish (tags + narration guards) for EX-15/16/17/30"

NEW_DESC = """STRUCTURAL/MECHANICAL polish ONLY for the 4 remaining failure-cluster master stories. Brings them in line with the EX-33B presentation standard WITHOUT inventing new factual content, so an autonomous session can run this end-to-end with no human fact-check.

FORBIDDEN in this task (deferred to a separate collaborative pass with the user):
- Inventing new evidence_quotes
- Inventing new analogies
- Rewriting Action / Result narrative
- Changing any factual claims (numbers, names, dates, project descriptions)

PERMITTED in this task:
- Adding entries to principle_tags (read-modify-write JSON, no removals)
- Appending a NARRATION-RISK GUARD paragraph to risk_statement (using the templates below — copy verbatim, do NOT rewrite)
- Appending a TEMPORAL POV PRINCIPLE paragraph to risk_statement, EX-16 only

DELIVERABLE: a single idempotent script scripts/_polish_failure_cluster_structural.py modeled after scripts/_patch_ex33b_kpi.py. Each edit gated on a marker string ("NARRATION-RISK GUARD" / "TEMPORAL POV") so re-running does not duplicate.

PER-STORY EXACT EDITS:

================================================================================
EX-15 (Model Deprecation Incident)
================================================================================

principle_tags: ensure JSON list contains the strings 'failure', 'humility', 'process_improvement_from_incident'. Use a read-modify-write pattern: load json, add missing, dump. Do NOT remove existing tags.

risk_statement: idempotent-append (gate on the marker substring 'NARRATION-RISK GUARD' — if already present, skip):

\\n\\nNARRATION-RISK GUARD: This is a 'failure that became a process improvement' story. The risk in narration is that the cross-team-alignment-mechanism tail makes the failure itself feel small. STOP the story at the lesson ('I learned to surface informal stakeholder relationships before deprecating shared infrastructure'); only mention the cross-team mechanism if the interviewer asks 'what changed afterwards'.

================================================================================
EX-16 (Cross-Datacenter Deployment Incident)
================================================================================

principle_tags: ensure JSON list contains 'failure', 'humility', 'cross_boundary_failure'. Read-modify-write.

risk_statement: idempotent-append (gate on the marker substring 'TEMPORAL POV' — if already present, skip):

\\n\\nNARRATION-RISK GUARD + TEMPORAL POV: This story has a redemption tail (the declarative artifactory invitation) that risks the disguised-success trap. For pure-failure / mistake / 'what would you do differently' questions, STOP the story at the rollback and the new cross-team-reviewer policy. The artifactory invitation belongs to a separate framing of the same incident (a calculated-risk / paradigm-shift cut) and must NOT be appended to the failure narration. At the moment of the incident, before the artifactory invitation existed, this WAS a failure full stop — and that is the only POV the interviewer should hear when they asked a failure question.

================================================================================
EX-17 (Difficult Feedback from Senior IC)
================================================================================

principle_tags: ensure JSON list contains 'failure', 'humility'. Read-modify-write.

risk_statement: idempotent-append (gate on the marker substring 'NARRATION-RISK GUARD'):

\\n\\nNARRATION-RISK GUARD: The temptation in this story is to lean on 'I built credibility back', which sounds like a redemption arc. The actual lesson is that I failed to push back on the manager-driven shortcut under pressure. Frame the lesson as 'I learned to gate-keep my own work even when my manager is the one cutting the corner', and let the credibility recovery be IMPLIED, not narrated.

================================================================================
EX-30 (Hash Capability Misdesign)
================================================================================

This is the gold-standard reference. Verify-only:
- principle_tags MUST already contain 'failure'. If absent, add it (do not remove anything).
- risk_statement MUST already contain a narration-risk note ('Use this story for failure-type questions; it does not have a success-tail to soften it.'). If the marker 'NARRATION-RISK GUARD' is also missing, append a one-line redirect to make grep-by-marker uniform across all 4 stories:
  \\n\\nNARRATION-RISK GUARD: See existing 'Use this story for failure-type questions...' clause above. This story is the cluster's gold standard and needs no additional guard.

================================================================================
VERIFICATION (script must run after the patches and exit non-zero if any check fails):

For each of EX-15, EX-16, EX-17, EX-30:
  - SELECT principle_tags FROM behavioral_examples WHERE example_id=...
  - assert 'failure' in json.loads(principle_tags)
  - SELECT risk_statement FROM behavioral_examples WHERE example_id=...
  - assert 'NARRATION-RISK GUARD' in risk_statement
For EX-16 specifically:
  - assert 'TEMPORAL POV' in risk_statement

After DB-level checks pass, verify via the API consumer path:
  - curl -s http://localhost:8100/api/behavioral/examples/by-example-id/EX-15 | python -c 'import json,sys; d=json.load(sys.stdin); assert "failure" in d["principle_tags"]; assert "NARRATION-RISK GUARD" in d["risk_statement"]'
  - Repeat for EX-16, EX-17, EX-30.

(Restart uvicorn first if T-P1-359 was not yet applied in this session.)

================================================================================
ACCEPTANCE:
- All 4 stories have 'failure' principle_tag.
- All 4 stories have a 'NARRATION-RISK GUARD' marker string in risk_statement.
- EX-16 specifically also has 'TEMPORAL POV' language.
- No new evidence_quotes / analogies / STAR-text rewrites were committed.
- Re-running scripts/_polish_failure_cluster_structural.py is idempotent (no duplicated paragraphs, exits cleanly).
- Commit message: '[T-P2-364] Failure cluster structural polish: tags + narration guards'.

DOES NOT cover (deferred to a separate user-collaborative task — to be filed only if the user asks for it):
- Adding new evidence_quotes to EX-15, EX-16, EX-17
- Adding analogies
- Rewriting Action sections to add realization beats
- Adding cn_elevator_pitch refinements (handled by T-P1-358)
"""


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET title=?, description=?, updated_at=CURRENT_TIMESTAMP WHERE id='T-P2-364'",
        (NEW_TITLE, NEW_DESC),
    )
    print(f"rowcount: {c.rowcount}")
    conn.commit()
    c.execute("SELECT title, length(description) FROM tasks WHERE id='T-P2-364'")
    title, desc_len = c.fetchone()
    print(f"new title: {title}")
    print(f"new desc len: {desc_len}")
    print("NEEDS-INPUT removed:", "NEEDS-INPUT" not in title)
    conn.close()


if __name__ == "__main__":
    main()
