"""T-P0-708 e2e verification: extract all python code blocks from
docs/drafts/lr_golden_v1.md, concatenate the class skeleton + helper
methods + fit/predict + the trailing e2e test block, and execute. Must
exit 0 with no exceptions, and stdout should print the MSE line.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DRAFT = REPO_ROOT / "docs" / "drafts" / "lr_golden_v1.md"


def main() -> int:
    text = DRAFT.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)
    if len(blocks) != 6:
        print(f"[FAIL] expected 6 python blocks, got {len(blocks)}")
        return 1

    skeleton = blocks[0]
    methods = blocks[1:5]
    e2e = blocks[5]

    method_blocks_indented = []
    for m in methods:
        lines = m.split("\n")
        method_blocks_indented.append("\n".join("    " + ln if ln else ln for ln in lines))

    full_module = skeleton + "\n\n" + "\n\n".join(method_blocks_indented) + "\n\n" + e2e

    out = REPO_ROOT / "logs" / "_lr_e2e_assembled.py"
    out.write_text(full_module, encoding="utf-8")

    namespace: dict = {}
    try:
        exec(compile(full_module, str(out), "exec"), namespace)
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] e2e raised: {exc!r}")
        return 1

    print("[PASS] e2e block executed cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
