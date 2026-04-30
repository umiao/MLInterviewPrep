"""PreToolUse hook: forbid SQL writes in scripts/migrations/*.py (Invariant 3)
and flag schedule-shaped prose writes that target company_documents.content
(Invariant-3 EXTENSION; T-P0-660b).

Invariant 3 (CLAUDE.md): every DB content row must have a git-tracked, idempotent
seed script as its source of truth. scripts/migrations/* must NOT perform direct
INSERT/UPDATE/DELETE/REPLACE against data/*.db -- find or extend the owning
seed_*.py script instead.

Detection is AST-based to catch all three SQL-write forms cited in T-P0-660:
  (i)  raw string:   cur.execute("INSERT INTO data ...")
  (ii) f-string:     cur.execute(f"INSERT INTO {table} ...")
  (iii) executemany: cur.executemany("INSERT INTO ...", rows)

Schedule-prose extension (T-P0-660b -- see logs/2026-04-30_pinterest_root_cause.md
recommendation (b)): block writes whose Python source contains BOTH a full ISO-8601
timestamp AND an interviewer-name-shaped phrase within ~30 lines of each other,
when the file also writes to the `company_documents` table. Schedule data lives
in `interview_events` (Dashboard InterviewTimeline widget); use
scripts/_add_<company>_<date>.py with canonical key
(company_id, scheduled_at, interviewer_name).

Modes:
  (default)            PreToolUse hook (reads JSON from stdin, blocks via stdout JSON + exit 2)
  --test               Run built-in self-test cases; exit 0 on pass, 2 on fail.
  --scan PATH          Read PATH from disk and report whether it would block (back-test mode).
  --sweep [DIR]        Scan all .py under DIR (default scripts/migrations) and report findings.
  --scan-prose [DIR]   False-positive sweep for the schedule-prose detector across .py
                       files under DIR (default scripts/) -- read-only; reports flags.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_utils import init_utf8_streams, safe_read_stdin  # noqa: E402

SQL_WRITE_RX = re.compile(
    r"\b(INSERT\s+INTO|UPDATE\s+\w+|DELETE\s+FROM|REPLACE\s+INTO)\b",
    re.IGNORECASE,
)

EXEMPT_RX = re.compile(r"^\s*#\s*INVARIANT-3-EXEMPT:")

EXEC_METHODS = ("execute", "executemany", "executescript")

VIOLATION_BANNER = (
    "[INVARIANT-3 VIOLATION] scripts/migrations/* must not write to the DB.\n"
    "Source-of-truth is scripts/seed_*.py. Find the seed that owns this row\n"
    "type and edit/extend it, then re-run the seed. See LESSONS.md 2026-04-30\n"
    "Invariant-3 entry and the /dashboard skill for widget->seed mapping.\n"
    "Escape hatch: add '# INVARIANT-3-EXEMPT: <reason>' as the first line."
)


def is_migration_path(file_path: str) -> bool:
    """True iff file_path is a Python file under scripts/migrations/."""
    if not file_path:
        return False
    p = file_path.replace("\\", "/").lower()
    if not p.endswith(".py"):
        return False
    return ("/scripts/migrations/" in p) or p.startswith("scripts/migrations/")


def has_exempt_marker(source: str) -> bool:
    """True iff first non-blank line is '# INVARIANT-3-EXEMPT: <reason>'."""
    for line in source.splitlines():
        if line.strip() == "":
            continue
        return bool(EXEMPT_RX.match(line))
    return False


def _string_payload(node):
    """If node is a Constant str or f-string, return (kind, assembled_text)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return ("raw string", node.value)
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            elif isinstance(v, ast.FormattedValue):
                parts.append("{?}")
        return ("f-string", "".join(parts))
    return None


def _build_parent_map(tree):
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    return parents


def _enclosing_exec_method(node, parents):
    """Walk up parents; if a Call ancestor's .func.attr is in EXEC_METHODS, return it."""
    cur = parents.get(node)
    while cur is not None:
        if (
            isinstance(cur, ast.Call)
            and isinstance(cur.func, ast.Attribute)
            and cur.func.attr in EXEC_METHODS
        ):
            return cur.func.attr
        cur = parents.get(cur)
    return None


