"""T-P0-119: Fix formula rendering in company_documents.

Scans all company_documents for formulas trapped in code blocks and converts
them to proper $$...$$ math blocks.
"""

import io
import re
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_PATH = "data/mle_prep.db"

# Math indicators that distinguish formula blocks from real code blocks
MATH_INDICATORS = [
    "\\frac", "\\sum", "\\prod", "\\int", "\\nabla", "\\partial",
    "\\theta", "\\alpha", "\\beta", "\\sigma", "\\mu", "\\mathbb",
    "\\text{", "\\log", "\\exp", "\\max", "\\min", "_{", "^{",
    "\\cdot", "\\rightarrow", "\\hat", "\\mathcal", "\\left", "\\right",
    "\\varepsilon", "\\pi",
    # Plain text math indicators (Unicode/ASCII)
    "L_SFT", "L_RM", "L_DPO", "L_PPO", "L_KD", "L_CE",
    "D_KL", "π_SFT", "π_old", "$\\pi", "$r_\\phi",
    "r(x,y)", "r(y_w)", "P(y_w", "E_{", "E[", "Σ_t",
    "p_teacher", "p_student", "p_i^(T)", "exp(z_i",
    "x_{t-1}", "UNet(x_t",
    "max_π", "max_{",
]

# Language tags that indicate real code (not formulas)
CODE_LANGS = {
    "python", "bash", "sql", "json", "javascript", "shell",
    "yaml", "html", "css", "typescript", "jsx", "tsx", "go",
    "java", "c", "cpp", "rust", "ruby", "php", "swift",
}


def is_formula_block(lang: str, content: str) -> bool:
    """Determine if a code block contains formula content rather than code."""
    if lang.lower() in CODE_LANGS:
        return False
    return any(ind in content for ind in MATH_INDICATORS)


def clean_inline_dollars(text: str) -> str:
    """Remove stray $...$ wrappers from within a formula that will be wrapped in $$."""
    # Pattern: $\something$ -> \something (when inside $$)
    # But preserve intentional inline math
    result = text
    # Remove $ wrapping around LaTeX commands like $\pi_\theta$ -> \pi_\theta
    result = re.sub(r'\$(\\.+?)\$', r'\1', result)
    # Remove $ wrapping around simple expressions like $\beta$ -> \beta
    result = re.sub(r'\$(\\\w+)\$', r'\1', result)
    return result


def convert_plain_text_to_latex(text: str) -> str:
    """Convert plain-text math (Unicode symbols) to proper LaTeX."""
    replacements = [
        ("−", "-"),  # Unicode minus -> ASCII minus
        ("·", "\\cdot "),
        ("≻", "\\succ "),
        ("≈", "\\approx "),
        ("→", "\\rightarrow "),
        ("‖", "\\| "),
        ("Σ_t", "\\sum_t"),
        ("Σ_j", "\\sum_j"),
        ("Σ_y", "\\sum_y"),
        ("π_SFT", "\\pi_{\\text{SFT}}"),
        ("π_old", "\\pi_{\\text{old}}"),
        ("π(y|x)", "\\pi(y|x)"),
        ("π(y_t", "\\pi(y_t"),
    ]
    result = text
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def convert_single_formula(content: str) -> str:
    """Convert a single formula block content to proper LaTeX display math."""
    content = content.strip()

    # Case 1: Already wrapped in $$...$$
    if content.startswith("$$") and content.endswith("$$"):
        inner = content[2:-2].strip()
        return f"\n$$\n{inner}\n$$\n"

    # Case 2: Wrapped in single $...$
    if content.startswith("$") and content.endswith("$") and not content.startswith("$$"):
        inner = content[1:-1].strip()
        return f"\n$$\n{inner}\n$$\n"

    # Case 3: Contains mixed $...$ inline math within plain text
    # Clean up inline dollars and convert to display math
    cleaned = clean_inline_dollars(content)
    cleaned = convert_plain_text_to_latex(cleaned)

    return f"\n$$\n{cleaned}\n$$\n"


def convert_multiline_formula(content: str) -> str:
    """Convert a multi-line formula/summary block to proper display math."""
    lines = content.strip().split("\n")

    # Check if it's a summary card with labels (like the formula cheat sheet)
    has_labels = any(":" in line and not line.strip().startswith("$") for line in lines if line.strip())

    if has_labels:
        # Convert each labeled formula line to its own display math block
        result_parts = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result_parts.append("")
                continue

            # Check if this is a label: formula line
            if ":" in stripped:
                parts = stripped.split(":", 1)
                label = parts[0].strip()
                formula = parts[1].strip() if len(parts) > 1 else ""

                if formula:
                    formula = clean_inline_dollars(formula)
                    formula = convert_plain_text_to_latex(formula)
                    result_parts.append(f"**{label}:**\n\n$$\n{formula}\n$$\n")
                else:
                    result_parts.append(f"**{label}**\n")
            else:
                # Standalone formula line
                cleaned = clean_inline_dollars(stripped)
                cleaned = convert_plain_text_to_latex(cleaned)
                result_parts.append(f"$$\n{cleaned}\n$$\n")

        return "\n" + "\n".join(result_parts) + "\n"
    else:
        # Multi-line formula without labels - use aligned environment or keep as-is
        cleaned_lines = []
        for line in lines:
            cleaned = clean_inline_dollars(line)
            cleaned = convert_plain_text_to_latex(cleaned)
            cleaned_lines.append(cleaned)
        inner = "\n".join(cleaned_lines)
        return f"\n$$\n{inner}\n$$\n"


def fix_document(doc_id: int, content: str) -> tuple[str, int]:
    """Fix all formula code blocks in a document. Returns (fixed_content, count)."""
    fixed = content
    count = 0

    # Find all code blocks (no language tag or non-code language tag)
    pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)

    def replace_block(match: re.Match) -> str:
        nonlocal count
        lang = match.group(1)
        block_content = match.group(2)

        if not is_formula_block(lang, block_content):
            return match.group(0)  # Keep as-is

        count += 1
        lines = block_content.strip().split("\n")

        # Single-line formula
        if len(lines) == 1:
            return convert_single_formula(block_content)

        # Multi-line: check if it's a two-line formula (like the aligned ones)
        # or a summary/cheat sheet block
        if len(lines) <= 3 and not any(":" in l for l in lines if l.strip()):
            return convert_multiline_formula(block_content)

        # Large multi-line block (summary/cheat sheet)
        return convert_multiline_formula(block_content)

    fixed = pattern.sub(replace_block, fixed)
    return fixed, count


def main():
    conn = sqlite3.connect(DB_PATH)

    # Get all documents
    rows = conn.execute(
        "SELECT id, title, content FROM company_documents ORDER BY id"
    ).fetchall()

    total_fixed = 0
    for doc_id, title, content in rows:
        if not content:
            continue

        fixed_content, count = fix_document(doc_id, content)

        if count > 0:
            print(f"Doc {doc_id}: {title[:60]} -- fixed {count} formula code block(s)")
            conn.execute(
                "UPDATE company_documents SET content = ? WHERE id = ?",
                (fixed_content, doc_id),
            )
            total_fixed += count

    conn.commit()
    conn.close()
    print(f"\nTotal: fixed {total_fixed} formula code blocks across all documents")


if __name__ == "__main__":
    main()
