"""Fetch LeetCode problem descriptions from leetcode.ca for problems missing descriptions.

Usage:
    python scripts/fetch_lc_descriptions.py [--limit N] [--dry-run] [--start-from N]

leetcode.ca hosts problems 1-1857. Problems with leetcode_id > 1857 are skipped.
"""

import argparse
import re
import sqlite3
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
BASE_URL = "https://leetcode.ca/all/{}.html"
MAX_LC_ID = 1857
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class DescriptionExtractor(HTMLParser):
    """Extract problem description from leetcode.ca HTML.

    The description lives inside <div class="markdown-body div-width">,
    ending before the first <h3> tag (Difficulty/Lock/Company sections).
    """

    def __init__(self) -> None:
        super().__init__()
        self._in_body = False
        self._depth = 0
        self._capture = True
        self._parts: list[str] = []
        self._tag_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)
        cls = attr_dict.get("class", "")

        # Enter the markdown-body div
        if tag == "div" and "markdown-body" in cls:
            self._in_body = True
            self._depth = 1
            return

        if not self._in_body:
            return

        if tag == "div":
            self._depth += 1

        # Stop capturing at the Difficulty/Lock/Company sections
        if tag == "h3":
            self._capture = False
            return

        if not self._capture:
            return

        # Convert HTML tags to plain text markers
        if tag == "br":
            self._parts.append("\n")
        elif tag == "p":
            self._parts.append("\n\n")
        elif tag == "li":
            self._parts.append("\n- ")
        elif tag == "pre" or tag in ("ol", "ul"):
            self._parts.append("\n")
        elif tag == "strong" or tag == "b":
            self._parts.append("")
        elif tag == "code":
            self._parts.append("`")
        elif tag == "sup":
            self._parts.append("^")

        self._tag_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self._in_body:
            return

        if tag == "div":
            self._depth -= 1
            if self._depth <= 0:
                self._in_body = False
                return

        if not self._capture:
            return

        if tag == "code":
            self._parts.append("`")
        elif tag == "p":
            pass  # newline already added at start
        elif tag == "pre":
            self._parts.append("\n")

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._in_body and self._capture:
            self._parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._in_body and self._capture:
            entities = {"lt": "<", "gt": ">", "amp": "&", "quot": '"', "nbsp": " "}
            self._parts.append(entities.get(name, f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self._in_body and self._capture:
            try:
                char = chr(int(name[1:], 16)) if name.startswith("x") else chr(int(name))
                self._parts.append(char)
            except (ValueError, OverflowError):
                self._parts.append(f"&#{name};")

    def get_description(self) -> str:
        """Return cleaned description text."""
        text = "".join(self._parts)
        # Clean up HTML indentation whitespace
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        text = "\n".join(lines)
        # Collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        return text


def fetch_description(leetcode_id: int) -> str | None:
    """Fetch and parse problem description from leetcode.ca.

    Returns the description text, or None if the page doesn't exist or parsing fails.
    """
    url = BASE_URL.format(leetcode_id)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        if e.code == 404:
            return None
        raise
    except (URLError, TimeoutError):
        return None

    parser = DescriptionExtractor()
    parser.feed(html)
    desc = parser.get_description()

    if not desc or len(desc) < 20:
        return None

    return desc


def main() -> None:
    """Fetch descriptions for all problems missing them."""
    argparser = argparse.ArgumentParser(description="Fetch LC descriptions from leetcode.ca")
    argparser.add_argument("--limit", type=int, default=0, help="Max problems to fetch (0=all)")
    argparser.add_argument("--dry-run", action="store_true", help="Print what would be fetched without writing DB")
    argparser.add_argument("--start-from", type=int, default=0, help="Start from this leetcode_id")
    argparser.add_argument("--delay", type=float, default=1.5, help="Seconds between requests (default: 1.5)")
    args = argparser.parse_args()

    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()

    # Get all problems needing descriptions, within leetcode.ca range
    cursor.execute(
        """SELECT id, leetcode_id, title FROM problems
           WHERE leetcode_id IS NOT NULL
             AND leetcode_id <= ?
             AND (description IS NULL OR length(description) <= 50)
             AND leetcode_id >= ?
           ORDER BY leetcode_id""",
        (MAX_LC_ID, args.start_from),
    )
    problems = cursor.fetchall()

    total = len(problems)
    if args.limit > 0:
        problems = problems[: args.limit]

    print(f"[INFO] {total} problems need descriptions (leetcode_id <= {MAX_LC_ID})")
    print(f"[INFO] Will fetch {len(problems)} problems" + (" (DRY RUN)" if args.dry_run else ""))

    fetched = 0
    failed = 0
    skipped_404 = 0

    for i, (prob_id, lc_id, title) in enumerate(problems):
        if args.dry_run:
            print(f"  Would fetch: LC {lc_id} - {title}")
            continue

        try:
            desc = fetch_description(lc_id)
        except Exception as e:
            print(f"  [FAIL] LC {lc_id} ({title}): {e}")
            failed += 1
            time.sleep(args.delay)
            continue

        if desc is None:
            skipped_404 += 1
            if (i + 1) % 50 == 0:
                print(f"  [PROGRESS] {i + 1}/{len(problems)} processed, {fetched} fetched, {skipped_404} 404s, {failed} errors")
        else:
            cursor.execute(
                "UPDATE problems SET description = ?, description_source = ? WHERE id = ?",
                (desc, "leetcode.ca", prob_id),
            )
            conn.commit()
            fetched += 1

        if (i + 1) % 50 == 0:
            print(f"  [PROGRESS] {i + 1}/{len(problems)} processed, {fetched} fetched, {skipped_404} 404s, {failed} errors")

        time.sleep(args.delay)

    if not args.dry_run:
        conn.commit()

    conn.close()

    print(f"\n[DONE] Fetched: {fetched}, 404/empty: {skipped_404}, Errors: {failed}")
    print(f"  Total processed: {fetched + skipped_404 + failed}/{len(problems)}")


if __name__ == "__main__":
    main()
