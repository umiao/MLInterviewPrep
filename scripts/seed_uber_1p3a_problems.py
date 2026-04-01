"""Seed Uber 1p3a interview problems into the problems table.

Idempotent: updates existing LC problems, skips custom problems that already exist.

Step 1: Update/create LC problems with Uber tag + 1p3a source + interview notes.
Step 2: Create custom (non-LC) problem entries from 1p3a interview reports.
Step 3: Update Uber BPS interview event with problem list reference.

Data source: C:/Users/Shenghui Xu/Desktop/staging/uber题目整理.txt
"""

import json
import sqlite3
import sys
from datetime import datetime

DB_PATH = "data/mle_prep.db"


def ensure_company_tag(existing_tags_json: str | None, company: str) -> str:
    """Add company to tags list if not present, return JSON string."""
    if not existing_tags_json:
        tags = []
    else:
        try:
            tags = json.loads(existing_tags_json)
        except (json.JSONDecodeError, TypeError):
            tags = [t.strip() for t in existing_tags_json.split(",") if t.strip()]
    if company not in tags:
        tags.append(company)
    return json.dumps(tags, ensure_ascii=False)


def ensure_source(existing_source: str | None, new_source: str) -> str:
    """Add source badge if not already present."""
    if not existing_source:
        return new_source
    sources = [s.strip() for s in existing_source.split(",")]
    if new_source not in sources:
        sources.append(new_source)
    return ", ".join(sources)


# ---------------------------------------------------------------------------
# Step 1: LeetCode problems
# ---------------------------------------------------------------------------

LC_PROBLEMS = [
    {
        "leetcode_id": 230,
        "notes": (
            "[1p3a Uber] Variant: kth LARGEST instead of smallest. "
            "Asked for both iterative and recursive solutions on HackerRank (must run). "
            "Follow-up: O(0) space solution -- Morris Traversal. "
            "Also discussed: adding left_count/right_count to nodes, flatten the tree approach. "
            "Full complexity analysis required for each approach."
        ),
    },
    {
        "leetcode_id": 547,
        "notes": (
            "[1p3a Uber] Standard Union Find + DFS approaches. "
            "Also appeared as variant: given balls on 2D plane with coordinates (x,y), "
            "balls attract if distance < d (chain reaction). Find min time to merge all. "
            "UF to count connected components (roots)."
        ),
    },
    {
        "leetcode_id": 337,
        "notes": (
            "[1p3a Uber] Tree DP with rob/not-rob states. "
            "Standard interview problem, no special variants reported."
        ),
    },
    {
        "leetcode_id": 1020,
        "notes": (
            "[1p3a Uber] BFS/DFS from border cells. "
            "Standard interview problem, no special variants reported."
        ),
    },
    {
        "leetcode_id": 977,
        "notes": (
            "[1p3a Uber] Two-pointer approach. "
            "Asked in phone screen along with ML knowledge questions."
        ),
    },
    {
        "leetcode_id": 815,
        "notes": (
            "[1p3a Uber] BFS on route graph. "
            "Standard interview problem."
        ),
    },
    {
        "leetcode_id": 981,
        "notes": (
            "[1p3a Uber] Binary search on timestamps. "
            "Follow-ups: (a) handle 1M+ requests/sec, "
            "(b) thread safety, (c) amortized time complexity analysis."
        ),
    },
    {
        "leetcode_id": 17,
        "notes": (
            "[1p3a Uber] Backtracking. "
            "Variant: output all letter combos for a 10-digit phone number "
            "(same idea, larger scale). Like LC 17 but digits 2-9 mapped to 26 letters."
        ),
    },
    {
        "leetcode_id": 23,
        "notes": (
            "[1p3a Uber] Heap approach + divide-and-conquer. "
            "Standard interview problem."
        ),
    },
    {
        "leetcode_id": 1197,
        "notes": (
            "[1p3a Uber] BFS on infinite board. "
            "Variant: board size is n (finite, not infinite)."
        ),
    },
    {
        "leetcode_id": 1697,
        "notes": (
            "[1p3a Uber] Offline queries + Union Find + sort. "
            "Variant: edge weight >= k (reversed condition, not < k). "
            "Sort edges descending, process queries by descending k."
        ),
    },
    {
        "leetcode_id": 549,
        "notes": (
            "[1p3a Uber] Tree DP tracking increasing/decreasing consecutive sequences. "
            "Standard interview problem."
        ),
    },
    {
        "leetcode_id": 987,
        "notes": (
            "[1p3a Uber] BFS/DFS with column tracking for vertical order. "
            "Standard interview problem."
        ),
    },
    {
        "leetcode_id": 79,
        "notes": (
            "[1p3a Uber] Variant: 8 directions (including diagonals), "
            "must go straight line (no turning). Simplifies to O(R*C*8*L) enumeration, "
            "no DFS/backtracking needed. Much simpler than standard Word Search."
        ),
    },
    {
        "leetcode_id": 994,
        "notes": (
            "[1p3a Uber] Multi-source BFS. "
            "Standard interview problem, no special variants reported."
        ),
    },
    {
        "leetcode_id": 2503,
        "notes": (
            "[1p3a Uber] Variant: terrain grid with limits array, start at (0,0). "
            "Traverse cells where value < limit. BFS for each limit, "
            "count max reachable cells. Sort queries + incremental BFS for efficiency."
        ),
    },
    {
        "leetcode_id": 2858,
        "notes": (
            "[1p3a Uber] Re-rooting DP. OA problem. "
            "Must self-construct edges from input. Watch for 1-indexed nodes. "
            "DFS from root 0, then re-root formula: dp[v] = dp[u] +/- 1."
        ),
    },
    {
        "leetcode_id": 2791,
        "notes": (
            "[1p3a Uber] Bitmask XOR + DFS prefix counting. "
            "Full solution: for each node, XOR path mask from root. "
            "Count prev masks where XOR = 0 or 2^k (palindrome condition). "
            "Use prefix_counts map with backtracking."
        ),
    },
]