def find_sql_write_violations(source: str):
    """Return human-readable violation messages, or [] if clean."""
    violations = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        for m in SQL_WRITE_RX.finditer(source):
            line = source.count("\n", 0, m.start()) + 1
            violations.append(
                "line " + str(line) + ": SQL-write keyword " + repr(m.group(0))
                + " (unparseable file, regex fallback)"
            )
        return violations

    parents = _build_parent_map(tree)

    seen_lines = set()
    for node in ast.walk(tree):
        payload = _string_payload(node)
        if payload is None:
            continue
        kind, text = payload
        if not text:
            continue
        m = SQL_WRITE_RX.search(text)
        if not m:
            continue
        line = getattr(node, "lineno", 0)
        if line in seen_lines:
            continue
        seen_lines.add(line)
        method = _enclosing_exec_method(node, parents)
        form = kind
        if method == "executemany":
            form = "executemany"
        first_nonblank = next((ln for ln in text.splitlines() if ln.strip()), "")
        preview = first_nonblank[:80]
        method_tag = " -> ." + method + "()" if method else ""
        violations.append(
            "line " + str(line) + ": SQL-write " + form + method_tag
            + ": " + m.group(0).upper() + " | " + repr(preview)
        )

    return violations


_BASH_MIG_RX = re.compile(
    # Require an invocation token before the path so heredoc text containing the
    # path does not trigger. Matches: `python ... scripts/migrations/x.py`,
    # `bash scripts/migrations/x.py`, `./scripts/migrations/x.py`.
    r"(?:(?:python\S*|bash|sh)\s+(?:-\S+\s+)*|\./)['\"]?(scripts[/\\]migrations[/\\][\w._-]+\.py)\b",
    re.IGNORECASE,
)


def extract_bash_migration_files(command: str):
    """Return paths of scripts/migrations/*.py files actually invoked by a Bash command.

    Only flags when the path is preceded by an invocation token (python/bash/sh/./).
    Mere mention of the path in a heredoc body or string is NOT flagged.
    """
    if not command:
        return []
    out = []
    for m in _BASH_MIG_RX.finditer(command):
        out.append(Path(m.group(1)))
    return out


def evaluate_source(file_path: str, source: str):
    """Return (block, violations) for a Python source string."""
    if not is_migration_path(file_path):
        return (False, [])
    if has_exempt_marker(source):
        return (False, [])
    violations = find_sql_write_violations(source)
    return (bool(violations), violations)


def format_block_message(file_path: str, violations):
    body = "\n".join("  - " + v for v in violations)
    return VIOLATION_BANNER + "\n\nFile: " + file_path + "\nFindings:\n" + body


def _emit_block(file_path, violations):
    msg = format_block_message(file_path, violations)
    print(msg, file=sys.stderr)
    print(json.dumps({"decision": "block", "reason": msg}))
    sys.exit(2)


def hook_main(hook_input):
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        source = tool_input.get("content", "") or ""

        # Detector 1: SQL writes in scripts/migrations/* (Invariant 3 enforcement).
        if is_migration_path(file_path):
            block, violations = evaluate_source(file_path, source)
            if block:
                _emit_block(file_path, violations)

        # Detector 2: Schedule-shaped prose targeting company_documents (T-P0-660b).
        block_p, findings_p = evaluate_schedule_prose(file_path, source, source)
        if block_p:
            _emit_schedule_block(file_path, findings_p)

        sys.exit(0)

    if tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        new_string = tool_input.get("new_string", "") or ""

        # Read disk for the existing file so we can (a) check the exempt marker
        # and (b) infer SQL target table when new_string alone is a fragment.
        try:
            disk_text = Path(file_path).read_text(encoding="utf-8")
        except OSError:
            disk_text = ""

        # Detector 1: migrations SQL writes -- behavior unchanged.
        if (
            is_migration_path(file_path)
            and find_sql_write_violations(new_string)
            and not has_exempt_marker(disk_text)
        ):
            block, violations = evaluate_source(file_path, new_string)
            if block:
                _emit_block(file_path, violations)

        # Detector 2: schedule prose targeting company_documents.
        # Use disk_text + new_string as the table-inference source so the
        # detector can see SQL writes that live elsewhere in the file.
        full_after_edit = disk_text + "\n" + new_string if disk_text else new_string
        block_p, findings_p = evaluate_schedule_prose(
            file_path, new_string, full_after_edit
        )
        if block_p:
            _emit_schedule_block(file_path, findings_p)

        sys.exit(0)

    if tool_name == "Bash":
        command = tool_input.get("command", "") or ""
        for mig_path in extract_bash_migration_files(command):
            try:
                source = mig_path.read_text(encoding="utf-8")
            except OSError:
                continue
            block, violations = evaluate_source(str(mig_path), source)
            if block:
                _emit_block(str(mig_path), violations)
        sys.exit(0)

    sys.exit(0)


