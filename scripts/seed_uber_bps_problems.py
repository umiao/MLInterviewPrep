"""Seed Uber BPS interview problems into mle_prep.db.

Step 1: Ensure LC problems have Uber tag + 1p3a source badge + interview notes.
Step 2: Create custom non-LC problem entries.
Step 3: Create/update interview event for Uber BPS.

Task: T-P0-241
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_connection() -> sqlite3.Connection:
    """Get a connection to the database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def merge_company_tags(existing_json: str | None, new_tag: str) -> str:
    """Add a company tag to the existing JSON array if not present."""
    tags = json.loads(existing_json) if existing_json else []
    if new_tag not in tags:
        tags.append(new_tag)
    return json.dumps(tags, ensure_ascii=False)


def merge_source(existing_source: str | None, new_source: str) -> str:
    """Add a source to the existing comma-separated source string."""
    if not existing_source:
        return new_source
    sources = [s.strip() for s in existing_source.split(",")]
    if new_source not in sources:
        sources.append(new_source)
    return ", ".join(sources)


def append_notes(existing_notes: str | None, new_notes: str) -> str:
    """Append new notes to existing notes if not already present."""
    if not existing_notes:
        return new_notes
    if new_notes in existing_notes:
        return existing_notes
    return existing_notes + "\n\n---\n\n" + new_notes


# ── Step 1: LC problems with Uber tag, 1p3a badge, interview notes ──

