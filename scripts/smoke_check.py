"""Smoke check: DOM assertions + API verification.

Verifies that the dev servers are running and key pages/APIs return expected
structural data. No pixel diffs, no baselines, no thresholds.

Usage:
    python scripts/smoke_check.py          # Run all checks
    python scripts/smoke_check.py --pages  # Pages only (Playwright)
    python scripts/smoke_check.py --api    # API only (urllib)
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8100"

VISUAL_ARCHIVE_DIR = Path(__file__).resolve().parent.parent / "data" / "visual_archive"
MAX_SCREENSHOTS_PER_PAGE = 10

# Page definitions: (path, assertions)
# Each assertion is (selector, min_count, description)
PAGE_CHECKS: list[tuple[str, list[tuple[str, int, str]]]] = [
    (
        "/",
        [
            ("nav", 1, "navigation bar exists"),
            ("a[href]", 3, "at least 3 navigation links"),
        ],
    ),
    (
        "/baking",
        [
            ("[class*='recipe'], [class*='Recipe'], [data-testid*='recipe']", 1, "recipe cards visible"),
        ],
    ),
    (
        "/problems",
        [
            ("table, [class*='problem'], [class*='Problem']", 1, "problem list/table visible"),
        ],
    ),
    (
        "/system-design",
        [
            ("a[href*='system-design'], [class*='card'], [class*='Card']", 1, "system design entries visible"),
        ],
    ),
]

# API definitions: (path, min_count_or_check, description)
# min_count_or_check: int = array length >= N, "non_empty" = response body not empty
API_CHECKS: list[tuple[str, int | str, str]] = [
    ("/api/baking/recipes", 10, "baking recipes count >= 10"),
    ("/api/problems", 1, "problems count > 0"),
    ("/api/system-design/topics", 1, "system design topics count > 0"),
]


@dataclass
class CheckResult:
    """Result of a single check."""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class SmokeReport:
    """Aggregated smoke check report."""

    results: list[CheckResult] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        """Add a check result."""
        self.results.append(CheckResult(name=name, passed=passed, detail=detail))

    @property
    def all_passed(self) -> bool:
        """Return True if all checks passed."""
        return all(r.passed for r in self.results)

    @property
    def failed(self) -> list[CheckResult]:
        """Return failed checks."""
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        """Return a human-readable summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        lines = [f"[SMOKE] {passed}/{total} checks passed"]
        for r in self.failed:
            lines.append(f"  [FAIL] {r.name}: {r.detail}")
        return "\n".join(lines)


def check_server_alive(url: str, name: str) -> bool:
    """Check if a server responds at the given URL."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except (urllib.error.URLError, OSError):
        print(f"[SMOKE] {name} not reachable at {url}, skipping", file=sys.stderr)
        return False


def run_api_checks(report: SmokeReport) -> None:
    """Run API endpoint checks using urllib."""
    for path, min_count, desc in API_CHECKS:
        url = f"{BACKEND_URL}{path}"
        check_name = f"API {path}"
        try:
            req = urllib.request.Request(url, method="GET")
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body)

                if isinstance(min_count, int):
                    if not isinstance(data, list):
                        report.add(check_name, False, f"expected array, got {type(data).__name__}")
                        continue
                    if len(data) < min_count:
                        report.add(check_name, False, f"got {len(data)} items, need >= {min_count}")
                        continue
                    report.add(check_name, True, f"{len(data)} items ({desc})")
                else:
                    # "non_empty" check
                    if not body.strip():
                        report.add(check_name, False, "empty response")
                        continue
                    report.add(check_name, True, desc)

        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            report.add(check_name, False, str(e))


def _page_slug(path: str) -> str:
    """Convert a URL path to a filesystem-safe slug."""
    if path == "/":
        return "home"
    return path.strip("/").replace("/", "_")


def _cleanup_old_screenshots(slug: str, archive_dir: Path) -> None:
    """Keep only the most recent MAX_SCREENSHOTS_PER_PAGE screenshots for a page."""
    pattern = f"{slug}_*.png"
    files = sorted(archive_dir.glob(pattern), key=lambda f: f.stat().st_mtime)
    excess = len(files) - MAX_SCREENSHOTS_PER_PAGE
    if excess > 0:
        for f in files[:excess]:
            f.unlink()


def _save_screenshot(
    page: object, path: str, archive_dir: Path
) -> str | None:
    """Save a screenshot of the current page. Returns the file path or None."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    slug = _page_slug(path)
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = archive_dir / f"{slug}_{ts}.png"
    try:
        page.screenshot(path=str(filepath), full_page=True)  # type: ignore[union-attr]
        _cleanup_old_screenshots(slug, archive_dir)
        return str(filepath)
    except Exception as e:
        print(f"[SMOKE] screenshot failed for {path}: {e}", file=sys.stderr)
        return None


def run_page_checks(
    report: SmokeReport, *, archive_dir: Path | None = None
) -> None:
    """Run Playwright DOM assertion checks on key pages."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[SMOKE] playwright not installed, skipping page checks", file=sys.stderr)
        return

    if archive_dir is None:
        archive_dir = VISUAL_ARCHIVE_DIR

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()

            for path, assertions in PAGE_CHECKS:
                url = f"{FRONTEND_URL}{path}"
                check_name = f"PAGE {path}"
                try:
                    page.goto(url, wait_until="networkidle", timeout=15000)
                except Exception as e:
                    report.add(check_name, False, f"failed to load: {e}")
                    continue

                all_ok = True
                details: list[str] = []
                for selector, min_count, desc in assertions:
                    count = page.locator(selector).count()
                    if count < min_count:
                        all_ok = False
                        details.append(f"{desc}: found {count}, need >= {min_count}")
                    else:
                        details.append(f"{desc}: OK ({count})")

                if all_ok:
                    saved = _save_screenshot(page, path, archive_dir)
                    if saved:
                        details.append(f"screenshot: {saved}")

                report.add(check_name, all_ok, "; ".join(details))
        finally:
            browser.close()


def main() -> int:
    """Run smoke checks and return exit code (0=pass, 1=fail, 2=skip)."""
    parser = argparse.ArgumentParser(description="Smoke check: DOM + API verification")
    parser.add_argument("--pages", action="store_true", help="Run page checks only")
    parser.add_argument("--api", action="store_true", help="Run API checks only")
    args = parser.parse_args()

    run_pages = not args.api or args.pages
    run_api = not args.pages or args.api

    # If neither flag is set, run both
    if not args.pages and not args.api:
        run_pages = True
        run_api = True

    report = SmokeReport()

    # Check servers
    frontend_alive = check_server_alive(FRONTEND_URL, "Frontend")
    backend_alive = check_server_alive(BACKEND_URL, "Backend")

    if not frontend_alive and not backend_alive:
        print("[SMOKE] Neither server running, skipping all checks", file=sys.stderr)
        return 2  # skip

    if run_api and backend_alive:
        run_api_checks(report)
    elif run_api and not backend_alive:
        print("[SMOKE] Backend not running, skipping API checks", file=sys.stderr)

    if run_pages and frontend_alive:
        run_page_checks(report)
    elif run_pages and not frontend_alive:
        print("[SMOKE] Frontend not running, skipping page checks", file=sys.stderr)

    if not report.results:
        print("[SMOKE] No checks executed (servers not running)", file=sys.stderr)
        return 2

    print(report.summary(), file=sys.stderr)
    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
