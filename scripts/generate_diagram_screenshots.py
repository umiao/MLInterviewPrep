"""Generate PNG screenshots from HTML system design diagrams using Playwright.

Usage:
    python scripts/generate_diagram_screenshots.py
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HTML_DIR = PROJECT_ROOT / "src" / "frontend" / "public" / "static" / "system-designs" / "html"
OUTPUT_DIR = PROJECT_ROOT / "src" / "frontend" / "public" / "static" / "system-designs"

DIAGRAMS = [
    "module_arbitration",
    "llm_orchestration",
    "pbe_pipeline",
    "ranking_allocation",
    "database_comparison",
    "distributed_task_queue",
]


def main() -> None:
    """Screenshot each HTML diagram to PNG."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1680, "height": 1200})

        for name in DIAGRAMS:
            html_path = HTML_DIR / f"{name}.html"
            out_path = OUTPUT_DIR / f"{name}.png"

            if not html_path.exists():
                print(f"[SKIP] {html_path} not found", file=sys.stderr)
                continue

            file_url = html_path.as_uri()
            page.goto(file_url)
            page.wait_for_load_state("networkidle")

            # Screenshot the body element directly to auto-crop whitespace
            body = page.locator("body")
            body.screenshot(path=str(out_path))
            print(f"[OK] {name}.png ({out_path.stat().st_size // 1024} KB)")

        browser.close()

    print(f"\nDone. {len(DIAGRAMS)} diagrams generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
