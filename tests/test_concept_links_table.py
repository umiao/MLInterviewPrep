"""Smoke tests for concept_links table (KG-P1-01).

Verifies: table exists, CHECK constraints enforced, UNIQUE constraint,
indexes present, basic insert/select round-trip. Skips if runtime DB missing.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

pytestmark = pytest.mark.skipif(
    not DB_PATH.exists(), reason="runtime DB data/mle_prep.db not present"
)


@pytest.fixture()
def conn():
    c = sqlite3.connect(str(DB_PATH))
    try:
        yield c
    finally:
        c.rollback()
        c.close()


def test_concept_links_table_exists(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='concept_links'"
    ).fetchone()
    assert row is not None, "concept_links table missing -- run migration"


def test_concept_links_indexes_exist(conn: sqlite3.Connection) -> None:
    names = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' "
            "AND tbl_name='concept_links'"
        ).fetchall()
    }
    assert "ix_concept_links_src" in names
    assert "ix_concept_links_dst" in names


def test_concept_links_insert_select_roundtrip(conn: sqlite3.Connection) -> None:
    conn.execute("BEGIN")
    try:
        cur = conn.execute(
            "INSERT INTO concept_links "
            "(src_kind, src_id, dst_kind, dst_id, relation, weight, note) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("framework_node", 999001, "company_document", 999002, "canonical", 1.0, "smoke"),
        )
        row_id = cur.lastrowid
        row = conn.execute(
            "SELECT src_kind, src_id, dst_kind, dst_id, relation, weight, note "
            "FROM concept_links WHERE id=?",
            (row_id,),
        ).fetchone()
        assert row == (
            "framework_node",
            999001,
            "company_document",
            999002,
            "canonical",
            1.0,
            "smoke",
        )
    finally:
        conn.rollback()


def test_concept_links_check_src_kind(conn: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO concept_links "
            "(src_kind, src_id, dst_kind, dst_id, relation) "
            "VALUES (?, ?, ?, ?, ?)",
            ("bad_kind", 1, "framework_node", 2, "canonical"),
        )
    conn.rollback()


def test_concept_links_check_relation(conn: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO concept_links "
            "(src_kind, src_id, dst_kind, dst_id, relation) "
            "VALUES (?, ?, ?, ?, ?)",
            ("framework_node", 1, "framework_node", 2, "not_a_relation"),
        )
    conn.rollback()


def test_concept_links_unique_constraint(conn: sqlite3.Connection) -> None:
    conn.execute("BEGIN")
    try:
        conn.execute(
            "INSERT INTO concept_links "
            "(src_kind, src_id, dst_kind, dst_id, relation) "
            "VALUES (?, ?, ?, ?, ?)",
            ("framework_node", 888001, "company_document", 888002, "mentions"),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO concept_links "
                "(src_kind, src_id, dst_kind, dst_id, relation) "
                "VALUES (?, ?, ?, ?, ?)",
                ("framework_node", 888001, "company_document", 888002, "mentions"),
            )
    finally:
        conn.rollback()
