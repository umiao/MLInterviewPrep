"""T-P0-675 / T-P0-735: Audit drawer URI consistency in company_documents.content.

Markdown drawer links inside `company_documents.content` use three schemes:
  - `db://N`     -- ProblemDrawer target; N must reference `problems.id`
  - `cd://N`     -- CompanyDocDrawer target; N must reference `company_documents.id`
  - `sd://<slug>` -- SystemDesignDrawer target; slug must reference
                    `system_designs.slug` (string-keyed, not numeric)

Because `problems` and `company_documents` are independent auto-increment tables,
the same numeric N can validly exist in BOTH tables. The URI scheme is the ONLY
disambiguator for db:// vs cd://. This audit scans every doc, extracts every
link of each scheme, and verifies the target row exists in the correct table.

For `sd://` cross-table confusion is physically impossible: `system_designs.slug`
is a string slug while `problems.id` / `company_documents.id` are integers. The
sd:// audit therefore only emits VALID or ERROR (dangling), never WARNING.

Outputs three result classes per (doc, link):
  - VALID   -- target found in the expected table.
  - WARNING -- (db:// / cd:// only) target found in expected table, but ALSO
               exists in the other table; the URI scheme makes the resolver
               unambiguous, so this is informational, not an error.
  - ERROR   -- target NOT found in expected table. Sub-categorised:
               * cross-table corruption: `db://N` where N is missing from
                 `problems` but present in `company_documents` (link should
                 be `cd://N`).
               * cross-table corruption: `cd://N` where N is missing from
                 `company_documents` but present in `problems` (link should
                 be `db://N`).
               * dangling: target absent from the relevant table(s).

Exits 0 if zero ERRORs, 1 otherwise. CI-friendly. Wire into
`.github/workflows/ci.yml` as a separate job (see README -- the audit only
needs the SQLite DB checked out alongside seed scripts).

Usage:
  python scripts/audit_uri_consistency.py            # human-readable
  python scripts/audit_uri_consistency.py --json     # machine output
  python scripts/audit_uri_consistency.py --hub 82   # restrict to one doc id
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

DB_LINK_RE = re.compile(r"db://(\d+)")
CD_LINK_RE = re.compile(r"cd://(\d+)")
SD_LINK_RE = re.compile(r"sd://([a-z0-9-]+)")


@dataclass(frozen=True)
class Finding:
    """One audit finding for a single link in a single doc."""

    doc_id: int
    doc_title: str
    company_id: int
    scheme: str           # "db", "cd", or "sd"
    target_id: int | str  # int for db://N / cd://N; str slug for sd://slug
    severity: str         # "VALID", "WARNING", "ERROR"
    message: str


def _connect(db_path: Path) -> sqlite3.Connection:
    """Open the SQLite DB read-only (uri=True) for safety."""
    if not db_path.exists():
        raise SystemExit(f"[FATAL] db not found: {db_path}")
    conn = sqlite3.connect(
        f"file:{db_path}?mode=ro",
        uri=True,
    )
    conn.row_factory = sqlite3.Row
    return conn


def _existing_ids(conn: sqlite3.Connection, table: str) -> set[int]:
    """Return the set of all `id` values in `table`."""
    cur = conn.execute(f"SELECT id FROM {table}")
    return {row[0] for row in cur.fetchall()}


def _existing_slugs(conn: sqlite3.Connection, table: str, slug_col: str) -> set[str]:
    """Return the set of all `slug_col` values in `table`.

    Parallel to `_existing_ids` but for string-keyed catalogs (e.g.
    `system_designs.slug`). Identifiers must be statically known -- callers
    pass literal strings, never user input.
    """
    cur = conn.execute(f"SELECT {slug_col} FROM {table}")
    return {row[0] for row in cur.fetchall()}


def _scan_doc(
    *,
    doc_id: int,
    doc_title: str,
    company_id: int,
    content: str,
    problem_ids: set[int],
    doc_ids: set[int],
    sd_slugs: set[str],
    target_doc_id: int | None,
) -> list[Finding]:
    """Extract every db://, cd://, sd:// link from `content` and classify each."""
    if target_doc_id is not None and doc_id != target_doc_id:
        return []
    findings: list[Finding] = []

    for match in DB_LINK_RE.finditer(content):
        n = int(match.group(1))
        in_problems = n in problem_ids
        in_docs = n in doc_ids
        if in_problems and in_docs:
            findings.append(Finding(
                doc_id, doc_title, company_id, "db", n, "WARNING",
                f"ambiguous: db://{n} also exists in company_documents.id "
                f"(scheme treats it as problem -- correct, but flag for review)",
            ))
        elif in_problems:
            findings.append(Finding(
                doc_id, doc_title, company_id, "db", n, "VALID",
                f"problems.id={n} resolved",
            ))
        elif in_docs:
            findings.append(Finding(
                doc_id, doc_title, company_id, "db", n, "ERROR",
                f"cross-table corruption: db://{n} missing from problems but "
                f"present in company_documents -- should be cd://{n}",
            ))
        else:
            findings.append(Finding(
                doc_id, doc_title, company_id, "db", n, "ERROR",
                f"dangling: db://{n} not found in problems OR company_documents",
            ))

    for match in CD_LINK_RE.finditer(content):
        n = int(match.group(1))
        in_problems = n in problem_ids
        in_docs = n in doc_ids
        if in_docs and in_problems:
            findings.append(Finding(
                doc_id, doc_title, company_id, "cd", n, "WARNING",
                f"ambiguous: cd://{n} also exists in problems.id "
                f"(scheme treats it as company_document -- correct, but flag for review)",
            ))
        elif in_docs:
            findings.append(Finding(
                doc_id, doc_title, company_id, "cd", n, "VALID",
                f"company_documents.id={n} resolved",
            ))
        elif in_problems:
            findings.append(Finding(
                doc_id, doc_title, company_id, "cd", n, "ERROR",
                f"cross-table corruption: cd://{n} missing from company_documents "
                f"but present in problems -- should be db://{n}",
            ))
        else:
            findings.append(Finding(
                doc_id, doc_title, company_id, "cd", n, "ERROR",
                f"dangling: cd://{n} not found in company_documents OR problems",
            ))

    # sd://<slug> -- string-keyed system_designs catalog. Cross-table confusion
    # with db://N / cd://N is physically impossible because slug is a string
    # while problems.id / company_documents.id are integers; the only failure
    # mode is dangling (slug missing from system_designs because the row was
    # deleted or renamed).
    for match in SD_LINK_RE.finditer(content):
        slug = match.group(1)
        if slug in sd_slugs:
            findings.append(Finding(
                doc_id, doc_title, company_id, "sd", slug, "VALID",
                f"system_designs.slug={slug!r} resolved",
            ))
        else:
            findings.append(Finding(
                doc_id, doc_title, company_id, "sd", slug, "ERROR",
                f"dangling: sd://{slug} not found in system_designs.slug",
            ))

    return findings


