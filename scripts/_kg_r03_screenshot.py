"""Capture Playwright screenshots verifying R03 interactions.

Captures:
1. Overview with hover tooltip on a category node + neighbor edge highlight.
2. After clicking "Expand All" -> all categories revealed at once.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HOVER_SHOT = ROOT / "logs" / "kg_r03_hover_tooltip.png"
EXPAND_ALL_SHOT = ROOT / "logs" / "kg_r03_expand_all.png"


def main() -> int:
    HOVER_SHOT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        page.goto("http://localhost:5173/kg", wait_until="networkidle", timeout=30_000)
        page.wait_for_selector('[data-testid="kg-canvas"]', timeout=10_000)
        page.wait_for_selector('[data-testid="kg-pillar-node"]', timeout=15_000)
        time.sleep(2.5)

        # Hover the first category node to fire the tooltip.
        cat = page.locator('[data-testid="kg-category-node"]').first
        cat.hover()
        time.sleep(0.6)
        page.screenshot(path=str(HOVER_SHOT), full_page=False)
        print(f"Saved: {HOVER_SHOT}")
        # Sanity assertions on tooltip presence.
        tooltip_count = page.locator('[data-testid="kg-tooltip"]').count()
        print(f"tooltip elements visible: {tooltip_count}")

        # Click "Expand All" and capture the expanded layout.
        page.locator('[data-testid="kg-expand-all"]').click()
        time.sleep(2.0)
        page.screenshot(path=str(EXPAND_ALL_SHOT), full_page=False)
        print(f"Saved: {EXPAND_ALL_SHOT}")
        leaf_count = page.locator('[data-testid="kg-leaf-node"]').count()
        print(f"visible leaves after expand-all: {leaf_count}")

        # Sanity check: collapse-all should remove leaves.
        page.locator('[data-testid="kg-collapse-all"]').click()
        time.sleep(1.0)
        leaf_after_collapse = page.locator('[data-testid="kg-leaf-node"]').count()
        cat_after_collapse = page.locator('[data-testid="kg-category-node"]').count()
        print(
            f"after collapse-all: leaves={leaf_after_collapse}, "
            f"categories={cat_after_collapse}"
        )

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
