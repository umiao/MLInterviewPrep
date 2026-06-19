"""Phase-A drift SCANNER: framework_nodes mutation surface vs reconcile (T-P1-912).

This is the "doctor not police" Phase A guard for the checkbox-canonical drift
class documented in `docs/adr/ADR-checkbox-canonical.md` (T-P0-910/914). It
DETECTS + WARNS + suggests the autofix; it NEVER blocks. CI fail-on-drift,
runtime self-heal, and PreToolUse wiring are Phase B (T-P1-917) and are
deliberately out of scope here.

Background (the bug this prevents from silently recurring)
----------------------------------------------------------
For a leaf `framework_nodes` row, the GFM checkbox state inside
`description` (`- [x]` / `- [ ]`) is canonical; `status` and `progress_pct`
are derived projections. A direct `description` write that toggles checkboxes
WITHOUT re-deriving `status`/`progress_pct` produces the 2026-05-19 node-44 bug
(5/5 boxes checked, still rendered "Not Started"). The sanctioned fix is to
call the single reconcile implementation in
`scripts/lib/framework_progress.py` after the write and before commit:

    from lib.framework_progress import reconcile_node_from_checkboxes
    reconcile_node_from_checkboxes(db, node.id)   # re-derive status/progress_pct
    # ... or, for the fully-checked batch:
    from lib.framework_progress import reconcile_all_fully_checked
    reconcile_all_fully_checked(db)

The mutation surface (ADR root-cause)
-------------------------------------
A `scripts/*.py` file *writes the surface* when it does any of:
  (i)  SQL: `UPDATE|INSERT INTO|REPLACE INTO framework_nodes` whose column set
       includes one of {description, status, progress_pct}.
  (ii) ORM: an attribute assignment `<obj>.description|.status|.progress_pct = ...`
       in a file that references the `FrameworkNode` model (the reference
       requirement scopes ORM detection to framework_nodes and filters
       unrelated `.status` writes such as `companies.status`).

Scanner semantics (AC2 -- BOTH branches, never blocks)
------------------------------------------------------
  * writes the surface AND (calls a `reconcile_*` helper OR carries a
    `# RECONCILE-EXEMPT: <reason>` line)  -> SILENT OK.
  * writes the surface WITHOUT a reconcile call AND not exempt
    -> WARN to stderr + a copy-paste autofix hint naming the helper, exit 0.

Phase A exit code is ALWAYS 0 in scan/staged/sweep paths. The only output is
the warning. Single mode -- no strict|safe abstraction until a use case appears.

Modes (parity with invariant3_guard's mode surface, AC3)
--------------------------------------------------------
  --test            Run built-in self-tests; exit 0 on pass, 2 on fail.
  --scan PATH       Read PATH from disk and report whether it would WARN
                    (back-test mode). Always exits 0 (Phase A never blocks).
  --sweep [DIR]     Read-only offender report over all .py under DIR
                    (default scripts/). Always exits 0; this is the AC6 triage
                    surface (retrofit-vs-exempt list).
  --staged          Scan staged scripts/*.py (git diff --cached). The pre-commit
                    SCAN wiring point (AC5). Always exits 0; commit proceeds.

Best-effort by design (AC edge case): AST + the exempt escape hatch. Residual
false-negatives are documented (e.g. surface writes assembled entirely from
non-literal SQL, or a file that writes node A's description but reconciles
node B -- file-level granularity cannot distinguish). Never crashes: any
infrastructure error degrades to a no-op exit 0.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_utils import init_utf8_streams  # noqa: E402

# --- Surface definition ----------------------------------------------------

SURFACE_COLUMNS = ("description", "status", "progress_pct")

# SQL write to the framework_nodes table (any of the three write verbs).
FRAMEWORK_NODES_WRITE_RX = re.compile(
    r"\b(?:UPDATE\s+framework_nodes\s+SET|"
    r"INSERT\s+INTO\s+framework_nodes|"
    r"REPLACE\s+INTO\s+framework_nodes)\b",
    re.IGNORECASE,
)
# A surface column mentioned within the same SQL string literal.
SURFACE_COLUMN_RX = re.compile(
    r"\b(description|status|progress_pct)\b",
    re.IGNORECASE,
)

# The model class whose presence scopes ORM attribute writes to framework_nodes.
FRAMEWORK_NODE_MODEL = "FrameworkNode"

# Exempt escape hatch (file-level; honoured anywhere in the file).
RECONCILE_EXEMPT_RX = re.compile(r"^\s*#\s*RECONCILE-EXEMPT:", re.MULTILINE)

# A call to the sanctioned reconcile helper family.
RECONCILE_CALL_PREFIX = "reconcile_"

WARN_BANNER = (
    "[DESCRIPTION-DRIFT WARN] framework_nodes mutation surface written without a "
    "reconcile_* call.\n"
    "The checkbox state in framework_nodes.description is canonical; status/"
    "progress_pct\n"
    "are derived projections. A direct write that does not re-derive them is the\n"
    "node-44 drift class (5/5 checked still showing 'Not Started').\n"
)

AUTOFIX_HINT = (
    "Autofix -- after the description write and before commit, add:\n"
    "    from lib.framework_progress import reconcile_node_from_checkboxes\n"
    "    reconcile_node_from_checkboxes(db, node.id)   # re-derive status/progress_pct\n"
    "  (or, for the fully-checked batch:\n"
    "    from lib.framework_progress import reconcile_all_fully_checked\n"
    "    reconcile_all_fully_checked(db))\n"
    "If this write deliberately carries no checkbox semantics, add a line:\n"
    "    # RECONCILE-EXEMPT: <reason>\n"
    "See docs/adr/ADR-checkbox-canonical.md. Phase A = warning only; "
    "commit still succeeds."
)


# --- Path / marker helpers -------------------------------------------------


def is_scripts_py_path(file_path: str) -> bool:
    """True iff file_path is a Python file under scripts/."""
    if not file_path:
        return False
    p = file_path.replace("\\", "/").lower()
    if not p.endswith(".py"):
        return False
    return ("/scripts/" in p) or p.startswith("scripts/")


def has_reconcile_exempt_marker(source: str) -> bool:
    """True iff a `# RECONCILE-EXEMPT: <reason>` line appears anywhere."""
    return bool(RECONCILE_EXEMPT_RX.search(source))


def references_framework_node_model(source: str) -> bool:
    """True iff the source references the FrameworkNode ORM model token."""
    return FRAMEWORK_NODE_MODEL in source


# --- Detection -------------------------------------------------------------


def _string_payload(node):
    """If node is a Constant str or an f-string, return its assembled text."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            elif isinstance(v, ast.FormattedValue):
                parts.append("{?}")
        return "".join(parts)
    return None


