"""T-P1-802: Coverage for `kg://` scheme support in audit_uri_consistency.

Mirrors the sd:// fixture pattern (test_audit_uri_consistency_sd.py): builds a
self-contained throwaway SQLite DB with the minimum schema audit needs
(`problems`, `company_documents`, `system_designs`, `framework_nodes`), seeds
one valid framework_node id + one doc containing both a valid and a dangling
kg:// link, and verifies the audit emits VALID + ERROR findings and exits
non-zero.

AC traceability (from task spec):
  - audit script processes a company_documents row containing kg://1 link
    with a valid framework_node id=1 -> reports VALID;
  - same row with id=99999 (nonexistent) -> reports ERROR.
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
    """Create a tiny DB with one good kg:// target and one dangling one."""
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
            CREATE TABLE framework_nodes (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL
            );
            INSERT INTO framework_nodes (id, path, title)
            VALUES (1, 'pillar1', 'Coding & Algorithms');
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (
                300,
                'kg-audit-fixture',
                1,
                'See [a](kg://1) and [b](kg://99999).'
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture()
def fixture_db(tmp_path: Path) -> Path:
    """Yield a one-shot SQLite DB path with the kg-audit-fixture schema."""
    db_path = tmp_path / "fixture.db"
    _build_fixture_db(db_path)
    return db_path


def test_kg_audit_emits_valid_and_dangling(fixture_db: Path) -> None:
    """audit() returns VALID for the known node id, ERROR for the dangling one.

    Direct AC check: `kg://1` (id=1 exists) -> VALID; `kg://99999` -> ERROR.
    """
    findings = audit(fixture_db)
    kg_findings = [f for f in findings if f.scheme == "kg"]
    assert len(kg_findings) == 2, kg_findings

    by_severity = {f.severity: f for f in kg_findings}
    assert "VALID" in by_severity and "ERROR" in by_severity, by_severity

    valid = by_severity["VALID"]
    err = by_severity["ERROR"]
    assert valid.target_id == 1
    assert valid.doc_id == 300
    assert err.target_id == 99999
    assert "dangling" in err.message
    assert "kg://99999" in err.message
    assert "framework_nodes" in err.message


def test_kg_audit_main_exits_nonzero_on_dangling(
    fixture_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI returns 1 when a kg:// dangling link exists."""
    rc = main(["--db", str(fixture_db)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "kg://99999" in out
    assert "ERROR" in out


def test_kg_audit_main_exits_zero_when_no_dangling(tmp_path: Path) -> None:
    """CLI returns 0 when every kg:// link resolves."""
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
            CREATE TABLE framework_nodes (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL
            );
            INSERT INTO framework_nodes (id, path, title)
            VALUES (7, 'pillar1/sub-7', 'Some Node');
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (400, 'clean-fixture', 1, 'Read [x](kg://7) here.');
            """
        )
        conn.commit()
    finally:
        conn.close()

    rc = main(["--db", str(db_path)])
    assert rc == 0


def test_kg_audit_with_anchor_fragment(tmp_path: Path) -> None:
    """`kg://1#section-a` should still resolve to id=1 (capture group only).

    The frontend regex (MarkdownPreview) accepts `^kg://(\\d+)(?:#[^\\s]*)?$`.
    The Python audit captures only the integer, so anchored URIs MUST audit
    the same as bare ones; the kg dispatcher handles the fragment client-side.
    """
    db_path = tmp_path / "anchor.db"
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
            CREATE TABLE framework_nodes (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL
            );
            INSERT INTO framework_nodes (id, path, title)
            VALUES (42, 'pillar2/x', 'Anchor Target');
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (
                500,
                'anchor-fixture',
                1,
                'Jump to [hash](kg://42#cluster-3) section.'
            );
            """
        )
        conn.commit()
    finally:
        conn.close()

    findings = audit(db_path)
    kg = [f for f in findings if f.scheme == "kg"]
    assert len(kg) == 1
    assert kg[0].severity == "VALID"
    assert kg[0].target_id == 42


def test_existing_db_cd_sd_audit_unchanged(tmp_path: Path) -> None:
    """Adding kg:// must not perturb db:// / cd:// / sd:// classifications."""
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
            CREATE TABLE framework_nodes (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL
            );
            INSERT INTO problems (id) VALUES (1), (2);
            INSERT INTO system_designs (id, slug) VALUES (1, 'twitter-feed');
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (
                10,
                'mixed',
                1,
                'See [p](db://1) and [missing](db://999) and [s](sd://twitter-feed).'
            );
            """
        )
        conn.commit()
    finally:
        conn.close()

    findings = audit(db_path)
    db_valid = [f for f in findings if f.scheme == "db" and f.severity == "VALID"]
    db_err = [f for f in findings if f.scheme == "db" and f.severity == "ERROR"]
    sd_valid = [f for f in findings if f.scheme == "sd" and f.severity == "VALID"]
    kg_findings = [f for f in findings if f.scheme == "kg"]
    assert len(db_valid) == 1 and db_valid[0].target_id == 1
    assert len(db_err) == 1 and db_err[0].target_id == 999
    assert len(sd_valid) == 1 and sd_valid[0].target_id == "twitter-feed"
    assert kg_findings == []


def test_kg_audit_no_cross_table_warning_on_id_collision(tmp_path: Path) -> None:
    """A kg://N where N also exists in problems is VALID (no WARNING, no ERROR).

    Unlike db:// vs cd:// (where collision indicates ambiguity), kg:// targets
    a semantically distinct table; integer-key collision is coincidental and
    must not be flagged. Locks in the design rule from the docstring.
    """
    db_path = tmp_path / "collide.db"
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
            CREATE TABLE framework_nodes (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL
            );
            INSERT INTO problems (id) VALUES (5);
            INSERT INTO framework_nodes (id, path, title)
            VALUES (5, 'pillar1/algo', 'Same Number, Different Catalog');
            INSERT INTO company_documents (id, title, company_id, content)
            VALUES (20, 'collision', 1, 'See [link](kg://5).');
            """
        )
        conn.commit()
    finally:
        conn.close()

    findings = audit(db_path)
    kg = [f for f in findings if f.scheme == "kg"]
    assert len(kg) == 1
    assert kg[0].severity == "VALID"
    assert kg[0].target_id == 5
    # No WARNING was emitted for kg:// despite problems.id == 5 collision.
    warnings = [f for f in findings if f.severity == "WARNING"]
    assert warnings == []


def test_kg_audit_json_output_includes_kg_findings(
    fixture_db: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """--json schema must emit kg-scheme findings with target_id as int."""
    import json

    rc = main(["--db", str(fixture_db), "--json"])
    assert rc == 1  # one dangling kg:// triggers non-zero
    payload = json.loads(capsys.readouterr().out)
    kg_findings = [f for f in payload["findings"] if f["scheme"] == "kg"]
    assert len(kg_findings) == 2
    target_ids = {f["target_id"] for f in kg_findings}
    assert target_ids == {1, 99999}
    severities = {f["severity"] for f in kg_findings}
    assert severities == {"VALID", "ERROR"}
    assert payload["summary"]["error"] >= 1