LC_PROBLEMS = [
    {
        "leetcode_id": 230,
        "notes": (
            "[1p3a Uber BPS] Kth Smallest Element in BST.\n"
            "Variant: kth LARGEST instead of smallest.\n"
            "Follow-ups:\n"
            "- O(0) space solution: Morris Traversal\n"
            "- Adding left_count/right_count to nodes\n"
            "- Flatten the tree approach\n"
            "Interviewer provided iterative first, then recursive. "
            "Needed time/space complexity analysis for each.\n"
            "Done on HackerRank, must run code."
        ),
        "pattern": "tree",
    },
    {
        "leetcode_id": 547,
        "notes": (
            "[1p3a Uber BPS] Number of Provinces.\n"
            "Standard Union Find + DFS approaches.\n"
            "Also appeared as ball attraction variant: given 2D ball coordinates (x,y), "
            "balls within distance d attract each other (chain reaction). "
            "Find minimum time to attract all balls. UF: count roots."
        ),
        "pattern": "union-find",
    },
    {
        "leetcode_id": 337,
        "notes": (
            "[1p3a Uber BPS] House Robber III.\n"
            "Tree DP with rob/not-rob states per node."
        ),
        "pattern": "tree",
    },
    {
        "leetcode_id": 1020,
        "notes": (
            "[1p3a Uber BPS] Number of Enclaves.\n"
            "BFS/DFS from border cells to mark reachable land."
        ),
        "pattern": "graph",
    },
    {
        "leetcode_id": 977,
        "notes": (
            "[1p3a Uber BPS] Squares of a Sorted Array.\n"
            "Two-pointer approach comparing absolute values from both ends.\n"
            "Appeared in phone screen with ML knowledge questions."
        ),
        "pattern": "two-pointers",
    },
    {
        "leetcode_id": 815,
        "notes": (
            "[1p3a Uber BPS] Bus Routes.\n"
            "BFS on route graph (not stop graph). Build route adjacency, "
            "BFS from source routes to target routes."
        ),
        "pattern": "graph",
    },
    {
        "leetcode_id": 981,
        "notes": (
            "[1p3a Uber BPS] Time Based Key-Value Store.\n"
            "Binary search on timestamps.\n"
            "Follow-ups:\n"
            "- How to handle 1M+ requests per second\n"
            "- How to guarantee thread safety\n"
            "- Amortized time complexity analysis"
        ),
        "pattern": "binary-search",
    },
    {
        "leetcode_id": 17,
        "notes": (
            "[1p3a Uber BPS] Letter Combinations of a Phone Number.\n"
            "Backtracking approach.\n"
            "Variant: output all letter combos for a 10-digit phone number "
            "(same idea, larger scale). Like LC 17 but with digits 2-9 mapping."
        ),
        "pattern": "backtracking",
    },
    {
        "leetcode_id": 23,
        "notes": (
            "[1p3a Uber BPS] Merge K Sorted Lists.\n"
            "Heap approach + divide-and-conquer alternative.\n"
            "Appeared in BPS 2 alongside UberEats Recommendation Ranking case study."
        ),
        "pattern": "heap",
    },
    {
        "leetcode_id": 1197,
        "notes": (
            "[1p3a Uber BPS] Minimum Knight Moves.\n"
            "BFS on infinite grid.\n"
            "Variant: board size is n (finite board, not infinite)."
        ),
        "pattern": "graph",
    },
    {
        "leetcode_id": 1697,
        "notes": (
            "[1p3a Uber BPS] Checking Existence of Edge Length Limited Paths.\n"
            "Offline queries + Union Find: sort queries and edges together.\n"
            "Variant: edge weight >= k (reversed condition from original)."
        ),
        "pattern": "union-find",
    },
    {
        "leetcode_id": 549,
        "notes": (
            "[1p3a Uber BPS] Binary Tree Longest Consecutive Sequence II.\n"
            "Tree DP tracking increasing/decreasing lengths per node."
        ),
        "pattern": "tree",
    },
    {
        "leetcode_id": 987,
        "notes": (
            "[1p3a Uber BPS] Vertical Order Traversal of a Binary Tree.\n"
            "BFS/DFS with column tracking, sort by column then row then value."
        ),
        "pattern": "tree",
    },
    {
        "leetcode_id": 79,
        "notes": (
            "[1p3a Uber BPS] Word Search.\n"
            "Variant: 8 directions (including diagonals), must go in straight line "
            "(no turning). Simplifies to O(R*C*8*L) enumeration -- no DFS/backtracking needed."
        ),
        "pattern": "backtracking",
    },
    {
        "leetcode_id": 994,
        "notes": (
            "[1p3a Uber BPS] Rotting Oranges.\n"
            "Multi-source BFS: enqueue all rotten cells, BFS layer by layer."
        ),
        "pattern": "graph",
    },
    {
        "leetcode_id": 2503,
        "notes": (
            "[1p3a Uber BPS] Maximum Number of Points From Grid Queries.\n"
            "Variant: terrain grid with limits array, start at (0,0), "
            "traverse cells where value < current limit. BFS + sort queries approach."
        ),
        "pattern": "graph",
    },
    {
        "leetcode_id": 2858,
        "notes": (
            "[1p3a Uber BPS] Minimum Edge Reversals So Every Node Is Reachable.\n"
            "Re-rooting DP: DFS from node 0, then re-root formula.\n"
            "Note from 1p3a: must self-construct edges, watch for 1-indexed."
        ),
        "pattern": "tree",
    },
    {
        "leetcode_id": 2791,
        "notes": (
            "[1p3a Uber BPS] Count Paths That Can Form a Palindrome in a Tree.\n"
            "Bitmask XOR + DFS prefix counting.\n"
            "Key insight: palindrome-formable = at most 1 char with odd count = "
            "XOR of path has at most 1 bit set."
        ),
        "pattern": "tree",
    },
]

# LC 1696 needs to be created
LC_1696_NEW = {
    "leetcode_id": 1696,
    "title": "Jump Game VI",
    "url": "https://leetcode.com/problems/jump-game-vi/",
    "difficulty": "medium",
    "tags": json.dumps(["dynamic-programming", "sliding-window", "heap"]),
    "pattern": "dynamic-programming",
    "category": "algorithm",
    "source": "1point3acres",
    "company_tags": json.dumps(["Uber"]),
    "priority": 1,
    "notes": (
        "[1p3a Uber BPS] Jump Game VI.\n"
        "Variant: can jump +1 or +prime ending in 3 (3, 13, 23, ...), "
        "maximize score. DP solution.\n"
        "Need to precompute primes ending in 3."
    ),
}


# ── Step 2: Custom non-LC problems ──

