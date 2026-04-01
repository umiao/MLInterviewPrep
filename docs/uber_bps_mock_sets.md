# Uber BPS -- Timed Mock Interview Problem Sets

> 3 timed mock sets simulating the 45-minute coding portion of the BPS screen.
> Each set: 1 medium (20 min) + 1 medium-hard (20 min) + follow-ups (5 min).
>
> **How to use**: Set a timer. Open HackerRank or a blank editor. No looking at
> solutions until time is up. After each set, review solutions in
> `uber_bps_lc_solutions.md` and `uber_bps_custom_solutions.md`.
>
> Task: T-P2-248

---

## Set 1: Tree Traversal + Union Find

**Patterns tested**: BST inorder traversal, Union Find with event handling

**Target time**: 45 minutes total

---

### Problem 1A: Kth Smallest in BST (Medium, 20 min)

**Source**: LC 230 variant

Given the root of a BST and an integer `k`, return the kth smallest element.

```
Input: root = [5, 3, 6, 2, 4, null, null, 1], k = 3
Output: 3
```

**Requirements**:
1. Implement using iterative inorder traversal (no recursion).
2. State time and space complexity.

**Follow-up A** (interviewer prompt, +3 min):
> "Now find the kth **largest** element instead."

Expected: Reverse inorder (right -> node -> left). Same complexity.

**Follow-up B** (interviewer prompt, +2 min):
> "If this BST is modified frequently (inserts/deletes) and `kthSmallest` is
> called often, how would you optimize?"

Expected: Augment each node with `left_count` (subtree size). O(H) lookup
without full traversal. Mention trade-off: O(H) per insert/delete to maintain
counts.

**Scoring rubric**:
- [ ] Clean iterative inorder: 2 pts
- [ ] Correct early termination at k: 1 pt
- [ ] Complexity analysis (O(H+k) time, O(H) space): 1 pt
- [ ] Follow-up A (reverse inorder): 1 pt
- [ ] Follow-up B (augmented BST): 1 pt

---

### Problem 1B: Rider Connection Log (Medium-Hard, 20 min)

**Source**: Custom #3

Given timestamped logs of rider interactions, find the earliest time all riders
are connected (directly or transitively).

```
Input:
  n_riders = 4
  logs = [
    (1, "Alice", "Bob"),       # timestamp 1: Alice shared ride with Bob
    (2, "Charlie", "Dave"),    # timestamp 2: Charlie shared ride with Dave
    (5, "Bob", "Charlie"),     # timestamp 5: Bob shared ride with Charlie
  ]
Output: 5  # At timestamp 5, all 4 riders are in one connected component
```

**Requirements**:
1. Implement Union Find with path compression and union by rank.
2. Process logs in chronological order. Return the earliest timestamp when
   `components == 1`, or `None` if never fully connected.
3. State time and space complexity.

**Follow-up** (interviewer prompt, +5 min):
> "Now the logs can also contain 'blocked' events:
> `(7, 'blocked', 'Alice', 'Bob')`. How do you handle disconnections?"

Expected approach: Union Find does not support deletions. Switch to adjacency
list + BFS/DFS connectivity check after each event. Discuss the trade-off:
UF is O(alpha(N)) per query but no delete; BFS rebuild is O(V+E) per event
but handles deletions. Mention offline reverse processing as an alternative
if all events are known upfront.

**Scoring rubric**:
- [ ] Correct UnionFind class (find with compression, union by rank): 2 pts
- [ ] Correct component counting and early return: 1 pt
- [ ] Handles rider name -> ID mapping: 1 pt
- [ ] Complexity analysis (O(E * alpha(N)) time, O(N) space): 1 pt
- [ ] Follow-up: BFS rebuild approach with trade-off discussion: 2 pts

---

### Set 1 Debrief Checklist

After completing Set 1, review:
- [ ] Did I explain my approach before coding?
- [ ] Did I write test cases and run them?
- [ ] Did I state complexity for every approach?
- [ ] Did I handle edge cases (empty tree, k=1, single rider)?
- [ ] Total time: ______ / 45 min

---

## Set 2: Multi-source BFS + Prefix Sum Binary Search

**Patterns tested**: Grid BFS, prefix sum with binary search

**Target time**: 45 minutes total

---

### Problem 2A: Rotting Oranges (Medium, 20 min)

**Source**: LC 994

You have an `m x n` grid where each cell is:
- `0` = empty
- `1` = fresh orange
- `2` = rotten orange

Every minute, any fresh orange adjacent (4-directional) to a rotten orange
becomes rotten. Return the minimum minutes until no fresh orange remains,
or `-1` if impossible.

```
Input: grid = [[2,1,1],[1,1,0],[0,1,1]]
Output: 4
```

