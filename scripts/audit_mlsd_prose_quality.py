"""Audit MLSD prose-quality mechanical gates 7/8/9/11/12 on a framework_node description.

Gates enforced (per id=18 Appendix A.1 + A.1.v2 amendment):

  Gate 7 - Prose ratio >= 0.30:
           non_bullet_non_table_lines / non_empty_lines >= 0.30 (document-wide).
  Gate 8 - Section Contract:
           For each `## 1.` .. `## 6.` section, the first >=60-char non-empty
           line after the heading must be prose (not starting with `-`, `*`,
           `#`, `|`, or `>`). There must also be a closing prose sentence
           before the next `##` (any prose line after the last table/bullet).
  Gate 9 - Triage signal presence:
           Any line containing an expanded triage verb
           /(选|使用|用|采用|切换到|归到|改用|上|走|挂|[Pp]ick|[Uu]se|[Gg]o with)/
           followed by a product token (min length 2 so `S2`, `S3`, `FA`, `Go`
           get caught) must have /因为|because/ within 1000 characters
           downstream. Blockquotes are scrubbed (illustrative examples).
  Gate 11 - Patch-ban:
           Per `## ` section, prose_line_count >= bullet_line_count.
  Gate 12 - Triage depth (A.1.v2):
           For each Gate-9 triage match, the NEXT 2000 characters must contain
           >=3 bold product names (matching `\\*\\*[A-Z][^*]+\\*\\*`) AND >=3
           why-not tokens (`但|不用|淘汰|更合适|更适合|why-not`). Enforces
           Rule 3's >=3-alternative requirement mechanically.

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

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

PROSE_RATIO_MIN = 0.30

# Heading pattern: "## 1. ..." through "## 6. ..."
NUMBERED_H2 = re.compile(r"^## (\d+)\.\s+\S")
ANY_H2 = re.compile(r"^## ")
BULLET_PREFIXES = ("- ", "* ", "+ ")
TABLE_LINE = re.compile(r"^\s*\|")
# Tech-choice triage detection (A.1.v2 - expanded 2026-04-18):
# Only flags when a trigger verb is followed within ~12 chars by what looks
# like a tech-product noun (ASCII PascalCase / all-caps token >= 2 chars so
# short brand names like `S2`, `S3`, `Go`, `Ch`, `FA` get caught), optionally
# bolded with `**`. Single-char CJK verbs (上/走/挂) only fire when the 12-char
# gap terminates on an ASCII capital, so plain prose like "上次" or "走查"
# (CJK-CJK) is not triggered.
#
# Verb list (expanded in A.1.v2):
#   CJK: 选|使用|用|采用|切换到|归到|改用|上|走|挂
#   EN:  Pick|Use|Go with
TRIAGE_RE = re.compile(
    r"(?P<verb>选|使用|用|采用|切换到|归到|改用|上|走|挂"
    r"|\b[Pp]ick\b|\b[Uu]se\b|\b[Gg]o with\b)"
    r"[\s\*\-:：,，。、\(\)（）]{0,12}"
    r"(?P<prod>(?:\*\*)?[A-Z][A-Za-z0-9+/\-]{1,}(?:\*\*)?)"
)
TRIAGE_WHY = re.compile(r"(因为|\bbecause\b)", re.IGNORECASE)

# Gate 12 (A.1.v2): per-match depth check.
# Count bold product names in the 2000-char window following a triage match.
# Also count why-not tokens: 但 / 不用 / 淘汰 / 更合适 / 更适合 / why-not.
BOLD_PRODUCT_RE = re.compile(r"\*\*[A-Z][^*]+\*\*")
WHY_NOT_RE = re.compile(r"但|不用|淘汰|更合适|更适合|why-not", re.IGNORECASE)
GATE12_WINDOW_CHARS = 2000
GATE12_MIN_ALTS = 3
GATE12_MIN_WHYNOT = 3

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
    return not (is_blockquote(line) or is_code_fence(line))


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


def gate12_triage_depth(full_text: str) -> list[str]:
    """Per Gate-9 match, next GATE12_WINDOW_CHARS chars must have
    >=GATE12_MIN_ALTS bold product names AND >=GATE12_MIN_WHYNOT why-not tokens.

    Blockquotes and code fences are scrubbed (same as Gate 9) so illustrative
    triage examples in `> **GOOD**:` callouts don't trigger the check.
    """
    problems: list[str] = []
    lines = strip_code_blocks(full_text.splitlines())
    scrubbed = [
        "" if is_blockquote(l) else l
        for l in lines
    ]
    text = "\n".join(scrubbed)
    for m in TRIAGE_RE.finditer(text):
        start = m.start()
        window = text[start:start + GATE12_WINDOW_CHARS]
        alt_count = len(BOLD_PRODUCT_RE.findall(window))
        why_count = len(WHY_NOT_RE.findall(window))
        if alt_count < GATE12_MIN_ALTS or why_count < GATE12_MIN_WHYNOT:
            line_no = text.count("\n", 0, start) + 1
            ctx = text[max(0, start - 20):start + 80].replace("\n", " \u00b6 ")
            problems.append(
                f"L{line_no} '{m.group('verb')} {m.group('prod')}' "
                f"alts={alt_count}/{GATE12_MIN_ALTS} "
                f"why-not={why_count}/{GATE12_MIN_WHYNOT}: ...{ctx}..."
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
    g12 = gate12_triage_depth(desc)

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
    print(f"\n[Gate 12 triage-depth] {'PASS' if not g12 else f'FAIL ({len(g12)})'}")
    for p in g12[:20]:
        print(f"  - {p}")
    if len(g12) > 20:
        print(f"  ... and {len(g12) - 20} more")

    all_pass = g7_ok and not g8 and not g9 and not g11 and not g12
    print(f"\n=== Overall: {'PASS' if all_pass else 'FAIL'} ===")

    if args.report_only:
        return 0
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
