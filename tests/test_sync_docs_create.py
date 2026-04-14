"""Tests for scripts/sync_docs_to_db.py create-new-row path (T-P0-217)."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from sqlalchemy import text


@pytest.fixture()
def sync_module(monkeypatch, db_engine, tmp_path):
    """Import sync_docs_to_db with DOCS_ROOT/get_engine patched to test fixtures."""
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    # Force-reimport so our monkeypatch takes effect.
    if "sync_docs_to_db" in sys.modules:
        del sys.modules["sync_docs_to_db"]
    mod = importlib.import_module("sync_docs_to_db")
    monkeypatch.setattr(mod, "DOCS_ROOT", tmp_path)
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(mod, "get_engine", lambda: db_engine)
    return mod


def _seed_company(db_engine, company_id: int = 3) -> None:
    with db_engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO companies (id, name) VALUES (:i, 'Google')"
        ), {"i": company_id})


def test_create_new_company_document_row(tmp_path, db_engine, sync_module):
    """Frontmatter with company_id+title but no target_id creates a new row."""
    _seed_company(db_engine, 3)
    md = tmp_path / "new_prep.md"
    md.write_text(
        "---\n"
        "target_table: company_documents\n"
        "company_id: 3\n"
        "doc_kind: prep_note\n"
        "title: 'Test Prep Note'\n"
        "---\n"
        "# Body\n\nhello\n",
        encoding="utf-8",
    )
    plans = sync_module.build_plans([md])
    assert len(plans) == 1
    assert plans[0].action == "create"
    updated, skipped, errors = sync_module.apply_plans(plans, dry_run=False)
    assert errors == 0
    assert updated == 1

    with db_engine.begin() as conn:
        row = conn.execute(text(
            "SELECT id, company_id, title, doc_kind, content FROM company_documents "
            "WHERE company_id = 3"
        )).fetchone()
    assert row is not None
    new_id = row[0]
    assert row[1] == 3
    assert row[2] == "Test Prep Note"
    assert row[3] == "prep_note"
    assert "hello" in row[4]

    # Frontmatter must be rewritten with target_id for idempotency.
    raw2 = md.read_text(encoding="utf-8")
    assert f"target_id: {new_id}" in raw2

    # Second run: plan should resolve via target_id and skip.
    plans2 = sync_module.build_plans([md])
    assert len(plans2) == 1
    assert plans2[0].action == "skip"


def test_create_requires_company_id_and_title(tmp_path, db_engine, sync_module):
    """Missing company_id still skips (no create path)."""
    md = tmp_path / "bad.md"
    md.write_text(
        "---\n"
        "target_table: company_documents\n"
        "title: 'No company'\n"
        "---\n"
        "body\n",
        encoding="utf-8",
    )
    plans = sync_module.build_plans([md])
    assert plans == []