**Requirements**:
1. Use multi-source BFS (enqueue all rotten oranges first).
2. Track fresh count; return -1 if fresh > 0 after BFS completes.
3. State time and space complexity.

**Follow-up A** (interviewer prompt, +3 min):
> "What if rotten oranges also spread diagonally (8-directional)?"

Expected: Add 4 diagonal directions to the direction array. Same BFS logic.
Time remains O(mn).

**Follow-up B** (interviewer prompt, +2 min):
> "What if certain cells are walls (value 3) that block spreading?"

Expected: Skip cells with value 3 in the BFS neighbor check. Same complexity.
Mention: walls may create unreachable fresh oranges, so the -1 case becomes
more common.

**Scoring rubric**:
- [ ] Correct multi-source BFS initialization: 2 pts
- [ ] Correct minute counting (layer-by-layer BFS): 1 pt
- [ ] Handles fresh == 0 edge case (return 0): 1 pt
- [ ] Returns -1 when unreachable: 1 pt
- [ ] Complexity analysis (O(mn) time and space): 1 pt

---

### Problem 2B: Purchase Optimization (Medium-Hard, 20 min)

**Source**: Custom #1

Given a list of item `prices` (may be unsorted) and a list of queries
`(start_pos, budget)`, for each query find the maximum number of items you
can buy starting from index `start_pos` with the given budget. Items must
be purchased in order from cheapest available.

```
Input:
  prices = [10, 5, 20, 15, 3]
  queries = [(0, 25), (2, 40), (0, 100)]
Output: [3, 2, 5]
  # Query 1: sorted = [3,5,10,15,20], from pos 0 with budget 25: buy 3+5+10=18, can't add 15 -> 3 items
  # Query 2: from pos 2 with budget 40: buy 10+15=25, can't add 20 -> wait, pos 2 in sorted -> 10,15,20 -> 10+15=25 <= 40, +20=45 > 40 -> 2 items
  # Query 3: from pos 0, budget 100: buy all 5 items (3+5+10+15+20=53 <= 100) -> 5
```

**Requirements**:
1. Sort prices first.
2. Build prefix sum array.
3. For each query, binary search for the maximum purchasable count.
4. State time and space complexity.

**Follow-up** (interviewer prompt, +5 min):
> "What if each item also has a 'category' and you can buy at most 2 items
> per category?"

Expected: Discuss that prefix sum + binary search no longer works because
the constraint is per-category, not global. Need a greedy approach: iterate
sorted prices, maintain category counts, skip items exceeding the per-category
limit. Time becomes O(n) per query instead of O(log n). Alternatively,
precompute a "filtered prefix sum" per category-limit constraint.

**Scoring rubric**:
- [ ] Correct sort + prefix sum construction: 1 pt
- [ ] Correct binary search (bisect_right on prefix sum): 2 pts
- [ ] Handles edge cases (pos out of bounds, budget 0): 1 pt
- [ ] Complexity analysis (O(n log n + q log n) time, O(n) space): 1 pt
- [ ] Follow-up: recognizes BS breaks, proposes greedy alternative: 2 pts

---

### Set 2 Debrief Checklist

After completing Set 2, review:
- [ ] Did I clarify constraints before coding (grid size, price range)?
- [ ] Did I proactively test with edge cases (all rotten, no fresh, empty grid)?
- [ ] Did I handle the prefix sum indexing correctly (off-by-one)?
- [ ] Did I discuss multiple approaches before choosing?
- [ ] Total time: ______ / 45 min

---

## Set 3: Graph Components + OOD

**Patterns tested**: Union Find / DFS for connectivity, Strategy pattern OOD

**Target time**: 45 minutes total

---

### Problem 3A: Number of Provinces (Medium, 20 min)

**Source**: LC 547

There are `n` cities. `isConnected[i][j] = 1` means city `i` and city `j` are
directly connected. A province is a group of directly or indirectly connected
cities. Return the number of provinces.

```
Input: isConnected = [[1,1,0],[1,1,0],[0,0,1]]
Output: 2
```

**Requirements**:
1. Implement using Union Find OR DFS (choose one, be ready to discuss the other).
2. State time and space complexity.
3. Walk through your solution with the example input.

**Follow-up A** (interviewer prompt, +3 min):
> "Given a sequence of new roads being built between cities, how would you
> efficiently track the number of provinces after each road?"

Expected: Union Find is ideal for online connectivity. Start with n components,
each union reduces count by 1 (if not already connected). O(alpha(n)) per road.
DFS would require full re-traversal after each edge -- much worse.

**Follow-up B** (interviewer prompt, +2 min):
> "If some roads are one-way (directed), does your approach still work?"

