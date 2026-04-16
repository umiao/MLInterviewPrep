"""Sanity scan for the IPS drill note: non-ASCII chars + orphan $ signs."""

from __future__ import annotations

import re
from pathlib import Path


def main() -> None:
    """Run scans and print pass/fail."""
    doc = Path(__file__).resolve().parent.parent / "docs" / "google_ips_counterfactual_drill.md"
    content = doc.read_text(encoding="utf-8")

    non_ascii = [c for c in content if ord(c) > 127]
    print(f"[CHECK] non-ascii chars: {len(non_ascii)}")

    no_code = re.sub(r"```[\s\S]*?```", "", content)
    no_math = re.sub(r"\$\$[\s\S]*?\$\$", "", no_code)
    no_inline_code = re.sub(r"`[^`]+`", "", no_math)
    no_inline_math = re.sub(r"\$[^$\n]+\$", "", no_inline_code)
    singles = re.findall(r"(?<!\$)\$(?!\$)", no_inline_math)
    print(f"[CHECK] orphan dollar signs: {len(singles)}")
    print(f"[CHECK] content length: {len(content)} chars")


if __name__ == "__main__":
    main()
