"""Fix stray $...$ inside $$...$$ blocks in company_documents."""

import io
import re
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_PATH = "data/mle_prep.db"


def fix_stray_dollars_in_display_math(content: str) -> tuple[str, int]:
    """Remove stray $...$ wrappers inside $$...$$ display math blocks."""
    count = 0

    def fix_block(match: re.Match) -> str:
        nonlocal count
        prefix = match.group(1)  # $$ or $$\n
        inner = match.group(2)
        suffix = match.group(3)

        # Find and remove stray $ pairs inside the block
        # Pattern: $<content>$ where content doesn't contain $ or newlines
        original = inner
        inner = re.sub(r'\$([^$\n]+?)\$', r'\1', inner)

        if inner != original:
            count += 1

        return prefix + inner + suffix

    # Match $$...$$ blocks (both inline and multi-line)
    result = re.sub(
        r'(\$\$\n?)(.*?)(\n?\$\$)',
        fix_block,
        content,
        flags=re.DOTALL,
    )
    return result, count


def main():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, title, content FROM company_documents ORDER BY id"
    ).fetchall()

    total = 0
    for doc_id, title, content in rows:
        if not content:
            continue
        fixed, count = fix_stray_dollars_in_display_math(content)
        if count > 0:
            print(f"Doc {doc_id}: {title[:60]} -- fixed {count} block(s) with stray $")
            conn.execute(
                "UPDATE company_documents SET content = ? WHERE id = ?",
                (fixed, doc_id),
            )
            total += count

    conn.commit()
    conn.close()
    print(f"\nTotal: fixed stray $ in {total} display math block(s)")


if __name__ == "__main__":
    main()