def _find_sql_surface_writes(tree, source: str):
    """Return findings for SQL writes to framework_nodes touching the surface."""
    findings = []
    seen_lines = set()
    for node in ast.walk(tree):
        text = _string_payload(node)
        if not text:
            continue
        if not FRAMEWORK_NODES_WRITE_RX.search(text):
            continue
        cols = {m.group(1).lower() for m in SURFACE_COLUMN_RX.finditer(text)}
        if not cols:
            continue
        line = getattr(node, "lineno", 0)
        if line in seen_lines:
            continue
        seen_lines.add(line)
        findings.append(
            "line " + str(line) + ": SQL write to framework_nodes touching "
            + "{" + ", ".join(sorted(cols)) + "}"
        )
    return findings


def _find_orm_surface_writes(tree, source: str):
    """Return findings for ORM `.description|.status|.progress_pct = ...` writes.

    Scoped to files that reference the FrameworkNode model so unrelated
    attribute writes (e.g. ``companies.status``) are not flagged.
    """
    if not references_framework_node_model(source):
        return []
    findings = []
    seen_lines = set()
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        else:
            continue
        for tgt in targets:
            if isinstance(tgt, ast.Attribute) and tgt.attr in SURFACE_COLUMNS:
                line = getattr(node, "lineno", 0)
                if line in seen_lines:
                    continue
                seen_lines.add(line)
                findings.append(
                    "line " + str(line) + ": ORM attribute write ." + tgt.attr
                    + " = ... (file references " + FRAMEWORK_NODE_MODEL + ")"
                )
    return findings


