"""T-P2-356: Semantic relevance spot-check for question-example links.

Two modes:

review
    Sample 10 random question_example_links (reproducible via --seed),
    print each pair with a markdown checklist for human review, and
    write the result to docs/audits/qe_link_spotcheck_2026-04-11.md.

apply
    Read a filled-in review file and apply the human decisions
    (KEEP/DROP/UPDATE) to question_example_links atomically.

Consumer-path verification: after apply, re-query each affected
example via the example-centric code path (the same builder the
/behavioral/examples API uses to populate linked_questions) and
print the resulting relevance_note, so we never trust INSERT/UPDATE
return status alone.
"""

from __future__ import annotations

import argparse
import random
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
DEFAULT_SEED = 20260411
DEFAULT_OUT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "audits"
    / "qe_link_spotcheck_2026-04-11.md"
)
SAMPLE_SIZE = 10
LINK_MARKER_RE = re.compile(r"<!--\s*link_row_id:\s*(\d+)\s*-->")
DECISION_RE = re.compile(
    r"-\s*\[(?P<mark>[xX ])\]\s*(?P<label>keep|drop|update-note)",
    re.IGNORECASE,
)
UPDATED_NOTE_RE = re.compile(
    r"\*\*Updated relevance_note\*\*.*?\n```text\n(?P<body>.*?)\n```",
    re.DOTALL,
)


@dataclass
class LinkRow:
    """One row from question_example_links joined with q/e metadata."""

    link_id: int
    question_code: str
    question_text: str
    example_code: str
    example_title: str
    situation: str
    result: str
    relevance_note: str


