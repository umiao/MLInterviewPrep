"""KG-FIX-05 smoke screenshot capture (T-P0-613).

Captures cold-start and Expand-All views of the KG page on the current
branch and saves them under logs/kg_fix_smoke_20260425/. Suffix is
controlled by --suffix (defaults to "after").

Usage:
    python scripts/_kg_fix_smoke_screenshot.py            # writes *_after.png
    python scripts/_kg_fix_smoke_screenshot.py --suffix before  # writes *_before.png
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs" / "kg_fix_smoke_20260425"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    """Capture cold and expand-all KG screenshots."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", default="after", choices=["before", "after"])
    parser.add_argument("--url", default="http://localhost:5173/kg")
    args = parser.parse_args()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        page.goto(args.url, wait_until="networkidle", timeout=30_000)
        page.wait_for_selector('[data-testid="kg-pillar-node"]', timeout=15_000)
        time.sleep(2.5)

        cold_path = OUT / f"cold_{args.suffix}.png"
        page.screenshot(path=str(cold_path), full_page=False)
        pillar_count_cold = page.locator('[data-testid="kg-pillar-node"]').count()
        print(f"{cold_path.name} saved (pillars visible: {pillar_count_cold})")

        page.locator('[data-testid="kg-expand-all"]').click()
        time.sleep(3.0)
        expandall_path = OUT / f"expandall_{args.suffix}.png"
        page.screenshot(path=str(expandall_path), full_page=False)
        pillar_count_full = page.locator('[data-testid="kg-pillar-node"]').count()
        leaf_count = page.locator('[data-testid="kg-leaf-node"]').count()
        cat_count = page.locator('[data-testid="kg-category-node"]').count()
        print(
            f"{expandall_path.name} saved "
            f"(pillars: {pillar_count_full}, categories: {cat_count}, leaves: {leaf_count})"
        )

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