# LC 1696 is NOT in DB -- need to create it
LC_1696_NEW = {
    "leetcode_id": 1696,
    "title": "Jump Game VI",
    "url": "https://leetcode.com/problems/jump-game-vi/",
    "difficulty": "medium",
    "tags": json.dumps(["Dynamic Programming", "Sliding Window", "Monotonic Queue"]),
    "pattern": "Dynamic Programming",
    "category": "algorithm",
    "source": "1point3acres",
    "company_tags": json.dumps(["Uber"]),
    "priority": 1,
    "notes": (
        "[1p3a Uber] Variant: can jump +1 or +prime-ending-in-3 "
        "(3, 13, 23, ...). Maximize score. DP solution with precomputed primes. "
        "Original LC 1696: jump at most k steps, maximize sum. "
        "Uber variant changes jump rule to prime-based."
    ),
}


# ---------------------------------------------------------------------------
# Step 2: Custom (non-LC) problems
# ---------------------------------------------------------------------------

CUSTOM_PROBLEMS = [
    {
        "title": "Purchase Optimization",
        "difficulty": "medium",
        "tags": json.dumps(["Prefix Sum", "Binary Search"]),
        "pattern": "Binary Search",
        "notes": (
            "[1p3a Uber] Given prices array and queries (pos, amount), "
            "find max items purchasable starting from pos with given amount. "
            "Approach: prefix sum + binary search on prefix array. "
            "Multiple 1p3a reports confirm this as a recurring Uber problem."
        ),
    },
    {
        "title": "Customer Revenue & Referral Tracking",
        "difficulty": "hard",
        "tags": json.dumps(["OOD", "Tree", "Sorting"]),
        "pattern": "OOD",
        "notes": (
            "[1p3a Uber] OOD design problem. "
            "API: insertNewCustomer(revenue, referrerID) -> customerID, "
            "getLowestK(k, minTotalRevenue) -> Set of k customer IDs. "
            "Revenue propagates up referral tree. Must handle tree aggregation efficiently. "
            "Key: maintain sorted structure for getLowestK queries."
        ),
    },
    {
        "title": "Uber Rider Connection Log",
        "difficulty": "medium",
        "tags": json.dumps(["Union Find", "String Parsing"]),
        "pattern": "Union Find",
        "notes": (
            "[1p3a Uber] Parse timestamped logs: 'A shared-ride-with B'. "
            "Find earliest time all riders connected (transitive). "
            "Follow-up: handle 'block' events (A blocked B). "
            "UF cannot handle deletions -- must use BFS/DFS rebuild. "
            "Interviewer pushes hard, wants both approaches discussed. "
            "Rayin style: push-to-fail, must explain while coding."
        ),
    },
    {
        "title": "Elevator Binary Search OA",
        "difficulty": "medium",
        "tags": json.dumps(["Array", "Simulation"]),
        "pattern": "Array",
        "notes": (
            "[1p3a Uber] OA problem. Array where each cell has a move distance "
            "(positive = forward, negative = backward). "
            "Find minimum starting index that never goes out of left boundary. "
            "Linear scan: traverse and track when boundary is violated, update answer."
        ),
    },
    {
        "title": "Server Throughput with Heap OA",
        "difficulty": "medium",
        "tags": json.dumps(["Heap", "Simulation"]),
        "pattern": "Heap",
        "notes": (
            "[1p3a Uber] OA problem. Server throughput simulation. "
            "Compare recursive vs heap-based solution. "
            "Heap approach preferred for efficiency."
        ),
    },
    {
        "title": "Cart & Pricing Engine OOD",
        "difficulty": "hard",
        "tags": json.dumps(["OOD", "Strategy Pattern", "Design Patterns"]),
        "pattern": "OOD",
        "notes": (
            "[1p3a Uber] Design Uber Eats cart & pricing engine. "
            "Requirements: item customization (add-ons like 'Extra Cheese', 'No Onions'), "
            "surge pricing multiplier, membership discounts (Uber One: 0%% delivery + 5%% off), "
            "promo codes (flat $5 off / percentage 10%% off), "
            "receipt breakdown output (Base Price, Add-ons, Fees, Discounts). "
            "Strategy pattern for pricing rules. Must handle multiple independent pricing rules."
        ),
    },
    {
        "title": "Circular Array Shortest Jump",
        "difficulty": "medium",
        "tags": json.dumps(["BFS", "Array"]),
        "pattern": "BFS",
        "notes": (
            "[1p3a Uber] Given circular array with jump distances, "
            "find shortest path from index A to B. "
            "arr[i] = exact jump distance (left or right). BFS on indices."
        ),
    },
    {
        "title": "Robot Distance in Grid",
        "difficulty": "medium",
        "tags": json.dumps(["Grid", "DP", "Preprocessing"]),
        "pattern": "Dynamic Programming",
        "notes": (
            "[1p3a Uber] Grid with robots(O), empty(E), obstacles(X). "
            "Given distance array [left, top, bottom, right], find robot matching distances. "
            "DP to precompute distances from each cell to nearest obstacle in 4 directions."
        ),
    },
    {
        "title": "Min Operations n to 0",
        "difficulty": "medium",
        "tags": json.dumps(["Math", "Greedy", "Bit Manipulation"]),
        "pattern": "Greedy",
        "notes": (
            "[1p3a Uber] Each operation: n += or -= 2^i. "
            "Find min operations to reach 0. "
            "Optimal: binary/NAF analysis. n%%2==0: shift right. "
            "n%%4==3: +1. n%%4==1: -1. Count operations on odd numbers."
        ),
    },
    {
        "title": "Shortest Subarray with k Distinct",
        "difficulty": "medium",
        "tags": json.dumps(["Sliding Window", "Hash Map"]),
        "pattern": "Sliding Window",
        "notes": (
            "[1p3a Uber] Find shortest subarray containing at least k distinct integers. "
            "Standard two-pointer / sliding window with counter. "
            "Expand right until >= k distinct, shrink left to minimize length."
        ),
    },
    {
        "title": "Price Discount (Monotonic Stack)",
        "difficulty": "medium",
        "tags": json.dumps(["Monotonic Stack", "Array"]),
        "pattern": "Monotonic Stack",
        "notes": (
            "[1p3a Uber] OA problem. For each i, find first j > i where prices[j] <= prices[i]. "
            "If discount exists: final = prices[i] - prices[j]. "
            "If no discount: sell at original price. "
            "Output: (1) total discounted sum, (2) indices sold at original price (0-based, ascending). "
            "Classic monotonic stack application."
        ),
    },
    {
        "title": "Balanced Permutation Check",
        "difficulty": "medium",
        "tags": json.dumps(["Array", "Math"]),
        "pattern": "Array",
        "notes": (
            "[1p3a Uber] Given permutation of 1..n, for each k check if subarray "
            "forming permutation of 1..k exists. "
            "Track min/max position as k increases. "
            "If maxPos - minPos + 1 == k, then k is balanced. Return binary string."
        ),
    },
    {
        "title": "Elevator/Stairs Energy Optimization",
        "difficulty": "medium",
        "tags": json.dumps(["Binary Search", "Math"]),
        "pattern": "Binary Search",
        "notes": (
            "[1p3a Uber] First mid floors by elevator (gain energy e1, cost t1 each), "
            "remaining by stairs (consume e2, time = ceil(c / energy)). "
            "Minimize time difference between elevator and stairs. "
            "Binary search on split point. Energy cannot go negative during stairs."
        ),
    },
    {
        "title": "N-ary Tree 3-part Problem",
        "difficulty": "medium",
        "tags": json.dumps(["Tree", "DFS"]),
        "pattern": "DFS",
        "notes": (
            "[1p3a Uber] Three parts: (a) sum all node values, (b) find max path value, "
            "(c) return nodes on max path. Must define Node class. "
            "DFS traversal for all parts."
        ),
    },
    {
        "title": "Max Throughput with Budget",
        "difficulty": "medium",
        "tags": json.dumps(["Binary Search", "Greedy"]),
        "pattern": "Binary Search",
        "notes": (
            "[1p3a Uber] Multiple services, each has current throughput and scale cost. "
            "Pipeline: service i+1 input comes from service i. "
            "Bottleneck = min throughput. Budget constraint. "
            "Binary search on target throughput. For each candidate, "
            "check if total cost to raise all services to target <= budget."
        ),
    },
    {
        "title": "Parking Lot OOD",
        "difficulty": "medium",
        "tags": json.dumps(["OOD", "Design Patterns"]),
        "pattern": "OOD",
        "notes": (
            "[1p3a Uber] Design parking lot with park/unpark/checkcar operations. "
            "Motorcycle spots: only motorcycles. Regular spots: motorcycles + regular cars. "
            "Class design with ParkingLot, Spot, Vehicle hierarchy."
        ),
    },
    {
        "title": "Task Assignment to 2 People",
        "difficulty": "medium",
        "tags": json.dumps(["Greedy", "Sorting"]),
        "pattern": "Greedy",
        "notes": (
            "[1p3a Uber] n tasks, reward1[i]/reward2[i] per person. "
            "Person 1 must do exactly k tasks. Maximize total reward. "
            "Greedy: sort by diff(r1 - r2) descending, pick top k for person 1, rest for person 2. "
            "Base sum = sum(reward2), add top-k diffs."
        ),
    },
    {
        "title": "Minesweeper Grid Generator",
        "difficulty": "easy",
        "tags": json.dumps(["Random", "Grid", "Code Quality"]),
        "pattern": "Array",
        "notes": (
            "[1p3a Uber] Place N mines randomly on 2D grid. "
            "Follow-up: optimize code quality -- remove unnecessary set, reduce variables, "
            "simplify logic. Interviewer pushes for cleaner code iteratively. "
            "Focus is on code quality, not algorithmic complexity."
        ),
    },
    {
        "title": "2D Grid Nearest Exit (BFS)",
        "difficulty": "medium",
        "tags": json.dumps(["BFS", "Grid"]),
        "pattern": "BFS",
        "notes": (
            "[1p3a Uber] BFS from starting point to find nearest boundary cell. "
            "Standard multi-source BFS variant. Similar to LC 1926."
        ),
    },
    {
        "title": "Lock Combination BFS",
        "difficulty": "medium",
        "tags": json.dumps(["BFS", "State Space"]),
        "pattern": "BFS",
        "notes": (
            "[1p3a Uber] Tech screening problem. Find minimum steps to unlock. "
            "BFS on state space. Similar to LC 752 (Open the Lock)."
        ),
    },
    {
        "title": "Non-overlapping Interval Triples",
        "difficulty": "hard",
        "tags": json.dumps(["Intervals", "Sorting", "DP"]),
        "pattern": "Intervals",
        "notes": (
            "[1p3a Uber] Count groups of 3 intervals with no pairwise overlap. "
            "Sort intervals, enumerate combinations efficiently. "
            "Time pressure: 40 min for 2 problems, interviewer moves on quickly."
        ),
    },
    {
        "title": "City Graph BFS Sort",
        "difficulty": "medium",
        "tags": json.dumps(["BFS", "Graph", "Sorting"]),
        "pattern": "BFS",
        "notes": (
            "[1p3a Uber] Given city graph + start city, sort cities by distance. "
            "Ties: smaller index first. BFS to compute distances, then sort. "
            "Time pressure: paired with interval triples in same 40-min session."
        ),
    },
    {
        "title": "Balls Attraction Union Find",
        "difficulty": "medium",
        "tags": json.dumps(["Union Find", "Geometry"]),
        "pattern": "Union Find",
        "notes": (
            "[1p3a Uber] 2D plane with balls at (x,y). "
            "Balls attract if distance < d (chain reaction). "
            "Each time step: choose one ball to start attraction. "
            "Find min time to merge all balls. "
            "UF: connect all pairs within distance d, answer = number of connected components."
        ),
    },
    {
        "title": "Layers and Energy Adventure",
        "difficulty": "medium",
        "tags": json.dumps(["Prefix Sum", "Two Pointers"]),
        "pattern": "Two Pointers",
        "notes": (
            "[1p3a Uber] layers[] = energy consumed per level, energy[] = threshold per level, "
            "K = initial energy. From level i: consume layers[i], if remaining >= energy[i] then pass. "
            "Return array: score[i] = max levels passable starting from i. "
            "Prefix sum + sliding window / two pointers approach."
        ),
    },
    {
        "title": "Driver Queue System Design",
        "difficulty": "hard",
        "tags": json.dumps(["System Design", "Queue"]),
        "pattern": "System Design",
        "category": "system_design",
        "notes": (
            "[1p3a Uber] Design internal API: given pickup area, return driver queue. "
            "Drivers enter area -> join queue, leave area -> removed. "
            "Feedback: need more conversation, don't just give answers. "
            "Reporter said SD was likely the failing round."
        ),
    },
]