CUSTOM_PROBLEMS = [
    {
        "title": "Purchase Optimization",
        "difficulty": "medium",
        "tags": json.dumps(["binary-search", "prefix-sum"]),
        "pattern": "binary-search",
        "category": "algorithm",
        "description": (
            "Given an array of prices and queries (pos, amount), find the maximum "
            "number of items purchasable starting from position pos with the given amount.\n\n"
            "Approach: prefix sum + binary search. Compute prefix sums of prices, "
            "then for each query binary search for the rightmost position where "
            "prefix[pos:end] <= amount."
        ),
        "notes": (
            "[1p3a Uber BPS] Frequently reported problem.\n"
            "Key: prefix sum array, then binary search for each query.\n"
            "Time: O(n + q*log(n)), Space: O(n)"
        ),
    },
    {
        "title": "Customer Revenue & Referral Tracking",
        "difficulty": "medium",
        "tags": json.dumps(["ood", "tree", "design"]),
        "pattern": "design",
        "category": "algorithm",
        "description": (
            "Design a system with:\n"
            "- insertNewCustomer(revenue) -> returns customer ID\n"
            "- insertNewCustomer(revenue, referrerID) -> returns customer ID\n"
            "- getLowestK(k, minTotalRevenue) -> returns k customer IDs with least "
            "revenue >= minTotalRevenue\n\n"
            "Revenue propagates up the referral tree. Must handle tree aggregation efficiently.\n\n"
            "Example:\n"
            "insertNewCustomer(10) -> 0\n"
            "insertNewCustomer(30, 0) -> 1\n"
            "insertNewCustomer(50, 1) -> 2\n"
            "getLowestK(1, 45) -> {2}\n"
            "getLowestK(2, 45) -> {1, 2}"
        ),
        "notes": (
            "[1p3a Uber BPS] OOD problem with tree aggregation.\n"
            "Key challenge: revenue propagation up referral chain.\n"
            "Consider using sorted structure for getLowestK queries."
        ),
    },
    {
        "title": "Uber Rider Connection Log",
        "difficulty": "medium",
        "tags": json.dumps(["union-find", "graph", "string-parsing"]),
        "pattern": "union-find",
        "category": "algorithm",
        "description": (
            "Given timestamped logs of riders sharing rides:\n"
            "  t1 Alice shared-ride-with Bob\n"
            "  t2 Charlie shared-ride-with Dan\n"
            "  ...\n"
            "Find the earliest time all riders are connected (transitively).\n\n"
            "Follow-up: handle 'block' events (A blocked B). Union Find cannot handle "
            "deletions, so must use BFS/DFS rebuild approach."
        ),
        "notes": (
            "[1p3a Uber BPS] Union Find with timestamps.\n"
            "Parse logs, union riders, check after each event if all connected.\n"
            "Block follow-up is critical: UF doesn't support deletion.\n"
            "Alternative for blocks: rebuild connectivity graph with BFS/DFS."
        ),
    },
    {
        "title": "Elevator Binary Search (OA)",
        "difficulty": "medium",
        "tags": json.dumps(["binary-search", "array", "simulation"]),
        "pattern": "binary-search",
        "category": "algorithm",
        "description": (
            "Given an array where each element represents the distance you can move "
            "(positive = forward, negative = backward). Find the minimum starting "
            "index from which you will never move out of the left boundary.\n\n"
            "Approach: traverse once, each time you exit the left boundary, update "
            "the answer."
        ),
        "notes": (
            "[1p3a Uber OA] Array-based jump problem.\n"
            "Simple traversal with boundary tracking."
        ),
    },
    {
        "title": "Server Throughput with Heap (OA)",
        "difficulty": "medium",
        "tags": json.dumps(["heap", "greedy"]),
        "pattern": "heap",
        "category": "algorithm",
        "description": (
            "OA problem about server throughput optimization.\n"
            "Compare recursive vs heap solution approaches."
        ),
        "notes": "[1p3a Uber OA] Heap-based throughput optimization.",
    },
    {
        "title": "Cart & Pricing Engine (OOD)",
        "difficulty": "medium",
        "tags": json.dumps(["ood", "design", "strategy-pattern"]),
        "pattern": "design",
        "category": "algorithm",
        "description": (
            "Design the core classes for Uber Eats Cart & Pricing Engine.\n\n"
            "Requirements:\n"
            "- Item Customization: add-ons (Extra Cheese, No Onions), each may add cost\n"
            "- Surge Pricing: multiplier on subtotal (e.g., 1.2x)\n"
            "- Membership Discounts: Uber One subscribers get 0% delivery fee + 5% off\n"
            "- Promo Codes: flat ($5 off) or percentage (10% off)\n"
            "- Receipt Breakdown: Base Price, Add-ons, Fees, Discounts\n\n"
            "Use Strategy pattern for flexible pricing rules."
        ),
        "notes": (
            "[1p3a Uber BPS] OOD problem.\n"
            "Key: Strategy pattern for pricing rules (surge, membership, promo).\n"
            "Must produce receipt breakdown output."
        ),
    },
    {
        "title": "Circular Array Shortest Jump",
        "difficulty": "medium",
        "tags": json.dumps(["bfs", "graph", "array"]),
        "pattern": "graph",
        "category": "algorithm",
        "description": (
            "Given a circular array where arr[i] represents the step distance you can "
            "jump left or right (exact jump), and two indices 'from' and 'to', find "
            "the shortest number of jumps to go from 'from' to 'to'.\n\n"
            "Approach: BFS on the circular array as a graph."
        ),
        "notes": "[1p3a Uber BPS] BFS on circular array.",
    },
    {
        "title": "Robot Distance in Grid",
        "difficulty": "medium",
        "tags": json.dumps(["dynamic-programming", "grid", "precomputation"]),
        "pattern": "dynamic-programming",
        "category": "algorithm",
        "description": (
            "Given a grid with robots (O), empty cells (E), and obstacles (X), and a "
            "distance array [left, top, bottom, right], find the robot matching those "
            "distances to nearest obstacle in each direction.\n\n"
            "Approach: DP to precompute distances from each cell to nearest obstacle "
            "in all 4 directions, then match against query."
        ),
        "notes": "[1p3a Uber BPS] Grid DP with 4-directional distance precomputation.",
    },
    {
        "title": "Min Operations n to 0 (NAF)",
        "difficulty": "medium",
        "tags": json.dumps(["math", "greedy", "bit-manipulation"]),
        "pattern": "math",
        "category": "algorithm",
        "description": (
            "Given positive integer n, one operation: n = n +/- 2^i (i >= 0). "
            "Find minimum operations to reduce n to 0.\n\n"
            "Approach: Binary/NAF (Non-Adjacent Form) analysis.\n"
            "While n != 0:\n"
            "  if n is even: n >>= 1\n"
            "  if n % 4 == 1: n -= 1, ops += 1\n"
            "  if n % 4 == 3: n += 1, ops += 1"
        ),
        "notes": (
            "[1p3a Uber BPS] Greedy with binary analysis.\n"
            "Key insight: n%4==1 -> subtract, n%4==3 -> add (NAF form)."
        ),
    },
    {
        "title": "Shortest Subarray with k Distinct Integers",
        "difficulty": "medium",
        "tags": json.dumps(["sliding-window", "hash-map", "two-pointers"]),
        "pattern": "sliding-window",
        "category": "algorithm",
        "description": (
            "Given array arr and integer k, find the shortest subarray containing "
            "at least k distinct integers. Return -1 if none exists.\n\n"
            "Approach: Sliding window with counter. Expand right to get k distinct, "
            "shrink left to minimize length."
        ),
        "notes": "[1p3a Uber BPS] Standard sliding window minimum.",
    },
    {
        "title": "Price Discount (Monotonic Stack)",
        "difficulty": "medium",
        "tags": json.dumps(["monotonic-stack", "array"]),
        "pattern": "stack",
        "category": "algorithm",
        "description": (
            "For each item i, the discount is the price of the first j > i where "
            "prices[j] <= prices[i]. If discount exists, final = prices[i] - prices[j]. "
            "Otherwise, sold at original price.\n\n"
            "Output: (1) total final price sum, (2) indices sold at original price.\n\n"
            "Approach: Monotonic (decreasing) stack. For each new price, pop all stack "
            "entries where current price <= stack top price."
        ),
        "notes": "[1p3a Uber BPS] Next smaller element pattern.",
    },
    {
        "title": "Balanced Permutation Check",
        "difficulty": "medium",
        "tags": json.dumps(["array", "math", "simulation"]),
        "pattern": "array",
        "category": "algorithm",
        "description": (
            "Given a permutation p of 1..n, for each k (1<=k<=n), check if there "
            "exists a subarray that is a permutation of 1..k. Return binary string.\n\n"
            "Approach: Track min/max positions as k increases. If maxPos - minPos + 1 == k, "
            "then k is balanced."
        ),
        "notes": (
            "[1p3a Uber BPS] Track min/max position as k increases.\n"
            "O(n) solution using position mapping."
        ),
    },
    {
        "title": "Elevator/Stairs Energy Optimization",
        "difficulty": "medium",
        "tags": json.dumps(["binary-search", "math"]),
        "pattern": "binary-search",
        "category": "algorithm",
        "description": (
            "Climb n floors. First mid floors by elevator (gain energy e1, cost time t1 each). "
            "Remaining floors by stairs (consume energy e2, time=ceil(c/energy) per step). "
            "Energy cannot go negative during stairs.\n\n"
            "Minimize the difference between elevator time and stairs time.\n"
            "Approach: Binary search on the split point mid."
        ),
        "notes": "[1p3a Uber BPS] Binary search on split point.",
    },
    {
        "title": "N-ary Tree 3-Part Problem",
        "difficulty": "medium",
        "tags": json.dumps(["tree", "dfs"]),
        "pattern": "tree",
        "category": "algorithm",
        "description": (
            "Given an N-ary tree:\n"
            "(a) Sum all node values\n"
            "(b) Find the maximum path value (root to leaf)\n"
            "(c) Return the nodes on the max-value path\n\n"
            "Must define Node class. DFS for all three parts."
        ),
        "notes": "[1p3a Uber BPS] Multi-part tree problem. Must define Node class.",
    },
    {
        "title": "Max Throughput with Budget",
        "difficulty": "medium",
        "tags": json.dumps(["binary-search", "greedy"]),
        "pattern": "binary-search",
        "category": "algorithm",
        "description": (
            "Multiple services in a pipeline. Each service has current throughput and "
            "scale cost. The i+1th service's input comes from the ith. "
            "Bottleneck = min throughput across all services.\n\n"
            "Given a budget, maximize throughput.\n\n"
            "Approach: Binary search on target throughput. For each guess, compute "
            "total cost to bring all services up to target. Check if <= budget."
        ),
        "notes": (
            "[1p3a Uber BPS] Binary search the answer pattern.\n"
            "Key: bottleneck is min(all throughputs), binary search on target."
        ),
    },
    {
        "title": "Parking Lot OOD",
        "difficulty": "easy",
        "tags": json.dumps(["ood", "design"]),
        "pattern": "design",
        "category": "algorithm",
        "description": (
            "Design a Parking Lot system with:\n"
            "- park(vehicle) -> spot assignment\n"
            "- unpark(vehicle) -> free spot\n"
            "- checkCar(vehicle) -> check if parked\n\n"
            "Motorcycle spots: only motorcycles. Regular spots: both motorcycles and cars.\n"
            "Class hierarchy design."
        ),
        "notes": "[1p3a Uber BPS] Classic OOD problem with vehicle hierarchy.",
    },
    {
        "title": "Task Assignment to 2 People",
        "difficulty": "medium",
        "tags": json.dumps(["greedy", "sorting"]),
        "pattern": "greedy",
        "category": "algorithm",
        "description": (
            "n tasks, each has reward1[i] and reward2[i] for person 1 and person 2. "
            "Person 1 must do exactly k tasks. Maximize total reward.\n\n"
            "Approach: Greedy. Start with all tasks assigned to person 2. "
            "Compute diff = reward1[i] - reward2[i] for each task. "
            "Sort by diff descending, assign top k to person 1."
        ),
        "notes": (
            "[1p3a Uber BPS] Greedy assignment by reward difference.\n"
            "Time: O(n log n), Space: O(n)"
        ),
    },
    {
        "title": "Minesweeper Grid Generator",
        "difficulty": "easy",
        "tags": json.dumps(["random", "grid", "code-quality"]),
        "pattern": "array",
        "category": "algorithm",
        "description": (
            "Place N mines randomly on a 2D grid.\n\n"
            "The coding itself is simple, but the interviewer pushes for iterative "
            "code quality improvements: remove unnecessary set, reduce variables, "
            "simplify logic. Focus is on writing clean, minimal code."
        ),
        "notes": (
            "[1p3a Uber Onsite] Code quality focused problem.\n"
            "Interviewer iteratively pushes for cleaner code.\n"
            "Not about the algorithm -- about coding craftsmanship."
        ),
    },
    {
        "title": "2D Grid Nearest Exit (BFS)",
        "difficulty": "medium",
        "tags": json.dumps(["bfs", "grid"]),
        "pattern": "graph",
        "category": "algorithm",
        "description": (
            "Given a 2D grid with a starting point, find the nearest boundary cell "
            "(exit) using BFS. Standard multi-source BFS.\n\n"
            "Similar to LC 1926 (Nearest Exit from Entrance in Maze)."
        ),
        "notes": "[1p3a Uber Onsite] Standard BFS grid problem.",
    },
    {
        "title": "Lock Combination BFS",
        "difficulty": "medium",
        "tags": json.dumps(["bfs", "state-space"]),
        "pattern": "graph",
        "category": "algorithm",
        "description": (
            "Find the minimum number of steps to unlock a combination lock. "
            "BFS on the state space of possible lock configurations.\n\n"
            "Similar to LC 752 (Open the Lock)."
        ),
        "notes": "[1p3a Uber Tech Screen] BFS on state space.",
    },
    {
        "title": "Non-overlapping Interval Triples",
        "difficulty": "hard",
        "tags": json.dumps(["intervals", "sorting", "combinatorics"]),
        "pattern": "intervals",
        "category": "algorithm",
        "description": (
            "Given a set of intervals, count the number of groups of 3 intervals "
            "that have no pairwise overlap.\n\n"
            "Approach: Sort intervals, then use combinatorial counting."
        ),
        "notes": (
            "[1p3a Uber BPS] Interval counting problem.\n"
            "Time pressure noted: 2 problems in 40 min, most candidates don't finish."
        ),
    },
    {
        "title": "City Graph BFS Sort",
        "difficulty": "medium",
        "tags": json.dumps(["bfs", "graph", "sorting"]),
        "pattern": "graph",
        "category": "algorithm",
        "description": (
            "Given a city graph (bidirectional edges) and a start city, sort all "
            "cities by: (1) distance from start (ascending), (2) tie-break: smaller "
            "index first.\n\n"
            "BFS to compute distances, then sort."
        ),
        "notes": (
            "[1p3a Uber BPS] BFS + custom sorting.\n"
            "Appeared as second problem in a 2-problem set with tight time."
        ),
    },
    {
        "title": "Min Edge Reversal for Optimal Root (Re-rooting DP)",
        "difficulty": "hard",
        "tags": json.dumps(["tree", "dynamic-programming", "dfs"]),
        "pattern": "tree",
        "category": "algorithm",
        "description": (
            "Given a directed graph (tree), choose a root node that minimizes the "
            "number of edge reversals needed so all edges point away from root.\n\n"
            "Approach: DFS from node 0 to compute cost, then re-root formula:\n"
            "- If edge node->child was original direction: dp[child] = dp[node] + 1\n"
            "- If edge was reversed: dp[child] = dp[node] - 1\n\n"
            "Similar to LC 2858 but may appear as a standalone custom problem."
        ),
        "notes": (
            "[1p3a Uber BPS] Re-rooting DP.\n"
            "Watch for 1-indexed vs 0-indexed edges."
        ),
    },
    {
        "title": "Palindrome Paths in Tree (Bitmask XOR)",
        "difficulty": "hard",
        "tags": json.dumps(["tree", "dfs", "bitmask"]),
        "pattern": "tree",
        "category": "algorithm",
        "description": (
            "Given a tree where each node has a character, count paths where the "
            "characters can be rearranged to form a palindrome.\n\n"
            "Approach: XOR bitmask prefix on tree paths. A path is palindrome-formable "
            "if at most 1 character has odd count (bitmask has at most 1 bit set).\n"
            "DFS with prefix counter map. For each node, check:\n"
            "- curr_mask == prev_mask (all even)\n"
            "- curr_mask ^ prev_mask == 2^k for some k (one odd)\n\n"
            "Similar to LC 2791 but may appear as standalone."
        ),
        "notes": (
            "[1p3a Uber BPS] Bitmask XOR + DFS prefix counting.\n"
            "Key: palindrome = at most 1 odd char = XOR with at most 1 bit set."
        ),
    },
]


