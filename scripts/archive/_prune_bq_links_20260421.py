"""T-P0-574: Apply conservative auto-prune to question_example_links.

AUTONOMOUS-SAFE MODE. No user gate: prune rules are conservative enough that
the user reviews the diff post-hoc via `docs/bq_link_prune_log_20260421.md`
and the git commit. Any individual deletion can be reverted by re-inserting
the logged (question_id, example_id, old_relevance_note) triple.

Rules (ALL must hold before a DELETE fires):

1. **Trigger (rule 1)**: relevance_note matches the old-framing placeholder
   pattern ``^\\s*brand\\s+recall\\s+.*\\s+story\\s*$`` (case-insensitive).
   These are the 11 bucket-3(a) rows in the T-P0-573 audit. They are
   <=6 word generic pointers with no facet substance.
   (Rule 2 from the task spec -- "note stale after example rewrite" -- is
   not activated in this run: ``behavioral_examples`` has no ``updated_at``
   column, so we cannot deterministically detect post-rewrite note drift.
   The 48 bucket-3(c) stale-framing rows are deliberately DEFERRED per the
   audit: they will be re-evaluated after T-P0-575..578 rewrites land.)

2. **Safety (rule 3)**: the question would still have >= 2 links after the
   prune. Questions with only 2 total links where one is a placeholder
   are kept (they are surfaced in the coverage-gap section of the audit
   for follow-up, not silently orphaned here).

3. **Safety (rule 4)**: the linked example is NOT is_golden=1. Golden
   stories get human-only prune decisions. In practice the candidate
   examples are BLOG-01 and BLOG-01B, both is_golden=0.

Operationally:

* Timestamped DB backup (``mle_prep.db.bak.<ts>_pre_link_prune``) before
  any DELETE.
* Single transaction: either all qualifying deletions apply or none do.
* Idempotent: on re-run, links already deleted log as ``[SKIP: already
  deleted]``; the backup step still runs (cheap; provides a per-run
  snapshot).
* Markdown log at ``docs/bq_link_prune_log_20260421.md`` enumerates every
  deletion or skip with the rule that triggered it plus the full
  pre-deletion relevance_note so manual revert is possible.

Usage
-----

    python scripts/_prune_bq_links_20260421.py
    python scripts/_prune_bq_links_20260421.py --dry-run   # no writes
"""

from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
LOG_PATH = REPO_ROOT / "docs" / "bq_link_prune_log_20260421.md"

PLACEHOLDER_RE = re.compile(r"^\s*brand\s+recall\s+.*\s+story\s*$", re.IGNORECASE)
MIN_LINKS_POST_PRUNE = 2


@dataclass
class PruneCandidate:
    """One link flagged by rule 1 (brand-recall placeholder)."""

    link_id: int
    question_code: str
    example_code: str
    is_golden: int
    relevance_note: str
    question_total_links: int  # total links on this question, pre-prune


@dataclass
class Decision:
    """Outcome of evaluating one candidate against rules 3 and 4."""

    candidate: PruneCandidate
    action: str  # "DELETE", "SKIP_GOLDEN", "SKIP_ORPHAN", "SKIP_ALREADY_GONE"
    rule_triggered: str  # human-readable rule reference