def audit(db_path: Path, target_doc_id: int | None = None) -> list[Finding]:
    """Run the audit and return a flat list of findings (any severity)."""
    conn = _connect(db_path)
    try:
        problem_ids = _existing_ids(conn, "problems")
        doc_ids = _existing_ids(conn, "company_documents")
        sd_slugs = _existing_slugs(conn, "system_designs", "slug")
        cur = conn.execute(
            "SELECT id, title, company_id, content FROM company_documents"
        )
        all_findings: list[Finding] = []
        for row in cur.fetchall():
            all_findings.extend(_scan_doc(
                doc_id=row["id"],
                doc_title=row["title"],
                company_id=row["company_id"],
                content=row["content"] or "",
                problem_ids=problem_ids,
                doc_ids=doc_ids,
                sd_slugs=sd_slugs,
                target_doc_id=target_doc_id,
            ))
        return all_findings
    finally:
        conn.close()


def _print_summary(findings: Iterable[Finding]) -> tuple[int, int, int]:
    """Print one row per scanned hub (doc) with valid/warn/error counts."""
    by_doc: dict[tuple[int, str], dict[str, int]] = defaultdict(
        lambda: {"VALID": 0, "WARNING": 0, "ERROR": 0}
    )
    total_v = total_w = total_e = 0
    for f in findings:
        by_doc[(f.doc_id, f.doc_title)][f.severity] += 1
        if f.severity == "VALID":
            total_v += 1
        elif f.severity == "WARNING":
            total_w += 1
        elif f.severity == "ERROR":
            total_e += 1
    if not by_doc:
        print("[INFO] no db://, cd://, or sd:// links found in any company_documents.")
        return total_v, total_w, total_e

    print("=" * 88)
    print(
        f"{'doc_id':>6}  {'valid':>5}  {'warn':>4}  {'err':>3}  title"
    )
    print("-" * 88)
    for (doc_id, title), counts in sorted(by_doc.items()):
        title_short = title if len(title) <= 60 else title[:57] + "..."
        print(
            f"{doc_id:>6}  {counts['VALID']:>5}  {counts['WARNING']:>4}  "
            f"{counts['ERROR']:>3}  {title_short}"
        )
    print("-" * 88)
    print(f"TOTAL   {total_v:>5}  {total_w:>4}  {total_e:>3}")
    print("=" * 88)
    return total_v, total_w, total_e


def _print_errors(findings: Iterable[Finding]) -> None:
    """Print every ERROR-severity finding in detail."""
    errors = [f for f in findings if f.severity == "ERROR"]
    if not errors:
        return
    print("\n[ERROR] details:")
    for f in errors:
        print(
            f"  - doc_id={f.doc_id} ({f.doc_title!r}) "
            f"company_id={f.company_id} {f.scheme}://{f.target_id}: {f.message}"
        )


def _print_warnings(findings: Iterable[Finding], limit: int = 20) -> None:
    """Print up to `limit` WARNING-severity findings (ambiguous schemes)."""
    warns = [f for f in findings if f.severity == "WARNING"]
    if not warns:
        return
    print(f"\n[WARNING] {len(warns)} ambiguous links (scheme disambiguates correctly):")
    for f in warns[:limit]:
        print(
            f"  - doc_id={f.doc_id} ({f.doc_title!r}) "
            f"{f.scheme}://{f.target_id}: {f.message}"
        )
    if len(warns) > limit:
        print(f"  ... ({len(warns) - limit} more suppressed)")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    # Force UTF-8 on stdout/stderr so CJK doc titles don't crash on Windows cp1252.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help=f"path to SQLite DB (default: {DB_PATH})",
    )
    parser.add_argument(
        "--hub",
        type=int,
        default=None,
        help="restrict scan to a single company_documents.id",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of human summary",
    )
    args = parser.parse_args(argv)

    findings = audit(args.db, target_doc_id=args.hub)

    if args.json:
        payload = {
            "findings": [asdict(f) for f in findings],
            "summary": {
                "valid": sum(1 for f in findings if f.severity == "VALID"),
                "warning": sum(1 for f in findings if f.severity == "WARNING"),
                "error": sum(1 for f in findings if f.severity == "ERROR"),
            },
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _v, _w, n_err = _print_summary(findings)
        _print_warnings(findings)
        _print_errors(findings)
        if n_err:
            print(f"\n[FAIL] {n_err} ERROR(s) -- exiting non-zero for CI.")
        else:
            print("\n[OK] 0 ERRORs.")

    return 1 if any(f.severity == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