def step1_update_lc_problems(conn: sqlite3.Connection) -> int:
    """Update existing LC problems with Uber tag, 1p3a source, and interview notes."""
    cur = conn.cursor()
    updated = 0

    for prob in LC_PROBLEMS:
        lc_id = prob["leetcode_id"]
        cur.execute(
            "SELECT id, company_tags, source, notes, pattern FROM problems WHERE leetcode_id = ?",
            (lc_id,),
        )
        row = cur.fetchone()
        if not row:
            print(f"  WARNING: LC {lc_id} not found in DB, skipping")
            continue

        db_id = row["id"]
        new_company_tags = merge_company_tags(row["company_tags"], "Uber")
        new_source = merge_source(row["source"], "1point3acres")
        new_notes = append_notes(row["notes"], prob["notes"])
        new_pattern = prob.get("pattern") or row["pattern"]

        cur.execute(
            "UPDATE problems SET company_tags = ?, source = ?, notes = ?, pattern = ? WHERE id = ?",
            (new_company_tags, new_source, new_notes, new_pattern, db_id),
        )
        updated += 1
        print(f"  Updated LC {lc_id} (id={db_id}): +Uber tag, +1p3a source, +notes")

    # Create LC 1696 if not exists
    cur.execute("SELECT id FROM problems WHERE leetcode_id = 1696")
    if not cur.fetchone():
        cur.execute(
            """INSERT INTO problems (leetcode_id, title, url, difficulty, tags, pattern,
               category, source, company_tags, priority, notes, is_completed, comfort_level)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)""",
            (
                LC_1696_NEW["leetcode_id"],
                LC_1696_NEW["title"],
                LC_1696_NEW["url"],
                LC_1696_NEW["difficulty"],
                LC_1696_NEW["tags"],
                LC_1696_NEW["pattern"],
                LC_1696_NEW["category"],
                LC_1696_NEW["source"],
                LC_1696_NEW["company_tags"],
                LC_1696_NEW["priority"],
                LC_1696_NEW["notes"],
            ),
        )
        updated += 1
        print(f"  Created LC 1696 (Jump Game VI) with Uber tag + 1p3a source")
    else:
        print(f"  LC 1696 already exists, updating tags")
        cur.execute("SELECT id, company_tags, source, notes FROM problems WHERE leetcode_id = 1696")
        row = cur.fetchone()
        new_ct = merge_company_tags(row["company_tags"], "Uber")
        new_src = merge_source(row["source"], "1point3acres")
        new_notes = append_notes(row["notes"], LC_1696_NEW["notes"])
        cur.execute(
            "UPDATE problems SET company_tags = ?, source = ?, notes = ? WHERE id = ?",
            (new_ct, new_src, new_notes, row["id"]),
        )
        updated += 1

    conn.commit()
    return updated


