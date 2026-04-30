# INVARIANT-3-EXEMPT: hook-editor script; test-case payloads contain the schedule-prose patterns intentionally and the script does not write to the DB.
"""One-off edit: extend .claude/hooks/invariant3_guard.py with the schedule-prose
detector (T-P0-660b). Idempotent: re-running detects existing extension and
no-ops with a clear message. Writes the modified hook back via UTF-8.

Edits performed:
  1. Replace top-of-file docstring with the extended version that mentions the
     new detector and --scan-prose mode.
  2. Insert new constants/functions for schedule-prose detection just before
     the existing TEST_CASES list.
  3. Insert new schedule-prose calls into hook_main() for Write and Edit,
     alongside the existing migrations-SQL detector.
  4. Append SCHEDULE_PROSE_TEST_CASES list.
  5. Update run_self_test() to also run the schedule-prose cases.
  6. Add --scan-prose mode to argparse + main() dispatcher.
"""
from __future__ import annotations

import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "invariant3_guard.py"

OLD_DOCSTRING = '''"""PreToolUse hook: forbid SQL writes in scripts/migrations/*.py (Invariant 3).

Invariant 3 (CLAUDE.md): every DB content row must have a git-tracked, idempotent
seed script as its source of truth. scripts/migrations/* must NOT perform direct
INSERT/UPDATE/DELETE/REPLACE against data/*.db -- find or extend the owning
seed_*.py script instead.

Detection is AST-based to catch all three SQL-write forms cited in T-P0-660:
  (i)  raw string:   cur.execute("INSERT INTO data ...")
  (ii) f-string:     cur.execute(f"INSERT INTO {table} ...")
  (iii) executemany: cur.executemany("INSERT INTO ...", rows)

Modes:
  (default)        PreToolUse hook (reads JSON from stdin, blocks via stdout JSON + exit 2)
  --test           Run built-in self-test cases; exit 0 on pass, 2 on fail.
  --scan PATH      Read PATH from disk and report whether it would block (back-test mode).
  --sweep [DIR]    Scan all .py under DIR (default scripts/migrations) and report findings.
"""'''

NEW_DOCSTRING = '''"""PreToolUse hook: forbid SQL writes in scripts/migrations/*.py (Invariant 3)
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
"""'''


SCHEDULE_PROSE_BLOCK = '''
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
    r"\\b\\d{4}-\\d{2}-\\d{2}"
    r"(?:[T ]\\d{2}:\\d{2}(?::\\d{2})?)?"
    r"\\b",
)

INTERVIEWER_NAME_RX = re.compile(
    r"(?:"
    r"\\bRound\\s+\\d+\\s+with\\s+[A-Z]"
    r"|\\bDay\\s+\\d+\\s+R\\d+\\b"
    r"|\\bInterviewer\\s*:\\s*[A-Z]"
    r"|\\bwith\\s+[A-Z][a-z]+\\s+[A-Z][a-z]+"
    r")",
)

TABLE_WRITE_RX = re.compile(
    r"\\b(?:INSERT\\s+INTO|UPDATE|DELETE\\s+FROM|REPLACE\\s+INTO)\\s+(\\w+)",
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
    r"(?:^|/)scripts/_add_[\\w.-]+\\.py$",
    re.IGNORECASE,
)

SCHEDULE_PROSE_BANNER = (
    "[INVARIANT-3 EXTENSION] Schedule-shaped prose detected in a write that\\n"
    "targets company_documents.content. Schedule data lives in interview_events\\n"
    "(Dashboard InterviewTimeline widget). Use scripts/_add_<company>_<date>.py\\n"
    "with canonical key (company_id, scheduled_at, interviewer_name).\\n"
    "See logs/2026-04-30_pinterest_root_cause.md recommendation (b).\\n"
    "Escape hatch: add '# INVARIANT-3-EXEMPT: <reason>' as the first line."
)


def is_event_seed_path(file_path: str) -> bool:
    """True iff file_path matches the scripts/_add_*.py interview_events convention."""
    if not file_path:
        return False
    p = file_path.replace("\\\\", "/")
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
    p = file_path.replace("\\\\", "/").lower()
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
    body = "\\n".join("  - " + f for f in findings)
    return SCHEDULE_PROSE_BANNER + "\\n\\nFile: " + file_path + "\\nFindings:\\n" + body


def _emit_schedule_block(file_path: str, findings) -> None:
    msg = format_schedule_block_message(file_path, findings)
    print(msg, file=sys.stderr)
    print(json.dumps({"decision": "block", "reason": msg}))
    sys.exit(2)


'''


