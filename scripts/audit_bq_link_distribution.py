"""T-P0-573: Link distribution audit on behavioral question_example_links.

Read-only audit over the 266 rows in question_example_links. Produces a
markdown report with four sections:

1. Questions with >= 3 story links (primary concept needed)
2. Stories with >= 5 question links (angle thinking needed)
3. Prune candidates -- notes that are short boilerplate, old-framing
   placeholders, or attached to stories scheduled for rewrite (Phase-A-II
   stale-high-link stories per docs/bq_golden_trait_matrix.md)
4. Coverage gaps -- questions with 0 non-boilerplate links

The script does NOT write to the database. It only reads and renders.

Phase A of BQ-DEPTH "cut-before-schema": prune spurious links first,
then Phase B schema uplift adds is_primary / probe_notes on the cleaner
surface. Adding is_primary on top of placeholder or stale-framing links
would bake in noise.

Usage
-----

    python scripts/audit_bq_link_distribution.py \\
        --out docs/bq_link_audit_20260421.md

    # Dry run to stdout only:
    python scripts/audit_bq_link_distribution.py --stdout
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
DEFAULT_OUT = (
    Path(__file__).resolve().parents[1] / "docs" / "bq_link_audit_20260421.md"
)

# Classification thresholds & patterns
BOILERPLATE_LEN = 60  # notes shorter than this are flagged single-sentence boilerplate
PRIMARY_THRESHOLD = 3  # questions with this many links "need a primary story"
ANGLE_THRESHOLD = 5  # stories with this many links "need angle thinking"
PLACEHOLDER_RE = re.compile(r"^\s*brand\s+recall\s+.*\s+story\s*$", re.IGNORECASE)

# Stale-high-link stories per docs/bq_golden_trait_matrix.md Phase-A-II plan.
# Their links are not wrong per se but will likely need re-framing after the
# story STAR is rewritten, so they are flagged as "re-audit after rewrite".
STALE_HIGH_LINK_STORIES = {"EX-01", "EX-02", "EX-14", "EX-33"}


@dataclass
class Link:
    """One row from question_example_links joined with q/e metadata."""

    link_id: int
    question_code: str
    question_text: str
    question_category: str
    example_code: str
    example_title: str
    relevance_note: str

    @property
    def note_len(self) -> int:
        """Character length of the relevance note (0 if NULL)."""
        return len(self.relevance_note or "")


def _connect(db_path: Path) -> sqlite3.Connection:
    """Open the SQLite DB with Row row-factory."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _fetch_all_links(conn: sqlite3.Connection) -> list[Link]:
    """Load every question_example_link joined with q/e metadata."""
    cur = conn.execute(
        """
        SELECT l.id AS link_id,
               q.question_id AS qcode,
               q.text AS qtext,
               q.category_id AS qcat,
               e.example_id AS ecode,
               e.title AS etitle,
               l.relevance_note AS relevance_note
        FROM question_example_links l
        JOIN behavioral_questions q ON q.id = l.question_id
        JOIN behavioral_examples e ON e.id = l.example_id
        ORDER BY q.question_id, e.example_id
        """
    )
    return [
        Link(
            link_id=row["link_id"],
            question_code=row["qcode"],
            question_text=row["qtext"] or "",
            question_category=row["qcat"] or "",
            example_code=row["ecode"],
            example_title=row["etitle"] or "",
            relevance_note=row["relevance_note"] or "",
        )
        for row in cur.fetchall()
    ]


def _classify_note(link: Link) -> tuple[str, str] | None:
    """Classify a note as a prune candidate. Returns (category, reason) or None.

    Category values:
      - "placeholder"     : matches BLOG-01 / BLOG-01B stale-framing pattern
      - "boilerplate"     : note shorter than BOILERPLATE_LEN chars
      - "stale-framing"   : attached to a Phase-A-II rewrite-target story
                             (EX-01/02/14/33); re-audit after story rewrite
      - None              : note looks sufficient

    A single link can trip multiple buckets; placeholder > boilerplate >
    stale-framing in priority (most severe first).
    """
    note = (link.relevance_note or "").strip()
    if PLACEHOLDER_RE.match(note):
        return (
            "placeholder",
            "Old-framing placeholder -- story was re-titled but note was never rewritten.",
        )
    if link.note_len < BOILERPLATE_LEN:
        return (
            "boilerplate",
            f"Single-sentence boilerplate ({link.note_len} chars < {BOILERPLATE_LEN}).",
        )
    if link.example_code in STALE_HIGH_LINK_STORIES:
        return (
            "stale-framing",
            f"Attached to {link.example_code} (Phase-A-II rewrite target). "
            "Re-audit after story STAR is rewritten.",
        )
    return None


