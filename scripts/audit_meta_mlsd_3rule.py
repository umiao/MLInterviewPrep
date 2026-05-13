"""T-P0-872 / META-MLSD-LINT-3X: Schema validator + cross-page consistency + diff-delta.

Three-part lint of the Meta-MLSD content corpus consumed by Meta's 45-min
ML System Design loop:

  (a) PER-PAGE SCHEMA VALIDATION
      - cd96 (company_documents.id=96, methodology playbook)
      - 4 sd-goldens: meta-reels-golden, meta-top3-comments-golden,
        meta-weapon-ads-golden, meta-friend-rec-golden
      Each surface is checked against:
        * section-level 3-rule pass (R-3RULE-decision / -tradeoff /
          -scale-sla / -twist-callback), at_least_one_bullet semantic
        * forbidden_patterns from schema (scope-aware)
        * R-NARRATIVE-prose-form measurable_proxy thresholds:
            bold density >= 3 per apply_3rule section
            bullet run <= 4 consecutive lines
            table body rows <= 3
        * cd96-only: section heading regexes + R-TIMING-row-4tag
        * sd-golden: target_chars per field, R-DRAWER-no-sd-drawer

  (b) CROSS-PAGE CONSISTENCY
        * 4 sd-goldens use canonical Strong-Moments section naming
        * every cd96 sd:// link resolves to a system_designs.slug
        * (forward-looking) twist_list alignment placeholder

  (c) DIFF-DELTA REPORT
        * post-hoc summary of line/char count reduction vs pre-T867 sd41
          and pre-T868 sd42 baselines; flag any >70% reduction.
        * for sd-weapon / sd-friend (new seeds, no pre-existing baseline)
          the report records current size only.

INPUT:
  schemas/meta_mlsd_canonical.yaml
  data/mle_prep.db

OUTPUT:
  logs/meta_mlsd_audit_<YYYY-MM-DD>.json  (machine-readable report)
  stdout                                   (human summary)

EXIT CODES:
  0  all 5 docs clean
  1  per-page or cross-page findings
  2  diff-delta >70% breach

Usage:
  python scripts/audit_meta_mlsd_3rule.py
  python scripts/audit_meta_mlsd_3rule.py --json
  python scripts/audit_meta_mlsd_3rule.py --strict   # fail on warnings too
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mle_prep.db"
SCHEMA_PATH = ROOT / "schemas" / "meta_mlsd_canonical.yaml"
LOGS_DIR = ROOT / "logs"

# DIFF-DELTA baselines (chars) captured pre-prune.
#   sd41 BASELINE = pre-T867 prune (T-865 audit / PROGRESS 2026-05-13 20:15).
#   sd42 BASELINE = pre-T868 reseed (reconstructed from PROGRESS line 414/615
#                   sanity-check numbers: verbal_outline 5500 + cheat_sheet
#                   5298 + the 7 other cols at sd42 initial-seed sizes).
BASELINE_CHARS = {
    "meta-reels-golden":         45274,
    "meta-top3-comments-golden": 44176,
}
# sd-weapon / sd-friend are new seeds (no pre-T872 baseline); diff-delta
# records current size only for them.
NEW_SD_GOLDENS = {"meta-weapon-ads-golden", "meta-friend-rec-golden"}

# sd-golden DB column -> schema field id mapping.
SD_GOLDEN_FIELDS = (
    "overview",
    "architecture",
    "dataflow",
    "formulas",
    "production_constraints",
    "tradeoffs",
    "defense",
    "verbal_outline",
    "cheat_sheet",
)
SD_GOLDEN_SLUGS = (
    "meta-reels-golden",
    "meta-top3-comments-golden",
    "meta-weapon-ads-golden",
    "meta-friend-rec-golden",
)

# Canonical Strong-Moments section header in sd-golden defense column.
# Schema canonical_header_regex is the OR of these two anchors.
STRONG_MOMENTS_HEADER_RE = re.compile(
    r"(?m)^#+\s*Strong Moments?\b|^#+ .*Strong Moments.*verbatim",
    re.IGNORECASE,
)
STRONG_MOMENTS_FORBIDDEN_SYNONYMS = (
    "Defense Highlights",
    "Key Moments",
    "Verbatim Lines",
)


# ---------------------------------------------------------------------------
# Schema load + DB helpers
# ---------------------------------------------------------------------------
def load_schema() -> dict[str, Any]:
    """Load the canonical Meta-MLSD YAML schema."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_cd96(conn: sqlite3.Connection) -> str:
    """Return cd96 markdown content."""
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id = 96"
    ).fetchone()
    if row is None:
        raise RuntimeError("company_documents.id=96 not found")
    return row[0] or ""


