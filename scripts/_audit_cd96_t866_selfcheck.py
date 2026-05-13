"""In-session schema self-check for cd96 after T-P0-866 (one-off audit).

Encodes the cd96_playbook rules from `schemas/meta_mlsd_canonical.yaml` directly,
since T-872's `audit_meta_mlsd_3rule.py` is not yet built. Stand-in until T-872.

Exit 0 = clean (all 866-relevant rules pass). Exit 1 = at least one finding.
Throwaway: prefixed with `_` per repo convention; do NOT promote to permanent.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def main() -> int:
    """Run cd96 self-check against schemas/meta_mlsd_canonical.yaml rules."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        content = conn.execute(
            "SELECT content FROM company_documents WHERE id = 96"
        ).fetchone()[0]
    finally:
        conn.close()

    findings: list[str] = []

    # R-FORBID-per-twist-4-section-template (scope: cd96_playbook)
    forbidden = re.compile(
        r"Per-twist 4-section template|Per-twist 4\s*段推导模板",
        re.IGNORECASE,
    )
    if forbidden.search(content):
        findings.append(
            "[R-FORBID-per-twist-4-section-template] pattern matched"
        )

    # Sections (heading_regex) — all 9 must be present.
    section_regexes = [
        ("§1", r"^## 1\.\s*节奏.*Timing Skeleton"),
        ("§2", r"^## 2\.\s*Twist"),
        ("§3", r"^## 3\.\s*4 Strong Moments"),
        ("§4", r"^## 4\.\s*ML-Native Vocabulary"),
        ("§5", r"^## 5\.\s*Framing.*Body.*Strong.*Zoom"),
        ("§6", r"^## 6\.\s*偏好节奏.*Meta-rules"),
        ("§7", r"^## 7\.\s*减少澄清"),
        ("§8", r"^## 8\.\s*E4.*E5"),
        ("§9", r"^## 9\.\s*30\s*秒"),
    ]
    for sid, pat in section_regexes:
        if not re.search(pat, content, re.MULTILINE):
            findings.append(f"[section] missing {sid} heading (/{pat}/)")

    # R-TIMING-row-4tag: Section 1 timing skeleton table.
    lines = content.splitlines()
    sec1_start = next(
        (i for i, ln in enumerate(lines) if ln.startswith("## 1.")), None
    )
    if sec1_start is None:
        findings.append("[R-TIMING-row-4tag] Section 1 heading not found")
    else:
        sec1_end = next(
            (
                i
                for i, ln in enumerate(lines[sec1_start + 1:], sec1_start + 1)
                if ln.startswith("## ")
            ),
            len(lines),
        )
        data_rows = [
            ln for ln in lines[sec1_start:sec1_end]
            if ln.lstrip().startswith("|") and "---" not in ln
        ][1:]  # skip header
        if len(data_rows) != 9:
            findings.append(
                f"[R-TIMING-row-4tag] expected 9 data rows, got {len(data_rows)}"
            )
        rhythm_vocab = {
            "Framing",
            "Data",
            "Model",
            "Bias",
            "Evaluation",
            "Zoomout",
            "Serving",
            "QA",
        }
        slot_vocab = {"#1", "#2", "#3", "#4", "-"}
        for i, row in enumerate(data_rows, 1):
            cells = [c.strip() for c in row.split("|")[1:-1]]
            if len(cells) != 6:
                findings.append(
                    f"[R-TIMING-row-4tag] row {i}: {len(cells)} cells (need 6)"
                )
                continue
            (time_band, rhythm, slot, twist, scale, trade) = cells
            if not time_band:
                findings.append(
                    f"[R-TIMING-row-4tag] row {i}: time_band empty"
                )
            if rhythm not in rhythm_vocab:
                findings.append(
                    f"[R-TIMING-row-4tag] row {i}: rhythm {rhythm!r} "
                    f"not in vocab {sorted(rhythm_vocab)}"
                )
            if slot not in slot_vocab:
                findings.append(
                    f"[R-TIMING-row-4tag] row {i}: strong_moment_slot {slot!r} "
                    f"not in vocab {sorted(slot_vocab)}"
                )
            if not trade:
                findings.append(
                    f"[R-TIMING-row-4tag] row {i}: tag_trade empty (REQUIRED)"
                )
            # twist + scale: '-' or non-empty (empty cell not allowed; we
            # treat empty as a finding too).
            if not twist:
                findings.append(
                    f"[R-TIMING-row-4tag] row {i}: tag_twist empty "
                    f"(use '-' if N/A)"
                )
            if not scale:
                findings.append(
                    f"[R-TIMING-row-4tag] row {i}: tag_scale empty "
                    f"(use '-' if N/A)"
                )

    # Section 2 keep/delete subsections.
    if "### 2.2" in content:
        findings.append("[§2.2 delete] '### 2.2' heading still present")
    for keep in ("### 2.1", "### 2.3", "### 2.4"):
        if keep not in content:
            findings.append(f"[§2 keep_subsections] {keep} missing")

    # Section-level 3-rule (apply_3rule sections: §1 (via timing), §2, §3, §5, §7, §9)
    # Heuristic per schema three_rule.rules (at_least_one_bullet pass).
    rules = {
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
            r"\bHNSW\b|\bIVF\b",
        ],
        "R-3RULE-twist-callback": [
            r"(?i)\b(twist|unique angle|the core decision here is|this is where)\b",
            r"(?i)\bcallback (to|of)\b",
        ],
    }

    # Apply at section level for sections with apply_3rule=true.
    apply_3rule_sections = ["§1", "§2", "§3", "§5", "§7", "§9"]
    heading_idx: dict[str, int] = {}
    for sid, pat in section_regexes:
        m = re.search(pat, content, re.MULTILINE)
        if m:
            heading_idx[sid] = m.start()
    sorted_ids = sorted(heading_idx, key=lambda s: heading_idx[s])
    for i, sid in enumerate(sorted_ids):
        if sid not in apply_3rule_sections:
            continue
        start = heading_idx[sid]
        end = (
            heading_idx[sorted_ids[i + 1]]
            if i + 1 < len(sorted_ids)
            else len(content)
        )
        body = content[start:end]
        for rule_id, patterns in rules.items():
            hit = any(
                re.search(p, body, re.IGNORECASE if "(?i)" in p else 0)
                for p in patterns
            )
            if not hit:
                findings.append(
                    f"[{rule_id}] section {sid} has no matching bullet "
                    f"(at_least_one_bullet pass)"
                )

    # Forbidden literal in cd96 only (R-FORBID-rhythm-philosophy is scoped to
    # sd-golden, NOT cd96; R-FORBID-drawer-header-literal scoped to sd-golden).
    # Only R-FORBID-per-twist-4-section-template applies here.

    # Drawer must contain the 2 currently-seeded sd:// slugs (the 4-slug
    # requirement is enforced by T-P0-871, not T-P0-866).
    for slug in ("meta-reels-golden", "meta-top3-comments-golden"):
        if f"sd://{slug}" not in content:
            findings.append(f"[drawer] sd://{slug} missing from cd96")

    print(f"cd96 self-check: chars={len(content)}")
    if findings:
        print(f"[FAIL] {len(findings)} finding(s):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("[OK] all schema rules for T-866 scope pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
