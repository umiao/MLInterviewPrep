"""Migrate Meta OA writeups from company_documents to problems table.

T-P0-252 path A. After migration:
- problems table gains 4 rows (Cloud File System, In-Memory Database,
  Bank System, Standalone Algos), each with full notes copy-ported from
  the corresponding company_documents row.
- company_documents 76, 77, 78, 79 are DELETEd (content now lives in
  problems.notes; the hub no longer needs to drawer-link to them).
- company_documents 80 (hub) UPDATEd: every `db://76|77|78|79` link is
  rewritten to `db://<new_problem_id>` so the hub drawer-links open the
  newly-migrated problems via /problems/{id} (which is what the `db://`
  protocol actually fetches — see ProblemDrawer.tsx L21-33).

Why migrate at all: the `db://N` markdown protocol (handled by
MarkdownPreview lines 118-159 + ProblemDrawer) opens `/problems/{N}` in
a SlideOverPanel, NOT `/companies/X/documents/{N}`. The 4 source docs
were authored as company_documents and the hub then drawer-linked them
via `db://76` etc., which silently misrouted to (likely-nonexistent)
problem id 76. Reauthoring the source content as `problems` rows makes
the hub's drawer pattern work as the user expects (Discord agreement
'同意A' on msg 1496613666878001264).

Source of truth for the migrated content: each of the 4
seed_meta_oa_<topic>.py scripts already exports its content as a module
global `CONTENT`. We import them at runtime so the migration cannot
drift from the source seeds. (This same content is what currently lives
in company_documents 76/77/78/79.)

Idempotency:
- INSERT skipped if a problem row with the same title + source exists.
- DELETE skipped if the doc id is already gone.
- Hub UPDATE skipped if the migration sentinel is already present.
- All work runs inside a single SQLite transaction; partial failure
  rolls back, so a re-run sees either pre- or post-migration state, not
  a half-applied mix.

Sentinel: `<!-- META_OA_HUB_PROBLEM_LINKS_20260422 -->` is injected into
hub doc 80 immediately after the existing
`<!-- META_OA_HUB_DRAWER_20260422 -->` sentinel.

Follow-up note: seed_meta_oa_prep_hub.py contains the pre-migration
hub CONTENT (with `db://76|77|78|79` links). Re-running THAT script
after this migration will clobber the rewritten links. Either rerun
this migration after, or rewrite the prep_hub seed to embed the new
problem ids. Out of scope for T-P0-252 (single migration script per
spec); flagged here so future sessions see the coupling.
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR.parent / "data" / "mle_prep.db"

COMPANY_ID = 31  # Meta
HUB_DOC_ID = 80
SOURCE_DOC_IDS = (76, 77, 78, 79)
PROBLEM_SOURCE = "Meta-OA-2026-04-22"
HUB_SENTINEL_OLD = "<!-- META_OA_HUB_DRAWER_20260422 -->"
HUB_SENTINEL_NEW = "<!-- META_OA_HUB_PROBLEM_LINKS_20260422 -->"

# Each entry binds: short title (used as the problems.title and the
# idempotency key), the legacy company_documents id we are replacing,
# the difficulty + pattern + source-seed-module to draw the notes from.
PROBLEM_DEFS: list[dict[str, object]] = [
    {
        "key": "cloud_file_system",
        "title": "Meta OA - Cloud File System",
        "old_doc_id": 76,
        "difficulty": "medium",
        "pattern": "System Design",
        "module": "seed_meta_oa_cloud_file_system",
    },
    {
        "key": "in_memory_database",
        "title": "Meta OA - In-Memory Database",
        "old_doc_id": 77,
        "difficulty": "medium",
        "pattern": "System Design",
        "module": "seed_meta_oa_in_memory_database",
    },
    {
        "key": "bank_system",
        "title": "Meta OA - Bank System",
        "old_doc_id": 78,
        "difficulty": "hard",
        "pattern": "System Design",
        "module": "seed_meta_oa_bank_system",
    },
    {
        "key": "standalone_algos",
        "title": "Meta OA - Standalone Algos",
        "old_doc_id": 79,
        "difficulty": "medium",
        "pattern": "String",
        "module": "seed_meta_oa_standalone_algos",
    },
]


def load_source_content(module_name: str) -> str:
    """Import a sibling seed script and return its CONTENT global.

    Side-effect free: the source seed scripts only run their main()
    under `if __name__ == "__main__"`, so importing them just defines
    the CONTENT constant.
    """
    spec = importlib.util.spec_from_file_location(
        module_name, SCRIPT_DIR / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load source module: {module_name}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "CONTENT"):
        raise RuntimeError(f"module {module_name} has no CONTENT global")
    return mod.CONTENT


def extract_description(content: str) -> str:
    """Pull the `## 1. Problem Overview` section as a brief description.

    The 4 source seeds share a `## 1. Problem Overview\n...\n---\n## 2.`
    layout. We capture between the two h2 markers and trim the trailing
    `---` separator.
    """
    m = re.search(
        r"^## 1\. Problem Overview\s*\n(.*?)(?=^## 2\.)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not m:
        raise RuntimeError("Problem Overview section not found in source")
    desc = m.group(1).rstrip()
    desc = re.sub(r"\n---\s*$", "", desc).rstrip()
    return desc


def rewrite_db_links(text: str, mapping: dict[int, int]) -> str:
    """Rewrite `db://<old>` -> `db://<new>` for every (old, new) in mapping.

    Lookbehind/lookahead enforce digit-boundary so `db://76` inside
    `db://763` is left alone. Only ids actually present in mapping are
    touched (e.g., `db://80` is preserved verbatim).
    """
    digit_alt = "|".join(str(k) for k in mapping)
    pattern = re.compile(rf"(?<![0-9])db://({digit_alt})(?![0-9])")

    def sub(m: re.Match[str]) -> str:
        old = int(m.group(1))
        return f"db://{mapping[old]}"

    return pattern.sub(sub, text)


def main() -> int:
    """Run the migration; idempotent."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}", file=sys.stderr)
        return 1

    sources = {p["key"]: load_source_content(str(p["module"])) for p in PROBLEM_DEFS}
    descriptions = {
        p["key"]: extract_description(sources[p["key"]]) for p in PROBLEM_DEFS
    }
    print(
        f"[OK] loaded {len(sources)} source CONTENT blobs "
        f"(lens: {[len(sources[p['key']]) for p in PROBLEM_DEFS]})"
    )

    conn = sqlite3.connect(str(DB_PATH), isolation_level=None)
    try:
        # company_documents has no FK constraints to it (verified manually);
        # the foreign_keys pragma is enabled defensively in case future
        # migrations add such constraints.
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("BEGIN IMMEDIATE")

        new_ids: dict[str, int] = {}
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Phase 1: ensure 4 problem rows exist (INSERT if missing).
        # Notes/description filled in phase 2 once we know all 4 ids,
        # so cross-refs (db://76 -> db://<new_cloud_fs_id>) can resolve.
        for pdef in PROBLEM_DEFS:
            row = conn.execute(
                "SELECT id FROM problems WHERE title = ? AND source = ?",
                (pdef["title"], PROBLEM_SOURCE),
            ).fetchone()
            if row is not None:
                pid = row[0]
                new_ids[str(pdef["key"])] = pid
                print(f"[SKIP-INSERT] '{pdef['title']}' exists id={pid}")
            else:
                cur = conn.execute(
                    "INSERT INTO problems "
                    "(title, description, notes, difficulty, pattern, "
                    "company_tags, source, description_source, "
                    "is_completed, comfort_level, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)",
                    (
                        pdef["title"],
                        "",  # placeholder, filled in phase 2
                        "",  # placeholder, filled in phase 2
                        pdef["difficulty"],
                        pdef["pattern"],
                        "Meta",
                        PROBLEM_SOURCE,
                        "manual",
                        now,
                    ),
                )
                pid = int(cur.lastrowid or 0)
                if pid <= 0:
                    raise RuntimeError(f"INSERT did not return rowid for {pdef['title']}")
                new_ids[str(pdef["key"])] = pid
                print(f"[INSERT] '{pdef['title']}' id={pid}")

        # mapping: legacy doc id -> newly-allocated problem id
        mapping: dict[int, int] = {
            int(p["old_doc_id"]): new_ids[str(p["key"])] for p in PROBLEM_DEFS
        }

        # Phase 2: UPDATE notes + description with cross-refs rewritten.
        # If existing values already match the desired payload we skip
        # the write (re-run idempotency).
        for pdef in PROBLEM_DEFS:
            pid = new_ids[str(pdef["key"])]
            full_notes = rewrite_db_links(sources[str(pdef["key"])], mapping)
            full_desc = rewrite_db_links(descriptions[str(pdef["key"])], mapping)
            existing = conn.execute(
                "SELECT description, notes FROM problems WHERE id = ?", (pid,)
            ).fetchone()
            if existing == (full_desc, full_notes):
                print(f"[SKIP-UPDATE] problem id={pid} byte-identical")
            else:
                conn.execute(
                    "UPDATE problems SET description = ?, notes = ? WHERE id = ?",
                    (full_desc, full_notes, pid),
                )
                print(
                    f"[UPDATE] problem id={pid} desc={len(full_desc)}ch "
                    f"notes={len(full_notes)}ch"
                )

        # Phase 3: DELETE old company_documents 76/77/78/79.
        for did in SOURCE_DOC_IDS:
            row = conn.execute(
                "SELECT id FROM company_documents WHERE id = ?", (did,)
            ).fetchone()
            if row is None:
                print(f"[SKIP-DELETE] company_documents id={did} already gone")
            else:
                conn.execute(
                    "DELETE FROM company_documents WHERE id = ?", (did,)
                )
                print(f"[DELETE] company_documents id={did}")

        # Phase 4: UPDATE hub (doc 80) - rewrite db:// links + add sentinel.
        hub_row = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?",
            (HUB_DOC_ID,),
        ).fetchone()
        if hub_row is None:
            raise RuntimeError(f"hub doc id={HUB_DOC_ID} missing")
        hub_content = hub_row[0]

        if HUB_SENTINEL_NEW in hub_content:
            print(f"[SKIP-UPDATE-HUB] sentinel '{HUB_SENTINEL_NEW}' already present")
        else:
            new_content = rewrite_db_links(hub_content, mapping)
            if HUB_SENTINEL_OLD in new_content:
                # Insert new sentinel right after the existing drawer sentinel
                # so both stay near the top of the file in chronological order.
                new_content = new_content.replace(
                    HUB_SENTINEL_OLD,
                    HUB_SENTINEL_OLD + "\n" + HUB_SENTINEL_NEW,
                    1,
                )
            else:
                # Defensive: the original drawer sentinel was renamed/removed.
                # Prepend the new one so future runs still skip cleanly.
                new_content = HUB_SENTINEL_NEW + "\n" + new_content

            residual = re.findall(
                r"(?<![0-9])db://(76|77|78|79)(?![0-9])", new_content
            )
            if residual:
                raise RuntimeError(
                    f"residual legacy db:// refs after rewrite: {residual}"
                )

            new_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()
            conn.execute(
                "UPDATE company_documents "
                "SET content = ?, content_hash = ?, updated_at = ? "
                "WHERE id = ?",
                (new_content, new_hash, now, HUB_DOC_ID),
            )
            new_refs = re.findall(r"db://\d+", new_content)
            print(
                f"[UPDATE-HUB] doc id={HUB_DOC_ID} new_refs={new_refs} "
                f"hash={new_hash[:12]}..."
            )

        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        print("[ERROR] migration rolled back", file=sys.stderr)
        raise
    finally:
        conn.close()

    # Sanity report (read-only, post-commit).
    conn = sqlite3.connect(str(DB_PATH))
    try:
        n_meta_problems = conn.execute(
            "SELECT COUNT(*) FROM problems "
            "WHERE company_tags LIKE '%Meta%' AND source = ?",
            (PROBLEM_SOURCE,),
        ).fetchone()[0]
        print(f"[SANITY-A] Meta source-tagged problems: {n_meta_problems} (expect 4)")
        if n_meta_problems != 4:
            raise RuntimeError(
                f"sanity A failed: expected 4 problems, got {n_meta_problems}"
            )

        n_meta_docs = conn.execute(
            "SELECT COUNT(*) FROM company_documents WHERE company_id = ?",
            (COMPANY_ID,),
        ).fetchone()[0]
        print(f"[SANITY-B] company_id={COMPANY_ID} docs remaining: {n_meta_docs} (expect 1)")
        if n_meta_docs != 1:
            raise RuntimeError(
                f"sanity B failed: expected 1 doc, got {n_meta_docs}"
            )

        hub_content_after = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?",
            (HUB_DOC_ID,),
        ).fetchone()[0]
        old_refs = re.findall(
            r"(?<![0-9])db://(76|77|78|79)(?![0-9])", hub_content_after
        )
        all_refs = re.findall(r"db://\d+", hub_content_after)
        print(f"[SANITY-C] hub legacy refs: {len(old_refs)} (expect 0)")
        print(f"[SANITY-C] hub all db:// refs: {all_refs}")
        if old_refs:
            raise RuntimeError(
                f"sanity C failed: residual legacy refs: {old_refs}"
            )
        if len(all_refs) != 8:
            raise RuntimeError(
                f"sanity C failed: expected 8 db:// refs, got {len(all_refs)}"
            )

        # Spot-check: each new problem id is reachable as 'SELECT id, title'.
        for pdef in PROBLEM_DEFS:
            row = conn.execute(
                "SELECT id, title, length(notes) FROM problems "
                "WHERE title = ? AND source = ?",
                (pdef["title"], PROBLEM_SOURCE),
            ).fetchone()
            print(
                f"[SANITY-D] problem '{pdef['title']}' id={row[0]} "
                f"notes_len={row[2]}"
            )
    finally:
        conn.close()

    print("[DONE] migration complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
