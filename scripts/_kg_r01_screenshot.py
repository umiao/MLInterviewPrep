"""Capture a Playwright screenshot of the /kg React Flow LR mind-map."""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs" / "kg_r01_reactflow_lr_mindmap.png"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        page.goto("http://localhost:5173/kg", wait_until="networkidle", timeout=30_000)
        page.wait_for_selector('[data-testid="kg-canvas"]', timeout=10_000)
        page.wait_for_selector('[data-testid="kg-pillar-node"]', timeout=15_000)
        time.sleep(2.0)
        page.screenshot(path=str(OUT), full_page=False)
        print(f"Saved: {OUT}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
