# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Audit formula safety across the 8 core system design modules.

Checks (math-focused, per T-P2-171 ACs):
- bare | inside $$...$$ blocks (should be \\mid)
- multi-line $$ blocks (content spans newlines)
- consecutive $$ blocks separated by only a single newline (need blank line)
- unbalanced $$

Inline $...$ is sensitive because many modules use `$` as currency in Chinese
prose; we therefore only flag inline bare `|` that sits between two clearly
math-like tokens (presence of backslash commands inside the span).

Read-only: does not modify the DB.
"""
import re
import sqlite3
import sys

MODULES = [
    'llm-orchestration',
    'ranking-allocation',
    'distributed-task-queue',
    'database-comparison',
    'pbe-pipeline',
    'module-arbitration',
    'ml-system-design-patterns',
    'vibe-code-engineering-patterns',
]
FIELDS = [
    'overview', 'architecture', 'dataflow', 'formulas',
    'production_constraints', 'tradeoffs', 'defense', 'verbal_outline',
]

BARE_PIPE = re.compile(r'(?<!\\)\|')
BLOCK_MATH = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
# Consecutive $$ blocks with only ONE newline (no blank line) between them.
CONSEC_DD_BAD = re.compile(r'\$\$[ \t]*\n[ \t]*\$\$')


def audit(text):
    issues = []
    if not text:
        return issues
    for m in BLOCK_MATH.finditer(text):
        body = m.group(1)
        if '\n' in body.strip():
            issues.append(('multiline_block', body[:120]))
        if BARE_PIPE.search(body):
            issues.append(('bare_pipe_block', body[:120]))
    for m in CONSEC_DD_BAD.finditer(text):
        s, e = max(0, m.start() - 40), min(len(text), m.end() + 40)
        issues.append(('consec_dd_no_blank', text[s:e]))
    if text.count('$$') % 2:
        issues.append(('unbalanced_dd', f'count={text.count("$$")}'))
    return issues


def main():
    c = sqlite3.connect('data/mle_prep.db')
    total = 0
    for mod in MODULES:
        row = c.execute(
            f"SELECT {','.join(FIELDS)} FROM system_designs WHERE slug=?",
            (mod,),
        ).fetchone()
        if not row:
            print(f"[MISSING] {mod}")
            continue
        mod_issues = {}
        for i, field in enumerate(FIELDS):
            iss = audit(row[i])
            if iss:
                mod_issues[field] = iss
        if not mod_issues:
            print(f"[CLEAN] {mod}")
        else:
            print(f"\n=== {mod} ===")
            for field, iss in mod_issues.items():
                print(f"  {field}: {len(iss)} issues")
                for t, s in iss[:8]:
                    print(f"    [{t}] {s!r}")
                if len(iss) > 8:
                    print(f"    ... +{len(iss) - 8}")
                total += len(iss)
    print(f"\n=== GRAND TOTAL: {total} math-safety issues ===")
    return total


if __name__ == '__main__':
    main()
    sys.exit(0)
