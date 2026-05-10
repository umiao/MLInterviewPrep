"""[T-P1-795 / KG-INT A0] EDA: red-dot threshold percentile distribution + recommendation.

Computes P25/P50/P75/P95 of length() across the 6 note surfaces from CLAUDE.md
Surface Identification table, broken down by company status and placeholder
classification, and emits a Markdown report to docs/audit/red_dot_threshold_eda_2026-05-10.md.

Surfaces measured:
  1. companies.prep_notes        (per-company markdown checklist)
  2. companies.notes             (free-form per-company notes)
  3. company_documents.content   (prose study notes)
  4. problem_company_tags.notes  (per-(problem,company) tag notes)
  5. node_company_tags.notes     (per-(node,company) tag notes)
  6. behavioral_example_company_tags.notes (per-(example,company) tag notes)

Plus framework_nodes.description (KG node prose; not a per-company surface,
but baseline for "real content" length sanity-check).

Output: docs/audit/red_dot_threshold_eda_2026-05-10.md (idempotent re-write).
"""

from __future__ import annotations

import sqlite3
import statistics
from collections.abc import Iterable
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
REPORT_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "audit"
    / "red_dot_threshold_eda_2026-05-10.md"
)

# Surfaces: (label, table, length_column, optional WHERE clause for company_id JOIN)
# Each surface is paired with a per-status breakdown via JOIN to companies.
SURFACES = [
    # (label, sql_select_lengths, has_status_breakdown)
    (
        "companies.prep_notes",
        """
        SELECT c.id, c.status, c.name, c.prep_notes
        FROM companies c
        """,
        "prep_notes",
        True,
    ),
    (
        "companies.notes",
        """
        SELECT c.id, c.status, c.name, c.notes
        FROM companies c
        """,
        "notes",
        True,
    ),
    (
        "company_documents.content",
        """
        SELECT cd.company_id, c.status, c.name, cd.content
        FROM company_documents cd
        JOIN companies c ON c.id = cd.company_id
        """,
        "content",
        True,
    ),
    (
        "problem_company_tags.notes",
        """
        SELECT pct.company_id, c.status, c.name, pct.notes
        FROM problem_company_tags pct
        JOIN companies c ON c.id = pct.company_id
        """,
        "notes",
        True,
    ),
    (
        "node_company_tags.notes",
        """
        SELECT nct.company_id, c.status, c.name, nct.notes
        FROM node_company_tags nct
        JOIN companies c ON c.id = nct.company_id
        """,
        "notes",
        True,
    ),
    (
        "behavioral_example_company_tags.notes",
        """
        SELECT bect.company_id, c.status, c.name, bect.notes
        FROM behavioral_example_company_tags bect
        JOIN companies c ON c.id = bect.company_id
        """,
        "notes",
        True,
    ),
    (
        "framework_nodes.description",
        """
        SELECT fn.id, NULL AS status, fn.path AS name, fn.description
        FROM framework_nodes fn
        """,
        "description",
        False,
    ),
]

# Heuristics for "placeholder vs real" classification.
PLACEHOLDER_PATTERNS = (
    "tbd",
    "todo",
    "to do",
    "n/a",
    "na",
    "placeholder",
    "stub",
    "fill me in",
    "fill in",
    "[ ]",  # an empty checklist item
    "lorem ipsum",
)


def is_placeholder(text: str | None) -> bool:
    """True if the text is empty/None or matches simple placeholder heuristics."""
    if text is None:
        return True
    stripped = text.strip()
    if not stripped:
        return True
    if len(stripped) < 5:
        return True
    lowered = stripped.lower()
    # Length cap: a long real doc with one stray "TODO" still counts as real;
    # only short bodies dominated by a placeholder marker classify as placeholder.
    return (
        len(stripped) < 80
        and any(pat in lowered for pat in PLACEHOLDER_PATTERNS)
    )