def _calls_reconcile(tree) -> bool:
    """True iff the AST contains a call to a `reconcile_*` function."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name and name.startswith(RECONCILE_CALL_PREFIX):
            return True
    return False


def find_surface_writes(source: str):
    """Return (sql_findings, orm_findings) for surface writes in source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Regex fallback for unparseable files: SQL form only (ORM needs AST).
        findings = []
        for m in FRAMEWORK_NODES_WRITE_RX.finditer(source):
            window = source[m.start():m.start() + 400]
            if SURFACE_COLUMN_RX.search(window):
                line = source.count("\n", 0, m.start()) + 1
                findings.append(
                    "line " + str(line)
                    + ": SQL write to framework_nodes (unparseable file, regex fallback)"
                )
        return (findings, [])
    return (_find_sql_surface_writes(tree, source), _find_orm_surface_writes(tree, source))


def evaluate_source(file_path: str, source: str):
    """Return (offending, findings).

    offending=True means: writes the surface, has NO reconcile_* call, and is
    NOT exempt -> the WARN case. Otherwise offending=False (silent OK).
    """
    if not is_scripts_py_path(file_path):
        return (False, [])
    sql_findings, orm_findings = find_surface_writes(source)
    findings = sql_findings + orm_findings
    if not findings:
        return (False, [])
    if has_reconcile_exempt_marker(source):
        return (False, [])
    try:
        tree = ast.parse(source)
        if _calls_reconcile(tree):
            return (False, [])
    except SyntaxError:
        # Unparseable: fall back to a literal token check for a reconcile call.
        if (RECONCILE_CALL_PREFIX in source) and "reconcile_" in source:
            return (False, [])
    return (True, findings)


def format_warn_message(file_path: str, findings) -> str:
    body = "\n".join("  - " + f for f in findings)
    return (
        WARN_BANNER + "\nFile: " + file_path + "\nFindings:\n" + body
        + "\n\n" + AUTOFIX_HINT
    )


# --- Modes -----------------------------------------------------------------


def run_scan(target: Path) -> int:
    """Back-test a single file. Always exits 0 (Phase A never blocks)."""
    try:
        source = target.read_text(encoding="utf-8")
    except OSError as exc:
        print("[SCAN-ERR] cannot read " + str(target) + ": " + str(exc), file=sys.stderr)
        return 0
    offending, findings = evaluate_source(str(target), source)
    if offending:
        print(format_warn_message(str(target), findings), file=sys.stderr)
    else:
        print("[CLEAN] " + str(target))
    return 0


def _classify(file_path: str, source: str) -> str:
    """Return one of CLEAN | WARN | RECONCILED | EXEMPT | OUT-OF-SCOPE."""
    if not is_scripts_py_path(file_path):
        return "OUT-OF-SCOPE"
    sql_findings, orm_findings = find_surface_writes(source)
    if not (sql_findings or orm_findings):
        return "CLEAN"
    if has_reconcile_exempt_marker(source):
        return "EXEMPT"
    try:
        if _calls_reconcile(ast.parse(source)):
            return "RECONCILED"
    except SyntaxError:
        if RECONCILE_CALL_PREFIX in source:
            return "RECONCILED"
    return "WARN"


