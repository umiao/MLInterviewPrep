"""Ad-hoc audit screenshots for KG UX review (not a committed script).

Captures:
1. Default view (pillars + categories).
2. After zooming in near top-left to check pan-drag behavior.
3. After expanding a single category (checks focus preservation).
4. After clicking "Expand All" (layout density).
5. An empty-category (e.g. 'SQL Fundamentals') reveals nothing.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs" / "kg_audit"
LOG.mkdir(parents=True, exist_ok=True)


def main() -> int:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        page.goto("http://localhost:5173/kg", wait_until="networkidle", timeout=30_000)
        page.wait_for_selector('[data-testid="kg-pillar-node"]', timeout=15_000)
        time.sleep(2.5)

        page.screenshot(path=str(LOG / "01_default.png"), full_page=False)
        print("01_default.png saved")

        # Expand All to see density
        page.locator('[data-testid="kg-expand-all"]').click()
        time.sleep(2.5)
        page.screenshot(path=str(LOG / "02_expand_all.png"), full_page=False)
        leaf_count = page.locator('[data-testid="kg-leaf-node"]').count()
        print(f"02_expand_all.png saved, leaves={leaf_count}")

        # Collapse, then click one specific category (e.g. Data Structures) and capture
        page.locator('[data-testid="kg-collapse-all"]').click()
        time.sleep(1.0)
        first_cat = page.locator('[data-testid="kg-category-node"]').first
        first_cat.click()
        time.sleep(1.8)
        page.screenshot(path=str(LOG / "03_one_cat_expanded.png"), full_page=False)
        print("03_one_cat_expanded.png saved")

        # Expand all and scroll / pan to see truncation
        page.locator('[data-testid="kg-expand-all"]').click()
        time.sleep(2.0)
        # Zoom in programmatically
        page.mouse.wheel(0, -800)  # scroll up to zoom in (react-flow panOnScroll)
        time.sleep(0.8)
        page.screenshot(path=str(LOG / "04_zoomed.png"), full_page=False)
        print("04_zoomed.png saved")

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