def seed_lc_problems(conn: sqlite3.Connection) -> tuple[int, int]:
    """Update existing LC problems and create LC 1696. Returns (updated, created)."""
    cursor = conn.cursor()
    updated = 0
    created = 0

    for prob in LC_PROBLEMS:
        lc_id = prob["leetcode_id"]
        cursor.execute(
            "SELECT id, company_tags, source, notes FROM problems WHERE leetcode_id = ?",
            (lc_id,),
        )
        row = cursor.fetchone()
        if not row:
            print(f"  [WARN] LC {lc_id} not found in DB, skipping")
            continue

        pid, existing_companies, existing_source, existing_notes = row

        new_companies = ensure_company_tag(existing_companies, "Uber")
        new_source = ensure_source(existing_source, "1point3acres")

        # Append notes if not already present
        marker = "[1p3a Uber]"
        if existing_notes and marker in existing_notes:
            new_notes = existing_notes  # already seeded
        elif existing_notes:
            new_notes = existing_notes + "\n\n" + prob["notes"]
        else:
            new_notes = prob["notes"]

        cursor.execute(
            "UPDATE problems SET company_tags = ?, source = ?, notes = ? WHERE id = ?",
            (new_companies, new_source, new_notes, pid),
        )
        updated += 1

    # Create LC 1696 if not exists
    cursor.execute(
        "SELECT id FROM problems WHERE leetcode_id = ?", (1696,)
    )
    if cursor.fetchone() is None:
        cursor.execute(
            """INSERT INTO problems
            (leetcode_id, title, url, difficulty, tags, pattern, category,
             source, company_tags, priority, is_completed, comfort_level,
             created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)""",
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
                datetime.utcnow().isoformat(),
                LC_1696_NEW["notes"],
            ),
        )
        created += 1
        print(f"  [NEW] LC 1696 - Jump Game VI created")
    else:
        print(f"  [SKIP] LC 1696 already exists")

    conn.commit()
    return updated, created