def _one_line(text: str, limit: int = 220) -> str:
    """Collapse text to a single short line."""
    if not text:
        return "(empty)"
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def _render_section_1(
    links: list[Link],
) -> tuple[str, dict[str, list[Link]]]:
    """Render section 1: questions with >= PRIMARY_THRESHOLD story links.

    Returns the markdown section plus a dict of {question_code: [links]} for
    later cross-reference (used by section 3's question pivot).
    """
    by_question: dict[str, list[Link]] = defaultdict(list)
    for link in links:
        by_question[link.question_code].append(link)

    ranked = sorted(
        by_question.items(),
        key=lambda kv: (-len(kv[1]), kv[0]),
    )
    heavy = [(q, ls) for q, ls in ranked if len(ls) >= PRIMARY_THRESHOLD]

    lines: list[str] = []
    lines.append(f"## 1. Questions with >= {PRIMARY_THRESHOLD} story links (primary concept needed)")
    lines.append("")
    lines.append(
        f"Total questions with >= {PRIMARY_THRESHOLD} linked stories: **{len(heavy)}**. "
        f"These are the questions that Phase-B probe_notes should anchor to a "
        f"*primary* story; the remaining links become explicit backups. Without a "
        f"primary designation the interview drill has to re-pick each time, and "
        f"the same story ends up told with the same facet across questions (the "
        f"failure mode the matrix doc guards against)."
    )
    lines.append("")
    lines.append("| Question | Category | Links | Text |")
    lines.append("|----------|----------|-------|------|")
    for q_code, ls in heavy:
        cat = ls[0].question_category
        text = _one_line(ls[0].question_text, limit=90)
        lines.append(f"| `{q_code}` | {cat} | {len(ls)} | {text} |")

    lines.append("")
    lines.append("### Weak-relevance tail spot-check")
    lines.append("")
    lines.append(
        "Per user direction, we specifically inspect the highest-count questions "
        "for weak-relevance tail -- links where the note is generic enough that "
        "the pair adds noise rather than optionality. Each tail below is sorted "
        "by note length ascending (shortest/most-generic first)."
    )
    lines.append("")
    spotlight = ["COM-2", "PS-1", "PS-2", "OWN-11", "INN-4"]
    for q_code in spotlight:
        pool = by_question.get(q_code, [])
        if not pool:
            continue
        lines.append(f"#### `{q_code}` ({len(pool)} links)")
        lines.append("")
        lines.append("| example | note len | relevance_note |")
        lines.append("|---------|---------:|----------------|")
        for link in sorted(pool, key=lambda x: (x.note_len, x.example_code)):
            lines.append(
                f"| `{link.example_code}` | {link.note_len} | {_one_line(link.relevance_note, limit=200)} |"
            )
        lines.append("")
    return "\n".join(lines), by_question


