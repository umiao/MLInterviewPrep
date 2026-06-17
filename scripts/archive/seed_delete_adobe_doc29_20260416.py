"""Seed: delete company_documents.id=29 (Adobe) -- byte-identical duplicate of id=28 (Uber).

T-P1-479 / [KG-M-03]. Idempotent: re-running after deletion prints [UNCHANGED].

Pre-check: SHA256(doc 28 content) must equal SHA256(doc 29 content). Halts otherwise.
Snapshot: archive/pre_kg/20260416/adobe_doc29_snapshot.md written if not present.
Safety: refuses to delete if concept_links or any table references id=29.
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
SNAPSHOT_PATH = REPO_ROOT / "archive" / "pre_kg" / "20260416" / "adobe_doc29_snapshot.md"
EXPECTED_SHA = "3f2db8f9287fc95d91e462577166ca5934a2b2096d5c206fc657ed4b7ef31d51"
TARGET_ID = 29
TWIN_ID = 28


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_snapshot(row: tuple) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc_id, company_name, title, content = row
    header = (
        f"<!-- Pre-delete snapshot of company_documents.id={doc_id} -->\n"
        f"<!-- company={company_name} title={title} -->\n"
        f"<!-- byte-identical duplicate of id={TWIN_ID} (Uber); deleted per T-P1-479 -->\n\n"
    )
    SNAPSHOT_PATH.write_text(header + content, encoding="utf-8")


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT cd.id, co.name AS company, cd.title, cd.content "
        "FROM company_documents cd LEFT JOIN companies co ON cd.company_id=co.id "
        "WHERE cd.id IN (?, ?)",
        (TWIN_ID, TARGET_ID),
    )
    rows = {r["id"]: r for r in cur.fetchall()}

    if TARGET_ID not in rows:
        print(f"[UNCHANGED] doc {TARGET_ID} already absent")
        conn.close()
        return 0
    if TWIN_ID not in rows:
        print(f"[ABORT] twin doc {TWIN_ID} missing -- refusing to delete {TARGET_ID}")
        conn.close()
        return 1

    sha28 = sha256_text(rows[TWIN_ID]["content"])
    sha29 = sha256_text(rows[TARGET_ID]["content"])
    if sha28 != sha29:
        print(f"[ABORT] content diverged: sha28={sha28} sha29={sha29}")
        conn.close()
        return 1
    if sha29 != EXPECTED_SHA:
        print(f"[ABORT] unexpected sha256 for id={TARGET_ID}: got {sha29}, expected {EXPECTED_SHA}")
        conn.close()
        return 1

    cur = conn.execute(
        "SELECT COUNT(*) FROM concept_links "
        "WHERE (src_kind='company_document' AND src_id=?) OR (dst_kind='company_document' AND dst_id=?)",
        (TARGET_ID, TARGET_ID),
    )
    link_count = cur.fetchone()[0]
    if link_count:
        print(f"[ABORT] {link_count} concept_links reference id={TARGET_ID}; migrate them first")
        conn.close()
        return 1

    if not SNAPSHOT_PATH.exists():
        write_snapshot(
            (
                rows[TARGET_ID]["id"],
                rows[TARGET_ID]["company"],
                rows[TARGET_ID]["title"],
                rows[TARGET_ID]["content"],
            )
        )
        print(f"[WROTE] {SNAPSHOT_PATH.relative_to(REPO_ROOT)}")
    else:
        print(f"[KEPT] existing snapshot at {SNAPSHOT_PATH.relative_to(REPO_ROOT)}")

    conn.execute("DELETE FROM company_documents WHERE id=?", (TARGET_ID,))
    conn.commit()
    print(f"[DELETED] company_documents.id={TARGET_ID} ({rows[TARGET_ID]['company']})")

    cur = conn.execute("SELECT COUNT(*) FROM company_documents WHERE id=?", (TARGET_ID,))
    remaining = cur.fetchone()[0]
    conn.close()
    if remaining:
        print("[FAIL] row still present after DELETE")
        return 1
    print("[DONE] verified absent post-delete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
