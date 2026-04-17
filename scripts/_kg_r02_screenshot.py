"""Capture Playwright screenshots of the /kg page after R02 visual encoding.

Saves an overview shot (semi-expanded) and a category-expanded shot showing
leaf nodes with completeness arcs + importance sizing.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OVERVIEW = ROOT / "logs" / "kg_r02_overview.png"
LEAVES = ROOT / "logs" / "kg_r02_leaves_expanded.png"


def main() -> int:
    OVERVIEW.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        page.goto("http://localhost:5173/kg", wait_until="networkidle", timeout=30_000)
        page.wait_for_selector('[data-testid="kg-canvas"]', timeout=10_000)
        page.wait_for_selector('[data-testid="kg-pillar-node"]', timeout=15_000)
        time.sleep(2.5)
        page.screenshot(path=str(OVERVIEW), full_page=False)
        print(f"Saved: {OVERVIEW}")

        # Navigate with category n9 (Data Structures, 8 leaves) pre-expanded
        # via URL state so we can demonstrate completeness arcs on leaves.
        page.goto(
            "http://localhost:5173/kg?expanded=n9",
            wait_until="networkidle",
            timeout=30_000,
        )
        page.wait_for_selector('[data-testid="kg-leaf-node"]', timeout=15_000)
        time.sleep(3.0)
        page.screenshot(path=str(LEAVES), full_page=False)
        print(f"Saved: {LEAVES}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