def run_sweep(root: Path) -> int:
    """Read-only offender report over all .py under root. Always exits 0 (AC6)."""
    if not root.exists():
        print("[SWEEP] no such directory: " + str(root))
        return 0
    files = sorted(p for p in root.rglob("*.py"))
    counts = {"CLEAN": 0, "WARN": 0, "RECONCILED": 0, "EXEMPT": 0}
    print("[SWEEP] scanning " + str(len(files)) + " .py file(s) under " + str(root) + "\n")
    for f in files:
        try:
            source = f.read_text(encoding="utf-8")
        except OSError as exc:
            print("  [SKIP] " + str(f) + ": " + str(exc))
            continue
        verdict = _classify(str(f), source)
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict == "WARN":
            _, findings = evaluate_source(str(f), source)
            print("  [WARN] " + str(f))
            for finding in findings:
                print("          - " + finding)
        elif verdict in ("RECONCILED", "EXEMPT"):
            print("  [" + verdict + "] " + str(f))
    print(
        "\n[SWEEP] summary: " + str(counts["CLEAN"]) + " clean, "
        + str(counts["WARN"]) + " warn (retrofit candidates), "
        + str(counts["RECONCILED"]) + " reconciled, "
        + str(counts["EXEMPT"]) + " exempt, total " + str(len(files))
    )
    print(
        "[SWEEP] triage: the " + str(counts["WARN"]) + " WARN file(s) are the "
        "retrofit-vs-exempt list. Retrofitting historical scripts is OUT OF SCOPE "
        "for T-P1-912 (Phase A)."
    )
    return 0