def fetch_sd_golden(conn: sqlite3.Connection, slug: str) -> dict[str, str]:
    """Return the 9 prose columns of a system_designs row by slug."""
    cur = conn.execute(
        "SELECT overview, architecture, dataflow, formulas, "
        "production_constraints, tradeoffs, defense, verbal_outline, "
        "cheat_sheet FROM system_designs WHERE slug = ?",
        (slug,),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"system_designs.slug={slug!r} not found")
    return dict(zip(SD_GOLDEN_FIELDS, [c or "" for c in row], strict=True))


def fetch_all_sd_slugs(conn: sqlite3.Connection) -> set[str]:
    """Return every slug present in system_designs (for sd:// link resolution)."""
    cur = conn.execute("SELECT slug FROM system_designs")
    return {r[0] for r in cur.fetchall()}


# ---------------------------------------------------------------------------
# Per-page check primitives
# ---------------------------------------------------------------------------
def split_cd96_sections(content: str, section_specs: list[dict[str, Any]]) -> dict[str, tuple[int, str]]:
    """Return {section_id: (start_offset, body)} for each cd96 section.

    A section's body runs from its heading match to the next section's heading
    match (or end-of-doc). Missing sections are omitted from the result.
    """
    found: dict[str, tuple[int, str]] = {}
    starts: list[tuple[str, int]] = []
    for spec in section_specs:
        sid = spec["id"]
        pat = spec["heading_regex"]
        m = re.search(pat, content, re.MULTILINE)
        if m:
            starts.append((sid, m.start()))
    starts.sort(key=lambda x: x[1])
    for i, (sid, off) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(content)
        found[sid] = (off, content[off:end])
    return found


def check_3rule_section(body: str, three_rule: dict[str, Any]) -> list[str]:
    """Return list of failing R-3RULE-* rule_ids for one section body.

    Section passes a rule if at_least_one of its detect_regex patterns matches
    anywhere in the body.
    """
    failing: list[str] = []
    for rule_id, spec in three_rule["rules"].items():
        patterns = spec.get("detect_regex", []) or []
        hit = False
        for pat in patterns:
            try:
                if re.search(pat, body, re.MULTILINE):
                    hit = True
                    break
            except re.error:
                continue
        if not hit:
            failing.append(rule_id)
    return failing


def check_narrative_prose(body: str, schema: dict[str, Any]) -> list[str]:
    """Return list of R-NARRATIVE-prose-form violations for one section body.

    Three measurable proxies:
      bold_density >= bold_density_per_section_min
      max consecutive bullet run <= bullet_run_max_consecutive
      max markdown-table body rows <= table_row_max
    """
    cfg = schema.get("narrative_prose_form", {})
    proxy = cfg.get("measurable_proxy", {})
    detect = cfg.get("detect_regex", {})

    bold_min = int(proxy.get("bold_density_per_section_min", 3))
    bullet_max = int(proxy.get("bullet_run_max_consecutive", 4))
    table_row_max = int(proxy.get("table_row_max", 3))

    bold_pat = detect.get("bold", r"\*\*[^*\n]+\*\*")
    bullet_pat = detect.get("bullet_line", r"^\s*[-*]\s+")

    violations: list[str] = []

    bold_count = len(re.findall(bold_pat, body))
    if bold_count < bold_min:
        violations.append(
            f"R-NARRATIVE bold_density={bold_count} < {bold_min}"
        )

    bullet_re = re.compile(bullet_pat, re.MULTILINE)
    run = max_run = 0
    for line in body.splitlines():
        if bullet_re.match(line):
            run += 1
            max_run = max(max_run, run)
        elif line.strip() == "":
            run = 0
        else:
            run = 0
    if max_run > bullet_max:
        violations.append(
            f"R-NARRATIVE bullet_run_max={max_run} > {bullet_max}"
        )

    # Table body rows: contiguous '|'-prefixed lines, minus header + separator.
    in_table = False
    rows_seen = 0
    max_body_rows = 0
    for line in body.splitlines():
        if line.lstrip().startswith("|"):
            rows_seen += 1
            in_table = True
        else:
            if in_table:
                max_body_rows = max(max_body_rows, max(rows_seen - 2, 0))
            in_table = False
            rows_seen = 0
    if in_table:
        max_body_rows = max(max_body_rows, max(rows_seen - 2, 0))
    if max_body_rows > table_row_max:
        violations.append(
            f"R-NARRATIVE table_body_rows_max={max_body_rows} > {table_row_max}"
        )

    return violations