def _one_line(text: str | None, limit: int = 220) -> str:
    """Collapse text to a single short line for the review doc."""
    if not text:
        return "(empty)"
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def _connect(db_path: Path) -> sqlite3.Connection:
    """Open the SQLite DB with row_factory set."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _fetch_all_links(conn: sqlite3.Connection) -> list[LinkRow]:
    """Load every question_example_link joined with q/e metadata, ordered by id."""
    cur = conn.execute(
        """
        SELECT l.id AS link_id,
               q.question_id AS qcode, q.text AS qtext,
               e.example_id AS ecode, e.title AS etitle,
               e.situation AS situation, e.result AS result,
               l.relevance_note AS relevance_note
        FROM question_example_links l
        JOIN behavioral_questions q ON q.id = l.question_id
        JOIN behavioral_examples e ON e.id = l.example_id
        ORDER BY l.id
        """
    )
    return [
        LinkRow(
            link_id=row["link_id"],
            question_code=row["qcode"],
            question_text=row["qtext"] or "",
            example_code=row["ecode"],
            example_title=row["etitle"] or "",
            situation=row["situation"] or "",
            result=row["result"] or "",
            relevance_note=row["relevance_note"] or "",
        )
        for row in cur.fetchall()
    ]


def _sample_links(links: list[LinkRow], seed: int, n: int) -> list[LinkRow]:
    """Reproducibly sample n links using random.Random(seed)."""
    rng = random.Random(seed)
    if n >= len(links):
        return list(links)
    return rng.sample(links, n)


def _render_review_doc(picks: list[LinkRow], seed: int) -> str:
    """Render a markdown review doc for the sampled links."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = []
    lines.append("# Behavioral Q-Example Link Spot-Check (T-P2-356)")
    lines.append("")
    lines.append(f"Generated: {ts}")
    lines.append(f"Seed: {seed}")
    lines.append(f"Sample size: {len(picks)}")
    lines.append("")
    lines.append("## Reviewer instructions")
    lines.append("")
    lines.append(
        "For each link, mark **exactly one** decision box with `[x]`. "
        "If you choose `update-note`, fill the fenced `text` block under "
        "**Updated relevance_note** with the replacement text. Leave "
        "unchecked entries untouched -- the apply step will skip them."
    )
    lines.append("")
    lines.append(
        "Do not edit or remove the `<!-- link_row_id: N -->` markers. "
        "They are the machine-parseable anchors used by apply mode."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    for idx, link in enumerate(picks, start=1):
        lines.append(f"### {idx}. {link.question_code} -> {link.example_code}")
        lines.append(f"<!-- link_row_id: {link.link_id} -->")
        lines.append("")
        lines.append(f"- **Question**: {_one_line(link.question_text)}")
        lines.append(f"- **Example title**: {_one_line(link.example_title)}")
        lines.append(f"- **Situation**: {_one_line(link.situation)}")
        lines.append(f"- **Result**: {_one_line(link.result)}")
        lines.append(
            f"- **Current relevance_note**: {_one_line(link.relevance_note, limit=500)}"
        )
        lines.append("")
        lines.append("**Decision** (mark exactly one):")
        lines.append("")
        lines.append("- [ ] keep")
        lines.append("- [ ] drop")
        lines.append("- [ ] update-note")
        lines.append("")
        lines.append("**Updated relevance_note** (fill only if update-note):")
        lines.append("")
        lines.append("```text")
        lines.append("")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def cmd_review(args: argparse.Namespace) -> int:
    """Generate the review markdown doc and write it to disk."""
    out_path = Path(args.out).resolve() if args.out else DEFAULT_OUT
    if out_path.exists() and not args.force:
        print(
            f"[FAIL] {out_path} already exists. Use --force to overwrite "
            "(this will discard any in-progress reviewer edits).",
            file=sys.stderr,
        )
        return 2

    with _connect(Path(args.db)) as conn:
        links = _fetch_all_links(conn)

    if not links:
        print("[FAIL] question_example_links is empty -- nothing to audit.", file=sys.stderr)
        return 2

    picks = _sample_links(links, seed=args.seed, n=SAMPLE_SIZE)
    doc = _render_review_doc(picks, seed=args.seed)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    print(f"[DONE] Wrote {len(picks)} review entries to {out_path}")
    print(f"[INFO] Seed={args.seed}. Re-running with the same seed selects the same pairs.")
    for idx, link in enumerate(picks, start=1):
        print(f"  {idx:2d}. link_id={link.link_id:<4d} {link.question_code} -> {link.example_code}")
    return 0


# ---------------------------------------------------------------------------
# Apply mode
# ---------------------------------------------------------------------------


@dataclass
class Decision:
    """One reviewer decision parsed out of the review doc."""

    link_id: int
    action: str  # "keep" | "drop" | "update-note"
    updated_note: str | None


def _parse_decisions(doc: str) -> list[Decision]:
    """Split the doc by link markers and parse each reviewer block.

    Returns decisions in order of appearance. Blocks with zero or multiple
    checked boxes are skipped (treated as unfilled) and reported by the
    caller via the apply-mode summary.
    """
    decisions: list[Decision] = []
    # Split the doc so each chunk starts immediately after a link marker.
    parts = LINK_MARKER_RE.split(doc)
    # parts[0] is the preamble, then alternating [link_id, body] pairs.
    for i in range(1, len(parts), 2):
        link_id = int(parts[i])
        body = parts[i + 1] if i + 1 < len(parts) else ""
        # Stop the block at the next section divider so we do not read
        # into the following entry.
        end = body.find("\n---")
        block = body if end == -1 else body[:end]

        checked: list[str] = []
        for m in DECISION_RE.finditer(block):
            if m.group("mark").lower() == "x":
                checked.append(m.group("label").lower())
        if len(checked) != 1:
            # unfilled (0) or ambiguous (>=2) -- skip per AC "tolerates resumption"
            continue
        action = checked[0]
        updated_note: str | None = None
        if action == "update-note":
            m = UPDATED_NOTE_RE.search(block)
            if m:
                body_text = m.group("body").strip()
                if body_text:
                    updated_note = body_text
            if not updated_note:
                # update-note chosen but no replacement text: skip (unfilled)
                continue
        decisions.append(
            Decision(link_id=link_id, action=action, updated_note=updated_note)
        )
    return decisions


def _linked_questions_for_example(
    conn: sqlite3.Connection, example_db_id: int
) -> list[dict]:
    """Replicate the /behavioral/examples builder's linked_questions path.

    This is the consumer view of question_example_links: the same join used
    by src/backend/routers/behavioral.py::_build_example_response to populate
    the API response. We use it as a post-apply verification read so that
    we never trust UPDATE/DELETE rowcount alone (per CLAUDE.md rule:
    verify via the consumer, not the producer).
    """
    cur = conn.execute(
        """
        SELECT q.id AS id, q.question_id AS question_id, q.text AS text,
               q.category_id AS category_id, l.relevance_note AS relevance_note
        FROM question_example_links l
        JOIN behavioral_questions q ON q.id = l.question_id
        WHERE l.example_id = ?
        ORDER BY l.id
        """,
        (example_db_id,),
    )
    return [dict(row) for row in cur.fetchall()]


def cmd_apply(args: argparse.Namespace) -> int:
    """Parse the review file and apply decisions to the DB atomically."""
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"[FAIL] review file not found: {file_path}", file=sys.stderr)
        return 2
    doc = file_path.read_text(encoding="utf-8")
    decisions = _parse_decisions(doc)

    if not decisions:
        print("[INFO] No filled-in decisions found. Nothing to apply.")
        return 0

    keeps = [d for d in decisions if d.action == "keep"]
    drops = [d for d in decisions if d.action == "drop"]
    updates = [d for d in decisions if d.action == "update-note"]

    print(
        f"[INFO] Parsed {len(decisions)} decisions: "
        f"{len(keeps)} keep, {len(drops)} drop, {len(updates)} update-note"
    )

    if args.dry_run:
        print("[INFO] --dry-run: not writing to DB")
        for d in drops:
            print(f"  would DROP link_id={d.link_id}")
        for d in updates:
            note = d.updated_note or ""
            print(f"  would UPDATE link_id={d.link_id} -> {_one_line(note, limit=120)}")
        return 0

    affected_example_ids: set[int] = set()
    dropped_ids: set[int] = set()

    with _connect(Path(args.db)) as conn:
        cur = conn.cursor()
        try:
            for d in drops:
                row = cur.execute(
                    "SELECT example_id FROM question_example_links WHERE id = ?",
                    (d.link_id,),
                ).fetchone()
                if row is None:
                    print(f"[WARN] drop target link_id={d.link_id} not found; skipping")
                    continue
                affected_example_ids.add(row["example_id"])
                cur.execute("DELETE FROM question_example_links WHERE id = ?", (d.link_id,))
                dropped_ids.add(d.link_id)

            for d in updates:
                row = cur.execute(
                    "SELECT example_id FROM question_example_links WHERE id = ?",
                    (d.link_id,),
                ).fetchone()
                if row is None:
                    print(f"[WARN] update target link_id={d.link_id} not found; skipping")
                    continue
                affected_example_ids.add(row["example_id"])
                cur.execute(
                    "UPDATE question_example_links SET relevance_note = ? WHERE id = ?",
                    (d.updated_note, d.link_id),
                )

            # Keeps are no-op but we still want to verify them through the consumer read.
            for d in keeps:
                row = cur.execute(
                    "SELECT example_id FROM question_example_links WHERE id = ?",
                    (d.link_id,),
                ).fetchone()
                if row is not None:
                    affected_example_ids.add(row["example_id"])

            conn.commit()
        except Exception:
            conn.rollback()
            raise

        # Consumer-path verification: re-read affected examples via the
        # same join the API uses, and print the resulting linked_questions.
        print("")
        print("[VERIFY] Consumer-path read of affected examples:")
        for ex_id in sorted(affected_example_ids):
            linked = _linked_questions_for_example(conn, ex_id)
            ex_code_row = conn.execute(
                "SELECT example_id FROM behavioral_examples WHERE id = ?", (ex_id,)
            ).fetchone()
            ex_code = ex_code_row["example_id"] if ex_code_row else f"ID={ex_id}"
            print(f"  {ex_code}: {len(linked)} linked question(s)")
            for q in linked:
                note_preview = _one_line(q["relevance_note"], limit=120)
                print(f"    - {q['question_id']}: {note_preview}")

    print("")
    print(
        f"[DONE] Applied: {len(updates)} update(s), {len(dropped_ids)} drop(s), "
        f"{len(keeps)} keep(s). {len(affected_example_ids)} example(s) verified."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=("review", "apply"), required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", default=None, help="Output markdown path (review mode)")
    parser.add_argument("--file", default=None, help="Filled-in review file (apply mode)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing review file")
    parser.add_argument("--dry-run", action="store_true", help="Parse decisions without writing to DB")
    parser.add_argument("--db", default=str(DB_PATH))
    args = parser.parse_args(argv)

    if args.mode == "review":
        return cmd_review(args)
    if args.mode == "apply":
        if not args.file:
            parser.error("--file is required in apply mode")
        return cmd_apply(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
