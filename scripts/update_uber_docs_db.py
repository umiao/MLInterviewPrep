"""
Update company_documents DB from translated markdown files.
Maps each Uber BPS markdown file to its DB document ID.
"""

import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_PATH = "data/mle_prep.db"

# Mapping: markdown file path -> DB document ID
FILE_TO_DOC = {
    "docs/uber_bps_mock_sets.md": 35,
    "docs/uber_phone_screen_prep.md": 3,
    "docs/uber_bps_knn_ml_fundamentals.md": 34,
    "docs/uber_bps_pattern_cheatsheet.md": 32,
    "docs/uber_bps_lc_solutions.md": 30,
    "docs/uber_bps_design_architecture.md": 33,
    "docs/uber_bps_custom_solutions.md": 31,
}


def main() -> None:
    """Read each markdown file and update the corresponding DB document."""
    conn = sqlite3.connect(DB_PATH)

    for md_path, doc_id in FILE_TO_DOC.items():
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        conn.execute(
            "UPDATE company_documents SET content = ? WHERE id = ?",
            (content, doc_id),
        )

        row = conn.execute(
            "SELECT length(content) FROM company_documents WHERE id = ?",
            (doc_id,),
        ).fetchone()
        print(f"[OK] Doc {doc_id} <- {md_path} ({row[0]} chars)")

    conn.commit()
    conn.close()
    print("[DONE] All Uber BPS docs updated in DB.")


if __name__ == "__main__":
    main()
