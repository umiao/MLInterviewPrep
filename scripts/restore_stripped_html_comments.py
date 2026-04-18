"""Restore HTML comment markers stripped by the T-P1-498 CN rewrite.

Companion to T-P1-504. The CN rewrite (commit 295ada1) lost leading
HTML comment sentinels on 7 nodes (67 was manually repaired on 2026-04-18;
193/195/197/198/200/201 still broken). This script:

1. For each node with a history row, compares leading HTML comments in the
   ORIGINAL (first history entry) description against the CURRENT description.
2. Any comment present in the original but absent from the current description
   is treated as "stripped" and re-prepended at the top (in original order).
3. Writes the current (post-rewrite) description to
   framework_nodes_description_history BEFORE the update, so the fix itself
   is reversible.
4. Idempotent: running twice is a no-op.

The script uses `split_leading_html_comments` from rewrite_nodes_to_cn so the
detection logic matches the fix going forward.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
LOGS_DIR = REPO_ROOT / "logs"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rewrite_nodes_to_cn import split_leading_html_comments  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def extract_comment_lines(leading: str) -> list[str]:
    """Return the list of <!-- ... --> strings from a leading block."""
    return re.findall(r"<!--[\s\S]*?-->", leading)


def audit(conn: sqlite3.Connection) -> list[tuple[int, list[str], list[str], str, str]]:
    """Find nodes whose current description is missing originally-present comments.

    Returns list of (node_id, missing_comments, original_comments_in_order,
    current_description, current_leading_block).
    """
    rows = conn.execute(
        """
        SELECT h.node_id,
               h.description AS original_desc,
               f.description AS current_desc
        FROM framework_nodes_description_history h
        JOIN framework_nodes f ON f.id = h.node_id
        WHERE h.id IN (
            SELECT MIN(id) FROM framework_nodes_description_history GROUP BY node_id
        )
        """
    ).fetchall()
    findings: list[tuple[int, list[str], list[str], str, str]] = []
    for node_id, original_desc, current_desc in rows:
        if not original_desc or not current_desc:
            continue
        original_leading, _ = split_leading_html_comments(original_desc)
        if not original_leading:
            continue
        original_comments = extract_comment_lines(original_leading)
        current_leading, _ = split_leading_html_comments(current_desc)
        # A comment that migrated from top to mid-document is NOT missing.
        missing = [c for c in original_comments if c not in current_desc]
        if missing:
            findings.append(
                (node_id, missing, original_comments, current_desc, current_leading)
            )
    return findings


def restore_node(
    original_comments: list[str],
    current_desc: str,
    current_leading: str,
) -> str:
    """Replace the current leading block with the full original-order block.

    Using original_comments (not missing+existing) preserves canonical order
    on partially-repaired nodes (e.g., node 67 already has doc_kind and
    KG_* sentinels; only canonical_topic needs reinsertion between them).
    """
    body = current_desc[len(current_leading):]
    new_leading = "".join(f"{c}\n" for c in original_comments) + "\n"
    return new_leading + body.lstrip("\n")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    if not DB_PATH.exists():
        print(f"[FAIL] DB not found at {DB_PATH}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(str(DB_PATH))
    try:
        findings = audit(conn)
        print(f"[INFO] Nodes with stripped markers: {len(findings)}")
        for node_id, missing, _, _, _ in findings:
            print(f"  node={node_id} missing={len(missing)}: "
                  f"{[m[:60] for m in missing]}")

        if args.dry_run:
            print("[DONE] Dry-run; no writes.")
            return 0
        if not findings:
            print("[DONE] Nothing to restore.")
            return 0

        updated = 0
        for node_id, missing, original_comments, current_desc, current_leading in findings:
            new_desc = restore_node(
                original_comments, current_desc, current_leading
            )
            conn.execute(
                "INSERT INTO framework_nodes_description_history "
                "(node_id, description) VALUES (?, ?)",
                (node_id, current_desc),
            )
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (new_desc, node_id),
            )
            conn.commit()
            updated += 1
            print(f"  [OK] node={node_id} restored {len(missing)} markers "
                  f"(len {len(current_desc)} -> {len(new_desc)})")

        # Re-audit to confirm idempotency
        remaining = audit(conn)
        if remaining:
            print(f"[WARN] Post-run audit still shows {len(remaining)} nodes "
                  f"with stripped markers.")
            return 1
        print(f"[DONE] Restored {updated} nodes. Post-audit clean.")

        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = LOGS_DIR / f"restore_stripped_html_comments_{ts}.md"
        lines = [
            "# restore_stripped_html_comments -- run summary\n",
            f"- **Timestamp**: {ts}",
            f"- **Nodes restored**: {updated}",
            "",
            "| node_id | markers_restored |",
            "|--------:|------------------|",
        ]
        for node_id, missing, _, _, _ in findings:
            preview = "; ".join(m[:60] for m in missing)
            lines.append(f"| {node_id} | {preview} |")
        log_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[INFO] Wrote {log_path}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
