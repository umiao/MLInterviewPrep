"""Seed 3 failure-story placeholders (EX-30/31/32) + links to 15 failure-ask Qs.

Context: A behavioral-content audit on 2026-04-11 found only 4 of 29 behavioral
examples (EX-05, EX-08, EX-19, EX-20) contain genuine failure-learning content.
All 15 failure-ask questions route to this tiny pool, forcing story reuse in a
two-failure-question round. These placeholders reserve slots for the user to
later author real failure stories; no invented content is stored.

Idempotent: re-running only inserts rows that do not already exist (keyed by
behavioral_examples.example_id and question_example_links.(question_id, example_id)).

Placeholders:
  EX-30 Technical miscall       (wrong arch / premature optimization / over-engineering)
  EX-31 Interpersonal failure   (peer conflict / lost trust / botched feedback)
  EX-32 Execution / delivery    (missed deadline / shipped regression / wrong project bet)

The 15 failure-ask question_ids are routed by theme:
  EX-30 (technical):      OWN-1, OWN-8, ADP-5, ADP-18, EXE-2
  EX-31 (interpersonal):  COL-1, COL-2, COM-5, ADP-19
  EX-32 (execution):      OWN-11, ADP-11, ADP-13, ADP-15, EXE-6, EXE-9
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

AUDIT_PREFIX = (
    "Audit 2026-04-11 found 4/29 examples contain genuine failure content. "
    "Placeholder reserves a slot for "
)

PLACEHOLDERS = [
    {
        "example_id": "EX-30",
        "title": "[NEEDS-INPUT] Failure story: Technical miscall",
        "theme": "technical",
        "risk_theme": "a technical-miscall (wrong architecture / premature "
        "optimization / over-engineering) failure story.",
    },
    {
        "example_id": "EX-31",
        "title": "[NEEDS-INPUT] Failure story: Interpersonal failure",
        "theme": "interpersonal",
        "risk_theme": "an interpersonal (mishandled peer conflict / lost trust "
        "/ botched feedback) failure story.",
    },
    {
        "example_id": "EX-32",
        "title": "[NEEDS-INPUT] Failure story: Execution / delivery miss",
        "theme": "execution",
        "risk_theme": "an execution/delivery-miss (missed deadline with customer "
        "impact / shipped regression / wrong project bet) failure story.",
    },
]

# Theme routing for the 15 failure-ask questions
QUESTION_ROUTING: dict[str, list[str]] = {
    "EX-30": ["OWN-1", "OWN-8", "ADP-5", "ADP-18", "EXE-2"],
    "EX-31": ["COL-1", "COL-2", "COM-5", "ADP-19"],
    "EX-32": ["OWN-11", "ADP-11", "ADP-13", "ADP-15", "EXE-6", "EXE-9"],
}

LINK_NOTE = "[PLACEHOLDER] pending user-authored failure story"
PRINCIPLE_TAGS_JSON = json.dumps(["failure", "learning", "needs_input"])


def seed(db_path: Path = DB_PATH) -> dict[str, int]:
    """Insert placeholders + links. Idempotent. Returns counts of inserts."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        now = datetime.utcnow().isoformat(sep=" ")

        inserted_examples = 0
        for p in PLACEHOLDERS:
            row = cur.execute(
                "SELECT id FROM behavioral_examples WHERE example_id = ?",
                (p["example_id"],),
            ).fetchone()
            if row is not None:
                continue
            cur.execute(
                """
                INSERT INTO behavioral_examples (
                    example_id, title, source_project,
                    situation, task, action, result,
                    evidence_quotes, principle_tags,
                    risk_statement, analogy, tech_terms,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p["example_id"],
                    p["title"],
                    None,  # source_project
                    "", "", "", "",  # empty STAR fields
                    json.dumps([]),  # evidence_quotes
                    PRINCIPLE_TAGS_JSON,
                    AUDIT_PREFIX + p["risk_theme"],
                    None,  # analogy
                    None,  # tech_terms
                    now,
                ),
            )
            inserted_examples += 1

        # Rebuild example_id -> db id map (for both existing and new rows)
        ex_map: dict[str, int] = {}
        for p in PLACEHOLDERS:
            row = cur.execute(
                "SELECT id FROM behavioral_examples WHERE example_id = ?",
                (p["example_id"],),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"placeholder {p['example_id']} not found after insert")
            ex_map[p["example_id"]] = row["id"]

        # Map string question_id -> db id for all 15 routed questions
        qid_strings = [q for qs in QUESTION_ROUTING.values() for q in qs]
        q_map: dict[str, int] = {}
        for qid in qid_strings:
            row = cur.execute(
                "SELECT id FROM behavioral_questions WHERE question_id = ?",
                (qid,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"failure-ask question {qid} not found in db")
            q_map[qid] = row["id"]

        inserted_links = 0
        for ex_str_id, qid_list in QUESTION_ROUTING.items():
            ex_db_id = ex_map[ex_str_id]
            for qid in qid_list:
                q_db_id = q_map[qid]
                existing = cur.execute(
                    "SELECT id FROM question_example_links WHERE question_id = ? AND example_id = ?",
                    (q_db_id, ex_db_id),
                ).fetchone()
                if existing is not None:
                    continue
                cur.execute(
                    """
                    INSERT INTO question_example_links (
                        question_id, example_id, relevance_note, created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (q_db_id, ex_db_id, LINK_NOTE, now),
                )
                inserted_links += 1

        conn.commit()
        return {
            "inserted_examples": inserted_examples,
            "inserted_links": inserted_links,
            "total_placeholders": len(PLACEHOLDERS),
            "total_links_expected": sum(len(v) for v in QUESTION_ROUTING.values()),
        }
    finally:
        conn.close()


def main() -> None:
    result = seed()
    print(
        "[seed_failure_placeholders] "
        f"inserted_examples={result['inserted_examples']}/{result['total_placeholders']} "
        f"inserted_links={result['inserted_links']}/{result['total_links_expected']}"
    )


if __name__ == "__main__":
    main()