def check_forbidden_patterns(
    text: str, doc_scope_token: str, schema: dict[str, Any]
) -> list[str]:
    """Return forbidden_pattern hits scoped to doc_scope_token.

    doc_scope_token forms accepted in schema:
        'cd96_playbook'                -- cd96-wide
        'sd_golden.<field>'            -- per sd-golden field
        'sd_golden'                    -- (not used here; field-level only)
    """
    hits: list[str] = []
    for entry in schema.get("forbidden_patterns", []) or []:
        scopes = entry.get("scope") or []
        # Support both string list and YAML inline-token lists.
        scopes_norm = [str(s) for s in scopes]
        if doc_scope_token not in scopes_norm:
            continue
        try:
            if re.search(entry["pattern"], text, re.MULTILINE):
                hits.append(f"{entry['id']} pattern matched")
        except re.error:
            continue
    return hits


# ---------------------------------------------------------------------------
# cd96 specific checks
# ---------------------------------------------------------------------------
def audit_cd96(conn: sqlite3.Connection, schema: dict[str, Any]) -> dict[str, Any]:
    """Run the cd96 per-page audit; return findings + char/line stats."""
    content = fetch_cd96(conn)
    findings: list[str] = []
    cfg = schema["cd96_playbook"]
    section_specs = cfg["sections"]

    # All 9 section headings must be present.
    sections = split_cd96_sections(content, section_specs)
    for spec in section_specs:
        sid = spec["id"]
        if sid not in sections:
            findings.append(f"[section] missing {sid} heading (/{spec['heading_regex']}/)")

    # Per-section apply_3rule check.
    three_rule = schema["three_rule"]
    for spec in section_specs:
        sid = spec["id"]
        if not spec.get("apply_3rule"):
            continue
        if sid not in sections:
            continue
        _off, body = sections[sid]
        for failing in check_3rule_section(body, three_rule):
            findings.append(
                f"[{failing}] cd96 section {sid} (at_least_one_bullet pass)"
            )

    # Forbidden patterns scoped to cd96_playbook.
    findings.extend(
        f"[cd96] {h}" for h in check_forbidden_patterns(content, "cd96_playbook", schema)
    )

    # R-TIMING-row-4tag: §1 table row schema.
    if "§1" in sections:
        _off, sec1_body = sections["§1"]
        findings.extend(_audit_cd96_timing_table(sec1_body, cfg))

    # Drawer linkage: every must_link_sd_goldens slug appears via sd:// in cd96.
    must_link = (cfg.get("drawer_header") or {}).get("must_link_sd_goldens") or []
    for slug in must_link:
        if f"sd://{slug}" not in content:
            findings.append(f"[drawer] sd://{slug} missing from cd96 drawer")

    # Section 2 keep/delete subsections.
    if "### 2.2" in content:
        findings.append("[§2.2 delete] '### 2.2' heading still present (T-866)")

    return {
        "doc": "cd96",
        "chars": len(content),
        "lines": content.count("\n") + 1,
        "findings": findings,
    }