# ---------------------------------------------------------------------------
# Schedule-prose detector (T-P0-660b)
# ---------------------------------------------------------------------------
# Co-occurrence rule (matches AC2 of T-P0-663):
#   (i)  full ISO-8601 timestamp pattern (YYYY-MM-DD with optional time), AND
#   (ii) interviewer-name-shaped phrase ("Day N R N", "Round N with X",
#        "Interviewer: X", "with FirstName LastName"),
#   within SCHEDULE_PROSE_WINDOW lines of each other,
#   AND the file also writes to the `company_documents` SQL table.
#
# When all three conditions hold, the write is the T-P0-651 misdirection
# pattern (schedule data being prose-attached to a study doc) and is blocked.
# See logs/2026-04-30_pinterest_root_cause.md recommendation (b).

ISO_8601_RX = re.compile(
    r"\b\d{4}-\d{2}-\d{2}"
    r"(?:[T ]\d{2}:\d{2}(?::\d{2})?)?"
    r"\b",
)

INTERVIEWER_NAME_RX = re.compile(
    r"(?:"
    r"\bRound\s+\d+\s+with\s+[A-Z]"
    r"|\bDay\s+\d+\s+R\d+\b"
    r"|\bInterviewer\s*:\s*[A-Z]"
    r"|\bwith\s+[A-Z][a-z]+\s+[A-Z][a-z]+"
    r")",
)

TABLE_WRITE_RX = re.compile(
    r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM|REPLACE\s+INTO)\s+(\w+)",
    re.IGNORECASE,
)

CD_TABLE = "company_documents"
SCHEDULE_PROSE_WINDOW = 30

# Path-exemption regex for the canonical interview_events seed convention.
# Files like scripts/_add_pinterest_vo_2026-05-05_06.py are by convention
# interview_events seed scripts, even when their bodies contain rich schedule
# prose. Exempting them via path keeps AC2(c) green even when AST/regex
# analysis cannot fully trace the write target.
EVENT_SEED_PATH_RX = re.compile(
    r"(?:^|/)scripts/_add_[\w.-]+\.py$",
    re.IGNORECASE,
)

SCHEDULE_PROSE_BANNER = (
    "[INVARIANT-3 EXTENSION] Schedule-shaped prose detected in a write that\n"
    "targets company_documents.content. Schedule data lives in interview_events\n"
    "(Dashboard InterviewTimeline widget). Use scripts/_add_<company>_<date>.py\n"
    "with canonical key (company_id, scheduled_at, interviewer_name).\n"
    "See logs/2026-04-30_pinterest_root_cause.md recommendation (b).\n"
    "Escape hatch: add '# INVARIANT-3-EXEMPT: <reason>' as the first line."
)


def is_event_seed_path(file_path: str) -> bool:
    """True iff file_path matches the scripts/_add_*.py interview_events convention."""
    if not file_path:
        return False
    p = file_path.replace("\\", "/")
    return bool(EVENT_SEED_PATH_RX.search(p))


def detect_target_tables(source: str) -> set:
    """Return the lowercase set of table names that `source` writes to via SQL."""
    return {m.group(1).lower() for m in TABLE_WRITE_RX.finditer(source)}


def _line_indices_with_match(source: str, rx) -> list:
    """Return list of (1-indexed) line numbers where rx matches the line."""
    hits = []
    for i, line in enumerate(source.splitlines(), start=1):
        if rx.search(line):
            hits.append(i)
    return hits


def detect_schedule_prose(source: str, window: int = SCHEDULE_PROSE_WINDOW) -> list:
    """Return human-readable findings when ISO-8601 + interviewer-name shapes
    co-occur within `window` lines. Empty list = no co-occurrence detected.
    """
    iso_lines = _line_indices_with_match(source, ISO_8601_RX)
    name_lines = _line_indices_with_match(source, INTERVIEWER_NAME_RX)
    if not iso_lines or not name_lines:
        return []
    findings = []
    seen_iso = set()
    for il in iso_lines:
        for nl in name_lines:
            if abs(il - nl) <= window and il not in seen_iso:
                findings.append(
                    "line " + str(il) + " (ISO-8601 timestamp) co-occurs with line "
                    + str(nl) + " (interviewer-name shape) within " + str(window) + " lines"
                )
                seen_iso.add(il)
                break
    return findings


