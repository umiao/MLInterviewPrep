"""Fetch descriptions for Pinterest LC problems missing from leetcode.ca.

Uses leetcode.ca for IDs <= 1857 and leetcode.com GraphQL for newer IDs.
Targets: LC 1110, 1723, 2402 (task T-P1-374).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from fetch_lc_descriptions import DescriptionExtractor, fetch_description  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"

TARGETS: list[tuple[int, str]] = [
    (1110, "delete-nodes-and-return-forest"),
    (1723, "find-minimum-time-to-finish-all-jobs"),
    (2402, "meeting-rooms-iii"),
]


def fetch_via_graphql(slug: str) -> str | None:
    """Fetch problem content HTML from leetcode.com GraphQL."""
    payload = json.dumps(
        {
            "query": "query q($titleSlug:String!){question(titleSlug:$titleSlug){content}}",
            "variables": {"titleSlug": slug},
        }
    ).encode("utf-8")
    req = Request(
        "https://leetcode.com/graphql/",
        data=payload,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
        },
    )
    with urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = (data.get("data") or {}).get("question", {}).get("content")
    if not content:
        return None
    wrapped = f'<div class="markdown-body">{content}</div>'
    parser = DescriptionExtractor()
    parser.feed(wrapped)
    text = parser.get_description()
    return text if text and len(text) >= 50 else None


def main() -> None:
    """Fetch and store missing descriptions."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    for lc_id, slug in TARGETS:
        desc: str | None
        source: str
        if lc_id <= 1857:
            desc = fetch_description(lc_id)
            source = "leetcode.ca"
            if not desc:
                desc = fetch_via_graphql(slug)
                source = "leetcode.com"
        else:
            desc = fetch_via_graphql(slug)
            source = "leetcode.com"

        if not desc:
            print(f"[FAIL] LC {lc_id}: no description found")
            continue
        cur.execute(
            "UPDATE problems SET description = ?, description_source = ? WHERE leetcode_id = ?",
            (desc, source, lc_id),
        )
        print(f"[OK]   LC {lc_id} ({source}): {len(desc)} chars")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
