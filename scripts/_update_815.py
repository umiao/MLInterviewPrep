"""Update LeetCode 815 Bus Routes with full solution notes."""
import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'data/mle_prep.db'

NOTES = r"""## Approach: BFS on Route Graph

**Key Insight**: Instead of BFS on stops (which can be huge), treat each bus route as a node. Two route-nodes are connected if they share any stop (set intersection).

### Algorithm
1. Build `routeData`: map each route index to its set of stops
2. Seed BFS with all routes containing `source`
3. Each BFS level = one more bus ride
4. At each level, check if current route contains `target` → return level count
5. Expand to all unvisited routes that share stops with current route

### Complexity
- **Time**: O(R² × S) where R = number of routes, S = avg stops per route (set intersection)
- **Space**: O(R × S) for storing route sets

### Code
```python
def numBusesToDestination(self, routes, source, target):
    if source == target:
        return 0
    routeData = dict()
    queue = deque()
    visited = set()
    for i in range(len(routes)):
        reachableSet = set(routes[i])
        routeData[i] = reachableSet
        if source in reachableSet:
            queue.append(i)
            visited.add(i)
    if len(queue) == 0:
        return -1
    ans = 1
    while len(queue) > 0:
        for _i in range(len(queue)):
            curStation = queue.popleft()
            if target in routeData[curStation]:
                return ans
            for key in routeData:
                if key not in visited and len(routeData[key] & routeData[curStation]) > 0:
                    queue.append(key)
                    visited.add(key)
        ans += 1
    return -1
```

### Notes
- Route-level BFS avoids TLE from stop-level BFS on large graphs
- Set intersection (`&`) is the key operation for detecting route connectivity
- Could optimize further with stop-to-routes mapping for sparser graphs
- Edge case: `source == target` returns 0 immediately (no bus needed)
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tags = json.dumps(["BFS", "Graph", "Hash Table"])
    company_tags = json.dumps(["LinkedIn"])

    cur.execute("""UPDATE problems SET
        difficulty = 'hard',
        tags = ?,
        pattern = 'BFS',
        is_completed = 1,
        comfort_level = 3,
        notes = ?,
        url = 'https://leetcode.com/problems/bus-routes/',
        company_tags = ?,
        last_attempted_at = datetime('now')
    WHERE leetcode_id = 815""", (tags, NOTES.strip(), company_tags))

    conn.commit()
    print(f'Updated problem 815: {cur.rowcount} row(s)')

    # Verify
    cur.execute('SELECT length(notes), difficulty, is_completed, comfort_level FROM problems WHERE leetcode_id=815')
    row = cur.fetchone()
    print(f'Notes length: {row[0]}, difficulty: {row[1]}, completed: {row[2]}, comfort: {row[3]}')

    conn.close()


if __name__ == '__main__':
    main()
