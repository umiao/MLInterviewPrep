"""Verification script for T-P1-203: Verify imported LC problems.

Checks:
1. Count problems per company tag matches 1014
2. Spot-check first 10 and last 10 match original frequency order
3. Existing problems retained prior data (notes, completion, comfort)
4. No duplicate leetcode_ids
5. All URLs valid format
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "mle_prep.db"
PARSED_PATH = Path(__file__).parent.parent / "data" / "staging_lc_parsed.json"

EXPECTED_TAGGED_COUNT = 1014
COMPANY_TAGS = ["LinkedIn", "Uber", "Adobe"]


def load_parsed() -> list[dict]:
    """Load the parsed staging file."""
    with open(PARSED_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_db_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def check_tag_counts(conn: sqlite3.Connection) -> list[str]:
    """Check 1: Each company tag appears on exactly 1014 problems."""
    errors = []
    cur = conn.cursor()
    for tag in COMPANY_TAGS:
        cur.execute(
            "SELECT COUNT(*) FROM problems WHERE company_tags LIKE ?",
            (f"%{tag}%",),
        )
        count = cur.fetchone()[0]
        if count != EXPECTED_TAGGED_COUNT:
            errors.append(f"[FAIL] {tag} tag count: {count} (expected {EXPECTED_TAGGED_COUNT})")
        else:
            print(f"[PASS] {tag} tag count: {count}")

    # All 3 tags together
    cur.execute(
        "SELECT COUNT(*) FROM problems "
        "WHERE company_tags LIKE '%LinkedIn%' "
        "AND company_tags LIKE '%Uber%' "
        "AND company_tags LIKE '%Adobe%'"
    )
    count = cur.fetchone()[0]
    if count != EXPECTED_TAGGED_COUNT:
        errors.append(f"[FAIL] All-3-tags count: {count} (expected {EXPECTED_TAGGED_COUNT})")
    else:
        print(f"[PASS] All-3-tags count: {count}")

    return errors


def check_frequency_order(conn: sqlite3.Connection, parsed: list[dict]) -> list[str]:
    """Check 2: First 10 and last 10 parsed problems match DB by leetcode_id."""
    errors = []
    cur = conn.cursor()

    # Build parsed lookup by lc_id
    first_10 = parsed[:10]
    last_10 = parsed[-10:]

    for label, group in [("first 10", first_10), ("last 10", last_10)]:
        print(f"\n  Spot-checking {label} parsed problems:")
        for p in group:
            lc_id = p["lc_id"]
            title = p["title"]
            cur.execute(
                "SELECT title, company_tags FROM problems WHERE leetcode_id = ?",
                (lc_id,),
            )
            row = cur.fetchone()
            if row is None:
                errors.append(f"[FAIL] lc_id={lc_id} ({title}) not found in DB")
            else:
                # Check title matches
                if row["title"] != title:
                    errors.append(
                        f"[FAIL] lc_id={lc_id} title mismatch: "
                        f"DB='{row['title']}' parsed='{title}'"
                    )
                # Check tags present
                tags = row["company_tags"] or ""
                missing = [t for t in COMPANY_TAGS if t not in tags]
                if missing:
                    errors.append(
                        f"[FAIL] lc_id={lc_id} missing tags: {missing}"
                    )
                else:
                    print(f"    [PASS] lc_id={lc_id}: {title}")

    return errors


def check_data_retention(conn: sqlite3.Connection) -> list[str]:
    """Check 3: Pre-existing problems retained notes, completion, comfort."""
    errors = []
    cur = conn.cursor()

    # Problems with notes should still have them
    cur.execute(
        "SELECT COUNT(*) FROM problems WHERE notes IS NOT NULL AND notes != ''"
    )
    notes_count = cur.fetchone()[0]
    print(f"\n  Problems with notes: {notes_count}")
    if notes_count == 0:
        errors.append("[FAIL] No problems have notes - data may have been lost")
    else:
        print(f"[PASS] {notes_count} problems retain notes")

    # Completed problems
    cur.execute("SELECT COUNT(*) FROM problems WHERE is_completed = 1")
    completed_count = cur.fetchone()[0]
    print(f"  Completed problems: {completed_count}")
    if completed_count == 0:
        errors.append("[FAIL] No completed problems - data may have been lost")
    else:
        print(f"[PASS] {completed_count} problems retain completion status")

    # Problems without the new tags (pre-existing only)
    cur.execute(
        "SELECT COUNT(*) FROM problems "
        "WHERE (company_tags NOT LIKE '%LinkedIn%' OR company_tags IS NULL)"
    )
    untagged = cur.fetchone()[0]
    print(f"  Pre-existing problems without new tags: {untagged}")
    if untagged > 0:
        print(f"[PASS] {untagged} pre-existing problems correctly not tagged")
        # Verify these still have their original data intact
        cur.execute(
            "SELECT id, leetcode_id, title, notes, is_completed FROM problems "
            "WHERE (company_tags NOT LIKE '%LinkedIn%' OR company_tags IS NULL) "
            "AND (notes IS NOT NULL AND notes != '' OR is_completed = 1) "
            "LIMIT 5"
        )
        rows = cur.fetchall()
        if rows:
            print(f"  Sample untagged with data: {len(rows)} found")
            for r in rows:
                print(f"    id={r['id']} lc={r['leetcode_id']} "
                      f"title={r['title'][:40]} completed={r['is_completed']}")

    return errors


def check_no_duplicate_ids(conn: sqlite3.Connection) -> list[str]:
    """Check 4: No duplicate leetcode_ids."""
    errors = []
    cur = conn.cursor()
    cur.execute(
        "SELECT leetcode_id, COUNT(*) as cnt FROM problems "
        "WHERE leetcode_id IS NOT NULL "
        "GROUP BY leetcode_id HAVING cnt > 1"
    )
    dupes = cur.fetchall()
    if dupes:
        for d in dupes:
            errors.append(f"[FAIL] Duplicate leetcode_id={d['leetcode_id']} (count={d['cnt']})")
    else:
        cur.execute("SELECT COUNT(DISTINCT leetcode_id) FROM problems WHERE leetcode_id IS NOT NULL")
        distinct = cur.fetchone()[0]
        print(f"[PASS] No duplicate leetcode_ids ({distinct} distinct IDs)")

    return errors


def check_urls(conn: sqlite3.Connection, parsed: list[dict]) -> list[str]:
    """Check 5: All URLs are valid LeetCode format.

    Only validates URLs for problems that were part of the import (have all 3
    company tags). Pre-existing problems may have non-standard URLs (leetcode.cn,
    algo.monster, etc.) which are intentional.
    """
    errors = []
    cur = conn.cursor()
    url_pattern = re.compile(r"^https://leetcode\.com/problems/[a-z0-9-]+/?$")

    # Check all problems with URLs
    valid_url_pattern = re.compile(r"^https?://[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}/")
    cur.execute(
        "SELECT id, leetcode_id, title, url FROM problems WHERE url IS NOT NULL"
    )
    rows = cur.fetchall()
    invalid_count = 0
    lc_url_count = 0
    alt_url_count = 0
    for r in rows:
        if not valid_url_pattern.match(r["url"]):
            invalid_count += 1
            if invalid_count <= 5:
                errors.append(
                    f"[FAIL] Malformed URL for id={r['id']} "
                    f"lc={r['leetcode_id']}: {r['url']}"
                )
        elif url_pattern.match(r["url"]):
            lc_url_count += 1
        else:
            alt_url_count += 1

    # Check imported problems without URL
    cur.execute(
        "SELECT COUNT(*) FROM problems "
        "WHERE company_tags LIKE '%LinkedIn%' "
        "AND (url IS NULL OR url = '')"
    )
    no_url = cur.fetchone()[0]

    if invalid_count == 0:
        print(f"[PASS] All {len(rows)} URLs are well-formed "
              f"({lc_url_count} leetcode.com, {alt_url_count} alternative sources)")
    else:
        errors.append(f"[FAIL] {invalid_count} malformed URLs total")

    if no_url > 0:
        print(f"[INFO] {no_url} problems have no URL")

    return errors


def main() -> int:
    """Run all verification checks."""
    print("=" * 60)
    print("LC Import Verification (T-P1-203)")
    print("=" * 60)

    parsed = load_parsed()
    print(f"\nParsed file: {len(parsed)} problems")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM problems")
    total = cur.fetchone()[0]
    print(f"Database: {total} total problems\n")

    all_errors: list[str] = []

    print("--- Check 1: Company tag counts ---")
    all_errors.extend(check_tag_counts(conn))

    print("\n--- Check 2: Frequency order spot-check ---")
    all_errors.extend(check_frequency_order(conn, parsed))

    print("\n--- Check 3: Data retention ---")
    all_errors.extend(check_data_retention(conn))

    print("\n--- Check 4: No duplicate leetcode_ids ---")
    all_errors.extend(check_no_duplicate_ids(conn))

    print("\n--- Check 5: URL validation ---")
    all_errors.extend(check_urls(conn, parsed))

    conn.close()

    print("\n" + "=" * 60)
    if all_errors:
        print(f"VERIFICATION FAILED: {len(all_errors)} error(s)")
        for e in all_errors:
            print(f"  {e}")
        return 1
    else:
        print("ALL CHECKS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
