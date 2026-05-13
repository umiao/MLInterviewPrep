"""In-session schema self-check for sd41 after T-P0-867 (one-off audit).

Encodes the sd_golden rules from `schemas/meta_mlsd_canonical.yaml` directly,
since T-872's `audit_meta_mlsd_3rule.py` is not yet built. Stand-in until T-872.

Checks for sd41 (slug='meta-reels-golden', system_designs.id=41):
  - R-DRAWER-no-sd-drawer       : no `^| ... sd:// ... |` table at top of any
                                  sd-golden field (drawer belongs to cd96).
  - R-FORBID-rhythm-philosophy  : `整体节奏哲学` must not appear in overview.
  - R-FORBID-why-this-is-strong : `(?i)why this is strong` must not appear in
                                  defense (meta-commentary belongs in cd96).
  - R-FORBID-drawer-header-literal : `^\\| Doc \\| ... sd://` must not appear
                                  in any sd-golden field.
  - target_chars ranges for overview/architecture/dataflow/defense.
  - 3-rule (R-3RULE-decision / -tradeoff / -scale-sla / -twist-callback)
    at section-level pass for apply_3rule=true fields: overview, architecture,
    dataflow, production_constraints, tradeoffs, defense.
  - DIFF-DELTA log line (informational; the >70% over-prune gate is
    pre-checked at seed time, not enforced here).

Exit 0 = clean (all T-867-relevant rules pass). Exit 1 = at least one finding.
Throwaway: prefixed with `_` per repo convention; do NOT promote to permanent.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

SLUG = "meta-reels-golden"

# Pre-T-867 baseline char counts (captured 2026-05-13 19:30 PDT before
# the seed rewrite). Used only for the informational DIFF-DELTA log.
BASELINE_CHARS_TOTAL = 45274

# sd_golden.fields target_chars from schemas/meta_mlsd_canonical.yaml.
TARGET_CHAR_RANGES = {
    "overview":     (1500, 4500),
    "architecture": (2000, 6000),
    "dataflow":     (2500, 9000),
    "defense":      (2500, 8500),
}

APPLY_3RULE_FIELDS = (
    "overview",
    "architecture",
    "dataflow",
    "production_constraints",
    "tradeoffs",
    "defense",
)

RULE_PATTERNS = {
    "R-3RULE-decision": [
        r"\b(I pick|we pick|I choose|we choose|default to|pick A)\b",
        r"(?i)\bdecision\b.*\bover\b",
    ],
    "R-3RULE-tradeoff": [
        r"(?i)\b(costs?|at the cost of|switches? to|in exchange for)\b",
        r"\bvs\b",
    ],
    "R-3RULE-scale-sla": [
        r"\b\d+\s*(ms|µs|us|qps|QPS|dim|k|K|M|B|fps|min|sec|s)\b",
        r"\bp(50|95|99|999)\b",
        r"\bHNSW\b|\bIVF\b|\bScaNN\b",
    ],
    "R-3RULE-twist-callback": [
        r"(?i)\b(twist|unique angle|the core decision here is|this is where)\b",
        r"(?i)\bcallback (to|of)\b",
    ],
}


def main() -> int:
    """Run sd41 self-check against schemas/meta_mlsd_canonical.yaml rules."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, overview, architecture, dataflow, formulas, "
            "production_constraints, tradeoffs, defense, verbal_outline, "
            "cheat_sheet FROM system_designs WHERE slug = ?",
            (SLUG,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        print(f"[FAIL] system_designs.slug={SLUG!r} not found")
        return 1

    (sd_id, overview, architecture, dataflow, formulas,
     prod_cons, tradeoffs, defense, verbal, cheat) = row
    fields = {
        "overview": overview,
        "architecture": architecture,
        "dataflow": dataflow,
        "formulas": formulas,
        "production_constraints": prod_cons,
        "tradeoffs": tradeoffs,
        "defense": defense,
        "verbal_outline": verbal,
        "cheat_sheet": cheat,
    }

    findings: list[str] = []

    # R-DRAWER-no-sd-drawer (top-of-field drawer table).
    drawer_top_re = re.compile(r"^\|.*sd://.*\|", re.MULTILINE)
    for name, val in fields.items():
        if val and drawer_top_re.search(val[:2000] or ""):
            findings.append(
                f"[R-DRAWER-no-sd-drawer] {name} has '| ... sd:// ... |' "
                f"table within first 2000 chars"
            )

    # R-FORBID-rhythm-philosophy (overview only).
    if overview and "整体节奏哲学" in overview:
        findings.append(
            "[R-FORBID-rhythm-philosophy] overview contains 整体节奏哲学 "
            "(duplicates cd96 §6)"
        )

    # R-FORBID-why-this-is-strong (defense only).
    if defense and re.search(r"(?i)why this is strong", defense):
        findings.append(
            "[R-FORBID-why-this-is-strong] defense contains "
            "'Why this is strong' meta-commentary (belongs in cd96)"
        )

    # R-FORBID-drawer-header-literal (all fields).
    drawer_header_re = re.compile(r"^\|\s*Doc\s*\|.*sd://", re.MULTILINE)
    for name, val in fields.items():
        if val and drawer_header_re.search(val):
            findings.append(
                f"[R-FORBID-drawer-header-literal] {name} has "
                f"'| Doc | ... sd://' header"
            )

    # Schema target_chars ranges (R-CHAR-range).
    for col, (lo, hi) in TARGET_CHAR_RANGES.items():
        n = len(fields.get(col) or "")
        if not (lo <= n <= hi):
            findings.append(
                f"[R-CHAR-range] {col} chars={n} not in [{lo}, {hi}]"
            )

    # 3-rule (section-level, at_least_one_bullet pass) for apply_3rule fields.
    for col in APPLY_3RULE_FIELDS:
        body = fields.get(col) or ""
        for rule_id, patterns in RULE_PATTERNS.items():
            hit = any(re.search(p, body) for p in patterns)
            if not hit:
                findings.append(
                    f"[{rule_id}] section {col} has no matching bullet "
                    f"(at_least_one_bullet pass)"
                )

    # Informational DIFF-DELTA log (the >70% over-prune gate fires
    # in the seed script, not here).
    total_chars = sum(len(v or "") for v in fields.values())
    delta_chars = total_chars - BASELINE_CHARS_TOTAL
    pct = (delta_chars / BASELINE_CHARS_TOTAL) * 100.0
    print(
        f"sd41 self-check: id={sd_id} slug={SLUG} chars_total={total_chars} "
        f"(baseline={BASELINE_CHARS_TOTAL}, delta={delta_chars:+d}, "
        f"{pct:+.1f}%)"
    )
    print("  per-field char counts:")
    for name, val in fields.items():
        print(f"    {name}: {len(val or ''):>6}")

    # DIFF-DELTA gate (T-865 R-DIFFDELTA-70pct) — informational only here.
    if pct < -70.0:
        findings.append(
            f"[R-DIFFDELTA-70pct] BREACH: reduction={-pct:.1f}% > 70% "
            f"(target ~40%); LIKELY OVER-DELETED — request human review"
        )

    if findings:
        print(f"\n[FAIL] {len(findings)} finding(s):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("\n[OK] all T-867 schema rules pass; DIFF-DELTA within gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
