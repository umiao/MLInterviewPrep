"""Seed Google (company_id=3) tags for problems, framework nodes, behavioral examples.

T-P0-218. Idempotent via UPSERT. Second run produces 0 diff.

Run:
    python scripts/tag_google_content.py [--auto-confirm]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
GOOGLE_ID = 3

PROBLEM_TAGS: list[tuple[int, str, str | None]] = [
    (1080, "core", None),
    (1081, "core", "User stumped; priority review"),
    (1082, "core", None),
    (1083, "core", None),
    (1084, "core", None),
    (1086, "core", None),
    (1085, "core", "LC 770 Basic Calculator IV"),
    (5, "likely", "LC 347 Top K Frequent"),
    (273, "likely", "LC 224 Basic Calculator"),
    (393, "likely", "LC 692 Top K Words"),
    (45, "likely", "LC 207 Course Schedule"),
    (113, "likely", "LC 210 Course Schedule II"),
    (254, "likely", "LC 772 Basic Calculator III"),
]

NODE_TAGS: list[tuple[int, str]] = [
    (195, "core"),
    (196, "core"),
    (197, "core"),
    (198, "core"),
    (193, "likely"),
]

BQ_TAGS: list[tuple[int, str, str]] = [
    (2, "core", "leadership"),
    (8, "core", "leadership"),
    (21, "core", "googleyness"),
]


def upsert_problem_tag(
    cur: sqlite3.Cursor, problem_id: int, relevance: str, notes: str | None
) -> str:
    existing = cur.execute(
        "SELECT id, relevance, notes FROM problem_company_tags "
        "WHERE problem_id=? AND company_id=?",
        (problem_id, GOOGLE_ID),
    ).fetchone()
    if existing is None:
        cur.execute(
            "INSERT INTO problem_company_tags (problem_id, company_id, relevance, "
            "source, notes) VALUES (?, ?, ?, 'manual', ?)",
            (problem_id, GOOGLE_ID, relevance, notes),
        )
        return "INSERT"
    if existing[1] != relevance or (existing[2] or None) != (notes or None):
        cur.execute(
            "UPDATE problem_company_tags SET relevance=?, notes=? WHERE id=?",
            (relevance, notes, existing[0]),
        )
        return "UPDATE"
    return "SKIP"


def upsert_node_tag(cur: sqlite3.Cursor, node_id: int, relevance: str) -> str:
    existing = cur.execute(
        "SELECT id, relevance FROM node_company_tags "
        "WHERE node_id=? AND company_id=?",
        (node_id, GOOGLE_ID),
    ).fetchone()
    if existing is None:
        cur.execute(
            "INSERT INTO node_company_tags (node_id, company_id, relevance, source) "
            "VALUES (?, ?, ?, 'manual')",
            (node_id, GOOGLE_ID, relevance),
        )
        return "INSERT"
    if existing[1] != relevance:
        cur.execute(
            "UPDATE node_company_tags SET relevance=? WHERE id=?",
            (relevance, existing[0]),
        )
        return "UPDATE"
    return "SKIP"


def upsert_bq_tag(
    cur: sqlite3.Cursor, example_id: int, relevance: str, attr: str
) -> str:
    existing = cur.execute(
        "SELECT id, relevance, company_attribute FROM "
        "behavioral_example_company_tags "
        "WHERE example_id=? AND company_id=?",
        (example_id, GOOGLE_ID),
    ).fetchone()
    if existing is None:
        cur.execute(
            "INSERT INTO behavioral_example_company_tags "
            "(example_id, company_id, relevance, source, company_attribute) "
            "VALUES (?, ?, ?, 'manual', ?)",
            (example_id, GOOGLE_ID, relevance, attr),
        )
        return "INSERT"
    if existing[1] != relevance or (existing[2] or "") != attr:
        cur.execute(
            "UPDATE behavioral_example_company_tags "
            "SET relevance=?, company_attribute=? WHERE id=?",
            (relevance, attr, existing[0]),
        )
        return "UPDATE"
    return "SKIP"


def confirm_bq_mappings(auto_confirm: bool) -> bool:
    print("\n=== BQ tag mappings (review gate) ===")
    id_to_code = {2: "EX-02", 8: "EX-08", 21: "EX-17"}
    for ex_id, rel, attr in BQ_TAGS:
        print(f"  {id_to_code[ex_id]} (id={ex_id}) -> "
              f"relevance={rel}, company_attribute={attr}")
    print("Distribution: 2 leadership + 1 googleyness")
    if auto_confirm:
        print("[--auto-confirm] Skipping prompt.")
        return True
    try:
        ans = input("Proceed with these BQ mappings? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-confirm", action="store_true",
                    help="Skip BQ review prompt")
    args = ap.parse_args()

    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    counts = {"INSERT": 0, "UPDATE": 0, "SKIP": 0}

    print("=== Problem tags ===")
    for pid, rel, notes in PROBLEM_TAGS:
        action = upsert_problem_tag(cur, pid, rel, notes)
        counts[action] += 1
        print(f"  problem {pid} ({rel}): {action}")

    print("=== Node tags ===")
    for nid, rel in NODE_TAGS:
        action = upsert_node_tag(cur, nid, rel)
        counts[action] += 1
        print(f"  node {nid} ({rel}): {action}")

    if not confirm_bq_mappings(args.auto_confirm):
        print("Aborted before BQ tags; committing problem + node tags only.")
        conn.commit()
        conn.close()
        return 1

    print("=== BQ tags ===")
    for ex_id, rel, attr in BQ_TAGS:
        action = upsert_bq_tag(cur, ex_id, rel, attr)
        counts[action] += 1
        print(f"  example {ex_id} ({rel}, {attr}): {action}")

    conn.commit()

    print("\n=== Totals ===")
    print(f"  INSERT: {counts['INSERT']}")
    print(f"  UPDATE: {counts['UPDATE']}")
    print(f"  SKIP:   {counts['SKIP']}")

    pct = cur.execute(
        "SELECT COUNT(*) FROM problem_company_tags WHERE company_id=?",
        (GOOGLE_ID,),
    ).fetchone()[0]
    nct = cur.execute(
        "SELECT COUNT(*) FROM node_company_tags WHERE company_id=?",
        (GOOGLE_ID,),
    ).fetchone()[0]
    bect = cur.execute(
        "SELECT COUNT(*) FROM behavioral_example_company_tags WHERE company_id=?",
        (GOOGLE_ID,),
    ).fetchone()[0]
    print(f"Google tag totals: problems={pct}, nodes={nct}, bq={bect}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