def evaluate_schedule_prose(file_path, prose_source: str, full_file_source: str = None):
    """Return (block, findings).

    `prose_source` is what is being written (Write content, or Edit new_string).
    `full_file_source` is the eventual whole-file contents we should consult
    when inferring the SQL target table -- defaults to `prose_source`.
    """
    if not file_path:
        return (False, [])
    p = file_path.replace("\\", "/").lower()
    if not p.endswith(".py"):
        return (False, [])
    if is_event_seed_path(file_path):
        return (False, [])
    if has_exempt_marker(prose_source) or (
        full_file_source and has_exempt_marker(full_file_source)
    ):
        return (False, [])
    findings = detect_schedule_prose(prose_source)
    if not findings:
        return (False, [])
    table_source = full_file_source if full_file_source is not None else prose_source
    tables = detect_target_tables(table_source)
    if CD_TABLE not in tables:
        return (False, [])
    findings = list(findings) + [
        "target table includes " + CD_TABLE
        + " (full set: " + (", ".join(sorted(tables)) if tables else "<none>") + ")"
    ]
    return (True, findings)


def format_schedule_block_message(file_path: str, findings) -> str:
    body = "\n".join("  - " + f for f in findings)
    return SCHEDULE_PROSE_BANNER + "\n\nFile: " + file_path + "\nFindings:\n" + body


def _emit_schedule_block(file_path: str, findings) -> None:
    msg = format_schedule_block_message(file_path, findings)
    print(msg, file=sys.stderr)
    print(json.dumps({"decision": "block", "reason": msg}))
    sys.exit(2)



TEST_CASES = [
    (
        "raw INSERT in migrations file blocks",
        "scripts/migrations/foo.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('INSERT INTO problems (id, title) VALUES (1, \"x\")')\n"
        ),
        True,
    ),
    (
        "f-string INSERT in migrations file blocks",
        "scripts/migrations/foo.py",
        (
            "table = 'problems'\n"
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute(f'INSERT INTO {table} (id) VALUES (1)')\n"
        ),
        True,
    ),
    (
        "executemany INSERT in migrations file blocks",
        "scripts/migrations/foo.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.executemany('INSERT INTO problems VALUES (?, ?)', [(1, 'a'), (2, 'b')])\n"
        ),
        True,
    ),
    (
        "UPDATE in migrations file blocks",
        "scripts/migrations/bar.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('UPDATE problems SET title=? WHERE id=?', ('y', 1))\n"
        ),
        True,
    ),
    (
        "DELETE in migrations file blocks",
        "scripts/migrations/bar.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('DELETE FROM problems WHERE id=1')\n"
        ),
        True,
    ),
    (
        "Same body in scripts/seed_x.py is allowed (path-based exemption)",
        "scripts/seed_problems.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('INSERT INTO problems (id, title) VALUES (1, \"x\")')\n"
        ),
        False,
    ),
    (
        "Migrations file with INVARIANT-3-EXEMPT first line is allowed",
        "scripts/migrations/foo.py",
        (
            "# INVARIANT-3-EXEMPT: schema-only DDL plus DML reference seed for testing\n"
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('INSERT INTO problems (id) VALUES (1)')\n"
        ),
        False,
    ),
    (
        "Migrations file with no SQL writes is allowed (DDL-only)",
        "scripts/migrations/baz.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('CREATE TABLE IF NOT EXISTS foo (id INTEGER PRIMARY KEY)')\n"
            "conn.execute('SELECT id FROM foo')\n"
        ),
        False,
    ),
    (
        "Variable-stored SQL write in migrations is detected via literal scan",
        "scripts/migrations/var.py",
        (
            "import sqlite3\n"
            "sql = 'INSERT INTO problems VALUES (?)'\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute(sql, (1,))\n"
        ),
        True,
    ),
    (
        "Comment-only mention of INSERT is NOT flagged",
        "scripts/migrations/comment.py",
        (
            "# This file used to do INSERT INTO foo but now is DDL-only\n"
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "conn.execute('CREATE INDEX IF NOT EXISTS idx ON foo(id)')\n"
        ),
        False,
    ),
]