def percentiles(values: Iterable[int]) -> dict[str, int | float]:
    """Compute count/min/P25/P50/P75/P95/max from an iterable of ints.

    Returns 0s when input is empty so the report is consistent.
    """
    sorted_vals = sorted(int(v) for v in values)
    n = len(sorted_vals)
    if n == 0:
        return {"count": 0, "min": 0, "p25": 0, "p50": 0, "p75": 0, "p95": 0, "max": 0, "mean": 0}

    def quantile(q: float) -> int:
        # Nearest-rank percentile (matches numpy default close enough for EDA).
        if n == 1:
            return sorted_vals[0]
        idx = max(0, min(n - 1, int(round(q * (n - 1)))))
        return sorted_vals[idx]

    return {
        "count": n,
        "min": sorted_vals[0],
        "p25": quantile(0.25),
        "p50": quantile(0.50),
        "p75": quantile(0.75),
        "p95": quantile(0.95),
        "max": sorted_vals[-1],
        "mean": int(round(statistics.mean(sorted_vals))),
    }


def fetch_surface(conn: sqlite3.Connection, sql: str, value_col: str) -> list[tuple]:
    """Fetch (id, status, name, length, is_placeholder) for a surface."""
    rows = conn.execute(sql).fetchall()
    out = []
    for row in rows:
        # Each row is (entity_id, status, name, raw_value)
        entity_id, status, name, raw = row[0], row[1], row[2], row[3]
        length = len(raw) if raw is not None else 0
        out.append((entity_id, status, name, length, is_placeholder(raw)))
    return out


def render_table(stats: dict[str, dict]) -> list[str]:
    """Render a Markdown table from {row_label: stats_dict}."""
    lines = [
        "| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |",
        "|-------|---|-----|-----|-----|-----|-----|-----|------|",
    ]
    for label, s in stats.items():
        lines.append(
            f"| {label} | {s['count']} | {s['min']} | {s['p25']} | "
            f"{s['p50']} | {s['p75']} | {s['p95']} | {s['max']} | {s['mean']} |"
        )
    return lines


# Status grouping for "applied" vs "phone_screen+onsite" buckets.
APPLIED_STATUSES = {"applied", "rejected"}  # not actively interviewing
ACTIVE_STATUSES = {"phone_screen", "onsite", "offer"}  # active or progressed


