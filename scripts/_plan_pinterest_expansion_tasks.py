"""Batch-add Pinterest prep expansion tasks (2025-11 cutoff dump)."""
import json
import subprocess
import sys

TASKS = [
    # --- New LC problems: add + write Chinese notes ---
    {
        "cmd": "add",
        "title": "[Pinterest/LC] Add + notes: LC 84 Largest Rectangle in Histogram",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "New Pinterest problem (2025-11 cutoff). Add to problems DB with Pinterest tag; "
            "fetch description; write Chinese notes: monotonic-stack O(n) canonical + "
            "divide-and-conquer O(n log n) + related LC 85/42/11 + pattern recognition."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/LC] Add + notes: LC 392 Is Subsequence",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "New Pinterest problem. Two-pointer O(n+m). Follow-up: many queries -> "
            "precompute indexed char positions, binary search each query. Chinese notes. "
            "Cross-link LC 1055 (greedy subsequence family)."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/LC] Add + notes: LC 3229 Min Operations to Make Array Equal to Target",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "New Pinterest problem. Diff-scan greedy (same family as LC 1526). "
            "Chinese notes covering increment/decrement region handling + sign-change counting. "
            "Cross-link LC 1526."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/LC] Add + notes: LC 1526 Min Increments on Subarrays",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "New Pinterest problem. Diff-array + greedy sign-change pattern. "
            "Chinese notes explaining why counting positive deltas is optimal. Cross-link LC 3229."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/LC] Add + notes: LC 1564 Put Boxes Into Warehouse I",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "New Pinterest problem. Greedy: warehouse prefix-min + sort boxes desc. "
            "Chinese notes highlighting the prefix-min insight."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/LC] Add + notes: LC 1580 Put Boxes Into Warehouse II",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "New Pinterest problem (harder variant of 1564, enter from both ends). "
            "Chinese notes: two-pointer shortest-interior-height preprocessing. Contrast with 1564."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/LC] Investigate + notes: 寻找餐馆区间",
        "priority": "P2",
        "complexity": "S",
        "description": (
            "Pinterest dump 2025-11 mentions this with no LC number. Research to identify "
            "the actual LC mapping (candidates: LC 1779 / 2563 / 1094 / 1851). "
            "If LC match found, add/update. If custom, create non-LC entry."
        ),
    },
    # --- Custom Pinterest coding problems ---
    {
        "cmd": "add",
        "title": "[Pinterest/custom] Escape Room game-state (Game(rooms, people))",
        "priority": "P0",
        "complexity": "M",
        "description": (
            "Pinterest coding 2025-11. Design data structure: proceedToNextRoom(pid), "
            "getTop(K), getPeople(roomId). Requirements: O(1) move, O(1) room query, "
            "O(N+K) getTop with positional ranking + tiebreak by entry-order within same room. "
            "Canonical: doubly-linked list per room + global position map. "
            "Write Python impl + Chinese notes as non-LC entry. "
            "Source: the two problem statements in 2025-11 dump."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/custom] Lighthouse 2D matrix light propagation",
        "priority": "P1",
        "complexity": "M",
        "description": (
            "Pinterest coding 2025-11. 2D matrix simulation of light propagation. "
            "Resolve exact variant from dump (light rays + mirrors? coverage? cycle?). "
            "Research variants; write solution + Chinese notes as non-LC entry."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/custom] Prefix-match first-word-index",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "Pinterest coding 2025-11: given ['a','apple','appz','b'] and prefix ['ap'], "
            "return index of first word containing prefix. Trie with earliest-word-index at "
            "each node (or sort+binary-search). Python + Chinese notes."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/custom] Grant Access permission propagation",
        "priority": "P1",
        "complexity": "M",
        "description": (
            "Pinterest coding 2025-11. Problem linked at hack2hire.com (URL in dump). "
            "Research and document: likely DAG/graph permission propagation. "
            "Solution + Chinese notes as non-LC entry. Link in Pinterest index doc."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/custom] Pin Connectivity",
        "priority": "P1",
        "complexity": "M",
        "description": (
            "Pinterest coding 2025-11. Graph connectivity problem on pin/board/user graph. "
            "Research variant, write canonical (Union-Find or BFS/DFS) + Chinese notes. "
            "Non-LC entry."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/custom] round() from scratch (string input)",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "Pinterest coding 2025-11. Implement round() given string s without using float(). "
            "Edge cases: float overflow, '-.2', '2.' (trailing dot). "
            "Parse digits+dot+sign manually; half-up rounding. Chinese notes with state machine."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/custom] Round string s by precision p",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "Pinterest coding 2025-11 follow-up. Round s by precision p. "
            "Examples: s='12567',p='100'->'12600'; s='1234.678',p='0.1'->'1234.7'. "
            "Parse both, determine decimal places from p, round accordingly. Chinese notes."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/custom] LC 332 loop follow-up addendum",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "Pinterest coding 2025-11 follow-up to LC 332: what if tickets form a cycle? "
            "Explain Hierholzer already handles Eulerian circuits naturally (returns to JFK). "
            "If question is detecting infeasible itinerary, discuss Eulerian existence conditions. "
            "Append as addendum to existing LC 332 notes (don't create new problem entry)."
        ),
    },
    # --- System Design deep-dives ---
    {
        "cmd": "add",
        "title": "[Pinterest/SD] ML SD: Design Pins Search Engine",
        "priority": "P0",
        "complexity": "L",
        "description": (
            "Pinterest SD (most frequently asked 2025-11). End-to-end: "
            "(1) candidate generation (two-tower embedding, ANN/HNSW, multi-source text/image/history), "
            "(2) ranking (pairwise vs pointwise, feature eng: text/image/graph/user-context, "
            "loss functions, offline metrics NDCG/MAP/AUC), "
            "(3) online metrics (CTR, repin-rate, session engagement), "
            "(4) infra (Faiss/ScaNN, feature stores, training pipeline), "
            "(5) cold-start + freshness. "
            "Chinese markdown docs/company/pinterest/system_design_pins_search.md."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/SD] ML SD: Notification Recommendation",
        "priority": "P0",
        "complexity": "L",
        "description": (
            "Pinterest SD 2025-11. "
            "(1) notification triggering (when to notify), "
            "(2) content candidate generation, (3) ranking, "
            "(4) delivery constraints (frequency cap, quiet hours, channel push/email/in-app), "
            "(5) offline metrics (open-rate AUC, long-term retention), "
            "(6) engagement-vs-annoyance tradeoffs. "
            "Chinese markdown docs/company/pinterest/system_design_notification_reco.md."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/SD] ML SD: Pin Ranking Recommendation",
        "priority": "P0",
        "complexity": "L",
        "description": (
            "Pinterest SD 2025-11. Pin ranking for home/topic feed. "
            "(1) two-stage retrieval+rerank, (2) features (pin/user/context/graph), "
            "(3) model family (MMOE/wide-and-deep/transformer), "
            "(4) multi-objective (engagement+diversity+long-term), "
            "(5) serving constraints, (6) metric ladder. "
            "Chinese markdown docs/company/pinterest/system_design_pin_ranking.md."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/SD] SD: Ad CTR prediction",
        "priority": "P1",
        "complexity": "L",
        "description": (
            "Pinterest SD 2025-11. "
            "(1) data pipeline (impressions/clicks with attribution), "
            "(2) feature engineering (user/ad/context crosses), "
            "(3) model (DeepFM/wide-and-deep/AutoInt), "
            "(4) calibration (Platt/isotonic), "
            "(5) serving (model server, feature store, latency budget), "
            "(6) online metrics (NE, LogLoss, calibration error). "
            "Chinese markdown docs/company/pinterest/system_design_ad_ctr.md."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/SD] SD: User & Item Embeddings",
        "priority": "P1",
        "complexity": "L",
        "description": (
            "Pinterest SD 2025-11. "
            "(1) objective (self-supervised contrastive / supervised from engagement), "
            "(2) encoder (towers, user sequence, graph-based GraphSAGE/PinSage), "
            "(3) training pipeline (streaming vs batch), "
            "(4) serving (ANN index, freshness, dimension), "
            "(5) downstream uses (candidate gen, ranking features, similar-pins). "
            "Chinese markdown docs/company/pinterest/system_design_embeddings.md."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/SD] SD: Catalog bulk update (500M records, S3+async)",
        "priority": "P0",
        "complexity": "L",
        "description": (
            "Pinterest SD 2025-11. Update internal downstream systems from large catalog (~500M). "
            "(1) ingestion (bulk via S3 consume; single sync/quick-async), "
            "(2) partitioning (range, hash, consistent-hash), "
            "(3) retry for failed partitions (at-least-once + idempotency, DLQ, checkpoint), "
            "(4) fan-out (Kafka, backpressure, flow control), "
            "(5) monitoring (lag, error-rate, RPO/RTO), "
            "(6) tradeoffs: sync-vs-async, exactly-once-vs-at-least-once. "
            "Chinese markdown docs/company/pinterest/system_design_catalog_bulk_update.md."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/SD] ML SD: Personalized Chat Bot Recommending Pins",
        "priority": "P1",
        "complexity": "L",
        "description": (
            "Pinterest SD 2025-11. "
            "(1) conversation understanding (LLM multi-turn state), "
            "(2) intent classification (ask-pins vs chit-chat), "
            "(3) retrieval-augmented pin recommendation, "
            "(4) grounding (pins match intent), "
            "(5) safety/moderation, "
            "(6) evaluation (relevance + conversation quality). "
            "Chinese markdown docs/company/pinterest/system_design_chatbot_pins.md."
        ),
    },
    # --- BQ + Integration ---
    {
        "cmd": "add",
        "title": "[Pinterest/BQ] Map Pinterest BQ questions to existing stories",
        "priority": "P1",
        "complexity": "S",
        "description": (
            "Pinterest BQ (2025-11): (1) project led end-to-end, (2) where requirement came from, "
            "(3) stepping ahead when not responsible, (4) negative feedback received, "
            "(5) working with someone missing deadlines. "
            "Create docs/company/pinterest/bq_question_map.md mapping each Q to 2-3 best-fit EX-XX "
            "stories with 1-sentence angle each. Reference post-rework stories. Chinese."
        ),
    },
    {
        "cmd": "add",
        "title": "[Pinterest/integration] Enrich Pinterest index doc with new sections",
        "priority": "P2",
        "complexity": "M",
        "description": (
            "Final integration after all new LC/custom/SD content lands. "
            "Refresh company_documents id=47 to include: "
            "(1) new LC section (84, 392, 3229, 1526, 1564, 1580, 餐馆区间), "
            "(2) Custom Coding section (Escape Room, Lighthouse, Prefix-match, Grant Access, "
            "Pin Connectivity, round(), Round-by-p, LC332 loop) with lc:// drawer links where applicable, "
            "(3) System Design section with links to docs/company/pinterest/system_design_*.md files, "
            "(4) BQ Question Map link, "
            "(5) cross-links LC problems <-> relevant SD modules (e.g. LC 1244 <-> Leaderboard SD family). "
            "Depends on all previous Pinterest expansion tasks being complete."
        ),
    },
]


def main() -> None:
    cmd = ["python", ".claude/hooks/task_db.py", "batch", "--commands", json.dumps(TASKS)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        sys.exit(1)
    print(result.stdout)


if __name__ == "__main__":
    main()
