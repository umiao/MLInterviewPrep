"""Backfill LeetCode problem descriptions for problems.description NULL/empty.

Primary source: LeetCode GraphQL public endpoint (covers all non-premium problems
at any leetcode_id). Fallback: leetcode.ca for problems whose GraphQL call fails
(older locked premium problems sometimes expose content only on leetcode.ca).

Usage:
    python scripts/backfill_lc_descriptions.py [--limit N] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
GRAPHQL_URL = "https://leetcode.com/graphql/"
LEETCODE_CA_SITEMAP = "https://leetcode.ca/sitemap.xml"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
QUERY = "query q($s: String!){question(titleSlug: $s){content}}"
_CA_URL_CACHE: dict[int, str] = {}


class HTMLToText(HTMLParser):
    """Flatten LeetCode problem HTML to plain-text description."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "br":
            self._parts.append("\n")
        elif tag in ("p", "div", "pre"):
            self._parts.append("\n\n")
        elif tag == "li":
            self._parts.append("\n- ")
        elif tag in ("ul", "ol"):
            self._parts.append("\n")
        elif tag == "code":
            self._parts.append("`")
        elif tag == "sup":
            self._parts.append("^")
        elif tag == "sub":
            self._parts.append("_")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag == "code":
            self._parts.append("`")
        elif tag in ("p", "pre"):
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self._parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._skip_depth:
            return
        entities = {"lt": "<", "gt": ">", "amp": "&", "quot": '"', "apos": "'", "nbsp": " "}
        self._parts.append(entities.get(name, f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self._skip_depth:
            return
        try:
            ch = chr(int(name[1:], 16)) if name.startswith("x") else chr(int(name))
            self._parts.append(ch)
        except (ValueError, OverflowError):
            self._parts.append(f"&#{name};")

    def get_text(self) -> str:
        """Return cleaned plain text."""
        text = "".join(self._parts)
        lines = [ln.strip() for ln in text.split("\n")]
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html_to_text(html: str) -> str:
    """Convert HTML fragment to plain text."""
    parser = HTMLToText()
    parser.feed(html)
    return parser.get_text()


def slug_from_url(url: str | None) -> str | None:
    """Extract titleSlug from leetcode.com URL."""
    if not url:
        return None
    m = re.search(r"leetcode\.com/problems/([a-z0-9\-]+)", url)
    return m.group(1) if m else None


def fetch_graphql(slug: str) -> str | None:
    """Fetch HTML content from LeetCode GraphQL. Returns None on failure/empty."""
    payload = json.dumps({"query": QUERY, "variables": {"s": slug}}).encode("utf-8")
    req = Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Referer": f"https://leetcode.com/problems/{slug}/",
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            j = json.loads(resp.read())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None
    q = (j.get("data") or {}).get("question")
    if not q:
        return None
    content = q.get("content")
    if not content:
        return None
    text = html_to_text(content)
    return text if len(text) >= 40 else None


def _load_ca_sitemap() -> dict[int, str]:
    """Parse leetcode.ca sitemap into {leetcode_id: url}. One-time per process."""
    if _CA_URL_CACHE:
        return _CA_URL_CACHE
    req = Request(LEETCODE_CA_SITEMAP, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=30) as resp:
            xml = resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError):
        return _CA_URL_CACHE
    for m in re.finditer(
        r"https://leetcode\.ca/\d{4}-\d{2}-\d{2}-(\d+)-[^/<]+/", xml
    ):
        lc_id = int(m.group(1))
        _CA_URL_CACHE.setdefault(lc_id, m.group(0))
    return _CA_URL_CACHE


def fetch_leetcode_ca(leetcode_id: int) -> str | None:
    """Fallback fetch via leetcode.ca (mirror for premium/locked problems)."""
    ca_map = _load_ca_sitemap()
    url = ca_map.get(leetcode_id)
    if not url:
        return None
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError):
        return None
    m = re.search(
        r"(?:Description|Problem)[^<]{0,20}</h[1-3]>(.*?)<h[1-3]",
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return None
    text = html_to_text(m.group(1))
    return text if len(text) >= 40 else None


def main() -> None:
    """Run the backfill across all LC problems missing descriptions."""
    ap = argparse.ArgumentParser(description="Backfill LC descriptions via GraphQL + leetcode.ca")
    ap.add_argument("--limit", type=int, default=0, help="Max rows to process (0=all)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    args = ap.parse_args()

    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()
    cur.execute(
        """SELECT id, leetcode_id, title, url FROM problems
           WHERE leetcode_id IS NOT NULL
             AND (description IS NULL OR description = '')
           ORDER BY leetcode_id"""
    )
    rows = cur.fetchall()
    total = len(rows)
    if args.limit > 0:
        rows = rows[: args.limit]

    print(f"[INFO] {total} LC problems need descriptions; processing {len(rows)}")

    fetched = failed = skipped = 0
    for i, (pid, lc_id, title, url) in enumerate(rows):
        slug = slug_from_url(url)
        desc: str | None = None
        source = ""
        if slug:
            desc = fetch_graphql(slug)
            if desc:
                source = "leetcode.com"
        if desc is None:
            desc = fetch_leetcode_ca(lc_id)
            if desc:
                source = "leetcode.ca"

        if desc is None:
            skipped += 1
            print(f"  [MISS] LC {lc_id} {title!r} (slug={slug})")
        else:
            if args.dry_run:
                print(f"  [DRY] LC {lc_id} {title!r} len={len(desc)} src={source}")
            else:
                cur.execute(
                    "UPDATE problems SET description = ?, description_source = ? WHERE id = ?",
                    (desc, source, pid),
                )
                conn.commit()
            fetched += 1

        if (i + 1) % 25 == 0:
            print(f"  [PROGRESS] {i + 1}/{len(rows)} fetched={fetched} miss={skipped} err={failed}")

        time.sleep(args.delay)

    conn.close()
    print(f"\n[DONE] fetched={fetched} miss={skipped} err={failed} total={len(rows)}")


if __name__ == "__main__":
    main()
