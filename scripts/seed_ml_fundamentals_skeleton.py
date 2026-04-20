"""Seed: T-P0-538 -- ML Fundamentals portal skeleton (1 root + 6 categories + 27 leaves).

Creates the framework_nodes tree for the ML Fundamentals portal ('ML 八股文'):

  root  depth=0  path='ml-fundamentals'
    category  depth=1  path='ml-fundamentals/<cat>'   (6 nodes)
      leaf    depth=2  path='ml-fundamentals/<cat>/<slug>'  (27 nodes)

Leaf descriptions are placeholder 'TODO[MLF-<slug>]' strings; real content is
filled by T-P0-539..T-P0-546. Leaf titles come from data/ml_fundamentals_inventory.yaml
(bilingual 'English (Chinese)').

Safety:
  1. SHA-256 of all 'ml-fundamentals%' rows captured pre/post for audit.
  2. Refuses to run if any target path already exists with a DIFFERENT title
     (protects against accidental overwrite of human edits).
  3. Idempotent: a node whose path+title already match is SKIPPED, not UPDATED.
     Second run yields inserted=0, skipped=34.
  4. Post-run invariant: exactly 34 rows match path LIKE 'ml-fundamentals%'.
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
ROOT_TITLE = "ML 八股文 · Fundamentals"

CATEGORY_TITLES: dict[str, str] = {
    "classical_ml": "Classical ML & Losses (经典 ML 与损失函数)",
    "eval_data": "Evaluation & Data (评估与数据)",
    "unsupervised": "Unsupervised Learning (无监督学习)",
    "dl_training": "Deep Learning Training (深度学习训练)",
    "attention_transformer": "Attention & Transformer (注意力机制与 Transformer)",
    "llm_stats": "LLM & Statistics (LLM 与统计)",
}
CATEGORY_ORDER = list(CATEGORY_TITLES.keys())


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


def load_inventory() -> list[dict]:
    """Load and lightly validate the 27-item YAML inventory."""
    with INVENTORY_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = data["items"]
    if len(items) != 27:
        raise RuntimeError(f"Expected 27 items, got {len(items)}")
    seen_slugs: set[str] = set()
    for it in items:
        if it["category"] not in CATEGORY_TITLES:
            raise RuntimeError(f"Unknown category {it['category']!r} on id={it['id']}")
        if it["slug"] in seen_slugs:
            raise RuntimeError(f"Duplicate slug {it['slug']!r}")
        seen_slugs.add(it["slug"])
    return items


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
    """Seed root + 6 categories + 27 leaves. Returns action counts."""
    items = load_inventory()
    counts = {"INSERTED": 0, "SKIPPED": 0}

    action, root_id = upsert_node(
        conn,
        path=ROOT_PATH,
        depth=0,
        title=ROOT_TITLE,
        description=None,
        parent_id=None,
        importance=1.0,
    )
    counts[action] += 1
    print(f"[{action}] root id={root_id} path={ROOT_PATH}")

    cat_ids: dict[str, int] = {}
    for cat in CATEGORY_ORDER:
        path = f"{ROOT_PATH}/{cat}"
        action, cat_id = upsert_node(
            conn,
            path=path,
            depth=1,
            title=CATEGORY_TITLES[cat],
            description=None,
            parent_id=root_id,
            importance=0.9,
        )
        counts[action] += 1
        cat_ids[cat] = cat_id
        print(f"[{action}] cat  id={cat_id} path={path}")

    items_sorted = sorted(items, key=lambda it: it["id"])
    for it in items_sorted:
        cat = it["category"]
        slug = it["slug"]
        path = f"{ROOT_PATH}/{cat}/{slug}"
        title = f"{it['title_en']} ({it['title_zh']})"
        description = f"TODO[MLF-{slug}]"
        action, leaf_id = upsert_node(
            conn,
            path=path,
            depth=2,
            title=title,
            description=description,
            parent_id=cat_ids[cat],
            importance=0.8,
        )
        counts[action] += 1
        print(f"[{action}] leaf id={leaf_id} path={path}")

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

    if total != 34:
        print(f"[FAIL] Expected 34 rows under ml-fundamentals, got {total}")
        sys.exit(1)
    expected = counts["INSERTED"] + counts["SKIPPED"]
    if expected != 34:
        print(f"[FAIL] Expected to touch 34 nodes, touched {expected}")
        sys.exit(1)
    print("[DONE]")


if __name__ == "__main__":
    main()
