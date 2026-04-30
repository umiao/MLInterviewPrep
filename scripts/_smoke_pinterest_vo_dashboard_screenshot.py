"""Capture Dashboard screenshot for Pinterest VO verification (T-P0-655 SECONDARY).

Per task spec:
- Playwright headless screenshot of http://localhost:5173/ (Dashboard root)
- Visible-text grep finds all 5 interviewer names: Yiyang Zhang, Daniel Liu,
  Jiankai Sun, Yijian Xiang, Zihao Zhang
- Screenshot saved to logs/pinterest_vo_dashboard_<timestamp>.png

This is a one-shot smoke test (idempotent re-runnable).
"""
from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

EXPECTED_NAMES: list[str] = [
    "Yiyang Zhang",
    "Daniel Liu",
    "Jiankai Sun",
    "Yijian Xiang",
    "Zihao Zhang",
]


def main() -> int:
    """Render Dashboard, save screenshot, grep visible text for all 5 names."""
    repo_root = Path(__file__).resolve().parents[1]
    logs_dir = repo_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    timestamp = _dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    screenshot_path = logs_dir / f"pinterest_vo_dashboard_{timestamp}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 1200})
        page = context.new_page()

        page.goto("http://localhost:5173/", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(screenshot_path), full_page=True)

        body_text = page.locator("body").inner_text()
        browser.close()

    found: dict[str, bool] = {n: (n in body_text) for n in EXPECTED_NAMES}
    missing = [n for n, ok in found.items() if not ok]

    print(f"Screenshot saved to: {screenshot_path.relative_to(repo_root)}")
    print(f"Screenshot size: {screenshot_path.stat().st_size} bytes")
    print()
    print("Visible-text grep results:")
    for name, ok in found.items():
        marker = "[OK]" if ok else "[MISSING]"
        print(f"  {marker} {name}")

    if missing:
        print()
        print(f"FAIL: missing names in visible text: {missing}")
        return 1

    print()
    print("PASS: all 5 interviewer names visible on Dashboard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