def _audit_cd96_timing_table(sec1_body: str, cfg: dict[str, Any]) -> list[str]:
    """Validate R-TIMING-row-4tag inside cd96 Section 1 timing skeleton table."""
    findings: list[str] = []
    sec1_spec = next(
        (s for s in cfg["sections"] if s["id"] == "§1"), None
    )
    if not sec1_spec or "row_schema" not in sec1_spec:
        return findings
    cols = sec1_spec["row_schema"]["columns"]
    rhythm_vocab: set[str] = set()
    slot_vocab: set[str] = set()
    for c in cols:
        if c["name"] == "rhythm":
            rhythm_vocab = set(c.get("vocab", []))
        if c["name"] == "strong_moment_slot":
            slot_vocab = set(c.get("vocab", []))

    data_rows = [
        ln for ln in sec1_body.splitlines()
        if ln.lstrip().startswith("|") and "---" not in ln
    ][1:]  # skip header row

    if not data_rows:
        findings.append("[R-TIMING-row-4tag] no data rows found in §1 table")
        return findings

    for i, row in enumerate(data_rows, 1):
        cells = [c.strip() for c in row.split("|")[1:-1]]
        if len(cells) != 6:
            findings.append(
                f"[R-TIMING-row-4tag] row {i}: {len(cells)} cells (need 6)"
            )
            continue
        time_band, rhythm, slot, twist, scale, trade = cells
        if not time_band:
            findings.append(f"[R-TIMING-row-4tag] row {i}: time_band empty")
        if rhythm_vocab and rhythm not in rhythm_vocab:
            findings.append(
                f"[R-TIMING-row-4tag] row {i}: rhythm {rhythm!r} not in vocab"
            )
        if slot_vocab and slot not in slot_vocab:
            findings.append(
                f"[R-TIMING-row-4tag] row {i}: strong_moment_slot {slot!r} not in vocab"
            )
        if not trade:
            findings.append(
                f"[R-TIMING-row-4tag] row {i}: tag_trade empty (REQUIRED)"
            )
        if not twist:
            findings.append(
                f"[R-TIMING-row-4tag] row {i}: tag_twist empty (use '-' if N/A)"
            )
        if not scale:
            findings.append(
                f"[R-TIMING-row-4tag] row {i}: tag_scale empty (use '-' if N/A)"
            )
    return findings


