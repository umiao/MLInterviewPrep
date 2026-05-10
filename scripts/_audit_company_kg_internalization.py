"""[KG-INT B1] Per-company audit dump across 6 note surfaces (T-P1-798).

Goal: produce an audit artifact that, for each of 32 companies, dumps stats
across the six surfaces where company-scoped notes accumulate. The output
feeds the KG-INT B-track (T-P1-803..807, T-P0-808/809, etc.) decision of
which prose / tag rows are candidates for promotion to the new `meta-prep`
pillar (>=3-of-11 P0+P1 companies threshold, T-P1-801).

The six surfaces:
  S1 prep_notes                    companies.prep_notes (markdown checklist)
  S2 notes                         companies.notes      (free-form prose)
  S3 company_documents             company_documents JOIN companies (prose study notes)
  S4 problem_company_tags          problem<->company association (LC tagging)
  S5 node_company_tags             framework_node<->company association (KG tagging)
  S6 behavioral_example_company_tags  behavioral_example<->company association

Per-surface columns (uniform across all 6):
  bytes               - total content bytes for the surface (0 for empty / no-rows)
  topics              - heuristic topic count
                        * prose surfaces (S1/S2/S3): markdown headers
                          (lines starting with `#`)
                        * tag-table surfaces (S4/S5/S6): distinct tag rows
  kg_refs             - count of references to KG / cross-doc artifacts:
                        * prose: regex hits for `kg://N`, `db://N`, `cd://N`,
                          `sd://slug` drawer URIs (sum across all schemes)
                        * tag tables: count of distinct framework_node /
                          problem ids referenced
  drawer_link_count   - count of markdown links `[..](..)` in prose surfaces
                        (0 for tag tables)
  candidate_pct       - heuristic internalization-candidate percentage:
                        * prose surfaces: percentage of non-empty lines that
                          do NOT mention the company name (case-insensitive
                          substring match) -- proxy for "shared substrate"
                          eligible for promotion to meta-prep
                        * tag tables: percentage of rows with relevance IN
                          ('likely','stretch') -- proxy for promotable
                          (core rows are highly company-specific)

These heuristics are deliberately coarse. They are a triage signal, not a
verdict. Final promotion decisions live in T-P1-803..807 and require
manual review of the actual prose / tags.

Output:
  docs/audit/company_kg_internalization_audit_<YYYY-MM-DD>.md

The script is idempotent in the sense that re-running on an unchanged DB
produces a byte-identical file (the `--date` override pins the report
date so the filename and the in-body header are deterministic; iteration
order is `companies.id ASC`; counts are derived from a fixed-seed query).

Usage:
  python scripts/_audit_company_kg_internalization.py
  python scripts/_audit_company_kg_internalization.py --date 2026-05-10
  python scripts/_audit_company_kg_internalization.py --json     # stdout JSON

Acceptance criteria (T-P1-798):
  * report exists at docs/audit/company_kg_internalization_audit_*.md
  * covers all 32 companies (rows present even when surface is empty)
  * each company has a 6-surface row table

This is a one-shot audit (prefixed `_`); it is not part of the recurring
audit suite. Re-run when the surfaces materially change.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "audit"

# Drawer URI patterns used in prose surfaces. `kg://` is the new scheme
# being introduced in T-P1-799; it doesn't appear in current content but
# is counted so re-runs after B2a will pick up adoption automatically.
URI_PATTERNS = [
    re.compile(r"kg://(\d+)"),
    re.compile(r"db://(\d+)"),
    re.compile(r"cd://(\d+)"),
    re.compile(r"sd://([a-z0-9-]+)"),
]
MD_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]+\)")
HEADER_RE = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)


SURFACE_LABELS = (
    ("S1", "prep_notes"),
    ("S2", "notes"),
    ("S3", "company_documents"),
    ("S4", "problem_company_tags"),
    ("S5", "node_company_tags"),
    ("S6", "behavioral_example_company_tags"),
)


def count_uri_refs(text: str) -> int:
    """Sum of matches across all drawer URI schemes in a prose blob."""
    if not text:
        return 0
    return sum(len(p.findall(text)) for p in URI_PATTERNS)


def count_drawer_links(text: str) -> int:
    """Count of markdown `[..](..)` links in a prose blob."""
    if not text:
        return 0
    return len(MD_LINK_RE.findall(text))


def count_headers(text: str) -> int:
    """Count of markdown headers (`#`...`######`) in a prose blob."""
    if not text:
        return 0
    return len(HEADER_RE.findall(text))


def prose_candidate_pct(text: str, company_name: str) -> float:
    """Percent of non-blank lines that do NOT mention the company name.

    Used as a "shared substrate" proxy for prose surfaces. Higher = more
    of the prose is generic / promotable to meta-prep. Companies often
    appear with case variations and as a substring of other tokens, so
    this is a coarse signal only.
    """
    if not text:
        return 0.0
    needle = company_name.lower()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    generic = sum(1 for ln in lines if needle not in ln.lower())
    return round(100.0 * generic / len(lines), 1)


def tag_candidate_pct(rows: list[tuple[str, ...]]) -> float:
    """Percent of tag rows whose relevance is 'likely' or 'stretch'.

    Used as a "promotable" proxy for tag-table surfaces. Core tags are
    deliberately company-specific; likely/stretch are softer signals
    that often generalize.
    """
    if not rows:
        return 0.0
    soft = sum(1 for r in rows if r[0] in ("likely", "stretch"))
    return round(100.0 * soft / len(rows), 1)


def gather_company_stats(
    conn: sqlite3.Connection, company_id: int, company_name: str
) -> dict[str, dict[str, Any]]:
    """Build the 6-surface stat dict for a single company.

    Each value dict carries `bytes`, `topics`, `kg_refs`, `drawer_link_count`,
    `candidate_pct`. Empty surfaces still emit a zero row so the report
    table is uniform.
    """
    cur = conn.cursor()
    out: dict[str, dict[str, Any]] = {}

    # S1 prep_notes
    cur.execute("SELECT prep_notes FROM companies WHERE id=?", (company_id,))
    pn = (cur.fetchone() or [None])[0] or ""
    out["S1"] = {
        "bytes": len(pn.encode("utf-8")),
        "topics": count_headers(pn),
        "kg_refs": count_uri_refs(pn),
        "drawer_link_count": count_drawer_links(pn),
        "candidate_pct": prose_candidate_pct(pn, company_name),
    }

    # S2 notes
    cur.execute("SELECT notes FROM companies WHERE id=?", (company_id,))
    nt = (cur.fetchone() or [None])[0] or ""
    out["S2"] = {
        "bytes": len(nt.encode("utf-8")),
        "topics": count_headers(nt),
        "kg_refs": count_uri_refs(nt),
        "drawer_link_count": count_drawer_links(nt),
        "candidate_pct": prose_candidate_pct(nt, company_name),
    }

    # S3 company_documents (sum across all docs for this company)
    cur.execute(
        "SELECT content FROM company_documents WHERE company_id=? ORDER BY id",
        (company_id,),
    )
    docs = [r[0] or "" for r in cur.fetchall()]
    if docs:
        joined = "\n\n".join(docs)
        out["S3"] = {
            "bytes": sum(len(d.encode("utf-8")) for d in docs),
            "topics": sum(count_headers(d) for d in docs),
            "kg_refs": sum(count_uri_refs(d) for d in docs),
            "drawer_link_count": sum(count_drawer_links(d) for d in docs),
            "candidate_pct": prose_candidate_pct(joined, company_name),
            "doc_count": len(docs),
        }
    else:
        out["S3"] = {
            "bytes": 0, "topics": 0, "kg_refs": 0,
            "drawer_link_count": 0, "candidate_pct": 0.0, "doc_count": 0,
        }

    # S4 problem_company_tags
    cur.execute(
        "SELECT relevance, problem_id FROM problem_company_tags "
        "WHERE company_id=? ORDER BY id",
        (company_id,),
    )
    pct_rows = cur.fetchall()
    out["S4"] = {
        "bytes": 0,
        "topics": len(pct_rows),
        "kg_refs": len({r[1] for r in pct_rows}),
        "drawer_link_count": 0,
        "candidate_pct": tag_candidate_pct(pct_rows),
    }

    # S5 node_company_tags
    cur.execute(
        "SELECT relevance, node_id FROM node_company_tags "
        "WHERE company_id=? ORDER BY id",
        (company_id,),
    )
    nct_rows = cur.fetchall()
    out["S5"] = {
        "bytes": 0,
        "topics": len(nct_rows),
        "kg_refs": len({r[1] for r in nct_rows}),
        "drawer_link_count": 0,
        "candidate_pct": tag_candidate_pct(nct_rows),
    }

    # S6 behavioral_example_company_tags
    cur.execute(
        "SELECT relevance, example_id FROM behavioral_example_company_tags "
        "WHERE company_id=? ORDER BY id",
        (company_id,),
    )
    bect_rows = cur.fetchall()
    out["S6"] = {
        "bytes": 0,
        "topics": len(bect_rows),
        "kg_refs": len({r[1] for r in bect_rows}),
        "drawer_link_count": 0,
        "candidate_pct": tag_candidate_pct(bect_rows),
    }

    return out


def build_report(
    companies: list[tuple[int, str, str | None]],
    stats: dict[int, dict[str, dict[str, Any]]],
    report_date: str,
) -> str:
    """Render the markdown report. Deterministic given inputs."""
    lines: list[str] = []
    lines.append(
        f"# Company KG-Internalization Audit ({report_date})"
    )
    lines.append("")
    lines.append(
        "Per-company stats across the six note surfaces. Generated by "
        "`scripts/_audit_company_kg_internalization.py`. See the script "
        "docstring for column definitions and heuristics."
    )
    lines.append("")
    lines.append("**Surface legend:**")
    for sid, label in SURFACE_LABELS:
        lines.append(f"- `{sid}` = `{label}`")
    lines.append("")

    # Roll-up summary
    lines.append("## Roll-up summary")
    lines.append("")
    lines.append(
        "| Company | Status | S1 B | S2 B | S3 B | S3 docs | "
        "S4 tags | S5 tags | S6 tags | Tot KG refs |"
    )
    lines.append(
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    )
    for cid, name, status in companies:
        s = stats[cid]
        tot_refs = sum(s[k]["kg_refs"] for k, _ in SURFACE_LABELS)
        lines.append(
            f"| {name} | {status or '-'} | "
            f"{s['S1']['bytes']} | {s['S2']['bytes']} | {s['S3']['bytes']} | "
            f"{s['S3']['doc_count']} | "
            f"{s['S4']['topics']} | {s['S5']['topics']} | {s['S6']['topics']} | "
            f"{tot_refs} |"
        )
    lines.append("")

    # Per-company 6-row tables
    lines.append("## Per-company surface breakdowns")
    lines.append("")
    for cid, name, status in companies:
        s = stats[cid]
        lines.append(f"### {name} (id={cid}, status={status or '-'})")
        lines.append("")
        lines.append(
            "| Surface | bytes | topics | kg_refs | drawer_links | candidate_% |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|")
        for sid, label in SURFACE_LABELS:
            row = s[sid]
            extra = ""
            if sid == "S3":
                extra = f" ({row['doc_count']} docs)"
            lines.append(
                f"| {sid} {label}{extra} | {row['bytes']} | {row['topics']} | "
                f"{row['kg_refs']} | {row['drawer_link_count']} | "
                f"{row['candidate_pct']} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Report date (default: today, YYYY-MM-DD).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON to stdout instead of writing a markdown report.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help=f"Path to mle_prep.db (default: {DB_PATH}).",
    )
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"DB not found: {args.db}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(args.db)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, status FROM companies ORDER BY id"
        )
        companies = list(cur.fetchall())
        stats: dict[int, dict[str, dict[str, Any]]] = {}
        for cid, name, _ in companies:
            stats[cid] = gather_company_stats(conn, cid, name)
    finally:
        conn.close()

    if args.json:
        out = {
            "date": args.date,
            "companies": [
                {"id": cid, "name": name, "status": status, "surfaces": stats[cid]}
                for cid, name, status in companies
            ],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    report = build_report(companies, stats, args.date)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"company_kg_internalization_audit_{args.date}.md"
    out_path.write_text(report, encoding="utf-8")
    print(
        f"Wrote {out_path} ({len(companies)} companies, "
        f"{sum(1 for _ in companies) * len(SURFACE_LABELS)} surface rows)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