BASH_TEST_CASES = [
    ("python scripts/migrations/foo.py runs the file", "python scripts/migrations/foo.py", 1),
    ("python -u scripts/migrations/foo.py runs the file", "python -u scripts/migrations/foo.py", 1),
    ("bash scripts/migrations/foo.py runs the file", "bash scripts/migrations/foo.py", 1),
    ("./scripts/migrations/foo.py runs the file", "./scripts/migrations/foo.py arg", 1),
    (
        "heredoc body mentioning path is NOT extracted",
        "cat <<EOF\nsee scripts/migrations/foo.py for details\nEOF",
        0,
    ),
    (
        "echo of path in PROGRESS message is NOT extracted",
        "echo 'see scripts/migrations/foo.py for details'",
        0,
    ),
    (
        "two distinct invocations both extracted",
        "python scripts/migrations/a.py && python scripts/migrations/b.py",
        2,
    ),
]



SCHEDULE_PROSE_TEST_CASES = [
    (
        "AC2(a) BLOCK: T-P0-651 literal payload (schedule prose + company_documents target)",
        "scripts/migrations/update_pinterest_onsite_itinerary.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "body = (\n"
            "    'Pinterest VO Day 1 R1 -- ML Systems Design with Yiyang Zhang.\\n'\n"
            "    'Tuesday 2026-05-05 15:00 PDT.\\n'\n"
            "    'Day 1 R2 -- HM/Competency with Daniel Liu, 2026-05-05 16:00.\\n'\n"
            ")\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 83', (body,))\n"
        ),
        True,
    ),
    (
        "AC2(b) ALLOW: paper reference in company_documents content (single year, no schedule shape)",
        "scripts/seed_attention_paper_doc.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "body = 'The Transformer architecture was published in 2018 by Vaswani et al."
            " It introduced multi-head self-attention.'\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 1', (body,))\n"
        ),
        False,
    ),
    (
        "AC2(c) ALLOW: schedule prose in scripts/_add_pinterest_*.py targeting interview_events",
        "scripts/_add_pinterest_vo_2026-05-05_06.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "body = 'Pinterest VO Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00.'\n"
            "conn.execute('INSERT INTO interview_events (title, description, scheduled_at) VALUES (?, ?, ?)',\n"
            "    ('Pinterest VO Day 1 R1', body, '2026-05-05 15:00:00'))\n"
        ),
        False,
    ),
    (
        "AC2(d) BLOCK: scripts/seed_pinterest_*.py with schedule prose AND company_documents write",
        "scripts/seed_pinterest_misrouted.py",
        (
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "body = 'Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00 PDT.'\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 83', (body,))\n"
        ),
        True,
    ),
    (
        "Schedule prose in script with NO target table is NOT blocked (insufficient signal)",
        "scripts/_smoke_print_schedule.py",
        (
            "body = 'Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00.'\n"
            "print(body)\n"
        ),
        False,
    ),
    (
        "INVARIANT-3-EXEMPT marker disables schedule-prose detection too",
        "scripts/seed_one_off_schedule_doc.py",
        (
            "# INVARIANT-3-EXEMPT: legacy import with embedded schedule context\n"
            "import sqlite3\n"
            "conn = sqlite3.connect('data/mle_prep.db')\n"
            "body = 'Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00.'\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 1', (body,))\n"
        ),
        False,
    ),
    (
        "Non-Python target (.md) with schedule prose is NOT flagged (out of scope)",
        "docs/notes/uber_vo_recap.md",
        (
            "Day 1 R1 -- ML Systems Design with Yiyang Zhang.\n"
            "Date: 2026-05-05 15:00 PDT.\n"
        ),
        False,
    ),
]

def run_self_test():
    failures = []
    for label, fp, src, expect_block in TEST_CASES:
        block, violations = evaluate_source(fp, src)
        ok = (block == expect_block)
        status = "PASS" if ok else "FAIL"
        print("[" + status + "] " + label)
        if violations:
            for v in violations:
                print("    " + v)
        if not ok:
            failures.append(label)
    print()
    print("--- Bash command extraction ---")
    for label, cmd, expect_count in BASH_TEST_CASES:
        got = extract_bash_migration_files(cmd)
        ok = (len(got) == expect_count)
        status = "PASS" if ok else "FAIL"
        print("[" + status + "] " + label + " (got " + str(len(got)) + ", expected " + str(expect_count) + ")")
        if not ok:
            failures.append(label)
    print()
    print("--- Schedule-prose detector (T-P0-660b) ---")
    for label, fp, src, expect_block in SCHEDULE_PROSE_TEST_CASES:
        block, findings = evaluate_schedule_prose(fp, src, src)
        ok = (block == expect_block)
        status = "PASS" if ok else "FAIL"
        print("[" + status + "] " + label)
        if findings:
            for f in findings:
                print("    " + f)
        if not ok:
            failures.append(label)
    print()
    total = len(TEST_CASES) + len(BASH_TEST_CASES) + len(SCHEDULE_PROSE_TEST_CASES)
    if failures:
        print("FAILED: " + str(len(failures)) + "/" + str(total))
        for f in failures:
            print("  - " + f)
        return 2
    print("PASSED: " + str(total) + "/" + str(total))
    return 0


