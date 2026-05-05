"""T-P0-735: Coverage for `sd://` scheme support in audit_uri_consistency.

Builds a self-contained throwaway SQLite DB with the minimum schema audit
needs (`problems`, `company_documents`, `system_designs`), seeds one valid
slug + one doc containing both a valid and a dangling sd:// link, and
verifies the audit emits VALID + ERROR findings and exits non-zero.
"""
from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "audit_uri_consistency",
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "audit_uri_consistency.py",
)
assert _SPEC and _SPEC.loader
_audit_module = importlib.util.module_from_spec(_SPEC)
sys.modules["audit_uri_consistency"] = _audit_module
_SPEC.loader.exec_module(_audit_module)

audit = _audit_module.audit
main = _audit_module.main


def _build_fixture_db(path: Path) -> None:
    """Create a tiny DB with one good sd:// target and one dangling one."""
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE problems (id INTEGER PRIMARY KEY);
            CREATE TABLE company_documents (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                company_id INTEGER NOT NULL,
                content TEXT NOT NULL
            );
            CREATE TABLE system_designs (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE
            );
            INSERT INTO system_designs (id, slug) VALUES (1, 'valid-design');
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (
                100,
                'sd-audit-fixture',
                1,
                'See [a](sd://valid-design) and [b](sd://no-such-design).'
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture()
def fixture_db(tmp_path: Path) -> Path:
    """Yield a one-shot SQLite DB path with the audit-fixture schema."""
    db_path = tmp_path / "fixture.db"
    _build_fixture_db(db_path)
    return db_path


def test_sd_audit_emits_valid_and_dangling(fixture_db: Path) -> None:
    """audit() returns VALID for the known slug, ERROR for the dangling one."""
    findings = audit(fixture_db)
    sd_findings = [f for f in findings if f.scheme == "sd"]
    assert len(sd_findings) == 2, sd_findings

    by_severity = {f.severity: f for f in sd_findings}
    assert "VALID" in by_severity and "ERROR" in by_severity, by_severity

    valid = by_severity["VALID"]
    err = by_severity["ERROR"]
    assert valid.target_id == "valid-design"
    assert valid.doc_id == 100
    assert err.target_id == "no-such-design"
    assert "dangling" in err.message
    assert "sd://no-such-design" in err.message


def test_sd_audit_main_exits_nonzero_on_dangling(
    fixture_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI returns 1 when an sd:// dangling link exists."""
    rc = main(["--db", str(fixture_db)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "sd://no-such-design" in out
    assert "ERROR" in out


def test_sd_audit_main_exits_zero_when_no_dangling(tmp_path: Path) -> None:
    """CLI returns 0 when every sd:// link resolves."""
    db_path = tmp_path / "clean.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE problems (id INTEGER PRIMARY KEY);
            CREATE TABLE company_documents (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                company_id INTEGER NOT NULL,
                content TEXT NOT NULL
            );
            CREATE TABLE system_designs (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE
            );
            INSERT INTO system_designs (id, slug) VALUES (1, 'good-slug');
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (200, 'clean-fixture', 1, 'Read [x](sd://good-slug) here.');
            """
        )
        conn.commit()
    finally:
        conn.close()

    rc = main(["--db", str(db_path)])
    assert rc == 0


def test_existing_db_cd_audit_unchanged(tmp_path: Path) -> None:
    """Adding sd:// must not perturb db:// / cd:// classifications."""
    db_path = tmp_path / "mixed.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE problems (id INTEGER PRIMARY KEY);
            CREATE TABLE company_documents (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                company_id INTEGER NOT NULL,
                content TEXT NOT NULL
            );
            CREATE TABLE system_designs (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE
            );
            INSERT INTO problems (id) VALUES (1), (2);
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (10, 'mixed', 1, 'See [p](db://1) and [missing](db://999).');
            """
        )
        conn.commit()
    finally:
        conn.close()

    findings = audit(db_path)
    db_valid = [f for f in findings if f.scheme == "db" and f.severity == "VALID"]
    db_err = [f for f in findings if f.scheme == "db" and f.severity == "ERROR"]
    sd_findings = [f for f in findings if f.scheme == "sd"]
    assert len(db_valid) == 1 and db_valid[0].target_id == 1
    assert len(db_err) == 1 and db_err[0].target_id == 999
    assert sd_findings == []