Expected: No. Union Find assumes undirected edges. For directed graphs, use
Tarjan's or Kosaraju's algorithm for strongly connected components. Mention
the difference between weakly and strongly connected components.

**Scoring rubric**:
- [ ] Correct UF or DFS implementation: 2 pts
- [ ] Correct province count: 1 pt
- [ ] Complexity analysis (O(n^2 * alpha(n)) UF or O(n^2) DFS): 1 pt
- [ ] Follow-up A: online UF advantage over DFS: 1 pt
- [ ] Follow-up B: directed graph awareness (SCC): 1 pt

---

### Problem 3B: Cart & Pricing Engine (Medium-Hard, 20 min)

**Source**: Custom #6

Design an Uber Eats cart system with the following features:
1. **Menu items** with base price and optional add-ons (e.g., "Extra cheese +$1.50")
2. **Surge pricing** (multiplier during peak hours, e.g., 1.3x)
3. **Membership discount** (e.g., Uber One gets 10% off)
4. **Promo codes** (flat amount or percentage off)
5. **Receipt generation** showing itemized breakdown

**Requirements**:
1. Design the class structure. Draw/describe the class relationships.
2. Implement the core classes: `MenuItem`, `CartItem`, `Cart`, and at least
   two pricing rules.
3. Pricing rules should be applied in configurable order (strategy pattern).
4. Show a usage example that produces a receipt.

```
Example usage:
  cart = Cart()
  burger = MenuItem("Burger", 12.00, add_ons=[AddOn("Extra cheese", 1.50)])
  cart.add_item(burger, quantity=2)
  cart.add_pricing_rule(SurgePricingRule(1.3))
  cart.add_pricing_rule(MembershipDiscountRule(10))
  print(cart.receipt())

Expected receipt:
  === Receipt ===
  Burger (+ Extra cheese) x2    $27.00
  Subtotal:                     $27.00
  Surge pricing (1.3x):        $35.10
  Uber One discount (-10%):    $31.59
  Total:                        $31.59
```

**Follow-up** (interviewer prompt, +5 min):
> "How would you add a rule that caps the maximum discount at $15? Where does
> it fit in the pricing pipeline?"

Expected: Create a `MaxDiscountCapRule` that compares current amount to
`(subtotal - max_discount)` and takes the higher value. Should be applied
LAST in the rule chain, after all discounts. Discuss: rule ordering matters --
the cap must be a post-processing step, not interleaved with discounts.

**Scoring rubric**:
- [ ] Clean class design (MenuItem, CartItem, Cart): 2 pts
- [ ] Strategy pattern for pricing rules (ABC + concrete implementations): 2 pts
- [ ] Correct receipt with pricing breakdown: 1 pt
- [ ] Extensibility discussion (adding new rules without modifying Cart): 1 pt
- [ ] Follow-up: max discount cap with ordering rationale: 1 pt

---

### Set 3 Debrief Checklist

After completing Set 3, review:
- [ ] Did I discuss UF vs DFS trade-offs for Problem 3A?
- [ ] Did I draw a class diagram or describe relationships for Problem 3B?
- [ ] Did I explain why Strategy pattern over if/else chain?
- [ ] Did I test my OOD code with the given example?
- [ ] Total time: ______ / 45 min

---

## Overall Practice Schedule

| Day | Set | Focus areas to review after |
|-----|-----|-----------------------------|
| Day 1 | Set 1 | BST traversal variants, Union Find template |
| Day 2 | Set 2 | BFS patterns, prefix sum + binary search |
| Day 3 | Set 3 | Graph connectivity, OOD/Strategy pattern |
| Day 4 | Weakest set | Re-do the set where you scored lowest |

### Scoring Guide

| Score | Level | Action |
|-------|-------|--------|
| 10-12 / 12 per set | Strong | Ready for BPS. Focus on speed. |
| 7-9 / 12 per set | Good | Review follow-up patterns. Practice explaining trade-offs aloud. |
| 4-6 / 12 per set | Needs work | Re-study the pattern in `uber_bps_pattern_cheatsheet.md`, re-solve from scratch. |
| < 4 / 12 per set | Gap | Drill the pattern with 3-5 similar LeetCode problems before retrying. |

### Time Management Tips

- **0-2 min**: Clarify the problem. Restate constraints. Ask about edge cases.
- **2-5 min**: Discuss 2 approaches. Pick one. State complexity.
- **5-18 min**: Code it. Talk while coding. Handle edge cases inline.
- **18-20 min**: Test with the given example + 1 edge case. Fix bugs.
- **Follow-ups**: Think out loud. Start with the key insight, not the full code.

> **Golden rule**: If you are stuck for more than 3 minutes on implementation,
> step back and re-examine your approach. A wrong algorithm coded perfectly
> scores 0. A correct algorithm with a minor bug scores well.