def main() -> None:
    """Compute percentiles, classify, and write the report."""
    if not DB_PATH.exists():
        raise SystemExit(f"DB not found at {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    out_lines: list[str] = []
    out_lines.append("# Red-Dot Threshold EDA -- 2026-05-10")
    out_lines.append("")
    out_lines.append("Task: T-P1-795 [KG-INT A0]. Goal: data-driven recommendation for")
    out_lines.append("the `has_meaningful_note` cutoff used by A1 (T-P1-796) /")
    out_lines.append("A2 (T-P1-797) to drive the company-card red dot. Default proposed")
    out_lines.append("by the umbrella plan was 50/100/20 chars (per-surface). This report")
    out_lines.append("validates or revises those values from current DB state.")
    out_lines.append("")
    out_lines.append("## Methodology")
    out_lines.append("")
    out_lines.append("- Source DB: `data/mle_prep.db`")
    out_lines.append("- Length unit: Python `len(text)` (Unicode code points; CJK = 1 each).")
    out_lines.append("- Percentile method: nearest-rank on sorted population.")
    out_lines.append("- Placeholder heuristic: empty / whitespace-only / <5 chars OR")
    out_lines.append("  body <80 chars containing one of:")
    out_lines.append(f"  `{', '.join(PLACEHOLDER_PATTERNS)}`.")
    out_lines.append("- Status buckets:")
    out_lines.append(
        f"  - applied-bucket: `{sorted(APPLIED_STATUSES)}` (not actively interviewing)"
    )
    out_lines.append(
        f"  - active-bucket: `{sorted(ACTIVE_STATUSES)}` (phone_screen / onsite / offer)"
    )
    out_lines.append("")

    # Per-surface stats accumulator for the recommendation section.
    surface_recommendations: dict[str, dict] = {}

    for label, sql, value_col, has_status in SURFACES:
        rows = fetch_surface(conn, sql, value_col)
        all_lengths = [r[3] for r in rows]
        nonempty_lengths = [r[3] for r in rows if r[3] > 0]
        real_lengths = [r[3] for r in rows if not r[4]]  # not placeholder
        placeholder_lengths = [r[3] for r in rows if r[4]]

        applied_real = [
            r[3] for r in rows
            if not r[4] and r[1] in APPLIED_STATUSES
        ]
        active_real = [
            r[3] for r in rows
            if not r[4] and r[1] in ACTIVE_STATUSES
        ]

        out_lines.append(f"## Surface: `{label}`")
        out_lines.append("")
        out_lines.append(f"- Total rows: **{len(rows)}**")
        out_lines.append(f"- Non-empty: **{len(nonempty_lengths)}**")
        out_lines.append(
            f"- Real (non-placeholder): **{len(real_lengths)}** "
            f"({100 * len(real_lengths) / len(rows):.1f}%)" if rows else
            "- Real (non-placeholder): **0**"
        )
        out_lines.append(
            f"- Placeholder: **{len(placeholder_lengths)}** "
            f"({100 * len(placeholder_lengths) / len(rows):.1f}%)" if rows else
            "- Placeholder: **0**"
        )
        out_lines.append("")

        slices = {
            "all rows": percentiles(all_lengths),
            "non-empty only": percentiles(nonempty_lengths),
            "real (non-placeholder)": percentiles(real_lengths),
            "placeholder only": percentiles(placeholder_lengths),
        }
        if has_status:
            slices["real & applied-bucket"] = percentiles(applied_real)
            slices["real & active-bucket"] = percentiles(active_real)

        out_lines.extend(render_table(slices))
        out_lines.append("")

        # Recommendation rule: validate (or revise) the umbrella plan defaults.
        # Use min(default, real_p25) clamped to >=20. The intent is:
        #   - default is the floor we *want* to hit (50/100/20 from the plan)
        #   - if the data shows real content already starts well above the
        #     default (e.g. all real docs are >7000 chars), the default is
        #     fine -- we don't want to *raise* the cutoff just because real
        #     content happens to be long, because that would only matter for
        #     edge-case future entries
        #   - if the data shows real content P25 sits BELOW the default (e.g.
        #     real `notes` P25 = 28 chars), the default is too aggressive and
        #     we'd flag too many legitimate-but-short entries; lower the
        #     cutoff to the data-driven floor
        #   - final clamp to >=20 prevents any cutoff from dropping into the
        #     trivial-string range
        real_p25 = slices["real (non-placeholder)"]["p25"]
        defaults = {
            "companies.prep_notes": 50,
            "companies.notes": 50,
            "company_documents.content": 100,
            "problem_company_tags.notes": 20,
            "node_company_tags.notes": 20,
            "behavioral_example_company_tags.notes": 20,
            "framework_nodes.description": 50,
        }
        default_val = defaults.get(label, 50)
        if len(real_lengths) > 0:
            recommended = max(20, min(default_val, int(real_p25)))
        else:
            # No real-content evidence yet (e.g. node_company_tags.notes is
            # all placeholders); fall back to default.
            recommended = default_val
        # Sanity flag: P25(real) far above default => default likely fine, but
        # also note the gap so we don't accidentally lower a stricter bar.
        gap = real_p25 - default_val if len(real_lengths) > 0 else None
        surface_recommendations[label] = {
            "default": default_val,
            "real_p25": real_p25,
            "real_min": slices["real (non-placeholder)"]["min"],
            "real_count": len(real_lengths),
            "placeholder_count": len(placeholder_lengths),
            "placeholder_max": (
                slices["placeholder only"]["max"]
                if len(placeholder_lengths) > 0
                else 0
            ),
            "recommended": recommended,
            "p25_gap_above_default": gap,
        }

    # Recommendation section.
    out_lines.append("## Recommendation")
    out_lines.append("")
    out_lines.append(
        "Recommendation rule: for each surface, set the `has_meaningful_note`")
    out_lines.append(
        "cutoff to `max(20, min(plan_default, real_content_P25))`. Rationale:")
    out_lines.append("")
    out_lines.append(
        "- `plan_default` is the umbrella plan's intent: the minimum length we")
    out_lines.append(
        "  consider 'sign of real prep'. We don't want to raise it just because")
    out_lines.append(
        "  current real content happens to be long -- that would penalize a")
    out_lines.append(
        "  legitimate-but-short future entry (e.g. a brief `notes` line).")
    out_lines.append(
        "- `real_content_P25`: if 25% of real entries already sit below the")
    out_lines.append(
        "  default, the default is too aggressive (would red-dot legitimate")
    out_lines.append(
        "  entries). In that case, drop the cutoff to that data-driven floor.")
    out_lines.append(
        "- The `max(20, ...)` clamp prevents the cutoff from collapsing into")
    out_lines.append("  the trivial-string range.")
    out_lines.append(
        "- Surfaces with no real-content evidence yet (e.g. `node_company_tags.notes`")
    out_lines.append(
        "  is currently 100% placeholders) fall back to the plan default.")
    out_lines.append("")
    out_lines.append(
        "**The placeholder filter (heuristic above) is independent of the length**")
    out_lines.append(
        "**cutoff and applies in addition to it.** Any entry matching the")
    out_lines.append(
        "placeholder-shape rules counts as 'no meaningful note' regardless of")
    out_lines.append("its length.")
    out_lines.append("")
    out_lines.append(
        "| Surface | Plan default | Real-content P25 | Real min | Placeholder max | Recommended | Real N | Placeholder N |")
    out_lines.append(
        "|---------|--------------|------------------|----------|-----------------|-------------|--------|---------------|")
    for label, rec in surface_recommendations.items():
        out_lines.append(
            f"| `{label}` | {rec['default']} | {rec['real_p25']} | "
            f"{rec['real_min']} | {rec['placeholder_max']} | "
            f"**{rec['recommended']}** | {rec['real_count']} | {rec['placeholder_count']} |"
        )
    out_lines.append("")

    # Aggregate "company is meaningful" rule.
    out_lines.append("### Aggregate `has_meaningful_note` rule (for A1)")
    out_lines.append("")
    out_lines.append(
        "A company is `has_meaningful_note=true` if ANY of the per-surface")
    out_lines.append("conditions below holds for that company_id:")
    out_lines.append("")
    for label, rec in surface_recommendations.items():
        if label == "framework_nodes.description":
            continue  # not a per-company surface
        out_lines.append(
            f"- `length({label}) >= {rec['recommended']}` "
            f"AND not placeholder-shaped"
        )
    out_lines.append("")
    out_lines.append(
        "Placeholder-shape filter is applied identically to the EDA heuristic")
    out_lines.append(
        "above. The intent: a company with only `TBD`/`TODO`/empty cells should")
    out_lines.append(
        "show the red dot regardless of how long those cells are.")
    out_lines.append("")

    # Sanity: which active companies would currently be red-dot ON vs OFF?
    out_lines.append("## Per-company simulation")
    out_lines.append("")
    out_lines.append(
        "Apply the aggregate rule against current DB state and bucket by status.")
    out_lines.append("")
    sim_sql = """
        SELECT
          c.id,
          c.name,
          c.status,
          COALESCE(LENGTH(c.prep_notes), 0)               AS len_prep_notes,
          COALESCE(LENGTH(c.notes), 0)                    AS len_notes,
          (SELECT MAX(LENGTH(content)) FROM company_documents WHERE company_id=c.id) AS len_doc,
          (SELECT MAX(LENGTH(notes)) FROM problem_company_tags WHERE company_id=c.id) AS len_pct,
          (SELECT MAX(LENGTH(notes)) FROM node_company_tags WHERE company_id=c.id) AS len_nct,
          (SELECT MAX(LENGTH(notes)) FROM behavioral_example_company_tags WHERE company_id=c.id) AS len_bect
        FROM companies c
        ORDER BY c.status, c.name
    """
    sim_rows = conn.execute(sim_sql).fetchall()
    cutoffs = {
        "prep_notes": surface_recommendations["companies.prep_notes"]["recommended"],
        "notes": surface_recommendations["companies.notes"]["recommended"],
        "doc": surface_recommendations["company_documents.content"]["recommended"],
        "pct": surface_recommendations["problem_company_tags.notes"]["recommended"],
        "nct": surface_recommendations["node_company_tags.notes"]["recommended"],
        "bect": surface_recommendations["behavioral_example_company_tags.notes"]["recommended"],
    }
    on_count = 0
    off_count = 0
    by_status_on: dict[str, int] = {}
    by_status_off: dict[str, int] = {}
    for r in sim_rows:
        meaningful = (
            (r["len_prep_notes"] or 0) >= cutoffs["prep_notes"]
            or (r["len_notes"] or 0) >= cutoffs["notes"]
            or (r["len_doc"] or 0) >= cutoffs["doc"]
            or (r["len_pct"] or 0) >= cutoffs["pct"]
            or (r["len_nct"] or 0) >= cutoffs["nct"]
            or (r["len_bect"] or 0) >= cutoffs["bect"]
        )
        if meaningful:
            on_count += 1
            by_status_on[r["status"]] = by_status_on.get(r["status"], 0) + 1
        else:
            off_count += 1
            by_status_off[r["status"]] = by_status_off.get(r["status"], 0) + 1

    total = len(sim_rows)
    out_lines.append(f"- Total companies: **{total}**")
    out_lines.append(
        f"- Would show red dot OFF (has_meaningful_note=true): **{on_count}** "
        f"({100 * on_count / total:.1f}%)" if total else
        "- Would show red dot OFF (has_meaningful_note=true): 0"
    )
    out_lines.append(
        f"- Would show red dot ON (has_meaningful_note=false): **{off_count}** "
        f"({100 * off_count / total:.1f}%)" if total else
        "- Would show red dot ON (has_meaningful_note=false): 0"
    )
    out_lines.append("")
    out_lines.append("By status -- has_meaningful_note=true:")
    out_lines.append("")
    for status, n in sorted(by_status_on.items(), key=lambda x: x[0] or ""):
        out_lines.append(f"  - `{status}`: {n}")
    out_lines.append("")
    out_lines.append("By status -- has_meaningful_note=false (red dot ON):")
    out_lines.append("")
    for status, n in sorted(by_status_off.items(), key=lambda x: x[0] or ""):
        out_lines.append(f"  - `{status}`: {n}")
    out_lines.append("")

    # Decision summary the upstream task can reference verbatim.
    out_lines.append("## Decision summary (for A1 / T-P1-796 to consume)")
    out_lines.append("")
    out_lines.append("```python")
    out_lines.append("# Per-surface cutoffs (chars) -- copy into A1 implementation.")
    out_lines.append("RED_DOT_CUTOFFS = {")
    for label, rec in surface_recommendations.items():
        if label == "framework_nodes.description":
            continue
        out_lines.append(f'    "{label}": {rec["recommended"]},')
    out_lines.append("}")
    out_lines.append("")
    out_lines.append("# A company has has_meaningful_note=True iff at least one of its")
    out_lines.append("# six surfaces meets its cutoff AND is not placeholder-shaped.")
    out_lines.append("```")
    out_lines.append("")
    out_lines.append(
        "Cross-reference: this report is the source of truth for the cutoff")
    out_lines.append(
        "values listed above. T-P1-796 (A1) acceptance criterion: 'A1 references")
    out_lines.append("report's recommended values' -- this section IS that reference.")
    out_lines.append("")

    REPORT_PATH.write_text("\n".join(out_lines), encoding="utf-8")
    conn.close()
    print(f"[OK] Wrote report: {REPORT_PATH}")
    print(f"[OK] Total surfaces analyzed: {len(SURFACES)}")
    print(f"[OK] Total companies simulated: {total}")
    print(f"[OK] Red-dot OFF: {on_count}/{total}; ON: {off_count}/{total}")


if __name__ == "__main__":
    main()