# ---------------------------------------------------------------------------
# sd-golden specific checks
# ---------------------------------------------------------------------------
def audit_sd_golden(conn: sqlite3.Connection, slug: str, schema: dict[str, Any]) -> dict[str, Any]:
    """Run the sd-golden per-page audit for one slug."""
    cols = fetch_sd_golden(conn, slug)
    findings: list[str] = []
    sg_cfg = schema["sd_golden"]
    three_rule = schema["three_rule"]

    # R-DRAWER-no-sd-drawer: no `| ... sd:// ... |` table at top of any field.
    drawer_top_re = re.compile(r"^\|.*sd://.*\|", re.MULTILINE)
    for k, v in cols.items():
        if v and drawer_top_re.search(v[:2000]):
            findings.append(
                f"[R-DRAWER-no-sd-drawer] {slug}.{k} has '| ... sd:// ... |' "
                f"table within first 2000 chars"
            )

    # Per-field rules from sg_cfg["fields"].
    fields_spec = {f["id"]: f for f in sg_cfg.get("fields", [])}
    for col, body in cols.items():
        spec = fields_spec.get(col)
        if not spec:
            continue
        # Required + char range.
        required = bool(spec.get("required"))
        target = spec.get("target_chars") or {}
        n = len(body or "")
        if required and n <= 200:
            findings.append(f"[required] {slug}.{col} length={n} <= 200")
        if target:
            lo = int(target.get("min", 0))
            hi = int(target.get("max", 10**9))
            if not (lo <= n <= hi):
                findings.append(
                    f"[R-CHAR-range] {slug}.{col} chars={n} not in [{lo}, {hi}]"
                )

        # 3-rule per section for apply_3rule=true fields.
        if spec.get("apply_3rule"):
            for failing in check_3rule_section(body, three_rule):
                findings.append(
                    f"[{failing}] {slug}.{col} (at_least_one_bullet pass)"
                )
            # R-NARRATIVE measurable proxies.
            for v in check_narrative_prose(body, schema):
                findings.append(f"[{slug}.{col}] {v}")

        # Forbidden patterns scoped to sd_golden.<field>.
        findings.extend(
            f"[{slug}.{col}] {h}"
            for h in check_forbidden_patterns(body, f"sd_golden.{col}", schema)
        )

    # tradeoffs section: bullet count + 'vs' pattern (schema-declared shape).
    # Accept either flat numbered list (`1. ... vs ...`) or H2-numbered prose
    # (`## 1. ... vs ...`) -- T-873 retrofit converted sd41/sd42 tradeoffs to
    # H2-prefixed prose paragraphs while sd-weapon / sd-friend kept the flat
    # form. Both forms preserve the "N items with vs" semantics.
    tradeoffs_spec = fields_spec.get("tradeoffs", {})
    body = cols.get("tradeoffs", "")
    if tradeoffs_spec and body:
        min_b = int(tradeoffs_spec.get("min_bullets", 0))
        max_b = int(tradeoffs_spec.get("max_bullets", 10**9))
        n_flat = len(re.findall(r"(?m)^\d+\.\s.+\bvs\b", body))
        n_h2 = len(re.findall(r"(?m)^##\s+\d+\.\s.+\bvs\b", body))
        n_numbered = max(n_flat, n_h2)
        if not (min_b <= n_numbered <= max_b):
            findings.append(
                f"[tradeoffs.count] {slug} numbered_vs_items={n_numbered} not in "
                f"[{min_b}, {max_b}] (accepts both '1. ... vs ...' and "
                f"'## 1. ... vs ...' forms)"
            )

    return {
        "doc": slug,
        "chars": sum(len(v or "") for v in cols.values()),
        "lines": sum((v or "").count("\n") + 1 if v else 0 for v in cols.values()),
        "per_field_chars": {k: len(v or "") for k, v in cols.items()},
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Cross-page consistency
# ---------------------------------------------------------------------------
def audit_cross_page(conn: sqlite3.Connection, schema: dict[str, Any]) -> dict[str, Any]:
    """Run cross-page checks: section-naming + sd:// link resolution."""
    findings: list[str] = []

    # R-XPAGE-section-naming: every sd-golden defense column must use the
    # canonical Strong-Moments header (or a # header containing "Strong Moments").
    for slug in SD_GOLDEN_SLUGS:
        cols = fetch_sd_golden(conn, slug)
        defense = cols.get("defense", "")
        if not STRONG_MOMENTS_HEADER_RE.search(defense):
            findings.append(
                f"[R-XPAGE-section-naming] {slug}.defense missing canonical "
                f"Strong-Moments header"
            )
        for syn in STRONG_MOMENTS_FORBIDDEN_SYNONYMS:
            if re.search(rf"(?m)^#+\s*{re.escape(syn)}\b", defense, re.IGNORECASE):
                findings.append(
                    f"[R-XPAGE-section-naming] {slug}.defense uses forbidden "
                    f"synonym header {syn!r}"
                )

    # R-XPAGE-sd-link-resolves: every sd://<slug> in cd96 must resolve.
    cd96 = fetch_cd96(conn)
    all_slugs = fetch_all_sd_slugs(conn)
    for m in re.finditer(r"sd://([a-z0-9][a-z0-9_-]*)", cd96):
        slug = m.group(1)
        if slug not in all_slugs:
            findings.append(
                f"[R-XPAGE-sd-link-resolves] cd96 -> sd://{slug} does not "
                f"resolve to a system_designs.slug"
            )

    return {"findings": findings}


# ---------------------------------------------------------------------------
# Diff-delta report
# ---------------------------------------------------------------------------
def audit_diff_delta(conn: sqlite3.Connection, schema: dict[str, Any]) -> dict[str, Any]:
    """Compute pre/post line+char deltas; flag any >70% reduction."""
    cfg = (schema.get("diff_delta") or {}).get("R-DIFFDELTA-70pct", {})
    threshold_pct = float(cfg.get("threshold_pct", 70))
    report: dict[str, Any] = {"threshold_pct": threshold_pct, "items": [], "breaches": []}

    for slug in SD_GOLDEN_SLUGS:
        cols = fetch_sd_golden(conn, slug)
        chars_now = sum(len(v or "") for v in cols.values())
        lines_now = sum((v or "").count("\n") + 1 if v else 0 for v in cols.values())
        baseline = BASELINE_CHARS.get(slug)
        item: dict[str, Any] = {
            "slug": slug,
            "chars_now": chars_now,
            "lines_now": lines_now,
            "baseline_chars": baseline,
        }
        if baseline:
            delta = chars_now - baseline
            pct = (delta / baseline) * 100.0
            item.update({"delta_chars": delta, "delta_pct": round(pct, 2)})
            if pct < -threshold_pct:
                item["breach"] = True
                report["breaches"].append(
                    f"{slug}: reduction={-pct:.1f}% > {threshold_pct:.0f}% "
                    f"(chars now={chars_now}, baseline={baseline}) -- "
                    f"likely over-deleted, request human re-review"
                )
        else:
            item["note"] = (
                "new seed (no pre-T872 baseline); diff-delta does not apply"
            )
        report["items"].append(item)

    return report


# ---------------------------------------------------------------------------
# Reporting + entrypoint
# ---------------------------------------------------------------------------
def write_report(report: dict[str, Any]) -> Path:
    """Write the JSON audit report to logs/meta_mlsd_audit_<date>.json."""
    LOGS_DIR.mkdir(exist_ok=True)
    out_path = LOGS_DIR / f"meta_mlsd_audit_{datetime.now():%Y-%m-%d}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return out_path


def print_summary(report: dict[str, Any]) -> None:
    """Print human-readable summary to stdout."""
    print("=== Meta-MLSD 3X audit ===")
    for page in report["per_page"]:
        print(
            f"  [{page['doc']}] chars={page['chars']} lines={page['lines']} "
            f"findings={len(page['findings'])}"
        )
        for f in page["findings"]:
            print(f"    - {f}")

    print()
    print("=== Cross-page ===")
    if report["cross_page"]["findings"]:
        for f in report["cross_page"]["findings"]:
            print(f"  - {f}")
    else:
        print("  (clean)")

    print()
    print(f"=== Diff-delta (>{report['diff_delta']['threshold_pct']:.0f}% gate) ===")
    for it in report["diff_delta"]["items"]:
        if "delta_pct" in it:
            tag = " BREACH" if it.get("breach") else ""
            print(
                f"  {it['slug']:30s} chars={it['chars_now']} "
                f"baseline={it['baseline_chars']} delta={it['delta_pct']:+.1f}%{tag}"
            )
        else:
            print(
                f"  {it['slug']:30s} chars={it['chars_now']} "
                f"(no baseline -- new seed)"
            )
    if report["diff_delta"]["breaches"]:
        for b in report["diff_delta"]["breaches"]:
            print(f"  BREACH: {b}")


def main() -> int:
    """CLI entrypoint: run all 3 audit parts, write JSON report, return exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true",
        help="print JSON report to stdout instead of human summary",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="reserved (currently identical to default behavior)",
    )
    args = parser.parse_args()

    schema = load_schema()
    conn = sqlite3.connect(str(DB_PATH))
    try:
        per_page: list[dict[str, Any]] = [audit_cd96(conn, schema)]
        for slug in SD_GOLDEN_SLUGS:
            per_page.append(audit_sd_golden(conn, slug, schema))
        cross_page = audit_cross_page(conn, schema)
        diff_delta = audit_diff_delta(conn, schema)
    finally:
        conn.close()

    report = {
        "schema_version": schema.get("schema_version"),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "per_page": per_page,
        "cross_page": cross_page,
        "diff_delta": diff_delta,
    }
    out_path = write_report(report)

    n_page_findings = sum(len(p["findings"]) for p in per_page)
    n_xpage_findings = len(cross_page["findings"])
    n_breaches = len(diff_delta["breaches"])

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_summary(report)
        print()
        print(
            f"report written: {out_path.relative_to(ROOT)} | "
            f"page_findings={n_page_findings} | "
            f"cross_page_findings={n_xpage_findings} | "
            f"diff_delta_breaches={n_breaches}"
        )

    if n_breaches:
        return 2
    if n_page_findings or n_xpage_findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