OLD_HOOK_MAIN = '''def hook_main(hook_input):
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        if not is_migration_path(file_path):
            sys.exit(0)
        source = tool_input.get("content", "") or ""
        block, violations = evaluate_source(file_path, source)
        if block:
            _emit_block(file_path, violations)
        sys.exit(0)

    if tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        if not is_migration_path(file_path):
            sys.exit(0)
        new_string = tool_input.get("new_string", "") or ""
        if find_sql_write_violations(new_string):
            try:
                disk_text = Path(file_path).read_text(encoding="utf-8")
            except OSError:
                disk_text = ""
            if has_exempt_marker(disk_text):
                sys.exit(0)
            block, violations = evaluate_source(file_path, new_string)
            if block:
                _emit_block(file_path, violations)
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

    sys.exit(0)'''


NEW_HOOK_MAIN = '''def hook_main(hook_input):
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
        if is_migration_path(file_path):
            if find_sql_write_violations(new_string):
                if not has_exempt_marker(disk_text):
                    block, violations = evaluate_source(file_path, new_string)
                    if block:
                        _emit_block(file_path, violations)

        # Detector 2: schedule prose targeting company_documents.
        # Use disk_text + new_string as the table-inference source so the
        # detector can see SQL writes that live elsewhere in the file.
        full_after_edit = disk_text + "\\n" + new_string if disk_text else new_string
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

    sys.exit(0)'''


SCHEDULE_PROSE_TEST_BLOCK = '''

SCHEDULE_PROSE_TEST_CASES = [
    (
        "AC2(a) BLOCK: T-P0-651 literal payload (schedule prose + company_documents target)",
        "scripts/migrations/update_pinterest_onsite_itinerary.py",
        (
            "import sqlite3\\n"
            "conn = sqlite3.connect('data/mle_prep.db')\\n"
            "body = (\\n"
            "    'Pinterest VO Day 1 R1 -- ML Systems Design with Yiyang Zhang.\\\\n'\\n"
            "    'Tuesday 2026-05-05 15:00 PDT.\\\\n'\\n"
            "    'Day 1 R2 -- HM/Competency with Daniel Liu, 2026-05-05 16:00.\\\\n'\\n"
            ")\\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 83', (body,))\\n"
        ),
        True,
    ),
    (
        "AC2(b) ALLOW: paper reference in company_documents content (single year, no schedule shape)",
        "scripts/seed_attention_paper_doc.py",
        (
            "import sqlite3\\n"
            "conn = sqlite3.connect('data/mle_prep.db')\\n"
            "body = 'The Transformer architecture was published in 2018 by Vaswani et al."
            " It introduced multi-head self-attention.'\\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 1', (body,))\\n"
        ),
        False,
    ),
    (
        "AC2(c) ALLOW: schedule prose in scripts/_add_pinterest_*.py targeting interview_events",
        "scripts/_add_pinterest_vo_2026-05-05_06.py",
        (
            "import sqlite3\\n"
            "conn = sqlite3.connect('data/mle_prep.db')\\n"
            "body = 'Pinterest VO Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00.'\\n"
            "conn.execute('INSERT INTO interview_events (title, description, scheduled_at) VALUES (?, ?, ?)',\\n"
            "    ('Pinterest VO Day 1 R1', body, '2026-05-05 15:00:00'))\\n"
        ),
        False,
    ),
    (
        "AC2(d) BLOCK: scripts/seed_pinterest_*.py with schedule prose AND company_documents write",
        "scripts/seed_pinterest_misrouted.py",
        (
            "import sqlite3\\n"
            "conn = sqlite3.connect('data/mle_prep.db')\\n"
            "body = 'Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00 PDT.'\\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 83', (body,))\\n"
        ),
        True,
    ),
    (
        "Schedule prose in script with NO target table is NOT blocked (insufficient signal)",
        "scripts/_smoke_print_schedule.py",
        (
            "body = 'Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00.'\\n"
            "print(body)\\n"
        ),
        False,
    ),
    (
        "INVARIANT-3-EXEMPT marker disables schedule-prose detection too",
        "scripts/seed_one_off_schedule_doc.py",
        (
            "# INVARIANT-3-EXEMPT: legacy import with embedded schedule context\\n"
            "import sqlite3\\n"
            "conn = sqlite3.connect('data/mle_prep.db')\\n"
            "body = 'Day 1 R1 -- ML Systems Design with Yiyang Zhang. 2026-05-05 15:00.'\\n"
            "conn.execute('UPDATE company_documents SET content = ? WHERE id = 1', (body,))\\n"
        ),
        False,
    ),
    (
        "Non-Python target (.md) with schedule prose is NOT flagged (out of scope)",
        "docs/notes/uber_vo_recap.md",
        (
            "Day 1 R1 -- ML Systems Design with Yiyang Zhang.\\n"
            "Date: 2026-05-05 15:00 PDT.\\n"
        ),
        False,
    ),
]
'''