def _connect(db_path: Path) -> sqlite3.Connection:
    """Open the SQLite DB with Row row-factory and FK enforcement."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _backup_db(db_path: Path, timestamp: str) -> Path:
    """Copy the DB file to ``<db>.bak.<timestamp>_pre_link_prune``.

    Args:
        db_path: Path to the live SQLite database.
        timestamp: Run timestamp string (``YYYYMMDD_HHMMSS``).

    Returns:
        Absolute path to the backup file.
    """
    backup = db_path.with_name(
        f"{db_path.name}.bak.{timestamp}_pre_link_prune"
    )
    shutil.copy2(db_path, backup)
    return backup


def _fetch_candidates(conn: sqlite3.Connection) -> list[PruneCandidate]:
    """Return all links whose relevance_note matches the placeholder regex.

    Runs two SQL passes: an overbroad LIKE filter (``'Brand recall%story%'``)
    then Python regex narrowing so the pattern stays a single source of
    truth. The second pass also joins the question's total link count so
    rule 3 can be evaluated without a per-row round-trip.
    """
    rows = conn.execute(
        """
        SELECT l.id         AS link_id,
               q.question_id AS question_code,
               e.example_id  AS example_code,
               e.is_golden   AS is_golden,
               l.relevance_note AS relevance_note,
               (SELECT COUNT(*) FROM question_example_links l2
                WHERE l2.question_id = l.question_id) AS question_total_links
        FROM question_example_links l
        JOIN behavioral_questions q ON l.question_id = q.id
        JOIN behavioral_examples  e ON l.example_id  = e.id
        WHERE l.relevance_note LIKE 'Brand recall%story%'
        ORDER BY q.question_id, l.id
        """
    ).fetchall()
    candidates: list[PruneCandidate] = []
    for row in rows:
        note = row["relevance_note"] or ""
        if not PLACEHOLDER_RE.match(note):
            continue
        candidates.append(
            PruneCandidate(
                link_id=row["link_id"],
                question_code=row["question_code"],
                example_code=row["example_code"],
                is_golden=int(row["is_golden"] or 0),
                relevance_note=note,
                question_total_links=int(row["question_total_links"]),
            )
        )
    return candidates


def _decide(candidates: Iterable[PruneCandidate]) -> list[Decision]:
    """Apply rules 3 and 4 to the candidate set.

    Rule 3 (orphan guard) needs a per-question count of how many candidates
    will drop, so we bucket first and count, then re-scan to emit decisions.
    """
    by_question: dict[str, list[PruneCandidate]] = {}
    for c in candidates:
        by_question.setdefault(c.question_code, []).append(c)

    decisions: list[Decision] = []
    for q_code, group in by_question.items():
        drop_count = len(group)
        total = group[0].question_total_links  # same for all in group
        remaining_if_all_dropped = total - drop_count
        for c in group:
            if c.is_golden:
                decisions.append(
                    Decision(
                        candidate=c,
                        action="SKIP_GOLDEN",
                        rule_triggered=(
                            "rule 4 (example.is_golden=1; golden links are "
                            "never auto-pruned)"
                        ),
                    )
                )
                continue
            if remaining_if_all_dropped < MIN_LINKS_POST_PRUNE:
                decisions.append(
                    Decision(
                        candidate=c,
                        action="SKIP_ORPHAN",
                        rule_triggered=(
                            f"rule 3 (question {q_code} has {total} links; "
                            f"dropping {drop_count} placeholder(s) would leave "
                            f"{remaining_if_all_dropped} < "
                            f"{MIN_LINKS_POST_PRUNE})"
                        ),
                    )
                )
                continue
            decisions.append(
                Decision(
                    candidate=c,
                    action="DELETE",
                    rule_triggered=(
                        "rule 1 (brand-recall placeholder) + rule 3 (question "
                        f"retains {remaining_if_all_dropped} links) + rule 4 "
                        "(example is not golden)"
                    ),
                )
            )
    decisions.sort(key=lambda d: d.candidate.link_id)
    return decisions


def _detect_already_gone(
    conn: sqlite3.Connection, decisions: list[Decision]
) -> list[Decision]:
    """Flip DELETE decisions whose link_id no longer exists (idempotent re-run)."""
    if not decisions:
        return decisions
    delete_ids = [d.candidate.link_id for d in decisions if d.action == "DELETE"]
    if not delete_ids:
        return decisions
    placeholders = ",".join("?" * len(delete_ids))
    existing = {
        row[0]
        for row in conn.execute(
            f"SELECT id FROM question_example_links WHERE id IN ({placeholders})",
            delete_ids,
        )
    }
    for d in decisions:
        if d.action == "DELETE" and d.candidate.link_id not in existing:
            d.action = "SKIP_ALREADY_GONE"
            d.rule_triggered = (
                "idempotent re-run (link already deleted in an earlier pass)"
            )
    return decisions


def _apply_deletes(conn: sqlite3.Connection, decisions: list[Decision]) -> int:
    """Execute DELETE rows in a single transaction. Returns rows deleted."""
    to_delete = [d.candidate.link_id for d in decisions if d.action == "DELETE"]
    if not to_delete:
        return 0
    placeholders = ",".join("?" * len(to_delete))
    cur = conn.execute(
        f"DELETE FROM question_example_links WHERE id IN ({placeholders})",
        to_delete,
    )
    return cur.rowcount


def _count_links(conn: sqlite3.Connection) -> int:
    """Return total row count in question_example_links."""
    return int(
        conn.execute("SELECT COUNT(*) FROM question_example_links").fetchone()[0]
    )


def _write_log(
    log_path: Path,
    *,
    timestamp: str,
    backup_path: Path,
    before_count: int,
    after_count: int,
    decisions: list[Decision],
    dry_run: bool,
) -> None:
    """Render the markdown prune log with one row per decision.

    The log is structured so reverting is mechanical: each DELETE row
    carries (link_id, question_code, example_code, relevance_note) and
    ``INSERT INTO question_example_links`` can be reconstructed from it.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    deletes = [d for d in decisions if d.action == "DELETE"]
    skips_golden = [d for d in decisions if d.action == "SKIP_GOLDEN"]
    skips_orphan = [d for d in decisions if d.action == "SKIP_ORPHAN"]
    skips_gone = [d for d in decisions if d.action == "SKIP_ALREADY_GONE"]

    lines: list[str] = []
    lines.append("# BQ Link Prune Log (T-P0-574)")
    lines.append("")
    lines.append(f"Run timestamp: `{timestamp}`")
    lines.append(
        f"Mode: **{'DRY-RUN (no writes)' if dry_run else 'APPLIED'}**"
    )
    lines.append(f"Backup: `{backup_path.name}`")
    lines.append("Script: `scripts/_prune_bq_links_20260421.py`")
    lines.append("Audit input: `docs/bq_link_audit_20260421.md`")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append(f"- Links before: **{before_count}**")
    lines.append(f"- Links after:  **{after_count}**")
    lines.append(f"- Net deleted:  **{before_count - after_count}**")
    lines.append("")
    lines.append(f"- Candidates matched by rule 1 (brand-recall placeholder): {len(decisions)}")
    lines.append(f"  - DELETE: {len(deletes)}")
    lines.append(f"  - SKIP_GOLDEN: {len(skips_golden)}")
    lines.append(f"  - SKIP_ORPHAN: {len(skips_orphan)}")
    lines.append(f"  - SKIP_ALREADY_GONE: {len(skips_gone)}")
    lines.append("")

    def _table(title: str, rows: list[Decision]) -> None:
        lines.append(f"## {title} ({len(rows)})")
        lines.append("")
        if not rows:
            lines.append("_None._")
            lines.append("")
            return
        lines.append(
            "| link_id | question | story | note | rule |"
        )
        lines.append(
            "|--------:|----------|-------|------|------|"
        )
        for d in rows:
            c = d.candidate
            note = (c.relevance_note or "").replace("|", "\\|")
            rule = d.rule_triggered.replace("|", "\\|")
            lines.append(
                f"| {c.link_id} | `{c.question_code}` | `{c.example_code}` "
                f"| {note} | {rule} |"
            )
        lines.append("")

    _table("Deletions applied", deletes)
    _table("Skipped -- golden story (rule 4)", skips_golden)
    _table("Skipped -- would orphan question (rule 3)", skips_orphan)
    _table("Skipped -- already deleted in earlier run", skips_gone)

    lines.append("## Revert recipe")
    lines.append("")
    lines.append(
        "Each DELETE row above can be reverted by re-inserting the triple "
        "`(question_id, example_id, relevance_note)`. The question/example "
        "numeric IDs are recoverable via the question_code/example_code in "
        "the table: look them up in `behavioral_questions.question_id` and "
        "`behavioral_examples.example_id` respectively. To revert the whole "
        "run, restore the backup file listed above."
    )
    lines.append("")

    log_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run prune, write log, return 0/1 exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be deleted, but do not write to DB.",
    )
    parser.add_argument(
        "--db",
        default=str(DB_PATH),
        help="Path to SQLite DB (default: data/mle_prep.db).",
    )
    parser.add_argument(
        "--log",
        default=str(LOG_PATH),
        help="Path to markdown prune log output.",
    )
    args = parser.parse_args(argv)

    db_path = Path(args.db).resolve()
    log_path = Path(args.log).resolve()

    if not db_path.exists():
        print(f"[FAIL] DB not found at {db_path}", file=sys.stderr)
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = _backup_db(db_path, timestamp)
    print(f"[BACKUP] {backup_path.name}")

    conn = _connect(db_path)
    try:
        before_count = _count_links(conn)
        candidates = _fetch_candidates(conn)
        print(f"[SCAN] {len(candidates)} candidate(s) match rule 1")
        decisions = _decide(candidates)
        decisions = _detect_already_gone(conn, decisions)
        delete_count = sum(1 for d in decisions if d.action == "DELETE")
        skip_counts = {
            action: sum(1 for d in decisions if d.action == action)
            for action in ("SKIP_GOLDEN", "SKIP_ORPHAN", "SKIP_ALREADY_GONE")
        }
        print(
            f"[PLAN] DELETE={delete_count}  "
            f"SKIP_GOLDEN={skip_counts['SKIP_GOLDEN']}  "
            f"SKIP_ORPHAN={skip_counts['SKIP_ORPHAN']}  "
            f"SKIP_ALREADY_GONE={skip_counts['SKIP_ALREADY_GONE']}"
        )
        for d in decisions:
            c = d.candidate
            print(
                f"  [{d.action:18s}] link={c.link_id:4d}  "
                f"q={c.question_code:7s}  e={c.example_code:8s}  "
                f"note={c.relevance_note!r}"
            )

        if args.dry_run:
            print("[DRY-RUN] no writes applied")
            after_count = before_count
        else:
            conn.execute("BEGIN")
            try:
                deleted = _apply_deletes(conn, decisions)
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
            after_count = _count_links(conn)
            print(
                f"[APPLY] deleted={deleted}  links_before={before_count}  "
                f"links_after={after_count}"
            )

        _write_log(
            log_path,
            timestamp=timestamp,
            backup_path=backup_path,
            before_count=before_count,
            after_count=after_count,
            decisions=decisions,
            dry_run=args.dry_run,
        )
        print(f"[LOG] {log_path.relative_to(REPO_ROOT)}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
