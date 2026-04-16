"""Smoke tests for extended doc_kind taxonomy (KG-P1-02).

Verifies: CHECK constraint now accepts canonical_hub/composition/drill,
still rejects unknown values, and the 11 Google R1 drill docs are
backfilled. Skips if runtime DB missing.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DRILL_DOC_IDS = (55, 56, 60, 61, 62, 63, 64, 65, 67, 68, 69)

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


def _insert_tmp(conn: sqlite3.Connection, doc_kind: str) -> None:
    conn.execute(
        "INSERT INTO company_documents (id, company_id, title, content, source_type, doc_kind) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (9_999_000, 3, "tmp taxonomy probe", "", "manual", doc_kind),
    )


def test_ddl_lists_new_kinds() -> None:
    with sqlite3.connect(str(DB_PATH)) as c:
        ddl = c.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='company_documents'"
        ).fetchone()[0]
    for kind in ("canonical_hub", "composition", "drill"):
        assert f"'{kind}'" in ddl, f"doc_kind CHECK missing {kind}"


@pytest.mark.parametrize("kind", ["canonical_hub", "composition", "drill"])
def test_check_accepts_new_kinds(conn: sqlite3.Connection, kind: str) -> None:
    conn.execute("BEGIN")
    try:
        _insert_tmp(conn, kind)
    finally:
        conn.rollback()


def test_check_still_rejects_unknown(conn: sqlite3.Connection) -> None:
    conn.execute("BEGIN")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            _insert_tmp(conn, "nonsense_kind")
    finally:
        conn.rollback()


def test_google_r1_drills_backfilled(conn: sqlite3.Connection) -> None:
    placeholders = ",".join("?" for _ in DRILL_DOC_IDS)
    rows = conn.execute(
        f"SELECT id, doc_kind FROM company_documents WHERE id IN ({placeholders})",
        DRILL_DOC_IDS,
    ).fetchall()
    assert len(rows) == len(DRILL_DOC_IDS), "some drill doc ids missing from DB"
    for row_id, kind in rows:
        assert kind == "drill", f"doc {row_id} expected drill, got {kind}"


def test_hub_doc_still_hub(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT doc_kind FROM company_documents WHERE id=53"
    ).fetchone()
    assert row is not None and row[0] == "hub_doc"