OLD_RUN_SELF_TEST_FOOTER = '''    print()
    print("--- Bash command extraction ---")
    for label, cmd, expect_count in BASH_TEST_CASES:
        got = extract_bash_migration_files(cmd)
        ok = (len(got) == expect_count)
        status = "PASS" if ok else "FAIL"
        print("[" + status + "] " + label + " (got " + str(len(got)) + ", expected " + str(expect_count) + ")")
        if not ok:
            failures.append(label)
    print()
    total = len(TEST_CASES) + len(BASH_TEST_CASES)
    if failures:
        print("FAILED: " + str(len(failures)) + "/" + str(total))
        for f in failures:
            print("  - " + f)
        return 2
    print("PASSED: " + str(total) + "/" + str(total))
    return 0'''


NEW_RUN_SELF_TEST_FOOTER = '''    print()
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
    return 0'''


SCAN_PROSE_FUNC_BLOCK = '''

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
    print("[SCAN-PROSE] scanning " + str(len(files)) + " .py file(s) under " + str(root) + "\\n")
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
        "\\n[SCAN-PROSE] summary: " + str(clean_count) + " clean, "
        + str(flag_count) + " flagged, total " + str(len(files))
    )
    return 0
'''


OLD_MAIN_BODY = '''def main(argv):
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
    args = parser.parse_args(argv)

    if args.test:
        return run_self_test()
    if args.scan is not None:
        return run_scan(args.scan)
    if args.sweep is not None:
        return run_sweep(args.sweep)'''


NEW_MAIN_BODY = '''def main(argv):
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
        return run_scan_prose(args.scan_prose)'''


def main() -> int:
    src = HOOK.read_text(encoding="utf-8")

    # Idempotency check: if extension marker already present, no-op.
    if "Schedule-prose detector (T-P0-660b)" in src:
        print("[NO-OP] schedule-prose extension already present; nothing to do.")
        return 0

    # 1. Replace docstring.
    if OLD_DOCSTRING not in src:
        print("[FAIL] expected old docstring not found", file=sys.stderr)
        return 1
    src = src.replace(OLD_DOCSTRING, NEW_DOCSTRING, 1)

    # 2. Insert schedule-prose constants/functions just before TEST_CASES.
    test_cases_anchor = "\nTEST_CASES = ["
    if test_cases_anchor not in src:
        print("[FAIL] TEST_CASES anchor not found", file=sys.stderr)
        return 1
    src = src.replace(
        test_cases_anchor,
        SCHEDULE_PROSE_BLOCK + test_cases_anchor,
        1,
    )

    # 3. Replace hook_main with the dual-detector version.
    if OLD_HOOK_MAIN not in src:
        print("[FAIL] old hook_main body not found", file=sys.stderr)
        return 1
    src = src.replace(OLD_HOOK_MAIN, NEW_HOOK_MAIN, 1)

    # 4. Append SCHEDULE_PROSE_TEST_CASES after BASH_TEST_CASES, before run_self_test.
    run_self_test_anchor = "\ndef run_self_test():"
    if run_self_test_anchor not in src:
        print("[FAIL] run_self_test anchor not found", file=sys.stderr)
        return 1
    src = src.replace(
        run_self_test_anchor,
        SCHEDULE_PROSE_TEST_BLOCK + run_self_test_anchor,
        1,
    )

    # 5. Update run_self_test footer to include schedule-prose cases.
    if OLD_RUN_SELF_TEST_FOOTER not in src:
        print("[FAIL] run_self_test footer not found", file=sys.stderr)
        return 1
    src = src.replace(OLD_RUN_SELF_TEST_FOOTER, NEW_RUN_SELF_TEST_FOOTER, 1)

    # 6. Append run_scan_prose function before main().
    main_anchor = "\ndef main(argv):"
    if main_anchor not in src:
        print("[FAIL] main(argv) anchor not found", file=sys.stderr)
        return 1
    src = src.replace(
        main_anchor,
        SCAN_PROSE_FUNC_BLOCK + main_anchor,
        1,
    )

    # 7. Update main() argparse + dispatcher.
    if OLD_MAIN_BODY not in src:
        print("[FAIL] old main() body not found", file=sys.stderr)
        return 1
    src = src.replace(OLD_MAIN_BODY, NEW_MAIN_BODY, 1)

    HOOK.write_text(src, encoding="utf-8")
    print("[OK] extended " + str(HOOK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
