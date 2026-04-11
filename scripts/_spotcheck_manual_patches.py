"""Manual patches outside the T-P2-356 spot-check apply tool scope.

User decisions on the 2026-04-11 spot-check (items 1B and 5b+5c) require
changes the reviewer markdown's apply mode cannot express:

- Option 1B: append a second-order meta-lesson to EX-05's result field so all
  questions routing to EX-05 (not just ADP-15) see the "don't pattern-match
  on other teams' model depth" learning.
- Option 5b: drop OWN-4 -> EX-23 (tight-deadline / responsibility-for-scale
  framing) and add OWN-4 -> EX-17 (difficult-feedback / earn-trust-back
  framing), which is the user's strongly preferred semantic match.
- Option 5c: append a root-cause paragraph to EX-17's result field making
  the over-promise + failed-gatekeeping + recovery-through-mgr-process arc
  explicit -- EX-17 already has the PR feedback / trust rebuild beats but
  does not currently name the over-promise root cause.

This script is idempotent: each UPDATE/DELETE/INSERT is gated by a marker
check so re-runs are no-ops.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"


EX05_APPEND = (
    "\n\n"
    "Second-order lesson I carry forward: the two-month XGBoost was partly a "
    "product of implicit cross-team envy. We had been pattern-matching on the "
    "model-depth trend other ML teams were shipping, without first checking "
    "whether our own traffic distribution, failure modes, and latency budget "
    "justified it. When I went back to the data, 80%+ of requests obviously "
    "did not need the big model at all. Don't anchor architecture decisions to "
    "\"everyone else is going deeper\" or \"this technique is trending.\" "
    "Anchor to your own problem assumptions, data shape, and application "
    "scenarios -- even inside the same org, different domains have meaningfully "
    "different answers."
)
EX05_MARKER = "Second-order lesson I carry forward"


EX17_APPEND = (
    "\n\n"
    "Root cause I later named explicitly: I had over-promised internally under "
    "delivery pressure, and when my manager asked the researcher to bypass the "
    "normal flow and submit the PR directly, I failed to push back on the "
    "shortcut. The senior IC's rejection of my extensive after-the-fact "
    "explanation was the right call -- the gate-keeping failure was mine, and "
    "no amount of explaining could substitute for having blocked the shortcut "
    "in the first place. I re-earned trust through a manager-mediated review "
    "process, rigorous checklist adherence, and time. Deeper lesson: process "
    "integrity is the gatekeeper's job. Over-promise pressure is exactly the "
    "moment you need to hold the line, not the moment to concede it."
)
EX17_MARKER = "Root cause I later named explicitly"


OWN4_NEW_NOTE = (
    "Took responsibility for a quality gatekeeping failure: over-promised "
    "internally, let a manager-driven shortcut through, lost the senior IC's "
    "trust. Recovered through a manager-mediated review process, rigorous "
    "checklist adherence, and time -- re-earned the trust I had let slip."
)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    changes = []

    try:
        conn.execute("BEGIN")

        # --- 1B: append EX-05 result -------------------------------------
        cur.execute(
            "SELECT id, result FROM behavioral_examples WHERE example_id = 'EX-05'"
        )
        ex05_id, ex05_result = cur.fetchone()
        if EX05_MARKER not in (ex05_result or ""):
            cur.execute(
                "UPDATE behavioral_examples SET result = ? WHERE id = ?",
                (ex05_result + EX05_APPEND, ex05_id),
            )
            changes.append("EX-05 result appended with meta-lesson")
        else:
            changes.append("EX-05 result already has meta-lesson (skip)")

        # --- 5c: append EX-17 result -------------------------------------
        cur.execute(
            "SELECT id, result FROM behavioral_examples WHERE example_id = 'EX-17'"
        )
        ex17_id, ex17_result = cur.fetchone()
        if EX17_MARKER not in (ex17_result or ""):
            cur.execute(
                "UPDATE behavioral_examples SET result = ? WHERE id = ?",
                (ex17_result + EX17_APPEND, ex17_id),
            )
            changes.append("EX-17 result appended with over-promise root cause")
        else:
            changes.append("EX-17 result already has over-promise root cause (skip)")

        # --- 5b part 1: add OWN-4 -> EX-17 link --------------------------
        cur.execute(
            "SELECT id FROM behavioral_questions WHERE question_id = 'OWN-4'"
        )
        (own4_id,) = cur.fetchone()

        cur.execute(
            "SELECT id FROM question_example_links "
            "WHERE question_id = ? AND example_id = ?",
            (own4_id, ex17_id),
        )
        existing = cur.fetchone()
        if existing is None:
            cur.execute(
                "INSERT INTO question_example_links "
                "(question_id, example_id, relevance_note) VALUES (?, ?, ?)",
                (own4_id, ex17_id, OWN4_NEW_NOTE),
            )
            changes.append("OWN-4 -> EX-17 link added")
        else:
            changes.append(f"OWN-4 -> EX-17 link already exists (id={existing[0]}) (skip)")

        # --- 5b part 2: drop OWN-4 -> EX-23 link -------------------------
        cur.execute(
            "SELECT id FROM behavioral_examples WHERE example_id = 'EX-23'"
        )
        (ex23_id,) = cur.fetchone()
        cur.execute(
            "DELETE FROM question_example_links "
            "WHERE question_id = ? AND example_id = ?",
            (own4_id, ex23_id),
        )
        if cur.rowcount:
            changes.append(f"OWN-4 -> EX-23 link dropped ({cur.rowcount} row)")
        else:
            changes.append("OWN-4 -> EX-23 link already absent (skip)")

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print("[DONE] Manual spot-check patches applied:")
    for c in changes:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
