# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Seed Pinterest must-do LeetCode problems into the problems table.

Idempotent: adds Pinterest company tag to existing problems, creates missing ones.

Data source: Pinterest interview prep LC list (user-provided 2026-04-12).
"""

import importlib.util
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

# Load sibling helper by file path -- the workspace has a colliding
# ``scripts`` package from another sub-project, so ``from scripts.*`` is
# unreliable here.
_HELPER_PATH = Path(__file__).resolve().parent / "_lc_import_helpers.py"
_helper_spec = importlib.util.spec_from_file_location(
    "_lc_import_helpers", _HELPER_PATH
)
assert _helper_spec is not None and _helper_spec.loader is not None
_lc_import_helpers = importlib.util.module_from_spec(_helper_spec)
_helper_spec.loader.exec_module(_lc_import_helpers)
warn_if_missing_family = _lc_import_helpers.warn_if_missing_family

DB_PATH = "data/mle_prep.db"


def ensure_company_tag(existing_tags_json: str | None, company: str) -> str:
    """Add company to tags list if not present, return JSON string."""
    if not existing_tags_json:
        tags = []
    else:
        try:
            tags = json.loads(existing_tags_json)
        except (json.JSONDecodeError, TypeError):
            tags = [t.strip() for t in existing_tags_json.split(",") if t.strip()]
    if company not in tags:
        tags.append(company)
    return json.dumps(tags, ensure_ascii=False)


# All 14 Pinterest must-do LC problems
PINTEREST_LC_PROBLEMS = [
    {"leetcode_id": 332, "title": "Reconstruct Itinerary", "difficulty": "hard"},
    {"leetcode_id": 465, "title": "Optimal Account Balancing", "difficulty": "hard"},
    {"leetcode_id": 815, "title": "Bus Routes", "difficulty": "hard"},
    {"leetcode_id": 322, "title": "Coin Change", "difficulty": "medium"},
    {"leetcode_id": 282, "title": "Expression Add Operators", "difficulty": "hard"},
    {"leetcode_id": 1055, "title": "Shortest Way to Form String", "difficulty": "medium"},
    {"leetcode_id": 311, "title": "Sparse Matrix Multiplication", "difficulty": "medium"},
    {"leetcode_id": 2402, "title": "Meeting Rooms III", "difficulty": "hard"},
    {"leetcode_id": 1110, "title": "Delete Nodes And Return Forest", "difficulty": "medium"},
    {"leetcode_id": 1244, "title": "Design A Leaderboard", "difficulty": "medium"},
    {"leetcode_id": 410, "title": "Split Array Largest Sum", "difficulty": "hard"},
    {"leetcode_id": 43, "title": "Multiply Strings", "difficulty": "medium"},
    {"leetcode_id": 642, "title": "Design Search Autocomplete System", "difficulty": "hard"},
    {"leetcode_id": 1723, "title": "Find Minimum Time to Finish All Jobs", "difficulty": "hard"},
]

# Problems that need to be created (not in DB)
NEW_PROBLEMS = {
    1110: {
        "url": "https://leetcode.com/problems/delete-nodes-and-return-forest/",
        "tags": json.dumps(["Tree", "DFS", "Binary Tree"]),
        "pattern": "DFS",
    },
    1723: {
        "url": "https://leetcode.com/problems/find-minimum-time-to-finish-all-jobs/",
        "tags": json.dumps(["Backtracking", "Bitmask", "Dynamic Programming"]),
        "pattern": "Dynamic Programming",
    },
}


def seed_pinterest_problems(conn: sqlite3.Connection) -> tuple[int, int, int]:
    """Tag existing problems with Pinterest, create missing ones. Returns (updated, created, skipped)."""
    cursor = conn.cursor()
    updated = 0
    created = 0
    skipped = 0

    for prob in PINTEREST_LC_PROBLEMS:
        lc_id = prob["leetcode_id"]
        cursor.execute(
            "SELECT id, company_tags FROM problems WHERE leetcode_id = ?",
            (lc_id,),
        )
        row = cursor.fetchone()

        if row:
            pid, existing_companies = row
            new_companies = ensure_company_tag(existing_companies, "Pinterest")
            if new_companies != existing_companies:
                cursor.execute(
                    "UPDATE problems SET company_tags = ? WHERE id = ?",
                    (new_companies, pid),
                )
                updated += 1
                print(f"  [TAG] LC {lc_id} - {prob['title']}: added Pinterest tag")
            else:
                skipped += 1
                print(f"  [SKIP] LC {lc_id} - {prob['title']}: already tagged Pinterest")
        else:
            # Create new problem. This seed script does not set a family, so
            # flag each fresh insert (warn + append to quarantine TSV).
            meta = NEW_PROBLEMS.get(lc_id, {})
            url = meta.get("url", f"https://leetcode.com/problems/{prob['title'].lower().replace(' ', '-')}/")
            tags = meta.get("tags", "[]")
            pattern = meta.get("pattern", "")
            family = meta.get("family")
            warn_if_missing_family(
                lc_id=lc_id,
                title=prob["title"],
                family=family,
                source_script="seed_pinterest_lc_problems.py",
            )
            cursor.execute(
                """INSERT INTO problems
                (leetcode_id, title, url, difficulty, tags, pattern, family, category,
                 source, company_tags, priority, is_completed, comfort_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'algorithm', 'pinterest_prep', ?, 1, 0, 0, ?)""",
                (
                    lc_id,
                    prob["title"],
                    url,
                    prob["difficulty"],
                    tags,
                    pattern,
                    family,
                    json.dumps(["Pinterest"]),
                    datetime.now(UTC).isoformat(),
                ),
            )
            created += 1
            print(f"  [NEW] LC {lc_id} - {prob['title']}: created with Pinterest tag")

    conn.commit()
    return updated, created, skipped


def main() -> None:
    """Run seed."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    print("=== Pinterest Must-Do LC Problems ===")
    updated, created, skipped = seed_pinterest_problems(conn)
    print(f"\n  Summary: {updated} tagged, {created} created, {skipped} already done")

    conn.close()
    print("\n[DONE]")


if __name__ == "__main__":
    main()