def run_scan(target):
    try:
        source = target.read_text(encoding="utf-8")
    except OSError as exc:
        print("[SCAN-ERR] cannot read " + str(target) + ": " + str(exc), file=sys.stderr)
        return 1
    block, violations = evaluate_source(str(target), source)
    if block:
        print(format_block_message(str(target), violations))
        return 2
    print("[CLEAN] " + str(target))
    if violations:
        for v in violations:
            print("  (info) " + v)
    return 0


def run_sweep(root):
    if not root.exists():
        print("[SWEEP] no such directory: " + str(root))
        return 0
    files = sorted(p for p in root.rglob("*.py"))
    block_count = 0
    clean_count = 0
    exempt_count = 0
    print("[SWEEP] scanning " + str(len(files)) + " .py file(s) under " + str(root) + "\n")
    for f in files:
        try:
            source = f.read_text(encoding="utf-8")
        except OSError as exc:
            print("  [SKIP] " + str(f) + ": " + str(exc))
            continue
        if has_exempt_marker(source):
            exempt_count += 1
            print("  [EXEMPT] " + str(f))
            continue
        violations = find_sql_write_violations(source)
        if violations:
            block_count += 1
            print("  [BLOCK] " + str(f))
            for v in violations:
                print("           - " + v)
        else:
            clean_count += 1
            print("  [CLEAN] " + str(f))
    print(
        "\n[SWEEP] summary: " + str(clean_count) + " clean, "
        + str(block_count) + " block, " + str(exempt_count) + " exempt, total "
        + str(len(files))
    )
    return 2 if block_count > 0 else 0



def run_scan_prose(root: Path) -> int:
    """False-positive sweep: scan all .py under root for schedule-prose flags.

    Read-only. Reports flags but always exits 0 (informational sweep).
    """
    if not root.exists():
        print("[SCAN-PROSE] no such directory: " + str(root))
        return 0
    files = sorted(p for p in root.rglob("*.py"))
    flag_count = 0
    clean_count = 0
    print("[SCAN-PROSE] scanning " + str(len(files)) + " .py file(s) under " + str(root) + "\n")
    for f in files:
        try:
            source = f.read_text(encoding="utf-8")
        except OSError as exc:
            print("  [SKIP] " + str(f) + ": " + str(exc))
            continue
        block, findings = evaluate_schedule_prose(str(f), source, source)
        if block:
            flag_count += 1
            print("  [FLAG] " + str(f))
            for finding in findings:
                print("           - " + finding)
        else:
            clean_count += 1
    print(
        "\n[SCAN-PROSE] summary: " + str(clean_count) + " clean, "
        + str(flag_count) + " flagged, total " + str(len(files))
    )
    return 0

def main(argv):
    init_utf8_streams()
    parser = argparse.ArgumentParser(prog="invariant3_guard")
    parser.add_argument("--test", action="store_true", help="run self-tests")
    parser.add_argument("--scan", type=Path, help="scan a single file (back-test mode)")
    parser.add_argument(
        "--sweep",
        nargs="?",
        const=Path("scripts/migrations"),
        type=Path,
        help="scan all .py under directory (default scripts/migrations)",
    )
    parser.add_argument(
        "--scan-prose",
        nargs="?",
        const=Path("scripts"),
        type=Path,
        dest="scan_prose",
        help="schedule-prose FP sweep across .py under directory (default scripts)",
    )
    args = parser.parse_args(argv)

    if args.test:
        return run_self_test()
    if args.scan is not None:
        return run_scan(args.scan)
    if args.sweep is not None:
        return run_sweep(args.sweep)
    if args.scan_prose is not None:
        return run_scan_prose(args.scan_prose)

    hook_input = safe_read_stdin("invariant3_guard")
    if hook_input is None:
        return 0
    try:
        hook_main(hook_input)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0
    except Exception as exc:
        print("[HOOK ERROR] invariant3_guard: " + str(exc), file=sys.stderr)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