def seed_custom_problems(conn: sqlite3.Connection) -> tuple[int, int]:
    """Create custom problem entries. Returns (created, skipped)."""
    cursor = conn.cursor()
    created = 0
    skipped = 0

    for prob in CUSTOM_PROBLEMS:
        # Dedup by title
        cursor.execute(
            "SELECT id FROM problems WHERE title = ?", (prob["title"],)
        )
        if cursor.fetchone() is not None:
            print(f"  [SKIP] '{prob['title']}' already exists")
            skipped += 1
            continue

        category = prob.get("category", "algorithm")
        cursor.execute(
            """INSERT INTO problems
            (title, difficulty, tags, pattern, category, source, company_tags,
             priority, is_completed, comfort_level, created_at, notes)
            VALUES (?, ?, ?, ?, ?, '1point3acres', ?, 1, 0, 0, ?, ?)""",
            (
                prob["title"],
                prob["difficulty"],
                prob["tags"],
                prob["pattern"],
                category,
                json.dumps(["Uber"]),
                datetime.utcnow().isoformat(),
                prob["notes"],
            ),
        )
        created += 1
        print(f"  [NEW] '{prob['title']}' created")

    conn.commit()
    return created, skipped


def update_interview_event(conn: sqlite3.Connection) -> None:
    """Update Uber BPS interview event with problem list reference."""
    cursor = conn.cursor()

    # Get only 1p3a-sourced Uber problems for reference
    cursor.execute(
        "SELECT id, leetcode_id, title FROM problems "
        "WHERE company_tags LIKE '%Uber%' AND notes LIKE '%[1p3a Uber]%' "
        "ORDER BY leetcode_id"
    )
    uber_problems = cursor.fetchall()
    lc_list = [f"LC {r[1]}" for r in uber_problems if r[1]]
    custom_list = [r[2] for r in uber_problems if not r[1]]

    problem_ref = (
        f"Uber MLE Phone Screen. Interviewer: Nikat Patel. "
        f"Exercise link: https://hr.gs/3026fd6\n\n"
        f"Problem pool ({len(uber_problems)} problems):\n"
        f"LC: {', '.join(lc_list)}\n"
        f"Custom: {len(custom_list)} non-LC interview problems from 1p3a reports"
    )

    # Update event ID 8 (Uber BPS phone screen)
    cursor.execute(
        "UPDATE interview_events SET description = ? WHERE id = 8",
        (problem_ref,),
    )
    conn.commit()
    print(f"  [OK] Updated interview event #8 with {len(uber_problems)} problem references")


def main() -> None:
    """Run all seed steps."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    print("=== Step 1: LC Problems ===")
    updated, created = seed_lc_problems(conn)
    print(f"  Summary: {updated} updated, {created} created")

    print("\n=== Step 2: Custom Problems ===")
    created, skipped = seed_custom_problems(conn)
    print(f"  Summary: {created} created, {skipped} skipped")

    print("\n=== Step 3: Interview Event ===")
    update_interview_event(conn)

    conn.close()
    print("\n[DONE] All steps complete.")


if __name__ == "__main__":
    main()