def _staged_scripts_py():
    """Return the list of staged scripts/*.py paths (git diff --cached)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except (OSError, ValueError):
        return []
    paths = []
    for line in (out.stdout or "").splitlines():
        line = line.strip()
        if is_scripts_py_path(line):
            paths.append(line)
    return paths


def run_staged() -> int:
    """Scan staged scripts/*.py. The pre-commit SCAN wiring point (AC5).

    Always exits 0 -- Phase A never blocks the commit.
    """
    paths = _staged_scripts_py()
    if not paths:
        return 0
    warned = 0
    for p in paths:
        try:
            source = Path(p).read_text(encoding="utf-8")
        except OSError:
            continue
        offending, findings = evaluate_source(p, source)
        if offending:
            warned += 1
            print(format_warn_message(p, findings), file=sys.stderr)
    if warned:
        print(
            "[description_progress_guard] "
            + str(warned)
            + " staged script(s) write the framework_nodes surface without a "
            "reconcile_* call (WARN only -- commit proceeds).",
            file=sys.stderr,
        )
    return 0


# --- Self-tests (AC3) ------------------------------------------------------

TEST_CASES = [
    (
        "SQL UPDATE framework_nodes SET description without reconcile -> WARN",
        "scripts/seed_x.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (d, 1))\n"
        ),
        True,
    ),
    (
        "SQL UPDATE ... description WITH reconcile_node_from_checkboxes -> OK",
        "scripts/seed_x.py",
        (
            "from lib.framework_progress import reconcile_node_from_checkboxes\n"
            "conn.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (d, 1))\n"
            "reconcile_node_from_checkboxes(db, 1)\n"
        ),
        False,
    ),
    (
        "ORM node.description write in a FrameworkNode file without reconcile -> WARN",
        "scripts/seed_pillarX_content.py",
        (
            "from src.backend.models import FrameworkNode\n"
            "node = db.query(FrameworkNode).filter_by(path='a').one()\n"
            "node.description = content.strip()\n"
            "db.commit()\n"
        ),
        True,
    ),
    (
        "ORM node.description write WITH reconcile_all_fully_checked -> OK",
        "scripts/seed_pillarX_content.py",
        (
            "from src.backend.models import FrameworkNode\n"
            "from lib.framework_progress import reconcile_all_fully_checked\n"
            "node = db.query(FrameworkNode).filter_by(path='a').one()\n"
            "node.description = content.strip()\n"
            "reconcile_all_fully_checked(db)\n"
            "db.commit()\n"
        ),
        False,
    ),
    (
        "RECONCILE-EXEMPT marker disables the warning -> OK",
        "scripts/seed_x.py",
        (
            "# RECONCILE-EXEMPT: pure prose rewrite, no checkbox semantics\n"
            "conn.execute('UPDATE framework_nodes SET description = ? WHERE id = ?', (d, 1))\n"
        ),
        False,
    ),
    (
        "Direct status/progress_pct ORM set in FrameworkNode file -> WARN (surface)",
        "scripts/migrate_recalc.py",
        (
            "from src.backend.models import FrameworkNode\n"
            "parent = db.query(FrameworkNode).get(5)\n"
            "parent.progress_pct = new_progress\n"
            "parent.status = new_status\n"
        ),
        True,
    ),
    (
        "Company .status write (no FrameworkNode reference) -> NOT flagged (precision)",
        "scripts/import_linkedin_seed.py",
        (
            "from src.backend.models import Company\n"
            "linkedin = db.query(Company).filter_by(name='LinkedIn').one()\n"
            "linkedin.status = 'phone_screen'\n"
        ),
        False,
    ),
    (
        "Reading description (==) but not writing -> NOT flagged",
        "scripts/audit_x.py",
        (
            "from src.backend.models import FrameworkNode\n"
            "for n in db.query(FrameworkNode).all():\n"
            "    if n.description == expected:\n"
            "        print(n.status)\n"
        ),
        False,
    ),
    (
        "UPDATE framework_nodes SET title only (no surface col) -> NOT flagged",
        "scripts/seed_x.py",
        (
            "conn.execute('UPDATE framework_nodes SET title = ? WHERE id = ?', (t, 1))\n"
        ),
        False,
    ),
    (
        "Non-scripts path with a surface write -> OUT OF SCOPE (not flagged)",
        "src/backend/routers/framework.py",
        (
            "node.description = body\n"
            "node.status = 'mastered'\n"
        ),
        False,
    ),
    (
        "Non-.py file -> not flagged",
        "scripts/notes.md",
        "UPDATE framework_nodes SET description = x\n",
        False,
    ),
    (
        "INSERT INTO framework_nodes with description column -> WARN",
        "scripts/seed_new_node.py",
        (
            "conn.execute('INSERT INTO framework_nodes (path, description) VALUES (?, ?)',\n"
            "    ('a/b', desc))\n"
        ),
        True,
    ),
]


def run_self_test() -> int:
    failures = []
    for label, fp, src, expect_offending in TEST_CASES:
        offending, findings = evaluate_source(fp, src)
        ok = (offending == expect_offending)
        status = "PASS" if ok else "FAIL"
        print("[" + status + "] " + label)
        if findings:
            for f in findings:
                print("    " + f)
        if not ok:
            failures.append(label + " (got offending=" + str(offending)
                             + ", expected " + str(expect_offending) + ")")
    print()
    total = len(TEST_CASES)
    if failures:
        print("FAILED: " + str(len(failures)) + "/" + str(total))
        for f in failures:
            print("  - " + f)
        return 2
    print("PASSED: " + str(total) + "/" + str(total))
    return 0


def main(argv) -> int:
    init_utf8_streams()
    parser = argparse.ArgumentParser(prog="description_progress_guard")
    parser.add_argument("--test", action="store_true", help="run self-tests")
    parser.add_argument("--scan", type=Path, help="back-test a single file (always exit 0)")
    parser.add_argument(
        "--sweep",
        nargs="?",
        const=Path("scripts"),
        type=Path,
        help="read-only offender report over .py under DIR (default scripts)",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="scan staged scripts/*.py (pre-commit wiring point; always exit 0)",
    )
    args = parser.parse_args(argv)

    if args.test:
        return run_self_test()
    if args.scan is not None:
        return run_scan(args.scan)
    if args.sweep is not None:
        return run_sweep(args.sweep)
    if args.staged:
        return run_staged()

    # No mode selected: print usage and exit 0 (never block; this is a scanner,
    # not a stdin PreToolUse hook -- settings.json wiring is Phase B / T-P1-917).
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