def _render_section_2(
    links: list[Link],
) -> tuple[str, dict[str, list[Link]]]:
    """Render section 2: stories with >= ANGLE_THRESHOLD question links."""
    by_story: dict[str, list[Link]] = defaultdict(list)
    for link in links:
        by_story[link.example_code].append(link)

    ranked = sorted(
        by_story.items(),
        key=lambda kv: (-len(kv[1]), kv[0]),
    )
    heavy = [(e, ls) for e, ls in ranked if len(ls) >= ANGLE_THRESHOLD]

    lines: list[str] = []
    lines.append(
        f"## 2. Stories with >= {ANGLE_THRESHOLD} question links (angle thinking needed)"
    )
    lines.append("")
    lines.append(
        f"Total stories with >= {ANGLE_THRESHOLD} linked questions: **{len(heavy)}**. "
        f"When one story is pulled into many questions the risk is angle collapse "
        f"-- the same STAR retold verbatim, which makes the drill brittle and "
        f"gives the interviewer a broken-record signal. The trait matrix already "
        f"maps the expected facet per (story, theme); these stories are the ones "
        f"that most need probe_notes to keep the facets distinct."
    )
    lines.append("")
    lines.append("| Story | Title | Q-Links | Questions spanned (categories) |")
    lines.append("|-------|-------|--------:|-------------------------------|")
    for e_code, ls in heavy:
        title = _one_line(ls[0].example_title, limit=70)
        cats = sorted({x.question_category for x in ls})
        cat_str = ", ".join(cats)
        lines.append(f"| `{e_code}` | {title} | {len(ls)} | {cat_str} |")

    lines.append("")
    lines.append("### Weak-relevance tail spot-check (high-link stories)")
    lines.append("")
    lines.append(
        "Per user direction we inspect the 5 highest-count stories for tails "
        "where the note is short enough that the link is doing no work. Each "
        "story below is sorted by note length ascending."
    )
    lines.append("")
    for e_code, ls in heavy[:5]:
        lines.append(f"#### `{e_code}` ({len(ls)} links) -- {_one_line(ls[0].example_title, limit=90)}")
        lines.append("")
        lines.append("| question | category | note len | relevance_note |")
        lines.append("|----------|----------|---------:|----------------|")
        for link in sorted(ls, key=lambda x: (x.note_len, x.question_code)):
            lines.append(
                f"| `{link.question_code}` | {link.question_category} | {link.note_len} | "
                f"{_one_line(link.relevance_note, limit=200)} |"
            )
        lines.append("")
    return "\n".join(lines), by_story


def _render_section_3(links: list[Link]) -> tuple[str, set[int]]:
    """Render section 3: prune candidates with NOTE text for per-link decision.

    Returns the rendered markdown plus the set of link_ids classified as
    prune candidates (used by section 4 to compute non-boilerplate link
    counts per question).
    """
    placeholders: list[tuple[Link, str]] = []
    boilerplate: list[tuple[Link, str]] = []
    stale: list[tuple[Link, str]] = []
    classified_ids: set[int] = set()

    for link in links:
        verdict = _classify_note(link)
        if verdict is None:
            continue
        category, reason = verdict
        classified_ids.add(link.link_id)
        if category == "placeholder":
            placeholders.append((link, reason))
        elif category == "boilerplate":
            boilerplate.append((link, reason))
        elif category == "stale-framing":
            stale.append((link, reason))

    lines: list[str] = []
    lines.append("## 3. Prune candidates (per-link accept/reject)")
    lines.append("")
    lines.append(
        "Three sub-buckets, roughly ordered by severity. The user reviews each "
        "row and decides KEEP / DROP / UPDATE-NOTE; this audit does NOT write to "
        "the DB (cut-before-schema means user approval is the gate). Every row "
        "includes the full `relevance_note` text so the decision can be made "
        "in-line without a round-trip to the database."
    )
    lines.append("")
    lines.append(
        "| Bucket | Count |\n|--------|------:|\n"
        f"| (a) Old-framing placeholder | {len(placeholders)} |\n"
        f"| (b) Single-sentence boilerplate (< {BOILERPLATE_LEN} chars, non-placeholder) | {len(boilerplate)} |\n"
        f"| (c) Stale-framing (story scheduled for Phase-A-II rewrite) | {len(stale)} |\n"
        f"| **Total unique link rows flagged** | **{len(classified_ids)}** |"
    )
    lines.append("")

    def _render_bucket(
        title: str,
        rationale: str,
        rows: list[tuple[Link, str]],
    ) -> list[str]:
        out: list[str] = []
        out.append(f"### 3{title}")
        out.append("")
        out.append(rationale)
        out.append("")
        if not rows:
            out.append("_No rows in this bucket._")
            out.append("")
            return out
        out.append("| link_id | question | story | note len | relevance_note |")
        out.append("|--------:|----------|-------|---------:|----------------|")
        for link, _reason in sorted(rows, key=lambda x: (x[0].question_code, x[0].example_code)):
            out.append(
                f"| {link.link_id} | `{link.question_code}` | `{link.example_code}` | "
                f"{link.note_len} | {_one_line(link.relevance_note, limit=220)} |"
            )
        out.append("")
        return out

    lines.extend(_render_bucket(
        "(a) Old-framing placeholders",
        "These notes literally contain the old `Brand recall X story` placeholder "
        "text -- the story was re-titled but the link note was never rewritten. "
        "Recommended action: **DROP or UPDATE-NOTE**. A note like 'Brand recall "
        "two-part story' does not tell the drill-runner *which* facet of that "
        "story matches this question, so the link is doing less work than the "
        "title of the story it points to.",
        placeholders,
    ))

    lines.extend(_render_bucket(
        "(b) Single-sentence boilerplate",
        f"Notes shorter than {BOILERPLATE_LEN} characters with no explicit "
        f"placeholder marker. Most are loose paraphrases of the question stem "
        f"('Mentored PhD interns through production stack transition' for LDR-1) "
        f"rather than a specific facet lock. Recommended action: **UPDATE-NOTE** "
        f"to a facet-specific line per `docs/bq_golden_trait_matrix.md`, or DROP "
        f"if a stronger story already covers the same angle.",
        boilerplate,
    ))

    lines.extend(_render_bucket(
        "(c) Stale-framing (Phase-A-II rewrite targets)",
        "Links attached to "
        + ", ".join(f"`{c}`" for c in sorted(STALE_HIGH_LINK_STORIES))
        + ". These stories are scheduled to be rewritten per the golden trait "
        "matrix plan (T-P0-575/576/577/578); the note may not survive the "
        "rewrite untouched. Recommended action: **DEFER** decision until after "
        "story rewrite, then re-audit with the new STAR in hand. Listed here "
        "only so the scope of the post-rewrite re-audit is explicit now.",
        stale,
    ))

    return "\n".join(lines), classified_ids


