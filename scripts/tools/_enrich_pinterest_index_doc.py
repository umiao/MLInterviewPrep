# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Enrich Pinterest LC index doc (company_documents id=47) with new sections.

Adds: (1) New LC section (84, 392, 3229, 1526, 1564, 1580, 1851),
(2) Custom Coding section with titles, (3) System Design section linking
to docs/company/pinterest/system_design_*.md, (4) BQ Question Map link,
(5) cross-links LC <-> SD.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime

DB = "data/mle_prep.db"
DOC_ID = 47

APPENDIX = """

---

## Pinterest Expansion (2025-11 Dump) -- New LC Set

Additional LC problems surfaced from the Pinterest 2025-11 Discord dump.
These are *not* part of the original 14-problem must-do list but appeared in
recent onsite reports; each is tagged `Pinterest` in the problems DB.

| # | LC | Title | Difficulty | Pattern | Notes |
|---|-----|-------|-----------|---------|-------|
| 1 | 84   | [Largest Rectangle in Histogram](lc://84)    | Hard   | Monotonic stack            | Foundation for skyline/histogram-style problems |
| 2 | 392  | [Is Subsequence](lc://392)                   | Easy   | Two-pointer                | Warmup; often asked as lead-in before LC 1055 |
| 3 | 1526 | [Minimum Number of Increments on Subarrays](lc://1526) | Hard   | Greedy on diffs            | One-pass: sum of positive first-diffs |
| 4 | 1564 | [Put Boxes Into Warehouse I](lc://1564)      | Medium | Greedy + prefix-min        | Sort boxes desc; scan warehouse |
| 5 | 1580 | [Put Boxes Into Warehouse II](lc://1580)     | Hard   | Two-pointer from both ends | Generalizes 1564 (warehouse has no height monotonicity) |
| 6 | 3229 | [Min Operations to Make Array Equal to Target](lc://3229) | Hard   | Greedy on diffs (signed)   | Variant of 1526; handles sign changes |
| 7 | 1851 | [Minimum Interval to Include Each Query](lc://1851) | Hard   | Offline sort + min-heap    | Best match for reported 「寻找餐馆区间」; see [investigation note](./pinterest/lc_investigation_restaurant_intervals.md) |

**Cluster F: Monotonic Stack / Histogram** -- LC 84

**Cluster G: Greedy on Differences** -- LC 1526, LC 3229

**Cluster H: Warehouse / Box Packing (Greedy)** -- LC 1564, LC 1580

**Cluster I: Interval Queries (Offline Sort + Heap)** -- LC 1851

---

## Custom Coding Problems (Pinterest-Specific)

Problems reported onsite without a direct LeetCode equivalent. Full write-ups
live under `problems.notes` in the problems DB; search by title.

| # | Title | Core Pattern | Notes |
|---|-------|--------------|-------|
| 1 | Escape Room Game State (rooms + people) | BFS / state machine | Multi-actor graph traversal |
| 2 | Lighthouse 2D Light Propagation (beam + mirrors + splitters) | Grid simulation + recursion | Branching on splitters; cycle detection |
| 3 | Prefix-Match First-Word-Index (sorted dictionary) | Binary search / Trie | `bisect_left` on sorted dict is the clean O(log n) |
| 4 | Grant Access / Permission Propagation on a DAG | BFS/DFS on DAG | Topological traversal; avoid re-visit |
| 5 | Pin Connectivity on a Pinterest Relationship Graph | Union-Find | Component queries over streaming edges |
| 6 | round() from scratch (string input, no float) | String/digit arithmetic | No `float()`; handle banker's vs half-up explicitly |
| 7 | round by precision p (string s, precision p) | String/digit arithmetic | Generalizes #6; align to p-th digit before rounding |
| 8 | [LC 332 -- Loop follow-up](lc://332) addendum | Graph + loop detection | Variant: detect if itinerary must revisit a ticket |

---

## System Design (SD) Modules

Each Pinterest-flavored SD write-up lives in `docs/company/pinterest/`. These are
multi-section documents with: problem framing, metrics, data/feature, model
architecture, training, serving, online eval, failure modes.

| # | Topic | File | Linked LC / Custom |
|---|-------|------|--------------------|
| 1 | Ad CTR Prediction                        | [system_design_ad_ctr.md](./pinterest/system_design_ad_ctr.md)                   | -- |
| 2 | User & Item Embeddings                    | [system_design_embeddings.md](./pinterest/system_design_embeddings.md)           | -- |
| 3 | Personalized Chat Bot Recommending Pins   | [system_design_chatbot_pins.md](./pinterest/system_design_chatbot_pins.md)       | -- |
| 4 | Pin Ranking                               | [system_design_pin_ranking.md](./pinterest/system_design_pin_ranking.md)         | [LC 1244 Leaderboard](lc://1244) (score-store analog) |
| 5 | Pins Search                               | [system_design_pins_search.md](./pinterest/system_design_pins_search.md)         | [LC 642 Autocomplete](lc://642), [LC 392 Is Subsequence](lc://392) |
| 6 | Notification Recommendation               | [system_design_notification_reco.md](./pinterest/system_design_notification_reco.md) | -- |
| 7 | Catalog Bulk Update                       | [system_design_catalog_bulk_update.md](./pinterest/system_design_catalog_bulk_update.md) | [LC 1526/3229 (batch-diff updates)](lc://1526) |

---

## BQ (Behavioral)

- **Pinterest BQ Question Map (2025-11)**: [bq_question_map.md](./pinterest/bq_question_map.md) -- maps the 5 reported BQ prompts to 2-3 best-fit EX-XX stories each with 1-sentence angles.

---

## LC <-> SD Cross-Links

Quick lookup: when a SD interview trends toward algorithm-style sub-questions,
these LC problems are the closest patterns.

| SD Module | Most Relevant LC / Pattern |
|-----------|----------------------------|
| Pin Ranking / Leaderboard      | [LC 1244 Design A Leaderboard](lc://1244), [LC 2402 Meeting Rooms III](lc://2402) (heap tiebreak) |
| Pins Search / Autocomplete     | [LC 642 Autocomplete](lc://642), [LC 1055 Shortest Way to Form String](lc://1055), [LC 392 Is Subsequence](lc://392) |
| Embeddings / Retrieval         | [LC 311 Sparse Matrix Multiplication](lc://311) (approx kNN warmup) |
| Catalog Bulk Update            | [LC 1526](lc://1526), [LC 3229](lc://3229) (diff-based minimum ops) |
| Ad CTR                         | [LC 322 Coin Change](lc://322) (budget DP analog for pacing) |
| Chat Bot Pins Reco             | [LC 282 Expression Add Operators](lc://282) (prompt-parse style backtrack) |
| Warehouse / Inventory Layout   | [LC 1564](lc://1564), [LC 1580](lc://1580) |

---

*Last enriched: {today} (T-P2-413).*
""".strip("\n")


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB)
    try:
        row = conn.execute(
            "SELECT content FROM company_documents WHERE id=?", (DOC_ID,)
        ).fetchone()
        if row is None:
            raise SystemExit(f"doc id={DOC_ID} not found")
        content = row[0]
        marker = "## Pinterest Expansion (2025-11 Dump) -- New LC Set"
        if marker in content:
            head = content.split(marker, 1)[0].rstrip() + "\n"
            new_content = head + "\n" + APPENDIX.format(today=today) + "\n"
        else:
            new_content = content.rstrip() + "\n\n" + APPENDIX.format(today=today) + "\n"
        conn.execute(
            "UPDATE company_documents SET content=?, updated_at=? WHERE id=?",
            (new_content, datetime.now().isoformat(timespec="seconds"), DOC_ID),
        )
        conn.commit()
        new_len = len(new_content)
        print(f"[DONE] doc id={DOC_ID} updated. new length={new_len} chars")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
