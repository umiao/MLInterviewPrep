"""POC patch: upgrade informal '详见 LLM Serving 节点' references on
framework_nodes 130 and 133 to the KG markdown convention (T-P0-472).

Convention (see docs/protocol/kg_markdown_conventions.md):
    > **也见** [LLM Serving (pillar5.serving_infra.llm_serving)](/framework/132)

Idempotent: appends an HTML-comment sentinel '<!-- KG_LINK_POC_20260416 -->'
to each patched description. On re-run, rows with the sentinel are skipped
and the script prints [UNCHANGED].
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- KG_LINK_POC_20260416 -->"

TARGET_NODE_ID = 132  # LLM Serving
CANONICAL_TAG = "> **也见** [LLM Serving (pillar5.serving_infra.llm_serving)](/framework/132)"

# Node 130: replace the informal "（详见 LLM Serving 节点）" parenthetical
# embedded inside a bullet, and append a dedicated blockquote line.
NODE_130_OLD = "- 显著提升 GPU 利用率（详见 LLM Serving 节点）"
NODE_130_NEW = (
    "- 显著提升 GPU 利用率\n"
    f"{CANONICAL_TAG}"
)

# Node 133: the informal "- 详见 LLM Serving 节点" is already a bullet on its
# own line inside the KV Cache section. Replace that bullet with the
# blockquote form so the parser can pick it up.
NODE_133_OLD = "- 详见 LLM Serving 节点"
NODE_133_NEW = CANONICAL_TAG


def patch_node(conn: sqlite3.Connection, node_id: int, old: str, new: str) -> str:
    """Apply one (old -> new) substitution to framework_nodes.description.

    Returns 'unchanged' if the sentinel is already present, 'patched' on
    successful patch, 'not_found' if the expected old substring is missing.
    """
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE id=?",
        (node_id,),
    ).fetchone()
    if row is None:
        return "missing_row"
    desc = row[0] or ""
    if SENTINEL in desc:
        return "unchanged"
    if old not in desc:
        return "not_found"
    patched = desc.replace(old, new, 1) + f"\n\n{SENTINEL}\n"
    conn.execute(
        "UPDATE framework_nodes SET description=? WHERE id=?",
        (patched, node_id),
    )
    return "patched"


def main() -> int:
    if not DB.exists():
        print(f"[ERROR] DB not found: {DB}")
        return 2
    conn = sqlite3.connect(str(DB))
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        targets = [
            (130, NODE_130_OLD, NODE_130_NEW, "Model Serving Systems"),
            (133, NODE_133_OLD, NODE_133_NEW, "Latency Optimization"),
        ]
        statuses: list[tuple[int, str, str]] = []
        for node_id, old, new, title in targets:
            status = patch_node(conn, node_id, old, new)
            statuses.append((node_id, title, status))
        conn.commit()
    finally:
        conn.close()

    patched = sum(1 for _, _, s in statuses if s == "patched")
    unchanged = sum(1 for _, _, s in statuses if s == "unchanged")
    problems = [row for row in statuses if row[2] not in ("patched", "unchanged")]

    for node_id, title, status in statuses:
        tag = {
            "patched": "[PATCHED]",
            "unchanged": "[UNCHANGED]",
            "not_found": "[NOT_FOUND]",
            "missing_row": "[MISSING]",
        }.get(status, f"[{status.upper()}]")
        print(f"{tag} node {node_id} ({title})")

    print(f"\nSummary: {patched} patched, {unchanged} unchanged, {len(problems)} problems")
    if problems:
        return 1
    if patched == 0:
        print("[DONE] all targets already carry the sentinel; no DB change.")
    else:
        print(f"[DONE] patched {patched} node(s) with canonical link blockquote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