def _render_section_4(
    links: list[Link], classified_ids: set[int]
) -> str:
    """Render section 4: coverage gaps.

    A question is a coverage gap if its non-boilerplate link count is 0,
    i.e. every one of its links falls into bucket (a), (b), or (c) from
    section 3. These are the questions that would lose all their coverage
    if every prune candidate were accepted without replacement.
    """
    by_question: dict[str, list[Link]] = defaultdict(list)
    for link in links:
        by_question[link.question_code].append(link)

    gaps: list[tuple[str, list[Link], int]] = []
    for q_code, ls in by_question.items():
        flagged = sum(1 for x in ls if x.link_id in classified_ids)
        non_boilerplate = len(ls) - flagged
        if non_boilerplate == 0:
            gaps.append((q_code, ls, flagged))

    gaps.sort(key=lambda x: (-x[2], x[0]))

    lines: list[str] = []
    lines.append("## 4. Coverage gaps (questions with 0 non-boilerplate links)")
    lines.append("")
    lines.append(
        "These are questions whose only links would all be pruned if every "
        "section-3 recommendation were accepted. They must be handled before "
        "pruning so we do not create 0-link questions: either (i) an existing "
        "flagged link gets UPDATE-NOTE instead of DROP, or (ii) a new link "
        "from an existing non-flagged story is added. Phase B (schema uplift) "
        "should not run until every question has >= 1 non-boilerplate link."
    )
    lines.append("")
    if not gaps:
        lines.append("**No coverage gaps detected.** Every question has at least one "
                     "non-boilerplate, non-stale link. The prune list in section 3 can "
                     "be applied without creating 0-link questions, subject to per-link "
                     "user approval.")
        lines.append("")
        return "\n".join(lines)

    lines.append("| question | category | total links | all flagged by | text |")
    lines.append("|----------|----------|------------:|----------------|------|")
    for q_code, ls, _flagged in gaps:
        buckets: set[str] = set()
        for link in ls:
            if link.link_id not in classified_ids:
                continue
            if PLACEHOLDER_RE.match(link.relevance_note or ""):
                buckets.add("placeholder")
            elif link.note_len < BOILERPLATE_LEN:
                buckets.add("boilerplate")
            elif link.example_code in STALE_HIGH_LINK_STORIES:
                buckets.add("stale-framing")
        text = _one_line(ls[0].question_text, limit=80)
        lines.append(
            f"| `{q_code}` | {ls[0].question_category} | {len(ls)} | "
            f"{', '.join(sorted(buckets))} | {text} |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_header(
    n_links: int, n_questions: int, n_stories: int
) -> str:
    """Render the doc header + summary counts."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = []
    lines.append("# BQ Link Distribution Audit (T-P0-573)")
    lines.append("")
    lines.append(f"Generated: {ts} (script: `scripts/audit_bq_link_distribution.py`)")
    lines.append("")
    lines.append(
        f"Inputs: `data/mle_prep.db` -- {n_links} rows in `question_example_links`, "
        f"{n_questions} questions, {n_stories} stories."
    )
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Phase A of the BQ-DEPTH plan (`docs/bq_golden_trait_matrix.md`) is "
        "**cut-before-schema**: prune spurious links *before* Phase B adds "
        "the `is_primary` / `probe_notes` columns. Adding a primary flag on "
        "top of placeholder or stale-framing notes would bake the noise in. "
        "This audit enumerates the prune surface per-link so the user can "
        "approve/reject row by row."
    )
    lines.append("")
    lines.append(
        "The audit is read-only: it does not touch the database. The apply "
        "step is T-P0-574, which is gated on user approval of the prune "
        "list in section 3."
    )
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append(
        f"- **Primary-concept threshold**: a question with >= {PRIMARY_THRESHOLD} "
        f"story links is a candidate for Phase-B `is_primary` designation "
        f"(picks one story as the go-to, others are backups).\n"
        f"- **Angle-thinking threshold**: a story with >= {ANGLE_THRESHOLD} "
        f"question links needs different facets per link or risks angle "
        f"collapse under the drill.\n"
        f"- **Prune heuristics**:\n"
        f"  - (a) placeholder: matches `^Brand recall .* story$` (old BLOG "
        f"framing before the 2-part rewrite).\n"
        f"  - (b) boilerplate: note length < {BOILERPLATE_LEN} chars and not a "
        f"placeholder.\n"
        f"  - (c) stale-framing: attached to a Phase-A-II rewrite-target story "
        f"({', '.join(sorted(STALE_HIGH_LINK_STORIES))}); re-audit after the "
        f"story is rewritten.\n"
        f"- **Coverage gap**: question whose non-boilerplate link count is 0."
    )
    lines.append("")
    return "\n".join(lines)


def _render_report(links: list[Link]) -> str:
    """Compose all four sections into one markdown document."""
    n_questions = len({link.question_code for link in links})
    n_stories = len({link.example_code for link in links})
    header = _render_header(len(links), n_questions, n_stories)
    sec1, _ = _render_section_1(links)
    sec2, _ = _render_section_2(links)
    sec3, classified_ids = _render_section_3(links)
    sec4 = _render_section_4(links, classified_ids)
    return "\n".join([header, sec1, sec2, sec3, sec4, ""])


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--db",
        default=str(DB_PATH),
        help="Path to mle_prep.db (default: data/mle_prep.db).",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output markdown path (default: docs/bq_link_audit_20260421.md).",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the report to stdout instead of writing a file.",
    )
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[FAIL] DB not found: {db_path}", file=sys.stderr)
        return 2

    with _connect(db_path) as conn:
        links = _fetch_all_links(conn)

    if not links:
        print("[FAIL] question_example_links is empty.", file=sys.stderr)
        return 2

    report = _render_report(links)

    if args.stdout:
        print(report)
        return 0

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"[DONE] Wrote audit to {out_path} ({len(report)} chars).")
    print(
        f"[INFO] {len(links)} links covered; "
        f"{len({x.question_code for x in links})} questions, "
        f"{len({x.example_code for x in links})} stories."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
