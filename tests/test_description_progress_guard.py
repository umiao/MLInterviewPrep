"""Tests for the T-P1-912 Phase-A drift scanner (description_progress_guard.py).

The scanner flags scripts/*.py that write the framework_nodes mutation surface
(description/status/progress_pct) without a reconcile_* call, WARN-only (never
blocks). These tests pin the two AC2 branches, the ORM-precision rule (a
companies.status write must NOT fire), the exempt escape hatch, and assert the
module's own built-in self-test suite stays green.
"""
import importlib
import sys
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent.parent / ".claude" / "hooks"
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

guard = importlib.import_module("description_progress_guard")


def _offending(file_path: str, source: str) -> bool:
    return guard.evaluate_source(file_path, source)[0]


def test_sql_description_write_without_reconcile_warns():
    src = "conn.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (d, 1))\n"
    assert _offending("scripts/seed_x.py", src) is True


def test_sql_description_write_with_reconcile_is_ok():
    src = (
        "from lib.framework_progress import reconcile_node_from_checkboxes\n"
        "conn.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (d, 1))\n"
        "reconcile_node_from_checkboxes(db, 1)\n"
    )
    assert _offending("scripts/seed_x.py", src) is False


def test_orm_description_write_in_framework_node_file_warns():
    src = (
        "from src.backend.models import FrameworkNode\n"
        "node = db.query(FrameworkNode).filter_by(path='a').one()\n"
        "node.description = content.strip()\n"
    )
    assert _offending("scripts/seed_pillarX_content.py", src) is True


def test_direct_status_progress_set_is_surface():
    src = (
        "from src.backend.models import FrameworkNode\n"
        "parent = db.query(FrameworkNode).get(5)\n"
        "parent.progress_pct = pct\n"
        "parent.status = st\n"
    )
    assert _offending("scripts/migrate_recalc.py", src) is True


def test_company_status_write_is_not_flagged():
    # No FrameworkNode reference -> ORM detector must not fire (precision).
    src = (
        "from src.backend.models import Company\n"
        "c = db.query(Company).filter_by(name='LinkedIn').one()\n"
        "c.status = 'phone_screen'\n"
    )
    assert _offending("scripts/import_linkedin_seed.py", src) is False


def test_reconcile_exempt_marker_silences_warning():
    src = (
        "# RECONCILE-EXEMPT: pure prose rewrite, no checkbox semantics\n"
        "conn.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (d, 1))\n"
    )
    assert _offending("scripts/seed_x.py", src) is False


def test_set_title_only_is_not_surface():
    src = "conn.execute('UPDATE framework_nodes SET title = ? WHERE id = ?', (t, 1))\n"
    assert _offending("scripts/seed_x.py", src) is False


def test_reading_description_is_not_a_write():
    src = (
        "from src.backend.models import FrameworkNode\n"
        "for n in db.query(FrameworkNode).all():\n"
        "    if n.description == expected:\n"
        "        print(n.status)\n"
    )
    assert _offending("scripts/audit_x.py", src) is False


def test_non_scripts_path_is_out_of_scope():
    src = "node.description = body\nnode.status = 'mastered'\n"
    assert _offending("src/backend/routers/framework.py", src) is False


def test_insert_into_framework_nodes_with_description_warns():
    src = (
        "conn.execute('INSERT INTO framework_nodes (path, description) VALUES (?, ?)',\n"
        "    ('a/b', desc))\n"
    )
    assert _offending("scripts/seed_new_node.py", src) is True


def test_scanner_never_blocks_in_scan_mode(tmp_path):
    # Even an offending file returns exit 0 from run_scan (Phase A guarantee).
    f = tmp_path / "seed_bad.py"
    f.write_text(
        "conn.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (d, 1))\n",
        encoding="utf-8",
    )
    assert guard.run_scan(f) == 0


def test_builtin_self_tests_pass(capsys):
    assert guard.run_self_test() == 0
