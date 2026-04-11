"""Seed secondary example links for single-link questions in communication,
collaboration, and leadership categories (T-P1-352).

Idempotent: re-running inserts nothing if the (question_id, example_id) pair
already exists. Never modifies or deletes existing rows.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

# (question_id, secondary_example_id, relevance_note)
# All relevance notes must be >= 30 characters and semantically defensible.
LINKS: list[tuple[str, str, str]] = [
    (
        "COL-4",
        "EX-13",
        "After the authorship dispute, I established explicit authorship and "
        "review norms for the team, which is the concrete mechanism I now "
        "point to when asked how I ensure effective team communication.",
    ),
    (
        "COL-6",
        "EX-04",
        "Educating senior stakeholders that MRR was a misleading proxy is a "
        "direct example of translating a complex statistical concept (metric "
        "bias) into an executive-level narrative with business framing.",
    ),
    (
        "COL-7",
        "EX-03",
        "The cross-org LLM relevance pipeline paired me with non-technical "
        "legal and policy reviewers alongside the eng team, so the story "
        "shows working across both technical and non-technical audiences.",
    ),
    (
        "COL-8",
        "EX-18",
        "Pushing back on the unreasonable distributed-training scope required "
        "managing expectations from PM, eng leads, and the requesting "
        "stakeholder simultaneously without burning trust in any direction.",
    ),
    (
        "COM-3",
        "EX-15",
        "The model-deprecation incident forced me to tell the consuming team "
        "their dependency was going away on a tight timeline -- a textbook "
        "case of delivering bad news while preserving the working relationship.",
    ),
    (
        "COM-4",
        "BLOG-01",
        "Changing the researcher-engineer dynamic was entirely a story of "
        "getting my views heard without formal authority, which is the core "
        "of making your ideas and opinions land inside a team.",
    ),
    (
        "LDR-10",
        "EX-12",
        "Moving the PhD interns from notebook work to production ownership "
        "built their confidence precisely by delegating real production "
        "surface to them instead of shielding them from it.",
    ),
    (
        "LDR-11",
        "EX-12",
        "The PhD interns were struggling with the production stack and the "
        "story walks through how I diagnosed the gap and helped them improve "
        "their delivery -- a direct struggling-team-member-improvement case.",
    ),
    (
        "LDR-2",
        "EX-12",
        "PhD interns unable to ship to production is a performance issue in "
        "junior team members, and the example shows the coaching cadence I "
        "used to close the gap without demoralizing them.",
    ),
    (
        "LDR-5",
        "EX-11",
        "Giving the intern a goal-visibility mechanism empowered them to own "
        "their overpromise recovery rather than being rescued, which is a "
        "clean empowerment example distinct from pure delegation.",
    ),
    (
        "LDR-6",
        "EX-12",
        "Deciding the PhD interns should own production deployments end-to-end "
        "is a concrete delegate-vs-do-it-myself judgment call where I chose "
        "delegation with scaffolding over taking it on personally.",
    ),
    (
        "LDR-7",
        "EX-11",
        "The mentoring story shows successful empowerment: the intern moved "
        "from hiding slippage to proactively surfacing risk on their own after "
        "I handed them the visibility mechanism.",
    ),
    (
        "LDR-8",
        "BLOG-02",
        "Aligning on code review standards meant trusting peers to make the "
        "actual review decisions under the new rubric instead of me reviewing "
        "every PR myself -- a real trust-someone-else moment.",
    ),
    (
        "LDR-9",
        "BLOG-02",
        "The code review standards alignment is explicitly about how to keep "
        "quality high while delegating the reviews themselves, which is the "
        "exact shape of this question.",
    ),
]


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    cur = con.cursor()

    q_id_map: dict[str, int] = {
        r[0]: r[1]
        for r in cur.execute("SELECT question_id, id FROM behavioral_questions")
    }
    e_id_map: dict[str, int] = {
        r[0]: r[1]
        for r in cur.execute("SELECT example_id, id FROM behavioral_examples")
    }

    inserted = 0
    skipped_existing = 0
    missing: list[str] = []

    for qid_str, eid_str, note in LINKS:
        assert len(note) >= 30, f"relevance_note too short for {qid_str}->{eid_str}"
        if qid_str not in q_id_map:
            missing.append(f"question:{qid_str}")
            continue
        if eid_str not in e_id_map:
            missing.append(f"example:{eid_str}")
            continue
        qid = q_id_map[qid_str]
        eid = e_id_map[eid_str]

        existing = cur.execute(
            "SELECT id FROM question_example_links WHERE question_id=? AND example_id=?",
            (qid, eid),
        ).fetchone()
        if existing:
            skipped_existing += 1
            continue

        cur.execute(
            "INSERT INTO question_example_links "
            "(question_id, example_id, relevance_note, created_at) "
            "VALUES (?, ?, ?, ?)",
            (qid, eid, note, datetime.utcnow().isoformat()),
        )
        inserted += 1

    con.commit()
    con.close()

    print(f"[seed] inserted={inserted} skipped_existing={skipped_existing}")
    if missing:
        print(f"[seed] MISSING: {missing}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
