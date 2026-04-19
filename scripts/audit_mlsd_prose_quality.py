"""Audit MLSD prose-quality mechanical gates 7/8/9/11 on a framework_node description.

Gates enforced (per id=18 Appendix A.1):

  Gate 7 - Prose ratio >= 0.30:
           non_bullet_non_table_lines / non_empty_lines >= 0.30 (document-wide).
  Gate 8 - Section Contract:
           For each `## 1.` .. `## 6.` section, the first >=60-char non-empty
           line after the heading must be prose (not starting with `-`, `*`,
           `#`, `|`, or `>`). There must also be a closing prose sentence
           before the next `##` (any prose line after the last table/bullet).
  Gate 9 - Triage signal presence:
           Any line containing /\\b(选|使用|用|pick)\\b/ must have /\\b(因为|because)\\b/
           within 1000 characters downstream in the raw text.
  Gate 11 - Patch-ban:
           Per `## ` section, prose_line_count >= bullet_line_count.

Usage:
    python scripts/audit_mlsd_prose_quality.py --node-id 92
    python scripts/audit_mlsd_prose_quality.py --node-id 92 --section 2
    python scripts/audit_mlsd_prose_quality.py --node-id 18 --report-only

Exit codes:
    0  all gates pass (or --report-only)
    1  gate failure (strict mode)
    2  bad args / node not found
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

PROSE_RATIO_MIN = 0.30

# Heading pattern: "## 1. ..." through "## 6. ..."
NUMBERED_H2 = re.compile(r"^## (\d+)\.\s+\S")
ANY_H2 = re.compile(r"^## ")
BULLET_PREFIXES = ("- ", "* ", "+ ")
TABLE_LINE = re.compile(r"^\s*\|")
# Tech-choice triage detection:
# Only flags when a trigger verb is followed within ~40 chars by what looks
# like a tech-product noun (ASCII PascalCase / all-caps token >= 3 chars,
# optionally bolded with `**`). CJK verbs alone (用户 / 选项) should not trigger.
# Verbs: 选|使用|用|pick.  Product token: `(?:\*\*)?[A-Z][A-Za-z0-9+/-]{2,}(?:\*\*)?`.
TRIAGE_RE = re.compile(
    r"(?P<verb>选|使用|用|\b[Pp]ick\b)"
    r"[\s\*\-:：,，。、\(\)（）]{0,12}"
    r"(?P<prod>(?:\*\*)?[A-Z][A-Za-z0-9+/\-]{2,}(?:\*\*)?)"
)
TRIAGE_WHY = re.compile(r"(因为|\bbecause\b)", re.IGNORECASE)

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def is_bullet(line: str) -> bool:
    s = line.lstrip()
    return any(s.startswith(p) for p in BULLET_PREFIXES)


def is_table(line: str) -> bool:
    return bool(TABLE_LINE.match(line))


def is_heading(line: str) -> bool:
    return line.lstrip().startswith("#")


def is_blockquote(line: str) -> bool:
    return line.lstrip().startswith(">")


def is_code_fence(line: str) -> bool:
    return line.lstrip().startswith("```")


def classify_prose(line: str) -> bool:
    """A line is prose iff it's non-empty, non-bullet, non-table, non-heading,
    non-blockquote, non-code-fence, non-checklist."""
    if not line.strip():
        return False
    if is_bullet(line) or is_table(line) or is_heading(line):
        return False
    if is_blockquote(line) or is_code_fence(line):
        return False
    return True


def split_sections(text: str) -> list[tuple[str, list[str]]]:
    """Split into (section_header, section_body_lines). Preamble (before first ##)
    is returned with header '__preamble__'."""
    sections: list[tuple[str, list[str]]] = []
    current_header = "__preamble__"
    current_lines: list[str] = []
    for line in text.splitlines():
        if ANY_H2.match(line):
            sections.append((current_header, current_lines))
            current_header = line.strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections.append((current_header, current_lines))
    return sections


def strip_code_blocks(lines: list[str]) -> list[str]:
    """Remove contents of fenced code blocks (they are neither prose nor bullets)."""
    out = []
    in_fence = False
    for line in lines:
        if is_code_fence(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(line)
    return out


def gate7_prose_ratio(full_text: str) -> tuple[bool, str, float]:
    """Document-wide prose ratio."""
    # Strip code fences document-wide.
    lines = strip_code_blocks(full_text.splitlines())
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return False, "no non-empty lines", 0.0
    prose_n = sum(1 for l in non_empty if classify_prose(l))
    ratio = prose_n / len(non_empty)
    ok = ratio >= PROSE_RATIO_MIN
    return ok, f"prose={prose_n}/{len(non_empty)} = {ratio:.2%} (min 30%)", ratio


def gate8_section_contract(sections: list[tuple[str, list[str]]]) -> list[str]:
    """For each numbered `## N.` section, verify opening prose and closing prose."""
    problems: list[str] = []
    for header, body in sections:
        m = NUMBERED_H2.match(header)
        if not m:
            continue
        body = strip_code_blocks(body)
        non_empty = [l for l in body if l.strip()]
        if not non_empty:
            problems.append(f"{header}: empty body")
            continue
        first = non_empty[0]
        if not classify_prose(first):
            problems.append(
                f"{header}: first non-empty line is not prose "
                f"({first.lstrip()[:50]!r})"
            )
        elif len(first.strip()) < 60:
            problems.append(
                f"{header}: opening prose too short ({len(first.strip())} chars; need >=60)"
            )
        last = non_empty[-1]
        if not classify_prose(last):
            problems.append(
                f"{header}: last non-empty line is not prose closing "
                f"({last.lstrip()[:50]!r})"
            )
    return problems


def gate9_triage_signal(full_text: str) -> list[str]:
    """For each triage verb + tech-product pair OUTSIDE blockquotes and code
    blocks, 因为/because must appear within 1000 chars downstream.

    Blockquote content is treated as illustrative (GOOD/BAD examples).
    """
    problems: list[str] = []
    lines = strip_code_blocks(full_text.splitlines())
    # Replace blockquote lines with blanks so char offsets stay stable for
    # the downstream window check.
    scrubbed = [
        "" if is_blockquote(l) else l
        for l in lines
    ]
    text = "\n".join(scrubbed)
    for m in TRIAGE_RE.finditer(text):
        start = m.start()
        window = text[start:start + 1000]
        if not TRIAGE_WHY.search(window):
            line_no = text.count("\n", 0, start) + 1
            ctx = text[max(0, start - 20):start + 80].replace("\n", " \u00b6 ")
            problems.append(
                f"L{line_no} '{m.group('verb')} {m.group('prod')}' "
                f"without 因为/because within 1000c: ...{ctx}..."
            )
    return problems


def gate11_patch_ban(sections: list[tuple[str, list[str]]]) -> list[str]:
    """Per section (any ##), prose_lines >= bullet_lines."""
    problems: list[str] = []
    for header, body in sections:
        if not ANY_H2.match(header):
            continue
        body = strip_code_blocks(body)
        bullets = sum(1 for l in body if is_bullet(l))
        prose = sum(1 for l in body if classify_prose(l))
        if bullets > prose:
            problems.append(
                f"{header}: bullet_lines={bullets} > prose_lines={prose}"
            )
    return problems


def _load_description(conn: sqlite3.Connection, node_id: int) -> str | None:
    """Try framework_nodes first, fall back to problems (for id=92 / id=198)."""
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()
    if row and row[0]:
        return row[0]
    # Problem-description fallback: Pillar-3 design problems live there.
    row = conn.execute(
        "SELECT description FROM problems WHERE id = ?", (node_id,)
    ).fetchone()
    if row and row[0]:
        return row[0]
    return None


def _maybe_one_section(text: str, section_num: int) -> str:
    """Isolate a single `## N.` section if requested."""
    lines = text.splitlines()
    start = None
    end = len(lines)
    header_re = re.compile(rf"^## {section_num}\.\s+\S")
    for i, line in enumerate(lines):
        if start is None and header_re.match(line):
            start = i
        elif start is not None and ANY_H2.match(line) and i != start:
            end = i
            break
    if start is None:
        raise SystemExit(f"[FAIL] section {section_num} not found")
    return "\n".join(lines[start:end])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--node-id", type=int, required=True,
                    help="framework_nodes.id or problems.id")
    ap.add_argument("--section", type=int, default=None,
                    help="audit only section N (e.g. 2 for `## 2. ...`)")
    ap.add_argument("--report-only", action="store_true",
                    help="print violations but always exit 0")
    args = ap.parse_args(argv)

    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}", file=sys.stderr)
        return 2
    conn = sqlite3.connect(str(DB_PATH))
    desc = _load_description(conn, args.node_id)
    conn.close()
    if desc is None:
        print(f"[FAIL] id={args.node_id} not found in framework_nodes or problems")
        return 2

    scope = f"id={args.node_id}"
    if args.section is not None:
        desc = _maybe_one_section(desc, args.section)
        scope += f" section={args.section}"

    sections = split_sections(desc)

    print(f"=== MLSD prose-quality audit: {scope} ({len(desc)} chars) ===")

    g7_ok, g7_msg, _ = gate7_prose_ratio(desc)
    g8 = gate8_section_contract(sections)
    g9 = gate9_triage_signal(desc)
    g11 = gate11_patch_ban(sections)

    print(f"\n[Gate 7 prose-ratio] {'PASS' if g7_ok else 'FAIL'}: {g7_msg}")
    print(f"\n[Gate 8 section-contract] {'PASS' if not g8 else f'FAIL ({len(g8)})'}")
    for p in g8:
        print(f"  - {p}")
    print(f"\n[Gate 9 triage-signal] {'PASS' if not g9 else f'FAIL ({len(g9)})'}")
    for p in g9[:20]:
        print(f"  - {p}")
    if len(g9) > 20:
        print(f"  ... and {len(g9) - 20} more")
    print(f"\n[Gate 11 patch-ban] {'PASS' if not g11 else f'FAIL ({len(g11)})'}")
    for p in g11:
        print(f"  - {p}")

    all_pass = g7_ok and not g8 and not g9 and not g11
    print(f"\n=== Overall: {'PASS' if all_pass else 'FAIL'} ===")

    if args.report_only:
        return 0
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
