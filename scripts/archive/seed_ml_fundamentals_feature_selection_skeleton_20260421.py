"""Seed: T-P1-588 -- ML Fundamentals feature_engineering_selection category + 1 leaf.

Adds a new category slot to the existing ml-fundamentals subtree:

  ml-fundamentals/feature_engineering_selection                (cat, depth=1)
    ml-fundamentals/feature_engineering_selection/
      feature-selection-pipeline-1000features                  (leaf, depth=2)

The leaf is inserted as a placeholder ('TODO[MLF-feature-selection-pipeline-1000features]')
and will be filled by T-P1-595. No existing category or leaf is touched.

Safety:
  1. SHA-256 of all 'ml-fundamentals%' rows captured pre/post for audit.
  2. Refuses to run if any target path already exists with a DIFFERENT title
     (protects against accidental overwrite of human edits).
  3. Idempotent: a node whose path+title already match is SKIPPED, not UPDATED.
     Second run yields inserted=0, skipped=2.
  4. Post-run invariant: exactly 36 rows match path LIKE 'ml-fundamentals%'
     (was 34: 1 root + 6 cats + 27 leaves; now 1 root + 7 cats + 28 leaves).
  5. Loads the inventory YAML and asserts item id=28 exists under the new
     category -- frontend wiring and seed stay consistent.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
INVENTORY_PATH = REPO_ROOT / "data" / "ml_fundamentals_inventory.yaml"

ROOT_PATH = "ml-fundamentals"
CATEGORY_SLUG = "feature_engineering_selection"
CATEGORY_TITLE = "Feature Engineering & Selection (特征工程与选择)"
LEAF_ITEM_ID = 28
EXPECTED_TOTAL = 36  # 1 root + 7 cats + 28 leaves


def sha256_subtree(conn: sqlite3.Connection) -> str:
    """Return SHA-256 of all 'ml-fundamentals%' rows, ordered by path."""
    rows = conn.execute(
        "SELECT path, depth, title, description "
        "FROM framework_nodes WHERE path LIKE 'ml-fundamentals%' "
        "ORDER BY path"
    ).fetchall()
    h = hashlib.sha256()
    for r in rows:
        h.update(repr(r).encode("utf-8"))
    return h.hexdigest()


def load_target_item() -> dict:
    """Load inventory YAML and return the item row for id=28.

    Fails loudly if the inventory is missing the expected row, so a drifted
    YAML cannot silently produce a half-wired node.
    """
    with INVENTORY_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = data["items"]
    match = [it for it in items if it["id"] == LEAF_ITEM_ID]
    if len(match) != 1:
        raise RuntimeError(
            f"Expected exactly one inventory item with id={LEAF_ITEM_ID}, "
            f"found {len(match)}"
        )
    item = match[0]
    if item["category"] != CATEGORY_SLUG:
        raise RuntimeError(
            f"Inventory id={LEAF_ITEM_ID} category={item['category']!r} "
            f"does not match seed category {CATEGORY_SLUG!r}"
        )
    return item


def upsert_node(
    conn: sqlite3.Connection,
    *,
    path: str,
    depth: int,
    title: str,
    description: str | None,
    parent_id: int | None,
    importance: float,
) -> tuple[str, int]:
    """Insert if absent, skip if present with matching title, refuse on title conflict.

    Returns (action, node_id) where action is 'INSERTED' or 'SKIPPED'.
    """
    existing = conn.execute(
        "SELECT id, title FROM framework_nodes WHERE path = ?", (path,)
    ).fetchone()
    if existing is not None:
        node_id, existing_title = existing
        if existing_title != title:
            raise RuntimeError(
                f"[CONFLICT] path={path!r} exists with title={existing_title!r}, "
                f"refusing to overwrite with {title!r}"
            )
        return "SKIPPED", node_id
    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description,
             importance, priority, status, progress_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (parent_id, path, depth, title, description,
         importance, "P1", "not_started", 0.0),
    )
    return "INSERTED", cur.lastrowid


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Seed the new category + 1 leaf. Returns action counts."""
    item = load_target_item()
    counts = {"INSERTED": 0, "SKIPPED": 0}

    root = conn.execute(
        "SELECT id FROM framework_nodes WHERE path = ?", (ROOT_PATH,)
    ).fetchone()
    if root is None:
        raise RuntimeError(
            f"Root node {ROOT_PATH!r} missing -- run seed_ml_fundamentals_skeleton.py first"
        )
    root_id = root[0]

    cat_path = f"{ROOT_PATH}/{CATEGORY_SLUG}"
    action, cat_id = upsert_node(
        conn,
        path=cat_path,
        depth=1,
        title=CATEGORY_TITLE,
        description=None,
        parent_id=root_id,
        importance=0.9,
    )
    counts[action] += 1
    print(f"[{action}] cat  id={cat_id} path={cat_path}")

    leaf_path = f"{ROOT_PATH}/{CATEGORY_SLUG}/{item['slug']}"
    leaf_title = f"{item['title_en']} ({item['title_zh']})"
    leaf_description = f"TODO[MLF-{item['slug']}]"
    action, leaf_id = upsert_node(
        conn,
        path=leaf_path,
        depth=2,
        title=leaf_title,
        description=leaf_description,
        parent_id=cat_id,
        importance=0.8,
    )
    counts[action] += 1
    print(f"[{action}] leaf id={leaf_id} path={leaf_path}")

    return counts


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)
    if not INVENTORY_PATH.exists():
        print(f"[FAIL] Inventory not found: {INVENTORY_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_subtree(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = seed(conn)
        conn.commit()

        post_hash = sha256_subtree(conn)
        print(f"[POST] sha256={post_hash}")

        total = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes WHERE path LIKE 'ml-fundamentals%'"
        ).fetchone()[0]
    finally:
        conn.close()

    print(f"[SUMMARY] inserted={counts['INSERTED']} "
          f"skipped={counts['SKIPPED']} "
          f"total_in_subtree={total}")

    if total != EXPECTED_TOTAL:
        print(f"[FAIL] Expected {EXPECTED_TOTAL} rows under ml-fundamentals, got {total}")
        sys.exit(1)
    touched = counts["INSERTED"] + counts["SKIPPED"]
    if touched != 2:
        print(f"[FAIL] Expected to touch 2 nodes (1 cat + 1 leaf), touched {touched}")
        sys.exit(1)
    print("[DONE]")


if __name__ == "__main__":
    main()