def step2_create_custom_problems(conn: sqlite3.Connection) -> int:
    """Create custom non-LC problem entries."""
    cur = conn.cursor()
    created = 0

    # Get existing custom Uber problem titles for dedup
    cur.execute(
        "SELECT title FROM problems WHERE leetcode_id IS NULL AND company_tags LIKE '%Uber%'"
    )
    existing_titles = {row["title"] for row in cur.fetchall()}

    for prob in CUSTOM_PROBLEMS:
        if prob["title"] in existing_titles:
            print(f"  SKIP (exists): {prob['title']}")
            continue

        cur.execute(
            """INSERT INTO problems (title, difficulty, tags, pattern, category, source,
               company_tags, priority, description, notes, is_completed, comfort_level)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)""",
            (
                prob["title"],
                prob["difficulty"],
                prob["tags"],
                prob["pattern"],
                prob["category"],
                "1point3acres",
                json.dumps(["Uber"]),
                1,  # priority 1 (highest)
                prob.get("description", ""),
                prob.get("notes", ""),
            ),
        )
        created += 1
        print(f"  Created: {prob['title']}")

    conn.commit()
    return created


def step3_create_interview_event(conn: sqlite3.Connection) -> int:
    """Create/update interview event for Uber BPS."""
    cur = conn.cursor()

    # Check if Uber BPS event already exists
    cur.execute(
        "SELECT id FROM interview_events WHERE company_name = 'Uber' AND event_type = 'phone_screen'"
    )
    existing = cur.fetchone()

    if existing:
        print(f"  Uber BPS event already exists (id={existing['id']}), updating")
        cur.execute(
            """UPDATE interview_events
               SET title = ?, description = ?, duration_minutes = ?, status = ?
               WHERE id = ?""",
            (
                "Uber MLE BPS (Behavioral + Problem Solving)",
                (
                    "BPS phone screen: 5min intro + 40-50min coding/D&A + 5min Q&A.\n"
                    "Platform: HackerRank with screen share.\n"
                    "Content: 1-2 coding problems + D&A project discussion + ML fundamentals.\n"
                    "Problem patterns: BFS/DFS, Union Find, Binary Search, DP, OOD.\n"
                    "See docs/uber_phone_screen_prep.md for full prep materials.\n"
                    "19 LC problems + 25 custom problems seeded from 1p3a reports."
                ),
                60,
                "upcoming",
                existing["id"],
            ),
        )
    else:
        cur.execute(
            """INSERT INTO interview_events
               (company_name, event_type, title, description, scheduled_at,
                duration_minutes, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                "Uber",
                "phone_screen",
                "Uber MLE BPS (Behavioral + Problem Solving)",
                (
                    "BPS phone screen: 5min intro + 40-50min coding/D&A + 5min Q&A.\n"
                    "Platform: HackerRank with screen share.\n"
                    "Content: 1-2 coding problems + D&A project discussion + ML fundamentals.\n"
                    "Problem patterns: BFS/DFS, Union Find, Binary Search, DP, OOD.\n"
                    "See docs/uber_phone_screen_prep.md for full prep materials.\n"
                    "19 LC problems + 25 custom problems seeded from 1p3a reports."
                ),
                datetime(2026, 4, 7, 10, 0, 0).isoformat(),
                60,
                "upcoming",
            ),
        )
        print("  Created Uber BPS interview event")

    conn.commit()
    return 1


def main() -> None:
    """Run all seeding steps."""
    print(f"Database: {DB_PATH}")
    if not DB_PATH.exists():
        print("ERROR: Database file not found!")
        sys.exit(1)

    conn = get_connection()

    print("\n=== Step 1: Update LC problems with Uber tag + 1p3a source + notes ===")
    n1 = step1_update_lc_problems(conn)
    print(f"  -> {n1} LC problems updated/created")

    print("\n=== Step 2: Create custom non-LC problem entries ===")
    n2 = step2_create_custom_problems(conn)
    print(f"  -> {n2} custom problems created")

    print("\n=== Step 3: Create/update interview event ===")
    n3 = step3_create_interview_event(conn)
    print(f"  -> {n3} event(s) created/updated")

    conn.close()

    print(f"\nDone! Total: {n1} LC updated, {n2} custom created, {n3} event(s)")


if __name__ == "__main__":
    main()
